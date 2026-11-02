export default async ({ page, shot }) => {
  const conv = async (fn) => { await page.evaluate(fn); await page.waitForTimeout(450); };
  const freeze = async (t) => page.evaluate((t) => { document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => { a.pause(); a.currentTime = t; }); }, t);
  const finish = async () => { await page.evaluate(() => document.getAnimations().filter((a) => a.timeline instanceof DocumentTimeline).forEach((a) => a.finish())); await page.waitForTimeout(250); };
  await conv(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 110; }); await shot('1latest');
  await conv(() => { const c = document.querySelector('#conversation'); c.scrollTop = c.scrollHeight; }); await shot('2end');
  await page.evaluate(() => { [...document.querySelectorAll('.t-panel')].pop().click(); }); await freeze(420); await shot('3t420');
  await finish(); await conv(() => { const p = [...document.querySelectorAll('.p-panel')].pop(); p.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 150; }); await shot('4panel');
};
