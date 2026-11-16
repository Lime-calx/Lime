# d10: typography, contrast and theme.
#  1. Contrast (WCAG 2.x) of every token pair the UI relies on, read from the REAL computed CSS (color-mix included),
#     in light and dark theme, for all 13 district accents: text >= 4.5, UI parts (borders, focus ring, bar fill) >= 3.
#  2. Press Start 2P only renders at 8, 16 or 24px (never 9-15 or 17-23) on every route, at text size 100% and 130%.
#  3. Text size setting scales the root; theme-color meta follows the in-app theme; the PWA head has light + dark metas;
#     Python's paper is essentially unchanged; scene art band matches the sky; Me has the Text size and Editor key row controls.
# Run from the clone:  python3 assemble.py && python3 tests/d10_contrast.py   (writes out/page.html like ui2.py)
import asyncio, os, re, sys
from playwright.async_api import async_playwright
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
W = os.path.dirname(L.rstrip('/')) + '/'
P = 'file://' + L + 'out/page.html'
sys.path.insert(0, L)
from curriculum import TRACKS
fails = []
def ok(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)

def parse(c):
    """'rgb(r, g, b)' or 'color(srgb r g b)' (0-1) -> [r,g,b] 0-255"""
    m = re.match(r'rgba?\(([^)]*)\)', c)
    if m: return [float(x) for x in re.split(r'[ ,/]+', m.group(1).strip())[:3]]
    m = re.match(r'color\(srgb ([^)]*)\)', c)
    if m: return [float(x) * 255 for x in m.group(1).split()[:3]]
    raise ValueError(c)
def lum(c):
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = [f(x / 255) for x in c]
    return .2126 * r + .7152 * g + .0722 * b
def cr(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)

TOKENS = ['bg', 'panel', 'ink', 'muted', 'line', 'accent', 'accent-ink', 'accent-soft', 'ok', 'ok-soft', 'bad', 'bad-soft', 'bad-ink',
          'warn-soft', 'code-bg', 'code-ink', 'sky']
TEXT = [('ink', 'bg'), ('ink', 'panel'), ('muted', 'bg'), ('muted', 'panel'), ('muted', 'accent-soft'), ('ink', 'accent-soft'),
        ('accent-ink', 'accent'), ('ok', 'ok-soft'), ('ok', 'panel'), ('bad', 'panel'), ('bad-ink', 'bad'), ('ink', 'ok-soft'),
        ('ink', 'bad-soft'), ('ink', 'warn-soft'), ('code-ink', 'code-bg'), ('code-ink', 'sky')]
UI = [('line', 'panel'), ('line', 'bg'), ('ink', 'bg'), ('ink', 'panel'), ('accent', 'code-bg'), ('accent', 'sky')]
READ = """(names) => { const p = document.createElement('i'); document.body.append(p); const o = {};
  for (const n of names){ p.style.color = 'var(--' + n + ')'; o[n] = getComputedStyle(p).color; } p.remove(); return o; }"""

PIX_SCAN = """() => { const bad = [], seen = {};
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()){ const t = w.currentNode; if (!t.textContent.trim()) continue; const el = t.parentElement; if (!el || el.closest('svg')) continue;  /* SVG text scales with its viewBox */
    const r = el.getBoundingClientRect(); if (!r.width && !r.height) continue;
    const cs = getComputedStyle(el); if (!/Press Start/.test(cs.fontFamily) || cs.visibility === 'hidden') continue;
    const fs = parseFloat(cs.fontSize); seen[fs] = (seen[fs] || 0) + 1;
    if ([8, 16, 24, 32].indexOf(Math.round(fs * 100) / 100) < 0) bad.push(fs + 'px ' + el.tagName.toLowerCase() + '.' + el.className + ' "' + t.textContent.trim().slice(0, 30) + '"'); }
  return {bad: bad.slice(0, 8), n: bad.length, seen: seen}; }"""
UNLOCK = """() => { const S = JSON.parse(JSON.stringify(__lime.state())); for (const L of __lime.LESSONS){ S.read[L.id]=Date.now(); L.exercises.forEach(e=>S.done[L.id+':'+e.id]={t:Date.now()-5*86400000,n:1}); L.predict.forEach((p,i)=>S.pred[L.id+':'+(p.id||'p'+i)]={ok:true,t:1}); const C=__lime.CITY[L.id]; C.jobs.forEach(j=>S.done[L.id+':job:'+j.id]={t:1,n:1}); C.parsons.forEach(p=>S.done[L.id+':par:'+p.id]={t:1}); C.read.forEach(r=>S.pred[L.id+':read:'+r.id]={ok:true,t:1}); S.teach[L.id]={self:'full',t:1}; } __lime.setState(S); return 1; }"""

