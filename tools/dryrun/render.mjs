// 本地干跑·渲染：把一条回复套上卡里的显示正则和样式，在日里聊天页的复刻版面里截图，一页签一张，并把每一页看得见的字抄出来查残留。
// 版面、作用域、无头出图的做法照 tools/rili_bench/static_bench.mjs（那一支吃的是样式文件和规则文件，这一支直接吃卡）。
// 用法：node tools/dryrun/render.mjs <回复.txt[,更早的回复.txt…]> <输出目录> [card=卡.json] [w=1920] [h=1080] [mobile=1] [tabs=panel,deed,…] [css=本地样式.css] [chrome=路径] [wait=毫秒]
//   回复写几条用逗号隔开，末一条是最新的（页签只挂在最新一条上）。
//   出：<输出目录>/00_正文.png、00_正文_末尾.png、NN_<页签>.png、展开.html（过完正则的结果）、页面.html、检查.txt（各页的字、残留的 § 和竖线、没取到的图）。
//   mobile=1 另按 390×844 截 m_ 开头的几张（浮栏在手机上是正文顶上一横排）。
// 样式：卡的样式格只剩平台外壳那几条，状态栏的样式在图床上，显示正则末一条往每条回复里插 <link>。这里不走网络：
//   照 link 里的文件名到 底稿/状态栏/外链样式/out/ 找本地那一份（已经加过 .custom-styles 作用域，就是图床上那一个文件），找不到再照地址取一回。
//   样式里引的立绘、图标是图床地址，截图时浏览器照常去取（跟真页面一样），断网时图是空的，字和版面照出。
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { CARD_FULL, ROOT, loadCard, readText, applyRules } from './lib.mjs';

const [fxList, outDir, ...rest] = process.argv.slice(2);
if (!fxList || !outDir) { console.log('用法：node tools/dryrun/render.mjs <回复.txt[,…]> <输出目录> [card=] [w=] [h=] [mobile=1] [tabs=]'); process.exit(1); }
const opt = Object.fromEntries(rest.map((a) => { const i = a.indexOf('='); return [a.slice(0, i), a.slice(i + 1)]; }));
const W = Number(opt.w || 1920), H = Number(opt.h || 1080);
const card = loadCard(opt.card || CARD_FULL);
const rules = card.assistantRegexReplace || [];
const bench = path.join(ROOT, 'tools', 'rili_bench');
fs.mkdirSync(outDir, { recursive: true });

// ---- 样式的作用域（static_bench.mjs 那个小解析器原样）
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
      return '';
    }
    if (b < 0) return '';
    const sel = splitSel(t.slice(0, b)).map((s) => { s = s.trim(); return s.startsWith(':root') ? sc + s.slice(5) : sc + ' ' + s; }).join(',');
    return sel + t.slice(b);
  }).join('\n');
}

// ---- 回复过正则；link 拿出来换成本地样式
const linked = [];
const msgHtml = fxList.split(',').map((f) => {
  let html = applyRules(readText(f), rules, 'front-end');
  html = html.replace(/<link\b[^>]*href="([^"]+)"[^>]*>/g, (m, href) => { if (!linked.includes(href)) linked.push(href); return ''; });
  return html;
});
fs.writeFileSync(path.join(outDir, '展开.html'), msgHtml[msgHtml.length - 1]);
let cdnCss = '';
const notes = [];
if (opt.css) cdnCss = fs.readFileSync(opt.css, 'utf8');
else for (const href of linked) {
  const name = href.split('/').pop();
  const local = path.join(ROOT, '底稿', '状态栏', '外链样式', 'out', name);
  if (fs.existsSync(local)) { cdnCss += '\n' + fs.readFileSync(local, 'utf8'); notes.push('样式用本地那一份：' + path.relative(ROOT, local)); }
  else { try { cdnCss += '\n' + await (await fetch(href)).text(); notes.push('样式从图床取的：' + href); } catch (e) { notes.push('样式没取到：' + href + '（' + e.message + '）'); } }
}
if (!linked.length && !opt.css) notes.push('回复过完正则没有插出 <link>，状态栏的样式没载进来（卡的显示正则末一条该插）');
const ownCss = scope(card.injectStyles || '');

