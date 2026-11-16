# d11: workbench + snippet library (random ids, overwrite prompt, unsaved-code guard, UNDO toast, Ctrl+Z,
# open status, SAVE / SAVE AS, rename, search, sort, delete, Enter / Ctrl+S save, copy, trace + notes, sync-safe ids).
# Run from the clone:  python3 assemble.py && python3 tests/d11_bench.py   (writes out/page.html like ui2.py)
import asyncio, os, re
from playwright.async_api import async_playwright
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = os.path.dirname(L.rstrip('/')) + '/'
P = 'file://' + L + 'out/page.html'
fails = []
def ok(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

SNIPS = "Object.entries(__lime.state().snip).filter(([k,v])=>!v.gone).map(([k,v])=>({id:k,name:v.name,code:v.code}))"

async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(L + 'out/lime.html').read()
    open(L + 'out/page.html', 'w').write(html)
    init = "window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W
    async with async_playwright() as p:
        b = await p.chromium.launch()
        errs = []
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        await ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
        pg = await ctx.new_page(); await pg.add_init_script(init)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(P + '#bench'); await pg.wait_for_timeout(400)
        ta = pg.locator('.bench textarea.ta'); nb = pg.locator('.bench .namebox')
        dlg = pg.locator('#modal .dlg')
        async def code(): return await ta.input_value()
        async def dlg_click(label):
            await dlg.get_by_role('button', name=label, exact=True).click(); await pg.wait_for_timeout(150)
        async def row(name): return pg.locator('.snip', has=pg.locator('b', has_text=re.compile('^' + re.escape(name))))

        h = await ta.evaluate("t=>t.getBoundingClientRect().height")
        ok(h >= 200, 'bench page editor is at least 200 px tall (%d)' % h)
        ok(await pg.evaluate("getComputedStyle(document.querySelector('.bench-full .bar2')).position") == 'sticky', 'RUN bar is sticky on the Bench page')

        # Enter in the name box saves; ids are random, not the name
        await ta.fill('print("A")'); await nb.fill('A'); await nb.press('Enter'); await pg.wait_for_timeout(200)
        s = await pg.evaluate(SNIPS)
        ok(len(s) == 1 and s[0]['name'] == 'A' and s[0]['code'] == 'print("A")', 'Enter in the name box saves')
        ok(re.match(r'^s[a-z0-9]{8,}$', s[0]['id']) is not None, 'snippet id is random (%s)' % s[0]['id'])
        st = await pg.locator('.bench-status').inner_text()
        ok('OPEN' in st and 'A' in st and 'saved' in st, 'status shows the open snippet (%r)' % st)

        # same name, other case: asks Overwrite / Save as copy
        await ta.fill('print("other")'); await nb.fill('a'); await pg.get_by_role('button', name='SAVE', exact=True).click(); await pg.wait_for_timeout(200)
        ok(await dlg.count() == 1 and 'already' in await dlg.inner_text(), 'saving an existing name asks first')
        await dlg_click('Save as copy')
        s = await pg.evaluate(SNIPS)
        ok(sorted(x['name'] for x in s) == ['A', 'a (2)'] and len(set(x['id'] for x in s)) == 2, 'Save as copy keeps both (%s)' % [x['name'] for x in s])
        await ta.fill('print("A2")'); await nb.fill('A'); await pg.get_by_role('button', name='SAVE AS').click(); await pg.wait_for_timeout(200)
        await dlg_click('Overwrite')
        s = await pg.evaluate(SNIPS)
        ok(len(s) == 2 and [x['code'] for x in s if x['name'] == 'A'] == ['print("A2")'], 'Overwrite replaces the named snippet')

        # Ctrl+S in the editor updates the open snippet (A is open now)
        await ta.fill('print("A3")'); st = await pg.locator('.bench-status').inner_text()
        ok('changed' in st, 'status marks unsaved changes (%r)' % st)
        await ta.focus(); await pg.keyboard.press('Control+s'); await pg.wait_for_timeout(200)
        s = await pg.evaluate(SNIPS)
        ok(await dlg.count() == 0 and [x['code'] for x in s if x['name'] == 'A'] == ['print("A3")'] and len(s) == 2, 'Ctrl+S saves the open snippet')

        # OPEN with unsaved code: Cancel keeps it, Replace + UNDO restores it
        await ta.fill('unsaved scratch'); r = await row('a (2)')
        await r.get_by_role('button', name='OPEN').click(); await pg.wait_for_timeout(200)
        ok(await dlg.count() == 1 and 'Unsaved' in await dlg.inner_text(), 'OPEN over unsaved code asks first')
        await dlg_click('Cancel')
        ok(await code() == 'unsaved scratch', 'Cancel keeps the bench code')
        await r.get_by_role('button', name='OPEN').click(); await pg.wait_for_timeout(200); await dlg_click('Replace')
        ok(await code() == 'print("other")', 'Replace opens the snippet')
        u = pg.locator('.toast.bench-undo')
        ok(await u.count() == 1, 'UNDO toast after OPEN')
        await u.get_by_role('button', name='UNDO').click(); await pg.wait_for_timeout(150)
        ok(await code() == 'unsaved scratch', 'UNDO restores the previous bench code')
        # Ctrl+Z after OPEN
        await r.get_by_role('button', name='OPEN').click(); await pg.wait_for_timeout(200); await dlg_click('Replace')
        await ta.focus(); await pg.keyboard.press('Control+z'); await pg.wait_for_timeout(150)
        ok(await code() == 'unsaved scratch', 'Ctrl+Z in the editor brings back the code before OPEN (%r)' % await code())

        # CLEAR with unsaved code: Save first, then UNDO
        # (Ctrl+Z also put back which snippet was open: A, where 'unsaved scratch' was typed)
        ok('A' in await pg.locator('.bench-status').inner_text(), 'Ctrl+Z restores the open snippet too')
        n0 = len(await pg.evaluate(SNIPS))
        await pg.get_by_role('button', name='CLEAR').click(); await pg.wait_for_timeout(200)
        ok(await dlg.count() == 1, 'CLEAR over unsaved code asks first')
        await dlg_click('Save first')
        s = await pg.evaluate(SNIPS)
        ok(await code() == '' and len(s) == n0 and [x['code'] for x in s if x['name'] == 'A'] == ['unsaved scratch'], 'Save first saves into the open snippet, then clears')
        await pg.locator('.toast.bench-undo').get_by_role('button', name='UNDO').click(); await pg.wait_for_timeout(150)
        ok(await code() == 'unsaved scratch', 'UNDO after CLEAR restores the code')
        await pg.wait_for_timeout(4200)
        ok(await pg.locator('.toast.bench-undo').count() == 0, 'UNDO toast goes away after 4 s')

        # rename (Enter in the dialog), search, sort, copy, delete
        r = await row('A')
        await r.get_by_role('button', name='RENAME').click(); await pg.wait_for_timeout(150)
        await dlg.locator('input').fill('Alpha'); await dlg.locator('input').press('Enter'); await pg.wait_for_timeout(150)
        ok('Alpha' in [x['name'] for x in await pg.evaluate(SNIPS)], 'rename works')
        await pg.locator('.snip-tools .search').fill('alp'); await pg.wait_for_timeout(100)
        names = await pg.locator('.snip .t b').all_inner_texts()
        ok(len(names) == 1 and names[0].startswith('Alpha'), 'search filters by name (%s)' % names)
        await pg.locator('.snip-tools .search').fill('')
        await pg.locator('.snip-tools [data-sort=name]').click(); await pg.wait_for_timeout(100)
        names = [re.sub(r'OPEN$', '', n.strip()).strip() for n in await pg.locator('.snip .t b').all_inner_texts()]
        ok(names == sorted(names, key=str.lower), 'A-Z sort (%s)' % names)
        r = await row('Alpha'); await r.get_by_role('button', name='COPY').click(); await pg.wait_for_timeout(200)
        clip = await pg.evaluate("navigator.clipboard.readText().catch(()=> '')")
        ok(clip == 'unsaved scratch' or await dlg.count() == 1, 'COPY copies the code (%r)' % clip)
        if await dlg.count(): await dlg_click('Done')
        n0 = len(await pg.evaluate(SNIPS))
        await r.get_by_role('button', name='DEL').click(); await pg.wait_for_timeout(150); await dlg_click('Delete')
        ok(len(await pg.evaluate(SNIPS)) == n0 - 1 and await pg.evaluate("Object.values(__lime.state().snip).some(v=>v.gone&&v.t)"), 'delete asks and leaves a {gone,t} marker')

        # sync-safe: the same name saved on two devices keeps both
        m = await pg.evaluate("""(()=>{const a=JSON.parse(JSON.stringify(__lime.state())), b=JSON.parse(JSON.stringify(a));
          a.snip.sx1aaaaaaaa={name:'Loop',code:'1',t:1000}; b.snip.sy2bbbbbbbb={name:'Loop',code:'2',t:2000};
          const m=__lime.mergeState(a,b); return Object.values(m.snip).filter(v=>v.name==='Loop').length;})()""")
        ok(m == 2, 'merge keeps same-named snippets from two devices (%s)' % m)

        # output: traceback + NIT notes
        await ta.fill('import time\ntime.sleep(1)\ndef f():\n    return 1/0\nf()\n'); await pg.get_by_role('button', name='RUN').click()
        await pg.wait_for_selector('.bench .out .err', timeout=60000); await pg.wait_for_timeout(200)
        ok(await pg.locator('.bench .out details.trace').count() == 1, 'full traceback shown')
        ok('time.sleep' in ' '.join(await pg.locator('.bench .explain').all_inner_texts()), 'runner notes shown')
        ok(any('NIT EXPLAINS' in t for t in await pg.locator('.bench .explain').all_inner_texts()), 'NIT explanation shown')

        # lesson split view: TO BENCH over unsaved code asks; aside stays compact
        await ta.fill('my experiment'); await pg.wait_for_timeout(500)
        await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(500)
        ok(await pg.evaluate("document.querySelector('.aside textarea').value") == 'my experiment', 'aside bench shows the same code')
        ah = await pg.evaluate("document.querySelector('.aside textarea').getBoundingClientRect().height")
        ok(ah <= 560, 'aside editor stays within its cap (%d); d09 gives it a 200px+ minimum beside the lesson' % ah)
        await pg.evaluate("document.querySelector('.cell .tobench').click()"); await pg.wait_for_timeout(200)
        ok(await dlg.count() == 1, 'TO BENCH over unsaved code asks first')
        await dlg_click('Save first'); await pg.wait_for_timeout(100)
        v = await pg.evaluate("document.querySelector('.aside textarea').value")
        ok(v != 'my experiment' and await pg.locator('.toast.bench-undo').count() == 1, 'TO BENCH replaces and offers UNDO')
        ok(any(x['code'] == 'my experiment' and x['name'].startswith('Bench ') for x in await pg.evaluate(SNIPS)), 'Save first on scratch code saves a dated snippet')
        await pg.locator('.toast.bench-undo').get_by_role('button', name='UNDO').click(); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("document.querySelector('.aside textarea').value") == 'my experiment', 'UNDO after TO BENCH')

        ok(not errs, 'no page errors %s' % errs)
        await b.close()
    print('fails:', fails)

asyncio.run(main())
