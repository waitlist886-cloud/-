// 此刻那一本的走查（11-24 第四拨 P1 写的那一支收进来，11-25 添主线原画那几样）。
//   先起本地服务（共用/utf8_server.py，8774，根是 底稿/门面/）和一个无头 Chrome：
//     chrome --headless=new --hide-scrollbars --no-first-run --enable-unsafe-swiftshader --remote-debugging-port=9385 --user-data-dir=<临时目录> about:blank
//   CDP_PORT=9385 node 底稿/门面/小样_此刻书/tools/walk_now.mjs 1920 945 <截图前缀>
//   CDP_PORT=9385 node 底稿/门面/小样_此刻书/tools/walk_now.mjs 390 844 <截图前缀>
// 两种宽度末行“对不上 0”才算过。
import fs from 'node:fs';
const { open, sleep } = await import('file:///E:/aldran_art/底稿/门面/第二轮/建档/tools/cdp.mjs');
const [W, H] = [+(process.argv[2] || 1920), +(process.argv[3] || 945)]; const OUT = process.argv[4] || 'shots/n';
const URL_ = 'http://localhost:8774/' + encodeURIComponent('小样_此刻书') + '/local.html?t=' + Date.now();
const P = await open(W, H, { mobile: W < 861, url: URL_ });
let bad = 0; const no = (m) => { bad++; console.log('  ✗ ' + m); }; const ok = (c, m) => (c ? console.log('  ✓ ' + m) : no(m));
await P.until('window.__now && __now.D && document.querySelectorAll(".st").length', 30000); await sleep(1500);
const BAN = /——|—|；|…|！|新月|满月|月牙|月亮|月光|玩家/;
const banCheck = async (where, sel) => { const t = await P.ev(`const r = document.querySelector(${JSON.stringify(sel)}); return r ? r.innerText : ''`); const m = String(t).match(BAN); if (m) no(where + ' 有 ' + m[0] + '：' + t.slice(Math.max(0, m.index - 20), m.index + 20)); return t; };
const D = await P.ev('return __now.D');
const CG = await P.ev('return __now.CG');
const ACT = ['一幕', '二幕', '三幕', '四幕', '五幕'];
ok((await P.ev('return document.querySelectorAll(".st").length')) === D.lines.length, '路上 ' + D.lines.length + ' 站都画出来了');
const gd = await P.ev('const e = document.querySelector(".grp .gd"); return e ? e.innerText : ""');
ok(gd && gd === D.groups[0].d, '兆一那一段的牌面字在：' + gd.slice(0, 24));
ok(!(await P.ev('return document.querySelectorAll(".grp .gd").length > 1')), '只有头一段有牌面字');
await banCheck('路', '#road');

// ---------- 主线原画：数据 ----------
const ids = new Set(D.lines.map((x) => x.id));
const cgLines = Object.keys(CG);
ok(cgLines.every((id) => ids.has(id)), 'cg.json 里的线都在路上');
let nPic = 0, nTh = 0;
const srcs = [];
for (const id of cgLines) {
  const x = D.lines.find((l) => l.id === id), c = CG[id];
  if (!x) continue;
  for (const [i, it] of Object.entries(c.acts || {})) { if (!x.acts[+i]) no(`${x.title} 没有第 ${+i + 1} 幕，却配了原画`); nPic++; srcs.push(it.src); }
  if (c.th) { nTh++; srcs.push(c.th); }
}
const dead = await P.ev(`const bad = []; for (const s of ${JSON.stringify(srcs)}) { try { const r = await fetch(A(s)); const b = await r.blob(); if (!r.ok || b.size < 4000 || !/image/.test(b.type)) bad.push(s); } catch (e) { bad.push(s); } } return bad`);
ok(!dead.length, `原画 ${nPic} 幅、小幅 ${nTh} 张都取得到` + (dead.length ? '，取不到：' + dead.join(' ') : ''));
console.log(`  有原画的主线 ${cgLines.length} 条（共 ${D.lines.length} 条），原画 ${nPic} 幅（各幕合计 ${D.lines.reduce((n, l) => n + l.acts.length, 0)} 幕）`);

// ---------- 路上的小幅：宽屏才出 ----------
const th = await P.ev(`return [...document.querySelectorAll('.st.has-th .th')].map((e) => getComputedStyle(e).display !== 'none')`);
ok(th.length === nTh, `带小幅的站 ${th.length} 个，对得上 cg.json 的 ${nTh} 张`);
ok(th.every((v) => v === (W >= 1100)), W >= 1100 ? '宽屏上小幅都露着' : '窄屏上小幅都收着');
const over = await P.ev(`return [...document.querySelectorAll('.st')].filter((e) => e.scrollWidth > e.clientWidth + 1).length`);
ok(!over, '路上各站没有横向撑破的');
ok(await P.ev('return document.documentElement.scrollWidth <= innerWidth + 1'), '整页没有横向滚动');
await P.ev('document.querySelector("#g1").scrollIntoView(); return 1'); await sleep(1200); await P.shot(`${OUT}_road.jpg`);

