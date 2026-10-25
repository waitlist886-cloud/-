"""命星说明去模板检查（10-25，照 底卡洗稿与命名重审_方向稿_第三版.md 第四节和写作口径「命星」）。

用法：python3 -I -X utf8 tools/starlint.py [页.md ...]   不给页就扫全部四十五页。
加 --list 把每一条犯了的星名列出来。

一颗星从「### 名 (类 | 阶)」起，到下一个 ### 或 ## 或「> 条目设置」为止。数这几样，每页给线：
  定位排四个单字（Art）              线 0
  共鸣、灵格、极境、英雄四档排满      线 两成
  被动那一行开头是属性加百分之几      线 0（属性挪到这一行末尾）
  修行关联开头是「与」                线 0
  修行关联里有互相促进                线 0
  一颗里同用两回以上                  线 0
  判定获得优势收尾                    线 两颗
  世界反应写某地的人说                线 三颗
  位阶越高                            线 三颗
  是……的那一门（月银纪那一路）       线 三颗
  先学…后学（诸国期那一路）          线 三颗
  Special、Passive 头两句没写成天赋   线 0（头两句里要有体质、天赋、生来、生下来、与生俱来、天生、一辈一辈这一类字）
只是报数，不改文件。
"""
import re, sys, glob, os, collections

PAGES = ['月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md',
         '纷争纪/纷争纪时段_*.md', '山铜纪/山铜纪时段_*.md', '迷宫纪前传/迷宫纪前传时段_*.md']
HEAD = re.compile(r'^### (.+?) \((Art|Special|Passive|Active)\s*\|\s*(\w+)\)\s*$')
INNATE = re.compile(r'体质|天赋|生来|生下来|与生俱来|天生|一辈一辈|一辈出|打娘胎|胎里|血里带|骨子里')
CHECKS = [
    ('定位排四个单字', 'Art', 0),
    ('四档排满', 'Art', '20%'),
    ('被动开头是属性', 'SP', 0),
    ('修行关联开头是与', 'ALL', 0),
    ('互相促进', 'ALL', 0),
    ('一颗里同用两回以上', 'ALL', 0),
    ('判定获得优势收尾', 'ALL', 2),
    ('某地的人说', 'ALL', 3),
    ('位阶越高', 'ALL', 3),
    ('是……的那一门', 'ALL', 3),
    ('先学后学', 'ALL', 3),
    ('头一句没写成天赋', 'SP', 0),
]


def blocks(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    i = 0
    while i < len(lines):
        m = HEAD.match(lines[i])
        if not m:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith('### ') and not lines[j].startswith('## ') and not lines[j].startswith('> 条目设置'):
            j += 1
        yield m.group(1), m.group(2), lines[i + 1:j]
        i = j


def first_sentence(name, body):
    """头两句：头一句说它是什么体质或天赋，第二句谁家常有、生下来怎样，两句里有一处就算。"""
    for ln in body:
        if ln.startswith('【' + name + '】'):
            return '。'.join(re.split(r"[。]", ln)[:2])
    for ln in body:
        if ln.strip() and not ln.startswith('【调用】') and not ln.startswith('-'):
            return '。'.join(re.split(r"[。]", ln)[:2])
    return ''


def check_star(name, kind, body):
    hits = []
    text = '\n'.join(body)
    def line(label):
        for ln in body:
            if ln.startswith('- ' + label + '：') or ln.startswith('- ' + label + ':'):
                return ln[len(label) + 3:]
        return None
    pos = line('定位')
    if kind == 'Art' and pos and re.match(r'^\s*[一-鿿]，[一-鿿]，[一-鿿]，[一-鿿][。，]', pos):
        hits.append('定位排四个单字')
    if kind == 'Art' and all(k in text for k in ('共鸣', '灵格', '极境', '英雄')):
        hits.append('四档排满')
    pas = line('被动')
    if kind in ('Special', 'Passive') and pas and re.match(r'^\s*[A-Z]{2,4}([／/、][A-Z]{2,4})*\s*\+\d', pas):
        hits.append('被动开头是属性')
    rel = line('修行关联') or line('修行重点')
    if rel is not None:
        if rel.lstrip().startswith('与'):
            hits.append('修行关联开头是与')
        if '互相促进' in rel:
            hits.append('互相促进')
        if rel.count('同用') >= 2:
            hits.append('一颗里同用两回以上')
    if re.search(r'判定获得优势[。]?\s*$', text, re.M):
        hits.append('判定获得优势收尾')
    world = line('世界反应') or ''
    if re.search(r'的人说', world):
        hits.append('某地的人说')
    if '位阶越高' in text:
        hits.append('位阶越高')
    if re.search(r'】是[^。\n]{0,60}的那一门', text):
        hits.append('是……的那一门')
    if re.search(r'先学[^。\n]{0,30}后学', text):
        hits.append('先学后学')
    if kind in ('Special', 'Passive'):
        fs = first_sentence(name, body)
        if not INNATE.search(fs):
            hits.append('头一句没写成天赋')
    return hits


def main(argv):
    show = '--list' in argv
    pages = [a for a in argv if a != '--list']
    if not pages:
        for pat in PAGES:
            pages += sorted(glob.glob(pat))
    grand = 0
    grand_counts = collections.Counter()
    for f in pages:
        stars = list(blocks(f))
        if not stars:
            continue
        counts = collections.Counter()
        who = collections.defaultdict(list)
        n_art = sum(1 for s in stars if s[1] == 'Art')
        n_sp = sum(1 for s in stars if s[1] in ('Special', 'Passive'))
        for name, kind, body in stars:
            for h in check_star(name, kind, body):
                counts[h] += 1
                who[h].append(name)
        over = []
        for label, scope, lim in CHECKS:
            c = counts.get(label, 0)
            if lim == '20%':
                lim_n = max(1, round(0.2 * n_art))
            else:
                lim_n = lim
            if c > lim_n:
                over.append((label, c, lim_n))
        grand += len(over)
        grand_counts.update(counts)
        print(f'== {os.path.basename(f)} | 星 {len(stars)}（Art {n_art}，Special/Passive {n_sp}） | 过线 {len(over)}')
        for label, c, lim_n in over:
            line = f'  - {label} {c} 颗，线 {lim_n}'
            if show:
                line += '：' + '、'.join(who[label])
            print(line)
    print('全卷各项：' + '，'.join(f'{k} {v}' for k, v in grand_counts.most_common()))
    print(f'合计 过线 {grand}')


if __name__ == '__main__':
    main(sys.argv[1:])
