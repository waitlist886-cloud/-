// 样张「此刻」截图（11-23）：起一个本机无头 Chrome，用 CDP 直接定视口（窗口尺寸在新版无头里不准，手机宽也开不到 390）。
//   node 底稿/门面/第二轮/样张_此刻/shots.mjs        写 截图/pc_*.png（1536×864）、m_*.png（390×844，两倍像素）
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '截图'); mkdirSync(OUT, { recursive: true });
const PAGE = pathToFileURL(join(HERE, 'index.html')).href;
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const PORT = 9363, UDD = join(tmpdir(), 'aldran_shot_' + PORT);
const SHOTS = [['01_牌桌五张牌', 'deal'], ['02_指着此刻那张', 'hover'], ['03_翻进书的过场', 'open'], ['04_此刻首屏', 'book'], ['05_路的开头', 'road'], ['06_路的往后', 'road2']];
const SIZES = [['pc', 1536, 864, 1, false], ['m', 390, 844, 2, true]];
const sleep = ms => new Promise(r => setTimeout(r, ms));

const proc = spawn(CHROME, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--remote-debugging-port=' + PORT, '--user-data-dir=' + UDD, 'about:blank'], { stdio: 'ignore' });
let ver;
for (let i = 0; i < 50 && !ver; i++) { await sleep(200); try { ver = await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json(); } catch (e) {} }
const tgt = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(tgt.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r));
let id = 0; const wait = new Map(), evs = [];
ws.addEventListener('message', m => { const d = JSON.parse(m.data); if (d.id && wait.has(d.id)) { wait.get(d.id)(d); wait.delete(d.id); } else if (d.method) evs.push(d.method); });
const cmd = (method, params = {}) => new Promise(r => { const n = ++id; wait.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });

await cmd('Page.enable');
for (const [tag, w, h, dpr, mobile] of SIZES) {
  await cmd('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: dpr, mobile });
  await cmd('Emulation.setTouchEmulationEnabled', { enabled: mobile });
  for (const [name, s] of SHOTS) {
    evs.length = 0;
    await cmd('Page.navigate', { url: PAGE + '?s=' + s });
    for (let i = 0; i < 60 && !evs.includes('Page.loadEventFired'); i++) await sleep(100);
    await cmd('Runtime.evaluate', { expression: 'document.fonts.ready.then(()=>1)', awaitPromise: true });
    await sleep(900);
    const r = await cmd('Page.captureScreenshot', { format: 'png' });
    writeFileSync(join(OUT, `${tag}_${name}.png`), Buffer.from(r.result.data, 'base64'));
    console.log(tag, name);
  }
}
ws.close(); proc.kill();
await sleep(500); try { rmSync(UDD, { recursive: true, force: true }); } catch (e) {}
