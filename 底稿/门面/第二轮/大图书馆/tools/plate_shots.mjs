// 大图书馆插图接进页面以后的截图（11-24）：无头 Chrome + CDP。先起 共用/utf8_server.py（8774）。
//   node plate_shots.mjs <pc|m> <书键> <第几张图> [名字]     翻到这一张图所在的那一叠截一张，再点标签折起原文截一张，写 ../插图/截图/
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
const OUT = process.env.OUT || 'E:/aldran_art/底稿/门面/第二轮/大图书馆/插图/截图';
mkdirSync(OUT, { recursive: true });
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const [, , which = 'pc', KEY = 'arcane-wytj', NTH = '1', NAME] = process.argv;
const mob = which === 'm';
const PORT = 9481 + (mob ? 1 : 0);
const SHELL = 'http://127.0.0.1:8774/' + encodeURI('小样_外壳/local.html');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const proc = spawn(CH, ['--headless=new', '--hide-scrollbars', '--no-first-run', '--enable-unsafe-swiftshader', `--remote-debugging-port=${PORT}`, `--user-data-dir=${path.join(os.tmpdir(), 'plate_cdp_' + PORT)}`, '--window-size=1920,945', 'about:blank'], { stdio: 'ignore' });
let ws, seq = 0; const wait = new Map(), events = [], errs = [];
const send = (method, params = {}) => { const id = ++seq; ws.send(JSON.stringify({ id, method, params })); return new Promise((res, rej) => wait.set(id, { res, rej })); };
async function connect() {
  for (let i = 0; i < 60; i++) {
    try {
      const t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
      ws = new WebSocket(t.webSocketDebuggerUrl);
      await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
      ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait.has(d.id)) { const w = wait.get(d.id); wait.delete(d.id); d.error ? w.rej(new Error(d.error.message)) : w.res(d.result); } else { events.push(d);
        if (d.method === 'Runtime.exceptionThrown') errs.push('异常 ' + (d.params.exceptionDetails.exception ? d.params.exceptionDetails.exception.description : d.params.exceptionDetails.text).slice(0, 300));
        if (d.method === 'Runtime.consoleAPICalled' && (d.params.type === 'error' || d.params.type === 'warning')) errs.push(d.params.type + ' ' + d.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
        if (d.method === 'Log.entryAdded' && d.params.entry.level === 'error') errs.push('log ' + d.params.entry.text.slice(0, 200) + ' ' + (d.params.entry.url || '').slice(-80)); } };
      return;
    } catch { await sleep(300); }
  }
  throw new Error('连不上 Chrome');
}
const js = (expr) => send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }).then((r) => { if (r.exceptionDetails) throw new Error(expr.slice(0, 80) + ' → ' + (r.exceptionDetails.exception || {}).description); return r.result && r.result.value; });
async function shot(name) { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); writeFileSync(path.join(OUT, name + '.jpg'), Buffer.from(r.data, 'base64')); console.log('截图', name); }
const L = 'window.Library';
try {
  await connect(); await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
  const [w, h] = mob ? [390, 844] : [1920, 945];
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: mob ? 2 : 1, mobile: mob, screenWidth: w, screenHeight: h });
  await send('Emulation.setTouchEmulationEnabled', { enabled: mob });
  await send('Page.navigate', { url: SHELL });
  for (let i = 0; i < 150 && !events.some((e) => e.method === 'Page.loadEventFired'); i++) await sleep(100);
  await sleep(2500);
  await js(`${L}.openBook(${JSON.stringify(KEY)})`);
  for (let i = 0; i < 60 && (await js(`${L}.state.book`)) !== KEY; i++) await sleep(150);
  for (let i = 0; i < 40 && await js(`${L}.state.busy`); i++) await sleep(150);
  await sleep(1500);
  if (mob) await js(`${L}._mode('page')`);
  // 第 NTH 张图在哪一节
  const where = await js(`(async()=>{const r=await fetch(${JSON.stringify('../共用/data/lib/' + KEY + '.json')});const b=await r.json();for(let i=0;i<b.secs.length;i++)for(const x of b.secs[i].b)if(x.k==='fig'&&x.n===${+NTH})return {i,im:x.im||null};return null})()`);
  console.log('图在', JSON.stringify(where));
  await js(`${L}._goto(${where.i})`); await sleep(800);
  const spreads = await js(`${L}.state.spreads`);
  let found = -1;
  for (let s = 0; s < spreads; s++) {
    await js(`${L}._goto(${where.i}, ${s})`); await sleep(250);
    const vis = await js(`(()=>{const win=document.querySelector('#lib .rd-win').getBoundingClientRect();const f=[...document.querySelectorAll('#lib figure.lx-plate details')].find(d=>+d.dataset.n===${+NTH});if(!f)return false;const r=f.closest('figure').getBoundingClientRect();return r.left>=win.left-2&&r.right<=win.right+2&&r.width>0})()`);
    if (vis) { found = s; break; }
  }
  console.log('在第', found, '叠，共', spreads);
  await sleep(1500);
  await js(`${L}._goto(${where.i}, ${Math.max(0, found)})`); await sleep(800);
  const info = await js(`(()=>{const f=[...document.querySelectorAll('#lib figure.lx-plate')];return f.map(x=>{const i=x.querySelector('img');return {n:x.querySelector('details').dataset.n,w:i.clientWidth,h:i.clientHeight,ok:i.complete&&i.naturalWidth>0}})})()`);
  console.log('这一页的插图', JSON.stringify(info));
  const base = NAME || (which + '_' + KEY + '_' + NTH);
  await shot(base + '_图');
  await js(`(()=>{const d=[...document.querySelectorAll('#lib figure.lx-plate details')].find(d=>+d.dataset.n===${+NTH});d.open=false})()`);
  await sleep(1200);
  await js(`${L}._goto(${where.i}, ${Math.max(0, found)})`); await sleep(800);
  console.log('折起以后', JSON.stringify(await js(`${L}.state`)));
  await shot(base + '_折起原文');
} catch (e) { console.error('停了：', e.message); }
finally {
  console.log('控制台报错', errs.length); for (const e of errs) console.log('  ', e);
  try { ws && ws.close(); } catch {} proc.kill();
}
