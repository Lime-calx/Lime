import asyncio, json, subprocess, sys, time
from playwright.async_api import async_playwright
SRV='/tmp/claude-0/-home-claude/f6ad2d12-6ada-5e0e-b708-bb181457ad9d/scratchpad/srv'
FAKE=open('/tmp/claude-0/-home-claude/f6ad2d12-6ada-5e0e-b708-bb181457ad9d/scratchpad/work/lime/ui2.py').read().split('FAKE = r"""')[1].split('"""')[0]
# night tonight in the fake plan
FAKE = FAKE.replace("JSON.stringify({blocks:[", "JSON.stringify({days:{[k]:{shift:{code:'N2',label:'Night',start:'20:00',end:'08:00',overnight:true},blocks:[]}}, blocks:[")
async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', '8765', '-d', SRV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            ctx = await b.new_context(viewport={'width':400,'height':860})
            pg = await ctx.new_page(); errs=[]
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('console', lambda m: errs.append(m.text) if m.type=='error' and 'fonts.g' not in m.text and 'ERR_' not in m.text else None)
            await pg.goto('http://localhost:8765/Lime/'); await pg.wait_for_timeout(1500)
            print('manifest:', await pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json()).then(j=>j.id+' '+j.icons.length)"))
            await pg.reload(); await pg.wait_for_timeout(1500)
            print('controlled:', await pg.evaluate("!!navigator.serviceWorker.controller"))
            await pg.goto('http://localhost:8765/Lime/#lesson-py01'); await pg.wait_for_timeout(500)
            await pg.locator('.cell .btn', has_text='RUN').first.click()
            await pg.wait_for_function("(document.querySelector('.cell .out')||{}).textContent && !/Starting|Running/.test(document.querySelector('.cell .out').textContent)", timeout=60000)
            print('python online:', (await pg.inner_text('.cell .out'))[:40])
            await ctx.set_offline(True)
            await pg.reload(); await pg.wait_for_timeout(1500)
            await pg.locator('.cell .btn', has_text='RUN').first.click()
            await pg.wait_for_function("(document.querySelector('.cell .out')||{}).textContent && !/Starting|Running/.test(document.querySelector('.cell .out').textContent)", timeout=60000)
            print('python OFFLINE:', (await pg.inner_text('.cell .out'))[:40])
            await ctx.set_offline(False)
            # deep link
            await pg.goto('http://localhost:8765/Lime/?from=citrus&do=review'); await pg.wait_for_timeout(800)
            print('deep link ->', await pg.evaluate('location.href'), '| chips:', (await pg.inner_text('#chips')).replace('\n',' '))
            # fake drive + plan with a night shift today
            await pg.evaluate(FAKE)
            await pg.evaluate("__lime.syncAll(true)"); await pg.wait_for_timeout(2000)
            st = json.loads(await pg.evaluate("Object.values(window.__files).find(f=>f.name==='status.json').content"))
            print('status: contract', st['contract'], '| asks', [(a['date'], a['minutes'], a['slot']) for a in st['asks']][:3], '| summary', st['summary'])
            print('actions', [a['id'] for a in st['actions']], '| url', st['url'])
            res = await pg.evaluate("async (s) => { const m = await import('/citrus/js/inbound.js'); const r = m.normalizeStatus(s); return {issues: r.issues, asks: r.asks.length, metrics: r.metrics.length, actions: (r.actions||[]).length}; }", st)
            print('CITRUS normalizeStatus:', res)
            print('chips after sync:', (await pg.inner_text('#chips')).replace('\n',' '))
            # second sync must not create duplicates and skip unchanged status
            n1 = await pg.evaluate("window.__calls.filter(c=>c.startsWith('PATCH')||c.startsWith('POST')).length")
            await pg.evaluate("__lime.syncAll(true)"); await pg.wait_for_timeout(1500)
            n2 = await pg.evaluate("window.__calls.filter(c=>c.startsWith('PATCH')||c.startsWith('POST')).length")
            print('writes first sync:', n1, 'second sync extra writes:', n2-n1, '| status files:', await pg.evaluate("Object.values(window.__files).filter(f=>f.name==='status.json').length"))
            # update flow: change sw.js version and check the update banner
            sw = open(SRV+'/Lime/sw.js').read(); open(SRV+'/Lime/sw.js','w').write(sw.replace("const VERSION = '", "const VERSION = 'x"))
            await pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>r.update())"); await pg.wait_for_timeout(2500)
            vis = await pg.locator('#upd').is_visible(); print('update banner:', vis)
            if vis:
                await pg.locator('#upd').click(); await pg.wait_for_timeout(2000)
                print('reloaded to new sw ok, banner now', await pg.locator('#upd').is_visible())
            print('errors:', errs)
            await b.close()
    finally:
        srv.terminate()
asyncio.run(main())
