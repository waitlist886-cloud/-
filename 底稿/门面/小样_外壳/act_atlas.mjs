// 图鉴那一枚钮拿真鼠标、真手指点（11-17 夜）：act_sandbox 只拿 Atlas.open() 直接开，钮点不点得开查不出来。
// 在“假的日里”里从图床走：薄壳 → 牌桌 → 选一纪 → 翻开这一本 → 量图鉴钮的位置、正中那一点压着谁 → 照屏幕坐标点下去 → 看开没开。
//   node act_atlas.mjs <宽> <高> <截图前缀> <薄壳的地址> [书=strife] [touch]
//     薄壳的地址照 act_sandbox.mjs（推了图床以后是 ../小样_外壳/thin.html），要先起 front-cors 8773；写 touch 就拿触摸点（手机）。
//     电脑上点开以后还走一遍 Esc 的先后（图鉴里点人开档案，Esc 先合档案，再按一下合图鉴）。
//   手机要加 ATLAS_TOP=1（薄壳当顶层页开）：仿日里的那一格是跨进程的，CDP 送进去的触摸和合成点按都出不了 click（世界之书那一枚一样），
//     顶层开才验得到手指点按。ATLAS_DEBUG=1 印出书里收到的事件，ATLAS_SEL=#wbBtn 换世界之书那一枚对照，ATLAS_TAP=gesture 用合成点按。
//   头一回跑常卡在头一步不动（几本书都碰到过），套 timeout 200，没走完就重跑。
import fs from 'node:fs';
const [W, H, OUT, SRC] = [+process.argv[2], +process.argv[3], process.argv[4], process.argv[5] || '../小样_外壳/thin_local.html'];
const BOOK = process.argv[6] || 'strife';
const TOUCH = process.argv[7] === 'touch';
const K = { moon: 0, strife: 1, bronze: 2, maze: 3 };
const PORT = +(process.env.CDP_PORT || 9335);
// ATLAS_TOP=1：不套仿日里的那一格，薄壳当顶层页开（手机上验手指点按用：CDP 送进跨进程那一格的触摸出不了 click，顶层没有这一层）
const TOP = !!process.env.ATLAS_TOP;
const URL0 = TOP ? 'http://localhost:8773/' + encodeURIComponent('小样_外壳') + '/' + SRC.split('/').pop() + '?t=' + Date.now()
  : 'http://localhost:8773/' + encodeURIComponent('探针') + '/host.html?src=' + encodeURIComponent(SRC) + '&t=' + Date.now();
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), errs = [], ctxs = [], waiters = [];
const send = (method, params = {}, sessionId) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params })); });
const OKERR = /front_ptr_g\d+\/front\.json|Permissions policy|allow-popups|allow-same-origin|favicon|sandboxed and lacks|Unrecognized feature|Blocked script execution|fileflashly/;
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') { const sid = m.params.sessionId; send('Runtime.enable', {}, sid); send('Log.enable', {}, sid); send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sid); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.sid === (m.sessionId || '') && x.c.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
  const push = (t) => { if (!OKERR.test(t)) errs.push(t); };
  if (m.method === 'Runtime.exceptionThrown') push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 360));
  if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) push(m.params.type + ' ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 260));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') push('LOG ' + m.params.entry.text.slice(0, 200) + ' ' + decodeURIComponent(m.params.entry.url || '').slice(-60));
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

await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
if (TOUCH) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL0 });
await Promise.race([loaded, sleep(15000)]);

const S = await where(`window.__tb && window.Shell && window.Codex`, 40000);
want(!!S, '薄壳把外壳那一页取来了');
if (!S) { say(errs.slice(0, 10)); process.exit(1); }
await evIn(`__tb.skip(); return 1`, S); await sleep(2600);
await evIn(`__tb.select(${K[BOOK]}); return 1`, S); await sleep(900);
await evIn(`__tb.pick(${K[BOOK]}); return 1`, S);
want(await until(S, `!document.querySelector('#acts').hidden && __tb.picked === ${K[BOOK]}`, 25000), '选定了 ' + BOOK);
await evIn(`document.querySelector('#openBook').click(); return 1`, S);
const B = await where(`window.SHELL && window.Codex && !window.Shell && document.querySelector('#toTable')`, 45000);
want(!!B, '书装进来了');
if (!B) { say(errs.slice(0, 10)); process.exit(1); }
await until(S, `document.querySelector('#sh-book .sh-veil').classList.contains('off')`, 20000); await sleep(3000);

// 量钮：图鉴那一枚在哪、正中那一点压着谁、数据载没载上
const SEL = process.env.ATLAS_SEL || '#atBtn';      // ATLAS_SEL=#wbBtn：拿世界之书那一枚对照（查是钮的毛病还是触摸本身没出点击）
const probe = `const b = document.querySelector('${SEL}'); if (!b) return JSON.stringify({ none: true });
  const r = b.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
  const t = document.elementFromPoint(cx, cy), chain = []; let e = t;
  while (e && chain.length < 7) { const s = getComputedStyle(e); chain.push((e.id ? '#' + e.id : e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/).join('.') : '')) + ' z' + s.zIndex + (s.pointerEvents === 'none' ? ' pe:none' : '')); e = e.parentElement; }
  return JSON.stringify({ atlas: !!window.Atlas, missing: !!(window.Atlas && Atlas.missing), loaded: !!(window.Atlas && Atlas.ready), hidden: b.hidden, rect: [r.left, r.top, r.width, r.height].map(Math.round), cx: Math.round(cx), cy: Math.round(cy), hit: !!(t && (t === b || b.contains(t))), top: chain, wb: (() => { const w = document.querySelector('#wbBtn'); const q = w && w.getBoundingClientRect(); return q ? [q.left, q.top, q.width, q.height].map(Math.round) : null; })() });`;
