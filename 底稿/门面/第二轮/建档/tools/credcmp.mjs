// 凭证逐字比：同一组选法，改前（git HEAD 的 shell.js）和改后各出一份。 node credcmp.mjs
// shell_HEAD.js：先 git show HEAD:底稿/门面/小样_外壳/shell.js > shell_HEAD.js 存一份改前的；本地服务 8774、无头 Chrome 9371（CDP_PORT 换）
import { open, sleep, BASE } from './cdp.mjs';
import fs from 'node:fs';
const OLD = fs.readFileSync(new URL('./shell_HEAD.js', import.meta.url));
const SC = [
  { id: 'moon_line', m: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' }, f: `F.soul='isekai'; F.world='原来是城里的护士'; F.name='莉娅'; F.sex='女'; F.age='19'; F.height='165cm'; F.look='银发'; F.race='human'; F.tier='共鸣·织理'; F.statMode='even'; F.weapon=E.weapons[0].n; F.style='蓄斩'; F.marts=E.arts[0].n; F.school=E.schools[0].n; F.oath='守序善良'; F.wishPick='守住一堆火'; F.extra='想要一只狗'; F.giftN=G[0].n; F.sheet={'哪一家':'城门边'};` },
  { id: 'strife_free', m: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, f: `F.soul='native'; F.name='托尔克'; F.year='1150'; F.race='dwarf'; F.goldN=GD; F.goldKnow=1; F.tier='灵格·塑形'; F.statMode='cap'; F.path='真理'; F.weapon='长戟'; F.oath='混乱中立'; F.sheet={'姓或家':'铁砧家'}; F.wall='北段'; F.skills=SK.slice(0,2); F.skill2='想学会读术式'; F.wish='活下去';` },
  { id: 'strife_line', m: { book: 'strife', era: '纷争纪', at: 's01', title: '执式者', line: '灰的年月·执式者', year: '元年' }, f: `F.soul='reborn'; F.name='维恩'; F.race='elf'; F.goldN='-'; F.statMode='later'; F.path='*'; F.pathCustom='剑与诗'; F.oath=''; F.sheet={'哪个村':'灰村','什么行当':'抄书','父亲是谁':'书吏'};` },
  { id: 'bronze_gold', m: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, f: `F.soul='native'; F.name='诺拉'; F.race='dwarf'; F.goldN='*'; F.tier='启源·临界'; F.statMode='even'; F.path='渊垒'; F.team='灰鸦团'; F.grade='低档'; F.sheet={'姓或家':'炉脉','从哪里来':'雨城'};` },
  { id: 'bronze_free', m: { book: 'bronze', era: '山铜纪', at: 'free', title: '无字碑', line: '', year: '' }, f: `F.soul='isekai'; F.name='凯'; F.year='700'; F.race='beastkin'; F.tier='英雄·破格'; F.statMode='even'; F.path='铁律'; F.giftN=G[1].n; F.team='夜枭'; F.place='白碑下的酒馆';` },
  { id: 'maze_line', m: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' }, f: `F.soul='isekai'; F.name='艾琳'; F.race='halfling'; F.tier='共鸣·寻音'; F.statMode='even'; F.path='行猎'; F.giftN=G[G.length-1].n; F.rank='风路';` },
  { id: 'maze_free', m: { book: 'maze', era: '迷宫纪', at: 'free', title: '空白委托', line: '', year: '' }, f: `F.soul='native'; F.name='格雷'; F.year='300'; F.race='human'; F.goldN=GD; F.tier='极境·绝地'; F.statMode='even'; F.path='天平'; F.grade='中档'; F.sheet={'谁担保':'书记','姓或家':'格雷家'};` },
];
const P = await open(1280, 800, { url: BASE + '?t=' + Date.now() });
await P.until('window.__tb && window.Shell', 30000);
await P.ev('__tb.skip(); return 1'); await sleep(800);
async function creds() {
  const out = {};
  for (const s of SC) {
    await P.ev(`await Shell.startBuild(${JSON.stringify(s.m)}); return 1`); await sleep(700);
    out[s.id] = await P.ev(`const F = __bd.F, E = (await (await fetch(A('data/build.json'))).json()).eras[${JSON.stringify(s.m.book)}]; const G = __bd.giftPool(); const gs = __bd.gods().filter((g) => !g.off); const GD = gs.length ? gs[0].n : '*';
      const P = __bd.pool('P'), A2 = __bd.pool('A'); const SK = ((E.periods || [])[0] || {}).skills || [];
      for (const k of Object.keys(F)) if (!/^_/.test(k)) delete F[k];
      ${s.f}
      if (P.length) F.starP = P[3 % P.length].id; if (A2.length) F.starA = A2[5 % A2.length].id;
      return __bd.cred();`);
  }
  return out;
}
const NEW = await creds();
await P.ev(`document.getElementById('sh-build').hidden = true; return 1`);
await P.ev(`const t = ${JSON.stringify(OLD.toString())}; (0, eval)(t); return 1`); await sleep(800);
await P.ev(`await Shell.startBuild({ book: 'moon', at: 'm07', line: '万兽·焚原', year: '1690' }); return 1`); await sleep(600);
console.log('换成改前的外壳', await P.ev(`return !('mode' in __bd) && !!document.querySelector('#sh-build .b2')`) );
const OLDC = await creds();
let bad = 0;
for (const s of SC) { const same = NEW[s.id] === OLDC[s.id]; if (!same) bad++; console.log(s.id, same ? '一样' : '不一样', NEW[s.id].length); if (!same) { fs.writeFileSync('cmp_' + s.id + '_new.txt', NEW[s.id]); fs.writeFileSync('cmp_' + s.id + '_old.txt', OLDC[s.id]); } fs.writeFileSync('cred_' + s.id + '.txt', NEW[s.id]); }
console.log('不一样', bad, 'errs', JSON.stringify(P.errs.filter((e) => !/favicon/.test(e)).slice(0, 6)));
await P.close();
