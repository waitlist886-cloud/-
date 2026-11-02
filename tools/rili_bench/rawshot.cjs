const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [txt, out, n] = process.argv.slice(2);
  const lines = fs.readFileSync(txt, 'utf8').split('\n').slice(0, Number(n || 60)).map(l => l.length > 46 ? l.slice(0, 46) + '…' : l);
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const html = `<html><head><meta charset="utf-8"></head><body style="margin:0;background:#101216;color:#cfd6e0;font:13px/1.55 'Noto Sans Mono CJK SC','Noto Sans CJK SC',monospace;padding:14px 12px;width:366px">${lines.map(l => `<div style="white-space:pre;overflow:hidden;${l.startsWith('§') ? 'color:#e6c780' : ''}">${esc(l) || '&nbsp;'}</div>`).join('')}</body></html>`;
  fs.writeFileSync(out.replace(/\.png$/, '.html'), html);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await p.goto('file://' + out.replace(/\.png$/, '.html')); await p.waitForTimeout(400);
  await p.screenshot({ path: out, clip: { x: 0, y: 0, width: 390, height: 844 } }); await b.close();
})();