// ---- 页面（static_bench.mjs 的骨架）
const row = (inner) => `<div class="vrow" style="contain: layout style; position: absolute; width: 100%; left: 0; top: 0"><div class="w-full max-w-2xl mx-auto my-3 px-4 pb-4"><div class="w-full h-full flex group">${inner}</div></div></div>`;
const tools = '<div class="msg-tools"><span class="cnt"><i></i>324<i></i>912</span><span class="ics">⟳ ⧉ ⑂ ✎ ⌫ ♪</span></div>';
const rows = [];
msgHtml.forEach((h, i) => {
  rows.push(row(`<div class="group flex flex-col gap-2 w-fit is-user ml-auto"><div class="bubble"><div class="space-y-3"><div class="text-sm">（玩家输入）</div></div></div>${tools}</div>`));
  rows.push(row(`<div class="group flex flex-col gap-2 w-fit is-assistant"><div class="bubble"><div class="space-y-3"><div class="text-sm rili-markdown-renderer break-words" data-m="${i}"></div></div></div>${tools}</div>`));
});
const PREFLIGHT = `*,::after,::before,::backdrop,::file-selector-button{box-sizing:border-box;margin:0;padding:0;border:0 solid}
html{line-height:1.5;-webkit-text-size-adjust:100%;tab-size:4}body{line-height:inherit}hr{height:0;color:inherit;border-top-width:1px}
h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit}a{color:inherit;text-decoration:inherit}b,strong{font-weight:bolder}
ol,ul,menu{list-style:none}img,svg,video,canvas,audio,iframe,embed,object{display:block;vertical-align:middle}img,video{max-width:100%;height:auto}
button,input,select,optgroup,textarea{font:inherit;color:inherit;letter-spacing:inherit;border-radius:0;background-color:transparent;opacity:1}textarea{resize:vertical}
[hidden]:not([hidden=until-found]){display:none!important}`;
const chips = (card.options?.items || []).slice(0, 4).map((o) => `<button type="button">${o.label}</button>`).join('');
const page = `<!doctype html><html lang="zh" class="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><style>${PREFLIGHT}</style><style>${fs.readFileSync(path.join(bench, 'shell.css'), 'utf8')}</style></head><body><div id="root"><div class="sidebar-wrapper"><div class="flex-1"><nav class="sticky top-0 w-full z-50 backdrop-blur custom-styles"><header><div class="h-left">▣</div><div class="h-center"></div><div class="h-right">◔ ◑ ☾</div></header></nav><main><div class="w-full h-full relative bg-background custom-styles"><style>${ownCss}</style><style>${cdnCss.split('</style').join('<\\/style')}</style><div class="flex flex-col items-center"><div id="conversation"><div class="conv-inner"><div id="list" style="contain: size style; overflow-anchor: none; flex: 0 0 auto; position: relative; width: 100%">${rows.join('')}</div></div></div><div class="fake-input"><div class="fake-input-inner rounded-xl bg-background"><div class="fake-chips"><button type="button" class="pl">⬡ 模组</button><button type="button" class="pl">◯ 评论 (0)</button><button type="button" class="sq">↓</button><button type="button" class="sq">▣</button><button type="button" class="sq">⌕</button><i class="vl"></i>${chips}</div><textarea id="chat-input" placeholder="在此输入您的消息"></textarea><div class="fake-tools"><span><button type="button" class="ic">⚙</button><button type="button" class="ic">ⓘ</button><button type="button" class="pill">✦ 模型</button></span><span><button type="button" class="pill">实时</button><button type="button" class="send">↵</button></span></div></div></div></div></div></main></div></div></div>
<script>
const M=${JSON.stringify(msgHtml).split('<').join('\\u003c')};
for(const el of document.querySelectorAll('[data-m]'))el.innerHTML=M[el.dataset.m];
const list=document.getElementById('list');
window.lay=()=>{let y=0;for(const r of list.children){r.style.top=y+'px';y+=r.getBoundingClientRect().height}list.style.height=y+'px'};
window.place=(mode)=>{const c=document.getElementById('conversation');if(mode==='end')c.scrollTop=c.scrollHeight;else if(mode==='latest'){const a=[...document.querySelectorAll('.rili-markdown-renderer')].pop();c.scrollTop=a.getBoundingClientRect().top-c.getBoundingClientRect().top+c.scrollTop-110}else c.scrollTop=Number(mode)};
lay();place('latest');
</script></body></html>`;
const htmlPath = path.join(outDir, '页面.html');
fs.writeFileSync(htmlPath, page);

