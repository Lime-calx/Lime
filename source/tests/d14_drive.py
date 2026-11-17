"""d14: Google Drive sync + Citrus hub, against a shared fake Drive (two browser contexts = two devices).
Run from the clone after `python3 assemble.py`:  LIME_PORT=8814 python3 tests/d14_drive.py
Citrus's real inbound.js is served next to the page (CITRUS_DOCS, as pwa_test.py does)."""
import asyncio, itertools, json, os, re, shutil, subprocess, sys, tempfile, time, urllib.parse
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # .../lime
W = os.path.dirname(HERE) + '/'
PORT = int(os.environ.get('LIME_PORT', '8814'))
CIT = os.environ.get('CITRUS_DOCS', '/tmp/claude-0/-home-claude/f6ad2d12-6ada-5e0e-b708-bb181457ad9d/scratchpad/citrus/docs')
BASE = 'http://localhost:%d/page.html' % PORT
FOLDER = 'application/vnd.google-apps.folder'
CORS = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods': '*', 'Content-Type': 'application/json'}
FAILS = []

def check(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg)
    if not cond: FAILS.append(msg)

class Drive:
    def __init__(self):
        self.files = {}; self.n = 0; self.clock = itertools.count(1); self.faults = []; self.delay = 0.0; self.calls = []; self.log = []
    def ts(self): return '2026-11-13T%08d' % next(self.clock)
    def add(self, name, parent='root', mime=FOLDER, content=None, props=None):
        self.n += 1; fid = 'f%d' % self.n; t = self.ts()
        self.files[fid] = dict(id=fid, name=name, parents=[parent], mimeType=mime, content=content, appProperties=dict(props or {}), trashed=False, createdTime=t, modifiedTime=t)
        self.log.append(fid); return fid
    def gone(self, f):
        while f:
            if f['trashed']: return True
            f = self.files.get(f['parents'][0])
        return False
    def live(self, name, folder=None):
        return [f for f in self.files.values() if f['name'] == name and not self.gone(f) and (folder is None or (f['mimeType'] == FOLDER) == folder)]
    def path(self, *names):
        cur = ['root']
        for nm in names: cur = [f['id'] for f in self.files.values() if f['name'] == nm and f['mimeType'] == FOLDER and not self.gone(f) and f['parents'][0] in cur]
        return cur
    def fault(self, **kw): kw.setdefault('times', 1); kw['hit'] = 0; self.faults.append(kw); return kw

    async def handle(self, route, dev):
        req = route.request; method = req.method; u = urllib.parse.urlparse(req.url); qs = urllib.parse.parse_qs(u.query)
        if method == 'OPTIONS': return await route.fulfill(status=204, headers=CORS, body='')
        self.calls.append((dev, method, u.path))
        if self.delay: await asyncio.sleep(self.delay)
        for f in self.faults:
            if f['times'] > 0 and f.get('method', method) == method and re.search(f.get('path_re', '.'), u.path) and f.get('dev', dev) == dev:
                f['times'] -= 1; f['hit'] += 1
                if f.get('abort'): return await route.abort('internetdisconnected')
                if f.get('create_then'):
                    await self._do(route, method, u, qs, req, fulfill=False)
                    return await route.fulfill(status=f['create_then'], headers=CORS, body='{"error":{"code":%d}}' % f['create_then'])
                body = {'error': {'code': f['status'], 'errors': [{'reason': f.get('reason', '')}]}}
                return await route.fulfill(status=f['status'], headers=CORS, body=json.dumps(body))
        return await self._do(route, method, u, qs, req)

    async def _do(self, route, method, u, qs, req, fulfill=True):
        async def J(x, st=200):
            if fulfill: await route.fulfill(status=st, headers=CORS, body=json.dumps(x))
        p = u.path
        if p == '/drive/v3/changes/startPageToken': return await J({'startPageToken': str(len(self.log) + 1)})
        if p == '/drive/v3/changes':
            t = int(qs['pageToken'][0]); ids = self.log[t - 1:]
            ch = [{'fileId': i, 'removed': False, 'file': {k: self.files[i][k] for k in ('id', 'name', 'parents')} | {'trashed': self.gone(self.files[i])}} for i in ids]
            return await J({'changes': ch, 'newStartPageToken': str(len(self.log) + 1)})
        if p == '/drive/v3/files' and method == 'GET':
            q = qs['q'][0]
            tg = re.search(r"appProperties has \{ key='(\w+)' and value='([^']*)' \}", q)
            if tg:
                hits = sorted([f for f in self.files.values() if not self.gone(f) and f['mimeType'] == FOLDER and f['appProperties'].get(tg.group(1)) == tg.group(2)], key=lambda f: f['createdTime'])
                return await J({'files': [{k: f[k] for k in ('id', 'name', 'parents', 'createdTime')} for f in hits]})
            nm = re.search(r"name='((?:[^'\\]|\\.)*)'", q); parent = re.search(r"'([^']*)' in parents", q).group(1)
            hits = [f for f in self.files.values() if parent in f['parents'] and not (('trashed=false' in q) and self.gone(f))]
            if nm: hits = [f for f in hits if f['name'] == nm.group(1).replace("\\'", "'")]
            if "mimeType='" in q: hits = [f for f in hits if f['mimeType'] == FOLDER]
            elif "mimeType!='" in q: hits = [f for f in hits if f['mimeType'] != FOLDER]
            hits.sort(key=lambda f: f['createdTime'])
            return await J({'files': [{k: f[k] for k in ('id', 'name', 'createdTime', 'modifiedTime', 'appProperties')} for f in hits[:int(qs.get('pageSize', ['100'])[0])]]})
        if p == '/drive/v3/files' and method == 'POST':
            m = json.loads(req.post_data); return await J({'id': self.add(m['name'], m['parents'][0], m.get('mimeType', FOLDER))})
        mm = re.match(r'^/drive/v3/files/(\w+)$', p)
        if mm:
            f = self.files.get(mm.group(1))
            if not f: return await J({'error': {'code': 404}}, 404)
            if method == 'PATCH':
                body = json.loads(req.post_data or '{}'); f['appProperties'].update(body.pop('appProperties', {}) or {}); f.update(body); f['modifiedTime'] = self.ts(); self.log.append(f['id']); return await J({'id': f['id']})
            if qs.get('alt') == ['media']:
                if fulfill: await route.fulfill(status=200, headers=CORS, body=f['content'] or '')
                return
            return await J({'id': f['id'], 'trashed': self.gone(f), 'appProperties': f['appProperties']})
        up = re.match(r'^/upload/drive/v3/files(?:/(\w+))?$', p)
        if up:
            parts = re.split(r'--lime\w+', req.post_data)
            meta = json.loads(parts[1].split('\r\n\r\n', 1)[1]); content = parts[2].split('\r\n\r\n', 1)[1]
            if content.endswith('\r\n'): content = content[:-2]
            if up.group(1):
                f = self.files.get(up.group(1))
                if not f: return await J({}, 404)
                f['content'] = content; f['appProperties'].update(meta.get('appProperties', {})); f['modifiedTime'] = self.ts(); self.log.append(f['id'])
                return await J({'id': f['id']})
            return await J({'id': self.add(meta['name'], meta['parents'][0], meta.get('mimeType'), content, meta.get('appProperties'))})
        return await J({'error': 'unknown ' + p}, 400)

    def seed_citrus(self, plan=None):
        ma = self.add('My Apps'); hub = self.add('hub', ma); cf = self.add('citrus', hub)
        self.add('plan.json', cf, 'application/json', json.dumps(plan if plan is not None else {'days': {}, 'blocks': []}))
        return ma, hub, cf

    def lime_states(self):
        return [json.loads(f['content']) for f in self.live('state.json') if self.files[f['parents'][0]]['appProperties'].get('citrusApp', 'lime') == 'lime' and self.files[f['parents'][0]]['name'] in ('lime', 'Programming - Lime')]

