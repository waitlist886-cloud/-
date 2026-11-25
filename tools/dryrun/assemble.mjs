// 本地干跑·拼提示词：给一局的目录和轮号，出这一轮平台会发给模型的全文，报醒了哪些条目。
// 用法：node tools/dryrun/assemble.mjs <局目录> <轮号> [card=卡.json] [base=本体卡.json|none] [seed=字] [tag=字] [why=条目标题里的字,字] [quiet=1]
//   局目录里放 轮1_玩家.txt（头一轮是建档凭证）、轮1_回复.txt、轮2_玩家.txt……第 N 轮要有 轮1..N 的玩家、轮1..N-1 的回复。
//   写出：轮N_全文.txt（发给模型的全文）、轮N_醒.md（醒了哪些、谁叫醒的、中的哪个字）、轮N_新醒.txt（上一轮没醒、这一轮新醒的条目正文）、
//         轮N_睡回去.txt（上一轮醒着这一轮没醒的）、轮N_醒.json，并把这一轮的数记进 汇总.json。
//   card 默认是全本（本体加七包 DLC）；base 默认是切过 DLC 的本体，拿来标哪些条目是 DLC 才有的。base=none 不标。
//   tag=字：换一张卡对比着跑的时候用（比如 card=本体 tag=本体），只写 轮N_全文_字.txt、轮N_醒_字.md，汇总里记成 轮N_字。
//   why=字：不拼全文，只把标题里带这几个字的条目在这一轮为什么醒、为什么不醒逐词列出来。
import fs from 'node:fs';
import path from 'node:path';
import { CARD_FULL, CARD_BASE, readText, loadCard, titleOf, applyRules, wakeEntry, rng32, kindOf, unsafe, eraOf, madeFor } from './lib.mjs';

const [runDir, nStr, ...rest] = process.argv.slice(2);
if (!runDir || !nStr) { console.log('用法：node tools/dryrun/assemble.mjs <局目录> <轮号> [card=] [base=] [seed=] [tag=] [why=] [quiet=1]'); process.exit(1); }
const opt = Object.fromEntries(rest.map((a) => { const i = a.indexOf('='); return [a.slice(0, i), a.slice(i + 1)]; }));
const N = Number(nStr);
const cardPath = opt.card || CARD_FULL;
const card = loadCard(cardPath);
const P = card.prompt;
const lb = P.lorebook;
const rules = card.assistantRegexReplace || [];
const sfx = opt.tag ? '_' + opt.tag : '';

// ---- 哪些条目是 DLC 才有的（全本有、本体没有）
const dlc = new Set();
if ((opt.base || '') !== 'none') {
  const bp = opt.base || CARD_BASE;
  if (fs.existsSync(bp) && path.resolve(bp) !== path.resolve(cardPath)) {
    const key = (e) => (e.folder || '') + '\u0001' + (e.content || JSON.stringify(e.contents || ''));
    const have = new Set(loadCard(bp).prompt.lorebook.map(key));
    lb.forEach((e, i) => { if (!have.has(key(e))) dlc.add(i); });
  }
}

// ---- 这一轮以前的消息
const msgs = [];
for (let k = 1; k <= N; k++) {
  const u = path.join(runDir, `轮${k}_玩家.txt`);
  if (!fs.existsSync(u)) { console.error('缺', u); process.exit(1); }
  msgs.push({ role: 'user', raw: readText(u).trim(), label: k === N ? '玩家·这一轮' : `玩家·第${k}轮` });
  if (k < N) {
    const a = path.join(runDir, `轮${k}_回复.txt`);
    if (!fs.existsSync(a)) { console.error('缺', a); process.exit(1); }
    msgs.push({ role: 'assistant', raw: readText(a).trim(), label: k === N - 1 ? '回复·上一轮' : `回复·第${k}轮` });
  }
}
for (const m of msgs) m.text = m.role === 'assistant' ? applyRules(m.raw, rules, 'back-end') : m.raw;

// ---- why：只解释
if (opt.why) {
  const keys = opt.why.split(',');
  lb.forEach((e, i) => {
    const t = titleOf(e);
    if (!keys.some((k) => t.includes(k))) return;
    console.log(`\n#${i} [${e.folder}] ${t}｜优先级 ${e.priority} 深度 ${e.scanDepth} 范围 ${e.triggerRange.join('+')} ${e.triggerWordsType}${dlc.has(i) ? '｜DLC' : ''}`);
    for (const d of wakeEntry(e, msgs, true)) {
      if (d.skip) { console.log('  ' + d.label + '：' + d.skip); continue; }
      console.log('  ' + d.label + '：' + (d.woke ? '醒' : '不醒') + (d.black ? '（黑名单中：' + d.black.join('、') + '）' : ''));
      for (const w of d.words) console.log('     ' + (w.hit ? '✓ ' + JSON.stringify(w.hit) : '✗') + '  ' + w.w);
    }
    if ((e.blackListWords || []).length) console.log('  黑名单：' + e.blackListWords.map((w) => w.slice(0, 90)).join(' ｜ '));
  });
  process.exit(0);
}

