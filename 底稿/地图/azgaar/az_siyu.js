// 纷争纪炮的年月（约3600年）的南边：照 az_nanyuan.js 改（11-08 时代地图方向稿第十二节第2件：墙照用户画的那一道，南头落在今天神陨沙海的北沿；
//   死域是墙南头往南那一片；南界从墙的南头顺着死域北沿往西一直到盐海）
//   南界那一条线照下面 SL 画：西头接盐海的东南角，过雷暴荒地北沿、红刺坡底下、墙的南头，往东到落星洼东边；死域东边到轰鸣断崖以西
//   南界以北：神陨沙海那一片这时候还没成沙（沙海是浮塔的年月才有），照月银纪的南原画成草
//   南界以南：死域，北沿一层灰绿的草，往里灰烂一片；落星洼是干的洼地，神和魔神多半落在这里，洼底一堆一堆的骨
//   双月内海往后北边那一片圆海（1001 年那一张），这时候是一个干的浅坑，长着草，只留一圈坑沿
//   地形符号：Azgaar 有时候会整层重画，所以藏符号写成 window.__siyuHideIcons()，截图以前再跑一回
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const C = pack.cells, P = pack.vertices.p;
  for (const id of ['siyuGrass', 'siyuDead', 'siyuDefs', 'siyuNanjie']) { const o = document.getElementById(id); if (o) o.remove(); }
  const defs = document.getElementById('featurePaths').closest('defs');
  const pd = mk('g', { id: 'siyuDefs' }, defs);
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const OPT = window.__siyuOpt || {};
  const SL = OPT.SL || [[476, 1128], [520, 1138], [570, 1144], [620, 1146], [662, 1138], [702, 1122], [742, 1102], [792, 1082], [832, 1066], [866, 1052], [890, 1034], [910, 1010], [928, 991], [944, 978], [972, 982], [1010, 990], [1050, 996], [1090, 1003], [1130, 1012], [1170, 1023], [1210, 1031], [1250, 1036], [1290, 1040], [1330, 1041], [1370, 1043], [1408, 1050], [1432, 1066]];
  const EAST = [[1440, 1100], [1442, 1140], [1436, 1180], [1430, 1220], [1426, 1262], [1426, 1400]];
  const POLY = [...SL, ...EAST, [476, 1400]];
  const inPoly = (x, y) => { let c = false; for (let i = 0, j = POLY.length - 1; i < POLY.length; j = i++) { const [xi, yi] = POLY[i], [xj, yj] = POLY[j]; if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c; } return c; };
  const slY = (x) => { for (let i = 0; i < SL.length - 1; i++) { const a = SL[i], b = SL[i + 1]; if (x >= a[0] && x <= b[0]) return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]); } return null; };
  const isSea = (n) => C.h[n] < 20 && !(pack.features[C.f[n]] && pack.features[C.f[n]].type === 'lake');
  // 南原那一片（照 az_nanyuan.js 找：热沙漠连成的一片、双月内海的湖底和湖岸、当中那一圈冷荒漠）
  let s0 = -1, best = 1e9;
  for (let i = 0; i < C.i.length; i++) { if (C.biome[i] !== 1) continue; const d = (C.p[i][0] - 900) ** 2 + (C.p[i][1] - 1080) ** 2; if (d < best) { best = d; s0 = i; } }
  const sand = new Uint8Array(C.i.length); const st = [s0]; sand[s0] = 1;
  while (st.length) { const i = st.pop(); for (const n of C.c[i]) if (!sand[n] && C.biome[n] === 1) { sand[n] = 1; st.push(n); } }
  const lakeF = (pack.features[9] && pack.features[9].type === 'lake') ? 9 : -1;
  const lake = new Uint8Array(C.i.length); for (let i = 0; i < C.i.length; i++) if (C.f[i] === lakeF) lake[i] = 1;
  const shore = new Uint8Array(C.i.length);
  for (let i = 0; i < C.i.length; i++) if (lake[i]) for (const n of C.c[i]) if (!lake[n] && C.h[n] >= 20) { shore[n] = 1; for (const m of C.c[n]) if (!lake[m] && C.h[m] >= 20) shore[m] = 1; }
  const nanyuan = new Uint8Array(C.i.length);
  for (let i = 0; i < C.i.length; i++) {
    if (sand[i] || lake[i] || shore[i]) { nanyuan[i] = 1; continue; }
    const [x, y] = C.p[i];
    if (C.biome[i] === 2 && C.h[i] >= 20 && C.h[i] <= 55 && x > 880 && x < 1480 && y > 880 && y < 1190 && !(y > 1150 && C.c[i].some(isSea))) nanyuan[i] = 1;
  }
  const grass = [], rim = [], dead = [], sandIn = [];
  for (let i = 0; i < C.i.length; i++) {
    const [x, y] = C.p[i];
    const land = C.h[i] >= 20 || lake[i];
    if (!land) continue;
    if (C.biome[i] === 11) continue;
    if (inPoly(x, y)) { if (OPT.sand && sand[i]) { sandIn.push(i); continue; } if (OPT.lake === 'wet' && lake[i]) continue; const sy = slY(x); if (sy !== null && y - sy < 16 && !lake[i]) rim.push(i); else dead.push(i); continue; }
    if (nanyuan[i]) grass.push(i);
  }
  const pathOf = (cells) => cells.map((i) => 'M' + C.v[i].map((v) => P[v][0].toFixed(2) + ',' + P[v][1].toFixed(2)).join('L') + 'Z').join('');
  // 湖从水遮罩、陆地遮罩、湖那一组里拿掉（落星洼这时候是干的）
  if (OPT.lake !== 'wet') for (const u of [...document.querySelectorAll('#land use, #water use, #lakes use')]) { const h = u.getAttribute('href') || u.getAttribute('xlink:href'); if (h === `#feature_${lakeF}`) { if (u.closest('#lakes')) u.style.display = 'none'; else u.remove(); } }
  const biomes = document.getElementById('biomes');
  const op = +(biomes.getAttribute('opacity') || 0.6);
  const grassC = document.getElementById('biome4').getAttribute('fill');
  const landC = document.getElementById('landmass').getAttribute('fill');
  // 南界以北的南原：草
  const gGrass = mk('g', { id: 'siyuGrass', mask: 'url(#land)' }, null);
  biomes.parentNode.insertBefore(gGrass, biomes.nextSibling);
  { const d = pathOf(grass); mk('path', { d, fill: landC, stroke: landC, 'stroke-width': 0.6, 'stroke-linejoin': 'round' }, gGrass); const gg = mk('g', { opacity: op }, gGrass); mk('path', { d, fill: grassC, stroke: grassC, 'stroke-width': 0.6, 'stroke-linejoin': 'round' }, gg); }
  // 南界以南：死域
  const gDead = mk('g', { id: 'siyuDead', mask: 'url(#land)' }, null);
  biomes.parentNode.insertBefore(gDead, gGrass.nextSibling);
  const dRim = pathOf(rim), dDead = pathOf(dead);
  mk('path', { d: dRim + dDead, fill: landC, stroke: landC, 'stroke-width': 0.6, 'stroke-linejoin': 'round' }, gDead);
  { const g1 = mk('g', { opacity: 0.72 }, gDead); mk('path', { d: dRim, fill: '#a9ae96', stroke: '#a9ae96', 'stroke-width': 0.6, 'stroke-linejoin': 'round' }, g1); }
  { const g2 = mk('g', { opacity: 0.8 }, gDead); mk('path', { d: dDead, fill: '#a39c92', stroke: '#a39c92', 'stroke-width': 0.6, 'stroke-linejoin': 'round' }, g2); }
  const pt = mk('pattern', { id: 'siyuRot', width: 7, height: 7, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(23)' }, pd);
  mk('rect', { width: 7, height: 7, fill: 'none' }, pt); mk('circle', { cx: 1.6, cy: 2.2, r: 1.1, fill: '#5d5650', opacity: 0.32 }, pt); mk('circle', { cx: 5.1, cy: 5.4, r: 0.7, fill: '#6b5f58', opacity: 0.28 }, pt); mk('path', { d: 'M3.5,0.5 l1,1.4 M0.4,5.6 l1.3,-0.6', stroke: '#4d4742', 'stroke-width': 0.3, opacity: 0.4 }, pt);
  mk('path', { d: dDead, fill: 'url(#siyuRot)' }, gDead);
  // 往里越深越暗：几团暗影（神血一层层渗进土里）
  { const rg = mk('radialGradient', { id: 'siyuStain' }, pd); mk('stop', { offset: '0', 'stop-color': '#4a4040', 'stop-opacity': 0.34 }, rg); mk('stop', { offset: '1', 'stop-color': '#4a4040', 'stop-opacity': 0 }, rg);
    for (const [x, y, r] of [[960, 1080, 70], [1090, 1130, 90], [1230, 1150, 70], [800, 1150, 55], [1330, 1110, 60], [620, 1205, 40]]) mk('ellipse', { cx: x, cy: y, rx: r * 1.3, ry: r * 0.8, fill: 'url(#siyuStain)' }, gDead); }
  // 落星洼：干洼，洼底一堆一堆的骨
  if (lakeF > 0 && OPT.lake !== 'wet') {
    mk('use', { href: `#feature_${lakeF}`, fill: '#c3b7a1', stroke: '#7e705e', 'stroke-width': 0.7, opacity: 0.9 }, gDead);
    mk('use', { href: `#feature_${lakeF}`, fill: 'none', stroke: '#e9e1cf', 'stroke-width': 2.4, opacity: 0.35, transform: 'translate(0,1.2)' }, gDead);
    const lp = document.getElementById(`feature_${lakeF}`); const sp = document.getElementById('map').createSVGPoint(); const bb = lp.getBBox(); let n = 0, tries = 0;
    while (n < 16 && tries < 600) { tries++; const x = bb.x + rnd() * bb.width, y = bb.y + rnd() * bb.height; sp.x = x; sp.y = y; if (!lp.isPointInFill(sp)) continue; n++; const s = 1.6 + rnd() * 1.8, a = rnd() * 180;
      const b = mk('g', { transform: `translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${a.toFixed(0)}) scale(${s.toFixed(2)})` }, gDead);
      mk('path', { d: 'M-2.2,0 L2.2,0', stroke: '#f6f1e6', 'stroke-width': 0.55, 'stroke-linecap': 'round' }, b);
      for (const dx of [-1.4, -0.5, 0.4, 1.3]) mk('path', { d: `M${dx},0 q0.5,-1.3 0.1,-1.9 M${dx},0 q0.5,1.3 0.1,1.9`, fill: 'none', stroke: '#f6f1e6', 'stroke-width': 0.38, 'stroke-linecap': 'round' }, b);
      mk('path', { d: 'M-2.2,0 L2.2,0', stroke: '#6b5f50', 'stroke-width': 0.14, opacity: 0.8 }, b); }
  }
  // 往后双月内海北边那一片圆海：这时候是一个干的浅坑，长草，只留一圈坑沿
  { const cx = 1338, cy = 948, rx = 52, ry = 82; const g = mk('g', { id: 'siyuNorthPit', opacity: 0.55 }, gGrass);
    for (let k = 0; k < 90; k++) { const a = k / 90 * Math.PI * 2; const x1 = cx + Math.cos(a) * rx, y1 = cy + Math.sin(a) * ry; const x2 = cx + Math.cos(a) * (rx - 3.6 - (k % 3)), y2 = cy + Math.sin(a) * (ry - 3.6 - (k % 3)); mk('line', { x1, y1, x2, y2, stroke: '#8d7f66', 'stroke-width': 0.5 }, g); }
    mk('ellipse', { cx, cy, rx, ry, fill: 'none', stroke: '#8d7f66', 'stroke-width': 0.6 }, g); }
  // 南界：死域北沿那一条，暗红的虚线
  { const sm = (pts) => { let d = `M${pts[0][0]},${pts[0][1]}`; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2; d += ` C${(p1[0] + (p2[0] - p0[0]) / 6).toFixed(1)},${(p1[1] + (p2[1] - p0[1]) / 6).toFixed(1)} ${(p2[0] - (p3[0] - p1[0]) / 6).toFixed(1)},${(p2[1] - (p3[1] - p1[1]) / 6).toFixed(1)} ${p2[0]},${p2[1]}`; } return d; };
    const d = sm(SL); const vb = document.getElementById('viewbox'); const gl = mk('g', { id: 'siyuNanjie' }, null); vb.insertBefore(gl, document.getElementById('rivers'));
    mk('path', { d, fill: 'none', stroke: '#f4ece2', 'stroke-width': 2.6, opacity: 0.6, 'stroke-linecap': 'round' }, gl);
    mk('path', { d, fill: 'none', stroke: '#8a2f28', 'stroke-width': 1.1, 'stroke-dasharray': '5 2.4', opacity: 0.85, 'stroke-linecap': 'round' }, gl); }
  // 落星洼这时候是干的，往后双月海门那一道出海的河（568）没有水：河藏掉，画一道干河床
  { const rv = pack.rivers.find((r) => r && r.i === 568); if (rv) { const pts = []; for (const c of rv.cells || []) if (c >= 0 && C.p[c]) pts.push(C.p[c]); const m = C.p[rv.mouth]; if (m) pts.push(m);
      if (pts.length > 2) { const d = 'M' + pts.map((p) => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join('L'); mk('path', { d, fill: 'none', stroke: '#e9e1cf', 'stroke-width': 2.2, opacity: 0.45, 'stroke-linejoin': 'round' }, gDead); mk('path', { d, fill: 'none', stroke: '#7d7466', 'stroke-width': 1, 'stroke-dasharray': '2 2', opacity: 0.75, 'stroke-linejoin': 'round' }, gDead); } } }
  if (OPT.sand && sandIn.length) {
    const isIn = new Uint8Array(C.i.length); for (const i of sandIn) isIn[i] = 1;
    let ring = sandIn.filter((i) => C.c[i].some((n) => !isIn[n] && C.h[n] >= 20 && C.p[n][1] < C.p[i][1] - 2.5 && Math.abs(C.p[n][0] - C.p[i][0]) < 9)); const glass = new Set(ring);
    for (let k = 0; k < 2; k++) { const nx = []; for (const i of ring) for (const n of C.c[i]) if (isIn[n] && !glass.has(n) && C.p[n][1] < 1150) { glass.add(n); nx.push(n); } ring = nx; }
    const gl = [...glass].filter((i) => C.p[i][1] < 1180);
    const dG = pathOf(gl); const gG = mk('g', { id: 'siyuGlass', mask: 'url(#land)' }, null); gDead.parentNode.insertBefore(gG, gDead.nextSibling);
    mk('path', { d: pathOf(sandIn), fill: '#8f8a84', stroke: '#8f8a84', 'stroke-width': 0.6, opacity: OPT.sandWash === undefined ? 0.16 : OPT.sandWash }, gG);
    mk('path', { d: dG, fill: '#c9d3cf', stroke: '#c9d3cf', 'stroke-width': 0.6, 'stroke-linejoin': 'round', opacity: 0.85 }, gG);
    const sh = mk('pattern', { id: 'siyuGlassSheen', width: 9, height: 9, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(-28)' }, pd); mk('rect', { width: 9, height: 9, fill: 'none' }, sh); mk('path', { d: 'M0,2 L9,2 M0,6.5 L9,6.5', stroke: '#ffffff', 'stroke-width': 0.6, opacity: 0.7 }, sh); mk('path', { d: 'M0,4 L9,4', stroke: '#6f8790', 'stroke-width': 0.25, opacity: 0.6 }, sh);
    mk('path', { d: dG, fill: 'url(#siyuGlassSheen)' }, gG);
    window.__siyuGlassN = gl.length; }
  mk('path', { id: 'siyuProbeDead', d: dRim + dDead, fill: '#000', opacity: 0 }, gDead);
  mk('path', { id: 'siyuProbeGrass', d: pathOf(grass), fill: '#000', opacity: 0 }, gGrass);
  if (OPT.sand) mk('path', { id: 'siyuProbeSand', d: pathOf(sandIn), fill: '#000', opacity: 0 }, gDead);
  window.__siyuHideIcons = () => {
    const pd2 = document.getElementById('siyuProbeDead'), pg = document.getElementById('siyuProbeGrass'), pd3 = document.getElementById('siyuProbeSand'); const p2 = document.getElementById('map').createSVGPoint(); let n = 0;
    { const r = document.getElementById('river568'); if (r) r.style.display = 'none'; }
    for (const u of document.querySelectorAll('#terrain use')) {
      if (u.style.display === 'none') continue; const h = u.getAttribute('href');
      p2.x = +u.getAttribute('x') + (+u.getAttribute('width')) / 2; p2.y = +u.getAttribute('y') + (+u.getAttribute('height')) / 2;
      if (p2.y < 860) continue;
      if (/dune|cactus|deadTree|swamp|deciduous|conifer|acacia|palm|grass/.test(h) && pd2.isPointInFill(p2)) { u.style.display = 'none'; n++; continue; }
      if (OPT.sand && /cactus|deadTree|swamp|deciduous|conifer|acacia|palm|grass/.test(h) && pd3 && pd3.isPointInFill(p2)) { u.style.display = 'none'; n++; continue; }
      if (/dune|cactus/.test(h) && pg.isPointInFill(p2)) { u.style.display = 'none'; n++; }
    }
    return n;
  };
  return `草 ${grass.length}，死域北沿 ${rim.length}，死域 ${dead.length}，沙海 ${sandIn.length}，玻璃 ${window.__siyuGlassN || 0}，藏符号 ${window.__siyuHideIcons()}`;
})();
