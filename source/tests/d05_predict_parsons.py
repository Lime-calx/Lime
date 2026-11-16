# d05: predict-the-output, Parsons and teach-back tests.
# Run from the clone:  python3 assemble.py && python3 tests/d05_predict_parsons.py   (writes out/page.html like ui2.py)
import asyncio, os, sys
from playwright.async_api import async_playwright
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = os.path.dirname(L.rstrip('/')) + '/'
P = 'file://' + L + 'out/page.html'
fails = []
def ok(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

# every lesson complete except: py01 predictions, py01 teach-back, py04 Parsons (so those can be exercised from fresh)
SETUP = """() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.pred = {}; S.teach = {}; S.done = {};
  for (const L of __lime.LESSONS){ S.read[L.id]=Date.now(); L.exercises.forEach(e=>S.done[L.id+':'+e.id]={t:1,n:1});
    if (L.id !== 'py01') L.predict.forEach((p,i)=>S.pred[L.id+':'+(p.id||'p'+i)]={ok:true,t:1});
    const C=__lime.CITY[L.id]; C.jobs.forEach(j=>S.done[L.id+':job:'+j.id]={t:1,n:1});
    C.parsons.forEach(p=>{ if (L.id !== 'py04') S.done[L.id+':par:'+p.id]={t:1}; }); C.read.forEach(r=>S.pred[L.id+':read:'+r.id]={ok:true,t:1});
    if (L.id !== 'py01') S.teach[L.id]={self:'full',t:1}; }
  __lime.setState(S); return 1; }"""

async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(L + 'out/lime.html').read()
    open(L + 'out/page.html', 'w').write(html)
    init = "window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W
    async with async_playwright() as p:
        b = await p.chromium.launch()
        errs = []
        ctx = await b.new_context(viewport={'width': 360, 'height': 800})
        pg = await ctx.new_page(); await pg.add_init_script(init)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(P + '#home'); await pg.wait_for_timeout(300)
        await pg.evaluate(SETUP)

        # ---------- 1. checker rules (unit) ----------
        pc = lambda g, a, t=None: pg.evaluate("([g,a,t]) => __lime.predCheck(g,a,t)", [g, a, t])
        r = await pc("‘a’ “b”", "'a' \"b\""); ok(r['ok'] and not r['notes'], 'curly quotes count as straight')
        r = await pc('[("a", 1), ("b", 2)]', "[('a', 1), ('b', 2)]"); ok(r['ok'] and 'single quotes' in r['notes'][0], 'double quotes accepted with the single-quote note')
        r = await pc("[('a',1),('b',2)]", "[('a', 1), ('b', 2)]"); ok(r['ok'] and len(r['notes']) == 1 and 'comma' in r['notes'][0], 'missing spaces after commas accepted with a note')
        r = await pc('{"a":1}', "{'a': 1}"); ok(r['ok'] and len(r['notes']) == 2, 'quotes + colon spacing together: two notes')
        r = await pc('2.5  2', '2.5 2'); ok(r['ok'] and 'exactly one space' in r['notes'][0], 'double space between items accepted with the spacing note')
        traps = {"3, 2, 3.4": "commas msg", "3 2 3": "float msg"}
        r = await pc('3, 2, 3.4', '3 2 3.4', traps); ok(not r['ok'] and r['trap'] == 'commas msg', 'exact trap gives its message')
        r = await pc('3,2,3.4', '3 2 3.4', traps); ok(not r['ok'] and r['trap'] == 'commas msg', 'trap matched in another spacing')
        r = await pc('9 9 9', '3 2 3.4', traps); ok(not r['ok'] and not r['trap'], 'other wrong answer: generic')
        r = await pc('3 2 3.4\r\n\n', '3 2 3.4'); ok(r['ok'] and not r['notes'], 'CRLF / trailing blank lines are exact')

        # ---------- 2. predict UI: traps, RUN IT gating, Ctrl+Enter, attributes ----------
        await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(400)
        bx = pg.locator('.pred:has(textarea)').nth(0); ta = bx.locator('textarea')
        attrs = await ta.evaluate("t => [t.getAttribute('autocorrect'), t.getAttribute('autocomplete'), t.getAttribute('spellcheck'), t.getAttribute('autocapitalize'), t.placeholder]")
        ok(attrs[:4] == ['off', 'off', 'false', 'off'] and len(attrs[4]) <= 30, 'textarea: autocorrect/autocomplete/spellcheck/autocapitalize off, short placeholder %r' % attrs[4])
        ok(not await bx.get_by_role('button', name='RUN IT').is_visible(), 'RUN IT hidden before any attempt')
        await ta.fill('3, 2, 3.4'); await ta.press('Control+Enter'); await pg.wait_for_timeout(150)
        fbt = await bx.locator('.fb').inner_text()
        ok('Not quite' in fbt and 'one space between them' in fbt, 'Ctrl+Enter checks; trap message shown')
        ok(await bx.get_by_role('button', name='RUN IT').is_visible(), 'RUN IT available after one CHECK')
        ok(await bx.locator('.fb').get_attribute('role') == 'status', 'feedback is a live status')
        await ta.fill('3 2  3.4'); await bx.get_by_role('button', name='CHECK').click(); await pg.wait_for_timeout(150)
        fbt = await bx.locator('.fb').inner_text()
        ok('Correct' in fbt and 'exactly one space' in fbt, 'spacing slip accepted with a note')
        ok(await pg.evaluate("__lime.predDone('py01:p0')"), 'predDone true after a right answer')

        # SHOW ANSWER does not count; copying it straight back does not count either
        b2 = pg.locator('.pred:has(textarea)').nth(1)
        await b2.get_by_role('button', name='SHOW ANSWER').click(); await pg.wait_for_timeout(100)
        rec = await pg.evaluate("__lime.state().pred['py01:p1']")
        ok(rec and rec['ok'] is False and rec['revealed'] is True, 'SHOW ANSWER stores {ok:false, revealed:true}')
        ok(await b2.get_by_role('button', name='RUN IT').is_visible(), 'RUN IT available after SHOW ANSWER')
        await b2.locator('textarea').fill('50'); await b2.get_by_role('button', name='CHECK').click(); await pg.wait_for_timeout(100)
        ok(not await pg.evaluate("__lime.predDone('py01:p1')") and 'later visit' in await b2.locator('.fb').inner_text(), 'copying the revealed answer does not count')
        await pg.reload(); await pg.wait_for_timeout(400)
        b2 = pg.locator('.pred:has(textarea)').nth(1)
        ok(not await b2.get_by_role('button', name='RUN IT').is_visible() and 'from memory' in await b2.locator('.fb').inner_text(), 'after reload: answer hidden, RUN IT hidden, retry note')
        await b2.locator('textarea').fill('50'); await b2.get_by_role('button', name='CHECK').click(); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("__lime.predDone('py01:p1')"), 'predicting it on a later visit counts')

        # parsons note: no indented line in py01 -> no "Dots show indentation"
        ok('Dots show indentation' not in await pg.locator('.pz').first.inner_text(), 'py01 Parsons: no dots note (nothing indented)')

        # ---------- 3. long code wraps on a phone ----------
        bad = []
        for lid in ['py05', 'py06', 'py07']:
            await pg.goto(P + '#lesson-' + lid); await pg.wait_for_timeout(350)
            bad += await pg.evaluate("[...document.querySelectorAll('.pred pre.src')].filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.textContent.slice(0, 40))")
            ok(await pg.evaluate("document.documentElement.scrollWidth") <= 360, lid + ': no page overflow')
        ok(not bad, 'prediction code fully visible at 360 px (cut: %s)' % bad[:3])
        ok(await pg.evaluate("document.querySelector('.pred pre.src').getAttribute('role') === 'region'"), 'code block is a labelled region')

        # ---------- 4. Parsons py04 ----------
        await pg.goto(P + '#lesson-py04'); await pg.wait_for_timeout(400)
        pz = pg.locator('.pz').first
        C = await pg.evaluate("__lime.CITY.py04.parsons[0]")
        ok('Dots show indentation' in await pz.inner_text(), 'py04 Parsons: dots note shown')
        await pz.get_by_role('button', name='CHECK ORDER').click(); await pg.wait_for_timeout(100)
        ok('empty' in await pz.locator('.res').inner_text(), 'CHECK with nothing placed shows a message')
        labels = await pz.locator('.zone:not(.ans) .ln').evaluate_all("bs => bs.map(b => b.getAttribute('aria-label'))")
        ok('Add line, indent 2: speed = limit' in labels and 'Add line, indent 2: print(limit)' in labels, 'aria labels carry indentation depth')
        pool = lambda: pz.locator('.zone:not(.ans) .ln')
        async def add(t):
            await pool().filter(has_text=t.strip()).first.focus(); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(60)
        # wrong order: line 2 before line 1, then the decoy
        order = C['lines']
        await add(order[1]);
        ok(await pg.evaluate("document.activeElement.classList.contains('ln') && !document.activeElement.closest('.ans')"), 'focus stays on the next pool line after adding')
        await add(order[0])
        for t in order[2:]: await add(t)
        await add(C['distractors'][0])
        ok(await pg.evaluate("document.activeElement.textContent === 'CHECK ORDER'"), 'pool empty: focus moves to CHECK ORDER')
        await pz.get_by_role('button', name='CHECK ORDER').click(); await pg.wait_for_timeout(150)
        rt = await pz.locator('.res').inner_text()
        ok('decoy' in rt and 'print(limit)' in rt and await pz.locator('.out').is_hidden(), 'decoy rejected before running')
        ok(await pz.locator('.ans .ln.bad').count() == 1, 'decoy line marked')
        # send the decoy back (last answer line)
        await pz.locator('.ans .lrow .ln').last.click(); await pg.wait_for_timeout(60)
        ok(await pg.evaluate("!!document.activeElement.closest('.ans')"), 'focus stays in YOUR PROGRAM after sending a line back')
        # reorder: Alt+Up on line 2 moves it to line 1, focus follows
        l2 = pz.locator('.ans .lrow .ln').nth(1)
        await l2.focus(); await pg.keyboard.press('Alt+ArrowUp'); await pg.wait_for_timeout(60)
        got = await pz.locator('.ans .lrow .ln').evaluate_all("bs => bs.map(b => b.getAttribute('aria-label'))")
        ok(got[0].startswith('Line 1, ' + order[0].strip()), 'Alt+Up reorders')
        ok(await pg.evaluate("document.activeElement.getAttribute('aria-label') || ''") == got[0], 'focus follows the moved line')
        # down button works too, and focus stays on a move button
        await pz.locator('.ans .lrow').nth(0).locator('.mv.dn').click(); await pg.wait_for_timeout(60)
        ok(await pg.evaluate("document.activeElement.classList.contains('mv')"), 'focus stays on the move button')
        await pz.locator('.ans .lrow').nth(1).locator('.mv.up').click(); await pg.wait_for_timeout(60)
        await pz.get_by_role('button', name='CHECK ORDER').click()
        await pg.wait_for_function("document.querySelector('.pz .tag').textContent==='SOLVED'", timeout=60000)
        rec = await pg.evaluate("__lime.state().done['py04:par:p1']")
        ok(rec and rec.get('order') == order, 'solved order stored')
        await pg.reload(); await pg.wait_for_timeout(400)
        shown = await pg.locator('.pz').first.locator('.ans .lrow .ln').count()
        ok(shown == len(order), 'solved order shown after reload')
        lw = await pg.evaluate("[...document.querySelectorAll('.pz .ln')].filter(b => b.scrollWidth > b.clientWidth + 1).length")
        ok(lw == 0, 'Parsons lines wrap at 360 px')

        # ---------- 5. teach-back ----------
        await pg.goto(P + '#lesson-py01'); await pg.wait_for_timeout(400)
        tb = pg.locator('.teach'); tta = tb.locator('textarea'); cmp = tb.get_by_role('button', name='COMPARE WITH A MODEL')
        await tta.fill(' '.join(['a'] * 30)); ok(await cmp.is_disabled(), '30 copies of one word: compare locked')
        txt = 'slash divides exactly giving a float while double slash rounds down to whole bags and percent gives the leftover coins'
        await tta.fill(txt); ok(not await cmp.is_disabled(), '15+ distinct words: compare open')
        await cmp.click(); await pg.wait_for_timeout(100)
        cbs = tb.locator('.tpoints input[type=checkbox]')
        ok(await cbs.count() >= 3, 'key points checklist shown after compare')
        full = tb.get_by_role('button', name='I COVERED IT ALL')
        ok(await full.is_disabled(), 'I COVERED IT ALL locked until every point ticked')
        n = await cbs.count()
        for i in range(n - 1): await cbs.nth(i).check()
        ok(await full.is_disabled(), 'still locked with one point unticked')
        await cbs.nth(n - 1).check(); ok(not await full.is_disabled(), 'unlocked when all ticked')
        await full.click(); await pg.wait_for_timeout(100)
        ok(await pg.evaluate("__lime.state().teach.py01.self") == 'full' and await pg.evaluate("__lime.lp(__lime.LESSONS[0]).taught"), 'rated full and counted')
        await cbs.nth(0).uncheck(); await pg.wait_for_timeout(50)
        ok(await pg.evaluate("__lime.state().teach.py01.self") == 'part', 'unticking a point downgrades full to partly')
        await tta.fill('too short now'); await pg.wait_for_timeout(50)
        ok(await pg.evaluate("__lime.state().teach.py01.self") == '' and not await pg.evaluate("__lime.lp(__lime.LESSONS[0]).taught"), 'text below the gate: rating stale, not counted')
        await pg.reload(); await pg.wait_for_timeout(400)
        ok('no longer counts' in await pg.locator('.teach').inner_text(), 'stale note survives reload')
        await pg.locator('.teach textarea').fill(txt); await pg.locator('.teach').get_by_role('button', name='COMPARE WITH A MODEL').click()
        await pg.locator('.teach').get_by_role('button', name='PARTLY').click(); await pg.wait_for_timeout(50)
        ok(await pg.evaluate("__lime.state().teach.py01.self") == 'part' and await pg.evaluate("__lime.lp(__lime.LESSONS[0]).taught"), 're-rated: counts again')

        ok(not errs, 'no page errors %s' % errs[:3])
        await b.close()
    print('FAILS:', fails if fails else 'none')
    sys.exit(1 if fails else 0)

asyncio.run(main())
