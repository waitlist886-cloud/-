// 介绍页收尾（11-15）的走查，迷宫纪这一本：世界之书的入口、迷宫纪卷、地图三个年代（第三个是 1001 年今天，小卡底下没有时代钮）、
// 点一处出小卡、从地图进时代页；时代页和档案里的剧透开关、小地图翻进地图、卡片档案和旧档案各一张、只有卡片的那一种；
// 委托单只有正面、点开壁画的钩子、井底的“从这里进”；最后装成在牌桌外壳里的样子再走一遍那几个钩子（回牌桌、enter、外壳叫开哪一页、换书）。
// 一样一样点，收报错，各截一张图。对不上的地方行头带“✗”。
//   node act_wb.mjs <宽> <高> <截图前缀> [当这几页还没有卡片，比如 q1,q5]
// 后一个参数是为了把“没有卡片的时代照旧”那一路也走到：走查的时候把这几页的卡片从 data/cards.json 里拿掉再喂给页面（只在这一遍里，不写盘）。
// 本地服务器是 .claude/launch.json 的 front-maze（8771），无头 Chrome 在 9337。
import fs from 'node:fs';
const [W, H, OUT, DROP] = [+process.argv[2], +process.argv[3], process.argv[4] || 'wb', (process.argv[5] || '').split(',').filter(Boolean)];
const PORT = 9337, BASE = 'http://localhost:8771/', ADDR = BASE + 'local.html?skip=1';
const readJ = (p, d) => { try { return JSON.parse(fs.readFileSync(new URL(p, import.meta.url), 'utf8')); } catch (e) { return d; } };
const D = readJ('./data/maze.json'), CARDS = readJ('./data/cards.json', {}), MAP = readJ('./common/data/map_maze.json', { periods: [] }), WBJ = readJ('./common/data/wb.json', { volumes: [] });
for (const k of DROP) delete CARDS[k];
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0, bad = 0; const pending = new Map(), errs = [], waiters = [];
// 世界之书的迷宫纪卷要是还没并进 common/data/wb.json（卡片/世界之书_迷宫纪.json 审过才并），走查的时候现并一份顶着，只在这一遍里，不写盘
let STANDIN = null;
if (!WBJ.volumes.some((v) => v.id === 'maze')) {
  const v = readJ('../卡片/世界之书_迷宫纪.json', null);
  if (v && v.id === 'maze') STANDIN = JSON.stringify({ volumes: WBJ.volumes.concat([v]) });
}
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Fetch.requestPaused') {
    if (DROP.length && m.params.request.url.includes('data/cards.json')) send('Fetch.fulfillRequest', { requestId: m.params.requestId, responseCode: 200, responseHeaders: [{ name: 'Content-Type', value: 'application/json; charset=utf-8' }], body: Buffer.from(JSON.stringify(CARDS), 'utf8').toString('base64') });
    else if (STANDIN && /common\/data\/wb\.json/.test(m.params.request.url)) send('Fetch.fulfillRequest', { requestId: m.params.requestId, responseCode: 200, responseHeaders: [{ name: 'Content-Type', value: 'application/json; charset=utf-8' }], body: Buffer.from(STANDIN, 'utf8').toString('base64') });
    else send('Fetch.continueRequest', { requestId: m.params.requestId });
    return;
  }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400 && !/favicon/.test(m.params.response.url)) errs.push(m.params.response.status + ' ' + m.params.response.url.replace(BASE, ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300)); return r.result && r.result.result ? r.result.result.value : undefined; };
