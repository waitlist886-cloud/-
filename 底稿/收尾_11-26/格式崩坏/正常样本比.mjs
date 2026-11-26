// 现成的正常样本（大框、第三轮的样本，干跑十五轮回复），现行全本卡和另一张卡展开（front-end 和 back-end 两路）一字不差吗
// 用法：node 正常样本比.mjs <另一张卡.json>
import fs from 'node:fs'; import path from 'node:path';
const { loadCard, readText, applyRules } = await import('file:///E:/aldran_art/tools/dryrun/lib.mjs');
const A = loadCard('E:/aldran_art/out/发布卡_四纪大框/奥尔德兰_四纪大框_原介绍页_全本.json').assistantRegexReplace;
const B = loadCard(process.argv[2] || 'card_new.json').assistantRegexReplace;
const files = [];
for (const d of ['E:/aldran_art/底稿/状态栏/大框', 'E:/aldran_art/底稿/状态栏/大框/第三轮']) for (const f of fs.readdirSync(d)) if (/^样本.*\.txt$/.test(f)) files.push(path.join(d, f));
for (const d of fs.readdirSync('E:/aldran_art/tools/dryrun/runs')) for (const f of fs.readdirSync('E:/aldran_art/tools/dryrun/runs/' + d)) if (/^轮\d_回复\.txt$/.test(f)) files.push(`E:/aldran_art/tools/dryrun/runs/${d}/${f}`);
let same = 0, diff = [];
for (const f of files) {
  const t = readText(f);
  const a = applyRules(t, A, 'front-end'), b = applyRules(t, B, 'front-end');
  const a2 = applyRules(t, A, 'back-end'), b2 = applyRules(t, B, 'back-end');
  if (a === b && a2 === b2) same++;
  else { let i = 0; while (a[i] === b[i]) i++; diff.push([path.basename(path.dirname(f)) + '/' + path.basename(f), a2 === b2 ? '' : '（发给模型的也变了）', JSON.stringify(a.slice(Math.max(0, i - 60), i + 80)), JSON.stringify(b.slice(Math.max(0, i - 60), i + 80))]); }
}
console.log('样本', files.length, '一字不差', same, '不一样', diff.length);
for (const d of diff) console.log(d.join('\n  '));
