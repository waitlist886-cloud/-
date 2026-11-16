/* 世界之书（11-15 介绍页收尾）：四本书和牌桌共用的一份。从月银纪那一本（小样_月银纪书/index.html）抽出来的。
   一本书，五卷（通用、月银纪、纷争纪、山铜纪、迷宫纪），字在 共用/data/wb.json（底稿/门面/卡片/世界之书.json 拷过来的）；
   各纪卷的“山河与地图”那一页放一张能点的地图，点在 共用/data/map_<卷>.json（prep_maps.py 出），底图在 共用/assets/map/。
   用法（书里）：
     await Codex.init({ vol: 'moon', host: 某个 position:fixed/absolute 撑满屏的元素, A, spoil: () => SPOIL, setSpoil, onEra, onOpen, onClose });
     Codex.open(卷, 页, { period, era, focus }) 打开；Codex.close()；Codex.isOpen()；
     Codex.mini(卷, 时代 id, 这一页的地方) 出时代页“这一带”那一小幅地图的 html，点击交给 Codex.miniClick(ev, 卷, 时代 id)。
   A(p) 是地址怎么换：单独打开一本书的时候原样，装在牌桌那个外壳里的时候换成图床的地址。 */
(function () {
  'use strict';
  const VOL_ORDER = [['general', '通用'], ['moon', '月银纪'], ['strife', '纷争纪'], ['bronze', '山铜纪'], ['maze', '迷宫纪']];
  const AR = 3072 / 1955;            // 底图都是 Azgaar 那一张整图（2200×1400）截的，宽高比一样
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const SPL = '<button class="spl" type="button" aria-label="剧透开关"><i></i><span>剧透　<em class="off">关着，谁死在哪里、主线怎么收场都不显示</em><em class="on">开着</em></span></button>';
  let C = null, WB = { volumes: [] }, root = null, wbVols, wbPgs, wbMain, opened = false, wbVol = 'general', wbPage = '', MAPAPPLY = null, ready = null;
  const MAPS = {};
  const A = (p) => (C && C.A ? C.A(p) : p);
  const volOf = (id) => (WB.volumes || []).find((v) => v.id === id);
  const spoilOn = () => !!(C && C.spoil && C.spoil());

  function build() {
    root = document.createElement('div');
    root.id = 'wb'; root.hidden = true;
    root.setAttribute('role', 'dialog'); root.setAttribute('aria-label', '世界之书');
    root.innerHTML = `<div class="bk"><nav class="rail"><h2><img src="${A('common/assets/ui/wb_cover.webp')}" alt="">世界之书</h2><div class="vols"></div><div class="pgs"></div></nav><div class="main"></div></div><button class="x" type="button">合上</button>`;
    (C.host || document.body).appendChild(root);
    wbVols = root.querySelector('.vols'); wbPgs = root.querySelector('.pgs'); wbMain = root.querySelector('.main');
    root.addEventListener('click', (ev) => {
      if (ev.target.closest('#wb > .x') || ev.target === root) { close(); return; }
      if (ev.target.closest('.spl')) { const y = wbMain.scrollTop; C.setSpoil(!spoilOn()); syncSpoil(); wbMain.scrollTop = y; return; }
      if (ev.target.closest('.wm')) return;
      const vb = ev.target.closest('.vol[data-v]'); if (vb) { wbVol = vb.dataset.v; showPage('', {}); return; }
      const pb = ev.target.closest('[data-p]'); if (pb) showPage(pb.dataset.p, {});
    });
    for (const ev of ['pointerdown', 'pointerup', 'pointermove', 'wheel', 'touchstart', 'touchmove']) root.addEventListener(ev, (e) => e.stopPropagation(), { passive: true });
    window.addEventListener('keydown', (e) => { if (opened && e.key === 'Escape') { e.stopPropagation(); e.preventDefault(); close(); } }, true);
    window.addEventListener('resize', () => { if (MAPAPPLY) MAPAPPLY(); });
  }

  function init(cfg) {
    C = Object.assign({ vol: 'general', host: null, A: null, spoil: () => false, setSpoil: () => {}, onEra: () => {}, onOpen: () => {}, onClose: () => {} }, cfg || {});
    wbVol = C.vol;
    build();
    const get = (p, d) => fetch(A(p)).then((r) => (r.ok ? r.json() : d)).catch(() => d);
    ready = Promise.all([get('common/data/wb.json', { volumes: [] })].concat(VOL_ORDER.slice(1).map(([id]) => get('common/data/map_' + id + '.json', null))))
      .then(([wb, ...maps]) => { WB = wb || { volumes: [] }; VOL_ORDER.slice(1).forEach(([id], k) => { if (maps[k]) MAPS[id] = maps[k]; }); return api; });
    return ready;
  }

  function syncSpoil() { if (root) root.classList.toggle('spoil-on', spoilOn()); }

  function open(vol, page, opts) {
    if (!root) return;
    wbVol = volOf(vol) ? vol : volOf(C.vol) ? C.vol : ((WB.volumes || [])[0] || {}).id;
    if (!wbVol) return;
    C.onOpen(); root.hidden = false; opened = true;          // 先露出来再排版，地图量得到框
    syncSpoil(); showPage(page, opts || {});
    requestAnimationFrame(() => root.classList.add('on'));
  }
  function close() {
    if (!opened) return;
    opened = false; root.classList.remove('on'); MAPAPPLY = null;
    setTimeout(() => { if (!opened) root.hidden = true; }, 380);
    C.onClose();
  }
  function railHTML() {
    wbVols.innerHTML = VOL_ORDER.map(([id, t]) => {
      const v = volOf(id);
      return v ? `<button class="vol" type="button" data-v="${id}" aria-current="${id === wbVol}">${esc(v.title)}${v.sub ? `<small>${esc(v.sub)}</small>` : ''}</button>`
        : `<span class="vol off" aria-disabled="true">${t}<small>这一卷还在写</small></span>`;
    }).join('');
    wbPgs.innerHTML = volOf(wbVol).pages.map((p) => `<button class="pg" type="button" data-p="${p.id}" aria-current="${p.id === wbPage}">${esc(p.title)}</button>`).join('');
  }
  function showPage(pid, opts) {
    const v = volOf(wbVol), pages = v.pages, p = pages.find((x) => x.id === pid) || pages[0];
    wbPage = p.id; railHTML();
    let h = `<p class="eb">世界之书　${esc(v.title)}</p><h1>${esc(p.title)}</h1>${p.sub ? `<p class="sub">${esc(p.sub)}</p>` : ''}`;
    const hasMap = p.id === 'map' && MAPS[wbVol];
    if (hasMap) h += '<div class="wm"></div>';             // 地图那一页图在前，字在图后
    if (p.kind === 'chron') h += SPL + `<ol class="chron">${(p.items || []).map((it) => `<li${it.spoil ? ' class="spoil"' : ''}><b>${esc(it.y)}</b><p>${esc(it.t)}</p></li>`).join('')}</ol>`;
    else h += (p.sections || []).map((s) => `<section>${s.h ? `<h3>${esc(s.h)}</h3>` : ''}<p>${esc(s.t)}</p></section>`).join('');
    const k = pages.indexOf(p), prev = pages[k - 1], next = pages[k + 1];
    h += `<div class="turn">${prev ? `<button type="button" data-p="${prev.id}">‹　${esc(prev.title)}</button>` : '<span></span>'}${next ? `<button type="button" data-p="${next.id}">${esc(next.title)}　›</button>` : '<span></span>'}</div>`;
    wbMain.innerHTML = h; wbMain.scrollTop = 0; MAPAPPLY = null;
    if (hasMap) {
      const host = wbMain.querySelector('.wm');
      mountMap(host, MAPS[wbVol], wbVol, opts);
      if (opts.era || opts.focus) requestAnimationFrame(() => { wbMain.scrollTop = Math.max(0, host.offsetTop - 70); });
    }
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
