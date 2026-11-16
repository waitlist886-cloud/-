// 迷宫纪的书全书走查：往下的井里四十三幅壁画一幅一幅停到跟前，核贴图载没载上、底下的题签、点开的大图；
// 绳上挂的委托单一张一张点开；六个时代页一页一页打开，核开头那一幅、这一段的委托、各条主线的壁画、人像拼图、灾祸的图、迷宫和冒险团、“这一带”那一小幅地图；
// 旅伴、相遇、传奇有档案的一个一个点开，核立绘加表情那一张；走到井底那一句。收报错和载不下来的文件。
// 11-15 介绍页收尾以后：先开剧透再走（主线的“没有你的那一版”、旅伴和相遇的下场收在剧透开关里）；委托单只留正面；
// 有短卡片的时代（data/cards.json）档案走卡片，没有的照旧，两种各数各的；名单上原来没有档案、这一回有了卡片的另数（“只有卡片的”）。
//   node act_all.mjs <宽> <高> [只查这几页，比如 q1,q4；全查写 all] [当这几页还没有卡片，比如 q1,q5]
// 后一个参数是为了把“没有卡片的时代照旧”那一路也走到：走查的时候把这几页的卡片从 data/cards.json 里拿掉再喂给页面（只在这一遍里，不写盘）。
// 本地服务器是 .claude/launch.json 的 front-maze（8771），无头 Chrome 在 9337。
import fs from 'node:fs';
const [W, H, ONLY, DROP] = [+process.argv[2], +process.argv[3], (process.argv[4] || '').split(',').filter((x) => x && x !== 'all'), (process.argv[5] || '').split(',').filter(Boolean)];
const PORT = 9337, BASE = 'http://localhost:8771/', ADDR = BASE + 'local.html?sim=1';
const readJ = (p, d) => { try { return JSON.parse(fs.readFileSync(new URL(p, import.meta.url), 'utf8')); } catch (e) { return d; } };
const D = readJ('./data/maze.json'), MU = readJ('./data/mural.json', {}), CARDS = readJ('./data/cards.json', {}), MAP = readJ('./common/data/map_maze.json', null);
for (const k of DROP) delete CARDS[k];
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Fetch.requestPaused') { send('Fetch.fulfillRequest', { requestId: m.params.requestId, responseCode: 200, responseHeaders: [{ name: 'Content-Type', value: 'application/json; charset=utf-8' }], body: Buffer.from(JSON.stringify(CARDS), 'utf8').toString('base64') }); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400 && !/favicon/.test(m.params.response.url)) errs.push(m.params.response.status + ' ' + m.params.response.url.replace(BASE, ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300)); return r.result && r.result.result ? r.result.result.value : undefined; };
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
if (DROP.length) { await send('Fetch.enable', { patterns: [{ urlPattern: '*data/cards.json*' }] }); console.log(`（这一遍当 ${DROP.join('、')} 还没有卡片）`); }
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 700 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR });
await Promise.race([loaded, sleep(15000)]);
for (let i = 0; i < 60; i++) { if (await ev('return !!(window.__mz && __mz.state)')) break; await sleep(200); }
for (let i = 0; i < 40; i++) { if (await ev('return !!(window.Codex && Codex.state.maps.length)')) break; await sleep(150); }      // 等地图的数据（时代页“这一带”要用）
await ev(`if (__mz.setSpoil) __mz.setSpoil(true); return 1`);   // 11-15 起主线的没有你的那一版、旅伴和相遇的下场收在剧透开关里，走查先打开
const imgOK = `const ok = (u) => new Promise((r) => { const i = new Image(); i.onload = () => r(i.naturalWidth > 0); i.onerror = () => r(false); i.src = u; });`;
let bad = 0;
const glOn = await ev('return __mz.gl()');
if (!glOn) { console.log('没有 WebGL，走的是一圈一段往下排的那一路'); }
const btn = JSON.parse(await ev(`${imgOK} const b = document.querySelector('#wbBtn'), im = b && b.querySelector('img'); return JSON.stringify({ has: !!b, img: im && im.getAttribute('src') ? await ok(im.getAttribute('src')) : false })`));
if (!btn.has || !btn.img) { console.log('世界之书的入口' + (btn.has ? '那一枚图没载上' : '没有')); bad++; }

