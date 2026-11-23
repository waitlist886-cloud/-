#!/usr/bin/env python3
# 11-23 风月探针（用户：“1先出探针我去测”）：出风月版以前要探明的三件，风月吃不吃得下四纪全卷、显示正则能放多少条、样式和门面走不走得了图床。
# 三张卡，都以线上那张风月底卡为底（out/发布卡_风月_迷宫纪大框/…_用户底.json 没有就用同目录那一张），只测平台，不能拿来玩：
#   甲  小卡（世界书照旧 1427 条）：显示正则填到 800 条，样式填到 180 万字，样式顶上一条 @import，回复末尾插一条 link，
#       简介页换成一张自己报结果的探针页（脚本、取图床上的文件、外链样式、外链脚本、图、本地存储）。回复末尾有一个黄框报四样。
#   乙  世界书换成四纪大框的 8440 条全量（触发照风月的写法粗转：一条 RE2 正则，没有黑名单、没有前后顾，纪元门控不在，只测装不装得下、一轮回不回得来）。
#   丙  同乙，只装前一半。乙不行的时候拿它二分。
# 用法（仓库根上）：python -I -X utf8 底稿/状态栏/风月探针_11-23/make_fy_probe.py [--push]   --push 先把 ext/ 推到图床 probe_fy 分支
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
EXT = os.path.join(HERE, 'ext')
MAN = os.path.join(HERE, 'ext_manifest.json')
OUT = os.path.join(ROOT, 'out', '风月探针_11-23')
REPO, BRANCH = 'waitlist886-cloud/aldran-img', 'probe_fy'
FY = os.path.join(ROOT, 'out', '发布卡_风月_迷宫纪大框', '奥尔德兰_风月底卡_迷宫纪大框.json')
RILI = os.path.join(ROOT, 'out', '发布卡_四纪大框', '奥尔德兰_四纪大框.json')
N_RULES, N_CSS = 800, 1800000


def git(cwd, *a):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError('git %s 失败：%s' % (' '.join(a[:2]), (r.stderr or r.stdout).strip()[-400:]))
    return r.stdout.strip()


