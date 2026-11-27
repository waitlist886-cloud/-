#!/usr/bin/env python3
# 风月：把一纪的卡里 DLC 那几包的条目拆出来，做成纯世界书的 mod（照风月世界书模板，跟 世界书_第N份.json 一个格式），本卡只留别的。
# 11-26 用户：“确实超时了（前传整卡 12.9MB），不过风月也能上传 mod，你可以看下前传有没有能拆成 mod 的条目，按照世界书模板改成纯世界书的 mod，我和迷宫纪前传的本卡分开”。
# 用法（仓库根上，先照常跑 fy_shell.py、build_fy_era.py 出好 导入/）：
#   python -I -X utf8 底稿/风月版/fy_mod.py [纪…]    纪默认 pre（迷宫纪前传）
# 出：out/发布卡_风月_四纪/<纪>/拆mod/
#   <纪>_本卡.json            外壳加 DLC 以外的世界书，整卡一张导
#   <纪>_mod_<包名>.json      一包一份（过 4.6MB 切第几份），{"world_book": [...]}
#   说明.md
# 哪一条归哪一包照日里切 DLC 的规矩（底稿/DLC/tools/packs.json、make_dlc.pick），拿 世界书_转换.json 里的 _src 对回日里全本的下标。
import collections
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'DLC', 'tools'))
import fy_lore as L      # noqa: E402
import fy_gate as G      # noqa: E402
import make_dlc as MD    # noqa: E402

PART = 4600 * 1024
# 日里 DLC 以外再拆的：照文件夹前缀归一包（前传本卡拆完 DLC 还有 10.9MB，贴着风月整卡导入的线，再挪一包世界观的出去）
EXTRA = {'pre': collections.OrderedDict([('世界观补遗', ('02·', '03·', '04·', '52·迷宫纪', '54·迷宫纪'))])}
WHOLE = 11 * 1000 * 1000


def dumps(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':'))


def main():
    cards = [G.card_of(a) for a in sys.argv[1:]] or ['pre']
    lb = json.load(open(L.SRC, encoding='utf-8'))['prompt']['lorebook']
    packs = json.load(open(os.path.join(HERE, '..', 'DLC', 'tools', 'packs.json'), encoding='utf-8'))
    rel = list(packs['_发布'])
    pack_of = {}
    for name, idx in MD.pick(lb, packs, rel).items():
        for i in idx:
            pack_of.setdefault(i, name)
    for card in cards:
        era = G.CARDS[card]['dir']
        d = os.path.join(L.OUT, era)
        conv = json.load(open(os.path.join(d, '世界书_转换.json'), encoding='utf-8'))['entries']
        by_val = {x['value']: pack_of.get(x['_src']) for x in conv}
        imp = os.path.join(d, '导入')
        base = json.load(open(os.path.join(imp, '%s_小底卡.json' % era), encoding='utf-8'))
        lore = []
        k = 1
        while os.path.exists(os.path.join(imp, '%s_世界书_第%d份.json' % (era, k))):
            lore += json.load(open(os.path.join(imp, '%s_世界书_第%d份.json' % (era, k)), encoding='utf-8'))['world_book']
            k += 1
        ex = EXTRA.get(card, {})
        keep, mods = [], collections.OrderedDict((n, []) for n in rel + list(ex))
        for e in lore:
            p = by_val.get(e['value']) or next((n for n, pre in ex.items() if (e.get('group') or '').startswith(pre)), None)
            (mods[p] if p else keep).append(e)
        out = os.path.join(d, '拆mod')
        os.makedirs(out, exist_ok=True)
        for f in os.listdir(out):
            os.remove(os.path.join(out, f))
        whole = dict(base)
        whole['world_bk'] = base['world_bk'] + keep
        txt = dumps(whole).encode('utf-8')
        open(os.path.join(out, '%s_本卡.json' % era), 'wb').write(txt)
        rows = ['%s_本卡.json：外壳加世界书 %d 条（常驻 %d），%.2f MB%s' % (era, len(whole['world_bk']), len(base['world_bk']), len(txt) / 1048576,
                                                                '' if len(txt) <= WHOLE else '，还是过了 11MB')]
        n_mod = 0
        for name, es in mods.items():
            if not es:
                continue
            parts, cur, size = [], [], 16
            for e in es:
                n = len(dumps(e).encode('utf-8')) + 1
                if cur and size + n > PART:
                    parts.append(cur)
                    cur, size = [], 16
                cur.append(e)
                size += n
            parts.append(cur)
            for j, p in enumerate(parts, 1):
                fn = '%s_mod_%s%s.json' % (era, name, '' if len(parts) == 1 else '_第%d份' % j)
                t = dumps({'world_book': p}).encode('utf-8')
                open(os.path.join(out, fn), 'wb').write(t)
                rows.append('%s：%d 条，%.2f MB' % (fn, len(p), len(t) / 1048576))
                n_mod += len(p)
        assert len(keep) + n_mod == len(lore)
        md = ['# %s：本卡和 mod 分开导（风月）' % era, '',
              '整卡 %.1f MB 导不进（风月整卡导入 11.3MB 导得进、12.6MB 超时），把日里那边切成 DLC 的那几包（%s）的条目拆出来，做成纯世界书的 mod。' % (
                  (len(txt) + sum(len(dumps(e)) for es in mods.values() for e in es)) / 1048576, '、'.join(n for n, es in mods.items() if es)), '',
              '先导本卡，再一份一份上传 mod（世界书模板的格式，跟分份导入的 世界书_第N份 一样）。mod 里的条目跟本卡一条不重，钥匙照原样，醒法跟整卡一样。', '']
        md += ['- ' + r for r in rows]
        open(os.path.join(out, '说明.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
        print('\n'.join(rows))


if __name__ == '__main__':
    main()
