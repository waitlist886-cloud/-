// 载入页录像（第二版，11-26 夜）：无头 Chrome 的 Page.startScreencast 把每一帧都推过来（不是隔一阵截一张），存成 jpg 加时间戳，
// 走到门口停两秒、点门、录到牌桌出来，再交给 ffmpeg 照时间戳拼成 30 帧的 mp4。
//   node 底稿/门面/载入页/tools/rec_gate.mjs <宽> <高> <输出目录> [慢网=0|1] [地址参数]
//   然后：ffmpeg -f concat -safe 0 -i <输出目录>/list.txt -vf "fps=30,format=yuv420p" -c:v libx264 -crf 22 <输出.mp4>
// Chrome 要先起：chrome --headless=new --remote-debugging-port=$CDP_PORT（默认 9351）；本地 front-cors 8773 起着。
import fs from 'node:fs';
import path from 'node:path';
const [W, H, DIR] = [+process.argv[2], +process.argv[3], process.argv[4]];
const SLOWNET = process.argv[5] === '1', QS = process.argv[6] || '';
const PORT = +(process.env.CDP_PORT || 9351);
fs.mkdirSync(DIR, { recursive: true });
for (const f of fs.readdirSync(DIR)) if (/^f\d+\.jpg$/.test(f)) fs.unlinkSync(path.join(DIR, f));
const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(tab.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(); const frames = [];
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Page.screencastFrame') {
    const n = frames.length, f = path.join(DIR, 'f' + String(n).padStart(5, '0') + '.jpg');
    fs.writeFileSync(f, Buffer.from(m.params.data, 'base64'));
    frames.push([path.basename(f), m.params.metadata.timestamp]);
    ws.send(JSON.stringify({ id: ++seq, method: 'Page.screencastFrameAck', params: { sessionId: m.params.sessionId } }));
  }
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
const mobile = W < 768;
// 录屏录的是整个窗口：窗口先撑到比要的屏幕大，帧里左上角那一块就是页面（make_video.py 照宽高裁）
try { const wi = await send('Browser.getWindowForTarget', { targetId: tab.id }); await send('Browser.setWindowBounds', { windowId: wi.result.windowId, bounds: { width: Math.max(W, 800) + 60, height: H + 260 } }); } catch (e) {}
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile });
if (SLOWNET) await send('Network.emulateNetworkConditions', { offline: false, latency: 300, downloadThroughput: 1.6 * 1024 * 1024 / 8, uploadThroughput: 750 * 1024 / 8 });
await send('Page.startScreencast', { format: 'jpeg', quality: 82, maxWidth: 4000, maxHeight: 4000, everyNthFrame: 1 });
const t0 = Date.now();
await send('Page.navigate', { url: 'http://127.0.0.1:8773/' + encodeURIComponent('小样_外壳') + '/thin_local.html?t=' + Date.now() + (QS ? '&' + QS : '') });
let s = null;
while (Date.now() - t0 < (SLOWNET ? 120000 : 45000)) {
  try { s = JSON.parse(await ev('window.__gate ? JSON.stringify(__gate.state()) : "null"')); } catch (e) { s = null; }
  if (s && s.phase >= 4) break;
  await sleep(250);
}
console.log('到门口', Date.now() - t0, 'ms', JSON.stringify(s));
await sleep(2400);
const r = await ev('(() => { const d = document.querySelector("#gate .g-door").getBoundingClientRect(); return [d.left + d.width / 2, d.top + d.height / 2]; })()');
await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: r[0], y: r[1], button: 'left', clickCount: 1 });
await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: r[0], y: r[1], button: 'left', clickCount: 1 });
await sleep(4500);
await send('Page.stopScreencast');
await sleep(300);
// ffmpeg 的 concat 清单：每一帧照到下一帧的时间差显示
const lines = [];
for (let i = 0; i < frames.length; i++) {
  const d = i + 1 < frames.length ? Math.max(0.001, frames[i + 1][1] - frames[i][1]) : 0.5;
  lines.push(`file '${frames[i][0]}'`, `duration ${d.toFixed(4)}`);
}
lines.push(`file '${frames[frames.length - 1][0]}'`);
fs.writeFileSync(path.join(DIR, 'list.txt'), lines.join('\n') + '\n');
const span = frames[frames.length - 1][1] - frames[0][1];
console.log('帧', frames.length, '时长', span.toFixed(1), 's', '平均', (frames.length / span).toFixed(1), 'fps');
await send('Page.close').catch(() => {});
process.exit(0);
