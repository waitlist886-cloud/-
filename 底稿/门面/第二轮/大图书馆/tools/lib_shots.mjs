// 大图书馆走查截图（11-24）：无头 Chrome + CDP，看外壳和四本书里的图书馆。先起 共用/utf8_server.py（8774）。node lib_shots.mjs <pc|m>，截图写 ../截图/（OUT 环境变量可改）
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
const OUT = process.env.OUT || 'E:/aldran_art/底稿/门面/第二轮/大图书馆/截图';
mkdirSync(OUT, { recursive: true });
const CH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9471 + (process.argv[2] === 'm' ? 1 : 0);
const BASE = 'http://127.0.0.1:8774/';
const SHELL = BASE + encodeURI('小样_外壳/local.html');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const proc = spawn(CH, ['--headless=new', '--hide-scrollbars', '--no-first-run', '--enable-unsafe-swiftshader', `--remote-debugging-port=${PORT}`, `--user-data-dir=${path.join(os.tmpdir(), 'lib_cdp_' + PORT)}`, '--window-size=1920,945', 'about:blank'], { stdio: 'ignore' });
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
async function go(url, w, h, mob) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: mob, screenWidth: w, screenHeight: h });
  await send('Emulation.setTouchEmulationEnabled', { enabled: mob });
  events.length = 0;
  await send('Page.navigate', { url });
  for (let i = 0; i < 150 && !events.some((e) => e.method === 'Page.loadEventFired'); i++) await sleep(100);
  await sleep(2500);
  await js('document.fonts.ready.then(()=>1)');
}
async function pt(sel, frame) {
  const W = frame ? 'document.getElementById("sh-frame").contentDocument' : 'document';
  return js(`(()=>{const e=${W}.querySelector(${JSON.stringify(sel)});if(!e)return null;e.scrollIntoView({block:'nearest'});const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()`);
}
async function hover(sel, frame) { const p = await pt(sel, frame); if (!p) throw new Error('没有 ' + sel); await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: p[0], y: p[1] }); }
async function click(sel, frame) { const p = await pt(sel, frame); if (!p) throw new Error('没有 ' + sel); const [x, y] = p; await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 }); await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 }); }
async function shot(name) { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); writeFileSync(path.join(OUT, name + '.jpg'), Buffer.from(r.data, 'base64')); console.log('截图', name); }
const L = 'window.Library';
const F = 'document.getElementById("sh-frame").contentWindow';

