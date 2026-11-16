from dsl import *

CITY = city(
    "py04",
    opener="Functions are stamps. Carve one carefully and you can press it a thousand times. Carve it badly and you get a thousand mistakes.",
    scene="""
    The Workshop's stamp press makes every brass ticket by hand: same shape, same lettering, fresh effort each time. The apprentices are exhausted. Their fare sheet looks like this, one copy of the rule per passenger:

    ```
    stops = 3
    print(min(stops * 2, 12))
    stops = 9
    print(min(stops * 2, 12))
    stops = 4
    print(min(stops * 2, 21))
    ```

    One copy has a typo nobody noticed: the cap is 21 instead of 12. "Carve the stamp once," says the old press-keeper, "then press." The fare stamp job below carves it: one function, one rule, one place to fix.

    NIT: "This is the most important idea in programming. I would underline it if I had a pen." """,
    jobs=[
        JOB("story", "fare_for", "The fare stamp",
            """
            Write `fare_for(stops, day_pass=False)`. A trip costs 2 coins per stop, but never more than 12 coins. Anyone with a day pass pays 0. The function must **return** the fare, not print it.""",
            "def fare_for(stops, day_pass=False):\n    pass\n",
            """
            f = ns.get("fare_for")
            check("defines fare_for", lambda: callable(f), "Keep the line def fare_for(stops, day_pass=False):")
            check_eq("3 stops cost 6", lambda: silent(f, 3)[0], 6, "2 coins per stop: stops * 2.")
            check("returns rather than prints", lambda: silent(f, 4) == (8, ""), "Use return. Printing inside the function gives the caller None.")
            check_eq("10 stops are capped at 12", lambda: f(10), 12, "Use min(...) or an if to cap the fare.")
            check_eq("6 and 7 stops both cost 12", lambda: [f(6), f(7)], [12, 12], "The cap starts exactly at 6 stops (6 * 2 = 12).")
            check_eq("0 and 1 stops", lambda: [f(0), f(1)], [0, 2], "Compute from stops; do not list the answers.")
            check_eq("a day pass costs 0", lambda: [f(5, day_pass=True), f(10, True)], [0, 0], "Check day_pass first and return 0 straight away.")
            """,
            "If day_pass is true, return 0. Otherwise return min(stops * 2, 12).",
            "def fare_for(stops, day_pass=False):\n    if day_pass:\n        return 0\n    return min(stops * 2, 12)"),
        JOB("repair", "speed", "Repair the speed gauge",
            """
            This should print `Speed: 24.0 km/h`, but it prints `24.0` and then `Speed: None km/h`. Repair `average_speed` so it gives its result back to the caller.""",
            'def average_speed(distance, minutes):\n    print(distance / minutes * 60)\n\nspeed = average_speed(12, 30)\nprint(f"Speed: {speed} km/h")\n',
            """
            check_eq("prints only Speed: 24.0 km/h", lambda: out.strip(), "Speed: 24.0 km/h", "The function prints its answer instead of handing it back.")
            f = ns.get("average_speed")
            check_eq("average_speed(10, 60) returns 10.0", lambda: silent(f, 10, 60)[0], 10.0, "Return distance / minutes * 60.")
            check_eq("average_speed prints nothing itself", lambda: silent(f, 10, 60)[1], "", "Remove the print inside the function: the caller prints.")
            """,
            "A function without return gives back None. Replace print with return.",
            'def average_speed(distance, minutes):\n    return distance / minutes * 60\n\nspeed = average_speed(12, 30)\nprint(f"Speed: {speed} km/h")', kind="fix"),
    ],
    read=[
        READ("r1", "The press-keeper's notebook",
             """
             def press(x, times=2):
                 return x * times

             def bump(n):
                 n = n + 1
                 return n

             n = 5
             bump(n)
             print(n, bump(n))
             print(press(3), press("ab"), press(2, times=4))

             def countdown(k):
                 if k == 0:
                     return "go"
                 return str(k) + " " + countdown(k - 1)

             print(countdown(3))
             """,
             "`bump` has its own local `n`; changing it never touches the outer `n`, and the first call's result is thrown away, so `n` is still 5 and `bump(n)` gives 6. `press` doubles by default: 6, `abab`, and with `times=4` it gives 8. `countdown` calls itself with a smaller `k` until the base case returns `go`, building `3 2 1 go`."),
    ],
    parsons=[
        PARSONS("p1", "The speed limiter",
                "Order the lines into a function that lowers the speed to the limit when it is too high and returns it, then prints the results for 40 and 20 with a limit of 30 (`30 20`). Indentation is set. One decoy prints instead of returning.",
                ["def safe_speed(speed, limit):", "    if speed > limit:", "        speed = limit", "    return speed", "print(safe_speed(40, 30), safe_speed(20, 30))"],
                """
                check_eq("prints 30 20", lambda: out.strip(), "30 20", "The function must return; only the last line prints.")
                f = ns.get("safe_speed")
                check("safe_speed(5, 10) returns 5", lambda: f is not None and silent(f, 5, 10) == (5, ""), "Below the limit the speed comes back unchanged.")
                """,
                distractors=["        print(limit)"],
                hint="The decoy prints instead of returning: leave it out."),
    ],
    teach=TEACH(
        "What is the difference between printing a value inside a function and returning it? Use the speed gauge bug to explain why the program printed `None`.",
        "`print` shows a value on the screen and nothing else: the program cannot use what was printed. `return` hands the value back to whoever called the function, so it can be stored, compared or printed later. `average_speed` printed 24.0 but had no `return`, and every function without one returns `None`. So `speed` was `None`, and the f-string showed it.",
        points=[
            "print shows text to a person; the program cannot use it",
            "return hands the value back to the caller to store or use",
            "a function with no return gives back None",
            "speed was None, so the f-string showed None",
        ]),
    terms=[
        TERM("function", "A named, reusable block of code that takes inputs and can give back a result.", "`def fare_for(stops): ...`", "Writing `fare_for` without brackets when you meant to call it: that names the function, it does not run it.", q="What is a function, in one sentence?", id="t0"),
        TERM("parameter", "A name in the function definition that receives a value when the function is called.", "`stops` in `def fare_for(stops):`", "", card=False, id="t1"),
        TERM("argument", "The actual value passed in a call.", "`3` in `fare_for(3)`", "", card=False, id="t2"),
        TERM("return value", "What a call gives back. Without `return`, a function returns `None`.", "`fare = fare_for(3)` stores the returned 6", "Printing inside the function and expecting the caller to receive the value.", card=False, id="t3"),
        TERM("default argument", "A parameter with a value used when the caller leaves it out.", "`day_pass=False`", "Using a list or dict as a default: it is shared between calls (lesson 6).", card=False, id="t4"),
        TERM("keyword argument", "An argument passed by name, so order does not matter and the call reads clearly.", "`fare_for(5, day_pass=True)`", "Putting a positional argument after a keyword one: `f(day_pass=True, 5)` is a SyntaxError.", q="What is a keyword argument, and why use one?", id="t5"),
        TERM("scope", "Where a name can be seen. Names assigned inside a function are local to it.", "`rate = 20` inside a function does not change the outer `rate`.", "Expecting a function to change an outer name by assigning to it.", card=False, id="t6"),
        TERM("docstring", "A string written as the first statement of a function's body. Python keeps it in `name.__doc__`.", '`"""Return the fare in coins."""` on the line after `def fare_for(stops):`', "", card=False, id="t7"),
        TERM("assert", "A statement that raises AssertionError if its condition is false. Used for quick self-checks.", "`assert fare_for(3) == 6`", "", card=False, id="t8"),
        TERM("recursion", "A function that calls itself on a smaller version of the problem.", "`countdown(k - 1)`", "Forgetting the base case, giving RecursionError.", card=False, id="t9"),
        TERM("base case", "The input where a recursive function stops calling itself and returns directly.", "`if k == 0: return \"go\"`", "", card=False, id="t10"),
        TERM("side effect", "Anything a function does that the caller can notice besides returning a value: printing, changing a global name, changing a list it was given.", "`print(...)` inside a function, or `doses.append(5)`", "Hiding a side effect in a function whose name sounds like a calculation.", q="What counts as a side effect of a function?", id="t-side-effect"),
        TERM("pure function", "A function that only uses its arguments and returns a result, with no side effects.", "`def bmi(w, h): return w / h ** 2`", "", card=False, id="t-pure"),
        TERM("local variable", "A name assigned inside a function. It exists only during that call, and each call gets a fresh one.", "`x` in `def f(): x = 1`", "Reading it before it is assigned in the same function: UnboundLocalError.", card=False, id="t-local"),
        TERM("call stack", "The pile of calls that have started but not finished. Each recursive call adds one; Python stops at about 1000 with RecursionError.", "`fact(3)` waits for `fact(2)`, which waits for `fact(1)`.", "", q="What is the call stack, and what happens when it gets too deep?", id="t-stack"),
    ],
    nit_right=[
        "Correct. A function without `return` gives back `None`; yours gave back something better.",
        "Accepted. Assigning to a name inside a function makes it local for the whole function, which I find tidy.",
        "Matched. Each recursive call waits for the smaller one, so the calls finish in reverse order.",
    ],
)
