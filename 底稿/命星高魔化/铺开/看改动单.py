# -*- coding: utf-8 -*-
"""铺开·看改动单：把一份 apply_edits 格式的改动单印成只剩改动的部分，好过目。
仓库根上跑：python -I -X utf8 底稿/命星高魔化/铺开/看改动单.py 改动单.md [--cut 字数] [--from 编号序] [--to 编号序] [--only 关键字]
一块印一段：编号｜说明｜文件，旧（去掉前后一样的部分），新（同样去掉）。--cut 管新串最多印多少字，0 是不裁。"""
import io, re, sys

p = sys.argv[1]
def opt(k, d):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
cut = int(opt('--cut', '0'))
a0 = int(opt('--from', '1'))
b0 = int(opt('--to', '100000'))
only = opt('--only', '')
s = io.open(p, encoding='utf-8').read().replace('\r', '')
parts = re.split(r'(?m)^(?=### [^\s｜]*[0-9]+｜)', s)
k = 0
for part in parts:
    m = re.match(r'### (.+)\n', part)
    if not m:
        continue
    f = re.search(r'(?m)^文件：(.+)$', part)
    o = re.search(r'(?ms)^原文：\n~~~\n(.*?)\n~~~', part)
    n = re.search(r'(?ms)^改成：\n~~~\n(.*?)\n~~~', part)
    if not (f and o and n):
        continue
    k += 1
    if k < a0 or k > b0:
        continue
    if only and only not in part:
        continue
    a, b = o.group(1), n.group(1)
    pre = 0
    while pre < min(len(a), len(b)) and a[pre] == b[pre]:
        pre += 1
    suf = 0
    while suf < min(len(a), len(b)) - pre and a[-1 - suf] == b[-1 - suf]:
        suf += 1
    s0 = max(0, pre - 14)
    ao = a[s0:len(a) - suf + min(suf, 10)]
    bo = b[s0:len(b) - suf + min(suf, 10)]
    if cut and len(bo) > cut:
        bo = bo[:cut] + '…（共%d字）' % len(bo)
    if len(ao) > 160:
        ao = ao[:150] + '…（共%d字）' % len(ao)
    print('【%d】%s｜%s' % (k, m.group(1), f.group(1).strip()))
    print('  旧：' + ao.replace('\n', '⏎'))
    print('  新：' + bo.replace('\n', '\n      '))
tail = re.search(r'(?ms)^## .*', parts[-1]) if parts else None
if tail and '--tail' in sys.argv:
    print('\n' + tail.group(0))
