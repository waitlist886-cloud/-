#!/usr/bin/env bash
# 立绘铺开（11-05）：一页一页排队出图。先换身份参考，再照这一页的键出设定图、艺术照、表情。日志写 out/日志/<页>.log。
#   bash run_pages.sh 前传 q5b.json q4a.json        一页接一页
#   EXTRA="q6_kian" bash run_pages.sh 前传 q5b.json  先补出几个零散的键
cd "$(dirname "$0")"
PY="/c/Users/waitl/AppData/Local/Comfy-Desktop/ComfyUI-Installs/ComfyUI (1)/ComfyUI/.venv/Scripts/python.exe"
SET="$1"; shift
mkdir -p out/日志
if [ -n "$EXTRA" ]; then
  echo "== 零散 $EXTRA"
  CAST_SET="$SET" CAST_WORKERS=${CAST_WORKERS:-3} "$PY" -X utf8 gpt_sheet.py $EXTRA > "out/日志/零散_$(date +%H%M%S).log" 2>&1
fi
for f in "$@"; do
  name="${f%.json}"
  echo "== $SET $name $(date +%H:%M)"
  python -I -X utf8 resolve_identity.py --apply "$f" > "out/日志/${SET}_${name}_身份.log" 2>&1
  keys=$(python -I -X utf8 -c "import json,sys;print(' '.join(c['en'] for c in json.load(open(sys.argv[1],encoding='utf-8'))))" "cast/$SET/$f")
  CAST_SET="$SET" CAST_WORKERS=${CAST_WORKERS:-3} "$PY" -X utf8 gpt_sheet.py $keys > "out/日志/${SET}_${name}.log" 2>&1
  # 第二遍只补缺的：同一页里照别人的头画的（孩子照大人）头一遍参考图还没有，偶尔失败的也在这一遍补上
  CAST_SET="$SET" CAST_WORKERS=${CAST_WORKERS:-3} "$PY" -X utf8 gpt_sheet.py $keys >> "out/日志/${SET}_${name}.log" 2>&1
  echo "   好了 $(grep -c 好了 "out/日志/${SET}_${name}.log")  失败 $(grep -c 失败 "out/日志/${SET}_${name}.log")  切不开 $(grep -c 切不开 "out/日志/${SET}_${name}.log")"
done
echo "== 排完 $(date +%H:%M)"
