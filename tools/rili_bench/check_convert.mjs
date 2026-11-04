// 旧版 HTML 回复过转换规则的结果：还剩不剩标签和记号，记录有几行，认不出落成了几行。
// 用法：node check_convert.mjs rules_convert.json 输出目录 回复1 回复2 …（转完的写进输出目录，文件名不变，后缀 .txt）
import fs from 'node:fs';
import path from 'node:path';
const rules = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = process.argv[3];
fs.mkdirSync(out, { recursive: true });
const apply = (t) => {
  for (const r of rules) {
    const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
    t = t.replace(new RegExp(m[1], m[2]), r.replaceString);
  }
  return t;
};
for (const f of process.argv.slice(4)) {
  const src = fs.readFileSync(f, 'utf8');
  const t0 = Date.now();
  const t = apply(src);
  const ms = Date.now() - t0;
  const name = path.basename(f).replace(/\.[^.]+$/, '');
  fs.writeFileSync(path.join(out, name + '.txt'), t);
  const kinds = {};
  for (const m of t.matchAll(/^§([^｜\n]{1,8})/gm)) kinds[m[1]] = (kinds[m[1]] || 0) + 1;
  const stray = t.split('\n').filter((l) => /[｜]/.test(l) && !l.startsWith('§'));
  console.log(name, '原', src.length, '转后', t.length, ms + 'ms', '标签', (t.match(/<[a-zA-Z/][^>]*>/g) || []).length, '记号', (t.match(/[ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ]/g) || []).length);
  console.log('  ', JSON.stringify(kinds));
  const tags = t.match(/<[a-zA-Z/][^>]{0,60}>/g); if (tags) console.log('   标签', tags.slice(0, 6));
  if (stray.length) console.log('   带竖线的散行', stray.length, stray.slice(0, 3).map((s) => s.slice(0, 60)));
  const other = t.match(/^§MOD｜记录[^\n]{0,60}/gm); if (other) console.log('   认不出', other.length, other.slice(0, 6));
}
