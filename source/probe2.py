import asyncio, functools, http.server, json, os, threading, sys
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8768), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
code, tests = open(sys.argv[1]).read(), open(sys.argv[2]).read()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.goto("http://127.0.0.1:8768/lime/bt.html")
        await pg.wait_for_function("window.pyReady === true || window.__err", timeout=90000)
        print(await pg.evaluate("([c,t]) => window.pyRun(c,t)", [code, tests]))
        await b.close()
asyncio.run(main())
