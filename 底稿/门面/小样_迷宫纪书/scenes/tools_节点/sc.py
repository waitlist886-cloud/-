import json,sys,glob
from PIL import Image
S='E:/aldran_art/底稿/门面/小样_迷宫纪书/scenes/'
OUT='E:/aldran_art/底稿/状态栏/comfy/out/门面_原画_迷宫纪_节点/'
idx={}
for f in sorted(glob.glob(S+'n[1-6].json')):
    for n in json.load(open(f,encoding='utf8'))['nodes']: idx[n['key']]=n
for k in sys.argv[1:]:
    n=idx[k]
    try: sz=Image.open(OUT+k+'.png').size
    except Exception: sz=None
    print('==',k,n['line'],n['act'],n['name'],sz,'noface' if n.get('noface') else '','young' if n.get('young') else '')
    print('who:',[w[0]+'/'+w[2] for w in n.get('who',[])], 'beast:',n.get('beast'),'like:',n.get('like'))
    print(n['text'])
    print()
