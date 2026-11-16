// 粗查一张卡（11-15）：显示规则和世界书触发的正则编不编得过、量词多不多、有没有量词套量词，各样大小在不在平台的上限里。
//   node 底稿/门面/共用/chk_card.mjs <卡.json>
// 量词套量词的算法照 rili-card-studio 里 fy2rili.py 那一段的简化版（平台自己是 safe-regex，这里不装依赖）。tools/rili_bench/check_card.mjs 查得更细，要先装它的 node_modules。
import fs from 'node:fs';
const card = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const parse = (s) => { const m = /^\/([\s\S]*)\/([a-z]*)$/.exec(s); return m ? { src: m[1], flags: [...m[2]].filter((f) => 'imsg'.includes(f)).join('') } : null; };
const strip = (k) => k.replace(/\\./g, 'x').replace(/\[(?:\\.|[^\]\\])*\]/g, 'C');
const quants = (k) => (strip(k).replace(/\(\?[:=!]|\(\?<[=!]/g, '(').match(/\{\d*,?\d*\}|[*+?]/g) || []).length;
function starHeight(k) {
  const s = strip(k); let i = 0, best = 0; const st = [0]; let prevClose = false, prevInner = 0;
  while (i < s.length) {
    const c = s[i];
    if (c === '(') { const m = /^\(\?(?:[:=!]|<[=!])/.exec(s.slice(i)); i += m ? m[0].length : 1; st.push(0); prevClose = false; continue; }
    if (c === ')') { prevInner = st.pop() || 0; prevClose = true; i++; continue; }
    const m = c === '{' ? /^\{\d*,?\d*\}/.exec(s.slice(i)) : null;
    if ('*+?'.includes(c) || m) { const d = 1 + (prevClose ? prevInner : 0); best = Math.max(best, d); st[st.length - 1] = Math.max(st[st.length - 1], d); i += m ? m[0].length : 1; prevClose = false; continue; }
    prevClose = false; i++;
  }
  return best;
}
let bad = 0, n = 0;
const chk = (what, s) => {
  const p = parse(String(s || '')); if (!p) return; n++;
  try { new RegExp(p.src, p.flags); } catch (e) { bad++; console.log('编不过', what, String(e.message).slice(0, 80)); return; }
  const q = quants(p.src), h = starHeight(p.src);
  if (q > 25) { bad++; console.log('量词', q, '个', what, s.slice(0, 70)); }
  if (h > 1) { bad++; console.log('量词套量词', what, s.slice(0, 90)); }
  if (s.length > 4096 && what.startsWith('规则')) { bad++; console.log('规则太长', what, s.length); }
};
(card.assistantRegexReplace || []).forEach((r, i) => chk('规则#' + i + ' ' + (r.name || ''), r.regex));
const lb = card.prompt.lorebook;
lb.forEach((e, i) => { (e.triggerWords || []).forEach((t) => chk('触发#' + i, t)); (e.blackListWords || []).forEach((t) => chk('黑名单#' + i, t)); });
const lim = (name, v, cap) => { if (v > cap) { bad++; console.log('过上限', name, v, '>', cap); } return name + ' ' + v; };
console.log('查了', n, '条正则，问题', bad);
console.log([lim('世界书条数', lb.length, 99999), lim('优先级最大', Math.max(...lb.map((e) => e.priority || 0)), 8192), lim('一条触发词最多', Math.max(...lb.map((e) => (e.triggerWords || []).length)), 256),
  lim('单条最长', Math.max(...lb.map((e) => (e.content || '').length)), 100000), lim('规则', (card.assistantRegexReplace || []).length, 500), lim('样式', (card.injectStyles || '').length, 2097152),
  lim('主提示词', card.prompt.systemPrompt.length, 98304), lim('后置词', (card.prompt.rearPrompt || '').length, 98304), '介绍页 ' + (card.introPage || '').length, lim('简介', (card.description || '').length, 1024),
  lim('更新说明', (card.changelog || '').length, 2048), lim('快捷键', ((card.options || {}).items || []).length, 50)].join('，'));
process.exit(bad ? 1 : 0);