// ---- 醒
const rnd = rng32(opt.seed || (path.basename(path.resolve(runDir)) + '#' + N));
const game = eraOf(msgs[0].raw);
const woke = [];
const warn = [];
lb.forEach((e, i) => {
  const r = wakeEntry(e, msgs);
  if (!r) return;
  if ((e.probability ?? 100) < 100 && rnd() * 100 >= e.probability) { warn.push(`概率 ${e.probability}% 这一轮没掷中：${titleOf(e)}`); return; }
  let content = e.content || '';
  if (e.contentMethod === 'weighted') {
    const cs = e.contents || [];
    let x = rnd() * cs.reduce((a, c) => a + c.probability, 0);
    let pick = cs[cs.length - 1];
    for (const c of cs) { x -= c.probability; if (x < 0) { pick = c; break; } }
    content = pick.content;
  }
  for (const w of [...(e.triggerWords || []), ...(e.blackListWords || [])]) { const u = unsafe(w); if (u) warn.push(`触发词可能叫平台丢掉（${u}）：#${i} ${titleOf(e)}｜${w.slice(0, 70)}`); }
  const era = madeFor(e);
  woke.push({ i, e, content, why: r, kind: kindOf(e), dlc: dlc.has(i), era, wrong: era !== '通用' && era !== game.tag });
});
woke.sort((a, b) => (a.e.priority - b.e.priority) || (a.i - b.i));

// ---- 拼
const sysEntries = woke.filter((w) => (w.e.impactRange || ['system']).includes('system'));
const headEntries = woke.filter((w) => (w.e.impactRange || []).includes('headPrompt'));
const rearEntries = woke.filter((w) => (w.e.impactRange || []).includes('rearPrompt'));
const cur = msgs[msgs.length - 1];
const userBlock = (P.headPrompt || '') + headEntries.map((w) => w.content + '\n').join('') + cur.text + (P.rearPrompt ? '\n\n' + P.rearPrompt : '') + rearEntries.map((w) => '\n' + w.content).join('');
const sysBlock = [P.systemPrompt, ...sysEntries.map((w) => w.content)].join('\n\n');
const bar = (s) => `\n\n━━━━━━━━━━━━━━━━━━━━ ${s} ━━━━━━━━━━━━━━━━━━━━\n\n`;
let full = bar('系统（主提示词，后头接醒了的世界书条目，优先级小的在前）') + sysBlock;
for (const m of msgs.slice(0, -1)) full += bar(m.role === 'user' ? '历史·' + m.label : '历史·' + m.label + '（过了「应用到全部」的正则）') + m.text;
full += bar('玩家这一轮（前置词＋玩家的话＋后置词）') + userBlock + '\n';
fs.writeFileSync(path.join(runDir, `轮${N}_全文${sfx}.txt`), full);

// ---- 新醒的、睡回去的（只在不带 tag 的正式那一遍记）
if (!opt.tag) {
  const prevPath = path.join(runDir, `轮${N - 1}_醒.json`);
  const prev = new Set(fs.existsSync(prevPath) ? JSON.parse(fs.readFileSync(prevPath, 'utf8')).map((x) => x.i) : []);
  fs.writeFileSync(path.join(runDir, `轮${N}_醒.json`), JSON.stringify(woke.map((w) => ({ i: w.i, t: titleOf(w.e), f: w.e.folder, n: w.content.length, kind: w.kind, dlc: w.dlc, era: w.era, wrong: w.wrong, by: w.why.by, hit: w.why.hits.map((h) => h.hit) }))));
  const always = (w) => w.e.triggerWords.length === 1 && w.e.triggerWords[0] === '/^/';
  const fresh = woke.filter((w) => !prev.has(w.i) || always(w) || w.e.contentMethod === 'weighted');
  fs.writeFileSync(path.join(runDir, `轮${N}_新醒.txt`), fresh.map((w) => `━━━ #${w.i}｜${w.e.folder}｜${w.content.length} 字${w.dlc ? '｜DLC' : ''}${w.wrong ? '｜别纪：' + w.era : ''}｜${w.why.by} ━━━\n${w.content}`).join('\n\n') + '\n');
  const gone = [...prev].filter((i) => !woke.some((w) => w.i === i));
  fs.writeFileSync(path.join(runDir, `轮${N}_睡回去.txt`), gone.map((i) => `#${i}｜${lb[i].folder}｜${titleOf(lb[i])}`).join('\n') + '\n');
}

