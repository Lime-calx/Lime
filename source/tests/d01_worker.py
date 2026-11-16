"""d01: learner Python runs in a Web Worker with a time limit, STOP, no page access, and friendly load failures.

Run from the clone:  python3 assemble.py && python3 tests/d01_worker.py
Serves the clone's parent folder over HTTP (workers cannot importScripts file:// URLs), so the worker path is used.
Set D01_SKIP_UI2=1 to skip (d), the full ui2.py walk-through in worker mode (about 30 s).
"""
import asyncio, os, sys, time, json, threading, subprocess, functools, re
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

LIME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.dirname(LIME) + '/'          # holds lime/ and node_modules/
PORT = int(os.environ.get('D01_PORT', '8901'))
ROOT = 'http://127.0.0.1:%d/' % PORT
BASE = ROOT + 'node_modules/brython/'
fails = []


def ok(cond, what):
    print(('PASS ' if cond else 'FAIL ') + what)
    if not cond:
        fails.append(what)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Quiet, directory=W))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def write_page():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(LIME + '/out/lime.html').read()
    open(LIME + '/out/d01_page.html', 'w').write(html)


async def new_page(b, base=BASE, extra=''):
    ctx = await b.new_context(viewport={'width': 800, 'height': 1000})
    pg = await ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    await pg.add_init_script("window.__LIME_BRYTHON_BASE=%s;localStorage.setItem('lime.gtok', JSON.stringify({t:'SECRET-TOKEN', exp:Date.now()+3600000}));%s" % (json.dumps(base), extra))
    await pg.goto(ROOT + 'lime/out/d01_page.html#bench')
    await pg.wait_for_selector('#view textarea')
    return ctx, pg, errs


