"""d02: runner.py hardening. Runs a table of tricky snippets through run_code() in CPython and in real Brython
(headless Chrome via bt.html) and asserts outputs, errors, line numbers, tracebacks and grading.

    python3 tests/d02_runner.py            # both engines
    python3 tests/d02_runner.py cpython    # CPython only
Cases run in order in one interpreter, so tamper cases also prove nothing leaks into the next run.
"""
import asyncio, functools, http.server, json, os, sys, threading, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../lime
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

STOP = "loop ran for too long"
TB_ZERO = """Traceback (most recent call last):
  File "your code", line 6, in <module>
    print(g())
  File "your code", line 5, in g
    return f(0)
  File "your code", line 2, in f
    return 1/x
ZeroDivisionError: division by zero"""

# (name, code, tests, expectations)
# expectations: out, out_has, err (exact), err_has, etype (str or tuple), eline, trace, trace_has, notes_has,
#               ok (list of bools), detail_has {i: text}, detail_not {i: text}, no_error
CASES = [
    # ---- 1. loop guard ----
    ("while( no space", "n = 0\nwhile(n >= 0):\n    n += 1\n", "", {"err_has": STOP, "etype": "RuntimeError", "eline": 2}),
    ("one-line while", "n = 0\nwhile n >= 0: n += 1\n", "", {"err_has": STOP, "eline": 2}),
    ("big for range", "t = 0\nfor i in range(10 ** 9):\n    t += i\n", "", {"err_has": STOP, "eline": 2}),
    ("nested while in for", "for i in range(3):\n    while True:\n        pass\n", "", {"err_has": STOP, "eline": 2}),
    ("list comprehension", "x = [i for i in range(10 ** 9)]\n", "", {"err_has": STOP, "eline": 1}),
    ("generator in sum", "print(sum(i for i in range(10 ** 9)))\n", "", {"err_has": STOP}),
    ("while inside function", "def f(n):\n    while n != 0:\n        n -= 2\n    return n\nprint(f(3))\n", "", {"err_has": STOP, "eline": 2,
                                                                                                                  "trace_has": ['line 5, in <module>', 'line 2, in f']}),
    ("old guard name is useless", "__lime_guard__ = lambda: True\nwhile True:\n    pass\n", "", {"err_has": STOP}),
    ("globals cannot reach the guard", "for k in list(globals()):\n    if k.startswith('_'):\n        globals()[k] = lambda *a: True\nwhile True: pass\n", "", {"err_has": STOP}),
    ("friendly stop message", "while True: pass\n", "", {"err_has": "Lime stopped your program"}),
    ("strings untouched", 's = """\nwhile x:\nfor i in y:\n"""\nprint(s)\nprint("while(1): for x in y:")\n', "", {"out": "\nwhile x:\nfor i in y:\n\nwhile(1): for x in y:\n"}),
    ("comment untouched", "x = 1  # while x: for y in z:\nprint(x)\n", "", {"out": "1\n"}),
    ("for over tuple", "for x in 1, 2:\n    print(x)\n", "", {"out": "1\n2\n"}),
    ("for/else and while/else", "for i in range(2):\n    pass\nelse:\n    print('f', i)\nj = 0\nwhile j < 2:\n    j += 1\nelse:\n    print('w', j)\n", "", {"out": "f 1\nw 2\n"}),
    ("walrus in while", "data = [3, 2, 1]\nwhile (n := len(data)) > 1:\n    data.pop()\nprint(n, data)\n", "", {"out": "1 [3]\n"}),
    ("walrus bare in while", "it = iter([1, 2, 0, 5])\nwhile x := next(it):\n    print(x)\n", "", {"out": "1\n2\n"}),
    ("lambda in while", "while (lambda: False)(): pass\nf = lambda: 0\nprint('ok', f())\n", "", {"out": "ok 0\n"}),
    ("dict/nested/filtered comps", "d = {k: v for k, v in zip('ab', range(2))}\nm = [[j for j in range(i)] for i in range(3)]\ne = [x for x in range(10) if x % 2 if x > 2 for y in range(1)]\nprint(d, m, e)\n", "",
     {"out": "{'a': 0, 'b': 1} [[], [0], [0, 1]] [3, 5, 7, 9]\n"}),
    ("comprehension in f-string", 'print(f"{[i for i in range(3)]}")\n', "", {"out": "[0, 1, 2]\n"}),
    ("class body comprehension", "class K:\n    vals = [a * 2 for a in range(3)]\nprint(K.vals)\n", "", {"out": "[0, 2, 4]\n"}),
    ("generator with while", "def gen():\n    i = 0\n    while i < 3:\n        yield i\n        i += 1\nprint(list(gen()))\n", "", {"out": "[0, 1, 2]\n"}),
    ("backslash continuation", "x = 1 + \\\n    2\ni = 0\nwhile i < \\\n  3:\n    i += 1\nprint(x, i)\n", "", {"out": "3 3\n"}),
    ("append while iterating (CPython semantics)", "x = [1]\nfor i in x:\n    if len(x) < 5:\n        x.append(i)\nprint(x)\n", "", {"out": "[1, 1, 1, 1, 1]\n"}),
    ("enumerate/zip/dict loops", "d = {'a': 1, 'b': 2}\nfor k, v in d.items():\n    print(k, v)\nfor i, (a, b) in enumerate(zip('xy', 'pq')):\n    print(i, a + b)\n", "", {"out": "a 1\nb 2\n0 xp\n1 yq\n"}),
    ("for over int still errors", "for x in 5:\n    pass\n", "", {"etype": "TypeError", "eline": 1, "err_has": "not iterable"}),
    ("runtime error line inside loop", "for i in range(3):\n    print(10 // (1 - i))\n", "", {"out": "10\n", "etype": "ZeroDivisionError", "eline": 2}),
    # ---- 2. emoji / astral characters ----
    ("emoji in comment", 'print("Hello, Lime!")  # done \U0001F600\n', "", {"out": "Hello, Lime!\n"}),
    ("emoji in string with loop", 'i = 0\nwhile i < 2: i += 1; print("\U0001F600", i)\n', "", {"out": "\U0001F600 1\n\U0001F600 2\n"}),
    ("escaped emoji prints right", 'print("\\U0001F600", len("\\U0001F600"))\n', "", {"out": "\U0001F600 1\n"}),
    ("escaped emoji in f-string", 'n = 2\nprint(f"\\U0001F34B x{n}")\n', "", {"out": "\U0001F34B x2\n"}),
    ("raw string keeps backslash", 'print(r"\\U0001F600")\n', "", {"out": "\\U0001F600\n"}),
    ("escaped backslash then U", 'print("\\\\U0001F600")\n', "", {"out": "\\U0001F600\n"}),
    ("emoji with checks", 'msg = "hi \U0001F600"\n', "check_eq('msg', lambda: ns['msg'], 'hi \U0001F600')\ncheck('bare', '\U0001F600' in code_bare)", {"ok": [True, True]}),
    ("unicode name", "caf\u00e9 = 1\nprint(caf\u00e9)\n", "", {"out": "1\n"}),
    # ---- 3. syntax error lines ----
    ("unexpected indent t5", "print(135 // 60)\n    print(135 % 60)\n\n\n\n", "", {"err": "IndentationError: unexpected indent  (line 2)", "eline": 2, "etype": "IndentationError"}),
    ("unexpected indent first line", "    x = 1\nprint(x)", "", {"etype": "IndentationError", "eline": 1}),
    ("unexpected indent mid", "x = 1\n    y = 2\nz=3\nw=4\nq=5", "", {"etype": "IndentationError", "eline": 2,
                                                                     "trace": '  File "your code", line 2\n    y = 2\nIndentationError: unexpected indent'}),
    ("unterminated string", 's = "abc\nprint(1)\n', "", {"err": "SyntaxError: unterminated string literal (detected at line 1)  (line 1)"}),
    ("unterminated triple string", 'x = 1\ns = """abc\nprint(1)\n', "", {"err": "SyntaxError: unterminated triple-quoted string literal (detected at line 3)  (line 2)"}),
    ("tab after spaces", "if True:\n    a = 1\n\tb = 2\n", "", {"etype": "TabError", "eline": 3, "err_has": "inconsistent use of tabs and spaces"}),
    ("spaces after tab", "if True:\n\ta = 1\n        b = 2\n", "", {"etype": "TabError", "eline": 3}),
    ("tabs only is fine", "if True:\n\tprint(1)\n\tif True:\n\t\tprint(2)\n", "", {"out": "1\n2\n"}),
    ("unindent mismatch", "for i in range(3):\n    pass\n  print(i)\n", "", {"etype": "IndentationError", "eline": 3, "err_has": "unindent does not match"}),
    ("expected indented block", "if True:\nprint(1)\n", "", {"etype": "IndentationError", "eline": 2, "err_has": "expected an indented block"}),
    ("missing colon", "if True\n    print(1)\n", "", {"etype": "SyntaxError", "eline": 1, "err_has": "expected ':'"}),
    ("never closed", "print((1)\nx = 2\n", "", {"etype": "SyntaxError", "eline": 1, "err_has": "was never closed"}),
    ("smart quotes", "x = \u201chi\u201d\n", "", {"etype": "SyntaxError", "eline": 1, "err_has": "invalid character"}),
    ("syntax error after blank tail", "x = 1\nprint(x))\n\n\n", "", {"etype": "SyntaxError", "eline": 2}),
    # ---- 4. tracebacks ----
    ("traceback", "def f(x):\n    return 1/x\n\ndef g():\n    return f(0)\nprint(g())\n", "", {"trace": TB_ZERO, "err": "ZeroDivisionError: division by zero  (line 2)", "etype": "ZeroDivisionError", "eline": 2}),
    ("module-level error trace", "x = [1, 2]\nprint(x[5])\n", "", {"trace": 'Traceback (most recent call last):\n  File "your code", line 2, in <module>\n    print(x[5])\nIndexError: list index out of range'}),
    ("no error fields", "print(1)\n", "", {"no_error": True, "out": "1\n"}),
    # ---- 5. messages and friendly replacements ----
    ("recursion", "def f(n):\n    return f(n + 1)\nf(0)\n", "", {"etype": "RecursionError", "trace_has": ["[Previous line repeated", "line 2, in f"], "eline": 2}),
    ("recursion after raising the limit", "import sys\nsys.setrecursionlimit(20000)\ndef f(n):\n    return f(n + 1)\nf(0)\n", "", {"etype": "RecursionError"}),
    ("recursion depth 950 works", "def f(n):\n    return 0 if n == 0 else 1 + f(n - 1)\nprint(f(950))\n", "", {"out": "950\n"}),
    ("no VVV", "print(len(5))\n", "", {"err": "TypeError: object of type 'int' has no len()  (line 1)"}),
    ("no iteration count", "d = {1: 1}\nfor k in d:\n    d[k + 1] = 1\n", "", {"err": "RuntimeError: dictionary changed size during iteration  (line 2)"}),
    ("str + int wording", "x = 'a' + 1\n", "", {"err": 'TypeError: can only concatenate str (not "int") to str  (line 1)'}),
    ("sys.exit is not an error", "import sys\nprint(1)\nsys.exit()\nprint(2)\n", "", {"out": "1\n", "no_error": True, "notes_has": "sys.exit()"}),
    ("exit() is not an error", "print(1)\nexit()\nprint(2)\n", "", {"out": "1\n", "no_error": True}),
    ("time.sleep passes", "import time\ntime.sleep(2)\nprint('done')\n", "", {"out": "done\n", "notes_has": "time.sleep()"}),
    ("help(own function)", 'def fare(n):\n    """Return the fare in coins."""\n    return n * 2\nhelp(fare)\n', "", {"out_has": ["fare(n)", "Return the fare in coins."], "no_error": True}),
    ("help(len)", "help(len)\n", "", {"out_has": ["Return the number of items"], "no_error": True}),
    ("help()", "help()\n", "", {"out_has": ["help(len)"], "no_error": True}),
    ("docstring kept for tests", 'def fare(n):\n    """Return the fare in coins."""\n    return n * 2\n', "check('doc', lambda: 'fare' in (ns['fare'].__doc__ or ''))", {"ok": [True]}),
    ("input()", "x = input('Name? ')\n", "", {"err_has": "input() is not available", "eline": 1}),
    ("builtins.input()", "import builtins\nbuiltins.input('Name? ')\n", "", {"err_has": "input() is not available"}),
    ("KeyError in tests -> renamed", "totl = 5\n", "check_eq('total', lambda: ns['total'], 5)", {"ok": [False], "detail_has": {0: "no longer defines `total`"}}),
    ("KeyError from learner code stays", "def f():\n    return {}['a']\n", "check_eq('f', lambda: ns['f'](), 1)", {"ok": [False], "detail_has": {0: "KeyError: 'a'  (line 2)"}}),
    ("spy on missing name", "def fac(n):\n    return 1\n", "s = spy('fact')", {"detail_has": {0: "no longer defines `fact`"}}),
    ("rerun without AssertionError", "a = 3\nprint(10 // a)\n", "ns2, o2 = rerun('a = 3', 'a = 0')", {"detail_has": {0: "With another starting value your code failed: ZeroDivisionError"},
                                                                                                "detail_not": {0: "AssertionError"}}),
    ("rerun edited line", "a = 4\nprint(a)\n", "ns2, o2 = rerun('a = 3', 'a = 0')", {"detail_has": {0: "Keep the line `a = 3`"}, "detail_not": {0: "AssertionError"}}),
    ("rerun works", "a = 3\nb = a * 2\n", "ns2, o2 = rerun('a = 3', 'a = 5')\ncheck_eq('b', lambda: ns2['b'], 10)", {"ok": [True]}),
    ("error inside a check", "def f(x):\n    return 1 / x\n", "check_eq('f0', lambda: ns['f'](0), 1)\ncheck_eq('f1', lambda: ns['f'](1), 1.0)",
     {"ok": [False, True], "detail_has": {0: "ZeroDivisionError: division by zero  (line 2)"}}),
    ("runaway loop in checks gives up sooner", "def is_even(n):\n    while n != 0:\n        n -= 2\n    return True\n",
     "check('3', lambda: ns['is_even'](3) is False)\ncheck('5', lambda: ns['is_even'](5) is False)\ncheck('7', lambda: ns['is_even'](7) is False)",
     {"ok": [False, False, False], "detail_has": {0: STOP, 1: STOP, 2: STOP}, "max_s": 12}),
    # ---- 6. tamper resistance ----
    ("patch json.dumps", "import json\njson.dumps = lambda *a, **k: '{\"out\": \"\", \"error\": null, \"results\": [{\"ok\": true}]}'\nx = 1\n",
     "check_eq('x is 2', lambda: ns['x'], 2)", {"ok": [False]}),
    ("next run after json patch", "x = 1\n", "check_eq('x is 2', lambda: ns['x'], 2)", {"ok": [False]}),
    ("patch bool/str/isinstance", "import builtins\nbuiltins.bool = lambda x=0: True\nbuiltins.str = lambda x='': 'x'\nbuiltins.isinstance = lambda *a: True\nbuiltins.len = lambda *a: 0\nx = 1\n",
     "check('x is 2', lambda: ns['x'] == 2)\ncheck_eq('x eq', lambda: ns['x'], 2)", {"ok": [False, False]}),
    ("builtins restored", "print(bool(0), str(5), isinstance(1, str), len([1, 2]), type(print).__name__ != 'function')\n", "", {"out": "False 5 False 2 True\n"}),
    ("always-equal object", "class E:\n    def __eq__(self, o):\n        return True\n    __hash__ = None\ndef cube(n):\n    return E()\n",
     "check_eq('cube 2', lambda: ns['cube'](2), 8)\ncheck('eq helper', lambda: eq(ns['cube'](3), 27))\ncheck('eq list', lambda: eq([ns['cube'](1)], [1]))", {"ok": [False, False, False]}),
    ("int subclass", "class I(int):\n    def __eq__(self, o):\n        return True\n    __hash__ = int.__hash__\ndef cube(n):\n    return I(0)\n", "check_eq('cube', lambda: ns['cube'](2), 8)", {"ok": [False]}),
    ("eq helper true case", "x = [1, (2, 'a'), {'k': 1.5}]\n", "check('eq', lambda: eq(ns['x'], [1, (2, 'a'), {'k': 1.5}]))\ncheck('eq types', lambda: eq(1, 1.0))", {"ok": [True, False]}),
    ("patching during a check", "def f():\n    import builtins\n    builtins.isinstance = lambda *a: True\n    builtins.len = lambda *a: 0\n    builtins.bool = lambda *a: True\n    return [1]\n",
     "check_eq('f', lambda: ns['f'](), [2])\ncheck('after', lambda: len([1]) == 1 and isinstance(1, int))", {"ok": [False, True]}),
    ("browser import blocked", "from browser import window\n", "", {"etype": ("ImportError", "ModuleNotFoundError"), "eline": 1}),
    ("print replaced", "import builtins\nbuiltins.print = None\n", "", {"no_error": True}),
    ("print back", "print('back')\n", "", {"out": "back\n"}),
    ("stdout replaced", "import sys, io\nsys.stdout = io.StringIO()\nprint('hidden')\n", "", {"out": ""}),
    ("stdout back", "print('visible')\n", "", {"out": "visible\n"}),
    ("recursion limit restored", "import sys\nprint(sys.getrecursionlimit() >= 1000)\n", "", {"out": "True\n"}),
    ("sleep restored after run", "import time\nprint(time.sleep.__name__ if hasattr(time.sleep, '__name__') else 'x')\n", "", {"no_error": True}),
    # ---- t4 S1: all()/any() over generators ----
    ("all(gen) raises in code", "print(all(1 / 0 for a in range(3)))\n", "", {"etype": "ZeroDivisionError"}),
    ("all(gen) raises in tests", "x = None\n", "check('all', lambda: all(ns['x'].items() for a in range(3)))", {"ok": [False], "detail_has": {0: "AttributeError"}}),
    ("any(gen) in tests", "x = [1, 2]\n", "check('any', lambda: any(v > 1 for v in ns['x']))\ncheck('all', lambda: all(v > 0 for v in ns['x']))", {"ok": [True, True]}),
    # ---- test helpers ----
    ("code_bare strips comments only", 's = """# not a comment"""\nprint(s)  # real\n', "check_eq('bare', code_bare, 's = \"\"\"# not a comment\"\"\"\\nprint(s)\\n')", {"ok": [True]}),
    ("code_bare defeats comment", "print(604800)  # *\n", "check('uses *', '*' in code_bare)", {"ok": [False]}),
    ("has_node / uses_call / silent", "def f(n):\n    print('x')\n    return sorted([n, 1])\nfor i in range(2):\n    pass\n",
     "check('For', has_node('For'))\ncheck('no While', not has_node('While'))\ncheck('sorted', uses_call('sorted'))\ncheck_eq('silent', lambda: silent(ns['f'], 3), ([1, 3], 'x\\n'))", {"ok": [True, True, True, True]}),
    ("prints during tests do not leak", "def f():\n    print('noise')\n    return 1\n", "check_eq('f', lambda: ns['f'](), 1)", {"ok": [True], "out": ""}),
]


