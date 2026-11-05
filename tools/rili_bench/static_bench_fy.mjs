// 风月聊天页的本地复刻台（11-04）：不装依赖，本机 Chrome 或 Edge 无头出图。
// 页面层级和类名照风月前端代码（chat 那个 chunk）搭：#installedBuiltInCss 底下外壳（顶栏、滚动容器）和输入栏是兄弟（11-05 改对的，头一版把输入栏放进了外壳，所以电脑上缺两扇在这里看不出来）。平台样式用真的（css= 指到从风月页面存下来的那几个 css 文件的目录，文件不进库）。
// 走平台的几道工序：正则脚本（只认 g，mode 分 renderOnly、all、persist）、消息里的标签过滤（照 Markdown 组件那一段）、行内 style 的属性名改写（--v 变 -V）、样式前缀（#installedBuiltInCss）。
// 只有 markdown 省掉了（展开以后都是 HTML），玩家的话照原样放。
// 用法：node static_bench_fy.mjs <卡.json> <样本1,样本2> <输出.png> css=<平台样式目录> [w=1536] [h=1024] [theme=dark|light] [sidebar=0|1] [mode=renderOnly|all] [scroll=latest|end|数字] [scrolls=..] [eval=脚本.js] [ask=玩家的话] [steps=步骤.json]
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const [cardFile, fxList, out, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => { const i = a.indexOf('='); return [a.slice(0, i), a.slice(i + 1)]; }));
const W = Number(opt.w || 1536), H = Number(opt.h || 1024);
const card = JSON.parse(fs.readFileSync(cardFile, 'utf8'));

// ---- 正则脚本：照平台 applyRegexScripts 抄
export function applyRegexScripts(e, n, r, o = 'all') {
  if (e == null || e === '' || !n?.length) return e;
  const i = n.filter((x) => {
    if (x?.is_enable === false || (x.scope !== 10 && x.scope !== r)) return false;
    const only = x.is_only_render === true;
    return (o !== 'persist' || !only) && (o !== 'renderOnly' || !!only) && typeof x.match_regex === 'string' && x.match_regex.length > 0;
  });
  let l = e;
  for (const x of i) {
    try { l = l.replace(RegExp(x.match_regex, 'g'), x.replace_text == null ? '' : String(x.replace_text)); } catch { console.log('正则编译失败', x.title); }
  }
  return l;
}

