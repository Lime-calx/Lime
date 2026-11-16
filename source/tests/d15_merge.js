// d15: property tests for Lime's mergeState / normalise / tally, taken verbatim from app.html.
// Run: node tests/d15_merge.js   (exit code 1 on any failure)
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'app.html'), 'utf8');
function grab(name){ const i = src.indexOf('function ' + name + '('); if (i < 0) throw new Error('missing ' + name); let d = 0, j = src.indexOf('{', i); for (; j < src.length; j++){ if (src[j] === '{') d++; else if (src[j] === '}'){ d--; if (!d) break; } } return src.slice(i, j + 1); }
const names = ['canon', 'same', 'blank', 'isObj', 'numOf', 'tally', 'normalise', 'tieWin', 'teachMerge', 'mergeState'];
const m = {}; new Function('module', names.map(grab).join('\n') + '\nmodule.exports={' + names.join(',') + '};')(m);
const {mergeState, normalise, blank, same, canon, tally} = m.exports;

let seed = 4242; function rnd(){ seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; }
const ri = n => Math.floor(rnd() * n), T = () => 1000 + ri(6);   // few distinct times -> many ties
const KEYS = ['py01:e1', 'py01:e2', 'py02:e1', 'py02:job:a', 'py03:par:x'], DAYS = ['2026-11-11', '2026-11-12', '2026-11-13'];
const DEVS = ['dA', 'dB', 'dC'];
function rstate(dev){
  const s = blank(); s.devId = dev; s.updatedAt = ri(1e6);
  KEYS.forEach(k => { if (rnd() < .5) s.done[k] = rnd() < .5 ? {t:T(), n:1 + ri(3)} : {t:T(), n:1 + ri(3), peek:ri(2)}; });
  KEYS.forEach((k, i) => { if (rnd() < .5) s.pred['p' + i] = rnd() < .5 ? {ok:true, t:T(), n:1 + ri(2)} : {ok:false, revealed:true, t:T()}; });
  ['py01', 'py02'].forEach(l => { if (rnd() < .6) s.read[l] = T(); if (rnd() < .3) s.seen[l + ':scene'] = T(); });
  ['c0', 'c1', 'c2'].forEach(c => { if (rnd() < .6) s.cards[c] = {ease:2.5, ivl:ri(30), reps:ri(5), lapses:0, due:ri(100), last:T()}; });
  DAYS.forEach(d => { if (rnd() < .6){ const r = {xp:ri(100), ex:ri(5), pred:ri(5), cards:ri(20), newc:ri(8), jobs:ri(3)}; if (rnd() < .5) r.by = {[dev]: Object.assign({}, r)}; s.days[d] = r; } });
  ['py01', 'py02'].forEach(l => {
    if (rnd() < .6){ const r = {t:T()}; if (rnd() < .7) r.text = 'expl ' + ri(4); if (rnd() < .5) r.self = ['full', 'part', 'miss'][ri(3)]; if (rnd() < .5) r.shown = 1; if (rnd() < .4 && r.text) r.textAt = T(); s.teach[l] = r; }
    if (rnd() < .5) s.notes[l] = {text:'n' + ri(3), t:T()};
  });
  ['s1', 's2'].forEach(id => { if (rnd() < .5) s.snip[id] = rnd() < .3 ? {gone:1, t:T()} : {name:id, code:'x=' + ri(3), t:T()}; });
  if (rnd() < .6) s.exam.py = {best:ri(5) / 4, n:ri(4), t:T()};
  if (rnd() < .4) s.redo['py01:e1'] = rnd() < .5 ? {t:T(), n:1} : {t:T(), skip:1};
  if (rnd() < .2) s.future = {x:ri(3)};
  s.set.theme = ['auto', 'light', 'dark'][ri(3)];
  return normalise(s);
}
const C = x => JSON.parse(JSON.stringify(x));
const strip = s => { const c = C(s); delete c.set; delete c.devId; delete c.updatedAt; return JSON.stringify(canon(c)); };
const M = (a, b, o) => mergeState(C(a), C(b), o);
const fails = {}, ex = {};
function check(name, ok, info){ if (!ok){ fails[name] = (fails[name] || 0) + 1; if (!ex[name]) ex[name] = info; } else fails[name] = fails[name] || 0; }

