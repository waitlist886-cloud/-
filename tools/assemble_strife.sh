#!/bin/bash
# 拼纷争纪第 N 页：照 CLAUDE.md「文件」那一节写的次序，把 纷争纪/parts*/ 的分段 cat 成整页。
# 用法（在仓库根上）：bash tools/assemble_strife.sh N            把第 N 页（1 到 7）拼好写回 纷争纪/纷争纪时段_*.md
#                     bash tools/assemble_strife.sh N --verify   不写盘，拿 HEAD 里的分段拼一遍，跟 HEAD 里的整页逐字节比
# 改了分段先跑 --verify 确认次序没错（HEAD 拼出来应当跟 HEAD 的整页一样），再不带参数跑一遍写回。
set -u
cd "$(dirname "$0")/.." || exit 1
N=${1:?要给页号 1 到 7}
case $N in
1) D=纷争纪/parts;  OUT=纷争纪/纷争纪时段_一_灰的年月.md;  L="p1_head p2_overview p3_line1 p4_line2 p5_line3 p6_stars p7_people p8_notes";;
2) D=纷争纪/parts2; OUT=纷争纪/纷争纪时段_二_白石的年月.md; L="";;
3) D=纷争纪/parts3; OUT=纷争纪/纷争纪时段_三_灯的年月.md; L="";;
4) D=纷争纪/parts4; OUT=纷争纪/纷争纪时段_四_炮的年月.md; L="t1 t2 t3 t4 t5 t6_stars t7_people t8_notes";;
5) D=纷争纪/parts5; OUT=纷争纪/纷争纪时段_五_浮塔的年月.md; L="u1 u2 u3 u4 u5 u6_stars u7_people u8_notes";;
6) D=纷争纪/parts6; OUT=纷争纪/纷争纪时段_六_铁狼的年月.md; L="v1 v2 v3 v4 v6_stars v7_people v7a_cenwa v8_notes";;
7) D=纷争纪/parts7; OUT=纷争纪/纷争纪时段_七_号角的年月.md; L="w1 w2 w3 w4 w5 w6_stars w7_people w8_notes";;
*) echo "页号只认 1 到 7" >&2; exit 1;;
esac
files=()
if [ "$N" = 2 ]; then for k in q1_ q2_ q3_ q4_ q4b q5 q6 q7 q8 q9; do files+=($(ls $D/${k}*.md | head -1)); done
elif [ "$N" = 3 ]; then for k in r1 r2 r3 r4 r5 r6 r7 r8; do files+=($(ls $D/${k}_*.md | head -1)); done
else for k in $L; do files+=($(ls $D/${k}*.md 2>/dev/null | grep -E "/${k}(_[^/]*)?\.md$" | head -1)); done; fi
echo "${files[@]}" | tr ' ' '\n' | sed 's#.*/##' | tr '\n' ' '; echo
if [ "${2:-}" = "--verify" ]; then
  T=$(mktemp); trap 'rm -f "$T"' EXIT
  for f in "${files[@]}"; do git show HEAD:"$f" >> "$T"; done
  if git show HEAD:"$OUT" | cmp -s - "$T"; then echo "HEAD 的分段拼出来跟 HEAD 的第 $N 页一样"; else echo "对不上：分段次序或文件名变了" >&2; exit 1; fi
else
  cat "${files[@]}" > "$OUT"; echo "写了 $OUT，$(wc -l < "$OUT") 行"
fi
