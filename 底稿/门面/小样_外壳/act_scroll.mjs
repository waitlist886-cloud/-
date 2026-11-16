// 在“假的日里”里验薄壳（11-15 拼装那一轮）：照日里的办法把介绍页放进 srcdoc 加 sandbox（只给 allow-scripts allow-modals allow-forms），
// 薄壳自己去取外壳那一页 → 牌桌 → 选一纪 → 翻开这一本（书是沙箱里再套一格）→ 从这里进 → 建档 → 请离 → 确认页 → 填进输入框；再走 1001 年那条路。
//   node act_sandbox.mjs <宽> <高> <截图前缀> <薄壳的地址> [书=moon]
//     薄壳的地址：本地是 ../小样_外壳/thin_local.html（make_thin.py --local 出的，要先起 front-cors 8773）；推了图床以后是 ../小样_外壳/thin.html
// 假的日里壳是 底稿/门面/探针/host.html（从 8773 取）。沙箱里各格是单独的进程，要 Target.setAutoAttach 一层一层挂上去才读得到。
import fs from 'node:fs';
const [W, H, OUT, SRC] = [+process.argv[2], +process.argv[3], process.argv[4], process.argv[5] || '../小样_外壳/thin_local.html'];
const BOOK = process.argv[6] || 'strife';
const K = { moon: 0, strife: 1, bronze: 2, maze: 3 }, ERA = { moon: '月银纪', strife: '纷争纪', bronze: '山铜纪', maze: '迷宫纪' };
const PORT = +(process.env.CDP_PORT || 9335);
const URL0 = 'http://localhost:8773/' + encodeURIComponent('探针') + '/host.html?src=' + encodeURIComponent(SRC) + '&t=' + Date.now();
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), errs = [], ctxs = [], waiters = [];
const send = (method, params = {}, sessionId) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params })); });
const OKERR = /front_ptr_g\d+\/front\.json|Permissions policy|allow-popups|allow-same-origin|favicon|sandboxed and lacks|Unrecognized feature|Blocked script execution/;
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') { const sid = m.params.sessionId; send('Runtime.enable', {}, sid); send('Log.enable', {}, sid); send('Network.enable', {}, sid); send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sid); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.sid === (m.sessionId || '') && x.c.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
  const push = (t) => { if (!OKERR.test(t)) errs.push(t); };
  if (m.method === 'Runtime.exceptionThrown') push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 360));
  if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) push(m.params.type + ' ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 260));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') push('LOG ' + m.params.entry.text.slice(0, 200) + ' ' + decodeURIComponent(m.params.entry.url || '').slice(-60));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) push(m.params.response.status + ' ' + decodeURIComponent(m.params.response.url).slice(-80));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function evIn(expr, x) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 30000, ...(x && x.c ? { contextId: x.c.id } : {}) }, (x && x.sid) || undefined);
  if (r.error) return undefined;
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
// 找一格：哪个执行环境里 pred 是真的
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

