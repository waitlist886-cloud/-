"""各页凡世至强的栏目名换成底卡洗稿那一套（10-25，照 底卡洗稿与命名重审_方向稿_第三版.md 第一节第2条）。

用法：python3 -I -X utf8 tools/relabel_legends.py [--apply] [文件 ...]
不给文件就扫各纪的源稿（月银纪、诸国期、萨尔维斯整页，纷争纪、山铜纪、前传的分段稿）。不加 --apply 只报。

换的：
  【后台能力收录｜AI一致性锚点】 → 【能力｜X】，X 照同一条里【独立声口｜X】的名字，没有就照标题 · 后头的名字
  可牵引线索 → 相关的事
  原创台词样例 → 台词样例
  首个高影响场景 → 头一回碰上
  ### 离场自转 → ### 玩家不在的时候
只在「## 凡世至强」起的那一节里换。声口补锚那一处要并进台词样例，脚本只报出来，手改。
改完照各页的拼法重拼。
"""
import re, sys, glob

SOURCES = ['月银纪史诗/第*歌_*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md',
           '纷争纪/parts/*.md', '纷争纪/parts[2-7]/*.md', '山铜纪/parts[1-6]/*.md', '迷宫纪前传/parts[1-5]/*.md']
SIMPLE = [('可牵引线索', '相关的事'), ('原创台词样例', '台词样例'), ('首个高影响场景', '头一回碰上'),
          ('### 离场自转', '### 玩家不在的时候')]


def fix(text):
    lines = text.split('\n')
    out, n, manual = [], 0, []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if not ln.startswith('## 凡世至强'):
            out.append(ln); i += 1
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith('## '):
            j += 1
        sec = lines[i:j]
        voice = None
        for s in sec:
            m = re.search(r'【独立声口｜([^】]+)】', s)
            if m:
                voice = m.group(1); break
        if voice is None:
            m = re.match(r'## 凡世至强：.*?· ?([^（(·\s]+)', ln)
            voice = m.group(1) if m else None
        for k, s in enumerate(sec):
            t = s
            if '【后台能力收录｜AI一致性锚点】' in t:
                if voice:
                    t = t.replace('【后台能力收录｜AI一致性锚点】', '【能力｜%s】' % voice)
                else:
                    manual.append(('没认出名字', ln))
            for a, b in SIMPLE:
                t = t.replace(a, b)
            if '声口补锚' in t:
                manual.append(('声口补锚', t[:40]))
            if t != s:
                n += 1
            out.append(t)
        i = j
    return '\n'.join(out), n, manual


def main(argv):
    apply = '--apply' in argv
    files = [a for a in argv if a != '--apply']
    if not files:
        for p in SOURCES:
            files += sorted(glob.glob(p))
    tot = 0
    for f in files:
        s = open(f, encoding='utf-8').read()
        new, n, manual = fix(s)
        if n or manual:
            print('%s：换 %d 行' % (f, n))
            for why, what in manual:
                print('  要手改（%s）：%s' % (why, what))
        if apply and new != s:
            open(f, 'w', encoding='utf-8').write(new)
        tot += n
    print('合计 换 %d 行%s' % (tot, '' if apply else '（只报，加 --apply 才写）'))


if __name__ == '__main__':
    main(sys.argv[1:])
