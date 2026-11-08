// 纷争纪的盐海（补卷_19 地图的几层：1088年萨尔缇和佛拉斯在盐原上打了九天，平原塌下去，海从碧湾的湾口倒灌进来，海刚灌进来是白的，往后一年一年染红）
// 在 az_reset.sh、碧湾那一步（_az_biwan_run.js）之后跑：碧湾＝今天赤盐内海那一整片水面加湾口，盐原在湾北边
//   塌下去的那一片：整片盐原连同盐原和湾之间那一溜地，并进湾里成了盐海，新岸在画布上抹圆了再描；
//   西边留一个岬角（往后盐沼灯镇在岬角尖上），岬角往西那一段北岸是老滩（红晶滩），联军的七座营垒修在滩上（照前传：盐沼灯镇是七座里靠东那一座）
//   碧湾那一步做的遮罩、岸线、浅色层都添上这一块；水染红，湾口那一头淡，往东北越来越红
//   往后的赤盐内海就是这一整片（1001 年那一张要跟着把塌下去的这一块画进去）
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  if (!document.getElementById('bay_moon')) return '先跑碧湾那一步';
  if (document.getElementById('saltsea_blob')) return '已经改过';
  const fp = document.getElementById('featurePaths');
  const defs = fp.closest('defs');
  const blobD = (cx, cy, rx, ry, ph, a1, a2) => { let d = ''; for (let a = 0; a < 360; a += 4) { const t = a * Math.PI / 180, k = 1 + a1 * Math.sin(3 * t + ph) + a2 * Math.sin(5 * t + ph * 2); d += (d ? 'L' : 'M') + (cx + Math.cos(t) * rx * k).toFixed(2) + ',' + (cy + Math.sin(t) * ry * k).toFixed(2); } return d + 'Z'; };
  // 塌下去的那一片：先拿一个椭圆盖住盐原南边大半和盐原跟湾之间那一溜地，跟今天赤盐内海那一片湖并起来，
  // 再在画布上把并起来的样子抹圆（模糊再取阈值，接缝那两个凹口填平），描出新岸；y 1090 以南照湖原来的岸
  const blobR = (cx, cy, rx, ry) => { let d = ''; for (let a = 0; a < 360; a += 3) { const t = a * Math.PI / 180, k = 1 + 0.07 * Math.sin(3 * t + 1.9) + 0.045 * Math.sin(5 * t + 3.8) + 0.03 * Math.sin(8 * t + 0.7) + 0.02 * Math.sin(13 * t + 2.2); d += (d ? 'L' : 'M') + (cx + Math.cos(t) * rx * k).toFixed(2) + ',' + (cy + Math.sin(t) * ry * k).toFixed(2); } return d + 'Z'; };
  const raw = blobR(382, 1028, 110, 76);
  // 东边那一道接缝放宽（西边那个凹口留着，往后盐沼灯镇就在那个岬角上）
  const rawE = blobD(442, 1080, 50, 38, 0.4, 0.05, 0.03);
  const X0 = 40, Y0 = 880, Wd = 560, Ht = 380, S = 2;
  const cv = document.createElement('canvas'); cv.width = Wd * S; cv.height = Ht * S; const cx0 = cv.getContext('2d');
  cx0.setTransform(S, 0, 0, S, -X0 * S, -Y0 * S); cx0.fillStyle = '#fff';
  const lakeD = document.getElementById('feature_10').getAttribute('d');
  cx0.fill(new Path2D(lakeD)); cx0.fill(new Path2D(raw)); cx0.fill(new Path2D(rawE));
  const cv2 = document.createElement('canvas'); cv2.width = cv.width; cv2.height = cv.height; const c2 = cv2.getContext('2d'); c2.filter = 'blur(22px)'; c2.drawImage(cv, 0, 0);
  const A0 = cx0.getImageData(0, 0, cv.width, cv.height).data, A1 = c2.getImageData(0, 0, cv.width, cv.height).data;
  const gw = cv.width, gh = cv.height, grid = new Uint8Array(gw * gh);
  for (let y = 0; y < gh; y++) { const my = Y0 + y / S; const w = my < 1086 ? 1 : my > 1112 ? 0 : (1112 - my) / 26; for (let x = 0; x < gw; x++) { const k = (y * gw + x) * 4 + 3; const v = w * A1[k] + (1 - w) * A0[k]; grid[y * gw + x] = v >= 0.4 * 255 ? 1 : 0; } }
  // 西边那个岬角往东留长一点（往后盐沼灯镇 286,1076 落在岬角尖上，不能落水）
  for (let y = 0; y < gh; y++) { const my = Y0 + y / S; if (my < 1064 || my > 1094) continue; for (let x = 0; x < gw; x++) { const mx = X0 + x / S; if (((mx - 281) / 17) ** 2 + ((my - 1079) / 8.5) ** 2 < 1) grid[y * gw + x] = 0; } }
  // 描边（marching squares），留最长的那一圈
  const segs = new Map(); const key = (x, y) => x + ',' + y; const addSeg = (a, b) => { if (!segs.has(a)) segs.set(a, []); segs.get(a).push(b); };
  const gv = (x, y) => (x < 0 || y < 0 || x >= gw || y >= gh) ? 0 : grid[y * gw + x];
  for (let y = -1; y < gh; y++) for (let x = -1; x < gw; x++) {
    const c = (gv(x, y) << 3) | (gv(x + 1, y) << 2) | (gv(x + 1, y + 1) << 1) | gv(x, y + 1);
    if (c === 0 || c === 15) continue;
    const T_ = key(2 * x + 1, 2 * y), R_ = key(2 * x + 2, 2 * y + 1), B_ = key(2 * x + 1, 2 * y + 2), L_ = key(2 * x, 2 * y + 1);
    const tab = { 1: [[L_, B_]], 2: [[B_, R_]], 3: [[L_, R_]], 4: [[R_, T_]], 5: [[L_, T_], [R_, B_]], 6: [[B_, T_]], 7: [[L_, T_]], 8: [[T_, L_]], 9: [[T_, B_]], 10: [[T_, R_], [B_, L_]], 11: [[T_, R_]], 12: [[R_, L_]], 13: [[R_, B_]], 14: [[B_, L_]] };
    for (const [a, b] of tab[c]) addSeg(a, b);
  }
  let bestLoop = [];
  const used = new Set();
  for (const start of segs.keys()) { if (used.has(start)) continue; const loop = []; let cur = start; while (cur && !used.has(cur)) { used.add(cur); loop.push(cur); cur = (segs.get(cur) || []).find((m) => !used.has(m)); } if (loop.length > bestLoop.length) bestLoop = loop; }
  const pts = bestLoop.filter((_, i) => i % 6 === 0).map((k) => { const [hx, hy] = k.split(',').map(Number); return [X0 + hx / 2 / S, Y0 + hy / 2 / S]; });
  const n = pts.length; let D = '';
  for (let i = 0; i < n; i++) { const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n]; if (i === 0) D += `M${p1[0].toFixed(1)},${p1[1].toFixed(1)}`; D += ` C${(p1[0] + (p2[0] - p0[0]) / 6).toFixed(1)},${(p1[1] + (p2[1] - p0[1]) / 6).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) / 6).toFixed(1)},${(p2[1] - (p3[1] - p1[1]) / 6).toFixed(1)} ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`; }
  D += ' Z';
  window.__saltD = D;
  mk('path', { id: 'saltsea_blob', d: D }, fp);
  const add = (id, attrs) => { const m = document.getElementById(id); if (m) mk('use', Object.assign({ href: '#saltsea_blob' }, attrs), m); return !!m; };
  add('land', { fill: 'black' });
  add('water', { fill: 'white' });
  add('nobay', { fill: 'black' });
  add('landside', { fill: 'black' });
  add('bayclip', {});
  add('noLakeIn', { fill: 'black' });
  add('noBayIn', { fill: 'black' });
  const box = { maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 2200, height: 1400 };
  const noBL = mk('mask', Object.assign({ id: 'noBayLakeIn' }, box), defs);
  mk('rect', { x: 0, y: 0, width: 2200, height: 1400, fill: 'white' }, noBL);
  mk('use', { href: '#bay_moon', fill: 'black' }, noBL);
  mk('use', { href: '#feature_10', fill: 'black' }, noBL);
  // 新岸照海岸线的样式描（只露陆地那一边）
  const sea = document.getElementById('sea_island');
  mk('use', { href: '#saltsea_blob', fill: 'none', mask: 'url(#landside)' }, sea);
  // 海的浅色层
  const ol = document.getElementById('oceanLayers');
  const g = ol.querySelector('g[clip-path="url(#bayclip)"]');
  const gf = g && g.querySelector('g[opacity="0.24"]');
  if (gf) mk('use', { href: '#saltsea_blob', fill: '#ecf2f9' }, gf);
  if (g) for (const w of [5, 10, 16]) mk('use', { href: '#saltsea_blob', fill: 'none', stroke: '#ecf2f9', 'stroke-opacity': '0.13', 'stroke-width': w, mask: 'url(#noBayLakeIn)' }, g);
  // 染红：湾口那一头淡，往东北越来越红
  const lg = mk('linearGradient', { id: 'saltRed', gradientUnits: 'userSpaceOnUse', x1: 150, y1: 1215, x2: 470, y2: 990 }, defs);
  const RK = window.__saltRedK || 1;  // 纷争纪中段 1，往后一年比一年红
  mk('stop', { offset: '0', 'stop-color': '#e2b9ad', 'stop-opacity': Math.min(0.9, 0.3 * RK) }, lg);
  mk('stop', { offset: '0.45', 'stop-color': '#cf8270', 'stop-opacity': Math.min(0.9, 0.5 * RK) }, lg);
  mk('stop', { offset: '1', 'stop-color': '#a83f30', 'stop-opacity': Math.min(0.92, 0.62 * RK) }, lg);
  const tint = mk('g', { id: 'saltRedTint', 'clip-path': 'url(#bayclip)' }, ol);
  mk('rect', { x: 40, y: 900, width: 480, height: 360, fill: 'url(#saltRed)' }, tint);
  // 盐原塌剩下的边上若还露一点盐壳，透红
  const sp = document.getElementById('moonSaltPlain');
  if (sp) { const rim = mk('path', { d: blobD(385, 1000, 92, 40, 0.7, 0.12, 0.07), fill: '#d99a8e', opacity: 0.32 }, null); sp.appendChild(rim); }
  // 流进塌陷那一片的河在新岸收住
  const ns = mk('mask', Object.assign({ id: 'noSaltSea' }, box), defs);
  mk('rect', { x: 0, y: 0, width: 2200, height: 1400, fill: 'white' }, ns);
  mk('use', { href: '#saltsea_blob', fill: 'black' }, ns);
  const probe = mk('path', { id: 'saltseaProbe', d: D, fill: '#000', opacity: 0 }, document.getElementById('viewbox'));
  window.__saltHideIcons = () => {
    const pt = document.getElementById('map').createSVGPoint(); let n = 0;
    for (const u of document.querySelectorAll('#terrain use')) { if (u.style.display === 'none') continue; const x = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2, y = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2; if (x < 250 || x > 500 || y < 960 || y > 1110) continue; pt.x = x; pt.y = y; if (probe.isPointInFill(pt)) { u.style.display = 'none'; n++; } }
    let r = 0; for (const p of document.querySelectorAll('#rivers path')) { const b = p.getBBox(); if (b.x < 500 && b.x + b.width > 250 && b.y < 1110 && b.y + b.height > 960) { p.setAttribute('mask', 'url(#noSaltSea)'); r++; } }
    return n + '/' + r;
  };
  return '盐海并好了（新岸 ' + n + ' 点），藏符号/收河 ' + window.__saltHideIcons();
})();
