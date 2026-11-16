// 纷争纪的书，介绍页收尾（11-15）的走查：世界之书、地图、剧透开关、卡片、小地图、装在牌桌外壳里的那几个钩子。一样一样点，收报错，各截一张图。
//   node act_wb.mjs <宽> <高> <截图前缀>
// 分三遍：一、照现在的数据（卡片二十一张都有）；二、?legacy=s13 当作第十三张没有卡片，看原来那一套还在不在；
// 三、先塞一个假的 window.SHELL（外壳），看“从这里进”、第二十二张、回到牌桌、外壳叫打开哪一页、世界之书里点了别一纪。
// 本地服务器是 .claude/launch.json 的 front-strife（8769），无头 Chrome 在 9341。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4] || 'wb'];
const PORT = 9341, ADDR = 'http://localhost:8769/local.html?skip=1';
const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), 'utf8'));
const D = read('./data/strife.json'), CG = read('./data/cg.json'), CARDS = read('./data/cards.json'), MAP = read('./common/data/map_strife.json'), WB = read('./common/data/wb.json');
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [], bad = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) errs.push(m.params.response.status + ' ' + m.params.response.url.replace('http://localhost:8769/', ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300)); return r.result && r.result.result ? r.result.result.value : undefined; };
const J = async (expr) => JSON.parse(await ev(expr));
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
// 真鼠标点一处（地图的点要按下抬起才算）
const clickAt = async (x, y) => {
  for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', buttons: type === 'mousePressed' ? 1 : 0, clickCount: 1 });
};
const key = async (k) => { for (const type of ['keyDown', 'keyUp']) await send('Input.dispatchKeyEvent', { type, key: k, code: k, windowsVirtualKeyCode: k === 'Escape' ? 27 : 13 }); };
const centerOf = async (sel) => J(`const el = document.querySelector(${JSON.stringify(sel)}); if (!el) return 'null'; el.scrollIntoView({block:'center'}); const r = el.getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height / 2]);`);
const say = (...a) => console.log(...a);
const want = (ok, what) => { if (!ok) { bad.push(what); say('  ✗ 对不上：' + what); } return ok; };
const load = async (url) => {
  const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
  await send('Page.navigate', { url: url + '&t=' + Date.now() });
  await Promise.race([loaded, sleep(15000)]);
  for (let k = 0; k < 150; k++) { if (await ev(`return !!(window.__bk && __bk.s.W && __bk.wb.vol)`)) break; await sleep(100); }
  await sleep(1800);
};
const wbState = () => J(`return JSON.stringify(__bk.wb)`);
const spoilVis = (root) => ev(`const a = [...document.querySelectorAll('${root} .spoil')]; return a.filter(e => getComputedStyle(e).display !== 'none').length + '/' + a.length`);
const scrolls = (a, b) => J(`return JSON.stringify([document.querySelector('${a}').scrollTop, document.querySelector('${b}').scrollTop].map(Math.round))`);
const eraI = (id) => D.eras.findIndex((x) => x.id === id);

await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
errs.length = 0;      // Runtime.enable 会把这一格原先那一页报过的错重放一遍，不算这一回的
await load(ADDR);

