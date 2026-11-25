// 本地干跑的公用部分：照日里平台的做法判世界书条目醒不醒、把显示正则套到回复上。
// 平台的口径都是仓库里以前探针量出来的（canon/README.md 探针三 10-13、交接存档 11-08 第 8 条、11-10 探针），这里一条一条照搬：
//   · 一条消息一条消息分开扫：AND 不跨消息，不拼接，黑名单只挡同一条消息里的字。
//   · 扫描深度 N＝往回看 N 条消息（玩家这一条算第 1 条，上一条回复第 2 条……），深度 1 看不到上一条回复；深度 0 当 3。
//   · 触发范围 user／assistant 只扫那一种角色的消息；前置词、后置词不算玩家这一句。
//   · 纯词按子串、分大小写；/…/flags 是 JS 正则，flags 只认 i m s g。
//   · 「应用到全部」的显示正则先改过 AI 的话，世界书扫的、下一轮发给模型的都是改过以后的字；「仅显示」的只管页面。
//   · 加权条目每轮重抽一条；触发概率照掷。
//   · 多条同时醒，优先级数小的在前。
// 没量过、这里照最自然的读法定的（README 里也写了）：条目正文接在主提示词后头、中间空一行；历史全带；条目醒了没有总量上限。
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const HERE = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(HERE, '..', '..');
export const CARD_FULL = path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框_原介绍页_全本.json');
export const CARD_BASE = path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框_原介绍页.json');