def check_case(name, r, exp, secs):
    bad = []

    def want(cond, msg):
        if not cond:
            bad.append(msg)
    if "out" in exp:
        want(r["out"] == exp["out"], "out %r != %r" % (r["out"], exp["out"]))
    for t in exp.get("out_has", []):
        want(t in r["out"], "out lacks %r: %r" % (t, r["out"]))
    if "err" in exp:
        want(r["error"] == exp["err"], "error %r != %r" % (r["error"], exp["err"]))
    if "err_has" in exp:
        want(r["error"] is not None and exp["err_has"] in r["error"], "error %r lacks %r" % (r["error"], exp["err_has"]))
    if "etype" in exp:
        et = exp["etype"] if isinstance(exp["etype"], tuple) else (exp["etype"],)
        want(r.get("etype") in et, "etype %r not in %r" % (r.get("etype"), et))
        want(r["error"] is not None and r["error"].split(":")[0] == r.get("etype"), "error line does not start with etype: %r" % r["error"])
    if "eline" in exp:
        want(r.get("eline") == exp["eline"], "eline %r != %r (%r)" % (r.get("eline"), exp["eline"], r["error"]))
        if r["error"]:
            want(("(line %d)" % exp["eline"]) in r["error"], "error lacks (line N): %r" % r["error"])
    if "trace" in exp:
        want(r.get("trace") == exp["trace"], "trace %r != %r" % (r.get("trace"), exp["trace"]))
    for t in exp.get("trace_has", []):
        want(r.get("trace") and t in r["trace"], "trace lacks %r: %r" % (t, r.get("trace")))
    if r.get("trace") and r.get("etype"):
        want(r["trace"].split("\n")[-1].startswith(r["etype"]), "trace last line is not the error: %r" % r["trace"])
    if "notes_has" in exp:
        want(any(exp["notes_has"] in n for n in r.get("notes", [])), "notes %r lack %r" % (r.get("notes"), exp["notes_has"]))
    if exp.get("no_error"):
        want(r["error"] is None and r.get("etype") is None and r.get("eline") is None and r.get("trace") is None, "unexpected error %r" % r["error"])
    if "ok" in exp:
        want([x["ok"] for x in r["results"]] == exp["ok"], "ok %r != %r %s" % ([x["ok"] for x in r["results"]], exp["ok"], json.dumps(r["results"])[:300]))
    for i, t in exp.get("detail_has", {}).items():
        want(len(r["results"]) > i and t in r["results"][i]["detail"], "detail[%d] lacks %r: %s" % (i, t, json.dumps(r["results"])[:300]))
    for i, t in exp.get("detail_not", {}).items():
        want(len(r["results"]) > i and t not in r["results"][i]["detail"], "detail[%d] has %r" % (i, t))
    if "max_s" in exp:
        want(secs <= exp["max_s"], "took %.1fs > %ss" % (secs, exp["max_s"]))
    for k in ("out", "error", "results", "etype", "eline", "trace", "notes"):
        want(k in r, "missing JSON field " + k)
    return bad


