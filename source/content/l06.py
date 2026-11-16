from dsl import *
import textwrap


def DEEP(x):
    """A "Going deeper" note (NOTE kind "deep"). Falls back to the same dict shape if dsl.py does not know the kind yet."""
    try:
        return NOTE("deep", x)
    except AssertionError:
        return {"t": "note", "k": "deep", "x": textwrap.dedent(x).strip("\n")}


LESSON = lesson(
    id="py06", track="py", n=6, title="Lists and tuples", minutes=80,
    summary="Mutable sequences, sorting with keys and lambdas, how tuples compare, aliasing and copying (including through functions and +=), comprehensions, safe looping, tuples, unpacking, enumerate and zip, and the costs of list operations.",
    goals=[
        "Create, index, slice and change lists",
        "Sort with key functions, lambdas and tuple keys, and use stability",
        "Explain aliasing: why b = a, a parameter and a += [x] do not copy a list",
        "Write list comprehensions with a condition, and avoid changing a list while looping over it",
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
        - `del items[i]` removes the item at position `i`

        `remove(x)` and `index(x)` raise `ValueError` when `x` is not in the list, so test `if x in items:` first when it might be missing."""),
        DEEP("""
        **Slice assignment** replaces a whole stretch of a list in place: `a[1:3] = []` deletes positions 1 and 2, `a[0:1] = ["x", "y"]` replaces one item with two, and `a[:] = new_items` swaps the entire contents of the *same* list object, so every other name for that list sees the new contents."""),

        H("Sorting"),
        CODE("""
        nums = [3, 1, 2]
        print(sorted(nums), nums)
        result = nums.sort()
        print(result, nums)
        words = ["banana", "apple", "Cherry"]
        print(sorted(words))
        print(sorted(words, key=str.lower))
        print(sorted(words, key=len, reverse=True))
        """),
        NOTE("trap", """
        `list.sort()` sorts **in place** and returns `None`. Writing `nums = nums.sort()` destroys your list. Use `sorted(nums)` when you want a new sorted list and the original left alone."""),
        P("""
        Plain `sorted(words)` puts `"Cherry"` first because strings compare by character code and capitals come before lower case (lesson 5). The `key` argument fixes that: it is a function applied to each item to decide its order, which is why functions being values (lesson 4) matters. `key=str.lower` sorts by the lower-case form while keeping the original words.

        Sorting is **stable**: items with equal keys keep their original relative order. Look at the last line above: `banana` and `Cherry` both have length 6, and `banana` stays first because it came first, even with `reverse=True`."""),
        P("""
        Often the key is a tiny function you need only once. A **lambda** writes it inline: `lambda w: w[-1]` is a function that takes `w` and returns `w[-1]`. It is the same as a `def` whose body is a single `return`, just without a name. The two sorts below are identical; notice that `tea` stays before `soda` (both end in `a`) because the sort is stable."""),
        CODE("""
        drinks = ["tea", "milk", "juice", "soda"]

        def last_letter(w):
            return w[-1]

        print(sorted(drinks, key=last_letter))
        print(sorted(drinks, key=lambda w: w[-1]))
        """),
        P("""
        **How tuples and lists compare.** Like strings, they compare item by item from the left, and the first difference decides: `(1, "z") < (2, "a")` because 1 < 2, and the second items are never looked at. Only on a tie does Python move on to the next item. That makes a tuple the natural key for "sort by this, then by that". A key can also look things up in another list, which lets you sort *positions* instead of values."""),
        CODE("""
        print((1, "z") < (2, "a"), (2, "a") < (2, "b"), (2, 5) < (2, 5, 0))
        rota = [("Ward B", "Noor"), ("Ward A", "Sam"), ("Ward B", "Ali")]
        print(sorted(rota))
        words = ["fig", "kiwi", "date", "yam"]
        print(sorted(words, key=lambda w: (-len(w), w)))
        temps = [37.2, 39.1, 36.8]
        print(sorted(range(len(temps)), key=lambda i: temps[i]))
        """),
        P("""
        The key `(-len(w), w)` means "longest first, then alphabetical". The last line sorts the positions 0, 1, 2 by the temperature at each position, giving the order coolest first: position 2, then 0, then 1."""),

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
        P("""
        **Through a function.** A parameter is one more name for the caller's object. Changing the object (`append`, `sort`, assigning to an index) shows up in the caller. Assigning a new value to the parameter only moves the local name, exactly as with numbers in lesson 4."""),
        CODE("""
        def add_dose(doses):
            doses.append(5)

        def replace_doses(doses):
            doses = doses + [5]

        mine = [10]
        add_dose(mine)
        print(mine)
        replace_doses(mine)
        print(mine)
        """),
        P("""
        **`+=` on a list changes it in place.** For numbers and strings, `x += y` means `x = x + y`. For a list it does not: `a += [3]` extends the existing list (like `extend`), so every alias sees it, while `a = a + [4]` builds a new list and moves only the name `a`."""),
        CODE("""
        a = [1, 2]
        b = a
        a += [3]
        print(b)
        a = a + [4]
        print(a, b)
        """),
        NOTE("trap", """
        A copy is **shallow**: it copies the outer list but not the lists inside it, so nested lists are still shared. For fully independent nested data use `deepcopy` from the `copy` module."""),
        CODE("""
        import copy

        grid = [[0, 0], [0, 0]]
        shallow = grid.copy()
        deep = copy.deepcopy(grid)
        shallow[0][0] = 9
        print(grid)
        print(deep)
        """),
        P("""
        `import copy` loads `copy`, one of the **modules** (files of ready-made tools) that come with Python, and `copy.deepcopy` means "the `deepcopy` function inside `copy`". Lesson 7 uses more modules."""),
        CODE("""
        bad = [[0] * 2] * 2
        bad[0][0] = 5
        print(bad)

        good = [[0] * 2 for _ in range(2)]
        good[0][0] = 5
        print(good)
        """),
        P("""
        `[[0] * 2] * 2` repeats the **same** inner list twice, so a change shows up in both rows. A list comprehension (below) builds a fresh row each time, which is the safe way to make a grid. The loop name `_` says "I don't need the number", as with `partition` in lesson 5."""),

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
        The standard fix is to use `None` as the default and create the list inside the function: `if bucket is None: bucket = []`. Test `is None`, not `if not bucket:`. An empty list that the caller passes in is falsy too, and would be quietly swapped for a new list the caller never sees."""),

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
        P("""
        **Two `for`s in one comprehension** run in the same order as the nested loops they replace: the first `for` is the outer loop. A comprehension *inside* another one builds a list of lists, one inner list per outer item."""),
        CODE("""
        pairs = []
        for letter in "AB":
            for digit in "12":
                pairs.append(letter + digit)
        print(pairs)
        print([letter + digit for letter in "AB" for digit in "12"])
        print([[r * c for c in range(1, 4)] for r in range(1, 3)])
        """),
        NOTE("trap", """
        Do not remove items from (or add items to) a list while a `for` loop is walking over it. The loop keeps its own position counter. Removing an item shifts the rest left, so the item after it is skipped. Loop over a copy (`for n in nums[:]:`) or build a new list with a comprehension."""),
        CODE("""
        nums = [1, 2, 2, 3]
        for n in nums:
            if n == 2:
                nums.remove(n)
        print(nums)

        nums = [1, 2, 2, 3]
        print([n for n in nums if n != 2])
        """),
        DEEP("""
        A comprehension's loop name lives only inside its brackets: after `sq = [x * x for x in range(3)]`, a name `x` defined earlier keeps its old value. A plain `for` loop is different: its name stays behind afterwards, holding the last item."""),

        H("A few more tools"),
        CODE("""
        kit = ["gauze", "saline", "tape"]
        for n, item in enumerate(kit, start=1):
            print(f"{n}. {item}")
        first, *rest = kit
        print(first, rest)
        print(any([len(k) > 5 for k in kit]), all([len(k) > 5 for k in kit]))
        print(max(kit, key=len), list(reversed(kit)))
        """),
        P("""
        - `enumerate(seq, start=1)` counts from 1, for numbering that people read
        - `first, *rest = seq` puts the first item in `first` and a **list** of all the others in `rest` (the starred name may also come last or in the middle)
        - `any(list)` is True if at least one item is truthy; `all(list)` is True if every item is, and `all([])` is True
        - `max(seq, key=...)` returns the item with the biggest key (the first one if several tie); `min` works the same way
        - `reversed(seq)` walks backwards without making a copy; wrap it in `list()` to see the items"""),

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
        A **tuple** is an ordered, immutable sequence. Use one for a fixed group of values that belong together, such as coordinates or a pair returned from a function. Note the trailing comma in `(5,)`: the comma makes the tuple, not the brackets.

        "Immutable" means the tuple always holds the **same objects**: you cannot replace, add or remove one. If one of those objects is a list, the list itself can still change. For the same reason a tuple can be a dictionary key (lesson 7) only when everything inside it could be a key too: `(1, "a")` works, while `([1], 2)` raises `TypeError`."""),
        CODE("""
        t = ([1], "x")
        t[0].append(2)
        print(t)
        print(len(t))
        """),

        H("zip: walk through lists together"),
        CODE("""
        names = ["Ada", "Alan", "Grace"]
        years = [1815, 1912, 1906]
        for name, year in zip(names, years):
            print(name, year)
        print(list(zip(names, years)))

        short = zip(names, [1815])
        print(list(short))
        print(list(short))
        """),
        P("""
        `zip` stops at the end of the **shortest** input and silently drops the rest. It also hands out its pairs only once: a `zip` is an *iterator*, so after one pass (here the first `list(short)`) it is used up, and a second pass gets nothing. Call `zip` again when you need another pass. `enumerate` behaves the same way."""),

        H("What operations cost"),
        P("""
        Checking `x in some_list` scans from the start until it finds a match, so on average it takes time proportional to the length of the list, written O(n). Reading `nums[i]` and appending to the end are fast. Inserting at the front is slow, because every other item has to shuffle along. When you need many fast membership checks, a set (next lesson) is the right tool."""),
        DEEP("""
        Costs multiply inside loops. The `dedupe` exercise below checks `item not in result` once per item, and each check scans `result`, so for n items the work grows roughly like n times n (O(n²)): instant for 100 items, slow for 100,000. Lesson 7 has the fast tools: a set remembers what has been seen in about constant time, and `list(dict.fromkeys(items))` removes duplicates in one line while keeping the order."""),
    ],
    exercises=[
        EX("dedupe", "dedupe",
           "Write `dedupe(items)` that returns a new list with duplicates removed, keeping the first occurrence of each item in its original order. The input list must not be changed.",
           "def dedupe(items):\n    pass\n",
           """
           f = ns.get("dedupe")
           check("defines dedupe", lambda: callable(f), "Start with def dedupe(items):")
           check_eq("[3, 1, 3, 2, 1]", lambda: f([3, 1, 3, 2, 1]), [3, 1, 2], "Keep the first time you see each item, in the original order (not sorted).")
           check_eq("empty list", lambda: f([]), [], "Return an empty list, not None.")
           check_eq("strings", lambda: f(["a", "a", "b"]), ["a", "b"])
           check_eq("already unique", lambda: f([5, 4]), [5, 4])
           def untouched():
               orig = [1, 1, 2]
               f(orig)
               return orig == [1, 1, 2]
           check("does not change the input", untouched, "Build and return a new list; never remove from the list you were given.")
           """,
           "Start with an empty result. For each item, append it only if it is not already in result.",
           "def dedupe(items):\n    result = []\n    for item in items:\n        if item not in result:\n            result.append(item)\n    return result"),
        EX("rotate", "rotate",
           "Write `rotate(items, k)` that returns a new list rotated left by `k` places: `rotate([1, 2, 3, 4, 5], 2)` is `[3, 4, 5, 1, 2]`. `k` may be larger than the list, zero or negative. The input must not change.",
           "def rotate(items, k):\n    pass\n",
           """
           f = ns.get("rotate")
           check("defines rotate", lambda: callable(f))
           check_eq("rotate([1, 2, 3, 4, 5], 2)", lambda: f([1, 2, 3, 4, 5], 2), [3, 4, 5, 1, 2], "Join two slices: from k to the end, then the start up to k.")
           check_eq("k = 0", lambda: f([1, 2, 3], 0), [1, 2, 3])
           check_eq("k larger than the list", lambda: f([1, 2, 3], 4), [2, 3, 1], "Rotating 3 items by 4 is the same as by 1: use k % len(items).")
           check_eq("empty list", lambda: f([], 3), [], "k % 0 is a ZeroDivisionError: return [] for an empty list first.")
           check_eq("negative k rotates right", lambda: f([1, 2, 3, 4], -1), [4, 1, 2, 3], "% with a positive length turns -1 into 3, which is a right rotation by 1.")
           def untouched():
               orig = [1, 2, 3]
               f(orig, 1)
               return orig == [1, 2, 3]
           check("does not change the input", untouched, "Slices and + build new lists; pop/insert change the original.")
           """,
           "Reduce k with `k % len(items)` (watch out for an empty list), then join two slices: `items[k:] + items[:k]`.",
           "def rotate(items, k):\n    if not items:\n        return []\n    k = k % len(items)\n    return items[k:] + items[:k]"),
        EX("transpose", "transpose",
           "Write `transpose(matrix)` that swaps rows and columns of a list of equal-length rows: `[[1, 2, 3], [4, 5, 6]]` becomes `[[1, 4], [2, 5], [3, 6]]`. The rows of the result must be lists, and an empty matrix `[]` gives `[]`.",
           "def transpose(matrix):\n    pass\n",
           """
           f = ns.get("transpose")
           check("defines transpose", lambda: callable(f))
           check_eq("2 x 3 matrix", lambda: f([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5], [3, 6]], "Rows must be lists. zip gives tuples, so convert each one with list(...).")
           check_eq("1 x 1 matrix", lambda: f([[1]]), [[1]])
           check_eq("column becomes row", lambda: f([[1], [2], [3]]), [[1, 2, 3]], "The number of new rows is the length of an old row: len(matrix[0]).")
           check_eq("empty matrix", lambda: f([]), [], "An empty matrix has no rows, so matrix[0] does not exist: return [] first.")
           """,
           "New row c is made of row[c] for every row of the old matrix: `[row[c] for row in matrix]`. Wrap that in a second comprehension over c in range(len(matrix[0])), after handling the empty matrix.",
           "def transpose(matrix):\n    if not matrix:\n        return []\n    return [[row[c] for row in matrix] for c in range(len(matrix[0]))]"),
        EX("moving", "moving_average",
           "Write `moving_average(nums, window)` that returns the average of every run of `window` consecutive numbers. `moving_average([1, 2, 3, 4, 5], 3)` is `[2.0, 3.0, 4.0]`. If the window is larger than the list, return an empty list.",
           "def moving_average(nums, window):\n    pass\n",
           """
           f = ns.get("moving_average")
           check("defines moving_average", lambda: callable(f))
           check_eq("window of 3", lambda: f([1, 2, 3, 4, 5], 3), [2.0, 3.0, 4.0], "Averages are floats: divide with /, never //.")
           check_eq("halves are kept", lambda: f([1, 2], 2), [1.5], "// throws away the .5. Use / for a true average.")
           check_eq("window of 1", lambda: f([4, 8], 1), [4.0, 8.0], "Each window of one number averages to that number, as a float.")
           check_eq("window larger than the list", lambda: f([1, 2], 5), [], "len(nums) - window + 1 is negative here, and range of a negative number is empty.")
           check_eq("window equal to length", lambda: f([2, 4, 6], 3), [4.0], "There is exactly one window: start at 0, and range(len(nums) - window + 1) must include it.")
           """,
           "There are len(nums) - window + 1 windows. Slice nums[i:i + window] for each start i and divide the sum by window with /.",
           "def moving_average(nums, window):\n    return [sum(nums[i:i + window]) / window for i in range(len(nums) - window + 1)]"),
        EX("flatten", "flatten",
           "Write `flatten(nested)` that turns a list of lists into one flat list, one level deep: `[[1, 2], [3], [], [4, 5]]` becomes `[1, 2, 3, 4, 5]`.",
           "def flatten(nested):\n    pass\n",
           """
           f = ns.get("flatten")
           check("defines flatten", lambda: callable(f))
           check_eq("mixed lengths", lambda: f([[1, 2], [3], [], [4, 5]]), [1, 2, 3, 4, 5], "Loop over the inner lists, and over the items of each one.")
           check_eq("empty outer list", lambda: f([]), [])
           check_eq("strings inside", lambda: f([["a"], ["b", "c"]]), ["a", "b", "c"], "append each item, not each inner list.")
           check_eq("only one level", lambda: f([[1, [2]], [3]]), [1, [2], 3], "Go one level deep only: a list inside an inner list stays as it is.")
           """,
           "Two loops: for each inner list, for each item in it, append to the result (or one comprehension with two fors, outer loop first).",
           "def flatten(nested):\n    result = []\n    for inner in nested:\n        for item in inner:\n            result.append(item)\n    return result"),
        EX("add_bonus", "Fix the hidden side effect",
           "`add_bonus` should return a **new** list with the bonus added to every score and leave the original alone, but it changes the list it was given. Fix it.",
           "def add_bonus(scores, bonus):\n    for i in range(len(scores)):\n        scores[i] += bonus\n    return scores\n",
           """
           f = ns.get("add_bonus")
           check("defines add_bonus", lambda: callable(f))
           check_eq("returns the new scores", lambda: f([1, 2], 10), [11, 12])
           def untouched():
               orig = [1, 2]
               f(orig, 10)
               return orig == [1, 2]
           check("leaves the original list alone", untouched, "scores is another name for the caller's list. Build a new list instead of changing scores in place.")
           """,
           "A comprehension builds a new list: `[s + bonus for s in scores]`.",
           "def add_bonus(scores, bonus):\n    return [s + bonus for s in scores]", kind="fix"),
        EX("bucket", "Fix the shared default",
           "Calls to `add_item` without a bucket should each start from a fresh empty list. Right now every call shares one list. Fix it, and keep the ability to pass your own bucket, even an empty one.",
           "def add_item(item, bucket=[]):\n    bucket.append(item)\n    return bucket\n",
           """
           f = ns.get("add_item")
           check("defines add_item", lambda: callable(f))
           check_eq("first call", lambda: f(1), [1])
           check_eq("second call is fresh", lambda: f(2), [2], "The default list is created once and shared between calls. Use None as the default.")
           check_eq("a passed-in bucket is used", lambda: f(3, [9]), [9, 3])
           def own_empty():
               b = []
               r = f(1, b)
               return b == [1] and r is b
           check("an empty bucket you pass in is used", own_empty, "`if not bucket` also replaces an empty list the caller passed in, so the caller's list stays empty. Test `if bucket is None`.")
           """,
           "Use `bucket=None` as the default and write `if bucket is None: bucket = []` inside.",
           "def add_item(item, bucket=None):\n    if bucket is None:\n        bucket = []\n    bucket.append(item)\n    return bucket", kind="fix"),
        EX("remove_negatives", "Fix the skipping loop",
           """
           `remove_negatives(nums)` must remove every negative number from the list it is given (the caller relies on its own list being cleaned) and return that same list. It deletes items while a loop walks over the positions, so it skips items and then runs off the end with `IndexError`. Fix it.""",
           "def remove_negatives(nums):\n    for i in range(len(nums)):\n        if nums[i] < 0:\n            del nums[i]\n    return nums\n",
           """
           f = ns.get("remove_negatives")
           check("defines remove_negatives", lambda: callable(f))
           check_eq("[-1, -2, 3]", lambda: f([-1, -2, 3]), [3], "Deleting -1 shifts -2 into position 0, which the loop has already passed, and the list is now shorter than range(len(nums)) promised. Loop over a copy instead, for n in nums[:]:, and remove n from nums.")
           check_eq("[1, -1, -1, -1, 2]", lambda: f([1, -1, -1, -1, 2]), [1, 2], "Several negatives in a row expose the skipping.")
           check_eq("no negatives", lambda: f([0, 4]), [0, 4], "0 is not negative.")
           check_eq("empty list", lambda: f([]), [])
           def same_list():
               b = [-5, 6, -7]
               r = f(b)
               return b == [6] and r is b
           check("cleans the caller's own list", same_list, "nums = [...] builds a new list and the caller's list keeps its negatives. Remove from nums itself while looping over nums[:], or replace its contents with nums[:] = [...].")
           """,
           "The loop must not walk over the list it is changing. Walk over a copy, `for n in nums[:]:`, and remove each negative n from the original with nums.remove(n).",
           "def remove_negatives(nums):\n    for n in nums[:]:\n        if n < 0:\n            nums.remove(n)\n    return nums", kind="fix"),
        EX("numbered", "numbered",
           """
           Write `numbered(items)` that returns a new list of strings numbering the items from 1 for a printed checklist.

           - `numbered(["gauze", "tape"])` is `["1. gauze", "2. tape"]`""",
           "def numbered(items):\n    pass\n",
           """
           f = ns.get("numbered")
           check("defines numbered", lambda: callable(f))
           check_eq("two items", lambda: f(["gauze", "tape"]), ["1. gauze", "2. tape"], "Count from 1, not 0: enumerate(items, start=1).")
           check_eq("empty list", lambda: f([]), [])
           check_eq("twelve items", lambda: f(list("abcdefghijkl"))[-1], "12. l", "Use the position as a number in an f-string: f\\"{n}. {item}\\".")
           check_eq("repeated items keep their own numbers", lambda: f(["x", "x"]), ["1. x", "2. x"], "Do not look items up with index(): duplicates would all get the first position.")
           """,
           "`[f\"{n}. {item}\" for n, item in enumerate(items, start=1)]`, or a loop that appends each line.",
           'def numbered(items):\n    return [f"{n}. {item}" for n, item in enumerate(items, start=1)]'),
    ],
    predict=[
        PRED("def add_tip(bill):\n    bill.append(5)\n\nlog = [20]\nadd_tip(log)\nprint(log)",
             "`bill` is a second name for the list `log` names, so appending through it changes the caller's list. Nothing was returned, and nothing needed to be.",
             traps={"[20]": "A parameter is another name for the caller's object. `append` changes that object, so `log` sees it.",
                    "None": "`print(log)` shows the list. The function returned None, but that value was never printed."}, id="p0"),
        PRED("row = [0, 0]\ngrid = [row, row]\ngrid[0][1] = 7\nprint(grid)",
             "Both rows are the one list named `row`, so changing it through `grid[0]` shows in `grid[1]` too.",
             traps={"[[0, 7], [0, 0]]": "`grid` holds the same list twice, not two copies. Make separate rows with `[0, 0]` twice or a comprehension."}, id="p1"),
        PRED("nums = [3, 1, 2]\nnums = nums.sort()\nprint(nums)",
             "`sort()` sorts in place and returns None, and the assignment then points `nums` at that None. The sorted list is lost.",
             traps={"[1, 2, 3]": "`sort()` returns None, and `nums = ...` stored that None. Write `nums.sort()` alone, or `nums = sorted(nums)`."}, id="p2"),
        PRED('z = zip("xyz", range(10))\nprint(len(list(z)), list(z))',
             "`zip` stops at the shorter input, so there are 3 pairs. The first `list(z)` uses the zip up; the second gets nothing.",
             traps={"10 []": "`zip` stops at the end of the shortest input: `\"xyz\"` has 3 characters.",
                    "3 [('x', 0), ('y', 1), ('z', 2)]": "A zip can be walked only once. The first `list(z)` used it up, so the second is empty."}, id="p3"),
        PRED("nums = [1, 2, 3, 4, 5]\nprint(nums[1:4], nums[::-1][:2], [n * 2 for n in nums if n % 2])",
             "`[1:4]` is positions 1 to 3. Reversed, the first two are 5 and 4. The comprehension keeps odd n (1, 3, 5) and doubles them.", id="p4"),
        PRED('def log_visit(name, seen=[]):\n    seen.append(name)\n    return len(seen)\n\nprint(log_visit("Ada"), log_visit("Alan"), log_visit("Grace", []))',
             "The default list is created once and shared, so the second call sees Ada too (2). The third call passes its own new list, so it starts from empty (1).",
             traps={"1 1 1": "The default `[]` is made once, when the function is defined, so calls that use it share one list.",
                    "1 2 3": "The third call passes its own empty list, so the shared default is not used: 1."}, id="p5"),
        PRED('print((2, "a") < (1, "z"), sorted([(2, "b"), (1, "c"), (2, "a")]))',
             "Tuples compare item by item: 2 > 1 settles the first comparison, so the letters are never looked at. Sorting uses the same rule: by first item, then by second on a tie.",
             traps={"True [(1, 'c'), (2, 'a'), (2, 'b')]": "The first items are compared first, and 2 < 1 is False. The second items only matter on a tie.",
                    "False [(1, 'c'), (2, 'b'), (2, 'a')]": "On a tie in the first item, the second item decides: 'a' comes before 'b'."}, id="p-tuple-cmp"),
        PRED('words = ["pear", "fig", "kiwi", "yam"]\nprint(sorted(words, key=len))',
             "The key looks only at length. fig and yam (3) come before pear and kiwi (4), and within each length the original order is kept, because sorting is stable.",
             traps={"['fig', 'yam', 'kiwi', 'pear']": "With `key=len`, only the length matters. Ties are not sorted alphabetically; they keep their original order (pear came before kiwi)."}, id="p-stable"),
        PRED("a = [1]\nb = a\na += [2]\na = a + [3]\nprint(a, b)",
             "`a += [2]` extends the one list both names share, so `b` sees the 2. `a = a + [3]` builds a new list and moves only `a`.",
             traps={"[1, 2, 3] [1]": "For lists, `+=` changes the existing list in place, so the alias `b` sees the 2.",
                    "[1, 2, 3] [1, 2, 3]": "`a = a + [3]` makes a new list and moves the name `a`; `b` still names the old one."}, id="p-iadd"),
        PRED('shifts = ["ok", "late", "late", "ok"]\nfor s in shifts:\n    if s == "late":\n        shifts.remove(s)\nprint(shifts)',
             "When the first `late` (position 1) is removed, the second `late` slides into position 1, which the loop has already visited. The loop moves on to position 2 (now `ok`), so one `late` survives.",
             traps={"['ok', 'ok']": "Removing while looping shifts items left, so the item after each removed one is skipped. Loop over a copy: `for s in shifts[:]`."}, id="p-loop-remove"),
        PRED('t = ([1], "x")\nt[0].append(2)\nprint(t)',
             "The tuple still holds the same two objects, so nothing about the tuple changed. The list inside it is mutable, and it grew.",
             traps={"TypeError": "You cannot replace an item of a tuple, but `t[0].append(2)` does not replace anything: it changes the list the tuple holds.",
                    "([1], 'x')": "The tuple holds the list itself, not a copy, so the change to that list shows."}, id="p-tuple-mut"),
        PRED('first, *rest = "lime"\nprint(first, rest)',
             "Unpacking walks the string: `first` gets `l`, and the starred name collects everything else **as a list**.",
             traps={"l ime": "The starred name always collects a list, even from a string: `['i', 'm', 'e']`."}, id="p-star"),
    ],
    cards=[
        CARD("What does 'lists are mutable' mean?", "You can change a list in place: assign to an index, append, remove and sort.", id="c0"),
        CARD("`a = [1]`, then `a.append([2, 3])`: what is `a`?", "`[1, [2, 3]]`: `append` adds its argument as one item. `extend([2, 3])` would give `[1, 2, 3]`.", id="c1"),
        CARD("What does `nums.sort()` return?", "`None`. It sorts in place. `sorted(nums)` returns a new sorted list.", id="c2"),
        CARD("After `b = a` for a list, are there two lists?", "No. Two names refer to one list, so changing it through either name shows up in both.", id="c3"),
        CARD("Name three ways to copy a list `a`.", "`a.copy()`, `a[:]` and `list(a)`. All three are shallow copies.", id="c4"),
        CARD("`g = [[0]]`, `h = g.copy()`, `h[0].append(1)`: what is `g`?", "`[[0, 1]]`. A shallow copy shares the inner lists. `copy.deepcopy(g)` would not.", id="c-shallow"),
        CARD("Why is `[[0] * 3] * 3` a trap for making a grid?", "It repeats one inner list three times, so all rows are the same object. Use `[[0] * 3 for _ in range(3)]`.", id="c5"),
        CARD("What is the syntax of a list comprehension with a filter?", "`[expression for item in sequence if condition]`.", id="c6"),
        CARD("How do you write a tuple with one item?", "`(5,)`. The trailing comma makes the tuple; `(5)` is just the number 5.", id="c7"),
        CARD("Why is `def f(x, items=[])` dangerous?", "The default list is created once and shared by every call that uses the default. Use `None` and create the list inside.", id="c8"),
        CARD("What is wrong with `if not bucket: bucket = []` as the fix for a `bucket=None` default?", "An empty list the caller passes in is falsy too, so it is replaced and the caller's list never changes. Test `if bucket is None`.", id="c-is-none"),
        CARD("Why is `x in some_list` slow for a big list?", "It checks item by item from the start until it finds a match, so the time grows with the length: O(n).", id="c9"),
        CARD("`(2, \"a\") < (1, \"z\")`: True or False?", "False. Tuples compare item by item from the left; 2 > 1 settles it, so the letters are never compared.", id="c-tuple-cmp"),
        CARD("What does 'sorting is stable' mean?", "Items with equal keys keep their original order. `sorted([\"pear\", \"fig\", \"kiwi\"], key=len)` keeps pear before kiwi.", id="c-stable"),
        CARD("Write `def key(w): return w[-1]` as a lambda.", "`lambda w: w[-1]`, e.g. `sorted(words, key=lambda w: w[-1])`.", id="c-lambda"),
        CARD("`a = [1]; b = a; a += [2]`: what is `b`?", "`[1, 2]`. For lists `+=` extends in place; `a = a + [2]` would have made a new list and left `b` as `[1]`.", id="c-iadd"),
        CARD("A function does `items.append(9)` on a list it was given. Does the caller's list change?", "Yes. The parameter is another name for the caller's list. Only reassigning the parameter (`items = ...`) leaves the caller alone.", id="c-param"),
        CARD("What goes wrong when you `remove` items from a list inside `for n in that_list:`?", "Items shift left and the loop skips the item after each removal. Loop over a copy (`nums[:]`) or build a new list.", id="c-loop-remove"),
        CARD("Can `([1], 2)` be a dictionary key?", "No (TypeError): a tuple can be a key only if everything inside it can. The list inside could change.", id="c-tuple-key"),
        CARD("`first, *rest = [1, 2, 3]`: what are `first` and `rest`?", "`first` is 1 and `rest` is the list `[2, 3]`.", id="c-star"),
        CARD("`z = zip(\"ab\", [1, 2, 3])`: what are `list(z)` and then `list(z)` again?", "`[('a', 1), ('b', 2)]` (stops at the shortest), then `[]`: a zip can be used only once.", id="c-zip-once"),
    ],
)
