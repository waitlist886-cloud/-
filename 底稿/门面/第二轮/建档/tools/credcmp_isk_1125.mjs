// 凭证逐字比（11-25 身穿降临者照主线开局那一回，本地干跑报告第 14 条）。 node credcmp_isk_1125.mjs [存凭证的目录]
// 先起改前的对照页：node headproxy.mjs 8783 <改前那个提交号>。本地服务 8774；无头 Chrome 的端口用 CDP_PORT 换，对照页用 OLD_BASE 换。
// 同一组选法在改后的页面和改前的对照页各出一份凭证：
//   甲组（一个字不能变）：本地之魂、转生之魂配四本书每一条主线和此刻十处起点；三种魂配自己报年份的开局（第二十二张、无字碑、空白委托）；
//                        身穿的人从一条主线切到“自己报年份”；带神亲、带命星、带赐物、各种旅印写法都轮到。
//   乙组（只许变那几行）：身穿的降临者配四本书每一条主线、此刻十处起点。逐行比：
//                        头一行、【五·命星天赋】底下两行、旅印那一行、别的行都要一样，行数也一样；
//                        只许 初始实力、这一段的本事、【面板状态】、当前处境 四行不一样，而且各照各的规矩变（见下面 judge）。
import { open, sleep, BASE } from './cdp.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const OUT = process.argv[2] || '';
const OLD = process.env.OLD_BASE || 'http://localhost:8783/' + encodeURIComponent('小样_外壳') + '/local.html';
const FRONT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const J = (p) => JSON.parse(fs.readFileSync(path.join(FRONT, p), 'utf8'));
const BOOKS = [['moon', '月银纪', '小样_月银纪书'], ['strife', '纷争纪', '小样_纷争纪书'], ['bronze', '山铜纪', '小样_山铜纪书'], ['maze', '迷宫纪', '小样_迷宫纪书']];
const LAND = J('小样_外壳/data/land.json');
const yOf = (s) => { const m = String(s == null ? '' : s).replace(/\s/g, '').match(/(\d{1,5})/); return m ? +m[1] : null; };

