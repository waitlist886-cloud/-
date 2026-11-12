// 本地验“真牌桌装进介绍页”那一张：无头 Chrome（9334）开假的日里壳，真实时钟走一遍（发牌、选、拿、进这一纪），再点右上角的“探”把情况填进输入框，再换轻量画法走一遍。
//   node table_test.mjs <宽> <高> <输出目录> [选哪一条] [端口 8766]
// 先起的两样同 probe_test.mjs。无头 Chrome 的触摸模拟在单独进程的那一格里把合成的点击算偏一个顶栏的高（64），小钮点不中，
// 所以右上角“探”那几个钮改用鼠标点（真机没这个毛病）；画带够大，照旧用触摸。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4]];
const K = +(process.argv[5] ?? 1), SPORT = process.argv[6] || '8766';
const PORT = 9334, URL = `http://localhost:${SPORT}/host.html?src=table_intro.html`;
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), errs = [], ctxs = [], kids = [], waiters = [];
const send = (method, params = {}, sessionId) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params })); });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') { const sid = m.params.sessionId; kids.push({ sid, info: m.params.targetInfo }); send('Runtime.enable', {}, sid); send('Log.enable', {}, sid); }
  if (m.method === 'Target.detachedFromTarget') { const i = kids.findIndex((k) => k.sid === m.params.sessionId); if (i >= 0) kids.splice(i, 1); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.exceptionThrown') errs.push('EXC ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) errs.push('console.' + m.params.type + ' ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 240));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') errs.push('LOG ' + m.params.entry.text.slice(0, 170) + ' ' + (m.params.entry.url || '').slice(-40));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function evIn(expr, sid, contextId) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 30000, ...(contextId ? { contextId } : {}) }, sid || undefined);
  if (!r.result) return 'ERR ' + JSON.stringify(r.error || r).slice(0, 200);
  if (r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 400);
  const v = r.result.result; return v ? v.value : undefined;
}
const top = (expr) => evIn(expr);
let shotN = 0;
async function shot(name) { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 84 }); fs.writeFileSync(`${OUT}/${String(++shotN).padStart(2, '0')}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); console.log('shot', name); }
await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
const phone = W < 600;
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: phone ? 2 : 1, mobile: phone });
if (phone) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
const t0 = Date.now();
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(20000)]);
async function frameCtx() {
  for (const k of kids) { const v = await evIn(`return !!document.getElementById('pbChip')`, k.sid); if (v === true) return { sid: k.sid }; }
  for (const x of ctxs) { if (x.sid) continue; const v = await evIn(`return !!document.getElementById('pbChip')`, '', x.c.id); if (v === true) return { sid: '', id: x.c.id }; }
  return null;
}
let F = null;
async function attach() { F = null; for (let i = 0; i < 40 && !F; i++) { F = await frameCtx(); if (!F) await sleep(300); } if (!F) { console.log('找不到介绍页那一格'); console.log(errs.slice(0, 8)); process.exit(1); } }
await attach();
console.log('介绍页那一格：', F.sid ? '单独的目标' : '同一个进程里', '载入', ((Date.now() - t0) / 1000).toFixed(1) + 's');
const fev = (expr) => evIn(expr, F.sid, F.id);
const frameTop = JSON.parse(await top(`const r = document.getElementById('f').getBoundingClientRect(); return JSON.stringify([r.left, r.top, r.width, r.height])`));
console.log('介绍页那一格的位置和大小', frameTop);
async function tapAt(x, y, mouse) {
  if (phone && !mouse) { await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] }); await sleep(40); await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); }
  else { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', buttons: 1, clickCount: 1 }); await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', buttons: 0, clickCount: 1 }); }
}
async function tapSel(sel, mouse) { const r = JSON.parse(await fev(`const b = document.querySelector(${JSON.stringify(sel)}).getBoundingClientRect(); return JSON.stringify([b.left + b.width / 2, b.top + b.height / 2])`)); await tapAt(frameTop[0] + r[0], frameTop[1] + r[1], mouse); }
async function run(tag) {
  let n = 0, stage = '';
  while (n++ < 60) { await sleep(600); stage = await fev(`return window.__tb ? __tb.stage : 'no-tb'`); if (n === 5) await shot(tag + '_开场'); if (stage === 'choose') break; }
  console.log(tag, 'stage', stage, '世界', await fev(`return document.getElementById('world').className + ' rigs=' + !!(window.__tb && __tb.rigs)`));
  await sleep(1300); await shot(tag + '_四张牌背');
  await tapSel(`.band:nth-of-type(${K + 1})`); await sleep(1500);
  console.log(tag, '点一下', await fev(`return JSON.stringify([__tb.stage, __tb.bands.map(b => Math.round(b.h || b.w)), document.querySelector('#sub').textContent])`));
  await shot(tag + '_选中');
  await tapSel(`.band:nth-of-type(${K + 1})`);
  await sleep(1500); await shot(tag + '_拿牌');
  n = 0; while (n++ < 40) { await sleep(400); stage = await fev(`return __tb.stage`); if (stage === 'done') break; }
  await sleep(2500); await shot(tag + '_这一纪');
  console.log(tag, 'end', stage);
}
await run('完整');
await tapSel('#pbChip', true); await sleep(1200); await shot('探_点开');
await tapSel('#pbFill', true); await sleep(500);
console.log('---- 填进输入框的 ----\n' + await top(`return window.__last || '(没收到)'`));
// 换轻量画法：页面自己重载，那一格的执行环境会换
await tapSel('#pbLite', true); await sleep(2500);
ctxs.length = 0; await send('Runtime.disable'); await send('Runtime.enable'); for (const k of kids) { await send('Runtime.disable', {}, k.sid); await send('Runtime.enable', {}, k.sid); }
await attach();
console.log('重载以后：', await fev(`return 'name=' + window.name + ' lite=' + !!document.querySelector('#world.lite') + ' 钮=' + document.getElementById('pbLite').textContent`));
await run('轻量');
const real = errs.filter((e) => !/favicon|aldran-img@|fontsource|Permissions policy|allow-popups/.test(e));
console.log('errors', real.length, '(旧页留下的和策略提示不算，共', errs.length, ')'); for (const e of real.slice(0, 12)) console.log('  ', e);
ws.close();
