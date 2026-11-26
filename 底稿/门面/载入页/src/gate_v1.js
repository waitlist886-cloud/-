/* 载入页（11-26，美化第四轮方向稿第三节第 5 小节）：魂灵往那扇门去的路。外壳那一页最前头，紧跟着第一拍的那几层（gate0.html）。
   薄壳那一截只画到第一拍（星空、灰雾、正中一团火），外壳接手以后：
   二、雾退开，身后（过去）和前方（往后）两层碎影淡进来，同一块在完好和破败之间闪；
   三、碎影一片一片剥落、飞到火的脚下落成路石，载入多少路铺多少，火顺着路往前走，镜头往前推；路边五处火对五纪，那一本书的页面和开书数据载好了才亮；
   四、路铺到尽头，雾里立起两扇门，门缝漏光，浮出“推开门扉”；第零层（外壳的页面、脚本、样式、牌桌的图、五张牌面）齐了门才亮，第一层（五本书）在后台接着载；
   五、点门（或者右下角跳过）：门往里推开，千千万万粒小火涌出来，连成一整片白，白退下去牌桌在那里。推开那一下调 window.__gateOpened()（往后放音乐用）。
   跟外壳别的部分怎么接：window.__g0(名) 是 index.html 里各个脚本、样式 onload 报到用的；window.__gateBook(书, 载到没有) 是 shell.js 的预载报的；
   window.__gateL0 在第零层齐了的时候兑现（shell.js 等它再开始预载五本书，免得跟门口要的东西抢带宽）；window.__gateHold 在白退下去那一刻兑现（牌桌这时候才开场）。
   下面 __X__ 几处是 tools/build_gate.py 填的（传说那几句、第零层的单子和大小、图的单子）。 */
