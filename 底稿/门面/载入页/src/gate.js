/* 载入页第二版（11-26 夜）。用户看了第一版说：“其实我想做的是更接近原神的那种。在道路上前进，光景在两侧自前方往身后远去，道路在脚下成型，加载完成后门扉成型。这样子我觉得可以吧这段加载拉长一点，多加载些资源”。
   薄壳那一截照旧只画第一拍（星空、灰雾、正中一团火，gate0.css），外壳接手以后：
   二、雾往两边散开，地平线亮起来，火落到画面下方当中，镜头起步，沿着路往前走（第三人称、略高、透视）；
   三、路在脚下成型：远处是散着的光点，到前头那一道“正在成型”的光边才凝成路石，镜头一直往前，脚下永远是刚凝成的那一段；
       两侧一幅一幅的景照纪的先后（月银纪的雪原和初火、万兽、辉塔；纷争纪的长垒、黑潮；山铜纪的双王旗、城邦；迷宫纪的井口、公会灯笼；此刻的灯海、浮空塔、崖上的背影）
       从远处的雾里浮出来、迎面变大、从身边掠过、淡到身后；每一纪的头一幅旁边路边立一处火，那一本书的页面和开书数据载好了才亮；
       真进度推着走：载得快走得快，载得慢就放慢脚步（不停下），景照常缓缓掠过；
   四、第零层、第一层、门后头一眼要用的那些（第二层）都齐了（或者到了时长上限），而且走够了最短的一段，路尽头的门由光点聚成、立起来，镜头慢下来停在门前，浮出“推开门扉”；
   五、点门（或跳过）：门往里推开，千千万万粒小火，连成一整片白，白退下去牌桌在那里。推开那一下调 window.__gateOpened()（往后放音乐用）。
   跟外壳别的部分怎么接：window.__g0(名) 是 index.html 里各个脚本、样式 onload 报到用的；window.__gateBook(书, 载到没有) 是 shell.js 的预载报的；
   window.__gateL0 在第零层齐了的时候兑现（shell.js 等它再开始预载五本书）；window.__gateHold 在白退下去那一刻兑现（牌桌这时候才开场）。
   下面 __X__ 几处是 tools/build_gate.py 填的（传说、第零层的单子和大小、五本书各多大、第二层的单子、图的单子）。
   本地看：地址带 ?gslow=3 整体放慢三倍；?gmin=秒 改最短时长；?nogate 直接跳过。 */
