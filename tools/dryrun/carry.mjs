// 本地干跑·照抄：骨架要每轮把没变的行照抄上一轮。当主持写第二轮以后的回复时，没变的行不用手抄，草稿里写记号，这一支照上一轮的回复补成整条。
// 用法：node tools/dryrun/carry.mjs <局目录> <轮号>      读 轮N_回复.草稿.txt 和 轮N-1_回复.txt，写 轮N_回复.txt（整条，跟模型自己一行行抄出来的一样）
// 草稿里的记号（单独占一行）：
//   @@抄 <行首的字>            上一轮回复里以这几个字开头的行，原样照次序抄过来。例：@@抄 §装备｜   @@抄 §记忆｜短期｜
//   @@抄组 <全名>              上一轮 §角色｜全名 那一组（到下一个 §角色｜、§宠｜、§见闻｜ 为止）整组抄过来
//   @@改 <整行>                只跟在 @@抄组 或 @@抄 后头：把刚抄来的行里名目相同的那一行换成这一行
//                              （§角色行｜X｜、§角色细｜X｜、§面板｜X｜、§能力｜类｜名｜、§装备｜部位｜、§物品｜类｜名 认到这一层，别的认到头一个｜）
//   @@添 <整行>                只跟在 @@抄组 后头：在那一组的 §角色行｜状态｜ 后头添一行（§角色行｜此刻｜ 用），组里没有状态行就添在组尾
// 别的行原样留着。记号用完了没对上的会报出来。
import fs from 'node:fs';
import path from 'node:path';
import { readText } from './lib.mjs';

const [runDir, nStr] = process.argv.slice(2);
const N = Number(nStr);
const prev = readText(path.join(runDir, `轮${N - 1}_回复.txt`)).split('\n');
const draft = readText(path.join(runDir, `轮${N}_回复.草稿.txt`)).split('\n');
const keyOf = (l) => {
  let m = l.match(/^(§(?:角色行|角色细|面板)｜[^｜\n]+)(?:｜|$)/);
  if (m) return m[1];
  m = l.match(/^(§(?:能力|物品)｜[^｜\n]+｜[^｜×\n]+)/);
  if (m) return m[1];
  m = l.match(/^(§装备｜[^｜\n]+)/);
  if (m) return m[1];
  m = l.match(/^(§[^｜\n]+)/);
  return m ? m[1] : l;
};
const out = [];
let last = null;   // 刚抄来的那一段在 out 里的起止
const bad = [];
for (const l of draft) {
  if (l.startsWith('@@抄组 ')) {
    const name = l.slice(4).trim();
    const s = prev.findIndex((x) => x.startsWith('§角色｜' + name + '｜'));
    if (s < 0) { bad.push('上一轮没有这一组：' + name); last = null; continue; }
    let e = s + 1;
    while (e < prev.length && !/^§(?:角色｜|宠｜|见闻｜|MOD｜|记忆｜|预载｜)/.test(prev[e])) e++;
    last = [out.length, out.length + (e - s)];
    out.push(...prev.slice(s, e));
    continue;
  }
  if (l.startsWith('@@抄 ')) {
    const pre = l.slice(4);
    const got = prev.filter((x) => x.startsWith(pre));
    if (!got.length) bad.push('上一轮没有以这几个字开头的行：' + pre);
    last = [out.length, out.length + got.length];
    out.push(...got);
    continue;
  }
  if (l.startsWith('@@改 ')) {
    const line = l.slice(4);
    const k = keyOf(line);
    let hit = -1;
    if (last) for (let i = last[0]; i < last[1]; i++) if (keyOf(out[i]) === k) { hit = i; break; }
    if (hit < 0) bad.push('@@改 没对上：' + line.slice(0, 40));
    else out[hit] = line;
    continue;
  }
  if (l.startsWith('@@添 ')) {
    const line = l.slice(4);
    if (!last) { bad.push('@@添 前头没有 @@抄组：' + line.slice(0, 40)); continue; }
    let at = -1;
    for (let i = last[0]; i < last[1]; i++) if (out[i].startsWith('§角色行｜状态｜')) at = i + 1;
    if (at < 0) at = last[1];
    out.splice(at, 0, line);
    last[1]++;
    continue;
  }
  if (l.startsWith('@@')) { bad.push('不认得的记号：' + l.slice(0, 40)); continue; }
  last = null;
  out.push(l);
}
fs.writeFileSync(path.join(runDir, `轮${N}_回复.txt`), out.join('\n').replace(/\n+$/, '') + '\n');
console.log(`轮${N}_回复.txt ${out.length} 行 ${out.join('\n').length} 字` + (bad.length ? '\n有毛病：\n  ' + bad.join('\n  ') : ''));