// ---------- 逐条开：字、原画 ----------
let firstCg = null;
for (const x of D.lines) {
  await P.ev(`__now.openLine(${JSON.stringify(x.id)}); return 1`); await sleep(60);
  const t = await banCheck('线 ' + x.title, '#ln .in');
  if (!t.includes(x.title) || !x.acts.every((a) => t.includes(a[0]) && t.includes(a[1]))) no('线 ' + x.title + ' 没画全');
  const want = Object.entries((CG[x.id] && CG[x.id].acts) || {}).filter(([, it]) => !it.sp).map(([i]) => +i).sort();
  const got = await P.ev(`return [...document.querySelectorAll('#ln li.cgi:not(.sp-pic) .cgb')].map((b) => ({ i: +b.dataset.cg, tag: b.querySelector('.cap b').textContent, nm: b.querySelector('.cap i').textContent, src: b.querySelector('img').getAttribute('src'), w: b.getBoundingClientRect().width, h: b.getBoundingClientRect().height }))`);
  if (JSON.stringify(got.map((g) => g.i).sort()) !== JSON.stringify(want)) no(`线 ${x.title} 的原画对不上：页上 ${got.map((g) => g.i)}，表里 ${want}`);
  for (const g of got) {
    if (g.tag !== ACT[g.i] || g.nm !== x.acts[g.i][0]) no(`线 ${x.title} 第 ${g.i + 1} 幕原画的题签不对：${g.tag} ${g.nm}`);
    if (!g.src.endsWith(CG[x.id].acts[g.i].src)) no(`线 ${x.title} 第 ${g.i + 1} 幕原画的图不对`);
    if (Math.abs(g.w / g.h - 1.5) > 0.02) no(`线 ${x.title} 第 ${g.i + 1} 幕原画不是三比二：${g.w}×${g.h}`);
  }
  const lis = await P.ev(`return document.querySelectorAll('#ln ol > li').length`);
  if (lis !== x.acts.length) no(`线 ${x.title} 列了 ${lis} 幕，该是 ${x.acts.length}`);
  if (await P.ev(`const b = document.querySelector('#ln .box'); return b.scrollWidth > b.clientWidth + 1`)) no('线 ' + x.title + ' 的浮层横向撑破了');
  if (got.length && !firstCg) firstCg = x;
}
console.log('  三十一条线逐条开过');

