// 取赤盐内海（feature_10）的轮廓点和从它流出去的那几条河（端点落在湖边、另一头在湖外西边的）
(() => {
  const lake = document.getElementById('feature_10');
  const L = lake.getTotalLength(), pts = [];
  for (let s = 0; s < L; s += 0.5) { const p = lake.getPointAtLength(s); pts.push([+p.x.toFixed(2), +p.y.toFixed(2)]); }
  const bb = lake.getBBox();
  const near = (p) => p.x > bb.x - 6 && p.x < bb.x + bb.width + 6 && p.y > bb.y - 6 && p.y < bb.y + bb.height + 6;
  const rivers = [];
  for (const r of document.querySelectorAll('#rivers path')) {
    const n = r.getTotalLength(); if (!n) continue;
    const a = r.getPointAtLength(0), b = r.getPointAtLength(n);
    if ((near(a) || near(b)) && Math.min(a.x, b.x) < bb.x + 20) {
      const rp = [];
      for (let s = 0; s <= n; s += 0.5) { const p = r.getPointAtLength(s); rp.push([+p.x.toFixed(2), +p.y.toFixed(2)]); }
      rivers.push({ id: r.id, a: [a.x, a.y], b: [b.x, b.y], len: n, pts: rp });
    }
  }
  return JSON.stringify({ bbox: [bb.x, bb.y, bb.width, bb.height], lake: pts, rivers });
})();
