(() => {
  const sh = [...document.querySelectorAll('.custom-styles')].find((e) => e.querySelector('#conversation'));
  const cs = getComputedStyle(sh);
  const v = (n) => cs.getPropertyValue(n).trim().replace(/^url\("?[^"]*\/([^/"]+)"?\)$/, '$1').slice(0, 44);
  const layers = getComputedStyle(sh, '::before').backgroundImage.split(/,\s*(?=url|none|linear)/).map((s) => (s.match(/([a-z_0-9]+)\.webp/) || [0, s.slice(0, 8)])[1]);
  const left = getComputedStyle(sh.querySelector(':scope > div'), '::before').backgroundImage;
  const nav = document.querySelector('nav.custom-styles');
  const main = document.querySelector('main');
  const eras = [...document.querySelectorAll('.sz-era')].map((e) => e.className.replace('sz-era era-', ''));
  const tabs = [...document.querySelectorAll('.sz-tabs')].map((n) => [...n.querySelectorAll('b')].map((b) => b.textContent).join(' '));
  const heads = [...document.querySelectorAll('.p-panel .sz-pane-head b')].map((b) => b.textContent);
  return JSON.stringify({
    回复里的纪元: eras,
    两扇: [v('--fm-l'), v('--fm-r')], 楣座: [v('--fm-top'), v('--fm-bot')], 手枪: [v('--fm-hl'), v('--fm-hr'), v('--fm-lance')],
    顶层图: layers, 左扇图: (left.match(/([a-z_0-9]+)\.webp/) || [0, 'none'])[1], 字色: v('--fm-ink'), 金色: v('--fm-acc'), 徽记: v('--fm-emblem').length > 10, bb: v('--fm-bb'),
    顶栏: getComputedStyle(nav).backgroundColor, main: getComputedStyle(main).backgroundColor,
    页签: tabs, 面板题: heads,
  }, null, 1);
})()
