// 真鼠标点书里左上角“回到牌桌”（11-15）：书整屏都在接指针（拖墙、拖路、下井），这枚钮要是没让开，脚本里的 .click() 点得着、真鼠标点不着。
// 四本书各翻开一回，照钮在屏幕上的位置发真的鼠标按下抬起，看回没回到牌桌。
//   node act_mouse.mjs <宽> <高> [书…]
// 本地服务器 front-cors（8773），无头 Chrome 9335。
const [W, H] = [+process.argv[2], +process.argv[3]];
const BOOKS = process.argv.slice(4).length ? process.argv.slice(4) : ['moon', 'strife', 'bronze', 'maze'];
const K = { moon: 0, strife: 1, bronze: 2, maze: 3 }, ERA = { moon: '月银纪', strife: '纷争纪', bronze: '山铜纪', maze: '迷宫纪' };
const PORT = +(process.env.CDP_PORT || 9335);
const ADDR = 'http://localhost:8773/' + encodeURIComponent('小样_外壳') + '/local.html?t=' + Date.now();
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
const until = async (expr, ms = 20000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (await ev(`try { return !!(${expr}); } catch (e) { return false; }`)) return true; await sleep(200); } return false; };
let bad = 0;
const want = (ok, what) => { if (!ok) bad++; console.log((ok ? '   ✓ ' : '   ✗ ') + what); };
const tap = async (x, y) => {
  if (W < 760) { await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] }); await sleep(60); await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); return; }
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await sleep(40);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 }); await sleep(60);
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
};
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
if (W < 760) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR });
await Promise.race([loaded, sleep(15000)]);
await until('window.__tb && window.Shell', 30000);
await ev(`__tb.skip(); return 1`); await sleep(1800);
for (const b of BOOKS) {
  console.log('== ' + ERA[b]);
  await ev(`__tb.select(${K[b]}); return 1`); await sleep(900);
  await ev(`__tb.pick(${K[b]}); return 1`);
  await until(`!document.querySelector('#acts').hidden && __tb.picked === ${K[b]}`, 25000);
  await ev(`document.querySelector('#openBook').click(); return 1`);
  const got = await until(`Shell.state.frame && document.querySelector('#sh-frame').contentWindow.document.querySelector('#toTable') && document.querySelector('#sh-book .sh-veil').classList.contains('off')`, 45000);
  want(got, '书装进来了');
  if (!got) continue;
  await sleep(4500);          // 进来那一下的题字过去
  const r = await ev(`const f = document.querySelector('#sh-frame'), fr = f.getBoundingClientRect(), d = f.contentWindow.document, t = d.querySelector('#toTable'), q = t.getBoundingClientRect(), cs = f.contentWindow.getComputedStyle(t);
    const cx = q.left + q.width / 2, cy = q.top + q.height / 2, hit = d.elementFromPoint(cx, cy);
    return JSON.stringify({ x: Math.round(fr.left + cx), y: Math.round(fr.top + cy), w: Math.round(q.width), h: Math.round(q.height), shown: cs.display !== 'none' && cs.visibility !== 'hidden' && +cs.opacity > .2, hit: hit ? (hit.id || hit.className || hit.tagName) : null })`);
  console.log('   钮', r);
  const o = JSON.parse(r);
  want(o.shown && o.w > 20, '“回到牌桌”看得见');
  await tap(o.x, o.y);
  want(await until(`!Shell.state.frame && document.querySelector('#sh-book').hidden`, 6000), '真' + (W < 760 ? '手指' : '鼠标') + '点了回到牌桌');
  if (await ev(`return !!Shell.state.frame`)) { await ev(`Shell.toTable(); return 1`); }
  await sleep(1600);
}
console.log('\n对不上的', bad, '处；报错', errs.length, '条'); for (const x of errs.slice(0, 10)) console.log('  ', x);
ws.close(); process.exit(bad ? 1 : 0);
