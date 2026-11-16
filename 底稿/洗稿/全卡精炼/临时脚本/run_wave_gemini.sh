#!/usr/bin/env bash
# 一拨洗稿的活并着交给 Gemini 4 Argon（agy）：bash run_wave_gemini.sh 铜5己 铜5庚 …
# 先跑 改派_gemini.py 写好 任务_Gemini.md。agy 无头跑不了命令，所以自查在它交回来以后由这里跑：
#   头一遍洗完 → 留底（稿_Codex原样/，名字照旧是给收稿那几支脚本认的）→ 自查
#   自查还报“错”→ 把 自查_收稿.txt 指给它再改一遍，至多改 FIXES 遍（默认 2）
# 换行符照 原/ 归一。每一遍的输出留在 agy_第N遍.jsonl。
#   AGY_MODEL=gemini-4-argon-high（默认） FIXES=2
BASE="C:/Users/waitl/codex_work/wash_1115"
AGY="/c/Users/waitl/AppData/Local/agy/bin/agy.exe"
MODEL="${AGY_MODEL:-gemini-4-argon-high}"
FIXES="${FIXES:-2}"
HERE="$(cd "$(dirname "$0")" && pwd)"
P1="照本文件夹的 任务_Gemini.md 做。先把它读完，再读 洗稿说明.md 和两份样稿，然后一节一节洗 稿/ 里的文件，整份洗完，最后交 改动说明.md 和 删除单.md。"
P2="上一遍洗完以后派活的人替你跑了自查，结果在本文件夹的 自查_收稿.txt 里。把里头每一条以“错｜”开头的都改掉：对着 原/ 里同一节改 稿/ 里那一节（电报腔的把句子写回完整的白话；改了受保护的行的照原稿改回；原稿没有的数、新添的引语删掉或照原稿写）。只动报了错的地方，别的节不要动。以“看｜”开头的只是提醒，不用改。"
norm() { python -I -X utf8 "$HERE/eol_like.py" "$1/稿" "$1/原"; }
check() { (cd "$1" && python -I -X utf8 自查.py > 自查_收稿.txt 2>&1; tail -1 自查_收稿.txt | tr -d '\r'); }
for j in "$@"; do
  (
    d="$BASE/$j"; cd "$d" || exit 1
    n=1; while [ -f "agy_第${n}遍.jsonl" ]; do n=$((n+1)); done
    "$AGY" -p "$P1" --model "$MODEL" --mode accept-edits --output-format stream-json > "agy_第${n}遍.jsonl" 2> agy_err.txt < /dev/null
    echo "== $j agy 头一遍 exit $? $(date +%H:%M:%S)"
    norm "$d"
    rm -rf "稿_Codex原样" && cp -r "稿" "稿_Codex原样"
    r="$(check "$d")"; echo "   $j 自查：$r"
    k=0
    while [ $k -lt "$FIXES" ] && ! echo "$r" | grep -q "^错 0"; do
      k=$((k+1)); n=$((n+1))
      "$AGY" -p "$P2" --model "$MODEL" --mode accept-edits --output-format stream-json > "agy_第${n}遍.jsonl" 2>> agy_err.txt < /dev/null
      echo "== $j agy 改第 $k 遍 exit $? $(date +%H:%M:%S)"
      norm "$d"
      rm -rf "稿_Codex原样" && cp -r "稿" "稿_Codex原样"
      r="$(check "$d")"; echo "   $j 自查：$r"
    done
    echo "   $j 完｜$(grep -c '"status":"SUCCESS"' agy_第*.jsonl | tr '\n' ' ')｜额度报错 $(cat agy_第*.jsonl agy_err.txt 2>/dev/null | grep -c -i 'quota\|RESOURCE_EXHAUSTED\|429')"
  ) &
  sleep 3
done
wait
echo "这一拨都回来了 $(date +%H:%M:%S)"
