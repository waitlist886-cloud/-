// 点最新一条的玉牒页签，等转场走完，停在这一页开头；再量一下有没有东西出框
(async () => {
  const all = [...document.querySelectorAll('.rili-markdown-renderer')];
  const last = all[all.length - 1];
  const inp = last.querySelector('.t-ming input');
  inp.click();
  await new Promise((r) => setTimeout(r, 300));
  for (const x of document.getAnimations()) if (x.timeline === document.timeline) x.finish();
  await new Promise((r) => setTimeout(r, 200));
  window.lay();
  const c = document.getElementById('conversation');
  const pane = last.querySelector('.p-ming');
  c.scrollTop += pane.getBoundingClientRect().top - c.getBoundingClientRect().top - 130;
  await new Promise((r) => setTimeout(r, 200));
  const w = innerWidth;
  const over = [...last.querySelectorAll('*')].filter((e) => { const b = e.getBoundingClientRect(); return b.width > 0 && b.right > w - 6 && getComputedStyle(e).display !== 'none'; }).slice(0, 5).map((e) => e.className || e.tagName);
  return JSON.stringify({ paneDisplay: getComputedStyle(pane).display, pane: pane.getBoundingClientRect().width, over });
})()
