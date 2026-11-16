"""d07: progress, guidance, Home hub, district page, ending guard, re-do levels.
Run from the clone: python3 assemble.py && python3 ui2.py (writes out/page.html) && python3 tests/d07_progress.py"""
import asyncio, datetime, os, re
from playwright.async_api import async_playwright

W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + '/'
P = 'file://' + W + 'lime/out/page.html'
T0 = datetime.datetime(2026, 11, 13, 9, 0, 0)
FAIL = []


def ok(label, cond, info=''):
    print(('PASS ' if cond else 'FAIL ') + label + ('' if cond else '  ' + str(info)))
    if not cond: FAIL.append(label)


# set py01 progress: k predictions right, rest revealed; e exercises; optional teach record
SETP = """(a) => { const [k, e, teach, extra] = a; const S = __lime.blank(); S.seen['py:story'] = 1; const L = __lime.LESSONS[0];
  S.read[L.id] = 1;
  L.predict.forEach((p, i) => S.pred[L.id + ':' + (p.id || 'p' + i)] = i < k ? {ok: true, t: 1} : {ok: false, revealed: true, t: 1});
  L.exercises.slice(0, e).forEach(x => S.done[L.id + ':' + x.id] = {t: Date.now(), n: 1});
  if (teach) S.teach[L.id] = teach;
  Object.assign(S, extra || {});
  __lime.setState(S); return __lime.lp(L); }"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 400, 'height': 800}, has_touch=True)
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W)
        await pg.clock.install(time=T0)
        await pg.goto(P + '#home'); await pg.wait_for_timeout(300)
        ev = pg.evaluate

        async def go(hsh, wait=250):
            await ev("h => { location.hash = h; }", hsh); await pg.wait_for_timeout(wait)

        # ---- Home, first visit ----
        txt = await pg.inner_text('#view')
        ok('home first visit: begin the story', 'BEGIN: ARRIVE IN CALX (2 MIN)' in txt and 'Begin: arrive in Calx (2 min)' in txt, txt[:200])
        ok('home first visit: how Lime works', 'How Lime works' in txt)
        ok('home first visit: no "welcome back"', 'Welcome back' not in txt)
        ok('home first visit: no green OK ticks', await pg.locator('#view .tick.on').count() == 0)
        ok('home: Calx banner first', (await pg.locator('#view .card').first.get_attribute('class')).find('calx') >= 0)

        # ---- lp rules ----
        L = await ev("__lime.LESSONS[0]")
        n_pred = len(L['predict'])
        r = await ev(SETP, [0, 0, None, None])
        ok('lp: revealed predictions do not count', r['pr'] == 0 and r['got'] == 0, r)
        r = await ev(SETP, [2, 0, None, None])
        ok('lp: right predictions count', r['pr'] == 2, r)
        r = await ev(SETP, [0, 0, {'self': 'miss', 'text': 'x', 't': 1, 'stale': 1}, None])
        ok('lp: stale teach-back rating does not count', r['taught'] is False and r['got'] == 0, r)
        r = await ev(SETP, [0, 0, {'self': 'part', 't': 1}, None])
        ok('lp: current rating counts', r['taught'] is True and r['got'] == 1, r)

        # ---- progress strip in plain words, consistent with the district page ----
        r = await ev(SETP, [2, 1, None, None])
        await go('#lesson-py01', 400)
        line = await pg.inner_text('.pstrip .lpline')
        exp = '%d of %d tasks done. %d more opens lesson 2.' % (r['got'], r['tot'], r['left'])
        ok('strip: plain sentence', line == exp, line + ' / ' + exp)
        await pg.locator('.pstrip summary').click()
        ok('strip: breakdown on tap', 'SHOW ANSWER does not count' in await pg.inner_text('.pstrip'))
        nb = pg.locator('#view a.btn.locked')
        ok('next-lesson button locked style while locked', await nb.count() == 1 and 'LOCKED' in await nb.inner_text())
        ok('section menu present', await pg.locator('.secnav button').count() >= 5)
        await go('#d-py')
        ok('district: same counts', exp in await pg.inner_text('#view'))

        # ---- unlock card ----
        r = await ev(SETP, [n_pred, len(L['exercises']), None, None])
        ok('setup: py01 past 60%', r['pct'] >= 0.6, r)
        await go('#lesson-py01', 400)
        ok('lesson: "lesson 2 is open" card', 'LESSON 2 IS OPEN' in await pg.inner_text('#view'))
        ok('next-lesson button unlocked style', await pg.locator('#view a.btn.locked').count() == 0)
        await go('#home')
        ok('home: "lesson 2 is open" card', 'LESSON 2 IS OPEN' in await pg.inner_text('#view'))
        await go('#lesson-py02', 400); await go('#home')
        ok('open card gone once lesson 2 is visited', 'LESSON 2 IS OPEN' not in await pg.inner_text('#view'))

        # ---- lesson resume ----
        await ev(SETP, [2, 1, None, None])
        await go('#lesson-py01', 1100)
        await ev("window.scrollTo(0, 4000)"); await pg.wait_for_timeout(500)
        pos = await ev("JSON.parse(localStorage.getItem('lime.lpos')||'{}').py01")
        ok('resume: position saved', pos and pos['y'] >= 3900, pos)
        await go('#home')
        await pg.locator('#view a.btn', has_text='CONTINUE').first.click(); await pg.wait_for_timeout(500)
        y = await ev("window.scrollY")
        want = await ev("(p) => { const el = [...document.querySelectorAll('[data-anchor]')].find(e => e.getAttribute('data-anchor') === p.a); return Math.round(el.getBoundingClientRect().top + scrollY + p.off); }", pos)
        ok('resume: CONTINUE from Home returns to the saved spot (same content, anchor-relative)', y > 1500 and abs(y - want) < 30, (y, want))
        await go('#map'); await go('#lesson-py01', 400)
        ok('resume bar offered on a plain visit', await pg.locator('.resume').count() == 1)
        await pg.locator('.resume button', has_text='JUMP TO YOUR NEXT TASK').click(); await pg.wait_for_timeout(200)
        top = await ev("""(() => { const el = [...document.querySelectorAll('[data-anchor]')].find(e => e.getAttribute('data-anchor') === 'py01:' + (__lime.LESSONS[0].predict[2].id || 'p2')); return el.getBoundingClientRect().top; })()""")
        ok('jump to next task: first unsolved prediction at top', 0 <= top < 120, top)
        await pg.locator('.secnav button', has_text='PRACTICE').click(); await pg.wait_for_timeout(200)
        top = await ev("""(() => [...document.querySelectorAll('[data-anchor]')].find(e => e.getAttribute('data-anchor') === 'sec-practice').getBoundingClientRect().top)()""")
        ok('section menu jumps to PRACTICE', 0 <= top < 120, top)
        ok('section menu is sticky', abs(await ev("document.querySelector('.secnav').getBoundingClientRect().top")) < 2)

        # ---- district: quest order, replay, story items, meridian ----
        await ev("(() => { const S = __lime.blank(); __lime.setState(S); })()")
        await go('#d-py')
        dt = await pg.inner_text('#view')
        ok('district: no REPLAY before the story is seen', 'REPLAY THE STORY' not in dt)
        ok('district: story items shown without City mode', 'Bench Key' in dt and 'Inspection Stamp' in dt)
        hook = (await ev("__lime.CITY.py01.opener"))[:20]
        ok('district: story hook under lesson title', hook in dt)
        order = await ev("""(() => { const ls = __lime.LESSONS.map(L => L.id); const q = __lime.DIST.py.quests.map((x, i) => [ls.indexOf(x.after), i, x.title]); q.sort((a, b) => a[0] - b[0] || a[1] - b[1]); return q.map(x => x[2]); })()""")
        shown = [t for t in re.findall(r'^(.+)$', dt, re.M) if t in order]
        ok('district: quests sorted by the lesson that opens them', shown == order, (shown, order))
        await ev("""(() => { __lime.DIST.py.meridian = [
            {id: 'm1', lesson: 'py01', title: 'First fragment', code: 'print(77 // 7, 77 % 7)', ans: '11 0', why: 'eleven years'},
            {id: 'm3', lesson: 'py03', title: 'Third fragment', code: 'print(1)', ans: '1', why: 'one'}]; })()""")
        await go('#map'); await go('#d-py')
        dt = await pg.inner_text('#view')
        ok('meridian: open lesson fragment rendered', 'MERIDIAN LOG: FIRST FRAGMENT' in dt)
        ok('meridian: locked lesson fragment gated', 'THIRD FRAGMENT' not in dt and 'Readable once lesson 3' in dt)

        # ---- ending guard ----
        await go('#ending-py')
        ok('ending locked before restore', 'NOT YET' in await pg.inner_text('#view'))
        ok('endingLink null before restore', await ev("__lime.endingLink('py') === null"))

        # ---- re-do levels (page.clock) ----
        await ev("""(() => { const S = __lime.blank(); S.seen['py:story'] = 1; const L = __lime.LESSONS[0];
            const w = L.exercises.find(e => e.kind !== 'fix'), f = L.exercises.find(e => e.kind === 'fix');
            S.done[L.id + ':' + w.id] = {t: Date.now(), n: 1}; if (f) S.done[L.id + ':' + f.id] = {t: Date.now(), n: 1};
            __lime.setState(S); })()""")
        ok('redo: nothing before 3 days', await ev("__lime.redoPick() === null"))
        await pg.clock.fast_forward(73 * 3600000)
        pick = await ev("(() => { const r = __lime.redoPick(); return r && {key: r.key, kind: r.ex.kind || 'write', sol: r.ex.solution}; })()")
        ok('redo: due after 3 days, write-it preferred over fix-it', pick and pick['kind'] != 'fix', pick)
        await go('#home')
        ok('home: "Last solved N days ago"', 'Last solved 3 days ago' in await pg.inner_text('#view'))
        # draft survives a reload within 12 h
        await go('#redo', 400)
        await pg.locator('.ex textarea').fill('# half done')
        await pg.wait_for_timeout(600)
        await pg.reload(); await pg.wait_for_timeout(400)
        ok('redo: draft restored after reload', '# half done' in await pg.locator('.ex textarea').input_value())
        # clean re-do -> level 1 (7 days)
        await pg.locator('.ex textarea').fill(pick['sol'])
        await pg.locator('.ex').get_by_role('button', name='CHECK').click()
        await pg.locator('.ex .win:not([hidden])').wait_for(timeout=60000)
        st = await ev("k => __lime.state().redo[k]", pick['key'])
        ok('redo: clean re-do moves to level 1', st and st.get('lv') == 1 and st.get('v') == 2, st)
        ok('redo: draft cleared after solve', await ev("k => window.__limeEd.drafts()['redo:' + k] == null", pick['key']))
        due_days = await ev("k => Math.round((__lime.redoState(k).due - __lime.redoState(k).at) / 86400000)", pick['key'])
        ok('redo: next interval 7 days', due_days == 7, due_days)
        # level ladder and resets via records
        ladder = await ev("""k => { const S = JSON.parse(JSON.stringify(__lime.state())); const out = [];
            for (const lv of [2, 3, 4]){ S.redo[k] = {v: 2, t: Date.now(), at: Date.now(), lv: lv}; __lime.setState(S); const s = __lime.redoState(k); out.push(s.retired ? 'retired' : Math.round((s.due - s.at) / 86400000)); }
            return out; }""", pick['key'])
        ok('redo: 21, 60 days, then retire', ladder == [21, 60, 'retired'], ladder)
        # hinted re-do resets to 3 days
        await ev("""k => { const S = JSON.parse(JSON.stringify(__lime.state())); S.redo[k] = {v: 2, t: Date.now() - 30 * 86400000, at: Date.now() - 30 * 86400000, lv: 2}; delete S.done[Object.keys(S.done).find(x => x !== k)]; __lime.setState(S); }""", pick['key'])
        await go('#home'); await go('#redo', 400)
        await pg.locator('.ex').get_by_role('button', name='HINT').click()
        await pg.locator('.ex textarea').fill(pick['sol'])
        await pg.locator('.ex').get_by_role('button', name='CHECK').click()
        await pg.locator('.ex .win:not([hidden])').wait_for(timeout=60000)
        st = await ev("k => __lime.state().redo[k]", pick['key'])
        ok('redo: hint resets to level 0 (3 days) and is recorded', st and st.get('lv') == 0 and st.get('hint') == 1, st)
        ok('redo: legacy record reads as level 1', await ev("""k => { const S = JSON.parse(JSON.stringify(__lime.state())); S.redo[k] = {t: Date.now(), n: 1}; __lime.setState(S); return __lime.redoState(k).lv === 1; }""", pick['key']))

        ok('no page errors', not errs, errs)
        await b.close()
    print('FAILED:', FAIL if FAIL else 'none')


asyncio.run(main())
