// 山铜纪·麦的年月（约900年）样张：make_bronze.py 拼的（共用的那几段照 az_strife.js，山铜纪自己的在 az_bronze_body.js），build_late.sh bronze 接着跑。
//   山铜纪补卷_14 地图的几层“后段那一张”：墙西从灰雨城城西塌口画出一条往西的车道，790年停在黑曜平原上，862年成了烬灭之都；九座高座一座一座熄了，
//   742到861年七处地方长成了七座城；灯路一站一站往外接，渊月长廊照灯路的线修，890年一期贯通；墙东河岸上的碑一面一面往下游排，平原改叫曙辉平原，
//   870年以后墙下立起界碑，射界里种上了麦；死域照旧在南段对面，沙海在死域里，落星洼到麦的年月是一大片望不到边的水。
//   高座照纷争纪中段那一张的位置（高座_纷争纪.json，塞进 SEATS），都熄了；长垒塞进 WALL_PTS。
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const vb = document.getElementById('viewbox');
  const defs = document.getElementById('featurePaths').closest('defs');
  for (const id of ['stCities', 'stGround', 'stMagic', 'stLabels', 'stDefs', 'stWall', 'stRail', 'stSeats', 'stRoads']) { const o = document.getElementById(id); if (o) o.remove(); }
  const pdefs = mk('g', { id: 'stDefs' }, defs);
  const log = [];
  let seed = 29; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const C = pack.cells;
  if (!window.__cellGrid) { const g = {}; for (let i = 0; i < C.i.length; i++) { const gx = Math.floor(C.p[i][0] / 12), gy = Math.floor(C.p[i][1] / 12); for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) { const k = (gx + a) + ',' + (gy + b); (g[k] || (g[k] = [])).push(i); } } window.__cellGrid = g; }
  const cellAt = (x, y) => { let best = -1, bd = 1e9; const gx = Math.floor(x / 12), gy = Math.floor(y / 12); for (const i of (window.__cellGrid[gx + ',' + gy] || [])) { const d = (C.p[i][0] - x) ** 2 + (C.p[i][1] - y) ** 2; if (d < bd) { bd = d; best = i; } } return best; };
  const spt = document.getElementById('map').createSVGPoint();
  const waterProbes = [...document.querySelectorAll('#fseaProbes path')].filter((e) => e.getAttribute('data-k') === 'f');
  for (const id of ['saltseaProbe', 'bay_moon']) { const e = document.getElementById(id); if (e) waterProbes.push(e); }
  const isDry = (x, y) => { const ci = cellAt(x, y); if (ci < 0 || C.h[ci] < 20) return false; const f = pack.features[C.f[ci]]; if (f && f.type === 'lake' && C.f[ci] !== 9) return false; spt.x = x; spt.y = y; for (const e of waterProbes) if (e.isPointInFill(spt)) return false; return true; };
  const smooth = (pts) => { let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2; d += ` C${(p1[0] + (p2[0] - p0[0]) / 6).toFixed(1)},${(p1[1] + (p2[1] - p0[1]) / 6).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) / 6).toFixed(1)},${(p2[1] - (p3[1] - p1[1]) / 6).toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`; } return d; };
  const WALL = JSON.parse('WALL_PTS');
  const wallX = (y) => { for (let i = 0; i < WALL.length - 1; i++) { const a = WALL[i], b = WALL[i + 1]; if ((a[1] - y) * (b[1] - y) <= 0 && a[1] !== b[1]) return a[0] + (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]); } return null; };
  const SL = [[476, 1128], [520, 1138], [570, 1144], [620, 1146], [662, 1138], [702, 1122], [742, 1102], [792, 1082], [832, 1066], [866, 1052], [890, 1034], [910, 1010], [928, 991], [944, 978], [972, 982], [1010, 990], [1050, 996], [1090, 1003], [1130, 1012], [1170, 1023], [1210, 1031], [1250, 1036], [1290, 1040], [1330, 1041], [1370, 1043], [1408, 1050], [1432, 1066]];
  const slY = (x) => { for (let i = 0; i < SL.length - 1; i++) { const a = SL[i], b = SL[i + 1]; if (x >= a[0] && x <= b[0]) return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]); } return null; };

  // ---- 共用的纹样和光 ----
  const glow = (id, c, o) => { const rg = mk('radialGradient', { id }, pdefs); mk('stop', { offset: '0', 'stop-color': c, 'stop-opacity': o }, rg); mk('stop', { offset: '0.45', 'stop-color': c, 'stop-opacity': o * 0.45 }, rg); mk('stop', { offset: '1', 'stop-color': c, 'stop-opacity': 0 }, rg); };
  glow('stEmber', '#ff8a4a', 0.95); glow('stEmberS', '#ffb066', 0.6); glow('stViolet', '#c9b6ff', 0.85); glow('stWhite', '#ffffff', 0.7); glow('stCyan', '#9ff0dc', 0.85); glow('stAmber', '#ffc76a', 0.95); glow('stSilver', '#eef3ff', 0.85); glow('stBlue', '#9fd4ff', 0.75); glow('stScorch', '#3b2c28', 0.4);
  const sh = mk('filter', { id: 'stShadow', x: '-50%', y: '-50%', width: '200%', height: '200%' }, pdefs); mk('feDropShadow', { dx: 0.6, dy: 1.1, stdDeviation: 0.6, 'flood-color': '#1b2733', 'flood-opacity': 0.45 }, sh);
  const bl = mk('filter', { id: 'stBlur', x: '-20%', y: '-20%', width: '140%', height: '140%' }, pdefs); mk('feGaussianBlur', { stdDeviation: 2.4 }, bl);
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

  // ---- 城市平面（照萨尔维斯那一套，西边的营城换暗色） ----
  const T = {
    gold:     { ground: '#d9cdb1', f1: '#cdc79a', f2: '#a9a274', mid: '#cbb994', core: '#b9a47e', line: '#8a7552', wall: '#5b4a33', hi: '#f3e7c6', keep: '#f0c75e' },
    holy:     { ground: '#e1dccd', f1: '#d4d0a8', f2: '#b1ad83', mid: '#d8d2c2', core: '#c9c2b0', line: '#958c75', wall: '#6b624d', hi: '#fffdf4', keep: '#fff6d8' },
    imperial: { ground: '#dcd8cc', f1: '#cfd0a8', f2: '#a9ab84', mid: '#d0cdc2', core: '#bfbcb4', line: '#7b7a80', wall: '#4b4d5e', hi: '#f7f6f1', keep: '#dfe9ff' },
    silver:   { ground: '#d6d6cc', f1: '#c8cba6', f2: '#a5aa86', mid: '#c2c2b6', core: '#a9aba5', line: '#76787a', wall: '#4b4f57', hi: '#f2f4f7', keep: '#e8eef8' },
    forge:    { ground: '#c4b4a2', f1: '#b8ab92', f2: '#958670', mid: '#b09a86', core: '#9a7c66', line: '#5d4535', wall: '#33251c', hi: '#ead7c4', keep: '#ffb066' },
    tide:     { ground: '#c4cdcd', f1: '#b6c0ac', f2: '#91a08c', mid: '#aab8ba', core: '#8ea2a8', line: '#536a73', wall: '#26404b', hi: '#e6f0f2', keep: '#4fa6c9' },
    elf:      { ground: '#c9d6bf', f1: '#b9cca6', f2: '#8faa80', mid: '#b5c9a6', core: '#9fb88f', line: '#5b7a52', wall: '#2f4a2c', hi: '#eef6e6', keep: '#d8f2c4' },
    rose:     { ground: '#b9a8a2', f1: '#a8948c', f2: '#86716a', mid: '#a38a84', core: '#8f736c', line: '#5e403c', wall: '#2e1d1c', hi: '#dcc6c0', keep: '#e0566a' },
    bone:     { ground: '#bdb8ae', f1: '#ada79a', f2: '#8b8578', mid: '#aaa498', core: '#958f82', line: '#5f5a50', wall: '#2c2925', hi: '#ece8dc', keep: '#f3f0e4' },
    mirror:   { ground: '#a9a2b4', f1: '#9b93a8', f2: '#7a7090', mid: '#968ca6', core: '#82779a', line: '#4d4266', wall: '#241c36', hi: '#d8d0e6', keep: '#c79bff' },
    ember:    { ground: '#b59f92', f1: '#a68e80', f2: '#856c5e', mid: '#9f8476', core: '#8a6c5e', line: '#553a2e', wall: '#2a1a14', hi: '#e2c8b8', keep: '#ff7a3a' },
    camp:     { ground: '#aea79c', f1: '#9f978b', f2: '#7e776b', mid: '#9c9488', core: '#867e72', line: '#4f4a42', wall: '#26231f', hi: '#d8d2c6', keep: '#ff9a4a' },
    abyss:    { ground: '#a2adb2', f1: '#93a09f', f2: '#748482', mid: '#8e9ca2', core: '#788a92', line: '#3e535c', wall: '#1a2c34', hi: '#d0dde2', keep: '#3fb6c9' },
  };
  const cities = mk('g', { id: 'stCities', mask: 'url(#land)' }, null);
  vb.insertBefore(cities, document.getElementById('rivers'));
  window.__stHide = [];
  const cityPlan = (key, x, y, R, th, walls) => {
    const t = T[th], ph = rnd() * 6, rot = rnd() * 90;
    const g = mk('g', { id: 'st_' + key }, cities);
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
    window.__stHide.push([x, y, R * 1.12]);
    return g;
  };
  const smallCity = (x, y, th) => { const t = T[th] || T.gold; mk('circle', { cx: x, cy: y, r: 2.1, fill: t.core, stroke: t.wall, 'stroke-width': 0.55 }, cities); mk('circle', { cx: x, cy: y, r: 0.7, fill: t.keep }, cities); window.__stHide.push([x, y, 3]); };
  const ruin = (x, y, R, c = '#6d665a') => { const g = mk('g', {}, cities); for (const f of [0.4, 0.72, 1.0]) mk('path', { d: wob(x, y, R * f, f * 3, 0.6), fill: 'none', stroke: c, 'stroke-width': 0.5, 'stroke-dasharray': '2.2 1.6', opacity: 0.8 }, g); mk('path', { d: wob(x, y, R, 1, 0.6), fill: '#cfc8b6', opacity: 0.25 }, g); for (let k = 0; k < 7; k++) { const a = rnd() * 6.28, d = rnd() * R * 0.7; mk('rect', { x: x + Math.cos(a) * d - 0.8, y: y + Math.sin(a) * d - 0.5, width: 1.6, height: 1, fill: '#8a8272', opacity: 0.8 }, g); } window.__stHide.push([x, y, R]); return g; };

  // ==== 山铜纪·麦的年月（约900年）：这一段接在 az_strife.js 的共用部分后头，make_bronze.py 拼成 az_bronze.js ====
  const SLB = window.__SL_LATE || SL;
  const slYB = (x) => { for (let i = 0; i < SLB.length - 1; i++) { const a = SLB[i], b = SLB[i + 1]; if (x >= a[0] && x <= b[0]) return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]); } return null; };
  const landNear = (x, y, maxR = 60) => { const ok = (xx, yy) => isDry(xx, yy) && (slYB(xx) === null || yy < slYB(xx) - 6); if (ok(x, y)) return [x, y]; for (let r = 3; r <= maxR; r += 3) for (let a = 0; a < 360; a += 15) { const xx = x + r * Math.cos(a * Math.PI / 180), yy = y + r * Math.sin(a * Math.PI / 180); if (ok(xx, yy)) return [xx, yy]; } return [x, y]; };
  const moved = {};
  T.obsidian = { ground: '#a39c98', f1: '#958d88', f2: '#756d68', mid: '#8f8783', core: '#7a706c', line: '#3d3434', wall: '#1d1717', hi: '#d8cfcb', keep: '#d23a2a' };
  T.bloom = { ground: '#e3d3cf', f1: '#d9c3bb', f2: '#bf9c93', mid: '#d6bdb6', core: '#c7a59d', line: '#8f6560', wall: '#5e3b38', hi: '#fbefe9', keep: '#e86d8f' };
  T.wind = { ground: '#d8dce0', f1: '#c9d1c0', f2: '#a7b29c', mid: '#cdd3d6', core: '#b4bcc2', line: '#6f7a85', wall: '#3f4a57', hi: '#f4f7fa', keep: '#bfe3ff' };

  // ---- 墙东：三座巨城，月镜的银湖城、风铃的高岚城、蔷薇的露玫城、碧穹王庭（200年关了门），白冠城是学城 ----
  const EAST = [
    ['jinyuan', 1518, 742, 25, 'gold', 3], ['xingguan', 1386, 560, 15, 'holy', 2], ['luxin', 1562, 1106, 14, 'forge', 2],
    ['gaolan', 1697.1, 518.7, 11, 'wind', 2], ['lumei', 1822.9, 981.5, 11, 'bloom', 2], ['biqiong', 2068, 308, 9, 'elf', 2],
    ['baiguan', 1186, 756, 8.5, 'holy', 2], ['baiyuan', 1408, 868, 8, 'imperial', 2], ['jinsui', 1606, 854, 8.5, 'gold', 2], ['yinfan', 2069.8, 747.3, 8, 'tide', 2],
  ];
  for (const m of EAST) cityPlan(...m);
  // 银湖城：城从湖心岛长出来，约410年以后长桥连到北岸的王宫（这一组画在湖上，不套陆地遮罩）
  { const free = mk('g', { id: 'stYinhu' }, null); vb.insertBefore(free, document.getElementById('rivers')); cityPlan('yinhu', 1952, 451, 9, 'silver', 2); free.appendChild(document.getElementById('st_yinhu'));
    mk('path', { d: 'M1952,441 L1952,427', stroke: '#f4f1ea', 'stroke-width': 1.8 }, free); mk('path', { d: 'M1952,441 L1952,427', stroke: '#5d6878', 'stroke-width': 0.35, 'stroke-dasharray': '1 1' }, free);
    mk('rect', { x: 1948, y: 421, width: 8, height: 5.5, fill: '#e8eef8', stroke: '#4b4f57', 'stroke-width': 0.4 }, free); }
  const SMALL_E = [[1563.8, 644.4, 'holy'], [2019.8, 865.3, 'tide'], [1694, 714, 'gold'], [1276, 938, 'imperial'], [1650, 868, 'gold'], [1540, 784, 'gold'], [1474, 588, 'imperial'], [1738, 602, 'gold'], [1760, 686, 'wind'],
    [1892.4, 953.7, 'gold'], [1879.9, 1024.8, 'gold'], [1979.8, 559, 'holy'], [1305, 392, 'imperial'], [1348, 392, 'imperial'], [1410, 400, 'gold'], [1250, 1000, 'gold'], [1496, 1008, 'gold'], [1540, 924, 'gold'],
    [1497.3, 1037.1, 'forge'], [1500, 1090, 'forge'], [1760, 1106, 'bloom'], [1790, 720, 'holy'], [1894.2, 683.2, 'elf'], [1800.3, 457.4, 'elf'], [1870, 400, 'elf'], [1090, 510, 'silver'], [980, 925, 'holy'], [1386, 224, 'silver']];
  for (const [x, y, th] of SMALL_E) smallCity(x, y, th);
  // 废了的：灰雨城（661年以后是废墟）、霜厅城（321年人走了）、穹都压在烬灭之都底下不画、旧神渡（中央旧战原当中）
  ruin(1032, 784, 7, '#5d6878'); ruin(1090, 445, 6); ruin(1100, 672, 11);

  // ---- 墙西：烬灭之都（862年立第一条，在黑曜平原上，脚底下压着穹都），七城 ----
  const WEST = [
    ['jinmie', 616, 714, 24, 'obsidian', 3], ['cangyan', 528, 980, 11, 'ember', 2], ['xueji', 682, 435.4, 10.5, 'rose', 2], ['haizhong', 374, 658, 11, 'bone', 2],
    ['yanjing', 497, 302, 10, 'mirror', 2], ['heiyi', 374, 200, 8.5, 'camp', 2], ['leiyu', 616, 1134, 10, 'forge', 2], ['shenchao', 198, 868, 10, 'abyss', 2],
  ];
  for (const m of WEST) cityPlan(...m);
  const zhekou = landNear(545, 1128); moved['辙口城'] = zhekou;
  const SMALL_W = [[665, 668, 'camp'], [352, 440, 'camp'], [748, 840, 'forge'], [858, 462, 'camp'], [814, 854, 'camp'], [616, 896, 'ember'], [690, 1060, 'forge'], [zhekou[0], zhekou[1], 'camp'], [154, 728, 'abyss'], [286.2, 1075.8, 'tide']];
  for (const [x, y, th] of SMALL_W) smallCity(x, y, th);

  // ---- 地上的东西 ----
  const ground = mk('g', { id: 'stGround' }, null);
  vb.insertBefore(ground, document.getElementById('rivers'));
  // 中央旧战原（月银纪神渡那一片星坑盆地）的坑沿
  { const cx = 1100, cy = 672, r = 92; for (let k = 0; k < 150; k++) { const a = k / 150 * Math.PI * 2, rr = r * (1 + 0.03 * Math.sin(5 * a)); const x1 = cx + Math.cos(a) * rr, y1 = cy + Math.sin(a) * rr, x2 = cx + Math.cos(a) * (rr - 4.5 - (k % 3)), y2 = cy + Math.sin(a) * (rr - 4.5 - (k % 3)); mk('line', { x1, y1, x2, y2, stroke: '#8d7f66', 'stroke-width': 0.55, opacity: 0.5 }, ground); } mk('path', { d: wob(cx, cy, r, 0.3, 0.6), fill: 'none', stroke: '#8d7f66', 'stroke-width': 0.7, opacity: 0.55 }, ground); }
  // 环山：靠里那一面化成一层黑玻璃（往后叫黑曜环山）；灰原上空悬着几块宅子的石台（坠落的天城）
  { const cx = 616, cy = 714; let gapAng = 0.6; { const bins = new Array(36).fill(0); for (const u of document.querySelectorAll('#terrain use')) { const h = u.getAttribute('href'); if (!/hill|mount/.test(h)) continue; const x = +u.getAttribute('x') + (+u.getAttribute('width')) / 2 - cx, y = +u.getAttribute('y') + (+u.getAttribute('height')) / 2 - cy; const d = Math.hypot(x, y); if (d < 94 || d > 170) continue; bins[Math.floor(((Math.atan2(y, x) + Math.PI * 2) % (Math.PI * 2)) / (Math.PI * 2) * 36)]++; } let mi = 0; for (let k = 1; k < 36; k++) if (bins[k] < bins[mi]) mi = k; gapAng = (mi + 0.5) / 36 * Math.PI * 2; }
    const r = 98, a0 = gapAng + 0.3, a1 = gapAng + Math.PI * 2 - 0.3; const d = `M${cx + Math.cos(a0) * r},${cy + Math.sin(a0) * r} A${r},${r} 0 1 1 ${cx + Math.cos(a1) * r},${cy + Math.sin(a1) * r}`;
    mk('path', { d, fill: 'none', stroke: '#1d1a20', 'stroke-width': 4, opacity: 0.45 }, ground); mk('path', { d, fill: 'none', stroke: '#9b93ae', 'stroke-width': 0.5, opacity: 0.55, 'stroke-dasharray': '3 2' }, ground);
    for (const [dx, dy, rx, ry, a] of [[30, 46, 5, 3, 14], [44, 38, 3.6, 2.2, -20], [18, 58, 3.2, 2, 30]]) { const x = cx + dx, y = cy + dy; mk('ellipse', { cx: x + 3, cy: y + 7, rx, ry: ry * 0.6, fill: '#1d2430', opacity: 0.22, filter: 'url(#stBlur)' }, ground); mk('ellipse', { cx: x, cy: y, rx, ry, fill: pat(`hz_${dx}`, 0.5, a, '#e2ded5', '#8d8a90', 0.09, 'grid'), stroke: '#3b3a44', 'stroke-width': 0.35, transform: `rotate(${a} ${x} ${y})`, filter: 'url(#stShadow)' }, ground); } }
  // 枯祭原（纷争纪的黑穗原）：851年最后一尊枯死，原心一个坑
  { const pd = pat('heisui', 1.6, 35, 'rgba(0,0,0,0)', '#2d2620', 0.28, 'stripe'); mk('ellipse', { cx: 360, cy: 500, rx: 62, ry: 46, fill: pd, opacity: 0.3, mask: 'url(#land)' }, ground); mk('ellipse', { cx: 352, cy: 476, rx: 9, ry: 5.5, fill: '#5b5048', stroke: '#2d2620', 'stroke-width': 0.5, opacity: 0.85 }, ground); }
  // 赤原的土垒（雨冲不平）
  { for (const [x, y, a] of [[784, 872, -18], [804, 884, -12], [822, 874, -24]]) { const dd = `M${x - 9},${y} q9,-3.2 18,0`; mk('path', { d: dd, fill: 'none', stroke: '#6b3424', 'stroke-width': 1.3, transform: `rotate(${a} ${x} ${y})`, opacity: 0.6 }, ground); } }
  // 月银原、寒天之钉
  { const MX = 905, MY = 168; mk('ellipse', { cx: MX, cy: MY, rx: 62, ry: 30, fill: 'url(#stSilver)', opacity: 0.8 }, ground); for (let k = 0; k < 22; k++) { const a = rnd() * 6.28, d = Math.sqrt(rnd()) * 42; const x = MX + Math.cos(a) * d * 1.3, y = MY + Math.sin(a) * d * 0.6; if (!isDry(x, y)) continue; const r = 1 + rnd() * 2.4; mk('ellipse', { cx: x, cy: y, rx: r, ry: r * 0.7, fill: '#cfd6e6', stroke: '#7d869c', 'stroke-width': 0.3, opacity: 0.9 }, ground); } }
  // 风铃的断崖：纷争纪10901年薇儿丹蒂一剑斩出，从脊上一直劈到谷底
  { const pts = [[1708, 620], [1716, 632], [1722, 646], [1731, 657], [1738, 671], [1748, 682]]; const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#2b3442', 'stroke-width': 2, opacity: 0.8 }, ground); mk('path', { d, fill: 'none', stroke: '#c9d6e6', 'stroke-width': 0.5, transform: 'translate(0.8,-0.6)' }, ground); }
  // 圣土：纷争纪10899年绝后者亚蒙倒在这里，白的，温的，寸草不生
  { mk('ellipse', { cx: 925, cy: 964, rx: 9, ry: 5.5, fill: '#fbf7ee', opacity: 0.9 }, ground); mk('ellipse', { cx: 925, cy: 964, rx: 14, ry: 9, fill: 'url(#stWhite)', opacity: 0.8 }, ground); }
  // 南沼：墙修到那里就没有了，三口盐泉一字排开，东泉蜥蜴人、西泉魔族，中泉两族隔日取水，泉边立着南沼停火的碑
  { for (const [x, y] of [[956, 987], [946, 988], [936, 989]]) { mk('circle', { cx: x, cy: y, r: 2.2, fill: '#bfe3e6', stroke: '#3f6b70', 'stroke-width': 0.4 }, ground); } mk('rect', { x: 945.2, y: 982.5, width: 1.6, height: 3, fill: '#f4f1ea', stroke: '#3b3a44', 'stroke-width': 0.3 }, ground);
    for (let k = 0; k < 10; k++) mk('path', { d: `M${928 + k * 3.2},${994 + (k % 2) * 1.6} q0.6,-1.2 1.2,0 q0.6,-1.2 1.2,0`, fill: 'none', stroke: '#6f8a7c', 'stroke-width': 0.35 }, ground); }
  // 擎天级：止戈那一年退到死域边上停下，11年那一台走回来跪在墙根
  { const kneel = (x, y, s) => { const g = mk('g', { transform: `translate(${x},${y}) scale(${s})` }, ground); mk('ellipse', { cx: 2, cy: 3.2, rx: 4.5, ry: 1.2, fill: '#1d2430', opacity: 0.25 }, g); mk('path', { d: 'M-2.4,3 L-1.6,-1.2 L-2.8,-4.2 L-1.2,-6.6 L1.2,-6.6 L2.6,-4.2 L1.6,-1.2 L3.2,1.2 L3.6,3 Z', fill: '#9aa3ab', stroke: '#2f3540', 'stroke-width': 0.35 }, g); mk('circle', { cx: 0, cy: -7.6, r: 1.2, fill: '#c9d0d6', stroke: '#2f3540', 'stroke-width': 0.3 }, g); }; kneel(944, 962, 1.3); for (const [x, y] of [[904, 1004], [884, 1022], [968, 1006], [1000, 1004]]) kneel(x, y, 1); }
  // 河心三日：灰河下游的渡口，渡口的人自己凿的一块河石
  mk('rect', { x: 719, y: 1015, width: 2.2, height: 3.2, fill: '#d8d2c6', stroke: '#3a3226', 'stroke-width': 0.3 }, ground);
  // 道头和白地：纷争纪掘线型开出来的一条道，过了白线往南
  mk('path', { d: 'M932,999 L928,1016 L924,1034', fill: 'none', stroke: '#e9e1cf', 'stroke-width': 1.6, opacity: 0.8 }, ground);
  // 沙海里塔落下来烧出的玻璃：东沿的玻璃坡（约7800年）、托纳修的塔（8137年）、第五十四塔（约7900年）
  for (const [x, y, rx, ry] of [[1144, 1148, 16, 9], [924, 1022, 12, 7], [950, 1062, 10, 6]]) { mk('ellipse', { cx: x, cy: y, rx, ry, fill: '#c7d3d2', stroke: '#6f8790', 'stroke-width': 0.5, opacity: 0.9 }, ground); mk('ellipse', { cx: x - rx * 0.25, cy: y - ry * 0.3, rx: rx * 0.45, ry: ry * 0.35, fill: '#ffffff', opacity: 0.55 }, ground); mk('path', { d: `M${x - 1.5},${y + 1} L${x - 0.6},${y - 4} L${x + 0.6},${y - 4} L${x + 1.5},${y + 1} Z`, fill: '#8a7e70', stroke: '#3f3830', 'stroke-width': 0.3, transform: `rotate(35 ${x} ${y})` }, ground); }
  // 沙海南头的火环
  { const x = 1078, y = 1252; mk('circle', { cx: x, cy: y, r: 12, fill: 'url(#stEmber)', opacity: 0.8 }, ground); mk('circle', { cx: x, cy: y, r: 5.5, fill: 'none', stroke: '#9a3a1a', 'stroke-width': 1.2 }, ground); mk('circle', { cx: x, cy: y, r: 5.5, fill: 'none', stroke: '#ffc76a', 'stroke-width': 0.45 }, ground); }
  // 落星洼：到麦的年月是一大片望不到边的水，骨堆一座一座露在水上，骨脊水浅的季节露出一截
  { const lp = document.getElementById('feature_9'); if (lp) { const sp = document.getElementById('map').createSVGPoint(); const bb = lp.getBBox(); let n = 0, tries = 0; const bones = mk('g', { id: 'stBones' }, null); vb.insertBefore(bones, document.getElementById('labels'));
      while (n < 12 && tries < 600) { tries++; const x = bb.x + rnd() * bb.width, y = bb.y + rnd() * bb.height; sp.x = x; sp.y = y; if (!lp.isPointInFill(sp) || (x - 1343) ** 2 / 900 + (y - 1126) ** 2 / 100 < 1) continue; n++; mk('ellipse', { cx: x, cy: y, rx: 2.6, ry: 1.4, fill: '#f6f1e6', stroke: '#6b5f50', 'stroke-width': 0.3 }, bones); mk('path', { d: `M${x - 1.8},${y} q0.6,-1.4 1.2,0 M${x + 0.2},${y} q0.6,-1.4 1.2,0`, fill: 'none', stroke: '#8a7e70', 'stroke-width': 0.3 }, bones); }
      const spn = [[1312, 1135], [1332, 1129], [1352, 1123], [1372, 1117]]; mk('path', { d: smooth(spn), fill: 'none', stroke: '#f6f1e6', 'stroke-width': 1.4, 'stroke-dasharray': '5 3', 'stroke-linecap': 'round' }, bones); } }

  // ---- 高座：七十二座都熄了（九座里最后一尊851年枯死），熄了的高座是一座一座黑山；有名的那四座立着碑 ----
  const seats = mk('g', { id: 'stSeats' }, null);
  vb.insertBefore(seats, document.getElementById('labels'));
  const SEATS = JSON.parse('SEATS');
  for (const [x, y, lit, big] of SEATS) { const w = 5.6 * big, h = 3 * big; mk('path', { d: `M${x - w / 2},${y + h / 2} L${x - w * 0.32},${y - h / 2} L${x + w * 0.32},${y - h / 2} L${x + w / 2},${y + h / 2} Z`, fill: '#8a857e', stroke: '#55524c', 'stroke-width': 0.4, opacity: 0.85 }, seats); window.__stHide.push([x, y, 4]); }
  const CANON = window.__stCanonSeats || [[572, 970], [462, 736], [520, 1100]];
  const stele = (x, y, n = 1) => { for (let k = 0; k < n; k++) { const xx = x + (k % 3 - 1) * 3.2, yy = y - 3 - Math.floor(k / 3) * 2.6; mk('rect', { x: xx - 0.8, y: yy - 2.6, width: 1.6, height: 2.8, fill: '#f4f1ea', stroke: '#2f2e36', 'stroke-width': 0.3 }, seats); } };
  stele(CANON[0][0], CANON[0][1], 1); stele(CANON[1][0], CANON[1][1], 9); stele(CANON[2][0], CANON[2][1], 1); stele(352, 470, 1);

  // ---- 长垒、墙后段城、星纱轨、路（照纷争纪中段那一套） ----
  // ---- 长垒：一段墙从一座雪山连到下一座雪山，夜里泛白光；墙后的段城一座挨一座 ----
  const wg = mk('g', { id: 'stWall' }, null);
  vb.insertBefore(wg, document.getElementById('labels'));
  const wd = smooth(WALL);
  mk('path', { d: wd, fill: 'none', stroke: '#fffdf2', 'stroke-width': 10, opacity: 0.34, filter: 'url(#stBlur)', 'stroke-linecap': 'round' }, wg);
  mk('path', { d: wd, fill: 'none', stroke: '#2f2e36', 'stroke-width': 3.8, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, wg);
  mk('path', { d: wd, fill: 'none', stroke: '#f7f4ec', 'stroke-width': 2.3, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, wg);
  mk('path', { d: wd, fill: 'none', stroke: '#9d968a', 'stroke-width': 0.55, 'stroke-dasharray': '1.3 2.1' }, wg);
  const wp = mk('path', { d: wd, fill: 'none' }, wg); const WL = wp.getTotalLength();
  const tan = (s) => { const p = wp.getPointAtLength(Math.max(0, s - 1)), q = wp.getPointAtLength(Math.min(WL, s + 1)); const dx = q.x - p.x, dy = q.y - p.y, l = Math.hypot(dx, dy) || 1; return [dx / l, dy / l]; };
  let nk = 0;
  for (let s = 7; s < WL - 3; s += 12.5) { const p = wp.getPointAtLength(s); const [tx, ty] = tan(s); const nx = ty, ny = -tx; const x = p.x + nx * 3.6, y = p.y + ny * 3.6; const a = Math.atan2(ty, tx) * 180 / Math.PI; mk('rect', { x: x - 1.15, y: y - 1.15, width: 2.3, height: 2.3, fill: '#efebe1', stroke: '#3a3944', 'stroke-width': 0.4, transform: `rotate(${a} ${x} ${y})` }, wg); if (nk % 4 === 1) mk('circle', { cx: p.x - nx * 2.4, cy: p.y - ny * 2.4, r: 2.8, fill: 'url(#stViolet)', opacity: 0.9 }, wg); nk++; }
  log.push('段城 ' + nk);
  const bigSeg = (x, y) => { mk('rect', { x: x - 2.4, y: y - 2.4, width: 4.8, height: 4.8, fill: '#f7f4ec', stroke: '#2f2e36', 'stroke-width': 0.7 }, wg); mk('rect', { x: x - 1, y: y - 1, width: 2, height: 2, fill: '#4b4d5e' }, wg); };
  for (const y of [505, 704, 896]) { const x = wallX(y); bigSeg(x + 4.4, y); }
  // 水门：旧神渡三条河在墙底下汇成一条，墙下开着水门（往后叫中央水门）
  { const x = 1021, y = 751; mk('circle', { cx: x, cy: y, r: 7, fill: 'url(#stBlue)', opacity: 0.8 }, wg); mk('rect', { x: x - 3.4, y: y - 3.4, width: 6.8, height: 6.8, fill: '#efe7d6', stroke: '#2f2e36', 'stroke-width': 0.7, transform: `rotate(45 ${x} ${y})` }, wg); mk('path', { d: `M${x - 2},${y + 0.6} q1,-1 2,0 q1,1 2,0`, fill: 'none', stroke: '#2e89c2', 'stroke-width': 0.6 }, wg); }
  // 盾碑：1020年举盾者陨落，盾抬回来立在墙上
  { const x = 944, y = 973; mk('circle', { cx: x, cy: y, r: 7, fill: 'url(#stWhite)' }, wg); mk('path', { d: `M${x - 2.8},${y - 3.2} h5.6 v2.6 q0,3.2 -2.8,4.8 q-2.8,-1.6 -2.8,-4.8 Z`, fill: '#e9e4d6', stroke: '#2f2e36', 'stroke-width': 0.55 }, wg); mk('path', { d: `M${x},${y - 2.6} v6`, stroke: '#8a7552', 'stroke-width': 0.45 }, wg); }
  // 四十七骑门：北段的缺口和山铜闸门
  { const y = 442, x = wallX(y); mk('rect', { x: x - 3.2, y: y - 1.2, width: 6.4, height: 2.4, fill: '#d8cfbd', stroke: '#2f2e36', 'stroke-width': 0.55 }, wg); mk('path', { d: `M${x - 1.6},${y - 1.2} v2.4 M${x + 1.6},${y - 1.2} v2.4`, stroke: '#2f2e36', 'stroke-width': 0.45 }, wg); }

  // ---- 星纱轨：墙后干线，往东三条支线（金鸢城、对炉街、星环） ----
  const rg = mk('g', { id: 'stRail' }, null);
  vb.insertBefore(rg, wg);
  const off = []; for (let s = 0; s <= WL; s += 8) { const p = wp.getPointAtLength(s); if (p.y < 400 || p.y > 965) continue; const [tx, ty] = tan(s); off.push([p.x + ty * 24, p.y - tx * 24]); }
  const rail = (pts, main) => { const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#cdbfff', 'stroke-width': main ? 5 : 3.6, opacity: 0.3, filter: 'url(#stBlur)' }, rg); mk('path', { d, fill: 'none', stroke: '#3c3646', 'stroke-width': main ? 1.7 : 1.3, 'stroke-linecap': 'round' }, rg); mk('path', { d, fill: 'none', stroke: '#f5f2ea', 'stroke-width': main ? 1.7 : 1.3, 'stroke-dasharray': '0.9 1.5' }, rg); return d; };
  const trunk = rail(off, true);
  const near = (y) => off.reduce((b, p) => (Math.abs(p[1] - y) < Math.abs(b[1] - y) ? p : b), off[0]);
  const j1 = near(758), j2 = near(905), j3 = near(560);
  rail([j1, [1110, 772], [1186, 770], [1262, 776], [1340, 770], [1420, 762], [1497, 752]], false);
  rail([j2, [1080, 904], [1160, 898], [1236, 884], [1292, 858], [1350, 846], [1408, 868], [1446, 924], [1474, 990], [1490, 1068]], false);
  rail([j3, [1110, 560], [1190, 556], [1270, 558], [1340, 560], [1386, 560], [1384, 504], [1372, 448], [1364, 416]], false);
  for (const [x, y] of [j1, j2, j3]) { mk('circle', { cx: x, cy: y, r: 1.9, fill: '#f5f2ea', stroke: '#3c3646', 'stroke-width': 0.6 }, rg); }
  // 星环：约3300年研究所从对炉街搬来，约3380年头一列星纱列车在这一圈轨上试成
  { const x = 1364, y = 406, r = 8.5; mk('circle', { cx: x, cy: y, r: r + 6, fill: 'url(#stViolet)', opacity: 0.75 }, rg); mk('circle', { cx: x, cy: y, r, fill: 'none', stroke: '#3c3646', 'stroke-width': 1.5 }, rg); mk('circle', { cx: x, cy: y, r, fill: 'none', stroke: '#f5f2ea', 'stroke-width': 1.5, 'stroke-dasharray': '0.9 1.5' }, rg); for (const [dx, dy] of [[-2.4, -1.2], [1.8, -2], [0.4, 2.2]]) mk('rect', { x: x + dx - 1.1, y: y + dy - 1.1, width: 2.2, height: 2.2, fill: '#e8e2f6', stroke: '#3c3646', 'stroke-width': 0.35 }, rg); window.__stHide.push([x, y, r + 3]); }
  // 一列车：干线上往南开
  { const el = mk('path', { d: trunk, fill: 'none' }, rg); const L = el.getTotalLength(); const s0 = L * 0.42; for (let k = 0; k < 4; k++) { const p = el.getPointAtLength(s0 - k * 3.4), q = el.getPointAtLength(s0 - k * 3.4 + 1); const a = Math.atan2(q.y - p.y, q.x - p.x) * 180 / Math.PI; mk('rect', { x: p.x - 1.5, y: p.y - 0.9, width: 3, height: 1.8, rx: 0.6, fill: k === 0 ? '#5a4f7a' : '#ece6f8', stroke: '#2b2638', 'stroke-width': 0.35, transform: `rotate(${a} ${p.x} ${p.y})` }, rg); } el.remove(); }

  // ---- 路：王道、金鸢城往北的大路、往星湖的大道；西边的裂影粮道 ----
  const roads = mk('g', { id: 'stRoads' }, null);
  vb.insertBefore(roads, rg);
  const road = (pts) => { const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#f4ead2', 'stroke-width': 1.5, opacity: 0.9 }, roads); mk('path', { d, fill: 'none', stroke: '#8a6e3e', 'stroke-width': 0.55, 'stroke-dasharray': '3 1.2' }, roads); };
  road([[1497, 738], [1440, 738], [1380, 742], [1330, 740], [1250, 736], [1180, 730], [1110, 738], [1050, 748], [1026, 751]]);
  road([[1512, 721], [1500, 660], [1474, 588], [1410, 545], [1320, 524], [1220, 508], [1130, 480], [1060, 470]]);
  road([[1538, 732], [1620, 690], [1700, 628], [1738, 602], [1820, 556], [1900, 500], [1940, 456]]);


  // 界碑：870年霜降月刀桥底下立头一块，889年北到冰原边上的山脚、南到南段的尽头，白石朝东、黑曜石朝西；墙下一箭之地是射界，种着麦
  { const jg = mk('g', { id: 'stJiebei' }, null); vb.insertBefore(jg, wg);
    for (let s = 4; s < WL - 2; s += 2) { const p = wp.getPointAtLength(s); const [tx, ty] = tan(s); mk('circle', { cx: p.x - ty * 5.2, cy: p.y + tx * 5.2, r: 1.5, fill: '#e3c766', opacity: 0.55 }, jg); }
    for (let s = 6; s < WL - 2; s += 9) { const p = wp.getPointAtLength(s); const [tx, ty] = tan(s); const x = p.x - ty * 9, y = p.y + tx * 9; mk('path', { d: `M${x},${y - 1.6} L${x + 1.1},${y} L${x},${y + 1.6} Z`, fill: '#f6f3ea', stroke: '#2f2e36', 'stroke-width': 0.25 }, jg); mk('path', { d: `M${x},${y - 1.6} L${x - 1.1},${y} L${x},${y + 1.6} Z`, fill: '#1d1a20', stroke: '#2f2e36', 'stroke-width': 0.25 }, jg); } }
  // 七柱碑：纷争纪9319年塌墙的那一截立起七根整块凿的石柱
  { const x = 984, y = 896; for (let k = 0; k < 7; k++) mk('rect', { x: x + k * 1.6, y: y - 3.2 - (k % 2) * 0.6, width: 1, height: 3.6, fill: '#f4f1ea', stroke: '#2f2e36', 'stroke-width': 0.25 }, wg); }
  // 金鸢城河岸上的账碑：669年开春头一面，往后每年黎明日添一面，一面一面往下游排
  { const rv = pack.rivers.find((r) => r && r.i === 232); if (rv) { const pts = []; for (const c of rv.cells || []) if (c >= 0 && C.p[c]) pts.push(C.p[c]); const seg = pts.filter(([x, y]) => x > 1532 && x < 1600 && Math.abs(y - 760) < 40); seg.forEach(([x, y], k) => { if (k % 1 === 0) mk('rect', { x: x - 0.7, y: y + 2.2, width: 1.4, height: 2, fill: '#f6f3ea', stroke: '#3a3226', 'stroke-width': 0.25 }, wg); }); } }

  // ---- 西边的路：往西的路（661年灰雨城城西的塌口出城，一路往西扎营，790年停在黑曜平原）、灯路、渊月长廊、灰之魔女修的粮道、黑耀运河 ----
  const wr = mk('g', { id: 'stWestRoads' }, null);
  vb.insertBefore(wr, document.getElementById('labels'));
  { const d = smooth([[1032, 784], [980, 792], [900, 806], [820, 830], [740, 852], [660, 872], [590, 862], [530, 832], [470, 800], [420, 762], [392, 706], [384, 668], [440, 650], [510, 650], [570, 684], [604, 708]]); mk('path', { d, fill: 'none', stroke: '#f3ead6', 'stroke-width': 2, opacity: 0.6 }, wr); mk('path', { d, fill: 'none', stroke: '#6b4a32', 'stroke-width': 0.8, 'stroke-dasharray': '4 2.4' }, wr); }
  const lampRoad = (pts) => { const d = smooth(pts); const el = mk('path', { d, fill: 'none', stroke: '#3a2a26', 'stroke-width': 0.5, opacity: 0.6 }, wr); const L = el.getTotalLength(); for (let s = 4; s < L; s += 9) { const p = el.getPointAtLength(s); mk('circle', { cx: p.x, cy: p.y, r: 2.2, fill: 'url(#stAmber)', opacity: 0.55 }, wr); mk('circle', { cx: p.x, cy: p.y, r: 0.55, fill: '#ffe2a8' }, wr); } };
  lampRoad([[616, 714], [560, 690], [470, 668], [380, 660]]);
  lampRoad([[616, 714], [640, 640], [664, 540], [682, 446]]);
  lampRoad([[640, 640], [590, 500], [520, 380], [500, 312]]);
  lampRoad([[500, 312], [440, 260], [384, 210]]);
  lampRoad([[616, 714], [520, 760], [380, 820], [240, 862], [205, 866]]);
  lampRoad([[616, 714], [600, 800], [570, 900], [552, 960], [536, 976]]);
  lampRoad([[552, 960], [586, 1030], [606, 1100], [614, 1124]]);
  const yuan = (pts) => { const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#b08cff', 'stroke-width': 3.6, opacity: 0.25, filter: 'url(#stBlur)' }, wr); mk('path', { d, fill: 'none', stroke: '#2a2140', 'stroke-width': 1.5 }, wr); mk('path', { d, fill: 'none', stroke: '#cdb8ff', 'stroke-width': 1.5, 'stroke-dasharray': '0.9 1.6' }, wr); };
  yuan([[640, 724], [600, 800], [570, 900], [552, 960], [536, 974]]);
  yuan([[640, 704], [700, 690], [760, 676], [792, 672]]);
  mk('circle', { cx: 792, cy: 672, r: 2, fill: '#cdb8ff', stroke: '#2a2140', 'stroke-width': 0.6 }, wr);
  const grainRoad = (pts) => { const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#e9e0d0', 'stroke-width': 1.2, opacity: 0.55 }, wr); mk('path', { d, fill: 'none', stroke: '#3a2a26', 'stroke-width': 0.6, 'stroke-dasharray': '1.2 1.6' }, wr); };
  grainRoad([[226, 1082], [262, 960], [300, 800], [330, 640], [350, 500]]);
  grainRoad([[528, 966], [500, 820], [440, 640], [362, 500]]);
  { const canal = (pts, dash) => { const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#24506a', 'stroke-width': 2.8, opacity: 0.55, 'stroke-linecap': 'round' }, wr); mk('path', { d, fill: 'none', stroke: '#9cc9e3', 'stroke-width': 1.6, 'stroke-dasharray': dash, 'stroke-linecap': 'round' }, wr); };
    canal([[436, 800], [464, 792], [496, 772], [530, 756], [566, 738], [596, 724]], '');
    canal([[640, 716], [700, 718], [760, 726], [800, 756], [834, 796]], '3 2.4'); }
  // 红刺坡：深潮点起的一串灯，862年以后七城添了几座烽灯
  { for (let k = 0; k < 6; k++) mk('circle', { cx: 862 + k * 6, cy: 1030 + Math.sin(k) * 2, r: 2.6, fill: 'url(#stAmber)', opacity: 0.9 }, wr); mk('circle', { cx: 900, cy: 1022, r: 4, fill: 'url(#stEmber)' }, wr); }

  // ---- 天上的、发光的 ----
  const mg = mk('g', { id: 'stMagic' }, null);
  vb.insertBefore(mg, document.getElementById('labels'));
  // 北辰塔824年落进湾口外头的海里：海上一圈波纹
  { const x = 368, y = 104; for (const r of [3, 5.5, 8]) mk('circle', { cx: x, cy: y, r, fill: 'none', stroke: '#eef6fb', 'stroke-width': 0.5, opacity: 0.8 }, mg); }
  // 寒天之钉
  { const lg = mk('linearGradient', { id: 'stCrystal', x1: 0, y1: 0, x2: 1, y2: 0 }, pdefs); mk('stop', { offset: '0', 'stop-color': '#9fd0ff' }, lg); mk('stop', { offset: '0.45', 'stop-color': '#eef8ff' }, lg); mk('stop', { offset: '1', 'stop-color': '#5d8fd6' }, lg); mk('ellipse', { cx: 1232, cy: 116, rx: 46, ry: 26, fill: 'url(#stBlue)', opacity: 0.55 }, mg); for (let k = 0; k < 30; k++) { const a = rnd() * Math.PI * 2, d = Math.sqrt(rnd()) * 32; const cx = 1232 + Math.cos(a) * d * 1.3, cy = 114 + Math.sin(a) * d * 0.7; const h = 6 + rnd() * 14, w = 1.1 + rnd() * 1.2, lean = (rnd() - 0.5) * 2.6; mk('path', { d: `M${cx - w},${cy} L${cx + lean},${cy - h} L${cx + w},${cy} L${cx},${cy + w * 0.6} Z`, fill: 'url(#stCrystal)', stroke: '#3f6aa8', 'stroke-width': 0.3 }, mg); } }
  // 罗盘、比例尺照 Azgaar 自己的
  { const b = document.querySelector('#mapLayers [data-layer=compass]'); if (b && b.classList.contains('buttonoff')) { b.click(); await sleep(700); } }


  // ---- 地名 ----
  if (!document.getElementById('pFont')) { const l = document.createElement('link'); l.id = 'pFont'; l.rel = 'stylesheet'; l.href = 'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700;900&display=swap'; document.head.appendChild(l); }
  const lab = mk('g', { id: 'stLabels', 'font-family': '"Noto Serif SC", serif', 'text-anchor': 'middle', 'paint-order': 'stroke', 'stroke-linejoin': 'round' }, vb);
  const T1 = (s, x, y, fs, o = {}) => { const e = mk('text', Object.assign({ x, y, 'font-size': fs, 'font-weight': 900, fill: '#2c261f', stroke: '#f6f0e2', 'stroke-width': fs * 0.2, 'letter-spacing': fs * 0.1 }, o), lab); e.textContent = s; return e; };
  const region = (s, x, y, fs, o = {}) => T1(s, x, y, fs, Object.assign({ 'font-weight': 500, fill: '#5b5245', stroke: '#f3eee2', 'stroke-width': fs * 0.16, 'letter-spacing': fs * 0.45, opacity: 0.9 }, o));
  const sea = (s, x, y, fs, o = {}) => T1(s, x, y, fs, Object.assign({ 'font-weight': 500, fill: '#2d5f73', stroke: '#d9eef3', 'stroke-width': fs * 0.12, 'letter-spacing': fs * 0.6, opacity: 0.85 }, o));
  const magic = (s, x, y, fs, o = {}) => T1(s, x, y, fs, Object.assign({ 'font-weight': 700, fill: '#3a3a52', stroke: '#f6f0e2', 'stroke-width': fs * 0.2, 'letter-spacing': fs * 0.08 }, o));

  T1('西 陆', 520, 540, 34, { 'font-weight': 900, fill: '#3b2f2a', stroke: '#f3eee2', 'stroke-width': 3, 'letter-spacing': 16, opacity: 0.32 });
  T1('东 陆', 1660, 640, 34, { 'font-weight': 900, fill: '#3b3528', stroke: '#f3eee2', 'stroke-width': 3, 'letter-spacing': 16, opacity: 0.32 });
  T1('黑 耀 帝 国', 560, 604, 13, { 'font-weight': 700, fill: '#5a2a24', opacity: 0.8, 'letter-spacing': 5 });
  T1('晨 曦 帝 国', 1560, 690, 13, { 'font-weight': 700, fill: '#6b5532', opacity: 0.75, 'letter-spacing': 5 });
  for (const [s, x, y] of [['月镜', 1996, 482], ['风铃', 1650, 500], ['蔷薇', 1860, 1012], ['银鹿公国', 1694, 742]]) region(s, x, y, 9.5, { 'font-weight': 700, fill: '#6b5532', opacity: 0.75 });
  for (const [s, x, y, fs] of [['西海', 110, 640, 24], ['北海', 470, 58, 20], ['冰海', 1350, 74, 16], ['南冰海', 1080, 1328, 18], ['银帆外海', 2150, 690, 11]]) sea(s, x, y, fs);
  sea('盐 海', 360, 1030, 14, { fill: '#6b2620', stroke: '#f3e1dc' });
  T1('老滩', 138, 1134, 5.5, { 'font-weight': 700, 'stroke-width': 1, fill: '#7a2f28' });
  T1('盐海门', 168, 1214, 7, { 'font-weight': 700, fill: '#7a2f28', 'stroke-width': 1.4 });
  for (const [s, x, y, fs] of [['枯祭原', 352, 528, 10], ['西境荒原', 360, 612, 9], ['裂影旧地', 404, 818, 8.5], ['黑石高地', 640, 628, 8.5], ['黑曜平原', 586, 782, 8], ['环山', 700, 826, 8.5], ['灰高原', 770, 918, 9], ['黑岭', 548, 952, 7], ['旧矿带', 596, 1050, 8], ['断岭', 700, 1104, 7.5], ['冰原', 960, 420, 10], ['化圣雪原', 990, 270, 15], ['月银原', 905, 146, 9.5], ['北境', 1140, 452, 9], ['曜冠山', 1300, 330, 11], ['龙眠天脊', 1760, 140, 12], ['翠冠林海', 1868, 304, 14], ['曙辉平原', 1330, 812, 12], ['蜜酒丘陵', 1880, 1046, 9], ['中央旧战原', 1112, 640, 9], ['星湖', 1896, 520, 9], ['南境', 1238, 962, 8.5]]) region(s, x, y, fs);
  T1('死 域', 880, 1140, 22, { 'font-weight': 900, fill: '#3e3a37', stroke: '#e8e3da', 'stroke-width': 2.2, 'letter-spacing': 14, opacity: 0.72 });
  T1('沙 海', 1080, 1200, 22, { 'font-weight': 900, fill: '#6b5532', stroke: '#f3ead6', 'stroke-width': 2.2, 'letter-spacing': 14, opacity: 0.7 });
  region('玻璃平原', 1000, 1046, 8, { fill: '#4f6670' });
  for (const [s, x, y, r] of [['南 界', 742, 1104, -36], ['南 界', 1262, 1028, 4]]) T1(s, x, y, 8.5, { 'font-weight': 700, fill: '#8a2f28', stroke: '#f6eee6', 'stroke-width': 1.8, 'letter-spacing': 3, transform: `rotate(${r} ${x} ${y})` });
  T1('落 星 洼', 1330, 1090, 11, { 'font-weight': 700, fill: '#1f4f69', stroke: '#e6f1f6', 'stroke-width': 1.8, 'letter-spacing': 4 });
  { const e = T1('白碑长垒', 1060, 560, 11, { 'font-weight': 900, fill: '#3a3944', stroke: '#fbf8f0', 'stroke-width': 2.4, 'letter-spacing': 6, style: 'writing-mode: vertical-rl' }); }
  { const e = T1('星纱轨', 1084, 860, 8, { 'font-weight': 700, fill: '#4b3f7a', stroke: '#f6f3fb', 'stroke-width': 1.6, 'letter-spacing': 3, style: 'writing-mode: vertical-rl' }); }
  { const e = T1('界碑与射界', 978, 640, 6.5, { 'font-weight': 700, fill: '#5b4a33', stroke: '#fbf8f0', 'stroke-width': 1.3, 'letter-spacing': 2, style: 'writing-mode: vertical-rl' }); }
  for (const [s, x, y] of [['鹰石', 1058, 436], ['燕巢', 1054, 482], ['塌门', 998, 742], ['水门段城', 1050, 764], ['鹳桥', 1006, 870], ['石鼓·南线大营', 950, 910], ['红炉', 978, 950]]) T1(s, x, y, 5.5, { 'font-weight': 700, fill: '#3a3944', 'stroke-width': 1.1 });
  for (const [s, x, y] of [['南沼', 960, 1003], ['圣土', 906, 958], ['擎天级', 868, 1012], ['盾碑', 922, 944]]) T1(s, x, y, 5.5, { 'font-weight': 700, fill: '#3a3944', 'stroke-width': 1.1 });
  const cityLabel = (s, x, y, R, fs, o = {}) => T1(s, x, y + R * 1.12 + fs * 0.95, fs, o);
  for (const [s, x, y, R, fs] of [['金鸢城', 1518, 742, 25, 15], ['星冠圣城', 1386, 560, 15, 11], ['炉城', 1562, 1106, 14, 10], ['高岚城', 1697.1, 518.7, 11, 8.5], ['露玫城', 1822.9, 981.5, 11, 8.5], ['碧穹王庭', 2068, 308, 9, 8], ['白冠城', 1186, 756, 8.5, 7.5], ['白鸢骑士城', 1408, 868, 8, 7.5], ['金穗王仓城', 1606, 854, 8.5, 7.5], ['银帆', 2069.8, 747.3, 8, 8]]) cityLabel(s, x, y, R, fs);
  T1('银湖城', 1952, 414, 8.5);
  for (const [s, x, y, R, fs] of [['烬灭之都', 616, 714, 24, 14], ['苍焰角城', 528, 980, 11, 8.5], ['血棘红园', 682, 435.4, 10.5, 8.5], ['骸钟墓城', 374, 658, 11, 8.5], ['魇镜幻都', 497, 302, 10, 8.5], ['黑翼天塔', 374, 200, 8.5, 8], ['雷狱铁城', 616, 1134, 10, 8.5], ['深潮蓝堡', 198, 868, 10, 8.5]]) cityLabel(s, x, y, R, fs, { fill: '#3a2420', stroke: '#efe6dc' });
  for (const [s, x, y] of [['曜石审判庭', 1564, 656], ['蓝湾', 2020, 877], ['老岭', 1694, 726], ['晨星岭', 1276, 950], ['四路庄', 1650, 880], ['曙禾镇', 1556, 790], ['誓桥', 1474, 600], ['白鹿驿', 1738, 614], ['雾铃驿城', 1760, 698], ['穴镇', 1892, 966], ['铃尾市集', 1880, 1037], ['白鹿书堡', 1980, 571], ['朝峰城', 1290, 404], ['守路的山城', 1356, 380], ['南枝村', 1410, 412], ['石饲之乡', 1250, 1012], ['苍麦坡', 1496, 1020], ['风车镇', 1540, 936], ['铁瀑', 1497, 1049], ['对炉街', 1500, 1102], ['篱口', 1760, 1118], ['净血院', 1790, 732], ['月露集', 1894, 695], ['林铃营', 1800, 469], ['外环林市', 1870, 412], ['霜渡', 1090, 522], ['霜厅城（空了）', 1090, 434], ['学院城', 1000, 930], ['灰雨城（废墟）', 1060, 792], ['天脊北路的最后一站', 1386, 236]]) T1(s, x, y + 4, 5.5, { 'font-weight': 700, 'stroke-width': 1 });
  for (const [s, x, y] of [['羊梁营', 665, 680], ['秤杆镇', 352, 452], ['灰炉', 748, 852], ['山口边营', 858, 474], ['断丘上的垒', 814, 866], ['荒丘', 616, 908], ['断岭的铸炉', 690, 1072], ['辙口城', zhekou[0], zhekou[1] + 12], ['黑石湾', 154, 740], ['赤盐边镇', 286, 1088], ['红刺坡', 878, 1046], ['东门外的站井', 792, 684]]) T1(s, x, y + 4, 5.5, { 'font-weight': 700, 'stroke-width': 1, fill: '#3a2420' });
  for (const [s, x, y, fs] of [['星环', 1364, 428, 7.5], ['寒天之钉', 1232, 146, 8], ['碎碑矿坑', CANON[0][0], CANON[0][1] - 9, 6.5], ['无名碑林', CANON[1][0], CANON[1][1] - 12, 6.5], ['灰岗', CANON[2][0] + 14, CANON[2][1] - 4, 6.5], ['渊月长廊', 586, 860, 6.5], ['灯路', 470, 650, 6.5], ['往西的路', 860, 812, 6.5], ['黑耀运河', 520, 772, 6.5], ['风铃的断崖', 1760, 650, 6.5], ['火环', 1078, 1274, 6.5], ['河心三日', 702, 1030, 6], ['北辰塔落海处', 368, 124, 6]]) magic(s, x, y, fs);
  // 题签
  { const g = mk('g', { id: 'stTitle' }, lab); mk('rect', { x: 1560, y: 1210, width: 470, height: 140, rx: 6, fill: '#f3ecdc', stroke: '#6b5532', 'stroke-width': 1.4, opacity: 0.94 }, g); mk('rect', { x: 1566, y: 1216, width: 458, height: 128, rx: 4, fill: 'none', stroke: '#6b5532', 'stroke-width': 0.6 }, g);
    const t1 = mk('text', { x: 1795, y: 1250, 'font-size': 26, 'font-weight': 900, fill: '#3a2f22', 'letter-spacing': 6 }, g); t1.textContent = '奥尔德兰 · 山铜纪';
    const t2 = mk('text', { x: 1795, y: 1276, 'font-size': 14, 'font-weight': 500, fill: '#5b4a33', 'letter-spacing': 2 }, g); t2.textContent = '麦的年月 · 约九百年 · 黑耀立国 · 墙下立起界碑';
    const t3 = mk('text', { x: 1795, y: 1296, 'font-size': 10, 'font-weight': 500, fill: '#5b4a33', 'letter-spacing': 1 }, g); t3.textContent = '白线是长垒，墙西黑白小菱是界碑，紫线是星纱轨，暗紫是渊月长廊，灰台是熄了的高座';
    const km = 19, x0 = 1690, y0 = 1326, seg = 1000 / km; for (let k = 0; k < 4; k++) mk('rect', { x: x0 + k * seg, y: y0, width: seg, height: 4, fill: k % 2 ? '#f3ecdc' : '#3a2f22', stroke: '#3a2f22', 'stroke-width': 0.6 }, g);
    for (let k = 0; k <= 4; k++) { const tt = mk('text', { x: x0 + k * seg, y: y0 - 4, 'font-size': 10, 'font-weight': 500, fill: '#3a2f22', 'stroke-width': 0 }, g); tt.textContent = k === 4 ? '4000 公里' : String(k * 1000); }
    const sb = document.getElementById('scaleBar'); if (sb) sb.style.display = 'none'; }
  window.__bronzeMoved = moved;
  try { await document.fonts.load('900 20px "Noto Serif SC"', '奥尔德兰纷争纪西陆东陆金鸢城白石长垒死域'); await document.fonts.load('500 20px "Noto Serif SC"', '西海南冰海盐海'); await sleep(1500); } catch (e) { log.push('字体 ' + e); }
  window.__stHideIcons = () => { let n = 0; for (const [x, y, r] of window.__stHide) { for (const u of document.querySelectorAll('#terrain use')) { if (u.style.display === 'none') continue; const ux = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2, uy = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2; if ((ux - x) ** 2 + (uy - y) ** 2 <= r * r) { u.style.display = 'none'; n++; } } } return n; };
  log.push('城下藏符号 ' + window.__stHideIcons());
  return log.join('；');
})();
