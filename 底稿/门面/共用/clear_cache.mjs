// 清掉无头 Chrome 的 HTTP 缓存（11-15）。本地的小服务器不带不许缓存的头，页面里的 data/*.json 改了以后，
// 同一个 Chrome 再开页面可能还拿旧的那一份（迷宫纪那一本改了名单以后走查就这样数岔过）。改了数据、重跑走查以前先清一遍。
//   node 底稿/门面/共用/clear_cache.mjs 9335 9336 9337 9341
for (const port of process.argv.slice(2)) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    const ws = new WebSocket(list.find((t) => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
    const done = new Promise((r) => { ws.onmessage = (e) => { if (JSON.parse(e.data).id === 2) r(); }; });
    ws.send(JSON.stringify({ id: 1, method: 'Network.enable' }));
    ws.send(JSON.stringify({ id: 2, method: 'Network.clearBrowserCache' }));
    await done; ws.close();
    console.log(port, '清了');
  } catch (e) { console.log(port, '没连上', String(e).slice(0, 80)); }
}
