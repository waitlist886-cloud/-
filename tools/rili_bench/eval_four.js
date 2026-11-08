// 四纪大框（11-08）：读页面上实际用了哪张图、页签写的什么字。static_bench.mjs 的 eval= 用
(async () => {
  await new Promise((r) => setTimeout(r, 2500));
  const short = (s) => (s || '').replace(/^url\("?/, '').replace(/"?\).*$/, '').split('/').pop().slice(0, 40);
  const out = [];
  for (const n of document.querySelectorAll('.sz-npc[data-portrait]')) {
    const p = n.querySelector('.sz-por');
    out.push('立绘 ' + n.dataset.portrait + ' 衣着' + (n.dataset.o || '') + ' → ' + short(getComputedStyle(p).backgroundImage) + ' 位置 ' + getComputedStyle(p).backgroundPosition.split(',')[0]);
  }
  for (const s of document.querySelectorAll('.sz-say')) {
    const f = s.querySelector('.sz-face');
    out.push('对话 ' + s.dataset.portrait + ' ' + s.dataset.em + ' → ' + short(getComputedStyle(f).backgroundImage) + ' 位置 ' + getComputedStyle(f).backgroundPosition.split(',')[0]);
  }
  for (const b of document.querySelectorAll('.sz-boss')) {
    const a = b.querySelector('.sz-boss-art');
    out.push('Boss ' + b.dataset.n + ' 阶' + (b.dataset.p || '') + ' → ' + short(getComputedStyle(b).getPropertyValue('--bart')) + ' | 显示 ' + short(a && getComputedStyle(a).backgroundImage));
  }
  for (const e of document.querySelectorAll('.sz-era')) out.push('纪元 ' + e.className + ' data-y=' + e.dataset.y);
  const tabs = [...document.querySelectorAll('.sz-tab b')].filter((b) => b.offsetParent).map((b) => b.innerText.trim());
  out.push('页签 ' + tabs.join(' '));
  const heads = [...document.querySelectorAll('.sz-pane-head b')].map((b) => b.innerText.trim()).filter(Boolean).slice(0, 8);
  out.push('页头 ' + heads.join(' / '));
  return out.join('\n');
})();
