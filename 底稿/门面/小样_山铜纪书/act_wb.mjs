// 山铜纪那一本接上世界之书以后的走查（11-15 介绍页收尾）：入口、卷页、地图各年代、点一处出小卡、从地图进时代页、
// 时代页和档案里的剧透开关（滚到哪儿、展开着哪几条都留着）、小地图翻进地图、卡片档案（带死的那一刻的一位）、没有卡片的时候照旧那一套、别的纪的时代，
// 路上的手势照旧不照旧（滚轮、拖、真鼠标点碑；手机上再拿手指点一回入口），
// 再照装在牌桌外壳里的样子走一遍（回到牌桌、从这里进、无字碑自由开局、外壳叫开哪一页、带着地方进来），
// 末了三样：进来那一下题字还在的时候入口不出、没有 WebGL 的退路、共用的那一份脚本载不下来书照样能走。一样一样点，收报错，各截一张图。
//   node act_wb.mjs <宽> <高> [截图前缀，不写不截图]          电脑 1920 945，手机 390 844，一遍两三分钟
// 本地服务器是 .claude/launch.json 的 front-bronze（8770），无头 Chrome 在 9336。
// 外壳是脚本垫的一个假的（window.SHELL，把页面发给外壳的话记下来）；真外壳里的样子另有主会话的 小样_外壳/act_shell.mjs（CDP_PORT=9336 … bronze）。
// 三样是拦下请求垫出来的（只在这一支脚本里，磁盘上的文件不动）：
//   世界之书里山铜纪那一卷要是还没并进 common/data/wb.json，垫一卷只有两页的空卷，地图照 map_bronze.json 走；
//   卡片要是六个时代都写齐了，“没有卡片的照旧”那一样拿掉一个时代的卡片再载一遍来走；
//   末了让 common/codex.js 回 404，看书自己还走不走得动。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4] || ''];
const PORT = 9336, BASE = 'http://localhost:8770/';          // 页面是 local.html?skip=1
const VOL = 'bronze';
const rd = (p, dflt) => { try { return JSON.parse(fs.readFileSync(new URL(p, import.meta.url), 'utf8')); } catch (e) { return dflt; } };
const D = rd('./data/bronze.json'), CARDS = rd('./data/cards.json', {}), CG = rd('./data/cg.json', {}), WBJ = rd('./common/data/wb.json', { volumes: [] }), MAP = rd('./common/data/map_bronze.json', null);
const HASVOL = WBJ.volumes.some((v) => v.id === VOL);
const STUB = { volumes: WBJ.volumes.concat([{ id: VOL, title: '山铜纪', sub: '走查垫的空卷', pages: [{ id: 'age', title: '这一纪', sections: [{ h: '', t: '这一卷还在写，走查先垫一页。' }] }, { id: 'map', title: '山河与地图', sections: [] }] }]) };
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0, stubOn = false, dropId = '', noCodex = false; const pending = new Map(), errs = [], waiters = [];
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const fulfil = (requestId, obj) => send('Fetch.fulfillRequest', { requestId, responseCode: 200, responseHeaders: [{ name: 'Content-Type', value: 'application/json; charset=utf-8' }], body: Buffer.from(JSON.stringify(obj)).toString('base64') });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Fetch.requestPaused') {
    const u = m.params.request.url;
    if (stubOn && /common\/data\/wb\.json/.test(u)) fulfil(m.params.requestId, STUB);
    else if (dropId && /data\/cards\.json/.test(u)) { const c = { ...CARDS }; delete c[dropId]; fulfil(m.params.requestId, c); }
    else if (noCodex && /common\/codex\.js/.test(u)) send('Fetch.fulfillRequest', { requestId: m.params.requestId, responseCode: 404, body: '' });
    else send('Fetch.continueRequest', { requestId: m.params.requestId });
    return;
  }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400 && !/favicon/.test(m.params.response.url)) errs.push(m.params.response.status + ' ' + m.params.response.url.replace(BASE, ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => {      // 页面里跑一句；等了四十秒还不回（比如在等一张不会载的图）就记一笔往下走，别把整支走查卡死
  const r = await Promise.race([send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }), sleep(40000).then(() => null)]);
  if (!r) { errs.push('脚本等了四十秒没回 ' + expr.slice(0, 120)); return undefined; }
  if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 400));
  return r.result && r.result.result ? r.result.result.value : undefined;
};
const evj = async (expr) => JSON.parse((await ev(expr)) || 'null');
const shot = async (name) => { if (!OUT) return; const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
// 真鼠标点一处（地图的点、右上角的入口都要按下抬起才算）
const clickAt = async (x, y) => { for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', buttons: type === 'mousePressed' ? 1 : 0, clickCount: 1 }); };
const key = async (k) => { await send('Input.dispatchKeyEvent', { type: 'keyDown', key: k, code: k }); await send('Input.dispatchKeyEvent', { type: 'keyUp', key: k, code: k }); };
const centerOf = async (sel) => evj(`const el = document.querySelector(${JSON.stringify(sel)}); if (!el) return 'null'; el.scrollIntoView({ block: 'center' }); const r = el.getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height / 2]);`);
// 地图上挑一个眼下在框里的点（框外的点叫 overflow 裁掉了，点不到）；pref 写 '.main' 是先挑大地方
const pinAt = async (pref = '') => evj(`const f = document.querySelector('.wm-frame').getBoundingClientRect(); for (const sel of [${JSON.stringify(pref)}, '']) for (const p of document.querySelectorAll('.wm-pin' + sel + ' i')) { const r = p.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2; if (x > f.left + 40 && x < f.right - 60 && y > f.top + 20 && y < f.bottom - 20) return JSON.stringify([x, y]); } return 'null'`);
const imgW = `const wOf = (u) => new Promise((r) => { const i = new Image(); i.onload = () => r(i.naturalWidth); i.onerror = () => r(0); i.src = u; });`;      // 页面里量一张图载不载得上（loading=lazy 的图不在眼前不载，另起一张去量）
let bad = 0;
const say = (...a) => console.log(...a);
const check = (name, ok, detail = '') => { say(ok ? '  对' : '  不对', name, detail === '' ? '' : typeof detail === 'string' ? detail : JSON.stringify(detail)); if (!ok) bad++; };
const st = () => evj(`const s = __bk.s, w = __bk.wb; return JSON.stringify({ page: s.pageOpen, stv: s.stOpen, wb: w.open, vol: w.vol, pg: w.page, spoil: w.spoil, frames: s.frames, camZT: s.camZT })`);

await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Fetch.enable', { patterns: [{ urlPattern: '*common/data/wb.json*', requestStage: 'Request' }, { urlPattern: '*data/cards.json*', requestStage: 'Request' }, { urlPattern: '*common/codex.js*', requestStage: 'Request' }] });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
let shellScript = null;
// 载一遍页面。stub 垫空卷，drop 拿掉哪个时代的卡片，shell 垫一个外壳，q 是地址上多带的参数，noskip 不跳过进来那一下，nocodex 让共用的那一份脚本载不下来
async function load({ stub = false, shell = null, drop = '', q = '', noskip = false, nocodex = false } = {}) {
  stubOn = stub; dropId = drop; noCodex = nocodex;
  if (shellScript) { await send('Page.removeScriptToEvaluateOnNewDocument', { identifier: shellScript }); shellScript = null; }
  if (shell) shellScript = (await send('Page.addScriptToEvaluateOnNewDocument', { source: `window.SHELL = { at: ${JSON.stringify(shell.at || '')}, posts: [], post(m) { this.posts.push(m); } };` })).result.identifier;
  const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
  await send('Page.navigate', { url: BASE + 'local.html?' + (noskip ? '' : 'skip=1&') + (q ? q + '&' : '') + 't=' + Date.now() });
  await Promise.race([loaded, sleep(15000)]);
  for (let i = 0; i < 80; i++) { if (await ev('return !!(window.__bk && __bk.s.W && __bk.wb)')) break; await sleep(noskip ? 60 : 200); }
  if (noskip) return;
  for (let i = 0; i < (nocodex ? 5 : 50); i++) { if ((await ev('return __bk.wb.maps.length')) >= 4) break; await sleep(100); }
  await sleep(600);
}
const eraIdx = (id) => D.eras.findIndex((e) => e.id === id);
const deathsOf = (e) => Object.keys((CG[e.id] || {}).deaths || {});
const people = (e) => e.cast.concat(e.meet || []);
const hasCard = (e, n) => !!(CARDS[e.id] && CARDS[e.id].people && CARDS[e.id].people[n]);
// 有卡片的时代挑一个（先挑里头有死的那一刻的）；没有卡片的时代要是有就拿它走“照旧”，没有就拿掉一个时代的卡片来走
let cardEra = D.eras.findIndex((e) => CARDS[e.id] && deathsOf(e).some((n) => hasCard(e, n)));
if (cardEra < 0) cardEra = D.eras.findIndex((e) => CARDS[e.id]);
let plainEra = D.eras.findIndex((e) => !CARDS[e.id] && deathsOf(e).length);
if (plainEra < 0) plainEra = D.eras.findIndex((e) => !CARDS[e.id]);
const dropEra = plainEra >= 0 ? -1 : D.eras.findIndex((e, k) => k !== cardEra && deathsOf(e).length);

// 〇、眼下这一份世界之书里有没有山铜纪那一卷
say(`世界之书里${HASVOL ? '有' : '还没有'}山铜纪那一卷（common/data/wb.json：${WBJ.volumes.map((v) => v.id).join('、')}）${HASVOL ? '' : '；先照眼下的样子看一眼入口，再垫一卷空卷走地图'}`);
say(`卡片：${D.eras.map((e) => e.id + (CARDS[e.id] ? ' ' + Object.keys(CARDS[e.id].people || {}).length + ' 人' : ' 没有')).join('，')}`);
let s, c;
if (!HASVOL) {
  await load();
  await ev(`__bk.openWB(${JSON.stringify(VOL)}, ''); return 1`); await sleep(600);
  s = await st();
  check('没有这一卷的时候入口照样打开一本书（落在通用卷）', s.wb && s.vol !== VOL, s);
  await ev(`__bk.closeWB(); return 1`); await sleep(500);
  await ev(`__bk.open(0); return 1`); await sleep(900);
  check('时代页的小地图照样出（地图那一份是有的）', (await ev(`return !!document.querySelector('#pg-body .mini')`)) === true);
}

// 一、路上右上角的入口（真鼠标点）、卷页
await load({ stub: !HASVOL });
say('一、入口和卷页');
const s0 = await st();
c = await centerOf('#wbBtn');
const btn = await evj(`const b = document.querySelector('#wbBtn'), im = b.querySelector('img'), r = b.getBoundingClientRect(); return JSON.stringify({ img: im.complete && im.naturalWidth, op: getComputedStyle(b).opacity, box: [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)] })`);
check('入口钮在右上角，图载上了', btn.img > 0 && +btn.op === 1 && btn.box[2] <= W && btn.box[0] > W / 2 && btn.box[1] >= 0, btn);
await shot('0_路上');
await clickAt(...c); await sleep(800);
s = await st();
check('点了入口，世界之书开在山铜纪那一卷', s.wb && s.vol === VOL, s);
check('点入口没有带着路走（没当成拖动）', Math.abs(s.camZT - s0.camZT) < 0.01);
say('  卷', await ev(`return [...document.querySelectorAll('#wb .vol')].map(v => v.textContent + (v.classList.contains('off') ? '（灰）' : '')).join(' / ')`));
await shot('1_书');
if (W < 760) {
  await ev(`__bk.closeWB(); return 1`); await sleep(500);
  await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 1 });
  const tap = async (x, y) => { await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] }); await sleep(60); await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); };
  c = await centerOf('#wbBtn'); await tap(...c); await sleep(800);
  s = await st();
  check('手指点入口也开得了，路没跟着走', s.wb && s.vol === VOL && Math.abs(s.camZT - s0.camZT) < 0.01, s);
  c = await centerOf('#wb > .x'); await tap(...c); await sleep(600);
  check('手指点合上', !(await st()).wb);
  await send('Emulation.setTouchEmulationEnabled', { enabled: false });
  await ev(`__bk.openWB(${JSON.stringify(VOL)}, ''); return 1`); await sleep(600);
}
// 这一卷一页一页翻过去
const pgs = await evj(`return JSON.stringify([...document.querySelectorAll('#wb .pg')].map((b) => [b.dataset.p, b.textContent]))`);
let pgBad = 0; const pgLen = [];
for (const [pid, title] of pgs) {
  await ev(`document.querySelector('#wb .pg[data-p=${JSON.stringify(pid)}]').click(); return 1`); await sleep(250);
  const r = await evj(`const m = document.querySelector('#wb .main'); return JSON.stringify({ h1: (m.querySelector('h1') || {}).textContent || '', n: m.innerText.length, cur: (document.querySelector('#wb .pg[aria-current="true"]') || {}).textContent || '' })`);
  pgLen.push(r.n);
  if (r.h1 !== title || r.cur !== title || r.n < (pid === 'map' ? 10 : 40)) { pgBad++; say('  这一页不对', pid, JSON.stringify(r)); }
}
check(`山铜纪那一卷 ${pgs.length} 页都翻得开（${pgs.map((p) => p[1]).join('、')}）`, pgs.length >= 2 && pgBad === 0, '各页字数 ' + pgLen.join('、'));
// 编年那一页的剧透开关：书里切了，整本跟着切
if (pgs.some((p) => p[0] === 'chron')) {
  await ev(`document.querySelector('#wb .pg[data-p="chron"]').click(); return 1`); await sleep(300);
  const cv = `[...document.querySelectorAll('#wb .chron li')].filter((e) => getComputedStyle(e).display !== 'none').length + '/' + document.querySelectorAll('#wb .chron li').length + '（收着的 ' + document.querySelectorAll('#wb .chron li.spoil').length + '）'`;
  const c1 = await ev(`return ${cv}`);
  await ev(`document.querySelector('#wb .main .spl').click(); return 1`); await sleep(300);
  const c2 = await ev(`return ${cv}`), sp = (await st()).spoil;
  await shot('1b_编年');
  await ev(`document.querySelector('#wb .main .spl').click(); return 1`); await sleep(300);
  check('编年那一页的剧透开关管着后半段，整本书跟着切', sp === true && (await st()).spoil === false && +c2.split('/')[0] >= +c1.split('/')[0], `关着 ${c1}，开了 ${c2}`);
}
await ev(`document.querySelector('#wb .pg').click(); return 1`); await sleep(200);
// 书开着：路停着，方向键不带着路走，Esc 只合上书
const f1 = (await st()).frames; await sleep(500); const f2 = (await st()).frames;
check('书开着的时候路不画', f1 === f2, `${f1} → ${f2}`);
await key('ArrowUp'); await sleep(200);
check('书开着的时候方向键不走路', Math.abs((await st()).camZT - s0.camZT) < 0.01);
await key('Escape'); await sleep(600);
s = await st();
check('Esc 合上了书，路上别的没动', !s.wb && s.page < 0 && s.stv < 0, s);
const f3 = s.frames; await sleep(400);
check('书合上以后路接着画', (await st()).frames > f3);

