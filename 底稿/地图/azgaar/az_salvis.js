// 月银纪·萨尔维斯末年（约9800年）样张：在 az_reset.sh、az_biwan_run.js、az_nanyuan.js 之后跑。
//   巨城照城市平面画（穹都、神渡城最大），穹都上空浮着上城那几块，神渡上空浮着客星城（倒托的山头）
//   星坑盆地的坑沿、月银原的银光、寒天之钉、北辰塔、扛岛、赤金纪的黄金城、终北的断谷
//   三百多座辉塔和圣荫，七曜的元素君王锁在哪（潮宫、引雷台、风塔、蓝焰铸城、客星城），橙冰没拿下
//   空路三条，王道一条；地名一纪一套（帝国、行省、大地方、城），罗盘和比例尺照 Azgaar 自己的
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const vb = document.getElementById('viewbox');
  const defs = document.getElementById('featurePaths').closest('defs');
  for (const id of ['svCities', 'svMagic', 'svLabels', 'svDefs', 'svGround', 'svLights']) { const o = document.getElementById(id); if (o) o.remove(); }
  const pdefs = mk('g', { id: 'svDefs' }, defs);
  const log = [];
  let seed = 23; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const C = pack.cells, P = pack.vertices.p;
  const pt = document.getElementById('map').createSVGPoint();
  const landMaskShape = document.querySelector('#land');
  const isLandAt = (x, y) => { let best = -1, bd = 1e9; const gx = Math.floor(x / 12), gy = Math.floor(y / 12); for (const i of (window.__cellGrid[gx + ',' + gy] || [])) { const d = (C.p[i][0] - x) ** 2 + (C.p[i][1] - y) ** 2; if (d < bd) { bd = d; best = i; } } if (best < 0) return false; return C.h[best] >= 20 && !(pack.features[C.f[best]] && pack.features[C.f[best]].type === 'lake' && C.f[best] !== 9); };
  if (!window.__cellGrid) { const g = {}; for (let i = 0; i < C.i.length; i++) { const gx = Math.floor(C.p[i][0] / 12), gy = Math.floor(C.p[i][1] / 12); for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) { const k = (gx + a) + ',' + (gy + b); (g[k] || (g[k] = [])).push(i); } } window.__cellGrid = g; }
  const cellAt = (x, y) => { let best = -1, bd = 1e9; const gx = Math.floor(x / 12), gy = Math.floor(y / 12); for (const i of (window.__cellGrid[gx + ',' + gy] || [])) { const d = (C.p[i][0] - x) ** 2 + (C.p[i][1] - y) ** 2; if (d < bd) { bd = d; best = i; } } return best; };

  // ---- 共用的纹样和光 ----
  const glow = (id, c, o) => { const rg = mk('radialGradient', { id }, pdefs); mk('stop', { offset: '0', 'stop-color': c, 'stop-opacity': o }, rg); mk('stop', { offset: '0.45', 'stop-color': c, 'stop-opacity': o * 0.45 }, rg); mk('stop', { offset: '1', 'stop-color': c, 'stop-opacity': 0 }, rg); };
  glow('svGold', '#ffe6a3', 0.9); glow('svHalo', '#fff1c4', 0.55); glow('svBlue', '#9fd4ff', 0.9); glow('svViolet', '#c9a2ff', 0.9); glow('svCyan', '#9ff0dc', 0.9); glow('svFlame', '#bfe6ff', 0.95); glow('svAmber', '#ffc76a', 0.95); glow('svIce', '#ffd3a6', 0.7); glow('svSilver', '#eef3ff', 0.85);
  const sh = mk('filter', { id: 'svShadow', x: '-50%', y: '-50%', width: '200%', height: '200%' }, pdefs); mk('feDropShadow', { dx: 0.6, dy: 1.1, stdDeviation: 0.6, 'flood-color': '#1b2733', 'flood-opacity': 0.45 }, sh);
  const sh2 = mk('filter', { id: 'svBlur', x: '-50%', y: '-50%', width: '200%', height: '200%' }, pdefs); mk('feGaussianBlur', { stdDeviation: 2.2 }, sh2);
  const pat = (id, size, rot, bg, line, w, kind) => {
    const p = mk('pattern', { id, width: size, height: size, patternUnits: 'userSpaceOnUse', patternTransform: `rotate(${rot})` }, pdefs);
    mk('rect', { width: size, height: size, fill: bg }, p);
    if (kind === 'grid') mk('path', { d: `M0,${size / 2}H${size}M${size / 2},0V${size}`, stroke: line, 'stroke-width': w }, p);
    else if (kind === 'stripe') mk('path', { d: `M0,${size / 2}H${size}`, stroke: line, 'stroke-width': w }, p);
    else if (kind === 'dots') { mk('circle', { cx: size / 4, cy: size / 4, r: w, fill: line }, p); mk('circle', { cx: size * 0.75, cy: size * 0.7, r: w * 0.8, fill: line }, p); }
    return `url(#${id})`;
  };
  const wob = (x, y, r, ph, amp = 1) => { let d = ''; for (let a = 0; a < 360; a += 5) { const t = a * Math.PI / 180; const rr = r * (1 + amp * (0.035 * Math.sin(3 * t + ph) + 0.025 * Math.sin(7 * t + ph * 1.7))); d += (d ? 'L' : 'M') + (x + Math.cos(t) * rr).toFixed(2) + ',' + (y + Math.sin(t) * rr).toFixed(2); } return d + 'Z'; };
  const wedge = (x, y, r1, r2, a0, a1) => { const pts = []; for (let a = a0; a <= a1 + 1e-6; a += (a1 - a0) / 12) pts.push([x + Math.cos(a) * r2, y + Math.sin(a) * r2]); for (let a = a1; a >= a0 - 1e-6; a -= (a1 - a0) / 12) pts.push([x + Math.cos(a) * r1, y + Math.sin(a) * r1]); return 'M' + pts.map((p) => p[0].toFixed(2) + ',' + p[1].toFixed(2)).join('L') + 'Z'; };

  // ---- 城市平面 ----
  const T = {
    imperial: { ground: '#dcd8cc', f1: '#cfd0a8', f2: '#a9ab84', mid: '#d0cdc2', core: '#bfbcb4', line: '#7b7a80', wall: '#4b4d5e', hi: '#f7f6f1', keep: '#dfe9ff' },
    gold:     { ground: '#d9cdb1', f1: '#cdc79a', f2: '#a9a274', mid: '#cbb994', core: '#b9a47e', line: '#8a7552', wall: '#5b4a33', hi: '#f3e7c6', keep: '#f0c75e' },
    holy:     { ground: '#e1dccd', f1: '#d4d0a8', f2: '#b1ad83', mid: '#d8d2c2', core: '#c9c2b0', line: '#958c75', wall: '#6b624d', hi: '#fffdf4', keep: '#fff6d8' },
    silver:   { ground: '#d6d6cc', f1: '#c8cba6', f2: '#a5aa86', mid: '#c2c2b6', core: '#a9aba5', line: '#76787a', wall: '#4b4f57', hi: '#f2f4f7', keep: '#e8eef8' },
    sand:     { ground: '#ddd2b5', f1: '#d6cc9a', f2: '#b2a676', mid: '#cfbf9c', core: '#bba682', line: '#8a7552', wall: '#5f4d36', hi: '#f6ead0', keep: '#f3c76a' },
    forge:    { ground: '#c4b4a2', f1: '#b8ab92', f2: '#958670', mid: '#b09a86', core: '#9a7c66', line: '#5d4535', wall: '#33251c', hi: '#ead7c4', keep: '#bfe6ff' },
    bone:     { ground: '#dcd8cc', f1: '#cfcabb', f2: '#a9a393', mid: '#cbc6b8', core: '#b4ae9f', line: '#7f796b', wall: '#4f4b42', hi: '#fbf8ef', keep: '#f3f0e4' },
    rose:     { ground: '#dccbbd', f1: '#d2b9a4', f2: '#b88f80', mid: '#ccb0a2', core: '#b9938a', line: '#87605a', wall: '#5a3a36', hi: '#f6e6de', keep: '#e48aa0' },
    mirror:   { ground: '#c9c1cf', f1: '#bdb5c6', f2: '#968aa6', mid: '#b5abbf', core: '#9a8faa', line: '#62577a', wall: '#372e4b', hi: '#efe9f6', keep: '#c79bff' },
    tide:     { ground: '#c4cdcd', f1: '#b6c0ac', f2: '#91a08c', mid: '#aab8ba', core: '#8ea2a8', line: '#536a73', wall: '#26404b', hi: '#e6f0f2', keep: '#4fa6c9' },
  };
  const cities = mk('g', { id: 'svCities', mask: 'url(#land)' }, null);
  vb.insertBefore(cities, document.getElementById('rivers'));
  const hideIconsIn = (x, y, r) => { for (const u of document.querySelectorAll('#terrain use')) { const ux = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2, uy = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2; if ((ux - x) ** 2 + (uy - y) ** 2 <= r * r) u.style.display = 'none'; } };
  window.__svHide = window.__svHide || [];
  const cityPlan = (key, x, y, R, th, walls) => {
    const t = T[th], ph = rnd() * 6, rot = rnd() * 90;
    const g = mk('g', { id: 'sv_' + key }, cities);
    const rings = walls === 3 ? [0.33, 0.62, 1.0] : [0.45, 1.0];
    const inner = rings[0], fieldIn = rings[rings.length - 2];
    mk('path', { d: wob(x, y, R * 1.22, ph, 1.4), fill: t.ground, opacity: 0.5 }, g);
    const nSec = 9;
    for (let k = 0; k < nSec; k++) { const a0 = (k / nSec) * Math.PI * 2 + ph, a1 = a0 + (Math.PI * 2) / nSec - 0.03; mk('path', { d: wedge(x, y, R * fieldIn, R * 0.99, a0, a1), fill: pat(`fl_${key}_${k}`, 0.75, rot + k * 47, t.f1, t.f2, 0.14, 'stripe') }, g); }
    const nSat = walls === 3 ? 9 : 6;
    for (let k = 0; k < nSat; k++) { const a = (k / nSat) * Math.PI * 2 + ph + 0.35, d = R * (fieldIn + (0.99 - fieldIn) * (0.45 + rnd() * 0.25)), r = R * (0.055 + rnd() * 0.035); const sx = x + Math.cos(a) * d, sy = y + Math.sin(a) * d; mk('circle', { cx: sx, cy: sy, r, fill: pat(`st_${key}_${k}`, 0.55, rnd() * 90, t.core, t.line, 0.1, 'grid') }, g); mk('circle', { cx: sx, cy: sy, r, fill: 'none', stroke: t.wall, 'stroke-width': 0.22 }, g); }
    if (walls === 3) mk('path', { d: wob(x, y, R * 0.62, ph + 2, 0.7), fill: pat(`md_${key}`, 0.8, rot + 20, t.mid, t.line, 0.12, 'dots') }, g);
    mk('path', { d: wob(x, y, R * inner, ph + 3, 0.6), fill: pat(`cr_${key}`, 0.62, rot, t.core, t.line, 0.12, 'grid') }, g);
    const nAve = walls === 3 ? 8 : 6;
    for (let k = 0; k < nAve; k++) { const a = (k / nAve) * Math.PI * 2 + ph * 0.3, bend = (rnd() - 0.5) * 0.18; const x1 = x + Math.cos(a) * R * 0.08, y1 = y + Math.sin(a) * R * 0.08; const mx = x + Math.cos(a + bend) * R * 0.6, my = y + Math.sin(a + bend) * R * 0.6; const x2 = x + Math.cos(a + bend * 1.6) * R * 1.12, y2 = y + Math.sin(a + bend * 1.6) * R * 1.12; const dd = `M${x1.toFixed(2)},${y1.toFixed(2)} Q${mx.toFixed(2)},${my.toFixed(2)} ${x2.toFixed(2)},${y2.toFixed(2)}`; mk('path', { d: dd, fill: 'none', stroke: t.hi, 'stroke-width': Math.max(0.28, R * 0.022), opacity: 0.95 }, g); mk('path', { d: dd, fill: 'none', stroke: t.line, 'stroke-width': Math.max(0.1, R * 0.008), opacity: 0.7 }, g); }
    rings.forEach((f, k) => { const rr = R * f, w = Math.max(0.35, R * (k === rings.length - 1 ? 0.055 : 0.04)); const d = wob(x, y, rr, ph + k * 1.3, 0.5); mk('path', { d, fill: 'none', stroke: t.wall, 'stroke-width': w }, g); mk('path', { d, fill: 'none', stroke: t.hi, 'stroke-width': w * 0.36, 'stroke-dasharray': `${(w * 0.9).toFixed(2)} ${(w * 0.5).toFixed(2)}` }, g); const nT = Math.max(8, Math.round((2 * Math.PI * rr) / (w * 7))); for (let j = 0; j < nT; j++) { const a = (j / nT) * Math.PI * 2; const rw = rr * (1 + 0.5 * (0.035 * Math.sin(3 * a + ph + k * 1.3) + 0.025 * Math.sin(7 * a + (ph + k * 1.3) * 1.7))); mk('circle', { cx: x + Math.cos(a) * rw, cy: y + Math.sin(a) * rw, r: w * 0.62, fill: t.hi, stroke: t.wall, 'stroke-width': w * 0.28 }, g); } });
    const kr = R * 0.09;
    mk('circle', { cx: x, cy: y, r: kr * 2.4, fill: t.keep, opacity: 0.3 }, g);
    mk('path', { d: `M${x},${y - kr * 1.6} L${x + kr * 1.15},${y} L${x},${y + kr * 1.6} L${x - kr * 1.15},${y} Z`, fill: t.keep, stroke: t.wall, 'stroke-width': Math.max(0.2, kr * 0.25) }, g);
    window.__svHide.push([x, y, R * 1.12]);
    return g;
  };
  const smallCity = (x, y, th) => { const t = T[th] || T.gold; mk('circle', { cx: x, cy: y, r: 2.1, fill: t.core, stroke: t.wall, 'stroke-width': 0.55 }, cities); mk('circle', { cx: x, cy: y, r: 0.7, fill: t.keep }, cities); };
  const ruin = (x, y, R) => { const g = mk('g', {}, cities); for (const f of [0.4, 0.72, 1.0]) mk('path', { d: wob(x, y, R * f, f * 3, 0.6), fill: 'none', stroke: '#6d665a', 'stroke-width': 0.5, 'stroke-dasharray': '2.2 1.6', opacity: 0.8 }, g); mk('path', { d: wob(x, y, R, 1, 0.6), fill: '#cfc8b6', opacity: 0.25 }, g); for (let k = 0; k < 7; k++) { const a = rnd() * 6.28, d = rnd() * R * 0.7; mk('rect', { x: x + Math.cos(a) * d - 0.8, y: y + Math.sin(a) * d - 0.5, width: 1.6, height: 1, fill: '#8a8272', opacity: 0.8 }, g); } };

  const MEGA = [
    ['qiongdu', 616, 714, 26, 'imperial', 3], ['shendu', 1100, 672, 21, 'gold', 3], ['xinghu', 1952, 443.5, 15, 'silver', 3],
    ['baiguan', 1186, 756, 13, 'holy', 2], ['xingguan', 1386, 560, 12, 'holy', 2], ['jinsha', 1080, 1110, 11, 'sand', 2],
    ['lanyan', 528, 980, 12, 'forge', 2], ['changmian', 374, 658, 11, 'bone', 2], ['liuli', 682, 435, 9, 'rose', 2],
    ['jinghu', 497, 302, 10, 'mirror', 2], ['chaomen', 198, 868, 9, 'tide', 2], ['luxin', 1562, 1106, 9, 'forge', 2],
  ];
  for (const m of MEGA) cityPlan(...m);
  ruin(1518, 742, 12);
  window.__svHide.push([1518, 742, 13]);
  const SMALL = [[1185, 425, 'gold'], [1290, 450, 'gold'], [1385, 415, 'gold'], [545, 355, 'gold'], [410, 950, 'sand'], [1780, 750, 'tide'], [1892.4, 953.7, 'gold'], [1385, 852, 'gold'], [1300, 800, 'gold'], [1314, 806, 'gold'], [1292, 992, 'sand'], [612, 540, 'forge'], [832, 215, 'silver'], [630, 385, 'gold'], [720, 400, 'forge'], [1625, 515, 'gold'], [1979.8, 559, 'holy'], [1452, 1176, 'forge'], [612, 532, 'forge'], [1465, 740, 'gold']];
  for (const [x, y, th] of SMALL) smallCity(x, y, th);

  // ---- 地上的大东西 ----
  const ground = mk('g', { id: 'svGround' }, null);
  vb.insertBefore(ground, document.getElementById('rivers'));
  // 星坑盆地的坑沿：一圈朝里的短线
  { const cx = 1100, cy = 672, r = 92; for (let k = 0; k < 150; k++) { const a = k / 150 * Math.PI * 2, rr = r * (1 + 0.03 * Math.sin(5 * a)); const x1 = cx + Math.cos(a) * rr, y1 = cy + Math.sin(a) * rr, x2 = cx + Math.cos(a) * (rr - 4.5 - (k % 3)), y2 = cy + Math.sin(a) * (rr - 4.5 - (k % 3)); mk('line', { x1, y1, x2, y2, stroke: '#8d7f66', 'stroke-width': 0.55, opacity: 0.55 }, ground); } mk('path', { d: wob(cx, cy, r, 0.3, 0.6), fill: 'none', stroke: '#8d7f66', 'stroke-width': 0.7, opacity: 0.6 }, ground); }
  // 月银原：北边雪原西头一片泛银光的原，坑一个一个（11-08 从 840,140 挪到冰上，原来那一点落在海里）
  { const MX = 905, MY = 168; mk('ellipse', { cx: MX, cy: MY, rx: 62, ry: 30, fill: 'url(#svSilver)' }, ground); for (let k = 0; k < 22; k++) { const a = rnd() * 6.28, d = Math.sqrt(rnd()) * 42; const x = MX + Math.cos(a) * d * 1.3, y = MY + Math.sin(a) * d * 0.6; const r = 1 + rnd() * 2.4; if (!isLandAt(x, y)) continue; mk('ellipse', { cx: x, cy: y, rx: r, ry: r * 0.7, fill: '#cfd6e6', stroke: '#7d869c', 'stroke-width': 0.3, opacity: 0.9 }, ground); } }
  // 终北的断谷
  { let d = 'M960,128'; for (let k = 1; k <= 8; k++) d += ` L${960 + k * 8 + (rnd() - 0.5) * 3},${128 + Math.sin(k) * 4 + k * 1.5}`; mk('path', { d, fill: 'none', stroke: '#2b3442', 'stroke-width': 1.6, opacity: 0.75 }, ground); mk('path', { d, fill: 'none', stroke: '#9fb0c8', 'stroke-width': 0.4, opacity: 0.8, transform: 'translate(0.6,-0.6)' }, ground); }
  // 扛岛：西海里一座岛
  { const ix = 110, iy = 540; let d = ''; for (let a = 0; a < 360; a += 8) { const t = a * Math.PI / 180, r = 9 * (1 + 0.18 * Math.sin(3 * t + 1) + 0.1 * Math.sin(7 * t)); d += (d ? 'L' : 'M') + (ix + Math.cos(t) * r * 1.3).toFixed(2) + ',' + (iy + Math.sin(t) * r * 0.8).toFixed(2); } d += 'Z'; const ig = mk('g', {}, null); vb.insertBefore(ig, document.getElementById('rivers')); mk('path', { d, fill: '#eef6fb' }, ig); mk('path', { d, fill: '#bdb49a', opacity: 0.6 }, ig); mk('path', { d, fill: 'none', stroke: '#1f3846', 'stroke-width': 0.7, opacity: 0.5 }, ig); mk('path', { d: `M${ix - 4},${iy + 1} L${ix - 1},${iy - 4} L${ix + 2},${iy + 1} Z M${ix + 1},${iy + 2} L${ix + 4},${iy - 2} L${ix + 7},${iy + 2} Z`, fill: '#efece4', stroke: '#6b6458', 'stroke-width': 0.35 }, ig); }

  // ---- 天上的、发光的 ----
  const mg = mk('g', { id: 'svMagic' }, null);
  vb.insertBefore(mg, document.getElementById('labels'));
  // 王道：金冕城西门到神渡东边的坡
  { const d = 'M1506,744 C1440,740 1380,742 1330,740 S1215,738 1150,700'; mk('path', { d, fill: 'none', stroke: '#f4ead2', 'stroke-width': 1.6, opacity: 0.9 }, mg); mk('path', { d, fill: 'none', stroke: '#8a6e3e', 'stroke-width': 0.6, 'stroke-dasharray': '3 1.2' }, mg); }
  // 辉塔：三百二十座，帝畿最密，丘陵、雪原、林子、裂影之地不立
  const lights = mk('g', { id: 'svLights' }, mg);
  const centers = [[616, 714, 170, 0.36], [1100, 672, 120, 0.14], [1186, 756, 90, 0.09], [1952, 443, 90, 0.08], [1080, 1110, 90, 0.07], [528, 980, 80, 0.06], [374, 658, 60, 0.04], [497, 302, 60, 0.04], [1330, 740, 150, 0.07], [198, 868, 60, 0.05]];
  const banned = (x, y) => (Math.hypot(x - 1386, y - 560) < 48) || (Math.hypot(x - 395, y - 728) < 42) || (y < 300 && x > 700 && x < 1800) || (x > 1600 && y < 470) || (Math.hypot(x - 2068, y - 308) < 120) || (Math.hypot(x - 616, y - 714) < 30);
  const towers = []; let tries = 0;
  while (towers.length < 320 && tries < 20000) { tries++; let u = rnd(), c = centers[centers.length - 1]; for (const cc of centers) { if (u < cc[3]) { c = cc; break; } u -= cc[3]; } const a = rnd() * 6.28, d = Math.sqrt(rnd()) * c[2]; const x = c[0] + Math.cos(a) * d, y = c[1] + Math.sin(a) * d; if (x < 5 || y < 5 || x > 2195 || y > 1395) continue; if (banned(x, y)) continue; const ci = cellAt(x, y); if (ci < 0 || C.h[ci] < 20 || C.h[ci] > 62) continue; const f = pack.features[C.f[ci]]; if (f && f.type === 'lake' && C.f[ci] !== 9) continue; if (towers.some(([tx, ty]) => (tx - x) ** 2 + (ty - y) ** 2 < 36)) continue; towers.push([x, y]); }
  for (const [x, y] of towers) mk('circle', { cx: x, cy: y, r: 15, fill: 'url(#svHalo)', opacity: 0.45 }, lights);
  for (const [x, y] of towers) { mk('circle', { cx: x, cy: y, r: 2.6, fill: 'url(#svGold)' }, lights); mk('path', { d: `M${(x - 0.45).toFixed(2)},${(y + 0.6).toFixed(2)} L${x.toFixed(2)},${(y - 2.6).toFixed(2)} L${(x + 0.45).toFixed(2)},${(y + 0.6).toFixed(2)} Z`, fill: '#fffaf0', stroke: '#6f6450', 'stroke-width': 0.14 }, lights); }
  log.push('辉塔 ' + towers.length);
  // 穹都上空的上城：一块一块浮着的城，影子落在城里
  { const cx = 616, cy = 714; const plates = [[0, -9, 9, 6], [-12, -5, 5.5, 3.6], [11, -4, 6, 4], [-7, 5, 4.6, 3], [8, 7, 4.2, 2.8], [-1, -20, 4, 2.6]];
    for (const [dx, dy, rx, ry] of plates) mk('ellipse', { cx: cx + dx + 3, cy: cy + dy + 10, rx, ry, fill: '#1d2430', opacity: 0.22, filter: 'url(#svBlur)' }, mg);
    plates.forEach(([dx, dy, rx, ry], k) => { const x = cx + dx, y = cy + dy; mk('ellipse', { cx: x, cy: y + ry * 0.55, rx: rx * 0.92, ry: ry * 0.75, fill: '#8e8a84', stroke: '#4b4d5e', 'stroke-width': 0.3 }, mg); mk('ellipse', { cx: x, cy: y, rx, ry, fill: pat(`up_${k}`, 0.5, 20 + k * 30, '#e9e6de', '#8d8a90', 0.09, 'grid'), stroke: '#4b4d5e', 'stroke-width': 0.4, filter: 'url(#svShadow)' }, mg); mk('ellipse', { cx: x, cy: y, rx: rx * 0.45, ry: ry * 0.45, fill: '#f7f6f1', stroke: '#6b6f86', 'stroke-width': 0.2 }, mg); });
    mk('path', { d: `M${cx - 1.4},${cy - 9} L${cx},${cy - 18} L${cx + 1.4},${cy - 9} Z`, fill: '#ffffff', stroke: '#4b4d5e', 'stroke-width': 0.3 }, mg);
    mk('circle', { cx, cy: cy - 18, r: 6, fill: 'url(#svGold)' }, mg); }
  // 神渡上空的客星城：从曜冠削下来的山头尖朝下托着，顶上是城，黄岩的君王锁在里头
  { const cx = 1100, cy = 640; mk('ellipse', { cx: cx + 4, cy: 676, rx: 16, ry: 6, fill: '#1d2430', opacity: 0.25, filter: 'url(#svBlur)' }, mg);
    mk('ellipse', { cx, cy: cy - 2, rx: 26, ry: 16, fill: 'url(#svAmber)', opacity: 0.85 }, mg);
    const rock = `M${cx - 15},${cy} Q${cx - 11},${cy + 9} ${cx - 4},${cy + 17} L${cx},${cy + 26} L${cx + 4},${cy + 16} Q${cx + 12},${cy + 8} ${cx + 15},${cy} Z`;
    mk('path', { d: rock, fill: '#8f8170', stroke: '#4a3f33', 'stroke-width': 0.45, filter: 'url(#svShadow)' }, mg);
    for (let k = 0; k < 7; k++) { const x = cx - 11 + k * 3.6; mk('path', { d: `M${x},${cy + 1.5} L${x + (cx - x) * 0.55},${cy + 14 + (k % 2) * 3}`, stroke: '#5d5246', 'stroke-width': 0.35, opacity: 0.7 }, mg); }
    mk('ellipse', { cx, cy, rx: 15, ry: 5.2, fill: pat('kx_top', 0.55, 12, '#efe3c2', '#9a8256', 0.1, 'grid'), stroke: '#5b4a33', 'stroke-width': 0.45 }, mg);
    mk('ellipse', { cx, cy, rx: 6, ry: 2.1, fill: '#fff4d6', stroke: '#8a6e3e', 'stroke-width': 0.25 }, mg);
    mk('circle', { cx, cy: cy + 12, r: 2.2, fill: '#ffcf70', stroke: '#a8671c', 'stroke-width': 0.3 }, mg); }
  // 七曜锁在哪：一道封印环加那一曜的光
  const seal = (x, y, grad, c, r = 9) => { mk('circle', { cx: x, cy: y, r: r * 2.2, fill: `url(#${grad})`, opacity: 0.9 }, mg); mk('circle', { cx: x, cy: y, r, fill: 'none', stroke: c, 'stroke-width': 0.7, 'stroke-dasharray': '1.2 0.8' }, mg); mk('circle', { cx: x, cy: y, r: r * 0.62, fill: 'none', stroke: c, 'stroke-width': 0.45 }, mg); for (let k = 0; k < 7; k++) { const a = k / 7 * Math.PI * 2 - Math.PI / 2; mk('circle', { cx: x + Math.cos(a) * r, cy: y + Math.sin(a) * r, r: 0.65, fill: c }, mg); } };
  seal(357.3, 1074.9, 'svBlue', '#3f7fc4');
  { const x = 357.3, y = 1074.9; mk('path', { d: `M${x - 4.5},${y + 1.2} Q${x - 4.5},${y - 3.5} ${x},${y - 5.5} Q${x + 4.5},${y - 3.5} ${x + 4.5},${y + 1.2} Z`, fill: '#eef6fb', stroke: '#2f5f8f', 'stroke-width': 0.35 }, mg); }
  seal(632, 1116, 'svViolet', '#7c4fd0');
  { const x = 632, y = 1116; mk('path', { d: `M${x - 1},${y + 2} L${x},${y - 7} L${x + 1},${y + 2} Z`, fill: '#f2ecff', stroke: '#4b3480', 'stroke-width': 0.3 }, mg); mk('path', { d: `M${x},${y - 7} l-2,3 l2.2,0.4 l-2.4,3.6`, fill: 'none', stroke: '#b78cff', 'stroke-width': 0.5 }, mg); }
  seal(1738, 490, 'svCyan', '#2c9c84');
  { const x = 1738, y = 490; mk('path', { d: `M${x - 1},${y + 2} L${x},${y - 7} L${x + 1},${y + 2} Z`, fill: '#effff9', stroke: '#24685a', 'stroke-width': 0.3 }, mg); for (let k = 0; k < 3; k++) mk('path', { d: `M${x + 2},${y - 5 + k * 2} q3,-1.5 6,0`, fill: 'none', stroke: '#5fd0b4', 'stroke-width': 0.4 }, mg); }
  seal(528, 980, 'svFlame', '#3b8fd6', 16);
  mk('ellipse', { cx: 1040, cy: 195, rx: 26, ry: 14, fill: 'url(#svIce)', opacity: 0.7 }, mg);
  // 北辰塔：峭壁上看星的塔，塔顶一道光
  { const x = 374, y = 196; mk('line', { x1: x, y1: y - 10, x2: x, y2: y - 40, stroke: '#eef4ff', 'stroke-width': 0.8, opacity: 0.55 }, mg); mk('path', { d: `M${x - 1.6},${y + 1} L${x - 0.6},${y - 10} L${x + 0.6},${y - 10} L${x + 1.6},${y + 1} Z`, fill: '#f4f1ea', stroke: '#3c3a44', 'stroke-width': 0.35, filter: 'url(#svShadow)' }, mg); mk('circle', { cx: x, cy: y - 10.5, r: 3.4, fill: 'url(#svSilver)' }, mg); }
  // 寒天之钉
  { const lg = mk('linearGradient', { id: 'svCrystal', x1: 0, y1: 0, x2: 1, y2: 0 }, pdefs); mk('stop', { offset: '0', 'stop-color': '#9fd0ff' }, lg); mk('stop', { offset: '0.45', 'stop-color': '#eef8ff' }, lg); mk('stop', { offset: '1', 'stop-color': '#5d8fd6' }, lg); mk('ellipse', { cx: 1232, cy: 116, rx: 46, ry: 26, fill: 'url(#svBlue)', opacity: 0.6 }, mg); for (let k = 0; k < 30; k++) { const a = rnd() * Math.PI * 2, d = Math.sqrt(rnd()) * 32; const cx = 1232 + Math.cos(a) * d * 1.3, cy = 114 + Math.sin(a) * d * 0.7; const h = 6 + rnd() * 14, w = 1.1 + rnd() * 1.2, lean = (rnd() - 0.5) * 2.6; mk('path', { d: `M${cx - w},${cy} L${cx + lean},${cy - h} L${cx + w},${cy} L${cx},${cy + w * 0.6} Z`, fill: 'url(#svCrystal)', stroke: '#2f5c98', 'stroke-width': 0.18, filter: 'url(#svShadow)' }, mg); } }
  // 赤金纪的黄金城：雪原北边一片金色的残基
  { const x = 1100, y = 84; mk('circle', { cx: x, cy: y, r: 14, fill: 'url(#svGold)', opacity: 0.5 }, mg); for (const f of [0.5, 1]) mk('path', { d: wob(x, y, 8 * f, f, 0.8), fill: 'none', stroke: '#a8822c', 'stroke-width': 0.6, 'stroke-dasharray': '2 1.4' }, mg); }
  // 空路：虚线弧，路上一两条飞船
  const skyRoute = (x1, y1, x2, y2, bend) => { const mx = (x1 + x2) / 2 + (y2 - y1) * bend, my = (y1 + y2) / 2 - (x2 - x1) * bend; const d = `M${x1},${y1} Q${mx},${my} ${x2},${y2}`; mk('path', { d, fill: 'none', stroke: '#f3f8ff', 'stroke-width': 1.4, opacity: 0.6 }, mg); mk('path', { d, fill: 'none', stroke: '#5f7fa8', 'stroke-width': 0.55, 'stroke-dasharray': '2.4 2' }, mg); const t = 0.45, sx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2, sy = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2; mk('path', { d: `M${sx - 3},${sy} q3,-2.2 6,0 q-3,1.6 -6,0 Z M${sx - 1.5},${sy - 1.2} l1.5,-2.5 l1.5,2.5`, fill: '#f6efe0', stroke: '#4d5566', 'stroke-width': 0.3 }, mg); };
  skyRoute(626, 696, 832, 222, 0.12);
  skyRoute(600, 726, 205, 862, -0.15);
  skyRoute(1745, 484, 1940, 452, 0.18);
  // 罗盘、比例尺照 Azgaar 自己的
  { const b = document.querySelector('#mapLayers [data-layer=compass]'); if (b.classList.contains('buttonoff')) { b.click(); await sleep(700); } }
  options.map.units.distance.scale = 19; options.map.units.distance.unit = '公里';
  { const b = document.querySelector('#mapLayers [data-layer=scaleBar]'); for (let k = 0; k < 3; k++) { b.click(); await sleep(900); const g = document.getElementById('scaleBar'); if (g.querySelectorAll('text').length && getComputedStyle(g).display !== 'none') break; } }
  log.push('比例尺 ' + [...document.querySelectorAll('#scaleBar text')].map((t) => t.textContent).join(' '));

  // ---- 地名 ----
  if (!document.getElementById('pFont')) { const l = document.createElement('link'); l.id = 'pFont'; l.rel = 'stylesheet'; l.href = 'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700;900&display=swap'; document.head.appendChild(l); }
  const lab = mk('g', { id: 'svLabels', 'font-family': '"Noto Serif SC", serif', 'text-anchor': 'middle', 'paint-order': 'stroke', 'stroke-linejoin': 'round' }, vb);
  const T1 = (s, x, y, fs, o = {}) => { const e = mk('text', Object.assign({ x, y, 'font-size': fs, 'font-weight': 900, fill: '#2c261f', stroke: '#f6f0e2', 'stroke-width': fs * 0.2, 'letter-spacing': fs * 0.1 }, o), lab); e.textContent = s; return e; };
  const region = (s, x, y, fs, o = {}) => T1(s, x, y, fs, Object.assign({ 'font-weight': 500, fill: '#5b5245', stroke: '#f3eee2', 'stroke-width': fs * 0.16, 'letter-spacing': fs * 0.45, opacity: 0.9 }, o));
  const sea = (s, x, y, fs) => T1(s, x, y, fs, { 'font-weight': 500, fill: '#2d5f73', stroke: '#d9eef3', 'stroke-width': fs * 0.12, 'letter-spacing': fs * 0.6, opacity: 0.85 });
  const magic = (s, x, y, fs) => T1(s, x, y, fs, { 'font-weight': 700, fill: '#3a3a52', stroke: '#f6f0e2', 'stroke-width': fs * 0.2, 'letter-spacing': fs * 0.08 });
  T1('萨 尔 维 斯 帝 国', 560, 590, 30, { 'font-weight': 900, fill: '#4b3f30', stroke: '#f3eee2', 'stroke-width': 3, 'letter-spacing': 9, opacity: 0.55 });
  for (const [s, x, y] of [['帝 畿', 700, 640], ['神渡行省', 1120, 560], ['东方行省', 1330, 860], ['东北行省', 1850, 380], ['南方行省', 1060, 1050], ['南境行省', 520, 1060], ['北境行省', 700, 330]]) region(s, x, y, 13, { 'font-weight': 700, fill: '#6b5532', opacity: 0.7 });
  for (const [s, x, y, fs] of [['西海', 120, 760, 26], ['北海', 420, 60, 22], ['碧湾', 300, 1185, 15]]) sea(s, x, y, fs);
  for (const [s, x, y, fs] of [['盐 原', 420, 1010, 10], ['南 原', 980, 1040, 16], ['赤 原', 830, 880, 10], ['黑石高地', 640, 500, 10], ['裂影之地', 395, 760, 9], ['星坑盆地', 1100, 780, 10], ['白石平原', 1380, 700, 13], ['曜冠山脉', 1300, 330, 12], ['化圣雪原', 990, 250, 16], ['月银原', 905, 146, 10], ['风铃高原', 1661, 620, 12], ['原初之森', 1930, 330, 15], ['千湖', 1782, 790, 10], ['蜜酒丘陵', 1880, 1060, 10], ['雷暴荒地', 650, 1085, 10], ['南部火山带', 560, 915, 9], ['龙眠天脊', 1760, 140, 12], ['东陆南部山脉', 1510, 1200, 10], ['星湖', 1914, 515, 10]]) region(s, x, y, fs);
  const cityLabel = (s, x, y, R, fs) => T1(s, x, y + R * 1.12 + fs * 0.95, fs);
  for (const [s, x, y, R, fs] of [['穹都', 616, 714, 26, 15], ['神渡城', 1100, 672, 21, 13], ['星湖城', 1952, 443, 15, 10], ['白冠城', 1186, 756, 13, 9], ['星冠圣城', 1386, 560, 12, 9], ['金沙边郡', 1080, 1110, 11, 8.5], ['蓝焰铸城', 528, 980, 12, 9], ['长眠陵城', 374, 658, 11, 8.5], ['琉璃庭', 682, 435, 9, 8], ['镜湖', 497, 302, 10, 8.5], ['潮门港', 198, 868, 9, 8], ['熔铁炉心', 1562, 1106, 9, 8], ['金冕城遗址', 1518, 742, 12, 8]]) cityLabel(s, x, y, R, fs);
  for (const [s, x, y] of [['贾曼尼', 1185, 437], ['鹿门城', 1290, 462], ['朝峰城', 1385, 427], ['白丘王城', 545, 367], ['盐井城', 410, 962], ['千湖王城', 1780, 762], ['穴镇', 1892, 966], ['野泉城', 1385, 864], ['金沙王城', 1292, 1004], ['黑石王都', 612, 552], ['灰桥', 630, 397], ['裂石城', 720, 412], ['松门城', 1625, 527], ['白鹿书塔', 1980, 571], ['轰鸣断崖', 1452, 1188], ['灰篱镇', 1465, 752]]) T1(s, x, y + 4, 5.5, { 'font-weight': 700, 'stroke-width': 1 });
  for (const [s, x, y, fs] of [['客星城', 1100, 608, 8.5], ['上城', 616, 680, 7.5], ['潮宫', 357, 1098, 7], ['引雷台', 632, 1138, 7], ['风塔', 1738, 512, 7], ['北辰塔', 374, 214, 7.5], ['寒天之钉', 1232, 146, 8], ['赤金纪的黄金城', 1100, 104, 6.5], ['精灵王庭', 2068, 330, 8], ['扛岛', 110, 562, 6.5], ['橙冰的冰川', 1040, 218, 6.5]]) magic(s, x, y, fs);
  // 题签
  { const g = mk('g', { id: 'svTitle' }, lab); mk('rect', { x: 1560, y: 1222, width: 470, height: 128, rx: 6, fill: '#f3ecdc', stroke: '#6b5532', 'stroke-width': 1.4, opacity: 0.94 }, g); mk('rect', { x: 1566, y: 1228, width: 458, height: 116, rx: 4, fill: 'none', stroke: '#6b5532', 'stroke-width': 0.6 }, g); const t1 = mk('text', { x: 1795, y: 1264, 'font-size': 26, 'font-weight': 900, fill: '#3a2f22', 'letter-spacing': 6 }, g); t1.textContent = '奥尔德兰 · 月银纪'; const t2 = mk('text', { x: 1795, y: 1292, 'font-size': 14, 'font-weight': 500, fill: '#5b4a33', 'letter-spacing': 2 }, g); t2.textContent = '萨尔维斯末年 · 约九千八百年 · 三百二十座辉塔';
    const km = 19, x0 = 1690, y0 = 1322, seg = 1000 / km; for (let k = 0; k < 4; k++) mk('rect', { x: x0 + k * seg, y: y0, width: seg, height: 4, fill: k % 2 ? '#f3ecdc' : '#3a2f22', stroke: '#3a2f22', 'stroke-width': 0.6 }, g);
    for (let k = 0; k <= 4; k++) { const tt = mk('text', { x: x0 + k * seg, y: y0 - 4, 'font-size': 10, 'font-weight': 500, fill: '#3a2f22', 'stroke-width': 0 }, g); tt.textContent = k === 4 ? '4000 公里' : String(k * 1000); }
    const sb = document.getElementById('scaleBar'); if (sb) sb.style.display = 'none'; }
  try { await document.fonts.load('900 20px "Noto Serif SC"', '萨尔维斯帝国穹都神渡'); await document.fonts.load('500 20px "Noto Serif SC"', '西海南原'); await sleep(1500); } catch (e) { log.push('字体 ' + e); }
  // 藏地形符号（城、遗址底下），截图以前再跑一回
  window.__svHideIcons = () => { let n = 0; for (const [x, y, r] of window.__svHide) { for (const u of document.querySelectorAll('#terrain use')) { if (u.style.display === 'none') continue; const ux = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2, uy = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2; if ((ux - x) ** 2 + (uy - y) ** 2 <= r * r) { u.style.display = 'none'; n++; } } } return n; };
  log.push('城下藏符号 ' + window.__svHideIcons() + '，南原藏符号 ' + (window.__hideMoonIcons ? window.__hideMoonIcons() : '—'));
  return log.join('；');
})();
