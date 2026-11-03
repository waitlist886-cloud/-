import React, { useState, useEffect, useRef } from 'react';
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
function Row({ m, onAction }) {
  return (
    <div className="vrow" style={{ contain: 'layout style', position: 'absolute', width: '100%', left: 0, top: 0 }}>
      <div className="w-full max-w-2xl mx-auto my-3 px-4 pb-4">
        <div className="w-full h-full flex group">
          <div className={'group flex flex-col gap-2 w-fit ' + (m.role === 'user' ? 'is-user ml-auto' : 'is-assistant')}>
            <div className="bubble">
              <div className="space-y-3">
                {m.role === 'user' ? <div className="text-sm">{m.text}</div> : (
                  <div className="text-sm rili-markdown-renderer break-words" onClick={onAction}>
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} rehypePlugins={[rehypeRaw, sanitize]}>{m.html}</ReactMarkdown>
                  </div>
                )}
              </div>
            </div>
            <div className="msg-tools"><span className="cnt"><i></i>324<i></i>912</span><span className="ics">⟳ ⧉ ⑂ ✎ ⌫ ♪</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
function App() {
  const [msgs, setMsgs] = useState(window.BENCH.messages);
  const [input, setInput] = useState('');
  const listRef = useRef(null);
  window.pushMsg = (m) => setMsgs((x) => [...x, m]);
  window.getInput = () => input;
  const onAction = (e) => {
    const a = e.target.closest && e.target.closest('[data-action]');
    if (!a || !e.currentTarget.contains(a)) return;
    const v = a.dataset.value;
    if (typeof v !== 'string') return;
    if (a.dataset.action === 'set-textinput') setInput(v);
    if (a.dataset.action === 'append-textinput') setInput((s) => s + v);
  };
  useEffect(() => {
    const list = listRef.current;
    const lay = () => { let y = 0; for (const r of list.children) { r.style.top = y + 'px'; y += r.getBoundingClientRect().height; } list.style.height = y + 'px'; };
    const ro = new ResizeObserver(lay);
    for (const r of list.children) ro.observe(r.firstElementChild);
    lay();
    return () => ro.disconnect();
  }, [msgs]);
  return (
    <div className="sidebar-wrapper">
      {window.BENCH.sidebar ? <aside className="fake-sidebar">导航</aside> : null}
      <div className="flex-1">
        <nav className="sticky top-0 w-full z-50 backdrop-blur custom-styles">
          <header><div className="h-left">▣</div><div className="h-center"></div><div className="h-right">◔ ◑ ☾</div></header>
        </nav>
        <main>
          <div className="w-full h-full relative bg-background custom-styles">
            <style dangerouslySetInnerHTML={{ __html: window.BENCH.css }} />
            <div className="flex flex-col items-center">
              <div id="conversation">
                <div className="conv-inner">
                  <div ref={listRef} style={{ contain: 'size style', overflowAnchor: 'none', flex: '0 0 auto', position: 'relative', width: '100%' }}>
                    {msgs.map((m, i) => <Row key={i} m={m} onAction={onAction} />)}
                  </div>
                </div>
              </div>
              <div className="fake-input"><div className="fake-input-inner rounded-xl bg-background"><div className="fake-chips"><button type="button" className="pl">⬡ 模组</button><button type="button" className="pl">◯ 评论 (0)</button><button type="button" className="sq">↓</button><button type="button" className="sq">▣</button><button type="button" className="sq">⌕</button><i className="vl"></i>{(window.BENCH.options || []).map((o, i) => <button key={i} type="button" onClick={() => setInput(o.value)}>{o.label}</button>)}</div><textarea id="chat-input" value={input} onChange={(e) => setInput(e.target.value)} placeholder="在此输入您的消息" /><div className="fake-tools"><span><button type="button" className="ic">⚙</button><button type="button" className="ic">ⓘ</button><button type="button" className="pill">✦ gemini-3.0-flash</button></span><span><button type="button" className="pill">实时</button><button type="button" className="send">↵</button></span></div></div></div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
createRoot(document.getElementById('root')).render(<App />);