async def main():
    html = '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">' + open(L + 'out/lime.html').read()
    open(L + 'out/page.html', 'w').write(html)
    init = "window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';" % W
    errs = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 390, 'height': 840}, device_scale_factor=1)
        pg = await ctx.new_page(); await pg.add_init_script(init)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(P + '#home'); await pg.wait_for_timeout(500)

        # ---------- 1. contrast ----------
        worst = {}
        for theme in ('light', 'dark'):
            await pg.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
            for t in TRACKS:
                await pg.evaluate("([a,i]) => { const s = document.documentElement.style; s.setProperty('--accent', a); s.setProperty('--accent-ink', i); }", [t['accent'], t['ink']])
                c = {k: parse(v) for k, v in (await pg.evaluate(READ, TOKENS)).items()}
                for kind, pairs, need in (('text', TEXT, 4.5), ('ui', UI, 3.0)):
                    for fg, bg in pairs:
                        r = cr(c[fg], c[bg]); key = (theme, kind, fg, bg)
                        if key not in worst or r < worst[key][0]: worst[key] = (r, t['id'])
                # progress bar: the fill must stand out from the track, either by itself or by its 2px --line edge
                r = max(cr(c['accent'], c['panel']), cr(c['line'], c['panel'])); key = (theme, 'ui', 'bar fill|edge', 'panel')
                if key not in worst or r < worst[key][0]: worst[key] = (r, t['id'])
                if t['id'] == 'py':
                    if theme == 'light': py_light = c
                    else: py_dark = c
        for (theme, kind, fg, bg), (r, tid) in sorted(worst.items()):
            ok(r >= (4.5 if kind == 'text' else 3.0), '%s %s %s on %s: worst %.2f (%s)' % (theme, kind, fg, bg, r, tid))
        # Python keeps its look: paper within a few levels of the 2.1 colours
        def near(c, hx, tol=4): return all(abs(c[i] - int(hx[1 + 2 * i:3 + 2 * i], 16)) <= tol for i in range(3))
        ok(near(py_light['bg'], '#EDF3DF') and near(py_light['panel'], '#FBFDF4'), 'light: Python paper unchanged (%s %s)' % (py_light['bg'], py_light['panel']))
        ok(near(py_dark['bg'], '#0B1206') and near(py_dark['panel'], '#142010'), 'dark: Python paper unchanged (%s %s)' % (py_dark['bg'], py_dark['panel']))
        game = TRACKS[[t['id'] for t in TRACKS].index('game')]
        await pg.evaluate("t => document.documentElement.setAttribute('data-theme', t)", 'light')
        await pg.evaluate("([a,i]) => { const s = document.documentElement.style; s.setProperty('--accent', a); s.setProperty('--accent-ink', i); }", [game['accent'], game['ink']])
        gbg = parse((await pg.evaluate(READ, ['bg']))['bg'])
        ok(gbg[0] > gbg[1], 'light: Carnival Row paper is tinted pink, not green (%s)' % gbg)
        await pg.evaluate("() => { document.documentElement.removeAttribute('data-theme'); document.documentElement.style.cssText = ''; }")

        # ---------- 2. pixel font sizes over all routes ----------
        await pg.evaluate(UNLOCK); await pg.wait_for_timeout(200)
        routes = ['home', 'map', 'cards', 'index', 'bench', 'me', 'redo', 'd-py', 'story-py', 'archive-py', 'ending-py'] + ['lesson-py0%d' % i for i in range(1, 9)]
        for size in (100, 130):
            await pg.evaluate("v => { const S = __lime.state(); S.set.textSize = v; __lime.setState(S); if (v === 100) document.documentElement.removeAttribute('data-text'); else document.documentElement.setAttribute('data-text', String(v)); }", size)
            for theme in (['light', 'dark'] if size == 100 else ['light']):
                await pg.evaluate("t => { document.documentElement.setAttribute('data-theme', t); }", theme)
                for r in routes:
                    await pg.evaluate("h => { location.hash = h; }", '#' + r); await pg.wait_for_timeout(250)
                    await pg.evaluate("() => document.querySelectorAll('details').forEach(d => d.open = true)")
                    res = await pg.evaluate(PIX_SCAN)
                    ok(res['n'] == 0, 'pixel font at 8/16/24 only: %s %d%% %s %s%s' % (r, size, theme, sorted(res['seen']), (' ' + '; '.join(res['bad'])) if res['n'] else ''))
            if size == 130:
                fs = await pg.evaluate("parseFloat(getComputedStyle(document.documentElement).fontSize)")
                ok(abs(fs - 20.8) < .05, 'text size 130%%: root font size %.2fpx' % fs)
                bfs = await pg.evaluate("location.hash='#me'; parseFloat(getComputedStyle(document.body).fontSize)")
                ok(abs(bfs - 17 * 1.3) < .1, 'text size 130%%: body text scales (%.2fpx)' % bfs)
        await pg.evaluate("() => { const S = __lime.state(); S.set.textSize = 100; S.set.theme = 'auto'; __lime.setState(S); }")

        # ---------- 3. Me controls, theme-color, art band ----------
        await pg.evaluate("location.hash = '#me'"); await pg.wait_for_timeout(300)
        ok(await pg.locator('[role=group][aria-label="Text size"] button').count() == 3, 'Me: Text size control (100/115/130)')
        ok(await pg.locator('[role=group][aria-label="Editor key row"] button').count() == 3, 'Me: Editor key row control (auto/on/off)')
        await pg.locator('[aria-label="Text size"] button', has_text='115%').click(); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("document.documentElement.getAttribute('data-text') === '115' && __lime.state().set.textSize === 115"), 'Me: 115% sets data-text and S.set.textSize')
        await pg.locator('[aria-label="Text size"] button', has_text='100%').click(); await pg.wait_for_timeout(200)
        await pg.locator('[aria-label="Editor key row"] button', has_text='ON').click(); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("window.__limeEd.prefs.get().keys === 'on'"), 'Me: editor key row ON stored via editorPrefs')
        await pg.locator('[aria-label="Editor key row"] button', has_text='AUTO').click(); await pg.wait_for_timeout(200)
        await pg.locator('[aria-label="Theme"] button', has_text='DARK').click(); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("[...document.querySelectorAll('meta[name=theme-color]')].every(m => m.content === '#142010')"), 'theme DARK: theme-color meta is dark')
        await pg.locator('[aria-label="Theme"] button', has_text='LIGHT').click(); await pg.wait_for_timeout(200)
        ok(await pg.evaluate("[...document.querySelectorAll('meta[name=theme-color]')].every(m => m.content === '#EDF3DF')"), 'theme LIGHT: theme-color meta is light')
        await pg.locator('[aria-label="Theme"] button', has_text='AUTO').click(); await pg.wait_for_timeout(200)
        for theme in ('light', 'dark'):
            await pg.evaluate("t => document.documentElement.setAttribute('data-theme', t)", theme)
            await pg.evaluate("location.hash = '#story-py'"); await pg.wait_for_timeout(300)
            band = await pg.evaluate("(() => { const a = document.querySelector('.art'); return a ? getComputedStyle(a).backgroundColor : '' })()")
            sky = await pg.evaluate("(() => { const r = document.querySelector('.art svg rect'); return r ? r.getAttribute('fill') : '' })()")
            ok(bool(band) and parse(band) == [16, 26, 10] and sky.lower() in ('#101a0a', 'var(--sky)'), '%s: scene art band matches the sky (%s / %s)' % (theme, band, sky))
        # focus ring on dark code surfaces uses the accent
        await pg.evaluate("document.documentElement.setAttribute('data-theme', 'light')")
        await pg.evaluate("location.hash = '#lesson-py01'"); await pg.wait_for_timeout(400)
        oc = await pg.evaluate("""(() => { const z = document.querySelector('.pz .zone.ans') || document.querySelector('.out') || document.querySelector('pre.src');
          const b = document.createElement('button'); b.textContent = 'x'; z.append(b); b.focus({focusVisible:true}); const c = getComputedStyle(b).outlineColor; b.remove(); return c; })()""")
        ok(parse(oc) == [139, 209, 34], 'light: focus ring on a code surface uses the accent (%s)' % oc)
        await b.close()
    head = open(L + 'build_pwa.py').read()
    ok('content="#EDF3DF" media="(prefers-color-scheme: light)"' in head and 'content="#142010" media="(prefers-color-scheme: dark)"' in head, 'PWA head: light and dark theme-color metas')
    ok(not errs, 'no page errors %s' % errs[:3])
    print('d10:', 'FAILED %d' % len(fails) if fails else 'all passed')
    sys.exit(1 if fails else 0)

asyncio.run(main())
