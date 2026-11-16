"""d16: checks for lessons py01/py02 and city c01/c02 (run: python3 tests/d16_content.py)."""
import json, os, runpy, sys, itertools
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from runner import run_code  # noqa: E402

L1 = runpy.run_path(os.path.join(HERE, "content/l01.py"))["LESSON"]
L2 = runpy.run_path(os.path.join(HERE, "content/l02.py"))["LESSON"]
C1 = runpy.run_path(os.path.join(HERE, "city/c01.py"))["CITY"]
C2 = runpy.run_path(os.path.join(HERE, "city/c02.py"))["CITY"]
fails = []


def passes(code, tests):
    r = json.loads(run_code(code, tests))
    return not r["error"] and r["results"] and all(x["ok"] for x in r["results"])


def ex(container, eid):
    items = container.get("exercises") or container.get("jobs")
    return [e for e in items if e["id"] == eid][0]


def expect(label, cond):
    if not cond:
        fails.append(label)


# correct alternatives must pass
GOOD = [
    (C1, "fares", "passengers = 13\nfare = 7\nbag = 20\nprint(fare * passengers)\nprint(fare * passengers // bag)\nprint(fare * passengers % bag)\n"),
    (C1, "fares", "passengers = 13\nfare = 7\nbag = 20\ncoins = passengers * fare\nprint(coins)\nprint(coins // bag)\nprint(coins % bag)\n"),
    (L2, "close", "import math\na = 0.1 + 0.2\nb = 0.3\nclose = math.isclose(a, b)\n"),
    (L1, "clock", "minutes = 135\n# hours\nprint(minutes // 60)\nprint(minutes % 60)\n"),
]
for cont, eid, code in GOOD:
    expect("good answer rejected: %s %r" % (eid, code), passes(code, ex(cont, eid)["tests"]))

# gamed answers from the beta reports must fail
BAD = [
    (C1, "fares", "passengers = 13\nfare = 7\nbag = 20\nprint(91)  # 13 * 7\nprint(4)  # //\nprint(11)  # %\n"),
    (C1, "fares", "passengers = 13\nfare = 7\nbag = 20\nprint(passengers * fare * 2)\nprint(passengers * fare * 2 // bag)\nprint(passengers * fare * 2 % bag)\n"),
    (C1, "midnight", "minutes = 1000\nprint(16)\nprint(40)  # 1000\n"),
    (L1, "week", "days = 7\nprint(604800)  # 60*60*24*7\n"),
    (L1, "average", 'a = 4\nb = 8\nc = 15\nprint("9.0")\n'),
    (L1, "clock", "minutes = 135\nprint(minutes // 60, minutes % 60)  # // %\n"),
    (L1, "datesep", 'day = 13\nmonth = 11\nyear = 2026\nprint("13/11/2026")\n'),
    (L2, "close", "a = 0.1 + 0.2\nb = 0.3\nclose = b == 0.3\n"),
    (L2, "close", "a = 0.1 + 0.2\nb = 0.3\nclose = round(a, 2) == round(b, 2)\n"),
    (L2, "swap", "a = 3\nb = 9\na, b = 9, a\n"),
    (L2, "dose", "weight = 72.6\nmg_per_kg = 1.5\nprint(108.9)\nprint(4)\n"),
    (L2, "dose", "weight = 72.6\nmg_per_kg = 1.5\nd = weight * mg_per_kg\nprint(round(d, 1))\nprint(d // 25)\n"),
    (C2, "pell_total", 'apples = "12"\npears = 7\nprint("Total fruit: 19")\n'),
    (C2, "tickets", 'driver = "Wren"\nriders = 12\nprice = 4.5\nprint("Wren sold", riders, "tickets for", format(riders * price, ".2f"), "coins")\n'),
]
for cont, eid, code in BAD:
    expect("gamed answer accepted: %s %r" % (eid, code), not passes(code, ex(cont, eid)["tests"]))

# Parsons decoys: inserting a decoy anywhere (dead code included) must fail; only the intended order passes
for C in (C1, C2):
    for p in C["parsons"]:
        for d in p["distractors"]:
            for i in range(len(p["lines"]) + 1):
                alt = p["lines"][:i] + [d] + p["lines"][i:]
                expect("decoy placeable %s %r at %d" % (C["lesson"], d, i), not passes("\n".join(alt) + "\n", p["tests"]))
        ok = [o for o in itertools.permutations(p["lines"]) if passes("\n".join(o) + "\n", p["tests"])]
        # several valid orders are fine (both setup lines can come first); the intended one must pass
        expect("parsons %s intended order rejected" % C["lesson"], tuple(p["lines"]) in ok)
        if C is C1:
            expect("c01 parsons should have one order", len(ok) == 1)

# the scene's broken fare box really double-counts
scene_code = C1["scene"].split("```")[1]
r = json.loads(run_code(scene_code, ""))
expect("scene program prints 182, 9, 2", r["out"].split() == ["182", "9", "2"])

# code lines short enough for a 400px phone (about 40 chars)
for L in (L1, L2):
    for b in L["blocks"]:
        if b["t"] == "code":
            for line in b["x"].split("\n"):
                expect("long code line in %s: %r" % (L["id"], line), len(line) <= 40)

# story wording and NIT lines
expect("c02 still says drawers", "drawer" not in json.dumps(C2).lower())
expect("c01/c02 need 3 nit_right lines", len(C1["nit_right"]) == 3 and len(C2["nit_right"]) == 3)
expect("teach-back points", all([3 <= len(C["teach"]["points"]) <= 4 for C in (C1, C2)]))
# traceback wording consistent with what Lime shows
expect("py01 still says read from the bottom", "from the bottom" not in json.dumps(L1) + json.dumps(C1))
# every prediction has traps
expect("predictions without traps", all([p.get("traps") for p in L1["predict"] + L2["predict"]]))
# at least a third of the cards are code -> output
for L in (L1, L2):
    code_cards = [c for c in L["cards"] if "`" in c["f"] and ("show" in c["f"] or "give" in c["f"] or "wrong" in c["f"])]
    expect("%s: too few code cards (%d/%d)" % (L["id"], len(code_cards), len(L["cards"])), len(code_cards) * 3 >= len(L["cards"]))

print("fails:", fails)
sys.exit(1 if fails else 0)
