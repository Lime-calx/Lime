from dsl import *

LESSON = lesson(
    id="py04", track="py", n=4, title="Functions", minutes=60,
    summary="Defining and calling functions, parameters, return values, scope, recursion, and testing with assert.",
    goals=[
        "Write functions with parameters, defaults and return values",
        "Explain the difference between print and return",
        "Predict which names a function can see and change",
        "Write a recursive function with a correct base case",
        "Test a function with assert before trusting it",
    ],
    blocks=[
        H("Why functions"),
        P("""
        A **function** is a named, reusable piece of code. Functions let you give a name to an idea, test it once, and use it many times. You have already called functions such as `print` and `type`. Now you write your own."""),

        H("Defining and calling"),
        CODE("""
        def greet(name):
            return "Hello, " + name + "!"

        message = greet("Ada")
        print(message)
        print(greet("Grace"))
        """),
        P("""
        `def` defines the function, and nothing inside it runs until it is **called**. `name` is a **parameter**: a name for an input. `"Ada"` is an **argument**: the actual value passed in. `return` ends the function and hands a value back to the caller."""),
        NOTE("trap", """
        `print` and `return` are different. `print` shows text to a person and gives back nothing. `return` hands a value back to the program so it can be stored or used. A function with no `return` gives back `None`."""),
        CODE("""
        def show_square(x):
            print(x * x)

        def square(x):
            return x * x

        a = show_square(4)
        b = square(4)
        print(a, b)
        """),
        P("""
        Functions that return values **compose**: `square(square(3))` works because the inner call produces a value for the outer one. A function that only prints cannot be used that way."""),

        H("Parameters: positional, keyword and default"),
        CODE("""
        def power(base, exponent=2):
            return base ** exponent

        print(power(5))
        print(power(2, 10))
        print(power(exponent=3, base=4))
        """),
        P("""
        Arguments can be passed by position or by keyword. A parameter with a **default value** becomes optional, and parameters with defaults must come after those without."""),

        H("Returning more than one value"),
        CODE("""
        def min_max(numbers):
            return min(numbers), max(numbers)

        low, high = min_max([4, 9, 2, 7])
        print(low, high)
        """),
        P("""
        This really returns one **tuple**, `(2, 9)`, which the caller unpacks into two names. Lists and tuples get a full lesson soon. For now, a list is written `[4, 9, 2, 7]`, and `min`, `max`, `sum` and `len` all work on it."""),

        H("Scope: where a name lives"),
        P("""
        Names created inside a function are **local**: they exist only while the function runs. A function can *read* names defined outside it, but assigning inside creates a new local name instead of changing the outer one."""),
        CODE("""
        rate = 10

        def double_rate():
            rate = 20          # a new local name
            return rate * 2

        print(double_rate())
        print(rate)
        """),
        NOTE("model", """
        Python looks names up in this order: **L**ocal, **E**nclosing function, **G**lobal, **B**uilt-in (the LEGB rule). Each call gets fresh locals, so a function that depends only on its arguments is easy to reason about, test and reuse. Avoid changing global state from inside functions unless you have a strong reason."""),
        CODE("""
        def add_one(x):
            x = x + 1
            return x

        n = 1
        add_one(n)
        print(n)
        """),
        P("""
        The function changed its own local `x`, never the caller's `n`, and the returned value was thrown away because nothing stored it."""),

        H("Docstrings and testing with assert"),
        P("""
        A **docstring**, a string on the first line of a function, documents what it does. `assert condition` raises an `AssertionError` when the condition is false, which makes a tiny test: silence means it passed."""),
        CODE('''
        def is_leap(year):
            """Return True if year is a leap year in the Gregorian calendar."""
            return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

        assert is_leap(2024)
        assert not is_leap(1900)
        assert is_leap(2000)
        print("all tests passed")
        '''),
        NOTE("tip", """
        Write the `assert` lines first, then the function. Seeing a test fail before it passes proves the test can actually fail. This habit is the core of test-driven development."""),

        H("Functions are values"),
        P("""
        A function is an object like any other: you can store it in a variable and pass it to another function. This is what makes tools such as `sorted(items, key=...)` possible."""),
        CODE("""
        def apply_twice(func, value):
            return func(func(value))

        def triple(x):
            return x * 3

        print(apply_twice(triple, 2))
        print(apply_twice(str.upper, "ab"))
        """),

        H("Recursion: a function that calls itself"),
        P("""
        A recursive function solves a problem by solving a smaller version of the same problem. It needs a **base case** that stops the recursion and a **recursive case** that moves toward it."""),
        CODE("""
        def factorial(n):
            if n <= 1:                    # base case
                return 1
            return n * factorial(n - 1)   # recursive case

        print(factorial(5))
        print(factorial(20))
        """),
        NOTE("trap", """
        Forget the base case, or never move toward it, and calls pile up until Python raises `RecursionError`. Each call also costs memory, so for plain counting a `for` loop is usually better. Recursion shines on naturally nested problems such as folders, trees and puzzles."""),
    ],
    exercises=[
        EX("is_even", "is_even",
           "Write `is_even(n)` that returns `True` when `n` is even and `False` otherwise. It must also work for negative numbers.",
           "def is_even(n):\n    # return True or False\n    pass\n",
           """
           f = ns.get("is_even")
           check("defines is_even", lambda: callable(f), "Use def is_even(n):")
           check("is_even(4) is True", lambda: f(4) is True, "Return a bool, not print it.")
           check("is_even(7) is False", lambda: f(7) is False)
           check("is_even(0) is True", lambda: f(0) is True)
           check("is_even(-4) is True", lambda: f(-4) is True, "Remainders of negative numbers still work with n % 2.")
           check("is_even(-3) is False", lambda: f(-3) is False)
           """,
           "`return n % 2 == 0`",
           "def is_even(n):\n    return n % 2 == 0"),
        EX("clamp", "clamp",
           "Write `clamp(x, lo, hi)` that returns `lo` if `x` is below `lo`, `hi` if `x` is above `hi`, and `x` otherwise.",
           "def clamp(x, lo, hi):\n    pass\n",
           """
           f = ns.get("clamp")
           check("defines clamp", lambda: callable(f))
           check("clamp(5, 0, 10) is 5", lambda: f(5, 0, 10) == 5)
           check("clamp(-3, 0, 10) is 0", lambda: f(-3, 0, 10) == 0)
           check("clamp(99, 0, 10) is 10", lambda: f(99, 0, 10) == 10)
           check("clamp(0.5, 0, 1) is 0.5", lambda: f(0.5, 0, 1) == 0.5)
           check("clamp(10, 0, 10) is 10", lambda: f(10, 0, 10) == 10)
           """,
           "Use if / elif / else, or combine min and max.",
           "def clamp(x, lo, hi):\n    if x < lo:\n        return lo\n    if x > hi:\n        return hi\n    return x"),
        EX("greet", "Defaults and keywords",
           """
           Write `greet(name, greeting="Hello")` that returns text like `Hello, Ada!`. It must work with the default, with a second positional argument and with keyword arguments.""",
           "def greet(name, greeting=\"Hello\"):\n    pass\n",
           """
           f = ns.get("greet")
           check("defines greet", lambda: callable(f))
           check('greet("Ada") is "Hello, Ada!"', lambda: f("Ada") == "Hello, Ada!")
           check('greet("Ada", "Hi") is "Hi, Ada!"', lambda: f("Ada", "Hi") == "Hi, Ada!")
           check("keyword arguments work", lambda: f(greeting="Yo", name="Bo") == "Yo, Bo!")
           """,
           "Build the text with an f-string: `f\"{greeting}, {name}!\"`.",
           'def greet(name, greeting="Hello"):\n    return f"{greeting}, {name}!"'),
        EX("spread", "spread",
           "Write `spread(numbers)` that returns the largest number minus the smallest number in a list. `spread([4, 9, 2, 7])` is 7.",
           "def spread(numbers):\n    pass\n",
           """
           f = ns.get("spread")
           check("defines spread", lambda: callable(f))
           check("spread([4, 9, 2, 7]) is 7", lambda: f([4, 9, 2, 7]) == 7)
           check("spread([5]) is 0", lambda: f([5]) == 0)
           check("works with negatives", lambda: f([-3, -10, 4]) == 14)
           """,
           "`max(numbers) - min(numbers)`",
           "def spread(numbers):\n    return max(numbers) - min(numbers)"),
        EX("cube", "Fix print versus return",
           "`cube(3) + 1` should be 28, but this function prints its answer and returns `None`. Fix it.",
           "def cube(x):\n    print(x * x * x)\n",
           """
           f = ns.get("cube")
           check("defines cube", lambda: callable(f))
           check("cube(3) returns 27", lambda: f(3) == 27, "The function must return the value, not print it.")
           check("cube(2) + 1 is 9", lambda: f(2) + 1 == 9)
           check("cube(-2) is -8", lambda: f(-2) == -8)
           """,
           "Replace print with return.",
           "def cube(x):\n    return x * x * x", kind="fix"),
        EX("fact", "Recursive factorial",
           "Write `fact(n)` using recursion: `fact(0)` and `fact(1)` are 1, and otherwise `fact(n)` is `n * fact(n - 1)`.",
           "def fact(n):\n    pass\n",
           """
           f = ns.get("fact")
           check("defines fact", lambda: callable(f))
           check("fact(0) is 1", lambda: f(0) == 1)
           check("fact(1) is 1", lambda: f(1) == 1)
           check("fact(5) is 120", lambda: f(5) == 120)
           check("fact(10) is 3628800", lambda: f(10) == 3628800)
           check("is recursive", lambda: code.count("fact(") >= 2, "fact must call itself.")
           """,
           "Base case first: if n <= 1 return 1. Then return n * fact(n - 1).",
           "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)"),
        EX("fib", "Fibonacci",
           "Write `fib(n)` returning the n-th Fibonacci number, with `fib(0)` = 0, `fib(1)` = 1 and each later number the sum of the two before it. Use a loop: the recursive version gets very slow.",
           "def fib(n):\n    pass\n",
           """
           f = ns.get("fib")
           check("defines fib", lambda: callable(f))
           check("fib(0) is 0", lambda: f(0) == 0)
           check("fib(1) is 1", lambda: f(1) == 1)
           check("fib(10) is 55", lambda: f(10) == 55)
           check("fib(30) is 832040", lambda: f(30) == 832040, "Too slow? Keep two variables and update them in a loop.")
           """,
           "Keep a and b = 0, 1. Repeat n times: a, b = b, a + b. Return a.",
           "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a"),
    ],
    predict=[
        PRED("def f(x):\n    x = x + 1\n    return x\n\na = 1\nf(a)\nprint(a)",
             "The function works on its own local `x`. The returned 2 was discarded, and the caller's `a` never changed."),
        PRED('def g():\n    print("hi")\n\nr = g()\nprint(r)',
             "`g` prints hi but has no return, so `r` is `None`."),
        PRED("x = 10\n\ndef h():\n    x = 5\n    return x\n\nprint(h(), x)",
             "Assigning inside `h` creates a new local `x`. The global `x` is untouched, so the output is 5 and 10."),
        PRED("def power(base, exponent=2):\n    return base ** exponent\n\nprint(power(3), power(2, 5), power(exponent=1, base=9))",
             "The default exponent is 2 (3 ** 2 = 9). Positional arguments give 2 ** 5 = 32. Keywords can come in any order: 9 ** 1 = 9."),
        PRED('def count_down(n):\n    if n == 0:\n        return "liftoff"\n    return count_down(n - 1)\n\nprint(count_down(3))',
             "Each call returns the result of the next smaller call until n reaches 0 and the base case returns the text."),
    ],
    cards=[
        CARD("What does `return` do?", "Ends the function and hands a value back to the caller. Without it the function returns `None`."),
        CARD("`print` versus `return`?", "`print` shows text to a person. `return` gives a value to the program so it can be stored and reused."),
        CARD("Parameter versus argument?", "A parameter is the name in the `def` line. An argument is the value you pass when you call it."),
        CARD("What does a default parameter value do?", "It makes that argument optional: `def power(b, e=2)` can be called as `power(5)`."),
        CARD("Can a function change the caller's variable by assigning to the same name?", "No. Assigning inside a function creates a new local name. The caller's variable is unchanged."),
        CARD("What is the LEGB rule?", "The order Python looks up a name: Local, Enclosing function, Global, Built-in."),
        CARD("What two parts must every recursive function have?", "A base case that stops it, and a recursive case that moves toward the base case."),
        CARD("What does `assert x > 0` do?", "Raises `AssertionError` if the condition is false and does nothing if it is true. A tiny test."),
        CARD("What does a function with no `return` give back?", "`None`."),
    ],
)
