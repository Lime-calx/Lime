# d15: local state, backup/reset and artifact cloud sync in a real browser.
# Run from the clone after `python3 assemble.py`:  python3 tests/d15_state.py
import asyncio, json, os, sys
from playwright.async_api import async_playwright

LIME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.dirname(LIME) + '/'
P = 'file://' + LIME + '/out/page.html'
BRY = "window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W
fails = []
def check(name, ok, info=''):
    print(('ok   ' if ok else 'FAIL ') + name + ('' if ok else '  ' + str(info)[:400]))
    if not ok: fails.append(name)

# Storage that can be made to fail: window.__quota = 'all' (every write throws) or 'big' (writes over 2 kB throw)
QUOTA = """
(() => { const real = Storage.prototype.setItem;
  Storage.prototype.setItem = function(k, v){
    const q = window.__quota || sessionStorage.getItem('quota');
    if (q === 'all' || (q === 'big' && String(v).length > 2000)) { const e = new Error('QuotaExceededError'); e.name = 'QuotaExceededError'; throw e; }
    return real.call(this, k, v);
  };
  window.__removed = []; const rr = Storage.prototype.removeItem;
  Storage.prototype.removeItem = function(k){ window.__removed.push(k); return rr.call(this, k); };
})();
"""

def state_with(n_done, n_cards, epoch=0):
    s = {'v': 2, 'epoch': epoch, 'updatedAt': 1, 'done': {}, 'cards': {}, 'days': {'2026-11-12': {'xp': 50, 'ex': n_done}}}
    for i in range(n_done): s['done']['py01:e%d' % i] = {'t': 1000 + i, 'n': 1}
    for i in range(n_cards): s['cards']['py01:c%d' % i] = {'ease': 2.5, 'ivl': 3, 'reps': 1, 'lapses': 0, 'due': 99999, 'last': 1000 + i}
    return s

async def toast_text(pg):
    return ' | '.join(await pg.locator('#toasts .toast').all_inner_texts())

async def new_page(b, init=''):
    ctx = await b.new_context(viewport={'width': 400, 'height': 860}, service_workers='block')
    await ctx.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    await ctx.add_init_script(BRY + init)
    pg = await ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    return ctx, pg

async def t_quota(b):
    # 1. storage blocked from the start: the boot probe shows the banner
    ctx, pg = await new_page(b, QUOTA + "sessionStorage.setItem('quota','all');")
    await pg.goto(P + '#home'); await pg.wait_for_timeout(300)
    t = await pg.locator('#banner-storage').inner_text() if await pg.locator('#banner-storage').count() else ''
    check('boot probe: banner when storage is blocked', "can't save on this device" in t and 'Copy a backup from Me' in t, t)
    await ctx.close()
    # 2. storage fills up later: first failing save shows the banner, lime.drafts is dropped and retried
    ctx, pg = await new_page(b, QUOTA)
    await pg.goto(P + '#me'); await pg.wait_for_timeout(300)
    check('no banner while storage works', await pg.locator('#banner-storage').count() == 0)
    await pg.evaluate("localStorage.setItem('lime.drafts', JSON.stringify({x:'y'.repeat(50)})); window.__quota='big'")
    await pg.evaluate("(s) => __lime.setState(s)", state_with(60, 0))
    await pg.wait_for_timeout(100)
    check('banner when a save fails', await pg.locator('#banner-storage').is_visible())
    check('lime.drafts dropped before retrying', 'lime.drafts' in await pg.evaluate('window.__removed'))
    check('Me says it is not saving', 'not saving progress right now' in await pg.inner_text('#view'))
    # storage recovers: the next save clears the banner
    await pg.evaluate("window.__quota=''; (s => __lime.setState(s))(__lime.state())")
    await pg.wait_for_timeout(100)
    check('banner goes when saving works again', await pg.locator('#banner-storage').count() == 0)
    check('no page errors (quota)', not pg.errs, pg.errs)
    await ctx.close()

async def t_corrupt(b):
    bad = json.dumps(state_with(5, 2))[:-40]   # truncated JSON
    ctx, pg = await new_page(b, "if (!sessionStorage.getItem('seeded')){ sessionStorage.setItem('seeded','1'); localStorage.setItem('lime.v1', %s); }" % json.dumps(bad))
    await pg.goto(P + '#me'); await pg.wait_for_timeout(300)
    check('corrupt: banner shown', await pg.locator('#banner-corrupt').is_visible())
    keys = await pg.evaluate("Object.keys(localStorage).filter(k => k.indexOf('lime.v1.corrupt-') === 0)")
    check('corrupt: raw text copied aside', len(keys) == 1 and await pg.evaluate("(k) => localStorage.getItem(k)", keys[0]) == bad, keys)
    # a local save while held must not overwrite lime.v1
    await pg.get_by_role('button', name='DARK').click(); await pg.wait_for_timeout(100)
    check('corrupt: lime.v1 not overwritten by a save', await pg.evaluate("localStorage.getItem('lime.v1')") == bad)
    await pg.get_by_role('button', name='START FRESH AND SAVE').click(); await pg.wait_for_timeout(100)
    await pg.locator('.dlg').get_by_role('button', name='Start fresh').click(); await pg.wait_for_timeout(100)
    ok = await pg.evaluate("(() => { try { return JSON.parse(localStorage.getItem('lime.v1')).set.theme === 'dark'; } catch(e){ return false; } })()")
    check('corrupt: START FRESH saves again', ok and await pg.locator('#banner-corrupt').count() == 0)
    check('no page errors (corrupt)', not pg.errs, pg.errs)
    await ctx.close()

