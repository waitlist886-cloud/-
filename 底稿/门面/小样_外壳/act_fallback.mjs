// 验薄壳的退路（11-15）：图床的几个镜像都连不上的时候，薄壳出一句话和两个钮，点“用原来的介绍页”整页换回卡里原来那一页。
//   node act_fallback.mjs <宽> <高> <截图前缀> [薄壳的地址=../小样_外壳/thin_dead.html]
// thin_dead.html 是拿 make_thin.thin_html(old=原来那一页, mirrors=[连不上的地址]) 出的。假的日里壳、端口同 act_sandbox.mjs。
import fs from 'node:fs';
const [W, H, OUT, SRC] = [+process.argv[2], +process.argv[3], process.argv[4], process.argv[5] || '../小样_外壳/thin_dead.html'];
const PORT = +(process.env.CDP_PORT || 9335);
const URL0 = 'http://localhost:8773/' + encodeURIComponent('探针') + '/host.html?src=' + encodeURIComponent(SRC) + '&t=' + Date.now();
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), errs = [], ctxs = [], waiters = [];
const send = (method, params = {}, sessionId) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params })); });
const OKERR = /Permissions policy|allow-popups|allow-same-origin|favicon|sandboxed and lacks|Unrecognized feature|Blocked script execution|ERR_CONNECTION_REFUSED|ERR_UNSAFE_PORT|Failed to load resource|Failed to fetch/;
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') { const sid = m.params.sessionId; send('Runtime.enable', {}, sid); send('Log.enable', {}, sid); send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sid); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.sid === (m.sessionId || '') && x.c.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
  const push = (t) => { if (!OKERR.test(t)) errs.push(t); };
  if (m.method === 'Runtime.exceptionThrown') push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 360));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') push('error ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 260));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') push('LOG ' + m.params.entry.text.slice(0, 200));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function evIn(expr, x) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 30000, ...(x && x.c ? { contextId: x.c.id } : {}) }, (x && x.sid) || undefined);
  if (r.error) return undefined;
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
async function where(pred, ms = 30000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    for (const x of [...ctxs]) { if (x.c.auxData && x.c.auxData.isDefault === false) continue; const v = await evIn(`try { return !!(${pred}); } catch (e) { return false; }`, x); if (v === true) return x; }
    await sleep(300);
  }
  return null;
}
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 84 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
let bad = 0;
const want = (ok, what) => { if (!ok) bad++; console.log((ok ? '   ✓ ' : '   ✗ ') + what); };

await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL0 });
await Promise.race([loaded, sleep(15000)]);

const T = await where(`document.getElementById('boot') && typeof window.__OLD1001 === 'string'`, 20000);
want(!!T, '薄壳开了，原来那一页存在里头');
if (!T) { console.log(errs.slice(0, 10)); process.exit(1); }
console.log('   存着的那一页', await evIn(`return window.__OLD1001.length`, T), '字');
const F = await where(`document.getElementById('again') && document.getElementById('useold')`, 60000);
want(!!F, '镜像都连不上以后，出了“再试一次”和“用原来的介绍页”两个钮');
if (F) {
  console.log('   那句话：', await evIn(`return document.querySelector('#boot p.s').textContent`, F));
  await shot('1_连不上');
  await evIn(`document.getElementById('useold').click(); return 1`, F);
  const O = await where(`typeof SC_CUR !== 'undefined' && document.getElementById('final_output') && !document.getElementById('boot')`, 30000);
  want(!!O, '点了以后整页换成了原来那一页');
  if (O) {
    await sleep(2500);
    const st = await evIn(`return JSON.stringify({ cur: SC_CUR, back: !!document.getElementById('aldran-back'), title: document.title, scenes: document.querySelectorAll('[id^="sc_"], .scene').length, w: innerWidth, h: innerHeight })`, O);
    console.log('   原来那一页', st);
    want(st && JSON.parse(st).back === false, '它是卡里原样的那一页（没有外壳添的回牌桌钮）');
    await shot('2_原来那一页');
    const moved = await evIn(`try { if (typeof go === 'function') go('menu'); } catch (e) { return 'ERR ' + e.message; } await new Promise(r => setTimeout(r, 1500)); return SC_CUR`, O);
    want(moved === 'menu', '翻得到目录那一幕（' + moved + '）');
    await shot('3_目录');
  }
}
console.log('\n对不上的', bad, '处；报错', errs.length, '条'); for (const x of [...new Set(errs)].slice(0, 20)) console.log('  ', x);
ws.close(); process.exit(bad ? 1 : 0);
