// 不装依赖的复刻台（11-03）：本机自带的 Chrome 或 Edge 无头出图，不要 react、playwright、postcss。
// 版面照 app.jsx 和 shell.css，样式的作用域照 platform.mjs，只有 markdown 省掉了（展开以后都是 HTML）。交互（点页签）要跑 bench.mjs。
// 用法：node static_bench.mjs <样本1,样本2> <输出.png> [w=1536] [h=1024] [sidebar=0|1] [extracss=文件1,文件2] [extrarules=文件1,文件2] [art=图目录] [scroll=latest|end|数字] [scrolls=end,300 再多截几张] [wait=毫秒] [chrome=路径] [chips=预设1,预设2 输入框上头那一排，默认照奥尔德兰的两个] [theme=light]
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { pathToFileURL, fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const [fxList, out, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => a.split('=')));
const W = Number(opt.w || 1536), H = Number(opt.h || 1024);

// ---- platform.mjs 那两道工序，postcss 换成一个小解析器
function splitRules(css) {
  const out = [];
  let i = 0, start = 0, depth = 0, quote = null, paren = 0;
  while (i < css.length) {
    const c = css[i];
    if (quote) { if (c === '\\') i++; else if (c === quote) quote = null; }
    else if (c === '"' || c === "'") quote = c;
    else if (css.startsWith('/*', i)) { const e = css.indexOf('*/', i + 2); i = e < 0 ? css.length : e + 1; }
    else if (c === '(') paren++;
    else if (c === ')') paren--;
    else if (c === '{' && !paren) depth++;
    else if (c === '}' && !paren) { depth--; if (!depth) { out.push(css.slice(start, i + 1)); start = i + 1; } }
    else if (c === ';' && !depth && !paren) { out.push(css.slice(start, i + 1)); start = i + 1; }
    i++;
  }
  return out;
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
function scope(css, sc = '.custom-styles') {
  const KEEP = /^@(-webkit-)?keyframes|^@font-face/;
  return splitRules(css.replace(/\/\*[\s\S]*?\*\//g, '')).map((r) => {
    const t = r.trim();
    if (!t) return '';
    const b = t.indexOf('{');
    if (t[0] === '@') {
      if (KEEP.test(t)) return t;
      if (/^@media/.test(t)) return t.slice(0, b + 1) + scope(t.slice(b + 1, t.lastIndexOf('}')), sc) + '}';
      return '';   // 平台丢掉别的 at 规则
    }
    if (b < 0) return '';
    const sel = splitSel(t.slice(0, b)).map((s) => { s = s.trim(); return s.startsWith(':root') ? sc + s.slice(5) : sc + ' ' + s; }).join(',');
    return sel + t.slice(b);
  }).join('\n');
}
function applyRules(text, rules, role = 'assistant', side = 'front-end') {
  for (const r of rules) {
    if (!r.enabled) continue;
    if (r.messageRole !== 'all' && r.messageRole !== role) continue;
    if (r.applyMode !== 'all' && r.applyMode !== side) continue;
    const m = r.regex.startsWith('/') ? r.regex.match(/^\/([\s\S]*)\/([^/]*)$/) : null;
    if (m) text = text.replace(new RegExp(m[1], [...m[2]].filter((f) => 'imsg'.includes(f)).join('')), r.replaceString);
    else text = text.split(r.regex).join(r.replaceString);
  }
  return text;
}

let styles = '';
if (opt.extracss) for (const f of opt.extracss.split(',')) styles += '\n' + fs.readFileSync(f, 'utf8');
if (opt.art) styles = styles.split('__ART__').join(pathToFileURL(path.resolve(opt.art)).href);
let rules = [];
if (opt.extrarules) for (const f of opt.extrarules.split(',')) rules = rules.concat(JSON.parse(fs.readFileSync(f, 'utf8')));
const row = (inner) => `<div class="vrow" style="contain: layout style; position: absolute; width: 100%; left: 0; top: 0"><div class="w-full max-w-2xl mx-auto my-3 px-4 pb-4"><div class="w-full h-full flex group">${inner}</div></div></div>`;
const tools = '<div class="msg-tools"><span class="cnt"><i></i>324<i></i>912</span><span class="ics">⟳ ⧉ ⑂ ✎ ⌫ ♪</span></div>';
const rows = [], msgHtml = [];
for (const f of fxList.split(',')) {
  rows.push(row(`<div class="group flex flex-col gap-2 w-fit is-user ml-auto"><div class="bubble"><div class="space-y-3"><div class="text-sm">（玩家输入）</div></div></div>${tools}</div>`));
  const html = applyRules(fs.readFileSync(f, 'utf8').split(String.fromCharCode(13)).join(''), rules);   // 这台机器上检出来是 CRLF，规则认 LF
  msgHtml.push(html);   // 一条一条放进 innerHTML，展开出来没闭合的标签就关在这一条里（平台上是 rehype-raw 做这件事）
  rows.push(row(`<div class="group flex flex-col gap-2 w-fit is-assistant"><div class="bubble"><div class="space-y-3"><div class="text-sm rili-markdown-renderer break-words" data-m="${msgHtml.length - 1}"></div></div></div>${tools}</div>`));
}
const PREFLIGHT = `*,::after,::before,::backdrop,::file-selector-button{box-sizing:border-box;margin:0;padding:0;border:0 solid}
html{line-height:1.5;-webkit-text-size-adjust:100%;tab-size:4}body{line-height:inherit}hr{height:0;color:inherit;border-top-width:1px}
h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit}a{color:inherit;text-decoration:inherit}b,strong{font-weight:bolder}
ol,ul,menu{list-style:none}img,svg,video,canvas,audio,iframe,embed,object{display:block;vertical-align:middle}img,video{max-width:100%;height:auto}
button,input,select,optgroup,textarea{font:inherit;color:inherit;letter-spacing:inherit;border-radius:0;background-color:transparent;opacity:1}textarea{resize:vertical}
[hidden]:not([hidden=until-found]){display:none!important}`;
const sidebar = opt.sidebar === '1';
const page = `<!doctype html><html lang="zh" class="${opt.theme === 'light' ? 'light' : 'dark'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>${PREFLIGHT}</style><style>${fs.readFileSync(path.join(here, 'shell.css'), 'utf8')}</style></head><body><div id="root"><div class="sidebar-wrapper">${sidebar ? '<aside class="fake-sidebar">导航</aside>' : ''}<div class="flex-1"><nav class="sticky top-0 w-full z-50 backdrop-blur custom-styles"><header><div class="h-left">▣</div><div class="h-center"></div><div class="h-right">◔ ◑ ☾</div></header></nav><main><div class="w-full h-full relative bg-background custom-styles"><style>${scope(styles)}</style><div class="flex flex-col items-center"><div id="conversation"><div class="conv-inner"><div id="list" style="contain: size style; overflow-anchor: none; flex: 0 0 auto; position: relative; width: 100%">${rows.join('')}</div></div></div><div class="fake-input"><div class="fake-input-inner rounded-xl bg-background"><div class="fake-chips"><button type="button" class="pl">⬡ 模组</button><button type="button" class="pl">◯ 评论 (0)</button><button type="button" class="sq">↓</button><button type="button" class="sq">▣</button><button type="button" class="sq">⌕</button><i class="vl"></i>${(opt.chips || '超程铭刻,防抢话').split(',').map((c) => `<button type="button">${c}</button>`).join('')}</div><textarea id="chat-input" placeholder="在此输入您的消息"></textarea><div class="fake-tools"><span><button type="button" class="ic">⚙</button><button type="button" class="ic">ⓘ</button><button type="button" class="pill">✦ gemini-3.0-flash</button></span><span><button type="button" class="pill">实时</button><button type="button" class="send">↵</button></span></div></div></div></div></div></main></div></div></div>
<script>
const M=${JSON.stringify(msgHtml).split('<').join('\\u003c')};
for(const el of document.querySelectorAll('[data-m]'))el.innerHTML=M[el.dataset.m];
const list=document.getElementById('list');
window.lay=()=>{let y=0;for(const r of list.children){r.style.top=y+'px';y+=r.getBoundingClientRect().height}list.style.height=y+'px'};
window.place=(mode)=>{mode=mode||${JSON.stringify(opt.scroll || 'latest')};const c=document.getElementById('conversation');if(mode==='end')c.scrollTop=c.scrollHeight;else if(mode==='latest'){const a=[...document.querySelectorAll('.rili-markdown-renderer')].pop();c.scrollTop=a.getBoundingClientRect().top-c.getBoundingClientRect().top+c.scrollTop-110}else c.scrollTop=Number(mode)};
lay();place();
</script></body></html>`;
const htmlPath = out.replace(/\.[a-z]+$/, '') + '.html';
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
fs.writeFileSync(htmlPath, page);
// ---- 无头浏览器：--window-size 在新版无头里含窗口边框，这里走 DevTools 协议定视口，node 24 自带 WebSocket
const chrome = opt.chrome || ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find((p) => fs.existsSync(p));
const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'rili_bench_'));
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
await send('Runtime.evaluate', { expression: 'window.lay&&window.lay(),window.place&&window.place(),1', returnByValue: true });
await sleep(300);
if (opt.eval) console.log((await send('Runtime.evaluate', { expression: fs.readFileSync(opt.eval, 'utf8'), returnByValue: true, awaitPromise: true })).result.result.value);
const shots = (opt.scrolls || '').split(',').filter(Boolean);
const shot = async (file) => { const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false }); fs.writeFileSync(file, Buffer.from(r.result.data, 'base64')); console.log('ok', file, fs.statSync(file).size); };
await shot(out);
for (const s of shots) {
  await send('Runtime.evaluate', { expression: `window.place(${JSON.stringify(s)})` });
  await sleep(400);
  await shot(out.replace(/\.png$/, `_${s}.png`));
}
ws.close();
proc.kill();
