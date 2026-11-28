/* 外壳（11-15 拼装那一轮）：牌桌那一页选定纪元以后的事都在这里。
   一、装书：这一纪的书是各自一个页面，拿过来装进一格 iframe（srcdoc）。头上塞 <base> 和一小段：告诉它图和数据在哪几个地址（window.A）、怎么跟外壳说话（window.SHELL）。
   二、书里“从这里进”→ 建档（照那一纪的册子画的一张登记表，字和可选的种族在 data/build.json）→ 请离那一眼 → 确认页（凭证填进聊天输入框，超过 8192 字就只给复制）。
   三、牌桌右上角的大图书馆（common/library.js，11-24 起替下世界之书的入口；世界之书 common/codex.js 留着，只管地图，图书馆的地图室翻它）。
   地址：装进卡里的时候，薄壳先给 window.FRONT_CFG（四本书各在图床的哪个地址、哪几个目录另放一段）；本地看的时候照下面 DEF（书在旁边的目录里）。 */
/* 11-27 止血（风月安卓 App 里玩家停在载入页第一拍那一团火上、整页划不动）：外壳的脚本只要跑起来，就一定把载入页拆掉——
   载入页自己报“卡住了”（window.__gate.alive() 为 false），或者七秒了载入页的脚本还没跑起来，就拆（有 __gateKill 调它，没有就直接拿掉 #gate、放开牌桌）。
   另补几样老内核（安卓系统 WebView 七八十版）没有的小东西：Object.fromEntries、String.prototype.matchAll、Array.prototype.flat／flatMap、Element.prototype.replaceChildren。 */
