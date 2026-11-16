/* 外壳（11-15 拼装那一轮）：牌桌那一页选定纪元以后的事都在这里。
   一、装书：这一纪的书是各自一个页面，拿过来装进一格 iframe（srcdoc）。头上塞 <base> 和一小段：告诉它图和数据在哪几个地址（window.A）、怎么跟外壳说话（window.SHELL）。
   二、书里“从这里进”→ 建档（照那一纪的册子画的一张登记表，字和可选的种族在 data/build.json）→ 请离那一眼 → 确认页（凭证填进聊天输入框，超过 8192 字就只给复制）。
   三、牌桌右上角的世界之书（common/codex.js，翻到通用卷）。
   地址：装进卡里的时候，薄壳先给 window.FRONT_CFG（四本书各在图床的哪个地址、哪几个目录另放一段）；本地看的时候照下面 DEF（书在旁边的目录里）。 */
(function () {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const BOOKS = ['moon', 'strife', 'bronze', 'maze'], ERA = { moon: '月银纪', strife: '纷争纪', bronze: '山铜纪', maze: '迷宫纪' };
  const DEF = { books: { moon: { core: '../小样_月银纪书/' }, strife: { core: '../小样_纷争纪书/' }, bronze: { core: '../小样_山铜纪书/' }, maze: { core: '../小样_迷宫纪书/' } }, old1001: '' };
  const CFG = Object.assign({}, DEF, window.FRONT_CFG || {});
  const HERE = new URL('.', document.baseURI).href;          // 外壳自己在哪（common/、data/、assets/ 都在它底下）
  const LIMIT = 8192;                                        // 日里那条填输入框的指令一回最多收这么多字（11-12 探针量的）
  const inRili = window.parent && window.parent !== window;
  let BUILD = null, cur = null, frame = null, pend = null, spoil = false, picked = -1;

  /* ---------- 页面上加的几层 ---------- */
  const mk = (tag, id, html) => { const el = document.createElement(tag); if (id) el.id = id; if (html) el.innerHTML = html; document.body.appendChild(el); return el; };
  const wbBtn = mk('button', 'wbBtn', `<img src="${A('common/assets/ui/wb_cover.webp')}" alt=""><span>世界之书</span>`);
  wbBtn.type = 'button'; wbBtn.setAttribute('aria-label', '打开世界之书');
  const codexHost = mk('div', 'sh-codex');
  const bookEl = mk('div', 'sh-book', '<div class="sh-veil"><i></i><span>这一纪的书正在翻开</span></div>'); bookEl.hidden = true;
  const buildEl = mk('div', 'sh-build'); buildEl.hidden = true;
  const leaveEl = mk('div', 'sh-leave', '<img alt=""><p></p>'); leaveEl.hidden = true;
  const sealEl = mk('div', 'sh-seal'); sealEl.hidden = true;
  const veil = bookEl.querySelector('.sh-veil');
  const busy = (on) => document.body.classList.toggle('sh-busy', on);
  const show = (el) => { el.hidden = false; requestAnimationFrame(() => requestAnimationFrame(() => el.classList.add('on'))); };
  const hide = (el, ms = 600) => { el.classList.remove('on'); setTimeout(() => { if (!el.classList.contains('on')) el.hidden = true; }, ms); };
  /* 书开着的时候牌桌整个收起来（display:none，连它那几层的显存一起放掉；光用 visibility 藏不住，里头亮着的几场自己写了 visible） */
  const tableOn = (on) => {
    window.__tbPause = !on;
    const v = document.getElementById('view'), u = document.getElementById('ui');
    if (v) v.style.display = on ? '' : 'none';
    if (u) u.style.visibility = on ? '' : 'hidden';
    if (on) { try { window.dispatchEvent(new Event('resize')); } catch (e) {} }
  };
  setTimeout(() => wbBtn.classList.add('on'), 1500);

  /* ---------- 世界之书（牌桌上这一份翻到通用卷；点了哪个时代就去那一纪的书） ---------- */
  if (window.Codex) {
    Codex.init({ vol: 'general', host: codexHost, A: window.A, spoil: () => spoil, setSpoil: (v) => { spoil = v; }, onOpen: () => { window.__tbPause = true; }, onClose: () => { if (!cur && buildEl.hidden) window.__tbPause = false; }, onEra: (vol, id) => openBook(vol, id) });
    wbBtn.addEventListener('click', () => Codex.open('general', ''));
  } else wbBtn.hidden = true;

  /* ---------- 装书 ---------- */
  const abs = (u) => new URL(u, HERE).href;
  function preamble(M, at) {
    return '(function(){var M=' + JSON.stringify(M) + ';'
      + 'window.A=function(p){for(var k in M)if(p.indexOf(k)===0)return M[k]+p;return p};'
      + 'window.SHELL={at:' + JSON.stringify(at || '') + ',post:function(m){m.aldran=1;parent.postMessage(m,"*")}};'
      + 'var f0=window.fetch.bind(window);'
      + 'window.fetch=function(u,o){if(typeof u!=="string")return f0(u,o);var j=/\\.json(\\?|$)/.test(u);'
      + 'return f0(window.A(u),o).then(function(r){if(!j||!r.ok)return r;return r.text().then(function(t){for(var k in M)if(k!=="common/")t=t.split(\'"\'+k).join(\'"\'+M[k]+k);'
      + 'return new Response(t,{status:200,headers:{"content-type":"application/json"}})})})};'
      + 'window.addEventListener("error",function(e){try{parent.postMessage({aldran:1,t:"err",msg:String(e.message||e.type).slice(0,200)},"*")}catch(x){}});'
      + 'var r0=window.requestAnimationFrame.bind(window),pq=[],pz=false;'
      + 'window.requestAnimationFrame=function(f){if(pz){pq.push(f);return 0}return r0(f)};'
      + 'window.addEventListener("message",function(e){var m=e.data;if(!m||m.aldran!==1||m.t!=="pause")return;pz=!!m.on;window.__paused=pz;if(!pz){var q=pq;pq=[];for(var i=0;i<q.length;i++)r0(q[i])}});'
      + '})();';
  }
  async function openBook(id, at) {
    const B = CFG.books[id];
    if (!B) return;
    if (window.Codex && Codex.isOpen()) Codex.close();
    closeFrame();
    cur = id; busy(true); veil.classList.remove('off'); veil.querySelector('span').textContent = ERA[id] + '的书正在翻开';
    show(bookEl); setTimeout(() => { if (cur) tableOn(false); }, 650);
    const core = abs(B.core), M = { 'common/': HERE };
    for (const k in (B.parts || {})) M[k] = abs(B.parts[k]);
    let html;
    try { html = await fetch(core + 'index.html').then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); }); }
    catch (e) { veil.querySelector('span').textContent = '这一本没有载下来'; const b = document.createElement('button'); b.textContent = '回到牌桌'; b.onclick = () => { b.remove(); toTable(); }; veil.appendChild(b); return; }
    if (cur !== id) return;
    for (const k in M) if (k !== 'common/') html = html.split(k).join(M[k] + k);        // 另放一段的那几个目录（assets/ps/ 这些）换成图床的地址
    html = html.replace(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com([^"]*)"(?![^>]*media=)/g, '<link rel="stylesheet" href="https://fonts.googleapis.com$1" media="print" onload="this.media=\'all\'"');   // 字体不挡着页面
    frame = document.createElement('iframe'); frame.id = 'sh-frame'; frame.setAttribute('title', ERA[id] + '的书'); frame.setAttribute('allow', 'autoplay; fullscreen');
    frame.srcdoc = '<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><base href="' + core + '"><script>' + preamble(M, at) + '<\/script></head><body>' + html + '</body></html>';
    frame.addEventListener('load', () => setTimeout(() => veil.classList.add('off'), 900));
    bookEl.insertBefore(frame, veil);
  }
  function closeFrame() { if (frame) { frame.remove(); frame = null; } cur = null; bookEl.style.visibility = ''; }
  /* 书藏起来（不拆，回去的时候还在原处）：藏着的时候叫它别画帧，手机上不跟牌桌抢 */
  function bookHide(on) {
    bookEl.style.visibility = on ? 'hidden' : '';
    if (frame && frame.contentWindow) { try { frame.contentWindow.postMessage({ aldran: 1, t: 'pause', on: !!on }, '*'); } catch (e) {} }
  }
  function toTable() {
    closeFrame(); closeOld(); hide(bookEl); hide(buildEl); busy(false); tableOn(true);
    if (window.__tb && __tb.again) __tb.again();
  }
  window.addEventListener('message', (ev) => {
    const m = ev.data || {};
    if (!m.aldran) return;
    if (frame && ev.source === frame.contentWindow) {
      if (m.t === 'table') toTable();
      else if (m.t === 'goto' && CFG.books[m.book]) openBook(m.book, m.at);
      else if (m.t === 'enter') { if (m.at === '1001') openOld(); else startBuild(m); }
      else if (m.t === 'err') console.warn('书里报错', cur, m.msg);
    } else if (oldFrame && ev.source === oldFrame.contentWindow) {
      if (m.t === 'table') toTable();
      else if (m.t === 'cred' && m.text) { pend = null; leave(String(m.text)); }
      else if (m.t === 'old-ready') oldEl.classList.add('ready');
    }
  });

  /* ---------- 迷宫纪 1001 年：原来那一整页介绍页（建档器、接续旧档、1001 年的世界之书和大陆全图）原样装进来 ----------
     它是卡里原来的介绍页，make_old1001.py 从打好的卡里取出来、末尾添一小段：直接翻到目录那一幕，铸印的时候把凭证交给外壳。 */
  const oldEl = mk('div', 'sh-old', '<div class="sh-veil"><i></i><span>迷宫纪 1001 年</span></div>'); oldEl.hidden = true;
  let oldFrame = null;
  async function openOld() {
    if (window.Codex && Codex.isOpen()) Codex.close();
    busy(true); show(oldEl); setTimeout(() => { if (!oldEl.hidden) { tableOn(false); bookHide(true); } }, 650);
    if (oldFrame) return;
    const v = oldEl.querySelector('.sh-veil'); v.classList.remove('off'); oldEl.classList.remove('ready');
    let html;
    try { html = await fetch(CFG.old1001 ? abs(CFG.old1001) : A('old1001.html')).then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); }); }
    catch (e) { v.querySelector('span').textContent = '这一页没有载下来'; const b = document.createElement('button'); b.textContent = '回去'; b.onclick = () => { b.remove(); backFromOld(); }; v.appendChild(b); return; }
    oldFrame = document.createElement('iframe'); oldFrame.id = 'sh-oldframe'; oldFrame.setAttribute('title', '迷宫纪 1001 年'); oldFrame.setAttribute('allow', 'autoplay; fullscreen; clipboard-write');
    oldFrame.srcdoc = html;
    oldFrame.addEventListener('load', () => setTimeout(() => v.classList.add('off'), 500));
    oldEl.insertBefore(oldFrame, v);
  }
  function closeOld() { if (oldFrame) { oldFrame.remove(); oldFrame = null; } hide(oldEl); }
  function backFromOld() { closeOld(); if (frame) { bookHide(false); } else { busy(false); tableOn(true); } }
  /* 画面卡的时候手动换轻量画法（牌桌自己那套“上回开崩了下回换轻的”靠 localStorage，日里的介绍页里没有） */
  if (!document.querySelector('#world.lite') && !/tb:lite/.test(window.name || '')) {
    const liteBtn = mk('button', 'liteBtn', '画面卡？换轻量画法');
    liteBtn.type = 'button';
    liteBtn.addEventListener('click', () => { try { window.name = 'tb:lite'; } catch (e) {} location.reload(); });
    setTimeout(() => liteBtn.classList.add('on'), 4000);
  }
  const oldBtn = mk('button', 'oldBtn', '<b>迷宫纪 1001 年</b><span>建档 · 接续旧档</span>');
  oldBtn.type = 'button'; oldBtn.setAttribute('aria-label', '直接去迷宫纪 1001 年：建档，或者接续旧档');
  oldBtn.addEventListener('click', openOld);
  setTimeout(() => oldBtn.classList.add('on'), 1500);

  /* ---------- 牌桌选定了一纪 ---------- */
  const openBtn = $('#openBook');
  if (openBtn) openBtn.addEventListener('click', () => { if (picked >= 0) openBook(BOOKS[picked]); });
  const Shell = { onEra(k) { picked = k; }, openBook, toTable, openOld, get state() { return { cur, picked, build: !buildEl.hidden, seal: !sealEl.hidden, frame: !!frame, old: !!oldFrame, pend }; } };

  /* ---------- 建档 ----------
     资料在 data/build.json（各纪的册子、各年代能选的种族和本事、她的几句话、凭证的写法），出处在 建档_资料说明.md。
     一纪一种登记法：月银纪火边报火、城门边报家，纷争纪的军册，山铜纪段城的兵册，迷宫纪公会的挂号册。降临者报不出的那一栏空着。 */
  const loadBuild = () => BUILD ? Promise.resolve(BUILD) : fetch(A('data/build.json')).then((r) => r.json()).then((d) => (BUILD = d));
  const yearOf = (s) => { const t = String(s || '').replace(/\s/g, ''); const m = t.match(/(\d{1,5})/); return m ? +m[1] : (/元年|^元$/.test(t) ? 1 : null); };
  const F = {};          // 填到一半的东西，回去改的时候还在
  async function startBuild(m) {
    pend = m;
    let D;
    try { D = await loadBuild(); } catch (e) { D = { format: {}, eras: {} }; }
    const E = (D.eras || {})[m.book] || { name: ERA[m.book], sheet: {}, periods: [], races: {} };
    const era = E.name || ERA[m.book], FR = E.free || null;
    if (F._book !== m.book) { F._book = m.book; for (const k of ['race', 'sub', 'kin', 'race2', 'origin', 'skills', 'skill2', 'year', 'place', 'from']) delete F[k]; }
    const yearText = (y) => { const t = String(y || '').replace(/\s/g, ''); if (m.book === 'strife' && /^1年?$/.test(t)) return '元年'; return t ? t + (/年$/.test(t) ? '' : '年') : ''; };          // 书里给的年份有“元年”“约1020”“9900—10078”这几种写法
    const key = m.book + '|' + m.at + '|' + (m.line || '');
    if (F._key !== key) { F._key = key; F.free = null; }
    let free = F.free != null ? F.free : (m.at === 'free' || !m.line);          // 自己报年份（第二十二张、无字碑、空白委托）
    if (free && !FR) free = false;
    const periodAt = (y) => { const Ps = E.periods || []; return (y != null && Ps.find((p) => p.from <= y && y <= p.to && p.id !== '1001')) || null; };
    const periodOfEra = () => (E.periods || []).find((p) => (p.eras || []).includes(m.at)) || periodAt(yearOf(m.year)) || (E.periods || [])[0] || { races: [], skills: [] };
    let P = free ? (periodAt(yearOf(F.year)) || (E.periods || [])[0] || { races: [], skills: [] }) : periodOfEra();
    const say = ((D.ronova && D.ronova.enter) || ['写下你的名字。']).slice();
    const placed = ((D.ronova && D.ronova.lines) || []).find((x) => /带过来/.test(x.use || ''));
    if (!free && placed) say.push(placed.line);
    const raceOf = (id) => Object.assign({ id }, (E.races || {})[id] || { name: id });
    const sheetOf = (p) => (E.sheets && p.sheet && E.sheets[p.sheet]) || E.sheet || {};

    buildEl.innerHTML = `<div class="bd-wrap"><div class="bd-say"><small>死 之 神 殿</small>${say.map((t) => `<p>${esc(t)}</p>`).join('')}</div>
<form class="bd-sheet ${m.book}" autocomplete="off" novalidate>
  <div class="bd-hd"><img src="${A('common/assets/ui/emblem_' + m.book + '.webp')}" alt=""><div><h2 id="bd-title"></h2><p id="bd-who"></p></div></div>
  <p class="bd-cols" id="bd-cols"></p>
  <div class="bd-at" id="bd-at"></div>
  ${FR ? `<div class="bd-f" id="bd-freebox"${free ? '' : ' hidden'}>
    <div class="bd-row two"><div class="bd-f"><label for="bd-year">哪一年<small>${esc(era)} ${FR.from} 到 ${FR.to} 年</small></label><input id="bd-year" type="text" inputmode="numeric" maxlength="6" placeholder="比如 ${Math.round((FR.from + FR.to) / 3)}"></div>
    <div class="bd-f"><label for="bd-place">哪里<small>可不填</small></label><input id="bd-place" type="text" maxlength="40" placeholder="想从哪一处睁眼，一句"></div></div>
    ${FR.note ? `<p class="bd-note">${esc(FR.note)}</p>` : ''}</div>
  ${m.line ? `<p class="bd-switch"><button type="button" id="bd-tofree">${free ? '照书里那一条主线开局' : '不走这条主线，自己报年份（' + esc(FR.label) + '）'}</button></p>` : ''}` : ''}
  <div class="bd-f"><span class="lb">你是<small>多半是落进来的生客</small></span>
    <div class="bd-chips" id="bd-origin"><button type="button" data-o="fall" aria-pressed="true">落进来的人</button><button type="button" data-o="gold" aria-pressed="false">生在这一纪的黄金裔</button></div>
    <p class="bd-note" id="bd-origin-note"></p></div>
  <div class="bd-row">
    <div class="bd-f"><label for="bd-name">名字</label><input id="bd-name" type="text" maxlength="24" placeholder="她先问这个"></div>
    <div class="bd-f"><label for="bd-sex">性别</label><input id="bd-sex" type="text" maxlength="8" placeholder="男、女，或者照你说的"></div>
    <div class="bd-f"><label for="bd-age">年岁</label><input id="bd-age" type="text" maxlength="12" placeholder="落地多大就多大"></div>
  </div>
  ${E.rank ? `<p class="bd-note">${esc(E.rank)}</p>` : ''}
  <div class="bd-f"><span class="lb">种族<small id="bd-race-when"></small></span>
    <div class="bd-races" id="bd-races"></div>
    <div class="bd-detail" id="bd-race-detail" hidden></div>
    <input id="bd-race2" type="text" maxlength="40" placeholder="想再说细一点的写这里（混血、哪一家、哪一支）">
  </div>
  <div class="bd-f"><label for="bd-look">样子</label><textarea id="bd-look" rows="2" maxlength="300" placeholder="头发、眼睛、个子，身上一样认得出的东西"></textarea></div>
  <div class="bd-f"><label for="bd-from" id="bd-from-lab"></label><textarea id="bd-from" rows="2" maxlength="300"></textarea>
    <p class="bd-blank" id="bd-blank" hidden></p><details class="bd-more" id="bd-more" hidden><summary>册子上别的几栏</summary><div></div></details></div>
  <div class="bd-f"><span class="lb">本事<small>挑一两样想往哪边长，也可以自己写</small></span>
    <div class="bd-chips" id="bd-skills"></div>
    <input id="bd-skill2" type="text" maxlength="60" placeholder="最想要的一样本事，一句话"></div>
  ${(D.oaths || []).length ? `<div class="bd-f"><span class="lb">誓心<small>可不选，她照你做的事替你记</small></span><div class="bd-chips" id="bd-oath">${D.oaths.map((o) => `<button type="button" data-oath="${esc(o)}" aria-pressed="false">${esc(o)}</button>`).join('')}</div></div>` : ''}
  <div class="bd-f"><label for="bd-wish">初心<small>可不填。为什么上路，想找什么</small></label><input id="bd-wish" type="text" maxlength="80" placeholder="一句就够"></div>
  <div class="bd-f"><label for="bd-art">立绘<small>可不填。贴一张全身图的地址，往后在聊天里也能换</small></label><input id="bd-art" type="text" maxlength="300" placeholder="https://"><input id="bd-face" type="text" maxlength="300" placeholder="头像的地址，可不填"></div>
  <div class="bd-f"><label for="bd-extra">还想让她知道的</label><textarea id="bd-extra" rows="2" maxlength="600" placeholder="别的设定，想要的开局，不想碰的东西"></textarea></div>
  ${(E.lacks || []).length ? `<details class="bd-more"><summary>这一纪没有的</summary><div>${E.lacks.map((t) => `<p>${esc(t)}</p>`).join('')}</div></details>` : ''}
  <p class="bd-err" role="alert"></p>
  <div class="bd-acts"><button type="button" class="back">${frame ? '回到书里' : '回到牌桌'}</button><button type="submit" class="go">交给她</button></div>
</form></div>`;
    const form = buildEl.querySelector('form'), q = (s) => form.querySelector(s);
    let race = '', sub = '', kin = '', origin = F.origin === 'gold' ? 'gold' : 'fall';
    const press = (box, attr, val) => { for (const b of box.querySelectorAll('[' + attr + ']')) b.setAttribute('aria-pressed', String(b.getAttribute(attr) === val)); };

    /* 种族那一格底下的说明：这个年代的这一族是什么样、降临者是这一族会怎样，再往下是支和家 */
    const raceDetail = () => {
      const box = q('#bd-race-detail'), R = race ? raceOf(race) : null;
      if (!R) { box.hidden = true; box.innerHTML = ''; return; }
      const subsNow = (R.subs || []).filter((x) => !x.from || x.from <= (P.to || 99999));          // 这个年代还没有的支和叫法不列
      const S = subsNow.find((x) => x.name === sub) || null;
      const pn = (P.race_notes || {})[race] || '';
      let h = '';
      if (pn) h += `<p>${esc(pn)}</p>`;
      if (R.arrive && origin === 'fall') h += `<p>${esc(R.arrive)}</p>`;
      if (subsNow.length) h += `<div class="bd-chips">${subsNow.map((x) => `<button type="button" data-sub="${esc(x.name)}" aria-pressed="${x.name === sub}">${esc(x.name)}</button>`).join('')}</div>`;
      if (S) {
        h += `<p class="s"><b>${esc(S.name)}</b>　${esc(S.note || '')}${S.art ? '　传承的手艺是' + esc(S.art) + '。' : ''}${S.when ? '（' + esc(S.when) + '）' : ''}</p>`;
        if (S.arrive && origin === 'fall') h += `<p>${esc(S.arrive)}</p>`;
        if ((S.kin || []).length) h += `<div class="bd-chips">${S.kin.map((x) => `<button type="button" data-kin="${esc(x.name)}" aria-pressed="${x.name === kin}" title="${esc((x.note || '') + (x.when ? '（' + x.when + '）' : ''))}">${esc(x.name)}</button>`).join('')}</div>`;
        const K = (S.kin || []).find((x) => x.name === kin);
        if (K) h += `<p class="s"><b>${esc(K.name)}</b>　${esc(K.note || '')}${K.when ? '（' + esc(K.when) + '）' : ''}</p>`;
      }
      box.innerHTML = h; box.hidden = !h;
    };
    const pickRace = (id) => { race = id; sub = ''; kin = ''; press(q('#bd-races'), 'data-r', id); raceDetail(); };

    /* 跟着年代走的那几块：册子、能选的种族、本事（自己报年份的时候，年份一改就重排） */
    const renderPeriod = () => {
      const S = sheetOf(P), gold = origin === 'gold';
      q('#bd-title').textContent = S.title || '登记'; q('#bd-who').textContent = (S.who ? S.who + '问的' : '') + (S.ask ? '　' + S.ask : '');
      q('#bd-cols').textContent = (S.cols || []).length ? '册子上的栏：' + S.cols.join('　｜　') : ''; q('#bd-cols').hidden = !(S.cols || []).length;
      const yr = free ? yearOf(q('#bd-year') ? q('#bd-year').value : '') : null;
      q('#bd-at').innerHTML = free
        ? `<b>${esc(era)}${yr != null ? ' ' + yr + ' 年' : ''}</b>　${esc(FR.label)}${P.name && yr != null ? '　' + esc(P.name) : ''}${P.note && yr != null ? `<span>${esc(P.note)}</span>` : ''}`
        : `<b>${esc(era)}${m.year ? ' ' + esc(yearText(m.year)) : ''}</b>　${esc(m.title || '')}　${esc(m.line || '')}${P.note ? `<span>${esc(P.note)}</span>` : ''}`;
      q('#bd-race-when').textContent = P.name ? P.name + '里的各族' : '';
      const absent = P.absent || [];
      q('#bd-races').innerHTML = (P.races || []).map(raceOf).filter((r) => r.name).map((r) => {
        const ab = absent.includes(r.id), off = ab && gold;          // 这时候世上还没有的族：落进来的人照样能是（他是头一个），黄金裔的凡人那一头不能是
        return `<button type="button" data-r="${esc(r.id)}" aria-pressed="false"${off ? ' disabled' : ''}${ab ? ' class="ab"' : ''}><b>${esc(r.name)}</b>${ab ? '<i>这时候世上还没有</i>' : ''}${r.note ? `<span>${esc(r.note)}</span>` : ''}</button>`;
      }).join('');
      if (race && (!(P.races || []).includes(race) || (gold && absent.includes(race)))) { race = ''; sub = ''; kin = ''; }
      press(q('#bd-races'), 'data-r', race); raceDetail();
      const keep = new Set([...q('#bd-skills').querySelectorAll('[aria-pressed="true"]')].map((b) => b.dataset.s).concat(F.skills || []));
      q('#bd-skills').innerHTML = (P.skills || []).map((s) => `<button type="button" data-s="${esc(s)}" aria-pressed="${keep.has(s)}">${esc(s)}</button>`).join('');
      // 报不出的那一栏
      const lab = (S.blank && S.blank.label) || '从哪里来';
      q('#bd-from-lab').innerHTML = gold ? '在哪里长大<small>凡人那一头的父亲或母亲是谁，你在哪里长大，一两句</small>' : esc(lab) + '<small>你落下来以前的那个世界，一两句，报不出也行</small>';
      q('#bd-from').placeholder = gold ? '比如 墙下村织麻人家的孩子，没见过父亲' : '这一栏这里的人填不了';
      const bl = q('#bd-blank'); bl.textContent = (!gold && S.blank && S.blank.line) || ''; bl.hidden = !bl.textContent;
      const more = q('#bd-more'), ms = (S.more || []);
      more.hidden = !ms.length; more.querySelector('div').innerHTML = ms.map((x) => `<p><b>${esc(x.label)}</b>　${esc(x.line)}</p>`).join('');
      q('#bd-origin-note').textContent = gold
        ? '你生在这一纪，父母里有一位是神，跟着凡人那一头长大，血是金色的。神亲是哪一位，你自己也不知道。' + (absent.length ? '这时候世上还没有的族，黄金裔选不了。' : '')
        : '你是从别处落进来的人，在这里没有生日，也没有故乡，旁人只当是异乡来的客人。';
    };
    renderPeriod();

    form.addEventListener('click', (e) => {
      const t = e.target;
      const rb = t.closest('[data-r]'); if (rb) { if (!rb.disabled) pickRace(rb.dataset.r === race ? '' : rb.dataset.r); return; }
      const sb = t.closest('[data-sub]'); if (sb) { sub = sb.dataset.sub === sub ? '' : sb.dataset.sub; kin = ''; raceDetail(); return; }
      const kb2 = t.closest('[data-kin]'); if (kb2) { kin = kb2.dataset.kin === kin ? '' : kb2.dataset.kin; raceDetail(); return; }
      const kb = t.closest('[data-s]'); if (kb) { const on = kb.getAttribute('aria-pressed') !== 'true'; if (on && form.querySelectorAll('#bd-skills [aria-pressed="true"]').length >= 2) return; kb.setAttribute('aria-pressed', String(on)); return; }
      const ob = t.closest('[data-o]'); if (ob) { origin = ob.dataset.o; press(q('#bd-origin'), 'data-o', origin); renderPeriod(); return; }
      const oa = t.closest('[data-oath]'); if (oa) { const on = oa.getAttribute('aria-pressed') !== 'true'; press(q('#bd-oath'), 'data-oath', on ? oa.dataset.oath : ''); return; }
      if (t.closest('#bd-tofree')) { stash(); F.free = !free; startBuild(m); return; }
      if (t.closest('.back')) { stash(); hide(buildEl); if (frame) { bookHide(false); tableOn(false); } else toTable(); }
    });
    const yearEl = q('#bd-year');
    if (yearEl) yearEl.addEventListener('input', () => { const y = yearOf(yearEl.value), np = periodAt(y); if (np && np !== P) { P = np; } renderPeriod(); });

    const v = (k) => { const el = q('#bd-' + k); return el ? el.value.trim() : ''; };
    function stash() {
      Object.assign(F, { year: v('year'), place: v('place'), name: v('name'), sex: v('sex'), age: v('age'), race, sub, kin, race2: v('race2'), look: v('look'), from: v('from'), skill2: v('skill2'), art: v('art'), face: v('face'), extra: v('extra'), wish: v('wish'), origin,
        skills: [...form.querySelectorAll('#bd-skills [aria-pressed="true"]')].map((b) => b.dataset.s), oath: (form.querySelector('#bd-oath [aria-pressed="true"]') || { dataset: {} }).dataset.oath || '' });
    }
    // 回去改的时候把上一回填的放回来
    for (const k of ['year', 'place', 'name', 'sex', 'age', 'race2', 'look', 'from', 'skill2', 'art', 'face', 'extra', 'wish']) { const el = q('#bd-' + k); if (el && F[k]) el.value = F[k]; }
    press(q('#bd-origin'), 'data-o', origin);
    if (free && F.year) { const np = periodAt(yearOf(F.year)); if (np) P = np; }
    renderPeriod();
    if (F.race && (P.races || []).includes(F.race)) { race = F.race; sub = F.sub || ''; kin = F.kin || ''; press(q('#bd-races'), 'data-r', race); raceDetail(); }
    if (F.oath && q('#bd-oath')) press(q('#bd-oath'), 'data-oath', F.oath);

    form.addEventListener('submit', (e) => {
      e.preventDefault(); stash();
      const err = q('.bd-err'), bad = (t, el) => { err.textContent = t; if (el) { el.focus(); el.scrollIntoView({ block: 'center', behavior: 'smooth' }); } else err.scrollIntoView({ block: 'center', behavior: 'smooth' }); };
      if (!F.name) return bad('名字还没写。', q('#bd-name'));
      if (free) { const y = yearOf(F.year); if (y == null || y < FR.from || y > FR.to) return bad(`哪一年要写一个数，${era} ${FR.from} 到 ${FR.to} 年之间。`, yearEl); }
      if (!F.race && !F.race2) return bad('种族挑一个，或者自己写。');
      err.textContent = '';
      leave(credential(D, E, P, m, free));
    });
    bookHide(true); tableOn(true);          // 书先藏着（不拆，回去改的时候还在原处），建档的底下垫着牌桌上这一纪的画
    show(buildEl); buildEl.scrollTop = 0;
  }
  /* 凭证：照现行那一套的写法（首轮入局驱动认得），头一行是这一纪的开局口令。写法在 data/build.json 的 format 里 */
  function credential(D, E, P, m, free) {
    const fm = D.format || {}, df = fm.defaults || {}, era = E.name || ERA[m.book], FR = E.free || {};
    const R = (E.races || {})[F.race] || {}, gold = F.origin === 'gold';
    const S = (E.sheets && P.sheet && E.sheets[P.sheet]) || E.sheet || {};
    const line = m.line || '';
    const start = E.start === 'line' ? line : (line.indexOf('·') >= 0 ? line.slice(line.indexOf('·') + 1) : line);
    const yr = yearOf(F.year);
    let open = free ? `纪元：${era}｜开局时段：${String(FR.cmd || (FR.label + '｜年份：{year}')).replace('{year}', yr === 1 && m.book === 'strife' ? '元' : yr)}` : `纪元：${era}｜开局时段：${start}`;
    if (gold) open += fm.opening_golden || '｜出身：黄金裔';
    const raceText = ([R.name || '', F.sub, F.kin].filter(Boolean).join(' · ') + (F.race2 ? '　' + F.race2 : '') || '未选择') + (gold ? '（黄金裔，凡人那一头是这一族）' : '');
    const skill = (F.skills || []).concat(F.skill2 ? [F.skill2] : []).join('、') || '未选择（由 AI 照这一纪的本事和我的来处定一个方向）';
    const art = F.art ? `立绘：${F.art}${F.face ? '｜头像:' + F.face : ''}` : '立绘：' + (df['立绘'] || '无');
    const age = F.age ? F.age + (gold ? '' : (fm.age_suffix || '')) : '未填写（' + (gold ? '' : '落地多大就多大，') + '由 AI 按容貌与经历定一个，开场用一句话说明，不得默认十八岁）';
    const soul = gold ? '这一纪生下来的人 · 黄金裔（有父母，跟着凡人那一头长大，神亲是谁不点破）' : (fm.soul || '降临之魂 · 身穿（连人带身跌入）');
    const from = gold ? '长在：' + (F.from || '未详述（由 AI 照这一纪寻常的出身定一处）') : (F.from ? '来处：' + F.from : '来处：未详述（降临者报不出这里的出身' + (S.blank && S.blank.label ? '，册子上“' + S.blank.label + '”那一栏空着' : '') + '）');
    const where = free ? `${era}${yr}年${F.place ? '，' + F.place : ''}（${FR.label || '自己报的年份'}，照那一年的时段总纲和地点起头）` : `${era}${m.year ? (m.book === 'strife' && /^1年?$/.test(String(m.year).replace(/\s/g, '')) ? '元年' : String(m.year).replace(/\s/g, '').replace(/年$/, '') + '年') : ''}，${m.title ? m.title + '，' : ''}主线「${line}」的开局`;
    return [open, '', fm.head || '命途已确认，请记录我的《奥尔德兰》角色建档：', '',
      '【一·灵魂形态】', soul, from, '',
      '【二·种族胎骨】', raceText, '',
      '【三·命路倾向】', skill, '',
      '【四·姓名容貌】', '姓名：' + F.name, '年龄：' + age, '性别：' + (F.sex || df['性别'] || '未填写'), '容貌：' + (F.look || df['容貌'] || '未详述'),
      '体态数据：身高 未记录（由AI按种族与出身补全）｜体型 未记录（由AI补全）　（静态资产，状态栏逐轮照抄，正文不主动报数）', art, '自定义设定：' + (F.extra || df['自定义设定'] || '（无）'),
      '初始实力：' + (df['初始实力'] || '启源·初识'),
      fm.note || '※ 凡标注「未记录／未选择」的项，由 AI 在首轮按已确定的内容补全，并在开场时用一句话说明补了哪些。', '',
      '【五·命星天赋】', 'Passive/Special：' + (gold ? '未选择（照这一纪黄金裔的规矩给一样天生的，样子跟着神亲的神性走，开场说明）' : '未选择（照这一纪的规矩来，这一纪不给落进来的人的就写无）'), 'Art/Active：未选择（同上）', '',
      '【六·誓心与赐物】', '誓心阵营：' + (F.oath || '随便（由世界照我的来处推一个，开场明说是推的）'), '神殿赐物：' + (df['神殿赐物'] || '未选择（拒绝了她的馈赠）'), '',
      '【七·现在何处】', '现在所在：' + where, '当前处境：' + (gold ? '这一纪生下来的人，从这一段的开局起头。' : '刚从死之神殿落下来，身上只有这一身。'), '',
      '【八·冒险初心】', F.wish || '还没想好（先走着看，头一轮不必追问）', '',
      fm.tail || '开始游戏。',
    ].join('\n');
  }

  /* ---------- 请离那一眼，再出确认页 ---------- */
  function leave(text) {
    const D = BUILD || {}, words = (D.ronova && D.ronova.leave) || ['去吧。'];
    const img = leaveEl.querySelector('img'), p = leaveEl.querySelector('p');
    img.src = A('assets/ronova.webp'); p.textContent = words[0];
    leaveEl.className = ''; show(leaveEl); hide(buildEl);
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches, T = reduce ? [100, 300, 900, 1400] : [900, 1900, 4300, 5600];
    setTimeout(() => leaveEl.classList.add('see'), T[0]);
    setTimeout(() => leaveEl.classList.add('say'), T[1]);
    setTimeout(() => { leaveEl.classList.add('gone'); leaveEl.classList.remove('say'); }, T[2]);
    setTimeout(() => { seal(text); hide(leaveEl, 900); }, T[3]);
  }
  function seal(text) {
    const tooLong = text.length > LIMIT;
    sealEl.innerHTML = `<div class="sl-wrap"><h2>建档凭证</h2><p class="sub">${tooLong ? '这一份比输入框一回收得下的长，点“复制”，回到聊天里粘贴再发送。' : (inRili ? '点“填进输入框”，凭证会落在聊天的输入框里，再点发送，就从那一年睁眼。' : '复制下来，回到聊天的输入框里粘贴，再发送。')}</p>
<div class="sl-paper" tabindex="0"></div>
<div class="sl-acts">${tooLong || !inRili ? '' : '<button type="button" class="go" data-a="fill">填进输入框</button>'}<button type="button" data-a="copy"${tooLong || !inRili ? ' class="go"' : ''}>复制</button><button type="button" data-a="edit">回去改</button><button type="button" data-a="table">回到牌桌</button></div>
<p class="sl-tip" aria-live="polite"></p></div>`;
    sealEl.querySelector('.sl-paper').textContent = text;
    const tip = sealEl.querySelector('.sl-tip'), say = (t, ok) => { tip.textContent = t; tip.classList.toggle('ok', !!ok); };
    sealEl.onclick = (e) => {
      const b = e.target.closest('[data-a]'); if (!b) return;
      const a = b.dataset.a;
      if (a === 'fill') { try { window.parent.postMessage({ type: 'rili-set-input', value: text }, '*'); say('填进去了。点一下发送，她就把你送过去。输入框里没有的话，点“复制”再粘贴。', true); } catch (err) { say('没填进去，点“复制”再粘贴。'); } }
      else if (a === 'copy') copy(text).then((ok) => say(ok ? '复制好了。回到聊天的输入框里粘贴，再发送。' : '没复制上：长按上面那一段文字，全选了再复制。', ok));
      else if (a === 'edit') { hide(sealEl); if (pend) startBuild(pend); }          // 1001 年那一页的凭证没有 pend：收起这一层，底下就是它自己铸印的那一幕，在那里往回改
      else if (a === 'table') { hide(sealEl); toTable(); }
    };
    show(sealEl); sealEl.scrollTop = 0;
  }
  function copy(text) {
    const old = () => { try { const ta = document.createElement('textarea'); ta.value = text; ta.style.cssText = 'position:fixed;left:-9999px;top:0'; document.body.appendChild(ta); ta.select(); const ok = document.execCommand('copy'); ta.remove(); return ok; } catch (e) { return false; } };
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text).then(() => true).catch(() => old());
    return Promise.resolve(old());
  }

  window.Shell = Shell;
  Shell.startBuild = startBuild; Shell.credential = () => (pend ? '' : '');
  function A(p) { return window.A ? window.A(p) : p; }
})();
