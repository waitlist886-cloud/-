// 拿一张卡的显示规则把一条回复展开（照平台的做法：顺序套，front-end 和 all 两种），看几种 MOD 写法各落到哪里。
// 用法：node expand_test.mjs <卡.json> <回复.txt> [要找的字…]
import fs from 'node:fs';
const [cardPath, txtPath, ...needles] = process.argv.slice(2);
const card = JSON.parse(fs.readFileSync(cardPath, 'utf8'));
const rules = card.assistantRegexReplace;
function applyRules(text, side) {
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
const src = fs.readFileSync(txtPath, 'utf8').replace(/\r\n/g, '\n');
const toModel = applyRules(src, 'back-end');     // 发给模型的那一路（只走 all 的）
const shown = applyRules(src, 'front-end');
fs.writeFileSync(txtPath.replace(/\.txt$/, '.shown.html'), shown);
fs.writeFileSync(txtPath.replace(/\.txt$/, '.tomodel.txt'), toModel);
const left = shown.match(/§[^\n<]{0,30}/g) || [];
console.log('规则', rules.length, '条；显示那一路残留的 §：', left.length, left.slice(0, 12));
// 每个要找的字：在显示结果里落在哪一页（往前找最近的 p-xxx 页或 sz- 容器）
for (const nd of needles) {
  let idx = shown.indexOf(nd);
  if (idx < 0) { console.log('【' + nd + '】显示结果里没有'); continue; }
  while (idx >= 0) {
    const before = shown.slice(0, idx);
    const pages = [...before.matchAll(/class="sz-page p-([a-z]+)[^"]*"/g)];
    const page = pages.length ? pages[pages.length - 1][1] : '（不在任何一页里）';
    const ctx = shown.slice(Math.max(0, idx - 220), idx + nd.length + 160).replace(/\n/g, '⏎');
    console.log('【' + nd + '】页=' + page + '：…' + ctx + '…\n');
    idx = shown.indexOf(nd, idx + nd.length);
    if (idx > 0) { console.log('   （还有一处）'); break; }
  }
}
// 发给模型的那一路里这几样变成了什么
for (const nd of needles) {
  const i = toModel.indexOf(nd);
  console.log('→模型【' + nd + '】', i < 0 ? '没有' : toModel.slice(Math.max(0, i - 80), i + nd.length + 80).replace(/\n/g, '⏎'));
}
