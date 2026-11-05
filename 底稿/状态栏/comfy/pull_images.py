#!/usr/bin/env python3
# 用户在一轮中途发的图不一定存进 uploads，会话记录（~/.claude/projects/…/会话号.jsonl）里有 base64。取最后几张存下来，就能当 GPT 的底稿或者参考。
#   python pull_images.py 会话记录.jsonl 输出目录 [张数，默认 14]
# 工具读图的结果也在里头，看文件名里的行号和类型分：用户发的多半是 webp，自己读的多半是 jpeg。人物参考放 语料/，不进库。
import base64
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
EXT = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp'}


def walk(o, lineno, found):
    if isinstance(o, dict):
        src = o.get('source')
        if o.get('type') == 'image' and isinstance(src, dict) and src.get('type') == 'base64':
            found.append((lineno, src.get('media_type'), src['data']))
        for v in o.values():
            walk(v, lineno, found)
    elif isinstance(o, list):
        for v in o:
            walk(v, lineno, found)


def main(path, out, n=14):
    os.makedirs(out, exist_ok=True)
    found = []
    with open(path, encoding='utf-8') as f:
        for lineno, line in enumerate(f):
            if '"base64"' not in line:
                continue
            try:
                walk(json.loads(line), lineno, found)
            except ValueError:
                continue
    print('一共', len(found), '张')
    for i, (lineno, mt, data) in enumerate(found[-n:]):
        name = 'tail_%02d_L%d.%s' % (i, lineno, EXT.get(mt, 'bin'))
        with open(os.path.join(out, name), 'wb') as f:
            f.write(base64.b64decode(data))
        print(name, mt)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 14)
