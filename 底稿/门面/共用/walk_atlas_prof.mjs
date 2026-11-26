// 图鉴“看档案”走查（11-25 写的）：各本图鉴每一类（旅伴、相遇、传奇）挑头、中、末三位，真鼠标点“看档案”，看档案层出没出来、是不是盖在图鉴最上面。
//   本地服务 共用/utf8_server.py（8774，根是 底稿/门面/），无头 Chrome 开调试口：CDP_PORT=<口> node 底稿/门面/共用/walk_atlas_prof.mjs 小样_月银纪书 1920 945 [截图前缀]
//   末行“对不上 0”算过。11-25 以前四本书的档案长在时代页里头，时代页没开着时从图鉴点开量出来是 0×0；此刻那一本的档案层（30）压在图鉴（40）底下。
// 各本图鉴：每一类（旅伴、相遇、传奇）挑几位带“看档案”的，真鼠标点“看档案”，看档案层出没出来、是不是盖在最上面
const { open, sleep } = await import('file:///E:/aldran_art/底稿/门面/第二轮/建档/tools/cdp.mjs');
const book = process.argv[2], W = +(process.argv[3] || 1920), H = +(process.argv[4] || 945), OUT = process.argv[5];
const url = 'http://localhost:8774/' + encodeURIComponent(book) + '/local.html?t=' + Date.now();
const P = await open(W, H, { mobile: W < 861, url });
await P.until('window.Atlas', 30000); await sleep(3000);
await P.ev('Atlas.open(); return 1'); await sleep(1500);
const list = await P.ev(`return [...document.querySelectorAll('#atl .a-ac.people')].map((b) => [b.dataset.sel, b.querySelector('.a-nm').textContent, b.querySelector('.a-tags .a-tg').textContent])`);
const by = {};
for (const x of list) (by[x[2]] = by[x[2]] || []).push(x);
console.log('类：', Object.entries(by).map(([k, v]) => k + v.length).join(' '));
let bad = 0, tot = 0;
for (const [k, v] of Object.entries(by)) {
  const pick = [v[0], v[Math.floor(v.length / 2)], v[v.length - 1]];
  for (const x of pick) {
    await P.ev(`Atlas.close && 0; return 1`);
    await P.ev(`const b = document.querySelector('#atl [data-sel="${x[0]}"]'); b.scrollIntoView({block:'center'}); b.click(); return 1`); await sleep(500);
    const r = await P.ev(`const b = document.querySelector('#atl [data-prof]'); if (!b) return null; b.scrollIntoView({block:'center'}); const q = b.getBoundingClientRect(); return [q.x + q.width / 2, q.y + q.height / 2]`);
    if (!r) { console.log('  · 没有看档案钮', k, x[1]); continue; }
    tot++;
    await sleep(200);
    await P.click(r[0], r[1]); await sleep(1500);
    const st = await P.ev(`const cand = [...document.querySelectorAll('#prof, #pf, .prof, [id^=prof]')].filter((e) => !e.hidden && getComputedStyle(e).display !== 'none' && getComputedStyle(e).visibility !== 'hidden' && e.getBoundingClientRect().width > 50);
      const top = document.elementFromPoint(innerWidth / 2, innerHeight / 2);
      return [cand.map((e) => '#' + e.id + '.' + [...e.classList].join('.')).join(' '), !!(top && cand.some((c) => c.contains(top))), top ? top.tagName + '#' + top.id + '.' + top.className.toString().slice(0, 40) : '']`);
    const okk = st[0] && st[1];
    if (!okk) bad++;
    console.log((okk ? '  ✓ ' : '  ✗ ') + k + ' ' + x[1] + '｜' + st.join('｜'));
    if (!okk && OUT) await P.shot(OUT + '_' + tot + '.jpg');
    // 关档案回图鉴
    await P.ev(`document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })); return 1`); await sleep(500);
    await P.ev(`if (!document.querySelector('#atl.on')) Atlas.open(); return 1`); await sleep(600);
  }
}
console.log('点了', tot, '对不上', bad, P.errs.slice(0, 3).join(' '));
await P.close(); process.exit(0);