async def bench_run(pg, code):
    await pg.locator('#view textarea').first.fill(code)
    await pg.locator('#view').get_by_role('button', name='RUN', exact=True).first.click()


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx, pg, errs = await new_page(b)
        out = pg.locator('#view .out').first

        # warm up: engine loads in a worker
        await bench_run(pg, 'print(6*7)')
        await pg.wait_for_function("document.querySelector('#view .out') && document.querySelector('#view .out').textContent.includes('42')", timeout=60000)
        mode = await pg.evaluate('__lime.Py.mode')
        ok(mode == 'worker', 'engine runs in a Web Worker (mode=%s)' % mode)

        # (a) runaway loops are stopped, and the page stays responsive during the run
        for code in ['while True:\n    pass\n', 'for i in range(10**9):\n    pass\n', 'n = 0\nwhile(n >= 0): n += 1\n']:
            t0 = time.time()
            await bench_run(pg, code)
            await pg.wait_for_selector('#view .out .stopbtn', timeout=10000)
            await pg.wait_for_timeout(1500)
            t1 = time.time()
            v = await pg.evaluate('1 + 1')            # would hang if the main thread were blocked
            resp = time.time() - t1
            txt = await out.inner_text()
            ok(v == 2 and resp < 1.0, 'page responsive during %r (evaluate took %.2f s, shows %r)' % (code.split('\n')[0], resp, txt.strip()[:40]))
            ok('Running' in txt, 'shows a Running... line with STOP')
            # either Lime's time limit or the runner's own loop guard (runner.py) may end it first
            try:
                await pg.wait_for_function("/Lime stopped your program|loop ran for too long/.test(document.querySelector('#view .out').textContent)", timeout=9000)
            except Exception:
                print('   output was:', await out.inner_text())
                raise
            el = time.time() - t0
            print('   ->', (await out.inner_text()).strip()[:90])
            lim = await pg.evaluate('__lime.Py.limitMs()') / 1000
            ok(el < lim + 2.5, 'stopped after %.1f s (limit here %.0f s: 5 s, stretched only on a slow or busy device)' % (el, lim))
            ok(await pg.locator('#view .explain').first.is_visible(), 'NIT explains the time limit')
        print('   message:', (await out.inner_text()).strip())
        print('   explain:', (await pg.locator('#view .explain').first.inner_text()).replace('\n', ' ')[:140])
        # a normal run right after a timeout still works (fresh worker)
        await bench_run(pg, 'print("after", sum(range(5)))')
        await pg.wait_for_function("document.querySelector('#view .out').textContent.includes('after 10')", timeout=15000)
        ok(True, 'runs normally after a timeout')

        # (b) STOP
        await bench_run(pg, 'while True:\n    x = 1\n')
        await pg.wait_for_selector('#view .out .stopbtn', timeout=10000)
        await pg.wait_for_timeout(700)
        t0 = time.time()
        await pg.locator('#view .out .stopbtn').click()
        await pg.wait_for_function("document.querySelector('#view .out').textContent.includes('You stopped the program')", timeout=3000)
        ok(time.time() - t0 < 1.5, 'STOP ends the run at once (%.2f s)' % (time.time() - t0))
        await bench_run(pg, 'print("still fine")')
        await pg.wait_for_function("document.querySelector('#view .out').textContent.includes('still fine')", timeout=15000)
        ok(True, 'runs normally after STOP')

        # (c) learner code cannot reach the page, storage, the token or __lime
        probes = {
            'window': 'from browser import window\nprint("W", window)\nprint(window.localStorage.getItem("lime.gtok"))',
            'self.localStorage': 'import browser\nprint(getattr(browser.self, "localStorage", "none"))',
            'document': 'from browser import document\nprint(document.body.innerHTML[:50])',
            '__lime': 'import browser\nprint(getattr(browser.self, "__lime", "none"))',
            'pyRun': 'import browser\nprint(getattr(browser.self, "pyRun", "none"))',
            'indexedDB': 'import browser\nprint(getattr(browser.self, "indexedDB", "none"))',
            'javascript': 'import javascript\nprint(javascript.this().localStorage)',
        }
        for name, code in probes.items():
            r = await pg.evaluate('([c]) => __lime.Py.run(c, "")', [code])
            blob = json.dumps(r)
            ok('SECRET-TOKEN' not in blob and 'gtok' not in blob.replace('lime.gtok")', '') and 'function' not in (r.get('out') or ''),
               'no page access via %s: %s' % (name, ((r.get('out') or '') + ' ' + (r.get('error') or '')).strip()[:90]))
        # tampering does not carry over: patch json.dumps / builtins, then a wrong answer still fails
        r = await pg.evaluate('''() => __lime.Py.run("import json, builtins\\n_o = json.dumps\\njson.dumps = lambda d, *a, **k: _o({'out':'', 'error':None, 'results':[{'label':'x','ok':True,'hint':'','detail':''}]})\\nbuiltins.bool = lambda x=0: True", "")''')
        r2 = await pg.evaluate('''() => __lime.Py.run("def f(x):\\n    return 0\\n", "check('f(2) is 4', ns['f'](2) == 4)")''')
        ok(r2['results'] and r2['results'][0]['ok'] is False, 'a patch made in one run does not reach the next check')
        # a result posted by learner code cannot fake a pass
        forge = ('import browser, json\n'
                 'browser.self.postMessage({"type": "result", "nonce": "x", "json": json.dumps({"out": "", "error": None, "results": [{"ok": True}]})})\n'
                 'def f(x):\n    return 0\n')
        r3 = await pg.evaluate('([c, t]) => __lime.Py.run(c, t)', [forge, "check('f(2) is 4', ns['f'](2) == 4)"])
        ok(bool(r3.get('error')) or (r3['results'] and r3['results'][0]['ok'] is False), 'a forged worker message is ignored (or browser import blocked)')
        ok(not errs, 'no page errors: %s' % errs[:3])

        # attempts: STOP does not count, a real run does
        await pg.goto(ROOT + 'lime/out/d01_page.html#lesson-py01')
        await pg.wait_for_timeout(600)
        ex = await pg.evaluate('__lime.LESSONS[0].exercises[0]')
        box = pg.locator('#ex-py01-' + ex['id'])
        await box.locator('textarea').fill('while True:\n    pass\n')
        await box.get_by_role('button', name='CHECK').click()
        await box.locator('.out .stopbtn').click()
        await box.locator('.out .err').wait_for(timeout=5000)
        await box.locator('textarea').fill(ex['solution'])
        await box.get_by_role('button', name='CHECK').click()
        await box.locator('.win:not([hidden])').wait_for(timeout=30000)
        rec = await pg.evaluate("(k) => JSON.stringify(Object.entries(__lime.state().done).filter(e => e[0].includes(k)))", ex['id'])
        ok('"n":1' in rec, 'STOPped check is not an attempt; solved on first counted try: ' + rec[:80])
        await ctx.close()

        # (e) bad Brython base: friendly message, TRY AGAIN, no duplicate script tags, predictions still work
        bad = 'http://127.0.0.1:%d/nonexistent/brython/' % PORT
        # block the fallback CDN so the test does not depend on the network
        ctx, pg, errs = await new_page(b, bad)
        await ctx.route('https://unpkg.com/**', lambda route: route.abort())
        await bench_run(pg, 'print(1)')
        await pg.wait_for_selector('#view .pyfail', timeout=60000)
        txt = await pg.locator('#view').inner_text()
        ok('Python did not load' in txt and 'TRY AGAIN' in txt and 'predictions' in txt, 'friendly load failure with TRY AGAIN')
        full = await pg.evaluate("document.querySelector('#view').textContent")
        ok('unpkg.com/brython@3.14.3' in full, 'fallback CDN was tried (details mention unpkg)')
        for i in range(3):
            await pg.get_by_role('button', name='TRY AGAIN').click()
            await pg.wait_for_timeout(300)
            await pg.wait_for_selector('#view .pyfail', timeout=60000)
        n = await pg.evaluate("document.querySelectorAll('script[src*=brython]').length")
        ok(n == 0, 'no leftover failed <script> tags after 4 tries (%d)' % n)
        # now the engine becomes reachable: TRY AGAIN recovers without a reload
        await pg.evaluate("(b) => { window.__fixBase = b; }", BASE)
        await ctx.route('**/nonexistent/brython/*', lambda route: route.continue_(url=BASE + route.request.url.rsplit('/', 1)[1]))
        await pg.get_by_role('button', name='TRY AGAIN').click()
        await pg.wait_for_function("document.querySelector('#view .out').textContent.trim() === '1'", timeout=60000)
        ok(True, 'TRY AGAIN recovers once the engine can load (mode=%s)' % await pg.evaluate('__lime.Py.mode'))
        await ctx.close()

        # main-thread fallback when workers are unavailable
        ctx, pg, errs = await new_page(b, BASE, 'window.__LIME_PY_WORKER=false;')
        r = await pg.evaluate('__lime.Py.run("print(2+2)", "")')
        ok(r['out'] == '4\n' and await pg.evaluate('__lime.Py.mode') == 'main', 'falls back to main-thread Brython')
        await ctx.close()
        ctx, pg, errs = await new_page(b, BASE, 'window.Worker = function(){ throw new Error("blocked by CSP"); };')
        r = await pg.evaluate('__lime.Py.run("print(3+3)", "")')
        ok(r['out'] == '6\n' and await pg.evaluate('__lime.Py.mode') == 'main', 'a blocked Worker falls back transparently')
        await ctx.close()

        # all content solutions pass in the worker (timing check for the 5 s limit)
        ctx, pg, errs = await new_page(b)
        items = await pg.evaluate('''() => { const a = [];
          __lime.LESSONS.forEach(L => (L.exercises || []).forEach(e => a.push([L.id + ':' + e.id, e.solution, e.tests])));
          return a; }''')
        slow, bad_items, t_all = 0, [], time.time()
        for key, sol, tests in items:
            t0 = time.time()
            r = await pg.evaluate('([c, t]) => __lime.Py.run(c, t)', [sol, tests])
            slow = max(slow, time.time() - t0)
            if r.get('error') or not r['results'] or not all(x['ok'] for x in r['results']):
                bad_items.append(key)
        ok(not bad_items, '%d core exercise solutions pass in the worker (slowest incl. worker swap %.2f s, total %.0f s) %s' % (len(items), slow, time.time() - t_all, bad_items[:5]))
        await ctx.close()
        await b.close()


