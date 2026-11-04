// 风月卡的规则回归：转过去的规则（只认 g）跟日里发布卡那一组（带 m、不带 g）逐条回复比，结果除了平台差别（<style>、大写变量、点击属性、钟点记号）要一字不差。
// 用法：node check_fy.mjs <风月卡.json> <日里发布卡.json> <样本文件或目录…>
// 一、历史显示（renderOnly）跟日里的显示比。二、存库（persist）跟日里发给模型的比，转完不许剩标签和临时记号，新记法一字不变（写错的「时段」两个字除外）。
// 三、流式（all）：每隔一截切一刀，跟日里的规则走同样几遍比，不许抛错、不许露临时记号。末尾报一条回复跑一遍多久。
import fs from 'node:fs';
import path from 'node:path';

const [fyFile, rlFile, ...inputs] = process.argv.slice(2);
const fy = JSON.parse(fs.readFileSync(fyFile, 'utf8')).regex_rp;
const rl = JSON.parse(fs.readFileSync(rlFile, 'utf8')).assistantRegexReplace.map((r) => {
  const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
  return { re: new RegExp(m[1], m[2]), rep: r.replaceString, mode: r.applyMode };
});
const fyc = fy.map((r) => ({ re: new RegExp(r.match_regex, 'g'), rep: r.replace_text, only: r.is_only_render === true, title: r.title }));
const runFy = (t, o) => { for (const r of fyc) { if (o === 'persist' && r.only) continue; if (o === 'renderOnly' && !r.only) continue; t = t.replace(r.re, r.rep); } return t; };
const runRl = (t, side) => { for (const r of rl) if (r.mode === 'all' || r.mode === side) t = t.replace(r.re, r.rep); return t; };
// 流式在风月上走 all：转换那一组存库一份、显示一份都走，所以这里也走两遍
const runRlAll = (t) => { for (const r of rl) if (r.mode === 'all') t = t.replace(r.re, r.rep); for (const r of rl) if (r.mode === 'all' || r.mode === 'front-end') t = t.replace(r.re, r.rep); return t; };
// 日里的结果换成风月该有的样子
const norm = (t) => t
  .replace(/<style>[\s\S]*?<\/style>/g, '')
  .replace(/(?<![\w-])--(v|m|h|n|a[1-6])(?![\w-])/g, (m, a) => '--' + a.toUpperCase())
  .replace(/ data-action="set-textinput" data-value="[^"]*"/g, '');
const normFy = (t) => t.replace(/<i class="sz-hh" data-h="[^"]*"><\/i>/g, '');
const MARK = /[ⒽⓁⓃⓅⒸⓎⓆⓔⓩ]/;
const files = [];
for (const p of inputs) {
  if (fs.statSync(p).isDirectory()) for (const f of fs.readdirSync(p)) { if (/\.(txt|html)$/.test(f)) files.push(path.join(p, f)); }
  else files.push(p);
}
let bad = 0, cuts = 0, maxMs = 0, maxFile = '';
const firstDiff = (a, b) => { let i = 0; while (i < a.length && a[i] === b[i]) i++; return `@${i} 风月「${a.slice(Math.max(0, i - 40), i + 60)}」 日里「${b.slice(Math.max(0, i - 40), i + 60)}」`; };
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8').split('\r').join('');
  const t0 = performance.now();
  const a = normFy(runFy(src, 'renderOnly'));
  const ms = performance.now() - t0;
  if (ms > maxMs) { maxMs = ms; maxFile = path.basename(f); }
  const b = norm(runRl(src, 'front-end'));
  if (a !== b) { bad++; console.log('一 显示不一样', path.basename(f), firstDiff(a, b)); }
  const p = runFy(src, 'persist');
  const q = runRl(src, 'back-end');
  if (p !== q) { bad++; console.log('二 存库不一样', path.basename(f), firstDiff(p, q)); }
  if (/\/[^/]*$/.test(f) && MARK.test(p)) { bad++; console.log('二 存库露记号', path.basename(f), p.match(/.{0,20}[ⒽⓁⓃⓅⒸⓎⓆⓔⓩ].{0,20}/)[0]); }
  for (let n = 80; n < src.length; n += 211) {
    const cut = src.slice(0, n);
    let c, d;
    try { c = normFy(runFy(cut, 'all')); } catch (e) { bad++; console.log('三 抛错', path.basename(f), n, e.message); break; }
    d = norm(runRlAll(cut));
    cuts++;
    if (c !== d) { bad++; console.log('三 流式不一样', path.basename(f), n, firstDiff(c, d)); break; }
    if (/[ⒽⓁⓃⓅⒸⓎⓆ]/.test(c)) { bad++; console.log('三 流式露记号', path.basename(f), n, c.match(/.{0,20}[ⒽⓁⓃⓅⒸⓎⓆ].{0,20}/)[0]); break; }
  }
}
console.log('样本', files.length, '条，切了', cuts, '刀，问题', bad, '；一条回复跑一遍最久', Math.round(maxMs), 'ms（' + maxFile + '）');
