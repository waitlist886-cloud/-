const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [out, title, ...pairs] = process.argv.slice(2);
  const items = pairs.map(p => p.split('='));
  const html = `<html><head><meta charset="utf-8"></head><body style="margin:0;background:#0b0c10;font-family:'Noto Sans CJK SC',sans-serif;color:#ddd">
  <div style="padding:14px 18px 4px;font-size:22px;letter-spacing:.1em">${title}</div>
  <div style="display:flex;gap:14px;padding:10px 18px 18px">${items.map(([lab, f]) => `<div style="width:390px"><div style="font-size:17px;padding:6px 2px;color:#c9c3b4">${lab}</div><img src="file://${f}" style="width:390px;border:1px solid #333"></div>`).join('')}</div></body></html>`;
  const tmp = out.replace(/\.png$/, '.html'); fs.writeFileSync(tmp, html);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 18 + items.length * 404 + 18, height: 400 } });
  await p.goto('file://' + tmp); await p.waitForTimeout(600);
  await p.screenshot({ path: out, fullPage: true }); await b.close();
})();
