from dsl import *

LESSON = lesson(
    id="py07", track="py", n=7, title="Dictionaries and sets", minutes=70,
    summary="Hash tables, key lookup, the counting and grouping patterns, nested data, and set algebra.",
    goals=[
        "Create, read, update and loop over dictionaries",
        "Explain why dictionary and set lookups are fast and why keys must be hashable",
        "Use the counting and grouping patterns",
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
        A **dictionary** stores key and value pairs. You look a value up by its key, not by a position. Keys are unique, assigning to an existing key replaces its value, and since Python 3.7 a dictionary remembers the order in which keys were first added."""),
        NOTE("model", """
        A dictionary works like the index of a book: instead of reading every page you jump straight to the entry. Python does this with a **hash table**. It computes a number from the key (its *hash*) and uses it to find the storage slot directly, so lookup, insert and delete take about the same time whether the dictionary holds ten entries or ten million."""),
        NOTE("trap", """
        Keys must be **hashable**, which in practice means immutable: strings, numbers and tuples work, but lists and dictionaries do not (`TypeError: unhashable type`). A key's hash must never change while it is stored, and a list could change."""),

        H("Missing keys"),
        CODE("""
        ages = {"Ada": 36}
        print(ages.get("Zed"))
        print(ages.get("Zed", 0))
        if "Zed" in ages:
            print("found")
        else:
            print("not found")
        """),
        P("""
        `d[key]` raises `KeyError` when the key is missing, which is right when absence is a bug. `d.get(key, default)` returns a fallback instead, which is right when absence is normal."""),

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
        Looping over a dictionary gives its keys. `.items()` gives `(key, value)` pairs and `.values()` gives the values. `max(scores, key=scores.get)` finds the key whose value is largest."""),

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
        Starting from a default and updating it, as `get` does here, is one of the most common dictionary idioms. The standard library has `collections.Counter` for exactly this job."""),
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
        `setdefault` and `collections.defaultdict(list)` shorten this. Values can be lists, other dictionaries, anything, and nested dictionaries are exactly what JSON data looks like."""),
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
        A **set** is an unordered collection of unique, hashable items. Duplicates vanish, and membership testing uses a hash table, so `x in some_set` stays fast however large the set is, unlike `x in some_list`."""),
        NOTE("trap", """
        `{}` is an empty **dictionary**, not an empty set. Use `set()` for an empty set. Sets have no order and no positions, so `s[0]` is an error and the printing order is not something to rely on. Sort when you need a stable order."""),
        CODE("""
        a = {1, 2, 3, 4}
        b = {3, 4, 5}
        print(sorted(a | b))   # union
        print(sorted(a & b))   # intersection
        print(sorted(a - b))   # difference
        print(sorted(a ^ b))   # symmetric difference
        print({1, 2} <= a)     # subset
        """),
        P("""
        Set algebra answers questions like "which students are in both classes?" (`&`), "who is in either?" (`|`) and "who is only in the first?" (`-`)."""),
        CODE("""
        seen = set()
        for n in [3, 1, 3, 2, 1]:
            if n in seen:
                print("first repeat:", n)
                break
            seen.add(n)
        """),

        H("Choosing the right collection"),
        P("""
        - **list**: ordered, duplicates allowed, position matters
        - **tuple**: a fixed group of related values; can be a dictionary key
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
           check('"a b a" counts', lambda: f("a b a") == {"a": 2, "b": 1})
           check("ignores case", lambda: f("The the THE") == {"the": 3})
           check("a single word", lambda: f("lime") == {"lime": 1})
           check("extra spaces are ignored", lambda: f(" a  a ") == {"a": 2})
           """,
           "Lowercase and split the text, then use counts[word] = counts.get(word, 0) + 1.",
           "def word_freq(text):\n    counts = {}\n    for word in text.lower().split():\n        counts[word] = counts.get(word, 0) + 1\n    return counts"),
        EX("invert", "invert",
           "Write `invert(d)` that returns a new dictionary with keys and values swapped. You may assume the values are unique and hashable.",
           "def invert(d):\n    pass\n",
           """
           f = ns.get("invert")
           check("defines invert", lambda: callable(f))
           check("simple dictionary", lambda: f({"a": 1, "b": 2}) == {1: "a", 2: "b"})
           check("empty dictionary", lambda: f({}) == {})
           check("does not change the input", lambda: (lambda d: (f(d), d)[1] == {"x": 9})({"x": 9}))
           """,
           "Loop over d.items() and set result[value] = key, or use a dictionary comprehension.",
           "def invert(d):\n    return {v: k for k, v in d.items()}"),
        EX("group", "group_by_length",
           "Write `group_by_length(words)` returning a dictionary from word length to the list of words of that length, in their original order.",
           "def group_by_length(words):\n    pass\n",
           """
           f = ns.get("group_by_length")
           check("defines group_by_length", lambda: callable(f))
           check("example", lambda: f(["tree", "lime", "oak", "pear", "fig"]) == {4: ["tree", "lime", "pear"], 3: ["oak", "fig"]})
           check("empty list", lambda: f([]) == {})
           check("one group", lambda: f(["a", "b"]) == {1: ["a", "b"]})
           """,
           "If len(word) is not yet a key, start it with an empty list. Then append the word.",
           "def group_by_length(words):\n    groups = {}\n    for word in words:\n        key = len(word)\n        if key not in groups:\n            groups[key] = []\n        groups[key].append(word)\n    return groups"),
        EX("common", "common",
           "Write `common(a, b)` that returns a sorted list of the items that appear in both lists, with no duplicates.",
           "def common(a, b):\n    pass\n",
           """
           f = ns.get("common")
           check("defines common", lambda: callable(f))
           check("numbers with duplicates", lambda: f([1, 2, 2, 3], [2, 3, 3, 4]) == [2, 3])
           check("no overlap", lambda: f([1, 2], [3, 4]) == [])
           check("strings", lambda: f(["b", "a", "c"], ["c", "a"]) == ["a", "c"])
           check("empty input", lambda: f([], [1]) == [])
           """,
           "Turn both lists into sets, intersect with &, then sort the result.",
           "def common(a, b):\n    return sorted(set(a) & set(b))"),
        EX("first_repeat", "first_repeat",
           "Write `first_repeat(items)` that returns the first item that has already appeared earlier in the list, scanning left to right, or `None` if there is no repeat. `first_repeat([3, 1, 3, 2, 1])` is 3.",
           "def first_repeat(items):\n    pass\n",
           """
           f = ns.get("first_repeat")
           check("defines first_repeat", lambda: callable(f))
           check("[3, 1, 3, 2, 1] gives 3", lambda: f([3, 1, 3, 2, 1]) == 3)
           check("[2, 1, 2, 1] gives 2", lambda: f([2, 1, 2, 1]) == 2)
           check("no repeat gives None", lambda: f([1, 2, 3]) is None)
           check("empty list gives None", lambda: f([]) is None)
           """,
           "Keep a set of items seen so far. If the item is already in the set, return it. Otherwise add it.",
           "def first_repeat(items):\n    seen = set()\n    for item in items:\n        if item in seen:\n            return item\n        seen.add(item)\n    return None"),
        EX("count_letters", "Fix the KeyError",
           "`count_letters` should count how many times each character appears, but it crashes with a `KeyError` the first time it sees a character. Fix it.",
           "def count_letters(text):\n    counts = {}\n    for ch in text:\n        counts[ch] += 1\n    return counts\n",
           """
           f = ns.get("count_letters")
           check("defines count_letters", lambda: callable(f))
           check('"aab" gives a: 2, b: 1', lambda: f("aab") == {"a": 2, "b": 1}, "A new key has no value to add to yet.")
           check("empty text", lambda: f("") == {})
           check("spaces count too", lambda: f("a a") == {"a": 2, " ": 1})
           """,
           "Use counts.get(ch, 0) + 1 so a missing key starts at 0.",
           "def count_letters(text):\n    counts = {}\n    for ch in text:\n        counts[ch] = counts.get(ch, 0) + 1\n    return counts", kind="fix"),
        EX("two_sum", "two_sum",
           """
           Write `two_sum(nums, target)` that returns a tuple `(i, j)` of two different positions, with `i < j`, whose numbers add up to `target`, or `None` if there are none. Use a dictionary so you only need one pass.""",
           "def two_sum(nums, target):\n    pass\n",
           """
           f = ns.get("two_sum")
           check("defines two_sum", lambda: callable(f))
           check("[2, 7, 11, 15] with 9", lambda: f([2, 7, 11, 15], 9) == (0, 1))
           check("[3, 2, 4] with 6", lambda: f([3, 2, 4], 6) == (1, 2))
           check("the same value twice", lambda: f([3, 3], 6) == (0, 1))
           check("no pair gives None", lambda: f([1, 2, 3], 100) is None)
           """,
           "For each number n at position i, ask whether target - n is already in a dictionary of value to position. If so you have the pair. Otherwise store n.",
           "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        need = target - n\n        if need in seen:\n            return (seen[need], i)\n        seen[n] = i\n    return None"),
    ],
    predict=[
        PRED('d = {}\nd["a"] = d.get("a", 0) + 1\nd["a"] = d.get("a", 0) + 1\nprint(d)',
             "The first `get` falls back to 0, giving 1. The second finds 1 and gives 2."),
        PRED("print(sorted({1, 2, 3} & {2, 3, 4}), sorted({1, 2} | {2, 5}))",
             "`&` keeps items in both sets. `|` keeps items in either, with duplicates removed."),
        PRED("print(type({}), type(set()), len({1, 1, 1}))",
             "`{}` is an empty dictionary. `set()` is an empty set. A set keeps only one copy of 1."),
        PRED('d = {"x": 1, "y": 2}\nfor k, v in d.items():\n    d[k] = v * 10\nprint(d)',
             "Changing the values while looping is fine because the keys are not added or removed."),
        PRED('d = {"a": 1}\nprint(d.get("b"), d.get("b", "none"), "a" in d)',
             "`get` returns None by default, or the fallback you give. `in` tests keys."),
        PRED('print(list({"b": 1, "a": 2}), sorted({"b": 1, "a": 2}.items()))',
             "A dictionary remembers insertion order, so its keys are b then a. Sorting the pairs orders them by key."),
    ],
    cards=[
        CARD("How fast is dictionary lookup and why?", "About constant time. Python hashes the key and jumps straight to the slot instead of scanning."),
        CARD("What does 'hashable' mean and which types are?", "A value whose hash never changes. Strings, numbers and tuples (of hashables) are. Lists, dicts and sets are not."),
        CARD("`d[key]` versus `d.get(key)`?", "`d[key]` raises `KeyError` if missing. `d.get(key, default)` returns the default (None if not given)."),
        CARD("What does looping directly over a dict give you?", "Its keys. Use `.items()` for (key, value) pairs and `.values()` for the values."),
        CARD("How do you count items with a dict?", "`counts[x] = counts.get(x, 0) + 1`, or use `collections.Counter`."),
        CARD("How do you group items by a key?", "Make an empty list for a new key, then append to `groups[key]`. `defaultdict(list)` does the first step for you."),
        CARD("What is `{}` and how do you make an empty set?", "`{}` is an empty dictionary. Use `set()` for an empty set."),
        CARD("What do `a | b`, `a & b`, `a - b` and `a ^ b` do for sets?", "Union, intersection, difference (in a not in b), and symmetric difference (in exactly one)."),
        CARD("Why is `x in a_set` faster than `x in a_list`?", "A set uses a hash table (about constant time). A list scans item by item (O(n))."),
        CARD("When do you choose list, tuple, dict or set?", "List for ordered items, tuple for a fixed group, dict to look up by key, set for uniqueness and fast membership."),
    ],
)
