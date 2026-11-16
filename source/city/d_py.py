from dsl import *

# The Workshop Quarter (Python foundations): opener, ending, Founders' Archive, side quests,
# closed-book exam (2 slots per lesson, 3 parallel items per slot), boss project and the MERIDIAN log.
# Rule for everything here: an item tied to lesson N uses only what lessons 1..N teach.

DISTRICT = district(
    "py",
    opener=[
        """
        You step off the night train into **Calx**, the Clockwork City, with a letter of apprenticeship and a bag that is mostly sandwiches. The station clock says 06:00. It has said 06:00 for eleven years.""",
        """
        Everything here runs on small programs written by the Founders: the trams, the fountains, the bells, the bread ovens. The Founders wrote no comments. The last Readers, who could make sense of their programs, have retired to the coast.""",
        """
        A brass cabinet on wheels rolls up beside you. It is full of pigeonholes, and every pigeonhole is labelled. "I am NIT," it says. "Numbered Index of Terms. You are late by four minutes and eleven seconds, which is very early by local standards."

        "Every stopped machine in this city has the same last line in its log," NIT adds, and slides out a card:

        `waiting for MERIDIAN`""",
        """
        "Your first district is the **Workshop Quarter**. Its benches, trams and stalls have all stopped. Learn to read their programs, and you can start them again. Learn enough, and we might find out what MERIDIAN is."

        Below is the station clock's whole program. `print` shows whatever is inside its brackets; you do not need to know more yet. Guess what it shows, then just press Run.

        ```
        print("Station clock")
        print("06:00")
        ```
        The program runs once, prints once and stops. Nothing in it can make the time move. A clock needs a **loop** that repeats, and an update inside it that changes the time on every pass. You will learn both in lesson 3, and the station clock will move again.""",
    ],
    ending=[
        """
        The Bench Automaton shudders, wheezes, and starts totalling its deliveries again: one line per category, the damaged lines counted instead of crashing it. Across the Quarter the trams move, Mrs Pell's till prints receipts a person can read, and Juno's signs are back in order.""",
        """
        NIT slides out the Automaton's log. Every line is fine, except the last:

        `inventory complete. waiting for MERIDIAN`

        "The Workshop works," NIT says. "But it is still waiting. Your boss-project skill can tell us how much of it is waiting." """,
        """
        Filter the log, as you filtered the Automaton's deliveries. Predict the count, then run it.

        ```
        log = [
            "06:00 bolts counted",
            "06:00 waiting for MERIDIAN",
            "06:00 gears oiled",
            "06:00 waiting for MERIDIAN",
            "06:00 inventory complete.",
            "06:00 waiting for MERIDIAN",
        ]
        end = "waiting for MERIDIAN"
        waiting = [x for x in log
                   if x.endswith(end)]
        print(len(waiting), "of", len(log), "waiting")
        times = set([x[:5] for x in log])
        print(sorted(times))
        ```
        Every waiting line, and every line at all, carries the same time: `06:00`. NIT turns its pigeonholes toward the great tower in the middle of the city, whose face is marked with Roman numerals and whose hands point at VI.

        "MERIDIAN is not a person," NIT says. "It is the great tower's clock. Every machine in Calx waits for its tick, and it stopped eleven years ago. The Workshop alone cannot start it. Twelve more districts can."

        Next: **The Conveyor Works**. Make the machine do the boring part.""",
    ],
    archive=[
        ARCHIVE("jacquard", "1801", "The loom that read cards",
                "Joseph Marie Jacquard demonstrated a loom controlled by a chain of punched cards in 1801 and perfected it in 1804-05, building on earlier punched-card and paper-tape looms by Basile Bouchon (1725), Jean-Baptiste Falcon and Jacques de Vaucanson. Each card's holes chose which threads were lifted, so the pattern was changed by changing the cards: an ordered sequence of instructions, read one after another, like the items of a list.",
                "Encyclopaedia Britannica, \"Jacquard loom\"",
                lesson="py06"),
        ARCHIVE("lovelace", "1843", "Notes on the Analytical Engine",
                "Ada Lovelace translated a French-language paper by the Italian engineer Luigi Menabrea about Charles Babbage's proposed Analytical Engine, and added her own notes, longer than the paper itself. Her Note G sets out, step by step, how the engine could compute Bernoulli numbers, and is often described as the first published computer program. She also argued that such a machine could act on symbols other than numbers, the idea behind every string you process.",
                "Encyclopaedia Britannica, \"Ada Lovelace\"; L. F. Menabrea, \"Sketch of the Analytical Engine invented by Charles Babbage\", translated with notes by A. A. L., Scientific Memoirs 3 (1843)",
                lesson="py05"),
        ARCHIVE("hollerith", "1890", "Counting a nation on cards",
                "Herman Hollerith's electric tabulating machines read punched cards to count the 1890 United States census: each card was one person, and each hole a fact about them. The machines added up how many cards had each hole, which is the counting pattern of lesson 7 done with electricity. Punched cards then carried data and programs for most of the twentieth century, and Hollerith's company became part of what was later named IBM.",
                "US Census Bureau, \"The Hollerith Machine\" (census.gov history); IBM Heritage, \"The punched card\"",
                lesson="py07"),
        ARCHIVE("fortran", "1957", "FORTRAN",
                "A team at IBM led by John Backus released FORTRAN (FORmula TRANslation), the first widely used high-level programming language. Programmers could write formulas such as `y = a * x + b` instead of machine instructions, and a compiler translated them into fast machine code. Naming a calculation once and reusing it is the same idea as writing a function.",
                "IBM Heritage, \"Fortran\"",
                lesson="py04"),
        ARCHIVE("bug", "1947", "The moth in the relay",
                "On 9 September 1947 operators of the Harvard Mark II computer found a moth trapped in a relay, taped it into the logbook and wrote \"First actual case of bug being found.\" The joke worked because engineers already called faults bugs. The logbook page survives in a museum.",
                "Smithsonian National Museum of American History, \"Log Book With Computer Bug\"",
                lesson="py08"),
        ARCHIVE("goto", "1968", "Structured programming",
                "Edsger Dijkstra's letter in Communications of the ACM argued that jumping freely around a program makes it hard to reason about. Its famous title, \"Go To Statement Considered Harmful\", was chosen by the journal's editor, Niklaus Wirth. The structured style that followed, built from sequence, if/else and loops, is the style Python is built around: Python has no goto at all.",
                "E. W. Dijkstra, \"Go To Statement Considered Harmful\", Communications of the ACM 11(3):147-148, March 1968",
                lesson="py03"),
        ARCHIVE("ieee754", "1985", "IEEE 754 floating point",
                "The IEEE 754 standard fixed the formats computers use to store floating-point numbers and required the basic operations (add, subtract, multiply, divide, square root) to be rounded correctly. Those operations therefore give the same results on any conforming machine, although compilers and maths libraries can still differ for other functions. The numbers are stored in binary, which is why 0.1 + 0.2 is not exactly 0.3 in Python and nearly every other language.",
                "IEEE 754-1985, \"IEEE Standard for Binary Floating-Point Arithmetic\" (revised as IEEE 754-2008 and 754-2019)",
                lesson="py02"),
        ARCHIVE("ascii", "1963", "ASCII, then Unicode",
                "ASCII, first published in 1963, gave letters, digits and symbols 7-bit numbers: 'A' is 65. The 1963 version had no lower-case letters; they were added in 1967, which is why `ord(\"a\")` is 97, exactly 32 after 'A'. ASCII had no room for most of the world's writing systems. Unicode, first published in 1991, now covers most of the world's scripts, and Python 3 strings are Unicode.",
                "Encyclopaedia Britannica, \"ASCII\"; The Unicode Consortium, \"History of Unicode\"",
                lesson="py05"),
        ARCHIVE("python", "1991", "Python is released",
                "Guido van Rossum began Python as a hobby project over the Christmas holidays of 1989 and published the first version in February 1991. The name comes from the BBC comedy series Monty Python's Flying Circus, not from the snake.",
                "G. van Rossum, foreword to Mark Lutz, \"Programming Python\" (O'Reilly, 1996); Python documentation, General FAQ: \"Why is it called Python?\"",
                lesson="py01"),
        ARCHIVE("py3", "2008", "Python 3 breaks with the past",
                "Python 3.0, released in December 2008, deliberately broke compatibility to fix old design mistakes: `print` became a function, text became Unicode by default, and `/` began always giving a float (in Python 2, `7 / 2` was 3). Python 2 was officially retired on 1 January 2020, so everything in Lime is Python 3.",
                "python.org, \"Sunsetting Python 2\"; PEP 238, \"Changing the Division Operator\"",
                lesson="py01"),
        ARCHIVE("zen", "1999", "The Zen of Python",
                "In 1999 Tim Peters posted 19 short aphorisms about good Python style to the Python mailing list; in 2004 they were written up as PEP 20. Among them: \"Readability counts\" and \"Errors should never pass silently.\" Run `import this` in the Bench to read them all.",
                "PEP 20, \"The Zen of Python\" (peps.python.org/pep-0020)",
                lesson="py04"),
    ],
    quests=[
        # ordered by the lesson that opens them (`after`), easiest first within a lesson
        JOB("quest", "collatz", "Side quest: the Collatz tram route",
            """
            Wren's night tram follows an odd rule. From stop number `n`: if `n` is even, the next stop is `n // 2`; if it is odd, the next stop is `3 * n + 1`. The route ends at stop 1. Starting from `start`, print two lines:

            - `steps: S`, the number of moves until the tram reaches 1;
            - `highest: H`, the largest stop number on the route, the start included.

            From 6 the route is 6, 3, 10, 5, 16, 8, 4, 2, 1, so it prints `steps: 8` and `highest: 16`. From 1 the tram is already home: `steps: 0`, `highest: 1`. Keep the `start = 6` line: the checker changes it.""",
            """
            start = 6
            # your loop here
            """,
            """
            def lines(text):
                return [l.strip() for l in text.strip().split("\\n")]
            check_eq("from 6", lambda: lines(out), ["steps: 8", "highest: 16"], "Print exactly two lines, e.g. print(\\"steps:\\", steps). Count a step each time the tram moves, and start `highest` at `start`.")
            check("uses a loop", lambda: has_node("While", "For"), "You do not know in advance how many moves there are: that is a job for `while n != 1:`.")
            check_eq("from 27 (a famously long route)", lambda: lines(rerun("start = 6", "start = 27")[1]), ["steps: 111", "highest: 9232"], "Your counting must follow the rule, not the example. Update `n` inside the loop and compare it with `highest` after every move.")
            check_eq("from 1, already home", lambda: lines(rerun("start = 6", "start = 1")[1]), ["steps: 0", "highest: 1"], "If the start is 1 the loop body must not run at all: `while n != 1:` checks before the first pass.")
            check_eq("from 7", lambda: lines(rerun("start = 6", "start = 7")[1]), ["steps: 16", "highest: 52"], "Use `n % 2 == 0` for even, and `n // 2` (not `/`) so the stops stay whole numbers.")
            """,
            "Use a separate name `n` for the current stop, starting at `start`. Loop `while n != 1:`; inside, choose the next stop with if/else, add 1 to `steps`, and keep `highest` as a running maximum.",
            """
            start = 6
            n = start
            steps = 0
            highest = start
            while n != 1:
                if n % 2 == 0:
                    n = n // 2
                else:
                    n = 3 * n + 1
                steps += 1
                if n > highest:
                    highest = n
            print("steps:", steps)
            print("highest:", highest)
            """),
        JOB("quest", "angle", "Side quest: the clock hands",
            """
            Write `hand_angle(hour, minute)` that returns the smaller angle in degrees between the hour and minute hands of an analogue clock, as a number. The hour hand moves smoothly: at 3:30 it is halfway between 3 and 4.

            - `hand_angle(3, 0)` is `90.0`
            - `hand_angle(3, 30)` is `75.0`
            - `hand_angle(12, 0)` is `0.0`

            Hours run from 1 to 12, minutes from 0 to 59.""",
            "def hand_angle(hour, minute):\n    pass\n",
            """
            f = ns.get("hand_angle")
            check("defines hand_angle", lambda: callable(f), "Start with `def hand_angle(hour, minute):`.")
            check_eq("3:00 is 90", lambda: float(f(3, 0)), 90.0, "The minute hand moves 6 degrees a minute, the hour hand 30 degrees an hour.")
            check_eq("3:30 is 75", lambda: float(f(3, 30)), 75.0, "The hour hand also moves 0.5 degrees per minute.")
            check_eq("12:00 is 0", lambda: float(f(12, 0)), 0.0, "12 o'clock is the same position as 0: use `hour % 12`.")
            check_eq("9:00 is 90, the smaller angle", lambda: float(f(9, 0)), 90.0, "Take the smaller of the angle and 360 minus it.")
            check_eq("6:00 is 180", lambda: float(f(6, 0)), 180.0)
            check_eq("3:15 is 7.5", lambda: float(f(3, 15)), 7.5, "At 3:15 the hour hand has moved a quarter of the way from 3 to 4.")
            check("returns, not prints", lambda: silent(f, 3, 0)[1] == "", "Hand the angle back with `return`; do not print it.")
            """,
            "Minute hand: 6 degrees per minute. Hour hand: 30 * (hour % 12) + 0.5 * minute. Take the difference with abs(), then min(diff, 360 - diff).",
            "def hand_angle(hour, minute):\n    m = 6.0 * minute\n    h = 30.0 * (hour % 12) + 0.5 * minute\n    diff = abs(h - m)\n    return min(diff, 360 - diff)"),
        JOB("quest", "rle", "Side quest: the loom's pattern code",
            """
            The loom stores patterns compressed: each run of the same character becomes the character followed by the length of the run. Write `encode(text)` and `decode(code)`.

            - `encode("aaabcc")` is `"a3b1c2"`
            - `decode("a3b1c2")` is `"aaabcc"`

            Rules: patterns contain only letters, and upper and lower case are different characters (`"aA"` is `"a1A1"`). Counts can have more than one digit (`"x12"`). `decode` may assume its input is well formed: a letter, then a count of at least 1, again and again (and `""` decodes to `""`).""",
            "def encode(text):\n    pass\n\ndef decode(code):\n    pass\n",
            """
            e = ns.get("encode")
            d = ns.get("decode")
            check("defines encode and decode", lambda: callable(e) and callable(d), "Define both functions.")
            check_eq('encode("aaabcc")', lambda: e("aaabcc"), "a3b1c2", "Walk the text; when the character changes, write the finished run as character + str(length).")
            check_eq('encode("")', lambda: e(""), "", "An empty pattern has no runs: return an empty string.")
            check_eq('encode("aA") keeps case apart', lambda: e("aA"), "a1A1", "Compare characters exactly with ==; do not lower() them.")
            check_eq("encode handles long runs", lambda: e("x" * 12 + "y"), "x12y1", "Do not forget the last run when the text ends.")
            check_eq('decode("a3b1c2")', lambda: d("a3b1c2"), "aaabcc", "Repeat each letter with `letter * int(count)`.")
            check_eq("decode handles two-digit counts", lambda: d("x12y1"), "x" * 12 + "y", "After a letter, collect every digit (`isdigit()`) up to the next letter.")
            check_eq('decode("")', lambda: d(""), "", "An empty code decodes to an empty pattern.")
            check_eq("decode(encode(s)) gives s back", lambda: [d(e(s)) for s in ["", "a", "abba", "zzzzzzzzzzzq", "mississippi"]], ["", "a", "abba", "zzzzzzzzzzzq", "mississippi"], "Test both directions on the same words: each mistake shows up here.")
            """,
            "encode: keep an index i; move a second index j forward while text[j] equals text[i]; the run length is j - i; then set i = j. decode: the same shape, but j moves forward while code[j] is a digit, and code[i + 1:j] is the count.",
            "def encode(text):\n    out = \"\"\n    i = 0\n    while i < len(text):\n        j = i\n        while j < len(text) and text[j] == text[i]:\n            j += 1\n        out += text[i] + str(j - i)\n        i = j\n    return out\n\ndef decode(code):\n    out = \"\"\n    i = 0\n    while i < len(code):\n        ch = code[i]\n        j = i + 1\n        while j < len(code) and code[j].isdigit():\n            j += 1\n        out += ch * int(code[i + 1:j])\n        i = j\n    return out"),
        JOB("quest", "roman", "Side quest: the tower's numerals",
            """
            The great tower's face uses Roman numerals. Write `to_roman(n)` for 1 to 3999, using the subtractive forms IV (4), IX (9), XL (40), XC (90), CD (400) and CM (900).

            `to_roman(1994)` is `"MCMXCIV"` and `to_roman(444)` is `"CDXLIV"`.""",
            "def to_roman(n):\n    pass\n",
            """
            f = ns.get("to_roman")
            check("defines to_roman", lambda: callable(f), "Start with `def to_roman(n):`.")
            check_eq("4 is IV", lambda: f(4), "IV", "Return a string. 4 is written IV, not IIII.")
            check_eq("9 is IX", lambda: f(9), "IX")
            check_eq("14 is XIV", lambda: f(14), "XIV")
            check_eq("40 is XL", lambda: f(40), "XL", "Your pairs need (40, \\"XL\\"), between 50 and 10.")
            check_eq("90 is XC", lambda: f(90), "XC")
            check_eq("400 is CD", lambda: f(400), "CD", "Your pairs need (400, \\"CD\\"), between 500 and 100.")
            check_eq("444 is CDXLIV", lambda: f(444), "CDXLIV", "Each subtractive pair must be tried in order, largest value first.")
            check_eq("1994 is MCMXCIV", lambda: f(1994), "MCMXCIV")
            check_eq("3999 is MMMCMXCIX", lambda: f(3999), "MMMCMXCIX", "Use `while n >= value` so a symbol can repeat (MMM).")
            """,
            "Keep a list of (value, symbols) pairs from 1000 down to 1, including 900 CM, 400 CD, 90 XC, 40 XL, 9 IX and 4 IV. For each pair, while it still fits into n, add its symbols and subtract its value.",
            "def to_roman(n):\n    pairs = [(1000, \"M\"), (900, \"CM\"), (500, \"D\"), (400, \"CD\"), (100, \"C\"), (90, \"XC\"), (50, \"L\"), (40, \"XL\"), (10, \"X\"), (9, \"IX\"), (5, \"V\"), (4, \"IV\"), (1, \"I\")]\n    out = \"\"\n    for value, sym in pairs:\n        while n >= value:\n            out += sym\n            n -= value\n    return out"),
        JOB("quest", "luhn", "Side quest: check the ticket number",
            """
            Tram season tickets carry a check digit using the **Luhn algorithm** (the same one used on bank card numbers). Write `luhn_ok(number)` that takes a string and returns `True` if it passes:

            1. Remove the spaces.
            2. If what is left is empty, or contains anything other than the digits 0 to 9, return `False`.
            3. Starting from the rightmost digit, double every second digit (the 2nd, 4th, ... from the right). If doubling gives more than 9, subtract 9.
            4. Add up all the digits. The number is valid if the total is a multiple of 10.

            `"4539 3195 0343 6467"` is valid. Change any single digit and it is not.""",
            "def luhn_ok(number):\n    pass\n",
            """
            f = ns.get("luhn_ok")
            check("defines luhn_ok", lambda: callable(f), "Start with `def luhn_ok(number):`.")
            check_eq("a valid number", lambda: f("4539 3195 0343 6467"), True, "Remove the spaces with replace(), then walk the digits from the right.")
            check_eq("one digit changed", lambda: f("4539 3195 0343 6468"), False, "Return the comparison `total % 10 == 0`, which is already True or False.")
            check_eq("79927398713 is valid", lambda: f("79927398713"), True, "Double the 2nd, 4th, ... digits counting from the right: reverse first, then double positions 1, 3, 5 (0-based).")
            check_eq("79927398710 is not", lambda: f("79927398710"), False)
            check_eq("0 is valid", lambda: f("0"), True)
            check_eq("an empty string is not a number", lambda: f(""), False, "Rule 2: nothing left after removing spaces means False.")
            check_eq("only spaces is not a number", lambda: f("   "), False, "Remove the spaces first, then check for an empty string.")
            check_eq("dashes are not digits", lambda: f("4539-3195-0343-6467"), False, "`isdigit()` is False if any character is not a digit.")
            check_eq("letters are not digits", lambda: f("12a4"), False, "Check the whole string before converting any character with int().")
            """,
            "digits = number.replace(\" \", \"\"); if not digits.isdigit(): return False (this also catches the empty string). Then reverse with [::-1] and use enumerate: positions 1, 3, 5... get doubled.",
            "def luhn_ok(number):\n    digits = number.replace(\" \", \"\")\n    if not digits.isdigit():\n        return False\n    total = 0\n    for i, ch in enumerate(digits[::-1]):\n        d = int(ch)\n        if i % 2 == 1:\n            d *= 2\n            if d > 9:\n                d -= 9\n        total += d\n    return total % 10 == 0"),
        JOB("quest", "change", "Side quest: the change maker",
            """
            The tram's change drawer holds coins worth 50, 20, 10, 5, 2 and 1. Write `make_change(amount)` that returns a dictionary of coin to count using as few coins as possible, leaving out coins with a count of 0.

            `make_change(78)` is `{50: 1, 20: 1, 5: 1, 2: 1, 1: 1}` and `make_change(0)` is `{}`.""",
            "def make_change(amount):\n    pass\n",
            """
            f = ns.get("make_change")
            check("defines make_change", lambda: callable(f), "Start with `def make_change(amount):`.")
            check_eq("78", lambda: f(78), {50: 1, 20: 1, 5: 1, 2: 1, 1: 1}, "Go from the largest coin down: count = amount // coin, then amount %= coin.")
            check_eq("40 is two 20s", lambda: f(40), {20: 2}, "Store only coins whose count is above 0.")
            check_eq("0 gives an empty dict", lambda: f(0), {}, "Start from `{}` and add a coin only when its count is above 0.")
            check_eq("every amount up to 200 adds up", lambda: [a for a in range(201) if sum([c * n for c, n in f(a).items()]) != a], [], "These amounts did not add up: check the remainder step.")
            check_eq("99 uses as few coins as possible", lambda: f(99), {50: 1, 20: 2, 5: 1, 2: 2}, "Largest coin first gives the fewest coins with these coin values.")
            """,
            "Go from the largest coin down: count = amount // coin, then amount %= coin. Only store counts above 0.",
            "def make_change(amount):\n    result = {}\n    for coin in [50, 20, 10, 5, 2, 1]:\n        count = amount // coin\n        if count:\n            result[coin] = count\n        amount %= coin\n    return result"),
        JOB("quest", "lamps", "Side quest: the inspector's report",
            """
            The night inspector checks the lamps at every tram stop and writes one line per stop: `"Brass Yard|4|1"` is the stop name, the number of lamps and the number of broken lamps. Write two functions.

            `read_stop(line)` returns a tuple `(name, lamps, broken)`, with the name stripped of spaces and both counts as ints. Spaces around any part are allowed. Otherwise it **raises** `ValueError` with exactly one of these messages, checked in this order:

            - `"expected 3 parts"` if the line does not split into exactly 3 parts on `|`
            - `"no stop name"` if the name is empty after stripping
            - `"counts must be whole numbers"` if either count, after stripping, is not made only of the digits 0 to 9
            - `"more broken than lamps"` if broken is larger than lamps

            `lamp_report(lines)` returns a dictionary with three keys:

            - `"working"`: the total of lamps minus broken over all good lines;
            - `"worst"`: the name of the stop with the most broken lamps (the first such stop on a tie), or `None` if no stop has a broken lamp;
            - `"problems"`: a list like `["line 2: no stop name"]`, counting lines from 1.

            Catch **only** `ValueError` in `lamp_report`. Anything else, such as a caller passing a number instead of a line of text, is a bug in the caller, and that error must pass out of `lamp_report` unchanged.""",
            "def read_stop(line):\n    pass\n\ndef lamp_report(lines):\n    pass\n",
            """
            r = ns.get("read_stop")
            rep = ns.get("lamp_report")
            check("defines read_stop and lamp_report", lambda: callable(r) and callable(rep), "Define both functions.")
            def msg(line):
                try:
                    r(line)
                except ValueError as err:
                    return str(err)
                return "no error"
            check_eq('read_stop("Brass Yard|4|1")', lambda: r("Brass Yard|4|1"), ("Brass Yard", 4, 1), "Split on \\"|\\", strip each part, convert the counts with int() and return a tuple.")
            check_eq("spaces around parts are fine", lambda: r(" Spring Lane | 6 | 0 "), ("Spring Lane", 6, 0), "Strip every part before checking it.")
            check_eq("wrong number of parts", lambda: [msg("A|1"), msg("A|1|0|2")], ["expected 3 parts", "expected 3 parts"], 'Check len(parts) != 3 first and `raise ValueError("expected 3 parts")`.')
            check_eq("an empty name", lambda: msg("  |3|1"), "no stop name", "After stripping, an empty name is an error of its own.")
            check_eq("counts that are not plain digits", lambda: [msg("A|x|1"), msg("A|3|-1"), msg("A|2.0|1"), msg("A||1")], ["counts must be whole numbers"] * 4, "Use isdigit() on both stripped counts: it is False for letters, signs, dots and empty text.")
            check_eq("more broken than lamps", lambda: msg("A|2|3"), "more broken than lamps", "Compare the two ints after converting them.")
            check_eq("the order of the checks", lambda: msg(" |x|1"), "no stop name", "Check in the order given: the name comes before the counts.")
            check_eq("a full report", lambda: rep(["Brass Yard|4|1", "|3|0", "Spring Lane|6|2", "Mill|2|5", "Depot|3|2"]), {"working": 8, "worst": "Spring Lane", "problems": ["line 2: no stop name", "line 4: more broken than lamps"]}, "Call read_stop inside try; in `except ValueError as err:` add f\\"line {i + 1}: {err}\\"; add the good stops in `else`.")
            check_eq("no broken lamps at all", lambda: rep(["A|2|0", "B|1|0"]), {"working": 3, "worst": None, "problems": []}, "Only a stop with at least one broken lamp can be the worst one.")
            check_eq("an empty night", lambda: rep([]), {"working": 0, "worst": None, "problems": []}, "Start from working = 0, worst = None, problems = [].")
            def other_error_passes():
                rep(["A|1|0"])
                try:
                    rep(["A|1|0", 5])
                except ValueError:
                    return False
                except Exception:
                    return True
                return False
            check("other errors pass out of lamp_report", other_error_passes, "Catch `except ValueError`, never a bare `except:` or `except Exception`: a number instead of a line is the caller's bug and must stay loud.")
            """,
            "In read_stop: parts = line.split(\"|\"); check the length; strip the parts; check the name, then isdigit() on both counts, then compare. Each failed check is one `raise ValueError(\"...\")`. In lamp_report: loop with enumerate, call read_stop in try, catch ValueError as err, and keep the worst stop as a running maximum of broken lamps (update only when strictly larger).",
            "def read_stop(line):\n    parts = line.split(\"|\")\n    if len(parts) != 3:\n        raise ValueError(\"expected 3 parts\")\n    name, lamps, broken = [p.strip() for p in parts]\n    if name == \"\":\n        raise ValueError(\"no stop name\")\n    if not lamps.isdigit() or not broken.isdigit():\n        raise ValueError(\"counts must be whole numbers\")\n    lamps = int(lamps)\n    broken = int(broken)\n    if broken > lamps:\n        raise ValueError(\"more broken than lamps\")\n    return (name, lamps, broken)\n\ndef lamp_report(lines):\n    working = 0\n    worst = None\n    most = 0\n    problems = []\n    for i, line in enumerate(lines):\n        try:\n            name, lamps, broken = read_stop(line)\n        except ValueError as err:\n            problems.append(f\"line {i + 1}: {err}\")\n        else:\n            working += lamps - broken\n            if broken > most:\n                most = broken\n                worst = name\n    return {\"working\": working, \"worst\": worst, \"problems\": problems}"),
    ],
    exam=[
        # ---- py01: operators and their order ----
        EXAMSLOT("py01",
            PRED("print(-2 ** 2 + 23 // 4, 23 % 4)",
                 "`**` comes before the minus sign, so `-2 ** 2` is -4; `23 // 4` is 5, and -4 + 5 is 1. 23 leaves 3 over after five 4s.",
                 id="x-ops-a"),
            PRED("print(60 // 7 * 2, 60 % 7, -1 ** 2)",
                 "`//` and `*` share a rung and go left to right: (60 // 7) * 2 is 16. 60 is 8 sevens and 4 over. `-1 ** 2` is -(1 ** 2), so -1.",
                 id="x-ops-b"),
            PRED("print(2 + 12 // 5 * 3, 12 / 4)",
                 "12 // 5 is 2, times 3 is 6, plus 2 is 8. `/` always gives a float, even for a whole answer: 3.0.",
                 id="x-ops-c")),
        # ---- py01: print's spaces and line endings ----
        EXAMSLOT("py01",
            PRED('print("a", "b", sep="")\nprint(1, 2, end="!")\nprint(3)',
                 "`sep=\"\"` puts nothing between the values. `end=\"!\"` replaces the line break, so the next print continues on the same line.",
                 id="x-print-a"),
            PRED('print("7", 7, sep="|", end=".")\nprint("ok")',
                 "Text and numbers print the same way, without quotes. The separator goes between the values and the end replaces the line break.",
                 id="x-print-b"),
            PRED('print("x", end="")\nprint("y", "z", sep=", ")',
                 "The first print ends with nothing, so `y` follows `x` directly; the commas inside print's brackets are never printed, only the `sep`.",
                 id="x-print-c")),
        # ---- py02: conversion and rounding ----
        EXAMSLOT("py02",
            PRED('print(int("7") + 3, "7" * 2, int(3.9))',
                 "`int(\"7\")` converts text to a number, while a string times an int repeats the text. `int()` cuts off the fraction; it does not round.",
                 id="x-conv-a"),
            PRED("print(round(2.5), round(3.5), int(-2.7))",
                 "`round` sends an exact half to the nearest even number. `int()` cuts toward zero, so -2.7 becomes -2.",
                 id="x-conv-b"),
            PRED('print(f"{7 / 2:.2f}|{7:03d}", float("4"))',
                 "`:.2f` keeps two decimals; `:03d` pads an int with zeros to width 3. `float(\"4\")` is 4.0.",
                 id="x-conv-c")),
        # ---- py02: names are tags ----
        EXAMSLOT("py02",
            PRED("x = 5\ny = x\nx = x + 1\nprint(x, y)",
                 "`y = x` ties a second tag to 5. `x = x + 1` makes a new value, 6, and moves only the `x` tag.",
                 id="x-tags-a"),
            PRED("a, b = 3, 9\na, b = b, a + b\nprint(a, b)",
                 "The right side is worked out first with the old values (9 and 3 + 9), then both names are moved.",
                 id="x-tags-b"),
            PRED("n = 4\nm = n\nn += 2\nm *= 3\nprint(n, m)",
                 "For numbers `n += 2` means `n = n + 2`: a new value for `n` only. `m` still started from 4.",
                 id="x-tags-c")),
        # ---- py03: conditions and truthiness ----
        EXAMSLOT("py03",
            PRED('print(bool("0"), bool([]), bool(0.0))',
                 "\"0\" is a non-empty string, so truthy. An empty list and zero are falsy.",
                 id="x-truth-a"),
            PRED("x = 3\nprint(x == 1 or 2, x > 1 and x < 5)",
                 "`x == 1 or 2` is `(x == 1) or 2`: False, so `or` gives its last value, 2. The second is a plain True.",
                 id="x-truth-b"),
            PRED('name = ""\nprint(name or "guest", not name)',
                 "An empty string is falsy, so `or` falls through to \"guest\"; `not` of a falsy value is True.",
                 id="x-truth-c")),
        # ---- py03: loops, break, continue, else ----
        EXAMSLOT("py03",
            PRED("n = 10\nsteps = 0\nwhile n > 1:\n    n //= 2\n    steps += 1\nprint(steps, n)",
                 "10, 5, 2, 1: three halvings. The condition is checked before each pass, so the loop stops once n is 1.",
                 id="x-loop-a"),
            PRED('for n in range(2, 9):\n    if n % 4 == 0:\n        break\n    if n % 2:\n        continue\n    print(n, end=" ")\nprint("done")',
                 "2 is printed; 3 is odd and skipped by continue; 4 triggers break before anything prints. Then the last line runs.",
                 id="x-loop-b"),
            PRED('for n in [3, 5, 7]:\n    if n % 2 == 0:\n        print("even", n)\n        break\nelse:\n    print("no break")\nprint(n)',
                 "No number is even, so break never runs and the loop's `else` does. The loop name keeps its last value, 7.",
                 id="x-loop-c")),
        # ---- py04: what a call gives back ----
        EXAMSLOT("py04",
            PRED("def show(x):\n    print(x * 2)\n\nr = show(3)\nprint(r)",
                 "`show` prints 6 but has no return, so the call gives back None, and printing r shows None.",
                 id="x-ret-a"),
            PRED('def sign(x):\n    if x > 0:\n        return "pos"\n\nprint(sign(5), sign(-1))',
                 "For -1 no return is reached, and a function that falls off its end returns None.",
                 id="x-ret-b"),
            PRED("def digits(n):\n    if n < 10:\n        return 1\n    return 1 + digits(n // 10)\n\nprint(digits(7), digits(2026))",
                 "Each call drops the last digit with `// 10` until one digit is left (the base case): 2026, 202, 20, 2 is four calls.",
                 id="x-ret-c")),
        # ---- py04: scope ----
        EXAMSLOT("py04",
            PRED("x = 5\n\ndef f():\n    x = 1\n    return x\n\nprint(f(), x)",
                 "Assigning `x` inside `f` makes a new local name; the global `x` is untouched.",
                 id="x-scope-a"),
            PRED("def bump(n):\n    n = n + 1\n    return n\n\nn = 1\nbump(n)\nprint(n, bump(n))",
                 "The parameter is the function's own local name, and the first returned value was thrown away, so the global `n` is still 1.",
                 id="x-scope-b"),
            PRED("total = 0\n\ndef add(n):\n    total = n\n    return total\n\nadd(4)\nprint(total, add(4))",
                 "`total = n` inside `add` creates a local `total`. The global one stays 0; only the returned value is 4.",
                 id="x-scope-c")),
        # ---- py05: indexing and slicing ----
        EXAMSLOT("py05",
            PRED('s = "workshop"\nprint(s[4:], s[:2] * 2, s[-1])',
                 "`[4:]` is from index 4 to the end; `[:2]` is \"wo\", repeated twice; -1 is the last character.",
                 id="x-slice-a"),
            PRED('s = "Calx City"\nprint(s[::-1][:4], s[5:100])',
                 "Reversed, the string starts with \"ytiC\". A slice past the end just stops at the end.",
                 id="x-slice-b"),
            PRED('s = "tram"\nprint(s[3:1:-1], len(s[5:]), s[-2:])',
                 "With step -1 the slice starts at index 3 (m) and stops before index 1: \"ma\". `s[5:]` is empty, not an error.",
                 id="x-slice-c")),
        # ---- py05: methods return new strings; split and join ----
        EXAMSLOT("py05",
            PRED('w = "lime"\nw.upper()\nprint(w, w.replace("i", "a"))',
                 "Strings are immutable: `w.upper()` made a new string and threw it away, so `w` is still \"lime\".",
                 id="x-str-a"),
            PRED('parts = "6:15:30".split(":")\nprint(parts[1], "-".join(parts))',
                 "`split` gives the list [\"6\", \"15\", \"30\"]; `join` glues it back with dashes.",
                 id="x-str-b"),
            PRED('print("a,b,,c".split(","), len("  a  b ".split()))',
                 "Splitting on a comma keeps the empty piece between two commas, and a list shows strings with quotes. `split()` with no argument ignores runs of spaces.",
                 id="x-str-c")),
        # ---- py06: aliasing, += and new lists ----
        EXAMSLOT("py06",
            PRED("a = [1, 2]\nb = a\nb = b + [3]\na.append(9)\nprint(a, b)",
                 "`b + [3]` builds a new list and moves only `b`, so `a` and `b` are now different lists; the append changes only `a`.",
                 id="x-alias-a"),
            PRED('x = ["a"]\ny = x\ny += ["b"]\nx = x + ["c"]\nprint(x, y)',
                 "On a list `y += [...]` extends the same list in place, so `x` sees \"b\". `x = x + [...]` then builds a new list for `x` alone.",
                 id="x-alias-b"),
            PRED("def add(lst):\n    lst.append(0)\n    lst = [9]\n\nnums = [1]\nadd(nums)\nprint(nums)",
                 "`append` changes the caller's list. `lst = [9]` only moves the local name, so the caller never sees the 9.",
                 id="x-alias-c")),
        # ---- py06: sorting and building lists ----
        EXAMSLOT("py06",
            PRED('words = ["pear", "fig", "apple"]\nprint(sorted(words, key=len)[0], words.sort())',
                 "`sorted` returns a new list, shortest first. `list.sort()` sorts in place and returns None.",
                 id="x-sort-a"),
            PRED('pts = [("b", 2), ("a", 2), ("c", 1)]\nprint(sorted(pts, key=lambda p: (-p[1], p[0])))',
                 "The tuple key sorts by the number, biggest first (because of the minus), and only breaks ties by the letter.",
                 id="x-sort-b"),
            PRED("print([n * 2 for n in range(6) if n % 3 == 0], sorted([3, 1, 2], reverse=True))",
                 "The comprehension keeps 0 and 3, then doubles them. `reverse=True` sorts from largest to smallest.",
                 id="x-sort-c")),
        # ---- py07: dictionaries ----
        EXAMSLOT("py07",
            PRED('d = {len(w): w for w in ["fig", "lime", "yam", "kiwi"]}\nprint(d)',
                 "Two words share each length; a repeated key keeps its first position but the later value replaces the earlier one.",
                 id="x-dict-a"),
            PRED('counts = {}\nfor ch in "abca":\n    counts[ch] = counts.get(ch, 0) + 1\nprint(counts["a"], counts.get("z", 0), len(counts))',
                 "The counting pattern: \"a\" appears twice. `get` with a default never raises, and there are three distinct keys.",
                 id="x-dict-b"),
            PRED('d = {"x": 1}\nd["y"] = 2\nd["x"] = 3\nprint(list(d), "x" in d, 1 in d)',
                 "Assigning to an existing key replaces its value without moving it. `in` tests keys, never values.",
                 id="x-dict-c")),
        # ---- py07: sets ----
        EXAMSLOT("py07",
            PRED("print(sorted({1, 2, 3} ^ {2, 3, 4}), {1, 2} <= {1, 2, 3})",
                 "`^` keeps items in exactly one of the sets; `<=` asks whether every item of the left set is in the right one.",
                 id="x-set-a"),
            PRED('a = {"x", "y"}\nb = {"y", "z"}\nprint(sorted(a - b), sorted(b - a), len(a | b))',
                 "`a - b` and `b - a` are different questions; the union holds three distinct items.",
                 id="x-set-b"),
            PRED('print(len(set("letter")), type({}))',
                 "A set keeps one copy of each letter: l, e, t, r. Empty braces make an empty dictionary, not a set.",
                 id="x-set-c")),
        # ---- py08: try, except, else, finally ----
        EXAMSLOT("py08",
            PRED('for t in ["3", "y"]:\n    try:\n        n = int(t)\n    except ValueError:\n        print("bad", t)\n    else:\n        print("ok", n)\n    finally:\n        print("next")',
                 "`else` runs only when nothing was raised; `finally` runs every time, error or not.",
                 id="x-try-a"),
            PRED('def f():\n    try:\n        return "a"\n    finally:\n        print("b")\n\nprint(f())',
                 "`finally` runs even on the way out through a `return`, so \"b\" is printed before the caller prints the returned \"a\".",
                 id="x-try-b"),
            PRED('try:\n    x = 1 / 0\n    print("after")\nexcept ZeroDivisionError:\n    print("caught")\nelse:\n    print("else")\nprint("end")',
                 "The rest of the `try` block is skipped once it raises, and `else` does not run because there was an error.",
                 id="x-try-c")),
        # ---- py08: raise, and errors travelling up through callers ----
        EXAMSLOT("py08",
            PRED('def half(n):\n    if n % 2:\n        raise ValueError("odd")\n    return n // 2\n\ntry:\n    print(half(8))\n    print(half(3))\n    print(half(4))\nexcept ValueError as e:\n    print("stopped:", e)',
                 "`raise` stops `half` at once, and the error jumps straight to the `except`: `half(4)` never runs. Printing the error shows its message.",
                 id="x-raise-a"),
            PRED('def g(t):\n    try:\n        return int(t)\n    finally:\n        print(t, "done")\n\ntry:\n    g("b")\nexcept ValueError:\n    print(-1)',
                 "`g` has no `except`, so the ValueError passes out of it, but its `finally` still runs first. The caller catches it.",
                 id="x-raise-b"),
            PRED('def total(items):\n    s = 0\n    for x in items:\n        s += int(x)\n        print("added", x)\n    return s\n\ntry:\n    print(total(["1", "x", "3"]))\nexcept ValueError:\n    print("no total")',
                 "The error at \"x\" leaves the loop and the function at once: nothing after it runs, not even the print for \"3\".",
                 id="x-raise-c")),
    ],
    project=JOB("project", "bench", "Boss machine: the Bench Automaton",
        """
        The Bench Automaton keeps the Workshop's parts inventory, one line per delivery: `"name,category,qty"`. Some lines are damaged. Write `bench_report(lines)` that returns a list of strings:

        - one line per category, `"category: total"`, ordered by total from highest to lowest, ties in alphabetical order of category;
        - then a final line `"bad lines: N"`.

        Spaces around parts are ignored (`" gears , 4"` is fine), and categories are not case-sensitive: `Metal` and `metal` on different lines are the same category, reported in lower case. A line is **bad** if:

        - it does not have exactly three comma-separated parts (this includes empty and whitespace-only lines);
        - its name or its category is empty after stripping;
        - its quantity, after stripping, is not made only of the digits 0 to 9. So `"0"` and `"12"` are fine, but `"-2"`, `"+4"`, `"4.0"`, `"1_000"` and `""` are bad. `int()` would accept `"+4"` and `"1_000"`, but the Automaton's delivery notes are written by hand, and a strict rule means a smudge is reported instead of quietly turned into a number.

        Use `try`/`except ValueError` to handle bad lines (raise a `ValueError` yourself for the rules `int()` does not check), never a bare `except:`. Do not change the list you are given.

        Example:
        ```
        bench_report(["bolt,metal,10", "cog, Metal ,5", "rope,fibre,7", "oops", "pin,metal,-2"])
        ```
        returns `["metal: 15", "fibre: 7", "bad lines: 2"]`.""",
        "def bench_report(lines):\n    pass\n",
        """
        f = ns.get("bench_report")
        check("defines bench_report", lambda: callable(f), "Start with `def bench_report(lines):`.")
        check_eq("the example", lambda: f(["bolt,metal,10", "cog, Metal ,5", "rope,fibre,7", "oops", "pin,metal,-2"]), ["metal: 15", "fibre: 7", "bad lines: 2"], "Split each line on commas, strip the parts, and add good quantities to a dict of totals.")
        check_eq("an empty inventory", lambda: f([]), ["bad lines: 0"], "Even with no lines the report ends with the bad-lines line.")
        check_eq("ties in alphabetical order", lambda: f(["a,zinc,3", "b,brass,3"]), ["brass: 3", "zinc: 3", "bad lines: 0"], "Sort with a tuple key: (-total, category) puts big totals first and breaks ties alphabetically.")
        check_eq("wrong part counts and non-numbers are bad", lambda: f(["a,b", "a,b,c,d", "a,b,two", "a,b, 4 "]), ["b: 4", "bad lines: 3"], "Unpacking the wrong number of parts raises ValueError, and so does int(\\"two\\").")
        check_eq("zero is allowed", lambda: f(["a,b,0"]), ["b: 0", "bad lines: 0"], "0 is a whole number of parts: keep the category with total 0.")
        check_eq("an empty category or name is bad", lambda: f(["a,,3", ",metal,3", "a, ,3", "nut,metal,1"]), ["metal: 1", "bad lines: 3"], 'After stripping, `if name == "" or cat == "":` raise ValueError.')
        check_eq("only plain digits count as a quantity", lambda: f(["a,b,+4", "a,b,1_000", "a,b,4.0", "a,b,-2", "a,b,", "a,b,7"]), ["b: 7", "bad lines: 5"], "int() accepts \\"+4\\" and \\"1_000\\": check `qty.isdigit()` first and raise ValueError if it is False.")
        check_eq("empty and whitespace-only lines are bad", lambda: f(["", "   ", "a,b,1"]), ["b: 1", "bad lines: 2"], "A blank line splits into one part, so unpacking it into three names fails.")
        check_eq("case merges across lines", lambda: f(["a,Metal,1", "b,METAL,2", "c,metal,3", "d,Wood,1"]), ["metal: 6", "wood: 1", "bad lines: 0"], "Lower-case the category before you use it as a key.")
        def unchanged():
            lines = ["a,Metal,1", " b , wood , 2 ", "bad"]
            copy = lines[:]
            f(lines)
            return eq(lines, copy)
        check("does not change the input list", unchanged, "Build new values (a dict, a report list); never assign into or sort `lines` itself.")
        check("handles bad lines with try/except", lambda: has_node("Try"), "Put the parsing of one line inside `try:` and count it in `except ValueError:`.")
        compact = code_bare.replace(" ", "").replace("\\t", "")
        check("catches ValueError by name, no bare except", lambda: "except:" not in compact and ("exceptValueError" in compact or "except(ValueError" in compact), "Write `except ValueError:`. A bare `except:` would also hide typos (NameError) and real bugs.")
        """,
        "Inside try: split on commas and strip each part, unpack three names, raise ValueError if the name or category is empty or the quantity is not isdigit(), then int() it. In except ValueError: add 1 to bad and continue. Accumulate totals in a dict under cat.lower(), then sort the items with key=lambda item: (-item[1], item[0]).",
        'def bench_report(lines):\n    totals = {}\n    bad = 0\n    for line in lines:\n        try:\n            name, cat, qty = [p.strip() for p in line.split(",")]\n            if name == "" or cat == "":\n                raise ValueError("empty name or category")\n            if not qty.isdigit():\n                raise ValueError("quantity must be plain digits")\n            qty = int(qty)\n        except ValueError:\n            bad += 1\n            continue\n        cat = cat.lower()\n        totals[cat] = totals.get(cat, 0) + qty\n    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))\n    report = [f"{c}: {t}" for c, t in ranked]\n    report.append(f"bad lines: {bad}")\n    return report'),
    meridian=[
        MERIDIAN("py01", "m-years", "MERIDIAN log, page 1: how long?",
                 """
                 # the first legible line of the log: days since the last tick
                 print(4015 // 365, "years and", 4015 % 365, "days")
                 """,
                 "4015 days is exactly 11 times 365, with nothing left over: eleven years, the same eleven years the station clock has shown 06:00. (The log ignores leap days. So, apparently, did MERIDIAN.)"),
        MERIDIAN("py02", "m-hour", "MERIDIAN log, page 2: the hour",
                 """
                 hour = "6"
                 minute = 0
                 print(hour + ":" + str(minute) + str(minute))
                 print(int(hour) * 60 + minute, "minutes after midnight")
                 """,
                 "The log stores the hour as text, so `+` joins it into \"6:00\"; converted with `int()` it becomes a number you can calculate with: 360 minutes after midnight. Every machine stopped at the same moment: 06:00."),
        MERIDIAN("py03", "m-range", "MERIDIAN log, page 3: the loop that ended",
                 """
                 for h in range(6, 7):
                     print(f"{h:02d}:00 waiting for MERIDIAN")
                 print("loop finished at", h)
                 """,
                 "`range(6, 7)` contains only 6, because the stop is never included. The log's loop ran exactly one hour and finished, which is why everything that copied it is still at 06:00."),
        MERIDIAN("py04", "m-tick", "MERIDIAN log, page 4: the tick that went nowhere",
                 """
                 def next_tick(hour):
                     hour = hour + 1

                 hour = 6
                 next_tick(hour)
                 print(hour, next_tick(hour))
                 """,
                 "`next_tick` changes only its own local `hour` and has no `return`, so the global `hour` stays 6 and the call gives back None. Whatever MERIDIAN is, the machines asked it for the next hour and got nothing back."),
        MERIDIAN("py05", "m-mirror", "MERIDIAN log, page 5: written backwards",
                 """
                 signal = "NAIDIREM rof gnitiaw"
                 print(signal[::-1])
                 print(signal[:8][::-1].title())
                 """,
                 "A step of -1 reads the string from right to left: the log's mirror-writing is the same last line every machine prints. `signal[:8]` is the first eight characters, reversed into the name."),
        MERIDIAN("py06", "m-pages", "MERIDIAN log, page 6: torn pages",
                 """
                 pages = [(2, "keeps the time"), (4, "in Calx."), (1, "MERIDIAN"), (3, "for every machine")]
                 words = [text for n, text in sorted(pages)]
                 print(" ".join(words))
                 """,
                 "Tuples sort by their first item, so the page numbers put the scraps in order, and the comprehension keeps only the text. Now you know what MERIDIAN does, though not yet what it is."),
        MERIDIAN("py07", "m-numerals", "MERIDIAN log, page 7: a face of letters",
                 """
                 face = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
                 mark = "VI"
                 print(sum([face[ch] for ch in mark]), "o'clock")
                 print(sorted(face, key=face.get)[-1])
                 """,
                 "A dictionary turns each numeral into its value: V + I is 6. Sorting the keys by their values puts M, the largest, last. Somewhere in Calx is a clock face marked in Roman numerals, stopped at VI."),
        MERIDIAN("py08", "m-choke", "MERIDIAN log, page 8: why the log choked",
                 """
                 last_line = "tick=O6"
                 try:
                     hour = int(last_line.partition("=")[2])
                     print("next hour:", hour + 1)
                 except ValueError as err:
                     print("choked:", err)
                     print("waiting for MERIDIAN")
                 """,
                 "The last tick was written with a capital letter O instead of a zero, so `int(\"O6\")` raised a ValueError. The machines caught the error and did the only thing their programs allowed: they waited."),
    ],
)

# The lesson that opens each quest (at 60%). Quests above are listed in this order.
AFTER = {"collatz": "py03", "angle": "py04", "rle": "py05", "roman": "py06", "luhn": "py06", "change": "py07", "lamps": "py08"}
for q in DISTRICT["quests"]:
    q["after"] = AFTER[q["id"]]
