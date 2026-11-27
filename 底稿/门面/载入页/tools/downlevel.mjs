// 11-27：把 html 里内联脚本的 ?. 和 ?? 改成老写法（只动这两样）。make_old1001.py 出了 old1001.html 以后跑一回。
// 用法：临时目录 npm install @babel/core@7.24.4 @babel/plugin-transform-optional-chaining@7.24.1 @babel/plugin-transform-nullish-coalescing-operator@7.24.1，拷过去 node downlevel.mjs <in.html> <out.html>；再在头一个 <script> 前补 flat、flatMap、fromEntries、replaceChildren 的兜底（见 old1001.html 头上那一段）。
// 把一份 html 里内联脚本的 ?. 和 ?? 改成老内核认得的写法（只动这两样，别的原样）。node downlevel.mjs <in.html> <out.html>
import fs from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const babel = require('@babel/core');
const [inp, out] = process.argv.slice(2);
let s = fs.readFileSync(inp, 'utf8'), n = 0;
s = s.replace(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi, (all, attrs, code) => {
  if (/\bsrc=/.test(attrs) || /type=["']?(application\/(ld\+)?json|text\/template)/i.test(attrs)) return all;
  if (!/\?\.|\?\?/.test(code)) return all;
  const r = babel.transformSync(code, { babelrc: false, configFile: false, compact: false, retainLines: true, sourceType: 'script', plugins: [require.resolve('@babel/plugin-transform-optional-chaining'), require.resolve('@babel/plugin-transform-nullish-coalescing-operator')], parserOpts: { sourceType: 'script' }, generatorOpts: { retainLines: true, jsescOption: { minimal: true } } });
  if (r.code === code) return all;
  n++;
  return '<script' + attrs + '>' + r.code.replace(/<\/script/gi, '<\/script') + '</script>';
});
fs.writeFileSync(out, s);
console.log('改了', n, '段脚本');
