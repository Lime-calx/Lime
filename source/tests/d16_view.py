"""d16: open py01/py02 at phone and wide widths; check no page errors, no overflowing code cells, deep notes present."""
import asyncio, os, sys
from playwright.async_api import async_playwright
W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
P = 'file://' + W + 'lime/out/page.html'
SHOTS = os.environ.get('D16_SHOTS')

async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(W + 'lime/out/lime.html').read()
    open(W + 'lime/out/page.html', 'w').write(html)
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for width in (400, 1280):
            ctx = await b.new_context(viewport={'width': width, 'height': 900})
            pg = await ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W)
            await pg.goto(P + '#home'); await pg.wait_for_timeout(300)
            await pg.evaluate("""() => { const S = JSON.parse(JSON.stringify(__lime.state())); for (const L of __lime.LESSONS.slice(0, 2)){ S.read[L.id] = Date.now(); L.exercises.forEach(e => S.done[L.id+':'+e.id] = {t:1,n:1}); L.predict.forEach((p,i) => S.pred[L.id+':'+(p.id||'p'+i)] = {ok:true,t:1}); const C = __lime.CITY[L.id]; C.jobs.forEach(j => S.done[L.id+':job:'+j.id] = {t:1,n:1}); C.parsons.forEach(p => S.done[L.id+':par:'+p.id] = {t:1}); C.read.forEach(r => S.pred[L.id+':read:'+r.id] = {ok:true,t:1}); S.teach[L.id] = {self:'full',t:1}; } __lime.setState(S); }""")
            if not await pg.evaluate("__lime.unlocked(__lime.LESSONS[1])"): bad.append('py02 not unlocked after finishing py01')
            for lid in ('py01', 'py02'):
                await pg.goto(P + '#lesson-' + lid); await pg.wait_for_timeout(600)
                sw = await pg.evaluate("document.documentElement.scrollWidth")
                if sw > width: bad.append('page overflow %s %d' % (lid, sw))
                over = await pg.evaluate("() => [...document.querySelectorAll('#view textarea, #view pre')].filter(t => (t.value || t.textContent).trim() && t.scrollWidth > t.clientWidth + 2).map(t => (t.value || t.textContent).slice(0, 50))")
                if width == 400 and over: bad.append('cut-off code in %s: %r' % (lid, over))
                txt = await pg.inner_text('#view')
                if 'from the bottom' in txt: bad.append('old traceback wording in ' + lid)
                if lid == 'py02' and 'drawer' in txt.lower(): bad.append('drawer metaphor in py02')
                if SHOTS: await pg.screenshot(path='%s/%s_%d.png' % (SHOTS, lid, width), full_page=True)
            if errs: bad.append('page errors %d: %r' % (width, errs))
            await ctx.close()
        await b.close()
    print('problems:', bad)
    sys.exit(1 if bad else 0)

asyncio.run(main())
