#!/usr/bin/env python3
# 此刻那一本旅伴档案“样子”那一栏（src/look_now.json）照卡里新的“外貌”重出（11-28 档案重写以后）。
#   python -I -X utf8 底稿/门面/小样_此刻书/tools/look_from_card.py [卡.json] [--apply]
# 外貌一样一样写部件（底稿/档案重写/档案口径.md）。门面这一栏另守 11-25 的两条：不拿前后比（这两年、这几年……那一句拿掉），不写罩杯三维；
# 身高和“看着几岁”从旧的那一句里取（体态数据里的身高也认），接在末尾。不加 --apply 只打印。
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(BOOK, '..', '..', '..'))
SRC = os.path.join(BOOK, 'src', 'look_now.json')
CMP = re.compile(r'这两年|这几年|这三年|这一年|比从前|蹿高|长开了|稚气淡了')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    card = args[0] if args else os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框.json')
    E = [e.get('content') or '' for e in json.load(open(card, encoding='utf-8'))['prompt']['lorebook']]
    d = json.load(open(SRC, encoding='utf-8'))
    out = {}
    for n, old in d['look'].items():
        b = next((e for e in E if re.search(r'(?m)^## 旅途同行：%s$' % re.escape(n), e)), '')
        m = re.search(r'(?m)^外貌：(.+)$', b)
        if not m:
            print('没找到外貌，照旧', n)
            out[n] = old
            continue
        sents = [s for s in re.split(r'(?<=。)', m.group(1)) if s.strip()]
        keep = ''.join(s for s in sents if not CMP.search(s) and not re.search(r'罩杯|[A-H]-cup|三维', s))
        h = re.search(r'(\d{3})cm', old) or re.search(r'身高 (\d{3})cm', b)
        age = re.search(r'看着([^，。]+岁)', old)
        tail = '，'.join(x for x in [(h.group(1) + 'cm') if h else '', ('看着' + age.group(1)) if age else ''] if x)
        out[n] = keep + (tail + '。' if tail else '')
        print(n, '｜', out[n])
    if '--apply' in sys.argv:
        d['look'] = out
        d['_说明'] = d.get('_说明', '') + ' 11-28 档案重写以后照卡里新的“外貌”重出（tools/look_from_card.py），拿前后比的那一句去掉，身高和看着几岁接在末尾。'
        json.dump(d, open(SRC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('写了', SRC)


if __name__ == '__main__':
    main()
