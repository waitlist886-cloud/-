// 大图书馆的走查（11-25）：馆里的钮一枚一枚拿真鼠标、真手指点，点完核页面真的变了。
// 起因：顶栏三枚钮（回圆厅、剧透开关、出馆）叫一条样式弄成了不接指针，脚本里 .click() 点得着，真鼠标、真手指点不着，
// 原来几支走查都是 .click()，没查出来。这一支一律照钮在屏幕上的位置从最外头那一页发真的按下抬起（手指是 touchStart、touchEnd），
// 外头盖着什么、哪一层不接指针，都会点不着。
//
//   node 底稿/门面/共用/act_lib.mjs [宽=1920] [高=945] [情形…] [--shots 截图目录] [--input mouse|touch|both] [--keys]
//     情形（不写就全走）：
//       shell                    外壳里从牌桌右上角进（小样_外壳/local.html）
//       shell:moon|strife|bronze|maze|now      外壳里装着的那一本书里进（落在那一纪的廊）
//       moon|strife|bronze|maze|now            单开那一本书（<书>/local.html?skip=1）
//       sandbox、sandbox:<书>    假的日里（探针/host.html：srcdoc 加 sandbox，只给 allow-scripts allow-modals allow-forms）里的外壳、外壳里装着的书
//                                鼠标用 探针/host.html（顶上 64px 假顶栏、底下假输入框）；手指用这一支自己出的那张壳（格子贴着页面左上角、铺满），缘故见 calibrate() 上头那一段
//                                设 ACT_LIB_BARHOST=1 手指也用 探针/host.html：校点会量出偏多少、照着补（补了以后格子最底下那一截点不到，翻页那几枚会报没点着）
//     --input   回圆厅、出馆那一圈拿什么点：both（默认，鼠标一遍、手指一遍，各自重开一回页面）、mouse、touch。别的钮只拿这一种宽度的本手点（760 以上鼠标，以下手指）。
//     --keys    只走回圆厅、出馆那一圈，别的钮不点（快）。
//     --shots   截图放哪（不写不截）：<目录>/<情形>_<宽>_<手>_<名>.jpg
//     --css     拿这一份样式顶替页面要载的 common/library.css（不动仓库里的文件）。核这一支查不查得出毛病用：
//               git show HEAD~N:底稿/门面/共用/library.css 存成一份，拿它跑，11-25 以前那一份顶栏三枚钮该报点不着。
//   本地服务：这一支自己在进程里起一个（根是 底稿/门面/，端口让系统挑，带跨域头、不留缓存，连接是长连的），走完就没了，不用先起别的。
//     想用现成的（比方 共用/cors_server.py 的 8773）设 FRONT_BASE=http://localhost:8773/（自己那一个照样起着，只出假的日里手指用的那张壳）。那一个一问一断，
//     几支走查并着跑、页面一回载上千个文件，本机的临时端口会用光（11-25 并四路时报过 EADDRNOTAVAIL，书的 JSON 十几秒取不回来，报出一串假的对不上）。
//     并着跑两三路为宜（一路一个无头 Chrome，内存紧的时候别多开）。全走一遍（十七种情形、两种宽）三路并着要一个钟头上下，平常改完图书馆跑
//     `1920 945 shell`、`390 844 shell`、`390 844 sandbox:maze`、`820 1180 shell --input touch`（平板宽，圆厅名牌两排、往前的廊收窄只在这种宽里走得到）加一本单开的书就够。
//   无头 Chrome：这一支每回自己起一个（调试端口让系统挑空的，资料目录放临时目录），走完自己停，不去碰别人开着的。Chrome 不在默认位置设 CHROME。
//     一定要用现成的那一个才设 CDP_PORT（先认准那个端口上是自己的：11-25 两个子任务各起了一个都写 9377，一个占了 127.0.0.1、一个占了 ::1，
//     两边的走查在同一页上互相搅，报出一串对不上，都是假的）。
//   走完末一行“对不上的 N 处”，退出码是 N（封顶 100）。
//
// 一圈里点什么：
//   回圆厅、出馆（--input 的每一种手各走一遍）：从入口进；在某一厅、在地图室、合上一本书（长的、带插图的）以后点回圆厅；
//     在圆厅、在某一厅（四十来本的那一厅，手机上先拖着滚一截）、在地图室、合上带插图的书以后点出馆；出了馆核入口那一枚又点得着。
//   别的钮（本手一遍）：顶栏剧透开关、借阅卡和“放回去”、长桌上那一本、翻开以后的往后翻往前翻、目录和目录里的一行、卷着读和一页一页翻、
//     青火印和书里的剧透开关、注号、纸页两边点一下翻页（手机上横着划）、插图底下原文的折起、合上；往前的廊烫手的书、往后的廊空白的书；
//     地图室点一张翻世界之书的地图、合上世界之书还在地图室；Esc 一层一层退。
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const opt = (name, def) => { const i = argv.indexOf('--' + name); if (i < 0) return def; const v = argv[i + 1]; argv.splice(i, 2); return v; };
const flag = (name) => { const i = argv.indexOf('--' + name); if (i < 0) return false; argv.splice(i, 1); return true; };
const SHOTS = opt('shots', ''), INPUT = opt('input', 'both'), CSS_FILE = opt('css', ''), KEYS_ONLY = flag('keys');
const CSS_BODY = CSS_FILE ? fs.readFileSync(CSS_FILE).toString('base64') : '';
const nums = argv.filter((a) => /^\d+$/.test(a)).map(Number);
const [W, H] = [nums[0] || 1920, nums[1] || 945];
const BOOKS = ['moon', 'strife', 'bronze', 'maze', 'now'];
const DIR = { moon: '小样_月银纪书', strife: '小样_纷争纪书', bronze: '小样_山铜纪书', maze: '小样_迷宫纪书', now: '小样_此刻书' };
const ERA = { moon: '月银纪', strife: '纷争纪', bronze: '山铜纪', maze: '迷宫纪', now: '此刻' };
const LAND = { moon: 'moon', strife: 'strife', bronze: 'bronze', maze: 'maze', now: 'maze' };          // 书里的入口落在哪一廊
const ALL = ['shell', ...BOOKS, ...BOOKS.map((b) => 'shell:' + b), 'sandbox', ...BOOKS.map((b) => 'sandbox:' + b)];
let CASES = argv.filter((a) => !/^\d+$/.test(a));
if (!CASES.length) CASES = ALL;
for (const c of CASES) if (!ALL.includes(c)) { console.log('不认得的情形', c, '　可以写：', ALL.join(' ')); process.exit(2); }
let BASE = process.env.FRONT_BASE ? process.env.FRONT_BASE.replace(/\/?$/, '/') : '';          // 不写就自己起一个，起好了填上
let PORT = +(process.env.CDP_PORT || 0);
const CHROME = process.env.CHROME || (process.platform === 'win32' ? 'C:/Program Files/Google/Chrome/Application/chrome.exe' : process.platform === 'darwin' ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' : 'google-chrome');
const PRIMARY = W < 760 ? 'touch' : 'mouse';
const BARHOST = process.env.ACT_LIB_BARHOST === '1';          // 假的日里：手指也用 探针/host.html（有 64px 假顶栏）。要看校点量出来偏多少、补不补得上的时候设
const HANDS = INPUT === 'both' ? ['mouse', 'touch'] : [INPUT];
const HAND = { mouse: '鼠标', touch: '手指' };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const say = (...a) => console.log(...a);
const q = (s) => encodeURIComponent(s);
if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });

