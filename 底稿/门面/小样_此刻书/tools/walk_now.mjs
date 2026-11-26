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

// ---------- 图鉴：剧透关着主线对手只露格里沃，开了十位（11-26 起强敌里还有楼层主，这里只数主线对手那一类） ----------
for (const sp of [false, true]) {
  await P.ev(`__now.setSpoil(${sp}); Atlas.open(); return 1`); await sleep(700);
  await P.ev(`const b = document.querySelector('[data-tab="foes"]'); if (b) b.click(); return !!b`); await sleep(500);
  const names = await P.ev(`return [...document.querySelectorAll('.a-ac.foes')].filter((b) => b.querySelector('.a-tg').textContent === '主线对手').map((b) => b.querySelector('.a-nm').textContent)`);
  ok(sp ? names.length === 10 : (names.length === 1 && names[0] === '咬灯格里沃'), `剧透${sp ? '开' : '关'}着主线对手 ${names.length} 张：${names.join('、')}`);
  await P.ev(`const b = document.querySelector('.a-ac.foes'); if (b) b.click(); return 1`); await sleep(400);
  await banCheck('图鉴强敌', '#atl');
  await P.shot(`${OUT}_atlas_foes_${sp ? 'on' : 'off'}.jpg`);
  if (sp) { await P.ev(`const bs = [...document.querySelectorAll('.a-ac.foes')].filter((b) => b.querySelector('.a-tg').textContent === '主线对手'); bs[bs.length - 1].click(); return 1`); await sleep(400); await banCheck('图鉴凯斯珀', '#atl'); await P.shot(`${OUT}_atlas_kesper.jpg`); }
  await P.ev(`Atlas.close(); return 1`); await sleep(400);
  ok(await P.ev(`return __now.openProf('凯斯珀·佩兰')`), '凯斯珀的档案开得了');
  await sleep(500);
  const vis = await P.ev(`return [...document.querySelectorAll('#pf .spoil')].map((e) => getComputedStyle(e).display !== 'none')`);
  ok(vis.length === 2 && vis.every((v) => v === sp), `档案底细 剧透${sp ? '开着露' : '关着藏'}`);
  await banCheck('凯斯珀档案', '#pf');
  await P.shot(`${OUT}_kesper_${sp ? 'on' : 'off'}.jpg`);
  await P.ev(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })); document.querySelectorAll('.dlg [data-close], .dlg .x').forEach((b) => b.click()); return 1`); await sleep(400);
}
// ---------- 图鉴楼层主（11-26）：十八位进强敌（楼层主十四、迷宫城之主四），剧透关着只露名字、在哪一层、一两句、一阶的名号和原画；
//            开了出阶段钮，切得过去，各阶名号、打法、乐章；有原画的（赝作魔王三阶）图取得到、跟着阶段换；点大图开整张，Esc 先合大图 ----------
{
  const ATf = await P.ev('return __now.AT.foes');
  const FB = ATf.filter((f) => f.fb);
  const nSt = FB.reduce((n, f) => n + f.fb.st.length, 0);
  ok(FB.length === 18 && nSt === 42, `楼层主 ${FB.length} 位、${nSt} 阶`);
  ok(FB.every((f) => f.fb.st.every((s) => s.nm)), '每一阶都有名号');
  const imgs = FB.flatMap((f) => f.fb.st.map((s) => s.img).filter(Boolean));
  const deadFb = await P.ev(`const bad = []; for (const s of ${JSON.stringify(imgs)}) { try { const r = await fetch(A(s)); const b = await r.blob(); if (!r.ok || b.size < 20000 || !/image/.test(b.type)) bad.push(s); } catch (e) { bad.push(s); } } return bad`);
  ok(imgs.length === 3 && !deadFb.length, `楼层主原画 ${imgs.length} 张都取得到` + (deadFb.length ? '：' + deadFb.join(' ') : ''));
  const SECRET = /凯尔萨斯|拉奇埃尔|波瑞亚斯|葛温|圣血之主|至暗之剑|传奇们的化身|风铃王|诺伦/;
  const pick = (n) => `[...document.querySelectorAll('#atl .a-ac.foes')].find((b) => b.querySelector('.a-nm').textContent === ${JSON.stringify(n)})`;
  const waitImg = `const im = document.querySelector('#atl .a-hero.fb img'); for (let i = 0; i < 60 && !(im && im.complete && im.naturalWidth); i++) await new Promise((r) => setTimeout(r, 100)); return 1`;
  for (const sp of [false, true]) {
    await P.ev(`__now.setSpoil(${sp}); Atlas.open(); return 1`); await sleep(700);
    await P.ev(`document.querySelector('[data-tab="foes"]').click(); return 1`); await sleep(400);
    const cards = await P.ev(`return [...document.querySelectorAll('#atl .a-ac.foes')].map((b) => [b.querySelector('.a-nm').textContent, b.querySelector('.a-tg').textContent, b.querySelector('.a-tags').textContent, b.innerText, !!b.querySelector('img'), !!b.querySelector('.a-fbs')])`);
    const fc = cards.filter((c) => c[1] === '楼层主' || c[1] === '迷宫城之主');
    ok(fc.length === 18 && fc.filter((c) => c[1] === '迷宫城之主').length === 4, `剧透${sp ? '开' : '关'}着楼层主卡 ${fc.length} 张：${fc.map((c) => c[0]).join('、')}`);
    ok(fc.every((c) => c[4] || c[5]), '每张楼层主卡有原画或层号牌，没有空人影');
    const leak = fc.filter((c) => SECRET.test(c[3]));
    ok(sp ? fc.some((c) => /\d 阶/.test(c[2])) && fc.some((c) => c[0] === '奥古斯都·凯尔萨斯·萨尔维斯') : (!leak.length && !fc.some((c) => /\d 阶/.test(c[2]))),
      sp ? '剧透开着卡上出阶数、换真名' : '剧透关着卡上不露阶数和真名' + (leak.length ? '：' + leak.map((c) => c[0]).join('、') : ''));
    await P.ev(`document.querySelector('[data-chip="楼层主"]').click(); return 1`); await sleep(300);
    await P.shot(`${OUT}_floor_list_${sp ? 'on' : 'off'}.jpg`);
    await P.ev(`document.querySelector('[data-chip="迷宫城之主"]').click(); return 1`); await sleep(300);
    // 赝作魔王：有三阶原画
    await P.ev(`${pick('赝作魔王')}.click(); return 1`); await sleep(500);
    await P.ev(waitImg);
    let r = await P.ev(`const pn = document.querySelector('#atl .at-panel'); const im = pn.querySelector('.a-hero.fb img'); return [im ? im.naturalWidth : 0, im ? im.getAttribute('src') : '', pn.querySelector('.a-full').textContent, pn.querySelectorAll('.a-phs .a-ph').length, !!pn.querySelector('.nospoil'), pn.innerText]`);
    ok(r[0] > 0 && /yanzuo_1\.webp/.test(r[1]) && r[2] === '弑君，弑神，焚天的魔王', `赝作魔王一阶原画 ${r[0]}px，名号 ${r[2]}`);
    ok(sp ? r[3] === 3 && !r[4] : r[3] === 0 && r[4] && !SECRET.test(r[5]), sp ? '剧透开着有三个阶段钮' : '剧透关着不露后两阶');
    await banCheck('图鉴赝作魔王', '#atl .at-panel');
    await P.shot(`${OUT}_floor_yanzuo_${sp ? 'on' : 'off'}.jpg`);
    if (sp) {
      for (const k of [1, 2]) {
        await P.ev(`document.querySelector('#atl .a-phs [data-ph="${k}"]').click(); return 1`); await sleep(400);
        await P.ev(waitImg);
        r = await P.ev(`const pn = document.querySelector('#atl .at-panel'); const im = pn.querySelector('.a-hero.fb img'); return [im.naturalWidth, im.getAttribute('src'), pn.querySelector('.a-full').textContent, pn.querySelector('.a-ph.on span:last-child').textContent, [...pn.querySelectorAll('.a-stage h3')].map((h) => h.textContent).join('｜')]`);
        ok(r[0] > 0 && r[1].includes('yanzuo_' + (k + 1)) && r[3] === (k + 1) + ' 阶' && /乐章《/.test(r[4]), `切到 ${k + 1} 阶：${r[2]}，${r[4]}`);
        await banCheck('图鉴赝作魔王' + (k + 1) + '阶', '#atl .at-panel');
        await P.shot(`${OUT}_floor_yanzuo_${k + 1}.jpg`);
      }
      // 点大图开整张，Esc 先合大图，图鉴还开着
      await P.ev(`document.querySelector('#atl .a-hero.fb img').click(); return 1`); await sleep(400);
      const zin = await P.ev(`const z = document.querySelector('#atl .a-zoom img'); return z ? z.getBoundingClientRect().height : 0`);
      await P.shot(`${OUT}_floor_zoom.jpg`);
      await P.ev(`window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); return 1`); await sleep(300);
      const zout = await P.ev(`return [!document.querySelector('#atl .a-zoom'), !!document.querySelector('#atl.on')]`);
      ok(zin > 200 && zout[0] && zout[1], `点大图开整张（高 ${Math.round(zin)}px），Esc 先合大图、图鉴还在`);
      // 诸王的化身：五阶，没有原画的阶段钮写阶数
      await P.ev(`${pick('诸王的化身')}.click(); return 1`); await sleep(400);
      r = await P.ev(`return [document.querySelectorAll('#atl .a-phs .a-ph').length, document.querySelectorAll('#atl .a-phs .a-phn').length]`);
      ok(r[0] === 5 && r[1] === 5, '诸王的化身五个阶段钮，没有图的写阶数');
      await P.ev(`document.querySelector('#atl .a-phs [data-ph="4"]').click(); return 1`); await sleep(300);
      r = await P.ev(`const pn = document.querySelector('#atl .at-panel'); return [pn.querySelector('.a-full').textContent, !!pn.querySelector('.a-words'), pn.innerText.includes('有人声')]`);
      ok(/诸王的化身$/.test(r[0]) && r[1] && r[2], '五阶名号、人声乐章带词：' + r[0]);
      await P.shot(`${OUT}_floor_kings_5.jpg`);
      // 凯尔萨斯：剧透开着才是真名
      await P.ev(`${pick('奥古斯都·凯尔萨斯·萨尔维斯')}.click(); return 1`); await sleep(300);
      ok(await P.ev(`return document.querySelector('#atl .at-panel h2').textContent === '奥古斯都·凯尔萨斯·萨尔维斯'`), '凯尔萨斯剧透开着露真名');
      // 奥里恩：二阶带终章
      await P.ev(`document.querySelector('[data-chip="楼层主"]').click(); return 1`); await sleep(300);
      await P.ev(`${pick('奥里恩')}.click(); return 1`); await sleep(300);
      await P.ev(`document.querySelector('#atl .a-phs [data-ph="1"]').click(); return 1`); await sleep(300);
      r = await P.ev(`const pn = document.querySelector('#atl .at-panel'); return [!!pn.querySelector('.a-fbs-big'), [...pn.querySelectorAll('.a-song h3')].map((h) => h.textContent).join('｜'), pn.innerText.includes('打完以后')]`);
      ok(r[0] && /终章《晓钟初鸣》/.test(r[1]) && r[2], '奥里恩没有原画画层号牌，二阶带终章和结局：' + r[1]);
      await P.shot(`${OUT}_floor_orion_2.jpg`);
      // 每一位每一阶都过一遍禁词
      const all = await P.ev(`const out = []; for (const ch of ['楼层主', '迷宫城之主']) { document.querySelector('#atl [data-chip="' + ch + '"]').click(); await new Promise((r) => setTimeout(r, 80));
        for (const c of [...document.querySelectorAll('#atl .a-ac.foes')]) { c.click(); await new Promise((r) => setTimeout(r, 60)); const n = document.querySelectorAll('#atl .a-phs .a-ph').length || 1;
          for (let k = 0; k < n; k++) { const ph = document.querySelector('#atl .a-phs [data-ph="' + k + '"]'); if (ph) { ph.click(); await new Promise((r) => setTimeout(r, 40)); } out.push(document.querySelector('#atl .at-panel').innerText); } } } return out`);
      const hit = all.map((t) => [t.slice(0, 12), String(t).match(BAN)]).filter((x) => x[1]);
      ok(all.length === 42 && !hit.length, `剧透开着翻遍 ${all.length} 阶没有禁词` + (hit.length ? '：' + hit.map((x) => x[0] + x[1][0]).join(' ') : ''));
    } else {
      await P.ev(`document.querySelector('[data-chip="楼层主"]').click(); return 1`); await sleep(300);
      await P.ev(`${pick('奥里恩')}.click(); return 1`); await sleep(300);
      r = await P.ev(`const pn = document.querySelector('#atl .at-panel'); return [!!pn.querySelector('.a-fbs-big'), pn.querySelector('.a-full').textContent, pn.innerText.includes('那一层'), pn.innerText.includes('乐章')]`);
      ok(r[0] && r[2] && !r[3], '奥里恩剧透关着：层号牌、一阶名号、那一层，没有乐章：' + r[1]);
      await P.shot(`${OUT}_floor_orion_off.jpg`);
    }
    await P.ev(`Atlas.close(); return 1`); await sleep(400);
  }
}
// ---------- 图鉴人物：常驻名录表以外的传奇（11-25）。相遇一栏空了，五位老传奇和活到今天的旧人六位都在传奇里；档位只在剧透开着时露 ----------
const AT = await P.ev('return __now.AT');
const OLD = ['希尔妲', '霍布', '凯恩', '珀拉', '卡兰缇娅', '蕾娃·升井', '苏海拉', '托芙·深井', '朵薇·六钟', '坎黛丝·焰沙', '肯特·墨鳞'];
const nLeg = AT.people.filter((x) => x.at.now === '传奇').length;
await P.ev(`__now.setSpoil(false); Atlas.open(); return 1`); await sleep(700);
await P.ev(`const b = document.querySelector('[data-tab="people"]'); if (b) b.click(); return 1`); await sleep(500);
const grps = await P.ev(`return [...document.querySelectorAll('#atl .a-grp')].map((e) => e.firstChild.textContent)`);
ok(!grps.includes('相遇') && grps.includes('传奇'), '人物一栏分组：' + grps.join('、'));
const chipT = await P.ev(`return [...document.querySelectorAll('#atl .a-chip')].map((e) => e.textContent.replace(/\\s+/g, ''))`);
ok(chipT.includes('传奇' + nLeg), '传奇一栏 ' + nLeg + ' 位：' + chipT.join(' '));
const cards = await P.ev(`return [...document.querySelectorAll('#atl .a-ac.people')].map((b) => [b.querySelector('.a-nm').textContent, b.querySelector('.a-tags').textContent, !!b.querySelector('.a-spr')])`);
for (const n of OLD) {
  const c = cards.find((x) => x[0] === n);
  ok(c && /^传奇/.test(c[1]) && c[2], `${n} 在传奇里、有小像` + (c ? '（' + c[1] + '）' : ''));
}
await P.ev(`const g = [...document.querySelectorAll('#atl .a-grp')].find((e) => e.firstChild.textContent === '传奇'); if (g) g.scrollIntoView(); return 1`); await sleep(400);
await P.shot(`${OUT}_atlas_legends.jpg`);
await P.ev(`const g = [...document.querySelectorAll('#atl .a-ac.people')].find((b) => b.querySelector('.a-nm').textContent === '希尔妲'); if (g) g.scrollIntoView({ block: 'center' }); return 1`); await sleep(400);
await P.shot(`${OUT}_atlas_old.jpg`);
await P.ev(`Atlas.close(); return 1`); await sleep(400);
for (const sp of [false, true]) {
  await P.ev(`__now.setSpoil(${sp}); return 1`);
  for (const n of OLD) {
    ok(await P.ev(`return __now.openProf(${JSON.stringify(n)})`), `${n} 的档案开得了`);
    await sleep(250);
    await P.ev(`const im = document.querySelector('#pf .art img'); for (let i = 0; i < 40 && !(im.complete && im.naturalWidth); i++) await new Promise((r) => setTimeout(r, 100)); return 1`);
    const r = await P.ev(`const pf = document.querySelector('#pf'); const sps = [...pf.querySelectorAll('.spoil')]; return [pf.querySelector('.k').textContent, sps.length, sps.every((e) => getComputedStyle(e).display !== 'none'), sps.map((e) => e.querySelector('h5').textContent).join('、'), pf.innerText.includes('名录'), pf.querySelector('.art img').naturalWidth]`);
    ok(r[1] >= 1 && r[2] === sp && r[3].includes('位阶') && r[4] && r[5] > 0, `${n}：${r[0]}，剧透${sp ? '开着露' : '关着藏'} ${r[3]}，写了名录，大像 ${r[5]}px`);
    await banCheck(n + '档案', '#pf');
    if (n === '苏海拉' || n === '希尔妲') await P.shot(`${OUT}_prof_${n === '苏海拉' ? 'suhaila' : 'hilda'}_${sp ? 'on' : 'off'}.jpg`);
    await P.ev(`document.querySelectorAll('.dlg [data-close], .dlg .x').forEach((b) => b.click()); return 1`); await sleep(350);
  }
}
// ---------- 档案换衣着（11-25）：有拼图的人五个钮（艺术照加四套），点了换得过去；九格表情；图取得到。从图鉴点“看档案”开得出来、盖在图鉴上面 ----------
const PSK = await P.ev('return [...__now.PSK]');
const keyed = AT.people.filter((x) => x.key);
ok(keyed.every((x) => PSK.includes(x.key)), `有立绘的 ${keyed.length} 位都有换衣着的拼图（${PSK.length} 张）`);
const deadPs = await P.ev(`const bad = []; for (const k of ${JSON.stringify(PSK)}) { try { const r = await fetch(A('assets/ps/' + k + '.webp')); const b = await r.blob(); if (!r.ok || b.size < 20000) bad.push(k); } catch (e) { bad.push(k); } } return bad`);
ok(!deadPs.length, '换衣着的拼图都取得到' + (deadPs.length ? '：' + deadPs.join(' ') : ''));
for (const n of ['艾莉娅·罗森塔尔', '卡麦莉加·夜绯', '苏海拉', '希尔妲', '索恩薇娅·里德']) {
  await P.ev(`__now.openProf(${JSON.stringify(n)}); return 1`); await sleep(400);
  const r = await P.ev(`const pf = document.querySelector('#pf'); const bs = [...pf.querySelectorAll('.otabs button')]; const out = [bs.length, pf.querySelectorAll('.faces figure').length];
    for (const b of bs) { b.click(); await new Promise((r) => setTimeout(r, 80)); const art = pf.querySelector('.art'); out.push((art.classList.contains('o') ? getComputedStyle(art.querySelector('.spr')).backgroundPosition : 'img') + (b.getAttribute('aria-pressed') === 'true' ? '' : '!')); }
    return out`);
  ok(r[0] === 5 && r[1] === 9 && r.slice(2).join(',') === 'img,0% 0px,33.333% 0px,66.667% 0px,100% 0px', `${n} 换衣着五格、表情九格：${r.slice(2).join(' ')}`);
  if (n === '卡麦莉加·夜绯') { await P.ev(`document.querySelector('#pf .otabs [data-o="3"]').click(); return 1`); await sleep(600); await P.shot(`${OUT}_prof_outfit.jpg`); }
  await banCheck(n + '档案', '#pf');
  const cup = await P.ev(`return /[Cc][Uu][Pp]|罩杯|三维/.test(document.querySelector('#pf').innerText)`);
  ok(!cup, `${n} 档案里没有罩杯、三维`);
  await P.ev(`document.querySelectorAll('.dlg [data-close], .dlg .x').forEach((b) => b.click()); return 1`); await sleep(350);
}
await P.ev(`Atlas.open(); return 1`); await sleep(700);
await P.ev(`const b = [...document.querySelectorAll('#atl .a-ac.people')].find((b) => b.querySelector('.a-nm').textContent === '苏海拉'); b.scrollIntoView({ block: 'center' }); b.click(); return 1`); await sleep(500);
await P.ev(`const b = document.querySelector('#atl [data-prof]'); b.scrollIntoView({ block: 'center' }); return 1`); await sleep(300);
const bp = await P.ev(`const q = document.querySelector('#atl [data-prof]').getBoundingClientRect(); return [q.x + q.width / 2, q.y + q.height / 2]`);
await P.click(bp[0], bp[1]); await sleep(900);
const onTop = await P.ev(`const pf = document.querySelector('#pf'); const t = document.elementFromPoint(innerWidth / 2, innerHeight / 2); return [pf.classList.contains('on'), pf.contains(t), (pf.querySelector('h3') || {}).textContent]`);
ok(onTop[0] && onTop[1] && onTop[2] === '苏海拉', '图鉴里点“看档案”，档案盖在图鉴上面：' + JSON.stringify(onTop));
await P.shot(`${OUT}_atlas_to_prof.jpg`);
await P.ev(`document.querySelectorAll('.dlg [data-close], .dlg .x').forEach((b) => b.click()); return 1`); await sleep(350);
await P.ev(`Atlas.close(); return 1`); await sleep(400);
// 旅伴“样子”不拿前后比
const lookBad = AT.people.filter((x) => x.at.now === '旅伴').map((x) => [x.n, (x.pf.find((q) => q[0] === '样子') || [])[1] || '']).filter(([, t]) => /长开|这两年|这三年|稚气淡/.test(t));
ok(!lookBad.length, '旅伴的样子没有拿前后比的话' + (lookBad.length ? '：' + lookBad.map((x) => x[0]).join('、') : ''));
await P.ev(`__now.setSpoil(false); return 1`);
const errs = P.errs.filter((e) => !/favicon/.test(e));
ok(!errs.length, '控制台没有报错' + (errs.length ? JSON.stringify(errs.slice(0, 5)) : ''));
console.log('对不上', bad);
await P.close(); process.exit(0);
