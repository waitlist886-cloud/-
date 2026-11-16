#!/usr/bin/env bash
# 撞了 Codex 额度、洗到一半停下的几份，额度回来（或者用户换了登录）以后接着洗：
#   bash 底稿/洗稿/全卡精炼/临时脚本/resume_wave.sh 铜1甲 铜1乙 …
# 会话号取这一份 codex.log 开头的 session id（第一回跑的那一个，存在 会话号.txt 里，往后每回都接同一个会话）。
# 旧的 codex.log 改名留底（codex_第N回.log），接着跑的输出写新的 codex.log。跑完照 run_wave.sh 留底、跑自查。
# 稿/ 里 Codex 已经洗过的字照旧在（它接着自己的会话往下做），所以别在接着洗以前重搭这一份活的文件夹。
BASE="C:/Users/waitl/codex_work/wash_1115"
CODEX="$LOCALAPPDATA/OpenAI/Codex/bin/14b838c1d074ff01/codex.exe"
PROMPT="上一回撞了额度停在半路。接着做完：照 AGENTS.md 和 洗稿说明.md，先看 稿/ 里哪几个文件、哪几节还没洗（跟 原/ 一字不差的就是没洗的），把没洗的洗完，再跑自查，把报错的都改掉（电报腔那一项也要改到没有错），最后交 改动说明.md 和 删除单.md。已经洗好的节不用重洗。"
pids=()
for j in "$@"; do
  (
    cd "$BASE/$j" || exit 1
    if [ ! -f 会话号.txt ]; then
      grep -m1 -i "session id" codex.log | sed 's/.*session id: *//' | tr -d '\r' > 会话号.txt
    fi
    sid="$(cat 会话号.txt)"
    if [ -z "$sid" ]; then echo "== $j 找不到会话号，跳过"; exit 1; fi
    n=1; while [ -f "codex_第${n}回.log" ]; do n=$((n+1)); done
    mv codex.log "codex_第${n}回.log"
    "$CODEX" exec resume --skip-git-repo-check -c 'sandbox_mode="workspace-write"' "$sid" "$PROMPT" > codex.log 2>&1 < /dev/null
    echo "== $j codex exit $? $(date +%H:%M:%S)"
    rm -rf "稿_Codex原样" && cp -r "稿" "稿_Codex原样"
    python -I -X utf8 自查.py > 自查_收稿.txt 2>&1
    echo "   $j 自查：$(tail -1 自查_收稿.txt | cut -c1-160)｜额度报错 $(grep -c 'hit your usage limit' codex.log) 回"
  ) &
  pids+=($!)
  sleep 5
done
wait
echo "这一拨都回来了 $(date +%H:%M:%S)"
