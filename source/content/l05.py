from dsl import *

LESSON = lesson(
    id="py05", track="py", n=5, title="Strings in depth", minutes=60,
    summary="Indexing, slicing, immutability, methods, split and join, escapes, and how characters are numbers.",
    goals=[
        "Index and slice strings, including negative and stepped slices",
        "Explain why strings are immutable and what that means for methods",
        "Use split and join to process text",
        "Convert between characters and numbers with ord and chr",
    ],
    blocks=[
        H("Strings are sequences of characters"),
        P("""
        A `str` is an ordered sequence of Unicode characters. `len(s)` counts them, a `for` loop visits them one at a time, and `in` tests for a substring."""),
        CODE("""
        word = "Python"
        print(len(word))
        print("th" in word)
        print("z" in word)
        for ch in word:
            print(ch, end="-")
        print()
        """),

        H("Indexing and slicing"),
        P("""
        Each character has a position called an **index**, starting at 0. Negative indexes count from the end, so `-1` is the last character. A slice `s[start:stop]` takes the characters from `start` up to but **not including** `stop`. Leave out either end to go to the edge, and add a third number for the step."""),
        CODE("""
        s = "Python"
        print(s[0], s[1], s[-1], s[-2])
        print(s[0:2])
        print(s[2:])
        print(s[:4])
        print(s[::2])
        print(s[::-1])
        """),
        NOTE("model", """
        Picture the indexes as cuts *between* the characters: `|P|y|t|h|o|n|` has cuts numbered 0 to 6. A slice `s[a:b]` takes whatever lies between cut `a` and cut `b`. That is why `s[:k] + s[k:]` always rebuilds the whole string and `len(s[a:b])` is `b - a`."""),
        NOTE("trap", """
        Indexing past the end raises `IndexError` (`s[6]` on a 6-character string), but slicing never raises: `s[2:100]` quietly stops at the end. Indexes are strict; slices are forgiving."""),
        CODE("""
        s = "Python"
        print(s[2:100])
        print(repr(s[10:]))
        """),

        H("Strings cannot be changed"),
        P("""
        Strings are **immutable**: you cannot change a character in place. Every apparent modification builds a new string."""),
        CODE("""
        word = "cat"
        word = "b" + word[1:]
        print(word)
        """),
        P("""
        Because of this, string methods return new strings instead of altering the original. Calling `s.upper()` on a line by itself does nothing useful."""),
        CODE("""
        name = "ada"
        name.upper()
        print(name)
        name = name.upper()
        print(name)
        """),

        H("Useful methods"),
        CODE("""
        text = "  Hello, World  "
        print(text.strip())
        print(text.lower())
        print(text.upper())
        print(text.replace("World", "Lime"))
        print("a,b,c".split(","))
        print("-".join(["2026", "11", "07"]))
        print("hello world".title())
        print("racecar".startswith("race"), "racecar".endswith("car"))
        print("banana".count("an"), "banana".find("n"), "banana".find("z"))
        """),
        P("""
        `split` turns a string into a list of pieces, and `join` glues a list of strings together with a separator. This pair is the backbone of text processing. `find` returns -1 when nothing is found, while `index` raises `ValueError`."""),
        CODE("""
        sentence = "the quick brown fox"
        words = sentence.split()
        print(words)
        print(len(words))
        print(" ".join(words[::-1]))
        """),
        NOTE("tip", """
        `split()` with no argument splits on any run of whitespace and ignores leading and trailing spaces, so `"  a   b ".split()` is `["a", "b"]`. `split(" ")` would keep the empty pieces."""),

        H("Checking what a string contains"),
        CODE("""
        print("abc".isalpha(), "abc123".isalpha(), "abc123".isalnum())
        print("123".isdigit(), "12.5".isdigit(), "  ".isspace())
        print("Hello".islower(), "hello".islower())
        """),

        H("Escapes, quotes and raw strings"),
        P(r"""
        A backslash starts an escape: `\n` is a new line, `\t` a tab, `\\` a backslash and `\"` a quote. Triple quotes span several lines. A **raw string**, `r"..."`, keeps backslashes literally, which helps with Windows paths and regular expressions."""),
        CODE(r"""
        print("line one\nline two")
        print("tab\tseparated")
        print("She said \"hi\"")
        print(r"C:\new\table")
        print('''multi
        line''')
        """),

        H("Characters are numbers"),
        P("""
        Every character has a numeric code. `ord(ch)` gives the code and `chr(n)` turns a code back into a character. Letters are consecutive, so `ord("b") - ord("a")` is 1. That is the key to shifting letters, as in a Caesar cipher."""),
        CODE("""
        print(ord("A"), ord("a"), ord("0"))
        print(chr(72), chr(105))
        print(chr(ord("a") + 3))
        print((ord("y") - ord("a") + 3) % 26)
        """),
        P("""
        The `%` operator wraps values around: shifting `y` by 3 should land on `b`, not on a symbol after `z`."""),
        NOTE("tip", """
        Python strings are Unicode, so `ord("é")` and `ord("日")` work too. Behind the scenes, text is stored as bytes using an *encoding*, usually UTF-8. Characters and bytes are different things, and you will meet that boundary again when reading files."""),
    ],
    exercises=[
        EX("palindrome", "is_palindrome",
           "Write `is_palindrome(s)` that returns `True` when the text reads the same forwards and backwards, ignoring upper or lower case and spaces.",
           "def is_palindrome(s):\n    pass\n",
           """
           f = ns.get("is_palindrome")
           check("defines is_palindrome", lambda: callable(f))
           check('"racecar" is True', lambda: f("racecar") is True)
           check('"Never odd or even" is True', lambda: f("Never odd or even") is True, "Remove spaces and compare in lower case.")
           check('"hello" is False', lambda: f("hello") is False)
           check('"" is True', lambda: f("") is True)
           check('"Was it a car or a cat I saw" is True', lambda: f("Was it a car or a cat I saw") is True)
           """,
           "Clean the text with replace and lower, then compare it to its reverse `t[::-1]`.",
           'def is_palindrome(s):\n    t = s.replace(" ", "").lower()\n    return t == t[::-1]'),
        EX("initials", "initials",
           'Write `initials(name)` that returns the capitalised initials with a full stop after each, so `"Ada Lovelace"` gives `"A.L."`.',
           "def initials(name):\n    pass\n",
           """
           f = ns.get("initials")
           check("defines initials", lambda: callable(f))
           check('"Ada Lovelace" gives "A.L."', lambda: f("Ada Lovelace") == "A.L.")
           check("lower case input", lambda: f("grace brewster murray hopper") == "G.B.M.H.")
           check("one name", lambda: f("plato") == "P.")
           check("extra spaces", lambda: f("  alan   turing ") == "A.T.", "split() with no argument handles extra spaces.")
           """,
           "Loop over name.split(). Add word[0].upper() + \".\" to a result string each time.",
           'def initials(name):\n    result = ""\n    for word in name.split():\n        result += word[0].upper() + "."\n    return result'),
        EX("vowels", "count_vowels",
           "Write `count_vowels(s)` that counts the vowels `a e i o u` in a string, ignoring case.",
           "def count_vowels(s):\n    pass\n",
           """
           f = ns.get("count_vowels")
           check("defines count_vowels", lambda: callable(f))
           check('"Lime" has 2', lambda: f("Lime") == 2)
           check('"rhythm" has 0', lambda: f("rhythm") == 0)
           check('"AEIOU" has 5', lambda: f("AEIOU") == 5, "Convert to lower case first.")
           check('"" has 0', lambda: f("") == 0)
           """,
           "Loop over s.lower() and count the characters that are in \"aeiou\".",
           'def count_vowels(s):\n    count = 0\n    for ch in s.lower():\n        if ch in "aeiou":\n            count += 1\n    return count'),
        EX("last_three", "Fix the slice",
           "`last_three(s)` should return the last three characters of a string, but it returns only two. Fix it. For strings shorter than three characters it should return the whole string.",
           "def last_three(s):\n    return s[len(s) - 2:]\n",
           """
           f = ns.get("last_three")
           check("defines last_three", lambda: callable(f))
           check('"abcdef" gives "def"', lambda: f("abcdef") == "def")
           check('"xy" gives "xy"', lambda: f("xy") == "xy")
           check('"" gives ""', lambda: f("") == "")
           check('"abc" gives "abc"', lambda: f("abc") == "abc")
           """,
           "Negative slices count from the end: `s[-3:]`.",
           "def last_three(s):\n    return s[-3:]", kind="fix"),
        EX("reverse_words", "reverse_words",
           'Write `reverse_words(sentence)` that reverses the order of the words, so `"the quick brown fox"` gives `"fox brown quick the"`. Extra spaces should be ignored.',
           "def reverse_words(sentence):\n    pass\n",
           """
           f = ns.get("reverse_words")
           check("defines reverse_words", lambda: callable(f))
           check("basic sentence", lambda: f("the quick brown fox") == "fox brown quick the")
           check("single word", lambda: f("lime") == "lime")
           check("extra spaces", lambda: f("  a   b ") == "b a")
           """,
           "split() gives a list of words, a slice [::-1] reverses a list, and \" \".join glues it back.",
           'def reverse_words(sentence):\n    return " ".join(sentence.split()[::-1])'),
        EX("caesar", "Caesar cipher",
           """
           Write `caesar(text, shift)` that moves every letter `shift` places along the alphabet, wrapping around from `z` to `a`. Keep upper and lower case, and leave anything that is not a letter unchanged. A negative shift must undo a positive one.""",
           "def caesar(text, shift):\n    pass\n",
           """
           f = ns.get("caesar")
           check("defines caesar", lambda: callable(f))
           check('caesar("abc", 1) is "bcd"', lambda: f("abc", 1) == "bcd")
           check("wraps around", lambda: f("xyz", 3) == "abc")
           check("keeps case and punctuation", lambda: f("Hello, World!", 5) == "Mjqqt, Btwqi!")
           check("negative shift decodes", lambda: f("Mjqqt, Btwqi!", -5) == "Hello, World!")
           check("shift of 26 changes nothing", lambda: f("Lime", 26) == "Lime")
           """,
           "For each letter: find its position with ord(ch) - ord(\"a\"), add shift, use % 26, then convert back with chr. Handle upper case with ord(\"A\") as the base.",
           'def caesar(text, shift):\n    result = ""\n    for ch in text:\n        if ch.islower():\n            result += chr((ord(ch) - ord("a") + shift) % 26 + ord("a"))\n        elif ch.isupper():\n            result += chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))\n        else:\n            result += ch\n    return result'),
    ],
    predict=[
        PRED('print("python"[1:4], "python"[::-1], "python"[-2:])',
             "`[1:4]` takes positions 1, 2, 3. `[::-1]` walks backwards through the whole string. `[-2:]` takes the last two characters."),
        PRED('s = "hello"\ns.upper()\nprint(s)',
             "Strings are immutable. `upper()` returned a new string that was thrown away, so `s` is unchanged."),
        PRED('print("a-b-c".split("-"), "-".join(["x", "y"]))',
             "`split` makes a list of pieces. `join` glues strings with the separator between them."),
        PRED('print("banana".find("n"), "banana".find("z"), "banana".count("a"))',
             "The first n is at index 2. `find` returns -1 when nothing matches. There are three a's."),
        PRED('print("abc"[1:100], len("abc"[5:]))',
             "A slice stops quietly at the end, giving bc. A slice starting past the end is empty, with length 0."),
        PRED('print(chr(ord("a") + 2), ord("c") - ord("a"))',
             "Letter codes are consecutive. a + 2 is c, and c minus a is 2."),
    ],
    cards=[
        CARD("What index does the first character of a string have?", "0. The last character is at `-1`."),
        CARD("Does the slice `s[2:5]` include index 5?", "No. The stop is excluded, so it has `5 - 2` = 3 characters."),
        CARD("How do you reverse a string?", "`s[::-1]`. A step of -1 walks backwards."),
        CARD("Index out of range versus slice out of range?", "An index past the end raises `IndexError`. A slice just stops at the end and never raises."),
        CARD("What does 'strings are immutable' mean?", "You cannot change a string in place. Methods like `upper()` return a new string."),
        CARD("What do `split` and `join` do?", "`split` breaks a string into a list of pieces. `sep.join(list)` glues a list of strings together with `sep` between."),
        CARD("`find` versus `index`?", "Both locate a substring. `find` returns -1 if missing. `index` raises `ValueError`."),
        CARD("What is a raw string and when do you use it?", "`r\"...\"` keeps backslashes literally. Useful for Windows paths and regular expressions."),
        CARD("What do `ord` and `chr` do?", "`ord(ch)` gives the numeric code of a character. `chr(n)` gives the character for a code."),
        CARD("How do you shift a letter in a Caesar cipher and wrap around?", "`chr((ord(ch) - ord(\"a\") + shift) % 26 + ord(\"a\"))`."),
    ],
)
