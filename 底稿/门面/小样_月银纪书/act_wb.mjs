// 介绍页收尾（11-15）的走查：世界之书、地图、剧透开关、卡片。一样一样点，收报错，各截一张图。
//   node act_wb.mjs <宽> <高> <截图前缀>
// 本地服务器是 .claude/launch.json 的 front-book（8768），无头 Chrome 在 9335。
import fs from 'node:fs';
const [W, H, OUT] = [+process.argv[2], +process.argv[3], process.argv[4] || 'wb'];
const PORT = 9335, ADDR = 'http://localhost:8768/local.html?skip=1';
const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pending = new Map(), errs = [], waiters = [];
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); return; }
  if (m.method === 'Runtime.exceptionThrown') errs.push('异常 ' + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
  if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('报错 ' + m.params.args.map((a) => a.value || a.description || '').join(' ').slice(0, 300));
  if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) errs.push(m.params.response.status + ' ' + m.params.response.url.replace('http://localhost:8768/', ''));
  if (m.method === 'Network.loadingFailed' && !m.params.canceled) errs.push('载不下来 ' + (m.params.errorText || ''));
  for (const w of waiters) if (w.ev === m.method) w.fn(m);
};
const send = (method, params = {}) => new Promise((r) => { const id = ++seq; pending.set(id, r); ws.send(JSON.stringify({ id, method, params })); });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: `(async () => { ${expr} })()`, returnByValue: true, awaitPromise: true }); if (r.result && r.result.exceptionDetails) errs.push('脚本 ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300)); return r.result && r.result.result ? r.result.result.value : undefined; };
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 86 }); fs.writeFileSync(`${OUT}_${name}.jpg`, Buffer.from(r.result.data, 'base64')); };
// 真鼠标点一处（地图的点要按下抬起才算）
const clickAt = async (x, y) => {
  for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', buttons: type === 'mousePressed' ? 1 : 0, clickCount: 1 });
};
const centerOf = async (sel) => JSON.parse(await ev(`const el = document.querySelector(${JSON.stringify(sel)}); if (!el) return 'null'; el.scrollIntoView({block:'center'}); const r = el.getBoundingClientRect(); return JSON.stringify([r.left + r.width / 2, r.top + r.height / 2]);`));
const say = (...a) => console.log(...a);

await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: W < 760 });
const loaded = new Promise((r) => waiters.push({ ev: 'Page.loadEventFired', fn: r }));
await send('Page.navigate', { url: ADDR + '&t=' + Date.now() });
await Promise.race([loaded, sleep(15000)]); await sleep(2500);

// 一、墙上的入口
let c = await centerOf('#wbBtn'); say('入口', c);
await clickAt(...c); await sleep(700);
say('打开以后', JSON.stringify(await ev(`return JSON.stringify(__bk.wb)`)));
say('卷', await ev(`return [...document.querySelectorAll('#wb .vol')].map(v => v.textContent + (v.classList.contains('off') ? '（灰）' : '')).join(' / ')`));
say('页', await ev(`return [...document.querySelectorAll('#wb .pg')].map(v => v.textContent).join(' / ')`));
await shot('1_书');

// 二、地图页
await ev(`document.querySelector('#wb .pg[data-p="map"]').click(); return 1`); await sleep(900);
const mp = JSON.parse(await ev(`const f = document.querySelector('.wm-frame'), im = document.querySelector('.wm-in img'); await new Promise(r => { if (im.complete) r(); else im.onload = r; }); return JSON.stringify({ pins: document.querySelectorAll('.wm-pin').length, img: im.naturalWidth, frame: [f.clientWidth, f.clientHeight], tabs: document.querySelectorAll('.wm-tabs button').length })`));
say('地图', JSON.stringify(mp));
await shot('2_地图');
c = await centerOf('.wm-pin.main'); await clickAt(...c); await sleep(400);
say('点了一处', await ev(`const k = document.querySelector('.wm-card'); return k.hidden ? '小卡没出' : k.textContent.slice(0, 80)`));
await shot('3_小卡');
// 换年代、放大
await ev(`document.querySelectorAll('.wm-tabs button')[2].click(); return 1`); await sleep(600);
const fc = await centerOf('.wm-frame');
for (let k = 0; k < 4; k++) await send('Input.dispatchMouseEvent', { type: 'mouseWheel', x: fc[0], y: fc[1], deltaX: 0, deltaY: -120 });
await sleep(400);
say('放大以后', await ev(`return document.querySelector('.wm-in').style.transform + ' z2=' + document.querySelector('.wm-frame').classList.contains('z2')`));
await shot('4_放大');
// 小卡上的时代 → 合上书、进时代页
// 放大以后挑一个还在框里的点（框外的点叫 overflow 裁掉了，点不到）
c = JSON.parse(await ev(`const f = document.querySelector('.wm-frame').getBoundingClientRect(); for (const p of document.querySelectorAll('.wm-pin i')) { const r = p.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2; if (x > f.left + 40 && x < f.right - 60 && y > f.top + 20 && y < f.bottom - 20) return JSON.stringify([x, y]); } return 'null'`));
await clickAt(...c); await sleep(400);
const chip = await ev(`const b = document.querySelector('.wm-card [data-era]'); return b ? b.dataset.era : ''`);
await ev(`const b = document.querySelector('.wm-card [data-era]'); if (b) b.click(); return 1`); await sleep(1200);
say('从地图进时代', chip, JSON.stringify(await ev(`return JSON.stringify({ wb: __bk.wb.open, page: __bk.s.pageOpen })`)));

