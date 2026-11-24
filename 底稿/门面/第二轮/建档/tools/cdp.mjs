// 小工具：连本机无头 Chrome（9371），开一页，量尺寸、跑脚本、截图。
import fs from 'node:fs';
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
export async function open(W, H, { mobile = false, reduce = false, url } = {}) {
  const PORT = +(process.env.CDP_PORT || 9371);
  const t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((r) => { ws.onopen = r; });
  let seq = 0; const pending = new Map(), errs = [], logs = [], waiters = [];
  const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
    if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 600));
    if (m.method === 'Runtime.consoleAPICalled') { const s = m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300); if (m.params.type === 'error') errs.push('报错 ' + s); else logs.push(m.params.type + ' ' + s); }
    if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') errs.push('日志 ' + m.params.entry.text.slice(0, 300) + ' ' + (m.params.entry.url || ''));
    for (const w of waiters) if (w.ev === m.method) w.fn(m);
  };
  await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile });
  if (mobile) await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: reduce ? 'reduce' : 'no-preference' }] });
  const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 600)); return r.result && r.result.result ? r.result.result.value : undefined; };
  const shot = async (file) => { const r = await send('Page.captureScreenshot', { format: file.endsWith('.png') ? 'png' : 'jpeg', quality: 82 }); fs.writeFileSync(file, Buffer.from(r.result.data, 'base64')); };
  const until = async (expr, ms = 15000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (await ev(`return !!(${expr})`)) return true; await sleep(150); } return false; };
  const go = async (u) => { const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r })); await send('Page.navigate', { url: u }); await Promise.race([loaded, sleep(15000)]); };
  const close = async () => { try { await fetch(`http://127.0.0.1:${PORT}/json/close/${t.id}`); } catch (e) {} ws.close(); };
  const click = async (x, y) => { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 }); await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 }); };
  const drag = async (x0, y0, x1, y1, n = 8) => { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: x0, y: y0 }); await send('Input.dispatchMouseEvent', { type: 'mousePressed', x: x0, y: y0, button: 'left', clickCount: 1 }); for (let i = 1; i <= n; i++) { await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: x0 + (x1 - x0) * i / n, y: y0 + (y1 - y0) * i / n, button: 'left', buttons: 1 }); await sleep(30); } await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x: x1, y: y1, button: 'left', clickCount: 1 }); };
  if (url) await go(url);
  return { send, ev, shot, until, go, close, errs, logs, click, drag };
}
export const BASE = 'http://localhost:8774/' + encodeURIComponent('小样_外壳') + '/local.html';
