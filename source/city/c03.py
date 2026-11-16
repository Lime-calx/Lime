from dsl import *

CITY = city(
    "py03",
    opener="Today: the tram loop, and the station clock. A loop whose condition never changes is a tram that never reaches the depot. Watch your conditions.",
    scene="""
    The Number 1 tram has stopped at Brass Yard and will not leave. Its program says "while there are stops left, announce the stop". It announced `Stops left: 5` twenty times, until its safety brake counted the announcements and pulled itself.

    Wren sighs. "It's very polite about it." Here is the program the tram is running:

    ```
    stops_left = 5
    announced = 0
    while stops_left > 0:
        print("Stops left:", stops_left)
        announced += 1
        if announced == 20:
            print("Safety brake! Still", stops_left, "stops left.")
            break
    print("Depot!")
    ```

    NIT: "Politeness is not progress. The condition is checked before every pass, and nothing inside the loop changes `stops_left`. Predict the output, then repair it below. While you are at it, the station clock has said 06:00 for eleven years: it has never had a loop at all." """,
    jobs=[
        JOB("story", "timetable", "Start the station clock",
            """
            NIT wires your timetable into the station clock. The first tram leaves at `start_hour`:00 and then every `every` minutes, up to and including `last` minutes after the first. Print each departure as `HH:MM`, one per line. With the values given that is 06:00, 06:15, ... 08:00 (nine lines), and for the first time in eleven years the clock shows something other than 06:00. Keep the three setting lines: the checker changes all of them.""",
            "start_hour = 6\nevery = 15\nlast = 120\n",
            """
            want = ["06:00", "06:15", "06:30", "06:45", "07:00", "07:15", "07:30", "07:45", "08:00"]
            check_eq("prints the nine departures", lambda: out.strip().split("\\n"), want, "Loop over the minutes after the first tram, then split each into hours (// 60) and minutes (% 60).")
            check("uses a loop", lambda: has_node("For", "While"), "Let a loop produce the lines, so the clock keeps moving whatever the settings.")
            def other():
                ns2, out2 = rerun("every = 15", "every = 40")
                return out2.strip().split("\\n")
            check_eq("works when trams run every 40 minutes", other, ["06:00", "06:40", "07:20", "08:00"], "Use every as the step of your range.")
            def late():
                ns2, out2 = rerun("start_hour = 6", "start_hour = 9")
                return out2.strip().split("\\n")
            check_eq("works when the first tram is at 09:00", late, ["09:00", "09:15", "09:30", "09:45", "10:00", "10:15", "10:30", "10:45", "11:00"], "Add start_hour to the hours you work out from the minutes.")
            def short():
                ns2, out2 = rerun("last = 120", "last = 60")
                return out2.strip().split("\\n")
            check_eq("works when the last tram is 60 minutes after the first", short, ["06:00", "06:15", "06:30", "06:45", "07:00"], "Build the stop from last. To include last itself, stop one past it: last + 1.")
            """,
            "range(0, last + 1, every) gives the minutes after the start. For each one, the hour is start_hour + m // 60 and the minute is m % 60. Pad both with :02d.",
            'start_hour = 6\nevery = 15\nlast = 120\nfor m in range(0, last + 1, every):\n    hour = start_hour + m // 60\n    minute = m % 60\n    print(f"{hour:02d}:{minute:02d}")'),
        JOB("repair", "stuck_tram", "Repair the stuck tram",
            """
            This is the tram's program from the scene. It should count down the stops to the depot and then print `Depot!`, but nothing inside the loop changes `stops_left`, so the safety brake has to stop it. Repair it so the output is `Stops left: 5` down to `Stops left: 1`, then `Depot!`. Keep the line `stops_left = 5`: the checker changes it.""",
            'stops_left = 5\nannounced = 0\nwhile stops_left > 0:\n    print("Stops left:", stops_left)\n    announced += 1\n    if announced == 20:\n        print("Safety brake! Still", stops_left, "stops left.")\n        break\nprint("Depot!")\n',
            """
            want = ["Stops left: 5", "Stops left: 4", "Stops left: 3", "Stops left: 2", "Stops left: 1", "Depot!"]
            check_eq("counts down and reaches the depot", lambda: out.strip().split("\\n"), want, "The condition is checked again before each pass. What inside the loop should change stops_left?")
            def other():
                ns2, out2 = rerun("stops_left = 5", "stops_left = 3")
                return out2.strip().split("\\n")
            check_eq("works from 3 stops", other, ["Stops left: 3", "Stops left: 2", "Stops left: 1", "Depot!"], "Let the loop do the counting; do not print the lines yourself.")
            """,
            "Inside the loop, after printing, take one off: stops_left -= 1. The brake can stay; it will never trip.",
            'stops_left = 5\nannounced = 0\nwhile stops_left > 0:\n    print("Stops left:", stops_left)\n    stops_left -= 1\n    announced += 1\n    if announced == 20:\n        print("Safety brake! Still", stops_left, "stops left.")\n        break\nprint("Depot!")', kind="fix"),
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
        "Use `for` when you know what you are going through before you start: `for stop in range(5)` visits each of 5 stops. Use `while` when you repeat until a condition changes and you don't know how many passes that takes: `while fuel > 0` keeps driving until the tank is empty. The condition is checked before every pass, so a `while` loop needs something inside it that moves toward making the condition false, or it never ends. `while True` with a `break` is the shape for stopping from the middle.",
        points=[
            "for: the items or the count are known before the loop starts",
            "while: repeat until a condition changes, number of passes unknown",
            "while checks its condition before every pass",
            "the body must change what the condition depends on, or the loop never ends",
        ]),
    terms=[
        TERM("boolean expression", "An expression whose value is `True` or `False`.", "`fuel > 0`", "", q="What kind of value does a boolean expression such as `fuel > 0` produce?", id="t0"),
        TERM("comparison operators", "`==`, `!=`, `<`, `<=`, `>`, `>=`. They can be chained: `0 < x < 10`. Text compares character by character.", "`stops == 0`", 'Comparing numbers stored as text: `"10" < "9"` is True.', card=False, id="t1"),
        TERM("short-circuit evaluation", "`and` stops at the first falsy value and `or` at the first truthy one; the rest is never run.", '`0 or "spare"` is `"spare"`.', "Expecting `and`/`or` to always return True or False. They return one of the values.", card=False, id="t2"),
        TERM("truthiness", "Every value counts as true or false in a condition. False: `0`, `0.0`, `\"\"`, `[]`, `{}`, `None`, `False`. Everything else is true.", '`if name:` is false for an empty name.', '`"0"` and `"False"` are non-empty strings, so they are truthy.', card=False, id="t3"),
        TERM("elif", "Short for \"else if\": a further condition in an if chain, tested only when every branch above it was false. Only the first true branch runs.", "`if t >= 39: ... elif t >= 38: ...`", "Writing several separate `if`s when only one branch should run.", card=False, id="t4"),
        TERM("else", "The last branch of an if chain: it runs when no condition above it was true. It belongs to the `if` directly above it.", '`if fuel > 0: print("go")` then `else: print("refuel")`', "Expecting an `else` to cover an earlier, separate `if`.", card=False, id="t-else"),
        TERM("while loop", "Repeats a block while a condition is true, checking before each pass.", "`while stops_left > 0:`", "Forgetting to change anything the condition depends on: an infinite loop.", card=False, id="t5"),
        TERM("for loop", "Repeats a block once for each item of a sequence, pointing the loop variable at each item in turn.", "`for day in range(1, 50):`", "Expecting `i = 10` inside the body to make the loop skip ahead. The next pass sets i again.", q="What does a `for` loop do with its loop variable on each pass?", id="t6"),
        TERM("range", "`range(start, stop, step)` gives numbers from start up to but not including stop.", "`range(0, 121, 15)` gives 0, 15, ..., 120.", "Expecting the stop value to be included.", card=False, id="t7"),
        TERM("accumulator", "A name that starts empty or at zero before a loop and collects a result during it.", "`total = 0` then `total += x`", "Resetting the accumulator inside the loop.", card=False, id="t8"),
        TERM("break", "Leaves the loop it is in at once. The code after the loop runs next.", "`if n % 7 == 0: break`", "Expecting it to leave an outer loop too: it leaves only the innermost one.", card=False, id="t9"),
        TERM("continue", "Skips the rest of this pass of the loop and starts the next pass.", "`if n % 2 == 0: continue`", "Using it when you meant to stop the loop: that is `break`.", card=False, id="t-continue"),
        TERM("infinite loop", "A loop whose condition never becomes false. Lime tries to stop it after a few seconds; ordinary Python runs until you interrupt it.", "`while stops_left > 0: print(stops_left)` (nothing changes stops_left)", "", q="What turns a `while` loop into an infinite loop?", id="t10"),
        TERM("flag", "A bool that records whether something has happened yet, such as `found = False` before a search and `found = True` when it succeeds.", "`found = False` ... `if t > 39: found = True`", "Resetting the flag inside the loop, so it only reports the last pass.", q="What is a flag variable used for in a loop?", id="t-flag"),
        TERM("running maximum", "A name holding the biggest value seen so far, replaced whenever a bigger one comes along.", "`best = values[0]` then `if v > best: best = v`", "Starting it at 0, which is wrong when every value is negative.", card=False, id="t-runmax"),
    ],
    nit_right=[
        "Correct. `range(5)` stopped before 5, as it always will.",
        "Matched. `not` runs after `==`, so `not x == 5` asks `not (x == 5)`. I admire its patience.",
        "Accepted. A loop's `else` runs only when no `break` fired. It is the most literal keyword I know.",
    ],
)
