import asyncio, json, sys
from playwright.async_api import async_playwright
W='/tmp/claude-0/-home-claude/f6ad2d12-6ada-5e0e-b708-bb181457ad9d/scratchpad/work/'
P='file://'+W+'lime/out/page.html'
FAKE = r"""
(() => {
  const files = {}; let n = 0;
  function add(meta, content){ const id = 'f' + (++n); files[id] = Object.assign({id, parents:['root'], appProperties:{}}, meta, {content}); return files[id]; }
  const citrus = add({name:'My Apps', mimeType:'application/vnd.google-apps.folder'});
  const hub = add({name:'hub', mimeType:'application/vnd.google-apps.folder', parents:[citrus.id]});
  const cf = add({name:'citrus', mimeType:'application/vnd.google-apps.folder', parents:[hub.id]});
  const today = new Date(); const k = today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2,'0')+'-'+String(today.getDate()).padStart(2,'0');
  add({name:'plan.json', mimeType:'application/json', parents:[cf.id]}, JSON.stringify({blocks:[{app:'lime', date:k, start:'18:00', end:'18:45', title:'Lime: loops', status:'accepted'},{app:'kumquat', date:k, start:'19:00', end:'19:30'}]}));
  window.__files = files; window.__calls = [];
  window.__limeToken = 'tok';
  const real = window.fetch;
  window.fetch = async (url, o) => {
    o = o || {}; const u = new URL(url); window.__calls.push((o.method||'GET') + ' ' + u.pathname);
    const json = (x) => new Response(JSON.stringify(x), {status:200, headers:{'Content-Type':'application/json'}});
    if (u.pathname === '/drive/v3/files' && (o.method||'GET') === 'GET'){
      const q = u.searchParams.get('q');
      const name = /name='([^']*)'/.exec(q)[1], parent = /'([^']*)' in parents/.exec(q)[1], folder = q.includes("mimeType='application");
      const hit = Object.values(files).filter(f => f.name === name && f.parents.includes(parent) && ((f.mimeType === 'application/vnd.google-apps.folder') === folder));
      return json({files: hit.map(f => ({id:f.id, name:f.name, appProperties:f.appProperties}))});
    }
    if (u.pathname === '/drive/v3/files' && o.method === 'POST'){ const m = JSON.parse(o.body); return json({id: add(m).id}); }
    const mm = /^\/drive\/v3\/files\/(\w+)$/.exec(u.pathname);
    if (mm){ const f = files[mm[1]]; if (!f) return new Response('{}', {status:404}); if (u.searchParams.get('alt') === 'media') return new Response(f.content); return json({id:f.id}); }
    const up = /^\/upload\/drive\/v3\/files(?:\/(\w+))?$/.exec(u.pathname);
    if (up){
      const parts = o.body.split(/--lime\w+/); const meta = JSON.parse(parts[1].split('\r\n\r\n')[1]); const content = parts[2].split('\r\n\r\n').slice(1).join('\r\n\r\n').replace(/\r\n$/, '');
      if (up[1]){ const f = files[up[1]]; f.content = content; f.appProperties = meta.appProperties; return json({id:f.id}); }
      return json({id: add(meta, content).id});
    }
    return real(url, o);
  };
})();
"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        ctx=await b.new_context(viewport={'width':400,'height':860})
        pg=await ctx.new_page()
        errs=[]
        pg.on('pageerror',lambda e:errs.append('PAGEERROR '+str(e)))
        pg.on('console',lambda m:errs.append(m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text and 'fonts' not in m.text else None)
        await pg.add_init_script("window.__LIME_BRYTHON_BASE='file://%snode_modules/brython/';"%W)
        html='<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">'+open(W+'lime/out/lime.html').read()
        open(W+'lime/out/page.html','w').write(html)
        async def go(h, wait=300):
            await pg.goto(P+h); await pg.wait_for_timeout(wait)
        async def sw(tag):
            w=await pg.evaluate("document.documentElement.scrollWidth")
            if w>400: print('OVERFLOW', tag, w)
        await go('#home'); print('home:', (await pg.inner_text('#view'))[:160].replace('\n',' | ')); await sw('home')
        await go('#map'); await sw('map'); await pg.screenshot(path=W+'lime/out/s_map.png', full_page=True)
        await go('#d-py'); await sw('district')
        await go('#story-py'); await sw('story')
        for i in range(3): await pg.get_by_role('button', name='NEXT >').click()
        await pg.locator('.scene .cell .btn').first.click()
        await pg.wait_for_selector('.scene .out:not([hidden])'); await pg.wait_for_function("document.querySelector('.scene .out').textContent.includes('06:00')", timeout=60000)
        print('story code out:', await pg.inner_text('.scene .out'))
        await pg.screenshot(path=W+'lime/out/s_story.png', full_page=True)
        await pg.get_by_role('button', name='TO THE DISTRICT').click(); await pg.wait_for_timeout(300)
        print('after story hash', await pg.evaluate('location.hash'))
        await go('#lesson-py01', 500); await sw('lesson')
        C=await pg.evaluate("__lime.CITY.py01")
        # parsons: click lines in solution order
        for line in C['parsons'][0]['lines']:
            await pg.locator('.pz .zone:not(.ans) .ln', has_text=line.strip()).first.click()
        await pg.locator('.pz').get_by_role('button', name='CHECK ORDER').click()
        await pg.wait_for_function("document.querySelector('.pz .tag').textContent==='SOLVED'", timeout=60000)
        print('parsons solved')
        # wrong order attempt on a fresh render is skipped; solve core exercises + jobs via fill
        L=await pg.evaluate("__lime.LESSONS[0]")
        for e in L['exercises']:
            box=pg.locator('#ex-py01-'+e['id'])
            await box.locator('textarea').fill(e['solution'])
            await box.get_by_role('button', name='CHECK').click()
            await box.locator('.win:not([hidden])').wait_for(timeout=30000)
        for j in C['jobs']:
            box=pg.locator('#ex-py01-job-'+j['id'])
            await box.locator('textarea').fill(j['solution'])
            await box.get_by_role('button', name='CHECK').click()
            await box.locator('.win:not([hidden])').wait_for(timeout=30000)
        print('exercises + jobs solved')
        # error explainer
        box=pg.locator('#ex-py01-'+L['exercises'][0]['id'])
        await box.locator('textarea').fill('print("hi"')
        await box.get_by_role('button', name='RUN').click()
        await box.locator('.explain').wait_for(timeout=20000)
        print('explain:', (await box.locator('.explain').inner_text())[:80])
        # predictions
        preds=pg.locator('.pred:has(textarea)')
        cnt=await preds.count()
        print('pred boxes', cnt)
        allp = L['predict'] + C['read']
        for i,pp in enumerate(allp):
            bx=preds.nth(i)
            await bx.locator('textarea').fill(pp['ans'])
            await bx.get_by_role('button', name='CHECK').click()
        # teach
        t=pg.locator('.teach textarea')
        await t.fill(' '.join(['word']*30))
        await pg.get_by_role('button', name='COMPARE WITH A MODEL').click()
        await pg.get_by_role('button', name='I COVERED IT ALL').click()
        await pg.wait_for_timeout(300)
        print('lp py01', await pg.evaluate("JSON.stringify(__lime.lp(__lime.LESSONS[0]))"))
        print('py02 unlocked', await pg.evaluate("__lime.unlocked(__lime.LESSONS[1])"), 'py03 unlocked', await pg.evaluate("__lime.unlocked(__lime.LESSONS[2])"))
        await go('#lesson-py03'); print('py03 view:', (await pg.inner_text('#view'))[:60].replace('\n',' '))
        # cards
        await go('#cards'); print('cards:', (await pg.inner_text('#view'))[:150].replace('\n',' '))
        await pg.get_by_role('button', name='START REVIEW').click()
        await pg.get_by_role('button', name='SHOW ANSWER').click()
        await pg.locator('.rate .good').click(); await pg.wait_for_timeout(200)
        await pg.keyboard.press(' '); await pg.keyboard.press('3'); await pg.wait_for_timeout(200)
        print('cards state:', await pg.evaluate("Object.keys(__lime.state().cards).length"))
        # index
        await go('#index'); await pg.fill('.search', 'modulo'); print('index:', (await pg.inner_text('#view'))[150:260].replace('\n',' '))
        # bench
        await go('#bench'); await pg.fill('.namebox', 'my first'); await pg.get_by_role('button', name='SAVE').click(); await pg.wait_for_timeout(200)
        print('snips', await pg.evaluate("Object.keys(__lime.state().snip)"))
        # simulate all lessons complete for exam + project
        st = await pg.evaluate("""() => { const S = JSON.parse(JSON.stringify(__lime.state())); for (const L of __lime.LESSONS){ S.read[L.id]=Date.now(); L.exercises.forEach(e=>S.done[L.id+':'+e.id]={t:Date.now()-5*86400000,n:1}); L.predict.forEach((p,i)=>S.pred[L.id+':p'+i]={ok:true,t:1}); const C=__lime.CITY[L.id]; C.jobs.forEach(j=>S.done[L.id+':job:'+j.id]={t:1,n:1}); C.parsons.forEach(p=>S.done[L.id+':par:'+p.id]={t:1}); C.read.forEach(r=>S.pred[L.id+':read:'+r.id]={ok:true,t:1}); S.teach[L.id]={self:'full',t:1}; } __lime.setState(S); return 1; }""")
        await go('#d-py'); await sw('district2'); 
        print('district:', 'START' in await pg.inner_text('#view'))
        # side quest
        D=await pg.evaluate("__lime.DIST.py")
        q=D['quests'][0]; box=pg.locator('#ex-py-quest-'+q['id'])
        await box.locator('textarea').fill(q['solution']); await box.get_by_role('button', name='CHECK').click(); await box.locator('.win:not([hidden])').wait_for(timeout=30000)
        print('quest solved')
        # exam
        await go('#exam-py'); await pg.get_by_role('button', name='BEGIN').click(); await pg.wait_for_timeout(200)
        for i in range(len(D['exam'])):
            code = await pg.inner_text('.pred pre.src')
            ans = [x['ans'] for x in D['exam'] if x['code']==code][0]
            if i==0: ans='wrong'
            await pg.fill('.pred textarea', ans)
            await pg.get_by_role('button', name='FINISH' if i==len(D['exam'])-1 else 'NEXT').click(); await pg.wait_for_timeout(80)
        print('exam:', (await pg.inner_text('#view'))[:60].replace('\n',' '))
        await pg.screenshot(path=W+'lime/out/s_exam.png')
        await go('#d-py')
        box=pg.locator('#ex-py-project-bench')
        await box.locator('textarea').fill(D['project']['solution']); await box.get_by_role('button', name='CHECK').click(); await box.locator('.win:not([hidden])').wait_for(timeout=30000)
        await pg.wait_for_timeout(300)
        print('restored:', 'SEE WHAT HAPPENS' in await pg.inner_text('#view'))
        await go('#ending-py'); print('ending ok', 'Automaton' in await pg.inner_text('#view'))
        await go('#archive-py'); print('archive cards', await pg.locator('.arch').count())
        # redo
        await go('#home'); print('home redo:', 'Re-do:' in await pg.inner_text('#view'))
        await go('#redo'); 
        it = await pg.evaluate("(()=>{const r=__lime.redoPick(); return {sol:r.ex.solution, key:r.key}})()")
        await pg.locator('.ex textarea').fill(it['sol']); await pg.get_by_role('button', name='CHECK').click(); await pg.locator('.ex .win:not([hidden])').wait_for(timeout=30000)
        print('redo ok', await pg.evaluate("Object.keys(__lime.state().redo).length"))
        # me + city mode
        await go('#me'); await pg.locator('.field', has_text='City mode').get_by_role('button', name='ON').click(); await pg.wait_for_timeout(200)
        print('cabinet items on:', await pg.locator('.cab .it:not(.off)').count())
        await sw('me'); await pg.screenshot(path=W+'lime/out/s_me.png', full_page=True)
        # fake drive
        await pg.evaluate(FAKE)
        await pg.evaluate("__lime.syncAll(true)"); await pg.wait_for_timeout(1500)
        names = await pg.evaluate("Object.values(window.__files).map(f=>f.name+'<'+(window.__files[f.parents[0]]||{name:'root'}).name)")
        print('drive files:', names)
        print('status file:', (await pg.evaluate("Object.values(window.__files).find(f=>f.name==='status.json').content"))[:200])
        await pg.evaluate("__lime.syncAll(true)"); await pg.wait_for_timeout(1500)
        print('after 2nd sync count:', await pg.evaluate("Object.values(window.__files).filter(f=>f.name==='lime').length"), 'plan', await pg.evaluate("JSON.stringify(__lime.G.plan)"))
        await go('#home'); print('citrus on home:', 'PLANNED IN CITRUS' in await pg.inner_text('#view'))
        # wide screenshot
        await pg.set_viewport_size({'width':1440,'height':900}); await go('#lesson-py02', 600)
        print('aside visible', await pg.locator('.aside').is_visible())
        await pg.screenshot(path=W+'lime/out/s_wide.png')
        await pg.set_viewport_size({'width':400,'height':860}); await go('#lesson-py02', 600)
        await pg.screenshot(path=W+'lime/out/s_lesson.png')
        print('errors:', errs)
        await b.close()
asyncio.run(main())
