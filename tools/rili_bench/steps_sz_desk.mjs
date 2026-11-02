// 手札样张·宽屏：整张手札对着构想图截一张，再点开面板截一张
export default async ({ page, shot }) => {
  const top = async (off) => { await page.evaluate((off) => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= off; }, off); await page.waitForTimeout(400); };
  await top(Number(process.env.SZ_OFF || 96)); await shot('1whole');
  await page.evaluate(() => { [...document.querySelectorAll('.t-panel')].pop().click(); }); await page.waitForTimeout(300);
  await page.evaluate(() => { const p = [...document.querySelectorAll('.p-panel')].pop(); p.scrollIntoView({ block: 'center' }); }); await page.waitForTimeout(400); await shot('2pane');
  await page.evaluate(() => { [...document.querySelectorAll('.t-party')].pop().click(); }); await page.waitForTimeout(300);
  await page.evaluate(() => { const p = [...document.querySelectorAll('.p-party')].pop(); p.scrollIntoView({ block: 'center' }); }); await page.waitForTimeout(400); await shot('3party');
  await page.evaluate(() => { [...document.querySelectorAll('.sz-x')].pop().click(); document.querySelector('.sz-head').click(); }); await page.waitForTimeout(300);
  await top(96); await shot('4hud');
};
