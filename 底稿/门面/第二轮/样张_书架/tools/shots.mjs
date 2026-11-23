// 书架样张截图（11-23）：起一个无头 Chrome，走 CDP（Node 自带的 WebSocket，不装包），电脑 1536×864、手机 390×844 各一套。
//   node shots.mjs [pc|m]     写 ../截图/
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import os from 'node:os';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PAGE = pathToFileURL(path.join(HERE, '..', 'index.html')).href;
const OUT = path.join(HERE, '..', '截图');
mkdirSync(OUT, { recursive: true });
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9361;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const proc = spawn(CH, ['--headless=new', '--disable-gpu', '--hide-scrollbars', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${path.join(os.tmpdir(), 'shelf_cdp')}`, '--window-size=1536,864', 'about:blank'], { stdio: 'ignore' });

let ws, seq = 0;
const wait = new Map(), events = [];
function send(method, params = {}) {
  const id = ++seq;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((res, rej) => wait.set(id, { res, rej }));
}
async function connect() {
  for (let i = 0; i < 50; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' });
      const t = await r.json();
      ws = new WebSocket(t.webSocketDebuggerUrl);
      await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
      ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && wait.has(d.id)) { const w = wait.get(d.id); wait.delete(d.id); d.error ? w.rej(new Error(d.error.message)) : w.res(d.result); } else events.push(d); };
      return;
    } catch { await sleep(300); }
  }
  throw new Error('连不上 Chrome');
}
async function go(w, h, mobile, q) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile, screenWidth: w, screenHeight: h });
  await send('Emulation.setTouchEmulationEnabled', { enabled: mobile });
  events.length = 0;
  await send('Page.navigate', { url: PAGE + (q || '') });
  for (let i = 0; i < 100 && !events.some(e => e.method === 'Page.loadEventFired'); i++) await sleep(100);
  await send('Runtime.evaluate', { expression: 'document.fonts.ready.then(()=>1)', awaitPromise: true });
  await sleep(900);
}
const js = expr => send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }).then(r => r.result && r.result.value);
async function center(sel) { return js(`(()=>{const r=document.querySelector(${JSON.stringify(sel)}).getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()`); }
async function hover(sel) { const [x, y] = await center(sel); await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); }
async function click(sel) { const [x, y] = await center(sel); await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 }); await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 }); }
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 88 });
  writeFileSync(path.join(OUT, name + '.jpg'), Buffer.from(r.data, 'base64'));
  console.log(name);
}

async function set(p, w, h, mob) {
  await go(w, h, mob, ''); await shot(p + '_01_书架全景');
  if (mob) { await go(w, h, mob, '?lit=guild'); } else { await go(w, h, mob, ''); await hover('.sp[data-k="guild"]'); await sleep(500); }
  await shot(p + '_02_指着一本');
  if (!mob) { await hover('.sp[data-k="h2"]'); await sleep(500); await shot(p + '_02b_指着烫手的'); }
  await go(w, h, mob, ''); await click('.sp[data-k="guild"]'); await sleep(760); await shot(p + '_03a_抽出来');
  await sleep(640); await shot(p + '_03b_转到封面');
  await sleep(500); await shot(p + '_03c_翻开');
  await sleep(1700); await shot(p + '_04_扉页');
  await go(w, h, mob, '?open=1'); await shot(p + '_05_前言');
  await go(w, h, mob, '?open=2'); await shot(p + '_06_目录');
  await go(w, h, mob, '?open=7'); await shot(p + '_07_正文一页带注脚');
  if (mob) { await js(`document.querySelector('.rd-body').scrollTop=1e5`); await sleep(300); await shot(p + '_07b_正文页边注脚'); }
  await go(w, h, mob, '?open=9'); await shot(p + '_08_红边的单子');
  await go(w, h, mob, '?open=12&spoil=1'); if (mob) { await js(`document.querySelector('.rd-body').scrollTop=1e5`); await sleep(300); } await shot(p + '_09_箱底读名_揭开后半截');
  await go(w, h, mob, '?lend=1'); await sleep(500); await shot(p + '_10_借阅卡');
}

try {
  await connect();
  await send('Page.enable');
  const which = process.argv[2];
  if (!which || which === 'pc') await set('pc', 1536, 864, false);
  if (!which || which === 'm') await set('m', 390, 844, true);
} catch (e) { console.error(e); }
finally { try { ws && ws.close(); } catch {} proc.kill(); }
