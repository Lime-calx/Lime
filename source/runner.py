"""Lime runner: runs student code and checks it. Works in Brython (browser) and CPython (build-time validation).

run_code(code, tests) -> JSON string with:
  out      what the program printed (str, capped at 20,000 chars)
  error    one line, "ErrorType: message  (line N)", or null      (stable: the UI's explainer parses it)
  etype    the error type name, e.g. "ZeroDivisionError", or null
  eline    the line number in the learner's code, or null
  trace    a short real-style traceback using only frames from the learner's code, or null
  notes    list of short notes (time.sleep skipped, sys.exit used, engine differences), may be empty
  results  list of {label, ok, hint, detail} from the tests

No `re` on learner source (Brython's re breaks on emoji); a small hand-written lexer does the source work.
"""
import sys, time, builtins
from io import StringIO

try:
    from browser import window
except Exception:
    window = None

BRYTHON = str(getattr(getattr(sys, "implementation", None), "name", "")).lower() == "brython" or sys.platform == "brython"
MAX_ITERS = 2000000
BUDGET = 6.0
FILENAME = "student"

# ---- captured at import, so learner code that reassigns builtins cannot change grading ----
_bool, _str, _repr, _isinstance, _type, _len = bool, str, repr, isinstance, type, len
_list, _dict, _tuple, _set, _int, _float = list, dict, tuple, set, int, float
_callable, _getattr, _setattr, _hasattr, _delattr = callable, getattr, setattr, hasattr, delattr
_exec, _compile, _iter, _next, _range, _sorted, _min = exec, compile, iter, next, range, sorted, min
_BaseException, _KeyError, _SyntaxError, _SystemExit = BaseException, KeyError, SyntaxError, SystemExit
_Exception, _RuntimeError, _StopIteration = Exception, RuntimeError, StopIteration
_time = time.time
_sleep = time.sleep
_StringIO = StringIO
_BUILTINS = _dict(builtins.__dict__)
_RLIMIT = sys.getrecursionlimit()
_STDOUT, _STDERR = sys.stdout, sys.stderr
_BLOCKED_MODS = ("browser", "javascript")


class _Note(Exception):
    """A plain message for the learner (shown without an 'ErrorType:' prefix)."""


def _safe_repr(v, limit=200):
    try:
        r = _repr(v)
        if _type(r) is not _str:
            r = "<unprintable value>"
    except _BaseException:
        r = "<unprintable value>"
    return r if _len(r) <= limit else r[:limit - 3] + "..."


# ================= JSON (own serializer: learner code cannot patch it) =================
def _jstr(s):
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    for c in _range(32):
        ch = chr(c)
        if ch in s:
            s = s.replace(ch, "\\u%04x" % c)
    for ch in ("\u2028", "\u2029"):
        if ch in s:
            s = s.replace(ch, "\\u%04x" % ord(ch))
    return '"' + s + '"'


def _jdump(v):
    t = _type(v)
    if v is None:
        return "null"
    if t is _bool:
        return "true" if v else "false"
    if t is _int:
        return _str(v)
    if t is _float:
        return _repr(v)
    if t is _str:
        return _jstr(v)
    if t is _list or t is _tuple:
        return "[" + ", ".join([_jdump(x) for x in v]) + "]"
    if t is _dict:
        return "{" + ", ".join([_jstr(_str(k)) + ": " + _jdump(x) for k, x in v.items()]) + "}"
    return _jstr(_safe_repr(v))


# ================= lexer (no re; handles strings, f-strings, comments, brackets) =================
_PREFIXES = ("r", "u", "b", "f", "t", "br", "rb", "fr", "rf", "tr", "rt")
_OPEN = "([{"
_CLOSE = ")]}"


def _is_name_char(ch):
    return ch == "_" or ch.isalnum() or (ord(ch) > 127 and ch.isidentifier())


