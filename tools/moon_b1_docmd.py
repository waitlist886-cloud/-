# -*- coding: utf-8 -*-
"""把 moon/batch1/g*.md 转成写进月银纪卷「第一批条目」分页用的 markdown（out/moon_b1_doc/*.doc.md）。
用法：python3 -I tools/moon_b1_docmd.py <repo根目录> [--check]   --check 只比对不写盘"""
import sys, os, re, glob
ROOT = sys.argv[1]
CHECK = '--check' in sys.argv
OUTD = os.path.join(ROOT, 'out', 'moon_b1_doc')

def parse(path):
    text = open(path, encoding='utf-8').read()
    items = []
    for b in re.split(r'^=== ', text, flags=re.M)[1:]:
        title, rest = b.split('\n', 1)
        head, body = rest.split('\n---\n', 1)
        meta = dict(l.split('：', 1) for l in head.strip().split('\n'))
        items.append((title.strip(), {k.strip(): v.strip() for k, v in meta.items()}, body.strip('\n')))
    return items

def spec(s):
    """触发、黑名单的写法：正则词放进行内代码，别名和纯词照原样。"""
    toks = re.findall(r'〔[^〕]+〕|[^、〔〕]+', s)
    return '、'.join('`%s`' % t.strip() if t.strip().startswith('/') else t.strip() for t in toks if t.strip())

def render(items):
    out = []
    for title, m, body in items:
        how = '触发（同时满足）' if m.get('触发方式') == '同时满足' else '触发'
        setting = '条目设置：文件夹 %s，%s %s，黑名单 %s，范围 用户与助手，深度 2，优先级 %s。' % (
            m['文件夹'], how, spec(m['触发']), spec(m.get('黑名单', '无')), m['优先级'])
        body = re.sub(r'^## ', '### ', body, flags=re.M)
        out.append('## %s\n\n%s\n\n%s' % (title, setting, body))
    return '\n\n'.join(out)

diff = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'moon', 'batch1', 'g*.md'))):
    name = os.path.basename(f)[:-3] + '.doc.md'
    txt = render(parse(f))
    dst = os.path.join(OUTD, name)
    old = open(dst, encoding='utf-8').read() if os.path.exists(dst) else None
    same = (old == txt)
    print(name, '一致' if same else '不同')
    if not same:
        diff += 1
        if not CHECK:
            open(dst, 'w', encoding='utf-8').write(txt)
print('不同的文件', diff)