/* ---------- 本地服务、无头 Chrome：没起着就自己起，走完自己停 ---------- */
const kids = [];
let tmpProfile = '';
const alive = async (u) => { try { const r = await fetch(u, { signal: AbortSignal.timeout(2500) }); return r.ok; } catch (e) { return false; } };
/* 进程里的静态服务：根是 底稿/门面/，照 cors_server.py 带跨域头、不留缓存（日里的沙箱里也不留缓存），连接长连 */
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.md': 'text/plain; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.wav': 'audio/wav', '.mp4': 'video/mp4', '.webm': 'video/webm', '.wasm': 'application/wasm' };
/* 假的日里，手指用的那一张：跟 探针/host.html 一样把整页放进 srcdoc、sandbox 只给 allow-scripts allow-modals allow-forms，只是格子贴着页面左上角、铺满（没有顶上那条 64px 的假顶栏）。
   缘故见 calibrate() 上头：格子离页面顶上有一截的时候，无头 Chrome 发的手指合成出来的 click 会偏那一截。鼠标照旧用 探针/host.html（有假顶栏、底下有假输入框） */
const HOST0_HTML = '<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>假的日里（格子贴着左上角）</title>'
  + '<style>html,body{margin:0;height:100%;background:#111;overflow:hidden}#f{display:block;position:fixed;left:0;top:0;width:100%;height:100%;border:0;background:#000}#in{display:none}</style></head><body>'
  + '<iframe id="f" sandbox="allow-scripts allow-modals allow-forms"></iframe><textarea id="in"></textarea>'
  + '<script>var q=new URLSearchParams(location.search);fetch(q.get("src")).then(function(r){return r.text()}).then(function(t){document.getElementById("f").srcdoc=t});'
  + 'addEventListener("message",function(e){var d=e.data;if(d&&d.type==="rili-set-input"){document.getElementById("in").value=d.value;window.__last=d.value}});<\/script></body></html>';
function serve() {
  const ROOT = path.resolve(HERE, '..');
  const HEAD = { 'Access-Control-Allow-Origin': '*', 'Cache-Control': 'no-store' };
  return new Promise((ok) => {
    const srv = http.createServer((req, res) => {
      let f;
      if (/^\/__act_lib\/host0\.html/.test(req.url)) { res.writeHead(200, { ...HEAD, 'Content-Type': 'text/html; charset=utf-8' }).end(HOST0_HTML); return; }
      try { f = path.join(ROOT, decodeURIComponent(new URL(req.url, 'http://x').pathname)); } catch (e) { res.writeHead(400, HEAD).end(); return; }
      if (f !== ROOT && !f.startsWith(ROOT + path.sep)) { res.writeHead(403, HEAD).end(); return; }
      fs.stat(f, (err, st) => {
        if (err || !st.isFile()) { res.writeHead(404, { ...HEAD, 'Content-Type': 'text/plain; charset=utf-8' }).end('File not found'); return; }
        res.writeHead(200, { ...HEAD, 'Content-Type': MIME[path.extname(f).toLowerCase()] || 'application/octet-stream', 'Content-Length': st.size });
        if (req.method === 'HEAD') { res.end(); return; }
        fs.createReadStream(f).on('error', () => res.destroy()).pipe(res);
      });
    });
    srv.keepAliveTimeout = 30000;
    srv.listen(0, '127.0.0.1', () => ok(srv));
  });
}
let server = null, HOST0 = '';
async function ensure() {
  server = await serve();          // 自己这一个总是起着：HOST0 那张壳在它上头
  const own = `http://127.0.0.1:${server.address().port}/`;
  HOST0 = own + '__act_lib/host0.html';
  if (!BASE) BASE = own;
  else if (!(await alive(BASE + q('小样_外壳') + '/local.html'))) { say('FRONT_BASE 那个本地服务连不上：', BASE); process.exit(2); }
  if (PORT) {          // 指明了用现成的那一个
    if (!(await alive(`http://127.0.0.1:${PORT}/json/version`))) { say('CDP_PORT 那个端口上没有无头 Chrome：', PORT); await stop(2); }
    return;
  }
  // 自己起一个：端口写 0 让系统挑，挑到哪个 Chrome 写在资料目录的 DevToolsActivePort 头一行
  tmpProfile = fs.mkdtempSync(path.join(os.tmpdir(), 'act_lib_chrome_'));
  kids.push(spawn(CHROME, ['--headless=new', '--hide-scrollbars', '--no-first-run', '--enable-unsafe-swiftshader', '--remote-debugging-port=0', '--user-data-dir=' + tmpProfile, '--window-size=1920,945', 'about:blank'], { stdio: 'ignore' }));
  const pf = path.join(tmpProfile, 'DevToolsActivePort');
  /* 内存紧、并着几路的时候 Chrome 起得慢（11-25 有一路等了十六秒没等到），等到一分钟 */
  for (let i = 0; i < 150 && !PORT; i++) { await sleep(400); try { PORT = parseInt(fs.readFileSync(pf, 'utf8'), 10) || 0; } catch (e) { /* 还没写出来 */ } }
  for (let i = 0; i < 120 && PORT && !(await alive(`http://127.0.0.1:${PORT}/json/version`)); i++) await sleep(500);          // 机器忙的时候本机连接一时连不上，多等一会儿
  if (!PORT || !(await alive(`http://127.0.0.1:${PORT}/json/version`))) { say('无头 Chrome 没起来（或者本机这会儿连不上它的调试端口）：', CHROME, PORT || ''); await stop(2); }
}
function stop(code) {
  for (const k of kids) { try { k.kill(); } catch (e) { /* 已经没了 */ } }
  if (tmpProfile) setTimeout(() => { try { fs.rmSync(tmpProfile, { recursive: true, force: true }); } catch (e) { /* 还占着就留着 */ } process.exit(code); }, 800);
  else process.exit(code);
  return new Promise(() => {});          // 等着退出，后头的不再往下走
}
await ensure();

