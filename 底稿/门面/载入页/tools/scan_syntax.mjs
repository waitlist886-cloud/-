// 11-27 止血那一轮：查脚本里老内核（安卓系统 WebView 七八十版）不认的写法。acorn 按 ES2018 解析，再列出 ?.、??、类字段这些新语法和 replaceAll、.at()、fromEntries 这些新方法。
// 用法：在一个临时目录 npm install acorn@8.11.3，把这一份拷过去，node scan_syntax.mjs <文件…>（.js 整份查，.html 查内联脚本）。
import fs from 'node:fs';
import path from 'node:path';
import * as acorn from 'acorn';
const files = process.argv.slice(2);
const API = [[/\.replaceAll\(/, 'replaceAll（Chrome 85）'], [/\.at\(\s*-?\d/, '.at()（Chrome 92）'], [/\bObject\.fromEntries\b/, 'Object.fromEntries（Chrome 73）'], [/\.flatMap\(|\.flat\(/, 'flat/flatMap（Chrome 69）'], [/\bPromise\.allSettled\b/, 'allSettled（76）'], [/\bPromise\.any\b/, 'Promise.any（85）'], [/\bglobalThis\b/, 'globalThis（71）'], [/\.matchAll\(/, 'matchAll（73）'], [/\bObject\.hasOwn\b/, 'Object.hasOwn（93）'], [/\bstructuredClone\b/, 'structuredClone（98）'], [/\.findLast(Index)?\(/, 'findLast（97）'], [/\bqueueMicrotask\b/, 'queueMicrotask（71）'], [/\.trimStart\(|\.trimEnd\(/, 'trimStart（66）'], [/\bAbortController\b/, 'AbortController（66）'], [/\bResizeObserver\b/, 'ResizeObserver（64）'], [/\bIntersectionObserver\b/, 'IntersectionObserver（58）'], [/\.replaceChildren\(/, 'replaceChildren（86）'], [/\.toggleAttribute\(/, 'toggleAttribute（69）'], [/\bcreateImageBitmap\b/, 'createImageBitmap'], [/\bOffscreenCanvas\b/, 'OffscreenCanvas（69）'], [/\bnew Intl\.Segmenter\b/, 'Intl.Segmenter（87）'], [/\.animate\(/, 'el.animate（WAAPI，Chrome 36，finished 84）'], [/\.finished\b/, 'Animation.finished（84）'], [/\bpadStart\b|\bpadEnd\b/, 'padStart（57）']];
function chunks(f) {
  const s = fs.readFileSync(f, 'utf8');
  if (!/\.html?$/.test(f)) return [{ code: s, line0: 0 }];
  const out = []; const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi; let m;
  while ((m = re.exec(s))) { const attrs = m[1]; if (/\bsrc=/.test(attrs) || /type=["']?(application\/(ld\+)?json|text\/template|text\/x-)/i.test(attrs)) continue; out.push({ code: m[2], line0: s.slice(0, m.index).split('\n').length - 1, module: /type=["']?module/.test(attrs) }); }
  return out;
}
const isNew = (n) => {
  switch (n.type) {
    case 'ChainExpression': return '可选链 ?.（Chrome 80）';
    case 'LogicalExpression': return n.operator === '??' ? '空值合并 ??（Chrome 80）' : '';
    case 'AssignmentExpression': return ['??=', '||=', '&&='].includes(n.operator) ? '逻辑赋值 ' + n.operator + '（Chrome 85）' : '';
    case 'PropertyDefinition': return '类字段（Chrome 72/74）';
    case 'PrivateIdentifier': return '私有成员 #（Chrome 74/84）';
    case 'StaticBlock': return 'static 块（94）';
    case 'ImportExpression': return '动态 import（63）';
    case 'MetaProperty': return n.meta.name === 'import' ? 'import.meta' : '';
    case 'Literal': if (n.bigint) return 'BigInt（67）'; if (typeof n.raw === 'string' && /^\d[\d_]*_/.test(n.raw)) return '数字分隔符（75）'; if (n.regex) { if (/d/.test(n.regex.flags)) return '正则 d 标记（90）'; if (/\(\?<[=!]/.test(n.regex.pattern)) return '正则 lookbehind（62）'; if (/\(\?<[A-Za-z]/.test(n.regex.pattern)) return '正则命名组（64）'; if (/\p\{/.test(n.regex.pattern)) return '正则 \p{}（64）'; if (n.regex.flags.includes('s')) return '正则 s 标记（62）'; } return '';
    case 'CatchClause': return n.param ? '' : 'catch 不写参数（66）';
    case 'AwaitExpression': return '';
    default: return '';
  }
};
function walk(n, f) { if (!n || typeof n.type !== 'string') return; f(n); for (const k in n) { if (k === 'loc') continue; const v = n[k]; if (Array.isArray(v)) v.forEach((x) => x && typeof x === 'object' && walk(x, f)); else if (v && typeof v === 'object' && v.type) walk(v, f); } }
let total = 0;
for (const f of files) {
  const res = []; let ck = 0;
  for (const c of chunks(f)) {
    ck++;
    try { acorn.parse(c.code, { ecmaVersion: 2018, sourceType: c.module ? 'module' : 'script', allowHashBang: true }); }
    catch (e) {
      res.push(`  2018 解析不过：第 ${c.line0 + (e.loc ? e.loc.line : 0)} 行 ${e.message}`);
    }
    let ast;
    try { ast = acorn.parse(c.code, { ecmaVersion: 'latest', sourceType: c.module ? 'module' : 'script', locations: true, allowHashBang: true, allowAwaitOutsideFunction: true }); }
    catch (e) { res.push(`  连 latest 都解析不过：第 ${c.line0 + (e.loc ? e.loc.line : 0)} 行 ${e.message}`); continue; }
    const seen = {};
    walk(ast, (n) => { const w = isNew(n); if (w) { const k = w + '@' + (c.line0 + n.loc.start.line); if (!seen[k]) { seen[k] = 1; res.push(`  ${w}：第 ${c.line0 + n.loc.start.line} 行`); } } });
    const lines = c.code.split('\n');
    lines.forEach((ln, i) => { for (const [re, w] of API) if (re.test(ln)) res.push(`  [API] ${w}：第 ${c.line0 + i + 1} 行  ${ln.trim().slice(0, 110)}`); });
  }
  total += res.filter((x) => !x.includes('[API]')).length;
  console.log(`== ${path.basename(path.dirname(f))}/${path.basename(f)}（${ck} 段脚本）${res.length ? '' : ' 没问题'}`);
  for (const r of res) console.log(r);
}
console.log('语法上的合计', total);
