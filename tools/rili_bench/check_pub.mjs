// 发布卡体检：正则都能编、量词数、量词不套量词；把回复一条条展开，看有没有残留的 § 和记号、页签几个、字里的竖线。用法：node check_pub.mjs 卡.json 回复1 回复2 …
import fs from 'node:fs';
const card = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const rules = card.assistantRegexReplace;
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
let bad = 0, maxQ = 0, nest = 0;
for (const r of rules) {
  const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
  try { new RegExp(m[1], m[2]); } catch (e) { bad++; console.log('编不过', r.regex.slice(0, 80)); }
  const q = (m[1].replace(/\[(?:\\.|[^\]])*\]/g, 'x').replace(/\(\?/g, '(').match(/[*+?]|\{\d/g) || []).length; if (q > maxQ) maxQ = q;
  if (q > 25) console.log('量词过 25', q, r.regex.slice(0, 90));
  if (nested(m[1])) { nest++; console.log('量词套量词', r.regex.slice(0, 140)); }
  if (/\(\?<[=!]/.test(m[1])) console.log('有后顾', r.regex.slice(0, 80));
  if (/[*+?}]\?/.test(m[1].replace(/\(\?/g, ''))) console.log('有惰性', r.regex.slice(0, 80));
  if (!r.enabled || r.messageRole !== 'assistant' || (r.applyMode !== 'front-end' && r.applyMode !== 'all')) console.log('设置不对', JSON.stringify(r).slice(0, 80));
}
console.log('正则', rules.length, '编不过', bad, '最多量词', maxQ, '量词套量词', nest, '样式', (card.injectStyles || '').length, '字');
const apply = (t) => { for (const r of rules) { const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/); t = t.replace(new RegExp(m[1], m[2]), r.replaceString); } return t; };
for (const f of process.argv.slice(3)) {
  const src = fs.readFileSync(f, 'utf8');
  const t0 = Date.now();
  const t = apply(src);
  const ms = Date.now() - t0;
  const text = t.replace(/<style[\s\S]*?<\/style>/g, '').replace(/<[^>]*>/g, '');
  console.log(f.split(/[\\/]/).pop(), '原', src.length, '展开', t.length, '字', ms + 'ms', '残留§', (t.match(/§/g) || []).length, '残留记号', (t.match(/[ⓐ-ⓩ]/g) || []).length, '换行', (t.match(/\n/g) || []).length, 'era-maze', t.includes('era-maze'), '页签', (t.match(/class="sz-tab /g) || []).length, '字里的竖线', (text.match(/[｜|]/g) || []).length, t === src ? '原样' : '');
  const m = text.match(/.{0,24}[｜|].{0,24}/g); if (m) console.log('  竖线', m.slice(0, 8));
  const sec = t.match(/§[^<]{0,60}/g); if (sec) console.log('  §', sec.slice(0, 8));
}
