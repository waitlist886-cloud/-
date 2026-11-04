// 迷宫纪的样本，改前改后的规则各展开一遍，去掉 <style> 以后逐字比
import fs from 'node:fs';
const [oldp, newp, ...files] = process.argv.slice(2);
const load = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
function apply(text, rules) {
  for (const r of rules) {
    const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
    text = text.replace(new RegExp(m[1], m[2]), r.replaceString);
  }
  return text;
}
const strip = (s) => s.replace(/<style>[\s\S]*?<\/style>/g, '');
const a = load(oldp), b = load(newp);
for (const f of files) {
  const t = fs.readFileSync(f, 'utf8');
  const x = strip(apply(t, a)), y = strip(apply(t, b));
  let i = 0;
  while (i < x.length && x[i] === y[i]) i++;
  console.log(f.split(/[\\/]/).pop(), x.length, y.length, x === y ? '一字不差' : '不同，第 ' + i + ' 字起\n  旧 ' + x.slice(Math.max(0, i - 60), i + 120) + '\n  新 ' + y.slice(Math.max(0, i - 60), i + 120));
}