// 二、地图页：各年代、点一处出小卡、放大、从小卡进时代页
say('二、地图');
await ev(`__bk.openWB(${JSON.stringify(VOL)}, 'map'); return 1`); await sleep(900);
const mp = await evj(`const f = document.querySelector('.wm-frame'), im = document.querySelector('.wm-in img'); if (!f) return 'null'; await new Promise(r => { if (im.complete) r(); else { im.onload = r; im.onerror = r; } }); return JSON.stringify({ pins: document.querySelectorAll('.wm-pin').length, img: im.naturalWidth, frame: [f.clientWidth, f.clientHeight], tabs: [...document.querySelectorAll('.wm-tabs button')].map((b) => b.textContent) })`);
check('地图页出来了', !!mp && mp.img > 0 && mp.pins > 0, mp);
await shot('2_地图');
if (mp) {
  const want = MAP ? MAP.periods.map((p) => p.pins.length) : [];
  const got = [];
  for (let k = 0; k < mp.tabs.length; k++) { await ev(`document.querySelectorAll('.wm-tabs button')[${k}].click(); return 1`); await sleep(350); got.push(await ev(`return document.querySelectorAll('.wm-pin').length`)); }
  check(`各年代的点数 ${got.join('、')}`, JSON.stringify(got) === JSON.stringify(want), '该是 ' + want.join('、'));
  await ev(`document.querySelectorAll('.wm-tabs button')[0].click(); return 1`); await sleep(400);
  c = await pinAt('.main'); await clickAt(...c); await sleep(400);
  const card = await ev(`const k = document.querySelector('.wm-card'); return k.hidden ? '' : k.textContent.slice(0, 80)`);
  check('点一处出小卡', !!card, card);
  await shot('3_小卡');
  // 换到最后一个年代、放大
  await ev(`const b = document.querySelectorAll('.wm-tabs button'); b[b.length - 1].click(); return 1`); await sleep(600);
  const fc = await centerOf('.wm-frame');
  for (let k = 0; k < 4; k++) await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: fc[0], y: fc[1], deltaX: 0, deltaY: -120 });
  await sleep(400);
  const z = await ev(`return document.querySelector('.wm-in').style.transform + ' z2=' + document.querySelector('.wm-frame').classList.contains('z2')`);
  check('滚轮放大', /z2=true/.test(z), z);
  await shot('4_放大');
  c = await pinAt(); await clickAt(...c); await sleep(400);
  const chip = await ev(`const b = document.querySelector('.wm-card [data-era]'); return b ? b.dataset.era : ''`);
  c = await centerOf('.wm-card [data-era]');      // 小卡长了那一排时代会滚到卡片底下去，先滚到眼前再点
  if (c) { await clickAt(...c); await sleep(1300); }
  s = await st();
  check(`从小卡进时代页（${chip}）`, !!chip && !s.wb && s.page === eraIdx(chip), s);
}

