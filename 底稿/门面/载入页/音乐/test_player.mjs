// 背景音乐播放器本地验（11-27）：无头 Chrome（要加 --mute-audio 起）走一遍，看每一步 __bgm.state()，截播放器展开的图（电脑、手机）。
//   node 底稿/门面/载入页/音乐/test_player.mjs <截图目录> [pc|mobile|el|seam]      （本地 front-cors 8773 起着，CDP_PORT 默认 9351；el 那一路要能拖进度，本地服务得认 Range，HTTP_PORT 指到认 Range 的那一个）
// THIN=thin.html 走图床上推好的那一版（薄壳认指针）。
// pc：开门起声 → 翻月银纪换曲 → 合书回牌桌续播 → 暂停 → 翻纷争纪不自动放 → 回牌桌还停着 → 点播放续播 → 拖到快结尾看接回去 → 大图书馆 → 建档 → 音量 → 点外面收起。
// mobile：手机竖屏开门、点开播放器截图、点外面收起。el：?bgmel 走 <audio> 那一路，开门、换曲、续播。
// seam：页面里把八首 mp3 用 OfflineAudioContext 解开、照 bgm.json 的循环点放过接缝那两秒，量跳回那一下前后的电平和样本跳变。
import fs from 'node:fs';
import path from 'node:path';
const DIR = process.argv[2], MODE = process.argv[3] || 'pc';
const MOB = MODE === 'mobile';
const W = MOB ? 390 : 1280, H = MOB ? 844 : 800, PORT = +(process.env.CDP_PORT || 9351);
fs.mkdirSync(DIR, { recursive: true });
const tab = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(tab.webSocketDebuggerUrl); await new Promise((r) => { ws.onopen = r; });
let seq = 0; const pend = new Map(), ctxs = [];
const send = (m, p = {}) => new Promise((r) => { const id = ++seq; pend.set(id, r); ws.send(JSON.stringify({ id, method: m, params: p })); });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); return; }
  if (m.method === 'Runtime.executionContextCreated') ctxs.push(m.params.context);
  if (m.method === 'Runtime.executionContextDestroyed') { const i = ctxs.findIndex((x) => x.id === m.params.executionContextId); if (i >= 0) ctxs.splice(i, 1); }
};
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const evIn = async (expr, x) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true, ...(x ? { contextId: x.id } : {}) }); if (r.result && r.result.exceptionDetails) console.log('  !!', JSON.stringify(r.result.exceptionDetails).slice(0, 300)); return r.result && r.result.result ? r.result.result.value : undefined; };
async function where(pred, ms = 30000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) { for (const x of [...ctxs]) { if ((await evIn(`(() => { try { return !!(${pred}); } catch (e) { return false; } })()`, x)) === true) return x; } await sleep(250); }
  return null;
}
const T0 = Date.now();
const log = (...a) => console.log(((Date.now() - T0) / 1000).toFixed(1).padStart(5) + 's', ...a);
async function clickAt(x, y) { for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x, y, button: 'left', clickCount: 1 }); }
async function clickSel(x, sel) { const r = await evIn(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return null; const b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; })()`, x); if (!r) { log('点不到', sel); return; } await clickAt(r[0], r[1]); }
async function shot(name) { const r = await send('Page.captureScreenshot', { format: 'jpeg', quality: 88 }); fs.writeFileSync(path.join(DIR, name), Buffer.from(r.result.data, 'base64')); log('截图', name); }
let bad = 0;
const ok = (cond, what) => { if (!cond) bad++; log((cond ? '  对 ' : '  不对 ') + what); };
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: MOB ? 2 : 1, mobile: MOB });
const qs = MODE === 'el' ? '?gmin=4&bgmtest&bgmel' : '?gmin=4&bgmtest';
await send('Page.navigate', { url: 'http://127.0.0.1:' + (process.env.HTTP_PORT || 8773) + '/' + encodeURIComponent('小样_外壳') + '/' + (process.env.THIN || 'thin_local.html') + qs + '&t=' + Date.now() });
const S = await where('window.__gate && window.__bgm', 30000);
const st = async (tag) => { const o = await evIn('window.__bgm.state()', S); log(tag.padEnd(16), `${o.mode} 起声=${o.unlocked ? o.by : '没'} ${o.playing ? '在放' : o.userPaused ? '玩家暂停' : '停着'} 场景=${o.scene} 在放=${(o.node || '').split('/').pop() || '-'} ${(+o.t).toFixed(1)}/${(+o.dur).toFixed(1)}秒 增益=${(+o.gain).toFixed(2)} 音量=${o.vol} 缓冲=${o.bufs} 错=${o.playErr || '-'}`); return o; };

if (MODE === 'seam') {
  const res = await evIn(`(async () => {
    const C = await (await fetch(A('data/bgm.json'))).json(), out = [];
    for (const [rel, t] of Object.entries(C.tracks)) {
      const ab = await (await fetch(A(rel))).arrayBuffer();
      const oc = new OfflineAudioContext(2, 48000 * 4, 48000);
      const buf = await oc.decodeAudioData(ab);
      const s = oc.createBufferSource(); s.buffer = buf; s.loop = true; s.loopStart = t.loop[0]; s.loopEnd = t.loop[1]; s.connect(oc.destination); s.start(0, t.loop[1] - 2);
      const r = await oc.startRendering(), a = r.getChannelData(0), b = r.getChannelData(1), J = 96000;
      const lv = (i0, i1) => { let e = 0; for (let i = i0; i < i1; i++) e += a[i] * a[i] + b[i] * b[i]; return 10 * Math.log10(e / (2 * (i1 - i0)) + 1e-12); };
      let dj = 0, dmax = 0; for (let i = J - 2; i <= J + 2; i++) dj = Math.max(dj, Math.abs(a[i] - a[i - 1]));
      const ds = []; for (let i = 1; i < a.length; i++) { const d = Math.abs(a[i] - a[i - 1]); ds.push(d); if (Math.abs(i - J) > 50) dmax = Math.max(dmax, d); }
      ds.sort((x, y) => x - y);
      out.push({ f: rel.split('/').pop(), len: +buf.duration.toFixed(2), loop: t.loop, before: +lv(J - 960, J).toFixed(1), after: +lv(J, J + 960).toFixed(1), jump: +dj.toFixed(4), p99: +ds[Math.floor(ds.length * 0.99)].toFixed(4), max: +dmax.toFixed(4), b1: +lv(J - 48000, J).toFixed(1), a1: +lv(J, J + 48000).toFixed(1) });
    }
    return out; })()`, S);
  for (const r of res) log(`${r.f.padEnd(12)} 解开 ${r.len}s 循环 ${r.loop[0]}→${r.loop[1]}  跳回前 20ms ${r.before} dB 后 ${r.after} dB（前 1 秒 ${r.b1} 后 1 秒 ${r.a1}）  跳那一下相邻样本差 ${r.jump}（这两秒里 99% 的相邻差在 ${r.p99} 以下，最大 ${r.max}）`);
  fs.writeFileSync(path.join(DIR, 'seam.json'), JSON.stringify(res, null, 1));
  await send('Page.close').catch(() => {}); process.exit(0);
}

for (let i = 0; i < 160; i++) { if ((await evIn('__gate.state().phase', S)) >= 4) break; await sleep(250); }
await sleep(600);
await st('开门以前');
await clickSel(S, '#gate .g-door');
await sleep(4000);
let o = await st('开门以后');
ok(o.unlocked && o.playing && /gate\.mp3$/.test(o.node), '开门起声，放的是死之神殿那一首');
if (MOB) {
  for (let i = 0; i < 80; i++) { if ((await evIn('window.__tb && __tb.stage', S)) === 'choose') break; await sleep(250); }
  await sleep(1200);
  await clickSel(S, '#bgmBtn'); await sleep(900);
  o = await st('点开播放器');
  ok(o.panel, '播放器展开了');
  await shot('播放器_手机_牌桌.jpg');
  await clickSel(S, '#bgmPanel .bp-pp'); await sleep(900); o = await st('点暂停'); ok(o.userPaused && !o.playing, '暂停了');
  await shot('播放器_手机_暂停.jpg');
  await clickAt(120, 600); await sleep(600); o = await st('点外面'); ok(!o.panel, '点外面收起了');
  await clickSel(S, '#bgmBtn'); await sleep(500); await clickSel(S, '#bgmPanel .bp-pp'); await sleep(1500); o = await st('再点播放'); ok(o.playing, '点播放又响了');
  await send('Page.close').catch(() => {}); console.log(bad ? `不对 ${bad} 处` : '都对'); process.exit(bad ? 1 : 0);
}
await sleep(4000);
const g1 = (await st('死之神殿放了八秒')).t;
await evIn('Shell.openBook("moon"); 1', S);
await sleep(1200); o = await st('翻开月银纪 1.2 秒');
await sleep(3000); o = await st('翻开月银纪 4 秒');
ok(o.playing && /moon\.mp3$/.test(o.node) && o.scene === 'moon', '换成月银纪那一首');
ok(o.pos['assets/bgm/gate.mp3'] >= g1, '死之神殿那一首记下了放到哪儿 ' + (o.pos['assets/bgm/gate.mp3'] || 0).toFixed(1));
await sleep(3000);
const m1 = (await st('月银纪放了七秒')).t;
await evIn('Shell.toTable(); 1', S);
await sleep(3500); o = await st('合书回牌桌');
ok(/gate\.mp3$/.test(o.node) && o.t > g1 + 1, '回牌桌接着放，不从头（' + o.t.toFixed(1) + ' 秒，离开时 ' + (o.pos['assets/bgm/gate.mp3'] || 0).toFixed(1) + '）');
await clickSel(S, '#bgmBtn'); await sleep(900);
await shot('播放器_电脑_牌桌.jpg');
await clickSel(S, '#bgmPanel .bp-pp'); await sleep(1200);
o = await st('点暂停'); ok(o.userPaused && !o.playing && !o.node, '暂停了');
const gp = o.t;
await evIn('Shell.openBook("strife"); 1', S); await sleep(4000);
o = await st('暂停着翻纷争纪'); ok(!o.playing && !o.node && o.scene === 'strife', '暂停着进下一页不自动放，场景跟着换');
const title = await evIn('document.querySelector("#bgmPanel .bp-ti").textContent + "｜" + document.querySelector("#bgmPanel .bp-sc").textContent', S);
ok(/Wall of Ash/.test(title), '播放器曲名跟着换：' + title);
await shot('播放器_电脑_暂停着进纷争纪.jpg');
await evIn('Shell.toTable(); 1', S); await sleep(3000);
o = await st('暂停着回牌桌'); ok(!o.playing && o.userPaused, '回牌桌还停着');
await clickSel(S, '#bgmBtn'); await sleep(400);
if (await evIn('document.getElementById("bgmPanel").hidden', S)) { await clickSel(S, '#bgmBtn'); await sleep(400); }
await clickSel(S, '#bgmPanel .bp-pp'); await sleep(2500);
o = await st('点播放'); ok(o.playing && /gate\.mp3$/.test(o.node) && Math.abs(o.t - gp - 2.5) < 2, '点播放从停下的地方接着放（停在 ' + gp.toFixed(1) + '）');
await evIn('__bgm.seek(__bgm.state().dur - 3); 1', S); await sleep(1000);
o = await st('拖到结尾前三秒');
await sleep(4500);
o = await st('过了接缝'); ok(o.playing && o.t > 4 && o.t < 15, '过了 N 秒接回 X 秒往后（' + o.t.toFixed(1) + '）');
await evIn('Library.open(); 1', S); await sleep(4000);
o = await st('大图书馆'); ok(/library\.mp3$/.test(o.node), '大图书馆换曲');
await evIn('Library.close(true); 1', S); await sleep(3000);
o = await st('出大图书馆'); ok(/gate\.mp3$/.test(o.node), '出来换回死之神殿');
await evIn('Shell.openBook("moon"); 1', S);
const B = await where('location.href === "about:srcdoc" && document.title.indexOf("月银纪") >= 0 && document.querySelector("#view")', 30000);
await sleep(2500);
o = await st('再进月银纪'); ok(/moon\.mp3$/.test(o.node) && o.t > m1, '月银纪也接着放（' + o.t.toFixed(1) + '，上回离开 ' + m1.toFixed(1) + ' 往后）');
await evIn(`SHELL.post({ t: 'enter', book: 'maze', era: '迷宫纪', at: 'q6', title: '垂暮的年月', line: '走查', year: '990', ti: '' }); 1`, B); await sleep(5000);
o = await st('进建档'); ok(o.scene === 'build' && /build\.mp3$/.test(o.node), '建档换曲');
await evIn('__bgm.vol(0.4); 1', S); await sleep(400);
o = await st('音量拉到 0.4'); ok(Math.abs(o.vol - 0.4) < 0.01, '音量');
if (await evIn('document.getElementById("bgmPanel").hidden', S)) await clickSel(S, '#bgmBtn'); await sleep(700);
await shot('播放器_电脑_建档.jpg');
await clickAt(200, 600); await sleep(600);
o = await st('点外面'); ok(!o.panel, '点外面收起');
await send('Page.close').catch(() => {});
console.log(bad ? `不对 ${bad} 处` : '都对'); process.exit(bad ? 1 : 0);
