# 专名粗筛：命星、名器、任务名（主线、支线、委托、羁绊的题）、地名。按几条“不够西幻”的迹象标出来，给人看着挑。
import collections
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
card = json.load(open('E:/aldran_art/out/发布卡_四纪大框/奥尔德兰_四纪大框.json', encoding='utf-8'))
lb = card['prompt']['lorebook']
ERAS = ['月银纪', '纷争纪', '山铜纪', '迷宫纪']


def title(e):
    c = (e.get('content') or '').strip()
    return c.split('\n', 1)[0].strip().lstrip('#').strip()


def folder(e):
    return e.get('folder') or ''


# 迹象：口语碎片和白描（动宾两三个字、带“的那这了不”的半句话）、家常器物、乡土的通名、数量词
HOME = '碗锅灶秤账篮筐担针线绳钉凳桌闩炉膛饼粥汤勺瓢盆缸桶筛箩袋麻布鞋袜帽袄被褥炕砖瓦'
RURAL = re.compile(r'(庄|屯|沟|集|坡|岗|铺|店|寨|洼|坳|坝|圩|甸|岔口|渡口|驿镇)$')
VERB2 = re.compile(r'^[砸拽拍背留记压接撞断分扛挑抬递端捆拴掰摁按抹搓揉敲凿钉缝补烧煮熬蒸喂牵赶拉推扶搀数认看听走问][^之的]{1,2}$')
HALF = re.compile(r'的那|那一|这一|头一|了$|不[^朽灭落折移眠冬]|没有|一个|两个|[一二三四五六七八九十百千]\w?[条根只个张块座把件枚袋车桶碗]')


def flags(n):
    f = []
    if VERB2.search(n):
        f.append('动宾白描')
    if HALF.search(n):
        f.append('半句话')
    if any(ch in n for ch in HOME):
        f.append('家常器物')
    if RURAL.search(n):
        f.append('乡土通名')
    return f


def show(label, names, limit=60):
    names = list(dict.fromkeys(names))
    fl = [(n, flags(n)) for n in names]
    hit = [(n, f) for n, f in fl if f]
    by = collections.Counter(x for _, f in hit for x in f)
    print('\n== %s：%d 个，标出来 %d 个（%s）' % (label, len(names), len(hit), '，'.join('%s %d' % kv for kv in by.most_common())))
    print('   ' + '、'.join(n for n, _ in hit[:limit]))


# 命星
for era in ERAS:
    st = [title(e) for e in lb if re.match(r'49·' + era, folder(e))]
    st = [re.sub(r'\s*[（(].*$', '', s).strip() for s in st]
    st = [re.sub(r'^.*?[｜|]', '', s) if '｜' in s[:8] else s for s in st]
    show('命星·' + era, st, 70)
base_star = [re.sub(r'\s*[（(].*$', '', title(e)).strip() for e in lb if re.match(r'07·', folder(e))]
show('命星·底卡', base_star, 40)

# 名器、装备、遗物
gear = [title(e) for e in lb if re.match(r'59·', folder(e))]
gear = [re.sub(r'^.*?[｜|]', '', g) for g in gear]
show('四纪的装备与名器', gear, 60)
relic = [title(e) for e in lb if re.match(r'10·', folder(e)) or '遗物' in title(e)[:8]]
show('底卡的装备、遗物', [re.sub(r'^.*?[｜|·]', '', g) for g in relic], 50)

# 任务名
for era in ERAS:
    ml = [title(e) for e in lb if re.match(r'41·' + era, folder(e)) and '主线' in title(e)[:10] and '·一幕' not in title(e) and '·二幕' not in title(e) and '·三幕' not in title(e) and '·收束' not in title(e) and '·幕间' not in title(e)]
    ml = [re.sub(r'（.*?）$', '', re.sub(r'^.*?[｜|]', '', m)) for m in ml]
    ml = [m.split('·')[-1] for m in ml]
    show('主线名·' + era, ml, 60)
    sd = [re.sub(r'^.*?[｜|]', '', title(e)) for e in lb if re.match(r'56·' + era, folder(e))]
    show('支线名·' + era, [s.split('·')[-1] for s in sd], 50)
quest = []
for e in lb:
    m = re.search(r'^题：(.+)$', e.get('content') or '', re.M)
    if m and re.match(r'41·', folder(e)):
        quest.append(m.group(1).split('｜')[-1].strip('【】'))
show('合篇的题和任务名', quest, 40)
bond = []
for e in lb:
    if re.match(r'57·', folder(e)):
        t = re.sub(r'^.*?[｜|]', '', title(e))
        bond.extend(t.split('·'))
show('羁绊的章名和题', bond, 70)
wt = [re.sub(r'^.*?[｜|]', '', title(e)) for e in lb if re.match(r'50·迷宫纪', folder(e))]
show('委托名', wt, 30)

# 地名
for era in ERAS:
    pl = [re.sub(r'^.*?[｜|]', '', title(e)) for e in lb if re.match(r'4[45]·' + era, folder(e))]
    names = []
    for p in pl:
        names.extend(re.split('[与和、·]', p))
    show('地点和城邦·' + era, [n for n in names if 1 < len(n) < 9], 60)
