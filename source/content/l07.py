from dsl import *

LESSON = lesson(
    id="py07", track="py", n=7, title="Dictionaries and sets", minutes=75,
    summary="Hash tables, key lookup, the counting and grouping patterns, nested data, and set algebra.",
    goals=[
        "Create, read, update and loop over dictionaries",
        "Explain why dictionary and set lookups are fast and why keys must be hashable",
        "Use the counting and grouping patterns, including setdefault and defaultdict",
        "Use sets for uniqueness, fast membership and set algebra",
        "Choose between list, tuple, dict and set",
    ],
    blocks=[
        H("Dictionaries map keys to values"),
        CODE("""
        ages = {"Ada": 36, "Alan": 41}
        print(ages["Ada"])
        ages["Grace"] = 85
        ages["Ada"] = 37
        print(ages)
        print(len(ages), "Alan" in ages, "Zed" in ages)
        print(list(ages))
        """),
        P("""
        A **dictionary** stores key and value pairs. You look a value up by its key, not by a position. Keys are unique, assigning to an existing key replaces its value, and since Python 3.7 a dictionary remembers the order in which keys were first added. `in` tests the **keys**, never the values."""),
        NOTE("model", """
        A dictionary works like the index of a book: instead of reading every page you jump straight to the entry. Python does this with a **hash table**. It computes a number from the key (its *hash*) and uses it to find the storage slot directly, so on average lookup, insert and delete take about the same time whether the dictionary holds ten entries or ten million."""),
        CODE("""
        beds = {(1, "A"): "Ada", (1, "B"): "Alan"}
        print(beds[(1, "B")])
        beds[(2, "A")] = "Grace"
        print(len(beds))
        """),
        NOTE("trap", """
        Keys must be **hashable**: their hash must never change while they are stored. In practice that means immutable values. Strings, numbers and tuples work, and lists, dictionaries and sets do not (`TypeError: unhashable type: 'list'`). A tuple is hashable **only if everything inside it is**: `(1, "A")` is a fine key, but `(1, [2])` is not, because the list inside could change."""),

        H("Missing keys"),
        CODE("""
        ages = {"Ada": 36}
        print(ages.get("Zed"))
        print(ages.get("Zed", 0))
        if "Zed" in ages:
            print("found")
        else:
            print("not found")
        print(ages["Zed"])
        """),
        P("""
        `d[key]` raises `KeyError` when the key is missing, which is right when absence is a bug. `d.get(key, default)` returns a fallback instead (or `None` if you give no default), which is right when absence is normal."""),

        H("Looping over a dictionary"),
        CODE("""
        scores = {"Ada": 90, "Alan": 85, "Grace": 95}
        for name in scores:
            print(name)
        for name, score in scores.items():
            print(name, score)
        print(sum(scores.values()) / len(scores))
        best = max(scores, key=scores.get)
        print(best)
        """),
        P("""
        Looping over a dictionary gives its keys. `.items()` gives `(key, value)` pairs and `.values()` gives the values. `max(scores, key=scores.get)` finds the key whose value is largest. When several keys tie, `max` keeps the **first** one it met, so sort the keys first if the tie-break should be alphabetical: `max(sorted(scores), key=scores.get)`."""),
        CODE("""
        stock = {"gauze": 4, "tape": 0, "saline": 0}
        for item in list(stock):
            if stock[item] == 0:
                del stock[item]
        print(stock)
        for item in stock:
            if stock[item] < 5:
                stock["order more " + item] = 10
        """),
        NOTE("trap", """
        Changing the **values** of existing keys while you loop is fine. Adding or removing **keys** while you loop over the dictionary itself raises `RuntimeError: dictionary changed size during iteration`, as the last loop above shows. Loop over `list(d)`, a separate copy of the keys made before the loop starts, or build a new dictionary instead. (Lime's in-browser Python only reports the adding case; standard Python reports both.)"""),

        H("The counting pattern"),
        CODE("""
        text = "the cat and the hat and the bat"
        counts = {}
        for word in text.split():
            counts[word] = counts.get(word, 0) + 1
        print(counts)

        def second(pair):
            return pair[1]

        top = sorted(counts.items(), key=second, reverse=True)
        print(top[:2])
        """),
        P("""
        Starting from a default and updating it, as `get` does here, is one of the most common dictionary idioms. The standard library has a ready-made tool for it. `from collections import Counter` loads the name `Counter` from the `collections` module, one of the many modules that come with Python: `import` is how a program borrows tools that are not built in."""),
        CODE("""
        from collections import Counter
        text = "the cat and the hat and the bat"
        print(Counter(text.split()).most_common(2))
        """),

        H("The grouping pattern"),
        CODE("""
        words = ["tree", "lime", "oak", "pear", "fig"]
        by_length = {}
        for word in words:
            key = len(word)
            if key not in by_length:
                by_length[key] = []
            by_length[key].append(word)
        print(by_length)
        """),
        P("""
        Two shortcuts remove the `if`. `d.setdefault(key, [])` returns the value already stored under `key`, or first stores the `[]` you gave and returns that. A `defaultdict(list)` creates a fresh empty list by itself the first time a missing key is used."""),
        CODE("""
        words = ["tree", "lime", "oak", "pear", "fig"]
        groups = {}
        for word in words:
            groups.setdefault(len(word), []).append(word)
        print(groups)

        from collections import defaultdict
        by_letter = defaultdict(list)
        for word in words:
            by_letter[word[0]].append(word)
        print(by_letter["t"], by_letter["z"], len(by_letter))
        """),
        NOTE("deep", """
        Reading a missing key from a `defaultdict` **creates** it: `by_letter["z"]` above added the key `"z"` with an empty list, which is why the length is 6, not 5. Use `"z" in by_letter` when you only want to ask. It prints as `defaultdict(<class 'list'>, {...})`; `dict(by_letter)` turns it back into a plain dictionary."""),
        P("""
        Values can be lists, other dictionaries, anything, and nested dictionaries are exactly what JSON data looks like."""),
        CODE("""
        person = {"name": "Ada", "langs": ["Python", "Analytical Engine"], "address": {"city": "London"}}
        print(person["langs"][0])
        print(person["address"]["city"])
        """),

        H("Dictionary comprehensions"),
        CODE("""
        squares = {n: n * n for n in range(1, 6)}
        print(squares)
        swapped = {v: k for k, v in squares.items()}
        print(swapped)
        """),
        P("""
        If a comprehension produces the same key twice, the later value replaces the earlier one, just as assigning to an existing key does."""),

        H("Sets: unique items, fast membership"),
        CODE("""
        a = {1, 2, 3, 3, 2}
        print(sorted(a), len(a))
        print(2 in a)
        print(set("banana") == {"b", "a", "n"})
        empty = set()
        print(type(empty), type({}))
        """),
        P("""
        A **set** is an unordered collection of unique, hashable items. Duplicates vanish, and membership testing uses a hash table, so `x in some_set` stays fast however large the set is, unlike `x in some_list`, which scans item by item."""),
        NOTE("trap", """
        `{}` is an empty **dictionary**, not an empty set. Use `set()` for an empty set. Sets have no order and no positions, so `s[0]` is an error and the printing order is not something to rely on. Sort when you need a stable order."""),
        CODE("""
        seen = {"Ada"}
        seen.add("Alan")
        seen.add("Ada")
        seen.discard("Zed")
        seen.remove("Alan")
        print(seen)
        """),
        P("""
        `add` puts an item in (adding one that is already there changes nothing). `remove` takes one out and raises `KeyError` if it is missing; `discard` does nothing if it is missing."""),

        H("Set algebra"),
        CODE("""
        monday = {"Ada", "Alan", "Grace", "Linus"}
        tuesday = {"Grace", "Linus", "Barbara"}
        print(sorted(monday & tuesday))   # in both: intersection
        print(sorted(monday | tuesday))   # in either: union
        print(sorted(monday - tuesday))   # in monday, not tuesday: difference
        print(sorted(tuesday - monday))   # order matters for -
        print(sorted(monday ^ tuesday))   # in exactly one: symmetric difference
        print({"Ada", "Grace"} <= monday) # subset: is every item also in monday?
        print(monday <= tuesday)
        """),
        P("""
        Set algebra answers questions like "who worked both days?" (`&`), "who worked at all?" (`|`), "who worked only Monday?" (`-`), "who worked exactly one day?" (`^`) and "has this record got every required item?" (`required <= record`). `a - b` and `b - a` are different questions; the other three operators give the same answer either way round."""),
        CODE("""
        seen = set()
        for n in [3, 1, 3, 2, 1]:
            if n in seen:
                print("first repeat:", n)
                break
            seen.add(n)
        """),
        NOTE("deep", """
        The operators have method twins that accept any iterable, not only sets: `a.union(list_b)`, `a.intersection(...)`, `a.difference(...)`, `a.symmetric_difference(...)`, `a.issubset(...)`. `a < b` means a proper subset (a subset and not equal). `a.isdisjoint(b)` is True when they share nothing. To remove duplicates **and keep the original order**, a set will not do; use `list(dict.fromkeys(items))`, because dictionary keys are unique and keep insertion order."""),

        H("Choosing the right collection"),
        P("""
        - **list**: ordered, duplicates allowed, position matters
        - **tuple**: a fixed group of related values; can be a dictionary key if everything inside is hashable
        - **dict**: look things up by a key; count; group
        - **set**: uniqueness, fast membership, set algebra"""),
    ],
    exercises=[
        EX("word_freq", "word_freq",
           "Write `word_freq(text)` that returns a dictionary counting each word, ignoring upper or lower case. Words are separated by whitespace.",
           "def word_freq(text):\n    pass\n",
           """
           f = ns.get("word_freq")
           check("defines word_freq", lambda: callable(f))
           check_eq('"a b a" counts', lambda: f("a b a"), {"a": 2, "b": 1}, "Count every word: counts[word] = counts.get(word, 0) + 1.")
           check_eq("ignores case", lambda: f("The the THE"), {"the": 3}, "Lowercase the text before splitting.")
           check_eq("a single word", lambda: f("lime"), {"lime": 1})
           check_eq("extra spaces are ignored", lambda: f(" a  a "), {"a": 2}, "split() with no argument ignores runs of spaces.")
           check_eq("a longer text", lambda: f("Pulse BP pulse temp BP pulse"), {"pulse": 3, "bp": 2, "temp": 1})
           """,
           "Lowercase and split the text, then use counts[word] = counts.get(word, 0) + 1.",
           "def word_freq(text):\n    counts = {}\n    for word in text.lower().split():\n        counts[word] = counts.get(word, 0) + 1\n    return counts"),
        EX("invert", "invert",
           "Write `invert(d)` that returns a new dictionary with keys and values swapped. You may assume the values are unique and hashable.",
           "def invert(d):\n    pass\n",
           """
           f = ns.get("invert")
           check("defines invert", lambda: callable(f))
           check_eq("simple dictionary", lambda: f({"a": 1, "b": 2}), {1: "a", 2: "b"})
           check_eq("empty dictionary", lambda: f({}), {})
           check_eq("ward codes", lambda: f({"ICU": "W1", "ER": "W2", "OH": "W3"}), {"W1": "ICU", "W2": "ER", "W3": "OH"})
           check("does not change the input", lambda: (lambda d: (f(d), d)[1] == {"x": 9})({"x": 9}), "Build a new dictionary; do not edit d.")
           """,
           "Loop over d.items() and set result[value] = key, or use a dictionary comprehension.",
           "def invert(d):\n    return {v: k for k, v in d.items()}"),
        EX("group", "group_by_length",
           "Write `group_by_length(words)` returning a dictionary from word length to the list of words of that length, in their original order. Try `setdefault` or the `if key not in` pattern.",
           "def group_by_length(words):\n    pass\n",
           """
           f = ns.get("group_by_length")
           check("defines group_by_length", lambda: callable(f))
           check_eq("example", lambda: f(["tree", "lime", "oak", "pear", "fig"]), {4: ["tree", "lime", "pear"], 3: ["oak", "fig"]}, "Each length needs its own list; append each word to the list for its length.")
           check_eq("empty list", lambda: f([]), {})
           check_eq("one group", lambda: f(["a", "b"]), {1: ["a", "b"]})
           check_eq("keeps duplicates and order", lambda: f(["bp", "hr", "bp", "temp"]), {2: ["bp", "hr", "bp"], 4: ["temp"]})
           check("returns a plain dict", lambda: type(f(["a"])) is dict, "If you used defaultdict, return dict(groups).")
           """,
           "If len(word) is not yet a key, start it with an empty list. Then append the word. groups.setdefault(len(word), []).append(word) does both.",
           "def group_by_length(words):\n    groups = {}\n    for word in words:\n        key = len(word)\n        if key not in groups:\n            groups[key] = []\n        groups[key].append(word)\n    return groups"),
        EX("common", "common",
           "Write `common(a, b)` that returns a sorted list of the items that appear in both lists, with no duplicates.",
           "def common(a, b):\n    pass\n",
           """
           f = ns.get("common")
           check("defines common", lambda: callable(f))
           check_eq("numbers with duplicates", lambda: f([1, 2, 2, 3], [2, 3, 3, 4]), [2, 3], "Turn both lists into sets so duplicates vanish.")
           check_eq("no overlap", lambda: f([1, 2], [3, 4]), [])
           check_eq("strings", lambda: f(["b", "a", "c"], ["c", "a"]), ["a", "c"])
           check_eq("empty input", lambda: f([], [1]), [])
           check_eq("returns a list, not a set", lambda: f([5, 9], [9]), [9], "sorted(...) of a set gives a list.")
           """,
           "Turn both lists into sets, intersect with &, then sort the result.",
           "def common(a, b):\n    return sorted(set(a) & set(b))"),
        EX("rota", "Compare two rotas",
           """
           `monday` and `tuesday` are lists of the staff who worked each day (a name may appear twice). Write `rota_report(monday, tuesday)` that returns a dictionary with three keys, each holding a **sorted list** of names:

           - `"both"`: worked both days
           - `"monday_only"`: worked Monday but not Tuesday
           - `"one_day"`: worked exactly one of the two days

           Use set operators, one for each key.""",
           "def rota_report(monday, tuesday):\n    pass\n",
           """
           f = ns.get("rota_report")
           check("defines rota_report", lambda: callable(f))
           check_eq("the example week", lambda: f(["Ada", "Alan", "Grace"], ["Grace", "Barbara", "Ada"]), {"both": ["Ada", "Grace"], "monday_only": ["Alan"], "one_day": ["Alan", "Barbara"]}, "both is &, monday_only is -, one_day is ^.")
           check_eq("duplicates in a list", lambda: f(["Ada", "Ada"], ["Ada"]), {"both": ["Ada"], "monday_only": [], "one_day": []}, "Make sets first so each name counts once.")
           check_eq("nobody on Monday", lambda: f([], ["Linus"]), {"both": [], "monday_only": [], "one_day": ["Linus"]}, "monday_only is monday - tuesday, not tuesday - monday.")
           check("one_day uses ^ (or symmetric_difference)", lambda: has_node("BitXor") or uses_call("symmetric_difference"), "a ^ b keeps what is in exactly one set; it is the operator this job practises.")
           check("monday_only uses - (or difference)", lambda: has_node("Sub") or uses_call("difference"), "a - b keeps what is in a but not in b.")
           """,
           "Make a = set(monday) and b = set(tuesday). Then both = a & b, monday_only = a - b, one_day = a ^ b. Wrap each in sorted(...).",
           'def rota_report(monday, tuesday):\n    a = set(monday)\n    b = set(tuesday)\n    return {"both": sorted(a & b), "monday_only": sorted(a - b), "one_day": sorted(a ^ b)}'),
        EX("vaccines", "Missing vaccines",
           """
           A fit-to-work screen needs every vaccine in `required`. A worker's `record` is a list of the vaccines they have had (it may include extra ones, or repeats). Write two functions:

           - `missing(record, required)` returns a sorted list of the required vaccines not in the record.
           - `is_complete(record, required)` returns `True` if every required vaccine is in the record. Use the subset operator `<=`.""",
           "def missing(record, required):\n    pass\n\ndef is_complete(record, required):\n    pass\n",
           """
           m = ns.get("missing")
           c = ns.get("is_complete")
           check("defines both functions", lambda: callable(m) and callable(c))
           check_eq("two missing", lambda: m(["MMR", "tetanus"], ["hepB", "MMR", "varicella"]), ["hepB", "varicella"], "required - record keeps what is required but not yet had.")
           check_eq("extras and repeats are fine", lambda: m(["hepB", "flu", "hepB", "MMR"], ["MMR", "hepB"]), [])
           check_eq("not complete", lambda: c(["MMR"], ["MMR", "hepB"]), False)
           check_eq("complete with extras", lambda: c(["hepB", "MMR", "flu"], ["MMR", "hepB"]), True, "set(required) <= set(record) asks: is every required item in the record?")
           check_eq("nothing required is always complete", lambda: c([], []), True)
           check("is_complete uses a subset test", lambda: has_node("LtE", "GtE") or uses_call("issubset") or uses_call("issuperset") or uses_call("missing"), "Practise the subset operator: set(required) <= set(record).")
           """,
           "missing: sorted(set(required) - set(record)). is_complete: set(required) <= set(record).",
           "def missing(record, required):\n    return sorted(set(required) - set(record))\n\ndef is_complete(record, required):\n    return set(required) <= set(record)"),
        EX("first_repeat", "first_repeat",
           "Write `first_repeat(items)` that returns the first item that has already appeared earlier in the list, scanning left to right, or `None` if there is no repeat. `first_repeat([3, 1, 3, 2, 1])` is 3.",
           "def first_repeat(items):\n    pass\n",
           """
           f = ns.get("first_repeat")
           check("defines first_repeat", lambda: callable(f))
           check_eq("[3, 1, 3, 2, 1] gives 3", lambda: f([3, 1, 3, 2, 1]), 3)
           check_eq("[2, 1, 2, 1] gives 2", lambda: f([2, 1, 2, 1]), 2)
           check_eq('["a", "b", "b", "a"] gives "b"', lambda: f(["a", "b", "b", "a"]), "b", "The first item whose second copy you reach, not the first item that has a copy somewhere.")
           check_eq("no repeat gives None", lambda: f([1, 2, 3]), None)
           check_eq("empty list gives None", lambda: f([]), None)
           """,
           "Keep a set of items seen so far. If the item is already in the set, return it. Otherwise add it.",
           "def first_repeat(items):\n    seen = set()\n    for item in items:\n        if item in seen:\n            return item\n        seen.add(item)\n    return None"),
        EX("count_letters", "Fix the KeyError",
           "`count_letters` should count how many times each character appears, but it crashes with a `KeyError` the first time it sees a character. Fix it.",
           "def count_letters(text):\n    counts = {}\n    for ch in text:\n        counts[ch] += 1\n    return counts\n",
           """
           f = ns.get("count_letters")
           check("defines count_letters", lambda: callable(f))
           check_eq('"aab" gives a: 2, b: 1', lambda: f("aab"), {"a": 2, "b": 1}, "A new key has no value to add to yet.")
           check_eq("empty text", lambda: f(""), {})
           check_eq("spaces count too", lambda: f("a a"), {"a": 2, " ": 1})
           """,
           "Use counts.get(ch, 0) + 1 so a missing key starts at 0.",
           "def count_letters(text):\n    counts = {}\n    for ch in text:\n        counts[ch] = counts.get(ch, 0) + 1\n    return counts", kind="fix"),
        EX("two_sum", "two_sum",
           """
           Write `two_sum(nums, target)` that returns a tuple `(i, j)` of two different positions, with `i < j`, whose numbers add up to `target`, or `None` if there are none. If several pairs work, return the one whose `j` is smallest. Use a dictionary so you only need one pass.""",
           "def two_sum(nums, target):\n    pass\n",
           """
           f = ns.get("two_sum")
           check("defines two_sum", lambda: callable(f))
           check_eq("[2, 7, 11, 15] with 9", lambda: f([2, 7, 11, 15], 9), (0, 1))
           check_eq("[3, 2, 4] with 6", lambda: f([3, 2, 4], 6), (1, 2), "A number cannot pair with itself: 3 + 3 uses position 0 twice.")
           check_eq("the same value twice", lambda: f([3, 3], 6), (0, 1))
           check_eq("no pair gives None", lambda: f([1, 2, 3], 100), None)
           check_eq("negative numbers", lambda: f([5, -2, 8, 4], 2), (1, 3))
           check("uses a dictionary", lambda: has_node("Dict", "DictComp") or uses_call("dict"), "Store each number's position in a dictionary as you go: seen[n] = i.")
           """,
           "For each number n at position i, ask whether target - n is already in a dictionary of value to position. If so you have the pair. Otherwise store n.",
           "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        need = target - n\n        if need in seen:\n            return (seen[need], i)\n        seen[n] = i\n    return None"),
    ],
    predict=[
        PRED('d = {}\nd["a"] = d.get("a", 0) + 1\nd["a"] = d.get("a", 0) + 1\nprint(d)',
             "The first `get` falls back to 0, giving 1. The second finds 1 and gives 2.",
             traps={"{'a': 1}": "Each line reads the current value again: the second `get` finds 1, so it stores 2.",
                    "{'a': 1, 'a': 2}": "Keys are unique. Assigning to an existing key replaces its value."}, id="p0"),
        PRED("print(sorted({1, 2, 3} & {2, 3, 4}), sorted({1, 2} | {2, 5}))",
             "`&` keeps items in both sets. `|` keeps items in either, with duplicates removed.",
             traps={"[2, 3] [1, 2, 2, 5]": "A set never holds duplicates, so the union has one 2.",
                    "[1, 2, 3, 4] [2]": "`&` is the items in both; `|` is the items in either. You swapped them."}, id="p1"),
        PRED("print(type({}), type(set()), len({1, 1, 1}))",
             "`{}` is an empty dictionary. `set()` is an empty set. A set keeps only one copy of 1.",
             traps={"<class 'set'> <class 'set'> 1": "`{}` is an empty dictionary; only `set()` makes an empty set.",
                    "<class 'dict'> <class 'set'> 3": "A set keeps one copy of each item, so `{1, 1, 1}` has one item."}, id="p2"),
        PRED('d = {"x": 1, "y": 2}\nfor k, v in d.items():\n    d[k] = v * 10\nprint(d)',
             "Changing the values while looping is fine because no keys are added or removed, so the dictionary's size never changes.",
             traps={"RuntimeError": "Only adding or removing keys changes the size. Replacing the value under an existing key is safe.",
                    "{'x': 1, 'y': 2}": "`d[k] = ...` changes the dictionary itself, not a copy."}, id="p3"),
        PRED('d = {"a": 1}\nprint(d.get("b"), d.get("b", "none"), "a" in d)',
             "`get` returns None by default, or the fallback you give. `in` tests keys.",
             traps={"KeyError": "`get` never raises KeyError; returning a fallback instead is its whole point. Only `d[\"b\"]` would raise."}, id="p4"),
        PRED('print(list({"b": 1, "a": 2}), sorted({"b": 1, "a": 2}.items()))',
             "A dictionary remembers insertion order, so its keys are b then a. Sorting the pairs orders them by key.",
             traps={"['a', 'b'] [('a', 2), ('b', 1)]": "A dictionary keeps insertion order; it never sorts its keys for you.",
                    "[1, 2] [('a', 2), ('b', 1)]": "`list(d)` gives the keys, not the values."}, id="p5"),
        PRED('a = {1, 2, 3}\nb = {2, 3, 4}\nprint(sorted(a ^ b), sorted(b - a), {2, 3} <= a, a <= b)',
             "`^` keeps items in exactly one set: 1 and 4. `b - a` keeps what is in b but not in a: 4. {2, 3} is inside a, so it is a subset; a has 1, which b lacks, so a is not a subset of b.",
             traps={"[1, 4] [1] True False": "Order matters for `-`: `b - a` keeps what is in b and not in a.",
                    "[1, 2, 3, 4] [4] True False": "`^` keeps items in exactly one set; `|` would be the union."}, id="p-set-ops"),
        PRED('d = {"a": 1, "b": 2}\nfor k in list(d):\n    d[k + k] = d[k]\nprint(len(d), list(d)[-1])',
             "`list(d)` copies the keys before the loop starts, so the loop sees only a and b even though two keys are added. The dictionary ends with 4 keys, and the last one added is bb.",
             traps={"RuntimeError": "That error comes from looping over `d` itself. `list(d)` is a separate copy of the keys, so adding keys is safe.",
                    "2 b": "The loop really adds keys: `d[k + k] = ...` stores aa and bb."}, id="p-dict-size"),
        PRED('d = {len(w): w for w in ["fig", "oak", "pear"]}\nprint(d)',
             "fig and oak both have length 3. The later value replaces the earlier one under the same key, so 3 maps to oak.",
             traps={"{3: 'fig', 4: 'pear'}": "A repeated key keeps the **last** value, as assigning to an existing key does.",
                    "{3: 'fig', 3: 'oak', 4: 'pear'}": "Keys are unique: a second value for 3 replaces the first."}, id="p-dict-dup"),
    ],
    cards=[
        CARD("What does 'hashable' mean, and which values are hashable?", "Its hash can never change while it is stored, so it can be a dict key or set item. In practice: immutable values (numbers, strings), and tuples only if everything inside is hashable. Lists, dicts and sets are not.", id="c1"),
        CARD('`d = {(1, [2]): "x"}`: what happens?', "`TypeError: unhashable type: 'list'`. A tuple is hashable only if everything inside it is.", id="c-tuple-key"),
        CARD("`d[key]` when the key is missing?", "It raises `KeyError`. Use `d.get(key, default)` when a missing key is normal.", id="c2"),
        CARD('`for x in {"a": 1, "b": 2}: print(x)` prints?', "`a` then `b`: looping over a dict gives its keys. Use `.items()` for (key, value) pairs.", id="c3"),
        CARD("Complete the counting line inside a loop: `counts[w] = ...`", "`counts[w] = counts.get(w, 0) + 1` (or use `collections.Counter`).", id="c4"),
        CARD("Group words by length with one line in the loop and no `if`.", "`groups.setdefault(len(w), []).append(w)`. setdefault returns the stored list, or stores your `[]` first.", id="c5"),
        CARD('`d = defaultdict(list)`, then `d["x"].append(1)`. What are `d["x"]` and `len(d)`?', "`[1]` and 1: a missing key gets a fresh empty list automatically.", id="c-defaultdict"),
        CARD("`print(type({}))`?", "`<class 'dict'>`. `{}` is an empty dictionary; an empty set is `set()`.", id="c6"),
        CARD("`sorted({1, 2, 3} - {2, 4})`?", "`[1]`: difference keeps what is in the first set and not in the second.", id="c7"),
        CARD("`sorted({1, 2, 3} ^ {2, 3, 4})`?", "`[1, 4]`: symmetric difference keeps what is in exactly one set.", id="c-set-xor"),
        CARD("Which set operator gives the items in both sets?", "`&` (intersection), e.g. `{1, 2} & {2, 3}` is `{2}`.", id="c-set-and"),
        CARD("`{1, 2} <= {1, 2, 3}`?", "`True`: `<=` asks whether every item on the left is also on the right (subset).", id="c-set-sub"),
        CARD("Why is `x in a_set` (or a dict key lookup) fast while `x in a_list` gets slow?", "A set or dict hashes x and jumps to its slot: about constant time on average. A list scans item by item: O(n).", id="c8"),
        CARD('What is wrong: `for k in d:` then `d[k + "_copy"] = d[k]`?', "Adding (or removing) keys while looping over d raises `RuntimeError: dictionary changed size during iteration`. Loop over `list(d)` instead.", id="c-dict-size"),
        CARD("You must check thousands of times whether a patient ID has already been seen. Which collection?", "A set: fast membership and no duplicates.", id="c9"),
        CARD("You need each drug's dose looked up by the drug's name. Which collection?", "A dict, with the name as key and the dose as value.", id="c-choose-dict"),
    ],
)
