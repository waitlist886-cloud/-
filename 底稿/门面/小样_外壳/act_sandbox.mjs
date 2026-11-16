// 在“假的日里”里验薄壳（11-15 拼装那一轮）：照日里的办法把介绍页放进 srcdoc 加 sandbox（只给 allow-scripts allow-modals allow-forms），
// 薄壳自己去取外壳那一页 → 牌桌 → 选一纪 → 翻开这一本（书是沙箱里再套一格）→ 从这里进 → 建档 → 请离 → 确认页 → 填进输入框；再走 1001 年那条路。
//   node act_sandbox.mjs <宽> <高> <截图前缀> <薄壳的地址> [书=moon]
//     薄壳的地址：本地是 ../小样_外壳/thin_local.html（make_thin.py --local 出的，要先起 front-cors 8773）；推了图床以后是 ../小样_外壳/thin.html
// 假的日里壳是 底稿/门面/探针/host.html（从 8773 取）。沙箱里各格是单独的进程，要 Target.setAutoAttach 一层一层挂上去才读得到。
import fs from 'node:fs';
const [W, H, OUT, SRC] = [+process.argv[2], +process.argv[3], process.argv[4], process.argv[5] || '../小样_外壳/thin_local.html'];
const BOOK = process.argv[6] || 'moon';
const K = { moon: 0, strife: 1, bronze: 2, maze: 3 }, ERA = { moon: '月银纪', strife: '纷争纪', bronze: '山铜纪', maze: '迷宫纪' };
const PORT = +(process.env.CDP_PORT || 9335);
const URL0 = 'http://localhost:8773/' + encodeURIComponent('探针') + '/host.html?src=' + encodeURIComponent(SRC) + '&t=' + Date.now();
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), errs = [], ctxs = [], waiters = [];
const send = (method, params = {}, sessionId) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params })); });
const OKERR = /front_ptr_g\d+\/front\.json|Permissions policy|allow-popups|allow-same-origin|favicon|sandboxed and lacks|Unrecognized feature|Blocked script execution/;
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') { const sid = m.params.sessionId; send('Runtime.enable', {}, sid); send('Log.enable', {}, sid); send('Network.enable', {}, sid); send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sid); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.sid === (m.sessionId || '') && x.c.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
  const push = (t) => { if (!OKERR.test(t)) errs.push(t); };
  if (m.method === 'Runtime.exceptionThrown') push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 360));
  if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) push(m.params.type + ' ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 260));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') push('LOG ' + m.params.entry.text.slice(0, 200) + ' ' + decodeURIComponent(m.params.entry.url || '').slice(-60));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) push(m.params.response.status + ' ' + decodeURIComponent(m.params.response.url).slice(-80));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function evIn(expr, x) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 30000, ...(x && x.c ? { contextId: x.c.id } : {}) }, (x && x.sid) || undefined);
  if (r.error) return undefined;
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
// 找一格：哪个执行环境里 pred 是真的
async function where(pred, ms = 30000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    for (const x of [...ctxs]) { if (x.c.auxData && x.c.auxData.isDefault === false) continue; const v = await evIn(`try { return !!(${pred}); } catch (e) { return false; }`, x); if (v === true) return x; }
    await sleep(300);
  }
  return null;
}
const until = async (x, expr, ms = 20000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if ((await evIn(`try { return !!(${expr}); } catch (e) { return false; }`, x)) === true) return true; await sleep(250); } return false; };
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 84 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
const say = (...a) => console.log(...a);
let bad = 0;
const want = (ok, what) => { if (!ok) { bad++; say('   ✗ ' + what); } else say('   ✓ ' + what); };

await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable'); await send('Network.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL0 });
await Promise.race([loaded, sleep(15000)]);

const S = await where(`window.__tb && window.Shell && window.Codex`, 40000);
want(!!S, '薄壳把外壳那一页取来了（牌桌、外壳、世界之书都在）');
if (!S) { say('执行环境', ctxs.length, errs.slice(0, 10)); process.exit(1); }
say('   沙箱里', await evIn(`let ls = 'ok'; try { localStorage.getItem('x'); } catch (e) { ls = '没有'; } return JSON.stringify({ origin: location.origin, base: document.baseURI.slice(0, 60), localStorage: ls, size: [innerWidth, innerHeight], cfg: !!window.FRONT_CFG, lite: !!document.querySelector('#world.lite') })`, S));
await evIn(`__tb.skip(); return 1`, S); await sleep(2600);
await shot('1_牌桌');
await evIn(`document.querySelector('#wbBtn').click(); return 1`, S); await sleep(1200);
want(await evIn(`return Codex.isOpen() && document.querySelectorAll('#wb .vol').length`, S) >= 5, '世界之书开了，五卷');
await evIn(`Codex.close(); return 1`, S); await sleep(600);

