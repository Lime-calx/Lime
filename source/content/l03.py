from dsl import *

LESSON = lesson(
    id="py03", track="py", n=3, title="Decisions and loops", minutes=75,
    summary="Booleans, comparisons, if/elif/else, while and for loops, and the loop patterns you will use every day: accumulator, counter, running maximum and search with break.",
    goals=[
        "Build conditions with comparisons, and, or and not, and know which runs first",
        "Know which values are truthy and falsy",
        "Choose between while and for, and write both correctly",
        "Use accumulators, counters, running maximums, break, continue and for/else",
    ],
    blocks=[
        H("Booleans and comparisons"),
        P("""
        A `bool` is `True` or `False`. Comparison operators produce booleans: `==` equal, `!=` not equal, `<`, `<=`, `>`, `>=`. Python also allows **chained** comparisons: `1 < x < 10` means `1 < x and x < 10`."""),
        CODE("""
        x = 7
        print(x == 7, x != 7, x > 10)
        print(1 < x < 10)
        """),
        NOTE("trap", """
        `=` assigns and `==` compares. Writing `if x = 5:` is a SyntaxError in Python, which protects you from a bug that is common in other languages. Types matter too: `"10" == 10` is False, because a string is never equal to a number."""),

        H("Comparing text"),
        P("""
        Strings compare **character by character**, from the left, using each character's code number. The first difference decides. In those codes the digits come first, then all capital letters, then all lower-case letters. So `"Zebra" < "apple"` is True, and digits inside text compare as characters, not as numbers."""),
        CODE("""
        print("apple" < "banana")   # a comes before b
        print("Zebra" < "apple")    # every capital comes before every lower-case letter
        print("10" < "9")           # "1" is compared with "9" first
        print(10 < 9)               # real numbers compare by size
        """),
        NOTE("trap", """
        Numbers that arrive as text (from a file, a form or a lab export) sort and compare wrongly: `"10" < "9"` is True. Convert first with `int(...)` or `float(...)`, then compare."""),

        H("and, or, not"),
        P("""
        `and` is true when both sides are, `or` when at least one is, and `not` flips a value. When they are mixed, Python works in this order: arithmetic first, then comparisons, then `not`, then `and`, then `or`. So `not x == 5` means `not (x == 5)`, and `a or b and c` means `a or (b and c)`."""),
        CODE("""
        age = 20
        print(age >= 18 and age < 65)
        x = 0
        print(not x == 5, (not x) == 5)
        print(True or False and False)
        """),
        P("""
        They also **short-circuit**: Python stops as soon as the answer is known, and the result is the last value it looked at, which is not always a bool. `or` gives the first truthy value; `and` gives the first falsy one (or the last value if all are truthy). `name or "guest"` is a common idiom for a fallback value."""),
        CODE("""
        print(0 or "fallback")
        print(3 and 4)
        print("" or "default name")
        """),
        NOTE("trap", """
        `if x == 1 or 2:` does not mean "x is 1 or 2". It means `(x == 1) or 2`, and `2` is always truthy, so the condition is always true. Write `x == 1 or x == 2`, or `x in (1, 2)`."""),
        NOTE("deep", """
        Short-circuiting is also a guard. In `count > 0 and total / count > 10` the division only runs when `count > 0` is true, so it can never divide by zero. Swap the two sides and it can crash. Also, `True` and `False` behave as the numbers 1 and 0 in arithmetic, so `True + True` is 2: adding up conditions counts how many are true."""),

        H("Truthiness"),
        P("""
        In an `if`, any value can act as a condition. These are **falsy**: `False`, `None`, `0`, `0.0`, the empty string `""`, and empty collections such as `[]`. Everything else is **truthy**. (`None` is Python's value for "nothing here"; you will meet it often from the next lesson on.)"""),
        CODE("""
        print(bool(0), bool(1), bool(""), bool("0"), bool(None), bool([]), bool([0]))
        """),
        P("""
        The text `"0"` is truthy, because it is a non-empty string, and so is `[0]`, because the list is not empty. To ask whether something is `None`, write `x is None` (or `x is not None`), not `x == None`."""),
        NOTE("deep", """
        `is` asks "is this the very same object?", while `==` asks "are these equal?". There is only one `None` object, so `is None` is exact, and it cannot be fooled by a value that defines its own odd idea of equality. Use `is` only for `None` (and `True`/`False` in rare cases); for numbers and text always use `==`."""),

        H("Making decisions with if"),
        P("""
        `if` runs a block only when its condition is truthy. The block is the indented lines under the colon, and **indentation is syntax** in Python: use 4 spaces. `elif` adds more conditions and `else` catches the rest. Only the first matching branch runs."""),
        CODE("""
        score = 72
        if score >= 90:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        else:
            grade = "F"
        print(grade)
        """),
        NOTE("tip", """
        Order matters in an `elif` chain, because the first true condition wins. If the chain above tested `score >= 50` first, everyone who passed would get a C."""),
        P("""
        Separate `if` statements are **not** a chain: each one is tested on its own, and an `else` belongs only to the `if` directly above it."""),
        CODE("""
        temp = 39.4
        if temp >= 38:
            print("fever")
        if temp >= 39:
            print("high fever")      # also runs: a separate if

        if temp >= 38:
            print("fever")
        elif temp >= 39:
            print("high fever")      # never runs: the first branch already matched
        """),

        H("Repeating with while"),
        P("""
        `while` repeats a block as long as its condition is truthy. The condition is checked before every pass. The body must change something so the condition eventually becomes false, or the loop runs forever."""),
        CODE("""
        n = 1
        while n <= 5:
            print(n)
            n += 1
        print("done, n is", n)
        """),
        NOTE("trap", """
        The classic infinite loop is forgetting the update (`n += 1`). Lime tries to stop runaway loops after a few seconds, but ordinary Python keeps going until you interrupt it."""),
        P("""
        A `while` loop fits when you do not know in advance how many repetitions you need, for example "keep halving until the number is small enough"."""),
        CODE("""
        size = 1000
        halvings = 0
        while size > 1:
            size = size // 2
            halvings += 1
        print(halvings)
        """),

        H("Repeating with for and range"),
        P("""
        `for` runs the body once for each item in a sequence. `range(stop)` produces 0, 1, ... up to `stop - 1`. `range(start, stop)` begins at `start`, and `range(start, stop, step)` moves by `step`. The stop value is **never included**."""),
        CODE("""
        for i in range(5):
            print(i)
        print("--")
        for i in range(2, 10, 3):
            print(i)
        print("--")
        for i in range(5, 0, -1):
            print(i)
        """),
        NOTE("model", """
        Include the start, exclude the stop. With the usual step of 1 and a stop at least as big as the start, `range(a, b)` gives exactly `b - a` numbers, and `range(0, 3)` followed by `range(3, 6)` covers 0 to 5 with no gap and no overlap. If the stop is already past the start, the range is simply empty: `range(5, 2)` gives nothing, and counting down needs a negative step, `range(5, 2, -1)`."""),
        P("""
        A `for` loop can also walk through text, one character per pass, and through a **list** of values. A list is written in square brackets, like `[36.6, 38.1, 37.2]`; lesson 6 covers lists in full."""),
        CODE("""
        for ch in "lime":
            print(ch * 3)
        for reading in [36.6, 38.1, 37.2]:
            print("temp", reading)
        """),
        P("""
        The loop variable is an ordinary name. Each pass, `for` points it at the next item, whatever you did to it inside the body, and after the loop it keeps its last value."""),
        CODE("""
        for i in range(3):
            print("pass", i)
            i = 100          # does not skip anything: the next pass sets i again
        print("after the loop i is", i)
        """),

        H("Patterns you will use constantly"),
        P("""
        An **accumulator** builds up a result one step at a time. A **counter** counts how many items meet a condition. Both start *before* the loop."""),
        CODE("""
        total = 0
        for n in range(1, 101):
            total += n
        print(total)

        evens = 0
        for n in range(1, 101):
            if n % 2 == 0:
                evens += 1
        print(evens)
        """),
        P("""
        A **running maximum** keeps the best value seen so far. Start it from the first real value, not from 0: if every reading is negative, a start of 0 would win and be wrong."""),
        CODE("""
        freezer = [-21, -18, -25, -19]
        warmest = freezer[0]          # [0] means the first item of the list
        for t in freezer:
            if t > warmest:
                warmest = t
        print(warmest)
        """),

        H("break, continue and for/else"),
        P("""
        `break` leaves the loop at once. `continue` skips the rest of this pass and starts the next. In the examples below, `end=" "` makes `print` finish with a space instead of a new line, and a bare `print()` just ends the line."""),
        CODE("""
        for n in range(2, 30):
            if n % 7 == 0:
                print("first multiple of 7:", n)
                break

        for n in range(1, 8):
            if n % 2 == 0:
                continue
            print(n, end=" ")
        print()
        """),
        P("""
        A search often uses a **flag**: a bool that starts False and becomes True when the thing is found. Python also has a shortcut: a loop can have an `else` block, which runs only if the loop finished **without** a `break`. Read it as "no break"."""),
        CODE("""
        target = 23
        for n in range(2, 20):
            if n == target:
                print("found it")
                break
        else:
            print(target, "is not in the range")
        """),
        P("""
        When you do not know where the loop should stop, write `while True:` and leave with `break` from the middle. This is the shape for "keep going until something happens"."""),
        CODE("""
        dose = 1
        while True:
            dose = dose * 2
            if dose > 50:
                break
        print(dose)
        """),
        P("""
        In nested loops, the inner loop runs its whole cycle for each pass of the outer one, and `break` leaves only the **innermost** loop it is in."""),
        CODE("""
        for row in range(1, 4):
            for col in range(1, 4):
                if col > row:
                    break             # ends this row only
                print(row * col, end=" ")
            print()
        """),
        NOTE("deep", """
        `while` loops can have an `else` too, with the same rule: it runs when the condition becomes false, but not after a `break`. Many programmers find `for`/`else` surprising, so a short comment such as `# no break` beside the `else` helps the next reader. To leave two loops at once, set a flag before `break` and test it in the outer loop, or (next lesson) put the loops in a function and `return`."""),
        NOTE("deep", """
        Avoid naming your own variables after built-in functions, such as `sum = 0` or `max = 5`. It works, but from then on `sum(...)` and `max(...)` no longer mean the built-ins, and the error appears far from the cause. Use `total` and `biggest` instead."""),
    ],
    exercises=[
        EX("fizzbuzz", "FizzBuzz",
           """
           Print the numbers 1 to `last`, one per line. For multiples of 3 print `Fizz` instead, for multiples of 5 print `Buzz`, and for multiples of both print `FizzBuzz`. Keep the line `last = 15`: the checker changes it.""",
           "last = 15\n# FizzBuzz from 1 to last\n",
           """
           def ref(m):
               return ["FizzBuzz" if k % 15 == 0 else "Fizz" if k % 3 == 0 else "Buzz" if k % 5 == 0 else str(k) for k in range(1, m + 1)]
           check_eq("prints the 15 lines correctly", lambda: out.strip().split("\\n"), ref(15), "Test the multiple of both 3 and 5 first, then 3, then 5, then print the number.")
           check("uses a loop", lambda: has_node("For", "While"), "Use a for loop over range(1, last + 1) instead of separate print lines.")
           def other():
               ns2, out2 = rerun("last = 15", "last = 20")
               return out2.strip().split("\\n")
           check_eq("works when last is 20", other, ref(20), "Use the variable last in your range, and remember the stop value is not included.")
           """,
           "Loop `for n in range(1, last + 1):`. Test `n % 15 == 0` first, then 3, then 5, then fall back to the number.",
           """
           last = 15
           for n in range(1, last + 1):
               if n % 15 == 0:
                   print("FizzBuzz")
               elif n % 3 == 0:
                   print("Fizz")
               elif n % 5 == 0:
                   print("Buzz")
               else:
                   print(n)
           """),
        EX("multiples", "Multiples of 3 or 5",
           """
           Add up every whole number below `limit` that is a multiple of 3 or of 5, and leave the answer in `total`. (Below 10 the answer is 23.)""",
           "limit = 1000\ntotal = 0\n# add up the multiples below limit\n",
           """
           def ref(k):
               s = 0
               for n in range(k):
                   if n % 3 == 0 or n % 5 == 0:
                       s += n
               return s
           check_eq("total is correct for limit = 1000", lambda: ns["total"], ref(1000), "Loop over range(limit) and add n when it is a multiple of 3 or 5.")
           def other():
               n2, _ = rerun("limit = 1000", "limit = 50")
               return n2["total"]
           check_eq("works for other limits", other, ref(50), "Use the variable limit, not the number 1000.")
           """,
           "`n % 3 == 0 or n % 5 == 0`, and add each match to total.",
           """
           limit = 1000
           total = 0
           for n in range(limit):
               if n % 3 == 0 or n % 5 == 0:
                   total += n
           """),
        EX("collatz", "Collatz steps",
           """
           Start from `n`. While `n` is not 1: if it is even, halve it; otherwise triple it and add 1. Count the steps in `steps`. Starting at 6 the path is 6, 3, 10, 5, 16, 8, 4, 2, 1, which takes 8 steps.""",
           "n = 27\nsteps = 0\n# follow the Collatz rule and count the steps\n",
           """
           def ref(k):
               s = 0
               while k != 1:
                   k = k // 2 if k % 2 == 0 else 3 * k + 1
                   s += 1
               return s
           check_eq("steps is correct for n = 27", lambda: ns["steps"], ref(27), "Use a while loop that runs until n becomes 1, adding 1 to steps each pass.")
           def other():
               n2, _ = rerun("n = 27", "n = 97")
               return n2["steps"]
           check_eq("works for other starting values", other, ref(97), "Do not type the answer in; compute it from n.")
           """,
           "Inside the loop: if n % 2 == 0 then n = n // 2, else n = 3 * n + 1. Then add 1 to steps.",
           """
           n = 27
           steps = 0
           while n != 1:
               if n % 2 == 0:
                   n = n // 2
               else:
                   n = 3 * n + 1
               steps += 1
           """),
        EX("range", "Fix the range",
           "This prints 0 to 4. Change the loop so it prints 1 to `last`, one number per line. Keep the line `last = 5`: the checker changes it.",
           "last = 5\nfor i in range(last):\n    print(i)\n",
           """
           check_eq("prints 1 to 5, one per line", lambda: out.strip().split("\\n"), ["1", "2", "3", "4", "5"], "range(stop) starts at 0. Give it a start and a stop, and remember the stop is not included.")
           def other():
               ns2, out2 = rerun("last = 5", "last = 8")
               return out2.strip().split("\\n")
           check_eq("works when last is 8", other, [str(k) for k in range(1, 9)], "Build the stop from last: to include last itself, stop one past it.")
           check("still uses range", lambda: uses_call("range"), "Keep the for loop over a range; change only its start and stop.")
           """,
           "range(1, last + 1) gives 1, 2, ..., last.",
           "last = 5\nfor i in range(1, last + 1):\n    print(i)", kind="fix"),
        EX("triangle", "Star triangle",
           "Print a right triangle of stars with `rows` rows: one star on the first row, then two, and so on. Keep the line `rows = 4`: the checker changes it.",
           "rows = 4\n# print the triangle\n",
           """
           check_eq("prints the 4-row triangle", lambda: out.strip().split("\\n"), ["*", "**", "***", "****"], "Row k holds k stars. A string can be repeated with *.")
           check("uses a loop", lambda: has_node("For", "While"), "Use a loop: one pass per row.")
           def other():
               ns2, out2 = rerun("rows = 4", "rows = 6")
               return out2.strip().split("\\n")
           check_eq("works with 6 rows", other, ["*" * k for k in range(1, 7)], "Loop from 1 up to and including rows.")
           """,
           "`\"*\" * k` is k stars. Loop k from 1 to rows with range(1, rows + 1).",
           """
           rows = 4
           for row in range(1, rows + 1):
               print("*" * row)
           """),
        EX("square", "First square past the limit",
           "Find the smallest whole number whose square is greater than `limit`, and leave it in `answer`. For limit 50 the answer is 8, because 7 * 7 is 49 and 8 * 8 is 64.",
           "limit = 5000\nanswer = 1\n# grow answer until answer * answer is more than limit\n",
           """
           def ref(k):
               n = 1
               while n * n <= k:
                   n += 1
               return n
           check_eq("answer is correct for limit = 5000", lambda: ns["answer"], ref(5000), "Keep adding 1 while the square is still too small.")
           def other():
               n2, _ = rerun("limit = 5000", "limit = 100")
               return n2["answer"]
           check_eq("works for other limits", other, ref(100), "Use limit in your condition. For limit 100 the square must be MORE than 100, so 10 is not enough.")
           """,
           "`while answer * answer <= limit:` then `answer += 1`.",
           """
           limit = 5000
           answer = 1
           while answer * answer <= limit:
               answer += 1
           """),
        EX("prime", "Prime test with for/else",
           """
           `n` is a whole number of at least 2. Set `is_prime` to `True` if no number from 2 up to `n - 1` divides it exactly, and `False` otherwise. Use a `for` loop with `break` when you find a divisor, and the loop's `else` for the "no divisor found" case. Keep the line `n = 97`: the checker changes it.""",
           "n = 97\nis_prime = None\n# search for a divisor; use for ... else\n",
           """
           def ref(k):
               for d in range(2, k):
                   if k % d == 0:
                       return False
               return True
           check_eq("97 is prime", lambda: ns["is_prime"], True, "Set is_prime = True in the loop's else block (it runs only if no break happened).")
           for k in (2, 9, 91, 13):
               check_eq("works for n = %d" % k, lambda k=k: rerun("n = 97", "n = %d" % k)[0]["is_prime"], ref(k), "A divisor d means n % d == 0. For 2, range(2, 2) is empty, so the else runs and 2 is prime.")
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
           def has_for_else():
               import ast
               fors = [x for x in _nodes(ast.parse(code), []) if type(x).__name__ == "For"]
               return len([x for x in fors if getattr(x, "orelse", None)]) > 0
           check("uses for ... else", has_for_else, "Put else: at the same indentation as the for, not the if.")
           """,
           "`for d in range(2, n):` then `if n % d == 0:` set is_prime = False and break. Under the for (same indentation as for), `else:` sets is_prime = True.",
           """
           n = 97
           is_prime = None
           for d in range(2, n):
               if n % d == 0:
                   is_prime = False
                   break
           else:
               is_prime = True
           """),
        EX("largest", "Warmest reading, no max()",
           """
           Find the highest value in the list `readings` and leave it in `highest`, using a loop and a running maximum, without `max()` or `sorted()`. Keep the `readings = ...` line: the checker changes it, including to a freezer where every reading is below zero.""",
           "readings = [36.8, 38.4, 37.1, 39.0, 37.6]\nhighest = 0\n# loop over readings and keep the highest so far\n",
           """
           def other(line):
               return rerun("readings = [36.8, 38.4, 37.1, 39.0, 37.6]", line)[0]["highest"]
           check_eq("highest is 39.0", lambda: ns["highest"], 39.0, "Each pass: if the reading is bigger than highest, replace highest.")
           check_eq("works when the highest comes first", lambda: other("readings = [40.1, 36.0, 37.5]"), 40.1, "Compare every reading, including the first.")
           check_eq("works when every reading is negative", lambda: other("readings = [-21, -18, -25]"), -18, "Starting highest at 0 is the bug: 0 beats every negative reading. Start from readings[0].")
           check("no max() or sorted()", lambda: not uses_call("max") and not uses_call("sorted"), "Do it with the loop: that is the pattern being practised.")
           """,
           "Set `highest = readings[0]` before the loop, then `for r in readings:` and `if r > highest: highest = r`.",
           """
           readings = [36.8, 38.4, 37.1, 39.0, 37.6]
           highest = readings[0]
           for r in readings:
               if r > highest:
                   highest = r
           """),
        EX("repeat", "First doubled letter",
           """
           Find the first letter in `text` that is the same as the letter just before it, and leave it in `repeat`. If there is none, `repeat` stays `None`. For `"bookkeeper"` the answer is `"o"`, not `"k"` or `"e"`: stop at the first one with `break`. Keep the `text = ...` line: the checker changes it.""",
           'text = "bookkeeper"\nrepeat = None\n# remember the previous letter as you loop\n',
           """
           def other(t):
               return rerun('text = "bookkeeper"', "text = %r" % t)[0]["repeat"]
           check_eq('"bookkeeper" gives "o"', lambda: ns["repeat"], "o", "Keep a name prev for the letter before; if ch == prev you found a double.")
           check_eq('"abcdd" gives "d"', lambda: other("abcdd"), "d", "Compare each letter with the one before it.")
           check_eq('"lime" gives None', lambda: other("lime"), None, "Leave repeat as None when no letter repeats.")
           check_eq('"aabb" gives "a"', lambda: other("aabb"), "a", "Stop at the first double: break as soon as you find it.")
           check("uses break", lambda: has_node("Break"), "Leave the loop with break once you have the answer.")
           """,
           "Start `prev = None`. In `for ch in text:`, if `ch == prev`, set repeat = ch and break. At the end of each pass set `prev = ch`.",
           """
           text = "bookkeeper"
           repeat = None
           prev = None
           for ch in text:
               if ch == prev:
                   repeat = ch
                   break
               prev = ch
           """),
        EX("digits", "Digit sum",
           """
           Add up the digits of the whole number `n` and leave the answer in `total`. For 4096 that is 4 + 0 + 9 + 6 = 19. Work with numbers: `n % 10` is the last digit and `n // 10` drops it. Keep the line `n = 4096`: the checker changes it.""",
           "n = 4096\ntotal = 0\n# peel off the last digit until nothing is left\n",
           """
           def ref(k):
               s = 0
               while k > 0:
                   s += k % 10
                   k = k // 10
               return s
           check_eq("total is 19 for 4096", lambda: ns["total"], 19, "Each pass: add n % 10 to total, then n = n // 10.")
           for k in (7, 1000000, 98765):
               check_eq("works for n = %d" % k, lambda k=k: rerun("n = 4096", "n = %d" % k)[0]["total"], ref(k), "Loop while n > 0, so it works for any number of digits.")
           check("uses % and //", lambda: has_node("Mod") and has_node("FloorDiv"), "Use the arithmetic: % 10 gives the last digit, // 10 removes it.")
           """,
           "`while n > 0:` then `total += n % 10` and `n = n // 10`.",
           """
           n = 4096
           total = 0
           while n > 0:
               total += n % 10
               n = n // 10
           """),
    ],
    predict=[
        PRED("for i in range(4, 13, 4):\n    print(i)",
             "`range(4, 13, 4)` starts at 4 and steps by 4: 4, 8, 12. The next would be 16, which is past the stop.",
             traps={"4\n8": "12 is below the stop 13, so it is included; only values at or past the stop are left out."}, id="p0"),
        PRED('print(bool(""), bool("0"), bool([]), bool(None))',
             "Only the non-empty string `\"0\"` is truthy. Empty string, empty list and None are falsy.",
             traps={"False False False False": '"0" is a string with one character in it, so it is truthy; only the empty string is falsy.'}, id="p1"),
        PRED("x = 0\nprint(not x == 5, (not x) == 5)",
             "`not` runs after `==`, so `not x == 5` is `not (0 == 5)`, which is `not False`: True. With brackets, `not x` is `not 0`, which is True, and `True == 5` is False.",
             traps={"False False": "`not` binds more loosely than `==`: `not x == 5` means `not (x == 5)`.",
                    "True True": "With the brackets, `not x` is evaluated first: True, and True is not equal to 5."}, id="p2"),
        PRED('print("" or "guest", 5 and 0, None or 0)',
             "`or` returns the first truthy value, or the last value if none is truthy: `guest`, then `0` (None is falsy, so it moves on to 0). `and` returns the first falsy value: 0.",
             traps={"guest False False": "`and` and `or` return one of the values they looked at, not a new True or False.",
                    "True False False": "`and` and `or` return one of the values they looked at, not a new True or False."}, id="p3"),
        PRED("total = 0\nfor n in range(1, 5):\n    if n == 3:\n        continue\n    total += n\nprint(total)",
             "`continue` skips the rest of the pass for n = 3 only, so the total is 1 + 2 + 4 = 7.",
             traps={"3": "That would be `break`. `continue` skips only this pass and goes on with n = 4.",
                    "10": "`continue` jumps over `total += n` when n is 3, so 3 is never added."}, id="p4"),
        PRED("print(True or False and False)",
             "`and` runs before `or`: `False and False` is False, then `True or False` is True.",
             traps={"False": "`and` binds tighter than `or`, so this is `True or (False and False)`, not `(True or False) and False`."}, id="p-and-or"),
        PRED('print("Zebra" < "apple", "10" < "9", 10 < 9)',
             "Strings compare by character codes from the left. Capital Z comes before lower-case a, and the character \"1\" comes before \"9\". Only the real numbers compare by size.",
             traps={"False False False": "Text compares character by character by code: every capital comes before every lower-case letter, and \"1\" < \"9\" decides \"10\" < \"9\".",
                    "False True False": "Every capital letter has a smaller code than every lower-case letter, so \"Z\" < \"a\"."}, id="p-strcmp"),
        PRED('for i in range(5, 2):\n    print(i)\nprint("end")',
             "The stop (2) is already below the start (5), and the step is the default +1, so the range is empty and the body never runs.",
             traps={"5\n4\n3\nend": "range only counts down with a negative step: range(5, 2, -1). With the default step it is empty."}, id="p-range-empty"),
        PRED("for i in range(4):\n    if i == 1:\n        i = 3\n    print(i)",
             "Reassigning `i` changes it only for the rest of that pass. The `for` takes the next value from the range anyway: 0, then 3 (changed), then 2, then 3.",
             traps={"0\n3": "Changing i does not make the loop skip ahead: the for loop gives i the next value of the range each pass."}, id="p-loopvar"),
        PRED("for a in range(3):\n    for b in range(3):\n        if b == 1:\n            break\n        print(a, b)",
             "`break` leaves only the inner loop. The outer loop carries on, so each `a` prints once with b = 0.",
             traps={"0 0": "break ends only the innermost loop; the outer loop still runs for a = 1 and a = 2."}, id="p-break-inner"),
        PRED('t = 38.5\nif t >= 38:\n    print("fever")\nif t >= 39:\n    print("high fever")\nelse:\n    print("normal")',
             "These are two separate `if` statements. The first prints fever. The `else` belongs only to the second `if`, and 38.5 is below 39, so it prints normal too.",
             traps={"fever": "The else belongs to the second if only. The first if does not stop the second test from running."}, id="p-elif-vs-if"),
        PRED('for n in range(2, 5):\n    if n == 7:\n        break\nelse:\n    print("no break")\nprint(n)',
             "7 never comes up, so the loop ends normally and its `else` runs. The loop variable keeps its last value, 4.",
             traps={"4": "A loop's else runs when the loop finishes without break, which is what happened here.",
                    "no break\n5": "range(2, 5) stops before 5, and n keeps the last value it was given: 4."}, id="p-forelse"),
    ],
    cards=[
        CARD("What does the chained comparison `1 < x < 10` mean?", "`1 < x and x < 10`, evaluated with x only once.", id="c0"),
        CARD("`=` versus `==`?", "`=` assigns a value to a name. `==` compares two values and gives a bool.", id="c1"),
        CARD("What does `0 or \"fallback\"` evaluate to, and why?", "`\"fallback\"`. `or` returns the first truthy value it meets, or the last value if none is truthy.", id="c2"),
        CARD("Which numbers are falsy in Python?", "Only zero: `0` and `0.0`. Every other number, even `-1`, is truthy.", id="c3"),
        CARD("What is wrong with `if x == 1 or 2:`?", "It parses as `(x == 1) or 2`, and 2 is always truthy, so it is always true. Write `x == 1 or x == 2` or `x in (1, 2)`.", id="c4"),
        CARD("In an if/elif chain, which branch runs?", "Only the first one whose condition is true, so put the most specific tests first.", id="c5"),
        CARD("How many numbers does `range(2, 10)` give?", "8: the numbers 2 to 9. The stop is never included.", id="c6"),
        CARD("When do you choose `while` over `for`?", "When you do not know the number of repetitions in advance and loop until a condition changes.", id="c7"),
        CARD("A loop `for n in range(5):` has the body `if n == 2: break` followed by `print(n)`. What does it print?", "`0` then `1`. `break` leaves the loop at once when n is 2, before 2 is printed.", id="c8"),
        CARD("What is wrong? `for n in range(1, 4):` has the body `total = 0` then `total += n`, and `print(total)` comes after the loop.", "The accumulator is reset every pass, so it prints 3, not 6. Put `total = 0` before the loop.", id="c9"),
        CARD("A loop `for n in range(5):` has the body `if n == 2: continue` followed by `print(n)`. What does it print?", "`0`, `1`, `3`, `4`. `continue` skips only the rest of the pass where n is 2.", id="c-continue"),
        CARD("Is `bool(\"0\")` True or False?", "True. `\"0\"` is a non-empty string, and only the empty string is falsy.", id="c-truthy-str"),
        CARD("What does `\"10\" < \"9\"` give, and why?", "True. Text compares character by character, and `\"1\"` comes before `\"9\"`. Convert with `int()` to compare as numbers.", id="c-strcmp"),
        CARD("How does Python read `not x == 5`?", "As `not (x == 5)`: comparisons run before `not`.", id="c-not-prec"),
        CARD("What does `True or False and False` give?", "True. `and` runs before `or`, so it is `True or (False and False)`.", id="c-and-or"),
        CARD("When does the `else` of a `for` loop run?", "When the loop finishes without a `break`. A `break` skips it.", id="c-forelse"),
        CARD("In two nested loops, what does a `break` in the inner loop leave?", "Only the inner loop. The outer loop carries on with its next pass.", id="c-break-inner"),
        CARD("How do you test whether `x` is None?", "`x is None` (or `x is not None`), rather than `x == None`.", id="c-is-none"),
        CARD("Why start a running maximum at the first value instead of 0?", "If every value is negative, 0 would beat them all and the answer would be wrong.", id="c-running-max"),
        CARD("After `for i in range(3): ...` finishes, what is `i`?", "2, the last value it was given. The loop variable survives the loop.", id="c-loopvar"),
    ],
)
