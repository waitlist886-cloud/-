// 手札样张·手机：头和三条、读到一半时贴在输入框上的页签、点开面板
export default async ({ page, shot }) => {
  const last = '[...document.querySelectorAll(".rili-markdown-renderer")].pop()';
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 90; }); await page.waitForTimeout(400); await shot('1top');
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop += 520; }); await page.waitForTimeout(400); await shot('2mid');
  await page.evaluate(() => { const c = [...document.querySelectorAll('.sz-choices')].pop(); c.scrollIntoView({ block: 'center' }); }); await page.waitForTimeout(400); await shot('3choices');
  await page.evaluate(() => { [...document.querySelectorAll('.t-panel')].pop().click(); }); await page.waitForTimeout(300);
  await page.evaluate(() => { const p = [...document.querySelectorAll('.p-panel')].pop(); p.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 60; }); await page.waitForTimeout(400); await shot('4pane');
};
