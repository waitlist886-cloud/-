#!/usr/bin/env python3
# 把 scenes/mNN.json 并进页面用的两张表：cg_table.json（哪一幅原画配哪一条主线的哪一幕、哪个人死的那一刻、叫什么）和 fate_table.json（死期和死因）。
# 第七歌是手写的，不动；别的时代照 scenes 重写（cg_table 里已有的 rev 留着）。跑完再跑 build_data.py 和 prep_assets.py cg。
#   python -I -X utf8 merge_scenes.py
import glob
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
BOOK = os.path.dirname(HERE)
ACTS = ['一幕', '二幕', '三幕', '收束']


def main():
    moon = json.load(open(os.path.join(BOOK, 'data', 'moon.json'), encoding='utf-8'))
    lines = {e['id']: [l['name'] for l in e['lines']] for e in moon['eras']}
    tp, fp = os.path.join(BOOK, 'cg_table.json'), os.path.join(BOOK, 'fate_table.json')
    old = json.load(open(tp, encoding='utf-8'))
    fates = json.load(open(fp, encoding='utf-8'))
    files = {os.path.basename(p)[:-5]: json.load(open(p, encoding='utf-8')) for p in sorted(glob.glob(os.path.join(HERE, 'm??.json')))}
    # 时代原画在前，再一个时代一个时代排：各幕（照主线、幕的次序，标了 first 的排在同一幕的前头），最后是死的那一刻
    table = {k: v for k, v in old.items() if v.get('key')}
    for eid in sorted(set(k.split('_')[0] for k in old) | set(files)):
        if eid not in files:      # 手写的（第七歌）原样留着
            table.update({k: v for k, v in old.items() if k.startswith(eid + '_') and not v.get('key')})
            continue
        d = files[eid]
        nodes = sorted(d.get('nodes', []), key=lambda s: (lines[eid].index(s['line']), ACTS.index(s['act']), 0 if s.get('first') else 1, s['key']))
        for s in nodes:
            t = {'line': s['line'], 'act': s['act'], 'name': s['name']}
            if old.get(s['key'], {}).get('rev'):
                t['rev'] = old[s['key']]['rev']
            table[s['key']] = t
        for s in d.get('deaths', []):
            t = {'death': s['death'], 'name': s['name']}
            if s.get('same'):
                t['src'] = s['same']
            elif old.get(s['key'], {}).get('rev'):
                t['rev'] = old[s['key']]['rev']
            table[s['key']] = t
        if d.get('fates'):
            fates[eid] = d['fates']
        else:
            fates.pop(eid, None)
    out = '{\n' + ',\n'.join('  %s: %s' % (json.dumps(k), json.dumps(v, ensure_ascii=False)) for k, v in table.items()) + '\n}\n'
    open(tp, 'w', encoding='utf-8', newline='\n').write(out)
    fates = {k: fates[k] for k in sorted(fates)}
    open(fp, 'w', encoding='utf-8', newline='\n').write(json.dumps(fates, ensure_ascii=False, indent=1) + '\n')
    n = [v for v in table.values() if v.get('line')]
    dd = [v for v in table.values() if v.get('death')]
    print('cg_table：时代原画', sum(1 for v in table.values() if v.get('key')), '节点', len(n), '死的那一刻', len(dd), '（其中借节点原画的', sum(1 for v in dd if v.get('src')), '）')
    print('fate_table：', len(fates), '个时代，', sum(len(v) for v in fates.values()), '条')


if __name__ == '__main__':
    main()
