/* 时代页按主线细分（11-20，位阶延寿与门面按主线细分_方向稿.md 第二节）。四本书共用。
   一个年代页的主线排成一条时间轴，点哪一格，整页停在那一年：
     旅伴　这一条主线的主角
     相遇　这一年还活着、跟这一页碰得上的人（上一段的旅伴长大了、老了落到这里），名牌上带这一年的岁数
     传奇　这一年在世的传奇（这一年以前凝名、到传奇的从相遇挪上来）
     故去　这一年以前死了的、这一页出过场的人，剧透开着才显示
   生卒、凝名、位阶节点照 data/life.json（底稿/命星重审第二轮 生卒那一批抽的，共用/build_life.py 出）。
   年份一律用总的纪年：月银纪 Y 是 Y，纷争纪 N 是 10080+N，山铜纪 N 是 21113+N，迷宫纪 N 是 22059+N。
   寿限照写作口径「位阶与寿限」：天生 × 位阶乘数 ＋ 突破攒的年数；长成以后看上去的岁数照寿限的比例走，名字凝住就停住。 */
(function () {
  const BASE = { moon: 0, strife: 10080, bronze: 21113, maze: 22059 };
  const MUL = { 启源: 1, 共鸣: 1.1, 灵格: 1.3, 极境: 1.6, 英雄: 2.5 };
  const QUAL = { 寻常: 0, 稳: 10, 漂亮: 35, 极品: 80 };
  const BANDS = [[18, '少年'], [30, '青年'], [50, '壮年'], [65, '中年'], [1e9, '老年']];
  let DATA = null, vol = '', pending = null, PATCH = {};
  const applyPatch = () => { if (DATA) for (const k in PATCH) DATA.people[k] = Object.assign({}, DATA.people[k] || {}, PATCH[k]); };
  const sel = {};                  // 时代 id → 选中的第几条主线（-1 整段）
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const yOf = (l) => { const m = String(l.year || '').match(/-?\d+/); return m ? +m[0] : null; };
  const short = (n) => String(n || '').split('·')[0];
  const segOf = (l) => String(l.name || '').split('·').slice(1).join('·') || String(l.name || '');

  function rec(name) {
    if (!DATA || !name) return null;
    const P = DATA.people;
    return P[name] || P[(DATA.alias || {})[name]] || P[(DATA.alias || {})[short(name)]] || null;
  }
  function rankAt(p, y) {
    let r = null;
    for (const [yy, k] of p.k || []) if (yy <= y) r = k;
    return r || ((p.k || [])[0] || [])[1] || '启源';
  }
  function limitAt(p, y) {          // 这一年的寿限
    const r = rankAt(p, y);
    if (r === '传奇') return Infinity;
    let add = 0;
    for (const [yy, k] of p.k || []) if (yy <= y && p.q && p.q[k]) add += QUAL[p.q[k]] || 0;
    return (p.s || 90) * (MUL[r] || 1) + add;
  }
  function adultAge(p) { return Math.min(100, Math.round(18 * Math.sqrt(Math.max(1, (p.s || 90) / 90)))); }
  /* 看上去的岁数（折成人类的岁数，好挑立绘那一档）：长成以前照种族长，长成以后一年年照这一年的寿限折，凝名或到传奇那一年停住 */
  function looks(p, y) {
    if (p.b == null) return null;
    const stop = Math.min(y, p.n != null ? p.n : Infinity, p.l != null ? p.l : Infinity);
    const real = stop - p.b, ad = adultAge(p);
    if (real <= ad) return Math.max(0, Math.round(18 * real / ad));
    let h = 18;
    for (let t = p.b + ad; t < stop; t++) { const lim = limitAt(p, t); if (lim === Infinity) break; h += 72 / Math.max(lim - ad, 1); }
    return Math.round(h);
  }
  const bandOf = (h) => (h == null ? '' : BANDS.find((b) => h < b[0])[1]);
  function state(p, y) {
    if (!p) return '';
    if (p.b != null && p.b > y) return 'unborn';
    if (p.d != null && p.d < y) return 'dead';
    if (p.l != null && p.l <= y) return 'legend';
    return 'alive';
  }

  const Life = {
    BASE, rec, rankAt, limitAt, looks, bandOf, state,
    load(v, url) {
      vol = v;
      return pending || (pending = fetch(url).then((r) => (r.ok ? r.json() : null)).catch(() => null).then((d) => { DATA = d; applyPatch(); return d; }));
    },
    ready: () => !!DATA,
    patch(o) { Object.assign(PATCH, o || {}); applyPatch(); },      // 暗线那一套另给的生卒（data/dark.json 的 life）
    /* 时间轴那一排：整段一格，再一条主线一格 */
    bar(e) {
      if (!DATA || !e.lines || e.lines.length < 2) return '';
      const k = sel[e.id] == null ? -1 : sel[e.id];
      const cell = (i, y, t) => `<button class="tl-k${i === k ? ' on' : ''}" data-tl="${i}"><small>${esc(y)}</small>${esc(t)}</button>`;
      return `<nav class="tl" aria-label="按主线看这一页的人">` + cell(-1, '整段', '全部的人') +
        e.lines.map((l, i) => cell(i, yOf(l) != null ? yOf(l) + ' 年' : '', segOf(l))).join('') + '</nav>';
    },
    /* 选了某一条：回 {cast, meet, legends, gone, y}；整段或没有数据回 null，照原样画 */
    view(e, spoil) {
      const k = sel[e.id] == null && e.lines && e.lines.length === 1 ? 0 : sel[e.id];      // 只有一条主线的页：整页就是那一条，照它那一年分
      if (!DATA || k == null || k < 0 || !e.lines[k]) return null;
      const l = e.lines[k], y0 = yOf(l);
      if (y0 == null) return null;
      const Y = y0 + BASE[vol], seg = segOf(l);
      const inSeg = (c) => (Array.isArray(c.seg) ? c.seg : [c.seg]).some((s) => s && (s === seg || seg.indexOf(s) >= 0));
      const tag = (c, p) => { const o = Object.assign({}, c); if (p && p.b != null && p.r !== '人偶') { o._age = Y - p.b; o._band = bandOf(looks(p, Y)); } return o; };
      const out = { cast: [], meet: [], legends: [], gone: [], y: Y };
      const seen = new Set();
      const put = (c, from) => {
        const nm = short(c.name);
        if (seen.has(nm)) return;
        seen.add(nm);
        const p = rec(c.name), st = state(p, Y);
        if (st === 'unborn') return;
        if (st === 'dead') { if (spoil) out.gone.push(Object.assign(tag(c, null), { _d: p.d, _h: p.h, _dage: p.b != null ? p.d - p.b : null })); return; }
        if (from === 'cast' && inSeg(c)) { out.cast.push(tag(c, p)); return; }
        if (from === 'legends' || st === 'legend') { out.legends.push(tag(c, p)); return; }
        out.meet.push(Object.assign(tag(c, p), { who: c.who || '', tag: c.tag || '' }));
      };
      e.cast.filter(inSeg).forEach((c) => put(c, 'cast'));
      e.cast.forEach((c) => put(c, 'cast-other'));
      (e.meet || []).forEach((c) => put(c, 'meet'));
      (e.legends || []).forEach((c) => put(c, 'legends'));
      return out;
    },
    ageText: (c) => (c._age != null ? ` · ${c._age} 岁` : ''),
    goneHTML(list, yearText) {
      if (!list.length) return '';
      return `<h2 class="spoil">故去</h2><p class="def spoil">这一年以前已经不在了的人。没有你的那一版。</p><ul class="meet gone spoil">` + list.map((c) =>
        `<li class="np"><b>${esc(c.name)}</b><span>${esc(yearText(c._d))}${c._h && c._h !== '不详' ? '　' + esc(c._h) : ''}${c._dage != null ? '　' + c._dage + ' 岁' : ''}</span></li>`).join('') + '</ul>';
    },
    bind(root, redraw, eraOf) {
      root.addEventListener('click', (ev) => {
        const b = ev.target.closest('[data-tl]');
        if (!b) return;
        const e = eraOf();
        if (!e) return;
        sel[e.id] = +b.dataset.tl;
        redraw();
      });
    },
  };
  window.Life = Life;
})();
