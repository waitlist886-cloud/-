#!/usr/bin/env python3
# 审稿用的摘要：一组传奇的 who、at、quotes，和 falls 的时候、地方、经过、图名、参考图、场面全文。
#   python -I -X utf8 digest_legends.py gA [输出.md]
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
gid = sys.argv[1]
d = json.load(open(os.path.join(HERE, gid + '.json'), encoding='utf-8'))
o = ['# ' + gid, '']
for n, x in d.get('legends', {}).items():
    o.append('## ' + n)
    o.append('who｜' + x.get('who', ''))
    for s in x.get('at', []):
        o.append('at %s｜%s' % ('-'.join(map(str, s['cards'])), s['text']))
    for q in x.get('quotes', []):
        o.append('说｜' + q)
    if x.get('note'):
        o.append('注｜' + x['note'])
    o.append('')
o.append('# falls')
o.append('')
for f in d.get('falls', []):
    o.append('## %s %s「%s」%s%s%s' % (f['key'], f['death'], f.get('name', ''), ' raw' if f.get('raw') else '', ' young' if f.get('young') else '', ' noart' if f.get('noart') else ''))
    o.append('%s｜%s｜%s%s' % (f.get('when'), f.get('where'), f.get('how'), '｜' + f['label'] if f.get('label') else ''))
    if not f.get('noart'):
        o.append('who %s｜beast %s｜style %s' % (json.dumps(f.get('who', []), ensure_ascii=False), f.get('beast', '无'), f.get('style')))
        o.append('light｜' + f.get('light', ''))
        o.append('camera｜' + f.get('camera', ''))
        o.append(f.get('text', ''))
    if f.get('note'):
        o.append('注｜' + f['note'])
    o.append('')
for n in d.get('notes', []):
    o.append('- ' + n)
out = '\n'.join(o) + '\n'
if len(sys.argv) > 2:
    open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(out)
    print(sys.argv[2], len(out), '字')
else:
    sys.stdout.reconfigure(encoding='utf-8')
    print(out)
