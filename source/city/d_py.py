from dsl import *

DISTRICT = district(
    "py",
    opener=[
        """
        You step off the night train into **Calx**, the Clockwork City, with a letter of apprenticeship and a bag that is mostly sandwiches. The station clock says 06:00. It has said 06:00 for eleven years.""",
        """
        Everything here runs on small programs written by the Founders: the trams, the fountains, the bells, the bread ovens. The Founders wrote no comments. The last Readers, who could make sense of their programs, have retired to the coast.""",
        """
        A brass cabinet on wheels rolls up beside you. It is full of pigeonholes, and every pigeonhole is labelled. "I am NIT," it says. "Index of Names and Things. You are late by four minutes and eleven seconds, which is very early by local standards."

        "Every stopped machine in this city has the same last line in its log," NIT adds, and slides out a card:

        `waiting for MERIDIAN`""",
        """
        "Your first district is the **Workshop Quarter**. Its benches, trams and stalls have all stopped. Learn to read their programs, and you can start them again. Learn enough, and we might find out what MERIDIAN is."

        Payload: below is the station clock's program. Read it, predict what it prints, then run it.

        ```
        hour = 6
        minute = 0
        print(f"{hour:02d}:{minute:02d}")
        ```
        Why does it never move? Nothing in it changes `minute`. You will fix programs like this all through the Quarter.""",
    ],
    ending=[
        """
        The Bench Automaton shudders, wheezes, and starts sorting bolts by size. Across the Quarter, trams move, Mrs Pell's till prints receipts a person can read, and Juno's signs are back in order.""",
        """
        NIT slides out the Automaton's log. Every line is fine, except the last:

        `inventory complete. waiting for MERIDIAN`

        "The Workshop works," NIT says. "But it is still waiting. The next district is the Conveyor Works, where they move everything by belt and nobody moves anything by hand. Bring your Bench Key." """,
    ],
    archive=[
        ARCHIVE("jacquard", "1804", "The loom that read cards",
                "Joseph Marie Jacquard demonstrated a loom controlled by a chain of punched cards: each card's holes chose which threads were lifted, so a pattern could be changed by changing the cards. It is an early example of a machine following stored instructions, and punched cards later carried data and programs for over a century.",
                "Encyclopaedia Britannica, \"Jacquard loom\""),
        ARCHIVE("lovelace", "1843", "Notes on the Analytical Engine",
                "Ada Lovelace translated an Italian paper about Charles Babbage's proposed Analytical Engine and added her own notes, longer than the paper. Her Note G sets out, step by step, how the engine could compute Bernoulli numbers, and is often called the first published computer program. She also argued that such a machine could act on symbols other than numbers.",
                "Encyclopaedia Britannica, \"Ada Lovelace\""),
        ARCHIVE("fortran", "1957", "FORTRAN",
                "A team at IBM led by John Backus released FORTRAN (FORmula TRANslation), the first widely used high-level programming language. Programmers could write formulas instead of machine instructions, and a compiler translated them into fast machine code.",
                "IBM, \"Fortran\" (IBM Heritage)"),
        ARCHIVE("bug", "1947", "The moth in the relay",
                "Operators of the Harvard Mark II computer found a moth trapped in a relay, taped it into the logbook and wrote \"First actual case of bug being found.\" The joke worked because engineers already called faults bugs. The logbook page survives in a museum.",
                "Smithsonian National Museum of American History, \"Log Book With Computer Bug\""),
        ARCHIVE("goto", "1968", "Structured programming",
                "Edsger Dijkstra's letter \"Go To Statement Considered Harmful\" in Communications of the ACM argued that jumping freely around a program makes it hard to reason about. The structured style that followed, built from sequence, if/else and loops, is the style Python is built around: Python has no goto at all.",
                "Communications of the ACM, March 1968"),
        ARCHIVE("ieee754", "1985", "IEEE 754 floating point",
                "The IEEE 754 standard fixed how computers store and round floating-point numbers, so the same calculation gives the same answer on different machines. It stores numbers in binary, which is why 0.1 + 0.2 is not exactly 0.3 in Python and nearly every other language.",
                "IEEE Standard 754"),
        ARCHIVE("ascii", "1963", "ASCII, then Unicode",
                "ASCII, first published in 1963, gave each English letter, digit and symbol a 7-bit number: 'A' is 65. It had no room for most of the world's writing systems. Unicode, first published in 1991, gives a number to characters from every script, and Python 3 strings are Unicode.",
                "Encyclopaedia Britannica, \"ASCII\"; The Unicode Consortium"),
        ARCHIVE("python", "1991", "Python is released",
                "Guido van Rossum began Python as a hobby project over Christmas 1989 and published the first version in February 1991. The name comes from the BBC comedy series Monty Python's Flying Circus, not from the snake.",
                "Python documentation, General FAQ: \"Why is it called Python?\" (docs.python.org)"),
        ARCHIVE("py3", "2008", "Python 3 breaks with the past",
                "Python 3.0, released in December 2008, deliberately broke compatibility to fix old design mistakes: `print` became a function and text became Unicode by default. Python 2 was officially retired on 1 January 2020, so everything in Lime is Python 3.",
                "python.org, \"Sunsetting Python 2\""),
        ARCHIVE("zen", "2004", "The Zen of Python",
                "Tim Peters' 19 short aphorisms about good Python style were written up as PEP 20. Among them: \"Readability counts\" and \"Errors should never pass silently.\" In desktop Python you can read them all by running `import this`.",
                "PEP 20 (peps.python.org/pep-0020)"),
    ],
    quests=[
        JOB("quest", "change", "Side quest: the change maker",
            """
            The tram's change drawer holds coins worth 50, 20, 10, 5, 2 and 1. Write `make_change(amount)` that returns a dictionary of coin to count using as few coins as possible, leaving out coins with a count of 0.

            `make_change(78)` is `{50: 1, 20: 1, 5: 1, 2: 1, 1: 1}`.""",
            "def make_change(amount):\n    pass\n",
            """
            f = ns.get("make_change")
            check("defines make_change", lambda: callable(f))
            check("78", lambda: f(78) == {50: 1, 20: 1, 5: 1, 2: 1, 1: 1})
            check("40 is two 20s", lambda: f(40) == {20: 2})
            check("0 gives an empty dict", lambda: f(0) == {})
            check("every amount up to 200 adds up", lambda: all(sum(c * n for c, n in f(a).items()) == a for a in range(201)))
            """,
            "Go from the largest coin down: count = amount // coin, then amount %= coin. Only store counts above 0.",
            "def make_change(amount):\n    result = {}\n    for coin in [50, 20, 10, 5, 2, 1]:\n        count = amount // coin\n        if count:\n            result[coin] = count\n        amount %= coin\n    return result"),
        JOB("quest", "rle", "Side quest: the loom's pattern code",
            """
            The loom stores patterns compressed: runs of the same character become the character followed by its count. Write `encode(text)` and `decode(code)`.

            - `encode("aaabcc")` is `"a3b1c2"`
            - `decode("a3b1c2")` is `"aaabcc"`

            Counts can be more than one digit (`"x12"`). Patterns contain only letters.""",
            "def encode(text):\n    pass\n\ndef decode(code):\n    pass\n",
            """
            e = ns.get("encode")
            d = ns.get("decode")
            check("defines encode and decode", lambda: callable(e) and callable(d))
            check('encode("aaabcc")', lambda: e("aaabcc") == "a3b1c2")
            check('encode("")', lambda: e("") == "")
            check("encode handles long runs", lambda: e("x" * 12 + "y") == "x12y1")
            check('decode("a3b1c2")', lambda: d("a3b1c2") == "aaabcc")
            check("decode handles two-digit counts", lambda: d("x12y1") == "x" * 12 + "y")
            check("decode(encode(s)) gives s back", lambda: all(d(e(s)) == s for s in ["", "a", "abba", "zzzzzzzzzzzq", "mississippi"]))
            """,
            "encode: walk the text keeping the current character and its run length; when the character changes, write the run. decode: collect digits after each letter until the next letter.",
            "def encode(text):\n    out = \"\"\n    i = 0\n    while i < len(text):\n        j = i\n        while j < len(text) and text[j] == text[i]:\n            j += 1\n        out += text[i] + str(j - i)\n        i = j\n    return out\n\ndef decode(code):\n    out = \"\"\n    i = 0\n    while i < len(code):\n        ch = code[i]\n        j = i + 1\n        while j < len(code) and code[j].isdigit():\n            j += 1\n        out += ch * int(code[i + 1:j])\n        i = j\n    return out"),
        JOB("quest", "angle", "Side quest: the clock hands",
            """
            Write `hand_angle(hour, minute)` that returns the smaller angle in degrees between the hour and minute hands of an analogue clock. The hour hand moves smoothly: at 3:30 it is halfway between 3 and 4.

            - `hand_angle(3, 0)` is `90.0`
            - `hand_angle(3, 30)` is `75.0`
            - `hand_angle(12, 0)` is `0.0`""",
            "def hand_angle(hour, minute):\n    pass\n",
            """
            f = ns.get("hand_angle")
            check("defines hand_angle", lambda: callable(f))
            check("3:00 is 90", lambda: f(3, 0) == 90.0)
            check("3:30 is 75", lambda: f(3, 30) == 75.0, "The hour hand moves 0.5 degrees per minute.")
            check("12:00 is 0", lambda: f(12, 0) == 0.0)
            check("9:00 is 90, the smaller angle", lambda: f(9, 0) == 90.0, "Take the smaller of the angle and 360 minus it.")
            check("6:00 is 180", lambda: f(6, 0) == 180.0)
            """,
            "Minute hand: 6 degrees per minute. Hour hand: 30 * (hour % 12) + 0.5 * minute. Take the difference, then min(diff, 360 - diff).",
            "def hand_angle(hour, minute):\n    m = 6.0 * minute\n    h = 30.0 * (hour % 12) + 0.5 * minute\n    diff = abs(h - m)\n    return min(diff, 360 - diff)"),
        JOB("quest", "roman", "Side quest: the tower's numerals",
            """
            The Meridian's face uses Roman numerals. Write `to_roman(n)` for 1 to 3999, using the subtractive forms (IV, IX, XL, XC, CD, CM).

            `to_roman(1994)` is `"MCMXCIV"`.""",
            "def to_roman(n):\n    pass\n",
            """
            f = ns.get("to_roman")
            check("defines to_roman", lambda: callable(f))
            check("4 is IV", lambda: f(4) == "IV")
            check("9 is IX", lambda: f(9) == "IX")
            check("14 is XIV", lambda: f(14) == "XIV")
            check("1994 is MCMXCIV", lambda: f(1994) == "MCMXCIV")
            check("3999 is MMMCMXCIX", lambda: f(3999) == "MMMCMXCIX")
            """,
            "Keep a list of (value, symbols) pairs from 1000 down to 1, including 900 CM, 400 CD, 90 XC, 40 XL, 9 IX, 4 IV. Take each as many times as it fits.",
            "def to_roman(n):\n    pairs = [(1000, \"M\"), (900, \"CM\"), (500, \"D\"), (400, \"CD\"), (100, \"C\"), (90, \"XC\"), (50, \"L\"), (40, \"XL\"), (10, \"X\"), (9, \"IX\"), (5, \"V\"), (4, \"IV\"), (1, \"I\")]\n    out = \"\"\n    for value, sym in pairs:\n        while n >= value:\n            out += sym\n            n -= value\n    return out"),
        JOB("quest", "luhn", "Side quest: check the ticket number",
            """
            Tram season tickets carry a check digit using the **Luhn algorithm** (the same one used on bank card numbers). Write `luhn_ok(number)` that takes a string of digits, possibly with spaces, and returns `True` if it passes:

            1. Remove the spaces.
            2. Starting from the rightmost digit, double every second digit (the 2nd, 4th, ... from the right). If doubling gives more than 9, subtract 9.
            3. Add up all the digits. The number is valid if the total is a multiple of 10.

            `"4539 3195 0343 6467"` is valid. Change any single digit and it is not.""",
            "def luhn_ok(number):\n    pass\n",
            """
            f = ns.get("luhn_ok")
            check("defines luhn_ok", lambda: callable(f))
            check("a valid number", lambda: f("4539 3195 0343 6467") is True)
            check("one digit changed", lambda: f("4539 3195 0343 6468") is False)
            check("79927398713 is valid", lambda: f("79927398713") is True)
            check("79927398710 is not", lambda: f("79927398710") is False)
            check("0 is valid", lambda: f("0") is True)
            """,
            "Reverse the digits, then use enumerate: positions 1, 3, 5... (0-based) get doubled.",
            "def luhn_ok(number):\n    digits = number.replace(\" \", \"\")[::-1]\n    total = 0\n    for i, ch in enumerate(digits):\n        d = int(ch)\n        if i % 2 == 1:\n            d *= 2\n            if d > 9:\n                d -= 9\n        total += d\n    return total % 10 == 0"),
    ],
    exam=[
        PRED("print(17 // 5, 17 % 5, -17 // 5)", "17 // 5 is 3 with remainder 2. -3.4 rounds down to -4."),
        PRED("x = [1, 2, 3]\ny = x\ny += [4]\nprint(x)", "`+=` on a list extends it in place, and `y` is the same list as `x`."),
        PRED('print("tram"[1:3] * 2)', "`[1:3]` is `ra`, repeated twice."),
        PRED('print(sorted({"b": 2, "a": 1}.items()))', "`.items()` gives pairs; sorted puts them in key order."),
        PRED("def f(n):\n    if n <= 1:\n        return 1\n    return n * f(n - 1)\n\nprint(f(5))", "Recursive factorial: 5 * 4 * 3 * 2 * 1."),
        PRED('print(bool(""), bool("0"), bool(0.0))', "Empty string and zero are falsy; `\"0\"` is a non-empty string, so truthy."),
        PRED("total = 0\nfor i in range(10):\n    if i == 6:\n        break\n    if i % 2:\n        continue\n    total += i\nprint(total)", "Odd numbers are skipped and the loop stops at 6: 0 + 2 + 4."),
        PRED('try:\n    print(int("4") + int("x"))\nexcept ValueError:\n    print("bad")', "`int(\"x\")` raises before print runs."),
        PRED('a = (1, 2, 3)\nprint(a[::-1], len(set("banana")))', "A reversed tuple; `banana` has three distinct letters."),
        PRED('print(f"{7 / 2:.2f}|{7 // 2:03d}")', "Two decimals, then an int padded with zeros to width 3."),
        PRED('d = {}\nfor w in "a b a c a".split():\n    d[w] = d.get(w, 0) + 1\nprint(max(d, key=d.get), d["a"])', "Counting pattern; `max` with `key=d.get` finds the key with the biggest count."),
        PRED("nums = [3, 1, 2]\nr = nums.sort()\nprint(r, nums)", "`sort` changes the list in place and returns None."),
    ],
    project=JOB("project", "bench", "Boss machine: the Bench Automaton",
        """
        The Bench Automaton keeps the Workshop's parts inventory, one line per delivery: `"name,category,qty"`. Some lines are damaged. Write `bench_report(lines)` that returns a list of strings:

        - one line per category, `"category: total"`, ordered by total from highest to lowest, ties in alphabetical order of category;
        - then a final line `"bad lines: N"`.

        A line is bad if it does not have exactly three comma-separated parts, if the quantity is not a whole number, or if the quantity is negative. Spaces around parts should be ignored (`" gears , 4"` is fine) and categories are not case-sensitive (store them in lower case).

        Example:
        ```
        bench_report(["bolt,metal,10", "cog, Metal ,5", "rope,fibre,7", "oops", "pin,metal,-2"])
        ```
        returns `["metal: 15", "fibre: 7", "bad lines: 2"]`.""",
        "def bench_report(lines):\n    pass\n",
        """
        f = ns.get("bench_report")
        check("defines bench_report", lambda: callable(f))
        check("the example", lambda: f(["bolt,metal,10", "cog, Metal ,5", "rope,fibre,7", "oops", "pin,metal,-2"]) == ["metal: 15", "fibre: 7", "bad lines: 2"])
        check("an empty inventory", lambda: f([]) == ["bad lines: 0"])
        check("ties in alphabetical order", lambda: f(["a,zinc,3", "b,brass,3"]) == ["brass: 3", "zinc: 3", "bad lines: 0"])
        check("non-numbers and wrong part counts are bad", lambda: f(["a,b", "a,b,c,d", "a,b,two", "a,b, 4 "]) == ["b: 4", "bad lines: 3"])
        check("zero is allowed", lambda: f(["a,b,0"]) == ["b: 0", "bad lines: 0"])
        """,
        "Parse each line inside try/except ValueError: split on commas, strip each part, unpack three names, int() the quantity, and raise ValueError yourself if it is negative. Accumulate totals in a dict, then sort the items with key (-total, category).",
        'def bench_report(lines):\n    totals = {}\n    bad = 0\n    for line in lines:\n        try:\n            name, cat, qty = [p.strip() for p in line.split(",")]\n            qty = int(qty)\n            if qty < 0:\n                raise ValueError("negative quantity")\n        except ValueError:\n            bad += 1\n            continue\n        cat = cat.lower()\n        totals[cat] = totals.get(cat, 0) + qty\n    def rank(item):\n        return (-item[1], item[0])\n    report = [f"{c}: {t}" for c, t in sorted(totals.items(), key=rank)]\n    report.append(f"bad lines: {bad}")\n    return report'),
)

AFTER = {"change": "py07", "rle": "py05", "angle": "py04", "roman": "py06", "luhn": "py06"}
for q in DISTRICT["quests"]:
    q["after"] = AFTER[q["id"]]
