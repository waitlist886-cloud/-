# -*- coding: utf-8 -*-
"""这一轮牵到立绘的人：把他们在四本书里的位置、立绘键和出图资料（who 等）印出来，判断旧图还对不对。
用法：por_need.py [名字…]   不给名字就印默认的那一批（11-18 改年轻的和升传奇的）。 --full 印 who 全文
先跑 por_cover.py（它把名单写到系统临时目录的 aldran_por_cover.json）。"""
import io, json, os, sys, glob, re, tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = tempfile.gettempdir()
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..')).replace('\\', '/') + '/'
YOUNG = ['比亚克·眠雷', '兹拉塔·门凳', '赞恩·枷匠', '苔丝', '博里', '玛格达', '布伦希', '纳丝塔', '托娃', '托芙', '塔隆·黑燧', '杜尔夫·断崖', '嘉莉·深井', '洛瑟恩', '茵瑞尔']
LEG = ['菲娅', '鲁珀特', '伊妮德', '安瑟姆', '玛格达', '格里姆', '欧丝嘉', '蕾娃', '苏海拉', '托芙', '朵薇', '坎黛丝', '肯特']
args = [a for a in sys.argv[1:] if not a.startswith('--')]
names = args or list(dict.fromkeys(YOUNG + LEG))
COVER = json.load(open(os.path.join(HERE, 'aldran_por_cover.json'), encoding='utf-8'))
CAST = {}
for fp in glob.glob(ROOT + '底稿/状态栏/comfy/cast/**/*.json', recursive=True):
    try:
        d = json.load(open(fp, encoding='utf-8'))
    except Exception:
        continue
    if not isinstance(d, list):
        continue
    for x in d:
        if isinstance(x, dict) and x.get('en'):
            x['_file'] = os.path.relpath(fp, ROOT + '底稿/状态栏/comfy/cast').replace('\\', '/')
            CAST.setdefault(x['en'], []).append(x)
BYNAME = {}
for k, xs in CAST.items():
    for x in xs:
        BYNAME.setdefault(x.get('name', ''), []).append(x)
full = '--full' in sys.argv
for n in names:
    print('====', n)
    keys = set()
    for ji, P in COVER.items():
        for pn, r in P.items():
            if pn == n or pn.split('·')[0] == n or n.split('·')[0] == pn.split('·')[0]:
                roles = {}
                for era, lab in r['roles']:
                    roles.setdefault(lab, []).append(era)
                print('  书', ji, pn, {k: (v if len(v) < 8 else v[:3] + ['…'] + v[-1:]) for k, v in roles.items()}, 'key', r['key'], r['pset'], '有图' if r['have'] else '没图')
                if r['key']:
                    keys.add(r['key'])
    seen = set()
    cand = [x for k in keys for x in CAST.get(k, [])]
    for nm, xs in BYNAME.items():
        if nm and (nm == n or nm.split('·')[0] == n.split('·')[0]):
            cand += xs
    for x in cand:
        if id(x) in seen:
            continue
        seen.add(id(x))
        extra = {k: x[k] for k in ('same_as', 'identity', 'tier', 'teen', 'ya', 'minor', 'small', 'young', 'refs') if k in x}
        who = x.get('who', '')
        print('  资料', x['_file'], x['en'], x.get('name'), extra)
        print('     who:', who if full else who[:420])
