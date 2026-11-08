// 一句玩家的话（或者一条回复）叫醒世界书里哪些条目：照平台的算法，触发词 OR/AND、黑名单 OR/AND，只看范围含这一侧的条目，不算深度。
// 用法：node wake_open.mjs 卡.json user|assistant 文件或者文字 …   一条一行报：叫醒几条、多少字、按文件夹数
import fs from 'node:fs';
const [cardPath, side, ...inputs] = process.argv.slice(2);
const lb = JSON.parse(fs.readFileSync(cardPath, 'utf8')).prompt.lorebook;
const mk = (w) => {
  if (w.startsWith('/')) {
    const m = w.match(/^\/([\s\S]*)\/([^/]*)$/);
    try { const re = new RegExp(m[1], m[2].replace(/[^imsu]/g, '')); return (t) => re.test(t); } catch { return () => false; }
  }
  return (t) => t.toLowerCase().includes(w.toLowerCase());
};
const tests = lb.map((e) => ({
  t: (e.triggerWords || []).map(mk), b: (e.blackListWords || []).map(mk), and: e.triggerWordsType === 'AND', band: e.blackListWordsType === 'AND',
  ok: e.enabled !== false && (e.triggerRange || []).includes(side), title: (e.content || '').split('\n')[0].slice(0, 40), len: (e.content || '').length, folder: e.folder || '',
}));
const wake = (txt) => {
  const s = [];
  tests.forEach((x, i) => {
    if (!x.ok || !x.t.length) return;
    const hit = x.and ? x.t.every((f) => f(txt)) : x.t.some((f) => f(txt));
    if (!hit) return;
    const bl = x.b.length && (x.band ? x.b.every((f) => f(txt)) : x.b.some((f) => f(txt)));
    if (!bl) s.push(i);
  });
  return s;
};
for (const inp of inputs) {
  const txt = fs.existsSync(inp) ? fs.readFileSync(inp, 'utf8') : inp;
  const s = wake(txt);
  const byF = {};
  for (const i of s) { const f = tests[i].folder.replace(/^\d+·/, '').slice(0, 10); byF[f] = (byF[f] || 0) + 1; }
  const chars = s.reduce((a, i) => a + tests[i].len, 0);
  console.log('【' + (fs.existsSync(inp) ? inp.split(/[\\/]/).pop() : inp.slice(0, 40)) + '】', s.length, '条', chars, '字', JSON.stringify(byF));
  if (process.env.LIST) for (const i of s) console.log('   #' + i, tests[i].folder.slice(0, 14), tests[i].title);
}
