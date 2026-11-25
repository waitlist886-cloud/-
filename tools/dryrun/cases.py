#!/usr/bin/env python3
# 本地干跑·列开局：把 底稿/状态栏/大框/slim_card.py 的 cases()（门面各条主线的凭证头一行、回复底座）列出来，挑开局用。
#   python -I -X utf8 tools/dryrun/cases.py            列出 纪｜主线名｜凭证头一行
#   python -I -X utf8 tools/dryrun/cases.py 雨城清查    只列名字里带这几个字的，连整段最小凭证一起印
import os
import sys

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, '底稿', '状态栏', '大框'))
import slim_card as SL  # noqa: E402

key = sys.argv[1] if len(sys.argv) > 1 else None
for era, name, old, new, reply in SL.cases(ROOT):
    head = (new or old).split('\n', 1)[0]
    if key is None:
        print('%s｜%s｜%s' % (era, name, head))
    elif key in name:
        print('==== %s｜%s\n%s\n---- 回复底座的样子\n%s\n' % (era, name, new or old, reply or '（没有）'))