say('—— 一、照现在的数据 ——');
// 1. 路上的入口
let c = await centerOf('#wbBtn'); say('入口钮在', c.map(Math.round).join(','));
// 入口钮的图写的是 data-a，载共用那一份的时候过一遍 A() 才有地址（装在外壳里 common/ 不在这一本自己那一段）
const icon = await J(`const im = document.querySelector('#wbBtn img'); return JSON.stringify({ src: im.getAttribute('src') || '', a: im.dataset.a || '', w: im.naturalWidth })`);
want(icon.w > 0 && icon.src.endsWith('common/assets/ui/emblem_strife.webp') && icon.a === 'common/assets/ui/emblem_strife.webp', '入口钮的图没载上 ' + JSON.stringify(icon));
const f0 = await ev(`return __bk.s.frames`);
await clickAt(...c); await sleep(700);
let st = await wbState(); say('点了入口', JSON.stringify(st));
want(st.open && st.vol === 'strife' && st.page === 'age', '点入口没翻到纷争纪卷');
const f1 = await ev(`return __bk.s.frames`); await sleep(400);
want((await ev(`return __bk.s.frames`)) === f1 && await ev(`return __bk.s.wbOpen`), '世界之书开着的时候路还在走');
say('卷', await ev(`return [...document.querySelectorAll('#wb .vol')].map(v => v.textContent + (v.classList.contains('off') ? '（灰）' : '')).join(' / ')`));
await shot('1_书');
// 2. 这一卷一页一页翻
const vol = WB.volumes.find((v) => v.id === 'strife');
const pages = await J(`return JSON.stringify([...document.querySelectorAll('#wb .pg')].map(v => v.dataset.p))`);
want(pages.join() === vol.pages.map((p) => p.id).join(), '这一卷的页跟 wb.json 对不上');
for (const pid of pages) {
  await ev(`document.querySelector('#wb .pg[data-p="${pid}"]').click(); return 1`); await sleep(pid === 'map' ? 700 : 200);
  const pg = await J(`const m = document.querySelector('#wb .main'); return JSON.stringify({ h1: m.querySelector('h1').textContent, secs: m.querySelectorAll('section').length, chron: m.querySelectorAll('.chron li').length, spoil: m.querySelectorAll('.chron li.spoil').length, shown: [...m.querySelectorAll('.chron li.spoil')].filter(e => getComputedStyle(e).display !== 'none').length, spl: m.querySelectorAll('.spl').length, map: !!m.querySelector('.wm-frame'), len: m.innerText.length })`);
  say('  页', pid, pg.h1, pg.map ? '（地图）' : pg.chron ? `编年 ${pg.chron} 条，其中剧透 ${pg.spoil} 条、看得见 ${pg.shown} 条，开关 ${pg.spl}` : `${pg.secs} 节`, pg.len + ' 字');
  want(pg.len > 80 && (pg.secs || pg.chron || pg.map), `世界之书 ${pid} 这一页是空的`);
  if (pg.chron) want(pg.spl === 1 && pg.shown === 0, '编年那一页关着剧透还看得见后半段');
}
// 3. 地图：四个年代，点数跟数据对
await ev(`document.querySelector('#wb .pg[data-p="map"]').click(); return 1`); await sleep(900);
const tabs = await ev(`return document.querySelectorAll('.wm-tabs button').length`);
want(tabs === MAP.periods.length, `地图的年代 ${tabs}／${MAP.periods.length}`);
for (let k = 0; k < MAP.periods.length; k++) {
  await ev(`document.querySelectorAll('.wm-tabs button')[${k}].click(); return 1`); await sleep(500);
  const mp = await J(`const f = document.querySelector('.wm-frame'), im = document.querySelector('.wm-in img'); await new Promise(r => { if (im.complete && im.naturalWidth) r(); else { im.onload = r; im.onerror = r; setTimeout(r, 8000); } }); return JSON.stringify({ pins: document.querySelectorAll('.wm-pin').length, img: im.naturalWidth, src: im.getAttribute('src'), frame: [f.clientWidth, f.clientHeight], note: document.querySelector('.wm-note').textContent.slice(0, 60) })`);
  say('  地图', k, MAP.periods[k].name, JSON.stringify(mp));
  want(mp.pins === MAP.periods[k].pins.length && mp.img > 0, `地图 ${MAP.periods[k].name} 点数 ${mp.pins}／${MAP.periods[k].pins.length} 或者底图没载上`);
  if (k === 0) await shot('2_地图');
}
// 4. 点一处出小卡
await ev(`document.querySelectorAll('.wm-tabs button')[0].click(); return 1`); await sleep(500);
c = await J(`const f = document.querySelector('.wm-frame').getBoundingClientRect(); for (const p of document.querySelectorAll('.wm-pin.main i')) { const r = p.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2; if (x > f.left + 30 && x < f.right - 50 && y > f.top + 20 && y < f.bottom - 20) return JSON.stringify([x, y]); } return 'null'`);
await clickAt(...c); await sleep(400);
const card1 = await ev(`const k = document.querySelector('.wm-card'); return k.hidden ? '' : k.textContent.slice(0, 80)`);
say('点了一处', card1 || '小卡没出'); want(!!card1, '地图上点一处没出小卡');
await shot('3_小卡');
// 5. 换年代、滚轮放大
await ev(`document.querySelectorAll('.wm-tabs button')[2].click(); return 1`); await sleep(600);
const fc = await centerOf('.wm-frame');
for (let k = 0; k < 4; k++) await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: fc[0], y: fc[1], deltaX: 0, deltaY: -120 });
await sleep(400);
const zoomed = await ev(`return document.querySelector('.wm-in').style.transform + ' z2=' + document.querySelector('.wm-frame').classList.contains('z2')`);
say('放大以后', zoomed); want(/scale\((1\.[5-9]|[2-6])/.test(zoomed), '滚轮没把地图放大');
await shot('4_放大');
// 6. 小卡上的时代 → 合上书、进那一张牌的时代页，路也挪到那张牌跟前
// 放大以后挑一个还在框里的点（框外的点叫 overflow 裁掉了，点不到）
c = await J(`const f = document.querySelector('.wm-frame').getBoundingClientRect(); for (const p of document.querySelectorAll('.wm-pin i')) { const r = p.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2; if (x > f.left + 40 && x < f.right - 60 && y > f.top + 20 && y < f.bottom - 20) return JSON.stringify([x, y]); } return 'null'`);
await clickAt(...c); await sleep(400);
const chip = await ev(`const b = document.querySelector('.wm-card [data-era]'); return b ? b.dataset.era : ''`);
await ev(`const b = document.querySelector('.wm-card [data-era]'); if (b) b.click(); return 1`); await sleep(1200);
st = await J(`const s = __bk.s; return JSON.stringify({ wb: __bk.wb.open, page: s.pageOpen, f: s.f, at: Math.round(s.cam) === Math.round(__bk.camFor(s.pageOpen)) })`);
say('从地图进时代', chip, JSON.stringify(st));
want(!!chip && !st.wb && st.page === eraI(chip) && st.at, '从地图的小卡进时代页没进对，或者路没挪到那张牌跟前');
await ev(`__bk.close(); return 1`); await sleep(700);

// 7. 时代页的剧透开关（第十三张：四条主线，旅伴死的那一刻两幅，传奇之陨两幅）
const E13 = eraI('s13'), e13 = D.eras[E13], cg13 = CG.s13, nDeath = Object.keys(cg13.deaths || {}).length, nFall = Object.keys(cg13.falls || {}).length;
await ev(`__bk.open(${E13}); return 1`); await sleep(1200);
want(await ev(`const b = document.querySelector('#wbBtn'), r = b.getBoundingClientRect(), t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return getComputedStyle(b).opacity === '0' && !b.contains(t)`), '时代页开着的时候入口钮没藏起来');
const before = await spoilVis('#pg-body'), cgs0 = await ev(`return __bk.s.cgs`);
await ev(`const d = document.querySelectorAll('#pg-body details.ln'); d[2].open = true; d[0].open = false; document.querySelector('#pg-body .spl').scrollIntoView({block:'start'}); return 1`); await sleep(300);
const sc0 = await scrolls('#pg-wrap', '#pg-body');
await ev(`document.querySelector('#pg-body .spl').click(); return 1`); await sleep(700);
const after = await spoilVis('#pg-body'), cgs1 = await ev(`return __bk.s.cgs`), sc1 = await scrolls('#pg-wrap', '#pg-body');
const det = await ev(`return [...document.querySelectorAll('#pg-body details.ln')].map(d => d.open ? 1 : 0).join('')`);
say('时代页剧透 关着看得见', before, '开了看得见', after, '原画那一串', cgs0, '→', cgs1, '滚到', sc0.join(','), '→', sc1.join(','), '主线摊开着的', det);
want(before === '0/' + e13.lines.length && after === e13.lines.length + '/' + e13.lines.length, '时代页的没有你的那一版没跟着开关走');
want(cgs1 - cgs0 === nDeath, `开了剧透，死的那一刻应该多 ${nDeath} 幅进原画那一串`);
want(sc0.join() === sc1.join() && det === '0010', '切了剧透以后时代页没有原地重画（滚到哪里、哪条主线摊开着变了）');
want(await ev(`return __bk.wb.spoil && document.querySelector('#view').classList.contains('spoil-on')`), '整本的剧透没开');
want(await ev(`const a = document.activeElement; return !!(a && a.classList.contains('spl') && a.closest('#pg-body'))`), '时代页切了剧透以后焦点没回到开关上');
await shot('5_时代页');
await ev(`document.querySelector('#pg-body .spl').click(); return 1`); await sleep(500);
want((await ev(`return __bk.s.cgs`)) === cgs0, '关了剧透，死的那一刻还留在原画那一串里');
// 8. 传奇之陨不归剧透开关管：关着也看得见
const fallsVis = await ev(`return [...document.querySelectorAll('#pg-body .falls .cgb')].filter(e => e.offsetParent).length`);
say('关着剧透，传奇之陨那一栏', fallsVis, '幅'); want(fallsVis === nFall, `传奇之陨那一栏 ${fallsVis}／${nFall}`);
// 9. 小地图
const mini = await J(`const m = document.querySelector('#pg-body .mini'); return JSON.stringify(m ? { pins: m.querySelectorAll('i').length, names: [...document.querySelectorAll('#pg-body .mini-names button')].map(b => b.textContent), old: document.querySelectorAll('#pg-body ul.places').length } : null)`);
say('小地图', JSON.stringify(mini));
want(mini && mini.pins === e13.places.length && mini.names.length === e13.places.length && !mini.old, '第十三张的小地图不对');
await ev(`const m = document.querySelector('#pg-body .mini'); if (m) m.scrollIntoView({block:'center'}); return 1`); await sleep(500);
await shot('6_小地图');
await ev(`document.querySelector('#pg-body .mini').click(); return 1`); await sleep(1000);
st = await J(`return JSON.stringify({ wb: __bk.wb, hi: document.querySelectorAll('.wm-pin.hi').length, tab: [...document.querySelectorAll('.wm-tabs button')].findIndex(b => b.getAttribute('aria-pressed') === 'true'), page: __bk.s.pageOpen })`);
say('点小地图', JSON.stringify(st));
want(st.wb.open && st.wb.page === 'map' && st.hi === e13.places.length && st.tab === MAP.periods.findIndex((p) => p.eras.includes('s13')) && st.page === E13, '小地图没翻到这一纪这个年代的地图，或者亮着的点不对');
await shot('7_这一纪的地方');
// Esc 归世界之书：合上书，时代页还开着
await key('Escape'); await sleep(600);
st = await J(`return JSON.stringify({ wb: __bk.wb.open, page: __bk.s.pageOpen })`);
say('按了 Esc', JSON.stringify(st)); want(!st.wb && st.page === E13, '世界之书开着的时候 Esc 没只合上书');
// 点一个地名 → 地图挪到那一处、出小卡
await ev(`document.querySelector('#pg-body .mini-names button').click(); return 1`); await sleep(1200);
const focus = await ev(`const k = document.querySelector('.wm-card'); return k && !k.hidden ? k.querySelector('b').textContent : ''`);
say('点地名', mini && mini.names[0], '→ 小卡', focus); want(mini && focus === mini.names[0], '点地名没翻到那一处');
await ev(`__bk.closeWB(); return 1`); await sleep(500);

// 10. 一张卡片档案（旅伴，死在这一段的）：立绘四套，档案里的剧透开关
const dead = Object.keys(cg13.deaths)[0];
await ev(`__bk.openProf(${JSON.stringify(dead)}); return 1`); await sleep(900);
let pf = await J(`const s = document.querySelector('#prof'), b = s.querySelector('.pf-body'); return JSON.stringify({ open: !s.hidden, card: b.dataset.card, eb: b.querySelector('.eyebrow').textContent, hs: [...b.querySelectorAll('h3')].map(x => x.textContent), tabs: s.querySelectorAll('.pf-tabs button').length, faces: b.querySelectorAll('.pf-faces figure').length, traits: !!b.querySelector('.pf-traits'), len: b.innerText.length })`);
say('档案', dead, JSON.stringify(pf));
want(pf.open && pf.card === '1' && pf.eb.startsWith('旅伴') && pf.tabs === 4 && pf.faces === 9, `${dead} 的档案不是短卡片，或者立绘四套、表情九格不齐`);
await shot('8_档案');
const fateVis = `const f = document.querySelector('#prof .pf-fate'); return f ? getComputedStyle(f.closest('.spoil') || f).display !== 'none' : 'none'`;
want((await ev(fateVis)) === false, '档案里的下场关着剧透还看得见');
await ev(`document.querySelectorAll('#prof .pf-tabs button')[2].click(); document.querySelector('#prof .spl').scrollIntoView({block:'center'}); return 1`); await sleep(300);
// 开了剧透，开关上头多出“死于哪一年”那一条，滚动的数会变，开关在屏幕上的高度不该变
const splTop = `return Math.round(document.querySelector('#prof .spl').getBoundingClientRect().top)`;
const ps0 = [await ev(splTop)];
await ev(`document.querySelector('#prof .spl').click(); return 1`); await sleep(600);
const ps1 = [await ev(splTop)];
pf = await J(`const s = document.querySelector('#prof'); return JSON.stringify({ open: !s.hidden, name: s.querySelector('h2').textContent, tab: [...s.querySelectorAll('.pf-tabs button')].findIndex(b => b.getAttribute('aria-pressed') === 'true'), pos: s.querySelector('.pf-spr').style.backgroundPosition, cg: !!s.querySelector('.pf-fate .cgb img'), dead: !!(s.querySelector('.pf-dead') && s.querySelector('.pf-dead').offsetParent) })`);
say('档案里点了剧透 下场', await ev(fateVis), '整本开了', await ev(`return __bk.wb.spoil`), JSON.stringify(pf), '开关在屏幕上的高度', ps0.join(','), '→', ps1.join(','));
want((await ev(fateVis)) === true && pf.open && pf.name === dead && pf.cg && pf.dead && await ev(`return __bk.wb.spoil`), '档案里点了剧透，下场、死期、死的那一刻没出来');
want(pf.tab === 2 && /^66\.6/.test(pf.pos) && Math.abs(ps0[0] - ps1[0]) <= 1, '档案没有原地重画（立绘换回去了，或者开关从手指底下跑了）');
want(await ev(`const a = document.activeElement; return !!(a && a.classList.contains('spl') && a.closest('#prof'))`), '档案里切了剧透以后焦点没回到开关上');
await ev(`document.querySelector('#prof .spl').scrollIntoView({block:'start'}); return 1`); await sleep(300);
await shot('9_档案剧透');
await ev(`document.querySelector('#prof .pf-fate .cgb').click(); return 1`); await sleep(600);
want(await ev(`const v = document.querySelector('#cgv'); return !v.hidden && v.classList.contains('on') && v.querySelector('img').getAttribute('src') === ${JSON.stringify(cg13.deaths[dead].src)}`), '死的那一刻点不开');
await ev(`document.querySelector('#cgv .x').click(); return 1`); await sleep(450);
await ev(`document.querySelector('#prof .spl').scrollIntoView({block:'center'}); return 1`); await sleep(300);
const ps2 = await ev(splTop);
await ev(`document.querySelector('#prof .spl').click(); return 1`); await sleep(400);
const ps3 = await ev(splTop);
say('再点一下 下场', await ev(fateVis), '开关的高度', ps2, '→', ps3); want((await ev(fateVis)) === false && !(await ev(`return __bk.wb.spoil`)), '档案里再点一下剧透没关上');
// 关上以后底下那一大块收起来了，页不够长的时候开关只能跟着落到页尾，这不算跑
const atEnd = await ev(`const ss = [document.querySelector('#prof .pf-wrap'), document.querySelector('#prof .pf-body')]; return ss.some(s => s.scrollHeight > s.clientHeight + 1 && s.scrollTop >= s.scrollHeight - s.clientHeight - 1) || ss.every(s => s.scrollHeight <= s.clientHeight + 1)`);
want(Math.abs(ps2 - ps3) <= 1 || atEnd, '关剧透的时候开关从手指底下跑了');
await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
// 11. 相遇的卡片；传奇的档案不走卡片、不进剧透开关（关着也看得见陨落）
const meet = e13.meet.find((m) => m.p).name, fallen = Object.keys(cg13.falls)[0];
await ev(`__bk.openProf(${JSON.stringify(meet)}); return 1`); await sleep(800);
pf = await J(`const b = document.querySelector('#prof .pf-body'); return JSON.stringify({ card: b.dataset.card, eb: b.querySelector('.eyebrow').textContent.slice(0, 2), hs: [...b.querySelectorAll('h3')].map(x => x.textContent), len: b.innerText.length })`);
say('相遇', meet, JSON.stringify(pf)); want(pf.card === '1' && pf.eb === '相遇', `${meet}（相遇）没走短卡片`);
await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
await ev(`__bk.openProf(${JSON.stringify(fallen)}); return 1`); await sleep(800);
pf = await J(`const b = document.querySelector('#prof .pf-body'), f = b.querySelector('.pf-fate'); return JSON.stringify({ card: b.dataset.card, eb: b.querySelector('.eyebrow').textContent.slice(0, 2), spl: b.querySelectorAll('.spl').length, fate: !!(f && f.offsetParent), img: !!(f && f.querySelector('.cgb img')), dead: !!(b.querySelector('.pf-dead') && b.querySelector('.pf-dead').offsetParent), now: [...b.querySelectorAll('h3')].some(x => x.textContent === '这一段里') })`);
say('传奇', fallen, JSON.stringify(pf));
want(pf.card === '0' && pf.eb === '传奇' && pf.spl === 0 && pf.fate && pf.img && pf.dead && pf.now, `${fallen}（传奇）的档案变了，或者陨落进了剧透开关`);
await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
await ev(`__bk.close(); return 1`); await sleep(600);
// 12. 没有地方的牌不出“这一带”
for (const e of D.eras.filter((x) => !x.places.length)) {
  await ev(`__bk.open(${eraI(e.id)}); return 1`); await sleep(700);
  const h2 = await ev(`return [...document.querySelectorAll('#pg-body h2')].map(x => x.textContent).join('、')`);
  say('没有地方的', e.id, h2); want(!/这一带/.test(h2), `${e.id} 没有地方，却出了这一带`);
  await ev(`__bk.close(); return 1`); await sleep(500);
}
// 13. 第二十二张（单独看的时候到小纸为止）
await ev(`__bk.go(${D.eras.length}); __bk.card(${D.eras.length}); return 1`); await sleep(500);
const sheet = await ev(`const s = document.querySelector('#sheet'); return s.hidden ? '' : s.innerText.replace(/\\n+/g, '｜')`);
say('第二十二张', sheet); want(/第二十二张/.test(sheet) && /好$/.test(sheet), '第二十二张的小纸不对');
await ev(`document.querySelector('#sheet button').click(); return 1`); await sleep(300);
say(errs.length ? '这一遍有报错：\n' + [...new Set(errs)].join('\n') : '这一遍没有报错');

say('—— 二、?legacy=s13：当作第十三张没有卡片 ——');
await load(ADDR + '&legacy=s13');
await ev(`__bk.open(${E13}); return 1`); await sleep(1200);
const ln = await J(`return JSON.stringify([...document.querySelectorAll('#pg-body details.ln')].map(d => ({ hooks: [...d.querySelectorAll('.hook')].map(x => x.textContent), open: (d.querySelector('p.open') || {}).textContent || '', tails: d.querySelectorAll('ol li.cgi p').length })))`);
say('主线', ln.map((l) => l.hooks.length + ' 句钩子、' + l.tails + ' 幕带字').join('；'));
want(ln.every((l, k) => l.hooks.join('|') === e13.lines[k].hooks.join('|') && l.open === e13.lines[k].open && l.tails === e13.lines[k].acts.length), '没有卡片的时候主线没照原来那一套');
await ev(`__bk.openProf(${JSON.stringify(dead)}); return 1`); await sleep(900);
pf = await J(`const b = document.querySelector('#prof .pf-body'), f = b.querySelector('.pf-fate'); return JSON.stringify({ card: b.dataset.card, hs: [...b.querySelectorAll('h3')].map(x => x.textContent), spl: b.querySelectorAll('.spl').length, inSpoil: !!(f && f.closest('.spoil')), vis: !!(f && f.offsetParent), len: b.innerText.length })`);
say('原来那一套的档案', dead, JSON.stringify(pf));
want(pf.card === '0' && pf.spl === 1 && pf.inSpoil && !pf.vis && pf.hs.includes('身份'), `${dead} 没有卡片的时候档案没照原来那一套，或者下场没收进剧透开关`);
await ev(`document.querySelector('#prof .spl').scrollIntoView({block:'center'}); document.querySelector('#prof .spl').click(); return 1`); await sleep(600);
want(await ev(`const f = document.querySelector('#prof .pf-fate'); return !!(f && f.offsetParent && f.querySelector('.cgb img'))`), '原来那一套的档案开了剧透，死期和死的那一刻没出来');
await ev(`document.querySelector('#prof .spl').scrollIntoView({block:'start'}); return 1`); await sleep(300);
await shot('10_原来那一套的档案');
await ev(`document.querySelector('#prof .spl').click(); document.querySelector('#prof .x').click(); return 1`); await sleep(450);
await ev(`__bk.close(); return 1`); await sleep(500);
const E12 = eraI('s12');
await ev(`__bk.open(${E12}); return 1`); await sleep(900);
await ev(`__bk.openProf(document.querySelector('#pg-body .cast [data-p]').dataset.p); return 1`); await sleep(800);
want((await ev(`return document.querySelector('#prof .pf-body').dataset.card`)) === '1', 'legacy=s13 的时候别的牌也没了卡片');
await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(450);
await ev(`__bk.close(); return 1`); await sleep(500);

say('—— 三、装在牌桌外壳里（塞一个假的 window.SHELL，at 写 s05） ——');
const inj = await send('Page.addScriptToEvaluateOnNewDocument', { source: `window.__posts = []; window.SHELL = { at: 's05', post: (m) => window.__posts.push(m) };` });
await load(ADDR);
const E05 = eraI('s05'), e05 = D.eras[E05];
st = await J(`const s = __bk.s; return JSON.stringify({ page: s.pageOpen, mini: !!document.querySelector('#pg-body .mini'), at: Math.round(s.cam) === Math.round(__bk.camFor(${E05})), tb: !!document.querySelector('#toTable') })`);
say('一上来', JSON.stringify(st)); want(st.page === E05 && st.mini && st.at && st.tb, 'SHELL.at 没把第五张的时代页打开（或者小地图没补上、路没挪过去、回牌桌的钮没出）');
await ev(`document.querySelector('#pg-body .go').click(); return 1`); await sleep(300);
let posts = await J(`return JSON.stringify(window.__posts.splice(0))`);
say('从这里进', JSON.stringify(posts), '小纸', await ev(`return document.querySelector('#sheet').hidden ? '没出' : '出了'`));
const l0 = e05.lines[0];
want(posts.length === 1 && posts[0].t === 'enter' && posts[0].book === 'strife' && posts[0].era === '纷争纪' && posts[0].at === 's05' && posts[0].title === e05.title && posts[0].line === l0.name && posts[0].year === (l0.year || e05.years) && posts[0].ti === l0.ti && await ev(`return document.querySelector('#sheet').hidden`), '装在外壳里，从这里进没照说好的发 enter');
await ev(`__bk.close(); return 1`); await sleep(700);
c = await centerOf('#toTable');
want(await ev(`const b = document.querySelector('#toTable'); return getComputedStyle(b).opacity === '1' && document.elementFromPoint(${c[0]}, ${c[1]}) === b`), '回到牌桌的钮叫别的东西盖住了');
await shot('11_外壳里的路');
await clickAt(...c); await sleep(300);
posts = await J(`return JSON.stringify(window.__posts.splice(0))`);
say('回到牌桌', JSON.stringify(posts), '路动了吗', await ev(`return __bk.s.pageOpen`)); want(posts.length === 1 && posts[0].t === 'table', '回到牌桌没发 table');
// 第二十二张：小纸上多一个“从这里进”，at 写 free
await ev(`__bk.go(${D.eras.length}); __bk.card(${D.eras.length}); return 1`); await sleep(500);
say('第二十二张', await ev(`return document.querySelector('#sheet').innerText.replace(/\\n+/g, '｜')`));
await shot('12_第二十二张');
await ev(`document.querySelector('#sheet [data-free]').click(); return 1`); await sleep(300);
posts = await J(`return JSON.stringify(window.__posts.splice(0))`);
say('第二十二张 从这里进', JSON.stringify(posts));
want(posts.length === 1 && posts[0].t === 'enter' && posts[0].book === 'strife' && posts[0].at === 'free' && posts[0].line === '' && await ev(`return document.querySelector('#sheet').hidden`), '第二十二张没照说好的发 enter（at 写 free，line 空着）');
// 外壳叫打开哪一页
await ev(`window.postMessage({ aldran: 1, t: 'open', at: 's17' }, '*'); return 1`); await sleep(900);
st = await J(`const s = __bk.s; return JSON.stringify({ page: s.pageOpen, at: Math.round(s.cam) === Math.round(__bk.camFor(s.pageOpen)) })`);
say('外壳叫打开 s17', JSON.stringify(st)); want(st.page === eraI('s17') && st.at, '外壳叫打开第十七张，没打开');
await ev(`window.postMessage({ aldran: 1, t: 'open', at: 'free' }, '*'); return 1`); await sleep(900);
st = await J(`const s = __bk.s; return JSON.stringify({ page: s.pageOpen, f: s.f, sheet: !document.querySelector('#sheet').hidden })`);
say('外壳叫打开 free', JSON.stringify(st)); want(st.page === -1 && st.f === D.eras.length && st.sheet, '外壳叫打开 free，没走到第二十二张');
await ev(`document.querySelector('#sheet').click(); return 1`); await sleep(300);
// 世界之书里点了别一纪的时代 → 交给外壳换书
await ev(`__bk.openWB('moon', 'map'); return 1`); await sleep(1200);
c = await J(`const f = document.querySelector('.wm-frame').getBoundingClientRect(); for (const p of document.querySelectorAll('.wm-pin i')) { const r = p.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2; if (x > f.left + 40 && x < f.right - 60 && y > f.top + 20 && y < f.bottom - 20) return JSON.stringify([x, y]); } return 'null'`);
await clickAt(...c); await sleep(400);
const chip2 = await ev(`const b = document.querySelector('.wm-card [data-era]'); if (!b) return ''; const id = b.dataset.era; b.click(); return id`); await sleep(700);
posts = await J(`return JSON.stringify(window.__posts.splice(0))`);
say('世界之书里点了月银纪的', chip2, JSON.stringify(posts), JSON.stringify(await wbState()));
want(!!chip2 && posts.length === 1 && posts[0].t === 'goto' && posts[0].book === 'moon' && posts[0].at === chip2 && !(await wbState()).open, '世界之书里点了别一纪的时代，没交给外壳');
await send('Page.removeScriptToEvaluateOnNewDocument', { identifier: inj.result.identifier });
want(await ev(`const v = document.querySelector('#view'); return v.scrollLeft === 0 && v.scrollTop === 0`), '撑满屏的那一层（#view）自己被带着滚了');

say(bad.length ? `对不上的 ${bad.length} 处：\n` + bad.join('\n') : '三遍都对得上');
say(errs.length ? '有报错：\n' + [...new Set(errs)].join('\n') : '没有报错，没有载不下来的文件');
ws.close();
