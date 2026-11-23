// 家业页这一份的体检（在仓库根上跑）：node 底稿/状态栏/大框/第三轮/check_家业页.mjs <rules_合并.json> [样本…]
// 一、这一份的规则：编得过、量词数、量词不套量词、没有后顾和惰性。二、合并以后的整张表展开各样本：没有剩 § 行和中间记号。
// 三、没有家业和魔宠的旧样本：合并前后只差收卷那一处（页签和一页空的）。
import fs from 'node:fs';
const [merged, ...samples] = process.argv.slice(2);
const mine = JSON.parse(fs.readFileSync('底稿/状态栏/大框/第三轮/家业页_rules.json', 'utf8'));
const base = JSON.parse(fs.readFileSync('底稿/状态栏/大框/rules_frame.json', 'utf8'));
const all = JSON.parse(fs.readFileSync(merged, 'utf8'));
// 星高：照 tools/rili_bench/check_card.mjs
function nested(src) {
  const st = [{ q: false }];
  let i = 0;
  const isQ = (k) => '*+?'.includes(src[k]) || (src[k] === '{' && /^\{\d/.test(src.slice(k)));
  while (i < src.length) {
    const c = src[i];
    if (c === '\\') { i += 2; if (i < src.length && isQ(i)) st[st.length - 1].q = true; continue; }
    if (c === '[') { i++; if (src[i] === '^') i++; if (src[i] === ']') i++; while (src[i] !== ']') { if (src[i] === '\\') i++; i++; } i++; if (isQ(i)) st[st.length - 1].q = true; continue; }
    if (c === '(') { st.push({ q: false }); i++; if (src[i] === '?') i += 2; continue; }
    if (c === ')') { const g = st.pop(); i++; if (isQ(i)) { if (g.q) return true; st[st.length - 1].q = true; } else if (g.q) st[st.length - 1].q = true; continue; }
    if (isQ(i)) { st[st.length - 1].q = true; if (src[i] === '{') { while (src[i] !== '}') i++; } i++; continue; }
    i++;
  }
  return false;
}
let maxQ = 0;
for (const r of mine) {
  const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
  try { new RegExp(m[1], m[2]); } catch (e) { console.log('编不过', r.name, e.message); }
  const q = (m[1].replace(/\[(?:\\.|[^\]])*\]/g, 'x').replace(/\(\?/g, '(').match(/[*+?]|\{\d/g) || []).length;
  maxQ = Math.max(maxQ, q);
  if (q > 25) console.log('量词过 25', q, r.name);
  if (nested(m[1])) console.log('量词套量词', r.name);
  if (/\(\?<[=!]/.test(m[1])) console.log('有后顾', r.name);
  if (/[*+?}]\?/.test(m[1].replace(/\(\?/g, ''))) console.log('有惰性', r.name);
  if (/\n/.test(m[1])) console.log('正则里有真换行', r.name);
}
console.log('这一份', mine.length, '条，最多量词', maxQ, '；合并以后', all.length, '条');
const run = (t, rules) => { for (const r of rules) { const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/); t = t.replace(new RegExp(m[1], m[2]), r.replaceString); } return t; };
for (const f of samples) {
  const src = fs.readFileSync(f, 'utf8').split('\r').join('');
  const t = run(src, all);
  const text = t.replace(/<style[\s\S]*?<\/style>/g, '').replace(/<[^>]*>/g, '');
  const has = /^§(家业|宠)｜/m.test(src);
  let line = `${f.split('/').pop()}：展开 ${t.length} 字，剩 § ${(t.match(/§/g) || []).length}，剩记号 ${(t.match(/[ⓐ-ⓩ]/g) || []).length}，字里的竖线 ${(text.match(/[｜]/g) || []).length}，卡 ${(t.match(/class="sz-es"/g) || []).length}，宠 ${(t.match(/class="sz-pet"/g) || []).length}，浮栏里的宠 ${(t.match(/sz-pfc sz-pfp/g) || []).length}`;
  if (!has) {
    const a = run(src, base);
    const b = t.replace(/<section class="sz-page sz-pane p-estate p-es0">[\s\S]*?<\/section>/, '').replace(/<label class="sz-tab t-estate">[\s\S]*?<\/label>/, '');
    line += a === b ? '；没有家业的样本：跟合并前一样（只多页签和一页空的）' : '；！！跟合并前不一样';
  }
  console.log(line);
  const sec = t.match(/§[^<]{0,40}/g); if (sec) console.log('  ', sec.slice(0, 6));
  if (process.env.DUMP) fs.writeFileSync(process.env.DUMP + '/' + f.split('/').pop() + '.html', t);
}
