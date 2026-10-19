import json, sys
p = sys.argv[1]; idxs = [int(x) for x in sys.argv[2].split(',')]
card = json.load(open(p, encoding='utf-8'))
def find_wb(c):
    if isinstance(c, dict):
        for k, v in c.items():
            if isinstance(v, list) and v and isinstance(v[0], dict) and ('content' in v[0] or 'value' in v[0]):
                return v
            r = find_wb(v)
            if r: return r
    return None
wb = find_wb(card)
print('entries', len(wb))
for i in idxs:
    e = wb[i]
    txt = e.get('content') or e.get('value') or ''
    print('=== #%d' % i, (e.get('comment') or e.get('name') or '')[:60], len(txt))
    print(txt[:int(sys.argv[3]) if len(sys.argv)>3 else 3000])
