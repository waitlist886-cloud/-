// 连上一直开着的无头 Chrome（--remote-debugging-port=9333），对头一个页面干一件事：
//   node cdp.mjs eval "<js>"             执行一段 JS（可以 await），打印返回值
//   node cdp.mjs file <脚本.js>          同上，脚本从文件读
//   node cdp.mjs shot <输出.png> [w h]   截当前视口
//   node cdp.mjs upload <css选择器> <文件>   给 <input type=file> 塞文件（DOM.setFileInputFiles），触发 change
//   node cdp.mjs downloads <目录>        下载落到这个目录
//   node cdp.mjs nav <url>               打开网址，等 load
import fs from 'node:fs';
import path from 'node:path';
const PORT = process.env.CDP_PORT || 9333;
const [cmd, a1, a2, a3] = process.argv.slice(2);
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), waiters = [];
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } else for (const w of waiters) if (w.ev === m.method) w.fn(m); };
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function evaluate(expr) {
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true, timeout: 600000 });
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 1500);
  const v = r.result && r.result.result;
  return v ? (v.value !== undefined ? v.value : v.description) : JSON.stringify(r).slice(0, 500);
}
if (cmd === 'eval') console.log(await evaluate(a1));
else if (cmd === 'file') console.log(await evaluate(fs.readFileSync(a1, 'utf8')));
else if (cmd === 'shot') {
  if (a2) await send('Emulation.setDeviceMetricsOverride', { width: +a2, height: +a3, deviceScaleFactor: 1, mobile: false });
  const r = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(a1, Buffer.from(r.result.data, 'base64'));
  console.log('ok', a1);
} else if (cmd === 'clip') {
  // node cdp.mjs clip <输出.png> x y w h scale   截地图上一块（页面坐标就是地图坐标），按倍数放大
  const [x, y, w, h, sc] = process.argv.slice(4).map(Number);
  const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x, y, width: w, height: h, scale: sc } });
  if (!r.result) { console.log('截不了', JSON.stringify(r).slice(0, 300)); process.exit(1); }
  fs.writeFileSync(a1, Buffer.from(r.result.data, 'base64'));
  console.log('ok', a1);
} else if (cmd === 'drag') {
  // node cdp.mjs drag x1 y1 x2 y2 [步数] [滚轮]   在页面上按住左键拖一段（转 3D 地球用），最后可以滚几下滚轮缩放
  const [x1, y1, x2, y2, steps = 20, wheel = 0] = process.argv.slice(3).map(Number);
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: x1, y: y1 });
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: x1, y: y1, button: 'left', buttons: 1, clickCount: 1 });
  for (let k = 1; k <= steps; k++) { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: x1 + (x2 - x1) * k / steps, y: y1 + (y2 - y1) * k / steps, button: 'left', buttons: 1 }); await sleep(30); }
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: x2, y: y2, button: 'left', buttons: 0, clickCount: 1 });
  if (wheel) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: x2, y: y2, deltaX: 0, deltaY: wheel }); }
  await sleep(1500);
  console.log('drag ok');
} else if (cmd === 'upload') {
  await send('DOM.enable');
  const doc = await send('DOM.getDocument', { depth: -1, pierce: true });
  const q = await send('DOM.querySelector', { nodeId: doc.result.root.nodeId, selector: a1 });
  if (!q.result || !q.result.nodeId) { console.log('没找到', a1, JSON.stringify(q).slice(0, 300)); process.exit(1); }
  const r = await send('DOM.setFileInputFiles', { nodeId: q.result.nodeId, files: [path.resolve(a2)] });
  console.log('upload', JSON.stringify(r).slice(0, 200));
} else if (cmd === 'downloads') {
  fs.mkdirSync(a1, { recursive: true });
  const r = await send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: path.resolve(a1) });
  console.log('downloads', JSON.stringify(r).slice(0, 200));
} else if (cmd === 'nav') {
  await send('Page.enable');
  const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
  await send('Page.navigate', { url: a1 });
  await Promise.race([loaded, sleep(60000)]);
  console.log('nav ok');
}
ws.close();