// 三、时代页：剧透开关、小地图、卡片
await ev(`__bk.close(); return 1`); await sleep(700);
await ev(`__bk.open(6); return 1`); await sleep(1200);
const before = await ev(`return [...document.querySelectorAll('#pg-body .spoil')].filter(e => getComputedStyle(e).display !== 'none').length + '/' + document.querySelectorAll('#pg-body .spoil').length`);
await ev(`document.querySelector('#pg-body .spl').click(); return 1`); await sleep(700);
const after = await ev(`return [...document.querySelectorAll('#pg-body .spoil')].filter(e => getComputedStyle(e).display !== 'none').length + '/' + document.querySelectorAll('#pg-body .spoil').length`);
say('剧透 关着看得见', before, '开了看得见', after);
await ev(`document.querySelector('#pg-body .spl').scrollIntoView({block:'start'}); return 1`); await sleep(300);
await shot('5_时代页');
await ev(`document.querySelector('#pg-body .spl').click(); return 1`); await sleep(500);
const mini = await ev(`const m = document.querySelector('#pg-body .mini'); return m ? m.querySelectorAll('i').length + '个点' : '没有小地图'`);
say('小地图', mini);
await ev(`const m = document.querySelector('#pg-body .mini'); if (m) m.scrollIntoView({block:'center'}); return 1`); await sleep(300);
await shot('6_小地图');
await ev(`document.querySelector('#pg-body .mini').click(); return 1`); await sleep(1000);
say('点小地图', JSON.stringify(await ev(`return JSON.stringify({ wb: __bk.wb, hi: document.querySelectorAll('.wm-pin.hi').length })`)));
await shot('7_这一纪的地方');
await ev(`__bk.closeWB(); return 1`); await sleep(500);
// 卡片
const who = await ev(`const p = document.querySelector('#pg-body [data-p]'); return p ? p.dataset.p : ''`);
await ev(`__bk.openProf(${JSON.stringify('')} || document.querySelector('#pg-body [data-p]').dataset.p); return 1`); await sleep(900);
say('档案', who, await ev(`const s = document.querySelector('#prof'); return s && !s.hidden ? (s.querySelector('.pf-traits') ? '卡片' : '旧的') + ' ' + s.innerText.length + '字' : '没开'`));
await shot('8_档案');
// 档案里的剧透开关：关着看不到下场，点开以后看得到，再关上
const fateVis = `const f = document.querySelector('#prof .pf-fate'); return f ? getComputedStyle(f.closest('.spoil') || f).display !== 'none' : 'none'`;
say('档案里的下场 关着', await ev(fateVis));
await ev(`document.querySelector('#prof .spl').click(); return 1`); await sleep(500);
say('档案里点了剧透', await ev(fateVis), '整本开了', await ev(`return __bk.wb.spoil`), '档案还开着', await ev(`return !document.querySelector('#prof').hidden`));
await ev(`document.querySelector('#prof .spl').scrollIntoView({block:'start'}); return 1`); await sleep(300);
await shot('9_档案剧透');
await ev(`document.querySelector('#prof .spl').click(); return 1`); await sleep(400);
say('再点一下', await ev(fateVis));
say(errs.length ? '有报错：\n' + errs.join('\n') : '没有报错');
ws.close();
