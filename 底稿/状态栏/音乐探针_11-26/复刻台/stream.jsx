// 音乐探针本地复刻：日里那一套 正则 → react-markdown(gfm, breaks, raw) → 拦 script/iframe/object/embed/base 和 on* → React 挂载。
// 一条回复可以一段一段地长（模拟流式），也可以卸载再挂上（模拟虚拟列表滚远滚回）。
import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import rehypeRaw from 'rehype-raw';

const DROP = new Set(['script', 'iframe', 'object', 'embed', 'base']);
function sanitize() {
  const walk = (node) => {
    if (!node.children) return;
    node.children = node.children.filter((c) => !(c.type === 'element' && DROP.has(c.tagName)));
    for (const c of node.children) {
      if (c.type === 'element' && c.properties) for (const k of Object.keys(c.properties)) if (/^on/i.test(k)) delete c.properties[k];
      walk(c);
    }
  };
  return (tree) => walk(tree);
}
function applyRules(text, rules) {
  for (const r of rules) {
    if (!r.enabled) continue;
    const m = r.regex.match(/^\/([\s\S]*)\/([^/]*)$/);
    text = text.replace(new RegExp(m[1], [...m[2]].filter((f) => 'imsg'.includes(f)).join('')), r.replaceString);
  }
  return text;
}
function Msg({ raw }) {
  return (
    <div className="rili-markdown-renderer">
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} rehypePlugins={[rehypeRaw, sanitize]}>{applyRules(raw, window.RULES)}</ReactMarkdown>
    </div>
  );
}
function App() {
  const [msgs, setMsgs] = useState([]);
  window.setMsgs = setMsgs;
  return (
    <div className="custom-styles">
      <style dangerouslySetInnerHTML={{ __html: window.BCSS }} />
      {msgs.map((m, i) => (
        <div key={i} className="row" data-i={i} style={{ contain: 'layout style', padding: '6px 12px', borderBottom: '1px solid #333' }}>
          {m.show ? <Msg raw={m.raw} /> : <i>（卸载了）</i>}
        </div>
      ))}
    </div>
  );
}
createRoot(document.getElementById('root')).render(<App />);
