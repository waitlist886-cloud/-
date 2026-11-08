// 试验场第三版（11-08），在 az_reset.sh 摆好的干净图上跑：
//   1. 比例尺照设定（半径约地球的一倍半，图从北到南约 160 度）每像素 19 公里，单位写公里
//   2. 巨城画成放大的城市平面：几道城墙一层套一层，墙里有田、有卫城，放射的大道，城心的宫
//   3. 用户自己在 .map 里画的 AUL 那一层（长垒、大迷宫的圈），AUL_SVG 由外面替换
//   4. 巨构和超自然景观：寒天之钉、星环、曜冠空环城、星落群岛、玻璃沙坡、黑曜环山、赤盐沉宫、黑潮螺旋城
//   5. 巨城的名字（思源宋体）
(async () => {
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const vb = document.getElementById('viewbox');
  const defs = document.getElementById('featurePaths').closest('defs');
  for (const id of ['playCities', 'playOverlay', 'playMagic', 'playLabels', 'playDefs']) { const o = document.getElementById(id); if (o) o.remove(); }
  const pdefs = mk('g', { id: 'playDefs' }, defs);
  const log = [];
  let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const C = pack.cells, P = pack.vertices.p;
  const isLand = (i) => C.h[i] >= 20 && (!pack.features[C.f[i]] || pack.features[C.f[i]].type !== 'lake');

  // ---- 1. 比例尺 ----
  options.map.units.distance.scale = 19;
  options.map.units.distance.unit = '公里';
  const sbBtn = document.querySelector('#mapLayers [data-layer=scaleBar]');
  if (sbBtn.classList.contains('buttonoff')) sbBtn.click(); else { sbBtn.click(); sbBtn.click(); }
  await new Promise((r) => setTimeout(r, 600));
  const sbt = [...document.querySelectorAll('#scaleBar text')].map((t) => t.textContent).join(' ');
  log.push('比例尺 ' + sbt);

  // ---- 2. 巨城 ----
  const T = {
    gold:   { ground: '#d9cdb1', f1: '#cdc79a', f2: '#a9a274', mid: '#cbb994', core: '#b9a47e', line: '#8a7552', wall: '#5b4a33', hi: '#f3e7c6', keep: '#f0c75e' },
    ash:    { ground: '#a39a92', f1: '#9b948b', f2: '#7d746c', mid: '#8f857e', core: '#6e6260', line: '#3f3534', wall: '#231c1c', hi: '#d9cfc6', keep: '#c4473b' },
    silver: { ground: '#d6d6cc', f1: '#c8cba6', f2: '#a5aa86', mid: '#c2c2b6', core: '#a9aba5', line: '#76787a', wall: '#4b4f57', hi: '#f2f4f7', keep: '#e8eef8' },
    wind:   { ground: '#d2d0c0', f1: '#c3c79c', f2: '#a0a57a', mid: '#bdb9a6', core: '#a6a08c', line: '#756e5c', wall: '#4d4a40', hi: '#f1eee2', keep: '#9fc3e0' },
    rose:   { ground: '#dccbbd', f1: '#d2b9a4', f2: '#b88f80', mid: '#ccb0a2', core: '#b9938a', line: '#87605a', wall: '#5a3a36', hi: '#f6e6de', keep: '#e48aa0' },
    azure:  { ground: '#c6c9c4', f1: '#b8bfae', f2: '#94a08f', mid: '#aeb4b2', core: '#8f99a3', line: '#5b6673', wall: '#2f3946', hi: '#e8eef4', keep: '#6fb6ff' },
    blood:  { ground: '#c9aea4', f1: '#b98278', f2: '#934f49', mid: '#b4948b', core: '#9b6f69', line: '#663b37', wall: '#3d1f1e', hi: '#efd9d2', keep: '#b8222e' },
    bone:   { ground: '#dcd8cc', f1: '#cfcabb', f2: '#a9a393', mid: '#cbc6b8', core: '#b4ae9f', line: '#7f796b', wall: '#4f4b42', hi: '#fbf8ef', keep: '#f3f0e4' },
    mirror: { ground: '#c9c1cf', f1: '#bdb5c6', f2: '#968aa6', mid: '#b5abbf', core: '#9a8faa', line: '#62577a', wall: '#372e4b', hi: '#efe9f6', keep: '#c79bff' },
    raven:  { ground: '#b5b2ae', f1: '#a9a69c', f2: '#86837a', mid: '#9f9b96', core: '#7f7b78', line: '#4b4846', wall: '#1f1d1d', hi: '#dedad4', keep: '#2a2626' },
    iron:   { ground: '#bdbab3', f1: '#b2b09f', f2: '#8e8c7c', mid: '#a7a49d', core: '#8b8984', line: '#56544f', wall: '#2c2b29', hi: '#e6e3dc', keep: '#ffd34d' },
    tide:   { ground: '#c4cdcd', f1: '#b6c0ac', f2: '#91a08c', mid: '#aab8ba', core: '#8ea2a8', line: '#536a73', wall: '#26404b', hi: '#e6f0f2', keep: '#4fa6c9' },
    holy:   { ground: '#e1dccd', f1: '#d4d0a8', f2: '#b1ad83', mid: '#d8d2c2', core: '#c9c2b0', line: '#958c75', wall: '#6b624d', hi: '#fffdf4', keep: '#fff6d8' },
    forge:  { ground: '#c4b4a2', f1: '#b8ab92', f2: '#958670', mid: '#b09a86', core: '#9a7c66', line: '#5d4535', wall: '#33251c', hi: '#ead7c4', keep: '#ff8a3d' },
    arcane: { ground: '#cfd2d6', f1: '#c3c9b2', f2: '#a0a88e', mid: '#c1c6cd', core: '#a8b0bd', line: '#6c7690', wall: '#39425c', hi: '#eef3fb', keep: '#8fd0ff' },
  };
  const CITY = [
    ['金鸢城', 21, 'gold', 3], ['烬灭之都', 21, 'ash', 3],
    ['银湖城', 16, 'silver', 3], ['高岚城', 16, 'wind', 2], ['露玫城', 16, 'rose', 2],
    ['苍焰角城', 13, 'azure', 2], ['血棘红园', 13, 'blood', 2], ['骸钟墓城', 13, 'bone', 2], ['魇镜幻都', 13, 'mirror', 2],
    ['黑翼天塔', 13, 'raven', 2], ['雷狱铁城', 13, 'iron', 2], ['深潮蓝堡', 13, 'tide', 2],
    ['星冠圣城', 12, 'holy', 2], ['熔铁炉心', 11, 'forge', 2], ['星环魔导都市', 12, 'arcane', 2],
    ['阿卡迪亚', 27, 'gold', 0],
  ];
  const cities = mk('g', { id: 'playCities', mask: 'url(#land)' }, null);
  vb.insertBefore(cities, document.getElementById('rivers'));
  const wob = (x, y, r, ph, amp = 1) => { let d = ''; for (let a = 0; a < 360; a += 5) { const t = a * Math.PI / 180; const rr = r * (1 + amp * (0.035 * Math.sin(3 * t + ph) + 0.025 * Math.sin(7 * t + ph * 1.7))); d += (d ? 'L' : 'M') + (x + Math.cos(t) * rr).toFixed(2) + ',' + (y + Math.sin(t) * rr).toFixed(2); } return d + 'Z'; };
  const wedge = (x, y, r1, r2, a0, a1) => { const pts = []; for (let a = a0; a <= a1 + 1e-6; a += (a1 - a0) / 12) pts.push([x + Math.cos(a) * r2, y + Math.sin(a) * r2]); for (let a = a1; a >= a0 - 1e-6; a -= (a1 - a0) / 12) pts.push([x + Math.cos(a) * r1, y + Math.sin(a) * r1]); return 'M' + pts.map((p) => p[0].toFixed(2) + ',' + p[1].toFixed(2)).join('L') + 'Z'; };
  const pat = (id, size, rot, bg, line, w, kind) => {
    const p = mk('pattern', { id, width: size, height: size, patternUnits: 'userSpaceOnUse', patternTransform: `rotate(${rot})` }, pdefs);
    mk('rect', { width: size, height: size, fill: bg }, p);
    if (kind === 'grid') mk('path', { d: `M0,${size / 2}H${size}M${size / 2},0V${size}`, stroke: line, 'stroke-width': w }, p);
    else if (kind === 'stripe') mk('path', { d: `M0,${size / 2}H${size}`, stroke: line, 'stroke-width': w }, p);
    else if (kind === 'dots') { mk('circle', { cx: size / 4, cy: size / 4, r: w, fill: line }, p); mk('circle', { cx: size * 0.75, cy: size * 0.7, r: w * 0.8, fill: line }, p); }
    return `url(#${id})`;
  };
  let hidIcons = 0, made = 0;
  for (const [nm, R, th, walls] of CITY) {
    const b = pack.burgs.find((q) => q && q.name && q.name.includes(nm));
    if (!b) { log.push('没找到 ' + nm); continue; }
    const t = T[th], x = b.x, y = b.y, ph = rnd() * 6, rot = rnd() * 90;
    const g = mk('g', { id: 'mega_' + b.i }, cities);
    if (walls === 0) {
      // 阿卡迪亚：围着口子的环城，一圈一圈往外长（用户画的金光和黑井压在上面）
      mk('path', { d: wob(x, y, R * 1.08, ph, 0.6), fill: t.ground, opacity: 0.6 }, g);
      for (let k = 0; k < 10; k++) { const a0 = k * Math.PI / 5 + 0.1, a1 = a0 + Math.PI / 5 - 0.12; mk('path', { d: wedge(x, y, R * 0.6, R * 0.98, a0, a1), fill: pat(`ar_f${k}`, 0.9, rot + k * 31, t.mid, t.line, 0.12, k % 2 ? 'grid' : 'dots') }, g); }
      mk('path', { d: wob(x, y, R * 0.6, ph + 1, 0.4), fill: pat('ar_core', 0.7, rot, t.core, t.line, 0.13, 'grid') }, g);
      for (const f of [0.6, 0.98]) { mk('path', { d: wob(x, y, R * f, ph + f, 0.4), fill: 'none', stroke: t.wall, 'stroke-width': 0.7 }, g); mk('path', { d: wob(x, y, R * f, ph + f, 0.4), fill: 'none', stroke: t.hi, 'stroke-width': 0.22 }, g); }
      for (let k = 0; k < 12; k++) { const a = k * Math.PI / 6; mk('line', { x1: x + Math.cos(a) * R * 0.3, y1: y + Math.sin(a) * R * 0.3, x2: x + Math.cos(a) * R * 1.0, y2: y + Math.sin(a) * R * 1.0, stroke: t.line, 'stroke-width': 0.3, opacity: 0.9 }, g); }
    } else {
      const rings = walls === 3 ? [0.33, 0.62, 1.0] : [0.45, 1.0];
      const inner = rings[0], fieldIn = rings[rings.length - 2];
      // 城外的郊野，比墙外再大一圈
      mk('path', { d: wob(x, y, R * 1.22, ph, 1.4), fill: t.ground, opacity: 0.5 }, g);
      // 外圈墙里是田，一扇一扇换方向
      const nSec = 9;
      for (let k = 0; k < nSec; k++) {
        const a0 = (k / nSec) * Math.PI * 2 + ph, a1 = a0 + (Math.PI * 2) / nSec - 0.03;
        mk('path', { d: wedge(x, y, R * fieldIn, R * 0.99, a0, a1), fill: pat(`fl_${b.i}_${k}`, 0.75, rot + k * 47, t.f1, t.f2, 0.14, 'stripe') }, g);
      }
      // 墙里的卫城：田里一座一座小城，各自也有一圈墙
      const nSat = walls === 3 ? 9 : 6;
      for (let k = 0; k < nSat; k++) {
        const a = (k / nSat) * Math.PI * 2 + ph + 0.35, d = R * (fieldIn + (0.99 - fieldIn) * (0.45 + rnd() * 0.25)), r = R * (0.055 + rnd() * 0.035);
        const sx = x + Math.cos(a) * d, sy = y + Math.sin(a) * d;
        mk('circle', { cx: sx, cy: sy, r, fill: pat(`st_${b.i}_${k}`, 0.55, rnd() * 90, t.core, t.line, 0.1, 'grid') }, g);
        mk('circle', { cx: sx, cy: sy, r, fill: 'none', stroke: t.wall, 'stroke-width': 0.22 }, g);
      }
      // 中间那几圈是街坊
      if (walls === 3) mk('path', { d: wob(x, y, R * 0.62, ph + 2, 0.7), fill: pat(`md_${b.i}`, 0.8, rot + 20, t.mid, t.line, 0.12, 'dots') }, g);
      mk('path', { d: wob(x, y, R * inner, ph + 3, 0.6), fill: pat(`cr_${b.i}`, 0.62, rot, t.core, t.line, 0.12, 'grid') }, g);
      // 放射的大道，过墙的地方开门
      const nAve = walls === 3 ? 8 : 6;
      for (let k = 0; k < nAve; k++) {
        const a = (k / nAve) * Math.PI * 2 + ph * 0.3, bend = (rnd() - 0.5) * 0.18;
        const x1 = x + Math.cos(a) * R * 0.08, y1 = y + Math.sin(a) * R * 0.08;
        const mx = x + Math.cos(a + bend) * R * 0.6, my = y + Math.sin(a + bend) * R * 0.6;
        const x2 = x + Math.cos(a + bend * 1.6) * R * 1.12, y2 = y + Math.sin(a + bend * 1.6) * R * 1.12;
        mk('path', { d: `M${x1.toFixed(2)},${y1.toFixed(2)} Q${mx.toFixed(2)},${my.toFixed(2)} ${x2.toFixed(2)},${y2.toFixed(2)}`, fill: 'none', stroke: t.hi, 'stroke-width': Math.max(0.28, R * 0.022), opacity: 0.95 }, g);
        mk('path', { d: `M${x1.toFixed(2)},${y1.toFixed(2)} Q${mx.toFixed(2)},${my.toFixed(2)} ${x2.toFixed(2)},${y2.toFixed(2)}`, fill: 'none', stroke: t.line, 'stroke-width': Math.max(0.1, R * 0.008), opacity: 0.7 }, g);
      }
      // 城墙：一圈一圈，墙上有塔
      rings.forEach((f, k) => {
        const rr = R * f, w = Math.max(0.35, R * (k === rings.length - 1 ? 0.055 : 0.04));
        const d = wob(x, y, rr, ph + k * 1.3, 0.5);
        mk('path', { d, fill: 'none', stroke: t.wall, 'stroke-width': w }, g);
        mk('path', { d, fill: 'none', stroke: t.hi, 'stroke-width': w * 0.36, 'stroke-dasharray': `${(w * 0.9).toFixed(2)} ${(w * 0.5).toFixed(2)}` }, g);
        const nT = Math.max(8, Math.round((2 * Math.PI * rr) / (w * 7)));
        for (let j = 0; j < nT; j++) { const a = (j / nT) * Math.PI * 2; const rw = rr * (1 + 0.5 * (0.035 * Math.sin(3 * a + ph + k * 1.3) + 0.025 * Math.sin(7 * a + (ph + k * 1.3) * 1.7))); mk('circle', { cx: x + Math.cos(a) * rw, cy: y + Math.sin(a) * rw, r: w * 0.62, fill: t.hi, stroke: t.wall, 'stroke-width': w * 0.28 }, g); }
      });
      // 城心的宫
      const kr = R * 0.09;
      if (th === 'raven') {
        mk('path', { d: `M${x - kr * 0.8},${y + kr} L${x},${y - kr * 4.2} L${x + kr * 0.8},${y + kr} Z`, fill: '#2b2727', stroke: '#e6e0d6', 'stroke-width': 0.18, filter: 'url(#playShadow)' }, g);
      } else if (th === 'holy') {
        for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4; mk('line', { x1: x, y1: y, x2: x + Math.cos(a) * kr * 2.6, y2: y + Math.sin(a) * kr * 2.6, stroke: '#fff6d8', 'stroke-width': 0.35 }, g); }
        mk('circle', { cx: x, cy: y, r: kr * 1.1, fill: t.keep, stroke: t.wall, 'stroke-width': 0.25 }, g);
      } else {
        mk('circle', { cx: x, cy: y, r: kr * 2.4, fill: t.keep, opacity: 0.28 }, g);
        mk('path', { d: `M${x},${y - kr * 1.6} L${x + kr * 1.15},${y} L${x},${y + kr * 1.6} L${x - kr * 1.15},${y} Z`, fill: t.keep, stroke: t.wall, 'stroke-width': Math.max(0.2, kr * 0.25) }, g);
      }
    }
    for (const u of document.querySelectorAll('#terrain use')) {
      const ux = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2, uy = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2;
      if ((ux - x) ** 2 + (uy - y) ** 2 <= (R * 1.12) ** 2) { u.style.display = 'none'; hidIcons++; }
    }
    for (const sel of [`#burg${b.i}`, `#anchor${b.i}`]) { const e = document.querySelector(sel); if (e) e.style.display = 'none'; }
    b._mega = R; made++;
  }
  if (!document.getElementById('playShadow')) { const sh = mk('filter', { id: 'playShadow', x: '-50%', y: '-50%', width: '200%', height: '200%' }, pdefs); mk('feDropShadow', { dx: 0.5, dy: 0.9, stdDeviation: 0.5, 'flood-color': '#1b2733', 'flood-opacity': 0.5 }, sh); }
  log.push('巨城 ' + made + '，藏了地形符号 ' + hidIcons);

  // ---- 3. 用户画的长垒和大迷宫 ----
  const ov = mk('g', { id: 'playOverlay' }, null);
  vb.insertBefore(ov, document.getElementById('labels'));
  ov.innerHTML = 'AUL_SVG';

  // ---- 4. 巨构和超自然景观 ----
  const mg = mk('g', { id: 'playMagic' }, null);
  vb.insertBefore(mg, document.getElementById('labels'));
  const lg = mk('linearGradient', { id: 'pCrystal', x1: 0, y1: 0, x2: 1, y2: 0 }, pdefs);
  mk('stop', { offset: '0', 'stop-color': '#9fd0ff' }, lg); mk('stop', { offset: '0.45', 'stop-color': '#eef8ff' }, lg); mk('stop', { offset: '1', 'stop-color': '#5d8fd6' }, lg);
  const glow = (id, c, o) => { const rg = mk('radialGradient', { id }, pdefs); mk('stop', { offset: '0', 'stop-color': c, 'stop-opacity': o }, rg); mk('stop', { offset: '1', 'stop-color': c, 'stop-opacity': 0 }, rg); };
  glow('pGlowBlue', '#bfe3ff', 0.85); glow('pGlowGold', '#ffe7a8', 0.85); glow('pGlowRed', '#ff6a4a', 0.7); glow('pGlowDeep', '#0f2f3d', 0.75);
  // 寒天之钉：北边冰原上一簇幽蓝的晶钉
  mk('ellipse', { cx: 1232, cy: 116, rx: 46, ry: 26, fill: 'url(#pGlowBlue)' }, mg);
  for (let k = 0; k < 30; k++) {
    const a = rnd() * Math.PI * 2, d = Math.sqrt(rnd()) * 32;
    const cx = 1232 + Math.cos(a) * d * 1.3, cy = 114 + Math.sin(a) * d * 0.7;
    const h = 6 + rnd() * 14, w = 1.1 + rnd() * 1.2, lean = (rnd() - 0.5) * 2.6;
    mk('path', { d: `M${cx - w},${cy} L${cx + lean},${cy - h} L${cx + w},${cy} L${cx},${cy + w * 0.6} Z`, fill: 'url(#pCrystal)', stroke: '#2f5c98', 'stroke-width': 0.18, filter: 'url(#playShadow)', opacity: 0.95 }, mg);
  }
  // 星环：奥法总塔外一道浮在天上的光环，七座浮塔挂在环上，地上一道淡影
  { const cx = 1363, cy = 324, rx = 40, ry = 14;
    mk('ellipse', { cx: cx + 4, cy: cy + 9, rx, ry, fill: 'none', stroke: '#26303c', 'stroke-width': 1.6, opacity: 0.16 }, mg);
    mk('ellipse', { cx, cy, rx, ry, fill: 'none', stroke: '#9ec8ff', 'stroke-width': 3.6, opacity: 0.32 }, mg);
    mk('ellipse', { cx, cy, rx, ry, fill: 'none', stroke: '#f5faff', 'stroke-width': 1.1, opacity: 0.95 }, mg);
    for (let k = 0; k < 7; k++) { const r = (k / 7) * Math.PI * 2 + 0.3, tx = cx + Math.cos(r) * rx, ty = cy + Math.sin(r) * ry; mk('ellipse', { cx: tx, cy: ty + 0.5, rx: 2.4, ry: 0.9, fill: '#7d8ea8', opacity: 0.6 }, mg); mk('path', { d: `M${tx - 1.6},${ty + 0.6} L${tx},${ty - 5.4} L${tx + 1.6},${ty + 0.6} Z`, fill: '#f8f3e6', stroke: '#45536b', 'stroke-width': 0.3, filter: 'url(#playShadow)' }, mg); }
    mk('path', { d: `M${cx - 2.4},${cy + 1} L${cx},${cy - 10} L${cx + 2.4},${cy + 1} Z`, fill: '#fffaf0', stroke: '#45536b', 'stroke-width': 0.35, filter: 'url(#playShadow)' }, mg); }
  // 曜冠空环城：山巅外一圈断开的城环，环上一段一段都是城
  { const ax = 1298, ay = 372, arx = 30, ary = 10.5;
    mk('ellipse', { cx: ax, cy: ay, rx: arx + 8, ry: ary + 6, fill: 'url(#pGlowGold)', opacity: 0.7 }, mg);
    const cityFill = pat('ring_city', 0.6, 25, '#eadcbc', '#8c7650', 0.11, 'grid');
    for (let k = 0; k < 9; k++) {
      const a0 = k * 40 + 5, a1 = a0 + 27;
      const p = (deg, s = 1) => { const r = deg * Math.PI / 180; return [ax + Math.cos(r) * arx * s, ay + Math.sin(r) * ary * s]; };
      const [x0, y0] = p(a0), [x1, y1] = p(a1), [x2, y2] = p(a1, 0.8), [x3, y3] = p(a0, 0.8);
      mk('path', { d: `M${x0},${y0} A${arx},${ary} 0 0,1 ${x1},${y1} L${x2},${y2} A${arx * 0.8},${ary * 0.8} 0 0,0 ${x3},${y3} Z`, fill: cityFill, stroke: '#5f5038', 'stroke-width': 0.4, filter: 'url(#playShadow)' }, mg);
    } }
  // 星落群岛：双月内海里一串骨头似的低岛，透一点蓝光
  { const lakeEl = document.getElementById('feature_9'); const pt = document.getElementById('map').createSVGPoint(); let n = 0;
    for (let k = 0; k < 80 && n < 8; k++) {
      const ix = 1345 + rnd() * 90, iy = 1122 + rnd() * 50; pt.x = ix; pt.y = iy;
      if (!lakeEl || !lakeEl.isPointInFill(pt)) continue;
      const L = 5 + rnd() * 5, W = 1.5 + rnd() * 0.9, ang = (rnd() - 0.5) * 80;
      const gg = mk('g', { transform: `translate(${ix.toFixed(2)},${iy.toFixed(2)}) rotate(${ang.toFixed(1)})` }, mg);
      mk('ellipse', { cx: 0, cy: 0, rx: L + 3.4, ry: W + 3, fill: 'url(#pGlowBlue)' }, gg);
      mk('path', { d: `M${-L},0 C${-L},${-W * 1.6} ${-L + W * 1.6},${-W * 1.4} ${-L + W * 1.4},${-W * 0.5} L${L - W * 1.4},${-W * 0.5} C${L - W * 1.6},${-W * 1.4} ${L},${-W * 1.6} ${L},0 C${L},${W * 1.6} ${L - W * 1.6},${W * 1.4} ${L - W * 1.4},${W * 0.5} L${-L + W * 1.4},${W * 0.5} C${-L + W * 1.6},${W * 1.4} ${-L},${W * 1.6} ${-L},0 Z`, fill: '#efe7d3', stroke: '#6f81a3', 'stroke-width': 0.4 }, gg);
      n++;
    } log.push('星落群岛 ' + n); }
  // 玻璃沙坡：炽镜村一带，沙海边沿那几圈格子发亮，离村子越远越淡
  { let c0 = -1, best = 1e9; for (let i = 0; i < C.i.length; i++) { if (C.biome[i] !== 1) continue; const d = (C.p[i][0] - 1144) ** 2 + (C.p[i][1] - 1160) ** 2; if (d < best) { best = d; c0 = i; } }
    const comp = new Uint8Array(C.i.length); const st = [c0]; comp[c0] = 1; while (st.length) { const i = st.pop(); for (const n of C.c[i]) if (!comp[n] && C.biome[n] === 1) { comp[n] = 1; st.push(n); } }
    const dist = new Int16Array(C.i.length).fill(-1); let q = [];
    for (let i = 0; i < C.i.length; i++) if (comp[i] && C.c[i].some((n) => !comp[n] && C.h[n] >= 20)) { dist[i] = 0; q.push(i); }
    for (let d = 1; d < 4; d++) { const nq = []; for (const i of q) for (const n of C.c[i]) if (comp[n] && dist[n] < 0) { dist[n] = d; nq.push(n); } q = nq; }
    const gp = mk('pattern', { id: 'pGlass', width: 2.2, height: 2.2, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(-35)' }, pdefs);
    mk('rect', { width: 2.2, height: 2.2, fill: '#f2fbfd', opacity: 0.6 }, gp); mk('path', { d: 'M0,0.5H2.2', stroke: '#ffffff', 'stroke-width': 0.4 }, gp); mk('path', { d: 'M0,1.6H2.2', stroke: '#bfe6f0', 'stroke-width': 0.18 }, gp);
    const rgm = mk('radialGradient', { id: 'pGlassFade', cx: 1144, cy: 1150, r: 170, gradientUnits: 'userSpaceOnUse' }, pdefs);
    mk('stop', { offset: '0', 'stop-color': '#fff' }, rgm); mk('stop', { offset: '0.55', 'stop-color': '#fff', 'stop-opacity': 0.7 }, rgm); mk('stop', { offset: '1', 'stop-color': '#fff', 'stop-opacity': 0 }, rgm);
    const m = mk('mask', { id: 'pGlassMask', maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 2200, height: 1400 }, pdefs); mk('rect', { x: 0, y: 0, width: 2200, height: 1400, fill: 'url(#pGlassFade)' }, m);
    const gg = mk('g', { mask: 'url(#pGlassMask)' }, mg); let cnt = 0;
    for (const [d, op] of [[0, 0.95], [1, 0.7], [2, 0.45], [3, 0.25]]) { const cells = []; for (let i = 0; i < C.i.length; i++) if (dist[i] === d) cells.push(i); cnt += cells.length; mk('path', { d: cells.map((i) => 'M' + C.v[i].map((v) => P[v][0].toFixed(2) + ',' + P[v][1].toFixed(2)).join('L') + 'Z').join(''), fill: 'url(#pGlass)', opacity: op }, gg); }
    log.push('玻璃沙坡格子 ' + cnt); }
  // 黑曜环山：烬灭之都外那一圈山压成黑红，底下的地也暗一层
  { const ann = mk('path', { d: wob(616, 714, 128, 0.4, 0.8) + wob(616, 714, 52, 1.1, 0.8), 'fill-rule': 'evenodd', fill: '#2a2224', opacity: 0.2, mask: 'url(#land)' }, null); vb.insertBefore(ann, document.getElementById('rivers'));
    let dark = 0; for (const u of document.querySelectorAll('#terrain use')) { const ux = +u.getAttribute('x'), uy = +u.getAttribute('y'); const d = Math.hypot(ux - 616, uy - 714); if (d > 52 && d < 128 && /mount|hill/.test(u.getAttribute('href'))) { u.setAttribute('style', 'filter: brightness(0.38) sepia(0.8) hue-rotate(-38deg) saturate(3.2)'); dark++; } }
    log.push('环山 ' + dark); }
  // 赤盐沉宫：盐海里露出半截宫顶
  { const sg = mk('g', { transform: 'translate(357,1075) scale(1.7)', filter: 'url(#playShadow)' }, mg);
    mk('ellipse', { cx: 0, cy: 1.2, rx: 8, ry: 2.8, fill: '#d98f8f', opacity: 0.45 }, sg);
    mk('path', { d: 'M-5,1 Q-5,-4 0,-6 Q5,-4 5,1 Z', fill: '#f4e9e4', stroke: '#8a4b4b', 'stroke-width': 0.35 }, sg);
    mk('path', { d: 'M-2.2,1 L-2.2,-2.6 M0,1 L0,-4.2 M2.2,1 L2.2,-2.6', stroke: '#b97373', 'stroke-width': 0.3 }, sg); }
  // 黑潮螺旋城：西海里一圈螺壳，从深水里透上来
  { mk('ellipse', { cx: 146, cy: 819, rx: 30, ry: 24, fill: 'url(#pGlowDeep)' }, mg);
    let sp = ''; for (let a = 0; a <= 6 * Math.PI; a += 0.12) { const r = 1.5 + a * 1.35; sp += (sp ? 'L' : 'M') + (146 + Math.cos(a) * r).toFixed(2) + ',' + (819 + Math.sin(a) * r * 0.78).toFixed(2); }
    mk('path', { d: sp, fill: 'none', stroke: '#e9f4f6', 'stroke-width': 1.3, opacity: 0.6 }, mg);
    mk('path', { d: sp, fill: 'none', stroke: '#123b4c', 'stroke-width': 0.4, opacity: 0.75 }, mg); }

  // ---- 5. 巨城的名字 ----
  if (!document.getElementById('pFont')) { const l = document.createElement('link'); l.id = 'pFont'; l.rel = 'stylesheet'; l.href = 'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700;900&display=swap'; document.head.appendChild(l); }
  const lab = mk('g', { id: 'playLabels', 'font-family': '"Noto Serif SC", serif', 'font-weight': 900, 'text-anchor': 'middle', fill: '#2c261f', stroke: '#f6f0e2', 'stroke-width': 1.6, 'paint-order': 'stroke', 'stroke-linejoin': 'round' }, vb);
  const names = [];
  for (const [nm, R] of CITY) { const b = pack.burgs.find((q) => q && q.name && q.name.includes(nm)); if (!b) continue; const fs = Math.max(6.5, R * 0.42); mk('text', { x: b.x, y: b.y + R * 1.12 + fs * 0.95, 'font-size': fs, 'letter-spacing': fs * 0.12 }, lab).textContent = b.name; names.push(b.name); }
  for (const [nm, x, y, fs] of [['寒天之钉', 1232, 146, 8], ['星环', 1363, 346, 8], ['曜冠空环城', 1298, 396, 7.5], ['星落群岛', 1390, 1186, 7], ['玻璃沙坡', 1150, 1205, 6.5], ['黑曜环山', 660, 842, 7.5], ['赤盐沉宫', 357, 1098, 6.5], ['黑潮螺旋城', 146, 852, 7]]) mk('text', { x, y, 'font-size': fs, 'letter-spacing': fs * 0.1, fill: '#3a3a52', 'font-weight': 700 }, lab).textContent = nm;
  try { await document.fonts.load('900 20px "Noto Serif SC"', names.join('') + '寒天之钉星环曜冠空环城星落群岛玻璃沙坡黑曜环山赤盐沉宫黑潮螺旋'); await new Promise((r) => setTimeout(r, 1500)); log.push('字体 ' + document.fonts.check('900 20px "Noto Serif SC"', '金鸢城')); } catch (e) { log.push('字体没载上 ' + e); }
  return log.join('；');
})();
