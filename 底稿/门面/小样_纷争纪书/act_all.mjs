// 纷争纪的书全书走查：二十一张牌的时代页一页一页打开，核时代原画、牌面、各幕的节点原画、人像拼图载没载上；
// 旅伴、相遇、神与魔神、传奇有档案的一个一个点开，核立绘加表情那一张（神是显像那一张）、死期那一块、死的那一刻那一幅；
// 传奇另核“这一段里”那一段、殁在这一段的“传奇之陨”那一块和那一幅，时代页上“传奇之陨”那一栏的图。收报错和载不下来的文件。
// 11-15 介绍页收尾以后：旅伴和相遇的死期、死的那一刻收进了剧透开关，走查先把开关打开，数要跟收尾以前一样
// （节点原画 148，档案 541、其中传奇 391，死期 28，死的那一刻 14，传奇之陨 46 条 45 幅）；
// 另核旅伴和相遇的档案走的是短卡片还是原来那一套、时代页“这一带”的小地图（这张牌没有地方的不出这一栏）。
//   node act_all.mjs <宽> <高> [只查这几张，比如 s05,s16；不挑写 -] [原来那一套：all 当作全书没有卡片，s02,s05 只当这几张没有]
// 卡片二十一张都齐了以后，“没有卡片的照旧用原来那一套”靠第四个参数走查（页面认 ?legacy）。
// 本地服务器是 .claude/launch.json 的 front-strife（8769），无头 Chrome 在 9341。
import fs from 'node:fs';
const [W, H] = [+process.argv[2], +process.argv[3]];
const ONLY = (process.argv[4] || '').split(',').filter((x) => x && x !== '-'), LEGACY = process.argv[5] || '';
const PORT = 9341, ADDR = 'http://localhost:8769/local.html?skip=1' + (LEGACY ? '&legacy=' + (LEGACY === 'all' ? '' : LEGACY) : '');
const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), 'utf8'));
const CG = read('./data/cg.json'), MOON = read('./data/strife.json');
const CARDS = fs.existsSync(new URL('./data/cards.json', import.meta.url)) ? read('./data/cards.json') : {};
const MAP = fs.existsSync(new URL('./common/data/map_strife.json', import.meta.url)) ? read('./common/data/map_strife.json') : { periods: [] };
const legacyOf = (id) => !!LEGACY && (LEGACY === 'all' || LEGACY.split(',').includes(id));
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400 && !/favicon/.test(m.params.response.url)) errs.push(m.params.response.status + ' ' + m.params.response.url.replace('http://localhost:8769/', ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
errs.length = 0;      // Runtime.enable 会把这一格原先那一页报过的错重放一遍，不算这一回的
await send('Page.navigate', { url: ADDR });
await Promise.race([loaded, sleep(15000)]);
for (let k = 0; k < 150; k++) { if (await ev(`return !!(window.__bk && __bk.s.W && __bk.wb.vol)`)) break; await sleep(100); }      // 头一回开（缓存是冷的）数据来得慢，等页面真起来
await sleep(2500);
if (!(await ev(`return !!(window.__bk && __bk.setSpoil)`))) { console.log('页面没起来（__bk 没有，或者还是收尾以前的页面）'); ws.close(); process.exit(1); }
await ev(`__bk.setSpoil(true); return 1`);   // 11-15 起死期、死的那一刻收在剧透开关里，走查先打开
const imgOK = `const ok = (u) => new Promise((r) => { if (!u) { r(false); return; } const i = new Image(); i.onload = () => r(i.naturalWidth > 0); i.onerror = () => r(false); i.src = u; });`;
let bad = 0, nNodes = 0, nProf = 0, nDeath = 0, nFate = 0, nLeg = 0, nFall = 0, nFallText = 0, nGal = 0, nCard = 0, nOld = 0, nMini = 0, nNoMini = 0, nLineCard = 0, nLineOld = 0;
for (let i = 0; i < MOON.eras.length; i++) {
  const e = MOON.eras[i];
  if (ONLY.length && !ONLY.includes(e.id)) continue;
  const cg = CG[e.id] || {};
  const cards = legacyOf(e.id) ? null : CARDS[e.id] || null;
  const want = Object.values(cg.nodes || {}).reduce((n, l) => n + Object.values(l).reduce((k, v) => k + (Array.isArray(v) ? v.length : 1), 0), 0);
  const period = MAP.periods.find((p) => p.eras.includes(e.id)), wantPins = period && e.places.length ? period.pins.filter((q) => (q.eras || []).includes(e.id)).length : 0;
  await ev(`__bk.open(${i}); return 1`); await sleep(900);
  const pg = JSON.parse(await ev(`${imgOK}
    const im = document.querySelector('#pg-img');
    const key = await ok(im.getAttribute('src'));
    const tc = document.querySelector('#pg-body .tarot figure img'), tarot = tc ? await ok(tc.getAttribute('src')) : false;
    const song = document.querySelectorAll('#pg-body .tarot .song p').length;
    const nodes = [...document.querySelectorAll('#pg-body .ln .cgb img')];
    const gal = [...document.querySelectorAll('#pg-body .falls .cgb img')];
    const galOK = await Promise.all(gal.map((n) => ok(n.getAttribute('src'))));
    const res = await Promise.all(nodes.map((n) => ok(n.getAttribute('src'))));
    const pors = [...document.querySelectorAll('#pg-body i.por')];
    const atlas = pors.length ? await ok(getComputedStyle(pors[0]).backgroundImage.replace(/^url\\(["']?|["']?\\)$/g, '')) : null;
    const mini = document.querySelector('#pg-body .mini'), mimg = mini && mini.querySelector('img');
    return JSON.stringify({ open: __bk.s.pageOpen, cg: document.querySelector('#page').classList.contains('cg'), key, tarot, song, nodes: nodes.length, broken: res.filter((x) => !x).length, pors: pors.length, atlas,
      gal: gal.length, galBroken: galOK.filter((x) => !x).length,
      spl: document.querySelectorAll('#pg-body .spl').length, hidden: [...document.querySelectorAll('#pg-body .spoil')].filter((x) => getComputedStyle(x).display === 'none').length,
      ends: document.querySelectorAll('#pg-body details.end.spoil').length, oldPlaces: document.querySelectorAll('#pg-body ul.places').length,
      lines: [...document.querySelectorAll('#pg-body details.ln')].map((d) => ({ name: (d.querySelector('.nm') || {}).textContent || '', intro: (d.querySelector('.intro') || {}).textContent || '', acts: [...d.querySelectorAll('ol > li')].map((x) => (x.querySelector('b') || {}).textContent || ''), hooks: [...d.querySelectorAll('.hook')].map((x) => x.textContent), open: (d.querySelector('p.open') || {}).textContent || '', tails: d.querySelectorAll('ol li.cgi p').length + [...d.querySelectorAll('ol li.txt')].filter((x) => x.textContent.length > ((x.querySelector('b') || {}).textContent || '').length).length })),
      mini: mini ? { pins: mini.querySelectorAll('i').length, names: document.querySelectorAll('#pg-body .mini-names button').length, img: mimg ? await ok(mimg.getAttribute('src')) : false } : null,
      people: [...new Set([...document.querySelectorAll('#pg-body [data-p]')].map((x) => x.dataset.p))], noimg: document.querySelectorAll('#pg-body .noimg').length });`));
  const msg = [];
  if (pg.open !== i || !pg.cg || !pg.key) msg.push('时代原画没出来');
  if (!pg.tarot || !pg.song) msg.push('牌面或牌文没出来');
  if (pg.nodes !== want) msg.push(`节点原画 ${pg.nodes}／${want}`);
  if (pg.broken) msg.push(`节点原画 ${pg.broken} 幅载不上`);
  if (pg.pors && !pg.atlas) msg.push('人像拼图载不上');
  const wantF = Object.keys(cg.falls || {}).length, wantFT = e.legends.filter((g) => g.end && g.p).length, wantLeg = e.legends.filter((g) => g.p).length;
  if (pg.gal !== wantF) msg.push(`传奇之陨那一栏 ${pg.gal}／${wantF}`);
  if (pg.galBroken) msg.push(`传奇之陨那一栏 ${pg.galBroken} 幅载不上`);
  // 11-15：剧透开关在不在、开了以后没有藏着的；主线用的是卡片上的钩子还是原来的；“这一带”是小地图
  if (pg.spl !== 1) msg.push(`时代页的剧透开关 ${pg.spl} 个`);
  if (pg.hidden) msg.push(`开了剧透还有 ${pg.hidden} 处藏着`);
  if (pg.ends !== e.lines.filter((l) => l.ending).length) msg.push(`没有你的那一版 ${pg.ends}／${e.lines.filter((l) => l.ending).length}`);
  if (pg.oldPlaces) msg.push('“这一带”还是原来那一串地名');
  let lineCard = 0;
  e.lines.forEach((l, k) => {
    const got = pg.lines[k], lc = cards && cards.lines && cards.lines[l.name];
    if (!got || got.name !== l.name) { msg.push(`主线 ${l.name} 没出来`); return; }
    const sty = cards && cards.story && cards.story[l.name];      // 11-21 剧情润色：有稿的核介绍、睁眼、幕名
    if (sty) {
      lineCard++;
      if (got.intro !== sty.intro || got.hooks.length || got.open !== ((lc && lc.open) || l.open || '')) msg.push(`${l.name} 介绍或睁眼的地方不是剧情稿上的`);
      sty.acts.forEach((a) => { if (!got.acts.some((h) => h.endsWith(a.name))) msg.push(`${l.name} ${a.tag} 幕名没出来`); });
    } else if (lc) {
      lineCard++;
      if (got.hooks.join('|') !== (lc.hook ? [lc.hook] : []).join('|') || got.open !== (lc.open || l.open || '')) msg.push(`${l.name} 钩子或睁眼的地方不是卡片上的`);
      if (got.tails) msg.push(`${l.name} 各幕还带着 ${got.tails} 段字`);
    } else if (got.hooks.join('|') !== l.hooks.join('|') || got.open !== (l.open || '')) msg.push(`${l.name} 钩子或睁眼的地方跟原来的不一样`);
  });
  nLineCard += lineCard; nLineOld += e.lines.length - lineCard;
  if (wantPins) {
    if (!pg.mini) msg.push('小地图没出来');
    else {
      if (pg.mini.pins !== wantPins || pg.mini.names !== e.places.length) msg.push(`小地图 ${pg.mini.pins}／${wantPins} 点、地名 ${pg.mini.names}／${e.places.length}`);
      if (!pg.mini.img) msg.push('小地图的底图载不上');
      nMini++;
    }
  } else { if (pg.mini) msg.push('这张牌没有地方，却出了小地图'); nNoMini++; }
  nNodes += pg.nodes;
  let profs = 0, spr = 0, deaths = 0, fates = 0, legs = 0, falls = 0, fallText = 0, cardN = 0, oldN = 0;
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
      const p = document.querySelector('#prof'), s = p.querySelector('.pf-spr'), bg = getComputedStyle(s).backgroundImage;
      const u = bg && bg !== 'none' ? bg.replace(/^url\\(["']?|["']?\\)$/g, '') : '';
      const d = p.querySelector('.pf-fate .cgb img'), eb = (p.querySelector('.pf-body .eyebrow') || {}).textContent || '';
      const hs = [...p.querySelectorAll('.pf-body h3')].map((x) => x.textContent), b = p.querySelector('.pf-body');
      return JSON.stringify({ noart: p.classList.contains('noart'), god: p.classList.contains('artonly'), sheet: u ? await ok(u) : null, tabs: p.querySelectorAll('.pf-tabs button').length, faces: p.querySelectorAll('.pf-faces figure').length,
        legend: eb.startsWith('传奇'), kind: eb.slice(0, 2), now: hs.includes('这一段里'), card: b.dataset.card === '1', spl: b.querySelectorAll('.spl').length, inSpoil: !!(b.querySelector('.pf-fate') && b.querySelector('.pf-fate').closest('.spoil')),
        hidden: [...b.querySelectorAll('.spoil')].filter((x) => getComputedStyle(x).display === 'none').length,
        fate: !!p.querySelector('.pf-fate'), dead: !!p.querySelector('.pf-dead'), death: d ? await ok(d.getAttribute('src')) : null, text: p.querySelector('.pf-body').textContent.length });`));
    profs++;
    if (pf.sheet === false) msg.push(`${name} 的立绘那一张载不上`);
    if (pf.sheet) { spr++; if (!pf.god && (pf.tabs !== 4 || pf.faces !== 9)) msg.push(`${name} 衣服 ${pf.tabs} 套、表情 ${pf.faces} 格`); }
    if (pf.fate !== pf.dead) msg.push(`${name} 死期那一条和那一块对不上`);
    if (pf.death === false) msg.push(`${name} 死的那一刻载不上`);
    if (pf.hidden) msg.push(`${name} 开了剧透还有 ${pf.hidden} 处藏着`);
    if (pf.legend) {
      legs++;
      if (!pf.now) msg.push(`${name} 没有这一段里那一段`);
      if (pf.fate) fallText++;
      if (pf.death) falls++;
      if (pf.card || pf.spl || pf.inSpoil) msg.push(`${name} 是传奇，档案不该走卡片、不该进剧透开关`);
    } else {
      if (pf.fate) fates++;
      if (pf.death) deaths++;
      if (pf.kind === '旅伴' || pf.kind === '相遇') {      // 有卡片的走短卡片，没有的照旧；死期那一块收在剧透开关里
        const wantCard = !!(cards && cards.people && cards.people[name]);
        if (pf.card !== wantCard) msg.push(`${name} ${wantCard ? '有卡片却走了原来那一套' : '没有卡片却走了卡片'}`);
        if (pf.card) cardN++; else oldN++;
        if (pf.fate && !pf.inSpoil) msg.push(`${name} 的死期没收进剧透开关`);
      } else if (pf.card || pf.spl) msg.push(`${name} 是神，档案不该走卡片`);
    }
    if (pf.text < 60) msg.push(`${name} 的档案是空的`);
    await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(380);
  }
  const wantD = Object.keys(cg.deaths || {}).length;
  if (deaths !== wantD) msg.push(`死的那一刻 ${deaths}／${wantD}`);
  if (legs !== wantLeg) msg.push(`传奇档案 ${legs}／${wantLeg}`);
  if (fallText !== wantFT) msg.push(`传奇之陨那一块 ${fallText}／${wantFT}`);
  if (falls !== wantF) msg.push(`传奇之陨的图 ${falls}／${wantF}`);
  nProf += profs; nDeath += deaths; nFate += fates; nLeg += legs; nFall += falls; nFallText += fallText; nGal += pg.gal; nCard += cardN; nOld += oldN;
  // “‖”以前那一截跟收尾以前的走查一个样子，拿来逐行对
  console.log(e.id, e.label, `节点 ${pg.nodes}／${want}`, `人像 ${pg.pors}（没图的 ${pg.noimg}）`, `档案 ${profs}（有立绘的 ${spr}）`, `死期 ${fates}`, `死的那一刻 ${deaths}／${wantD}`, `传奇 ${legs}／${wantLeg}`, `陨 ${fallText}（图 ${falls}／${wantF}）`,
    '‖', `主线卡片 ${lineCard}／${e.lines.length}`, `短卡片 ${cardN}、原来那一套 ${oldN}`, pg.mini ? `小地图 ${pg.mini.pins} 点` : '没有这一带', msg.length ? '｜' + msg.join('；') : '');
  bad += msg.length;
  await ev(`__bk.close(); return 1`); await sleep(500);
}
console.log(`合计：节点原画 ${nNodes}，档案 ${nProf}（其中传奇 ${nLeg}），死期 ${nFate}，死的那一刻 ${nDeath}，传奇之陨 ${nFallText} 条、档案里的图 ${nFall} 幅、时代页那一栏 ${nGal} 幅；对不上的 ${bad} 处`);
console.log(`卡片：主线走卡片的 ${nLineCard} 条、照原来的 ${nLineOld} 条；旅伴和相遇的档案走短卡片的 ${nCard} 份、原来那一套 ${nOld} 份；小地图 ${nMini} 张，没有地方、不出这一栏的 ${nNoMini} 张${LEGACY ? '（这一遍是 legacy=' + LEGACY + '）' : ''}`);
console.log(errs.length ? '报错和载不下来的：\n' + [...new Set(errs)].slice(0, 40).join('\n') : '页面没有报错，没有载不下来的文件');
ws.close();