/* ---------- 调试协议：沙箱里各格是单独的进程，一层一层挂上去才读得到（照 小样_外壳/act_sandbox.mjs） ---------- */
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let finished = false;
ws.onclose = () => { if (finished) return; console.log('跟无头 Chrome 的线断了'); stop(101); };
let seq = 0, errs = [];
const pending = new Map(), ctxs = [], waiters = [];
const send = (method, params = {}, sessionId) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params })); });
const OKERR = /Permissions policy|allow-popups|allow-same-origin|favicon|sandboxed and lacks|Unrecognized feature|Blocked script execution|front_ptr|ERR_ABORTED|net::ERR_BLOCKED_BY_ORB|fonts\.googleapis\.com|fonts\.gstatic\.com|googleapis\.com\/css/;
let SOLO = false;          // 单开一本书：大图书馆的插图只拷进了外壳（sync.py），书自己的 common/ 里没有，那几条 404 不算
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Target.attachedToTarget') { const sid = m.params.sessionId; send('Runtime.enable', {}, sid); send('Log.enable', {}, sid); if (CSS_BODY) send('Fetch.enable', { patterns: [{ urlPattern: '*common/library.css*' }] }, sid); send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true }, sid); }
  if (m.method === 'Fetch.requestPaused') {          // --css：图书馆的样式换成给的那一份
    send('Fetch.fulfillRequest', { requestId: m.params.requestId, responseCode: 200, responseHeaders: [{ name: 'Content-Type', value: 'text/css; charset=utf-8' }, { name: 'Access-Control-Allow-Origin', value: '*' }, { name: 'Cache-Control', value: 'no-store' }], body: CSS_BODY }, m.sessionId || undefined);
    return;
  }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push({ sid: m.sessionId || '', c: m.params.context });
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.sid === (m.sessionId || '') && x.c.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
  if (m.method === 'Runtime.executionContextsCleared') { for (let i = ctxs.length - 1; i >= 0; i--) if (ctxs[i].sid === (m.sessionId || '')) ctxs.splice(i, 1); }
  const push = (t) => { if (!OKERR.test(t) && !(SOLO && /assets\/lib\/plates\//.test(t))) errs.push(t); };
  if (m.method === 'Runtime.exceptionThrown') push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 360));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') push('报错 ' + JSON.stringify(m.params.args.map((a) => a.value ?? a.description)).slice(0, 260));
  if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') push('LOG ' + m.params.entry.text.slice(0, 200) + ' ' + decodeURIComponent(m.params.entry.url || '').slice(-70));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
async function evIn(expr, x) {
  const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true, timeout: 30000, ...(x && x.c ? { contextId: x.c.id } : {}) }, (x && x.sid) || undefined);
  if (r.error) return undefined;
  if (r.result && r.result.exceptionDetails) return 'ERR ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300);
  const v = r.result && r.result.result; return v ? v.value : undefined;
}
async function where(pred, ms = 30000) {          // 哪一格里 pred 是真的
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    for (const x of [...ctxs]) { if (x.c.auxData && x.c.auxData.isDefault === false) continue; const v = await evIn(`try { return !!(${pred}); } catch (e) { return false; }`, x); if (v === true) return x; }
    await sleep(300);
  }
  return null;
}
const until = async (x, expr, ms = 8000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if ((await evIn(`try { return !!(${expr}); } catch (e) { return false; }`, x)) === true) return true; await sleep(150); } return false; };
await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
await send('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: false, flatten: true });
if (CSS_BODY) { await send('Fetch.enable', { patterns: [{ urlPattern: '*common/library.css*' }] }); say('（图书馆的样式换成了', CSS_FILE, '）'); }

/* ---------- 真鼠标、真手指：从最外头那一页照屏幕上的位置发 ---------- */
async function tapAt(x, y, how) {
  if (how === 'touch') {
    await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y, id: 1 }] }); await sleep(70);
    await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    return;
  }
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y }); await sleep(40);
  await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', buttons: 1, clickCount: 1 }); await sleep(60);
  await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
}
async function dragAt(x, y0, y1, x1) {          // 手指按住拖一截（竖着是滚，横着是翻页）
  const n = 8, xe = x1 == null ? x : x1;
  await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y: y0, id: 1 }] }); await sleep(40);
  for (let i = 1; i <= n; i++) { await send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x + (xe - x) * i / n, y: y0 + (y1 - y0) * i / n, id: 1 }] }); await sleep(24); }
  await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
}
const pressKey = async (key) => { for (const type of ['rawKeyDown', 'keyUp']) await send('Input.dispatchKeyEvent', { type, key, code: key, windowsVirtualKeyCode: key === 'Escape' ? 27 : key === 'ArrowRight' ? 39 : 37 }); };

/* 馆里一样东西在哪、看不看得见、那一点上最上面是谁。g 是取这一样东西的一句脚本（多半是 document.querySelector(...)）。
   不在滚动格里看得见的那一截就先把滚动格挪一挪（顶上留出顶栏那一条）；顶栏的钮不挪，照它本来在的地方点 */
const HIT = (g) => `const t = ${g}; if (!t) return JSON.stringify({ found: false });
  const sc = t.closest('.lx-scroller, .rd-toc .lx-box, .rd-margin, .rd-book.lx-scroll .rd-win');
  if (sc && !t.closest('.lb-top')) { const r = t.getBoundingClientRect(), R = sc.getBoundingClientRect(); if (r.top < R.top + 74 || r.bottom > R.bottom - 12) { sc.scrollTop += (r.top + r.height / 2) - (R.top + R.height / 2); await new Promise((r) => setTimeout(r, 160)); } }
  const b = t.getBoundingClientRect(), cs = getComputedStyle(t), cx = b.left + b.width / 2, cy = b.top + b.height / 2, hit = document.elementFromPoint(cx, cy);
  const nm = (n) => n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + (typeof n.className === 'string' && n.className ? '.' + n.className.trim().split(/\\s+/).slice(0, 3).join('.') : '');
  const pth = []; for (let n = hit; n && n !== document.documentElement && pth.length < 4; n = n.parentElement) pth.push(nm(n));
  return JSON.stringify({ found: true, x: cx, y: cy, w: Math.round(b.width), h: Math.round(b.height), shown: cs.display !== 'none' && cs.visibility !== 'hidden' && +cs.opacity > .2 && b.width > 2 && b.height > 2,
    pe: cs.pointerEvents, same: !!hit && (hit === t || t.contains(hit)), top: pth.join(' < ') || '（空的）', name: (t.getAttribute('aria-label') || t.textContent || '').trim().replace(/\\s+/g, '').slice(0, 14) });`;
const Q = (sel) => `document.querySelector(${JSON.stringify(sel)})`;
/* 馆的样子（Library.state 加页面上看得见的几样） */
const ST = `(() => { const s = Library.state, q = (x) => document.querySelector(x), lib = q('#lib'), off = (el) => !el || el.hidden || /lx-(off|back|zoom)/.test(el.className);
  return { open: s.open, view: s.view, hall: s.hall, book: s.book, page: s.page, pages: s.pages, spread: s.spread, spreads: s.spreads, mode: s.mode, busy: s.busy, mob: s.mob,
    on: !!lib && !lib.hidden && lib.classList.contains('lx-on'), gone: !lib || lib.hidden,
    vHall: !off(q('#lib .lb-hall')), vWing: !off(q('#lib .lb-wing')), vMap: !off(q('#lib .lb-map')),
    reader: !!q('#lib .lb-reader.lx-on') && !q('#lib .lb-reader').hidden, spoil: !!lib && lib.classList.contains('lx-spoil-on'),
    lend: !!q('#lib .lb-lend.lx-on') && !q('#lib .lb-lend').hidden, toc: !!q('#lib .rd-toc.lx-on') && !q('#lib .rd-toc').hidden, toast: !!q('#lib .lb-toast.lx-on'), slip: !!q('#lib .lb-slip.lx-on') }; })()`;
