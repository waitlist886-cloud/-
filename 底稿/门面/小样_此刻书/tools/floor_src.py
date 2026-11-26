#!/usr/bin/env python3
# 楼层主图鉴的源稿（11-26）：从卡里十八位楼层主的条目抽出名号、各阶段的情报、攻击方式、圣歌谱，写 src/floor_bosses.json 的初稿。
#   python -I -X utf8 底稿/门面/小样_此刻书/tools/floor_src.py [卡.json] [--out 路径] [--force]
# 只出初稿：src/floor_bosses.json 是手改过的那一份（改字改那一份），已经有了就不覆盖，要重抽加 --force 写到别处再对着并。
# 抽出来的字过一遍 build_data.clean()（标点、★、出处括号），“玩家”改“你”，AI 提示、硬锁、裁定锁、属性速记、接主线（勿说破）那几行不进。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(BOOK, '..', '..', '..'))
args = [a for i, a in enumerate(sys.argv[1:]) if not a.startswith('--') and sys.argv[i] != '--out']
CARD = args[0] if args else os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框.json')
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(BOOK, 'src', 'floor_bosses.json')
CN = '一二三四五六七八九'


def clean(s):
    s = re.sub(r'（★）|★', '', s or '')
    s = re.sub(r'\*\*', '', s)
    s = re.sub(r'（(?:详)?见[^）]*）', '', s)
    s = re.sub(r'，?见「[^」]*」(?:那一条|第.节)?', '', s)
    s = re.sub(r'，?见[^，。）]{1,30}那一条', '', s)
    s = re.sub(r'（照[^）]*那一条）', '', s)
    s = s.replace('——', '，').replace('—', '，').replace('；', '，').replace('…', '。').replace('！', '。')
    s = s.replace('玩家', '你')
    return re.sub(r'，。', '。', s).strip()


SKIP = re.compile(r'^(?:（AI 提示|（硬锁|AI 提示|属性速记|接主线|裁定锁|阶段口径|【调用】|【适用】|---)')


def paras(block):
    out = []
    for ln in block.split('\n'):
        ln = ln.strip()
        if not ln or SKIP.match(ln):
            continue
        out.append(ln)
    return out


def entry(E, head):
    for e in E:
        if e.startswith(head):
            return e
    raise KeyError(head)


def bracket(s):
    """第一对【】里的字，认得里头再套一对【】（奥里恩、卡珊德拉那两个）"""
    i = s.find('【')
    if i < 0:
        return ''
    d, j = 0, i
    while j < len(s):
        if s[j] == '【':
            d += 1
        elif s[j] == '】':
            d -= 1
            if d == 0:
                return s[i + 1:j]
        j += 1
    return s[i + 1:]


def skills(text):
    """“技能三样。【A】是……。【B】，……”这一路写在一句里的招式：名字加后头那一截"""
    out = []
    names = list(re.finditer(r'【([^【】]{1,16})】', text))
    for k, m in enumerate(names):
        end = names[k + 1].start() if k + 1 < len(names) else len(text)
        d = text[m.end():end].strip('，。、是和（）() ')
        d = re.sub(r'^(?:，|是|）)', '', d).strip()
        if d.startswith('决死技') or d in ('和', '决死技是'):
            d = ''
        out.append([m.group(1), clean(d) if len(d) > 3 else ''])
    return out


