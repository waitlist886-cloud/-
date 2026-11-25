// 身穿的降临者照一条主线开局，直接构筑从头走到铸印（11-25，本地干跑报告第 14 条）。 node walk_isk_1125.mjs W H 前缀 [书=maze]
// 照 walk.mjs 的走法，改了三处：第一步挑身穿那一张（第三张），金血那一步没有（第三步往下直接到第五步），第九步多点两样本事、收一件赐物。
// 走到第十一步取凭证，查那几句（落点句、初始实力、本事、面板状态、旅印）；铸印以后查确认页上那一份也带着落点句。每一步查叠字、查有没有手，末了报控制台的错。
import { open, sleep, BASE } from './cdp.mjs';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const [W, H] = [+(process.argv[2] || 1920), +(process.argv[3] || 945)];
const OUT = process.argv[4] || 'shots/isk'; const book = process.argv[5] || 'maze';
const MS = { maze: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: 852, ti: '' }, mazeold: { book: 'maze', era: '迷宫纪', at: 'q1', title: '探井的年月', line: '探井的年月·头一回下井', year: 7, ti: '' },
  bronze: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, moon: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' },
  strife: { book: 'strife', era: '纷争纪', at: 's10', title: '盾碑', line: '灯的年月·盾碑', year: 1020 },
  now: { book: 'maze', era: '迷宫纪', at: '1001', site: '阿卡迪亚·外环棚区', ti: '井口边的不眠之城', line: '迷宫纪1001年·阿卡迪亚·外环棚区', year: '1001' } };
