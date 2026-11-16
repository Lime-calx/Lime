"""d17: py03/py04 content checks. Run from the repo root: python3 tests/d17_content.py
- the gaming attempts found by the beta testers now fail
- honest alternative solutions still pass
- no ordering of the c03/c04 Parsons lines that uses a decoy passes
- the stuck-tram starter fails fast with small output
"""
import itertools, json, os, runpy, sys, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.chdir(HERE)
from runner import run_code  # noqa: E402

L3 = runpy.run_path("content/l03.py")["LESSON"]
L4 = runpy.run_path("content/l04.py")["LESSON"]
C3 = runpy.run_path("city/c03.py")["CITY"]
C4 = runpy.run_path("city/c04.py")["CITY"]


def item(container, key, ident):
    return [e for e in container[key] if e["id"] == ident][0]


def passes(code, tests):
    r = json.loads(run_code(code, tests))
    return (not r["error"]) and r["results"] and all(x["ok"] for x in r["results"]), r


fails = []


def expect(name, ex, code, want):
    ok, r = passes(code, ex["tests"])
    if bool(ok) != want:
        fails.append("%s: expected %s, got %s %s" % (name, "pass" if want else "fail", "pass" if ok else "fail", json.dumps(r)[:300]))


# ---- gaming attempts must fail ----
fb = item(L3, "exercises", "fizzbuzz")
lit = "last = 15\n# FizzBuzz for 1 to 15\n" + "".join("print(%r)\n" % ("FizzBuzz" if k % 15 == 0 else "Fizz" if k % 3 == 0 else "Buzz" if k % 5 == 0 else str(k)) for k in range(1, 16))
expect("fizzbuzz literal prints", fb, lit, False)

rg = item(L3, "exercises", "range")
expect("range one-line literal", rg, 'last = 5\nprint("1 2 3 4 5")\n', False)
expect("range hardcoded 6", rg, "last = 5\nfor i in range(1, 6):\n    print(i)\n", False)

tt = item(C3, "jobs", "timetable")
expect("timetable hardcoded last", tt, 'start_hour = 6\nevery = 15\nlast = 120\nfor m in range(0, 121, every):\n    print(f"{start_hour + m // 60:02d}:{m % 60:02d}")\n', False)
expect("timetable while loop (honest)", tt, 'start_hour = 6\nevery = 15\nlast = 120\nm = 0\nwhile m <= last:\n    print(f"{start_hour + m // 60:02d}:{m % 60:02d}")\n    m += every\n', True)

st = item(C3, "jobs", "stuck_tram")
expect("stuck_tram literal prints", st, 'stops_left = 5\nprint("Stops left: 5\\nStops left: 4\\nStops left: 3\\nStops left: 2\\nStops left: 1\\nDepot!")\n', False)
expect("stuck_tram for loop (honest)", st, 'stops_left = 5\nfor s in range(stops_left, 0, -1):\n    print("Stops left:", s)\nprint("Depot!")\n', True)
t0 = time.time()
r = json.loads(run_code(st["starter"], st["tests"]))
if time.time() - t0 > 1.0 or len(r["out"]) > 1000:
    fails.append("stuck_tram starter is slow or noisy: %.2fs, %d chars" % (time.time() - t0, len(r["out"])))

lg = item(L3, "exercises", "largest")
expect("largest starting at 0", lg, "readings = [36.8, 38.4, 37.1, 39.0, 37.6]\nhighest = 0\nfor r in readings:\n    if r > highest:\n        highest = r\n", False)
expect("largest with max()", lg, "readings = [36.8, 38.4, 37.1, 39.0, 37.6]\nhighest = max(readings)\n", False)

pr = item(L3, "exercises", "prime")
expect("prime with a flag, no for/else", pr, "n = 97\nis_prime = None\nis_prime = True\nfor d in range(2, n):\n    if n % d == 0:\n        is_prime = False\n        break\n", False)
expect("prime else on the if (wrong)", pr, "n = 97\nis_prime = None\nfor d in range(2, n):\n    if n % d == 0:\n        is_prime = False\n        break\n    else:\n        is_prime = True\n", False)

rp = item(L3, "exercises", "repeat")
expect("repeat without break keeps the last", rp, 'text = "bookkeeper"\nrepeat = None\nprev = None\nfor ch in text:\n    if ch == prev:\n        repeat = ch\n    prev = ch\n', False)

