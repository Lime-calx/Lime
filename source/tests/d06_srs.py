"""d06: flashcards and spaced repetition. Run from the clone: python3 assemble.py && python3 ui2.py (writes out/page.html) && python3 tests/d06_srs.py
Uses page.clock to simulate 3 days in a row, a 14-day gap and a 20-day gap with 75 overdue cards,
plus touch swipes vs scrolling, undo, again-requeue, new-card gating and the scheduler rules."""
import asyncio, datetime, json, os, sys
from playwright.async_api import async_playwright

W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
P = 'file://' + W + 'lime/out/page.html'
T0 = datetime.datetime(2026, 11, 13, 9, 0, 0)
FAIL = []


def ok(label, cond, info=''):
    print(('PASS ' if cond else 'FAIL ') + label + ('' if cond else '  ' + str(info)))
    if not cond: FAIL.append(label)


# progress helper: mark lessons [0..n) fully done, lesson n optionally partly
PROGRESS = """(args) => { const [n, partial] = args; const S = JSON.parse(JSON.stringify(__lime.state()));
  __lime.LESSONS.forEach((L, i) => { if (i > n) return; S.read[L.id] = 1;
    const exs = i < n ? L.exercises : L.exercises.slice(0, Math.round(L.exercises.length * partial));
    exs.forEach(e => S.done[L.id + ':' + e.id] = {t: 1, n: 1});
    const pr = i < n ? L.predict : L.predict.slice(0, Math.round(L.predict.length * partial));
    pr.forEach((p, j) => S.pred[L.id + ':' + (p.id || 'p' + j)] = {ok: true, t: 1});
    if (i < n){ const C = __lime.CITY[L.id]; C.jobs.forEach(j => S.done[L.id + ':job:' + j.id] = {t: 1, n: 1}); C.parsons.forEach(p => S.done[L.id + ':par:' + p.id] = {t: 1});
      C.read.forEach(r => S.pred[L.id + ':read:' + r.id] = {ok: true, t: 1}); S.teach[L.id] = {self: 'full', t: 1}; } });
  __lime.setState(S); return __lime.LESSONS.map(L => Math.round(100 * __lime.lp(L).pct)); }"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 400, 'height': 740}, has_touch=True)
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W)
        await pg.clock.install(time=T0)
        await pg.goto(P + '#home'); await pg.wait_for_timeout(300)
        ev = pg.evaluate

        async def day(n, hour=9):
            await pg.clock.set_system_time(T0 + datetime.timedelta(days=n, hours=hour - 9))
            await ev("location.hash = '#home'"); await ev("location.hash = '#cards'"); await pg.wait_for_timeout(60)

        async def view(): return (await pg.inner_text('#view')).replace('\n', ' | ')

        async def review_all(key='3', limit=200):
            n = 0
            while n < limit and await pg.locator('.fcard').count():
                await pg.keyboard.press('Enter'); await pg.keyboard.press(key); n += 1
            return n

        # ---------- scheduler unit rules ----------
        r = await ev("""() => { const s = __lime.schedule; const t = 100;
          const n = s(null, 2, t, true);                       // new, Good -> 2d, first = t
          const a1 = s(n, 0, t, true);                         // Again on first day: no ease penalty
          const rev = {ease: 2.5, ivl: 10, reps: 3, lapses: 0, due: 100, last: 1, first: 50};
          const f1 = s(rev, 0, t, true), f2 = s(f1, 0, t, true), f3 = s(f2, 0, t, true);   // 3 Agains same day
          const h1 = s(Object.assign({}, rev), 1, t, true);
          const h2 = s(Object.assign({}, h1, {due: t}), 1, t, true);                      // Hard twice same day
          const g = s({ease: 2.0, ivl: 10, reps: 3, lapses: 1, due: 100, last: 1}, 2, t, true);
          const gTop = s({ease: 2.48, ivl: 10, reps: 3, lapses: 1, due: 100, last: 1}, 2, t, true);
          const late0 = s({ease: 2.5, ivl: 2, reps: 1, lapses: 0, due: 3, last: 1}, 2, 3, true);
          const late13 = s({ease: 2.5, ivl: 2, reps: 1, lapses: 0, due: 3, last: 1}, 2, 16, true);
          const fz = []; for (let i = 0; i < 200; i++) fz.push(s({ease: 2.5, ivl: 20, reps: 3, lapses: 0, due: 100, last: 1}, 2, 100).ivl);
          const small = []; for (let i = 0; i < 50; i++) small.push(s({ease: 2.5, ivl: 1, reps: 1, lapses: 0, due: 100, last: 1}, 1, 100).ivl);
          const pass = s(f1, 2, t, true);                      // relearn pass the same day
          return {n, a1, f1e: f1.ease, f3e: f3.ease, f3l: f3.lapses, h2e: h2.ease, ge: g.ease, gTop: gTop.ease, late0: late0.ivl, late13: late13.ivl,
            fmin: Math.min(...fz), fmax: Math.max(...fz), small: [...new Set(small)], pass: pass.ivl, passLrn: pass.lrn,
            lbNew: __lime.ivlLabel(null, 0, t), lbRev: __lime.ivlLabel(rev, 0, t), keys: Object.keys(f1).sort() }; }""")
        ok('new card stores first day', r['n']['first'] == 100 and r['n']['ivl'] == 2, r['n'])
        ok('no ease penalty on first day', r['a1']['ease'] == 2.5, r['a1'])
        ok('ease penalty and lapse once per day (3 Agains)', abs(r['f1e'] - 2.3) < 1e-9 and abs(r['f3e'] - 2.3) < 1e-9 and r['f3l'] == 1, r)
        ok('Hard penalty once per day', abs(r['h2e'] - 2.35) < 1e-9, r['h2e'])
        ok('Good restores +0.05 up to 2.5', abs(r['ge'] - 2.05) < 1e-9 and r['gTop'] == 2.5, (r['ge'], r['gTop']))
        ok('late-review credit (13 days late beats on-time)', r['late13'] > 13 and r['late0'] == 5, (r['late0'], r['late13']))
        ok('fuzz within +-5% (min +-1d) for ivl>=3', 47 <= r['fmin'] < r['fmax'] <= 53, (r['fmin'], r['fmax']))
        ok('no fuzz below 3 days', r['small'] == [2], r['small'])
        ok('relearn pass same day -> 1d, learning cleared', r['pass'] == 1 and r['passLrn'] is None, r)
        ok('Again labels <1m / 1d', r['lbNew'] == '<1m' and r['lbRev'] == '1d', (r['lbNew'], r['lbRev']))
        ok('state shape kept (fields only added)', all(k in r['keys'] for k in ['ease', 'ivl', 'reps', 'lapses', 'due', 'last']), r['keys'])

        # ---------- new-card gating ----------
        await ev("__lime.setState({})")
        pct = await ev(PROGRESS, [0, 0.3])
        n0 = await ev("__lime.cardList().length")
        ok('opened lesson below 60% unlocks no cards', n0 == 0, (pct, n0))
        pct = await ev(PROGRESS, [0, 1.0])
        ids = await ev("__lime.cardList().map(c => c.id)")
        ok('lesson at 60% unlocks only its cards', pct[0] >= 60 and ids and all(i.startswith('py01:') for i in ids), (pct, ids[:3]))
        pct = await ev(PROGRESS, [2, 0])
        await day(0)
        await pg.get_by_role('button', name='START REVIEW').click()
        q = await ev("() => { const L = __lime.LESSONS; return null; }")
        first_ids = []
        for i in range(3):
            first_ids.append(await pg.inner_text('.fcard .q'))
            await pg.keyboard.press('Enter')
            lt = await pg.inner_text('.fcard .a .side')
            first_ids[-1] = lt
            await pg.keyboard.press('3')
        ok('new cards come in lesson order', all('LESSON 1:' in x for x in first_ids), first_ids)
        front = await pg.inner_text('.fcard .side')
        ok('lesson title hidden on the front', 'LESSON' not in front and 'PROGRAMS' not in front.upper(), front)
        await pg.keyboard.press('Escape')
        await ev("() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.cards = {}; S.days = {}; __lime.setState(S); }")

        # glossary rules
        g = await ev("""() => { const C = __lime.CITY; const t0 = C.py01.terms[0], t1 = C.py01.terms[1];
            const save = [t0.card, t1.q];
            t0.card = false; t1.q = 'When is an expression shown?';
            const L = __lime.cardList(); const ids = L.map(c => c.id);
            const out = {noT0: !ids.includes('py01:t0'), q: (L.find(c => c.id === 'py01:t1') || {}).f};
            t0.card = save[0]; if (save[1] === undefined) delete t1.q; else t1.q = save[1];
            return out; }""")
        ok('term card=False skipped', g['noT0'], g)
        g = await ev("""() => { const T = __lime.termCard;
            return {q: T({term: 'x', def: 'd', q: 'When is an expression shown?'}),
                    sort: T({term: 'sort vs sorted', def: 'd', mistake: '`a = a.sort()` sets `a` to None.'}),
                    fix: T({term: 'KeyError', def: 'd', mistake: 'Fix it with dict.get(key, default).'}),
                    alias: T({term: 'alias', def: 'd', mistake: 'Expecting a copy.'})}; }""")
        ok('term q used as the front', g['q']['f'] == 'When is an expression shown?', g['q'])
        ok('mistake confronted on the front (code)', g['sort']['f'] == 'What is wrong with `a = a.sort()`?' and 'The mistake:' in g['sort']['b'], g['sort'])
        ok('a "fix" in the mistake slot is not used as a front', 'wrong' not in g['fix']['f'] and 'Common mistake:' in g['fix']['b'], g['fix'])
        ok('action mistake confronted', 'Expecting a copy' in g['alias']['f'], g['alias'])

        # ---------- 3 days in a row, then a 14-day gap ----------
        await ev("() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.cards = {}; S.days = {}; __lime.setState(S); }")
        await ev(PROGRESS, [2, 0])  # lessons 1-2 done, 3 open: ~37 cards
        news = []
        for d in range(3):
            await day(d)
            plan = await ev("__lime.reviewPlan()")
            news.append(plan['newToday'])
            if await pg.get_by_role('button', name='START REVIEW').count():
                await pg.get_by_role('button', name='START REVIEW').click()
                await review_all('3')
        ok('3 days in a row: 8 new cards each day', news == [8, 8, 8], news)
        await day(3)
        plan = await ev("__lime.reviewPlan()")
        ok('day 4 after 3 study days: still 8 new', plan['newToday'] == 8, plan)
        await day(17)
        plan = await ev("__lime.reviewPlan()")
        ok('14-day gap: no new cards, says why', plan['newToday'] == 0 and plan['reason'] in ('away', 'backlog') and plan['away'] == 15 and 'away' in plan['note'] + 'overdue', plan)
        ok('14-day gap: lower first-day cap', plan['cap'] == 30 and plan['due'] == min(30, plan['waiting']), plan)
        txt = await view()
        ok('cards page states the real numbers', str(plan['due']) + ' due' in txt and 'No new cards today' in txt, txt[:300])
        before = await ev("JSON.parse(JSON.stringify(__lime.state().cards))")
        await pg.get_by_role('button', name='START REVIEW').click()
        await review_all('3')
        after = await ev("__lime.state().cards")
        tnow = await ev("Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000)")
        late = [(k, before[k]['ivl'], after[k]['ivl']) for k in before if before[k]['due'] <= tnow - 13 and after[k]['last'] != before[k]['last']]
        ok('late reviews after the gap get credit (ivl 2 -> >= 13)', late and all(a >= 12 for k, bf, a in late if bf == 2), late[:4])
        txt = await view()
        ok('session summary with next reviews dd/mm/yyyy', 'SESSION COMPLETE' in txt and 'Next reviews:' in txt and '/2026' in txt, txt[:300])

        # ---------- 20-day gap with 75 overdue ----------
        await ev(PROGRESS, [7, 1])  # every lesson open, so 75 cards exist whatever the per-lesson counts
        await ev("""() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.cards = {}; S.days = {};
            const now = Date.now(), t = Math.floor((now - new Date().getTimezoneOffset() * 60000) / 86400000);
            const ids = __lime.cardList().map(c => c.id).slice(0, 75);
            ids.forEach((id, i) => S.cards[id] = {ease: 2.5, ivl: 4, reps: 2, lapses: 0, due: t - 18 + (i % 5), last: now - 20 * 86400000, first: t - 25});
            const d = new Date(now - 20 * 86400000); const k = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
            S.days[k] = {xp: 30, cards: 20}; __lime.setState(S); return ids.length; }""")
        await day(17, 10)
        plan = await ev("__lime.reviewPlan()")
        ok('20-day gap, 75 overdue: no new cards, capped at 30', plan['waiting'] == 75 and plan['newToday'] == 0 and plan['due'] == 30 and plan['reason'] == 'backlog', plan)
        ok('note gives real numbers', '75 reviews are overdue' in plan['note'] and '30' in plan['note'], plan['note'])
        await pg.get_by_role('button', name='START REVIEW').click()
        n = await review_all('3')
        plan2 = await ev("__lime.reviewPlan()")
        ok('cap is enforced across sessions the same day', n == 30 and plan2['due'] == 0 and plan2['shownToday'] == 30, (n, plan2))

        # ---------- again-requeue ----------
        await ev("""() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.cards = {}; S.days = {};
            const t = Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000);
            S.set.newPerDay = 0; const ids = __lime.cardList().map(c => c.id);
            S.cards[ids[0]] = {ease: 2.5, ivl: 5, reps: 3, lapses: 0, due: t, last: Date.now() - 5 * 86400000, first: t - 9}; __lime.setState(S); }""")
        await day(17, 12)
        await pg.get_by_role('button', name='START REVIEW').click()
        q1 = await pg.inner_text('.fcard .q')
        await pg.keyboard.press('Enter'); await pg.keyboard.press('1'); await pg.wait_for_timeout(50)
        txt = await view()
        ok('failed card is held when the queue is short', '1 card returns in 60 s' in txt and await pg.locator('.fcard').count() == 0, txt[:200])
        await pg.clock.run_for(61000); await pg.wait_for_timeout(50)
        ok('held card returns after about 60 s', await pg.locator('.fcard').count() == 1 and await pg.inner_text('.fcard .q') == q1)
        await pg.keyboard.press('Enter'); await pg.keyboard.press('3')
        await ev("""() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.cards = {}; S.days = {};
            const t = Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000);
            __lime.cardList().map(c => c.id).slice(0, 10).forEach(id => S.cards[id] = {ease: 2.5, ivl: 5, reps: 3, lapses: 0, due: t, last: Date.now() - 5 * 86400000, first: t - 9}); __lime.setState(S); }""")
        await ev("location.hash = '#home'"); await ev("location.hash = '#cards'")
        await pg.get_by_role('button', name='START REVIEW').click()
        q1 = await pg.inner_text('.fcard .q')
        await pg.keyboard.press('Enter'); await pg.keyboard.press('1')
        seen = []
        for i in range(6):
            seen.append(await pg.inner_text('.fcard .q'))
            await pg.keyboard.press('Enter'); await pg.keyboard.press('3')
        ok('failed card returns 5 cards later', q1 not in seen[:5] and seen[5] == q1, seen)
        await pg.keyboard.press('Escape')

        # ---------- undo ----------
        await ev("""() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.cards = {}; S.days = {}; S.set.newPerDay = 8; __lime.setState(S); }""")
        await ev("location.hash = '#home'"); await ev("location.hash = '#cards'")
        await pg.get_by_role('button', name='START REVIEW').click()
        await pg.keyboard.press('Enter'); await pg.keyboard.press('3')
        q2 = await pg.inner_text('.fcard .q')
        await pg.keyboard.press('Enter'); await pg.keyboard.press('4')
        st1 = await ev("() => ({n: Object.keys(__lime.state().cards).length, d: JSON.stringify(Object.values(__lime.state().days)[0])})")
        t = await pg.inner_text('#toasts')
        ok('rating toast with UNDO', 'Rated EASY.' in t and 'UNDO' in t, t)
        await pg.get_by_role('button', name='UNDO').click()
        st2 = await ev("() => ({n: Object.keys(__lime.state().cards).length, d: Object.values(__lime.state().days)[0]})")
        ok('undo restores card state and day counters', st1['n'] == 2 and st2['n'] == 1 and st2['d']['newc'] == 1 and st2['d']['cards'] == 1, (st1, st2))
        ok('undo restores queue position (same card, answer shown)', await pg.inner_text('.fcard .q') == q2 and await pg.locator('.rate .good').is_visible())
        ok('focus is on the card after undo/rating', await ev("document.activeElement.classList.contains('fcard')"))
        await pg.keyboard.press('3')
        await pg.wait_for_timeout(50)
        await pg.clock.run_for(4100)
        ok('undo toast disappears after 4 s', await pg.locator('.toast.undo').count() == 0)

        # ---------- a11y ----------
        role = await ev("() => { const f = document.querySelector('.fcard'); return [f.tagName, f.getAttribute('role'), f.getAttribute('aria-label')]; }")
        ok('card is a section, not role=button', role[0] == 'SECTION' and role[1] is None, role)
        await pg.get_by_role('button', name='SHOW ANSWER').click()
        live = await ev("document.querySelector('.fcard .ans').getAttribute('aria-live')")
        ok('answer announced (live region)', live == 'polite' and 'ANSWER' in await pg.inner_text('.fcard .ans'))

        # ---------- touch: scroll never rates, horizontal swipe does ----------
        cdp = await ctx.new_cdp_session(pg)

        async def drag(dx, dy, steps=8):
            box = await pg.locator('.fcard').bounding_box()
            x0, y0 = box['x'] + box['width'] / 2, box['y'] + min(box['height'] / 2, 150)
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x0, 'y': y0}]})
            for i in range(1, steps + 1):
                await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x0 + dx * i / steps, 'y': y0 + dy * i / steps}]})
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
            await pg.wait_for_timeout(80)

        ncards = lambda: ev("Object.keys(__lime.state().cards).length")
        c0 = await ncards(); qa = await pg.inner_text('.fcard .q')
        await drag(0, -160); await drag(0, 160)
        ok('vertical drags on a flipped card do not rate', await ncards() == c0 and await pg.inner_text('.fcard .q') == qa)
        await drag(120, 80)
        ok('diagonal drag (|dx| < 2|dy|) does not rate', await ncards() == c0)
        await drag(70, 0)
        ok('short horizontal drag (< 100 px) does not rate', await ncards() == c0)
        await drag(160, 10)
        ok('horizontal swipe right rates Good', await ncards() == c0 + 1 and 'Rated GOOD' in await pg.inner_text('#toasts'))
        await drag(-160, 0)
        ok('horizontal swipe on the front flips it', await pg.locator('.rate .good').is_visible())

        # ---------- keyboard: Space = Good setting, Escape ends ----------
        await ev("() => { __lime.state().set.spaceGood = true; }")
        c1 = await ncards()
        await pg.keyboard.press('Space')
        ok('Space = Good after flip (setting on)', await ncards() == c1 + 1)
        await pg.keyboard.press('Escape')
        txt = await view()
        ok('Escape ends the session with a summary', 'SESSION ENDED' in txt and 'Next reviews:' in txt, txt[:200])
        ok('no page errors', not errs, errs)
        await b.close()
    print('FAILED:', FAIL if FAIL else 'none')
    sys.exit(1 if FAIL else 0)

asyncio.run(main())