const evJ = async (expr) => JSON.parse(await ev(expr));
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
// 真鼠标点一处（地图的点要按下抬起才算；井里的钮也要验按下去不会被井的拖动接走）
const clickAt = async (x, y) => {
  for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', buttons: type === 'mousePressed' ? 1 : 0, clickCount: 1 });
};
const centerOf = async (sel) => evJ(`const el = document.querySelector(${JSON.stringify(sel)}); if (!el) return 'null'; el.scrollIntoView({block:'center'}); const r = el.getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height / 2]);`);
// 地图上挑一个眼下在框里看得见的点（框外的点叫 overflow 裁掉了，点不到），main 只挑大地方
const pinAt = async (main) => evJ(`const fr = document.querySelector('.wm-frame'); fr.scrollIntoView({block:'center'}); const f = fr.getBoundingClientRect(); for (const p of document.querySelectorAll('.wm-pin${main ? '.main' : ''} i')) { const r = p.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2; if (x > f.left + 40 && x < f.right - 60 && y > f.top + 20 && y < f.bottom - 20) return JSON.stringify([x, y]); } return 'null'`);
const say = (...a) => console.log(...a);
const check = (ok, ...a) => { if (!ok) bad++; console.log(ok ? '  ' : '✗ ', ...a); };
const load = async (url) => {
  const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
  await send('Page.navigate', { url });
  await Promise.race([loaded, sleep(15000)]);
  for (let i = 0; i < 60; i++) { if (await ev('return !!(window.__mz && __mz.state)')) break; await sleep(200); }
  for (let i = 0; i < 40; i++) { if (await ev('return !!(window.Codex && Codex.state.maps.length)')) break; await sleep(150); }
  await sleep(1200);
};
const eraIdx = (id) => D.eras.findIndex((e) => e.id === id);
const withCards = D.eras.filter((e) => CARDS[e.id]), noCards = D.eras.filter((e) => !CARDS[e.id]);

await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Fetch.enable', { patterns: [{ urlPattern: '*common/data/wb.json*' }, { urlPattern: '*data/cards.json*' }] });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
await load(ADDR + '&t=' + Date.now());
say(STANDIN ? '（common/data/wb.json 里还没有迷宫纪卷，这一遍拿 卡片/世界之书_迷宫纪.json 现并了一份顶着，没写盘）' : WBJ.volumes.some((v) => v.id === 'maze') ? '（世界之书用的是 common/data/wb.json 里的迷宫纪卷）' : '（世界之书里还没有迷宫纪卷，也找不到 卡片/世界之书_迷宫纪.json，下面卷和地图几项会对不上）');
say(`卡片：有的时代 ${withCards.map((e) => e.id).join(' ') || '无'}，还没有的 ${noCards.map((e) => e.id).join(' ') || '无'}${DROP.length ? '（这一遍当 ' + DROP.join('、') + ' 还没有卡片）' : ''}`);

// 一、井边的入口
say('一、入口');
const f0 = (await evJ('return JSON.stringify(__mz.state())')).frames;
let c = await centerOf('#wbBtn');
const btn = await evJ(`const b = document.querySelector('#wbBtn'), im = b.querySelector('img'); return JSON.stringify({ img: im.naturalWidth, op: getComputedStyle(b).opacity, txt: b.textContent })`);
check(btn.img > 0 && btn.op === '1', '入口钮', JSON.stringify(c), JSON.stringify(btn));
await clickAt(...c); await sleep(800);
let wb = await evJ('return JSON.stringify(__mz.wb)');
const mvShut = await ev(`return document.querySelector('#mv').hidden`);
check(wb.open && wb.vol === 'maze' && mvShut, '点开以后', JSON.stringify({ open: wb.open, vol: wb.vol, page: wb.page }), '这一下没有连带点开壁画', mvShut);
say('  卷', await ev(`return [...document.querySelectorAll('#wb .vol')].map(v => v.firstChild.textContent + (v.classList.contains('off') ? '（灰）' : '')).join(' / ')`));
say('  页', await ev(`return [...document.querySelectorAll('#wb .pg')].map(v => v.textContent).join(' / ')`));
await shot('1_书');
const f1 = (await evJ('return JSON.stringify(__mz.state())')); await sleep(500);
const f2 = (await evJ('return JSON.stringify(__mz.state())'));
check(f1.paused && f1.frames === f2.frames && f1.frames > f0 - 1, '世界之书开着的时候井停着', `帧 ${f0} → ${f1.frames} → ${f2.frames}`);

