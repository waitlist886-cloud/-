// 月银纪的书铺开以后的全书走查：二十七个时代一页一页打开，核时代原画、各幕的节点原画、人像拼图载没载上；
// 旅伴和相遇有档案的一个一个点开，核立绘加表情那一张、死期那一块、死的那一刻那一幅。收报错和载不下来的文件。
//   node act_all.mjs <宽> <高> [只查这几个时代，比如 m05,m16]
// 本地服务器是 .claude/launch.json 的 front-book（8768），无头 Chrome 在 9335。
import fs from 'node:fs';
const [W, H, ONLY] = [+process.argv[2], +process.argv[3], (process.argv[4] || '').split(',').filter(Boolean)];
const PORT = 9335, ADDR = 'http://localhost:8768/local.html?skip=1';
const CG = JSON.parse(fs.readFileSync(new URL('./data/cg.json', import.meta.url), 'utf8'));
const MOON = JSON.parse(fs.readFileSync(new URL('./data/moon.json', import.meta.url), 'utf8'));
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 300));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) errs.push(m.params.response.status + ' ' + m.params.response.url.replace('http://localhost:8768/', ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR });
await Promise.race([loaded, sleep(15000)]); await sleep(2500);
const imgOK = `const ok = (u) => new Promise((r) => { const i = new Image(); i.onload = () => r(i.naturalWidth > 0); i.onerror = () => r(false); i.src = u; });`;
let bad = 0, nNodes = 0, nProf = 0, nDeath = 0, nFate = 0;
for (let i = 0; i < MOON.eras.length; i++) {
  const e = MOON.eras[i];
  if (ONLY.length && !ONLY.includes(e.id)) continue;
  const cg = CG[e.id] || {};
  const want = Object.values(cg.nodes || {}).reduce((n, l) => n + Object.values(l).reduce((k, v) => k + (Array.isArray(v) ? v.length : 1), 0), 0);
  await ev(`__bk.open(${i}); return 1`); await sleep(900);
  const pg = JSON.parse(await ev(`${imgOK}
    const im = document.querySelector('#pg-img');
    const key = await ok(im.getAttribute('src'));
    const nodes = [...document.querySelectorAll('#pg-body .cgb img')];
    const res = await Promise.all(nodes.map((n) => ok(n.getAttribute('src'))));
    const pors = [...document.querySelectorAll('#pg-body i.por')];
    const atlas = pors.length ? await ok(getComputedStyle(pors[0]).backgroundImage.replace(/^url\\(["']?|["']?\\)$/g, '')) : null;
    return JSON.stringify({ open: __bk.s.pageOpen, cg: document.querySelector('#page').classList.contains('cg'), key, nodes: nodes.length, broken: res.filter((x) => !x).length, pors: pors.length, atlas,
      people: [...document.querySelectorAll('#pg-body [data-p]')].map((x) => x.dataset.p), noimg: document.querySelectorAll('#pg-body .noimg').length });`));
  const msg = [];
  if (pg.open !== i || !pg.cg || !pg.key) msg.push('时代原画没出来');
  if (pg.nodes !== want) msg.push(`节点原画 ${pg.nodes}／${want}`);
  if (pg.broken) msg.push(`节点原画 ${pg.broken} 幅载不上`);
  if (pg.pors && !pg.atlas) msg.push('人像拼图载不上');
  nNodes += pg.nodes;
  let profs = 0, spr = 0, deaths = 0, fates = 0;
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
      const d = p.querySelector('.pf-fate .cgb img');
      return JSON.stringify({ noart: p.classList.contains('noart'), sheet: u ? await ok(u) : null, tabs: p.querySelectorAll('.pf-tabs button').length, faces: p.querySelectorAll('.pf-faces figure').length,
        fate: !!p.querySelector('.pf-fate'), dead: !!p.querySelector('.pf-dead'), death: d ? await ok(d.getAttribute('src')) : null, text: p.querySelector('.pf-body').textContent.length });`));
    profs++;
    if (pf.sheet === false) msg.push(`${name} 的立绘那一张载不上`);
    if (pf.sheet) { spr++; if (pf.tabs !== 4 || pf.faces !== 9) msg.push(`${name} 衣服 ${pf.tabs} 套、表情 ${pf.faces} 格`); }
    if (pf.fate) fates++;
    if (pf.fate !== pf.dead) msg.push(`${name} 死期那一条和那一块对不上`);
    if (pf.death === false) msg.push(`${name} 死的那一刻载不上`);
    if (pf.death) deaths++;
    if (pf.text < 60) msg.push(`${name} 的档案是空的`);
    await ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(380);
  }
  const wantD = Object.keys(cg.deaths || {}).length;
  if (deaths !== wantD) msg.push(`死的那一刻 ${deaths}／${wantD}`);
  nProf += profs; nDeath += deaths; nFate += fates;
  console.log(e.id, e.label, `节点 ${pg.nodes}／${want}`, `人像 ${pg.pors}（没图的 ${pg.noimg}）`, `档案 ${profs}（有立绘的 ${spr}）`, `死期 ${fates}`, `死的那一刻 ${deaths}／${wantD}`, msg.length ? '｜' + msg.join('；') : '');
  bad += msg.length;
  await ev(`__bk.close(); return 1`); await sleep(500);
}
console.log(`合计：节点原画 ${nNodes}，档案 ${nProf}，死期 ${nFate}，死的那一刻 ${nDeath}；对不上的 ${bad} 处`);
console.log(errs.length ? '报错和载不下来的：\n' + [...new Set(errs)].slice(0, 40).join('\n') : '页面没有报错，没有载不下来的文件');
ws.close();