await evIn(`if (window.Atlas && Atlas.ready) await Atlas.ready; return 1`, B);
const p0 = await evIn(probe, B);
say('   钮', p0);
const P = JSON.parse(p0);
want(P.atlas && !P.missing && !P.hidden, '图鉴的脚本和数据载上了，钮露着');
want(P.hit, '钮正中那一点压着的就是钮自己');
await shot('1_书');

// 照屏幕坐标点：外层假日里的那一格 → 外壳里装书的那一格 → 书里的钮
const f1 = TOP ? [0, 0] : JSON.parse(await evIn(`const r = document.querySelector('#f').getBoundingClientRect(); return JSON.stringify([r.left, r.top])`));
const f2 = JSON.parse(await evIn(`const r = document.querySelector('#sh-frame').getBoundingClientRect(); return JSON.stringify([r.left, r.top])`, S));
const x = f1[0] + f2[0] + P.cx, y = f1[1] + f2[1] + P.cy;
say('   点在屏幕', Math.round(x), Math.round(y), TOUCH ? '（手指）' : '（鼠标）');
// ATLAS_DEBUG=1：点以前在书里记下收到的指针、触摸和点击事件，点完印出来（查点不开的时候用）
if (process.env.ATLAS_DEBUG) await evIn(`window.__ev = []; for (const t of ['pointerdown', 'pointerup', 'pointercancel', 'click', 'touchstart', 'touchend', 'gotpointercapture', 'lostpointercapture']) document.addEventListener(t, (e) => window.__ev.push(t + ':' + (e.target.id || e.target.tagName) + (e.pointerType ? '/' + e.pointerType : '')), true); return 1`, B);
if (TOUCH && process.env.ATLAS_TAP === 'gesture') {      // Chrome 自己合成一下点按（触摸加点按手势），比光送触摸事件像真手指
  const g = await send('Input.synthesizeTapGesture', { x, y, duration: 60, tapCount: 1, gestureSourceType: 'touch' });
  if (g.error) say('   合成点按报错', JSON.stringify(g.error));
} else if (TOUCH) {      // 光送触摸事件：仿日里的沙箱那几格里不出 click（世界之书那一枚也一样），只看得出按下、抬起落在谁身上
  await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] }); await sleep(80);
  await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
} else {
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await sleep(60);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 }); await sleep(60);
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
}
await sleep(1600);
const after = await evIn(SEL === '#atBtn' ? `const R = document.querySelector('#atl'); return JSON.stringify({ open: !!(window.Atlas && Atlas.isOpen()), shown: !!(R && !R.hidden && R.classList.contains('on')), tabs: R ? R.querySelectorAll('.a-tab').length : 0 })` : `return JSON.stringify({ open: !!(window.Codex && Codex.isOpen()), shown: true, tabs: 0 })`, B);
say('   点完', after);
if (process.env.ATLAS_DEBUG) say('   书里收到的事件', await evIn(`return JSON.stringify(window.__ev || null)`, B));
want(after && JSON.parse(after).open && JSON.parse(after).shown, '点一下图鉴开了');
await shot('2_点完');

// 电脑上再走一遍 Esc 的先后（11-17 夜添的）：图鉴里点人开档案（档案盖在图鉴上面），Esc 先合档案、图鉴还开着，再按一下才合图鉴
if (!TOUCH) {
  const tap = async (sel) => {
    const r = await evIn(`const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return ''; e.scrollIntoView({ block: 'center' }); await new Promise((r) => setTimeout(r, 250)); const q = e.getBoundingClientRect(); return JSON.stringify([q.left + q.width / 2, q.top + q.height / 2]);`, B);
    if (!r) return false;
    const [cx, cy] = JSON.parse(r), X = f1[0] + f2[0] + cx, Y = f1[1] + f2[1] + cy;
    await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: X, y: Y }); await sleep(50);
    await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: X, y: Y, button: 'left', clickCount: 1 }); await sleep(50);
    await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: X, y: Y, button: 'left', clickCount: 1 });
    return true;
  };
  const esc = async () => {
    await send('Input.dispatchKeyEvent', { type: 'rawKeyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await sleep(700);
  };
  const state = `const P = document.querySelector('#prof'); return JSON.stringify({ atlas: Atlas.isOpen(), prof: !!(P && !P.hidden && P.classList.contains('on')), over: !!(P && P.classList.contains('over')) })`;
  const p1 = await tap('#atl .at-list [data-sel^="people:"]'); await sleep(700);
  const p2 = p1 && await tap('#atl .at-panel [data-prof]'); await sleep(1400);
  const s1 = JSON.parse(await evIn(state, B));
  want(p1 && p2 && s1.atlas && s1.prof && s1.over, '图鉴里点人，档案盖在图鉴上面开了');
  await shot('3_档案');
  await esc();
  const s2 = JSON.parse(await evIn(state, B));
  want(!s2.prof && s2.atlas, 'Esc 先合档案，图鉴还开着');
  await esc();
  const s3 = JSON.parse(await evIn(state, B));
  want(!s3.atlas, '再按一下 Esc 合上图鉴');
  say('   Esc 前后', JSON.stringify([s1, s2, s3]));
}
say('');
say('对不上的 ' + bad + ' 处；报错 ' + errs.length + ' 条');
for (const e of errs.slice(0, 12)) say('   ' + e);
ws.close();
process.exit(bad ? 1 : 0);
