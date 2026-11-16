from dsl import *
import textwrap


def DEEP(x):
    """A "Going deeper" note (NOTE kind "deep"). Falls back to the same dict shape if dsl.py does not know the kind yet."""
    try:
        return NOTE("deep", x)
    except AssertionError:
        return {"t": "note", "k": "deep", "x": textwrap.dedent(x).strip("\n")}


LESSON = lesson(
    id="py05", track="py", n=5, title="Strings in depth", minutes=70,
    summary="Indexing, slicing (including backwards), immutability, methods, split, partition and join, str versus repr, comparing strings, aligned f-strings, and how characters are numbers.",
    goals=[
        "Index and slice strings, including negative and stepped slices",
        "Explain why strings are immutable and what that means for methods",
        "Use split, partition and join to process text",
        "Read the difference between str() and repr(), and why lists show quotes",
        "Compare strings and shift letters using their character codes",
    ],
    blocks=[
        H("Strings are sequences of characters"),
        P("""
        A `str` is an ordered sequence of Unicode characters. `len(s)` counts them, a `for` loop visits them one at a time, and `in` tests for a substring."""),
        CODE("""
        word = "Python"
        print(len(word))
        print("th" in word)
        print("z" in word, "P" in word, "p" in word)
        for ch in word:
            print(ch, end="-")
        print()
        """),
        DEEP("""
        `in` is case-sensitive (`"p" in "Python"` is False). And `"" in s` is True for every string, even `""` itself: the empty string fits between any two characters. So a check like `if part in text:` passes when `part` is accidentally empty."""),

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
        Picture the indexes as cuts *between* the characters: `|P|y|t|h|o|n|` has cuts numbered 0 to 6. A slice `s[a:b]` takes whatever lies between cut `a` and cut `b`. That is why `s[:k] + s[k:]` always rebuilds the whole string. When `0 <= a <= b <= len(s)`, `len(s[a:b])` is `b - a`. Otherwise Python first cuts `a` and `b` down to fit the string, and a slice whose start lies after its stop is simply empty."""),
        NOTE("trap", """
        Indexing past the end raises `IndexError` (`s[6]` on a 6-character string), but slicing never raises `IndexError`: `s[2:100]` quietly stops at the end, and `s[10:]` is the empty string. Indexes are strict; slices are forgiving. (The one slice that is an error: a step of 0, as in `s[::0]`, raises `ValueError`.)"""),
        CODE("""
        s = "Python"
        print(s[2:100])
        print(len(s[10:]), len(s[4:2]), len(s[-100:2]))
        """),
        P("""
        **Stepping backwards.** With a negative step the slice walks from right to left: it starts **at** index `start` (included) and stops just **before** index `stop`. Leave both out and you get the whole string reversed. If `start` is already left of `stop`, there is nothing to walk and the slice is empty."""),
        CODE("""
        s = "Python"
        print(s[4:1:-1])
        print(s[-1:-4:-1])
        print(s[::-2])
        print(len(s[1:4:-1]))
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
        NOTE("trap", """
        `strip`, `lstrip` and `rstrip` remove characters from the ends. Given an argument, they treat it as a **set of characters**, not a word: `"xxhixyx".strip("xy")` is `"hi"`. To remove one exact piece of text from the start or the end, use `removeprefix` or `removesuffix`."""),
        CODE("""
        print("xxhixyx".strip("xy"))
        print("www.calx.org".removeprefix("www."))
        print("scan_04.png".removesuffix(".png"))
        print("scan_04.png".removesuffix(".jpg"))
        """),
        DEEP("""
        Two quiet surprises. `count` counts **non-overlapping** matches from left to right, so `"aaaa".count("aa")` is 2, not 3. And `title()` capitalises every letter that follows a non-letter, so `"they're".title()` is `"They'Re"` and `"o'neil"` becomes `"O'Neil"`. For real titles you write your own rule (one of the exercises below)."""),

        H("Splitting and joining"),
        CODE("""
        sentence = "the quick brown fox"
        words = sentence.split()
        print(words)
        print(len(words))
        print(" ".join(words[::-1]))
        """),
        NOTE("tip", """
        `split()` with no argument splits on any run of whitespace and ignores leading and trailing spaces, so `"  a   b ".split()` is `["a", "b"]`. `split(" ")` would keep the empty pieces."""),
        P("""
        **Splitting only once.** `split(sep, n)` splits at most `n` times and leaves the rest in one piece. `partition(sep)` splits at the **first** `sep` only and always gives three parts: before, the separator, after. It returns them as a tuple (the fixed group of values from lesson 4), so you can unpack it into three names. If `sep` is missing, the last two parts are empty strings. When you do not need one of the values, the name `_` is the usual way to say "I don't need this one". It is an ordinary name; the underscore is a convention for human readers."""),
        CODE("""
        line = "note=BP=120/80"
        print(line.split("="))
        print(line.split("=", 1))
        key, _, value = line.partition("=")
        print(key, value)
        print("no sign here".partition("="))
        """),
        DEEP("""
        Building a long string with `result += piece` in a loop works, but because strings are immutable each `+=` makes a brand-new string and copies everything collected so far. For a few pieces that does not matter (and CPython often optimises it). For many thousands of pieces the copying grows roughly with the square of the count. The fast habit is to collect the pieces in a list and call `"".join(pieces)` once at the end; lesson 6 shows how to grow a list and why some list operations are cheap and others are not."""),

        H("Checking what a string contains"),
        CODE("""
        print("abc".isalpha(), "abc123".isalpha(), "abc123".isalnum())
        print("123".isdigit(), "12.5".isdigit(), "-5".isdigit(), "".isdigit())
        print("  ".isspace(), "Hello".islower(), "hello".islower())
        """),
        P("""
        `isdigit()` asks "is every character a digit?", so it is not a test for "is this a number": `"-5"` and `"12.5"` give False although `int("-5")` and `float("12.5")` both work. An empty string gives False for every `is...` method."""),
        DEEP("""
        These methods understand all of Unicode: `"é".isalpha()` and `"é".islower()` are both True. That matters whenever your code quietly assumes "letter" means a to z, as the Caesar exercise below shows."""),

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

        H("str() and repr(): two ways to show a value"),
        P(r"""
        Every value has two text forms. `str(x)` is the friendly form, and it is what `print` shows. `repr(x)` is the precise form a programmer needs: for a string it adds quotes and spells out escapes such as `\n`, so you can see exactly what is there, spaces included. When Python shows a **list**, it shows each item with `repr`. That is why strings inside a printed list have quotes and numbers do not. Python picks single quotes unless the text itself contains a single quote."""),
        CODE(r"""
        s = " spaced \n"
        print("[" + s + "]")
        print(repr(s))
        print(repr("it's"), repr(42))
        print(["a", "b c", 5, "5"])
        """),
        NOTE("tip", """
        When a value prints strangely, print its `repr`: stray spaces, a hidden new line or a number stored as text show up at once. Inside an f-string, `{x!r}` gives the repr."""),

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
        The `%` operator wraps values around: shifting `y` by 3 should land on `b`, not on a symbol after `z`. Position 24 plus 3 is 27, and `27 % 26` is 1, the position of `b`."""),
        NOTE("tip", """
        Python strings are Unicode, so `ord("é")` and `ord("日")` work too. Behind the scenes, text is stored as bytes using an *encoding*, usually UTF-8. Characters and bytes are different things, and you will meet that boundary again when reading files."""),

        H("Comparing strings"),
        P("""
        `<`, `>` and `==` compare strings **character by character from the left, by character code**. The first difference decides. If one string runs out first, the shorter one is smaller. Every capital letter (codes 65 to 90) comes before every lower-case letter (97 to 122), so `"Zebra" < "apple"`. Digits are compared as characters too, so `"10" < "9"`, because `"1"` comes before `"9"`. That is why sorting words needs care (lesson 6) and why numbers stored as text sort strangely. A chained comparison such as `"a" <= ch <= "z"` is the plain way to ask "is `ch` one of the letters a to z?"."""),
        CODE("""
        print("apple" < "banana", "apple" < "apricot")
        print("Zebra" < "apple", ord("Z"), ord("a"))
        print("10" < "9", 10 < 9)
        print("app" < "apple")
        ch = "q"
        print("a" <= ch <= "z", "a" <= "Q" <= "z")
        """),

        H("Lining up columns with f-strings"),
        P("""
        Lesson 2 showed `:>10`. After the colon you can combine an alignment, a width and a precision, as in `{price:>8.2f}`: `<` aligns left, `>` right and `^` centre, and the width is the **minimum** number of characters. Text aligns left by default and numbers right. Width and precision together line up a column of prices. A character before the alignment sign is used for padding."""),
        CODE("""
        print(f"{'Item':<8}|{'Qty':>4}|{'Price':>8}|")
        print(f"{'gauze':<8}|{12:>4}|{3.5:>8.2f}|")
        print(f"{'saline':<8}|{3:>4}|{12.25:>8.2f}|")
        print(f"{'ok':^6}|{'ok':*^6}|{'too long':<4}|")
        """),
    ],
    exercises=[
        EX("palindrome", "is_palindrome",
           "Write `is_palindrome(s)` that returns `True` when the text reads the same forwards and backwards, ignoring upper or lower case and spaces.",
           "def is_palindrome(s):\n    pass\n",
           """
           f = ns.get("is_palindrome")
           check("defines is_palindrome", lambda: callable(f), "Start with def is_palindrome(s):")
           check_eq('"racecar"', lambda: f("racecar"), True, "Return a bool: compare the text with its reverse t[::-1].")
           check_eq('"Never odd or even"', lambda: f("Never odd or even"), True, "Remove spaces and compare in lower case.")
           check_eq('"hello"', lambda: f("hello"), False, "A word that differs from its reverse must give False.")
           check_eq('""', lambda: f(""), True, "The empty string reads the same both ways.")
           check_eq('"Was it a car or a cat I saw"', lambda: f("Was it a car or a cat I saw"), True, "Lower-case everything and drop every space, not just the first.")
           check_eq('"ab ba c"', lambda: f("ab ba c"), False, "Compare the whole cleaned text, not just its ends.")
           """,
           "Clean the text with replace and lower, then compare it to its reverse `t[::-1]`.",
           'def is_palindrome(s):\n    t = s.replace(" ", "").lower()\n    return t == t[::-1]'),
        EX("initials", "initials",
           'Write `initials(name)` that returns the capitalised initials with a full stop after each, so `"Ada Lovelace"` gives `"A.L."`.',
           "def initials(name):\n    pass\n",
           """
           f = ns.get("initials")
           check("defines initials", lambda: callable(f), "Start with def initials(name):")
           check_eq('"Ada Lovelace"', lambda: f("Ada Lovelace"), "A.L.", "One capital letter and a full stop per word.")
           check_eq("lower case input", lambda: f("grace brewster murray hopper"), "G.B.M.H.", "Use word[0].upper() so lower-case names still give capitals.")
           check_eq("one name", lambda: f("plato"), "P.")
           check_eq("extra spaces", lambda: f("  alan   turing "), "A.T.", "split() with no argument handles extra spaces; split(\\" \\") keeps empty pieces.")
           """,
           "Loop over name.split(). Add word[0].upper() + \".\" to a result string each time.",
           'def initials(name):\n    result = ""\n    for word in name.split():\n        result += word[0].upper() + "."\n    return result'),
        EX("vowels", "count_vowels",
           "Write `count_vowels(s)` that counts the vowels `a e i o u` in a string, ignoring case.",
           "def count_vowels(s):\n    pass\n",
           """
           f = ns.get("count_vowels")
           check("defines count_vowels", lambda: callable(f), "Start with def count_vowels(s):")
           check_eq('"Lime"', lambda: f("Lime"), 2, "Count every vowel, one at a time, and return the number.")
           check_eq('"rhythm"', lambda: f("rhythm"), 0)
           check_eq('"AEIOU"', lambda: f("AEIOU"), 5, "Convert to lower case first.")
           check_eq('""', lambda: f(""), 0)
           check_eq('"Queueing"', lambda: f("Queueing"), 5, "Repeated vowels each count.")
           """,
           "Loop over s.lower() and count the characters that are in \"aeiou\".",
           'def count_vowels(s):\n    count = 0\n    for ch in s.lower():\n        if ch in "aeiou":\n            count += 1\n    return count'),
        EX("last_three", "Fix the slice",
           "`last_three(s)` should return the last three characters of a string, but it returns only two. Fix it. For strings shorter than three characters it should return the whole string.",
           "def last_three(s):\n    return s[len(s) - 2:]\n",
           """
           f = ns.get("last_three")
           check("defines last_three", lambda: callable(f))
           check_eq('"abcdef"', lambda: f("abcdef"), "def", "Three characters means the slice starts three before the end.")
           check_eq('"xy"', lambda: f("xy"), "xy", "With len(s) - 3 the start is -1 for \\"xy\\", and a negative start counts from the END, so you get only \\"y\\". A negative start of -3 is clipped to fit instead: s[-3:].")
           check_eq('""', lambda: f(""), "")
           check_eq('"abc"', lambda: f("abc"), "abc")
           check_eq('"a"', lambda: f("a"), "a", "Short strings come back whole.")
           """,
           "Negative slices count from the end, and a slice start that is too far left is clipped to 0: `s[-3:]`.",
           "def last_three(s):\n    return s[-3:]", kind="fix"),
        EX("reverse_words", "reverse_words",
           'Write `reverse_words(sentence)` that reverses the order of the words, so `"the quick brown fox"` gives `"fox brown quick the"`. Extra spaces should be ignored.',
           "def reverse_words(sentence):\n    pass\n",
           """
           f = ns.get("reverse_words")
           check("defines reverse_words", lambda: callable(f))
           check_eq("basic sentence", lambda: f("the quick brown fox"), "fox brown quick the", "Reverse the list of words, not the characters.")
           check_eq("single word", lambda: f("lime"), "lime", "One word stays as it is (reversing the string would give \\"emil\\").")
           check_eq("extra spaces", lambda: f("  a   b "), "b a", "split() with no argument drops the extra spaces.")
           """,
           "split() gives a list of words, a slice [::-1] reverses a list, and \" \".join glues it back.",
           'def reverse_words(sentence):\n    return " ".join(sentence.split()[::-1])'),
        EX("caesar", "Caesar cipher",
           """
           Write `caesar(text, shift)` that moves every letter from `a` to `z` and from `A` to `Z` `shift` places along the alphabet, wrapping around from `z` to `a`. Keep upper and lower case. Everything else stays unchanged, including accented letters such as `é` (they are letters, but not in this 26-letter alphabet). A negative shift must undo a positive one.""",
           "def caesar(text, shift):\n    pass\n",
           """
           f = ns.get("caesar")
           check("defines caesar", lambda: callable(f))
           check_eq('caesar("abc", 1)', lambda: f("abc", 1), "bcd", "Shift each letter's position: ord(ch) - ord(\\"a\\") + shift.")
           check_eq("wraps around", lambda: f("xyz", 3), "abc", "Use % 26 so positions past z wrap back to a.")
           check_eq("keeps case and punctuation", lambda: f("Hello, World!", 5), "Mjqqt, Btwqi!", "Capitals need ord(\\"A\\") as the base; anything else is copied unchanged.")
           check_eq("negative shift decodes", lambda: f("Mjqqt, Btwqi!", -5), "Hello, World!")
           check_eq("shift of 26 changes nothing", lambda: f("Lime", 26), "Lime")
           check_eq('accented letters stay: caesar("café", 1)', lambda: f("café", 1), "dbgé", "islower() is True for é too. Test the range instead: \\"a\\" <= ch <= \\"z\\".")
           check_eq('caesar("Ærø Zß", 2)', lambda: f("Ærø Zß", 2), "Ætø Bß", "Only a to z and A to Z move. isupper() and isalpha() accept Æ and ß.")
           """,
           "For each character: if \"a\" <= ch <= \"z\", find its position with ord(ch) - ord(\"a\"), add shift, use % 26, then convert back with chr. Do the same with \"A\" for capitals. Copy anything else unchanged.",
           'def caesar(text, shift):\n    result = ""\n    for ch in text:\n        if "a" <= ch <= "z":\n            result += chr((ord(ch) - ord("a") + shift) % 26 + ord("a"))\n        elif "A" <= ch <= "Z":\n            result += chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))\n        else:\n            result += ch\n    return result'),
        EX("title_case", "title_case",
           """
           `"they're back".title()` gives `"They'Re Back"`. Write `title_case(s)` that does it properly: split the text into words on spaces, make the first character of each word upper case and the rest lower case, and join the words with single spaces. Do not use `title()`.

           - `title_case("they're BACK")` is `"They're Back"`""",
           "def title_case(s):\n    return s.title()\n",
           """
           f = ns.get("title_case")
           check("defines title_case", lambda: callable(f))
           check_eq('"they\\'re BACK"', lambda: f("they're BACK"), "They're Back", "title() capitalises after every non-letter, including the apostrophe. Handle each word yourself: word[0].upper() + word[1:].lower().")
           check_eq('"x-ray of o\\'neil"', lambda: f("x-ray of o'neil"), "X-ray Of O'neil", "Only the first character of each space-separated word is capitalised.")
           check_eq("extra spaces", lambda: f("  dr   who "), "Dr Who", "split() with no argument drops extra spaces; join with one space.")
           check_eq("one shouted word", lambda: f("ADA"), "Ada", "The rest of each word must be lower case: word[1:].lower().")
           check("does not call title()", lambda: not uses_call("title"), "Build each word yourself instead of calling title().")
           """,
           "Loop over s.split(). For each word build word[0].upper() + word[1:].lower(), add it and a space to a result string, and strip the last space at the end (or collect the words and \" \".join them).",
           'def title_case(s):\n    result = ""\n    for word in s.split():\n        result += word[0].upper() + word[1:].lower() + " "\n    return result.strip()'),
        EX("parse_pair", "parse_pair",
           """
           Settings arrive as text like `"dose = 5 mg"`. Write `parse_pair(text)` that returns two values, the key and the value, split at the **first** `=` only and with spaces stripped from both. If there is no `=`, the value is `""`.

           - `parse_pair("dose = 5 mg")` returns `("dose", "5 mg")`
           - `parse_pair("a=b=c")` returns `("a", "b=c")`""",
           "def parse_pair(text):\n    key, value = text.split(\"=\")\n    return key, value\n",
           """
           f = ns.get("parse_pair")
           check("defines parse_pair", lambda: callable(f))
           check_eq('"dose = 5 mg"', lambda: f("dose = 5 mg"), ("dose", "5 mg"), "Strip the spaces from both parts with strip().")
           check_eq('"a=b=c"', lambda: f("a=b=c"), ("a", "b=c"), "Split at the first = only: split(\\"=\\", 1) or partition(\\"=\\").")
           check_eq("no = sign", lambda: f("  flag "), ("flag", ""), "With no = there is nothing to split. partition gives an empty value for free.")
           check_eq("empty key", lambda: f("=x"), ("", "x"))
           check_eq("url as value", lambda: f("link = a.org/?q=1"), ("link", "a.org/?q=1"))
           """,
           "`key, _, value = text.partition(\"=\")` always gives three parts, even when there is no `=`. Then return key.strip(), value.strip().",
           'def parse_pair(text):\n    key, _, value = text.partition("=")\n    return key.strip(), value.strip()'),
    ],
    predict=[
        PRED('w = "stethoscope"\nprint(w[:5], w[-5:], w[::3])',
             "`[:5]` is positions 0 to 4 (the stop is excluded): steth. `[-5:]` is the last five: scope. `[::3]` takes positions 0, 3, 6 and 9: s, t, s, p.",
             traps={"stetho scope stsp": "The stop is excluded: `w[:5]` is positions 0 to 4, five characters."}, id="p0"),
        PRED('s = "hello"\ns.replace("l", "L")\nprint(s)',
             "Strings are immutable. `replace()` built a new string, `heLLo`, and nothing kept it, so `s` is unchanged.",
             traps={"heLLo": "`replace` returns a new string; it cannot change `s`. Keep the result: `s = s.replace(...)`.",
                    "heLlo": "`replace` replaces every match, but here its result was thrown away anyway."}, id="p1"),
        PRED('parts = " a  b".split(" ")\nprint(parts, "|".join(parts))',
             "With an explicit separator, `split` cuts at every single space, so the leading space and the double space leave empty strings. A list shows its strings with quotes. `join` puts `|` only between pieces, so the empty pieces show as `||`.",
             traps={"['a', 'b'] a|b": "Only `split()` with no argument drops empty pieces. `split(\" \")` cuts at every single space and keeps the empty strings between them.",
                    "[a, b] a|b": "A list shows each item with repr(), so strings keep their quotes, and `split(\" \")` keeps empty pieces."}, id="p2"),
        PRED('print("nanana".count("nana"), "nanana".find("an"), "nanana".find("x"))',
             "`count` counts non-overlapping matches: after `nana` at 0, only `na` is left, so 1. The first `an` starts at index 1. `find` returns -1 when there is no match.",
             traps={"2 1 -1": "`count` does not count overlapping matches. Once `nana` is used up at 0, the remaining `na` cannot match.",
                    "1 1 None": "`find` returns -1 for no match (and `index` would raise ValueError)."}, id="p3"),
        PRED('w = "tram"\nprint(w[1:99] + w[9:] + "!", len(w[3:1]))',
             "Slices are forgiving: `[1:99]` stops at the end (ram), `[9:]` is empty, and a slice whose start is after its stop is empty, so its length is 0, not -2.",
             traps={"ram! -2": "`len(s[a:b])` is `b - a` only when a <= b; a slice with its start after its stop is empty."}, id="p4"),
        PRED('print(chr(ord("A") + 32), ord("z") - ord("a"))',
             "Every lower-case letter is exactly 32 codes after its capital (A is 65, a is 97). z is 25 places after a, because a is place 0.",
             traps={"a 26": "a is place 0, so z is place 25: the difference between their codes is 25."}, id="p5"),
        PRED('print("python"[4:1:-1], len("python"[1:4:-1]))',
             "A negative step walks right to left, starting AT index 4 (o) and stopping just before index 1: o, h, t. `[1:4:-1]` would have to walk left from 1 to reach 4, so it is empty.",
             traps={"hty 0": "With a negative step the start (4, `o`) is included and the stop (1, `y`) is excluded.",
                    "oht 3": "Walking left from 1 never reaches 4, so `[1:4:-1]` is empty: length 0."}, id="p-neg-step"),
        PRED('print("Zebra" < "apple", "10" < "9", "app" < "apple")',
             "Strings compare by character code from the left. `Z` (90) is smaller than `a` (97). `\"1\"` (49) is smaller than `\"9\"` (57), whatever follows. When one string runs out first, the shorter one is smaller.",
             traps={"False False True": "Strings are not compared alphabetically or as numbers, but by character codes: every capital comes before every lower-case letter, and `\"1\" < \"9\"`.",
                    "False True True": "Capital letters have smaller codes than lower-case ones: `Z` is 90, `a` is 97."}, id="p-compare"),
        PRED('word = "hi"\nprint(word, repr(word), [word, "5", 5])',
             "`print` shows the str() form: hi. `repr` adds the quotes. A list shows every item with repr, so its strings get quotes and the number does not.",
             traps={"hi hi [hi, 5, 5]": "`repr` adds quotes, and a list always shows its items with repr: `['hi', '5', 5]`.",
                    "hi 'hi' ['hi', '5', '5']": "Only strings get quotes; the number 5 is shown as 5."}, id="p-repr"),
        PRED('print("www.lime.com".strip("w.com"))',
             "The argument of `strip` is a set of characters: Python removes w, ., c, o and m from both ends until it meets another character. From the left that takes `www.`; from the right `.com`. Use `removeprefix`/`removesuffix` for exact text.",
             traps={"www.lime.com": "`strip` does not look for the word `w.com`; it removes any of the characters w . c o m from both ends.",
                    "www.lime": "`strip` works on both ends, and treats `w.com` as a set of characters, not as text to find."}, id="p-strip"),
        PRED('print(f"[{\'ab\':>4}][{\'ab\':<4}][{7:03d}]")',
             "`>4` pushes the text to the right of a 4-character field, `<4` to the left. `03d` pads a whole number with zeros to width 3.",
             traps={"[ab  ][  ab][007]": "The arrow points to the side the text moves to: `>` right-aligns, `<` left-aligns.",
                    "[  ab][ab  ][7]": "`03d` pads with zeros to a width of 3: 007."}, id="p-fwidth"),
    ],
    cards=[
        CARD("What index does the first character of a string have?", "0. The last character is at `-1`.", id="c0"),
        CARD("Does the slice `s[2:5]` include index 5?", "No. The stop is excluded, so it has `5 - 2` = 3 characters (if the string is at least 5 long).", id="c1"),
        CARD("How do you reverse a string?", "`s[::-1]`. A step of -1 walks backwards.", id="c2"),
        CARD("`s = \"abc\"`: what do `s[5]` and `s[1:50]` do?", "`s[5]` raises `IndexError`. `s[1:50]` gives `'bc'`: slices stop at the end and never raise IndexError (only a step of 0 is an error).", id="c3"),
        CARD("What does 'strings are immutable' mean?", "You cannot change a string in place. Methods like `upper()` return a new string, so keep the result.", id="c4"),
        CARD("What does `\"a,b,,c\".split(\",\")` give?", "`['a', 'b', '', 'c']`. With an explicit separator, empty pieces are kept.", id="c5"),
        CARD("What does `\"-\".join([\"2026\", \"11\", \"07\"])` give?", "`'2026-11-07'`: the separator goes between items, not after the last.", id="c-join"),
        CARD("`\"abc\".find(\"z\")` versus `\"abc\".index(\"z\")`?", "`find` returns -1. `index` raises `ValueError`.", id="c6"),
        CARD("What is a raw string and when do you use it?", "`r\"...\"` keeps backslashes literally. Useful for Windows paths and regular expressions.", id="c7"),
        CARD("What do `ord` and `chr` do?", "`ord(ch)` gives the numeric code of a character. `chr(n)` gives the character for a code.", id="c8"),
        CARD("In a Caesar shift, `chr((ord(ch) - ord(\"a\") + shift) % 26 + ord(\"a\"))`: why `% 26`?", "There are 26 letters. `% 26` wraps a position past `z` (25) back to the start, so `y` + 3 gives position 1, `b`, instead of a symbol after `z`.", id="c-why-mod26"),
        CARD("What does `print([\"a\", 1])` show, and why the quotes?", "`['a', 1]`. A list shows each item with `repr()`, which puts quotes round strings.", id="c-repr"),
        CARD("`\"Zebra\" < \"apple\"` and `\"10\" < \"9\"`: True or False?", "Both True. Strings compare character codes from the left; capitals (65-90) come before lower case (97-122), and `\"1\"` comes before `\"9\"`.", id="c-compare"),
        CARD("What is `\"python\"[4:1:-1]`?", "`'oht'`. A negative step starts at index 4 (included) and stops before index 1.", id="c-neg-step"),
        CARD("What is wrong with `\"www.lime.com\".strip(\"www.\")` to remove the prefix?", "`strip` treats its argument as a set of characters to peel from both ends, not as text. Use `removeprefix(\"www.\")`.", id="c-strip"),
        CARD("What is `\"aaaa\".count(\"aa\")`?", "2. `count` counts non-overlapping matches.", id="c-count"),
        CARD("What is `\"a=b=c\".split(\"=\", 1)`?", "`['a', 'b=c']`: at most one split. `partition(\"=\")` would give `('a', '=', 'b=c')`.", id="c-split-max"),
        CARD("What does `f\"{'ab':>5}|\"` give?", "`'   ab|'`: right-aligned in a field 5 characters wide.", id="c-fwidth"),
        CARD("Why prefer `\"\".join(pieces)` over `result += piece` in a long loop?", "Strings are immutable, so each `+=` copies everything built so far; `join` builds the result once.", id="c-join-loop"),
    ],
)
