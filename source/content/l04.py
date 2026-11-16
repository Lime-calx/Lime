from dsl import *

LESSON = lesson(
    id="py04", track="py", n=4, title="Functions", minutes=70,
    summary="Defining and calling functions, parameters, return values, scope, pure functions and side effects, recursion, and testing with assert.",
    goals=[
        "Write functions with parameters, defaults and return values",
        "Explain the difference between print and return",
        "Predict which names a function can see and change",
        "Write a recursive function with a correct base case, and know when a loop is better",
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
        `def` defines the function, and nothing inside it runs until it is **called**. `name` is a **parameter**: a name for an input. `"Ada"` is an **argument**: the actual value passed in. `return` ends the function at once and hands a value back to the caller."""),
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

        H("Early and multiple returns"),
        P("""
        A function can have several `return` statements. The first one reached ends the call, so later lines never run. This lets you handle the special cases first and leave the normal case at the bottom, without deep `else` nesting."""),
        CODE("""
        def triage(heart_rate):
            if heart_rate < 40:
                return "too slow"
            if heart_rate > 130:
                return "too fast"
            return "in range"

        print(triage(35), triage(150), triage(72))
        """),

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
        Inside a function, Python looks a name up first among the function's own **local** names, then among the **global** names of the program, then among the **built-in** names such as `print` and `len`. Each call gets fresh locals, so a function that depends only on its arguments is easy to reason about, test and reuse."""),
        P("""
        Python decides which names are local **before** the function runs: if a name is assigned anywhere in the function, it is local everywhere in that function. Reading it before the assignment is then an error, even though a global with that name exists."""),
        CODE("""
        count = 5

        def show():
            print(count)   # count is assigned below, so it is local here too
            count = 0

        show()
        """),
        P("""
        That is an `UnboundLocalError`: the local `count` has no value yet. The fix is to use a different name, or better, to pass the value in and return the new one. (Python has a `global count` statement that lets a function assign to the outer name, but it makes code hard to follow; prefer returning a value.)"""),
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
        NOTE("deep", """
        The full rule is called **LEGB**: Local, Enclosing, Global, Built-in. "Enclosing" matters only when you define a function inside another function: the inner one can read the outer one's local names. For example, inside `def outer(): unit = "mg"` a nested `def label(x): return str(x) + unit` can see `unit`. You will rarely need this early on."""),

        H("Lists passed to functions"),
        P("""
        A parameter is just another name for the caller's value. With numbers and text that never matters, because they cannot be changed in place. A list can be: `lst.append(x)` adds `x` to the end of that very list. (`append` is a *method*, a function attached to a value and called after a dot; lesson 5 covers methods.) `lst + [x]` instead builds a **new** list."""),
        CODE("""
        def add_in_place(doses):
            doses.append(5)          # changes the caller's list

        def add_new(doses):
            doses = doses + [5]      # points the local name at a new list
            return doses

        mine = [10]
        add_in_place(mine)
        print(mine)
        result = add_new(mine)
        print(mine, result)
        """),
        P("""
        So "a function cannot change the caller's variable" is true for **assignment**, but a function can change the list it was given. When that is not what the caller expects, it is a bug that is hard to find. Lesson 6 explores this in depth."""),

        H("Pure functions and side effects"),
        P("""
        A **pure function** only reads its arguments and returns a result: same inputs, same output, nothing else touched. Anything else a function does that the caller can notice, such as printing, changing a global name or changing a list it was given, is a **side effect**. Programs need some side effects, but keep them in a few clear places. Pure functions are the easiest to test."""),
        CODE("""
        def bmi(weight_kg, height_m):          # pure: returns, touches nothing
            return weight_kg / height_m ** 2

        def report(weight_kg, height_m):       # side effect: printing
            print(f"BMI {bmi(weight_kg, height_m):.1f}")

        report(70, 1.75)
        print(bmi(70, 1.75) == bmi(70, 1.75))
        """),

        H("Docstrings and testing with assert"),
        P("""
        A **docstring** is a string written as the first statement of a function's body. It documents what the function does, and Python keeps it with the function: in ordinary Python, `is_leap.__doc__` gives the text back and `help(is_leap)` shows it, which is how editors show you what a function does. (Lime's in-browser Python drops docstrings to save space, so here `__doc__` shows `None`.) `assert condition` raises an `AssertionError` when the condition is false, which makes a tiny test: silence means it passed."""),
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
        Write the `assert` lines first, then the function. Seeing a test fail before it passes proves the test can actually fail. Test the edges: for a cut-off at 50, try 49 and 50, not just 20 and 80."""),

        H("Functions are values"),
        P("""
        A function is an object like any other: you can store it in a variable and pass it to another function, without the brackets. This is what makes tools such as `sorted(items, key=...)` possible. Below, `abs` is the built-in function that gives a number's size without its sign: `abs(-7)` is 7."""),
        CODE("""
        def apply_twice(func, value):
            return func(func(value))

        def triple(x):
            return x * 3

        print(apply_twice(triple, 2))
        print(apply_twice(abs, -7))
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
        P("""
        Each call waits for the smaller call to finish before it carries on. Lines before the recursive call run on the way down; lines after it run on the way back up, in reverse order."""),
        CODE("""
        def descend(n):
            if n == 0:
                return            # a bare return ends the call (and returns None)
            print("down", n)
            descend(n - 1)
            print("up", n)

        descend(3)
        """),
        P("""
        Recursion can also be very wasteful. The obvious recursive Fibonacci, `fib(n - 1) + fib(n - 2)`, recomputes the same values again and again. This pure function counts how many calls it would make:"""),
        CODE("""
        def calls(n):
            if n < 2:
                return 1
            return 1 + calls(n - 1) + calls(n - 2)

        print(calls(10), calls(20))
        """),
        NOTE("trap", """
        Forget the base case, or never move toward it, and calls pile up until Python raises `RecursionError`. For plain counting a loop is usually simpler and faster. Recursion shines on naturally nested problems, such as folders inside folders, which you will meet later."""),
        NOTE("deep", """
        Every waiting call takes a slot on the **call stack**, and Python limits its depth to about 1000 calls by default. So `factorial(3000)` raises `RecursionError` even though the function is correct; a loop has no such limit."""),
    ],
    exercises=[
        EX("is_even", "is_even",
           "Write `is_even(n)` that returns `True` when `n` is even and `False` otherwise. It must also work for negative numbers.",
           "def is_even(n):\n    # return True or False\n    pass\n",
           """
           f = ns.get("is_even")
           check("defines is_even", lambda: callable(f), "Use def is_even(n):")
           check_eq("is_even(4) is True", lambda: f(4), True, "Return a bool, not print it: n % 2 == 0 is already True or False.")
           check_eq("is_even(7) is False", lambda: f(7), False, "An odd number leaves remainder 1 when divided by 2.")
           check_eq("is_even(0) is True", lambda: f(0), True, "0 % 2 is 0, so 0 is even.")
           check_eq("is_even(-4) is True", lambda: f(-4), True, "Remainders of negative numbers still work with n % 2.")
           check_eq("is_even(-3) is False", lambda: f(-3), False, "In Python -3 % 2 is 1, so the same test works.")
           check_eq("works for other numbers", lambda: [f(k) for k in (12, 31, 1000001, -100)], [True, False, False, True], "Compute the answer from n; do not list cases.")
           """,
           "`return n % 2 == 0`",
           "def is_even(n):\n    return n % 2 == 0"),
        EX("clamp", "clamp",
           "Write `clamp(x, lo, hi)` that returns `lo` if `x` is below `lo`, `hi` if `x` is above `hi`, and `x` otherwise.",
           "def clamp(x, lo, hi):\n    pass\n",
           """
           f = ns.get("clamp")
           check("defines clamp", lambda: callable(f), "Use def clamp(x, lo, hi):")
           check_eq("clamp(5, 0, 10) is 5", lambda: f(5, 0, 10), 5, "Inside the range, give x back unchanged.")
           check_eq("clamp(-3, 0, 10) is 0", lambda: f(-3, 0, 10), 0, "Below lo, return lo.")
           check_eq("clamp(99, 0, 10) is 10", lambda: f(99, 0, 10), 10, "Above hi, return hi.")
           check_eq("clamp(0.5, 0, 1) is 0.5", lambda: f(0.5, 0, 1), 0.5, "Return x itself, not a rounded version.")
           check_eq("clamp(10, 0, 10) is 10", lambda: f(10, 0, 10), 10, "x equal to hi is allowed.")
           check_eq("clamp(36, 37, 42) is 37", lambda: f(36, 37, 42), 37, "Use the parameters lo and hi, not fixed numbers.")
           """,
           "Use early returns: if x < lo return lo; if x > hi return hi; otherwise return x.",
           "def clamp(x, lo, hi):\n    if x < lo:\n        return lo\n    if x > hi:\n        return hi\n    return x"),
        EX("greet", "Defaults and keywords",
           """
           Write `greet(name, greeting="Hello")` that returns text like `Hello, Ada!`. It must work with the default, with a second positional argument and with keyword arguments.""",
           "def greet(name, greeting=\"Hello\"):\n    pass\n",
           """
           f = ns.get("greet")
           check("defines greet", lambda: callable(f), 'Keep the line def greet(name, greeting="Hello"):')
           check_eq('greet("Ada") is "Hello, Ada!"', lambda: f("Ada"), "Hello, Ada!", "Return the text; mind the comma, the space and the !.")
           check_eq('greet("Ada", "Hi") is "Hi, Ada!"', lambda: f("Ada", "Hi"), "Hi, Ada!", "Use the greeting parameter, not the fixed word Hello.")
           check_eq("keyword arguments work", lambda: f(greeting="Yo", name="Bo"), "Yo, Bo!", "Keywords match by name, so the order of the call does not matter.")
           """,
           "Build the text with an f-string: `f\"{greeting}, {name}!\"`.",
           'def greet(name, greeting="Hello"):\n    return f"{greeting}, {name}!"'),
        EX("spread", "spread",
           "Write `spread(numbers)` that returns the largest number minus the smallest number in a list. `spread([4, 9, 2, 7])` is 7.",
           "def spread(numbers):\n    pass\n",
           """
           f = ns.get("spread")
           check("defines spread", lambda: callable(f), "Use def spread(numbers):")
           check_eq("spread([4, 9, 2, 7]) is 7", lambda: f([4, 9, 2, 7]), 7, "max(numbers) - min(numbers).")
           check_eq("spread([5]) is 0", lambda: f([5]), 0, "With one number the largest and smallest are the same.")
           check_eq("works with negatives", lambda: f([-3, -10, 4]), 14, "4 - (-10) is 14.")
           check_eq("works with decimals", lambda: f([36.5, 38.0, 37.0]), 1.5, "Do not round: return the difference as it is.")
           """,
           "`max(numbers) - min(numbers)`",
           "def spread(numbers):\n    return max(numbers) - min(numbers)"),
        EX("cube", "Fix print versus return",
           "`cube(3) + 1` should be 28, but this function prints its answer and returns `None`. Fix it so it returns the cube and prints nothing.",
           "def cube(x):\n    print(x * x * x)\n",
           """
           f = ns.get("cube")
           check("defines cube", lambda: callable(f), "Keep def cube(x):")
           check_eq("cube(3) returns 27", lambda: silent(f, 3)[0], 27, "The function must return the value, not print it.")
           check_eq("cube(3) prints nothing", lambda: silent(f, 3)[1], "", "Remove the print: the caller decides whether to show the result.")
           check_eq("cube(2) + 1 is 9", lambda: silent(f, 2)[0] + 1, 9, "A returned value can be used in arithmetic; None cannot.")
           check_eq("cube(-2) is -8", lambda: silent(f, -2)[0], -8, "Multiply x by itself three times (or use x ** 3).")
           """,
           "Replace print(...) with return ...",
           "def cube(x):\n    return x * x * x", kind="fix"),
        EX("grade", "Grade with early returns",
           """
           Write `grade(score)` for a score from 0 to 100. It returns `"distinction"` for 90 and above, `"pass"` for 50 and above, and `"fail"` below 50. Use early returns, and test the cut-offs: 49 and 50, 89 and 90.""",
           "def grade(score):\n    pass\n",
           """
           f = ns.get("grade")
           check("defines grade", lambda: callable(f), "Use def grade(score):")
           check_eq("grade(49) is fail", lambda: f(49), "fail", "49 is below the pass mark of 50.")
           check_eq("grade(50) is pass", lambda: f(50), "pass", "50 itself passes: use >= 50, not > 50.")
           check_eq("grade(89) is pass", lambda: f(89), "pass", "89 is below the distinction mark.")
           check_eq("grade(90) is distinction", lambda: f(90), "distinction", "90 itself is a distinction: use >= 90. Test the highest band first.")
           check_eq("grade(100) and grade(0)", lambda: [f(100), f(0)], ["distinction", "fail"], "The ends of the range must work too.")
           check("returns, does not print", lambda: silent(f, 70)[1] == "", "Return the word; do not print it.")
           def _nodes(n, acc):
               acc.append(n)
               try:
                   d = vars(n)
               except TypeError:
                   d = {}
               if not d and hasattr(n, "_fields"):
                   d = {k: getattr(n, k, None) for k in n._fields}
               for k, v in list(d.items()):
                   if not k.startswith("_"):
                       for x in (v if isinstance(v, list) else [v]):
                           if hasattr(x, "_fields"):
                               _nodes(x, acc)
               return acc
           def returns():
               import ast
               return len([x for x in _nodes(ast.parse(code), []) if type(x).__name__ == "Return"])
           check("uses early returns", lambda: returns() >= 2, "Return as soon as you know the answer: one return per band, highest band first.")
           """,
           "if score >= 90: return \"distinction\". if score >= 50: return \"pass\". Then return \"fail\".",
           'def grade(score):\n    if score >= 90:\n        return "distinction"\n    if score >= 50:\n        return "pass"\n    return "fail"'),
        EX("pure", "Make it pure",
           """
           `add_visit` changes a global counter, a side effect. Rewrite it as a pure function: `add_visit(count)` takes the current count and returns the new one, with no `global`. Then use it so the program still prints `2`.""",
           "visits = 0\n\ndef add_visit():\n    global visits\n    visits = visits + 1\n\nadd_visit()\nadd_visit()\nprint(visits)\n",
           """
           f = ns.get("add_visit")
           check("defines add_visit", lambda: callable(f), "Keep the name add_visit, with one parameter.")
           check_eq("add_visit(5) returns 6", lambda: silent(f, 5)[0], 6, "Return count + 1.")
           check_eq("same input, same output", lambda: [f(0), f(0)], [1, 1], "A pure function gives the same answer every time for the same input.")
           check("no global statement", lambda: not has_node("Global"), "Remove global: pass the count in and return the new value.")
           check_eq("the program still prints 2", lambda: out.strip(), "2", "Store each result: visits = add_visit(visits).")
           """,
           "def add_visit(count): return count + 1. Then visits = add_visit(visits), twice.",
           "visits = 0\n\ndef add_visit(count):\n    return count + 1\n\nvisits = add_visit(visits)\nvisits = add_visit(visits)\nprint(visits)", kind="fix"),
        EX("fact", "Recursive factorial",
           "Write `fact(n)` using recursion: `fact(0)` and `fact(1)` are 1, and otherwise `fact(n)` is `n * fact(n - 1)`.",
           "def fact(n):\n    pass\n",
           """
           f = ns.get("fact")
           check("defines fact", lambda: callable(f), "Use def fact(n):")
           check_eq("fact(0) is 1", lambda: f(0), 1, "Base case: if n <= 1, return 1.")
           check_eq("fact(1) is 1", lambda: f(1), 1, "Base case: if n <= 1, return 1.")
           check_eq("fact(5) is 120", lambda: f(5), 120, "5 * 4 * 3 * 2 * 1.")
           check_eq("fact(10) is 3628800", lambda: f(10), 3628800, "Return n * fact(n - 1).")
           s = spy("fact")
           def count():
               s.reset()
               ns["fact"](5)
               return s.calls
           check_eq("fact(5) calls itself (5 calls in all)", count, 5, "fact(5) should call fact(4), which calls fact(3), and so on down to fact(1). A loop makes only 1 call.")
           """,
           "Base case first: if n <= 1 return 1. Then return n * fact(n - 1).",
           "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)"),
        EX("fib", "Fibonacci with a loop",
           "Write `fib(n)` returning the n-th Fibonacci number, with `fib(0)` = 0, `fib(1)` = 1 and each later number the sum of the two before it. Use a loop, not recursion: the recursive version makes thousands of calls (see the `calls` demo above). In a loop that only repeats, you can name the loop variable `_`, a name meaning \"I don't need this value\".",
           "def fib(n):\n    pass\n",
           """
           f = ns.get("fib")
           check("defines fib", lambda: callable(f), "Use def fib(n):")
           check_eq("fib(0) is 0", lambda: f(0), 0, "With no steps, return the first value, 0.")
           check_eq("fib(1) is 1", lambda: f(1), 1, "One step from 0, 1 gives 1.")
           check_eq("fib(10) is 55", lambda: f(10), 55, "Keep two names a, b = 0, 1 and update both each pass: a, b = b, a + b.")
           s = spy("fib")
           def count():
               s.reset()
               ns["fib"](20)
               return s.calls
           check_eq("fib(20) makes only one call", count, 1, "Your fib(20) calls itself (the number above is how many calls). Use a loop that updates two names instead.")
           ns["fib"] = s.orig
           check_eq("fib(30) is 832040", lambda: f(30), 832040, "Repeat the update n times with for _ in range(n).")
           """,
           "Keep a and b = 0, 1. Repeat n times: a, b = b, a + b. Return a.",
           "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a"),
    ],
    predict=[
        PRED('def shout(word):\n    word = word + "!"\n\nw = "hi"\nshout(w)\nprint(w)',
             "`shout` points its own local `word` at new text. The caller's `w` still names \"hi\", and the function returned nothing anyway.",
             traps={"hi!": "Assigning to the parameter changes only the function's local name; the caller's w is untouched."}, id="p0"),
        PRED('def g(x):\n    print(x * 2)\n\nr = g(4)\nprint(r)',
             "Calling `g` prints 8. It has no return, so `r` is `None`, which prints as None.",
             traps={"8\n8": "g prints its answer but has no return, so the caller gets None.",
                    "8": "The second print runs too: it shows r, which is None."}, id="p1"),
        PRED("level = 3\n\ndef peek():\n    return level * 2\n\ndef reset():\n    level = 0\n    return level\n\nprint(peek(), reset(), peek())",
             "`peek` reads the global `level`. `reset` assigns, so its `level` is a new local name; the global stays 3, and the second `peek` still gives 6.",
             traps={"6 0 0": "reset assigned to a local level. The global level is still 3."}, id="p2"),
        PRED("def f(a, b=2, c=3):\n    return a + 10 * b + 100 * c\n\nprint(f(1), f(1, c=0), f(1, 0))",
             "Defaults give 1 + 20 + 300 = 321. The keyword sets only c: 21. A second positional argument fills the second parameter, b: 1 + 0 + 300 = 301.",
             traps={"321 21 21": "A second positional argument fills b, the second parameter. Only a keyword can skip to c."}, id="p3"),
        PRED('def count_down(n):\n    if n == 0:\n        return "liftoff"\n    return count_down(n - 1)\n\nprint(count_down(3))',
             "Each call returns the result of the next smaller call until n reaches 0 and the base case returns the text, which is passed back up unchanged.",
             traps={"None": "Every level returns what the smaller call returned, so the text travels all the way back up."}, id="p4"),
        PRED("count = 0\n\ndef bump():\n    count = count + 1\n\nprint(\"defined\", count)",
             "`def` only defines `bump`; its body never runs because `bump` is never called. Calling it would raise UnboundLocalError (count is local because it is assigned), but the program only prints the global count.",
             traps={"UnboundLocalError": "The error would come only when bump() is called. Defining a function runs nothing inside it.",
                    "defined 1": "bump is never called, so nothing adds 1."}, id="p-unbound"),
        PRED("def add_dose(doses):\n    doses.append(5)\n\nmine = [10]\nadd_dose(mine)\nprint(mine)",
             "`doses` and `mine` are two names for the same list. `append` changes that list, so the caller sees the 5.",
             traps={"[10]": "No assignment happens here: append changes the one list both names point at."}, id="p-list-append"),
        PRED("def add_dose(doses):\n    doses = doses + [5]\n\nmine = [10]\nadd_dose(mine)\nprint(mine)",
             "`doses + [5]` builds a new list, and the assignment points only the local name at it. The caller's list is unchanged.",
             traps={"[10, 5]": "`+` makes a new list and `=` re-points the local name; the caller's list was never changed."}, id="p-list-rebind"),
        PRED("def f(n):\n    if n == 0:\n        return\n    print(n)\n    f(n - 1)\n    print(n)\n\nf(2)",
             "f(2) prints 2, then f(1) prints 1, then f(0) returns at once. Back in f(1) the second print shows 1; back in f(2) it shows 2. Calls finish in reverse order.",
             traps={"2\n1\n2\n1": "The second print in each call waits until the smaller call has finished, so the innermost call finishes first.",
                    "2\n1": "After each smaller call returns, the caller carries on and runs its second print."}, id="p-trace"),
    ],
    cards=[
        CARD("What does `return` do?", "Ends the function at once and hands a value back to the caller.", id="c0"),
        CARD("`print` versus `return`?", "`print` shows text to a person. `return` gives a value to the program so it can be stored and reused.", id="c1"),
        CARD("Parameter versus argument?", "A parameter is the name in the `def` line. An argument is the value you pass when you call it.", id="c2"),
        CARD("With `def power(b, e=2): return b ** e`, what is `power(3)`?", "9. `e` was left out, so its default 2 is used: 3 ** 2.", id="c3"),
        CARD("Can a function change the caller's variable by assigning to the same name?", "No. Assigning inside a function creates a new local name. The caller's variable is unchanged.", id="c4"),
        CARD("Inside a function, in what order does Python look up a name?", "Local names first, then global names, then built-ins (the LEGB rule; E, enclosing, applies to functions defined inside functions).", id="c5"),
        CARD("What two parts must every recursive function have?", "A base case that stops it, and a recursive case that moves toward the base case.", id="c6"),
        CARD("What does `assert x > 0` do?", "Raises `AssertionError` if the condition is false and does nothing if it is true. A tiny test.", id="c7"),
        CARD("What does a function with no `return` give back?", "`None`.", id="c8"),
        CARD("If `def add(lst): lst.append(1)` is called as `add(mine)`, does `mine` change?", "Yes. `lst` and `mine` name the same list, and `append` changes that list in place.", id="c-list-param"),
        CARD("If `def add(lst): lst = lst + [1]` is called as `add(mine)`, does `mine` change?", "No. `lst + [1]` builds a new list and only the local name `lst` is pointed at it.", id="c-list-rebind"),
        CARD("What is wrong? `count = 5`, then a function whose body is `print(count)` followed by `count = 0`.", "Calling it raises UnboundLocalError: `count` is assigned in the function, so it is local throughout, and it has no value yet when printed.", id="c-unbound"),
        CARD("What does the `global` statement do, and what is usually better?", "`global x` lets a function assign to the outer `x`. Better: pass the value in and return the new value.", id="c-global"),
        CARD("What is a pure function?", "One that only uses its arguments and returns a result: same inputs, same output, no side effects.", id="c-pure"),
        CARD("`def f(n):` prints n, calls `f(n - 1)` while n > 0, then prints n again. What does `f(2)` print?", "2, 1, 1, 2. Lines after the recursive call run as the calls return, innermost first.", id="c-trace"),
        CARD("What does `def f(): return 1` followed by `print(\"after\")` inside f print when you call `print(f())`?", "Only `1`. `return` ends the call, so the line after it never runs.", id="c-early-return"),
        CARD("Why is `fib(n) = fib(n - 1) + fib(n - 2)` slow?", "It recomputes the same values over and over: fib(20) makes 21,891 calls. A loop with two names makes one.", id="c-fib-calls"),
        CARD("What makes a string a docstring?", "Being the first statement of a function's body. Python keeps it as `function_name.__doc__` and `help()` shows it.", id="c-docstring"),
    ],
)