(function () {
  'use strict';
  var G = document.getElementById('gate');
  var holdRes, l0Res;
  window.__gateHold = new Promise(function (r) { holdRes = r; });
  window.__gateL0 = new Promise(function (r) { l0Res = r; });
  if (!G) { holdRes(); l0Res(); return; }
  var now = function () { return performance.now(); };
  var T0 = typeof window.__gateT0 === 'number' && window.__gateT0 <= now() ? window.__gateT0 : now();
  G.style.setProperty('--gt', (T0 - now()).toFixed(0) + 'ms');      // 薄壳那一截的动画接着原来的相位走
  var LORE = __LORE__, ITEMS = __ITEMS__, IM = __IMG__;
  var BOOKS = [['moon', '月银纪'], ['strife', '纷争纪'], ['bronze', '山铜纪'], ['maze', '迷宫纪·前传'], ['now', '迷宫纪·此刻']];
  var MIR = ['https://cdn.jsdelivr.net/', 'https://fastly.jsdelivr.net/', 'https://gcore.jsdelivr.net/', 'https://testingcf.jsdelivr.net/', 'https://quantil.jsdelivr.net/'];
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var Q = new URLSearchParams(location.search);
  var SLOW = Math.max(.1, +Q.get('gslow') || 1);                  // 本地看动作：?gslow=4 整体放慢四倍
  window.__tbPause = true;                                          // 牌桌那一层先不画
  var phase = 1, tP2 = 0, R = 0, placed = 0, lastPlace = 0, books = {}, opened = false, onDoor = false;
  var cam = G.querySelector('#g-cam'), soul = G.querySelector('.g-soul'), fogEl = G.querySelector('.g-fog');
  var mk = function (tag, cls, parent, before) { var e = document.createElement(tag); if (cls) e.className = cls; (parent || cam).insertBefore(e, before || null); return e; };

  /* ---------- 图：取到一层淡进一层；镜像取不到换下一个；都取不到就留着线和光 ---------- */
  var abs = function (u) { try { return new URL(u, document.baseURI).href; } catch (e) { return u; } };
  /* 图都用 <img> 元素挂上去，不走样式里的背景图：沙箱里同一个地址样式再取一回会再下一回，同一页里的 <img> 浏览器认得是同一张 */
  function img(rel, ok, hi) {
    var im = new Image(), src = abs(rel), n = 0;
    im.decoding = 'async'; im.alt = '';
    try { im.fetchPriority = hi ? 'high' : 'low'; } catch (e) {}
    im.onload = function () { im.onload = null; ok(im); };
    im.onerror = function () {
      for (var i = 0; i < MIR.length; i++) if (src.indexOf(MIR[i]) === 0 && n < MIR.length - 1) { n++; src = MIR[(i + 1) % MIR.length] + src.slice(MIR[i].length); im.src = src; return; }
    };
    im.src = src;
  }
  var layer = function (parent, cls, before) { return mk('div', 'g-img ' + cls, parent, before); };
  var rift = G.querySelector('.g-rift');
  var skyI = layer(cam, 'g-skyi', rift);
  var fut = mk('div', 'g-fut', cam, fogEl), futA = layer(fut, 'a'), futB = layer(fut, 'b');
  var past = mk('div', 'g-past', cam, fogEl), pastA = layer(past, 'a'), pastB = layer(past, 'b');
  var door = mk('div', 'g-door', cam, fogEl);
  door.innerHTML = '<div class="glow"></div><svg viewBox="0 0 100 150" preserveAspectRatio="none"><path d="M18 146V58Q18 16 50 4Q82 16 82 58V146" fill="rgba(10,10,18,.55)" stroke="rgba(255,226,180,.8)" stroke-width=".8" vector-effect="non-scaling-stroke"/><path d="M8 150H92M12 146H88" stroke="rgba(255,226,180,.5)" stroke-width=".8" vector-effect="non-scaling-stroke"/></svg><div class="lf"></div><div class="rt"></div><div class="fr"></div><div class="seam"></div>';
  var beam = mk('div', 'g-beam', cam, fogEl);
  var NS = 'http://www.w3.org/2000/svg', road = document.createElementNS(NS, 'svg');
  road.setAttribute('class', 'g-road'); cam.insertBefore(road, fogEl);
  var edgeL = document.createElementNS(NS, 'path'), edgeR = document.createElementNS(NS, 'path');
  road.appendChild(edgeL); road.appendChild(edgeR);
  var stoneBox = mk('div', 'g-stones', cam, fogEl), fireBox = mk('div', 'g-fires', cam, fogEl);
  var mist1 = mk('div', 'g-mist m1', cam, soul), mist2 = mk('div', 'g-mist m2', cam, soul);
  var cv = mk('canvas', 'g-motes', G), white = mk('div', 'g-white', G);
  var push = mk('p', 'g-push', G); push.textContent = '推开门扉';
  var lore = mk('p', 'g-lore', G); lore.textContent = LORE[Math.floor(Math.random() * LORE.length)];
  var skip = mk('button', 'g-skip', G); skip.type = 'button'; skip.textContent = '跳过';
  var fires = BOOKS.map(function (b) { var f = mk('div', 'g-fire', fireBox); f.innerHTML = '<b></b><i></i><span>' + b[1] + '</span>'; return f; });
  var STONE = null;
  function loadArt() {      // 先远景、往后、过去，再门、石头、雾，破败那两张最后
    var bg = function (el) { return function (im) { el.appendChild(im); requestAnimationFrame(function () { el.classList.add('on'); }); }; };
    img(IM.sky, bg(skyI), 1); img(IM.fut_a, bg(futA), 1); img(IM.past_a, bg(pastA), 1);
    var dn = 0, dset = function (cls) { return function (im) { door.querySelector(cls).appendChild(im); if (++dn === 3) door.classList.add('img'); }; };
    img(IM.door_f, dset('.fr'), 1); img(IM.door_l, dset('.lf'), 1); img(IM.door_r, dset('.rt'), 1);
    img(IM.stones, function (im) { STONE = im; for (var i = 0; i < placed; i++) skin(stoneEls[i], i); }, 1);
    img(IM.fog1, bg(mist1)); img(IM.fog2, bg(mist2));
    img(IM.fut_b, bg(futB)); img(IM.past_b, bg(pastB));
  }

  /* ---------- 第零层：外壳的页面、脚本、样式、牌桌的图、五张牌面。图自己取（同一页里同一个地址浏览器只取一回），脚本和样式靠 index.html 里的 onload 报到 ---------- */
  var got = {};
  window.__g0 = function (k) { got[k] = 1; };
  ITEMS.forEach(function (it) { if (it.img) { var im = new Image(); im.onload = im.onerror = function () { got[it.k] = 1; }; im.src = abs(it.k); } });
  var loadedAll = false;
  window.addEventListener('load', function () { loadedAll = true; });
  var W0 = ITEMS.reduce(function (s, it) { return s + it.w; }, 0);
  function p0() {
    if (loadedAll) return 1;
    var s = 0; ITEMS.forEach(function (it) { if (got[it.k]) s += it.w; });
    return W0 ? s / W0 : 1;
  }
  window.__gateBook = function (id, ok) { books[id] = ok === false ? 2 : 1; };

  /* ---------- 版式：竖屏路从下往上，横屏往画面深处。火站在 A，门脚在 B；路面照透视（远处 z 大，宽度、间距照 1/z 缩） ---------- */
  var N = 12, ZF = 3.6, Wd, Hd, wide, A, B, wA, doorH, doorW, sway;
  var FIRE_AT = [1.5, 3.5, 5.5, 7.5, 9.5];
  function L() {
    Wd = innerWidth || document.documentElement.clientWidth || 1; Hd = innerHeight || document.documentElement.clientHeight || 1;
    wide = Wd / Hd >= 1.15;
    A = [Wd / 2, Hd * (wide ? .64 : .56) + 4];
    B = [Wd / 2, Hd * (wide ? .43 : .29)];
    wA = wide ? Math.min(Wd * .085, Hd * .17, 170) : Math.min(Wd * .3, 140);
    doorH = Hd * (wide ? .395 : .255); doorW = doorH * IM.doorAspect;
    sway = wA * .55;
  }
  var zOf = function (t) { return 1 + (ZF - 1) * t; };
  function P(t) {     // 路面上 t（0 近 1 远）那一点：屏上的 x、y、路宽、缩放
    var z = zOf(t), k = (1 / z - 1 / ZF) / (1 - 1 / ZF);
    return { x: A[0] + Math.sin(t * Math.PI * 1.15) * sway / z, y: B[1] + (A[1] - B[1]) * k, w: wA / z, s: 1 / z };
  }
  var tOf = function (i) { return (i + .5) / N; };          // 第 i 块石头在哪
  function layout() {
    L();
    road.setAttribute('width', Wd); road.setAttribute('height', Hd);
    var l = [], r = [];
    for (var i = 0; i <= 40; i++) { var p = P(i / 40 * .995); l.push((p.x - p.w * .56).toFixed(1) + ' ' + p.y.toFixed(1)); r.push((p.x + p.w * .56).toFixed(1) + ' ' + p.y.toFixed(1)); }
    edgeL.setAttribute('d', 'M' + l.join('L')); edgeR.setAttribute('d', 'M' + r.join('L'));
    [edgeL, edgeR].forEach(function (e) { var n = e.getTotalLength ? e.getTotalLength() : 2000; e.style.strokeDasharray = n + ' ' + n; e.__n = n; });
    var dt = B[1] + doorH * .035 - doorH;
    door.style.cssText = 'left:' + (B[0] - doorW / 2).toFixed(1) + 'px;top:' + dt.toFixed(1) + 'px;width:' + doorW.toFixed(1) + 'px;height:' + doorH.toFixed(1) + 'px';
    door.querySelector('.lf').style.transformOrigin = (IM.hingeL * 100).toFixed(1) + '% 50%';
    door.querySelector('.rt').style.transformOrigin = (IM.hingeR * 100).toFixed(1) + '% 50%';
    beam.style.cssText = 'left:' + (B[0] - wA * 1.6).toFixed(1) + 'px;top:' + (B[1] - doorH * .1).toFixed(1) + 'px;width:' + (wA * 3.2).toFixed(1) + 'px;height:' + (A[1] - B[1] + wA * .8).toFixed(1) + 'px';
    push.style.top = (dt + doorH * .36).toFixed(1) + 'px';
    cam.style.transformOrigin = B[0].toFixed(1) + 'px ' + (B[1] - doorH * .3).toFixed(1) + 'px';
    fires.forEach(function (f, i) {
      var p = P(FIRE_AT[i] / N), side = i % 2 ? 1 : -1;
      f.style.transform = 'translate(' + (p.x + side * p.w * .95).toFixed(1) + 'px,' + p.y.toFixed(1) + 'px) scale(' + Math.max(.5, Math.pow(p.s, .55)).toFixed(3) + ')';
    });
    for (var j = 0; j < placed; j++) stoneEls[j].style.transform = stoneT(j);
    sizeCv();
    drawRoad();
  }
  /* 石头的样子：精灵图里第 i 块（照路上的先后：兽骨、墙砖、铜犁和田土、井沿、台阶） */
  var stoneEls = [];
  var ORDER = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
  /* 石头躺在路面上：宽照路宽，高照这一格在屏上占多高（透视压扁），不照精灵图原来的高宽比 */
  function stoneBoxWH(i) { var p = P(tOf(i)), a = P(i / N), b = P((i + 1) / N), r = IM.rects[ORDER[i] % IM.rects.length], w = p.w * 1.04; return [w, Math.min(w * r[3] / r[2], Math.max((a.y - b.y) * 1.7, w * .3))]; }
  function stoneT(i) { var p = P(tOf(i)), wh = stoneBoxWH(i); return 'translate(' + (p.x - wh[0] / 2).toFixed(1) + 'px,' + (p.y - wh[1] * .6).toFixed(1) + 'px)'; }
  function skin(el, i) {
    var wh = stoneBoxWH(i), r = IM.rects[ORDER[i] % IM.rects.length], k = wh[0] / r[2], ky = wh[1] / r[3];
    el.style.width = wh[0].toFixed(1) + 'px'; el.style.height = wh[1].toFixed(1) + 'px';
    if (!STONE) { el.classList.add('ln'); return; }
    el.classList.remove('ln');
    var im = el.firstChild || el.appendChild(STONE.cloneNode());
    im.style.width = (IM.sheet[0] * k).toFixed(1) + 'px'; im.style.height = (IM.sheet[1] * ky).toFixed(1) + 'px';
    im.style.transform = 'translate(' + (-r[0] * k).toFixed(1) + 'px,' + (-r[1] * ky).toFixed(1) + 'px)';
  }
  function placeStone(i) {
    var el = mk('div', 'g-st', stoneBox); stoneEls[i] = el; el.style.zIndex = String(100 - i);
    skin(el, i);
    var end = stoneT(i);
    lastPlace = now();
    if (reduce) { el.style.transform = end; return; }
    /* 从哪一块碎影上剥下来：前十块从身后（过去）来，末两块从前方（往后）来 */
    var fromPast = i < 10, ox, oy;
    if (wide) { ox = fromPast ? (Math.random() < .5 ? Wd * (.04 + Math.random() * .2) : Wd * (.76 + Math.random() * .2)) : Wd * (.3 + Math.random() * .4); oy = fromPast ? Hd * (.55 + Math.random() * .35) : Hd * (.06 + Math.random() * .22); }
    else { ox = Wd * (.08 + Math.random() * .84); oy = fromPast ? Hd * (.68 + Math.random() * .26) : Hd * (.04 + Math.random() * .2); }
    var wh = stoneBoxWH(i), p = P(tOf(i)), mx = (ox + p.x) / 2 + (Math.random() - .5) * Wd * .15, my = Math.min(oy, p.y) - Hd * .08;
    var tr = function (x, y, s, r) { return 'translate(' + (x - wh[0] / 2).toFixed(1) + 'px,' + (y - wh[1] * .6).toFixed(1) + 'px) rotate(' + r + 'deg) scale(' + s + ')'; };
    var r0 = Math.round((Math.random() - .5) * 140);
    flick(fromPast ? pastB : futB, 260);
    var an = el.animate([
      { transform: tr(ox, oy, .55, r0), opacity: 0, filter: 'brightness(2.4) sepia(.6)' },
      { transform: tr(ox, oy - 6, .6, r0), opacity: 1, offset: .12, filter: 'brightness(2.2) sepia(.6)' },
      { transform: tr(mx, my, .9, r0 / 3), opacity: 1, offset: .62, filter: 'brightness(1.5) sepia(.3)' },
      { transform: end, opacity: 1, filter: 'brightness(1) sepia(0)' }
    ], { duration: 980 * SLOW, easing: 'cubic-bezier(.33,.1,.25,1)', fill: 'forwards' });
    an.onfinish = function () { el.style.transform = end; an.cancel(); spark(p.x, p.y - wh[1] * .1, 10, p.s); };
  }

  /* ---------- 完好和破败：破败那一张时不时闪一下 ---------- */
  function flick(el, ms) { if (reduce || !el.classList.contains('on')) return; el.classList.add('fl'); setTimeout(function () { el.classList.remove('fl'); }, ms); }
  (function flickLoop() {
    if (opened) return;
    if (phase >= 2) { var w = Math.random() < .5 ? pastB : futB; flick(w, 90 + Math.random() * 260); if (Math.random() < .35) setTimeout(function () { flick(w, 70 + Math.random() * 120); }, 260); }
    setTimeout(flickLoop, (1400 + Math.random() * 2600) * SLOW);
  })();

  /* ---------- 光粒（落地的火星、开门涌出的小火） ---------- */
  var ctx = cv.getContext && cv.getContext('2d'), DPR = 1, motes = [];
  function sizeCv() { DPR = Math.min(2, window.devicePixelRatio || 1); cv.width = Math.round(Wd * DPR); cv.height = Math.round(Hd * DPR); }
  function spark(x, y, n, s) {
    if (reduce) return;
    for (var i = 0; i < n; i++) { var a = -Math.PI * (.15 + Math.random() * .7); motes.push({ x: x, y: y, vx: Math.cos(a) * (.6 + Math.random() * 1.6) * s, vy: Math.sin(a) * (.8 + Math.random() * 1.8) * s, r: (.6 + Math.random() * 1.3) * Math.max(.6, s), l: 0, m: 26 + Math.random() * 30, g: .03, c: Math.random() < .5 ? '255,214,150' : '255,170,100' }); }
  }
  function drawMotes() {
    if (!ctx) return;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.clearRect(0, 0, Wd, Hd);
    if (!motes.length) return;
    ctx.globalCompositeOperation = 'lighter';
    for (var i = motes.length - 1; i >= 0; i--) {
      var m = motes[i]; m.l++;
      if (m.l > m.m) { motes.splice(i, 1); continue; }
      m.x += m.vx; m.y += m.vy; m.vy += m.g; if (m.grow) { m.vx *= 1.035; m.vy *= 1.035; m.r *= 1.012; }
      var a = Math.sin(Math.PI * m.l / m.m);
      ctx.fillStyle = 'rgba(' + m.c + ',' + (a * .95).toFixed(3) + ')';
      ctx.beginPath(); ctx.arc(m.x, m.y, m.r, 0, 6.2832); ctx.fill();
      if (m.r > 1.1) { ctx.fillStyle = 'rgba(' + m.c + ',' + (a * .18).toFixed(3) + ')'; ctx.beginPath(); ctx.arc(m.x, m.y, m.r * 3.2, 0, 6.2832); ctx.fill(); }
    }
    ctx.globalCompositeOperation = 'source-over';
  }

  /* ---------- 路的边、火、镜头 ---------- */
  function drawRoad() {
    var e = Math.min(1, R * 1.08);
    [edgeL, edgeR].forEach(function (p) { if (p.__n) p.style.strokeDashoffset = (p.__n * (1 - e)).toFixed(1); });
  }
  var soulT = 0;
  function moveSoul() {
    var target = placed ? Math.max(0, tOf(placed - 1) - .02) : 0;
    if (phase >= 4) target = tOf(N - 1) + .02;
    soulT += (target - soulT) * .045;
    var p = P(soulT), p0_ = P(0);
    soul.style.transform = 'translate(' + (p.x - p0_.x).toFixed(1) + 'px,' + (p.y - p0_.y).toFixed(1) + 'px) scale(' + Math.pow(p.s, .7).toFixed(3) + ')';
    cam.style.transform = 'scale(' + (1 + .1 * soulT).toFixed(4) + ')';
  }
  function lightFires() {
    fires.forEach(function (f, i) {
      var id = BOOKS[i][0];
      if (!f.classList.contains('on') && books[id] && (R * N >= FIRE_AT[i] + .5 || phase >= 4)) { f.classList.add('on'); var p = P(FIRE_AT[i] / N); spark(p.x + (i % 2 ? 1 : -1) * p.w * .95, p.y - 12, 14, p.s); }
    });
  }

  /* ---------- 节奏：每一拍有最短的时长，跟着真进度走 ---------- */
  var MIN1 = 450, ROAD = 1200;
  function toP2() {
    phase = 2; tP2 = now(); G.classList.add('g-p2');
    if (reduce) toDoor();
  }
  function toDoor() {
    if (phase >= 4) return;
    phase = 4; onDoor = true; G.classList.add('g-p4');
    if (reduce) { while (placed < N) placeStone(placed++); R = 1; }
  }
  var last = now(), l0said = false;
  function frame() {
    if (opened) return;
    var t = now(), dt = Math.min(64, t - last); last = t;
    /* 走查脚本直接驱动牌桌（__tb.skip、select……）的时候，载入页自己让开 */
    if (window.__tb && window.__tb.stage && window.__tb.stage !== 'intro') { open(true); return; }
    var pr = p0();
    if (pr >= 1 && !l0said) { l0said = true; l0Res(); }
    if (phase === 1 && t - T0 >= MIN1 * SLOW) toP2();
    if (phase >= 2 && !reduce) {
      var cap = Math.max(0, (t - tP2 - 550 * SLOW) / (ROAD * SLOW));
      var tgt = Math.min(pr, cap, 1);
      if (tgt > R) R = Math.min(tgt, R + Math.max((tgt - R) * dt / 260, dt / (ROAD * SLOW) * .35));
      if (pr >= 1 && cap >= 1 && R > .985) R = 1;
      while (placed < N && R >= (placed + 1) / N - 1e-6) placeStone(placed++);
      if (phase < 4 && placed === N && t - lastPlace > 700 * SLOW) toDoor();
    }
    if (phase >= 2) { moveSoul(); lightFires(); drawRoad(); }
    drawMotes();
    requestAnimationFrame(frame);
  }

  /* ---------- 第五拍：门往里推开，千千万万粒小火，连成一片白，白退下去牌桌在那里 ---------- */
  function open(fast) {
    if (opened) return;
    opened = true; l0Res();
    try { if (typeof window.__gateOpened === 'function') window.__gateOpened(); } catch (e) {}
    try { window.dispatchEvent(new CustomEvent('aldran:gate-opened')); } catch (e) {}
    if (phase < 4) G.classList.add('g-p4');
    G.classList.add('g-p5');
    var S = (fast ? .55 : 1) * SLOW;
    var dr = door.getBoundingClientRect(), cx = dr.left + dr.width / 2, cy = dr.top + dr.height * .58;
    var D = 3 * Math.max(Wd, Hd);      // 白是一个很大的软边圆，从门心长开，长满了屏幕四角都在它实心的那一截里
    white.style.cssText = 'left:' + (cx - D / 2).toFixed(0) + 'px;top:' + (cy - D / 2).toFixed(0) + 'px;width:' + D + 'px;height:' + D + 'px';
    var end = function () {
      holdRes(); window.__tbPause = false;
      cam.style.display = 'none'; cv.style.display = 'none';
      var an = white.animate([{ opacity: 1 }, { opacity: 0 }], { duration: reduce ? 300 : 1300 * SLOW, easing: 'cubic-bezier(.4,0,.2,1)', fill: 'forwards' });
      an.onfinish = function () { G.remove(); };
    };
    if (reduce) { white.animate([{ opacity: 0, transform: 'none' }, { opacity: 1, transform: 'none' }], { duration: 300, fill: 'forwards' }).onfinish = end; return; }
    var ease = 'cubic-bezier(.55,.05,.3,1)';
    door.querySelector('.lf').animate([{ transform: 'rotateY(0)' }, { transform: 'rotateY(80deg)' }], { duration: 1150 * S, easing: ease, fill: 'forwards' });
    door.querySelector('.rt').animate([{ transform: 'rotateY(0)' }, { transform: 'rotateY(-80deg)' }], { duration: 1150 * S, easing: ease, fill: 'forwards' });
    door.querySelector('.glow').animate([{ opacity: 0 }, { opacity: 1 }], { duration: 700 * S, easing: 'ease-in', fill: 'forwards' });
    /* 光粒：从门缝里一粒一粒涌出来，越来越多，往镜头这边来 */
    var t0 = now(), born = 0, TOTAL = fast ? 900 : 1800;
    (function emit() {
      if (!G.isConnected) return;
      var e = (now() - t0) / (1500 * S), want = Math.min(TOTAL, Math.floor(TOTAL * Math.pow(Math.min(1, e), 1.6)));
      for (; born < want; born++) {
        var a = Math.random() * 6.2832, sp = .4 + Math.random() * 2.2, ox = (Math.random() - .5) * dr.width * (.15 + e * .6), oy = (Math.random() - .5) * dr.height * (.2 + e * .5);
        motes.push({ x: cx + ox, y: cy + oy, vx: Math.cos(a) * sp + ox * .012, vy: Math.sin(a) * sp * .8 + oy * .012, r: (.7 + Math.random() * 1.8) * Math.max(1, Hd / 900), l: 0, m: 50 + Math.random() * 60, g: -.004, grow: 1, c: Math.random() < .3 ? '255,255,255' : Math.random() < .6 ? '255,236,196' : '255,196,130' });
      }
      if (e < 1.3) requestAnimationFrame(emit);
    })();
    (function run() { if (!G.isConnected || cv.style.display === 'none') return; drawMotes(); requestAnimationFrame(run); })();
    soul.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 900 * S, delay: 700 * S, fill: 'forwards' });
    var wa = white.animate([{ opacity: 0, transform: 'scale(.03)' }, { opacity: .8, transform: 'scale(.3)', offset: .45 }, { opacity: 1, transform: 'scale(1)' }],
      { duration: 900 * S, delay: 750 * S, easing: 'cubic-bezier(.5,0,.6,1)', fill: 'forwards' });
    wa.onfinish = function () { setTimeout(end, 180 * S); };
  }
  G.addEventListener('click', function (e) { if (e.target === skip) return; if (onDoor) open(false); });
  skip.addEventListener('click', function (e) { e.stopPropagation(); open(true); });
  addEventListener('keydown', function (e) { if (!opened && (e.key === 'Enter' || e.key === ' ') && onDoor) open(false); });

  /* 本地验的时候用：__gate.state() 看走到哪；__gate.p0 看第零层几成 */
  window.__gate = { state: function () { return { phase: phase, R: R, placed: placed, p0: p0(), books: books, opened: opened }; }, open: open, toDoor: toDoor };
  try {
    layout(); addEventListener('resize', layout);
    loadArt();
    requestAnimationFrame(frame);
    if (Q.has('nogate')) open(true);      // 本地看牌桌、不看载入页
  } catch (err) {      // 载入页自己出了错，不能把牌桌拦住
    try { G.remove(); } catch (e) {}
    window.__tbPause = false; holdRes(); l0Res();
  }
})();
