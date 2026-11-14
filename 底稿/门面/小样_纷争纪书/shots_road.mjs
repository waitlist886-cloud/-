// 纷争纪的路：连上无头 Chrome（9335），照原尺寸摆几个样子各截一帧。
//   node shots_road.mjs <宽> <高> <输出目录> <名字>=<在页面里跑的一句> …
//   名字后头写 @毫秒 是摆好以后再等多久才截（不写是 1600；牌翻面、字淡进来都是照真实时钟走的，要等）
//   例：node shots_road.mjs 1920 945 out "a=__bk.go(3)" "page=__bk.open(3)"
// 本地服务器是 .claude/launch.json 的 front-strife（8769）。环境变量 BK_Q 是地址上多带的参数（比如 grid=1），BK_DPR 是屏幕倍数。
// 地址带 skip=1：不放进来的那一下，直接在路上。页面用真实时钟（不带 sim），截以前等够时间就行。
import fs from 'node:fs';
const [W, H, OUT, ...shots] = [+process.argv[2], +process.argv[3], process.argv[4], ...process.argv.slice(5)];
const PORT = 9335, URL = 'http://localhost:8769/local.html?skip=1' + (process.env.BK_Q ? '&' + process.env.BK_Q : '');
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), waiters = [], errs = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 500));
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) errs.push(m.params.type + ' ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 500));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) errs.push(m.params.response.status + ' ' + m.params.response.url.replace('http://localhost:8769/', ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function ev(expr) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 120000 });
  if (r.result && r.result.exceptionDetails) { console.log('ERR', JSON.stringify(r.result.exceptionDetails).slice(0, 900)); process.exit(1); }
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
fs.mkdirSync(OUT, { recursive: true });
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: +(process.env.BK_DPR || 1), mobile: W < 700 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(20000)]);
for (let i = 0; i < 60; i++) { if (await ev('return !!(window.__bk && __bk.s.W)')) break; await sleep(200); }
console.log('开了', JSON.stringify(await ev('const s = __bk.s; return { W: s.W, H: s.H, wide: s.wide, PWd: s.PWd, CW: s.CW, CH: s.CH, TOTAL: Math.round(s.TOTAL) }')));
for (const sh of shots) {
  const k = sh.indexOf('='); const nm = sh.slice(0, k).split('@'), name = nm[0], settle = nm[1] === undefined ? 1600 : +nm[1], expr = sh.slice(k + 1);
  await ev(expr + '; return 1');
  for (let i = 0; i < 80; i++) { await sleep(150); if (await ev('return __bk.ready()')) break; }
  await sleep(settle);
  const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 88 });
  fs.writeFileSync(`${OUT}/rd_${W}x${H}_${name}.jpg`, Buffer.from(r.result.data, 'base64'));
  console.log('截', name, JSON.stringify(await ev('const s = __bk.s; return { cam: Math.round(s.cam), f: s.f, seen: s.seen, parts: s.parts, page: s.pageOpen, light: s.light, frames: s.frames }')));
}
console.log(errs.length ? '页面报的：\n' + [...new Set(errs)].slice(0, 12).join('\n') : '页面没有报错');
ws.close();
