// 改前的外壳起一份对照页（11-25）：别的文件都转给本地服务 8774，只有 小样_外壳/shell.js、shell.css 换成 git 里某一版的。
//   node headproxy.mjs [端口=8779] [版本=HEAD]
// credcmp_1125.mjs、starpile.mjs 拿它比凭证、比池子。提交以后 HEAD 就是改后的了，那时候把版本写成改前那一个提交号。
import http from 'node:http';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const PORT = +(process.argv[2] || 8779), REV = process.argv[3] || 'HEAD';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../../../..');          // 仓库根
const show = (f) => execFileSync('git', ['-C', ROOT, 'show', `${REV}:底稿/门面/小样_外壳/${f}`], { maxBuffer: 64 << 20 });
const OLD = { 'shell.js': [show('shell.js'), 'text/javascript; charset=utf-8'], 'shell.css': [show('shell.css'), 'text/css; charset=utf-8'] };
http.createServer((req, res) => {
  const p = decodeURIComponent(req.url.split('?')[0]);
  const m = p.match(/\/小样_外壳\/(shell\.js|shell\.css)$/);
  if (m) { res.writeHead(200, { 'Content-Type': OLD[m[1]][1], 'Cache-Control': 'no-store' }); res.end(OLD[m[1]][0]); return; }
  const fwd = (left) => {          // 本地服务偶尔断一下连接，取文件的请求再试两回
    const up = http.request({ host: '127.0.0.1', port: 8774, path: req.url, method: 'GET', headers: req.headers }, (r) => { res.writeHead(r.statusCode, r.headers); r.pipe(res); });
    up.on('error', () => { if (left > 0 && !res.headersSent) setTimeout(() => fwd(left - 1), 150); else if (!res.headersSent) { res.writeHead(502); res.end('本地服务 8774 没起'); } else res.end(); });
    up.end();
  };
  fwd(2);
}).listen(PORT, '127.0.0.1', () => console.log(`改前（${REV}）的外壳在 http://localhost:${PORT}/小样_外壳/local.html`));
