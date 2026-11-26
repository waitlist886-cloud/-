// 载入页本地截图（11-26）：无头 Chrome 开薄壳（本地那一版 thin_local.html，要先起 front-cors 8773），一路截第一拍、路铺到一半、门亮、开门的光、牌桌出来，另录一串逐帧（拼动图用）。
//   node 底稿/门面/载入页/tools/shot_gate.mjs <宽> <高> <输出前缀> [慢网=0|1] [减少动态=0|1] [逐帧=0|1] [地址参数]
// Chrome 要先起：chrome --headless=new --remote-debugging-port=$CDP_PORT（默认 9351）
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4]];
const SLOWNET = process.argv[5] === '1', REDUCE = process.argv[6] === '1', FRAMES = process.argv[7] === '1', QS = process.argv[8] || '';
const PORT = +(process.env.CDP_PORT || 9351);
const URL0 = 'http://127.0.0.1:8773/' + encodeURIComponent('小样_外壳') + '/thin_local.html?t=' + Date.now() + (QS ? '&' + QS : '');
const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [];
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('error ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 200));
  if (m.method === 'Network.loadingFailed' && !/fonts\.g|front_ptr/.test(m.params.errorText + '')) errs.push('载不下 ' + m.params.errorText);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
const t0 = Date.now(), ms = () => Date.now() - t0;
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); console.log(ms() + 'ms', name); };
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
const mobile = W < 768;
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: mobile ? 2 : 1, mobile });
if (REDUCE) await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
// 慢网：照手机上一般的 4G 打个折（下行 1.6Mbps，往返 300 毫秒）
if (SLOWNET) await send('Network.emulateNetworkConditions', { offline: false, latency: 300, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8 });
let fr = 0, recording = FRAMES;
const rec = async () => { while (recording) { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 70 }); fs.writeFileSync(`${OUT}_f${String(fr++).padStart(4, '0')}.jpg`, Buffer.from(r.result.data, 'base64')); fs.appendFileSync(`${OUT}_frames.txt`, ms() + '\n'); await sleep(40); } };
if (FRAMES) { try { fs.unlinkSync(`${OUT}_frames.txt`); } catch (e) {} }
await send('Page.navigate', { url: URL0 });
if (FRAMES) rec();
const st = async () => { try { return JSON.parse(await ev('window.__gate ? JSON.stringify(__gate.state()) : "null"')); } catch (e) { return null; } };
// 第一拍：薄壳还在、外壳没到的时候
await sleep(SLOWNET ? 1200 : 150);
if (!FRAMES) await shot('1_罅隙');
let s, half = false, log = [];
const tEnd = Date.now() + (SLOWNET ? 90000 : 30000);
while (Date.now() < tEnd) {
  s = await st();
  if (s) log.push(ms() + ' ' + JSON.stringify(s));
  if (s && !half && s.cards >= 6) { half = true; if (!FRAMES) await shot('2_走到一半'); }
  if (s && s.phase >= 4) break;
  await sleep(SLOWNET ? 400 : 80);
}
console.log('到门口', ms() + 'ms', JSON.stringify(s));
await sleep(2200);
if (!FRAMES) await shot('3_门亮');
fs.writeFileSync(`${OUT}_state.txt`, log.join('\n'));
// 点门
await ev('window.__gateOpenedCalls = 0; window.__gateOpened = () => { window.__gateOpenedCalls++; }; 0');      // 开门的钩子（往后放音乐用）有没有调到
const r = await ev('(() => { const d = document.querySelector("#gate .g-door").getBoundingClientRect(); return [d.left + d.width / 2, d.top + d.height / 2]; })()');
await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: r[0], y: r[1], button: 'left', clickCount: 1 });
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: r[0], y: r[1], button: 'left', clickCount: 1 });
const tc = Date.now();
if (!FRAMES) {
  for (const [w, n] of [[450, '4a_门开'], [1050, '4b_光粒'], [1600, '4c_白'], [3400, '5_牌桌']]) { await sleep(Math.max(0, w - (Date.now() - tc))); await shot(n); }
} else { await sleep(4200); recording = false; await sleep(300); }
console.log('钩子', await ev('String(window.__gateOpenedCalls || 0)'), '载入页还在', await ev('!!document.getElementById("gate")'));
console.log(errs.length ? errs.join('\n') : '没有报错');
await send('Page.close').catch(() => {});
process.exit(0);
