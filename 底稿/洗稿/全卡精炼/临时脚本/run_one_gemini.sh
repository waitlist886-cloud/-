#!/usr/bin/env bash
# 一份洗稿的活交给 Gemini 4 Argon（agy）洗完、留底、跑自查，报错就让它再改：bash run_one_gemini.sh <份名> [resume]
# 给 run_pool_gemini.sh 用的（一份一个进程）。做的事跟 run_wave_gemini.sh 里一份的那一段一样。
# 第二个参数写 resume：上一回断在半路，只洗还没洗的节。
#   AGY_MODEL=gemini-4-argon-high（默认） FIXES=2
BASE="C:/Users/waitl/codex_work/wash_1115"
AGY="/c/Users/waitl/AppData/Local/agy/bin/agy.exe"
MODEL="${AGY_MODEL:-gemini-4-argon-high}"
FIXES="${FIXES:-2}"
HERE="$(cd "$(dirname "$0")" && pwd)"
j="$1"
P1="照本文件夹的 任务_Gemini.md 做。先把它读完，再读 洗稿说明.md 和两份样稿，然后一节一节洗 稿/ 里的文件，整份洗完，最后交 改动说明.md 和 删除单.md。"
if [ "$2" = "resume" ]; then
  P1="这一份活上一回洗到一半停了。先读本文件夹的 任务_Gemini.md 和 洗稿说明.md。然后拿 稿/ 里的每个文件跟 原/ 里同名的文件一节一节比：## 标题底下跟 原/ 一字不差的节是还没洗的，别的节已经洗过了，一个字也不要再动。只把还没洗的节照任务单洗完（命星那一节照 ### 一颗一颗比），最后交 改动说明.md 和 删除单.md（已经有的就接着往下写）。"
fi
P2="上一遍洗完以后派活的人替你跑了自查，结果在本文件夹的 自查_收稿.txt 里。把里头每一条以“错｜”开头的都改掉：对着 原/ 里同一节改 稿/ 里那一节（电报腔的把句子写回完整的白话；改了受保护的行的照原稿改回；原稿没有的数、新添的引语删掉或照原稿写）。只动报了错的地方，别的节不要动。以“看｜”开头的只是提醒，不用改。"
d="$BASE/$j"; cd "$d" || exit 1
# 无头的 agy 跑不了命令：有的模型（Flash）头一步就想拿命令列目录，被拒以后整遍空着退出来。把文件名和能用的工具直接写进话里。
FILES="$(python -I -X utf8 -c "import json,os,io,sys; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8'); print('、'.join(os.path.basename(f) for f in json.load(open('job.json',encoding='utf-8'))['files']))")"
NOCMD=" 这里跑不了任何命令（run_command 一律被拒），不要试，也不用列目录。读文件用 read_file，改文件用 edit_file（一回换一节）。稿/ 和 原/ 里要洗的文件是：$FILES。任务单里点到的别的文件（洗稿说明.md、样稿_改前.md、样稿_改后.md）都在本文件夹里，照名字直接读。"
P1="$P1$NOCMD"; P2="$P2$NOCMD"
n=1; while [ -f "agy_第${n}遍.jsonl" ]; do n=$((n+1)); done
"$AGY" -p "$P1" --model "$MODEL" --mode accept-edits --output-format stream-json > "agy_第${n}遍.jsonl" 2> agy_err.txt < /dev/null
echo "== $j agy 头一遍 exit $? $(date +%H:%M:%S)"
python -I -X utf8 "$HERE/eol_like.py" "$d/稿" "$d/原"
rm -rf "稿_Codex原样" && cp -r "稿" "稿_Codex原样"
python -I -X utf8 自查.py > 自查_收稿.txt 2>&1
r="$(tail -1 自查_收稿.txt | tr -d '\r')"; echo "   $j 自查：$r"
k=0
while [ $k -lt "$FIXES" ] && ! echo "$r" | grep -q "^错 0"; do
  k=$((k+1)); n=$((n+1))
  "$AGY" -p "$P2" --model "$MODEL" --mode accept-edits --output-format stream-json > "agy_第${n}遍.jsonl" 2>> agy_err.txt < /dev/null
  echo "== $j agy 改第 $k 遍 exit $? $(date +%H:%M:%S)"
  python -I -X utf8 "$HERE/eol_like.py" "$d/稿" "$d/原"
  rm -rf "稿_Codex原样" && cp -r "稿" "稿_Codex原样"
  python -I -X utf8 自查.py > 自查_收稿.txt 2>&1
  r="$(tail -1 自查_收稿.txt | tr -d '\r')"; echo "   $j 自查：$r"
done
echo "   $j 完 $(date +%H:%M:%S)｜成功的遍数 $(cat agy_第*.jsonl | grep -c '"status":"SUCCESS"')｜额度报错 $(cat agy_第*.jsonl agy_err.txt 2>/dev/null | grep -c -i 'RESOURCE_EXHAUSTED\|quota exceeded\|"code":429')"