async function pc(p, w, h, mob) {
  const S = (n) => p + '_' + n;
  await go(SHELL, w, h, mob);
  await js(`${L}.open()`); await sleep(1400); await shot(S('01_圆厅'));
  if (!mob) { await hover('#lib .lb-arch[data-k="strife"]'); await sleep(500); await shot(S('02_指着拱门')); }
  await click('#lib .lb-arch[data-k="strife"]'); await sleep(1300); await shot(S('03_纷争纪廊'));
  if (!mob) { await hover('#lib .lb-wing .lb-sp[data-b="strife-qyzy"]'); await sleep(500); await shot(S('04_指着一本')); }
  await click('#lib .lb-wing .lb-sp[data-b="strife-qyzy"]'); await sleep(700); await shot(S('05a_抽出来'));
  await sleep(900); await shot(S('05b_转到封面'));
  for (let i = 0; i < 40 && await js(`${L}.state.busy`); i++) await sleep(150);
  await sleep(300); await shot(S('06_扉页'));
  await js(`${L}._goto('toc')`); await sleep(400); await shot(S('07_目录'));
  await js(`${L}._goto(1)`); await sleep(600); await shot(S('08_剧透关着'));
  await js(`document.querySelector('#lib .rd-top .lb-spl').click()`); await sleep(700); await shot(S('09_剧透开着'));
  await js(`document.querySelector('#lib .rd-top .lb-spl').click()`); await sleep(300);
  // 带青墨注、图版的：万物的清点、七剑四兽图
  await js(`document.querySelector('#lib .rd-top .lx-sh').click()`); await sleep(2300);
  await js(`${L}.openBook('yuan-wwdqd')`); for (let i = 0; i < 40 && !(await js(`${L}.state.book`)); i++) await sleep(150); await sleep(2200);
  await js(`${L}._goto(2)`); await sleep(500); await shot(S('10_青墨注'));
  if (mob) { await js(`(()=>{const s=document.querySelector('#lib .rd-flow sup.lx-fn');s.scrollIntoView({block:'center'});s.click()})()`); await sleep(500); await shot(S('10b_点注号')); }
  await js(`${L}._goto('notes')`); await sleep(500); await shot(S('11_注脚'));
  await js(`document.querySelector('#lib .rd-top .lx-sh').click()`); await sleep(2300);
  await js(`${L}.openBook('ming-qjsst')`); for (let i = 0; i < 40 && !(await js(`${L}.state.book`)); i++) await sleep(150); await sleep(2200);
  await js(`${L}._goto(1)`); await sleep(500); await shot(S('12_图版框'));
  await js(`${L}._mode('${mob ? 'page' : 'scroll'}')`); await sleep(500); await shot(S('13_' + (mob ? '一页一页翻' : '卷着读')));
  await js(`document.querySelector('#lib .rd-top .lx-sh').click()`); await sleep(2300);
  // 往前、往后的廊，地图室，借阅卡
  await js(`${L}.open('past')`); await sleep(1300);
  if (!mob) { await hover('#lib .lb-wing .lb-sp.lx-hot[data-e="2"][data-i="1"]'); await sleep(400); }
  await click('#lib .lb-wing .lb-sp.lx-hot[data-e="2"][data-i="1"]'); await sleep(250); await shot(S('14_往前的廊_抽不出'));
  await js(`${L}.open('future')`); await sleep(1300);
  if (!mob) { await hover('#lib .lb-wing .lb-sp[data-s="20"]'); await sleep(400); }
  await shot(S('15_往后的廊'));
  await js(`${L}.open('map')`); await sleep(1300); await shot(S('16_地图室'));
  await click('#lib .lb-mc[data-v="bronze"]'); await sleep(1500); await shot(S('17_地图室翻到地图'));
  console.log('世界之书', JSON.stringify(await js('Codex.state')));
  await js('Codex.close()'); await sleep(600);
  await js(`${L}.open()`); await sleep(1200); await click('#lib .lb-card'); await sleep(700); await shot(S('18_借阅卡'));
  await js(`document.querySelector('#lib .lb-lend .lx-x').click()`); await js(`${L}.close(true)`); await sleep(400);
  // 从纷争纪那一本里开图书馆
  await js('Shell.openBook("strife")'); await sleep(9000);
  await js(`${F}.document.getElementById('intro') && ${F}.document.getElementById('intro').classList.add('off')`);
  await sleep(1200); await shot(S('19_纷争纪书'));
  await js(`${F}.document.getElementById('wbBtn').click()`); await sleep(1600);
  console.log('书里的图书馆', JSON.stringify(await js(`${F}.Library.state`)));
  await shot(S('20_纷争纪书里开图书馆'));
  for (const b of ['moon', 'bronze', 'maze']) {
    await js(`${F}.Library.close(true)`); await js(`Shell.openBook("${b}")`); await sleep(9000);
    await js(`${F}.document.getElementById('wbBtn').click()`); await sleep(1500);
    console.log(b + ' 书里开图书馆', JSON.stringify(await js(`${F}.Library.state`)));
    await js(`${F}.document.querySelector('#lib .lb-wing .lb-sp[data-b]').click()`); await sleep(4500);
    console.log(b + ' 抽一本', JSON.stringify(await js(`(()=>{const st=${F}.Library.state;return {book:st.book,page:st.page,busy:st.busy}})()`)));
    if (b === 'moon') await shot(S('21_月银纪书里翻一本'));
  }
}

try {
  await connect(); await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
  const which = process.argv[2] || 'pc';
  if (which === 'pc') await pc('pc', 1920, 945, false); else await pc('m', 390, 844, true);
} catch (e) { console.error('停了：', e.message); }
finally {
  console.log('控制台报错', errs.length); for (const e of errs) console.log('  ', e);
  try { ws && ws.close(); } catch {} proc.kill();
}
