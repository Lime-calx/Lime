from dsl import *

LESSON = lesson(
    id="py08", track="py", n=8, title="Errors, exceptions and debugging", minutes=70,
    summary="Reading tracebacks, handling and raising exceptions, a repeatable debugging method, and testing edge cases.",
    goals=[
        "Tell syntax, runtime and logic errors apart",
        "Read a multi-level traceback and find the line to investigate",
        "Use try, except, else and finally, and catch specific exceptions",
        "Raise your own exceptions with clear messages, and follow them up through the callers",
        "Follow a debugging method instead of guessing",
    ],
    blocks=[
        H("Three kinds of mistake"),
        P("""
        - **Syntax errors**: the text is not valid Python. Python reports them before anything runs, not even the first line.
        - **Runtime errors** (exceptions): the code is valid, but something fails while it runs. The program stops at that line.
        - **Logic errors**: the program runs and finishes but gives the wrong answer. There is no message at all, which makes these the hardest."""),
        CODE("""
        print("start")
        numbers = [1, 2, 3]
        print(numbers[5])
        print("never printed")
        """),

        H("Reading a traceback"),
        CODE("""
        def average(values):
            return sum(values) / len(values)

        def report(values):
            return "average: " + str(average(values))

        print(report([4, 6]))
        print(report([]))
        """),
        P("""
        Lime's error box shows the last line of the report and the deepest line of your code. A terminal prints the whole **traceback**, one entry per function call that was still running, oldest first ("most recent call last"). If the program above were saved as `clinic.py`, it would print:

        - `Traceback (most recent call last):`
        - `File "clinic.py", line 8, in <module>`: `print(report([]))`
        - `File "clinic.py", line 5, in report`: `return "average: " + str(average(values))`
        - `File "clinic.py", line 2, in average`: `return sum(values) / len(values)`
        - `ZeroDivisionError: division by zero`"""),
        P("""
        Read it in this order. First the **last line**: what went wrong (`ZeroDivisionError`) and the message. Then the **entry just above it**: the line that actually failed (line 2, inside `average`). Then walk **up** the chain to see how you got there: `report` called `average` (line 5), and the main program called `report([])` (line 8). `<module>` means the top level of the file, outside any function."""),
        NOTE("tip", """
        The deepest line of your own code is where to look first, but it is often not where the bug is. `average` divided correctly; the real question is why it was handed an empty list, and the answer is two entries higher, at line 8. Ask "where did this bad value come from?" and follow the chain upward."""),

        H("Common exception types"),
        P("""
        - `SyntaxError`, `IndentationError`: invalid code layout
        - `NameError`: a name Python does not know
        - `TypeError`: the wrong type for an operation, or the wrong number of arguments
        - `ValueError`: the right type but an unusable value, like `int("x")`, or unpacking the wrong number of parts
        - `IndexError`, `KeyError`: a missing position or key
        - `ZeroDivisionError`: dividing by zero
        - `AttributeError`: the object has no such attribute or method
        - `FileNotFoundError`: opening a file that is not there
        - `AssertionError`: an `assert` failed
        - `RecursionError`: too many nested calls"""),
        CODE("""
        time, coins = "06:15,7".split(",")
        print(time, coins)
        parts = "06:15,7,9".split(",")
        print(parts, len(parts))
        time, coins = parts
        """),
        P("""
        Unpacking needs exactly as many names as there are parts. Two names and three parts raises `ValueError: too many values to unpack`; one part raises `not enough values to unpack`. When you split text you did not write yourself (a log line, a CSV row), expect this error."""),

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
        Code in `try` runs normally. If it raises an exception that matches an `except` clause, Python jumps to that clause instead of crashing; the rest of the `try` block is skipped. Catch the **specific** exceptions you expect and know how to handle."""),
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
        `else` runs only when no exception happened. Put the risky line in `try` and the follow-up work in `else`, so an error in the follow-up is not mistaken for the one you meant to catch. `finally` runs no matter what, even after a `return`, which makes it the right place for cleanup such as closing a file."""),
        NOTE("trap", """
        Never write a bare `except:` or `except Exception: pass` as a quick fix. The error disappears, the bug stays, and you lose the only clue you had. A bare `except:` even hides a typo in a variable name (a `NameError`). Catch the narrowest exception, then handle it or let it continue upward."""),

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
        `raise` signals that a function cannot do its job and stops it on the spot: no later line of the function runs. Fail early with a clear message instead of letting a bad value travel and cause a confusing error far away."""),
        P("""
        Three new tools appear here. `isinstance(age, int)` asks "is `age` an int?" and gives `True` or `False`. `except (ValueError, TypeError) as error` catches either type and names the exception object `error`; printing it, or `str(error)`, gives its message. `type(error).__name__` is the name of its type as text, such as `"ValueError"`."""),
        NOTE("deep", """
        `isinstance(True, int)` is `True`, because `bool` is a kind of `int` in Python, so a strict check for whole numbers also needs `not isinstance(age, bool)`. Inside an `except` block, a bare `raise` re-raises the exception you caught, which is handy when you want to log something and still let it continue upward."""),

        H("Exceptions travel up through the callers"),
        CODE("""
        def read_dose(text):
            print("reading", text)
            dose = int(text)
            print("read", dose)
            return dose

        def total_dose(texts):
            total = 0
            for t in texts:
                total += read_dose(t)
            return total

        try:
            print(total_dose(["5", "10"]))
            print(total_dose(["5", "ten"]))
        except ValueError as err:
            print("could not total:", err)
        """),
        P("""
        An exception stops the function where it happens and leaves it, then leaves the function that called it, and so on up the chain, until an `except` that matches catches it. Nothing in between runs: not the rest of `read_dose`, not the rest of the loop in `total_dose`. If nothing catches it, the program stops and prints the traceback. Catch it at the level that knows what to do about it; here, only the top level knows that one bad dose means "report and stop"."""),
        NOTE("model", """
        Two styles. **LBYL**, "look before you leap", checks first: `if text.isdigit(): n = int(text)`. **EAFP**, "easier to ask forgiveness than permission", just tries and catches the failure: `try: n = int(text)` then `except ValueError:`. Python code often prefers EAFP because the check and the action cannot disagree: `isdigit()` rejects `"-3"` and `" 7"`, which `int()` happily accepts. LBYL is fine when the check is simple and exact, such as `if not values:` before dividing. When a Lime task says "use try/except", it is practising EAFP and checks for a `try` statement; otherwise any correct approach passes."""),

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
           'Write `safe_int(text, default=0)` that returns `int(text)`, or `default` when the text cannot be converted. Use try/except (EAFP).',
           "def safe_int(text, default=0):\n    pass\n",
           """
           f = ns.get("safe_int")
           check("defines safe_int", lambda: callable(f))
           check_eq('"42" gives 42', lambda: f("42"), 42)
           check_eq('"x" gives the default 0', lambda: f("x"), 0, "Catch the ValueError that int() raises and return default.")
           check_eq("custom default", lambda: f("x", -1), -1, "Return the default you were given, not 0.")
           check_eq("surrounding spaces are fine", lambda: f(" 7 "), 7, "int() itself ignores surrounding spaces; let it decide.")
           check_eq('"-3" gives -3', lambda: f("-3"), -3, "isdigit() rejects the minus sign, but int() accepts it. Let int() decide.")
           check_eq('"3.5" is not a whole number', lambda: f("3.5"), 0)
           check("uses try/except", lambda: has_node("Try"), "This exercise practises EAFP: try int(text), catch ValueError.")
           """,
           "Put int(text) in a try block and catch ValueError.",
           "def safe_int(text, default=0):\n    try:\n        return int(text)\n    except ValueError:\n        return default"),
        EX("safe_divide", "safe_divide",
           "Write `safe_divide(a, b)` that returns `a / b`, or `None` when `b` is zero. Use try/except.",
           "def safe_divide(a, b):\n    pass\n",
           """
           f = ns.get("safe_divide")
           check("defines safe_divide", lambda: callable(f))
           check_eq("10 / 4 is 2.5", lambda: f(10, 4), 2.5)
           check_eq("division by zero gives None", lambda: f(1, 0), None, "Catch ZeroDivisionError and return None.")
           check_eq("zero numerator", lambda: f(0, 5), 0.0)
           check_eq("negative divisor", lambda: f(9, -3), -3.0)
           check("uses try/except", lambda: has_node("Try"), "This exercise practises EAFP: try a / b, catch ZeroDivisionError.")
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
           check_eq('"30" gives 30', lambda: f("30"), 30)
           check('"abc" raises ValueError', lambda: raises(lambda: f("abc"), ValueError), "int() already raises ValueError for text that is not a number: let it.")
           check('"-1" raises ValueError', lambda: raises(lambda: f("-1"), ValueError), "Add your own raise ValueError(...) for the range check.")
           check('"200" raises ValueError', lambda: raises(lambda: f("200"), ValueError))
           check_eq('"0" is allowed', lambda: f("0"), 0, "0 is inside the range: use < 0, not <= 0.")
           check_eq('"150" is allowed', lambda: f("150"), 150, "150 is inside the range: use > 150, not >= 150.")
           check('"" raises ValueError', lambda: raises(lambda: f(""), ValueError))
           """,
           "int(text) already raises ValueError for non-numbers. Add your own raise for the range check.",
           'def parse_age(text):\n    age = int(text)\n    if age < 0 or age > 150:\n        raise ValueError("age out of range")\n    return age'),
        EX("first_valid", "first_valid",
           'Write `first_valid(texts)` that returns the first item of the list that converts to an int (as an int), or `None` if none of them do. `first_valid(["x", "y", "12", "7"])` is 12. Use try/except.',
           "def first_valid(texts):\n    pass\n",
           """
           f = ns.get("first_valid")
           check("defines first_valid", lambda: callable(f))
           check_eq("finds 12", lambda: f(["x", "y", "12", "7"]), 12)
           check_eq("none valid gives None", lambda: f(["a", "b"]), None, "After the loop, return None.")
           check_eq("empty list gives None", lambda: f([]), None)
           check_eq("first item valid", lambda: f(["5", "x"]), 5)
           check_eq("negative numbers count", lambda: f(["-", "-4", "9"]), -4)
           check("uses try/except", lambda: has_node("Try"), "Practise EAFP: try int(text) inside the loop.")
           """,
           "Loop over the texts. In each pass try int(text) and return it. In the except branch do nothing and move on.",
           "def first_valid(texts):\n    for text in texts:\n        try:\n            return int(text)\n        except ValueError:\n            pass\n    return None"),
        EX("traceback_read", "Read the traceback",
           """
           This program crashed on a ward round:

           ```
           1  def dose_per_kg(dose, weight):
           2      return dose / weight
           3
           4  def chart_line(patient):
           5      per_kg = dose_per_kg(patient["dose"], patient["weight"])
           6      return patient["name"] + ": " + str(per_kg)
           7
           8  ward = [{"name": "Bed 1", "dose": 500, "weight": 50},
           9          {"name": "Bed 2", "dose": 250, "weight": 0}]
           10 for p in ward:
           11     print(chart_line(p))
           ```

           The terminal showed:

           ```
           Bed 1: 10.0
           Traceback (most recent call last):
             File "ward.py", line 11, in <module>
               print(chart_line(p))
             File "ward.py", line 5, in chart_line
               per_kg = dose_per_kg(patient["dose"], patient["weight"])
             File "ward.py", line 2, in dose_per_kg
               return dose / weight
           ZeroDivisionError: division by zero
           ```

           Fill in the three answers: the exception's name as text, the line number where it was raised, and the name of the bed whose data caused it.""",
           'error_name = ""\nraised_line = 0\nbad_bed = ""\n',
           """
           check_eq("error_name", lambda: ns.get("error_name"), "ZeroDivisionError", "The last line of a traceback names the error; copy the name exactly, as text.")
           check_eq("raised_line", lambda: ns.get("raised_line"), 2, "The entry just above the last line is where it was raised: the deepest call, at the bottom of the chain.")
           check_eq("bad_bed", lambda: ns.get("bad_bed"), "Bed 2", "Bed 1 printed fine. Which patient has a weight of 0? The bug is in the data that line 11 passed down.")
           """,
           "Last line: the error's name. Just above it: the line that failed. Then look for the value that made it fail: which weight is 0?",
           'error_name = "ZeroDivisionError"\nraised_line = 2\nbad_bed = "Bed 2"'),
        EX("average", "Hunt two bugs",
           """
           `average(values)` should return the average of a list, or 0 for an empty list. It has two bugs: one gives wrong answers for normal lists, and the other crashes on an empty list. Fix both.""",
           'def average(values):\n    """Average of a list; 0 for an empty list."""\n    total = 0\n    for i in range(1, len(values)):\n        total += values[i]\n    return total / len(values)\n',
           """
           f = ns.get("average")
           check("defines average", lambda: callable(f))
           check_eq("average([2, 4, 6]) is 4", lambda: f([2, 4, 6]), 4.0, "Does the loop visit every item, including the first?")
           check_eq("average([5]) is 5", lambda: f([5]), 5.0)
           check_eq("average([1, 2]) is 1.5", lambda: f([1, 2]), 1.5)
           check_eq("average([-3, 3, 9]) is 3", lambda: f([-3, 3, 9]), 3.0)
           check("average([]) is 0", lambda: f([]) == 0, "Handle the empty list before dividing: if not values: return 0.")
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
           check_eq("find_max([3, 9, 2]) is 9", lambda: f([3, 9, 2]), 9)
           check_eq("all negative numbers", lambda: f([-5, -2, -9]), -2, "Starting best at 0 is wrong when every number is below 0.")
           check_eq("single item", lambda: f([7]), 7)
           check_eq("largest first", lambda: f([8, 1, 3]), 8)
           check("empty list raises ValueError", lambda: raises(lambda: f([]), ValueError), "Before the loop: if not nums: raise ValueError(\\"empty list\\").")
           """,
           "Start best at nums[0] instead of 0, after checking that the list is not empty.",
           'def find_max(nums):\n    if not nums:\n        raise ValueError("empty list")\n    best = nums[0]\n    for n in nums:\n        if n > best:\n            best = n\n    return best', kind="fix"),
    ],
    predict=[
        PRED('try:\n    print(int("12"))\n    print(int("x1"))\n    print("after")\nexcept ValueError:\n    print("bad number")\nfinally:\n    print("done")',
             "The first print works. `int(\"x1\")` raises ValueError, so `after` is skipped, the except clause runs, and `finally` always runs last.",
             traps={"12\nbad number\nafter\ndone": "Once a line in `try` raises, the rest of the `try` block is skipped.",
                    "12\nbad number": "`finally` always runs, whether or not there was an exception."}, id="p0"),
        PRED('def f():\n    try:\n        return "try"\n    finally:\n        print("cleanup")\n\nprint(f())',
             "`finally` runs before the function actually returns, so `cleanup` is printed first, and then the returned text is printed.",
             traps={"try\ncleanup": "`print(f())` can only print after `f` has finished, and `finally` runs before `f` finishes."}, id="p1"),
        PRED('try:\n    print([1, 2, 3][3])\nexcept (IndexError, KeyError):\n    print("lookup failed")\nelse:\n    print("fine")',
             "Index 3 does not exist in a three-item list, so IndexError is raised and `else` is skipped.",
             traps={"lookup failed\nfine": "`else` runs only when the `try` block raised nothing.",
                    "3": "Positions start at 0, so a three-item list has positions 0, 1 and 2."}, id="p2"),
        PRED('def check(n):\n    if n < 0:\n        raise ValueError("negative")\n    return n\n\nfor v in [1, -1, 2]:\n    try:\n        print(check(v))\n    except ValueError as err:\n        print("error:", err)',
             "The loop keeps going because the exception is handled inside it. Only -1 triggers the except clause, and printing the exception shows its message.",
             traps={"1\nerror: negative": "The `try` is inside the loop, so after handling -1 the loop carries on with 2.",
                    "1\nerror: ValueError\n2": "Printing an exception shows its message. `type(err).__name__` would give the name."}, id="p3"),
        PRED('for line in ["a,1", "b", "c,2,3"]:\n    try:\n        name, n = line.split(",")\n        print(name, n)\n    except ValueError:\n        print("bad:", line)',
             "`\"b\"` splits into one part and `\"c,2,3\"` into three. Unpacking into two names needs exactly two parts, so both raise ValueError.",
             traps={"a 1\nbad: b\nc 2": "Extra parts are not dropped: three parts into two names raises ValueError.",
                    "a 1\nb\nbad: c,2,3": "Too few parts is also an error: one part cannot fill two names."}, id="p-unpack"),
        PRED('def load(text):\n    try:\n        return int(text)\n    finally:\n        print("closing", text)\n\ntry:\n    print(load("5"))\n    print(load("x"))\nexcept ValueError:\n    print("caller caught it")',
             "`load` has no `except`, so the ValueError from `int(\"x\")` leaves the function, but its `finally` still runs on the way out. The caller's `except` catches it, and the second print never happens.",
             traps={"closing 5\n5\ncaller caught it": "`finally` runs even when an exception is leaving the function.",
                    "5\nclosing 5\nclosing x\ncaller caught it": "`finally` runs before the value is handed back, so `closing 5` comes before 5 is printed."}, id="p-pass-out"),
        PRED('def take(n):\n    if n < 0:\n        raise ValueError("negative")\n    print("taking", n)\n    return n\n\ntotal = 0\nfor n in [2, -1, 3]:\n    try:\n        total += take(n)\n    except ValueError as err:\n        print("skipped:", err)\n    else:\n        print("total now", total)',
             "`raise` stops `take` at once, so `taking -1` never prints, and `total` is not changed. `else` runs only for the passes with no exception.",
             traps={"taking 2\ntotal now 2\ntaking -1\nskipped: negative\ntaking 3\ntotal now 5": "`raise` stops the function on the spot; the print after it never runs.",
                    "taking 2\ntotal now 2\nskipped: negative\ntotal now 2\ntaking 3\ntotal now 5": "`else` is skipped when the `try` block raised an exception."}, id="p-raise-else"),
    ],
    cards=[
        CARD("A program runs to the end with no error message but prints the wrong dose. Which kind of error is it?", "A logic error. Only tests with known answers catch it.", id="c0"),
        CARD('Line 1 is `print("start")`; line 5 is missing a closing bracket. Is `start` printed?', "No. A SyntaxError is reported before any line runs.", id="c-syntax-first"),
        CARD("A traceback has three `File ...` entries: line 9 in `<module>`, line 4 in `report`, line 2 in `average`. Which line failed, and where do you look for the cause?", "Line 2 (the entry just above the error line) is where it failed. Then walk up: the bad value usually came from a caller, line 4 or line 9.", id="c-tb-multi"),
        CARD('`int("seven")` raises which exception, and why not TypeError?', "ValueError: a string is the right type for `int()`, but this string's content cannot be converted.", id="c2"),
        CARD("When does the `else` of a try statement run?", "Only when the `try` block raised no exception.", id="c3"),
        CARD('`def f():` / `try: return 1` / `finally: print("bye")`. What does `print(f())` show?', "`bye` then `1`: `finally` runs before the function hands back its value.", id="c-finally"),
        CARD("What is wrong with `try: avg = sum(fares) / len(fare)` followed by `except: avg = 0`?", "The bare `except` also hides the typo `fare` (a NameError), turning a bug into a believable 0. Catch `ZeroDivisionError` only.", id="c4"),
        CARD("How do you stop your own function with a clear error when an age is negative?", '`raise ValueError("age cannot be negative")`. The function stops on that line.', id="c5"),
        CARD("Is `if b != 0: r = a / b` EAFP or LBYL?", "LBYL (look before you leap): check first, then act. EAFP would try `a / b` and catch ZeroDivisionError.", id="c6"),
        CARD('`a, b = "1,2,3".split(",")`?', "`ValueError: too many values to unpack`: three parts, two names.", id="c-unpack"),
        CARD("A function raises ValueError and has no `except`. Where does the exception go?", "Up to its caller, then that caller's caller, until a matching `except` catches it. If none does, the program stops with a traceback.", id="c-pass-out"),
        CARD("Your report is wrong for a 500-line input file. What is the first debugging step?", "Reproduce it with the smallest input that still fails, so every value can be seen.", id="c7"),
        CARD("You believe `total` is 30 after the loop, but the answer is wrong. What do you do before changing any code?", "Check the belief: print or assert `total` there. The bug lives where a belief turns out false.", id="c-dbg-belief"),
        CARD("A 40-line calculation ends with a wrong value. How do you find where it first goes wrong without checking every line?", "Bisect: print the value halfway. If it is already wrong, search the first half, otherwise the second. Repeat.", id="c-dbg-bisect"),
        CARD("You changed three things at once and the bug went away. What is the problem?", "You do not know which change fixed it, or whether another one broke something. Change one thing at a time.", id="c-dbg-one"),
        CARD("Your `average(values)` works on `[3, 1, 2]`. Name two other inputs you should test.", "For example the empty list `[]` and a single item `[5]`. Negatives, zeros and duplicates are good too.", id="c8"),
    ],
)
