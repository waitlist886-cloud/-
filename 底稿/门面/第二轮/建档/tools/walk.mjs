// 直接构筑走一遍：每一步点一样，截一张。 node walk.mjs W H 前缀 书
import { open, sleep, BASE } from './cdp.mjs';
import fs from 'node:fs';
const [W, H] = [+(process.argv[2] || 1920), +(process.argv[3] || 945)];
const OUT = process.argv[4] || 'shots/w'; const book = process.argv[5] || 'bronze';
const MS = { bronze: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, moon: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' },
  strife: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, maze: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' },
  now: { book: 'maze', era: '迷宫纪', at: '1001', site: '阿卡迪亚·外环棚区', ti: '井口边的不眠之城', line: '迷宫纪1001年·阿卡迪亚·外环棚区', year: '1001' } };
const M = MS[book];
fs.mkdirSync(OUT.replace(/\/[^/]*$/, ''), { recursive: true });
const P = await open(W, H, { mobile: W < 861, url: BASE + '?t=' + Date.now() });
await P.until('window.__tb && window.Shell', 30000);
await P.ev('__tb.skip(); return 1'); await sleep(1200);
await P.ev(`await Shell.startBuild(${JSON.stringify(M)}); return 1`);
const idle = async () => { await sleep(150); await P.until('window.__bd && !__bd.busy', 12000); await sleep(250); };
const cl = (sel, i = 0) => P.ev(`const e = document.querySelectorAll(${JSON.stringify('#sh-build ' + sel)})[${i}]; if (!e) return 'no:' + ${JSON.stringify(sel)}; e.scrollIntoView({ block: 'center' }); e.click(); return 'ok'`);
const nx = () => P.ev(`document.querySelector('#sh-build .bx-ctl [data-a="next"]').click(); return 1`);
const OV = `const out = []; const els = []; const w = document.createTreeWalker(document.querySelector('#sh-build .bx'), NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { if (!n.nodeValue.trim()) continue; const el = n.parentElement; if (!el || el.closest('.bx-hand,.bx-say,svg,.bx-lay .bx-race .face.a')) continue; const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.opacity === '0') continue;
    const rg = document.createRange(); rg.selectNodeContents(n); for (const r of rg.getClientRects()) if (r.width > 2 && r.height > 2 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth) { const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); if (t && (t === el || el.contains(t) || t.contains(el))) els.push([r, n.nodeValue.trim().slice(0, 8), el]); } }
  for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) { const [a, ta, ea] = els[i], [b, tb, eb] = els[j]; if (ea === eb) continue;
    const x = Math.min(a.right, b.right) - Math.max(a.left, b.left), y = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top); if (x > 3 && y > 3) out.push(ta + '×' + tb); }
  return out.slice(0, 12);`;
const HANDQ = `return [...document.querySelectorAll('#sh-build img')].filter((i) => /hand/.test(i.getAttribute('src') || '')).length + document.querySelectorAll('#sh-build .bx-hand').length`;
const shot = async (n) => { await idle(); await P.shot(`${OUT}_${n}.jpg`); const hn = await P.ev(HANDQ); if (hn) console.log('有手', n, hn); const o = await P.ev(OV); if (o && o.length) console.log('叠字', n, JSON.stringify(o)); };
await sleep(2400); await shot('00gate');
await cl('[data-a="way"][data-v="direct"]'); await sleep(400); await shot('01');
console.log(await cl('.bx-soul', 0)); await shot('01b');
await nx(); await shot('02');
await P.ev(`const i = document.querySelector('#b2-name'); i.value = '诺拉'; i.dispatchEvent(new Event('input', { bubbles: true })); return 1`);
if (M.at === 'free') await P.ev(`const i = document.querySelector('#b2-year'); i.value = '1150'; i.dispatchEvent(new Event('input', { bubbles: true })); return 1`);
await cl('[data-a="sex"][data-v="女"]'); await P.ev(`const i = document.querySelector('#b2-age'); i.value = '18'; i.dispatchEvent(new Event('input', { bubbles: true })); return 1`);
await shot('02b');
await nx(); await shot('03');
console.log(await cl('.bx-race', 2)); await shot('03b');
console.log(await cl('.bx-focus .sb', 0)); await shot('03c');
await nx(); await shot('04');
console.log(await cl('.bx-god:not(.off)', 1)); await shot('04b');
await nx(); await shot('05');
console.log(await cl('.bx-tier', 3)); await shot('05b');
await nx(); await shot('06');
// 拖一角
const pt = await P.ev(`const g = document.querySelector('.bx-chart .hd[data-k="STR"]'); const r = g.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]`);
if (pt) { await P.drag(pt[0], pt[1], pt[0], pt[1] - 60); }
await shot('06b');
console.log(await cl('[data-a="stat"][data-v="roll"]')); await sleep(400); await P.shot(`${OUT}_06c.jpg`); await shot('06d');
await nx(); await shot('07');
console.log(await cl(M.book === 'moon' ? '.bx-tag' : '.bx-emb', 4)); await shot('07b');
await nx(); await sleep(900); await P.shot(`${OUT}_08a.jpg`); await shot('08');
console.log(await cl('.bx-slots .bx-star', 0)); await shot('08b');
console.log(await cl('[data-a="pool"][data-v="A"]')); await shot('08c');
console.log(await cl('.bx-slots .bx-star', 1)); await shot('08d');
await nx(); await shot('09');
console.log(await cl('.bx-oath', 3)); await shot('09b');
await nx(); await shot('10');
console.log(await cl('.bx-map .pin.hot, .bx-map .pin', 0)); await shot('10b');
console.log(await cl('.bx-wish .bx-tag', 0));
await nx(); await shot('11');
const cred = await P.ev(`return __bd.cred()`);
fs.writeFileSync(`${OUT}_cred.txt`, cred || '');
await nx(); await sleep(1500); await P.shot(`${OUT}_12a.jpg`); await sleep(2500); await P.shot(`${OUT}_12b.jpg`);
await P.until(`document.querySelector('#sh-seal.on')`, 15000); await sleep(800); await P.shot(`${OUT}_13.jpg`);
console.log('step', await P.ev('return __bd.step'), 'errs', JSON.stringify(P.errs.filter((e) => !/favicon/.test(e)).slice(0, 12)));
await P.close();
