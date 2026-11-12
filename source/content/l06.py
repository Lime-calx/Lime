from dsl import *

LESSON = lesson(
    id="py06", track="py", n=6, title="Lists and tuples", minutes=70,
    summary="Mutable sequences, aliasing and copying, comprehensions, tuples, unpacking, and the costs of list operations.",
    goals=[
        "Create, index, slice and change lists",
        "Explain aliasing: why b = a does not copy a list",
        "Write list comprehensions with a condition",
        "Use tuples, unpacking, enumerate and zip",
        "Avoid the mutable default argument trap",
    ],
    blocks=[
        H("A list is an ordered, changeable collection"),
        CODE("""
        nums = [10, 20, 30, 40]
        print(nums)
        print(len(nums), nums[0], nums[-1])
        print(nums[1:3])
        nums[0] = 99
        print(nums)
        """),
        P("""
        Lists are written with square brackets and can hold any values, even mixed types. Indexing and slicing work exactly as they do for strings, with one big difference: lists are **mutable**, so you can assign to a position."""),

        H("Changing lists"),
        CODE("""
        items = ["a", "b"]
        items.append("c")
        items.extend(["d", "e"])
        items.insert(0, "start")
        print(items)
        last = items.pop()
        print(last, items)
        items.remove("b")
        print(items)
        print("c" in items, items.index("c"))
        del items[0]
        print(items)
        """),
        P("""
        - `append(x)` adds one item at the end
        - `extend(other)` adds every item of another sequence
        - `insert(i, x)` puts an item at position `i`
        - `pop()` removes and returns the last item, or the item at an index you give
        - `remove(x)` removes the first item equal to `x`
        - `del items[i]` removes the item at position `i`"""),

        H("Sorting"),
        CODE("""
        nums = [3, 1, 2]
        print(sorted(nums), nums)
        result = nums.sort()
        print(result, nums)
        words = ["banana", "Apple", "cherry"]
        print(sorted(words))
        print(sorted(words, key=str.lower))
        print(sorted(words, key=len, reverse=True))
        """),
        NOTE("trap", """
        `list.sort()` sorts **in place** and returns `None`. Writing `nums = nums.sort()` destroys your list. Use `sorted(nums)` when you want a new sorted list and the original left alone."""),
        P("""
        The `key` argument is a function applied to each item to decide its order, which is why functions being values (lesson 4) matters. Sorting is **stable**: items with equal keys keep their original relative order."""),

        H("Names, aliases and copies"),
        P("""
        This is where the label idea from lesson 2 pays off. `b = a` does not copy a list. It attaches a second name to the **same** list object."""),
        CODE("""
        a = [1, 2, 3]
        b = a
        b.append(4)
        print(a)
        print(a is b)
        c = a.copy()
        c.append(5)
        print(a, c)
        print(a is c, a == c)
        """),
        NOTE("model", """
        `==` asks whether two lists have equal contents. `is` asks whether they are the very same object. Changing a list through one name is visible through every other name for that object. When you need independence, copy: `a.copy()`, `a[:]` or `list(a)`."""),
        NOTE("trap", """
        A copy is **shallow**: it copies the outer list but not the lists inside it, so nested lists are still shared. For fully independent nested data use `copy.deepcopy`."""),
        CODE("""
        grid = [[0, 0], [0, 0]]
        shallow = grid.copy()
        shallow[0][0] = 9
        print(grid)

        bad = [[0] * 2] * 2
        bad[0][0] = 5
        print(bad)

        good = [[0] * 2 for _ in range(2)]
        good[0][0] = 5
        print(good)
        """),
        P("""
        `[[0] * 2] * 2` repeats the **same** inner list twice, so a change shows up in both rows. A list comprehension builds a fresh row each time, which is the safe way to make a grid."""),

        H("A trap with default arguments"),
        P("""
        A default value is created **once**, when the function is defined, not each time it is called. If that default is a mutable list, every call that uses it shares the same list."""),
        CODE("""
        def add_item(item, bucket=[]):
            bucket.append(item)
            return bucket

        print(add_item(1))
        print(add_item(2))
        """),
        P("""
        The standard fix is to use `None` as the default and create the list inside the function: `if bucket is None: bucket = []`."""),

        H("Looping and comprehensions"),
        CODE("""
        nums = [1, 2, 3, 4, 5, 6]
        for n in nums:
            print(n * n, end=" ")
        print()
        for i, n in enumerate(nums):
            if i < 2:
                print(i, n)
        squares = [n * n for n in nums]
        evens = [n for n in nums if n % 2 == 0]
        print(squares)
        print(evens)
        print(sum(nums), min(nums), max(nums), len(nums))
        """),
        P("""
        A **list comprehension**, `[expression for item in sequence if condition]`, builds a new list in one readable line. Read it as: for each item, keep it if the condition holds, and put the expression in the new list. `enumerate` gives `(index, item)` pairs when you need both."""),

        H("Tuples: lists that cannot change"),
        CODE("""
        point = (3, 4)
        x, y = point
        print(x, y, point[0])
        single = (5,)
        print(type(single), type((5)))

        def divide(a, b):
            return a // b, a % b

        q, r = divide(17, 5)
        print(q, r)
        """),
        P("""
        A **tuple** is an ordered, immutable sequence. Use one for a fixed group of values that belong together, such as coordinates or a pair returned from a function. Because they cannot change, tuples can be dictionary keys, which lists cannot. Note the trailing comma in `(5,)`: the comma makes the tuple, not the brackets."""),

        H("zip: walk through lists together"),
        CODE("""
        names = ["Ada", "Alan", "Grace"]
        years = [1815, 1912, 1906]
        for name, year in zip(names, years):
            print(name, year)
        print(list(zip(names, years)))
        """),

        H("What operations cost"),
        P("""
        Checking `x in some_list` scans from the start until it finds a match, so on average it takes time proportional to the length of the list, written O(n). Reading `nums[i]` and appending to the end are fast. Inserting at the front is slow, because every other item has to shuffle along. When you need many fast membership checks, a set (next lesson) is the right tool."""),
    ],
    exercises=[
        EX("dedupe", "dedupe",
           "Write `dedupe(items)` that returns a new list with duplicates removed, keeping the first occurrence of each item in its original order. The input list must not be changed.",
           "def dedupe(items):\n    pass\n",
           """
           f = ns.get("dedupe")
           check("defines dedupe", lambda: callable(f))
           check("[3, 1, 3, 2, 1] gives [3, 1, 2]", lambda: f([3, 1, 3, 2, 1]) == [3, 1, 2])
           check("empty list", lambda: f([]) == [])
           check("strings", lambda: f(["a", "a", "b"]) == ["a", "b"])
           def untouched():
               orig = [1, 1, 2]
               f(orig)
               return orig == [1, 1, 2]
           check("does not change the input", untouched, "Build and return a new list.")
           """,
           "Start with an empty result. For each item, append it only if it is not already in result.",
           "def dedupe(items):\n    result = []\n    for item in items:\n        if item not in result:\n            result.append(item)\n    return result"),
        EX("rotate", "rotate",
           "Write `rotate(items, k)` that returns a new list rotated left by `k` places: `rotate([1, 2, 3, 4, 5], 2)` is `[3, 4, 5, 1, 2]`. `k` may be larger than the list, zero or negative. The input must not change.",
           "def rotate(items, k):\n    pass\n",
           """
           f = ns.get("rotate")
           check("defines rotate", lambda: callable(f))
           check("rotate([1, 2, 3, 4, 5], 2)", lambda: f([1, 2, 3, 4, 5], 2) == [3, 4, 5, 1, 2])
           check("k = 0", lambda: f([1, 2, 3], 0) == [1, 2, 3])
           check("k larger than the list", lambda: f([1, 2, 3], 4) == [2, 3, 1])
           check("empty list", lambda: f([], 3) == [])
           check("negative k rotates right", lambda: f([1, 2, 3, 4], -1) == [4, 1, 2, 3])
           def untouched():
               orig = [1, 2, 3]
               f(orig, 1)
               return orig == [1, 2, 3]
           check("does not change the input", untouched)
           """,
           "Reduce k with `k % len(items)` (watch out for an empty list), then join two slices: `items[k:] + items[:k]`.",
           "def rotate(items, k):\n    if not items:\n        return []\n    k = k % len(items)\n    return items[k:] + items[:k]"),
        EX("transpose", "transpose",
           "Write `transpose(matrix)` that swaps rows and columns of a list of equal-length rows: `[[1, 2, 3], [4, 5, 6]]` becomes `[[1, 4], [2, 5], [3, 6]]`.",
           "def transpose(matrix):\n    pass\n",
           """
           f = ns.get("transpose")
           check("defines transpose", lambda: callable(f))
           check("2 x 3 matrix", lambda: f([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]])
           check("1 x 1 matrix", lambda: f([[1]]) == [[1]])
           check("column becomes row", lambda: f([[1], [2], [3]]) == [[1, 2, 3]])
           """,
           "The new row c is made of row[c] for every row in the old matrix. A comprehension inside a comprehension works well.",
           "def transpose(matrix):\n    return [[row[c] for row in matrix] for c in range(len(matrix[0]))]"),
        EX("moving", "moving_average",
           "Write `moving_average(nums, window)` that returns the average of every run of `window` consecutive numbers. `moving_average([1, 2, 3, 4, 5], 3)` is `[2.0, 3.0, 4.0]`. If the window is larger than the list, return an empty list.",
           "def moving_average(nums, window):\n    pass\n",
           """
           f = ns.get("moving_average")
           check("defines moving_average", lambda: callable(f))
           check("window of 3", lambda: f([1, 2, 3, 4, 5], 3) == [2.0, 3.0, 4.0])
           check("window of 1", lambda: f([4, 8], 1) == [4.0, 8.0])
           check("window larger than the list", lambda: f([1, 2], 5) == [])
           check("window equal to length", lambda: f([2, 4, 6], 3) == [4.0])
           """,
           "There are len(nums) - window + 1 windows. Slice nums[i:i + window] for each start i and divide the sum by window.",
           "def moving_average(nums, window):\n    return [sum(nums[i:i + window]) / window for i in range(len(nums) - window + 1)]"),
        EX("flatten", "flatten",
           "Write `flatten(nested)` that turns a list of lists into one flat list, one level deep: `[[1, 2], [3], [], [4, 5]]` becomes `[1, 2, 3, 4, 5]`.",
           "def flatten(nested):\n    pass\n",
           """
           f = ns.get("flatten")
           check("defines flatten", lambda: callable(f))
           check("mixed lengths", lambda: f([[1, 2], [3], [], [4, 5]]) == [1, 2, 3, 4, 5])
           check("empty outer list", lambda: f([]) == [])
           check("strings inside", lambda: f([["a"], ["b", "c"]]) == ["a", "b", "c"])
           """,
           "Two loops: for each inner list, for each item in it, append to the result.",
           "def flatten(nested):\n    result = []\n    for inner in nested:\n        for item in inner:\n            result.append(item)\n    return result"),
        EX("add_bonus", "Fix the hidden side effect",
           "`add_bonus` should return a **new** list with the bonus added to every score and leave the original alone, but it changes the list it was given. Fix it.",
           "def add_bonus(scores, bonus):\n    for i in range(len(scores)):\n        scores[i] += bonus\n    return scores\n",
           """
           f = ns.get("add_bonus")
           check("defines add_bonus", lambda: callable(f))
           check("returns the new scores", lambda: f([1, 2], 10) == [11, 12])
           def untouched():
               orig = [1, 2]
               f(orig, 10)
               return orig == [1, 2]
           check("leaves the original list alone", untouched, "Build a new list instead of changing scores in place.")
           """,
           "A comprehension builds a new list: `[s + bonus for s in scores]`.",
           "def add_bonus(scores, bonus):\n    return [s + bonus for s in scores]", kind="fix"),
        EX("bucket", "Fix the shared default",
           "Calls to `add_item` without a bucket should each start from a fresh empty list. Right now every call shares one list. Fix it, and keep the ability to pass your own bucket.",
           "def add_item(item, bucket=[]):\n    bucket.append(item)\n    return bucket\n",
           """
           f = ns.get("add_item")
           check("defines add_item", lambda: callable(f))
           check("first call gives [1]", lambda: f(1) == [1])
           check("second call gives [2], not [1, 2]", lambda: f(2) == [2], "The default list is shared between calls.")
           check("a passed-in bucket is used", lambda: f(3, [9]) == [9, 3])
           """,
           "Use `bucket=None` as the default and write `if bucket is None: bucket = []` inside.",
           "def add_item(item, bucket=None):\n    if bucket is None:\n        bucket = []\n    bucket.append(item)\n    return bucket", kind="fix"),
    ],
    predict=[
        PRED("a = [1, 2]\nb = a\nb.append(3)\nprint(a)",
             "`b = a` gave the same list a second name, so appending through `b` changes what `a` sees."),
        PRED("grid = [[0] * 2] * 2\ngrid[0][0] = 5\nprint(grid)",
             "`* 2` repeats a reference to the same inner list, so both rows are one object."),
        PRED("nums = [3, 1, 2]\nprint(nums.sort())",
             "`sort()` sorts in place and returns None, so None is printed."),
        PRED('print(list(zip("ab", [1, 2])))',
             "`zip` pairs the items position by position into tuples."),
        PRED("nums = [1, 2, 3, 4, 5]\nprint(nums[1:4], nums[::-1][:2], [n * 2 for n in nums if n % 2])",
             "`[1:4]` is positions 1 to 3. Reversed, the first two are 5 and 4. The comprehension keeps odd n (1, 3, 5) and doubles them."),
        PRED("def add(item, bucket=[]):\n    bucket.append(item)\n    return bucket\n\nadd(1)\nprint(add(2))",
             "The default list is created once and shared, so the second call sees the item added by the first."),
    ],
    cards=[
        CARD("What does 'lists are mutable' mean?", "You can change a list in place: assign to an index, append, remove and sort."),
        CARD("`append` versus `extend`?", "`append(x)` adds x as one item. `extend(seq)` adds each item of seq."),
        CARD("What does `nums.sort()` return?", "`None`. It sorts in place. `sorted(nums)` returns a new sorted list."),
        CARD("After `b = a` for a list, are there two lists?", "No. Two names refer to one list, so changing it through either name shows up in both."),
        CARD("How do you copy a list, and what is a shallow copy?", "`a.copy()`, `a[:]` or `list(a)`. A shallow copy copies the outer list only; nested lists are still shared."),
        CARD("Why is `[[0] * 3] * 3` a trap for making a grid?", "It repeats one inner list three times, so all rows are the same object. Use `[[0] * 3 for _ in range(3)]`."),
        CARD("What is the syntax of a list comprehension with a filter?", "`[expression for item in sequence if condition]`."),
        CARD("How do you write a tuple with one item?", "`(5,)`. The trailing comma makes the tuple; `(5)` is just the number 5."),
        CARD("Why is `def f(x, items=[])` dangerous?", "The default list is created once and shared by every call that uses the default. Use `None` and create the list inside."),
        CARD("Why is `x in some_list` slow for big lists?", "It scans item by item: O(n). A set does the same check in about constant time."),
    ],
)