def song(text):
    """【圣歌谱】那一节：一阶、二阶……各一个乐章，终章另记"""
    i = text.find('【圣歌谱】')
    if i < 0:
        return [], None, ''
    lines = text[i:].split('\n')[1:]
    st, fin, note, cur = [], None, '', None
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        m = re.match(r'^- (?:(.)阶|终章)《(.+?)》｜(.+)$', s)
        if m:
            rest = m.group(3)
            if s.startswith('- 终章'):
                cur = dict(nm=m.group(2), t=clean(rest), words=[])
                fin = cur
                continue
            parts = rest.split('。', 1)
            head = parts[0]
            voice = '｜人声' in head
            line = head.replace('｜人声', '')
            cur = dict(nm=m.group(2), line=clean(line), voice=voice, lead=clean(parts[1]) if len(parts) > 1 else '', me='', it='', words=[])
            st.append(cur)
            continue
        if s.startswith('｜我方：') and cur is not None:
            cur['me'] = clean(s[4:])
        elif re.match(r'^｜(?:它|他|她|祂)：', s) and cur is not None:
            cur['it'] = clean(s[3:])
            cur['who'] = s[1]
        elif s.startswith('>') and cur is not None:
            cur['words'].append(clean(s.lstrip('> ').strip()))
        elif s.startswith('（') and cur is not None and not s.startswith('（七道线'):
            cur.setdefault('aside', clean(s.strip('（）')))
        elif s.startswith('本场无人声') or s.startswith('这一场从头到尾没有人声'):
            note = clean(s)
        elif s.startswith('#') or s.startswith('打得过它') or s.startswith('打赢了') or s.startswith('掉落') or s.startswith('撤离') or s.startswith('裁定锁'):
            break
    return st, fin, note


def world(text, start, stop):
    i = text.find(start)
    if i < 0:
        return []
    j = text.find(stop, i + len(start)) if stop else -1
    return [clean(p) for p in paras(text[i + len(start):j if j > 0 else None]) if not p.startswith('#')]


def card_entries():
    c = json.load(open(CARD, encoding='utf-8'))
    return [e.get('content') or '' for e in c['prompt']['lorebook']]


