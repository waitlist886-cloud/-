#!/bin/bash
# 洗稿收完一页、重拼以后的整页检查，洗前拿标签 详本_11-15 的同一页。
#   bash 底稿/洗稿/全卡精炼/临时脚本/页检.sh <拼好的页，路径相对仓库根> <分段目录> [放标签页的临时目录]
# 印：洗前洗后各一遍 recv_check（比的是合计那几个数），受保护的行，洗稿自己起的事件名，栏目，机制词，节首。
cd "$(dirname "$0")/../../../.." || exit 1
P="$1"; D="$2"; T="${3:-${TMPDIR:-/tmp}/页检_tag}"
ERA=$(dirname "$P")
mkdir -p "$T/$ERA"
TP="$T/$P"
git show "详本_11-15:$P" > "$TP" || exit 1
echo "######## 洗前（标签）"
bash tools/recv_check.sh "$TP" | sed 's#^== .*#== 标签页#'
echo "######## 洗后"
bash tools/recv_check.sh "$P"
echo "######## 行数 $(wc -l < "$TP") → $(wc -l < "$P")"
echo "######## 受保护的行"
python -I tools/check_protected.py "$TP" "$P" 2>&1 | tail -4
echo "######## 洗稿自己起的事件名"
python -I -X utf8 底稿/洗稿/全卡精炼/临时脚本/coined.py "$P" 2>&1 | tail -8
echo "######## 栏目"
python -I -X utf8 底稿/洗稿/全卡精炼/查栏目.py "$P" 2>&1 | tail -6
if [ -n "$D" ]; then
  echo "######## 机制词"
  python -I -X utf8 底稿/洗稿/全卡精炼/还原机制词.py --repo "$D"/*.md 2>&1 | tail -3
  echo "######## 节首"
  python -I -X utf8 底稿/洗稿/全卡精炼/还原节首.py --repo "$D"/*.md 2>&1 | tail -3
fi
