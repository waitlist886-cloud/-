// 结构体检：每个样本过一遍卡里的显示正则（front-end），在无头 Chrome 里解析成 DOM，数每一页里有什么、页外漏了什么、看得见的字里残留的 § 和竖线
// 用法：node analyze.mjs <cases目录> <输出.json> [card=卡.json] [only=前缀,前缀]
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
const LIB = 'file:///E:/aldran_art/tools/dryrun/lib.mjs';
const { CARD_FULL, loadCard, readText, applyRules } = await import(LIB);
const [dir, outFile, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => { const i = a.indexOf('='); return [a.slice(0, i), a.slice(i + 1)]; }));
const card = loadCard(opt.card || CARD_FULL);
const rules = card.assistantRegexReplace;
let files = fs.readdirSync(dir).filter((f) => f.endsWith('.txt')).sort();
if (opt.only) files = files.filter((f) => opt.only.split(',').some((p) => f.startsWith(p)));
const html = {}, back = {};
for (const f of files) {
  const t = readText(path.join(dir, f));
  html[f] = applyRules(t, rules, 'front-end').replace(/<link\b[^>]*>/g, '');
  back[f] = applyRules(t, rules, 'back-end');
}
const page = `<!doctype html><html><head><meta charset="utf-8"></head><body>${files.map((f, i) => `<div class="msg" data-f="${i}"></div>`).join('')}
<script>
const H=${JSON.stringify(files.map((f) => html[f])).split('<').join('\\u003c')};
document.querySelectorAll('.msg').forEach((el)=>{el.innerHTML=H[el.dataset.f]});
const Q={foe:'.sz-foe',enc:'.sz-enc',wn:'.sz-wn',boss:'.sz-boss',cell:'.sz-cell',bagrow:'.sz-bagn',slot:'.sz-sl',npc:'.sz-npc',mm:'.sz-mm',nw:'.sz-nw',li:'li',say:'.sz-say',p:'p',f:'.sz-f',ab:'.sz-ab',jg:'.jg-w,.jg-hd',row:'.sz-row',table:'table',pre:'pre,code'};
function txt(n){return (n.textContent||'')}
const res=[...document.querySelectorAll('.msg')].map((m)=>{
  const top=[...m.childNodes].map((c)=>c.nodeType===3?(c.textContent.trim()?'#text:'+c.textContent.trim().slice(0,40):null):(c.tagName.toLowerCase()+(c.className?'.'+String(c.className).split(' ').slice(0,3).join('.'):''))).filter(Boolean);
  const secs=[...m.querySelectorAll('.sz-page')].map((s)=>{const k=([...s.classList].find((x)=>/^p-/.test(x))||(s.classList.contains('sz-prose')?'prose':'?'));const c={};for(const [n,q] of Object.entries(Q)){const v=s.querySelectorAll(q).length;if(v)c[n]=v}
    // 本页“自己的”字：不算嵌在里面的别的 sz-page
    const own=[];const w=document.createTreeWalker(s,NodeFilter.SHOW_TEXT);let x;while((x=w.nextNode())){let p=x.parentElement;while(p&&p!==s&&!p.classList.contains('sz-page'))p=p.parentElement;if(p===s)own.push(x.textContent)}
    const t=own.join('');return {k,c,len:t.length,sect:(t.match(/§[^\\s]{0,12}/g)||[]).slice(0,8),bars:(t.match(/[^\\n｜|]{0,10}[｜|][^\\n｜|]{0,10}/g)||[]).length,nested:s.querySelectorAll('.sz-page').length}});
  const all=txt(m);
  const navs=m.querySelectorAll('nav.sz-tabs').length;
  return {top,secs,navs,hud:m.querySelectorAll('.sz-hud').length,sect:(all.match(/§[^\\s]{0,14}/g)||[]).slice(0,12),secLeft:(all.match(/§/g)||[]).length,raw:(all.match(/[ⓔⓩⓐⓒⓦⓖⓡⓙⓓⓠⓨⓑⓧⓛⓚⓜⓝⓂⓈⒷⓋⓍ]/g)||[]).length,lt:(all.match(/[<>]/g)||[]).length,len:all.length};
});
document.body.setAttribute('data-res',JSON.stringify(res));
document.title='done';
</script></body></html>`;
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'fmtana_'));
const pf = path.join(tmp, 'p.html');
fs.writeFileSync(pf, page);
const chrome = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const prof = path.join(tmp, 'prof');
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--no-first-run', '--remote-debugging-port=0', `--user-data-dir=${prof}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let port = null;
for (let i = 0; i < 300 && !port; i++) { await sleep(100); try { port = fs.readFileSync(path.join(prof, 'DevToolsActivePort'), 'utf8').split(/\s+/)[0].trim(); } catch {} }
const target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pend = new Map();
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pend.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
await send('Page.enable');
await send('Page.navigate', { url: pathToFileURL(pf).href });
let res = null;
for (let i = 0; i < 200 && !res; i++) { await sleep(150); const r = await send('Runtime.evaluate', { expression: 'document.body&&document.body.getAttribute("data-res")', returnByValue: true }); res = r.result?.result?.value; }
ws.close(); proc.kill();
const out = {};
files.forEach((f, i) => { out[f] = JSON.parse(res)[i]; out[f].back_sect_lines = back[f].split('\n').filter((l) => /^§/.test(l)).length; out[f].back_len = back[f].length; });
fs.writeFileSync(outFile, JSON.stringify(out, null, 1));
for (const [f, r] of Object.entries(out)) {
  const secs = r.secs.map((s) => `${s.k.replace('p-', '')}[${Object.entries(s.c).map(([k, v]) => k + v).join(' ')}${s.sect.length ? ' §' + s.sect.length : ''}${s.bars ? ' ｜' + s.bars : ''}]`).join(' ');
  const top = r.top.filter((t) => !/^(details\.sz-hud|div\.sz-page|section\.sz-page|nav\.sz-tabs)/.test(t));
  console.log(`${f}\n  hud ${r.hud} nav ${r.navs} §残留 ${r.secLeft} 记号残留 ${r.raw} 尖括号 ${r.lt}${top.length ? ' 页外:' + JSON.stringify(top.slice(0, 6)) : ''}\n  ${secs}`);
}
