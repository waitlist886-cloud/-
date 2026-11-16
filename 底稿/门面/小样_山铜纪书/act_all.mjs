// 山铜纪的书全书走查：往前走的路上三十六块碑和无字碑一块一块走到跟前、点开、翻面，核立牌、碑的图和碑面刻的字，路当中两个人哪一年是哪一身，路分开和走到头那两段；
// 六个时代页一页一页打开，核时代原画、这一段的碑那一排、各幕的节点原画、人像拼图、灾祸的图；
// 旅伴、相遇、传奇、神与魔神有档案的一个一个点开，核立绘加表情那一张（神是显像那一张）、死期那一块。收报错和载不下来的文件。
// 11-15 介绍页收尾以后：下场、死期死因、死的那一刻收进了剧透开关，走查先把开关打开再走；各页另核剧透开关、没有你的那一版、“这一带”的小地图，
// 有短卡片的时代（data/cards.json）核档案走的是不是卡片；死期、死的那一刻、下场照 data/prof、data/cg.json 的数对。
//   node act_all.mjs <宽> <高> [只查这几页，比如 p1,p4]
// 本地服务器是 .claude/launch.json 的 front-bronze（8770），无头 Chrome 在 9336。
import fs from 'node:fs';
const [W, H, ONLY] = [+process.argv[2], +process.argv[3], (process.argv[4] || '').split(',').filter(Boolean)];
const PORT = 9336, BASE = 'http://localhost:8770/', ADDR = BASE + 'local.html?skip=1';
const rd = (p, dflt) => { try { return JSON.parse(fs.readFileSync(new URL(p, import.meta.url), 'utf8')); } catch (e) { return dflt; } };
const CG = rd('./data/cg.json', {}), D = rd('./data/bronze.json'), CARDS = rd('./data/cards.json', {});
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400 && !/favicon/.test(m.params.response.url)) errs.push(m.params.response.status + ' ' + m.params.response.url.replace(BASE, ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 700 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR });
await Promise.race([loaded, sleep(15000)]);
for (let i = 0; i < 60; i++) { if (await ev('return !!(window.__bk && __bk.s.W)')) break; await sleep(200); }
const NEW = await ev(`return !!__bk.setSpoil`);          // 收尾以前的页面没有剧透开关（拿这一支去量旧页面的数也行）
await ev(`if (__bk.setSpoil) __bk.setSpoil(true); return 1`);   // 11-15 起下场、死期、死的那一刻收在剧透开关里，走查先打开
if (NEW) for (let i = 0; i < 50; i++) { if ((await ev('return __bk.wb.maps.length')) >= 1) break; await sleep(100); }      // 等世界之书的地图到了，小地图才出得来
const imgOK = `const ok = (u) => new Promise((r) => { const i = new Image(); i.onload = () => r(i.naturalWidth > 0); i.onerror = () => r(false); i.src = u; });`;
let bad = 0;