// 编年页里的剧透开关，跟书里的是同一个
await ev(`const b = document.querySelector('#wb .pg[data-p="chron"]'); if (b) b.click(); return 1`); await sleep(600);
const chr = async () => evJ(`const li = [...document.querySelectorAll('#wb .chron li')]; return JSON.stringify({ n: li.length, sp: li.filter(x => x.classList.contains('spoil')).length, vis: li.filter(x => getComputedStyle(x).display !== 'none').length, book: __mz.wb.spoil })`);
const ch0 = await chr();
c = await centerOf('#wb .spl'); if (c) { await clickAt(...c); await sleep(400); }
const ch1 = await chr();
check(ch0.n > 0 && ch0.vis === ch0.n - ch0.sp && !ch0.book && ch1.vis === ch1.n && ch1.book, `编年 ${ch0.n} 条（剧透的 ${ch0.sp} 条）：关着看得见 ${ch0.vis}，开了看得见 ${ch1.vis}，书里的开关跟着开了`, ch1.book);
await ev(`const s = document.querySelector('#wb .spl'); if (s) s.click(); return 1`); await sleep(300);
check(!(await ev('return __mz.wb.spoil')), '再点一下，书里的也关上了');

// 二、地图页：三个年代
say('二、地图');
await ev(`const b = document.querySelector('#wb .pg[data-p="map"]'); if (b) b.click(); return 1`); await sleep(900);
const tabs = await ev(`return document.querySelectorAll('.wm-tabs button').length`);
check(tabs === MAP.periods.length, `年代 ${tabs}／${MAP.periods.length}`);
for (let k = 0; k < MAP.periods.length; k++) {
  await ev(`document.querySelectorAll('.wm-tabs button')[${k}].click(); return 1`); await sleep(700);
  const mp = await evJ(`const f = document.querySelector('.wm-frame'), im = document.querySelector('.wm-in img'); await new Promise(r => { if (im.complete) r(); else { im.onload = r; im.onerror = r; } }); return JSON.stringify({ pins: document.querySelectorAll('.wm-pin').length, img: im.naturalWidth, frame: [f.clientWidth, f.clientHeight], name: document.querySelector('.wm-tabs button[aria-pressed="true"]').firstChild.textContent })`);
  check(mp.pins === MAP.periods[k].pins.length && mp.img > 0, `「${mp.name}」 点 ${mp.pins}／${MAP.periods[k].pins.length}，底图 ${mp.img}，框 ${mp.frame.join('×')}`);
  await shot(`2_地图_${k + 1}`);
}
// 头一个年代：点一处出小卡，小卡底下有时代
await ev(`document.querySelectorAll('.wm-tabs button')[0].click(); return 1`); await sleep(600);
c = await pinAt(true); await clickAt(...c); await sleep(400);
let card = await evJ(`const k = document.querySelector('.wm-card'); return JSON.stringify({ shown: !k.hidden, txt: k.textContent.slice(0, 60), eras: k.querySelectorAll('[data-era]').length })`);
check(card.shown && card.eras > 0, '点了一处', JSON.stringify(card));
await shot('3_小卡');
// 第三个年代是 1001 年今天：放大，点一处，小卡底下没有时代钮
const today = MAP.periods.findIndex((p) => !p.eras.length);
if (today >= 0) {
  await ev(`document.querySelectorAll('.wm-tabs button')[${today}].click(); return 1`); await sleep(600);
  const fc = await centerOf('.wm-frame');
  for (let k = 0; k < 4; k++) await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: fc[0], y: fc[1], deltaX: 0, deltaY: -120 });
  await sleep(400);
  say('  放大以后', await ev(`return document.querySelector('.wm-in').style.transform + ' z2=' + document.querySelector('.wm-frame').classList.contains('z2')`));
  c = await pinAt(false);
  await clickAt(...c); await sleep(400);
  card = await evJ(`const k = document.querySelector('.wm-card'); return JSON.stringify({ shown: !k.hidden, txt: k.textContent.slice(0, 60), eras: k.querySelectorAll('[data-era]').length })`);
  check(card.shown && card.eras === 0, '1001 年今天点了一处，小卡底下没有时代钮', JSON.stringify(card));
  await shot('4_今天_放大');
}
// 第二个年代：小卡上的时代 → 合上书、进时代页
await ev(`document.querySelectorAll('.wm-tabs button')[1].click(); return 1`); await sleep(600);
c = await pinAt(true); await clickAt(...c); await sleep(400);
const chip = await ev(`const b = document.querySelector('.wm-card [data-era]'); return b ? b.dataset.era : ''`);
await ev(`const b = document.querySelector('.wm-card [data-era]'); if (b) b.click(); return 1`); await sleep(1200);
let st = await evJ(`return JSON.stringify({ wb: __mz.wb.open, page: __mz.state().page })`);
check(!st.wb && st.page === eraIdx(chip) && st.page >= 0, '从地图进时代', chip, JSON.stringify(st));

