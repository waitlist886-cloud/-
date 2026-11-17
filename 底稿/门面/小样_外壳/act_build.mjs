// 建档那一页单独验（11-17 第二版，十一步）：不经过书，直接叫外壳开建档，几种开局一步一步走到铸印，各出一份凭证。
//   node act_build.mjs <宽> <高> <截图前缀> [只走哪几种，逗号隔开]
// 查：每一步都走得过去（没有卡在“还没填”上），每一步截一张，页面上的字没有这张卡不用的标点和月相字，
//     凭证头一行对、新添的几行在、不过 8192 字。
// 本地服务器 front-cors（8773），无头 Chrome 默认 9335，CDP_PORT 换。
// data/stars.json 还没有的时候，设 STARS_FAKE=<假的命星池.json>，这一支拦下那个请求、拿它顶上（不往 data/ 里写）。
// REDUCE=1 照“减少动画”走，每一步查有没有还在动的东西。最后一种 maxlen 把每一格填到最长，看凭证过不过 8192（只走它就写 maxlen）。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4] || 'bd'];
const ONLY = (process.argv[5] || '').split(',').filter(Boolean);
const PORT = +(process.env.CDP_PORT || 9335);
const FAKE = process.env.STARS_FAKE ? fs.readFileSync(process.env.STARS_FAKE) : null;
const ADDR = 'http://localhost:8773/' + encodeURIComponent('小样_外壳') + '/local.html?t=' + Date.now();
const MOBILE = W < 861;
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Fetch.requestPaused') { send('Fetch.fulfillRequest', { requestId: m.params.requestId, responseCode: 200, responseHeaders: [{ name: 'Content-Type', value: 'application/json; charset=utf-8' }], body: FAKE.toString('base64') }); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result && r.result.result ? r.result.result.value : undefined; };
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 80 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
const until = async (expr, ms = 15000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (await ev(`return !!(${expr})`)) return true; await sleep(150); } return false; };
let bad = 0; const warn = [];
const want = (ok, what) => { if (!ok) bad++; console.log((ok ? '   ✓ ' : '   ✗ ') + what); };

await send('Page.enable'); await send('Runtime.enable');
if (FAKE) await send('Fetch.enable', { patterns: [{ urlPattern: '*data/stars.json*' }] });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: MOBILE });
// REDUCE=1：照“减少动画”走一遍，每一步查这一页上没有在动的东西
const REDUCE = !!process.env.REDUCE;
await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: REDUCE ? 'reduce' : 'no-preference' }] });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR });
await Promise.race([loaded, sleep(15000)]);
await until('window.__tb && window.Shell', 30000);
await ev(`__tb.skip(); return 1`); await sleep(1500);

// 页面上的小工具
const q = (s) => JSON.stringify(s);
const click = (sel) => ev(`const e = document.querySelector(${q(sel)}); if (!e) return 'no'; if (e.disabled) return 'off'; e.scrollIntoView({ block: 'center' }); e.click(); return 'ok'`);
const setv = (sel, v) => ev(`const e = document.querySelector(${q(sel)}); if (!e) return 'no'; e.value = ${q(v)}; e.dispatchEvent(new Event('input', { bubbles: true })); return 'ok'`);
const step = () => ev(`return window.__bd ? __bd.step : 0`);
const nextBtn = async () => ev(`const sheet = document.querySelector('#sh-build .b2.sheet'); const b = ${MOBILE} && !sheet ? document.querySelector('#sh-build .b2-bar [data-a="next"]') : document.querySelector('#sh-build .b2-side [data-a="next"]'); b.click(); return b.textContent`);
// 这一页上看得见的字：不许有这张卡不用的标点、月相字；冒号前头过八个字的记下来
const BAN = /——|—|；|…|！|新月|满月|月牙|月亮|月光/;
const pageText = () => ev(`const r = document.querySelector('#sh-build'); const parts = []; const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) { const el = n.parentElement; if (!el || el.closest('script,style')) continue; const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') continue; parts.push(n.nodeValue); } const ph = [...r.querySelectorAll('input,textarea')].map((x) => x.placeholder || ''); return parts.concat(ph).join('\\n')`);
function textCheck(t, where) {
  const m = String(t || '').match(BAN); if (m) { bad++; console.log('   ✗ ' + where + ' 页面上有 ' + m[0] + '：' + String(t).slice(Math.max(0, m.index - 20), m.index + 20).replace(/\n/g, ' ')); }
  for (const seg of String(t || '').split(/\n/)) { const i = seg.indexOf('：'); if (i < 0) continue; const head = seg.slice(0, i).split(/[，。、「」（）\s]/).pop(); if (head.length > 8) warn.push(where + '｜' + seg.slice(0, 40)); }
}

