#!/usr/bin/env python3
# 过条底子（11-24）：把 交稿/<份>.md 换回源稿。
#   python -I -X utf8 底稿/收尾_11-24/过条/tools/splice.py --dry [交稿…]    只报（不给文件就读 交稿/*.md）
#   python -I -X utf8 底稿/收尾_11-24/过条/tools/splice.py --apply [交稿…]  写盘，另写 收稿/过条记录.json，末尾印要重拼的页
# 认 清点.json：每人的文件、条目标题、原来那几行（【行 a】是 清点.json 里「行」的头一行，往下 b、c……）。
# 一人一段：
#   【人】G012
#   【行 b】整行（换掉原来那一行；原行在源稿那一条里一字不差地找，找不到就不换、报出来）
#   【兼修】整行（插在这个人最后一行能力行后头；写「无」不插）
#   【走势补】一句（接在技艺走势那一行末尾；写「无」不接）
#   【改名】旧→新｜缘故（只认生来的星；这一条里【旧】都换成【新】）
#   【没改】一句（只记）
# 核：换上去的行，技艺（Art、技艺）的名字和次序跟原行一样；生来星换了名字的要在【改名】里写；主修那一门带「档·N阶」或「档·未入阶」；
# 跟原行差得太多的报出来手看；同一人几条（清点.json 的「同一人」）生来星名字要一样，阶按条目先后只升不降。
import difflib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import NL, CRLF, ROOT, W, MARK, JIE, KIND, load_json  # noqa: E402
import glob  # noqa: E402

LETTERS = 'abcdefghijklmnopqrstuvwxyz'
NUM = {'未入阶': 0, '一阶': 1, '二阶': 2, '三阶': 3, '四阶': 4, '五阶': 5}


def parse(t):
    t = t.replace(CRLF, NL)
    out = []
    for seg in re.split(r'^={4,}\s*$', t, flags=re.M):
        m = re.search(r'^【人】\s*(G\d{3})', seg, re.M)
        if not m:
            continue
        p = {'id': m.group(1), 'lines': {}, 'jx': '', 'zs': '', 'ren': [], 'kept': []}
        for lm in re.finditer(r'^【行 ?([a-z])】(.*)$', seg, re.M):
            p['lines'][lm.group(1)] = lm.group(2).rstrip()
        mm = re.search(r'^【兼修】(.*)$', seg, re.M)
        p['jx'] = mm.group(1).strip() if mm else ''
        mm = re.search(r'^【走势补】(.*)$', seg, re.M)
        p['zs'] = mm.group(1).strip() if mm else ''
        for rm in re.finditer(r'^【改名】(.+?)→(.+?)｜(.*)$', seg, re.M):
            p['ren'].append((rm.group(1).strip(), rm.group(2).strip(), rm.group(3).strip()))
        p['kept'] = [x.strip() for x in re.findall(r'^【没改】(.*)$', seg, re.M)]
        out.append(p)
    return out


def names(line):
    return [(KIND[k], n) for k, n in MARK.findall(line)]


def jie_list(line):
    return [NUM[x.split('·')[1]] for x in JIE.findall(line)]


def entry_span(t, head):
    m = re.search(r'(?m)^' + re.escape('## ' + head) + r'[ \t]*\n.*?(?=^## (?!裁定锁)|\Z)', t, re.S)
    return (m.start(), m.end()) if m else None


def zs_pat(who, single):
    nm = re.escape(who.split('·')[0])
    return (r'^(?:- )?(?:' + nm + r'｜)?技艺走势[：。].*$') if single else (r'^- ' + nm + r'｜技艺走势[：。].*$')


