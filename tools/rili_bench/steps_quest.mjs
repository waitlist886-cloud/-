// v12 主线进状态栏：截推演底座折着的那一行，再点开看一眼，再截见闻的在办
export default async ({ page, shot, scrollTo }) => {
  await scrollTo('.arc-hud-details', 'start', 'last', 90); await shot('1hud');
  const box = await page.evaluate(() => { const q = [...document.querySelectorAll('.hud-quest')].pop(); const r = q.getBoundingClientRect(); const s = getComputedStyle(q); return { y: r.y, h: r.height, color: s.color, order: s.order, display: s.display, text: q.textContent }; });
  console.log('hud-quest', JSON.stringify(box));
  await scrollTo('.f.quest', 'center', 'last'); await shot('2daily');
};