dg = item(L3, "exercises", "digits")
expect("digits via str", dg, "n = 4096\ntotal = 0\nfor ch in str(n):\n    total += int(ch)\n", False)

fa = item(L4, "exercises", "fact")
expect("fact loop with comment", fa, "def fact(n):\n    # fact( fact(\n    r = 1\n    for k in range(2, n + 1):\n        r *= k\n    return r\n", False)
expect("fact via math.factorial", fa, "import math\ndef fact(n):\n    return math.factorial(n)\nfact(1)\n", False)

fi = item(L4, "exercises", "fib")
expect("fib naive recursion", fi, "def fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n", False)
expect("fib while loop (honest)", fi, "def fib(n):\n    a, b = 0, 1\n    while n > 0:\n        a, b = b, a + b\n        n -= 1\n    return a\n", True)

cu = item(L4, "exercises", "cube")
expect("cube prints and returns", cu, "def cube(x):\n    print(x * x * x)\n    return x * x * x\n", False)

gr = item(L4, "exercises", "grade")
expect("grade with > 50", gr, 'def grade(score):\n    if score > 90:\n        return "distinction"\n    if score > 50:\n        return "pass"\n    return "fail"\n', False)
expect("grade lookup", gr, 'def grade(score):\n    return {49: "fail", 50: "pass", 89: "pass", 90: "distinction", 100: "distinction", 0: "fail", 70: "pass"}[score]\n', False)

pu = item(L4, "exercises", "pure")
expect("pure keeps global", pu, "visits = 0\n\ndef add_visit(count):\n    global visits\n    visits = count + 1\n    return visits\n\nvisits = add_visit(visits)\nvisits = add_visit(visits)\nprint(visits)\n", False)

ie = item(L4, "exercises", "is_even")
expect("is_even lookup table", ie, "def is_even(n):\n    return {4: True, 7: False, 0: True, -4: True, -3: False}[n]\n", False)

sp = item(C4, "jobs", "speed")
expect("speed prints and returns", sp, 'def average_speed(distance, minutes):\n    print(distance / minutes * 60)\n    return distance / minutes * 60\n\nspeed = average_speed(12, 30)\nprint(f"Speed: {speed} km/h")\n', False)


# ---- Parsons: no ordering that contains a decoy may pass ----
def parsons_exhaustive(lid, p):
    bad, good = [], 0
    pool = p["lines"] + p["distractors"]
    nd = len(p["distractors"])
    for k in range(0, nd + 1):
        for decoys in itertools.combinations(p["distractors"], k):
            for perm in itertools.permutations(p["lines"] + list(decoys)):
                ok, _ = passes("\n".join(perm) + "\n", p["tests"])
                if ok:
                    if k:
                        bad.append(perm)
                    else:
                        good += 1
    if bad:
        fails.append("%s %s: %d orderings with a decoy pass, e.g. %r" % (lid, p["id"], len(bad), bad[0]))
    if good < 1:
        fails.append("%s %s: intended order does not pass" % (lid, p["id"]))
    return good


for lid, C in (("py03", C3), ("py04", C4)):
    for p in C["parsons"]:
        parsons_exhaustive(lid, p)

# ---- structure ----
for C in (C3, C4):
    if len(C["nit_right"]) != 3:
        fails.append("%s: nit_right needs 3 lines" % C["lesson"])
    if not (3 <= len(C["teach"]["points"]) <= 4):
        fails.append("%s: teach points" % C["lesson"])
    for t in C["terms"]:
        if not t["ex"]:
            fails.append("%s term %s has no example" % (C["lesson"], t["term"]))
if not any([b["t"] == "note" and b["k"] == "deep" for b in L3["blocks"]]):
    fails.append("py03 has no deep notes")
if "```" not in C3["scene"]:
    fails.append("c03 scene lacks the tram program")
for L in (L3, L4):
    for p in L["predict"]:
        if not p.get("traps"):
            fails.append("%s %s has no traps" % (L["id"], p["id"]))
    for c in L["cards"]:
        if "```" in c["f"]:
            fails.append("%s card %s uses a fenced block (card fronts render inline only)" % (L["id"], c["id"]))

print("fails:", len(fails))
for f in fails:
    print(" -", f)
sys.exit(1 if fails else 0)
