// 片头样片的几样手上动作在真实时钟下走一遍：点屏幕到下一句，点顶上的牌跳到那一处，应那一句，跳过，再看一遍。收报错。
//   node act_pv.mjs <宽> <高>
const [W, H] = [+process.argv[2], +process.argv[3]];
const PORT = 9334, URL = 'http://localhost:8767/local.html';
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
const click = async (x, y) => { for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 }); };
const center = (sel) => ev(`const r = document.querySelector('${sel}').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]`);
const beat = () => ev('const s = __pv.scene; return s ? s.b.i + " " + s.b.kind + " " + (s.b.text || "") + " @" + __pv.T.toFixed(1) : "?"');
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: W < 700 ? 2 : 1, mobile: false });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL });
await Promise.race([loaded, sleep(15000)]); await sleep(2500);
console.log('开场', await beat());
await click(W / 2, H / 2); await sleep(400); console.log('点一下', await beat());
await click(W / 2, H / 2); await sleep(400); console.log('再点一下', await beat());
let p = await center('#go-1'); await click(p[0], p[1]); await sleep(600); console.log('点第二张牌', await beat());
p = await center('#go-coda'); await click(p[0], p[1]); await sleep(600); console.log('点「收」', await beat());
for (let i = 0; i < 5; i++) { await click(W / 2, H / 2); await sleep(350); }
console.log('连点五下', await beat());
await sleep(1200); await click(W / 2, H / 2); await sleep(500); console.log('应那一句', await beat(), '应了以后这一句里走到', await ev('const s = __pv.scene; return (s.lt).toFixed(2)'));
p = await center('#go-pre'); await click(p[0], p[1]); await sleep(500); console.log('点「序」', await beat());
p = await center('#skip'); await click(p[0], p[1]); await sleep(500); console.log('跳过', await beat());
await sleep(6500); console.log('末尾那一页出来了没有', await ev('return !document.querySelector("#end").hidden'), await beat());
p = await center('#again'); await click(p[0], p[1]); await sleep(600); console.log('再看一遍', await beat(), '末尾那一页还在不在', await ev('return !document.querySelector("#end").hidden'));
console.log(errs.length ? '页面报的：\n' + [...new Set(errs)].slice(0, 8).join('\n') : '页面没有报错');
ws.close();
