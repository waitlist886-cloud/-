// 验薄壳的退路换成简式建档以后（11-17）：图床的几个镜像都连不上，薄壳出一句话和两个钮，点“用简式建档”整页换成那一页，
// 几种开局各出一份凭证，看头一行和几样要紧的行，再点“填进输入框”看假日里壳的输入框收没收到。
//   node act_lite.mjs <宽> <高> <截图前缀> [薄壳的地址=../小样_外壳/thin_dead_lite.html] [凭证写到哪个文件]
// thin_dead_lite.html 是 make_thin.thin_html(lite=True, mirrors=[连不上的地址]) 出的。假的日里壳、端口同 act_fallback.mjs。
import fs from 'node:fs';
const [W, H, OUT, SRC, DUMP] = [+process.argv[2], +process.argv[3], process.argv[4], process.argv[5] || '../小样_外壳/thin_dead_lite.html', process.argv[6]];
const PORT = +(process.env.CDP_PORT || 9335);
const URL0 = 'http://localhost:8773/' + encodeURIComponent('探针') + '/host.html?src=' + encodeURIComponent(SRC) + '&t=' + Date.now();
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0;
const pending = new Map(), errs = [], ctxs = [], waiters = [];
const send = (method, params = {}, sessionId) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params })); });
const OKERR = /Permissions policy|allow-popups|allow-same-origin|favicon|sandboxed and lacks|Unrecognized feature|Blocked script execution|ERR_CONNECTION_REFUSED|ERR_UNSAFE_PORT|Failed to load resource|Failed to fetch/;
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') { const sid = m.params.sessionId; send('Runtime.enable', {}, sid); send('Log.enable', {}, sid); send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sid); }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.sid === (m.sessionId || '') && x.c.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
  const push = (t) => { if (!OKERR.test(t)) errs.push(t); };
  if (m.method === 'Runtime.exceptionThrown') push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 360));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') push('error ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 260));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') push('LOG ' + m.params.entry.text.slice(0, 200));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function evIn(expr, x) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 30000, ...(x && x.c ? { contextId: x.c.id } : {}) }, (x && x.sid) || undefined);
  if (r.error) return undefined;
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
async function where(pred, ms = 30000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    for (const x of [...ctxs]) { if (x.c.auxData && x.c.auxData.isDefault === false) continue; const v = await evIn(`try { return !!(${pred}); } catch (e) { return false; }`, x); if (v === true) return x; }
    await sleep(300);
  }
  return null;
}
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 84 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
let bad = 0;
const want = (ok, what) => { if (!ok) bad++; console.log((ok ? '   ✓ ' : '   ✗ ') + what); };

await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: URL0 });
await Promise.race([loaded, sleep(15000)]);

const T = await where(`document.getElementById('boot') && typeof window.__OLD1001 === 'string'`, 20000);
want(!!T, '薄壳开了，简式建档存在里头');
if (!T) { console.log(errs.slice(0, 10)); process.exit(1); }
console.log('   存着的那一页', await evIn(`return window.__OLD1001.length`, T), '字');
const F = await where(`document.getElementById('again') && document.getElementById('useold')`, 60000);
want(!!F, '镜像都连不上以后，出了“再试一次”和“用简式建档”两个钮');
if (!F) process.exit(1);
console.log('   那句话：', await evIn(`return document.querySelector('#boot p.s').textContent + '｜' + document.getElementById('useold').textContent`, F));
await shot('1_连不上');
await evIn(`document.getElementById('useold').click(); return 1`, F);
const L = await where(`document.getElementById('era') && document.getElementById('fill') && !document.getElementById('boot')`, 30000);
want(!!L, '点了以后整页换成了简式建档');
if (!L) process.exit(1);
await sleep(600);
await shot('2_简式建档');

