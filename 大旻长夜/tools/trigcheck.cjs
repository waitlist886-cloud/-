// 紧凑卡世界书的正则逐条查：Node 里能不能建、过不过 safe-regex、量词多不多、长不长。用法：node trigcheck.cjs 卡.json（safe-regex 从复刻台 tools/rili_bench 的 node_modules 取，在那个目录里跑，或者设 NODE_PATH）
const fs = require('fs'); const safe = require('safe-regex');
const card = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let n = 0, bad = [];
const qcount = (s) => (s.replace(/\\./g, 'x').replace(/\[[^\]]*\]/g, 'C').match(/\{\d*,?\d*\}|[*+?]/g) || []).length;
card.prompt.lorebook.forEach((e, i) => {
  for (const w of [...e.triggerWords, ...e.blackListWords]) {
    const m = w.match(/^\/([\s\S]*)\/([a-z]*)$/); if (!m) continue; n++;
    try { new RegExp(m[1], m[2]); } catch (err) { bad.push(`#${i} 编译失败 ${err.message.slice(0, 60)}`); continue; }
    if (!safe(m[1])) bad.push(`#${i} safe-regex 不过：${m[1].slice(0, 60)}`);
    if (qcount(m[1]) > 25) bad.push(`#${i} 量词 ${qcount(m[1])}`);
    if (m[1].length > 1024) bad.push(`#${i} 太长`);
  }
});
console.log('正则', n, '个，问题', bad.length); bad.slice(0, 20).forEach((b) => console.log(b));