// 三、时代页：剧透开关（滚到哪儿、展开着哪几条主线都留着）、小地图翻进地图
say('三、时代页');
const E1 = cardEra >= 0 ? cardEra : 0;
await ev(`__bk.close(); return 1`); await sleep(700);
await ev(`__bk.setSpoil(false); __bk.open(${E1}); return 1`); await sleep(1200);
const vis = `[...document.querySelectorAll('#pg-body .spoil')].filter(e => getComputedStyle(e).display !== 'none').length + '/' + document.querySelectorAll('#pg-body .spoil').length`;
const before = await ev(`return ${vis}`);
// 先把第二条主线也展开、头一块碑翻过去，再滚到开关跟前
await ev(`const d = document.querySelectorAll('#pg-body details.ln')[1]; if (d) d.open = true; const s = document.querySelector('#pg-body .srow .st'); if (s) s.click(); document.querySelector('#pg-body .spl').scrollIntoView({ block: 'center' }); return 1`); await sleep(400);
const posOf = `(() => { const b = document.querySelector('#pg-body .spl').getBoundingClientRect(); const ln = [...document.querySelectorAll('#pg-body details.ln')].map((d) => d.open ? 1 : 0).join(''); return JSON.stringify({ y: Math.round(b.top), ln, turn: document.querySelector('#pg-body .srow .st').classList.contains('turn'), sc: [Math.round(document.querySelector('#pg-wrap').scrollTop), Math.round(document.querySelector('#pg-body').scrollTop)] }); })()`;
const p0 = await evj(`return ${posOf}`);
c = await evj(`const r = document.querySelector('#pg-body .spl').getBoundingClientRect(); return JSON.stringify([r.left + 20, r.top + r.height / 2])`);
await clickAt(...c); await sleep(700);
const after = await ev(`return ${vis}`), p1 = await evj(`return ${posOf}`);
check('时代页的剧透开关：关着看不见，开了看得见', /^0\//.test(before) && +after.split('/')[0] === +after.split('/')[1] && +after.split('/')[1] > 0, `关着 ${before}，开了 ${after}`);
check('切了以后原地重画：开关还在原处，展开着的主线、翻过去的碑都留着', Math.abs(p0.y - p1.y) <= 1 && p0.ln === p1.ln && p0.ln[1] === '1' && p1.turn === true, { 前: p0, 后: p1 });
check('整本的开关跟着开了', (await st()).spoil === true);
await shot('5_时代页');
// 滚到旅伴那一排再切：眼前的东西不该叫上头多出来少掉的那几行顶走
{
  const a = await evj(`const f = document.querySelector('#pg-body .cast figure'); f.scrollIntoView({ block: 'center' }); await new Promise((r) => setTimeout(r, 200)); const y0 = Math.round(f.getBoundingClientRect().top); __bk.setSpoil(false); const y1 = Math.round(document.querySelector('#pg-body .cast figure').getBoundingClientRect().top); __bk.setSpoil(true); const y2 = Math.round(document.querySelector('#pg-body .cast figure').getBoundingClientRect().top); return JSON.stringify([y0, y1, y2])`);
  check('滚到旅伴那一排再切开关，眼前那一排不动', Math.abs(a[0] - a[1]) <= 1 && Math.abs(a[0] - a[2]) <= 1, a);
  await ev(`document.querySelector('#pg-body .spl').scrollIntoView({ block: 'center' }); return 1`); await sleep(300);
  c = await evj(`const r = document.querySelector('#pg-body .spl').getBoundingClientRect(); return JSON.stringify([r.left + 20, r.top + r.height / 2])`);
}
await clickAt(...c); await sleep(600);
check('再点一下关上', (await ev(`return ${vis}`)).startsWith('0/') && (await st()).spoil === false);
// 小地图
const mini = await evj(`${imgW} const m = document.querySelector('#pg-body .mini'); if (!m) return 'null'; return JSON.stringify({ dots: m.querySelectorAll('i').length, img: await wOf(m.querySelector('img').getAttribute('src')), names: [...document.querySelectorAll('#pg-body .mini-names button')].map((b) => b.textContent), old: document.querySelectorAll('#pg-body ul.places li').length, stele: document.querySelectorAll('#pg-body .srow .mini').length })`);
check('“这一带”是小地图，地名一个不少，原来那一串没有了', !!mini && mini.img > 0 && mini.dots > 0 && mini.names.length === D.eras[E1].places.length && mini.old === 0 && mini.stele === 0, mini);
c = await centerOf('#pg-body .mini'); await sleep(500);
await shot('6_小地图');
await clickAt(...c); await sleep(1000);
const mm = await evj(`return JSON.stringify({ wb: __bk.wb, hi: document.querySelectorAll('.wm-pin.hi').length, tab: [...document.querySelectorAll('.wm-tabs button')].findIndex((b) => b.getAttribute('aria-pressed') === 'true') })`);
check('点小地图翻进世界之书的地图，这一页提到的地方亮着', mm.wb.open && mm.wb.vol === VOL && mm.wb.page === 'map' && mm.hi > 0 && mm.tab === (MAP ? MAP.periods.findIndex((p) => p.eras.includes(D.eras[E1].id)) : mm.tab), mm);
await shot('7_这一页的地方');
await key('Escape'); await sleep(600);
check('Esc 合上书，时代页还开着', !(await st()).wb && (await st()).page === E1);
{
  // 地名底下那一排：点一个翻到地图上那一处（挑一个图上有点的；这一页的地名图上没有点的，另列出来）
  const pinsOf = (e) => { const p = MAP && MAP.periods.find((q) => q.eras.includes(e.id)); return new Set(p ? p.pins.filter((q) => (q.eras || []).includes(e.id)).map((q) => q.name) : []); };
  const nm = mini ? mini.names.find((n) => pinsOf(D.eras[E1]).has(n)) : '';
  if (nm) {
    c = await centerOf(`#pg-body .mini-names button[data-mf=${JSON.stringify(nm)}]`); await clickAt(...c); await sleep(1100);
    const foc = await ev(`const k = document.querySelector('.wm-card'); return k && !k.hidden ? k.querySelector('b').textContent : ''`);
    check(`点地名“${nm}”翻到地图上那一处`, foc === nm, foc);
    await ev(`__bk.closeWB(); return 1`); await sleep(500);
  }
  const lost = D.eras.map((e) => [e.id, e.places.map((p) => p.name).filter((n) => !pinsOf(e).has(n))]).filter((x) => x[1].length);
  if (lost.length) say('  （数据）这几页“这一带”的地名在地图上没有点，点了只翻到地图、不出小卡：' + lost.map((x) => x[0] + ' ' + x[1].join('、')).join('；'));
}

// 四、档案：有卡片的走卡片，没有卡片的照旧；下场、死期死因、死的那一刻收在剧透开关里
say('四、档案');
const profState = `(() => { const p = document.querySelector('#prof'), b = p.querySelector('.pf-body'); const shown = (el) => { for (let x = el; x && x !== b; x = x.parentElement) if (getComputedStyle(x).display === 'none') return false; return true; };
  const f = p.querySelector('.pf-fate'), sp = p.querySelector('.pf-body .spoil'), d = p.querySelector('.pf-fate .cgb img'), spl = p.querySelector('.pf-body .spl');
  return JSON.stringify({ open: !p.hidden, name: (b.querySelector('h2') || {}).textContent || '', card: !!b.querySelector('[data-card]'), text: b.innerText.length, heads: [...b.querySelectorAll('h3')].map((h) => h.textContent), end: !!sp && shown(sp), fate: !!f && shown(f), death: !!d && shown(d),
    splY: spl ? Math.round(spl.getBoundingClientRect().top) : null, tab: [...p.querySelectorAll('.pf-tabs button')].findIndex((x) => x.getAttribute('aria-pressed') === 'true'), pos: p.querySelector('.pf-spr').style.backgroundPosition }); })()`;
// 一位带死的那一刻的：关着什么都看不见，开了下场、死期死因、那一幅都出来，点那一幅看大图
async function deathWalk(name, tag) {
  await ev(`__bk.setSpoil(false); document.querySelector('#pg-body [data-p=${JSON.stringify(name)}]').click(); return 1`); await sleep(900);
  let pf = await evj(`return ${profState}`);
  check(`${name}（${tag}）剧透关着：没有你的那一版、死期死因、死的那一刻都看不见`, pf.open && pf.name === name && !pf.end && !pf.fate && !pf.death, { 卡片: pf.card });
  await ev(`document.querySelector('#prof .spl').click(); return 1`); await sleep(700);
  pf = await evj(`return ${profState}`);
  const dimg = await ev(`${imgW} const d = document.querySelector('#prof .pf-fate .cgb img'); return d ? await wOf(d.getAttribute('src')) : 0`);
  check('开了剧透：下场、死期死因、死的那一刻都出来了', pf.end && pf.fate && pf.death && dimg > 0, { 那一幅: dimg });
  await ev(`document.querySelector('#prof .pf-fate').scrollIntoView({ block: 'center' }); return 1`); await sleep(400);
  await shot(tag === '卡片' ? '10_卡片档案_死的那一刻' : '11_旧档案_死的那一刻');
  c = await centerOf('#prof .pf-fate .cgb'); await clickAt(...c); await sleep(700);
  const cgv = await evj(`const v = document.querySelector('#cgv'); return JSON.stringify({ open: !v.hidden && v.classList.contains('on'), cap: v.querySelector('.cap').textContent })`);
  check('点那一幅看大图', cgv.open && cgv.cap.includes(name), cgv);
  await key('Escape'); await sleep(450); await key('Escape'); await sleep(450);
  check('Esc 两下退回时代页', (await evj(`return JSON.stringify({ cg: document.querySelector('#cgv').classList.contains('on'), prof: document.querySelector('#prof').classList.contains('on') })`)).prof === false);
  await ev(`__bk.setSpoil(false); return 1`); await sleep(300);
}
if (cardEra >= 0) {
  const e = D.eras[cardEra], who = people(e).find((x) => x.p && hasCard(e, x.name));
  await ev(`document.querySelector('#pg-body [data-p=${JSON.stringify(who.name)}]').click(); return 1`); await sleep(900);
  let pf = await evj(`return ${profState}`);
  check(`${e.title}的${who.name}：档案走的是卡片`, pf.open && pf.name === who.name && pf.card && pf.heads.includes('初见') && !pf.heads.includes('外貌'), { 字数: pf.text, 栏: pf.heads.join('、') });
  check('剧透关着，下场看不见', pf.end === false && pf.fate === false);
  await shot('8_卡片档案');
  // 换一套衣服、滚到开关跟前，点开关：档案原地重画
  await ev(`const t = document.querySelectorAll('#prof .pf-tabs button')[2]; if (t) t.click(); const s = document.querySelector('#prof .spl'); if (s) s.scrollIntoView({ block: 'center' }); return 1`); await sleep(400);
  pf = await evj(`return ${profState}`);
  c = await evj(`const s = document.querySelector('#prof .spl'); if (!s) return 'null'; const r = s.getBoundingClientRect(); return JSON.stringify([r.left + 20, r.top + r.height / 2])`);
  if (c) {
    await clickAt(...c); await sleep(600);
    const pf2 = await evj(`return ${profState}`);
    check('档案里点剧透开关：下场出来了，档案还开着，开关在原处，衣服还是换过的那一套', pf2.open && pf2.end === true && Math.abs(pf2.splY - pf.splY) <= 1 && pf2.tab === pf.tab && pf2.pos === pf.pos && (await st()).spoil === true, { 前: [pf.splY, pf.tab, pf.pos], 后: [pf2.splY, pf2.tab, pf2.pos] });
    await shot('9_档案剧透');
    await clickAt(...c); await sleep(500);
    check('再点一下关上', (await evj(`return ${profState}`)).end === false && (await st()).spoil === false);
  } else check('这一位的档案里有剧透开关', false);
  await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
  const dn = deathsOf(e).find((n) => hasCard(e, n) && people(e).some((x) => x.name === n && x.p));
  if (dn) await deathWalk(dn, '卡片'); else say('  有卡片的时代里眼下没有带死的那一刻的人，这一样没走');
  // 有卡片的主线：钩子和睁眼的地方照卡片，各幕只留幕名配原画
  const l0 = e.lines[0], lc = CARDS[e.id].lines && CARDS[e.id].lines[l0.name];
  if (lc) {
    const ln = await evj(`const d = document.querySelector('#pg-body details.ln'); return JSON.stringify({ hooks: [...d.querySelectorAll('.hook')].map((h) => h.textContent), open: (d.querySelector('p.open') || {}).textContent || '', tails: d.querySelectorAll('ol li.cgi > p').length, acts: d.querySelectorAll('ol li').length, imgs: d.querySelectorAll('ol .cgb img').length })`);
    check(`${l0.name}：钩子和睁眼的地方照卡片，各幕只留幕名配原画`, ln.hooks.join('|') === (lc.hook || '') && ln.open === (lc.open || l0.open) && ln.tails === 0 && ln.acts > 0, { 钩子: ln.hooks, 幕: ln.acts, 图: ln.imgs });
  }
  // 神与魔神没有卡片，照旧那一套
  const gk = D.eras.findIndex((x) => (x.gods || []).some((g) => g.p));
  if (gk >= 0) {
    const g = D.eras[gk].gods.find((x) => x.p);
    await ev(`__bk.open(${gk}); return 1`); await sleep(1000);
    await ev(`document.querySelector('#pg-body [data-p=${JSON.stringify(g.name)}]').click(); return 1`); await sleep(900);
    pf = await evj(`return ${profState}`);
    check(`${g.name}（神与魔神）：档案照旧`, pf.open && pf.name === g.name && !pf.card && pf.text > 40, { 字数: pf.text, 栏: pf.heads.join('、') });
    await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
  }
} else say('  眼下没有哪个时代有卡片，卡片档案这一样没走');
// 传奇的档案不进剧透开关
{
  const died = (e) => { const pf = rd(`./data/prof/${e.id}.json`, {}); return (e.legends || []).find((g) => g.p && pf[g.name] && pf[g.name].died); };
  const k = D.eras.findIndex((e) => died(e));
  if (k >= 0) {
    const g = died(D.eras[k]);
    await ev(`__bk.setSpoil(false); __bk.open(${k}); return 1`); await sleep(1000);
    await ev(`document.querySelector('#pg-body [data-p=${JSON.stringify(g.name)}]').click(); return 1`); await sleep(900);
    const pf = await evj(`return ${profState}`);
    check(`传奇${g.name}：殁于这一段照旧看得见，没有剧透开关`, pf.open && pf.fate === true && pf.splY === null, pf.heads.join('、'));
    await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
  }
}

// 五、路上照旧（手势那几处添了世界之书的判断，真鼠标再走一回）；碑面开着的时候入口藏起来；别的纪的时代（单独打开这一本的时候说一声）
say('五、路上、碑面、别的纪');
await ev(`__bk.close(); return 1`); await sleep(700);
{
  await ev(`__bk.z(0); return 1`); await sleep(300);
  await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: W / 2, y: H / 2, deltaX: 0, deltaY: 400 }); await sleep(700);
  const z1 = (await st()).camZT;
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: W / 2, y: H * 0.7, button: 'left', buttons: 1, clickCount: 1 });
  for (let k = 1; k <= 6; k++) await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: W / 2, y: H * 0.7 - k * 30, button: 'left', buttons: 1 });
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: W / 2, y: H * 0.7 - 180, button: 'left', buttons: 0, clickCount: 1 }); await sleep(500);
  const z2 = (await st()).camZT;
  check('路上滚轮往前走、按住往上拖也往前走', z1 > 5 && z2 > z1 + 1, [z1, z2].map((v) => +v.toFixed(1)));
  await ev(`__bk.go(3); return 1`); await sleep(900);
  c = await evj(`const r = __bk.STL[3].el.getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height * 0.55])`);
  await clickAt(...c); await sleep(900);
  check('真鼠标点路边的碑，碑面弹出来', (await st()).stv === 3, c.map(Math.round));
}
check('碑面开着，入口藏起来', +(await ev(`return getComputedStyle(document.querySelector('#wbBtn')).opacity`)) === 0 && (await ev(`return getComputedStyle(document.querySelector('#wbBtn')).pointerEvents`)) === 'none');
c = await centerOf('#stv .btns .x'); if (c) await clickAt(...c); await sleep(1100);
check('点合上碑面收起来，入口回来', (await st()).stv < 0 && +(await ev(`return getComputedStyle(document.querySelector('#wbBtn')).opacity`)) > 0.9);
{
  const other = ['moon', 'strife', 'maze'].find((v) => WBJ.volumes.some((x) => x.id === v));
  if (other) {
    await ev(`__bk.openWB(${JSON.stringify(other)}, 'map'); return 1`); await sleep(1000);
    c = await pinAt('.main'); if (c) { await clickAt(...c); await sleep(400); }
    c = await centerOf('.wm-card [data-era]');      // 小卡长了那一排时代会滚到卡片底下去，先滚到眼前再点
    if (c) { await clickAt(...c); await sleep(900); }
    const sh = await evj(`const s = document.querySelector('#sheet'); return JSON.stringify({ open: !s.hidden, text: s.textContent.slice(0, 40) })`);
    s = await st();
    check(`在 ${other} 那一卷的地图上点一个时代：书合上，说一声在另一本书里`, !!c && !s.wb && s.page < 0 && sh.open && /另一本书/.test(sh.text), sh);
    await shot('12_别的纪');
    await key('Escape'); await sleep(300);
    check('Esc 收起那张小纸', await ev(`return document.querySelector('#sheet').hidden`));
  }
}