def main(apply, files):
    recs = load_json('清点.json')
    byid = {r['id']: r for r in recs}
    per_entry = {}
    for r in recs:
        per_entry.setdefault((r['文件'][0] if r['文件'] else '', r['条目']), []).append(r['id'])
    files = files or sorted(glob.glob(os.path.join(W, '交稿', '*.md')))
    texts, warn, log = {}, [], {'people': 0, 'lines': 0, 'jx': 0, 'zs': 0, 'ren': [], 'kept': [], 'missing': []}
    got = {}
    for f in files:
        for p in parse(open(f, encoding='utf-8').read()):
            if p['id'] in got:
                warn.append('%s：交了两回（%s）' % (p['id'], os.path.basename(f)))
            got[p['id']] = p
    # 交稿里缺了谁：照 分份.json，交了哪一份就查哪一份
    fen = load_json('分份.json')
    for name, s in fen.items():
        if any(os.path.basename(f) == name + '.md' for f in files):
            miss = [i for i in s['人'] if i not in got]
            if miss:
                log['missing'] += miss
                warn.append('%s 缺 %d 人：%s' % (name, len(miss), '、'.join(miss)))

    def load(src):
        if src not in texts:
            raw = open(os.path.join(ROOT, src), encoding='utf-8', newline='').read()
            texts[src] = [raw, raw.replace(CRLF, NL), CRLF in raw]
        return texts[src]

    newlines = {}
    for pid, p in got.items():
        r = byid.get(pid)
        if not r:
            warn.append('%s：清点.json 里没有这个编号' % pid)
            continue
        if not r['文件']:
            warn.append('%s %s：清点里没有源稿' % (pid, r['人']))
            continue
        ren = {o: n for o, n, _ in p['ren']}
        single = r['类别'] == '凡世至强' or len(per_entry[(r['文件'][0], r['条目'])]) == 1
        done_any = False
        for src in r['文件']:
            st = load(src)
            sp = entry_span(st[1], r['条目'])
            if not sp:
                warn.append('%s %s：%s 里找不到条目「%s」' % (pid, r['人'], src, r['条目'][:30]))
                continue
            e = st[1][sp[0]:sp[1]]
            last_anchor = None
            for i, orig in enumerate(r['行']):
                ch = LETTERS[i]
                new = p['lines'].get(ch)
                if not re.search(r'(?m)^' + re.escape(orig) + r'$', e):
                    warn.append('%s %s 行%s：源稿里找不到原行（scan 以后改过？重跑 scan、material）' % (pid, r['人'], ch))
                    continue
                if new is None or new == orig:
                    last_anchor = orig
                    continue
                o, n = names(orig), names(new)
                oa = [x for k, x in o if k == 'A']
                na = [x for k, x in n if k == 'A']
                og = [ren.get(x, x) for k, x in o if k != 'A']
                ng = [x for k, x in n if k != 'A']
                if oa != na:
                    warn.append('%s %s 行%s：技艺的名字或次序变了 %s → %s，没换' % (pid, r['人'], ch, oa, na))
                    last_anchor = orig
                    continue
                if og != ng:
                    warn.append('%s %s 行%s：生来星名字变了又没写【改名】%s → %s，没换' % (pid, r['人'], ch, og, ng))
                    last_anchor = orig
                    continue
                if na and not JIE.search(new) and '兼修' not in new:
                    warn.append('%s %s 行%s：技艺没带阶' % (pid, r['人'], ch))
                ratio = difflib.SequenceMatcher(None, orig, new).ratio()
                if ratio < 0.6:
                    warn.append('%s %s 行%s：跟原行差得多（相似 %.2f），手看' % (pid, r['人'], ch, ratio))
                e = re.sub(r'(?m)^' + re.escape(orig) + r'$', lambda _m: new, e, count=1)
                log['lines'] += 1
                last_anchor = new
                newlines.setdefault(pid, []).append(new)
            if p['jx'] and not p['jx'].startswith('无'):
                jx = p['jx']
                if not jx.startswith('- ') or '兼修' not in jx:
                    warn.append('%s %s：【兼修】要写整行，「- 」起头、带「兼修」两个字，没插｜%s' % (pid, r['人'], jx[:40]))
                elif r['兼修']:
                    warn.append('%s %s：原来就有兼修，没插' % (pid, r['人']))
                elif last_anchor is None:
                    warn.append('%s %s：找不到插兼修的地方' % (pid, r['人']))
                else:
                    e = re.sub(r'(?m)^' + re.escape(last_anchor) + r'$', lambda _m: last_anchor + NL + jx, e, count=1)
                    log['jx'] += 1
                    newlines.setdefault(pid, []).append(jx)
            if p['zs'] and not p['zs'].startswith('无'):
                zm = re.search(zs_pat(r['人'], single), e, re.M)
                if zm:
                    z = zm.group(0).rstrip()
                    e = e[:zm.start()] + z + ('' if z.endswith('。') else '。') + p['zs'] + e[zm.end():]
                    log['zs'] += 1
                else:
                    warn.append('%s %s：没有技艺走势那一行，走势补没接' % (pid, r['人']))
            for o_, n_ in ren.items():
                if '【%s】' % o_ not in e:
                    warn.append('%s %s：【改名】%s 这一条里没有' % (pid, r['人'], o_))
                e = e.replace('【%s】' % o_, '【%s】' % n_)
                log['ren'].append('%s｜%s｜%s→%s' % (pid, r['人'], o_, n_))
            st[1] = st[1][:sp[0]] + e + st[1][sp[1]:]
            done_any = True
        if done_any:
            log['people'] += 1
        log['kept'] += ['%s｜%s｜%s' % (pid, r['人'], k) for k in p['kept']]
    # 同一人几条：生来星名字一样，阶只升不降（按清点里的次序，就是纪和页的先后）
    seen = set()
    for r in recs:
        grp = [r['id']] + r.get('同一人', [])
        key = tuple(sorted(grp))
        if key in seen or len(grp) < 2:
            continue
        seen.add(key)
        rows = [byid[i] for i in sorted(grp)]
        gsets, prev = {}, None
        for x in rows:
            ls = newlines.get(x['id']) or x['行']
            txt = NL.join(l for l in ls if '兼修' not in l)
            gsets[x['id']] = sorted(set(n for k, n in names(txt) if k != 'A'))
            js = jie_list(txt)
            if js and prev is not None and max(js) < prev:
                warn.append('%s %s：阶比前一条（%s）低' % (x['id'], x['人'], prev))
            if js:
                prev = max(js)
        if len(set(tuple(v) for v in gsets.values() if v)) > 1:
            warn.append('同一人 %s：生来星几条不一样 %s' % (rows[0]['人'], gsets))
    print('换了 %d 人：%d 行，兼修 %d，走势补 %d，改名 %d，没改 %d，缺交 %d' % (
        log['people'], log['lines'], log['jx'], log['zs'], len(log['ren']), len(log['kept']), len(log['missing'])))
    for x in warn:
        print('  看：', x)
    touched = [src for src, st in texts.items() if (st[1].replace(NL, CRLF) if st[2] else st[1]) != st[0]]
    print('要动的文件 %d 个' % len(touched))
    for src in touched:
        print('   ', src)
        if '--diff' in sys.argv:
            st = texts[src]
            for dl in difflib.unified_diff(st[0].replace(CRLF, NL).split(NL), st[1].split(NL), lineterm='', n=0):
                print('      ' + dl[:160])
    pages = set()
    for src in touched:
        m = re.match(r'(纷争纪|山铜纪|迷宫纪前传)/parts(\d?)/', src)
        if m:
            pages.add((m.group(1), int(m.group(2) or 1)))
    cmds = []
    for era, n in sorted(pages):
        if era == '纷争纪':
            cmds.append('bash tools/assemble_strife.sh %d' % n)
        elif era == '山铜纪':
            cmds.append('python -I -X utf8 tools/assemble_shantong_p%d.py .' % n)
        else:
            cmds.append('python -I -X utf8 tools/assemble_maze.py . %d' % n)
    if cmds:
        print('换完重拼：')
        for c in cmds:
            print('   ', c)
    if apply:
        for src in touched:
            st = texts[src]
            open(os.path.join(ROOT, src), 'w', encoding='utf-8', newline='').write(st[1].replace(NL, CRLF) if st[2] else st[1])
        os.makedirs(os.path.join(W, '收稿'), exist_ok=True)
        json.dump(log, open(os.path.join(W, '收稿', '过条记录.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('写了 %d 个文件' % len(touched))


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--apply' not in sys.argv and '--dry' not in sys.argv:
        print('要写 --dry 或 --apply')
        sys.exit(1)
    main('--apply' in sys.argv, args)
