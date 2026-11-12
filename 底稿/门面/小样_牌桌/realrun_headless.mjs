// 真实时钟、真鼠标跑一遍宽屏的流程（无头 Chrome，9334）：开场、发牌、烧开、鼠标移上去、点下去、拿牌、进这一纪。
//   node realrun_headless.mjs <宽> <高> <输出目录> [选哪一条 0..3]      （输出目录要先建好；无头 Chrome 的起法在 门面重做_方向稿.md 第十二节第十七版那一块）
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4]];
const K = +(process.argv[5] ?? 0);
const PORT = 9334, URL = 'http://localhost:8765/local.html?full=1';
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
  const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true, timeout: 30000 });
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 500);
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
const t0 = Date.now(), T = () => ((Date.now() - t0) / 1000).toFixed(2);
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 82 });
  fs.writeFileSync(`${OUT}/${name}.jpg`, Buffer.from(r.result.data, 'base64'));
}
const mouse = (type, x, y, extra = {}) => send('Input.dispatchMouseEvent', { type, x, y, pointerType: 'mouse', ...extra });

await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
await mouse('mouseMoved', 5, 5);
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(20000)]);
console.log(T(), 'loaded');
// 开场到四条摆好：每 600 毫秒看一眼走到哪了、截一张
let n = 0, stage = '';
while (n < 40) {
  await sleep(600); n++;
  stage = await ev(`JSON.stringify([__tb.stage, +__tb.hand.a.toFixed(1), Math.round(__tb.hand.x), __tb.bands.map(b => +b.open), !!__tb.rigs])`);
  await shot(`r${String(n).padStart(2, '0')}_intro`);
  console.log(T(), stage);
  if (stage.startsWith('["choose"')) break;
}
await sleep(1200); await shot('s1_choose');
const mid = (k) => Math.round(W * (k + .5) / 4);
// 鼠标移到别的一条上，再移到要选的那一条上
const other = K === 2 ? 1 : 2;
await mouse('mouseMoved', mid(other), Math.round(H * .5)); await sleep(750);
console.log(T(), 'hover', other, await ev(`JSON.stringify([__tb.stage, __tb.bands.map(b => Math.round(b.w)), document.querySelector('#sub').textContent])`));
await shot('s2_hover_other');
await mouse('mouseMoved', mid(K), Math.round(H * .5)); await sleep(750);
console.log(T(), 'hover', K, await ev(`JSON.stringify([__tb.stage, __tb.bands.map(b => Math.round(b.w)), document.querySelector('#sub').textContent])`));
await shot('s3_hover_pick');
// 点下去
await mouse('mousePressed', mid(K), Math.round(H * .5), { button: 'left', buttons: 1, clickCount: 1 });
await mouse('mouseReleased', mid(K), Math.round(H * .5), { button: 'left', buttons: 0, clickCount: 1 });
const tc = Date.now();
for (let i = 0; i < 24; i++) {
  await shot(`p${String(i).padStart(2, '0')}_${String(Date.now() - tc).padStart(4, '0')}ms`);
  await sleep(40);
}
console.log(T(), 'after pick', await ev(`JSON.stringify([__tb.stage, __tb.sw.on, +__tb.sw.u.toFixed(2)])`));
n = 0;
while (n++ < 30) { await sleep(400); stage = await ev(`__tb.stage`); if (stage === 'done') break; }
await sleep(2500); await shot('z1_era');
console.log(T(), 'end', stage, await ev(`JSON.stringify({ step: localStorage.getItem('tb_step'), lite: localStorage.getItem('tb_lite') })`));
// 再选一纪：点底下那个钮
const btn = JSON.parse(await ev(`(() => { const r = document.querySelector('#again').getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height / 2]); })()`));
await mouse('mouseMoved', btn[0], btn[1]); await mouse('mousePressed', btn[0], btn[1], { button: 'left', buttons: 1, clickCount: 1 }); await mouse('mouseReleased', btn[0], btn[1], { button: 'left', buttons: 0, clickCount: 1 });
await sleep(1600);
console.log(T(), 'again', await ev(`JSON.stringify([__tb.stage, __tb.bands.map(b => Math.round(b.w))])`));
await mouse('mouseMoved', btn[0] + 3, btn[1] - 60); await sleep(800);      // 鼠标本来就停在这一条上，动一下就选中
console.log(T(), 'move in place', await ev(`JSON.stringify([__tb.stage, __tb.bands.map(b => Math.round(b.w)), document.querySelector('#sub').textContent])`));
await shot('z2_again');
console.log('errors', errs.length, errs.slice(0, 8));
ws.close();
