# usage: python3 -I align.py file.md [file2.md ...]
# For every stanza (blank-line separated, headings and blockquotes skipped) print line lengths;
# flag stanzas whose lines are not all the same length. Also flags banned punctuation.
import sys, re
BAN = ['——', '—', '；', '…', '！', '：', '「', '」', '...']
tot_bad = 0
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    st = [b.strip('\n') for b in re.split(r'\n\s*\n', s) if b.strip()]
    for k, b in enumerate(st):
        ls = b.split('\n')
        if ls[0].startswith('#') or ls[0].startswith('>'):
            continue
        lens = [len(l) for l in ls]
        flag = '' if len(set(lens)) == 1 else '  <-- UNEVEN'
        bp = [x for x in BAN if x in b]
        q = b.count('“') - b.count('”')
        if bp: flag += '  BANNED ' + ' '.join(bp)
        if q: flag += '  QUOTES %+d' % q
        if flag:
            tot_bad += 1
            print('%s #%d %s%s' % (p.split('/')[-1], k, lens, flag))
            for l in ls:
                print('    %2d %s' % (len(l), l))
print('stanzas needing work:', tot_bad)
