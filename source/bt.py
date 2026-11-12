"""Run every code block, prediction and exercise solution in real Brython (headless Chrome) and compare with CPython."""
import asyncio, functools, http.server, json, os, sys, threading
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8766), functools.partial(Quiet, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
expected = json.load(open(os.path.join(HERE, "out", "expected.json")))


async def main():
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page()
        await pg.goto("http://127.0.0.1:8766/lime/bt.html")
        await pg.wait_for_function("window.pyReady === true || window.__err", timeout=90000)
        print("load error:", await pg.evaluate("window.__err || null"))
        for e in expected:
            try:
                r = json.loads(await pg.evaluate("([c,t]) => window.pyRun(c,t)", [e["code"], e.get("tests", "")]))
            except Exception as ex:
                print("CRASH", e["k"], str(ex)[:200]); bad += 1; continue
            if e["kind"] == "ex":
                fails = [x for x in r["results"] if not x["ok"]]
                if r["error"] or fails or not r["results"]:
                    bad += 1
                    print("EX FAIL in Brython:", e["k"], r["error"], json.dumps(fails)[:400])
            else:
                same_out = r["out"] == e["out"]
                same_err = (r["error"] is None) == (e["err"] is None)
                if not (same_out and same_err):
                    bad += 1
                    print("DIFF", e["k"])
                    print("  code:", e["code"][:160].replace("\n", " | "))
                    print("  cpython:", repr(e["out"][:200]), e["err"])
                    print("  brython:", repr(r["out"][:200]), r["error"])
        await b.close()
    print("checked", len(expected), "items; problems:", bad)

asyncio.run(main())
