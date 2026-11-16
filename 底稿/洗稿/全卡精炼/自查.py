#!/usr/bin/env python3
# 全卡精炼洗稿的自查：拿 稿/ 跟 原/ 比。只用标准库，放在活的文件夹里跑，也给主会话收稿用。
#   python -I -X utf8 自查.py [稿目录 原目录]
# 报“错”的要改掉，报“看”的自己看一眼。
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
NEW = sys.argv[1] if len(sys.argv) > 2 else os.path.join(HERE, '稿')
OLD = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, '原')
han = lambda s: len(re.findall(r'[一-鿿]', s))
PROT = re.compile(r'^(?:#{2,3} |> 条目设置|固定锚定：|底座：|体态数据|题：|篇：|章：|- 题：|专属羁绊：'
                  r'|[^\s【】：]{1,8}之章：【|【(?!调用)[^】｜]{1,14}】[^\n]*·[^\n]*玩家)')   # 末两样是羁绊章里紧跟标题的章名行和人物底座行（11-16 添）
FROZEN = re.compile(r'史诗|传唱|设计备注|传奇表|凡世至强')          # 这几种节整节不动（凡世至强是 11-16 添的：传奇条的格式是定好的，洗的时候被压丢了栏）
TICS = [('那一', 20), ('这一', 20), ('往后', 5), ('头一', 5), ('照旧', 5)]
BAN = ['——', '—', '；', '…', '！', '!', ';']
MOON = ['新月', '满月', '残月', '月牙', '弦月', '月亮', '月光']
# 仓库里卡面检查（tools/cardscan.py、check_people_v7.py）认的口径词，洗的时候别带进来
WORDS = ['时辰', '节气', '冬至', '春分', '守岁', '碗筷', '宜忌', '仪轨', '会盟', '诸侯', '城主', '管事', '史馆', '内侍', '诏书', '学塾', '驿卒', '官道', '佃户', '师门',
         '长衫', '伙计', '街坊', '学宫', '客栈', '朝廷', '门客', '掌柜', '客官', '百官', '丫头', '宗门', '长老', '功法', '镖局', '一丝', '一抹', '不禁', '威压', '修为',
         '登记', '军令', '条例', '晋升', '量子', '坐标', '频率', '能量', '系统', '除籍', '封锁令', '审批', '编制', '抚恤', '核验', '流程', '资质', '注册', '合规',
         '嘴角勾起', '玩味', '深不可测', '恐怖如斯']
# 往书面和文言上收的字：洗稿是把话说顺，不是把白话压成公文。比原稿密了就报
BOOKISH = ['仅', '仍', '则', '未', '便可', '由此', '此后', '遂', '皆', '均', '亦', '乃', '尚未', '并未', '传自', '可见', '如旧', '许久', '无法', '是否', '若', '之后']
RULES = ['玩家在场插手', '到了已识，往后的事看这一局', '下场照正史发生', '只取底座年份所在的那一段', '潮汐格写的是主线、幕间、收束还是自由都算', '的共战照战斗规则打', '正史里的下场是底，叙述里不点破，也不拿它吓玩家。']


def sections(text):
    """照 ## 标题切成节。回 [(标题, 正文)]，页头算一节（标题空）。"""
    out, cur, buf = [], '', []
    for l in text.split('\n'):
        if l.startswith('## '):
            out.append((cur, '\n'.join(buf)))
            cur, buf = l[3:].strip(), [l]
        else:
            buf.append(l)
    out.append((cur, '\n'.join(buf)))
    return out


