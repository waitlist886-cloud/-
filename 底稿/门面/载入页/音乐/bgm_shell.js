
/* ---------- 背景音乐播放器和交互音效（11-26 夜起；11-27 换上 Suno 的八首、做成播放器）。源稿在 底稿/门面/载入页/音乐/bgm_shell.js，接在 shell.js 末尾 ----------
   一、曲子：data/bgm.json 的 scenes 是场景到文件，tracks 是每个文件的曲名、循环点 [X, N]（make_bgm.py 量好写进去的），labels 是场景给人看的名字。
       用 WebAudio 放：整首取下来解成缓冲，AudioBufferSourceNode 设 loop、loopStart=X、loopEnd=N，样本级接上，一圈一圈没有空隙；
       文件末尾那几秒已经跟前奏交叉好了（make_bgm.py），跳回去的地方两边是同一段声音。音量、淡入淡出用 GainNode，iOS 上也调得动。
       解好的缓冲至多留两首（一首三分钟解开有六七十 MB），别的丢掉，回头要再取（浏览器有缓存）。
       曲子放在图床另一段（front_bgm），地址照 data/bgm_cdn.json 的提交号换；本地没有这一份，照相对地址取。取不到换下一个镜像。
       没有 WebAudio、或者解不开的：退回一首一个 <audio>（放到 N 秒拨回 X 秒），音量在 iOS 上改不了。
   二、换场景：照外壳的状态每 0.4 秒看一回（Shell.state 的 cur、build，body 上的 sh-libon），进哪一页换哪一首，两秒交叉淡入淡出；
       新的那一首还没取好的时候旧的接着放。每一首记住自己放到哪儿（离开那一刻），回来从那里接着放。
   三、玩家点了暂停就一直停着：换场景、离开再回来都不自动放，场景照样跟着换（播放器上曲名跟着变），只有玩家自己点播放才响，放的是当前场景那一首。
       页面切到后台时整个停（不算玩家暂停），回来接着放。
   四、起声要用户的手势：载入页开门那一下（window.__gateOpened，点了跳过也算）；没有载入页的（?nogate、减少动态效果、载入页出错拆掉了），第一次点任何地方。
       手势里 resume AudioContext，再放一个空缓冲（iOS 要这一下才算解开）。死之神殿那一首在第零层齐了以后就先取、先解，开门那一下就有。
   五、右上角（大图书馆钮底下）一个小喇叭，点开是播放器：曲名（英文原名）、底下一行小字是场景，播放/暂停，进度条（拖得动），音量。点外面收起。
       还没起声的时候点喇叭也算起声。只给我们测用的状态：地址带 ?bgmtest，或者三秒里连点喇叭五下，屏幕右下出一行小字。?bgmel 强制走 <audio> 那一路。
       window.__bgm：state() 看状态，unlock() 手动起声，scene(名) 手动换场景，play()/pause()/seek(秒)/vol(0..1)（本地验用）。
   六、交互音效：data/sfx.json 里的十几个短声（assets/sfx/），也解成缓冲，跟曲子共用一个 AudioContext 和音量。外壳里的事直接调 window.__sfx(名)；
       书在嵌套的 iframe 里，书里调 SFX(名)（装书时塞进书里的那一小段给的），发消息给外壳放。音效有一个总开关 sfx_off（11-27 先关着），
       播放器里不放音效的开关。window.__sfxLog 记每一声放的时刻（本地录带声的视频用）。 */
