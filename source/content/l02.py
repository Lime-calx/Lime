from dsl import *

LESSON = lesson(
    id="py02", track="py", n=2, title="Names, types and objects", minutes=45,
    summary="Variables as labels on objects, the core types, conversion, f-strings and why floats are approximate.",
    goals=[
        "Explain assignment as attaching a name to a value",
        "Recognise int, float, str, bool and None and convert between them",
        "Build text with f-strings and format specifiers",
        "Compare floats safely and store money as integers",
    ],
    blocks=[
        H("Names point at values"),
        P("""
        A **variable** is a name attached to a value. `price = 12` creates the value `12` and attaches the name `price` to it. The `=` sign is **assignment**, not a claim of equality: it means "make this name refer to that value"."""),
        CODE("""
        price = 12
        print(price)
        price = 15
        print(price)
        """),
        NOTE("model", """
        Think of names as labels on objects, not as boxes that hold values. Two names can label the same object, and moving a label never changes the object. For numbers this is invisible. For lists in lesson 6 it becomes critical."""),
        CODE("""
        x = 5
        y = x
        x = 7
        print(x, y)
        """),
        P("""
        `y = x` attached a second label to the value 5. Then `x = 7` moved only the `x` label to a new value, so `y` still points at 5."""),

        H("Naming rules and habits"),
        P("""
        Names may contain letters, digits and underscores, cannot start with a digit, and cannot be a reserved word such as `if` or `for`. Case matters: `Score` and `score` are different names.

        Python convention is `snake_case` for variables and functions. Choose names that say what the value *means*: `seconds_per_day` beats `x`, and a month from now you will thank yourself."""),

        H("The core types"),
        P("""
        Every value has a **type** that decides what you can do with it. `type(value)` tells you which."""),
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
        - `bool`: `True` or `False`
        - `NoneType`: the single value `None`, meaning "no value here\""""),

        H("Operators depend on type"),
        CODE("""
        print(2 + 3)
        print("2" + "3")
        print("ab" * 3)
        print("Ada" + " " + "Lovelace")
        """),
        NOTE("trap", """
        Mixing types is a `TypeError`: `"5" + 5` fails because Python will not guess whether you want `10` or `"55"`. Convert explicitly with `int()`, `float()` or `str()`."""),
        CODE("""
        age_text = "17"
        age = int(age_text)
        print(age + 1)
        print(str(age) + " years")
        print(float("2.5") * 2)
        """),
        P("""
        `int("abc")` raises a `ValueError`: the type is right (a string) but this particular value cannot be converted."""),

        H("f-strings: building text from values"),
        P("""
        An **f-string** puts values straight into text. Write `f"..."` and put expressions inside `{}`. After a colon you can add a **format specifier**: `:.2f` means two decimal places, `:>8` right-aligns in 8 characters, `:,` adds thousands separators, and `:02d` pads an integer with zeros to width 2."""),
        CODE("""
        item = "notebook"
        price = 3.5
        qty = 4
        print(f"{qty} x {item} = {qty * price}")
        print(f"{qty * price:.2f}")
        print(f"{1234567:,}")
        print(f"{item:>10}|")
        print(f"{7:02d}")
        """),
        P("""
        The expression inside `{}` is evaluated like any other, so `{qty * price}` works."""),

        H("Floating-point numbers are approximations"),
        CODE("""
        print(0.1 + 0.2)
        print(0.1 + 0.2 == 0.3)
        print(abs((0.1 + 0.2) - 0.3) < 1e-9)
        """),
        P("""
        Computers store floats in binary. Just as 1/3 has no exact decimal form, 0.1 has no exact binary form, so tiny errors appear. The practical rule: never compare floats with `==`. Compare with a tolerance such as `abs(a - b) < 1e-9`, and use `round()` or a format specifier for display."""),
        NOTE("tip", """
        Whole numbers as ints are exact. That is why prices are best stored as integer cents (`1999`) and only formatted as `19.99` when shown."""),

        H("Updating values"),
        CODE("""
        count = 0
        count = count + 1
        count += 1
        count *= 5
        print(count)
        """),
        P("""
        `count += 1` is shorthand for `count = count + 1`, and the same pattern works for `-=`, `*=`, `/=`, `//=`, `%=` and `**=`. You can also assign several names at once, which gives a swap without a temporary variable:"""),
        CODE("""
        a, b = 3, 9
        a, b = b, a
        print(a, b)
        """),
        P("""
        The right side is worked out completely first, producing the pair `9, 3`, and only then are the names assigned. That is why the swap works."""),
    ],
    exercises=[
        EX("swap", "Swap two names",
           "Swap the values of `a` and `b` so that afterwards `a` is 9 and `b` is 3. Do not retype the numbers.",
           "a = 3\nb = 9\n# swap the values below\n",
           """
           check("a is 9 and b is 3", lambda: ns["a"] == 9 and ns["b"] == 3, "After your code a should hold the old b and b the old a.")
           def other():
               n2, _ = rerun("a = 3", "a = 100")
               return n2["a"] == 9 and n2["b"] == 100
           check("works for other starting values", other, "Do not type 9 or 3 in your own code.")
           """,
           "Tuple assignment: a, b = b, a",
           "a = 3\nb = 9\na, b = b, a"),
        EX("receipt", "Build a receipt line",
           """
           Using an f-string, print `4 x notebook = 14.00` built from the three variables. The total must show two decimal places.""",
           'item = "notebook"\nprice = 3.5\nqty = 4\n# print the receipt line below\n',
           """
           check("prints the receipt line", lambda: out.strip() == "4 x notebook = 14.00", "Format: quantity, ' x ', item, ' = ', total with 2 decimals.")
           def other():
               n2, o2 = rerun("qty = 4", "qty = 3")
               return o2.strip() == "3 x notebook = 10.50"
           check("works for other quantities", other, "Compute the total from the variables instead of typing it.")
           """,
           "Inside the braces, `qty * price:.2f` multiplies and formats in one step.",
           'item = "notebook"\nprice = 3.5\nqty = 4\nprint(f"{qty} x {item} = {qty * price:.2f}")'),
        EX("types", "Fix the type error",
           """
           This code raises a `TypeError`. Fix it so `next_year` is the integer 18 and the program prints `18`.""",
           'age = "17"\nnext_year = age + 1\nprint(next_year)\n',
           """
           check("prints 18", lambda: out.strip() == "18", "age is a string. Convert it before adding.")
           check("next_year is an int", lambda: type(ns["next_year"]) is int, "Use int() on the string.")
           def other():
               n2, _ = rerun('age = "17"', 'age = "40"')
               return n2["next_year"] == 41
           check("works for another age", other, "Convert the variable, not the number 17.")
           """,
           "Wrap the string in int() before adding 1.",
           'age = "17"\nnext_year = int(age) + 1\nprint(next_year)', kind="fix"),
        EX("close", "Compare floats safely",
           """
           Set `close` to `True` when `a` and `b` are equal within `1e-9`, and `False` otherwise.""",
           "a = 0.1 + 0.2\nb = 0.3\n# set close below\nclose = None\n",
           """
           check("close is True for 0.1 + 0.2 and 0.3", lambda: ns["close"] is True, "Compare the distance between them to a tiny tolerance.")
           def other():
               n2, _ = rerun("b = 0.3", "b = 0.4")
               return n2["close"] is False
           check("close is False when they differ", other, "abs(a - b) is the distance between the two numbers.")
           """,
           "abs(a - b) < 1e-9",
           "a = 0.1 + 0.2\nb = 0.3\nclose = abs(a - b) < 1e-9"),
        EX("clocktime", "Format a clock time",
           """
           `total_minutes` holds minutes since midnight. Print them as a clock time `HH:MM`, with both parts padded to two digits, so 785 prints `13:05`.""",
           "total_minutes = 785\n# print the clock time below\n",
           """
           check("prints 13:05", lambda: out.strip() == "13:05", "785 minutes is 13 hours and 5 minutes.")
           def other():
               n2, o2 = rerun("total_minutes = 785", "total_minutes = 61")
               return o2.strip() == "01:01"
           check("pads with zeros (61 gives 01:01)", other, "Use the :02d format specifier.")
           """,
           "Use // and % for the parts and :02d inside the f-string braces.",
           'total_minutes = 785\nhours = total_minutes // 60\nminutes = total_minutes % 60\nprint(f"{hours:02d}:{minutes:02d}")'),
    ],
    predict=[
        PRED("x = 5\ny = x\nx = 7\nprint(x, y)",
             "`y = x` attaches a second label to the value 5. `x = 7` then moves only the label `x`."),
        PRED("print(type(3 / 1), type(3 // 1))",
             "`/` always gives a float. `//` on two ints gives an int."),
        PRED("print(0.1 + 0.2 == 0.3, round(0.1 + 0.2, 2) == 0.3)",
             "The raw sum is 0.30000000000000004, so `==` is False. Rounding to 2 places gives 0.3, which equals 0.3."),
        PRED("a, b = 1, 2\na, b = b, a + b\nprint(a, b)",
             "The right side is evaluated first using the old values: (2, 1 + 2). Then both names are assigned."),
        PRED('print("3" + "4", int("3") + int("4"))',
             "Strings concatenate, giving the text 34. After converting to int, `+` adds them: 7."),
    ],
    cards=[
        CARD("What does `x = 5` really do?", "It attaches the name `x` to the value 5. Names are labels on objects, not boxes holding values."),
        CARD("After `y = x` then `x = 7`, what is `y`?", "Still the old value. Reassigning `x` moves only the label `x`."),
        CARD("What are the five core types so far?", "`int`, `float`, `str`, `bool` and `NoneType` (the value `None`)."),
        CARD("Why does `\"5\" + 5` fail?", "It is a `TypeError`: Python will not guess between `10` and `\"55\"`. Convert with `int()` or `str()`."),
        CARD("What do `{x:.2f}`, `{x:>8}`, `{x:,}` and `{x:02d}` do inside an f-string?", "Two decimals; right-align in 8 characters; thousands separators; pad an integer with zeros to width 2."),
        CARD("Why is `0.1 + 0.2 == 0.3` False?", "Floats are stored in binary and 0.1 has no exact binary form. The sum is 0.30000000000000004."),
        CARD("How should you compare floats?", "With a tolerance, like `abs(a - b) < 1e-9`, never with `==`."),
        CARD("How do you swap two variables in Python?", "`a, b = b, a`. The right side is built first, then both names are assigned."),
        CARD("Best way to store money in code?", "As integer cents. Ints are exact, and you format to dollars only for display."),
    ],
)
