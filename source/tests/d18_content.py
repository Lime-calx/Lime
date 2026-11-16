"""d18: py05/py06 content checks. Run from the repo root: python3 tests/d18_content.py

Proves that the classic wrong answers named in the beta reports are now caught by the tests
(with a teaching hint), that the right-but-different answers still pass, and that the
corrected facts in the lesson text are present."""
import json, os, runpy, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.chdir(HERE)
from runner import run_code  # noqa: E402

L5 = runpy.run_path("content/l05.py")["LESSON"]
L6 = runpy.run_path("content/l06.py")["LESSON"]
C5 = runpy.run_path("city/c05.py")["CITY"]
C6 = runpy.run_path("city/c06.py")["CITY"]
fails = []


def ex(L, eid):
    for e in L.get("exercises", L.get("jobs", [])):
        if e["id"] == eid:
            return e
    raise KeyError(eid)


def run(e, code):
    r = json.loads(run_code(code, e["tests"]))
    return r


def expect(name, e, code, ok, hint_has=None):
    r = run(e, code)
    passed = not r["error"] and r["results"] and all(x["ok"] for x in r["results"])
    if passed != ok:
        fails.append("%s: expected %s, got %s %s" % (name, "pass" if ok else "fail", "pass" if passed else "fail", json.dumps(r)[:400]))
        return
    if hint_has:
        hints = " ".join(x["hint"] + " " + x["detail"] for x in r["results"] if not x["ok"])
        if hint_has not in hints:
            fails.append("%s: failing hint should mention %r, got %r" % (name, hint_has, hints[:300]))


# --- py05 ---
caesar = ex(L5, "caesar")
expect("caesar with islower() mangles accents", caesar,
       'def caesar(text, shift):\n    r = ""\n    for ch in text:\n        if ch.islower():\n            r += chr((ord(ch) - 97 + shift) % 26 + 97)\n        elif ch.isupper():\n            r += chr((ord(ch) - 65 + shift) % 26 + 65)\n        else:\n            r += ch\n    return r\n',
       False, "a\" <= ch <= \"z")
expect("caesar model solution", caesar, caesar["solution"], True)

last = ex(L5, "last_three")
expect("last_three with len(s) - 3", last, "def last_three(s):\n    return s[len(s) - 3:]\n", False, "counts from the END")

title = ex(L5, "title_case")
expect("title_case via title()", title, "def title_case(s):\n    return s.title()\n", False, "apostrophe")
expect("title_case via join", title, 'def title_case(s):\n    return " ".join([w[0].upper() + w[1:].lower() for w in s.split()])\n', True)

pp = ex(L5, "parse_pair")
expect("parse_pair with split('=')", pp, 'def parse_pair(text):\n    k, v = text.split("=")\n    return k.strip(), v.strip()\n', False)
expect("parse_pair with split('=', 1)", pp, 'def parse_pair(text):\n    if "=" not in text:\n        return text.strip(), ""\n    k, v = text.split("=", 1)\n    return k.strip(), v.strip()\n', True)

model = " ".join(b["x"] for b in L5["blocks"] if b["t"] == "note")
if "and `len(s[a:b])` is `b - a`" in model or "<= len(s)`, `len(s[a:b])`" not in model:
    fails.append("l05 still states len(s[a:b]) == b - a unconditionally")
if "step of 0" not in model:
    fails.append("l05 slice trap should mention that a step of 0 is an error")
if any(["repr(" in b["x"] for b in L5["blocks"][:12] if b["t"] == "code"]):
    fails.append("repr() used in an l05 code block before the str/repr section")
ids5 = [c["id"] for c in L5["cards"]]
if "c9" in ids5 or "c-why-mod26" not in ids5:
    fails.append("Caesar formula card should be replaced by the 'why % 26' card")
preds5 = {p["id"]: p for p in L5["predict"]}
for pid in ("p-neg-step", "p-compare", "p-repr", "p-strip", "p-fwidth"):
    if pid not in preds5 or not preds5[pid].get("traps"):
        fails.append("l05 prediction %s missing or without traps" % pid)
if "```" not in C5["scene"] or len(C5["nit_right"]) != 3:
    fails.append("c05 scene payload / nit_right missing")

# --- py06 ---
mv = ex(L6, "moving")
expect("moving_average with //", mv, "def moving_average(nums, window):\n    return [sum(nums[i:i + window]) // window for i in range(len(nums) - window + 1)]\n", False, "//")

