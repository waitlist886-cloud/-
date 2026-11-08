// 发布卡换规则以前对一遍：同一批回复，旧卡和新卡各展开一遍（显示一路、发给模型一路），报大框、纪元、地图页、兜底的头、MOD 卡、残留 § 和记号几样，两路一字不差的标出来。
// 用法：node cmp_rules_pub.mjs 旧卡.json 新卡.json 回复1 回复2 …（写歪的回复在 底稿/状态栏/大框/发布/试写/写歪/）
import fs from 'node:fs';
const load = (p) => JSON.parse(fs.readFileSync(p, 'utf8')).assistantRegexReplace;
function apply(text, rules, side) {
  for (const r of rules) {
    if (!r.enabled || (r.messageRole !== 'all' && r.messageRole !== 'assistant')) continue;
    if (r.applyMode !== 'all' && r.applyMode !== side) continue;
    const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
    text = m ? text.replace(new RegExp(m[1], m[2]), r.replaceString) : text.split(r.regex).join(r.replaceString);
  }
  return text;
}
const [oldCard, newCard, ...files] = process.argv.slice(2);
const OLD = load(oldCard), NEW = load(newCard);
const cnt = (s, re) => (s.match(re) || []).length;
const stat = (t) => `大框${cnt(t, /class="sz-hud"/g)} 纪元${cnt(t, /era-maze/g)} 地图${cnt(t, /p-map/g)} 兜底头${cnt(t, /class="sz-raw"/g)} MOD${cnt(t, /data-k="MOD"/g)} §${cnt(t, /§/g)} 记号${cnt(t, /[ⓐ-ⓩⒶ-Ⓩ]/g)}`;
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8').replace(/\r/g, '');
  const o = apply(src, OLD, 'front-end'), n = apply(src, NEW, 'front-end');
  const same = o === n, sameAi = apply(src, OLD, 'back-end') === apply(src, NEW, 'back-end');
  console.log(f.split(/[\/]/).pop(), '| 旧', stat(o), '| 新', stat(n), same ? '| 显示一样' : '| 显示变了', sameAi ? '| 发模型一样' : '| 发模型变了');
}
