// 预载和图鉴“正在取”那一路（11-17 夜）：在仿日里的沙箱里从图床走（那一格没有浏览器缓存，跟日里一样），看
//   一、牌桌上歇一会儿，外壳把四本书的页面和一开就要的数据取进内存，每个只取一回；
//   二、翻开一本书，书的页面和那几份数据不再下第二回；
//   三、图鉴头一屏取的是小图（assets/at/），没点人以前不取整张人像拼图（assets/pa/）；
//   四、hold：图鉴的数据（atlas.json）故意卡住，点图鉴先出“正在取”，放行以后自己画出来；
//       fail：atlas.json 一律取不到，点图鉴出“没取下来”和“再取一次”，放开以后点“再取一次”取得到、画得出来。
//   node act_pre.mjs <宽> <高> <截图前缀> <薄壳的地址> [书=strife] [hold|fail]
//     薄壳的地址照 act_atlas.mjs（推了图床以后是 ../小样_外壳/thin.html），要先起 front-cors 8773 和无头 Chrome 9335。
//     头一回跑常卡在头一步不动，套 timeout 240，没走完就重跑。
import fs from 'node:fs';
const [W, H, OUT, SRC] = [+process.argv[2], +process.argv[3], process.argv[4], process.argv[5] || '../小样_外壳/thin.html'];
const BOOK = process.argv[6] || 'strife';
const MODE = process.argv[7] || '';
const K = { moon: 0, strife: 1, bronze: 2, maze: 3 };
const BOOT = {
  moon: ['moon', 'cards', 'cg', 'have', 'pa', 'tiles', 'atlas'],
  strife: ['strife', 'card', 'cards', 'cg', 'have', 'pa', 'road', 'roadc', 'atlas'],
  bronze: ['bronze', 'road', 'cards', 'cg', 'have', 'pa', 'props', 'sky', 'stele', 'tex', 'walk', 'atlas'],
  maze: ['maze', 'cards', 'have', 'mural', 'pa', 'atlas'],
};
const PORT = +(process.env.CDP_PORT || 9335);
const URL0 = 'http://localhost:8773/' + encodeURIComponent('探针') + '/host.html?src=' + encodeURIComponent(SRC) + '&t=' + Date.now();
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0, phase = MODE === 'fail' ? 'fail' : MODE === 'hold' ? 'hold' : 'pass';
const pending = new Map(), errs = [], ctxs = [], waiters = [], reqs = [], held = [];
const T0 = Date.now();
const send = (method, params = {}, sessionId) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params })); });
const OKERR = /front_ptr_g\d+\/front\.json|Permissions policy|allow-popups|allow-same-origin|favicon|sandboxed and lacks|Unrecognized feature|Blocked script execution|fileflashly|atlas\.json|ERR_FAILED|net::/;
const fetchOn = (sid) => (MODE ? send('Fetch.enable', { patterns: [{ urlPattern: '*atlas.json*', requestStage: 'Request' }] }, sid) : null);
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') {
    const sid = m.params.sessionId;
    send('Runtime.enable', {}, sid); send('Log.enable', {}, sid); send('Network.enable', {}, sid); fetchOn(sid);
    send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sid);
  }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.sid === (m.sessionId || '') && x.c.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
  const push = (t) => { if (!OKERR.test(t)) errs.push(t); };
  if (m.method === 'Runtime.exceptionThrown') push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 360));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') push('error ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 260));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error' && m.params.entry.timestamp >= T0 - 2000) push('LOG ' + m.params.entry.text.slice(0, 200) + ' ' + decodeURIComponent(m.params.entry.url || '').slice(-60));
  if (m.method === 'Network.requestWillBeSent' && /^https?:/.test(m.params.request.url)) reqs.push({ t: Date.now(), url: m.params.request.url, id: m.params.requestId });
  if (m.method === 'Fetch.requestPaused') {
    const sid = m.sessionId, rid = m.params.requestId;
    if (phase === 'hold') held.push({ sid, rid });
    else if (phase === 'fail') send('Fetch.failRequest', { requestId: rid, errorReason: 'ConnectionReset' }, sid);
    else send('Fetch.continueRequest', { requestId: rid }, sid);
  }
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function evIn(expr, x) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 30000, ...(x && x.c ? { contextId: x.c.id } : {}) }, (x && x.sid) || undefined);
  if (r.error) return undefined;
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
async function where(pred, ms = 30000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    for (const x of [...ctxs]) { if (x.c.auxData && x.c.auxData.isDefault === false) continue; const v = await evIn(`try { return !!(${pred}); } catch (e) { return false; }`, x); if (v === true) return x; }
    await sleep(300);
  }
  return null;
}
const until = async (x, expr, ms = 20000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if ((await evIn(`try { return !!(${expr}); } catch (e) { return false; }`, x)) === true) return true; await sleep(250); } return false; };
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 84 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
const say = (...a) => console.log(...a);
let bad = 0;
const want = (ok, what) => { if (!ok) { bad++; say('   ✗ ' + what); } else say('   ✓ ' + what); };
const tail = (u) => decodeURIComponent(u).replace(/^https?:\/\/[^/]+\/gh\/[^@]+@[0-9a-f]{10}[0-9a-f]*\//, '');

await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable'); await send('Network.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL0 });
await Promise.race([loaded, sleep(15000)]);

