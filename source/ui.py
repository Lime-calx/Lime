import asyncio, json
from playwright.async_api import async_playwright
W='/tmp/claude-0/-home-claude/f6ad2d12-6ada-5e0e-b708-bb181457ad9d/scratchpad/work/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':400,'height':800})
        errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/'"%W)
        html='<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">'+open(W+'lime/out/lime.html').read()
        open(W+'lime/out/page.html','w').write(html)
        await pg.goto('file://'+W+'lime/out/page.html')
        await pg.wait_for_timeout(500)
        print('home:',(await pg.inner_text('#view'))[:200].replace('\n',' | '))
        await pg.goto('file://'+W+'lime/out/page.html#lesson-py01')
        await pg.wait_for_timeout(500)
        # run first code cell
        await pg.click('.cell .btn')
        await pg.wait_for_selector('.cell .out:not([hidden])',timeout=30000)
        print('cell out:',await pg.inner_text('.cell .out'))
        # solve first exercise with solution
        r=await pg.evaluate("""async()=>{const L=__lime.LESSONS[0];return L.exercises[0].solution}""")
        ta=pg.locator('.ex').first.locator('textarea')
        await ta.fill(r)
        await pg.locator('.ex').first.get_by_text('CHECK',exact=True).click()
        await pg.wait_for_selector('.ex .win:not([hidden])',timeout=30000)
        print('solved:',await pg.locator('.ex .win').first.inner_text())
        # predict
        ans=await pg.evaluate("__lime.LESSONS[0].predict[0].ans")
        await pg.locator('.pred textarea').first.fill(ans)
        await pg.locator('.pred').first.get_by_text('CHECK',exact=True).click()
        print('pred:',(await pg.locator('.pred .fb').first.inner_text())[:30])
        # cards
        await pg.goto('file://'+W+'lime/out/page.html#cards'); await pg.wait_for_timeout(300)
        await pg.get_by_text('START REVIEW').click()
        await pg.get_by_text('SHOW ANSWER').click()
        await pg.locator('.rate .good').click()
        print('chips:',await pg.inner_text('#chips'))
        await pg.goto('file://'+W+'lime/out/page.html#me'); await pg.wait_for_timeout(300)
        print('me ok',len(await pg.inner_text('#view')))
        await pg.goto('file://'+W+'lime/out/page.html#learn'); await pg.wait_for_timeout(300)
        sw=await pg.evaluate("document.documentElement.scrollWidth")
        print('scrollWidth',sw)
        await pg.screenshot(path=W+'lime/out/learn.png')
        await pg.goto('file://'+W+'lime/out/page.html#lesson-py03'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=W+'lime/out/lesson.png')
        # all exercise solutions through UI engine
        bad=await pg.evaluate("""async()=>{await __lime.Py.load();let bad=[];for(const L of __lime.LESSONS)for(const e of L.exercises){const r=await __lime.Py.run(e.solution,e.tests);if(r.error||!r.results.every(x=>x.ok))bad.push(L.id+':'+e.id)}return bad}""")
        print('bad solutions in app engine:',bad)
        print('errors:',errs)
        await b.close()
asyncio.run(main())