def main():
    errs = looks = 0
    files = sorted(f for f in os.listdir(NEW) if f.endswith('.md'))
    for f in files:
        new = open(os.path.join(NEW, f), encoding='utf-8').read().replace('\r\n', '\n')
        old = open(os.path.join(OLD, f), encoding='utf-8').read().replace('\r\n', '\n')
        print('== %s｜%d 字 → %d 字（留 %d%%）' % (f, han(old), han(new), 100 * han(new) / max(1, han(old))))
        # 一、受保护的行：原来有的都得在，先后不变
        po = [l for l in old.split('\n') if PROT.match(l)]
        pn = [l for l in new.split('\n') if PROT.match(l)]
        miss = [l for l in po if l not in pn]
        add = [l for l in pn if l not in po]
        for l in miss[:12]:
            print('  错｜受保护的行没了或者改了：%s' % l[:70])
        for l in add[:12]:
            print('  错｜多出来的受保护行：%s' % l[:70])
        errs += len(miss) + len(add)
        if not miss and not add and po != pn:
            print('  错｜受保护的行先后变了')
            errs += 1
        # 二、整节不动的
        so, sn = dict(sections(old)), dict(sections(new))
        for t, body in so.items():
            if t and FROZEN.search(t):
                if sn.get(t) != body:
                    print('  错｜这一节整节不许动：%s' % t[:40])
                    errs += 1
        # 三、数：改后的数都得出自原稿
        do = set(re.findall(r'\d+(?:\.\d+)?', old))
        extra = sorted(set(re.findall(r'\d+(?:\.\d+)?', new)) - do, key=float)
        if extra:
            print('  错｜原稿没有的数：%s' % '、'.join(extra[:20]))
            errs += 1
        lost = sorted(do - set(re.findall(r'\d+(?:\.\d+)?', new)), key=float)
        years = [x for x in lost if len(x) >= 3]
        if years:
            print('  看｜洗掉的数（三位以上，多半是年份）%d 个：%s' % (len(years), '、'.join(years[:30])))
            looks += 1
        # 四、引号里的话：改后的引语都得是原稿里有的
        qo = set(re.findall(r'“([^”\n]{2,60})”', old))
        newq = [q for q in re.findall(r'“([^”\n]{2,60})”', new) if q not in qo and not any(q in x for x in qo)]
        for q in newq[:10]:
            print('  看｜原稿里没有的引语：“%s”' % q[:40])
        looks += len(newq)
        # 五、卡面：标点、月相字、句中的冒号（冻住的节和条目设置不查）
        body = []
        for t, b in sections(new):
            if not (t and FROZEN.search(t)):
                body += [l for l in b.split('\n') if not l.startswith('> ')]
        btxt = '\n'.join(body)
        for ch in BAN:
            n = btxt.count(ch)
            if n:
                on = sum(b.count(ch) for t, b in sections(old) if not (t and FROZEN.search(t)))
                if n > on:
                    print('  错｜禁用标点 %s 比原稿多（%d → %d）' % (ch, on, n))
                    errs += 1
        for w in MOON:
            if btxt.count(w) > old.count(w):
                print('  错｜月相字多了：%s' % w)
                errs += 1
        # 口径词：这张卡的卡面不用的词，洗后比原稿多了就报（原稿本来有的不算）
        for w in WORDS:
            if btxt.count(w) > old.count(w):
                print('  错｜卡面不用的词多了：%s（换个白话的说法，比如晋升写成到某一档、登记写成记名）' % w)
                errs += 1
        # 机制用语照原稿：底卡通篇写“判定获得优势”，洗后写成“判定有优势”“判定占优”的报错
        mech = re.compile(r'判定(?:上)?(?:有|占|得|具有|带)(?:优势|劣势)|判定占优(?!势)')
        if len(mech.findall(btxt)) > len(mech.findall(old)):
            print('  错｜机制用语改了字：“判定获得优势”“判定获得劣势”照原稿写，不写成“判定有优势”“判定占优”（%d 处）' % (len(mech.findall(btxt)) - len(mech.findall(old))))
            errs += 1
        for l in body:
            m = re.match(r'^(\s*(?:- )?(?:\*\*)?)([^：\n“”｜]{9,})：', l)
            if m and '：' not in l[:len(m.group(1)) + 9] and not l.lstrip().startswith(('|', '>')):
                if l not in old:
                    print('  看｜冒号前头超过八个字，或者冒号用在了句子中间：%s' % l.strip()[:44])
                    looks += 1
        # 六、口癖和规矩句
        w = han(btxt) / 1e4
        over = ['%s %.0f' % (k, btxt.count(k) / w) for k, hi in TICS if w and btxt.count(k) / w > hi]
        if over:
            print('  看｜口癖每万字超了（%s）' % '，'.join(over))
            looks += 1
        obody = '\n'.join(l for t, b in sections(old) if not (t and FROZEN.search(t)) for l in b.split('\n') if not l.startswith('> '))
        ow = han(obody) / 1e4
        thick_words = []
        for k in BOOKISH:
            a, c = obody.count(k), btxt.count(k)
            if c >= 4 and w and ow and c / w > 1.6 * (a / ow) + 1:
                thick_words.append('%s %d→%d' % (k, a, c))
        if thick_words:
            print('  错｜书面字比原稿密了（原稿几处→洗后几处，洗后的字数只有原稿一半上下，照原稿的白话改回去）：%s' % '，'.join(thick_words))
            errs += 1
        push = len(re.findall(r'见(?:主线|背景条|旅伴条|人物条|上文|下文)', btxt)) - len(re.findall(r'见(?:主线|背景条|旅伴条|人物条|上文|下文)', obody))
        if push > 3:
            print('  看｜“见主线”“见背景条”这类往外推的话比原稿多了 %d 处，各人的下场要写在各人的条里' % push)
            looks += 1
        left = [r for r in RULES if r in btxt]
        if left:
            print('  看｜该拿掉的规矩句还在：%s' % '｜'.join(left))
            looks += 1
        # 七、一节一节留了多少
        rows = []
        for t, b in sections(old):
            if not t or FROZEN.search(t):
                continue
            a, c = han(b), han(sn.get(t, ''))
            if t not in sn:
                print('  错｜这一节没了：%s' % t[:40])
                errs += 1
            elif a >= 300:
                rows.append((c / a, a, c, t))
        thick = [r for r in rows if r[0] > 0.78 and r[1] > 800]
        thin = [r for r in rows if r[0] < 0.3]
        for r in thick[:8]:
            print('  看｜留得太多，没怎么收（%d → %d）：%s' % (r[1], r[2], r[3][:36]))
        for r in thin[:8]:
            print('  看｜留得不到三成（%d → %d）：%s' % (r[1], r[2], r[3][:36]))
        looks += len(thick) + len(thin)
        # 八、电报腔：收短该靠删句子、删重复，不该靠删虚字。一块一块量“的了着是在就也还把这那他她它”占汉字的比例，
        #     洗后的比例掉到原稿的七成以下，就是把白话压成了电报（“远打石，近杖挡”“最多抱一孩，停步即断”这一类）。
        #     用户认过的样稿这个数在七成七到九成三之间。
        tel_e, tel_l = [], []
        bo, bn = blocks(old), blocks(new)
        for t, b in bo.items():
            if FROZEN.search(t) or t not in bn:
                continue
            a, c = dens(b), dens(bn[t])
            if not a or not c or a[0] < 250 or c[0] < 120 or a[1] < 6:
                continue
            r = c[1] / a[1]
            if r < 0.70:
                tel_e.append((r, t, a, c))
            elif r < 0.76:
                tel_l.append((r, t, a, c))
        for r, t, a, c in sorted(tel_e)[:40]:
            print('  错｜电报腔（虚字的比例只有原稿的 %d%%，原稿每百字 %.1f 个，洗后 %.1f 个）：%s' % (r * 100, a[1], c[1], t[:36]))
        for r, t, a, c in sorted(tel_l)[:20]:
            print('  看｜偏电报腔（虚字的比例是原稿的 %d%%）：%s' % (r * 100, t[:36]))
        errs += len(tel_e)
        looks += len(tel_l)
        # 八之二、节首：## 这一代的命星、## 这一代的人物 标题底下到头一颗星、头一条人物以前那一段是给作者看的，不进卡，不许动
        for h in ('这一代的命星', '这一代的人物', '星'):
            io_, in_ = sec_intro(old, h), sec_intro(new, h)
            if io_ is not None and in_ is not None and io_.strip() != in_.strip():
                print('  错｜“## %s”标题底下、头一颗星或头一条人物以前的那一段是给作者看的，照原稿一字不动' % h)
                errs += 1
        # 八之三、星条【调用】开头的年月（某某的年月里、祭火期、诸国期）照原稿留着
        co, cn = star_calls(old), star_calls(new)
        lost = [k for k, v in cn.items() if k in co and ERA_HEAD.match(co[k]) and not ERA_HEAD.match(v) and ERA_HEAD.match(co[k]).group(1) not in v]
        if lost:
            print('  错｜星条【调用】开头的年月照原稿留着（%d 颗丢了，比如 %s）' % (len(lost), '、'.join(lost[:4])))
            errs += 1
        # 九、命星头一句：Special、Passive 是生来的天赋。原稿头一句写着“生来、天赋、体质”一类字的，洗后也得在
        so_full = {k: full for k, lead, full in star_leads(old)}
        for key, lead, full in star_leads(new):
            if key.endswith('（Special）') and key in so_full and full.strip() != so_full[key].strip():
                print('  错｜Special 命星的头一段要照原稿一字不动（那句老话是这颗星照着这个人命运的地方）：%s' % key)
                errs += 1
        so_st = {k: lead for k, lead, full in star_leads(old)}
        for key, lead, full in star_leads(new):
            if key.endswith('（Special）'):
                continue
            two = lambda s: '。'.join(s.split('。')[:2])
            # 第二个条件照 tools/starlint.py 的口径（头两句、它那张词表）：11-16 定手“一辈出不了几双”洗成“一辈难出几双”，光第一个条件没报
            if (BORN.search(so_st.get(key, '')) and not BORN.search(lead)) or (INNATE.search(two(so_full.get(key, ''))) and not INNATE.search(two(full))):
                print('  错｜命星头一句丢了“生来的体质、天赋”那一层（照原稿的说法补回几个字，“生来、生下来、天生、一辈出、血里带着”这一类原稿有的照留）：%s｜原稿：%s' % (key, so_st[key][:36]))
                errs += 1
        # 十、旅伴条“身份”那一行：原稿开头报的全名（名·姓）洗后还得在这一行里，模型认人靠它。
        #     11-16 Gemini 3.8 Flash 洗的几份常把“维布克·艾希，人族哨兵”收成“燕巢段城的哨兵”，名字和种族一起丢了。
        for t, b in sections(old):
            if not t.startswith('旅途同行：') or t not in sn:
                continue
            lo = [l for l in b.split('\n') if l.startswith('身份：')]
            ln_ = [l for l in sn[t].split('\n') if l.startswith('身份：')]
            if not lo or not ln_:
                continue
            m = re.match(r'身份：([^，。｜（(\s]{2,16})', lo[0])
            if m and '·' in m.group(1) and m.group(1) not in ln_[0]:
                print('  错｜旅伴条“身份”那一行开头的全名丢了（原稿开头是“%s”，照原稿那一行的开头把名字、种族和行当补回）：%s' % (lo[0][3:3 + 24], t[:30]))
                errs += 1
    print('错 %d，看 %d' % (errs, looks))