// 三、时代页：剧透开关（有卡片的时代优先）
say('三、时代页');
const E1 = withCards[0] || D.eras[0], i1 = eraIdx(E1.id);
await ev(`__mz.closeEra(); return 1`); await sleep(700);
await ev(`__mz.openEra(${i1}); return 1`); await sleep(1200);
const visSpoil = `[...document.querySelectorAll('#pg-body .spoil')].filter(e => getComputedStyle(e).display !== 'none').length + '/' + document.querySelectorAll('#pg-body .spoil').length`;
// 先展开第二条主线、滚到开关那里，切了以后看滚动位置和展开的样子留没留着
await ev(`const d = document.querySelectorAll('#pg-body details.ln')[1]; if (d) d.open = true; return 1`); await sleep(200);
c = await centerOf('#pg-body .spl'); await sleep(300);          // centerOf 会把开关滚到当中，滚完再记位置
const keep0 = await evJ(`const w = document.querySelector('#pg-wrap'), b = document.querySelector('#pg-body'); return JSON.stringify({ y: [w.scrollTop, b.scrollTop], open: [...document.querySelectorAll('#pg-body details.ln')].map(d => d.open ? 1 : 0).join('') })`);
const before = await ev(`return ${visSpoil}`);
await clickAt(...c); await sleep(600);
const after = await ev(`return ${visSpoil}`);
const keep1 = await evJ(`const w = document.querySelector('#pg-wrap'), b = document.querySelector('#pg-body'); return JSON.stringify({ y: [w.scrollTop, b.scrollTop], open: [...document.querySelectorAll('#pg-body details.ln')].map(d => d.open ? 1 : 0).join('') })`);
check(before.startsWith('0/') && after === `${E1.lines.filter((l) => l.ending).length}/${E1.lines.filter((l) => l.ending).length}`, `${E1.id} 剧透 关着看得见 ${before}，开了看得见 ${after}`);
check(keep0.open === keep1.open && Math.abs(keep0.y[0] - keep1.y[0]) < 4 && Math.abs(keep0.y[1] - keep1.y[1]) < 4, '切了以后留在原地', JSON.stringify(keep0), '→', JSON.stringify(keep1), '整本开了', await ev(`return __mz.wb.spoil`));
await shot('5_时代页');
await ev(`document.querySelector('#pg-body .spl').click(); return 1`); await sleep(400);
check((await ev(`return ${visSpoil}`)).startsWith('0/'), '再点一下关上', await ev(`return ${visSpoil}`));
// 主线：有卡片的只有幕名
const ln = await evJ(`const d = document.querySelector('#pg-body details.ln'); return JSON.stringify({ hooks: d.querySelectorAll('.hook').length, acts: [...d.querySelectorAll('ol li')].map(li => li.textContent), open: (d.querySelector('p.open') || {}).textContent || '' })`);
if (CARDS[E1.id]) { const lc = CARDS[E1.id].lines[E1.lines[0].name]; check(ln.open === lc.open && ln.acts.every((a) => a.length < 24), `${E1.id} 头一条主线走卡片：睁眼的地方 ${ln.open.length} 字，各幕 ${ln.acts.join('｜')}`); }
// 委托只有正面
const cm = await evJ(`const c = document.querySelector('#pg-body .crow .comm'); return JSON.stringify({ n: document.querySelectorAll('#pg-body .crow .comm').length, front: c ? c.querySelector('.front').textContent.length : 0, rows: document.querySelectorAll('#pg-body .crow dt, #pg-body .crow details').length })`);
check(cm.n === E1.comms.length && cm.front > 20 && cm.rows === 0, `委托 ${cm.n} 张，只有正面（头一张 ${cm.front} 字，单头和背面 ${cm.rows} 行）`);
await ev(`const c = document.querySelector('#pg-body .crow'); if (c) c.scrollIntoView({block:'start'}); return 1`); await sleep(300); await shot('6_委托');
// 迷宫和冒险团只留头一句
const mz = await evJ(`return JSON.stringify([...document.querySelectorAll('#pg-body ul.mz li')].map(li => ((li.querySelector('b') || {}).textContent || '') + '：' + ((li.querySelector('p.w') || {}).textContent || '')))`);
check(mz.length === (E1.mazes || []).length + (E1.teams || []).length && mz.every((t) => t.length < 140), `迷宫和冒险团 ${mz.length} 条，只留头一句（最长 ${Math.max(0, ...mz.map((t) => t.length))} 字）`);
await ev(`const c = document.querySelector('#pg-body ul.mz'); if (c) c.scrollIntoView({block:'start'}); return 1`); await sleep(300); await shot('7_迷宫和冒险团');
// 小地图
const per = MAP.periods.findIndex((p) => p.eras.includes(E1.id)), wantDots = per >= 0 ? MAP.periods[per].pins.filter((q) => (q.eras || []).includes(E1.id)).length : 0;
const mini = await evJ(`const m = document.querySelector('#pg-body .mini'); return JSON.stringify({ has: !!m, dots: m ? m.querySelectorAll('i').length : 0, names: document.querySelectorAll('#pg-body .mini-names button').length, old: document.querySelectorAll('#pg-body ul.places').length })`);
check(mini.has && mini.dots === wantDots && mini.names === E1.places.length && !mini.old, '小地图', JSON.stringify(mini), `该有 ${wantDots} 个点、${E1.places.length} 个地名`);
await ev(`const m = document.querySelector('#pg-body .mini'); if (m) m.scrollIntoView({block:'center'}); return 1`); await sleep(400);
await shot('8_小地图');
c = await centerOf('#pg-body .mini'); await clickAt(...c); await sleep(1000);
st = await evJ(`return JSON.stringify({ wb: __mz.wb, hi: document.querySelectorAll('.wm-pin.hi').length, tab: [...document.querySelectorAll('.wm-tabs button')].findIndex(b => b.getAttribute('aria-pressed') === 'true'), page: __mz.state().page })`);
check(st.wb.open && st.wb.page === 'map' && st.hi === wantDots && st.tab === per && st.page === i1, '点小地图翻进地图', JSON.stringify({ vol: st.wb.vol, page: st.wb.page, hi: st.hi, tab: st.tab }));
await shot('9_这一页的地方');
// Esc 只合上书，底下的时代页还在
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 }); await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 }); await sleep(600);
st = await evJ(`return JSON.stringify({ wb: __mz.wb.open, page: __mz.state().page })`);
check(!st.wb && st.page === i1, 'Esc 合上书，时代页还开着', JSON.stringify(st));
// 点一个地名：翻进地图、停在那一处、小卡出来
const nm = await ev(`const b = document.querySelector('#pg-body .mini-names button'); if (b) { b.scrollIntoView({block:'center'}); } return b ? b.textContent : ''`);
c = await centerOf('#pg-body .mini-names button'); await clickAt(...c); await sleep(1200);
card = await evJ(`const k = document.querySelector('.wm-card'); return JSON.stringify({ open: __mz.wb.open, shown: !!k && !k.hidden, name: k ? (k.querySelector('b') || {}).textContent : '' })`);
check(card.open && card.shown && card.name === nm, '点地名', nm, JSON.stringify(card));
await ev(`__mz.closeWB(); return 1`); await sleep(500);