const CASES = [
  { id: 'moon_line', note: '月银纪主线开局、身穿带赐物、兵器与技艺', m: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' },
    p: { soul: 'isekai', world: '原来是城里的护士', name: '走查的人', sex: '女', age: '24', race: 'human', sub: 'first', tier: '启源·凝华', stat: 'roll', moon: { weapon: '大剑', style: '蓄斩', marts: '饮血', school: '熔铁炉心的炉城' }, stars: 1, oath: '中立善良', skills: 2, gift: 'first', wish: 'first', extra: '不想碰恋爱线' },
    head: '纪元：月银纪1690年｜开局时段：万兽·焚原', has: ['降临之魂 · 身穿', '来处：原来是城里的护士', '兵器：大剑（近身）｜风格：蓄斩', '法门与手艺：饮血｜学派：熔铁炉心的炉城', '职业格：大剑·蓄斩', '神殿赐物：', '旅印：无（月银纪没有旅印', '出身：城门边报家', '【六·誓心与赐物】'] },
  { id: 'strife_line', note: '纷争纪主线开局（元年）、本地、不要金血', m: { book: 'strife', era: '纷争纪', at: 's01', title: '执式者', line: '灰的年月·执式者', year: '元年' },
    p: { soul: 'native', name: '走查的人', sex: '男', age: '二十', race: 'human', tier: '启源·初识', stat: 'even', path: '渊垒', weapon: '塔盾', stars: 1, oath: '守序中立', skills: 1, sheet: 1, gold: '-', wish: 'first' },
    head: '纪元：纷争纪元年｜开局时段：执式者', has: ['本地之魂（生于此世）', '金血：无', '命路：渊垒（先行者）', '旅印：无（233年以前还没有军册）', '出身：报村报行当报父亲', '｜从哪里来 走查填的', '从这一条主线的开局起头'] },
  { id: 'strife_1150', note: '纷争纪自己报 1150 年、本地带金血、真理当先行者', m: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' },
    p: { soul: 'native', name: '走查的人', sex: '女', age: '20', year: '1150', race: 'human', sub: 'first', gold: 'first', tier: '共鸣·寻音', stat: 'even', path: '真理', weapon: '长杖', stars: 1, oath: '中立善良', skills: 2, sheet: 1, pin: 1, wish: 'first' },
    head: '纪元：纷争纪1150年｜开局时段：第二十二张｜年份：1150｜出身：黄金裔', has: ['金血：神亲 ', '金血祝颂【', '（Legend · Passive）', '命路：真理（先行者）', '职业格：长杖·奥法解析（先行者）', '出身：军册三栏（联军的书记问的）｜名字 走查的人｜姓或家 走查填的｜族 人类', '｜从哪里来 走查填的', '旅印：无（这一纪没有旅印，墙上认军册', '现在所在：纷争纪1150年，', '从自己报的那一年起头', '让墙上记住我的名字：战报上写一回'] },
  { id: 'strife_3600', note: '纷争纪自己报 3600 年、胎穿、金血神亲不挑、渊垒已有名字', m: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' },
    p: { soul: 'reborn', world: '前一世是个教书的', name: '走查的人', age: '30', year: '3600', race: 'dwarf', sub: 'first', gold: '*', tier: '灵格·塑形', stat: 'cap', path: '渊垒', weapon: '塔盾', stars: 1, oath: '守序善良', skills: 2, pin: 1 },
    head: '纪元：纷争纪3600年｜开局时段：第二十二张｜年份：3600｜出身：黄金裔', has: ['转生之魂 · 胎穿', '前一世：前一世是个教书的', '金血：黄金裔，神亲未挑', '命路：渊垒（1104年有了路册）', '职业格：塔盾·渊垒', '同阶满溢开局'] },
  { id: 'bronze_gold', note: '山铜纪主线开局、本地带金血（七神）', m: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' },
    p: { soul: 'native', name: '走查的人', sex: '女', age: '19', race: 'elf', sub: 'first', gold: 'first', know: 1, tier: '启源·初识', stat: 'even', path: '铁律', weapon: '短剑', stars: 1, skills: 1, sheet: 1 },
    head: '纪元：山铜纪2年｜开局时段：雨城清查｜出身：黄金裔', has: ['金血：神亲 ', '不知道，往后自己认出来', '命路：铁律（先行者）', '旅印：无（这一纪没有旅印，30年前后才有头一个有名字的团）'] },
  { id: 'bronze_free', note: '山铜纪自己报 700 年、身穿、拉一个团', m: { book: 'bronze', era: '山铜纪', at: 'free', title: '无字碑', line: '', year: '' },
    p: { soul: 'isekai', name: '走查的人', sex: '男', age: '33', year: '700', race: 'halforc', tier: '极境·绝地', stat: 'later', path: '摧锋', weapon: '大锤', stars: 1, gift: 'first', team: '灰帆', grade: '低档', pin: 1 },
    head: '纪元：山铜纪700年｜开局时段：无字碑｜年份：700', has: ['降临之魂 · 身穿', '六维：未分配', '命路：摧锋', '旅印：无（这一纪没有旅印）｜团 灰帆｜行会的档次 低档', '神殿赐物：'] },
  { id: 'maze_line', note: '迷宫纪前传主线开局（2 年，还没有公会）', m: { book: 'maze', era: '迷宫纪', at: 'q1', title: '探井的年月', line: '探井的年月·寻人', year: '2' },
    p: { soul: 'native', name: '走查的人', age: '17', race: 'human', sub: 'first', gold: '-', tier: '启源·初识', stat: 'even', path: '行猎', stars: 1, skills: 1 },
    head: '纪元：迷宫纪2年｜开局时段：寻人', has: ['旅印：无（3年霜降月以前还没有公会）', '这一年公会还不替人就职'] },
  { id: 'maze_switch', note: '迷宫纪前传从主线换成自己报 500 年、旅印七阶', m: { book: 'maze', era: '迷宫纪', at: 'q3', title: '繁荣的年月', line: '繁荣的年月·屠林令', year: '433' },
    p: { soul: 'native', name: '走查的人', age: '22', tofree: 1, year: '500', race: 'beastkin', sub: 'first', gold: 'first', tier: '共鸣·织理', stat: 'even', path: '诡刃', weapon: '双刃', stars: 1, pin: 1, rank: '风路' },
    head: '纪元：迷宫纪500年｜开局时段：空白委托｜年份：500｜出身：黄金裔', has: ['隔代醒', '旅印：风路', '职业格：双刃·诡刃', '【面板状态】已觉醒'] },
  { id: 'maze_grade', note: '迷宫纪前传自己报 300 年、旅印不分阶、公会的档次和担保', m: { book: 'maze', era: '迷宫纪', at: 'free', title: '空白委托', line: '', year: '' },
    p: { soul: 'reborn', name: '走查的人', age: '25', year: '300', race: 'halfling', gold: '-', tier: '共鸣·寻音', stat: 'even', path: '天平', stars: 1, skills: 1, pin: 1, grade: '低档', gua: '书记老汉斯' },
    head: '纪元：迷宫纪300年｜开局时段：空白委托｜年份：300', has: ['旅印：山铜旅印（不分阶）｜公会的档次 低档｜担保 书记老汉斯', '这一年公会还不替人就职', '【面板状态】这一年没有面板'] },
  { id: 'maze_isekai', note: '迷宫纪前传黑潮主线、身穿带遗物赐物', m: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' },
    p: { soul: 'isekai', name: '走查的人', sex: '女', age: '26', race: 'tiefling', tier: '英雄·破格', stat: 'even', path: '绝影', weapon: '短刃', stars: 1, gift: 'relic', extra: '伟业：在第三层背回过一整队人' },
    head: '纪元：迷宫纪852年｜开局时段：头一回斩首', has: ['降临之魂 · 身穿', '神殿赐物：', '遗物，原主已经不在了', '旅印：无印（未登记）', '初始实力：英雄·破格'] },
];

