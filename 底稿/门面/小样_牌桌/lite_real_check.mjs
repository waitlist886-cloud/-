// 补两样别的脚本没管的：轻的画法（?lite=1，没有 WebGL 的那一路）逐帧走一遍；真实时钟加点按（手机尺寸是触摸，别的是鼠标点）走一遍。连无头 Chrome（9334），收报错。
//   node lite_real_check.mjs <lite|real> <宽> <高> <输出目录> [选哪一条 0..3]      （输出目录要先建好；无头 Chrome 的起法在 门面重做_方向稿.md 第十二节第十七版那一块）
import fs from 'node:fs';
const [mode, W, H, OUT] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5]];
const K = +(process.argv[6] ?? 1);
const PORT = 9334;
const URL = mode === 'lite' ? 'http://localhost:8765/local.html?sim=1&lite=1' : 'http://localhost:8765/local.html?full=1';
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), waiters = [], errs = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('EXC ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) errs.push(m.params.type + ' ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 300));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') errs.push('LOG ' + m.params.entry.text.slice(0, 300) + ' ' + (m.params.entry.url || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function ev(expr) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 120000 });
  if (r.result && r.result.exceptionDetails) { console.log('ERR', JSON.stringify(r.result.exceptionDetails).slice(0, 800)); process.exit(1); }
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.result.data, 'base64'));
  console.log('shot', name);
}
await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
const phone = W < 600;
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: phone ? 2 : 1, mobile: phone });
if (phone) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(20000)]);
await sleep(2500);
const tag = `${mode}_${W}x${H}`;
if (mode === 'lite') {
  console.log('open', await ev(`await __tb.tick(300); return JSON.stringify({ cls: document.querySelector('#world').className, rigs: !!__tb.rigs, note: (document.querySelector('#note') || {}).textContent || '' })`));
  await ev(`await __tb.tick(4000); let n = 0; while (__tb.stage !== 'choose' && n++ < 600) await __tb.tick(50); await __tb.tick(400);`); await sleep(2600); await shot(`${tag}_1_四张牌背`);
  if (phone) await ev(`__tb.tap(${K}); await __tb.tick(700);`); else await ev(`__tb.select(${K}, true); await __tb.tick(700);`);
  await sleep(2200); await shot(`${tag}_2_选中`);
  await ev(`__tb.tap(${K}); await __tb.tick(900);`); await sleep(1200); await shot(`${tag}_3_收成牌`);
  await ev(`await __tb.tick(1400);`); await sleep(1200); await shot(`${tag}_4_立住`);
  await ev(`let n = 0; while (__tb.stage !== 'done' && n++ < 400) await __tb.tick(50); await __tb.tick(600);`); await sleep(3200); await shot(`${tag}_5_这一纪`);
  console.log('end', await ev(`return JSON.stringify([__tb.stage, !!__tb.rigs])`));
} else {
  // 真实时钟：等四条摆好，点一下撑开，再点一下选定，等进这一纪，再点“再选一纪”
  let n = 0, stage = '';
  while (n++ < 50) { await sleep(600); stage = await ev(`return __tb.stage`); if (stage === 'choose') break; }
  console.log('stage', stage);
  await sleep(1200); await shot(`${tag}_1_四张牌背`);
  const pt = JSON.parse(await ev(`const r = document.querySelectorAll('.band')[${K}].getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height / 2])`));
  const tap = async (x, y) => {
    if (phone) { await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] }); await sleep(40); await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); }
    else { await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', buttons: 1, clickCount: 1 }); await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', buttons: 0, clickCount: 1 }); }
  };
  await tap(pt[0], pt[1]); await sleep(1400);
  console.log('tap1', await ev(`return JSON.stringify([__tb.stage, __tb.bands.map(b => Math.round(b.h || b.w)), document.querySelector('#sub').textContent])`));
  await shot(`${tag}_2_选中`);
  const pt2 = JSON.parse(await ev(`const r = document.querySelectorAll('.band')[${K}].getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height / 2])`));
  await tap(pt2[0], pt2[1]);
  n = 0;
  while (n++ < 40) { await sleep(400); stage = await ev(`return __tb.stage`); if (stage === 'done') break; }
  await sleep(2500); await shot(`${tag}_3_这一纪`);
  console.log('end', stage, await ev(`return JSON.stringify({ step: localStorage.getItem('tb_step'), lite: localStorage.getItem('tb_lite'), rigs: !!__tb.rigs })`));
  const btn = JSON.parse(await ev(`const r = document.querySelector('#again').getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height / 2])`));
  await tap(btn[0], btn[1]); await sleep(1800);
  console.log('again', await ev(`return JSON.stringify([__tb.stage, __tb.bands.map(b => Math.round(b.h || b.w))])`));
  await shot(`${tag}_4_再选一纪`);
}
console.log('errors', errs.length, errs.slice(0, 8));
ws.close();
