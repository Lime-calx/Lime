from dsl import *

LESSON = lesson(
    id="py01", track="py", n=1, title="Programs, values and expressions", minutes=35,
    summary="What a program is, how Python runs it, and how to build and read expressions.",
    goals=[
        "Explain what the interpreter does with your code",
        "Use print and the arithmetic operators, including // and %",
        "Predict the result of an expression using precedence rules",
        "Read an error message from the bottom up",
    ],
    blocks=[
        H("What a program is"),
        P("""
        A program is a precise list of instructions. A computer cannot guess what you meant, so it does exactly what the text says, in order, from the first line to the last.

        Python is an *interpreted* language: a program called the **interpreter** reads your text, checks that it is valid Python, and carries out one statement at a time. In Lime the interpreter runs inside this page."""),
        CODE("""
        print("Hello, world")
        print("Lines run top to bottom")
        """),
        P("""
        `print(...)` is a **function call**: it sends text to the output. Text inside quotes is a **string**. Edit the code above and press Run. Changing code and watching what happens is the fastest way to learn."""),
        NOTE("tip", """
        Run every example, then change one thing and predict what will happen before you run it again. Prediction followed by checking is the habit that builds real understanding."""),

        H("Values, expressions and statements"),
        P("""
        A **value** is a piece of data, like `42`, `3.5` or `"hi"`. An **expression** is code that produces a value, like `6 * 7`. A **statement** is a complete instruction, like `print(6 * 7)`. Python works out the expression first, then the statement uses the result."""),
        CODE("""
        print(6 * 7)
        print(10 - 4)
        print(2 ** 8)
        6 * 7   # calculated and thrown away: nothing is shown
        """),
        NOTE("trap", """
        In a script, an expression alone on a line is calculated and discarded. Only `print` shows something. (Interactive shells print it for you, which is why some tutorials seem to disagree.)"""),

        H("The arithmetic operators"),
        CODE("""
        print(7 + 2)    # addition
        print(7 - 2)    # subtraction
        print(7 * 2)    # multiplication
        print(7 / 2)    # true division: always a float
        print(7 // 2)   # floor division
        print(7 % 2)    # remainder (modulo)
        print(7 ** 2)   # power
        """),
        NOTE("model", """
        `/` always returns a float, even when the answer is whole: `8 / 2` is `4.0`. `//` divides and rounds **down** toward negative infinity, so `-7 // 2` is `-4`, not `-3`. `%` is the matching remainder, and the two always agree: `a == (a // b) * b + a % b`."""),
        CODE("""
        print(8 / 2)
        print(-7 // 2, -7 % 2)
        print((-7 // 2) * 2 + (-7 % 2))
        """),
        P("""
        Floor division and remainder appear everywhere in programming: turning minutes into hours and minutes, wrapping around a clock, picking every Nth item, and testing whether a number is even (`n % 2 == 0`)."""),

        H("Precedence: what Python calculates first"),
        P("""
        With several operators in one expression, Python follows precedence rules, as in maths: parentheses first, then `**`, then `*`, `/`, `//`, `%`, then `+` and `-`. Operators of equal rank run left to right, except `**`, which runs right to left."""),
        CODE("""
        print(2 + 3 * 4)
        print((2 + 3) * 4)
        print(-2 ** 2)
        print((-2) ** 2)
        print(2 ** 3 ** 2)
        """),
        NOTE("trap", """
        `-2 ** 2` is `-4`, because `**` binds tighter than the minus sign: it means `-(2 ** 2)`. When unsure, add parentheses. Extra parentheses cost nothing and remove doubt."""),

        H("Two kinds of number"),
        P("""
        `int` is a whole number of any size. `float` is a number with a decimal point, stored in binary with limited precision. `3` is an int and `3.0` is a float. The next lesson studies them properly; for now notice how they print."""),
        CODE("""
        print(3, 3.0)
        print(2 ** 100)
        print(1 / 3)
        """),
        P("""
        Python integers never overflow, so `2 ** 100` is exact. Floats are approximations, which is why `1 / 3` shows many digits and then stops."""),

        H("Comments"),
        P("""
        Anything after `#` on a line is a **comment**. Python ignores it; people read it. Good comments explain *why*, not *what*: `# skip the header row` helps, while a comment that repeats the code does not."""),

        H("Reading an error message"),
        P("""
        Mistakes are normal. Python reports them with a **traceback**. Read it from the bottom: the last line names the error type and explains it, and the lines above show where in your code it happened."""),
        CODE("""
        print("before")
        print(1 / 0)
        print("after")
        """),
        P("""
        `before` appears, then the program stops at the error and `after` never runs. Common errors at this stage:

        - `SyntaxError`: the text is not valid Python, so nothing runs
        - `NameError`: Python does not know a name, often a typo or missing quotes
        - `TypeError`: an operation was used on the wrong kind of value
        - `ZeroDivisionError`: division by zero"""),
        CODE("""
        print(Hello)   # without quotes, Hello is a name, not text
        """),
        NOTE("model", """
        An error message is information, not punishment. It is a colleague pointing at the exact line and telling you what they saw."""),
    ],
    exercises=[
        EX("hello", "Say hello",
           'Print exactly `Hello, Lime!`',
           "# write your code below\n",
           """
           check("prints Hello, Lime!", lambda: out.strip() == "Hello, Lime!",
                 "The text must match exactly: capital H and L, a comma, an exclamation mark.")
           """,
           "Use print() with the text inside quotes.",
           'print("Hello, Lime!")'),
        EX("week", "Seconds in a week",
           """
           Print the number of seconds in one week. Build it as an expression from 60, 24 and 7 so your working is visible, and print only the number.""",
           "# seconds in a week\n",
           """
           check("prints 604800", lambda: out.strip() == "604800", "Seconds per minute x minutes per hour x hours per day x days.")
           check("is written as an expression", lambda: "*" in code, "Write 60 * 60 * ... rather than typing the answer.")
           """,
           "60 seconds x 60 minutes x 24 hours x 7 days.",
           "print(60 * 60 * 24 * 7)"),
        EX("average", "Fix the average",
           """
           This should print the average of 4, 8 and 15, which is `9.0`, but it prints `17.0`. Fix it.""",
           "print(4 + 8 + 15 / 3)\n",
           """
           check("prints 9.0", lambda: out.strip() == "9.0", "Division happens before addition. Which part must be added first?")
           """,
           "Parentheses force the addition to happen before the division.",
           "print((4 + 8 + 15) / 3)", kind="fix"),
        EX("clock", "Hours and minutes",
           """
           A film lasts 135 minutes. Print the whole hours on one line and the leftover minutes on the next line, so the output is `2` then `15`. Use `//` and `%` to work them out.""",
           "# 135 minutes as hours and minutes\n",
           """
           check("prints 2 then 15 on two lines", lambda: out.split() == ["2", "15"], "Two print calls, one per line.")
           check("uses // and %", lambda: "//" in code and "%" in code, "Calculate the numbers instead of typing them.")
           """,
           "135 // 60 gives the hours. 135 % 60 gives what is left over.",
           "print(135 // 60)\nprint(135 % 60)"),
    ],
    predict=[
        PRED("print(7 // 2, 7 % 2, -7 // 2)",
             "`//` rounds down: 7 / 2 is 3.5 so the floor is 3, the remainder is 1, and -3.5 rounds down to -4."),
        PRED("print(2 + 3 * 4 ** 2)",
             "`**` first (4 ** 2 is 16), then `*` (48), then `+` (50)."),
        PRED("print(10 / 4, 10 // 4)",
             "`/` is true division and gives 2.5. `//` floors the result to 2."),
        PRED("print(-3 ** 2, (-3) ** 2)",
             "`**` binds tighter than the minus sign, so the first is -(3 ** 2) = -9. With parentheses the base is -3, giving 9."),
    ],
    cards=[
        CARD("What does the Python interpreter do?", "It reads your code and carries out its statements one at a time, from top to bottom."),
        CARD("Expression or statement: what is the difference?", "An expression produces a value (`6 * 7`). A statement is a complete instruction (`print(6 * 7)`)."),
        CARD("What are `7 // 2`, `7 % 2` and `-7 // 2`?", "3, 1 and -4. `//` rounds toward negative infinity."),
        CARD("What type does `/` always return?", "A float, even for whole results: `8 / 2` is `4.0`."),
        CARD("Python's order of operations?", "Parentheses, then `**`, then `* / // %`, then `+ -`. `**` runs right to left."),
        CARD("Why is `-2 ** 2` equal to `-4`?", "`**` binds tighter than the unary minus, so it is `-(2 ** 2)`."),
        CARD("How do you read a traceback?", "From the bottom: the error type and message are on the last line, and the line of your code is just above."),
        CARD("What does `#` do in Python code?", "It starts a comment: Python ignores the rest of that line."),
    ],
)
