// 交互音效走一遍录像（11-26 夜）：无头 Chrome 录屏（Page.startScreencast，每帧记时刻），从门口开始：开门、牌桌发牌翻牌、选月银纪、进书翻页、开档案换衣着拨剧透合上、
// 书里的大图书馆推门进厅抽书、回书从这里进建档掷骰抽命星铸印。外壳把每一声放的时刻记在 window.__sfxLog（墙上时刻，毫秒），
// 走完存 <输出目录>/sfxlog.json；mix_sfx.py 照时刻把同一份音效混成音轨、跟画面合成一个 mp4（无头 Chrome 没有声卡，录不到真的声音）。
//   node 底稿/门面/载入页/音乐/walk_sfx.mjs <输出目录>      （本地 front-cors 8773 起着，CDP_PORT 默认 9351）
import fs from 'node:fs';
import path from 'node:path';
const DIR = process.argv[2];
const W = 390, H = 844, PORT = +(process.env.CDP_PORT || 9351);
fs.mkdirSync(DIR, { recursive: true });
for (const f of fs.readdirSync(DIR)) if (/^f\d+\.jpg$/.test(f)) fs.unlinkSync(path.join(DIR, f));
const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(tab.webSocketDebuggerUrl); await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pend = new Map(), ctxs = [], frames = [];
const send = (m, p = {}, sid) => new Promise((r) => { const id = ++seq; pend.set(id, r); ws.send(JSON.stringify(sid ? { id, method: m, params: p, sessionId: sid } : { id, method: m, params: p })); });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); return; }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.c.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
  if (m.method === 'Page.screencastFrame') {
    const f = 'f' + String(frames.length).padStart(5, '0') + '.jpg';
    fs.writeFileSync(path.join(DIR, f), Buffer.from(m.params.data, 'base64'));
    frames.push([f, m.params.metadata.timestamp]);
    ws.send(JSON.stringify({ id: ++seq, method: 'Page.screencastFrameAck', params: { sessionId: m.params.sessionId } }));
  }
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const evIn = async (expr, x) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, ...(x ? { contextId: x.c.id } : {}) }); return r.result && r.result.result ? r.result.result.value : undefined; };
async function where(pred, ms = 30000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) { for (const x of [...ctxs]) { if ((await evIn(`(() => { try { return !!(${pred}); } catch (e) { return false; } })()`, x)) === true) return x; } await sleep(250); }
  return null;
}
const log = (...a) => console.log(((Date.now() - T0) / 1000).toFixed(1).padStart(5) + 's', ...a);
/* 点一处：在哪一格里找元素，量它在屏上的位置（书那一格的偏移另加），发真的鼠标事件 */
async function clickIn(x, sel, off = [0, 0], nth = 0) {
  const pick = `[...document.querySelectorAll(${JSON.stringify(sel)})].filter((e) => { const b = e.getBoundingClientRect(); return b.width && b.height; })[${nth}]`;
  const ok = await evIn(`(() => { const e = ${pick}; if (!e) return false; const b = e.getBoundingClientRect(); if (b.top < 60 || b.bottom > innerHeight - 40) e.scrollIntoView({ block: 'center' }); return true; })()`, x);
  if (!ok) { log('点不到', sel); return false; }
  await sleep(700);
  const r = await evIn(`(() => { const e = ${pick}; const b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + Math.min(b.height / 2, 30)]; })()`, x);
  await clickAt(r[0] + off[0], r[1] + off[1]);
  return true;
}
async function clickAt(x, y) { for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 }); }
await send('Page.enable'); await send('Runtime.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
try { const wi = await send('Browser.getWindowForTarget', { targetId: tab.id }); await send('Browser.setWindowBounds', { windowId: wi.result.windowId, bounds: { width: 860, height: H + 260 } }); } catch (e) {}
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: true });
const T0 = Date.now();
await send('Page.navigate', { url: 'http://127.0.0.1:8773/' + encodeURIComponent('小样_外壳') + '/thin_local.html?gmin=4&t=' + Date.now() });
const S = await where('window.__gate && window.__sfx', 30000);
for (let i = 0; i < 160; i++) { if ((await evIn('__gate.state().phase', S)) >= 4) break; await sleep(250); }
await sleep(800);
await send('Page.startScreencast', { format: 'jpeg', quality: 80, maxWidth: 4000, maxHeight: 4000, everyNthFrame: 1 });
await sleep(1000);
log('点门'); await clickIn(S, '#gate .g-door');
for (let i = 0; i < 80; i++) { if ((await evIn('window.__tb && __tb.stage', S)) === 'choose') break; await sleep(250); }
log('牌桌摆好了'); await sleep(900);
/* 选月银纪：点一下撑开，再点一下选定 */
const band = async () => evIn('(() => { const b = __tb.bands[0].el.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; })()', S);
let p = await band(); await clickAt(p[0], p[1]); await sleep(900);
p = await band(); log('选定月银纪'); await clickAt(p[0], p[1]);
for (let i = 0; i < 60; i++) { if ((await evIn('!document.querySelector("#acts").hidden', S)) === true) break; await sleep(250); }
await sleep(600); log('翻开这一本'); await clickIn(S, '#openBook');
const B = await where('location.href === "about:srcdoc" && document.title.indexOf("月银纪") >= 0 && document.querySelector("#view")', 30000);
await sleep(3500);
/* 翻页：书里的墙，点一块砖 */
const fr = await evIn('(() => { const f = document.getElementById("sh-frame").getBoundingClientRect(); return [f.left, f.top]; })()', S);
log('沿墙走'); for (let k = 0; k < 3; k++) { await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: 195, y: 500, deltaX: 0, deltaY: 400 }); await sleep(350); }
await sleep(1400);
log('翻页（点墙上一幅）'); await clickAt(300, 360); await sleep(2200);
log('剧透开关'); await clickIn(B, '.spl', fr); await sleep(1500);
log('开档案'); await clickIn(B, '[data-p]', fr); await sleep(1600);
log('换衣着'); await clickIn(B, '[data-o="1"]', fr); await sleep(1300);
log('合上档案'); await clickIn(B, '.on .x, .x', fr); await sleep(1400);
log('回到墙前'); await clickIn(B, '#pg-close', fr); await sleep(1400);
log('大图书馆'); await clickIn(B, '#wbBtn', fr); await sleep(2400);
log('推门进一厅'); await clickIn(B, '.lb-arch:not(.lx-hot):not(.lx-blank):not(.lx-map)', fr); await sleep(2400);
log('抽一本书'); await clickIn(B, '.lb-sp', fr); await sleep(2800);
await evIn('window.Library && Library.close(true); 1', B); await sleep(900);
log('再翻开一页'); await clickAt(300, 360); await sleep(2200);
log('从这里进'); await evIn('(() => { const d = document.querySelector("details"); if (d) d.open = true; return 1; })()', B);
/* 建档那一段要有命星那一步（月银纪那时候还没有面板，建档里没有命星），所以从书里报一回迷宫纪 990 年进建档（跟书里“从这里进”发的是同一种消息） */
await evIn(`SHELL.post({ t: 'enter', book: 'maze', era: '迷宫纪', at: 'q6', title: '垂暮的年月', line: '走查', year: '990', ti: '' }); 1`, B); await sleep(3800);
log('建档：掷骰子'); await evIn('__bd.go(6); 1', S); await sleep(1800); await clickIn(S, '[data-a="stat"][data-v="roll"]'); await sleep(2000);
/* 第七步起每一步把要挑的各挑头一个（不是放音效的地方，快快走过去），走到命星那一步抽一回、留一颗，再往后走到铸印 */
const FILL = `(() => { const nav = new Set(['menu','step','route','out','say','hdp','unfocus','next','prev','idclose','idopen','stat','draw','sreset','skeep','shold','sdrop','mint']);
  const g = {}; for (const e of document.querySelectorAll('#sh-build [data-a]')) { const a = e.dataset.a; if (nav.has(a) || e.disabled) continue; if (!g[a]) g[a] = e; }
  for (const a in g) g[a].click(); return Object.keys(g).join(','); })()`;
