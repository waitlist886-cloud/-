#!/usr/bin/env python3
# 立绘资料自查（11-05 铺开各纪）：python cast_lint.py cast/<纪>/<页>.json [更多文件]
# 查：栏齐不齐、体型档对不对、键重不重（同一纪的目录里）、年少的写没写全、第三格换句的格式、垫底和身份参考的图在不在、禁用的词。
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
NEED = ('name', 'en', 'src', 'sex', 'tier', 'who', 'palette', 'casual', 'private', 'battle', 'formal', 'art')
TIERS = ('woman', 'man', 'burly', 'small', 'youth', 'girl', 'boy', 'child')
BAN = re.compile(r'(?i)\bcrescent|\bmoon|kimono|hanfu|qipao|cheongsam|samurai|ninja|katana|chinese|oriental')
BODY = re.compile(r'(?i)\bbust|cleavage|\bhips?\b|curv|sexy|voluptuous|\bthighs?\b|seductive|alluring|\bbreasts?\b')
TAN = re.compile(r'(?i)\btan(?:ned)?\b|sun-?browned|bronzed skin|dark-skinned')


def lint(path):
    errs, warns = [], []
    try:
        data = json.load(open(path, encoding='utf-8'))
    except Exception as e:
        return ['JSON 读不了：%s' % e], []
    if not isinstance(data, list):
        return ['顶层要是数组'], []
    others = {}
    for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(path)), '*.json')):
        if os.path.abspath(f) == os.path.abspath(path):
            continue
        try:
            for c in json.load(open(f, encoding='utf-8')):
                others[c.get('en')] = f
        except Exception:
            pass
    seen = set()
    for i, c in enumerate(data):
        tag = '%d %s %s' % (i, c.get('en', '?'), c.get('name', '?'))
        for k in NEED:
            if not str(c.get(k, '')).strip():
                errs.append(tag + '：缺 ' + k)
        en = c.get('en', '')
        if en in seen or en in others:
            errs.append(tag + '：键重了' + (('，跟 ' + os.path.basename(others[en])) if en in others else ''))
        seen.add(en)
        if not re.fullmatch(r'[a-z0-9_]+', en or ''):
            errs.append(tag + '：键只用小写字母、数字、下划线')
        t = c.get('tier')
        if t not in TIERS:
            errs.append(tag + '：tier 不认得 ' + str(t))
        young = t in ('girl', 'boy', 'child') or c.get('minor')
        if t == 'small' and 'halfling' in (c.get('who') or '').lower():
            if re.search(r'(?i)\bcup\b|bust|\bhips?\b|waist', c.get('build') or ''):
                errs.append(tag + '：半身人的 build 不写胸、腰、胯')
            if re.search(r'(?i)adult face|grown woman|not a child', (c.get('who') or '') + (c.get('face') or '')):
                errs.append(tag + '：半身人是幼态脸，不写成年脸')
        if young:
            for k in (('minor', 'young_ok') if c.get('teen') else ('minor', 'young_ok', 'art_close')):
                if c.get(k) is not True:
                    errs.append(tag + '：年少的要写 %s: true' % k)
            if c.get('build'):
                errs.append(tag + '：年少的不写 build')
            for k in ('who', 'face', 'casual', 'private', 'battle', 'formal', 'art', 'art_extra'):
                m = BODY.search(c.get(k, '') or '')
                if m:
                    errs.append(tag + '：年少的 %s 里有写身体的词 %s' % (k, m.group()))
        if c.get('sex') not in ('m', 'f'):
            errs.append(tag + '：sex 只写 m 或 f')
        if t in ('girl',) and c.get('sex') != 'f' or t in ('boy', 'youth') and c.get('sex') != 'm':
            errs.append(tag + '：tier 跟 sex 对不上')
        bp = c.get('battle_pose')
        if bp and not (bp.startswith('3) ') and bp.endswith('. ')):
            errs.append(tag + '：battle_pose 要以 "3) " 开头、以句号加空格结尾')
        for k in ('anchor', 'identity'):
            v = c.get(k)
            if v and not os.path.exists(os.path.join(OUT, v)):
                (errs if k == 'anchor' else warns).append(tag + '：%s 的图还不在 %s' % (k, v))
        for k, v in c.items():
            if isinstance(v, str):
                m = BAN.search(v)
                if m:
                    errs.append(tag + '：%s 里有禁用的词 %s' % (k, m.group()))
                m = TAN.search(v)
                if m:
                    warns.append(tag + '：%s 里有 %s，页上写了晒黑才留' % (k, m.group()))
        n = len((c.get('who') or '').split())
        if n and not 40 <= n <= 200:
            warns.append(tag + '：who %d 个词，宜六十到一百四十' % n)
        if c.get('src') and not re.search(r':\d+$', c['src']):
            warns.append(tag + '：src 带上行号')
    return errs, warns


if __name__ == '__main__':
    bad = 0
    for p in sys.argv[1:]:
        e, w = lint(p)
        print('==', p, '问题 %d，提醒 %d' % (len(e), len(w)))
        for x in e:
            print('  问题', x)
        for x in w:
            print('  提醒', x)
        bad += len(e)
    sys.exit(1 if bad else 0)