async def t_backup_after_reset(b):
    ctx, pg = await new_page(b)
    await pg.goto(P + '#me'); await pg.wait_for_timeout(200)
    await pg.evaluate("(s) => __lime.setState(s)", state_with(24, 18))
    backup = await pg.evaluate("JSON.stringify(__lime.state())")
    await pg.get_by_role('button', name='RESET PROGRESS').click(); await pg.wait_for_timeout(100)
    await pg.locator('.dlg').get_by_role('button', name='Reset everything').click(); await pg.wait_for_timeout(200)
    check('reset cleared progress', await pg.evaluate("Object.keys(__lime.state().done).length") == 0)
    check('reset kept lime.v1.before-reset', len(json.loads(await pg.evaluate("localStorage.getItem('lime.v1.before-reset')"))['done']) == 24)
    check('UNDO RESET offered', await pg.get_by_role('button', name='UNDO RESET').count() == 1)
    # paste the pre-reset backup and merge
    await pg.fill('textarea.paste', backup)
    await pg.get_by_role('button', name='MERGE').click(); await pg.wait_for_timeout(150)
    dlg = await pg.locator('.dlg').inner_text() if await pg.locator('.dlg').count() else ''
    import datetime; today = datetime.date.today().strftime('%d/%m/%Y')
    check('asks to restore a pre-reset backup', ('Restore your backup from before the %s reset?' % today) in dlg, dlg)
    await pg.get_by_role('button', name='Restore it').click(); await pg.wait_for_timeout(150)
    t = await toast_text(pg)
    check('merge says exactly what merged', 'Merged: 24 solved items, 18 cards' in t, t)
    check('backup restored after reset', await pg.evaluate("Object.keys(__lime.state().done).length") == 24)
    await pg.fill('textarea.paste', backup)
    await pg.get_by_role('button', name='MERGE').click(); await pg.wait_for_timeout(150)
    if await pg.locator('.dlg').count(): await pg.get_by_role('button', name='Restore it').click(); await pg.wait_for_timeout(150)
    t = await toast_text(pg)
    check('never "Merged." when nothing changed', 'Nothing to merge' in t and 'Merged.' not in t, t)
    # a Drive state.json ({app, v, state:{...}}) is unwrapped
    wrapped = {'app': 'lime', 'v': 2, 'updatedAt': '2026-11-13T08:00:00Z', 'state': state_with(26, 0)}
    await pg.fill('textarea.paste', json.dumps(wrapped))
    await pg.get_by_role('button', name='MERGE').click(); await pg.wait_for_timeout(150)
    if await pg.locator('.dlg').count(): await pg.get_by_role('button', name='Restore it').click(); await pg.wait_for_timeout(150)
    t = await toast_text(pg)
    check('state.json accepted', 'Merged: 2 solved items' in t, t)
    # undo the reset in a fresh reset: UNDO brings everything back
    await pg.get_by_role('button', name='RESET PROGRESS').click(); await pg.wait_for_timeout(100)
    await pg.locator('.dlg').get_by_role('button', name='Reset everything').click(); await pg.wait_for_timeout(150)
    await pg.get_by_role('button', name='UNDO RESET').click(); await pg.wait_for_timeout(150)
    check('UNDO RESET restores', await pg.evaluate("Object.keys(__lime.state().done).length") == 26)
    check('no page errors (backup)', not pg.errs, pg.errs)
    await ctx.close()

