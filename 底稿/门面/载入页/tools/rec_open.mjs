// 只录开门那一段（11-26 夜，“被吸进门里”那一拍）：录屏在开门那一下页面最忙的时候会好几百毫秒不推帧，录出来一顿一顿的，不是页面本身卡。
// 这里换个办法：地址带 ?gslow=4 让载入页整体慢四倍，逐张截图，每张记下真实时刻，时长再除以四，拼回原速。
//   node 底稿/门面/载入页/tools/rec_open.mjs <宽> <高> <输出目录>
//   python -I -X utf8 底稿/门面/载入页/tools/make_video.py <输出目录> <宽> <高> <输出.mp4> <ffmpeg>
import fs from 'node:fs';
import path from 'node:path';
const [W, H, DIR] = [+process.argv[2], +process.argv[3], process.argv[4]];
const K = 4, PORT = +(process.env.CDP_PORT || 9351);
fs.mkdirSync(DIR, { recursive: true });
for (const f of fs.readdirSync(DIR)) if (/^f\d+\.jpg$/.test(f)) fs.unlinkSync(path.join(DIR, f));
const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(tab.webSocketDebuggerUrl); await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pend = new Map();
const send = (m, p = {}) => new Promise((r) => { const id = ++seq; pend.set(id, r); ws.send(JSON.stringify({ id, method: m, params: p })); });
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (e) => { const r = await send('Runtime.evaluate', { expression: e, returnByValue: true }); return r.result.result && r.result.result.value; };
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 768 });
await send('Page.navigate', { url: 'http://127.0.0.1:8773/' + encodeURIComponent('小样_外壳') + '/thin_local.html?gslow=' + K + '&t=' + Date.now() });
for (let i = 0; i < 400; i++) { if ((await ev('window.__gate && __gate.state().phase')) >= 4) break; await sleep(300); }
await sleep(2500 * K / 2);
const shots = [];
const grab = async () => { const s = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); const f = 'f' + String(shots.length).padStart(5, '0') + '.jpg'; fs.writeFileSync(path.join(DIR, f), Buffer.from(s.result.data, 'base64')); shots.push([f, Date.now()]); };
for (let i = 0; i < 6; i++) await grab();          // 门前停着的一小段
await ev('__gate.open(false)');
const t0 = Date.now();
while (Date.now() - t0 < 5200 * K / 2) await grab();
const lines = [];
for (let i = 0; i < shots.length; i++) {
  const d = i + 1 < shots.length ? (shots[i + 1][1] - shots[i][1]) / 1000 / K : 0.4;
  lines.push(`file '${shots[i][0]}'`, `duration ${d.toFixed(4)}`);
}
lines.push(`file '${shots[shots.length - 1][0]}'`);
fs.writeFileSync(path.join(DIR, 'list.txt'), lines.join('\n') + '\n');
const span = (shots[shots.length - 1][1] - shots[0][1]) / 1000 / K;
console.log('截了', shots.length, '张，折回原速', span.toFixed(2), '秒，合', (shots.length / span).toFixed(0), '帧一秒');
await send('Page.close').catch(() => {}); process.exit(0);
