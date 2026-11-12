from dsl import *

CITY = city(
    "py08",
    opener="Machines fail. Good machines fail loudly, say where, and say why. Bad machines fail quietly and let you find out at dinner.",
    scene="""
    The fare box is back on the tram, writing a log line for every stop. But the ink smudges: some lines are unreadable, and the old program simply stops when it meets one. Wren wants the day's total anyway.

    NIT: "Never let one smudge stop the whole day. Also never pretend the smudge is not there. Count it." """,
    jobs=[
        JOB("story", "fare_log", "Read the smudged log",
            """
            Each log line looks like `"06:15,7"`: a time, a comma, the coins taken. Some lines are smudged and can't be read. Write `total_coins(lines)` that returns a tuple `(total, bad)`: the sum of the coins on the good lines and the number of bad lines.

            A line is bad if it does not split into exactly two parts on the comma, or if the coins part is not a whole number. Catch only the errors you expect.""",
            "def total_coins(lines):\n    pass\n",
            """
            f = ns.get("total_coins")
            check("defines total_coins", lambda: callable(f))
            check("all good lines", lambda: f(["06:15,7", "08:00,12"]) == (19, 0))
            check("smudged coins and a line with no comma", lambda: f(["06:15,7", "07:00,x", "garbage", "08:00,12"]) == (19, 2), "Unpacking the wrong number of parts and int('x') both raise ValueError.")
            check("too many commas is bad", lambda: f(["06:15,7,9"]) == (0, 1))
            check("an empty log", lambda: f([]) == (0, 0))
            check("catches a specific exception", lambda: "except ValueError" in code or "except (ValueError" in code, "A bare except would also hide real bugs, such as a typo in a name.")
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
            check("[2, 4] gives 3.0", lambda: f([2, 4]) == 3.0)
            check("an empty list raises ValueError", lambda: raises(lambda: f([]), ValueError), "Check for the empty case first and raise ValueError(\\"...\\").")
            check("text in the list raises TypeError", lambda: raises(lambda: f([2, "x"]), TypeError), "Remove the blanket except so real errors surface.")
            """,
            "Delete the try/except. Before dividing, if not fares: raise ValueError('no fares to average').",
            'def average_fare(fares):\n    if not fares:\n        raise ValueError("no fares to average")\n    return sum(fares) / len(fares)', kind="fix"),
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
             "For 3: the try succeeds, `else` prints `fine`, and `finally` prints `logged 3` before the return value 3 is printed. For 0: `ZeroDivisionError` jumps to the except branch, which prints `zero!`; `finally` still prints `logged 0`; then -1 is printed. `int(\"seven\")` raises ValueError, and `type(e).__name__` is its class name."),
    ],
    parsons=[
        PARSONS("p1", "A safe converter",
                "Order the lines into a function that turns text into an int, or gives `None` if it can't, then print the results for `\"12\"` and `\"twelve\"` (`12 None`). Indentation is set. Two decoys hide errors or invent numbers.",
                ["def to_int(text):", "    try:", "        return int(text)", "    except ValueError:", "        return None", 'print(to_int("12"), to_int("twelve"))'],
                """
                check("prints 12 None", lambda: out.strip() == "12 None")
                check("catches ValueError by name", lambda: "except ValueError" in code, "A bare except would also hide typos.")
                """,
                distractors=["    except:", "        return 0"]),
    ],
    teach=TEACH(
        "Describe the debugging method from this lesson in your own words, using the stuck tram from lesson 3 as your example.",
        "Reproduce it: run the tram program and see it never reach the depot. Read the evidence: the output repeats 'Stops left: 5' forever. Form a hypothesis: the condition `stops_left > 0` never becomes false, so nothing in the loop changes `stops_left`. Test the hypothesis by printing `stops_left` each pass, or by tracing by hand. Fix one thing (subtract 1 each pass), run again, and check the whole output, including the end."),
    terms=[
        TERM("syntax error", "Python cannot even read the code: a missing bracket, colon or quote. Nothing runs.", "", ""),
        TERM("runtime error", "The code is valid but something goes wrong while running, raising an exception.", "`10 // 0`", ""),
        TERM("logic error", "The code runs without errors but gives the wrong answer. Only tests find these.", "", ""),
        TERM("exception", "An object Python raises to signal an error; it travels up until something handles it or the program stops.", "", ""),
        TERM("try / except", "Run a block, and if a named exception happens, run the handler instead of stopping.", "`except ValueError:`", "A bare `except:` that also hides typos and real bugs."),
        TERM("else / finally", "`else` runs if no exception happened; `finally` always runs, even after return.", "", ""),
        TERM("raise", "Signal an error yourself, with a message.", '`raise ValueError("no fares")`', ""),
        TERM("ValueError", "The value has the right type but an unusable content.", '`int("seven")`', ""),
        TERM("TypeError", "An operation got a value of the wrong type.", '`"12" + 7`', ""),
        TERM("IndexError", "A sequence index is out of range.", "`[1, 2][2]`", ""),
        TERM("ZeroDivisionError", "Division or modulo by zero.", "", ""),
        TERM("debugging", "Reproduce, read the evidence, form a hypothesis, test it, fix one thing, re-check.", "", "Changing several things at once and not knowing which fixed it."),
    ],
)