// 四、档案：卡片的、旧的、只有卡片的
say('四、档案');
const fateVis = `const f = document.querySelector('#prof .pf-body .spoil'); return f ? getComputedStyle(f).display !== 'none' : 'none'`;
const profOf = async (name) => {
  await ev(`const x = document.querySelector('#pg-body [data-p=${JSON.stringify(name)}]'); x.scrollIntoView({block:'center'}); x.click(); return 1`);
  for (let k = 0; k < 40; k++) { await sleep(80); if (await ev(`const p = document.querySelector('#prof'); return !p.hidden && p.classList.contains('on') && (p.querySelector('.pf-body h2') || {}).textContent === ${JSON.stringify(name)}`)) break; }
  return evJ(`const p = document.querySelector('#prof'), b = p.querySelector('.pf-body'); return JSON.stringify({ open: !p.hidden, card: b.dataset.card === '1', len: b.innerText.length, h3: [...b.querySelectorAll('h3')].map(h => h.textContent).join('、'), tabs: p.querySelectorAll('.pf-tabs button').length, faces: p.querySelectorAll('.pf-faces figure').length, spl: b.querySelectorAll('.spl').length })`);
};
if (CARDS[E1.id]) {
  const who = E1.cast.find((x) => x.p && CARDS[E1.id].people[x.name]);
  let pf = await profOf(who.name);
  check(pf.open && pf.card && pf.tabs === 4, `卡片档案 ${who.name}`, JSON.stringify(pf));
  await sleep(450); await shot('10_卡片档案');
  check((await ev(fateVis)) === false, '档案里的下场 关着看不到', await ev(fateVis));
  await ev(`document.querySelector('#prof .spl').scrollIntoView({block:'center'}); return 1`); await sleep(300);
  const y0 = await evJ(`const p = document.querySelector('#prof'); return JSON.stringify([p.querySelector('.pf-wrap').scrollTop, p.querySelector('.pf-body').scrollTop])`);
  c = await centerOf('#prof .spl'); await clickAt(...c); await sleep(500);
  const y1 = await evJ(`const p = document.querySelector('#prof'); return JSON.stringify([p.querySelector('.pf-wrap').scrollTop, p.querySelector('.pf-body').scrollTop])`);
  check((await ev(fateVis)) === true && (await ev(`return __mz.wb.spoil`)) && !(await ev(`return document.querySelector('#prof').hidden`)) && Math.abs(y0[0] - y1[0]) < 4 && Math.abs(y0[1] - y1[1]) < 4, '档案里点了剧透：下场出来了，整本开了，档案还开着、留在原地', JSON.stringify(y0), '→', JSON.stringify(y1));
  await shot('11_档案剧透');
  await ev(`document.querySelector('#prof .spl').click(); return 1`); await sleep(400);
  check((await ev(fateVis)) === false, '再点一下关上', await ev(fateVis));
  await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
  // 相遇里的一张卡片
  const m1 = (E1.meet || []).find((x) => x.p && CARDS[E1.id].people[x.name]);
  if (m1) { pf = await profOf(m1.name); check(pf.open && pf.card, `相遇的卡片 ${m1.name}`, JSON.stringify(pf)); await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450); }
  // 传奇的档案不动
  const lg = (E1.legends || []).find((x) => x.p);
  if (lg) { pf = await profOf(lg.name); check(pf.open && !pf.card && pf.spl === 0, `传奇照旧 ${lg.name}`, JSON.stringify(pf)); await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450); }
}
// 名单上原来没有档案、这一回有了卡片的（一群人那几条）
const onlyE = D.eras.find((e) => CARDS[e.id] && e.cast.concat(e.meet || []).some((x) => !x.p && CARDS[e.id].people[x.name]));
if (onlyE) {
  const x = onlyE.cast.concat(onlyE.meet || []).find((q) => !q.p && CARDS[onlyE.id].people[q.name]);
  await ev(`__mz.openEra(${eraIdx(onlyE.id)}); return 1`); await sleep(1000);
  const pf = await profOf(x.name);
  check(pf.open && pf.card && pf.len > 30, `只有卡片的 ${onlyE.id} ${x.name}`, JSON.stringify(pf));
  await sleep(450); await shot('12_只有卡片的');
  await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
} else say('  （眼下没有“只有卡片、没有档案”的人）');
// 还没有卡片的时代：照旧
if (noCards.length) {
  const E2 = noCards[0];
  await ev(`__mz.openEra(${eraIdx(E2.id)}); return 1`); await sleep(1100);
  const l2 = await evJ(`const d = document.querySelector('#pg-body details.ln'); return JSON.stringify({ hooks: d.querySelectorAll('.hook').length, acts: [...d.querySelectorAll('ol li')].map(li => li.textContent.length), end: d.querySelectorAll('details.end.spoil').length })`);
  check(l2.hooks === E2.lines[0].hooks.length && l2.acts.some((n) => n > 12) && l2.end === (E2.lines[0].ending ? 1 : 0), `${E2.id} 还没有卡片，主线照旧`, JSON.stringify(l2));
  const who = E2.cast.find((q) => q.p);
  const pf = await profOf(who.name);
  check(pf.open && !pf.card && pf.len > 200, `旧档案 ${who.name}`, JSON.stringify(pf));
  await sleep(450); await shot('13_旧档案');
  check((await ev(fateVis)) === false, '旧档案的下场 关着看不到', await ev(fateVis));
  await ev(`document.querySelector('#prof .spl').click(); return 1`); await sleep(400);
  check((await ev(fateVis)) === true, '点了剧透看得到', await ev(fateVis));
  await ev(`document.querySelector('#prof .spl').click(); document.querySelector('#prof .x').click(); return 1`); await sleep(450);
} else say('  （六个时代都有卡片了，旧档案那一路没得走）');
await ev(`__mz.closeEra(); return 1`); await sleep(700);