bucket = ex(L6, "bucket")
expect("bucket with `if not bucket`", bucket, "def add_item(item, bucket=None):\n    if not bucket:\n        bucket = []\n    bucket.append(item)\n    return bucket\n", False, "is None")

tr = ex(L6, "transpose")
expect("transpose with zip tuples", tr, "def transpose(matrix):\n    if not matrix:\n        return []\n    return [r for r in zip(*matrix)]\n", False, "tuples")
expect("transpose model crashes on [] if unguarded", tr, "def transpose(matrix):\n    return [[row[c] for row in matrix] for c in range(len(matrix[0]))]\n", False, "return [] first")
expect("transpose with list(zip)", tr, "def transpose(matrix):\n    if not matrix:\n        return []\n    return [list(r) for r in zip(*matrix)]\n", True)

rn = ex(L6, "remove_negatives")
expect("remove_negatives starter skips", rn, rn["starter"], False, "already passed")
expect("remove_negatives rebinding a new list", rn, "def remove_negatives(nums):\n    nums = [n for n in nums if n >= 0]\n    return nums\n", False, "caller")
expect("remove_negatives with slice assignment", rn, "def remove_negatives(nums):\n    nums[:] = [n for n in nums if n >= 0]\n    return nums\n", True)
expect("remove_negatives with while", rn, "def remove_negatives(nums):\n    i = 0\n    while i < len(nums):\n        if nums[i] < 0:\n            del nums[i]\n        else:\n            i += 1\n    return nums\n", True)

nb = ex(L6, "numbered")
expect("numbered from 0", nb, 'def numbered(items):\n    return [f"{i}. {x}" for i, x in enumerate(items)]\n', False, "start=1")

bh = ex(C6, "best_hours")
expect("best_hours via stability (key -sales[h])", bh, "def best_hours(sales, n):\n    return sorted(range(len(sales)), key=lambda h: -sales[h])[:n]\n", True)
expect("best_hours via tuple key", bh, "def best_hours(sales, n):\n    return sorted(range(len(sales)), key=lambda h: (-sales[h], h))[:n]\n", True)
expect("best_hours returns amounts", bh, "def best_hours(sales, n):\n    return sorted(sales, reverse=True)[:n]\n", False, "hour numbers")
expect("best_hours sorts in place", bh, "def best_hours(sales, n):\n    h = list(range(len(sales)))\n    s = sales\n    s.sort()\n    return sorted(h, key=lambda i: -sales[i])[:n]\n", False)
if "(-sales[h], h)" in bh["hint"] or "stable" not in bh["hint"]:
    fails.append("best_hours hint should lead with stability, not an untaught tuple key")

txt6 = " ".join(b["x"] for b in L6["blocks"])
for needle in ("import copy", "lambda w: w[-1]", "(1, \"z\") < (2, \"a\")", "a += [3]", "enumerate(kit, start=1)", "first, *rest", "shortest", "if not bucket", "ValueError", "for _ in range(2)"):
    if needle not in txt6:
        fails.append("l06 text missing %r" % needle)
for pid in ("p-tuple-cmp", "p-stable", "p-iadd", "p-loop-remove", "p-tuple-mut", "p-star"):
    if pid not in {p["id"] for p in L6["predict"]}:
        fails.append("l06 prediction %s missing" % pid)
codes6 = [b["x"] for b in L6["blocks"] if b["t"] == "code"]
for p in L6["predict"]:
    if p["code"] in codes6:
        fails.append("l06 prediction %s copies a lesson example" % p["id"])
if "```" not in C6["scene"] or len(C6["nit_right"]) != 3 or len(C6["teach"]["points"]) != 4:
    fails.append("c06 scene payload / nit_right / teach points missing")

# card rules: at least a third of each lesson's cards are code -> output / what-is-wrong cards
for L in (L5, L6):
    code_cards = [c for c in L["cards"] if "`" in c["f"] and ("give" in c["f"] or "what" in c["f"].lower() or "True or False" in c["f"] or "wrong" in c["f"])]
    if len(code_cards) * 3 < len(L["cards"]):
        fails.append("%s: only %d of %d cards are code cards" % (L["id"], len(code_cards), len(L["cards"])))

print("d18 content checks:", "OK" if not fails else "FAILED")
for f in fails:
    print(" -", f)
sys.exit(1 if fails else 0)
