#!/usr/bin/env bash
# 风月平台自己的样式（聊天页那几个 css），下到 $1，给 static_bench_fy.mjs 的 css= 用。文件不进库，用的时候重下。
# 11-08 下的那一回九个文件，主要是 Tailwind 那一大份；聊天页的脚本（输入栏、翻页的结构）也在同一个地方，要看就照 chat 页面的 script 列表下
# （输入栏在 _next/static/chunks 里带 ai-mod-button2 那一个，翻页是 FyPagination）。
set -e
d=${1:?要下到哪个目录}
mkdir -p "$d"
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
curl -s -L -A "$UA" https://aisearches.xyz/zh/explore/installed/1 \
  | grep -o '/_next/static/chunks/[A-Za-z0-9_-]*\.css' | sort -u \
  | while read -r p; do curl -s -A "$UA" -o "$d/$(basename "$p")" "https://aisearches.xyz$p"; done
ls "$d"
