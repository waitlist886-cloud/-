#!/usr/bin/env bash
# 11-25b 打卡一串（换账号以后那一回）：拿已经整跑过的 v12（不加 --fast）往下打：四纪大框 → 样式外链 → 薄壳 → 切 DLC → 分批 → 打包。
# 用法：bash 底稿/DLC/tools/build_all_1125b.sh <v12 输出目录> <四纪大框临时目录> [--fast-v12]
#   v12 输出目录里要有 奥尔德兰_日里版_四纪全卷_测试v12.json；加 --fast-v12 就先在仓库里跑一遍 v12 --fast 写进那个目录。
# 哪一步不过就停。临时目录是会话的，换会话照传参。
set -u
cd /e/aldran_art || exit 1
V="$1"; F="$2"; O="out/发布卡_四纪大框"
mkdir -p "$V" "$F"
PY="python -I -X utf8"
step() { echo "=== $1"; }
if [ "${3:-}" = "--fast-v12" ]; then
  step "v12 --fast"
  $PY out/进卡_v12/tools/build_v12.py . . "$V" --fast > "$V/build.log" 2>&1 || { echo "v12 失败"; tail -5 "$V/build.log"; exit 1; }
  grep -q '^问题 0 条' "$V/build.log" || { echo "v12 有问题"; grep -A12 '^问题' "$V/build.log" | cut -c1-240; exit 1; }
fi
head -1 "$V/build.log" | cut -c1-200
grep -m1 '^问题' "$V/build.log"
step 四纪大框
$PY 底稿/状态栏/大框/make_four_era_card.py out/发布卡_迷宫纪大框/底本_发布卡_11-08.json "$V/奥尔德兰_日里版_四纪全卷_测试v12.json" "$F" > "$F/make.log" 2>&1 || { echo "四纪大框失败"; tail -8 "$F/make.log" | cut -c1-300; exit 1; }
tail -3 "$F/make.log" | cut -c1-300
step 样式外链
$PY 底稿/状态栏/外链样式/css_cdn.py "$F/奥尔德兰_四纪大框.json" "$F/奥尔德兰_四纪大框_css.json" 2>&1 | tail -2 | cut -c1-240 || exit 1
[ -f "$F/奥尔德兰_四纪大框_css.json" ] || { echo "样式外链没出卡"; exit 1; }
step 薄壳
cp "$F/奥尔德兰_四纪大框_css.json" "$O/奥尔德兰_四纪大框_原介绍页.json" || exit 1
$PY 底稿/门面/共用/make_thin.py 2>&1 | tail -1
$PY 底稿/门面/共用/into_card.py "$O/奥尔德兰_四纪大框_原介绍页.json" "$O/奥尔德兰_四纪大框.json" 2>&1 | tail -2 | cut -c1-240 || exit 1
step 切DLC
$PY 底稿/DLC/tools/make_dlc.py "$O/奥尔德兰_四纪大框.json" --also "$O/奥尔德兰_四纪大框_原介绍页.json" --ver 11-25b > "$F/dlc.log" 2>&1
rc=$?
tail -50 "$F/dlc.log" | cut -c1-260
[ $rc -eq 0 ] || { echo "切 DLC 退出码 $rc"; exit 1; }
step 分批
$PY 底稿/门面/共用/split_card.py "$O/奥尔德兰_四纪大框.json" "$O/分批导入" 2>&1 | tail -14 | cut -c1-240 || exit 1
step 打包
$PY 底稿/门面/共用/zip_cards.py 11-25b --old --dlc 2>&1 | tail -12 | cut -c1-240
echo "=== 完"
ls -la "$O"/*.zip "$O/DLC" 2>/dev/null | cut -c24-200
