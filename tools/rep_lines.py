# 用法：python -X utf8 rep.py 文件 <<< 'old|||new' 多行，每行一对；每个 old 必须正好出现一次
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read()
for line in sys.stdin.read().split('\n'):
    if '|||' not in line: continue
    a,b=line.split('|||',1)
    n=t.count(a)
    if n!=1: print('!! count',n,a); continue
    t=t.replace(a,b)
open(p,'w',encoding='utf-8').write(t)
