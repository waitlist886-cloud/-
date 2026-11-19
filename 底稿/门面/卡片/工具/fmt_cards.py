# -*- coding: utf-8 -*-
"""卡片文件照原来的排版写回去：拿提交里的那一版试几种排法，哪一种一字不差就用哪一种重排现在的内容。
也当库用：save(路径, 对象) 照这个文件在提交里的排版写。
11-18 门面卡片跟上那一轮写的。卡片文件有两种排法（多数是一人一块、星一行一颗的紧凑排法，十来个是 indent=1），
脚本改卡片、共用/fix_lists.py 重写卡片以后都拿它排回去，免得提交里满是排版的差别。
  python -I -X utf8 底稿/门面/卡片/工具/fmt_cards.py      把四纪的卡片文件都照提交里的排法重排一遍"""
import io, json, os, subprocess, sys, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..')).replace('\\', '/') + '/'


def serA(o, ind=2):
    def val(v, lvl):
        pad = ' ' * (ind * (lvl + 1))
        if isinstance(v, dict):
            if not v:
                return '{}'
            items = [pad + json.dumps(k, ensure_ascii=False) + ': ' + val(x, lvl + 1) for k, x in v.items()]
            return '{\n' + ',\n'.join(items) + '\n' + ' ' * (ind * lvl) + '}'
        if isinstance(v, list):
            if all(isinstance(x, str) for x in v):
                return '[' + ', '.join(json.dumps(x, ensure_ascii=False) for x in v) + ']'
            items = [pad + '{' + ', '.join(json.dumps(k, ensure_ascii=False) + ': ' + json.dumps(x, ensure_ascii=False) for k, x in d.items()) + '}' for d in v]
            return '[\n' + ',\n'.join(items) + '\n' + ' ' * (ind * lvl) + ']'
        return json.dumps(v, ensure_ascii=False)
    return val(o, 0)


STYLES = {
    'A2': lambda o: serA(o, 2),
    'A1': lambda o: serA(o, 1),
    'S1': lambda o: json.dumps(o, ensure_ascii=False, indent=1),
    'S2': lambda o: json.dumps(o, ensure_ascii=False, indent=2),
    'S4': lambda o: json.dumps(o, ensure_ascii=False, indent=4),
    'C': lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')),
}
_cache = {}


def style_of(path):
    rel = os.path.relpath(path, ROOT).replace('\\', '/')
    if rel in _cache:
        return _cache[rel]
    r = subprocess.run(['git', '-C', ROOT, 'show', 'HEAD:' + rel], capture_output=True)
    if r.returncode != 0:
        _cache[rel] = (None, '\n', True)
        return _cache[rel]
    head = r.stdout.decode('utf-8')
    nl = '\r\n' if '\r\n' in head else '\n'
    body = head.replace('\r\n', '\n')
    tail = body.endswith('\n')
    obj = json.loads(body)
    got = None
    for k, f in STYLES.items():
        if f(obj) == body.rstrip('\n'):
            got = k
            break
    _cache[rel] = (got, nl, tail)
    return _cache[rel]


def save(path, obj, default='A2'):
    st, nl, tail = style_of(path)
    txt = STYLES[st or default](obj) + ('\n' if tail else '')
    io.open(path, 'w', encoding='utf-8', newline='').write(txt.replace('\n', nl))
    return st


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    miss = []
    for fp in sorted(glob.glob(ROOT + '底稿/门面/卡片/*/*.json')):
        obj = json.load(open(fp, encoding='utf-8'))
        st = save(fp, obj)
        if not st:
            miss.append(os.path.relpath(fp, ROOT))
    import collections
    print(collections.Counter(v[0] for v in _cache.values()))
    print('认不出排法的', miss)