// 六、没有卡片的时代照旧那一套（卡片写齐了的话，拿掉一个时代的卡片再载一遍）
say('六、没有卡片的照旧');
{
  const k = plainEra >= 0 ? plainEra : dropEra;
  if (k < 0) say('  没有合适的时代，这一样没走');
  else {
    const e = D.eras[k];
    if (plainEra < 0) { say(`  卡片六个时代都有了：拦下 data/cards.json，拿掉 ${e.id} 那一份再载一遍`); await load({ stub: !HASVOL, drop: e.id }); }
    await ev(`__bk.setSpoil(false); __bk.open(${k}); return 1`); await sleep(1100);
    const l0 = e.lines[0];
    const ln = await evj(`const d = document.querySelector('#pg-body details.ln'); return JSON.stringify({ hooks: [...d.querySelectorAll('.hook')].map((h) => h.textContent), open: (d.querySelector('p.open') || {}).textContent || '', tails: d.querySelectorAll('ol li.cgi > p').length })`);
    check(`${e.title}没有卡片：主线照旧（钩子、睁眼的地方、各幕带字）`, ln.hooks.join('|') === l0.hooks.join('|') && ln.open === (l0.open || '') && ln.tails > 0, { 钩子: ln.hooks.length, 带字的幕: ln.tails });
    const who = people(e).find((x) => x.p);
    await ev(`document.querySelector('#pg-body [data-p=${JSON.stringify(who.name)}]').click(); return 1`); await sleep(900);
    const pf = await evj(`return ${profState}`);
    check(`${who.name}：档案照旧那一套（不是卡片）`, pf.open && pf.name === who.name && !pf.card && pf.text > 200 && pf.heads.includes('外貌'), { 字数: pf.text, 栏: pf.heads.join('、') });
    await shot('11a_旧档案');
    await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
    const dn = deathsOf(e).find((n) => people(e).some((x) => x.name === n && x.p));
    if (dn) await deathWalk(dn, '照旧'); else say('  这个时代没有带死的那一刻的人');
    // 别的时代的卡片还在
    const o = D.eras.findIndex((x, j) => j !== k && CARDS[x.id]);
    if (o >= 0) {
      const w2 = people(D.eras[o]).find((x) => x.p && hasCard(D.eras[o], x.name));
      await ev(`__bk.open(${o}); return 1`); await sleep(1000);
      await ev(`document.querySelector('#pg-body [data-p=${JSON.stringify(w2.name)}]').click(); return 1`); await sleep(900);
      check(`同一回里${D.eras[o].title}的${w2.name}照样走卡片`, (await evj(`return ${profState}`)).card === true);
      await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
    }
  }
}

