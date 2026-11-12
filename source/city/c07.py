from dsl import *

CITY = city(
    "py07",
    opener="The Archives have lent the Workshop a card index: keys on the front, values on the back. Treat it gently. It is older than me.",
    scene="""
    Mrs Pell's tin now holds a week of scraps: each one says what she sold and for how much. She wants to know what earns her the most.

    "Apples, I think," she says. "Or plums. It feels like plums."

    NIT: "Feelings are not a data structure. A dictionary is." """,
    jobs=[
        JOB("story", "ledger", "Mrs Pell's ledger",
            """
            Each record is a tuple `(item, coins)`. Write two functions:

            - `totals_by_item(records)` returns a dictionary of item to total coins.
            - `best_seller(records)` returns the item with the largest total. If totals tie, return the one that comes first alphabetically. For no records, return `None`.""",
            "def totals_by_item(records):\n    pass\n\ndef best_seller(records):\n    pass\n",
            """
            t = ns.get("totals_by_item")
            b = ns.get("best_seller")
            week = [("apple", 4), ("plum", 3), ("apple", 2), ("fig", 6), ("plum", 3)]
            check("defines both functions", lambda: callable(t) and callable(b))
            check("totals for the week", lambda: t(week) == {"apple": 6, "plum": 6, "fig": 6})
            check("no records give an empty dict", lambda: t([]) == {})
            check("a clear best seller", lambda: b([("apple", 4), ("fig", 9)]) == "fig")
            check("a three-way tie gives apple", lambda: b(week) == "apple", "Compare (-total, item) or sort the items first.")
            check("no records give None", lambda: b([]) is None)
            """,
            "Counting pattern: totals[item] = totals.get(item, 0) + coins. For the best seller, reuse totals_by_item, then look for the largest total; a key such as (-total, name) handles ties.",
            "def totals_by_item(records):\n    totals = {}\n    for item, coins in records:\n        totals[item] = totals.get(item, 0) + coins\n    return totals\n\ndef best_seller(records):\n    totals = totals_by_item(records)\n    if not totals:\n        return None\n    def rank(item):\n        return (-totals[item], item)\n    return sorted(totals, key=rank)[0]"),
        JOB("repair", "riders", "Repair the rider counter",
            """
            `unique_riders(names)` should count how many **different** people rode today. It counts every ride instead, so a regular who rides twice is counted twice. Repair it.""",
            "def unique_riders(names):\n    riders = []\n    for n in names:\n        riders.append(n)\n    return len(riders)\n",
            """
            f = ns.get("unique_riders")
            check("defines unique_riders", lambda: callable(f))
            check("Wren, Juno, Wren gives 2", lambda: f(["Wren", "Juno", "Wren"]) == 2, "A set keeps only one of each.")
            check("nobody gives 0", lambda: f([]) == 0)
            check("case matters: Ada and ada are different", lambda: f(["Ada", "ada"]) == 2)
            check("handles 20000 rides quickly", lambda: f([i % 50 for i in range(20000)]) == 50, "A set checks membership instantly; a list has to search.")
            """,
            "Use a set instead of a list: riders = set(), riders.add(n). Or simply len(set(names)).",
            "def unique_riders(names):\n    return len(set(names))", kind="fix"),
    ],
    read=[
        READ("r1", "The borrowed card index",
             """
             stock = {"gear": 3, "spring": 0}
             stock["gear"] += 2
             stock["bolt"] = stock.get("bolt", 0) + 1
             print(stock)
             print(len(stock), "spring" in stock, stock.get("nut"))
             seen = {3, 1, 3, 2}
             print(len(seen), sorted(seen))
             a = {"x", "y", "z"}
             b = {"y", "z", "w"}
             print(sorted(a & b), sorted(a - b), len(a | b))
             print({k: v * 2 for k, v in stock.items() if v})
             """,
             "`+=` updates the existing key, and `get` with a default creates `bolt` safely. A dict remembers insertion order. `in` checks keys, so `spring` is there even though its value is 0, and a missing key with `get` gives None. A set keeps one of each, so {3, 1, 3, 2} has 3 items. `&` is shared items, `-` is in a but not b, `|` is everything (4). The comprehension skips `spring` because 0 is falsy."),
    ],
    parsons=[
        PARSONS("p1", "Group the stops by letter",
                "Order the lines into a function that groups stop names by their first letter, then print the result for three stops. Indentation is set. One decoy resets the groups inside the loop.",
                ["def by_letter(names):", "    groups = {}", "    for name in names:", "        key = name[0]", "        if key not in groups:", "            groups[key] = []", "        groups[key].append(name)", "    return groups", 'print(by_letter(["Bell", "Brass", "Cog"]))'],
                """
                check("prints the grouped dict", lambda: out.strip() == "{'B': ['Bell', 'Brass'], 'C': ['Cog']}")
                """,
                distractors=["        groups = {}"]),
    ],
    teach=TEACH(
        "Explain why `x in a_set` stays fast for a million items while `x in a_list` gets slow. What does that mean for the rider counter?",
        "A list has no idea where an item is, so `in` checks items one by one: a million items can mean a million checks. A set (and a dict's keys) stores each item at a place worked out from its hash, so Python jumps straight to where it would be: about the same speed for ten items or a million. The rider counter only needs 'have I seen this person?', which is exactly what a set is built for."),
    terms=[
        TERM("dictionary", "A mutable mapping from keys to values, kept in insertion order.", '`{"gear": 3}`', ""),
        TERM("key / value", "A dict stores each value under a unique key. Keys must be hashable.", "", "Using a list as a key: lists are mutable, so they cannot be hashed."),
        TERM("KeyError", "Raised when you read `d[k]` and `k` is not a key.", "", "Fix with `d.get(k, default)` or check `k in d` first."),
        TERM(".get()", "Returns the value for a key, or a default (None if not given) when the key is missing.", '`stock.get("nut", 0)`', ""),
        TERM(".items()", "Gives (key, value) pairs for looping.", "`for item, coins in totals.items():`", ""),
        TERM("set", "An unordered, mutable collection of unique hashable items with fast membership tests.", "`{3, 1, 2}`", "`{}` is an empty dict; an empty set is `set()`."),
        TERM("hashable", "Has a fixed hash value, so it can be a dict key or set item. Numbers, strings and tuples of hashables are; lists and dicts are not.", "", ""),
        TERM("counting pattern", "`counts[k] = counts.get(k, 0) + 1` inside a loop.", "", ""),
        TERM("grouping pattern", "Create an empty list for a new key, then append to it.", "", ""),
        TERM("set operations", "`&` intersection, `|` union, `-` difference, `^` in exactly one.", "", ""),
    ],
)