// ---- 报
const sum = (a) => a.reduce((x, w) => x + w.content.length, 0);
const fixed = (P.systemPrompt || '').length + (P.headPrompt || '').length + (P.rearPrompt || '').length;
const res = woke.filter((w) => w.kind !== '话题');
const top = woke.filter((w) => w.kind === '话题');
const hist = msgs.slice(0, -1).reduce((a, m) => a + m.text.length, 0);
const cnt = (f) => woke.filter(f).length;
const stat = {
  轮: N, 这一局: game.tag, 卡: path.basename(cardPath), 总字数: full.length, 固定_主提示词前后置: fixed, 常驻条数: res.length, 常驻字数: sum(res), 话题条数: top.length, 话题字数: sum(top),
  其中DLC条数: cnt((w) => w.dlc), 其中DLC字数: sum(woke.filter((w) => w.dlc)), 别纪条数: cnt((w) => w.wrong), 别纪字数: sum(woke.filter((w) => w.wrong)), 历史字数: hist, 玩家这一句: cur.text.length,
};
const byF = {};
for (const w of woke) { const f = w.e.folder || '（无）'; byF[f] = byF[f] || { n: 0, c: 0 }; byF[f].n++; byF[f].c += w.content.length; }
const folders = Object.entries(byF).sort((a, b) => a[0].localeCompare(b[0], 'zh'));
stat.按文件夹 = Object.fromEntries(folders.map(([k, v]) => [k, v.n + '条/' + v.c + '字']));

const cell = (s) => String(s).replace(/\|/g, '｜').replace(/`/g, "'");
let md = `# 第 ${N} 轮醒了什么（${path.basename(path.resolve(runDir))}${opt.tag ? '，' + opt.tag : ''}）\n\n卡：${path.basename(cardPath)}（世界书 ${lb.length} 条）\n\n`;
md += `- 发给模型的全文 ${full.length} 字：主提示词 ${P.systemPrompt.length}、前置词 ${(P.headPrompt || '').length}、后置词 ${(P.rearPrompt || '').length}、常驻条目 ${res.length} 条 ${sum(res)} 字（各纪常驻与时钟、骰表、命运骰）、话题条目 ${top.length} 条 ${sum(top)} 字、历史 ${hist} 字、玩家这一句 ${cur.text.length} 字\n`;
md += `- 醒了的里头 DLC 才有的 ${stat.其中DLC条数} 条 ${stat.其中DLC字数} 字\n`;
md += `- 这一局是 ${game.tag}；给别的纪写的条目醒了 ${stat.别纪条数} 条 ${stat.别纪字数} 字（表里「类」那一栏带「别纪」的；底卡里写 1001 年今天样子的那几组也算，粗分，要逐条看）\n\n## 按文件夹\n\n| 文件夹 | 条 | 字 |\n|---|---|---|\n`;
for (const [k, v] of folders) md += `| ${k} | ${v.n} | ${v.c} |\n`;
md += `\n## 逐条（照发给模型的次序）\n\n| # | 优先级 | 类 | 文件夹 | 标题 | 字 | 叫醒它的消息 | 中的字 |\n|---|---|---|---|---|---|---|---|\n`;
for (const w of woke) md += `| ${w.i} | ${w.e.priority} | ${w.kind}${w.dlc ? '·DLC' : ''}${w.wrong ? '·别纪' + w.era : ''} | ${w.e.folder} | ${cell(titleOf(w.e))} | ${w.content.length} | ${w.why.by} | ${w.why.hits.map((h) => '`' + cell(h.hit) + '`').join(' ＋ ')} |\n`;
if (warn.length) md += `\n## 提醒\n\n` + [...new Set(warn)].map((x) => '- ' + x).join('\n') + '\n';
fs.writeFileSync(path.join(runDir, `轮${N}_醒${sfx}.md`), md);
const sumPath = path.join(runDir, '汇总.json');
const all = fs.existsSync(sumPath) ? JSON.parse(fs.readFileSync(sumPath, 'utf8')) : {};
all['轮' + N + sfx] = stat;
fs.writeFileSync(sumPath, JSON.stringify(all, null, 1));
if (!opt.quiet) {
  console.log(`第 ${N} 轮（${game.tag}）：全文 ${full.length} 字｜主提示词等 ${fixed}｜常驻 ${res.length} 条 ${sum(res)} 字｜话题 ${top.length} 条 ${sum(top)} 字（DLC ${stat.其中DLC条数} 条 ${stat.其中DLC字数} 字，别纪 ${stat.别纪条数} 条 ${stat.别纪字数} 字）｜历史 ${hist} 字`);
  if (!opt.brief) for (const [k, v] of folders) console.log('   ' + String(v.n).padStart(3) + ' 条 ' + String(v.c).padStart(6) + ' 字  ' + k);
  if (warn.length) console.log('提醒 ' + [...new Set(warn)].length + ' 条，见 轮' + N + '_醒' + sfx + '.md');
}
