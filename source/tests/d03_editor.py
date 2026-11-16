# d03: code editor tests (touch tap after typing, key row, selection indent, undo, Enter rules, Esc-Tab, drafts).
# Run from the clone:  python3 assemble.py && python3 tests/d03_editor.py   (writes out/page.html like ui2.py)
import asyncio, os, sys
from playwright.async_api import async_playwright
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = os.path.dirname(L.rstrip('/')) + '/'  # folder that holds lime/ and node_modules/
P = 'file://' + L + 'out/page.html'
fails = []
def ok(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(L + 'out/lime.html').read()
    open(L + 'out/page.html', 'w').write(html)
    init = "window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W
    async with async_playwright() as p:
        b = await p.chromium.launch()
        errs = []
        # ---------- touch phone ----------
        ctx = await b.new_context(viewport={'width': 400, 'height': 860}, has_touch=True, is_mobile=True, device_scale_factor=1)
        pg = await ctx.new_page(); await pg.add_init_script(init)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(400)
        e0 = (await pg.evaluate("__lime.LESSONS[0]"))['exercises'][0]['id']
        box = pg.locator('#ex-py01-' + e0)
        ta = box.locator('textarea'); chk = box.get_by_role('button', name='CHECK')
        await ta.scroll_into_view_if_needed()
        await pg.evaluate("window.scrollBy(0, 200)")
        r = await ta.bounding_box()
        await pg.touchscreen.tap(r['x'] + 40, r['y'] + 20); await pg.wait_for_timeout(450)
        ok(await pg.evaluate("document.activeElement.classList.contains('ta')"), 'touch: tap focuses the editor')
        ok(await pg.evaluate("!!document.querySelector('.keys:not([hidden])')"), 'touch: key row shows (any-pointer:coarse)')
        await pg.keyboard.press('End'); await pg.keyboard.type('\nprint("x")')
        await pg.wait_for_timeout(450)
        kb = await pg.evaluate("(()=>{const k=document.querySelector('.keys');const r=k.getBoundingClientRect();return {top:r.top,bottom:r.bottom,h:visualViewport.height,labels:[...k.querySelectorAll('button')].map(b=>b.textContent)}})()")
        ok(abs(kb['bottom'] - kb['h']) < 2, 'touch: key row pinned to the bottom of the visual viewport (%s)' % kb['bottom'])
        ok(kb['labels'][:10] == ['⇥', ':', '(', ')', '"', '=', '[', ']', ',', '.'] and '!' in kb['labels'] and '←' in kb['labels'] and '→' in kb['labels'], 'touch: key order + ! and arrows')
        c1 = await chk.bounding_box()
        cx, cy = c1['x'] + c1['width'] / 2, c1['y'] + c1['height'] / 2
        hit = await pg.evaluate("([x,y])=>document.elementFromPoint(x,y)?.textContent", [cx, cy])
        ok(hit == 'CHECK', 'touch: CHECK is not covered by the key row (hit=%r)' % hit)
        await pg.touchscreen.tap(cx, cy); await pg.wait_for_timeout(150)
        c2 = await chk.bounding_box()
        ok(abs(c2['y'] - c1['y']) < 1, 'touch: CHECK did not move on blur (%.0f -> %.0f)' % (c1['y'], c2['y']))
        ran = await box.locator('.out:not([hidden]), .res:not([hidden])').count()
        ok(ran > 0, 'touch: first tap on CHECK after typing runs the check')
        ok(await pg.evaluate("!!document.querySelector('.keys[hidden]')"), 'touch: key row hidden after blur')
        # key row inserts into the focused editor and keeps focus
        await pg.touchscreen.tap(r['x'] + 40, r['y'] + 20); await pg.wait_for_timeout(400)
        await pg.keyboard.press('Control+End')
        before = await ta.input_value()
        kr = await pg.locator('.keys button[data-k=":"]').bounding_box()
        await pg.touchscreen.tap(kr['x'] + kr['width'] / 2, kr['y'] + kr['height'] / 2)
        kr = await pg.locator('.keys button[data-k="Left"]').bounding_box()
        await pg.touchscreen.tap(kr['x'] + kr['width'] / 2, kr['y'] + kr['height'] / 2)
        kr = await pg.locator('.keys button[data-k="("]').bounding_box()
        await pg.touchscreen.tap(kr['x'] + kr['width'] / 2, kr['y'] + kr['height'] / 2)
        ok(await ta.input_value() == before + '(:', 'touch: keys insert, <- moves caret (%r)' % (await ta.input_value())[-4:])
        ok(await pg.evaluate("document.activeElement.classList.contains('ta')"), 'touch: focus stays in the editor after key taps')
        # simulated soft keyboard: long code on the bench, short viewport
        await pg.set_viewport_size({'width': 360, 'height': 400})
        await pg.goto(P + '#bench'); await pg.wait_for_timeout(400)
        bt = pg.locator('.ta').first
        await bt.evaluate("(t)=>{t.value=Array.from({length:30},(_, i)=>'print('+i+')').join('\\n');t.dispatchEvent(new Event('input'))}")
        await bt.scroll_into_view_if_needed(); await pg.wait_for_timeout(100)  # the bench header grew (d11), so the editor starts below a 400px viewport
        r = await bt.bounding_box()
        await pg.touchscreen.tap(r['x'] + 30, r['y'] + 15); await pg.wait_for_timeout(450)
        await pg.keyboard.press('Control+End'); await pg.keyboard.type('x'); await pg.wait_for_timeout(200)
        g = await pg.evaluate("(()=>{const k=document.querySelector('.keys').getBoundingClientRect(),t=document.querySelector('.ta').getBoundingClientRect();return {kt:k.top,kb:k.bottom,th:t.height,vh:visualViewport.height}})()")
        ok(g['kb'] <= g['vh'] + 1 and g['kt'] > 0, 'keyboard open: key row stays on screen with 30 lines (%s)' % g)
        ok(g['th'] <= g['vh'] * 0.45 + 4 or g['th'] <= 142, 'keyboard open: editor capped to ~45%% of visual viewport (%.0f)' % g['th'])
        await ctx.close()

        # ---------- desktop keyboard ----------
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800})
        pg = await ctx.new_page(); await pg.add_init_script(init)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(P + '#bench'); await pg.wait_for_timeout(400)
        ok(await pg.evaluate("__limeEd.prefs.get().keys") == 'auto', 'prefs: default keys auto')
        ta = pg.locator('.ta').first
        async def setv(v, s, e):
            await ta.evaluate("(t,[v,s,e])=>{t.value=v;t.focus();t.setSelectionRange(s,e)}", [v, s, e])
        src = 'for i in range(3):\nprint(i)\nprint(2)\n'
        await setv(src, src.index('print(i)'), len(src) - 1)
        await pg.keyboard.press('Tab')
        ok(await ta.input_value() == 'for i in range(3):\n    print(i)\n    print(2)\n', 'Tab indents every selected line')
        await pg.keyboard.press('Shift+Tab')
        ok(await ta.input_value() == src, 'Shift-Tab dedents every selected line')
        mix = 'a\n  b\n\tc\n      d'
        await setv(mix, 0, len(mix)); await pg.keyboard.press('Shift+Tab')
        ok(await ta.input_value() == 'a\nb\nc\n  d', 'Shift-Tab handles 2 spaces, a tab, and 6 spaces (%r)' % await ta.input_value())
        # undo after Tab/Enter (native history via execCommand)
        await setv('', 0, 0)
        await pg.keyboard.type('abc'); await pg.keyboard.press('Tab'); await pg.keyboard.type('x'); await pg.keyboard.press('Enter'); await pg.keyboard.type('y')
        full = await ta.input_value()
        ok(full == 'abc x\ny', 'typing with Tab/Enter: %r' % full)
        seen = []
        for _ in range(8):
            await pg.keyboard.press('Control+z'); seen.append(await ta.input_value())
            if seen[-1] == '': break
        ok(seen[-1] == '' and 'abc' in seen and 'abc x' in seen, 'Ctrl+Z undoes step by step through Enter and Tab %r' % seen)
        for _ in range(8):
            await pg.keyboard.press('Control+Shift+z')
            if await ta.input_value() == full: break
        ok(await ta.input_value() == full, 'Ctrl+Shift+Z redoes (%r)' % await ta.input_value())
        await setv('for i in x:\n    print(i)\n', 0, 0)
        await pg.keyboard.press('Control+a'); await pg.keyboard.press('Tab'); await pg.keyboard.press('Control+z')
        ok(await ta.input_value() == 'for i in x:\n    print(i)\n', 'Ctrl+Z undoes a block indent')
        # Enter rules
        cases = [('if x:', '    '), ('    for i in r:  # loop', '        '), ('d = {"a":', ''), ('x = 1  # see:', ''),
                 ('    return x', ''), ('        break', '    '), ('    pass', ''), ('    raise ValueError', ''), ('    continue  # next', ''),
                 ('    f(a,', '    '), ('x = [', '    '), ('else:', '    '), ('    elif y:', '        '), ('class A:', '    '),
                 ('    s = "a:"', '    '), ('lambda x:', ''), ('while True:', '    '), ('try:', '    '), ('match cmd:', '    '), ('    case 1:', '        ')]
        bad = []
        for line, want in cases:
            got = await pg.evaluate("(s)=>__limeEd.enterIndent(s)", line)
            if got != want: bad.append((line, got, want))
        ok(not bad, 'Enter indent rules %s' % (bad or ''))
        await setv('def f(n):', 9, 9); await pg.keyboard.press('Enter'); await pg.keyboard.type('return n'); await pg.keyboard.press('Enter'); await pg.keyboard.type('z')
        ok(await ta.input_value() == 'def f(n):\n    return n\nz', 'Enter in the editor: indent after def, dedent after return')
        # Esc releases the Tab trap
        await setv('', 0, 0)
        await pg.evaluate("document.querySelector('.ta').blur()"); await pg.wait_for_timeout(700)
        await ta.focus()
        ok(await pg.evaluate("!document.querySelector('.edhint').hidden"), 'keyboard focus shows "Esc then Tab to leave"')
        await pg.keyboard.press('Tab')
        ok(await ta.input_value() == '    ' and await pg.evaluate("document.activeElement.classList.contains('ta')"), 'Tab inside the editor indents and keeps focus')
        await pg.keyboard.press('Escape'); await pg.keyboard.press('Tab')
        ok(await pg.evaluate("!document.activeElement.classList.contains('ta')") and await ta.input_value() == '    ', 'Esc then Tab leaves the editor (now on %s)' % await pg.evaluate("document.activeElement.textContent.slice(0,20)"))
        await pg.keyboard.press('Shift+Tab')
        ok(await pg.evaluate("document.activeElement.classList.contains('ta')"), 'Shift-Tab returns to the editor')
        await pg.keyboard.press('Tab')
        ok(await ta.input_value() == '        ', 'after refocus Tab indents again')
        # setting hook
        await pg.evaluate("__limeEd.prefs.set({keys:'on'})")
        ok(await pg.evaluate("JSON.parse(localStorage.getItem('lime.editor')).keys") == 'on', 'prefs: stored in lime.editor')
        await ta.click(); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("!!document.querySelector('.keys:not([hidden])')"), "prefs: keys 'on' shows the row on desktop")
        await pg.evaluate("__limeEd.prefs.set({keys:'off'})")
        await pg.evaluate("document.querySelector('.ta').blur()"); await ta.click(); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("!document.querySelector('.keys:not([hidden])')"), "prefs: keys 'off' hides it")
        await pg.evaluate("__limeEd.prefs.set({keys:'auto'})")
        # fallback undo stack when execCommand is unavailable
        await pg.evaluate("__limeEd.prefs._noExec=true"); await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(300)
        await pg.evaluate("__limeEd.prefs._noExec=true")
        await pg.goto(P + '#bench'); await pg.wait_for_timeout(300)
        ta = pg.locator('.ta').first
        await pg.evaluate("__limeEd.prefs._noExec=true")
        await setv('', 0, 0); await pg.keyboard.type('ab'); await pg.wait_for_timeout(800); await pg.keyboard.press('Tab'); await pg.keyboard.press('Enter')
        v1 = await ta.input_value()
        await pg.keyboard.press('Control+z'); a1 = await ta.input_value()
        await pg.keyboard.press('Control+z'); a2 = await ta.input_value()
        await pg.keyboard.press('Control+Shift+z'); await pg.keyboard.press('Control+Shift+z'); a3 = await ta.input_value()
        ok(a1 == 'ab  ' and a2 == 'ab' and a3 == v1, 'fallback undo/redo stack (%r %r %r)' % (a1, a2, a3))
        await pg.evaluate("__limeEd.prefs._noExec=false")

        # drafts: flush on reload within 100 ms
        await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(400)
        box = pg.locator('#ex-py01-' + e0); ta = box.locator('textarea')
        await ta.click(); await pg.keyboard.press('Control+End'); await pg.keyboard.type('# keep me')
        await pg.wait_for_timeout(60); await pg.reload(); await pg.wait_for_timeout(400)
        ok((await pg.locator('#ex-py01-' + e0 + ' textarea').input_value()).endswith('# keep me'), 'draft survives a reload 60 ms after typing')
        # drafts: flushed before CHECK (click), with no wait at all
        ta = pg.locator('#ex-py01-' + e0 + ' textarea')
        await ta.click(); await pg.keyboard.press('Control+End'); await pg.keyboard.type('!')
        await pg.evaluate("document.querySelector('#ex-py01-%s .bar2 button').click()" % e0)
        ok(await pg.evaluate("JSON.parse(localStorage.getItem('lime.drafts'))['%s']" % ('py01-' + e0) + "?.endsWith('!') || Object.values(JSON.parse(localStorage.getItem('lime.drafts'))).some(v=>String(v).endsWith('# keep me!'))"), 'draft flushed before CHECK click')
        # multi-tab merge
        pa = pg; pb = await ctx.new_page(); await pb.add_init_script(init)
        await pb.goto(P + '#bench'); await pb.wait_for_timeout(300)
        await pb.locator('.ta').first.evaluate("(t)=>{t.focus();t.value='# from B';t.dispatchEvent(new Event('input'));t.blur()}")
        await pa.wait_for_timeout(100)
        await pa.locator('#ex-py01-' + e0 + ' textarea').evaluate("(t)=>{t.focus();t.value='# from A';t.dispatchEvent(new Event('input'));t.blur()}")
        st = await pa.evaluate("JSON.parse(localStorage.getItem('lime.drafts'))")
        ok(st.get('__bench') == '# from B' and '# from A' in st.values(), 'two tabs: both drafts kept')
        ok(await pa.evaluate("__limeEd.drafts().__bench") == '# from B', 'two tabs: storage event updates the other tab')
        await ctx.close(); await b.close()
        ok(not errs, 'no page errors %s' % errs)
    print('d03 editor:', 'ALL PASS' if not fails else '%d FAILED' % len(fails))
    sys.exit(1 if fails else 0)
asyncio.run(main())
