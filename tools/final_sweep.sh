#!/bin/bash
# 全卷复查（10-23 起用的那一份，10-24 收进仓库）：四十页、补卷、碑、二十二张，看眼下的样子，不跟 HEAD 比。
# 查卡面扫描、作者记号、check_people_v7 的硬问题、原神撞句。原神那一项要先把语料抓进 语料/（见 CLAUDE.md「换账号接手」）。
# 用法（在仓库根上）：bash tools/final_sweep.sh。跟 HEAD 逐页比改前改后用 tools/full_sweep.sh。
cd "$(dirname "$0")/.." || exit 1
PAGES=(月银纪史诗/第*歌_*.md 诸国期/诸国期时段_*.md 萨尔维斯/萨尔维斯时段_*.md 纷争纪/纷争纪时段_*.md 山铜纪/山铜纪时段_*.md)
echo "== cardscan 各页"; python3 -I -X utf8 tools/cardscan.py "${PAGES[@]}" | tail -1
echo "== cardscan 补卷、碑、二十二张"; python3 -I -X utf8 tools/cardscan.py 纷争纪/补卷/*.md 月银纪补卷/*.md 萨尔维斯/补卷/*.md 山铜纪/补卷/*.md 山铜纪/山铜纪_碑_第一版.md 纷争纪/天黑以后_二十二张_第六版.md | tail -1
echo "== authormark"; python3 -I -X utf8 tools/authormark.py "${PAGES[@]}" 纷争纪/补卷/*.md 月银纪补卷/*.md 萨尔维斯/补卷/*.md 山铜纪/补卷/*.md 山铜纪/山铜纪_碑_第一版.md | grep -v "照[A-I]份" | tail -1
echo "== check_people_v7 硬问题（只列不是 0 的页）"
for f in "${PAGES[@]}"; do h=$(python3 -I -X utf8 tools/check_people_v7.py "$f" . 2>/dev/null | grep -o "硬问题合计 [0-9]*" | grep -o "[0-9]*$"); [ "$h" != "0" ] && echo "  $f: $h"; done
echo "== 原神撞句（只列不是 0 的页）"
if [ -d 语料 ] && [ -n "$(ls -A 语料 2>/dev/null)" ]; then
  for f in "${PAGES[@]}"; do r=$(python3 -X utf8 tools/ngram.py "$f" 语料 2>/dev/null | tail -1 | grep -o "hits [0-9]*"); [ "$r" != "hits 0" ] && echo "  $f: $r"; done
else
  echo "  语料/ 是空的，这一项没查"
fi
echo done