// ==== 下面是 act_scroll 自己的走法（上面那一截是照 act_sandbox.mjs 抄的连接和工具）====
// 11-16 用户说日里上“进入这一段”的建档页滚不动。这一支在仿日里的沙箱里走到建档页，用真滚轮和真手指去滚它。
//   node act_scroll.mjs <宽> <高> <截图前缀> <薄壳的地址> [书=strife]
await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable'); await send('Network.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
if (W < 760) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL0 });
await Promise.race([loaded, sleep(15000)]);
const S = await where(`window.__tb && window.Shell && window.Codex`, 40000);
want(!!S, '外壳载上了');
if (!S) process.exit(1);
await evIn(`__tb.skip(); return 1`, S); await sleep(2600);
// 〇、牌桌上的世界之书（跟建档页同在外壳这一页里，同一条监听管着）：真滚轮滚得动
{
  await evIn(`document.querySelector('#wbBtn').click(); return 1`, S);
  await until(S, `Codex.state.open`, 8000); await sleep(1500);
  const x0 = Math.round(W * (W < 760 ? .5 : .62)), y0 = Math.round(64 + (H - 174) * .6);
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: x0, y: y0 }); await sleep(80);
  for (let i = 0; i < 3; i++) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: x0, y: y0, deltaX: 0, deltaY: 240 }); await sleep(120); }
  await sleep(600);
  const w = await evIn(`const out = []; for (const el of document.querySelectorAll('#wb, #wb *')) if (el.scrollTop > 0) out.push((el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : el.tagName.toLowerCase()) + ' ' + Math.round(el.scrollTop) + '/' + (el.scrollHeight - el.clientHeight)); const m = document.querySelector('#wb .main'); return JSON.stringify({ moved: out, main: m ? [m.scrollHeight, m.clientHeight] : null })`, S);
  say('   世界之书滚轮以后', w);
  want(JSON.parse(w || '{}').moved && JSON.parse(w).moved.length > 0, '牌桌上的世界之书滚得动');
  await shot('0_世界之书滚过');
  await evIn(`Codex.close(); return 1`, S); await sleep(700);
}
await evIn(`__tb.select(${K[BOOK]}); return 1`, S); await sleep(900);
await evIn(`__tb.pick(${K[BOOK]}); return 1`, S);
await until(S, `!document.querySelector('#acts').hidden && __tb.picked === ${K[BOOK]}`, 25000);
await evIn(`document.querySelector('#openBook').click(); return 1`, S);
const B = await where(`window.SHELL && window.Codex && !window.Shell && document.querySelector('#toTable')`, 45000);
want(!!B, '书装进来了');
await until(S, `document.querySelector('#sh-book .sh-veil').classList.contains('off')`, 20000); await sleep(3000);
await evIn(`const B_ = window.__bk || window.__mz || {}, op_ = B_.open || B_.openEra; if (op_) { try { op_(B_.firstEra != null ? B_.firstEra : 0); } catch (e) {} } await new Promise(r => setTimeout(r, 2000)); const go = document.querySelector('.go[data-e]') || document.querySelector('.go'); if (go) { go.scrollIntoView({ block: 'center' }); go.click(); } return 1`, B);
want(await until(S, `Shell.state.build`, 8000), '建档那一页出来了');
await sleep(1200);
const M = `const el = document.querySelector('#sh-build'), cs = getComputedStyle(el), p = document.elementFromPoint(innerWidth / 2, innerHeight / 2); const chain = []; for (let n = p; n && n.nodeType === 1 && chain.length < 8; n = n.parentElement) chain.push((n.id ? '#' + n.id : n.tagName.toLowerCase() + (n.className && typeof n.className === 'string' ? '.' + n.className.split(' ')[0] : ''))); return JSON.stringify({ scrollH: el.scrollHeight, clientH: el.clientHeight, top: el.scrollTop, overflowY: cs.overflowY, pe: cs.pointerEvents, touch: cs.touchAction, inner: [innerWidth, innerHeight], hit: chain, body: getComputedStyle(document.body).overflow + '/' + getComputedStyle(document.body).touchAction, html: getComputedStyle(document.documentElement).overflow + '/' + getComputedStyle(document.documentElement).touchAction, docScroll: [document.documentElement.scrollHeight, document.documentElement.clientHeight, document.scrollingElement && document.scrollingElement.scrollTop] })`;
say('   起头', await evIn(M, S));
await shot('1_建档起头');
const cx = Math.round(W / 2), cy = Math.round(64 + (H - 174) / 2);
// 一、真滚轮
await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: cx, y: cy }); await sleep(80);
for (let i = 0; i < 4; i++) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: cx, y: cy, deltaX: 0, deltaY: 240 }); await sleep(120); }
await sleep(600);
const a = JSON.parse(await evIn(M, S));
say('   滚轮以后', JSON.stringify({ top: a.top, doc: a.docScroll }));
want(a.top > 100, '真滚轮滚得动建档页（scrollTop ' + a.top + '）');
await evIn(`document.querySelector('#sh-build').scrollTop = 0; return 1`, S); await sleep(200);
// 二、真手指（往上划）
try {
  await send('Input.synthesizeScrollGesture', { x: cx, y: cy, yDistance: -500, xDistance: 0, speed: 900, gestureSourceType: 'touch' });
} catch (e) { say('   手指那一下没发出去', String(e).slice(0, 80)); }
await sleep(800);
let b = JSON.parse(await evIn(M, S));
say('   合成手势以后', JSON.stringify({ top: b.top, doc: b.docScroll }));
// 二之二、一下一下发触摸事件（touchStart → touchMove… → touchEnd）。合成手势在沙箱那一格（单独的进程）里不一定送得到，这一种走的是浏览器自己的触摸分发
async function swipe(x, y0, y1, steps = 14) {
  await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y: y0, id: 1 }] });
  for (let i = 1; i <= steps; i++) { await send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y: Math.round(y0 + (y1 - y0) * i / steps), id: 1 }] }); await sleep(16); }
  await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
}
if (b.top < 100) {
  await swipe(cx, cy + 180, cy - 220); await sleep(900);
  b = JSON.parse(await evIn(M, S));
  say('   逐个触摸事件以后', JSON.stringify({ top: b.top, doc: b.docScroll }));
}
// 二之三、对照：同一格里临时盖一层最普通的能滚的东西，同样划一下。它也不动，就是这套验法送不进手指，不是页面的事
if (b.top < 100) {
  await evIn(`const d = document.createElement('div'); d.id = 'ctl_'; d.style.cssText = 'position:fixed;inset:0;z-index:99999;overflow-y:auto;background:#123'; d.innerHTML = '<div style="height:3000px"></div>'; document.body.appendChild(d); return 1`, S);
  await sleep(200); await swipe(cx, cy + 180, cy - 220); await sleep(900);
  const c1 = await evIn(`return document.querySelector('#ctl_').scrollTop`, S);
  await evIn(`document.querySelector('#ctl_').scrollTop = 0; return 1`, S);
  for (let i = 0; i < 3; i++) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: cx, y: cy, deltaX: 0, deltaY: 240 }); await sleep(120); }
  await sleep(500);
  const c2 = await evIn(`const v = document.querySelector('#ctl_').scrollTop; document.querySelector('#ctl_').remove(); return v`, S);
  say('   对照那一层：手指划过 scrollTop ' + c1 + '，滚轮滚过 scrollTop ' + c2);
}
want(b.top > 100, '真手指划得动建档页（scrollTop ' + b.top + '）');
await shot('2_建档滚过');
// 三、键盘（焦点在表单里时的 PageDown）、底下那枚钮够不够得着
const g = await evIn(`const go = document.querySelector('#sh-build .go'); const r = go.getBoundingClientRect(); return JSON.stringify({ goTop: Math.round(r.top), goBottom: Math.round(r.bottom), inner: innerHeight })`, S);
say('   “走”那枚钮', g);
// 四、确认页（同在外壳这一页里）：凭证长了也得滚得到底下那一排钮
await evIn(`const f = document.querySelector('#sh-build form'); f.querySelector('#bd-name').value = '走查的人'; const r = f.querySelector('.bd-races button'); if (r) r.click(); else f.querySelector('#bd-race2').value = '人类'; const w = f.querySelector('#bd-when'); if (w) w.value = '100 年，随便哪里'; f.querySelector('.go').click(); return 1`, S);
want(await until(S, `Shell.state.seal`, 12000), '请离以后出了确认页');
await sleep(900);
const SM = `const el = document.querySelector('#sh-seal'), a = document.querySelector('.sl-acts'); const r = a ? a.getBoundingClientRect() : null; return JSON.stringify({ scrollH: el.scrollHeight, clientH: el.clientHeight, top: el.scrollTop, actsBottom: r ? Math.round(r.bottom) : null, inner: innerHeight })`;
const s0 = JSON.parse(await evIn(SM, S));
say('   确认页起头', JSON.stringify(s0));
if (s0.scrollH > s0.clientH + 4) {
  // 凭证那一块纸自己能滚（最高 46vh），滚轮落在它上头先滚它。这里把滚轮放在纸上头的标题那一带，量的是整页
  const ty = 64 + 36;
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: cx, y: ty }); await sleep(80);
  for (let i = 0; i < 4; i++) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: cx, y: ty, deltaX: 0, deltaY: 240 }); await sleep(120); }
  await sleep(600);
  const s1 = JSON.parse(await evIn(SM, S));
  say('   确认页滚轮以后', JSON.stringify(s1));
  want(s1.top > 20 && s1.actsBottom <= s1.inner + 2, '确认页滚得动，底下那一排钮够得着');
} else want(s0.actsBottom <= s0.inner + 2, '确认页一屏放得下，那一排钮就在屏里');
await shot('3_确认页');
say('');
say(bad ? `对不上的 ${bad} 处` : '对不上的 0 处', '；报错', errs.length, '条');
for (const e of errs.slice(0, 8)) say('   ', e);
process.exit(0);