class _Lex:
    """Tokens: (kind, start, end, line, text). kind: name, num, str, op, nl (logical line end at depth 0).
    Also: logical lines [(line, indent_str, first_tok, last_tok)], comments [(start, end)], error (cls, msg, line)."""

    def __init__(self, src):
        self.s = _list(src)
        self.toks = []
        self.lines = []
        self.comments = []
        self.error = None
        self.depth_open = []  # stack of (char, line)
        try:
            self._run()
        except _Note:
            pass

    def _err(self, cls, msg, line):
        if self.error is None:
            self.error = (cls, msg, line)
        raise _Note("lex")

    def _string(self, i, line, prefix):
        """i at the opening quote. Returns (end_index, end_line)."""
        s = self.s
        n = _len(s)
        q = s[i]
        triple = i + 2 < n and s[i + 1] == q and s[i + 2] == q
        start_line = line
        fmode = "f" in prefix or "t" in prefix
        j = i + (3 if triple else 1)
        while True:
            if j >= n:
                if triple:
                    end_line = line - 1 if n and s[n - 1] == "\n" else line
                    self._err("SyntaxError", "unterminated triple-quoted string literal (detected at line %d)" % end_line, start_line)
                self._err("SyntaxError", "unterminated string literal (detected at line %d)" % start_line, start_line)
            ch = s[j]
            if ch == "\\":
                if j + 1 < n and s[j + 1] == "\n":
                    line += 1
                j += 2
                continue
            if ch == "\n":
                if not triple:
                    self._err("SyntaxError", "unterminated string literal (detected at line %d)" % start_line, start_line)
                line += 1
                j += 1
                continue
            if ch == q:
                if not triple:
                    return j + 1, line
                if j + 2 < n and s[j + 1] == q and s[j + 2] == q:
                    return j + 3, line
                j += 1
                continue
            if fmode and ch == "{":
                if j + 1 < n and s[j + 1] == "{":
                    j += 2
                    continue
                j, line = self._fexpr(j + 1, line)
                continue
            j += 1

    def _fexpr(self, j, line):
        """Inside an f-string replacement field; returns index after the matching }."""
        s = self.s
        n = _len(s)
        depth = 1
        while j < n:
            ch = s[j]
            if ch in "'\"":
                j, line = self._string(j, line, "")
                continue
            if ch == "\n":
                line += 1
            elif ch in _OPEN:
                depth += 1
            elif ch in _CLOSE:
                depth -= 1
                if depth == 0:
                    return j + 1, line
            j += 1
        return j, line

    def _run(self):
        s = self.s
        n = _len(s)
        i = 0
        line = 1
        at_bol = True
        cont = False  # previous line ended with a backslash
        toks = self.toks
        while i < n:
            if at_bol:
                at_bol = False
                if not self.depth_open and not cont:
                    j = i
                    while j < n and s[j] in " \t\f":
                        j += 1
                    if j < n and s[j] not in "#\n\r":
                        self.lines.append([line, "".join(s[i:j]), _len(toks), -1])
                    i = j
                    continue
                cont = False
            ch = s[i]
            if ch == "\n":
                if not self.depth_open and self.lines and self.lines[-1][3] == -1 and _len(toks) > self.lines[-1][2]:
                    toks.append(("nl", i, i + 1, line, "\n"))
                    self.lines[-1][3] = _len(toks) - 1
                line += 1
                i += 1
                at_bol = True
                continue
            if ch in " \t\f\r":
                i += 1
                continue
            if ch == "#":
                j = i
                while j < n and s[j] != "\n":
                    j += 1
                self.comments.append((i, j))
                i = j
                continue
            if ch == "\\" and i + 1 < n and s[i + 1] in "\r\n":
                i += 2 if s[i + 1] == "\n" else 3
                line += 1
                at_bol = True
                cont = True
                continue
            if ch in "'\"":
                j, l2 = self._string(i, line, "")
                toks.append(("str", i, j, line, ""))
                i, line = j, l2
                continue
            if _is_name_char(ch):
                j = i
                while j < n and _is_name_char(s[j]):
                    j += 1
                word = "".join(s[i:j])
                if j < n and s[j] in "'\"" and word.lower() in _PREFIXES:
                    k, l2 = self._string(j, line, word.lower())
                    toks.append(("str", i, k, line, word.lower()))
                    i, line = k, l2
                    continue
                toks.append(("num" if ch.isdigit() else "name", i, j, line, word))
                i = j
                continue
            if ch == "." and i + 1 < n and s[i + 1].isdigit():
                j = i + 1
                while j < n and _is_name_char(s[j]):
                    j += 1
                toks.append(("num", i, j, line, "".join(s[i:j])))
                i = j
                continue
            if ch == ":" and i + 1 < n and s[i + 1] == "=":
                toks.append(("op", i, i + 2, line, ":="))
                i += 2
                continue
            if ch in _OPEN:
                self.depth_open.append((ch, line))
            elif ch in _CLOSE:
                if self.depth_open:
                    self.depth_open.pop()
            toks.append(("op", i, i + 1, line, ch))
            i += 1
        if self.lines and self.lines[-1][3] == -1 and not self.depth_open:
            toks.append(("nl", n, n, line, ""))
            self.lines[-1][3] = _len(toks) - 1
        if self.depth_open:
            ch, l0 = self.depth_open[0]
            self._err("SyntaxError", "'%s' was never closed" % ch, l0)