// 选时代：1001 写 1001，别的写纪名；从哪里进：写主线名（照 option 的字找），free 写 free
const CASES = [
  { id: '1001_降临', era: '1001', soul: 'isekai', name: '走查的人', want: ['命途已确认', '现在所在：迷宫纪1001年，未定', '降临之魂'] },
  { id: '1001_本地', era: '1001', soul: 'native', name: '走查的人', place: '阿卡迪亚的井口', want: ['命途已确认', '本地之魂（生于此世）', '【六·你的前半生】', '现在所在：迷宫纪1001年，阿卡迪亚的井口'] },
  { id: '月银纪_焚原', era: '月银纪', line: '万兽·焚原', name: '走查的人', head: '纪元：月银纪1690年｜开局时段：万兽·焚原' },
  { id: '纷争纪_执式者', era: '纷争纪', line: '灰的年月·执式者', name: '走查的人', head: '纪元：纷争纪元年｜开局时段：执式者' },
  { id: '纷争纪_自报', era: '纷争纪', line: 'free', year: '3600', name: '走查的人', head: '纪元：纷争纪3600年｜开局时段：第二十二张｜年份：3600' },
  { id: '山铜纪_篡位', era: '山铜纪', line: '黎明的年月·黎明篡位', name: '走查的人', head: '纪元：山铜纪668年｜开局时段：黎明篡位' },
  { id: '山铜纪_自报', era: '山铜纪', line: 'free', year: '700', name: '走查的人', head: '纪元：山铜纪700年｜开局时段：无字碑｜年份：700' },
  { id: '前传_寻人', era: '迷宫纪', line: '探井的年月·寻人', name: '走查的人', head: '纪元：迷宫纪2年｜开局时段：寻人' },
  { id: '前传_自报', era: '迷宫纪', line: 'free', year: '500', name: '走查的人', head: '纪元：迷宫纪500年｜开局时段：空白委托｜年份：500' },
  { id: '没写名字', era: '山铜纪', line: '黎明的年月·黎明篡位', name: '', err: '名字还没写' },
  { id: '年份出界', era: '迷宫纪', line: 'free', year: '1200', name: '走查的人', err: '1000 年之间' },
];
const dump = {};
for (const c of CASES) {
  const r = await evIn(`
    const $ = (id) => document.getElementById(id), era = $('era'), line = $('line');
    const ev = (el) => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); };
    era.value = ${JSON.stringify(c.era)} === '1001' ? '1001' : [...era.options].find(o => o.textContent === ${JSON.stringify(c.era)}).value; era.onchange();
    if (${JSON.stringify(c.era)} !== '1001') {
      const want = ${JSON.stringify(c.line || '')};
      const opt = want === 'free' ? [...line.options].find(o => o.value === 'free') : [...line.options].find(o => o.textContent.split('　')[0] === want);
      if (!opt) return JSON.stringify({ miss: want });
      line.value = opt.value; line.onchange();
    }
    if (${JSON.stringify(c.soul || '')}) { $('soul').value = ${JSON.stringify(c.soul || '')}; ev($('soul')); }
    $('year').value = ${JSON.stringify(c.year || '')}; ev($('year'));
    $('place').value = ${JSON.stringify(c.place || '')}; ev($('place'));
    $('name').value = ${JSON.stringify(c.name)}; ev($('name'));
    $('fill').click();
    await new Promise(r => setTimeout(r, 200));
    return JSON.stringify({ out: $('out').textContent, tip: $('tip').textContent, yearShown: !$('r-year').hidden, lineShown: !$('r-line').hidden });
  `, L);
  let o = {};
  try { o = JSON.parse(r); } catch (e) { o = { raw: r }; }
  console.log('== ' + c.id);
  if (o.miss !== undefined) { want(false, '找不到这一条：' + o.miss); continue; }
  if (c.err) { want(!o.out && String(o.tip).includes(c.err), '报了：' + o.tip); continue; }
  const first = String(o.out || '').split('\n')[0];
  if (c.head) want(first === c.head, '头一行：' + first + (first === c.head ? '' : '　（要的是 ' + c.head + '）'));
  for (const w of c.want || []) want(String(o.out).includes(w), '有这一行：' + w);
  const got = await evIn(`return document.getElementById('in').value`);
  want(got === o.out, '填进了假输入框（' + String(got || '').length + ' 字）');
  dump[c.id] = o.out;
  if (c.id === '山铜纪_篡位') { await shot('3_' + c.id); console.log(String(o.out).split('\n').map((l) => '      ' + l).join('\n')); }
}
if (DUMP) fs.writeFileSync(DUMP, JSON.stringify(dump, null, 1));
console.log('\n对不上的', bad, '处；报错', errs.length, '条'); for (const x of [...new Set(errs)].slice(0, 20)) console.log('  ', x);
ws.close(); process.exit(bad ? 1 : 0);