// ---------- 看大图 ----------
if (firstCg) {
  const x = firstCg, n = Object.values(CG[x.id].acts).filter((it) => !it.sp).length;
  await P.ev(`__now.openLine(${JSON.stringify(x.id)}); return 1`); await sleep(500);
  await P.ev(`const b = document.querySelector('#ln .cgb'); b.scrollIntoView({ block: 'center' }); return 1`); await sleep(900);
  // 图是 loading=lazy 的，前头刚连着开过三十一条线，头一幅有时要多等一两秒：最多等八秒，等不到才算没载出来
  let loaded = false;
  for (let i = 0; i < 40 && !loaded; i++) { loaded = await P.ev(`const im = document.querySelector('#ln .cgb img'); return im.complete && im.naturalWidth > 600`); if (!loaded) await sleep(200); }
  ok(loaded, '浮层里的原画载出来了');
  await P.shot(`${OUT}_line_cg.jpg`);
  await P.ev(`document.querySelector('#ln .cgb').click(); return 1`); await sleep(700);
  ok(await P.ev(`const v = document.querySelector('#cgv'); return !v.hidden && v.classList.contains('on') && __now.cgAt === 0`), '点原画开了大图');
  ok(await P.ev(`const im = document.querySelector('#cgv > img'); await im.decode().catch(() => 0); const r = im.getBoundingClientRect(); return im.naturalWidth > 600 && r.width <= innerWidth + 1 && r.height <= innerHeight + 1 && r.width > innerWidth * .5`), '大图载出来了，没出屏');
  const cap = await P.ev(`return document.querySelector('#cgv .cap').innerText`);
  ok(cap.includes(x.title) && cap.includes(x.acts[+Object.keys(CG[x.id].acts).sort()[0]][0]), '大图的题签是主线名和幕名');
  await banCheck('大图题签', '#cgv .cap');
  await P.shot(`${OUT}_cgv.jpg`);
  if (n > 1) {
    await P.ev(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true })); return 1`); await sleep(300);
    ok(await P.ev(`return __now.cgAt === 1`), '右方向键翻到下一幅');
    await P.ev(`document.querySelector('#cgv .nav.l').click(); return 1`); await sleep(300);
    ok(await P.ev(`return __now.cgAt === 0`), '左边的钮翻回上一幅');
  }
  ok(await P.ev(`return document.querySelector('#cgv .nav.l').disabled && document.querySelector('#cgv .nav.r').disabled === ${n < 2}`), '头一幅左边的钮灰着' + (n < 2 ? '，只有一幅右边也灰着' : ''));
  await P.ev(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); return 1`); await sleep(500);
  ok(await P.ev(`return document.querySelector('#cgv').hidden && document.querySelector('#ln').classList.contains('on')`), '按 Esc 只合上大图，主线的浮层还在');
  // 归剧透的那一格：页上眼下没有，拿这一幅临时标上试一回显隐，试完改回去
  const ai = Object.keys(CG[x.id].acts).sort()[0];
  for (const sp of [false, true]) {
    await P.ev(`__now.CG[${JSON.stringify(x.id)}].acts[${JSON.stringify(ai)}].sp = 1; __now.setSpoil(${sp}); __now.openLine(${JSON.stringify(x.id)}); return 1`); await sleep(200);
    const v = await P.ev(`const p = document.querySelector('#ln li.sp-pic'), t = document.querySelector('#ln li.sp-txt'); return [p && getComputedStyle(p).display !== 'none', t && getComputedStyle(t).display !== 'none']`);
    ok(v[0] === sp && v[1] === !sp, `标了归剧透的一幅，剧透${sp ? '开着出图' : '关着只出字'}`);
  }
  await P.ev(`delete __now.CG[${JSON.stringify(x.id)}].acts[${JSON.stringify(ai)}].sp; __now.setSpoil(false); return 1`);
} else console.log('  （还没有进书的原画，看大图那几样没走）');
await P.ev(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); return 1`); await sleep(400);
await P.ev(`__now.openLine('L1175'); return 1`); await sleep(500); await P.shot(`${OUT}_L1175.jpg`);
await P.ev(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); return 1`); await sleep(400);
ok(!(await P.ev(`return document.querySelector('.dlg.on')`)), '浮层都合上了');

// ---------- 图鉴：剧透关着强敌只露格里沃，开了十位 ----------
for (const sp of [false, true]) {
  await P.ev(`__now.setSpoil(${sp}); Atlas.open(); return 1`); await sleep(700);
  await P.ev(`const b = document.querySelector('[data-tab="foes"]'); if (b) b.click(); return !!b`); await sleep(500);
  const names = await P.ev(`return [...document.querySelectorAll('.a-ac.foes .a-nm')].map((e) => e.textContent)`);
  ok(sp ? names.length === 10 : (names.length === 1 && names[0] === '咬灯格里沃'), `剧透${sp ? '开' : '关'}着强敌 ${names.length} 张：${names.join('、')}`);
  await P.ev(`const b = document.querySelector('.a-ac.foes'); if (b) b.click(); return 1`); await sleep(400);
  await banCheck('图鉴强敌', '#atl');
  await P.shot(`${OUT}_atlas_foes_${sp ? 'on' : 'off'}.jpg`);
  if (sp) { await P.ev(`const bs = [...document.querySelectorAll('.a-ac.foes')]; bs[bs.length - 1].click(); return 1`); await sleep(400); await banCheck('图鉴凯斯珀', '#atl'); await P.shot(`${OUT}_atlas_kesper.jpg`); }
  await P.ev(`Atlas.close(); return 1`); await sleep(400);
  ok(await P.ev(`return __now.openProf('凯斯珀·佩兰')`), '凯斯珀的档案开得了');
  await sleep(500);
  const vis = await P.ev(`return [...document.querySelectorAll('#pf .spoil')].map((e) => getComputedStyle(e).display !== 'none')`);
  ok(vis.length === 2 && vis.every((v) => v === sp), `档案底细 剧透${sp ? '开着露' : '关着藏'}`);
  await banCheck('凯斯珀档案', '#pf');
  await P.shot(`${OUT}_kesper_${sp ? 'on' : 'off'}.jpg`);
  await P.ev(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })); document.querySelectorAll('.dlg [data-close], .dlg .x').forEach((b) => b.click()); return 1`); await sleep(400);
}
await P.ev(`__now.setSpoil(false); return 1`);
const errs = P.errs.filter((e) => !/favicon/.test(e));
ok(!errs.length, '控制台没有报错' + (errs.length ? JSON.stringify(errs.slice(0, 5)) : ''));
console.log('对不上', bad);
await P.close(); process.exit(0);
