# Writing tests for Lime exercises

Tests are Python run after the learner's code (CPython at build time, Brython in the app). Names available in a test:

| name | what |
|---|---|
| `ns` | dict of the learner's globals after their code ran |
| `out` | everything their code printed (str) |
| `code` | their source (str); `code_bare` = same with comments removed (use this for any source check) |
| `check(label, cond_or_callable, hint="")` | one pass/fail row; exceptions inside are caught and shown |
| `check_eq(label, fn, expected, hint="")` | compares with `==` **and the same types** (1 vs 1.0, list vs tuple); on failure shows `Expected X, got Y.` Prefer it for every value check. |
| `eq(a, b)` | strict equality (same types all the way down, so `1 != 1.0`, `[1] != (1,)`, and an object whose `__eq__` always says True never matches). Use it inside `check` whenever you compare a learner value: `check("cube", lambda: eq(ns["cube"](3), 27))`, never `ns["cube"](3) == 27`. |
| `rerun(old_line, new_line)` | runs their code again with one starter line replaced; returns `(ns2, out2)`; raises a clear message if they edited that line |
| `has_node("For", "While")` | AST check on their code (node class names: For, While, FloorDiv, Mod, Mult, If, Try, ListComp, Return, ...) |
| `uses_call("sorted")` | they call `sorted(...)` or `x.sorted(...)` |
| `silent(fn, *args)` | calls fn capturing prints: returns `(result, printed_text)`; use to check a function prints nothing |
| `spy("fact")` | wraps their function so calls through the global name are counted: `s = spy("fact"); ns["fact"](5); s.calls` |

Rules:
- Never compare a learner value with `==` inside `check`: a learner object can make `==` always True. Use `check_eq` or `eq(a, b)`.
- Never use `all(gen)` / `any(gen)`: Brython's own `all()` hides exceptions inside generators. Use `all([...])`. The build rejects it. (The runner also swaps in a safe `all`/`any` while learner code and tests run, as a backstop.)
- Do not check source text with `in code` (comments defeat it): use `has_node`, `uses_call`, `code_bare`, or better, `rerun` with other values.
- Defeat hardcoding: put inputs in starter variables and `rerun` with different values, or call functions with extra inputs.
- Every check that can fail should have a hint that teaches (what to look at), and value checks should use `check_eq` so expected/got is shown.
- The build (`python3 build.py`) proves: every solution passes, every starter fails, predictions and READ items run, traps differ from answers, ids are unique. `python3 bt.py` re-checks everything in real Brython (slow; run once before you finish).

Content schema (dsl.py): CARD(front, back, id), PRED(code, why, traps={wrong_output: message}, id), TERM(term, def, ex, mistake, card=True, q=None, id),
TEACH(prompt, model, points=[...]), city(..., nit_right=[...]), ARCHIVE(..., lesson=), EXAMSLOT(lesson_id, PRED, PRED, PRED), district(..., meridian=[MERIDIAN(lesson_id, id, title, code, why)]).
Ids: existing items keep their ids (progress is keyed on them). New items get new, descriptive ids (e.g. id="c-repr", "p-sep-end", "t-lambda"); never reuse a deleted id.

Runner behaviour test authors can rely on (runner.py, verified in CPython and Brython by tests/d02_runner.py):
- Every `while` and `for` loop (and comprehension) in learner code is guarded: past 2,000,000 steps or ~6 s it stops with a RuntimeError "Lime stopped your program: a loop ran for too long ...". After one runaway loop, later checks in the same run give up after 1 s.
- Anything learner code prints while tests run is discarded (use `silent()` to capture it). `input()`, `help()`, `time.sleep()` (no pause) and `sys.exit()` (not an error) are replaced while learner code runs; builtins, `sys.stdout`, `time.sleep` and the recursion limit (1000) are restored after every run and after every check.
- A `KeyError` for a name missing from `ns` reads "Your code no longer defines `x` ..."; `rerun` failures read "With another starting value your code failed: ...".
