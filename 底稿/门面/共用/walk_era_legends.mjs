// 时代页传奇卡走查（11-25 写的）：每一页数带档案记号的传奇卡，点头一张、末一张（真鼠标），看档案出没出来、名字对不对。
//   CDP_PORT=<口> node 底稿/门面/共用/walk_era_legends.mjs 小样_月银纪书 1920 945（四本书都认，此刻那一本没有时代页）。末行“对不上 0”算过。
// 时代页上的传奇卡：每一页数一数带档案记号的有几张，点头一张、末一张（真鼠标），看档案出没出来
const { open, sleep } = await import('file:///E:/aldran_art/底稿/门面/第二轮/建档/tools/cdp.mjs');
const book = process.argv[2], W = +(process.argv[3] || 1920), H = +(process.argv[4] || 945);
const P = await open(W, H, { mobile: W < 861, url: 'http://localhost:8774/' + encodeURIComponent(book) + '/local.html?t=' + Date.now() });
await P.until('window.__bk || window.__mz', 30000); await sleep(3000);
const api = await P.ev('return window.__mz ? "__mz" : "__bk"');
const n = await P.ev(api === '__mz' ? 'return __mz.RINGS ? document.querySelectorAll("#page").length && 6 : 6' : 'return document.querySelectorAll(".tick, [data-era]").length');
const N = api === '__mz' ? 6 : (book.includes('月银') ? 27 : book.includes('纷争') ? 21 : 6);
let bad = 0, tot = 0, clicked = 0;
for (let i = 0; i < N; i++) {
  await P.ev(`${api}.${api === '__mz' ? 'openEra' : 'open'}(${i}); return 1`); await sleep(1500);
  const figs = await P.ev(`return [...document.querySelectorAll('#pg-body .cast.lg figure')].map((f) => [f.querySelector('b').textContent, !!f.dataset.p])`);
  const withP = figs.filter((f) => f[1]).length; tot += figs.length;
  if (withP < figs.length) { bad++; console.log(`  ✗ 第 ${i + 1} 页传奇 ${figs.length} 张，能点的 ${withP}：点不开 ${figs.filter((f) => !f[1]).map((f) => f[0]).join('、')}`); }
  for (const pick of [0, figs.length - 1].filter((x, k, a) => x >= 0 && a.indexOf(x) === k)) {
    if (!figs[pick] || !figs[pick][1]) continue;
    const r = await P.ev(`const f = [...document.querySelectorAll('#pg-body .cast.lg figure')][${pick}]; f.scrollIntoView({ block: 'center' }); await new Promise((r) => setTimeout(r, 300)); const q = f.getBoundingClientRect(); return [q.x + q.width / 2, q.y + q.height / 3]`);
    await P.click(r[0], r[1]); await sleep(1200); clicked++;
    const st = await P.ev(`const p = document.querySelector('#prof'); const q = p.getBoundingClientRect(); const top = document.elementFromPoint(innerWidth / 2, innerHeight / 2); return [!p.hidden && p.classList.contains('on') && q.width > 100, p.contains(top), (p.querySelector('h2') || {}).textContent || '']`);
    if (!(st[0] && st[1] && st[2] === figs[pick][0])) { bad++; console.log(`  ✗ 第 ${i + 1} 页点 ${figs[pick][0]}：`, JSON.stringify(st)); }
    await P.ev(`document.querySelector('#prof .x').click(); return 1`); await sleep(500);
  }
  await P.ev(`${api}.${api === '__mz' ? 'closeEra' : 'close'}(); return 1`); await sleep(700);
}
console.log(`${book} ${W}：${N} 页，传奇卡 ${tot} 张，点了 ${clicked} 回，对不上 ${bad}`, P.errs.filter((e) => !/favicon/.test(e)).slice(0, 3).join(' '));
await P.close(); process.exit(0);
