// 外壳的走查（11-15 拼装那一轮）：牌桌 → 世界之书 → 选一纪 → 翻开这一本 → 从这里进 → 建档 → 请离 → 确认页 → 回去改 → 回牌桌；再走一遍 1001 年那条路。
//   node act_shell.mjs <宽> <高> <截图前缀> [书…]        书是 moon strife bronze maze，不写就四本都走
// 本地服务器是 .claude/launch.json 的 front-cors（8773，根是 底稿/门面，带跨域头），无头 Chrome 在 9335（跟月银纪那一本共用，别同时跑）。
// 地址可以用环境变量 SHELL_URL 换（验薄壳、验沙箱里的样子的时候）。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4] || 'shell'];
const BOOKS = process.argv.slice(5).length ? process.argv.slice(5) : ['moon', 'strife', 'bronze', 'maze'];
const PORT = +(process.env.CDP_PORT || 9335);
const ADDR = process.env.SHELL_URL || 'http://localhost:8773/' + encodeURIComponent('小样_外壳') + '/local.html';
const K = { moon: 0, strife: 1, bronze: 2, maze: 3 }, ERA = { moon: '月银纪', strife: '纷争纪', bronze: '山铜纪', maze: '迷宫纪' };
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) errs.push(m.params.type + ' ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) errs.push(m.params.response.status + ' ' + decodeURIComponent(m.params.response.url).replace(/^https?:\/\/[^/]+\//, ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result && r.result.result ? r.result.result.value : undefined; };
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 84 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
const until = async (expr, ms = 20000, step = 250) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (await ev(`return !!(${expr})`)) return true; await sleep(step); } return false; };
const say = (...a) => console.log(...a);
// 建档第二版（11-17，十一步）：身穿、填名字、挑头一个能挑的族，余下几步照默认一路往下走到铸印、交给她。返回停在第几步（交出去了是 11）
const FAST_BUILD = `const W_ = (ms) => new Promise((r) => setTimeout(r, ms));
  const C_ = (s) => { const e = document.querySelector(s); if (e && !e.disabled) { e.click(); return true; } return false; };
  const V_ = (s, v) => { const e = document.querySelector(s); if (e) { e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); } };
  const N_ = () => { const m = matchMedia('(max-width: 860px)').matches, sh = document.querySelector('#sh-build .b2.sheet'); (m && !sh ? document.querySelector('#sh-build .b2-bar [data-a="next"]') : document.querySelector('#sh-build .b2-side [data-a="next"]')).click(); };
  __bd.go(1); await W_(200);
  C_('[data-a="soul"][data-v="isekai"]'); await W_(200); N_(); await W_(300);
  V_('[data-f="name"]', '走查的人'); V_('[data-f="age"]', '二十'); V_('[data-f="look"]', '黑头发，背一把旧剑'); if (__bd.free) V_('[data-f="year"]', '100'); await W_(150); N_(); await W_(300);
  if (!C_('[data-a="race"]:not(:disabled)')) V_('[data-f="race2"]', '人类'); await W_(200); N_(); await W_(300);
  for (let i = 0; i < 7 && __bd.step < 11; i++) { N_(); await W_(300); }
  const at = __bd.step; if (at === 11) N_(); return at;`;
let bad = 0;
const want = (ok, what) => { if (!ok) { bad++; say('   ✗ ' + what); } else say('   ✓ ' + what); };

await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR + (ADDR.includes('?') ? '&' : '?') + 't=' + Date.now() });
await Promise.race([loaded, sleep(15000)]);
want(await until('window.__tb && window.Shell && window.Codex', 30000), '牌桌、外壳、世界之书都载上了');
await ev(`__tb.skip(); return 1`); await sleep(2600);
await shot('1_牌桌');
say('牌桌', await ev(`const r = (s) => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), Math.round(b.height)]; }; return JSON.stringify({ wb: r('#wbBtn'), old: r('#oldBtn'), stage: __tb.stage })`));

// 一、世界之书（通用卷）
await ev(`document.querySelector('#wbBtn').click(); return 1`); await sleep(900);
const vols = await ev(`return [...document.querySelectorAll('#wb .rib .rb')].map(v => v.textContent.trim() + (v.classList.contains('off') ? '（灰）' : '')).join(' / ')`);
say('世界之书的卷', vols);
want(await ev(`return Codex.isOpen()`), '世界之书开了');
want(vols && !/灰/.test(vols), '五卷都有');
await shot('2_世界之书');
await ev(`Codex.close(); return 1`); await sleep(700);