# two devices on a stubbed window.claude.use('db'): local echo with hasPendingWrites, then the server snapshot to everyone
STUB = """
window.__snapCbs = [];
window.__cloudEmit = (doc, pending) => { const snap = {exists: !!doc, data: () => doc && JSON.parse(JSON.stringify(doc)), metadata: {fromCache: false, hasPendingWrites: !!pending}}; window.__snapCbs.forEach(cb => cb(snap)); };
window.claude = { use: async (what) => {
  if (what === 'user') return { id: async () => 'user-1' };
  if (what === 'db') return { doc: (path) => ({
     onSnapshot: (cb, err) => { window.__snapCbs.push(cb); window.__cloudSubscribe(path); return () => {}; },
     set: async (data) => { window.__cloudEmit(data, true); await window.__cloudSet(path, JSON.stringify(data)); }
  }) };
} };
"""
async def t_cloud(b):
    store = {'doc': None}; pages = []; sets = {}
    async def emit_all():
        for pg in pages:
            try: await pg.evaluate('(d) => window.__cloudEmit(d, false)', store['doc'])
            except Exception: pass
    async def device(name, theme, n):
        ctx = await b.new_context(viewport={'width': 400, 'height': 860}, service_workers='block')
        await ctx.route('**/fonts.googleapis.com/**', lambda r: r.abort())
        sets[name] = 0
        async def cset(source, path, data):
            sets[name] += 1; store['doc'] = json.loads(data)
            asyncio.get_event_loop().call_later(0.05, lambda: asyncio.ensure_future(emit_all()))
        async def csub(source, path):
            pg = source['page']
            asyncio.get_event_loop().call_later(0.05, lambda: asyncio.ensure_future(pg.evaluate('(d) => window.__cloudEmit(d, false)', store['doc'])))
        await ctx.expose_binding('__cloudSet', cset); await ctx.expose_binding('__cloudSubscribe', csub)
        st = {'v': 2, 'epoch': 0, 'updatedAt': 1, 'done': {('w:%s:%d' % (name, i)): {'t': 1 + i} for i in range(n)}, 'set': {'theme': theme}}
        await ctx.add_init_script(BRY + STUB + "if (!sessionStorage.getItem('seeded')){ sessionStorage.setItem('seeded','1'); localStorage.setItem('lime.v1', %s); }" % json.dumps(json.dumps(st)))
        pg = await ctx.new_page(); pg.errs = []; pg.on('pageerror', lambda e: pg.errs.append(str(e)))
        pages.append(pg)
        await pg.goto(P + '#home'); await pg.wait_for_timeout(600)
        return pg
    A = await device('A', 'dark', 3)
    B = await device('B', 'light', 2)
    await asyncio.sleep(3.5); s1 = dict(sets)
    await asyncio.sleep(5.0); s2 = dict(sets)
    idle = s2['A'] - s1['A'] + s2['B'] - s1['B']
    print('   cloud writes: total %s, while idle 5 s: %d' % (s2, idle))
    check('two devices with different themes go quiet', idle == 0, s2)
    check('few writes to converge', s2['A'] + s2['B'] <= 4, s2)
    da = sorted(await A.evaluate("Object.keys(__lime.state().done)")); db = sorted(await B.evaluate("Object.keys(__lime.state().done)"))
    check('both devices converged', da == db and len(da) == 5, (da, db))
    check('themes stay local', await A.evaluate("__lime.state().set.theme") == 'dark' and await B.evaluate("__lime.state().set.theme") == 'light')
    check('device id not pushed', 'devId' not in (store['doc'] or {}).get('state', {}))
    # a theme change alone writes nothing
    await B.goto(P + '#me'); await B.wait_for_timeout(200)
    s3 = dict(sets); await B.get_by_role('button', name='DARK').click(); await asyncio.sleep(2.5)
    check('a settings change does not write to the cloud', sets['B'] == s3['B'], sets)
    # a reset on A arrives at B: B keeps its own copy and offers to keep it
    await A.goto(P + '#me'); await A.wait_for_timeout(200)
    await A.get_by_role('button', name='RESET PROGRESS').click(); await A.wait_for_timeout(100)
    await A.locator('.dlg').get_by_role('button', name='Reset everything').click(); await asyncio.sleep(2.5)
    check('reset reached B', await B.evaluate("Object.keys(__lime.state().done).length") == 0)
    before = await B.evaluate("localStorage.getItem('lime.v1.before-reset')")
    check('B kept lime.v1.before-reset', bool(before) and len(json.loads(before)['done']) == 5)
    bt = await B.locator('#banner-reset').inner_text() if await B.locator('#banner-reset').count() else ''
    check('B shows the reset notice', 'Progress was reset on another device on' in bt, bt)
    await B.get_by_role('button', name="KEEP THIS DEVICE'S PROGRESS").click(); await asyncio.sleep(3)
    check("keeping B's progress merges it back", await B.evaluate("Object.keys(__lime.state().done).length") == 5)
    check('...and it syncs to A at the new epoch', await A.evaluate("Object.keys(__lime.state().done).length") == 5 and await A.evaluate("__lime.state().epoch") > 0)
    s4 = dict(sets); await asyncio.sleep(4)
    check('quiet again after the reset round', sets == s4, (s4, sets))
    check('no page errors (cloud)', not A.errs and not B.errs, A.errs + B.errs)

async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(LIME + '/out/lime.html').read()
    open(LIME + '/out/page.html', 'w').write(html)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        try:
            await t_quota(b); await t_corrupt(b); await t_backup_after_reset(b); await t_cloud(b)
        finally:
            await b.close()
    print('FAILED: ' + ', '.join(fails) if fails else 'all d15 state tests pass')
    sys.exit(1 if fails else 0)
asyncio.run(main())
