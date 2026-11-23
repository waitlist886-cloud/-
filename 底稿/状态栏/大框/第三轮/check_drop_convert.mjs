// 11-23 第三轮：拿掉“转”那一组（旧 HTML 回复转记录，132 条）以后，新格式的样本展开出来一不一样。
// 用法（仓库根上）：node 底稿/状态栏/大框/第三轮/check_drop_convert.mjs
import fs from 'node:fs';
import path from 'node:path';
const D = 'E:/aldran_art/底稿/状态栏/大框';
const conv = JSON.parse(fs.readFileSync(D + '/rules_convert.json', 'utf8'));
const frame = JSON.parse(fs.readFileSync(D + '/rules_frame.json', 'utf8'));
function apply(text, rules) {
  for (const r of rules) {
    const m = r.regex.startsWith('/') ? r.regex.match(/^\/([\s\S]*)\/([^/]*)$/) : null;
    if (m) text = text.replace(new RegExp(m[1], [...m[2]].filter((f) => 'imsg'.includes(f)).join('')), r.replaceString);
    else text = text.split(r.regex).join(r.replaceString);
  }
  return text;
}
const keep = conv.filter((r) => !(r.name || '').startsWith('转'));
console.log('转换那一组', conv.length, '条，拿掉转以后剩', keep.length, '条；大框', frame.length, '条');
const files = fs.readdirSync(D).filter((f) => /^样本.*\.txt$/.test(f)).map((f) => D + '/' + f)
  .concat(fs.existsSync(D + '/第三轮') ? fs.readdirSync(D + '/第三轮').filter((f) => /^样本.*\.txt$/.test(f)).map((f) => D + '/第三轮/' + f) : []);
let bad = 0;
for (const f of files) {
  const t = fs.readFileSync(f, 'utf8').replace(/\r\n/g, '\n');
  const a = apply(t, conv.concat(frame)), b = apply(t, keep.concat(frame));
  if (a !== b) { bad++; let k = 0; while (a[k] === b[k]) k++; console.log('不一样', path.basename(f), '第', k, '字：', JSON.stringify(a.slice(k - 30, k + 60)), '｜', JSON.stringify(b.slice(k - 30, k + 60))); }
}
console.log('样本', files.length, '个，不一样的', bad);