def main():
    if os.path.exists(OUT) and '--force' not in sys.argv:
        sys.exit('%s 已经有了（手改过的那一份），要重抽加 --force 并写到别处：--out <路径>' % OUT)
    E = card_entries()
    B = []

    # ---------- 浅层四位（#1100）：一阶，只有基础圣歌 ----------
    t = entry(E, '# 大迷宫·本土层带（上中层1–32）')
    for band in re.finditer(r'(?ms)^## (.+?)（(\d+)–(\d+)层｜([^）]+)）\n(.*?)(?=^## |\Z)', t):
        m = re.search(r'(?m)^楼层主（(\d+)层(.+?)）·(.+?)，LVL([\d\-–]+)｜(.+)$', band.group(5))
        if not m:
            continue
        nm = m.group(3).strip('【】')
        short = nm.split('，')[-1]
        first = paras(band.group(5))[0]
        B.append(dict(id='', k='楼层主', n=short, lyr=int(m.group(1)), where='第%s层·%s' % (m.group(1), m.group(2)), band='阿卡迪亚大迷宫·' + band.group(1),
                      lv='LVL ' + m.group(4), what=clean(m.group(5).split('。')[0]) + '。', world=[clean(first)],
                      st=[dict(nm=nm, lv='LVL ' + m.group(4), t=[clean(m.group(5))], atk=[])], song_note='基础圣歌，只有一道线，没有曲名，没有人声。', end=[], drop=''))

    # ---------- 本世界深处三位（#1101） ----------
    t = entry(E, '# 大迷宫·本土层带（深层前沿与未至41–100）')
    for band in re.finditer(r'(?ms)^## (下层·骨谷|深层前沿·以太乱潮|未至·雪脊摹境)（(.+?)）\n(.*?)(?=^## |\Z)', t):
        b = band.group(3)
        i = b.find('楼层主（')
        head = b[i:].split('\n', 1)[0]
        m = re.match(r'楼层主（(\d+)层·?(.+?)）(?:·(【.+?】)，(LVL[\d\- –]+))?(?:，[^｜]*)?｜(.+)$', head)
        lyr, room, intro = int(m.group(1)), m.group(2), m.group(5)
        intro = re.split(r'(?:三阶段|多段)', intro)[0].rstrip('，。') + '。'
        sb = b[i + len(head):b.find('【圣歌谱】')]
        st = []
        for ln in sb.split('\n'):
            s = ln.rstrip()
            mm = re.match(r'^- (.)阶·(.+)$', s)
            if mm:
                nm = bracket(mm.group(2))
                suf = re.search(r'•「(.)」', mm.group(2))
                desc = mm.group(2).split('｜', 1)[1] if '｜' in mm.group(2) else ''
                st.append(dict(nm=nm + ('•「%s」' % suf.group(1) if suf else ''), lv='', t=[clean(desc)] if desc else [], atk=[]))
                continue
            if not st or not s.strip() or SKIP.match(s.strip()):
                continue
            x = s.strip()
            if x.startswith('- ') and s.startswith('  '):
                st[-1]['atk'].append(['', clean(x[2:])])
            elif x.startswith('>'):
                st[-1]['t'].append(clean(x.lstrip('> ')))
            elif x.startswith('（AI') or x.startswith('玩家要是问起'):
                continue
            else:
                st[-1]['t'].append(clean(x))
        sg, fin, note = song(b)
        drop = re.search(r'(?m)^掉落：(.+)$', b)
        lvm = re.search(r'LVL ?([\d\-–]+)', head)
        lv = 'LVL ' + lvm.group(1) if lvm and '压到' not in head else 'LVL 300（压制），神域'
        name = st[0]['nm']
        B.append(dict(id='', k='楼层主', n=re.sub(r'•「.」', '', name).split('，')[-1].split('·')[-1], lyr=lyr, where='第%d层·%s' % (lyr, room),
                      band='阿卡迪亚大迷宫·' + band.group(1), lv=lv, what=clean(intro), world=[clean(paras(b)[0])], st=st,
                      song=sg, fin=fin, song_note=note, end=[], drop=clean(drop.group(1)) if drop else ''))
        for k, s in enumerate(st):
            if k < len(sg):
                s['song'] = sg[k]

    # ---------- 残响异界四位（#1102 到 #1105） ----------
    for head, lyr in (('# 残响异界·挽晨之城', 35), ('# 残响异界·赫玛血宴之城', 38), ('# 残响异界·无谬之城', 53), ('# 残响异界·卡诺莎眠雪封存都', 66)):
        t = entry(E, head)
        city = head[2:]
        i = t.find('\n楼层主｜')
        room = re.findall(r'(?m)^### (\d+)层·(.+?)（', t)[-1]
        roomdesc = t[t.find('### %s层' % room[0]):i].split('\n')[1].strip()
        hd = t[i + 1:].split('\n', 1)[0]
        nm0, intro = hd[4:].split('。', 1)
        body = t[i + 1 + len(hd):t.find('## 【圣歌谱】')]
        st, end, drop = [], [], ''
        for p in paras(body):
            mm = re.match(r'^(.)阶（[^）]*）｜(.+)$', p)
            if mm:
                nm = bracket(mm.group(2))
                rest = mm.group(2)[len(nm) + 2:].lstrip('，。')
                lvm = re.match(r'(LVL[\d\-– ]+(?:（压制）)?)，([^。]+)。(.*)$', rest)
                lv = ''
                if lvm:
                    lv, rest = lvm.group(1) + '，' + lvm.group(2), lvm.group(3)
                st.append(dict(nm=nm, lv=lv, t=[clean(rest)] if rest.strip() else [], atk=[]))
                continue
            if p.startswith('- 没集齐') or p.startswith('- 集齐'):
                a, _, b2 = p[2:].partition('｜')
                end.append([clean(a), clean(b2)])
                continue
            if p.startswith('奖励：'):
                drop = clean(p[3:])
                continue
            if re.match(r'^(两种结局|结局各)', p):
                continue
            if st:
                st[-1]['t'].append(clean(p))
        for s in st:
            sk = [q for q in s['t'] if re.search(r'技能|换成|决死技|手里换成', q)]
            for q in sk:
                s['atk'] += skills(q[q.find('【'):] if '【' in q else q)
        sg, fin, note = song(t)
        for k, s in enumerate(st):
            if k < len(sg):
                s['song'] = sg[k]
        wd = world(t, '## 这是一个什么世界', '## ')
        B.append(dict(id='', k='楼层主', n=nm0.split('·')[-1][-4:], lyr=lyr, where='第%d层·%s' % (lyr, room[1]), band=city, lv=st[0]['lv'],
                      what=clean(intro), room=clean(roomdesc), world=wd, st=st, fin=fin, song_note=note, end=end, drop=drop))

    # ---------- 薪火之国三位（#1107 到 #1109） ----------
    for head in ('# 薪火之国·圣血之城亚楠', '# 薪火之国·狼之城法兰赛斯特', '# 薪火之国·王城罗德林姆'):
        t = entry(E, head)
        m = re.search(r'(?m)^## 楼层主（(\d+)层·(.+?)）·(.+?)（(.+?)）$', t)
        lyr, room, note0 = int(m.group(1)), m.group(2), m.group(4)
        body = t[m.end():t.find('## 裁定锁', m.end())]
        st = []
        for ln in body.split('\n'):
            s = ln.rstrip()
            mm = re.match(r'^　(.)阶｜(.+)$', s)
            if mm:
                nm = bracket(mm.group(2))
                rest = mm.group(2)[len(nm) + 2:].lstrip('。')
                st.append(dict(nm=nm, lv='LVL 300（压制）', t=[clean(rest)] if rest else [], atk=[]))
                continue
            x = s.strip()
            if not st or not x or x.startswith('#'):
                continue
            st[-1]['t'].append(clean(x.lstrip('> ')))
        sg, fin, note = song(t)
        for k, s in enumerate(st):
            if k < len(sg):
                s['song'] = sg[k]
        city = head[2:]
        B.append(dict(id='', k='楼层主', n=st[-1]['nm'].split('，')[-1], lyr=lyr, where='第%d层·%s' % (lyr, room), band='残响异界·' + city, lv='LVL 300（压制）',
                      what=clean(note0), world=world(t, '## 城\n', '## '), st=st, song_note=note, end=[], drop=''))

    # ---------- 四座超大型迷宫城（#1066、#1074、#1081、#1087） ----------
    for head in ('# 黑潮螺旋城·楼层主战', '# 翠冠树海迷宫城·楼层主战', '# 曜冠空环城·楼层主战', '# 镜湖未竟城·楼层主战'):
        t = entry(E, head)
        m = re.search(r'(?m)^## 楼层主·(.+?)（史诗战·(.)阶段）$', t)
        body = t[m.end():t.find('## 【圣歌谱】')]
        secs = re.split(r'(?m)^### ', body)
        intro = [clean(p) for p in paras(secs[0])]
        st, lore = [], []
        for s in secs[1:]:
            ttl, _, rest = s.partition('\n')
            mm = re.match(r'^(.)阶·(.+)$', ttl)
            if not mm:
                lore.append([ttl.strip(), [clean(p.lstrip('> ')) for p in paras(rest) if not p.startswith('（AI')]])
                continue
            nm = bracket(mm.group(2))
            lvm = re.search(r'（(LVL[^）]+)）', mm.group(2)[len(nm):])
            S = dict(nm=nm, lv=lvm.group(1).replace('LVL ', 'LVL ') if lvm else '', t=[], atk=[])
            for p in paras(rest):
                if p.startswith('（AI') or p.startswith('（硬锁'):
                    continue
                q = re.match(r'^- (?:([^：]{1,10})：)?(.+)$', p)
                if q:
                    S['atk'].append([q.group(1) or '', clean(q.group(2))])
                else:
                    S['t'].append(clean(p.lstrip('> ')))
            st.append(S)
        sg, fin, note = song(t)
        for k, s in enumerate(st):
            if k < len(sg):
                s['song'] = sg[k]
        B.append(dict(id='', k='迷宫城之主', n=bracket(m.group(1)), lyr=0, where=head[2:head.find('·')], band='超大型迷宫城', lv=st[0]['lv'],
                      what=intro[0] if intro else '', world=intro, lore=lore, st=st, song_note=note, end=[], drop=''))

    n_st = sum(len(b['st']) for b in B)
    json.dump({'_说明': '初稿，floor_src.py 抽的', 'bosses': B}, open(OUT, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('楼层主', len(B), '位，', n_st, '阶 →', OUT)
    for b in B:
        print(' ', b['k'], b['where'], b['n'], len(b['st']), '阶', '｜'.join(s['nm'] for s in b['st']))


if __name__ == '__main__':
    main()
