// 日里聊天页的两道前端工序，照 2026-10-10 实测复刻（rili-chat-frontend §7）
import postcss from 'postcss';
const KEEP = new Set(['media', 'keyframes', '-webkit-keyframes', 'font-face']);
export function scopeCss(css, scope = '.custom-styles') {
  const root = postcss.parse(css);
  const dropped = {};
  root.walkAtRules((at) => {
    if (!KEEP.has(at.name)) { dropped['@' + at.name] = (dropped['@' + at.name] || 0) + 1; at.remove(); }
  });
  root.walkRules((rule) => {
    let p = rule.parent;
    while (p && p.type !== 'root') { if (p.type === 'atrule' && /keyframes$/.test(p.name)) return; p = p.parent; }
    rule.selectors = rule.selectors.map((s) => {
      s = s.trim();
      if (s.startsWith(':root')) return scope + s.slice(5);
      return scope + ' ' + s;
    });
  });
  return { css: root.toString(), dropped };
}
export function applyRules(text, rules, role = 'assistant', side = 'front-end') {
  for (const r of rules) {
    if (!r.enabled) continue;
    if (r.messageRole !== 'all' && r.messageRole !== role) continue;
    if (r.applyMode !== 'all' && r.applyMode !== side) continue;
    const m = r.regex.startsWith('/') ? r.regex.match(/^\/([\s\S]*)\/([^/]*)$/) : null;
    if (m) text = text.replace(new RegExp(m[1], [...m[2]].filter((f) => 'imsg'.includes(f)).join('')), r.replaceString);
    else text = text.split(r.regex).join(r.replaceString);
  }
  return text;
}
