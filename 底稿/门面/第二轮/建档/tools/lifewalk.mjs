// 走一遍前半生：一页挑一样，终章写名字，去抽命星，铸印。 node lifewalk.mjs W H 前缀 书
import { open, sleep, BASE } from './cdp.mjs';
import fs from 'node:fs';
const [W, H] = [+(process.argv[2] || 1920), +(process.argv[3] || 945)];
const OUT = process.argv[4] || 'shots/l'; const book = process.argv[5] || 'moon';
const MS = { bronze: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, moon: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' },
  strife: { book: 'strife', era: '纷争纪', at: 'free', title: '第二十二张', line: '', year: '' }, maze: { book: 'maze', era: '迷宫纪', at: 'q5', title: '黑潮的年月', line: '黑潮的年月·头一回斩首', year: '852' },
  now: { book: 'maze', era: '迷宫纪', at: '1001', site: '阿卡迪亚·外环棚区', ti: '井口边的不眠之城', line: '迷宫纪1001年·阿卡迪亚·外环棚区', year: '1001' } };
const M = MS[book];
fs.mkdirSync('shots', { recursive: true });
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
await sleep(2400);
await cl('[data-a="way"][data-v="life"]'); await shot('00');
const L = await P.ev('return __bd.lifeList()');
console.log(L.join(' '));
for (let i = 0; i < L.length - 1; i++) {
  const k = L[i];
  if (k === 'year') { await P.ev(`const i = document.querySelector('#b2-year'); i.value = '3600'; i.dispatchEvent(new Event('input', { bubbles: true })); return 1`); }
  else if (k === 'bones') { console.log(k, await cl('.bx-race', 0)); await idle(); console.log(await cl('.bx-focus .sb', 1)); }
  else if (k === 'path') { console.log(k, await cl(M.book === 'moon' ? '.bx-tag' : '.bx-emb', 2)); }
  else { console.log(k, await cl('.bx-lopt', i % 3)); }
  await shot(String(i + 1).padStart(2, '0') + k);
  await nx(); await idle();
}
await shot('end');
await P.ev(`const i = document.querySelector('#b2-name'); i.value = '莉娅'; i.dispatchEvent(new Event('input', { bubbles: true })); return 1`);
await shot('end2');
const F = await P.ev('return JSON.stringify(__bd.F)');
await nx(); await shot('star');
console.log('step', await P.ev('return __bd.step'), 'mode', await P.ev('return __bd.mode'));
fs.writeFileSync(`${OUT}_F.json`, F);
fs.writeFileSync(`${OUT}_cred.txt`, await P.ev('return __bd.cred()') || '');
console.log('errs', JSON.stringify(P.errs.filter((e) => !/favicon/.test(e)).slice(0, 12)));
await P.close();