BORN = re.compile(r'生来|天赋|体质|生下来|打小|胎里|与生俱来|天生|生就|落地|娘胎|血里|骨头里|一出生|出生时|生在')
ERA_HEAD = re.compile(r'^【调用】((?:[一-鿿]{1,4}的年月|祭火期|万兽期|诸国期|萨尔维斯[一-鿿]{0,4}|[一-鿿]{2,4}纪)[里，])')


def sec_intro(text, head):
    """## head 标题底下，到头一个 ### 、下一个 ## 、> 条目设置 以前的那一段；没有这个标题回 None。"""
    m = re.search(r'^## ' + re.escape(head) + r'[ \t]*\n', text, re.M)
    if not m:
        return None
    e = re.search(r'^(?:### |## |> 条目设置)', text[m.end():], re.M)
    return text[m.end():m.end() + (e.start() if e else len(text) - m.end())]


def star_calls(text):
    """{星名: 【调用】那一行}"""
    out, cur = {}, None
    for ln in text.split('\n'):
        m = re.match(r'^### (.+?) \((?:Special|Passive|Art|Active)', ln)
        if m:
            cur = m.group(1).strip()
        elif cur and ln.startswith('【调用】') and cur not in out:
            out[cur] = ln
    return out


INNATE = re.compile(r'体质|天赋|生来|生下来|与生俱来|天生|一辈一辈|一辈出|打娘胎|胎里|血里带|骨子里')