let starDone = false;
for (let n = 7; n <= 11; n++) {
  for (let k = 0; k < 8; k++) { await evIn(`__bd.go(${n}); 1`, S); await sleep(700); if ((await evIn('__bd.step', S)) === n) break; }      // 牌还在走的时候 go 不理，等它停了再来
  const info = await evIn(`__bd.step + ' 星' + document.querySelectorAll('.bx-star').length + ' 抽' + document.querySelectorAll('[data-a="draw"]').length`, S);
  log('建档第', n, '步', info);
  if (!starDone && (await evIn(`!!document.querySelector('[data-a="draw"]')`, S))) { log('建档：命星'); await clickIn(S, '[data-a="draw"]'); await sleep(2600); starDone = true; }
  if (n < 11) { log('  挑了', await evIn(FILL, S)); await sleep(500); }
}
log('建档：铸印'); log('  第', await evIn('__bd.step', S), '步');
for (let k = 0; k < 6; k++) { await evIn('__bd.mint && __bd.mint(); 1', S); await sleep(1500); if (await evIn('__sfxLog.some((x) => x.n === "seal")', S)) break; log('  还没压下去，再来'); }
await sleep(2500);
await send('Page.stopScreencast'); await sleep(300);
const sfx = JSON.parse(await evIn('JSON.stringify(window.__sfxLog)', S));
log('音效', sfx.map((x) => x.n).join(' '));
fs.writeFileSync(path.join(DIR, 'sfxlog.json'), JSON.stringify({ frames: frames.map((f) => f[1]), sfx }, null, 1));
const lines = [];
for (let i = 0; i < frames.length; i++) { const d = i + 1 < frames.length ? Math.max(0.001, frames[i + 1][1] - frames[i][1]) : 0.5; lines.push(`file '${frames[i][0]}'`, `duration ${d.toFixed(4)}`); }
lines.push(`file '${frames[frames.length - 1][0]}'`);
fs.writeFileSync(path.join(DIR, 'list.txt'), lines.join('\n') + '\n');
console.log('帧', frames.length, '时长', (frames[frames.length - 1][1] - frames[0][1]).toFixed(1), 's');
await send('Page.close').catch(() => {}); process.exit(0);