// 五、井里：委托单只有正面，点开壁画的钩子，井底
say('五、井里');
await ev(`__mz.openComm(0); return 1`); await sleep(500);
const cv = await evJ(`const v = document.querySelector('#cv'), c = v.querySelector('.comm'); return JSON.stringify({ open: !v.hidden, front: c.querySelector('.front').textContent.length, rows: c.querySelectorAll('dt, details').length, btn: getComputedStyle(document.querySelector('#wbBtn')).opacity })`);
check(cv.open && cv.front > 20 && cv.rows === 0 && cv.btn === '0', '绳上的委托单只有正面，入口钮让开了', JSON.stringify(cv));
await shot('14_委托单');
await ev(`__mz.closeComm(); return 1`); await sleep(450);
let hookBad = 0, hookN = 0;
const stops = await evJ(`return JSON.stringify(__mz.STOPS.map(s => ({ era: s.era, line: s.line })))`);
for (let k = 0; k < stops.length; k++) {
  const s = stops[k]; if (s.era < 0) continue;
  const e = D.eras[s.era], l = e.lines[s.line], lc = CARDS[e.id] && CARDS[e.id].lines[l.name], want = lc ? lc.hook : (l.hooks[0] || '');
  const got = await ev(`__mz.openMural(${k}); const p = document.querySelector('#mv .txt p'); return p ? p.textContent : ''`);
  hookN++; if (got !== want) { hookBad++; say('   壁画', k, l.name, '钩子是', got, '该是', want); }
}
await ev(`__mz.closeMural(); return 1`); await sleep(450);
check(!hookBad, `点开壁画的钩子 ${hookN} 条（有卡片的用卡片上的，空的不放）`, `对不上 ${hookBad}`);
const K = await ev('return __mz.state().K');
await ev(`__mz.go(${K}); return 1`); await sleep(1800);
c = await centerOf('#endgo');
const endOn = await ev(`return document.querySelector('#endtx').classList.contains('on')`);
await shot('15_井底');
await clickAt(...c); await sleep(500);
const sh = await evJ(`const s = document.querySelector('#sheet'); return JSON.stringify({ shown: !s.hidden, txt: s.textContent.slice(0, 40) })`);
check(endOn && sh.shown && /1001/.test(sh.txt), '井底的“从这里进”（单独打开是那张小纸）', JSON.stringify(sh));
await ev(`document.querySelector('#sheet button').click(); return 1`); await sleep(300);
// 世界之书里点别一纪的时代：单独打开的时候说一声
const other = ['moon', 'strife', 'bronze'].find((v) => wb.vols.includes(v) && wb.maps.includes(v));
if (other) {
  await ev(`__mz.go(3); __mz.openWB(${JSON.stringify(other)}, 'map'); return 1`); await sleep(1000);
  c = await pinAt(true); await clickAt(...c); await sleep(400);
  const ob = await ev(`const b = document.querySelector('.wm-card [data-era]'); if (b) { b.click(); return b.dataset.era; } return ''`); await sleep(700);
  const s2 = await evJ(`const s = document.querySelector('#sheet'); return JSON.stringify({ wb: __mz.wb.open, page: __mz.state().page, sheet: !s.hidden, txt: s.textContent.slice(0, 30) })`);
  check(!!ob && !s2.wb && s2.page < 0 && s2.sheet, `世界之书里点了别一纪（${other} ${ob}）`, JSON.stringify(s2));
  await ev(`document.querySelector('#sheet').hidden = true; return 1`);
}

