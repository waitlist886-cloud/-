
/* ---------- 背景音乐（11-26 夜，先做底子和探针；曲子往后用 Suno 出的换，地址在 data/bgm.json）。源稿在 底稿/门面/载入页/音乐/bgm_shell.js，接在 shell.js 末尾 ----------
   一、两个 <audio> 轮着用：换场景（翻开哪一本书、合上回牌桌、大图书馆、建档）两秒交叉淡入淡出。场景照外壳的状态每 0.4 秒看一回（Shell.state 的 cur、build，body 上的 sh-libon），不往各处塞调用。
       曲子不预载（preload=none），用到才取；取不到换下一个镜像。
   二、起声要用户的手势：载入页开门那一下（window.__gateOpened，点了跳过也算）；没有载入页的（?nogate、减少动态效果、载入页出错拆掉了），第一次点任何地方。
       iOS 上一个 <audio> 要在手势里亲手 play() 过一回，往后才放得出来，所以起声那一下两个都 play 一下（第二个静音放一下就停）。
   三、右上角（大图书馆钮左边）一个小喇叭：点了静音、再点放出来；没有本地存储，只管这一回打开。还没起声的时候点它就是起声。
   四、只给我们测用的状态：地址带 ?bgmtest，或者三秒里连点喇叭五下，喇叭底下出一行小字（起没起声、play() 成没成、报什么错、放到第几秒）。play() 失败的错误名记在 window.__bgmErr。
   window.__bgm：state() 看状态，unlock() 手动起声，scene(名) 手动换场景（本地验用）。
   五、交互音效（11-26 夜）：data/sfx.json 里的十几个短声（assets/sfx/，本机合的），WebAudio 解码成缓冲，起声那一下在手势里开 AudioContext、一次载好。
       外壳里的事直接调 window.__sfx(名)；书在嵌套的 iframe 里，书里调 SFX(名)（装书时塞进书里的那一小段给的），发消息给外壳放。
       跟小喇叭共用一个开关，静音全静；音效另有一个总开关 sfx_off（背景音乐的 off 管不到它：曲子没到以前音效可以先上）。window.__sfxLog 记每一声放的时刻（本地录带声的视频用）。 */
