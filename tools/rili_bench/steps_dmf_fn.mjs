// 存档轮在最后：上一条叙事轮照旧带页签、推演、行止
export default async ({ page, shot }) => {
  await page.evaluate(() => { const c = document.querySelector('#conversation'); c.scrollTop = c.scrollHeight; }); await page.waitForTimeout(400); await shot('1存档');
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].filter((r) => r.querySelector('.dm-run:not(.dm-fn)')).pop(); r.querySelector('.dm-tabs').scrollIntoView({ block: 'end' }); document.querySelector('#conversation').scrollTop += 60; }); await page.waitForTimeout(400); await shot('2上一条叙事');
  console.log(await page.evaluate(() => JSON.stringify([...document.querySelectorAll('.rili-markdown-renderer')].map((r) => ({ fn: !!r.querySelector('.dm-fn'), tabs: r.querySelector('.dm-tabs') ? getComputedStyle(r.querySelector('.dm-tabs')).display : '-', hud: r.querySelector('details.dm-hud') ? getComputedStyle(r.querySelector('details.dm-hud')).display : '-' })))));
};
