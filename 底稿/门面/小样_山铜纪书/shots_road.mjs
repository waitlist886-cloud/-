// 山铜纪的路：连上无头 Chrome（9336），照原尺寸摆几个样子各截一帧。
//   node shots_road.mjs <宽> <高> <输出目录> <名字>=<在页面里跑的一句> …
//   名字后头写 @毫秒 是摆好以后再等多久才截（不写是 900；碑面亮起来、翻面照真实时钟走，要等）
//   例：node shots_road.mjs 1920 945 out "gate=__bk.z(0)" "meet=__bk.z(436)" "a=__bk.go(3)" "big=__bk.go(3);__bk.stele(3)" "page=__bk.open(3)"
//   __bk.z(远近) 把镜头摆到路上那一处，__bk.go(第几块碑) 走到那一块跟前，__bk.tick(毫秒) 往后走几帧。
// 本地服务器是 .claude/launch.json 的 front-bronze（8770）。环境变量 BK_Q 是地址上多带的参数（nogl=1 是 2D 的退路），BK_DPR 是屏幕倍数。
import fs from 'node:fs';
const [W, H, OUT, ...shots] = [+process.argv[2], +process.argv[3], process.argv[4], ...process.argv.slice(5)];
const PORT = 9336, URL = 'http://localhost:8770/local.html?skip=1&sim=1' + (process.env.BK_Q ? '&' + process.env.BK_Q : '');
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), waiters = [], errs = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 500));
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) errs.push(m.params.type + ' ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 500));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) errs.push(m.params.response.status + ' ' + m.params.response.url.replace('http://localhost:8770/', ''));
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
console.log('开了', JSON.stringify(await ev('const s = __bk.s; return { W: s.W, H: s.H, mode: s.mode, NS: s.NS, ZS: s.ZS, ZG: s.ZG }')));
for (const sh of shots) {
  const k = sh.indexOf('='); const nm = sh.slice(0, k).split('@'), name = nm[0], settle = nm[1] === undefined ? 900 : +nm[1], expr = sh.slice(k + 1);
  await ev(expr + '; return 1');
  for (let i = 0; i < 80; i++) { await ev('__bk.tick(32); return 1'); await sleep(120); if (await ev('return __bk.ready()')) break; }
  await ev('__bk.tick(64); return 1');
  await sleep(settle);
  await ev('__bk.tick(16); return 1');
  const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 88 });
  fs.writeFileSync(`${OUT}/br_${W}x${H}_${name}.jpg`, Buffer.from(r.result.data, 'base64'));
  console.log('截', name, JSON.stringify(await ev('const s = __bk.s; return { z: +s.camZ.toFixed(1), year: s.year, page: s.page, focus: s.focus, lbl: s.lbl, cam: s.cam, open: s.pageOpen, stv: s.stOpen, walkers: __bk.walkers(), shown: __bk.shown().length }')));
}
console.log(errs.length ? '页面报的：\n' + [...new Set(errs)].slice(0, 12).join('\n') : '页面没有报错');
ws.close();
