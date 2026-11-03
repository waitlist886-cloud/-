// 《大旻长夜》日里版面板样张：最新一条的行卷、各面板逐块点开截图，再往上看一眼旧回复
export default async ({ page, shot, scrollTo, prefix }) => {
  const last = async (sel) => page.evaluate((sel) => { const a = [...document.querySelectorAll('.is-assistant')].pop(); return !!a.querySelector(sel); }, sel);
  const open = async (cls) => page.evaluate((cls) => { const a = [...document.querySelectorAll('.is-assistant')].pop(); const d = a.querySelector('.' + cls); if (d) d.open = true; }, cls);
  const to = async (sel, off = 90) => page.evaluate(([sel, off]) => { const a = [...document.querySelectorAll('.is-assistant')].pop(); const el = a.querySelector(sel); if (!el) return; el.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= off; }, [sel, off]);
  await to('.dm-p-shu'); await page.waitForTimeout(250); await shot('1-开卷');
  await to('.dm-scroll'); await page.waitForTimeout(250); await shot('2-行卷');
  await to('.dm-scroll .dm-check, .dm-p-ming', 160); await page.waitForTimeout(250); await shot('3-收卷与玉牒');
  await open('dm-p-ming'); await to('.dm-p-ming'); await page.waitForTimeout(250); await shot('4-命主玉牒');
  await to('.dm-sec-skill'); await page.waitForTimeout(250); await shot('5-武藏天赋');
  await open('dm-p-jian'); await to('.dm-p-jian'); await page.waitForTimeout(250); await shot('6-群英照鉴');
  await to('.dm-p-wen'); await page.waitForTimeout(250); await shot('7-天下风闻');
  await to('.dm-sec-actions', 120); await page.waitForTimeout(250); await shot('8-行止抉择');
  // 点一条行策，看输入框
  await page.evaluate(() => { const a = [...document.querySelectorAll('.is-assistant')].pop(); a.querySelector('.dm-act').dispatchEvent(new MouseEvent('click', { bubbles: true })); });
  await page.waitForTimeout(250); await shot('9-点行策填进输入框');
  await to('.dm-p-li'); await page.waitForTimeout(250); await shot('10-天时经纬');
  await open('dm-p-cang'); await to('.dm-p-cang'); await page.waitForTimeout(250); await shot('11-光阴藏卷');
  const n = await page.evaluate(() => document.querySelectorAll('.is-assistant').length);
  if (n > 1) { await page.evaluate(() => { const a = document.querySelectorAll('.is-assistant')[0]; a.querySelector('.dm-scroll').scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 90; }); await page.waitForTimeout(250); await shot('12-旧回复'); }
  console.log('输入框：', await page.evaluate(() => document.querySelector('#chat-input').value));
};
