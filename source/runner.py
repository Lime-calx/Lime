"""Lime runner: runs student code and checks it. Works in Brython (browser) and CPython (build-time validation)."""
import sys, json, re, time
from io import StringIO

try:
    from browser import window
except Exception:
    window = None

MAX_ITERS = 2000000
BUDGET = 6.0
_WHILE = re.compile(r'^([ \t]*)while[ \t]+(.+?):[ \t]*(#.*)?$', re.M)


class _Guard:
    def __init__(self):
        self.reset()

    def reset(self):
        self.n = 0
        self.t = time.time()

    def __call__(self):
        self.n += 1
        if self.n > MAX_ITERS or (self.n % 5000 == 0 and time.time() - self.t > BUDGET):
            raise RuntimeError("Stopped: a loop ran for too long. Does a while loop never end?")
        return True


def _prep(code):
    def sub(m):
        tail = (" " + m.group(3)) if m.group(3) else ""
        return "%swhile __lime_guard__() and (%s):%s" % (m.group(1), m.group(2), tail)
    return _WHILE.sub(sub, code)


def _fmt_error(e):
    name = e.__class__.__name__
    msg = str(e)
    line = None
    try:
        tb = e.__traceback__
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == "student":
                line = tb.tb_lineno
            tb = tb.tb_next
    except Exception:
        pass
    if isinstance(e, SyntaxError) and getattr(e, "lineno", None):
        line = e.lineno
    out = name + (": " + msg if msg else "")
    if line:
        out += "  (line %s)" % line
    return out


def _input(prompt=""):
    raise RuntimeError("input() is not available in Lime. Put the value in a variable instead.")


def _new_ns(guard):
    return {"__name__": "__main__", "__lime_guard__": guard, "input": _input}


def _run(code, ns):
    buf = StringIO()
    old = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf
    err = None
    try:
        exec(compile(_prep(code), "student", "exec"), ns)
    except BaseException as e:
        err = _fmt_error(e)
    finally:
        sys.stdout, sys.stderr = old
    return buf.getvalue(), err


def run_code(code, tests_src="", ):
    guard = _Guard()
    ns = _new_ns(guard)
    out, err = _run(code, ns)
    if len(out) > 20000:
        out = out[:20000] + "\n... output cut ..."
    results = []
    if tests_src and err is None:
        def check(label, cond, hint=""):
            guard.reset()
            ok = False
            detail = ""
            try:
                ok = bool(cond() if callable(cond) else cond)
            except BaseException as e:
                detail = _fmt_error(e)
            results.append({"label": label, "ok": ok, "hint": hint, "detail": detail})

        def rerun(old, new):
            if old not in code:
                raise AssertionError("Keep the line `%s` exactly as it is, so the checker can try other values." % old)
            guard.reset()
            ns2 = _new_ns(guard)
            out2, err2 = _run(code.replace(old, new), ns2)
            if err2:
                raise AssertionError("With another starting value your code failed: " + err2)
            return ns2, out2

        tns = {"ns": ns, "out": out, "code": code, "check": check, "rerun": rerun}
        try:
            exec(compile(tests_src, "tests", "exec"), tns)
        except BaseException as e:
            results.append({"label": "checker", "ok": False, "hint": "", "detail": _fmt_error(e)})
    return json.dumps({"out": out, "error": err, "results": results})


if window is not None:
    window.pyRun = run_code
    window.pyReady = True
