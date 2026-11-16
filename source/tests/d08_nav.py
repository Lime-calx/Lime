"""d08: routing, focus, keyboard, gamepad and the exam.
Run from the clone: python3 assemble.py && python3 ui2.py (writes out/page.html) && python3 tests/d08_nav.py"""
import asyncio, datetime, os
from playwright.async_api import async_playwright

W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
P = 'file://' + W + 'lime/out/page.html'
FAIL = []


def ok(label, cond, info=''):
    print(('PASS ' if cond else 'FAIL ') + label + ('' if cond else '  ' + str(info)))
    if not cond: FAIL.append(label)


ALL_DONE = """() => { const S = JSON.parse(JSON.stringify(__lime.state()));
  __lime.LESSONS.forEach(L => { S.read[L.id] = 1; L.exercises.forEach(e => S.done[L.id + ':' + e.id] = {t: 1, n: 1});
    L.predict.forEach((p, j) => S.pred[L.id + ':' + (p.id || 'p' + j)] = {ok: true, t: 1});
    const C = __lime.CITY[L.id]; C.jobs.forEach(j => S.done[L.id + ':job:' + j.id] = {t: 1, n: 1}); C.parsons.forEach(p => S.done[L.id + ':par:' + p.id] = {t: 1});
    C.read.forEach(r => S.pred[L.id + ':read:' + r.id] = {ok: true, t: 1}); S.teach[L.id] = {self: 'full', t: 1}; });
  __lime.setState(S); }"""
