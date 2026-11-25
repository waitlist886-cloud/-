// 凭证逐字比（11-25 落星和候星那一回）：同一组选法，改前的外壳和改后的各出一份凭证，一个字一个字比。 node credcmp_1125.mjs [存凭证的目录]
// 先起改前的对照页：node headproxy.mjs（8779）。本地服务 8774、无头 Chrome 9371（CDP_PORT 换）。
// 改后那一边的命星不是直接写进去的：照 route 走一遍落星、候星、归叠、换留，或者真的在页面上点牌、点主钮，最后留下的是哪三颗，改前那一边就直接写哪三颗。
import { open, sleep, BASE } from './cdp.mjs';
import fs from 'node:fs';
const OUT = process.argv[2] || '';
const OLD = process.env.OLD_BASE || 'http://localhost:8779/' + encodeURIComponent('小样_外壳') + '/local.html';
const SC = [
  { id: 'moon_line', route: 'piles', st: { S: 3, P: 5, A: 2 }, m: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' }, f: `F.soul='isekai'; F.world='原来是城里的护士'; F.name='莉娅'; F.sex='女'; F.age='19'; F.height='165cm'; F.look='银发'; F.race='human'; F.tier='共鸣·织理'; F.statMode='even'; F.weapon=E.weapons[0].n; F.style='蓄斩'; F.marts=E.arts[0].n; F.school=E.schools[0].n; F.oath='守序善良'; F.wishPick='守住一堆火'; F.extra='想要一只狗'; F.giftN=G[0].n; F.sheet={'哪一家':'城门边'};` },
  { id: 'strife_free', route: 'viahold', st: { S: 0, P: 7, A: 11 }, m: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, f: `F.soul='native'; F.name='托尔克'; F.year='1150'; F.race='dwarf'; F.goldN=GD; F.goldKnow=1; F.tier='灵格·塑形'; F.statMode='cap'; F.path='真理'; F.weapon='长戟'; F.oath='混乱中立'; F.sheet={'姓或家':'铁砧家'}; F.wall='北段'; F.skills=SK.slice(0,2); F.skill2='想学会读术式'; F.wish='活下去';` },
  { id: 'strife_line', route: 'none', st: {}, m: { book: 'strife', era: '纷争纪', at: 's01', title: '执式者', line: '灰的年月·执式者', year: '元年' }, f: `F.soul='reborn'; F.name='维恩'; F.race='elf'; F.goldN='-'; F.statMode='later'; F.path='*'; F.pathCustom='剑与诗'; F.oath=''; F.sheet={'哪个村':'灰村','什么行当':'抄书','父亲是谁':'书吏'};` },
  { id: 'bronze_gold', route: 'piles', st: { S: 10 }, m: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, f: `F.soul='native'; F.name='诺拉'; F.race='dwarf'; F.goldN='*'; F.tier='启源·临界'; F.statMode='even'; F.path='渊垒'; F.team='灰鸦团'; F.grade='低档'; F.sheet={'姓或家':'炉脉','从哪里来':'雨城'};` },
  { id: 'bronze_free', route: 'direct', st: { P: 4 }, m: { book: 'bronze', era: '山铜纪', at: 'free', title: '无字碑', line: '', year: '' }, f: `F.soul='isekai'; F.name='凯'; F.year='700'; F.race='beastkin'; F.tier='英雄·破格'; F.statMode='even'; F.path='铁律'; F.giftN=G[1].n; F.team='夜枭'; F.place='白碑下的酒馆';` },
  { id: 'maze_line', route: 'viahold', st: { A: 9 }, m: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' }, f: `F.soul='isekai'; F.name='艾琳'; F.race='halfling'; F.tier='共鸣·寻音'; F.statMode='even'; F.path='行猎'; F.giftN=G[G.length-1].n; F.rank='风路';` },
  { id: 'maze_free_custom', route: 'piles', st: { S: '*', P: 20, A: '*' }, m: { book: 'maze', era: '迷宫纪', at: 'free', title: '空白委托', line: '', year: '' }, f: `F.soul='native'; F.name='格雷'; F.year='300'; F.race='human'; F.goldN=GD; F.tier='极境·绝地'; F.statMode='even'; F.path='天平'; F.grade='中档'; F.sheet={'谁担保':'书记','姓或家':'格雷家'}; F.scSn='账页过目'; F.scSr='Epic'; F.scSd='看过的账一页不忘，一天三回'; F.scAn='压秤'; F.scAt='Active'; F.scAr='Legend'; F.scAd='一句话压住价，冷却一天';` },
  { id: 'now_ui', route: 'ui', st: { S: 0, P: 1, A: 2 }, m: { book: 'maze', era: '迷宫纪', at: '1001', site: '阿卡迪亚·外环棚区', ti: '井口边的不眠之城', line: '迷宫纪1001年·阿卡迪亚·外环棚区', year: '1001' }, f: `F.soul='native'; F.name='米拉'; F.sex='女'; F.age='17'; F.race='human'; F.goldN='-'; F.tier='启源·凝华'; F.statMode='even'; F.path='惊弦'; F.oath='中立善良';` },
  { id: 'maze_q3_full', route: 'full', st: { S: 30, P: 40, A: 50 }, m: { book: 'maze', era: '迷宫纪', at: 'q3', title: '繁荣的年月', line: '繁荣的年月·屠林令', year: '433' }, f: `F.soul='reborn'; F.world='前一世是个教书的'; F.name='塞恩'; F.age='22'; F.race='beastkin'; F.goldN='-'; F.tier='共鸣·织理'; F.statMode='even'; F.path='诡刃'; F.weapon='双刃'; F.rank='风路';` },
  { id: 'strife_late_ui', route: 'ui', st: { S: 4, P: 0, A: 6 }, m: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, f: `F.soul='native'; F.name='伊瑟'; F.year='10900'; F.race='demon'; F.goldN='-'; F.tier='极境·峙岳'; F.statMode='even'; F.path='摧锋'; F.weapon='大剑'; F.oath='守序邪恶'; F.wall='南段';` },
];
const PRE = (s) => `await Shell.startBuild(${JSON.stringify(s.m)}); await new Promise((r) => setTimeout(r, 500));
  const F = __bd.F, E = (await (await fetch(A('data/build.json'))).json()).eras[${JSON.stringify(s.m.book)}]; const G = __bd.giftPool(); const gs = __bd.gods().filter((g) => !g.off); const GD = gs.length ? gs[0].n : '*';
  const SK = ((E.periods || [])[0] || {}).skills || [];
  for (const k of Object.keys(F)) if (!/^_/.test(k)) delete F[k];
  ${s.f}
  const want = ${JSON.stringify(s.st)}, pick = {}; for (const k of ['S', 'P', 'A']) { const p = __bd.pool(k); pick[k] = want[k] == null ? '' : want[k] === '*' ? '*' : (p.length ? p[want[k] % p.length].id : ''); }`;
// 改后：照 route 把命星留成 pick 那三颗（ui 的是在页面上点出来的，点到哪颗算哪颗），回最后留下的 id 和凭证
const NEWRUN = (s) => PRE(s) + `
  const S = __bd.star, route = ${JSON.stringify(s.route)};
  const idle = async () => { await new Promise((r) => setTimeout(r, 80)); for (let i = 0; i < 400 && __bd.busy; i++) await new Promise((r) => setTimeout(r, 50)); await new Promise((r) => setTimeout(r, 80)); };
  for (const k of ['S', 'P', 'A']) {
    const id = pick[k]; if (!id && route !== 'ui') continue;
    if (route === 'direct') S.keep(k, id);
    else if (route === 'viahold') { S.draw(k); if (id !== '*') S.hold(k, id); S.draw(k); S.draw(k); S.keep(k, id); S.reset(k); }
    else if (route === 'piles') { S.draw(k); let z = S.zones(k); S.hold(k, z.hand[1]); S.hold(k, z.hand[2]); S.keep(k, z.hand[0]); S.draw(k); S.draw(k); z = S.zones(k); S.keep(k, z.hand[3]); S.keep(k, id); z = S.zones(k); if (z.hold[0]) S.drop(k, z.hold[0]); S.reset(k); S.draw(k); }
    else if (route === 'full') { for (let i = 0; i < 6; i++) S.draw(k); S.keep(k, id); let z = S.zones(k); for (const h of z.hand.slice(0, 3)) S.hold(k, h); S.draw(k); S.reset(k); S.draw(k); }
  }
  if (route === 'ui') {          // 真在页面上点：进第八步，一池一池翻开一张、点主钮留下；头一池先把一张放进候星、再抽一手再留
    F._route = 'direct'; F._max = 11; __bd.deal(false); await idle(); __bd.go(8); await idle();
    const q = (s2) => document.querySelector('#sh-build ' + s2);
    for (const k of ['S', 'P', 'A']) {
      q('[data-a="pool"][data-v="' + k + '"]').click(); await idle();
      if (k === 'S') { document.querySelectorAll('#sh-build .bx-slots .bx-star:not(.cus)')[5].click(); await idle(); q('[data-a="shold"]').click(); await idle(); q('[data-a="draw"]').click(); await idle(); }
      document.querySelectorAll('#sh-build .bx-slots .bx-star:not(.cus)')[want[k]].click(); await idle();
      q('.bx-ctl [data-a="next"]').click(); await idle();
    }
    if (__bd.step !== 8) return { err: '点主钮留下以后不该离开第八步，到了第 ' + __bd.step + ' 步' };
  }
  const kept = { S: F.starS || '', P: F.starP || '', A: F.starA || '' };
  const z = S.zones('S');
  return { kept, cred: __bd.cred(), piles: 'S 池 候星 ' + z.hold.length + ' 落星 ' + z.gone.length + ' 台面 ' + z.hand.length };`;
const OLDRUN = (s, kept) => PRE(s) + `
  const kept = ${JSON.stringify(kept)}; for (const k of ['S', 'P', 'A']) if (kept[k]) F['star' + k] = kept[k];
  return { cred: __bd.cred(), old: !__bd.star };`;

const P = await open(1280, 800, { reduce: true, url: BASE + '?t=' + Date.now() });
await P.until('window.__tb && window.Shell', 30000); await P.ev('__tb.skip(); return 1'); await sleep(900);
const Q = await open(1280, 800, { reduce: true, url: OLD + '?t=' + Date.now() });
await Q.until('window.__tb && window.Shell', 30000); await Q.ev('__tb.skip(); return 1'); await sleep(900);
let bad = 0;
if (OUT) fs.mkdirSync(OUT, { recursive: true });
for (const s of SC) {
  await P.send('Page.bringToFront');          // 两页同开，不在前头的那一页计时器会被浏览器压慢：用哪一页先把它拿到前头
  const a = await P.ev(NEWRUN(s));
  if (!a || a.err) { bad++; console.log(s.id, '✗ 改后没跑完', a && a.err || ''); continue; }
  await Q.send('Page.bringToFront');
  const b = await Q.ev(OLDRUN(s, a.kept));
  if (!b) { bad++; console.log(s.id, '✗ 改前没跑完'); continue; }
  if (!b.old) { bad++; console.log(s.id, '✗ 对照页不是改前的外壳'); }
  const same = a.cred === b.cred, stars = (a.cred.match(/【五·命星天赋】\n([^\n]*)\n([^\n]*)/) || []).slice(1).map((l) => l.slice(0, 46)).join(' ／ ');
  if (!same) bad++;
  console.log(`${s.id}　${same ? '一样' : '不一样'}　${a.cred.length} 字　走法 ${s.route}（${a.piles}）　留下 ${JSON.stringify(a.kept)}\n      ${stars}`);
  if (OUT) { fs.writeFileSync(`${OUT}/cred_${s.id}.txt`, a.cred); if (!same) fs.writeFileSync(`${OUT}/cred_${s.id}_改前.txt`, b.cred); }
}
const errs = P.errs.concat(Q.errs.filter((e) => !/Failed to load resource/.test(e))).filter((e) => !/favicon/.test(e));          // 对照页经转发取图偶尔断一张，不算页面的错
console.log('\n' + SC.length + ' 组里不一样的', bad, '组；控制台报错', errs.length, '条'); for (const e of errs.slice(0, 6)) console.log('  ', e);
await P.close(); await Q.close();
await sleep(300); process.exitCode = bad || errs.length ? 1 : 0;
