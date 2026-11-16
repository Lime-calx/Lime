import asyncio
from playwright.async_api import async_playwright
W='/tmp/claude-0/-home-claude/f6ad2d12-6ada-5e0e-b708-bb181457ad9d/scratchpad/work/'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':400,'height':860})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+W+'lime/out/page.html#lesson-py01'); await pg.wait_for_timeout(500)
        print(errs, await pg.locator('.pz').count(), await pg.locator('.pz .ln').count())
        print((await pg.locator('.pz').first.inner_text())[:400] if await pg.locator('.pz').count() else (await pg.inner_text('#view'))[:300])
        await b.close()
asyncio.run(main())
