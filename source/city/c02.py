from dsl import *

CITY = city(
    "py02",
    opener="Names are tags tied to objects. The values are the objects. Keep track of which tag is tied to which object.",
    scene="""
    Mrs Pell runs the fruit stall at the corner of Spring Lane. Her till died last winter, so she keeps every price in her head and writes receipts in a hand nobody can read. Her nephew typed the till's program back in from memory, and it crashes at once:

    ```
    apples = "12"
    pears = 7
    total = apples + pears
    print("Total fruit: " + total)
    ```

    "Can your machine write a receipt a person can read?" she asks.

    NIT: "Heads are not storage. Names are. The delivery note gives `apples` as text, in quotes, and text plus a number is a `TypeError`. Also, her handwriting is a syntax error." """,
    jobs=[
        JOB("story", "tickets", "Wren's ticket line",
            """
            Wren sells day tickets. Using the names given, print exactly:

            `Wren sold 12 tickets for 54.00 coins`

            Build the line with one f-string, and show the money with two decimal places. Keep the first three lines as they are: the checker changes them to test you.""",
            'driver = "Wren"\nriders = 12\nprice = 4.5\n',
            """
            check_eq("prints the exact line", lambda: out.strip(), "Wren sold 12 tickets for 54.00 coins",
                     "Two decimals: {value:.2f}. Check the spaces and the word order.")
            check("uses an f-string", lambda: has_node("JoinedStr"),
                  "Put an f straight before the opening quote, then the names inside {}.")
            def other():
                ns2, out2 = rerun("riders = 12", "riders = 3")
                return out2.strip()
            check_eq("works for 3 riders too", other, "Wren sold 3 tickets for 13.50 coins",
                     "Calculate riders * price inside the braces instead of typing 54.00.")
            def other_driver():
                ns2, out2 = rerun('driver = "Wren"', 'driver = "Ada"')
                return out2.strip()
            check_eq("works for another driver", other_driver, "Ada sold 12 tickets for 54.00 coins",
                     "Put {driver} in the text instead of typing Wren.")
            """,
            "Put expressions inside the braces: {riders * price:.2f}.",
            'driver = "Wren"\nriders = 12\nprice = 4.5\nprint(f"{driver} sold {riders} tickets for {riders * price:.2f} coins")'),
        JOB("repair", "pell_total", "Repair Mrs Pell's till",
            """
            This is the till program from the scene. The stall's stock arrives as text from the delivery note, so `apples` is the string `"12"`. The till should print `Total fruit: 19` but crashes with a `TypeError`. Repair it without changing the first line: the checker changes it to test you.""",
            'apples = "12"\npears = 7\ntotal = apples + pears\nprint("Total fruit: " + total)\n',
            """
            check_eq("prints Total fruit: 19", lambda: out.strip(), "Total fruit: 19",
                     "Two conversions are needed: text to number for the sum, number to text for the message (or use an f-string).")
            check_eq("total is the int 19", lambda: ns["total"], 19,
                     "Convert apples with int() before adding, so total is a number.")
            def other():
                n2, o2 = rerun('apples = "12"', 'apples = "30"')
                return o2.strip()
            check_eq('works when apples is "30"', other, "Total fruit: 37",
                     "The data arrives as text. Convert the name apples; do not type the number.")
            """,
            "int(apples) turns the text into a number. Then either str(total) or an f-string puts it back into the message.",
            'apples = "12"\npears = 7\ntotal = int(apples) + pears\nprint(f"Total fruit: {total}")', kind="fix"),
    ],
    read=[
        READ("r1", "Tags and objects",
             """
             a = 5
             b = a
             a = a + 1
             print(a, b)
             c = "5"
             print(c * 2, int(c) * 2)
             print(type(a / 1), type(a // 1))
             total = 0
             total += 4
             total *= 3
             print(total)
             """,
             "`b = a` ties `b` to the value 5. `a = a + 1` makes a new value 6 and moves only the `a` tag, so `b` still shows 5. `*` on a string repeats it (`55`); after `int` it multiplies (10). `/` gives a float even for whole answers; `//` on ints gives an int, and `type()` prints as `<class '...'>`. `+=` and `*=` update: 0 + 4 is 4, times 3 is 12."),
    ],
    parsons=[
        PARSONS("p1", "Swap the gear tags",
                "Order the lines so the two names swap their values through a spare name, then print `copper brass`. One decoy line only pretends to swap: it prints the names in the other order and changes nothing. Leave it out.",
                ['left = "brass"', 'right = "copper"', "spare = left", "left = right", "right = spare", "print(left, right)"],
                """
                check("prints copper brass", lambda: out.strip() == "copper brass", "Save one value in spare before you overwrite it, and print only once, at the end.")
                check("the names really swapped", lambda: ns.get("left") == "copper" and ns.get("right") == "brass", "Printing in another order does not move any tags; assignment does.")
                """,
                distractors=["print(right, left)"]),
    ],
    teach=TEACH(
        "Why does `b = a` followed by `a = a + 1` leave `b` unchanged? Explain it with tags tied to objects.",
        "A name is a tag tied to a value. `b = a` ties a second tag to the same value, 5. `a = a + 1` calculates a new value, 6, and moves the `a` tag onto it. Nothing changed the 5, and the `b` tag is still tied to it. Numbers and strings can never be changed in place (they are immutable), so the only way to 'change' them is to move a tag to a new value.",
        points=[
            "a name is a tag tied to a value, not a box",
            "`b = a` ties `b` to the same value, 5",
            "`a + 1` makes a new value; `=` moves only the `a` tag",
            "ints and strings are immutable, so the 5 itself never changes",
        ]),
    terms=[
        TERM("name (variable)", "A tag that refers to a value. Assignment ties it to the value.", "`price = 4.5`", "Thinking `b = a` links the two names forever.", card=False, id="t0"),
        TERM("assignment", "The `=` statement: work out the right side, then tie the name on the left to the result.", "`total = total + 4`", "Reading `=` as 'equals' in the maths sense. It means 'now refers to'.", q="`total = total + 4` would be false in maths. What does it mean in Python?", id="t1"),
        TERM("type", "The kind of value, which decides what operations make sense. `type(x)` tells you.", "`type(3.0)` prints as `<class 'float'>`.", "Thinking `3` and `3.0` are the same type; one is an int, the other a float.", card=False, id="t2"),
        TERM("str", "The text type: a sequence of characters in quotes.", '`"brass"`, `\'12\'`', 'Adding `"12" + 7`: text and numbers do not mix without conversion.', q="Is `\"12\"` a number or text, and what is its type called?", id="t3"),
        TERM("bool", "The type with exactly two values, `True` and `False`.", "`0.1 + 0.2 == 0.3` gives the bool `False`.", "Writing `true` in lower case: it must be `True`.", q="What are the only two values of type bool, spelled exactly?", id="t4"),
        TERM("f-string", "A string starting with `f` where expressions in `{}` are calculated and inserted, optionally with a format after a colon.", '`f"{price:.2f}"` gives `"4.50"`.', "Forgetting the `f`, so the braces print literally.", q="What is an f-string, and what does `f\"{price:.2f}\"` give when price is 4.5?", id="t5"),
        TERM("type conversion", "Making a value of one type from another: `int()`, `float()`, `str()`, `bool()`. `int()` only accepts text of a whole number: `int(\"4.5\")` is a ValueError, so use `float()` for decimals.", '`int("12")` is 12.', '`int("4.5")` fails with a ValueError; use `float` first.', q="What happens with `int(\"4.5\")`?", id="t6"),
        TERM("floating-point error", "Floats are stored in binary, so most decimals are approximations.", "`0.1 + 0.2` is `0.30000000000000004`.", "Comparing floats with `==`; use `math.isclose` or a small tolerance instead.", card=False, id="t7"),
        TERM("augmented assignment", "Shorthand that updates a name: `x += 1` means `x = x + 1`.", "`total = 4`, then `total *= 3` makes total 12.", "Writing `x =+ 1`, which just sets x to +1.", q="`total = 4`, then `total *= 3`. What is total?", id="t8"),
        TERM("immutable", "Cannot be changed in place. Ints, floats and strings are immutable: operations make new values.", "`a = a + 1` makes a new int and moves the tag `a` to it.", "Thinking `a + 1` changes the old value for every name tied to it.", q="What does it mean that an int is immutable?", id="t-immutable"),
    ],
    nit_right=[
        "Correct. `=` moved a tag; the old value did not change, because ints are immutable.",
        "Accepted. `int()` turned the text into a number. `input()` would have handed you text too.",
        "Right. `round(2.5)` is 2: exact halves go to the even neighbour.",
    ],
)