// 七、装在牌桌外壳里的样子（脚本先垫一个 window.SHELL，把页面发给外壳的话记下来）
say('七、装在外壳里');
await load({ stub: !HASVOL, shell: { at: '' } });
const posts = async () => evj(`return JSON.stringify(SHELL.posts)`);
check('外壳在的时候左上角有回到牌桌', await ev(`return !!window.SHELL && !!document.querySelector('#toTable')`));
await shot('13_外壳_路上');
c = await centerOf('#toTable'); await clickAt(...c); await sleep(300);
let ps = await posts();
check('点回到牌桌，跟外壳说 table', ps.length === 1 && ps[0].t === 'table', ps);
check('点回到牌桌没有带着路走', Math.abs((await st()).camZT - s0.camZT) < 0.01);
const E2 = cardEra >= 0 ? cardEra : 0, e2 = D.eras[E2];
await ev(`__bk.open(${E2}); return 1`); await sleep(1000);
check('时代页开着的时候回到牌桌藏起来', +(await ev(`return getComputedStyle(document.querySelector('#toTable')).opacity`)) === 0);
c = await centerOf('#pg-body details.ln .go'); await clickAt(...c); await sleep(400);
ps = await posts();
const en = ps[ps.length - 1] || {};
check('从这里进：不出小纸，跟外壳说 enter', (await ev(`return document.querySelector('#sheet').hidden`)) && en.t === 'enter' && en.book === VOL && en.era === '山铜纪' && en.at === e2.id && en.title === e2.title && en.line === e2.lines[0].name && String(en.year) === String(e2.lines[0].year || e2.years) && en.ti === (e2.lines[0].ti || ''), en);
await ev(`__bk.close(); return 1`); await sleep(700);
// 无字碑：自由开局
const NS = await ev('return __bk.s.NS');
await ev(`__bk.go(${NS - 1}); __bk.stele(${NS - 1}); return 1`); await sleep(500);
const fr = await evj(`const s = document.querySelector('#sheet'); return JSON.stringify({ open: !s.hidden, half: s.querySelectorAll('.half').length, free: !!s.querySelector('[data-free]'), btns: [...s.querySelectorAll('button')].map((b) => b.textContent) })`);
check('无字碑点开：碑基那几处半行还在，多一个从这里进', fr.open && fr.half === 1 && fr.free, fr);
await sleep(1500);
await shot('14_外壳_无字碑');
c = await centerOf('#sheet [data-free]'); await clickAt(...c); await sleep(400);
ps = await posts();
const ef = ps[ps.length - 1] || {};
check('无字碑从这里进：enter，at 写 free，主线空着', ef.t === 'enter' && ef.book === VOL && ef.at === 'free' && ef.line === '' && (await ev(`return document.querySelector('#sheet').hidden`)), ef);
// 外壳叫打开哪一页
const E3 = D.eras.length - 2;
await ev(`window.postMessage({ aldran: 1, t: 'open', at: ${JSON.stringify(D.eras[E3].id)} }, '*'); return 1`); await sleep(1200);
check(`外壳叫打开 ${D.eras[E3].id}`, (await st()).page === E3);
await ev(`window.postMessage({ aldran: 1, t: 'open', at: 'free' }, '*'); return 1`); await sleep(900);
s = await st();
check('外壳叫打开 free：回到路上，走到无字碑跟前，小纸摊开', s.page < 0 && (await ev(`return !document.querySelector('#sheet').hidden && !!document.querySelector('#sheet [data-free]')`)), s);
await ev(`document.querySelector('#sheet').hidden = true; return 1`);
{
  const other = ['moon', 'strife', 'maze'].find((v) => WBJ.volumes.some((x) => x.id === v));
  if (other) {
    await ev(`__bk.openWB(${JSON.stringify(other)}, 'map'); return 1`); await sleep(1000);
    c = await pinAt('.main'); if (c) { await clickAt(...c); await sleep(400); }
    const chip = await ev(`const b = document.querySelector('.wm-card [data-era]'); return b ? b.dataset.era : ''`);
    await ev(`const b = document.querySelector('.wm-card [data-era]'); if (b) b.click(); return 1`); await sleep(700);
    ps = await posts();
    const g = ps[ps.length - 1] || {};
    check('外壳里点别的纪的时代：跟外壳说 goto', g.t === 'goto' && g.book === other && g.at === chip, g);
  }
}
// 带着地方进来
await load({ stub: !HASVOL, shell: { at: D.eras[1].id } });
await sleep(900);
check(`外壳带着 ${D.eras[1].id} 进来，直接翻到那一页`, (await st()).page === 1);
await shot('15_外壳_带着地方进来');

