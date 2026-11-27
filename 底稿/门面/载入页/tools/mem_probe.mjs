// 量一下一页的渲染进程吃多少内存（11-27 止血那一轮查“App 里被踢出来”）：开门、进月银纪、回牌桌，每一步记渲染进程的内存（CDP 的 SystemInfo.getProcessInfo 没有内存，这里取 Performance.getMetrics 的 JS 堆，另由外面拿 PowerShell 量进程）。
//   node mem_probe.mjs <查询串>      （CDP_PORT 默认 9351）
import { spawnSync } from 'node:child_process';
const PS = "(Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object { $_.CommandLine -match 'chrome_mute' -and $_.CommandLine -match 'type=renderer' } | ForEach-Object { [math]::Round($_.PrivatePageCount/1MB) }) -join ','";
const PORT = +(process.env.CDP_PORT || 9351), QS = process.argv[2] || '';
const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(tab.webSocketDebuggerUrl); await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pend = new Map(), ctxs = [];
const send = (m, p = {}) => new Promise((r) => { const id = ++seq; pend.set(id, r); ws.send(JSON.stringify({ id, method: m, params: p })); });
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); return; } if (m.method === 'Runtime.executionContextCreated') ctxs.push(m.params.context); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const evIn = async (expr, x) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, ...(x ? { contextId: x.id } : {}) }); return r.result && r.result.result ? r.result.result.value : undefined; };
await send('Page.enable'); await send('Runtime.enable'); await send('Performance.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 800, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: 'http://127.0.0.1:8773/' + encodeURIComponent('小样_外壳') + '/thin_local.html?gmin=4&bgmtest' + QS + '&t=' + Date.now() });
let S = null; for (let i = 0; i < 120 && !S; i++) { for (const x of [...ctxs]) if ((await evIn('!!window.__bgm', x)) === true) { S = x; break; } await sleep(250); }
const mark = async (tag) => { const m = (await send('Performance.getMetrics')).result.metrics; const g = (k) => (m.find((x) => x.name === k) || {}).value || 0; const rss = (spawnSync('powershell', ['-NoProfile', '-Command', PS]).stdout || '').toString().trim();
  console.log('MARK', tag, '渲染进程私有内存MB', rss, 'JS堆', (g('JSHeapUsedSize') / 1048576).toFixed(0) + 'MB', (await evIn('JSON.stringify({m: __bgm.state().mode, n: __bgm.state().node || __bgm.state().rel, b: __bgm.state().bufs})', S))); await sleep(3500); };
for (let i = 0; i < 80; i++) { if ((await evIn('window.__gate && __gate.state && __gate.state().phase', S)) >= 4) break; await sleep(250); }
await mark('门前');
const d = await evIn('(() => { const b = document.querySelector("#gate .g-door").getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; })()', S);
for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x: d[0], y: d[1], button: 'left', clickCount: 1 });
await sleep(9000); await mark('开门后');
await evIn('Shell.openBook("moon"); 1', S); await sleep(9000); await mark('月银纪');
await evIn('Shell.toTable(); 1', S); await sleep(6000); await mark('回牌桌');
await send('Page.close').catch(() => {}); process.exit(0);