// 六、装在牌桌外壳里的样子：外壳给 window.SHELL（post 收到的话先记下来），一上来叫开一页
say('六、装在外壳里');
const AT = (withCards[1] || withCards[0] || D.eras[2]).id;
const shellSrc = `window.SHELL = { at: ${JSON.stringify(AT)}, post: (m) => { (window.__posted = window.__posted || []).push(m); } };`;
const inj = await send('Page.addScriptToEvaluateOnNewDocument', { source: shellSrc });
await load(ADDR + '&shell=1&t=' + Date.now());
await sleep(800);
st = await evJ(`const t = document.querySelector('#toTable'); return JSON.stringify({ shell: !!window.SHELL, page: __mz.state().page, tb: !!t, tbOp: t ? getComputedStyle(t).opacity : '' })`);
check(st.shell && st.page === eraIdx(AT) && st.tb && st.tbOp === '0', `外壳一上来叫开 ${AT}，回牌桌的钮在、时代页开着的时候让开`, JSON.stringify(st));
// 从这里进 → enter
await ev(`const b = document.querySelector('#pg-body .go'); b.scrollIntoView({block:'center'}); return 1`); await sleep(300);
c = await centerOf('#pg-body .go'); await clickAt(...c); await sleep(400);
let posted = await evJ(`return JSON.stringify({ p: window.__posted || [], sheet: !document.querySelector('#sheet').hidden })`);
const E3 = D.eras[eraIdx(AT)], L3 = E3.lines[0], en = posted.p[posted.p.length - 1] || {};
check(en.t === 'enter' && en.book === 'maze' && en.era === '迷宫纪' && en.at === AT && en.title === E3.title && en.line === L3.name && String(en.year) === String(L3.year || E3.years) && !posted.sheet, '从这里进 → enter', JSON.stringify(en));
await ev(`__mz.closeEra(); return 1`); await sleep(800);
await shot('16_外壳里的井');
c = await centerOf('#toTable'); await clickAt(...c); await sleep(300);
posted = await evJ(`return JSON.stringify(window.__posted || [])`);
check((posted[posted.length - 1] || {}).t === 'table' && (await ev(`return document.querySelector('#mv').hidden`)), '回到牌桌 → table', JSON.stringify(posted[posted.length - 1]));
// 外壳叫开另一页、叫到井底
const AT2 = D.eras[D.eras.length - 2].id;
await ev(`window.postMessage({ aldran: 1, t: 'open', at: ${JSON.stringify(AT2)} }, '*'); return 1`); await sleep(1200);
check((await ev('return __mz.state().page')) === eraIdx(AT2), `外壳叫开 ${AT2}`, await ev('return __mz.state().page'));
await ev(`window.postMessage({ aldran: 1, t: 'open', at: '1001' }, '*'); return 1`); await sleep(1800);
st = await evJ(`return JSON.stringify({ page: __mz.state().page, end: document.querySelector('#endtx').classList.contains('on') })`);
check(st.page < 0 && st.end, '外壳叫到 1001：合上时代页，下到井底', JSON.stringify(st));
c = await centerOf('#endgo'); await clickAt(...c); await sleep(400);
posted = await evJ(`return JSON.stringify({ p: window.__posted || [], sheet: !document.querySelector('#sheet').hidden })`);
const e1 = posted.p[posted.p.length - 1] || {};
check(e1.t === 'enter' && e1.book === 'maze' && e1.era === '迷宫纪' && e1.at === '1001' && e1.line === '' && !posted.sheet, '井底的从这里进 → enter', JSON.stringify(e1));
if (other) {
  await ev(`__mz.go(3); __mz.openWB(${JSON.stringify(other)}, 'map'); return 1`); await sleep(1000);
  c = await pinAt(true); await clickAt(...c); await sleep(400);
  const ob = await ev(`const b = document.querySelector('.wm-card [data-era]'); if (b) { b.click(); return b.dataset.era; } return ''`); await sleep(600);
  posted = await evJ(`return JSON.stringify(window.__posted || [])`);
  const g = posted[posted.length - 1] || {};
  check(g.t === 'goto' && g.book === other && g.at === ob, '世界之书里点了别一纪 → goto', JSON.stringify(g));
}
await send('Page.removeScriptToEvaluateOnNewDocument', { identifier: inj.result.identifier });
await send('Fetch.disable');
say(`对不上的 ${bad} 处`);
say(errs.length ? '有报错：\n' + [...new Set(errs)].join('\n') : '没有报错，没有载不下来的文件');
ws.close();