const S = await where(`window.__tb && window.Shell && window.Codex`, 40000);
want(!!S, '薄壳把外壳那一页取来了');
if (!S) { say(errs.slice(0, 10)); process.exit(1); }
await evIn(`__tb.skip(); return 1`, S);
await sleep(13000);          // 外壳起来四秒以后开始预载，两路并着取

// 一、预载了哪些
const books = {};
for (const r of reqs) {
  const m = tail(r.url).match(/^(index\.html|data\/([a-z0-9_]+)\.json)$/);
  if (!m) continue;
  const key = r.url.replace(/\/(index\.html|data\/[a-z0-9_]+\.json)$/, '/');
  (books[key] = books[key] || {})[m[2] || 'index'] = ((books[key] || {})[m[2] || 'index'] || 0) + 1;
}
const preCount = reqs.length;
const got = {};
for (const id of Object.keys(BOOT)) {
  const b = Object.values(books).find((x) => x[id]) || {};
  got[id] = ['index'].concat(BOOT[id]).filter((f) => b[f]).length + '/' + (BOOT[id].length + 1);
}
say('   预载（页面加数据，取到/该取）', JSON.stringify(got));
const okPre = MODE ? Object.values(got).some((v) => !v.startsWith('0/')) : Object.values(got).every((v) => v.split('/')[0] === v.split('/')[1]);
want(okPre, MODE ? '牌桌上就开始预载了（hold、fail 两种跑法里图鉴那一份卡着，后头几本取到哪算哪）' : '牌桌上把四本书的页面和数据都取进来了');
const dup = Object.values(books).flatMap((b) => Object.entries(b).filter(([, n]) => n > 1).map(([k]) => k));
want(!dup.length, '预载时每个文件只取一回' + (dup.length ? '：' + dup.join('、') : ''));

// 二、翻开一本书
await evIn(`__tb.select(${K[BOOK]}); return 1`, S); await sleep(900);
await evIn(`__tb.pick(${K[BOOK]}); return 1`, S);
want(await until(S, `!document.querySelector('#acts').hidden && __tb.picked === ${K[BOOK]}`, 25000), '选定了 ' + BOOK);
const tOpen = Date.now();
await evIn(`document.querySelector('#openBook').click(); return 1`, S);
const B = await where(`window.SHELL && window.Codex && !window.Shell && document.querySelector('#toTable')`, 45000);
want(!!B, '书装进来了（' + (Date.now() - tOpen) + ' 毫秒）');
if (!B) { say(errs.slice(0, 10)); process.exit(1); }
await until(S, `document.querySelector('#sh-book .sh-veil').classList.contains('off')`, 20000); await sleep(2500);
say('   书里看外壳的内存', await evIn(`let a; try { a = typeof parent.__preGet; } catch (e) { a = '直接拿不到（' + e.name + '）'; } return a + '；转交 ' + (window.__preVia || '无')`, B));
const again = reqs.slice(preCount).filter((r) => /\/(index\.html|data\/[a-z0-9_]+\.json)$/.test(r.url) && reqs.slice(0, preCount).some((p) => p.url === r.url));
want(MODE ? true : !again.length, MODE ? '（卡着图鉴的跑法不查这一项）' : '书的页面和数据没有再下第二回' + (again.length ? '：' + again.map((r) => tail(r.url)).join('、') : ''));

