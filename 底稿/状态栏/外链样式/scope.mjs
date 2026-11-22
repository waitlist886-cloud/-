// 卡的样式照日里平台的规矩加 .custom-styles 作用域（跟 tools/rili_bench/platform.mjs 的 scopeCss 一样，11-21 外链样式探针用的那一份）。
// 平台只对卡的样式格做这一步；挪上图床、靠 link 载进来的样式平台不管，得先照样做好。
//   node scope.mjs <源.css> <出.css>
import fs from 'fs';
import postcss from 'postcss';
const KEEP = new Set(['media', 'keyframes', '-webkit-keyframes', 'font-face']);
const [, , src, dst] = process.argv;
const root = postcss.parse(fs.readFileSync(src, 'utf8'));
const dropped = {};
root.walkAtRules((at) => {
  if (!KEEP.has(at.name)) { dropped['@' + at.name] = (dropped['@' + at.name] || 0) + 1; at.remove(); }
});
root.walkRules((rule) => {
  let p = rule.parent;
  while (p && p.type !== 'root') { if (p.type === 'atrule' && /keyframes$/.test(p.name)) return; p = p.parent; }
  rule.selectors = rule.selectors.map((s) => {
    s = s.trim();
    if (s.startsWith(':root')) return '.custom-styles' + s.slice(5);
    return '.custom-styles ' + s;
  });
});
const css = root.toString();
fs.writeFileSync(dst, css);
console.log(JSON.stringify({ len: css.length, dropped }));
