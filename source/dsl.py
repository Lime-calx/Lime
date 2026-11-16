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
    assert kind in ("model", "trap", "tip", "deep")
    return {"t": "note", "k": kind, "x": _t(x)}


def EX(id, title, prompt, starter, tests, hint, solution, kind="write"):
    assert kind in ("write", "fix")
    return {
        "id": id, "title": title, "kind": kind, "prompt": _t(prompt),
        "starter": _t(starter) + "\n", "tests": _t(tests) + "\n",
        "hint": _t(hint), "solution": _t(solution) + "\n",
    }


def PRED(code, why, traps=None, id=None):
    """A predict-the-output item. id: stable, unique within the lesson (progress is keyed on it).
    traps: optional {wrong_output: message} for common wrong answers (exact output text, compared like answers)."""
    d = {"code": _t(code), "why": _t(why)}
    if id: d["id"] = id
    if traps: d["traps"] = {_t(k): _t(v) for k, v in traps.items()}
    return d


def CARD(front, back, id=None):
    """A flashcard. id: stable and unique within the lesson (review history is keyed on it). Never reuse an old id for a new meaning."""
    d = {"f": _t(front), "b": _t(back)}
    if id: d["id"] = id
    return d


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


def TEACH(prompt, model, points=()):
    """Teach-back. points: 3-4 short key points the learner ticks after comparing with the model."""
    return {"prompt": _t(prompt), "model": _t(model), "points": [_t(p) for p in points]}


def TERM(term, definition, example="", mistake="", card=True, q=None, id=None):
    """Glossary entry for NIT's Index. card=False keeps it out of flashcards (use when a lesson card already covers it).
    q: optional card question to use instead of the generic one."""
    d = {"term": term, "def": _t(definition), "ex": _t(example), "mistake": _t(mistake), "card": bool(card)}
    if q: d["q"] = _t(q)
    if id: d["id"] = id
    return d


def city(lesson_id, opener, scene, jobs, read, parsons, teach, terms, nit_right=()):
    """nit_right: optional lesson-specific NIT lines for correct answers, each teaching one fact."""
    return {"lesson": lesson_id, "opener": _t(opener), "scene": _t(scene), "jobs": jobs,
            "read": read, "parsons": parsons, "teach": teach, "terms": terms, "nit_right": [_t(x) for x in nit_right]}


def ARCHIVE(id, year, title, text, source, lesson=None):
    """lesson: optional lesson id this history card belongs to (shown at the end of that lesson)."""
    return {"id": id, "year": year, "title": title, "text": _t(text), "source": source, "lesson": lesson}


def EXAMSLOT(lesson_id, *preds):
    """One exam slot: parallel PRED items testing the same idea; one is drawn per attempt. lesson_id = where it is taught."""
    return {"lesson": lesson_id, "items": list(preds)}


def district(track, opener, ending, archive, quests, exam, project, meridian=()):
    """exam: list of EXAMSLOT (a bare PRED counts as a one-item slot). meridian: optional READ items keyed by lesson
    (dicts from MERIDIAN(...)) forming the district's mystery log."""
    slots = [x if "items" in x else {"lesson": None, "items": [x]} for x in exam]
    return {"track": track, "opener": [_t(x) for x in opener], "ending": [_t(x) for x in ending],
            "archive": archive, "quests": quests, "exam": slots, "project": project, "meridian": list(meridian)}


def MERIDIAN(lesson_id, id, title, code, why):
    """A MERIDIAN log fragment: a short program decodable with that lesson's skill (a read-the-machine item)."""
    d = READ(id, title, code, why)
    d["lesson"] = lesson_id
    return d
