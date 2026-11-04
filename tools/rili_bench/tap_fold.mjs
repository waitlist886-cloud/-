// 手机上输入栏折叠（11-04）：真的按下抬起，看点击落在谁身上。先跑一遍 static_bench.mjs 出 html，再跑这个。
// 用法：node tap_fold.mjs <static_bench 写的.html> [w=390] [h=844] [wrap=1 把输入框往里多包两层，照真页面]
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const [htmlPath, ...rest] = process.argv.slice(2);
const opt = Object.fromEntries(rest.map((a) => a.split('=')));
const W = Number(opt.w || 390), H = Number(opt.h || 844);
const chrome = ['C:/Program Files/Google/Chrome/Application/chrome.exe', 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].find((p) => fs.existsSync(p));
const prof = fs.mkdtempSync(path.join(os.tmpdir(), 'tap_fold_'));
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
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 2, mobile: false });
await send('Emulation.setFocusEmulationEnabled', { enabled: true });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: pathToFileURL(path.resolve(htmlPath)).href });
await loaded;
await sleep(1500);
const ev = async (expression) => { const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }); if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result.result.value; };
await ev(`(() => {
  window.lay && window.lay(); const c = document.getElementById('conversation'); c.scrollTop = c.scrollHeight;
  ${opt.wrap === '1' ? `const ta = document.querySelector('#chat-input'); const a = document.createElement('div'), b = document.createElement('div'); ta.parentNode.insertBefore(a, ta); a.appendChild(b); b.appendChild(ta);` : ''}
  window.__log = [];
  const d = (t) => t && t.tagName ? t.tagName.toLowerCase() + (t.id ? '#' + t.id : '') + (t.className && typeof t.className === 'string' ? '.' + t.className.split(' ')[0] : '') + (t.tagName === 'BUTTON' ? '[' + t.textContent.slice(0, 6) + ']' : '') : String(t);
  for (const n of ['mousedown', 'mouseup', 'click', 'focusin', 'focusout']) document.addEventListener(n, (e) => window.__log.push(n + ':' + d(e.target)), true);
  // 点预设平台会把字填进输入框，这里照做
  document.addEventListener('click', (e) => { const b = e.target.closest && e.target.closest('.fake-chips button:not(.pl):not(.sq)'); if (b) { const ta = document.querySelector('#chat-input'); ta.value = b.textContent; ta.dispatchEvent(new Event('input', { bubbles: true })); ta.focus(); } });
  return 1;
})()`);
const rect = (sel) => ev(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); const c = e.getBoundingClientRect(); return { x: c.left + c.width / 2, y: c.top + c.height / 2, shown: getComputedStyle(e).display !== 'none' && c.height > 0 }; })()`);
const state = () => ev(`(() => { const p = document.querySelector('.fake-input-inner').getBoundingClientRect(), s = document.getElementById('conversation').closest('.custom-styles'); return { 栏高: Math.round(p.height), 钮: Math.round(document.querySelector('.fake-chips').getBoundingClientRect().height), dock: getComputedStyle(s).getPropertyValue('--fm-dock').trim(), 焦点: document.activeElement.tagName, 字: document.querySelector('#chat-input').value }; })()`);
const flush = () => ev('(() => { const l = window.__log; window.__log = []; return l.join(" "); })()');
const tap = async (sel, name, x) => {
  const r = await rect(sel);
  const px = x === undefined ? r.x : x;
  // 无头里手势合成不出事件，按下抬起走鼠标那一路，点按时平台认的也是这一路的 mousedown、mouseup、click
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: px, y: r.y });
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: px, y: r.y, button: 'left', buttons: 1, clickCount: 1 });
  await sleep(Number(opt.press || 60));
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: px, y: r.y, button: 'left', clickCount: 1 });
  await sleep(40);
  const soon = await state();
  await sleep(600);
  console.log(`\n【${name}】目标显示着=${r.shown}\n  事件 ${await flush()}\n  刚点完 ${JSON.stringify(soon)}\n  稳定后 ${JSON.stringify(await state())}`);
};
console.log('一开始', JSON.stringify(await state()));
await tap('#chat-input', '点输入框');
await tap('.fake-tools .pill', '展开时点模型签（没字）');
await tap('#chat-input', '再点输入框');
await tap('.fake-chips .pl', '展开时点模组（没字）');
await tap('#chat-input', '再点输入框');
await tap('.fake-tools .send', '展开时点发送（没字）');
await tap('#chat-input', '再点输入框');
await tap('.fake-chips button:not(.pl):not(.sq)', '展开时点预设');
await tap('#chat-input', '点回输入框');
await tap('#conversation', '有字时点对话（失焦）');
await ev(`(() => { const ta = document.querySelector('#chat-input'); ta.value = ''; ta.dispatchEvent(new Event('input', { bubbles: true })); return 1; })()`);
await sleep(500);
console.log('\n清空以后', JSON.stringify(await state()));
await tap('#chat-input', '点输入框');
await tap('#conversation', '没字时点对话（失焦）');
// 输入框有焦点、没字的时候点页签：页签不能在手指底下挪走，这一下要点中
await tap('#chat-input', '再点输入框');
{ const b = await ev(`(() => { const t = [...document.querySelectorAll('.sz-tabs .t-bag, .sz-tabs label')].pop(); const c = t.getBoundingClientRect(); return { x: c.left + c.width / 2, y: c.top + c.height / 2, top: Math.round(innerHeight - c.bottom), h: t.className }; })()`);
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: b.x, y: b.y });
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: b.x, y: b.y, button: 'left', buttons: 1, clickCount: 1 });
  await sleep(60);
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: b.x, y: b.y, button: 'left', clickCount: 1 });
  await sleep(700);
  console.log(`
【有焦点没字时点页签】${JSON.stringify(b)}
  事件 ${await flush()}
  稳定后 ${JSON.stringify(await state())}`); }
ws.close();
proc.kill();
process.exit(0);
