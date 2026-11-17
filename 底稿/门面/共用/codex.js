/* 世界之书：四本书和牌桌共用的一份。11-15 介绍页收尾那一轮从月银纪那一本抽出来，11-17 前端精修换了装：
   一本对开的精装书（手机上一次一页），五卷（通用、月银纪、纷争纪、山铜纪、迷宫纪）一卷一种装帧，书侧五条缎带书签换卷，
   每卷头一页是扉页和目录，每一章左页是章首（横幅、第几章、题、题记），右页是正文（首字下沉、章节之间的花饰），换章是一张纸翻过去。
   字在 共用/data/wb.json（底稿/门面/卡片/世界之书.json 并出来的），章首的图和题记在 共用/data/wb_dress.json（prep_wb.py 出），
   各纪卷的“山河与地图”那一章放一张能点的地图，点在 共用/data/map_<卷>.json（prep_maps.py 出），底图在 共用/assets/map/；
   正文里提到的地方（地图上有的）点得开，出一张小卡，能翻到地图上看。
   用法（书里）：
     await Codex.init({ vol: 'moon', host: 某个 position:fixed/absolute 撑满屏的元素, A, spoil: () => SPOIL, setSpoil, onEra, onOpen, onClose });
     Codex.open(卷, 章, { period, era, focus }) 打开（章写 '' 是这一卷的扉页和目录）；Codex.close()；Codex.isOpen()；
     Codex.mini(卷, 时代 id, 这一页的地方) 出时代页“这一带”那一小幅地图的 html，点击交给 Codex.miniClick(ev, 卷, 时代 id)。
   A(p) 是地址怎么换：单独打开一本书的时候原样，装在牌桌那个外壳里的时候换成图床的地址。 */
