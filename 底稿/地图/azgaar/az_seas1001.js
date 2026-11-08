// 1001 年的海与水路（试样）：在 az_reset.sh 摆好的图上跑。
//   内海通外洋：赤盐内海顺着它出海那条河（176）开一道赤盐海门，双月内海顺着出海那条河（568）开一道双月海门，两片湖都改成海
//   新切的海湾：西岸顺着黯月河往里切一道深蓝海湾（深潮蓝堡那七座港城的湾），北岸往里切一道北辰湾（黑翼天塔挂在湾头的崖上）
//   运河：黑耀运河（深蓝海湾湾头穿过环山的口子到烬灭之都），王道运河（金鸢城顺着王道往西到阿卡迪亚）
//   通内陆的水路：白碑水道（阿卡迪亚往南顺着河进双月内海），金鸢河（金鸢城往东进月潮内海），灰契河（墙西往东到中央水门）
//   航路：外洋沿岸、南海、内海和水路连成一张网
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const C = pack.cells, P = pack.vertices.p, R = pack.rivers;
  const vb = document.getElementById('viewbox');
  const defs = document.getElementById('featurePaths').closest('defs');
  for (const id of ['seaDefs', 'seaWater', 'seaCanals', 'seaLanes', 'seaLabels']) { const o = document.getElementById(id); if (o) o.remove(); }
  const sd = mk('g', { id: 'seaDefs' }, defs);
  const log = [];
  let seed = 41; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  // 平滑折线
  const smooth = (pts) => { if (pts.length < 3) return 'M' + pts.map((p) => p.map((v) => v.toFixed(1)).join(',')).join('L'); let d = `M${pts[0][0].toFixed(1)},${pts[0][1].toFixed(1)}`; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2; const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6], c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6]; d += ` C${c1[0].toFixed(1)},${c1[1].toFixed(1)} ${c2[0].toFixed(1)},${c2[1].toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`; } return d; };
  const riverPts = (i) => { const rv = R.find((r) => r && r.i === i); const pts = []; for (const c of rv.cells || []) if (c >= 0 && C.p[c]) pts.push([C.p[c][0], C.p[c][1]]); const m = C.p[rv.mouth]; if (m && (!pts.length || pts[pts.length - 1][0] !== m[0])) pts.push([m[0], m[1]]); return pts; };
  // 一道海湾：中线加每一点的半宽，左右各偏出去，带一点毛边
  const gulfPoly = (pts, w0, w1) => { const L = [], Rr = []; const n = pts.length; for (let i = 0; i < n; i++) { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)]; let dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l; const t = i / (n - 1), w = (w0 + (w1 - w0) * t) * (1 + 0.18 * Math.sin(i * 1.7 + 1) + 0.1 * (rnd() - 0.5)); L.push([pts[i][0] - dy * w, pts[i][1] + dx * w]); Rr.push([pts[i][0] + dy * w * (0.85 + 0.3 * rnd()), pts[i][1] - dx * w * (0.85 + 0.3 * rnd())]); } return smooth(L) + ' L' + smooth(Rr.reverse()).slice(1) + ' Z'; };
  const gulfPolyW = (pts, ws) => { const L = [], Rr = []; const n = pts.length; for (let i = 0; i < n; i++) { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)]; let dx = b[0] - a[0], dy = b[1] - a[1]; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l; const w = ws[i] * (1 + 0.1 * Math.sin(i * 1.7 + 1)); L.push([pts[i][0] - dy * w, pts[i][1] + dx * w]); Rr.push([pts[i][0] + dy * w * (0.9 + 0.2 * rnd()), pts[i][1] - dx * w * (0.9 + 0.2 * rnd())]); } return smooth(L) + ' L' + smooth(Rr.reverse()).slice(1) + ' Z'; };
  const lerpLine = (a, b, n) => { const out = []; for (let k = 0; k <= n; k++) out.push([a[0] + (b[0] - a[0]) * k / n + (k && k < n ? (rnd() - 0.5) * 4 : 0), a[1] + (b[1] - a[1]) * k / n + (k && k < n ? (rnd() - 0.5) * 4 : 0)]); return out; };

  // ---- 新的水面 ----
  const fp = document.getElementById('featurePaths');
  const shapes = [];
  // 两道海门：顺着出海的河，中线描粗
  const strait = (id, river, w) => { const pts = riverPts(river); const d = smooth(pts); mk('path', { id, d }, fp); shapes.push({ id, kind: 'stroke', w, d }); return pts; };
  strait('sea_chiyan', 176, 9);
  // 赤盐内海往北那一大片：纷争纪1088年盐原整片塌下去连上碧湾，往后一直是海（形照 build_strife_mid.sh 存的 盐海_纷争纪.path.txt，跑以前用 embed.py 塞进 SALT_D；不塞就照 Azgaar 原来的湖）
  { const d = 'SALT_D'; if (d.charAt(0) === 'M') { mk('path', { id: 'sea_chiyan_salt', d }, fp); shapes.push({ id: 'sea_chiyan_salt', kind: 'fill', d }); } }
  strait('sea_shuangyue', 568, 11);
  // 深蓝海湾：从西岸黯月河口往东，口子宽、往里窄，拐几道弯
  { const pts = [[104, 852], [146, 846], [182, 834], [220, 818], [258, 808], [292, 808], [326, 814], [360, 816], [392, 810], [418, 802], [438, 798]]; const d = gulfPolyW(pts, [24, 21, 24, 32, 38, 40, 38, 32, 22, 10, 2.5]); mk('path', { id: 'sea_shenlan', d }, fp); shapes.push({ id: 'sea_shenlan', kind: 'fill', d }); }
  // 北辰湾：北岸往南切到黑翼天塔的崖下
  { const pts = [[368, 112], [370, 132], [372, 152], [373, 170], [374, 186]]; const d = gulfPoly(pts, 30, 10); mk('path', { id: 'sea_beichen', d }, fp); shapes.push({ id: 'sea_beichen', kind: 'fill', d }); }
  // 镰月海：西岸往里一道月牙形的内海，两只角朝西，北角开一道口子出外海（镰月商港守着口子），东边鼓到饥渊枯祭原的岸下
  { const A = [266, 334], B = [336, 474], Cc = [192, 628];
    const D = 2 * (A[0] * (B[1] - Cc[1]) + B[0] * (Cc[1] - A[1]) + Cc[0] * (A[1] - B[1]));
    const ux = ((A[0] ** 2 + A[1] ** 2) * (B[1] - Cc[1]) + (B[0] ** 2 + B[1] ** 2) * (Cc[1] - A[1]) + (Cc[0] ** 2 + Cc[1] ** 2) * (A[1] - B[1])) / D;
    const uy = ((A[0] ** 2 + A[1] ** 2) * (Cc[0] - B[0]) + (B[0] ** 2 + B[1] ** 2) * (A[0] - Cc[0]) + (Cc[0] ** 2 + Cc[1] ** 2) * (B[0] - A[0])) / D;
    const r = Math.hypot(A[0] - ux, A[1] - uy);
    let a0 = Math.atan2(A[1] - uy, A[0] - ux), a1 = Math.atan2(Cc[1] - uy, Cc[0] - ux); if (a1 < a0) a1 += Math.PI * 2;
    const am = Math.atan2(B[1] - uy, B[0] - ux); let amm = am; while (amm < a0) amm += Math.PI * 2; if (amm > a1) { const t = a0; a0 = a1; a1 = t + Math.PI * 2; }
    const outer = [], inner = []; const N = 48;
    for (let k = 0; k <= N; k++) { const s2 = k / N, ang = a0 + (a1 - a0) * s2; const t = 112 * Math.sin(Math.PI * s2) ** 0.6 * (1 + 0.06 * Math.sin(k * 1.3)); const ro = r * (1 + 0.012 * Math.sin(k * 2.1)); outer.push([ux + Math.cos(ang) * ro, uy + Math.sin(ang) * ro]); inner.push([ux + Math.cos(ang) * (ro - t), uy + Math.sin(ang) * (ro - t)]); }
    const d = smooth(outer) + ' L' + smooth(inner.reverse()).slice(1) + ' Z';
    mk('path', { id: 'sea_lianyue', d }, fp); shapes.push({ id: 'sea_lianyue', kind: 'fill', d });
    const sd2 = smooth([[A[0] + 4, A[1] + 6], [A[0] - 10, A[1] - 2], [236, 318], [214, 312]]); mk('path', { id: 'sea_lianyue_gate', d: sd2 }, fp); shapes.push({ id: 'sea_lianyue_gate', kind: 'stroke', w: 9, d: sd2 });
    log.push('镰月海 圆心 ' + Math.round(ux) + ',' + Math.round(uy) + ' 半径 ' + Math.round(r));
    const blob = (cx, cy, rx, ry, rot, ph) => { const pts = []; for (let a = 0; a < 360; a += 8) { const t2 = a * Math.PI / 180, k = 1 + 0.07 * Math.sin(3 * t2 + ph) + 0.05 * Math.sin(5 * t2 + ph * 2); const x0 = Math.cos(t2) * rx * k, y0 = Math.sin(t2) * ry * k, c = Math.cos(rot), sn = Math.sin(rot); pts.push([cx + x0 * c - y0 * sn, cy + x0 * sn + y0 * c]); } pts.push(pts[0]); return smooth(pts) + ' Z'; };
    window.__blob = blob;
    const db = blob(388, 420, 82, 46, -0.12, 1.3); mk('path', { id: 'sea_lianyue_e', d: db }, fp); shapes.push({ id: 'sea_lianyue_e', kind: 'fill', d: db }); }
  // 双月内海往北伸一片：晨星公国岭和白鸢骑士城当中
  { const d = window.__blob(1338, 948, 52, 82, 0.05, 0.7); mk('path', { id: 'sea_shuangyue_n', d }, fp); shapes.push({ id: 'sea_shuangyue_n', kind: 'fill', d }); }
  // 长船湾：西陆北岸、魇镜幻都和血棘红园之间往南切一道
  { const pts = [[606, 112], [609, 140], [613, 172], [619, 206], [626, 242], [630, 278], [628, 312], [624, 334]]; const d = gulfPoly(pts, 44, 3); mk('path', { id: 'sea_changchuan', d }, fp); shapes.push({ id: 'sea_changchuan', kind: 'fill', d }); }
  // 白碑湾：白碑河口往北淹进去的一道湾（双月内海北岸往阿卡迪亚那个方向伸）
  { const pts = [[1244, 1052], [1228, 1020], [1204, 1000], [1178, 988], [1156, 980], [1140, 975]]; const d = gulfPoly(pts, 24, 2.5); mk('path', { id: 'sea_baibei', d }, fp); shapes.push({ id: 'sea_baibei', kind: 'fill', d }); }
  const useShape = (s, parent, attrs) => { const a = Object.assign({ href: '#' + s.id }, attrs); if (s.kind === 'stroke') { a.fill = 'none'; a.stroke = attrs.fill; a['stroke-width'] = s.w; a['stroke-linecap'] = 'round'; } return mk('use', a, parent); };
  const land = document.getElementById('land'), water = document.getElementById('water');
  for (const s of shapes) { useShape(s, land, { fill: 'black' }); useShape(s, water, { fill: 'white' }); }
  // 两片湖改成海：湖那一组里藏掉，海自己露出来
  for (const u of document.querySelectorAll('#lakes use')) { const h = u.getAttribute('href') || u.getAttribute('xlink:href'); if (h === '#feature_9' || h === '#feature_10') u.style.display = 'none'; }
  const box = { maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 2200, height: 1400 };
  const newWater = (m) => { for (const s of shapes) useShape(s, m, { fill: 'black' }); mk('use', { href: '#feature_9', fill: 'black' }, m); mk('use', { href: '#feature_10', fill: 'black' }, m); };
  const noNew = mk('mask', Object.assign({ id: 'seaNoNew' }, box), sd); mk('rect', { x: 0, y: 0, width: 2200, height: 1400, fill: 'white' }, noNew); newWater(noNew);
  const landSide = mk('mask', Object.assign({ id: 'seaLandSide' }, box), sd); mk('use', { href: '#feature_2', fill: 'white' }, landSide); newWater(landSide);
  // 原来的岸线在新水面里藏掉（海门口、湾口那一截），新岸照海岸线的样式描
  const seaIsland = document.getElementById('sea_island');
  for (const u of seaIsland.querySelectorAll('use')) u.setAttribute('mask', 'url(#seaNoNew)');
  const coast = mk('g', { mask: 'url(#seaLandSide)' }, seaIsland);
  for (const s of shapes) { if (s.kind === 'stroke') mk('use', { href: '#' + s.id, fill: 'none', 'stroke-width': s.w + 1.4, 'stroke-linecap': 'round' }, coast); else mk('use', { href: '#' + s.id, fill: 'none' }, coast); }
  mk('use', { href: '#feature_9', fill: 'none' }, coast); mk('use', { href: '#feature_10', fill: 'none' }, coast);
  // 海的浅色层：新水面里叠一层，近岸再叠几道
  const ol = document.getElementById('oceanLayers');
  const gw = mk('g', { id: 'seaWater' }, ol);
  const gf = mk('g', { opacity: 0.22 }, gw);
  for (const s of shapes) useShape(s, gf, { fill: '#ecf2f9' });
  mk('use', { href: '#feature_9', fill: '#ecf2f9' }, gf); mk('use', { href: '#feature_10', fill: '#ecf2f9' }, gf);
  for (const w of [4, 9, 15]) { mk('use', { href: '#feature_9', fill: 'none', stroke: '#ecf2f9', 'stroke-opacity': 0.14, 'stroke-width': w }, gw); mk('use', { href: '#feature_10', fill: 'none', stroke: '#ecf2f9', 'stroke-opacity': 0.14, 'stroke-width': w }, gw); }
  // 赤盐内海透一点红
  mk('use', { href: document.getElementById('sea_chiyan_salt') ? '#sea_chiyan_salt' : '#feature_10', fill: '#c96a5b', 'fill-opacity': 0.16 }, gw);
  // 新水面里的河和地形符号藏掉
  document.getElementById('rivers').setAttribute('mask', 'url(#seaNoNew)');
  for (const id of ['river176', 'river568', 'river433', 'river32', 'river44']) { const r = document.getElementById(id); if (r) r.style.display = 'none'; }
  const probes = mk('g', { id: 'seaProbes', opacity: 0, 'pointer-events': 'none' }, vb);
  for (const s of shapes) mk('path', s.kind === 'stroke' ? { d: s.d, fill: 'none', stroke: '#000', 'stroke-width': s.w + 2, 'data-k': 's' } : { d: s.d, fill: '#000', 'data-k': 'f' }, probes);
  mk('use', { href: '#feature_9', fill: '#000', 'data-k': 'u' }, probes); mk('use', { href: '#feature_10', fill: '#000', 'data-k': 'u' }, probes);
  window.__seaHideIcons = () => { const pt = document.getElementById('map').createSVGPoint(); const els = [...document.querySelectorAll('#seaProbes path')]; const lakes = [document.getElementById('feature_9'), document.getElementById('feature_10')]; let n = 0; for (const u of document.querySelectorAll('#terrain use')) { if (u.style.display === 'none') continue; pt.x = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2; pt.y = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2; let inside = lakes.some((e) => e.isPointInFill(pt)); if (!inside) for (const e of els) { if (e.getAttribute('data-k') === 's' ? e.isPointInStroke(pt) : e.isPointInFill(pt)) { inside = true; break; } } if (inside) { u.style.display = 'none'; n++; } } return n; };
  { const sh = window.__seaHideIcons; window.__seaHideIcons = () => { for (const id of ['river32', 'river44']) { const r = document.getElementById(id); if (r) r.style.display = 'none'; } return sh(); }; }
  log.push('新水面里藏符号 ' + window.__seaHideIcons());
  { const LM = [["阿卡迪亚大迷宫", 1100.0, 672.0], ["晨曦帝都·金鸢城", 1518.0, 742.0], ["星冠圣城", 1386.0, 560.0], ["原初之森·碧穹王庭", 2068.0, 308.0], ["熔铁炉心", 1562.0, 1106.0], ["轰鸣断崖", 1452.0, 1176.0], ["蜜酒丘陵与铃尾市集", 1879.9, 1024.8], ["龙眠天脊", 1760.0, 154.0], ["白碑长垒", 995.9, 826.0], ["烬灭之都", 616.0, 714.0], ["渊月长廊", 814.0, 700.0], ["苍焰角城", 528.0, 980.0], ["血棘红园", 682.0, 435.4], ["骸钟墓城", 374.0, 658.0], ["魇镜幻都", 497.0, 302.0], ["黑翼天塔", 374.0, 196.0], ["雷狱铁城", 616.0, 1134.0], ["深潮蓝堡", 198.0, 868.0], ["星坠冒险者学院", 1186.0, 756.0], ["星环魔导都市", 1364.0, 406.0], ["白鸢骑士城", 1408.0, 868.0], ["金穗王仓城", 1606.0, 854.0], ["银帆海港", 2069.8, 747.3], ["曜石审判庭", 1563.8, 644.4], ["蔷薇王都·露玫城", 1822.9, 981.5], ["月镜王都·银湖城", 1952.1, 443.5], ["风铃王都·高岚城", 1697.1, 518.7], ["白鹿书堡", 1979.8, 559.0], ["蔷薇铁卫城", 1760.0, 1106.0], ["雾铃驿城", 1760.0, 686.0], ["苍麦公国岭", 1496.0, 1008.0], ["银鹿公国岭", 1694.0, 714.0], ["晨星公国岭", 1276.0, 938.0], ["蓝湾公国岭", 2019.8, 865.3], ["渡鸦监塞", 858.0, 462.0], ["灰烬门关", 902.0, 686.0], ["断锋黑垒", 814.0, 854.0], ["赤棘烽垒", 880.0, 1036.0], ["镰月商港", 240.9, 278.6], ["黯潮军港", 154.0, 728.0], ["赤盐海门", 234.3, 1188.6], ["极光冰冠", 1210.0, 70.0], ["南冠寂塔", 1254.0, 1316.0], ["星镜大湖", 1914.0, 490.0], ["翠冠大湖", 2002.0, 365.1], ["双月内海", 1342.0, 1087.9], ["赤盐内海", 330.0, 1130.5], ["金鸢河", 1604.5, 788.6], ["白碑河", 1222.1, 1013.6], ["黯月河", 227.9, 800.5], ["熔铁灰河", 1553.9, 1124.8], ["曜冠山脉", 1320.0, 355.5], ["黑曜环山", 660.0, 812.0], ["风鸣高原", 1694.0, 586.9], ["雾镜湿地", 1782.0, 756.0], ["星落群岛", 1386.0, 1148.0], ["静霜北岭", 1483.2, 168.0], ["镜湖未竟城", 1987.5, 544.6], ["黑潮螺旋城", 145.9, 819.1], ["翠冠树海迷宫城", 1848.0, 322.0], ["赤盐沉宫", 357.3, 1074.9], ["曜冠空环城", 1298.0, 378.0], ["河灯镇", 1738.0, 798.0], ["风车灯镇", 1540.0, 924.0], ["灰岩驿镇", 1122.0, 868.0], ["蜜酒穴镇", 1892.4, 953.7], ["盐沼灯镇", 286.2, 1075.8], ["星屑桥镇", 1343.3, 1171.9], ["林铃营镇", 1800.3, 457.4], ["铁瀑采矿镇", 1497.3, 1037.1], ["亥珀波瑞亚遗址", 1100.0, 84.0], ["终北断谷", 990.0, 140.0], ["寒天之钉群", 1232.0, 112.0], ["银白古树根脉", 1760.0, 252.0], ["灰雨城遗址", 968.0, 784.0], ["无名碑林", 462.0, 742.0], ["葛摩恩碎碑矿坑", 572.0, 980.0], ["饥渊枯祭原", 352.0, 476.0], ["白碑断门", 1021.0, 751.0], ["迷宫都市·阿卡迪亚", 1100.0, 672.0], ["化圣雪原", 990.0, 271.7], ["神陨沙海", 1012.0, 1104.6], ["曙辉平原", 1584.0, 700.0], ["砂祷镇", 924.0, 1008.0], ["圣骸井", 968.0, 1176.0], ["风蚀驿", 814.0, 1078.0], ["炽镜村", 1144.0, 1148.0], ["琉火坠坛", 1078.0, 1260.0], ["雪祷村", 968.0, 392.0], ["白熄修院", 1100.0, 350.0], ["霜灯堡", 902.0, 252.0], ["冰脊前哨", 1386.0, 224.0], ["曙禾镇", 1540.0, 784.0], ["誓桥镇", 1474.0, 588.0], ["白鹿驿", 1738.0, 602.0], ["鸢歌村", 1628.0, 490.0], ["四路庄", 1650.0, 868.0], ["灰炉镇", 748.0, 840.0], ["红契渡口", 880.0, 770.0], ["暮角屯", 616.0, 896.0], ["森隙村", 1851.5, 585.8], ["月露集", 1894.2, 683.2], ["黑耀帝国自然科学与工程研究院", 770.0, 490.0], ["渊月电网主塔群", 704.0, 602.0], ["渊月列车总枢纽", 792.0, 672.0], ["黑曜电报总站", 594.0, 644.0], ["赤雷军械实验场", 652.7, 1153.5], ["帝国电械义肢医院", 572.0, 770.0], ["星环奥法总塔", 1363.3, 324.5], ["银镜湖占星塔群", 1891.3, 567.8], ["阿卡迪亚公会以太钟楼", 1149.9, 610.0], ["晨曦金鸢工坊区", 1474.0, 784.0], ["星纱列车东陆总枢纽", 1672.0, 742.0], ["圣堂净化封印院", 1408.0, 602.0], ["白石长垒城防机关阵", 1004.1, 700.0], ["元素晶匣工坊镇", 1452.0, 476.0], ["翠冠林海", 1936.0, 350.0], ["霜眠群峰", 1716.0, 238.0], ["赤熔断岭", 682.0, 1120.0], ["灰烬高原", 770.0, 924.4], ["银镜盆地", 1870.0, 476.0], ["风啸高原", 1628.0, 586.9], ["星冠丘陵", 1517.8, 671.4], ["月潮内海", 1914.0, 804.6], ["风铃天池", 1738.0, 490.0], ["圣印湖", 1540.0, 588.0], ["星泪湖", 1408.0, 504.0], ["霜羽河", 1743.7, 420.6], ["镜潮河", 1915.8, 728.6], ["风歌河", 1524.6, 790.9], ["灰契河", 836.0, 798.0], ["曜沙湾", 1196.6, 1086.3], ["掷月城", 814.0, 980.0], ["擂环城", 1672.0, 644.0], ["雪歌城", 1804.0, 546.0], ["汤鳞城", 1653.1, 309.8], ["鹭影泊", 1813.7, 815.4], ["霞藤庄", 1430.0, 994.0], ["摘星车镇", 704.0, 756.0], ["羽筝崖", 1650.0, 616.0]]; const pt = document.getElementById('map').createSVGPoint(); const els = [...document.querySelectorAll('#seaProbes path')]; const wet = []; const near = []; for (const [n, x, y] of LM) { pt.x = x; pt.y = y; let inside = false; for (const e of els) { if (e.getAttribute('data-k') === 's' ? e.isPointInStroke(pt) : e.isPointInFill(pt)) { inside = true; break; } } if (inside) wet.push(n); else { for (const e of els) { if (e.getAttribute('data-k') === 's') continue; for (const [dx, dy] of [[8, 0], [-8, 0], [0, 8], [0, -8]]) { pt.x = x + dx; pt.y = y + dy; if (e.isPointInFill(pt)) { near.push(n); break; } } } } } log.push('落进新海里的地标 ' + (wet.join('、') || '没有') + '；挨着新海的 ' + [...new Set(near)].join('、')); }

  // ---- 运河和通内陆的水路 ----
  const cg = mk('g', { id: 'seaCanals' }, null);
  vb.insertBefore(cg, document.getElementById('labels'));
  const canal = (d, w = 2.2) => { mk('path', { d, fill: 'none', stroke: '#24506a', 'stroke-width': w + 1.2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', opacity: 0.85 }, cg); mk('path', { d, fill: 'none', stroke: '#9cc9e3', 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, cg); const el = mk('path', { d, fill: 'none' }, cg); const L = el.getTotalLength(); for (let s = 14; s < L - 6; s += 26) { const p = el.getPointAtLength(s), q = el.getPointAtLength(s + 1); const dx = q.x - p.x, dy = q.y - p.y, l = Math.hypot(dx, dy) || 1; mk('line', { x1: p.x - dy / l * (w + 1.6), y1: p.y + dx / l * (w + 1.6), x2: p.x + dy / l * (w + 1.6), y2: p.y - dx / l * (w + 1.6), stroke: '#24506a', 'stroke-width': 0.6 }, cg); } el.remove(); };
  const waterway = (pts) => { const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#2f6f92', 'stroke-width': 2.4, 'stroke-linecap': 'round', opacity: 0.55 }, cg); mk('path', { d, fill: 'none', stroke: '#e9f3f8', 'stroke-width': 0.8, 'stroke-dasharray': '3 2.2', 'stroke-linecap': 'round' }, cg); };
  // 黑耀运河：湾头往东北，穿过环山西南的口子进烬灭之都（口子照环山那一圈山的空当找）
  let gapAng = null;
  { const bins = new Array(36).fill(0); for (const u of document.querySelectorAll('#terrain use')) { const h = u.getAttribute('href'); if (!/hill|mount/.test(h)) continue; const x = +u.getAttribute('x') + (+u.getAttribute('width')) / 2 - 616, y = +u.getAttribute('y') + (+u.getAttribute('height')) / 2 - 714; const d = Math.hypot(x, y); if (d < 94 || d > 170) continue; bins[Math.floor(((Math.atan2(y, x) * 180 / Math.PI) + 360) % 360 / 10)]++; } let best = 1e9; for (let k = 0; k < 36; k++) { const a = k * 10 + 5; const diff = Math.abs(((a - 155 + 540) % 360) - 180); if (bins[k] === 0 && diff < best) { best = diff; gapAng = a; } } log.push('环山空当 ' + bins.map((v, k) => v ? '' : k * 10).filter((v) => v !== '').join(',')); }
  canal(smooth([[436, 800], [464, 792], [496, 772], [530, 756], [566, 738], [596, 724]]));
  canal(smooth([[640, 716], [700, 718], [760, 726], [800, 756], [834, 796]]), 2);
  // 王道运河：金鸢城西门顺着王道往西到阿卡迪亚
  canal('M1500,744 C1440,742 1380,744 1330,742 S1215,738 1128,690', 2.4);
  // 三河汇流：凛河从北来，灰契河（烬河）从西穿过中央水门来，汇到阿卡迪亚，白碑河往南进白碑湾
  const rv = document.getElementById('rivers');
  const meander = (pts, amp) => { const el = mk('path', { d: smooth(pts), fill: 'none' }, rv); const L = el.getTotalLength(); const out = []; const ph = rnd() * 6; for (let s0 = 0; s0 <= L; s0 += 5) { const p = el.getPointAtLength(s0), q = el.getPointAtLength(Math.min(L, s0 + 1)); let dx = q.x - p.x, dy = q.y - p.y; const l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l; const e = (s0 < 8 || s0 > L - 8) ? 0 : amp * (Math.sin(s0 / 9 + ph) + 0.5 * Math.sin(s0 / 4.1 + ph * 2) + 0.4 * (rnd() - 0.5)); out.push([p.x - dy * e, p.y + dx * e]); } el.remove(); return out; };
  const river = (pts0, w0, w1, amp = 2.4) => { const pts = meander(pts0, amp); const el = mk('path', { d: smooth(pts), fill: 'none' }, rv); const L = el.getTotalLength(); const n = Math.max(6, Math.round(L / 6)); let prev = el.getPointAtLength(0); for (let k = 1; k <= n; k++) { const p = el.getPointAtLength(L * k / n); mk('line', { x1: prev.x, y1: prev.y, x2: p.x, y2: p.y, stroke: '#2e89c2', 'stroke-width': w0 + (w1 - w0) * k / n, 'stroke-linecap': 'round' }, rv); prev = p; } el.remove(); return pts; };
  const linhe = river([[1094, 362], [1086, 420], [1097, 498], [1090, 580], [1076, 640], [1066, 694], [1042, 732], [1024, 749]], 0.8, 2.3);
  const huiqi = river([[770, 862], [790, 830], [812, 808], [836, 798], [860, 782], [880, 770], [930, 762], [980, 756], [1018, 751]], 1.0, 2.5);
  const baibei = river([[1024, 754], [1033, 800], [1046, 856], [1070, 912], [1110, 952], [1152, 978]], 2.6, 3.6);
  // 熔铁灰河（炉城底下流出来的断崖下的河）往西流进双月内海；墙西的灰河从灰烬高原当中往西南，过渡口，到赤熔断岭北头接上顺着断岭往南的那一条（11-08 灰河分两条）
  river([[1556, 1125], [1549, 1131], [1535, 1142], [1515, 1143], [1498, 1147], [1478, 1150], [1458, 1146], [1443, 1139], [1427, 1131]], 0.9, 2.0, 1.4);
  river([[775, 912], [762, 948], [746, 984], [726, 1014], [708, 1034], [688, 1050]], 0.7, 1.5, 1.6);
  waterway(huiqi); waterway(baibei); waterway([[1128, 690], [1096, 700], [1066, 700], [1042, 732], [1024, 749]]);
  { const pts = riverPts(232); waterway([[1534, 744], pts[0]]); waterway(pts); }
  // 红契渡口：灰契河进中央水门以前最后一道河湾，等闸的船排在这里；红契碑、红契桥
  { const x = 880, y = 770; mk('circle', { cx: x, cy: y, r: 7.5, fill: '#b8473a', opacity: 0.18 }, cg); for (let k = 0; k < 6; k++) { const a = k / 6 * Math.PI * 2; mk('path', { d: `M${x + Math.cos(a) * 4.2},${y + Math.sin(a) * 4.2} l${Math.cos(a) * 2.2},${Math.sin(a) * 2.2}`, stroke: '#5a2a24', 'stroke-width': 0.5 }, cg); } mk('rect', { x: x - 1.1, y: y - 4.4, width: 2.2, height: 4.2, fill: '#b8473a', stroke: '#4a221d', 'stroke-width': 0.35 }, cg); mk('line', { x1: x - 5, y1: y + 3.4, x2: x + 5, y2: y + 1.2, stroke: '#4a3b2a', 'stroke-width': 1.1 }, cg); for (let k = 0; k < 5; k++) mk('path', { d: `M${x - 9 + k * 2.6},${y - 6.5} l1.6,0 l-0.8,-1.4 z`, fill: '#e9e2cf', stroke: '#3a3226', 'stroke-width': 0.25 }, cg); }
  // 中央水门：灰契河穿墙的地方
  { const x = 1021, y = 751; mk('rect', { x: x - 3.2, y: y - 3.2, width: 6.4, height: 6.4, fill: '#efe7d6', stroke: '#3a3226', 'stroke-width': 0.6, transform: `rotate(45 ${x} ${y})` }, cg); }
  { const ov = mk('g', { id: 'seaAUL' }, null); vb.insertBefore(ov, document.getElementById('seaCanals')); ov.innerHTML = 'AUL_SVG'; }
  // ---- 航路 ----
  const lg = mk('g', { id: 'seaLanes' }, null);
  vb.insertBefore(lg, document.getElementById('labels'));
  const lane = (pts, c = '#1d4e66') => { const d = smooth(pts); mk('path', { d, fill: 'none', stroke: '#f4fbff', 'stroke-width': 1.6, opacity: 0.55, 'stroke-linecap': 'round' }, lg); mk('path', { d, fill: 'none', stroke: c, 'stroke-width': 0.8, 'stroke-dasharray': '5 3', opacity: 0.85, 'stroke-linecap': 'round' }, lg); };
  lane([[214, 312], [170, 380], [120, 520], [95, 650], [104, 760], [112, 824]]);
  lane([[214, 312], [236, 318], [262, 342], [296, 392], [352, 412], [430, 414]], '#2a5d78');
  lane([[296, 392], [306, 470], [282, 548], [236, 610]], '#2a5d78');
  lane([[368, 118], [480, 104], [590, 104], [612, 150], [622, 230], [626, 300]], '#2a5d78');
  lane([[112, 824], [180, 810], [260, 796], [340, 806], [420, 802]], '#2a5d78');
  lane([[112, 824], [95, 960], [80, 1120], [123, 1180]]);
  lane([[123, 1180], [100, 1232], [200, 1276], [450, 1264], [650, 1242], [850, 1256], [1000, 1262], [1180, 1246], [1248, 1222]]);
  lane([...riverPts(568).reverse(), [1212, 1062], [1214, 1012], [1180, 990], [1150, 978]], '#2a5d78');
  lane([[1248, 1222], [1500, 1218], [1720, 1186], [1900, 1116], [2060, 990], [2100, 870], [2069, 760]]);
  lane([[2069, 760], [1990, 800], [1914, 805], [1840, 812]], '#2a5d78');
  lane([[2069, 747], [2150, 690], [2178, 520], [2176, 330], [2150, 175], [2000, 118]]);
  lane([...riverPts(176).reverse(), [240, 1112], [300, 1094], [352, 1082]], '#7a3e36');
  lane([[214, 312], [232, 250], [300, 170], [368, 118]]);
  // ---- 地名 ----
  if (!document.getElementById('pFont')) { const l = document.createElement('link'); l.id = 'pFont'; l.rel = 'stylesheet'; l.href = 'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700;900&display=swap'; document.head.appendChild(l); }
  const lab = mk('g', { id: 'seaLabels', 'font-family': '"Noto Serif SC", serif', 'text-anchor': 'middle', 'paint-order': 'stroke', 'stroke-linejoin': 'round' }, vb);
  const T = (s, x, y, fs, o = {}) => { const e = mk('text', Object.assign({ x, y, 'font-size': fs, 'font-weight': 700, fill: '#2c261f', stroke: '#f6f0e2', 'stroke-width': fs * 0.2, 'letter-spacing': fs * 0.08 }, o), lab); e.textContent = s; return e; };
  const sea = (s, x, y, fs) => T(s, x, y, fs, { 'font-weight': 500, fill: '#24566b', stroke: '#dcedf2', 'stroke-width': fs * 0.14, 'letter-spacing': fs * 0.5, opacity: 0.9 });
  const wl = (s, x, y, fs, rot = 0) => T(s, x, y, fs, { 'font-weight': 700, fill: '#1f4f69', stroke: '#eef6f9', 'stroke-width': fs * 0.22, transform: rot ? `rotate(${rot} ${x} ${y})` : '' });
  for (const [s, x, y, fs] of [['西海', 70, 690, 24], ['北海', 600, 60, 20], ['南海', 760, 1292, 22], ['东海', 2182, 600, 15], ['双月内海', 1330, 1070, 14], ['赤盐内海', 300, 1124, 12], ['月潮内海', 1925, 832, 10], ['镰 月 海', 318, 470, 14], ['长船湾', 650, 232, 8], ['深蓝海湾', 292, 812, 9], ['北辰湾', 404, 140, 7.5], ['白碑湾', 1190, 1018, 7]]) sea(s, x, y, fs);
  for (const [s, x, y, fs, r] of [['赤盐海门', 150, 1198, 7.5, 0], ['双月海门', 1270, 1176, 7.5, 0], ['镰月海门', 205, 300, 7, 0], ['黑耀运河', 520, 772, 7.5, -20], ['王道运河', 1320, 728, 8, 0], ['白碑河', 1068, 860, 7.5, 62], ['熔铁灰河', 1506, 1134, 6.5, -8], ['灰河', 757, 962, 6.5, 64], ['灰契河', 792, 846, 7, -40], ['凛河', 1112, 470, 7, 80], ['红契渡口', 892, 792, 7.5, 0], ['金鸢河', 1700, 782, 7.5, 5]]) wl(s, x, y, fs, r);
  for (const [s, x, y] of [['烬灭之都', 616, 740], ['金鸢城', 1518, 768], ['阿卡迪亚', 1100, 708], ['中央水门', 1021, 772], ['深潮蓝堡', 198, 884], ['黯潮军港', 154, 744], ['镰月商港', 252, 268], ['饥渊枯祭原', 368, 492], ['赤盐沉宫', 357, 1090], ['银帆海港', 2069, 763], ['黑翼天塔', 374, 210], ['曜沙湾', 1196, 1102], ['星落群岛', 1386, 1164]]) { mk('circle', { cx: x, cy: y - 14, r: 2, fill: '#c0392b', stroke: '#fff', 'stroke-width': 0.6 }, lab); T(s, x, y, 7.5); }
  try { await document.fonts.load('700 20px "Noto Serif SC"', '西海北海南海东海双月赤盐月潮深蓝北辰海门运河王道白碑水道金鸢灰契烬灭之都阿卡迪亚深潮蓝堡黯军港沉宫银帆黑翼天塔曜沙星落群岛镰商'); await sleep(1200); } catch (e) { log.push('字体 ' + e); }
  return log.join('；');
})();
