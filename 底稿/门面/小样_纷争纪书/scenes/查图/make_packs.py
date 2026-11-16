#!/usr/bin/env python3
# 传奇之陨新添那一批的查图包（11-16）。一位审稿人一包：图拷到一个文件夹，旁边一份清单（哪一幅、场面稿、要留神的）。
#   python -I -X utf8 底稿/门面/小样_纷争纪书/scenes/查图/make_packs.py <输出目录> [每包几幅=12]
#   python -I -X utf8 底稿/门面/小样_纷争纪书/scenes/查图/make_packs.py <输出目录> [每包几幅] --fixed
#       第二遍：只包改过的（有 <键>_a0.png 的新图），一幅带两张，<键>.png 是改后的，<键>_改前.png 是原来的，清单里写这一幅改的是什么。不混对照。
# 每包混一幅已知有毛病的旧图（上一轮重画以前的 <键>_a0.png，拷进去的时候去掉 _a0），不告诉审稿人是哪一幅，回来看他认没认出来。
# 对照是哪几幅记在 <输出目录>/对照.json（别给审稿人看）。
import glob
import io
import json
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LEG = os.path.normpath(os.path.join(HERE, '..', 'legends'))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
IMG = os.path.join(ROOT, '底稿', '状态栏', 'comfy', 'out', '门面_原画_纷争纪')
NEW = 'IJKLMNOPQ'


def falls(letters):
    out = []
    for f in sorted(glob.glob(os.path.join(LEG, 'g?.json'))):
        if os.path.basename(f)[1] not in letters:
            continue
        d = json.load(open(f, encoding='utf-8'))
        for x in d.get('falls', []):
            x = dict(x)
            x['_file'] = os.path.basename(f)
            out.append(x)
    return out


def main():
    out = sys.argv[1]
    per = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 12
    if '--fixed' in sys.argv:
        return fixed(out, per)
    new = [x for x in falls(NEW) if os.path.exists(os.path.join(IMG, x['key'] + '.png'))]
    lack = [x['key'] for x in falls(NEW) if not os.path.exists(os.path.join(IMG, x['key'] + '.png'))]
    old = {x['key']: x for x in falls('ABCDEFGH')}
    ctrl = sorted(k for k in old if os.path.exists(os.path.join(IMG, k + '_a0.png')))
    packs = [new[i:i + per] for i in range(0, len(new), per)]
    if len(packs) > 1 and len(packs[-1]) < per // 2:
        packs[-2] += packs.pop()
    os.makedirs(out, exist_ok=True)
    note = {}
    for n, pk in enumerate(packs, 1):
        d = os.path.join(out, '包%d' % n)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        items = [(x, x['key'] + '.png') for x in pk]
        if ctrl:
            c = old[ctrl[(n - 1) % len(ctrl)]]
            note['包%d' % n] = c['key']
            items.insert(len(items) // 2, (c, c['key'] + '_a0.png'))
        lines = ['# 查图包 %d' % n, '', '图都在这个文件夹里，文件名就是键加 .png。一幅一节：', '']
        for x, src in items:
            shutil.copyfile(os.path.join(IMG, src), os.path.join(d, x['key'] + '.png'))
            lines += ['## ' + x['key'] + '｜' + (x.get('death') or x.get('name') or ''),
                      '- 图名：' + (x.get('name') or ''),
                      '- 时候和地方：' + (x.get('when') or '') + '｜' + (x.get('where') or ''),
                      '- 经过（中文，书里给玩家看的）：' + (x.get('how') or ''),
                      '- 这个人：' + ('看着不满十八岁，画的是出事以前最后一个完好的瞬间，不该有伤口和血' if x.get('young') else '成年人，场面写了血和伤的照画'),
                      '- 场面稿（英文，出图用的）：' + (x.get('text') or ''), '']
        open(os.path.join(d, '清单.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
        print('包%d %d 幅 → %s' % (n, len(items), d))
    json.dump(note, open(os.path.join(out, '对照.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('新图 %d 幅，还没出的 %d 幅：%s' % (len(new), len(lack), ' '.join(lack)))


def fixed(out, per):
    how = {}
    for f in sorted(glob.glob(os.path.join(HERE, '改法_*.json'))):
        how.update(json.load(open(f, encoding='utf-8')))
    todo = [x for x in falls(NEW) if os.path.exists(os.path.join(IMG, x['key'] + '_a0.png')) and os.path.exists(os.path.join(IMG, x['key'] + '.png'))]
    wait = [x['key'] for x in falls(NEW) if os.path.exists(os.path.join(IMG, x['key'] + '_a0.png')) and not os.path.exists(os.path.join(IMG, x['key'] + '.png'))]
    if '--only' in sys.argv:                      # 只包点名的几个键（补一包用）
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
        todo = [x for x in todo if x['key'] in only]
    first = int(sys.argv[sys.argv.index('--from') + 1]) if '--from' in sys.argv else 1    # 包的编号从几起
    packs = [todo[i:i + per] for i in range(0, len(todo), per)]
    if len(packs) > 1 and len(packs[-1]) < per // 2:
        packs[-2] += packs.pop()
    os.makedirs(out, exist_ok=True)
    json.dump([x['key'] for x in todo], open(os.path.join(out, '复查_包了哪些_从%d.json' % first), 'w', encoding='utf-8'), ensure_ascii=False)
    for n, pk in enumerate(packs, first):
        d = os.path.join(out, '复查%d' % n)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        lines = ['# 复查包 %d' % n, '', '一幅两张：`<键>.png` 是改后的（要查的），`<键>_改前.png` 是原来的（只拿来比）。', '']
        for x in pk:
            k = x['key']
            shutil.copyfile(os.path.join(IMG, k + '.png'), os.path.join(d, k + '.png'))
            shutil.copyfile(os.path.join(IMG, k + '_a0.png'), os.path.join(d, k + '_改前.png'))
            v = how.get(k) or {}
            if v.get('verdict') == '改':
                what = '只改一处。原来的毛病：' + (v.get('see') or '') + '\n- 叫它改的（英文原话）：' + (v.get('change') or '')
            elif k in FLIPPED:
                what = '整幅左右翻转了一下（原来左右跟场面稿相反），别的没动。只看翻过来以后左右对不对。'
            else:
                what = '整幅重画（原来那一张整幅坏了，场面稿改过）。改前那一张只当参考，改后这一张当一幅新图从头查。'
            lines += ['## ' + k + '｜' + (x.get('death') or x.get('name') or ''),
                      '- 这一回：' + what,
                      '- 经过（中文）：' + (x.get('how') or ''),
                      '- 这个人：' + ('看着不满十八岁，不该有伤口和血' if x.get('young') else '成年人'),
                      '- 场面稿（英文，现在的）：' + (x.get('text') or ''), '']
        open(os.path.join(d, '清单.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
        print('复查%d %d 幅 → %s' % (n, len(pk), d))
    print('改后出好了的 %d 幅，还没出的 %d 幅：%s' % (len(todo), len(wait), ' '.join(wait)))


FLIPPED = {'s10_f_ilase'}


if __name__ == '__main__':
    main()