(function () {
  'use strict';
  const Q = new URLSearchParams(location.search);
  const MIR = ['https://cdn.jsdelivr.net/', 'https://fastly.jsdelivr.net/', 'https://gcore.jsdelivr.net/', 'https://testingcf.jsdelivr.net/', 'https://quantil.jsdelivr.net/'];
  const abs = (u) => { try { return new URL(window.A ? window.A(u) : u, document.baseURI).href; } catch (e) { return u; } };
  let CONF = null, CDN = null, unlocked = false, by = '', userPaused = false, scene = 'table', want = 'table', playErr = '', playOk = false, showSt = Q.has('bgmtest'), userVol = 1;
  let confOk;
  const confReady = new Promise((r) => { confOk = r; });
  Promise.all([
    fetch(abs('data/bgm.json')).then((r) => r.json()).catch(() => ({ scenes: {}, off: true })),
    fetch(abs('data/bgm_cdn.json')).then((r) => (r.ok ? r.json() : null)).catch(() => null),
  ]).then(([j, c]) => { CONF = j; CDN = c; paint(); confOk(); });
  const OFF = () => !!(CONF && CONF.off) && !Q.has('bgmtest');      // 曲目表 off:true 时整个不放、喇叭不露；地址带 ?bgmtest 照旧能测
  const VOL = () => (CONF && +CONF.vol) || 0.5, FADE = () => ((CONF && +CONF.fade) || 2) * 1000;
  const relOf = (s) => { const m = (CONF && CONF.scenes) || {}; return m[s] || m.table || ''; };
  const infoOf = (rel) => (CONF && CONF.tracks && CONF.tracks[rel]) || {};
  const labelOf = (s) => (CONF && CONF.labels && CONF.labels[s]) || s;
  const loopOf = (rel) => { const L = infoOf(rel).loop; return L && L.length === 2 && +L[1] > +L[0] ? [+L[0], +L[1]] : null; };
  /* 曲子在图床的 front_bgm 那一段：外壳那一段的地址换成 bgm_cdn.json 里的提交号 */
  const urlOf = (rel) => {
    const u = abs(rel), c = CDN && CDN.commit;
    if (!c || !/^[0-9a-f]{40}$/.test(c)) return u;
    const m = u.match(/^(.*\/gh\/[^/]+\/[^/@]+)@[0-9a-f]{40}\/(.*)$/);
    return m ? m[1] + '@' + c + '/' + m[2] : u;
  };
  const POS = {};      // 每一首放到哪儿了（秒）
  const wrap = (rel, x) => { const L = loopOf(rel); return L && x >= L[1] ? L[0] + ((x - L[0]) % (L[1] - L[0])) : Math.max(0, x); };

  /* ---------- AudioContext（曲子、音效共用） ---------- */
  let AC = null, acErr = '', acOpened = false, master = null;
  function ensureAC() {
    if (!AC) {
      const C = window.AudioContext || window.webkitAudioContext;
      if (C) { try { AC = new C(); master = AC.createGain(); master.gain.value = userVol; master.connect(AC.destination); } catch (e) { acErr = e.name || String(e); AC = null; } }
    }
    return AC;
  }
  function acUnlock() {      // 一定要在手势里调：AudioContext 在这一下 resume，iOS 上再放一个空的缓冲才算解开
    try {
      if (!ensureAC()) return;
      if (AC.state === 'suspended') AC.resume();
      const b = AC.createBuffer(1, 1, 22050), s = AC.createBufferSource(); s.buffer = b; s.connect(AC.destination); s.start(0);
    } catch (e) { acErr = e.name || String(e); }
    acOpened = true;
  }
  function decode(ab) { return new Promise((ok, no) => { try { const p = AC.decodeAudioData(ab, ok, no); if (p && p.then) p.then(ok, no); } catch (e) { no(e); } }); }
  function getBuf(u, n) {
    return fetch(u).then((r) => { if (!r.ok) throw new Error(r.status); return r.arrayBuffer(); }).then(decode).catch((e) => {
      for (let i = 0; i < MIR.length; i++) if (u.indexOf(MIR[i]) === 0 && n < MIR.length - 1) return getBuf(MIR[(i + 1) % MIR.length] + u.slice(MIR[i].length), n + 1);
      throw e;
    });
  }
  let elMode = Q.has('bgmel');      // 解不开（内存不够、格式不认）就退回 <audio> 那一路，往后都走那一路
  const WA = () => !elMode && !!ensureAC();

  /* ---------- WebAudio 那一路 ---------- */
  const BUF = new Map();      // 地址 → Promise<AudioBuffer>，至多留两首
  function track(rel) {
    const u = urlOf(rel);
    if (BUF.has(u)) { const p = BUF.get(u); BUF.delete(u); BUF.set(u, p); return p; }
    const p = getBuf(u, 0);
    BUF.set(u, p);
    while (BUF.size > 2) BUF.delete(BUF.keys().next().value);
    p.catch(() => BUF.delete(u));
    return p;
  }
  let node = null, pending = '';      // node：正在放的那一首 {rel, src, g, t0, loop}；pending：在取、取好了要放的那一首
  function startNode(rel, buf, fadeMs, at) {
    const L0 = loopOf(rel), L = L0 && L0[1] <= buf.duration ? L0 : [0, buf.duration];
    const src = AC.createBufferSource(), g = AC.createGain(), t = AC.currentTime;
    at = wrap(rel, at || 0); if (at >= buf.duration) at = L[0];
    src.buffer = buf; src.loop = true; src.loopStart = L[0]; src.loopEnd = L[1];
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(VOL(), t + fadeMs / 1000);
    src.connect(g); g.connect(master); src.start(t, at);
    return { rel, src, g, t0: t - at, loop: L };
  }
  const posOf = (n) => { if (!n || !AC) return 0; const d = AC.currentTime - n.t0, [a, b] = n.loop; return d < b ? d : a + ((d - a) % (b - a)); };
  function stopNode(n, ms) {
    if (!n) return;
    try { const t = AC.currentTime; n.g.gain.cancelScheduledValues(t); n.g.gain.setValueAtTime(n.g.gain.value, t); n.g.gain.linearRampToValueAtTime(0, t + ms / 1000); n.src.stop(t + ms / 1000 + 0.05); } catch (e) {}
  }
  function retire(n, ms) { if (!n) return; POS[n.rel] = posOf(n); stopNode(n, ms); }
  function waPlay(rel, fadeMs) {
    if (node && node.rel === rel) { pending = ''; return; }
    pending = rel;
    track(rel).then((buf) => {
      if (pending !== rel || userPaused || !unlocked) return;      // 取的工夫里又换了场景，或者玩家暂停了
      pending = '';
      const old = node;
      node = startNode(rel, buf, fadeMs, POS[rel] || 0);
      retire(old, FADE());
      playOk = true; playErr = ''; paint();
    }, (e) => {
      playErr = 'decode:' + ((e && e.name) || String(e)); window.__bgmErr = playErr;
      if (pending === rel) { pending = ''; elMode = true; retire(node, 300); node = null; elPlay(rel, fadeMs); }
    });
  }
  function waPause(ms) { pending = ''; retire(node, ms); node = null; }
  function waSeek(rel, x) {
    POS[rel] = wrap(rel, x);
    if (node && node.rel === rel) { const old = node; node = startNode(rel, old.src.buffer, 120, POS[rel]); stopNode(old, 120); }
  }

  /* ---------- <audio> 那一路（退路）：一首一个 ---------- */
  const EM = new Map();
  let elCur = null;
  function elOf(rel) {
    if (EM.has(rel)) return EM.get(rel);
    const a = document.createElement('audio');
    a.preload = 'none'; a.setAttribute('playsinline', ''); a.style.display = 'none'; a.dataset.rel = rel;
    document.body.appendChild(a);
    a.addEventListener('error', () => retry(a));
    a.addEventListener('timeupdate', () => { const L = loopOf(rel); if (L && a.currentTime >= L[1]) a.currentTime = L[0] + (a.currentTime - L[1]); });      // 末尾多拷的那 1.5 秒跟 X 秒以后一样，拨回去听不出
    a.addEventListener('loadedmetadata', () => { if (a.dataset.seek) { try { a.currentTime = +a.dataset.seek; } catch (e) {} delete a.dataset.seek; } });
    a.src = urlOf(rel);
    EM.set(rel, a);
    return a;
  }
  function retry(a) {      // 镜像取不到换下一个
    const s = a.currentSrc || a.src, n = +(a.dataset.mr || 0);
    if (n >= MIR.length - 1) { playErr = 'MediaError' + (a.error ? a.error.code : ''); window.__bgmErr = playErr; return; }
    for (let i = 0; i < MIR.length; i++) if (s.indexOf(MIR[i]) === 0) { const t = a.currentTime; a.dataset.mr = n + 1; a.dataset.seek = t; a.src = MIR[(i + 1) % MIR.length] + s.slice(MIR[i].length); if (a === elCur && unlocked && !userPaused) play(a); return; }
    playErr = 'MediaError' + (a.error ? a.error.code : ''); window.__bgmErr = playErr;
  }
  function play(a) {
    let p;
    try { p = a.play(); } catch (e) { playErr = e.name || String(e); window.__bgmErr = playErr; return; }
    if (p && p.then) p.then(() => { playOk = true; playErr = ''; paint(); }, (e) => { playOk = false; playErr = (e && e.name) || String(e); window.__bgmErr = playErr; if (playErr === 'NotAllowedError' && a === elCur) { unlocked = false; by = ''; paint(); } });      // 浏览器不许：算没起声，下一回点页面再起
  }
  const fades = new Map();
  function fadeTo(a, v, ms, done) {      // iOS 上 <audio> 的 volume 改不了，那边就是直接放出来
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
  function elSet(a, x) { if (a.readyState >= 1) { try { a.currentTime = x; } catch (e) {} } else a.dataset.seek = x; }
  function elPlay(rel, fadeMs) {
    const a = elOf(rel), prev = elCur;
    if (prev === a && !a.paused) return;
    elCur = a;
    if (POS[rel] != null && Math.abs((a.currentTime || 0) - POS[rel]) > 0.5) elSet(a, POS[rel]);
    try { a.volume = 0; } catch (e) {}
    play(a);
    fadeTo(a, VOL() * userVol, fadeMs);
    if (prev && prev !== a) { POS[prev.dataset.rel] = prev.currentTime; fadeTo(prev, 0, FADE(), () => { if (prev !== elCur) prev.pause(); }); }
  }
  function elPause(ms) { const a = elCur; if (!a) return; POS[a.dataset.rel] = a.currentTime; fadeTo(a, 0, ms, () => { if (userPaused || a !== elCur) a.pause(); }); }
  function elSeek(rel, x) { POS[rel] = wrap(rel, x); const a = EM.get(rel); if (a) elSet(a, POS[rel]); }

  /* ---------- 放、停、换 ---------- */
  function playScene(s, fadeMs) { const rel = relOf(s); if (!rel) return; if (WA()) waPlay(rel, fadeMs); else elPlay(rel, fadeMs); }
  function setScene(s) {
    if (s === scene) return;
    scene = s;
    if (unlocked && !userPaused) playScene(s, FADE());
    paint();
  }
  function doPause() { userPaused = true; if (WA()) waPause(500); else elPause(500); paint(); }
  function doPlay() { userPaused = false; if (!unlocked) { unlock('点了播放'); return; } acUnlock(); playScene(scene, 900); paint(); }
  function doSeek(x) { const rel = relOf(scene); if (!rel) return; if (WA()) waSeek(rel, x); else elSeek(rel, x); paint(); }
  function doVol(v) {
    userVol = Math.max(0, Math.min(1, v));
    if (master) { try { const t = AC.currentTime; master.gain.cancelScheduledValues(t); master.gain.setValueAtTime(master.gain.value, t); master.gain.linearRampToValueAtTime(userVol, t + 0.08); } catch (e) { master.gain.value = userVol; } }
    if (elCur && !fades.has(elCur)) { try { elCur.volume = VOL() * userVol; } catch (e) {} }
    paint();
  }
  function unlock(how) {
    acUnlock();
    if (!SFX_OFF()) loadSfx();
    if (unlocked || OFF() || !CONF) { paint(); return; }
    unlocked = true; by = how || '';
    scene = want;
    if (!WA()) for (const s of Object.keys((CONF && CONF.scenes) || {})) { const a = elOf(relOf(s)); if (relOf(s) !== relOf(scene)) { try { a.muted = true; const p = a.play(); const stop = () => { a.pause(); a.muted = false; }; if (p && p.then) p.then(stop, stop); else stop(); } catch (e) {} } }      // iOS：每个 <audio> 都在手势里放一下
    if (!userPaused) playScene(scene, 1500);
    paint();
  }
  /* 第零层齐了：先开一个（还静着的）AudioContext，把开门要放的那一首和音效取好、解好，手势里再 resume */
  (window.__gateL0 || Promise.resolve()).then(() => confReady).then(() => setTimeout(() => {
    if (!OFF() && WA()) { const r = relOf(want); if (r) track(r).catch(() => {}); }
    if (!SFX_OFF()) { ensureAC(); loadSfx(); }
  }, 300));
  /* 页面切到后台：整个停（不算玩家暂停）；回来接着放 */
  document.addEventListener('visibilitychange', () => {
    if (AC && acOpened) { try { if (document.hidden) AC.suspend(); else AC.resume(); } catch (e) {} }
    if (elCur && unlocked && !WA()) { if (document.hidden) elCur.pause(); else if (!userPaused) play(elCur); }
  });

  /* ---------- 交互音效 ---------- */
  let SCONF = null, sfxLoading = false, sfxErr = '';
  const SB = {};
  window.__sfxLog = [];
  fetch(abs('data/sfx.json')).then((r) => r.json()).then((j) => { SCONF = j; paint(); if (AC && acOpened) loadSfx(); }).catch(() => { SCONF = { sfx_off: true, sounds: {} }; });
  const SFX_OFF = () => !SCONF || !!SCONF.sfx_off;
  function loadSfx() {
    if (sfxLoading || !ensureAC() || !SCONF || SFX_OFF()) return;
    sfxLoading = true;
    const L = Object.entries(SCONF.sounds || {});
    let i = 0;
    const one = () => { if (i >= L.length) return; const [k, v] = L[i++]; getBuf(abs(v.src), 0).then((b) => { SB[k] = b; }, (e) => { sfxErr = (e && e.name) || String(e); }).then(one); };
    one(); one(); one();
  }
  const lastAt = {};
  window.__sfx = function (n, k) {      // k：这一回再乘的轻重（牌桌后三张翻牌用），不给是 1
    if (!AC || !acOpened || SFX_OFF() || !SB[n]) return;
    const now = performance.now(); if (now - (lastAt[n] || -1e9) < 100) return; lastAt[n] = now;      // 同一声一下子来几回只响一声
    try {
      if (AC.state === 'suspended') AC.resume();
      const v = SCONF.sounds[n] || {}, src = AC.createBufferSource(), g = AC.createGain();
      src.buffer = SB[n]; k = k == null ? 1 : +k; g.gain.value = (+SCONF.vol || 0.35) * (v.gain == null ? 1 : +v.gain) * k;
      src.connect(g); g.connect(master); src.start(0);
      window.__sfxLog.push({ n, k, at: performance.timeOrigin + performance.now() });
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
  setInterval(() => { want = sceneNow(); if (want !== scene) setScene(want); else if (showSt || !panel.hidden) paint(); }, 400);
  /* 起声的手势 */
  const prevOpened = window.__gateOpened;
  window.__gateOpened = function () { try { if (typeof prevOpened === 'function') prevOpened(); } catch (e) {} unlock('开门'); window.__sfx('door'); };
  const anyTap = (e) => { if ((unlocked || OFF()) && acOpened) return; if (document.getElementById('gate')) return; if (e && e.target && e.target.closest && e.target.closest('#bgmBtn,#bgmPanel')) return; unlock('点了页面'); };
  ['click', 'touchend', 'keydown'].forEach((ev) => document.addEventListener(ev, anyTap, true));

  /* ---------- 小喇叭和播放器 ---------- */
  const btn = document.createElement('button');
  btn.id = 'bgmBtn'; btn.type = 'button'; btn.setAttribute('aria-label', '背景音乐'); btn.setAttribute('aria-expanded', 'false');
  const panel = document.createElement('div');
  panel.id = 'bgmPanel'; panel.hidden = true; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', '背景音乐');
  panel.innerHTML = '<div class="bp-hd"><b class="bp-ti"></b><i class="bp-sc"></i></div>' +
    '<div class="bp-row"><button type="button" class="bp-pp" aria-label="暂停"></button><span class="bp-tm bp-t0">0:00</span><input class="bp-seek" type="range" min="0" max="1000" step="1" value="0" aria-label="进度"><span class="bp-tm bp-t1">0:00</span></div>' +
    '<div class="bp-row bp-vr"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9.5h3.2L12 5.6v12.8l-4.8-3.9H4z" fill="currentColor"/><path d="M15.2 9.1a4 4 0 0 1 0 5.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg><input class="bp-vol" type="range" min="0" max="100" step="1" value="100" aria-label="音量"></div>';
  const st = document.createElement('div'); st.id = 'bgmSt';
  document.body.appendChild(btn); document.body.appendChild(panel); document.body.appendChild(st);
  const $p = (s) => panel.querySelector(s);
  const ppB = $p('.bp-pp'), seekI = $p('.bp-seek'), volI = $p('.bp-vol');
  const ICON = (on) => '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9.5h3.2L12 5.6v12.8l-4.8-3.9H4z" fill="currentColor"/>' +
    (on ? '<path d="M15.2 9.1a4 4 0 0 1 0 5.8M17.6 6.9a7.2 7.2 0 0 1 0 10.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>' : '<path d="M15.5 8.5l5 7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>') + '</svg>';
  const PP = (playing) => playing ? '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6.5" y="5" width="3.6" height="14" rx="1" fill="currentColor"/><rect x="13.9" y="5" width="3.6" height="14" rx="1" fill="currentColor"/></svg>'
    : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.2v13.6a.8.8 0 0 0 1.2.7l10.6-6.8a.8.8 0 0 0 0-1.4L9.2 4.5a.8.8 0 0 0-1.2.7z" fill="currentColor"/></svg>';
  const mmss = (x) => { x = Math.max(0, Math.floor(x || 0)); return Math.floor(x / 60) + ':' + String(x % 60).padStart(2, '0'); };
  const showPanel = (on) => { panel.hidden = !on; btn.setAttribute('aria-expanded', on ? 'true' : 'false'); btn.classList.toggle('open', on); paint(); };
  let taps = [];
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    const t = performance.now(); taps = taps.filter((x) => t - x < 3000); taps.push(t);
    if (taps.length >= 5) { showSt = !showSt; taps = []; }
    if (!unlocked && !OFF()) unlock('点了喇叭'); else acUnlock();
    showPanel(panel.hidden);
  });
  ppB.addEventListener('click', (e) => { e.stopPropagation(); if (playingNow()) doPause(); else doPlay(); });
  let dragging = false;
  const durOf = () => { const r = relOf(scene), L = loopOf(r); return L ? L[1] : WA() && node && node.rel === r ? node.src.buffer.duration : elCur && elCur.dataset.rel === r && isFinite(elCur.duration) ? elCur.duration : 0; };
  seekI.addEventListener('input', () => { dragging = true; $p('.bp-t0').textContent = mmss(durOf() * seekI.value / 1000); });
  seekI.addEventListener('change', () => { dragging = false; const d = durOf(); if (d) doSeek(d * seekI.value / 1000); });
  volI.addEventListener('input', () => doVol(volI.value / 100));
  ['pointerdown', 'touchstart'].forEach((ev) => document.addEventListener(ev, (e) => { if (panel.hidden) return; const t = e.target; if (t && t.closest && t.closest('#bgmPanel,#bgmBtn')) return; showPanel(false); }, true));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !panel.hidden) showPanel(false); });
  const posNow = () => { const r = relOf(scene); if (WA()) return node && node.rel === r ? posOf(node) : POS[r] || 0; return elCur && elCur.dataset.rel === r ? elCur.currentTime : POS[r] || 0; };
  const playingNow = () => unlocked && !userPaused && (WA() ? !!(node || pending) : !!(elCur && !elCur.paused));
  function paint() {
    const live = playingNow() || (OFF() && acOpened && !SFX_OFF());
    btn.innerHTML = ICON(live && userVol > 0);
    btn.classList.toggle('off', !live);
    btn.title = '背景音乐' + (userPaused ? '（暂停着）' : '');
    btn.hidden = OFF() && SFX_OFF() && !showSt;      // 背景音乐、音效都关着才不露
    if (!panel.hidden) {
      const r = relOf(scene), info = infoOf(r), d = durOf(), p = posNow();
      $p('.bp-ti').textContent = info.title || '—';
      $p('.bp-sc').textContent = labelOf(scene);
      const on = playingNow();
      ppB.innerHTML = PP(on); ppB.setAttribute('aria-label', on ? '暂停' : '播放'); ppB.classList.toggle('on', on);
      if (!dragging) { seekI.value = d ? Math.round(p / d * 1000) : 0; $p('.bp-t0').textContent = mmss(p); }
      $p('.bp-t1').textContent = mmss(d);
      seekI.style.setProperty('--p', (seekI.value / 10) + '%'); volI.style.setProperty('--p', Math.round(userVol * 100) + '%');
      if (document.activeElement !== volI) volI.value = Math.round(userVol * 100);
    }
    st.hidden = !showSt;
    if (showSt) {
      st.textContent = '起声' + (unlocked ? '：' + by : '：还没') + ' · ' + (WA() ? 'WebAudio ' + (AC ? AC.state : '') : '<audio>') + ' · 放：' + (playOk ? '成了' : playErr ? '没成 ' + playErr : unlocked ? '等着' : '—') +
        ' · ' + (playingNow() ? '在放' : userPaused ? '玩家暂停' : '停着') + ' ' + posNow().toFixed(1) + '秒 · 场景 ' + scene + ' · ' + (relOf(scene).split('/').slice(-1)[0] || '—') +
        ' · 音量 ' + userVol.toFixed(2) + ' · 缓冲 ' + BUF.size + (CDN && CDN.commit ? ' · bgm@' + CDN.commit.slice(0, 7) : '') + (acErr ? ' · ' + acErr : '') +
        ' ｜ 音效：' + (SFX_OFF() ? '关着' : !AC ? '还没开' : AC.state + ' ' + Object.keys(SB).length + '/' + Object.keys((SCONF && SCONF.sounds) || {}).length + (sfxErr ? ' ' + sfxErr : ''));
    }
  }
  setInterval(() => { if (!panel.hidden) paint(); }, 250);
  paint();
  window.__bgm = {
    state: () => ({ unlocked, by, userPaused, scene, want, playOk, playErr, mode: WA() ? 'webaudio' : 'audio', ac: AC ? AC.state : '', playing: playingNow(), t: posNow(), dur: durOf(), vol: userVol,
      rel: relOf(scene), node: WA() ? (node ? node.rel : '') : elCur && !elCur.paused ? elCur.dataset.rel : '', gain: node ? node.g.gain.value : elCur ? elCur.volume : 0, pos: Object.assign({}, POS), bufs: BUF.size, panel: !panel.hidden,
      sfx: { ac: AC ? AC.state : '', n: Object.keys(SB).length, opened: acOpened, off: SFX_OFF(), err: sfxErr } }),
    unlock: () => unlock('脚本'), scene: (s) => { want = s; setScene(s); }, play: doPlay, pause: doPause, seek: doSeek, vol: doVol, panel: showPanel,
  };
})();
