from dsl import *

CITY = city(
    "py01",
    opener="The tram fare box counts every coin twice. You can count once. Lend it your arithmetic.",
    scene="""
    Wren drives the Number 1 tram round the Workshop Quarter. This morning 13 passengers each paid 7 coins, and the fare box reported 182 coins, 9 full bags of 20 and 2 loose coins. Wren counted the bags by hand: there are 4, and 11 loose coins. Wren hands you the box's program and a cup of oil.

    ```
    # the fare box's program
    print(13 * 7 * 2)
    print(13 * 7 * 2 // 20)
    print(13 * 7 * 2 % 20)
    ```

    "It used to just work," Wren says.

    NIT clicks from its pigeonholes: "Everything used to just work. That is how you know someone wrote it. Note the `* 2`: the program does exactly what it says, and it says count twice." Your first job below is to write the fare box a correct program.""",
    jobs=[
        JOB("story", "fares", "Count the fare box",
            """
            Write the fare box's program again, counting each coin once. Using the names `passengers`, `fare` and `bag`, print three lines: the total number of coins, the number of full bags, and the loose coins left over. For today that is `91`, `4` and `11`. The checker also tries other days, so calculate from the names.""",
            "passengers = 13\nfare = 7\nbag = 20\n# print total, full bags, loose coins\n",
            """
            check_eq("prints 91, 4 and 11 on three lines", lambda: out.strip().split("\\n"), ["91", "4", "11"],
                     "Three print calls: total coins first, then full bags, then the leftover.")
            def fewer():
                n2, o2 = rerun("passengers = 13", "passengers = 9")
                return o2.strip().split("\\n")
            check_eq("works for 9 passengers (63, 3, 3)", fewer, ["63", "3", "3"],
                     "Build every line from the names (passengers * fare ...) instead of typing numbers.")
            def bigger_bags():
                n2, o2 = rerun("bag = 20", "bag = 25")
                return o2.strip().split("\\n")
            check_eq("works for bags of 25 (91, 3, 16)", bigger_bags, ["91", "3", "16"],
                     "Full bags is the total // bag; the leftover is the total % bag.")
            """,
            "Total: passengers * fare. Full bags: passengers * fare // bag. Leftover: passengers * fare % bag. `*`, `//` and `%` share a rung and run left to right, so no brackets are needed.",
            "passengers = 13\nfare = 7\nbag = 20\nprint(passengers * fare)\nprint(passengers * fare // bag)\nprint(passengers * fare % bag)"),
        JOB("repair", "midnight", "Repair the tower clock",
            """
            The tower clock turns minutes since midnight into hours and minutes. For 1000 minutes it should print `16` then `40`, but the hours come out as `16.666666666666668`. Repair it. The checker also tries other times.""",
            "minutes = 1000\nprint(minutes / 60)\nprint(minutes % 60)\n",
            """
            check_eq("prints 16 then 40", lambda: out.strip().split("\\n"), ["16", "40"],
                     "Hours must be a whole number. Which division drops the fraction?")
            def other():
                n2, o2 = rerun("minutes = 1000", "minutes = 61")
                return o2.strip().split("\\n")
            check_eq("prints 1 then 1 for 61 minutes", other, ["1", "1"],
                     "Fix the operator and keep calculating from minutes rather than typing the answer.")
            """,
            "One operator is wrong. Which division drops the fraction?",
            "minutes = 1000\nprint(minutes // 60)\nprint(minutes % 60)", kind="fix"),
    ],
    read=[
        READ("r1", "The fare box's spare program",
             """
             print(13 * 7 // 20 * 20)
             print(13 * 7 - 13 * 7 // 20 * 20)
             print(2 + 2 * 2 ** 2)
             print(7 / 7, 7 // 7)
             """,
             "`*`, `//` and `%` share one rung and run left to right: 91 // 20 is 4, times 20 is 80. Then 91 - 80 is 11, which is exactly `91 % 20`. `**` is done first: 2 ** 2 is 4, times 2 is 8, plus 2 is 10. `/` always gives a float (1.0); `//` on two ints gives an int (1), and `print` puts one space between them."),
    ],
    parsons=[
        PARSONS("p1", "Furnace readings",
                "Put the lines in order so the program prints a heading, then the average of the three furnace readings 12, 15 and 18 (`15.0`), then the average rounded down (`15`). One line is a decoy that gets the precedence wrong: leave it out.",
                ['print("Furnace average")', "print((12 + 15 + 18) / 3)", "print((12 + 15 + 18) // 3)"],
                """
                check("prints the heading, 15.0 and 15 in order", lambda: out.strip().split("\\n") == ["Furnace average", "15.0", "15"], "Heading first, then the true division, then the floor division.")
                """,
                distractors=["print(12 + 15 + 18 / 3)"]),
    ],
    teach=TEACH(
        "Explain to Wren, who has never programmed, the difference between `/`, `//` and `%`. Use the fare box (91 coins, bags of 20) as your example.",
        "`/` divides exactly and always gives a float: 91 / 20 is 4.55. `//` divides and rounds down to a whole number: 91 // 20 is 4 full bags. `%` gives what is left after taking out the whole bags: 91 % 20 is 11 loose coins. They always fit together: 4 * 20 + 11 is 91 again.",
        points=[
            "`/` gives the exact answer as a float (4.55)",
            "`//` gives the whole number of bags, rounded down (4)",
            "`%` gives the leftover coins (11)",
            "bags times 20 plus the leftover is the total again",
        ]),
    terms=[
        TERM("interpreter", "The program that reads your Python code, checks it, and carries out its statements one at a time, from top to bottom.", "Lime runs a Python interpreter inside the page.", "Thinking the computer understands what you meant. It only does what the text says.", card=False, id="t0"),
        TERM("expression", "Code that produces a value.", "`6 * 7` is an expression with the value 42.", "Writing an expression alone on a line and expecting it to be shown. Only `print` shows it.", card=False, id="t1"),
        TERM("statement", "A complete instruction that Python carries out.", "`print(6 * 7)` is a statement; `6 * 7` inside it is an expression.", "", q="What is a statement in Python, and what is an example?", id="t2"),
        TERM("operator precedence", "The order in which Python works out an expression: brackets, then `**`, then unary minus (`-x`), then `*` `/` `//` `%`, then `+` `-`. Lesson 3 adds comparisons, then `not`, `and`, `or`.", "`2 + 3 * 4` is 14, not 20.", "Forgetting that `-3 ** 2` is -9, because `**` is done before the minus sign.", card=False, id="t3"),
        TERM("floor division (//)", "Division that rounds down to a whole number (toward the more negative side).", "`7 // 2` is 3 and `-7 // 2` is -4.", "Expecting `-7 // 2` to be -3.", card=False, id="t4"),
        TERM("modulo (%)", "The remainder after floor division: what is left over once the whole groups are taken out.", "`91 % 20` is 11: 4 bags of 20 make 80, and 11 coins are left.", "Using `/` and expecting the leftover: `91 / 20` is 4.55, not 11.", card=False, id="t5"),
        TERM("int", "The whole-number type. A Python int has no size limit.", "`42`, `-7`, `2 ** 100`.", "Writing `3.0` and expecting an int; the decimal point makes it a float.", q="Is there a largest number a Python int can hold?", id="t6"),
        TERM("float", "A number with a decimal point, stored approximately in binary.", "`3.5`, and `8 / 2` (which is `4.0`).", "Expecting `/` to give an int when the answer is whole.", q="What is a float, and what is `8 / 2`?", id="t7"),
        TERM("comment", "Text after `#` that Python skips. Written for humans.", "`# bags of 20 coins`", "Writing a comment that only repeats the code instead of saying why.", card=False, id="t8"),
        TERM("traceback", "Python's report when an error stops a program. Lime shows a short traceback: the line number in your code, with the error type and message on the last line.", "`ZeroDivisionError: division by zero` on line 2.", "Reading only the top of the report. The last line names the error.", card=False, id="t9"),
        TERM("function call", "Running a named piece of code (a function) by writing its name followed by brackets. Values for it go inside the brackets.", "`print(\"hi\")` calls the function `print` with the value `\"hi\"`.", "Leaving out the brackets: `print \"hi\"` is a SyntaxError.", q="What does it mean to call a function, and how do you write it?", id="t-call"),
        TERM("string", "Text inside quotes. Python shows it exactly as written, without the quotes.", "`\"Hello, Lime!\"`", "Leaving out the quotes: `print(Hello)` makes Python look for a name called Hello (a NameError).", q="What happens if you write `print(Hello)` without quotes?", id="t-string"),
    ],
    nit_right=[
        "Correct. `print` put exactly one space between your values; the commas stayed in the code.",
        "Accepted. `//` rounded down and `%` kept the rest. Together they lose nothing.",
        "Right. `/` gave a float even though the answer was whole. It always will.",
    ],
)
