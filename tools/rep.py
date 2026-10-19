# usage: python rep.py file.md "old1" "new1" ["old2" "new2" ...]  each old must occur exactly once
import sys
p=sys.argv[1]; t=open(p,encoding='utf-8').read()
args=sys.argv[2:]
for i in range(0,len(args),2):
    a,b=args[i],args[i+1]
    n=t.count(a)
    if n!=1: raise SystemExit(f'count {n}: {a[:40]}')
    t=t.replace(a,b)
open(p,'w',encoding='utf-8').write(t); print('ok',p.split('/')[-1])
