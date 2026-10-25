"""底卡洗稿核对（10-25，照 底卡洗稿与命名重审_方向稿_第三版.md 第一节第5条）。

用法：python3 -I -X utf8 tools/wash_check.py 底卡洗稿/批次_XX.md [...] [--card 打好的卡.json] [--dump 正文.md]
  --dump 把洗过的正文一条接一条写进一个文件，拿去跑 check_people_v7、ngram。

洗稿文件的样子，一条一节：

  ## #885 凡世至强：光辉顶点 · 莱恩哈特·奥兰（Reinhardt Orlane）
  - 底本哈希：0123456789ab
  - 添触发：晨曦骑士、971（可以没有）
  - 放行：圣座巅峰、东境军权最高支柱（有意删掉的字串，可以没有，用顿号隔开）

  ````
  洗过的整条正文
  ````

底本是打完补丁的那一版底卡（--card 指一张打好的卡，前一千三百九十七条就是底卡，照 #号排；不给就用 out/进卡_v9 的那一张）。
底本哈希是底本正文 utf-8 的 sha1 前十二位，对不上说明前面的补丁改了这一条，要重洗。

查的：
  底本里的数字、LVL、#号、「」里的条目名、【】里的名字、★Feat 名、好感的分数，洗过的里面少了哪个。
  条目名、【】里的名字、Feat 名只要字面还在就算（「」和【】可以拿掉），六个设计文档栏目名换掉不报。
  状态栏那一行一个字符都不能变（去掉加粗以后比）。
  ## 标题行不能变。
  数洗前洗后的破折号、分号、省略号、感叹号、加粗、八股词、禁词。
少了的东西在「放行」里写明了就不报。
"""
import re, sys, os, json, hashlib, collections, glob

DEFAULT_CARD = 'out/进卡_v9/奥尔德兰_日里版_三纪全卷_测试v9.json'
LABELS = {'后台能力收录｜AI一致性锚点', '可牵引线索', '声口补锚', '主线接口', '离场自转', '首个高影响场景', '原创台词样例'}
BAGU = ['核心', '机制', '叙事', '体系', '支柱', '锚点', '底层', '母题', '可牵引线索', '后台能力收录', 'AI一致性锚点',
        '声口补锚', '主线接口', '离场自转', '首个高影响场景', '巅峰', '压制线']
BANNED = ['学宫', '客栈', '朝廷', '门客', '时辰', '掌柜', '百官', '丫头', '宗门', '长老', '功法', '镖局', '一丝', '一抹',
          '不禁', '威压', '修为', '登记', '军令', '条例', '晋升', '量子', '熵', '坐标', '频率', '能量', '系统', '流程', '编制']


def load_lorebook(path):
    card = json.load(open(path, encoding='utf-8'))

    def find(c):
        if isinstance(c, dict):
            for v in c.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and 'content' in v[0]:
                    return v
                r = find(v)
                if r:
                    return r
    return find(card)


def sha12(text):
    return hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]


def parse_wash(path):
    text = open(path, encoding='utf-8').read()
    out = []
    for m in re.finditer(r'^## #(\d+) (.*)$', text, re.M):
        start = m.end()
        nxt = re.search(r'^## #\d+ ', text[start:], re.M)
        block = text[start:start + nxt.start()] if nxt else text[start:]
        hm = re.search(r'^- 底本哈希：\s*([0-9a-f]{12})', block, re.M)
        allow = re.search(r'^- 放行：(.*)$', block, re.M)
        body = re.search(r'^````[^\n]*\n(.*?)\n````\s*$', block, re.M | re.S)
        out.append({
            'idx': int(m.group(1)), 'title': m.group(2).strip(),
            'hash': hm.group(1) if hm else None,
            'allow': [a.strip() for a in allow.group(1).split('、')] if allow else [],
            'body': body.group(1) if body else None,
        })
    return out


