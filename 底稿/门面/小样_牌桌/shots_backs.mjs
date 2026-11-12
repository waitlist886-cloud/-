// 牌背版的分镜（第十八版起，第十九版定稿）：连上无头 Chrome（9334），照原尺寸截。页面带 ?sim=1，时间只在 __tb.tick 里走；样式的过渡和烧开的圆照真的钟走，每一步后面真等一会儿再截。
//   node shots_backs.mjs <套名> <宽> <高> <输出目录>      （输出目录要先建好；无头 Chrome 的起法在 门面重做_方向稿.md 第十二节第十七版那一块）
// 套名只剩 back（全流程），留着这个参数是为了截出来的文件名不变。第十九版把原画版和地址的 ?bands= 拿掉了，原来的 art 那一套跟着去掉。
import fs from 'node:fs';
const [set, W, H, OUT] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5]];
const PORT = 9334, URL = 'http://localhost:8765/local.html?sim=1&full=1';
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const target = list.find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), waiters = [];
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } else for (const w of waiters) if (w.ev === m.method) w.fn(m); };
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
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: W < 600 ? 2 : 1, mobile: W < 600 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(20000)]);
await sleep(2500);
console.log('open', await ev(`await __tb.tick(300); return JSON.stringify({ cls: document.querySelector('#world').className, iw: innerWidth, ih: innerHeight })`));
const tag = `${set}_${W}x${H}`;
// 烧开、合上的圆是照真的钟走的动画：要截半路的样子，就把它们停在某一毫秒
const freezeBands = (ms) => `{ const T = ${JSON.stringify(ms)}, bs = [...document.querySelectorAll('.band')]; document.getAnimations().forEach(a => { const e = a.effect && a.effect.target; if (e && e.classList && (e.classList.contains('bimg') || e.classList.contains('bring'))) { a.pause(); a.currentTime = T[bs.indexOf(e.closest('.band'))]; } }); }`;
const freezeEra = (ms) => `document.getAnimations().forEach(a => { const t = a.effect && a.effect.target; if (t && (t.id === 'sEra' || t.id === 'ering')) { a.pause(); a.currentTime = ${ms}; } });`;
const thaw = `document.getAnimations().forEach(a => { if (a.playState === 'paused') a.finish(); });`;

{
  const K = W < 600 ? 1 : 0;
  await ev(`await __tb.tick(4000); let n = 0; while (!__tb.bands[3].open && n++ < 900) await __tb.tick(16.7); await __tb.tick(60); ${freezeBands([400, 270, 150, 45])}`); await sleep(500); await shot(`${tag}_1_烧开`);
  await ev(`${thaw} let n = 0; while (__tb.stage !== 'choose' && n++ < 300) await __tb.tick(50); await __tb.tick(400);`); await sleep(2600); await shot(`${tag}_2_四张牌背`);
  if (W < 600) await ev(`__tb.tap(${K}); await __tb.tick(700);`); else await ev(`__tb.select(${K}, true); await __tb.tick(700);`);
  await sleep(2200); await shot(`${tag}_3_选中`);
  await ev(`__tb.tap(${K}); await __tb.tick(900);`); await sleep(1500); await shot(`${tag}_4_收成牌`);
  await ev(`await __tb.tick(1400);`); await sleep(1500); await shot(`${tag}_5_立住`);
  await ev(`let n = 0; while (!document.querySelector('#sEra').classList.contains('on') && n++ < 400) await __tb.tick(16.7); ${freezeEra(270)}`); await sleep(400); await shot(`${tag}_6_原画烧开`);
  await ev(`${thaw} let n = 0; while (__tb.stage !== 'done' && n++ < 300) await __tb.tick(50); await __tb.tick(600);`); await sleep(3200); await shot(`${tag}_7_这一纪`);
  console.log('rigs', await ev(`return !!__tb.rigs`));
}
ws.close();
