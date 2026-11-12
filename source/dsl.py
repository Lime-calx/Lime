import textwrap


def _t(x):
    return textwrap.dedent(x).strip("\n")


def H(x):
    return {"t": "h", "x": x.strip()}


def P(x):
    return {"t": "p", "x": _t(x)}


def CODE(x):
    return {"t": "code", "x": _t(x)}


def NOTE(kind, x):
    assert kind in ("model", "trap", "tip")
    return {"t": "note", "k": kind, "x": _t(x)}


def EX(id, title, prompt, starter, tests, hint, solution, kind="write"):
    assert kind in ("write", "fix")
    return {
        "id": id, "title": title, "kind": kind, "prompt": _t(prompt),
        "starter": _t(starter) + "\n", "tests": _t(tests) + "\n",
        "hint": _t(hint), "solution": _t(solution) + "\n",
    }


def PRED(code, why):
    return {"code": _t(code), "why": _t(why)}


def CARD(front, back):
    return {"f": _t(front), "b": _t(back)}


def lesson(id, track, n, title, minutes, summary, goals, blocks, exercises, predict, cards):
    return {
        "id": id, "track": track, "n": n, "title": title, "minutes": minutes,
        "summary": _t(summary), "goals": goals, "blocks": blocks,
        "exercises": exercises, "predict": predict, "cards": cards,
    }


# ---- City layer (story content that adds practice, never replaces it) ----

def JOB(role, *a, **k):
    """A city exercise. role: story | repair | quest | project."""
    assert role in ("story", "repair", "quest", "project")
    e = EX(*a, **k)
    e["role"] = role
    return e


def READ(id, title, code, why):
    """Read-the-machine: a longer program to trace before running."""
    return {"id": id, "title": title, "code": _t(code), "why": _t(why)}


def PARSONS(id, title, prompt, lines, tests, distractors=(), hint=""):
    """Order the lines (indentation is given). Checked by running the tests on the assembled program."""
    return {"id": id, "title": title, "prompt": _t(prompt), "lines": list(lines),
            "distractors": list(distractors), "tests": _t(tests) + "\n", "hint": _t(hint)}


def TEACH(prompt, model):
    return {"prompt": _t(prompt), "model": _t(model)}


def TERM(term, definition, example="", mistake=""):
    return {"term": term, "def": _t(definition), "ex": _t(example), "mistake": _t(mistake)}


def city(lesson_id, opener, scene, jobs, read, parsons, teach, terms):
    return {"lesson": lesson_id, "opener": _t(opener), "scene": _t(scene), "jobs": jobs,
            "read": read, "parsons": parsons, "teach": teach, "terms": terms}


def ARCHIVE(id, year, title, text, source):
    return {"id": id, "year": year, "title": title, "text": _t(text), "source": source}


def district(track, opener, ending, archive, quests, exam, project):
    return {"track": track, "opener": [_t(x) for x in opener], "ending": [_t(x) for x in ending],
            "archive": archive, "quests": quests, "exam": exam, "project": project}
