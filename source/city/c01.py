from dsl import *

CITY = city(
    "py01",
    opener="The tram fare box has forgotten arithmetic. You have not. Lend it yours.",
    scene="""
    Wren drives the Number 1 tram round the Workshop Quarter. This morning the fare box added every coin twice, then stopped altogether. Wren hands you the box's last program and a cup of oil.

    "It used to just work," Wren says.

    NIT clicks from its pigeonholes: "Everything used to just work. That is how you know someone wrote it." """,
    jobs=[
        JOB("story", "fares", "Count the fare box",
            """
            Thirteen passengers each paid 7 coins today. Coins go into bags of 20. Print three lines: the total number of coins, the number of full bags, and the loose coins left over. Work each one out with an expression, not by hand.""",
            "# 13 passengers, 7 coins each, bags of 20\n",
            """
            check("prints 91, 4 and 11 on three lines", lambda: out.split() == ["91", "4", "11"], "Total first, then full bags, then the leftover.")
            check("calculates instead of typing answers", lambda: "13 * 7" in code.replace("13*7", "13 * 7"), "Write 13 * 7 so your working shows.")
            check("uses // and %", lambda: "//" in code and "%" in code, "Full bags is floor division; leftover is the remainder.")
            """,
            "Full bags: 13 * 7 // 20. Leftover: 13 * 7 % 20. Precedence works left to right for * // and %, so no brackets are needed.",
            "print(13 * 7)\nprint(13 * 7 // 20)\nprint(13 * 7 % 20)"),
        JOB("repair", "midnight", "Repair the tower clock",
            """
            The tower clock turns minutes since midnight into hours and minutes. For 1000 minutes it should print `16` then `40`, but the hours come out as `16.666666666666668`. Repair it.""",
            "print(1000 / 60)\nprint(1000 % 60)\n",
            """
            check("prints 16 then 40", lambda: out.split() == ["16", "40"], "Hours must be a whole number.")
            check("still calculates from 1000", lambda: "1000" in code and "16" not in code, "Fix the operator rather than typing the answer.")
            """,
            "One operator is wrong. Which division drops the fraction?",
            "print(1000 // 60)\nprint(1000 % 60)", kind="fix"),
    ],
    read=[
        READ("r1", "The fare box's last program",
             """
             print(13 * 7 // 20 * 20)
             print(13 * 7 - 13 * 7 // 20 * 20)
             print(2 + 2 * 2 ** 2)
             print(7 / 7, 7 // 7)
             """,
             "`*`, `//` and `%` share one level and run left to right: 91 // 20 is 4, times 20 is 80. Then 91 - 80 is 11, which is exactly `91 % 20`. `**` binds tightest: 2 ** 2 is 4, times 2 is 8, plus 2 is 10. `/` always gives a float (1.0); `//` on two ints gives an int (1)."),
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
        "`/` divides exactly and always gives a float: 91 / 20 is 4.55. `//` divides and rounds down to a whole number: 91 // 20 is 4 full bags. `%` gives what is left after taking out the whole bags: 91 % 20 is 11 loose coins. They always fit together: 4 * 20 + 11 is 91 again."),
    terms=[
        TERM("interpreter", "The program that reads your Python code and carries out its statements one at a time, from top to bottom.", "Lime runs a Python interpreter inside the page.", "Thinking the computer understands what you meant. It only does what the text says."),
        TERM("expression", "Code that produces a value.", "`6 * 7` is an expression with the value 42.", "Writing an expression alone on a line in a script and expecting it to be shown. Only `print` shows it."),
        TERM("statement", "A complete instruction that Python carries out.", "`print(6 * 7)` is a statement.", ""),
        TERM("operator precedence", "The rules that decide which part of an expression is calculated first: `**`, then `*` `/` `//` `%`, then `+` `-`. Brackets override everything.", "`2 + 3 * 4` is 14, not 20.", "Forgetting that `-3 ** 2` is -9, because `**` binds tighter than the minus sign."),
        TERM("floor division (//)", "Division that rounds down toward negative infinity.", "`7 // 2` is 3 and `-7 // 2` is -4.", "Expecting `-7 // 2` to be -3."),
        TERM("modulo (%)", "The remainder after floor division. It always matches `//`: `a == (a // b) * b + a % b`.", "`91 % 20` is 11.", ""),
        TERM("int", "A whole number type with no size limit in Python.", "`42`, `-7`, `10 ** 30`.", ""),
        TERM("float", "A number with a decimal point, stored approximately in binary.", "`3.5`, `8 / 2` (which is `4.0`).", "Expecting `/` to give an int when the answer is whole."),
        TERM("comment", "Text after `#` that Python ignores. Written for humans.", "`# bags of 20 coins`", ""),
        TERM("traceback", "The error report Python prints when something goes wrong. Read it from the bottom: the last line names the error, the lines above show where.", "`ZeroDivisionError: division by zero`", "Reading only the top line."),
    ],
)