(function () {
  'use strict';
  const Q = new URLSearchParams(location.search);
  const MIR = ['https://cdn.jsdelivr.net/', 'https://fastly.jsdelivr.net/', 'https://gcore.jsdelivr.net/', 'https://testingcf.jsdelivr.net/', 'https://quantil.jsdelivr.net/'];
  const abs = (u) => { try { return new URL(window.A ? window.A(u) : u, document.baseURI).href; } catch (e) { return u; } };
  let CONF = null, unlocked = false, by = '', muted = false, scene = 'table', want = 'table', playErr = '', playOk = false, showSt = Q.has('bgmtest');
  fetch(abs('data/bgm.json')).then((r) => r.json()).then((j) => { CONF = j; paint(); }).catch(() => { CONF = { scenes: {} }; });
  const OFF = () => !!(CONF && CONF.off) && !Q.has('bgmtest');      // 11-26：曲子没到以前先关着（曲目表 off:true），喇叭也不露；地址带 ?bgmtest 照旧能测
  const VOL = () => (CONF && +CONF.vol) || 0.5, FADE = () => ((CONF && +CONF.fade) || 2) * 1000;
  const SWAP = Q.get('bgmtest') === 'swap';      // 本地验换曲用：同一段音每个场景挂不同的地址尾巴，交叉淡入淡出才走得到
  const urlOf = (s) => { const m = (CONF && CONF.scenes) || {}; return (m[s] || m.table || 'assets/bgm/probe.mp3') + (SWAP ? '#' + s : ''); };
  const mkAudio = () => { const a = document.createElement('audio'); a.preload = 'none'; a.loop = true; a.setAttribute('playsinline', ''); a.style.display = 'none'; document.body.appendChild(a); a.addEventListener('error', () => retry(a)); return a; };
  const A1 = mkAudio(), A2 = mkAudio();
  let cur = A1, curUrl = '';
  function retry(a) {      // 镜像取不到换下一个
    const s = a.currentSrc || a.src, n = +(a.dataset.mr || 0);
    if (n >= MIR.length - 1) { playErr = 'MediaError' + (a.error ? a.error.code : ''); window.__bgmErr = playErr; return; }
    for (let i = 0; i < MIR.length; i++) if (s.indexOf(MIR[i]) === 0) { a.dataset.mr = n + 1; a.src = MIR[(i + 1) % MIR.length] + s.slice(MIR[i].length); if (a === cur && unlocked) play(a); return; }
    playErr = 'MediaError' + (a.error ? a.error.code : ''); window.__bgmErr = playErr;
  }
  function play(a) {
    let p;
    try { p = a.play(); } catch (e) { playErr = e.name || String(e); window.__bgmErr = playErr; return; }
    if (p && p.then) p.then(() => { playOk = true; playErr = ''; }, (e) => { playOk = false; playErr = (e && e.name) || String(e); window.__bgmErr = playErr; if (playErr === 'NotAllowedError' && a === cur) { unlocked = false; by = ''; curUrl = ''; paint(); } });      // 浏览器不许：算没起声，下一回点页面再起
  }
  /* 音量慢慢拉到目标（iOS 上 volume 改不了，那边就是直接放出来） */
  const fades = new Map();
  function fadeTo(a, v, ms, done) {
    const v0 = a.volume, t0 = performance.now(), id = {};
    fades.set(a, id);
    const step = () => {
      if (fades.get(a) !== id) return;
      const k = Math.min(1, (performance.now() - t0) / Math.max(1, ms));
      try { a.volume = Math.max(0, Math.min(1, v0 + (v - v0) * k)); } catch (e) {}
      if (k < 1) requestAnimationFrame(step); else { fades.delete(a); if (done) done(); }
    };
    requestAnimationFrame(step);
  }
  function switchTo(s, first) {
    scene = s;
    const u = abs(urlOf(s));
    if (u === curUrl) return;
    const next = first ? cur : (cur === A1 ? A2 : A1), prev = first ? null : cur;
    curUrl = u; cur = next;
    next.dataset.mr = 0;
    if (next.src !== u) next.src = u;
    next.muted = muted; try { next.volume = 0; } catch (e) {}
    play(next);
    fadeTo(next, VOL(), first ? 1500 : FADE());
    if (prev) fadeTo(prev, 0, FADE(), () => { if (prev !== cur) prev.pause(); });
  }
  function unlock(how) {
    sfxUnlock();
    if (unlocked || OFF()) { paint(); return; }
    unlocked = true; by = how || '';
    const other = cur === A1 ? A2 : A1;
    switchTo(want, true);
    try { other.muted = true; other.src = cur.src; const p = other.play(); const stop = () => { other.pause(); other.muted = muted; }; if (p && p.then) p.then(stop, stop); else stop(); } catch (e) {}      // iOS：第二个也在手势里放一下
    paint();
  }
  /* ---------- 交互音效 ---------- */
  let AC = null, SCONF = null, sfxLoading = false, sfxErr = '';
  const SB = {};
  window.__sfxLog = [];
  fetch(abs('data/sfx.json')).then((r) => r.json()).then((j) => { SCONF = j; paint(); if (AC) loadSfx(); }).catch(() => { SCONF = { sfx_off: true, sounds: {} }; });
  const SFX_OFF = () => !SCONF || !!SCONF.sfx_off;
  function ensureAC() { if (!AC) { const C = window.AudioContext || window.webkitAudioContext; if (C) { try { AC = new C(); } catch (e) { sfxErr = e.name || String(e); } } } return AC; }
  /* 门轴那一声要在开门那一下就有：第零层齐了就先开一个（还静着的）AudioContext 把音效解好，手势里再 resume */
  (window.__gateL0 || Promise.resolve()).then(() => setTimeout(() => { if (SCONF && SFX_OFF()) return; ensureAC(); loadSfx(); }, 300));
  function sfxUnlock() {      // 一定要在手势里调：AudioContext 在这一下 resume，iOS 上再放一个空的缓冲才算解开
    if (SFX_OFF() && SCONF) return;
    try {
      if (!ensureAC()) return;
      if (AC.state === 'suspended') AC.resume();
      const b = AC.createBuffer(1, 1, 22050), s = AC.createBufferSource(); s.buffer = b; s.connect(AC.destination); s.start(0);
    } catch (e) { sfxErr = e.name || String(e); }
    sfxOpened = true;
    loadSfx();
  }
  function decode(ab) { return new Promise((ok, no) => { try { const p = AC.decodeAudioData(ab, ok, no); if (p && p.then) p.then(ok, no); } catch (e) { no(e); } }); }
  function getBuf(u, n) {
    return fetch(u).then((r) => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); }).then(decode).catch((e) => {
      for (let i = 0; i < MIR.length; i++) if (u.indexOf(MIR[i]) === 0 && n < MIR.length - 1) return getBuf(MIR[(i + 1) % MIR.length] + u.slice(MIR[i].length), n + 1);
      throw e;
    });
  }
  function loadSfx() {
    if (sfxLoading || !AC || !SCONF || SFX_OFF()) return;
    sfxLoading = true;
    const L = Object.entries(SCONF.sounds || {});
    let i = 0;
    const one = () => { if (i >= L.length) return; const [k, v] = L[i++]; getBuf(abs(v.src), 0).then((b) => { SB[k] = b; }, (e) => { sfxErr = (e && e.name) || String(e); }).then(one); };
    one(); one(); one();
  }
  const lastAt = {};
  window.__sfx = function (n) {
    if (!AC || !sfxOpened || muted || SFX_OFF() || !SB[n]) return;
    const now = performance.now(); if (now - (lastAt[n] || -1e9) < 150) return; lastAt[n] = now;      // 同一声一下子来几回（三叠命星一起发）只响一声
    try {
      if (AC.state === 'suspended') AC.resume();
      const v = SCONF.sounds[n] || {}, src = AC.createBufferSource(), g = AC.createGain();
      src.buffer = SB[n]; g.gain.value = (+SCONF.vol || 0.35) * (v.gain == null ? 1 : +v.gain);
      src.connect(g); g.connect(AC.destination); src.start(0);
      window.__sfxLog.push({ n, at: performance.timeOrigin + performance.now() });
    } catch (e) { sfxErr = e.name || String(e); }
  };
  /* 书那一格里的事：书发 {aldran:1, t:'sfx', n} 上来 */
  addEventListener('message', (e) => { const m = e.data; if (m && m.aldran === 1 && m.t === 'sfx' && typeof m.n === 'string') window.__sfx(m.n); });
  /* 场景：照外壳的状态看 */
  const sceneNow = () => {
    if (document.getElementById('gate')) return 'table';
    if (document.body.classList.contains('sh-libon')) return 'library';
    const st = window.Shell && window.Shell.state;
    if (st && st.build) return 'build';
    if (st && st.cur && st.cur !== 'old') return st.cur;
    return 'table';
  };
  setInterval(() => { want = sceneNow(); if (unlocked && want !== scene) switchTo(want); if (showSt) paint(); }, 400);
  /* 起声的手势 */
  const prevOpened = window.__gateOpened;
  window.__gateOpened = function () { try { if (typeof prevOpened === 'function') prevOpened(); } catch (e) {} unlock('开门'); window.__sfx('door'); };
  let sfxOpened = false;
  const anyTap = () => { if ((unlocked || OFF()) && sfxOpened) return; if (document.getElementById('gate')) return; unlock('点了页面'); };
  ['click', 'touchend', 'keydown'].forEach((ev) => document.addEventListener(ev, anyTap, true));
  /* 小喇叭 */
  const btn = document.createElement('button');
  btn.id = 'bgmBtn'; btn.type = 'button'; btn.setAttribute('aria-label', '背景音乐');
  const st = document.createElement('div'); st.id = 'bgmSt';
  document.body.appendChild(btn); document.body.appendChild(st);
  const ICON = (on) => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9.5h3.2L12 5.6v12.8l-4.8-3.9H4z" fill="currentColor"/>' +
    (on ? '<path d="M15.2 9.1a4 4 0 0 1 0 5.8M17.6 6.9a7.2 7.2 0 0 1 0 10.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>' : '<path d="M15.5 8.5l5 7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>') + '</svg>';
  let taps = [];
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const t = performance.now(); taps = taps.filter((x) => t - x < 3000); taps.push(t);
    if (taps.length >= 5) { showSt = !showSt; taps = []; }
    if (!unlocked && !OFF()) { muted = false; unlock('点了喇叭'); return; }
    sfxUnlock();
    muted = !muted; A1.muted = muted; A2.muted = muted;
    if (!muted && cur.paused) play(cur);
    paint();
  });
  function paint() {
    const live = (unlocked || (OFF() && sfxOpened)) && !muted;
    btn.innerHTML = ICON(live);
    btn.classList.toggle('off', !live);
    btn.title = muted ? '声音：静音（点一下放出来）' : live ? '声音：开（点一下静音）' : '点一下放声音';
    st.hidden = !showSt;
    btn.hidden = OFF() && SFX_OFF() && !showSt;      // 背景音乐、音效都关着才不露
    if (showSt) {
      const a = cur;
      st.textContent = '起声' + (unlocked ? '：' + by : '：还没') + ' · play()：' + (playOk ? '成了' : playErr ? '没成 ' + playErr : unlocked ? '等着' : '—') +
        ' · ' + (a.paused ? '停着' : '在放') + ' ' + (a.currentTime || 0).toFixed(1) + '秒' + (muted ? ' · 静音' : '') + ' · 场景 ' + scene + ' · 音量 ' + (+a.volume).toFixed(2) +
        ' · ' + (curUrl ? curUrl.split('/').slice(-1)[0] : '—') + (+a.dataset.mr > 0 ? ' · 换过镜像' : '') +
        ' ｜ 音效：' + (SFX_OFF() ? '关着' : !AC ? '还没开' : AC.state + ' ' + Object.keys(SB).length + '/' + Object.keys((SCONF && SCONF.sounds) || {}).length + (sfxErr ? ' ' + sfxErr : ''));
    }
  }
  paint();
  window.__bgm = { state: () => ({ unlocked, by, muted, scene, want, playOk, playErr, paused: cur.paused, t: cur.currentTime, vol: cur.volume, src: curUrl, sfx: { ac: AC ? AC.state : '', n: Object.keys(SB).length, opened: sfxOpened, off: SFX_OFF(), err: sfxErr }, other: { paused: (cur === A1 ? A2 : A1).paused, vol: (cur === A1 ? A2 : A1).volume } }), unlock: () => unlock('脚本'), scene: (s) => { want = s; if (unlocked) switchTo(s); } };
})();
