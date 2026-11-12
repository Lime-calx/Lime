"""Build the installable Lime (GitHub Pages) into pwa/dist from out/lime.html.

dist/
  index.html            the app, with manifest, icons, Brython from vendor/, service worker registration
  manifest.webmanifest
  sw.js                 offline shell, cache-first; an update waits for a tap
  icons/                pixel lime, 192/512 + maskable + apple
  vendor/brython/       Brython 3.14.3 (so Python works offline and without a CDN)
"""
import hashlib, json, os, re, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "pwa", "dist")
BRY = os.path.join(HERE, "..", "node_modules", "brython")

app = open(os.path.join(HERE, "out", "lime.html"), encoding="utf-8").read()
version = re.search(r"version:'([\d.]+)'", app).group(1)

shutil.rmtree(DIST, ignore_errors=True)
os.makedirs(os.path.join(DIST, "icons"))
os.makedirs(os.path.join(DIST, "vendor", "brython"))
for f in ("brython.min.js", "brython_stdlib.js"):
    shutil.copy(os.path.join(BRY, f), os.path.join(DIST, "vendor", "brython", f))

# ---- icons from the same pixel art as the logo
ART = ['......ss....', '.....ssl....', '...ggggggg..', '..gGGGGGGGg.', '.gGGGwGGGGGg', '.gGGwGGGGGGg',
       '.gGGGGGGGGGg', '.gGGGGGGGGGg', '..gGGGGGGGg.', '...gGGGGGg..', '....ggggg...', '............']
COL = {'g': (0x4E, 0x8F, 0x12), 'G': (0x8B, 0xD1, 0x22), 'w': (0xEA, 0xF9, 0xBA), 's': (0x7A, 0x5B, 0x2E), 'l': (0x5D, 0xAA, 0x1A)}
BG = (0x0B, 0x12, 0x06)


def icon(size, pad_frac, name):
    img = Image.new("RGB", (size, size), BG)
    inner = int(size * (1 - 2 * pad_frac))
    cell = inner // 12
    off = (size - cell * 12) // 2
    for y, row in enumerate(ART):
        for x, ch in enumerate(row):
            if ch in COL:
                for yy in range(cell):
                    for xx in range(cell):
                        img.putpixel((off + x * cell + xx, off + y * cell + yy + cell // 2), COL[ch])
    img.save(os.path.join(DIST, "icons", name))


icon(192, 0.08, "icon-192.png")
icon(512, 0.08, "icon-512.png")
icon(512, 0.2, "maskable-512.png")
icon(180, 0.1, "apple-180.png")
icon(64, 0.04, "favicon.png")

manifest = {
    "id": "/Lime/", "name": "Lime", "short_name": "Lime",
    "description": "Learn programming and computer science in Calx, the Clockwork City.",
    "start_url": "./", "scope": "./", "display": "standalone", "orientation": "any",
    "background_color": "#0B1206", "theme_color": "#8BD122",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
json.dump(manifest, open(os.path.join(DIST, "manifest.webmanifest"), "w"), indent=2)

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#8BD122">
<meta name="description" content="Learn programming and computer science in Calx, the Clockwork City.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="icons/favicon.png">
<link rel="apple-touch-icon" href="icons/apple-180.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}
#upd{position:fixed;top:calc(8px + env(safe-area-inset-top,0px));left:50%;transform:translateX(-50%);z-index:80;font:10px/1.5 'Press Start 2P',monospace;background:#FFD75E;color:#17230E;border:2px solid #17230E;box-shadow:3px 3px 0 #17230E;padding:10px 14px;cursor:pointer}</style>
<script>window.__LIME_BRYTHON_BASE = 'vendor/brython/';</script>
</head>
<body>
"""
TAIL = """
<button id="upd" type="button" hidden>UPDATE READY: TAP TO RELOAD</button>
<script>
(function(){
  if (!('serviceWorker' in navigator)) return;
  var btn = document.getElementById('upd'), waiting = null, reloading = false;
  function offer(w){ waiting = w; btn.hidden = false; }
  btn.addEventListener('click', function(){ if (waiting) waiting.postMessage('skip'); });
  navigator.serviceWorker.addEventListener('controllerchange', function(){ if (reloading) return; reloading = true; location.reload(); });
  navigator.serviceWorker.register('sw.js').then(function(reg){
    if (reg.waiting && navigator.serviceWorker.controller) offer(reg.waiting);
    reg.addEventListener('updatefound', function(){
      var nw = reg.installing; if (!nw) return;
      nw.addEventListener('statechange', function(){ if (nw.state === 'installed' && navigator.serviceWorker.controller) offer(nw); });
    });
    setInterval(function(){ reg.update().catch(function(){}); }, 60 * 60 * 1000);
    document.addEventListener('visibilitychange', function(){ if (document.visibilityState === 'visible') reg.update().catch(function(){}); });
  }).catch(function(){});
})();
</script>
</body>
</html>
"""
index = HEAD + app + TAIL
open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(index)

files = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png",
         "icons/apple-180.png", "icons/favicon.png", "vendor/brython/brython.min.js", "vendor/brython/brython_stdlib.js"]
h = hashlib.sha256()
for f in files[1:]:
    h.update(open(os.path.join(DIST, f), "rb").read())
tag = version + "-" + h.hexdigest()[:10]

SW = """/* Lime service worker: offline shell, cache-first; a new version waits until the user taps Update. */
const VERSION = '%s';
const SHELL = 'lime-shell-' + VERSION;
const FONTS = 'lime-fonts';
const FILES = %s;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(FILES)));
});
self.addEventListener('message', e => { if (e.data === 'skip') self.skipWaiting(); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('lime-shell-') && k !== SHELL).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin){
    if (url.pathname.endsWith('manifest.webmanifest')){
      e.respondWith(fetch(req).then(r => { const copy = r.clone(); caches.open(SHELL).then(c => c.put(req, copy)); return r; }).catch(() => caches.match(req)));
      return;
    }
    e.respondWith(caches.match(req, {ignoreSearch: true}).then(hit => hit || (req.mode === 'navigate' ? caches.match('index.html') : null)).then(hit => hit || fetch(req)));
    return;
  }
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com'){
    e.respondWith(caches.open(FONTS).then(c => c.match(req).then(hit => hit || fetch(req).then(r => { if (r.ok || r.type === 'opaque') c.put(req, r.clone()); return r; }))));
  }
  /* everything else (Google sign-in, Drive) goes straight to the network */
});
""" % (tag, json.dumps(files))
open(os.path.join(DIST, "sw.js"), "w").write(SW)
open(os.path.join(DIST, ".nojekyll"), "w").write("")
open(os.path.join(DIST, "README.md"), "w").write(
    "# Lime\n\nLearn programming and computer science in Calx, the Clockwork City.\n\n"
    "Installable app: https://lime-calx.github.io/Lime/\n\n"
    "Static PWA (GitHub Pages, main branch, root). Python runs in the page with Brython 3.14.3 (vendor/brython). "
    "Progress syncs through Google Drive (`My Apps/hub/lime/`) following the My Apps hub contract.\n")
print("built", tag, sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(DIST) for f in fs) // 1024, "KB")
