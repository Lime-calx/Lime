"""d19: py07/py08 content checks. Run from the repo root: python3 tests/d19_content.py
Proves that the tightened tests reject the wrong-but-plausible answers the beta reports found,
accept the correct alternatives they should accept, and that the card/term rules hold."""
import json, os, runpy, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from runner import run_code  # noqa: E402

L7 = runpy.run_path(os.path.join(HERE, "content", "l07.py"))["LESSON"]
L8 = runpy.run_path(os.path.join(HERE, "content", "l08.py"))["LESSON"]
C7 = runpy.run_path(os.path.join(HERE, "city", "c07.py"))["CITY"]
C8 = runpy.run_path(os.path.join(HERE, "city", "c08.py"))["CITY"]


def item(src, iid):
    for e in src.get("exercises", []) + src.get("jobs", []):
        if e["id"] == iid:
            return e
    raise KeyError(iid)


def results(ex, code):
    r = json.loads(run_code(code, ex["tests"]))
    assert not r["error"], r["error"]
    return {x["label"]: x["ok"] for x in r["results"]}


fails = []


def expect(name, cond):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        fails.append(name)


# riders: a list-based "not in" counter gives right numbers but must not pass (t4)
riders = item(C7, "riders")
r = results(riders, "def unique_riders(names):\n    riders = []\n    for n in names:\n        if n not in riders:\n            riders.append(n)\n    return len(riders)\n")
expect("riders: list-based solution is rejected", not all(r.values()) and not r["keeps the riders in a set"])
r = results(riders, "def unique_riders(names):\n    seen = set()\n    for n in names:\n        seen.add(n)\n    return len(seen)\n")
expect("riders: set.add solution passes", all(r.values()))

# fare_log: prompt now says try/except; spacing and comments must not fool the style check (t4)
fare = item(C8, "fare_log")
expect("fare_log: prompt asks for try/except", "Use try/except" in fare["prompt"])
good2 = 'def total_coins(lines):\n    total = bad = 0\n    for line in lines:\n        try:\n            t, c = line.split(",")\n            total += int(c)\n        except  ValueError:\n            bad += 1\n    return (total, bad)\n'
expect("fare_log: 'except  ValueError' (two spaces) passes", all(results(fare, good2).values()))
bare = 'def total_coins(lines):\n    total = bad = 0\n    for line in lines:\n        try:\n            t, c = line.split(",")\n            total += int(c)\n        except:  # except ValueError\n            bad += 1\n    return (total, bad)\n'
expect("fare_log: bare except with the phrase in a comment fails", not results(fare, bare)["catches ValueError by name"])

# ledger: first-seen tie-break must fail; max(sorted(...)) passes
ledger = item(C7, "ledger")
firstseen = "def totals_by_item(records):\n    t = {}\n    for i, c in records:\n        t[i] = t.get(i, 0) + c\n    return t\n\ndef best_seller(records):\n    t = totals_by_item(records)\n    if not t:\n        return None\n    return max(t, key=t.get)\n"
expect("ledger: first-seen tie-break is rejected", not all(results(ledger, firstseen).values()))

# rota: practises ^ and -
rota = item(L7, "rota")
loopy = 'def rota_report(monday, tuesday):\n    a = set(monday)\n    b = set(tuesday)\n    return {"both": sorted([x for x in a if x in b]), "monday_only": sorted([x for x in a if x not in b]), "one_day": sorted([x for x in a | b if (x in a) != (x in b)])}\n'
r = results(rota, loopy)
expect("rota: comprehension-only answer is told to use ^ and -", not r["one_day uses ^ (or symmetric_difference)"])

# tickets: bare except fails; correct solution with different wording passes
tk = item(C8, "tickets")
sol = tk["solution"]
expect("tickets: reference passes", all(results(tk, sol).values()))
expect("tickets: bare except is rejected", not all(results(tk, sol.replace("except ValueError as err:", "except Exception as err:").replace("except Exception as err:", "except:\n            err = 'x'")).values()))

# traceback reading: the classic wrong answer (top line) fails
tb = item(L8, "traceback_read")
r = results(tb, 'error_name = "ZeroDivisionError"\nraised_line = 11\nbad_bed = "Bed 2"\n')
expect("traceback_read: choosing the top entry (line 11) fails", not r["raised_line"])

# cards: no list cards left for the reported ids; at least a third are code/what-is-wrong cards
ids8 = {c["id"] for c in L8["cards"]}
expect("py08: old 'how to read a traceback' card c1 is gone (py01 owns it)", "c1" not in ids8 and "c-tb-multi" in ids8)
ids7 = {c["id"] for c in L7["cards"]}
expect("py07: one membership-cost card (c0 merged into c8)", "c0" not in ids7 and "c8" in ids7)
for L in (L7, L8):
    code_cards = [c for c in L["cards"] if "`" in c["f"] and ("?" in c["f"]) and ("print" in c["f"] or "wrong" in c["f"] or "=" in c["f"] or "(" in c["f"])]
    expect("%s: >= 1/3 code cards (%d of %d)" % (L["id"], len(code_cards), len(L["cards"])), len(code_cards) * 3 >= len(L["cards"]))
t2 = [t for t in C7["terms"] if t["id"] == "t2"][0]
expect("py07 t2 KeyError mistake is a mistake, not a fix", "Fix" not in t2["mistake"] and "Reading" in t2["mistake"])
for C in (C7, C8):
    expect("%s: every term has an example" % C["lesson"], all([bool(t["ex"]) for t in C["terms"]]))
    expect("%s: nit_right has 3 lines" % C["lesson"], len(C["nit_right"]) == 3)
    expect("%s: teach-back has 3-4 points" % C["lesson"], 3 <= len(C["teach"]["points"]) <= 4)
    expect("%s: scene holds a runnable program" % C["lesson"], "```" in C["scene"])

print("\nfailures:", fails)
sys.exit(1 if fails else 0)
