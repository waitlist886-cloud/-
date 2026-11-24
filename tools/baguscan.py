"""八股排查用的数数脚本（11-24）。只数数，不改字；命中不等于有错，看密度，改不改由人读了定。

口径在 底稿/排查_八股/口径.md（从 rewrite-natural-prose、chinese-prose-register、western-fantasy-prose、
jrpg-lore-writing 四份里摘的）。一类一类数，一份文件一行，按每万字几处报；--lines 把命中的行印出来。

用法（仓库根上）：
  python -I -X utf8 tools/baguscan.py 文件或目录… [--lines] [--only 类名,类名] [--top N] [--min 密度]
  --lines  印命中的行（一类至多印 --top 条，默认 12）
  --only   只数这几类
  --min    只列合计密度不低于这个数的文件（每万字几处）
  --tsv    出一张 tsv（文件、字数、各类处数、合计密度），给分份用
不数的地方：「> 条目设置」行、代码块、「## 设计备注」以后、表格行、〔图…〕插图标记。
"""
import collections, os, re, sys

CJK = re.compile(r'[一-鿿]')

# 一类：名字 -> [(说明, 正则)]
CATS = collections.OrderedDict()
CATS['姿态收尾'] = [
    ('看了很久/站了很久这一路', r'(?:看|站|坐|望|盯|等|停|愣|想|沉默|立)了(?:很久|好久|许久|半天|一会儿|好一会儿|一阵)'),
    ('没说话这一路', r'(?:没有?|不)(?:再)?(?:说话|作声|出声|吭声|开口|回头|回答|抬头|解释)(?=[，。]|$)'),
    ('什么也没说', r'(?:什么|一句话?|一个字)(?:也|都)(?:没有?|不)(?:说|问|提|讲|写)'),
    ('半天没/很久没', r'(?:半天|很久|好久|许久|好一会儿)(?:没有?|不)(?:说话|动|出声|开口)'),
    ('没有人知道', r'(?:没有?人|谁也不|谁都不|无人)(?:知道|晓得|说得清|记得|明白)'),
    ('她没有说过', r'(?:他|她|祂|它)(?:自己)?(?:从来|从|一直)?(?:没有?|不)(?:说过|提过|解释过|讲过)'),
    ('从此再没有', r'(?:从此|往后|后来)(?:再)?(?:没有?|不曾)(?:人)?[^，。]{0,8}过(?=[，。])'),
]
CATS['套句'] = [
    ('不是…而是', r'不是[^，。？\n]{1,24}[，,]\s*(?:而)?是(?!不是)[^，。？\n]{1,24}'),
    ('没有…也没有…只有', r'没有[^，。\n]{1,14}[，,]\s*也?没有[^，。\n]{1,14}[，,]\s*(?:只有|只剩)'),
    ('那一刻/这一刻他明白', r'(?:那|这)一刻[^。\n]{0,10}(?:明白|懂了|知道|意识到)'),
    ('终于明白', r'终于(?:明白|懂得|懂了|知道)'),
    ('仿佛/似乎/好像', r'仿佛|似乎|宛如|犹如'),
    ('某种/一种', r'某种|一种(?:说不[出清]|难以|莫名)'),
    ('与其说…不如说', r'与其说'),
    ('真正…的是', r'真正[^，。\n]{1,12}的(?:，)?(?:是|不是)'),
    ('意味着', r'意味着|象征着|代表着'),
    ('不X的Y成排', r'不[^，。\n的]{1,3}的[^，。\n]{1,4}[、，]不[^，。\n的]{1,3}的'),
]
CATS['身体八股'] = [
    ('眼嘴指喉', r'眼(?:中|里|底)闪过|嘴角(?:勾|扬|牵|抽)|瞳孔一缩|指节(?:泛|发)白|喉结|深吸一口气|心头一(?:凛|紧|震|颤)|倒吸一口'),
    ('一丝一抹一股', r'一丝|一抹|一股(?!脑)|近乎'),
    ('空气凝固', r'空气(?:仿佛|好像|像是)?(?:凝固|凝住|安静)|弥漫着'),
]
CATS['翻译腔'] = [
    ('进行/加以/予以/作出', r'进行了?|加以|予以|作出了?|做出了?(?:决定|选择|回应|判断)'),
    ('有着/之一', r'有着|之一(?=[，。])'),
    ('作为一(?:名|个|位)', r'作为(?:一(?:名|个|位))'),
    ('当…时', r'当[^，。\n]{2,18}(?:时|的时候)[，,]'),
    ('被字成串', r'被[^，。\n]{1,10}[，,][^，。\n]{0,12}被'),
    ('导致/使得', r'导致|使得|以至于'),
    ('性度化', r'[一-鿿]{2}(?:性|度|化)(?=的[一-鿿])'),
]
CATS['假大空'] = [
    ('大词', r'命运|宿命|羁绊|永恒|荣耀|信仰的力量|光明与黑暗|历史的|时代的洪流|岁月'),
    ('无名的宏大主语', r'(?:人们|世人|整个大陆|所有人|无数)(?:都|皆|将|会|曾)'),
    ('形容词通胀', r'古老的|神秘的|强大的|伟大的|可怕的|无尽的|深不可测|难以(?:言喻|名状|想象)'),
]
CATS['废话衔接'] = [
    ('换句话说', r'换句话说|也就是说|总而言之|总之|值得一提|不得不说|毫无疑问|可以说|某种意义上|事实上|实际上|说到底|归根结底'),
    ('重申否定', r'(?:并|也)不是说|这并不(?:是|意味)'),
]
CATS['作者口癖'] = [
    ('那一X', r'那一(?!年|天|夜|月|条|页|本|节|份|位|个|家|座|段|次|回|刻|日|晚|冬|夏|春|秋|边|头|半|带|路|行|章|卷|场|仗|战|代|辈|纪|步|层|顿|句|张|块|把|支|只|件|样|种|批|队|群|口|扇|道|面|根|颗|枚|粒|盏|杯|碗|瓶|袋|车|船|匹|声|眼|下|拨|窗|栏|格|列|排|圈|点|滴|勺)[一-鿿]'),
    ('不写成…也不写成', r'不写成[^。\n]{2,30}也不写成'),
    ('照旧', r'照旧'),
]