// 一、井里：一幅一幅停到跟前
const K = await ev('return __mz.state().K');
let mOK = 0, mTex = 0;
for (let k = 0; k < K; k++) {
  await ev(`__mz.go(${k}); __mz.tick(16); return 1`);
  let tex = false;
  for (let i = 0; i < 40 && glOn; i++) { await ev('__mz.tick(32); return 1'); if (await ev(`return __mz.texOK(${k})`)) { tex = true; break; } await sleep(60); }
  for (let i = 0; i < 8; i++) await ev('__mz.tick(60); return 1');
  const st = JSON.parse(await ev(`const s = __mz.state(), c = document.querySelector('#cap'), st = __mz.STOPS[${k}];
    return JSON.stringify({ cur: s.curStop, on: c.classList.contains('on'), name: c.querySelector('b').textContent, want: st.name, ring: s.ring, wantRing: st.ring, has: __mz.hasMural(${k}) })`));
  const msg = [];
  if (glOn && st.cur !== k) msg.push(`停在第 ${st.cur} 幅`);
  if (glOn && !st.on) msg.push('题签没出来');
  if (st.name !== st.want) msg.push(`题签是「${st.name}」`);
  if (st.ring !== st.wantRing) msg.push(`深度板在第 ${st.ring} 圈`);
  if (st.has && glOn && !tex) msg.push('贴图没载上');
  if (!st.has) msg.push('还没有壁画');
  mTex += tex ? 1 : 0;
  // 点开看大图
  await ev(`__mz.openMural(${k}); return 1`); await sleep(380);
  const mv = JSON.parse(await ev(`${imgOK} const v = document.querySelector('#mv'), im = v.querySelector('.pic img');
    return JSON.stringify({ open: !v.hidden, img: im.getAttribute('src') ? await ok(im.getAttribute('src')) : null, title: (v.querySelector('.txt b') || {}).textContent, go: !!v.querySelector('.txt .go') })`));
  if (!mv.open) msg.push('大图没打开');
  if (st.has && !mv.img) msg.push('大图载不上');
  if (mv.title !== st.want) msg.push('大图的名字对不上');
  await ev('__mz.closeMural(); return 1'); await sleep(360);
  mOK += msg.length ? 0 : 1;
  if (msg.length) { console.log('壁画', k, st.want, '｜' + msg.join('；')); bad += msg.length; }
}
console.log(`井里的壁画 ${K} 幅：走查过的 ${mOK}，贴图载上的 ${mTex}`);
// 绳上挂的委托单：只留正面（委托人的话），单头、背面、结案栏收起来了
const CM = await ev('return __mz.comms().length');
let cOK = 0, shownAny = 0;
for (let i = 0; i < CM; i++) {
  await ev(`__mz.openComm(${i}); return 1`); await sleep(340);
  const c = JSON.parse(await ev(`const v = document.querySelector('#cv'), cm = v.querySelector('.comm');
    return JSON.stringify({ open: !v.hidden, h3: cm ? cm.querySelector('h3').textContent : '', front: cm ? cm.querySelector('.front').textContent.length : 0, rows: cm ? cm.querySelectorAll('dt').length : 0, more: cm ? cm.querySelectorAll('details').length : 0 })`));
  const msg = [];
  if (!c.open) msg.push('没打开');
  if (c.front < 20) msg.push('正面没字');
  if (c.rows || c.more) msg.push(`单头和背面还露着 ${c.rows} 行`);
  await ev('__mz.closeComm(); return 1'); await sleep(320);
  cOK += msg.length ? 0 : 1;
  if (msg.length) { console.log('委托单', i, c.h3, '｜' + msg.join('；')); bad += msg.length; }
}
// 停到每一圈头一幅，看绳上挂出来的单子
for (let k = 0; k < K && glOn; k++) {
  await ev(`__mz.go(${k}); for (let i = 0; i < 6; i++) __mz.tick(40); return 1`);
  shownAny += await ev('return __mz.comms().filter((c) => c.shown).length');
}
console.log(`委托单 ${CM} 张：点开对的 ${cOK}（只有正面）；一幅一幅停下来时屏幕上挂着的单子合计 ${shownAny}`);
// 井底：那一句，和底下 1001 年今天的“从这里进”（没有 WebGL 的那一路，它在列表最底下）
await ev(`__mz.go(${K}); for (let i = 0; i < 40; i++) __mz.tick(50); return 1`);
const end = JSON.parse(await ev(`const b = document.querySelector('#endgo'), lb = document.querySelector('#list button.end');
  return JSON.stringify({ on: document.querySelector('#endtx').classList.contains('on'), go: !!b && getComputedStyle(b).pointerEvents !== 'none', list: !!lb })`));