// ---- 消息过滤：照 Markdown 组件那一段（DOMPurify 那一步只碰纯文字，省掉）
const y = ['script', 'iframe', 'object', 'embed', 'applet', 'link', 'meta', 'base', 'html', 'head', 'body', 'form', 'style'];
const A = 'cot[a-z0-9]{0,2}|thinking|reasoning';
const v = /^(?:cot[a-z0-9]{0,2}|thinking|reasoning)$/i;
const I = /<\/?[a-zA-Z][\w-]*(\s+[^\s=<>/]+(\s*=\s*("[\s\S]*?"|'[\s\S]*?'|[^\s"'=<>`]+))?)*\s*\/?>|<!--[\s\S]*?-->/g;
function stripThink(e) {
  let t = e, a = '';
  const n = `<(?:${A})\\b[^>]*>`, r = `<\\/(?:${A})\\s*>`;
  for (; t !== a;) { a = t; t = t.replace(RegExp(`${n}[\\s\\S]*?${r}`, 'gi'), ''); }
  t = t.replace(RegExp(`${n}[\\s\\S]*?(?=<div\\b|<details\\b|<p\\b|<table\\b|$)`, 'gi'), '');
  return t.replace(RegExp(`</?(?:${A})\\b[^>]*>`, 'gi'), '');
}
function stripTags(e) {
  let t = e, n = '';
  for (; t !== n;) for (const x of (n = t, y)) t = t.replace(RegExp(`<${x}\\b[^>]*>[\\s\\S]*?<\\/${x}\\s*>`, 'gi'), '');
  return t.replace(RegExp(`</?(?:${y.join('|')})\\b[^>]*>`, 'gi'), '');
}
function fixTag(e) {
  if (e.startsWith('<!--')) return e;
  const n = e.match(/^<\/?([a-zA-Z][\w-]*)\b([^>]*)(\/?)>$/);
  if (!n) return e;
  const [, r, a, i] = n, o = r.toLowerCase();
  if (y.includes(o) || v.test(o)) return '';
  if (e.startsWith('</')) return `</${r}>`;
  const s = [], l = /([^\s=]+)(\s*=\s*(?:"([\s\S]*?)"|'([\s\S]*?)'|([^\s"'=<>`]+)))?/g;
  let t;
  for (; (t = l.exec(a));) {
    const k = t[1], kl = k.toLowerCase();
    if (kl.startsWith('on') || kl === 'srcdoc') continue;
    const val = t[3] ?? t[4] ?? t[5];
    if (kl === 'ref') { if (val != null) s.push(`data-ref="${String(val).replace(/"/g, '&quot;')}"`); continue; }
    if (kl !== 'key') { if (val == null) { s.push(k); continue; } if (!((kl === 'href' || kl === 'src') && /^\s*javascript:/i.test(val))) s.push(`${k}="${val.replace(/"/g, '&quot;')}"`); }
  }
  const c = s.length ? ` ${s.join(' ')}` : '';
  return `<${r}${c}${i ? ' /' : ''}>`;
}
function fyMarkdown(p) {
  const c = stripTags(stripThink(p));
  const u = [];
  const m = c.replace(I, (e) => { u.push(e); return '__PH__'; }).replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return m.replace(/__PH__/g, () => fixTag(u.shift() || ''));
}

// ---- 样式前缀：照平台 addPrefixForStyle（postcss-prefix-selector 加它自己的 transform），postcss 换成一个小解析器
function splitRules(css) {
  const res = [];
  let i = 0, start = 0, depth = 0, quote = null, paren = 0;
  while (i < css.length) {
    const c = css[i];
    if (quote) { if (c === '\\') i++; else if (c === quote) quote = null; }
    else if (c === '"' || c === "'") quote = c;
    else if (css.startsWith('/*', i)) { const e = css.indexOf('*/', i + 2); i = e < 0 ? css.length : e + 1; }
    else if (c === '(') paren++;
    else if (c === ')') paren--;
    else if (c === '{' && !paren) depth++;
    else if (c === '}' && !paren) { depth--; if (!depth) { res.push(css.slice(start, i + 1)); start = i + 1; } }
    else if (c === ';' && !depth && !paren) { res.push(css.slice(start, i + 1)); start = i + 1; }
    i++;
  }
  return res;
}
function splitSel(s) {
  const parts = [];
  let d = 0, cur = '', q = null;
  for (const c of s) {
    if (q) { if (c === q) q = null; cur += c; continue; }
    if (c === '"' || c === "'") q = c;
    if (c === '(' || c === '[') d++;
    if (c === ')' || c === ']') d--;
    if (c === ',' && !d) { parts.push(cur); cur = ''; } else cur += c;
  }
  parts.push(cur);
  return parts;
}
const PFX = '#installedBuiltInCss';
function prefixOne(e) {
  e = e.trim();
  if (e === 'body' || e === 'html') return `${PFX} ${e}`;
  if (e === '.dark' || e.startsWith('.dark ') || e.startsWith('.dark:')) return `${PFX}${e}`;
  if (e === 'html.dark' || e.startsWith('html.dark ')) { const r = e.slice(9).trim(); return r ? `html.dark ${PFX} ${r}` : `html.dark ${PFX}`; }
  return `${PFX} ${e}`;
}
function prefix(css) {
  return splitRules(css.replace(/\/\*[\s\S]*?\*\//g, '')).map((r) => {
    const t = r.trim();
    if (!t) return '';
    const b = t.indexOf('{');
    if (t[0] === '@') {
      if (/^@(-webkit-)?keyframes|^@font-face/.test(t)) return t;
      if (b > 0 && /^@(media|supports|layer|container)/.test(t)) return t.slice(0, b + 1) + prefix(t.slice(b + 1, t.lastIndexOf('}'))) + '}';
      return t;
    }
    if (b < 0) return '';
    return splitSel(t.slice(0, b)).map(prefixOne).join(',') + t.slice(b);
  }).join('\n');
}

const rules = card.regex_rp || [];
const mode = opt.mode || 'renderOnly';
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const qText = opt.ask || '（玩家输入）';
const tools = `<div class="flex items-center gap-1 mt-1 fy-tools"><button class="inline-flex items-center justify-center size-6 rounded-md text-text-secondary" title="刷新">⟳</button><button class="inline-flex items-center justify-center size-6 rounded-md text-text-secondary" title="编辑">✎</button><button class="inline-flex items-center justify-center size-6 rounded-md text-text-secondary" title="复制">⧉</button></div>`;
const msgs = [];
function question() {
  return `<div id="customized-question" class="group flex mb-2 last:mb-0"><div id="customized-question-avatar" class="shrink-0 w-10 h-10 relative bg-white rounded-full bg-background block md:block"><div class="w-full h-full rounded-full border-[0.5px] border-black/5 border-border"></div></div><div id="customized-question-content-container" class="group relative ml-2 md:ml-4 mr-4 md:mr-0"><div data-has-css="true" id="customized-question-content" class="relative inline-block px-4 py-3 max-w-full text-gray-900 bg-gray-100/90 rounded-xl text-sm bg-secondary data-[has-css=false]:text-text-main"><div id="customized-question-content-thinking-line" class="absolute top-0 left-1/2 transform -translate-x-1/2 w-[94%] h-0.5 bg-[#c9e1e9] rounded-xl"></div><div id="customized-question-content-markdown" class="markdown-body" style="font-size:14px">${esc(qText)}</div></div></div></div>`;
}
function answer(raw) {
  const html = fyMarkdown(applyRegexScripts(raw, rules, 1, mode));
  msgs.push(html);
  return `<div id="customized-answer" class="flex mb-2 last:mb-0"><div id="customized-answer-container" class="chat-answer-container group grow w-0 mr-2 md:mr-4"><div id="customized-answer-content-container" class="group relative ml-4 md:ml-0 "><div data-has-css="true" id="customized-answer-content" class="relative inline-block px-4 py-3 w-full bg-gray-100/90  rounded-xl text-sm text-gray-900 bg-secondary data-[has-css=false]:text-text-main"><div id="customized-answer-content-thinking-line" class="absolute top-0 right-1/2 transform translate-x-1/2 w-[94%] h-0.5 bg-[#F1CBCB] rounded-xl"></div><div id="customized-answer-content-markdown" class="markdown-body  " style="font-size:14px" data-m="${msgs.length - 1}"></div><div id="customized-answer-content-created-time" class="text-xs text-text-secondary mt-1">2026-11-04 14:20</div><div id="customized-answer-content-model" class="flex flex-row items-center flex-wrap gap-2.5 mt-1"><span id="customized-answer-content-model-name" class="text-xs text-primary">gemini-3-flash</span><span class="text-xs text-text-secondary">消耗 12 积分</span></div>${tools}</div></div></div><div id="customized-answer-avatar" class="shrink-0 relative w-10 h-10 bg-gray-100/90 rounded-full block md:block"><div class="flex items-center justify-center w-full h-full rounded-full bg-[#d5f5f6] border-[0.5px] border-black/5 text-xl">🤖</div></div></div>`;
}
const files = fxList.split(',').filter(Boolean);
const pairs = files.map((f) => question() + answer(fs.readFileSync(f, 'utf8').split(String.fromCharCode(13)).join('')));
const lastPair = pairs.pop();
const rows = pairs.map((p, i) => `<div data-index="${i}" data-known-size="160" data-item-index="${i}" class="pb-2" style="overflow-anchor:none;contain:layout style paint">${p}</div>`).join('');
const virt = pairs.length ? `<div data-testid="virtuoso-scroller"><div data-viewport-type="element" style="width:100%;height:100%"><div data-testid="virtuoso-item-list" style="box-sizing:border-box;padding-top:0;padding-bottom:0;margin-top:0">${rows}</div></div></div>` : '';
const btn = (id, t) => `<button${id ? ` id="${id}"` : ''} class="inline-flex items-center justify-center gap-2 whitespace-nowrap font-medium border border-input bg-background shadow-xs rounded-md h-8 px-3 text-xs shrink-0">${t}</button>`;
const cmds = (card.short_cmds || []).map((c, i) => btn(`customized-shortcut-command-button-${i}`, esc(c.label))).join('');
const foot = `<div class="bg-gradient-to-t from-white via-white to-transparent absolute w-full bottom-0 left-0 right-0 dark:from-background dark:via-background pb-4"><div class="relative mx-auto w-full max-w-[720px] px-4"><div id="customized-ai-input-container" class="relative mt-2"><div class="w-full z-[5] py-1" id="customized-pagination-container"><div class="relative" id="customized-pagination"><div class="flex items-center justify-center gap-1 py-0 text-xs h-6 text-text-main"><button class="size-6">‹</button><button class="size-6 rounded bg-primary text-white">1</button><button class="size-6">2</button><button class="size-6">›</button></div></div></div><div id="ai-mod-button2" data-tour="novice-step-5" class="flex items-center gap-2 pb-2 overflow-x-auto">${btn('ai-mod-button', '模组')}${btn('customized-more-button', '更多')}${btn('toggle-sub-buttons', '收起')}${cmds}</div><div class="mb-2 bg-white border-[1.5px] border-gray-200 dark:bg-background relative rounded-xl"><div id="ai-input-content" class="w-full overflow-y-auto p-[5.5px] max-h-[150px]"><textarea id="ai-chat-input" rows="1" placeholder="在这里输入" class="block w-full px-2 pr-[118px] py-[7px] leading-5 max-h-none text-sm text-text-main outline-hidden appearance-none resize-none bg-background"></textarea></div><div id="ai-input-controls" class="absolute bottom-2 right-2 flex items-center h-8 bg-white/80 backdrop-blur-sm rounded-lg z-10"><div id="ai-input-control-input-length" class="flex items-center px-1 h-5 rounded-md bg-gray-100 text-xs font-medium text-gray-500">0</div><div id="ai-input-control-separator" class="mx-2 w-px h-4 bg-black/5"></div><div id="ai-send-button" class="group flex items-center justify-center w-8 h-8 rounded-lg cursor-pointer">➤</div></div></div></div></div></div>`;
const hdr = `<div class="sticky w-full top-0 flex items-center px-2 h-12 md:h-16 text-base font-medium text-text-main border-b-[0.5px] backdrop-blur-md z-20"><div class="flex items-center justify-between w-full relative min-w-0"><div class="flex items-center gap-1 shrink-0"><span class="text-xs px-2">私有</span></div><div id="customized-model-selector" class="absolute left-1/2 z-10 max-w-[50vw] min-w-0 -translate-x-1/2 md:static md:left-auto md:max-w-none md:translate-x-0"><button class="bg-secondary max-w-[50vw] w-full rounded-md px-3 h-8 text-sm">gemini-3-flash</button></div><div class="flex items-center gap-2 shrink-0"><button class="size-8">⚙</button></div></div></div>`;
const cssDir = opt.css;
const platCss = fs.readdirSync(cssDir).filter((f) => f.endsWith('.css')).map((f) => fs.readFileSync(path.join(cssDir, f), 'utf8')).join('\n');
const cardCss = prefix(card.built_in_css || '');
const sidebar = opt.sidebar === '1';
const page = `<!doctype html><html lang="zh" class="${opt.theme === 'light' ? 'light' : 'dark'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>${platCss}</style><style id="installedBuiltInCss_css">${cardCss}</style></head>
<body style="margin:0;height:100dvh;overflow:hidden" class="${opt.theme === 'light' ? '' : 'dark'}"><div style="display:flex;height:100dvh">${sidebar ? '<aside style="flex:0 0 260px;background:#222;color:#888;padding:16px;font-size:13px">导航</aside>' : ''}<div style="flex:1 1 0;min-width:0;height:100%">
<div id="installedBuiltInCss" class="relative w-full h-full overflow-hidden dark:text-foreground dark:bg-background ${opt.theme === 'light' ? '' : 'dark'}"><div id="fy-sh" class="relative h-full ">${hdr}<div class="overflow-y-auto w-full h-full chat-container mx-auto "><div id="fy-inner" class="mx-auto pt-24 w-full max-w-[720px] px-1 md:px-4 relative">${virt}${lastPair}</div></div></div>${foot}</div></div></div>
<script>
const M=${JSON.stringify(msgs).split('<').join('\\u003c')};
// react-markdown 改写行内 style 的属性名：-x 变 X；-- 开头的走 setProperty，别的当普通属性
function fixStyles(root){for(const el of root.querySelectorAll('[style]')){const s=el.getAttribute('style');el.removeAttribute('style');for(const part of s.split(';')){const i=part.indexOf(':');if(i<0)continue;const k=part.slice(0,i).trim();const v=part.slice(i+1).trim();const key=k.replace(/-([a-z])/g,(m,c)=>c.toUpperCase());if(key.startsWith('--'))el.style.setProperty(key,v);else el.style[key]=v;}}}
for(const el of document.querySelectorAll('[data-m]')){el.innerHTML=M[el.dataset.m];fixStyles(el);}
const sh=document.getElementById('fy-sh'),ft=document.querySelector('#installedBuiltInCss > .bg-gradient-to-t'),inner=document.getElementById('fy-inner'),fi=ft.firstElementChild;
const fit=()=>{sh.style.paddingBottom=ft.getBoundingClientRect().height+55+'px';fi.style.width=inner.clientWidth+'px'};
new ResizeObserver(fit).observe(ft);fit();addEventListener('resize',fit);
window.place=(mode)=>{mode=mode||${JSON.stringify(opt.scroll || 'latest')};const c=sh.querySelector('.chat-container');if(mode==='end')c.scrollTop=c.scrollHeight;else if(mode==='latest'){const a=[...document.querySelectorAll('#customized-answer')].pop();c.scrollTop=Math.max(0,a.offsetTop-c.offsetTop-120)}else c.scrollTop=Number(mode)};
place();
</script></body></html>`;
const htmlPath = out.replace(/\.[a-z]+$/, '') + '.html';
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
fs.writeFileSync(htmlPath, page);
const chrome = opt.chrome || ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find((p) => fs.existsSync(p));
const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'fy_bench_'));
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files', '--no-first-run', '--remote-debugging-port=0', `--user-data-dir=${prof}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let port = null;
for (let i = 0; i < 200 && !port; i++) { await sleep(100); try { port = fs.readFileSync(path.join(prof, 'DevToolsActivePort'), 'utf8').split(/\s+/)[0].trim(); } catch {} }
const target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), waiters = [];
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } else for (const w of waiters) if (w.ev === m.method) w.fn(m); };
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: pathToFileURL(path.resolve(htmlPath)).href });
await loaded;
await sleep(Number(opt.wait || 1500));
await send('Runtime.evaluate', { expression: 'window.place&&window.place(),1', returnByValue: true });
await sleep(300);
if (opt.eval) { const r = await send('Runtime.evaluate', { expression: fs.readFileSync(opt.eval, 'utf8'), returnByValue: true, awaitPromise: true }); console.log(r.result?.exceptionDetails ? JSON.stringify(r.result.exceptionDetails).slice(0, 600) : r.result?.result?.value ?? JSON.stringify(r).slice(0, 400)); }
const shots = (opt.scrolls || '').split(',').filter(Boolean);
const shot = async (file) => { const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false }); fs.writeFileSync(file, Buffer.from(r.result.data, 'base64')); console.log('ok', file, fs.statSync(file).size); };
await shot(out);
for (const s of shots) {
  await send('Runtime.evaluate', { expression: `window.place(${JSON.stringify(s)})` });
  await sleep(400);
  await shot(out.replace(/\.png$/, `_${s}.png`));
}
// steps=文件：[{"name":"panel","js":"表达式"}]，一步一张图。转场的动画直接走完（无头里动画时钟不走）
if (opt.steps) for (const st of JSON.parse(fs.readFileSync(opt.steps, 'utf8'))) {
  const r = await send('Runtime.evaluate', { expression: `(()=>{${st.js};for(const a of document.getAnimations())if(a.timeline instanceof DocumentTimeline&&isFinite(a.effect.getComputedTiming().endTime))a.finish();})()`, returnByValue: true });
  if (r.result.exceptionDetails) console.log('步骤出错', st.name, r.result.exceptionDetails.exception?.description);
  await sleep(350);
  await shot(out.replace(/\.png$/, `_${st.name}.png`));
}
ws.close();
proc.kill();