// 八、别的：进来那一下题字还在的时候入口不出；没有 WebGL 的退路；共用的那一份脚本没载下来书照样能走
say('八、进来那一下、没有 WebGL 的退路、共用那一份没载下来');
await load({ stub: !HASVOL, noskip: true });
{
  const i0 = await evj(`const b = document.querySelector('#wbBtn'); return JSON.stringify({ started: __bk.s.started, op: getComputedStyle(b).opacity, pe: getComputedStyle(b).pointerEvents })`);
  for (let i = 0; i < 40; i++) { if (await ev('return __bk.s.started')) break; await sleep(150); }
  await sleep(1000);
  const i1 = +(await ev(`return getComputedStyle(document.querySelector('#wbBtn')).opacity`));
  if (i0.started) say('  （进来那一下已经过了，没量到题字还在的时候）');
  else check('进来那一下题字还在：入口不出', +i0.op === 0 && i0.pe === 'none', i0);
  check('题字淡了，入口出来', i1 > 0.9, i1);
}
await load({ stub: !HASVOL, q: 'nogl=1' });
{
  const mode = await ev('return __bk.s.mode');
  c = await centerOf('#wbBtn'); await clickAt(...c); await sleep(700);
  check('没有 WebGL 的退路（nogl=1）：路照画，入口照开', mode === '2d' && (await st()).wb === true, mode);
  await shot('16_退路');
  await key('Escape'); await sleep(500);
}
{
  const nErr = errs.length;
  await load({ nocodex: true });
  const cm = await evj(`const b = document.querySelector('#wbBtn'); return JSON.stringify({ ok: !!(window.__bk && __bk.s.W), codex: typeof window.Codex, op: getComputedStyle(b).opacity, frames: __bk.s.frames })`);
  await ev(`__bk.open(0); return 1`); await sleep(900);
  const cp = await evj(`return JSON.stringify({ page: __bk.s.pageOpen, mini: !!document.querySelector('#pg-body .mini'), lines: document.querySelectorAll('#pg-body details.ln').length })`);
  await ev(`document.querySelector('#pg-body .spl').click(); return 1`); await sleep(400);
  check('共用那一份脚本（codex.js）载不下来：书照样能走，入口藏起来，时代页没有小地图，剧透开关照用', cm.ok && cm.codex === 'undefined' && +cm.op === 0 && cp.page === 0 && !cp.mini && cp.lines > 0 && (await st()).spoil === true, { ...cm, ...cp });
  for (let i = errs.length - 1; i >= nErr; i--) if (/codex\.js/.test(errs[i])) errs.splice(i, 1);      // 这一回的 404 是故意的
}
if (shellScript) { await send('Page.removeScriptToEvaluateOnNewDocument', { identifier: shellScript }); shellScript = null; }
await send('Fetch.disable');

say(`对不上的 ${bad} 处`);
say(errs.length ? '有报错：\n' + [...new Set(errs)].join('\n') : '没有报错，没有载不下来的文件');
ws.close();
