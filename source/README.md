# Lime source

- `content/l0x.py` core lessons, `city/c0x.py` the Calx story layer per lesson, `city/d_*.py` districts, `curriculum.py` the 13-district map. Authored in the Python DSL in `dsl.py`.
- `python3 build.py` validates every solution, starter, prediction and Parsons decoy in CPython and writes `out/content.json` + `out/expected.json`.
- `python3 bt.py` re-runs everything in real Brython (headless Chrome) and compares with CPython (needs `npm i brython@3.14.3` one level up).
- `python3 assemble.py` injects content and `runner.py` into `app.html` → `out/lime.html` (the Claude artifact).
- `python3 build_pwa.py` → `pwa/dist/` (this repository's root: index.html, sw.js, manifest, icons, vendor/brython).
- Tests: `ui2.py` (full UI walk-through with a fake Drive), `pwa_test.py` (service worker, offline Python, deep links, Citrus's own normalizeStatus on our status.json).
