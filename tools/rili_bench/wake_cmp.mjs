// 同一条回复的两种写法，各叫醒世界书里哪些「范围含助手」的条目（单条消息，不带开局口令，不算深度）
import fs from 'node:fs';
const [cardPath, a, b] = process.argv.slice(2);
const lb = JSON.parse(fs.readFileSync(cardPath, 'utf8')).prompt.lorebook;
const mk = (w) => { if (w.startsWith('/')) { const m = w.match(/^\/([\s\S]*)\/([^/]*)$/); try { const re = new RegExp(m[1], m[2].replace(/[^imsu]/g, '')); return (t) => re.test(t); } catch { return () => false; } } return (t) => t.includes(w); };
const tests = lb.map((e) => ({ t: e.triggerWords.map(mk), b: e.blackListWords.map(mk), and: e.triggerWordsType === 'AND', band: e.blackListWordsType === 'AND', ok: (e.triggerRange || []).includes('assistant'), title: e.content.split('\n')[0].slice(0, 46) }));
const wake = (txt) => { const s = new Set(); tests.forEach((x, i) => { if (!x.ok || !x.t.length) return; const hit = x.and ? x.t.every((f) => f(txt)) : x.t.some((f) => f(txt)); if (!hit) return; const bl = x.b.length && (x.band ? x.b.every((f) => f(txt)) : x.b.some((f) => f(txt))); if (bl) return; s.add(i); }); return s; };
const A = wake(fs.readFileSync(a, 'utf8')), B = wake(fs.readFileSync(b, 'utf8'));
const onlyA = [...A].filter((i) => !B.has(i)), onlyB = [...B].filter((i) => !A.has(i));
console.log('HTML 版叫醒', A.size, '条，紧凑版叫醒', B.size, '条，两边都醒', [...A].filter((i) => B.has(i)).length);
console.log('只在 HTML 版醒的：'); onlyA.forEach((i) => console.log('  #' + i, lb[i].folder.slice(0, 14), tests[i].title));
console.log('只在紧凑版醒的：'); onlyB.forEach((i) => console.log('  #' + i, lb[i].folder.slice(0, 14), tests[i].title));
