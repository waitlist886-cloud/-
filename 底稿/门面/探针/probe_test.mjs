// 本地验门面探针：无头 Chrome（9334）开假的日里壳（host.html / host_csp.html），等自动测跑完，真鼠标点一遍手动的钮，读结果、收报错、截图。
//   node probe_test.mjs <宽> <高> <输出目录> [host.html|host_csp.html] [端口 8766]
// 先起两样：.claude/launch.json 的 front-probe（8766，根是 out/探针_11-12/本地验/）；无头 Chrome 照 门面重做_方向稿.md 第十二节第十七版那一块的起法（9334）。
// 介绍页那一格在沙箱里是单独的进程，要 Target.setAutoAttach 挂上去才读得到。报错里的 Permissions policy、allow-popups 那几条是沙箱该有的，不算毛病。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4]];
const HOST = process.argv[5] || 'host.html', SPORT = process.argv[6] || '8766';
const PORT = 9334, URL = `http://localhost:${SPORT}/${HOST}`;
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
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
  if (m.method === 'Runtime.exceptionThrown') errs.push('EXC ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('console.error ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 240));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') errs.push('LOG ' + m.params.entry.text.slice(0, 170) + ' ' + (m.params.entry.url || '').slice(-40));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function evIn(expr, sid, contextId) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 30000, ...(contextId ? { contextId } : {}) }, sid || undefined);
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 400);
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
const top = (expr) => evIn(expr);
let shotN = 0;
async function shot(name) { const r = await send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(`${OUT}/${String(++shotN).padStart(2, '0')}_${name}.png`, Buffer.from(r.result.data, 'base64')); }

await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
const phone = W < 600;
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: phone ? 2 : 1, mobile: phone });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(15000)]);
await sleep(1500);
// 找介绍页那一格的执行环境：要么是同进程里另一格的环境，要么是单独挂上来的一个目标
async function frameCtx() {
  for (const k of kids) { const v = await evIn(`return !!document.getElementById('rep')`, k.sid); if (v === true) return { sid: k.sid }; }
  for (const x of ctxs) { if (x.sid) continue; const v = await evIn(`return !!document.getElementById('rep')`, '', x.c.id); if (v === true) return { sid: '', id: x.c.id }; }
  return null;
}
let F = null;
for (let i = 0; i < 20 && !F; i++) { F = await frameCtx(); if (!F) await sleep(300); }
if (!F) { console.log('找不到介绍页那一格', kids.map((k) => k.info.type + ' ' + k.info.url), ctxs.length); process.exit(1); }
console.log('介绍页那一格：', F.sid ? '单独的目标' : '同一个进程里');
const fev = (expr) => evIn(expr, F.sid, F.id);
const frameTop = JSON.parse(await top(`const r = document.getElementById('f').getBoundingClientRect(); return JSON.stringify([r.left, r.top])`));
async function click(id, sel) {
  const q = sel ? `document.querySelector(${JSON.stringify(sel)})` : `document.getElementById(${JSON.stringify(id)})`;
  const r = JSON.parse(await fev(`const el = ${q}; el.scrollIntoView({ block: 'center' }); await new Promise(r => setTimeout(r, 120)); const b = el.getBoundingClientRect(); return JSON.stringify([b.left + b.width / 2, b.top + b.height / 2])`));
  const x = frameTop[0] + r[0], y = frameTop[1] + r[1];
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', buttons: 1, clickCount: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', buttons: 0, clickCount: 1 });
}
await sleep(11500);
await shot('自动测');
console.log('---- 自动测完的结果 ----\n' + await fev(`return document.getElementById('rep').value`));
await click('sA'); await sleep(700); await click('sB'); await sleep(900); await click('sC'); await sleep(1600);
await click(null, '[data-ask="heard"] button'); await sleep(200);
await shot('声音');
await click('bB'); await sleep(2200);
await click('bC'); await sleep(500); await click('aC'); await sleep(500);
await click(null, '[data-ask="popup"] button:nth-child(2)');
await click('f1'); await sleep(300); const v1 = await top(`return document.getElementById('in').value`);
await click(null, '[data-ask="f1"] button');
await click('f2'); await sleep(300); const v2 = await top(`return document.getElementById('in').value`);
await click(null, '[data-ask="f2"] button');
await click('f3'); await sleep(300); const v3 = await top(`return document.getElementById('in').value`);
await click(null, '[data-ask="f3"] button'); await click(null, '[data-ask="kb"] button:nth-child(3)');
console.log('填框：', JSON.stringify(v1), JSON.stringify(v2), v3.length, v3.slice(0, 12), v3.slice(-12));
await shot('填框');
await click('bD'); await sleep(2900);
await click('loopOn'); await sleep(900);
await click('rFill'); await sleep(400);
await shot('结果');
console.log('---- 点完以后填进输入框的结果 ----\n' + await top(`return window.__last || ''`));
console.log('顶上：', await fev(`return document.getElementById('code').textContent + ' ' + document.getElementById('alive').textContent + 's ' + document.getElementById('loadn').textContent`));
await fev(`window.scrollTo(0, 0)`); await sleep(200); await shot('回到顶上');
console.log('errors', errs.length); for (const e of errs.slice(0, 14)) console.log('  ', e);
ws.close();