(function () {
  'use strict';
  const VOL_ORDER = [['general', '通用'], ['moon', '月银纪'], ['strife', '纷争纪'], ['bronze', '山铜纪'], ['maze', '迷宫纪']];
  const EMB = { general: 'wb_cover', moon: 'emblem_moon', strife: 'emblem_strife', bronze: 'emblem_bronze', maze: 'emblem_maze' };
  const NUM = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'];
  const AR = 3072 / 1955;            // 底图都是 Azgaar 那一张整图（2200×1400）截的，宽高比一样
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const reEsc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const SPL = '<button class="spl" type="button" aria-label="剧透开关"><i></i><span>剧透　<em class="off">关着，谁死在哪里、主线怎么收场都不显示</em><em class="on">开着</em></span></button>';
  let C = null, WB = { volumes: [] }, DR = { ban: {}, front: {}, epi: {} }, root = null, bk, bg, spread, pl, pr, rib, tp, tx, tip = null;
  let opened = false, wbVol = 'general', wbPage = '', MAPAPPLY = null, ready = null, busy = 0;
  const MAPS = {}, TERMS = {}, PRE = {};
  const A = (p) => (C && C.A ? C.A(p) : p);
  const volOf = (id) => (WB.volumes || []).find((v) => v.id === id);
  const spoilOn = () => !!(C && C.spoil && C.spoil());
  const ban = (vol, pid) => ((DR.ban || {})[vol] || {})[pid];
  const img = (name) => A('common/assets/wb/' + name + '.webp');
  const abs = (u) => { try { return new URL(u, document.baseURI).href; } catch (e) { return u; } };
  const twoPage = () => spread && getComputedStyle(spread).display === 'grid';
  const scroller = () => (twoPage() ? pr : spread);
  const reduced = () => window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function build() {
    root = document.createElement('div');
    root.id = 'wb'; root.hidden = true;
    root.setAttribute('role', 'dialog'); root.setAttribute('aria-label', '世界之书');
    root.innerHTML = '<div class="wb-bg"></div>'
      + '<div class="bk" data-v="general"><div class="cov"><i class="ck tl"></i><i class="ck tr"></i><i class="ck bl"></i><i class="ck br"></i></div>'
      + '<nav class="rib" aria-label="换卷"></nav>'
      + '<div class="spread"><section class="pg pl"></section><section class="pg pr"></section><div class="gut"></div></div>'
      + '<button class="tn tp" type="button" aria-label="往前翻">‹</button><button class="tn tx" type="button" aria-label="往后翻">›</button></div>'
      + '<button class="x" type="button"><b>×</b>合上</button>';
    (C.host || document.body).appendChild(root);
    bk = root.querySelector('.bk'); bg = root.querySelector('.wb-bg'); spread = root.querySelector('.spread');
    pl = root.querySelector('.pl'); pr = root.querySelector('.pr'); rib = root.querySelector('.rib');
    tp = root.querySelector('.tp'); tx = root.querySelector('.tx');
    root.addEventListener('click', (ev) => {
      const t = ev.target;
      if (t.closest('.wtip .go')) { const b = t.closest('.go'); hideTip(); go(() => { showPage('map', { period: +b.dataset.mk, focus: b.dataset.mf }); }, 1); return; }
      if (t.closest('.wtip')) return;
      hideTip();
      if (t.closest('#wb > .x') || t === root || t === bg) { close(); return; }
      if (t.closest('.spl')) { const s = scroller(), y = s.scrollTop; C.setSpoil(!spoilOn()); syncSpoil(); s.scrollTop = y; return; }
      if (t.closest('.wm')) return;
      const tm = t.closest('.tm'); if (tm) { showTip(tm); return; }
      if (t.closest('.tp')) { step(-1); return; }
      if (t.closest('.tx')) { step(1); return; }
      const sec = t.closest('[data-sec]'); if (sec) { const el = pr.querySelector('section[data-i="' + sec.dataset.sec + '"]'); if (el) { const s = scroller(); s.scrollTo({ top: el.offsetTop - (s === pr ? 30 : 70), behavior: reduced() ? 'auto' : 'smooth' }); } return; }
      const vb = t.closest('.rb[data-v]');
      if (vb) {
        const nv = vb.dataset.v, d = order(nv) - order(wbVol);
        if (nv === wbVol && !wbPage) return;
        go(() => { wbVol = nv; render('', {}); }, d || -1); return;
      }
      const pb = t.closest('[data-p]'); if (pb) { const pid = pb.dataset.p, d = pageIdx(pid) - pageIdx(wbPage); go(() => render(pid, {}), d >= 0 ? 1 : -1); }
    });
    for (const ev of ['pointerdown', 'pointerup', 'pointermove', 'wheel', 'touchstart', 'touchmove']) root.addEventListener(ev, (e) => e.stopPropagation(), { passive: true });
    for (const el of [pr, spread]) el.addEventListener('scroll', hideTip, { passive: true });
    window.addEventListener('keydown', (e) => {
      if (!opened) return;
      if (e.key === 'Escape') { e.stopPropagation(); e.preventDefault(); if (tip) hideTip(); else close(); }
      else if ((e.key === 'ArrowLeft' || e.key === 'ArrowRight') && !e.target.closest('input,textarea')) { e.preventDefault(); step(e.key === 'ArrowLeft' ? -1 : 1); }
    }, true);
    window.addEventListener('resize', () => { hideTip(); if (MAPAPPLY) MAPAPPLY(); });
  }

  function init(cfg) {
    C = Object.assign({ vol: 'general', host: null, A: null, spoil: () => false, setSpoil: () => {}, onEra: () => {}, onOpen: () => {}, onClose: () => {} }, cfg || {});
    wbVol = C.vol;
    build();
    const get = (p, d) => fetch(A(p)).then((r) => (r.ok ? r.json() : d)).catch(() => d);
    ready = Promise.all([get('common/data/wb.json', { volumes: [] }), get('common/data/wb_dress.json', null)].concat(VOL_ORDER.slice(1).map(([id]) => get('common/data/map_' + id + '.json', null))))
      .then(([wb, dr, ...maps]) => {
        WB = wb || { volumes: [] }; if (dr) DR = dr;
        VOL_ORDER.slice(1).forEach(([id], k) => { if (maps[k]) MAPS[id] = maps[k]; });
        return api;
      });
    return ready;
  }

  function syncSpoil() { if (root) root.classList.toggle('spoil-on', spoilOn()); }
  const order = (id) => VOL_ORDER.findIndex(([v]) => v === id);
  const pageIdx = (pid) => (pid ? (volOf(wbVol).pages.findIndex((p) => p.id === pid) + 1) : 0);

  function open(vol, page, opts) {
    if (!root) return;
    hideTip();
    wbVol = volOf(vol) ? vol : volOf(C.vol) ? C.vol : ((WB.volumes || [])[0] || {}).id;
    if (!wbVol) return;
    C.onOpen(); root.hidden = false; opened = true;          // 先露出来再排版，地图量得到框
    syncSpoil(); render(page || '', opts || {});
    requestAnimationFrame(() => root.classList.add('on'));
  }
  function close() {
    if (!opened) return;
    hideTip();
    opened = false; root.classList.remove('on'); MAPAPPLY = null;
    setTimeout(() => { if (!opened) root.hidden = true; }, 380);
    C.onClose();
  }

  // 整本书照先后排成一条：每卷的扉页，再是这一卷的各章
  function seq() {
    const out = [];
    for (const [id] of VOL_ORDER) { const v = volOf(id); if (!v) continue; out.push([id, '']); for (const p of v.pages) out.push([id, p.id]); }
    return out;
  }
  function step(d) {
    const S = seq(), i = S.findIndex(([v, p]) => v === wbVol && p === wbPage), j = i + d;
    if (i < 0 || j < 0 || j >= S.length) return;
    go(() => { wbVol = S[j][0]; render(S[j][1], {}); }, d);
  }

  // 翻页：先排好新的两页，再拿一张纸盖在上面翻过去，纸的正面是原来那一页，背面是新的那一页
  function go(fn, dir) {
    hideTip();
    const anim = opened && dir && twoPage() && !reduced() && !bk.classList.contains('wide');
    if (!anim) { fn(); return; }
    const oldL = pl.innerHTML, oldR = pr.innerHTML, oldY = pr.scrollTop, oldV = bk.dataset.v;
    fn();
    if (bk.classList.contains('wide')) return;
    const leaf = document.createElement('div'), a = document.createElement('section'), b = document.createElement('section');
    leaf.className = 'leaf ' + (dir > 0 ? 'f' : 'b');
    if (dir > 0) { a.className = 'pg pr face'; a.innerHTML = oldR; b.className = 'pg pl face back'; b.innerHTML = pl.innerHTML; }
    else { a.className = 'pg pl face'; a.innerHTML = oldL; b.className = 'pg pr face back'; b.innerHTML = pr.innerHTML; }
    a.dataset.v = oldV; b.dataset.v = bk.dataset.v;          // 跨卷翻的时候，正面还是原来那一卷的颜色
    leaf.append(a, b); spread.appendChild(leaf);
    if (dir > 0) a.scrollTop = oldY;
    const k = ++busy;
    const done = () => { if (leaf.parentNode) leaf.remove(); };
    leaf.addEventListener('animationend', done, { once: true });
    setTimeout(() => { if (k === busy || leaf.parentNode) done(); }, 900);
  }

  function render(pid, opts) {
    const v = volOf(wbVol);
    const p = pid && v.pages.find((x) => x.id === pid);
    bk.dataset.v = wbVol;
    const front = (DR.front || {})[wbVol], b0 = ban(wbVol, 'age') || ban(wbVol, (v.pages[0] || {}).id) || front;
    bg.style.setProperty('--bgimg', b0 ? `url("${abs(img(b0))}")` : 'none');      // 变量里的相对地址会照 codex.css 那个目录去找，先换成整的
    ribHTML();
    for (const name of [front].concat(v.pages.map((x) => ban(wbVol, x.id)))) if (name && !PRE[name]) { PRE[name] = new Image(); PRE[name].src = img(name); }      // 这一卷的图先载上，翻到哪一章都不等
    if (p) showPage(p.id, opts); else showToc();
    const S = seq(), i = S.findIndex(([vv, pp]) => vv === wbVol && pp === wbPage);
    tp.disabled = i <= 0; tx.disabled = i >= S.length - 1;
  }

  function ribHTML() {
    rib.innerHTML = VOL_ORDER.map(([id, t]) => {
      const v = volOf(id);
      return v ? `<button class="rb" type="button" data-v="${id}" data-c="${id}" aria-current="${id === wbVol}"><img src="${A('common/assets/ui/' + EMB[id] + '.webp')}" alt=""><span>${esc(v.title)}</span></button>`
        : `<span class="rb off" data-c="${id}" aria-disabled="true"><img src="${A('common/assets/ui/' + EMB[id] + '.webp')}" alt=""><span>${t}</span></span>`;
    }).join('');
    if (!twoPage()) {      // 手机上缎带排成顶上一条，当前那一卷挪到看得见的地方（只动这一条自己的横向卷动，不碰外面）
      const a = rib.querySelector('.rb[aria-current="true"]');
      if (a) rib.scrollLeft = Math.max(0, a.offsetLeft - (rib.clientWidth - a.offsetWidth) / 2);
    }
  }

  const corners = '<i class="bc tl"></i><i class="bc tr"></i><i class="bc bl"></i><i class="bc br"></i>';

  // 扉页和目录：左页卷名、徽记、扉页的小画、题记，右页各章
  function showToc() {
    const v = volOf(wbVol), front = (DR.front || {})[wbVol], epi = (DR.epi || {})[wbVol];
    const [yrs, motto] = String(v.sub || '').split('　');
    wbPage = ''; bk.classList.remove('wide'); MAPAPPLY = null;
    pl.innerHTML = `<div class="tt"><p class="rh">世界之书</p><img class="em" src="${A('common/assets/ui/' + EMB[wbVol] + '.webp')}" alt="">`
      + `<h1>${esc(v.title)}<small>卷</small></h1>${yrs ? `<p class="yrs">${esc(yrs)}</p>` : ''}${motto ? `<p class="mot">${esc(motto)}</p>` : ''}`
      + `${front ? `<div class="fr"><img src="${img(front)}" alt="">${corners}</div>` : ''}`
      + `${epi ? `<blockquote class="epi"><p>${esc(epi[0])}</p><cite>${esc(epi[1])}</cite></blockquote>` : ''}</div>`;
    pr.innerHTML = `<p class="rh r">目录</p><ol class="toc">${v.pages.map((p, k) => {
      const b = ban(wbVol, p.id);
      return `<li><button type="button" data-p="${p.id}"><i class="th${b ? '' : ' none'}"${b ? ` style="background-image:url('${img(b)}')"` : ''}></i>`
        + `<b>第${NUM[k] || k + 1}章</b><span>${esc(p.title)}</span>${p.sub ? `<small>${esc(p.sub)}</small>` : ''}</button></li>`;
    }).join('')}</ol>`;
    pr.scrollTop = 0; spread.scrollTop = 0;
  }

  // 正文里地图上有的地方：一卷一张名单，长的先认，同一章里每个名字只点亮头一回
  function terms(vol) {
    if (TERMS[vol] !== undefined) return TERMS[vol];
    const MD = MAPS[vol];
    if (!MD) { TERMS[vol] = null; return null; }
    const info = {};
    MD.periods.forEach((p, k) => p.pins.forEach((q) => { if (q.name && q.name.length >= 2 && !info[q.name]) info[q.name] = { k, q }; }));
    const names = Object.keys(info).sort((a, b) => b.length - a.length);
    TERMS[vol] = names.length ? { re: new RegExp(names.map(reEsc).join('|'), 'g'), info } : null;
    return TERMS[vol];
  }
  function link(t, used) {
    const T = terms(wbVol), s = esc(t);
    if (!T) return s;
    return s.replace(T.re, (m) => { if (used.has(m)) return m; used.add(m); return `<button type="button" class="tm" data-t="${m}">${m}</button>`; });
  }

  function showPage(pid, opts) {
    const v = volOf(wbVol), pages = v.pages, k = Math.max(0, pages.findIndex((x) => x.id === pid)), p = pages[k];
    wbPage = p.id;
    const hasMap = p.id === 'map' && MAPS[wbVol], used = new Set(), b = ban(wbVol, p.id), epi = k === 0 ? (DR.epi || {})[wbVol] : null;
    bk.classList.toggle('wide', !!hasMap);
    const prev = pages[k - 1], next = pages[k + 1];
    const nav = `<div class="nav">${prev ? `<button type="button" data-p="${prev.id}">‹　${esc(prev.title)}</button>` : '<button type="button" data-p="">‹　目录</button>'}`
      + `${next ? `<button type="button" data-p="${next.id}">${esc(next.title)}　›</button>` : '<span></span>'}</div>`;
    const secs = (p.sections || []).map((s, i) => `${i ? '<i class="fl"></i>' : ''}<section data-i="${i}">${s.h ? `<h3>${esc(s.h)}</h3>` : ''}<p${i ? '' : ' class="dc"'}>${link(s.t, used)}</p></section>`).join('');
    if (hasMap) {
      pl.innerHTML = '';
      pr.innerHTML = `<p class="rh r">世界之书 · ${esc(v.title)}卷</p><div class="mh"><p class="chno">第${NUM[k] || k + 1}章</p><h1>${esc(p.title)}</h1>${p.sub ? `<p class="sub">${esc(p.sub)}</p>` : ''}</div>`
        + `<div class="wm"></div><div class="body">${secs}</div>${nav}`;
    } else {
      const outline = (p.sections || []).length >= 3 ? `<ol class="ol">${p.sections.map((s, i) => `<li><button type="button" data-sec="${i}">${esc(s.h || '')}</button></li>`).join('')}</ol>` : '';
      pl.innerHTML = `<p class="rh">世界之书 · ${esc(v.title)}卷</p>${b ? `<div class="ban" style="background-image:url('${img(b)}')">${corners}</div>` : ''}`
        + `<p class="chno">第${NUM[k] || k + 1}章</p><h1>${esc(p.title)}</h1>${p.sub ? `<p class="sub">${esc(p.sub)}</p>` : ''}`
        + `${epi ? `<blockquote class="epi"><p>${esc(epi[0])}</p><cite>${esc(epi[1])}</cite></blockquote>` : '<i class="fl sm"></i>'}`
        + `${p.kind === 'chron' ? `<div class="cn">${SPL}<p>${(p.items || []).length} 件事，照年份排。剧透开着的时候，往后那一半也显出来。</p></div>` : outline}<p class="folio">${NUM[k] || k + 1}</p>`;
      let body;
      if (p.kind === 'chron') body = `<ol class="chron">${(p.items || []).map((it) => `<li${it.spoil ? ' class="spoil"' : ''}><b>${esc(it.y)}</b><p>${link(it.t, used)}</p></li>`).join('')}</ol>`;
      else body = `<div class="body">${secs}</div>`;
      pr.innerHTML = `<p class="rh r">${esc(p.title)}</p>${body}${nav}`;
    }
    pr.scrollTop = 0; spread.scrollTop = 0; MAPAPPLY = null;
    if (hasMap) {
      const host = pr.querySelector('.wm');
      mountMap(host, MAPS[wbVol], wbVol, opts || {});
      if ((opts || {}).era || (opts || {}).focus) requestAnimationFrame(() => { const s = scroller(); s.scrollTop = Math.max(0, host.offsetTop - 60); });
    }
  }

  // 正文里点一个地方：小卡（它是什么、在哪、往后叫什么），带一个钮翻到地图上
  function showTip(btn) {
    hideTip();
    const T = terms(wbVol), it = T && T.info[btn.dataset.t];
    if (!it) return;
    const q = it.q, rr = root.getBoundingClientRect(), r = btn.getBoundingClientRect();
    tip = document.createElement('div');
    tip.className = 'wtip'; tip.dataset.v = wbVol;
    tip.innerHTML = `<b>${esc(q.name)}</b>${q.kind ? `<em>${esc(q.kind)}</em>` : ''}${q.where ? `<p>${esc(q.where)}</p>` : ''}`
      + `${q.later ? `<i>到迷宫纪 1001 年，这里叫${esc(q.later)}</i>` : ''}<button type="button" class="go" data-mk="${it.k}" data-mf="${esc(q.name)}">在地图上看 ›</button>`;
    root.appendChild(tip);
    btn.classList.add('on');
    const w = tip.offsetWidth, h = tip.offsetHeight;
    let x = clamp(r.left - rr.left - 20, 10, rr.width - w - 10), y = r.top - rr.top - h - 12, below = false;
    if (y < 10) { y = r.bottom - rr.top + 12; below = true; }
    y = clamp(y, 10, Math.max(10, rr.height - h - 10));
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
    tip.style.setProperty('--ax', clamp(r.left - rr.left - x + r.width / 2, 16, w - 16) + 'px');
    tip.classList.toggle('below', below);
  }
  function hideTip() {
    if (!tip) return;
    tip.remove(); tip = null;
    for (const b of root.querySelectorAll('.tm.on')) b.classList.remove('on');
  }

  /* 地图：一个年代一张底图，点照地点谱的坐标落。滚轮、两指缩放，按住拖，点一处出小卡，
     小卡底下是提到这一处的时代，点了合上书、进那个时代页（交给 C.onEra）。从时代页翻过来的，那一页提到的地方亮着。 */
  function mountMap(host, MD, vol, opts) {
    const P = MD.periods, names = MD.names || {};
    let pi = opts.period != null && P[opts.period] ? opts.period : opts.era ? Math.max(0, P.findIndex((p) => p.eras.includes(opts.era))) : 0;
    host.innerHTML = `<div class="wm-tabs">${P.map((p, k) => `<button type="button" data-k="${k}" aria-pressed="${k === pi}">${esc(p.name)}<small>${esc(p.sub)}</small></button>`).join('')}</div>`
      + '<div class="wm-frame"><div class="wm-in"><img alt=""><div class="wm-pins"></div></div><div class="wm-zoom"><button type="button" data-z="1" aria-label="放大">+</button><button type="button" data-z="-1" aria-label="缩小">−</button></div><div class="wm-card" hidden></div></div><p class="wm-note"></p>';
    const frame = host.querySelector('.wm-frame'), inner = host.querySelector('.wm-in'), img = inner.querySelector('img'), pinsEl = inner.querySelector('.wm-pins'), card = host.querySelector('.wm-card'), note = host.querySelector('.wm-note');
    let s = 1, tx = 0, ty = 0, recenter = true;
    // 底图照原比例铺满框（框比图高就左右能拖，手机上框是竖的），点的位置是底图上的百分数
    const base = () => { const fw = frame.clientWidth, fh = frame.clientHeight; return fw / fh > AR ? [fw, fw / AR] : [fh * AR, fh]; };
    const apply = () => {
      const fw = frame.clientWidth, fh = frame.clientHeight, [bw, bh] = base();
      if (!fw || !fh) return;                       // 书还藏着、量不到框，等 ResizeObserver 再来
      if (recenter) { tx = (fw - bw) / 2; ty = (fh - bh) / 2; recenter = false; }
      inner.style.width = bw.toFixed(1) + 'px'; inner.style.height = bh.toFixed(1) + 'px';
      s = clamp(s, 1, 6); tx = clamp(tx, fw - bw * s, 0); ty = clamp(ty, fh - bh * s, 0);
      inner.style.transform = `translate(${tx.toFixed(1)}px,${ty.toFixed(1)}px) scale(${s.toFixed(4)})`;
      inner.style.setProperty('--is', (1 / s).toFixed(4));
      frame.classList.toggle('z2', s >= 1.9);
    };
    MAPAPPLY = apply;
    const zoomAt = (f, cx, cy) => { const ns = clamp(s * f, 1, 6), k = ns / s; tx = cx - (cx - tx) * k; ty = cy - (cy - ty) * k; s = ns; apply(); };
    const showCard = (j) => {
      const q = P[pi].pins[j];
      for (const b of pinsEl.children) b.classList.toggle('sel', +b.dataset.j === j);
      card.innerHTML = `<button type="button" class="cx" aria-label="合上">×</button><b>${esc(q.name)}</b>${q.kind ? `<span>${esc(q.kind)}</span>` : ''}${q.where ? `<p>${esc(q.where)}</p>` : ''}`
        + `${q.later ? `<em>到迷宫纪 1001 年，这里叫${esc(q.later)}</em>` : ''}`
        + `${(q.eras || []).length ? `<div class="eras">${q.eras.map((id) => `<button type="button" data-era="${id}">${esc(names[id] || id)}</button>`).join('')}</div>` : ''}`;
      card.hidden = false;
    };
    const focusPin = (j) => {
      const q = P[pi].pins[j], fw = frame.clientWidth, fh = frame.clientHeight, [bw, bh] = base();
      s = Math.max(s, fw < 600 ? 1.6 : 2.4); tx = fw / 2 - q.x / 100 * bw * s; ty = fh / 2 - q.y / 100 * bh * s; apply(); showCard(j);
    };
    const show = (k) => {
      pi = k; const p = P[k], hl = opts.era && p.eras.includes(opts.era) ? opts.era : '';
      for (const b of host.querySelectorAll('.wm-tabs button')) b.setAttribute('aria-pressed', String(+b.dataset.k === k));
      img.src = A('common/assets/map/' + p.img + '.webp'); inner.classList.toggle('night', !!p.night);
      frame.classList.toggle('dim', !!hl);
      pinsEl.innerHTML = p.pins.map((q, j) => `<button type="button" class="wm-pin${q.main ? ' main' : ' lo'}${hl && (q.eras || []).includes(hl) ? ' hi' : ''}" data-j="${j}" style="left:${q.x}%;top:${q.y}%" aria-label="${esc(q.name)}"><i></i><b>${esc(q.name)}</b></button>`).join('');
      card.hidden = true; s = 1; recenter = true; apply();
      note.textContent = `${p.name}，${p.sub}。${p.borrow ? p.borrow + '。' : ''}图上 ${p.pins.length} 处，${hl ? '亮着的是这一页提到的地方，' : ''}点一处看它是什么。滚轮或两指缩放，按住拖动。`;
    };
    host.querySelector('.wm-tabs').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) show(+b.dataset.k); });
    host.querySelector('.wm-zoom').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) zoomAt(+b.dataset.z > 0 ? 1.5 : 1 / 1.5, frame.clientWidth / 2, frame.clientHeight / 2); });
    card.addEventListener('click', (e) => {
      if (e.target.closest('.cx')) { card.hidden = true; for (const b of pinsEl.children) b.classList.remove('sel'); return; }
      const b = e.target.closest('[data-era]');
      if (b) { const id = b.dataset.era; close(); C.onEra(vol, id); }
    });
    pinsEl.addEventListener('click', (e) => { if (e.detail === 0) { const b = e.target.closest('.wm-pin'); if (b) showCard(+b.dataset.j); } });      // 键盘回车
    const pts = new Map(); let moved = false, pinch = 0, downPin = -1;
    frame.addEventListener('pointerdown', (e) => {
      if (e.target.closest('.wm-zoom,.wm-card')) return;
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (pts.size === 1) { moved = false; const pb = e.target.closest('.wm-pin'); downPin = pb ? +pb.dataset.j : -1; }
      try { frame.setPointerCapture(e.pointerId); } catch (err) { /* 有的浏览器不认 */ }
      frame.classList.add('drag');
      if (pts.size === 2) { const [a, b] = [...pts.values()]; pinch = Math.hypot(a.x - b.x, a.y - b.y); moved = true; }
    });
    frame.addEventListener('pointermove', (e) => {
      const o = pts.get(e.pointerId); if (!o) return;
      const dx = e.clientX - o.x, dy = e.clientY - o.y;
      if (Math.abs(dx) + Math.abs(dy) > 2) moved = true;
      o.x = e.clientX; o.y = e.clientY;
      if (pts.size === 1) { tx += dx; ty += dy; apply(); }
      else if (pts.size === 2) { const [a, b] = [...pts.values()], d = Math.hypot(a.x - b.x, a.y - b.y), r = frame.getBoundingClientRect(); if (pinch) zoomAt(d / pinch, (a.x + b.x) / 2 - r.left, (a.y + b.y) / 2 - r.top); pinch = d; }
    });
    const up = (e) => {
      if (!pts.has(e.pointerId)) return;
      pts.delete(e.pointerId); pinch = 0;
      if (!pts.size) { frame.classList.remove('drag'); if (!moved && downPin >= 0) showCard(downPin); }
    };
    frame.addEventListener('pointerup', up); frame.addEventListener('pointercancel', up);
    frame.addEventListener('wheel', (e) => { e.preventDefault(); const r = frame.getBoundingClientRect(); zoomAt(e.deltaY < 0 ? 1.18 : 1 / 1.18, e.clientX - r.left, e.clientY - r.top); }, { passive: false });
    frame.addEventListener('dblclick', (e) => { const r = frame.getBoundingClientRect(); zoomAt(1.8, e.clientX - r.left, e.clientY - r.top); });
    show(pi);
    if (window.ResizeObserver) new ResizeObserver(() => { if (MAPAPPLY === apply) apply(); }).observe(frame);
    if (opts.focus) { const j = P[pi].pins.findIndex((q) => q.name === opts.focus); if (j >= 0) requestAnimationFrame(() => focusPin(j)); }
  }

  /* 时代页“这一带”：这个年代那一张地图缩小了放在这里，这一页提到的地方亮着，点了翻到世界之书的地图 */
  function mini(vol, eraId, places) {
    const MD = MAPS[vol];
    if (!MD || !places || !places.length) return '';
    const k = MD.periods.findIndex((p) => p.eras.includes(eraId));
    if (k < 0) return '';
    const p = MD.periods[k], pins = p.pins.filter((q) => (q.eras || []).includes(eraId));
    if (!pins.length) return '';                      // 这一段的地方一个也没落在图上，就不出这一栏（空着一张图没用）
    return `<h2>这一带</h2><button class="mini${p.night ? ' night' : ''}" type="button" data-mv="${vol}" data-mk="${k}" aria-label="在世界之书里看这一带的地图"><img loading="lazy" src="${A('common/assets/map/' + p.img + '.webp')}" alt="">`
      + pins.map((q) => `<i style="left:${q.x}%;top:${q.y}%"></i>`).join('') + `<span>在世界之书里看地图</span></button>`
      + `<div class="mini-names">${places.map((x) => `<button type="button" data-mv="${vol}" data-mk="${k}" data-mf="${esc(x.name)}">${esc(x.name)}</button>`).join('')}</div>`;
  }
  function miniClick(ev, eraId) {
    const mk = ev.target.closest('[data-mk]');
    if (!mk) return false;
    open(mk.dataset.mv || C.vol, 'map', { period: +mk.dataset.mk, era: eraId, focus: mk.dataset.mf || '' });
    return true;
  }

  const api = {
    init, open, close, mini, miniClick, syncSpoil,
    isOpen: () => opened,
    ready: () => ready,
    get state() { return { open: opened, vol: wbVol, page: wbPage, vols: (WB.volumes || []).map((v) => v.id), maps: Object.keys(MAPS) }; },
  };
  window.Codex = api;
})();
