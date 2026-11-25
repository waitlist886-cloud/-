// 风月外壳的简介页（薄壳）放进一格沙箱里的 srcdoc 框跑一遍（11-25）。不装依赖，本机 Chrome 或 Edge 无头跑，要连外网。一般不直接叫它，走 fy_descr_all.py。
//   node fy_descr_check.mjs <外壳_纪.json 或者薄壳.html> <输出前缀> <start> <only,逗号隔开> [w=1920] [h=945] [build={"book":..}] [mirrors=bad]
// 框是 sandbox="allow-scripts allow-popups allow-forms allow-modals"（没有同源，所以没有本地存储，跟探针在风月上量到的一样；风月真页面给框的是哪几样没读过）。
// 看：一、从图床取到门面外壳，直接翻开 start 那一本；二、书里往别纪翻（goto）拦不拦、出不出那一句；三、回牌桌以后点“此刻”那张牌、
// “翻开这一本”拦不拦；四、建档走到确认页，“填进输入框”那一枚在不在、“复制”是不是主钮、说明是不是复制的说法；接续旅印那一格同样。
// 宿主页记下框里往外发的消息（有没有往平台填输入框的那一种）。
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const [cardFile, outPfx, START, ONLYS, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => { const i = a.indexOf('='); return [a.slice(0, i), a.slice(i + 1)]; }));
const W = Number(opt.w || 1920), H = Number(opt.h || 945);
const ONLY = ONLYS.split(',');
const ALL = ['moon', 'strife', 'bronze', 'maze', 'now'];
let descr = /\.html$/.test(cardFile) ? fs.readFileSync(cardFile, 'utf8') : JSON.parse(fs.readFileSync(cardFile, 'utf8')).descr;
if (opt.mirrors === 'bad') descr = descr.replace(/https:\/\/(cdn|fastly|gcore|testingcf|quantil)\.jsdelivr\.net\//g, 'https://127.0.0.1:9/').replace(/https:\/\/raw\.githubusercontent\.com\//g, 'https://127.0.0.1:9/');
const lit = JSON.stringify(descr).replace(/<\//g, '<\\/').replace(/<!--/g, '<\\!--');
const host = `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body{margin:0;height:100%;background:#333}iframe{position:fixed;inset:0;width:100%;height:100%;border:0}</style></head><body>
<iframe id="f" sandbox="allow-scripts allow-popups allow-forms allow-modals"></iframe>
<script>window.__msgs=[];addEventListener('message',function(e){try{window.__msgs.push(JSON.stringify(e.data).slice(0,200))}catch(x){}});document.getElementById('f').srcdoc=${lit};</script></body></html>`;
fs.mkdirSync(path.dirname(path.resolve(outPfx)), { recursive: true });
const hostPath = outPfx + '_host.html';
fs.writeFileSync(hostPath, host);

const chrome = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find((p) => fs.existsSync(p));
const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'fy_descr_'));
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--remote-debugging-port=0', '--disable-site-isolation-trials',
  '--disable-features=IsolateSandboxedIframes,IsolateOrigins,site-per-process', `--user-data-dir=${prof}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let port = null;
// 机器忙的时候无头浏览器二十秒起不来，等到一分半
for (let i = 0; i < 900 && !port; i++) { await sleep(100); try { port = fs.readFileSync(path.join(prof, 'DevToolsActivePort'), 'utf8').split(/\s+/)[0].trim(); } catch {} }
const target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find((t) => t.type === 'page');
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), ctx = new Map(), errs = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.executionContextCreated') { const c = m.params.context; if (c.auxData && c.auxData.isDefault) ctx.set(c.auxData.frameId, c.id); }
  else if (m.method === 'Runtime.executionContextDestroyed') { for (const [k, v] of ctx) if (v === m.params.executionContextId) ctx.delete(k); }
  else if (m.method === 'Runtime.exceptionThrown') errs.push((m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text || '').slice(0, 200));
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 800 });
await send('Emulation.setFocusEmulationEnabled', { enabled: true });
await send('Page.navigate', { url: pathToFileURL(path.resolve(hostPath)).href });

async function frames() {   // [主页, 薄壳那一格, 书那一格…]
  const t = (await send('Page.getFrameTree')).result.frameTree;
  const out = [];
  (function walk(n, d) { out.push({ id: n.frame.id, d, name: n.frame.name || '', url: (n.frame.url || '').slice(0, 40) }); for (const c of (n.childFrames || [])) walk(c, d + 1); })(t, 0);
  return out;
}
async function ev(depth, expr, which = 0) {
  const fs_ = (await frames()).filter((f) => f.d === depth);
  const f = fs_[which];
  if (!f || !ctx.has(f.id)) return { err: '没有这一格 d=' + depth };
  const r = await send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, contextId: ctx.get(f.id), returnByValue: true, awaitPromise: true });
  if (r.result?.exceptionDetails) return { err: (r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text || '').slice(0, 300) };
  return r.result?.result?.value;
}
async function until(depth, expr, ms) { const t0 = Date.now(); for (;;) { const v = await ev(depth, 'return ' + expr); if (v && !v.err) return Date.now() - t0; if (Date.now() - t0 > ms) return -1; await sleep(250); } }
const shot = async (tag) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 72 }); const f = `${outPfx}_${tag}.jpg`; fs.writeFileSync(f, Buffer.from(r.result.data, 'base64')); return path.basename(f); };
const R = { card: path.basename(cardFile), w: W, start: START, only: ONLY, checks: [], bad: [] };
const ok = (name, pass, info) => { R.checks.push([name, !!pass, info ?? '']); if (!pass) R.bad.push(name); };
const TIP = `(()=>{const e=[...document.querySelectorAll('div[role="status"]')].find(x=>x.textContent.indexOf('这一张卡里只有')>=0);return e?e.style.opacity+'|'+e.textContent:''})()`;
const ST = 'JSON.stringify(Object.assign({},window.Shell&&Shell.state,{pend:undefined}))';

if (opt.mirrors === 'bad') {
  // 图床连不上：该出“门面没有载下来”和“用简式建档”，点了换成简式建档那一页
  const t = await until(1, `!!document.getElementById('useold')`, 90000);
  ok('连不上时出退路的钮', t >= 0, t + 'ms');
  await shot('退路_钮');
  await ev(1, `document.getElementById('useold').click();return 1`);
  await sleep(1200);
  const v = await ev(1, `return JSON.stringify({title:document.title,copy:!!document.getElementById('copy'),fill:!!document.getElementById('fill'),eras:[...document.querySelectorAll('#era option')].map(o=>o.textContent),lines:document.querySelectorAll('#line option').length,txt:document.body.innerText.slice(0,160)})`);
  R.lite = v;
  let j = {}; try { j = JSON.parse(v); } catch {}
  ok('简式建档那一页出来了', j.copy === true, v);
  ok('简式建档没有填输入框那一枚', j.fill === false);
  await shot('退路_简式建档');
  // 填个名字，看凭证出不出得来
  const c = await ev(1, `const n=document.querySelector('input[type=text],#name');if(n){n.value='诺拉';n.dispatchEvent(new Event('input',{bubbles:true}));}const o=document.getElementById('out')||document.querySelector('textarea,pre');return o?(o.value||o.textContent||'').slice(0,200):'无'`);
  R.liteCred = c;
} else {
  // 一、取到外壳、直接翻开这一纪的书
  let t = await until(1, '!!(window.Shell&&Shell.openBook&&window.FRONT_CFG)', 60000);
  ok('从图床取到门面外壳', t >= 0, t + 'ms');
  const cfg = await ev(1, 'return JSON.stringify({start:FRONT_CFG.start,only:FRONT_CFG.only,nofill:FRONT_CFG.nofill,mirror:FRONT_CFG.mirror,n:FRONT_CFG.n,books:Object.keys(FRONT_CFG.books),inFrame:window.parent!==window,ls:(()=>{try{localStorage.setItem("a","1");return "有"}catch(e){return "没有"}})()})');
  R.cfg = cfg;
  t = await until(1, `(Shell.state.cur===${JSON.stringify(START)}&&Shell.state.frame)`, 45000);
  ok('直接翻开 ' + START, t >= 0, t + 'ms ' + (await ev(1, 'return ' + ST)));
  await until(1, `document.querySelector('#sh-book .sh-veil')&&document.querySelector('#sh-book .sh-veil').classList.contains('off')`, 45000);
  await sleep(2500);
  R.shots = [await shot('1_翻开')];
  R.bookTitle = await ev(1, `const f=document.getElementById('sh-frame');return f?f.title:''`);
  // 二、书里往别纪翻
  const other = ALL.filter((b) => !ONLY.includes(b));
  for (const b of other) {
    await ev(2, `parent.postMessage({aldran:1,t:'goto',book:${JSON.stringify(b)},turn:1},'*');return 1`);
    await sleep(1500);
    const st = JSON.parse(await ev(1, 'return ' + ST)), tip = await ev(1, 'return ' + TIP);
    ok('书里翻 ' + b + ' 拦下', st.cur === START && /^1\|这一张卡里只有/.test(tip), st.cur + ' ' + tip);
    if (b === other[0]) R.shots.push(await shot('2_拦下'));
    await sleep(400);
  }
  for (const b of ONLY.filter((x) => x !== START)) {      // 这一张卡里的另一本（迷宫纪那一张：此刻翻前传）放行
    await ev(2, `parent.postMessage({aldran:1,t:'goto',book:${JSON.stringify(b)}},'*');return 1`);
    t = await until(1, `(Shell.state.cur===${JSON.stringify(b)}&&Shell.state.frame)`, 30000);
    ok('书里翻 ' + b + ' 放行', t >= 0, t + 'ms');
    await sleep(3500);
    R.shots.push(await shot('2_翻' + b));
  }
  // 三、回牌桌
  await ev(2, `parent.postMessage({aldran:1,t:'table'},'*');return 1`);
  t = await until(1, '(!Shell.state.cur&&!Shell.state.frame)', 8000);
  ok('回得了牌桌', t >= 0, await ev(1, 'return ' + ST));
  await ev(1, 'if(window.__tb&&__tb.skip)__tb.skip();return 1');
  await sleep(2500);
  R.shots.push(await shot('3_牌桌'));
  await ev(1, `document.getElementById('nowCard').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));return 1`);
  await sleep(1800);
  let st = JSON.parse(await ev(1, 'return ' + ST)), tip = await ev(1, 'return ' + TIP);
  if (ONLY.includes('now')) { t = await until(1, `Shell.state.cur==='now'`, 15000); ok('牌桌上点此刻放行', t >= 0, t + 'ms'); await ev(1, 'Shell.toTable();return 1'); await sleep(800); }
  else ok('牌桌上点此刻拦下', !st.cur && /^1\|/.test(tip), st.cur + ' ' + tip);
  for (let k = 0; k < 4; k++) {
    await sleep(3800);     // 那一句话三秒六收
    await ev(1, `Shell.onEra(${k});document.getElementById('openBook').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));return 1`);
    await sleep(1500);
    st = JSON.parse(await ev(1, 'return ' + ST)); tip = await ev(1, 'return ' + TIP);
    if (ONLY.includes(ALL[k])) { ok('牌桌上翻 ' + ALL[k] + ' 放行', st.cur === ALL[k], st.cur); await ev(1, 'Shell.toTable();return 1'); await sleep(800); }
    else ok('牌桌上翻 ' + ALL[k] + ' 拦下', !st.cur && /^1\|/.test(tip), st.cur + ' ' + tip);
  }
  // 四、建档走到确认页
  if (opt.build) {
    const M = JSON.parse(opt.build);
    const b0 = await ev(1, `await Shell.startBuild(${JSON.stringify(M)});return 'ok'`);
    await sleep(2500);
    R.shots.push(await shot('4_建档'));
    const rs = await ev(1, `__bd.resume();await new Promise(r=>setTimeout(r,500));const p=document.querySelector('.bx-pop');return p?JSON.stringify({rfill:!!p.querySelector('[data-a="rfill"]'),rcopy:(p.querySelector('[data-a="rcopy"]')||{}).className||''}):'没有这一格'`);
    let j = {}; try { j = JSON.parse(rs); } catch {}
    ok('接续旅印没有填输入框那一枚、复制是主钮', j.rfill === false && /\bpri\b/.test(j.rcopy || ''), rs);
    R.shots.push(await shot('4_接续旅印'));
    await ev(1, `const x=document.querySelector('.bx-pop [data-a="rclose"]');if(x)x.click();return 1`);
    await sleep(400);
    await ev(1, `__bd.way('direct');return 1`);
    await sleep(600); await until(1, '(window.__bd&&!__bd.busy)', 15000); await sleep(400);
    const m1 = await ev(1, `__bd.F.name='诺拉';__bd.F.sex=__bd.F.sex||'女';const c=__bd.cred();__bd.mint();return (c||'').slice(0,60)`);
    R.build = { start: b0, cred: m1 };
    t = await until(1, `(()=>{const s=document.getElementById('sh-seal');return s&&!s.hidden&&s.querySelector('.sl-acts')})()`, 30000);
    await sleep(1500);
    const sl = await ev(1, `const s=document.getElementById('sh-seal');return JSON.stringify({fill:!!s.querySelector('[data-a="fill"]'),copy:(s.querySelector('[data-a="copy"]')||{}).className||'',sub:(s.querySelector('.sl-hd .sub')||{}).textContent||'',acts:[...s.querySelectorAll('.sl-acts button')].map(b=>b.textContent)})`);
    j = {}; try { j = JSON.parse(sl); } catch {}
    ok('确认页出来了', t >= 0, t + 'ms');
    ok('确认页没有填输入框那一枚', j.fill === false, sl);
    ok('确认页复制是主钮', /\bgo\b/.test(j.copy || ''), j.copy);
    ok('确认页的说明是复制的说法', /复制/.test(j.sub || '') && !/填进输入框/.test(j.sub || ''), j.sub);
    R.shots.push(await shot('4_确认页'));
    // 真点一下“复制”（带用户手势的点击）：沙箱框里 navigator.clipboard 多半不给，看退回 execCommand 那一路成不成
    const rc = await ev(1, `const b=document.querySelector('#sh-seal [data-a="copy"]');b.scrollIntoView({block:'center'});await new Promise(r=>setTimeout(r,300));const r=b.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]`);
    if (Array.isArray(rc)) { for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x: rc[0], y: rc[1], button: 'left', clickCount: 1 }); }
    await sleep(900);
    R.afterCopy = await ev(1, `return (document.querySelector('#sh-seal .sl-tip')||{}).textContent||''`);
    ok('真点复制以后说复制好了', /复制好了/.test(R.afterCopy || ''), R.afterCopy);
    R.shots.push(await shot('4_复制以后'));
  }
  R.msgs = await ev(0, 'return JSON.stringify(window.__msgs.slice(0,8))');
  ok('没往平台发填输入框的消息', !/set-input/.test(R.msgs || ''), R.msgs);
}
R.errs = errs.slice(0, 8);
console.log(JSON.stringify(R, null, 1));
ws.close();
proc.kill();
process.exit(R.bad.length ? 1 : 0);
