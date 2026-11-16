"""d09: layout. No horizontal overflow on every route at 320-2560; TO BENCH visible when the bench sits beside the lesson (>=1280);
rail x constant across routes; wide-screen columns; 44px touch targets on coarse pointers; toast placement; exam hides the tab bar.
Set D09_SHOTS=<dir> for screenshots."""
import asyncio, os, sys
from playwright.async_api import async_playwright
W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
P = 'file://' + W + 'lime/out/page.html'
SHOTS = os.environ.get('D09_SHOTS')
ROUTES = ['home', 'map', 'd-py', 'cards', 'index', 'bench', 'me', 'redo', 'lesson-py01', 'lesson-py05', 'story-py', 'archive-py', 'exam-py', 'ending-py']
WIDTHS = [320, 360, 390, 800, 1280, 1440, 1920, 2560]
DONE = """() => { const S = JSON.parse(JSON.stringify(__lime.state())); for (const L of __lime.LESSONS){ S.read[L.id]=Date.now(); L.exercises.forEach(e=>S.done[L.id+':'+e.id]={t:Date.now()-5*86400000,n:1}); L.predict.forEach((p,i)=>S.pred[L.id+':'+(p.id||'p'+i)]={ok:true,t:1}); const C=__lime.CITY[L.id]; C.jobs.forEach(j=>S.done[L.id+':job:'+j.id]={t:1,n:1}); C.parsons.forEach(p=>S.done[L.id+':par:'+p.id]={t:1}); C.read.forEach(r=>S.pred[L.id+':read:'+r.id]={ok:true,t:1}); S.teach[L.id]={self:'full',t:1}; } S.seen['py:story']=1; __lime.setState(S); }"""

