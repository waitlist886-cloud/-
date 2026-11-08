// 四纪大框（11-08）：字眼从一处一条规则改成页上写齐四纪、样式露一个，对一遍。
// 用法：node cmp_four.mjs 旧规则.json 新规则.json 回复1 回复2 …
//   旧规则、新规则都可以是卡（读 assistantRegexReplace）或规则清单（make_rules_frame.py 写的那种）。
//   新的那一路照回复里的纪元挑出那一纪的字（w0 迷宫纪、前传，wm 月银纪，ws 纷争纪，wb 山铜纪），凡极那一格月银纪、纷争纪、山铜纪拿掉，再跟旧的比。
//   加 --loose：对话框、正文里的专名小卡、衣着这些旧规则没有的东西先拆回原样再比，只报剩下的差别（拿发布卡当旧的时候用）。
import fs from 'node:fs';
const args = process.argv.slice(2);
const loose = args.includes('--loose');
const [oldP, newP, ...files] = args.filter((a) => !a.startsWith('--'));
const load = (p) => { const j = JSON.parse(fs.readFileSync(p, 'utf8')); return Array.isArray(j) ? j : j.assistantRegexReplace; };
function apply(text, rules, side) {
  for (const r of rules) {
    if (r.enabled === false || (r.messageRole !== 'all' && r.messageRole !== 'assistant')) continue;
    if (r.applyMode !== 'all' && r.applyMode !== side) continue;
    const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
    text = m ? text.replace(new RegExp(m[1], m[2]), r.replaceString) : text.split(r.regex).join(r.replaceString);
  }
  return text;
}
const OLD = load(oldP), NEW = load(newP);
const conv = JSON.parse(fs.readFileSync(new URL('../../底稿/状态栏/大框/rules_convert.json', import.meta.url), 'utf8'));
const withConv = (rs) => (rs.length < 400 ? conv.concat(rs) : rs);   // 只给了展开那一组的，前头补上转换那一组
const O = withConv(OLD), N = withConv(NEW);
const LW = /<span class="lw"><span class="w0">([^<]*)<\/span><span class="wm">([^<]*)<\/span><span class="ws">([^<]*)<\/span><span class="wb">([^<]*)<\/span><\/span>/g;
function pick(t) {
  const era = /era-moon/.test(t) ? 2 : /era-strife/.test(t) ? 3 : /era-bronze/.test(t) ? 4 : 1;
  t = t.replace(LW, (...m) => m[era]);
  if (era > 1) t = t.split('<i data-t="凡极"><b>凡极</b></i>').join('');
  return t.replace(/ data-y="[^"]*"/g, '');   // 11-08 认纪元那一枚记号添了年份
}
function unloose(t) {
  // 专名小卡拆回字，对话框拆回一段（只留台词），衣着的属性拿掉
  t = t.replace(/<span class="sz-t(?: new)?" tabindex="0">([^<]*)<i class="sz-tip"[^>]*><\/i><\/span>/g, '$1');
  t = t.replace(/ data-o="[^"]*"/g, '').replace(/<b class="sz-por-t"><\/b>/g, '');
  t = t.replace(/ data-portrait="[^"]*"/g, '').replace(/<b class="sz-por-t"[^>]*><\/b>/g, '');   // 11-08 名牌也照名字认立绘
  return t;
}
let bad = 0;
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8').replace(/\r/g, '');
  for (const side of ['front-end', 'back-end']) {
    let o = apply(src, O, side), n = pick(apply(src, N, side));
    if (loose) { o = unloose(o); n = unloose(n); }
    if (o !== n) {
      bad++;
      let i = 0;
      while (i < o.length && o[i] === n[i]) i++;
      console.log('✗', f.split(/[\\/]/).pop(), side, '从第', i, '字起不一样\n   旧', JSON.stringify(o.slice(Math.max(0, i - 60), i + 140)), '\n   新', JSON.stringify(n.slice(Math.max(0, i - 60), i + 140)));
    }
  }
}
console.log(files.length, '条回复，不一样的', bad, '处');
