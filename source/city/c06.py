from dsl import *

CITY = city(
    "py06",
    opener="Mrs Pell keeps her sales on scraps of paper. A list is a better scrap: ordered, growable, and it does not blow away.",
    scene="""
    Mrs Pell tips a biscuit tin of paper scraps onto the counter. Each scrap is one hour's takings. "I want to know my best hours," she says, "and I want to stop losing scraps."

    NIT: "This is the beginning of a ledger. Ledgers are the beginning of everything. Banks. Archives. Arguments." """,
    jobs=[
        JOB("story", "best_hours", "Mrs Pell's best hours",
            """
            `sales[i]` is what Mrs Pell took in hour `i`. Write `best_hours(sales, n)` that returns a list of the `n` hours with the biggest sales, biggest first. When two hours tie, the earlier hour comes first. Do not change the list you are given.

            - `best_hours([12, 0, 7, 30, 7, 15], 2)` is `[3, 5]`
            - `best_hours([5, 5, 1], 2)` is `[0, 1]`""",
            "def best_hours(sales, n):\n    pass\n",
            """
            f = ns.get("best_hours")
            check("defines best_hours", lambda: callable(f))
            check("top 2 of [12, 0, 7, 30, 7, 15]", lambda: f([12, 0, 7, 30, 7, 15], 2) == [3, 5])
            check("top 3 of the same", lambda: f([12, 0, 7, 30, 7, 15], 3) == [3, 5, 0])
            check("ties keep the earlier hour first", lambda: f([5, 5, 1], 2) == [0, 1], "Sort by sales from high to low, and by hour from low to high.")
            check("ties further down", lambda: f([7, 9, 7, 7], 3) == [1, 0, 2])
            def untouched():
                s = [3, 1, 2]
                f(s, 2)
                return s == [3, 1, 2]
            check("does not change the list", untouched, "sorted() returns a new list; list.sort() changes the old one.")
            """,
            "Sort the hours, not the sales: sorted(range(len(sales)), key=...). A key function can return a tuple such as (-sales[h], h). Then slice the first n.",
            "def best_hours(sales, n):\n    def rank(h):\n        return (-sales[h], h)\n    return sorted(range(len(sales)), key=rank)[:n]"),
        JOB("repair", "restock", "Repair the restock",
            """
            `restock` should return a new shelf with the item added, leaving the original alone. It changes the morning shelf too. The program should print `['apple', 'pear']` then `['apple', 'pear', 'fig']`. Repair `restock`.""",
            'def restock(shelf, item):\n    shelf.append(item)\n    return shelf\n\nmorning = ["apple", "pear"]\nevening = restock(morning, "fig")\nprint(morning)\nprint(evening)\n',
            """
            check("prints the two shelves", lambda: out.strip().split("\\n") == ["['apple', 'pear']", "['apple', 'pear', 'fig']"], "shelf and morning are two names for one list.")
            f = ns.get("restock")
            def untouched():
                s = ["a"]
                r = f(s, "b")
                return s == ["a"] and r == ["a", "b"]
            check("leaves its argument unchanged", untouched)
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
        "Assignment never copies. `b = a` attaches a second name to the same list, so `b.append(...)` changes what `a` shows too, and passing a list to a function does the same: the parameter is another name for the caller's list. To get a separate list, make one: `a[:]`, `list(a)` or `a.copy()` (a shallow copy), or build a new list with `+` or a comprehension."),
    terms=[
        TERM("list", "An ordered, mutable sequence written in square brackets.", "`[12, 0, 7]`", ""),
        TERM("tuple", "An ordered, immutable sequence written with commas, usually in brackets.", "`(5, 6)`", "Writing `(5)` for a one-item tuple; it needs a comma: `(5,)`."),
        TERM("mutable", "Can be changed in place. Lists, dicts and sets are mutable.", "", ""),
        TERM("append / extend", "`append` adds one item; `extend` adds every item of another sequence.", "", "`a.append([1, 2])` adds one item that is a list."),
        TERM("sort vs sorted", "`list.sort()` changes the list and returns None; `sorted(x)` returns a new list.", "", "`a = a.sort()` sets `a` to None."),
        TERM("key function", "A function given to sorting that turns each item into the value to sort by.", "`sorted(words, key=len)`", ""),
        TERM("alias", "A second name for the same object.", "`b = a`", "Expecting a copy."),
        TERM("shallow copy", "A new outer list that holds the same inner objects.", "`a[:]`, `a.copy()`", "Copying a list of lists and expecting the inner lists to be separate."),
        TERM("list comprehension", "A compact expression that builds a list from a loop and optional condition.", "`[n * n for n in range(5) if n % 2]`", ""),
        TERM("zip", "Pairs items from several sequences, stopping at the shortest.", '`zip("ab", [1, 2])`', ""),
        TERM("unpacking", "Assigning the items of a sequence to several names at once.", "`x, y = (5, 6)`", ""),
    ],
)