# give every exam slot two alternatives so the "no reuse" rule can be seen (d20 adds real pools)
POOL = """() => { __lime.DIST.py.exam.forEach((sl, i) => { if (sl.items.length < 2) sl.items.push({id: 'alt' + i, code: 'print(' + (100 + i) + ')', ans: String(100 + i), why: 'alt'}); if (!sl.lesson) sl.lesson = 'py0' + (1 + i % 8); }); }"""
CODES = "() => [...document.querySelectorAll('.pred pre.src')].map(p => p.textContent)"
ANS = """(code) => { for (const sl of __lime.DIST.py.exam) for (const x of sl.items) if (x.code === code) return x.ans; return null; }"""
PAD = """() => { window.__pad = {buttons: Array.from({length: 17}, () => ({pressed: false, value: 0})), axes: [0, 0, 0, 0], connected: true, index: 0, id: 'stub', mapping: 'standard'};
  navigator.getGamepads = () => [window.__pad]; window.dispatchEvent(new Event('gamepadconnected')); }"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800})
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W)
        await pg.clock.install(time=datetime.datetime(2026, 11, 13, 9, 0, 0))
        await pg.goto(P + '#home'); await pg.wait_for_timeout(300)
        ev = pg.evaluate
        await ev(ALL_DONE); await pg.wait_for_timeout(100)

        # ---- titles, focus, nav kept ----
        ok('home title', (await pg.title()) == 'Today · Lime', await pg.title())
        await pg.focus('#nav a[data-r="map"]'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(150)
        ok('map title', (await pg.title()) == 'Map · Lime', await pg.title())
        ok('focus on h1 after route change', await ev("document.activeElement.tagName") == 'H1', await ev("document.activeElement.outerHTML.slice(0,80)"))
        ok('aria-current moved', await ev("document.querySelector('#nav a[data-r=map]').getAttribute('aria-current')") == 'page')
        await ev("location.hash='#lesson-py01'"); await pg.wait_for_timeout(300)
        ok('lesson title', (await pg.title()).startswith('Lesson 1: '), await pg.title())
        ok('skip link first in tab order', await ev("(() => { document.activeElement.blur(); return document.querySelector('#app').firstElementChild.id; })()") == 'skip')

        # ---- scroll restore ----
        await ev("window.scrollTo(0, 3000)"); await pg.wait_for_timeout(400)
        y0 = await ev("scrollY")
        await ev("location.hash='#bench'"); await pg.wait_for_timeout(200)
        ok('forward link goes to top', await ev("scrollY") == 0)
        await pg.go_back(); await pg.wait_for_timeout(500)
        y1 = await ev("scrollY")
        ok('Back restores lesson scroll', abs(y1 - y0) < 5 and y0 > 1000, (y0, y1))
        await pg.go_forward(); await pg.wait_for_timeout(300)
        ok('Forward lands on bench', await ev("location.hash") == '#bench')

        # ---- shortcuts ----
        await ev("document.activeElement.blur()")
        await pg.keyboard.press('g'); await pg.keyboard.press('c'); await pg.wait_for_timeout(200)
        ok('g c -> cards', await ev("location.hash") == '#cards')
        await pg.keyboard.press('/'); await pg.wait_for_timeout(200)
        ok('/ focuses index search', await ev("location.hash") == '#index' and await ev("document.activeElement.type") == 'search')
        await pg.keyboard.type('gm'); await pg.wait_for_timeout(100)
        ok('typing in search is not a shortcut', await ev("location.hash") == '#index')
        await ev("location.hash='#lesson-py01'"); await pg.wait_for_timeout(300)
        await pg.keyboard.press('Alt+b'); await pg.wait_for_timeout(100)
        ok('Alt+B focuses bench editor', await ev("document.activeElement.getAttribute('aria-label')") == 'Workbench code')
        await ev("document.activeElement.blur(); scrollTo(0,0)")
        await pg.keyboard.press(']'); await pg.wait_for_timeout(100); await pg.keyboard.press(']'); await pg.wait_for_timeout(100)
        ok('] jumps to section 2', (await ev("document.activeElement.textContent")).startswith('2.'), await ev("document.activeElement.textContent"))
        await pg.keyboard.press('['); await pg.wait_for_timeout(100)
        ok('[ jumps back to section 1', (await ev("document.activeElement.textContent")).startswith('1.'))
        await pg.keyboard.press('Shift+Slash'); await pg.wait_for_timeout(100)
        ok('? opens help', await ev("!document.querySelector('#modal').hidden && document.querySelector('#modal').textContent.includes('Alt+B')"))

        # ---- dialog trap ----
        ok('app inert under dialog', await ev("document.querySelector('#app').inert"))
        ok('aria-describedby set', await ev("!!document.getElementById(document.querySelector('.dlg').getAttribute('aria-describedby'))"))
        for _ in range(4): await pg.keyboard.press('Tab')
        ok('Tab stays in dialog', await ev("document.querySelector('#modal').contains(document.activeElement)"))
        await pg.keyboard.press('Shift+Tab')
        ok('Shift+Tab stays in dialog', await ev("document.querySelector('#modal').contains(document.activeElement)"))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
        ok('Escape closes, app not inert, still on lesson', await ev("document.querySelector('#modal').hidden && !document.querySelector('#app').inert && location.hash === '#lesson-py01'"))

        # ---- arrows move focus ----
        await ev("location.hash='#home'"); await pg.wait_for_timeout(200)
        await pg.keyboard.press('ArrowDown'); await pg.wait_for_timeout(50)
        a1 = await ev("document.activeElement.textContent")
        await pg.keyboard.press('ArrowDown'); await pg.wait_for_timeout(50)
        a2 = await ev("document.activeElement.textContent")
        ok('arrows move focus between controls', a1 != a2 and await ev("document.activeElement.tagName") in ('A', 'BUTTON'), (a1, a2))

        # ---- gamepad ----
        await ev(PAD); await pg.wait_for_timeout(100)
        ok('gamepad toast + gp mode', await ev("document.documentElement.classList.contains('gp') && document.querySelector('#toasts').textContent.includes('GAMEPAD CONNECTED')"))

        async def press(i, ms=80):
            await ev("(i) => { __pad.buttons[i].pressed = true; __pad.buttons[i].value = 1; }", i); await pg.wait_for_timeout(ms)
            await ev("(i) => { __pad.buttons[i].pressed = false; __pad.buttons[i].value = 0; }", i); await pg.wait_for_timeout(ms)
        await press(9)
        ok('Start -> Me', await ev("location.hash") == '#me')
        await press(5)
        ok('R1 -> next nav item from Me (home)', await ev("location.hash") in ('#home',), await ev("location.hash"))
        await press(5)
        ok('R1 -> map', await ev("location.hash") == '#map')
        await press(1); await pg.wait_for_timeout(100)
        ok('B goes back', await ev("location.hash") == '#home', await ev("location.hash"))
        await press(13); f1 = await ev("document.activeElement.outerHTML.slice(0,60)")
        await press(13); f2 = await ev("document.activeElement.outerHTML.slice(0,60)")
        ok('D-pad moves focus', f1 != f2, (f1, f2))
        await press(8)
        ok('Select opens help', await ev("!document.querySelector('#modal').hidden"))
        await press(1)
        ok('B closes dialog', await ev("document.querySelector('#modal').hidden"))
        # X runs the example cell in a lesson
        await ev("location.hash='#lesson-py01'"); await pg.wait_for_timeout(300); await pg.clock.run_for(1000); await pg.wait_for_timeout(100)
        await ev("() => { const c = [...document.querySelectorAll('.cell')].find(x => x.checkVisibility()); c.id = 'xcell'; c.scrollIntoView({block:'center'}); c.querySelector('button').focus(); window.__runs = 0; c.querySelector('button').addEventListener('click', () => window.__runs++); }")
        await press(2)
        await pg.wait_for_timeout(100)
        ok('X presses RUN in the current cell (page.clock stalls the worker, so only the click is checked)', await ev("__runs") == 1, await ev("document.activeElement.outerHTML.slice(0,80)"))
        # flashcards
        await ev("location.hash='#cards'"); await pg.wait_for_timeout(200)
        await pg.get_by_role('button', name='START REVIEW').click(); await pg.wait_for_timeout(200)
        n0 = await ev("Object.keys(__lime.state().cards).length")
        await press(0)
        ok('A flips the card', await ev("!document.querySelector('.rate').hidden"))
        await press(15); await pg.wait_for_timeout(100)
        ok('D-pad right rates Good', await ev("Object.keys(__lime.state().cards).length") == n0 + 1 and 'GOOD' in await ev("document.querySelector('#toasts').textContent"))
        await ev("document.querySelectorAll('#toasts .toast').forEach(t => t.remove())")
        await pg.mouse.click(5, 5)
        ok('pointer leaves gamepad mode', not await ev("document.documentElement.classList.contains('gp')"))

        # ---- exam ----
        await ev(POOL)
        await ev("location.hash='#exam-py'"); await pg.wait_for_timeout(200)
        await pg.get_by_role('button', name='BEGIN').click(); await pg.wait_for_timeout(150)
        ok('nav hidden in exam', await ev("getComputedStyle(document.querySelector('#nav')).display") == 'none')
        ok('timer role', await ev("document.querySelector('.timer').getAttribute('role')") == 'timer')
        first = await ev("JSON.parse(sessionStorage.getItem('lime.exam')).qs.map(q => q.code)")
        await pg.fill('.pred textarea', 'draft answer')
        await pg.reload(); await pg.wait_for_timeout(400)
        ok('reload resumes the attempt', await ev("document.querySelector('.pred textarea') && document.querySelector('.pred textarea').value") == 'draft answer')
        await ev(POOL)
        # leaving asks
        await ev("location.hash='#cards'"); await pg.wait_for_timeout(150)
        ok('leaving asks to confirm', await ev("!document.querySelector('#modal').hidden && location.hash === '#exam-py'"))
        await pg.get_by_role('button', name='Stay').click(); await pg.wait_for_timeout(100)
        ok('Stay keeps the exam', await ev("!!document.querySelector('.pred textarea')"))
        # warnings
        left_ms = await ev("JSON.parse(sessionStorage.getItem('lime.exam')).end - Date.now()")  # exam length follows the slot count
        await pg.clock.run_for(int(left_ms) - 125 * 1000); await pg.wait_for_timeout(100)
        await pg.clock.run_for(10 * 1000); await pg.wait_for_timeout(50)
        ok('2:00 warning', '2 minutes left' in await ev("document.querySelector('.examwarn').textContent"), await ev("document.querySelector('.timer').textContent"))
        await pg.clock.run_for(92 * 1000); await pg.wait_for_timeout(50)
        ok('0:30 warning', '30 seconds left' in await ev("document.querySelector('.examwarn').textContent"), await ev("document.querySelector('.timer').textContent"))
        # answer all wrong with Ctrl+Enter, before time is up
        await pg.focus('.pred textarea'); await pg.fill('.pred textarea', 'nope'); await pg.keyboard.press('Control+Enter'); await pg.wait_for_timeout(100)
        ok('Ctrl+Enter submits', await ev("JSON.parse(sessionStorage.getItem('lime.exam')).i") == 1)
        await pg.clock.run_for(40 * 1000); await pg.wait_for_timeout(150)
        txt = await ev("document.querySelector('#view').textContent")
        ok('time up -> results, answers hidden on attempt 1', 'NOT YET' in txt and 'Output:' not in txt and 'See lesson' in txt, txt[:200])
        # retake: fresh, no reuse
        await ev("location.hash='#d-py'"); await pg.wait_for_timeout(150)
        await pg.get_by_role('link', name='RETAKE').click(); await pg.wait_for_timeout(150)
        ok('RETAKE starts fresh', await pg.get_by_role('button', name='BEGIN').count() == 1)
        await pg.get_by_role('button', name='BEGIN').click(); await pg.wait_for_timeout(150)
        second = await ev("JSON.parse(sessionStorage.getItem('lime.exam')).qs.map(q => q.code)")
        ok('retake reuses no item where alternatives exist', all(a != b for a, b in zip(first, second)), list(zip(first, second))[:3])
        # pass it -> answers + ending link
        nq = await ev("JSON.parse(sessionStorage.getItem('lime.exam')).qs.length")
        for i in range(nq):
            code = await pg.inner_text('.pred pre.src')
            await pg.fill('.pred textarea', await ev(ANS, code))
            await pg.keyboard.press('Control+Enter') if i else await pg.get_by_role('button', name='NEXT').click()
            await pg.wait_for_timeout(60)
        txt = await ev("document.querySelector('#view').textContent")
        ok('pass shows answers', 'PASSED' in txt and 'Output:' in txt, txt[:120])
        ok('passed exam counted', await ev("__lime.state().exam.py.n") == 2)
        # practice is separate
        await ev("location.hash='#d-py'"); await pg.wait_for_timeout(100)
        await ev("location.hash='#exam-py'"); await pg.wait_for_timeout(150)
        await pg.get_by_role('button', name='UNTIMED PRACTICE').click(); await pg.wait_for_timeout(150)
        ok('practice untimed', await ev("document.querySelector('.timer').textContent") == 'UNTIMED')
        for i in range(nq):
            await pg.fill('.pred textarea', 'x'); await pg.keyboard.press('Control+Enter'); await pg.wait_for_timeout(50)
        st = await ev("__lime.state().exam")
        ok('practice recorded separately', st.get('py~practice', {}).get('n') == 1 and st['py']['n'] == 2 and st['py']['best'] >= 0.75, st)
        ok('citrus chip opens new window (when present)', await ev("[...document.querySelectorAll('#chips a')].filter(a => a.textContent.includes('CITRUS')).every(a => a.target === '_blank')"))
        ok('no page errors', not errs, errs)
        await b.close()
    print('FAILURES:', FAIL)


asyncio.run(main())
