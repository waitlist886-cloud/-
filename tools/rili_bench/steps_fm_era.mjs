// 大框改层次那一轮：一纪一张宽屏，最新一条开头，五纪拼一张看框和两扇
export default async ({ page, shot }) => {
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 100; });
  await page.waitForTimeout(450); await shot('1top');
};
