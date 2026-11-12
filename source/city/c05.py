from dsl import *

CITY = city(
    "py05",
    opener="Strings are rows of characters, numbered from zero. I have always counted from zero. It saves time at the start.",
    scene="""
    Overnight a gust of wind spun every stop sign on the Number 1 line. The sign painter, Juno, has new boards but no idea what codes the old signs carried.

    "There was a pattern," Juno says, "letters and a number. My uncle knew it."

    NIT: "Your uncle was a string function. Let us rebuild him." """,
    jobs=[
        JOB("story", "stop_code", "Stop codes",
            """
            Every stop has a code: the first three letters of its name with spaces removed, in capitals, followed by the length of the full name (spaces included). Write `stop_code(name)`.

            - `stop_code("Brass Yard")` is `"BRA10"`
            - `stop_code("A B")` is `"AB3"` (only two letters exist)""",
            "def stop_code(name):\n    pass\n",
            """
            f = ns.get("stop_code")
            check("defines stop_code", lambda: callable(f))
            check('"Brass Yard" gives "BRA10"', lambda: f("Brass Yard") == "BRA10")
            check('"Gearwell" gives "GEA8"', lambda: f("Gearwell") == "GEA8")
            check('"A B" gives "AB3"', lambda: f("A B") == "AB3", "Slicing past the end is safe: it just gives what exists.")
            check('"o ld mill" gives "OLD9"', lambda: f("o ld mill") == "OLD9", "Remove the spaces before taking the first three letters.")
            """,
            'name.replace(" ", "")[:3].upper() gives the letters; str(len(name)) gives the number.',
            'def stop_code(name):\n    letters = name.replace(" ", "")[:3].upper()\n    return letters + str(len(name))'),
        JOB("repair", "shout", "Repair the sign painter",
            """
            `shout(sign)` should return the sign in capitals with `!` on the end, so `shout("tram stop")` is `"TRAM STOP!"`. It returns `"tram stop!"`. Repair it.""",
            'def shout(sign):\n    sign.upper()\n    return sign + "!"\n\nprint(shout("tram stop"))\n',
            """
            f = ns.get("shout")
            check('shout("tram stop") is "TRAM STOP!"', lambda: f("tram stop") == "TRAM STOP!", "upper() does not change the string: it returns a new one.")
            check('shout("a") is "A!"', lambda: f("a") == "A!")
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
        "Strings are immutable: once made, their characters can never change, so assigning to a position raises TypeError. Instead you build a new string from pieces and move the name to it: `s = \"X\" + s[1:]`. Methods like `upper()` and `replace()` work the same way: they return a new string and leave the old one alone, which is why you must keep their result."),
    terms=[
        TERM("string", "An immutable sequence of characters.", '`"Brass Yard"`', ""),
        TERM("index", "A character's position, counting from 0. Negative indexes count from the end.", '`"tram"[0]` is `"t"`, `"tram"[-1]` is `"m"`.', "Using `len(s)` as an index: the last one is `len(s) - 1`."),
        TERM("slice", "`s[start:stop:step]` gives a new string from start up to, not including, stop. Out-of-range slices are safe.", '`"clockwork"[2:5]` is `"ock"`.', ""),
        TERM("immutable", "Cannot be changed after creation. Strings, numbers and tuples are immutable.", "", "Calling `s.upper()` and expecting `s` to change."),
        TERM("method", "A function attached to a value, called with a dot.", '`name.replace(" ", "")`', ""),
        TERM("len", "Built-in that returns how many items a sequence has.", '`len("A B")` is 3.', ""),
        TERM("in (substring)", "`a in b` is True if text `a` appears anywhere in `b`.", '`"work" in "clockwork"`', ""),
        TERM("escape sequence", "A backslash code inside a string: `\\n` new line, `\\t` tab, `\\\\` backslash.", "", ""),
        TERM("raw string", "A string prefixed with `r` where backslashes are kept as typed.", '`r"C:\\new"`', ""),
        TERM("ord / chr", "`ord` gives a character's Unicode number; `chr` turns a number back into a character.", '`ord("A")` is 65.', ""),
        TERM("Unicode", "The standard that gives every character in every writing system a number.", "", ""),
    ],
)
