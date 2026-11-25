#!/usr/bin/env python3
# 此刻那一本（迷宫纪 1001 年，门面第五本书，11-24）的数据。
#   python -I -X utf8 底稿/门面/小样_此刻书/build_data.py [卡.json]       卡不写就用 out/发布卡_四纪大框/奥尔德兰_四纪大框.json
# 写 data/now.json（路、起点、大陆全图）和 data/atlas.json（图鉴：旅伴、相遇、凡世至强、七神与魔王），再跑 prep_assets.py 出图。
# 字从哪里来：
#   路上三十一条主线的介绍和幕名、十处起点、旅伴的一句话：src/road_text.json（门面口气，照 门面剧情润色_方向稿.md 第五稿写的，改字改这一份）。
#   哪一条落在哪一年（排在路上第几段）：卡里各条主线的“适期”。十兆是真相层，页上不出兆名（头一段的兆名玩家在状态栏上看得见，留着）。
#   路尽头那几盏灯剧透开了露的边：大图书馆 书稿/迷宫纪廊_十兆.md 里井环的孩子唱的那首数钟歌，只露歌，不露兆名。
#   图鉴：旅伴、凡世至强照 1001 年常驻「预设短名」那一节分组，档案的栏目照卡里各人的条目抽；相遇是 11-23 新添的六位人物；
#        七神照迷宫纪那一本的图鉴（共用/build_atlas.py 出的），魔王的神域栏照 底卡新条目/神域_今天的八位.md。
#   大陆全图：底稿/状态栏/大框/map_data.json 的一百四十一处地标，原画照旧 1001 页（小样_外壳/old1001.html 的 AUL_ART，一百九十三张）。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FRONT = os.path.normpath(os.path.join(HERE, '..'))
ROOT = os.path.normpath(os.path.join(FRONT, '..', '..'))
CARD = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框.json')
RES = os.path.join(ROOT, '底稿', '状态栏', '大框', '主提示词', '常驻_迷宫纪1001年.md')
ROSTER = json.load(open(os.path.join(ROOT, '底稿', '状态栏', '大框', 'roster.json'), encoding='utf-8'))
ROSTER.update({'蕾娃': 'reva', '苏海拉': 'suhaila', '托芙': 'tove', '朵薇': 'dove', '坎黛丝': 'candace', '肯特': 'kent'})
CN = '〇一二三四五六七八九'


def cn_year(y):
    """1001 → 一千零一年"""
    s = '一千'
    r = y - 1000
    if r == 0:
        return s + '年'
    if r < 10:
        return s + '零' + CN[r] + '年'
    t, o = divmod(r, 10)
    return s + '零' + CN[t] + '十' + (CN[o] if o else '') + '年'


def clean(s):
    s = re.sub(r'（★）|★', '', s or '')
    s = re.sub(r'\*\*', '', s)
    s = re.sub(r'（见[^）]*）', '', s)
    s = re.sub(r'（照[^）]*那一条）', '', s)
    return s.replace('——', '，').replace('—', '，').replace('；', '，').replace('…', '。').replace('！', '。').strip()


def entries():
    c = json.load(open(CARD, encoding='utf-8'))
    return [e.get('content') or '' for e in c['prompt']['lorebook']]


def field(body, lab):
    m = re.search(r'(?m)^(?:- )?%s[：｜](.+)$' % re.escape(lab), body)
    return clean(m.group(1)) if m else ''


