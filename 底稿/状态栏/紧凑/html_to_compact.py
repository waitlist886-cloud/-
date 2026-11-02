# 把一条照旧骨架写的 HTML 回复转成紧凑记法（方向稿第二版的样本用，不进卡）。用法：python3 -I -X utf8 html_to_compact.py 回复.html 输出.txt
import re,sys
src=open(sys.argv[1],encoding='utf-8').read().replace('</div>','</div>\n').replace('</details>','</details>\n')
def txt(s):
    s=s.replace('<span class="ats">','｜').replace('</span><span class="at','</span>｜<span class="at')
    s=re.sub(r'\s*<i class="bar p\d+"></i>','｜EXP ',s)
    s=re.sub(r'<i class="c c-b"></i>',' 巴尔 ',s); s=re.sub(r'<i class="c c-s"></i>',' 索恩 ',s); s=re.sub(r'<i class="c c-p"></i>',' 便士 ',s)
    s=re.sub(r'<[^>]+>','',s)
    s=re.sub(r'[ 　]{2,}',' ',s).strip()
    return s
out=[]
meta=re.search(r'<span class="hud-meta">([^<]*)</span>',src).group(1).strip()
out.append('§底座｜纪元：'+meta)
weather=re.search(r'<div><b>天气</b><br>([^<]*)</div>',src).group(1)
timeline=re.search(r'<div><b>时辰</b><br>[^·<]*·\s*([^<]*)</div>',src).group(1)
out.append('§环境｜%s｜%s'%(weather,timeline))
for m in re.finditer(r'<div class="f d"><b>(\d)｜([^<]*)</b>(.*?)</div>\n',src):
    out.append('§推演｜%s｜%s｜%s'%(m.group(1),m.group(2),txt(m.group(3))))
place=re.search(r'<div class="arc-prose-head"><span>([^<]*)</span></div>',src).group(1)
out.append('§正文｜'+place)
prose=src[src.index('<div class="arc-prose-head">'):src.index('<div class="choices">')]
for p in re.findall(r'<p>(.*?)</p>',prose,re.S):
    out.append(''); out.append(txt(p))
out.append('')
for li in re.findall(r'<li>(.*?)</li>',src):
    out.append('§分支｜'+txt(li))
def section(cls, name):
    block=src[src.index('<details class="%s'%cls):]
    block=block[:block.index('</details>')+10]
    for lab,body in re.findall(r'<div class="f [a-z0-9]+"><b>([^<]*)</b>(.*?)</div>\n',block):
        out.append('§%s｜%s｜%s'%(name,lab,txt(body)))
section('arc-panel','面板')
section('arc-deed-panel','伟业')
section('arc-bag','背包')
npc=src[src.index('<div class="arc-npc-card">'):src.index('<details class="arc-daily"')]
nm=re.search(r'<div class="arc-npc-name"><b>([^<]*)</b><span>([^<]*)</span>',npc)
out.append('§角色｜%s｜%s｜名牌'%(nm.group(1),nm.group(2)))
tags=re.findall(r'<span>([^<]*)</span>',re.search(r'<div class="arc-npc-tags">(.*?)</div>',npc).group(1))
out.append('§角色签｜'+'｜'.join(t.strip() for t in tags))
out.append('§角色话｜'+re.search(r'<p>[“"]([^”"]*)[”"]</p>',npc).group(1))
main,more=npc.split('<details class="arc-npc-more">')
for m in re.finditer(r'<div class="nf ([a-z]+)"><b>([^<]*)</b>(.*?)(?:</div>|\n)',main):
    out.append('§角色行｜%s｜%s'%(m.group(2),txt(m.group(3))))
for lab,body in re.findall(r'<div class="nf [a-z]+"><b>([^<]*)</b>(.*?)</div>',more):
    out.append('§角色细｜%s｜%s'%(lab,txt(body)))
section('arc-daily','见闻')
mem=src[src.index('<details class="arc-memory"'):]
for lab,body in re.findall(r'<div class="f (?:mem|done)"><b>([^<]*)</b>(.*?)</div>',mem):
    out.append('§记忆｜%s｜%s'%(lab,txt(body)))
s='\n'.join(out)+'\n'
open(sys.argv[2],'w',encoding='utf-8').write(s)
print(len(src), len(s))