// 二、四本书各走一遍
const inFrame = (code) => `const fw = document.querySelector('#sh-frame') && document.querySelector('#sh-frame').contentWindow; if (!fw) return null; return await fw.eval(${JSON.stringify('(async () => { ' + code + ' })()')});`;
for (const b of BOOKS) {
  say('== ' + ERA[b]);
  const e0 = errs.length;
  await ev(`__tb.again && __tb.again(); return 1`); await sleep(1200);
  await ev(`__tb.select(${K[b]}); return 1`); await sleep(900);
  await ev(`__tb.pick(${K[b]}); return 1`);
  want(await until(`!document.querySelector('#acts').hidden && __tb.picked === ${K[b]}`, 25000), '选定了，出了“翻开这一本”');
  await shot(`3_${b}_选定`);
  await ev(`document.querySelector('#openBook').click(); return 1`);
  want(await until(`document.querySelector('#sh-frame') && document.querySelector('#sh-book .sh-veil').classList.contains('off')`, 40000), '书装进来了');
  await sleep(2500);
  const info = await ev(inFrame(`return JSON.stringify({ shell: !!window.SHELL, codex: !!window.Codex, toTable: !!document.querySelector('#toTable'), wbBtn: !!document.querySelector('#wbBtn'), title: document.title })`));
  say('   书里', info);
  want(info && JSON.parse(info).shell && JSON.parse(info).codex, '书里认得外壳，世界之书在');
  await shot(`4_${b}_书`);
  // 书里的世界之书：翻到这一卷的地图
  const wbin = await ev(inFrame(`Codex.open(${JSON.stringify(b)}, 'map'); await new Promise(r => setTimeout(r, 1200)); const im = document.querySelector('.wm-in img'); if (im && !im.complete) await new Promise(r => { im.onload = im.onerror = r; setTimeout(r, 8000); }); const o = { open: Codex.isOpen(), pins: document.querySelectorAll('.wm-pin').length, img: im ? im.naturalWidth : 0, tabs: document.querySelectorAll('.wm-tabs button').length }; return JSON.stringify(o)`));
  say('   书里的地图', wbin);
  want(wbin && JSON.parse(wbin).pins > 5 && JSON.parse(wbin).img > 0, '这一卷的地图有点、底图载上了');
  await shot(`5_${b}_地图`);
  await ev(inFrame(`Codex.close(); return 1`)); await sleep(600);
  // 从这里进：找头一个能进的时代页和它的头一条主线
  const entered = await ev(inFrame(`
    const B = window.__bk || window.__mz || {}, op = B.open || B.openEra;          // 迷宫纪那一本的钩子叫 __mz.openEra
    if (op) { try { op(B.firstEra != null ? B.firstEra : 0); } catch (e) {} }
    await new Promise(r => setTimeout(r, 1500));
    const go = document.querySelector('.go[data-e]') || document.querySelector('#page .go, #pg .go') || document.querySelector('.go');
    if (go) { go.scrollIntoView({ block: 'center' }); go.click(); return 'clicked'; }
    return 'no-go';`));
  say('   从这里进', entered);
  if (entered !== 'clicked') {          // 页面上没找着钮：直接发那句话，至少把建档那一段走了
    await ev(inFrame(`SHELL.post({ t: 'enter', book: ${JSON.stringify(b)}, era: ${JSON.stringify(ERA[b])}, at: 'x', title: '走查', line: '走查的主线', year: '100', ti: '' }); return 1`));
  }
  want(await until(`Shell.state.build`, 8000), '建档那一页出来了');
  await sleep(900);
  // 书藏在建档底下的时候不画帧（外壳发 pause，书那一格头上垫的脚本把 requestAnimationFrame 先攒着）
  const fr = await ev(inFrame(`const n = () => new Promise(r => { let c = 0; const t0 = performance.now(); const id = setInterval(() => { if (performance.now() - t0 > 600) { clearInterval(id); r(c); } }, 50); const f = () => { c++; requestAnimationFrame(f); }; requestAnimationFrame(f); }); return JSON.stringify({ paused: !!window.__paused, frames: await n() })`));
  want(fr && JSON.parse(fr).paused && JSON.parse(fr).frames === 0, '书藏着的时候停了画帧 ' + fr);
  const bd = await ev(`const r = document.querySelector('#sh-build .b2'); return JSON.stringify({ era: r.dataset.era, step: __bd.step, title: r.querySelector('.b2-hd h1').textContent, rail: r.querySelector('.b2-era').textContent.trim().slice(0, 60), steps: r.querySelectorAll('.b2-st').length, souls: r.querySelectorAll('[data-a="soul"]').length, free: __bd.free })`);
  say('   建档', bd);
  want(bd && JSON.parse(bd).steps === 11 && JSON.parse(bd).souls === 3, '建档是十一步，头一步是魂');
  await shot(`6_${b}_建档`);
  const at = await ev(FAST_BUILD);
  want(at === 11, '十一步一路走到铸印（停在第 ' + at + ' 步）');
  want(await until(`Shell.state.seal`, 12000), '请离以后出了确认页');
  await sleep(900);
  const cred = await ev(`return document.querySelector('.sl-paper').textContent`);
  say('   凭证头两行', JSON.stringify((cred || '').split('\n').slice(0, 2)), '共', (cred || '').length, '字');
  want(cred && cred.startsWith('纪元：' + ERA[b]) && cred.includes('姓名：走查的人') && cred.includes('命途已确认'), '凭证的纪元、名字、起头那一句都在');
  await shot(`7_${b}_确认页`);
  await ev(`document.querySelector('.sl-acts [data-a="edit"]').click(); return 1`); await sleep(900);
  want(await ev(`return Shell.state.build && __bd.step === 11 && __bd.F.name === '走查的人'`), '回去改，落在铸印那一步，填过的还在');
  await ev(`document.querySelector('#sh-build [data-a="out"]').click(); return 1`); await sleep(900);
  want(await ev(`return !Shell.state.build && Shell.state.frame`), '回到书里，书还在原处');
  const fr2 = await ev(inFrame(`let c = 0; const f = () => { c++; requestAnimationFrame(f); }; requestAnimationFrame(f); await new Promise(r => setTimeout(r, 600)); return JSON.stringify({ paused: !!window.__paused, frames: c })`));
  want(fr2 && !JSON.parse(fr2).paused && JSON.parse(fr2).frames > 3, '回到书里接着画帧 ' + fr2);
  await ev(inFrame(`const t = document.querySelector('#toTable'); if (t) t.click(); else SHELL.post({ t: 'table' }); return 1`)); await sleep(1500);
  want(await ev(`return !Shell.state.frame && document.querySelector('#sh-book').hidden`), '回到牌桌');
  const mine = errs.slice(e0);
  say('   这一本的报错', mine.length, mine.slice(0, 6).join(' ｜ '));
}

