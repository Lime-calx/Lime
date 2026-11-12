"""Validate all lessons against CPython and emit content.json + expected.json."""
import glob, json, os, runpy, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from runner import run_code  # noqa: E402

problems = []
lessons = []
expected = []  # (lesson, kind, key, code, output) for Brython comparison

for path in sorted(glob.glob(os.path.join(HERE, "content", "l*.py"))):
    L = runpy.run_path(path)["LESSON"]
    lessons.append(L)

seen = set()
for L in lessons:
    assert L["id"] not in seen, L["id"]
    seen.add(L["id"])
    # exercises
    ids = set()
    for ex in L["exercises"]:
        key = L["id"] + ":" + ex["id"]
        assert ex["id"] not in ids, key
        ids.add(ex["id"])
        sol = json.loads(run_code(ex["solution"], ex["tests"]))
        if sol["error"] or not sol["results"] or not all(r["ok"] for r in sol["results"]):
            problems.append("SOLUTION FAILS %s: %s" % (key, json.dumps(sol)[:600]))
        st = json.loads(run_code(ex["starter"], ex["tests"]))
        if not st["error"] and st["results"] and all(r["ok"] for r in st["results"]):
            problems.append("STARTER ALREADY PASSES %s" % key)
        expected.append({"k": key, "kind": "ex", "code": ex["solution"], "tests": ex["tests"]})
    # code blocks
    bi = 0
    for b in L["blocks"]:
        if b["t"] == "code":
            r = json.loads(run_code(b["x"], ""))
            expected.append({"k": "%s:b%d" % (L["id"], bi), "kind": "block", "code": b["x"], "out": r["out"], "err": r["error"]})
            bi += 1
    # predictions
    for i, p in enumerate(L["predict"]):
        r = json.loads(run_code(p["code"], ""))
        if r["error"]:
            problems.append("PREDICT ERRORS %s:p%d %s" % (L["id"], i, r["error"]))
        p["ans"] = r["out"].rstrip("\n")
        expected.append({"k": "%s:p%d" % (L["id"], i), "kind": "pred", "code": p["code"], "out": r["out"], "err": r["error"]})


# ---- city layer ----
def check_ex(key, ex):
    sol = json.loads(run_code(ex["solution"], ex["tests"]))
    if sol["error"] or not sol["results"] or not all(r["ok"] for r in sol["results"]):
        problems.append("SOLUTION FAILS %s: %s" % (key, json.dumps(sol)[:600]))
    st = json.loads(run_code(ex["starter"], ex["tests"]))
    if not st["error"] and st["results"] and all(r["ok"] for r in st["results"]):
        problems.append("STARTER ALREADY PASSES %s" % key)
    expected.append({"k": key, "kind": "ex", "code": ex["solution"], "tests": ex["tests"]})

def run_pred(key, p):
    r = json.loads(run_code(p["code"], ""))
    if r["error"]:
        problems.append("PREDICT ERRORS %s %s" % (key, r["error"]))
    p["ans"] = r["out"].rstrip("\n")
    expected.append({"k": key, "kind": "pred", "code": p["code"], "out": r["out"], "err": r["error"]})

ids_by_lesson = {L["id"]: L for L in lessons}
cities = {}
for path in sorted(glob.glob(os.path.join(HERE, "city", "c*.py"))):
    C = runpy.run_path(path)["CITY"]
    assert C["lesson"] in ids_by_lesson, C["lesson"]
    lid = C["lesson"]
    core = {e["id"] for e in ids_by_lesson[lid]["exercises"]}
    for j in C["jobs"]:
        assert j["id"] not in core, (lid, j["id"])
        check_ex("%s:%s" % (lid, j["id"]), j)
    for r in C["read"]:
        run_pred("%s:%s" % (lid, r["id"]), r)
    for p in C["parsons"]:
        sol = "\n".join(p["lines"]) + "\n"
        r = json.loads(run_code(sol, p["tests"]))
        if r["error"] or not r["results"] or not all(x["ok"] for x in r["results"]):
            problems.append("PARSONS FAILS %s:%s %s" % (lid, p["id"], json.dumps(r)[:400]))
        # the decoys must not be usable in place of a real line
        for d in p["distractors"]:
            for i in range(len(p["lines"])):
                alt = p["lines"][:i] + [d] + p["lines"][i + 1:]
                r2 = json.loads(run_code("\n".join(alt) + "\n", p["tests"]))
                if not r2["error"] and r2["results"] and all(x["ok"] for x in r2["results"]):
                    problems.append("PARSONS DECOY WORKS %s:%s %r at %d" % (lid, p["id"], d, i))
        expected.append({"k": "%s:%s" % (lid, p["id"]), "kind": "ex", "code": sol, "tests": p["tests"]})
    cities[lid] = C

districts = {}
for path in sorted(glob.glob(os.path.join(HERE, "city", "d_*.py"))):
    D = runpy.run_path(path)["DISTRICT"]
    t = D["track"]
    for q in D["quests"]:
        check_ex("%s:%s" % (t, q["id"]), q)
    check_ex("%s:%s" % (t, D["project"]["id"]), D["project"])
    for i, p in enumerate(D["exam"]):
        run_pred("%s:exam%d" % (t, i), p)
    districts[t] = D

terms = sum(len(c["terms"]) for c in cities.values())
print("city lessons:", len(cities), "jobs:", sum(len(c["jobs"]) for c in cities.values()),
      "parsons:", sum(len(c["parsons"]) for c in cities.values()), "terms:", terms,
      "districts:", len(districts), "quests:", sum(len(d["quests"]) for d in districts.values()),
      "archive:", sum(len(d["archive"]) for d in districts.values()))

with open(os.path.join(HERE, "out", "content.json"), "w") as f:
    from curriculum import TRACKS
    json.dump({"lessons": lessons, "tracks": TRACKS, "city": cities, "districts": districts}, f, ensure_ascii=False)
with open(os.path.join(HERE, "out", "expected.json"), "w") as f:
    json.dump(expected, f, ensure_ascii=False)

print("lessons:", len(lessons), "exercises:", sum(len(L["exercises"]) for L in lessons),
      "predict:", sum(len(L["predict"]) for L in lessons), "cards:", sum(len(L["cards"]) for L in lessons))
if problems:
    print("PROBLEMS:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("all solutions pass, all starters fail, predictions computed")
