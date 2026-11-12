// 第十七版的分镜：连上无头 Chrome（9334），照原尺寸一帧一帧截。页面带 ?sim=1，时间只在 __tb.tick 里走；样式的过渡和烧开的那个圆照真的钟走，所以每一步后面真等一会儿再截。
//   node shots_headless.mjs <套名> <宽> <高> <输出目录>      （输出目录要先建好；无头 Chrome 的起法在 门面重做_方向稿.md 第十二节第十七版那一块）
// 套名：main（1920×945 全流程九帧）、adapt（别的尺寸：四条带、标题页各一帧）
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
async function open() {
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
  await send('Page.navigate', { url: URL });
  await Promise.race([loaded, sleep(20000)]);
  await sleep(2500);
  console.log('open', await ev(`await __tb.tick(300); return JSON.stringify({ cls: document.querySelector('#world').className, iw: innerWidth, ih: innerHeight })`));
}
// 烧开、合上的那个圆是照真的钟走的动画：要截半路的样子，就把它们停在第 ms 毫秒
const freeze = (ms) => `{ const T = ${JSON.stringify(ms)}, bs = [...document.querySelectorAll('.band')]; document.getAnimations().forEach(a => { const e = a.effect && a.effect.target; if (e && e.classList && (e.classList.contains('bimg') || e.classList.contains('bring'))) { a.pause(); a.currentTime = T[bs.indexOf(e.closest('.band'))]; } }); }`;
const thaw = `document.getAnimations().forEach(a => { if (a.playState === 'paused') a.finish(); });`;

await open();
if (set === 'main') {
  const K = 1;       // 选纷争纪
  await ev(`await __tb.tick(4000);`); await sleep(2600); await shot('m1_开场');
  await ev(`let n = 0; while (__tb.hand.a < 1 && n++ < 80) await __tb.tick(100); await __tb.tick(1050);`); await sleep(900); await shot('m2_发牌');
  // 扫完、四张牌飞到各自那一条的当中、挨个烧开：走到最后一张刚点着，把四个圆停在半路
  await ev(`let n = 0; while (!__tb.bands[3].open && n++ < 400) await __tb.tick(16.7); await __tb.tick(60); ${freeze([400, 270, 150, 45])}`); await sleep(500); await shot('m3_烧开');
  await ev(`${thaw} let n = 0; while (__tb.stage !== 'choose' && n++ < 300) await __tb.tick(50); await __tb.tick(400);`); await sleep(2600); await shot('m4_四个纪元');
  await ev(`__tb.select(${K}, true); await __tb.tick(700);`); await sleep(1600); await shot('m5_移上去');
  await ev(`__tb.tap(${K}); await __tb.tick(900);`); await sleep(1500); await shot('m6_按住收成牌');
  await ev(`await __tb.tick(300);`); await sleep(900); await shot('m7_提起');
  await ev(`await __tb.tick(260);`); await sleep(700); await shot('m8_甩过来');
  await ev(`await __tb.tick(800);`); await sleep(1500); await shot('m9_立住');
  await ev(`let n = 0; while (__tb.stage !== 'done' && n++ < 300) await __tb.tick(50); await __tb.tick(600);`); await sleep(3200); await shot('m10_这一纪');
  console.log('rigs', await ev(`return !!__tb.rigs`));
} else {
  await ev(`await __tb.tick(600); __tb.skip(); await __tb.tick(1500);`); await sleep(2800); await shot(`a_${W}x${H}_四个纪元`);
  await ev(`__tb.select(0, true); await __tb.tick(600); __tb.tap(0); let n = 0; while (__tb.stage !== 'done' && n++ < 400) await __tb.tick(50); await __tb.tick(600);`); await sleep(3200); await shot(`a_${W}x${H}_这一纪`);
}
ws.close();