// ---- 无头浏览器
const chrome = opt.chrome || ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', '/usr/bin/google-chrome', '/usr/bin/chromium'].find((p) => fs.existsSync(p));
const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'dryrun_'));
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files', '--no-first-run', '--remote-debugging-port=0', `--user-data-dir=${prof}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let port = null;
for (let i = 0; i < 200 && !port; i++) { await sleep(100); try { port = fs.readFileSync(path.join(prof, 'DevToolsActivePort'), 'utf8').split(/\s+/)[0].trim(); } catch {} }
const target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), waiters = [], failed = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Network.loadingFailed' || (m.method === 'Network.responseReceived' && m.params.response.status >= 400)) failed.push(m.params.requestId);
  if (m.method === 'Network.requestWillBeSent') reqs.set(m.params.requestId, m.params.request.url);
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const reqs = new Map();
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const evalJs = async (expression) => (await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true })).result?.result?.value;
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false }); const f = path.join(outDir, name); fs.writeFileSync(f, Buffer.from(r.result.data, 'base64')); return f; };
await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
const FINISH = `document.getAnimations().forEach((a)=>{try{if(a.timeline instanceof DocumentTimeline&&a.effect&&a.effect.getTiming().iterations!==Infinity)a.finish()}catch(e){}});`;
const report = [];
async function pass(w, h, mobile, pre) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: !!mobile });
  await send('Emulation.setFocusEmulationEnabled', { enabled: true });
  const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
  await send('Page.navigate', { url: pathToFileURL(path.resolve(htmlPath)).href });
  await loaded;
  await sleep(Number(opt.wait || 2500));
  await evalJs(`${FINISH}window.lay(),window.place('latest'),1`);
  await sleep(300);
  await shot(pre + '00_正文.png');
  await evalJs(`window.place('end'),1`);
  await sleep(300);
  await shot(pre + '00_正文_末尾.png');
  // 正文里的演出（检定面板、起手、技）一样一张：把那一处滚到视口中间再截
  if (!mobile) {
    const fx = { 判: '.jg-hd', 起手: '.sz-rite', 技: '.sz-waza' };
    for (const [name, sel] of Object.entries(fx)) {
      const n = await evalJs(`[...document.querySelectorAll('.rili-markdown-renderer')].pop().querySelectorAll('${sel}').length`);
      for (let i = 0; i < Math.min(n || 0, 2); i++) {
        await evalJs(`(()=>{const el=[...document.querySelectorAll('.rili-markdown-renderer')].pop().querySelectorAll('${sel}')[${i}];const c=document.getElementById('conversation');const r=el.getBoundingClientRect();c.scrollTop+=r.top-${Math.round(h * 0.28)};${FINISH}return 1})()`);
        await sleep(350);
        await shot(`${pre}00_正文_${name}${i + 1}.png`);
      }
    }
  }
  // 页签：最新一条里看得见的那几个
  const tabs = await evalJs(`(()=>{const last=[...document.querySelectorAll('.rili-markdown-renderer')].pop();return [...last.querySelectorAll('.sz-tab')].map((t)=>{const c=[...t.classList].find((x)=>/^t-/.test(x));const s=getComputedStyle(t);return {k:c?c.slice(2):'',name:(t.innerText||'').trim().replace(/\\s+/g,''),shown:s.display!=='none'&&s.visibility!=='hidden'&&t.getBoundingClientRect().width>0}})})()`) || [];
  if (!mobile) report.push('页签：' + (tabs.length ? tabs.map((t) => `${t.k}〔${t.name}〕${t.shown ? '' : '（藏着）'}`).join('、') : '一个也没有（大框没出来）'));
  const want = opt.tabs ? opt.tabs.split(',') : tabs.filter((t) => t.shown && t.k && t.k !== 'prose').map((t) => t.k);
  let n = 1;
  for (const k of want) {
    const r = await evalJs(`(async()=>{const last=[...document.querySelectorAll('.rili-markdown-renderer')].pop();const tab=last.querySelector('.sz-tab.t-${k} input');if(!tab)return null;tab.click();await new Promise((r)=>setTimeout(r,700));${FINISH}window.lay();const p=last.querySelector('.sz-page.p-${k}')||last.querySelector('.p-${k}');const c=document.getElementById('conversation');if(p)c.scrollTop=p.getBoundingClientRect().top-c.getBoundingClientRect().top+c.scrollTop-112;await new Promise((r)=>setTimeout(r,350));return p?{text:p.innerText,h:Math.round(p.getBoundingClientRect().height)}:{text:'',h:0}})()`);
    if (!r) { if (!mobile) report.push(`\n━━ 页 ${k}：点不到页签`); continue; }
    const tag = String(n++).padStart(2, '0');
    await shot(`${pre}${tag}_${k}.png`);
    if (!mobile && r.h > h - 150) { await evalJs(`(()=>{const c=document.getElementById('conversation');c.scrollTop+=${h - 260};return 1})()`); await sleep(250); await shot(`${pre}${tag}_${k}_下一屏.png`); }
    if (!mobile) report.push(`\n━━ 页 ${k}（高 ${r.h}px）看得见的字：\n` + (r.text || '（空）').replace(/\n{2,}/g, '\n').trim());
  }
}
await pass(W, H, false, '');
// ---- 查：最新一条里残留的记录记号
const chk = await evalJs(`(()=>{const last=[...document.querySelectorAll('.rili-markdown-renderer')].pop();const all=last.innerText;const prose=last.querySelector('.sz-page.p-prose')||last;
const lines=all.split('\\n');const sect=lines.filter((l)=>l.includes('§')).slice(0,40);const bars=lines.filter((l)=>/[｜|]/.test(l)).slice(0,40);
const imgs=[...last.querySelectorAll('*')].map((el)=>getComputedStyle(el).backgroundImage).filter((b)=>b&&b!=='none'&&b.includes('url(')).map((b)=>b.replace(/^.*?url\\("?/,'').replace(/"?\\).*$/,'')).filter((u)=>!u.startsWith('data:'));
const q=(s)=>last.querySelectorAll(s).length;
return {sect,bars,nimg:new Set(imgs).size,cnt:{'对话 sz-say':q('.sz-say'),'浮栏的人 sz-pfc':q('.sz-pfc'),'技 sz-waza':q('.sz-waza'),'起手 sz-rite':q('.sz-rite'),'角色卡 sz-npc':q('.sz-npc'),'背包格 sz-cell':q('.sz-cell'),'分支':q('[data-action="set-textinput"]')},prose:(prose.innerText||'').slice(0,6000)}})()`);
const proseTxt = chk?.prose || '';
report.unshift(`渲染：${fxList}\n视口 ${W}×${H}\n` + notes.join('\n'));
report.push('\n━━ 残留的 §（看得见的字里，至多四十行）：' + (chk.sect.length ? '\n' + chk.sect.map((l) => '  ' + l.slice(0, 160)).join('\n') : ' 无'));
report.push('━━ 带竖线的行（看得见的字里，至多四十行）：' + (chk.bars.length ? '\n' + chk.bars.map((l) => '  ' + l.slice(0, 160)).join('\n') : ' 无'));
report.push('━━ 各样东西出了几个：' + Object.entries(chk.cnt).map(([k, v]) => `${k} ${v}`).join('｜'));
const bad = [...new Set(failed.map((id) => reqs.get(id)).filter(Boolean))];
report.push(`━━ 图：页面用到 ${chk.nimg} 张外头的图，取不到的 ${bad.length} 张` + (bad.length ? '\n' + bad.slice(0, 30).map((u) => '  ' + u).join('\n') : ''));
report.push('\n━━ 正文页（或整条）看得见的字，前六千字：\n' + proseTxt.replace(/\n{2,}/g, '\n'));
if (opt.mobile) await pass(390, 844, true, 'm_');
fs.writeFileSync(path.join(outDir, '检查.txt'), report.join('\n') + '\n');
console.log(report.slice(0, 2).join('\n').split('\n').slice(0, 6).join('\n'));
console.log('残留 § ' + chk.sect.length + ' 行，带竖线 ' + chk.bars.length + ' 行，取不到的图 ' + bad.length + ' 张；' + Object.entries(chk.cnt).map(([k, v]) => `${k.split(' ')[0]} ${v}`).join(' '));
ws.close();
proc.kill();
try { fs.rmSync(prof, { recursive: true, force: true }); } catch {}
