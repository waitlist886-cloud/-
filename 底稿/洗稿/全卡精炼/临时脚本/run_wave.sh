#!/usr/bin/env bash
# 一拨洗稿的活并着交给 Codex：bash run_wave.sh 月1 月2 …
# 每份的输出写在它自己文件夹的 codex.log，跑完把 稿/ 留一份底（稿_Codex原样/），再跑一遍自查。
BASE="C:/Users/waitl/codex_work/wash_1115"
CODEX="$LOCALAPPDATA/OpenAI/Codex/bin/14b838c1d074ff01/codex.exe"
PROMPT="照 AGENTS.md 做。先读 洗稿说明.md 和两份样稿，再一节一节洗 稿/ 里的文件，洗完跑自查，把报错的都改掉（电报腔那一项也要改到没有错），交 改动说明.md 和 删除单.md。"
pids=()
for j in "$@"; do
  (
    cd "$BASE/$j" || exit 1
    "$CODEX" exec -C "$BASE/$j" -s workspace-write --skip-git-repo-check "$PROMPT" > codex.log 2>&1 < /dev/null
    echo "== $j codex exit $? $(date +%H:%M:%S)"
    rm -rf "稿_Codex原样" && cp -r "稿" "稿_Codex原样"
    python -I -X utf8 自查.py > 自查_收稿.txt 2>&1
    echo "   $j 自查：$(grep -c '^错' 自查_收稿.txt) 条错，$(grep -c '^看' 自查_收稿.txt) 条看｜$(tail -1 自查_收稿.txt | cut -c1-160)"
  ) &
  pids+=($!)
  sleep 5
done
wait
echo "这一拨都回来了 $(date +%H:%M:%S)"
