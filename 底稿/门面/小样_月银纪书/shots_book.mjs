// 月银纪的墙：连上无头 Chrome（9335），照原尺寸摆几个样子各截一帧。页面带 ?sim=1，时间只在 __bk.tick 里走。
//   node shots_book.mjs <宽> <高> <输出目录> <名字>=<在页面里跑的一句> …
//   名字后头写 @毫秒 是摆好以后再走多久才截（不写是 1500），比如 b1@0=…
//   例：node shots_book.mjs 1920 945 out "a=__bk.go(6);__bk.see(0,8);__bk.torch(900,420)" "page=__bk.open(6)"
// 本地服务器是 .claude/launch.json 的 front-book（8768）。环境变量 BK_Q 是地址上多带的参数（比如 nogl=1），BK_DPR 是屏幕倍数，BK_WAIT 是截以前再等多少毫秒（字是照真实时钟淡进来的，要等）。
import fs from 'node:fs';
const [W, H, OUT, ...shots] = [+process.argv[2], +process.argv[3], process.argv[4], ...process.argv.slice(5)];
const PORT = 9335, URL = 'http://localhost:8768/local.html?sim=1' + (process.env.BK_Q ? '&' + process.env.BK_Q : '');
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), waiters = [], errs = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 500));
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) errs.push(m.params.type + ' ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 500));
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
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: +(process.env.BK_DPR || 1), mobile: W < 700 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(20000)]);
for (let i = 0; i < 50; i++) { if (await ev('return !!(window.__bk && __bk.s.W)')) break; await sleep(200); }
console.log('开了', JSON.stringify(await ev('const s = __bk.s; return { W: s.W, H: s.H, wide: s.wide, TW: s.TW, TH: s.TH, GAP: s.GAP, TOTAL: Math.round(s.TOTAL), gl: s.gl }')));
for (const sh of shots) {
  const k = sh.indexOf('='); const nm = sh.slice(0, k).split('@'), name = nm[0], settle = nm[1] === undefined ? 1500 : +nm[1], expr = sh.slice(k + 1);
  await ev(expr + '; return 1');
  for (let i = 0; i < 60; i++) { await ev('__bk.s.pageOpen < 0 && __bk.tick(16); return 1'); if (await ev('return __bk.ready()')) break; await sleep(150); }
  if (settle > 0) await ev(`if (__bk.s.pageOpen < 0) __bk.tick(${settle}); return 1`);
  await sleep(+(process.env.BK_WAIT || 0) || (name.startsWith('page') ? 1400 : 350));
  const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 88 });
  fs.writeFileSync(`${OUT}/bk_${W}x${H}_${name}.jpg`, Buffer.from(r.result.data, 'base64'));
  console.log('截', name, JSON.stringify(await ev('const s = __bk.s; return { cam: Math.round(s.cam), f: s.f, brk: +s.brk.toFixed(2), loaded: s.loaded, bad: s.bad, page: s.pageOpen }')));
}
console.log(errs.length ? '页面报的：\n' + [...new Set(errs)].slice(0, 12).join('\n') : '页面没有报错');
ws.close();
