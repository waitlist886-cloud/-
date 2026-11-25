// 命星池的落星（废卡）和候星（预选）测逻辑（11-25）： node starpile.mjs [每池抽几回=400]
// 本地服务 8774、无头 Chrome 9371（CDP_PORT 换）。拿真的 stars.json，几纪几个年份各跑一遍，三池各连抽几百回，中间随手留、放进候星、撤下、归叠。
// 查：抽到的只从星叠里出（不是落星、候星、留下的，也不是上一手）；上一手没留的都进落星；再抽不动候星和留下的；候星至多三颗；
//     撤下的进落星；换留下的那一颗原先那颗不丢；落星归叠只清落星，候星、留下的、台面不动；星叠抽空了回 0、不报错、不动牌。
// 另查：进第八步自己发一手；自己报的年份改了，落星清掉、候星里还在新池子里的照留；池子（按年份取最新版、按种族挡）跟改前的外壳逐颗一样（要先起 headproxy.mjs）。
import { open, sleep, BASE } from './cdp.mjs';
const N = +(process.argv[2] || 400);
const OLD = process.env.OLD_BASE || 'http://localhost:8779/' + encodeURIComponent('小样_外壳') + '/local.html';
const SC = [
  { id: '月银纪 1690 年', m: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' }, f: `F.race='human';` },
  { id: '纷争纪 1150 年 矮人', m: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, f: `F.year='1150'; F.race='dwarf';` },
  { id: '纷争纪 10900 年 魔族', m: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, f: `F.year='10900'; F.race='demon';` },
  { id: '山铜纪 2 年', m: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, f: `F.race='elf';` },
  { id: '山铜纪 700 年 兽人', m: { book: 'bronze', era: '山铜纪', at: 'free', title: '无字碑', line: '', year: '' }, f: `F.year='700'; F.race='beastkin';` },
  { id: '迷宫纪 300 年', m: { book: 'maze', era: '迷宫纪', at: 'free', title: '空白委托', line: '', year: '' }, f: `F.year='300'; F.race='human';` },
  { id: '迷宫纪 852 年 魔裔', m: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' }, f: `F.race='tiefling';` },
  { id: '此刻 1001 年', m: { book: 'maze', era: '迷宫纪', at: '1001', site: '阿卡迪亚·外环棚区', ti: '井口边的不眠之城', line: '迷宫纪1001年·阿卡迪亚·外环棚区', year: '1001' }, f: `F.race='';` },
];
const SETUP = (s) => `await Shell.startBuild(${JSON.stringify(s.m)}); const F = __bd.F; for (const k of Object.keys(F)) if (!/^_/.test(k)) delete F[k]; F._route = 'direct'; F.soul = 'native'; F.name = '测'; F.tier = '启源·凝华'; F.statMode = 'even'; ${s.f}`;
const LOGIC = `
const S = __bd.star, F = __bd.F, out = { bad: [], log: [] };
const eq = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
const has = (arr, x) => arr.indexOf(x) >= 0;
const chk = (c, m) => { if (!c && out.bad.length < 40) out.bad.push(m); };
const rnd = (a) => a[Math.floor(Math.random() * a.length)];
function inv(k, tag) {          // 各处不重，合起来正好是整个池子，候星不过三颗
  const z = S.zones(k), all = z.hand.concat(z.hold, z.gone, z.deck), off = z.kept && z.kept !== '*' && !has(z.hand, z.kept) ? [z.kept] : [];
  const u = new Set(all.concat(off));
  chk(u.size === all.length + off.length, tag + ' 有牌同时在两处');
  chk(u.size === z.pool.length && z.pool.every((id) => u.has(id)), tag + ' 各处合起来不是整个池子 ' + u.size + '/' + z.pool.length);
  chk(z.hold.length <= 3, tag + ' 候星过了三颗');
  return z;
}
for (const k of ['S', 'P', 'A']) {
  delete F['draw' + k]; F['star' + k] = '';
  inv(k, k + ' 开头');
  let draws = 0, dry = 0, resets = 0, holds = 0, fulls = 0, drops = 0, keeps = 0, swaps = { table: 0, hold: 0, back: 0 };
  for (let i = 0; i < ${N}; i++) {
    const b = S.zones(k), n = S.draw(k), a = inv(k, k + ' 第' + i + '抽');
    if (n === 0) {          // 星叠空了
      dry++;
      chk(b.deck.length === 0, k + ' 星叠里还有牌却没抽');
      chk(eq(a.hand, b.hand) && eq(a.gone, b.gone) && eq(a.hold, b.hold) && a.kept === b.kept && a.n === b.n, k + ' 抽空的时候动了牌');
      if (dry % 3 === 1) { for (let j = 0; j < 5; j++) S.draw(k); const c0 = inv(k, k + ' 空着连抽'); chk(eq(c0.hand, b.hand) && eq(c0.gone, b.gone), k + ' 空着连抽动了牌'); }
      const r = S.reset(k), c = inv(k, k + ' 归叠'); resets++;
      chk(r === b.gone.length && c.gone.length === 0, k + ' 归叠以后落星还有牌');
      chk(eq(c.hold, b.hold) && c.kept === b.kept && eq(c.hand, b.hand), k + ' 归叠动了留下的、候星或台面');
      chk(c.deck.length === b.deck.length + b.gone.length && b.gone.every((id) => has(c.deck, id)), k + ' 落星没都回到星叠');
      continue;
    }
    draws++;
    chk(n === a.hand.length && n === Math.min(10, b.deck.length), k + ' 抽到的张数不对 ' + n);
    for (const id of a.hand) chk(has(b.deck, id), k + ' 抽到了不在星叠里的 ' + id + (has(b.gone, id) ? '（落星）' : has(b.hold, id) ? '（候星）' : id === b.kept ? '（留下的）' : has(b.hand, id) ? '（上一手）' : ''));
    for (const id of b.hand) if (id !== b.kept) chk(has(a.gone, id), k + ' 上一手没留的没进落星 ' + id);
    for (const id of b.gone) chk(has(a.gone, id), k + ' 落星里的牌不见了');
    chk(a.gone.length === b.gone.length + b.hand.filter((id) => id !== b.kept).length, k + ' 落星的数不对');
    chk(eq(a.hold, b.hold), k + ' 再抽动了候星'); chk(a.kept === b.kept, k + ' 再抽动了留下的');
    const act = Math.random(), free = a.hand.filter((x) => x !== a.kept);
    if (act < 0.3 && free.length) {          // 放进候星
      const id = rnd(free), r = S.hold(k, id), c = inv(k, k + ' 放进候星');
      if (a.hold.length >= 3) { fulls++; chk(r === 'full' && eq(c.hold, a.hold) && eq(c.hand, a.hand), k + ' 候星满了还放得进'); }
      else { holds++; chk(r === 'ok' && has(c.hold, id) && !has(c.hand, id) && c.kept === a.kept, k + ' 没放进候星'); }
    } else if (act < 0.42 && a.hold.length) {          // 撤下候星
      const id = rnd(a.hold), r = S.drop(k, id), c = inv(k, k + ' 撤下'); drops++;
      chk(r === 'gone' && has(c.gone, id) && !has(c.hold, id), k + ' 撤下的没进落星');
    } else if (act < 0.62 && free.length) {          // 留下台面上的一颗
      const id = rnd(free), went = S.keep(k, id), c = inv(k, k + ' 留下'), o = a.kept; keeps++;
      chk(c.kept === id && has(c.hand, id), k + ' 没留下');
      if (o && o !== '*') {
        if (has(a.hand, o)) chk(went === 'table' && has(c.hand, o), k + ' 原先那颗在台面上，该留在台面上');
        else if (a.hold.length < 3) chk(went === 'hold' && has(c.hold, o), k + ' 原先那颗该压进候星');
        else chk(went === 'back' && has(c.hand, o), k + ' 候星满了，原先那颗该放回台面');
        chk(!has(c.gone, o) && !has(c.deck, o), k + ' 换留下的时候原先那颗丢了');
        swaps[went] = (swaps[went] || 0) + 1;
      }
      if (free.length > 1 && Math.random() < 0.5) { const id2 = rnd(free.filter((x) => x !== id)), w2 = S.keep(k, id2), c2 = inv(k, k + ' 同一手再留一颗'); chk(w2 === 'table' && c2.kept === id2 && has(c2.hand, id) && !has(c2.gone, id), k + ' 同一手换留，原先那颗该留在台面上'); swaps.table++; }
    } else if (act < 0.72 && a.hold.length) {          // 从候星里留
      const id = rnd(a.hold), o = a.kept; S.keep(k, id); const c = inv(k, k + ' 候星里留'); keeps++;
      chk(c.kept === id && !has(c.hold, id), k + ' 候星里的没留下');
      if (o && o !== '*') chk(has(c.hand, o) || has(c.hold, o), k + ' 从候星里留，原先那颗丢了');
    } else if (act < 0.77 && a.kept) {          // 不留了
      const o = a.kept, on = has(a.hand, o), r = S.drop(k, o), c = inv(k, k + ' 不留');
      chk(c.kept === '' && (on ? r === 'table' && has(c.hand, o) : r === 'gone' && has(c.gone, o)), k + ' 不留了以后去处不对');
    } else if (act < 0.8) {          // 半路归叠
      const b2 = S.zones(k), r = S.reset(k), c = inv(k, k + ' 半路归叠'); resets++;
      chk(r === b2.gone.length && c.gone.length === 0 && eq(c.hold, b2.hold) && c.kept === b2.kept && eq(c.hand, b2.hand), k + ' 半路归叠动了别的');
    }
  }
  out.log.push(k + ' 池子 ' + S.zones(k).pool.length + '｜抽 ' + draws + ' 回，抽空 ' + dry + ' 回，归叠 ' + resets + ' 回，放进候星 ' + holds + '（满了挡回 ' + fulls + '），撤下 ' + drops + '，留下 ' + keeps + '（原先那颗留台面 ' + swaps.table + '、进候星 ' + swaps.hold + '、放回台面 ' + swaps.back + '）');
  delete F['draw' + k]; F['star' + k] = '';
}
return out;`;
// 进第八步自己发一手；留一颗、候两颗、抽几手以后把年份改掉，落星清空、候星和留下的只剩新池子里还有的
const IDLE = `const idle = async () => { await new Promise((r) => setTimeout(r, 60)); for (let i = 0; i < 300 && __bd.busy; i++) await new Promise((r) => setTimeout(r, 50)); await new Promise((r) => setTimeout(r, 60)); };`;
const STEP8 = IDLE + `
const S = __bd.star, F = __bd.F, out = [];
__bd.deal(false); F._max = 11; await idle(); __bd.go(8); await idle();
if (__bd.step !== 8) out.push('没走到第八步，停在 ' + __bd.mode + ' ' + __bd.step);
for (const k of ['S', 'P', 'A']) { const z = S.zones(k); if (z.pool.length && (z.hand.length !== Math.min(10, z.pool.length) || z.gone.length || z.n !== 1)) out.push(k + ' 进第八步没发好头一手 ' + z.hand.length + '/' + z.n); }
const z0 = S.zones('S'); S.keep('S', z0.hand[0]); S.hold('S', z0.hand[1]); S.hold('S', z0.hand[2]); S.draw('S'); S.draw('S');
const z1 = S.zones('S'); if (z1.gone.length !== 7 + 10 || z1.hold.length !== 2 || z1.kept !== z0.hand[0]) out.push('留一候二抽两手以后的账不对 ' + JSON.stringify([z1.gone.length, z1.hold.length]));
__bd.go(7); await idle(); __bd.go(8); await idle();
const z2 = S.zones('S'); if (z2.gone.length !== z1.gone.length || z2.hand.join() !== z1.hand.join()) out.push('回到第八步不该重发');
return out;`;
const YEAR = (y) => IDLE + `
const S = __bd.star, F = __bd.F, out = [];
const z1 = S.zones('S'); F.year = '${y}'; await idle(); __bd.go(2); await idle(); __bd.go(8); await idle();
if (__bd.step !== 8) out.push('没走到第八步');
const z3 = S.zones('S'), np = new Set(z3.pool);
if (z3.gone.length) out.push('换了年份落星没清 ' + z3.gone.length);
if (z3.hand.length !== Math.min(10, z3.deck.length + z3.hand.length)) out.push('换了年份没重发一手');
if (z3.hold.join() !== z1.hold.filter((id) => np.has(id)).join()) out.push('换了年份候星不对');
if (z3.kept !== (np.has(z1.kept) ? z1.kept : '')) out.push('换了年份留下的不对');
return out.concat(['（年份 ${y}：池子 ' + z1.pool.length + ' 到 ' + z3.pool.length + '，候星 ' + z1.hold.length + ' 到 ' + z3.hold.length + '）']);`;
const POOL = `const o = {}; for (const k of ['S', 'P', 'A']) o[k] = __bd.pool(k).map((t) => [t.id, t.name, t.type, t.tier, t.note].join('|')); return o;`;

// 一回只开一页：两页同开，不在前头的那一页计时器会被浏览器压慢（一秒一跳，久了一分钟一跳），看着像卡死
const P = await open(1280, 800, { reduce: true, url: BASE + '?t=' + Date.now() });          // 照“减少动画”开，翻牌不等
await P.send('Page.bringToFront');
await P.until('window.__tb && window.Shell', 30000); await P.ev('__tb.skip(); return 1'); await sleep(900);
let bad = 0; const pools = {};
for (const s of SC) {
  console.log('== ' + s.id);
  await P.ev(SETUP(s) + ' return 1'); await sleep(300);
  pools[s.id] = await P.ev(POOL);
  const r = await P.ev(LOGIC);
  if (!r) { bad++; console.log('   ✗ 脚本没跑完'); continue; }
  for (const l of r.log) console.log('   ' + l);
  for (const b of r.bad) { bad++; console.log('   ✗ ' + b); }
  if (!r.bad.length) console.log('   ✓ 三池的账都对');
  const e8 = await P.ev(STEP8) || ['脚本没跑完'];
  for (const b of e8) { bad++; console.log('   ✗ ' + b); }
  if (!e8.length) console.log('   ✓ 进第八步发头一手，回来不重发');
  if (s.m.at === 'free') {
    const y2 = { strife: s.f.includes('10900') ? '300' : '9500', bronze: '100', maze: '900' }[s.m.book];
    const ey = await P.ev(YEAR(y2)) || ['脚本没跑完'];
    const note = ey.filter((x) => x.startsWith('（')).join(''), errs = ey.filter((x) => !x.startsWith('（'));
    for (const b of errs) { bad++; console.log('   ✗ ' + b); }
    if (!errs.length) console.log('   ✓ 改了年份：落星清掉、重发一手，候星和留下的只留新池子里还有的 ' + note);
  }
}
const errs = P.errs.filter((e) => !/favicon/.test(e));
await P.close();
// 池子跟改前的外壳逐颗比（按年份取最新版、后世的 Special 不提前出现、按种族挡，这几样都在池子里）
let okOld = false;
try { okOld = (await fetch(OLD, { signal: AbortSignal.timeout(3000) })).ok; } catch (e) {}
if (!okOld) console.log('\n（改前的对照页没起，池子逐颗比这一项跳过：先 node headproxy.mjs）');
else {
  console.log('\n== 池子跟改前逐颗比');
  const Q = await open(1280, 800, { reduce: true, url: OLD + '?t=' + Date.now() });
  await Q.send('Page.bringToFront');
  await Q.until('window.__tb && window.Shell', 30000); await Q.ev('__tb.skip(); return 1'); await sleep(900);
  if (await Q.ev('return !!(window.__bd && __bd.star)')) { bad++; console.log('   ✗ 对照页不是改前的外壳'); }
  for (const s of SC) {
    await Q.ev(SETUP(s) + ' return 1'); await sleep(300);
    const a = pools[s.id], b = await Q.ev(POOL);
    const same = a && b && ['S', 'P', 'A'].every((k) => a[k].length === b[k].length && a[k].every((x, i) => x === b[k][i]));
    if (!same) bad++;
    console.log((same ? '   ✓ ' : '   ✗ ') + s.id + '　' + (same ? '一样' : '不一样') + (a ? '（S ' + a.S.length + '、P ' + a.P.length + '、A ' + a.A.length + '）' : ''));
  }
  await Q.close();
}
console.log('\n对不上的', bad, '处；控制台报错', errs.length, '条'); for (const e of errs.slice(0, 8)) console.log('  ', e);
await sleep(300); process.exitCode = bad || errs.length ? 1 : 0;
