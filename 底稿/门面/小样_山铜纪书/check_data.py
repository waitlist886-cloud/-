#!/usr/bin/env python3
# 查 data/bronze.json 和 data/prof/ 有没有漏、有没有把只给模型看的话搬上页。
#   python -I -X utf8 check_data.py
# 报“错”的要改（漏了的栏、给模型的字眼、三维罩杯、月相字）；报“看”的自己看一眼（搬过来的句子在源稿里找不到原样、没有立绘）。
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
COMFY = os.path.join(ROOT, '底稿', '状态栏', 'comfy')
NUM = '一二三四五六'
PAGES = ['犁的年月', '长夜的年月', '白鸦的年月', '黎明的年月', '七城的年月', '麦的年月']
META = re.compile(r'★|(?<![A-Za-z])AI(?![A-Za-z])|NPC|玩家|只给|裁定|条目|这一稿|叙述里|叙述不|模型|底卡|锁里|不提前说|潮汐格|凭证|照[^。，“”]{0,24}那[一两三]条(?=[。，）]|$)|见人物|（#|#\d')
META_Q = re.compile(r'这一页|这一条|这一卷')        # 台词里常有，只查引号外头的
BODY = re.compile(r'三维|三围|罩杯|[A-HＡ-Ｈ]杯|cup|\d+/\d+/\d+')
MOON = re.compile(r'月亮|月光|新月|满月|残月|月牙|弦月')
PUNCT = re.compile(r'——|—|；|…|！')


def walk(v, path=''):
    if isinstance(v, str):
        yield path, v
    elif isinstance(v, list):
        for i, x in enumerate(v):
            yield from walk(x, '%s[%d]' % (path, i))
    elif isinstance(v, dict):
        for k, x in v.items():
            if k in ('id', 'key', 'pset', 'side', 'kind', 'art', 'img', 'imgs', 'code'):
                continue
            yield from walk(x, path + '.' + k)


def plain(t):
    return re.sub(r'（[^（）]*）|\s', '', t)


