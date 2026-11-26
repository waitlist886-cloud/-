/* 图鉴（11-17 前端精修）：四本书共用的一份，一纪一本。字在各本书的 data/atlas.json（共用/build_atlas.py 出）。
   顶上一条年代轴（全纪加这一纪的各个时代），四个页签：人物、强敌、神、生物。点人物交给书里开档案，别的在右边一栏看。
   用法（书里）：
     await Atlas.init({ vol, host, A, spoil: () => SPOIL, setSpoil, openPerson: (时代 id, 名字) => …, goEra: (时代 id) => …, curEra: () => 时代 id 或 null, onOpen, onClose });
     Atlas.open(时代 id 或不写)；Atlas.close()；Atlas.isOpen()；Atlas.syncSpoil()（剧透开关在别处切了，叫它跟上）。 */
(function () {
  'use strict';
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const TABS = [['people', '人物'], ['foes', '强敌'], ['gods', '神'], ['beasts', '生物']];
  const ELEM = { 赤火: '#e0654a', 橙冰: '#f0a35a', 黄岩: '#cfa94c', 绿草: '#7fb46a', 青风: '#5fc6c0', 蓝水: '#5b8fd8', 紫雷: '#a07ad8' };
  const SPL = '<button class="a-spl" type="button" aria-label="剧透开关"><i></i><span>剧透　<em class="off">关着</em><em class="on">开着</em></span></button>';
  let C = null, D = null, root = null, axis, bar, chips, list, panel, opened = false, ready = null, want = null, warmed = null;
  let per = 'all', tab = 'people', chip = '全部', sel = null;
  // 图床的几个镜像（跟薄壳那一份一样）：头一个取不到 atlas.json 就换下一个
  const MIR = ['https://cdn.jsdelivr.net/', 'https://fastly.jsdelivr.net/', 'https://gcore.jsdelivr.net/', 'https://testingcf.jsdelivr.net/', 'https://quantil.jsdelivr.net/'];
  const A = (p) => (C && C.A ? C.A(p) : p);
  const spoilOn = () => !!(C && C.spoil && C.spoil());
  const reduced = () => window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const narrow = () => window.matchMedia && matchMedia('(max-width: 760px)').matches;
  const perOf = (id) => (D.periods || []).find((p) => p.id === id);

  function build() {
    root = document.createElement('div');
    root.id = 'atl'; root.hidden = true; root.dataset.v = C.vol;
    root.setAttribute('role', 'dialog'); root.setAttribute('aria-label', '图鉴');
    root.innerHTML = '<div class="at-bg"></div><div class="at-wrap">'
      + '<header class="at-hd"><img class="a-em" alt=""><h1></h1><span class="a-sp"></span>' + SPL + '<button class="a-x" type="button"><b>×</b>合上</button></header>'
      + '<nav class="at-axis" aria-label="年代"></nav>'
      + '<div class="at-bar" role="tablist"></div><div class="at-chips"></div>'
      + '<div class="at-main"><div class="at-list"></div><aside class="at-panel" aria-live="polite"></aside></div></div>';
    (C.host || document.body).appendChild(root);
    axis = root.querySelector('.at-axis'); bar = root.querySelector('.at-bar'); chips = root.querySelector('.at-chips');
    list = root.querySelector('.at-list'); panel = root.querySelector('.at-panel');
    root.addEventListener('click', onClick);
    for (const ev of ['pointerdown', 'pointerup', 'pointermove', 'wheel', 'touchstart', 'touchmove']) root.addEventListener(ev, (e) => e.stopPropagation(), { passive: true });
    window.addEventListener('keydown', (e) => {
      if (!opened || e.key !== 'Escape') return;
      e.stopPropagation(); e.preventDefault();
      if (C.onEsc()) return;          // 书里有东西盖在图鉴上面（点人开的档案），先合它
      const zm = root.querySelector('.a-zoom');
      if (zm) { zm.remove(); return; }          // 楼层主的大图先合
      if (root.classList.contains('pan') && narrow()) closePanel(); else close();
    }, true);
  }

  function init(cfg) {
    C = Object.assign({ vol: 'moon', host: null, A: null, spoil: () => false, setSpoil: () => {}, openPerson: () => {}, goEra: () => {}, curEra: () => null, onOpen: () => {}, onClose: () => {}, onEsc: () => false }, cfg || {});
    build();
    return load();
  }
  /* 取 atlas.json（11-17 夜）：头一个地址取不到就换镜像再取；几个都 404 才算这一本没有图鉴（书里会把钮藏起来），
     网断了、慢的不算没有，钮留着，点开照样等、照样能再取一回。取到以后歇一会儿把小图先载上。 */
  function load() {
    const u = A('data/atlas.json');
    let abs = u;
    try { abs = new URL(u, document.baseURI).href; } catch (e) { /* 照原样 */ }
    const tries = [u], m = MIR.find((h) => abs.indexOf(h) === 0);
    if (m) for (const h of MIR) if (h !== m) tries.push(h + abs.slice(m.length));
    let gone = 0;
    const next = (k) => (k >= tries.length ? Promise.resolve(null)
      : fetch(tries[k]).then((r) => { if (r.ok) return r.json(); if (r.status === 404) gone++; throw new Error(r.status); }).catch(() => next(k + 1)));
    ready = next(0).then((d) => {
      D = d; api.missing = !d && gone === tries.length;
      if (d) {
        root.querySelector('.a-em').src = A(d.emblem);
        root.querySelector('h1').innerHTML = esc(d.name) + '<small>' + esc(d.sub) + '</small>';
        setTimeout(() => (window.requestIdleCallback || ((f) => setTimeout(f, 0)))(warm), 2500);
      }
      return api;
    });
    return ready;
  }
  /* 小图先载上（11-17 夜）：图鉴头一屏要的那几张（徽、年代轴、人物小图）在书里先取一遍，点开图鉴就不用等。省流量的设置开着就不取。 */
  function warm() {
    if (!D || warmed || (navigator.connection && navigator.connection.saveData)) return;
    const urls = [];
    if (D.emblem) urls.push(A(D.emblem));
    if (D.ax) urls.push(A('assets/at/ax.webp'));
    for (const k of Object.keys(D.th || {})) urls.push(A('assets/at/' + k + '.webp'));
    warmed = [];
    let i = 0;
    const one = () => { if (i >= urls.length) return; const im = new Image(); warmed.push(im); im.onload = im.onerror = one; im.src = urls[i++]; };
    one(); one();
  }
  /* 点开的时候数据还没到：先把图鉴摆出来写“正在取”，到了再画；取不下来写一句、给一个再取的钮。不再点了没反应。 */
  function waitOpen(eraId) {
    want = eraId || null;
    C.onOpen(); root.hidden = false; opened = true; root.classList.add('wait');
    axis.innerHTML = ''; bar.innerHTML = ''; chips.innerHTML = ''; panel.innerHTML = '';
    list.innerHTML = '<p class="a-empty">图鉴正在取，稍等一下。</p>';
    requestAnimationFrame(() => root.classList.add('on'));
    const go = () => {
      if (!opened) return;
      root.classList.remove('wait');
      if (D) { opened = false; open(want); } else list.innerHTML = '<p class="a-empty">图鉴没取下来，多半是网络卡住了。</p><div class="a-btns" style="max-width:240px"><button class="a-bt pri a-retry" type="button">再取一次</button></div>';
    };
    (ready || Promise.resolve()).then(go, go);
  }

  function open(eraId) {
    if (!root) return;
    if (!D) { waitOpen(eraId); return; }
    const cur = eraId || (C.curEra && C.curEra());
    per = cur && perOf(cur) ? cur : 'all';
    sel = null; chip = '全部';
    C.onOpen(); root.hidden = false; opened = true; root.classList.remove('wait');
    syncSpoil(); renderAll();
    requestAnimationFrame(() => { root.classList.add('on'); centerAxis(); });
  }
  function close() {
    if (!opened) return;
    opened = false; root.classList.remove('on', 'pan');
    setTimeout(() => { if (!opened) root.hidden = true; }, 340);
    C.onClose();
  }
  function syncSpoil() {
    if (!root) return;
    root.classList.toggle('spoil-on', spoilOn());
    if (opened) { renderTabs(); renderList(); if (sel) renderPanel(); }
  }

  /* ---------- 挑数据 ---------- */
  const inPer = (x) => per === 'all' || (x.at && (Array.isArray(x.at) ? x.at.includes(per) : x.at[per]));
  const hiddenFoe = (f) => /隐藏/.test(f.n);
  // 楼层主（11-26，此刻那一本）：nx 是剧透开了的真名（凯尔萨斯、拉奇埃尔、薪火之国那三位），关着用 n
  const foeName = (x) => (x.nx && spoilOn() ? x.nx : x.n.replace(/·隐藏\s*/, '·'));
  function kindOf(t, x) {
    if (t === 'people') { const k = per === 'all' ? Object.values(x.at)[0] : x.at[per]; return k || '旅伴'; }
    if (t === 'foes') return x.k || '强敌';
    if (t === 'gods') return x.side === '柱' ? '七支柱' : x.side === '魔' ? '魔神' : '正神';
    return x.kind || '魔物';
  }
  function items(t) {
    let xs = (D[t] || []).filter(inPer);
    if (t === 'foes' && !spoilOn()) xs = xs.filter((f) => !hiddenFoe(f));
    if (t === 'people') {
      const rank = { 旅伴: 0, 相遇: 1, 传奇: 2 };
      xs = xs.slice().sort((a, b) => rank[kindOf(t, a)] - rank[kindOf(t, b)]);
    }
    return xs;
  }
  function chipList(t, xs) {
    const seen = [];
    for (const x of xs) { const k = kindOf(t, x); if (!seen.includes(k)) seen.push(k); }
    const order = { people: ['旅伴', '相遇', '传奇'], gods: ['七支柱', '正神', '魔神'], beasts: ['魔物', '魔兽', '坐骑'] }[t] || [];
    return seen.sort((a, b) => (order.indexOf(a) + 9) % 99 - (order.indexOf(b) + 9) % 99);
  }

  /* ---------- 画 ---------- */
  function renderAll() { renderAxis(); renderTabs(); renderList(); renderPanel(); }

  // 年代轴的小圆点：有拼好的小图（D.ax）就从那一张里取那一格，没有照旧用整幅时代图
  function dot(p) {
    if (D.ax && p.tx != null) {
      const c = D.ax[0], r = D.ax[1], x = p.tx % c, y = Math.floor(p.tx / c);
      return ` style="background-image:url('${A('assets/at/ax.webp')}');background-size:${c * 100}% ${r * 100}%;background-position:${c > 1 ? (x / (c - 1)) * 100 : 0}% ${r > 1 ? (y / (r - 1)) * 100 : 0}%"`;
    }
    return p.img ? ` style="background-image:url('${A(p.img)}')"` : '';
  }
  function renderAxis() {
    const P = D.periods || [];
    let h = `<button class="a-stop all${per === 'all' ? ' on' : ''}" type="button" data-per="all"><span class="a-dot">全纪</span><b>${esc(D.era)}</b></button>`;
    let part = null;
    P.forEach((p) => {
      const lead = p.part != null && p.part !== part ? ' lead' : ''; part = p.part;
      h += `<button class="a-stop${per === p.id ? ' on' : ''}${lead}" type="button" data-per="${p.id}"><span class="a-dot"${dot(p)}></span>`
        + `<b>${esc(p.t)}</b><small>${esc(p.lb ? p.lb + ' · ' : '')}${esc(p.y)}</small></button>`;
    });
    axis.innerHTML = h;
    const p = perOf(per);
    root.querySelector('.at-bg').style.backgroundImage = p && p.img ? `url('${A(p.img)}')` : 'none';
  }
  function centerAxis() {
    const on = axis.querySelector('.a-stop.on');
    if (on && axis.scrollWidth > axis.clientWidth) axis.scrollLeft = on.offsetLeft - axis.clientWidth / 2 + on.offsetWidth / 2;
  }

  function renderTabs() {
    bar.innerHTML = TABS.filter(([t]) => t === tab || (D[t] || []).length).map(([t, n]) => `<button class="a-tab" type="button" role="tab" data-tab="${t}" aria-selected="${t === tab}">${n}<sup>${items(t).length}</sup></button>`).join('');
    const xs = items(tab), cs = chipList(tab, xs);
    if (!cs.includes(chip)) chip = '全部';
    chips.innerHTML = cs.length > 1 ? ['全部'].concat(cs).map((c) => `<button class="a-chip" type="button" data-chip="${esc(c)}" aria-pressed="${c === chip}">${esc(c)}${c === '全部' ? '' : ` <small>${xs.filter((x) => kindOf(tab, x) === c).length}</small>`}</button>`).join('') : '';
  }

  function sprite(x, cls) {
    // 名录里的卡用小图（prep_atlas_thumbs.py 出的 assets/at/），右边那张大像照旧用整张拼图
    const tdim = cls === 'a-im' && x.th && D.th && D.th[x.th[0]];
    if (tdim) {
      const c = tdim[0], r = tdim[1], i = x.th[1];
      return `<span class="${cls}"><i class="a-spr" style="--c:${c};--r:${r};--x:${i % c};--y:${Math.floor(i / c)};background-image:url('${A('assets/at/' + x.th[0] + '.webp')}')"></i></span>`;
    }
    const dim = x.pa && D.pa[x.pa[0]];
    if (!dim) return `<span class="${cls} none"></span>`;
    const c = dim[0], r = dim[1], i = x.pa[1];
    return `<span class="${cls}"><i class="a-spr" style="--c:${c};--r:${r};--x:${i % c};--y:${Math.floor(i / c)};background-image:url('${A('assets/pa/' + x.pa[0] + '.webp')}')"></i></span>`;
  }
  const sigil = (x) => `<span class="a-im a-sig" style="--el:${ELEM[(x.elem || '').replace(/[。，].*$/, '')] || 'var(--acc2)'}"><i>${esc((x.n || '').replace(/[，·（].*$/, '').slice(-1))}</i></span>`;
  const pic = (u, pos) => (u ? `<span class="a-im"><img loading="lazy" decoding="async" alt="" src="${esc(u)}"${pos ? ` style="object-position:${pos}"` : ''}></span>` : '<span class="a-im none"></span>');

  function cardHTML(t, x, k) {
    const kind = kindOf(t, x), on = sel && sel.t === t && sel.i === k ? ' sel' : '';
    let im, sub = '', tags = `<span class="a-tg">${esc(kind)}</span>`;
    if (t === 'people') {
      im = sprite(x, 'a-im');
      sub = x.who || x.race || '';
      if (kind === '传奇' && x.title) tags += `<span class="a-tg lg">${esc(x.title)}</span>`;
      if (x.tier) tags += `<span class="a-tg">${esc(x.tier)}</span>`;
    } else if (t === 'foes') {
      if (x.fb) {          // 楼层主：图在书里（assets/fb/），没有图的画一块层号牌；几阶归剧透开关
        im = (x.ph[0] || {}).img ? pic(A(x.ph[0].img), '50% 22%') : fbSig(x, 'a-im');
        sub = x.full && x.full !== x.n ? x.full : (x.what || '');
        tags += `<span class="a-tg">${esc(x.fb.where.replace(/·.*$/, ''))}</span>`;
        if (spoilOn() && x.fb.st.length > 1) tags += `<span class="a-tg">${x.fb.st.length} 阶</span>`;
      } else {
      im = pic((x.ph[0] || {}).img ? A(x.ph[0].img) : '', '50% 30%');
      sub = x.full !== x.n ? x.full : (x.what || '');
      if (x.ph.length > 1) tags += `<span class="a-tg">${x.ph.length} 阶</span>`;
      }
      if (hiddenFoe(x)) tags += '<span class="a-tg lock">隐藏</span>';
    } else if (t === 'gods') {
      im = pic(x.img, '50% 16%');
      sub = (x.tag ? x.tag + '，' : '') + (x.rule || '');
    } else {
      im = sigil(x);
      sub = x.what || x.src || '';
      if (x.tier) tags += `<span class="a-tg lg">${esc(x.tier)}</span>`;
      else if (x.rank) tags += `<span class="a-tg">${esc(x.rank.split(/[，。]/)[0])}</span>`;
    }
    return `<button class="a-ac ${t}${on}" type="button" data-sel="${t}:${k}"><span class="a-fr">${im}</span><b class="a-nm">${esc(t === 'foes' ? foeName(x) : x.n)}</b><small class="a-who">${esc(sub)}</small><span class="a-tags">${tags}</span></button>`;
  }

  function renderList() {
    const xs = items(tab).filter((x) => chip === '全部' || kindOf(tab, x) === chip);
    const all = D[tab] || [];
    if (!xs.length) { list.innerHTML = '<p class="a-empty">这一段没有。</p>'; return; }
    if (tab === 'people' && chip === '全部') {
      const groups = chipList(tab, xs);
      const blurb = { 旅伴: '这个时代最有天分的年轻人', 相遇: '大人和老人，故事的配角', 传奇: '此刻在世的至强' };
      list.innerHTML = groups.map((g) => `<h3 class="a-grp">${esc(g)}<small>${esc(blurb[g] || '')}</small></h3><div class="a-grid">`
        + xs.filter((x) => kindOf(tab, x) === g).map((x) => cardHTML(tab, x, all.indexOf(x))).join('') + '</div>').join('');
    } else {
      list.innerHTML = `<div class="a-grid ${tab}">` + xs.map((x) => cardHTML(tab, x, all.indexOf(x))).join('') + '</div>';
    }
    list.scrollTop = 0;
  }

  function perChips(ids, limit) {
    const P = (Array.isArray(ids) ? ids : Object.keys(ids || {})).map(perOf).filter(Boolean);
    if (!P.length) return '';
    const show = P.slice(0, limit || 99);
    return `<p class="a-pers">${show.map((p) => `<button class="a-pc" type="button" data-go="${p.id}">${esc(p.t)}</button>`).join('')}${P.length > show.length ? `<span>…等 ${P.length} 段</span>` : ''}</p>`;
  }

  function renderPanel() {
    if (!sel) { panel.innerHTML = `<div class="a-hint"><img alt="" src="${A(D.emblem)}"><p>点一张卡，在这里看。</p><p class="s">人物点开是档案；强敌、神、生物在这里看样子和出没的年代。</p></div>`; return; }
    const x = (D[sel.t] || [])[sel.i]; if (!x) return;
    let h = '<button class="a-back" type="button">‹ 回到名录</button>';
    const here = per !== 'all' ? per : null;
    if (sel.t === 'people') {
      h += `<div class="a-hero">${sprite(x, 'a-big')}</div><h2>${esc(x.n)}</h2>`;
      h += `<p class="a-meta"><span class="a-tg">${esc(kindOf('people', x))}</span>${x.title ? `<span class="a-tg lg">${esc(x.title)}</span>` : ''}${x.tier ? `<span class="a-tg">${esc(x.tier)}</span>` : ''}${x.race ? `<span class="a-tg">${esc(x.race)}</span>` : ''}</p>`;
      if (x.who) h += `<p class="a-tx">${esc(x.who)}</p>`;
      h += '<h3>在这几段里</h3>' + perChips(x.at, 12);
      const pid = x.prof ? (here && x.prof.includes(here) ? here : x.prof[0]) : null;
      h += `<div class="a-btns">${pid ? `<button class="a-bt pri" type="button" data-prof="${pid}">看档案</button>` : ''}<button class="a-bt" type="button" data-go="${here || Object.keys(x.at)[0]}">去那一段</button></div>`;
    } else if (sel.t === 'foes' && x.fb) {
      h += fbHTML(x);
    } else if (sel.t === 'foes') {
      const k = Math.min(sel.ph || 0, Math.max(0, x.ph.length - 1)), ph = x.ph[k] || {};
      h += `<div class="a-hero foe">${ph.img ? `<img alt="" src="${esc(A(ph.img))}">` : '<span class="none"></span>'}</div><h2>${esc(x.n.replace(/·隐藏\s*/, '·'))}</h2>`;
      if (x.full && x.full !== x.n) h += `<p class="a-full">${esc(x.full)}</p>`;
      h += `<p class="a-meta"><span class="a-tg">${esc(kindOf('foes', x))}</span>${x.note ? `<span class="a-tg">${esc(x.note.replace(/^[A-Z]\d+[-·\dA-Z]*\s*[，、]?/, ''))}</span>` : ''}</p>`;
      if (x.ph.length > 1) h += '<div class="a-phs">' + x.ph.map((p, j) => `<button type="button" class="a-ph${j === k ? ' on' : ''}" data-ph="${j}"><img loading="lazy" alt="" src="${esc(A(p.img))}"><span>${j + 1} 阶</span></button>`).join('') + '</div>';
      if (ph.nm) h += `<h3>${x.ph.length > 1 ? (k + 1) + ' 阶　' : ''}${esc(ph.nm)}</h3>`;
      if (ph.look) h += `<p class="a-tx">${esc(ph.look)}</p>`;
      if (x.what) h += `<h3>${x.k === '主线对手' ? '是谁' : '本体'}</h3><p class="a-tx">${esc(x.what)}</p>`;
      if (x.where) h += `<p class="a-tx s">${esc(x.where)}</p>`;
      h += '<h3>出在哪一段</h3>' + (perChips(x.at, 8) || '<p class="a-tx s">不落在哪一段，别的局里碰上也是这一副。</p>');
      if ((x.at || []).length) h += `<div class="a-btns"><button class="a-bt pri" type="button" data-go="${here && x.at.includes(here) ? here : x.at[0]}">去那一段</button></div>`;
    } else if (sel.t === 'gods') {
      h += `<div class="a-hero god">${x.img ? `<img alt="" src="${esc(x.img)}">` : '<span class="none"></span>'}</div><h2>${esc(x.tag ? x.tag + x.n : x.n)}</h2>`;
      h += `<p class="a-meta"><span class="a-tg">${esc(kindOf('gods', x))}</span>${x.grp ? `<span class="a-tg">${esc(x.grp)}</span>` : ''}</p>`;
      if (x.rule) h += `<p class="a-tx">${esc(x.rule)}。</p>`;
      if (x.look) h += `<h3>样子</h3><p class="a-tx">${esc(x.look)}</p>`;
      if (x.since) h += `<p class="a-tx s">约 ${x.since} 年聚成，往前这个神位空着。</p>`;
      if (x.fell) h += `<p class="a-tx s spoil">${esc(x.fellText || ('倒在 ' + x.fell + ' 年'))}</p><p class="a-tx s nospoil">往后的事归剧透开关管。</p>`;
      if (x.dom) h += domHTML(x.dom);
      h += '<h3>在这几段里</h3>' + perChips(x.at, 10);
      const pid = x.prof ? (here && x.prof.includes(here) ? here : x.prof[0]) : null;
      if (pid) h += `<div class="a-btns"><button class="a-bt pri" type="button" data-prof="${pid}">看档案</button></div>`;
    } else {
      h += `<div class="a-hero a-sig">${sigil(x)}</div><h2>${esc(x.n)}</h2>`;
      h += `<p class="a-meta"><span class="a-tg">${esc(kindOf('beasts', x))}</span>${x.tier ? `<span class="a-tg lg">${esc(x.tier)}</span>` : ''}${x.rank ? `<span class="a-tg">${esc(x.rank.replace(/。$/, ''))}</span>` : ''}${x.elem ? `<span class="a-tg">${esc(x.elem.replace(/。$/, ''))}</span>` : ''}</p>`;
      if (x.what) h += `<p class="a-tx">${esc(x.what)}</p>`;
      if (x.where) h += `<h3>在哪里</h3><p class="a-tx">${esc(x.where)}</p>`;
      for (const s of x.sk || []) h += `<h3>${esc(s.nm)}</h3><p class="a-tx">${esc(s.t)}</p>`;
      if (x.way) h += `<h3>打得过的路</h3><p class="a-tx">${esc(x.way)}</p>`;
      if (x.drop) h += `<h3>身上的东西</h3><p class="a-tx">${esc(x.drop)}</p>`;
      if (x.src) h += `<h3>从哪里找</h3><p class="a-tx">${esc(x.src)}</p>`;
    }
    panel.innerHTML = h;
    panel.scrollTop = 0;
  }

  /* 楼层主（11-26，此刻那一本）：剧透关着只看基础的（名字、在哪一层、一两句是什么、一阶的名号和原画、明着的规矩、那一层的样子），
     剧透开了换成各阶段：阶段钮切换（有原画的出小图），每一阶的名号、LVL、情报、打法、那一段乐章（我方、它、有人声的带词），末了是那个世界、结局、身上留下的。 */
  function fbSig(x, cls) {
    const f = x.fb, big = f.lyr ? String(f.lyr) : f.where.replace(/迷宫城.*$|·.*$/, '').slice(0, 4);
    return `<span class="${cls} a-fbs${f.lyr ? '' : ' city'}"><i>${esc(big)}</i><small>${esc(f.lyr ? '第 ' + f.lyr + ' 层' : '迷宫城')}</small></span>`;
  }
  const paraHTML = (ps, cls) => (ps || []).map((p) => `<p class="a-tx${cls ? ' ' + cls : ''}">${esc(p)}</p>`).join('');
  function songHTML(sg) {
    if (!sg) return '';
    let h = `<div class="a-song"><h3>乐章《${esc(sg.nm)}》</h3><p class="a-meta"><span class="a-tg lg">${esc(sg.line)}</span>${sg.voice ? '<span class="a-tg">有人声</span>' : ''}</p>`;
    if (sg.lead) h += `<p class="a-tx s">${esc(sg.lead)}</p>`;
    if (sg.me) h += `<p class="a-tx"><b>我方</b>　${esc(sg.me)}</p>`;
    if (sg.it) h += `<p class="a-tx"><b>${esc(sg.who || '它')}</b>　${esc(sg.it)}</p>`;
    if ((sg.words || []).length) h += `<blockquote class="a-words">${sg.words.map(esc).join('<br>')}</blockquote>`;
    if (sg.aside) h += `<p class="a-tx s">${esc(sg.aside)}</p>`;
    return h + '</div>';
  }
  function fbHTML(x) {
    const f = x.fb, on = spoilOn(), n = f.st.length;
    const k = on ? Math.min(sel.ph || 0, n - 1) : 0, s = f.st[k];
    let h = `<div class="a-hero foe fb${s.img ? '' : ' noart'}">${s.img ? `<img alt="" src="${esc(A(s.img))}">` : fbSig(x, 'a-fbs-big')}</div><h2>${esc(foeName(x))}</h2>`;
    h += `<p class="a-full">${esc(on ? s.nm : x.full)}</p>`;
    h += `<p class="a-meta"><span class="a-tg">${esc(x.k)}</span><span class="a-tg">${esc(f.where)}</span>${f.band ? `<span class="a-tg">${esc(f.band.replace(/^阿卡迪亚大迷宫·/, ''))}</span>` : ''}${(on ? s.lv || f.lv : f.lv) ? `<span class="a-tg lg">${esc(on ? s.lv || f.lv : f.lv)}</span>` : ''}</p>`;
    if (x.what) h += `<p class="a-tx">${esc(x.what)}</p>`;
    if (f.rule) h += `<p class="a-tx s">${esc(f.rule)}</p>`;
    if (!on) {
      if (f.room) h += `<h3>那一层</h3><p class="a-tx s">${esc(f.room)}</p>`;
      h += `<p class="a-tx s nospoil">${n > 1 ? '往后几个阶段的名号和样子、' : ''}打法、情报和圣歌谱，归剧透开关管。</p>`;
      return h;
    }
    if (n > 1) h += '<div class="a-phs fb">' + f.st.map((p, j) => `<button type="button" class="a-ph${j === k ? ' on' : ''}" data-ph="${j}" aria-label="第 ${j + 1} 阶">${p.img ? `<img loading="lazy" alt="" src="${esc(A(p.img))}">` : `<span class="a-phn">${'一二三四五六七八九'[j]}</span>`}<span>${j + 1} 阶</span></button>`).join('') + '</div>';
    h += `<div class="a-stage" data-stage="${k}"><h3>${n > 1 ? (k + 1) + ' 阶　' : ''}${esc(s.nm)}</h3>`;
    h += paraHTML(s.t);
    if ((s.atk || []).length) h += '<h3>打法</h3>' + s.atk.map((a) => `<p class="a-tx">${a[0] ? `<b>${esc(a[0])}</b>　` : ''}${esc(a[1])}</p>`).join('');
    h += songHTML(s.song);
    if (k === n - 1 && f.fin) h += `<div class="a-song"><h3>终章《${esc(f.fin.nm)}》</h3><p class="a-tx s">${esc(f.fin.t)}</p>${(f.fin.words || []).length ? `<blockquote class="a-words">${f.fin.words.map(esc).join('<br>')}</blockquote>` : ''}</div>`;
    if (k === n - 1 && f.note) h += `<p class="a-tx s">${esc(f.note)}</p>`;
    h += '</div>';
    if (f.room) h += `<h3>那一层</h3><p class="a-tx s">${esc(f.room)}</p>`;
    if ((f.world || []).length) h += `<h3>${f.lyr ? (/残响异界|薪火/.test(f.band || '') ? '那个世界' : '那一带') : '城里'}</h3>` + paraHTML(f.world, 's');
    for (const l of f.lore || []) h += `<h3>${esc(l[0])}</h3>` + paraHTML(l[1], 's');
    if ((f.end || []).length) h += '<h3>打完以后</h3>' + f.end.map((e) => `<p class="a-tx"><b>${esc(e[0])}</b></p>` + paraHTML(String(e[1]).split('　'), 's')).join('');
    if (f.drop) h += `<h3>身上留下的</h3><p class="a-tx s">${esc(f.drop)}</p>`;
    return h;
  }

  // 神域栏（11-22）：神性、本域、三迹、权柄做得到什么、神域专长、神国是明着的；神力的数、带年份的句子、对上祂、陨落以后归剧透开关
  function domHTML(d) {
    let h = '<div class="a-dom"><h3 class="a-domh">神域</h3>';
    h += '<p class="a-meta">' + (d.sx ? `<span class="a-tg lg">${esc(d.sx)}</span>` : '') + (d.dm ? `<span class="a-tg">${esc(d.dm[0])}·${esc(d.dm[1])}</span>` : '') + '</p>';
    if (d.gh) h += `<p class="a-tx s spoil"><b>神力</b>　${esc(d.gh)}</p>`;
    if (d.dm && d.dm[2]) h += `<p class="a-tx"><b>${esc(d.dm[1])}</b>　${esc(d.dm[2])}</p>`;
    if (d.dm && d.dm[3]) h += `<p class="a-tx s"><b>祭司求得来的三迹</b>　${esc(d.dm[3])}</p>`;
    if (d.dmx) h += `<p class="a-tx s">${esc(d.dmx)}</p>`;
    for (const q of d.qb || []) {
      h += `<h3>权柄｜${esc(q[0])}</h3>`;
      if (q[1]) h += `<p class="a-tx">${esc(q[1])}</p>`;
      if (q[2]) h += `<p class="a-tx s spoil">${esc(q[2])}</p>`;
    }
    if (d.zc) h += `<h3>神域专长</h3><p class="a-tx">${esc(d.zc)}</p>`;
    if (d.gk) h += `<h3>${esc(d.gk[0])}</h3><p class="a-tx">${esc(d.gk[1])}</p>`;
    if (d.now) h += `<h3>今天</h3><p class="a-tx">${esc(d.now)}</p>`;
    if (d.vs) h += `<div class="spoil"><h3>对上祂</h3><p class="a-tx">${esc(d.vs)}</p></div>`;
    if (d.af) h += `<div class="spoil"><h3>往后</h3><p class="a-tx">${esc(d.af)}</p></div>`;
    if (d.gh || d.vs || d.af) h += '<p class="a-tx s nospoil">神力站在哪一级、怎么对上祂，归剧透开关管。</p>';
    return h + '</div>';
  }

  function openPanel(t, i) {
    sel = { t, i, ph: 0 };
    for (const b of list.querySelectorAll('.a-ac.sel')) b.classList.remove('sel');
    const b = list.querySelector(`[data-sel="${t}:${i}"]`); if (b) b.classList.add('sel');
    renderPanel(); root.classList.add('pan');
  }
  function closePanel() { root.classList.remove('pan'); }

  function onClick(ev) {
    const t = ev.target;
    if (t.closest('.at-hd .a-x')) { close(); return; }
    if (t.closest('.a-retry')) { list.innerHTML = '<p class="a-empty">再取一次，稍等一下。</p>'; load(); opened = false; waitOpen(want); return; }
    if (t.closest('.a-spl')) { C.setSpoil(!spoilOn()); syncSpoil(); return; }
    const st = t.closest('[data-per]');
    if (st) { per = st.dataset.per; sel = null; closePanel(); renderAll(); centerAxis(); return; }
    const tb = t.closest('[data-tab]');
    if (tb) { tab = tb.dataset.tab; chip = '全部'; sel = null; closePanel(); renderTabs(); renderList(); renderPanel(); return; }
    const ch = t.closest('[data-chip]');
    if (ch) { chip = ch.dataset.chip; renderTabs(); renderList(); return; }
    const card = t.closest('[data-sel]');
    if (card) {
      const [tt, i] = card.dataset.sel.split(':');
      openPanel(tt, +i); return;
    }
    if (t.closest('.at-panel .a-back')) { closePanel(); return; }
    const zm = t.closest('.a-zoom');
    if (zm) { zm.remove(); return; }
    const hz = t.closest('.a-hero.foe img');          // 强敌有原画的都点得开大图（11-26 起不只楼层主）
    if (hz) { const z = document.createElement('div'); z.className = 'a-zoom'; z.innerHTML = `<img alt="" src="${esc(hz.getAttribute('src'))}">`; root.appendChild(z); return; }
    const ph = t.closest('[data-ph]');
    if (ph && sel) { sel.ph = +ph.dataset.ph; renderPanel(); return; }
    const pf = t.closest('[data-prof]');
    if (pf && sel) { const x = D[sel.t][sel.i]; C.openPerson(pf.dataset.prof, x.n); return; }
    const go = t.closest('[data-go]');
    if (go) { const id = go.dataset.go; close(); C.goEra(id); return; }
  }

  const api = { init, open, close, syncSpoil, isOpen: () => opened, missing: false, get ready() { return ready; } };
  window.Atlas = api;
})();
