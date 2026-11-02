export default async ({ page, shot }) => {
  const conv = async (fn) => { await page.evaluate(fn); await page.waitForTimeout(400); };
  const finish = async () => { await page.evaluate(() => document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => a.finish())); await page.waitForTimeout(250); };
  await conv(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 100; }); await shot('1top');
  await page.evaluate(() => { [...document.querySelectorAll('.t-panel')].pop().click(); }); await page.waitForTimeout(80);
  await page.evaluate(() => document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => { a.pause(); a.currentTime = 420; })); await shot('2veil');
  await finish(); await conv(() => { const p = [...document.querySelectorAll('.p-panel')].pop(); p.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 90; }); await shot('3panel');
};
