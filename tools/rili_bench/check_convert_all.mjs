// 转换规则的几道回归。用法：node check_convert_all.mjs 卡.json 旧回复目录 --new 新记法回复…
// 一、发给模型的那一路（只走 applyMode all）：旧回复转完不许剩标签和临时记号。
// 二、流式：旧回复和混写回复从头每隔一截切一刀，两路都不许抛错、不许露临时记号。
// 三、新记法的回复过这一组，除了写错的「时段」两个字，一个字不变。
import fs from 'node:fs';
import path from 'node:path';
const card = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const oldDir = process.argv[3];
const newStart = process.argv.indexOf('--new');
const news = newStart > 0 ? process.argv.slice(newStart + 1) : [];
const comp = card.assistantRegexReplace.map((r) => {
  const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
  return { re: new RegExp(m[1], m[2]), rep: r.replaceString, mode: r.applyMode };
});
const run = (t, side) => { for (const r of comp) if (r.mode === 'all' || r.mode === side) t = t.replace(r.re, r.rep); return t; };
const MARK = /[ⒽⓁⓃⓅⒸⓎⓆ]/;
let bad = 0;
const olds = fs.readdirSync(oldDir).map((f) => path.join(oldDir, f));
for (const f of olds) {
  const src = fs.readFileSync(f, 'utf8');
  const ai = run(src, 'back-end');
  const tags = ai.match(/<\/?[a-zA-Z][^>]{0,60}>/g) || [];
  if (tags.length || MARK.test(ai)) { bad++; console.log('一 剩东西', path.basename(f), tags.slice(0, 4)); }
  for (let n = 80; n < src.length; n += 97) {
    const cut = src.slice(0, n);
    for (const side of ['back-end', 'front-end']) {
      let o;
      try { o = run(cut, side); } catch (e) { bad++; console.log('二 抛错', path.basename(f), n, e.message); continue; }
      if (MARK.test(o)) { bad++; console.log('二 露记号', path.basename(f), side, n, o.match(/.{0,20}[ⒽⓁⓃⓅⒸⓎⓆ].{0,20}/)[0]); n = src.length; break; }
    }
  }
}
for (const f of news) {
  const src = fs.readFileSync(f, 'utf8');
  const ai = run(src, 'back-end');
  if (ai !== src && ai !== src.replace(/^(§底座｜[^\n]{0,60}\d{1,2}[:：]\d{2}) 时段(?= ·)/m, '$1')) { bad++; console.log('三 动了新记法', path.basename(f), ai.length, src.length); }
}
console.log('旧回复', olds.length, '条，新记法', news.length, '条，问题', bad);
