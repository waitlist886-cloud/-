(() => {
  const C = pack.cells, F = pack.features;
  const W = 2200, H = 1400, G = 5, gw = W / G, gh = H / G;
  // 每 5 格一个方块，记海（海水，不算湖）、陆
  const sea = new Uint8Array(gw * gh), land = new Uint8Array(gw * gh);
  let area = { land: 0, lake: 0, sea: 0 }, wsum = { land: 0, all: 0 };
  for (let i = 0; i < C.i.length; i++) {
    const f = F[C.f[i]], isLake = f && f.type === 'lake', isLand = C.h[i] >= 20 && !isLake;
    const a = C.area[i];
    if (isLand) area.land += a; else if (isLake) area.lake += a; else area.sea += a;
    const lat = 80 - 160 * C.p[i][1] / H, w = Math.cos(lat * Math.PI / 180);
    wsum.all += a * w; if (isLand) wsum.land += a * w;
  }
  for (let gy = 0; gy < gh; gy++) for (let gx = 0; gx < gw; gx++) {
    const x = gx * G + G / 2, y = gy * G + G / 2;
    let best = -1, bd = 1e9; const k = Math.floor(x / 12) + ',' + Math.floor(y / 12);
    for (const i of (window.__cellGrid && window.__cellGrid[k]) || []) { const d = (C.p[i][0] - x) ** 2 + (C.p[i][1] - y) ** 2; if (d < bd) { bd = d; best = i; } }
    if (best < 0) continue;
    const f = F[C.f[best]], isLake = f && f.type === 'lake';
    if (C.h[best] < 20 && !isLake) sea[gy * gw + gx] = 1; else if (C.h[best] >= 20 && !isLake) land[gy * gw + gx] = 1;
  }
  // 离海多远：从所有海的方块往外走（8 邻，斜走算 1.414）
  const dist = new Float32Array(gw * gh).fill(1e9); const q = [];
  for (let i = 0; i < gw * gh; i++) if (sea[i]) { dist[i] = 0; q.push(i); }
  // 简单的 Dijkstra 近似：多轮松弛
  for (let it = 0; it < 4; it++) {
    for (let gy = 0; gy < gh; gy++) for (let gx = 0; gx < gw; gx++) { const i = gy * gw + gx; for (const [dx, dy, c] of [[-1, 0, 1], [0, -1, 1], [-1, -1, 1.414], [1, -1, 1.414]]) { const nx = gx + dx, ny = gy + dy; if (nx < 0 || ny < 0 || nx >= gw) continue; const j = ny * gw + nx; if (dist[j] + c < dist[i]) dist[i] = dist[j] + c; } }
    for (let gy = gh - 1; gy >= 0; gy--) for (let gx = gw - 1; gx >= 0; gx--) { const i = gy * gw + gx; for (const [dx, dy, c] of [[1, 0, 1], [0, 1, 1], [1, 1, 1.414], [-1, 1, 1.414]]) { const nx = gx + dx, ny = gy + dy; if (nx >= gw || ny >= gh || nx < 0) continue; const j = ny * gw + nx; if (dist[j] + c < dist[i]) dist[i] = dist[j] + c; } }
  }
  let far = 0, farAt = null; const bins = [0, 0, 0, 0, 0]; let nl = 0;
  for (let i = 0; i < gw * gh; i++) if (land[i]) { nl++; const d = dist[i] * G; if (d > far) { far = d; farAt = [(i % gw) * G, Math.floor(i / gw) * G]; } const b = d < 50 ? 0 : d < 100 ? 1 : d < 200 ? 2 : d < 300 ? 3 : 4; bins[b]++; }
  const at = (x, y) => Math.round(dist[Math.floor(y / G) * gw + Math.floor(x / G)] * G);
  const tot = W * H;
  return JSON.stringify({
    landPct: +(100 * area.land / tot).toFixed(1), lakePct: +(100 * area.lake / tot).toFixed(1), seaPct: +(100 * area.sea / tot).toFixed(1),
    landPctLatWeighted: +(100 * wsum.land / wsum.all).toFixed(1),
    farthestFromSea_px: Math.round(far), farAt,
    landByDistance_px: { '<50': +(100 * bins[0] / nl).toFixed(1), '50-100': +(100 * bins[1] / nl).toFixed(1), '100-200': +(100 * bins[2] / nl).toFixed(1), '200-300': +(100 * bins[3] / nl).toFixed(1), '>300': +(100 * bins[4] / nl).toFixed(1) },
    arcadia: at(1100, 672), jinyuan: at(1518, 742), jinmie: at(616, 714), xingguan: at(1386, 560),
  });
})();
