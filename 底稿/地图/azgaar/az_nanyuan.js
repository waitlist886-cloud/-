// 月银纪的南原（第三版）：神陨沙海那一大片沙地和双月内海（落星洼）都还没有，是一片草原。
// 在 az_reset.sh 摆好、碧湾那一角改过（az_biwan_run.js）的图上跑。
//   沙地那一片（离南边海岸三格以内、y 1150 以南的那一溜留沙，末年南边的沙往北推了几十里）、双月内海的湖底、湖岸那一圈
//   照 Azgaar 草原的样子画：先铺陆地底色，再照群系那一层的不透明度（0.6）叠草原色，跟别处的草原一个颜色
//   湖从水遮罩、陆地遮罩、湖那一组里拿掉
//   地形符号：Azgaar 有时候会整层重画，所以藏符号写成 window.__hideMoonIcons()，截图以前再跑一回
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  const C = pack.cells, P = pack.vertices.p;
  for (const id of ['moonNanyuan']) { const o = document.getElementById(id); if (o) o.remove(); }
  let seed = -1, best = 1e9;
  for (let i = 0; i < C.i.length; i++) { if (C.biome[i] !== 1) continue; const d = (C.p[i][0] - 900) ** 2 + (C.p[i][1] - 1080) ** 2; if (d < best) { best = d; seed = i; } }
  const sand = new Uint8Array(C.i.length); const st = [seed]; sand[seed] = 1;
  while (st.length) { const i = st.pop(); for (const n of C.c[i]) if (!sand[n] && C.biome[n] === 1) { sand[n] = 1; st.push(n); } }
  const isSea = (n) => C.h[n] < 20 && !(pack.features[C.f[n]] && pack.features[C.f[n]].type === 'lake');
  const dsea = new Int16Array(C.i.length).fill(-1); let q = [];
  for (let i = 0; i < C.i.length; i++) if (sand[i] && C.c[i].some(isSea)) { dsea[i] = 0; q.push(i); }
  for (let d = 1; d <= 3; d++) { const nq = []; for (const i of q) for (const n of C.c[i]) if (sand[n] && dsea[n] < 0) { dsea[n] = d; nq.push(n); } q = nq; }
  const lakeF = (pack.features[9] && pack.features[9].type === 'lake') ? 9 : -1;
  const lake = new Uint8Array(C.i.length); for (let i = 0; i < C.i.length; i++) if (C.f[i] === lakeF) lake[i] = 1;
  const shore = new Uint8Array(C.i.length);
  for (let i = 0; i < C.i.length; i++) if (lake[i]) for (const n of C.c[i]) if (!lake[n] && C.h[n] >= 20) { shore[n] = 1; for (const m of C.c[n]) if (!lake[m] && C.h[m] >= 20) shore[m] = 1; }
  const cells = []; let kept = 0;
  for (let i = 0; i < C.i.length; i++) {
    if (sand[i] && dsea[i] >= 0 && C.p[i][1] > 1150) { kept++; continue; }
    if (sand[i] || lake[i] || shore[i]) { cells.push(i); continue; }
    // 双月内海四周、沙地和湖之间那一圈冷荒漠（群系 2）月银纪也是南原的草；南边沿海那一溜照旧
    const [x, y] = C.p[i];
    if (C.biome[i] === 2 && C.h[i] >= 20 && C.h[i] <= 55 && x > 880 && x < 1480 && y > 880 && y < 1190 && !(y > 1150 && C.c[i].some(isSea))) cells.push(i);
  }
  const d = cells.map((i) => 'M' + C.v[i].map((v) => P[v][0].toFixed(2) + ',' + P[v][1].toFixed(2)).join('L') + 'Z').join('');
  for (const u of [...document.querySelectorAll('#land use, #water use, #lakes use')]) { const h = u.getAttribute('href') || u.getAttribute('xlink:href'); if (h === `#feature_${lakeF}`) { if (u.closest('#lakes')) u.style.display = 'none'; else u.remove(); } }
  const biomes = document.getElementById('biomes');
  const op = +(biomes.getAttribute('opacity') || 0.6);
  const grass = document.getElementById('biome4').getAttribute('fill');
  const land = document.getElementById('landmass').getAttribute('fill');
  const g = mk('g', { id: 'moonNanyuan', mask: 'url(#land)' }, null);
  biomes.parentNode.insertBefore(g, biomes.nextSibling);
  mk('path', { d, fill: land, stroke: land, 'stroke-width': 0.6, 'stroke-linejoin': 'round' }, g);
  const gg = mk('g', { opacity: op }, g);
  mk('path', { d, fill: grass, stroke: grass, 'stroke-width': 0.6, 'stroke-linejoin': 'round' }, gg);
  mk('path', { id: 'moonNanyuanProbe', d, fill: '#000', opacity: 0 }, g);
  window.__hideMoonIcons = () => {
    const probe = document.getElementById('moonNanyuanProbe'); const pt = document.getElementById('map').createSVGPoint(); let n = 0;
    for (const u of document.querySelectorAll('#terrain use')) {
      if (!/dune|cactus|deadTree|swamp|deciduous|conifer|acacia|palm/.test(u.getAttribute('href'))) continue;
      pt.x = +u.getAttribute('x') + (+u.getAttribute('width')) / 2; pt.y = +u.getAttribute('y') + (+u.getAttribute('height')) / 2;
      if (probe.isPointInFill(pt)) { u.style.display = 'none'; n++; }
    }
    return n;
  };
  const hid = window.__hideMoonIcons();
  return `南原格子 ${cells.length}（沙 ${sand.reduce((a, b) => a + b, 0)}，南边留沙 ${kept}，湖 ${lake.reduce((a, b) => a + b, 0)}，湖岸 ${shore.reduce((a, b) => a + b, 0)}），藏了符号 ${hid}，地形符号一共 ${document.getElementById('terrain').children.length}`;
})();
