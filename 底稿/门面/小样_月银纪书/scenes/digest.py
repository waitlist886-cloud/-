#!/usr/bin/env python3
# 审稿用的摘要：一个时代一段，列主线和年份、各幅的名字和参考、死期、死的那一刻。
#   python -I -X utf8 digest.py m05 m06      只看这几个时代
#   python -I -X utf8 digest.py --names      只列玩家看得见的名字（节点和死的那一刻）
#   python -I -X utf8 digest.py --fates      只列死期
#   python -I -X utf8 digest.py --text m05_n2 m05_d_lisi   看这几幅的全文
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
moon = json.load(open(os.path.join(BOOK, 'data', 'moon.json'), encoding='utf-8'))
ERA = {e['id']: e for e in moon['eras']}


def load(eid):
    return json.load(open(os.path.join(HERE, eid + '.json'), encoding='utf-8'))


def years(s):
    return [int(x) for x in re.findall(r'\d{3,5}', s or '')]


def span(era, seg):
    """一条主线的年份（起、止）。没写的用时代的年份。"""
    for l in era['lines']:
        if l['name'] == seg and years(l.get('year')):
            y = years(l['year'])
            return min(y), max(y)
    y = years(era['years'])
    return (min(y), max(y)) if y else (0, 99999)


def people(era):
    out = {}
    for kind in ('cast', 'meet'):
        for c in era.get(kind, []):
            out[c['name']] = dict(c, kind=kind)
    return out


def main():
    args = sys.argv[1:]
    mode = [a for a in args if a.startswith('--')]
    ids = [a for a in args if re.match(r'^m\d\d$', a)] or sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(HERE, 'm??.json')))
    if '--text' in mode:
        want = [a for a in args if '_' in a]
        for eid in sorted({w.split('_')[0] for w in want}):
            d = load(eid)
            for s in d.get('nodes', []) + d.get('deaths', []):
                if s['key'] in want:
                    print('==', s['key'], s.get('name'), s.get('line', ''), s.get('act', ''), s.get('death', ''), s.get('age', ''), 'raw' if s.get('raw') else '')
                    print('who', s.get('who') or s.get('row'), 'beast', s.get('beast'), 'style', s.get('style'))
                    print('light:', s.get('light'))
                    print('camera:', s.get('camera'))
                    print(s.get('text'))
                    print('note:', s.get('note'))
                    print()
        return
    for eid in ids:
        era, d = ERA[eid], load(eid)
        ppl = people(era)
        key2 = {c['key']: c for c in era.get('cast', []) + era.get('meet', []) + era.get('legends', []) if c.get('key')}
        if '--names' in mode:
            print(eid, era['label'], era['title'], '｜', '　'.join('%s·%s' % (s.get('act') or '死', s['name']) for s in d.get('nodes', []) + d.get('deaths', [])))
            continue
        print('=' * 8, eid, era['label'], era['title'], era['years'])
        for l in era['lines']:
            print('  主线', l['name'], '｜', l.get('year'), '｜', '　'.join(a.split('。')[0][:14] for a in l['acts']))
        if '--fates' not in mode:
            for s in d.get('nodes', []):
                ps = s.get('who') or s.get('row') or []
                tags = []
                for p in ps:
                    c = key2.get(p[0])
                    tags.append('%s%s/%s' % (c['name'] if c else p[0], '(%s)' % c['age'] if c and c.get('age') is not None else '', p[1]))
                print('  %s %s「%s」%s %s%s%s %d词' % (s['key'], s['act'], s['name'], '+'.join(s['style']), ('row:' if s.get('row') else '') + '、'.join(tags),
                                               ' 兽:' + s['beast'] if s.get('beast') else '', ' RAW' if s.get('raw') else '', len(s['text'].split())))
                print('      注：', (s.get('note') or '')[:150])
        for n, f in (d.get('fates') or {}).items():
            c = ppl.get(n, {})
            a, b = span(era, c.get('seg'))
            ys = years(f.get('when'))
            flag = ''
            if ys and (max(ys) < a - 1 or min(ys) > b + 3):
                flag = '　【年份在主线 %d–%d 以外】' % (a, b)
            print('  死期 %s（%s，%s，开头%s岁）%s｜%s｜%s%s' % (n, c.get('kind', '？'), c.get('seg') or '', c.get('age'), '〔%s〕' % f['label'] if f.get('label') else '', f.get('when'), f.get('where'), flag))
            print('      ', f.get('how'))
        for s in d.get('deaths', []):
            ps = s.get('who') or s.get('row') or []
            print('  死的那一刻 %s %s %s岁%s「%s」%s %s%s%s' % (s['key'], s['death'], s.get('age'), '(minor)' if s.get('minor') else '', s['name'], '+'.join(s['style']),
                                                   '、'.join('%s/%s' % (p[0], p[1]) for p in ps), ' 兽:' + s['beast'] if s.get('beast') else '', ' RAW' if s.get('raw') else ''))
            print('      注：', (s.get('note') or '')[:150])
        for n in d.get('notes', []):
            print('  备注：', n[:200])
        print()


if __name__ == '__main__':
    main()