def _indent_problem(lx):
    """CPython's indentation rules on the lexer's logical lines. Returns (cls, msg_or_None, line) or None."""
    stack = [(0, 0)]
    prev_colon = False
    prev_line = 0
    prev_kw = ""

    def expected():
        what = {"def": "function definition", "class": "class definition"}.get(prev_kw)
        if not what and prev_kw in ("if", "elif", "else", "for", "while", "try", "except", "finally", "with", "match", "case"):
            what = "'%s' statement" % prev_kw
        return "expected an indented block after %s on line %d" % (what, prev_line) if what else None
    for ln, ind, first, last in lx.lines:
        col = alt = 0
        for ch in ind:
            if ch == "\t":
                col = (col // 8 + 1) * 8
                alt += 1
            elif ch == " ":
                col += 1
                alt += 1
            else:
                col = alt = 0
        tc, ta = stack[-1]
        if col > tc:
            if alt <= ta:
                return ("TabError", "inconsistent use of tabs and spaces in indentation", ln)
            if not prev_colon:
                return ("IndentationError", "unexpected indent", ln)
            stack.append((col, alt))
        elif col == tc:
            if alt != ta:
                return ("TabError", "inconsistent use of tabs and spaces in indentation", ln)
            if prev_colon:
                return ("IndentationError", expected(), ln)
        else:
            while _len(stack) > 1 and col < stack[-1][0]:
                stack.pop()
            if col != stack[-1][0]:
                return ("IndentationError", "unindent does not match any outer indentation level", ln)
            if alt != stack[-1][1]:
                return ("TabError", "inconsistent use of tabs and spaces in indentation", ln)
            if prev_colon:
                return ("IndentationError", expected(), ln)
        lt = lx.toks[last - 1] if last > 0 else None
        prev_colon = lt is not None and lt[0] == "op" and lt[4] == ":"
        prev_line = ln
        ft = lx.toks[first] if first < _len(lx.toks) else None
        prev_kw = ft[4] if ft and ft[0] == "name" else ""
        if prev_kw == "async" and first + 1 < _len(lx.toks):
            prev_kw = lx.toks[first + 1][4]
    return None


def _scan_problem(lx):
    """First tokenizer-level problem by line: (cls, msg, line) or None."""
    a = lx.error
    b = _indent_problem(lx)
    if a and b:
        return a if a[2] <= b[2] else b
    return a or b


def _strip_comments_src(src):
    """Source with comments removed (strings kept)."""
    lx = _Lex(src)
    if not lx.comments:
        return src
    s = lx.s
    out = []
    pos = 0
    for a, b in lx.comments:
        out.append("".join(s[pos:a]).rstrip(" \t\f"))
        pos = b
    out.append("".join(s[pos:]))
    return "".join(out)


# ================= loop guard (token-based rewrite; strings and comments untouched) =================
def _header_end(toks, k, depth, comp):
    """From token k, find where a while/for header (comp=False) or a comprehension iterable (comp=True) ends.
    Returns the index of the last token of the expression, or -1."""
    d = depth
    lambdas = 0
    last = -1
    n = _len(toks)
    while k < n:
        kind, a, b, ln, txt = toks[k]
        if kind == "nl":
            return -1
        if kind == "op":
            if txt in _OPEN:
                d += 1
            elif txt in _CLOSE:
                d -= 1
                if d < depth:
                    return last if comp else -1
            elif txt == ":" and d == depth:
                if lambdas:
                    lambdas -= 1
                elif not comp:
                    return last
            elif txt == ";" and d == depth:
                return -1
        elif kind == "name" and d == depth:
            if txt == "lambda":
                lambdas += 1
            elif comp and txt in ("if", "for", "async"):
                return last
        last = k
        k += 1
    return -1


def _escape_fix(text, prefix):
    """Brython misreads \\UXXXXXXXX escapes above U+FFFF: write those characters literally (same meaning)."""
    if "r" in prefix or "b" in prefix or "\\U" not in text:
        return text
    out = []
    i = 0
    n = _len(text)
    while i < n:
        ch = text[i]
        if ch == "\\" and i + 1 < n:
            if text[i + 1] == "U" and i + 10 <= n:
                h = text[i + 2:i + 10]
                try:
                    cp = _int(h, 16)
                except _BaseException:
                    cp = -1
                if 0xFFFF < cp <= 0x10FFFF:
                    out.append(chr(cp))
                    i += 10
                    continue
            out.append(text[i:i + 2])
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _rewrite(src, gname, wname, lx=None):
    """Guard every while (condition wrapped) and for (iterable wrapped), including comprehensions.
    Never adds lines, so line numbers stay the same."""
    lx = lx or _Lex(src)
    toks = lx.toks
    ins = []  # (index, text)
    depth = 0
    prev = None
    for k in _range(_len(toks)):
        kind, a, b, ln, txt = toks[k]
        if kind == "op":
            if txt in _OPEN:
                depth += 1
            elif txt in _CLOSE:
                depth -= 1
        elif kind == "name" and txt == "while" and depth == 0:
            e = _header_end(toks, k + 1, 0, False)
            if e >= k + 1:
                ins.append((b, " %s() and (" % gname))
                ins.append((toks[e][2], ")"))
        elif kind == "name" and txt == "for" and not (prev and prev[0] == "name" and prev[4] == "async"):
            d = depth
            m = k + 1
            dd = d
            while m < _len(toks):
                t = toks[m]
                if t[0] == "nl":
                    m = -1
                    break
                if t[0] == "op" and t[4] in _OPEN:
                    dd += 1
                elif t[0] == "op" and t[4] in _CLOSE:
                    dd -= 1
                    if dd < d:
                        m = -1
                        break
                elif t[0] == "name" and t[4] == "in" and dd == d:
                    break
                m += 1
            if 0 < m < _len(toks):
                e = _header_end(toks, m + 1, d, d > 0)
                if e >= m + 1:
                    ins.append((toks[m][2], " %s(" % wname))
                    ins.append((toks[e][2], ")"))
        prev = toks[k]
    s = lx.s
    fixes = []
    if BRYTHON:
        for t in toks:
            if t[0] == "str" and "\\U" in "".join(s[t[1]:t[2]]):
                fixes.append(t)
    if not ins and not fixes:
        return src
    ins = _sorted(ins, key=lambda x: x[0])
    out = []
    pos = 0
    fi = 0
    for idx, text in ins:
        while fi < _len(fixes) and fixes[fi][2] <= idx:
            f = fixes[fi]
            if f[1] >= pos:
                out.append("".join(s[pos:f[1]]))
                out.append(_escape_fix("".join(s[f[1]:f[2]]), f[4]))
                pos = f[2]
            fi += 1
        out.append("".join(s[pos:idx]))
        out.append(text)
        pos = idx
    while fi < _len(fixes):
        f = fixes[fi]
        if f[1] >= pos:
            out.append("".join(s[pos:f[1]]))
            out.append(_escape_fix("".join(s[f[1]:f[2]]), f[4]))
            pos = f[2]
        fi += 1
    out.append("".join(s[pos:]))
    return "".join(out)


_STOP_MSG = ("Lime stopped your program: a loop ran for too long (more than %s steps or %d seconds). "
             "Check that the loop's condition can become false, or that the range is not huge.")


def _make_guard():
    """Returns (state, tick, wrap). Closures only: nothing a learner can reach through a module."""
    st = {"n": 0, "left": 5000, "t": _time(), "max": MAX_ITERS, "budget": BUDGET, "tripped": False}

    def slow():
        st["n"] += 5000 - st["left"]
        st["left"] = 5000
        names = st.get("names")
        if names:  # put the guard back if learner code replaced it
            d = builtins.__dict__
            if d.get(names[0]) is not tick:
                d[names[0]] = tick
            if d.get(names[1]) is not wrap:
                d[names[1]] = wrap
        if st["n"] > st["max"] or _time() - st["t"] > st["budget"]:
            st["tripped"] = True
            st["left"] = 1
            raise _RuntimeError(_STOP_MSG % ("{:,}".format(st["max"]), int(st["budget"] + 0.5)))

    def tick():
        st["left"] -= 1
        if st["left"] <= 0:
            slow()
        return True

    def wrap(*args):
        it = args[0] if _len(args) == 1 else args
        if _type(it) is _list:
            lst = it
            i = 0
            while i < _len(lst):  # CPython list-iterator semantics (Brython differs when the list grows)
                st["left"] -= 1
                if st["left"] <= 0:
                    slow()
                yield lst[i]
                i += 1
            return
        for x in it:
            st["left"] -= 1
            if st["left"] <= 0:
                slow()
            yield x

    def reset():
        st["n"] = 0
        st["left"] = 5000
        st["t"] = _time()
        if st["tripped"]:  # after one runaway loop, later checks give up sooner
            st["max"] = 200000
            st["budget"] = 1.0

    return st, tick, wrap, reset


# ================= safe replacements while learner code runs =================
_DOCS = {
    "print": "print(*values, sep=' ', end='\\n')\n    Prints the values, separated by sep and followed by end.",
    "len": "len(obj, /)\n    Return the number of items in a container.",
    "range": "range(stop) or range(start, stop[, step])\n    A sequence of whole numbers from start (default 0) up to, but not including, stop.",
    "input": "input(prompt='')\n    Read a line of text typed by the user. (Not available in Lime: use a variable.)",
    "int": "int(x=0)\n    Convert a number or a string of digits to a whole number (int).",
    "float": "float(x=0.0)\n    Convert a number or a string to a floating-point number.",
    "str": "str(object='')\n    Return the text form of object.",
    "list": "list(iterable=())\n    Build a new list from the items of iterable.",
    "dict": "dict(**kwargs) or dict(iterable)\n    Build a new dictionary of key: value pairs.",
    "tuple": "tuple(iterable=())\n    Build a new tuple (an unchangeable list).",
    "set": "set(iterable=())\n    Build a new set: unordered, no duplicates.",
    "sorted": "sorted(iterable, /, *, key=None, reverse=False)\n    Return a new sorted list of the items.",
    "sum": "sum(iterable, /, start=0)\n    Add up the items (numbers), plus start.",
    "min": "min(iterable) or min(a, b, ...)\n    Return the smallest item.",
    "max": "max(iterable) or max(a, b, ...)\n    Return the largest item.",
    "abs": "abs(x, /)\n    Return the absolute value (distance from zero) of x.",
    "round": "round(number, ndigits=None)\n    Round to ndigits decimal places (to a whole number if ndigits is left out).",
    "type": "type(object)\n    Return the type of object, e.g. <class 'int'>.",
    "isinstance": "isinstance(obj, class_or_tuple, /)\n    True if obj is of that type (or a subclass of it).",
    "enumerate": "enumerate(iterable, start=0)\n    Give (index, item) pairs: for i, x in enumerate(items).",
    "zip": "zip(*iterables)\n    Pair up items: zip([1, 2], 'ab') gives (1, 'a'), (2, 'b').",
    "help": "help(thing)\n    Show the help text for a function, type or value.",
    "repr": "repr(obj, /)\n    Return the precise text form of obj (strings keep their quotes).",
    "map": "map(func, iterable)\n    Apply func to every item.",
    "filter": "filter(func, iterable)\n    Keep the items where func(item) is true.",
    "any": "any(iterable, /)\n    True if at least one item is true.",
    "all": "all(iterable, /)\n    True if every item is true (and for an empty iterable).",
    "divmod": "divmod(x, y, /)\n    Return the pair (x // y, x % y).",
    "pow": "pow(base, exp, mod=None)\n    base ** exp (optionally % mod).",
    "ord": "ord(c, /)\n    Return the Unicode code point of a one-character string.",
    "chr": "chr(i, /)\n    Return the one-character string for Unicode code point i.",
    "bool": "bool(x=False)\n    Return True if x is truthy, False otherwise.",
    "reversed": "reversed(sequence, /)\n    Go through a sequence backwards.",
}
_BAD_DOC = "The base class of the class hierarchy"


def _all(iterable):
    for x in iterable:
        if not x:
            return False
    return True


def _any(iterable):
    for x in iterable:
        if x:
            return True
    return False


class _Session:
    """Everything that is patched while learner code (or a check calling it) runs, and restored after."""

    def __init__(self, code, notes):
        self.code = code
        self.notes = notes
        self.docs = None
        self.gname = "_lime_g%d" % (int(_time() * 1000) % 1000003)
        self.wname = self.gname + "w"
        self.st, self.tick, self.wrap, self.reset = _make_guard()
        self.st["names"] = (self.gname, self.wname)
        self.sink = _StringIO()
        self.saved_mods = {}
        self.pre = _dict(builtins.__dict__)

    def _note(self, msg):
        if msg not in self.notes:
            self.notes.append(msg)

    def _input(self, prompt=""):
        raise _RuntimeError("input() is not available in Lime. Put the value in a variable instead.")

    def _sleep(self, secs=0):
        self._note("time.sleep() does not pause in Lime: the program carried straight on.")

    def _exit(self, code=None):
        raise _SystemExit(code)

    def _doc_map(self):
        if self.docs is None:
            self.docs = {}
            try:
                import ast
                tree = ast.parse(self.code)
                lines = self.code.split("\n")
                for node in _walk_nodes(tree, []):
                    if _type(node).__name__ in ("FunctionDef", "ClassDef"):
                        body = _getattr(node, "body", []) or []
                        doc = None
                        if body and _type(body[0]).__name__ == "Expr":
                            v = _getattr(body[0], "value", None)
                            if _type(v).__name__ in ("Constant", "Str") and _isinstance(_getattr(v, "value", _getattr(v, "s", None)), _str):
                                doc = _getattr(v, "value", _getattr(v, "s", None))
                        head = lines[node.lineno - 1].strip() if 0 < node.lineno <= _len(lines) else node.name
                        if head.startswith("def "):
                            head = head[4:]
                        if head.endswith(":"):
                            head = head[:-1]
                        self.docs[node.name] = (head, doc)
            except _BaseException:
                pass
        return self.docs

    def _help(self, *args):
        if not args:
            print("help(thing) shows what a function or type does, for example help(len) or help(str.upper).")
            return
        obj = args[0]
        name = _getattr(obj, "__name__", None)
        if _isinstance(obj, _str):
            name = obj
        dm = self._doc_map()
        kind = "function" if _callable(obj) and not _isinstance(obj, _type) else "class"
        if name in dm and (_getattr(obj, "__module__", None) in (None, "__main__") or _isinstance(obj, _str)):
            head, doc = dm[name]
            print("Help on %s %s:\n\n%s\n    %s\n" % (kind, name, head, (doc or "(no docstring)").strip().replace("\n", "\n    ")))
            return
        if name in _DOCS and _getattr(builtins, name, None) is obj or (_isinstance(obj, _str) and obj in _DOCS):
            print("Help on built-in %s:\n\n%s\n" % (name, _DOCS[name]))
            return
        doc = _getattr(obj, "__doc__", None)
        if doc and _isinstance(doc, _str) and _BAD_DOC not in doc:
            print("Help on %s:\n\n%s\n" % (name or _type(obj).__name__, doc.strip()))
            return
        print("No help text is available for %s in Lime. Search the web for 'python %s'." % (name or _safe_repr(obj), name or _type(obj).__name__))

    def enter(self):
        self.pre = _dict(builtins.__dict__)
        sys.stdout = sys.stderr = self.sink
        _setattr(builtins, self.gname, self.tick)
        _setattr(builtins, self.wname, self.wrap)
        builtins.input = self._input
        builtins.help = self._help
        builtins.exit = builtins.quit = self._exit
        if BRYTHON:
            builtins.all = _all  # Brython's all() swallows errors raised inside the iterable
            builtins.any = _any
            try:
                sys.setrecursionlimit(1000)
            except _BaseException:
                pass
        time.sleep = self._sleep
        for m in _BLOCKED_MODS:
            if m not in self.saved_mods:
                self.saved_mods[m] = sys.modules.get(m, "__absent__")
            sys.modules[m] = None

    def leave(self):
        """Undo everything learner code may have changed. Returns True if the loop guard had been tampered with."""
        tampered = builtins.__dict__.get(self.gname) is not self.tick or builtins.__dict__.get(self.wname) is not self.wrap
        sys.stdout, sys.stderr = _STDOUT, _STDERR
        d = builtins.__dict__
        want = _dict(self.pre)
        for k, v in _BUILTINS.items():
            want[k] = v  # import-time originals win over anything changed since
        for k in _list(d.keys()):
            if k not in want:
                try:
                    _delattr(builtins, k)
                except _BaseException:
                    pass
        for k, v in want.items():
            if d.get(k, None) is not v:
                try:
                    _setattr(builtins, k, v)
                except _BaseException:
                    pass
        time.sleep = _sleep
        for m, v in self.saved_mods.items():
            if v == "__absent__":
                sys.modules.pop(m, None)
            else:
                sys.modules[m] = v
        try:
            if sys.getrecursionlimit() != _RLIMIT:
                sys.setrecursionlimit(_RLIMIT)
        except _BaseException:
            pass
        _restore_self()
        return tampered


def _walk_nodes(n, acc):
    """Own AST walker (Brython's ast.walk/iter_child_nodes are broken)."""
    acc.append(n)
    try:
        d = vars(n)
    except TypeError:
        d = {}
    if not d and hasattr(n, "_fields"):
        d = {k: getattr(n, k, None) for k in n._fields}
    for k, v in list(d.items()):
        if k.startswith("_"):
            continue
        if isinstance(v, list):
            for x in v:
                if type(x).__module__ == "ast" or hasattr(x, "_fields"):
                    _walk_nodes(x, acc)
        elif type(v).__module__ == "ast" or hasattr(v, "_fields"):
            _walk_nodes(v, acc)
    return acc


# ================= errors =================
def _clean_msg(name, msg):
    """Remove Brython debug junk and use CPython's wording where Brython differs."""
    msg = msg.rstrip()
    if msg.endswith(" VVV"):
        msg = msg[:-4].rstrip()
    k = msg.rfind("during iteration ")
    if k >= 0 and msg[k + 17:].strip().isdigit():
        msg = msg[:k + 16]
    if name == "TypeError" and msg.startswith("unsupported operand type(s) for +: 'str' and '") and msg.endswith("'"):
        other = msg[len("unsupported operand type(s) for +: 'str' and '"):-1]
        msg = 'can only concatenate str (not "%s") to str' % other
    if name == "TypeError" and msg.startswith("Can't multiply sequence"):
        msg = "c" + msg[1:]
    if name == "ZeroDivisionError" and msg == "float modulo":
        msg = "float modulo by zero"
    return msg


def _frames(e):
    """[(line, funcname)] for the learner's own frames, outermost first."""
    fr = []
    try:
        tb = e.__traceback__
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == FILENAME:
                fr.append((tb.tb_lineno, tb.tb_frame.f_code.co_name))
            tb = tb.tb_next
    except _BaseException:
        pass
    return fr


def _error_info(e, code, syntax_override=None):
    """-> dict(etype, msg, line, trace, text)."""
    name = _type(e).__name__
    try:
        msg = _str(e)
    except _BaseException:
        msg = ""
    if _isinstance(e, _Note):
        return {"etype": None, "msg": msg, "line": None, "trace": None, "text": msg}
    is_syn = _isinstance(e, _SyntaxError)
    if is_syn:
        msg = _getattr(e, "msg", None) or msg
    if name in ("JavascriptError", "InternalError") or "call stack size" in msg or "too much recursion" in msg:
        name, msg = "RecursionError", "maximum recursion depth exceeded"
    msg = _clean_msg(name, msg)
    lines = code.split("\n")
    nlines = _len(lines)
    while nlines > 1 and not lines[nlines - 1].strip():
        nlines -= 1
    fr = [] if is_syn else _frames(e)
    line = fr[-1][0] if fr else None
    if is_syn:
        line = _getattr(e, "lineno", None)
        if syntax_override:
            name, m2, line = syntax_override
            if m2:
                msg = m2
        if line and line > nlines:
            line = nlines
        if name == "SyntaxError" and msg in ("unexpected indent", "unindent does not match any outer indentation level"):
            name = "IndentationError"
    head = name + (": " + msg if msg else "")
    text = head + ("  (line %s)" % line if line else "")

    def src(n):
        return lines[n - 1].strip() if n and 0 < n <= _len(lines) else ""

    if is_syn:
        tr = ['  File "your code", line %s' % line] if line else []
        if src(line):
            tr.append("    " + src(line))
        trace = "\n".join(tr + [head])
    elif fr:
        tr = ["Traceback (most recent call last):"]
        shown = []
        i = 0
        while i < _len(fr):  # collapse runaway recursion like CPython does
            j = i
            while j + 1 < _len(fr) and fr[j + 1] == fr[i]:
                j += 1
            reps = j - i + 1
            for r in _range(_min(reps, 3)):
                shown.append(fr[i])
            if reps > 3:
                shown.append(("rep", reps - 3))
            i = j + 1
        if _len(shown) > 12:
            shown = shown[:3] + [("cut", _len(shown) - 9)] + shown[-6:]
        for f in shown:
            if f[0] == "rep":
                tr.append("  [Previous line repeated %d more times]" % f[1])
            elif f[0] == "cut":
                tr.append("  ... (%d more lines)" % f[1])
            else:
                fn = f[1] if f[1] and f[1] != "<module>" else "<module>"
                tr.append('  File "your code", line %s, in %s' % (f[0], fn))
                if src(f[0]):
                    tr.append("    " + src(f[0]))
        trace = "\n".join(tr + [head])
    else:
        trace = head
    return {"etype": name, "msg": msg, "line": line, "trace": trace, "text": text}


def _fmt_error(e, code=""):
    return _error_info(e, code)["text"]


# ================= running =================
def _compile_learner(code, sess, notes):
    """Compile with the loop guard. Raises SyntaxError (with a corrected line in Brython)."""
    lx = _Lex(code)
    if BRYTHON and "\t" in code:
        p = _scan_problem(lx)
        if p and p[0] == "TabError":
            raise _SyntaxErrorWith(p)
    try:
        _compile(code, FILENAME, "exec")
    except _SyntaxError as e:
        if BRYTHON:
            p = _scan_problem(lx)
            bl = _getattr(e, "lineno", None) or 10 ** 9
            if p and p[2] <= bl:
                try:
                    e._lime_override = p
                except _BaseException:
                    raise _SyntaxErrorWith(p)
        raise
    guarded = _rewrite(code, sess.gname, sess.wname, lx)
    try:
        return _compile(guarded, FILENAME, "exec")
    except _SyntaxError:
        notes.append("Lime could not add its loop guard to this code, so a runaway loop will not be stopped early.")
        return _compile(code, FILENAME, "exec")


class _SyntaxErrorWith(SyntaxError):
    def __init__(self, p):
        SyntaxError.__init__(self, p[1] or "invalid syntax")
        self.msg = p[1] or "invalid syntax"
        self.lineno = p[2]
        self._lime_override = p


def _run(code, ns, sess):
    """Run learner code in ns. Returns (printed, error_info_or_None)."""
    buf = _StringIO()
    err = None
    sess.reset()
    sess.enter()
    sys.stdout = sys.stderr = buf
    try:
        try:
            c = _compile_learner(code, sess, sess.notes)
        except _SyntaxError as e:
            err = _error_info(e, code, _getattr(e, "_lime_override", None))
            c = None
        if c is not None:
            _exec(c, ns)
    except _BaseException as e:
        if _isinstance(e, _SystemExit) or e is _SystemExit:
            fr = _frames(e) if _isinstance(e, _BaseException) else []
            sess._note("Your program stopped early at sys.exit()%s. That is not an error." % (" (line %d)" % fr[-1][0] if fr else ""))
        else:
            err = _error_info(e, code)
    finally:
        tampered = sess.leave()
    if tampered and err is None:
        err = {"etype": "RuntimeError", "msg": "Your code changed Lime's loop guard, so the result cannot be trusted.", "line": None,
               "trace": None, "text": "RuntimeError: Your code changed Lime's loop guard, so the result cannot be trusted."}
    if BRYTHON and "__doc__" in code:
        sess._note("Lime's Python (Brython) drops docstrings, so f.__doc__ is None here; real Python shows the text. help(f) does show it.")
    if BRYTHON:
        try:
            for name, val in _list(ns.items()):
                if _callable(val) and _getattr(val, "__doc__", None) is None:
                    dm = sess._doc_map()
                    if name in dm and dm[name][1]:
                        try:
                            val.__doc__ = dm[name][1]
                        except _BaseException:
                            pass
        except _BaseException:
            pass
    return buf.getvalue(), err


def _new_ns():
    return {"__name__": "__main__"}


def run_code(code, tests_src=""):
    _restore_self()
    code = _str(code).replace("\r\n", "\n")
    notes = []
    sess = _Session(code, notes)
    ns = _new_ns()
    out, err = _run(code, ns, sess)
    if _len(out) > 20000:
        out = out[:20000] + "\n... output cut ..."
    results = []
    if tests_src and err is None:
        _run_tests(code, tests_src, ns, out, sess, results)
    e = err or {}
    return _jdump({"out": out, "error": e.get("text"), "results": results, "etype": e.get("etype"),
                   "eline": e.get("line"), "trace": e.get("trace"), "notes": notes})


def _run_tests(code, tests_src, ns, out, sess, results):
    guard_reset = sess.reset

    def detail_of(e):
        if _isinstance(e, _KeyError) and _len(e.args) == 1 and _isinstance(e.args[0], _str) and e.args[0] not in ns and not _frames(e):
            return "Your code no longer defines `%s`, and the checker needs it. Keep that name, spelled exactly, and give it a value." % e.args[0]
        return _error_info(e, code)["text"]

    def recheck():
        sess.leave()
        sess.enter()
        sys.stdout = sys.stderr = sess.sink

    def check(label, cond, hint=""):
        guard_reset()
        ok = False
        detail = ""
        try:
            v = cond() if _callable(cond) else cond
            recheck()
            ok = _bool(v) is True
        except _BaseException as e:
            recheck()
            detail = detail_of(e)
        results.append({"label": _str(label), "ok": ok, "hint": _str(hint), "detail": _str(detail)})

    def rerun(old, new):
        if old not in code:
            raise _Note("Keep the line `%s` exactly as it is, so the checker can try other values." % old)
        ns2 = _new_ns()
        sub = _Session(code.replace(old, new), sess.notes)
        sub.st["max"], sub.st["budget"] = sess.st["max"], sess.st["budget"]
        sess.leave()
        out2, err2 = _run(code.replace(old, new), ns2, sub)
        sess.enter()
        sys.stdout = sys.stderr = sess.sink
        if sub.st["tripped"]:
            sess.st["tripped"] = True
        if err2:
            raise _Note("With another starting value your code failed: " + err2["text"])
        return ns2, out2

    _tree = {}

    def all_nodes():
        if "n" not in _tree:
            import ast
            try:
                _tree["n"] = _walk_nodes(ast.parse(code), [])
            except _BaseException:
                _tree["n"] = []
        return _tree["n"]

    def has_node(*names):
        """True if the student's code contains any AST node type named, e.g. has_node("For", "While"), has_node("FloorDiv")."""
        got = _set([_type(n).__name__ for n in all_nodes()])
        return _any([x in got for x in names])

    def uses_call(fname):
        """True if the code calls fname(...) or something.fname(...)."""
        for n in all_nodes():
            if _type(n).__name__ == "Call":
                f = _getattr(n, "func", None)
                if _getattr(f, "id", None) == fname or _getattr(f, "attr", None) == fname:
                    return True
        return False

    def silent(fn, *a, **k):
        """Call fn and capture what it prints: returns (result, printed_text)."""
        buf = _StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            r = fn(*a, **k)
        finally:
            sys.stdout = old
        return r, buf.getvalue()

    class _Spy:
        def __init__(self, name):
            if name not in ns:
                raise _Note("Your code no longer defines `%s`, and the checker needs it. Keep that name, spelled exactly." % name)
            self.name = name
            self.calls = 0
            self.orig = ns[name]
            spy_self = self

            def wrapper(*a, **k):
                spy_self.calls += 1
                return spy_self.orig(*a, **k)
            ns[name] = wrapper

        def reset(self):
            self.calls = 0

    def spy(name):
        """Wrap ns[name] so calls (including recursive ones through the global name) are counted: s = spy("fact"); ns["fact"](5); s.calls"""
        return _Spy(name)

    def check_eq(label, fn, expected, hint=""):
        """Like check, but compares with == and the same types (1 vs 1.0, list vs tuple) and reports expected vs got."""
        guard_reset()
        ok = False
        detail = ""
        try:
            got = fn() if _callable(fn) else fn
            recheck()
            ok = _same(got, expected)
            if not ok:
                detail = "Expected %s, got %s." % (_safe_repr(expected), _safe_repr(got))
        except _BaseException as e:
            recheck()
            detail = detail_of(e)
        results.append({"label": _str(label), "ok": ok, "hint": "" if ok else _str(hint), "detail": _str(detail)})

    tns = {"ns": ns, "out": out, "code": code, "check": check, "rerun": rerun,
           "check_eq": check_eq, "eq": _same, "has_node": has_node, "uses_call": uses_call, "silent": silent,
           "spy": spy, "code_bare": _strip_comments_src(code)}
    sess.enter()
    sys.stdout = sys.stderr = sess.sink
    try:
        _exec(_compile(tests_src, "tests", "exec"), tns)
    except _BaseException as e:
        recheck()
        results.append({"label": "checker", "ok": False, "hint": "", "detail": detail_of(e)})
    finally:
        sess.leave()


def _same(a, b):
    """Strict equality: same types all the way down (1 vs 1.0, list vs tuple, True vs 1 differ), so objects
    whose __eq__ always says True cannot pass. Available to tests as eq(a, b)."""
    ta, tb = _type(a), _type(b)
    if ta is not tb:
        return False
    if ta is _list or ta is _tuple:
        return _len(a) == _len(b) and _all([_same(x, y) for x, y in zip(a, b)])
    if ta is _dict:
        return _len(a) == _len(b) and _all([(k in b) and _same(a[k], b[k]) for k in a])
    if ta in (_int, _float, _str, _bool, _set, frozenset, _type(None), bytes, complex, range):
        return _bool(a == b) is True
    return _bool(a == b) is True and _bool(b == a) is True


_SELF = None


def _restore_self():
    """Put back this module's own names if learner code reached them (e.g. via sys.modules)."""
    if _SELF is None:
        return
    g = globals()
    for k, v in _SELF.items():
        if g.get(k) is not v:
            g[k] = v


_SELF = dict(globals())


if window is not None:
    window.pyRun = run_code
    window.pyReady = True
else:
    # Web Worker entry point: app.html runs learner code in a worker, where there is no window.
    # The worker's JS takes pyRun once at start-up and then deletes it from the worker's globals.
    try:
        import browser as _browser
        if getattr(_browser, "is_webworker", False):
            _browser.self.pyRun = run_code
            _browser.self.pyReady = True
    except Exception:
        pass