WORK = """(tag) => { const S = JSON.parse(JSON.stringify(__lime.state())); S.done['w:' + tag] = {t: Date.now(), n: 1}; S.updatedAt = Date.now(); __lime.setState(S); return 1; }"""
THEME = """(t) => { const S = JSON.parse(JSON.stringify(__lime.state())); S.set.theme = t; __lime.setState(S); }"""
DONE = "Object.keys(__lime.state().done).filter(k => k.startsWith('w:')).sort().join(',')"
SYNC = '__lime.syncAll(true)'

async def device(browser, drive, name, init=''):
    ctx = await browser.new_context(viewport={'width': 400, 'height': 860}, service_workers='block')
    await ctx.route(re.compile(r'https://www\.googleapis\.com/.*'), lambda r: drive.handle(r, name))
    await ctx.route(re.compile(r'https://(accounts\.google\.com|fonts\.)'), lambda r: r.abort())
    pg = await ctx.new_page(); pg.errs = []
    pg.on('pageerror', lambda e: pg.errs.append('PAGEERROR ' + str(e)))
    await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/'; window.__limeToken=%s;" % (W, json.dumps('tok-' + name)) + init)
    await pg.goto(BASE + '#home'); await pg.wait_for_timeout(400)
    pg.ctx = ctx; return pg

