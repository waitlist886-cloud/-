// 月银纪的墙：真实时钟下把手上的动作走一遍，数帧率，收报错。无头 Chrome 是软件渲染，帧率只当下限看。
//   node act_book.mjs <宽> <高> [地址上多带的参数，比如 nogl=1]
// 走的是：等进场，滚轮往右，按住拖动，点一幅画进时代页，点从这里进、关掉，回到墙前，点底下的刻度跳到第二十七幅，再往右走到最后一年。
const [W, H, EXTRA] = [+process.argv[2], +process.argv[3], process.argv[4] || ''];
const PORT = 9335, URL = 'http://localhost:8768/local.html?skip=1' + (EXTRA ? '&' + EXTRA : '');
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning'].includes(m.params.type)) errs.push(m.params.type + ' ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 400));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(() => { ${expr} })()`, returnByValue: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
const mouse = (type, x, y, extra = {}) => send('Input.dispatchMouseEvent', { type, x, y, button: type === 'mouseMoved' && !extra.buttons ? 'none' : 'left', clickCount: 1, ...extra });
const click = async (x, y) => { await mouse('mousePressed', x, y, { buttons: 1 }); await mouse('mouseReleased', x, y); };
const st = () => ev('const s = __bk.s; return JSON.stringify({ cam: Math.round(s.cam), f: s.f, seen: s.seen, brk: +s.brk.toFixed(2), page: s.pageOpen, loaded: s.loaded, bad: s.bad })');
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(15000)]); await sleep(2500);
console.log('开场', await st());
const f0 = await ev('return __bk.s.frames'); await sleep(4000); const f1 = await ev('return __bk.s.frames');
console.log(`四秒里 ${f1 - f0} 帧（每秒 ${((f1 - f0) / 4).toFixed(1)}），WebGL ${await ev('return __bk.s.gl')}`);
await mouse('mouseMoved', W * .6, H * .4);
for (let i = 0; i < 6; i++) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: W / 2, y: H / 2, deltaX: 0, deltaY: 240 }); await sleep(120); }
await sleep(900); console.log('滚轮往右六下', await st());
await mouse('mousePressed', W * .7, H * .45, { buttons: 1 });
for (let i = 1; i <= 12; i++) { await mouse('mouseMoved', W * .7 - i * W * .04, H * .45, { buttons: 1 }); await sleep(16); }
await mouse('mouseReleased', W * .7 - 12 * W * .04, H * .45); await sleep(1200);
console.log('按住往左拖', await st());
const hit = await ev('const s = __bk.s; const i = s.f; return [__bk.tx[i] - s.cam + s.TW / 2, s.TY + s.TH / 2, i]');
await mouse('mouseMoved', hit[0], hit[1]); await sleep(300); await click(hit[0], hit[1]); await sleep(900);
console.log('点第 ' + (hit[2] + 1) + ' 幅', await st(), '时代页标题：', await ev('return document.querySelector("#pg-body h1").textContent'));
const go = await ev('const b = document.querySelector("#pg-body .go"); b.scrollIntoView({ block: "center" }); const r = b.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]');
await sleep(300); await click(go[0], go[1]); await sleep(400);
console.log('点从这里进，小签出来了没有', await ev('return !document.querySelector("#sheet").hidden'), await ev('return document.querySelector("#sheet h3").textContent'));
const ok = await ev('const r = document.querySelector("#sheet button").getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]');
await click(ok[0], ok[1]); await sleep(300);
const cl = await ev('const r = document.querySelector("#pg-close").getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]');
await click(cl[0], cl[1]); await sleep(900);
console.log('回到墙前', await st(), '时代页藏起来了没有', await ev('return document.querySelector("#page").hidden'));
const tk = await ev('const r = document.querySelectorAll("#rail button")[26].getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]');
await click(tk[0], tk[1]); await sleep(2600);
console.log('点最后一个刻度', await st());
for (let i = 0; i < 8; i++) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: W / 2, y: H / 2, deltaX: 0, deltaY: 300 }); await sleep(120); }
await sleep(2600); console.log('再往右走到最后一年', await st(), '那一句亮了没有', await ev('return document.querySelector("#ruin").classList.contains("show")'));
for (let i = 0; i < 10; i++) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: W / 2, y: H / 2, deltaX: 0, deltaY: -300 }); await sleep(100); }
await sleep(2200); console.log('往回走', await st());
console.log(errs.length ? '页面报的：\n' + [...new Set(errs)].slice(0, 8).join('\n') : '页面没有报错');
ws.close();
