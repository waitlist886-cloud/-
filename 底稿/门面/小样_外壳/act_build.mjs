// 建档那一页单独验（11-15）：不经过书，直接叫外壳开建档，几种开局各出一份凭证，看头一行对不对；每种截一张图。
//   node act_build.mjs <宽> <高> <截图前缀>
// 本地服务器 front-cors（8773），无头 Chrome 9335。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4] || 'bd'];
const PORT = +(process.env.CDP_PORT || 9335);
const ADDR = 'http://localhost:8773/' + encodeURIComponent('小样_外壳') + '/local.html?t=' + Date.now();
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result && r.result.result ? r.result.result.value : undefined; };
const shot = async (name, full) => {
  let clip;
  if (full) { const h = await ev(`const b = document.querySelector('#sh-build'); return b.scrollHeight`); await send('Emulation.setDeviceMetricsOverride', { width: W, height: Math.min(h, 6000), deviceScaleFactor: 1, mobile: W < 760 }); await sleep(300); }
  const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 82 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64'));
  if (full) { await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 }); await sleep(200); }
};
const until = async (expr, ms = 15000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (await ev(`return !!(${expr})`)) return true; await sleep(200); } return false; };
let bad = 0;
const want = (ok, what) => { if (!ok) bad++; console.log((ok ? '   ✓ ' : '   ✗ ') + what); };

await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR });
await Promise.race([loaded, sleep(15000)]);
await until('window.__tb && window.Shell', 30000);
await ev(`__tb.skip(); return 1`); await sleep(1500);

const CASES = [
  { id: 'moon_line', m: { book: 'moon', era: '月银纪', at: 'm07', title: '焚原断刃', line: '万兽·焚原', year: '1690' }, fill: {}, head: '纪元：月银纪1690年｜开局时段：万兽·焚原' },
  { id: 'strife_line', m: { book: 'strife', era: '纷争纪', at: 's01', title: '执式者', line: '灰的年月·执式者', year: '元年' }, fill: {}, head: '纪元：纷争纪元年｜开局时段：执式者' },
  { id: 'strife_free', m: { book: 'strife', era: '纷争纪', at: 'free', title: '', line: '', year: '' }, fill: { year: '3600', place: '长垒中段的段城' }, head: '纪元：纷争纪3600年｜开局时段：第二十二张｜年份：3600' },
  { id: 'bronze_gold', m: { book: 'bronze', era: '山铜纪', at: 'p1', title: '犁的年月', line: '犁的年月·雨城清查', year: '2' }, fill: { gold: 1 }, head: '纪元：山铜纪2年｜开局时段：雨城清查｜出身：黄金裔' },
  { id: 'bronze_free', m: { book: 'bronze', era: '山铜纪', at: 'free', title: '', line: '', year: '' }, fill: { year: '700' }, head: '纪元：山铜纪700年｜开局时段：无字碑｜年份：700' },
  { id: 'maze_line', m: { book: 'maze', era: '迷宫纪', at: 'q1', title: '探井的年月', line: '探井的年月·寻人', year: '2' }, fill: {}, head: '纪元：迷宫纪2年｜开局时段：寻人' },
  { id: 'maze_switch', m: { book: 'maze', era: '迷宫纪', at: 'q3', title: '繁荣的年月', line: '繁荣的年月·屠林令', year: '433' }, fill: { tofree: 1, year: '500' }, head: '纪元：迷宫纪500年｜开局时段：空白委托｜年份：500' },
];
for (const c of CASES) {
  console.log('== ' + c.id);
  await ev(`await Shell.startBuild(${JSON.stringify(c.m)}); return 1`);
  await until(`Shell.state.build && document.querySelector('#sh-build form')`); await sleep(500);
  if (c.fill.tofree) { await ev(`document.querySelector('#bd-tofree').click(); return 1`); await sleep(700); }
  await ev(`document.querySelector('[data-o="${c.fill.gold ? 'gold' : 'fall'}"]').click(); return 1`); await sleep(200);
  if (c.fill.year) { await ev(`const y = document.querySelector('#bd-year'); y.value = ${JSON.stringify(c.fill.year)}; y.dispatchEvent(new Event('input', { bubbles: true })); return 1`); await sleep(200); }
  if (c.fill.place) await ev(`document.querySelector('#bd-place').value = ${JSON.stringify(c.fill.place)}; return 1`);
  const info = await ev(`const f = document.querySelector('#sh-build form'); const rs = [...f.querySelectorAll('.bd-races button')]; if (!rs.some(b => b.getAttribute('aria-pressed') === 'true')) rs.find(b => !b.disabled).click(); await new Promise(r => setTimeout(r, 150)); const sb = f.querySelector('#bd-race-detail [data-sub]'); if (sb && !f.querySelector('#bd-race-detail [data-sub][aria-pressed="true"]')) sb.click(); await new Promise(r => setTimeout(r, 150));
    return JSON.stringify({ title: f.querySelector('#bd-title').textContent, who: f.querySelector('#bd-who').textContent, cols: f.querySelector('#bd-cols').textContent, at: f.querySelector('#bd-at').textContent.slice(0, 70), races: rs.length, ab: rs.filter(b => b.classList.contains('ab')).length, off: rs.filter(b => b.disabled).length, skills: [...f.querySelectorAll('#bd-skills button')].map(b => b.textContent).slice(0, 4), fromLab: f.querySelector('#bd-from-lab').textContent.slice(0, 30), detail: f.querySelector('#bd-race-detail').textContent.slice(0, 90) })`);
  console.log('  ', info);
  await shot(c.id, true);
  await ev(`const f = document.querySelector('#sh-build form'); f.querySelector('#bd-name').value = '走查的人'; f.querySelector('#bd-age').value = '二十'; f.querySelector('.go').click(); return 1`);
  const ok = await until(`Shell.state.seal`, 12000);
  const cred = ok ? await ev(`return document.querySelector('.sl-paper').textContent`) : (await ev(`return document.querySelector('.bd-err').textContent`));
  const first = String(cred || '').split('\n')[0];
  want(ok && first === c.head, '头一行：' + first + (first === c.head ? '' : '　（要的是 ' + c.head + '）'));
  if (c.id === 'bronze_gold' || c.id === 'strife_free') console.log(String(cred).split('\n').map((l) => '      ' + l).join('\n'));
  await ev(`const b = document.querySelector('.sl-acts [data-a="table"]'); if (b) b.click(); return 1`); await sleep(900);
}
console.log('\n对不上的', bad, '处；报错', errs.length, '条'); for (const x of errs.slice(0, 20)) console.log('  ', x);
ws.close(); process.exit(bad ? 1 : 0);
