// 片头样片的分镜：连上无头 Chrome（9334），照原尺寸在几个时刻各截一帧。页面带 ?sim=1，时间只在 __pv.tick 里走。
//   node shots_pv.mjs <宽> <高> <输出目录> <时刻…>        时刻写秒数，或者写 第几句（b12 就是第 12 句开头往后 60% 处；b12@0.2 是 20% 处）
//   node shots_pv.mjs <宽> <高> <输出目录> list            只列出每一句从第几秒起
// 无头 Chrome 的起法见 门面重做_方向稿.md 第十二节第十七版那一块；本地服务器是 .claude/launch.json 的 front-pv（8767）。
import fs from 'node:fs';
const [W, H, OUT, ...whens] = [+process.argv[2], +process.argv[3], process.argv[4], ...process.argv.slice(5)];
const PORT = 9334, URL = 'http://localhost:8767/local.html?sim=1' + (process.env.PV_Q ? '&' + process.env.PV_Q : '');
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), waiters = [], errs = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) errs.push(m.params.type + ' ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 400));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function ev(expr) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 120000 });
  if (r.result && r.result.exceptionDetails) { console.log('ERR', JSON.stringify(r.result.exceptionDetails).slice(0, 800)); process.exit(1); }
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: +(process.env.PV_DPR || 1), mobile: W < 700 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(20000)]);
await sleep(1500);
// 等图都到
for (let i = 0; i < 40; i++) { const ok = await ev(`return window.__pv ? Object.values(__pv.imgs).every(o => o.ok || o.bad) : false`); if (ok) break; await sleep(300); }
console.log('开了', await ev(`return JSON.stringify({ iw: innerWidth, ih: innerHeight, gl: __pv.gl, total: +__pv.total.toFixed(1), beats: __pv.beats.length, bad: Object.entries(__pv.imgs).filter(([k, o]) => o.bad).map(([k]) => k) })`));
if (whens[0] === 'list') {
  console.log(await ev(`return __pv.beats.map(b => b.i + ' ' + b.t0.toFixed(1) + ' +' + b.dur.toFixed(1) + ' ' + b.kind + ' ' + (b.plate || '') + ' ' + (b.text || (b.era !== undefined ? '第' + (b.era + 1) + '处' : ''))).join('\\n')`));
} else {
  for (const w of whens) {
    const m = /^b(\d+)(?:@([\d.]+))?$/.exec(w);
    const expr = m ? `const b = __pv.beats[${+m[1]}]; const t = b.t0 + b.dur * ${m[2] ? +m[2] : 0.6};` : `const t = ${+w};`;
    const t = await ev(`${expr} __pv.seek(Math.max(0, t - 1.6)); await __pv.tick(1600); return +__pv.T.toFixed(2)`);
    await sleep(350);
    const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 90 });
    const name = `${OUT}/pv_${W}x${H}_${w.replace('@', '_')}.jpg`;
    fs.writeFileSync(name, Buffer.from(r.result.data, 'base64'));
    console.log('截', w, '在', t, '秒');
  }
}
if (errs.length) console.log('页面报的：\n' + [...new Set(errs)].slice(0, 12).join('\n')); else console.log('页面没有报错');
ws.close();
