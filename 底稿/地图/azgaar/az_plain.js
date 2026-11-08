// 整张图 1:1 摆好（2200×1400，缩放归一），关掉1001年那几层：地名、城镇图标、国界线、路网
(() => {
  const svg = document.getElementById('map');
  svg.setAttribute('width', 2200);
  svg.setAttribute('height', 1400);
  document.getElementById('viewbox').setAttribute('transform', 'translate(0 0) scale(1)');
  for (const id of ['labels', 'burgIcons', 'borders', 'routes', 'anchors']) {
    const g = document.getElementById(id);
    if (g) g.style.display = 'none';
  }
  // 页面上 Azgaar 自己的面板、按钮都藏掉
  for (const el of document.querySelectorAll('body > *:not(#map)')) el.style.visibility = 'hidden';
  document.body.style.background = 'transparent';
  svg.style.position = 'fixed'; svg.style.left = '0'; svg.style.top = '0';
  return 'ok ' + svg.getAttribute('width') + 'x' + svg.getAttribute('height');
})();