def main():
    d = json.load(open(os.path.join(HERE, 'data', 'bronze.json'), encoding='utf-8'))
    errs, looks = [], []
    src = {}
    for i, p in enumerate(PAGES):
        src[i] = plain(open(os.path.join(ROOT, '山铜纪', '山铜纪时段_%s_%s.md' % (NUM[i], p)), encoding='utf-8').read())
    first = plain(open(os.path.join(ROOT, '山铜纪', '山铜纪_碑_第一版.md'), encoding='utf-8').read())
    tsv = plain(open(os.path.join(ROOT, '底稿', '地图', '地点谱', '山铜纪.tsv'), encoding='utf-8').read())
    boss_md = plain(open(os.path.join(ROOT, '底稿', '立绘', '史诗战名号', '山铜纪.md'), encoding='utf-8').read())
    allsrc = ''.join(src.values()) + first + tsv + boss_md
    profs = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'data', 'prof', 'p?.json'))):
        profs[os.path.basename(f)[:-5]] = json.load(open(f, encoding='utf-8'))
    # 一、字眼
    for name, obj in [('bronze.json', d)] + [('prof/%s.json' % k, v) for k, v in profs.items()]:
        for path, s in walk(obj):
            if path.endswith('.years'):
                continue
            unq = re.sub(r'“[^“”]*”', '', s)
            for rx, what, bad, txt in ((META, '给模型的字眼', True, s), (META_Q, '给模型的字眼', True, unq), (BODY, '三维罩杯', True, s), (MOON, '月相字', True, s), (PUNCT, '禁用的标点', False, s)):
                m = rx.search(txt)
                s = txt
                if m:
                    (errs if bad else looks).append('%s %s：%s「%s」' % (name, path, what, s[max(0, m.start() - 12):m.end() + 12]))
    # 二、每一页的栏
    nst = 0
    for e in d['eras']:
        eid, pi = e['id'], e['no'] - 1
        for k in ('title', 'years', 'chap', 'chapName', 'chapDesc'):
            if not e.get(k):
                errs.append('%s 缺 %s' % (eid, k))
        if not e['steles']:
            errs.append('%s 没有碑' % eid)
        for s in e['steles']:
            nst += 1
            for k in ('name', 'year', 'side', 'kind', 'where', 'material'):
                if s.get(k) in (None, ''):
                    errs.append('%s 碑 %s 缺 %s' % (eid, s.get('name'), k))
            if not s.get('fl'):
                errs.append('%s 碑 %s 正面没有字' % (eid, s['name']))
            if not s.get('bl'):
                errs.append('%s 碑 %s 背面没有字' % (eid, s['name']))
            if not (e['y0'] <= s['year'] <= e['y1'] + 10):
                looks.append('%s 碑 %s 立在 %s 年，出了这一页的年份' % (eid, s['name'], s['year']))
            for x in s.get('fl', []) + s.get('bl', []):
                if plain(x).rstrip('。') not in src[pi] and plain(x).rstrip('。') not in first:
                    errs.append('%s 碑 %s 刻的这一句源稿里找不到原样：%s' % (eid, s['name'], x))
            if not s.get('art') and s['name'] != '灰雨城之乱':
                errs.append('%s 碑 %s 没有对上图键' % (eid, s['name']))
        for l in e['lines']:
            for k in ('task', 'chap', 'chapName', 'open', 'acts', 'ending', 'year'):
                if not l.get(k):
                    errs.append('%s 主线 %s 缺 %s' % (eid, l['name'], k))
            for x in [l.get('open', '')] + l.get('hooks', []):
                for sen in re.split(r'(?<=[。？])', x):
                    if len(plain(sen)) >= 8 and plain(sen).rstrip('。') not in src[pi]:
                        looks.append('%s 主线 %s 有一句在源稿里找不到原样：%s' % (eid, l['name'], sen[:40]))
        ps = profs.get(eid, {})
        for kind in ('cast', 'meet', 'legends', 'gods'):
            for c in e.get(kind, []):
                if c.get('p') and c['name'] not in ps:
                    errs.append('%s %s 标了有档案，prof 里没有：%s' % (eid, kind, c['name']))
                if kind in ('cast', 'legends') and not c.get('key'):
                    looks.append('%s %s 没有立绘：%s' % (eid, kind, c['name']))
        for c in e['cast']:
            if c.get('age') is None:
                looks.append('%s 旅伴 %s 算不出岁数' % (eid, c['name']))
        for b in e.get('bosses', []):
            for k in b.get('imgs', []):
                if not os.path.exists(os.path.join(COMFY, 'out', '史诗战', 'bronze', k + '.png')):
                    errs.append('%s 灾祸 %s 的图 %s 没有' % (eid, b['name'], k))
            if not b.get('imgs'):
                looks.append('%s 灾祸 %s 一张图也没有' % (eid, b['name']))
        # 档案里搬过来的句子
        for n, p in ps.items():
            for path, s in walk(p):
                if path.startswith('.stars') or path in ('.kind', '.tag', '.race', '.age', '.rose', '.height', '.rank', '.job'):
                    continue
                for sen in re.split(r'(?<=[。？])', s):
                    q = plain(sen).rstrip('。')
                    if len(q) >= 10 and q not in allsrc:
                        looks.append('%s %s %s 有一句在源稿里找不到原样：%s' % (eid, n, path, sen[:36]))
    end = d.get('end', {})
    if len(end.get('base', [])) != 4:
        errs.append('无字碑碑基不是四处半行：%s' % end.get('base'))
    if not end.get('art'):
        errs.append('无字碑没有对上图键')
    print('六页，碑 %d 块加无字碑；主线 %d 条；旅伴 %d、相遇 %d、传奇 %d 人次；神与魔神 %d；灾祸 %d；档案 %d 份' % (
        nst, sum(len(e['lines']) for e in d['eras']), sum(len(e['cast']) for e in d['eras']), sum(len(e['meet']) for e in d['eras']),
        sum(len(e['legends']) for e in d['eras']), sum(len(e['gods']) for e in d['eras']), sum(len(e['bosses']) for e in d['eras']), sum(len(v) for v in profs.values())))
    for x in errs:
        print('  错｜' + x)
    for x in looks[:80]:
        print('  看｜' + x)
    if len(looks) > 80:
        print('  看｜……另有 %d 条' % (len(looks) - 80))
    print('错合计', len(errs), '看合计', len(looks))
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
