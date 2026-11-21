#!/usr/bin/env python3
# 门面剧情润色（11-21）：四本书的 lineHTML 接 cards.json 里的 story（介绍、幕名、幕描述、任务名）。只改一回，改过的跳过。
#   python -I -X utf8 底稿/门面/剧情润色/tools/hook_front.py
# 数据：prep_cards.py 把 底稿/门面/剧情润色/<纪>/<时代 id>.json 并进 cards.json 的 <时代 id>.story。
# 页上：有介绍的替掉钩子引语那一行；幕名换成新的，原来的日期、时长留在后头当小字（.dt）；幕描述放在幕名下面（.ds）。
import os
import sys

FRONT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CSS = ('.ln .intro{margin:2px 0 10px;font-size:15.5px;line-height:2;letter-spacing:.05em;color:#f6e9d2}\n'
       '.ln ol li .dt{display:inline-block;margin-left:.2em;font-size:11.5px;letter-spacing:.06em;color:var(--dim)}\n'
       '.ln ol li .ds{display:block;margin-top:2px}\n'
       '.ln ol.road li.cgi p .dt{display:block;margin:4px 0 0}\n')
REPS = [
    ("  const acts = l.acts.map((a) => {",
     "  const sty = (CARDS[e.id] && CARDS[e.id].story && CARDS[e.id].story[l.name]) || null;      // 11-21 剧情润色\n"
     "  const acts = l.acts.map((a, ai) => {"),
    ("    if (lc) { if (tag === '幕间'",
     "    const sa = sty && sty.acts && sty.acts[ai] && sty.acts[ai].tag === tag ? sty.acts[ai] : null; let dt = '';\n"
     "    if (sa) { dt = (nm ? rest.slice(dot + 1) : rest || '').trim(); nm = sa.name; tail = sa.desc || ''; }\n"
     "    if (lc && !sa) { if (tag === '幕间'"),
    ("${j || !tail ? '' : `<p>${esc(tail)}</p>`}",
     "${j || !(tail || dt) ? '' : `<p>${esc(tail)}${dt ? `<small class=\"dt\">${esc(dt)}</small>` : ''}</p>`}"),
    ("<b>${esc(head)}</b>${esc(tail)}</li>",
     "<b>${esc(head)}</b>${dt ? `<small class=\"dt\">${esc(dt)}</small>` : ''}${sa ? `<span class=\"ds\">${esc(tail)}</span>` : esc(tail)}</li>"),
    ("<li><b>${esc(tag + (nm ? '　' + nm : ''))}</b>${esc(tail)}</li>",
     "<li><b>${esc(tag + (nm ? '　' + nm : ''))}</b>${dt ? `<small class=\"dt\">${esc(dt)}</small>` : ''}${sa ? `<span class=\"ds\">${esc(tail)}</span>` : esc(tail)}</li>"),
    ("  const hooks = lc ? (lc.hook",
     "  const hooks = sty && sty.intro ? [] : lc ? (lc.hook"),
    ("    + hooks.map((h) => `<p class=\"hook\">${esc(h)}</p>`).join('')",
     "    + (sty && sty.intro ? `<p class=\"intro\">${esc(sty.intro)}</p>` : '')\n"
     "    + hooks.map((h) => `<p class=\"hook\">${esc(h)}</p>`).join('')"),
    ("<span class=\"tt\">【${esc(l.task || l.name)}】</span>",
     "<span class=\"tt\">【${esc((sty && sty.task) || l.task || l.name)}】</span>"),
]


def patch(book):
    fp = os.path.join(FRONT, book, 'index.html')
    s = open(fp, encoding='utf-8').read()
    if 'const sty = (CARDS' in s:
        print(book, '改过了')
        return
    a = s.index('function lineHTML(')
    b = s.index('\n}\n', a) + 3
    body = s[a:b]
    done = []
    for old, new in REPS:
        if old in body:
            body = body.replace(old, new, 1)
            done.append(old[:18])
    s = s[:a] + body + s[b:]
    k = s.index('.ln .hook{')
    k = s.index('\n', k) + 1
    s = s[:k] + CSS + s[k:]
    open(fp, 'w', encoding='utf-8', newline='\n').write(s)
    print(book, len(done), '处', done)


for bk in sys.argv[1:] or ['小样_月银纪书', '小样_纷争纪书', '小样_山铜纪书', '小样_迷宫纪书']:
    patch(bk)
