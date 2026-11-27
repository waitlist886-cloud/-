/* 大图书馆（11-24，门面第二轮）：外壳和四本书共用的一份。照 底稿/门面/第二轮/样张_书架/ 那一本的做法扩成整座馆：
   圆厅（一圈拱门，正中长桌上摊着《万物的清点》，桌角一张借阅卡）→ 各厅各廊（一面面书架，书脊照那一厅的装帧）→ 抽出来、转到封面、翻开 →
   扉页（藏书票）、前言、目录、正文、后记、注脚。往前的廊抽不出来，往后的廊还没写成。地图室调世界之书（common/codex.js）翻到那一纪的地图。
   字在 common/data/lib/（共用/build_lib.py 出）：index.json 一开就取，一本书点开才取那一本的 <书键>.json。
   图在 common/assets/lib/（hall_pc、hall_m、wing_<厅>、spine_<厅>_<n>、cover_<厅>、paper_<纸>、plate、card、seal、maproom），没到的时候拿 library.css 画的顶着，到了自己换上。
   门面没有本地存储（日里介绍页的沙箱），读到哪、借阅卡都只在这一回打开里。
   用法：
     await Library.init({ vol, host, A, spoil: () => SPOIL, setSpoil, openMap: (纪) => Codex.open(纪, 'map'), onOpen, onClose });
     Library.open()（圆厅）；Library.open('moon'|'strife'|'bronze'|'maze'|厅键)（那一厅、那一廊）；Library.openBook(书键)；Library.close()；
     Library.isOpen()；Library.syncSpoil()（剧透开关在别处切了，叫它跟上）；Library.addPlayerBook({ name, title, era, vis, year, line, text, paper })（11-24 建档升级接上：铸印以后玩家那一本，往后的廊第二十一格、借阅卡最末一行）。 */
