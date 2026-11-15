"""底卡世界书合并查看：底本 src/rili_v7.json，洗稿层 底卡洗稿/*.md 整条盖上去（只读）。
11-14 盘点大迷宫生态那一回子任务写的，收进仓库时仓库根改成照这个文件的位置往上找。
用法（在仓库根上跑）：
  python -I -X utf8 底稿/迷宫纪前传/补完/盘点/wb.py show 1018,1019            整条打印（洗稿层优先，标明来源）
  python -I -X utf8 底稿/迷宫纪前传/补完/盘点/wb.py base 1018                 只看底本
  python -I -X utf8 底稿/迷宫纪前传/补完/盘点/wb.py kw 正则 [ctx] [--max N]   全量关键词，带条目号和标题
  python -I -X utf8 底稿/迷宫纪前传/补完/盘点/wb.py count 正则                各条命中数
"""
import json, re, sys, glob, os
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
card = json.load(open(os.path.join(REPO, "src", "rili_v7.json"), encoding="utf-8"))
lb = card["prompt"]["lorebook"]
wash = {}
for fp in sorted(glob.glob(os.path.join(REPO, "底卡洗稿", "*.md"))):
    text = open(fp, encoding="utf-8").read()
    for m in re.finditer(r"^## #(\d+) (.*)$", text, re.M):
        start = m.end()
        nxt = re.search(r"^## #\d+ ", text[start:], re.M)
        block = text[start:start + nxt.start()] if nxt else text[start:]
        body = re.search(r"^````[^\n]*\n(.*?)\n````\s*$", block, re.M | re.S)
        addt = re.search(r"^- 添触发：(.*)$", block, re.M)
        wash[int(m.group(1))] = {
            "title": m.group(2).strip(), "file": os.path.basename(fp),
            "body": body.group(1) if body else None,
            "addtrig": addt.group(1).strip() if addt else "",
        }

def entry(i):
    e = lb[i]
    w = wash.get(i)
    body = w["body"] if (w and w["body"]) else e["content"]
    src = ("洗稿层 " + w["file"]) if (w and w["body"]) else "底本"
    trig = "、".join(e.get("triggerWords") or [])
    if w and w["addtrig"]:
        trig += " ＋添：" + w["addtrig"]
    head = body.split("\n", 1)[0]
    return {"i": i, "body": body, "src": src, "trig": trig, "folder": e.get("folder"),
            "range": e.get("triggerRange"), "depth": e.get("scanDepth"), "head": head,
            "bl": "、".join(e.get("blackListWords") or [])}

def main():
    cmd = sys.argv[1]
    if cmd in ("show", "base"):
        for x in sys.argv[2].split(","):
            i = int(x)
            if cmd == "base":
                e = lb[i]
                print(f"==== #{i} 底本 ｜folder {e.get('folder')} ｜触发 {'、'.join(e.get('triggerWords') or [])}")
                print(e["content"]); print()
            else:
                d = entry(i)
                print(f"==== #{i} [{d['src']}] ｜folder {d['folder']} ｜范围 {d['range']} ｜深度 {d['depth']} ｜触发 {d['trig']} ｜黑名单 {d['bl'][:200]}")
                print(d["body"]); print()
    elif cmd == "kw":
        pat = re.compile(sys.argv[2]); ctx = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else 50
        mx = 100000
        if "--max" in sys.argv:
            mx = int(sys.argv[sys.argv.index("--max") + 1])
        n = 0
        for i in range(len(lb)):
            d = entry(i)
            for li, line in enumerate(d["body"].split("\n"), 1):
                for m in pat.finditer(line):
                    s = max(0, m.start() - ctx); e = min(len(line), m.end() + ctx)
                    print(f"#{i}|{d['head'][:28]}|L{li}: …{line[s:e]}…")
                    n += 1
                    if n >= mx: return
        print(f"[合计 {n} 处]")
    elif cmd == "count":
        pat = re.compile(sys.argv[2])
        rows = []
        for i in range(len(lb)):
            d = entry(i)
            c = len(pat.findall(d["body"]))
            if c: rows.append((c, i, d["head"][:40]))
        for c, i, h in sorted(rows, key=lambda r: -r[0]):
            print(f"{c:4d}  #{i}  {h}")
        print(f"[条目 {len(rows)}]")

if __name__ == "__main__":
    main()
