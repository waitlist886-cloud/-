// 本地干跑·看条目：照卡里的下标（轮N_醒.md 头一栏的 #）把条目正文印出来，带触发设置。
// 用法：node tools/dryrun/show.mjs <下标,下标,…|标题里的字> [max=每条至多印多少字] [card=卡.json] [set=1 只印设置]
import { CARD_FULL, loadCard, titleOf } from './lib.mjs';

const [what, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => { const i = a.indexOf('='); return [a.slice(0, i), a.slice(i + 1)]; }));
const lb = loadCard(opt.card || CARD_FULL).prompt.lorebook;
const ids = /^[\d,]+$/.test(what) ? what.split(',').map(Number) : lb.map((e, i) => (titleOf(e).includes(what) ? i : -1)).filter((i) => i >= 0);
const max = Number(opt.max || 1e9);
for (const i of ids) {
  const e = lb[i];
  if (!e) continue;
  const body = e.contentMethod === 'weighted' ? e.contents.map((c) => `〔${c.probability}%〕${c.content}`).join('\n') : e.content;
  console.log(`━━━ #${i}｜${e.folder}｜优先级 ${e.priority}｜深度 ${e.scanDepth}｜范围 ${e.triggerRange.join('+')}｜${e.triggerWordsType}｜概率 ${e.probability}｜${body.length} 字 ━━━`);
  console.log('触发：' + e.triggerWords.map((w) => w.slice(0, 300)).join(' ‖ '));
  if ((e.blackListWords || []).length) console.log('黑名单：' + e.blackListWords.map((w) => w.slice(0, 200)).join(' ‖ '));
  if (!opt.set) console.log(body.length > max ? body.slice(0, max) + `\n……（后面还有 ${body.length - max} 字）` : body);
  console.log('');
}