// 一、路上：门洞里开头那几句，路边三十六块碑和无字碑一块一块走到跟前，核立牌在不在屏幕里、底下浮出来的名字；
//    点开碑面，核碑的图、碑面刻的字（正名一行排得下、刻得下）、翻面；路当中两个人哪一年是哪一身；走到头那几句
const NS = await ev('return __bk.s.NS');
let stOK = 0, stImg = 0, stTxt = 0;
const settle = async (n = 40) => { for (let k = 0; k < n; k++) { await ev('__bk.tick(32); return 1'); await sleep(60); if (await ev('return __bk.ready()')) return true; } return false; };
await ev('__bk.z(0); return 1'); await settle();
const g0 = JSON.parse(await ev(`return JSON.stringify({ lead: +getComputedStyle(document.querySelector('#lead')).opacity, h2: (document.querySelector('#lead h2') || {}).textContent, walkers: __bk.walkers().length })`));
if (!(g0.lead > 0.9 && g0.h2 === '山铜纪')) { console.log('开头门洞那几句没出来'); bad++; }
const WANT = { bal: new Map(), sor: new Map() };
for (const who of ['bal', 'sor']) for (const [yr, key] of await ev(`return __bk.RD.${who}.map((r) => [r[0], r[1]])`)) WANT[who].set(key, yr);
for (let i = 0; i < NS; i++) {
  await ev(`__bk.go(${i}); return 1`);
  if (!(await settle())) console.log('碑', i, '图等了很久还没载完');
  const road = JSON.parse(await ev(`const t = __bk.STL[${i}], s = __bk.s, r = t.el.getBoundingClientRect();
    return JSON.stringify({ name: t.end ? '无字碑' : t.s.name, year: s.year, focus: s.focus, lbl: s.lbl, vis: t.vis, walkers: __bk.walkers(),
      inView: r.width > 20 && r.left > -r.width * 0.25 && r.right < innerWidth + r.width * 0.25 && r.top < innerHeight && r.bottom > 0, img: t.img ? (t.img.complete && t.img.naturalWidth > 0) : null });`));
  const msg = [];
  if (!road.vis || !road.inView) msg.push('走到跟前碑不在屏幕里');
  if (road.focus !== i) msg.push('没对上这一块');
  if (road.lbl !== road.name) msg.push(`碑底下的名字是「${road.lbl}」`);
  if (road.img === false) msg.push('立牌的图没载上');
  if (!road.walkers.length) msg.push('路当中没有人');
  for (const w of road.walkers) {          // 换装的年份：哪一身亮得最多，那一身的年份不该晚于这一处的年份
    const [key, op] = w.split(':');
    const who = key.startsWith('w_bal') ? 'bal' : 'sor', yr = WANT[who].get(key);
    if (+op > 0.6 && yr > road.year + 6) msg.push(`${key} 是 ${yr} 年起的那一身，这里才 ${road.year} 年`);
  }
  if (road.name === '无字碑') {
    await ev(`__bk.stele(${i}); return 1`); await sleep(300);
    const ok = await ev(`return !document.querySelector('#sheet').hidden && document.querySelectorAll('#sheet .half').length === 1 && document.querySelector('#sheet .half').innerHTML.split('<br>').length === 4`);
    if (!ok) msg.push('无字碑点开以后碑基那四处半行没出来');
    await ev(`document.querySelector('#sheet').hidden = true; return 1`);
  } else {
    await ev(`__bk.stele(${i}); return 1`);
    await settle(30);
    await ev('__bk.flip(); return 1'); await sleep(160);
    const r = JSON.parse(await ev(`${imgOK}
      const el = document.querySelector('#stv .stage .st');
      const imgs = [...el.querySelectorAll('img')], res = await Promise.all(imgs.map((m) => ok(m.getAttribute('src') || m.dataset.src)));
      const fr = el.querySelector('.f.fr .face'), bk = el.querySelector('.f.bk .face'), tt = [...fr.querySelectorAll('.tt b')];
      const vis = (f) => { const b = f.getBoundingClientRect(); return b.width > 10 && b.height > 10; };
      return JSON.stringify({ open: !document.querySelector('#stv').hidden, turn: el.classList.contains('turn'), imgs: imgs.length, broken: res.filter((x) => !x).length, css: el.querySelectorAll('.cssst').length,
        front: fr.textContent.length, back: bk.textContent.length, fblank: fr.classList.contains('blank'), bblank: bk.classList.contains('blank'), vis: vis(fr),
        cap: (document.querySelector('#stv .cap h3') || {}).textContent, ttWrap: tt.some((b) => b.scrollWidth > fr.clientWidth + 1),
        over: fr.scrollHeight > fr.clientHeight + 2 || bk.scrollHeight > bk.clientHeight + 2 });`));
    if (!r.open) msg.push('碑面没弹出来');
    if (!r.turn) msg.push('没翻过去');
    if (r.broken) msg.push(`${r.broken} 张图载不上`);
    if ((!r.fblank && r.front < 4) || (!r.bblank && r.back < 4)) msg.push(`碑面没字（正 ${r.front}，背 ${r.back}）`);
    if (!r.vis) msg.push('碑面框是空的');
    if (r.cap !== road.name) msg.push('碑面旁边的名字对不上');
    if (r.ttWrap) msg.push('正名一行排不下');
    if (r.over) msg.push('碑面的字刻不下');
    stImg += r.imgs - r.css > 0 ? 1 : 0; stTxt += r.front + r.back;
    await ev('__bk.stvClose(); return 1'); await sleep(340);
  }
  stOK += msg.length ? 0 : 1;
  if (msg.length) { console.log('碑', i, road.name, '｜' + msg.join('；')); bad += msg.length; }
}
console.log(`路边的碑 ${NS} 块：走查过的 ${stOK}，有图的 ${stImg}（别的拿 CSS 画的碑顶着），碑面刻的字合计 ${stTxt}`);
// 灰雨之夜路分开以后两个人各在一条路上；走到头两个人都在、那几句出来
const sp = JSON.parse(await ev(`__bk.z(__bk.s.ZS + 40); return JSON.stringify(__bk.s)`));
await settle();
const two = await ev('return __bk.walkers()');
if (!(two.some((w) => w.startsWith('w_bal')) && two.some((w) => w.startsWith('w_sor')))) { console.log('路分开以后两条路上没有各走一个人', two); bad++; }
if (!(sp.cam.h > 6)) { console.log('路分开以后镜头没升上去', sp.cam); bad++; }
await ev('__bk.z(__bk.s.ZMAX); return 1'); await settle(); await sleep(1900);
const end = JSON.parse(await ev(`return JSON.stringify({ show: document.querySelector('#endtx').classList.contains('show'), op: +getComputedStyle(document.querySelector('#endtx')).opacity, rift: +document.querySelector('#rift').style.opacity, walkers: __bk.walkers().length })`));
if (!end.show || end.op < 0.9 || end.rift < 0.9 || end.walkers !== 2) { console.log('走到头那一段不对', end); bad++; }