def star_leads(text):
    """回 [(星名（类）, 头一句, 头一段)]：### 名字 (Special|Passive | 档) 底下头一行正文（跳过【调用】那一行）的头一句。"""
    out, ls = [], text.split('\n')
    for i, l in enumerate(ls):
        m = re.match(r'^### (.+?) \((Special|Passive) \| ', l)
        if not m:
            continue
        body = ''
        for k in ls[i + 1:i + 10]:
            k = k.strip()
            if k and not k.startswith(('#', '>', '【调用】', '- ')):
                body = k
                break
        out.append((m.group(1) + '（' + m.group(2) + '）', body.split('。')[0], body))
    return out


PART = set('的了着是在就也还把这那他她它')


def blocks(text):
    """照 ## 和 ### 标题切成块（量电报腔用，比节细一层）。回 {标题: 正文}，同名的接在一起。"""
    out, name, buf, top = {}, '', [], ''
    for l in text.split('\n'):
        if l.startswith('## ') or l.startswith('### '):
            if name:
                out[name] = out.get(name, '') + '\n'.join(buf) + '\n'
            if l.startswith('## '):
                top = l[3:].strip()
                name = top
            else:
                name = top[:14] + '｜' + l[4:].strip()
            buf = []
        elif not PROT.match(l) and not l.startswith('> '):
            buf.append(l)
    if name:
        out[name] = out.get(name, '') + '\n'.join(buf) + '\n'
    return out


def dens(t):
    h = re.findall(r'[一-鿿]', t)
    if not h:
        return None
    return len(h), 100.0 * sum(1 for c in h if c in PART) / len(h)


if __name__ == '__main__':
    main()