const IS = {
  open: 'S.open && S.on',
  hall: `S.open && S.view === 'hall' && S.vHall && !S.book`,
  wing: (k) => `S.open && S.view === 'wing' && S.hall === ${JSON.stringify(k)} && S.vWing`,
  map: `S.open && S.view === 'map' && S.vMap`,
  closed: '!S.open',
  reading: 'S.book && !S.busy && S.reader',
  shut: '!S.book && !S.busy && !S.reader',
};

let bad = 0, total = 0;
const fails = [];
let TAG = '';
const want = (ok, what) => { total++; if (!ok) { bad++; fails.push(TAG + '　' + what); say('   ✗ ' + what); } else say('   ✓ ' + what); return ok; };

/* ---------- 一种情形：把页面开到入口那一枚点得着的地方 ---------- */
// 假的日里里放的薄壳：照 小样_外壳/thin_local.html 的办法取外壳那一页换进来，五本书都认（那一份是 11-15 出的，不认此刻那一本）
function thinHTML() {
  const books = {}; for (const b of BOOKS) books[b] = { core: BASE + q(DIR[b]) + '/', parts: {} };
  const cfg = { ver: 'act_lib', mirror: BASE, books, old1001: BASE + q('小样_外壳') + '/old1001.html' };
  return '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body style="margin:0;background:#04050a"><script>'
    + '(function(){var SH=' + JSON.stringify(BASE + q('小样_外壳') + '/') + ',CFG=' + JSON.stringify(cfg) + ';'
    + 'function sized(){return new Promise(function(ok){var n=0;(function w(){if((innerWidth>0&&innerHeight>0)||n++>50)ok();else setTimeout(w,100)})()})}'
    + 'fetch(SH+"index.html").then(function(r){return r.text()}).then(function(html){sized().then(function(){'
    + 'var doc=\'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><base href="\'+SH+\'"><script>window.FRONT_CFG=\'+JSON.stringify(CFG)+\';<\\/script></head><body>\'+html+\'</body></html>\';'
    + 'document.open();document.write(doc);document.close()})})})();<\/script></body></html>';
}
const SHELL_PRED = 'window.__tb && window.Shell && window.Library';
const BOOK_IN_SHELL = `window.SHELL && window.Library && !window.Shell && document.querySelector('#wbBtn')`;
async function load(cs, hand) {
  errs = []; ctxs.length = 0; SOLO = BOOKS.includes(cs);
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
  await send('Emulation.setTouchEmulationEnabled', { enabled: hand === 'touch', maxTouchPoints: 5 });
  await send('Page.navigate', { url: 'about:blank' }); await sleep(300);
  const [kind, book] = cs.includes(':') ? cs.split(':') : BOOKS.includes(cs) ? ['book', cs] : [cs, ''];
  const url = kind === 'book' ? BASE + q(DIR[book]) + '/local.html?skip=1&t=' + Date.now()
    : kind === 'shell' ? BASE + q('小样_外壳') + '/local.html?t=' + Date.now()
      : (hand === 'touch' && !BARHOST ? HOST0 : BASE + q('探针') + '/host.html') + '?src=' + q('data:text/html;charset=utf-8,' + q(thinHTML())) + '&t=' + Date.now();
  const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
  await send('Page.navigate', { url });
  await Promise.race([loaded, sleep(15000)]); waiters.length = 0;
  const frames = [];          // 从外到里：每一层那一格在上一层里的位置（[那一层的环境, 取那一格的脚本]）
  let L = null;
  if (kind === 'book') {
    L = await where(`window.Library && !window.Shell && document.querySelector('#wbBtn')`, 40000);
    if (!L) return null;
  } else {
    if (kind === 'sandbox') { const Hc = await where(`document.getElementById('f') && document.getElementById('in')`, 15000); if (!Hc) return null; frames.push([Hc, Q('#f')]); }
    const S = await where(SHELL_PRED, 45000);
    if (!S) return null;
    await evIn(`__tb.skip(); return 1`, S); await sleep(2600);
    L = S;
    if (book) {
      await evIn(`Shell.openBook(${JSON.stringify(book)}); return 1`, S);
      const B = await where(BOOK_IN_SHELL, 50000);
      if (!B) return null;
      await until(S, `document.querySelector('#sh-book .sh-veil').classList.contains('off')`, 25000);
      frames.push([S, Q('#sh-frame')]);
      L = B;
    }
  }
  await until(L, 'window.Library && Library.state && !Library.missing', 15000);
  // 页面自己那一大段脚本走完了再点（入口的 click 是那一段末尾才绑的；单开一本书时一上来几十张图排着队载，书的 JSON 要等）
  await until(L, `document.readyState === 'complete' && (window.Shell || window.__bk || window.__mz || window.__now)`, 45000);
  // 入口那一枚点得着了再往下走（书一翻开有一段题字，过去了才让点）
  const ok = await until(L, `(() => { const t = document.querySelector('#wbBtn'); if (!t) return false; const b = t.getBoundingClientRect(), cs = getComputedStyle(t), h = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2); return cs.pointerEvents !== 'none' && +cs.opacity > .5 && h && t.contains(h); })()`, 9000);
  if (!ok) { await evIn(`try { const B_ = window.__bk || window.__mz || {}; if (B_.begin) B_.begin(); if (B_.go && window.__mz) B_.go(2); } catch (e) {} return 1`, L); await sleep(1500); }
  return { L, frames, land: book ? LAND[book] : 'hall', cs, hand };
}

