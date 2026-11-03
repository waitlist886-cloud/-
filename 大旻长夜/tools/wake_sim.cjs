// 照日里实测的触发规则模拟一轮叫醒哪些世界书条目：扫描深度圈最近 N 条消息，按触发范围挑出玩家或助手的，
// 一条消息一条消息单独判（OR 是这一条里有任一个词，AND 是所有词都在同一条里，黑名单只看同一条）。不算概率。
// 用法：node wake_sim.cjs 卡.json 对话.json [--list]   对话.json：[{role:"user"|"assistant", file:"路径"}…]，最后一条是这一轮玩家的话
const fs = require('fs'), path = require('path');
const [cardPath, convPath, ...flags] = process.argv.slice(2);
const card = JSON.parse(fs.readFileSync(cardPath, 'utf8'));
const conv = JSON.parse(fs.readFileSync(convPath, 'utf8')).map((m) => ({ role: m.role, text: m.text || fs.readFileSync(path.resolve(path.dirname(convPath), m.file), 'utf8') }));
const toRe = (w) => { const m = w.match(/^\/([\s\S]*)\/([a-z]*)$/); return m ? new RegExp(m[1], m[2].replace(/[^imsg]/g, '')) : { test: (t) => t.includes(w) }; };
const lore = card.prompt.lorebook;
const woke = [];
for (const [i, e] of lore.entries()) {
  if (!e.enabled) continue;
  const msgs = conv.slice(-e.scanDepth).filter((m) => e.triggerRange.includes(m.role));
  const tw = e.triggerWords.map(toRe), bl = (e.blackListWords || []).map(toRe);
  const hit = msgs.some((m) => {
    const ok = e.triggerWordsType === 'AND' ? tw.every((r) => r.test(m.text)) : tw.some((r) => r.test(m.text));
    if (!ok) return false;
    if (!bl.length) return true;
    const blocked = (e.blackListWordsType === 'AND') ? bl.every((r) => r.test(m.text)) : bl.some((r) => r.test(m.text));
    return !blocked;
  });
  if (hit) woke.push({ i, folder: e.folder, head: e.content.split('\n').find((l) => l.trim()).slice(0, 34), len: e.content.length, p: e.probability });
}
const byF = {};
for (const w of woke) { byF[w.folder] = byF[w.folder] || { n: 0, len: 0 }; byF[w.folder].n++; byF[w.folder].len += w.len; }
console.log('叫醒 %d 条，正文 %d 字（其中带概率的 %d 条）', woke.length, woke.reduce((a, w) => a + w.len, 0), woke.filter((w) => w.p < 100).length);
for (const [f, v] of Object.entries(byF).sort((a, b) => b[1].len - a[1].len)) console.log('  %s  %d 条  %d 字', f, v.n, v.len);
if (flags.includes('--list')) for (const w of woke) console.log('   #%d %s（%d字%s）', w.i, w.head, w.len, w.p < 100 ? '，概率' + w.p : '');
