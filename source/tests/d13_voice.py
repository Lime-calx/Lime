"""d13: NIT's voice, error explanations, toasts and sound.
Run from the clone: python3 assemble.py && python3 ui2.py (writes out/page.html) && python3 tests/d13_voice.py"""
import asyncio, json, os, re
from playwright.async_api import async_playwright

W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
P = 'file://' + W + 'lime/out/page.html'
FAIL = []


def ok(label, cond, info=''):
    print(('PASS ' if cond else 'FAIL ') + label + ('' if cond else '  ' + str(info)))
    if not cond: FAIL.append(label)


# err, extra, expected title code, regex the text must match
CASES = [
    ('SyntaxError: invalid syntax  (line 1)', {'etype': 'SyntaxError', 'eline': 1, 'trace': '  File "your code", line 1\n    print(Hello, Lime!)\nSyntaxError: invalid syntax'}, 'SyntaxError', r'inside quotes'),
    ("TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'  (line 1)", {'trace': 'Traceback (most recent call last):\n  File "your code", line 1, in <module>\n    print(4 + 8 + 15) / 3\nTypeError: x'}, 'TypeError', r'gives back `?None|print\(\(4 \+ 8 \+ 15\) / 3\)'),
    ("TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'", {}, 'TypeError', r'None'),
    ('TabError: inconsistent use of tabs and spaces in indentation  (line 3)', {}, 'TabError', r'tab characters and spaces.*line 3'),
    ("ModuleNotFoundError: No module named 'numpy'  (line 1)", {}, 'ModuleNotFoundError', r'numpy'),
    ('ImportError: No module named numpy', {}, 'ModuleNotFoundError', r'pip install'),
    ("OverflowError: (34, 'Numerical result out of range')  (line 1)", {}, 'OverflowError', r'1\.8e308'),
    ("SyntaxError: invalid character '“' (U+201C)  (line 1)", {}, 'SyntaxError', r'curly quote'),
    ('SyntaxError: invalid non-printable character U+00A0  (line 1)', {}, 'SyntaxError', r'non-breaking space'),
    ('SystemExit  (line 3)', {}, 'SystemExit', r'on purpose'),
    ('SyntaxError: unterminated string literal (detected at line 1)  (line 1)', {}, 'SyntaxError', r'quote is missing'),
    ('JavascriptError: Maximum call stack size exceeded', {}, 'RecursionError', r'base case'),
    ('RecursionError: maximum recursion depth exceeded  (line 2)', {'etype': 'RecursionError', 'eline': 2}, 'RecursionError', r'Start at line 2'),
    ('RuntimeError: input() is not available in Lime. Put the value in a variable instead.  (line 1)', {}, 'RuntimeError', r'always returns text'),
    ("Your code no longer defines `total`, and the checker needs it.", {}, 'KeyError', r'Names are exact'),
    ("SyntaxError: '(' was never closed  (line 1)", {}, 'SyntaxError', r'Every `?\(`? needs'),
    ("TypeError: expected string or bytes-like object, got 'UndefinedType'", {}, 'TypeError', r'emoji'),
]
EXPLAIN = """([err, extra]) => { const b = __limeVoice.explainBox(err, extra); if (!b) return null;
  const t = b.querySelector('b'); return {title: t.textContent, code: t.querySelector('code') ? t.querySelector('code').textContent : '', text: b.textContent.slice(t.textContent.length)}; }"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 400, 'height': 800})
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W)
        await pg.goto(P + '#home'); await pg.wait_for_timeout(300)
        await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(300)
        ev = pg.evaluate

        # ---- NIT lines
        lines = await ev("__limeVoice.NIT_LINES")
        for k in ['right', 'rightFirst', 'tries', 'wrong', 'lesson', 'first', 'welcome', 'gap', 'parsonsWrong', 'teach']:
            L = lines.get(k, [])
            ok('NIT %s has 6-10 lines' % k, 6 <= len(L) <= 10, len(L))
            bad = [x for x in L if not re.search(r'`|\d', x)]
            ok('NIT %s: every line has a fact token' % k, not bad, bad)
            ok('NIT %s: no duplicates' % k, len(set(L)) == len(L))
        allL = [x for v in lines.values() for x in v]
        ok('no NIT line says "Mostly to me"', not any('Mostly to me' in x for x in allL))
        html = open(W + 'lime/app.html').read()
        ok('"Mostly to me" is gone from the app', 'Mostly to me' not in html)
        ok('first-visit welcome on a fresh install', await ev("__limeVoice.nitFirstVisit() && __limeVoice.NIT_LINES.first.includes(__limeVoice.nitLine('welcome'))"))
        home_nit = await pg.locator('#view .nit').first.inner_text()
        ok('home shows a first-visit line, not "welcome back"', 'back' not in home_nit.lower(), home_nit)
        r = await ev("""() => { const L = __lime.LESSONS[2], own = __lime.CITY[L.id].nit_right, all = own.concat(__limeVoice.NIT_LINES.right);
          let hits = 0; for (let i = 0; i < 40; i++){ const x = __limeVoice.nitLine('right', L); if (!all.includes(x)) return -1; if (own.includes(x)) hits++; } return hits; }""")
        ok("nitLine('right', L) prefers the lesson's nit_right", r > 15, r)
        await ev("() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.read.py01 = 1; __lime.setState(S); }")
        ok('returning visit uses welcome-back lines', await ev("!__limeVoice.nitFirstVisit() && __limeVoice.NIT_LINES.welcome.includes(__limeVoice.nitLine('welcome'))"))
        gapl = await ev("__limeVoice.nitLine('gap')")
        ok('gap line states real numbers from reviewPlan()', 'Today:' in gapl and re.search(r'\d', gapl.split('Today:')[1] or '') is not None or 'no reviews waiting' in gapl, gapl)

        # ---- error explanations
        for err, extra, code, rx in CASES:
            r = await ev(EXPLAIN, [err, extra])
            good = r and r['code'] == code and r['title'].startswith('NIT EXPLAINS') and re.search(rx, r['text'])
            ok('explainBox: ' + err[:60], bool(good), r)
        r = await ev(EXPLAIN, ['SyntaxError: invalid syntax  (line 1)', {}])
        ok('title keeps the real case (<code>SyntaxError</code>)', r['title'] == 'NIT EXPLAINS SyntaxError' and r['code'] == 'SyntaxError', r)
        r = await ev(EXPLAIN, [None, {'notes': ['time.sleep() does not pause in Lime: the program carried straight on.']}])
        ok('explainBox explains the time.sleep note', r and 'sleep' in r['code'] and 'carries straight on' in r['text'], r)
        ok('explainBox(null) with no notes is null', await ev("__limeVoice.explainBox(null) === null && __limeVoice.explainBox('Python could not start') === null"))
        # level: lesson 1 text avoids if/for/def/type()
        await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(300)
        for err in ['SyntaxError: invalid syntax  (line 1)', 'TypeError: can only concatenate str (not "int") to str  (line 1)', "NameError: name 'Hello' is not defined  (line 1)", 'IndentationError: unexpected indent  (line 1)']:
            r = await ev(EXPLAIN, [err, {}])
            ok('lesson-1 level for ' + err.split(':')[0], not re.search(r'\b(if|for|def|while)\b|type\(', r['text']), r['text'])
        await pg.goto(P + '#lesson-py05'); await pg.wait_for_timeout(300)
        r = await ev(EXPLAIN, ['SyntaxError: invalid syntax  (line 1)', {}])
        ok('later lessons get the full SyntaxError text', '`if`' in r['text'] or 'if' in r['text'], r['text'])
        # real Brython messages through the engine
        snippets = [("print(“hi”)", r'curly quote|non-breaking'), ('print("hi)', r'quote is missing|never closed'),
                    ('import numpy', r'numpy'), ('def f(n):\n    return f(n + 1)\nf(1)', r'base case'),
                    ('print(Hello, Lime!)', r'inside quotes|quote at both ends'), ('print(4 + 8 + 15) / 3', r'None')]
        for code, rx in snippets:
            r = await ev("""async (code) => { const r = await __lime.Py.run(code, ''); const b = __limeVoice.explainBox(r.error, r);
              return {error: r.error, etype: r.etype, text: b ? b.textContent : null}; }""", code)
            ok('Brython: ' + code.split('\n')[0], r['text'] and re.search(rx, r['text']), r)

        # ---- toasts
        r = await ev("""() => { const a = __limeVoice.toast('Copied.'), b = __limeVoice.toast('x', 'EXAM', 'warn'), c = __limeVoice.toast('y', null, 'bad');
          return [a.className, b.className, c.className, __limeVoice.toastKind('That is not a Lime backup.'), __limeVoice.toastKind('Time is up.'), c.getAttribute('role')]; }""")
        ok('toast kinds', r == ['toast ok', 'toast warn', 'toast bad', 'bad', 'warn', 'alert'], r)
        ok('old toast(msg, label) still works', await ev("__limeVoice.toast('Saved.', 'SNIPPET').className === 'toast ok'"))

        # ---- sound settings
        st = await ev("__lime.state().set")
        ok('both sounds off by default', not st.get('sound') and not st.get('ambience'), st)
        await pg.goto(P + '#me'); await pg.wait_for_timeout(300)
        for name in ['Feedback sounds', 'City ambience']:
            await pg.locator('.seg[aria-label="%s"] button' % name).first.click(); await pg.wait_for_timeout(150)
        st = await ev("__lime.state().set")
        ok('toggles turn both on', st.get('sound') is True and st.get('ambience') is True, st)
        await pg.reload(); await pg.wait_for_timeout(400)
        st = await ev("__lime.state().set")
        ok('sound settings persist across reload', st.get('sound') is True and st.get('ambience') is True, st)
        await pg.mouse.click(5, 5); await pg.wait_for_timeout(100)
        ok('ambience starts after a tap', await ev("__limeVoice.Snd.tick !== null"))
        ok('ambience may tick on a plain page', await ev("__limeVoice.Snd.muted()") == '')
        ok('ambience muted during the exam', await ev("(document.body.classList.add('exam-on'), __limeVoice.Snd.muted())") == 'exam')
        await ev("document.body.classList.remove('exam-on')")
        r = await ev("() => { const t = document.createElement('textarea'); document.body.append(t); t.focus(); const m = __limeVoice.Snd.muted(); t.remove(); return m; }")
        ok('ambience muted while typing', r == 'typing', r)
        await pg.locator('.seg[aria-label="City ambience"] button').nth(1).click(); await pg.wait_for_timeout(150)
        ok('ambience off stops the ticking', await ev("__limeVoice.Snd.tick === null && __lime.state().set.ambience === false && __lime.state().set.sound === true"))
        ok('Snd.unlock and Snd.page exist', await ev("typeof __limeVoice.Snd.unlock === 'function' && typeof __limeVoice.Snd.page === 'function'"))

        # ---- index header and empty state
        await ev("localStorage.clear()"); await pg.goto(P + '#index'); await pg.reload(); await pg.wait_for_timeout(300)
        t = await pg.locator('#view').inner_text()
        ok('index header wording', 'Every term from your lessons, filed alphabetically. Precise definitions are a kindness to your future self.' in t, t[:200])
        ok('index empty state is one line', t.count('as you open lessons') + t.count('Each lesson you open files') == 1, t)

        ok('no page errors', not errs, errs)
        await b.close()
    print('FAILED: %d' % len(FAIL) if FAIL else 'ALL PASS')


asyncio.run(main())
