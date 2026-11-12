// 两张卡的显示规则把同一批回复各展开一遍，比显示那一路和发给模型那一路。新卡多出来的扩展页签先拿掉再比。
// 用法：node regress.mjs <旧卡.json> <新卡.json> <回复文件或目录…>
import fs from 'node:fs';
import path from 'node:path';
const [oldP, newP, ...targets] = process.argv.slice(2);
const load = (p) => JSON.parse(fs.readFileSync(p, 'utf8')).assistantRegexReplace;
const RO = load(oldP), RN = load(newP);
function run(rules, text, side) {
  for (const r of rules) {
    if (r.enabled === false) continue;
    if (r.messageRole !== 'all' && r.messageRole !== 'assistant') continue;
    if (r.applyMode !== 'all' && r.applyMode !== side) continue;
    const m = r.regex.startsWith('/') ? r.regex.match(/^\/([\s\S]*)\/([^/]*)$/) : null;
    if (m) text = text.replace(new RegExp(m[1], [...m[2]].filter((f) => 'imsg'.includes(f)).join('')), r.replaceString);
    else text = text.split(r.regex).join(r.replaceString);
  }
  return text;
}
// 新卡的规则都得编得过
let bad = 0;
for (const r of RN) { const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/); try { new RegExp(m[1], m[2]); } catch (e) { bad++; console.log('编不过', r.regex.slice(0, 80), e.message); } }
const TAB = '<label class="sz-tab t-mod"><input type="radio" name="sz-tab"><i></i><b>扩展</b></label>';
const files = [];
for (const t of targets) {
  if (fs.statSync(t).isDirectory()) for (const f of fs.readdirSync(t)) { if (/\.(txt|html)$/.test(f) && !/\.(shown|expanded)\.html$/.test(f) && !/tomodel/.test(f)) files.push(path.join(t, f)); }
  else files.push(t);
}
let same = 0; const diffs = [];
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8').replace(/\r\n/g, '\n');
  const t0 = Date.now();
  const a = run(RO, src, 'front-end'), b = run(RN, src, 'front-end').split(TAB).join('');
  const am = run(RO, src, 'back-end'), bm = run(RN, src, 'back-end');
  const ms = Date.now() - t0;
  const left = (b.match(/§[^\n<]{0,24}/g) || []).length;
  if (a === b && am === bm) same++; else {
    let i = 0; while (i < a.length && a[i] === b[i]) i++;
    let j = 0; while (j < am.length && am[j] === bm[j]) j++;
    diffs.push([path.basename(f), a === b ? '显示一样' : '显示不同@' + i + '：旧「' + a.slice(Math.max(0, i - 40), i + 90).replace(/\n/g, '⏎') + '」新「' + b.slice(Math.max(0, i - 40), i + 130).replace(/\n/g, '⏎') + '」',
      am === bm ? '发给模型的一样' : '发给模型的不同@' + j + '：旧「' + am.slice(Math.max(0, j - 30), j + 70).replace(/\n/g, '⏎') + '」新「' + bm.slice(Math.max(0, j - 30), j + 90).replace(/\n/g, '⏎') + '」']);
  }
  if (left || ms > 1500) console.log('  ', path.basename(f), '残留 §', left, '用时', ms, 'ms');
}
console.log('规则 旧', RO.length, '新', RN.length, '编不过', bad, '；回复', files.length, '条，一样的', same, '条，不一样的', diffs.length, '条');
for (const d of diffs) console.log('—', d[0], '\n   ', d[1], '\n   ', d[2]);
