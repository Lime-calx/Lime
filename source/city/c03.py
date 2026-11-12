from dsl import *

CITY = city(
    "py03",
    opener="Today: the tram loop. A loop whose condition never changes is a tram that never reaches the depot. Watch your conditions.",
    scene="""
    The Number 1 tram has stopped at Brass Yard and will not leave. Its program says "while there are stops left, announce the stop". It has announced Brass Yard four thousand times.

    Wren sighs. "It's very polite about it."

    NIT: "Politeness is not progress. Something inside the loop must move it toward the end." """,
    jobs=[
        JOB("story", "timetable", "Print the tram timetable",
            """
            The tram leaves at 06:00 and then every `every` minutes, up to and including `last` minutes after 06:00. Print each departure as `HH:MM`, one per line. With the values given, that is 06:00, 06:15, ... 08:00 (nine lines). Keep the three setting lines: the checker changes them.""",
            "start_hour = 6\nevery = 15\nlast = 120\n",
            """
            want = ["06:00", "06:15", "06:30", "06:45", "07:00", "07:15", "07:30", "07:45", "08:00"]
            check("prints the nine departures", lambda: out.strip().split("\\n") == want, "Loop over the minutes after 06:00, then split each into hours and minutes.")
            check("uses a loop", lambda: "for " in code or "while " in code, "Let the loop produce the lines.")
            def other():
                ns2, out2 = rerun("every = 15", "every = 40")
                return out2.strip().split("\\n") == ["06:00", "06:40", "07:20", "08:00"]
            check("works when trams run every 40 minutes", other)
            def late():
                ns2, out2 = rerun("start_hour = 6", "start_hour = 9")
                return out2.strip().split("\\n")[-1] == "11:00"
            check("works when the first tram is at 09:00", late)
            """,
            "range(0, last + 1, every) gives the minutes after the start. For each one, the hour is start_hour + m // 60 and the minute is m % 60. Pad both with :02d.",
            'start_hour = 6\nevery = 15\nlast = 120\nfor m in range(0, last + 1, every):\n    hour = start_hour + m // 60\n    minute = m % 60\n    print(f"{hour:02d}:{minute:02d}")'),
        JOB("repair", "stuck_tram", "Repair the stuck tram",
            """
            This loop should count down the stops to the depot and then print `Depot!`. Instead it never ends (Lime stops it after a few seconds). Repair it. The output should be `Stops left: 5` down to `Stops left: 1`, then `Depot!`.""",
            'stops_left = 5\nwhile stops_left > 0:\n    print("Stops left:", stops_left)\nprint("Depot!")\n',
            """
            want = ["Stops left: 5", "Stops left: 4", "Stops left: 3", "Stops left: 2", "Stops left: 1", "Depot!"]
            check("counts down and reaches the depot", lambda: out.strip().split("\\n") == want, "The condition is checked again each time round. What inside the loop should change it?")
            """,
            "Inside the loop, after printing, take one off stops_left.",
            'stops_left = 5\nwhile stops_left > 0:\n    print("Stops left:", stops_left)\n    stops_left -= 1\nprint("Depot!")', kind="fix"),
    ],
    read=[
        READ("r1", "The fuel gauge",
             """
             stops = 0
             fuel = 10
             while fuel > 0:
                 fuel -= 3
                 stops += 1
             print(stops, fuel)
             total = 0
             for i in range(1, 8):
                 if i % 2 == 0:
                     continue
                 if i > 5:
                     break
                 total += i
             print(total)
             print(0 or "spare", 3 and 0, not "")
             """,
             "Fuel goes 10, 7, 4, 1, -2: the check happens before each pass, so the loop runs 4 times and fuel ends at -2. In the for loop, even numbers are skipped and 7 triggers `break`, so total is 1 + 3 + 5 = 9. `or` returns the first truthy value (`spare`); `and` returns the first falsy one (0); an empty string is falsy, so `not \"\"` is True."),
    ],
    parsons=[
        PARSONS("p1", "Count the inspection days",
                "The tram is inspected on every day number from 1 to 49 that is a multiple of 7. Order the lines to count those days and print the count (`7`). Indentation is already set. Two lines are decoys.",
                ["count = 0", "for day in range(1, 50):", "    if day % 7 == 0:", "        count += 1", "print(count)"],
                """
                check("prints 7", lambda: out.strip() == "7", "Start the counter before the loop and print after it.")
                """,
                distractors=["    count = 0", "    print(day)"]),
    ],
    teach=TEACH(
        "When would you use `while` instead of `for`? Give one tram example of each and say why.",
        "Use `for` when you know what you are going through before you start: `for stop in range(5)` visits each of 5 stops. Use `while` when you repeat until a condition changes and you don't know how many passes that takes: `while fuel > 0` keeps driving until the tank is empty. A `while` loop needs something inside it that moves toward making the condition false, or it never ends."),
    terms=[
        TERM("boolean expression", "An expression whose value is `True` or `False`.", "`fuel > 0`", ""),
        TERM("comparison operators", "`==`, `!=`, `<`, `<=`, `>`, `>=`. They can be chained: `0 < x < 10`.", "`stops == 0`", "Using `=` (assignment) where you meant `==` (comparison)."),
        TERM("short-circuit evaluation", "`and` stops at the first falsy value and `or` at the first truthy one; the rest is never run.", '`0 or "spare"` is `"spare"`.', "Expecting `and`/`or` to always return True or False. They return one of the values."),
        TERM("truthiness", "Every value counts as true or false in a condition. False: `0`, `0.0`, `\"\"`, `[]`, `{}`, `None`, `False`. Everything else is true.", '`if name:` is false for an empty name.', '`"0"` and `"False"` are non-empty strings, so they are truthy.'),
        TERM("if / elif / else", "Run the first block whose condition is true; `else` catches everything left.", "", "Writing several separate `if`s when only one branch should run."),
        TERM("while loop", "Repeats a block while a condition is true, checking before each pass.", "`while stops_left > 0:`", "Forgetting to change anything the condition depends on: an infinite loop."),
        TERM("for loop", "Repeats a block once for each item of a sequence.", "`for day in range(1, 50):`", ""),
        TERM("range", "`range(start, stop, step)` gives numbers from start up to but not including stop.", "`range(0, 121, 15)` gives 0, 15, ..., 120.", "Expecting the stop value to be included."),
        TERM("accumulator", "A name that starts empty or at zero before a loop and collects a result during it.", "`total = 0` then `total += x`", "Resetting the accumulator inside the loop."),
        TERM("break / continue", "`break` leaves the loop at once; `continue` skips to the next pass.", "", ""),
        TERM("infinite loop", "A loop whose condition never becomes false. Lime stops it after a few seconds.", "", ""),
    ],
)
