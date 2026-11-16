"""d20: district content checks for city/d_py.py. Run from the repo root: python3 tests/d20_content.py
Structure (exam slots per lesson, quest order, archive lesson ids, MERIDIAN per lesson, ending), story
fixes (opener, NIT's name, no early tower name), and that the tightened quest/boss tests reject the
wrong-but-plausible answers the beta reports found while accepting correct alternatives."""
import json, os, re, runpy, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from runner import run_code  # noqa: E402

D = runpy.run_path(os.path.join(HERE, "city", "d_py.py"))["DISTRICT"]
LESSONS = {}
for n in range(1, 9):
    L = runpy.run_path(os.path.join(HERE, "content", "l0%d.py" % n))["LESSON"]
    LESSONS[L["id"]] = L
ORDER = sorted(LESSONS, key=lambda k: LESSONS[k]["n"])

fails = []


def expect(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


def results(ex, code):
    r = json.loads(run_code(code, ex["tests"]))
    if r["error"]:
        return {"__error__": False}
    return {x["label"]: x["ok"] for x in r["results"]}


def quest(qid):
    return [q for q in D["quests"] if q["id"] == qid][0]


# ---- exam: 2 slots per lesson, 3 parallel items each, each with a why, unique ids, not lesson copies ----
slots = D["exam"]
expect("exam has 16 slots", len(slots) == 16)
for lid in ORDER:
    expect("exam: 2 slots for %s" % lid, len([s for s in slots if s["lesson"] == lid]) == 2)
expect("exam: every slot has 3 items", all(len(s["items"]) == 3 for s in slots))
items = [p for s in slots for p in s["items"]]
expect("exam: every item has a why", all(p["why"].strip() for p in items))
expect("exam: item ids unique and set", len(set(p.get("id") for p in items)) == len(items) and all(p.get("id") for p in items))
lesson_code = set()
for L in LESSONS.values():
    lesson_code |= {b["x"].strip() for b in L["blocks"] if b["t"] == "code"}
    lesson_code |= {p["code"].strip() for p in L["predict"]}
expect("exam: no item copies a lesson block or prediction", not [p["id"] for p in items if p["code"].strip() in lesson_code])
outs = {}
for p in items:
    r = json.loads(run_code(p["code"], ""))
    outs[p["id"]] = r["out"].strip()
    expect("exam item %s runs without error" % p["id"], not r["error"])
expect("exam: the three items of each slot have different answers or code", all(len(set(p["code"] for p in s["items"])) == 3 for s in slots))
# l08 coverage: else, finally, raise, and an error passing out of a function
l08_code = "\n".join(p["code"] for s in slots if s["lesson"] == "py08" for p in s["items"])
for kw in ("else:", "finally:", "raise ", "except ValueError as"):
    expect("exam py08 covers %r" % kw, kw in l08_code)
expect("exam: += on a list is in the py06 slot (taught there)", any("+= [" in p["code"] for s in slots if s["lesson"] == "py06" for p in s["items"]))
expect("exam: no += on a list before py06", not any(re.search(r"\+= \[", p["code"]) for s in slots if LESSONS[s["lesson"]]["n"] < 6 for p in s["items"]))
expect("exam: reports' proposals present (scope, print->None, ^, dict comp dup key, b = b + [3])",
       outs["x-scope-a"] == "1 5" and outs["x-ret-a"] == "6\nNone" and outs["x-set-a"] == "[1, 4] True"
       and outs["x-dict-a"] == "{3: 'yam', 4: 'kiwi'}" and outs["x-alias-a"] == "[1, 2, 9] [1, 2, 3]")
# the timer is 75 s per slot: keep the exam short enough for a burst
expect("exam: 16 slots = 20 minutes", len(slots) * 75 // 60 == 20)

# ---- quests: ordered by `after`, every lesson 3..8 opens one ----
afters = [LESSONS[q["after"]]["n"] for q in D["quests"]]
expect("quests listed in unlock order", afters == sorted(afters))
expect("a py03 quest and a py08 quest exist", "py03" in [q["after"] for q in D["quests"]] and "py08" in [q["after"] for q in D["quests"]])
expect("roman quest names the great tower's face, not MERIDIAN", "Meridian" not in quest("roman")["prompt"] and "great tower" in quest("roman")["prompt"])
expect("quest tests use check_eq", all("check_eq(" in q["tests"] for q in D["quests"]))

roman = quest("roman")
noxl = 'def to_roman(n):\n    pairs = [(1000, "M"), (900, "CM"), (500, "D"), (100, "C"), (90, "XC"), (50, "L"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]\n    out = ""\n    for v, s in pairs:\n        while n >= v:\n            out += s\n            n -= v\n    return out\n'
r = results(roman, noxl)
expect("roman: a solution without XL/CD is rejected", not r.get("40 is XL", True) and not r.get("444 is CDXLIV", True))

luhn = quest("luhn")
loose = 'def luhn_ok(number):\n    digits = number.replace(" ", "")[::-1]\n    total = 0\n    for i, ch in enumerate(digits):\n        d = int(ch)\n        if i % 2 == 1:\n            d *= 2\n            if d > 9:\n                d -= 9\n        total += d\n    return total % 10 == 0\n'
r = results(luhn, loose)
expect("luhn: the old reference (empty string is valid) is rejected", not all(r.values()))
tryver = 'def luhn_ok(number):\n    s = number.replace(" ", "")\n    if s == "":\n        return False\n    total = 0\n    for i, ch in enumerate(s[::-1]):\n        try:\n            d = int(ch)\n        except ValueError:\n            return False\n        if i % 2:\n            d = d * 2 - 9 if d * 2 > 9 else d * 2\n        total += d\n    return total % 10 == 0\n'
expect("luhn: a try/except digit check passes too", all(results(luhn, tryver).values()))

rle = quest("rle")
lower = 'def encode(text):\n    text = text.lower()\n    out = ""\n    i = 0\n    while i < len(text):\n        j = i\n        while j < len(text) and text[j] == text[i]:\n            j += 1\n        out += text[i] + str(j - i)\n        i = j\n    return out\n\ndef decode(code):\n    out = ""\n    i = 0\n    while i < len(code):\n        j = i + 1\n        while j < len(code) and code[j].isdigit():\n            j += 1\n        out += code[i] * int(code[i + 1:j])\n        i = j\n    return out\n'
expect("rle: case-folding encode is rejected", not results(rle, lower)['encode("aA") keeps case apart'])

collatz = quest("collatz")
hard = 'start = 6\nprint("steps: 8")\nprint("highest: 16")\n'
expect("collatz: hard-coded output is rejected", not all(results(collatz, hard).values()))

lamps = quest("lamps")
bare = lamps["solution"].replace("except ValueError as err:", "except Exception as err:")
r = results(lamps, bare)
expect("lamps: catching Exception (hides caller bugs) is rejected", not r["other errors pass out of lamp_report"] and r["a full report"])

# ---- boss project ----
P = D["project"]
for word in ("+4", "1_000", "whitespace-only", "empty after stripping", "bare `except:`", "Do not change the list"):
    expect("project prompt states the rule %r" % word, word in P["prompt"])
lenient = P["solution"].replace("            if not qty.isdigit():\n                raise ValueError(\"quantity must be plain digits\")\n            qty = int(qty)\n", "            qty = int(qty)\n            if qty < 0:\n                raise ValueError(\"negative\")\n")
expect("project: lenient int() solution differs from reference", lenient != P["solution"])
r = results(P, lenient)
expect("project: int() accepting '+4'/'1_000' is rejected", not r["only plain digits count as a quantity"])
barex = P["solution"].replace("except ValueError:", "except:")
r = results(P, barex)
expect("project: bare except is rejected", not r["catches ValueError by name, no bare except"])
mut = P["solution"].replace("    for line in lines:\n", "    for k in range(len(lines)):\n        lines[k] = lines[k].lower()\n    for line in lines:\n", 1)
expect("project: mutating the input is rejected", not results(P, mut)["does not change the input list"])
nocase = P["solution"].replace("        cat = cat.lower()\n", "")
expect("project: no case merging is rejected", not results(P, nocase)["case merges across lines"])
noempty = P["solution"].replace('            if name == "" or cat == "":\n                raise ValueError("empty name or category")\n', "")
expect("project: empty category accepted is rejected", not results(P, noempty)["an empty category or name is bad"])
for lbl in ("empty and whitespace-only lines are bad", "ties in alphabetical order"):
    expect("project has check %r" % lbl, lbl in P["tests"])

# ---- archive ----
A = {a["id"]: a for a in D["archive"]}
expect("archive: every card has a valid lesson id", all(a.get("lesson") in LESSONS for a in D["archive"]))
expect("archive: Lovelace paper is French-language, by Menabrea", "French-language" in A["lovelace"]["text"] and "Menabrea" in A["lovelace"]["text"] and "an Italian paper" not in A["lovelace"]["text"])
expect("archive: Jacquard 1801 / 1804-05 and predecessors", "1801" in A["jacquard"]["text"] and "1804-05" in A["jacquard"]["text"] and "Bouchon" in A["jacquard"]["text"])
expect("archive: Hollerith 1890 census", "1890" in A["hollerith"]["text"])
expect("archive: ASCII lower case 1967, Unicode 'most'", "1967" in A["ascii"]["text"] and "most of the world's scripts" in A["ascii"]["text"] and "every script" not in A["ascii"]["text"])
expect("archive: IEEE 754 no overclaim", "same answer on different machines" not in A["ieee754"]["text"] and "754-1985" in A["ieee754"]["source"])
expect("archive: Zen 1999 and PEP 20 2004, Bench", "1999" in A["zen"]["text"] and "2004" in A["zen"]["text"] and "Bench" in A["zen"]["text"])
expect("archive: Dijkstra full citation and Wirth", "11(3):147-148" in A["goto"]["source"] and "Wirth" in A["goto"]["text"])
expect("archive: Python foreword cited", "Programming Python" in A["python"]["source"])
expect("archive: lesson links as suggested", A["ieee754"]["lesson"] in ("py01", "py02") and A["ascii"]["lesson"] == "py05" and A["goto"]["lesson"] == "py03" and A["bug"]["lesson"] == "py08")
r = json.loads(run_code("import this\n", ""))
expect("archive: `import this` runs in the runner", not r["error"] and "Readability counts" in r["out"])

# ---- MERIDIAN: one fragment per lesson, deterministic ----
M = D["meridian"]
expect("meridian: one fragment per lesson, in order", [m["lesson"] for m in M] == ORDER)
for m in M:
    a = json.loads(run_code(m["code"], ""))
    b = json.loads(run_code(m["code"], ""))
    expect("meridian %s runs and is deterministic" % m["id"], not a["error"] and a["out"] == b["out"] and a["out"].strip())
expect("meridian py01 decodes eleven years", json.loads(run_code(M[0]["code"], ""))["out"].startswith("11 "))
expect("meridian py08 shows int('O6') choking", "'O6'" in json.loads(run_code(M[-1]["code"], ""))["out"])

# ---- story ----
op = "\n".join(D["opener"])
expect("opener: no 'Payload'", "Payload" not in op and "payload" not in op)
expect("opener: NIT backronym spells NIT", "Numbered Index of Terms" in op and "Index of Names and Things" not in op)
expect("opener: explains run once / loop / lesson 3", "runs once" in op and "loop" in op and "lesson 3" in op)
code4 = re.findall(r"```\n(.*?)```", D["opener"][3], re.S)[0]
expect("opener: screen 4 program is print-only (lesson 1)", all(l.strip().startswith("print(") for l in code4.strip().split("\n")) and "f\"" not in code4)
expect("opener: tower not named as MERIDIAN early", "tower" not in op.lower())
expect("ending: three screens", len(D["ending"]) == 3)
end3 = D["ending"][2]
ecode = re.findall(r"```\n(.*?)```", end3, re.S)
expect("ending: third screen has a runnable program", ecode and not json.loads(run_code(ecode[0], ""))["error"])
expect("ending: program counts waiting lines", json.loads(run_code(ecode[0], ""))["out"].startswith("3 of 6 waiting"))
expect("ending: reveals MERIDIAN is the great tower's clock", "great tower's clock" in end3)
expect("ending: closes with the next district's theme", end3.rstrip().endswith("Make the machine do the boring part."))
expect("ending: no 'sorting bolts by size'", "sorting bolts" not in "\n".join(D["ending"]))

print("\n%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
