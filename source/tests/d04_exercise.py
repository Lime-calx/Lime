"""d04: exercise component - help ladder persists, FIRST LINES never gives the answer, HINT scroll/hold/tap,
expected/got rendering, traceback on errors, role=status summary, h3 titles, MORE toggle on phones.

Run from the clone:  python3 assemble.py && python3 tests/d04_exercise.py
"""
import asyncio, os, json
from playwright.async_api import async_playwright

LIME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.dirname(LIME) + '/'
P = 'file://' + LIME + '/out/d04_page.html'
fails = []


def ok(cond, what):
    print(('PASS ' if cond else 'FAIL ') + what)
    if not cond:
        fails.append(what)


async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(LIME + '/out/lime.html').read()
    open(LIME + '/out/d04_page.html', 'w').write(html)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 400, 'height': 860}, has_touch=True)
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W)
        await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(400)
        L = await pg.evaluate("__lime.LESSONS[0]")
        hello = next(e for e in L['exercises'] if e['id'] == 'hello')
        box = pg.locator('#ex-py01-hello')

        # headings and narrow-screen buttons
        ok(await box.locator('h3.ext').count() == 1, 'exercise title is an h3')
        ok(not await box.get_by_role('button', name='SOLUTION').is_visible(), 'SOLUTION hidden behind MORE on a phone')
        await box.get_by_role('button', name='MORE').click()
        ok(await box.get_by_role('button', name='SOLUTION').is_visible() and await box.get_by_role('button', name='RESET').is_visible(), 'MORE reveals SOLUTION and RESET')

        # HINT: a scroll that starts on the button is not a peek
        hb = box.get_by_role('button', name='HINT')
        await hb.scroll_into_view_if_needed()
        await hb.evaluate("""b => { const r = b.getBoundingClientRect(), x = r.x + 5, y = r.y + 5;
            const o = {bubbles:true, pointerId:1, pointerType:'touch', isPrimary:true};
            b.dispatchEvent(new PointerEvent('pointerdown', Object.assign({clientX:x, clientY:y}, o)));
            b.dispatchEvent(new PointerEvent('pointermove', Object.assign({clientX:x, clientY:y - 120}, o)));
            b.dispatchEvent(new PointerEvent('pointercancel', o)); }""")
        st = await pg.evaluate("__lime.state().help['py01:hello'] || null")
        ok(st is None or not st.get('h'), 'scroll starting on HINT does not mark hinted')
        ok(await box.get_by_role('button', name='FIRST LINES').is_disabled(), 'FIRST LINES still disabled after the scroll')
        ok(await box.locator('.box:not(.sol)').is_hidden(), 'hint hidden after pointercancel')
        # hold for 400 ms: a peek, recorded, closes again
        await hb.evaluate("""b => new Promise(res => { const o = {bubbles:true, pointerId:2, pointerType:'touch', isPrimary:true};
            b.dispatchEvent(new PointerEvent('pointerdown', o)); setTimeout(() => { b.dispatchEvent(new PointerEvent('pointerup', o)); b.click(); res(); }, 400); })""")
        st = await pg.evaluate("__lime.state().help['py01:hello']")
        ok(st and st['h'] == 1 and st['lv'] == 1, 'hold >= 350 ms records the hint')
        ok(await box.locator('.box:not(.sol)').is_hidden() and await hb.get_attribute('aria-expanded') == 'false', 'hold-to-peek closes on release (the trailing click is ignored)')
        await hb.click()
        ok(await box.locator('.box:not(.sol)').is_visible() and await hb.get_attribute('aria-expanded') == 'true', 'tap keeps the hint open')

        # FIRST LINES on a 1-line solution: a skeleton, never the answer
        await box.get_by_role('button', name='FIRST LINES').click()
        part = await box.locator('.box.sol').first.inner_text()
        ok('print(___)' in part and 'Hello, Lime!' not in part, 'FIRST LINES shows a skeleton for a 1-line solution: ' + part.split('\n')[1][:40])
        # fix-it with one changed line: points at the line, does not show the fix
        av = pg.locator('#ex-py01-average')
        await av.get_by_role('button', name='HINT').click(); await av.get_by_role('button', name='MORE').click()
        await av.get_by_role('button', name='FIRST LINES').click()
        t = await av.locator('.box.sol').first.inner_text()
        ok('line 4' in t and '(a + b + c)' not in t, 'FIRST LINES on a fix-it names the line to change without the fix')

        # SOLUTION (confirmed) then reload: the peek is remembered
        await box.get_by_role('button', name='SOLUTION').click()
        await pg.get_by_role('button', name='Show it').click()
        await pg.wait_for_timeout(200)
        ok(await pg.evaluate("__lime.state().help['py01:hello'].lv") == 3, 'SOLUTION sets level 3')
        await pg.reload(); await pg.wait_for_timeout(500)
        box = pg.locator('#ex-py01-hello')
        st = await pg.evaluate("__lime.state().help['py01:hello']")
        ok(st and st['lv'] == 3 and st['h'] == 1, 'help ladder survives a reload')

        # wrong answer: expected/got in monospace, role=status summary
        await box.locator('textarea').fill('print("hello lime")')
        await box.get_by_role('button', name='CHECK').click()
        await box.locator('.res:not([hidden]) li').first.wait_for(timeout=60000)
        det = box.locator('.res li.no code.det')
        ok(await det.count() >= 1 and 'Expected' in await det.first.inner_text() and 'got' in await det.first.inner_text(), 'expected/got detail rendered under the failing row')
        ff = await det.first.evaluate("e => getComputedStyle(e).fontFamily")
        ok('mono' in ff.lower() or 'courier' in ff.lower() or 'consol' in ff.lower(), 'detail is monospace (' + ff[:30] + ')')
        stat = await box.locator('[role=status]').inner_text()
        ok(' of ' in stat and 'passed' in stat and stat.split()[0].isdigit(), 'role=status summary: ' + stat)

        # runtime error: traceback shown with the NIT explanation and a summary
        await box.locator('textarea').fill('x = 1\nprint(x / 0)')
        await box.get_by_role('button', name='CHECK').click()
        await box.locator('.out .err').wait_for(timeout=30000)
        await pg.wait_for_timeout(200)
        err = await box.locator('.out .err').inner_text()
        ok('Traceback' in err and 'line 2' in err and 'ZeroDivisionError' in err, 'short traceback rendered')
        ok(await box.locator('.explain').count() >= 1, 'NIT explanation for the error')
        stat = await box.locator('[role=status]').inner_text()
        ok('ZeroDivisionError' in stat and 'no checks ran' in stat, 'error summary announced: ' + stat)

        # solve after the peek: honest message and a peek record
        await box.locator('textarea').fill(hello['solution'])
        await box.get_by_role('button', name='CHECK').click()
        await box.locator('.win:not([hidden])').wait_for(timeout=30000)
        win = await box.locator('.win').inner_text()
        done = await pg.evaluate("__lime.state().done['py01:hello']")
        ok(done['peek'] == 1 and done['n'] == 3, 'solve record keeps the peek and all attempts: ' + json.dumps(done))
        ok('First try' not in win and 'solution' in win.lower(), 'win message is honest: ' + win.replace('\n', ' ')[:90])
        nr = await pg.evaluate("__lime.CITY['py01'].nit_right")
        ok(any(x[:20].replace('`', '') in win for x in nr), 'lesson-specific NIT line shown')
        stat = await box.locator('[role=status]').inner_text()
        ok('Solved' in stat, 'solved summary announced')

        # merge keeps a peek from either device
        m = await pg.evaluate("""() => { const a = __lime.state(); const b = JSON.parse(JSON.stringify(a));
            a.help = {k:{t:10, h:1, lv:3, n:2}}; b.help = {k:{t:20, h:0, lv:0, n:1}, k2:{t:5, h:1, lv:1, n:0}};
            return __lime.mergeState(a, b).help; }""")
        ok(m['k']['lv'] == 3 and m['k']['h'] == 1 and m['k']['n'] == 2 and m['k']['t'] == 20 and 'k2' in m, 'mergeState: help newest wins, peek/hint/attempts never lost')
        ok(not errs, 'no page errors ' + str(errs[:2]))
        await b.close()
    print('fails:', fails)
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
