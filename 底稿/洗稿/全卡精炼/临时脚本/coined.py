#!/usr/bin/env python3
# 找洗后新冒出来的“某某之战、之役、之乱、之夜、之冬、之变、之盟、之约”这一类名字（原稿整份里没有的）。
#   python -I -X utf8 coined.py <仓库里的文件…>   洗前取标签 详本_11-15
import io
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PAT = re.compile(r'[一-鿿]{1,5}之(?:战|役|乱|夜|冬|变|盟|约|围|祸|劫|灾|誓|名号)|[一-鿿]{2,6}(?:战役|会战|事变|惨案|血案)')
tot = 0
for f in sys.argv[1:]:
    new = open(f, encoding='utf-8').read().replace('\r', '')
    old = subprocess.run(['git', 'show', '详本_11-15:' + f], capture_output=True).stdout.decode('utf-8').replace('\r', '')
    m = re.search(r'^## [^\n]*设计备注', new, re.M)
    body = new[:m.start()] if m else new
    seen = set()
    for i, line in enumerate(body.split('\n'), 1):
        if line.startswith('> 条目设置'):
            continue
        for x in PAT.findall(line):
            # 取最短的那一截去原稿里找
            core = re.search(r'[一-鿿]{2}之(?:战|役|乱|夜|冬|变|盟|约|围|祸|劫|灾|誓|名号)|[一-鿿]{2}(?:战役|会战|事变|惨案|血案)', x)
            key = core.group(0) if core else x
            if key in old or key in seen:
                continue
            seen.add(key)
            tot += 1
            print('%s:%d｜%s｜%s' % (f.split('/')[-1], i, key, line.strip()[:110]))
print('合计', tot)