def main():
    E = entries()
    rt = json.load(open(os.path.join(HERE, 'src', 'road_text.json'), encoding='utf-8'))

    # ---------- 路 ----------
    lines = []
    for L in rt['lines']:
        body = next((e for e in E if re.search(r'(?m)^# (?:地区|主城)活事件｜[^\n]*：%s$' % re.escape(L['title']), e)), '')
        m = re.search(r'适期：兆(.)', body)
        z = '一二三四五六七八九十'.index(m.group(1)) + 1 if m else 1
        lines.append(dict(id='L%d' % L['src'], title=L['title'], prefix=L['prefix'], place=L['place'].replace('迷宫都市阿卡迪亚', '迷宫都市·阿卡迪亚'),
                          kind=L['kind'], intro=L['intro'], acts=L['acts'], with_=L['with'], z=z))
    for x in lines:
        x['with'] = x.pop('with_')
    # 一段一年（兆 N 起于 1001+2(N-1) 年），头一段带兆名（状态栏上看得见），往后只写年份
    IMG = {1: 'r2', 2: 'r1', 4: 'r3', 5: 'r4', 6: 'r5', 7: 'r6'}
    groups = []
    for z in range(1, 11):
        ls = [x['id'] for x in lines if x['z'] == z]
        if not ls:
            continue
        y = 1001 + 2 * (z - 1)
        # 牌面那一段字：只给头一段（11-24 第四拨，照兆一新写的起潮那一夜和本兆之王；往后各段照旧不出字）
        groups.append(dict(z=z, y=y, yt=cn_year(y), name='魔兽离巢' if z == 1 else '', d=(rt.get('zface') or {}).get(str(z), '') if z == 1 else '',
                           img=IMG.get(z, ''), lines=ls))
    # 地区主线排在同一段的前头
    for g in groups:
        g['lines'].sort(key=lambda i: (next(x for x in lines if x['id'] == i)['kind'] != '五幕', i))
    # 路尽头的灯：井环那一版数钟歌（剧透开了才露，只露歌）
    book = open(os.path.join(FRONT, '第二轮', '大图书馆', '书稿', '迷宫纪廊_十兆.md'), encoding='utf-8').read()
    song = re.findall(r'(?m)^(.{1,3}声钟，[^\n]+?)[，。]$', book)[:10]
    assert len(song) == 10, song

    # ---------- 大陆全图 ----------
    # 地标上挂的原画原来外链在 imgur（旧 1001 页），tools/localize_pics.py 取下来放 assets/mp/<键>.webp；本地有就写本地（11-24）
    def local_pic(u):
        m = re.search(r'imgur\.com/([A-Za-z0-9]+)\.', u)
        if m and os.path.exists(os.path.join(HERE, 'assets', 'mp', m.group(1) + '.webp')):
            return 'assets/mp/' + m.group(1) + '.webp'
        return u
    md = json.load(open(os.path.join(ROOT, '底稿', '状态栏', '大框', 'map_data.json'), encoding='utf-8'))
    old = open(os.path.join(FRONT, '小样_外壳', 'old1001.html'), encoding='utf-8').read()
    i = old.find('var AUL_ART=')
    art = json.loads(old[i + len('var AUL_ART='):old.find(';', i)])
    lands = []
    for l in md['lands']:
        pics = [[k.split('|', 1)[1], local_pic(v)] for k, v in art.items() if k.split('|', 1)[0] == l['n']]
        d = clean(l['d']).replace('满月雾夜', '起雾的夜里').replace('月光沿裂痕照下', '夜光沿裂痕照下').replace('诏令', '敕令')          # 门面不写月相（专名除外）；诏书一类照换词表写敕令
        lands.append(dict(n=l['n'], x=l['x'], y=l['y'], z=l['z'], t=l['t'], r=clean(l['r']), lv=l['lv'], d=d, pics=pics))
    nart = sum(len(l['pics']) for l in lands)

    out = dict(groups=groups, lines=lines, song=song, sites=rt['sites'],
               map=dict(img='assets/map.webp', w=2200, h=1400, lands=lands))
    json.dump(out, open(os.path.join(HERE, 'data', 'now.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(',', ':'))
    print('now.json：主线', len(lines), '条，', len(groups), '段，起点', len(rt['sites']), '处，地标', len(lands), '处，原画', nart, '张')

    # ---------- 图鉴 ----------
    res = open(RES, encoding='utf-8').read()
    sec = res[res.find('**旅伴**'):res.find('旅伴专武')]
    people, grp = [], ''
    for ln in sec.split('\n'):
        m = re.match(r'^\*\*(.+?)\*\*', ln)
        if m:
            grp = m.group(1)
            continue
        for it in ln.split('｜'):
            if '：' not in it:
                continue
            n, w = it.split('：', 1)
            people.append(dict(n=n.strip(), grp=grp, line=w.strip()))
    comp = {c['n']: c for c in rt['companions']}

    def body_of(head_re):
        return next((e for e in E if re.search(head_re, e)), '')

    P = []
    for p in people:
        short = p['n'].split('·')[0]
        key = ROSTER.get(short)
        kind = '旅伴' if p['grp'] == '旅伴' else '传奇'
        x = dict(n=p['n'], key=key, at={'now': kind}, prof=['now'], grp=p['grp'])
        if kind == '旅伴':
            b = body_of(r'(?m)^## 旅途同行：%s$' % re.escape(p['n']))
            c = comp.get(p['n'], {})
            x['who'] = c.get('who') or p['line']
            x['bond'] = c.get('bond', '')
            pf = [['身份', field(b, '身份')], ['样子', field(b, '外貌')], ['容貌', field(b, '容貌评价')]]
            sw = re.search(r'(?m)^专武：【(.+?)】\((.+?)\)', b)
            if sw:
                pf.append(['专武', sw.group(1) + '，' + sw.group(2).replace('·', '，')])
            stars = re.findall(r'(?m)^- (Special|Passive|Art)【(.+?)】\((\w+)\)｜(.+)$', b)
            if stars:
                pf.append(['命星', '　'.join('%s · %s · %s' % (t, n, r) for t, n, r, _ in stars)])
            lines_ = re.search(r'台词样例：(.+)$', b, re.M)
            if lines_:
                pf.append(['她说', '　'.join(lines_.group(1).split('／')[:3]) if lines_ else ''])
            fm = re.search(r'固定锚定：([^\n]+)', b)
            if fm:
                race = re.search(r'种族锚定=([^｜]+)', fm.group(1))
                x['race'] = race.group(1) if race else ''
            x['pf'] = [q for q in pf if q[1]]
        else:
            b = body_of(r'(?m)^## 凡世至强(?:镜像栏位)?：[^\n]*%s' % re.escape(p['n'].split('·')[0]))
            h = re.search(r'(?m)^## 凡世至强(?:镜像栏位)?：(.+?) · ', b)
            x['title'] = h.group(1).replace(' · ', '·') if h else ''
            x['who'] = p['line']
            fm = re.search(r'种族锚定=([^｜\n]+)', b)
            x['race'] = fm.group(1) if fm else ''
            tier = re.search(r'(?m)^位阶(?:与职责)?：([^｜。\n]+)', b)
            x['tier'] = tier.group(1).replace('传奇·', '') if tier and '传奇' in tier.group(1) else ''
            pf = [['位阶', field(b, '位阶与职责') or field(b, '位阶')], ['在哪', field(b, '势力/地点')], ['样子', field(b, '仪容与印象') or field(b, '外貌')],
                  ['容貌', field(b, '容貌评价')], ['凝名', field(b, '凝名纪年')], ['伟业', field(b, '凝名伟业')]]
            x['pf'] = [q for q in pf if q[1]]
        P.append(x)
    # 相遇：11-23 新添的六位（迷宫纪1001年起在各地的人，有立绘）
    for e in E:
        m = re.match(r'## 人物｜(.+?)（(.+?)）\n', e)
        if not m or '迷宫纪1001年起' not in e[:200]:
            continue
        n = m.group(1)
        key = ROSTER.get(n.split('·')[0])
        if not key:
            continue
        who = field(e, '是谁')
        P.append(dict(n=n, key=key, at={'now': '相遇'}, prof=['now'], grp='相遇', who=m.group(2), race='',
                      pf=[q for q in [['是谁', who], ['样子', field(e, '样子')], ['本事', field(e, '本事')], ['在哪', field(e, '在哪')]] if q[1]]))

    # 神：七神照迷宫纪那一本的图鉴，魔王另做一张
    maze = json.load(open(os.path.join(FRONT, '小样_迷宫纪书', 'data', 'atlas.json'), encoding='utf-8'))
    gods = []
    for g in maze['gods']:
        g = dict(g, at=['now'])
        gods.append(g)
    sys.path.insert(0, os.path.join(FRONT, '共用'))
    import build_atlas as BA          # noqa: E402
    doms = BA.load_domains()
    bt = [dict(n='巴尔缇娜')]
    today = BA.load_today(bt)
    bb = body_of(r'(?m)^## 凡世至强镜像栏位：魔王')
    look = re.search(r'(?m)^外貌：(.+)$', bb)
    gods.insert(0, dict(n='巴尔缇娜', tag='魔王', side='魔王', grp='魔王', img='assets/art/baltina.webp', rule='黑耀帝国的王，山铜纪的人叫她灰之魔女',
                        look=clean(look.group(1)).split('底下那一节')[0].strip() if look else '', at=['now'], dom=BA.make_dom(today.get('巴尔缇娜'), doms) or {}))
    bd = gods[0]['dom']
    if bd.get('sx') == '两份':          # 她的神性一行开头就是“两份。”，抽第一截只剩两个字，补上后头那两句
        m = re.search(r'(?m)^- 神性：两份。(.+)$', open(os.path.join(ROOT, '底卡新条目', '神域_今天的八位.md'), encoding='utf-8').read())
        bd['sx'] = '两份。' + clean(m.group(1)) if m else '两份'
    # 十王和凯斯珀·佩兰（11-24 第四拨）：从 底卡新条目/大敌线_1001.md 取。接法照山铜纪那一本的“主线对手”（没有图，大图那格空着）。
    # 剧透关着只露兆一的咬灯格里沃和凯斯珀明面上的身份（他进人物的传奇一栏）；别的八位王和他的底细名字带“·隐藏”，剧透开了才出（atlas.js 的 hiddenFoe）。
    # 格里沃那一张不写回廊里那一句（回廊是真相层），写打法。
    foes = []
    big = open(os.path.join(ROOT, '底卡新条目', '大敌线_1001.md'), encoding='utf-8').read()
    ZN = ['魔兽离巢', '迷宫长芽', '遗迹点灯', '亡者归来', '元素乱季', '龙群迁徙', '深海开门', '神火黯淡', '天穹裂门', '万迷宫齐鸣']
    KIND = ['魔狼王', '镜甲骑士长', '古代魔导将军', '亡国女王', '雷霆凤凰', '冰冠古龙', '海雾提督', '堕落圣骑士', '虚空骑士团长']
    for m in re.finditer(r'(?ms)^## 迷宫纪·本兆之王｜兆(.)·(.+?)\n(.*?)(?=^## )', big):
        z = '一二三四五六七八九'.index(m.group(1)) + 1
        nm, b = m.group(2).strip(), m.group(3)
        def bul(lab):
            q = re.search(r'(?m)^- %s：(.+)$' % lab, b)
            return clean(q.group(1)).replace('玩家', '你') if q else ''
        f = dict(k='主线对手', full=bul('名号'), note='兆%s·%s' % ('一二三四五六七八九'[z - 1], ZN[z - 1]), what=bul('是什么'), ph=[], at=['now'])
        if z == 1:
            f.update(n=nm, where=bul('打法'))
        else:
            f.update(n='%s·隐藏 %s' % (KIND[z - 1], nm.replace(KIND[z - 1], '') or nm), where='回廊里，' + bul('回廊里'))
        foes.append(f)
    assert len(foes) == 9, len(foes)
    kb = big[big.find('## 迷宫纪·人物｜凯斯珀·佩兰'):big.find('## 迷宫纪·势力｜沉灯会')]
    rank = field(kb, '位阶与职责').split('往后')[0].rstrip('，')
    P.append(dict(n='凯斯珀·佩兰', key=None, at={'now': '传奇'}, prof=['now'], grp='冒险者公会', title='三百一十二盏', race='人类', tier='撼世',
                  who='铃尾市集东角看蜂蜜井的人，弩手，兆一起潮那一夜踏进传奇',
                  pf=[q for q in [['位阶', rank], ['在哪', field(kb, '势力/地点')], ['样子', field(kb, '仪容与印象')], ['容貌', field(kb, '容貌评价')],
                                  ['凝名', field(kb, '凝名纪年').replace('（名字凝住）', '名字凝住')], ['伟业', field(kb, '凝名伟业')]] if q[1]]
                  + [['底细', '他是这一纪第四位渊染传奇。969年那一件伟业是沉灯会的会首替他撬开蜂蜜井造出来的，他真守了一夜，世界认下的却是一件空的事。十兆每一兆他出一手，明面上都在救人，帮的忙也是真的，他点的灯却替井底下那东西把潮一兆一兆领了出来。他只当井许了愿，要把948年老堤那一夜没上来的姐姐还给他。到了第十兆，他坐在归还门前的石阶顶上，说门我替你守着。', 1],
                     ['回头的门', '揭穿要当众，要有实物，凑够两样，他跌回英雄。劝回要一件摆在眼前、他做得成的事，最后那一回是苇染家的活扣，有人在他手腕上系一截新布，他回头，转身守门。', 1]]))
    foes.append(dict(n='门前的人·隐藏 凯斯珀·佩兰', k='主线对手', full='十王回廊的第十道门，归还门前石阶顶上坐着的那一位', note='兆十·万迷宫齐鸣', at=['now'],
                     ph=[dict(nm='', img='', look=field(kb, '仪容与印象'))],
                     what='三百一十二盏，十兆里最受爱戴的传奇，也是每一兆大潮背后点灯的那只手。第十道门没有天，一截石阶，三百一十二盏灯，归还门在顶上，他坐在最上面一级。照他说的进门，门那一边定成井那一边，不进，就在石阶上打。',
                     where='回廊里前九道门的王都认得你。斩过、封过的，是母兽照着做的，开口用你的嗓子说你在大潮里对它说的最后一句，缔约过的是它本身，说它自己的话。'))

    # 图鉴的人像拼图：照 prep_assets.py 的 pa 那几张排（一组一张，八列）
    PA = {}
    order = [('c', lambda x: x['at']['now'] == '旅伴'), ('m', lambda x: x['at']['now'] == '相遇'), ('l', lambda x: x['at']['now'] == '传奇')]
    for sk, f in order:
        ks = [x for x in P if f(x) and x.get('key')]
        cols = min(8, len(ks))
        PA[sk] = [cols, (len(ks) + cols - 1) // cols]
        for i, x in enumerate(ks):
            x['pa'] = [sk, i]
    atlas = dict(vol='now', era='此刻', name='旅人手册', sub='迷宫纪一千零一年 · 同行的人、在世的传奇、七神与魔王', emblem='common/assets/ui/emblem_maze.webp',
                 periods=[dict(id='now', t='一千零一年', lb='', y='迷宫纪', y0=1001, y1=1001, img='assets/main.webp', part=None)],
                 pa=PA, people=P, foes=foes, gods=gods, beasts=[])
    json.dump(atlas, open(os.path.join(HERE, 'data', 'atlas.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(',', ':'))
    print('atlas.json：人物', len(P), '（旅伴', sum(1 for x in P if x['at']['now'] == '旅伴'), '，相遇', sum(1 for x in P if x['at']['now'] == '相遇'),
          '，传奇', sum(1 for x in P if x['at']['now'] == '传奇'), '），没立绘的', [x['n'] for x in P if not x.get('key')], '，神', len(gods))
    json.dump({'pa': {k: [x['key'] for x in P if x.get('pa', [''])[0] == k] for k in PA}}, open(os.path.join(HERE, 'data', 'pa_keys.json'), 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
