import sys, re
sys.stdout.reconfigure(encoding="utf-8")
d = open(sys.argv[1], encoding="utf-8").read()
def segs(t):
    t = re.sub(r"\s", "", t)
    return [s for s in re.split(r"[，。？！；、“”——…]", t) if s]
dg = set()
for s in segs(d):
    for i in range(len(s) - 5):
        dg.add(s[i:i+6])
for p in sys.argv[2:]:
    t = open(p, encoding="utf-8").read()
    hits = set()
    for s in segs(t):
        for i in range(len(s) - 5):
            g = s[i:i+6]
            if g in dg: hits.add(g)
    print(p.split("/")[-1], sorted(hits))
