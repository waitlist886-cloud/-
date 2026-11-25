// 11-25 兜底那一轮的体检（由 兜底_体检.py 叫起来，也可以单跑）：node check_兜底.mjs <卡里次序的规则.json> <歪法单.json> [改前的规则.json]
// 一、整张规则表：编得过、量词不过二十五、量词不套量词、没有后顾（照 tools/rili_bench/check_card.mjs 的数法）。
// 二、歪法单：一种一种换进 第三轮/样本_四样同屏.txt 展开，数整张、简版、落成一行的、家业卡、宠卡、漏在页上的竖线反引号记号，跟单子上要的比。
// 三、给了改前的规则：大框/ 和 第三轮/ 下现成的样本改前改后各展开一遍，只许差主角那一边的 jg-pc 和立绘样式多认的那一个选择器；发给模型的（只走 all 的规则）要一字不差。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const D = path.dirname(here);
const [rulesPath, probesPath, basePath] = process.argv.slice(2);
const rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8'));
const cnt = (s, re) => (s.match(re) || []).length;
const split = (rx) => rx.match(/^\/([\s\S]*)\/([^/]*)$/);
function apply(text, rs, side) {
  for (const r of rs) {
    if (r.enabled === false) continue;
    if (r.applyMode !== 'all' && r.applyMode !== side) continue;
    const m = split(r.regex);
    text = text.replace(new RegExp(m[1], [...m[2]].filter((f) => 'imsg'.includes(f)).join('')), r.replaceString);
  }
  return text;
}
// ---- 一 ----
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
let badRule = 0, maxQ = [0, ''];
for (const r of rules) {
  const m = split(r.regex);
  let why = '';
  try { new RegExp(m[1], m[2]); } catch (e) { why += ' 编不过：' + e.message; }
  const q = (m[1].replace(/\[(?:\\.|[^\]])*\]/g, 'x').replace(/\(\?/g, '(').match(/[*+?]|\{\d/g) || []).length;
  if (q > maxQ[0]) maxQ = [q, r.name || ''];
  if (q > 25) why += ' 量词 ' + q + ' 过二十五';
  if (nested(m[1])) why += ' 量词套量词';
  if (/\(\?<[=!]/.test(m[1])) why += ' 有后顾';
  if (why) { badRule++; console.log('规则不过关', r.name || r.regex.slice(0, 40), why); }
  if (/稳·三录|^判/.test(r.name || '')) console.log('  ' + (r.name + '　　　　').slice(0, 8), '量词', q, r.applyMode);
}
console.log('规则', rules.length, '条（卡里另有 css_cdn 末尾插样式的一条），量词最多', maxQ[0], maxQ[1], '，不过关的', badRule);
// ---- 二 ----
const base = fs.readFileSync(here + '/样本_四样同屏.txt', 'utf8').split('\r').join('');
const probes = JSON.parse(fs.readFileSync(probesPath, 'utf8'));
let bad = 0;
for (const p of probes) {
  const L = base.split('\n');
  const i = L.findIndex((l) => l.startsWith('§' + p.kind + '｜'));
  L.splice(i, 1, ...p.lines);
  const t = apply(L.join('\n'), rules, 'front-end');
  const text = t.replace(/<style[\s\S]*?<\/style>/g, '').replace(/<[^>]*>/g, '\n');
  const o = {
    整张: cnt(t, /class="sz-judge"/g), 简版: cnt(t, /class="sz-judge jg-s"/g), 判落兜底: cnt(t, /sz-row" data-k="判"/g),
    家业卡: cnt(t, /class="sz-es"/g), 没类的卡: cnt(t, /class="sz-es" data-k=""/g), 宠卡: cnt(t, /class="sz-pet"/g), 没头的宠: cnt(t, /class="sz-pet" data-s=""/g), 浮栏宠: cnt(t, /sz-pfc sz-pfp/g),
    MOD卡: cnt(t, /data-k="MOD"/g), 剩半角竖线: cnt(text, /\|/g), 剩反引号: cnt(text, /`/g), 剩记号: cnt(t, /[ⓐ-ⓩⒶ-Ⓩ]/g),
  };
  const miss = Object.entries(p.expect || {}).filter(([k, v]) => o[k] !== v).map(([k, v]) => k + ' 要 ' + v + ' 得 ' + o[k]);
  if (miss.length) bad++;
  if (miss.length || process.env.ALL) console.log((miss.length ? '  ×× ' : '  ok ') + p.name + '：' + Object.entries(o).filter(([, v]) => v).map(([k, v]) => k + ' ' + v).join('，') + (miss.length ? '　对不上：' + miss.join('；') : '') + (p.note ? '　（' + p.note + '）' : ''));
}
console.log('歪法', probes.length, '种，对不上的', bad);
// ---- 三 ----
if (basePath) {
  const old = JSON.parse(fs.readFileSync(basePath, 'utf8'));
  const norm = (t) => t.replace(/ jg-pc(" data-portrait="[^"]*") data-r="[^"]*" data-g="[^"]*" data-e="[^"]*"/g, '$1').replace(/(\.sz-say\[data-portrait="[^"]*"\]),\.custom-styles \.jg-w\.jg-pc\{/g, '$1{');
  const files = [D, here].flatMap((d) => fs.readdirSync(d).filter((f) => /^样本.*\.txt$/.test(f) && !/兜底|主角头像/.test(f)).map((f) => d + '/' + f));
  let same = 0, sameN = 0, diff = 0, sent = 0;
  for (const f of files) {
    const t = fs.readFileSync(f, 'utf8').split('\r').join('');
    const a = apply(t, old, 'front-end'), b = apply(t, rules, 'front-end');
    if (apply(t, old, '') !== apply(t, rules, '')) { sent++; console.log('  发给模型的不一样', path.basename(f)); }
    if (a === b) same++; else if (norm(b) === a) sameN++; else { diff++; let k = 0; const nb = norm(b); while (a[k] === nb[k]) k++; console.log('  不一样', path.basename(f), '\n    改前', JSON.stringify(a.slice(Math.max(0, k - 40), k + 120)), '\n    改后', JSON.stringify(nb.slice(Math.max(0, k - 40), k + 120))); }
  }
  console.log('现成的样本', files.length, '个：一字不差', same, '，只差主角那一边的记号', sameN, '，别的不一样', diff, '，发给模型的不一样', sent);
}
process.exitCode = badRule || bad ? 1 : 0;