/* ---------- 走 ---------- */
function runner(P, round) {
  const { L } = P;
  const state = async () => { try { return JSON.parse(await evIn(`return JSON.stringify(${ST})`, L)); } catch (e) { return {}; } };
  const cond = (expr, ms) => until(L, `(() => { const S = ${ST}; return ${expr}; })()`, ms);
  async function offset() { let x = P.fix ? P.fix[0] : 0, y = P.fix ? P.fix[1] : 0; for (const [cx, g] of P.frames) { const r = await evIn(`const e = ${g}; if (!e) return '[0,0]'; const b = e.getBoundingClientRect(); return JSON.stringify([b.left, b.top])`, cx); try { const [a, b] = JSON.parse(r); x += a; y += b; } catch (e) { /* 照 0 */ } } return [x, y]; }
  /* 校一下：从最外头发的一下，到了馆那一格里按下落在哪、click 落在哪。先在那一格里盖一层透明的把这一下接住（事件不往下传），页面上什么都不会动，量完撤掉。
     差了就记在 P.fix 里，往后每一下照 click 落下的地方补上，并在日志里说一声：差的是走查这一头发点的事，不是页面的毛病（一下都收不到才算对不上）。
     11-25 量到的：假的日里里装着书（两层沙箱格）时，无头 Chrome 发的手指按下落得准，跟着合成的 click 往上偏一截，偏的正好是外头那一格离页面顶上的距离（64px），
     名牌点成上面那一块、顶栏的钮点到格子外头去。鼠标不偏；一层格不偏。所以假的日里那几种情形手指用 HOST0 那张壳（格子贴着左上角），这里留着当保险。 */
  async function calibrate() {
    P.fix = [0, 0];
    const [ox, oy] = await offset();
    const sz = JSON.parse(await evIn(`
      if (!window.__evs) { window.__evs = [];
        for (const ev of ['touchstart', 'touchend', 'touchcancel', 'pointerdown', 'pointerup', 'pointercancel', 'mousedown', 'mouseup', 'click']) window.addEventListener(ev, (e) => { const t = (e.touches && e.touches[0]) || (e.changedTouches && e.changedTouches[0]) || e; const n = e.target;
          window.__evs.push(ev + ' ' + Math.round(t.clientX) + ',' + Math.round(t.clientY) + ' ' + (n && n.tagName ? n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + (typeof n.className === 'string' && n.className ? '.' + n.className.trim().split(/\\s+/).slice(0, 2).join('.') : '') : '')); if (window.__evs.length > 14) window.__evs.shift(); }, { capture: true, passive: true }); }
      const old = document.getElementById('__actcal'); if (old) old.remove();
      const d = document.createElement('div'); d.id = '__actcal'; d.style.cssText = 'position:fixed;left:0;top:0;right:0;bottom:0;z-index:2147483647;background:transparent;pointer-events:auto';
      window.__cal = {};
      for (const ev of ['touchstart', 'touchend', 'pointerdown', 'pointerup', 'mousedown', 'mouseup', 'click']) d.addEventListener(ev, (e) => { e.stopPropagation(); const t = (e.touches && e.touches[0]) || (e.changedTouches && e.changedTouches[0]) || e; if (!(ev in window.__cal)) window.__cal[ev] = [Math.round(t.clientX), Math.round(t.clientY)]; });
      document.body.appendChild(d);
      return JSON.stringify([innerWidth, innerHeight])`, L) || '[0,0]');
    const lx = Math.round(sz[0] * 0.5), ly = Math.round(sz[1] * 0.42);
    await tapAt(ox + lx, oy + ly, P.how);
    await sleep(500);
    let got = {}; try { got = JSON.parse(await evIn(`const d = document.getElementById('__actcal'); if (d) d.remove(); return JSON.stringify(window.__cal || {})`, L)) || {}; } catch (e) { /* 没收到 */ }
    const dn = P.how === 'touch' ? got.touchstart : got.mousedown, ck = got.click;
    if (!dn && !ck) { want(false, `校点：从最外头发的${HAND[P.how]}，馆那一格里没收到（发在 ${Math.round(ox + lx)},${Math.round(oy + ly)}）`); return; }
    const d1 = dn ? [dn[0] - lx, dn[1] - ly] : null, d2 = ck ? [ck[0] - lx, ck[1] - ly] : null;
    const use = d2 || d1;
    if (!ck) say(`     校点：这一下${HAND[P.how]}按下收到了，没有跟着出 click（发在 ${Math.round(ox + lx)},${Math.round(oy + ly)}）`);
    if (use[0] || use[1] || (d1 && (d1[0] || d1[1]))) {
      P.fix = [-use[0], -use[1]];
      say(`     校点：发出去的${HAND[P.how]}到了馆那一格里，按下偏 ${d1 ? d1.join(',') : '（没收到）'}、click 偏 ${d2 ? d2.join(',') : '（没有）'}（各层格的位置 ${Math.round(ox)},${Math.round(oy)}）；是走查这一头发点的事，往后每一下照 click 的补上`);
    }
  }
  let shotN = 0;
  const shot = async (name) => { if (!SHOTS) return; const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 82 }); fs.writeFileSync(path.join(SHOTS, `${P.cs.replace(':', '-')}_${W}_${HAND[P.how]}_${round}${String(++shotN).padStart(2, '0')}_${name}.jpg`), Buffer.from(r.result.data, 'base64')); };
  /* 点一样东西，等 expect 成真。没点着的时候拿 rescue 那一句补上，后头的步子照样查得下去 */
  async function tap(what, g, expect, o = {}) {
    const how = o.how || P.how;
    let h;
    try { h = JSON.parse(await evIn(HIT(g), L)); } catch (e) { h = { found: false }; }
    if (!h.found) { want(false, `${what}：页面上没有这一样`); if (o.rescue) await evIn(o.rescue + '; return 1', L); return false; }
    const [ox, oy] = await offset();
    const x = ox + h.x + (o.dx || 0) * h.w, y = o.topPx != null ? oy + h.y - h.h / 2 + o.topPx : oy + h.y + (o.dy || 0) * h.h;          // dx、dy 是离正中几成，topPx 是离上沿几个像素
    await evIn(`window.__evs = []; return 1`, L);
    await tapAt(x, y, how);
    const ok = expect ? await cond(expect, o.ms || 6000) : true;
    let why = '';
    if (!ok) { const s = await state(); why = `　没点着：点在 ${Math.round(x)},${Math.round(y)}，这一枚${h.shown ? '' : '看不见，'}pointer-events ${h.pe}，那一点上最上面是 ${h.top}；馆这会儿 ${JSON.stringify({ open: s.open, view: s.view, hall: s.hall, book: s.book, busy: s.busy, vHall: s.vHall, vWing: s.vWing, vMap: s.vMap, reader: s.reader })}，各层 ${await evIn(`const f = await Promise.race([new Promise((r) => requestAnimationFrame(() => r('走'))), new Promise((r) => setTimeout(() => r('不走'), 1500))]); return [...document.querySelectorAll('#lib .lb-v')].map((e) => e.className.replace('lb-v ', '') + (e.hidden ? '[hidden]' : '')).join(' | ') + '，帧' + f + '，页面' + document.visibilityState + '；这一格收到的 ' + ((window.__evs || []).join(' / ') || '（什么都没收到）')`, L)}`; }
    want(ok, `${what}（${HAND[how]}）` + why);
    if (!ok) await shot('没点着_' + what.replace(/[\\/:*?"<>|（）《》“”，、：\s]+/g, '').slice(0, 24));          // 补上以前先照一张：点了以后页面还是原样
    if (!ok && o.rescue) { await evIn(o.rescue + '; return 1', L); if (expect) await cond(expect, 4000); }
    await sleep(o.wait == null ? 650 : o.wait);
    return ok;
  }
  const TOP_BK = Q('#lib .lb-top .lx-bk'), TOP_X = Q('#lib .lb-top .lx-x'), ENTRY = Q('#wbBtn');
  const arch = (k) => Q(`#lib .lb-arch[data-k="${k}"]`);
  const spine = (k, pi) => Q(`#lib .lb-wing .lb-sp[data-b="${k}"]${pi != null ? `[data-pi="${pi}"]` : ''}`);
  const JS = { hall: `Library.close(true); Library.open()`, close: `Library.close(true)`, shut: `document.querySelector('#lib .rd-top .lx-sh').click()` };
  const backHall = (from) => tap(`${from}点回圆厅`, TOP_BK, IS.hall, { rescue: `(() => { const b = document.querySelector('#lib .lb-top .lx-bk'); if (b) b.click(); })()` });
  const leave = async (from) => {
    const ok = await tap(`${from}点出馆`, TOP_X, IS.closed, { rescue: JS.close, wait: 700 });
    const s = await state();
    want(s.gone, `${from}出了馆，馆那一层收掉了`);
    let h = {}; try { h = JSON.parse(await evIn(HIT(ENTRY), L)); } catch (e) { /* 没有 */ }
    want(h.found && h.same && h.pe !== 'none', `${from}出了馆，入口那一枚又点得着` + (h.same ? '' : `　那一点上最上面是 ${h.top}`));
    return ok;
  };
  async function enter(first) {          // 从入口进，走到圆厅
    const ok = await tap(first ? '入口那一枚进馆' : '再从入口进馆', ENTRY, IS.open, { rescue: P.land === 'hall' ? `Library.open()` : `Library.open(${JSON.stringify(P.land)})`, wait: 300 });
    await cond(P.land === 'hall' ? IS.hall : IS.wing(P.land), 10000); await sleep(1000);          // 书目取到了才搭出厅来
    await until(L, `document.querySelector('#lib .lb-v:not([hidden])').classList.contains('lx-has-img')`, 6000);          // 这一屏的主画到了再往下（头一回开页面图排着队，慢的时候要两三秒；没有主画就等满这几秒）
    const s = await state();
    if (P.land !== 'hall') {
      want(s.view === 'wing' && s.hall === P.land, `书里进馆落在${ERA[P.land]}廊`);
      await backHall(`${ERA[P.land]}廊（一进馆）`);
    } else want(s.view === 'hall' && s.vHall, '进馆是圆厅');
    const b = JSON.parse(await evIn(HIT(TOP_BK), L) || '{}');
    want(!b.shown, '圆厅里没有“回圆厅”那一枚');
    return ok;
  }
  const toWing = (k, nm) => tap(`圆厅点${nm}的拱门`, arch(k), IS.wing(k), { rescue: `Library.open(${JSON.stringify(k)})`, wait: 900 });
  const openBook = (k, nm, pi) => tap(`抽出${nm}翻开`, spine(k, pi), `S.book === ${JSON.stringify(k)} && !S.busy && S.reader`, { ms: 40000, rescue: `Library.openBook(${JSON.stringify(k)})`, wait: 500 });
  const shutBook = (nm) => tap(`${nm}点“合上，放回去”`, Q('#lib .rd-top .lx-sh'), IS.shut, { ms: 9000, wait: 500 });
  /* 这一屏上的钮有没有叫别的层盖着：每一枚取十三个点（当中三成、五成、七成处九个，四条边当中靠里一成处各一个），那一点上最上面不是它自己就算盖着一处。
     看不见的层（透明的、opacity 0 的）照样会接走指针，眼睛看不出来，点正中又点得着，只有这样一处一处问才查得出。
     滚动格里没露全的不算；手机上滚到顶栏底下的那几行叫顶栏的钮压着是本来的样子，也不算 */
  async function cover(label, scopes) {
    const r = await evIn(`const nm = (n) => n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + (typeof n.className === 'string' && n.className ? '.' + n.className.trim().split(/\\s+/).slice(0, 3).join('.') : '');
      const out = [];
      for (const b of document.querySelectorAll(${JSON.stringify(scopes.map((s) => s + ' button, ' + s + ' summary').join(', '))})) {
        const r = b.getBoundingClientRect(), cs = getComputedStyle(b);
        if (r.width < 8 || r.height < 8 || cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < .2 || b.disabled || b.closest('[hidden]')) continue;
        const sc = b.closest('.lx-scroller, .rd-toc .lx-box, .rd-win');
        if (sc) { const R = sc.getBoundingClientRect(); if (r.top < R.top || r.bottom > R.bottom || r.left < R.left || r.right > R.right) continue; }
        if (r.left < 0 || r.top < 0 || r.right > innerWidth || r.bottom > innerHeight) continue;
        let bad = 0, who = '';
        const pts = [[.5, .1], [.5, .9], [.1, .5], [.9, .5]]; for (const fx of [.3, .5, .7]) for (const fy of [.3, .5, .7]) pts.push([fx, fy]);
        for (const [fx, fy] of pts) {
          const h = document.elementFromPoint(r.left + r.width * fx, r.top + r.height * fy);
          if (!h || h === b || b.contains(h)) continue;
          if (h.closest('.lb-top') && !b.closest('.lb-top')) continue;
          bad++; who = nm(h);
        }
        if (bad) out.push((b.getAttribute('aria-label') || b.textContent || nm(b)).trim().replace(/\\s+/g, '').slice(0, 12) + '（' + nm(b) + '）' + bad + '/13 处叫 ' + who + ' 盖着' + (cs.pointerEvents === 'none' ? '，它自己 pointer-events none' : ''));
      }
      return JSON.stringify(out)`, L);
    let list = []; try { list = JSON.parse(r); } catch (e) { list = ['查不了：' + String(r).slice(0, 120)]; }
    want(!list.length, `${label}：这一屏上的钮没有叫别的层盖着` + (list.length ? '　' + list.slice(0, 6).join('；') + (list.length > 6 ? ` ……共 ${list.length} 枚` : '') : ''));
  }
  /* 电脑版（宽 760 以上）一廊的书脊都要在屏里：电脑版的廊不滚，伸出屏外的那几本就点不着了（11-25 往前的廊在 820、1024 宽的时候最外头一纪整个在屏外）。
     手机版是一列往下滚的，不查 */
  async function inView(label) {
    if (W < 760) return;
    const r = await evIn(`const out = [];
      for (const b of document.querySelectorAll('#lib .lb-wing .lb-sp')) { const r = b.getBoundingClientRect(); if (r.width < 2) continue; if (r.left < 0 || r.right > innerWidth) out.push((b.getAttribute('aria-label') || '').slice(0, 10) + ' ' + Math.round(r.left) + '～' + Math.round(r.right)); }
      return JSON.stringify(out)`, L);
    let list = []; try { list = JSON.parse(r); } catch (e) { list = ['查不了：' + String(r).slice(0, 120)]; }
    want(!list.length, `${label}：书脊都在屏里` + (list.length ? '　' + list.length + ' 本伸出屏外：' + list.slice(0, 5).join('；') : ''));
  }
  /* 翻开的书里这一叠上看得全的头一样 sel（卷着读的时候不管在不在这一屏，点以前会滚过去） */
  const VIS = (sel) => `(() => { const win = document.querySelector('#lib .rd-win'); if (!win) return null; const w = win.getBoundingClientRect(), roll = !!win.closest('.lx-scroll');
    return [...document.querySelectorAll(${JSON.stringify(sel)})].find((e) => { const r = e.getBoundingClientRect(); return r.width > 1 && r.height > 1 && (roll || (r.left >= w.left - 2 && r.right <= w.right + 2 && r.top >= w.top - 2 && r.bottom <= w.bottom + 2)); }) || null; })()`;
  /* 一节一节、一叠一叠翻着找，找到停在那里（头六节、每节头八叠） */
  async function seek(sel) {
    const s = await state(), secs = (s.pages || []).filter((p) => /^sec\d+$/.test(p)).map((p) => +p.slice(3)).slice(0, 6);
    for (const i of secs) {
      await evIn(`Library._goto(${i}); return 1`, L); await sleep(350);
      const n = Math.min((await state()).spreads || 1, 8);
      for (let sp = 0; sp < n; sp++) {
        if (sp) { await evIn(`Library._goto(${i}, ${sp}); return 1`, L); await sleep(700); }
        if (await evIn(`return !!${VIS(sel)}`, L)) return true;
      }
    }
    return false;
  }

  /* 回圆厅、出馆那一圈 */
  async function keys() {
    say(` — 回圆厅、出馆（${HAND[P.how]}）`);
    await enter(true);
    await shot('圆厅'); await cover('圆厅', ['#lib .lb-top', '#lib .lb-hall']);
    await toWing('ming', '命路厅'); await shot('命路厅'); await cover('命路厅', ['#lib .lb-top', '#lib .lb-wing']);
    await backHall('命路厅'); await shot('命路厅点回圆厅以后');
    await tap('圆厅点地图室的拱门', arch('map'), IS.map, { rescue: `Library.open('map')`, wait: 900 }); await shot('地图室'); await cover('地图室', ['#lib .lb-top', '#lib .lb-map']);
    await backHall('地图室');
    await toWing('ming', '命路厅');
    if (await openBook('ming-zddyslbcxqstgm', '《战斗的艺术》上册（长的）', 0)) {
      await shot('翻开_战斗的艺术'); await cover('翻开的书', ['#lib .rd-top', '#lib .rd-nav']);
      const c = JSON.parse(await evIn(HIT(TOP_X), L) || '{}');
      say(`     翻开的时候顶栏那两枚叫书页盖着（本来就这样，先合上书）：出馆那一点上最上面是 ${c.top}`);
      await shutBook('《战斗的艺术》');
    } else await evIn(`${JS.shut}; return 1`, L);
    await backHall('合上书以后在命路厅');
    await toWing('arcane', '奥法与工程厅');
    if ((await state()).mob) {          // 手机上厅是一列（这一厅四十来本），拖着往下滚一截，顶栏还在原处
      const [ox, oy] = await offset();
      const vh = +(await evIn(`return innerHeight`, L)), vw = +(await evIn(`return innerWidth`, L));
      const y0 = await evIn(`return document.querySelector('#lib .lb-wing').scrollTop`, L);
      await dragAt(ox + vw / 2, oy + vh * 0.78, oy + vh * 0.3); await sleep(700);
      const y1 = await evIn(`return document.querySelector('#lib .lb-wing').scrollTop`, L);
      if (P.how === 'touch') want(y1 > y0 + 40, `手机上厅里手指拖得动（滚了 ${Math.round(y1 - y0)}px）`);
      else await evIn(`document.querySelector('#lib .lb-wing').scrollTop = 500; return 1`, L);
      await shot('奥法与工程厅_滚了一截');
    }
    await leave('奥法与工程厅'); await shot('奥法与工程厅点出馆以后');
    await enter();
    await leave('圆厅');
    await enter();
    await tap('圆厅点地图室的拱门', arch('map'), IS.map, { rescue: `Library.open('map')`, wait: 900 });
    await leave('地图室');
    await enter();
    await toWing('ming', '命路厅');
    if (await openBook('ming-jd', '《角抵》（八十多张插图）')) {
      await evIn(`Library._goto(1); return 1`, L); await sleep(1200);
      const im = await evIn(`const a = [...document.querySelectorAll('#lib .rd-flow figure.lx-plate img')]; await Promise.all(a.slice(0, 6).map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; setTimeout(r, 6000); }))); return JSON.stringify({ n: a.length, ok: a.filter((i) => i.naturalWidth > 0).length })`, L);
      say('     插图', im);
      await shot('翻开_角抵_插图');
      await shutBook('《角抵》');
    } else await evIn(`${JS.shut}; return 1`, L);
    await leave('合上带插图的书以后在命路厅');
  }

  /* 别的钮 */
  async function others() {
    say(` — 别的钮（${HAND[P.how]}）`);
    await enter(true);
    const sp0 = (await state()).spoil;
    await tap('顶栏剧透开关：开', Q('#lib .lb-top .lb-spl'), `S.spoil === ${!sp0}`, { wait: 300 });
    await tap('顶栏剧透开关：关回去', Q('#lib .lb-top .lb-spl'), `S.spoil === ${sp0}`, { wait: 300 });
    await tap('长桌一角的借阅卡', Q('#lib .lb-hall .lb-card'), 'S.lend', { rescue: `document.querySelector('#lib .lb-hall .lb-card').click()` });
    await shot('借阅卡'); await cover('借阅卡', ['#lib .lb-lend']);
    await tap('借阅卡“放回去”', Q('#lib .lb-lend .lx-x'), '!S.lend', { rescue: `document.querySelector('#lib .lb-lend .lx-x').click()` });
    if (await tap('长桌上摊着的那一本', Q('#lib .lb-hall .lb-open'), IS.reading, { ms: 40000, wait: 500 })) await shutBook('《万物的清点》'); else await evIn(`${JS.shut}; return 1`, L);
    await sleep(500);
    await toWing('shen', '神与魔神厅');
    if (await openBook('shen-qsey', '《七十二域》（剧透多）')) {
      const pos = async () => { const s = await state(); return s.page + ':' + s.spread; };
      let p0 = await pos();
      await tap('往后翻', Q('#lib .rd-nav .lx-nx'), `(S.page + ':' + S.spread) !== ${JSON.stringify(p0)}`, { wait: 700 });
      p0 = await pos();
      await tap('往后翻（再一回）', Q('#lib .rd-nav .lx-nx'), `(S.page + ':' + S.spread) !== ${JSON.stringify(p0)}`, { wait: 700 });
      p0 = await pos();
      await tap('往前翻', Q('#lib .rd-nav .lx-pv'), `(S.page + ':' + S.spread) !== ${JSON.stringify(p0)}`, { wait: 700 });
      await tap('目录', Q('#lib .rd-top .lx-tc'), 'S.toc', { wait: 500 });
      await shot('目录');
      p0 = await pos();
      await tap('目录里点一节', `[...document.querySelectorAll('#lib .rd-toc .lx-it:not(.lx-here):not(.lx-pt)')].slice(-2)[0]`, `!S.toc && (S.page + ':' + S.spread) !== ${JSON.stringify(p0)}`, { wait: 600 });
      const m0 = (await state()).mode, other = m0 === 'page' ? 'scroll' : 'page';
      await tap(m0 === 'page' ? '卷着读' : '一页一页翻', Q('#lib .rd-top .lx-md'), `S.mode === '${other}'`, { wait: 500 });
      await tap(other === 'page' ? '卷着读（换回去）' : '一页一页翻（换回去）', Q('#lib .rd-top .lx-md'), `S.mode === '${m0}'`, { wait: 500 });
      // 青火印：翻到头一节有印的地方，点印出一句提示；书里的剧透开关开了，印揭开
      if ((await state()).spoil) { await evIn(`document.querySelector('#lib .rd-top .lb-spl').click(); return 1`, L); await sleep(500); }
      const SEAL = '#lib .rd-flow .lb-seal, #lib .rd-flow .lb-secseal';
      if (await seek(SEAL)) {
        await tap('点一枚青火印（出一句提示）', VIS(SEAL), 'S.toast && !S.spoil', { wait: 400 });
        await shot('青火印');
        await tap('书里的剧透开关：开', Q('#lib .rd-top .lb-spl'), 'S.spoil', { wait: 600 });
        want(await evIn(`const c = document.querySelector('#lib .rd-flow .lx-sp-c'), s = document.querySelector('#lib .rd-flow .lb-seal, #lib .rd-flow .lb-secseal'); return !!c && getComputedStyle(c).display !== 'none' && (!s || getComputedStyle(s).display === 'none')`, L), '开了剧透，印收了，底下的字出来了');
        await shot('青火印_揭开');
        await tap('书里的剧透开关：关回去', Q('#lib .rd-top .lb-spl'), '!S.spoil', { wait: 600 });
      } else say('     这一本头几节没翻到青火印，这几步跳过');
      // 纸页两边点一下翻页（一页一页翻的时候，点在纸的上沿那一条白边上）；手指横着划
      if ((await state()).mode !== 'page') { await evIn(`Library._mode('page'); return 1`, L); await sleep(500); }
      const BK = Q('#lib .rd-book');
      for (const p of ((await state()).pages || []).filter((p) => /^sec/.test(p)).slice(0, 6)) { await evIn(`Library._goto(${+p.slice(3)}); return 1`, L); await sleep(300); if ((await state()).spreads > 1) break; }
      await sleep(400);
      if ((await state()).spreads > 1) {
        await tap('点纸页右边翻过去', BK, 'S.spread === 1', { dx: 0.43, topPx: 12, wait: 800 });
        await tap('点纸页左边翻回来', BK, 'S.spread === 0', { dx: -0.43, topPx: 12, wait: 800 });
        if (P.how === 'touch') {
          const h = JSON.parse(await evIn(HIT(BK), L)), [ox, oy] = await offset();
          await dragAt(ox + h.x + h.w * 0.3, oy + h.y, oy + h.y, ox + h.x - h.w * 0.3);
          want(await cond('S.spread === 1', 3000), '手指横着划，翻过去一叠'); await sleep(700);
        }
      } else say('     头几节都只有一叠，纸页两边那两步跳过');
      await shot('翻开_七十二域');
      await shutBook('《七十二域》');
    } else await evIn(`${JS.shut}; return 1`, L);
    await backHall('神与魔神厅');
    await toWing('ming', '命路厅');
    // 注号：电脑上页边那一条亮一下，没有页边的时候（手机、窄屏）浮一张小纸条，点纸条收起来
    if (await openBook('ming-zddyslbcxqstgm', '《战斗的艺术》上册', 0)) {
      const FN = '#lib .rd-flow > :not(.lx-sp-g) sup.lx-fn';
      if (await seek(FN)) {
        await tap('点一个注号', VIS(FN), `S.slip || !!document.querySelector('#lib .rd-margin .lx-mn.lx-lit')`, { wait: 500 });
        await shot('注');
        if ((await state()).slip) await tap('点小纸条收起来', Q('#lib .lb-slip'), '!S.slip', { wait: 300 });
      } else say('     头几节没翻到看得见的注号，这一步跳过');
      await shutBook('《战斗的艺术》');
    } else await evIn(`${JS.shut}; return 1`, L);
    await sleep(400);
    // 插图底下的原文：点标签折起来
    if (await openBook('ming-jd', '《角抵》')) {
      const SUM = '#lib .rd-flow figure.lx-plate details[open] > summary';
      if (await seek(SUM)) {
        const n0 = await evIn(`return document.querySelectorAll('#lib .rd-flow figure.lx-plate details[open]').length`, L);
        await tap('插图底下的标签：折起原文', VIS(SUM), `document.querySelectorAll('#lib .rd-flow figure.lx-plate details[open]').length === ${n0} - 1`, { wait: 500 });
      } else say('     头几节没翻到看得全的插图标签，这一步跳过');
      await shutBook('《角抵》');
    } else await evIn(`${JS.shut}; return 1`, L);
    await backHall('命路厅');
    // 往前的廊、往后的廊
    await toWing('past', '往前的廊');
    await inView('往前的廊');
    await tap('往前的廊：烫手的书抽不出来（出一句话）', Q('#lib .lb-wing .lb-sp.lx-hot'), 'S.toast && !S.book && !S.busy', { wait: 400 });
    await shot('往前的廊');
    await backHall('往前的廊');
    await toWing('future', '往后的廊');
    await inView('往后的廊');
    await tap('往后的廊：还没写成的书（出一句话）', Q('#lib .lb-wing .lb-sp.lx-white:not(.lx-mine)'), 'S.toast && !S.book && !S.busy', { wait: 400 });
    await backHall('往后的廊');
    // 地图室：点一张翻世界之书的地图，合上世界之书还在地图室
    await tap('圆厅点地图室的拱门', arch('map'), IS.map, { rescue: `Library.open('map')`, wait: 900 });
    if (await tap('地图室点月银纪那一张', Q('#lib .lb-map .lb-mc[data-v="moon"]'), `window.Codex && Codex.isOpen()`, { wait: 1500, rescue: `Codex.open('moon', 'map')` })) {
      await shot('地图室_世界之书');
      await tap('世界之书“合上”', Q('#wb > .x'), `!Codex.isOpen() && ${IS.map}`, { wait: 900, rescue: `Codex.close()` });
    }
    await backHall('合上世界之书以后在地图室');
    // 键盘
    if (W >= 760) {
      await toWing('crown', '星冠圣堂厅');
      await pressKey('Escape'); want(await cond(IS.hall, 4000), 'Esc：从厅里退回圆厅'); await sleep(700);
      await pressKey('Escape'); want(await cond(IS.closed, 4000), 'Esc：从圆厅出馆'); await sleep(700);
    } else await leave('圆厅（末了）');
  }
  return { keys, others, state, shot, calibrate };
}

for (const cs of CASES) {
  for (const how of HANDS) {
    TAG = `${cs} ${W}×${H} ${HAND[how]}`;
    say(`\n== ${TAG}`);
    const P = await load(cs, how);
    if (!P) { want(false, '页面没有开起来（外壳、书或者图书馆没载上）'); continue; }
    P.how = how;
    const R = runner(P, 'a');
    try {
      await R.calibrate();
      await R.keys();
      if (!KEYS_ONLY && how === (HANDS.includes(PRIMARY) ? PRIMARY : HANDS[0])) {
        // 别的钮重开一回页面走，免得上一圈留下什么
        const P2 = await load(cs, how);
        if (P2) { P2.how = how; const R2 = runner(P2, 'b'); await R2.calibrate(); await R2.others(); } else want(false, '第二回页面没有开起来');
      }
    } catch (e) { want(false, '走查脚本自己出了错：' + String(e && e.stack || e).slice(0, 300)); }
    const es = [...new Set(errs)];
    if (es.length) { say(`   页面报错 ${es.length} 条`); for (const x of es.slice(0, 8)) say('     ', x); }
  }
}
say(`\n点了、核了 ${total} 处，对不上的 ${bad} 处`);
for (const f of fails) say('  ✗', f);
finished = true;
ws.close();
stop(Math.min(bad, 100));
