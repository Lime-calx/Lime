from dsl import *

LESSON = lesson(
    id="py08", track="py", n=8, title="Errors, exceptions and debugging", minutes=65,
    summary="Reading tracebacks, handling and raising exceptions, a repeatable debugging method, and testing edge cases.",
    goals=[
        "Tell syntax, runtime and logic errors apart",
        "Read a traceback and find the line to investigate",
        "Use try, except, else and finally, and catch specific exceptions",
        "Raise your own exceptions with clear messages",
        "Follow a debugging method instead of guessing",
    ],
    blocks=[
        H("Three kinds of mistake"),
        P("""
        - **Syntax errors**: the text is not valid Python. Python reports them before anything runs.
        - **Runtime errors** (exceptions): the code is valid, but something fails while it runs. The program stops at that line.
        - **Logic errors**: the program runs and finishes but gives the wrong answer. There is no message at all, which makes these the hardest."""),
        CODE("""
        print("start")
        numbers = [1, 2, 3]
        print(numbers[5])
        print("never printed")
        """),

        H("Reading a traceback"),
        P("""
        Read a traceback from the bottom. The last line is the error type and message. Above it is the line that failed, and above that the chain of function calls that led there."""),
        CODE("""
        def average(values):
            return sum(values) / len(values)

        def report(values):
            return "average: " + str(average(values))

        print(report([4, 6]))
        print(report([]))
        """),
        NOTE("tip", """
        Start at the last line, then find the **deepest line in your own code**. That is usually where to look first, though the real cause may be a bad value that was passed in from higher up the chain."""),

        H("Common exception types"),
        P("""
        - `SyntaxError`, `IndentationError`: invalid code layout
        - `NameError`: a name Python does not know
        - `TypeError`: the wrong type for an operation, or the wrong number of arguments
        - `ValueError`: the right type but an unusable value, like `int("x")`
        - `IndexError`, `KeyError`: a missing position or key
        - `ZeroDivisionError`: dividing by zero
        - `AttributeError`: the object has no such attribute or method
        - `FileNotFoundError`: opening a file that is not there
        - `AssertionError`: an `assert` failed
        - `RecursionError`: too many nested calls"""),

        H("Handling exceptions with try and except"),
        CODE("""
        def to_int(text):
            try:
                return int(text)
            except ValueError:
                return None

        print(to_int("42"), to_int("4x2"), to_int(""))
        """),
        P("""
        Code in `try` runs normally. If it raises an exception that matches an `except` clause, Python jumps to that clause instead of crashing. Catch the **specific** exceptions you expect and know how to handle."""),
        CODE("""
        for text in ["10", "zero", "0"]:
            try:
                value = 100 / int(text)
            except ValueError:
                print(text, "is not a number")
            except ZeroDivisionError:
                print("cannot divide by zero")
            else:
                print("result", value)
            finally:
                print("checked", text)
        """),
        P("""
        `else` runs only when no exception happened. `finally` runs no matter what, which makes it the right place for cleanup such as closing a file."""),
        NOTE("trap", """
        Never write a bare `except:` or `except Exception: pass` as a quick fix. The error disappears, the bug stays, and you lose the only clue you had. Catch the narrowest exception, then handle it or let it continue upward."""),

        H("Raising your own exceptions"),
        CODE("""
        def set_age(age):
            if not isinstance(age, int):
                raise TypeError("age must be a whole number")
            if age < 0:
                raise ValueError("age cannot be negative")
            return age

        for candidate in [30, -5, "x"]:
            try:
                print(set_age(candidate))
            except (ValueError, TypeError) as error:
                print(type(error).__name__ + ":", error)
        """),
        P("""
        `raise` signals that a function cannot do its job and stops it on the spot. Fail early with a clear message instead of letting a bad value travel and cause a confusing error far away. `except ... as error` gives you the exception object so you can use its message."""),
        NOTE("model", """
        Python style leans towards **EAFP**: "easier to ask forgiveness than permission". Try the operation and handle the failure, instead of checking every condition first (**LBYL**, "look before you leap"). EAFP avoids duplicated checks and race conditions. LBYL reads better when failure is common and cheap to test."""),

        H("A debugging method that works"),
        P("""
        - **Reproduce** it: find the smallest input that fails, every time.
        - **Read** the error and the line it points to before you change anything.
        - **State your beliefs** about the values at that line, then check each one with a `print` or an `assert`. The bug lives where a belief turns out false.
        - **Bisect**: put a print halfway through. Is the value already wrong there? Search the half where it goes wrong, and repeat.
        - **Change one thing** at a time, then run again.
        - **Explain** the problem aloud to a rubber duck or a friend. Putting it into words exposes wrong assumptions surprisingly often."""),
        CODE("""
        def total_price(prices, tax_rate):
            total = 0
            for p in prices:
                total += p
                print("debug: p =", p, "total =", total)
            return total * (1 + tax_rate)

        print(total_price([10, 20], 0.5))
        """),
        P("""
        Print debugging is crude but effective: show the values your beliefs depend on, and remove the debug lines when you finish. Later you will meet real debuggers that pause a running program so you can inspect it."""),

        H("Logic errors and tests"),
        P("""
        A logic error gives a wrong answer without any message, so the defence is tests. Write down examples with known answers, including **edge cases**: empty input, one item, zero, negatives, very large values and duplicates. Most bugs hide at the edges."""),
        CODE("""
        def average(values):
            return sum(values) / len(values)

        assert average([2, 4, 6]) == 4
        assert average([5]) == 5
        try:
            average([])
        except ZeroDivisionError:
            print("the empty list is an unhandled edge case")
        """),
        P("""
        That last case is a design decision. Should `average([])` return `0`, return `None`, or raise a clearer error? Decide, write it in the docstring, and test it."""),
    ],
    exercises=[
        EX("safe_int", "safe_int",
           'Write `safe_int(text, default=0)` that returns `int(text)`, or `default` when the text cannot be converted.',
           "def safe_int(text, default=0):\n    pass\n",
           """
           f = ns.get("safe_int")
           check("defines safe_int", lambda: callable(f))
           check('"42" gives 42', lambda: f("42") == 42)
           check('"x" gives the default 0', lambda: f("x") == 0)
           check("custom default", lambda: f("x", -1) == -1)
           check("surrounding spaces are fine", lambda: f(" 7 ") == 7)
           check('"3.5" is not a whole number', lambda: f("3.5") == 0)
           """,
           "Put int(text) in a try block and catch ValueError.",
           "def safe_int(text, default=0):\n    try:\n        return int(text)\n    except ValueError:\n        return default"),
        EX("safe_divide", "safe_divide",
           "Write `safe_divide(a, b)` that returns `a / b`, or `None` when `b` is zero.",
           "def safe_divide(a, b):\n    pass\n",
           """
           f = ns.get("safe_divide")
           check("defines safe_divide", lambda: callable(f))
           check("10 / 4 is 2.5", lambda: f(10, 4) == 2.5)
           check("division by zero gives None", lambda: f(1, 0) is None)
           check("zero numerator", lambda: f(0, 5) == 0)
           """,
           "Catch ZeroDivisionError.",
           "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None"),
        EX("parse_age", "parse_age",
           'Write `parse_age(text)` that returns the age as an int. It must raise `ValueError` if the text is not a whole number, or if the age is below 0 or above 150.',
           "def parse_age(text):\n    pass\n",
           """
           f = ns.get("parse_age")
           def raises(fn, exc):
               try:
                   fn()
               except exc:
                   return True
               except BaseException:
                   return False
               return False
           check("defines parse_age", lambda: callable(f))
           check('"30" gives 30', lambda: f("30") == 30)
           check('"abc" raises ValueError', lambda: raises(lambda: f("abc"), ValueError))
           check('"-1" raises ValueError', lambda: raises(lambda: f("-1"), ValueError))
           check('"200" raises ValueError', lambda: raises(lambda: f("200"), ValueError))
           check('"0" and "150" are allowed', lambda: f("0") == 0 and f("150") == 150)
           """,
           "int(text) already raises ValueError for non-numbers. Add your own raise for the range check.",
           'def parse_age(text):\n    age = int(text)\n    if age < 0 or age > 150:\n        raise ValueError("age out of range")\n    return age'),
        EX("first_valid", "first_valid",
           'Write `first_valid(texts)` that returns the first item of the list that converts to an int (as an int), or `None` if none of them do. `first_valid(["x", "y", "12", "7"])` is 12.',
           "def first_valid(texts):\n    pass\n",
           """
           f = ns.get("first_valid")
           check("defines first_valid", lambda: callable(f))
           check("finds 12", lambda: f(["x", "y", "12", "7"]) == 12)
           check("none valid gives None", lambda: f(["a", "b"]) is None)
           check("empty list gives None", lambda: f([]) is None)
           check("first item valid", lambda: f(["5", "x"]) == 5)
           """,
           "Loop over the texts. In each pass try int(text) and return it. In the except branch do nothing and move on.",
           "def first_valid(texts):\n    for text in texts:\n        try:\n            return int(text)\n        except ValueError:\n            pass\n    return None"),
        EX("average", "Hunt two bugs",
           """
           `average(values)` should return the average of a list, or 0 for an empty list. It has two bugs: one gives wrong answers for normal lists, and the other crashes on an empty list. Fix both.""",
           'def average(values):\n    """Average of a list; 0 for an empty list."""\n    total = 0\n    for i in range(1, len(values)):\n        total += values[i]\n    return total / len(values)\n',
           """
           f = ns.get("average")
           check("defines average", lambda: callable(f))
           check("average([2, 4, 6]) is 4", lambda: f([2, 4, 6]) == 4, "Does the loop visit every item, including the first?")
           check("average([5]) is 5", lambda: f([5]) == 5)
           check("average([1, 2]) is 1.5", lambda: f([1, 2]) == 1.5)
           check("average([]) is 0", lambda: f([]) == 0, "Handle the empty list before dividing.")
           """,
           "range(1, ...) skips index 0. And an empty list makes len(values) zero.",
           'def average(values):\n    if not values:\n        return 0\n    return sum(values) / len(values)', kind="fix"),
        EX("find_max", "Fix the edge case",
           """
           `find_max(nums)` should return the largest number, and raise `ValueError` for an empty list. It gives the wrong answer when every number is negative. Fix it, and add the empty-list behaviour.""",
           "def find_max(nums):\n    best = 0\n    for n in nums:\n        if n > best:\n            best = n\n    return best\n",
           """
           f = ns.get("find_max")
           def raises(fn, exc):
               try:
                   fn()
               except exc:
                   return True
               except BaseException:
                   return False
               return False
           check("defines find_max", lambda: callable(f))
           check("find_max([3, 9, 2]) is 9", lambda: f([3, 9, 2]) == 9)
           check("all negative numbers", lambda: f([-5, -2, -9]) == -2, "Starting best at 0 is wrong when every number is below 0.")
           check("single item", lambda: f([7]) == 7)
           check("empty list raises ValueError", lambda: raises(lambda: f([]), ValueError))
           """,
           "Start best at nums[0] instead of 0, after checking that the list is not empty.",
           'def find_max(nums):\n    if not nums:\n        raise ValueError("empty list")\n    best = nums[0]\n    for n in nums:\n        if n > best:\n            best = n\n    return best', kind="fix"),
    ],
    predict=[
        PRED('try:\n    print(int("12"))\n    print(int("x1"))\n    print("after")\nexcept ValueError:\n    print("bad number")\nfinally:\n    print("done")',
             "The first print works. `int(\"x1\")` raises ValueError, so `after` is skipped, the except clause runs, and `finally` always runs last."),
        PRED('def f():\n    try:\n        return "try"\n    finally:\n        print("cleanup")\n\nprint(f())',
             "`finally` runs before the function actually returns, so `cleanup` is printed first, and then the returned text is printed."),
        PRED('try:\n    print([1, 2, 3][3])\nexcept (IndexError, KeyError):\n    print("lookup failed")\nelse:\n    print("fine")',
             "Index 3 does not exist in a three-item list, so IndexError is raised and `else` is skipped."),
        PRED('def check(n):\n    if n < 0:\n        raise ValueError("negative")\n    return n\n\nfor v in [1, -1, 2]:\n    try:\n        print(check(v))\n    except ValueError as err:\n        print("error:", err)',
             "The loop keeps going because the exception is handled inside it. Only -1 triggers the except clause."),
    ],
    cards=[
        CARD("Syntax error, runtime error and logic error: what is the difference?", "Syntax: invalid code, nothing runs. Runtime: an exception stops the program at a line. Logic: it runs but gives the wrong answer, with no message."),
        CARD("How do you read a traceback?", "From the bottom: error type and message, then the failing line, then the chain of calls. Find the deepest line in your own code."),
        CARD("`TypeError` versus `ValueError`?", "TypeError: the wrong kind of value for the operation. ValueError: the right kind but an unusable value, like `int(\"x\")`."),
        CARD("What do `else` and `finally` do in a try statement?", "`else` runs only if no exception happened. `finally` always runs, which suits cleanup."),
        CARD("Why avoid a bare `except:`?", "It hides every error, including typos and bugs. Catch the narrowest specific exception you can handle."),
        CARD("How do you signal an error from your own function?", "`raise ValueError(\"clear message\")`. Fail early with a message that says what was wrong."),
        CARD("EAFP versus LBYL?", "EAFP: try it and handle the exception. LBYL: check conditions before acting. Python favours EAFP."),
        CARD("What is a good debugging routine?", "Reproduce with a small input, read the error, check your beliefs with prints or asserts, bisect the code, change one thing at a time."),
        CARD("Which edge cases should you test?", "Empty input, one item, zero, negative numbers, duplicates and very large values."),
    ],
)
