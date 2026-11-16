#!/usr/bin/env bash
# 一份洗稿的活交给 Gemini 分块洗：一回只洗几节（默认至多四节、七千字上下），洗完一回再派下一回。
# 11-16 夜量出来的：Gemini 3.8 Flash 一口气洗一整份，洗到后头（第二个文件、命星、人物、遗迹）会走样，整块压成文言电报；
# 一回只给它几节，每一回都从头读一遍任务单，后头的节就跟前头一样规矩。
#   bash run_one_gemini_chunk.sh <份名> [K]
#   AGY_MODEL=gemini-3.8-flash-high（默认） FIXES=2
# 断在半路（额度、报错）重跑同一条命令就行：只派 稿/ 里跟 原/ 一字不差的节，洗过的不再动。
# 先要跑过 改派_gemini.py。后台跑着的时候别改这个脚本文件（bash 边读边跑）。
BASE="C:/Users/waitl/codex_work/wash_1115"
AGY="/c/Users/waitl/AppData/Local/agy/bin/agy.exe"
MODEL="${AGY_MODEL:-gemini-3.8-flash-high}"
FIXES="${FIXES:-2}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
j="$1"; K="${2:-4}"
d="$BASE/$j"; cd "$d" || exit 1
NOCMD="这里跑不了任何命令（run_command 一律被拒），不要试，也不用列目录。读文件用 read_file，改文件用 edit_file（一回换一节）。任务单里点到的别的文件（洗稿说明.md、样稿_改前.md、样稿_改后.md）都在本文件夹里，照名字直接读。"
rm -f 分块_派过.txt
quota=0
r=0
while [ $r -lt 16 ]; do
  LIST="$(python -I -X utf8 "$HERE/unwashed.py" "$j" "$K" 分块_派过.txt)"
  [ -z "$LIST" ] && break
  r=$((r+1))
  n=1; while [ -f "agy_第${n}遍.jsonl" ]; do n=$((n+1)); done
  P="照本文件夹的 任务_Gemini.md 做：先把它读完，再读 洗稿说明.md 和两份样稿。这一份活分几回洗，这一回只洗下面这几节（一行一节，竖线前头是文件，后头是 ## 标题），对着 原/ 里同名文件的同一节洗。别的节一个字不要动。洗完这几节就停，这一回不用交改动说明和删除单。
$LIST
$NOCMD"
  "$AGY" -p "$P" --model "$MODEL" --mode accept-edits --output-format stream-json > "agy_第${n}遍.jsonl" 2> agy_err.txt < /dev/null
  echo "== $j 第 $r 回（$(echo "$LIST" | wc -l) 节）exit $? $(date +%H:%M:%S)"
  if grep -q -i 'RESOURCE_EXHAUSTED\|quota reached\|quota exceeded\|"code":429' "agy_第${n}遍.jsonl" agy_err.txt 2>/dev/null; then quota=1; echo "   $j 额度报错，停"; break; fi
done
python -I -X utf8 "$HERE/eol_like.py" "$d/稿" "$d/原"
rm -rf "稿_Codex原样" && cp -r "稿" "稿_Codex原样"
python -I -X utf8 自查.py > 自查_收稿.txt 2>&1
(cd "$ROOT" && python -I -X utf8 底稿/洗稿/全卡精炼/查添.py "$j" --min 0.5) > 查添_收稿.txt 2>&1
res="$(tail -1 自查_收稿.txt | tr -d '\r')"; add="$(grep -c '^  \[' 查添_收稿.txt)"
echo "   $j 自查：$res｜查添 $add 句"
P2="上一遍洗完以后派活的人替你跑了两样检查，结果在本文件夹的 自查_收稿.txt 和 查添_收稿.txt 里。先读 任务_Gemini.md。一、自查_收稿.txt 里每一条以“错｜”开头的都改掉，只动报了错的那一块：报电报腔的那一块，直接把 原/ 里同一块的原句拿回来，再删掉重复的、不要紧的整句来收短，不许自己往句子里添字，改完不许比原稿长；报身份行丢了全名的，照原稿那一行的开头把名字、种族和行当补回；改了受保护的行的照原稿改回；原稿没有的数、新添的引语删掉或照原稿写；卡面不用的词换成白话。二、查添_收稿.txt 列的是你改写以后在原稿里找不到出处的句子（方括号里是节名），多半是写成了文言、书面话，或者把意思改歪了：逐句拿 原/ 里对应的原句换回来，原稿没有这件事的就删掉。以“看｜”开头的只是提醒，不用改。别的节不要动。
$NOCMD"
k=0
while [ "$quota" = 0 ] && [ $k -lt "$FIXES" ] && { ! echo "$res" | grep -q "^错 0" || [ "$add" -ge 4 ]; }; do
  k=$((k+1))
  n=1; while [ -f "agy_第${n}遍.jsonl" ]; do n=$((n+1)); done
  "$AGY" -p "$P2" --model "$MODEL" --mode accept-edits --output-format stream-json > "agy_第${n}遍.jsonl" 2>> agy_err.txt < /dev/null
  echo "== $j 改第 $k 遍 exit $? $(date +%H:%M:%S)"
  if grep -q -i 'RESOURCE_EXHAUSTED\|quota reached\|quota exceeded\|"code":429' "agy_第${n}遍.jsonl" agy_err.txt 2>/dev/null; then quota=1; echo "   $j 额度报错，停"; fi
  python -I -X utf8 "$HERE/eol_like.py" "$d/稿" "$d/原"
  rm -rf "稿_Codex原样" && cp -r "稿" "稿_Codex原样"
  python -I -X utf8 自查.py > 自查_收稿.txt 2>&1
  (cd "$ROOT" && python -I -X utf8 底稿/洗稿/全卡精炼/查添.py "$j" --min 0.5) > 查添_收稿.txt 2>&1
  res="$(tail -1 自查_收稿.txt | tr -d '\r')"; add="$(grep -c '^  \[' 查添_收稿.txt)"
  echo "   $j 自查：$res｜查添 $add 句"
done
left="$(python -I -X utf8 "$HERE/unwashed.py" "$j" 99 --count)"
echo "   $j 完 $(date +%H:%M:%S)｜洗了 $r 回，改了 $k 遍｜还没洗的节 $left｜额度报错 $quota"