const N = 2000;
for (let i = 0; i < N; i++){
  const a = rstate(DEVS[0]), b = rstate(DEVS[1]), c = rstate(DEVS[2]);
  const a0 = C(a), b0 = C(b);
  const ab = M(a, b), ba = M(b, a);
  check('commutative', strip(ab) === strip(ba), {ab: strip(ab), ba: strip(ba)});
  check('inputs untouched', same(a, a0) && same(b, b0));
  check('idempotent (x+x = x)', strip(M(ab, ab)) === strip(ab));
  check('idempotent (re-merging an input changes nothing)', strip(M(ab, b)) === strip(ab) && strip(M(ab, a)) === strip(ab));
  const aa = M(a, a); check('self-merge keeps the data', strip(M(aa, aa)) === strip(aa) && Object.keys(aa.done).length === Object.keys(a.done).length);
  check('associative', strip(M(M(a, b), c)) === strip(M(a, M(b, c))));
  check('local settings kept', same(ab.set, a.set) && ab.devId === a.devId);
  for (const k in a.done) check('no solved item lost', !!ab.done[k]);
  for (const k in b.done) check('no solved item lost', !!ab.done[k]);
  if (a.exam.py && b.exam.py) check('exam best', ab.exam.py.best === Math.max(a.exam.py.best, b.exam.py.best));
  for (const d of DAYS) if (ab.days[d]){
    const by = ab.days[d].by; let s = 0; for (const k in by) s += by[k].xp;
    check('day total = sum over devices', ab.days[d].xp === s);
  }
  // teach: text never vanishes because the other side has none
  for (const l of ['py01', 'py02']){
    const ta = a.teach[l], tb = b.teach[l];
    if ((ta && ta.text != null) || (tb && tb.text != null)) check('teach text kept', ab.teach[l] && ab.teach[l].text != null);
    if ((ta && ta.self) || (tb && tb.self)) check('teach self kept', ab.teach[l] && !!ab.teach[l].self);
  }
  if (a.future || b.future) check('unknown keys kept', 'future' in ab);
  // reset epochs: a higher epoch wins in both orders; manual (data) merge ignores it
  const reset = normalise(Object.assign(blank(), {epoch:5000, devId:'dR'}));
  check('reset wins', !Object.keys(M(a, reset).done).length && !Object.keys(M(reset, a).done).length && M(reset, a).epoch === 5000);
  const restored = M(reset, a, {data:true});
  check('data merge ignores epoch', restored.epoch === 5000 && Object.keys(a.done).every(k => restored.done[k]));
}
// per-device counters: two devices studying the same day add up; repeated merges don't double
{
  const A = blank(); A.devId = 'dA'; A.days['2026-11-13'] = {xp:40, ex:2, pred:0, cards:10, newc:4, jobs:0}; tally(A, 'dA');
  const B = blank(); B.devId = 'dB'; B.days['2026-11-13'] = {xp:30, ex:1, pred:2, cards:15, newc:8, jobs:1}; tally(B, 'dB');
  const AB = M(A, B); check('two devices sum', AB.days['2026-11-13'].xp === 70 && AB.days['2026-11-13'].newc === 12, AB.days);
  check('sum is stable on re-merge', M(AB, B).days['2026-11-13'].xp === 70 && M(M(AB, A), AB).days['2026-11-13'].xp === 70);
  // a later local increase on A is attributed to A only
  const A2 = C(AB); A2.devId = 'dA'; A2.days['2026-11-13'].xp += 5; tally(A2, 'dA');
  check('local delta goes to own device', A2.days['2026-11-13'].by.dA.xp === 45 && A2.days['2026-11-13'].by.dB.xp === 30);
  // legacy (2.1) days without .by merge by max, as before (both copies came from one sync)
  const L1 = blank(); L1.days.d = {xp:40}; const L2 = blank(); L2.days.d = {xp:40};
  check('legacy days not doubled', M(L1, L2).days.d.xp === 40);
  const E1 = blank(); E1.devId = 'dA'; E1.exam.py = {best:.5, n:2, t:10}; tally(E1, 'dA');
  const E2 = blank(); E2.devId = 'dB'; E2.exam.py = {best:.8, n:1, t:20}; tally(E2, 'dB');
  const E = M(E1, E2).exam.py; check('exam attempts sum', E.n === 3 && E.best === .8, E);
}
// teach field-by-field: A writes text, B (not synced) rates later -> both survive, both orders
{
  const A = blank(); A.teach.py01 = {text:'My explanation of variables', shown:1, t:100};
  const B = blank(); B.teach.py01 = {self:'full', t:200};
  for (const r of [M(A, B).teach.py01, M(B, A).teach.py01]) check('rating keeps text', r.text === 'My explanation of variables' && r.self === 'full' && r.shown === 1 && r.t === 200, r);
  const A2 = blank(); A2.teach.py01 = {text:'new text', textAt:300, t:300};
  check('newer text wins', M(M(A, B), A2).teach.py01.text === 'new text' && M(M(A, B), A2).teach.py01.self === 'full');
}
// notes newest-wins, snippet deletion stays
{
  const a = blank(); a.notes.x = {text:'old', t:1}; a.snip.z = {name:'z', code:'1', t:100};
  const b = blank(); b.notes.x = {text:'new', t:2}; b.snip.z = {gone:1, t:200};
  check('notes newest', M(a, b).notes.x.text === 'new' && M(b, a).notes.x.text === 'new');
  check('snippet tombstone', M(a, b).snip.z.gone && M(b, a).snip.z.gone);
}
// malformed entries never break a merge
{
  const good = rstate('dA');
  const bad = {epoch:0, done:{a:null, b:5, c:{t:1}}, pred:{p:null, q:'x'}, read:{r:7, s:null}, seen:{x:'y'}, cards:{c:null, d:[1]}, days:{d:null, e:{xp:'9', by:{z:null, y:{xp:3}}}},
    teach:{py01:null, py02:7}, notes:{n:null}, snip:{s:null}, exam:{py:null}, redo:{r:null}, examBy:{py:null}, set:null};
  let ok = true, out;
  try { out = M(good, bad); M(bad, good); M(bad, bad); normalise(null); normalise([1]); normalise('x'); } catch(e){ ok = false; ex.malformed = String(e.stack); }
  check('malformed entries survive merge', ok);
  if (ok){
    check('malformed dropped', !('a' in out.done || 'b' in out.done) || (good.done.a || good.done.b));
    check('numbers allowed in read', normalise(bad).read.r === 7 && !('s' in normalise(bad).read));
    check('bad day counters coerced', normalise(bad).days.e.xp === 9);
  }
}
// tie-breaks: equal t in done and cards -> same pick both ways
{
  const a = blank(); a.done.k = {t:5, n:1}; a.cards.c = {last:9, ivl:1};
  const b = blank(); b.done.k = {t:5, n:2, peek:0}; b.cards.c = {last:9, ivl:3, first:1};
  check('done tie prefers more info', M(a, b).done.k.peek === 0 && M(b, a).done.k.peek === 0);
  check('card tie deterministic', same(M(a, b).cards.c, M(b, a).cards.c) && M(a, b).cards.c.first === 1);
}
const bad = Object.entries(fails).filter(([, n]) => n);
for (const [k, n] of Object.entries(fails)) console.log((n ? 'FAIL ' : 'ok   ') + k + (n ? ' x' + n : ''));
if (bad.length){ for (const [k] of bad) if (ex[k]) console.log('example', k, JSON.stringify(ex[k]).slice(0, 1500)); process.exit(1); }
console.log('all merge properties hold over', N, 'random triples');
