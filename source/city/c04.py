from dsl import *

CITY = city(
    "py04",
    opener="Functions are stamps. Carve one carefully and you can press it a thousand times. Carve it badly and you get a thousand mistakes.",
    scene="""
    The Workshop's stamp press makes every brass ticket by hand: same shape, same lettering, fresh effort each time. The apprentices are exhausted.

    "Carve the stamp once," says the old press-keeper, "then press."

    NIT: "This is the most important idea in programming. I would underline it if I had a pen." """,
    jobs=[
        JOB("story", "fare_for", "The fare stamp",
            """
            Write `fare_for(stops, day_pass=False)`. A trip costs 2 coins per stop, but never more than 12 coins. Anyone with a day pass pays 0. The function must **return** the fare, not print it.""",
            "def fare_for(stops, day_pass=False):\n    pass\n",
            """
            f = ns.get("fare_for")
            check("defines fare_for", lambda: callable(f))
            check("3 stops cost 6", lambda: f(3) == 6)
            check("10 stops are capped at 12", lambda: f(10) == 12, "Use min(...) or an if to cap the fare.")
            check("0 stops cost 0", lambda: f(0) == 0)
            check("a day pass costs 0", lambda: f(5, day_pass=True) == 0, "Check day_pass first.")
            check("returns rather than prints", lambda: f(4) == 8, "Use return. Printing inside the function gives the caller None.")
            """,
            "If day_pass is true, return 0. Otherwise return min(stops * 2, 12).",
            "def fare_for(stops, day_pass=False):\n    if day_pass:\n        return 0\n    return min(stops * 2, 12)"),
        JOB("repair", "speed", "Repair the speed gauge",
            """
            This should print `Speed: 24.0 km/h`, but it prints `24.0` and then `Speed: None km/h`. Repair `average_speed` so it gives its result back to the caller.""",
            'def average_speed(distance, minutes):\n    print(distance / minutes * 60)\n\nspeed = average_speed(12, 30)\nprint(f"Speed: {speed} km/h")\n',
            """
            check("prints only Speed: 24.0 km/h", lambda: out.strip() == "Speed: 24.0 km/h", "The function prints its answer instead of handing it back.")
            f = ns.get("average_speed")
            check("average_speed(10, 60) returns 10.0", lambda: f(10, 60) == 10.0)
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
                "Order the lines into a function that returns the speed, but never more than the limit, then prints the results for 40 and 20 with a limit of 30 (`30 20`). Indentation is set. One decoy prints instead of returning.",
                ["def safe_speed(speed, limit):", "    if speed > limit:", "        return limit", "    return speed", "print(safe_speed(40, 30), safe_speed(20, 30))"],
                """
                check("prints 30 20", lambda: out.strip() == "30 20")
                f = ns.get("safe_speed")
                check("safe_speed(5, 10) returns 5", lambda: f is not None and f(5, 10) == 5)
                """,
                distractors=["        print(limit)"]),
    ],
    teach=TEACH(
        "What is the difference between printing a value inside a function and returning it? Use the speed gauge bug to explain why the program printed `None`.",
        "`print` shows a value on the screen and nothing else: the program cannot use what was printed. `return` hands the value back to whoever called the function, so it can be stored, compared or printed later. `average_speed` printed 24.0 but had no `return`, and every function without one returns `None`. So `speed` was `None`, and the f-string showed it."),
    terms=[
        TERM("function", "A named, reusable block of code that takes inputs and can give back a result.", "`def fare_for(stops): ...`", ""),
        TERM("parameter", "A name in the function definition that receives a value when the function is called.", "`stops` in `def fare_for(stops):`", ""),
        TERM("argument", "The actual value passed in a call.", "`3` in `fare_for(3)`", ""),
        TERM("return value", "What a call gives back. Without `return`, a function returns `None`.", "", "Printing inside the function and expecting the caller to receive the value."),
        TERM("default argument", "A parameter with a value used when the caller leaves it out.", "`day_pass=False`", "Using a list or dict as a default: it is shared between calls (lesson 6)."),
        TERM("keyword argument", "An argument passed by name, so order does not matter and the call reads clearly.", "`fare_for(5, day_pass=True)`", ""),
        TERM("scope", "Where a name can be seen. Names assigned inside a function are local to it.", "", "Expecting a function to change an outer name by assigning to it."),
        TERM("docstring", "A string as the first line of a function that explains what it does.", '`"""Return the fare in coins."""`', ""),
        TERM("assert", "A statement that raises AssertionError if its condition is false. Used for quick self-checks.", "`assert fare_for(3) == 6`", ""),
        TERM("recursion", "A function that calls itself on a smaller version of the problem.", "`countdown(k - 1)`", "Forgetting the base case, giving RecursionError."),
        TERM("base case", "The input where a recursive function stops calling itself and returns directly.", "`if k == 0: return \"go\"`", ""),
    ],
)
