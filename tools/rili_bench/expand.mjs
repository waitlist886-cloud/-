// 拿规则把一条回复展开，打印结果，并检查记号有没有残留、safe-regex
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { applyRules } from './platform.mjs';
const require = createRequire(import.meta.url);
const safe = require('safe-regex');
const [txtPath, ...rulePaths] = process.argv.slice(2);
let rules = []; for (const p of rulePaths) rules = rules.concat(JSON.parse(fs.readFileSync(p, 'utf8')));
const bad = rules.filter(r => { const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/); return !m || !safe(m[1]); }).map(r => r.name);
console.log('规则', rules.length, '条，safe-regex 不过的：', bad.join('、') || '无');
const out = applyRules(fs.readFileSync(txtPath, 'utf8'), rules);
const left = (out.match(/[ⓔⓩ]|§[^\n<]{0,20}/g) || []);
console.log('残留记号/记录：', left.slice(0, 8));
console.log('换行数', (out.match(/\n/g) || []).length, '长度', out.length);
fs.writeFileSync(txtPath.replace(/\.txt$/, '.expanded.html'), out);
console.log(out.slice(0, 1500));
