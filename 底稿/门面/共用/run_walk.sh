#!/usr/bin/env bash
# 四本书的全书走查（11-18 门面卡片跟上那一轮写的）：各起一个无头 Chrome（端口照各本 act_all.mjs 里写的：
# 月银纪 9335、纷争纪 9341、山铜纪 9336、迷宫纪 9337），电脑 1920×945、手机 390×844 各走一遍，日志写 <输出目录>/<书>_<宽>.log。
#   bash 底稿/门面/共用/run_walk.sh <输出目录> [serial]
# 先用 .claude/launch.json 的 front-book、front-strife、front-bronze、front-maze 把四个本地服务起起来（8768 到 8771）。
# 四本并着跑省时间，可载东西会互相抢：11-18 山铜纪电脑那一遍报过两百多处“没有你的那一版没出来”（剧透开关没开上），
# 月银纪报过一条一次性的 Failed to fetch，单独重跑都是 0。并着跑报了对不上，先单独重跑那一本，或者第二个参数写 serial 一本一本跑。
# 跑完脚本不会自己退（它起的 Chrome 还开着）：看日志齐了就把这四个 Chrome 停掉。
SP="${1:?要一个放日志和浏览器资料的目录}"
MODE="${2:-parallel}"
CH="/c/Program Files/Google/Chrome/Application/chrome.exe"
F="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$SP/walk"
start_chrome() {
  MSYS_NO_PATHCONV=1 "$CH" --headless=new --hide-scrollbars --no-first-run --enable-unsafe-swiftshader --remote-debugging-port=$1 --user-data-dir="$SP/chrome_$1" --window-size=1920,945 about:blank >/dev/null 2>&1 &
}
for p in 9335 9341 9336 9337; do start_chrome $p; done
for i in 1 2 3 4 5 6 7 8 9 10 11 12; do
  ok=0
  for p in 9335 9341 9336 9337; do curl -s -o /dev/null "http://127.0.0.1:$p/json/version" && ok=$((ok+1)); done
  [ $ok -eq 4 ] && break
  sleep 2
done
echo "Chrome 起了 $ok 个"
walk() {   # 目录 名字
  cd "$F/$1" || return
  for wh in "1920 945" "390 844"; do
    set -- "$1" "$2" $wh
    for try in 1 2; do
      timeout 1500 node act_all.mjs $3 $4 > "$SP/walk/$2_$3.log" 2>&1
      rc=$?
      [ $rc -eq 0 ] && break
      echo "[重跑] $2 $3 退出码 $rc" >> "$SP/walk/$2_$3.log"
    done
    echo "$2 $3×$4 退出码 $rc，末尾：$(tail -3 "$SP/walk/$2_$3.log" | tr '\n' ' ' | cut -c1-300)"
  done
}
if [ "$MODE" = "serial" ]; then
  walk 小样_月银纪书 moon; walk 小样_纷争纪书 strife; walk 小样_山铜纪书 bronze; walk 小样_迷宫纪书 maze
else
  walk 小样_月银纪书 moon &
  W1=$!
  walk 小样_纷争纪书 strife &
  W2=$!
  walk 小样_山铜纪书 bronze &
  W3=$!
  walk 小样_迷宫纪书 maze &
  W4=$!
  wait $W1 $W2 $W3 $W4
fi
echo 走查完
