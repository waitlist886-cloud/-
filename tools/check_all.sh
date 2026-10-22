#!/bin/bash
# 世界生长那一轮的新文件一并查：月银纪补卷和纷争纪补卷 16 到 39。
# 用法（在仓库任意位置）：bash tools/check_all.sh
cd "$(dirname "$0")/.." || exit 1
FILES=$(ls 月银纪补卷/*.md 纷争纪/补卷/补卷_1[6-9]_*.md 纷争纪/补卷/补卷_2[0-9]_*.md 纷争纪/补卷/补卷_3[0-9]_*.md 2>/dev/null)
echo "== 文件（每条的汉字，不算条目设置和设计备注）"
python3 -I -X utf8 - $FILES <<'PY'
import sys, re
for f in sys.argv[1:]:
    s = open(f, encoding='utf-8').read()
    for sec in re.split(r'(?m)^## ', s)[1:]:
        head = sec.split('\n', 1)[0]
        if head.startswith('设计备注'):
            continue
        body = '\n'.join(l for l in sec.split('\n')[1:] if not l.startswith('>'))
        print('%s｜%s｜%d' % (f.split('/')[-1], head, len(re.findall(r'[一-鿿]', body))))
PY
echo "== check_people_v7"
for f in $FILES; do python3 -I -X utf8 tools/check_people_v7.py "$f" . 2>&1 | grep -E "硬问题合计|硬|引用不存在|冒号|标点|词 " | sed "s|^|$f: |" | head -12; done
echo "== ngram（要 语料/ 下的两份文本）"
for f in $FILES; do python3 -I -X utf8 tools/ngram.py "$f" 语料/原神武器文本.md 语料/原神圣遗物文本.md 2>&1 | tail -1 | sed "s|^|$f: |"; done
echo "== yeartest_moon（月银纪）"
for f in 月银纪补卷/*.md; do python3 -I tools/yeartest_moon.py "$f" 2>&1 | sed "s|^|$f: |" | head -8; done
echo "== lint_salvis（只看禁名、真实世界、耐色瑞尔、原神、旧地名、引用；看| 一并列出）"
for f in $FILES; do python3 -I -X utf8 tools/lint_salvis.py "$f" 2>&1 | grep -E "硬\|(禁名|真实世界|耐色瑞尔|原神|旧地名|引用指不到)|看\|" | sed "s|^|$f: |"; done
echo "== regex_check"
python3 -I -X utf8 tools/regex_check.py $FILES 2>&1 | grep -E "硬|看|合计"