export const readText = (f) => fs.readFileSync(f, 'utf8').replace(/^﻿/, '').split('\r').join('');
export const loadCard = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
export const titleOf = (e) => ((e.content || (e.contents && e.contents[0] && e.contents[0].content) || '').split('\n')[0] || '').replace(/^#+\s*/, '').slice(0, 60);

// ---- 显示正则（tools/rili_bench/platform.mjs 的 applyRules 原样）：side='front-end' 是页面看到的，side='back-end' 是存进历史、发给模型、世界书扫的
export function applyRules(text, rules, side = 'front-end', role = 'assistant') {
  for (const r of rules) {
    if (r.enabled === false) continue;
    if (r.messageRole !== 'all' && r.messageRole !== role) continue;
    if (r.applyMode !== 'all' && r.applyMode !== side) continue;
    const m = r.regex.startsWith('/') ? r.regex.match(/^\/([\s\S]*)\/([^/]*)$/) : null;
    if (m) text = text.replace(new RegExp(m[1], [...m[2]].filter((f) => 'imsg'.includes(f)).join('')), r.replaceString);
    else text = text.split(r.regex).join(r.replaceString);
  }
  return text;
}

// ---- 触发词
const cache = new Map();
export function matcher(w) {
  let f = cache.get(w);
  if (f) return f;
  const m = w.startsWith('/') ? w.match(/^\/([\s\S]*)\/([^/]*)$/) : null;
  if (m) {
    let re = null;
    try { re = new RegExp(m[1], [...m[2]].filter((x) => 'ims'.includes(x)).join('')); } catch { re = null; }
    f = re ? (t) => { const r = re.exec(t); return r ? { hit: r[0], at: r.index } : null; } : () => null;
  } else {
    f = (t) => { const i = t.indexOf(w); return i < 0 ? null : { hit: w, at: i }; };
  }
  cache.set(w, f);
  return f;
}
// 照 safe-regex 的口径粗查（tools/rili_bench/check_card.mjs 的 nested 搬过来）：量词套量词、量词过 25 个的，平台会悄悄换成永不命中
export function unsafe(w) {
  const m = w.startsWith('/') ? w.match(/^\/([\s\S]*)\/([^/]*)$/) : null;
  if (!m) return null;
  const src = m[1];
  try { new RegExp(src); } catch (e) { return '编不过：' + e.message; }
  const q = (src.replace(/\\./g, 'x').replace(/\[(?:\\.|[^\]])*\]/g, 'x').replace(/\(\?[:=!]/g, '(').match(/[*+?]|\{\d/g) || []).length;
  if (q > 25) return '量词 ' + q + ' 个，过 25';
  const st = [{ q: false }];
  let i = 0;
  const isQ = (k) => '*+?'.includes(src[k]) || (src[k] === '{' && /^\{\d/.test(src.slice(k)));
  while (i < src.length) {
    const c = src[i];
    if (c === '\\') { i += 2; if (i < src.length && isQ(i)) st[st.length - 1].q = true; continue; }
    if (c === '[') { i++; if (src[i] === '^') i++; if (src[i] === ']') i++; while (i < src.length && src[i] !== ']') { if (src[i] === '\\') i++; i++; } i++; if (isQ(i)) st[st.length - 1].q = true; continue; }
    if (c === '(') { st.push({ q: false }); i++; if (src[i] === '?') i += 2; continue; }
    if (c === ')') { const g = st.length > 1 ? st.pop() : { q: false }; i++; if (isQ(i)) { if (g.q) return '量词套量词'; st[st.length - 1].q = true; } else if (g.q) st[st.length - 1].q = true; continue; }
    if (isQ(i)) { st[st.length - 1].q = true; if (src[i] === '{') { while (i < src.length && src[i] !== '}') i++; } i++; continue; }
    i++;
  }
  return null;
}

// 中的字太长（预载那一类正则从消息开头一路吃到名字），只留末尾，名字就在末尾
const clip = (t) => (t.length > 36 ? '…' + t.slice(-22) : t).replace(/\n/g, '⏎');
function hitList(words, typ, text) {
  if (!words || !words.length) return null;
  const res = words.map((w) => matcher(w)(text));
  if ((typ || 'OR') === 'AND') return res.every(Boolean) ? res : null;
  const first = res.findIndex(Boolean);
  return first < 0 ? null : [res[first]];
}

// msgs：[{role:'user'|'assistant', text, label}]，末一条是玩家这一轮的话；assistant 的 text 要先过 back-end 那一路的正则
// 醒了返回 {by: 哪一条消息, role, hits:[{hit}]}，没醒返回 null。why=true 时返回每条消息、每个词的详情
export function wakeEntry(e, msgs, why = false) {
  if (e.enabled === false) return null;
  const depth = e.scanDepth === 0 ? 3 : (e.scanDepth || 1);
  const win = msgs.slice(-depth).reverse();   // 近的在前
  const rng = e.triggerRange || [];
  const detail = [];
  for (const m of win) {
    if (!rng.includes(m.role)) { if (why) detail.push({ label: m.label, skip: '范围不含' + m.role }); continue; }
    const h = hitList(e.triggerWords, e.triggerWordsType, m.text);
    const b = h ? hitList(e.blackListWords, e.blackListWordsType, m.text) : null;
    if (why) {
      detail.push({ label: m.label, words: (e.triggerWords || []).map((w) => { const r = matcher(w)(m.text); return { w: w.slice(0, 110), hit: r ? clip(r.hit) : null }; }), black: b ? b.map((x) => clip(x.hit)) : null, woke: !!(h && !b) });
      continue;
    }
    if (h && !b) return { by: m.label, role: m.role, hits: h.map((x) => ({ hit: clip(x.hit) })) };
  }
  return why ? detail : null;
}

export function rng32(seedStr) {
  let h = 1779033703 ^ seedStr.length;
  for (let i = 0; i < seedStr.length; i++) { h = Math.imul(h ^ seedStr.charCodeAt(i), 3432918353); h = (h << 13) | (h >>> 19); }
  let a = h >>> 0;
  return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

// 这一局是哪一纪（看头一条玩家消息的头一行；没写纪元的照迷宫纪 1001 年）
export function eraOf(firstUser) {
  const m = firstUser.match(/纪元：(月银纪|纷争纪|山铜纪|迷宫纪)(元|\d+)?/);
  if (!m) return { era: '迷宫纪', y: 1001, tag: '1001' };
  const y = m[2] === '元' ? 1 : Number(m[2] || 0);
  return { era: m[1], y, tag: m[1] === '迷宫纪' ? (y >= 1001 ? '1001' : '前传') : m[1] };
}
// 条目是给哪一纪写的：40 号以后的文件夹名里带纪名（迷宫纪＝前传，1001 年的常驻那一条除外）；00 到 28 是底卡，写的是 1001 年今天的样子，
// 里头核心运行、建档、数值、命路、命星、种族、职业、货币装备、队伍羁绊这几组当通用规则，别的（历史、真相、神祇、势力、地点、人物、公会迷宫、怪物、委托、主线、时钟）只该在 1001 年的局里用。
// 这是粗分，报出来的「别纪」要逐条看：有的底卡条目本来就打算四纪共用。
const BASE_GENERIC = /^(?:00|01|05|06|07|08|09|10|20)·/;
export function madeFor(e) {
  const f = e.folder || '';
  const m = f.match(/^(\d\d)·(?:(月银纪|纷争纪|山铜纪|迷宫纪)｜)?/);
  if (!m) return '通用';
  const no = Number(m[1]);
  if (no >= 90) return '通用';
  if (no >= 40) {
    if (m[2] === '迷宫纪') return /这一局在迷宫纪1001年/.test((e.content || '').split('\n')[0]) ? '1001' : '前传';
    return m[2] || '通用';
  }
  return BASE_GENERIC.test(f) ? '通用' : '1001';
}

// 条目归哪一类：固定的不在这里；这里分 常驻（各纪常驻与时钟、只挂 /^/ 的命运骰和骰牌）、骰表（各纪骰表）和 话题
export function kindOf(e) {
  const f = e.folder || '';
  if (/^40·/.test(f)) return '常驻';
  if ((e.triggerWords || []).length === 1 && e.triggerWords[0] === '/^/') return '常驻';
  if (/^60·.*骰表/.test(f)) return '骰表';
  return '话题';
}
