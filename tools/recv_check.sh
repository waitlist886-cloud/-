#!/bin/bash
# 收稿检查（10-31 补完那一轮用的）：bash tools/recv_check.sh 文件…，路径相对仓库根。每个文件一行合计，有问题的另列前几行。
cd "$(dirname "$0")/.." || exit 1
for f in "$@"; do
  [ -f "$f" ] || { echo "== $f 不存在"; continue; }
  cs=$(python3 -I -X utf8 tools/cardscan.py "$f" 2>&1 | grep -E '合计' | tail -1)
  cp=$(python3 -I -X utf8 tools/check_people_v7.py "$f" . 2>&1 | grep -E '硬问题' | tail -1)
  am=$(python3 -I -X utf8 tools/authormark.py "$f" 2>&1 | grep -E '合计' | tail -1)
  ng=$(python3 -X utf8 tools/ngram.py "$f" 语料 2>&1 | tail -1)
  rc=$(python3 -I -X utf8 tools/regex_check.py "$f" 2>&1 | grep -E '硬问题|合计' | tail -1)
  echo "== $f"
  echo "   cardscan: $cs | people: $cp | authormark: $am"
  echo "   ngram: $ng | regex: $rc"
  if grep -q '^### .* (\(Art\|Special\|Passive\) |' "$f"; then
    sl=$(python3 -I -X utf8 tools/starlint.py "$f" 2>&1 | tail -1)
    nl=$(python3 -I -X utf8 tools/namelint.py "$f" 2>&1 | tail -1)
    echo "   starlint: $sl | namelint: $nl"
  fi
done