SKIP_LINE = re.compile(r'^\s*(?:>\s*条目设置|\||```|〔图|\[图)')


def read_body(path):
    out = []
    code = False
    for raw in open(path, encoding='utf-8', errors='replace'):
        line = raw.rstrip('\n')
        if line.startswith('```'):
            code = not code
            continue
        if code:
            continue
        if re.match(r'^##\s*设计备注', line):
            break
        if SKIP_LINE.match(line):
            continue
        out.append(line)
    return out


def sentences(text):
    return [s for s in re.split(r'[。？！\n]', text) if len(CJK.findall(s)) >= 2]


def shape_stats(lines):
    """骨架：连着四句以上差不多长的短句、单句成段的比例、一句里四个以上的「的」、同一个句头连用。"""
    hits = collections.defaultdict(list)
    paras = [l for l in lines if l.strip() and not l.lstrip().startswith('#')]
    single = 0
    prose = 0
    for p in paras:
        ss = sentences(re.sub(r'^[\s\-*>]+', '', p))
        if not ss:
            continue
        if not re.match(r'^\s*[-*>]', p):
            prose += 1
            if len(ss) == 1 and len(CJK.findall(ss[0])) <= 14:
                single += 1
        lens = [len(CJK.findall(s)) for s in ss]
        run = 1
        for i in range(1, len(lens)):
            if lens[i] <= 12 and lens[i - 1] <= 12 and abs(lens[i] - lens[i - 1]) <= 3:
                run += 1
                if run == 5:
                    hits['短句连排'].append(p[:120])
            else:
                run = 1
        for s in ss:
            if s.count('的') >= 5 and len(CJK.findall(s)) <= 60:
                hits['的的不休'].append(s.strip()[:120])
        heads = [re.sub(r'^[\s\-*>“"（(【]+', '', s)[:2] for s in ss]
        for i in range(2, len(heads)):
            if heads[i] and heads[i] == heads[i - 1] == heads[i - 2] and CJK.match(heads[i]):
                hits['三句同头'].append(p[:120])
                break
    if prose >= 20 and single / prose >= 0.3:
        hits['单句成段多'].append('单句成段 %d/%d 段' % (single, prose))
    return hits


def scan(path, only=None):
    lines = read_body(path)
    text = '\n'.join(lines)
    n = len(CJK.findall(text))
    res = collections.OrderedDict()
    for cat, pats in CATS.items():
        if only and cat not in only:
            continue
        got = []
        for label, pat in pats:
            rx = re.compile(pat)
            for ln in lines:
                for m in rx.finditer(ln):
                    s = max(0, m.start() - 18)
                    got.append((label, ln[s:m.end() + 18].strip()))
        res[cat] = got
    if not only or '骨架' in only:
        sh = shape_stats(lines)
        res['骨架'] = [(k, v) for k, vs in sh.items() for v in vs]
    return n, res


def walk(args):
    for a in args:
        if os.path.isdir(a):
            for root, _, fs in os.walk(a):
                for f in sorted(fs):
                    if f.endswith('.md'):
                        yield os.path.join(root, f)
        else:
            yield a


def main():
    argv = sys.argv[1:]
    show = '--lines' in argv
    tsv = '--tsv' in argv
    only = None
    top = 12
    mind = 0.0
    paths = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--only':
            only = set(argv[i + 1].split(','))
            i += 1
        elif a == '--top':
            top = int(argv[i + 1])
            i += 1
        elif a == '--min':
            mind = float(argv[i + 1])
            i += 1
        elif not a.startswith('--'):
            paths.append(a)
        i += 1
    rows = []
    for p in walk(paths):
        n, res = scan(p, only)
        if n < 200:
            continue
        tot = sum(len(v) for k, v in res.items() if k != '作者口癖')
        dens = tot * 10000.0 / n
        rows.append((dens, p, n, res))
    rows.sort(key=lambda r: -r[0])
    cats = list(rows[0][3].keys()) if rows else []
    if tsv:
        print('\t'.join(['文件', '字数'] + cats + ['每万字']))
    for dens, p, n, res in rows:
        if dens < mind:
            continue
        if tsv:
            print('\t'.join([p.replace('\\', '/'), str(n)] + [str(len(res[c])) for c in cats] + ['%.1f' % dens]))
            continue
        print('%6.1f/万字  %6d字  %s' % (dens, n, p.replace('\\', '/')))
        print('        ' + '  '.join('%s %d' % (c, len(res[c])) for c in cats if res[c]))
        if show:
            for c in cats:
                if not res[c]:
                    continue
                cnt = collections.Counter(l for l, _ in res[c])
                print('    [%s] %s' % (c, '，'.join('%s×%d' % kv for kv in cnt.most_common())))
                for label, s in res[c][:top]:
                    print('      · %s｜%s' % (label, s))


if __name__ == '__main__':
    main()