// 三、1001 年那条路
say('== 迷宫纪 1001 年（原来那一整页）');
const e1 = errs.length;
await ev(`document.querySelector('#oldBtn').click(); return 1`);
want(await until(`document.querySelector('#sh-oldframe') && document.querySelector('#sh-old').classList.contains('ready')`, 40000), '原来那一页装进来了');
await sleep(1500);
const inOld = (code) => `const fw = document.querySelector('#sh-oldframe').contentWindow; return await fw.eval(${JSON.stringify('(async () => { ' + code + ' })()')});`;
say('   停在哪一幕', await ev(inOld(`return SC_CUR + ' ' + !!document.getElementById('aldran-back')`)));
await shot('8_1001_目录');
await ev(inOld(`document.getElementById('final_output').value = '命途已确认，请记录我的《奥尔德兰》角色建档：\\n\\n【一·灵魂形态】\\n走查'; openSeal(); return 1`));
want(await until(`Shell.state.seal`, 12000), '铸印以后外壳出了确认页');
await sleep(600);
const c1 = await ev(`return document.querySelector('.sl-paper').textContent`);
want(c1 && c1.startsWith('命途已确认'), '1001 年的凭证原样交过来了');
await shot('9_1001_确认页');
await ev(`document.querySelector('.sl-acts [data-a="table"]').click(); return 1`); await sleep(1200);
want(await ev(`return !Shell.state.old && !Shell.state.seal`), '回到牌桌');
say('   这一段的报错', errs.length - e1, errs.slice(e1, e1 + 6).join(' ｜ '));

say('\n对不上的', bad, '处；报错和载不下来的', errs.length, '条');
for (const x of errs.slice(0, 30)) say('  ', x);
ws.close();
process.exit(bad ? 1 : 0);
