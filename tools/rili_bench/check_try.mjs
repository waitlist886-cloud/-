// 试写的回复过一遍卡的规则（显示那一路），报：大框出没出、认的哪一纪和年份、残留的 § 和记号、对话框几个、立绘和衣着、主线那一格、§底座 原文
// 用法：node check_try.mjs 卡.json 回复1 回复2 …
import fs from 'node:fs';
const [cardPath, ...files] = process.argv.slice(2);
const rules = JSON.parse(fs.readFileSync(cardPath, 'utf8')).assistantRegexReplace;
function apply(text, side) {
  for (const r of rules) {
    if (r.enabled === false || (r.messageRole !== 'all' && r.messageRole !== 'assistant')) continue;
    if (r.applyMode !== 'all' && r.applyMode !== side) continue;
    const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
    text = m ? text.replace(new RegExp(m[1], m[2]), r.replaceString) : text.split(r.regex).join(r.replaceString);
  }
  return text;
}
const cnt = (s, re) => (s.match(re) || []).length;
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8').replace(/\r/g, '');
  const h = apply(src, 'front-end');
  const vis = h.replace(/<style>[\s\S]*?<\/style>/g, '').replace(/<[^>]*>/g, '');
  const era = (h.match(/class="sz-era (era-[a-z]+)" data-y="([^"]*)"/) || []).slice(1).join(' ');
  const pors = [...h.matchAll(/class="sz-npc" data-portrait="([^"]*)" data-o="([^"]*)"/g)].map((m) => m[1] + '/' + (m[2] || '-'));
  const says = [...h.matchAll(/class="sz-say" data-portrait="([^"]*)" data-em="([^"]*)"/g)].map((m) => m[1] + '/' + (m[2] || '-'));
  const quest = (h.match(/<span class="sz-quest">([\s\S]*?)<\/span><\/span>|<span class="sz-quest">([\s\S]*?)<\/span>/) || [''])[0].replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
  const leftS = (vis.match(/[^\n]{0,20}§[^\n]{0,30}/g) || []).slice(0, 4);
  console.log('==', f.split(/[\\/]/).pop(), '| 大框', cnt(h, /class="sz-hud"/g), '|', era || '没认出纪元', '| 页签', cnt(h, /class="sz-tabs"/g), '| 兜底行', cnt(h, /sz-row"/g), '| 记号', cnt(vis, /[ⓐ-ⓩⒶ-Ⓩ]/g));
  console.log('   底座', (src.match(/^§底座｜[^\n]*/m) || ['(没有)'])[0].slice(0, 150));
  console.log('   主线', quest || '(没有)', '| 对话', says.length, says.slice(0, 6).join(' '), '| 立绘', pors.join(' '));
  if (leftS.length) console.log('   残留 §', leftS.join(' ‖ '));
  const recs = [...new Set((src.match(/^§[^｜\n]{1,8}/gm) || []))];
  console.log('   写了的记录', recs.join(' '));
}
