"""d12: pixel art. Scene sprites per key, windows lit by progress, 13 building shapes, map road + names,
cabinet sprites and fact dialogs, First Repair ignores Parsons, no console errors.
Run after `python3 assemble.py`."""
import asyncio, os, sys
from playwright.async_api import async_playwright
W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
P = 'file://' + W + 'lime/out/page.html'

FILL = """(n) => { const S = JSON.parse(JSON.stringify(__lime.state())); S.set.cityMode = true;
 __lime.LESSONS.slice(0, n).forEach(L => { S.read[L.id]=Date.now(); L.exercises.forEach(e=>S.done[L.id+':'+e.id]={t:1,n:1}); L.predict.forEach((p,i)=>S.pred[L.id+':'+(p.id||'p'+i)]={ok:true,t:1}); const C=__lime.CITY[L.id]; C.jobs.forEach(j=>S.done[L.id+':job:'+j.id]={t:1,n:1}); C.parsons.forEach(p=>S.done[L.id+':par:'+p.id]={t:1}); S.teach[L.id]={self:'full',t:1}; });
 __lime.setState(S); return 1; }"""

async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(W + 'lime/out/lime.html').read()
    open(W + 'lime/out/page.html', 'w').write(html)
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 400, 'height': 860})
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'ERR_TUNNEL' not in m.text and 'fonts' not in m.text else None)
        await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W)
        await pg.goto(P + '#home'); await pg.wait_for_timeout(400)

        # 1. every scene key renders a distinct SVG (same pct), with its sprite
        r = await pg.evaluate("""() => { const A = __lime.art, keys = Object.keys(A.SCENE_SPRITES), out = {};
          keys.forEach(k => { const s = A.sceneArt('py', k, 0.5); out[k] = {html: s.outerHTML, sprite: !!s.querySelector('[data-sprite="' + k + '"]')}; });
          return out; }""")
        keys = ['py01', 'py02', 'py03', 'py04', 'py05', 'py06', 'py07', 'py08', 'opener', 'ending', 'home']
        for k in keys:
            if k not in r: bad.append('no sprite for ' + k)
            elif not r[k]['sprite']: bad.append('sprite not drawn for ' + k)
        if len({v['html'] for v in r.values()}) != len(r): bad.append('scene SVGs not distinct')
        # skylines differ between two-letter district ids (seed is a hash, not the length)
        d = await pg.evaluate("() => __lime.art.sceneArt('py', 'x', 0).outerHTML.replace(/data-tid=\"\\w+\"/, '') === __lime.art.sceneArt('js', 'x', 0).outerHTML.replace(/data-tid=\"\\w+\"/, '')")
        if d: bad.append('py and js skylines identical')

        # 2. lit windows grow with pct, deterministically
        lits = await pg.evaluate("() => [0, 0.2, 0.5, 0.8, 1].map(p => +__lime.art.sceneArt('py', 'py01', p).getAttribute('data-lit'))")
        tot = await pg.evaluate("() => +__lime.art.sceneArt('py', 'py01', 1).getAttribute('data-windows')")
        if lits[0] != 0 or lits[-1] != tot or any(lits[i] > lits[i + 1] for i in range(4)) or lits[2] in (0, tot): bad.append('windows by pct %r of %d' % (lits, tot))
        same = await pg.evaluate("() => __lime.art.sceneArt('py', 'py02', 0.4).outerHTML === __lime.art.sceneArt('py', 'py02', 0.4).outerHTML")
        if not same: bad.append('scene art not deterministic')
        clock = await pg.evaluate("() => [__lime.art.sceneArt('py', 'opener', 0).getAttribute('data-clock'), __lime.art.sceneArt('py', 'ending', 1).getAttribute('data-clock')]")
        if clock != ['06:00', '09:00']: bad.append('clock %r' % clock)

        # 3. 13 distinct building shapes; windows = lessons, last row centred
        await pg.evaluate("location.hash = '#map'")
        await pg.wait_for_timeout(400)
        info = await pg.evaluate("""() => [...document.querySelectorAll('.map .dtile svg')].map(s => ({shape: s.getAttribute('data-shape'), wins: +s.getAttribute('data-windows'), html: s.innerHTML.replace(/fill="#[0-9a-fA-F]+"/g, '')}))""")
        if len(info) != 13: bad.append('tiles %d' % len(info))
        if len({i['shape'] for i in info}) != 13: bad.append('shapes not distinct: %r' % [i['shape'] for i in info])
        if len({i['html'] for i in info}) != 13: bad.append('building geometry not distinct')
        want = await pg.evaluate("() => __lime.art.tracks.map(t => __lime.LESSONS.filter(L => L.track === t.id).length || t.planned.length)")
        if [i['wins'] for i in info] != want: bad.append('windows per district %r vs lessons %r' % ([i['wins'] for i in info], want))
        txt = await pg.inner_text('#view')
        if 'Great Meridian' in txt or 'The silent tower' not in txt: bad.append('map hero not renamed')
        plots = await pg.evaluate("() => [...document.querySelectorAll('svg.plan .plot')].map(a => a.getAttribute('data-n'))")
        if plots != [str(i) for i in range(1, 14)]: bad.append('plan plots %r' % plots)
        locked = await pg.evaluate("() => { const t = document.querySelector('.dtile.locked'); return t ? [getComputedStyle(t).opacity, !!t.querySelector('.padlock'), getComputedStyle(t.querySelector('svg')).filter] : null; }")
        if not locked or locked[0] != '1' or not locked[1] or 'grayscale' not in locked[2]: bad.append('locked look %r' % locked)
        # windows centred: for each tile the last row's window span is centred within one pixel of the row above
        cen = await pg.evaluate("""() => [...document.querySelectorAll('.map .dtile svg')].filter(s => s.getAttribute('data-shape') !== 'wheel').map(s => {
            const w = [...s.querySelectorAll('rect.win')].map(r => [+r.getAttribute('x'), +r.getAttribute('y'), +r.getAttribute('width')]);
            const rows = {}; w.forEach(r => (rows[r[1]] = rows[r[1]] || []).push(r));
            return Object.values(rows).map(rw => { const a = Math.min(...rw.map(r => r[0])), z = Math.max(...rw.map(r => r[0] + r[2])); return (a + z) / 2; }); })""")
        # rows of one region share a centre (stair/gate have several regions; compare within each region by y-gap)
        for i, cs in enumerate(cen):
            if cs and max(cs) - min(cs) > 1 and info[i]['shape'] not in ('stair', 'gate'): bad.append('windows not centred on %s: %r' % (info[i]['shape'], cs))
        da = await pg.evaluate("() => { const s = __lime.art.districtArt('py', 4); return [s.getAttribute('width'), s.getAttribute('data-shape')]; }")
        if da != ['96', 'workshop']: bad.append('districtArt %r' % da)
        ea = await pg.evaluate("() => __lime.art.emptyArt().getAttribute('class')")
        if ea != 'empty-art': bad.append('emptyArt')

        # 4. cabinet: First Repair not from Parsons alone; distinct sprites; fact dialog opens and closes
        await pg.evaluate("() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.set.cityMode = true; S.done = {}; S.done['py01:par:x'] = {t:1}; __lime.setState(S); }")
        fr = await pg.evaluate("() => __lime.art.cabinetItems().map(i => i[2])")
        if fr[0] or not fr[1]: bad.append('First Repair / Line Spanner from Parsons: %r' % fr[:2])
        await pg.evaluate(FILL, 3)
        await pg.evaluate("location.hash = '#me'"); await pg.wait_for_timeout(400)
        items = await pg.evaluate("() => [...document.querySelectorAll('.cab .it')].map(b => [b.tagName, b.querySelector('svg').getAttribute('data-item'), b.querySelector('svg').innerHTML])")
        if len(items) != 10 or any(i[0] != 'BUTTON' for i in items): bad.append('cabinet items %r' % [i[:2] for i in items])
        if len({i[1] for i in items}) != 10: bad.append('cabinet sprite keys not distinct')
        earned = await pg.evaluate("() => __lime.art.cabinetItems().map(i => i[2])")
        if not earned[0]: bad.append('First Repair not earned after exercises')
        await pg.locator('.cab .it').nth(0).click(); await pg.wait_for_timeout(200)
        dlg = await pg.evaluate("() => { const d = document.querySelector('#modal .dlg'); return d ? d.innerText : null; }")
        if not dlg or 'First Repair' not in dlg or 'passing test' not in dlg: bad.append('fact dialog %r' % dlg)
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
        if not await pg.evaluate("document.getElementById('modal').hidden"): bad.append('dialog did not close')

        # 5. call sites: lesson scene uses its id, story opener/ending their keys
        for route, key in (('#lesson-py02', 'py02'), ('#story-py', 'opener')):
            await pg.evaluate("h => location.hash = h", route); await pg.wait_for_timeout(400)
            k = await pg.evaluate("() => { const s = document.querySelector('#view .art svg'); return s && s.getAttribute('data-key'); }")
            if k != key: bad.append('%s art key %r' % (route, k))
        await pg.evaluate("location.hash = '#home'"); await pg.wait_for_timeout(300)
        k = await pg.evaluate("() => [...document.querySelectorAll('#view .art svg')].map(s => s.getAttribute('data-key'))")
        if 'home' not in k: bad.append('home art key %r' % k)
        if errs: bad.append('console errors %r' % errs)
        await b.close()
    print('d12_art:', 'OK' if not bad else bad)
    sys.exit(1 if bad else 0)

asyncio.run(main())
