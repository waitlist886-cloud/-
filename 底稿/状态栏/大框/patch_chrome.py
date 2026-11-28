#!/usr/bin/env python3
# 只改平台外壳样式（platform_chrome.css）的时候用（11-28）：不整卡重打，把打好的卡里 injectStyles 第一行（css_cdn.py 写的外链说明）以后那一段换成新的 platform_chrome.css。
#   python -I -X utf8 底稿/状态栏/大框/patch_chrome.py <卡.json> [<卡.json> …]
# 第一行认 css_cdn.py 的记号，对不上就停，免得改了没走过 css_cdn 的卡。改完照旧跑 split_card、zip_cards。
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.path.join(HERE, 'platform_chrome.css')


def main():
    new = open(CHROME, encoding='utf-8').read()
    for p in sys.argv[1:]:
        card = json.load(open(p, encoding='utf-8'))
        s = card.get('injectStyles') or ''
        first = s.split('\n', 1)[0]
        if 'css_cdn.py' not in first:
            sys.exit('%s 的样式格头一行不是 css_cdn.py 写的，停' % p)
        stub = first + '\n' + new
        if stub == s:
            print('没变', p)
            continue
        card['injectStyles'] = stub
        if 'injectStylesSizeBytes' in card:
            card['injectStylesSizeBytes'] = len(stub.encode('utf-8'))
        json.dump(card, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print('换了', p, len(s), '→', len(stub), '字')


if __name__ == '__main__':
    main()
