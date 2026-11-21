#!/bin/bash
# 纷争纪铺开交稿的卡面检查（11-21）：bash tools/api/strife_scan.sh <拨>
# 每份先 fix_colons 去多余冒号分号，再跑 cardscan、check_people_v7、authormark、ngram，结果写 底稿/审稿/纷争纪/铺开/扫_<主线>.txt，末尾印一张合计。
cd "$(dirname "$0")/../.." || exit 1
W=${1:-1}
D=底稿/审稿/纷争纪/铺开
for f in $D/${W}_*.md; do
  n=$(basename "$f" .md); n=${n#${W}_}
  python -I -X utf8 tools/api/fix_colons.py "$f" > /dev/null
  o=$D/扫_$n.txt
  {
    echo "## cardscan"; python -I -X utf8 tools/cardscan.py "$f" 2>&1 | tail -40
    echo "## check_people_v7"; python -I -X utf8 tools/check_people_v7.py "$f" . 2>&1 | grep -v '^\s*$' | tail -40
    echo "## authormark"; python -I -X utf8 tools/authormark.py "$f" 2>&1 | tail -30
    if [ -n "$(ls 语料 2>/dev/null)" ]; then echo "## ngram（原神撞句）"; python -X utf8 tools/ngram.py "$f" 语料 2>&1 | tail -15; fi
  } > "$o"
  cs=$(grep -E '合计' "$o" | head -1)
  hp=$(grep -E '硬问题' "$o" | tail -1)
  printf '%-10s %s | %s\n' "$n" "$cs" "$hp"
done