async def scenario(b, title, setup, run, devs=2):
    d = Drive(); setup(d)
    pages = [await device(b, d, n) for n in 'AB'[:devs]]
    print('\n== ' + title)
    try: await run(d, *pages)
    except Exception as e: check(False, title + ': raised ' + repr(e)[:300])
    for p in pages:
        check(not p.errs, title + ': no page errors ' + str(p.errs[:2])); await p.ctx.close()

async def main():
    srv_dir = tempfile.mkdtemp(prefix='d14srv')
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(HERE + '/out/lime.html').read()
    open(srv_dir + '/page.html', 'w').write(html)
    if os.path.isdir(CIT): shutil.copytree(CIT, srv_dir + '/citrus')
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '-d', srv_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()

            async def race(d, A, B):
                await A.evaluate(WORK, 'A'); await B.evaluate(WORK, 'B')
                await A.evaluate(THEME, 'dark'); await B.evaluate(THEME, 'light')
                d.delay = 0.15
                await asyncio.gather(A.evaluate(SYNC), B.evaluate(SYNC))
                d.delay = 0
                for i in range(2): await A.evaluate(SYNC); await B.evaluate(SYNC)
                check(len(d.path('My Apps')) == 1 and len(d.path('My Apps', 'hub')) == 1 and len(d.path('My Apps', 'hub', 'lime')) == 1,
                      'simultaneous first sync -> one live folder tree (My Apps %s, hub %s, lime %s)' % (d.path('My Apps'), d.path('My Apps', 'hub'), d.path('My Apps', 'hub', 'lime')))
                print('     (folders created in the race: My Apps %d, hub %d, lime %d; healed %s/%s)' % (len(d.live('My Apps') + [f for f in d.files.values() if f['name'] == 'My Apps' and f['trashed']]), len([f for f in d.files.values() if f['name'] == 'hub']), len([f for f in d.files.values() if f['name'] == 'lime']), await A.evaluate('__lime.G.healed'), await B.evaluate('__lime.G.healed')))
                da, db = await A.evaluate(DONE), await B.evaluate(DONE)
                check(da == db == 'w:A,w:B', 'both devices converge: A=%s B=%s' % (da, db))
                check(len(d.lime_states()) == 1 and len(d.live('status.json')) == 1, 'one live state.json and one status.json (%d, %d)' % (len(d.lime_states()), len(d.live('status.json'))))
                check(all('set' not in s['state'] for s in d.lime_states()), 'state.json carries no device-local settings')
                check(await A.evaluate("__lime.state().set.theme") == 'dark' and await B.evaluate("__lime.state().set.theme") == 'light', 'settings stay device-local')
                n0 = len([c for c in d.calls if c[1] in ('PATCH', 'POST') and c[2].startswith('/upload')])
                for i in range(2): await A.evaluate(SYNC); await B.evaluate(SYNC)
                n1 = len([c for c in d.calls if c[1] in ('PATCH', 'POST') and c[2].startswith('/upload')])
                check(n1 == n0, 'idle syncs with different themes upload nothing (%d uploads)' % (n1 - n0))
                c0 = len(d.calls); await A.evaluate('__lime.syncAll(false)'); c1 = len(d.calls)
                check(c1 - c0 == 1, 'idle background sync is one request via the changes feed (%d)' % (c1 - c0))
                await A.evaluate(WORK, 'A2'); await B.evaluate(WORK, 'B2'); d.delay = 0.2
                await asyncio.gather(A.evaluate(SYNC), B.evaluate(SYNC)); d.delay = 0
                await A.evaluate(SYNC); await B.evaluate(SYNC)
                st = d.lime_states()[0]['state']['done']
                check('w:A2' in st and 'w:B2' in st, 'concurrent state sync keeps both items on Drive')
                check(await A.evaluate(DONE) == await B.evaluate(DONE) == 'w:A,w:A2,w:B,w:B2', 'devices converge after concurrent sync')
                check(await A.evaluate("__lime.syncHealth().state") == 'ok', 'syncHealth ok: ' + await A.evaluate("JSON.stringify(__lime.syncHealth())"))
            await scenario(b, 'empty Drive, both devices sync for the first time at once', lambda d: None, race)

            def twin_setup(d):
                ma, hub, cf = d.seed_citrus(); old = d.add('lime', hub); new = d.add('lime', hub)
                d.add('state.json', new, 'application/json', json.dumps({'app': 'lime', 'v': 2, 'state': {'v': 2, 'epoch': 0, 'done': {'w:twin': {'t': 1, 'n': 1}}}}))
                d.add('status.json', new, 'application/json', '{}')
                d.twin = new; d.old = old
            async def twins(d, A):
                await A.evaluate("(id) => localStorage.setItem('lime.gids', JSON.stringify({'My Apps/hub/lime': id}))", d.twin)
                await A.reload(); await A.wait_for_timeout(300)
                await A.evaluate(WORK, 'A'); await A.evaluate(SYNC)
                lime = d.path('My Apps', 'hub', 'lime')
                check(lime == [d.old], 'cached newer twin -> switched to the oldest lime folder %s' % lime)
                check(await A.evaluate(DONE) == 'w:A,w:twin', "twin's state.json merged in: " + await A.evaluate(DONE))
                check(d.files[d.twin]['trashed'], 'emptied twin folder trashed')
                check(len(d.live('status.json')) == 1, 'one status.json left')
            await scenario(b, 'twin lime folders, device cached the newer one', twin_setup, twins, devs=1)

            def dupfile_setup(d):
                ma, hub, cf = d.seed_citrus(); lime = d.add('lime', hub)
                d.add('state.json', lime, 'application/json', json.dumps({'app': 'lime', 'v': 2, 'state': {'done': {'w:old': {'t': 1}}}}), {'rev': '1'})
                d.add('state.json', lime, 'application/json', json.dumps({'app': 'lime', 'v': 2, 'state': {'done': {'w:new': {'t': 1}}}}), {'rev': '1'})
            async def dupfile(d, A):
                await A.evaluate(SYNC)
                check(await A.evaluate(DONE) == 'w:new,w:old', 'duplicate state.json: both twins merged')
                check(len(d.lime_states()) == 1 and d.lime_states()[0]['state']['done'].keys() >= {'w:new', 'w:old'}, 'extra state.json trashed, survivor holds both')
            await scenario(b, 'duplicate state.json files', dupfile_setup, dupfile, devs=1)

            async def trashed(d, A, B):
                await A.evaluate(SYNC)
                for f in d.live('lime', True): f['trashed'] = True
                await A.evaluate(WORK, 'A3'); await A.evaluate(SYNC)
                check(len(d.path('My Apps', 'hub', 'lime')) == 1 and any('w:A3' in s['state']['done'] for s in d.lime_states()), 'trashed cached folder dropped; work lands in a live folder')
                check(await A.evaluate('__lime.G.lastErr') == '', 'no error')
                await B.evaluate(SYNC)
                check('w:A3' in await B.evaluate(DONE), 'a fresh device sees the work')
            await scenario(b, 'cached lime folder gets trashed', lambda d: d.seed_citrus(), trashed)

            async def post5xx(d, A):
                d.fault(method='POST', path_re='^/drive/v3/files$', create_then=500, dev='A')
                d.fault(method='POST', path_re='^/upload/drive/v3/files$', create_then=503, times=2, dev='A')
                await A.evaluate(WORK, 'A5'); await A.evaluate(SYNC)
                check(len(d.live('lime', True)) == 1, 'folder POST that succeeded but answered 500 -> one lime folder')
                check(len(d.live('state.json')) == 1 and len(d.live('status.json')) == 1, 'upload POST 503-but-created -> no twin files (%d state, %d status)' % (len(d.live('state.json')), len(d.live('status.json'))))
                check(await A.evaluate('__lime.G.lastErr') == '', 'sync reports success: ' + repr(await A.evaluate('__lime.G.lastErr')))
            await scenario(b, 'creates answered 5xx after they succeeded', lambda d: d.seed_citrus(), post5xx, devs=1)

            async def quota(d, A):
                await A.evaluate(SYNC)
                fq = d.fault(method='PATCH', path_re='^/upload', status=403, reason='storageQuotaExceeded', times=5, dev='A')
                await A.evaluate(WORK, 'Q'); await A.evaluate(SYNC)
                err = await A.evaluate('__lime.G.lastErr')
                check('Google Drive is full' in err and fq['hit'] == 1, 'quota 403 not retried and explained: %r (hits %d)' % (err, fq['hit']))
                check(await A.evaluate("__lime.syncHealth().state") == 'error', 'syncHealth shows error')
                fq['times'] = 0
                fr = d.fault(method='PATCH', path_re='^/upload', status=403, reason='userRateLimitExceeded', times=1, dev='A')
                await A.evaluate(SYNC)
                check(fr['hit'] == 1 and await A.evaluate('__lime.G.lastErr') == '' and any('w:Q' in s['state']['done'] for s in d.lime_states()), 'rate-limit 403 retried and succeeded')
                d.fault(path_re='.', abort=True, times=60, dev='A'); await A.evaluate(SYNC)
                check(await A.evaluate("__lime.syncHealth().state") == 'offline', 'offline -> syncHealth offline')
            await scenario(b, 'quota / rate-limit 403s', lambda d: d.seed_citrus(), quota, devs=1)

            T = time.strftime('%Y-%m-%d'); TM = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400))
            odd = {'days': {T: {'shift': {'code': 'N', 'overnight': 'false'}}, TM: {'shift': {'overnight': True}}, 'junk': 5, '2026-13-45': {'shift': {'overnight': True}}},
                   'blocks': [{'app': 'lime', 'date': 20261113, 'start': '18:00', 'end': '19:00'}, {'app': 'lime', 'date': T, 'start': '18:00', 'end': '18:30', 'title': {'x': 1}},
                              {'app': 'lime', 'date': T, 'start': '25:00', 'end': '26:00'}, None, 'junk', {'app': 'kumquat', 'date': T, 'start': '10:00', 'end': '11:00'}]}
            async def plan(d, A):
                await A.evaluate(SYNC)
                pl = json.loads(await A.evaluate('JSON.stringify(__lime.G.plan)'))
                check(pl == [{'date': T, 'start': '18:00', 'end': '18:30', 'title': 'Lime', 'status': 'suggested'}], 'odd plan.json -> only the valid block, safe title: %s' % pl)
                ex = json.loads(await A.evaluate('JSON.stringify(__lime.buildStatus().extra)'))
                check(ex['dayKind'] == 'day', 'overnight:"false" is a day shift, not a night (%s)' % ex['dayKind'])
                asks = json.loads(await A.evaluate('JSON.stringify(__lime.buildStatus().asks)'))
                check(not any(a['date'] == TM for a in asks), 'overnight === true tomorrow -> no ask that day')
                [f for f in d.live('plan.json')][0]['content'] = '{not json'
                await A.evaluate(SYNC)
                check(await A.evaluate('JSON.stringify(__lime.G.planDays)') == '{}' and 'plan.json' in await A.evaluate('__lime.G.lastErr'), 'corrupt plan -> planDays cleared and error recorded: ' + await A.evaluate('__lime.G.lastErr'))
                [f for f in d.live('plan.json')][0]['trashed'] = True
                await A.evaluate(SYNC)
                check(await A.evaluate('JSON.stringify(__lime.G.plan)') == '[]' and await A.evaluate('__lime.G.lastErr') == '', 'plan gone -> plan cleared, no error')
            await scenario(b, 'odd plan.json', lambda d: d.seed_citrus(odd), plan, devs=1)

            async def status(d, A):
                await A.evaluate("() => localStorage.setItem('lime.gtok', JSON.stringify({token:'old', exp: Date.now() + 3e6}))")
                await A.reload(); await A.wait_for_timeout(300)
                check(await A.evaluate("localStorage.getItem('lime.gtok')") is None and await A.evaluate('__lime.G.token') is None, 'old stored token deleted at boot, not used')
                check(await A.evaluate("__lime.syncHealth().state") == 'off', 'never connected -> syncHealth off')
                await A.evaluate("localStorage.setItem('lime.gconn', '1')")
                check(await A.evaluate("__lime.syncHealth().state") == 'needs-tap', 'no token -> syncHealth needs-tap')
                await A.evaluate(WORK, 'S'); await A.evaluate(SYNC)
                check(await A.evaluate("Object.keys(localStorage).filter(k => /tok/.test(k)).length") == 0, 'token not written to localStorage')
                st = json.loads([f for f in d.live('status.json')][0]['content'])
                res = await A.evaluate("async (s) => { const m = await import('/citrus/js/inbound.js'); const r = m.normalizeStatus(s); return {issues: r.issues, icon: r.icon, labels: (r.actions||[]).map(a => a.label), aicons: (r.actions||[]).map(a => a.icon)}; }", st)
                check(res['issues'] == [], 'Citrus normalizeStatus: zero issues %s' % res['issues'])
                check(res['icon'] == '\U0001F7E9' and all(i == '\U0001F7E9' for i in res['aicons']), 'icon intact after Citrus cut: %r' % res['icon'])
                check(all(len(l) <= 28 for l in st['actions'] for l in [l['label']]) and not any(a['label'].startswith('Lime: ') for a in st['actions']), 'action labels <= 28, no prefix: %s' % [a['label'] for a in st['actions']])
                check('streak' not in st and 'xp' not in st['extra'] and 'streak' not in st['extra'], 'no streak / XP in no-pressure mode')
                await A.evaluate("() => { const S = JSON.parse(JSON.stringify(__lime.state())); S.set.showXp = true; __lime.setState(S); }")
                st2 = await A.evaluate('__lime.buildStatus()')
                check('xp' in st2['extra'] and 'streak' in st2, 'streak / XP sent when shown')
                f = d.live('status.json')[0]; f['appProperties']['h'] = 'someone-else'; f['content'] = '{}'; d.log.append(f['id'])
                await A.evaluate('__lime.syncAll(false)')
                check(d.live('status.json')[0]['content'] != '{}', 'status rewritten when the file on Drive is not the one this device wrote')
            await scenario(b, 'status.json, token', lambda d: d.seed_citrus(), status, devs=1)

            async def queued(d, A):
                await A.evaluate(SYNC); d.delay = 0.05
                p1 = A.evaluate('__lime.syncAll(false)')
                await A.wait_for_timeout(5)
                r = await A.evaluate("(async () => { const p = __lime.syncAll(false); await __lime.syncAll(true); return __lime.G.last > 0; })()")
                await p1; d.delay = 0
                check(r, 'manual sync during a running sync is queued and runs')
            await scenario(b, 'tap during a sync', lambda d: d.seed_citrus(), queued, devs=1)
            # ---- Drive layout (claude/drive-layout.md, 17/11/2026): folders found by tag ----
            async def tag_fresh(d, A):
                await A.evaluate(SYNC)
                lime = d.path('My Apps', 'hub', 'lime')
                check(len(lime) == 1 and d.files[lime[0]]['appProperties'].get('citrusApp') == 'lime', 'nothing tagged: old path created and tagged citrusApp=lime')
                st = json.loads(d.live('status.json')[0]['content'])
                check(st.get('drive') == {'byTag': True}, 'status.json says drive.byTag: %s' % st.get('drive'))
                res = await A.evaluate("async (s) => { const m = await import('/citrus/js/inbound.js'); return m.normalizeStatus(s).issues; }", st)
                check(res == [], 'Citrus normalizeStatus still zero issues with drive.byTag %s' % res)
            await scenario(b, 'tag: fresh Drive', lambda d: d.seed_citrus(), tag_fresh, devs=1)

            def moved(d):
                # what Citrus organiseDrive leaves behind: tagged folders moved and renamed under Citrus/, My Apps/hub empty
                ma, hub, cf = d.seed_citrus({'days': {}, 'blocks': [{'app': 'lime', 'date': time.strftime('%Y-%m-%d'), 'start': '18:00', 'end': '18:45', 'title': 'Lime: tagged plan', 'status': 'accepted'}]})
                old = d.add('lime', hub, props={'citrusApp': 'lime'})
                d.add('state.json', old, 'application/json', json.dumps({'app': 'lime', 'v': 2, 'state': {'done': {'w:old': {'t': 1, 'n': 1}}}}))
                root = d.add('Citrus'); h0 = d.add('00 Hub', root, props={'citrusArea': 'hub'}); learn = d.add('Learning', root); tech = d.add('Tech', learn)
                d.files[old]['parents'] = [tech]; d.files[old]['name'] = 'Programming - Lime'
                d.files[cf]['parents'] = [h0]; d.files[cf]['name'] = 'Citrus'; d.files[cf]['appProperties']['citrusApp'] = 'citrus'
                d.moved = old
            async def tag_moved(d, A):
                await A.evaluate(WORK, 'A'); await A.evaluate(SYNC)
                check(not d.path('My Apps', 'hub', 'lime'), 'after the move Lime creates no My Apps/hub/lime again')
                sts = d.live('state.json')
                check(len(sts) == 1 and sts[0]['parents'] == [d.moved], 'state.json written in the moved, renamed folder')
                check(await A.evaluate(DONE) == 'w:A,w:old', 'progress from the moved folder merged: %s' % await A.evaluate(DONE))
                ss = d.live('status.json')
                check(len(ss) == 1 and ss[0]['parents'] == [d.moved], 'status.json in the moved folder')
                titles = await A.evaluate("JSON.stringify(__lime.G.plan.map(b => b.title))")
                check('tagged plan' in titles, 'plan.json read from the tagged Citrus folder: %s' % titles)
                check(not [f for f in d.files.values() if f['trashed']], 'nothing trashed (My Apps belongs to Citrus)')
            await scenario(b, 'tag: folder moved by Citrus', moved, tag_moved, devs=1)

            def two_tagged(d):
                d.seed_citrus(); a = d.add('Programming - Lime', props={'citrusApp': 'lime'}); bb = d.add('lime copy', props={'citrusApp': 'lime'})
                d.add('state.json', bb, 'application/json', json.dumps({'app': 'lime', 'v': 2, 'state': {'done': {'w:twin': {'t': 1, 'n': 1}}}}))
                d.oldest = a
            async def tag_two(d, A):
                await A.evaluate(SYNC); await A.evaluate(SYNC)
                live = [f for f in d.live('state.json')]
                check(len(live) == 1 and live[0]['parents'] == [d.oldest], 'two tagged folders: the oldest is used, the twin merged')
                check('w:twin' in await A.evaluate(DONE), 'twin progress kept')
            await scenario(b, 'tag: two tagged folders', two_tagged, tag_two, devs=1)
            await b.close()
    finally:
        srv.terminate(); shutil.rmtree(srv_dir, ignore_errors=True)
    print('\nFAILS:', FAILS)
    sys.exit(1 if FAILS else 0)

asyncio.run(main())