def facts(text):
    t = text.replace('**', '')
    f = collections.Counter()
    for x in re.findall(r'\d+(?:\.\d+)?%?', t):
        f['数 ' + x] += 1
    for x in re.findall(r'#\d+', t):
        f['号 ' + x] += 1
    for x in re.findall(r'「([^」]{1,40})」', t):
        f['条目 ' + x] += 1
    for x in re.findall(r'【([^】]{1,30})】', t):
        f['名 ' + x] += 1
    for x in re.findall(r'★\s*([^\s(（·]{1,12})', t):
        f['Feat ' + x] += 1
    for x in re.findall(r'[+＋−-]\d+(?:～[+＋−-]?\d+)?', t):
        f['分 ' + x] += 1
    return f


def status_lines(text):
    return [l.replace('**', '').strip() for l in text.split('\n') if '状态栏' in l and 'Feat' in l]


def counts(text):
    c = collections.Counter()
    c['破折号'] = text.count('——') + text.count('—') - 2 * text.count('——')
    c['分号'] = text.count('；')
    c['省略号'] = text.count('…') + text.count('...')
    c['感叹号'] = text.count('！')
    c['加粗'] = text.count('**') // 2
    c['八股词'] = sum(text.count(w) for w in BAGU)
    c['禁词'] = sum(text.count(w) for w in BANNED)
    return c


def main(argv):
    card = DEFAULT_CARD
    files = []
    dump = None
    bodies = []
    i = 0
    while i < len(argv):
        if argv[i] == '--card':
            card = argv[i + 1]; i += 2
        elif argv[i] == '--dump':
            dump = argv[i + 1]; i += 2
        else:
            files.append(argv[i]); i += 1
    lb = load_lorebook(card)
    bad = 0
    tot_before, tot_after = collections.Counter(), collections.Counter()
    for f in files:
        for e in parse_wash(f):
            probs = []
            if e['idx'] >= 1397:
                probs.append('#号超出底卡')
                print(f'== #{e["idx"]} {e["title"][:30]} | ' + '；'.join(probs)); bad += 1
                continue
            src = lb[e['idx']]['content']
            if e['body'] is None:
                probs.append('没找到四个反引号围起来的正文')
            else:
                bodies.append(e['body'].strip('\n'))
                if e['hash'] != sha12(src):
                    probs.append(f'底本哈希对不上（写的 {e["hash"]}，底本 {sha12(src)}）')
                h_src = src.split('\n')[0].strip()
                h_new = e['body'].split('\n')[0].strip()
                if h_src.replace('**', '') != h_new.replace('**', ''):
                    probs.append('标题行变了')
                if status_lines(src) != status_lines(e['body']):
                    probs.append('状态栏那一行变了')
                fs, fn = facts(src), facts(e['body'])
                plain = e['body'].replace('**', '')
                missing = []
                for k, v in fs.items():
                    if fn.get(k, 0) < 1:
                        kind, val = k.split(' ', 1)
                        if kind in ('条目', '名', 'Feat') and val in plain:
                            continue
                        if val in LABELS:
                            continue
                        if any(val in a or a in val for a in e['allow'] if a):
                            continue
                        missing.append(k)
                if missing:
                    probs.append('少了：' + '、'.join(missing[:30]) + ('……' if len(missing) > 30 else ''))
                cb, ca = counts(src), counts(e['body'])
                tot_before.update(cb); tot_after.update(ca)
                left = {k: v for k, v in ca.items() if v and k in ('破折号', '分号', '省略号', '感叹号')}
                if left:
                    probs.append('还剩 ' + '，'.join(f'{k}{v}' for k, v in left.items()))
            mark = '问题 ' + str(len(probs)) if probs else '过'
            print(f'== #{e["idx"]} {e["title"][:30]} | {mark}')
            for p in probs:
                print('  - ' + p)
            bad += bool(probs)
    if tot_before:
        print('洗前：' + '，'.join(f'{k} {v}' for k, v in tot_before.items()))
        print('洗后：' + '，'.join(f'{k} {v}' for k, v in tot_after.items()))
    if dump:
        open(dump, 'w', encoding='utf-8').write('\n\n'.join(bodies) + '\n')
        print(f'正文 {len(bodies)} 条写到 {dump}')
    print(f'合计 有问题的条 {bad}')


if __name__ == '__main__':
    main(sys.argv[1:])
