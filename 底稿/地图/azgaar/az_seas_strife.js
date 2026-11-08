// 纷争纪的海与三河（照 az_seas_moon.js 改）：镰月海这一纪叫镰刀湾（补卷_30 峭壁西边的镰刀湾：弯得像镰刀，刃口朝外海，北辰塔的灯照着湾口），珠湾叫潮门的湾，北辰湾照旧；
//   三河在墙下水门汇流（中段墙下的水门，往后的中央水门），汇成的那一条贴着墙东往南流，流进死域就断了，往南只剩一道旧河床
//   在碧湾、盐海、死域那几步之后跑
// 原注：月银纪的海与三河（海与水路_方向稿第五节）：在 az_reset.sh、az_biwan_run.js、az_nanyuan.js 之后、az_salvis.js 以前跑。
//   那时候已经有的：镰月海（衔枝纪挖的，北角镰月海门，东北的海盆），珠湾（往后的深蓝海湾，约2800年沉下去以后深了），北辰湾，长船湾
//   还没有的：双月内海（南原）、白碑湾、两道海门里的双月海门、两条运河
//   三河：凛河、烬河、吟河在神渡城当中汇流，汇成的那一条往南流过南原，顺着往后双月海门那一道旧河道入海
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const C = pack.cells, R = pack.rivers;
  const vb = document.getElementById('viewbox');
  const defs = document.getElementById('featurePaths').closest('defs');
  const fp = document.getElementById('featurePaths');
  for (const id of ['fseaDefs', 'fseaWater', 'fseaProbes', 'fseaLabels', 'fseaRivers']) { const o = document.getElementById(id); if (o) o.remove(); }
  const sd = mk('g', { id: 'fseaDefs' }, defs);
  const log = [];
  let seed = 41; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const smooth = (pts) => { let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2; const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6]; d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`; } return d; };
  const riverPts = (i) => { const rv = R.find((r) => r && r.i === i); const pts = []; for (const c of rv.cells || []) if (c >= 0 && C.p[c]) pts.push([C.p[c][0], C.p[c][1]]); const m = C.p[rv.mouth]; if (m && (!pts.length || pts[pts.length - 1][0] !== m[0])) pts.push([m[0], m[1]]); return pts; };
  const gulfPoly = (pts, w0, w1) => { const ws = pts.map((_, i) => w0 + (w1 - w0) * i / (pts.length - 1)); return gulfPolyW(pts, ws); };
  const gulfPolyW = (pts, ws) => { const L = [], Rr = []; const n = pts.length; for (let i = 0; i < n; i++) { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)]; let dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l; const w = ws[i] * (1 + 0.1 * Math.sin(i * 1.7 + 1)); L.push([pts[i][0] - dy * w, pts[i][1] + dx * w]); Rr.push([pts[i][0] + dy * w * (0.9 + 0.2 * rnd()), pts[i][1] - dx * w * (0.9 + 0.2 * rnd())]); } return smooth(L) + ' L' + smooth(Rr.reverse()).slice(1) + ' Z'; };
  const blob = (cx, cy, rx, ry, rot, ph) => { const pts = []; for (let a = 0; a < 360; a += 8) { const t2 = a * Math.PI / 180, k = 1 + 0.07 * Math.sin(3 * t2 + ph) + 0.05 * Math.sin(5 * t2 + ph * 2); const x0 = Math.cos(t2) * rx * k, y0 = Math.sin(t2) * ry * k, c = Math.cos(rot), sn = Math.sin(rot); pts.push([cx + x0 * c - y0 * sn, cy + x0 * sn + y0 * c]); } pts.push(pts[0]); return smooth(pts) + ' Z'; };
  const shapes = [];
  const add = (id, d, kind = 'fill', w = 0) => { mk('path', { id, d }, fp); shapes.push({ id, d, kind, w }); };
  // 镰月海：跟 1001 年那一版同一个形（衔枝纪挖的，几纪都在）
  { const A = [266, 334], B = [336, 474], Cc = [192, 628];
    const D = 2 * (A[0] * (B[1] - Cc[1]) + B[0] * (Cc[1] - A[1]) + Cc[0] * (A[1] - B[1]));
    const ux = ((A[0] ** 2 + A[1] ** 2) * (B[1] - Cc[1]) + (B[0] ** 2 + B[1] ** 2) * (Cc[1] - A[1]) + (Cc[0] ** 2 + Cc[1] ** 2) * (A[1] - B[1])) / D;
    const uy = ((A[0] ** 2 + A[1] ** 2) * (Cc[0] - B[0]) + (B[0] ** 2 + B[1] ** 2) * (A[0] - Cc[0]) + (Cc[0] ** 2 + Cc[1] ** 2) * (B[0] - A[0])) / D;
    const r = Math.hypot(A[0] - ux, A[1] - uy);
    let a0 = Math.atan2(A[1] - uy, A[0] - ux), a1 = Math.atan2(Cc[1] - uy, Cc[0] - ux); if (a1 < a0) a1 += Math.PI * 2;
    const outer = [], inner = []; const N = 48; seed = 41;
    for (let k = 0; k <= N; k++) { const s2 = k / N, ang = a0 + (a1 - a0) * s2; const t = 112 * Math.sin(Math.PI * s2) ** 0.6 * (1 + 0.06 * Math.sin(k * 1.3)); const ro = r * (1 + 0.012 * Math.sin(k * 2.1)); outer.push([ux + Math.cos(ang) * ro, uy + Math.sin(ang) * ro]); inner.push([ux + Math.cos(ang) * (ro - t), uy + Math.sin(ang) * (ro - t)]); }
    add('fsea_lianyue', smooth(outer) + ' L' + smooth(inner.reverse()).slice(1) + ' Z');
    add('fsea_lianyue_gate', smooth([[A[0] + 4, A[1] + 6], [A[0] - 10, A[1] - 2], [236, 318], [214, 312]]), 'stroke', 9);
    add('fsea_lianyue_e', blob(388, 420, 82, 46, -0.12, 1.3)); }
  add('fsea_zhuwan', gulfPolyW([[104, 852], [146, 846], [182, 834], [220, 818], [258, 808], [292, 808], [326, 814], [360, 816], [392, 810], [418, 802], [438, 798]], [24, 21, 24, 32, 38, 40, 38, 32, 22, 10, 2.5]));
  add('fsea_beichen', gulfPoly([[368, 112], [370, 132], [372, 152], [373, 170], [374, 186]], 30, 10));
  add('fsea_changchuan', gulfPoly([[606, 112], [609, 140], [613, 172], [619, 206], [626, 242], [630, 278], [628, 312], [624, 334]], 44, 3));
  const useShape = (s, parent, attrs) => { const a = Object.assign({ href: '#' + s.id }, attrs); if (s.kind === 'stroke') { a.fill = 'none'; a.stroke = attrs.fill; a['stroke-width'] = s.w; a['stroke-linecap'] = 'round'; } return mk('use', a, parent); };
  const land = document.getElementById('land'), water = document.getElementById('water');
  for (const s of shapes) { useShape(s, land, { fill: 'black' }); useShape(s, water, { fill: 'white' }); }
  const box = { maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 2200, height: 1400 };
  const noNew = mk('mask', Object.assign({ id: 'fseaNoNew' }, box), sd); mk('rect', { x: 0, y: 0, width: 2200, height: 1400, fill: 'white' }, noNew); for (const s of shapes) useShape(s, noNew, { fill: 'black' });
  if (document.getElementById('saltsea_blob')) mk('use', { href: '#saltsea_blob', fill: 'black' }, noNew);
  const landSide = mk('mask', Object.assign({ id: 'fseaLandSide' }, box), sd); mk('use', { href: '#feature_2', fill: 'white' }, landSide); for (const s of shapes) useShape(s, landSide, { fill: 'black' });
  const seaIsland = document.getElementById('sea_island');
  for (const u of seaIsland.querySelectorAll(':scope > use')) { const m = u.getAttribute('mask'); if (!m) u.setAttribute('mask', 'url(#fseaNoNew)'); }
  // 已经套了碧湾那一道遮罩的岸线，再包一层
  { const g = mk('g', { mask: 'url(#fseaNoNew)' }, seaIsland); for (const u of [...seaIsland.querySelectorAll(':scope > use[mask="url(#nobay)"]')]) g.appendChild(u); }
  const coast = mk('g', { mask: 'url(#fseaLandSide)' }, seaIsland);
  for (const s of shapes) { if (s.kind === 'stroke') mk('use', { href: '#' + s.id, fill: 'none', 'stroke-width': s.w + 1.4, 'stroke-linecap': 'round' }, coast); else mk('use', { href: '#' + s.id, fill: 'none' }, coast); }
  const ol = document.getElementById('oceanLayers');
  const gw = mk('g', { id: 'fseaWater' }, ol);
  const gf = mk('g', { opacity: 0.22 }, gw); for (const s of shapes) useShape(s, gf, { fill: '#ecf2f9' });
  const rivers = document.getElementById('rivers');
  rivers.setAttribute('mask', 'url(#fseaNoNew)');
  const r433 = document.getElementById('river433'); if (r433) r433.style.display = 'none';
  // 新水面里的地形符号藏掉（截图以前再跑一回）
  const probes = mk('g', { id: 'fseaProbes', opacity: 0, 'pointer-events': 'none' }, vb);
  for (const s of shapes) mk('path', s.kind === 'stroke' ? { d: s.d, fill: 'none', stroke: '#000', 'stroke-width': s.w + 2, 'data-k': 's' } : { d: s.d, fill: '#000', 'data-k': 'f' }, probes);
  window.__fseaHideIcons = () => { const pt = document.getElementById('map').createSVGPoint(); const els = [...document.querySelectorAll('#fseaProbes path')]; let n = 0; for (const u of document.querySelectorAll('#terrain use')) { if (u.style.display === 'none') continue; pt.x = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2; pt.y = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2; for (const e of els) { if (e.getAttribute('data-k') === 's' ? e.isPointInStroke(pt) : e.isPointInFill(pt)) { u.style.display = 'none'; n++; break; } } } return n; };
  log.push('新水面里藏符号 ' + window.__fseaHideIcons());
  // 三河在神渡城当中汇流，汇成的那一条往南过南原，顺着往后双月海门那道旧河道入海
  const rg = mk('g', { id: 'fseaRivers', mask: 'url(#fseaNoNew)' }, null); rivers.parentNode.insertBefore(rg, rivers.nextSibling);
  const meander = (pts, amp) => { const el = mk('path', { d: smooth(pts), fill: 'none' }, rg); const L = el.getTotalLength(); const out = []; const ph = rnd() * 6; for (let s0 = 0; s0 <= L; s0 += 5) { const p = el.getPointAtLength(s0), q = el.getPointAtLength(Math.min(L, s0 + 1)); let dx = q.x - p.x, dy = q.y - p.y; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l; const e = (s0 < 8 || s0 > L - 8) ? 0 : amp * (Math.sin(s0 / 9 + ph) + 0.5 * Math.sin(s0 / 4.1 + ph * 2) + 0.4 * (rnd() - 0.5)); out.push([p.x - dy * e, p.y + dx * e]); } el.remove(); return out; };
  const river = (pts0, w0, w1, amp = 2.4) => { const pts = meander(pts0, amp); const el = mk('path', { d: smooth(pts), fill: 'none' }, rg); const L = el.getTotalLength(); const n = Math.max(6, Math.round(L / 6)); let prev = el.getPointAtLength(0); for (let k = 1; k <= n; k++) { const p = el.getPointAtLength(L * k / n); mk('line', { x1: prev.x, y1: prev.y, x2: p.x, y2: p.y, stroke: '#2e89c2', 'stroke-width': w0 + (w1 - w0) * k / n, 'stroke-linecap': 'round' }, rg); prev = p; } el.remove(); };
  river([[1094, 362], [1086, 420], [1097, 498], [1090, 580], [1076, 640], [1066, 694], [1042, 732], [1024, 749]], 0.8, 2.3);
  river([[770, 862], [790, 830], [812, 808], [836, 798], [860, 782], [880, 770], [930, 762], [980, 756], [1018, 751]], 1.0, 2.5);
  river([[1250, 598], [1214, 618], [1176, 640], [1140, 662], [1100, 690], [1062, 718], [1030, 746]], 0.8, 1.9);
  const FOPT = window.__fseaOpt || {};
  if (FOPT.river === 'lake') river([[1024, 754], [1033, 800], [1046, 856], [1070, 912], [1110, 952], [1150, 980], [1190, 1010], [1220, 1038], [1240, 1056]], 2.6, 3.3);
  else river([[1024, 754], [1033, 800], [1046, 856], [1070, 912], [1110, 952], [1146, 984], [1172, 1010]], 2.6, 3.1);
  // 进了死域就断了：往南只剩一道旧河床，干的，通到落星洼的坑沿
  if (FOPT.river !== 'lake') { const d = smooth(meander([[1172, 1010], [1196, 1030], [1218, 1046], [1240, 1060]], 1.4)); mk('path', { d, fill: 'none', stroke: '#e9e1cf', 'stroke-width': 2.6, opacity: 0.5 }, rg); mk('path', { d, fill: 'none', stroke: '#7d7466', 'stroke-width': 1.3, 'stroke-dasharray': '2.2 2.2', opacity: 0.85 }, rg); }
  // 灰河分两条（11-08）：炉城底下流出来的断崖下的河往西流进落星洼（月银纪那时候它往南入海，就是 Azgaar 原来那一条 32，纷争纪洼打出来以后改道），
  //   墙西的灰河从灰高原当中往西南，过渡口，到断岭北头接上顺着断岭往南的那一条（74）
  for (const id of ['river32', 'river44']) { const r = document.getElementById(id); if (r) r.style.display = 'none'; }
  river([[1556, 1125], [1549, 1131], [1535, 1142], [1515, 1143], [1498, 1147], [1478, 1150], [1458, 1146]], 0.9, 1.8, 1.4);
  if (FOPT.river === 'lake') river([[1458, 1146], [1443, 1139], [1427, 1131]], 1.8, 2.1, 0.8);
  else { const d = smooth([[1458, 1146], [1443, 1139], [1427, 1131]]); mk('path', { d, fill: 'none', stroke: '#e9e1cf', 'stroke-width': 2.2, opacity: 0.5 }, rg); mk('path', { d, fill: 'none', stroke: '#7d7466', 'stroke-width': 1.1, 'stroke-dasharray': '2.2 2.2', opacity: 0.85 }, rg); }
  river([[775, 912], [762, 948], [746, 984], [726, 1014], [708, 1034], [688, 1050]], 0.7, 1.5, 1.6);
  { const fh = window.__fseaHideIcons; window.__fseaHideIcons = () => { for (const id of ['river32', 'river44']) { const r = document.getElementById(id); if (r) r.style.display = 'none'; } return fh(); }; }
  // 地名（照萨尔维斯末年那一套的字体）
  const lab = mk('g', { id: 'fseaLabels', 'font-family': '"Noto Serif SC", serif', 'text-anchor': 'middle', 'paint-order': 'stroke', 'stroke-linejoin': 'round' }, vb);
  const T = (s, x, y, fs, o = {}) => { const e = mk('text', Object.assign({ x, y, 'font-size': fs, 'font-weight': 700, fill: '#2c261f', stroke: '#f6f0e2', 'stroke-width': fs * 0.2, 'letter-spacing': fs * 0.08 }, o), lab); e.textContent = s; return e; };
  const sea = (s, x, y, fs) => T(s, x, y, fs, { 'font-weight': 500, fill: '#24566b', stroke: '#dcedf2', 'stroke-width': fs * 0.14, 'letter-spacing': fs * 0.45, opacity: 0.9 });
  const wl = (s, x, y, fs, rot = 0) => T(s, x, y, fs, { fill: '#1f4f69', stroke: '#eef6f9', 'stroke-width': fs * 0.22, transform: rot ? `rotate(${rot} ${x} ${y})` : '' });
  for (const [s, x, y, fs] of [['镰 刀 湾', 318, 470, 14], [FOPT.bay || '潮门的湾', 300, 813, 8.5], ['北辰湾', 404, 140, 7.5], ['长船湾', 650, 232, 8]]) sea(s, x, y, fs);
  for (const [s, x, y, fs, r] of [['凛河', 1112, 470, 7, 80], ['烬河', 900, 790, 7, -12], ['吟河', 1190, 628, 7, -28], ['断崖下的河', 1506, 1134, 6, -8], ['灰河', 757, 962, 6.5, 64], ['三河', 1066, 868, 7.5, 64], ...(FOPT.river === 'lake' ? [] : [['旧河床', 1222, 1036, 6, 36]])]) wl(s, x, y, fs, r);
  return log.join('；');
})();
