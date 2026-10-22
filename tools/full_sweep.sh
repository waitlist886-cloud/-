#!/bin/bash
# 全卷复查：34 页时段页、二十二张、三首长诗，跟 HEAD 比。
# 用法（在仓库任意位置）：bash tools/full_sweep.sh
# 原神撞句那一栏要用 语料/ 下的两份文本（不进仓库，照 genshin-item-lore 的 fetch_corpus.py 重建），没有就显示空。
cd "$(dirname "$0")/.." || exit 1
H=$(mktemp -d)
printf "%-34s | %-8s | %-6s | %-10s | %-10s | %s\n" 文件 硬问题 撞句 命星 年份 受保护
for f in 月银纪史诗/第*歌_*.md 诸国期/诸国期时段_*.md 萨尔维斯/萨尔维斯时段_*.md 纷争纪/纷争纪时段_*.md 纷争纪/天黑以后_二十二张_第四版.md moon/poem_v10/天亮以前_第十稿_全文.md 诸国期/天亮以后_全文.md 萨尔维斯/天黑以前_全文.md; do
  b="$H/$(echo $f | tr '/' '_')"
  git show HEAD:"$f" > "$b" 2>/dev/null || cp "$f" "$b"
  h0=$(python3 -I -X utf8 tools/check_people_v7.py "$b" . 2>&1 | tail -1 | grep -o '硬问题合计 [0-9]*' | grep -o '[0-9]*')
  h1=$(python3 -I -X utf8 tools/check_people_v7.py "$f" . 2>&1 | tail -1 | grep -o '硬问题合计 [0-9]*' | grep -o '[0-9]*')
  ng=$(python3 -I -X utf8 tools/ngram.py "$f" 语料/原神武器文本.md 语料/原神圣遗物文本.md 2>&1 | tail -1 | grep -o 'hits [0-9]*' | grep -o '[0-9]*')
  case "$f" in
    纷争纪/纷争纪时段_*) yt="python3 -I tools/yeartest.py";;
    *) yt="python3 -I tools/yeartest_era.py";;
  esac
  if [[ "$f" == *时段_* || "$f" == 月银纪史诗/* ]]; then
    ab=$(diff <(python3 -I tools/abil_cross.py "$b" 2>&1 | grep -v '^L[0-9]') <(python3 -I tools/abil_cross.py "$f" 2>&1 | grep -v '^L[0-9]') | grep -c '^[<>]')
    if [[ "$f" == 纷争纪/* ]]; then
      yd=$(diff <($yt "$b" 2>&1 | sed 's/^L[0-9]* //') <($yt "$f" 2>&1 | sed 's/^L[0-9]* //') | grep -c '^[<>]')
    else
      yd=$(diff <($yt "$b" 月银纪 10081 2>&1 | sed 's/^L[0-9]* //') <($yt "$f" 月银纪 10081 2>&1 | sed 's/^L[0-9]* //') | grep -c '^[<>]')
    fi
    pr=$(python3 -I tools/check_protected.py "$b" "$f" 2>&1 | grep -o 'protected [A-Z]*' | head -1 | cut -d' ' -f2)
  else
    ab=-; yd=-; pr=-
  fi
  printf "%-34s | %s→%s | %s | 差%s行 | 差%s行 | %s\n" "$(basename $f .md)" "$h0" "$h1" "$ng" "$ab" "$yd" "$pr"
done
rm -rf "$H"
