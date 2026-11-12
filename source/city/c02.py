from dsl import *

CITY = city(
    "py02",
    opener="Names are labels tied to drawers. The values live in the drawers. Keep track of which label is on which drawer.",
    scene="""
    Mrs Pell runs the fruit stall at the corner of Spring Lane. Her till died last winter, so she keeps every price in her head and writes receipts in a hand nobody can read.

    "Can your machine write a receipt a person can read?" she asks.

    NIT: "Heads are not storage. Names are. Also, her handwriting is a syntax error." """,
    jobs=[
        JOB("story", "tickets", "Wren's ticket line",
            """
            Wren sells day tickets. Using the names given, print exactly:

            `Wren sold 12 tickets for 54.00 coins`

            Build the line with one f-string, and show the money with two decimal places. Keep the first three lines as they are: the checker changes them to test you.""",
            'driver = "Wren"\nriders = 12\nprice = 4.5\n',
            """
            check("prints the exact line", lambda: out.strip() == "Wren sold 12 tickets for 54.00 coins", "Two decimals: {value:.2f}.")
            check("uses an f-string", lambda: 'f"' in code or "f'" in code)
            def other():
                ns2, out2 = rerun("riders = 12", "riders = 3")
                return out2.strip() == "Wren sold 3 tickets for 13.50 coins"
            check("works for 3 riders too", other, "Calculate riders * price inside the braces instead of typing 54.00.")
            """,
            "Put expressions inside the braces: {riders * price:.2f}.",
            'driver = "Wren"\nriders = 12\nprice = 4.5\nprint(f"{driver} sold {riders} tickets for {riders * price:.2f} coins")'),
        JOB("repair", "pell_total", "Repair Mrs Pell's till",
            """
            The stall's stock arrives as text from the delivery note, so `apples` is the string `"12"`. The till should print `Total fruit: 19` but crashes with a `TypeError`. Repair it without changing the first line.""",
            'apples = "12"\npears = 7\ntotal = apples + pears\nprint("Total fruit: " + total)\n',
            """
            check("prints Total fruit: 19", lambda: out.strip() == "Total fruit: 19", "Two conversions are needed: text to number for the sum, number to text for the message (or use an f-string).")
            check('keeps apples = "12"', lambda: 'apples = "12"' in code, "The data arrives as text. Convert it; don't retype it.")
            """,
            "int(apples) turns the text into a number. Then either str(total) or an f-string puts it back into the message.",
            'apples = "12"\npears = 7\ntotal = int(apples) + pears\nprint(f"Total fruit: {total}")', kind="fix"),
    ],
    read=[
        READ("r1", "Labels and drawers",
             """
             a = 5
             b = a
             a = a + 1
             print(a, b)
             c = "5"
             print(c * 2, int(c) * 2)
             print(type(a / 1).__name__, type(a // 1).__name__)
             total = 0
             total += 4
             total *= 3
             print(total)
             """,
             "`b = a` ties `b` to the value 5. `a = a + 1` makes a new value 6 and moves only the label `a`, so `b` still shows 5. `*` on a string repeats it (`55`); after `int` it multiplies (10). `/` gives a float even for whole answers; `//` on ints gives an int. `+=` and `*=` update: 0 + 4 is 4, times 3 is 12."),
    ],
    parsons=[
        PARSONS("p1", "Swap the gear labels",
                "Order the lines so the two names swap their values through a spare name, then print `copper brass`. One decoy line would overwrite a value before it is saved.",
                ['left = "brass"', 'right = "copper"', "spare = left", "left = right", "right = spare", "print(left, right)"],
                """
                check("prints copper brass", lambda: out.strip() == "copper brass", "Save one value in spare before you overwrite it.")
                """,
                distractors=["right = left"]),
    ],
    teach=TEACH(
        "Why does `b = a` followed by `a = a + 1` leave `b` unchanged? Explain it with labels and drawers.",
        "A name is a label attached to a value. `b = a` attaches a second label to the same value, 5. `a = a + 1` calculates a new value, 6, and moves the `a` label onto it. Nothing changed the 5, and the `b` label is still on it. Numbers and strings can never be changed in place, so the only way to 'change' them is to move a label to a new value."),
    terms=[
        TERM("name (variable)", "A label that refers to a value. Assignment attaches it.", "`price = 4.5`", "Thinking `b = a` links the two names forever."),
        TERM("assignment", "The `=` statement: work out the right side, then attach the name on the left to the result.", "`total = total + 4`", "Reading `=` as 'equals' in the maths sense. It means 'now refers to'."),
        TERM("type", "The kind of value, which decides what operations make sense. `type(x)` tells you.", "`type(3.0)` is `float`.", ""),
        TERM("str", "The text type: a sequence of characters in quotes.", '`"brass"`, `\'12\'`', 'Adding `"12" + 7`: text and numbers do not mix without conversion.'),
        TERM("bool", "The type with exactly two values, `True` and `False`.", "`5 > 3` is `True`.", ""),
        TERM("f-string", "A string starting with `f` where expressions in `{}` are calculated and inserted, optionally with a format after a colon.", '`f"{price:.2f}"` gives `"4.50"`.', "Forgetting the `f`, so the braces print literally."),
        TERM("type conversion", "Making a value of one type from another: `int()`, `float()`, `str()`, `bool()`.", '`int("12")` is 12.', '`int("4.5")` fails; use `float` first.'),
        TERM("floating-point error", "Floats are stored in binary, so most decimals are approximations.", "`0.1 + 0.2` is `0.30000000000000004`.", "Comparing floats with `==`; compare the difference to a small tolerance instead."),
        TERM("augmented assignment", "Shorthand that updates a name: `x += 1` means `x = x + 1`.", "`total *= 3`", ""),
    ],
)
