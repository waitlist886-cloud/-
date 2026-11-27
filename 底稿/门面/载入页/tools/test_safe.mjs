// 载入页止血那一轮的本地验（11-27）：无头 Chrome（加 --mute-audio 起），几种走法各开一页，看载入页是不是一定让路、牌桌出没出来、背景音乐走哪一路。
//   node 底稿/门面/载入页/tools/test_safe.mjs <截图目录> [方式…]     （本地 front-cors 8773 起着，CDP_PORT 默认 9351；THIN=thin.html 走图床那一版）
// 方式：wv（安卓 App 的系统 WebView 的 UA，手机竖屏）、norafp（requestAnimationFrame 不走，模拟 3D 画不动卡住）、boom（一帧里抛错）、nojs（载入页的脚本头一行就死了，只剩外壳的保底）、desk（电脑，照旧走全的）、old（老内核：UA 写 Chrome 70、没有 WebGL）
import fs from 'node:fs';
import path from 'node:path';
const DIR = process.argv[2]; const MODES = process.argv.slice(3).length ? process.argv.slice(3) : ['wv', 'norafp', 'boom', 'old', 'desk'];
const PORT = +(process.env.CDP_PORT || 9351), THIN = process.env.THIN || 'thin_local.html';
fs.mkdirSync(DIR, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let bad = 0;
const WVUA = 'Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36';
const OLDUA = 'Mozilla/5.0 (Linux; Android 8.1.0; vivo Y83A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36';
for (const MODE of MODES) {
  const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
  const ws = new WebSocket(tab.webSocketDebuggerUrl); await new Promise((r) => { ws.onopen = r; });
  let seq = 0; const pend = new Map(), ctxs = [], errs = [];
  const send = (m, p = {}) => new Promise((r) => { const id = ++seq; pend.set(id, r); ws.send(JSON.stringify({ id, method: m, params: p })); });
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); return; }
    if (m.method === 'Runtime.executionContextCreated') ctxs.push(m.params.context);
    if (m.method === 'Runtime.exceptionThrown') errs.push((m.params.exceptionDetails.exception && m.params.exceptionDetails.exception.description || m.params.exceptionDetails.text || '').split('\n')[0]);
  };
  const evIn = async (expr, x) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, ...(x ? { contextId: x.id } : {}) }); return r.result && r.result.result ? r.result.result.value : undefined; };
  const T0 = Date.now(); const log = (...a) => console.log(('[' + MODE + '] ' + ((Date.now() - T0) / 1000).toFixed(1) + 's').padEnd(14), ...a);
  const ok = (c, w) => { if (!c) bad++; log((c ? '对 ' : '不对 ') + w); };
  await send('Page.enable'); await send('Runtime.enable');
  const mob = MODE !== 'desk';
  await send('Emulation.setDeviceMetricsOverride', { width: mob ? 390 : 1280, height: mob ? 844 : 800, deviceScaleFactor: mob ? 2 : 1, mobile: mob });
  if (mob) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
  if (MODE === 'wv') await send('Network.setUserAgentOverride', { userAgent: WVUA });
  if (MODE === 'old') { await send('Network.setUserAgentOverride', { userAgent: OLDUA }); await send('Page.addScriptToEvaluateOnNewDocument', { source: 'HTMLCanvasElement.prototype.getContext = (function (g) { return function (t) { return /webgl/.test(t) ? null : g.apply(this, arguments); }; })(HTMLCanvasElement.prototype.getContext);' }); }
  if (MODE === 'norafp') await send('Page.addScriptToEvaluateOnNewDocument', { source: 'var __q = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = function (f) { return __q(function (t) { if (document.getElementById("g-3d")) return; f(t); }); };' });
  if (MODE === 'nojs') await send('Page.addScriptToEvaluateOnNewDocument', { source: 'Object.defineProperty(window, "__gateHold", { configurable: true, get: function () { return undefined; }, set: function () { throw new TypeError("模拟载入页的脚本头一行就死了"); } });' });
  if (MODE === 'boom') await send('Page.addScriptToEvaluateOnNewDocument', { source: 'var __n = 0, __r = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = function (f) { return __r(function (t) { if (document.getElementById("g-3d") && ++__n === 40) { throw new TypeError("模拟一帧里出错"); } f(t); }); };' });
  const q = MODE === 'desk' ? '?gmin=4&bgmtest' : '?bgmtest';
  await send('Page.navigate', { url: 'http://127.0.0.1:8773/' + encodeURIComponent('小样_外壳') + '/' + THIN + q + '&t=' + Date.now() });
  let S = null;
  for (let i = 0; i < 120 && !S; i++) { for (const x of [...ctxs]) if ((await evIn('!!window.__bgm', x)) === true) { S = x; break; } await sleep(250); }
  if (!S) { ok(false, '外壳没起来'); continue; }
  const gs = async () => evIn('JSON.stringify({gate: !!document.getElementById("gate"), lite: window.__gateLite, why: window.__gateWhy || "", phase: window.__gate && window.__gate.state ? window.__gate.state().phase : null, tb: window.__tb ? window.__tb.stage : null, pause: !!window.__tbPause})', S);
  let st = JSON.parse(await gs()); log('起来了', JSON.stringify(st));
  let gone = 0;
  for (let i = 0; i < 100; i++) { st = JSON.parse(await gs()); if (!st.gate) { gone = (Date.now() - T0) / 1000; break; } if (MODE === 'desk' && st.phase >= 4) break; await sleep(250); }
  if (MODE === 'desk') {
    ok(st.lite === false && st.phase >= 4, '电脑照旧走全的、走到门前（第 ' + st.phase + ' 拍）');
    await evIn('document.querySelector("#gate .g-skip").click(); 1', S); await sleep(3000);
    st = JSON.parse(await gs()); ok(!st.gate, '点跳过以后载入页拆了');
  } else {
    ok(!st.gate, '载入页让路了（' + gone.toFixed(1) + ' 秒，缘故：' + (st.why || (st.lite ? '轻量的一路走完' : '')) + '）');
    if (MODE === 'wv' || MODE === 'old') ok(st.lite === true, '走的是轻量的一路');
  }
  for (let i = 0; i < 40; i++) { if ((await evIn('window.__tb && __tb.stage', S)) === 'choose') break; await sleep(250); }
  st = JSON.parse(await gs()); ok(st.tb === 'choose' && !st.pause, '牌桌出来了（' + st.tb + '）');
  await send('Page.captureScreenshot', { format: 'jpeg', quality: 80 }).then((r) => fs.writeFileSync(path.join(DIR, MODE + '.jpg'), Buffer.from(r.result.data, 'base64')));
  if (MODE !== 'desk') { await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 60, y: 400 }] }); await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: 60, y: 400, button: 'left', clickCount: 1 }); await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: 60, y: 400, button: 'left', clickCount: 1 }); }
  await sleep(3000);
  const b = await evIn('window.__bgm.state()', S);
  log('背景音乐', b.mode, b.unlocked ? '起声了' : '没起声', b.playing ? '在放' : '没放', (+b.t).toFixed(1) + '秒', b.rel, b.playErr || '');
  if (MODE === 'wv' || MODE === 'old') ok(b.mode === 'audio', '手机、App 里走 <audio>');
  if (MODE === 'desk') ok(b.mode === 'webaudio', '电脑走 WebAudio');
  if (mob) ok(b.unlocked && b.playing && b.t > 0.5, '点一下页面起声、在放');
  if (errs.length) log('页面报的错：', errs.slice(0, 4).join(' ｜ '));
  await send('Page.close').catch(() => {});
}
console.log(bad ? `不对 ${bad} 处` : '都对'); process.exit(bad ? 1 : 0);
