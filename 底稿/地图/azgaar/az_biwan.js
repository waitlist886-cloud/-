// 月银纪的西南一角（第二版，照 月银纪·风土｜地图的几层：碧湾和它北边的盐原往后连成一片咸水海，是赤盐内海，潮宫沉在底下）
//   碧湾＝今天赤盐内海那一整片水面，加上朝西南出海的那一道口子（BAY_D，bay_shape.py 算的），潮宫在湾心
//   盐原＝湾北边那一片地（盐井城在它北沿），白的盐壳，中间一片盐沼（约2700年萨尔缇在盐原上聚成以后核心退成盐沼）
// Azgaar 的遮罩：陆地遮罩里湖本来就是黑的，口子再挖黑；水遮罩里加白；湖那一组里的那一个藏掉，海自己露出来
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const mk = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };
  if (document.getElementById('bay_moon')) return '已经改过';
  const fp = document.getElementById('featurePaths');
  mk('path', { id: 'bay_moon', d: 'BAY_D' }, fp);
  const defs = fp.closest('defs');
  const land = document.getElementById('land'), water = document.getElementById('water');
  mk('use', { href: '#bay_moon', fill: 'black' }, land);
  mk('use', { href: '#bay_moon', fill: 'white' }, water);
  const box = { maskUnits: 'userSpaceOnUse', x: 0, y: 0, width: 2200, height: 1400 };
  // 湾＝口子加整片湖
  const nobay = mk('mask', Object.assign({ id: 'nobay' }, box), defs);
  mk('rect', { x: 0, y: 0, width: 2200, height: 1400, fill: 'white' }, nobay);
  mk('use', { href: '#bay_moon', fill: 'black' }, nobay);
  mk('use', { href: '#feature_10', fill: 'black' }, nobay);
  const landside = mk('mask', Object.assign({ id: 'landside' }, box), defs);
  mk('use', { href: '#feature_2', fill: 'white' }, landside);
  mk('use', { href: '#bay_moon', fill: 'black' }, landside);
  mk('use', { href: '#feature_10', fill: 'black' }, landside);
  const bayclip = mk('clipPath', { id: 'bayclip' }, defs);
  mk('use', { href: '#bay_moon' }, bayclip);
  mk('use', { href: '#feature_10' }, bayclip);
  // 湖那一组里的赤盐内海藏掉（湖的岸线跟着没了）
  for (const u of document.querySelectorAll('#lakes use')) { const h = u.getAttribute('href') || u.getAttribute('xlink:href'); if (h === '#feature_10') u.style.display = 'none'; }
  // 海岸线：原来的岸线在湾里藏掉，新岸照海岸线的样式描（只露陆地那一边）
  const sea = document.getElementById('sea_island');
  for (const u of sea.querySelectorAll('use')) u.setAttribute('mask', 'url(#nobay)');
  mk('use', { href: '#bay_moon', fill: 'none', mask: 'url(#landside)' }, sea);
  mk('use', { href: '#feature_10', fill: 'none', mask: 'url(#landside)' }, sea);
  // 海的浅色层：湾里叠三层，近岸再叠三道
  const ol = document.getElementById('oceanLayers');
  const g = mk('g', { 'clip-path': 'url(#bayclip)' }, ol);
  const gf = mk('g', { opacity: 0.24 }, g);
  for (const id of ['#bay_moon', '#feature_10']) mk('use', { href: id, fill: '#ecf2f9' }, gf);
  const noLake = mk('mask', Object.assign({ id: 'noLakeIn' }, box), defs); mk('rect', { x: 0, y: 0, width: 2200, height: 1400, fill: 'white' }, noLake); mk('use', { href: '#feature_10', fill: 'black' }, noLake);
  const noBay = mk('mask', Object.assign({ id: 'noBayIn' }, box), defs); mk('rect', { x: 0, y: 0, width: 2200, height: 1400, fill: 'white' }, noBay); mk('use', { href: '#bay_moon', fill: 'black' }, noBay);
  for (const w of [5, 10, 16]) {
    mk('use', { href: '#bay_moon', fill: 'none', stroke: '#ecf2f9', 'stroke-opacity': '0.13', 'stroke-width': w, mask: 'url(#noLakeIn)' }, g);
    mk('use', { href: '#feature_10', fill: 'none', stroke: '#ecf2f9', 'stroke-opacity': '0.13', 'stroke-width': w, mask: 'url(#noBayIn)' }, g);
  }
  // 出海那条河成了湾，藏掉
  const r = document.getElementById('river176');
  if (r) r.style.display = 'none';
  // 盐原：湾北边一片盐壳，中间一片盐沼
  const pd = mk('g', { id: 'moonSalt' }, defs);
  const sp = mk('pattern', { id: 'saltCrust', width: 3, height: 2.6, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(8)' }, pd);
  mk('rect', { width: 3, height: 2.6, fill: '#f2eee8' }, sp);
  mk('path', { d: 'M0,1.3 L0.75,0 L2.25,0 L3,1.3 L2.25,2.6 L0.75,2.6 Z', fill: 'none', stroke: '#d8ccbb', 'stroke-width': 0.22 }, sp);
  const blob = (cx, cy, rx, ry, ph) => { let d = ''; for (let a = 0; a < 360; a += 6) { const t = a * Math.PI / 180, k = 1 + 0.12 * Math.sin(3 * t + ph) + 0.07 * Math.sin(7 * t + ph * 2); d += (d ? 'L' : 'M') + (cx + Math.cos(t) * rx * k).toFixed(2) + ',' + (cy + Math.sin(t) * ry * k).toFixed(2); } return d + 'Z'; };
  const sg = mk('g', { id: 'moonSaltPlain', mask: 'url(#land)' }, null);
  const biomes = document.getElementById('biomes');
  biomes.parentNode.insertBefore(sg, biomes.nextSibling);
  mk('path', { d: blob(385, 1000, 92, 40, 0.7), fill: 'url(#saltCrust)', opacity: 0.92 }, sg);
  mk('path', { d: blob(385, 1000, 92, 40, 0.7), fill: 'none', stroke: '#b9a78f', 'stroke-width': 0.6, opacity: 0.8 }, sg);
  mk('path', { d: blob(378, 1006, 38, 15, 2.1), fill: '#e3ebe8', stroke: '#9fb3ad', 'stroke-width': 0.5 }, sg);
  for (let k = 0; k < 26; k++) { const a = k * 2.399, d = 6 + (k % 7) * 4.2; const x = 378 + Math.cos(a) * d * 0.9, y = 1006 + Math.sin(a) * d * 0.36; if ((x - 378) ** 2 / 34 ** 2 + (y - 1006) ** 2 / 13 ** 2 > 1) continue; mk('path', { d: `M${x - 1.2},${y} q0.6,-1.2 1.2,0 q0.6,-1.2 1.2,0`, fill: 'none', stroke: '#7f9a92', 'stroke-width': 0.3 }, sg); }
  // 湾里、盐原上的地形符号藏掉（Azgaar 重画以后再跑一回）
  window.__hideBayIcons = () => { const pt = document.getElementById('map').createSVGPoint(); const bay = document.getElementById('bay_moon'), lake = document.getElementById('feature_10'); let n = 0; for (const u of document.querySelectorAll('#terrain use')) { const x = +u.getAttribute('x') + (+u.getAttribute('width') || 0) / 2, y = +u.getAttribute('y') + (+u.getAttribute('height') || 0) / 2; if (x < 90 || x > 490 || y < 940 || y > 1230) continue; pt.x = x; pt.y = y; const inSalt = ((x - 385) / 98) ** 2 + ((y - 1000) / 44) ** 2 < 1; if (bay.isPointInFill(pt) || lake.isPointInFill(pt) || inSalt) { u.style.display = 'none'; n++; } } return n; };
  return 'ok，湾里和盐原上藏了地形符号 ' + window.__hideBayIcons();
})();