if (!end.on) { console.log('走到井底那一句没出来'); bad++; }
if (glOn ? !end.go : !end.list) { console.log('井底那一枚“从这里进”点不到'); bad++; }

// 二、时代页
let nCg = 0, nProf = 0, nSpr = 0, nCard = 0, nOnly = 0, nEnd = 0, nFate = 0, nMini = 0;
for (let i = 0; i < D.eras.length; i++) {
  const e = D.eras[i];
  if (ONLY.length && !ONLY.includes(e.id)) continue;
  const PF = readJ(`./data/prof/${e.id}.json`, {}), cards = (CARDS[e.id] && CARDS[e.id].people) || {}, lcards = (CARDS[e.id] && CARDS[e.id].lines) || {};
  const folk = e.cast.concat(e.meet || []), noP = new Set(folk.filter((c) => !c.p).map((c) => c.name));
  const per = MAP ? MAP.periods.find((p) => p.eras.includes(e.id)) : null, wantPins = per ? per.pins.filter((q) => (q.eras || []).includes(e.id)).length : 0;
  await ev(`__mz.openEra(${i}); return 1`); await sleep(900);
  const pg = JSON.parse(await ev(`${imgOK}
    const im = document.querySelector('#pg-img'), src = im.getAttribute('src');
    const key = src ? await ok(src) : null;
    const comms = document.querySelectorAll('#pg-body .crow .comm').length;
    const cgs = [...document.querySelectorAll('#pg-body .ln .cgb img')], res = await Promise.all(cgs.map((n) => ok(n.getAttribute('src'))));
    const pors = [...document.querySelectorAll('#pg-body i.por')];
    const atlas = pors.length ? await ok(getComputedStyle(pors[0]).backgroundImage.replace(/^url\\(["']?|["']?\\)$/g, '')) : null;
    const thumbs = [...document.querySelectorAll('#pg-body .boss .thumb[data-k]')], tRes = await Promise.all(thumbs.map((t) => ok(getComputedStyle(t).backgroundImage.replace(/^url\\(["']?|["']?\\)$/g, ''))));
    const vis = (el) => getComputedStyle(el).display !== 'none';
    const mini = document.querySelector('#pg-body .mini'), mimg = mini && mini.querySelector('img');
    return JSON.stringify({ open: __mz.state().page, cg: document.querySelector('#page').classList.contains('cg'), key, comms,
      commRows: document.querySelectorAll('#pg-body .crow dt, #pg-body .crow details').length,
      lines: document.querySelectorAll('#pg-body details.ln').length, cgs: cgs.length, broken: res.filter((x) => !x).length, pors: pors.length, atlas,
      boss: document.querySelectorAll('#pg-body .boss figure').length, tBroken: tRes.filter((x) => !x).length,
      mz: document.querySelectorAll('#pg-body ul.mz li').length, mzLong: [...document.querySelectorAll('#pg-body ul.mz p.w')].filter((p) => p.textContent.length > 130).length,
      spl: document.querySelectorAll('#pg-body .spl').length, ends: [...document.querySelectorAll('#pg-body details.end')].filter(vis).length,
      hooks: [...document.querySelectorAll('#pg-body details.ln')].map((d) => d.querySelectorAll('.hook').length),
      mini: !!mini, miniImg: mimg ? await ok(mimg.getAttribute('src')) : null, dots: mini ? mini.querySelectorAll('i').length : 0, names: document.querySelectorAll('#pg-body .mini-names button').length,
      places: document.querySelectorAll('#pg-body ul.places').length,
      people: [...new Set([...document.querySelectorAll('#pg-body [data-p]')].map((x) => x.dataset.p))], noimg: document.querySelectorAll('#pg-body .noimg').length });`));
  const msg = [];
  const want = e.lines.filter((l) => MU[l.mural]).length, wantEnd = e.lines.filter((l) => l.ending).length;
  if (pg.open !== i) msg.push('时代页没打开');
  if (want && (!pg.cg || !pg.key)) msg.push('开头那一幅没出来');
  if (pg.comms !== e.comms.length) msg.push(`委托 ${pg.comms}／${e.comms.length}`);
  if (pg.commRows) msg.push('委托的单头和背面还露着');
  if (pg.lines !== e.lines.length) msg.push(`主线 ${pg.lines}／${e.lines.length}`);
  if (pg.cgs !== want) msg.push(`壁画 ${pg.cgs}／${want}`);
  if (pg.broken) msg.push(`壁画 ${pg.broken} 幅载不上`);
  if (pg.pors && !pg.atlas) msg.push('人像拼图载不上');
  if (pg.boss !== (e.bosses || []).length) msg.push(`灾祸 ${pg.boss}／${(e.bosses || []).length}`);
  if (pg.tBroken) msg.push(`灾祸的图 ${pg.tBroken} 张载不上`);
  if (pg.mz !== (e.mazes || []).length + (e.teams || []).length) msg.push(`迷宫和冒险团 ${pg.mz}／${(e.mazes || []).length + (e.teams || []).length}`);
  if (pg.mzLong) msg.push(`迷宫和冒险团有 ${pg.mzLong} 条不止头一句`);
  if (pg.spl !== 1) msg.push(`剧透开关 ${pg.spl} 个`);
  if (pg.ends !== wantEnd) msg.push(`没有你的那一版 ${pg.ends}／${wantEnd}`);
  e.lines.forEach((l, k) => { const lc = lcards[l.name], w = lc ? (lc.hook ? 1 : 0) : l.hooks.length; if (pg.hooks[k] !== w) msg.push(`${l.name} 的钩子 ${pg.hooks[k]}／${w}`); });
  if (pg.places) msg.push('“这一带”那一串地名还在');
  if (MAP && e.places.length) {
    if (!pg.mini) msg.push('“这一带”的小地图没出来');
    else { if (!pg.miniImg) msg.push('小地图的底图载不上'); if (pg.dots !== wantPins) msg.push(`小地图上的点 ${pg.dots}／${wantPins}`); if (pg.names !== e.places.length) msg.push(`小地图底下的地名 ${pg.names}／${e.places.length}`); }
  }
  nCg += pg.cgs; nEnd += pg.ends; nMini += pg.mini ? 1 : 0;
  let profs = 0, spr = 0, card = 0, only = 0, fates = 0;
  for (const name of pg.people) {
    await ev(`document.querySelector('#pg-body [data-p=${JSON.stringify(name)}]').click(); return 1`);
    let st = null;
    for (let k = 0; k < 40; k++) {
      await sleep(80);
      st = JSON.parse(await ev(`const p = document.querySelector('#prof'); return JSON.stringify({ open: !p.hidden && p.classList.contains('on'), name: (p.querySelector('.pf-body h2') || {}).textContent || '' })`));
      if (st.open && st.name === name) break;
    }
    if (!st.open || st.name !== name) { msg.push(`${name} 的档案没打开`); continue; }
    const pf = JSON.parse(await ev(`${imgOK}
      const p = document.querySelector('#prof'), s = p.querySelector('.pf-spr'), bg = getComputedStyle(s).backgroundImage, b = p.querySelector('.pf-body');
      const u = bg && bg !== 'none' ? bg.replace(/^url\\(["']?|["']?\\)$/g, '') : '';
      const sp = b.querySelector('.spoil');
      return JSON.stringify({ sheet: u ? await ok(u) : null, tabs: p.querySelectorAll('.pf-tabs button').length, faces: p.querySelectorAll('.pf-faces figure').length,
        card: b.dataset.card === '1', fate: !!sp && getComputedStyle(sp).display !== 'none', spl: b.querySelectorAll('.spl').length, text: b.textContent.length });`));
    const isOnly = noP.has(name), kind = (PF[name] || {}).kind, isFolk = folk.some((c) => c.name === name) && kind !== 'legend';
    if (isOnly) only++; else profs++;
    if (pf.sheet === false) msg.push(`${name} 的立绘那一张载不上`);
    if (pf.sheet) { spr++; if (pf.tabs !== 4 || pf.faces !== 9) msg.push(`${name} 衣服 ${pf.tabs} 套、表情 ${pf.faces} 格`); }
    if (pf.text < 40) msg.push(`${name} 的档案是空的`);
    const wantCard = isFolk && !!cards[name];
    if (pf.card !== wantCard) msg.push(`${name} ${wantCard ? '有卡片，开出来的是旧档案' : '没有卡片，开出来的却是卡片'}`);
    if (pf.card) card++;
    const wantFate = isFolk && !!(PF[name] || {}).fate;
    if (pf.fate !== wantFate) msg.push(`${name} 的下场${wantFate ? '没出来' : '不该有'}`);
    if (pf.fate) { fates++; if (pf.spl !== 1) msg.push(`${name} 档案里的剧透开关 ${pf.spl} 个`); }
    await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(360);
  }
  nProf += profs; nSpr += spr; nCard += card; nOnly += only; nFate += fates;
  console.log(e.id, e.title, `委托 ${pg.comms}`, `主线 ${pg.lines}`, `壁画 ${pg.cgs}／${want}`, `人像 ${pg.pors}（没图的 ${pg.noimg}）`, `档案 ${profs}（有立绘的 ${spr}）`, `灾祸 ${pg.boss}`, `迷宫和冒险团 ${pg.mz}`,
    `｜没有你的那一版 ${pg.ends}`, `下场 ${fates}`, `走卡片的 ${card - only}、照旧的 ${profs + only - card}${only ? '，另有只有卡片的 ' + only : ''}`, `小地图 ${pg.mini ? pg.dots + ' 点' : '无'}`, msg.length ? '｜' + msg.join('；') : '');
  bad += msg.length;
  await ev(`__mz.closeEra(); return 1`); await sleep(500);
}
console.log(`合计：时代页里的壁画 ${nCg}，档案 ${nProf}（有立绘的 ${nSpr}）；没有你的那一版 ${nEnd}，下场 ${nFate}；档案里走卡片的 ${nCard - nOnly}、照旧的 ${nProf + nOnly - nCard}（传奇，和还没有卡片的旅伴、相遇），另有原来没有档案、只有卡片的 ${nOnly}；小地图 ${nMini} 页；对不上的 ${bad} 处`);
console.log(errs.length ? '报错和载不下来的：\n' + [...new Set(errs)].slice(0, 40).join('\n') : '页面没有报错，没有载不下来的文件');
if (DROP.length) await send('Fetch.disable');
ws.close();
