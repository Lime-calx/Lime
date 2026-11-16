from dsl import *

CITY = city(
    "py06",
    opener="Mrs Pell keeps her sales on scraps of paper. A list is a better scrap: ordered, growable, and it does not blow away.",
    scene="""
    Mrs Pell tips a biscuit tin of paper scraps onto the counter. Each scrap is one hour's takings, in order from opening time. "I want to know my best hours," she says, "and I want to stop losing scraps."

    Her nephew already tried. This is his program. Predict both lines before you run it:

    ```
    sales = [12, 0, 7, 30, 7, 15]
    best = sales
    best.sort(reverse=True)
    print(best[:2])
    print(sales)
    ```

    NIT: "Two faults. It answers with amounts, when she asked for hours. And `best = sales` copied nothing: `sort()` reordered the one list both names share, so the record of which hour took what is gone. This is the beginning of a ledger. Ledgers are the beginning of everything. Banks. Archives. Arguments. The first job fixes both faults." """,
    jobs=[
        JOB("story", "best_hours", "Mrs Pell's best hours",
            """
            `sales[i]` is what Mrs Pell took in hour `i`. Write `best_hours(sales, n)` that returns a list of the `n` hours with the biggest sales, biggest first. When two hours tie, the earlier hour comes first. Do not change the list you are given.

            - `best_hours([12, 0, 7, 30, 7, 15], 2)` is `[3, 5]`
            - `best_hours([5, 5, 1], 2)` is `[0, 1]`""",
            "def best_hours(sales, n):\n    pass\n",
            """
            f = ns.get("best_hours")
            check("defines best_hours", lambda: callable(f), "Start with def best_hours(sales, n):")
            check_eq("top 2 of [12, 0, 7, 30, 7, 15]", lambda: f([12, 0, 7, 30, 7, 15], 2), [3, 5], "Return hour numbers (positions), not the sales amounts.")
            check_eq("top 3 of the same", lambda: f([12, 0, 7, 30, 7, 15], 3), [3, 5, 0], "Biggest first, then slice off the first n.")
            check_eq("ties keep the earlier hour first", lambda: f([5, 5, 1], 2), [0, 1], "Sorting is stable: hours with equal sales keep their original order, earlier first, as long as the key is only the sales.")
            check_eq("ties further down", lambda: f([7, 9, 7, 7], 3), [1, 0, 2])
            check_eq("n larger than the day", lambda: f([4, 6], 5), [1, 0], "Slicing past the end is safe: you get every hour.")
            def untouched():
                s = [3, 1, 2]
                f(s, 2)
                return s == [3, 1, 2]
            check("does not change the list", untouched, "sorted() returns a new list; list.sort() changes the old one, which is what lost the scraps.")
            """,
            "Sorting is stable: ties keep their original order. Sort the hour numbers, `range(len(sales))`, by their sales with a key such as `lambda h: sales[h]` and `reverse=True` (or the key `-sales[h]`), then slice the first n.",
            "def best_hours(sales, n):\n    hours = sorted(range(len(sales)), key=lambda h: sales[h], reverse=True)\n    return hours[:n]"),
        JOB("repair", "restock", "Repair the restock",
            """
            `restock` should return a new shelf with the item added, leaving the original alone. It changes the morning shelf too. The program should print `['apple', 'pear']` then `['apple', 'pear', 'fig']`. Repair `restock`.""",
            'def restock(shelf, item):\n    shelf.append(item)\n    return shelf\n\nmorning = ["apple", "pear"]\nevening = restock(morning, "fig")\nprint(morning)\nprint(evening)\n',
            """
            check_eq("prints the two shelves", lambda: out.strip().split("\\n"), ["['apple', 'pear']", "['apple', 'pear', 'fig']"], "shelf and morning are two names for one list, so append changes the morning shelf too.")
            f = ns.get("restock")
            def untouched():
                s = ["a"]
                r = f(s, "b")
                return s == ["a"] and r == ["a", "b"]
            check("leaves its argument unchanged", untouched, "Build a new list (shelf + [item]) instead of changing shelf. Note that shelf += [item] would still change it.")
            """,
            "Build a new list: return shelf + [item], or copy first with shelf[:].",
            'def restock(shelf, item):\n    return shelf + [item]\n\nmorning = ["apple", "pear"]\nevening = restock(morning, "fig")\nprint(morning)\nprint(evening)', kind="fix"),
    ],
    read=[
        READ("r1", "Two names, one tin",
             """
             a = [1, 2]
             b = a
             c = a[:]
             b.append(3)
             c.append(4)
             print(a, b, c)
             print(a is b, a is c, a == [1, 2, 3])
             t = (5, 6)
             x, y = t
             print(y, x, len(a + c))
             print([n * n for n in range(5) if n % 2 == 1])
             print(list(zip("ab", [1, 2, 3])))
             """,
             "`b = a` makes a second name for the same list, so appending through `b` shows in `a`. `a[:]` is a copy, so `c` changes alone. `is` asks 'same object?', `==` asks 'same contents?'. Unpacking puts 5 in x and 6 in y. `a + c` has 3 + 3 items. The comprehension squares the odd numbers 1 and 3. `zip` stops at the shorter input."),
    ],
    parsons=[
        PARSONS("p1", "A running total",
                "Order the lines to build a running total of Mrs Pell's hourly sales and print it: `[12, 12, 19, 49]`. Indentation is set. Two decoys are placed wrongly.",
                ["sales = [12, 0, 7, 30]", "running = []", "total = 0", "for s in sales:", "    total += s", "    running.append(total)", "print(running)"],
                """
                check("prints [12, 12, 19, 49]", lambda: out.strip() == "[12, 12, 19, 49]")
                """,
                distractors=["    running = []", "    running.append(s)"]),
    ],
    teach=TEACH(
        "Using Mrs Pell's list of sales, explain aliasing: when do two names share one list, and how do you make a real copy?",
        "Assignment never copies. `b = a` attaches a second name to the same list, so `b.append(...)` changes what `a` shows too, and passing a list to a function does the same: the parameter is another name for the caller's list. To get a separate list, make one: `a[:]`, `list(a)` or `a.copy()` (a shallow copy), or build a new list with `+` or a comprehension.",
        points=[
            "Assignment never copies: `b = a` gives one list two names",
            "A parameter is another name for the caller's list, so changes inside a function show outside",
            "Copy with `a[:]`, `list(a)`, `a.copy()`, or build a new list with `+` or a comprehension",
            "Copies are shallow: inner lists are still shared (use `copy.deepcopy` for nested data)",
        ]),
    terms=[
        TERM("list", "An ordered, mutable sequence written in square brackets.", "`[12, 0, 7]`", "Expecting `print(sales)` to show strings without quotes: a list shows its items with repr.", id="t0"),
        TERM("tuple", "An ordered, immutable sequence written with commas, usually in brackets. Its items cannot be replaced, but a mutable item inside it (such as a list) can still change.", "`(5, 6)`; `t = ([1],)` then `t[0].append(2)` works.", "Writing `(5)` for a one-item tuple; it needs a comma: `(5,)`.", id="t1"),
        TERM("mutable", "Can be changed in place. Lists, dicts and sets are mutable.", "`nums[0] = 99` changes the list `nums` itself.", "Thinking `x = 5; x += 1` changes the number 5: ints are immutable, the name just moves.",
             q="Which of these can be changed in place: str, list, tuple, int?", id="t2"),
        TERM("append / extend", "`append` adds one item; `extend` adds every item of another sequence.", "`[1].extend([2, 3])` gives `[1, 2, 3]`.", "`a.append([1, 2])` adds one item that is a list.", card=False, id="t3"),
        TERM("sort vs sorted", "`list.sort()` changes the list and returns None; `sorted(x)` returns a new list.", "`sorted([3, 1])` is `[1, 3]`.", "`a = a.sort()` sets `a` to None.", card=False, id="t4"),
        TERM("key function", "A function given to sorting that turns each item into the value to sort by.", "`sorted(words, key=len)`", "Writing `key=len()` with brackets: pass the function, do not call it.",
             q="In `sorted(words, key=len)`, why is it `len` and not `len()`?", id="t5"),
        TERM("alias", "A second name for the same object.", "`b = a`", "Expecting a copy.", card=False, id="t6"),
        TERM("shallow copy", "A new outer list that holds the same inner objects.", "`a[:]`, `a.copy()`", "Copying a list of lists and expecting the inner lists to be separate.", card=False, id="t7"),
        TERM("list comprehension", "A compact expression that builds a list from a loop and optional condition.", "`[n * n for n in range(5) if n % 2]`", "", card=False, id="t8"),
        TERM("zip", "Pairs items from several sequences, stopping at the shortest. A zip can be walked only once.", '`list(zip("ab", [1, 2]))` is `[(\'a\', 1), (\'b\', 2)]`.', "Reusing a zip after a loop has used it up.", card=False, id="t9"),
        TERM("unpacking", "Assigning the items of a sequence to several names at once.", "`x, y = (5, 6)`", "Unpacking into the wrong number of names raises ValueError: `a, b = [1, 2, 3]`.",
             q="What happens with `a, b = [1, 2, 3]`?", id="t10"),
        TERM("lambda", "A small unnamed function written in one expression: `lambda arguments: result`.", "`sorted(words, key=lambda w: w[-1])`", "Writing `return` inside a lambda: the expression after the colon is returned automatically.", card=False, id="t-lambda"),
        TERM("stable sort", "A sort that keeps items with equal keys in their original order. Python's sorts are stable.", '`sorted(["pear", "fig", "kiwi"], key=len)` keeps pear before kiwi.', "Expecting ties to be broken alphabetically without asking for it.", card=False, id="t-stable"),
        TERM("deep copy", "A copy of a nested structure where the inner objects are copied too, so nothing is shared.", "`import copy` then `copy.deepcopy(grid)`", "Using `grid.copy()` on a list of lists and expecting the rows to be separate.", card=False, id="t-deepcopy"),
        TERM("import / module", "`import name` loads a module, a file of ready-made tools, so you can use them as `name.tool`.", "`import copy` then `copy.deepcopy(x)`", "Calling `deepcopy(x)` without the `copy.` prefix after `import copy`.",
             q="After `import copy`, how do you call its `deepcopy` function?", id="t-import"),
        TERM("identity (is)", "`a is b` is True when both names refer to the very same object; `==` only compares contents.", "`[1] == [1]` is True but `[1] is [1]` is False.", "Using `is` to compare values such as numbers or strings; use `==`.",
             q="`[1] == [1]` and `[1] is [1]`: which is True?", id="t-is"),
    ],
    nit_right=[
        "Correct. `b = a` gave the list a second name. I have filed both names on the same card.",
        "Accepted. `sorted` handed you a new list and left the old one exactly as it was.",
        "Right. Equal keys kept their places. Sorting in Python is stable, which is more than I can say for the tin.",
    ],
)
