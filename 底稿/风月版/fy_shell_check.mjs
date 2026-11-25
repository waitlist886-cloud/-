// 风月外壳的规则回归（11-25，照 tools/rili_bench/check_fy.mjs 的路子）。fy_shell.py 写一份 dump（风月规则、改成这一张卡以后的日里写法、日里原样的规则），这里拿样本逐条比：
//   甲、转法：风月只认 g 的规则跟同一份日里写法（带 m、不带 g）逐条回复比，显示、存库、存了再显示、流式切刀四路，要一字不差。
//   乙、改法：这一张卡的日里写法跟日里原样的规则比（只拿这一纪的样本）。除了平台差别（<style>、大写变量、点击属性、钟点记号、主角立绘挂的属性、字眼拆回这一纪）要一字不差。
// 用法：node fy_shell_check.mjs <dump.json> <样本文件…>      样本文件名前头带 @ 的只跑甲（别纪的样本、旧 HTML）
import fs from 'node:fs';
import path from 'node:path';

const [dumpFile, ...inputs] = process.argv.slice(2);
const D = JSON.parse(fs.readFileSync(dumpFile, 'utf8'));
let bad = 0;
const fyc = D.fy.map((r) => { try { return { re: new RegExp(r.match_regex, 'g'), rep: r.replace_text, only: r.is_only_render === true, title: r.title }; } catch (e) { bad++; console.log('编不过', r.title, e.message); return null; } }).filter(Boolean);
const rl = (list) => list.map((r) => { const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/); return { re: new RegExp(m[1], m[2]), rep: r.replaceString, mode: r.applyMode, name: r.name }; });
const ref = rl(D.ref.convert.concat(D.ref.frame));
const orig = rl(D.orig);
const runFy = (t, o) => { for (const r of fyc) { if (o === 'persist' && r.only) continue; if (o === 'renderOnly' && !r.only) continue; t = t.replace(r.re, r.rep); } return t; };
const run = (rules, t, side) => { for (const r of rules) if (r.mode === 'all' || r.mode === side) t = t.replace(r.re, r.rep); return t; };
const runAll = (rules, t) => { for (const r of rules) if (r.mode === 'all') t = t.replace(r.re, r.rep); for (const r of rules) if (r.mode === 'all' || r.mode === 'front-end') t = t.replace(r.re, r.rep); return t; };
// 乙：日里原样的结果换成这一张卡该有的样子
const UP = new RegExp('(?<![\\w-])--(' + D.names.join('|') + ')(?![\\w-])', 'g');
const LWRE = /<span class="lw"><span class="w0">([^<]*)<\/span><span class="wm">([^<]*)<\/span><span class="ws">([^<]*)<\/span><span class="wb">([^<]*)<\/span><\/span>/g;
const normO = (t) => t
  .replace(/<style>[\s\S]*?<\/style>/g, '')
  .replace(UP, (m, a) => '--' + a.toUpperCase())
  .replace(/ data-action="set-textinput" data-value="[^"]*"/g, '')
  .replace(LWRE, (...g) => g[D.lw]);
const normA = (t) => t
  .replace(/<i class="sz-hh" data-h="[^"]*"><\/i>/g, '')
  .replace(/ data-pc="[^"]*"/g, '')
  .replace(/ data-pcu="1" style="--U[^"]*"/g, '');
const MARK = /[ⒽⓁⓃⓅⒸⓎⓆⓔⓩ]/;
const firstDiff = (a, b, x, y) => { let i = 0; while (i < a.length && a[i] === b[i]) i++; return `@${i} ${x}「${a.slice(Math.max(0, i - 50), i + 70)}」 ${y}「${b.slice(Math.max(0, i - 50), i + 70)}」`; };
let cuts = 0, maxMs = 0, maxFile = '', nA = 0, nB = 0, leak = 0, nSkip = 0;
for (let f of inputs) {
  const onlyA = f.startsWith('@');
  if (onlyA) f = f.slice(1);
  const src = fs.readFileSync(f, 'utf8').split('\r').join('');
  const name = path.basename(f);
  nA++;
  const t0 = performance.now();
  const a = runFy(src, 'renderOnly');
  const ms = performance.now() - t0;
  if (ms > maxMs) { maxMs = ms; maxFile = name; }
  const b = run(ref, src, 'front-end');
  if (a !== b) { bad++; console.log('甲 显示不一样', name, firstDiff(a, b, '风月', '日里写法')); }
  if (/§(?:底座|面板|角色|记忆|见闻|物品|能力|伟业|装备)｜/.test(a) || /[ⓔⓩⓟⓛⓚⓜⓝⓠⓨⓑⓓⓖⓡⓙⓐⓒⓦⓧ]/.test(a)) { leak++; console.log('甲 展开以后还剩记录或记号', name, (a.match(/.{0,30}(?:§(?:底座|面板|角色|记忆|见闻|物品|能力|伟业|装备)｜|[ⓔⓩⓟⓛⓚⓜⓝⓠⓨⓑⓓⓖⓡⓙⓐⓒⓦⓧ]).{0,30}/) || [''])[0].replace(/\n/g, '⏎')); }
  if (/<style|data-action|<link/.test(a)) { bad++; console.log('甲 展开出来有平台会拿掉的东西', name); }
  const p = runFy(src, 'persist');
  const q = run(ref, src, 'back-end');
  if (p !== q) { bad++; console.log('甲 存库不一样', name, firstDiff(p, q, '风月', '日里写法')); }
  if (MARK.test(p)) { bad++; console.log('甲 存库露记号', name, p.match(/.{0,20}[ⒽⓁⓃⓅⒸⓎⓆⓔⓩ].{0,20}/)[0]); }
  const a2 = runFy(p, 'renderOnly'), b2 = run(ref, q, 'front-end');
  if (a2 !== b2) { bad++; console.log('甲 存了再显示不一样', name, firstDiff(a2, b2, '风月', '日里写法')); }
  for (let n = 80; n < src.length; n += 211) {
    const cut = src.slice(0, n);
    let c, d;
    try { c = runFy(cut, 'all'); } catch (e) { bad++; console.log('甲 流式抛错', name, n, e.message); break; }
    d = runAll(ref, cut);
    cuts++;
    if (c !== d) { bad++; console.log('甲 流式不一样', name, n, firstDiff(c, d, '风月', '日里写法')); break; }
    if (/[ⒽⓁⓃⓅⒸⓎⓆ]/.test(c)) { bad++; console.log('甲 流式露记号', name, n); break; }
  }
  if (!onlyA) {
    nB++;
    const x = normA(b), y = normO(run(orig, src, 'front-end'));
    const era = (y.match(/class="sz-era era-(\w+)"/) || [])[1];
    if (era && !D.eras.includes(era)) { nB--; nSkip++; }     // 别纪的回复（旧样本里混着的），这一张不管
    else if (x !== y) { bad++; console.log('乙 跟日里原样不一样', name, firstDiff(x, y, '这一张', '日里原样')); }
  }
}
console.log(`${D.card}：风月规则 ${D.fy.length} 条都编过了（编不过的上面列了）；甲 ${nA} 条样本、流式 ${cuts} 刀，乙 ${nB} 条样本（别纪的 ${nSkip} 条不比）；问题 ${bad}，展开不干净 ${leak}；一条回复显示一遍最久 ${Math.round(maxMs)} ms（${maxFile}）`);
process.exit(bad ? 1 : 0);