(function () {
  'use strict';
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const hash = (s) => { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967296; };
  const SEAL = '此处压着一枚青火印，开了剧透才揭得开';
  const SPL = '<button class="lb-spl" type="button" aria-label="剧透开关"><i></i><span>剧透　<em class="lx-off">关着</em><em class="lx-on">开着</em></span></button>';
  const ERA_NAME = { moon: '月银纪', strife: '纷争纪', bronze: '山铜纪', maze: '迷宫纪' };
  const MAP_LINE = { moon: '祭火、万兽、诸国、萨尔维斯', strife: '长垒一万一千年', bronze: '七城与九座', maze: '井口和两块大陆' };
  // 圆厅那一圈拱门，从左到右：四纪的廊排在正中（往前、四纪、往后），两边是各厅
  const RING = ['map', 'ming', 'shen', 'crown', 'past', 'moon', 'strife', 'bronze', 'maze', 'future', 'arcane', 'craft', 'stage', 'child'];
  const NUMC = ['〇', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
  const cnum = (n) => (n <= 10 ? NUMC[n] : n < 20 ? '十' + (n % 10 ? NUMC[n % 10] : '') : NUMC[Math.floor(n / 10)] + '十' + (n % 10 ? NUMC[n % 10] : ''));
  // 借阅卡上已经写了的几行（字叫水洇了，认不清）；最末一行空着
  const LEND = [['莉娅·维恩', '天亮以前', 1], ['托尔克', '长垒战报汇编', 1], ['埃尔德·冬', '佣兵碑拓本', 1], ['诺拉·赛弗', '公会委托存档', 1], ['米尔塔', '万物的清点', 1], ['（刮花了）', '天使叛书', 0]];

  let C = null, root = null, IDX = null, ready = null, opened = false, view = 'hall', curHall = null, mob = false;
  let hallEl, wingEl, mapEl, tipEl, toastEl, stageEl, readerEl, lendEl, slipEl, topBack, topTitle, topClose;
  const ASSET = {};
  let PCDN = null;
  /* 一张插图的地址：common/assets/lib/plates/<段>/<书键>_<n>.webp。外壳在图床上时（地址里有 gh/<仓库>@<提交>/），这一段换成插图那一段的提交号，镜像照外壳的 */
  function plateSrc(sg, k, n) {
    const p = 'common/assets/lib/plates/' + sg + '/' + k + '_' + n + '.webp';
    const u = absU(A(p)), c = PCDN && PCDN.parts && PCDN.parts[sg];
    if (!c || !/^[0-9a-f]{40}$/.test(c)) return u;
    const m = u.match(/^(.*\/gh\/[^/]+\/[^/@]+)@[0-9a-f]{40}\/(.*)$/);
    return m ? m[1] + '@' + c + '/' + m[2] : u;
  }
  const A = (p) => (C && C.A ? C.A(p) : p);
  const spoilOn = () => !!(C && C.spoil && C.spoil());
  const reduced = () => window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const src = (name) => A('common/assets/lib/' + name + '.webp');
  const absU = (u) => { try { return new URL(u, document.baseURI).href; } catch (e) { return u; } };
  const cssUrl = (name) => 'url("' + absU(src(name)).replace(/"/g, '%22') + '")';          // 写成整个地址：变量里的相对地址会照用它的那一份样式表去算
  /* 图有没有：index.json 的 assets 写着 assets/lib/ 里有哪几张（build_lib.py 照目录列的，图到了重跑一回就换上，不去取没有的、控制台里不报 404）；
     没有这一栏才去探。载得下来才换上，载不下来照旧用画的 */
  function asset(name) {
    if (!(name in ASSET)) ASSET[name] = (ready || Promise.resolve()).then(() => {
      if (IDX && IDX.assets && IDX.assets.indexOf(name) < 0) return false;
      return new Promise((res) => { const im = new Image(); im.onload = () => res(im.naturalWidth > 0); im.onerror = () => res(false); im.src = src(name); });
    });
    return ASSET[name];
  }
  const HALL = (k) => (IDX ? IDX.halls.find((h) => h.k === k) : null);

  /* ---------- 搭架子 ---------- */
  function build() {
    root = document.createElement('div');
    root.id = 'lib'; root.hidden = true;
    root.setAttribute('role', 'dialog'); root.setAttribute('aria-label', '大图书馆');
    root.innerHTML = '<div class="lb-v lb-hall"></div><div class="lb-v lb-wing" hidden></div><div class="lb-v lb-map" hidden></div>'
      + '<div class="lb-top"><button class="lb-btn lx-bk" type="button"><b>‹</b><span>回圆厅</span></button><span class="lx-sp"></span>' + SPL + '<button class="lb-btn lx-x" type="button"><b>×</b>出馆</button></div>'
      + '<div class="lb-tip"><div class="lx-n"></div><div class="lx-a"></div><div class="lx-e"></div><div class="lx-q"></div></div>'
      + '<div class="lb-stage" hidden><div class="lx-dim"></div><div class="lx-b3"><div class="lx-f lx-back"></div><div class="lx-f lx-spine"><span class="lx-spt"></span></div><div class="lx-f lx-front"><div class="lx-pages"></div><div class="lx-lid"><div class="lx-out"><div class="lx-covt"><b></b><i></i></div></div><div class="lx-in"></div></div></div></div></div>'
      + '<div class="lb-reader" hidden></div><div class="lb-lend" hidden></div><div class="lb-slip"></div><div class="lb-toast"></div>';
    const host = C.host || document.body;
    const wb = host.querySelector(':scope > #wb');          // 地图室翻世界之书：世界之书要盖在图书馆上面，排在它前头
    if (wb) host.insertBefore(root, wb); else host.appendChild(root);
    hallEl = root.querySelector('.lb-hall'); wingEl = root.querySelector('.lb-wing'); mapEl = root.querySelector('.lb-map');
    tipEl = root.querySelector('.lb-tip'); toastEl = root.querySelector('.lb-toast'); stageEl = root.querySelector('.lb-stage');
    readerEl = root.querySelector('.lb-reader'); lendEl = root.querySelector('.lb-lend'); slipEl = root.querySelector('.lb-slip');
    topBack = root.querySelector('.lb-top .lx-bk'); topClose = root.querySelector('.lb-top .lx-x');
    topBack.hidden = true;          // 11-25：书目还没取到、厅还没搭出来的那一会儿只留“出馆”一枚（原来这一枚先露着，那时候点它是出馆，对不上它写的字）
    topBack.addEventListener('click', () => { if (view === 'hall') close(); else showHall(); });
    topClose.addEventListener('click', () => close());
    root.querySelector('.lb-top .lb-spl').addEventListener('click', toggleSpoil);
    for (const ev of ['pointerdown', 'pointerup', 'pointermove', 'wheel', 'touchstart', 'touchmove', 'touchend', 'click', 'keyup']) root.addEventListener(ev, (e) => e.stopPropagation(), { passive: true });
    window.addEventListener('keydown', onKey, true);
    window.addEventListener('resize', onResize);
    lendEl.addEventListener('click', (e) => { if (e.target === lendEl || e.target.closest('.lx-x')) closeLend(); });
    slipEl.addEventListener('click', () => slipEl.classList.remove('lx-on'));
  }
  function toggleSpoil() { C.setSpoil(!spoilOn()); syncSpoil(); }
  function syncSpoil() {
    if (!root) return;
    root.classList.toggle('lx-spoil-on', spoilOn());
    if (RD.book && !readerEl.hidden) relayout(true);
  }
  function measure() { const r = root.getBoundingClientRect(); mob = r.width < 760; root.classList.toggle('lb-m', mob); return r; }
  let rsT = 0;
  function onResize() {
    if (!opened) return;
    clearTimeout(rsT);
    rsT = setTimeout(() => {
      const was = mob; measure(); hideTip();
      if (view === 'hall') buildHall(); else if (view === 'wing' && curHall) buildWing(curHall); else if (view === 'map') buildMap();
      if (RD.book && !readerEl.hidden) relayout(true, was !== mob);
    }, 120);
  }

  function init(cfg) {
    C = Object.assign({ vol: 'general', host: null, A: null, spoil: () => false, setSpoil: () => {}, openMap: () => {}, onOpen: () => {}, onClose: () => {} }, cfg || {});
    build();
    ready = fetch(A('common/data/lib/index.json')).then((r) => (r.ok ? r.json() : null)).catch(() => null).then((d) => { IDX = d; api.missing = !d; return api; });
    // 插图在图床上另放几段（deploy_front.py 推完写 common/data/plates_cdn.json：{repo, parts: {p1: 提交, …}}）；本地没有这一份，照相对地址取
    fetch(A('common/data/plates_cdn.json')).then((r) => (r.ok ? r.json() : null)).catch(() => null).then((d) => { PCDN = d; });
    ready.then(() => { for (const n of ['plate', 'card', 'seal']) asset(n); });          // 小的先载上
    return ready;
  }

  /* ---------- 开、合 ---------- */
  /* 11-26 夜 交互音效：外壳里调 window.__sfx，书那一格里调 SFX（发给外壳放） */
  const SND = (n) => { try { (window.__sfx || window.SFX || (() => {}))(n); } catch (e) { /* 没有音效 */ } };
  function open(where) {
    if (!root) return;
    C.onOpen(); root.hidden = false; opened = true; measure(); syncSpoil();
    SND('hall');          // 推门进厅
    requestAnimationFrame(() => root.classList.add('lx-on'));
    (ready || Promise.resolve()).then(() => {
      if (!IDX) { hallEl.innerHTML = '<div class="lb-cap"><h1>大图书馆</h1><p>这一回没有取到书目，合上再开一回试试</p></div>'; setView('hall'); return; }
      const k = typeof where === 'string' ? where : '';
      if (k && (HALL(k) || k === 'map')) { if (k === 'map') showMap(true); else showWing(k, true); }
      else if (where && where.book) { showHall(true); openBookKey(where.book, where.part); }
      else showHall(true);
    });
  }
  function close(fast) {
    if (!opened) return;
    hideTip(); closeLend(true); slipEl.classList.remove('lx-on');
    opened = false; root.classList.remove('lx-on');
    const done = () => { if (!opened) { root.hidden = true; readerEl.hidden = true; stageEl.hidden = true; RD.book = null; } };
    if (fast) done(); else setTimeout(done, 420);
    C.onClose();
  }
  function setView(v, from) {
    view = v;
    const els = { hall: hallEl, wing: wingEl, map: mapEl };
    for (const k in els) {
      const el = els[k];
      if (k === v) { el.hidden = false; el.classList.remove('lx-off', 'lx-zoom', 'lx-back'); }
      else if (!el.hidden) { el.classList.add(from && k === 'hall' ? 'lx-zoom' : 'lx-off'); setTimeout(() => { if (view !== k) el.hidden = true; }, reduced() ? 0 : 500); }
    }
    toastEl.classList.remove('lx-on');
    topBack.querySelector('span').textContent = v === 'hall' ? '出馆' : '回圆厅';
    topBack.hidden = v === 'hall';
    topClose.innerHTML = '<b>×</b>' + (v === 'hall' ? '出馆' : '出馆');
    hideTip();
  }

  /* ---------- 青火 ---------- */
  const flame = (x, y, fs) => '<span class="lb-fl" style="left:' + x + '%;top:' + y + '%;--fs:' + fs + 'px;animation-delay:' + (hash(x + ':' + y) * 3).toFixed(2) + 's"></span>';

  /* ---------- 圆厅 ---------- */
  function showHall(first) {
    curHall = null;
    buildHall();
    if (!first && !hallEl.hidden) { setView('hall'); return; }
    hallEl.classList.add('lx-back'); hallEl.hidden = false;
    setView('hall');
    hallEl.classList.add('lx-back'); requestAnimationFrame(() => requestAnimationFrame(() => hallEl.classList.remove('lx-back')));
  }
  /* 圆厅主画（hall_pc，1920×1081）上长桌和桌上那一本的位置，照画的比例记的（画换了要跟着量）：x0、y0、x1、y1 */
  const HALL_PC = { iw: 1920, ih: 1081, book: [0.414, 0.645, 0.586, 0.761], few: [0.300, 0.737], card: [0.668, 0.735] };
  const hasAsset = (n) => !!(IDX && IDX.assets && IDX.assets.indexOf(n) >= 0);
  function buildHall() {
    const r = measure(), W = r.width, H = r.height;
    const yuan = HALL('yuan'), table = yuan ? yuan.books : [];
    const main = table[0];
    const img = !mob && hasAsset('hall_pc');
    // 画铺满（cover，竖着照 42% 对齐）以后，画上一点在屏上哪里
    const sc = Math.max(W / HALL_PC.iw, H / HALL_PC.ih), ox = (W - HALL_PC.iw * sc) / 2, oy = (H - HALL_PC.ih * sc) * 0.42;
    const at = (fx, fy) => [ox + fx * HALL_PC.iw * sc, oy + fy * HALL_PC.ih * sc];
    hallEl.classList.toggle('lx-plq', img);
    let h = '<div class="lx-bg"></div><div class="lx-dome"></div>';
    if (!mob && !img) for (const [x, y] of [[8, 30], [20, 36], [33, 40], [67, 40], [80, 36], [92, 30]]) h += flame(x, y, 20);
    h += '<div class="lb-cap"><h1>久远与无垠的大图书馆</h1><p>每一纪写下的，都收在这里。直到终点以前</p></div>';
    h += '<div class="lb-arches">';
    const n = RING.length;
    RING.forEach((k, i) => {
      const hl = k === 'map' ? null : HALL(k);
      if (k !== 'map' && !hl) return;
      const name = k === 'map' ? '地图室' : hl.n;
      const sub = k === 'map' ? '四纪各一张地图' : k === 'past' ? '三纪十二本，都烫手' : k === 'future' ? cnum(hl.count - 1) + '格，最末一格空着' : cnum(hl.count) + '本';
      let st = '';
      if (!mob) {
        // 一圈拱门排成一道弧，正中最远（小、高），两边近；间距一样，不叠
        const t = i / (n - 1), x = 6 + t * 88, depth = Math.sin(Math.PI * t);
        const gap = W * 0.88 / (n - 1);
        if (img) {          // 有主画：画上自己有拱门，这里挂一圈名牌
          // 11-25：屏窄到一圈名牌挤不下（间距不到 100px，约 1590 宽以下：笔记本、平板横竖都算），名牌错成上下两排，单数那几块往下挪一块牌子高，
          // 一块牌子就能宽到两格。原来照旧一排，名字是不折行的，820 宽的时候一块名牌的字压在左右两块上，边上点着的是隔壁那一块
          const two = gap < 100, y = 28.5 - depth * 3.2;
          const pw = two ? Math.min(gap * 1.7, 140) : Math.min(gap * 0.9, 150);
          const top = two && i % 2 ? 'calc(' + y.toFixed(2) + '% + 80px)' : y.toFixed(2) + '%';
          const left = two ? clamp(W * x / 100, pw / 2 + 8, W - pw / 2 - 8).toFixed(1) + 'px' : x.toFixed(2) + '%';          // 两头那两块别伸出屏
          st = ' style="left:' + left + ';top:' + top + ';--pw:' + pw.toFixed(1) + 'px"';
        } else {
          const aw = Math.min(clamp(W * (0.045 + (1 - depth) * 0.02), 50, 124) * clamp(H / 945, 0.7, 1.2), gap * 0.6);
          st = ' style="left:' + x.toFixed(2) + '%;top:' + (60 - depth * 9).toFixed(2) + '%;--aw:' + aw.toFixed(1) + 'px;z-index:' + Math.round((1 - depth) * 10) + '"';
        }
      }
      const cls = 'lb-arch' + (k === 'past' ? ' lx-hot' : k === 'future' ? ' lx-blank' : k === 'map' ? ' lx-map' : '');
      h += '<button type="button" class="' + cls + '" data-k="' + k + '"' + st + ' aria-label="' + esc(name) + '"><span class="lx-col lx-l"></span><span class="lx-col lx-r"></span><span class="lx-ky"></span><span class="lx-door">' + flame(50, 40, 12) + '</span><span class="lx-nm">' + esc(name) + '</span><span class="lx-cnt">' + esc(sub) + '</span><span class="lx-sub">' + esc(sub + '　' + (k === 'map' ? '点一张，翻到那一纪的地图' : hl.line)) + '</span></button>';
    });
    h += '</div>';
    const px = (v) => v.toFixed(1) + 'px';
    let bst = '', fst = '', cst = '', bh = 96;
    if (img) {          // 桌和书是画上的：那一本只留一块指得着的地方，几本小书立在桌面左边，借阅卡压在右边
      const [x0, y0] = at(HALL_PC.book[0], HALL_PC.book[1]), [x1, y1] = at(HALL_PC.book[2], HALL_PC.book[3]);
      bst = ' style="position:absolute;left:' + px(x0) + ';top:' + px(y0) + ';width:' + px(x1 - x0) + ';height:' + px(y1 - y0) + ';bottom:auto;transform:none"';
      const [fx, fy] = at(HALL_PC.few[0], HALL_PC.few[1]); bh = 100 * sc;
      fst = ' style="position:absolute;left:' + px(fx) + ';top:' + px(fy) + ';bottom:auto;transform:translateY(-100%)"';
      const [cx, cy] = at(HALL_PC.card[0], HALL_PC.card[1]);
      cst = ' style="position:absolute;left:' + px(cx) + ';top:' + px(cy) + ';right:auto;bottom:auto;width:' + px(78 * sc) + ';height:' + px(108 * sc) + ';margin-top:' + px(-108 * sc) + '"';
    }
    const tb = '<div class="lb-table"' + (img ? ' style="inset:0;left:0;bottom:0;width:auto;height:auto;transform:none;pointer-events:none"' : '') + '><div class="lx-top"></div><div class="lx-edge"></div><div class="lx-leg lx-l"></div><div class="lx-leg lx-r"></div>';
    h += tb;
    if (main) h += '<button type="button" class="lb-open' + (img ? ' lx-spot' : '') + '" data-b="' + main.k + '" aria-label="' + esc(main.t) + '"' + bst + '><span class="lx-pg lx-l"></span><span class="lx-pg lx-r"></span>' + flame(50, -8, 22) + '<span class="lx-t">' + esc(main.t) + '</span></button>';
    h += '<div class="lb-few"' + fst + '>' + table.slice(1).map((b, j) => spineHTML('yuan', b, j + 1, mob ? 0 : bh + hash(b.k) * bh * 0.27, mob ? 0 : Math.round((22 + hash(b.t) * 8) * (img ? sc * 1.1 : 1)))).join('') + '</div>';
    h += '<button type="button" class="lb-card" aria-label="借阅卡"' + cst + '><span class="lx-pp"></span><span class="lx-mini"><b>借阅卡</b><i></i><i></i><i></i><i></i><i></i><i></i></span></button></div>';
    hallEl.innerHTML = h;
    hallEl.classList.toggle('lx-scroller', mob);
    if (mob) { const tb = hallEl.querySelector('.lb-table'); hallEl.insertBefore(tb, hallEl.querySelector('.lb-arches')); }
    asset(mob ? 'hall_m' : 'hall_pc').then((ok) => { if (ok) { hallEl.classList.add('lx-has-img'); hallEl.style.setProperty('--img', cssUrl(mob ? 'hall_m' : 'hall_pc')); } });
    asset('card').then((ok) => { if (ok) root.style.setProperty('--card', cssUrl('card')); });
    applySpines(hallEl, 'yuan');
    hallEl.querySelectorAll('.lb-arch').forEach((el) => {
      const k = el.dataset.k, hl = HALL(k);
      const tipOf = () => (k === 'map' ? { n: '地图室', a: '一张摊开的地图桌，四纪各一张', e: '点一张，翻到那一纪的地图' }
        : { n: hl.n, a: hl.line, e: k === 'past' ? '衔枝纪、赤金纪、葬火纪，十二本，抽不出来' : k === 'future' ? cnum(hl.count - 1) + '格书脊，最末一格空着' : cnum(hl.count) + '本', cls: k === 'past' ? 'hot' : k === 'future' ? 'white' : '' });
      el.addEventListener('mouseenter', () => showTip(tipOf())); el.addEventListener('focus', () => showTip(tipOf()));
      el.addEventListener('mouseleave', hideTip); el.addEventListener('blur', hideTip);
      el.addEventListener('click', () => { hideTip(); zoomFrom(el); if (k === 'map') showMap(); else showWing(k); });
    });
    const ob = hallEl.querySelector('.lb-open');
    if (ob) {
      const tipM = () => showTip({ n: main.t, a: main.a, e: main.y });
      ob.addEventListener('mouseenter', tipM); ob.addEventListener('focus', tipM); ob.addEventListener('mouseleave', hideTip); ob.addEventListener('blur', hideTip);
      ob.addEventListener('click', () => openBook(main, ob, 'yuan'));
    }
    bindSpines(hallEl, 'yuan', table.slice(1));
    const cd = hallEl.querySelector('.lb-card');
    cd.addEventListener('mouseenter', () => showTip({ n: '借阅卡', a: '借书的人一行一行往下写，最末一行空着', e: '长桌一角' }));
    cd.addEventListener('mouseleave', hideTip);
    cd.addEventListener('click', openLend);
  }
  function zoomFrom(el) {
    if (mob || reduced()) return;
    const r = el.getBoundingClientRect(), R = root.getBoundingClientRect();
    hallEl.style.transformOrigin = ((r.left + r.width / 2 - R.left) / R.width * 100).toFixed(1) + '% ' + ((r.top + r.height / 2 - R.top) / R.height * 100).toFixed(1) + '%';
  }

  /* ---------- 书脊 ---------- */
  const shortY = (y) => { const t = String(y || '').split(/[，。（(]/)[0]; return t.slice(0, 16); };          // 手机上书脊右边那一小格只写成书的头一截
  function spineW(b) { return Math.round(clamp(26 + Math.sqrt(b.n || 9000) * 0.17, 34, 72)); }
  function spineHTML(hk, b, j, h, w, extra) {
    const v = Math.floor(hash(b.k) * 3);
    const set = b.parts ? b.parts : null;
    const t = b.st || b.t;
    const fz = t.length > 12 ? 11 : t.length > 8 ? 12 : 12.5;
    return '<button type="button" class="lb-sp' + (extra || '') + '" data-h="' + hk + '" data-n="' + v + '" data-b="' + esc(b.k) + '"' + (b.pi != null ? ' data-pi="' + b.pi + '"' : '')
      + ' style="--h:' + Math.round(h) + 'px;--w:' + w + 'px;--fz:' + fz + 'px;--ty:' + (12 + Math.round(hash(b.t + 'y') * 8)) + '%" aria-label="' + esc(b.t) + '">'
      + '<span class="lx-rot"></span><span class="lx-t">' + esc(t) + '</span>' + (b.pl ? '<span class="lx-pt">' + esc(b.pl) + '</span>' : '') + '<span class="lx-m">' + esc(shortY(b.y)) + '</span></button>';
  }
  function applySpines(scope, hk) {
    const els = Array.from(scope.querySelectorAll('.lb-sp[data-h="' + hk + '"]:not(.lx-hot):not(.lx-white):not(.lx-slot):not(.lx-deep)'));
    if (!els.length) return;
    Promise.all([1, 2, 3, 4].map((n) => asset('spine_' + hk + '_' + n))).then((oks) => {
      const have = [1, 2, 3, 4].filter((n, i) => oks[i]);
      if (!have.length) return;
      els.forEach((el, i) => { const n = have[(+el.dataset.n + i) % have.length]; el.style.setProperty('--sk', cssUrl('spine_' + hk + '_' + n)); el.classList.add('lx-img'); el.style.setProperty('--rw', (Math.round(root.clientWidth) - 32) + 'px'); });
    });
  }
  function bindSpines(scope, hk, books) {
    scope.querySelectorAll('.lb-sp[data-b]').forEach((el) => {
      const b = books.find((x) => x.k === el.dataset.b);
      if (!b) return;
      const part = el.dataset.pi != null ? +el.dataset.pi : null;
      const tp = () => showTip({ n: b.t + (part != null ? '　' + b.parts[part] : ''), a: b.a, e: [b.y, b.set ? (IDX.sets || {})[b.set] + '，第' + cnum(b.seq) + '本' : ''].filter(Boolean).join('　') });
      el.addEventListener('mouseenter', tp); el.addEventListener('focus', tp);
      el.addEventListener('mouseleave', hideTip); el.addEventListener('blur', hideTip);
      el.addEventListener('click', () => openBook(b, el, hk, part));
    });
  }

  /* ---------- 一厅一廊 ---------- */
  function showWing(k, first) {
    curHall = k;
    if (!first) SND('hall');          // 从圆厅推门进这一厅
    buildWing(k);
    wingEl.classList.add('lx-back'); wingEl.hidden = false;
    setView('wing', !first);
    requestAnimationFrame(() => requestAnimationFrame(() => wingEl.classList.remove('lx-back')));
  }
  function buildWing(k) {
    const hl = HALL(k), r = measure();
    if (!hl) return;
    wingEl.dataset.h = k;
    let h = '<div class="lx-bg"></div>';
    if (!mob) h += '<div class="lx-pil lx-l">' + flame(50, 24, 26) + '</div><div class="lx-pil lx-r">' + flame(50, 24, 26) + '</div>';
    h += '<div class="lb-whead"><h2>' + esc(hl.n) + '</h2><p>' + esc(hl.line) + '</p>';
    if (k === 'past') h += '<p class="lx-sub">' + hl.past.intro.slice(0, 1).join('') + '</p>';
    if (k === 'future') h += '<p class="lx-sub">' + hl.future.intro.slice(0, 1).join('') + '</p>';
    h += '</div><div class="lb-shelves"></div>';
    wingEl.innerHTML = h;
    wingEl.classList.toggle('lx-scroller', mob);
    const shel = wingEl.querySelector('.lb-shelves');
    const SW = r.width * 0.84, SH = r.height - Math.max(54, r.height * 0.065) - 96 - r.height * 0.15;
    if (k === 'past') shel.innerHTML = pastHTML(hl, SW, SH);
    else if (k === 'future') shel.innerHTML = futureHTML(hl, SW, SH);
    else shel.innerHTML = shelfHTML(k, hl.books, SW, SH);
    asset('wing_' + k).then((ok) => { if (ok && curHall === k) { wingEl.classList.add('lx-has-img'); wingEl.style.setProperty('--img', cssUrl('wing_' + k)); } });
    if (k === 'past') bindPast(hl);
    else if (k === 'future') bindFuture(hl);
    else { applySpines(wingEl, k); bindSpines(wingEl, k, hl.books); }
  }
  /* 书排成几层：成套的挨着放（971 三册、大兽志五本、两本神谱）。一层放不下就分两三层 */
  function shelfHTML(k, books, SW, SH) {
    const items = [];
    for (let i = 0; i < books.length; i++) {
      const b = books[i];
      if (b.parts) { items.push({ g: b.t.split('：')[0], list: b.parts.map((p, j) => Object.assign({}, b, { st: b.t.split('：')[0], pl: p.slice(0, 1), pi: j, n: (b.n || 30000) / b.parts.length })) }); continue; }
      if (b.set) {
        const ms = books.filter((x) => x.set === b.set);
        if (ms[0] === b) items.push({ g: (IDX.sets || {})[b.set] + '　' + cnum(ms.length) + '本', list: ms.map((x) => Object.assign({}, x, { st: x.t.replace(/^.*?·/, '') })) });
        continue;
      }
      items.push({ list: [b] });
    }
    if (mob) return '<div class="lb-row">' + items.map((it) => (it.g ? '<div class="lb-grp"><span class="lx-gl">' + esc(it.g) + '</span>' : '') + it.list.map((b) => spineHTML(k, b, 0, 56, 0)).join('') + (it.g ? '</div>' : '')).join('') + '</div>';
    const wOf = (it) => it.list.reduce((s, b) => s + spineW(b) + 5, 0) + (it.g ? 16 : 0);
    const total = items.reduce((s, it) => s + wOf(it), 0);
    let rows = clamp(Math.ceil(total / SW), 1, 3);
    if (rows === 1 && books.length > 13 && SH > 520) rows = 2;
    const target = total / rows, R = [[]];
    let acc = 0;
    for (const it of items) { const w = wOf(it); if (acc > 0 && acc + w / 2 > target && R.length < rows) { R.push([]); acc = 0; } R[R.length - 1].push(it); acc += w; }
    const rgap = R.length > 1 ? 52 : 0;
    const rowH = (SH - rgap * (R.length - 1)) / R.length;
    const widest = Math.max(...R.map((row) => row.reduce((s, it) => s + wOf(it), 0)));
    const shrink = widest > SW ? SW / widest : Math.min(1.45, SW * 0.62 / widest, Math.max(1, (R.length > 1 ? 300 : 380) / 260));          // 书少的一层放宽一些，别挤在当中
    const hb = clamp(rowH - 8, 150, R.length > 1 ? 300 : 380);
    wingEl.style.setProperty('--rowh', Math.round(rowH + rgap) + 'px');
    let out = '';
    for (const row of R) {
      out += '<div class="lb-row" style="--sh:' + Math.round(hb) + 'px">';
      for (const it of row) {
        if (it.g) out += '<div class="lb-grp"><span class="lx-gl">' + esc(it.g) + '</span>';
        for (const b of it.list) out += spineHTML(k, b, 0, hb * (0.8 + hash(b.k + (b.pi || '')) * 0.2), Math.round(spineW(b) * shrink));
        if (it.g) out += '</div>';
      }
      out += '</div>';
    }
    root.style.setProperty('--rgap', rgap + 'px');
    return out;
  }
  /* 往前的廊：书脊烫着字，指上去浮那一两句，点了抖一下抽不出来 */
  function pastHTML(hl, SW, SH) {
    const P = hl.past, hb = mob ? 56 : clamp(SH - 30, 180, 330);
    // 11-25：屏窄了（约 1200 宽以下）一排放不下，原来照旧一排居中，两头的书伸出屏外、点不着（820 宽的时候最外头一纪的书整个在屏外）。
    // 放不下就把书脊照比例收窄（至多收到五成五），还不够就不摆“再往里”那几本
    const bw = (b) => 46 + hash(b.t + 'w') * 18, dw = (i) => 40 + Math.round(hash('w' + i) * 16);
    const need = (f, deep) => P.eras.reduce((s, era) => s + era.books.reduce((a, b) => a + Math.round(bw(b) * f) + 5, 0) + 49, 0)
      + (deep ? [0, 1, 2, 3, 4].reduce((a, i) => a + Math.round(dw(i) * f) + 5, 0) + 49 : 0);
    let fit = 1, deep = !mob;
    if (!mob && need(1, true) > SW) {
      fit = Math.max(0.55, SW / need(1, true));
      if (need(fit, true) > SW) { deep = false; fit = Math.max(0.55, Math.min(1, SW / need(1, false))); }
    }
    let out = '<div class="lb-row" style="--sh:' + Math.round(hb) + 'px">';
    P.eras.forEach((era, ei) => {
      out += '<div class="lb-era"><span class="lx-gl">' + esc(era.n) + '</span>';
      era.books.forEach((b, bi) => {
        const hh = mob ? 56 : hb * (0.84 + hash(b.t) * 0.16), w = mob ? 0 : Math.round(bw(b) * fit);
        out += '<button type="button" class="lb-sp lx-hot" data-h="past" data-e="' + ei + '" data-i="' + bi + '" style="--h:' + Math.round(hh) + 'px;--w:' + w + 'px;--hy:' + Math.round(30 + hash(b.t) * 40) + '%" aria-label="' + esc(b.t) + '"><span class="lx-ember"></span><span class="lx-t">' + esc(b.t) + '</span><span class="lx-hint">' + esc(strip(b.touch || '')) + '</span></button>';
      });
      out += '</div>';
    });
    if (deep) { out += '<div class="lb-era"><span class="lx-gl">再往里</span>'; for (let i = 0; i < 5; i++) out += '<span class="lb-sp lx-deep" style="--h:' + Math.round(hb * (0.8 + hash('d' + i) * 0.2)) + 'px;--w:' + Math.round(dw(i) * fit) + 'px;opacity:' + (0.4 - i * 0.07).toFixed(2) + '"></span>'; out += '</div>'; }
    return out + '</div>' + (mob && P.deeper ? '<p class="lb-whead"><span class="lx-sub">' + P.deeper + '</span></p>' : '');
  }
  const strip = (h) => String(h).replace(/<[^>]+>/g, '');
  function bindPast(hl) {
    wingEl.querySelectorAll('.lb-sp.lx-hot').forEach((el) => {
      const era = hl.past.eras[+el.dataset.e], b = era.books[+el.dataset.i];
      const tp = () => showTip({ n: '《' + b.t + '》', a: strip(b.touch || ''), e: b.fly ? '书口松了一线，扉页上只读得到一行：' + strip(b.fly) : era.n + '　抽不出来', q: (b.qn || []).map(strip).join('　'), cls: 'hot' });
      el.addEventListener('mouseenter', tp); el.addEventListener('focus', tp); el.addEventListener('mouseleave', hideTip); el.addEventListener('blur', hideTip);
      el.addEventListener('click', () => { el.classList.remove('lx-shake'); void el.offsetWidth; el.classList.add('lx-shake'); toast(strip(b.hot || '书脊是烫的，抽不出来。'), 'hot'); });
    });
  }
  /* 往后的廊：书脊越往里越白，第二十一格“的旅印”前头空着名字，最末一格空着 */
  const FUT_LABEL = { 第十格: '第　次远征记', 第十一格: '金鸢', 第十四格: '春', 第十九格: '·', 第二十一格: '' };
  function futureHTML(hl, SW, SH) {
    const S = hl.future.slots, n = S.length;
    const rows = mob ? 1 : (n * 50 > SW ? 2 : 1);
    const per = Math.ceil(n / rows);
    const hb = mob ? 56 : clamp((SH - (rows - 1) * 52) / rows - 8, 150, 330);
    wingEl.style.setProperty('--rowh', Math.round(hb + 60) + 'px');
    root.style.setProperty('--rgap', rows > 1 ? '52px' : '0px');
    let out = '';
    for (let r = 0; r < rows; r++) {
      out += '<div class="lb-row" style="--sh:' + Math.round(hb) + 'px">';
      S.slice(r * per, (r + 1) * per).forEach((s, jj) => {
        const i = r * per + jj, m = /《([^》]+)》/.exec(strip(s.h));
        let label = m ? m[1] : (FUT_LABEL[s.n] != null ? FUT_LABEL[s.n] : '');
        const gold = Math.max(0, 0.95 - i * 0.042), hh = mob ? 56 : hb * (0.96 - i * 0.004 - hash(s.n) * 0.08), w = mob ? 0 : Math.round(clamp(54 - i * 1.2, 22, 54));
        if (s.last) { out += '<button type="button" class="lb-sp lx-slot" data-s="' + i + '" style="--h:' + Math.round(hb * 0.92) + 'px;--w:58px" aria-label="最末一格"><span class="lx-t">空着</span></button>'; return; }
        const pl = s.n === '第二十一格' ? lastPlayer() : null;          // 玩家铸了印，这一格烫上他的名字
        const lab = s.n === '第二十一格' ? (pl ? '<b class="lx-mine">' + esc(pl.name) + '</b>的旅印' : '<i class="lx-blank"></i>的旅印') : esc(label);
        out += '<button type="button" class="lb-sp lx-white" data-h="future" data-s="' + i + '" style="--h:' + Math.round(hh) + 'px;--w:' + w + 'px;--gold:' + gold.toFixed(2) + ';opacity:' + clamp(1 - i * 0.022, 0.45, 1).toFixed(2) + '" aria-label="' + esc(s.n) + '">' + (lab ? '<span class="lx-t">' + lab + '</span>' : '') + '<span class="lx-m">' + esc(s.n) + '</span></button>';
      });
      out += '</div>';
    }
    return out;
  }
  function bindFuture(hl) {
    wingEl.querySelectorAll('.lb-sp[data-s]').forEach((el) => {
      const s = hl.future.slots[+el.dataset.s];
      const pl = s.n === '第二十一格' ? lastPlayer() : null;
      if (pl) {          // 玩家自己那一本：抽得出来，翻得开
        el.classList.add('lx-mine');
        const meta = PBOOK[pl.k];
        const tp = () => showTip({ n: meta.t, a: '若娜瓦的殿里铸的印，翻开第一页是凭证', e: meta.y });
        el.addEventListener('mouseenter', tp); el.addEventListener('focus', tp); el.addEventListener('mouseleave', hideTip); el.addEventListener('blur', hideTip);
        el.addEventListener('click', () => openBook(meta, el, 'future'));
        return;
      }
      const tp = () => showTip({ n: s.n, a: strip(s.h), e: s.last ? '' : '还没写成', q: s.qn ? strip(s.qn) : '', cls: 'white' });
      el.addEventListener('mouseenter', tp); el.addEventListener('focus', tp); el.addEventListener('mouseleave', hideTip); el.addEventListener('blur', hideTip);
      el.addEventListener('click', () => toast(s.last ? '这一格空着。' : '这一本还没写成，抽出来是白的。'));
    });
  }

  /* ---------- 地图室 ---------- */
  function showMap(first) {
    curHall = null; buildMap();
    mapEl.classList.add('lx-back'); mapEl.hidden = false;
    setView('map', !first);
    requestAnimationFrame(() => requestAnimationFrame(() => mapEl.classList.remove('lx-back')));
  }
  function buildMap() {
    measure();
    let h = '<div class="lx-bg"></div><div class="lb-whead"><h2>地图室</h2><p>一张摊开的地图桌，四纪各一张</p></div><div class="lb-mtable">';
    ['moon', 'strife', 'bronze', 'maze'].forEach((v, i) => {
      h += '<button type="button" class="lb-mc" data-v="' + v + '" style="--r:' + ((i % 2 ? 1 : -1) * (1 + i * 0.6)).toFixed(1) + 'deg"><img alt="" src="' + esc(A('common/assets/ui/emblem_' + v + '.webp')) + '" onerror="this.remove()"><b>' + ERA_NAME[v] + '</b><span>' + esc(MAP_LINE[v]) + '</span></button>';
    });
    h += '</div><p class="lx-note">点一张，翻到世界之书里那一纪的地图。合上地图，还在这一间</p>';
    mapEl.innerHTML = h;
    mapEl.classList.toggle('lx-scroller', mob);
    asset('maproom').then((ok) => { if (ok) { mapEl.classList.add('lx-has-img'); mapEl.querySelector('.lb-mtable').classList.add('lx-has-img'); mapEl.style.setProperty('--img', cssUrl('maproom')); } });
    mapEl.querySelectorAll('.lb-mc').forEach((el) => el.addEventListener('click', () => C.openMap(el.dataset.v)));
  }

  /* ---------- 签、提示 ---------- */
  function showTip(o) {
    if (mob) return;
    const [n, a, e, q] = tipEl.children;
    tipEl.className = 'lb-tip lx-on' + (o.cls ? ' lx-' + o.cls : '');
    n.textContent = o.n || ''; a.textContent = o.a || ''; e.textContent = o.e || ''; q.textContent = o.q || ''; q.hidden = !o.q;
  }
  function hideTip() { if (tipEl) tipEl.classList.remove('lx-on'); }
  let toastT = 0;
  function toast(t, cls) { toastEl.textContent = t; toastEl.className = 'lb-toast lx-on' + (cls ? ' lx-' + cls : ''); clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('lx-on'), 2600); }

  /* ---------- 借阅卡 ---------- */
  function openLend() {
    hideTip();
    lendEl.innerHTML = '<div class="lx-lc"><button class="lx-x" type="button">放回去</button><h3>借阅卡</h3><div class="lx-sub">这一馆的书，不出这一殿</div>'
      + '<table><thead><tr><th style="width:34%">借书的人</th><th>借去的</th><th style="width:20%">还了没有</th></tr></thead><tbody>'
      + LEND.map((r) => '<tr><td class="lx-sm">' + esc(r[0]) + '</td><td>' + esc(r[1]) + '</td><td><span class="lx-ret' + (r[2] ? '' : ' lx-no') + '">' + (r[2] ? '已还' : '未还') + '</span></td></tr>').join('')
      + PLAYER.map((p) => '<tr><td>' + esc(p.name) + '</td><td>' + esc(p.book || '') + '</td><td></td></tr>').join('')
      + '<tr class="lx-empty"><td></td><td></td><td></td></tr></tbody></table><div class="lx-foot"><span>最末一行，还空着</span><b>已清点</b></div></div>';
    lendEl.hidden = false; requestAnimationFrame(() => requestAnimationFrame(() => lendEl.classList.add('lx-on')));
  }
  function closeLend(fast) { if (lendEl.hidden) return; lendEl.classList.remove('lx-on'); setTimeout(() => { lendEl.hidden = true; }, fast || reduced() ? 0 : 360); }
  /* 玩家自己那一本（11-24 建档升级接上）：铸印以后外壳调 addPlayerBook({ name, title, era, vis, year, line, text, paper })。
     往后的廊第二十一格“的旅印”前头烫上名字，点开能翻，翻开第一页就是凭证；借阅卡最末一行写上他。门面没有本地存储，只在这一回打开里有。 */
  const PLAYER = [], PBOOK = {};
  function addPlayerBook(o) {
    if (!o || !o.text) return null;
    const k = 'player_' + (PLAYER.length + 1), name = String(o.name || '无名'), t = o.title || name + '的旅印';
    const blocks = String(o.text).split('\n').filter((l) => l.trim()).map((l, i) => {
      const m = l.match(/^(【[^】]+】)(.*)$/);
      if (i === 0) return { k: 'p', h: '<b>' + esc(l) + '</b>' };
      if (m && !m[2]) return { k: 'h3', h: esc(m[1].replace(/[【】]/g, '')) };
      return { k: 'p', h: esc(l) };
    });
    PBOOK[k] = { k, t, a: name, y: [o.era, o.year].filter(Boolean).join(' '), paper: o.paper || 'print', player: 1, tocAt: 99,
      fly: [['h', esc(t)], ['p', esc([o.era, o.year].filter(Boolean).join(' ') + (o.line ? '　' + o.line : ''))], ['p', '若娜瓦的殿里铸的印']],
      secs: [{ t: '建档凭证', b: blocks }], notes: {} };
    PLAYER.push({ k, name, book: t, era: o.era || '', vis: o.vis || '' });
    if (opened && view === 'wing' && curHall === 'future') buildWing('future');
    return k;
  }
  const lastPlayer = () => PLAYER[PLAYER.length - 1] || null;

  /* ---------- 抽出来、转到封面、翻开 ---------- */
  const RD = { book: null, meta: null, hall: '', pages: [], pi: 0, spread: 0, spreads: 1, mode: 'page', src: null, lay: null };
  let busy = false;
  function bookDims() {
    const R = root.getBoundingClientRect();
    const H = mob ? Math.min(R.height * 0.6, 520) : Math.min(R.height * 0.72, 660);
    const W = Math.round(H * 0.68), T = Math.round(W * 0.16);
    return { W, H: Math.round(H), T, R };
  }
  function fromSpine(el, d) {
    const r = el.getBoundingClientRect(), R = d.R;
    const cx = r.left + r.width / 2 - R.left - R.width / 2, cy = r.top + r.height / 2 - R.top - R.height / 2;
    const P = 2400, z = d.W / 2;
    if (el.classList.contains('lb-open')) return 'translate(' + cx + 'px,' + cy + 'px) scale(' + (r.width / d.W * 0.55).toFixed(3) + ') rotateX(50deg) rotateY(0deg)';
    if (mob && el.classList.contains('lb-sp')) { const s = r.width / d.H * (P - z) / P; return 'translate(' + cx + 'px,' + cy + 'px) scale(' + s.toFixed(3) + ') rotateZ(-90deg) rotateY(90deg)'; }
    const s = r.height / d.H * (P - z) / P;
    return 'translate(' + cx + 'px,' + cy + 'px) scale(' + s.toFixed(3) + ') rotateZ(0deg) rotateY(90deg)';
  }
  /* 动画：页面在后台、动画不走的时候 finished 不来，多等一会儿照样往下走，别卡在半路 */
  function anim(el, frames, ms, easing) {
    if (reduced()) ms = 1;
    const an = el.animate(frames, { duration: ms, easing: easing || 'cubic-bezier(.2,.7,.2,1)', fill: 'forwards' });
    return Promise.race([an.finished ? an.finished.catch(() => {}) : new Promise(() => {}), new Promise((r) => setTimeout(r, ms + 250))])      // 11-27：老内核（Chrome 84 以前）没有 finished，只等时间.then(() => { try { an.finish(); } catch (e) { /* 已经取消了 */ } });
  }
  const fetchBook = (k) => (PBOOK[k] ? Promise.resolve(PBOOK[k]) : fetch(A('common/data/lib/' + k + '.json')).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); }));
  function dress(el, hk, v, meta) {          // 照书脊那一格的颜色和花纹，封面也是这一套
    el.dataset.h = hk; el.dataset.n = v;
    const probe = document.createElement('span'); probe.className = 'lb-sp'; probe.dataset.h = hk; probe.dataset.n = v; probe.style.display = 'none'; root.appendChild(probe);
    const cs = getComputedStyle(probe), pal = {};
    for (const p of ['--c1', '--c2', '--tc', '--pat']) pal[p] = cs.getPropertyValue(p).trim();
    probe.remove();
    for (const p in pal) if (pal[p]) el.style.setProperty(p, pal[p]);
    return pal;
  }
  function openBookKey(k, part) {
    if (!IDX) return;
    for (const h of IDX.halls) { const b = (h.books || []).find((x) => x.k === k); if (b) { openBook(b, null, h.k, part); return; } }
  }
  async function openBook(meta, el, hk, part) {
    if (busy) return; busy = true; hideTip();
    SND('draw_book');          // 从架上抽书
    const b3 = stageEl.querySelector('.lx-b3'), d = bookDims(), v = Math.floor(hash(meta.k) * 3);
    const pal = dress(b3, hk, v, meta);
    b3.style.setProperty('--W', d.W + 'px'); b3.style.setProperty('--H', d.H + 'px'); b3.style.setProperty('--T', d.T + 'px');
    b3.querySelector('.lx-covt b').textContent = meta.t; b3.querySelector('.lx-covt i').textContent = meta.a || '';
    b3.querySelector('.lx-spt').textContent = meta.t;
    b3.classList.remove('lx-img'); b3.style.removeProperty('--cov');
    asset('cover_' + hk).then((ok) => { if (ok) { b3.style.setProperty('--cov', cssUrl('cover_' + hk)); b3.classList.add('lx-img'); } });
    if (el && el.style.getPropertyValue('--sk')) b3.style.setProperty('--sk', el.style.getPropertyValue('--sk')); else b3.style.removeProperty('--sk');
    const lid = b3.querySelector('.lx-lid');
    lid.getAnimations().forEach((a) => a.cancel()); b3.getAnimations().forEach((a) => a.cancel());
    const got = fetchBook(meta.k).catch(() => null);
    RD.src = el; RD.hall = hk; RD.meta = meta; RD.pal = pal; RD.v = v;
    stageEl.hidden = false;
    const centre = 'translate(0px,0px) scale(1) rotateZ(0deg) rotateX(0deg) rotateY(0deg)';
    if (el && el.getBoundingClientRect().width) {
      const start = fromSpine(el, d);
      const lift = mob ? start.replace(/^translate\(([-\d.]+)px,([-\d.]+)px\)/, (m, x, y) => 'translate(' + (+x + 26) + 'px,' + y + 'px)')
        : start.replace(/^translate\(([-\d.]+)px,([-\d.]+)px\)/, (m, x, y) => 'translate(' + x + 'px,' + (+y - 46) + 'px)');
      b3.style.transform = start; el.classList.add('lx-out');
      anim(stageEl.querySelector('.lx-dim'), [{ opacity: 0 }, { opacity: 1 }], 600);
      await anim(b3, [{ transform: start }, { transform: lift }], 320, 'ease-out');
      await anim(b3, [{ transform: lift }, { transform: centre }], 900);
    } else {
      b3.style.transform = centre;
      await anim(stageEl.querySelector('.lx-dim'), [{ opacity: 0 }, { opacity: 1 }], 300);
    }
    const book = await got;
    if (!book) { toast('这一本没有取下来，放回去再抽一回试试。'); await shut(true); busy = false; return; }
    await new Promise((r) => setTimeout(r, reduced() ? 0 : 260));
    startReader(book, part);
    anim(lid, [{ transform: 'rotateY(0deg)' }, { transform: 'rotateY(-165deg)' }], 900, 'cubic-bezier(.4,.1,.3,1)');
    await new Promise((r) => setTimeout(r, reduced() ? 0 : 520));
    readerEl.classList.add('lx-on');
    await new Promise((r) => setTimeout(r, reduced() ? 0 : 450));
    stageEl.hidden = true; busy = false;
    const nx = readerEl.querySelector('.lx-nx'); if (nx) nx.focus({ preventScroll: true });
  }
  async function shut(noBook) {
    if (busy && !noBook) return; busy = true;
    const b3 = stageEl.querySelector('.lx-b3'), lid = b3.querySelector('.lx-lid'), d = bookDims();
    b3.style.setProperty('--W', d.W + 'px'); b3.style.setProperty('--H', d.H + 'px'); b3.style.setProperty('--T', d.T + 'px');
    b3.getAnimations().forEach((a) => a.cancel()); lid.getAnimations().forEach((a) => a.cancel());
    const centre = 'translate(0px,0px) scale(1) rotateZ(0deg) rotateX(0deg) rotateY(0deg)';
    b3.style.transform = centre;
    stageEl.hidden = false; stageEl.querySelector('.lx-dim').style.opacity = 1;
    slipEl.classList.remove('lx-on');
    if (!noBook) {
      lid.style.transform = 'rotateY(-165deg)';
      readerEl.classList.remove('lx-on');
      await anim(lid, [{ transform: 'rotateY(-165deg)' }, { transform: 'rotateY(0deg)' }], 760, 'cubic-bezier(.4,.1,.3,1)');
    }
    readerEl.hidden = true; lid.style.transform = ''; RD.book = null;
    const el = RD.src;
    anim(stageEl.querySelector('.lx-dim'), [{ opacity: 1 }, { opacity: 0 }], 800);
    if (el && el.isConnected && el.getBoundingClientRect().width + 1) {
      el.classList.add('lx-out');
      const end = fromSpine(el, d);
      await anim(b3, [{ transform: centre }, { transform: end }], 880, 'cubic-bezier(.5,0,.3,1)');
      el.classList.remove('lx-out');
    } else await anim(b3, [{ transform: centre, opacity: 1 }, { transform: 'translate(0px,40px) scale(.6)', opacity: 0 }], 500);
    b3.getAnimations().forEach((a) => a.cancel());
    stageEl.hidden = true; busy = false;
    if (el && el.isConnected) el.focus({ preventScroll: true });
  }

  /* ---------- 读：页面、版式 ---------- */
  function startReader(book, part) {
    RD.book = book; RD.fold = new Set(); RD.mode = mob ? 'scroll' : 'page';
    const P = [{ t: 'fly' }];
    const tocAt = book.tocAt != null ? book.tocAt : 0;
    book.secs.forEach((s, i) => { if (i === tocAt) P.push({ t: 'toc' }); P.push({ t: 'sec', i }); });
    if (tocAt >= book.secs.length) P.push({ t: 'toc' });
    if (Object.keys(book.notes || {}).length) P.push({ t: 'notes' });
    RD.pages = P; RD.pi = 0; RD.spread = 0;
    if (part != null && part > 0) { const j = P.findIndex((p) => p.t === 'sec' && book.secs[p.i].pt === part); if (j > 0) RD.pi = j; }
    if (book.player) RD.pi = 1;          // 玩家自己那一本：翻开第一页就是凭证
    readerEl.innerHTML = '<div class="rd-top"><button class="lb-btn lx-sh" type="button"><b>‹</b>合上，放回去</button><span class="lx-where"></span>'
      + '<button class="lb-btn lx-md" type="button"></button><button class="lb-btn lx-tc" type="button">目录</button>' + SPL + '</div>'
      + '<div class="rd-body"><div class="rd-book"><div class="lx-cover"></div><div class="lx-paper"><div class="rd-hd lx-l"></div><div class="rd-hd lx-r"></div><div class="rd-win"><div class="rd-flow"></div></div><div class="rd-folio lx-l"></div><div class="rd-folio lx-r"></div></div></div><aside class="rd-margin"></aside></div>'
      + '<nav class="rd-nav"><button class="lb-btn lx-pv" type="button">往前翻</button><span class="lx-pg"></span><button class="lb-btn lx-nx" type="button">往后翻</button></nav><div class="rd-toc" hidden><div class="lx-box"></div></div>';
    const bk = readerEl.querySelector('.rd-book');
    bk.dataset.paper = book.paper || 'print'; bk.dataset.h = RD.hall;
    for (const p of ['--c1', '--c2', '--tc']) if (RD.pal[p]) bk.style.setProperty(p, RD.pal[p]);
    asset('paper_' + (book.paper || 'print')).then((ok) => { if (ok && RD.book === book) { bk.style.setProperty('--pimg', cssUrl('paper_' + book.paper)); bk.classList.add('lx-pimg'); } });
    readerEl.querySelector('.lx-sh').addEventListener('click', () => shut());
    readerEl.querySelector('.lx-md').addEventListener('click', () => { RD.mode = RD.mode === 'page' ? 'scroll' : 'page'; relayout(false, true); });
    readerEl.querySelector('.lx-tc').addEventListener('click', openTocPanel);
    readerEl.querySelector('.lb-spl').addEventListener('click', toggleSpoil);
    readerEl.querySelector('.lx-pv').addEventListener('click', () => turn(-1));
    readerEl.querySelector('.lx-nx').addEventListener('click', () => turn(1));
    readerEl.querySelector('.rd-toc').addEventListener('click', (e) => {
      const it = e.target.closest('.lx-it'); if (it) { closeTocPanel(); gotoSec(+it.dataset.i, it.dataset.b != null ? +it.dataset.b : -1, it.dataset.p != null ? +it.dataset.p : null); return; }
      if (e.target.classList.contains('rd-toc')) closeTocPanel();
    });
    bk.addEventListener('click', onPageClick);
    let tx = 0, ty = 0;
    bk.addEventListener('touchstart', (e) => { const t = e.touches[0]; tx = t.clientX; ty = t.clientY; }, { passive: true });
    bk.addEventListener('touchend', (e) => { if (RD.mode !== 'page') return; const t = e.changedTouches[0], dx = t.clientX - tx, dy = t.clientY - ty; if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.4) turn(dx < 0 ? 1 : -1); }, { passive: true });
    readerEl.hidden = false;
    relayout(false, true);
  }
  /* 量一回版式：电脑上两页对开（右边留一栏页边写注），手机或窄屏一页；卷轴是一节从头滚到尾 */
  function layoutDims() {
    const body = readerEl.querySelector('.rd-body'), bk = readerEl.querySelector('.rd-book'), mg = readerEl.querySelector('.rd-margin');
    const W = body.clientWidth - (mob ? 16 : 52), H = body.clientHeight - 4;
    const one = mob || W < 760;
    let mw = 0;
    if (!one && W > 1180) mw = clamp(W * 0.18, 210, 290);
    let bh = Math.min(H - (one ? 6 : 14), 920), bw;
    if (one) bw = Math.min(W, 640);
    else { bw = Math.min(W - mw - (mw ? 26 : 0), bh * 1.5); if (bw < 860 && mw) { mw = 0; bw = Math.min(W, bh * 1.5); } }
    bw = Math.floor(bw);
    const pageW = one ? bw : bw / 2;
    const pl = Math.round(clamp(pageW * 0.1, 18, 62)), pt = one ? 34 : 50, pb = one ? 34 : 46;
    const cw = Math.floor(pageW - pl * 2), cg = pl * 2;
    bk.classList.toggle('lx-one', one);
    bk.style.setProperty('--bw', bw + 'px'); bk.style.setProperty('--bh', bh + 'px');
    bk.style.setProperty('--pl', pl + 'px'); bk.style.setProperty('--pt', pt + 'px'); bk.style.setProperty('--pb', pb + 'px');
    bk.style.setProperty('--cw', cw + 'px'); bk.style.setProperty('--cg', cg + 'px');
    bk.style.setProperty('--ww', (one ? cw : cw * 2 + cg) + 'px');
    bk.style.setProperty('--fz', (one ? (bw < 420 ? 15.5 : 16) : clamp(pageW / 36, 14.5, 17)).toFixed(1) + 'px');
    mg.hidden = !mw; mg.style.setProperty('--mw', mw + 'px');
    return { one, cw, cg, mw, step: cw + cg };
  }
  function relayout(keep, modeChanged) {
    if (!RD.book) return;
    const bk = readerEl.querySelector('.rd-book');
    bk.classList.toggle('lx-scroll', RD.mode === 'scroll');
    const md = readerEl.querySelector('.lx-md'); md.textContent = RD.mode === 'page' ? '卷着读' : '一页一页翻';
    RD.lay = layoutDims();
    const anchor = keep ? RD.spread : 0;
    renderPage(keep ? 'keep' : 0, anchor);
  }
  const SEALH = '<div class="lb-seal"><i></i><span>' + SEAL + '</span></div>';
  function blockHTML(b) {
    switch (b.k) {
      case 'p': return '<p' + (b.h.indexOf('<br>') >= 0 ? ' class="lx-ni"' : '') + '>' + b.h + '</p>';
      case 'h3': return '<h3>' + b.h + '</h3>';
      case 'h4': return '<h4>' + b.h + '</h4>';
      case 'q': return '<blockquote>' + b.h + '</blockquote>';
      case 'mk': return '<p class="lx-mkb">' + b.h + '</p>';
      case 'hr': return '<hr>';
      case 'fig': {
        /* 插图（11-24）：assets/lib/plates/<段>/<书键>_<n>.webp 在（数据里 im 是宽高、sg 是段），出图，图下照旧带原文，点标签折起；没有就照旧画字框 */
        if (b.im && RD.book) {
          const fold = RD.fold && RD.fold.has(b.n);
          return '<figure class="lx-plate" data-v="' + b.v + '"><img alt="" loading="eager" decoding="async" width="' + b.im[0] + '" height="' + b.im[1] + '" style="aspect-ratio:' + b.im[0] + '/' + b.im[1] + '" src="' + esc(plateSrc(b.sg || 'p2', RD.book.k, b.n)) + '">'
            + '<figcaption><details data-n="' + b.n + '"' + (fold ? '' : ' open') + '><summary>' + b.l + '</summary><span class="lx-ft">' + b.h + '</span></details></figcaption></figure>';
        }
        return '<figure data-v="' + b.v + '"><div class="lx-pi"><span>' + b.h + '</span></div><figcaption>' + b.l + '</figcaption></figure>';
      }
      case 'ul': case 'ol': {
        const li = (it) => '<li>' + (it.s ? '<span class="lx-isp"><span class="lx-ispc">' + it.h + '</span></span>' : it.h) + (it.sub ? '<ul>' + it.sub.map(li).join('') + '</ul>' : '') + '</li>';
        return '<' + b.k + (b.st && b.st !== 1 ? ' start="' + b.st + '"' : '') + '>' + b.i.map(li).join('') + '</' + b.k + '>';
      }
      case 'tb': {
        const rows = b.r.map((r, i) => { const tag = b.hd && i === 0 ? 'th' : 'td'; return '<tr>' + r.c.map((c) => '<' + tag + '>' + (r.s ? '<span class="lx-isp"><span class="lx-ispc">' + c + '</span></span>' : c) + '</' + tag + '>').join('') + '</tr>'; });
        return '<table>' + rows.join('') + '</table>';
      }
    }
    return '';
  }
  function blocksHTML(bs) {
    let out = '', grp = '';
    for (const b of bs) {
      const h = blockHTML(b);
      if (b.s) grp += h; else { if (grp) { out += '<div class="lx-sp-g">' + SEALH + '<div class="lx-sp-c">' + grp + '</div></div>'; grp = ''; } out += h; }
    }
    if (grp) out += '<div class="lx-sp-g">' + SEALH + '<div class="lx-sp-c">' + grp + '</div></div>';
    return out;
  }
  const noteHTML = (id, n) => '<div class="lx-mn lx-' + n.ink + '" data-n="' + id + '"><span class="lx-k">' + esc(n.m) + '</span>'
    + (n.s ? '<span class="lx-isp"><span class="lx-ispc">' + n.h + '</span></span>' : n.h) + (n.by ? '<span class="lx-by">' + n.by + '</span>' : '') + '</div>';
  function chapter(t, small) { return '<div class="lx-ch"><h2>' + t + '</h2>' + (small ? '<small>' + small + '</small>' : '') + '<i></i></div>'; }
  function pageHTML(p) {
    const B = RD.book;
    if (p.t === 'toc') {
      let h = chapter('目录');
      const ents = B.toc || [];
      if (ents.length) h += '<ul class="lx-toc">' + ents.map((e) => (e.c != null ? '<li class="lx-c">' + e.c + '</li>'
        : '<li' + (e.lv ? ' class="lx-lv1"' : '') + '>' + (e.i >= 0 ? '<button type="button" data-i="' + e.i + '"' + (e.b != null ? ' data-b="' + e.b + '"' : '') + '>' + e.h + '</button>' : '<span class="lx-no">' + e.h + '</span>') + '</li>')).join('') + '</ul>';
      if (B.tocx || !ents.length) h += (ents.length ? '<h3>章次</h3>' : '') + '<ul class="lx-toc">' + B.secs.map((s, i) => '<li><button type="button" data-i="' + i + '">' + s.t + '</button></li>').join('') + '</ul>';
      if (Object.keys(B.notes || {}).length) h += '<ul class="lx-toc"><li><button type="button" data-p="notes">注脚</button></li></ul>';
      return h;
    }
    if (p.t === 'notes') {
      const ids = Object.keys(B.notes);
      let h = chapter('注脚'), part = null;
      h += '<div class="lx-fnl">';
      for (const id of ids) {
        const pt = B.parts ? 'abc'.indexOf(id[0]) : -1;
        if (B.parts && pt !== part) { part = pt; h += '<h4>' + esc(B.parts[pt] || '') + '</h4>'; }
        h += noteHTML(id, B.notes[id]);
      }
      return h + '</div><p class="lx-endmark">已清点</p>';
    }
    const s = B.secs[p.i];
    const partName = B.parts && s.pt != null && (p.i === 0 || B.secs[p.i - 1].pt !== s.pt) ? B.parts[s.pt] : '';
    let h = chapter(s.t, partName);
    if (s.s) h += '<div class="lx-sp-g"><div class="lb-secseal"><i></i><span>这一节整节压着青火印<br>开了剧透才揭得开</span></div><div class="lx-sp-c">' + blocksHTML(s.b.map((b) => Object.assign({}, b, { s: 0 }))) + '</div></div>';
    else h += blocksHTML(s.b);
    return h;
  }
  function flyHTML() {
    const B = RD.book;
    const lines = B.fly || [];
    let title = '', rest = [];
    for (const [k, h] of lines) { if (k === 'h' && !title) title = h; else rest.push(h); }
    if (!title) title = esc(B.t);
    const auth = esc(B.a || '');
    const body = rest.filter((h) => strip(h) !== strip(B.a || '')).map((h) => '<p>' + h + '</p>').join('');
    return '<div class="rd-fly"><div class="lx-inner"><div class="lx-plate"><div class="lx-pp lx-fb">' + flame(50, 44, 26) + '</div><div class="lx-ok">已清点</div></div></div>'
      + '<div class="lx-ttl"><h1>' + title + '</h1>' + body + (auth && !rest.length ? '<p class="lx-by">' + auth + '</p>' : '') + '<p class="lx-ft">' + esc(B.y || '') + '</p></div></div>';
  }
  /* 画这一页：dir 1 往后、-1 往前、0 直接、'keep' 照原来那一叠（版式变了以后） */
  function renderPage(dir, anchor) {
    const B = RD.book, p = RD.pages[RD.pi], bk = readerEl.querySelector('.rd-book'), win = bk.querySelector('.rd-win'), flow = bk.querySelector('.rd-flow');
    const old = bk.querySelector('.rd-fly'); if (old) old.remove();
    const where = p.t === 'fly' ? '扉页' : p.t === 'toc' ? '目录' : p.t === 'notes' ? '注脚' : strip(B.secs[p.i].t);
    readerEl.querySelector('.lx-where').textContent = B.t + '　' + where;
    bk.querySelector('.rd-hd.lx-l').textContent = B.t; bk.querySelector('.rd-hd.lx-r').textContent = where;
    flow.classList.add('lx-still');
    if (p.t === 'fly') {
      win.style.visibility = 'hidden'; flow.innerHTML = '';
      bk.querySelector('.lx-paper').insertAdjacentHTML('beforeend', flyHTML());
      const pp = bk.querySelector('.rd-fly .lx-pp');
      asset('plate').then((ok) => { if (ok && pp) { pp.classList.remove('lx-fb'); pp.innerHTML = ''; pp.style.setProperty('--plate-img', cssUrl('plate')); const okEl = pp.parentNode.querySelector('.lx-ok'); if (okEl) okEl.hidden = true; } });
      RD.spreads = 1; RD.spread = 0;
    } else {
      win.style.visibility = '';
      flow.innerHTML = pageHTML(p);
      bindFlow(flow);
      asset('seal').then((ok) => { if (ok) { root.style.setProperty('--seal', cssUrl('seal')); flow.querySelectorAll('.lb-seal').forEach((x) => x.classList.add('lx-img')); } });
      if (RD.mode === 'page') {
        flow.style.transform = 'translateX(0)';
        const cols = Math.max(1, Math.round((flow.scrollWidth + RD.lay.cg) / RD.lay.step));
        RD.cols = cols;
        RD.spreads = RD.lay.one ? cols : Math.ceil(cols / 2);
        RD.spread = dir === 'keep' ? clamp(anchor || 0, 0, RD.spreads - 1) : dir === -1 ? RD.spreads - 1 : 0;
        if (typeof anchor === 'object' && anchor && anchor.block != null) RD.spread = spreadOfBlock(flow, anchor.block);
      } else {
        RD.spreads = 1; RD.spread = 0; win.scrollTop = 0;
        if (typeof anchor === 'object' && anchor && anchor.block != null) { const el = flow.querySelectorAll(':scope > h3, :scope > h4, :scope > .lx-sp-g h3, :scope > .lx-sp-g h4')[anchor.hi]; if (el) win.scrollTop = el.offsetTop - 20; }
      }
    }
    placeSpread(dir === 1 || dir === -1 ? dir : 0);
  }
  /* 第几个小标题在第几叠 */
  function spreadOfBlock(flow, hi) {
    const hs = flow.querySelectorAll('h3, h4');
    const el = hs[hi];
    if (!el) return 0;
    const fr = flow.getBoundingClientRect(), r = el.getBoundingClientRect();
    if (!r.width) return 0;
    const col = Math.floor((r.left - fr.left + 2) / RD.lay.step);
    return clamp(RD.lay.one ? col : Math.floor(col / 2), 0, RD.spreads - 1);
  }
  function placeSpread(dir) {
    const bk = readerEl.querySelector('.rd-book'), flow = bk.querySelector('.rd-flow'), p = RD.pages[RD.pi];
    if (RD.mode === 'page' && p.t !== 'fly') {
      const k = RD.lay.one ? RD.spread : RD.spread * 2;
      flow.style.transform = 'translateX(' + (-k * RD.lay.step) + 'px)';
    }
    if (dir && !reduced() && RD.mode === 'page') {
      const lf = document.createElement('div'); lf.className = 'rd-leaf ' + (dir > 0 ? 'lx-fw' : 'lx-bw');
      bk.querySelector('.lx-paper').appendChild(lf); setTimeout(() => lf.remove(), 600);
    }
    // 页码、钮
    const pg = readerEl.querySelector('.rd-nav .lx-pg'), last = RD.pi === RD.pages.length - 1 && RD.spread >= RD.spreads - 1;
    const sec = p.t === 'sec' ? p.i : -1;
    const fl = bk.querySelector('.rd-folio.lx-l'), fr = bk.querySelector('.rd-folio.lx-r');
    if (p.t === 'fly') { fl.textContent = ''; fr.textContent = ''; pg.textContent = '扉页'; }
    else if (RD.mode === 'page') {
      const a = RD.lay.one ? RD.spread + 1 : RD.spread * 2 + 1;
      fl.textContent = cnum(a); fr.textContent = RD.lay.one ? cnum(a) : (a + 1 <= RD.cols ? cnum(a + 1) : '');
      if (RD.lay.one) fl.textContent = '';
      pg.textContent = (RD.spread + 1) + ' ／ ' + RD.spreads;
    } else { fl.textContent = ''; fr.textContent = ''; pg.textContent = (RD.pi + 1) + ' ／ ' + RD.pages.length; }
    readerEl.querySelector('.lx-pv').disabled = RD.pi === 0 && RD.spread === 0;
    readerEl.querySelector('.lx-nx').disabled = last;
    readerEl.querySelector('.lx-nx').textContent = RD.mode === 'scroll' || RD.spread >= RD.spreads - 1 ? (last ? '到底了' : '下一节') : '往后翻';
    readerEl.querySelector('.lx-pv').textContent = RD.mode === 'scroll' || RD.spread === 0 ? '上一节' : '往前翻';
    if (sec < -1) return;
    fillMargin();
  }
  function turn(d) {
    if (!RD.book || busy) return;
    slipEl.classList.remove('lx-on');
    if (RD.mode === 'page' && RD.pages[RD.pi].t !== 'fly') {
      const n = RD.spread + d;
      if (n >= 0 && n < RD.spreads) { RD.spread = n; placeSpread(d); return; }
    }
    const j = RD.pi + d;
    if (j < 0 || j >= RD.pages.length) return;
    RD.pi = j; renderPage(d);
  }
  function gotoSec(i, bi, special) {
    if (special === 'notes' || (typeof special === 'string')) { const j = RD.pages.findIndex((p) => p.t === 'notes'); if (j >= 0) { RD.pi = j; renderPage(1); } return; }
    const j = RD.pages.findIndex((p) => p.t === 'sec' && p.i === i);
    if (j < 0) return;
    RD.pi = j;
    let hi = null;
    if (bi != null && bi >= 0) { const bs = RD.book.secs[i].b; hi = 0; for (let k = 0; k < bi; k++) if (bs[k].k === 'h3' || bs[k].k === 'h4') hi++; }
    renderPage(1, hi != null ? { block: bi, hi } : 0);
  }
  /* 页边：这一叠上引到的注，写在右边一栏（清点的人添的那几条是青墨） */
  function visibleRefs() {
    const flow = readerEl.querySelector('.rd-flow'), out = [];
    const fr = flow.getBoundingClientRect();
    flow.querySelectorAll('sup.lx-fn').forEach((s) => {
      const r = s.getBoundingClientRect();
      if (!r.width) return;
      if (RD.mode === 'page') {
        const col = Math.floor((r.left - fr.left + 1) / RD.lay.step), k = RD.lay.one ? RD.spread : RD.spread * 2;
        if (col < k || col > k + (RD.lay.one ? 0 : 1)) return;
      }
      if (out.indexOf(s.dataset.n) < 0) out.push(s.dataset.n);
    });
    return out;
  }
  function fillMargin() {
    const mg = readerEl.querySelector('.rd-margin');
    if (mg.hidden || !RD.book) return;
    const p = RD.pages[RD.pi];
    if (p.t === 'fly' || p.t === 'notes') { mg.innerHTML = ''; return; }
    const ids = visibleRefs(), N = RD.book.notes || {};
    mg.innerHTML = ids.filter((id) => N[id]).map((id) => noteHTML(id, N[id])).join('') || (p.t === 'toc' ? '<p class="lx-none">点一行，翻到那一节</p>' : '');
  }
  function bindFlow(flow) {
    /* 插图下的原文折起、展开：记下这一本里哪几张折着，重排一回版（分页跟着变），停在原来那一叠 */
    if (!flow._figBound) {
      flow._figBound = 1;
      flow.addEventListener('toggle', (e) => {
        const d = e.target;
        if (!d.matches || !d.matches('figure.lx-plate details')) return;
        if (!RD.fold) RD.fold = new Set();
        const n = +d.dataset.n, was = RD.fold.has(n);
        if (d.open === !was) return;
        if (d.open) RD.fold.delete(n); else RD.fold.add(n);
        if (RD.mode === 'page') relayout(true);
      }, true);
    }
    flow.querySelectorAll('.lx-toc button').forEach((b) => b.addEventListener('click', (e) => { e.stopPropagation(); gotoSec(+b.dataset.i, b.dataset.b != null ? +b.dataset.b : -1, b.dataset.p || null); }));
  }
  function onPageClick(e) {
    const t = e.target;
    const sup = t.closest('sup.lx-fn');
    if (sup) { e.stopPropagation(); showNote(sup.dataset.n, sup); return; }
    if (t.closest('.lb-seal, .lb-secseal') || (t.classList && t.classList.contains('lx-isp') && !spoilOn())) { sealHint(); return; }
    if (t.closest('button, a, .lx-toc, summary, .lx-ft')) return;
    if (RD.mode !== 'page') return;
    const r = e.currentTarget.getBoundingClientRect(), x = (e.clientX - r.left) / r.width;
    if (x > 0.72) turn(1); else if (x < 0.28) turn(-1);
  }
  function sealHint() {
    const s = readerEl.querySelector('.rd-top .lb-spl');
    s.classList.remove('lx-flash'); void s.offsetWidth; s.classList.add('lx-flash');
    toast('剧透开关在右上角，开了，青火印就揭开了。');
  }
  function showNote(id, sup) {
    const n = (RD.book.notes || {})[id];
    if (!n) return;
    const mg = readerEl.querySelector('.rd-margin');
    const m = !mg.hidden && mg.querySelector('.lx-mn[data-n="' + id + '"]');
    if (m) { m.scrollIntoView({ block: 'nearest', behavior: reduced() ? 'auto' : 'smooth' }); m.classList.add('lx-lit'); setTimeout(() => m.classList.remove('lx-lit'), 1400); return; }
    slipEl.innerHTML = noteHTML(id, n);
    slipEl.classList.add('lx-on');
  }
  function openTocPanel() {
    const B = RD.book, box = readerEl.querySelector('.rd-toc .lx-box'), cur = RD.pages[RD.pi];
    let h = '<h4>' + esc(B.t) + '</h4>';
    let part = null;
    h += '<button class="lx-it" type="button" data-i="-1" data-p="fly">扉页</button>';
    B.secs.forEach((s, i) => {
      if (B.parts && s.pt !== part) { part = s.pt; h += '<button class="lx-it lx-pt" type="button" data-i="' + i + '">' + esc(B.parts[s.pt]) + '</button>'; }
      h += '<button class="lx-it' + (cur.t === 'sec' && cur.i === i ? ' lx-here' : '') + '" type="button" data-i="' + i + '">' + s.t + '</button>';
    });
    if (Object.keys(B.notes || {}).length) h += '<button class="lx-it" type="button" data-i="-1" data-p="notes">注脚</button>';
    box.innerHTML = h;
    box.querySelectorAll('.lx-it[data-p="fly"]').forEach((b) => { b.removeAttribute('data-i'); b.addEventListener('click', (e) => { e.stopPropagation(); closeTocPanel(); RD.pi = 0; renderPage(-1); }); });
    box.querySelectorAll('.lx-it[data-p="notes"]').forEach((b) => { b.addEventListener('click', (e) => { e.stopPropagation(); closeTocPanel(); gotoSec(-1, -1, 'notes'); }); });
    const tc = readerEl.querySelector('.rd-toc'); tc.hidden = false; requestAnimationFrame(() => tc.classList.add('lx-on'));
  }
  function closeTocPanel() { const tc = readerEl.querySelector('.rd-toc'); if (!tc || tc.hidden) return false; tc.classList.remove('lx-on'); setTimeout(() => { tc.hidden = true; }, 300); return true; }

  /* ---------- 键盘 ---------- */
  function onKey(e) {
    if (!opened || e.defaultPrevented) return;          // 世界之书（地图室翻开的）盖在上面的时候，键归它
    if (window.Codex && Codex.isOpen && Codex.isOpen()) return;
    if (e.target && e.target.closest && e.target.closest('input,textarea')) return;
    const k = e.key;
    let used = true;
    if (k === 'Escape') {
      if (!lendEl.hidden) closeLend();
      else if (slipEl.classList.contains('lx-on')) slipEl.classList.remove('lx-on');
      else if (RD.book && !readerEl.hidden) { if (!closeTocPanel()) shut(); }
      else if (view !== 'hall') showHall();
      else close();
    } else if (RD.book && !readerEl.hidden && !busy) {
      if (k === 'ArrowRight' || k === 'PageDown') turn(1);
      else if (k === 'ArrowLeft' || k === 'PageUp') turn(-1);
      else used = false;
    } else used = false;
    if (used) { e.stopPropagation(); e.preventDefault(); }
  }

  const api = {
    init, open, close, syncSpoil, addPlayerBook,
    openBook: (k, part) => { if (!opened) open(); (ready || Promise.resolve()).then(() => openBookKey(k, part)); },
    isOpen: () => opened,
    get state() { return { open: opened, view, hall: curHall, book: RD.book ? RD.book.k : null, page: RD.pi, pages: RD.pages.map((p) => p.t + (p.i != null ? p.i : '')), spread: RD.spread, spreads: RD.spreads, mode: RD.mode, mob, busy }; },
    // 走查、截图用：直接翻到哪一节
    _goto: (i, spread) => { if (!RD.book) return; const j = RD.pages.findIndex((p) => (i === 'toc' ? p.t === 'toc' : i === 'notes' ? p.t === 'notes' : p.t === 'sec' && p.i === i)); if (j >= 0) { RD.pi = j; renderPage(0); if (spread) { RD.spread = clamp(spread, 0, RD.spreads - 1); placeSpread(0); } } },
    _mode: (m) => { RD.mode = m; relayout(false, true); },
  };
  window.Library = api;
})();
