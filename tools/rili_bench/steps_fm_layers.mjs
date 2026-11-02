// 大框改层次那一轮：同一屏拆成五层各截一张透明底的（对话｜框边、窗外一圈底、两扇的影｜左右两扇｜楣、座、框角、那一颗｜平台的顶栏和输入框），再截一张合起来的
export default async ({ page, prefix }) => {
  await page.evaluate(() => { const r = [...document.querySelectorAll('.rili-markdown-renderer')].pop(); r.scrollIntoView({ block: 'start' }); document.querySelector('#conversation').scrollTop -= 110; });
  await page.waitForTimeout(450);
  await page.screenshot({ path: `${prefix}-0all.png` });
  const SH = '.custom-styles:has(#conversation)';
  const P = { shB: `${SH}::before`, shA: `${SH}::after`, inB: `${SH}>div:has(#conversation)::before`, inA: `${SH}>div:has(#conversation)::after` };
  const clear = `html,body,main,div.custom-styles,html body ${SH}:has(.sz-hud){background:transparent!important}`;
  const hide = (sels) => sels.length ? `${sels.map((x) => 'html body ' + x).join(',')}{display:none!important}` : '';
  const layers = [
    ['1dialog', [P.shB, P.shA, P.inB, P.inA], false, false],
    ['2edge', [P.shB, P.inB, P.inA], true, false],
    ['3wings', [P.shB, P.shA], true, false],
    ['4top', [P.shA, P.inB, P.inA], true, false],
    ['5platform', [P.shB, P.shA, P.inB, P.inA], true, true],
  ];
  for (const [name, hidden, hideConv, keepPlat] of layers) {
    const css = clear + hide(hidden) + (hideConv ? '#conversation{opacity:0!important}' : '') + (keepPlat ? '' : 'nav,.fake-input{visibility:hidden!important}');
    const h = await page.addStyleTag({ content: css });
    await page.waitForTimeout(250);
    await page.screenshot({ path: `${prefix}-${name}.png`, omitBackground: true });
    await h.evaluate((el) => el.remove());
  }
};
