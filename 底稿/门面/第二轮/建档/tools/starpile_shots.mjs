// 命星那一步的落星（废卡）和候星（预选）在页面上走一遍、截图（11-25）： node starpile_shots.mjs 宽 高 前缀 [书=bronze]
// 真点页面上的钮（点以前先看那一枚钮是不是露在外头、没被别的盖住），每一段记一回各处的数。本地服务 8774、无头 Chrome 9371（CDP_PORT 换）。
// 走：发一手 → 翻开一张 → 放进候星（放满三颗，第四颗挡回）→ 留下一颗 → 再抽（没留的进落星）→ 摊开手边的星 → 撤下一颗候星 → 从候星里留一颗
//     → 手艺那一叠抽到空 → 空了再点抽 → 落星归叠 → 往下走到第九步。
import { open, sleep, BASE } from './cdp.mjs';
import fs from 'node:fs';
const [W, H] = [+(process.argv[2] || 1920), +(process.argv[3] || 945)];
const OUT = process.argv[4] || 'shots/sp'; const book = process.argv[5] || 'bronze';
const MS = { bronze: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, moon: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' },
  strife: { book: 'strife', era: '纷争纪', at: 's01', title: '执式者', line: '灰的年月·执式者', year: '元年' }, maze: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' },
  now: { book: 'maze', era: '迷宫纪', at: '1001', site: '阿卡迪亚·外环棚区', ti: '井口边的不眠之城', line: '迷宫纪1001年·阿卡迪亚·外环棚区', year: '1001' } };
const MOBILE = W < 861;
fs.mkdirSync(OUT.replace(/[\\/][^\\/]*$/, ''), { recursive: true });
const P = await open(W, H, { mobile: MOBILE, url: BASE + '?t=' + Date.now() });
await P.until('window.__tb && window.Shell', 30000);
await P.ev('__tb.skip(); return 1'); await sleep(1200);
await P.ev(`await Shell.startBuild(${JSON.stringify(MS[book])}); return 1`); await sleep(900);
let bad = 0;
const want = (ok, what) => { if (!ok) bad++; console.log((ok ? '   ✓ ' : '   ✗ ') + what); };
const idle = async () => { await sleep(200); await P.until('window.__bd && !__bd.busy', 20000); await sleep(350); };
// 点一枚钮：要在页面上、没被盖住（滚进来以后拿它正中那一点去问页面，问到的得是它自己或它里头的东西）
const cl = async (sel, i = 0) => {
  const r = await P.ev(`const e = document.querySelectorAll(${JSON.stringify('#sh-build ' + sel)})[${i}]; if (!e) return '没有 ' + ${JSON.stringify(sel)}; if (e.disabled) return '点不动 ' + ${JSON.stringify(sel)};
    e.scrollIntoView({ block: 'nearest' }); await new Promise((r2) => setTimeout(r2, 60)); const b = e.getBoundingClientRect(); if (!b.width || !b.height) return '看不见 ' + ${JSON.stringify(sel)};
    const t = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2); if (!t || !(t === e || e.contains(t))) return '被盖住 ' + ${JSON.stringify(sel)} + ' ← ' + (t ? t.className : '');
    e.click(); return 'ok'`);
  if (r !== 'ok') { bad++; console.log('   ✗ ' + r); }
  await idle(); return r;
};
const primary = () => cl(MOBILE ? '.bx-dbtn [data-a="next"]' : '.bx-ctl [data-a="next"]');
const Z = (k) => P.ev(`const z = __bd.star.zones(${JSON.stringify(k)}); return { kept: z.kept, hand: z.hand, hold: z.hold, gone: z.gone, deck: z.deck.length, pool: z.pool.length }`);
const cnt = (z) => `星叠 ${z.deck}　台面 ${z.hand.length}　候星 ${z.hold.length}　落星 ${z.gone.length}　留下 ${z.kept ? 1 : 0}`;
const say = () => P.ev(`return [...document.querySelectorAll('#sh-build .bx-say p')].map((p) => p.textContent).filter(Boolean).join(' ')`);
const shot = async (n) => { await idle(); await P.shot(`${OUT}_${n}.jpg`); };
// 页面横着不该能滑；选牌那一块露在外头的高度记下来
const fit = async (tag) => {
  const r = await P.ev(`const st = document.querySelector('#sh-build .bx-stage'), sl = document.querySelector('#sh-build .bx-slots'), ctl = document.querySelector('#sh-build .bx-ctl').getBoundingClientRect(); const a = st.getBoundingClientRect(), b = sl.getBoundingClientRect();
    const tray = document.querySelector('#sh-build .bx-tray').getBoundingClientRect(); const over = [...document.querySelectorAll('#sh-build .bx-tray > *')].filter((e) => e.getBoundingClientRect().width && (e.getBoundingClientRect().right > tray.right + 1 || e.scrollWidth > e.clientWidth + 1 && !e.classList.contains('kp'))).map((e) => e.className);
    const wide = [...st.querySelectorAll('*')].filter((e) => !e.closest('.rays,.glow') && e.getBoundingClientRect().width && e.getBoundingClientRect().right > a.right + 1).map((e) => String(e.className || e.tagName)).slice(0, 4);          // 牌上的光芒本来就比牌宽，台面横着是裁掉的，不算
    return { wide, dx: document.documentElement.scrollWidth - innerWidth, see: Math.round(Math.min(a.bottom, ctl.top) - Math.max(a.top, b.top)), trayH: Math.round(tray.height), over }`);
  want(!r.wide.length && r.dx <= 1, `${tag}：台面上没有横着撑出去的` + (r.wide.length ? '（' + r.wide.join('、') + '）' : ''));
  want(!r.over.length, `${tag}：那一排没有挤出去的` + (r.over.length ? '（' + r.over.join('、') + '）' : ''));
  console.log(`   选牌的区露出来 ${r.see}px 高，留下、候星、落星那一排 ${r.trayH}px 高`);
};

