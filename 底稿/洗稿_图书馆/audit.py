#!/usr/bin/env python3
# 洗稿试点的机器关（11-28）：洗后稿对原稿，硬的不过就打回。
#   python -I -X utf8 底稿/洗稿_图书馆/audit.py 书名 [轮次，默认 1]
# 查：元信息行、## 小标题、〔…〕标记（次序）、青墨注脚、带“·”的人名、数字串一样不少；篇幅 ±15%；
#     禁用标点、禁词、月相、科技词、中式口语、GPT 腔；八股高频词每万字前后对比。
import io, os, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HERE = os.path.join(ROOT, '底稿', '洗稿_图书馆')
BOOKS = os.path.join(ROOT, '底稿', '门面', '第二轮', '大图书馆', '书稿')

BAN_P = ['——', '—', '；', '…', '！', '...']
BAN_W = ['学宫', '客栈', '朝廷', '门客', '时辰', '掌柜', '客官', '百官', '丫头', '宗门', '长老', '功法', '镖局',
         '一丝', '一抹', '嘴角勾起', '玩味', '命运的齿轮', '历史的车轮', '山雨欲来', '不禁', '深不可测', '恐怖如斯', '威压', '修为',
         '新月', '满月', '残月', '月牙', '弦月', '月亮', '月光', '量子', '坐标', '频率', '能量', '系统']
COLLOQ = ['咱', '俺', '啥', '甭', '咋', '晌午', '得嘞', '哎呀', '哎哟', '呗', '嘛', '罢了', '吾', '汝', '矣', '焉', '爹', '娘', '掌柜', '伙计', '老伙计']
GPT = ['不是', '而是', '不仅', '更是', '交织', '宛如', '仿佛', '彷佛', '如同一', '似乎在诉说', '静静地', '缓缓地', '轻轻地', '默默地', '心中', '灵魂深处', '命运']
SHUMIAN = ['享年', '逐张', '逐行', '逐字', '逐层', '逐个', '依次', '陆续', '接连', '渐渐', '始终', '此前', '竟', '充作', '供人', '随即', '遂']
BAGU = ['往后', '头一回', '那一位', '这一样', '那一样', '照旧', '前头', '后头', '一个一个', '一面一面', '没说话', '不说话', '看了很久', '别的不写', '不记']


def body(t):
    return re.sub(r'(?m)^>.*$', '', t)


def per10k(t, ws):
    n = len(re.findall(r'[一-鿿]', t)) or 1
    return {w: round(t.count(w) * 10000 / n, 1) for w in ws}


def main(book, rnd):
    a = io.open(os.path.join(BOOKS, book + '.md'), encoding='utf-8').read()
    bp = os.path.join(HERE, '试点B', book, '第%d轮' % rnd, '洗后.md')
    if not os.path.exists(bp):
        print('没有洗后稿', bp); return
    b = io.open(bp, encoding='utf-8').read()
    hard = []
    def same(name, xa, xb):
        if xa != xb:
            lost = [x for x in xa if x not in xb]; extra = [x for x in xb if x not in xa]
            hard.append('%s 对不上：少了 %s｜多了 %s' % (name, lost[:6], extra[:6]))
    same('元信息行', re.findall(r'(?m)^>.*$', a), re.findall(r'(?m)^>.*$', b))
    same('小标题', re.findall(r'(?m)^#{1,3} .*$', a), re.findall(r'(?m)^#{1,3} .*$', b))
    same('方括号标记', re.findall(r'〔[^〕]{1,20}〕', a), re.findall(r'〔[^〕]{1,20}〕', b))
    ca = collections.Counter(re.findall(r'[一-鿿]{1,6}·[一-鿿]{1,6}', a))
    cb = collections.Counter(re.findall(r'[一-鿿]{1,6}·[一-鿿]{1,6}', b))
    lostn = [k for k in ca if k not in cb]
    if lostn: hard.append('带·的名字没了：%s' % lostn[:10])
    na = collections.Counter(re.findall(r'\d+', a)); nb = collections.Counter(re.findall(r'\d+', b))
    lostd = [k for k in na if nb[k] < na[k]]
    if lostd: hard.append('数字少了：%s' % lostd[:12])
    for ln in a.split('\n'):
        if '青墨' in ln and ln.strip() and ln.strip() not in b:
            hard.append('青墨注脚改了：%s' % ln.strip()[:40])
    la, lb = len(re.findall(r'[一-鿿]', a)), len(re.findall(r'[一-鿿]', b))
    ratio = lb / la
    if not 0.85 <= ratio <= 1.15: hard.append('篇幅 %d→%d 字，%.0f%%，出了 ±15%%' % (la, lb, ratio * 100))
    bb = body(b)
    for w in BAN_P + BAN_W:
        if w in bb: hard.append('禁用：%s ×%d' % (w, bb.count(w)))
    soft = []
    for w in COLLOQ:
        k = bb.count(w) - body(a).count(w)
        if k > 0: soft.append('中式口语 %s 多了 %d' % (w, k))
    for w in GPT:
        k = bb.count(w) - body(a).count(w)
        if k > 0: soft.append('GPT 腔 %s 多了 %d' % (w, k))
    for w in SHUMIAN:
        k = bb.count(w) - body(a).count(w)
        if k > 0: soft.append('书面词 %s 多了 %d' % (w, k))
    print('==', book, '第%d轮' % rnd, '｜汉字 %d→%d（%.0f%%）' % (la, lb, ratio * 100))
    print('硬：' + ('无' if not hard else ''))
    for h in hard: print('  ' + h)
    print('软：' + ('无' if not soft else ''))
    for s in soft: print('  ' + s)
    pa, pb = per10k(body(a), BAGU), per10k(bb, BAGU)
    print('八股高频（每万字，前→后）：' + '，'.join('%s %s→%s' % (w, pa[w], pb[w]) for w in BAGU if pa[w] or pb[w]))


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
