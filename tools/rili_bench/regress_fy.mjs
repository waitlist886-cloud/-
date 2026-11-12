// 风月两张卡的显示规则把同一批回复各展开一遍再比。风月只认 g；新回复先走不带仅渲染的（写回库里），显示再走仅渲染的。
// 用法：node regress_fy.mjs <旧卡.json> <新卡.json> <回复文件或目录…>
import fs from 'node:fs';
import path from 'node:path';
const [oldP, newP, ...targets] = process.argv.slice(2);
function load(p) {
  const c = JSON.parse(fs.readFileSync(p, 'utf8'));
  const k = Object.keys(c).find((x) => Array.isArray(c[x]) && c[x].length && c[x][0] && 'match_regex' in c[x][0]);
  return c[k];
}
const RO = load(oldP), RN = load(newP);
function pass(rules, text, renderOnly) {
  for (const r of rules) {
    if (!r.is_enable || !(r.scope & 1)) continue;
    if (!!r.is_only_render !== renderOnly) continue;
    text = text.replace(new RegExp(r.match_regex, 'g'), r.replace_text);
  }
  return text;
}
const run = (rules, src) => { const stored = pass(rules, src, false); return [stored, pass(rules, stored, true)]; };
let bad = 0;
for (const r of RN) { try { new RegExp(r.match_regex, 'g'); } catch (e) { bad++; console.log('编不过', r.title, e.message); } }
const TAB = '<label class="sz-tab t-mod"><input type="radio" name="sz-tab"><i></i><b>扩展</b></label>';
const files = [];
for (const t of targets) {
  if (fs.statSync(t).isDirectory()) for (const f of fs.readdirSync(t)) { if (/\.(txt|html)$/.test(f) && !/\.(shown|expanded)\.html$/.test(f) && !/tomodel/.test(f)) files.push(path.join(t, f)); }
  else files.push(t);
}
let same = 0; const diffs = [];
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8').replace(/\r\n/g, '\n');
  const [as, a] = run(RO, src);
  let [bs, b] = run(RN, src);
  b = b.split(TAB).join('');
  if (a === b && as === bs) same++; else {
    let i = 0; while (i < a.length && a[i] === b[i]) i++;
    diffs.push([path.basename(f), as === bs ? '存的一样' : '存的不同', a === b ? '显示一样' : '显示不同@' + i + '：新「' + b.slice(Math.max(0, i - 30), i + 150).replace(/\n/g, '⏎') + '」',
      (b.match(/class="sz-page sz-pane p-mod"/g) || []).length + ' 个扩展页，' + (b.match(/class="sz-nw sz-mods" data-k="[^"]*"/g) || []).join(' ')]);
  }
}
console.log('规则 旧', RO.length, '新', RN.length, '编不过', bad, '；回复', files.length, '条，一样的', same, '条，不一样的', diffs.length, '条');
for (const d of diffs) console.log('—', d.join('\n    ').slice(0, 520));
