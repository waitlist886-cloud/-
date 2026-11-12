#!/bin/bash
# 让 Gemini 4 Argon 照文件夹里的 任务.md 写一轮回复。用法：run_agy.sh <文件夹…>（几个文件夹并着跑）
MODEL="${AGY_MODEL:-gemini-4-argon-medium}"
for d in "$@"; do
  (
    cd "$d" || exit 1
    rm -f 回复.md
    "/c/Users/waitl/AppData/Local/agy/bin/agy.exe" -p "照本文件夹的 任务.md 做。" --model "$MODEL" --mode accept-edits --output-format stream-json > agy.jsonl 2> agy_err.txt
    echo "agy exit $? $(date +%H:%M:%S)" >> agy_err.txt
  ) &
done
wait
for d in "$@"; do
  echo "== $d"; tail -n 1 "$d/agy_err.txt"; ls -la "$d/回复.md" 2>/dev/null || echo "没有 回复.md"
done