await P.ev(`const F = __bd.F; F._route = 'direct'; Object.assign(F, { soul: 'native', name: '诺拉', sex: '女', age: '18', race: 'human', tier: '启源·凝华', statMode: 'even', path: '渊垒', _max: 11 }); __bd.deal(true); __bd.go(8); return 1`);
await sleep(800); await idle(); await sleep(2600);
console.log('== 发一手'); await shot('01_发一手'); await fit('刚进来');
let z = await Z('S'); want(z.hand.length === 10 && !z.gone.length && !z.hold.length, cnt(z));

console.log('== 翻开一张看'); await cl('.bx-slots .bx-star:not(.cus)', 2); await shot('02_翻开一张');
want(await P.ev(`return !!document.querySelector('#sh-build .bx-detail.on [data-a="shold"]') && !__bd.F.starS`), '翻开只是看，还没留，说明里有“放进候星”');
want((await P.ev(`return document.querySelector('#sh-build ${MOBILE ? '.bx-dbtn' : '.bx-ctl'} [data-a="next"]').textContent`)) === '留下这一颗', '主钮写的是“留下这一颗”');

console.log('== 放进候星'); const h1 = z.hand[2]; await cl('.bx-detail [data-a="shold"]'); await shot('03_放进候星');
z = await Z('S'); want(z.hold.length === 1 && z.hold[0] === h1 && !z.hand.includes(h1), cnt(z) + '　她说：' + await say());
for (const i of [0, 0]) { await cl('.bx-slots .bx-star:not(.cus)', 3 + i); await cl('.bx-detail [data-a="shold"]'); }
z = await Z('S'); want(z.hold.length === 3, '放满三颗　' + cnt(z));
await cl('.bx-slots .bx-star:not(.cus)', 4); await cl('.bx-detail [data-a="shold"]'); await shot('04_候星满了');
const z4 = await Z('S'); want(z4.hold.length === 3 && z4.hand.length === z.hand.length, '第四颗挡回　她说：' + await say());
await cl(MOBILE ? '.bx-dbtn [data-a="unfocus"]' : '.bx-dx');
if (MOBILE) want(await P.ev(`return getComputedStyle(document.querySelector('#sh-build .bx-dim')).display === 'none'`), '收起说明，暗幕也收了');

console.log('== 留下一颗'); z = await Z('S'); const k1 = z.hand[0]; await cl('.bx-slots .bx-star:not(.cus)', 0); await primary(); await shot('05_留下一颗');
z = await Z('S'); want(z.kept === k1 && z.hand.includes(k1), cnt(z) + '　她说：' + await say());
want(await P.ev(`return __bd.step === 8 && !!document.querySelector('#sh-build .bx-star.picked') && document.querySelector('#sh-build .bx-detail').hidden`), '留完还在第八步，那一张盖着“留”，说明收起');

console.log('== 再抽'); const before = z; await cl('.bx-tray [data-a="draw"]'); await sleep(2600); await shot('06_再抽_没留的进落星');
z = await Z('S');
want(z.kept === k1 && z.hold.join() === before.hold.join(), '再抽没动留下的和候星');
want(z.gone.length === before.hand.length - 1 && before.hand.filter((id) => id !== k1).every((id) => z.gone.includes(id)), '上一手没留的都进了落星　' + cnt(z));
want(z.hand.every((id) => !before.hand.includes(id) && !before.hold.includes(id)), '新的一手没有上一手、候星里的牌');
await fit('再抽以后');

