#!/bin/bash
# 拼纷争纪第 N 页：照 CLAUDE.md「文件」那一节写的次序，把 纷争纪/parts*/ 的分段 cat 成整页。
# 用法（在仓库根上）：bash tools/assemble_strife.sh N            把第 N 页（1 到 7）拼好写回 纷争纪/纷争纪时段_*.md
#                     bash tools/assemble_strife.sh N --verify   不写盘，拿 HEAD 里的分段拼一遍，跟 HEAD 里的整页逐字节比
# 改了分段先跑 --verify 确认次序没错（HEAD 拼出来应当跟 HEAD 的整页一样），再不带参数跑一遍写回。
# 10-30 添空档短主线（底稿/纷争纪/空档主线_计划.md 第三节）：第四到六页的次序里加了新主线分段和人物文件（照年份插），
# 不在的文件跳过；星的文件（X 那一行）不单独接，并进命星一节最后那一行「> 条目设置」以前。--verify 只拿 HEAD 里有的文件。
set -u
cd "$(dirname "$0")/.." || exit 1
N=${1:?要给页号 1 到 7}
X=""
case $N in
1) D=纷争纪/parts;  OUT=纷争纪/纷争纪时段_一_灰的年月.md;  L="p1_head p2_overview p3_line1 p4_line2 p5_line3 p6_stars p7_people p8_notes";;
2) D=纷争纪/parts2; OUT=纷争纪/纷争纪时段_二_白石的年月.md; L="";;
3) D=纷争纪/parts3; OUT=纷争纪/纷争纪时段_三_灯的年月.md; L="r1 r2 r3 r3b r4 r5 r6 r7 r7b r8"; X="r6b";;
4) D=纷争纪/parts4; OUT=纷争纪/纷争纪时段_四_炮的年月.md; L="t1 t2 t3 t3a t3b t4 t5 t5b t5c t5d t6_stars t7_people t7b t7c t7d t7e t7f t8_notes"; X="t6b t6c t6d t6e t6f";;
5) D=纷争纪/parts5; OUT=纷争纪/纷争纪时段_五_浮塔的年月.md; L="u1 u2 u2b u2c u2d u3 u4 u4b u4c u5 u5b u6_stars u7_people u7b u7c u7d u7e u7f u7g u8_notes"; X="u6b u6c u6d u6e u6f u6g";;
6) D=纷争纪/parts6; OUT=纷争纪/纷争纪时段_六_铁狼的年月.md; L="v1 v2 v3 v3b v3c v3d v3e v4 v6_stars v7_people v7b v7c v7d v7e v7a_cenwa v8_notes"; X="v6c v6d v6e v6f";;
7) D=纷争纪/parts7; OUT=纷争纪/纷争纪时段_七_号角的年月.md; L="w1 w2 w3 w4 w5 w6_stars w7_people w8_notes";;
*) echo "页号只认 1 到 7" >&2; exit 1;;
esac
pick() { ls $D/${1}*.md 2>/dev/null | grep -E "/${1}(_[^/]*)?\.md$" | head -1; }
files=()
if [ "$N" = 2 ]; then for k in q1_ q2_ q3_ q4_ q4b q5 q6 q7 q8 q9; do files+=($(ls $D/${k}*.md | head -1)); done
else for k in $L; do f=$(pick $k); [ -n "$f" ] && files+=("$f"); done; fi
xfiles=()
for k in $X; do f=$(pick $k); [ -n "$f" ] && xfiles+=("$f"); done
MODE=write; [ "${2:-}" = "--verify" ] && MODE=verify
python3 -I -X utf8 - "$MODE" "$OUT" "$N" "${#files[@]}" "${files[@]}" "${xfiles[@]}" <<'PY'
import sys, subprocess
mode, out, n, nf = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
files, xfiles = sys.argv[5:5 + nf], sys.argv[5 + nf:]
def read(f):
    if mode == 'verify':
        r = subprocess.run(['git', 'show', 'HEAD:' + f], capture_output=True)
        return r.stdout.decode('utf-8') if r.returncode == 0 else None
    return open(f, encoding='utf-8').read()
used, parts = [], []
xs = [(f, read(f)) for f in xfiles]
xs = [(f, t) for f, t in xs if t is not None]
for f in files:
    t = read(f)
    if t is None:
        continue
    if xs and '_stars' in f.split('/')[-1] and '\n> 条目设置' in t:
        k = t.rindex('\n> 条目设置') + 1
        ins = ''.join(x if x.endswith('\n') else x + '\n' for _, x in xs)
        head = t[:k] if t[:k].endswith('\n\n') else t[:k] + '\n'
        t = head + ins + ('' if ins.endswith('\n\n') else '\n') + t[k:]
        used.append(f.split('/')[-1] + '(+' + ' '.join(x.split('/')[-1] for x, _ in xs) + ')')
    else:
        used.append(f.split('/')[-1])
    parts.append(t)
print(' '.join(used))
whole = ''.join(parts)
if mode == 'verify':
    r = subprocess.run(['git', 'show', 'HEAD:' + out], capture_output=True)
    if r.stdout.decode('utf-8') == whole:
        print('HEAD 的分段拼出来跟 HEAD 的第 %s 页一样' % n)
    else:
        print('对不上：分段次序或文件名变了', file=sys.stderr); sys.exit(1)
else:
    open(out, 'w', encoding='utf-8').write(whole)
    print('写了 %s，%d 行' % (out, whole.count('\n')))
PY
