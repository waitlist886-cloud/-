// 第四版大框样张·手机：最新一条开头、读到一半（页签贴在框底）、分支、点面板的转场一帧、面板、背包
export default async ({ page, shot }) => {
  const conv = async (fn) => { await page.evaluate(fn); await page.waitForTimeout(450); };
  const freeze = async (t) => page.evaluate((t) => { document.getAnimations().forEach((a) => { a.pause(); a.currentTime = t; }); }, t);
  const finish = async () => { await page.evaluate(() => document.getAnimations().forEach((a) => a.finish())); await page.waitForTimeout(250); };
  await conv(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 100; }); await shot('1top');
  await conv(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop += 600; }); await shot('2mid');
  await conv(() => { const c = document.querySelector('#conversation'); c.scrollTop = c.scrollHeight; }); await shot('3end');
  await page.evaluate(() => { [...document.querySelectorAll('.t-panel')].pop().click(); }); await freeze(420); await shot('4t420');
  await finish(); await conv(() => { const p = [...document.querySelectorAll('.p-panel')].pop(); p.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 90; }); await shot('5panel');
  await page.evaluate(() => { [...document.querySelectorAll('.t-bag')].pop().click(); }); await finish();
  await conv(() => { const p = [...document.querySelectorAll('.p-bag')].pop(); p.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 90; }); await shot('6bag');
};
