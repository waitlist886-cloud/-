// 迷宫纪的书截几帧：井口上头、几圈里停下来的样子、井底、时代页、点开的壁画和委托单。
//   node shots_maze.mjs <宽> <高> <输出目录>
// 本地服务器 front-maze（8771），无头 Chrome 在 9337。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4]];
const PORT = 9337, ADDR = 'http://localhost:8771/local.html?sim=1';
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), waiters = [];
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; } for (const w of waiters) if (w.ev === m.method) w.fn(m); };
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 700 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR });
await Promise.race([loaded, sleep(15000)]);
for (let i = 0; i < 60; i++) { if (await ev('return !!(window.__mz && __mz.state)')) break; await sleep(200); }
fs.mkdirSync(OUT, { recursive: true });
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); fs.writeFileSync(`${OUT}/${name}.jpg`, Buffer.from(r.result.data, 'base64')); console.log(name); };
const at = async (v, settle = 30) => {
  await ev(`__mz.go(${v}); return 1`);
  for (let i = 0; i < settle; i++) { await ev('__mz.tick(40); return 1'); await sleep(40); }
};
const K = await ev('return __mz.state().K');
await at(-1); await shot('1_井口');
await at(0); await shot('2_地开那一夜');
await at(3); await shot('3_探井');
await at(14); await shot('4_繁荣');
await at(22); await shot('5_深井');
await at(36); await shot('6_黑潮');
await at(41); await shot('7_垂暮');
await at(K, 60); await sleep(1500); await shot('8_井底');
await at(30); await ev('__mz.openMural(30); return 1'); await sleep(900); await shot('9_点开壁画');
await ev('__mz.closeMural(); return 1'); await sleep(400);
await ev('__mz.openComm(12); return 1'); await sleep(700); await shot('10_委托单');
await ev('__mz.closeComm(); return 1'); await sleep(400);
await ev('__mz.openEra(4); return 1'); await sleep(1600); await shot('11_时代页');
ws.close();
