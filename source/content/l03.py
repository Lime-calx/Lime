from dsl import *

LESSON = lesson(
    id="py03", track="py", n=3, title="Decisions and loops", minutes=60,
    summary="Booleans, comparisons, if/elif/else, while and for loops, and the accumulator and counter patterns.",
    goals=[
        "Build conditions with comparisons, and, or and not",
        "Know which values are truthy and falsy",
        "Choose between while and for, and write both correctly",
        "Use accumulators, counters, break and continue",
    ],
    blocks=[
        H("Booleans and comparisons"),
        P("""
        A `bool` is `True` or `False`. Comparison operators produce booleans: `==` equal, `!=` not equal, `<`, `<=`, `>`, `>=`. Python also allows **chained** comparisons: `1 < x < 10` means `1 < x and x < 10`."""),
        CODE("""
        x = 7
        print(x == 7, x != 7, x > 10)
        print(1 < x < 10)
        print("apple" < "banana")
        """),
        NOTE("trap", """
        `=` assigns and `==` compares. Writing `if x = 5:` is a SyntaxError in Python, which protects you from a bug that is common in other languages. Also remember that types matter: `"10" == 10` is False, because a string is never equal to a number."""),

        H("and, or, not and short-circuiting"),
        P("""
        `and` is true when both sides are, `or` when at least one is, and `not` flips a value. They **short-circuit**: Python stops as soon as the answer is known, and the result is the last value it looked at, which is not always a bool."""),
        CODE("""
        print(True and False, True or False, not True)
        print(0 or "fallback")
        print(3 and 4)
        print("" or "default name")
        age = 20
        print(age >= 18 and age < 65)
        """),
        P("""
        `x or default` is a common idiom for a fallback value. `a and b` protects `b`: it only runs when `a` is truthy, which matters when `b` would crash if `a` were false."""),
        NOTE("trap", """
        `if x == 1 or 2:` does not mean "x is 1 or 2". It means `(x == 1) or 2`, and `2` is always truthy, so the condition is always true. Write `x == 1 or x == 2`, or `x in (1, 2)`."""),

        H("Truthiness"),
        P("""
        In an `if`, any value can act as a condition. These are **falsy**: `False`, `None`, `0`, `0.0`, the empty string `""`, and empty collections such as `[]`. Everything else is **truthy**."""),
        CODE("""
        print(bool(0), bool(1), bool(""), bool("0"), bool(None), bool([]), bool([0]))
        """),
        P("""
        Notice that the text `"0"` is truthy, because it is a non-empty string, and so is `[0]`, because the list is not empty."""),

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

        H("Repeating with while"),
        P("""
        `while` repeats a block as long as its condition is truthy. The body must change something so the condition eventually becomes false, or the loop runs forever."""),
        CODE("""
        n = 1
        while n <= 5:
            print(n)
            n += 1
        print("done, n is", n)
        """),
        NOTE("trap", """
        The classic infinite loop is forgetting the update (`n += 1`). Lime stops runaway loops after a few seconds, but ordinary Python would keep going until you interrupt it."""),
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
        `for` runs the body once for each item in a sequence. `range(stop)` produces 0, 1, ... up to `stop - 1`. `range(start, stop)` begins at `start`, and `range(start, stop, step)` skips by `step`. The stop value is **never included**."""),
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
        `range(a, b)` yields exactly `b - a` numbers. That half-open convention (include the start, exclude the end) is also used by slicing. It makes ranges join cleanly: `range(0, 3)` followed by `range(3, 6)` covers 0 to 5 with no gap and no overlap."""),
        P("""
        You can loop over text as well: each pass of `for ch in "lime"` gives one character."""),
        CODE("""
        for ch in "lime":
            print(ch.upper())
        """),

        H("Two patterns you will use constantly"),
        P("""
        An **accumulator** builds up a result one step at a time. A **counter** counts how many items meet a condition."""),
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

        H("break, continue and nested loops"),
        P("""
        `break` leaves the loop at once. `continue` skips to the next pass. A loop inside a loop runs its whole cycle for each pass of the outer one."""),
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

        for row in range(1, 4):
            for col in range(1, 4):
                print(row * col, end=" ")
            print()
        """),
    ],
    exercises=[
        EX("fizzbuzz", "FizzBuzz",
           """
           Print the numbers 1 to 15, one per line. For multiples of 3 print `Fizz` instead, for multiples of 5 print `Buzz`, and for multiples of both print `FizzBuzz`.""",
           "# FizzBuzz for 1 to 15\n",
           """
           exp = []
           for k in range(1, 16):
               exp.append("FizzBuzz" if k % 15 == 0 else "Fizz" if k % 3 == 0 else "Buzz" if k % 5 == 0 else str(k))
           check("prints the 15 lines correctly", lambda: out.strip().split("\\n") == exp, "Check the multiple of both 3 and 5 first.")
           check("uses a loop", lambda: "for" in code or "while" in code, "Use a loop instead of fifteen print lines.")
           """,
           "Test `n % 15 == 0` first, then 3, then 5, then fall back to the number.",
           """
           for n in range(1, 16):
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
               return sum(n for n in range(k) if n % 3 == 0 or n % 5 == 0)
           check("total is correct for limit = 1000", lambda: ns["total"] == ref(1000), "Loop over range(limit) and add n when it is a multiple of 3 or 5.")
           def other():
               n2, _ = rerun("limit = 1000", "limit = 50")
               return n2["total"] == ref(50)
           check("works for other limits", other, "Use the variable limit, not the number 1000.")
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
           check("steps is correct for n = 27", lambda: ns["steps"] == ref(27), "Use a while loop that runs until n becomes 1.")
           def other():
               n2, _ = rerun("n = 27", "n = 97")
               return n2["steps"] == ref(97)
           check("works for other starting values", other, "Do not type the answer in; compute it.")
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
           "This prints 0 to 4. Change it so it prints 1 to 5, one number per line.",
           "for i in range(5):\n    print(i)\n",
           """
           check("prints 1 to 5", lambda: out.split() == ["1", "2", "3", "4", "5"], "range(stop) starts at 0. Give it a start and a stop, and remember the stop is not included.")
           """,
           "range(1, 6) gives 1, 2, 3, 4, 5.",
           "for i in range(1, 6):\n    print(i)", kind="fix"),
        EX("triangle", "Star triangle",
           "Print a right triangle of stars with 4 rows: one star on the first row, then two, three and four.",
           "# print the triangle\n",
           """
           check("prints the triangle", lambda: out.strip().split("\\n") == ["*", "**", "***", "****"], "Row k holds k stars. A string can be repeated with *.")
           check("uses a loop", lambda: "for" in code or "while" in code, "Use a loop.")
           """,
           "`\"*\" * k` is k stars. Loop k from 1 to 4.",
           """
           for row in range(1, 5):
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
           check("answer is correct for limit = 5000", lambda: ns["answer"] == ref(5000), "Keep adding 1 while the square is still too small.")
           def other():
               n2, _ = rerun("limit = 5000", "limit = 100")
               return n2["answer"] == ref(100)
           check("works for other limits", other, "Use limit in your condition.")
           """,
           "`while answer * answer <= limit:` then `answer += 1`.",
           """
           limit = 5000
           answer = 1
           while answer * answer <= limit:
               answer += 1
           """),
    ],
    predict=[
        PRED("for i in range(2, 10, 3):\n    print(i)",
             "`range(2, 10, 3)` starts at 2 and steps by 3: 2, 5, 8. The next would be 11, which is past the stop."),
        PRED('print(bool(""), bool("0"), bool([]), bool(None))',
             "Only the non-empty string `\"0\"` is truthy. Empty string, empty list and None are falsy."),
        PRED("x = 5\nprint(1 < x < 10, x > 3 and x < 4, not x == 5)",
             "The chained comparison is true. `x > 3 and x < 4` is false because x < 4 fails. `not x == 5` is `not True`."),
        PRED('print(0 or "fallback", 3 and 4)',
             "`or` returns the first truthy value, here the text. `and` returns the last value when everything before it is truthy: 4."),
        PRED("total = 0\nfor n in range(1, 5):\n    if n == 3:\n        continue\n    total += n\nprint(total)",
             "`continue` skips n = 3, so the total is 1 + 2 + 4 = 7."),
    ],
    cards=[
        CARD("What does the chained comparison `1 < x < 10` mean?", "`1 < x and x < 10`, evaluated with x only once."),
        CARD("`=` versus `==`?", "`=` assigns a value to a name. `==` compares two values and gives a bool."),
        CARD("What does `0 or \"fallback\"` evaluate to, and why?", "`\"fallback\"`. `or` returns the first truthy value it meets, or the last value if none is truthy."),
        CARD("Which values are falsy in Python?", "`False`, `None`, `0`, `0.0`, `\"\"` and empty collections. Everything else is truthy."),
        CARD("Why is `if x == 1 or 2:` a bug?", "It parses as `(x == 1) or 2`, and 2 is always truthy. Write `x == 1 or x == 2` or `x in (1, 2)`."),
        CARD("In an if/elif chain, which branch runs?", "Only the first one whose condition is true, so put the most specific tests first."),
        CARD("Does `range(2, 10)` include 10? How many numbers does it give?", "No, the stop is excluded. It gives `10 - 2` = 8 numbers: 2 to 9."),
        CARD("When do you choose `while` over `for`?", "When you do not know the number of repetitions in advance and loop until a condition changes."),
        CARD("What do `break` and `continue` do?", "`break` leaves the loop at once. `continue` skips the rest of this pass and starts the next."),
        CARD("What are the accumulator and counter patterns?", "Accumulator: start at 0 (or empty) and add to it each pass. Counter: add 1 each time a condition is met."),
    ],
)
