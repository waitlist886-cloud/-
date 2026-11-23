// 建档样张的截图：连上无头 Chrome（9377，自己起的那一个），开本地服务（8791，根是本目录）上的 index.html?u=1（头一回抽星保一颗 Unique），照真的钟走一遍。
//   node shots.mjs <前缀> <宽> <高> [mobile]      写 截图/<前缀>_NN_名字.png
import fs from 'node:fs';
const [PRE, W, H, MOB] = [process.argv[2], +process.argv[3], +process.argv[4], process.argv[5] === 'mobile'];
const OUT = new URL('./截图/', import.meta.url);
fs.mkdirSync(OUT, { recursive: true });
const list = await (await fetch('http://127.0.0.1:9377/json/list')).json();
const target = list.find((t) => t.type === 'page' && /about:blank|8791/.test(t.url));
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map();
ws.onmessage = (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function ev(expr) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true });
  if (r.result && r.result.exceptionDetails) { console.log('ERR', JSON.stringify(r.result.exceptionDetails).slice(0, 600)); }
  return r.result && r.result.result ? r.result.result.value : undefined;
}
let n = 0;
async function shot(name) {
  const r = await send('Page.captureScreenshot', { format: 'png' });
  const f = new URL(`${PRE}_${String(++n).padStart(2, '0')}_${name}.png`, OUT);
  fs.writeFileSync(f, Buffer.from(r.result.data, 'base64')); console.log('shot', name);
}
const idle = async (extra = 300) => { for (let i = 0; i < 80; i++) { if (!(await ev('return __bd.busy()'))) break; await sleep(150); } await sleep(extra); };
const frame = async (f) => { for (let i = 0; i < 100; i++) { if ((await ev('return window.__frame')) === f) return; await sleep(40); } };

await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: MOB ? 2 : 1, mobile: MOB });
await send('Page.navigate', { url: 'http://127.0.0.1:8791/index.html?u=1&t=' + Date.now() });
await sleep(2500); await idle(900);
await shot('魂_三张');
await ev('__bd.pickSoul(0)'); await idle(1200);
await shot('魂_翻开一张');
await ev(`document.querySelector('#bNext').click()`); await sleep(500); await idle(900);
await shot('胎骨_一扇');
await ev(`__bd.focusRace('dwarf')`); await idle(900);
await shot('胎骨_翻过来是支系');
await ev(`__bd.pickSub('dwarf', 0)`); await idle(1000);
await shot('胎骨_选好一族_身份牌变了');
await ev(`document.querySelector('#bNext').click()`); await sleep(500); await idle(800);
await ev('__bd.draw()'); await sleep(200);
// Unique 那一张翻开、放光的那一刻
for (let i = 0; i < 120; i++) { if (await ev(`return !!document.querySelector('.card.lit[data-t=Unique]')`)) break; await sleep(50); }
await sleep(260);
await shot('命星_Unique翻开放光');
await idle(600);
await ev('__bd.keepTop()'); await sleep(700);
await shot('命星_一排翻开');
await ev(`__bd.switchPool('A')`); await sleep(300); await ev('__bd.draw()'); await sleep(300); await idle(500);
await ev('__bd.keepTop()'); await sleep(700);
await shot('命星_两颗都留了');
await ev(`document.querySelector('#bNext').click()`); await sleep(500); await idle(1200);
await shot('铸印_挪到正中');
await ev(`window.__frame = ''; document.querySelector('#bNext').click()`);
await frame('press'); await sleep(140); await shot('铸印1_印压下去');
await frame('book'); await sleep(420); await shot('铸印2_收成书脊');
await frame('fly'); await sleep(360); await shot('铸印3_飞上书架');
await frame('shelf'); await sleep(900); await shot('铸印4_落在架上');
ws.close(); process.exit(0);
