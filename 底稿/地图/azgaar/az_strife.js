// 纷争纪·炮的年月（约3600年）样张：在 az_reset.sh、碧湾、盐海（az_salthai.js）、死域（az_siyu.js）、海与三河（az_seas_strife.js）之后跑。
//   照补卷_19 地图的几层：墙东墙西从此是两张图，东边墙后的段城一座挨一座，段城后头隔着几个月的路是少数几座巨城（金鸢城、星冠圣城、炉城）；
//   西边是营、营城和高座，高座底下的营城是那一边的巨城。约3400年到3600年墙后铺起了星纱轨，往东拉了支线到金鸢城和对炉街。
//   长垒照用户在 .map 里画的那一道（参考/长垒_用户画.tsv，跑以前用 embed.py 塞进 WALL_PTS），这一纪没有阿卡迪亚那两道圈
//   高座七十二座，炮的年月到这时候倒下十几尊，空的高座画成灰的（神谱方向稿第三节：灯的年月末魔神七十二，炮的年月末五十）
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

  // 墙东：金鸢城几百万人，星冠圣城、炉城，三个王国的王城（白鸢、湖星、金穗），白冠城是学城
  const EAST = [
    ['jinyuan', 1518, 742, 22, 'gold', 3], ['xingguan', 1386, 560, 15, 'holy', 2], ['luxin', 1562, 1106, 14, 'forge', 2],
    ['baiguan', 1186, 756, 9, 'holy', 2], ['xinghu', 1952, 443.5, 11, 'silver', 2], ['baiyuan', 1408, 868, 8.5, 'imperial', 2], ['jinsui', 1606, 854, 8.5, 'gold', 2],
    ['yinfan', 2069.8, 747.3, 7, 'tide', 2], ['cuiguan', 2068, 308, 8, 'elf', 2],
  ];
  for (const m of EAST) { if (m[0] === 'xinghu') continue; cityPlan(...m); }
  // 星湖城：那一夜湖上空的塔砸进湖里，城沉了一半。城画在北岸上（这一组不套陆地遮罩），朝湖那一半泡在水里
  { const x = 1952, y = 436, R = 11; const free = mk('g', { id: 'stXinghu' }, null); vb.insertBefore(free, document.getElementById('rivers'));
    cityPlan('xinghu', x, y, R, 'silver', 2); free.appendChild(document.getElementById('st_xinghu'));
    mk('path', { d: `M${x - R * 1.2},${y + 0.5} A${R * 1.2},${R * 1.2} 0 0 0 ${x + R * 1.2},${y + 0.5} Z`, fill: '#8fb7cf', opacity: 0.62 }, free);
    for (let k = 0; k < 4; k++) mk('path', { d: `M${x - 8 + k * 4.5},${y + 4 + (k % 2) * 2.5} q1.2,-0.8 2.4,0 q1.2,0.8 2.4,0`, fill: 'none', stroke: '#eef6fb', 'stroke-width': 0.4, opacity: 0.95 }, free); }
  // 墙西：高座底下的营城
  const WEST = [
    ['yancheng', 682, 435.4, 9, 'rose', 2], ['zhongcheng', 374, 658, 9, 'bone', 2], ['rongyuan', 528, 980, 9, 'ember', 2], ['huiying', 902, 686, 8, 'camp', 2],
    ['wuhu', 497, 302, 8, 'mirror', 2], ['chaomen', 198, 868, 7.5, 'abyss', 2], ['shankou', 858, 462, 6, 'camp', 2], ['duanying', 616, 1134, 6, 'ember', 2],
  ];
  for (const m of WEST) cityPlan(...m);
  const SMALL_E = [[1540, 810, 'gold'], [1979.8, 559, 'holy'], [1305, 385, 'imperial'], [1490, 1075, 'forge'], [1474, 588, 'imperial'], [1650, 868, 'gold'], [1540, 784, 'gold'], [1738, 602, 'gold'], [1760, 686, 'gold'], [1892.4, 953.7, 'gold'], [1180, 1000, 'gold'], [1150, 950, 'imperial'], [1110, 470, 'silver'], [1694, 714, 'gold'], [1496, 1008, 'gold'], [1820, 470, 'elf'], [1894.2, 683.2, 'elf'], [1122, 868, 'imperial'], [1276, 938, 'imperial'], [1386, 224, 'silver'], [1080, 525, 'silver']];
  for (const [x, y, th] of SMALL_E) smallCity(x, y, th);
  const SMALL_W = [[154, 728, 'abyss'], [814, 854, 'camp'], [616, 896, 'ember'], [410, 580, 'camp']];
  for (const [x, y, th] of SMALL_W) smallCity(x, y, th);
  // 废了的：穹都、旧神渡、鸦岭（西征东撤以后没人肯住）
  ruin(616, 714, 24, '#4a4450'); ruin(1100, 672, 12); ruin(730, 580, 6);

  // ---- 地上的东西 ----
  const ground = mk('g', { id: 'stGround' }, null);
  vb.insertBefore(ground, document.getElementById('rivers'));
  // 神渡盆地（星坑盆地）的坑沿
  { const cx = 1100, cy = 672, r = 92; for (let k = 0; k < 150; k++) { const a = k / 150 * Math.PI * 2, rr = r * (1 + 0.03 * Math.sin(5 * a)); const x1 = cx + Math.cos(a) * rr, y1 = cy + Math.sin(a) * rr, x2 = cx + Math.cos(a) * (rr - 4.5 - (k % 3)), y2 = cy + Math.sin(a) * (rr - 4.5 - (k % 3)); mk('line', { x1, y1, x2, y2, stroke: '#8d7f66', 'stroke-width': 0.55, opacity: 0.5 }, ground); } mk('path', { d: wob(cx, cy, r, 0.3, 0.6), fill: 'none', stroke: '#8d7f66', 'stroke-width': 0.7, opacity: 0.55 }, ground); }
  // 墙外打得最密的那一片：中段墙前一片一片烧过的地
  for (const [x, y, r] of [[952, 690, 26], [930, 640, 18], [960, 740, 20], [905, 720, 14], [968, 600, 14], [948, 800, 16], [960, 860, 14]]) mk('ellipse', { cx: x, cy: y, rx: r, ry: r * 0.72, fill: 'url(#stScorch)' }, ground);
  // 穹都：环山靠城那一面化成一层黑玻璃，山脊上砸出一个口子；上城落回环山，一块一块歪着
  { const cx = 616, cy = 714; let gapAng = 0.6; { const bins = new Array(36).fill(0); for (const u of document.querySelectorAll('#terrain use')) { const h = u.getAttribute('href'); if (!/hill|mount/.test(h)) continue; const x = +u.getAttribute('x') + (+u.getAttribute('width')) / 2 - cx, y = +u.getAttribute('y') + (+u.getAttribute('height')) / 2 - cy; const d = Math.hypot(x, y); if (d < 94 || d > 170) continue; bins[Math.floor(((Math.atan2(y, x) + Math.PI * 2) % (Math.PI * 2)) / (Math.PI * 2) * 36)]++; } let mi = 0; for (let k = 1; k < 36; k++) if (bins[k] < bins[mi]) mi = k; gapAng = (mi + 0.5) / 36 * Math.PI * 2; }
    const r = 98, a0 = gapAng + 0.3, a1 = gapAng + Math.PI * 2 - 0.3; const d = `M${cx + Math.cos(a0) * r},${cy + Math.sin(a0) * r} A${r},${r} 0 1 1 ${cx + Math.cos(a1) * r},${cy + Math.sin(a1) * r}`;
    mk('path', { d, fill: 'none', stroke: '#26222b', 'stroke-width': 2.6, opacity: 0.3 }, ground); mk('path', { d, fill: 'none', stroke: '#9b93ae', 'stroke-width': 0.5, opacity: 0.5, 'stroke-dasharray': '3 2' }, ground);
    const plates = [[-6, -8, 7, 4.4, 18], [9, -3, 5, 3.2, -24], [-10, 6, 4.2, 2.8, 40], [6, 9, 4, 2.4, -10], [-1, -18, 3.6, 2.2, 60]];
    for (const [dx, dy, rx, ry, a] of plates) { mk('ellipse', { cx: cx + dx, cy: cy + dy, rx, ry, fill: pat(`fall_${dx}`, 0.5, a, '#d9d5cc', '#8d8a90', 0.09, 'grid'), stroke: '#3b3a44', 'stroke-width': 0.4, transform: `rotate(${a} ${cx + dx} ${cy + dy})`, opacity: 0.85 }, ground); }
    for (const pts of [[[594, 726], [600, 734], [596, 742], [603, 750]], [[606, 730], [612, 738], [609, 746]], [[588, 738], [582, 746], [586, 754]]]) mk('path', { d: 'M' + pts.map((p) => p.join(',')).join('L'), fill: 'none', stroke: '#1f1b22', 'stroke-width': 0.9, opacity: 0.8 }, ground); }
  // 赤原：万兽期一场大火烧成的红土，172年秋矮人工兵的铲锋落处赤土自己隆起来成垒，往后雨冲不平
  { mk('ellipse', { cx: 800, cy: 880, rx: 46, ry: 26, fill: '#b9634a', opacity: 0.22 }, ground); for (const [x, y, a] of [[784, 872, -18], [804, 884, -12], [822, 874, -24]]) { const dd = `M${x - 9},${y} q9,-3.2 18,0`; mk('path', { d: dd, fill: 'none', stroke: '#6b3424', 'stroke-width': 1.4, transform: `rotate(${a} ${x} ${y})`, opacity: 0.75 }, ground); mk('path', { d: dd, fill: 'none', stroke: '#e3b49c', 'stroke-width': 0.4, transform: `rotate(${a} ${x} ${y - 0.6})`, opacity: 0.9 }, ground); } }
  // 黑穗原：帝国的麦田改种黑穗，一年比一年大
  { const pd = pat('heisui', 1.6, 35, 'rgba(0,0,0,0)', '#2d2620', 0.28, 'stripe'); mk('ellipse', { cx: 360, cy: 500, rx: 62, ry: 46, fill: pd, opacity: 0.45, mask: 'url(#land)' }, ground); }
  // 月银原、寒天之钉照旧在北边
  { const MX = 905, MY = 168; mk('ellipse', { cx: MX, cy: MY, rx: 62, ry: 30, fill: 'url(#stSilver)', opacity: 0.8 }, ground); for (let k = 0; k < 22; k++) { const a = rnd() * 6.28, d = Math.sqrt(rnd()) * 42; const x = MX + Math.cos(a) * d * 1.3, y = MY + Math.sin(a) * d * 0.6; if (!isDry(x, y)) continue; const r = 1 + rnd() * 2.4; mk('ellipse', { cx: x, cy: y, rx: r, ry: r * 0.7, fill: '#cfd6e6', stroke: '#7d869c', 'stroke-width': 0.3, opacity: 0.9 }, ground); } }
  // 盐海：岬角往西那一段北岸是老滩（红晶滩），联军1088年以后在滩上修了七座营垒，约3300到3400年叫珂伦娜一座一座围下来，往后空着立在滩上，第七座没开门，
  //   靠东那一座在岬角尖上（往后住了人，山铜纪叫赤盐边镇，往后是盐沼灯镇）；红滩链：从滩上往礁里拉铁链，链上挂灯，链尽头是盐垒
  { const wet = [...['saltsea_blob', 'bay_moon', 'feature_10'].map((id) => document.getElementById(id)).filter(Boolean)]; const sp2 = document.getElementById('map').createSVGPoint();
    const isWet = (x, y) => { sp2.x = x; sp2.y = y; return wet.some((e) => e.isPointInFill(sp2)); };
    const shoreDown = (x, y0, y1) => { for (let y = y0; y < y1; y += 0.5) if (isWet(x, y)) return y; return null; };
    const shoreUp = (x, y0, y1) => { for (let y = y0; y > y1; y -= 0.5) if (isWet(x, y)) return y; return null; };
    const forts = [];
    for (const x of [158, 179, 200, 221, 242, 263]) { const y = shoreDown(x, 1030, 1200); if (y !== null) forts.push([x, y - 4.5]); }
    forts.push([286.2, 1075.8]);
    const mg0 = mk('g', { id: 'stSaltChain' }, null); vb.insertBefore(mg0, document.getElementById('labels'));
    mk('path', { d: smooth(forts), fill: 'none', stroke: '#b86a58', 'stroke-width': 3.2, opacity: 0.35, 'stroke-linecap': 'round' }, mg0);
    forts.forEach(([x, y], k) => { const shut = k === 3; mk('rect', { x: x - 2, y: y - 2, width: 4, height: 4, fill: shut ? '#e9e4d6' : '#cfc8b6', stroke: '#4a4038', 'stroke-width': 0.45, transform: `rotate(45 ${x} ${y})` }, mg0); if (shut) mk('circle', { cx: x, cy: y, r: 0.7, fill: '#4a4038' }, mg0); else mk('path', { d: `M${x - 1.4},${y - 1} l2.8,2`, stroke: '#4a4038', 'stroke-width': 0.4 }, mg0); });
    window.__saltForts = forts;
    const chain = [[276, 1086], [286, 1098], [296, 1109], [308, 1119], [322, 1128]]; const cd = smooth(chain);
    mk('path', { d: cd, fill: 'none', stroke: '#3b2c26', 'stroke-width': 0.8, 'stroke-dasharray': '1.2 0.8' }, mg0);
    const el = mk('path', { d: cd, fill: 'none' }, mg0); const L = el.getTotalLength(); for (let s = 0; s <= L; s += 7) { const p = el.getPointAtLength(s); mk('circle', { cx: p.x, cy: p.y, r: 4.2, fill: 'url(#stAmber)', opacity: 0.85 }, mg0); mk('rect', { x: p.x - 1.2, y: p.y - 1.2, width: 2.4, height: 2.4, fill: '#f1e3d4', stroke: '#4a3a30', 'stroke-width': 0.35 }, mg0); } el.remove();
    // 潮宫：沉在湾底（往后的赤盐沉宫），水底下一圈淡淡的影子
    mk('circle', { cx: 357.3, cy: 1074.9, r: 9, fill: 'none', stroke: '#6f3e38', 'stroke-width': 0.6, 'stroke-dasharray': '1.5 1.2', opacity: 0.6 }, mg0); mk('circle', { cx: 357.3, cy: 1074.9, r: 5, fill: 'none', stroke: '#6f3e38', 'stroke-width': 0.45, opacity: 0.5 }, mg0);
    // 盐沼：南岸，运晶的船在盐沼边上岸
    { const x = 330, y = shoreUp(x, 1250, 1120); if (y !== null) { window.__saltMarsh = [x, y + 6]; for (let k = 0; k < 8; k++) mk('path', { d: `M${x - 9 + k * 2.6},${y + 5 + (k % 3)} q0.6,-1.2 1.2,0 q0.6,-1.2 1.2,0`, fill: 'none', stroke: '#7f9a92', 'stroke-width': 0.4 }, mg0); } } }

  // ---- 高座：七十二座，倒下的那几尊的高座空着 ----
  const seats = mk('g', { id: 'stSeats' }, null);
  vb.insertBefore(seats, document.getElementById('labels'));
  const seatAt = [], seatInfo = [];
  const seat = (x, y, lit, big = 1) => {
    const w = 6.2 * big, h = 3.4 * big;
    if (lit) mk('circle', { cx: x, cy: y - h * 0.9, r: 7 * big, fill: 'url(#stEmberS)' }, seats);
    mk('path', { d: `M${x - w / 2},${y + h / 2} L${x - w * 0.32},${y - h / 2} L${x + w * 0.32},${y - h / 2} L${x + w / 2},${y + h / 2} Z`, fill: lit ? '#2a2322' : '#8e8a84', stroke: lit ? '#120d0c' : '#5d5a55', 'stroke-width': 0.45, filter: 'url(#stShadow)' }, seats);
    mk('path', { d: `M${x - w * 0.32},${y - h / 2} L${x + w * 0.32},${y - h / 2}`, stroke: lit ? '#6a4a3a' : '#b6b1a8', 'stroke-width': 0.5 }, seats);
    if (lit) { mk('circle', { cx: x, cy: y - h / 2 - 0.4, r: 1.1 * big, fill: '#ffd08a' }, seats); mk('circle', { cx: x, cy: y - h / 2 - 0.4, r: 2.6 * big, fill: 'url(#stEmber)' }, seats); }
    seatAt.push([x, y]); seatInfo.push([+x.toFixed(1), +y.toFixed(1), lit ? 1 : 0, big]); window.__stHide.push([x, y, 4.5 * big]);
  };
  // 有名的几座先摆：黑穗原原心、万角原，还有营城背后的那几座
  // 落在水里或者死域里的往近处的干地上挪（灰岗那一带条目估的点叫盐海盖住了）
  const landNear = (x, y, maxR = 70) => { const ok = (xx, yy) => isDry(xx, yy) && (slY(xx) === null || yy < slY(xx) - 8); if (ok(x, y)) return [x, y]; for (let r = 4; r <= maxR; r += 4) for (let a = 0; a < 360; a += 15) { const xx = x + r * Math.cos(a * Math.PI / 180), yy = y + r * Math.sin(a * Math.PI / 180); if (ok(xx, yy)) return [xx, yy]; } return [x, y]; };
  // 铸枷者在旧矿带（七座坑一字排开，第七坑往后叫碎碑矿坑）、噬名者在沉碑泽（往后无名碑林）、城破之后的鸦在灰岗（山铜纪补卷_14 地图的几层）
  const canonSeats = [[572, 970], [462, 736], [520, 1100]].map(([x, y]) => landNear(x, y));
  window.__stCanonSeats = canonSeats.map((p) => p.map((v) => +v.toFixed(1)));
  const named = [...canonSeats.map(([x, y]) => [x, y, 1, 1.12]), [352, 476, 1, 1.5], [540, 560, 1, 1.4], [682, 418, 1, 1.15], [374, 640, 1, 1.15], [528, 962, 1, 1.15], [902, 668, 1, 1.1], [497, 285, 1, 1.1], [198, 850, 1, 1.05], [858, 447, 1, 1], [616, 1118, 1, 1]];
  for (const [x, y, lit, big] of named) seat(x, y, lit, big);
  const westOK = (x, y) => { const wx = wallX(y); if (wx === null) { if (y < 384 && x < 990) return true; return false; } if (x > wx - 28) return false; const sy = slY(x); if (sy !== null && y > sy - 14) return false; return true; };
  const cityKeep = [...WEST.map((m) => [m[1], m[2], m[3] * 1.6]), [616, 714, 30], [730, 580, 10], [800, 880, 30], [352, 500, 18]];
  let tries = 0; const TOTAL = 72, DEAD = 16; const all = [];
  while (seatAt.length + all.length < TOTAL && tries < 40000) { tries++; const x = 50 + rnd() * 940, y = 150 + rnd() * 1000; if (!westOK(x, y) || !isDry(x, y)) continue; if (cityKeep.some(([cx, cy, r]) => Math.hypot(x - cx, y - cy) < r)) continue; const ci = cellAt(x, y); if (C.h[ci] > 70 || C.biome[ci] === 11) continue; if ([...seatAt, ...all].some(([sx, sy]) => Math.hypot(sx - x, sy - y) < 40)) continue; all.push([x, y]); }
  all.forEach(([x, y], k) => seat(x, y, k >= DEAD, 1));
  window.__stSeats = seatInfo;
  log.push('高座 ' + seatAt.length + '（空 ' + Math.min(DEAD, all.length) + '）');

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
  const darkRoad = (pts) => { const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#e9e0d0', 'stroke-width': 1.3, opacity: 0.6 }, roads); mk('path', { d, fill: 'none', stroke: '#3a2a26', 'stroke-width': 0.7, 'stroke-dasharray': '1.2 1.6' }, roads); };
  darkRoad([[352, 496], [392, 560], [440, 630], [500, 690], [560, 716], [640, 700], [720, 690], [800, 690], [890, 688]]);
  darkRoad([[500, 690], [490, 780], [470, 860], [440, 920], [410, 958]]);

  // ---- 天上的、发光的 ----
  const mg = mk('g', { id: 'stMagic' }, null);
  vb.insertBefore(mg, document.getElementById('labels'));
  // 北辰塔：那一夜没掉，歪着悬在峭壁上，塔顶那盏灯一直亮着，斜斜地照着湾口
  { const x = 374, y = 196; mk('path', { d: `M${x},${y - 9} L${x - 70},${y + 30}`, stroke: '#fff7d6', 'stroke-width': 5, opacity: 0.16, filter: 'url(#stBlur)' }, mg); const g = mk('g', { transform: `rotate(-24 ${x} ${y})` }, mg); mk('path', { d: `M${x - 1.6},${y + 1} L${x - 0.6},${y - 10} L${x + 0.6},${y - 10} L${x + 1.6},${y + 1} Z`, fill: '#f4f1ea', stroke: '#3c3a44', 'stroke-width': 0.35, filter: 'url(#stShadow)' }, g); mk('circle', { cx: x, cy: y - 10.5, r: 3.4, fill: 'url(#stSilver)' }, g); window.__stHide.push([x, y, 6]); }
  // 寒天之钉
  { const lg = mk('linearGradient', { id: 'stCrystal', x1: 0, y1: 0, x2: 1, y2: 0 }, pdefs); mk('stop', { offset: '0', 'stop-color': '#9fd0ff' }, lg); mk('stop', { offset: '0.45', 'stop-color': '#eef8ff' }, lg); mk('stop', { offset: '1', 'stop-color': '#5d8fd6' }, lg); mk('ellipse', { cx: 1232, cy: 116, rx: 46, ry: 26, fill: 'url(#stBlue)', opacity: 0.55 }, mg); for (let k = 0; k < 30; k++) { const a = rnd() * Math.PI * 2, d = Math.sqrt(rnd()) * 32; const cx = 1232 + Math.cos(a) * d * 1.3, cy = 114 + Math.sin(a) * d * 0.7; const h = 6 + rnd() * 14, w = 1.1 + rnd() * 1.2, lean = (rnd() - 0.5) * 2.6; mk('path', { d: `M${cx - w},${cy} L${cx + lean},${cy - h} L${cx + w},${cy} L${cx},${cy + w * 0.6} Z`, fill: 'url(#stCrystal)', stroke: '#3f6aa8', 'stroke-width': 0.3 }, mg); } }
  // 灰岩坡上的大驿：坡上架着魔晶炮阵
  { const x = 1122, y = 862; for (const dx of [-3.2, 0, 3.2]) { mk('path', { d: `M${x + dx - 0.6},${y} L${x + dx + 1.4},${y - 3.6}`, stroke: '#3c3646', 'stroke-width': 1.1, 'stroke-linecap': 'round' }, mg); mk('circle', { cx: x + dx + 1.5, cy: y - 3.8, r: 2.2, fill: 'url(#stViolet)' }, mg); } }
  // 晨星岭顶的烽塔、红刺坡上那一串海兽油的灯、冰原上的石屋、不生火的屋子、北风口的哨、插鳞石
  mk('circle', { cx: 1276, cy: 934, r: 4.5, fill: 'url(#stEmber)' }, mg);
  for (let k = 0; k < 6; k++) mk('circle', { cx: 862 + k * 6, cy: 1030 + Math.sin(k) * 2, r: 2.6, fill: 'url(#stAmber)', opacity: 0.9 }, mg);
  for (const [dx, dy] of [[-3, 0], [0, -2], [3, 1]]) mk('rect', { x: 968 + dx - 0.9, y: 392 + dy - 0.9, width: 1.8, height: 1.8, fill: '#e6e2da', stroke: '#4b4f57', 'stroke-width': 0.3 }, mg);
  mk('rect', { x: 1098.8, y: 348.8, width: 2.4, height: 2.4, fill: '#f6f8ff', stroke: '#6b7b98', 'stroke-width': 0.35 }, mg);
  mk('path', { d: 'M902,248 l-1.2,4 h2.4 Z', fill: '#e6e2da', stroke: '#4b4f57', 'stroke-width': 0.35 }, mg);
  mk('path', { d: 'M1600,198 l-1,-5 l1.6,-1 l1,5.6 Z', fill: '#c9b48a', stroke: '#5b4a33', 'stroke-width': 0.35 }, mg);
  // 潮歌群岛：银帆外海上一串唱航路的岛
  { let n = 0; for (const [x, y, r] of [[2128, 772, 3.2], [2142, 786, 2.4], [2150, 802, 3.4], [2138, 818, 2.2], [2156, 832, 2.8]]) { if (isDry(x, y)) continue; mk('circle', { cx: x, cy: y, r: r + 5, fill: 'url(#stCyan)', opacity: 0.6 }, mg); mk('path', { d: wob(x, y, r, n, 2), fill: '#e8e2cf', stroke: '#3c5560', 'stroke-width': 0.4 }, mg); n++; } log.push('潮歌的岛 ' + n); }

  // 罗盘、比例尺照 Azgaar 自己的
  { const b = document.querySelector('#mapLayers [data-layer=compass]'); if (b && b.classList.contains('buttonoff')) { b.click(); await sleep(700); } }

  // ---- 地名 ----
  if (!document.getElementById('pFont')) { const l = document.createElement('link'); l.id = 'pFont'; l.rel = 'stylesheet'; l.href = 'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700;900&display=swap'; document.head.appendChild(l); }
  const lab = mk('g', { id: 'stLabels', 'font-family': '"Noto Serif SC", serif', 'text-anchor': 'middle', 'paint-order': 'stroke', 'stroke-linejoin': 'round' }, vb);
  const T1 = (s, x, y, fs, o = {}) => { const e = mk('text', Object.assign({ x, y, 'font-size': fs, 'font-weight': 900, fill: '#2c261f', stroke: '#f6f0e2', 'stroke-width': fs * 0.2, 'letter-spacing': fs * 0.1 }, o), lab); e.textContent = s; return e; };
  const region = (s, x, y, fs, o = {}) => T1(s, x, y, fs, Object.assign({ 'font-weight': 500, fill: '#5b5245', stroke: '#f3eee2', 'stroke-width': fs * 0.16, 'letter-spacing': fs * 0.45, opacity: 0.9 }, o));
  const sea = (s, x, y, fs, o = {}) => T1(s, x, y, fs, Object.assign({ 'font-weight': 500, fill: '#2d5f73', stroke: '#d9eef3', 'stroke-width': fs * 0.12, 'letter-spacing': fs * 0.6, opacity: 0.85 }, o));
  const magic = (s, x, y, fs, o = {}) => T1(s, x, y, fs, Object.assign({ 'font-weight': 700, fill: '#3a3a52', stroke: '#f6f0e2', 'stroke-width': fs * 0.2, 'letter-spacing': fs * 0.08 }, o));
  T1('西 陆', 520, 560, 34, { 'font-weight': 900, fill: '#3b2f2a', stroke: '#f3eee2', 'stroke-width': 3, 'letter-spacing': 16, opacity: 0.35 });
  T1('东 陆', 1660, 640, 34, { 'font-weight': 900, fill: '#3b3528', stroke: '#f3eee2', 'stroke-width': 3, 'letter-spacing': 16, opacity: 0.35 });
  T1('晨 曦 帝 国', 1560, 690, 13, { 'font-weight': 700, fill: '#6b5532', opacity: 0.75, 'letter-spacing': 5 });
  for (const [s, x, y] of [['白鸢王国', 1408, 900], ['金穗王国', 1610, 890], ['湖星王国', 1900, 412], ['公国岭', 1700, 742]]) region(s, x, y, 9.5, { 'font-weight': 700, fill: '#6b5532', opacity: 0.75 });
  for (const [s, x, y, fs] of [['西海', 110, 640, 24], ['北海', 470, 58, 20], ['冰海', 1350, 74, 16], ['南冰海', 1080, 1328, 18], ['银帆外海', 2150, 690, 11]]) sea(s, x, y, fs);
  sea('盐 海', 360, 1030, 14, { fill: '#7a2f28', stroke: '#f3e1dc' });
  T1('老滩', 138, 1134, 5.5, { 'font-weight': 700, 'stroke-width': 1, fill: '#7a2f28' });
  T1('盐沼', 330, (window.__saltMarsh ? window.__saltMarsh[1] : 1200) + 9, 5.5, { 'font-weight': 700, 'stroke-width': 1, fill: '#3f5a52' });
  T1('盐海门', 168, 1214, 7, { 'font-weight': 700, fill: '#7a2f28', 'stroke-width': 1.4 });
  for (const [s, x, y, fs] of [['黑穗原', 352, 528, 10], ['万角原', 540, 590, 10], ['老谷', 512, 750, 9], ['黑石高地', 640, 628, 9], ['环山', 690, 822, 8.5], ['赤原', 800, 910, 10], ['雷暴荒地', 688, 1098, 8], ['冰原', 960, 420, 10], ['化圣雪原', 990, 270, 15], ['月银原', 905, 146, 9.5], ['北境', 1138, 448, 9], ['曜冠山', 1300, 330, 11], ['龙眠天脊', 1760, 140, 12], ['翠冠林海', 1868, 304, 14], ['风铃高原', 1696, 574, 11], ['白石平原', 1330, 812, 12], ['花谷', 1822, 1000, 9], ['蜜酒丘陵', 1880, 1046, 9], ['神渡盆地', 1112, 640, 9], ['星湖', 1896, 520, 9]]) region(s, x, y, fs);
  T1('死 域', 1150, 1170, 26, { 'font-weight': 900, fill: '#3e3a37', stroke: '#e8e3da', 'stroke-width': 2.4, 'letter-spacing': 18, opacity: 0.72 });
  for (const [s, x, y, r] of [['南 界', 742, 1104, -36], ['南 界', 1262, 1028, 4]]) T1(s, x, y, 8.5, { 'font-weight': 700, fill: '#8a2f28', stroke: '#f6eee6', 'stroke-width': 1.8, 'letter-spacing': 3, transform: `rotate(${r} ${x} ${y})` });
  region('落星洼', 1330, 1112, 10, { fill: '#5b4f43' });
  { const e = T1('白石长垒', 1060, 560, 11, { 'font-weight': 900, fill: '#3a3944', stroke: '#fbf8f0', 'stroke-width': 2.4, 'letter-spacing': 6, style: 'writing-mode: vertical-rl' }); }
  { const e = T1('星纱轨', 1084, 860, 8, { 'font-weight': 700, fill: '#4b3f7a', stroke: '#f6f3fb', 'stroke-width': 1.6, 'letter-spacing': 3, style: 'writing-mode: vertical-rl' }); }
  for (const [s, x, y] of [['北段', 1004, 509], ['中段', 966, 708], ['南段', 952, 900]]) T1(s, x, y, 7, { 'font-weight': 700, fill: '#3a3944', 'stroke-width': 1.4 });
  T1('水门', 1042, 762, 7, { 'font-weight': 700, fill: '#1f4f69', 'stroke-width': 1.4 });
  T1('盾碑', 926, 968, 6.5, { 'font-weight': 700, fill: '#3a3944', 'stroke-width': 1.3 });
  T1('四十七骑门', 1072, 446, 6, { 'font-weight': 700, fill: '#3a3944', 'stroke-width': 1.2 });
  const cityLabel = (s, x, y, R, fs, o = {}) => T1(s, x, y + R * 1.12 + fs * 0.95, fs, o);
  for (const [s, x, y, R, fs] of [['金鸢城', 1518, 742, 22, 15], ['星冠圣城', 1386, 560, 15, 11], ['熔铁炉心', 1562, 1106, 14, 10], ['白冠城', 1186, 756, 9, 8], ['星湖城', 1952, 412, 0, 8.5], ['白鸢王城', 1408, 868, 8.5, 7.5], ['金穗的仓', 1606, 854, 8.5, 7.5], ['银帆', 2069.8, 747.3, 7, 8], ['翠冠王庭', 2068, 308, 8, 8]]) cityLabel(s, x, y, R, fs);
  for (const [s, x, y, R, fs] of [['宴城', 682, 435.4, 9, 8.5], ['钟城', 374, 658, 9, 8.5], ['熔原', 528, 980, 9, 8.5], ['灰营', 902, 686, 8, 8], ['雾湖', 497, 302, 8, 8], ['潮门港', 198, 868, 7.5, 8], ['山口里的营', 858, 462, 6, 7], ['锻营', 616, 1134, 6, 7.5]]) cityLabel(s, x, y, R, fs, { fill: '#3a2420', stroke: '#efe6dc' });
  for (const [s, x, y] of [['苇岸城', 1540, 810], ['白鹿书堡', 1980, 571], ['贾曼尼', 1305, 397], ['对炉街', 1490, 1087], ['誓桥', 1474, 600], ['粮镇', 1650, 880], ['粮棚镇', 1556, 788], ['白鹿驿', 1738, 614], ['崖下的驿', 1760, 698], ['穴镇', 1892, 966], ['苦泉', 1180, 1012], ['晨曦岭', 1150, 962], ['长厅', 1110, 482], ['老岭', 1694, 726], ['金穗南坡', 1496, 1020], ['林市', 1820, 482], ['夜集', 1894, 695], ['灰岩坡', 1122, 880], ['晨星岭', 1276, 950], ['霜渡', 1080, 537], ['天脊北路的最后一站', 1386, 236]]) T1(s, x, y + 4, 5.5, { 'font-weight': 700, 'stroke-width': 1 });
  for (const [s, x, y] of [['黑石湾', 154, 740], ['断丘上的垒', 814, 866], ['荒丘', 616, 908], ['仓村', 410, 592], ['红刺坡', 878, 1046], ['鸦岭（空城）', 730, 594]]) T1(s, x, y + 4, 5.5, { 'font-weight': 700, 'stroke-width': 1, fill: '#3a2420' });
  for (const [s, x, y, fs] of [['穹都废墟', 616, 754, 9], ['旧神渡', 1100, 696, 7]]) T1(s, x, y, fs, { 'font-weight': 700, fill: '#4a4450' });
  for (const [s, x, y, fs] of [['星环', 1364, 428, 7.5], ['北辰塔', 380, 214, 7.5], ['寒天之钉', 1232, 146, 8], ['七座营垒', 214, 1074, 6.5], ['红滩链', 330, 1110, 6.5], ['潮歌群岛', 2150, 852, 7]]) magic(s, x, y, fs);
  // 题签
  { const g = mk('g', { id: 'stTitle' }, lab); mk('rect', { x: 1560, y: 1210, width: 470, height: 140, rx: 6, fill: '#f3ecdc', stroke: '#6b5532', 'stroke-width': 1.4, opacity: 0.94 }, g); mk('rect', { x: 1566, y: 1216, width: 458, height: 128, rx: 4, fill: 'none', stroke: '#6b5532', 'stroke-width': 0.6 }, g);
    const t1 = mk('text', { x: 1795, y: 1250, 'font-size': 26, 'font-weight': 900, fill: '#3a2f22', 'letter-spacing': 6 }, g); t1.textContent = '奥尔德兰 · 纷争纪';
    const t2 = mk('text', { x: 1795, y: 1276, 'font-size': 14, 'font-weight': 500, fill: '#5b4a33', 'letter-spacing': 2 }, g); t2.textContent = '炮的年月 · 约三千六百年 · 墙后的星纱轨刚通车';
    const t3 = mk('text', { x: 1795, y: 1296, 'font-size': 10, 'font-weight': 500, fill: '#5b4a33', 'letter-spacing': 1 }, g); t3.textContent = '白线是长垒，紫线是星纱轨，黑台是高座（亮着的有主，灰的空了）';
    const km = 19, x0 = 1690, y0 = 1326, seg = 1000 / km; for (let k = 0; k < 4; k++) mk('rect', { x: x0 + k * seg, y: y0, width: seg, height: 4, fill: k % 2 ? '#f3ecdc' : '#3a2f22', stroke: '#3a2f22', 'stroke-width': 0.6 }, g);
    for (let k = 0; k <= 4; k++) { const tt = mk('text', { x: x0 + k * seg, y: y0 - 4, 'font-size': 10, 'font-weight': 500, fill: '#3a2f22', 'stroke-width': 0 }, g); tt.textContent = k === 4 ? '4000 公里' : String(k * 1000); }
    const sb = document.getElementById('scaleBar'); if (sb) sb.style.display = 'none'; }
  try { await document.fonts.load('900 20px "Noto Serif SC"', '奥尔德兰纷争纪西陆东陆金鸢城白石长垒死域'); await document.fonts.load('500 20px "Noto Serif SC"', '西海南冰海盐海'); await sleep(1500); } catch (e) { log.push('字体 ' + e); }
  window.__stHideIcons = () => { let n = 0; for (const [x, y, r] of window.__stHide) { for (const u of document.querySelectorAll('#terrain use')) { if (u.style.display === 'none') continue; const ux = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2, uy = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2; if ((ux - x) ** 2 + (uy - y) ** 2 <= r * r) { u.style.display = 'none'; n++; } } } return n; };
  log.push('城下藏符号 ' + window.__stHideIcons());
  return log.join('；');
})();