const M = MS[book];
const LAND = JSON.parse(fs.readFileSync(path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../小样_外壳/data/land.json'), 'utf8'));
fs.mkdirSync(OUT.replace(/\/[^/]*$/, ''), { recursive: true });
const P = await open(W, H, { mobile: W < 861, url: BASE + '?t=' + Date.now() });
await P.until('window.__tb && window.Shell', 30000);
await P.ev('__tb.skip(); return 1'); await sleep(1200);
await P.ev(`await Shell.startBuild(${JSON.stringify(M)}); return 1`);
const idle = async () => { await sleep(150); await P.until('window.__bd && !__bd.busy', 12000); await sleep(250); };
const cl = (sel, i = 0) => P.ev(`const e = document.querySelectorAll(${JSON.stringify('#sh-build ' + sel)})[${i}]; if (!e) return 'no:' + ${JSON.stringify(sel)}; e.scrollIntoView({ block: 'center' }); e.click(); return 'ok'`);
const nx = () => P.ev(`document.querySelector('#sh-build .bx-ctl [data-a="next"]').click(); return 1`);
const step = () => P.ev('return __bd.step');
const OV = `const out = []; const els = []; const w = document.createTreeWalker(document.querySelector('#sh-build .bx'), NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { if (!n.nodeValue.trim()) continue; const el = n.parentElement; if (!el || el.closest('.bx-hand,.bx-say,svg,.bx-lay .bx-race .face.a')) continue; const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.opacity === '0') continue;
    const rg = document.createRange(); rg.selectNodeContents(n); for (const r of rg.getClientRects()) if (r.width > 2 && r.height > 2 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth) { const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); if (t && (t === el || el.contains(t) || t.contains(el))) els.push([r, n.nodeValue.trim().slice(0, 8), el]); } }
  for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) { const [a, ta, ea] = els[i], [b, tb, eb] = els[j]; if (ea === eb) continue;
    const x = Math.min(a.right, b.right) - Math.max(a.left, b.left), y = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top); if (x > 3 && y > 3) out.push(ta + '×' + tb); }
  return out.slice(0, 12);`;
const HANDQ = `return [...document.querySelectorAll('#sh-build img')].filter((i) => /hand/.test(i.getAttribute('src') || '')).length + document.querySelectorAll('#sh-build .bx-hand').length`;
const bad = [], say = (...a) => console.log(...a), must = (ok, what) => { if (!ok) { bad.push(what); say('✗', what); } };
const shot = async (n) => { await idle(); await P.shot(`${OUT}_${n}.jpg`); const hn = await P.ev(HANDQ); if (hn) say('有手', n, hn); const o = await P.ev(OV); if (o && o.length) say('叠字', n, JSON.stringify(o)); };
const want = async (n, tag) => { const s = await step(); must(s === n, `${tag}：该在第 ${n} 步，眼下在第 ${s} 步`); };

await sleep(2400); await shot('00gate');
await cl('[data-a="way"][data-v="direct"]'); await sleep(400); await shot('01');
must(await cl('[data-a="soul"][data-v="isekai"]') === 'ok', '第一步点不到身穿那一张'); await shot('01b');
must(await P.ev(`return __bd.F.soul`) === 'isekai', '点了以后魂不是身穿');
await nx(); await shot('02'); await want(2, '挑了身穿');
await P.ev(`const i = document.querySelector('#b2-name'); i.value = '叶澄'; i.dispatchEvent(new Event('input', { bubbles: true })); return 1`);
await cl('[data-a="sex"][data-v="女"]'); await P.ev(`const i = document.querySelector('#b2-age'); i.value = '26'; i.dispatchEvent(new Event('input', { bubbles: true })); return 1`);
await shot('02b');
await nx(); await shot('03'); await want(3, '写了名字');
say(await cl('.bx-race', 0)); await shot('03b');
say(await cl('.bx-focus .sb', 0)); await shot('03c');
await nx(); await shot('05'); await want(5, '身穿的人没有金血那一步，第三步往下该到第五步');
say(await cl('.bx-tier', 3)); await shot('05b');
await nx(); await shot('06'); await want(6, '挑了起点');
say(await cl('[data-a="stat"][data-v="roll"]')); await sleep(400); await shot('06b');
await nx(); await shot('07'); await want(7, '分了六维');
say(await cl(M.book === 'moon' ? '.bx-tag' : '.bx-emb', 9)); await shot('07b');
await nx(); await sleep(900); await shot('08'); await want(8, '挑了命路');
const faceUp = async () => { await P.until(`window.__bd && !__bd.busy && !document.querySelector('#sh-build .bx-slots .bx-star:not(.cus):not(.up)')`, 20000); await idle(); };
await faceUp();
say(await cl('.bx-slots .bx-star', 0)); await shot('08b'); await nx(); await idle();
say(await cl('[data-a="pool"][data-v="A"]')); await faceUp();
say(await cl('.bx-slots .bx-star', 1)); await shot('08c'); await nx(); await idle();
say('留下的', await P.ev(`return [__bd.F.starS, __bd.F.starA].map((x) => (x ? '有' : '没有')).join(' ') + '，还在第 ' + __bd.step + ' 步'`));
await nx(); await shot('09'); await want(9, '留了命星');
say(await cl('.bx-sk', 1), await cl('.bx-sk', 4)); await shot('09a');
say(await cl('.bx-oath', 2)); await shot('09b');
must(await cl('.bx-gift', 0) === 'ok', '第九步没有赐物可挑'); await shot('09c');
await nx(); await shot('10'); await want(10, '挑了誓心、本事和赐物');
const ui10 = await P.ev(`return document.querySelector('#sh-build .bx-body').innerText`);
say(await cl('.bx-map .pin.hot, .bx-map .pin', 0)); await shot('10b');
say(await cl('.bx-wish .bx-tag', 0));
await nx(); await shot('11'); await want(11, '落在哪那一步走完');
const cred = (await P.ev(`return __bd.cred()`)) || '';
fs.writeFileSync(`${OUT}_cred.txt`, cred);
// 凭证里那几句
const line = (t) => cred.split('\n').find((l) => l.startsWith(t)) || '', y = +String(M.year).replace(/\D/g, ''), panel = M.book === 'maze' && y >= 420;
const land = M.site ? '' : (LAND.eras[M.book] || {})[M.line];
must(/^纪元：/.test(cred), '头一行不是 纪元： 起头');
must(cred.includes('降临之魂 · 身穿（连人带身跌入）'), '凭证里不是身穿');
if (!M.site) { must(!!land, 'land.json 里没有这一条主线的句子'); must(line('当前处境：').startsWith('当前处境：刚从死之神殿落下来，身上只有穿越时那一身') && line('当前处境：').endsWith(land), '当前处境后头没接上落点句：' + line('当前处境：')); }
else must(/。$/.test(line('当前处境：')) && !/落在/.test(line('当前处境：')), '此刻的当前处境不该接落点句');
must(/｜原来的世界带来的底子，落地时原样带着，/.test(line('初始实力：')) && !/照得出|看得出的/.test(line('初始实力：')), '初始实力那一行没换：' + line('初始实力：'));
must(/（原来的世界带来的本事，照这一纪的叫法记的。/.test(line('这一段的本事：')), '本事那一行没注：' + line('这一段的本事：'));
if (panel) must(line('【面板状态】') === (M.site ? '【面板状态】尚未觉醒，开局先去公会登记、觉醒面板。' : '【面板状态】尚未觉醒，开局照主线一幕的地方起头，等到了有公会书记的地方再领旅印、觉醒面板。'), '面板状态：' + line('【面板状态】'));
must(/^神殿赐物：.+（/.test(line('神殿赐物：')), '赐物没进凭证');
must(line('旅印：').length > 3, '没有旅印那一行');
say('凭证', cred.length, '字｜', line('初始实力：'), '\n      ', line('这一段的本事：'), '\n      ', line('【面板状态】'), '\n      ', line('当前处境：'), '\n      ', line('旅印：'));
// 铸印
await nx(); await sleep(1500); await P.shot(`${OUT}_12a.jpg`); await sleep(2500); await P.shot(`${OUT}_12b.jpg`);
must(await P.until(`document.querySelector('#sh-seal.on')`, 15000), '铸印以后确认页没出来'); await sleep(800); await P.shot(`${OUT}_13.jpg`);
const sealText = (await P.ev(`const p = document.querySelector('#sh-seal .sl-paper'); return p ? p.innerText : ''`)) || '';
if (land) must(sealText.replace(/\s+/g, '').includes(land), '确认页上那一份没有落点句');
must(sealText.replace(/\s+/g, '').includes('原来的世界带来的底子'), '确认页上那一份初始实力没换');
const errs = P.errs.filter((e) => !/favicon/.test(e));
say('step', await step(), '｜对不上', bad.length, '处｜控制台报错', errs.length, '条', JSON.stringify(errs.slice(0, 12)));
await P.close();
process.exitCode = bad.length || errs.length ? 1 : 0;