(function () {
  'use strict';
  var G = document.getElementById('gate');
  var holdRes, l0Res;
  window.__gateHold = new Promise(function (r) { holdRes = r; });
  window.__gateL0 = new Promise(function (r) { l0Res = r; });
  if (!G) { holdRes(); l0Res(); return; }
  /* 11-27 止血（风月安卓 App 里玩家停在第一拍那一团火上、整页划不动）：载入页只要出一点岔子就自己让路。
     window.__gateKill(缘故)：拆掉整个载入页、放出牌桌（外壳 shell.js 的保底也调它）。缘故记在 window.__gateWhy。 */
  var killed = false;
  function kill(why) {
    if (killed) return;
    killed = true; opened = true;
    window.__gateWhy = String(why || '');
    try { G.remove(); } catch (e) { try { G.style.display = 'none'; } catch (x) {} }
    window.__tbPause = false; holdRes(); l0Res();
  }
  window.__gateKill = kill;
  /* 代码出错（不是网取不到）就拆：TypeError、ReferenceError、SyntaxError、RangeError */
  var codeErr = function (e) { return e && /^(TypeError|ReferenceError|SyntaxError|RangeError)$/.test(e.name || ''); };
  window.addEventListener('error', function (ev) { if (!killed && !opened && (codeErr(ev.error) || (!ev.error && ev.message && /Error/.test(ev.message)))) kill('出错：' + (ev.message || '')); });
  window.addEventListener('unhandledrejection', function (ev) { if (!killed && !opened && codeErr(ev.reason)) kill('出错：' + ev.reason.name + ' ' + ev.reason.message); });
  var now = function () { return performance.now(); };
  var T0 = typeof window.__gateT0 === 'number' && window.__gateT0 <= now() ? window.__gateT0 : now();
  G.style.setProperty('--gt', (T0 - now()).toFixed(0) + 'ms');      // 薄壳那一截的动画接着原来的相位走
  var LORE = __LORE__, ITEMS = __ITEMS__, BOOKW = __BOOKW__, L2 = __L2__, IM = __IMG__;
  var BOOKS = [['moon', '月银纪'], ['strife', '纷争纪'], ['bronze', '山铜纪'], ['maze', '迷宫纪·前传'], ['now', '迷宫纪·此刻']];
  var MIR = ['https://cdn.jsdelivr.net/', 'https://fastly.jsdelivr.net/', 'https://gcore.jsdelivr.net/', 'https://testingcf.jsdelivr.net/', 'https://quantil.jsdelivr.net/'];
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var Q = new URLSearchParams(location.search);
  /* 11-27：3D 那几拍只给够得上的环境放。安卓 App 里的系统 WebView（UA 带 “; wv)”）、取不到 WebGL（多半是软件渲染）、
     浏览器不认 preserve-3d、内存 2GB 以下、安卓上 Chrome 内核九十以前的，都走轻量的一路。?glite 强制走轻量，?gfull 强制走全的（本地验用）。 */
  var UA = navigator.userAgent || '';
  var cv0 = +((UA.match(/Chrome\/(\d+)/) || [])[1] || 0);
  var hasGL = (function () { try { var c = document.createElement('canvas'), g = c.getContext('webgl') || c.getContext('experimental-webgl'); if (!g) return false; var x = g.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); return true; } catch (e) { return false; } })();
  var can3d = !!(window.CSS && CSS.supports && CSS.supports('transform-style', 'preserve-3d') && CSS.supports('perspective', '1px'));
  var lite = Q.has('gfull') ? false : Q.has('glite') || !can3d || !hasGL || /; wv\)/.test(UA) || (navigator.deviceMemory && navigator.deviceMemory <= 2) || (/Android/.test(UA) && cv0 > 0 && cv0 < 90);
  window.__gateLite = lite;
  var SLOW = Math.max(.1, +Q.get('gslow') || 1);
  var TMIN = (+Q.get('gmin') || 9) * 1000 * SLOW;                  // 最短走多久（缓存都在也走完这一段才出门）
  window.__tbPause = true;                                          // 牌桌那一层先不画
  var phase = 1, t2 = 0, opened = false, onDoor = false, books = {};
  var cam = G.querySelector('#g-cam'), soul = G.querySelector('.g-soul'), fogEl = G.querySelector('.g-fog'), rift = G.querySelector('.g-rift');
  var mk = function (tag, cls, parent, before) { var e = document.createElement(tag); if (cls) e.className = cls; (parent || cam).insertBefore(e, before || null); return e; };

  /* ---------- 图：都用 <img> 挂（沙箱里同一个地址样式再取一回会再下一回），镜像取不到换下一个 ---------- */
  var abs = function (u) { try { return new URL(u, document.baseURI).href; } catch (e) { return u; } };
  var KEEP = window.__gateKeep = [];                                // 取过的图留着引用，牌桌和书用到的时候同一页里不再下一回
  function img(rel, ok, hi, bad) {
    var im = new Image(), src = abs(rel), n = 0;
    im.decoding = 'async'; im.alt = '';
    try { im.fetchPriority = hi ? 'high' : 'low'; } catch (e) {}
    im.onload = function () { im.onload = im.onerror = null; KEEP.push(im); ok && ok(im); };
    im.onerror = function () {
      for (var i = 0; i < MIR.length; i++) if (src.indexOf(MIR[i]) === 0 && n < MIR.length - 1) { n++; src = MIR[(i + 1) % MIR.length] + src.slice(MIR[i].length); im.src = src; return; }
      bad && bad();
    };
    im.src = src;
    return im;
  }

  /* ---------- 搭场景 ---------- */
  var skyI = mk('div', 'g-skyi', cam, rift);
  var hzL = mk('div', 'g-hz', cam, fogEl), ground = mk('div', 'g-ground', cam, fogEl);
  var D3 = mk('div', '', cam, fogEl); D3.id = 'g-3d';
  var WD = mk('div', 'g-wd', D3);
  var road = mk('div', 'g-road', WD), rtex = mk('div', 'g-rtex', road);
  var spark = mk('div', 'g-spark', WD), stex = mk('div', 'g-stex', spark);
  var edge = mk('div', 'g-edge', WD); mk('i', '', edge);
  var door = mk('div', 'g-door', WD);
  door.innerHTML = '<div class="glow"></div><svg class="ln" viewBox="0 0 100 150" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;overflow:visible"><path d="M18 146V58Q18 16 50 4Q82 16 82 58V146" fill="rgba(10,10,18,.55)" stroke="rgba(255,226,180,.85)" stroke-width="1" vector-effect="non-scaling-stroke"/><path d="M8 150H92M12 146H88" stroke="rgba(255,226,180,.5)" stroke-width="1" vector-effect="non-scaling-stroke"/></svg><div class="lf"></div><div class="rt"></div><div class="fr"></div><div class="seam"></div>';
  door.classList.add('nol');
  var white = mk('div', 'g-white', G), cv = mk('canvas', 'g-motes', G);
  var push = mk('p', 'g-push', G); push.textContent = '推开门扉';
  var lore = mk('p', 'g-lore', G);
  var skip = mk('button', 'g-skip', G); skip.type = 'button'; skip.textContent = '跳过';
  var CARDS = IM.cards;           // [{k, era}]，照纪的先后
  var cardImg = {};
  /* 载入页自己的图排成一队、两路取：路面先（慢网上它是画面的大半），再星空、景（照出场的先后）、门。慢网上一下子全发出去，哪一张都到得晚 */
  function loadArt() {
    var dn = 0, dset = function (cls) { return function (im) { door.querySelector(cls).appendChild(im); if (++dn === 3) door.classList.remove('nol'); }; };
    var q = [[IM.road, function (im) { rtex.style.backgroundImage = 'url("' + im.src + '")'; texH = 0; layout(); }],
             [IM.sky, function (im) { im.className = 'g-fill'; skyI.appendChild(im); requestAnimationFrame(function () { skyI.classList.add('on'); }); }]];
    CARDS.forEach(function (c, i) { q.push([IM.dir + c.k + '.webp', function (im) { cardImg[c.k] = im; }]); if (i === 5) q.push([IM.door_f, dset('.fr')], [IM.door_l, dset('.lf')], [IM.door_r, dset('.rt')]); });
    var i = 0, one = function () { if (i >= q.length) return; var it = q[i++]; img(it[0], function (im) { it[1](im); one(); }, 1, one); };
    one(); one();
  }

  /* ---------- 第零层：外壳的页面、脚本、样式、牌桌的图、五张牌面 ---------- */
  var got = {};
  window.__g0 = function (k) { got[k] = 1; };
  /* 第零层的图牌桌那边也在取，这里只是看它到没到，取的先后让给载入页自己的图（路面、景）：慢网上先看得见路 */
  var reg0 = function () { ITEMS.forEach(function (it) { if (it.img) img(it.k, function () { got[it.k] = 1; }, 0, function () { got[it.k] = 1; }); }); };
  var loadedAll = false;
  window.addEventListener('load', function () { loadedAll = true; });
  var W0 = ITEMS.reduce(function (s, it) { return s + it.w; }, 0);
  function done0() { if (loadedAll) return W0; var s = 0; ITEMS.forEach(function (it) { if (got[it.k]) s += it.w; }); return s; }
  /* 第一层：五本书的页面和开书数据（shell.js 取，取完一本报一本） */
  var W1 = 0; for (var bk in BOOKW) W1 += BOOKW[bk];
  window.__gateBook = function (id, ok) { books[id] = ok === false ? 2 : 1; };
  function done1() { var s = 0; for (var k in books) s += BOOKW[k] || 0; return s; }
  /* 第二层：门后头一眼要用的（建档的资料和图、大图书馆圆厅、世界之书的头几页、她请离那一眼的图）。
     只载外壳这一页自己会用到的：书是沙箱里另一格，跟这一页不共用浏览器的缓存（11-26 量过，同一张图两边各下一回），书里的图在这里先载了也省不下。
     开了省流量、网速慢（2G、3G，或者第零层载得慢）就不载这一层。 */
  var W2 = L2.reduce(function (s, it) { return s + it.w; }, 0), got2 = {}, slow = false, l2on = false;
  try { var NC = navigator.connection; if (NC && (NC.saveData || /(^|-)(2g|3g)$/.test(NC.effectiveType || ''))) slow = true; } catch (e) {}
  function done2() { var s = 0; L2.forEach(function (it) { if (got2[it.k]) s += it.w; }); return s; }
  function startL2() {
    if (l2on || slow) return; l2on = true;
    var i = 0, one = function () {
      if (i >= L2.length) return;
      var it = L2[i++], fin = function () { got2[it.k] = 1; one(); };
      if (it.j) { var go = function () { if (window.__preGet) window.__preGet(abs(it.k)).then(fin, fin); else setTimeout(go, 300); }; go(); }
      else img(it.k, fin, 0, fin);
    };
    one(); one();
  }
  var l0at = 0;
  function P() {      // 总进度（照大小加权）；慢网只算第零、一层
    var a = done0(), b = done1(), c = slow ? 0 : done2(), w = W0 + W1 + (slow ? 0 : W2);
    return w ? (a + b + c) / w : 1;
  }

  /* ---------- 版式：镜头、地平线、路、两侧的景位置都照屏高的比例（u），竖屏横屏一套算法 ---------- */
  var Wd, Hd, wide, u, PER, hzY, yG, RW, Lr, zc, zE, texH = 0, feetY, sY0;
  var ZS = -180, SPACING = 640, ZFAR = -5600, ZSTOP = -1150;
  function L() {
    Wd = innerWidth || document.documentElement.clientWidth || 1; Hd = innerHeight || document.documentElement.clientHeight || 1;
    wide = Wd / Hd >= 1.15; u = Hd / 844;
    PER = 760 * u; hzY = Hd * (wide ? .44 : .40);
    feetY = Hd * (wide ? .84 : .80);
    yG = (feetY - hzY) * (PER - ZS * u) / PER;
    RW = (wide ? 400 : 300) * u; Lr = 9200 * u; zc = 300 * u - Lr / 2; zE = -1500 * u;
    sY0 = Hd * (wide ? .64 : .56) + 6;      // 第一拍火脚的位置（gate0.css 的 --sy）
  }
  var proj = function (x, y, z) { var s = PER / (PER - z); return [Wd / 2 + x * s, hzY + y * s, s]; };
  function layout() {
    L();
    G.style.setProperty('--hz', (hzY / Hd * 100).toFixed(2) + '%');
    D3.style.perspective = PER.toFixed(0) + 'px';
    road.style.width = spark.style.width = RW.toFixed(1) + 'px';
    road.style.height = spark.style.height = Lr.toFixed(0) + 'px';
    var t = 'translate3d(' + (-RW / 2).toFixed(1) + 'px,' + (yG - Lr / 2).toFixed(1) + 'px,' + zc.toFixed(1) + 'px) rotateX(90deg)';
    road.style.transform = t; spark.style.transform = t;
    var fe = (zE - (zc - Lr / 2)) / Lr * 100;
    G.style.setProperty('--fe0', (fe - 4).toFixed(2) + '%'); G.style.setProperty('--fe1', fe.toFixed(2) + '%'); G.style.setProperty('--fe2', (fe + 3).toFixed(2) + '%');
    texH = RW * 1.5;
    rtex.style.height = (Lr + texH).toFixed(0) + 'px'; rtex.style.backgroundSize = RW.toFixed(1) + 'px ' + texH.toFixed(1) + 'px';
    stex.style.height = (Lr + 140).toFixed(0) + 'px';
    var ew = RW * 1.7, eh = 260 * u;
    edge.style.width = ew + 'px'; edge.style.height = eh + 'px';
    edge.style.transform = 'translate3d(' + (-ew / 2).toFixed(1) + 'px,' + (yG - eh / 2 - 1).toFixed(1) + 'px,' + zE.toFixed(1) + 'px) rotateX(90deg)';
    sizeCv();
    objs.forEach(place);
  }

  /* ---------- 世界里的东西：两侧的景、路边的火、门。z 每一帧往镜头这边挪 ---------- */
  var objs = [];
  function place(o) {
    var x, y, w, h, tr = '';
    if (o.t === 'card') {
      w = (wide ? 1250 : 820) * u; h = w * 2 / 3;
      x = o.side * (RW / 2 + w * (wide ? .5 : .3) + (wide ? 120 : 0) * u);
      y = -h * (wide ? .08 : .02);      // 记忆的碎片浮在眼睛那么高，迎面过来往两边让开
      o.el.style.width = w + 'px'; o.el.style.height = h + 'px';
      tr = ' rotateY(' + (-o.side * 30) + 'deg)' + (o.flip ? ' scaleX(-1)' : '');
    } else if (o.t === 'post') {
      w = h = 0; x = o.side * (RW / 2 + 60 * u); y = yG;
      tr = ' scale(' + (1.25 * u).toFixed(3) + ')';
      if (o.lab) o.lab.style.opacity = (Math.min(1, Math.max(0, (o.z + 3600) / 900)) * Math.min(1, Math.max(0, (-500 - o.z) / 500))).toFixed(3);
    } else {      // door
      h = (wide ? .5 : .42) * Hd * (PER - ZSTOP * u) / PER; w = h * IM.doorAspect;
      x = 0; y = yG - h * .465;
      o.el.style.width = w + 'px'; o.el.style.height = h + 'px';
      door.querySelector('.lf').style.transformOrigin = (IM.hingeL * 100).toFixed(1) + '% 50%';
      door.querySelector('.rt').style.transformOrigin = (IM.hingeR * 100).toFixed(1) + '% 50%';
    }
    o.w = w; o.h = h; o.x = x; o.y = y;
    o.el.style.transform = 'translate3d(' + (x - w / 2).toFixed(1) + 'px,' + (y - h / 2).toFixed(1) + 'px,' + (o.z * u).toFixed(1) + 'px)' + tr;
    if (o.t === 'card') {
      var z = o.z, a = Math.min(1, Math.max(0, (z - ZFAR) / 1800)) * Math.min(1, Math.max(0, (-150 - z) / 550));
      o.el.style.opacity = (a * (o.dim || 1)).toFixed(3);
    }
  }
  var nCard = 0, lastSpawn = 0, side = -1, shown = [];
  function spawnCard(c, dim) {
    var el = mk('div', 'g-card', WD, door), im = cardImg[c.k].cloneNode();
    el.appendChild(im);
    side = -side;
    var o = { t: 'card', el: el, z: ZFAR, side: side, dim: dim || 1, flip: !!dim && Math.random() < .5 };
    objs.push(o); place(o); lastSpawn = now();
    if (!dim) shown.push(c);
    if (!dim && c.era != null && c.first) spawnPost(c.era, -side);
  }
  var posts = [];
  function spawnPost(era, sd) {
    var el = mk('div', 'g-post ' + (sd < 0 ? 'l' : 'r'), WD, door);
    el.innerHTML = '<b></b><u></u><i></i><span>' + BOOKS[era][1] + '</span>';
    var o = { t: 'post', el: el, z: ZFAR + 600, side: sd, era: era, lab: el.querySelector('span') };
    objs.push(o); posts.push(o); place(o);
  }
  var doorO = null;
  function spawnDoor(at) {
    if (doorO) return;
    doorO = { t: 'door', el: door, z: at == null ? -5000 : at };
    objs.push(doorO); place(doorO);
    setTimeout(function () { door.classList.add('on'); }, at == null ? 500 : 0);
    gather = now();
  }

  /* ---------- 光粒：成型那一道光上冒的火星、火走过留下的、门聚起来的、开门涌出来的 ---------- */
  var ctx = cv.getContext && cv.getContext('2d'), DPR = 1, motes = [], gather = 0;
  function sizeCv() { DPR = Math.min(2, window.devicePixelRatio || 1); cv.width = Math.round(Wd * DPR); cv.height = Math.round(Hd * DPR); }
  /* ?gslow=N 放慢的时候光粒也跟着慢（本地逐张截图录开门那一段用） */
  var GF = Math.pow(1.035, 1 / SLOW), RF = Math.pow(1.012, 1 / SLOW), SF = Math.pow(1.06, 1 / SLOW);
  function mote(o) {
    if (SLOW !== 1) { if (o.vx != null) { o.vx /= SLOW; o.vy /= SLOW; } if (o.g) o.g /= SLOW * SLOW; o.m *= SLOW; }
    motes.push(o); if (motes.length > 2600) motes.splice(0, motes.length - 2600);
  }
  function drawMotes() {
    if (!ctx) return;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.clearRect(0, 0, Wd, Hd);
    if (!motes.length) return;
    ctx.globalCompositeOperation = 'lighter';
    for (var i = motes.length - 1; i >= 0; i--) {
      var m = motes[i]; m.l++;
      if (m.l > m.m) { motes.splice(i, 1); continue; }
      if (m.tx != null) { var k = Math.min(1, m.l / m.m); var e = k * k * (3 - 2 * k); m.x = m.x0 + (m.tx - m.x0) * e; m.y = m.y0 + (m.ty - m.y0) * e; }
      else { m.x += m.vx; m.y += m.vy; m.vy += m.g; if (m.grow) { m.vx *= GF; m.vy *= GF; m.r *= RF; } }
      var a = Math.sin(Math.PI * m.l / m.m);
      if (m.st) {      // 速度线：顺着走的方向拉一道
        m.vx *= SF; m.vy *= SF;
        ctx.strokeStyle = 'rgba(' + m.c + ',' + (a * .8).toFixed(3) + ')'; ctx.lineWidth = m.r;
        ctx.beginPath(); ctx.moveTo(m.x - m.vx * 3.2 * SLOW, m.y - m.vy * 3.2 * SLOW); ctx.lineTo(m.x, m.y); ctx.stroke();
        continue;
      }
      ctx.fillStyle = 'rgba(' + m.c + ',' + (a * .95).toFixed(3) + ')';
      ctx.beginPath(); ctx.arc(m.x, m.y, m.r, 0, 6.2832); ctx.fill();
      if (m.r > 1.1) { ctx.fillStyle = 'rgba(' + m.c + ',' + (a * .18).toFixed(3) + ')'; ctx.beginPath(); ctx.arc(m.x, m.y, m.r * 3.2, 0, 6.2832); ctx.fill(); }
    }
    ctx.globalCompositeOperation = 'source-over';
  }

  /* ---------- 传说：底下一句，走路的时候隔一阵换一句 ---------- */
  var li = Math.floor(Math.random() * LORE.length);
  function nextLore() {
    lore.classList.remove('on');
    setTimeout(function () { lore.textContent = LORE[li++ % LORE.length]; lore.classList.add('on'); }, 700);
  }

  /* ---------- 一帧 ---------- */
  var D = 0, v = 0, last = now(), l0said = false, soulK = 0, roadOff = 0, sparkOff = 0, tLore = 0, waitImg = 0;
  function toP2() {
    phase = 2; t2 = now(); G.classList.add('g-p2'); nextLore(); tLore = t2;
    if (reduce) staticScene();
  }
  var staticDone = {};
  function staticCards() {      // 减少动态效果：不走，景摆几幅在两边（图到一张摆一张），门直接立在路尽头
    [0, 3, 5, 7, 9].forEach(function (ci, j) {
      var c = CARDS[ci]; if (!c || staticDone[ci] || !cardImg[c.k]) return; staticDone[ci] = 1;
      side = j % 2 ? -1 : 1; spawnCard(c); var o = objs[objs.length - 1]; o.z = -1400 - j * 700; place(o);
      posts.forEach(function (p, k) { p.z = -800 - k * 700; place(p); });
    });
  }
  function staticScene() { staticCards(); spawnDoor(ZSTOP); toDoor(); }
  function toDoor() {
    if (phase >= 4) return;
    phase = 4; onDoor = true; G.classList.add('g-p4');
    var r = door.getBoundingClientRect();
    push.style.top = (r.top + r.height * .34).toFixed(1) + 'px';
  }
  function frame() {
    if (opened) return;
    lastFrame = now();
    var t = now(), dt = Math.min(64, t - last) / 1000; last = t;
    if (window.__tb && window.__tb.stage && window.__tb.stage !== 'intro') { open(true); return; }      // 走查脚本直接驱动牌桌的时候让开
    var a0 = done0();
    if (a0 >= W0 && !l0said) {
      l0said = true; l0at = t; l0Res(); startL2();
      if (!slow && (t - T0) > 1500 && W0 * 1024 / ((t - T0) / 1000) < 250 * 1024) slow = true;      // 第零层载得比每秒 250KB 慢，算慢网
    }
    if (phase === 1 && t - T0 >= 450 * SLOW) toP2();
    if (phase >= 2 && !reduce) {
      var since = t - t2, cap = since > (slow ? 16000 : 30000) * SLOW;
      var p = cap && l0said ? 1 : P();
      var allow = CARDS.length * SPACING * Math.min(1, p, since / TMIN);
      var vmax = 1300 * u / SLOW, vmin = 280 * u / SLOW, vt;
      if (doorO) {       // 门出来了：照离停下来的地方多远放慢
        var rem = (ZSTOP - doorO.z) * u;
        vt = rem > 2 ? Math.max(40 * u, Math.min(950 * u, rem * 1.15)) / SLOW : 0;
        if (rem <= 2 && phase < 4) { doorO.z = ZSTOP; v = 0; toDoor(); }
      } else vt = Math.max(vmin, Math.min(vmax, (allow - D) * u / .9 / SLOW));
      var ease = Math.min(1, dt / .45);
      v += (vt - v) * ease;
      if (since < 1400 * SLOW) v *= since / (1400 * SLOW);      // 起步
      var dz = v * dt / u;                                     // 这一帧往前走了多少（世界单位）
      if (doorO && doorO.z + dz > ZSTOP) dz = Math.max(0, ZSTOP - doorO.z);
      D += dz;
      /* 景：走到了就从远处浮出来一幅；进度不够的时候不往前透（至多早一幅），图没到的先不出 */
      var want = Math.floor(D / SPACING);
      if (nCard < CARDS.length && want >= nCard && nCard * SPACING <= allow + SPACING * .5) {
        var c = CARDS[nCard];
        if (cardImg[c.k]) { spawnCard(c); nCard++; waitImg = 0; }
        else if (!waitImg) waitImg = t;
        else if (t - waitImg > 9000 * SLOW) { nCard++; waitImg = 0; }       // 这一幅等九秒还不到就跳过（图都是排着队取的，一般等得到）
      }
      /* 卡住的时候：隔一阵把走过的再淡淡地浮一幅（照镜子翻过来），路上不空 */
      if (shown.length && t - lastSpawn > 2600 * SLOW && !doorO) spawnCard(shown[Math.floor(Math.random() * shown.length)], .5);
      /* 门：都齐了、走够了、景都出过了 */
      if (!doorO && p >= 1 && l0said && since >= TMIN * .8 && nCard >= CARDS.length) spawnDoor();
      for (var i = objs.length - 1; i >= 0; i--) {
        var o = objs[i];
        o.z += dz;
        if (o.t !== 'door' && o.z > 600) { o.el.remove(); objs.splice(i, 1); continue; }
        place(o);
      }
      /* 路面往镜头流 */
      roadOff = (roadOff + dz * u) % (texH || 1e9); sparkOff = (sparkOff + dz * u) % 140;
      rtex.style.transform = 'translate3d(0,' + (roadOff - texH).toFixed(1) + 'px,0)';
      stex.style.transform = 'translate3d(0,' + (sparkOff - 140).toFixed(1) + 'px,0)';
      /* 成型那一道光上冒火星；火身后掉火星 */
      var ep = proj(0, yG, zE), es = ep[2];
      if (Math.random() < .55) mote({ x: ep[0] + (Math.random() - .5) * RW * es * 1.1, y: ep[1] + (Math.random() - .5) * 4, vx: (Math.random() - .5) * .3, vy: -.3 - Math.random() * .7, r: .6 + Math.random() * 1.2, l: 0, m: 40 + Math.random() * 40, g: -.002, c: Math.random() < .5 ? '255,226,180' : '255,190,120' });
      /* 魂灵：从第一拍的位置落到画面下方，走路一起一伏 */
      soulK = Math.min(1, soulK + dt / (1.6 * SLOW));
      var sk = soulK * soulK * (3 - 2 * soulK), bob = Math.sin(t / (300 * SLOW)) * 3 * Math.min(1, v / (300 * u / SLOW));
      soul.style.transform = 'translate(0,' + ((feetY - sY0) * sk + bob).toFixed(1) + 'px) scale(' + (1 + .25 * sk).toFixed(3) + ')';
      if (v > 50 * u && Math.random() < .3) mote({ x: Wd / 2 + (Math.random() - .5) * 10, y: feetY - 14, vx: (Math.random() - .5) * .5, vy: .6 + Math.random() * .8, r: .5 + Math.random(), l: 0, m: 26 + Math.random() * 20, g: .01, c: '255,190,120' });
      /* 门聚起来：光点从四周飞向门 */
      if (doorO && t - gather < 2600 * SLOW && Math.random() < .9) {
        var r = door.getBoundingClientRect();
        for (var q = 0; q < 6; q++) { var tx = r.left + Math.random() * r.width, ty = r.top + Math.random() * r.height; mote({ x0: Math.random() * Wd, y0: hzY + (Math.random() - .3) * Hd * .5, tx: tx, ty: ty, x: 0, y: 0, r: .7 + Math.random() * 1.3, l: 0, m: 50 + Math.random() * 40, c: Math.random() < .5 ? '255,244,220' : '255,210,150' }); }
      }
      G.style.setProperty('--glow', Math.min(1, P() * .8 + (doorO ? .4 : 0)).toFixed(3));
      if (t - tLore > 6500 * SLOW && phase < 4) { tLore = t; nextLore(); }
    }
    if (reduce && phase >= 2) staticCards();
    if (phase >= 4) { var dr = door.getBoundingClientRect(); if (dr.height) push.style.top = (dr.top + dr.height * .34).toFixed(1) + 'px'; }
    /* 路边的火：那一本书载好了才亮 */
    posts.forEach(function (o) { if (!o.el.classList.contains('on') && books[BOOKS[o.era][0]]) o.el.classList.add('on'); });
    drawMotes();
    requestAnimationFrame(frame);
  }

  /* ---------- 第五拍：门往里推开，千千万万粒小火，连成一片白，白退下去牌桌在那里 ---------- */
  function open(fast) {
    if (opened) return;
    if (lite) {      // 轻量的一路：点跳过就是当场让路（这一下是手势，顺手起声）
      opened = true; l0Res(); holdRes(); window.__tbPause = false;
      try { if (typeof window.__gateOpened === 'function') window.__gateOpened(); } catch (e) {}
      try { G.remove(); } catch (e) {}
      return;
    }
    opened = true; l0Res();
    try { if (typeof window.__gateOpened === 'function') window.__gateOpened(); } catch (e) {}
    try { window.dispatchEvent(new CustomEvent('aldran:gate-opened')); } catch (e) {}
    if (!doorO) { spawnDoor(ZSTOP); door.style.transition = 'opacity .25s'; }      // 跳过：门当场立起来
    door.classList.add('on'); G.classList.add('g-p4'); G.classList.add('g-p5');
    var S = (fast ? .55 : 1) * SLOW;
    var dr = door.getBoundingClientRect(), cx = dr.left + dr.width / 2, cy = dr.top + dr.height * .58;
    if (!dr.width) { cx = Wd / 2; cy = hzY; }
    var D_ = 3 * Math.max(Wd, Hd);
    white.style.cssText = 'left:' + (cx - D_ / 2).toFixed(0) + 'px;top:' + (cy - D_ / 2).toFixed(0) + 'px;width:' + D_ + 'px;height:' + D_ + 'px';
    var end = function () {
      holdRes(); window.__tbPause = false;
      cam.style.display = 'none';
      var an = white.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 1100 * SLOW, easing: 'cubic-bezier(.4,0,.2,1)', fill: 'forwards' });
      cv.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 1100 * SLOW, fill: 'forwards' });
      an.onfinish = function () { G.remove(); };
    };
    /* 减少动态效果：不开门、不冲，整个载入页淡掉，牌桌淡进来 */
    if (reduce) { holdRes(); window.__tbPause = false; G.style.transition = 'opacity .6s ease'; G.style.opacity = '0'; setTimeout(function () { G.remove(); }, 700); return; }
    /* 11-26 夜（用户：“最后推门的那一下门往内开，然后镜头缩近到门里如同一下子被吸到了门里面”）：
       一、两扇门照门轴往里（往门后）转开，门缝里的光涌出来；
       二、镜头沿着路往前推，前头慢、后头一下子快（像被吸进去），门框从画面四边飞出去，光粒往后拉成速度线；
       三、冲进门里的那一刻整屏是门里的光，接光粒、白、牌桌。整段两秒上下，跳过走快版。 */
    var ease = 'cubic-bezier(.5,0,.25,1)';      // 门重，先推得慢，推开了顺势荡进去
    door.querySelector('.lf').animate([{ transform: 'rotateY(0)' }, { transform: 'rotateY(72deg)' }], { duration: 950 * S, easing: ease, fill: 'forwards' });
    door.querySelector('.rt').animate([{ transform: 'rotateY(0)' }, { transform: 'rotateY(-72deg)' }], { duration: 950 * S, easing: ease, fill: 'forwards' });
    door.querySelector('.glow').animate([{ opacity: 0 }, { opacity: 1 }], { duration: 600 * S, easing: 'ease-in', fill: 'forwards' });
    soul.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 400 * S, delay: 380 * S, fill: 'forwards' });
    /* 门缝里先涌出一小股光粒 */
    for (var q = 0; q < (fast ? 120 : 220); q++) {
      var a0 = Math.random() * 6.2832, sp0 = .3 + Math.random() * 1.6;
      mote({ x: cx + (Math.random() - .5) * dr.width * .18, y: cy + (Math.random() - .5) * dr.height * .5, vx: Math.cos(a0) * sp0, vy: Math.sin(a0) * sp0 * .7, r: (.6 + Math.random() * 1.4) * Math.max(1, Hd / 900), l: 0, m: 40 + Math.random() * 40, g: -.003, c: Math.random() < .4 ? '255,255,255' : '255,232,190' });
    }
    /* 镜头往前冲：门（连路、景、火）一起往镜头这边挪，挪的快慢照被吸进去的样子——先慢慢起，后头一下子快 */
    var tD0 = now() + 380 * S, DUR = 1000 * S, z0 = doorO.z, zEnd = PER / u * .9, off0 = roadOff, last0 = z0;
    (function dolly() {
      if (!G.isConnected || cam.style.display === 'none') return;
      var k = Math.min(1, Math.max(0, (now() - tD0) / DUR)), e = k * k * k;
      var zt = z0 + (zEnd - z0) * e, dz = zt - last0; last0 = zt;
      if (dz > 0) {
        objs.forEach(function (o) { o.z += dz; place(o); });
        roadOff = (roadOff + dz * u) % (texH || 1e9); rtex.style.transform = 'translate3d(0,' + (roadOff - texH).toFixed(1) + 'px,0)';
        /* 速度线：从门心往四边拉，冲得越快越长越多 */
        var n = Math.floor((2 + e * 26) / SLOW + Math.random());
        for (var q = 0; q < n; q++) {
          var a = Math.random() * 6.2832, r0 = (20 + Math.random() * 120) * Math.max(1, Hd / 844), sp = (6 + Math.random() * 10) * (.4 + e * 2.2) * Math.max(1, Hd / 844);
          mote({ x: cx + Math.cos(a) * r0, y: cy + Math.sin(a) * r0, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, r: .6 + Math.random() * 1.2, l: 0, m: 18 + Math.random() * 14, g: 0, st: 1, c: Math.random() < .5 ? '255,250,236' : '255,220,170' });
        }
      }
      if (k < 1) requestAnimationFrame(dolly);
    })();
    (function run() { if (!G.isConnected || cv.style.display === 'none') return; drawMotes(); requestAnimationFrame(run); })();
    /* 冲进门里的那一刻整屏是门里的光：光从门心长开，赶在镜头穿过门框的时候铺满 */
    var wa = white.animate([{ opacity: 0, transform: 'scale(.05)' }, { opacity: .85, transform: 'scale(.35)', offset: .55 }, { opacity: 1, transform: 'scale(1)' }],
      { duration: 340 * S, delay: 1130 * S, easing: 'cubic-bezier(.6,0,.8,.6)', fill: 'forwards' });
    wa.onfinish = function () {
      /* 白里还有一层光粒慢慢散开（千千万万盏小火），再退下去见牌桌 */
      for (var q = 0; q < (fast ? 300 : 700); q++) {
        var a = Math.random() * 6.2832, rr = Math.random() * Math.max(Wd, Hd) * .5, sp = .2 + Math.random() * .9;
        mote({ x: Wd / 2 + Math.cos(a) * rr, y: Hd / 2 + Math.sin(a) * rr, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp, r: .8 + Math.random() * 1.8, l: 0, m: 40 + Math.random() * 50, g: -.002, c: Math.random() < .5 ? '255,214,150' : '255,190,120' });
      }
      setTimeout(end, 140 * S);
    };
  }
  G.addEventListener('click', function (e) { if (e.target === skip) return; if (onDoor) open(false); });
  skip.addEventListener('click', function (e) { e.stopPropagation(); open(true); });
  addEventListener('keydown', function (e) { if (!opened && (e.key === 'Enter' || e.key === ' ') && onDoor) open(false); });

  /* 本地验的时候用 */
  window.__gate = { alive: function () { return alive(); }, state: function () { return { phase: phase, P: +P().toFixed(3), p0: +(done0() / W0).toFixed(3), D: Math.round(D), v: Math.round(v), cards: nCard, objs: objs.length, door: doorO ? Math.round(doorO.z) : null, slow: slow, books: books, l2: Object.keys(got2).length + '/' + L2.length, opened: opened }; }, open: open, toDoor: toDoor };
  /* 11-27：卡住了就让路。一帧一帧在走就记一下；隔一秒看一回：
     帧停了四秒以上（页面在前台）、外壳接手八秒还没起步、走了二十四秒门还没出来就让门当场出来、四十秒还没到门前就拆。 */
  var lastFrame = now();
  document.addEventListener('visibilitychange', function () { lastFrame = now(); });
  function alive() {
    if (killed || opened) return true;
    var t = now();
    if (!document.hidden && t - lastFrame > 4000) return false;
    if (phase < 2 && t - T0 > 8000) return false;
    if (phase < 4 && t - T0 > 40000) return false;
    return true;
  }
  var dog = setInterval(function () {
    if (killed || opened || !G.isConnected) { clearInterval(dog); return; }
    if (!alive()) { clearInterval(dog); kill('卡住了'); return; }
    if (!lite && phase >= 2 && phase < 4 && !doorO && now() - t2 > 24000 * SLOW) { try { spawnDoor(ZSTOP); } catch (e) { kill('门出不来'); } }
  }, 1000);
  window.__gate = window.__gate || {};
  window.__gate.alive = alive;
  function liteRun() {
    G.classList.add('g-lite');
    reg0();
    var go = false;
    (function tick() {
      if (killed || opened) return;
      lastFrame = now();
      var t = now();
      if (!l0said && done0() >= W0) { l0said = true; l0Res(); }
      if (!go && ((l0said && t - T0 > 1200) || t - T0 > 6000)) {
        go = true; opened = true; l0Res(); holdRes(); window.__tbPause = false;
        G.style.transition = 'opacity .7s ease'; G.style.opacity = '0';
        setTimeout(function () { try { G.remove(); } catch (e) {} }, 800);
        return;
      }
      setTimeout(tick, 120);
    })();
  }
  try {
    if (lite) {
      liteRun();
    } else {
      layout(); addEventListener('resize', layout);
      loadArt(); reg0();
      requestAnimationFrame(frame);
    }
    if (Q.has('nogate')) { if (lite) kill('nogate'); else open(true); }
  } catch (err) {      // 载入页自己出了错，不能把牌桌拦住
    kill('出错：' + (err && err.message));
  }
})();
