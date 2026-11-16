from dsl import *

CITY = city(
    "py07",
    opener="The Archives have lent the Workshop a card index: keys on the front, values on the back. Treat it gently. It is older than me.",
    scene="""
    Mrs Pell's tin now holds a week of scraps: each one says what she sold and for how much. She wants to know what earns her the most.

    "Plums," she says. "I am always selling plums." Her nephew wrote her a little program to prove it:

    ```
    scraps = [("plum", 1), ("fig", 9), ("plum", 1), ("apple", 4), ("plum", 1)]
    counts = {}
    for item, coins in scraps:
        counts[item] = counts.get(item, 0) + 1
    print(counts)
    ```

    It does say plums: three scraps. But it counts **scraps**, not **coins**, and the fig sold once for 9.

    NIT: "Feelings are not a data structure. A dictionary is. Although this one is answering a different question from the one you asked." """,
    jobs=[
        JOB("story", "ledger", "Mrs Pell's ledger",
            """
            Each record is a tuple `(item, coins)`. Write two functions:

            - `totals_by_item(records)` returns a dictionary of item to **total coins** (not the number of scraps).
            - `best_seller(records)` returns the item with the largest total. If totals tie, return the one that comes first alphabetically. For no records, return `None`.

            Remember that `max` keeps the first of equal values, so the order of the keys you give it decides ties.""",
            "def totals_by_item(records):\n    pass\n\ndef best_seller(records):\n    pass\n",
            """
            t = ns.get("totals_by_item")
            b = ns.get("best_seller")
            week = [("apple", 4), ("plum", 3), ("apple", 2), ("fig", 6), ("plum", 3)]
            scraps = [("plum", 1), ("fig", 9), ("plum", 1), ("apple", 4), ("plum", 1)]
            check("defines both functions", lambda: callable(t) and callable(b))
            check_eq("totals for the week", lambda: t(week), {"apple": 6, "plum": 6, "fig": 6}, "Add the coins: totals[item] = totals.get(item, 0) + coins.")
            check_eq("the scene's scraps add coins, not scraps", lambda: t(scraps), {"plum": 3, "fig": 9, "apple": 4}, "Add `coins`, not 1.")
            check_eq("no records give an empty dict", lambda: t([]), {})
            check_eq("the fig earns most", lambda: b(scraps), "fig")
            check_eq("a three-way tie gives apple", lambda: b(week), "apple", "Give max the keys in alphabetical order: max(sorted(totals), key=totals.get).")
            check_eq("a tie between pear and lime gives lime", lambda: b([("pear", 5), ("lime", 2), ("lime", 3)]), "lime", "The tie-break is alphabetical, not first-seen.")
            check_eq("no records give None", lambda: b([]), None, "An empty dictionary has no best key: check for it before calling max.")
            check("does not change the records", lambda: (lambda r: (b(r), r)[1] == [("fig", 1)])([("fig", 1)]))
            """,
            "Counting pattern: totals[item] = totals.get(item, 0) + coins. For the best seller, reuse totals_by_item; if it is empty return None; otherwise max(sorted(totals), key=totals.get) gives the alphabetically first of the largest.",
            "def totals_by_item(records):\n    totals = {}\n    for item, coins in records:\n        totals[item] = totals.get(item, 0) + coins\n    return totals\n\ndef best_seller(records):\n    totals = totals_by_item(records)\n    if not totals:\n        return None\n    return max(sorted(totals), key=totals.get)"),
        JOB("repair", "riders", "Repair the rider counter",
            """
            `unique_riders(names)` should count how many **different** people rode today. It counts every ride instead, so a regular who rides twice is counted twice. Repair it so that it stays fast when thousands of different people ride: keep the riders you have seen in a set.""",
            "def unique_riders(names):\n    riders = []\n    for n in names:\n        riders.append(n)\n    return len(riders)\n",
            """
            f = ns.get("unique_riders")
            uses_set = uses_call("set") or has_node("Set", "SetComp")
            check("defines unique_riders", lambda: callable(f))
            check_eq("Wren, Juno, Wren gives 2", lambda: f(["Wren", "Juno", "Wren"]), 2, "A set keeps only one of each.")
            check_eq("nobody gives 0", lambda: f([]), 0)
            check_eq("case matters: Ada and ada are different", lambda: f(["Ada", "ada"]), 2)
            check("keeps the riders in a set", lambda: uses_set, "`if n not in riders` on a list scans every rider seen so far: with 5000 riders that is millions of steps. A set jumps straight to the answer.")
            check_eq("5000 different riders over 10000 rides", lambda: f(["rider%d" % (i % 5000) for i in range(10000)]) if uses_set else "skipped until a set is used", 5000, "Every rider rode twice: count each once.")
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
        "A list has no idea where an item is, so `in` checks items one by one: a million items can mean a million checks. A set (and a dict's keys) stores each item at a place worked out from its hash, so Python jumps straight to where it would be: about the same speed for ten items or a million. That is also why set items and dict keys must be hashable: if an item could change, its hash would change and Python would look in the wrong place. The rider counter only needs 'have I seen this person?', which is exactly what a set is built for.",
        points=[
            "`in` on a list checks items one by one (O(n))",
            "A set or dict computes the item's hash and jumps to its slot (about constant time)",
            "So items and keys must be hashable: their hash cannot change",
            "The rider counter only asks 'seen before?', so a set fits",
        ]),
    terms=[
        TERM("dictionary", "A mutable mapping from unique keys to values, kept in insertion order.", '`{"gear": 3}`', "Expecting `in` to search the values: it only tests keys.", q="What does `\"gear\" in stock` test when `stock` is a dictionary?", id="t0"),
        TERM("key / value", "A dict stores each value under a unique key. Assigning to an existing key replaces its value.", '`d = {"a": 1}; d["a"] = 2` leaves `{"a": 2}`', "Expecting a second entry for the same key.", q='`d = {"a": 1}`, then `d["a"] = 2`. What is `d`?', id="t1"),
        TERM("KeyError", "Raised when you read `d[k]` and `k` is not a key. Avoid it with `d.get(k, default)` or by checking `k in d` first.", '`{"a": 1}["b"]`', "Reading `d[k]` for a key that may not exist yet, such as `counts[w] += 1` for a word seen for the first time.", card=False, id="t2"),
        TERM(".get()", "Returns the value for a key, or a default (None if not given) when the key is missing.", '`stock.get("nut", 0)` gives 0 when there is no "nut"', "", q='What does `stock.get("nut", 0)` return when "nut" is not a key?', id="t3"),
        TERM(".items()", "Gives (key, value) pairs for looping.", "`for item, coins in totals.items():`", "", card=False, id="t4"),
        TERM("set", "An unordered, mutable collection of unique hashable items with fast membership tests.", "`{3, 1, 2}`, `set(\"banana\")`", "`{}` is an empty dict; an empty set is `set()`.", q="What is a set, and what happens to duplicates in one?", id="t5"),
        TERM("hashable", "Has a hash that never changes, so it can be a dict key or set item. Numbers, strings and tuples of hashables are; lists, dicts and sets are not.", '`{(1, "A"): "Ada"}` works; `{[1]: "x"}` raises TypeError', "Using a tuple that contains a list as a key.", card=False, id="t6"),
        TERM("counting pattern", "`counts[k] = counts.get(k, 0) + 1` inside a loop.", 'for w in words: counts[w] = counts.get(w, 0) + 1', "`counts[k] += 1` on a new key raises KeyError.", card=False, id="t7"),
        TERM("grouping pattern", "Create an empty list for a new key, then append to it.", "`groups.setdefault(len(w), []).append(w)`", "Resetting `groups = {}` inside the loop, which throws away every earlier group.", card=False, id="t8"),
        TERM("set operations", "`&` intersection, `|` union, `-` difference, `^` in exactly one, `<=` subset.", "`{1, 2, 3} - {2}` is `{1, 3}`", "Treating `a - b` and `b - a` as the same.", card=False, id="t9"),
        TERM("setdefault", "`d.setdefault(k, v)` returns `d[k]`, first storing `v` under `k` if it is missing.", '`groups.setdefault("A", []).append("Ada")`', "", card=False, id="t-setdefault"),
        TERM("defaultdict", "A dict from `collections` that makes a default value (for example an empty list) the first time a missing key is used.", "`from collections import defaultdict; d = defaultdict(list)`", "Reading a missing key to check it: that creates the key. Use `k in d`.", card=False, id="t-defaultdict"),
    ],
    nit_right=[
        "Correct. A dictionary's `in` looks at keys only; the values were never consulted.",
        "Accepted. Duplicates vanished on entering the set, as they always will.",
        "Right. `a - b` and `b - a` are different questions, and you asked the intended one.",
    ],
)
