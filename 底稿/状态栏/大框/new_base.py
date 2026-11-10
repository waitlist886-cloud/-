# 底卡新条目（11-10 起）：仓库根上 底卡新条目/*.md 里「## 迷宫纪·X｜Y」起的节，一节一条，接在迷宫纪1001年切片的世界书末尾。
# 风月（make_fy_card.py 把日里底卡后头的单条新条目照搬过去）、两张用户底（merge_user_rili.py、merge_user_fy.py 接上这一版多出来的）跟着走。
# 四纪大框不收：这些条目只写1001年那一局，玩家那一侧的触发挡不住别纪（黑名单只看同一条消息）。
#
# 一节的样子（照各页的写法，条目设置在节末，cardscan、authormark 认得）：
#   ## 迷宫纪·路程｜几处大地方之间要走多久
#   （正文，可以有 ### 小节）
#   > 条目设置：文件夹 19·旅行、城镇与医疗，触发 路程、车程、`/正则/`，黑名单 无，范围 用户与AI，深度 2。
# 也认另一种（条目设置紧跟在标题底下，分号隔开）：
#   ## 迷宫纪·产业｜银行与借贷
#   条目设置：触发 银行、借贷、/正则/；范围 用户、AI；深度 2；文件夹 10·货币、装备与制作[；黑名单 X、Y][；优先级 N]
#   （正文，到下一个 ## 为止）
# 进卡的正文头一行写成「## 路程｜几处大地方之间要走多久」（去掉迷宫纪·，底卡的标题都不带纪名）。
import glob
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
DIR = os.path.join(ROOT, '底卡新条目')
RANGE = {'用户': 'user', '玩家': 'user', 'AI': 'assistant', '助手': 'assistant', '系统': 'system'}
HEAD = re.compile(r'^## 迷宫纪·(.+)$')


def split_outside_ticks(s, seps):
    """照分隔符切开，反引号里的（正则）不切"""
    parts, cur, tick = [], '', False
    for ch in s:
        if ch == '`':
            tick = not tick
        if ch in seps and not tick:
            parts.append(cur)
            cur = ''
        else:
            cur += ch
    parts.append(cur)
    return [p for p in parts if p.strip()]


def words(v):
    out = []
    for w in split_outside_ticks(v, '、'):
        w = w.strip().strip('`')
        if w and w != '无':
            out.append(w)
    return out


def parse_setting(s, where):
    m = re.match(r'^(?:> )?条目设置[：:]\s*(.+?)。?$', s.strip())
    assert m, ('%s 认不出条目设置' % where, s[:40])
    out = {}
    for part in split_outside_ticks(m.group(1), '；;，'):
        part = part.strip()
        if not part:
            continue
        k = re.match(r'^(触发|黑名单|范围|深度|文件夹|优先级)\s*', part)
        assert k, ('%s 条目设置里认不出 %s' % (where, part[:20]))
        v = part[k.end():].strip()
        k = k.group(1)
        if k == '触发':
            out['trig'] = words(v)
        elif k == '黑名单':
            out['black'] = words(v)
        elif k == '范围':
            out['range'] = [RANGE[w.strip()] for w in re.split(r'[、,，与]', v) if w.strip()]
        elif k == '深度':
            out['depth'] = int(v)
        elif k == '文件夹':
            out['folder'] = v
        elif k == '优先级':
            out['prio'] = int(v)
    for k in ('trig', 'range', 'depth', 'folder'):
        assert k in out, ('%s 条目设置少了 %s' % (where, k))
    for w in out['trig'] + out.get('black', []):
        if w.startswith('/') and w.endswith('/') and len(w) > 2:
            re.compile(w[1:-1])
    return out


def load(dir_=DIR):
    """读 底卡新条目/*.md，返回 [(文件, 标题, 设置, 正文)]，正文头一行是去掉纪名的标题"""
    out = []
    for f in sorted(glob.glob(os.path.join(dir_, '*.md'))):
        lines = open(f, encoding='utf-8').read().replace('\r', '').split('\n')
        i = 0
        while i < len(lines):
            m = HEAD.match(lines[i])
            if not m:
                i += 1
                continue
            title = m.group(1).strip()
            where = '%s｜%s' % (os.path.basename(f), title)
            j = i + 1
            while j < len(lines) and not lines[j].startswith('## '):
                j += 1
            block = lines[i + 1:j]
            if block and block[0].startswith('条目设置'):
                st = parse_setting(block[0], where)
                block = block[1:]
            else:
                k = [n for n, l in enumerate(block) if l.startswith('> 条目设置')]
                assert len(k) == 1, ('%s 节末要正好一行「> 条目设置」' % where, len(k))
                st = parse_setting(block[k[0]], where)
                assert not ''.join(block[k[0] + 1:]).strip(), ('%s 条目设置那一行后头还有字' % where)
                block = block[:k[0]]
            body = '\n'.join(block).strip('\n')
            assert body.strip(), ('%s 没有正文' % where)
            out.append((os.path.basename(f), title, st, '## %s\n%s' % (title, body)))
            i = j
    return out


def entries(lorebook, dir_=DIR):
    """照底卡已有的文件夹排优先级：同一个文件夹里接在最后一条后头"""
    folders = {}
    for e in lorebook:
        folders.setdefault(e['folder'], []).append(e['priority'])
    out = []
    bump = {}
    for f, title, st, content in load(dir_):
        assert st['folder'] in folders, ('文件夹在底卡里没有', st['folder'], title)
        bump[st['folder']] = bump.get(st['folder'], 0) + 1
        prio = st.get('prio', max(folders[st['folder']]) + bump[st['folder']])
        out.append({'enabled': True, 'triggerWords': st['trig'], 'triggerWordsType': 'OR',
                    'blackListWords': st.get('black', []), 'blackListWordsType': 'OR', 'folder': st['folder'],
                    'priority': prio, 'probability': 100, 'scanDepth': st['depth'], 'triggerRange': st['range'],
                    'impactRange': ['system'], 'contentMethod': 'single', 'content': content})
    return out


def apply(card, n_base=1397):
    """接在 1001 年切片的世界书末尾，返回接了几条"""
    lb = card['prompt']['lorebook']
    new = entries(lb[:n_base])
    lb.extend(new)
    return len(new)


if __name__ == '__main__':
    for f, title, st, content in load():
        print(f, title, st['folder'], st['range'], st['depth'], len(st['trig']), '触发', len(content), '字')