(function () {
  try {
    if (!Object.fromEntries) Object.fromEntries = function (it) { var o = {}; Array.from(it).forEach(function (kv) { o[kv[0]] = kv[1]; }); return o; };
    if (!String.prototype.matchAll) String.prototype.matchAll = function (re) { var r = new RegExp(re.source, re.flags.indexOf('g') < 0 ? re.flags + 'g' : re.flags), out = [], m; while ((m = r.exec(this))) { out.push(m); if (m[0] === '') r.lastIndex++; } return out[Symbol.iterator](); };
    if (!Array.prototype.flat) Array.prototype.flat = function (d) { d = d === undefined ? 1 : d; return this.reduce(function (a, x) { return a.concat(Array.isArray(x) && d > 0 ? x.flat(d - 1) : [x]); }, []); };
    if (!Array.prototype.flatMap) Array.prototype.flatMap = function (f, t) { return this.map(f, t).flat(1); };
    if (window.Element && !Element.prototype.replaceChildren) Element.prototype.replaceChildren = function () { while (this.firstChild) this.removeChild(this.firstChild); for (var i = 0; i < arguments.length; i++) this.append(arguments[i]); };
  } catch (e) {}
  var t0 = Date.now();
  function drop(why) {
    var g = document.getElementById('gate'); if (!g) return;
    if (typeof window.__gateKill === 'function') { try { window.__gateKill(why); } catch (e) {} }
    g = document.getElementById('gate');
    if (g) { try { g.parentNode.removeChild(g); } catch (e) { g.style.display = 'none'; } window.__tbPause = false; window.__gateWhy = why; }
  }
  function check() {
    if (!document.getElementById('gate')) return;
    var G = window.__gate;
    if (!G || typeof G.alive !== 'function') { if (Date.now() - t0 > 7000) { drop('外壳保底：载入页的脚本没跑起来'); return; } }
    else { var ok = true; try { ok = G.alive(); } catch (e) { ok = false; } if (!ok) { drop('外壳保底：载入页卡住了'); return; } }
    setTimeout(check, 1000);
  }
  setTimeout(check, 1000);
})();
(function () {
  'use strict';
  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  // 11-24 第五本书“此刻”（迷宫纪 1001 年，小样_此刻书/）：牌桌正中那张正面朝上的牌开它；卡里旧的薄壳不认它的时候（FRONT_CFG 里没有 now），那张牌退回开旧 1001 页
  const BOOKS = ['moon', 'strife', 'bronze', 'maze', 'now'], ERA = { moon: '月银纪', strife: '纷争纪', bronze: '山铜纪', maze: '迷宫纪', now: '此刻' };
  const DEF = { books: { moon: { core: '../小样_月银纪书/' }, strife: { core: '../小样_纷争纪书/' }, bronze: { core: '../小样_山铜纪书/' }, maze: { core: '../小样_迷宫纪书/' }, now: { core: '../小样_此刻书/' } }, old1001: '' };
  const CFG = Object.assign({}, DEF, window.FRONT_CFG || {});
  const HERE = new URL('.', document.baseURI).href;          // 外壳自己在哪（common/、data/、assets/ 都在它底下）
  const LIMIT = 8192;                                        // 日里那条填输入框的指令一回最多收这么多字（11-12 探针量的）
  const inRili = window.parent && window.parent !== window;
  let BUILD = null, cur = null, frame = null, pend = null, spoil = false, picked = -1;

  /* ---------- 预载（11-17 夜）：日里的介绍页在沙箱里，浏览器不留缓存（同一个文件取两回就下两回，探针量过），
     书的页面和一开就要的数据先取进内存；书里取 JSON 先找这里（装书那一段的 fetch 认 parent.__preGet），外壳自己取的 JSON 也走这里。 ---------- */
  const PRE = {}, fetch0 = window.fetch.bind(window);
  const preGet = (u) => PRE[u] || (PRE[u] = fetch0(u).then((r) => { if (!r.ok) throw new Error(r.status); return r.text(); }).catch((e) => { delete PRE[u]; throw e; }));
  window.__preGet = preGet;
  window.fetch = function (u, o) {
    if (typeof u !== 'string' || !/\.json(\?|$)/.test(u) || (o && o.method && o.method !== 'GET')) return fetch0(u, o);
    let w = u;
    try { w = new URL(u, document.baseURI).href; } catch (e) { /* 照原样 */ }
    return preGet(w).then((t) => new Response(t, { status: 200, headers: { 'content-type': 'application/json' } }), () => fetch0(u, o));
  };
  // 四本书一翻开就取的那几份（各本 index.html 里 fetch 的、加上图鉴的 atlas.json），书的页面排在最前头
  const BOOT = {
    moon: ['moon', 'cards', 'cg', 'have', 'pa', 'tiles', 'atlas'],
    strife: ['strife', 'card', 'cards', 'cg', 'have', 'pa', 'road', 'roadc', 'atlas'],
    bronze: ['bronze', 'road', 'cards', 'cg', 'have', 'pa', 'props', 'sky', 'stele', 'tex', 'walk', 'atlas'],
    maze: ['maze', 'cards', 'have', 'mural', 'pa', 'atlas'],
    now: ['now', 'atlas'],
  };
  /* 11-26 载入页（底稿/门面/载入页/）：路边五处火对五本书，一本的页面和开书数据都取回来了，告诉载入页（window.__gateBook）那一处亮起来。
     有载入页的时候不等四秒：门口要的东西（第零层，window.__gateL0）齐了就取，免得跟门口的东西抢带宽（慢网上量过，两秒半就开始取的话门要晚好几秒）；
     点了跳过、开了门，载入页也会兑现它。 */
  const tellGate = (id, ok) => { try { if (window.__gateBook) window.__gateBook(id, ok); } catch (e) { /* 载入页已经撤了 */ } };
  function preloadAll() {
    if (navigator.connection && navigator.connection.saveData) { BOOKS.forEach((id) => tellGate(id, false)); return; }          // 开着省流量就不预载
    const q = [], left = {};
    for (const id of BOOKS) {
      const B = CFG.books[id];
      if (!B) { tellGate(id, false); continue; }
      const core = new URL(B.core, HERE).href;
      q.push([id, core + 'index.html']);
      for (const f of BOOT[id] || []) q.push([id, core + 'data/' + f + '.json']);
    }
    for (const [id] of q) left[id] = (left[id] || 0) + 1;
    let i = 0;      // 两路并着取；哪一个八秒不回话就先往下取，不让它把后头的都堵住（那一个照旧在取，取到了照样存下）
    const one = () => {
      if (i >= q.length) return;
      const [id, u] = q[i++], p = preGet(u);
      p.then(() => 1, () => 0).then(() => { if (--left[id] === 0) tellGate(id, true); });
      Promise.race([p, new Promise((r) => setTimeout(r, 8000))]).then(one, one);
    };
    one(); one();
  }
  if (window.__gateL0) window.__gateL0.then(preloadAll);
  else setTimeout(() => (window.requestIdleCallback ? (f) => requestIdleCallback(f, { timeout: 3000 }) : (f) => setTimeout(f, 0))(preloadAll), 4000);

  /* ---------- 页面上加的几层 ---------- */
  const mk = (tag, id, html) => { const el = document.createElement(tag); if (id) el.id = id; if (html) el.innerHTML = html; document.body.appendChild(el); return el; };
  const wbBtn = mk('button', 'wbBtn', `<img src="${A('common/assets/ui/wb_cover.webp')}" alt=""><span>大图书馆</span>`);
  wbBtn.type = 'button'; wbBtn.setAttribute('aria-label', '走进大图书馆');
  const libHost = mk('div', 'sh-lib');          // 大图书馆（11-24），盖在牌桌上、世界之书底下（地图室翻开的世界之书要在它上面）
  const codexHost = mk('div', 'sh-codex');
  const bookEl = mk('div', 'sh-book', '<div class="sh-veil"><u></u><b></b><em></em><i></i><span>这一纪的书正在翻开</span></div>'); bookEl.hidden = true;
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

  /* ---------- 世界之书（11-24 起只管地图：图书馆的地图室翻它；点了哪个时代就去那一纪的书） ---------- */
  const libOpen = () => !!(window.Library && Library.isOpen());
  if (window.Codex) {
    Codex.init({ vol: 'general', host: codexHost, A: window.A, spoil: () => spoil, setSpoil: (v) => { spoil = v; if (window.Library) Library.syncSpoil(); }, onOpen: () => { window.__tbPause = true; }, onClose: () => { if (!cur && buildEl.hidden && !libOpen()) window.__tbPause = false; }, onEra: (vol, id) => openBook(vol, id) });
  }
  /* ---------- 大图书馆（11-24）：牌桌右上角那一枚，进门是圆厅 ---------- */
  if (window.Library) {
    Library.init({ vol: 'general', host: libHost, A: window.A, spoil: () => spoil, setSpoil: (v) => { spoil = v; if (window.Codex) Codex.syncSpoil(); },
      openMap: (v) => { if (window.Codex) Codex.open(v, 'map'); },
      onOpen: () => { window.__tbPause = true; document.body.classList.add('sh-libon'); }, onClose: () => { document.body.classList.remove('sh-libon'); if (!cur && buildEl.hidden && !(window.Codex && Codex.isOpen())) window.__tbPause = false; } });
    wbBtn.addEventListener('click', () => Library.open());
  } else if (window.Codex) wbBtn.addEventListener('click', () => Codex.open('general', ''));
  else wbBtn.hidden = true;

  /* ---------- 装书 ---------- */
  const abs = (u) => new URL(u, HERE).href;
  // 图床的几个镜像（跟薄壳那一份一样）：书里一张图载不下来，换下一个镜像再载（11-17 夜）
  const MIRRORS = ['https://cdn.jsdelivr.net/', 'https://fastly.jsdelivr.net/', 'https://gcore.jsdelivr.net/', 'https://testingcf.jsdelivr.net/', 'https://quantil.jsdelivr.net/'];
  function preamble(M, at) {
    return '(function(){var M=' + JSON.stringify(M) + ',MIR=' + JSON.stringify(MIRRORS) + ';'
      + 'window.A=function(p){for(var k in M)if(p.indexOf(k)===0)return M[k]+p;return p};'
      + 'window.SHELL={at:' + JSON.stringify(at || '') + ',post:function(m){m.aldran=1;parent.postMessage(m,"*")}};'
      // 11-26 夜 交互音效：书里调 SFX(名)，外壳放（书里不另开声音）。只认真人点出来的那一下（window.event 是真的），书自己初始化、原地重画的时候不响；第二个参数给 true 就不看这个
      + 'if(!Object.fromEntries)Object.fromEntries=function(it){var o={};Array.from(it).forEach(function(kv){o[kv[0]]=kv[1]});return o};if(!Array.prototype.flat)Array.prototype.flat=function(d){d=d===undefined?1:d;return this.reduce(function(a,x){return a.concat(Array.isArray(x)&&d>0?x.flat(d-1):[x])},[])};if(!Array.prototype.flatMap)Array.prototype.flatMap=function(f,t){return this.map(f,t).flat(1)};'
      + 'window.SFX=function(n,any){var e=window.event;if(!any&&!(e&&e.isTrusted))return;try{parent.postMessage({aldran:1,t:"sfx",n:n},"*")}catch(x){}};'
      + 'var f0=window.fetch.bind(window),G=null;try{G=parent.__preGet||null}catch(x){}window.__preVia=G?"direct":"msg";'
      // 沙箱里书那一格跟外壳不同源，拿不到外壳的变量：发消息问外壳要（外壳从内存里给，正在取的等它取完），二十秒没回话就自己去取
      + 'if(!G){var pn=0,pw={};window.addEventListener("message",function(e){var m=e.data;if(!m||m.aldran!==1||m.t!=="preR"||!pw[m.id])return;var w=pw[m.id];delete pw[m.id];clearTimeout(w.k);if(m.ok)w.res(m.text);else w.rej(new Error("pre"))});'
      + 'G=function(u){return new Promise(function(res,rej){var id=++pn;pw[id]={res:res,rej:rej,k:setTimeout(function(){if(pw[id]){delete pw[id];rej(new Error("pre timeout"))}},20000)};parent.postMessage({aldran:1,t:"pre",id:id,u:u},"*")})}}'
      + 'var J=function(t){for(var k in M)if(k!=="common/")t=t.split(\'"\'+k).join(\'"\'+M[k]+k);return new Response(t,{status:200,headers:{"content-type":"application/json"}})};'
      + 'window.fetch=function(u,o){if(typeof u!=="string")return f0(u,o);var j=/\\.json(\\?|$)/.test(u),a=window.A(u);'
      + 'var d=function(){return f0(a,o).then(function(r){if(!j||!r.ok)return r;return r.text().then(J)})};'
      + 'if(!j||!G||(o&&o.method&&o.method!=="GET"))return d();var w=a;try{w=new URL(a,document.baseURI).href}catch(x){}'
      + 'return G(w).then(J,d)};'
      + 'document.addEventListener("error",function(e){var t=e.target;if(!t||t.tagName!=="IMG")return;var s=t.getAttribute("src")||"",n=+(t.getAttribute("data-mr")||0);if(n>=MIR.length-1)return;'
      + 'for(var i=0;i<MIR.length;i++)if(s.indexOf(MIR[i])===0){t.setAttribute("data-mr",n+1);t.setAttribute("src",MIR[(i+1)%MIR.length]+s.slice(MIR[i].length));return}},true);'
      + 'window.addEventListener("error",function(e){try{parent.postMessage({aldran:1,t:"err",msg:String(e.message||e.type).slice(0,200)},"*")}catch(x){}});'
      + 'var r0=window.requestAnimationFrame.bind(window),pq=[],pz=false;'
      + 'window.requestAnimationFrame=function(f){if(pz){pq.push(f);return 0}return r0(f)};'
      + 'window.addEventListener("message",function(e){var m=e.data;if(!m||m.aldran!==1||m.t!=="pause")return;pz=!!m.on;window.__paused=pz;if(!pz){var q=pq;pq=[];for(var i=0;i<q.length;i++)r0(q[i])}});'
      + '})();';
  }
  /* 路的尽头翻到下一本（11-23）：书发 goto 带 turn。幕先在这一本上头浮起来，写下一纪的序号、名字和牌桌上那张牌底下的一句（跟 index.html 的 ERAS 一样），
     盖严了再拆这一本、装下一本，装好了幕照常退下去。 */
  const TURN = {
    moon: { num: 'Ⅰ', line: '天亮以前，人只有火。', tint: '176,204,255' },
    strife: { num: 'Ⅱ', line: '神和魔神倒在墙的两边，墙还站着。', tint: '255,150,128' },
    bronze: { num: 'Ⅲ', line: '机器睡了，剑醒了。两个王背对背走远。', tint: '255,214,150' },
    maze: { num: 'Ⅳ', line: '地开了。人一层一层往下走。', tint: '150,176,255' },
    now: { num: 'Ⅴ', line: '灯火照旧。远处，钟敲了第一声。', tint: '255,198,120' },          // 11-24 迷宫纪那一本的尽头翻到此刻，此刻的尽头翻回月银纪
  };
  let turning = 0;
  function turnBook(id) {
    const T = TURN[id];
    if (!T || turning) return;
    veil.querySelector('u').textContent = T.num; veil.querySelector('b').textContent = ERA[id]; veil.querySelector('em').textContent = T.line;
    veil.querySelector('span').textContent = '';
    veil.style.setProperty('--sh-turn', T.tint);
    veil.classList.add('turn'); veil.classList.remove('off');
    turning = setTimeout(() => { turning = 0; openBook(id, '', true); }, 900);
  }
  async function openBook(id, at, turn) {
    const B = CFG.books[id];
    if (!B) { if (id === 'now') { if (turning) { clearTimeout(turning); turning = 0; } veil.classList.remove('turn'); openOld(); } return; }          // 卡里的薄壳还不认此刻那一本：退回旧 1001 页
    if (turning) { clearTimeout(turning); turning = 0; }
    if (window.Codex && Codex.isOpen()) Codex.close();
    if (libOpen()) Library.close(true);
    closeFrame();
    veil.classList.toggle('turn', !!turn);
    cur = id; busy(true); veil.classList.remove('off'); veil.querySelector('span').textContent = ERA[id] + '的书正在翻开';
    (window.__sfx || (() => {}))('book_open');          // 11-26 夜 交互音效：翻开书
    show(bookEl); setTimeout(() => { if (cur) tableOn(false); }, 650);
    const core = abs(B.core), M = { 'common/': HERE };
    for (const k in (B.parts || {})) M[k] = abs(B.parts[k]);
    let html;
    try { html = await preGet(core + 'index.html'); }          // 预载过就不再下
    catch (e) { veil.classList.remove('turn'); veil.querySelector('span').textContent = '这一本没有载下来'; const b = document.createElement('button'); b.textContent = '回到牌桌'; b.onclick = () => { b.remove(); toTable(); }; veil.appendChild(b); return; }
    if (cur !== id) return;
    for (const k in M) if (k !== 'common/') html = html.split(k).join(M[k] + k);        // 另放一段的那几个目录（assets/ps/ 这些）换成图床的地址
    html = html.replace(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com([^"]*)"(?![^>]*media=)/g, '<link rel="stylesheet" href="https://fonts.googleapis.com$1" media="print" onload="this.media=\'all\'"');   // 字体不挡着页面
    frame = document.createElement('iframe'); frame.id = 'sh-frame'; frame.setAttribute('title', ERA[id] + '的书'); frame.setAttribute('allow', 'autoplay; fullscreen');
    frame.srcdoc = '<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><base href="' + core + '"><script>' + preamble(M, at) + '<\/script></head><body>' + html + '</body></html>';
    frame.addEventListener('load', () => setTimeout(() => { veil.classList.add('off'); if (turn) setTimeout(() => { if (veil.classList.contains('off')) veil.classList.remove('turn'); }, 800); }, turn ? 1500 : 900));      // 翻下一本的那一回幕多停一会，字念得完
    bookEl.insertBefore(frame, veil);
  }
  function closeFrame() { if (frame) { frame.remove(); frame = null; } cur = null; bookEl.style.visibility = ''; }
  /* 书藏起来（不拆，回去的时候还在原处）：藏着的时候叫它别画帧，手机上不跟牌桌抢 */
  function bookHide(on) {
    bookEl.style.visibility = on ? 'hidden' : '';
    if (frame && frame.contentWindow) { try { frame.contentWindow.postMessage({ aldran: 1, t: 'pause', on: !!on }, '*'); } catch (e) {} }
  }
  function toTable() {
    if (turning) { clearTimeout(turning); turning = 0; }
    veil.classList.remove('turn');
    closeFrame(); closeOld(); hide(bookEl); hide(buildEl); busy(false); tableOn(true);
    if (window.__tb && __tb.again) __tb.again();
  }
  window.addEventListener('message', (ev) => {
    const m = ev.data || {};
    if (!m.aldran) return;
    if (frame && ev.source === frame.contentWindow) {
      if (m.t === 'table') toTable();
      else if (m.t === 'goto' && (CFG.books[m.book] || m.book === 'now')) { if (m.turn && CFG.books[m.book]) turnBook(m.book); else openBook(m.book, m.at); }
      else if (m.t === 'enter') { if (m.old || (m.at === '1001' && !m.site)) openOld(); else startBuild(m); }          // 11-24：1001 年从此刻那一本进，带着起点（site）走外壳的建档；带 old 的是书里那一枚“旧版建档与接续旧档”
      else if (m.t === 'err') console.warn('书里报错', cur, m.msg);
      else if (m.t === 'pre' && typeof m.u === 'string' && /^https?:\/\/[^?#]+\.json(\?|$)/.test(m.u)) {      // 书要一份 JSON：从内存里给（沙箱里书那一格拿不到外壳的变量，只能这样转交）
        const src = ev.source, id = m.id;
        preGet(m.u).then((text) => { try { src.postMessage({ aldran: 1, t: 'preR', id, ok: 1, text }, '*'); } catch (e) {} },
          () => { try { src.postMessage({ aldran: 1, t: 'preR', id, ok: 0 }, '*'); } catch (e) {} });
      }
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
    if (libOpen()) Library.close(true);
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
  /* ---------- 牌桌正中那张正面朝上的牌：此刻（11-24，方向稿第三节） ----------
     若娜瓦扫出四张牌、四条画带铺开以后（牌桌走到 choose），第五张从上头翻着落下来，正面朝上停在正中（手机上停在右手边两条画带的缝上）。
     指上去浮出书名和一句；点它，牌放大、黄铜的光一闪，翻开此刻那一本。选定了别的纪（pick）、书或者建档开着的时候收起来。
     原来左上角那一枚“迷宫纪 1001 年 建档·接续旧档”拿掉了，旧 1001 页从此刻那一本里一枚小字的“旧版建档与接续旧档”进（openOld 留着）。 */
  const NOW_CSS = `
#nowCard{all:unset;position:fixed;z-index:6;left:50%;top:41%;--h:min(50vh,470px);height:var(--h);aspect-ratio:2/3;margin:calc(var(--h)/-2) 0 0 calc(var(--h)/-3);cursor:pointer;perspective:1600px;visibility:hidden;pointer-events:none;-webkit-tap-highlight-color:transparent}
#nowCard.on{visibility:visible;pointer-events:auto}
#nowCard .nc-in{position:absolute;inset:0;transform-style:preserve-3d;transform:translateY(-110vh) rotateY(180deg) rotateZ(-14deg);opacity:0;transition:transform 1.25s cubic-bezier(.16,.8,.22,1),opacity .5s ease}
#nowCard.on .nc-in{transform:none;opacity:1}
#nowCard.landed .nc-in{transition:transform .45s cubic-bezier(.2,.8,.3,1)}
#nowCard.landed:hover .nc-in,#nowCard.landed:focus-visible .nc-in{transform:translateY(-10px) scale(1.035)}
#nowCard .nc-face,#nowCard .nc-back{position:absolute;inset:0;border-radius:14px;overflow:hidden;backface-visibility:hidden;-webkit-backface-visibility:hidden}
#nowCard .nc-back{transform:rotateY(180deg);background:var(--nc-back) center/100% 100%}
#nowCard .nc-face{background:#0d2159 var(--nc-img) center top/100% auto no-repeat;box-shadow:0 26px 60px rgba(0,0,0,.7),0 0 0 1.5px rgba(214,176,112,.75),inset 0 0 0 4px rgba(6,10,30,.45);transition:box-shadow .4s}
#nowCard .nc-face::before{content:"";position:absolute;inset:6px;border-radius:10px;box-shadow:inset 0 0 0 1px rgba(214,176,112,.45)}
#nowCard .nc-face::after{content:"";position:absolute;inset:-20% -70%;background:linear-gradient(108deg,rgba(255,240,210,0) 44%,rgba(255,240,210,.32) 50%,rgba(255,240,210,0) 56%);transform:translateX(-70%);opacity:0}
#nowCard.landed .nc-face::after{animation:ncFoil 1.2s cubic-bezier(.3,.5,.3,1)}
#nowCard.landed:hover .nc-face::after{animation:ncFoil2 1s cubic-bezier(.3,.5,.3,1)}
@keyframes ncFoil{0%{transform:translateX(-70%);opacity:0}15%,85%{opacity:1}100%{transform:translateX(70%);opacity:0}}
@keyframes ncFoil2{0%{transform:translateX(-70%);opacity:0}15%,85%{opacity:1}100%{transform:translateX(70%);opacity:0}}
#nowCard:hover .nc-face,#nowCard:focus-visible .nc-face{box-shadow:0 30px 70px rgba(0,0,0,.75),0 0 0 2px rgba(255,198,120,.9),0 0 44px rgba(255,198,120,.35),inset 0 0 0 4px rgba(6,10,30,.45)}
#nowCard .nc-plate{position:absolute;left:0;right:0;bottom:5.5%;text-align:center;font-family:"Noto Serif SC","Songti SC",serif}
#nowCard .nc-plate b{display:block;font-weight:600;font-size:calc(var(--h)*.085);letter-spacing:.5em;text-indent:.5em;line-height:1.25;color:#eeeaf3;text-shadow:0 0 24px rgba(255,198,120,.45)}
#nowCard .nc-plate span{display:block;font-size:calc(var(--h)*.028);letter-spacing:.3em;text-indent:.3em;color:rgba(238,234,243,.7)}
#nowCard .nc-glow{position:absolute;left:50%;top:50%;width:150%;aspect-ratio:1;transform:translate(-50%,-50%) scale(.6);border-radius:50%;pointer-events:none;opacity:0;
  background:radial-gradient(closest-side,rgba(255,198,120,.24),rgba(255,198,120,.07) 45%,rgba(255,198,120,0) 72%);transition:opacity 1.2s ease .9s,transform 1.6s ease .9s}
#nowCard.on .nc-glow{opacity:1;transform:translate(-50%,-50%)}
#nowCard.landed .nc-glow{animation:ncBreathe 4.8s ease-in-out infinite alternate}
@keyframes ncBreathe{from{opacity:1}to{opacity:.55}}
#nowCard.go .nc-in{transform:scale(3.2)!important;opacity:0!important;transition:transform 1s cubic-bezier(.6,0,.2,1),opacity .5s ease .5s!important}
#nowCard:focus-visible{outline:none}
#nowTip{position:fixed;z-index:6;left:50%;top:calc(41% + min(50vh,470px)/2 + 14px);width:min(560px,92vw);margin-left:calc(min(560px,92vw)/-2);text-align:center;pointer-events:none;opacity:0;transform:translateY(10px);transition:opacity .45s ease,transform .45s ease;text-shadow:0 2px 14px rgba(0,0,0,.95);font-family:"Noto Serif SC","Songti SC",serif}
#nowTip.on{opacity:1;transform:none}
#nowTip b{display:block;font-weight:600;font-size:20px;letter-spacing:.34em;text-indent:.34em;color:#eeeaf3}
#nowTip b em{font-style:normal;color:rgb(214,176,112);margin:0 .2em}
#nowTip span{display:block;margin-top:6px;font-size:15px;letter-spacing:.14em;text-indent:.14em;color:#c9ccd8}
#nowFlash{position:fixed;inset:0;z-index:7;pointer-events:none;opacity:0;background:radial-gradient(70% 60% at 50% 50%,rgba(255,236,200,.95),rgba(255,198,120,.7) 40%,rgba(13,33,89,.95) 100%)}
#nowFlash.on{animation:ncFlash 1.5s ease forwards}
@keyframes ncFlash{0%{opacity:0}45%{opacity:1}100%{opacity:0}}
@media (max-aspect-ratio:1/1),(max-width:760px){
  #nowCard{left:auto;right:max(14px,4vw);top:47%;--h:min(34vh,44vw*1.5);margin:calc(var(--h)/-2) 0 0 0}
  #nowTip{display:none}
}
@media (prefers-reduced-motion:reduce){#nowCard .nc-in,#nowCard .nc-glow{transition:none!important}#nowCard .nc-face::after,#nowCard .nc-glow{animation:none!important}#nowFlash.on{animation:none}}`;
  mk('style', 'sh-now-css', NOW_CSS);
  const nowCard = mk('button', 'nowCard', '<span class="nc-glow"></span><span class="nc-in"><span class="nc-back"></span><span class="nc-face"><span class="nc-plate"><b>此刻</b><span>一千零一年</span></span></span></span>');
  nowCard.type = 'button'; nowCard.setAttribute('aria-label', '此刻，迷宫纪一千零一年。翻开这一本'); nowCard.tabIndex = -1;
  nowCard.style.setProperty('--nc-img', `url('${new URL(A('assets/now_card.webp'), document.baseURI).href}')`);
  nowCard.style.setProperty('--nc-back', `url('${new URL(A('assets/back_3.webp'), document.baseURI).href}')`);
  const nowTip = mk('div', 'nowTip', '<b>此刻<em>·</em>迷宫纪一千零一年</b><span>灯火照旧。远处，钟敲了第一声。</span>');
  const nowFlash = mk('div', 'nowFlash');
  let nowOn = false, nowLand = 0;
  const nowWanted = () => !!(window.__tb && __tb.stage === 'choose') && !cur && !oldFrame && buildEl.hidden && sealEl.hidden && leaveEl.hidden && !libOpen() && !(window.Codex && Codex.isOpen()) && !nowCard.classList.contains('go');
  function nowSync() {
    const want = nowWanted();
    if (want === nowOn) return;
    nowOn = want; clearTimeout(nowLand);
    nowCard.classList.toggle('on', want); nowCard.tabIndex = want ? 0 : -1;
    if (want) nowLand = setTimeout(() => nowCard.classList.add('landed'), matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 1300);
    else { nowCard.classList.remove('landed'); nowTip.classList.remove('on'); }
  }
  setInterval(nowSync, 250);
  const tipOn = (on) => nowTip.classList.toggle('on', on && nowOn);
  nowCard.addEventListener('mouseenter', () => tipOn(true)); nowCard.addEventListener('mouseleave', () => tipOn(false));
  nowCard.addEventListener('focus', () => tipOn(true)); nowCard.addEventListener('blur', () => tipOn(false));
  nowCard.addEventListener('click', () => {
    if (!nowOn) return;
    tipOn(false); nowCard.classList.add('go'); nowFlash.classList.remove('on'); void nowFlash.offsetWidth; nowFlash.classList.add('on');
    setTimeout(() => { openBook('now'); setTimeout(() => { nowCard.classList.remove('go', 'on', 'landed'); nowOn = false; }, 900); }, 650);
  });
  window.__now = { card: nowCard, sync: nowSync, wanted: nowWanted };          // 走查用

  /* ---------- 牌桌选定了一纪 ---------- */
  const openBtn = $('#openBook');
  if (openBtn) openBtn.addEventListener('click', () => { if (picked >= 0) openBook(BOOKS[picked]); });
  const Shell = { onEra(k) { picked = k; }, openBook, toTable, openOld, get state() { return { cur, picked, build: !buildEl.hidden, seal: !sealEl.hidden, frame: !!frame, old: !!oldFrame, pend }; } };

  /* ---------- 建档（11-17 第二版）：照迷宫纪 1001 年那一页的步子，十一步 ----------
     魂 → 睁眼之前 → 胎骨 → 金血 → 起点 → 六维 → 命路（月银纪是兵器与技艺）→ 命星 → 誓心与出身 → 落在哪 → 铸印。
     资料：data/build.json（各纪的册子、年代、种族、本事、命路、凭证的写法），data/gold.json（金血祝颂），data/gifts.json（身穿的赐物），
           data/stars.json（命星池，一颗星照四纪各写一份），common/data/map_<纪>.json（时代地图上的点）。
     规矩照 1001：起点十九档；六维单项上限是档的基数乘胎骨修正，可分配的是上限总和的一半；命星三池（Special、Passive、Art·Active，11-24 第二轮从两池分开）各抽十颗（Unique 2%、Legend 8%、Epic 25%，
     五抽以内保一颗 Legend、十二抽以内保一颗 Unique）；赐物一回五件（三抽保 Legend、八抽保 Unique）。四纪的差别照 前端精修_方向稿.md 第九节。
     做法写在 底稿/门面/建档第二版_做法.md。 */
  const loadBuild = () => BUILD ? Promise.resolve(BUILD) : fetch(A('data/build.json')).then((r) => r.json()).then((d) => (BUILD = d));
  const getJSON = (p, dflt) => fetch(A(p)).then((r) => (r.ok ? r.json() : dflt)).catch(() => dflt);
  const DATA = { gold: null, gifts: null, stars: null, maps: {}, life: null, art: null, land: null, pc: null };
  const loadAll = (book) => Promise.all([
    loadBuild().catch(() => (BUILD = { format: {}, eras: {} })),
    DATA.land || getJSON('data/land.json', null).then((d) => (DATA.land = d && d.eras ? d : { eras: {} })),          // 身穿的人照主线开局落在哪（11-25）
    DATA.life || getJSON('data/life.json', null).then((d) => (DATA.life = d && d.eras ? d : { eras: {} })),          // 走一遍前半生（11-24）
    DATA.pc || getJSON('data/pc_art.json', null).then((d) => (DATA.pc = d && d.pc ? d : { pc: {} })),          // 体格与立绘的预览（11-26，第二轮/建档/tools/pc_art.py 照状态栏主角预设写）
    DATA.art || getJSON('data/bx_art.json', null).then((d) => (DATA.art = d && d.have ? d : { have: [], hands: {} })),          // 建档的图有哪几张、手（11-24）
    DATA.gold || getJSON('data/gold.json', null).then((d) => (DATA.gold = d && d.eras ? d : { eras: {} })),
    DATA.gifts || getJSON('data/gifts.json', null).then((d) => (DATA.gifts = d && d.gifts ? d : { gifts: [], relics: [] })),
    DATA.stars || getJSON('data/stars.json', null).then((d) => (DATA.stars = d && d.stars ? d : { stars: [] })),
    book in DATA.maps ? DATA.maps[book] : getJSON('common/data/map_' + book + '.json', null).then((d) => (DATA.maps[book] = d)),
  ]);
  const yearOf = (s) => { const t = String(s || '').replace(/\s/g, ''); const m = t.match(/(\d{1,5})/); return m ? +m[1] : (/元年|^元$/.test(t) ? 1 : null); };
  /* 年岁可能写成汉字（二十、一百二十） */
  const numOf = (s) => {
    const t = String(s || '').trim(), m = t.match(/\d+/); if (m) return +m[0];
    const D = { 〇: 0, 零: 0, 一: 1, 二: 2, 两: 2, 三: 3, 四: 4, 五: 5, 六: 6, 七: 7, 八: 8, 九: 9 };
    let sum = 0, cur = 0, seen = false;
    for (const ch of t) {
      if (ch in D) { cur = D[ch]; seen = true; } else if (ch === '十') { sum += (cur || 1) * 10; cur = 0; seen = true; }
      else if (ch === '百') { sum += (cur || 1) * 100; cur = 0; seen = true; } else if (ch === '千') { sum += (cur || 1) * 1000; cur = 0; seen = true; }
      else if (seen) break;
    }
    return seen ? sum + cur : null;
  };
  /* 资料里有几份是照 1001 年那一页搬过来的（赐物、遗物），带着这张卡不用的几种标点：显示和凭证里都换掉。★ 和（★）是给作者看的，拿掉 */
  const clean = (s) => String(s == null ? '' : s).replace(/（★）|★/g, '').replace(/(\d)\s*[—–]\s*(\d)/g, '$1到$2')
    .replace(/——|—|–/g, '，').replace(/；/g, '，').replace(/…+/g, '。').replace(/！/g, '。').replace(/，\s*(?=[，。、）])/g, '').replace(/^[，\s]+|[，\s]+$/g, '');

  const K_OF = { moon: 0, strife: 1, bronze: 2, maze: 3 };
  const STEPS = ['魂', '睁眼之前', '胎骨', '金血', '起点', '六维', '命路', '命星', '誓心与出身', '落在哪', '铸印'];
  const NUM = ['', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一'];
  const SOUL = {
    native: { n: '本地之魂', tag: '生于此世', cred: '本地之魂（生于此世）', d: '你生在这一纪，有父母，有故乡。走出这座神殿，这里的事你会慢慢忘掉，睁开眼时，你已经是在那里长大的人。', i: '可以挑金血',
      say: ['「那你便生在那一纪。」', '「睁开眼的时候，你已经在那里长大了。」'] },
    reborn: { n: '转生之魂 · 胎穿', tag: '带着记性重来', cred: '转生之魂 · 胎穿（带前世记忆）', d: '你在另一个世界死去，还记得那一生。你会在这一纪重新出生、长大，带着只有自己知道的往事。', i: '可以挑金血',
      say: ['「你仍带着前世的记忆。」', '「走到这里的灵魂，原该放下旧事。既然你还记得，就带着它们重新生活。往后的选择，由你自己作出。」'] },
    isekai: { n: '降临之魂 · 身穿', tag: '原样落进来', cred: '降临之魂 · 身穿（连人带身跌入）', d: '你连同身体和随身之物一起到了这里。故乡、亲友和过去的生活都留在另一个世界，这一纪没有人见过你，你在这里没有生日，也没有故乡。', i: '她会给你一件赐物',
      say: ['「连身体也一同到了这里。」', '「你的旅程尚未结束。离开这座神殿，去看看那一纪吧。」'] },
  };
  const TIERS = [['启源·初识', 'LVL 1-7', 30], ['启源·凝华', 'LVL 8-14', 30], ['启源·临界', 'LVL 15-20', 30],
    ['共鸣·寻音', 'LVL 21-27', 60], ['共鸣·织理', 'LVL 28-34', 60], ['共鸣·破障', 'LVL 35-40', 60],
    ['灵格·塑形', 'LVL 41-54', 150], ['灵格·极诣', 'LVL 55-67', 150], ['灵格·辉耀', 'LVL 68-80', 150],
    ['极境·绝地', 'LVL 81-94', 300], ['极境·峙岳', 'LVL 95-107', 300], ['极境·凡巅', 'LVL 108-120', 300],
    ['英雄·破格', 'LVL 121-146', 600], ['英雄·铸史', 'LVL 147-173', 600], ['英雄·冠名', 'LVL 174-200', 600],
    ['传奇·撼世', 'LVL 201-225', 999], ['传奇·天灾', 'LVL 226-250', 999], ['传奇·圣座', 'LVL 251-299', 999], ['传奇·凡极', 'LVL 300', 999]];
  const TIER_GROUP = [['启源', 'LVL 1 到 20'], ['共鸣', 'LVL 21 到 40'], ['灵格', 'LVL 41 到 80'], ['极境', 'LVL 81 到 120'], ['英雄', 'LVL 121 到 200'], ['传奇', 'LVL 201 到 300']];
  const tierOf = (k) => TIERS.find((t) => t[0] === k) || TIERS[0];
  /* 起点那一步，档照这一纪量人的说法改叫（★，照方向稿第九节第 2 小节第四步） */
  const MEASURE = {
    // 一句话不带你我，页上和凭证里都读得通
    moon: { t: '这一纪没有面板，人看不见位阶，量一个人看他斩过什么', g: { 启源: '刚拿得动兵器，还没斩过什么', 共鸣: '斩过寻常的兽，跟着猎过几回', 灵格: '斩过一头有名有号的兽，一城都听说过', 极境: '斩过大兽，守得住一座城', 英雄: '斩过兽王，歌里唱过这个名字', 传奇: '名字凝住了，诗人唱过好几个国' } },
    strife: { t: '这一纪的人看不见位阶，墙上量一个人，看他守过哪一段，挡下过谁', g: { 启源: '刚上墙，还没挡下过什么', 共鸣: '守过一段墙，挡下过几回小股的魔物', 灵格: '一段墙上都叫得出名字，战报写过一回', 极境: '一方镇将，守得住一座段城', 英雄: '战报写过好几回，挡下过有名者', 传奇: '名字凝住了，一个人顶得住一段墙' } },
    bronze: { t: '这一纪的人看不见位阶，量一个人，看他做成过什么，碑上有没有他', g: { 启源: '还没做成过什么', 共鸣: '接过几回活，团里认得这个人', 灵格: '做成过一件，一座段城都知道', 极境: '做成过几件大事，碑的背面刻着名字', 英雄: '做成的那一件，碑匠专门来刻过碑', 传奇: '名字凝住了，上了碑的正面' } },
    maze: { t: '420年以前人看不见位阶，公会量人看档次和他下过的井', g: { 启源: '刚按了印，下井还要人领', 共鸣: '下过几回井，带得回自己', 灵格: '井口的人都认得，下过深一点的层', 极境: '交过几回大差，有一队人肯跟着下', 英雄: '公会的册子上记着做成过的事', 传奇: '名字凝住了，公会名录上有一行' } },
    panel: { t: '420年起公会的面板照得出位阶', g: { 启源: '尚未成名的年头', 共鸣: '有了自己的门路', 灵格: '一城之内都听过这个名字', 极境: '凡人的天花板', 英雄: '被写进史诗的人', 传奇: '这一代的传奇之一' } },
  };
  const STAT = [['STR', '力量', '肌力、负重、近战冲击'], ['DEX', '敏捷', '身法、命中、闪避、潜行与精密动作'], ['MANA', '魔力', '魔法威力、魔力周转与魔导器'], ['MIND', '精神', '魔力总量、意志、专注与学习'], ['VGR', '体魄', '耐力与恢复，抗毒抗病与承伤'], ['FTH', '感应', '祷告、奇迹、神圣与自然的共鸣']];
  const RACE_MOD = { 人类: {}, 高等精灵: { MANA: 30, MIND: 30, STR: -20, VGR: -20 }, 木精灵: { DEX: 20, FTH: 20, MANA: 10, STR: -10, VGR: -10 }, 暗精灵: { DEX: 20, MANA: 20, MIND: 15, VGR: -10, FTH: -5 },
    矮人: { STR: 30, VGR: 30, MANA: -20, DEX: -20 }, 半身人: { DEX: 20, FTH: 20, STR: -15, VGR: -15 }, 兽耳族: { DEX: 25, FTH: 25, MIND: -15 }, 龙裔: { STR: 20, VGR: 20, MANA: 20 }, 真龙幼体: { STR: 20, VGR: 20, MANA: 20 },
    提夫林: { MANA: 15, MIND: 15, DEX: 10, FTH: -10, VGR: -5 }, 魔族: { MANA: 15, STR: 15, VGR: 15, FTH: -10 }, 海裔: { VGR: 20, FTH: 20, DEX: 10, MIND: -10 }, 半兽人: { STR: 30, VGR: 30, MANA: -15, MIND: -15 } };
  const OATH = [['守序善良', '重视承诺、公正与他人的安危，想用可靠的秩序护住其中的人。'], ['中立善良', '先顾眼前要帮的人，再掂量规矩和立场，愿意找伤人更少的办法。'], ['混乱善良', '珍视自由，也肯替受欺压的人出头，不公的规矩叫你没法袖手。'],
    ['守序中立', '看重职责、程序和守约，分歧照大家认的准则办。'], ['绝对中立', '审慎衡量各方立场，看重自己的处境和局势的平衡，不急着许下阵营。'], ['混乱中立', '照自己的意思挑路，喜欢自由和新鲜事，不愿长久叫一个身份拴住。'],
    ['守序邪恶', '熟悉秩序和权力怎么运转，借规矩替自己扩张，护着对自己有利的位置。'], ['中立邪恶', '自己的好处排在头一位，等得起，也可能为了目的把别人推下去。'], ['混乱邪恶', '放任欲望和暴力，轻视约束和别人的安危，靠人怕你撑住自己的分量。']];
  const SEAL_NAME = { moon: '一道炭痕', strife: '军册的红印', bronze: '碑匠的凿印', maze: '公会的蜡印' };
  /* 初心（★，照 1001 年那一页的冒险初心，一纪一套） */
  const WISH = {
    // 说明不带你我，页上念给玩家听、凭证里当自己的话写，两边都读得通
    moon: [['让诗人唱我的名字', '想有一天，诗人在火边唱到这个名字，唱过一个国，再唱过下一个。'], ['守住一堆火', '有一处地方、一群人，想让他们熬过这一个冬天。'], ['斩一头有名有号的兽', '那头兽的名字人人都知道，想让下一首歌里换上自己的名字。']],
    strife: [['让墙上记住我的名字', '战报上写一回，伤亡册上别写。'], ['守住一段墙', '那一段墙后头有要护着的人。'], ['活着看见这一仗打完', '谁都说这一仗打不完，想亲眼看看。']],
    bronze: [['让碑上刻我的名字', '碑匠只刻做成了的事，想让他自己找上门来。'], ['拉起自己的团', '团名已经想好了，缺的是肯跟着走的人。'], ['查清一件没人肯说的事', '有些事碑上没刻，背面也没人留名，想弄清楚。']],
    maze: [['让公会名录写下我的名字', '名录上一行一个人，想占一行。'], ['下到没人到过的那一层', '深度板最上面那一行，想往下再写一行。'], ['在井口有一扇自己的门', '下井的人都想有个回得去的地方，想先有一个。']],
  };
  const WISH_ALL = [['替一个人做完一件事', '那个人走到半路停下了，想把剩下的路走完。'], ['找回去的路', '故乡还在另一个世界，想找到回去的路。']];

  const F = {};          // 填到一半的东西：回去改、回到书里再进来，都还在
  let BS = null;         // 这一回建档：哪一纪、哪一段、走到第几步
  const PERSIST = ['soul', 'world', 'name', 'sex', 'sexOther', 'age', 'height', 'look', 'oath', 'wish', 'extra', 'art', 'face', 'pcMode', 'entry', 'lifeOwn', 'lifeOn'];          // 跟人走的；初心挑的那一样一纪一套（wishPick），换一纪就清掉
  function resetEra() { for (const k of Object.keys(F)) if (!PERSIST.includes(k) && k !== '_book') delete F[k]; }

  /* ---------- 年代 ---------- */
  const oyear = () => (BS.free ? yearOf(F.year) : yearOf(BS.m.year));
  const periodAt = (y) => { const Ps = BS.E.periods || []; return (y != null && Ps.find((p) => p.from <= y && y <= p.to && p.id !== '1001')) || null; };
  const curP = () => {
    const Ps = BS.E.periods || [], first = Ps[0] || { races: [], skills: [], eras: [] };
    if (BS.free) return periodAt(yearOf(F.year)) || first;
    return Ps.find((p) => (p.eras || []).includes(BS.m.at)) || periodAt(yearOf(BS.m.year)) || first;
  };
  const yText = (y) => (y == null ? '' : (y === 1 && BS.book === 'strife' ? '元年' : y + '年'));
  const ageNum = () => { const n = numOf(F.age); return n == null || n < 1 || n > 9999 ? null : n; };
  const birthYear = () => { const y = oyear(); if (y == null) return null; return y - (ageNum() || 18); };
  const isGoldSoul = () => F.soul === 'native' || F.soul === 'reborn';
  const panelOn = () => BS.book === 'maze' && (oyear() || 0) >= 420;
  const measure = () => (panelOn() ? MEASURE.panel : MEASURE[BS.book]);
  const sheetOf = (P) => (BS.E.sheets && P.sheet && BS.E.sheets[P.sheet]) || BS.E.sheet || {};

  /* ---------- 种族 ---------- */
  const raceOf = (id) => Object.assign({ id }, (BS.E.races || {})[id] || { name: id });
  // 支系照年份给：带 from、to 的只在那几年里有（11-26：月银纪人类的支系跟着年代走，祭火、万兽、诸国、萨尔维斯各是那一段真有的人群）
  const subsNow = (R) => { const y = oyear(); return (R.subs || []).filter((x) => visible(x, y)); };
  /* 选中的那一家（kin）；带 blood 的（人类文化圈底下“家里说不清的老姓”，11-24），凭证种族那一行底下多一行 血：<blood> */
  const kinPicked = () => { if (!F.race || !F.sub || !F.kin) return null; const S = (raceOf(F.race).subs || []).find((x) => x.name === F.sub); return S ? (S.kin || []).find((x) => x.name === F.kin) || null : null; };
  const raceText = () => {
    const R = raceOf(F.race || ''), s = [R.id ? R.name : '', F.sub, F.kin].filter(Boolean).join(' · ');
    return s + (F.race2 ? (s ? '　' : '') + F.race2 : '');
  };
  const statRace = () => {
    const R = F.race ? raceOf(F.race) : null; if (!R) return '人类';
    const S = (R.subs || []).find((x) => x.name === F.sub);
    if (S && S.base && RACE_MOD[S.base]) return S.base;
    if (R.id === 'merfolk') return '海裔';
    if (R.base && RACE_MOD[R.base]) return R.base;
    if (R.id === 'elf') return '高等精灵';
    return '自定义';
  };
  /* 主角立绘的预设：族属照支系或这一族在 1001 年那一套里的叫法（build.json 的 portraits） */
  const pcFolk = () => {
    const Pt = (BUILD && BUILD.portraits) || {}, R = F.race ? raceOf(F.race) : null; if (!R) return '';
    const S = (R.subs || []).find((x) => x.name === F.sub);
    if (S && S.base && (Pt.races || []).includes(S.base)) return S.base;
    const by = (Pt.by_race || {})[R.base || R.name] || (Pt.by_race || {})[R.name];
    return by && by.length ? by[0] : '';
  };
  const pcSexKey = () => (F.sex === '女' ? '女' : '男');
  const pcPreset = (b) => { const f = pcFolk(); return f && b ? (((DATA.pc || {}).pc || {})[f + '·' + pcSexKey() + '·' + b] || null) : null; };
  const okUrl = (u) => /^https?:\/\/\S+$/.test(String(u || '').trim());
  // 立绘预览（11-26）：预设的出那一张艺术照和头像，没画好的写明；贴图的出贴的那两张
  function pcPreviewHTML() {
    if (F.pcMode === 'preset') {
      const f = pcFolk(); if (!f) return '';
      const p = pcPreset(F.build), any = pcBodies().some((b) => pcPreset(b));
      if (!F.build) return `<p class="b2-note b2-pcn">${any ? '挑一种体格，旁边出那一张立绘。' : '这一族、这一支还没有画好的预设立绘。挑了体格照族属和体格的描述写，状态栏里先是一道剪影。'}</p>`;
      if (!p) return `<p class="b2-note b2-pcn">${esc(f)}·${esc(pcSexKey())}·${esc(F.build)}还没有画好的预设立绘，开局照描述写，状态栏里先是一道剪影。</p>`;
      return `<div class="b2-pcv"><img class="a" src="${esc(p.art || p.por)}" alt="${esc(f)}·${esc(pcSexKey())}·${esc(F.build)}的立绘" loading="lazy" referrerpolicy="no-referrer"><div><span class="f fx" style="background-image:url('${esc(p.face)}')"></span><b>${esc(f)} · ${esc(pcSexKey())} · ${esc(F.build)}</b><small>对话框里你开口、面板上那个人，用的都是这一张。衣着跟着这一纪换。</small></div></div>`;
    }
    if (F.pcMode === 'url') {
      const a = okUrl(F.art) ? String(F.art).trim() : '', fc = okUrl(F.face) ? String(F.face).trim() : '';
      if (!a && !fc) return '<p class="b2-note b2-pcn">贴上地址，这里出那一张的样子。</p>';
      return `<div class="b2-pcv own">${a ? `<img class="a" src="${esc(a)}" alt="贴的全身图" referrerpolicy="no-referrer" onerror="this.replaceWith(Object.assign(document.createElement('span'),{className:'a bad',textContent:'这一张取不到'}))">` : '<span class="a bad">还没贴全身图</span>'}<div>${fc || a ? `<img class="f" src="${esc(fc || a)}" alt="" referrerpolicy="no-referrer" onerror="this.remove()">` : ''}<b>自己的图</b><small>${fc ? '头像用贴的那一张' : '头像没贴，从全身图的上半截裁'}。图要一直取得到，换了地址开局也跟着换。</small></div></div>`;
    }
    return '';
  }
  const pcBodies = () => { const Pt = (BUILD && BUILD.portraits) || {}, f = pcFolk(); const b = (Pt.bodies || {})[f] || {}; return b[F.sex === '女' ? '女' : '男'] || []; };

  /* ---------- 金血 ---------- */
  function godsNow() {
    const G = ((DATA.gold && DATA.gold.eras) || {})[BS.book] || { gods: [] }, by = birthYear();
    return (G.gods || []).map((g) => {
      let off = '';
      if (BS.book === 'moon' && g.since != null && by != null && g.since > by) off = g.since + '年才聚成';
      if (BS.book === 'strife' && g.fell != null && by != null && g.fell <= by) off = (+g.fell === 1 ? '元' : g.fell) + '年倒下';
      return Object.assign({}, g, { off });
    });
  }
  const godName = (g) => (g ? (g.tag || '') + g.n : '');
  const goldPicked = () => (F.goldN ? godsNow().find((g) => g.n === F.goldN && !g.off) || null : null);
  const isGold = () => isGoldSoul() && (F.goldN === '*' || !!goldPicked());

  /* ---------- 起点、六维 ---------- */
  const tierKey = () => F.tier || '启源·初识';
  const caps = () => { const cap = tierOf(tierKey())[2], mods = RACE_MOD[statRace()] || {}; const o = {}; for (const [k] of STAT) o[k] = Math.max(1, Math.floor(cap * (100 + (mods[k] || 0)) / 100)); return o; };
  const capSum = (c) => STAT.reduce((s, [k]) => s + c[k], 0);
  const budget = () => { const c = caps(), t = capSum(c); if (F.statMode === 'cap') return t; if (F.statMode === 'roll' && F.rollKey === statKey() && F.rollBudget) return Math.min(Math.floor(t * 0.7), F.rollBudget); return Math.max(6, Math.floor(t * 0.5)); };
  const statKey = () => statRace() + '|' + tierKey();
  function balanced() {
    const c = caps(), B = budget(), t = capSum(c), s = {}; let used = 0; const rem = [];
    for (const [k] of STAT) { const raw = B * c[k] / t, v = Math.max(1, Math.min(c[k], Math.floor(raw))); s[k] = v; used += v; rem.push([raw - v, k]); }
    rem.sort((a, b) => b[0] - a[0]);
    for (let g = 0; used < B && g < 5000; g++) for (const [, k] of rem) { if (used >= B) break; if (s[k] < c[k]) { s[k]++; used++; } }
    return s;
  }
  function rolled() {
    const c = caps(), t = capSum(c), lo = Math.max(6, Math.ceil(t * 0.4)), hi = Math.max(lo, Math.floor(t * 0.7)), B = lo + Math.floor(Math.random() * (hi - lo + 1));
    const s = {}; for (const [k] of STAT) s[k] = 1; let left = B - 6;
    for (let g = 0; left > 0 && g < 50000; g++) { const ks = STAT.map((x) => x[0]).filter((k) => s[k] < c[k]); if (!ks.length) break; const k = ks[Math.floor(Math.random() * ks.length)]; const st = Math.max(1, Math.min(left, Math.floor(Math.random() * Math.max(2, Math.ceil(B / 70))) + 1, c[k] - s[k])); s[k] += st; left -= st; }
    F.rollBudget = B; F.rollKey = statKey(); return s;
  }
  function ensureStats() {
    if (F.statMode === 'later') return;
    const c = caps();
    if (!F.stats || F.statKey !== statKey()) { F.statKey = statKey(); if (F._lean && F.statMode === 'manual' && lifeActive()) F.stats = lean(F._lean); else { if (F.statMode !== 'cap') F.statMode = 'even'; F.stats = F.statMode === 'cap' ? Object.fromEntries(STAT.map(([k]) => [k, c[k]])) : balanced(); } }
    for (const [k] of STAT) F.stats[k] = Math.max(1, Math.min(c[k], +F.stats[k] || 1));
  }
  const statTotal = () => (F.stats ? STAT.reduce((s, [k]) => s + (+F.stats[k] || 0), 0) : 0);

  /* ---------- 命路 ---------- */
  const PATH_GROUP = ['战职', '施法', '圣职', '影系', '射术', '技巧', '规则'];
  function pathState(name) {
    const y = oyear(), b = BS.book;
    if (b === 'strife') {
      const s = (BS.E.paths || {})[name] || {};
      if (s.demon && F.race === 'demon') return { lit: true, tag: '魔族营里早就有', s };
      if (s.from && y != null && s.from <= y) return { lit: true, tag: s.from + '年有了路册', s };
      return { lit: false, tag: s.from ? (s.from > 11034 ? '纪末才对上路册' : '约' + s.from + '年才有名字') : '这一纪还没走成路', s };
    }
    if (b === 'bronze') { const f = (BS.E.path_from || {})[name]; if (f && (y == null || y < f)) return { lit: false, tag: f + '年才走成路', s: {} }; return { lit: true, tag: '立着', s: {} }; }
    return { lit: true, tag: (y != null && y < (BS.E.job_from || 420)) ? '只挑路，不就职' : '可以就职', s: {} };
  }
  const visible = (x, y) => y == null || ((x.from == null || x.from <= y) && (x.to == null || y <= x.to));

  /* ---------- 命星 ----------
     11-24 第二轮（用户：“special，passive，art/active 分三个池子。玩家可以留一个 special，一个 passive，一个 art 或 active”）：
     三个池子 S（Special）、P（Passive）、A（Art、Active），各抽各留一颗。凭证照旧两行，Passive/Special 那一行写进 Passive 和 Special 两颗。
     哪一颗在不在池子里照 stars.json：eras 里这一纪是 null 的不进，from、to 之外的不进（生来的星这一年以前有过的都在、往后才有的不出现）；
     这一纪写成一串版本的（数组，照 from 排），只取这一年已经有的最新那一版，补成新版以后旧版不进池子。
     11-25 落星和候星（用户：“增加一个废卡区，抽过的没选的卡进废卡，重抽不出，玩家可以选择重置。同时每个种类玩家可以取出三张牌放到预选，同时继续抽，
     预选的牌取消预选后进废卡，重置后回到卡池。重置只重置废卡区，不把玩家留下的和预选的带回卡池，重新抽也不动预选和留下的。”）：
     一池里的牌各在一处：星叠（还抽得到的）、台面（这一手，F.drawX.ids）、留下的（F.starX，一颗）、候星（预选，F.drawX.hold，至多三颗）、落星（废卡，F.drawX.gone）。
     再抽：台面上没留、没取走的落进落星，新的一手只从星叠里出；留下的和候星不动。撤下候星、撤下不在台面上的那颗留下的，都落进落星。
     落星归叠（重置）只把落星倒回星叠。换留下的那一颗：原先那颗还在台面上就留在台面上，不在台面上的先压进候星，候星满了放回台面。
     凭证只认 F.starX，这几处一个字不进凭证。做法和界面上的叫法见 第二轮/建档/备注_废卡预选_11-25.md。 */
  const T_RANK = { Unique: 4, Legend: 3, Epic: 2, Rare: 1, Normal: 0 };
  const HOLD_MAX = 3;
  const TRAY = { deck: '星叠', hold: '候星', gone: '落星', reset: '落星归叠' };          // 页面上的叫法（★）：卡池、预选、废卡、重置。要改叫法改这一行
  const STAR_KINDS = ['S', 'P', 'A'];
  const KIND_TYPES = { S: ['Special'], P: ['Passive'], A: ['Art', 'Active'] };
  const KIND_NAME = { S: 'Special', P: 'Passive', A: 'Art · Active' }, KIND_CN = { S: '天赋', P: '体质', A: '手艺' };
  const eraVer = (e, y) => {          // 这一纪那一版：写成数组的照年份取最新的一版
    if (!Array.isArray(e)) return e;
    let got = null;
    for (const v of e) if (v && (y == null ? !got : (v.from == null || v.from <= y) && (v.to == null || y <= v.to))) got = v;
    return got;
  };
  // 长在身子上的星（翅膀、角、鳃、四条胳膊……）只给那几族：need 是 ["demon:夜翼", "beastkin:禽羽", "dragonborn"] 这样，
  // 写族就是这一族都行，写族加支系就只认那一支；还没选种族、选了自定义、选了族还没定支系的，照旧都给看
  const raceFits = (need) => {
    if (!F.race || F.race === 'custom') return true;
    return need.some((t) => { const [r, sb] = String(t).split(':'); return r === F.race && (!sb || !F.sub || sb === F.sub); });
  };
  function starPool(kind) {
    const y = oyear(), S = (DATA.stars && DATA.stars.stars) || [];
    const want = KIND_TYPES[kind] || KIND_TYPES.A;
    const out = [];
    for (const s of S) {
      let e = {};
      if (s.eras) { e = eraVer(s.eras[BS.book], y); if (!e) continue; if (y != null && ((e.from != null && y < e.from) || (e.to != null && y > e.to))) continue; }
      const type = e.type || s.type; if (!want.includes(type)) continue;
      if (s.need && !raceFits(s.need)) continue;
      out.push({ id: String(s.id != null ? s.id : s.name), name: e.name || s.name, base: s.name, type, tier: e.tier || s.tier || 'Rare', desc: e.desc || s.desc || '', note: e.note || '' });
    }
    return out;
  }
  const rates = () => { const r = DATA.stars && DATA.stars.rates; if (r && typeof r === 'object' && typeof r.Legend === 'number') return { U: r.Unique || 2, L: r.Legend || 8, E: r.Epic || 25, pl: r.pity_legend || 5, pu: r.pity_unique || 12 }; return { U: 2, L: 8, E: 25, pl: 5, pu: 12 }; };
  /* 这一池的几处：ids 台面、hold 候星、gone 落星（都是 id）。读的时候把这一年、这一族已经不在池子里的滤掉，几处之间不重 */
  function starZ(kind, pool) {
    const D = F['draw' + kind] = F['draw' + kind] || { n: 0, lp: 0, up: 0, ids: [] };
    if (!Array.isArray(D.ids)) D.ids = []; if (!Array.isArray(D.hold)) D.hold = []; if (!Array.isArray(D.gone)) D.gone = [];
    const ok = new Set((pool || starPool(kind)).map((t) => t.id)), seen = new Set();
    const uniq = (a) => a.filter((id) => ok.has(id) && !seen.has(id) && (seen.add(id), true));
    D.hold = uniq(D.hold).slice(0, HOLD_MAX); D.ids = uniq(D.ids); D.gone = uniq(D.gone);
    const kept = F['star' + kind]; if (kept && kept !== '*') { D.hold = D.hold.filter((id) => id !== kept); D.gone = D.gone.filter((id) => id !== kept); }
    return D;
  }
  /* 星叠：池子里除掉台面、留下的、候星、落星，还抽得到的 */
  function starDeck(kind, pool) {
    pool = pool || starPool(kind);
    const D = starZ(kind, pool), out = new Set(D.ids.concat(D.hold, D.gone)), kept = F['star' + kind];
    if (kept) out.add(kept);
    return pool.filter((t) => !out.has(t.id));
  }
  /* 抽一手。星叠空了就不动台面，回 0（页面上提示让落星归叠）；抽得出就先把台面上没留的落进落星，回抽到几张 */
  function drawStars(kind) {
    const pool = starPool(kind); const R = rates(); const D = starZ(kind, pool);
    const deck = starDeck(kind, pool);
    if (!deck.length) return 0;
    const kept = F['star' + kind];
    for (const id of D.ids) if (id !== kept) D.gone.push(id);
    D.n++; D.lp++; D.up++;
    const used = new Set(), res = [];
    for (let i = 0; i < 10; i++) {
      const left = deck.filter((t) => !used.has(t.id)); if (!left.length) break;
      const x = Math.random() * 100, tg = x < R.U ? 'Unique' : x < R.U + R.L ? 'Legend' : x < R.U + R.L + R.E ? 'Epic' : 'Rare';
      let cs = left.filter((t) => t.tier === tg || (tg === 'Rare' && t.tier === 'Normal'));
      if (!cs.length) cs = left.filter((t) => t.tier === 'Legend'); if (!cs.length) cs = left;
      const p = cs[Math.floor(Math.random() * cs.length)]; res.push(p); used.add(p.id);
    }
    const force = (tier) => { const cs = deck.filter((t) => t.tier === tier && !used.has(t.id)); if (!cs.length || !res.length) return; let lo = 0; res.forEach((t, i) => { if ((T_RANK[t.tier] || 0) < (T_RANK[res[lo].tier] || 0)) lo = i; }); used.delete(res[lo].id); res[lo] = cs[Math.floor(Math.random() * cs.length)]; used.add(res[lo].id); };
    if (D.lp >= R.pl && !res.some((t) => T_RANK[t.tier] >= 3)) force('Legend');
    if (D.up >= R.pu && !res.some((t) => t.tier === 'Unique')) force('Unique');
    if (res.some((t) => T_RANK[t.tier] >= 3)) D.lp = 0;
    if (res.some((t) => t.tier === 'Unique')) D.up = 0;
    res.sort((a, b) => (T_RANK[b.tier] || 0) - (T_RANK[a.tier] || 0) || String(a.type).localeCompare(String(b.type)) || String(a.name).localeCompare(String(b.name), 'zh-Hans-CN'));
    D.ids = res.map((t) => t.id);
    return res.length;
  }
  const drawn = (kind) => { const D = F['draw' + kind]; if (!D) return []; const pool = starPool(kind); return D.ids.map((id) => pool.find((t) => t.id === id)).filter(Boolean); };
  const starsBy = (kind, ids) => { const pool = starPool(kind); return (ids || []).map((id) => pool.find((t) => t.id === id)).filter(Boolean); };
  /* 一颗星眼下在哪：keep 留下的（off 是不在台面上）、hand 台面、hold 候星、gone 落星、deck 星叠 */
  function starAt(kind, id) {
    const D = starZ(kind);
    if (F['star' + kind] === id) return D.ids.includes(id) || id === '*' ? 'keep' : 'keep-off';
    return D.ids.includes(id) ? 'hand' : D.hold.includes(id) ? 'hold' : D.gone.includes(id) ? 'gone' : 'deck';
  }
  /* 留下这一颗。原先那一颗：还在台面上的留在台面上（回 table），不在台面上的先压进候星（hold），候星满了放回台面（back）。从候星里留的，原先那颗正好顶它的空 */
  function starKeep(kind, id) {
    const D = starZ(kind), old = F['star' + kind];
    if (!id || old === id) return '';
    if (id !== '*' && !starPool(kind).some((t) => t.id === id)) return '';
    D.hold = D.hold.filter((x) => x !== id); D.gone = D.gone.filter((x) => x !== id);
    let went = '';
    if (old && old !== '*') {
      if (D.ids.includes(old)) went = 'table';
      else if (D.hold.length < HOLD_MAX) { D.hold.push(old); went = 'hold'; }
      else { D.ids.push(old); went = 'back'; }
    }
    F['star' + kind] = id;
    return went;
  }
  /* 放进候星：从台面取出来压在手边（留下的那一颗也能改放进来）。满了回 full，不动 */
  function starHold(kind, id) {
    const D = starZ(kind);
    if (!id || id === '*' || !starPool(kind).some((t) => t.id === id)) return '';
    if (D.hold.includes(id)) return 'ok';
    if (D.hold.length >= HOLD_MAX) return 'full';
    if (F['star' + kind] === id) F['star' + kind] = '';
    D.ids = D.ids.filter((x) => x !== id); D.gone = D.gone.filter((x) => x !== id);
    D.hold.push(id);
    return 'ok';
  }
  /* 撤下：候着的落进落星；留下的那一颗不留了，还在台面上的留在台面上（回 table），不在台面上的落进落星（回 gone） */
  function starDrop(kind, id) {
    const D = starZ(kind);
    if (!id) return '';
    if (F['star' + kind] === id) { F['star' + kind] = ''; if (id === '*' || D.ids.includes(id)) return 'table'; D.gone.push(id); return 'gone'; }
    if (D.hold.includes(id)) { D.hold = D.hold.filter((x) => x !== id); D.gone.push(id); return 'gone'; }
    return '';
  }
  /* 落星归叠：只把落星倒回星叠，留下的、候星、台面都不动。回倒回去几颗 */
  function starReset(kind) { const D = starZ(kind), n = D.gone.length; D.gone = []; return n; }
  const starOf = (kind) => { const id = F['star' + kind]; if (!id) return null; if (id === '*') return { custom: 1 }; return starPool(kind).find((t) => t.id === id) || null; };

  /* ---------- 赐物 ---------- */
  function giftPool() {
    const y = oyear() || 0, G = DATA.gifts || { gifts: [], relics: [] }, b = BS.book;
    const ok = (av) => !av || (av[b] != null && y >= av[b]);
    return (G.gifts || []).filter((g) => ok(g.avail)).map((g) => Object.assign({ kind: 'gift' }, g))
      .concat((G.relics || []).filter((g) => g.avail && ok(g.avail)).map((g) => Object.assign({ kind: 'relic' }, g)));
  }
  function drawGifts() {
    const a = giftPool().slice(), D = F.drawG = F.drawG || { n: 0, sl: 0, su: 0, ns: [] };
    for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    let out = a.slice(0, 5); D.n++;
    const below = (t) => out.every((g) => (T_RANK[g.r] || 0) < T_RANK[t]);
    if (D.su >= 7 && below('Unique')) { const u = a.find((g) => g.r === 'Unique' && !out.includes(g)); if (u) out[out.length - 1] = u; }
    if (D.sl >= 2 && below('Legend')) { const l = a.find((g) => (T_RANK[g.r] || 0) >= 3 && !out.includes(g)); if (l) out[0] = l; }
    D.sl = out.some((g) => (T_RANK[g.r] || 0) >= 3) ? 0 : D.sl + 1; D.su = out.some((g) => g.r === 'Unique') ? 0 : D.su + 1;
    out.sort((x, z) => (T_RANK[z.r] || 0) - (T_RANK[x.r] || 0)); D.ns = out.map((g) => g.n);
  }
  const giftsDrawn = () => { const D = F.drawG; if (!D) return []; const P = giftPool(); return D.ns.map((n) => P.find((g) => g.n === n)).filter(Boolean); };
  const giftOf = () => (F.giftN && F.giftN !== '-' ? giftPool().find((g) => g.n === F.giftN) || null : null);

  /* ---------- 落在哪 ---------- */
  function mapNow() {
    const M = DATA.maps[BS.book], P = curP(); if (!M || !M.periods) return null;
    const keys = BS.free ? (P.eras || []) : [BS.m.at].concat(P.eras || []);
    const per = M.periods.find((x) => (x.eras || []).some((k) => keys.includes(k))); if (!per) return null;
    const hot = BS.free ? (P.eras || []) : [BS.m.at];
    // 自己报年份的照那一年（11-17）：点只在它头一回出现的那一段起头以后才有，那一年所在的那一段亮着；map_<纪>.json 的 years 是各时代页的起止
    const YR = M.years || {}, y = BS.free ? oyear() : null;
    const born = (p) => y == null || !(p.eras || []).length || (p.eras || []).some((k) => !YR[k] || YR[k][0] <= y);
    const live = (p) => (p.eras || []).some((k) => YR[k] && YR[k][0] <= y && y <= YR[k][1]);
    return { M, per, pins: per.pins.map((p, i) => Object.assign({ i, hot: y != null && Object.keys(YR).length ? live(p) : (p.eras || []).some((k) => hot.includes(k)) }, p)).filter(born) };
  }
  /* 旅印那一格：一纪一样（方向稿第九节第 2 小节第十步） */
  function sealInfo() {
    const y = oyear(), b = BS.book, isk = F.soul === 'isekai';
    if (b === 'moon') return { kind: 'none', note: '月银纪没有旅印。诗人还没唱你的名字，往后唱不唱，看你做了什么。', cred: '无（月银纪没有旅印，诗人还没唱你的名字）' };
    if (b === 'strife') {
      if (y != null && y < 233) return { kind: 'none', note: '233年诸族按剑为盟以前还没有长垒，也没有军册。', cred: '无（233年以前还没有军册）' };
      return { kind: 'roll', note: '军册上一个人三栏：名字、姓或家、族。报不出姓的，书记写他守的那一段墙。' };
    }
    if (b === 'bronze') {
      if (y != null && y < 30) return { kind: 'none', note: '这一纪没有旅印。30年前后才有头一个有名字的团，60年以后几座大段城才有行会。', cred: '无（这一纪没有旅印，30年前后才有头一个有名字的团）' };
      return { kind: 'team', guild: y == null || y >= 60, note: '这一纪没有旅印。拉一个团，团名自己起' + (y == null || y >= 60 ? '。行会的档次看挂号的年头、交过几回差、谁替你作保，跟本事不相干。' : '。60年以后才有行会。') };
    }
    if (y != null && y < 3) return { kind: 'none', note: '3年霜降月以前还没有公会，活钉在水门段城西门门洞的号墙上。', cred: '无（3年霜降月以前还没有公会）' };
    if (y != null && y < 420) return { kind: 'grade', gua: y >= 7, stone: y < 20, note: '旅印是' + (y < 20 ? '塌门白石刻的' : '山铜铸的，外圈一杆公会秤') + '，不分阶。公会量人看档次，档次跟本事不相干' + (y >= 7 ? '。从前没在哪家行会挂过号的人，按印要有人担保。' : '。') };
    return { kind: 'rank', isk, note: isk ? '身穿的人落地时没有旅印，开局先去公会登记、觉醒面板。' : '420年起旅印分七阶，照面板上的本事分。' };
  }
  const RANKS = ['无印', '见习', '营火', '风路', '月桂', '界钥', '星图', '圣歌'];
  const GRADES = ['还没入会', '最低一档', '低档', '中档', '高档'];
  const TEAM_GRADES = ['没挂号', '最低一档', '低档', '中档', '高档'];
  function rankDefault() {
    if (F.soul === 'isekai') return '无印';
    const k = tierKey(); if (k === '启源·初识') return '无印';
    const m = { '启源·凝华': '见习', '启源·临界': '营火', '共鸣·寻音': '营火', '共鸣·织理': '风路', '共鸣·破障': '风路' }; if (m[k]) return m[k];
    return { 灵格: '月桂', 极境: '界钥', 英雄: '星图', 传奇: '圣歌' }[k.split('·')[0]] || '见习';
  }

  /* ---------- 开始（11-24 建档升级） ----------
     规矩、资料和凭证照旧（上头那一串、下面 credential() 一个字没动），改的是画面和一条新路：
     开头若娜瓦问一句，自己一项一项定（直接构筑，十一步，一步一种样子），还是让她翻你的前半生（八章，data/life.json，一纪几段，选完自动填好十一步，最后能回去改哪一步）。
     建档这一段不出手（11-24 用户看了说手不要了）：牌自己滑进来，选中的那一张自己亮起来浮一下，骰子自己滚出来，换步的时候这一步的牌自己拢起来收走；她每一步那一两句话照留。
     右边一张这一纪的身份牌边建边长（月银纪火歌里的名字木牌、纷争纪军册的一页、山铜纪佣兵碑上那一格、迷宫纪旅印、此刻黄铜那一版）。
     铸印：那一纪的印自己压下去，身份牌收成一本薄书飞上书架（Library.addPlayerBook），确认页是那一本的第一页。接续旅印也在这里（旧 1001 页挪过来的）。
     图在 assets/bx/（第二轮/建档/prep_art.py 出，data/bx_art.json 记着有哪几张、手里那张牌在图上哪里），没到的拿画的顶着。 */
  const RMo = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
  const T = (ms) => new Promise((r) => setTimeout(r, RMo() ? 0 : ms));
  const isM = () => innerWidth <= 860;
  const visOf = (b) => (b === 'now' ? 'now' : b);
  const BXA = (n) => A('assets/bx/' + n + '.webp');
  const hasArt = (n) => !!(DATA.art && (DATA.art.have || []).includes(n));
  const artUrl = (n) => { try { return new URL(BXA(n), document.baseURI).href; } catch (e) { return BXA(n); } };
  const RACE_ART = { human: 'race_human', elf: 'race_highelf', dwarf: 'race_dwarf', halfling: 'race_halfling', beastkin: 'race_beastkin', halforc: 'race_halforc', dragonborn: 'race_dragonborn', truedragon: 'race_truedragon', demon: 'race_demon', tiefling: 'race_tiefling', merfolk: 'race_merfolk', custom: 'race_custom' };
  const PATH_KEY = { 摧锋: 'cuifeng', 沸血: 'feixue', 熔心: 'rongxin', 洪流: 'hongliu', 真理: 'zhenli', 悲悯: 'beimin', 断罪: 'duanzui', 无形: 'wuxing', 绝影: 'jueying', 诡刃: 'guiren', 惊弦: 'jingxian', 行猎: 'xinglie',
    魔梭: 'mosuo', 渊垒: 'yuanlei', 死舞: 'siwu', 阵剑: 'zhenjian', 极光: 'jiguang', 天平: 'tianping', 鼎镬: 'dinghuo', 千锤: 'qianchui', 枯荣: 'kurong', 铁律: 'tielv', 解构: 'jiegou', '*': 'custom' };
  const OATH_KEY = { 守序善良: 'oath_lg', 中立善良: 'oath_ng', 混乱善良: 'oath_cg', 守序中立: 'oath_ln', 绝对中立: 'oath_tn', 混乱中立: 'oath_cn', 守序邪恶: 'oath_le', 中立邪恶: 'oath_ne', 混乱邪恶: 'oath_ce' };
  // 誓心牌上那一句誓词（★，一张一句，照九种誓心的说明写，第一人称，不加不减数值）
  const VOW = { 守序善良: '我许下的约，替身后的人守到最后一个。', 中立善良: '路上倒下的人，我先扶起来，再问规矩。', 混乱善良: '锁要是拴着无辜的人，我就把锁砸开。',
    守序中立: '账要清，约要守，谁来都照这一本册子办。', 绝对中立: '我站在秤的正中，两头都看清了再说话。', 混乱中立: '风往哪边吹，我往哪边走，谁也别想拴住我。',
    守序邪恶: '规矩是梯子，我踩着它往上走。', 中立邪恶: '我等得起，等到该推的那个人自己站到崖边。', 混乱邪恶: '他们怕我，这就够了。' };
  const ID_TITLE = { moon: ['火歌里的名字', '一块木牌，火边的人唱到它'], strife: ['军册的一页', '名字、姓或家、族，三栏'], bronze: ['段城的兵册', '佣兵碑上刻名的那一格'], maze: ['旅印', '公会挂号册上按的那一枚'], now: ['旅印', '黄铜铸的那一版'] };
  const PAPER = { moon: 'hide', strife: 'report', bronze: 'rubbing', maze: 'form', now: 'print' };
  const TIER_SAY = { Unique: ['这一颗，世上同一时刻只亮在一个人身上。', '你运气倒好。别急着高兴，它要的也多。'], Legend: ['歌里有人带过这一颗。', '留不留，看你。'], Epic: ['还算像样，撑得起一路的本事。', '再往上的，就看你肯不肯再抽。'], Rare: ['都是寻常的星。', '寻常的也能走很远，只是走得辛苦些。'] };
  /* 她每一步说的话（★，从容、有一点促狭、会催） */
  const LINES = {
    gate: { in: ['要不要我先翻一翻你的前半生？', '翻的话多几章，后面几步我照着先替你填上，到了那一步你再改。'], idle: ['翻不翻，十一步都一样走到门口。别站在门槛上想一整夜。'] },
    // 11-26 并成一条路以后（★）：翻前半生在胎骨之后；后面几步是照前半生先填的
    lifeOn: ['那就翻。胎骨定了，我从你降生那一页念起。'], lifeOff: ['不翻也好。前半生留给往后的路。'], pre: ['这一页我照你的前半生先填上了。', '不合意就改，改了算你的。'],
    1: { in: ['生者自有去处，亡魂也有归程。', '你既已来到这里，便将来历说清。三张牌，挑一张给我看。'], idle: ['手停在牌上不动，牌也替你选不了。', '挑错了也不要紧，再挑一张就是。'] },
    2: { in: ['写下你的名字。', '年龄也说清楚。别只报一个看着顺眼的数。'], idle: ['空着的地方我会替你补，名字可替你补不了。'] },
    3: { in: ['这一纪的各族都摆在这里了。', '挑一张翻过来，看你生在哪一支。'], idle: ['看了这么久，是在等哪一张自己跳起来？', '牌都摆在这里了，我可不会再多给一张。'], done: ['这副骨头，往后你得带着走很久。', '选好了就别回头嫌它。'] },
    4: { in: ['你的血醒着。', '挑一位，或者谁也不挑。凡人的血也走得很远。'], no: ['你是整个人掉进来的，血里没有这一纪的神。', '这一页，我替你翻过去。'], idle: ['神也会等，不过祂们不爱等太久。'] },
    5: { in: ['从哪一级起步，你自己说。', '往高处挑也行，只是伟业要配得上，最后那一页写清楚。'], idle: ['低一点的台阶，走起来也有走的好处。'] },
    6: { in: ['六样本钱，你自己分。', '拖一角，那一样就长。不想算就交给我，我掷骰子比你快。'], roll: ['掷了。', '点数是天给的，怎么用是你的事。'], idle: ['分得匀不匀，路上自会告诉你。'] },
    7: { in: ['二十三条路，摆成一圈。', '挑一条走。灰着的那几条，这一年还没有名字。'], moon: ['这一纪没有命路。', '先认兵器，再说是哪一家教的。'], idle: ['路不会自己走到你脚下来。'] },
    8: { in: ['这三叠是星。我替你抽，你来留。', '天赋留一颗，体质留一颗，手艺留一颗。'], redraw: ['还要？星不会越抽越亮，是你越抽越贪。', '好吧，再给你十张。没留的那几颗，落下去就不再出了。'], idle: ['抽了不留，牌桌上可没有这个规矩。'],
      // 11-25 落星和候星（★）
      hold: ['先替你压在手边。', '候星只压得下三颗，再抽我不动它。'], full: ['候星只压得下三颗。', '撤一颗下去，再来取这一颗。'], drop: ['撤下去了。', '它落进落星，叠里不再出它。'], free: ['那就先不留。', '它还在台面上，再抽就落下去了。'],
      reset: ['落星都归叠了。', '留下的和候着的，我一颗没动。'], reset0: ['落星里一颗也没有，无星可归。'], dry: ['这一叠抽空了。', '让落星归叠，才有牌再抽。'], dry0: ['这一叠的星都在你手边了。', '没有可抽的，就从这几颗里留。'],
      swapHold: '原先那一颗，替你压进候星了。', swapBack: '候星满了，原先那一颗放回台面了。', swapTable: '原先那一颗还在台面上。' },
    9: { in: ['誓心不拦你做什么，只记你待人行事的样子。', '再把册子上那几栏填了。'], idle: ['不挑誓心也行，我照你往后做的事替你记。'] },
    10: { in: ['我把你放在哪儿，你就从哪儿开始。', '再说一句，你为什么上路。'], free: ['你要落在哪一处？', '点一处，我替你按一枚印。'], idle: ['地图不会变大，你看得再久也一样。'] },
    11: { in: ['名字按进印里，就改不回去了。', '想好了，就按下去。'], idle: ['手按在印上，用不着发抖。'],
      // 11-26 入局：先听前半生，还是径直推门（★，一样一句）
      life: ['那就先听我把你的前半生念完，再推门。'], open: ['不听也罢。门推开，便是第一幕。'] },
    // 11-26 前半生“自己写”（★）：哪三张都不像你，这一段你自己说
    own: { in: ['那这一段你自己说给我听。', '记得什么说什么，我照这一纪的规矩记，不替你添。'], off: ['那就还是照牌上的念。', '你写的我先夹在这一页里，想用再翻出来。'],
      over: ['写得太长了，这一页记不下。', '经历二百字，收获一百字，删一删再给我。'], two: ['偏向只记两样。', '先撤一样，再挑这一样。'] },
  };

  let BX = { busy: false, lineSeq: 0, idleT: 0, idleN: 0, revealed: {}, deal: true };
  async function startBuild(m) {
    pend = m;
    try { await loadAll(m.book); } catch (e) {}
    const D = BUILD || { format: {}, eras: {} }, E = (D.eras || {})[m.book] || { name: ERA[m.book], sheet: {}, periods: [], races: {} };
    if (F._book !== m.book) { resetEra(); F._book = m.book; F._max = 1; F._step = 1; }
    const key = m.book + '|' + m.at + '|' + (m.line || '');
    if (F._key !== key) { if (F._key) F._step = Math.min(F._step || 1, 2); F._key = key; F.free = null; delete F.placeI; delete F.place; F._sealed = 0; }          // 同一纪换了一条主线进来：从睁眼之前那一步看起，年份换了
    let free = F.free != null ? F.free : (m.at === 'free' || !m.line);
    if (free && !E.free) free = false;
    BS = { m, D, E, book: m.book, vis: m.at === '1001' || m.site ? 'now' : visOf(m.book), era: E.name || ERA[m.book], FR: E.free || null, free, step: F._step || 1, focus: null, mode: 'step', pool: 'S' };
    BX.revealed = {}; BX.minting = false; BX.busy = false;
    if (!BX.pre) { BX.pre = 1; const want = (DATA.art && DATA.art.have || []).filter((n) => /^(soul_|race_|star_|oath_|id_|tier_)/.test(n));          // 先把前几步要翻的牌面载上，翻到的时候不空着
      want.forEach((n, i) => setTimeout(() => { const im = new Image(); im.decoding = 'async'; im.src = artUrl(n); }, i * 40)); }
    buildEl.innerHTML = shellHTML();
    wire();
    bookHide(true); tableOn(false);          // 书先藏着（不拆，回去改的时候还在原处）；这一页自己铺底，牌桌不用画
    show(buildEl);
    await T(60);
    if (!F._route) gate();
    else if (F._route === 'life' && F._life && lifeActive()) lifeGo(F._life.i || 0, true);
    else go(Math.min(F._step || 1, F._max || 1), true);
  }
  const absA = (p) => { try { return new URL(A(p), document.baseURI).href; } catch (e) { return A(p); } };          // 样式变量里的 url() 照样式表的目录找，先换成整的地址
  const SIL = '<svg viewBox="0 0 100 130" aria-hidden="true"><path d="M50 6c11 0 19 9 19 21s-8 22-19 22-19-10-19-22S39 6 50 6zM22 58c8-6 17-8 28-8s20 2 28 8c8 7 12 22 13 40l2 32H7l2-32c1-18 5-33 13-40z"/></svg>';
  function shellHTML() {
    const k = K_OF[BS.book] != null ? K_OF[BS.book] : 3, v = BS.vis, it = ID_TITLE[v] || ID_TITLE.maze;
    const idImg = hasArt('id_' + v) ? artUrl('id_' + v) : (hasArt('id_bronze') ? artUrl('id_bronze') : '');
    return `<div class="bx" data-era="${v}" style="--back:url('${absA('assets/back_' + k + '.webp')}');--bb:url('${absA('assets/bb_' + k + '.webp')}');--sback:url('${hasArt('star_back') ? artUrl('star_back') : absA('assets/bb_' + k + '.webp')}')">
<div class="bx-bg" style="background-image:url('${absA('assets/era_' + k + '.webp')}')"></div><div class="bx-mat"></div><div class="bx-vig"></div>
<header class="bx-top"><div class="bx-tt"><small>建 档</small><h1></h1><em></em><span class="bx-pg" aria-hidden="true"><b></b><i><s></s></i></span></div><button type="button" class="bx-mn" data-a="menu" aria-label="步子和别的路" aria-expanded="false"><i></i><i></i><i></i></button><div class="bx-mp"><p class="bx-mi"></p><ol class="bx-steps" aria-label="建档的步子"></ol><div class="bx-tb"><button type="button" class="bx-rt" data-a="route" hidden></button><button type="button" class="bx-out" data-a="out">${frame ? '回到书里' : '回到牌桌'}</button></div></div></header>
<div class="bx-say" aria-live="polite" data-a="say"><p></p><p></p></div>
<main class="bx-stage" tabindex="-1"><div class="bx-body"></div></main><div class="bx-lay"></div>
<section class="bx-detail" aria-live="polite" hidden><button type="button" class="bx-dx" data-a="unfocus" aria-label="收起">收起</button><div class="bx-din"></div><div class="bx-dbtn"><button type="button" class="bt" data-a="unfocus">再看看</button><button type="button" class="bt pri" data-a="next"></button></div></section>
<div class="bx-dim" data-a="unfocus"></div>
<nav class="bx-ctl"><button type="button" class="bt" data-a="prev">上一步</button><button type="button" class="bt pri" data-a="next"></button></nav>
<aside class="bx-aside" aria-label="这个人"><button type="button" class="bx-ax" data-a="idclose">收起</button><div class="bx-lb"><b>${esc(it[0])}</b>${esc(it[1])}</div>
<div class="bx-id" data-era="${v}"><div class="fr"${idImg ? ` style="background-image:url('${idImg}')"` : ''}></div><div class="niche"><img alt="" referrerpolicy="no-referrer">${SIL}</div>
<div class="rows"><div class="nm"></div><div class="ln l1"></div><div class="ln l2"></div><div class="sx"></div><div class="st sS"></div><div class="st sP"></div><div class="st sA"></div></div><div class="mark" aria-hidden="true"></div></div>
<div class="bx-hint">选什么，这一格就写什么。</div></aside>
<button type="button" class="bx-idm" data-a="idopen" aria-label="看这个人"><span class="th"><img alt="" referrerpolicy="no-referrer">${SIL}</span><span class="tx"><b></b><i></i></span><span class="ch"><em class="sS"></em><em class="sP"></em><em class="sA"></em></span></button>
<div class="bx-flash" aria-hidden="true"></div>
</div>`;
  }
  const $b = (s) => buildEl.querySelector(s);
  const $$b = (s) => [...buildEl.querySelectorAll(s)];
  const root = () => buildEl.querySelector('.bx');
  const bodyEl = () => buildEl.querySelector('.bx-body');

  /* ---------- 她的话 ---------- */
  async function speak(lines) {
    const my = ++BX.lineSeq, box = $b('.bx-say'); if (!box) return;
    const ps = box.querySelectorAll('p');
    ps.forEach((p) => p.classList.remove('on'));
    await T(240); if (my !== BX.lineSeq) return;
    ps[0].textContent = (lines && lines[0]) || ''; ps[1].textContent = (lines && lines[1]) || '';
    box.classList.remove('open'); box.classList.toggle('more', !!ps[1].textContent);          // 手机上只露头一句，有第二句的点开看
    ps[0].classList.toggle('on', !!ps[0].textContent); await T(420); if (my !== BX.lineSeq) return;
    if (ps[1].textContent) ps[1].classList.add('on');
  }
  function poke() {
    clearTimeout(BX.idleT);
    if (buildEl.hidden) return;
    BX.idleT = setTimeout(() => {
      if (buildEl.hidden || BX.busy) return;
      const L = BS && (BS.mode === 'gate' ? LINES.gate : BS.mode === 'life' ? null : LINES[BS.step]);
      if (L && L.idle) speak([L.idle[BX.idleN++ % L.idle.length]]);
    }, 14000);
  }

  /* ---------- 选中的那一张自己亮起来、浮一下（11-24 用户看了说手不要了：建档这一段不出手，牌自己滑进来、自己翻、骰子自己滚、印自己压下去） ---------- */
  function tapGlow(el) { if (!el || RMo()) return; el.classList.remove('bx-tapped'); void el.offsetWidth; el.classList.add('bx-tapped'); }

  /* ---------- 牌的进和出：一叠从台面上沿滑进来，散到各自的位置；换步的时候拢起来、往上收走 ---------- */
  async function dealIn(els, opt = {}) {
    els = els.filter((e) => e && e.getBoundingClientRect().width);
    if (!els.length || RMo() || !BX.deal) return;
    BX.busy = true;
    if (BS) { const sk = BS.mode + ':' + BS.step; BS.dealt = BS.dealt || new Set(); if (!BS.dealt.has(sk)) { BS.dealt.add(sk); (window.__sfx || (() => {}))('bcard'); } }          // 建档：牌滑进来（11-26 夜改：这一回建档里每一步只在头一回进来时响）
    const st = $b('.bx-stage').getBoundingClientRect();
    const o = opt.from || { x: st.left + st.width / 2, y: st.top - 40 };
    const rs = els.map((e) => e.getBoundingClientRect());
    els.forEach((e, i) => { const r = rs[i]; e.style.transition = 'none'; e.style.transform = `translate(${o.x - (r.left + r.width / 2)}px,${o.y - (r.top + r.height / 2)}px) rotate(${(i % 3) - 1}deg) scale(.82)`; e.style.opacity = '0'; });
    void document.body.offsetWidth;
    const stag = opt.stagger != null ? opt.stagger : Math.max(18, Math.min(70, 700 / els.length));
    els.forEach((e, i) => setTimeout(() => { e.style.transition = 'transform .62s cubic-bezier(.2,.75,.2,1),opacity .35s'; e.style.opacity = '1'; e.style.transform = ''; }, i * stag));
    await T(els.length * stag + 660);
    els.forEach((e) => { e.style.transition = ''; e.style.transform = ''; e.style.opacity = ''; });
    BX.busy = false;
  }
  async function sweepOut() {
    const els = $$b('.bx-body [data-deal]').filter((e) => { const r = e.getBoundingClientRect(); return r.width && r.bottom > 0 && r.top < innerHeight; });
    if (!els.length || RMo()) return;
    BX.busy = true;
    const st = $b('.bx-stage').getBoundingClientRect(), cx = st.left + st.width / 2, cy = st.top + Math.min(st.height * 0.42, 300);
    const rs = els.map((e) => e.getBoundingClientRect());
    els.forEach((e, i) => { const r = rs[i]; e.style.transition = 'transform .42s cubic-bezier(.4,.1,.3,1),opacity .4s'; e.style.transform = `translate(${cx - (r.left + r.width / 2)}px,${cy - (r.top + r.height / 2)}px) rotate(${(i % 5) - 2}deg) scale(.86)`; });
    await T(440);
    els.forEach((e, i) => { const r = rs[i]; e.style.transition = 'transform .45s cubic-bezier(.5,0,.8,.4),opacity .45s'; e.style.transform = `translate(${cx - (r.left + r.width / 2)}px,${-r.top - r.height - 120}px) scale(.86)`; e.style.opacity = '0'; });
    await T(420);
    BX.busy = false;
  }


  /* ---------- 画一步 ---------- */
  async function go(n, first) {
    n = Math.max(1, Math.min(11, n));
    if (BX.busy) return;
    const enter = first || BS.mode !== 'step' || n !== BS.step;
    if (BS.mode === 'step' && BS.step === 11 && n !== 11) unMint();
    if (!first && enter) await sweepOut();
    BS.mode = 'step'; F._route = 'direct'; BS.lift = null;
    BS.step = n; F._step = n; F._max = Math.max(F._max || 1, n); BS.focus = null;
    validate();
    renderRail(); renderStep(enter); renderSide(); idUpdate();
    const st = $b('.bx-stage'); if (st && enter) st.scrollTop = 0;
    if (enter) {
      const L = LINES[n];
      speak(n === 4 && !isGoldSoul() ? L.no : n === 7 && BS.book === 'moon' ? L.moon : n === 10 && BS.free ? L.free : preOn(n) ? LINES.pre : L.in);
      BX.idleN = 0; poke();
    }
  }
  function renderRail() {
    const P = curP(), y = oyear();
    $b('.bx-tt h1').innerHTML = `${esc(BS.era)}${P && P.name ? '<span>' + esc(P.name) + '</span>' : ''}`;
    $b('.bx-tt em').textContent = (y != null ? yText(y) : '还没报年份') + (BS.free ? ' · 自己报的年份' : BS.m.site ? ' · ' + BS.m.site : (BS.m.line ? ' · ' + String(BS.m.line).split('·').pop() : ''));
    const rt = $b('.bx-rt');
    if (BS.mode === 'gate') {
      $b('.bx-steps').innerHTML = ''; rt.hidden = true;
    } else {
      const done = F._done || [], li = BS.mode === 'life' && F._life ? F._life.i : -1, lmax = F._life ? (F._life.left ? 99 : F._life.max || 0) : -1;
      $b('.bx-steps').innerHTML = railItems().map((it) => {
        if (it.life != null) {
          const j = it.life, on = j <= lmax || (j === 0 && done.includes(3));
          return `<li class="lf"><button type="button" class="bx-st lf ${j === li ? 'cur' : (F._life && (F._life.left || j < (F._life.max || 0))) ? 'done' : ''}" data-a="lifeat" data-v="${j}"${on ? '' : ' disabled'} title="前半生 · ${esc(LIFE_NAME[it.k])}"${j === li ? ' aria-current="step"' : ''}><i></i><span>${esc(LIFE_NAME[it.k])}</span></button></li>`;
        }
        const n = it.n, skip = n === 4 && !isGoldSoul(), cur = BS.mode === 'step' && n === BS.step;
        const cls = cur ? 'cur' : (done.includes(n) ? 'done' : (n <= (F._max || 1) ? 'seen' : ''));
        return `<li><button type="button" class="bx-st ${cls}${skip ? ' skip' : ''}" data-a="step" data-v="${n}"${n > (F._max || 1) ? ' disabled' : ''} title="第${NUM[n]}步 ${esc(stepName(n))}${skip ? '，身穿的人没有这一步' : ''}"${cur ? ' aria-current="step"' : ''}><i></i><span>${esc(stepName(n))}</span></button></li>`;
      }).join('');
      rt.hidden = F.soul === 'isekai'; rt.textContent = lifeActive() ? '不翻前半生了' : '翻我的前半生';
    }
    // 手机上顶上只留一条：纪元、年份和走到第几步（一道细进度），步子和两枚钮收进“…”
    const pg = $b('.bx-pg'), ytx = y != null ? yText(y) : '';
    if (pg) {
      let t = '', f = 0;
      const R = railItems(), at = R.findIndex((it) => (BS.mode === 'life' ? it.life === (F._life ? F._life.i : 0) : it.n === BS.step));
      if (BS.mode === 'life') { const L = lifeList(), i = F._life ? F._life.i : 0; t = `前半生 ${i + 1}/${L.length} · ${LIFE_NAME[L[i]] || ''}`; f = (at + 1) / R.length; }
      else if (BS.mode === 'gate') t = '翻不翻前半生';
      else { t = `${BS.step}/11 · ${stepName(BS.step)}`; f = (at + 1) / R.length; }
      pg.querySelector('b').textContent = (ytx ? ytx + ' · ' : '') + t;
      pg.querySelector('s').style.width = Math.round(f * 100) + '%';
    }
    const mi = $b('.bx-mi'); if (mi) mi.textContent = $b('.bx-tt em').textContent;
  }
  const stepName = (n) => (n === 7 && BS.book === 'moon' ? '兵器与技艺' : n === 4 ? '金血' : n === 10 && !BS.free ? '初心与旅印' : STEPS[n - 1]);          // 拿车票进来的，落在哪车票定了，第十步只剩初心和旅印
  const railItems = () => { const out = []; for (let n = 1; n <= 11; n++) { out.push({ n }); if (n === 3 && lifeActive()) lifeList().forEach((k, j) => out.push({ life: j, k })); } return out; };
  const preOn = (n) => lifeActive() && F._life && F._life.left && !!(F._pre || {})[n];
  function renderStep(enter) {
    const r = STEP[BS.step]();
    const body = bodyEl();
    body.className = 'bx-body s' + BS.step;
    body.innerHTML = `<header class="bx-hd"><small>第${NUM[BS.step]}步${r.small ? '　' + esc(r.small) : ''}</small><h2>${esc(r.h1 || stepName(BS.step))}</h2>${r.p ? `<p data-a="hdp">${r.p}</p>` : ''}${preOn(BS.step) ? `<p class="b2-pre"><button type="button" data-a="lifeat" data-v="0">照你的前半生填的</button>${esc(PRE_NOTE[BS.step] || '')}，不合意就在这一步改。</p>` : ''}</header>` + (r.body || '');
    BS.primary = r.primary || '下一步';
    ctlSync();
    const bp = $b('.bx-ctl [data-a="prev"]'); if (bp) { bp.disabled = false; bp.textContent = BS.step === 1 ? '换一条路' : '上一步'; }
    $b('.bx-flash') && $b('.bx-flash').classList.remove('go');
    const lay = $b('.bx-lay'); if (lay) lay.innerHTML = BS.step === 3 ? raceFocusHTML() : '';
    if (r.after) r.after(enter);
    if (enter) dealIn($$b('.bx-body [data-deal]'), typeof r.deal === 'function' ? r.deal() : (r.deal || {}));
  }
  const PRE_NOTE = { 5: '起点照离家那一章', 6: '六维照几章的收获往两头偏', 9: '誓心、出身那几栏、本事照几章选的', 10: '初心照离家那一章' };
  function ctlSync() {
    const f = BS.focus && SIDE[BS.focus.k] ? SIDE[BS.focus.k](BS.focus.v) : null;
    for (const nb of $$b('.bx-ctl [data-a="next"], .bx-dbtn [data-a="next"]')) nb.textContent = f && f.primary ? f.primary : BS.primary;
  }
  function renderSide() {
    const r = BS.mode !== 'gate' && BS.focus && SIDE[BS.focus.k] ? SIDE[BS.focus.k](BS.focus.v) : null;
    const d = $b('.bx-detail'), x = root();
    if (!d) return;
    if (r) { d.querySelector('.bx-din').innerHTML = r.html; d.hidden = false; requestAnimationFrame(() => d.classList.add('on')); if (r.after) r.after(); }
    else { d.classList.remove('on'); d.hidden = true; }
    x.classList.toggle('focused', !!r);
    ctlSync();
  }
  function focusOn(k, v, open) {
    BS.focus = { k, v }; renderSide();
    if (open !== false && isM()) root().classList.add('sheet');
    const s = $b('.bx-din'); if (s) s.scrollTop = 0;
  }
  function unfocus() { BS.focus = null; root().classList.remove('sheet'); renderSide(); const fo = $b('.bx-focus'); if (fo) { fo.remove(); $$b('.bx-race.lifted').forEach((e) => e.classList.remove('lifted')); } }
  /* 年份一变（自己报年份）、族一换，后面几步里已经挑了的东西可能这一年还没有：挑掉 */
  function validate() {
    const P = curP(), y = oyear();
    if (F.race && !(P.races || []).includes(F.race)) { F.race = ''; F.sub = ''; F.kin = ''; }
    if (F.race) { const R = raceOf(F.race), subs = subsNow(R); if (F.sub && !subs.some((x) => x.name === F.sub)) { F.sub = ''; F.kin = ''; } }
    if (F.kin) { const K = kinPicked(); if (!K || !visible(K, y)) F.kin = ''; }
    if (F.goldN && F.goldN !== '-' && F.goldN !== '*' && !goldPicked()) F.goldN = '';
    if (F.tier === '传奇·凡极' && !(BS.book === 'maze' && (y || 0) >= 318)) F.tier = '';
    if (BS.book === 'moon') for (const [a, src] of [['weapon', 'weapons'], ['armor', 'weapons'], ['marts', 'arts'], ['school', 'schools']]) { if (F[a] && !(BS.E[src] || []).some((x) => x.n === F[a] && visible(x, y))) F[a] = ''; }
    if (F.starP && F.starP !== '*' && !starPool('P').some((t) => t.id === F.starP) && starPool('S').some((t) => t.id === F.starP)) { if (!F.starS) F.starS = F.starP; F.starP = ''; }          // 两叠那时候留在生来的那一叠里的 Special 挪到自己的池子
    for (const k of STAR_KINDS) if (F['star' + k] && F['star' + k] !== '*' && !starPool(k).some((t) => t.id === F['star' + k])) F['star' + k] = '';
    if (F.giftN && F.giftN !== '-' && !giftPool().some((g) => g.n === F.giftN)) F.giftN = '';
    const MP = mapNow(), mk = MP ? MP.per.id : ''; if (F.placeMap !== mk) { F.placeMap = mk; F.placeI = null; }
    if (F.skills) { const ok = (P.skills || []).map((s) => (typeof s === 'string' ? { s } : s)).filter((s) => visible(s, y)).map((s) => s.s); F.skills = F.skills.filter((s) => ok.includes(s)); }
  }
  const byText = (by) => (by == null ? '' : by < 1 ? ({ moon: '月银纪以前', strife: '月银纪末年', bronze: '纷争纪末年', maze: '山铜纪末年' }[BS.book]) : (by < 2 && BS.book !== 'moon' && BS.book !== 'strife' ? { bronze: '纷争纪末年', maze: '山铜纪末年' }[BS.book] : yText(by)));
  function pathShort() {
    if (BS.book === 'moon') return [F.weapon, F.style].filter(Boolean).join('·');
    if (F.path === '*') return '自定义命路';
    return F.path || '';
  }

  /* ---------- 右边那张身份牌：边建边长 ---------- */
  function idUpdate() {
    const x = root(); if (!x || !BS) return;
    const R = F.race ? raceOf(F.race) : null, soul = F.soul ? SOUL[F.soul].n.split(' · ')[0] : '';
    const l1 = [soul || '魂未定', R ? raceText() : '胎骨未定'].join(' · ');
    const l2 = [tierKey(), pathShort() || (BS.book === 'moon' ? '兵器未认' : '路还没定')].join(' · ');
    const name = String(F.name || '').trim() || '未署名';
    const set = (sel, t, empty) => { for (const e of $$b(sel)) { e.textContent = t; e.classList.toggle('e', !!empty); } };
    set('.bx-id .nm', name, !F.name); set('.bx-idm .tx b', name, !F.name);
    set('.bx-id .l1', l1, !F.soul && !R); set('.bx-id .l2', l2, !F.tier && !pathShort()); set('.bx-idm .tx i', l1, !F.soul && !R);
    const sx = $b('.bx-id .sx');
    if (sx) sx.innerHTML = F.stats && F.statMode !== 'later' ? STAT.map(([k]) => `<span><i>${k}</i>${F.stats[k]}</span>`).join('') : '<span class="e">六维未分</span>';
    for (const k of STAR_KINDS) {
      const s = starOf(k), lab = KIND_CN[k];
      const t = s ? (s.custom ? (F['sc' + k + 'n'] || '自定义') : s.name) : '';
      for (const e of $$b('.bx-id .s' + k)) { e.textContent = s ? lab + ' · ' + t + (s.tier ? ' · ' + s.tier : '') : lab + ' · 未定'; e.classList.toggle('e', !s); e.dataset.t = s && s.tier ? s.tier : ''; }
      for (const e of $$b('.bx-idm .s' + k)) { e.textContent = s ? t : lab + ' 未定'; e.classList.toggle('e', !s); e.dataset.t = s && s.tier ? s.tier : ''; }
    }
    // 龛里：贴了自己的图用自己的，挑了族用那一族的牌面，都没有是剪影
    let art = '', own = false;
    if (F.pcMode === 'url' && /^https?:\/\//.test(String(F.face || F.art || ''))) { art = String(F.face || F.art); own = true; }
    else if (F.pcMode === 'preset' && pcPreset(F.build)) { art = pcPreset(F.build).art || pcPreset(F.build).por; own = true; }          // 头像那一张是九格表情，龛里放艺术照
    else if (R && RACE_ART[R.id] && hasArt(RACE_ART[R.id])) art = artUrl(RACE_ART[R.id]);
    for (const box of $$b('.bx-id .niche, .bx-idm .th')) {
      const img = box.querySelector('img');
      if (art) { if (img.getAttribute('src') !== art) img.src = art; img.classList.add('on'); img.classList.toggle('own', own); } else img.classList.remove('on');
      box.classList.toggle('has', !!art);
    }
  }
  const pop = (el) => { if (!el) return; el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop'); };
  const popId = () => pop(isM() ? $b('.bx-idm') : $b('.bx-id'));

  /* ---------- 开头：两条路，和接续旅印 ---------- */
  function gate() {
    BS.mode = 'gate'; BS.focus = null;
    renderRail(); renderSide(); idUpdate();
    const isk = F.soul === 'isekai', tk = !BS.free && BS.FR && !BS.m.site;          // 拿车票进来的：车票定了纪、主线和落在哪；这一纪有自己报年份的，另给一条从头建的路
    const body = bodyEl(); body.className = 'bx-body gate';
    body.innerHTML = `<div class="bx-gate">
<button type="button" class="bx-card bx-way life" data-deal data-a="way" data-v="life"${isk ? ' disabled' : ''}><span class="face"${hasArt('life_end') ? ` style="--img:url('${artUrl('life_end')}')"` : ''}><span class="pic"></span><b>翻我的前半生</b><small>十一步，多五章前半生</small><em>${isk ? '你是整个人掉进来的，这一纪没有你的前半生。' : '胎骨定了以后，降生、家、孩童、少年、离家，一章一张牌，或者自己写。她照你翻的替后面几步先填上，到了那一步还能改。'}</em></span></button>
<button type="button" class="bx-card bx-way direct" data-deal data-a="way" data-v="direct"><span class="face"><span class="sheet-art"><i></i><i></i><i></i><i></i><i></i></span><b>一项一项定</b><small>不翻前半生，十一步</small><em>魂、胎骨、金血、起点、六维、命路、命星、誓心，一步一样，自己挑。前半生留给第〇轮她来念。</em></span></button>
</div>
${tk ? `<p class="bx-resume bx-ticket"><span class="tk">车票　${esc(BS.m.site ? '起点「' + BS.m.site + '」' : '主线「' + (BS.m.line || '') + '」的开局')}</span><button type="button" data-a="tofree">不拿车票，从头建一个人</button><span>自己报一年，落在哪也自己挑（${esc(BS.FR.label)}）</span></p>` : ''}
<p class="bx-resume"><button type="button" data-a="resume">接续旅印</button><span>贴一段旧的存档或上一轮的回复，接着往下走</span></p>`;
    $b('.bx-ctl [data-a="next"]').textContent = isk ? '一项一项定' : '翻我的前半生';
    const bp = $b('.bx-ctl [data-a="prev"]'); bp.textContent = frame ? '回到书里' : '回到牌桌';
    speak(LINES.gate.in); BX.idleN = 0; poke();
    dealIn($$b('.bx-body [data-deal]'));
  }

  /* ---------- 十一步 ---------- */
  const STEP = {}, SIDE = {};
  const prose = (ls) => `<div class="b2-prose">${ls.map((l) => `<p${/^「/.test(l) ? ' class="r"' : ''}>${l}</p>`).join('')}</div>`;
  const imgOr = (n, fb) => (hasArt(n) ? `url('${artUrl(n)}')` : fb || 'var(--bb)');
  // 一张牌：外头一层只管位置（进出的动画动它），里头一层翻面
  const cardHTML = (cls, attrs, front, back, up) => `<button type="button" class="bx-card ${cls}${up ? ' up' : ''}" data-deal ${attrs}><span class="lift"><span class="flip"><span class="face a">${front}</span><span class="face b">${back}</span></span></span></button>`;

  // 一、魂：三张牌三幅画
  STEP[1] = () => ({
    p: '三种都行。本地是这一纪生下来的人，胎穿是带着前一世的记性生在这一纪，身穿是连人带身子原样落进来。',
    body: `<div class="bx-souls">${Object.entries(SOUL).map(([k, s], i) => cardHTML('bx-soul' + (F.soul === k ? ' picked' : ''), `data-a="soul" data-v="${k}" aria-pressed="${F.soul === k}"`,
      `<span class="img" style="background-image:var(--bb)"></span>`,
      `<span class="img" style="background-image:${imgOr('soul_' + k)}"></span><span class="bx-pl">${esc(s.n.split(' · ')[0])}<small>${esc(s.tag)}</small></span><span class="num">${['I', 'II', 'III'][i]}</span>`, true)).join('')}</div>
<div class="bx-paper bx-world"${F.soul === 'reborn' || F.soul === 'isekai' ? '' : ' hidden'}><label for="b2-world">${F.soul === 'isekai' ? '你从哪个世界来' : '前一世是什么样的人'}<small>一两句，可不填，不填由她替你补</small></label><textarea id="b2-world" data-f="world" rows="2" maxlength="300" placeholder="比如 原来是城里的护士，一场车祸以后就到了这里">${esc(F.world || '')}</textarea></div>`,
    primary: '就是这样来的',
    deal: { stagger: 120 },
  });
  SIDE.soul = (k) => {
    const s = SOUL[k], E = BS.E;
    const extra = k === 'isekai' ? [E.panel, E.first].filter(Boolean) : ['你生在' + BS.era + '，有父母、有故乡，这一纪的人当你是自己人。从哪一家长大、学过什么，后面几步一样一样定。', '金血那一步你可以挑神亲，祂的祝福落在你血里。'];
    if (k === 'reborn') extra.push('没有人知道，你其实已经活过一次了。');
    return { html: `<h2>${esc(s.n)}</h2><span class="tag">${esc(s.tag)}</span>${prose(s.say)}<h5>在${esc(BS.era)}</h5>${extra.map((t) => `<p>${esc(clean(t))}</p>`).join('')}`, primary: '就是这样来的' };
  };

  // 二、睁眼之前：她推过来一张纸
  function whenHTML() {
    const y = oyear(), FR = BS.FR, P = curP();
    if (BS.free) {
      const Ps = (BS.E.periods || []).filter((p) => p.id !== '1001' && FR && p.from <= FR.to && p.to >= FR.from);
      const Pn = periodAt(y), lo = Pn ? Math.max(Pn.from, FR.from) : FR.from, hi = Pn ? Math.min(Pn.to, FR.to) : FR.to;
      return `<div class="b2-when"><p class="r">「你要落进哪一年？」</p>
<div class="b2-axis" role="list">${Ps.map((p) => `<button type="button" role="listitem" class="b2-stop${Pn === p ? ' on' : ''}" data-a="per" data-v="${esc(p.id)}"><span class="dot"></span><b>${esc(p.name)}</b><small>${esc(yText(Math.max(p.from, FR.from)))}到${esc(yText(Math.min(p.to, FR.to)))}</small></button>`).join('')}</div>
<div class="b2-yr"><input type="range" min="${lo}" max="${hi}" step="1" value="${y != null ? Math.max(lo, Math.min(hi, y)) : lo}" data-a="yr" aria-label="在这一段里挑一年"><label>哪一年<input id="b2-year" type="text" inputmode="numeric" maxlength="6" data-f="year" value="${esc(F.year || '')}" placeholder="${esc(BS.era)} ${FR.from} 到 ${FR.to}"></label></div>
<p class="b2-note">${y != null && Pn ? `<b>${esc(BS.era)} ${esc(yText(y))} · ${esc(Pn.name)}</b>　${esc(clean(Pn.note || ''))}` : esc(clean(FR.note || ''))}</p>
${BS.m.line ? `<p class="b2-switch"><button type="button" data-a="tofree">照书里那一条主线开局</button></p>` : ''}</div>`;
    }
    if (BS.m.site) return `<div class="b2-when"><p class="r">「我把你放在哪儿，你就从哪儿开始。」</p><p class="b2-at"><b>${esc(BS.era)}${y != null ? ' ' + esc(yText(y)) : ''}</b>　起点「${esc(BS.m.site)}」${BS.m.ti ? `<span>${esc(clean(BS.m.ti))}</span>` : ''}</p></div>`;          // 此刻那一本挑的起点：站在一处，不是落在一条主线上
    return `<div class="b2-when"><p class="r">「我把你放在哪儿，你就从哪儿开始。」</p><p class="b2-at"><b>${esc(BS.era)}${y != null ? ' ' + esc(yText(y)) : ''}</b>　${esc(BS.m.title || '')}　主线「${esc(BS.m.line || '')}」${P && P.note ? `<span>${esc(clean(P.note))}</span>` : ''}</p>
${BS.FR ? `<p class="b2-switch"><button type="button" data-a="tofree">不走这条主线，自己报年份（${esc(BS.FR.label)}）</button></p>` : ''}</div>`;
  }
  STEP[2] = () => {
    const sexes = ['男', '女', '无性', '自定义'], isk = F.soul === 'isekai';
    return {
      p: '她把纸推到你面前，指尖在空白处停了一停。这一页只有名字要写，别的留空，她会替你补上，在凭证里注明。',
      body: `<div class="bx-paper big" data-deal>
<div class="b2-f"><label for="b2-name">名字<small class="r">「写下你的名字。」</small></label><input id="b2-name" type="text" maxlength="24" data-f="name" value="${esc(F.name || '')}" placeholder="她先问这个"></div>
<div class="b2-row"><div class="b2-f"><span class="lb">性别</span><div class="b2-chips">${sexes.map((s) => `<button type="button" data-a="sex" data-v="${s}" aria-pressed="${F.sex === s}">${s}</button>`).join('')}</div><input type="text" maxlength="12" data-f="sexOther" value="${esc(F.sexOther || '')}" placeholder="照你说的写"${F.sex === '自定义' ? '' : ' hidden'}></div>
<div class="b2-f"><label for="b2-age">年岁<small>${isk ? '穿越前多大，落地以后就是多大' : '开局那一年你多大'}</small></label><input id="b2-age" type="text" maxlength="12" data-f="age" value="${esc(F.age || '')}" placeholder="可不填"><small class="b2-hint r">「年龄也说清楚。别只报一个看着顺眼的数。」</small></div>
<div class="b2-f"><label for="b2-height">身高<small>可不填</small></label><input id="b2-height" type="text" maxlength="16" data-f="height" value="${esc(F.height || '')}" placeholder="比如 168cm"></div></div>
<div class="b2-f"><label for="b2-look">样子<small class="r">「模样也写清。往后以这副身姿走在人世，总该由你先认一认。」</small></label><textarea id="b2-look" rows="2" maxlength="300" data-f="look" placeholder="头发、眼睛、个子，身上一样认得出的东西">${esc(F.look || '')}</textarea></div>
${whenHTML()}</div>`,
      primary: '好了，回到她面前',
    };
  };

  // 三、胎骨：十二族一族一张牌，排成一扇；点一张挪到正中翻过来，背面是支系
  function raceFan(life) {
    const P = curP(), absent = P.absent || [], born = isGoldSoul() || life;
    const races = (P.races || []).map(raceOf).filter((r) => r.name);
    return `<div class="bx-fan" data-n="${races.length}">${races.map((r, i) => {
      const ab = absent.includes(r.id), off = ab && born, art = RACE_ART[r.id] && hasArt(RACE_ART[r.id]);
      return `<div class="bx-slot" data-i="${i}">${cardHTML('bx-race' + (F.race === r.id ? ' picked' : '') + (ab ? ' ab' : '') + (art ? '' : ' noart'), `data-a="race" data-v="${esc(r.id)}"${off ? ' disabled' : ''} aria-pressed="${F.race === r.id}"`,
        `<span class="img" style="background-image:${art ? `url('${artUrl(RACE_ART[r.id])}')` : 'var(--bb)'}"></span><span class="bx-pl">${esc(r.name)}${ab ? '<small>这时候世上还没有</small>' : (F.race === r.id && F.sub ? `<small>${esc(F.sub)}</small>` : '')}</span>`,
        '', false).replace('class="bx-card bx-race', `class="bx-card bx-race${BS.lift === r.id ? ' lifted' : ''}`)}</div>`;
    }).join('')}</div>`;
  }
  function raceFocusHTML() {
    if (!BS.lift || BS.lift !== F.race || !F.race) return '';
    const R = raceOf(F.race), subs = subsNow(R), y = oyear(), art = RACE_ART[R.id] && hasArt(RACE_ART[R.id]);
    const later = (R.subs || []).filter((x) => x.from && x.to == null && y != null && x.from > y);          // 带 to 的是某一段才有的人群，别的年代不列“N年才有”
    return `<div class="bx-focus"><div class="bx-card bx-race big up"><span class="lift"><span class="flip"><span class="face a"><span class="img" style="background-image:${art ? `url('${artUrl(RACE_ART[R.id])}')` : 'var(--bb)'}"></span></span>
<span class="face b"><span class="subs"><b class="h">${esc(R.name)}</b><span class="nt">${esc(clean(R.note || ''))}</span>
<span class="list">${subs.length ? subs.map((x) => `<button type="button" class="sb" data-a="sub" data-v="${esc(x.name)}" aria-pressed="${x.name === F.sub}">${esc(x.name)}<small>${esc(clean(x.note || ''))}</small></button>`).join('') : '<span class="nt">这一族不分支。</span>'}
${later.map((x) => `<span class="sb off">${esc(x.name)}<small>${x.from}年才有</small></span>`).join('')}</span>
<button type="button" class="back" data-a="unfocus">放回去</button></span></span></span></span></div></div>`;
  }
  function raceMore() {
    const folk = pcFolk(), bodies = pcBodies(), Pt = (BUILD && BUILD.portraits) || {};
    return `<details class="bx-more"${F.race || F.race2 || F.pcMode || F.build ? ' open' : ''}><summary>细处：混血、哪一家、体格与立绘（看得见立绘）</summary><div class="bx-paper">
<div class="b2-f"><label for="b2-race2">想再说细一点<small>混血、哪一家、哪一支，选了自定义的写在这里</small></label><input id="b2-race2" type="text" maxlength="60" data-f="race2" value="${esc(F.race2 || '')}" placeholder="可不填"></div>
<div class="b2-f b2-pc"><span class="lb">体格与立绘<small>${esc(clean(Pt.clothes || ''))}</small></span>
<div class="b2-chips">${[['', '不要立绘'], ['preset', '照族属、性别、体格的预设'], ['url', '贴自己的图']].map(([v, t]) => `<button type="button" data-a="pcm" data-v="${v}" aria-pressed="${(F.pcMode || '') === v}">${t}</button>`).join('')}</div>
${F.pcMode === 'preset' ? (folk ? `<p class="b2-note">族属照${esc(folk)}${F.sex === '女' || F.sex === '男' ? '，' + esc(F.sex) : '，性别没写照男'}。挑一种体格：</p><div class="b2-chips b2-bodies">${bodies.map((b) => { const p = pcPreset(b); return `<button type="button" data-a="body" data-v="${esc(b)}" aria-pressed="${F.build === b}"${p ? ' class="th"' : ''}>${p ? `<span class="fx" style="background-image:url('${esc(p.face)}')"></span>` : ''}${esc(b)}</button>`; }).join('')}</div>` : '<p class="b2-note">先挑一族。</p>') : ''}
${F.pcMode === 'url' ? `<input type="text" maxlength="300" data-f="art" value="${esc(F.art || '')}" placeholder="全身图的地址 https://"><input type="text" maxlength="300" data-f="face" value="${esc(F.face || '')}" placeholder="头像的地址，可不填">` : ''}
<div class="b2-pcw">${pcPreviewHTML()}</div>
${F.pcMode !== 'preset' ? `<input type="text" maxlength="24" data-f="build" value="${esc(F.build || '')}" placeholder="体格，比如 修长紧实、结实敦厚，可不填">` : ''}</div></div></details>`;
  }
  STEP[3] = () => {
    const P = curP(), born = isGoldSoul();
    return {
      p: `${esc(P.name || '这一纪')}里的各族。这时候世上还没有的族，${born ? '生在这一纪的你选不了' : '原样落进来的你可以是头一个'}。点一张翻过来，背面是支系，再在下面挑哪一家。`,
      body: raceFan() + raceMore(),
      primary: '就是这一族',
      after: () => layoutFan(),
      deal: { stagger: 45 },
    };
  };
  function layoutFan() {
    const fan = $b('.bx-fan'); if (!fan) return;
    const slots = [...fan.querySelectorAll('.bx-slot')], n = slots.length; if (!n) return;
    const W = fan.clientWidth;
    if (isM()) { fan.style.height = ''; slots.forEach((s) => { s.style.cssText = ''; }); fan.classList.add('grid'); return; }
    fan.classList.remove('grid');
    const st = $b('.bx-stage'), H = Math.max(260, (st ? st.clientHeight : 600) - 170);
    const cw = Math.max(84, Math.min(150, W / 8.2, H / 2.1)), ch = cw * 1.5;
    const R = Math.max(W * 0.95, 700), A0 = Math.min(34, (W * 0.42 / R) * 180 / Math.PI);
    fan.style.height = Math.round(ch + R * (1 - Math.cos(A0 * Math.PI / 180)) + 40) + 'px';
    fan.style.setProperty('--cw', cw + 'px');
    slots.forEach((s, i) => {
      const a = n > 1 ? -A0 + 2 * A0 * i / (n - 1) : 0, rad = a * Math.PI / 180;
      const x = W / 2 + R * Math.sin(rad) - cw / 2, y = 14 + R * (1 - Math.cos(rad));
      s.style.left = x + 'px'; s.style.top = y + 'px'; s.style.setProperty('--r', a + 'deg'); s.style.zIndex = i;
    });
  }
  SIDE.race = (id) => {
    const R = raceOf(id), P = curP(), subs = subsNow(R), S = subs.find((x) => x.name === F.sub) || null, ab = (P.absent || []).includes(id);
    let h = `<h2>${esc(R.name)}</h2>${ab ? '<span class="tag">这时候世上还没有，你是头一个</span>' : ''}<p>${esc(clean(R.note || ''))}</p>`;
    const pn = (P.race_notes || {})[id]; if (pn) h += `<h5>这一段</h5><p>${esc(clean(pn))}</p>`;
    if (R.arrive && F.soul === 'isekai') h += `<h5>原样落进来的${esc(R.name)}</h5><p>${esc(clean(R.arrive))}</p>`;
    if (subs.length) h += `<h5>支系</h5><div class="b2-chips">${subs.map((x) => `<button type="button" data-a="sub" data-v="${esc(x.name)}" aria-pressed="${x.name === F.sub}">${esc(x.name)}</button>`).join('')}</div>`;
    if (S) {
      h += `<p class="s"><b>${esc(S.name)}</b>　${esc(clean(S.note || ''))}${S.art ? '　传承的手艺是' + esc(S.art) + '。' : ''}${S.when ? '　' + esc(clean(S.when)) + '。' : ''}</p>`;
      if (S.arrive && F.soul === 'isekai') h += `<p>${esc(clean(S.arrive))}</p>`;
      const kins = (S.kin || []).filter((x) => visible(x, oyear()));
      if (kins.length) h += `<h5>哪一家</h5><div class="b2-chips">${kins.map((x) => `<button type="button" data-a="kin" data-v="${esc(x.name)}" aria-pressed="${x.name === F.kin}">${esc(x.name)}</button>`).join('')}</div>`;
      const K = kins.find((x) => x.name === F.kin); if (K) h += `<p class="s"><b>${esc(K.name)}</b>　${esc(clean(K.note || ''))}${K.when ? '　' + esc(clean(K.when)) : ''}</p>`;
    }
    return { html: h, primary: '就是这一族' };
  };

  // 四、金血：神亲一枚一枚的像，排成几道弧
  STEP[4] = () => {
    if (!isGoldSoul()) return { p: '身穿的人没有这一步。', body: `<div class="bx-paper" data-deal>${prose(['你是原样落进来的，血里没有这一纪的神。', '她看了你一眼，没有在这一页上停。'])}</div>`, primary: '往下走' };
    const G = ((DATA.gold && DATA.gold.eras) || {})[BS.book] || { gods: [] }, by = birthYear(), y = oyear(), list = godsNow();
    const grp = []; for (const g of list) { let x = grp.find((q) => q[0] === g.grp); if (!x) grp.push(x = [g.grp, []]); x[1].push(g); }
    const ageT = ageNum() ? '你报的年岁是' + ageNum() + '岁' : '年岁没报，照十八岁算';
    const live = list.filter((g) => !g.off).length;
    return {
      small: '生在这一纪的人才有，可以跳过',
      h1: '金血祝颂',
      p: `你的血醒着。${esc(clean(G.note || ''))}${by != null ? `${esc(yText(y))}开局，${esc(ageT)}，你生在<b>${esc(byText(by))}前后</b>，那时候在世的有 ${live} 位。` : ''}挑一位，祂的祝福落在血里，是一颗 <b>Legend 的 Passive</b>。`,
      body: `<div class="bx-gold0">${cardHTML('bx-plain' + (F.goldN === '-' ? ' picked' : ''), 'data-a="gold" data-v="-"', '', '<span class="pl"><b>不要金血</b><small>父母都是凡人，血是红的。</small></span>', true)}${cardHTML('bx-plain' + (F.goldN === '*' ? ' picked' : ''), 'data-a="gold" data-v="*"', '', '<span class="pl"><b>金血醒着，神亲不挑</b><small>照这一纪的规矩替你挑一位，开场不点破。</small></span>', true)}</div>
${grp.map(([n, gs]) => `${grp.length > 1 ? `<h3 class="bx-gh">${esc(n)}<small>${gs.filter((g) => !g.off).length} 位</small></h3>` : ''}<div class="bx-gods">${gs.map((g) => `<button type="button" class="bx-god${g.off ? ' off' : ''}${F.goldN === g.n ? ' picked' : ''}" data-deal data-a="god" data-v="${esc(g.n)}"${g.off ? ` data-d="${esc(g.off)}"` : ''}><i><img src="${esc(g.img || '')}" alt="" loading="lazy" decoding="async" onerror="this.remove()"></i><b>${esc(godName(g))}</b><small>${esc(g.off || String(g.rule || '').replace(/^管/, ''))}</small></button>`).join('')}</div>`).join('')}`,
      primary: F.goldN && F.goldN !== '-' ? '就是这一位' : '往下走',
      deal: { stagger: 22 },
    };
  };
  SIDE.god = (n) => {
    const g = godsNow().find((x) => x.n === n); if (!g) return null;
    const by = birthYear();
    const year = g.off ? (BS.book === 'strife' ? `祂在${esc(g.off.replace('倒下', ''))}倒下了。你生在${esc(byText(by))}前后，那时候祂已经不在。` : `你生在${esc(byText(by))}前后，那时候祂还没有聚成。`)
      : (by != null ? `${esc(byText(by))}前后，祂还在。` : '');
    const know = (DATA.gold && DATA.gold.know) || ['知道是谁的血', '不知道，往后自己认出来'];
    return {
      html: `<h2>${esc(g.n)}</h2><span class="tag">神亲</span><span class="tag g">${esc(g.tag || '')}${esc(g.n)} · ${esc(String(g.rule || '').replace(/^管/, ''))}</span>
<h5>这一年</h5><p>${year}</p>
<div class="b2-star"><b>${esc(g.star)}<small>Legend · Passive · 金血祝颂</small></b><p class="bl">${esc(clean(g.bless))}</p>${g.motto ? `<p class="mt">${esc(clean(g.motto))}</p>` : ''}${g.desc ? `<p>${esc(clean(g.desc))}</p>` : ''}<details open><summary>效果</summary><p>${esc(clean(g.eff))}</p></details><details><summary>限制</summary><p>${esc(clean(g.lim))}</p></details></div>
${BS.book === 'maze' && g.old ? `<p class="b2-note">${esc(clean(g.old))}</p>` : ''}
${g.off ? '' : `<h5>你知不知道</h5><div class="b2-know b2-chips">${know.map((t, i) => `<button type="button" data-a="know" data-v="${i}" aria-pressed="${(F.goldKnow || 0) === i}">${esc(t)}</button>`).join('')}</div><p class="b2-note">叙述和旁人不点破。往后的事归剧透开关，关着。</p>`}`,
      primary: g.off ? '再看看' : '就是这一位',
    };
  };
  SIDE.gold0 = (v) => ({ html: v === '*' ? `<h2>神亲不挑</h2><p>你是黄金裔，血是金色的，神亲是哪一位照这一纪的规矩替你挑，开场不点破。金血祝颂跟着那一位走，是一颗 Legend 的 Passive。</p>` : `<h2>不要金血</h2><p>父母都是凡人，你照寻常人长大。往后走到哪一步，看你自己。</p>`, primary: '往下走' });

  // 五、起点：六位阶一阶一枚徽记，十九档挂在徽记下
  STEP[5] = () => {
    const M = measure(), y = oyear(), fanji = BS.book === 'maze' && (y || 0) >= 318;
    return {
      p: `${esc(M.t)}。十九档都能选，档决定六维的上限和点数。英雄和传奇要有配得上的伟业，写在最后一步，留空由她替你补。`,
      body: `<div class="bx-tiers">${TIER_GROUP.map(([g, r], gi) => `<div class="bx-tg${g === '传奇' ? ' hi' : ''}${tierKey().startsWith(g) ? ' on' : ''}" data-deal><span class="ins" style="background-image:${hasArt('tier_' + gi) ? `url('${artUrl('tier_' + gi)}')` : 'none'}"><i>${esc(g.slice(0, 1))}</i></span><b>${g}</b><small>${r}</small><span class="ms">${esc(M.g[g])}</span><span class="cord"></span><span class="tags">${TIERS.filter((t) => t[0].startsWith(g)).map((t) => {
        const off = t[0] === '传奇·凡极' && !fanji;
        return `<button type="button" class="bx-tier${tierKey() === t[0] ? ' on' : ''}" data-a="tier" data-v="${t[0]}"${off ? ' disabled title="凡人的尽头要到迷宫纪318年才有人走到"' : ''}><b>${t[0].split('·')[1]}</b><span>${t[1]}</span></button>`;
      }).join('')}</span></div>`).join('')}</div>`,
      primary: '从这里起步',
      deal: { stagger: 90 },
    };
  };
  SIDE.tier = (k) => {
    const t = tierOf(k), g = k.split('·')[0], M = measure(), c = (() => { const o = F.tier; F.tier = k; const r = caps(); F.tier = o; return r; })();
    const awake = BS.book === 'maze' && panelOn() ? (F.soul === 'isekai' ? '原样落进来的人落地时面板还没觉醒，开局先去公会登记。' : (k === '启源·初识' ? '还没推开公会那扇门，面板要到登记那天才亮。' : '你已经登记过，也已经觉醒，面板开局就生效。')) : '';
    return { html: `<h2>${esc(k)}</h2><span class="tag">${esc(t[1])}</span><span class="tag g">${esc(g)}位阶</span><h5>这一纪看得出的</h5><p>${esc(M.g[g])}。</p><h5>六维</h5><p>单项基础上限 ${t[2]}，再照胎骨修正，六维上限合起来 ${capSum(c)}，自己分的点数是一半。</p>${awake ? `<p>${esc(awake)}</p>` : ''}${g === '英雄' || g === '传奇' ? '<p class="b2-note">从这一档起步要有配得上的伟业，写在最后一步“还想让她知道的”里，留空由她替你补。</p>' : ''}`, primary: '从这里起步' };
  };

  // 六、六维：一盘星图，拖一角那一维就长；掷一回是两颗骰子自己滚出来
  STEP[6] = () => {
    ensureStats();
    const c = caps(), mods = RACE_MOD[statRace()] || {}, later = F.statMode === 'later';
    return {
      p: '单项上限看起点和胎骨，自己分的点数是上限总和的一半。拖星图上的一角，那一样就长。也可以掷一回（四成到七成），或者满溢开局。不想分就交给她，照胎骨和起点补。',
      body: `<div class="bx-statw">
<div class="bx-chart" data-deal>${later ? '<p class="later">六维留给她照胎骨、起点和出身补，开场一句话说明。</p>' : chartSVG()}<div class="dice" aria-hidden="true"><i></i><i></i></div></div>
<div class="bx-sside" data-deal><div class="b2-sctx"><b>${esc(statRace())}</b> · ${esc(tierKey())}</div>
<div class="b2-chips b2-sact"><button type="button" data-a="stat" data-v="even" aria-pressed="${F.statMode === 'even' || F.statMode === 'manual'}">均衡分配</button><button type="button" data-a="stat" data-v="roll" aria-pressed="${F.statMode === 'roll'}">掷一回</button><button type="button" data-a="stat" data-v="cap" aria-pressed="${F.statMode === 'cap'}">全上限开局（满溢）</button><button type="button" data-a="stat" data-v="later" aria-pressed="${later}">先不分，交给她</button></div>
${later ? '' : `<div class="b2-meter"><span>已分</span><b></b><span>/ ${budget()}</span><i><u></u></i><em></em></div>
<div class="bx-srows">${STAT.map(([k, n, d]) => { const md = mods[k] || 0; return `<div class="bx-srow" data-k="${k}"><span class="k"><b>${k}</b>${n}${md ? `<em class="${md > 0 ? 'up' : 'dn'}">${md > 0 ? '+' : ''}${md}%</em>` : ''}<small>${esc(d)}</small></span><button type="button" class="pm" data-a="sdec" data-v="${k}" aria-label="${n}减一">−</button><input type="number" min="1" max="${c[k]}" value="${F.stats[k]}" data-a="sn" data-v="${k}" aria-label="${n}的点数"><button type="button" class="pm" data-a="sinc" data-v="${k}" aria-label="${n}加一">+</button><span class="cap">/ ${c[k]}</span></div>`; }).join('')}</div>`}</div></div>`,
      primary: '定了',
      after: () => { syncMeter(); bindChart(); },
    };
  };
  const SC = 200, SR = 148;
  const axis = (i) => { const a = (-90 + i * 60) * Math.PI / 180; return [Math.cos(a), Math.sin(a)]; };
  function chartSVG() {
    const rings = [0.25, 0.5, 0.75, 1].map((f) => `<polygon class="ring" points="${STAT.map((_, i) => { const [x, y] = axis(i); return (SC + x * SR * f).toFixed(1) + ',' + (SC + y * SR * f).toFixed(1); }).join(' ')}"/>`).join('');
    const ax = STAT.map(([k, n], i) => { const [x, y] = axis(i); return `<line class="ax" x1="${SC}" y1="${SC}" x2="${SC + x * SR}" y2="${SC + y * SR}"/><text class="lb" x="${SC + x * (SR + 28)}" y="${SC + y * (SR + 28) + 5}" text-anchor="middle">${k}<tspan class="cn" x="${SC + x * (SR + 28)}" dy="15">${n}</tspan></text>`; }).join('');
    const stars = [...Array(26)].map((_, i) => { const a = i * 2.39996, r = 20 + (i * 37) % 170; return `<circle class="dust" cx="${(SC + Math.cos(a) * r).toFixed(1)}" cy="${(SC + Math.sin(a) * r).toFixed(1)}" r="${(0.6 + (i % 3) * 0.4).toFixed(1)}"/>`; }).join('');
    const hs = STAT.map(([k, n], i) => `<g class="hd" data-k="${k}" data-i="${i}" tabindex="0" role="slider" aria-label="${n}" aria-valuemin="1"><circle class="hit" r="20"/><circle class="dot" r="7"/><text class="v" dy="-13" text-anchor="middle"></text></g>`).join('');
    return `<svg class="chart" viewBox="-30 -20 460 450" aria-label="六维星图">${stars}${rings}${ax}<polygon class="val" points=""/>${hs}<text class="tot" x="${SC}" y="${SC + 6}" text-anchor="middle"></text></svg>`;
  }
  function drawChart() {
    const svg = $b('.bx-chart svg'); if (!svg || !F.stats) return;
    const c = caps();
    const pts = STAT.map(([k], i) => { const f = Math.max(0.02, Math.min(1, (F.stats[k] || 1) / c[k])), [x, y] = axis(i); return [SC + x * SR * f, SC + y * SR * f]; });
    svg.querySelector('.val').setAttribute('points', pts.map((p) => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' '));
    svg.querySelectorAll('.hd').forEach((g) => { const i = +g.dataset.i, k = g.dataset.k; g.setAttribute('transform', `translate(${pts[i][0].toFixed(1)},${pts[i][1].toFixed(1)})`); g.querySelector('.v').textContent = F.stats[k]; g.setAttribute('aria-valuenow', F.stats[k]); g.setAttribute('aria-valuemax', c[k]); });
    svg.querySelector('.tot').textContent = statTotal() + ' / ' + budget();
  }
  function setStat(k, v) {
    const c = caps(); v = Math.max(1, Math.min(c[k], Math.round(v)));
    if (F.stats[k] === v) return;
    F.stats[k] = v; if (F.statMode !== 'roll') F.statMode = 'manual';          // 掷过一回的照掷出来的总数分，别的照上限的一半
    for (const b of $$b('[data-a="stat"]')) b.setAttribute('aria-pressed', 'false');
    const inp = $b(`.bx-srow[data-k="${k}"] input`); if (inp && document.activeElement !== inp) inp.value = v;
    drawChart(); syncMeter(); idUpdate();
  }
  function bindChart() {
    drawChart();
    const svg = $b('.bx-chart svg'); if (!svg) return;
    let drag = null;
    const toSvg = (e) => { const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY; return pt.matrixTransform(svg.getScreenCTM().inverse()); };
    svg.addEventListener('pointerdown', (e) => { const g = e.target.closest('.hd'); if (!g) return; drag = g; g.setPointerCapture(e.pointerId); g.classList.add('drag'); e.preventDefault(); });
    svg.addEventListener('pointermove', (e) => {
      if (!drag) return;
      const p = toSvg(e), i = +drag.dataset.i, k = drag.dataset.k, [ax, ay] = axis(i), c = caps();
      const t = Math.max(0, Math.min(1, ((p.x - SC) * ax + (p.y - SC) * ay) / SR));
      const room = budget() - statTotal() + (F.stats[k] || 0);
      setStat(k, Math.min(Math.max(1, Math.round(t * c[k])), Math.max(1, room)));
    });
    const up = () => { if (drag) { drag.classList.remove('drag'); drag = null; } };
    svg.addEventListener('pointerup', up); svg.addEventListener('pointercancel', up);
    svg.addEventListener('keydown', (e) => { const g = e.target.closest('.hd'); if (!g) return; const k = g.dataset.k, d = e.key === 'ArrowUp' || e.key === 'ArrowRight' ? 1 : e.key === 'ArrowDown' || e.key === 'ArrowLeft' ? -1 : 0; if (!d) return; e.preventDefault(); if (d > 0 && statTotal() >= budget()) return; setStat(k, (F.stats[k] || 1) + d); });
  }
  const syncMeter = () => {
    const B = budget(), tot = statTotal(), m = $b('.b2-meter'); if (!m) return;
    m.classList.toggle('ok', tot === B); m.querySelector('b').textContent = tot; m.querySelector('u').style.width = Math.min(100, B ? tot / B * 100 : 0) + '%';
    m.querySelector('em').textContent = tot === B ? '正好' : (tot < B ? '还余 ' + (B - tot) : '超了 ' + (tot - B));
    const s = $b('.bx-chart .tot'); if (s) s.textContent = tot + ' / ' + B;
  };
  // 掷一回：两颗骰子自己滚到星图上
  async function rollDice() {
    const ch = $b('.bx-chart'); if (!ch || BX.busy) { setStatMode('roll'); return; }
    BX.busy = true;
    const dice = ch.querySelector('.dice');
    if (!RMo()) {
      dice.querySelectorAll('i').forEach((d) => { d.dataset.p = 1 + Math.floor(Math.random() * 6); });
      dice.classList.remove('go'); void dice.offsetWidth; dice.classList.add('go');
      (window.__sfx || (() => {}))('dice');          // 建档：掷骰子
      await T(1000);
    }
    BX.busy = false;
    setStatMode('roll');
    speak(LINES[6].roll);
  }

  // 七、命路：二十三条一条一枚纹章，排成一圈；月银纪是兵器与技艺，兵器挂在架上
  function pathRing() {
    const paths = (BS.D.paths || []), sel = F.path;
    const P = sel && sel !== '*' ? paths.find((p) => p.name === sel) : null, st = P ? pathState(P.name) : null;
    return `<div class="bx-ring"><div class="core">${P ? `<span class="em" style="background-image:${imgOr('path_' + PATH_KEY[P.name], 'none')}"></span><b>${esc(P.name)}</b><em>${esc(P.type)}</em><span>${esc(P.short)}</span><i>${esc(st.lit ? st.tag : '先行者 · ' + st.tag)}</i>` : sel === '*' ? '<b>自定义</b><span>写你自己的路子，写在下面那一格。</span>' : '<b>挑一枚</b><span>二十三条路，灰着的这一年还没有名字，选了你就是先行者。</span>'}</div>
${paths.map((p, i) => { const s = pathState(p.name), k = PATH_KEY[p.name]; return `<button type="button" class="bx-emb${s.lit ? '' : ' grey'}${sel === p.name ? ' picked' : ''}" data-deal data-i="${i}" data-a="path" data-v="${esc(p.name)}" title="${esc(p.name + '　' + p.type + '　' + s.tag)}"><span class="em" style="background-image:${imgOr('path_' + k, 'none')}"><i>${esc(p.name.slice(0, 1))}</i></span><b>${esc(p.name)}</b></button>`; }).join('')}
<button type="button" class="bx-emb cus${sel === '*' ? ' picked' : ''}" data-deal data-a="path" data-v="*"><span class="em" style="background-image:${imgOr('path_custom', 'none')}"><i>自</i></span><b>自定义</b></button></div>`;
  }
  function layoutRing() {
    const ring = $b('.bx-ring'); if (!ring) return;
    const embs = [...ring.querySelectorAll('.bx-emb:not(.cus)')], n = embs.length;
    if (isM()) { ring.classList.add('grid'); ring.style.height = ''; embs.forEach((e) => { e.style.left = ''; e.style.top = ''; }); return; }
    ring.classList.remove('grid');
    const st = $b('.bx-stage'), W = ring.clientWidth, H = Math.max(420, Math.min(st ? st.clientHeight - 130 : 600, W * 0.95));
    const S = Math.min(W, H), R = S / 2 - 58;
    ring.style.height = S + 'px';
    embs.forEach((e, i) => { const a = (-90 + i * 360 / n) * Math.PI / 180; e.style.left = (W / 2 + Math.cos(a) * R) + 'px'; e.style.top = (S / 2 + Math.sin(a) * R) + 'px'; e.style.setProperty('--lx', (Math.cos(a) * 50).toFixed(1) + 'px'); e.style.setProperty('--ly', (Math.sin(a) * 42).toFixed(1) + 'px'); });          // 名字照这一枚在圈上的方向往外放，不压着旁边那一枚
    const cu = ring.querySelector('.cus'); if (cu) { const out = W / 2 + R + 110 < W; cu.style.left = (out ? W / 2 + R + 80 : W / 2 + R * 0.62) + 'px'; cu.style.top = (out ? S / 2 + R * 0.75 : S / 2 + R * 0.72) + 'px'; }          // 自定义那一枚：圈外右下角，放不下才进圈里
  }
  STEP[7] = () => {
    const y = oyear(), E = BS.E;
    if (BS.book === 'moon') {
      const ws = (E.weapons || []).filter((w) => visible(w, y)), arts = (E.arts || []).filter((a) => visible(a, y)), sch = (E.schools || []).filter((s) => visible(s, y));
      const grp = (k) => ws.filter((w) => w.k === k);
      const tag = (a, x) => `<button type="button" class="bx-tag${F[a] === x.n ? ' picked' : ''}" data-deal data-a="${a}" data-v="${esc(x.n)}"><b>${esc(x.n)}</b><span>${esc(clean(x.note || x.teach || ''))}</span></button>`;
      return {
        h1: '兵器与技艺',
        p: `这一纪没有命路，认一个人先看他手里的兵器，再问是哪一家教的。${esc(clean(E.job || ''))}`,
        body: `<div class="bx-rack"><h3 class="bx-gh">近身</h3><div class="row">${grp('近身').map((w) => tag('weapon', w)).join('')}</div>
<h3 class="bx-gh">远身</h3><div class="row">${grp('远身').map((w) => tag('weapon', w)).join('')}</div>
${grp('甲').length ? `<h3 class="bx-gh">身上的甲<small>可不选</small></h3><div class="row">${grp('甲').map((w) => tag('armor', w)).join('')}</div>` : ''}</div>
<div class="bx-paper"><div class="b2-f"><label for="b2-style">风格<small>兵器加风格，比如 大剑·蓄斩、长刀·风铃一剑</small></label><input id="b2-style" type="text" maxlength="20" data-f="style" value="${esc(F.style || '')}" placeholder="可不填"></div></div>
<h3 class="bx-gh">法门与手艺<small>${esc(clean(E.arts_rule || '').split('。')[0])}</small></h3><div class="bx-scrolls">${arts.map((a) => tag('marts', a)).join('')}</div>
<h3 class="bx-gh">学派<small>可不选</small></h3><div class="bx-scrolls">${sch.map((s) => tag('school', s)).join('')}</div>`,
        primary: '带上这些',
        deal: { stagger: 16 },
      };
    }
    const job = BS.book === 'maze' && y != null && y < (E.job_from || 420);
    let head;
    if (BS.book === 'strife') head = (y != null && y < 1104 ? '命路这个叫法 <b>1104 年</b>才有，这一年二十三条都还没有名字。' : '命路这个叫法是 <b>1104 年</b>起的。这一年有名字、有路册的亮着。') + '灰着的也能选，选了你就是那一路的<b>先行者</b>。' + (F.race === 'demon' ? '沸血在魔族营里早就有，你是魔族，这一张是亮的。' : '沸血在魔族营里早就有，选魔族的人这一张是亮的。') + '铁律、解构这一纪还没走成路。';
    else if (BS.book === 'bronze') head = '二十三条命路纷争纪末已经归齐。铁律到麦的年月（862年）才走成一条路，这以前灰着，选了你就是那一路的<b>先行者</b>。';
    else head = '二十三条都立着。' + (job ? '公会的秘仪 <b>420 年</b>起才替人就职，这一年只挑路，不就职。' : '公会的秘仪替人就职，职业格写兵器加路名。');
    return {
      p: head,
      body: `<div class="bx-pathw">` + pathRing() + `<div class="bx-paper bx-pside"><div class="b2-row"><div class="b2-f"><label for="b2-weapon">手里的兵器<small>可不填</small></label><input id="b2-weapon" type="text" maxlength="16" data-f="weapon" value="${esc(F.weapon || '')}" placeholder="比如 长戟、塔盾、长弓"></div>
<div class="b2-f"><label for="b2-style">风格<small>${BS.book === 'strife' ? '路还没有名字的写风格' : '还没认路的写风格'}</small></label><input id="b2-style" type="text" maxlength="20" data-f="style" value="${esc(F.style || '')}" placeholder="可不填"></div></div>
${F.path === '*' ? `<div class="b2-f"><label for="b2-pathc">自定义命路</label><textarea id="b2-pathc" rows="2" maxlength="300" data-f="pathCustom" placeholder="主修哪几项，擅长的手艺，想往哪边长">${esc(F.pathCustom || '')}</textarea></div>` : ''}
${job ? `<p class="b2-note">${esc(yText(y))}公会的秘仪还不替人就职，420年起才有，这一步只挑路。</p>` : ''}
<p class="b2-note">${esc(clean(E.job || ''))}</p></div></div>`,
      primary: '走这一路',
      after: () => layoutRing(),
      deal: { stagger: 26 },
    };
  };
  SIDE.path = (name) => {
    if (name === '*') return { html: '<h2>自定义命路</h2><p>写在下面那一格里：主修哪几项，擅长的手艺，想往哪边长。</p>', primary: '走这一路' };
    const p = (BS.D.paths || []).find((x) => x.name === name) || { name, type: '', short: '' }, st = pathState(name), y = oyear(), s = st.s || {};
    let h = `<h2>${esc(p.name)}</h2>${st.lit ? '' : '<span class="tag">先行者</span>'}<span class="tag g">${esc(String(p.type).replace(' / ', ' · '))}</span><p>${esc(p.short)}</p>`;
    if (BS.book === 'strife') {
      h += `<h5>这一年</h5><p>${st.lit ? esc(yText(y)) + '，' + esc(clean(s.when || '')) + '。' : esc(yText(y)) + '，' + esc(p.name) + '还没有名字，也没有路册。' + (s.from ? '要到' + esc(clean(s.when || '')) + '。' : esc(clean(s.when || '')) + '。')}</p>`;
      if (s.root) h += `<h5>根</h5><p>${esc(clean(s.root))}。</p>`;
    } else if (BS.book === 'bronze') {
      h += `<h5>这一年</h5><p>${st.lit ? esc(clean(BS.E.paths_note || '')) : esc(p.name) + '要到' + (BS.E.path_from || {})[name] + '年麦的年月才走成一条路。'}</p>`;
    } else {
      h += `<h5>这一年</h5><p>${esc(clean(BS.E.paths_note || ''))}${y != null && y < (BS.E.job_from || 420) ? '　' + esc(yText(y)) + '公会还不替人就职，只挑路。' : ''}</p>`;
    }
    if (!st.lit) h += `<h5>你走这一路</h5><p>你是头一批走这一路的人。往后订成路册的时候，头一页记着的人里有你一份。墙上的人照旧叫不出这一路的名字，只说你会那一手。</p><div class="b2-cred">【命路】倾向：${esc(p.name)}（先行者）<br>这一年还没有名字，叙述照那时候的叫法写</div>`;
    return { html: h, primary: '走这一路' };
  };
  SIDE.mitem = (v) => {
    const [a, n] = v.split('|'), E = BS.E, src = a === 'school' ? E.schools : a === 'marts' ? E.arts : E.weapons, x = (src || []).find((q) => q.n === n); if (!x) return null;
    const lab = { weapon: '兵器', armor: '甲', marts: x.k || '法门', school: '学派' }[a];
    return { html: `<h2>${esc(x.n)}</h2><span class="tag g">${esc(lab)}${x.k && a !== 'marts' ? ' · ' + esc(x.k) : ''}</span>${x.teach ? `<h5>教什么</h5><p>${esc(clean(x.teach))}</p>` : ''}<p>${esc(clean(x.note || ''))}</p>${a === 'marts' ? `<p class="b2-note">${esc(clean(E.arts_rule || ''))}</p>` : ''}`, primary: '带上这些' };
  };

  // 八、命星：从一叠星牌里抽，翻牌的时候按稀有度放光，Unique 那一张一眼不一样
  // 11-25：点一张牌只是翻开来看，留不留、放不放进候星在说明里定（下面那枚主钮是“留下这一颗”）。台面上多了一排：留下、候星、落星、落星归叠
  const starKey = (k) => (F['draw' + k] ? F['draw' + k].n + ':' + (F['draw' + k].key || '') : '');          // 翻没翻过只看是第几手：取走一张、放回一张不重翻
  const starOn = (k, id) => !!(BS.focus && BS.focus.k === 'star' && BS.focus.v === k + '|' + id);
  function starCardHTML(t, k, sel, up) {
    const fr = hasArt('star_' + t.tier.toLowerCase()) ? `url('${artUrl('star_' + t.tier.toLowerCase())}')` : 'none';
    return `<button type="button" class="bx-card bx-star${sel === t.id ? ' picked' : ''}${starOn(k, t.id) ? ' on' : ''}${up ? ' up' : ''}${up && t.tier !== 'Rare' && t.tier !== 'Normal' ? ' lit' : ''}" data-t="${esc(t.tier)}" data-deal data-a="star" data-v="${k}|${esc(t.id)}"><span class="rays"></span><span class="glow"></span><span class="lift"><span class="flip"><span class="face a" style="background-image:var(--sback)"></span><span class="face b" style="background-image:${fr}"><span class="txt"><span class="ty">${esc(t.type)} · ${esc(t.tier)}</span><span class="nm">${esc(t.name)}</span><span class="ds">${esc(clean(t.desc).replace(/^(Passive|Special|Art|Active)。/, ''))}</span></span></span></span></span></button>`;
  }
  STEP[8] = () => {
    const empty = !((DATA.stars && DATA.stars.stars) || []).length;
    if (empty) return { p: '命星池还在备。这一步先交给她，照这一纪的规矩给你三颗，开场说明。', body: `<div class="bx-paper" data-deal>${prose(['她把两只空着的手摊开，又合上。', '「这一样，等你到了那里再说。」'])}</div>`, primary: '往下走' };
    const dk = BS.book + '|' + (curP().id || '') + '|' + (oyear() == null ? '' : oyear());          // 年份换了（自己报年份改了年份），池子跟着换，重抽
    for (const q of STAR_KINDS) {
      const pool = starPool(q); if (!pool.length) continue;
      const D0 = F['draw' + q];
      if (!D0 || D0.key !== dk) {          // 头一回，或者池子换了：旧的台面和落星作废（不算抽过），候星和留下的还在新池子里的照留
        const Dq = starZ(q, pool); Dq.ids = []; Dq.gone = []; drawStars(q); Dq.key = dk;
      } else {
        const Dq = starZ(q, pool);
        if (!Dq.ids.length && !Dq.hold.length && !Dq.gone.length && !(F['star' + q] && F['star' + q] !== '*')) drawStars(q);          // 换了族，台面上那一手都不在池子里了
      }
    }
    const k = STAR_KINDS.includes(BS.pool) ? BS.pool : 'S', pool = starPool(k), D = starZ(k, pool), list = drawn(k), sel = F['star' + k];
    const deck = starDeck(k, pool).length, hold = starsBy(k, D.hold), gone = D.gone.length, kept = starOf(k), R = rates();
    const shown = BX.revealed[k] === starKey(k);
    const CUS = { S: 'Special 要写清被动、主动、冷却、限制和代价。', P: 'Passive 写持续的效果和边界。', A: 'Art 写修行的路子和瓶颈，Active 写怎么放、耗什么、冷却和代价。' };
    const chip = (t, cls, lab) => `<button type="button" class="tk ${cls}${starOn(k, t.id) ? ' on' : ''}" data-t="${esc(t.tier)}" data-a="sview" data-v="${k}|${esc(t.id)}" title="${esc(t.type)} · ${esc(t.tier)}">${lab ? `<small>${lab}</small>` : ''}<b>${esc(t.name)}</b></button>`;
    const keptChip = !kept ? `<button type="button" class="tk kp none" data-a="tray" data-v="${k}"><small>留下</small><b>未留</b></button>`
      : kept.custom ? `<button type="button" class="tk kp has${starOn(k, '*') ? ' on' : ''}" data-a="sview" data-v="${k}|*"><small>留下</small><b>${esc(F['sc' + k + 'n'] || '自己写的一颗')}</b></button>` : chip(kept, 'kp has', '留下');
    const dry = !deck ? `<p class="b2-note bx-dry">${gone ? `${TRAY.deck}抽空了。让${TRAY.gone}归叠，才有牌再抽，留下的和${TRAY.hold}不会动。` : `这一叠的星都在你手边了，没有可抽的。就从这几颗里留。`}</p>` : '';
    return {
      p: `三叠各抽十颗，各留一颗，点一张翻开看，再定留不留。Special 是生来的天赋，Passive 是生来的体质，Art 和 Active 是学来的手艺。池子照${esc(BS.era)}${esc(yText(oyear()))}滤过：生来的星这一年以前有过的都在，往后才有的不在。手艺只留这一年最新的那一版，改了叫法的照这一纪的叫法。`,
      body: `<div class="bx-sttab">${STAR_KINDS.map((q) => `<button type="button" data-a="pool" data-v="${q}" aria-pressed="${k === q}">${KIND_NAME[q]}<b>${KIND_CN[q]}</b>${F['star' + q] ? '<i>已留</i>' : ''}</button>`).join('')}</div>
<div class="bx-tray" data-k="${k}"><span class="tl">留下</span>${keptChip}<span class="tl hx">${TRAY.hold}</span><span class="hc">${hold.map((t) => chip(t, 'hd')).join('')}${'<i class="tk slot" aria-hidden="true"></i>'.repeat(Math.max(0, HOLD_MAX - hold.length))}</span>
<span class="tn">没留的落进${TRAY.gone}，再抽不再出。${TRAY.hold}至多三颗，再抽不动它。归叠只倒回${TRAY.gone}。</span>
<button type="button" class="tk sum" data-a="tray" data-v="${k}" aria-label="${TRAY.hold} ${hold.length}，至多 ${HOLD_MAX}">${TRAY.hold}<b>${hold.length}/${HOLD_MAX}</b></button><button type="button" class="tk gn" data-a="tray" data-v="${k}" title="抽过没留的，再抽不会再出">${TRAY.gone}<b>${gone}</b></button>
<button type="button" class="tk rs${!deck && gone ? ' call' : ''}" data-a="sreset" data-v="${k}" title="只把${TRAY.gone}倒回${TRAY.deck}，留下的和${TRAY.hold}不动"${gone ? '' : ' disabled'}>${TRAY.reset}</button><button type="button" class="dr${deck ? '' : ' off'}" data-a="draw" data-v="${k}">${deck ? '再抽' + NUM[Math.min(10, deck)] + '张' : '叠空了'}</button></div>
<div class="bx-stars"><div class="bx-deck${deck ? '' : ' dry'}"><span></span><span></span><span></span><em>${deck} 颗</em></div><div class="bx-slots">${list.map((t) => starCardHTML(t, k, sel, shown)).join('')}
<button type="button" class="bx-card bx-star cus${sel === '*' ? ' picked' : ''}${starOn(k, '*') ? ' on' : ''} up" data-a="star" data-v="${k}|*"><span class="lift"><span class="flip"><span class="face a"></span><span class="face b"><span class="txt"><span class="ty">自定义 ${KIND_NAME[k]}</span><span class="nm">自己写一颗</span><span class="ds">${CUS[k]}</span></span></span></span></span></button></div></div>
${dry}<p class="b2-pity">Legend 保底 ${Math.min(D.lp, R.pl)}/${R.pl}　Unique 保底 ${Math.min(D.up, R.pu)}/${R.pu}　已抽 ${D.n} 回　照${esc(BS.era)}${esc(yText(oyear()))}滤过的 ${KIND_NAME[k]} 池子 ${pool.length} 颗｜${TRAY.deck} ${deck}　台面 ${list.length}　${TRAY.hold} ${hold.length}　${TRAY.gone} ${gone}</p>`,
      primary: '带上这三颗',
      after: (enter) => { if (!shown) revealStars(k); if (BX.trayPop) { pop($b('.bx-tray .' + BX.trayPop)); BX.trayPop = ''; } },
      deal: () => ({ stagger: 34, from: deckAt() || undefined }),
    };
  };
  /* 手边的星：留下的、候星、落星摊开看（手机上那一排只有数，点开是这一张；电脑上点“落星”也是它） */
  SIDE.tray = (k) => {
    if (!STAR_KINDS.includes(k)) return null;
    const pool = starPool(k), D = starZ(k, pool), kept = starOf(k), hold = starsBy(k, D.hold), deck = starDeck(k, pool).length;
    const gone = starsBy(k, D.gone).sort((a, b) => (T_RANK[b.tier] || 0) - (T_RANK[a.tier] || 0) || String(a.name).localeCompare(String(b.name), 'zh-Hans-CN'));
    const row = (id, name, sub, tier, acts) => `<div class="bx-trow" data-t="${esc(tier || '')}"><button type="button" class="nm" data-a="sview" data-v="${k}|${esc(id)}"><b>${esc(name)}</b><small>${esc(sub)}</small></button>${acts}</div>`;
    const b = (a, id, t, cls) => `<button type="button" class="bt sm${cls ? ' ' + cls : ''}" data-a="${a}" data-v="${k}|${esc(id)}">${t}</button>`;
    const keptRow = !kept ? `<p class="s">还没有留。台面上点一张翻开看，再定留不留。</p>`
      : kept.custom ? row('*', F['sc' + k + 'n'] || '自己写的一颗', '自定义 ' + KIND_NAME[k], '', b('sdrop', '*', '先不留'))
        : row(kept.id, kept.name, kept.type + ' · ' + kept.tier, kept.tier, (hold.length < HOLD_MAX ? b('shold', kept.id, '改放进' + TRAY.hold) : '') + b('sdrop', kept.id, starAt(k, kept.id) === 'keep' ? '先不留' : '撤下'));
    return { html: `<h2>手边的星</h2><span class="tag g">${KIND_NAME[k]} · ${KIND_CN[k]}</span>
<h5>留下的</h5>${keptRow}
<h5>${TRAY.hold}　${hold.length}/${HOLD_MAX}</h5><p class="b2-note">看中了又想接着抽的，先压在这里，一叠至多三颗。再抽不动它，撤下的落进${TRAY.gone}。</p>${hold.map((t) => row(t.id, t.name, t.type + ' · ' + t.tier, t.tier, b('skeep', t.id, '留下', 'pri') + b('sdrop', t.id, '撤下'))).join('') || '<p class="s">空着。</p>'}
<h5>${TRAY.gone}　${gone.length} 颗</h5><p class="b2-note">抽过没留的都落在这里，再抽不会再出。${TRAY.reset}只把它们倒回${TRAY.deck}，留下的和${TRAY.hold}不动。</p>${gone.length ? `<div class="bx-gone">${gone.map((t) => `<button type="button" data-t="${esc(t.tier)}" data-a="sview" data-v="${k}|${esc(t.id)}">${esc(t.name)}</button>`).join('')}</div>` : '<p class="s">空着。</p>'}
<div class="bx-sact"><button type="button" class="bt sm" data-a="sreset" data-v="${k}"${gone.length ? '' : ' disabled'}>${TRAY.reset}</button></div>
<h5>${TRAY.deck}　${deck} 颗</h5><p class="b2-note">还抽得到的。${deck ? '' : '眼下抽空了。'}</p>` };
  };
  // 一张一张翻，按稀有度放光
  async function revealStars(k) {
    const cards = $$b('.bx-slots .bx-star:not(.cus)'); if (!cards.length) return;
    BX.revealed[k] = starKey(k);
    if (RMo()) { cards.forEach((c) => { c.classList.add('up'); if (!/Rare|Normal/.test(c.dataset.t)) c.classList.add('lit'); }); return; }
    await T(40);
    while (BX.busy) await T(80);
    BX.busy = true;
    await T(200);
    let best = 'Rare';
    for (const c of cards) {
      if (!c.isConnected) break;
      const t = c.dataset.t; c.classList.add('up');
      if ((T_RANK[t] || 0) > (T_RANK[best] || 0)) best = t;
      await T(t === 'Unique' ? 360 : 120);
      if (t !== 'Rare' && t !== 'Normal') c.classList.add('lit');
      if (t === 'Unique') { const r = c.getBoundingClientRect(), f = $b('.bx-flash'); f.style.setProperty('--fx', (r.left + r.width / 2) + 'px'); f.style.setProperty('--fy', (r.top + r.height / 2) + 'px'); f.classList.remove('go'); void f.offsetWidth; f.classList.add('go'); await T(650); }
      else await T(t === 'Legend' ? 300 : 70);
    }
    BX.busy = false;
    speak(TIER_SAY[best] || TIER_SAY.Rare);
  }
  SIDE.star = (v) => {
    const [k, id] = v.split('|');
    if (id === '*') {
      const ty = KIND_TYPES[k] || KIND_TYPES.A;
      const ph = { S: ['复合天赋的名字', 'Special 写被动、主动、冷却、限制和代价。'], P: ['体质的名字', 'Passive 写持续的效果和边界。'], A: ['技艺或主动能力的名字', 'Art 写修行的路子、怎么入门、往哪边长、卡在哪里。Active 写怎么放、耗什么、多大范围、冷却和代价。'] }[k] || ['', ''];
      return { html: `<h2>自己写一颗</h2><span class="tag g">${KIND_NAME[k] || 'Art · Active'}</span>
<div class="b2-f"><label>名字</label><input type="text" maxlength="24" data-f="sc${k}n" value="${esc(F['sc' + k + 'n'] || '')}" placeholder="${ph[0]}"></div>
<div class="b2-row">${ty.length > 1 ? `<div class="b2-f"><label>类</label><div class="b2-chips">${ty.map((t) => `<button type="button" data-a="sct" data-v="${k}|${t}" aria-pressed="${(F['sc' + k + 't'] || ty[0]) === t}">${t}</button>`).join('')}</div></div>` : ''}
<div class="b2-f"><label>阶</label><div class="b2-chips">${['Rare', 'Epic', 'Legend', 'Unique'].map((t) => `<button type="button" data-a="scr" data-v="${k}|${t}" aria-pressed="${(F['sc' + k + 'r'] || 'Rare') === t}">${t}</button>`).join('')}</div></div></div>
<div class="b2-f"><label>写清楚</label><textarea rows="5" maxlength="500" data-f="sc${k}d" placeholder="${ph[1]}">${esc(F['sc' + k + 'd'] || '')}</textarea></div>
${F['star' + k] === '*' ? `<div class="bx-sact"><span class="at">留下的</span><button type="button" class="bt sm" data-a="sdrop" data-v="${k}|*">先不留</button></div>` : ''}`, primary: F['star' + k] === '*' ? undefined : '留下这一颗' };
    }
    const t = starPool(k).find((x) => x.id === id); if (!t) return null;
    // 这一颗眼下在哪，能拿它做什么。留下那一枚在手机上跟底下的主钮是同一件事，只在电脑上显（.k）
    const at = starAt(k, id), n = starZ(k).hold.length, full = n >= HOLD_MAX;
    const b = (a, txt, cls) => `<button type="button" class="bt sm${cls ? ' ' + cls : ''}" data-a="${a}" data-v="${k}|${esc(id)}">${txt}</button>`;
    const AT = { keep: '留下的', 'keep-off': '留下的', hand: '台面上', hold: TRAY.hold, gone: TRAY.gone, deck: TRAY.deck }[at];
    const acts = at === 'hand' ? b('skeep', '留下这一颗', 'pri k') + b('shold', `放进${TRAY.hold} ${n}/${HOLD_MAX}`, full ? 'dimmed' : '')
      : at === 'hold' ? b('skeep', '留下这一颗', 'pri k') + b('sdrop', `撤下，落进${TRAY.gone}`)
        : at === 'keep' ? b('shold', `改放进${TRAY.hold} ${n}/${HOLD_MAX}`, full ? 'dimmed' : '') + b('sdrop', '先不留')
          : at === 'keep-off' ? b('shold', `改放进${TRAY.hold} ${n}/${HOLD_MAX}`, full ? 'dimmed' : '') + b('sdrop', `撤下，落进${TRAY.gone}`) : '';
    const tip = at === 'gone' ? `<p class="b2-note">这一颗落在${TRAY.gone}里，再抽不会再出。${TRAY.reset}以后它回到${TRAY.deck}，再抽才可能遇见。</p>` : at === 'hold' ? `<p class="b2-note">压在${TRAY.hold}里，再抽不动它。</p>` : at === 'keep-off' ? `<p class="b2-note">已经留下，不在台面上，再抽不动它。</p>` : '';
    return { html: `<h2>${esc(t.name)}</h2><span class="tag">${esc(t.type)}</span><span class="tag g t-${t.tier}">${esc(t.tier)}</span>
<div class="bx-sact"><span class="at">${AT}</span>${acts}</div>${tip}${t.name !== t.base ? `<p class="b2-note">迷宫纪1001年叫它${esc(t.base)}。</p>` : ''}${t.note ? `<h5>在${esc(BS.era)}</h5><p>${esc(clean(t.note))}</p>` : ''}<p>${esc(clean(t.desc))}</p>`, primary: at === 'hand' || at === 'hold' ? '留下这一颗' : undefined };
  };

  // 九、誓心与出身：九张誓心牌，一张一句誓词；底下是这一纪的册子
  STEP[9] = () => {
    const P = curP(), S = sheetOf(P), y = oyear(), isk = F.soul === 'isekai';
    const sks = (P.skills || []).map((s) => (typeof s === 'string' ? { s } : s)).filter((s) => visible(s, y));          // 11-24 第二轮起一项可以带 d（一句说明）：挑上的那一项按钮里多一行小字，电脑上悬停也浮出来；凭证照旧只写短名
    const cols = (S.cols || []).map((c) => {
      let v = (F.sheet || {})[c] || '', ro = '', ph = '';
      if (c === '名字') { v = F.name || ''; ro = '照第二步'; }
      else if (c === '族') { v = raceText(); ro = '照第三步'; }
      else if (c === '手里的兵器' && BS.book === 'moon' && F.weapon && !v) v = F.weapon;
      else if (c === '哪一家教的' && BS.book === 'moon' && F.school && !v) v = F.school;
      const blank = S.blank && S.blank.label === c && isk;
      if (blank) ph = '报不出';
      return `<div class="b2-sc"><span>${esc(c)}</span>${ro ? `<b>${esc(v || '未写')}<small>${ro}</small></b>` : `<input type="text" maxlength="40" data-sheet="${esc(c)}" value="${esc(blank ? '' : v)}" placeholder="${esc(ph || (c === '谁担保' ? '可不填，7年起要有人担保' : '可不填'))}"${blank ? ' disabled' : ''}>`}</div>`;
    }).join('');
    const extraCol = isk ? '' : (S.blank && S.blank.label && !(S.cols || []).includes(S.blank.label) ? `<div class="b2-sc"><span>${esc(S.blank.label)}</span><input type="text" maxlength="40" data-sheet="${esc(S.blank.label)}" value="${esc((F.sheet || {})[S.blank.label] || '')}" placeholder="可不填"></div>` : '');
    let gifts = '';
    if (isk) {
      if (!F.drawG || !giftsDrawn().length) drawGifts();
      const D = F.drawG, gs = giftsDrawn();
      gifts = `<h3 class="bx-gh">神殿赐物<small>身穿的人才有，只许一件</small></h3>${prose(['「孤身来到陌生的世界，手里总该有件可用之物。选吧，只许一件。」', '「原主都已离世。若有人认出它，问起故人，怎样回答，你自己斟酌。」'])}
<div class="b2-gmeta"><button type="button" class="bt sm" data-a="regift">再看一批</button><span>已看 ${D.n} 批　Legend 保底 ${Math.min(D.sl, 3)}/3　Unique 保底 ${Math.min(D.su, 8)}/8</span></div>
<div class="bx-gifts">${gs.map((g) => `<button type="button" class="bx-gift t-${g.r}${F.giftN === g.n ? ' picked' : ''}" data-t="${esc(g.r)}" data-a="gift" data-v="${esc(g.n)}"><i class="tier">${esc(g.r)}${g.kind === 'relic' ? ' · 遗物' : ''}</i><b>${esc(g.n)}</b><span>${esc(clean(g.d))}</span></button>`).join('')}<button type="button" class="bx-gift plain${F.giftN === '-' ? ' picked' : ''}" data-a="gift" data-v="-"><i class="tier">不收</i><b>什么也不要</b><span>两手空空地出这道门。</span></button></div>`;
    }
    return {
      p: `誓心不拦你做什么，只记你待人行事的样子，可以不选。出身照这一纪的册子写，${esc(S.who || '')}${S.who ? '问的' : ''}${isk ? '，你报不出的那一栏空着' : ''}。`,
      body: `<div class="bx-oaths">${OATH.map(([n, d]) => cardHTML('bx-oath' + (F.oath === n ? ' picked' : '') + (hasArt(OATH_KEY[n]) ? '' : ' noart'), `data-a="oath" data-v="${esc(n)}" aria-pressed="${F.oath === n}"`, '',
        `<span class="img" style="background-image:${imgOr(OATH_KEY[n])}"></span><span class="bx-pl">${esc(n)}<small>${esc(VOW[n])}</small></span>`, true)).join('')}</div>
<h3 class="bx-gh">出身<small>${esc(P.name || '')}</small></h3>
<div class="bx-paper b2-sheet"><div class="hd"><img src="${A('common/assets/ui/emblem_' + (BS.book === 'now' ? 'maze' : BS.book) + '.webp')}" alt=""><div><b>${esc(S.title || '登记')}</b><small>${esc(S.who || '')}${S.ask ? '　' + esc(S.ask) : ''}</small></div></div>${cols}${extraCol}
${isk && S.blank && S.blank.line ? `<p class="blank">${esc(clean(S.blank.line))}</p>` : ''}${(S.more || []).length ? `<details class="more"><summary>册子上别的几栏</summary>${S.more.map((x) => `<p><b>${esc(x.label)}</b>　${esc(clean(x.line))}</p>`).join('')}</details>` : ''}</div>
<h3 class="bx-gh">这一段的本事<small>挑一两样想往哪边长，也可以自己写</small></h3><div class="bx-sks">${sks.map((k) => `<button type="button" class="bx-sk${k.d ? ' d' : ''}" data-a="skill" data-v="${esc(k.s)}" aria-pressed="${(F.skills || []).includes(k.s)}"><b>${esc(k.s)}</b>${k.d ? `<small>${esc(clean(k.d))}</small>` : ''}</button>`).join('')}</div>
<div class="b2-f"><input type="text" maxlength="60" data-f="skill2" value="${esc(F.skill2 || '')}" placeholder="最想要的一样本事，一句话，可不填"></div>${gifts}`,
      primary: '往下走',
      deal: { stagger: 40 },
    };
  };
  SIDE.oath = (n) => { const o = OATH.find((x) => x[0] === n); return o ? { html: `<h2>${esc(o[0])}</h2><p class="vow">「${esc(VOW[n] || '')}」</p><p>${esc(o[1])}</p><p class="b2-note">誓心影响初识者的态度、交谈和神明的问询，不拦你做什么，不加不减数值。</p>`, primary: '往下走' } : null; };
  SIDE.gift = (n) => {
    if (n === '-') return { html: '<h2>什么也不要</h2><p>你两手空空地出这道门。往后碰上的东西，都是你自己挣来的。</p>', primary: '往下走' };
    const g = giftPool().find((x) => x.n === n); if (!g) return null;
    return { html: `<h2>${esc(g.n)}</h2><span class="tag t-${g.r}">${esc(g.r)}</span>${g.kind === 'relic' ? '<span class="tag g">遗物，原主已经不在了</span>' : ''}<p>${esc(clean(g.d))}</p><h5>效果</h5><p>${esc(clean(g.e))}</p>${g.note ? `<p class="b2-note">${esc(clean(g.note))}</p>` : ''}`, primary: '就要这一件' };
  };

  // 十、落在哪：时代地图上落一枚印
  STEP[10] = () => {
    const MP = mapNow(), P = curP(), y = oyear(), si = sealInfo();
    const wishes = (WISH[BS.book] || []).concat(F.soul === 'native' ? WISH_ALL.slice(0, 1) : WISH_ALL);
    let map = '';
    if (MP) {
      const pins = MP.pins;
      const on = BS.free && F.placeI != null ? pins.find((p) => p.i === F.placeI) : null;
      map = `<div class="bx-map${MP.per.night ? ' night' : ''}" data-deal><div class="in" style="aspect-ratio:${MP.M.w || 2200}/${MP.M.h || 1400}"><img src="${A('common/assets/map/' + MP.per.img + '.webp')}" alt="${esc(MP.per.name)}" loading="lazy">${pins.map((p) => `<button type="button" class="pin${p.hot ? ' hot' : ''}${on && on.i === p.i ? ' on' : ''}" style="left:${p.x}%;top:${p.y}%" data-a="pin" data-v="${p.i}" title="${esc(p.name)}"><i></i><span>${esc(p.name)}</span></button>`).join('')}${on ? `<span class="bx-pinseal" style="left:${on.x}%;top:${on.y}%"></span>` : ''}</div><span class="cap">${esc(MP.per.name)}　${esc(MP.per.sub || '')}</span></div>
<div class="b2-chips pins">${pins.filter((p) => p.hot).concat(pins.filter((p) => !p.hot)).slice(0, 40).map((p) => `<button type="button" data-a="pin" data-v="${p.i}" aria-pressed="${F.placeI === p.i && BS.free}" class="${p.hot ? 'hot' : ''}">${esc(p.name)}</button>`).join('')}</div>`;
    }
    const where = BS.free
      ? `<p class="b2-note">${esc(clean((BS.FR || {}).note || ''))}</p>${map}<div class="b2-f"><label for="b2-place">或者自己写一处<small>可不填，不填落在那一年一处寻常的地方</small></label><input id="b2-place" type="text" maxlength="40" data-f="place" value="${esc(F.placeI == null ? (F.place || '') : '')}" placeholder="想从哪一处睁眼，一句"></div>`
      : `<p class="b2-at bx-tkline"><b>落在 ${esc(BS.m.site ? '起点「' + BS.m.site + '」' : '主线「' + (BS.m.line || '') + '」的开局')}</b>　车票定的。${esc(BS.m.site ? clean(BS.m.ti || '') : (BS.m.title || ''))}</p><p class="b2-switch"><button type="button" data-a="out">回到书里换一张车票</button>${BS.FR && !BS.m.site ? `<button type="button" data-a="tofree">不拿车票，自己报一年（${esc(BS.FR.label)}）</button>` : ''}</p>`;
    let seal = `<p class="b2-note">${esc(si.note)}</p>`;
    if (si.kind === 'roll') { const sh = F.sheet || {}; seal += `<div class="b2-sheet roll"><div class="b2-sc"><span>名字</span><b>${esc(F.name || '未写')}</b></div><div class="b2-sc"><span>姓或家</span><input type="text" maxlength="20" data-sheet="姓或家" value="${esc(sh['姓或家'] || '')}" placeholder="${F.soul === 'isekai' ? '报不出的空着，书记写你守的那一段墙' : '可不填'}"></div><div class="b2-sc"><span>族</span><b>${esc(raceText() || '未写')}</b></div><div class="b2-sc"><span>守哪一段墙</span><input type="text" maxlength="30" data-f="wall" value="${esc(F.wall || '')}" placeholder="可不填"></div></div>`; }
    if (si.kind === 'team') seal += `<div class="b2-row"><div class="b2-f"><label for="b2-team">团名<small>可不填，还没有团就空着</small></label><input id="b2-team" type="text" maxlength="20" data-f="team" value="${esc(F.team || '')}" placeholder="自己起"></div>${si.guild ? `<div class="b2-f"><span class="lb">行会的档次</span><div class="b2-chips">${TEAM_GRADES.map((g) => `<button type="button" data-a="grade" data-v="${g}" aria-pressed="${(F.grade || '没挂号') === g}">${g}</button>`).join('')}</div></div>` : ''}</div>`;
    if (si.kind === 'grade') seal += `<div class="b2-row"><div class="b2-f"><span class="lb">公会的档次</span><div class="b2-chips">${GRADES.map((g) => `<button type="button" data-a="grade" data-v="${g}" aria-pressed="${(F.grade || '还没入会') === g}">${g}</button>`).join('')}</div></div>${si.gua ? `<div class="b2-f"><label for="b2-gua">谁担保<small>可不填，跟挂号册上那一栏是同一栏</small></label><input id="b2-gua" type="text" maxlength="24" data-sheet="谁担保" value="${esc((F.sheet || {})['谁担保'] || '')}" placeholder="头一批担保印是书记按的"></div>` : ''}</div>`;
    if (si.kind === 'rank') seal += `<div class="b2-chips">${RANKS.map((r) => `<button type="button" data-a="rank" data-v="${r}" aria-pressed="${(F.rank || rankDefault()) === r}"${si.isk && r !== '无印' ? ' disabled' : ''}>${r}</button>`).join('')}</div><p class="b2-note">照起点推的是「${esc(rankDefault())}」，可以改。${(y || 0) >= 600 ? '600年起下深层要持深印。' : ''}${(y || 0) >= 850 && (y || 0) <= 970 ? '850年起打仗和潮来的时候公会发战印。' : ''}</p>`;
    return {
      p: BS.free ? '落在哪、为什么上路，和这一纪的人拿什么认你。' : '落在哪车票定了。这一步只问为什么上路，和这一纪的人拿什么认你。',
      body: `<h3 class="bx-gh">${BS.free ? '落在哪' : '车票'}<small>${esc(BS.era)}${y != null ? ' ' + esc(yText(y)) : ''}${P && P.name ? ' · ' + esc(P.name) : ''}</small></h3>${where}
<h3 class="bx-gh">初心<small>为什么上路，可不选</small></h3><div class="bx-wish">${wishes.map(([n, d]) => `<button type="button" class="bx-tag${F.wishPick === n ? ' picked' : ''}" data-deal data-a="wish" data-v="${esc(n)}"><b>${esc(n)}</b><span>${esc(d)}</span></button>`).join('')}</div>
<div class="b2-f"><input type="text" maxlength="80" data-f="wish" value="${esc(F.wish || '')}" placeholder="或者自己写一句，写了的照这一句"></div>
<h3 class="bx-gh">旅印<small>${esc(BS.era)}拿什么认你</small></h3><div class="bx-paper">${seal}</div>`,
      primary: '往下走',
    };
  };
  SIDE.pin = (i) => {
    const MP = mapNow(); const p = MP && MP.pins.find((q) => q.i === +i); if (!p) return null;
    return { html: `<h2>${esc(p.name)}</h2><span class="tag g">${esc(String(p.kind || '').split('：')[0])}</span>${p.hot ? '<span class="tag">这一段碰得上</span>' : ''}<p>${esc(clean(p.where || ''))}</p>${p.later ? `<h5>往后</h5><p>往后叫${esc(p.later)}。</p>` : ''}${BS.free ? '' : BS.m.site ? '<p class="b2-note">这一回从起点「' + esc(BS.m.site) + '」睁眼。</p>' : '<p class="b2-note">这一回照主线开局，睁眼的地方照那一条主线写。</p>'}`, primary: BS.free ? '就落在这里' : '往下走' };
  };
  SIDE.wish = (n) => { const w = (WISH[BS.book] || []).concat(WISH_ALL).find((x) => x[0] === n); return w ? { html: `<h2>${esc(w[0])}</h2><p>${esc(w[1])}</p>`, primary: '往下走' } : null; };

  // 十一、铸印：身份牌挪到正中，这一纪的印自己压下去
  STEP[11] = () => {
    const y = oyear(), P = curP(), g = goldPicked();
    const rows = [['魂', F.soul ? SOUL[F.soul].n : '未定'], ['名字', F.name || '未写'], ['胎骨', raceText() || '未定'], ['金血', isGoldSoul() ? (g ? godName(g) + '　【' + g.star + '】' : F.goldN === '*' ? '醒着，神亲不挑' : '没有') : '身穿没有'],
      ['起点', tierKey()], [BS.book === 'moon' ? '兵器与技艺' : '命路', pathLine() || '未定'], ['命星', STAR_KINDS.map(starLine).filter(Boolean).join(' ＋ ') || '交给她'], ['誓心', F.oath && F.oath !== '-' ? F.oath : '随便'],
      [F.soul === 'isekai' ? '赐物' : '出身', F.soul === 'isekai' ? (giftOf() ? giftOf().n : '什么也不要') : (sheetOf(P).title || '')], [BS.free ? '落在哪' : '落在', BS.free ? placeLine() : placeLine() + '（车票定的）'], ['初心', F.wish || F.wishPick || '还没想好']];
    if (lifeActive() && F._life && F._life.left) rows.splice(3, 0, ['前半生', lifeList().map((k) => LIFE_NAME[k] + (isOwn(k) && ownFilled(k) ? '（自述）' : lifeOpt(k) ? '' : '（留白）')).join('、')]);
    return {
      h1: '铸印',
      p: `都写好了。最后一样，还想让她知道的写在下面，然后盖上${esc(SEAL_NAME[BS.book] || '公会的蜡印')}。`,
      body: `<div class="bx-mint"><div class="b2-final" data-deal data-era="${BS.vis}"><div class="hd"><img src="${A('common/assets/ui/emblem_' + (BS.book === 'now' ? 'maze' : BS.book) + '.webp')}" alt=""><div><b>${esc(BS.era)}${y != null ? ' ' + esc(yText(y)) : ''}</b><small>${esc(P.name || '')}${BS.free ? ' · ' + esc((BS.FR || {}).label || '') : BS.m.site ? ' · 起点「' + esc(BS.m.site) + '」' : (BS.m.line ? ' · 主线「' + esc(BS.m.line) + '」' : '')}</small></div></div>
<dl>${rows.map(([a, b]) => { const t = { 魂: 1, 名字: 2, 胎骨: 3, 金血: 4, 起点: 5, 兵器与技艺: 7, 命路: 7, 命星: 8, 誓心: 9, 赐物: 9, 出身: 9, 落在哪: 10, 初心: 10 }[a]; const btn = a === '前半生' ? 'data-a="lifeat" data-v="0"' : a === '落在' ? 'data-a="out" title="回到书里换一张车票"' : `data-a="step" data-v="${t}"`; return `<dt><button type="button" ${btn}>${esc(a)}</button></dt><dd>${esc(b)}${a === '落在' ? '<small class="tkc">点“落在”回到书里换车票</small>' : ''}</dd>`; }).join('')}</dl>
<div class="b2-f"><label for="b2-extra">还想让她知道的<small>别的设定、想要的开局、不想碰的东西，英雄和传奇起步的写下你的伟业</small></label><textarea id="b2-extra" rows="4" maxlength="600" data-f="extra" placeholder="可不填">${esc(F.extra || '')}</textarea></div>
<div class="b2-f b2-entry"><span class="lb">门扉以前<small>落进这一纪以前，殿里还剩最后一页</small></span><div class="b2-chips">${ENTRY.map(([k, t]) => `<button type="button" data-a="entry" data-v="${k}" aria-pressed="${entryOf() === k}">${esc(t)}</button>`).join('')}</div><p class="b2-note">${esc(ENTRY_NOTE[entryOf()])}</p></div>
<div class="b2-f b2-opts"><span class="lb">开局的档位<small>凭证里多一行快捷指令，不挑就照默认</small></span>${OPTS.map(([k, lab, , cs]) => `<div class="b2-orow"><span class="ol">${esc(lab)}</span><div class="b2-chips">${cs.map(([v, t]) => `<button type="button" data-a="opt" data-v="${k}|${esc(v)}" aria-pressed="${optOf(k) === v}">${esc(t || v)}</button>`).join('')}</div></div>`).join('')}<p class="b2-note">${esc(OPT_NOTE)}</p></div></div>
<div class="bx-mintc"><div class="spot"></div><p class="cap">${esc(SEAL_NAME[BS.book] || '公会的蜡印')}</p></div></div>`,
      primary: '按下去',
      after: () => { root().classList.add('minting'); placeMintCard(); setTimeout(placeMintCard, 480); setTimeout(placeMintCard, 1400); },
    };
  };
  /* 11-26 首轮入局（方向稿 首轮入局_前半生与主控锚点_方向稿.md）：凭证末尾多一行 入局：先补前半生／入局：直接开场，卡里首轮入局驱动认这一行。
     默认先补前半生；旧凭证没有这一行的，卡里也照先补前半生走。凭证别的行一个字没动 */
  const ENTRY = [['life', '先听她念完前半生'], ['open', '径直推开门扉']];
  const ENTRY_NOTE = { life: '她翻开你那一页账，念你从哪里来，交你一页锚点。你应一声“推开门扉”，才落进第一幕。', open: '前半生不念，留给往后的路。头一回便落进第一幕。' };
  const ENTRY_CRED = { life: '入局：先补前半生', open: '入局：直接开场' };
  const entryOf = () => (F.entry === 'open' ? 'open' : 'life');
  /* 11-28 开局的档位：难度、防抢话、篇幅、节奏、调子在铸印那一步先挑好，凭证里多一行卡里现成的快捷指令（【难度：困难】这一类，主提示词「正文输出档位」「玩家主权与防抢话」认的写法），
     卡本体不动。这一行放在“开始游戏。”前头，入局那一行照旧是末行，头一行照旧是纪元 */
  const OPTS = [
    ['diff', '难度', '难度', [['普通'], ['困难']], '普通'],
    ['guard', '防抢话', '防抢话', [['开启', '开'], ['关闭', '关']], '开启'],
    ['len', '篇幅', '输出档位', [['长', '长 · 约千字'], ['很长', '很长 · 约一千五'], ['小说', '小说 · 约两千']], '很长'],
    ['pace', '节奏', '节奏', [['均衡'], ['慢速'], ['快速'], ['大纲']], '均衡'],
    ['tone', '调子', '调子', [['随场', '随场 · 她照场面挑'], ['史诗'], ['冒险'], ['热血'], ['权谋'], ['温情'], ['悬疑'], ['日常'], ['民谣'], ['阴郁'], ['歌剧'], ['荒诞']], '随场'],
  ];
  const optOf = (k) => { const o = OPTS.find((x) => x[0] === k); const v = (F.opt || {})[k]; return o && o[3].some((c) => c[0] === v) ? v : (o ? o[4] : ''); };
  const optLine = () => '开局档位：' + OPTS.map(([k, , cmd]) => `【${cmd}：${optOf(k)}】`).join('') + '（头一条 §底座 照这一行写，往后照底座一轮一轮传）';
  const OPT_NOTE = '进了局也能改，打出【难度：困难】【输出档位：小说】这样的字就切。防抢话开着，她不替你说话、不替你拿主意；关着，你定下的事她替你写完。';
  const starLine = (k) => { const s = starOf(k); if (!s) return ''; if (s.custom) return F['sc' + k + 'n'] ? F['sc' + k + 'n'] + '（自定义）' : '自定义 ' + KIND_NAME[k]; return s.name + '（' + s.tier + '）'; };
  function pathLine() {
    if (BS.book === 'moon') return [F.weapon && F.weapon + (F.style ? '·' + F.style : ''), F.marts, F.school].filter(Boolean).join('，');
    if (!F.path) return '';
    if (F.path === '*') return '自定义';
    return F.path + (pathState(F.path).lit ? '' : '（先行者）');
  }
  function placeLine() {
    if (!BS.free) return BS.m.site ? BS.m.site : '主线「' + (BS.m.line || '') + '」的开局';          // 11-24 此刻那一本挑的起点
    const MP = mapNow(); const p = MP && F.placeI != null ? MP.pins.find((q) => q.i === F.placeI) : null;
    return p ? p.name : (F.place || '那一年一处寻常的地方');
  }
  // 铸印那一步：右边那张身份牌挪到桌子正中那一格
  function placeMintCard() {
    const id = $b('.bx-id'), spot = $b('.bx-mintc .spot'); if (!id || !spot) return;
    if (isM() || BX.minting) { if (isM()) id.style.transform = ''; return; }
    if (BS.mode !== 'step' || BS.step !== 11) return;
    const tr = id.style.transition; id.style.transition = 'none'; id.style.transform = '';
    const a = id.getBoundingClientRect(), b = spot.getBoundingClientRect();
    void id.offsetWidth; id.style.transition = tr;
    const s = Math.min(1.15, b.height / a.height);
    id.style.transform = `translate(${b.left + b.width / 2 - (a.left + a.width / 2)}px,${b.top + b.height / 2 - (a.top + a.height / 2)}px) scale(${s})`;
  }
  function unMint() { BX.minting = false; const x = root(); if (!x) return; x.classList.remove('minting', 'minted'); const id = $b('.bx-id'); if (id) { id.style.transform = ''; id.style.opacity = ''; id.classList.remove('minted', 'shake'); } }

  /* ---------- 每一步往下走以前查一下 ---------- */
  function check(n) {
    if (n === 1 && !F.soul) return '先挑一种来法。';
    if (n === 2) {
      if (!String(F.name || '').trim()) return '名字还没写。';
      if (BS.free) { const y = yearOf(F.year), FR = BS.FR; if (y == null || y < FR.from || y > FR.to) return `哪一年要写一个数，${BS.era} ${FR.from} 到 ${FR.to} 年之间。`; }
    }
    if (n === 3 && !F.race && !String(F.race2 || '').trim()) return '种族挑一个，或者自己写。';
    if (n === 3 && F.race && isGoldSoul() && (curP().absent || []).includes(F.race)) return '这时候世上还没有这一族，生在这一纪的你选不了。';
    if (n === 6 && F.statMode !== 'later') { ensureStats(); const B = budget(), t = statTotal(); if (t !== B) return `六维要正好分满 ${B} 点，眼下是 ${t}。不想分就点“先不分，交给她”。`; }
    return '';
  }
  const markDone = (n) => { F._done = F._done || []; if (!F._done.includes(n)) F._done.push(n); };
  function next() {
    if (BX.busy) return;
    if (BS.mode === 'gate') { F.lifeOn = F.soul !== 'isekai'; F._route = 'direct'; go(Math.min(F._step || 1, F._max || 1)); return; }
    if (BS.mode === 'life') { lifeNext(); return; }
    const err = check(BS.step);
    if (err) { flashErr(err); return; }
    markDone(BS.step);
    if (BS.step === 11) { F._sealed = 1; mint(); return; }
    let n = BS.step + 1;
    if (n === 4 && !isGoldSoul()) { markDone(4); n = 5; }          // 身穿的人没有金血那一步
    if (BS.step === 3 && lifeActive()) { lifeGo(F._life ? Math.min(F._life.i || 0, F._life.left ? 0 : 99) : 0); return; }          // 翻前半生的：胎骨以后先翻那几章
    if (BS.step === 3) { speak(LINES[3].done); }
    go(n);
  }
  function flashErr(t) { const e = $b('.b2-flash'); if (e) e.remove(); const d = document.createElement('p'); d.className = 'b2-flash'; d.setAttribute('role', 'alert'); d.textContent = t; root().appendChild(d); setTimeout(() => d.remove(), 3600); speak([t]); }
  function prev() {
    if (BX.busy) return;
    if (BS.mode === 'gate') { hide(buildEl); if (frame) { bookHide(false); tableOn(false); } else toTable(); return; }
    if (BS.mode === 'life') { lifePrev(); return; }
    if (BS.step <= 1) { unMint(); gate(); return; }
    let n = BS.step - 1; if (n === 4 && !isGoldSoul()) n = 3;
    if (n === 3 && BS.step > 3 && lifeActive()) { if (BS.step === 11) unMint(); lifeGo(lifeList().length - 1); return; }
    if (BS.step === 11) unMint();
    go(n);
  }

  /* ---------- 凭证 ----------
     头一行照旧（纪元、开局时段带年份，卡里的时段钥匙认它；黄金裔在末尾接 ｜出身：黄金裔）。往下照 1001 年那一页的八节排。没选的照原来的写法交给 AI 补。 */
  /* 身穿的降临者照书里开局（11-25，本地干跑报告第 14 条）：凭证里有几句跟“刚从死之神殿落下来”对不上，只对这一种人换说法，别的组合一个字不动。
     管的是照一条主线开局和此刻那一本挑起点的（不是自己报年份的）：初始实力后半句不写这一纪的人怎么量他（斩过什么、下过几回井，他刚落下来），这一段的本事后头注一句是原来的世界带来的。
     照主线开局的另添两处：当前处境后头接一句落在哪、那里的人拿他当什么人（data/land.json，一条主线一句，照各纪页里那一条主线的开局段写的；没有的用 fallback）；
     迷宫纪 420 年以后【面板状态】不写“开局先去公会”（主线一幕不一定在公会门口，有的在井里）。旅印那一行、头一行、命星那两行照旧。 */
  const ISK_LAND = '落在这一条主线头一幕的地方，那里的人头一回见到这个生人，凭什么待得住照那一处的世道定，开场用一句话说明。';
  const iskLand = (m) => { const L = DATA.land || {}, t = ((L.eras || {})[BS.book] || {})[m.line || '']; return clean(t || L.fallback || ISK_LAND); };
  function credential() {
    const D = BS.D, fm = D.format || {}, df = fm.defaults || {}, E = BS.E, era = BS.era, FR = BS.FR || {}, m = BS.m, P = curP(), S = sheetOf(P), y = oyear();
    const line = m.line || '', start = E.start === 'line' ? line : (line.indexOf('·') >= 0 ? line.slice(line.indexOf('·') + 1) : line);
    const yT = y == null ? '' : (y === 1 && BS.book === 'strife' ? '元年' : y + '年');
    let open = BS.free ? `纪元：${era}${yT}｜开局时段：${String(FR.cmd || (FR.label + '｜年份：{year}')).replace('{year}', y === 1 && BS.book === 'strife' ? '元' : y)}` : `纪元：${era}${yT}｜开局时段：${start}`;
    const gold = isGold(), g = goldPicked(), isk = F.soul === 'isekai', soul = F.soul || 'isekai';
    const iskIn = isk && !BS.free, iskLine = iskIn && !m.site;          // 身穿的人照书里开局：照主线的（iskLine），或者此刻那一本挑的起点
    if (gold) open += fm.opening_golden || '｜出身：黄金裔';
    const L = [open, '', fm.head || '命途已确认，请记录我的《奥尔德兰》角色建档：', ''];
    // 一
    L.push('【一·灵魂形态】', SOUL[soul].cred);
    if (soul === 'isekai') L.push('来处：' + (F.world ? clean(F.world) : '未详述（降临者报不出这里的出身' + (S.blank && S.blank.label ? '，册子上“' + S.blank.label + '”那一栏空着' : '') + '）'));
    else {
      if (soul === 'reborn') L.push('前一世：' + (F.world ? clean(F.world) : '未详述（由 AI 定一个，开场一句话说明）'));
      if (g) {
        const know = ((DATA.gold && DATA.gold.know) || ['知道是谁的血', '不知道，往后自己认出来'])[F.goldKnow || 0];
        L.push(`金血：神亲 ${godName(g)}（${clean(g.rule || '')}）｜${know}${BS.book === 'maze' ? '｜隔代醒，祖上是山铜纪七神的孩子' : ''}（叙述和旁人不点破）`);
        L.push(`金血祝颂【${g.star}】（Legend · Passive）｜${g.desc ? clean(g.desc) + '　' : ''}效果：${clean(g.eff)}　限制：${clean(g.lim)}`);
      } else if (F.goldN === '*') L.push('金血：黄金裔，神亲未挑（照这一纪的规矩随机，金血祝颂跟着那一位走，Legend 的 Passive，开场不点破）');
      else L.push('金血：无');
    }
    L.push('');
    // 二
    const R = F.race ? raceOf(F.race) : null;
    let rt = raceText() || '未选择';
    if (R && (P.absent || []).includes(R.id)) rt += '（这时候世上还没有这一族，你是头一个）';
    if (gold) rt += '（黄金裔，凡人那一头是这一族）';
    const KB = kinPicked();
    L.push('【二·种族胎骨】', rt);
    if (KB && KB.blood) L.push('血：' + KB.blood);
    L.push('');
    // 三
    L.push('【三·命路倾向】');
    if (BS.book === 'moon') {
      const w = F.weapon ? (E.weapons || []).find((x) => x.n === F.weapon) : null;
      L.push('兵器：' + (F.weapon ? F.weapon + (w && w.k ? '（' + w.k + '）' : '') : '未认兵') + (F.armor ? '｜甲：' + F.armor : '') + (F.style ? '｜风格：' + F.style : ''));
      L.push('法门与手艺：' + (F.marts || '未选择') + '｜学派：' + (F.school || '未选择'));
      L.push('职业格：' + (F.weapon ? F.weapon + '·' + (F.style || '未定风格') : '未认兵') + '（这一纪没有命路，认人看兵器和哪一家教的）');
    } else if (!F.path) {
      L.push('未选择（由 AI 照这一纪的本事和我的来处定一个方向）');
    } else if (F.path === '*') {
      L.push('自定义命路：' + (F.pathCustom ? clean(F.pathCustom) : '未详述'));
      if (F.weapon || F.style) L.push('职业格：' + [F.weapon || '未认兵', F.style].filter(Boolean).join('·'));
    } else {
      const st = pathState(F.path), p = (D.paths || []).find((x) => x.name === F.path) || { type: '' }, sty = F.style || String(p.type).split(' / ')[1] || '';
      if (st.lit) {
        const nojob = BS.book === 'maze' && y != null && y < (E.job_from || 420);
        L.push('命路：' + F.path + (BS.book === 'strife' && st.tag ? '（' + st.tag + '）' : ''));
        L.push(nojob ? '职业格：' + (F.weapon ? F.weapon + '·' + (F.style || F.path) : '未认兵') + '（这一年公会还不替人就职，不写就职的名目）' : '职业格：' + (F.weapon || '未认兵') + '·' + F.path);
      } else {
        L.push('命路：' + F.path + '（先行者）');
        L.push('职业格：' + (F.weapon || '未认兵') + '·' + sty + '（先行者）');
        L.push('※ 这一年这一路还没有名字，也没有路册，我是头一批走它的人。叙述照那时候的叫法写，墙上的人叫不出名字，只说我会那一手。');
      }
    }
    L.push('');
    // 四
    const tk = tierKey(), tt = tierOf(tk), tg = tk.split('·')[0];
    const ageS = F.age ? clean(F.age) + (isk ? (fm.age_suffix || '') : '') : '未填写（' + (isk ? '落地多大就多大，' : '') + '由 AI 按容貌与经历定一个，开场用一句话说明，不得默认十八岁）';
    const sex = F.sex === '自定义' ? (F.sexOther || '自定义') : (F.sex || df['性别'] || '未填写');
    let pc = '立绘：' + (df['立绘'] || '无');
    if (F.pcMode === 'preset' && pcFolk()) pc = '立绘：预设·' + pcFolk() + '·' + (F.sex === '女' ? '女' : '男') + '·' + (F.build || (pcBodies()[0] || ''));
    else if (F.pcMode === 'url' && F.art) pc = '立绘：' + F.art + (F.face ? '｜头像:' + F.face : '');
    L.push('【四·姓名容貌】', '姓名：' + clean(F.name), '年龄：' + ageS, '性别：' + sex, '容貌：' + (F.look ? clean(F.look) : (df['容貌'] || '未详述')),
      '体态数据：身高 ' + (F.height ? clean(F.height) : (df['身高'] || '未记录（由AI按种族与出身补全）')) + '｜体型 ' + (F.build ? clean(F.build) : (df['体型'] || '未记录（由AI补全）')) + '　（静态资产，状态栏逐轮照抄，正文不主动报数）',
      pc, '自定义设定：' + (F.extra ? clean(F.extra) : (df['自定义设定'] || '（无）')),
      '初始实力：' + tk + '（' + tg + '位阶 · ' + tk.split('·')[1] + '能级｜' + tt[1] + '）｜' + (iskIn ? '原来的世界带来的底子，落地时原样带着，' + (BS.book === 'maze' && panelOn() ? '面板还没照过' : era + '还没有人见过')
        : (BS.book === 'maze' && panelOn() ? '面板照得出' : era + '看得出的') + '：' + measure().g[tg]),
      fm.note || '※ 凡标注「未记录／未选择」的项，由 AI 在首轮按已确定的内容补全，并在开场时用一句话说明补了哪些。', '');
    // 五
    // 一颗星一段：名(类 | 阶)：说明。Passive/Special 那一行先 Special 后 Passive，两颗之间用｜隔开（11-24 第二轮分三池，凭证照旧两行）
    // Special 放前头：现行卡的首轮入局驱动认“这一格第一颗就是命星”，Special 先出来，旧卡也把它当命星，Passive 下回打卡再认进 Passive 行
    const st1 = (k) => {
      const s = starOf(k);
      if (!s) return '';
      if (s.custom) { const ty = F['sc' + k + 't'] || (KIND_TYPES[k] || KIND_TYPES.A)[0]; return `【自定义${ty}】${clean(F['sc' + k + 'n'] || '未命名')}(${ty} | ${F['sc' + k + 'r'] || 'Rare'})：${clean(F['sc' + k + 'd'] || '未详述')}`; }
      return `${s.name}(${s.type} | ${s.tier})：${clean(s.desc)}${s.note ? '　' + era + '：' + clean(s.note) : ''}${s.base && s.base !== s.name ? '　迷宫纪1001年叫' + s.base : ''}`;
    };
    const NOPICK = '未选择（照这一纪的规矩来，由 AI 补一颗，开场说明）';
    const ps = ['S', 'P'].map((k) => st1(k) || (KIND_NAME[k] + ' ' + NOPICK));
    const psLine = 'Passive/Special：' + (!starOf('P') && !starOf('S') ? '未选择（照这一纪的规矩来，由 AI 补一颗 Passive、一颗 Special，开场说明）' : ps.join('｜'));
    L.push('【五·命星天赋】', psLine, 'Art/Active：' + (st1('A') || NOPICK), '');
    // 六
    L.push(isk ? '【六·誓心与赐物】' : '【六·誓心与出身】', '誓心阵营：' + (F.oath && F.oath !== '-' ? F.oath : '随便（由世界照我的来处推一个，开场明说是推的）'));
    // 册子上的几栏，生在这一纪的人另把“从哪里来”那一栏接上（第九步填的），降临者那一栏报不出
    const extraC = !isk && S.blank && S.blank.label && !(S.cols || []).includes(S.blank.label) ? [S.blank.label] : [];
    const cols = (S.cols || []).concat(extraC).map((c) => {
      let v = c === '名字' ? clean(F.name) : c === '族' ? (raceText() || '') : ((F.sheet || {})[c] || (c === '手里的兵器' && BS.book === 'moon' ? F.weapon || '' : '') || (c === '哪一家教的' && BS.book === 'moon' ? F.school || '' : ''));
      if (isk && S.blank && S.blank.label === c) v = '报不出';
      return c + ' ' + (v ? clean(v) : (extraC.includes(c) ? '未写（由 AI 照这一纪寻常的出身定一处）' : '未写'));
    });
    L.push('出身：' + (S.title || '登记') + (S.who ? '（' + S.who + '问的）' : '') + (cols.length ? '｜' + cols.join('｜') : '') + (isk && S.blank && S.blank.line ? '｜' + clean(S.blank.line) : ''));
    const sk = (F.skills || []).concat(F.skill2 ? [clean(F.skill2)] : []);
    L.push('这一段的本事：' + (sk.length ? sk.join('、') + (iskIn ? '（原来的世界带来的本事，照这一纪的叫法记的。这一纪的地方和人还没经过，往后想往这边长）' : '') : '未选择（由 AI 照这一纪的本事和我的来处定一个方向）'));
    L.push(...ownCredLines());          // 11-26 前半生自己写的那几章，一章一行，末了一行说明；没有自述的一行不添
    if (isk) {
      const gf = giftOf();
      L.push('神殿赐物：' + (gf ? gf.n + '（' + gf.r + (gf.kind === 'relic' ? '，遗物，原主已经不在了' : '') + '）：' + clean(gf.d) + '　效果：' + clean(gf.e) + (gf.note ? '　' + clean(gf.note) : '') + (gf.kind === 'relic' ? '　（所印数值为启源档，随持有者位阶折算，武具入装备格写 名〔品阶·类型·×修正〕）' : '') : (df['神殿赐物'] || '未选择（拒绝了她的馈赠）')));
    }
    if (F.statMode === 'later' || !F.stats) L.push('六维：未分配（由 AI 按胎骨、起点与出身补全，开场一句话说明）');
    else {
      const c = caps(), B = budget(), tot = statTotal();
      L.push('六维（起点给的底子＋自由分配）：' + STAT.map(([k]) => `${k} ${F.stats[k]}（上限${c[k]}）`).join(' / '), `当前分配：${tot}/${B}｜六维总上限：${capSum(c)}${F.statMode === 'cap' ? '｜同阶满溢开局' : ''}`, '属性经验：各项从0起，阈值＝属性×100｜潜力：各项100%（建档起点，下限10%，上不封顶）', `单项上限依据：${tg}位阶（单项基础上限${tt[2]}）`);
    }
    L.push('攻防与装备：建档未写定，首轮照骨架的算法结算 ATK、PV、DV，主手、副手写 名〔品阶·类型·×修正〕，甲写 名〔品阶·轻/中/重·耐久%〕，没有就写无｜' + (isk ? '开局只有穿越时身上那一套' + (giftOf() ? '和神殿赐物' : '') + '，没有别的兵器' : '照起点与' + (BS.book === 'moon' ? '兵器' : '命路') + '配一套跟这一纪相称的装备，开场一句话说明'));
    L.push('【面板状态】' + (BS.book === 'maze' && panelOn() ? (isk ? (iskLine ? '尚未觉醒，开局照主线一幕的地方起头，等到了有公会书记的地方再领旅印、觉醒面板。' : '尚未觉醒，开局先去公会登记、觉醒面板。') : (tk === '启源·初识' ? '尚未觉醒，开局先去公会完成成年登记与面板觉醒。' : '已觉醒，以上为已生效的面板。')) : '这一年没有面板，位阶、六维和命星照旧在底座里记，这一纪的人看不见。'), '');
    // 七
    let where;
    if (BS.free) { const MP = mapNow(), pin = MP && F.placeI != null ? MP.pins.find((q) => q.i === F.placeI) : null; where = `${era}${y}年，${pin ? pin.name + '（' + clean(pin.where || '') + '）' : (F.place ? clean(F.place) : '那一年一处寻常的地方')}（${FR.label || '自己报的年份'}，照那一年的时段总纲和地点起头）`; }
    else if (m.site) where = `${era}${yT}，${m.site}${m.ti ? '（' + clean(m.ti) + '）' : ''}（此刻，主线不预设，照迷宫纪1001年的常驻和这一处的地点起头）`;          // 11-24 此刻那一本挑的起点（1001 页建档器的降临地）
    else where = `${era}${yT}，${m.title ? m.title + '，' : ''}主线「${line}」的开局`;
    L.push('【七·现在何处】', '现在所在：' + where, '当前处境：' + (isk ? '刚从死之神殿落下来，身上只有穿越时那一身' + (giftOf() ? '，和她给的' + giftOf().n : '') + '。' + (iskLine ? iskLand(m) : '') : '这一纪生下来的人，从' + (BS.free ? '自己报的那一年' : m.site ? '这一处' : '这一条主线的开局') + '起头。' + (soul === 'reborn' ? '没有人知道，我其实已经活过一次了。' : '')));
    const si = sealInfo();
    let seal;
    if (si.kind === 'none') seal = si.cred;
    else if (si.kind === 'roll') seal = '无（这一纪没有旅印，墙上认军册，名字、姓或家、族三栏见出身那一行）' + (F.wall ? '｜守的那一段 ' + clean(F.wall) : '');
    else if (si.kind === 'team') seal = '无（这一纪没有旅印）｜' + (F.team ? '团 ' + clean(F.team) : '还没有团') + (si.guild ? '｜行会的档次 ' + (F.grade && TEAM_GRADES.includes(F.grade) ? F.grade : '没挂号') : '');
    else if (si.kind === 'grade') seal = (si.stone ? '白石旅印' : '山铜旅印') + '（不分阶）｜公会的档次 ' + (F.grade && GRADES.includes(F.grade) ? F.grade : '还没入会') + (si.gua ? '｜担保 ' + ((F.sheet || {})['谁担保'] ? clean(F.sheet['谁担保']) : '未写') : '');
    else { const r = isk ? '无印' : (F.rank || rankDefault()); seal = r + (r === '无印' ? (isk ? '（未登记）' : '（尚未登记）') : ''); }
    L.push('旅印：' + seal, '');
    // 八
    const wish = F.wish ? clean(F.wish) : (F.wishPick ? F.wishPick + '：' + (((WISH[BS.book] || []).concat(WISH_ALL)).find((x) => x[0] === F.wishPick) || ['', ''])[1] : '');
    L.push('【八·冒险初心】', wish || '还没想好（先走着看，头一轮不必追问）', '', optLine(), '', fm.tail || '开始游戏。');          // 11-28 开局档位那一行在“开始游戏。”前头
    L.push('', ENTRY_CRED[entryOf()]);          // 11-26 首轮入局：末尾一行，别的行照旧
    return L.join('\n');
  }

  /* ---------- 点和填 ---------- */
  const tapAfter = (a, v) => { const el = $b(`.bx-body [data-a="${a}"][data-v="${String(v).replace(/["\\]/g, '\\$&')}"]`); if (el) tapGlow(el); };
  function keep(k, v) {
    const st = $b('.bx-stage'), sc = st ? st.scrollTop : 0;
    BS.focus = k ? { k, v } : null;
    if (!k) root().classList.remove('sheet');          // 11-25：手机上“再看看”收了说明，暗幕也跟着收（原来要再点一下才散）
    renderRail();
    if (BS.mode === 'life') lifeRender(false); else renderStep(false);
    if (st) st.scrollTop = sc;
    renderSide(); idUpdate();
    if (k && isM() && !(k === 'race' && BS.lift)) root().classList.add('sheet');          // 手机上翻过来的那张牌背面就是支系，先不盖说明
  }
  const refresh = () => keep(BS.focus ? BS.focus.k : null, BS.focus ? BS.focus.v : null);
  const menuOn = (on) => { const x = root(); if (!x) return; x.classList.toggle('menu', on); const b = $b('.bx-mn'); if (b) b.setAttribute('aria-expanded', String(on)); };
  const unquote = (ls) => ls.map((l) => String(l).replace(/^「|」$/g, ''));
  function wire() {
    buildEl.onclick = (e) => {
      const x = root();
      if (x && x.classList.contains('menu') && !e.target.closest('.bx-mn')) {          // “…”开着：点外头只是收起来，点里头的钮收起来再照常走
        menuOn(false);
        if (!e.target.closest('.bx-mp')) return;
      }
      if (x && x.classList.contains('idopen') && !BX.minting && e.target.closest('.bx-aside') && !e.target.closest('.bx-id,[data-a]')) { x.classList.remove('idopen'); return; }          // 手机上浮出整张身份牌：点牌外头的暗处也收起
      const t = e.target.closest('[data-a]'); if (!t || t.disabled || t.getAttribute('aria-disabled') === 'true') return;
      const a = t.dataset.a, v = t.dataset.v;
      if (BX.busy && !/^(unfocus|idopen|idclose|rclose|rcopy|rfill|rkind|out|menu|say|hdp)$/.test(a)) return;
      poke();
      if (F._pre) { const pn = { tier: 5, stat: 6, sdec: 6, sinc: 6, oath: 9, skill: 9, wish: 10, pin: 10 }[a]; if (pn) delete F._pre[pn]; }          // 在那一步自己动过的，就不再说是照前半生填的
      switch (a) {
        case 'menu': menuOn(!x.classList.contains('menu')); return;
        case 'say': if (isM()) t.classList.toggle('open'); return;
        case 'hdp': if (isM()) t.classList.toggle('open'); return;
        case 'out': hide(buildEl); clearTimeout(BX.idleT); if (frame) { bookHide(false); tableOn(false); } else toTable(); return;
        case 'way': F.lifeOn = v === 'life' && F.soul !== 'isekai'; F._route = 'direct'; go(Math.min(F._step || 1, F._max || 1)); return;
        case 'route': {          // 顶上那一枚：翻、不翻前半生随时换。已经过了胎骨的，翻就从降生那一章起；在那几章里说不翻，接着往金血走
          F.lifeOn = !lifeActive();
          if (F.lifeOn && BS.mode === 'step' && BS.step >= 4) { lifeGo(0); speak(LINES.lifeOn); return; }
          if (!F.lifeOn && BS.mode === 'life') { go(afterLife()); speak(LINES.lifeOff); return; }
          renderRail(); speak(F.lifeOn ? LINES.lifeOn : LINES.lifeOff); return;
        }
        case 'resume': openResume(); return;
        case 'rkind': RS.kind = v; for (const b of $$b('[data-a="rkind"]')) b.setAttribute('aria-pressed', String(b.dataset.v === v)); return;
        case 'rcopy': resumeOut(false); return;
        case 'rfill': resumeOut(true); return;
        case 'rclose': { const p = $b('.bx-pop'); if (p) p.remove(); return; }
        case 'step': { const n = +v; if (n > (F._max || 1)) return; const e2 = n > 2 ? check(2) : ''; if (e2) { flashErr(e2); go(2); return; } if (BS.step === 11 && n !== 11) unMint(); go(n); return; }
        case 'lifeat': lifeGo(+v); return;
        case 'prev': if (BS.focus && isM() && root().classList.contains('sheet')) { root().classList.remove('sheet'); return; } prev(); return;
        case 'next': if (BS.focus) { const ok = commitFocus(); if (ok === false) return; } next(); return;
        case 'unfocus': BS.lift = null; if (isM() && root().classList.contains('sheet') && t.classList.contains('bx-dim')) { root().classList.remove('sheet'); return; } keep(null); return;
        case 'idopen': root().classList.add('idopen'); return;
        case 'idclose': root().classList.remove('idopen'); return;
        case 'soul': case 'lsoul': F.soul = v; if (!isGoldSoul()) { F.goldN = ''; } keep(a === 'soul' ? 'soul' : null, v); tapAfter(a, v); popId(); speak(unquote(SOUL[v].say)); return;
        case 'sex': F.sex = v; for (const b of $$b('[data-a="sex"]')) b.setAttribute('aria-pressed', String(b.dataset.v === v)); { const o = $b('[data-f="sexOther"]'); if (o) o.hidden = v !== '自定义'; } return;
        case 'per': { const p = (BS.E.periods || []).find((x) => x.id === v); if (p) { const y = Math.max(p.from, BS.FR.from); F.year = String(y); yearChanged(); } return; }
        case 'tofree': F.free = !BS.free; if (F._route && (F._step || 1) > 2) F._step = 2; startBuild(BS.m); return;          // 换了拿不拿车票，回第二步报年份（或者看车票的那一年）
        case 'race': raceLift(t, v); return;
        case 'sub': pickSub(v); return;
        case 'kin': F.kin = F.kin === v ? '' : v; keep('race', F.race); return;
        case 'pcm': F.pcMode = v; refresh(); return;
        case 'body': F.build = F.build === v ? '' : v; refresh(); return;
        case 'gold': F.goldN = v; keep('gold0', v); tapAfter(a, v); return;
        case 'god': if (!t.classList.contains('off')) F.goldN = v; keep('god', v); tapAfter(a, v); popId(); return;
        case 'entry': {          // 11-26 铸印那一步：先听前半生还是径直推门，不重画（还想让她知道的那一格照旧）
          F.entry = v === 'open' ? 'open' : 'life';
          for (const b of $$b('[data-a="entry"]')) b.setAttribute('aria-pressed', String(b.dataset.v === entryOf()));
          const nt = $b('.b2-entry .b2-note'); if (nt) nt.textContent = ENTRY_NOTE[entryOf()];
          speak(LINES[11][entryOf()]); return;
        }
        case 'opt': {          // 11-28 开局的档位：不重画，只翻这一组的钮
          const i = v.indexOf('|'), k = v.slice(0, i), val = v.slice(i + 1);
          F.opt = F.opt || {}; F.opt[k] = val;
          for (const b of $$b(`[data-a="opt"][data-v^="${k}|"]`)) b.setAttribute('aria-pressed', String(b.dataset.v === k + '|' + optOf(k)));
          return;
        }
        case 'know': F.goldKnow = +v; for (const b of $$b('[data-a="know"]')) b.setAttribute('aria-pressed', String(b.dataset.v === v)); return;
        case 'tier': F.tier = v; F.statKey = ''; keep('tier', v); tapAfter(a, v); popId(); return;
        case 'stat': if (v === 'roll') rollDice(); else setStatMode(v); return;
        case 'sdec': case 'sinc': { if (!F.stats) return; const d = a === 'sinc' ? 1 : -1; if (d > 0 && statTotal() >= budget()) return; setStat(v, (F.stats[v] || 1) + d); return; }
        case 'path': F.path = v; keep('path', v); tapAfter(a, v); popId(); return;
        case 'weapon': case 'armor': case 'marts': case 'school': F[a] = F[a] === v ? '' : v; keep('mitem', a + '|' + v); tapAfter(a, v); return;
        case 'pool': BS.pool = v; keep(null); return;
        case 'draw': redrawStars(v); return;
        case 'star': keep('star', v); tapAfter(a, v); return;          // 11-25：点一张只是翻开来看，留不留在说明里定
        case 'sview': keep('star', v); return;
        case 'tray': keep('tray', v); return;
        case 'skeep': case 'shold': case 'sdrop': { const [k, id] = v.split('|'); starDo(a.slice(1), k, id); return; }
        case 'sreset': starDo('reset', v); return;
        case 'sct': { const [k, x] = v.split('|'); F['sc' + k + 't'] = x; focusOn('star', k + '|*', false); return; }
        case 'scr': { const [k, x] = v.split('|'); F['sc' + k + 'r'] = x; focusOn('star', k + '|*', false); return; }
        case 'oath': F.oath = F.oath === v ? '' : v; keep('oath', v); tapAfter(a, v); popId(); return;
        case 'skill': { const s = F.skills = F.skills || []; const i = s.indexOf(v); if (i >= 0) s.splice(i, 1); else { if (s.length >= 2) return; s.push(v); } t.setAttribute('aria-pressed', String(i < 0)); return; }
        case 'regift': drawGifts(); F.giftN = ''; keep(null); return;
        case 'gift': F.giftN = v; keep('gift', v); tapAfter(a, v); return;
        case 'pin': if (BS.free) { F.placeI = +v; F.place = ''; } keep('pin', v); if (BS.free) { const s = $b('.bx-pinseal'); if (s && !RMo()) s.classList.add('drop'); } return;
        case 'wish': F.wishPick = F.wishPick === v ? '' : v; keep('wish', v); return;
        case 'grade': F.grade = v; refresh(); return;
        case 'rank': F.rank = v; refresh(); return;
        case 'lpick': { const [k, i] = v.split('|'); F._life.picks[k] = F._life.picks[k] === +i ? null : +i; keep(null); tapAfter(a, v); const o = lifeOpt(k); if (o && o.say) speak([o.say]); return; }
        case 'lown': {          // 11-26 自己写：点开两格，再点退回去挑牌（写的字留着）
          const on = !isOwn(v); F._life.picks[v] = on ? 'own' : null; ownOf(v); keep(null); speak(on ? LINES.own.in : LINES.own.off);
          const w = $b('.bx-lown'); if (w && on) { stageTo(w, isM() ? 'start' : 'nearest'); if (!isM() && matchMedia('(hover:hover)').matches) { const ta = $b('.bx-lown [data-own="e"]'); if (ta) ta.focus({ preventScroll: true }); } }
          return;
        }
        case 'ltag': {
          const [k, kind, val] = v.split('|'), o = ownOf(k), r = tagToggle(o.g, kind, val);
          if (r.err) { speak(LINES.own.two); tapGlow(t); return; }
          o.g = r.g; const ta = $b(`.bx-lown [data-own="g"]`); if (ta) { ta.value = o.g; if (kind === 'get') { ta.focus({ preventScroll: true }); ta.setSelectionRange(ta.value.length, ta.value.length); if (isM()) ownKeep(ta); } }
          ownSync(k); if (ownOver(k)) speak(LINES.own.over); return;
        }
        default:
      }
    };
    buildEl.oninput = (e) => {
      const t = e.target;
      if (t.dataset.own) { ownOf(t.dataset.v)[t.dataset.own] = t.value; ownSync(t.dataset.v); return; }          // 11-26 前半生自己写的两格
      if (F._pre) { const pn = t.dataset.sheet ? 9 : t.dataset.a === 'sn' ? 6 : /^(wish|place)$/.test(t.dataset.f || '') ? 10 : 0; if (pn) delete F._pre[pn]; }
      if (t.dataset.f) {
        F[t.dataset.f] = t.value;
        if (t.dataset.f === 'year') { yearChanged(true); return; }
        if (/^(name|age|world|art|face)$/.test(t.dataset.f)) idUpdate();
        if (/^(art|face)$/.test(t.dataset.f)) { clearTimeout(BX.pcT); BX.pcT = setTimeout(() => { const w = $b('.b2-pcw'); if (w) w.innerHTML = pcPreviewHTML(); }, 350); }
        if (t.dataset.f === 'place' && t.value) { F.placeI = null; for (const b of $$b('[data-a="pin"]')) { b.classList.remove('on'); if (b.hasAttribute('aria-pressed')) b.setAttribute('aria-pressed', 'false'); } const s = $b('.bx-pinseal'); if (s) s.remove(); }
        return;
      }
      if (t.dataset.sheet) { (F.sheet = F.sheet || {})[t.dataset.sheet] = t.value; return; }
      if (t.dataset.a === 'yr') { F.year = t.value; const yi = $b('#b2-year'); if (yi) yi.value = t.value; yearChanged(false, true); return; }
      if (t.dataset.a === 'sn') { if (t.value === '') return; setStat(t.dataset.v, parseInt(t.value, 10) || 1); }
    };
    buildEl.onkeydown = (e) => { if (e.key === 'Escape') { if (root().classList.contains('menu')) { menuOn(false); return; } if ($b('.bx-pop')) { $b('.bx-pop').remove(); return; } if (root().classList.contains('idopen')) { root().classList.remove('idopen'); return; } if (BS.focus || BS.lift) { BS.lift = null; keep(null); } } };
  }
  /* 换年份（自己报年份的时候）：年代、能选的族、本事、命路的亮灭、神亲、命星池都跟着变 */
  function yearChanged(fromInput, fromSlider) {
    renderRail();
    const note = () => { const n = $b('.b2-when .b2-note'), y = oyear(), Pn = periodAt(y); if (n) n.innerHTML = y != null && Pn ? `<b>${esc(BS.era)} ${esc(yText(y))} · ${esc(Pn.name)}</b>　${esc(clean(Pn.note || ''))}` : esc(clean((BS.FR || {}).note || '')); return Pn; };
    if (fromSlider) { note(); idUpdate(); return; }
    if (fromInput) {
      const Pn = note(), y = oyear();
      for (const b of $$b('.b2-stop')) b.classList.toggle('on', !!Pn && b.dataset.v === Pn.id);
      const r = $b('[data-a="yr"]'); if (r && Pn) { r.min = Math.max(Pn.from, BS.FR.from); r.max = Math.min(Pn.to, BS.FR.to); r.value = y; }
      idUpdate();
      return;
    }
    refresh();
  }
  /* 下面那一枚主钮：点开的那一张就是要的那一张 */
  function commitFocus() {
    const f = BS.focus; if (!f) return true;
    if (f.k === 'god') { const g = godsNow().find((x) => x.n === f.v); if (!g || g.off) { keep(null); return false; } F.goldN = f.v; }
    if (f.k === 'pin' && BS.free) { F.placeI = +f.v; F.place = ''; }
    if (f.k === 'star') {          // 翻开的是还没留的一颗（台面上的、候星里的、自己写的）：主钮是留下它，留完停在这一步
      const [k, id] = String(f.v).split('|'), at = id === '*' ? (F['star' + k] === '*' ? 'keep' : 'hand') : starAt(k, id);
      if (at === 'hand' || at === 'hold') { starDo('keep', k, id); return false; }
    }
    return true;
  }
  /* 命星那一步的几个动作：留下、放进候星、撤下、落星归叠。做完收起说明（摊着“手边的星”的时候留着它），她说一句 */
  function starDo(act, k, id) {
    if (!STAR_KINDS.includes(k)) return;
    const L = LINES[8]; let say = null;
    if (act === 'keep') {
      const had = F['star' + k], went = starKeep(k, id);
      if (F['star' + k] !== id) return;
      const left = STAR_KINDS.filter((q) => !F['star' + q]);
      say = !left.length ? ['三颗都留了，往下走吧。'] : ['留这一颗。', left.map((q) => KIND_CN[q]).join('和') + '那一叠还没挑。'];
      if (had && had !== '*' && went) say = ['换这一颗。', went === 'hold' ? L.swapHold : went === 'back' ? L.swapBack : L.swapTable];
      BX.trayPop = 'kp';
    } else if (act === 'hold') {
      const r = starHold(k, id);
      if (r === 'full') { speak(L.full); pop($b('.bx-tray .sum')); pop($b('.bx-tray .hc')); return; }
      if (r !== 'ok') return;
      say = L.hold; BX.trayPop = isM() ? 'sum' : 'hc';
    } else if (act === 'drop') {
      const r = starDrop(k, id); if (!r) return;
      say = r === 'table' ? L.free : L.drop; BX.trayPop = r === 'gone' ? 'gn' : 'kp';
    } else if (act === 'reset') {
      const n = starReset(k);
      say = n ? L.reset : L.reset0; BX.trayPop = 'gn';
    } else return;
    const inTray = BS.focus && BS.focus.k === 'tray';
    if (!inTray) root().classList.remove('sheet');
    if (BS.mode === 'step' && BS.step === 8) { if (inTray) keep('tray', k); else keep(null); } else idUpdate();
    if (act === 'keep' || act === 'drop' || act === 'hold') popId();
    if (act === 'keep') tapAfter('star', k + '|' + id);
    speak(say);
  }
  function setStatMode(v) {
    if (v === 'later') { F.statMode = F.statMode === 'later' ? 'even' : 'later'; if (F.statMode !== 'later') { F.statKey = ''; } refresh(); return; }
    const c = caps();
    if (v === 'even') { F.statMode = 'even'; F.stats = balanced(); }
    if (v === 'roll') { F.statMode = 'roll'; F.stats = rolled(); }
    if (v === 'cap') { F.statMode = 'cap'; F.stats = Object.fromEntries(STAT.map(([k]) => [k, c[k]])); }
    F.statKey = statKey(); refresh();
  }

  /* ---------- 胎骨：点一张，挪到正中翻过来；挑了支系，牌飞进右边那一格 ---------- */
  async function raceLift(el, v) {
    if (F.race !== v) { F.sub = ''; F.kin = ''; }
    F.race = v; F.statKey = '';
    if (!RMo() && !isM() && el.getBoundingClientRect().width) {
      BX.busy = true;
      const st = $b('.bx-stage').getBoundingClientRect(), r = el.getBoundingClientRect();
      const s = Math.min(3, (st.height * 0.8) / r.height, 300 / r.width);
      el.classList.add('lifting'); el.style.transition = 'transform .5s cubic-bezier(.2,.75,.2,1)'; el.style.zIndex = 90;
      el.style.transform = `translate(${st.left + st.width / 2 - (r.left + r.width / 2)}px,${st.top + st.height * 0.5 - (r.top + r.height / 2)}px) scale(${s})`;
      await T(520);
      BX.busy = false;
    }
    BS.lift = v;
    keep('race', v);
    const big = $b('.bx-focus .bx-race');
    if (big && !RMo()) { big.classList.remove('up'); void big.offsetWidth; requestAnimationFrame(() => big.classList.add('up')); }
    await T(560);
    const R = raceOf(v); speak([R.name + '。往下看，哪一支？', R.arrive && F.soul === 'isekai' ? clean(R.arrive).split('，').slice(0, 2).join('，') + '。' : '']);
  }
  async function pickSub(v) {
    F.sub = F.sub === v ? '' : v; F.kin = ''; F.statKey = '';
    const big = $b('.bx-focus .bx-race');
    if (F.sub && big && !RMo()) {
      BX.busy = true;
      big.classList.remove('up'); await T(420);
      const nb = (isM() ? $b('.bx-idm .th') : $b('.bx-id .niche')).getBoundingClientRect(), r = big.getBoundingClientRect();
      big.style.transition = 'transform .55s cubic-bezier(.4,.1,.3,1),opacity .55s';
      big.style.transform = `translate(${nb.left + nb.width / 2 - (r.left + r.width / 2)}px,${nb.top + nb.height / 2 - (r.top + r.height / 2)}px) scale(${nb.width / r.width})`;
      big.style.opacity = '.2';
      await T(560);
      BX.busy = false;
    }
    if (F.sub) BS.lift = null;
    keep('race', F.race); popId();
    if (F.sub) speak(LINES[3].done);
  }

  /* ---------- 命星：收回去，再抽十张 ---------- */
  const deckAt = () => { const d = $b('.bx-deck'); if (!d) return null; const r = d.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; };
  async function redrawStars(k) {
    if (!STAR_KINDS.includes(k)) return;
    const D = starZ(k);
    if (!starDeck(k).length) {          // 星叠空了：台面不动，告诉他让落星归叠
      speak(D.gone.length ? LINES[8].dry : LINES[8].dry0);
      pop($b('.bx-tray .rs')); const dn = $b('.bx-dry'); if (dn) { pop(dn); if (dn.scrollIntoView) dn.scrollIntoView({ block: 'nearest' }); }
      return;
    }
    const dn = Math.min(10, starDeck(k).length);          // 星叠里不足十张的时候，她那一句照实数说
    speak(D && D.n >= 1 ? LINES[8].redraw.map((s) => s.replace('十张', NUM[dn] + '张')) : ['再抽一回。']);
    // 没留的往落星那一格落下去，留下的那一张收到“留下”那一格
    const at = (sel) => { const e = $b(sel); if (!e) return null; const r = e.getBoundingClientRect(); return r.width ? { x: r.left + r.width / 2, y: r.top + r.height / 2 } : null; };
    const cards = $$b('.bx-slots .bx-star:not(.cus)'), gn = at('.bx-tray .gn') || deckAt(), kp = at('.bx-tray .kp') || gn, keptV = k + '|' + (F['star' + k] || '');
    if (cards.length && gn && !RMo()) {
      BX.busy = true;
      cards.forEach((c) => { const to = c.dataset.v === keptV ? kp : gn; c.classList.remove('lit', 'on'); const r = c.getBoundingClientRect(); c.style.transition = 'transform .45s cubic-bezier(.4,.1,.3,1),opacity .45s'; c.style.transform = `translate(${to.x - (r.left + r.width / 2)}px,${to.y - (r.top + r.height / 2)}px) scale(.3)`; c.style.opacity = '.15'; });
      await T(460);
      BX.busy = false;
    }
    drawStars(k);
    BX.trayPop = 'gn';
    BS.focus = null; root().classList.remove('sheet'); renderSide();
    const st = $b('.bx-stage'), sc = st ? st.scrollTop : 0;
    renderStep(true); if (st) st.scrollTop = sc;
  }

  /* ---------- 前半生（11-26 并成一条路）：十一步照走，翻前半生的在胎骨之后多五章（降生、家、孩童、少年、启程），
     一章几张牌加一条“自己写”。翻完了照选的替后面几步先填（起点、六维、誓心与出身、初心），那几步照样走到、能改；凭证里多一节前半生 ---------- */
  const LIFE_NAME = { birth: '降生', home: '家', child: '孩童', youth: '少年', depart: '离家' };          // 末一章原叫启程，凭证里“启程”两个字会叫醒各纪的路程规则，改叫离家
  const LIFE_LA = { birth: 'CAPUT I · NATIVITAS', home: 'CAPUT II · DOMUS', child: 'CAPUT III · PUERITIA', youth: 'CAPUT IV · ADOLESCENTIA', depart: 'CAPUT V · PROFECTIO' };
  const LIFE_IMG = { birth: 'life_birth', home: 'life_home', child: 'life_child', youth: 'life_youth', depart: 'life_depart' };
  const LIFE_SAY = {};
  const lifeList = () => ['birth', 'home', 'child', 'youth', 'depart'];
  const lifeActive = () => !!F.lifeOn && F.soul !== 'isekai';          // 翻前半生：开头那一问答了翻，而且不是整个人掉进来的
  const afterLife = () => (isGoldSoul() ? 4 : 5);
  function lifeGroup() {
    const G = ((DATA.life && DATA.life.eras) || {})[BS.vis === 'now' ? 'now' : BS.book] || [], y = oyear();
    return G.find((g) => y != null && (g.from == null || g.from <= y) && (g.to == null || y <= g.to)) || G[0] || null;
  }
  const optOn = (o) => { const y = oyear(); return !!o && (y == null || ((o.from == null || o.from <= y) && (o.to == null || y <= o.to))); };
  const lifeOpt = (k) => { const G = lifeGroup(), i = F._life && F._life.picks ? F._life.picks[k] : null; const o = G && i != null && G[k] ? G[k][i] || null : null; return optOn(o) ? o : null; };
  function lifeStart() {          // 走查和旧入口用：照开头答了“翻”，从降生那一章起
    if (F.soul === 'isekai') { flashErr('你是整个人掉进来的，这一纪没有你的前半生。'); return; }
    F.soul = F.soul || 'native'; F.lifeOn = true;
    F._life = F._life || { i: 0, max: 0, picks: {} };
    lifeGo(F._life.i || 0);
  }
  async function lifeGo(i, first) {
    if (BX.busy) return;
    F._life = F._life || { i: 0, max: 0, picks: {} };
    const L = lifeList(); i = Math.max(0, Math.min(L.length - 1, i));
    const enter = first || BS.mode !== 'life' || i !== F._life.i;
    if (!first && enter) await sweepOut();
    unMint();
    BS.mode = 'life'; F._route = 'life'; F._life.i = i; F._life.max = Math.max(F._life.max || 0, i); BS.focus = null; BS.lift = null;
    validate();
    renderRail(); lifeRender(enter); renderSide(); idUpdate();
    const st = $b('.bx-stage'); if (st && enter) st.scrollTop = 0;
    if (enter) { const G = lifeGroup() || {}; speak((G.say || {})[L[i]] || LIFE_SAY[L[i]] || []); poke(); }
  }
  function lifeOpts(k) {
    const G = lifeGroup() || {}, os = (G[k] || []).map((o, i) => [o, i]).filter(([o]) => optOn(o)), pk = F._life.picks[k];
    if (!os.length) return '<p class="b2-note">这一段的手记还没写到这一页，翻过去，开局由她补上。</p>' + (OWN_K.includes(k) ? `<div class="bx-lopts">${ownHTML(k)}</div>` : '');
    return `<div class="bx-lopts">${os.map(([o, i]) => `<button type="button" class="bx-lopt${pk === i ? ' picked' : ''}" data-deal data-a="lpick" data-v="${k}|${i}" aria-pressed="${pk === i}"><b>${esc(o.t)}</b><span>${esc(o.d)}</span>${pk === i && lifeGain(o) ? `<small>${esc(lifeGain(o))}</small>` : ''}</button>`).join('')}${OWN_K.includes(k) ? ownHTML(k) : ''}</div>`;
  }
  /* 11-26 前半生“自己写”：牌底下多一条，点开是经历、收获两格（F.lifeOwn 跟人走，换一纪、翻回去都还在）。
     选了的那一章 F._life.picks[k] = 'own'；凭证里这一章另起一行“前半生·家：（自述）经历 ……｜收获 ……”，没有自述的凭证一个字不变 */
  const OWN_K = ['birth', 'home', 'child', 'youth', 'depart'];
  const OWN_MAX = { e: 200, g: 100 };
  const OWN_PH = { birth: '比如 生在哪里，那一年家里、城里出了什么事', home: '比如 家里做的是什么，谁把你带大，屋里常有什么人来', child: '比如 小时候常往哪里跑，闯过什么祸，记得最清楚的一件事', youth: '比如 十几岁接的头一件活，跟谁学的手艺，吃过什么亏', depart: '比如 出门那天做成过什么，为什么非走不可，谁送你到路口' };
  const ownOf = (k) => { F.lifeOwn = F.lifeOwn || {}; return (F.lifeOwn[k] = F.lifeOwn[k] || { e: '', g: '' }); };
  const ownLen = (s) => Array.from(String(s || '').trim()).length;
  const ownFilled = (k) => { const o = (F.lifeOwn || {})[k]; return !!o && (ownLen(o.e) > 0 || ownLen(o.g) > 0); };
  const ownOver = (k) => { const o = (F.lifeOwn || {})[k]; return !!o && (ownLen(o.e) > OWN_MAX.e || ownLen(o.g) > OWN_MAX.g); };
  const isOwn = (k) => !!F._life && F._life.picks && F._life.picks[k] === 'own';
  const lifeHas = (k) => { const p = F._life && F._life.picks ? F._life.picks[k] : null; return p === 'own' ? ownFilled(k) : p != null; };
  const ownLine = (s) => clean(String(s || '').replace(/[｜|]/g, '，').replace(/\s*[\r\n]+\s*/g, ' ').replace(/\s{2,}/g, ' '));
  // 收获那一格的小签：照这一章几张牌的属性、本事挑（起步那一档只在启程这一章有），点了往收获里添，再点撤掉
  function ownTags(k) {
    const G = lifeGroup() || {}, os = (G[k] || []).filter(optOn), out = [];
    const sts = STAT.map(([s]) => s).filter((s) => os.some((o) => o.st && o.st[s] > 0));
    for (const s of sts) out.push(['st', STAT_CN[s], '偏' + STAT_CN[s]]);
    const P = curP(), y = oyear(), ok = (P.skills || []).map((s) => (typeof s === 'string' ? { s } : s)).filter((s) => visible(s, y)).map((s) => s.s), sk = [];
    for (const o of os) for (const h of o.sk || []) { const hit = ok.find((s) => s.indexOf(h) >= 0 && !sk.includes(s)); if (hit && sk.length < 6) sk.push(hit); }
    for (const s of sk) out.push(['sk', s, '会：' + s]);
    if (k === 'depart') for (const o of os) if (o.tier && TIERS.some((t) => t[0] === o.tier) && !out.some((t) => t[1] === o.tier)) out.push(['tier', o.tier, '从' + o.tier + '起步']);
    out.push(['get', '', '得了一样东西']);
    return out;
  }
  // 收获写成“偏力量、体魄 · 会：探路先锋 · 得了：……”这样几截，小签只动它认得的那一截，别的字原样留着
  const gainSegs = (g) => String(g || '').split(/\s+·\s+/).map((s) => s.trim()).filter(Boolean);          // 几截之间是“ · ”（两边带空格），从启源·初识起步里那一点不算
  const segHead = (s) => (/^偏/.test(s) ? 'st' : /^会[：:]/.test(s) ? 'sk' : /^从.+起步$/.test(s) ? 'tier' : /^得了[：:]?/.test(s) ? 'get' : '');
  const segItems = (s, kind) => (kind === 'st' ? s.slice(1) : kind === 'sk' ? s.replace(/^会[：:]/, '') : s).split(/[、，,\s]+/).filter(Boolean);
  function tagOn(g, kind, v) {
    const seg = gainSegs(g).find((s) => segHead(s) === kind);
    if (!seg) return false;
    if (kind === 'tier') return seg === '从' + v + '起步';
    if (kind === 'get') return true;
    return segItems(seg, kind).includes(v);
  }
  function tagToggle(g, kind, v) {
    const segs = gainSegs(g), i = segs.findIndex((s) => segHead(s) === kind);
    if (kind === 'get') { if (i < 0) segs.push('得了：'); return { g: segs.join(' · ') }; }
    if (kind === 'tier') { const s = '从' + v + '起步'; if (i < 0) segs.push(s); else if (segs[i] === s) segs.splice(i, 1); else segs[i] = s; return { g: segs.join(' · ') }; }
    const items = i < 0 ? [] : segItems(segs[i], kind), j = items.indexOf(v);
    if (j >= 0) items.splice(j, 1);
    else { if (kind === 'st' && items.filter((x) => Object.values(STAT_CN).includes(x)).length >= 2) return { g, err: 'two' }; items.push(v); }
    const seg = items.length ? (kind === 'st' ? '偏' + items.join('、') : '会：' + items.join('、')) : '';
    if (i < 0) { if (seg) segs.push(seg); } else if (seg) segs[i] = seg; else segs.splice(i, 1);
    return { g: segs.join(' · ') };
  }
  // 自述的收获里门面认得出的几样（偏哪两样、会哪样本事、从哪一级起步），照一张牌的分量折进六维、本事、起点
  function ownParse(k) {
    const o = (F.lifeOwn || {})[k] || {}, g = String(o.g || ''), st = {}, sk = [];
    const CN = {}; for (const [s] of STAT) CN[STAT_CN[s]] = s;
    for (const m of g.matchAll(/偏([^·｜。；\n]*)/g)) for (const w of m[1].split(/[、，,和与\s]+/)) if (CN[w] && Object.keys(st).length < 2) st[CN[w]] = 1;
    const P = curP(), y = oyear(), ok = (P.skills || []).map((s) => (typeof s === 'string' ? { s } : s)).filter((s) => visible(s, y)).map((s) => s.s);
    for (const m of g.matchAll(/会[：:]([^·｜。；\n]*)/g)) for (const w of m[1].split(/[、，,\s]+/)) if (ok.includes(w) && !sk.includes(w)) sk.push(w);
    const tm = g.match(/从(\S+?·\S+?)起步/), tier = tm && TIERS.some((t) => t[0] === tm[1]) ? tm[1] : '';
    return { st, sk, tier, own: true };
  }
  function ownCount(el, k, f) {
    const n = ownLen(ownOf(k)[f]), mx = OWN_MAX[f];
    el.textContent = n > mx ? `${n}/${mx}，多了 ${n - mx} 字` : `${n}/${mx}`;
    el.classList.toggle('over', n > mx);
  }
  function ownHTML(k) {
    const on = isOwn(k), o = ownOf(k), tags = ownTags(k), id = 'b2-own-' + k;
    const ts = tags.filter((t) => t[0] === 'st').slice(0, 2).map((t) => t[1]), tk = tags.find((t) => t[0] === 'sk');
    const gph = '比如 ' + [ts.length ? '偏' + ts.join('、') : '', tk ? '会：' + tk[1] : '', '得了：一样带得走的旧物'].filter(Boolean).join(' · ');
    const head = `<button type="button" class="bx-lownb" data-a="lown" data-v="${k}" aria-pressed="${on}" aria-expanded="${on}"><i aria-hidden="true"></i><b>自己写</b><span>${on ? '这一段照你写的记。再点一下，退回去挑牌。' : '牌上写的都不像你，这一段你自己说给她听。'}</span></button>`;
    if (!on) return `<div class="bx-lown" data-deal>${head}</div>`;
    const cnt = (f) => { const n = ownLen(o[f]), mx = OWN_MAX[f]; return `<small class="b2-cnt${n > mx ? ' over' : ''}" data-cnt="${f}" aria-live="polite">${n > mx ? `${n}/${mx}，多了 ${n - mx} 字` : `${n}/${mx}`}</small>`; };
    return `<div class="bx-lown picked" data-deal>${head}<div class="bx-lownf bx-paper">
<div class="b2-f"><label for="${id}-e">这一段的经历<small>几句话，${OWN_MAX.e}字以内</small></label><textarea id="${id}-e" rows="4" maxlength="${OWN_MAX.e * 2}" data-own="e" data-v="${k}" placeholder="${esc(OWN_PH[k] || '比如 那几年你在哪里、跟谁、做过什么')}">${esc(o.e)}</textarea>${cnt('e')}</div>
<div class="b2-f"><label for="${id}-g">这一段的收获<small>学会了什么、偏向哪两样、得了什么，${OWN_MAX.g}字以内</small></label>
<div class="b2-chips bx-ltags" role="group" aria-label="点一下填进收获">${tags.map(([t, v, txt]) => `<button type="button" data-a="ltag" data-v="${k}|${t}|${esc(v)}" aria-pressed="${t === 'get' ? 'false' : tagOn(o.g, t, v)}" class="t-${t}">${esc(txt)}</button>`).join('')}</div>
<textarea id="${id}-g" rows="2" maxlength="${OWN_MAX.g * 2}" data-own="g" data-v="${k}" placeholder="${esc(gph)}">${esc(o.g)}</textarea>${cnt('g')}</div>
<p class="b2-note">点上面的小签填进收获，也可以全自己写。认得出的几样照一张牌的分量记，别的开局由她照这一纪的规矩折算，不额外加强。</p>
</div></div>`;
  }
  function ownSync(k) {          // 打字、点小签以后：计数、小签亮灭、主钮的字跟着换，不重画（输入框的光标留着）
    const o = ownOf(k);
    for (const f of ['e', 'g']) { const c = $b(`.bx-lown [data-cnt="${f}"]`); if (c) ownCount(c, k, f); }
    for (const b of $$b('.bx-lown [data-a="ltag"]')) { const [, t, v] = b.dataset.v.split('|'); if (t !== 'get') b.setAttribute('aria-pressed', String(tagOn(o.g, t, v))); }
    const nb = $b('.bx-ctl [data-a="next"]'); if (nb && BS.mode === 'life') { const p = lifeHas(k) ? (k === 'birth' ? '记下这户人家' : '记下这一段') : '留白，往下翻'; nb.textContent = p; BS.primary = p; }
  }
  // 只挪中间那一格（.bx-stage）的滚动；scrollIntoView 会连外头 overflow:hidden 的框一起挪，手机上顶栏会被推出去
  function stageTo(el, where) {
    const st = el && el.closest('.bx-stage'); if (!st) return;
    const sr = st.getBoundingClientRect(), r = el.getBoundingClientRect(), pad = 10;
    let d = 0;
    if (where === 'start') d = r.top - sr.top - pad;
    else if (where === 'center') d = (r.top + r.height / 2) - (sr.top + sr.height / 2);
    else if (r.bottom > sr.bottom - pad) d = Math.min(r.bottom - sr.bottom + pad, r.top - sr.top - pad); else if (r.top < sr.top + pad) d = r.top - sr.top - pad;
    if (d) st.scrollTo({ top: st.scrollTop + d, behavior: RMo() ? 'auto' : 'smooth' });
  }
  function ownOverErr(k, jump) {
    const o = ownOf(k), f = ownLen(o.e) > OWN_MAX.e ? 'e' : 'g', n = ownLen(o[f]) - OWN_MAX[f];
    flashErr(`${LIFE_NAME[k]}那一段的${f === 'e' ? '经历' : '收获'}多了 ${n} 字，${f === 'e' ? '经历' : '收获'}${OWN_MAX[f]}字以内。`);
    if (jump && F._life.i !== lifeList().indexOf(k)) { lifeGo(lifeList().indexOf(k)); return; }
    const ta = $b(`.bx-lown [data-own="${f}"]`); if (ta) { ta.focus({ preventScroll: true }); stageTo(ta, 'center'); }
  }
  // 凭证里那一节（11-26）：翻了前半生、翻到过金血那一头的，五章一章一行，末了一行说明；不翻的一行不添
  function ownCredLines() {
    if (!lifeActive() || !F._life || !F._life.left) return [];
    const anyOwn = lifeList().some((k) => isOwn(k) && ownFilled(k));
    return lifeList().map((k) => {
      const n = `前半生·${LIFE_NAME[k]}：`;
      if (isOwn(k) && ownFilled(k)) { const o = F.lifeOwn[k]; return n + `（自述）经历 ${ownLen(o.e) ? ownLine(o.e) : '未写（由 AI 照收获补一两句）'}｜收获 ${ownLen(o.g) ? ownLine(o.g) : '未写（由 AI 照经历折一样，不额外加强）'}`; }
      const o = lifeOpt(k); if (!o) return n + '留白（由她照前后几章补一段）';
      const g = lifeGain(o); return n + clean(o.t) + '｜' + clean(o.d) + (g ? '｜收获 ' + g : '');
    }).concat('※ 前半生这几行是玩家在门面上一章一章翻的，第〇轮照它一章一章念、一章一章补完，不另起炉灶，留白的照前后几章补。' + (anyOwn ? '标着（自述）的是玩家自己写的，收获里门面认得出的（偏哪两样、会哪样本事、从哪一级起步）已经照一张牌的分量折进属性、本事、初始实力那几行，没认出来的由 AI 照这一纪的规矩折成属性倾向和本事，不额外加强，不越过初始实力那一档，得来的东西照这一纪寻常的品阶算。' : '收获已经折进属性、本事、初始实力那几行，不再另加。'));
  }
  const STAT_CN = { STR: '力量', DEX: '敏捷', MANA: '魔力', MIND: '精神', VGR: '体魄', FTH: '感应' };
  function lifeGain(o) {
    const p = [];
    const st = Object.keys(o.st || {}).filter((k) => o.st[k] > 0); if (st.length) p.push('偏' + st.map((k) => STAT_CN[k]).join('、'));
    if (o.tier) p.push('从' + o.tier + '起步');
    if (o.sk && o.sk.length) { const got = lifeSkills([o]); if (got.length) p.push('会：' + got.join('、')); }
    return p.join(' · ');
  }
  function lifeRender(enter) {
    const L = lifeList(), k = L[F._life.i], G = lifeGroup() || {}, body = bodyEl();
    body.className = 'bx-body life c-' + k;
    const intro = (G.intro || {})[k] || '', img = LIFE_IMG[k];
    const main = lifeOpts(k), primary = lifeHas(k) ? (k === 'birth' ? '记下这户人家' : '记下这一段') : '留白，往下翻';
    const title = (G.title || {})[k] || '';
    body.innerHTML = `<header class="bx-hd life"><small>前半生 · ${esc(LIFE_LA[k])}</small><h2>${esc(LIFE_NAME[k])}${title ? '<span> · ' + esc(title) + '</span>' : ''}</h2>${intro ? `<p data-a="hdp">${esc(intro)}</p>` : ''}</header>${hasArt(img) ? `<div class="bx-vign" data-deal style="background-image:url('${artUrl(img)}')"></div>` : ''}` + main;
    const lay = $b('.bx-lay'); if (lay) lay.innerHTML = '';
    const nb = $b('.bx-ctl [data-a="next"]'); if (nb) nb.textContent = primary; BS.primary = primary;
    const bp = $b('.bx-ctl [data-a="prev"]'); if (bp) { bp.disabled = false; bp.textContent = '上一步'; }
    if (enter) dealIn($$b('.bx-body [data-deal]'), { stagger: 70 });
  }
  function lifeNext() {
    const k = lifeList()[F._life.i];
    if (isOwn(k) && ownOver(k)) { ownOverErr(k); return; }
    if (F._life.i >= lifeList().length - 1) { lifeLeave(); return; }
    lifeGo(F._life.i + 1);
  }
  function lifePrev() { if (F._life.i <= 0) { go(3); return; } lifeGo(F._life.i - 1); }
  /* 翻完最后一章：照选的替后面几步先填上（选的没变就不再填，免得盖掉在那几步里改过的），往金血或者起点走 */
  function lifeLeave(n) {
    if (BX.busy) return;
    { const ov = lifeList().find((k) => isOwn(k) && ownOver(k)); if (ov) { ownOverErr(ov, true); return; } }
    applyLife();
    F._life.left = true;
    go(n || afterLife());
  }
  function lifeFinish(n) { F.lifeOn = true; F._life = F._life || { i: 0, max: 0, picks: {} }; lifeLeave(n); }          // 走查用（__bd.finish）
  /* 选了的几页落到十一步上：出身那几栏、本事、起点、六维往哪边偏、誓心、初心、落在哪 */
  function lifeSkills(opts) {
    const P = curP(), y = oyear(), ok = (P.skills || []).map((s) => (typeof s === 'string' ? { s } : s)).filter((s) => visible(s, y)).map((s) => s.s), out = [];
    for (const o of opts) for (const h of o.sk || []) { const hit = o.own && ok.includes(h) ? (out.includes(h) ? '' : h) : ok.find((s) => s.indexOf(h) >= 0 && !out.includes(s)); if (hit && out.length < 2) out.push(hit); }          // 自述认出来的是整名，照整名
    return out;
  }
  const lifeSig = () => JSON.stringify([oyear(), F.race, F.sub, lifeList().map((k) => (isOwn(k) ? ['own', ((F.lifeOwn || {})[k] || {}).g || '', ownFilled(k)] : F._life.picks[k] == null ? null : F._life.picks[k]))]);
  function applyLife() {
    const G = lifeGroup(); if (!G || !F._life) return;
    const sig = lifeSig(); if (F._life.sig === sig) return; F._life.sig = sig;
    const pre = F._pre = {};
    const opts = ['birth', 'home', 'child', 'youth', 'depart'].map((k) => (isOwn(k) && ownFilled(k) ? ownParse(k) : lifeOpt(k))).filter(Boolean);          // 自己写的那几章照它认得出的几样当一张牌
    const S = sheetOf(curP()), cols = (S.cols || []).concat(S.blank && S.blank.label ? [S.blank.label] : []);
    F.sheet = F.sheet || {};
    for (const o of opts) for (const c in (o.sheet || {})) if (cols.includes(c) && c !== '名字' && c !== '族') { F.sheet[c] = o.sheet[c]; pre[9] = 1; }
    const sk = lifeSkills(opts); if (sk.length) { F.skills = sk; pre[9] = 1; }
    const dp = isOwn('depart') && ownFilled('depart') ? ownParse('depart') : lifeOpt('depart');
    if (dp && dp.tier && TIERS.some((t) => t[0] === dp.tier)) { F.tier = dp.tier; pre[5] = 1; }
    if (dp && dp.wish) { if ((WISH[BS.book] || []).concat(WISH_ALL).some((w) => w[0] === dp.wish)) { F.wishPick = dp.wish; pre[10] = 1; } else if (!F.wish) { F.wish = dp.wish; pre[10] = 1; } }
    if (dp && dp.place && BS.free && F.placeI == null && !F.place) { F.place = dp.place; pre[10] = 1; }
    // 六维：底子照胎骨和起点（上限的一半），往选过的那几样偏
    const w = {}; for (const [k] of STAT) w[k] = 0;
    for (const o of opts) for (const k in (o.st || {})) if (k in w) w[k] += +o.st[k] || 0;
    F.stats = lean(w); F.statMode = 'manual'; F.statKey = statKey(); F._lean = w; pre[6] = 1;          // 偏向留着：后面起点一换，六维照同样的偏向重分
    // 誓心：守序和混乱、善良和邪恶各记一笔
    const al = { law: 0, chaos: 0, good: 0, evil: 0 };
    for (const o of opts) for (const k in (o.al || {})) if (k in al) al[k] += +o.al[k] || 0;
    const lc = al.law - al.chaos, ge = al.good - al.evil;
    const a1 = lc >= 1 ? '守序' : lc <= -1 ? '混乱' : '中立', a2 = ge >= 1 ? '善良' : ge <= -1 ? '邪恶' : '中立';
    if (opts.some((o) => o.al)) { F.oath = a1 === '中立' && a2 === '中立' ? '绝对中立' : a1 + a2; pre[9] = 1; }
  }
  function lean(w) {
    const c = caps(), B = budget(), s = {};
    const f = {}; let tot = 0; for (const [k] of STAT) { f[k] = c[k] * (1 + 0.5 * Math.max(0, w[k] || 0)); tot += f[k]; }
    let used = 0; const rem = [];
    for (const [k] of STAT) { const raw = B * f[k] / tot, v = Math.max(1, Math.min(c[k], Math.floor(raw))); s[k] = v; used += v; rem.push([raw - v, k]); }
    rem.sort((a, b) => b[0] - a[0]);
    for (let g = 0; used < B && g < 5000; g++) { let moved = false; for (const [, k] of rem) { if (used >= B) break; if (s[k] < c[k]) { s[k]++; used++; moved = true; } } if (!moved) break; }
    for (let g = 0; used > B && g < 5000; g++) { const k = STAT.map((x) => x[0]).sort((a, b) => s[b] - s[a])[0]; if (s[k] <= 1) break; s[k]--; used--; }
    return s;
  }

  /* ---------- 铸印：这一纪的印自己压下去，身份牌收成一本薄书，飞上书架 ---------- */
  function stampSVG(v) {
    const b = v || (BS ? BS.vis : 'maze');
    if (b === 'moon') return '<svg viewBox="0 0 220 70"><defs><filter id="bxch"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="7"/></filter></defs><path d="M12 44 C 50 22, 96 20, 132 28 S 196 40, 210 22 L 206 34 C 186 52, 150 46, 118 40 S 48 46, 16 54 Z" fill="#0b0a0a" opacity=".9" filter="url(#bxch)"/></svg>';
    if (b === 'strife') return '<svg viewBox="0 0 120 120"><defs><filter id="bxrd"><feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.6"/><feComposite in="SourceGraphic" operator="in"/></filter></defs><g filter="url(#bxrd)"><rect x="8" y="8" width="104" height="104" rx="6" fill="none" stroke="#b3261e" stroke-width="7"/><rect x="18" y="18" width="84" height="84" fill="none" stroke="#b3261e" stroke-width="2"/><text x="60" y="55" text-anchor="middle" font-size="30" fill="#b3261e" font-family="serif" font-weight="700">军</text><text x="60" y="91" text-anchor="middle" font-size="30" fill="#b3261e" font-family="serif" font-weight="700">册</text></g></svg>';
    if (b === 'bronze') return '<svg viewBox="0 0 120 120"><g fill="none" stroke-linecap="round"><path d="M60 10 L104 60 L60 110 L16 60 Z" stroke="#0e0e10" stroke-width="5"/><path d="M60 10 L104 60 L60 110 L16 60 Z" stroke="#f3eee2" stroke-width="2" transform="translate(1.6 1.6)" opacity=".55"/><path d="M60 30 V90 M38 60 H82" stroke="#0e0e10" stroke-width="4"/><path d="M60 30 V90 M38 60 H82" stroke="#f3eee2" stroke-width="1.6" transform="translate(1.4 1.4)" opacity=".5"/></g></svg>';
    if (b === 'now') return '<svg viewBox="0 0 120 120"><defs><radialGradient id="bxbr" cx=".38" cy=".32" r=".75"><stop offset="0" stop-color="#f6d58c"/><stop offset=".55" stop-color="#c08a3a"/><stop offset="1" stop-color="#6b4614"/></radialGradient></defs><circle cx="60" cy="60" r="52" fill="url(#bxbr)"/><circle cx="60" cy="60" r="44" fill="none" stroke="#fff3cf" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="3 3"/><path d="M60 26 L66 54 L94 60 L66 66 L60 94 L54 66 L26 60 L54 54 Z" fill="#fff6dc" opacity=".85"/><circle cx="60" cy="60" r="6" fill="#6b4614"/></svg>';
    return `<svg viewBox="0 0 120 120"><defs><radialGradient id="bxwx" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#b53a2c"/><stop offset=".7" stop-color="#7a1c17"/><stop offset="1" stop-color="#4a0f0d"/></radialGradient></defs><path d="M60 6 C82 6 90 18 104 24 C116 38 112 52 114 64 C116 84 98 100 84 108 C70 116 50 116 36 108 C20 100 6 86 8 64 C9 46 4 34 18 22 C30 12 40 6 60 6 Z" fill="url(#bxwx)"/><circle cx="60" cy="62" r="34" fill="none" stroke="#e8a48d" stroke-opacity=".35" stroke-width="2"/></svg><img src="${A('common/assets/ui/emblem_maze.webp')}" alt="">`;
  }
  async function mint() {
    if (BX.busy) return;
    const text = credential(), name = String(F.name || '').trim() || '无名', x = root(), y = oyear();
    BX.busy = true; BX.minting = true;
    const ctl = $b('.bx-ctl'); if (ctl) ctl.classList.add('off');
    if (isM()) { x.classList.add('idopen', 'minting'); await T(80); }
    const id = $b('.bx-id'), r = id.getBoundingClientRect();
    const cx = r.left + r.width / 2, cy = r.top + r.height * 0.62, sw = Math.min(150, r.width * 0.5);
    const st = document.createElement('div'); st.className = 'bx-stamp s-' + BS.vis; st.innerHTML = stampSVG(); x.appendChild(st);
    st.style.width = st.style.height = sw + 'px';
    st.style.transition = 'none'; st.style.transform = `translate(${cx - sw / 2}px,${cy - sw / 2 - 160}px) scale(1.6)`; st.style.opacity = '0'; void st.offsetWidth; st.style.transition = '';
    await T(60);
    st.style.opacity = '1'; st.style.transform = `translate(${cx - sw / 2}px,${cy - sw / 2}px) scale(1)`;
    await T(440);
    id.classList.add('shake', 'minted'); id.querySelector('.mark').innerHTML = stampSVG();
    (window.__sfx || (() => {}))('seal');          // 建档：铸印压下去
    const ring = document.createElement('div'); ring.className = 'bx-ring2'; ring.style.left = cx + 'px'; ring.style.top = cy + 'px'; x.appendChild(ring); requestAnimationFrame(() => ring.classList.add('go'));
    await T(720);
    st.style.opacity = '0'; st.style.transform = `translate(${cx - sw / 2}px,${cy - sw / 2 - 120}px) scale(1.2)`;
    speak([LINES[11].in[0].replace('就改不回去了', '就改不回去了') && '刻好了。这一本，我替你放上架。']);
    await T(620);
    // 这一格收成一本薄书的书脊
    const bk = document.createElement('div'); bk.className = 'bx-book'; bk.dataset.era = BS.vis;
    const sp = { moon: 'moon', strife: 'strife', bronze: 'bronze', maze: 'maze', now: 'future' }[BS.vis] || 'maze';
    bk.style.setProperty('--sp', `url('${absA('common/assets/lib/spine_' + sp + '_1.webp')}')`);
    bk.innerHTML = `<b>${esc(name)}</b><i>${esc(BS.era)}</i>`; x.appendChild(bk);
    const ir = id.getBoundingClientRect(), bw = bk.offsetWidth, bh = bk.offsetHeight, icx = ir.left + ir.width / 2, icy = ir.top + ir.height / 2;
    bk.style.transition = 'none'; bk.style.transform = `translate(${icx - bw / 2}px,${icy - bh / 2}px) scale(${ir.height / bh})`; bk.style.opacity = '0'; void bk.offsetWidth; bk.style.transition = '';
    id.classList.remove('shake'); id.style.transition = 'transform .8s cubic-bezier(.3,.7,.2,1),opacity .6s';
    id.style.transform = (id.style.transform || '') + ` scale(${bw / ir.width * 1.1},${bh / ir.height * 0.98})`; id.style.opacity = '0';
    bk.style.opacity = '1'; bk.style.transform = `translate(${icx - bw / 2}px,${icy - bh / 2}px) scale(${Math.min(1, ir.height / bh)})`;
    await T(900);
    // 书架从右上角降下来，这一本飞进空着的那一格
    const sh = document.createElement('div'); sh.className = 'bx-shelf';
    const cols = ['#3c5a8f', '#5b6577', '#7a2c2a', '#3a3d44', '#1f2c5c', '#8a7a5a', '#2d3140', '#4a3a5e'];
    sh.innerHTML = `<div class="case"></div><div class="cap">大图书馆 · 往后的廊</div><div class="row">${cols.map((c, i) => `<span class="sp" style="--c:${c};--h:${96 + (i * 37) % 30}px;--w:${14 + (i * 7) % 12}px"></span>`).join('')}<span class="slot"></span><span class="sp" style="--c:#e8e4da;--h:104px;--w:16px;opacity:.6"></span><span class="sp" style="--c:#f3f1ec;--h:98px;--w:14px;opacity:.4"></span></div>`;
    x.appendChild(sh); requestAnimationFrame(() => sh.classList.add('on'));
    await T(320);
    const sr = sh.querySelector('.slot').getBoundingClientRect(), sx = sr.left + sr.width / 2, sy = sr.top + sr.height / 2, s1 = sr.height / bh;
    bk.style.transform = `translate(${(icx + sx) / 2 - bw / 2 + 60}px,${Math.min(icy, sy) - bh / 2 - 40}px) rotate(-16deg) scale(${(1 + s1) / 2})`;
    await T(620);
    bk.style.transform = `translate(${sx - bw / 2}px,${sy - bh / 2}px) rotate(0deg) scale(${s1})`;
    await T(950);
    sh.querySelector('.slot').classList.add('full');
    const leaveW = (BUILD && BUILD.ronova && BUILD.ronova.leave) || ['去吧。'];
    speak(['好了。这一本，我替你放上架。', leaveW[0]]);
    try { if (window.Library && Library.addPlayerBook) Library.addPlayerBook({ name, title: name + '的旅印', era: BS.era, vis: BS.vis, year: y != null ? yText(y) : '', line: BS.free ? ((BS.FR || {}).label || '') : (BS.m.line || ''), text, paper: PAPER[BS.vis] || 'print' }); } catch (e) { console.warn('上架', e); }
    await T(1100);
    BX.busy = false;
    seal(text, true);
    setTimeout(() => { for (const el of [st, ring, bk, sh]) el.remove(); if (ctl) ctl.classList.remove('off'); }, 900);
  }

  /* ---------- 请离那一眼（迷宫纪 1001 年旧页交上来的凭证还走这一段），确认页 ---------- */
  function leave(text) {
    const D = BUILD || {}, words = (D.ronova && D.ronova.leave) || ['去吧。'];
    const img = leaveEl.querySelector('img'), p = leaveEl.querySelector('p');
    img.src = A('assets/ronova.webp'); p.textContent = words[0];
    leaveEl.className = ''; show(leaveEl); hide(buildEl);
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches, Tm = reduce ? [100, 300, 900, 1400] : [900, 1900, 4300, 5600];
    setTimeout(() => leaveEl.classList.add('see'), Tm[0]);
    setTimeout(() => leaveEl.classList.add('say'), Tm[1]);
    setTimeout(() => { leaveEl.classList.add('gone'); leaveEl.classList.remove('say'); }, Tm[2]);
    setTimeout(() => { seal(text); hide(leaveEl, 900); }, Tm[3]);
  }
  /* 确认页：玩家那一本书的第一页。凭证照那一纪的材质排好（字一个不改，复制、填进输入框的是原文），底下照旧能复制、填进输入框；超过 8192 字只给复制 */
  function credHTML(text) {
    return text.split('\n').map((l, i) => {
      if (!l.trim()) return '<i class="gap"></i>';
      if (i === 0) return `<p class="op">${esc(l)}</p>`;
      const m = l.match(/^(【[^】]+】)(.*)$/);
      if (m && !m[2]) return `<h4>${esc(m[1])}</h4>`;
      if (m) return `<p><b>${esc(m[1])}</b>${esc(m[2])}</p>`;
      const k = l.match(/^([^：]{1,14}：)(.*)$/);
      return k ? `<p><span class="k">${esc(k[1])}</span>${esc(k[2])}</p>` : `<p>${esc(l)}</p>`;
    }).join('');
  }
  function seal(text, own) {
    const tooLong = text.length > LIMIT, v = own && BS ? BS.vis : 'maze', name = own ? String(F.name || '').trim() || '无名' : '';
    const pap = PAPER[v] || 'print', y = own ? oyear() : null;
    sealEl.innerHTML = `<div class="sl-wrap sl-book" data-era="${v}" style="--paper:url('${absA('common/assets/lib/paper_' + pap + '.webp')}')"><div class="sl-page">
<header class="sl-hd">${own ? `<small>${esc(BS.era)}${y != null ? ' ' + esc(yText(y)) : ''}　第一页</small><h2>${esc(name)}的旅印</h2>` : '<small>建档凭证</small><h2>建档凭证</h2>'}<div class="sl-stamp">${own ? stampSVG(v) : ''}</div>
<p class="sub">${tooLong ? '这一份比输入框一回收得下的长，点“复制”，回到聊天里粘贴再发送。' : (inRili ? '点“填进输入框”，凭证会落在聊天的输入框里，再点发送，就从那一年睁眼。' : '复制下来，回到聊天的输入框里粘贴，再发送。')}</p></header>
<div class="sl-paper" tabindex="0">${credHTML(text)}</div>
<div class="sl-acts">${tooLong || !inRili ? '' : '<button type="button" class="go" data-a="fill">填进输入框</button>'}<button type="button" data-a="copy"${tooLong || !inRili ? ' class="go"' : ''}>复制</button><button type="button" data-a="edit">回去改</button>${own && window.Library ? '<button type="button" data-a="lib">到书架上看看</button>' : ''}<button type="button" data-a="table">回到牌桌</button></div>
<p class="sl-tip" aria-live="polite">${own ? '这一本放在大图书馆往后的廊，第二十一格。这一回打开门面的时候都在，下回进来就不在了。' : ''}</p></div></div>`;
    const tip = sealEl.querySelector('.sl-tip'), say = (t, ok) => { tip.textContent = t; tip.classList.toggle('ok', !!ok); };
    sealEl.onclick = (e) => {
      const b = e.target.closest('[data-a]'); if (!b) return;
      const a = b.dataset.a;
      if (a === 'fill') { try { window.parent.postMessage({ type: 'rili-set-input', value: text }, '*'); say('填进去了。点一下发送，她就把你送过去。输入框里没有的话，点“复制”再粘贴。', true); } catch (err) { say('没填进去，点“复制”再粘贴。'); } }
      else if (a === 'copy') copy(text).then((ok) => say(ok ? '复制好了。回到聊天的输入框里粘贴，再发送。' : '没复制上：长按上面那一段文字，全选了再复制。', ok));
      else if (a === 'edit') { hide(sealEl); if (pend) startBuild(pend); }          // 1001 年那一页的凭证没有 pend：收起这一层，底下就是它自己铸印的那一幕，在那里往回改
      else if (a === 'lib') { hide(sealEl); hide(buildEl, 300); if (frame) bookHide(false); setTimeout(() => { Library.open('future'); }, 120); }
      else if (a === 'table') { hide(sealEl); toTable(); }
    };
    show(sealEl); sealEl.scrollTop = 0;
  }
  function copy(text) {
    const old = () => { try { const ta = document.createElement('textarea'); ta.value = text; ta.style.cssText = 'position:fixed;left:-9999px;top:0'; document.body.appendChild(ta); ta.select(); const ok = document.execCommand('copy'); ta.remove(); return ok; } catch (e) { return false; } };
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text).then(() => true).catch(() => old());
    return Promise.resolve(old());
  }

  /* ---------- 接续旅印（旧 1001 页的“接续旧档”挪过来，五本书都能用）：贴一段存档或上一轮的回复，认出是哪一种，接成接续文本 ---------- */
  const RS = { kind: '' };
  function resumeGuess(raw) {
    if (/A｜时间与世界|B｜玩家与成长|C｜队伍、人物与羁绊|存档完毕/.test(raw)) return 'load';
    if (/跨版本迁移凭证|跨会话存档文件|迁移凭证/.test(raw)) return 'migrate';
    if (/当前主要角色|冒险者面板|成长与伟业|arc-npc-card|arc-memory|§面板｜|§记忆｜|§底座/.test(raw)) return 'carry';
    return '';
  }
  function resumeText(raw) {
    const k = RS.kind || resumeGuess(raw) || 'load';
    if (k === 'carry') return '接档——下面是正式版最后一轮的回复，照【接档】接住。\n\n' + raw;
    if (k === 'migrate') return '【读取迁移凭证】\n\n' + raw;
    return (/^读档/.test(raw) ? '' : '读档\n\n') + raw;
  }
  function openResume() {
    const old = $b('.bx-pop'); if (old) old.remove();
    RS.kind = '';
    const p = document.createElement('div'); p.className = 'bx-pop'; p.setAttribute('role', 'dialog'); p.setAttribute('aria-label', '接续旅印');
    p.innerHTML = `<div class="box bx-paper"><button type="button" class="x" data-a="rclose">合上</button><h3>接续旅印</h3>
<p>贴进上一段旅程的存档，或者上一轮的整段回复，认清是哪一种，再把接续文本带回聊天里发出去。角色、命星和已有的经历都从记录那一处接着走。</p>
<div class="b2-chips">${[['load', '存档'], ['carry', '上一轮的状态记录'], ['migrate', '重制以前的旧档']].map(([k, t]) => `<button type="button" data-a="rkind" data-v="${k}" aria-pressed="false">${t}</button>`).join('')}</div>
<p class="b2-note">带「A｜时间与世界」的是存档。带冒险者面板、成长与伟业、背包、人物和记忆的整段回复是上一轮的状态记录，旧版带 HTML 标签的、新版以 §底座 开头的都算。更早的存档和迁移凭证选重制以前的旧档。贴进来会自己认，认错了点一下改。</p>
<textarea class="rin" rows="8" placeholder="把存档，或者上一轮的整段回复贴在这里"></textarea>
<div class="acts">${inRili ? '<button type="button" class="bt pri" data-a="rfill">填进输入框</button>' : ''}<button type="button" class="bt${inRili ? '' : ' pri'}" data-a="rcopy">复制接续文本</button></div><p class="tip" aria-live="polite"></p></div>`;
    root().appendChild(p);
    const ta = p.querySelector('.rin');
    ta.addEventListener('input', () => { const g = resumeGuess(ta.value || ''); if (g) { RS.kind = g; for (const b of p.querySelectorAll('[data-a="rkind"]')) b.setAttribute('aria-pressed', String(b.dataset.v === g)); } });
    setTimeout(() => ta.focus(), 60);
    speak(['旧的手记带来了？', '贴进来，我认得出是哪一本。']);
  }
  function resumeOut(fill) {
    const p = $b('.bx-pop'); if (!p) return;
    const raw = (p.querySelector('.rin').value || '').trim(), tip = p.querySelector('.tip');
    if (!raw) { tip.textContent = '先把存档或上一轮的回复贴进来。'; return; }
    const txt = resumeText(raw);
    if (fill && txt.length <= LIMIT) { try { window.parent.postMessage({ type: 'rili-set-input', value: txt }, '*'); tip.textContent = '填进去了。开一个新对话也行，点一下发送就接着走。'; return; } catch (e) { /* 照复制 */ } }
    copy(txt).then((ok) => { tip.textContent = ok ? (fill ? '这一段太长，输入框收不下，已经复制好了，' : '') + '接续文本复制好了。开一个新对话，整段发出去。' : '没复制上：在上面那一格里全选了再复制。'; });
  }

  window.Shell = Shell;
  Shell.startBuild = startBuild; Shell.credential = () => (BS ? credential() : '');
  Shell.resume = (m) => { startBuild(m || pend || { book: 'maze', at: 'free' }).then(() => openResume()); };          // 书里“接续旅印”那一枚可以直接叫这个
  addEventListener('resize', () => { if (buildEl.hidden || !BS) return; clearTimeout(BX.rz); BX.rz = setTimeout(() => { layoutFan(); layoutRing(); if (BS.mode === 'step' && BS.step === 11 && !BX.busy) placeMintCard(); }, 150); });
  for (const ev of ['pointerdown', 'keydown']) buildEl.addEventListener(ev, poke);
  /* 11-26 前半生自己写：手机上点进那两格，键盘弹起来以后把这一格挪进还看得见的那一截（照 visualViewport 量，键盘盖住的不算） */
  function ownKeep(t) {
    const st = t && t.closest && t.closest('.bx-stage'); if (!st) return;
    const vv = window.visualViewport, vb = vv ? vv.offsetTop + vv.height : innerHeight, sr = st.getBoundingClientRect(), r = t.getBoundingClientRect();
    const top = sr.top + 8, bot = Math.min(vb, sr.bottom) - 10, cnt = t.nextElementSibling, rb = cnt ? Math.max(r.bottom, cnt.getBoundingClientRect().bottom) : r.bottom;
    if (rb > bot) st.scrollTop += Math.min(rb - bot, r.top - top); else if (r.top < top) st.scrollTop -= top - r.top;
  }
  buildEl.addEventListener('focusin', (e) => { const t = e.target; if (!isM() || !t.closest || !t.closest('.bx-lown')) return; ownKeep(t); setTimeout(() => { if (document.activeElement === t) ownKeep(t); }, 350); });
  if (window.visualViewport) visualViewport.addEventListener('resize', () => { const t = document.activeElement; if (!buildEl.hidden && isM() && t && t.closest && t.closest('.bx-lown')) ownKeep(t); });
  /* 走查用（act_build.mjs 这几支）：看走到哪一步、填了什么，直接跳步 */
  window.__bd = { go: (n) => BS && go(n), next: () => BS && next(), get F() { return F; }, get step() { return BS ? BS.step : 0; }, get mode() { return BS ? BS.mode : ''; }, get free() { return BS ? BS.free : null; }, get busy() { return BX.busy; }, get BS() { return BS; },
    cred: () => (BS ? credential() : ''), drawn: (k) => (BS ? drawn(k) : []), gifts: () => (BS ? giftsDrawn() : []), giftPool: () => (BS ? giftPool() : []), gods: () => (BS ? godsNow() : []), pool: (k) => (BS ? starPool(k) : []),
    // 命星几处的账（第二轮/建档/tools/starpile.mjs 测逻辑用）：zones 这一池各处有哪几颗，draw 抽一手（回抽到几张），keep、hold、drop、reset 同页面上那几枚钮
    star: { zones: (k) => { if (!BS) return null; const D = starZ(k); return { kept: F['star' + k] || '', hand: D.ids.slice(), hold: D.hold.slice(), gone: D.gone.slice(), deck: starDeck(k).map((t) => t.id), pool: starPool(k).map((t) => t.id), n: D.n }; },
      draw: (k) => (BS ? drawStars(k) : 0), keep: (k, id) => (BS ? starKeep(k, id) : ''), hold: (k, id) => (BS ? starHold(k, id) : ''), drop: (k, id) => (BS ? starDrop(k, id) : ''), reset: (k) => (BS ? starReset(k) : 0), at: (k, id) => (BS ? starAt(k, id) : '') },
    way: (v) => (v === 'life' ? lifeStart() : (F._route = 'direct', go(Math.min(F._step || 1, F._max || 1)))), life: (i) => lifeGo(i), lifeList: () => (BS ? lifeList() : []), finish: (n) => lifeFinish(n), mint: () => mint(), resume: () => openResume(), deal: (on) => { BX.deal = !!on; } };
  function A(p) { return window.A ? window.A(p) : p; }
})();

// <bgm>
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
    if (elMode && SFX_OFF()) { acOpened = true; return; }      // 11-27：走 <audio> 而且音效关着，用不着 AudioContext，不开
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
  /* 11-27 止血：手机、平板、安卓 App 里的 WebView 一律走 <audio>（边下边放，不把整首解进内存：一首解开六七十 MB，App 里内存一紧整页会被杀掉）。
     只有电脑（不是触屏、UA 里没有手机的字样）走 WebAudio。?bgmel 强制 <audio>，?bgmwa 强制 WebAudio（本地验用）。
     WebAudio 解不开（内存不够、格式不认）也退回 <audio> 那一路，往后都走那一路。 */
  const UA = navigator.userAgent || '';
  const DESK = !/Android|iPhone|iPad|iPod|Mobile|; wv\)|HarmonyOS|OpenHarmony|MicroMessenger|Windows Phone/i.test(UA) && !(navigator.maxTouchPoints > 1 && /Macintosh/.test(UA)) && !(window.matchMedia && matchMedia('(pointer: coarse)').matches);
  let elMode = Q.has('bgmel') || (!DESK && !Q.has('bgmwa'));
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

  /* ---------- <audio> 那一路：两个轮着用，边下边放；每一首放到哪儿记在 POS，换回来照它 seek（等 loadedmetadata） ---------- */
  let E1 = null, E2 = null, elCur = null;
  function mkEl() {
    const a = document.createElement('audio');
    a.preload = 'none'; a.setAttribute('playsinline', ''); a.style.display = 'none';
    document.body.appendChild(a);
    a.addEventListener('error', () => retry(a));
    a.addEventListener('timeupdate', () => { const L = a.dataset.rel && loopOf(a.dataset.rel); if (L && a.currentTime >= L[1]) a.currentTime = L[0] + (a.currentTime - L[1]); });      // 末尾多拷的那 1.5 秒跟 X 秒以后一样，拨回去听不出
    a.addEventListener('loadedmetadata', () => { if (a.dataset.seek != null && a.dataset.seek !== '') { const x = +a.dataset.seek; delete a.dataset.seek; if (x > 0) { try { a.currentTime = x; } catch (e) {} } } });
    return a;
  }
  function els() { if (!E1) { E1 = mkEl(); E2 = mkEl(); } }
  function elLoad(a, rel) {
    if (a.dataset.rel !== rel) { a.dataset.rel = rel; a.dataset.mr = 0; a.dataset.seek = POS[rel] || 0; a.src = urlOf(rel); }
    else if (POS[rel] != null && Math.abs((a.currentTime || 0) - POS[rel]) > 0.5) elSet(a, POS[rel]);
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
    els();
    const prev = elCur;
    if (prev && prev.dataset.rel === rel && !prev.paused) return;
    const a = prev && prev.dataset.rel === rel ? prev : prev === E1 ? E2 : E1;
    if (prev && prev !== a && prev.dataset.rel) POS[prev.dataset.rel] = prev.currentTime;
    elLoad(a, rel);
    elCur = a;
    a.muted = false; try { a.volume = 0; } catch (e) {}
    play(a);
    fadeTo(a, VOL() * userVol, fadeMs);
    if (prev && prev !== a) fadeTo(prev, 0, FADE(), () => { if (prev !== elCur) prev.pause(); });
  }
  function elPause(ms) { const a = elCur; if (!a) return; POS[a.dataset.rel] = a.currentTime; fadeTo(a, 0, ms, () => { if (userPaused || a !== elCur) a.pause(); }); }
  function elSeek(rel, x) { POS[rel] = wrap(rel, x); if (elCur && elCur.dataset.rel === rel) elSet(elCur, POS[rel]); }

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
    if (!userPaused) playScene(scene, 1500);
    if (!WA() && elCur) {      // iOS、安卓 WebView：两个 <audio> 都要在手势里放过一回，往后换曲才放得出来；另一个静音放一下就停
      const b = elCur === E1 ? E2 : E1;
      try { b.muted = true; b.dataset.rel = elCur.dataset.rel; b.src = elCur.src; const p = b.play(); const stop = () => { b.pause(); b.muted = false; }; if (p && p.then) p.then(stop, stop); else stop(); } catch (e) {}
    }
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
// </bgm>
