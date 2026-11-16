from dsl import *

CITY = city(
    "py05",
    opener="Strings are rows of characters, numbered from zero. I have always counted from zero. It saves time at the start.",
    scene="""
    Overnight a gust of wind spun every stop sign on the Number 1 line. The sign painter, Juno, has new boards but no idea what codes the old signs carried.

    "There was a pattern," Juno says, "letters and a number. My uncle knew it. The board still runs his program, but the wind shook it about." She holds up the old sign for Brass Yard: `BRA10`.

    NIT reads the board's program aloud. Predict what it prints before you run it:

    ```
    name = "Brass Yard"
    code = name[3:].upper() + str(len(name))
    print(code)
    print(name.replace(" ", "")[:3])
    ```

    NIT: "The slice starts at the cut after the third character instead of stopping there, and nothing removes the space or capitalises the letters it should keep. Your uncle was a string function. Let us rebuild him: the first job writes `stop_code` properly." """,
    jobs=[
        JOB("story", "stop_code", "Stop codes",
            """
            Every stop has a code: the first three letters of its name with spaces removed, in capitals, followed by the length of the full name (spaces included). Write `stop_code(name)`.

            - `stop_code("Brass Yard")` is `"BRA10"`
            - `stop_code("A B")` is `"AB3"` (only two letters exist)""",
            "def stop_code(name):\n    pass\n",
            """
            f = ns.get("stop_code")
            check("defines stop_code", lambda: callable(f), "Start with def stop_code(name):")
            check_eq('"Brass Yard"', lambda: f("Brass Yard"), "BRA10", "Letters first, then the length as text: str(len(name)).")
            check_eq('"Gearwell"', lambda: f("Gearwell"), "GEA8", "Take the first three with [:3], not everything after them with [3:].")
            check_eq('"A B"', lambda: f("A B"), "AB3", "Slicing past the end is safe: it just gives what exists.")
            check_eq('"o ld mill"', lambda: f("o ld mill"), "OLD9", "Remove the spaces before taking the first three letters.")
            check_eq('"quay 12"', lambda: f("quay 12"), "QUA7", "Count the length of the full name, spaces included.")
            """,
            'name.replace(" ", "")[:3].upper() gives the letters; str(len(name)) gives the number.',
            'def stop_code(name):\n    letters = name.replace(" ", "")[:3].upper()\n    return letters + str(len(name))'),
        JOB("repair", "shout", "Repair the sign painter",
            """
            `shout(sign)` should return the sign in capitals with `!` on the end, so `shout("tram stop")` is `"TRAM STOP!"`. It returns `"tram stop!"`. Repair it.""",
            'def shout(sign):\n    sign.upper()\n    return sign + "!"\n\nprint(shout("tram stop"))\n',
            """
            f = ns.get("shout")
            check_eq('shout("tram stop")', lambda: f("tram stop"), "TRAM STOP!", "upper() does not change the string: it returns a new one. Keep it.")
            check_eq('shout("a")', lambda: f("a"), "A!")
            check_eq('shout("Gear 4")', lambda: f("Gear 4"), "GEAR 4!", "Digits and spaces pass through upper() unchanged.")
            """,
            "Strings never change. Keep the result: sign = sign.upper().",
            'def shout(sign):\n    sign = sign.upper()\n    return sign + "!"\n\nprint(shout("tram stop"))', kind="fix"),
    ],
    read=[
        READ("r1", "Juno's sign board",
             """
             s = "clockwork"
             print(s[0], s[-1], s[2:5])
             print(s[::-1][:4])
             print(s.replace("o", "0").count("0"), len(s))
             print("work" in s, s.find("x"), s.find("o"))
             print("-".join(["BRA", "GEA", "OLD"]))
             print(ord("A"), chr(ord("A") + 2))
             """,
             "Index 0 is `c`, -1 is the last character `k`, and `[2:5]` takes positions 2, 3, 4: `ock`. Reversed, `clockwork` is `krowkcolc`; its first four are `krow`. There are two o's. `in` checks for a substring; `find` returns -1 when missing and the first position otherwise (2). `join` glues the list with the separator. `A` is code 65, and two codes later is `C`."),
    ],
    parsons=[
        PARSONS("p1", "Count the vowels on a sign",
                "Order the lines into a function that counts vowels in any capitalisation, then print the count for `Clockwork City` (`3`). Indentation is set. One decoy resets the count in the wrong place.",
                ["def count_vowels(text):", "    total = 0", "    for ch in text.lower():", '        if ch in "aeiou":', "            total += 1", "    return total", 'print(count_vowels("Clockwork City"))'],
                """
                check("prints 3", lambda: out.strip() == "3")
                f = ns.get("count_vowels")
                check('"AEIOU" gives 5', lambda: f is not None and f("AEIOU") == 5)
                """,
                distractors=["        total = 0"]),
    ],
    teach=TEACH(
        "Why does `s[0] = \"X\"` fail, and how do you get a string with a different first letter instead?",
        "Strings are immutable: once made, their characters can never change, so assigning to a position raises TypeError. Instead you build a new string from pieces and move the name to it: `s = \"X\" + s[1:]`. Methods like `upper()` and `replace()` work the same way: they return a new string and leave the old one alone, which is why you must keep their result.",
        points=[
            "Strings are immutable: a character cannot be replaced in place (TypeError)",
            "Build a new string from pieces, e.g. `\"X\" + s[1:]`",
            "Rebind the name to the new string: `s = ...`",
            "Methods such as upper() and replace() also return new strings, so keep their result",
        ]),
    terms=[
        TERM("string", "An immutable sequence of characters.", '`"Brass Yard"` has 10 characters, including the space.', "Treating `\"5\"` as the number 5: it is text until you convert it.", id="t0"),
        TERM("index", "A character's position, counting from 0. Negative indexes count from the end.", '`"tram"[0]` is `"t"`, `"tram"[-1]` is `"m"`.', "Using `len(s)` as an index: the last one is `len(s) - 1`.",
             q="What is the last valid index of a string `s`, counted from the front?", id="t1"),
        TERM("slice", "`s[start:stop:step]` gives a new string from start up to, not including, stop. A slice never raises IndexError; out-of-range ends are cut down to fit.", '`"clockwork"[2:5]` is `"ock"`.', "Expecting `s[2:5]` to include index 5.", card=False, id="t2"),
        TERM("immutable", "Cannot be changed after creation. Strings, numbers and tuples are immutable.", '`s[0] = "X"` raises TypeError for a string.', "Calling `s.upper()` and expecting `s` to change.", card=False, id="t3"),
        TERM("method", "A function attached to a value, called with a dot.", '`name.replace(" ", "")`', "Forgetting the brackets: `name.upper` is the method itself, not its result.", id="t4"),
        TERM("len", "Built-in that returns how many items a sequence has.", '`len("A B")` is 3.', "", q='What is `len("A B")`, and why?', id="t5"),
        TERM("in (substring)", "`a in b` is True if text `a` appears anywhere in `b`. The empty string is in every string.", '`"work" in "clockwork"` is True; `"" in "abc"` is True too.', "Forgetting case: `\"P\" in \"python\"` is False.",
             q='What does `"" in "abc"` give, and why?', id="t6"),
        TERM("escape sequence", "A backslash code inside a string: `\\n` new line, `\\t` tab, `\\\\` backslash.", '`print("a\\tb")` puts a tab between a and b.', "Writing a Windows path like `\"C:\\new\"` and getting a new line; use a raw string.", id="t7"),
        TERM("raw string", "A string prefixed with `r` where backslashes are kept as typed.", '`r"C:\\new"`', "", card=False, id="t8"),
        TERM("ord / chr", "`ord` gives a character's Unicode number; `chr` turns a number back into a character.", '`ord("A")` is 65.', "", card=False, id="t9"),
        TERM("Unicode", "The standard that gives every character in every writing system a number.", '`ord("é")` is 233.', "Assuming every letter is between a and z: `\"é\".isalpha()` is True.",
             q="Why does `\"é\".islower()` give True, and why does that matter for a 26-letter cipher?", id="t10"),
        TERM("repr", "The precise text form of a value, made for programmers: strings get quotes and escapes are spelled out. Lists show their items this way.", '`repr("a\\n")` shows `\'a\\n\'`, quotes included.', "Reading the quotes in `['a']` as part of the text.", card=False, id="t-repr"),
        TERM("partition", "`s.partition(sep)` splits at the first `sep` and returns a tuple of three parts: before, sep, after.", '`"a=b=c".partition("=")` is `(\'a\', \'=\', \'b=c\')`.', "Using `split(\"=\")` and unpacking into two names: `\"a=b=c\"` gives three pieces and the unpacking fails.",
             q='What does `"a=b=c".partition("=")` give?', id="t-partition"),
    ],
    nit_right=[
        "Correct. A slice's stop is a cut, not a character: `s[:3]` ends before index 3.",
        "Accepted. `upper()` gave you a new string. The old one is exactly as it was, as strings always are.",
        "Right. `\"Z\" < \"a\"` because 90 is less than 97. I compare codes, never alphabets.",
    ],
)