// 场面
const SC = []; let n = 0;
const LINES = [];
for (const [b, era, dir] of BOOKS) {
  const D = J(dir + '/data/' + b + '.json');
  for (const e of D.eras) for (const l of e.lines || []) LINES.push({ book: b, m: { book: b, era, at: e.id, title: e.title, line: l.name, year: l.year || e.years, ti: l.ti || '' } });
}
const SITES = J('小样_此刻书/data/now.json').sites.map((s) => ({ book: 'maze', m: { book: 'maze', era: '迷宫纪', at: '1001', now: 1, title: '此刻', line: '迷宫纪1001年·' + s.n, site: s.n, ti: s.t, year: '1001' } }));
const FREE = { strife: [{ book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, [1, 150, 233, 1150, 4600, 10900, 11034]],
  bronze: [{ book: 'bronze', era: '山铜纪', at: 'free', title: '无字碑', line: '', year: '' }, [2, 29, 60, 700, 947]],
  maze: [{ book: 'maze', era: '迷宫纪', at: 'free', title: '空白委托', line: '', year: '' }, [2, 5, 19, 300, 419, 420, 852, 1000]] };
// 甲组
for (const L of LINES) for (const soul of ['native', 'reborn']) SC.push({ id: 'A' + (++n), grp: 'A', what: `${L.m.era}｜${L.m.line}｜${soul}`, soul, i: n, ...L });
for (const L of SITES) for (const soul of ['native', 'reborn']) SC.push({ id: 'A' + (++n), grp: 'A', what: `此刻｜${L.m.site}｜${soul}`, soul, i: n, ...L });
for (const b of Object.keys(FREE)) for (const y of FREE[b][1]) for (const soul of ['native', 'reborn', 'isekai']) SC.push({ id: 'A' + (++n), grp: 'A', what: `${FREE[b][0].era}｜${FREE[b][0].title} ${y}年｜${soul}`, soul, i: n, book: b, m: FREE[b][0], year: y });
// 身穿的人进了一条主线，又切到“自己报年份”（页面上那一枚“自己报年份”的钮）：照自己报年份的写，不许变
for (const L of LINES.filter((x) => x.book !== 'moon').filter((x, k) => k % 9 === 0)) SC.push({ id: 'A' + (++n), grp: 'A', what: `${L.m.era}｜${L.m.line}｜身穿，切到自己报年份`, soul: 'isekai', i: n, sw: 1, year: yOf(L.m.year) || 500, ...L });
// 乙组
for (const L of LINES) SC.push({ id: 'B' + (++n), grp: 'B', what: `${L.m.era}｜${L.m.line}`, soul: 'isekai', i: n, ...L });
for (const L of SITES) SC.push({ id: 'B' + (++n), grp: 'B', what: `此刻｜${L.m.site}`, soul: 'isekai', i: n, site: 1, ...L });
// 乙组再补几种：没挑本事、没收赐物、起点最低、起点最高，头一回斩首照干跑那一份
const pick = (name) => LINES.find((x) => x.m.line === name);
for (const [name, fix] of [['黑潮的年月·头一回斩首', { tier: '共鸣·寻音', nosk: 0, gift: 0 }], ['黑潮的年月·头一回斩首', { tier: '启源·初识', nosk: 1, gift: 1 }], ['探井的年月·头一回下井', { tier: '启源·初识', nosk: 1, gift: 0 }],
  ['万兽·焚原', { tier: '传奇·撼世', nosk: 0, gift: 1 }], ['灯的年月·盾碑', { tier: '启源·初识', nosk: 1, gift: 0 }], ['犁的年月·雨城清查', { tier: '英雄·破格', nosk: 0, gift: 1 }], ['繁荣的年月·头一回实习', { tier: '灵格·塑形', nosk: 0, gift: 0 }]])
  SC.push({ id: 'B' + (++n), grp: 'B', what: `${pick(name).m.era}｜${name}｜${fix.tier}${fix.nosk ? '，没挑本事' : ''}${fix.gift ? '，带赐物' : '，不收赐物'}`, soul: 'isekai', i: n, fix, ...pick(name) });

// 页面里跑：一批场面，各填一份、各出一份凭证
const TL = ['启源·初识', '启源·凝华', '启源·临界', '共鸣·寻音', '共鸣·织理', '共鸣·破障', '灵格·塑形', '灵格·极诣', '灵格·辉耀', '极境·绝地', '极境·峙岳', '极境·凡巅', '英雄·破格', '英雄·铸史', '英雄·冠名', '传奇·撼世', '传奇·天灾', '传奇·圣座'];
const RUN = (list) => `
  const out = [], zz = (ms) => new Promise((r) => setTimeout(r, ms));
  const BUILD = await (await fetch(A('data/build.json'))).json(), TL = ${JSON.stringify(TL)};
  for (const s of ${JSON.stringify(list)}) {
    try {
      await Shell.startBuild(s.m); await zz(50);
      const F = __bd.F; for (const k of Object.keys(F)) if (!/^_/.test(k)) delete F[k];
      if (s.sw) { F.free = true; await Shell.startBuild(s.m); await zz(50); }
      const E = BUILD.eras[s.m.book], i = s.i, fx = s.fix || {};
      if (s.year != null) F.year = String(s.year);
      const y = s.year != null ? s.year : (String(s.m.year).replace(/\\s/g, '').match(/\\d+/) || [1])[0] * 1;
      const Ps = E.periods || [], per = (__bd.free ? null : Ps.find((p) => (p.eras || []).includes(s.m.at))) || Ps.find((p) => p.id !== '1001' && p.from <= y && y <= p.to) || Ps[0];
      const SK = (per.skills || []).map((x) => (typeof x === 'string' ? x : x.s));
      F.soul = s.soul; F.name = '试' + i; F.sex = ['女', '男', '自定义'][i % 3]; if (i % 3 === 2) F.sexOther = '不说'; if (i % 4) F.age = String(16 + i % 30); if (i % 5) F.height = (150 + i % 40) + 'cm'; if (i % 2) F.look = '银发，左眼角一颗痣';
      if (i % 2) F.world = '原来是城里的护士';
      const rid = (per.races || ['human'])[i % (per.races || ['human']).length]; F.race = rid; const R = (E.races || {})[rid]; if (R && R.subs && R.subs.length && i % 2) F.sub = R.subs[i % R.subs.length].name;
      F.tier = fx.tier || TL[i % TL.length]; F.statMode = i % 3 ? 'even' : 'later';
      if (s.m.book === 'moon') { F.weapon = E.weapons[i % E.weapons.length].n; if (i % 2) F.style = '蓄斩'; F.marts = E.arts[i % E.arts.length].n; F.school = E.schools[i % E.schools.length].n; }
      else { if (i % 7) F.path = i % 11 === 0 ? '*' : BUILD.paths[i % BUILD.paths.length].name; if (F.path === '*') F.pathCustom = '剑与诗'; if (i % 2) F.weapon = '长戟'; if (i % 5 === 0) F.style = '游击'; }
      if (s.soul !== 'isekai') { const gs = __bd.gods().filter((g) => !g.off); F.goldN = i % 3 === 0 ? '-' : i % 3 === 1 && gs.length ? gs[i % gs.length].n : '*'; F.goldKnow = i % 2; }
      else { const G = __bd.giftPool(); if (fx.gift != null ? fx.gift : i % 3) F.giftN = G.length ? G[i % G.length].n : ''; }
      ['S', 'P', 'A'].forEach((k, j) => { const p = __bd.pool(k); if (p.length && (i + j) % 4) F['star' + k] = p[(i * 7 + j) % p.length].id; });
      if (fx.nosk != null ? !fx.nosk : i % 4) F.skills = [SK[i % SK.length], SK[(i + 3) % SK.length]].filter((x, k2, a) => x && a.indexOf(x) === k2); if (i % 5 === 0 && !fx.nosk) F.skill2 = '想学会读术式';
      if (i % 3) F.oath = ['守序善良', '混乱中立', '中立邪恶'][i % 3]; if (i % 2) F.wishPick = '找回去的路'; else if (i % 3 === 0) F.wish = '活下去'; if (i % 6 === 0) F.extra = '想要一只狗';
      if (i % 2) F.wall = '北段'; if (i % 2) F.team = '灰鸦团'; F.grade = ['', '低档', '中档'][i % 3]; F.rank = ['', '风路', '月桂'][i % 3];
      F.sheet = { 姓或家: i % 2 ? '铁砧家' : '', 谁担保: i % 3 === 1 ? '书记' : '', 哪一家: i % 2 ? '城门边' : '', 从哪里来: i % 3 ? '雨城' : '', 户名: i % 2 ? '北街户' : '' };
      if (s.year != null && i % 2) F.place = '白碑下的酒馆';
      out.push({ id: s.id, cred: __bd.cred(), free: !!__bd.free });
    } catch (e) { out.push({ id: s.id, err: String(e && e.stack || e) }); }
  }
  return out;`;

async function runAll(url, tag) {
  const P = await open(1280, 800, { reduce: true, url: url + '?t=' + Date.now() });
  await P.until('window.__tb && window.Shell', 30000); await P.ev('__tb.skip(); return 1'); await sleep(900);
  await P.send('Page.bringToFront');
  const res = {};
  for (let k = 0; k < SC.length; k += 40) {
    const part = await P.ev(RUN(SC.slice(k, k + 40)));
    if (!part) { console.log(tag, '第', k, '批没跑完', P.errs.slice(-2)); continue; }
    for (const r of part) res[r.id] = r;
    process.stdout.write(`\r${tag} ${Math.min(k + 40, SC.length)}/${SC.length}`);
  }
  const marks = await P.ev(`const sc = [...document.scripts].map((x) => x.src).find((u) => /shell\\.js/.test(u)); const t = sc ? await (await fetch(sc)).text() : ''; return { src: sc || '', isk: /iskLand/.test(t), land: !!(await fetch(A('data/land.json')).then((r) => r.ok).catch(() => false)) }`);
  const errs = P.errs.filter((e) => !/favicon|Failed to load resource/.test(e));
  await P.close();
  process.stdout.write('\n');
  return { res, errs, marks };
}
const NEW = await runAll(BASE, '改后');
const OLDR = await runAll(OLD, '改前');

// 乙组一行一行判
const ALLOW = ['初始实力：', '这一段的本事：', '【面板状态】', '当前处境：'];
function judge(s, a, b) {          // a 改后，b 改前；回 [毛病…] 和变了的行
  const A = a.split('\n'), B = b.split('\n'), bad = [], ch = [];
  if (A.length !== B.length) return { bad: ['行数不一样 ' + B.length + '→' + A.length], ch };
  if (A[0] !== B[0]) bad.push('头一行变了');
  const y = yOf(s.m.year), panel = s.m.book === 'maze' && y >= 420, line = !s.m.site;
  for (let k = 0; k < A.length; k++) {
    if (A[k] === B[k]) continue;
    const tag = ALLOW.find((t) => B[k].startsWith(t));
    if (!tag) { bad.push('不该变的行变了：' + B[k].slice(0, 30)); continue; }
    ch.push([tag, B[k], A[k]]);
    if (tag === '初始实力：') {
      const cut = B[k].indexOf('）｜') + 2, want = B[k].slice(0, cut) + '原来的世界带来的底子，落地时原样带着，' + (panel ? '面板还没照过' : s.m.era + '还没有人见过');
      if (A[k] !== want) bad.push('初始实力那一行不是预想的样子：' + A[k]);
    } else if (tag === '这一段的本事：') {
      if (B[k].startsWith('这一段的本事：未选择')) bad.push('没挑本事的那一行也变了');
      if (A[k] !== B[k] + '（原来的世界带来的本事，照这一纪的叫法记的。这一纪的地方和人还没经过，往后想往这边长）') bad.push('本事那一行不是预想的样子：' + A[k]);
    } else if (tag === '【面板状态】') {
      if (!(panel && line)) bad.push('这一份的面板状态不该变');
      if (B[k] !== '【面板状态】尚未觉醒，开局先去公会登记、觉醒面板。' || A[k] !== '【面板状态】尚未觉醒，开局照主线一幕的地方起头，等到了有公会书记的地方再领旅印、觉醒面板。') bad.push('面板状态不是预想的样子：' + A[k]);
    } else if (tag === '当前处境：') {
      if (!line) bad.push('此刻的当前处境不该变');
      const want = (LAND.eras[s.m.book] || {})[s.m.line];
      if (!want) bad.push('land.json 里没有这一条的句子');
      if (A[k] !== B[k] + want) bad.push('当前处境不是“原句＋落点句”：' + A[k]);
    }
  }
  const has = (t) => ch.some((c) => c[0] === t);
  if (!has('初始实力：')) bad.push('初始实力那一行没换');
  if (line && !has('当前处境：')) bad.push('没接上落点句');
  if (panel && line && !has('【面板状态】')) bad.push('面板状态没换');
  if (!B.find((l) => l.startsWith('这一段的本事：')).startsWith('这一段的本事：未选择') && !has('这一段的本事：')) bad.push('挑了本事，那一行没注');
  const i5 = B.indexOf('【五·命星天赋】'); if (i5 < 0 || A[i5 + 1] !== B[i5 + 1] || A[i5 + 2] !== B[i5 + 2]) bad.push('命星那两行变了');
  const sb = B.find((l) => l.startsWith('旅印：')), sa = A.find((l) => l.startsWith('旅印：')); if (!sb || sa !== sb) bad.push('旅印那一行变了');
  if (/[；…！]|——/.test(A.filter((l, k) => l !== B[k]).join(''))) bad.push('新句子里有卡面不用的标点');
  return { bad, ch };
}

let badA = 0, badB = 0, nA = 0, nB = 0; const diffs = [], keep = [];
if (OUT) fs.mkdirSync(OUT, { recursive: true });
for (const s of SC) {
  const a = NEW.res[s.id], b = OLDR.res[s.id];
  if (!a || !b || a.err || b.err) { (s.grp === 'A' ? badA++ : badB++); console.log(s.id, s.what, '✗ 没跑完', (a && a.err) || (b && b.err) || ''); continue; }
  if (s.grp === 'A') {
    nA++;
    if (a.cred !== b.cred) { badA++; console.log(s.id, s.what, '✗ 不一样'); if (OUT) { fs.writeFileSync(`${OUT}/${s.id}_改后.txt`, a.cred); fs.writeFileSync(`${OUT}/${s.id}_改前.txt`, b.cred); } }
    if ((s.year != null) !== a.free) { badA++; console.log(s.id, s.what, '✗ 该是自己报年份的那一种，页面上不是（或者反过来）'); }
  } else {
    nB++;
    const j = judge(s, a.cred, b.cred);
    if (j.bad.length) { badB++; console.log(s.id, s.what, '✗', j.bad.join('；')); }
    diffs.push({ id: s.id, what: s.what, ch: j.ch });
    keep.push({ id: s.id, what: s.what, old: b.cred, new: a.cred });
  }
}
if (OUT) {
  fs.writeFileSync(`${OUT}/乙组_全部.json`, JSON.stringify(keep, null, 1));
  fs.writeFileSync(`${OUT}/乙组_变了的行.md`, diffs.map((d) => `### ${d.id}　${d.what}\n` + d.ch.map((c) => `- 改前　${c[1]}\n- 改后　${c[2]}`).join('\n')).join('\n\n') + '\n');
}
console.log(`\n甲组（一个字不能变）${nA} 份，不一样 ${badA} 份；乙组（身穿配主线和此刻）${nB} 份，不合规矩 ${badB} 份。`);
console.log('改后那一页', NEW.marks && NEW.marks.isk ? '是改后的外壳' : '✗ 不像改后的外壳', '；对照页', OLDR.marks && !OLDR.marks.isk ? '是改前的外壳' : '✗ 不是改前的外壳');
const errs = NEW.errs.concat(OLDR.errs);
console.log('控制台报错', errs.length, '条'); for (const e of errs.slice(0, 6)) console.log('  ', e);
await sleep(200); process.exitCode = badA || badB || errs.length || !(NEW.marks && NEW.marks.isk) || (OLDR.marks && OLDR.marks.isk) ? 1 : 0;
