// 背景音乐本地验（11-26 夜）。无头 Chrome（CDP_PORT，默认 9351），本地 front-cors 8773 起着、thin_local.html 是 make_thin.py --local http://127.0.0.1:8773/ 出的。
//   node 底稿/门面/载入页/音乐/test_bgm.mjs <方式> [sandbox]
//     方式：gate（走到门口、点门起声，再翻书换曲、合书换回、静音钮）、skip（走路的时候点跳过起声）、nogate（地址带 ?nogate，点页面起声）
//     带 sandbox：照日里的办法装进假日里的沙箱（探针/host.html，srcdoc + sandbox="allow-scripts allow-modals allow-forms"）
// 每一步打印 __bgm.state() 的要紧几样：起没起声、怎么起的、play() 成没成、停着还是在放、放到第几秒、场景、音量。
const MODE = process.argv[2] || 'gate', SBX = process.argv[3] === 'sandbox';
const PORT = +(process.env.CDP_PORT || 9351);
const base = 'http://127.0.0.1:8773/';
const qs = MODE === 'nogate' ? '?nogate' : MODE === 'gate' ? '?bgmtest=swap' : '';
const THIN = process.env.THIN || 'thin_local.html';      // THIN=thin.html 验图床上的那一版
const URL0 = SBX ? base + encodeURIComponent('探针') + '/host.html?src=' + encodeURIComponent('../小样_外壳/' + THIN) + '&t=' + Date.now() : base + encodeURIComponent('小样_外壳') + '/' + THIN + qs;
const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(tab.webSocketDebuggerUrl); await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pend = new Map(), ctxs = [];
const send = (m, p = {}, sid) => new Promise((r) => { const id = ++seq; pend.set(id, r); ws.send(JSON.stringify(sid ? { id, method: m, params: p, sessionId: sid } : { id, method: m, params: p })); });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') { const sid = m.params.sessionId; send('Runtime.enable', {}, sid); send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sid); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const evIn = async (expr, x) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, ...(x && x.c ? { contextId: x.c.id } : {}) }, (x && x.sid) || undefined); return r.result && r.result.result ? r.result.result.value : undefined; };
async function where(pred, ms = 40000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) { for (const x of [...ctxs]) { if (x.c.auxData && x.c.auxData.isDefault === false) continue; if ((await evIn(`try { !!(${pred}) } catch (e) { false }`, x)) === true) return x; } await sleep(300); }
  return null;
}
await send('Page.enable'); await send('Runtime.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
await send('Page.navigate', { url: URL0 });
const X = await where('window.__bgm');
if (!X) { console.log('没找到外壳'); process.exit(1); }
const OFF = SBX ? 64 : 0;          // 假日里的顶栏
const st = async (tag) => { const s = await evIn('JSON.stringify(window.__bgm.state())', X); const o = JSON.parse(s); console.log(tag.padEnd(14), `起声=${o.unlocked ? o.by : '没'} play()=${o.playOk ? '成' : o.playErr || '-'} ${o.paused ? '停着' : '在放'} ${(+o.t).toFixed(1)}秒 场景=${o.scene} 音量=${(+o.vol).toFixed(2)} 另一个=${o.other.paused ? '停' : '放'}/${(+o.other.vol).toFixed(2)} 静音=${o.muted} __bgmErr=${await evIn('String(window.__bgmErr || "")', X)}`); return o; };
const click = async (sel) => {
  const r = await evIn(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return null; const b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; })()`, X);
  if (!r) { console.log('点不到', sel); return; }
  for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x: r[0], y: r[1] + OFF, button: 'left', clickCount: 1 });
};
await sleep(1500);
await st('一开始');
if (MODE === 'gate') {
  for (let i = 0; i < 120; i++) { if ((await evIn('window.__gate && __gate.state().phase', X)) >= 4) break; await sleep(300); }
  await st('走到门口');
  await click('#gate .g-door'); await sleep(2600);
  await st('点门以后');
  await sleep(1500); await st('又过一秒半');
  if (!SBX) {
    await evIn('Shell.openBook("moon"); 1', X); await sleep(1300); await st('翻开月银纪 1s');
    await sleep(2200); await st('翻开月银纪 3.5s');
    await evIn('Shell.toTable(); 1', X); await sleep(1300); await st('合上 1s');
    await sleep(2200); await st('合上 3.5s');
  }
  await click('#bgmBtn'); await sleep(400); await st('点喇叭（静音）');
  await click('#bgmBtn'); await sleep(400); await st('再点（放出来）');
} else if (MODE === 'skip') {
  await sleep(2500); await st('走路中');
  await click('#gate .g-skip'); await sleep(2800); await st('点跳过以后');
} else {
  await sleep(1000); await st('没点之前');
  for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x: 120, y: 500 + OFF, button: 'left', clickCount: 1 });
  await sleep(2200); await st('点了页面以后');
}
await send('Page.close').catch(() => {}); process.exit(0);