for (const c of CASES) {
  if (ONLY.length && !ONLY.includes(c.id)) continue;
  console.log('== ' + c.id + '　' + c.note);
  const e0 = errs.length, p = c.p;
  await ev(`await Shell.startBuild(${q(c.m)}); return 1`);
  await until(`Shell.state.build && window.__bd && __bd.step`); await sleep(400);
  // 每一回从第一步走：上一回在同一纪里留下的东西不一定对得上
  await ev(`__bd.go(1); return 1`); await sleep(200);
  const stepped = [];
  const atStep = async (n) => { const s = await step(); if (s !== n) { bad++; console.log(`   ✗ 该在第${n}步，停在第${s}步：` + (await ev(`return (document.querySelector('#sh-build .b2-err') || {}).textContent || (document.querySelector('.b2-flash') || {}).textContent || ''`))); return false; } return true; };
  const doStep = async (n, fn) => {
    if (!(await atStep(n))) return false;
    await sleep(250); await shot(`${c.id}_${String(n).padStart(2, '0')}`);
    textCheck(await pageText(), c.id + ' 第' + n + '步');
    if (REDUCE) {
      const mv = await ev(`const r = document.querySelector('#sh-build .b2'); const o = []; for (const el of [r, ...r.querySelectorAll('*')]) { const cs = getComputedStyle(el); if (cs.animationName !== 'none') o.push('动画 ' + el.className); if (cs.transitionDuration.split(',').some((d) => parseFloat(d) > 0)) o.push('过渡 ' + el.className); } return o.slice(0, 4).join('｜')`);
      if (mv) { bad++; console.log('   ✗ 第' + n + '步减少动画时还在动：' + mv); }
    }
    if (fn) await fn();
    await sleep(250); if (n !== 11) await shot(`${c.id}_${String(n).padStart(2, '0')}b`);
    stepped.push(n);
    await nextBtn(); await sleep(450);
    return true;
  };
  // 一、魂
  await doStep(1, async () => { await click(`[data-a="soul"][data-v="${p.soul}"]`); await sleep(200); if (p.world) await setv('[data-f="world"]', p.world); });
  // 二、睁眼之前
  await doStep(2, async () => {
    if (MOBILE) await ev(`const s = document.querySelector('#sh-build .b2.sheet'); if (s) s.classList.remove('sheet'); return 1`);
    if (p.tofree) { await click('[data-a="tofree"]'); await sleep(700); }
    await setv('[data-f="name"]', p.name); if (p.sex) await click(`[data-a="sex"][data-v="${p.sex}"]`); if (p.age) await setv('[data-f="age"]', p.age);
    await setv('[data-f="height"]', '170cm'); await setv('[data-f="look"]', '黑头发，左眉一道旧疤');
    if (p.year) { await setv('[data-f="year"]', p.year); await sleep(200); }
  });
  if (p.tofree) { const fr = await ev(`return __bd.free`); want(fr === true, '换成了自己报年份'); }
  // 三、胎骨
  await doStep(3, async () => {
    const r = await click(`[data-a="race"][data-v="${p.race}"]`); if (r !== 'ok') await click('[data-a="race"]:not(:disabled)');
    await sleep(250); if (p.sub) await click('[data-a="sub"]'); await sleep(200);
    await click('[data-a="pcm"][data-v="preset"]'); await sleep(200); await click('[data-a="body"]');
  });
  // 四、金血（身穿的人跳过）
  if (p.soul !== 'isekai') {
    await doStep(4, async () => {
      const live = await ev(`return __bd.gods().filter(g => !g.off).length + '/' + __bd.gods().length`); console.log('   在世的神亲 ' + live);
      if (p.gold === 'first') { await click('.b2-god:not(.off)'); await sleep(250); if (p.know) await click(`[data-a="know"][data-v="${p.know}"]`); }
      else if (p.gold) await click(`[data-a="gold"][data-v="${p.gold}"]`);
    });
  }
  // 五、起点
  await doStep(5, async () => { await click(`[data-a="tier"][data-v="${p.tier}"]`); });
  // 六、六维
  await doStep(6, async () => { if (p.stat && p.stat !== 'even') await click(`[data-a="stat"][data-v="${p.stat}"]`); });
  // 七、命路，或者兵器与技艺
  await doStep(7, async () => {
    if (c.m.book === 'moon') { const M = p.moon; await click(`[data-a="weapon"][data-v="${M.weapon}"]`); await sleep(200); await setv('[data-f="style"]', M.style); await click(`[data-a="marts"][data-v="${M.marts}"]`); await sleep(200); await click(`[data-a="school"][data-v="${M.school}"]`); }
    else { await click(`[data-a="path"][data-v="${p.path}"]`); await sleep(250); if (p.weapon) await setv('[data-f="weapon"]', p.weapon); }
  });
  // 八、命星
  await doStep(8, async () => {
    const n = await ev(`return document.querySelectorAll('[data-a="star"]').length`); console.log('   命星卡 ' + n + ' 张，池子 ' + (await ev(`return __bd.pool('P').length + ' + ' + __bd.pool('A').length`)));
    if (p.stars) { await click('[data-a="star"][data-v^="P|"]:not([data-v$="|*"])'); await sleep(200); await click('[data-a="star"][data-v^="A|"]:not([data-v$="|*"])'); }
  });
  // 九、誓心与出身
  await doStep(9, async () => {
    if (p.oath) await click(`[data-a="oath"][data-v="${p.oath}"]`);
    if (MOBILE) await ev(`const s = document.querySelector('#sh-build .b2.sheet'); if (s) s.classList.remove('sheet'); return 1`);
    for (let i = 0; i < (p.skills || 0); i++) await ev(`const b = [...document.querySelectorAll('[data-a="skill"]')].filter(x => x.getAttribute('aria-pressed') !== 'true')[0]; if (b) b.click(); return 1`);
    if (p.sheet) await ev(`for (const x of document.querySelectorAll('[data-sheet]')) if (!x.disabled) { x.value = '走查填的'; x.dispatchEvent(new Event('input', { bubbles: true })); } return 1`);
    if (p.gift) {
      const gs = await ev(`return __bd.gifts().map(g => g.n + (g.kind === 'relic' ? '·遗物' : '')).join('、')`); console.log('   赐物 ' + gs);
      if (p.gift === 'relic') { for (let i = 0; i < 6 && !(await ev(`return __bd.gifts().some(g => g.kind === 'relic')`)); i++) { await click('[data-a="regift"]'); await sleep(200); } const rn = await ev(`const g = __bd.gifts().find(g => g.kind === 'relic'); return g ? g.n : ''`); if (rn) await click(`[data-a="gift"][data-v="${rn}"]`); }
      else await click('[data-a="gift"]:not([data-v="-"])');
    }
  });
  // 十、落在哪
  await doStep(10, async () => {
    if (p.pin) await click('.b2-map .pin.hot');
    if (MOBILE) await ev(`const s = document.querySelector('#sh-build .b2.sheet'); if (s) s.classList.remove('sheet'); return 1`);
    if (p.wish) await ev(`if (!document.querySelector('[data-a="wish"].on')) document.querySelector('[data-a="wish"]').click(); return 1`);          // 同一纪上一种挑过的还亮着，再点一下就取消了
    if (MOBILE) await ev(`const s = document.querySelector('#sh-build .b2.sheet'); if (s) s.classList.remove('sheet'); return 1`);
    if (p.team) await setv('[data-f="team"]', p.team);
    if (p.grade) await click(`[data-a="grade"][data-v="${p.grade}"]`);
    if (p.gua) await setv('#b2-gua', p.gua);
    if (p.rank) await click(`[data-a="rank"][data-v="${p.rank}"]`);
  });
  // 十一、铸印
  await doStep(11, async () => { if (p.extra) await setv('[data-f="extra"]', p.extra); await sleep(700); await shot(`${c.id}_11b`); });
  const ok = await until(`Shell.state.seal`, 12000);
  want(ok, '交给她以后请离、出了确认页');
  const cred = ok ? await ev(`return document.querySelector('.sl-paper').textContent`) : '';
  fs.writeFileSync(`${OUT}_${c.id}_凭证.txt`, cred || '');
  const first = String(cred || '').split('\n')[0];
  want(first === c.head, '头一行：' + first + (first === c.head ? '' : '　（要的是 ' + c.head + '）'));
  for (const h of c.has) want(String(cred).includes(h), '有这一句：' + h);
  for (const sec of ['【一·灵魂形态】', '【二·种族胎骨】', '【三·命路倾向】', '【四·姓名容貌】', '【五·命星天赋】', '【七·现在何处】', '【八·冒险初心】']) if (!String(cred).includes(sec)) { bad++; console.log('   ✗ 少了一节 ' + sec); }
  const ban = String(cred).match(/——|；|…|！/); want(!ban, '凭证里没有这张卡不用的标点' + (ban ? '（有 ' + ban[0] + '）' : ''));
  want(cred.length > 0 && cred.length <= 8192, '字数 ' + cred.length + '（上限 8192）');
  console.log('   走过的步子 ' + stepped.join(' ') + '　确认页的钮 ' + (await ev(`return [...document.querySelectorAll('.sl-acts button')].map(b => b.textContent).join(' / ')`)));
  await shot(`${c.id}_12_确认页`);
  // 回去改：回到铸印那一步，填过的还在
  await ev(`document.querySelector('.sl-acts [data-a="edit"]').click(); return 1`); await sleep(900);
  want(await ev(`return Shell.state.build && __bd.step === 11 && __bd.F.name === ${q(p.name)}`), '回去改，落在铸印那一步，填过的还在');
  await ev(`document.querySelector('#sh-build [data-a="out"]').click(); return 1`); await sleep(900);
  const mine = errs.slice(e0); if (mine.length) console.log('   这一种的报错', mine.length, mine.slice(0, 4).join(' ｜ '));
}
// 每一格都填到最长（页上 maxlength 的上限），金血挑字最多的那一位、赐物挑字最多的那一件，看凭证会不会过 8192
if (!ONLY.length || ONLY.includes('maxlen')) {
  console.log('== maxlen　每一格都填到最长');
  for (const m of [{ book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' }]) {
    await ev(`await Shell.startBuild(${q(m)}); return 1`); await until(`Shell.state.build && window.__bd && __bd.step`); await sleep(300);
    const r = await ev(`const F = __bd.F, L = (n) => '长'.repeat(n), out = [];
      for (const soul of ['native', 'reborn', 'isekai']) {
        Object.assign(F, { soul, year: ${q(m.book === 'strife' ? '1150' : '')}, world: L(300), name: L(24), age: '二十', height: L(16), look: L(300), race2: L(60), build: L(24), pcMode: 'url', art: 'https://' + 'a'.repeat(292), face: 'https://' + 'b'.repeat(292), path: '*', pathCustom: L(300), weapon: L(16), style: L(20), starP: '*', starA: '*', scPn: L(24), scAn: L(24), scPd: L(500), scAd: L(500), oath: '中立善良', skill2: L(60), wish: L(80), extra: L(600), sex: '自定义', sexOther: L(12), place: L(40), wall: L(30), team: L(20), statMode: 'even', stats: null });
        F.sheet = {}; for (const c of ['姓或家', '谁担保', '从哪里来', '哪个村', '什么行当', '父亲是谁']) F.sheet[c] = L(40);
        const gs = __bd.gods().filter((g) => !g.off).sort((a, b) => (b.desc + b.eff + b.lim).length - (a.desc + a.eff + a.lim).length);
        F.goldN = soul !== 'isekai' && gs[0] ? gs[0].n : '';
        const gp = __bd.giftPool().sort((a, b) => ((b.d || '') + (b.e || '') + (b.note || '')).length - ((a.d || '') + (a.e || '') + (a.note || '')).length);
        F.giftN = soul === 'isekai' && gp[0] ? gp[0].n : '';
        out.push(soul + ' ' + __bd.cred().length);
      }
      return out.join('，')`);
    const n = Math.max(...String(r || '').split('，').map((x) => +x.split(' ')[1] || 0));
    want(n > 0 && n <= 8192, m.era + ' 最长的凭证 ' + r + '（上限 8192）');
  }
}
console.log('\n对不上的', bad, '处；报错', errs.length, '条；冒号前头过八个字的', warn.length, '处');
for (const x of errs.slice(0, 20)) console.log('  ', x);
for (const x of [...new Set(warn)].slice(0, 20)) console.log('   冒号', x);
ws.close(); process.exit(bad ? 1 : 0);
