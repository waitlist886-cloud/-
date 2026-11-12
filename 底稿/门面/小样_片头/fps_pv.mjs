// 片头样片在真实时钟下跑一段：数帧率，收报错。无头 Chrome 是软件渲染，帧率只当下限看。
//   node fps_pv.mjs <宽> <高> <从第几秒起> [地址上多带的参数，比如 nogl=1]
const [W, H, T0, EXTRA] = [+process.argv[2], +process.argv[3], +process.argv[4] || 0, process.argv[5] || ''];
const PORT = 9334, URL = `http://localhost:8767/local.html?t=${T0}` + (EXTRA ? '&' + EXTRA : '');
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) errs.push(m.params.type + ' ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(() => { ${expr} })()`, returnByValue: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: W < 700 ? 2 : 1, mobile: W < 700 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(15000)]); await sleep(3000);
const a = await ev('return [__pv.frames, __pv.T, __pv.gl]'); await sleep(5000);
const b = await ev('return [__pv.frames, __pv.T, __pv.gl]');
console.log(`${W}x${H} 从 ${T0} 秒起 ${EXTRA}：五秒里 ${b[0] - a[0]} 帧（每秒 ${((b[0] - a[0]) / 5).toFixed(1)}），片子走了 ${(b[1] - a[1]).toFixed(2)} 秒，WebGL ${b[2]}`);
console.log(errs.length ? '页面报的：\n' + [...new Set(errs)].slice(0, 8).join('\n') : '页面没有报错');
ws.close();