def push():
    files = sorted(f for f in os.listdir(EXT) if os.path.isfile(os.path.join(EXT, f)))
    tmp = tempfile.mkdtemp(prefix='ghfy_')
    try:
        git(tmp, 'init', '-q')
        git(tmp, 'checkout', '-q', '-b', BRANCH)
        for f in files:
            shutil.copy2(os.path.join(EXT, f), os.path.join(tmp, f))
        with open(os.path.join(tmp, '.gitattributes'), 'w', newline='\n') as fh:
            fh.write('* -text\n')
        git(tmp, 'add', '-A')
        git(tmp, '-c', 'user.name=Claude', '-c', 'user.email=noreply@anthropic.com', 'commit', '-q', '-m', 'probe_fy：风月探针的测试桩 %d 个' % len(files))
        commit = git(tmp, 'rev-parse', 'HEAD')
        git(tmp, 'push', '-q', '--force', 'https://github.com/%s.git' % REPO, 'HEAD:refs/heads/%s' % BRANCH)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    man = {'repo': REPO, 'branch': BRANCH, 'commit': commit, 'base': 'https://cdn.jsdelivr.net/gh/%s@%s/' % (REPO, commit), 'files': files}
    json.dump(man, open(MAN, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('推好了', commit)


if '--push' in sys.argv:
    push()
BASE = json.load(open(MAN, encoding='utf-8'))['base']
fy = json.load(open(FY, encoding='utf-8'))
os.makedirs(OUT, exist_ok=True)


def save(card, name):
    p = os.path.join(OUT, name)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(card, f, ensure_ascii=False, separators=(',', ':'))
    print(name, '%.1f MB' % (os.path.getsize(p) / 1048576), '世界书', len(card['world_bk']), '条，正则', len(card['regex_rp']), '条，样式', len(card['built_in_css']), '字')


# ---------------- 甲 ----------------
a = copy.deepcopy(fy)
a['name'] = '【探针甲】风月：正则条数、样式大小、外链'
a['abstract'] = '平台探针，不能玩。开一段对话随便发一句，看回复末尾的黄框；再看简介页。说明见 怎么测.md。'
box = ('<div class="fyp" style="margin:12px 0;padding:10px 12px;border:2px dashed #c80;background:#fff8e6;color:#222;font-size:14px;line-height:1.9">'
       '<b>风月探针·甲</b><br>'
       '<span class="fyp-r">① 第 %d 条显示正则：<b>✗ⓧR</b></span><br>'
       '<span class="fyp-c">② 内嵌样式 %d 万字的最后一条：<b class="no">✗ 没到</b></span><br>'
       '<span class="fyp-b">③ 样式里的 @import 外链：<b class="no">✗ 没载</b></span><br>'
       '<span class="fyp-a">④ 回复里插 link 外链：<b class="no">✗ 没载</b></span>'
       '</div><link rel="stylesheet" href="%sfy_probe_link.css">') % (N_RULES, N_CSS // 10000, BASE)
rules = a['regex_rp']
n0 = len(rules)
rules.append({'title': '探针·黄框', 'match_regex': r'^([\s\S]+)$', 'replace_text': '$1\n\n' + box, 'scope': 1, 'is_enable': True, 'is_only_render': True})
while len(rules) < N_RULES - 1:
    rules.append({'title': '探针·填充%03d' % len(rules), 'match_regex': 'ⓧ探针填充%03d' % len(rules), 'replace_text': '', 'scope': 1, 'is_enable': True, 'is_only_render': True})
rules.append({'title': '探针·末条', 'match_regex': '✗ⓧR', 'replace_text': '✓ 通', 'scope': 1, 'is_enable': True, 'is_only_render': True})
assert len(rules) == N_RULES
css = '@import url("%sfy_probe_import.css");\n' % BASE + a['built_in_css'].rstrip() + '\n'
pad = []
k, size = 0, len(css)
while size < N_CSS - 200:
    s = '.fyp-pad-%06d{color:#%06x;margin:0 0 0 %dpx}\n' % (k, k % 0xffffff, k % 7)
    pad.append(s)
    size += len(s)
    k += 1
css += ''.join(pad) + '.fyp-c .no{display:none}.fyp-c::after{content:"✓ 通";color:#2a7a4a;font-weight:700}\n'
a['built_in_css'] = css
a['descr'] = open(os.path.join(HERE, 'descr_probe.html'), encoding='utf-8').read().replace('__BASE__', BASE)
save(a, '探针甲_正则样式外链.json')
print('  甲：原正则', n0, '条填到', N_RULES, '；原样式', len(fy['built_in_css']), '字填到', len(css))

# ---------------- 乙、丙 ----------------
RG = {'system': 1, 'user': 2, 'assistant': 4}
RV = {'system': 1, 'headPrompt': 2, 'rearPrompt': 4}
LOOK = re.compile(r'\(\?(?:=|!|<=|<!)')
META = re.compile(r'([\\.^$*+?()\[\]{}|])')


def word(w):
    """日里的一个触发词 → RE2 能认的一段；带前后顾的认不了，返回 None"""
    if len(w) > 2 and w.startswith('/') and w.rfind('/') > 0:
        k = w.rfind('/')
        body, flags = w[1:k], w[k + 1:]
        if LOOK.search(body) or re.search(r'\\[1-9]', body):
            return None
        return ('(?i)' if 'i' in flags else '') + '(?:' + body + ')'
    return META.sub(r'\\\1', w)


def entry(e):
    ws = [word(w) for w in e['triggerWords']]
    dropped = sum(1 for w in ws if w is None)
    ws = [w for w in ws if w]
    if not ws:
        key = 'ⓧ探针无钥'
    elif e.get('triggerWordsType') == 'AND' and len(ws) >= 2:
        x, y = ws[0], '|'.join(ws[1:])
        key = '%s[\\s\\S]*(?:%s)|(?:%s)[\\s\\S]*%s' % (x, y, y, x)
    else:
        key = '|'.join(ws)
    val = e.get('content') or (e.get('contents') or [{'content': ''}])[0]['content']
    return {'group': e.get('folder') or '', 'match_type': 3, 'key': key, 'key_region': sum(RG.get(x, 0) for x in e['triggerRange']) or 2,
            'value_type': 0, 'value': val, 'value_configs': [], 'value_region': sum(RV.get(x, 0) for x in e['impactRange']) or 1,
            'sort': e['priority'], 'depth': max(1, e['scanDepth']), 'probability': e['probability'], 'enable': e['enabled']}, dropped


rili = json.load(open(RILI, encoding='utf-8'))
conv = [entry(e) for e in rili['prompt']['lorebook']]
wb = [x for x, _ in conv]
for x in wb:
    re.compile(x['key'].replace('(?i)', ''))   # 粗核一遍编得过（Python 的正则比 RE2 宽，RE2 不认的前后顾和反向引用上面拿掉了）
print('四纪世界书', len(wb), '条；带前后顾拿掉的触发词', sum(d for _, d in conv), '个；没钥匙的', sum(1 for x in wb if x['key'] == 'ⓧ探针无钥'),
      '条；最长的钥匙', max(len(x['key']) for x in wb), '字，过一千字的', sum(1 for x in wb if len(x['key']) > 1000), '条；最长的正文', max(len(x['value']) for x in wb), '字')
for name, title, n in (('探针乙_世界书全量.json', '【探针乙】风月：四纪世界书全量 %d 条' % len(wb), len(wb)),
                       ('探针丙_世界书半量.json', '【探针丙】风月：四纪世界书半量 %d 条' % (len(wb) // 2), len(wb) // 2)):
    c = copy.deepcopy(fy)
    c['name'] = title
    c['abstract'] = '平台探针，不能玩（纪元门控不在，条目会乱醒）。只看导不导得进、存不存得住、开一段对话发一句回不回得来。说明见 怎么测.md。'
    c['world_bk'] = wb[:n]
    save(c, name)
# ---------------- 第二轮（用户测下来：乙导入时 normalize 那个请求一直挂着）：把“条数”和“字节”拆开各测一样 ----------------
#   己  8440 条全在，正文截到 60 字（钥匙照旧）：只测条数和钥匙，文件小
#   壬  同己，只装前一半
#   丁  四分之一量、正文照旧（12MB 上下）：测字节
bad = [x['key'][:60] for x in wb if re.search(r'\\u[0-9a-fA-F]{4}|\[\^\]|\(\?<[A-Za-z]|\\k<|\\c[A-Z]', x['key'])]
print('钥匙里 RE2 不认的写法（\\u、[^]、命名组）', len(bad), bad[:3])


def short(x):
    y = dict(x)
    y['value'] = x['value'][:60]
    return y


for name, title, lst in (('探针己_全量条数_正文截短.json', '【探针己】风月：8440 条、正文截短', [short(x) for x in wb]),
                         ('探针壬_半量条数_正文截短.json', '【探针壬】风月：4220 条、正文截短', [short(x) for x in wb[:len(wb) // 2]]),
                         ('探针丁_四分之一量.json', '【探针丁】风月：四纪世界书四分之一 %d 条' % (len(wb) // 4), wb[:len(wb) // 4])):
    c = copy.deepcopy(fy)
    c['name'] = title
    c['abstract'] = '平台探针，不能玩。只看导不导得进、存不存得住。说明见 怎么测_第二轮.md。'
    c['world_bk'] = lst
    save(c, name)
# ---------------- 第三轮（己 8.8MB 行、丁 12.6MB 超时）：线在两者之间，再切两刀 ----------------
base_bytes = len(json.dumps({k: v for k, v in fy.items() if k != 'world_bk'}, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
for name, title, target in (('探针戊_10MB.json', '【探针戊】风月：整卡 10MB', 10.0), ('探针辛_11MB.json', '【探针辛】风月：整卡 11.3MB', 11.3)):
    lst, size = [], base_bytes
    for x in wb:
        n = len(json.dumps(x, ensure_ascii=False, separators=(',', ':')).encode('utf-8')) + 1
        if size + n > target * 1048576:
            break
        lst.append(x)
        size += n
    c = copy.deepcopy(fy)
    c['name'] = title
    c['abstract'] = '平台探针，不能玩。只看导不导得进、存不存得住。'
    c['world_bk'] = lst
    save(c, name)
# ---------------- 第四轮（用户：“试一下能不能跟rili一样拆分，先入底卡，然后世界书一份份的导入专用的模版”）----------------
# 风月的世界书有单独的模板导入（{"world_book":[…]}，一份里可以有多条）。先导一张小底卡，再把四纪 8440 条切成几份一份一份导、导一份存一回，看存到第几份不行。
c = copy.deepcopy(fy)
c['name'] = '【探针底】风月：世界书分批导入用的小底卡'
c['abstract'] = '平台探针，不能玩。先导这一张，再照 怎么测_第四轮.md 一份一份导世界书。'
c['world_bk'] = fy['world_bk'][:20]
save(c, '探针底_小底卡.json')
PART = 4.6 * 1048576
parts, cur, size = [], [], 0
for x in wb:
    n = len(json.dumps(x, ensure_ascii=False, separators=(',', ':')).encode('utf-8')) + 1
    if cur and size + n > PART:
        parts.append(cur)
        cur, size = [], 0
    cur.append(x)
    size += n
if cur:
    parts.append(cur)
for k, lst in enumerate(parts, 1):
    p = os.path.join(OUT, '世界书分批_第%d份.json' % k)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'world_book': lst}, f, ensure_ascii=False, separators=(',', ':'))
    print('世界书分批 第%d份' % k, len(lst), '条', '%.1f MB' % (os.path.getsize(p) / 1048576), '导完累计', sum(len(q) for q in parts[:k]) + 20, '条')
for n in ('怎么测.md', '怎么测_第二轮.md', '怎么测_第四轮.md'):
    shutil.copyfile(os.path.join(HERE, n), os.path.join(OUT, n))
