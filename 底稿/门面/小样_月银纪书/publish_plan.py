#!/usr/bin/env python3
# 月银纪的书发布到私有网页用的清单。这张网页一版至多 511 个文件（连页面 512 项）、256MB，一回发布至多 255 个文件、64MB，所以分几批发到同一个地址。
#   python -I -X utf8 publish_plan.py 已发布的清单.txt 输出目录
# 已发布的清单是 Artifact 工具 list（scope files）回的那一段字，存成文件传进来（只认里头带引号的路径）。
# 出 batch_N.json：发布路径 → 本地路径（相对这个文件夹），要拿掉的写 null。
# 先后：只添图的批先发，页面拿旧的 index_v4.html 顶着（新图旧页面用不上，不碍事）；
# 哪一批发完线上会过 511 个，就在它前头先发“换页面”的那一批（新的 index.html、数据、人像拼图，同时拿掉不用的旧图），往后的批页面都用 index.html。
# 一直没过上限的话，换页面的那一批排在最后。11-12 头一回是把换页面排在最后，原画第一批撞了上限（deploy 422: manifest exceeds 512 entries）。
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
MAXN, MAXB, LIMIT = 240, 50 * 1000 * 1000, 511


def main():
    listed, out = sys.argv[1], sys.argv[2]
    pub = set(re.findall(r'"((?:assets|data)/[^"]+)"', open(listed, encoding='utf-8').read()))
    cg = json.load(open(os.path.join(HERE, 'data', 'cg.json'), encoding='utf-8'))
    pa = json.load(open(os.path.join(HERE, 'data', 'pa.json'), encoding='utf-8'))
    have = json.load(open(os.path.join(HERE, 'data', 'have.json'), encoding='utf-8'))
    need_cg = set()
    for e in cg.values():
        if e.get('key'):
            need_cg.add(e['key']['src'])
        for line in e.get('nodes', {}).values():
            for v in line.values():
                for x in (v if isinstance(v, list) else [v]):
                    need_cg.add(x['src'])
        for v in e.get('deaths', {}).values():
            need_cg.add(v['src'])
    murals = {'assets/m%02d.webp' % i for i in range(1, 28)}
    need_pa = {'assets/pa/%s.webp' % k for k in pa}
    need_ps = {'assets/ps/%s.webp' % k for k in have['ps']}
    data = {'data/cg.json', 'data/have.json', 'data/moon.json', 'data/pa.json', 'data/tiles.json'} | {'data/prof/m%02d.json' % i for i in range(1, 28)}
    need = murals | need_cg | need_pa | need_ps | data
    lost = sorted(p for p in need if not os.path.exists(os.path.join(HERE, p)))
    if lost:
        print('本地缺', len(lost), lost[:8])
        sys.exit(1)
    size = lambda p: os.path.getsize(os.path.join(HERE, p))
    gone = sorted(p for p in pub if p not in need)
    new_img = sorted(p for p in (need_ps | need_cg) if p not in pub)      # 已经发过、名字没变的图不重发（重画的换了名字）
    batches, cur, n = [], {}, 0
    for p in new_img:
        if len(cur) >= MAXN or n + size(p) > MAXB:
            batches.append(cur)
            cur, n = {}, 0
        cur[p] = p
        n += size(p)
    if cur:
        batches.append(cur)
    last = {p: p for p in sorted(data | need_pa)}
    last.update({p: None for p in gone})
    if len(last) > 255:
        print('换页面的那一批', len(last), '项，超了 255，要再拆')
    add_last = sum(1 for k, v in last.items() if v and k not in pub)
    plan, count, switched = [], len(pub), False       # (这一批, 页面用哪一份, 发完线上几个)
    for b in batches:
        if not switched and count + len(b) > LIMIT:
            count += add_last - len(gone)
            plan.append((last, 'index.html', count))
            switched = True
        count += len(b)
        plan.append((b, 'index.html' if switched else 'index_v4.html', count))
    if not switched:
        count += add_last - len(gone)
        plan.append((last, 'index.html', count))
    os.makedirs(out, exist_ok=True)
    print('线上现在 %d 个文件（不算页面）' % len(pub))
    for i, (b, page, cnt) in enumerate(plan, 1):
        json.dump(b, open(os.path.join(out, 'batch_%d.json' % i), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print('第 %d 批：%d 项，添 %d 个 %.1fMB，拿掉 %d 个，页面用 %s%s，发完线上 %d 个%s' % (
            i, len(b), sum(1 for v in b.values() if v), sum(size(k) for k, v in b.items() if v) / 1e6, sum(1 for v in b.values() if v is None),
            page, '（换页面的那一批）' if b is last else '', cnt, '　过了上限' if cnt > LIMIT else ''))
    total = need | {'index.html'}
    print('发完以后这一版：%d 个文件，%.1fMB' % (len(total), (sum(size(p) for p in need) + os.path.getsize(os.path.join(HERE, 'index.html'))) / 1e6))


if __name__ == '__main__':
    main()