async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(W + 'lime/out/lime.html').read()
    open(W + 'lime/out/page.html', 'w').write(html)
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for width in WIDTHS:
            touch = width <= 800
            hgt = 1440 if width == 2560 else 800 if width >= 1280 else 844
            ctx = await b.new_context(viewport={'width': width, 'height': hgt}, has_touch=touch, is_mobile=touch)
            pg = await ctx.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W)
            await pg.goto(P + '#home'); await pg.wait_for_timeout(250)
            await pg.evaluate(DONE)
            rails = {}
            for r in ROUTES:
                await pg.evaluate("sessionStorage.removeItem('lime.exam')")  # a live exam asks before leaving (d08)
                await pg.goto(P + '#' + r); await pg.reload(); await pg.wait_for_timeout(250)
                if r == 'exam-py':
                    await pg.get_by_role('button', name='BEGIN').click(); await pg.wait_for_timeout(150)
                sw = await pg.evaluate("document.documentElement.scrollWidth")
                if sw > width: bad.append('overflow %s @%d: %d' % (r, width, sw))
                if width < 600:
                    cut = await pg.evaluate("() => [...document.querySelectorAll('#view pre.wrapl')].filter(x => x.offsetParent && x.scrollWidth > x.clientWidth + 1).length")
                    if cut: bad.append('%d read-only code blocks still cut off on %s @%d' % (cut, r, width))
                if width >= 900 and r != 'exam-py':
                    rails[r] = await pg.evaluate("Math.round(document.getElementById('nav').getBoundingClientRect().x)")
                if SHOTS and (r in ('home', 'map', 'd-py', 'me', 'bench', 'lesson-py01', 'exam-py')):
                    await pg.screenshot(path='%s/%s_%d.png' % (SHOTS, r, width))
            if rails and len(set(rails.values())) != 1: bad.append('rail moves @%d: %r' % (width, rails))
            # lesson: TO BENCH and the split view
            await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(300)
            vis = await pg.evaluate("() => [...document.querySelectorAll('.tobench')].filter(x => getComputedStyle(x).display !== 'none' && x.getBoundingClientRect().width > 0).length")
            aside = await pg.evaluate("() => { const a = document.querySelector('.aside'); return a && getComputedStyle(a).display !== 'none' ? Math.round(a.getBoundingClientRect().width) : 0; }")
            if width >= 1280 and (not vis or not aside): bad.append('TO BENCH/aside hidden @%d (%d buttons, aside %d)' % (width, vis, aside))
            if width < 1000 and (vis or aside): bad.append('split view shown on narrow @%d' % width)
            if width >= 1280:
                exp = max(440, min(720, round(0.36 * width)))
                if abs(aside - exp) > 2: bad.append('aside width @%d: %d, want %d' % (width, aside, exp))
                edges = await pg.evaluate("() => { const m = document.querySelector('.lgrid>.lay-a, .lgrid>div:not(.laybar)'); const r = m.getBoundingClientRect(); return [...m.querySelectorAll(':scope>.card, :scope>.prose, .prose>.cell, :scope>.pred, :scope>.ex')].filter(x => x.offsetParent).map(x => Math.round(x.getBoundingClientRect().right - r.right)).filter(d => Math.abs(d) > 1).length; }")
                if edges: bad.append('ragged lesson column @%d: %d blocks' % (width, edges))
                await pg.locator('.tobench:visible').first.click(); await pg.wait_for_timeout(150)
                t = await pg.evaluate("() => { const t = document.querySelector('#toasts .toast'), m = document.getElementById('view').getBoundingClientRect(); if (!t) return null; const r = t.getBoundingClientRect(); return {top:r.top, right:r.right, mright:m.right, pe:getComputedStyle(t).pointerEvents}; }")
                if not t or t['top'] > 40 or abs(t['right'] - t['mright']) > 4 or t['pe'] != 'none': bad.append('toast placement @%d: %r' % (width, t))
                # the toggle turns the split off and is remembered
                await pg.locator('.benchtog').click(); await pg.wait_for_timeout(100)
                off = await pg.evaluate("[document.getElementById('app').classList.contains('bench-side'), localStorage.getItem('lime.layout')]")
                if off[0] or 'off' not in (off[1] or ''): bad.append('bench toggle @%d: %r' % (width, off))
                await pg.locator('.benchtog').click(); await pg.wait_for_timeout(100)
                if not await pg.evaluate("document.getElementById('app').classList.contains('bench-side')"): bad.append('bench toggle does not turn back on @%d' % width)
                ed = await pg.evaluate("Math.round(document.querySelector('.aside .ta').getBoundingClientRect().height)")
                if ed < 200: bad.append('bench editor too short @%d: %d' % (width, ed))
            if width == 1440:
                await pg.goto(P + '#bench'); await pg.wait_for_timeout(200)
                sbs = await pg.evaluate("() => { const c = document.querySelector('#view .cell'); return getComputedStyle(c).display; }")
                if sbs != 'grid': bad.append('bench page not side by side @1440')
            if width >= 1600:
                for r, sel in (('home', '.v-home .lay-b'), ('d-py', '.v-district .lay-b')):
                    await pg.goto(P + '#' + r); await pg.wait_for_timeout(200)
                    x = await pg.evaluate("(s) => { const a = document.querySelector(s.replace('lay-b','lay-a')), b = document.querySelector(s); return a && b ? [a.getBoundingClientRect().top, b.getBoundingClientRect().top, b.getBoundingClientRect().left - a.getBoundingClientRect().right] : null; }", sel)
                    if not x or abs(x[0] - x[1]) > 2 or x[2] < 10: bad.append('%s not in two columns @%d: %r' % (r, width, x))
                await pg.goto(P + '#map'); await pg.wait_for_timeout(200)
                cols = await pg.evaluate("getComputedStyle(document.querySelector('.map')).gridTemplateColumns.split(' ').length")
                if cols < 5: bad.append('map only %d columns @%d' % (cols, width))
            if touch:
                coarse = await pg.evaluate("matchMedia('(pointer:coarse)').matches")
                if not coarse: bad.append('pointer not coarse in touch context @%d' % width)
                for r in ('lesson-py01', 'me', 'd-py'):
                    await pg.goto(P + '#' + r); await pg.wait_for_timeout(200)
                    small = await pg.evaluate("() => [...document.querySelectorAll('.btn.small, .crumb, .chip, .seg button, input[type=range]')].filter(x => x.offsetParent && x.getBoundingClientRect().height < 44).map(x => x.className + ':' + Math.round(x.getBoundingClientRect().height))")
                    if small: bad.append('small targets on %s @%d: %r' % (r, width, small[:5]))
                # bottom nav never covers the end of the page
                await pg.evaluate("sessionStorage.removeItem('lime.exam')"); await pg.goto(P + '#me'); await pg.reload(); await pg.wait_for_timeout(250)
                await pg.evaluate("window.scrollTo(0, 1e6)"); await pg.wait_for_timeout(100)
                cov = await pg.evaluate("() => { const v = document.getElementById('view').getBoundingClientRect(), n = document.getElementById('nav').getBoundingClientRect(); return [v.bottom, n.top]; }")
                if cov[0] > cov[1] + 1: bad.append('nav covers content @%d: %r' % (width, cov))
                # toasts: bottom normally, top while a text field is focused
                await pg.goto(P + '#bench'); await pg.wait_for_timeout(200)
                y1 = await pg.evaluate("__limeLayout.toast('x').getBoundingClientRect().top")
                try:
                    await pg.focus('.namebox', timeout=5000)
                except Exception as e:
                    print('DEBUG', width, await pg.evaluate("location.hash + ' modal:' + !document.querySelector('#modal').hidden + ' ' + document.querySelector('#view').textContent.slice(0,150)")); raise
                y2 = await pg.evaluate("__limeLayout.toast('y', null, 'warn').getBoundingClientRect().top")
                if not (y1 > hgt / 2 and y2 < 130): bad.append('phone toast placement @%d: %r' % (width, (y1, y2)))
                # exam running: tab bar hidden
                await pg.evaluate("document.body.classList.add('exam-on')")
                nv = await pg.evaluate("getComputedStyle(document.getElementById('nav')).display")
                if nv != 'none': bad.append('nav shown during exam @%d' % width)
                await pg.evaluate("document.body.classList.remove('exam-on')")
            if errs: bad.append('page errors @%d: %r' % (width, errs[:3]))
            await ctx.close()
        await b.close()
    print('problems:', bad)
    sys.exit(1 if bad else 0)

asyncio.run(main())