def run_ui2_in_worker_mode():
    src = open(LIME + '/ui2.py').read()
    src = src.replace("'file://'+W+'lime/out/page.html'", repr(ROOT + 'lime/out/page.html'))
    src = src.replace("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';\"%W", "window.__LIME_BRYTHON_BASE='%s';\"" % BASE)
    src = src.replace("pg.on('console'", "pg.on('console'", 1)
    assert ROOT in src and BASE in src, 'ui2.py layout changed; update the rewrite in d01_worker.py'
    path = LIME + '/out/d01_ui2_http.py'
    open(path, 'w').write(src.replace("os.path.abspath(__file__)", repr(LIME + '/ui2.py')))
    t0 = time.time()
    r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=600)
    last = [l for l in r.stdout.splitlines() if l.startswith('errors:')]
    print('   ui2 (worker mode) took %.0f s; %s' % (time.time() - t0, last))
    ok(last == ['errors: []'] and r.returncode == 0, 'ui2.py walk-through passes in worker mode' + ('' if last else ' :: ' + (r.stderr[-400:])))


if __name__ == '__main__':
    srv = serve()
    write_page()
    asyncio.run(main())
    if not os.environ.get('D01_SKIP_UI2'):
        run_ui2_in_worker_mode()
    srv.shutdown()
    print('FAILURES:', fails)
    sys.exit(1 if fails else 0)