def report(engine, rows):
    fails = 0
    for name, bad, secs in rows:
        if bad:
            fails += 1
            print("FAIL [%s] %s (%.2fs)" % (engine, name, secs))
            for b in bad:
                print("     ", b)
    print("%s: %d cases, %d failed" % (engine, len(rows), fails))
    return fails


def run_cpython():
    import runner
    rows = []
    for name, code, tests, exp in CASES:
        t0 = time.time()
        r = json.loads(runner.run_code(code, tests))
        secs = time.time() - t0
        rows.append((name, check_case(name, r, exp, secs), secs))
    import json as j2
    assert j2.dumps is json.dumps
    return report("cpython", rows)


def run_brython():
    from playwright.async_api import async_playwright

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    port = int(os.environ.get("LIME_PORT", "8802"))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Quiet, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    async def main():
        rows = []
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
            pg = await b.new_page()
            await pg.goto("http://127.0.0.1:%d/%s/bt.html" % (port, os.path.basename(HERE)))
            await pg.wait_for_function("window.pyReady === true || window.__err", timeout=90000)
            err = await pg.evaluate("window.__err || null")
            if err:
                print("load error:", err)
                return 1
            for name, code, tests, exp in CASES:
                t0 = time.time()
                try:
                    r = json.loads(await pg.evaluate("([c,t]) => window.pyRun(c,t)", [code, tests]))
                except Exception as ex:
                    rows.append((name, ["CRASH " + str(ex)[:300]], time.time() - t0))
                    continue
                secs = time.time() - t0
                rows.append((name, check_case(name, r, exp, secs), secs))
            await b.close()
        return report("brython", rows)
    return asyncio.run(main())


if __name__ == "__main__":
    f = run_cpython()
    if "cpython" not in sys.argv[1:]:
        f += run_brython()
    sys.exit(1 if f else 0)
