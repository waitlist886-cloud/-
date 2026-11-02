export default async ({ page, shot }) => {
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 60; }); await page.waitForTimeout(400);
  const b = await page.evaluate(() => { const r = document.querySelector('.sz-bars').getBoundingClientRect(); return { x: r.x - 10, y: r.y - 10, width: r.width + 20, height: r.height + 20 }; });
  await shot('bars', b);
  console.log(await page.evaluate(() => [...document.querySelectorAll('.sz-trk')].map(t => { const a = getComputedStyle(t, '::after').width; return t.getBoundingClientRect().width.toFixed(0) + '→' + a; }).join(' ')));
};