console.log('== 手边的星'); await cl(MOBILE ? '.bx-tray .sum' : '.bx-tray .gn'); await shot('07_手边的星');
want(await P.ev(`return document.querySelectorAll('#sh-build .bx-detail.on .bx-trow').length === 4 && document.querySelectorAll('#sh-build .bx-detail.on .bx-gone button').length === ${z.gone.length}`), '摊开：留下的一行、候星三行、落星一片');

console.log('== 撤下一颗候星'); const d1 = z.hold[2]; await cl('.bx-detail .bx-trow [data-a="sdrop"]', 3); await shot('08_撤下候星_进落星');
z = await Z('S'); want(z.hold.length === 2 && z.gone.includes(d1), cnt(z) + '　她说：' + await say());

console.log('== 从候星里留一颗'); const h0 = z.hold[0]; await cl('.bx-detail .bx-trow [data-a="skeep"]', 0); await shot('09_候星里留_原先那颗顶进候星');
z = await Z('S'); want(z.kept === h0 && z.hold.includes(k1) && z.hold.length === 2 && !z.gone.includes(k1), '原先留下的那颗顶进候星，没丢　' + cnt(z) + '　她说：' + await say());
await cl(MOBILE ? '.bx-dbtn [data-a="unfocus"]' : '.bx-dx');

console.log('== 手艺那一叠抽到空'); await cl('.bx-sttab [data-a="pool"][data-v="A"]'); await sleep(2400); await idle();
let a = await Z('A'), n = 0;
while (a.deck > 0 && n++ < 40) { if (a.deck > 14) { await P.ev(`__bd.star.draw('A'); return 1`); } else { await P.ev(`__bd.go(8); return 1`); await idle(); await cl('.bx-tray [data-a="draw"]'); await sleep(1500); await idle(); } a = await Z('A'); }
await P.ev(`__bd.go(8); return 1`); await sleep(2200); await shot('10_抽空了');
a = await Z('A'); want(a.deck === 0 && a.hand.length > 0, cnt(a));
want(await P.ev(`return document.querySelector('#sh-build .bx-tray .dr').textContent === '叠空了' && !!document.querySelector('#sh-build .bx-tray .rs.call') && !!document.querySelector('#sh-build .bx-dry')`), '钮写“叠空了”，落星归叠亮起来，底下有一行提示');
await fit('抽空的时候');
const e0 = P.errs.length;
if (MOBILE) await P.ev(`__bd.star.draw('A'); return 1`); else await cl('.bx-tray [data-a="draw"]');
if (MOBILE) { await P.ev(`const b = document.querySelector('#sh-build .bx-tray .dr'); b.click(); return 1`); await idle(); }          // 手机上抽空以后那一枚换成了落星归叠，这里直接叫它一回，看不报错
const a2 = await Z('A'); await shot('11_空了再抽_提示');
want(a2.hand.join() === a.hand.join() && a2.gone.length === a.gone.length && P.errs.length === e0, '空了再抽：牌没动，没报错　她说：' + await say());

console.log('== 落星归叠'); await cl('.bx-tray [data-a="sreset"]'); await shot('12_落星归叠');
const a3 = await Z('A'); want(a3.gone.length === 0 && a3.deck === a.gone.length && a3.hand.join() === a.hand.join() && a3.kept === a.kept && a3.hold.join() === a.hold.join(), '落星回了星叠，台面、候星、留下的没动　' + cnt(a3) + '　她说：' + await say());
const zS = await Z('S'); want(zS.kept === h0 && zS.hold.length === 2 && zS.gone.length === z.gone.length, '别的池子没受牵连（天赋那一池 ' + cnt(zS) + '）');

console.log('== 往下走'); await cl('.bx-ctl [data-a="next"]'); await shot('13_第九步');
want(await P.ev(`return __bd.step === 9`), '主钮回到“带上这三颗”，走到第九步');
const cred = await P.ev(`return __bd.cred()`);
want(/Passive\/Special：[^\n]+\(Special \| /.test(cred) && !/落星|候星|星叠/.test(cred), '凭证里命星那两行照旧，没有落星、候星这些字');
const errs = P.errs.filter((e) => !/favicon/.test(e));
console.log(`\n${W}×${H} ${book}　对不上的 ${bad} 处；控制台报错 ${errs.length} 条`); for (const e of errs.slice(0, 8)) console.log('  ', e);
await P.close();
await sleep(300); process.exitCode = bad || errs.length ? 1 : 0;
