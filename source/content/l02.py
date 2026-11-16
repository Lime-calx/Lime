from dsl import *

LESSON = lesson(
    id="py02", track="py", n=2, title="Names, types and objects", minutes=45,
    summary="Variables as labels on objects, the core types, conversion, rounding, f-strings and why floats are approximate.",
    goals=[
        "Explain what the = sign really does: it ties a name to a value",
        "Recognise int, float, str, bool and None, and convert between them",
        "Round and cut off numbers on purpose, not by accident",
        "Build readable text from values with f-strings",
        "Compare decimal numbers safely and store money exactly",
    ],
    blocks=[
        H("Names point at values"),
        P("""
        A **variable** is a name tied to a value. `price = 12` creates the value `12` and ties the name `price` to it. The `=` sign is **assignment**, not a claim of equality: it means "from now on, this name refers to that value"."""),
        CODE("""
        price = 12
        print(price)
        price = 15
        print(price)
        """),
        NOTE("model", """
        Think of names as tags tied to objects, like luggage tags on crates, not as boxes that hold values. Two tags can be tied to the same object, and moving a tag never changes the object. For numbers this is invisible. For lists in lesson 6 it becomes critical."""),
        CODE("""
        x = 5
        y = x
        x = 7
        print(x, y)
        """),
        P("""
        `y = x` tied a second tag to the value 5. Then `x = 7` moved only the `x` tag to a new value, so `y` still points at 5.

        Ints, floats and strings are **immutable**: they can never be changed in place. An operation such as `x + 1` always makes a new value, and assignment then moves a tag onto it."""),

        H("Naming rules and habits"),
        P("""
        Names may contain letters, digits and underscores, cannot start with a digit, and cannot be a reserved word such as `if` or `for`. Case matters: `Score` and `score` are different names.

        Python convention is `snake_case` for variables and functions. Choose names that say what the value *means*: `seconds_per_day` beats `x`, and a month from now you will thank yourself."""),
        NOTE("trap", """
        Do not reuse the names of Python's own functions. After `print = 5`, the name `print` is tied to 5 and `print("hi")` fails with a `TypeError`. The same goes for `type`, `int`, `str`, `round` and `sum`."""),

        H("The core types"),
        P("""
        Every value has a **type** that decides what you can do with it. The function `type(value)` tells you which. It prints as `<class '...'>` with the type's name inside the quotes."""),
        CODE("""
        print(type(42))
        print(type(3.14))
        print(type("text"))
        print(type(True))
        print(type(None))
        """),
        P("""
        - `int`: whole numbers of unlimited size
        - `float`: decimal numbers with about 15 to 17 significant digits
        - `str`: text, in single or double quotes
        - `bool`: `True` or `False` (yes/no answers)
        - `NoneType`: the single value `None`, meaning "no value here\""""),
        NOTE("deep", """
        `bool` is a kind of int underneath: `True` behaves as 1 and `False` as 0, so `True + True` is 2. That is handy later for counting how many conditions were true."""),

        H("Operators depend on type"),
        CODE("""
        print(2 + 3)
        print("2" + "3")
        print("ab" * 3)
        print(3 + 2.0, type(3 + 2.0))
        """),
        P("""
        The same `+` adds numbers and joins strings. Some mixes of types are defined: an int and a float give a float, and a string times an int repeats the string. Other mixes are not defined and raise a `TypeError`."""),
        NOTE("trap", """
        `"5" + 5` is a `TypeError`: Python will not guess whether you want `10` or `"55"`. Convert explicitly with `int()`, `float()` or `str()`."""),
        CODE("""
        age_text = "17"
        age = int(age_text)
        print(age + 1)
        print(str(age) + " years")
        print(float("2.5") * 2)
        """),
        P("""
        `int("abc")` raises a `ValueError`: the type is right (a string) but this particular value cannot be converted. `int("4.5")` fails the same way; use `float("4.5")` for text with a decimal point."""),
        NOTE("tip", """
        In ordinary Python, `input("Age? ")` waits for the user to type something and always gives back a **string**, even if they typed digits. That is why conversion matters so much. Lime has no typing prompt, so exercises put the text in a variable instead, like `age_text = "17"` above."""),

        H("Rounding and cutting off"),
        P("""
        `round(x)` gives the nearest whole number and `round(x, 2)` keeps 2 decimal places. `int(x)` does not round: it cuts off the fraction, toward zero. `//` rounds down instead, which differs for negative numbers."""),
        CODE("""
        print(round(3.7), round(3.14159, 2))
        print(int(3.9), int(-3.9))
        print(-3.9 // 1)
        print(round(2.5), round(3.5))
        """),
        NOTE("trap", """
        `round()` sends an exact half to the nearest **even** number: `round(2.5)` is 2 and `round(3.5)` is 4. This is called banker's rounding; it avoids pushing totals upward. If a protocol says "round halves up", do not rely on `round()` alone."""),
        NOTE("deep", """
        `round(2.675, 2)` gives `2.67`, not `2.68`, because 2.675 is stored as 2.67499999... in binary. `import math` loads Python's maths toolbox, then `math.floor(x)` always rounds down and `math.ceil(x)` always rounds up: `math.ceil(3.1)` is 4."""),

        H("f-strings: building text from values"),
        P("""
        An **f-string** puts values straight into text. Write `f"..."` and put expressions inside `{}`. After a colon you can add a **format specifier** that controls how the value looks."""),
        CODE("""
        item = "notebook"
        price = 3.5
        qty = 4
        print(f"{qty} x {item} = {qty * price}")
        """),
        P("""
        The expression inside `{}` is worked out like any other, so `{qty * price}` works. Four specifiers cover most needs:

        - `:.2f`: two decimal places (`14.00`)
        - `:>8`: right-align in 8 characters
        - `:,`: thousands separators (`1,234,567`)
        - `:02d`: pad a whole number with zeros to width 2 (`07`)"""),
        CODE("""
        print(f"{14:.2f}")
        print(f"{1234567:,}")
        print(f"{'ab':>8}|")
        print(f"{7:02d}")
        """),
        NOTE("trap", """
        `:02d` only works on an int. `f"{7.0:02d}"` raises a `ValueError`, so convert with `int()` first or use `:02.0f`."""),

        H("Floating-point numbers are approximations"),
        P("""
        `==` asks "are these equal?" and gives `True` or `False`; `<` asks "is the left one smaller?". Lesson 3 covers comparisons fully. `abs(x)` gives the size of a number without its sign: `abs(-0.5)` is `0.5`."""),
        CODE("""
        print(0.1 + 0.2)
        print(0.1 + 0.2 == 0.3)
        print(abs((0.1 + 0.2) - 0.3) < 1e-9)
        """),
        P("""
        Computers store floats in binary. Just as 1/3 has no exact decimal form, 0.1 has no exact binary form, so tiny errors appear. `1e-9` is a float written in scientific notation: 0.000000001.

        The practical rule: use `==` on floats only when you know the values are exact (`0.5 + 0.25 == 0.75` is safe because halves and quarters are exact in binary). Otherwise check whether the two numbers are *close*. For display, use `round()` or a format specifier."""),
        CODE("""
        import math
        a = 0.1 + 0.2
        print(math.isclose(a, 0.3))
        print(math.isclose(1e16, 1e16 + 2))
        """),
        P("""
        `import math` loads Python's maths toolbox, and `math.isclose(a, b)` means the `isclose` function inside it. It allows a difference *relative to the size* of the numbers, so it works for tiny and huge values alike. A fixed tolerance such as `abs(a - b) < 1e-9` is fine for everyday sizes, but it says False for huge neighbours like `1e16` and `1e16 + 2`."""),
        NOTE("tip", """
        Whole numbers as ints are exact. That is why one safe way to store money is integer cents (`1999`), formatted as `19.99` only when shown. Python's `decimal` module is the other standard choice."""),

        H("Updating values"),
        CODE("""
        count = 0
        count = count + 1
        count += 1
        count *= 5
        print(count)
        """),
        P("""
        `count += 1` is shorthand for `count = count + 1`, and the same pattern works for `-=`, `*=`, `/=`, `//=`, `%=` and `**=`. You can also assign several names at once, which gives a swap without a spare variable:"""),
        CODE("""
        a, b = 3, 9
        a, b = b, a
        print(a, b)
        """),
        P("""
        The right side is worked out completely first, producing the pair `9, 3`, and only then are the names tied to the values. That is why the swap works."""),
    ],
    exercises=[
        EX("swap", "Swap two names",
           "Swap the values of `a` and `b` so that afterwards `a` is 9 and `b` is 3. Do not retype the numbers: the checker tries other values.",
           "a = 3\nb = 9\n# swap the values below\n",
           """
           check_eq("a is 9 and b is 3", lambda: (ns["a"], ns["b"]), (9, 3),
                    "After your code a should hold the old b, and b the old a.")
           def other_a():
               n2, _ = rerun("a = 3", "a = 100")
               return (n2["a"], n2["b"])
           check_eq("works when a starts as 100", other_a, (9, 100), "Do not type 9 or 3 in your own code.")
           def other_b():
               n2, _ = rerun("a = 3\\nb = 9", "a = 3\\nb = 42")
               return (n2["a"], n2["b"])
           check_eq("works when b starts as 42", other_b, (42, 3),
                    "Both new values must come from the old names: a, b = b, a.")
           """,
           "Assign both at once: a, b = b, a",
           "a = 3\nb = 9\na, b = b, a"),
        EX("receipt", "Build a receipt line",
           """
           Using an f-string, print `4 x notebook = 14.00` built from the three variables. The total must show two decimal places.""",
           'item = "notebook"\nprice = 3.5\nqty = 4\n# print the receipt line below\n',
           """
           check_eq("prints the receipt line", lambda: out.strip(), "4 x notebook = 14.00",
                    "Format: quantity, ' x ', item, ' = ', total with 2 decimals.")
           def other():
               n2, o2 = rerun("qty = 4", "qty = 3")
               return o2.strip()
           check_eq("works for 3 notebooks", other, "3 x notebook = 10.50",
                    "Compute the total from the variables instead of typing it.")
           def other_price():
               n2, o2 = rerun("price = 3.5", "price = 2.25")
               return o2.strip()
           check_eq("works for another price", other_price, "4 x notebook = 9.00",
                    "Multiply qty by price inside the braces.")
           """,
           "Inside the braces, `qty * price:.2f` multiplies and formats in one step.",
           'item = "notebook"\nprice = 3.5\nqty = 4\nprint(f"{qty} x {item} = {qty * price:.2f}")'),
        EX("types", "Fix the type error",
           """
           This code raises a `TypeError`. Fix it so `next_year` is the integer 18 and the program prints `18`.""",
           'age = "17"\nnext_year = age + 1\nprint(next_year)\n',
           """
           check_eq("prints 18", lambda: out.strip(), "18", "age is a string. Convert it before adding.")
           check_eq("next_year is the int 18", lambda: ns["next_year"], 18, "Use int() on the string, not str() on the result.")
           def other():
               n2, _ = rerun('age = "17"', 'age = "40"')
               return n2["next_year"]
           check_eq("works for another age", other, 41, "Convert the variable, not the number 17.")
           """,
           "Wrap the string in int() before adding 1.",
           'age = "17"\nnext_year = int(age) + 1\nprint(next_year)', kind="fix"),
        EX("close", "Compare floats safely",
           """
           Set `close` to `True` when `a` and `b` are equal apart from tiny float errors, and `False` otherwise. Use `math.isclose` or a tolerance of `1e-9`. The checker tries several pairs.""",
           "a = 0.1 + 0.2\nb = 0.3\n# set close below\nclose = None\n",
           """
           check_eq("close is True for 0.1 + 0.2 and 0.3", lambda: ns["close"], True,
                    "Check that the distance between a and b is tiny, not that they are exactly equal.")
           def far_b():
               n2, _ = rerun("b = 0.3", "b = 0.4")
               return n2["close"]
           check_eq("False when b is 0.4", far_b, False, "abs(a - b) is the distance between the two numbers.")
           def far_a():
               n2, _ = rerun("a = 0.1 + 0.2", "a = 0.7")
               return n2["close"]
           check_eq("False when a is 0.7", far_a, False, "Compare a with b; do not test b on its own.")
           def near():
               n2, _ = rerun("a = 0.1 + 0.2", "a = 0.3001")
               return n2["close"]
           check_eq("False for 0.3001 and 0.3", near, False,
                    "Rounding both to 2 places is too loose: use a tolerance of 1e-9 or math.isclose.")
           def other_pair():
               n2, _ = rerun("b = 0.3", "a = 1.1 * 3\\nb = 3.3")
               return n2["close"]
           check_eq("True for 1.1 * 3 and 3.3", other_pair, True,
                    "1.1 * 3 is 3.3000000000000003: close, but not equal.")
           """,
           "abs(a - b) < 1e-9, or import math and use math.isclose(a, b)",
           "a = 0.1 + 0.2\nb = 0.3\nclose = abs(a - b) < 1e-9"),
        EX("clocktime", "Format a clock time",
           """
           `total_minutes` holds minutes since midnight. Print them as a clock time `HH:MM`, with both parts padded to two digits, so 785 prints `13:05`.""",
           "total_minutes = 785\n# print the clock time below\n",
           """
           check_eq("prints 13:05", lambda: out.strip(), "13:05", "785 minutes is 13 hours and 5 minutes.")
           def other():
               n2, o2 = rerun("total_minutes = 785", "total_minutes = 61")
               return o2.strip()
           check_eq("pads with zeros (61 gives 01:01)", other, "01:01", "Use the :02d format specifier.")
           def late():
               n2, o2 = rerun("total_minutes = 785", "total_minutes = 1439")
               return o2.strip()
           check_eq("1439 gives 23:59", late, "23:59", "Hours are total_minutes // 60, minutes are total_minutes % 60.")
           """,
           "Use // and % for the parts and :02d inside the f-string braces.",
           'total_minutes = 785\nhours = total_minutes // 60\nminutes = total_minutes % 60\nprint(f"{hours:02d}:{minutes:02d}")'),
        EX("dose", "Round a dose, count whole tablets",
           """
           A drug is given at `mg_per_kg` mg per kg. Print the dose for `weight` kg rounded to 1 decimal place (`108.9` for 72.6 kg), then on the next line the number of whole 25 mg tablets that fit in that dose (`4`) as an int. The checker also tries another weight. (A practice calculation, not a clinical rule.)""",
           "weight = 72.6\nmg_per_kg = 1.5\n# rounded dose, then whole tablets\n",
           """
           check_eq("prints 108.9 then 4", lambda: out.strip().split("\\n"), ["108.9", "4"],
                    "72.6 * 1.5 is 108.89999999999999; round(..., 1) tidies it. Whole tablets must print as 4, not 4.0.")
           def other():
               n2, o2 = rerun("weight = 72.6", "weight = 10")
               return o2.strip().split("\\n")
           check_eq("10 kg gives 15.0 then 0", other, ["15.0", "0"],
                    "Calculate from weight and mg_per_kg. int() cuts off the fraction: int(15.0 / 25) is 0.")
           """,
           "round(weight * mg_per_kg, 1) for the dose. int(dose / 25) for whole tablets: // on a float gives a float like 4.0.",
           "weight = 72.6\nmg_per_kg = 1.5\ndose = weight * mg_per_kg\nprint(round(dose, 1))\nprint(int(dose / 25))"),
    ],
    predict=[
        PRED("a = 10\nb = a\na = a + 5\nprint(a, b)",
             "`b = a` ties a second tag to the value 10. `a = a + 5` makes a new value, 15, and moves only the `a` tag onto it, so `b` still shows 10.",
             traps={
                 "15 15": "`b = a` does not link the names forever: it ties `b` to the value 10, and moving `a` later leaves `b` where it is.",
                 "10 10": "`a = a + 5` really does move `a` to the new value 15.",
             }, id="p0"),
        PRED("print(type(3 / 1), type(3 // 1))",
             "`/` always gives a float. `//` on two ints gives an int. `type()` prints as `<class '...'>`.",
             traps={
                 "<class 'int'> <class 'int'>": "`/` always gives a float, even when the answer is whole: 3 / 1 is 3.0.",
                 "float int": "`type()` prints in the form `<class 'float'>`, not just the name.",
             }, id="p1"),
        PRED("s = 0.1 + 0.2\nprint(s == 0.3, round(s, 2) == 0.3)",
             "The raw sum is 0.30000000000000004, so `==` is False. Rounding to 2 places gives 0.3, which equals 0.3.",
             traps={
                 "True True": "0.1 + 0.2 is stored as 0.30000000000000004, so exact `==` with 0.3 is False.",
                 "False False": "round(..., 2) removes the tiny error, giving exactly the same float as 0.3.",
             }, id="p2"),
        PRED("a, b = 1, 2\na, b = b, a + b\nprint(a, b)",
             "The right side is worked out first using the old values: (2, 1 + 2). Then both names are tied to the new values.",
             traps={
                 "2 4": "The whole right side uses the OLD values: a + b is 1 + 2, worked out before `a` changes.",
             }, id="p3"),
        PRED('print("3" + "4", int("3") + int("4"))',
             "Strings join, giving the text 34. After converting to int, `+` adds them: 7.",
             traps={
                 "7 7": "`+` on two strings joins them: \"3\" + \"4\" is \"34\".",
                 "34 34": "After `int()` they are numbers, so `+` adds: 7.",
             }, id="p4"),
        PRED("print(round(2.5), round(3.5), int(3.9))",
             "`round` sends exact halves to the nearest even number: 2 and 4. `int` does not round at all; it cuts the fraction off, giving 3.",
             traps={
                 "3 4 4": "`round(2.5)` is 2 (halves go to the even neighbour), and `int(3.9)` cuts off to 3 rather than rounding.",
                 "3 4 3": "Exact halves go to the nearest even number, so `round(2.5)` is 2.",
                 "2 4 4": "`int()` cuts off the fraction instead of rounding: `int(3.9)` is 3.",
             }, id="p-round"),
        PRED('x = "5"\nprint(x * 2, int(x) * 2, float(x) + 1)',
             "A string times an int repeats it (55). After `int` it multiplies (10). `float` gives 5.0, and a float plus an int is a float: 6.0.",
             traps={
                 "10 10 6.0": "`x` is still the string \"5\": a string times 2 repeats it, giving 55.",
                 "55 10 6": "Adding an int to a float gives a float: 6.0.",
             }, id="p-mix"),
    ],
    cards=[
        CARD("What does `x = 5` really do?", "It ties the name `x` to the value 5. Names are tags on objects, not boxes holding values.", id="c0"),
        CARD("`x = 5`, then `y = x`, then `x = 7`. What does `print(y)` show?", "`5`. Reassigning `x` moves only the `x` tag; `y` still points at 5.", id="c1"),
        CARD("Which type is the value `None`?", "`NoneType`. `None` is its only value and means \"no value here\".", id="c2"),
        CARD("What is wrong with `\"5\" + 5`?", "It is a `TypeError`: Python will not guess between `10` and `\"55\"`. Convert with `int()` or `str()`.", id="c3"),
        CARD("`x = 3.14159`. What does `f\"{x:.2f}\"` give?", "`3.14`: `:.2f` shows two decimal places.", id="c4"),
        CARD("What does `f\"{1234567:,}\"` give?", "`1,234,567`: `:,` adds thousands separators.", id="c-fmt-comma"),
        CARD("What does `f\"{7:02d}\"` give?", "`07`: `:02d` pads a whole number with zeros to width 2.", id="c-fmt-pad"),
        CARD("What does `f\"{'ab':>5}\"` give?", "`   ab`: `:>5` right-aligns in 5 characters (3 spaces, then ab).", id="c-fmt-right"),
        CARD("Why is `0.1 + 0.2 == 0.3` False?", "Floats are stored in binary and 0.1 has no exact binary form. The sum is 0.30000000000000004.", id="c5"),
        CARD("When is `==` safe for floats?", "Only when you know the values are exact (like 0.5 or 0.25). Otherwise compare with `math.isclose(a, b)` or a tolerance like `abs(a - b) < 1e-9`.", id="c6"),
        CARD("How do you swap two variables in Python?", "`a, b = b, a`. The right side is built first, then both names are assigned.", id="c7"),
        CARD("Name one safe way to store money in code.", "Integer cents (ints are exact, format to 19.99 only for display), or Python's `decimal.Decimal`.", id="c8"),
        CARD("What does `print(round(2.5), round(3.5))` show?", "`2 4`: `round` sends exact halves to the nearest even number.", id="c-round-half"),
        CARD("What does `print(int(-3.9))` show?", "`-3`: `int()` cuts off the fraction toward zero (whereas `-3.9 // 1` is `-4.0`).", id="c-int-trunc"),
        CARD("What type does `input()` give back, even when the user types digits?", "Always a string (`str`). Convert it with `int()` or `float()` before doing arithmetic.", id="c-input"),
        CARD("What does `print(type(42))` show?", "`<class 'int'>`.", id="c-type-format"),
        CARD("What does `print(3 + 2.0)` show?", "`5.0`: an int mixed with a float gives a float.", id="c-mix"),
    ],
)
