from dsl import *

LESSON = lesson(
    id="py01", track="py", n=1, title="Programs, values and expressions", minutes=40,
    summary="What a program is, how Python runs it, how print shows values, and how Python calculates.",
    goals=[
        "Say what happens, step by step, when Python runs your code",
        "Print text and numbers, and control the spaces and line breaks",
        "Calculate with Python, including whole-number division and remainders",
        "Work out which part of a calculation Python does first",
        "Use an error message to find the line that went wrong",
    ],
    blocks=[
        H("What a program is"),
        P("""
        A program is a precise list of instructions. A computer cannot guess what you meant, so it does exactly what the text says, in order, from the first line to the last.

        A program called the **interpreter** reads your text, checks that all of it is valid Python, and then carries out one instruction at a time. In Lime the interpreter runs inside this page."""),
        CODE("""
        print("Hello, world")
        print("Lines run top to bottom")
        """),
        P("""
        A **function** is a named piece of code that does one job. You **call** it by writing its name and brackets: `print(...)` calls the function `print`, whose job is to show what is inside the brackets. Text inside quotes is a **string**: Python shows it exactly as written, without the quotes.

        Edit the code above and press Run. Changing code and watching what happens is the fastest way to learn."""),
        NOTE("tip", """
        Before you run an example, predict what it will show. Then run it and compare. Predicting first is the habit that builds real understanding."""),

        H("Comments"),
        P("""
        Anything after `#` on a line is a **comment**. Python skips it; it is a note for people. In this course comments sit on their own line above the code they explain."""),
        CODE("""
        # this line is a note: Python skips it
        print("shown")
        # print("not shown")
        """),
        P("""
        Good comments explain *why*, not *what*: `# skip the header row` helps, while a comment that repeats the code does not. Putting `#` in front of a line, as in the last line above, is also a quick way to switch it off."""),

        H("Printing several values"),
        P("""
        Give `print` several values separated by commas and it shows them on one line with **one space** between them. Each `print` then ends the line, so the next `print` starts on a new line. An empty `print()` prints just a line break, which gives a blank line."""),
        CODE("""
        print("total", 91)
        print(1, 2, 3)
        print()
        print("after a blank line")
        """),
        P("""
        Two optional settings change this. `sep="..."` sets what goes *between* the values. `end="..."` sets what goes at the *end* instead of the line break."""),
        CODE("""
        print(13, 11, 2026, sep="/")
        print(1, 2, 3, sep="")
        print("no line break", end=" ")
        print("so this continues")
        """),
        NOTE("trap", """
        The commas are not printed. `print(3, 1)` shows `3 1`, not `3, 1`. If you want commas, ask for them: `print(3, 1, sep=", ")`."""),

        H("Values, expressions and statements"),
        P("""
        A **value** is a piece of data, like `42`, `3.5` or `"hi"`. An **expression** is code that produces a value, like `6 * 7`. A **statement** is a complete instruction, like `print(6 * 7)`. Python works out the expression first, and then the statement uses the result."""),
        CODE("""
        print(6 * 7)
        print(2 ** 8)
        # calculated, then thrown away:
        6 * 7
        """),
        NOTE("trap", """
        An expression alone on a line is calculated and then discarded: nothing is shown. Only `print` shows something."""),
        NOTE("deep", """
        Some tutorials type code into an *interactive shell* (the `>>>` prompt), which shows the value of a bare expression automatically. A program run from a file, like the code in Lime, does not. That is why tutorials sometimes seem to disagree."""),

        H("Two kinds of number"),
        P("""
        Python has two everyday kinds of number. An **int** (integer) is a whole number: `3`, `-7`, `1000`. A **float** is a number with a decimal point: `3.0`, `2.5`. They print differently, so `3` and `3.0` are not the same to look at."""),
        CODE("""
        print(3, 3.0)
        print(2 ** 100)
        print(1 / 3)
        """),
        P("""
        An int can be as large as you like, so `2 ** 100` is exact. A float is stored in binary with a fixed number of digits, so it is an approximation: `1 / 3` shows 16 or so digits and stops. Lesson 2 looks at why."""),

        H("The arithmetic operators"),
        CODE("""
        print(7 + 2)
        print(7 - 2)
        print(7 * 2)
        # true division: always a float
        print(7 / 2)
        # floor division: whole part
        print(7 // 2)
        # remainder (modulo)
        print(7 % 2)
        # power: 7 squared
        print(7 ** 2)
        """),
        NOTE("model", """
        `/` always gives a float, even when the answer is whole: `8 / 2` is `4.0`.

        `//` divides and rounds **down** to a whole number. `%` gives what is left over. Think of 91 coins packed in bags of 20: `91 // 20` is 4 full bags, and `91 % 20` is 11 loose coins. The two always fit back together: 4 bags of 20 plus 11 is 91 again."""),
        CODE("""
        print(91 / 20)
        print(91 // 20)
        print(91 % 20)
        print(91 // 20 * 20 + 91 % 20)
        """),
        P("""
        `//` and `%` appear everywhere in programming: minutes into hours and minutes, packing items into boxes, wrapping round a clock face, picking every 3rd item. A number is even exactly when `n % 2` is 0."""),
        NOTE("deep", """
        "Round down" means toward the more negative number, not toward zero: `-7 // 2` is `-4`, not `-3`, and `-7 % 2` is then `1`, so the two still fit together. The remainder takes the sign of the number you divide by: `7 % -2` is `-1`. If either number is a float, `//` gives a float: `7.0 // 2` is `3.0`. `divmod(91, 20)` gives both answers at once, as the pair `(4, 11)`."""),

        H("Precedence: what Python calculates first"),
        P("""
        With several operators in one expression, Python follows a fixed order, like the order of operations in maths. From first to last:

        - brackets `( )`
        - `**` (power)
        - a minus sign in front of a number, as in `-x` (called **unary minus**)
        - `*`, `/`, `//`, `%`
        - `+` and `-` between two numbers

        Operators on the same rung work left to right, so `6 / 3 * 2` is `(6 / 3) * 2`, which is `4.0`."""),
        CODE("""
        print(2 + 3 * 4)
        print((2 + 3) * 4)
        print(6 / 3 * 2)
        print(-2 ** 2)
        print((-2) ** 2)
        print(2 ** -1)
        """),
        NOTE("trap", """
        `-2 ** 2` is `-4`. The power is on a higher rung than the minus sign, so Python does `2 ** 2` first and then makes it negative: `-(2 ** 2)`. On the other side of `**` the minus is fine: `2 ** -1` is `0.5`. When unsure, add brackets. Extra brackets cost nothing and remove doubt."""),
        NOTE("deep", """
        `**` is the one operator that works right to left: `2 ** 3 ** 2` means `2 ** (3 ** 2)`, which is `2 ** 9`, so `512`, not `64`. The ladder continues below `+` and `-` with comparisons such as `<` and `==`, then `not`, then `and`, then `or`; lesson 3 teaches those."""),

        H("Giving a value a name"),
        P("""
        One more tool, so that the exercises can try your code with other numbers. `fare = 7` gives the value 7 the name `fare`. After that line, writing `fare` in an expression means 7. Lesson 2 explains names properly."""),
        CODE("""
        fare = 7
        passengers = 13
        print(fare * passengers)
        """),

        H("Reading an error message"),
        P("""
        Mistakes are normal. When Python cannot carry on, it stops and reports an **error**. Full Python prints a report called a **traceback**; Lime shows a short traceback: the line number in your code, and on the last line the error type and what went wrong. Read the last line first, then go to the line it names."""),
        CODE("""
        print("before")
        print(1 / 0)
        print("after")
        """),
        P("""
        `before` appears, then the program stops at line 2 and `after` never runs. A **SyntaxError** is different: Python checks the whole program *before* running any of it, so one bad line means nothing at all runs. Here the missing `)` on line 2 stops even line 1:"""),
        CODE("""
        print("before")
        print("after"
        """),
        P("""
        Errors you will meet early:

        - `SyntaxError`: the text is not valid Python, so nothing runs
        - `NameError`: Python does not know a name, often a typo or missing quotes
        - `TypeError`: an operation was used on the wrong kind of value
        - `ZeroDivisionError`: division by zero"""),
        CODE("""
        # no quotes: Python looks for a
        # name called Hello and finds none
        print(Hello)
        """),
        NOTE("model", """
        An error message is information, not punishment. It is a colleague pointing at the exact line and telling you what they saw."""),
    ],
    exercises=[
        EX("hello", "Say hello",
           'Print exactly `Hello, Lime!`',
           "# write your code below\n",
           """
           check_eq("prints Hello, Lime!", lambda: out.strip(), "Hello, Lime!",
                 "The text must match exactly: capital H and L, a comma, an exclamation mark, all inside quotes.")
           """,
           "Use print() with the text inside quotes.",
           'print("Hello, Lime!")'),
        EX("week", "Seconds in a week",
           """
           `days` is the number of days. Print the number of seconds in that many days, built as an expression from 60, 24 and `days`, so that for 7 days it prints `604800`. Print only the number. The checker also tries other values of `days`.""",
           "days = 7\n# print the seconds in that many days\n",
           """
           check_eq("prints 604800 for 7 days", lambda: out.strip(), "604800",
                    "Seconds per minute x minutes per hour x hours per day x days.")
           def other():
               n2, o2 = rerun("days = 7", "days = 1")
               return o2.strip()
           check_eq("prints 86400 for 1 day", other, "86400",
                    "Use the name days in your expression instead of typing 7 or the answer.")
           """,
           "60 seconds x 60 minutes x 24 hours x days.",
           "days = 7\nprint(60 * 60 * 24 * days)"),
        EX("average", "Fix the average",
           """
           This should print the average of `a`, `b` and `c`, which for 4, 8 and 15 is `9.0`, but it prints `17.0`. Fix the calculation. The checker also tries other numbers.""",
           "a = 4\nb = 8\nc = 15\nprint(a + b + c / 3)\n",
           """
           check_eq("prints 9.0", lambda: out.strip(), "9.0",
                    "Division happens before addition. Which part must be added first?")
           def other():
               n2, o2 = rerun("c = 15", "c = 3")
               return o2.strip()
           check_eq("prints 5.0 for 4, 8 and 3", other, "5.0",
                    "Keep calculating from a, b and c; do not type the answer.")
           """,
           "Brackets force the addition to happen before the division.",
           "a = 4\nb = 8\nc = 15\nprint((a + b + c) / 3)", kind="fix"),
        EX("clock", "Hours and minutes",
           """
           A film lasts `minutes` minutes. Print the whole hours on one line and the leftover minutes on the next line, so 135 gives `2` then `15`. Use `//` and `%`. The checker also tries other lengths.""",
           "minutes = 135\n# print hours, then leftover minutes\n",
           """
           check_eq("prints 2 then 15 on two lines", lambda: out.strip().split("\\n"), ["2", "15"],
                    "Two print calls, one per line: hours first, then minutes.")
           def other():
               n2, o2 = rerun("minutes = 135", "minutes = 61")
               return o2.strip().split("\\n")
           check_eq("prints 1 then 1 for 61 minutes", other, ["1", "1"],
                    "Calculate from the name minutes with // 60 and % 60 instead of typing the numbers.")
           """,
           "minutes // 60 gives the hours. minutes % 60 gives what is left over.",
           "minutes = 135\nprint(minutes // 60)\nprint(minutes % 60)"),
        EX("datesep", "A date with slashes",
           """
           Print the date as `13/11/2026` from the three names, using one `print` with `sep`. The checker also tries another day.""",
           "day = 13\nmonth = 11\nyear = 2026\n# print day/month/year below\n",
           """
           check_eq("prints 13/11/2026", lambda: out.strip(), "13/11/2026",
                    "print puts a space between values unless you set sep. What should go between them?")
           def other():
               n2, o2 = rerun("day = 13", "day = 5")
               return o2.strip()
           check_eq("prints 5/11/2026 when day is 5", other, "5/11/2026",
                    "Print the names day, month and year rather than typing the numbers.")
           """,
           'print(day, month, year, sep="...") with the right text instead of the dots.',
           'day = 13\nmonth = 11\nyear = 2026\nprint(day, month, year, sep="/")'),
    ],
    predict=[
        PRED("print(17 // 5, 17 % 5, 17 / 5)",
             "`//` gives the whole part (3 fives fit in 17), `%` the leftover (2), and `/` the exact answer as a float (3.4). `print` puts one space between the values.",
             traps={
                 "3, 2, 3.4": "The commas separate the values in the code; print shows one space between them, not commas.",
                 "3 2 3": "`/` is true division: it always gives a float, here 3.4.",
                 "4 2 3.4": "`//` rounds down, not to the nearest whole number: 3.4 becomes 3.",
             }, id="p0"),
        PRED("print(2 + 3 * 4 ** 2)",
             "`**` first (4 ** 2 is 16), then `*` (3 * 16 is 48), then `+` (50).",
             traps={
                 "400": "Python does not simply go left to right: `**` comes first, then `*`, then `+`.",
                 "146": "`**` applies only to the 4 next to it, not to `3 * 4`.",
                 "196": "`**` applies only to the 4 next to it, not to everything before it.",
             }, id="p1"),
        PRED("print(12 / 3, 12 // 3)",
             "`/` always gives a float, even for a whole answer: 4.0. `//` on two ints gives an int: 4.",
             traps={
                 "4 4": "`/` always gives a float, even when the answer is whole: 4.0.",
                 "4.0 4.0": "`//` on two ints gives an int; only `/` always makes a float.",
             }, id="p2"),
        PRED("print(-3 ** 2, (-3) ** 2)",
             "`**` is on a higher rung than the minus sign, so the first is -(3 ** 2) = -9. With brackets the base is -3, giving 9.",
             traps={
                 "9 9": "Without brackets the power happens first and the minus is applied after: -(3 ** 2).",
                 "-9 -9": "With brackets the base really is -3, and -3 times -3 is 9.",
             }, id="p3"),
        PRED('print(1, 2, sep="-")\nprint("a", end="|")\nprint("b")',
             "`sep` replaces the space between values, giving 1-2. `end` replaces the line break, so `b` continues on the same line after `a|`.",
             traps={
                 "1-2\na|\nb": "`end=\"|\"` replaces the line break, so the next print continues on the same line.",
                 "1 - 2\na|b": "`sep` replaces the single space completely; no extra spaces are added.",
                 "1-2\na b": "`end` is printed instead of the line break: here a `|`, with no space.",
             }, id="p-sep-end"),
        PRED("print(3 + 2.0, 6 / 3 * 2)",
             "A float anywhere in a sum makes the result a float: 5.0. `/` and `*` share a rung, so they run left to right: 6 / 3 is 2.0, times 2 is 4.0.",
             traps={
                 "5 4": "One float in the calculation makes the result a float, and `/` always gives a float.",
                 "5.0 1.0": "`/` and `*` share a rung and run left to right: first 6 / 3, then times 2.",
                 "5 4.0": "3 + 2.0 mixes an int and a float, and the result is a float: 5.0.",
             }, id="p-mixed"),
    ],
    cards=[
        CARD("What does the Python interpreter do with your program?", "It checks that the whole text is valid Python, then carries out the instructions one at a time, from top to bottom.", id="c0"),
        CARD("A line in a program contains only `6 * 7`. What is shown?", "Nothing. The expression is calculated and thrown away; only `print` shows a value.", id="c1"),
        CARD("What does `7 // 2` give?", "`3`: `//` divides and rounds down to a whole number.", id="c2"),
        CARD("What does `91 % 20` give?", "`11`: the remainder after taking out 4 whole twenties.", id="c-mod"),
        CARD("What does `-7 // 2` give?", "`-4`, not `-3`: `//` rounds down, toward the more negative number.", id="c-floor-neg"),
        CARD("What does `print(8 / 2)` show?", "`4.0`: `/` always gives a float, even when the answer is whole.", id="c3"),
        CARD("What does `print(2 + 3 * 4)` show?", "`14`: `*` is done before `+`.", id="c4"),
        CARD("Why is `-2 ** 2` equal to `-4`?", "`**` is done before the unary minus (a minus sign in front of a number), so it means `-(2 ** 2)`.", id="c5"),
        CARD("What does `print(2 ** 3 ** 2)` show?", "`512`: `**` works right to left, so it is `2 ** 9`.", id="c-pow-right"),
        CARD("Where do you look first in a Lime error message?", "The last line: it names the error type and says what went wrong. Then go to the line number it gives.", id="c6"),
        CARD("What does `print(2 + 3)  # print(9)` show?", "`5`: everything after `#` is a comment, so Python skips it.", id="c7"),
        CARD("What does `print(1, 2, 3)` show?", "`1 2 3`: print puts one space between values and does not show the commas.", id="c-print-several"),
        CARD("What does `print(1, 2, sep=\"-\")` show?", "`1-2`: `sep` sets what goes between the values.", id="c-sep"),
        CARD("What does `end=\" \"` change in `print(\"a\", end=\" \")`?", "It prints a space instead of the line break, so the next print continues on the same line.", id="c-end"),
        CARD("Line 5 of your program has a SyntaxError. Which lines run?", "None. Python checks the whole program before running any of it.", id="c-syntax"),
    ],
)