// 三、四：点图鉴
const state = `const R = document.querySelector('#atl'); return JSON.stringify({ open: !!(window.Atlas && Atlas.isOpen()), shown: !!(R && !R.hidden), tabs: R ? R.querySelectorAll('.a-tab').length : 0, cards: R ? R.querySelectorAll('.at-list [data-sel]').length : 0, txt: R ? R.querySelector('.at-list').innerText.slice(0, 40) : '', retry: !!(R && R.querySelector('.a-retry')) })`;
const before = reqs.length, tClick = Date.now();
await evIn(`document.querySelector('#atBtn').click(); return 1`, B);
await sleep(700);
let st = JSON.parse(await evIn(state, B));
if (MODE === 'hold') {
  say('   点了以后', JSON.stringify(st), '卡着的请求', held.length);
  want(st.open && st.shown && /正在取/.test(st.txt), '数据还没到，图鉴先摆出来写“正在取”');
  await shot('1_正在取');
  phase = 'pass';
  for (const h of held.splice(0)) await send('Fetch.continueRequest', { requestId: h.rid }, h.sid);
  await until(B, `document.querySelectorAll('#atl .at-list [data-sel]').length > 0`, 20000);
  st = JSON.parse(await evIn(state, B));
  want(st.tabs === 4 && st.cards > 0, '放行以后自己画出来了（' + st.cards + ' 张卡）');
} else if (MODE === 'fail') {
  await until(B, `document.querySelector('#atl .a-retry')`, 20000);
  st = JSON.parse(await evIn(state, B));
  say('   点了以后', JSON.stringify(st));
  want(st.open && st.retry && /没取下来/.test(st.txt), '取不到的时候写“没取下来”，给一个再取一次的钮');
  await shot('1_没取下来');
  phase = 'pass';
  await evIn(`document.querySelector('#atl .a-retry').click(); return 1`, B);
  await until(B, `document.querySelectorAll('#atl .at-list [data-sel]').length > 0`, 25000);
  st = JSON.parse(await evIn(state, B));
  want(st.tabs === 4 && st.cards > 0, '点“再取一次”取到了，画出来了（' + st.cards + ' 张卡）');
} else {
  await until(B, `document.querySelectorAll('#atl .at-list [data-sel]').length > 0`, 10000);
  st = JSON.parse(await evIn(state, B));
  want(st.open && st.tabs === 4 && st.cards > 0, '点一下就开了，' + (Date.now() - tClick) + ' 毫秒里画出 ' + st.cards + ' 张卡');
}
await sleep(2500);
await shot('2_图鉴');
const imgs = reqs.slice(before).map((r) => tail(r.url));
const at = imgs.filter((u) => /^assets\/at\//.test(u)), pa = imgs.filter((u) => /^assets\/pa\//.test(u));
say('   点开图鉴以后取的图', 'at', at.length, 'pa', pa.length, at.slice(0, 6).join(' '));
want(!pa.length, '没点人以前不取整张人像拼图');
const dots = await evIn(`const d = [...document.querySelectorAll('#atl .a-dot')].map((e) => e.style.backgroundImage).filter(Boolean); return JSON.stringify([d.length, d.filter((s) => /assets\\/at\\/ax\\.webp/.test(s)).length])`, B);
const [nd, nax] = JSON.parse(dots);
want(nd > 0 && nd === nax, '年代轴的小圆点都从 ax.webp 取（' + nax + '/' + nd + '）');
const thumbs = await evIn(`const s = [...document.querySelectorAll('#atl .at-list .a-spr')].map((e) => e.style.backgroundImage); return JSON.stringify([s.length, s.filter((x) => /assets\\/at\\/p\\d+\\.webp/.test(x)).length])`, B);
const [ns, nat] = JSON.parse(thumbs);
want(ns > 0 && ns === nat, '名录里的人物卡都用小图（' + nat + '/' + ns + '）');

say('\n对不上的', bad, '处；报错', errs.length, '条');
for (const e of errs.slice(0, 8)) say('  ', e);
ws.close();
process.exit(bad ? 1 : 0);
