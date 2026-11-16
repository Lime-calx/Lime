from dsl import *

CITY = city(
    "py08",
    opener="Machines fail. Good machines fail loudly, say where, and say why. Bad machines fail quietly and let you find out at dinner.",
    scene="""
    The fare box is back on the tram, writing a log line for every stop. But the ink smudges: some lines are unreadable, and the old program simply stops when it meets one. This is the program, with three of today's lines:

    ```
    log = ["06:15,7", "07:00,1O", "08:00,12"]
    total = 0
    for line in log:
        time, coins = line.split(",")
        total += int(coins)
    print("total:", total)
    ```

    Run it. The smudge turned the 0 of "10" into a letter O, `int("1O")` raised a `ValueError`, and the program stopped before it ever reached 08:00 or the final print. Wren wants the day's total anyway.

    NIT: "Never let one smudge stop the whole day. Also never pretend the smudge is not there. Count it." """,
    jobs=[
        JOB("story", "fare_log", "Read the smudged log",
            """
            Each log line looks like `"06:15,7"`: a time, a comma, the coins taken. Some lines are smudged and can't be read. Write `total_coins(lines)` that returns a tuple `(total, bad)`: the sum of the coins on the good lines and the number of bad lines.

            A line is bad if it does not split into exactly two parts on the comma, or if the coins part is not a whole number. **Use try/except**: put the risky lines in `try` and catch only `ValueError`, the one error you expect.""",
            "def total_coins(lines):\n    pass\n",
            """
            import re
            f = ns.get("total_coins")
            check("defines total_coins", lambda: callable(f))
            check_eq("all good lines", lambda: f(["06:15,7", "08:00,12"]), (19, 0))
            check_eq("the scene's log", lambda: f(["06:15,7", "07:00,1O", "08:00,12"]), (19, 1), "int(\\"1O\\") raises ValueError: count the line as bad and keep going.")
            check_eq("smudged coins and a line with no comma", lambda: f(["06:15,7", "07:00,x", "garbage", "08:00,12"]), (19, 2), "Unpacking the wrong number of parts and int('x') both raise ValueError.")
            check_eq("too many commas is bad", lambda: f(["06:15,7,9"]), (0, 1), "Three parts into two names raises ValueError too.")
            check_eq("an empty coins part is bad", lambda: f(["06:15,"]), (0, 1))
            check_eq("an empty log", lambda: f([]), (0, 0))
            check("uses try/except", lambda: has_node("Try"), "This job practises EAFP: try the split and the int(), and catch the failure.")
            check("catches ValueError by name", lambda: re.search(r"except\\s*\\(?\\s*ValueError", code_bare) is not None and re.search(r"except\\s*:", code_bare) is None, "Write except ValueError:. A bare except would also hide real bugs, such as a typo in a name.")
            """,
            "In the loop: try: time, coins = line.split(','); total += int(coins) except ValueError: bad += 1.",
            'def total_coins(lines):\n    total = 0\n    bad = 0\n    for line in lines:\n        try:\n            time, coins = line.split(",")\n            total += int(coins)\n        except ValueError:\n            bad += 1\n    return (total, bad)'),
        JOB("repair", "average_fare", "Repair the silent average",
            """
            `average_fare(fares)` hides every problem by returning 0. That turns a broken list into a believable wrong answer. Repair it so that:

            - a normal list gives its average,
            - an empty list raises `ValueError` with a clear message,
            - a list containing text lets the `TypeError` through instead of hiding it.""",
            "def average_fare(fares):\n    try:\n        return sum(fares) / len(fares)\n    except Exception:\n        return 0\n",
            """
            f = ns.get("average_fare")
            def raises(fn, exc):
                try:
                    fn()
                except exc:
                    return True
                except Exception:
                    return False
                return False
            check_eq("[2, 4] gives 3.0", lambda: f([2, 4]), 3.0)
            check_eq("[5, 6, 10] gives 7.0", lambda: f([5, 6, 10]), 7.0)
            check("an empty list raises ValueError", lambda: raises(lambda: f([]), ValueError), "Check for the empty case first and raise ValueError(\\"...\\").")
            check("text in the list raises TypeError", lambda: raises(lambda: f([2, "x"]), TypeError), "Remove the blanket except so real errors surface.")
            """,
            "Delete the try/except. Before dividing, if not fares: raise ValueError('no fares to average').",
            'def average_fare(fares):\n    if not fares:\n        raise ValueError("no fares to average")\n    return sum(fares) / len(fares)', kind="fix"),
        JOB("story", "tickets", "The ticket inspector",
            """
            Juno, the tram's ticket inspector, copies each ticket as a line like `"T104,adult,2"`: an id, a kind, and the number of zones. Write two functions.

            `check_ticket(line)` returns the id if the ticket is valid. Otherwise it **raises** `ValueError` with exactly one of these messages, checked in this order:

            - `"expected 3 parts"` if the line does not split into exactly 3 parts on commas
            - `"unknown kind"` if the kind is not `"adult"` or `"child"`
            - `"zones must be 1 to 5"` if the zones part is not a whole number from 1 to 5

            `validate_tickets(lines)` returns a tuple `(ok, problems)`. `ok` is the list of valid ids, in order. `problems` is a list of strings like `"line 2: unknown kind"`, counting lines from 1. Call `check_ticket`, catch its error with `except ValueError as err`, and put `err` into the string with an f-string.""",
            "def check_ticket(line):\n    pass\n\ndef validate_tickets(lines):\n    pass\n",
            """
            import re
            c = ns.get("check_ticket")
            v = ns.get("validate_tickets")
            def message(line):
                try:
                    return "returned " + repr(c(line))
                except ValueError as err:
                    return str(err)
            check("defines both functions", lambda: callable(c) and callable(v))
            check_eq("a good ticket gives its id", lambda: c("T104,adult,2"), "T104")
            check_eq("a child ticket for 5 zones is fine", lambda: c("T7,child,5"), "T7", "5 is inside the range 1 to 5.")
            check_eq("two parts", lambda: message("T1,adult"), "expected 3 parts", "Split on commas, check len(parts) != 3, and raise ValueError(\\"expected 3 parts\\") before unpacking.")
            check_eq("four parts", lambda: message("T1,adult,2,9"), "expected 3 parts")
            check_eq("unknown kind", lambda: message("T2,senior,1"), "unknown kind", "Only \\"adult\\" and \\"child\\" are kinds.")
            check_eq("zones not a number", lambda: message("T3,child,x"), "zones must be 1 to 5", "zones.isdigit() is False for \\"x\\": raise your own message instead of letting int() raise its own.")
            check_eq("zones too high", lambda: message("T3,child,9"), "zones must be 1 to 5")
            check_eq("zero zones", lambda: message("T3,adult,0"), "zones must be 1 to 5", "1 to 5 includes 1 and 5 but not 0.")
            check_eq("a bad line and a bad kind", lambda: v(["T1,adult,1", "T2,senior,1", "smudge", "T3,child,5"]), (["T1", "T3"], ["line 2: unknown kind", "line 3: expected 3 parts"]), "Number the lines from 1: enumerate gives 0 first, so add 1.")
            check_eq("no lines", lambda: v([]), ([], []))
            check_eq("all good", lambda: v(["A1,child,3"]), (["A1"], []))
            check("check_ticket raises its own errors", lambda: has_node("Raise"), "Use raise ValueError(\\"...\\") for each rule.")
            check("validate_tickets calls check_ticket inside try", lambda: has_node("Try") and uses_call("check_ticket"), "Reuse check_ticket; do not repeat its rules.")
            check("catches ValueError by name", lambda: re.search(r"except\\s*\\(?\\s*ValueError", code_bare) is not None and re.search(r"except\\s*:", code_bare) is None, "Write except ValueError as err:, never a bare except.")
            """,
            'check_ticket: parts = line.split(","); if len(parts) != 3: raise ValueError("expected 3 parts"). Unpack ticket_id, kind, zones = parts, check the kind, then if not zones.isdigit() or int(zones) < 1 or int(zones) > 5: raise. validate_tickets: loop with enumerate; try: ticket_id = check_ticket(line) except ValueError as err: problems.append(f"line {i + 1}: {err}") else: ok.append(ticket_id).',
            'def check_ticket(line):\n    parts = line.split(",")\n    if len(parts) != 3:\n        raise ValueError("expected 3 parts")\n    ticket_id, kind, zones = parts\n    if kind != "adult" and kind != "child":\n        raise ValueError("unknown kind")\n    if not zones.isdigit() or int(zones) < 1 or int(zones) > 5:\n        raise ValueError("zones must be 1 to 5")\n    return ticket_id\n\ndef validate_tickets(lines):\n    ok = []\n    problems = []\n    for i, line in enumerate(lines):\n        try:\n            ticket_id = check_ticket(line)\n        except ValueError as err:\n            problems.append(f"line {i + 1}: {err}")\n        else:\n            ok.append(ticket_id)\n    return (ok, problems)'),
    ],
    read=[
        READ("r1", "NIT's own log",
             """
             def risky(x):
                 try:
                     result = 10 // x
                 except ZeroDivisionError:
                     print("zero!")
                     return -1
                 else:
                     print("fine")
                     return result
                 finally:
                     print("logged", x)

             print(risky(3))
             print(risky(0))
             try:
                 int("seven")
             except ValueError as e:
                 print("bad:", type(e).__name__)
             """,
             "For 3: the try succeeds, `else` prints `fine`, and `finally` prints `logged 3` before the return value 3 is printed. For 0: `ZeroDivisionError` jumps to the except branch, which prints `zero!`; `finally` still prints `logged 0`; then -1 is printed. `int(\"seven\")` raises ValueError, and `type(e).__name__` is the name of its type as text."),
    ],
    parsons=[
        PARSONS("p1", "A safe converter",
                "Order the lines into a function that turns text into an int, or gives `None` if it can't, then print the results for `\"12\"` and `\"twelve\"` (`12 None`). Indentation is set. Two decoys hide errors or invent numbers.",
                ["def to_int(text):", "    try:", "        return int(text)", "    except ValueError:", "        return None", 'print(to_int("12"), to_int("twelve"))'],
                """
                import re
                check("prints 12 None", lambda: out.strip() == "12 None")
                check("catches ValueError by name", lambda: re.search(r"except\\s+ValueError", code_bare) is not None and re.search(r"except\\s*:", code_bare) is None, "A bare except would also hide typos.")
                """,
                distractors=["    except:", "        return 0"]),
    ],
    teach=TEACH(
        "Describe the debugging method from this lesson in your own words, using the stuck tram from lesson 3 as your example.",
        "Reproduce it: run the tram program and see it never reach the depot. Read the evidence: the output repeats 'Stops left: 5' forever. Form a hypothesis: the condition `stops_left > 0` never becomes false, so nothing in the loop changes `stops_left`. Test the hypothesis by printing `stops_left` each pass, or by tracing by hand. Fix one thing (subtract 1 each pass), run again, and check the whole output, including the end.",
        points=[
            "Reproduce the failure reliably, with the smallest case",
            "Read the evidence (output or traceback) before changing code",
            "State a belief about a value and check it with print or assert",
            "Change one thing, then rerun and check the whole output",
        ]),
    terms=[
        TERM("syntax error", "Python cannot even read the code: a missing bracket, colon or quote. Nothing runs, not even the lines before it.", '`print("hi"` (no closing bracket)', "Expecting the lines above the mistake to run first.", card=False, id="t0"),
        TERM("runtime error", "The code is valid but something goes wrong while running, raising an exception at that line.", "`10 // 0`", "", q="What is a runtime error? Give an example.", id="t1"),
        TERM("logic error", "The code runs without errors but gives the wrong answer. Only tests find these.", "`range(1, len(xs))` that silently skips the first item", "", card=False, id="t2"),
        TERM("exception", "An object Python raises to signal an error; it travels up through the callers until an `except` handles it or the program stops.", '`ValueError("negative")`', "", card=False, id="t3"),
        TERM("try / except", "Run a block, and if a named exception happens, run the handler instead of stopping.", "`except ValueError:`", "A bare `except:` that also hides typos and real bugs.", q="What does `except ValueError:` after a `try` block do?", id="t4"),
        TERM("else / finally", "`else` runs if no exception happened; `finally` always runs, even after return.", '`finally: print("closing")`', "", card=False, id="t5"),
        TERM("raise", "Signal an error yourself, with a message. The function stops on that line.", '`raise ValueError("no fares")`', "", card=False, id="t6"),
        TERM("ValueError", "The value has the right type but unusable content, or unpacking got the wrong number of parts.", '`int("seven")`', "", card=False, id="t7"),
        TERM("TypeError", "An operation got a value of the wrong type.", '`"12" + 7`', "", q='What does `"12" + 7` raise, and why?', id="t8"),
        TERM("IndexError", "A sequence index is out of range.", "`[1, 2][2]`", "Forgetting that a list of length 2 has positions 0 and 1.", q="What does `[1, 2][2]` raise?", id="t9"),
        TERM("ZeroDivisionError", "Division or modulo by zero.", "`5 / 0`, `5 % 0`", "", q="Which exception do `5 / 0` and `5 % 0` raise?", id="t10"),
        TERM("debugging", "Reproduce, read the evidence, form a hypothesis, test it, fix one thing, re-check.", "Printing `total` inside a loop to see where it first goes wrong", "Changing several things at once and not knowing which fixed it.", card=False, id="t11"),
        TERM("EAFP / LBYL", "Two styles. EAFP: try it and catch the exception. LBYL: check the condition first, then act.", "EAFP: `try: n = int(t)` / `except ValueError:`. LBYL: `if t.isdigit(): n = int(t)`", "", card=False, id="t-eafp"),
        TERM("isinstance()", "`isinstance(value, type)` gives True if the value is of that type.", "`isinstance(5, int)` is True; `isinstance(\"5\", int)` is False", "", q='What do `isinstance(5, int)` and `isinstance("5", int)` give?', id="t-isinstance"),
    ],
    nit_right=[
        "Correct. The rest of a `try` block is skipped the moment one line raises.",
        "Accepted. `finally` ran, as it does on every way out, including a return.",
        "Right. You read the traceback's last line first. It is where the error introduces itself.",
    ],
)