say('== ' + ERA[BOOK]);
await evIn(`__tb.select(${K[BOOK]}); return 1`, S); await sleep(900);
await evIn(`__tb.pick(${K[BOOK]}); return 1`, S);
want(await until(S, `!document.querySelector('#acts').hidden && __tb.picked === ${K[BOOK]}`, 25000), '选定了');
await evIn(`document.querySelector('#openBook').click(); return 1`, S);
const B = await where(`window.SHELL && window.Codex && !window.Shell && document.querySelector('#toTable')`, 45000);
want(!!B, '书装进来了（沙箱里再套的一格）');
if (B) {
  await until(S, `document.querySelector('#sh-book .sh-veil').classList.contains('off')`, 20000); await sleep(2500);
  await shot('2_书');
  // 进来那一下的题字过去以后往里走几步再截一张：看从图床载的贴图（墙、路、井壁）出没出来
  await sleep(4500);
  await evIn(`try { const B_ = window.__bk || window.__mz || {}; if (B_.begin) B_.begin(); if (B_.z) B_.z(260); else if (B_.go) B_.go(window.__mz ? 2 : 3); if (B_.tick) for (let i = 0; i < 40; i++) B_.tick(50); } catch (e) {} return 1`, B);
  await sleep(3500);
  await shot('2b_往里走几步');
  const wbin = await evIn(`Codex.open(${JSON.stringify(BOOK)}, 'map'); await new Promise(r => setTimeout(r, 1500)); const im = document.querySelector('.wm-in img'); if (im && !im.complete) await new Promise(r => { im.onload = im.onerror = r; setTimeout(r, 8000); }); return JSON.stringify({ pins: document.querySelectorAll('.wm-pin').length, img: im ? im.naturalWidth : 0 })`, B);
  say('   书里的地图', wbin);
  want(wbin && JSON.parse(wbin).pins > 5 && JSON.parse(wbin).img > 0, '书里的世界之书和地图载上了');
  await evIn(`Codex.close(); return 1`, B); await sleep(500);
  const imgs = await evIn(`const B_ = window.__bk || window.__mz || {}, op_ = B_.open || B_.openEra; if (op_) { try { op_(B_.firstEra != null ? B_.firstEra : 0); } catch (e) {} } await new Promise(r => setTimeout(r, 2500)); const all = [...document.querySelectorAll('img')].filter(i => i.src && !i.src.startsWith('data:')); const broken = all.filter(i => i.complete && !i.naturalWidth).map(i => i.src.slice(-50)); return JSON.stringify({ imgs: all.length, broken: broken.slice(0, 5), go: !!(document.querySelector('.go[data-e]') || document.querySelector('.go')) })`, B);
  say('   时代页', imgs);
  want(imgs && !JSON.parse(imgs).broken.length, '时代页里的图没有载不下来的');
  await shot('3_时代页');
  await evIn(`const go = document.querySelector('.go[data-e]') || document.querySelector('.go'); if (go) { go.scrollIntoView({ block: 'center' }); go.click(); } else SHELL.post({ t: 'enter', book: ${JSON.stringify(BOOK)}, era: ${JSON.stringify(ERA[BOOK])}, at: 'x', title: '走查', line: '走查的主线', year: '100', ti: '' }); return 1`, B);
  want(await until(S, `Shell.state.build`, 8000), '建档那一页出来了');
  await sleep(700); await shot('4_建档');
  await evIn(`const f = document.querySelector('#sh-build form'); f.querySelector('#bd-name').value = '走查的人'; const r = f.querySelector('.bd-races button'); if (r) r.click(); else f.querySelector('#bd-race2').value = '人类'; const w = f.querySelector('#bd-when'); if (w) w.value = '100 年，随便哪里'; f.querySelector('.go').click(); return 1`, S);
  want(await until(S, `Shell.state.seal`, 12000), '请离以后出了确认页');
  await sleep(700); await shot('5_确认页');
  say('   确认页的钮', await evIn(`return [...document.querySelectorAll('.sl-acts button')].map(b => b.textContent).join(' / ')`, S));
  await evIn(`const b = document.querySelector('.sl-acts [data-a="fill"]'); if (b) b.click(); return !!b`, S); await sleep(500);
  const got = await evIn(`return document.getElementById('in').value`);
  say('   假输入框里', JSON.stringify(String(got || '').split('\n').slice(0, 2)), String(got || '').length, '字');
  want(got && String(got).startsWith('纪元：' + ERA[BOOK]) && String(got).includes('姓名：走查的人'), '凭证填进了输入框');
  await evIn(`document.querySelector('.sl-acts [data-a="table"]').click(); return 1`, S); await sleep(1500);
}

say('== 迷宫纪 1001 年');
await evIn(`document.querySelector('#oldBtn').click(); return 1`, S);
const O = await where(`typeof SC_CUR !== 'undefined' && document.getElementById('aldran-back')`, 45000);
want(!!O, '原来那一页装进来了');
if (O) {
  await sleep(1500);
  say('   停在', await evIn(`return SC_CUR`, O));
  await shot('6_1001');
  await evIn(`document.getElementById('final_output').value = '命途已确认，请记录我的《奥尔德兰》角色建档：\\n\\n【一·灵魂形态】\\n走查'; openSeal(); return 1`, O);
  want(await until(S, `Shell.state.seal`, 12000), '铸印以后外壳出了确认页');
  await sleep(500);
  await evIn(`const b = document.querySelector('.sl-acts [data-a="fill"]'); if (b) b.click(); return 1`, S); await sleep(500);
  const got = await evIn(`return document.getElementById('in').value`);
  want(got && String(got).startsWith('命途已确认'), '1001 年的凭证填进了输入框');
  await evIn(`document.querySelector('.sl-acts [data-a="table"]').click(); return 1`, S); await sleep(1000);
}
say('\n对不上的', bad, '处；报错', errs.length, '条');
for (const x of [...new Set(errs)].slice(0, 30)) say('  ', x);
ws.close();
process.exit(bad ? 1 : 0);