// 二、时代页
let nNodes = 0, nProf = 0, nSpr = 0, nFate = 0, nDeath = 0, nEnd = 0, nDied = 0, nCard = 0, nLineEnd = 0, nPlace = 0;
for (let i = 0; i < D.eras.length; i++) {
  const e = D.eras[i];
  if (ONLY.length && !ONLY.includes(e.id)) continue;
  const cg = CG[e.id] || {}, PF = rd(`./data/prof/${e.id}.json`, {}), cards = CARDS[e.id] || null;
  const want = Object.values(cg.nodes || {}).reduce((n, l) => n + Object.values(l).reduce((k, v) => k + (Array.isArray(v) ? v.length : 1), 0), 0);
  await ev(`__bk.open(${i}); return 1`); await sleep(900);
  const pg = JSON.parse(await ev(`${imgOK}
    const shown = (el) => { for (let x = el; x && x.id !== 'pg-body'; x = x.parentElement) if (getComputedStyle(x).display === 'none') return false; return true; };
    const ends = [...document.querySelectorAll('#pg-body details.ln > .in > details.end')];
    const mini = document.querySelector('#pg-body .mini'), mimg = mini && mini.querySelector('img');
    const extra = { spl: document.querySelectorAll('#pg-body .spl').length, ends: ends.length, endsShown: ends.filter(shown).length,
      mini: !!mini, miniImg: mimg ? await ok(mimg.getAttribute('src')) : null, dots: mini ? mini.querySelectorAll('i').length : 0, names: document.querySelectorAll('#pg-body .mini-names button').length,
      oldPlaces: document.querySelectorAll('#pg-body ul.places li').length,
      lnText: [...document.querySelectorAll('#pg-body details.ln')].map((d) => ({ hooks: [...d.querySelectorAll('.hook')].map((h) => h.textContent), open: (d.querySelector('p.open') || {}).textContent || '', tails: d.querySelectorAll('ol li.cgi > p').length })) };
    const im = document.querySelector('#pg-img'), src = im.getAttribute('src');
    const key = src ? await ok(src) : null;
    const sts = [...document.querySelectorAll('#pg-body .srow .st')];
    const stImgs = [...document.querySelectorAll('#pg-body .srow img')], stRes = await Promise.all(stImgs.map((n) => ok(n.getAttribute('src'))));
    const nodes = [...document.querySelectorAll('#pg-body .ln .cgb img')], res = await Promise.all(nodes.map((n) => ok(n.getAttribute('src'))));
    const pors = [...document.querySelectorAll('#pg-body i.por')];
    const atlas = pors.length ? await ok(getComputedStyle(pors[0]).backgroundImage.replace(/^url\\(["']?|["']?\\)$/g, '')) : null;
    const thumbs = [...document.querySelectorAll('#pg-body .boss .thumb[data-k]')], tRes = await Promise.all(thumbs.map((t) => ok(getComputedStyle(t).backgroundImage.replace(/^url\\(["']?|["']?\\)$/g, ''))));
    sts[0] && sts[0].click(); await new Promise((r) => setTimeout(r, 60));
    const turned = sts[0] ? sts[0].classList.contains('turn') : false; sts[0] && sts[0].click();
    return JSON.stringify({ open: __bk.s.pageOpen, cg: document.querySelector('#page').classList.contains('cg'), key, sts: sts.length, stBroken: stRes.filter((x) => !x).length, turned,
      lines: document.querySelectorAll('#pg-body details.ln').length, nodes: nodes.length, broken: res.filter((x) => !x).length, pors: pors.length, atlas,
      boss: document.querySelectorAll('#pg-body .boss figure').length, tBroken: tRes.filter((x) => !x).length, extra,
      people: [...new Set([...document.querySelectorAll('#pg-body [data-p]')].map((x) => x.dataset.p))], noimg: document.querySelectorAll('#pg-body .noimg').length });`));
  const msg = [], x = pg.extra;
  // 没有你的那一版（主线的）：开了剧透都看得见；“这一带”换成了小地图，地名一个不少；有卡片的主线用卡片上的钩子和睁眼的地方，各幕不带字
  const wantEnds = e.lines.filter((l) => l.ending).length;
  if (x.ends !== wantEnds || x.endsShown !== wantEnds) msg.push(`主线的没有你的那一版 ${x.endsShown}／${wantEnds}`);
  if (NEW) {
    if (x.spl !== 1) msg.push(`时代页的剧透开关 ${x.spl} 个`);
    if (e.places.length && !(x.mini && x.miniImg && x.names === e.places.length && x.dots > 0)) msg.push(`这一带的小地图不对 ${JSON.stringify({ mini: x.mini, img: x.miniImg, dots: x.dots, names: x.names })}`);
    if (x.oldPlaces) msg.push('原来那一串地名还在');
    e.lines.forEach((l, k) => {
      const lc = cards && cards.lines && cards.lines[l.name], t = x.lnText[k] || { hooks: [], open: '', tails: 0 };
      if (lc) { if (t.hooks.join('|') !== (lc.hook || '') || t.open !== (lc.open || l.open || '') || t.tails) msg.push(`${l.name} 没照卡片出`); }
      else if (t.hooks.join('|') !== l.hooks.join('|') || t.open !== (l.open || '')) msg.push(`${l.name} 的钩子和睁眼的地方跟原来不一样`);
    });
  }
  nLineEnd += x.endsShown; nPlace += NEW ? x.names : x.oldPlaces;
  if (pg.open !== i) msg.push('时代页没打开');
  if (cg.key && (!pg.cg || !pg.key)) msg.push('时代原画没出来');
  if (pg.sts !== e.steles.length) msg.push(`碑 ${pg.sts}／${e.steles.length}`);
  if (pg.stBroken) msg.push(`碑图 ${pg.stBroken} 张载不上`);
  if (!pg.turned) msg.push('碑点了没翻');
  if (pg.lines !== e.lines.length) msg.push(`主线 ${pg.lines}／${e.lines.length}`);
  if (pg.nodes !== want) msg.push(`节点原画 ${pg.nodes}／${want}`);
  if (pg.broken) msg.push(`节点原画 ${pg.broken} 幅载不上`);
  if (pg.pors && !pg.atlas) msg.push('人像拼图载不上');
  if (pg.boss !== e.bosses.length) msg.push(`灾祸 ${pg.boss}／${e.bosses.length}`);
  if (pg.tBroken) msg.push(`灾祸的图 ${pg.tBroken} 张载不上`);
  // 灾祸是一个对手一张拼图：缩略图露头一格（背景宽 = 格数 × 100%），点开各阶只露那一格
  const bc = JSON.parse(await ev(`const ts = [...document.querySelectorAll('#pg-body .boss .thumb[data-k]')];
    const bad = ts.filter((t) => { const s = t.style; return !/\\d+% 100%/.test(s.backgroundSize) || s.backgroundPosition.replace(/px/g, '%') !== '0% 0%'; }).length;
    const t = ts.find((x) => parseInt(x.style.backgroundSize) >= 200);
    if (!t) return JSON.stringify({ n: ts.length, bad, cell: null });
    __bk.cg(+t.dataset.k + 1); await new Promise((r) => setTimeout(r, 500));
    const c = document.querySelector('#cgv .cell'), im = c.querySelector('img'), r = c.getBoundingClientRect(), ri = im.getBoundingClientRect();
    const out = { n: ts.length, bad, cell: { shown: !c.hidden && !document.querySelector('#cgv').hidden, i: getComputedStyle(c).getPropertyValue('--i').trim(), w: Math.round(r.width), h: Math.round(r.height),
      ratio: +(r.width / Math.max(1, r.height)).toFixed(3), shift: Math.round(r.left - ri.left), loaded: im.complete && im.naturalWidth > 0 } };
    document.querySelector('#cgv').dispatchEvent(new MouseEvent('click', { bubbles: true })); await new Promise((r) => setTimeout(r, 380));
    return JSON.stringify(out);`));
  if (bc.bad) msg.push(`灾祸的缩略图 ${bc.bad} 张没对上格子`);
  if (bc.cell && !(bc.cell.shown && bc.cell.i === '1' && bc.cell.loaded && Math.abs(bc.cell.ratio - 2 / 3) < 0.02 && Math.abs(bc.cell.shift - bc.cell.w) <= 2)) msg.push('点开灾祸第二阶没露对那一格 ' + JSON.stringify(bc.cell));
  nNodes += pg.nodes;
  let profs = 0, spr = 0, fates = 0, deaths = 0, endsP = 0, died = 0, cardN = 0, wFate = 0, wEnd = 0, wDied = 0, wCard = 0;
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
      const body = p.querySelector('.pf-body'), shown = (el) => { for (let x = el; x && x !== body; x = x.parentElement) if (getComputedStyle(x).display === 'none') return false; return true; };
      const f = p.querySelector('.pf-fate'), d = p.querySelector('.pf-fate .cgb img'), dead = p.querySelector('.pf-dead'), endH = [...p.querySelectorAll('.pf-body h3')].find((h) => h.textContent === '没有你的那一版');
      return JSON.stringify({ god: p.classList.contains('artonly'), sheet: u ? await ok(u) : null, tabs: p.querySelectorAll('.pf-tabs button').length, faces: p.querySelectorAll('.pf-faces figure').length,
        kind: ((p.querySelector('.pf-body .eyebrow') || {}).textContent || '').split('　')[0], card: !!p.querySelector('.pf-body [data-card]'), spl: p.querySelectorAll('.pf-body .spl').length,
        fate: !!f && shown(f), dead: !!dead && shown(dead), death: d ? (shown(d) ? await ok(d.getAttribute('src')) : false) : null, end: !!endH && shown(endH), text: body.textContent.length });`));
    profs++;
    if (pf.sheet === false) msg.push(`${name} 的立绘那一张载不上`);
    if (pf.sheet) { spr++; if (!pf.god && (pf.tabs !== 4 || pf.faces !== 9)) msg.push(`${name} 衣服 ${pf.tabs} 套、表情 ${pf.faces} 格`); }
    if (pf.text < 40) msg.push(`${name} 的档案是空的`);
    // 下场、死期死因、死的那一刻照 data/prof 和 data/cg.json 对（传奇那一块是“殁于这一段”，不在剧透开关里）；有卡片的旅伴和相遇走卡片
    const pd = PF[name] || {}, legend = pf.kind === '传奇', person = pf.kind === '旅伴' || pf.kind === '相遇';
    const wf = legend ? !!pd.died : !!pd.death, we = !legend && !!(pd.fate || pd.death), wd = !legend && !!(cg.deaths || {})[name], wc = person && !!(cards && cards.people && cards.people[name]);
    if (pf.fate !== wf) msg.push(`${name} ${legend ? '殁于这一段' : '死期死因'}那一块${wf ? '没出来' : '多出来了'}`);
    if (pf.fate !== pf.dead) msg.push(`${name} 死期那一条和那一块对不上`);
    if (pf.end !== we) msg.push(`${name} 没有你的那一版${we ? '没出来' : '多出来了'}`);
    if (wd && !pf.death) msg.push(`${name} 死的那一刻${pf.death === false ? '载不上' : '没出来'}`);
    if (!wd && pf.death != null) msg.push(`${name} 多了一幅死的那一刻`);
    if (NEW && pf.card !== wc) msg.push(`${name} ${wc ? '有卡片，档案没走卡片' : '没有卡片，档案却是卡片的样子'}`);
    if (NEW && pf.spl !== (we ? 1 : 0)) msg.push(`${name} 档案里的剧透开关 ${pf.spl} 个`);
    if (legend) { died += pf.fate ? 1 : 0; wDied += wf ? 1 : 0; } else { fates += pf.fate ? 1 : 0; wFate += wf ? 1 : 0; }
    endsP += pf.end ? 1 : 0; wEnd += we ? 1 : 0; deaths += pf.death ? 1 : 0; cardN += pf.card ? 1 : 0; wCard += wc ? 1 : 0;
    await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(360);
  }
  const wantD = Object.keys(cg.deaths || {}).length;
  if (deaths !== wantD) msg.push(`死的那一刻 ${deaths}／${wantD}`);
  nProf += profs; nSpr += spr; nFate += fates; nDeath += deaths; nEnd += endsP; nDied += died; nCard += cardN;
  console.log(e.id, e.title, `碑 ${pg.sts}`, `主线 ${pg.lines}`, `节点 ${pg.nodes}／${want}`, `人像 ${pg.pors}（没图的 ${pg.noimg}）`, `档案 ${profs}（有立绘的 ${spr}）`, `灾祸 ${pg.boss}`,
    `｜没有你的那一版 主线 ${x.endsShown}／${wantEnds} 档案 ${endsP}／${wEnd}`, `死期 ${fates}／${wFate}`, `死的那一刻 ${deaths}／${wantD}`, `传奇殁于这一段 ${died}／${wDied}`,
    NEW ? `卡片 ${cardN}／${wCard}　这一带 ${x.names} 处（小地图 ${x.dots} 个点）` : `这一带 ${x.oldPlaces} 处`, msg.length ? '｜' + msg.join('；') : '');
  bad += msg.length;
  await ev(`__bk.close(); return 1`); await sleep(500);
}
console.log(`合计：节点原画 ${nNodes}，档案 ${nProf}（有立绘的 ${nSpr}）；没有你的那一版 主线 ${nLineEnd}、档案 ${nEnd}，死期 ${nFate}，死的那一刻 ${nDeath}，传奇殁于这一段 ${nDied}，卡片档案 ${nCard}，这一带 ${nPlace} 处；对不上的 ${bad} 处`);
console.log(errs.length ? '报错和载不下来的：\n' + [...new Set(errs)].slice(0, 40).join('\n') : '页面没有报错，没有载不下来的文件');
ws.close();
