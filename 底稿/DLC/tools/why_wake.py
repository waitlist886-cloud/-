import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
OUT = sys.argv[1]
ROOT = sys.argv[2]
ents = json.load(open(os.path.join(OUT, 'v12_entries.json'), encoding='utf-8'))
if isinstance(ents, dict):
    ents = ents.get('entries') or list(ents.values())
reply = open(os.path.join(ROOT, 'moon', 'samples', 'reply_迷宫纪首轮_人类.html'), encoding='utf-8').read()
want = sys.argv[3:]
BS = chr(92)


def split_top(rx):
    out, depth, cur, esc, cls = [], 0, '', False, False
    for ch in rx:
        if esc:
            cur += ch; esc = False; continue
        if ch == BS:
            cur += ch; esc = True; continue
        if cls:
            cur += ch
            if ch == ']':
                cls = False
            continue
        if ch == '[':
            cls = True; cur += ch; continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == '|' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return out


def title(e):
    return (e.get('content') or '')[:160]


print('条目数', len(ents), '键', list(ents[0].keys())[:14])
for e in ents:
    t = title(e)
    if not any(w in t for w in want):
        continue
    print('==', t)
    for w in e.get('triggerWords') or e.get('keys') or []:
        if not (w.startswith('/') and w.rstrip('gimsu').endswith('/')):
            if w in reply:
                print('   纯词中：', w)
            continue
        body = w[1:w.rstrip('gimsu').rfind('/')] if not w.endswith('/') else w[1:-1]
        if '迷宫纪(?:100' in body:
            continue
        for br in split_top(body):
            try:
                m = re.search(br, reply)
            except re.error:
                continue
            if m:
                s = reply[max(0, m.start() - 14):m.end() + 14].replace('\n', ' ')
                print('   中：', br, '｜', s)
