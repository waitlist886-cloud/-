# 从拼好的页里抽台词样例给 genshin-dialogue-voice 的 voice_check.py 用，写成「## 说话人」加「- 台词」
# 用法（在仓库根目录下）：python3 -I -X utf8 tools/extract_samples.py 拼好的页.md 输出.txt，再跑 voice_check.py 输出.txt --ban "…！—；"
# 说话人：【独立声口｜X】标记 > 人物条里的「- X｜」小条 > ## 标题（人物条取逗号后面那一截）
import re, sys
NOTE = re.compile(r'(?m)^## (?:这一份的设计备注|设计备注)')
LEG = re.compile(r'(?ms)^## 这一段的传奇表.*?(?=^## )')
def title_name(t):
    t = re.sub(r'（人物）$|\(人物\)$', '', t).strip()
    t = re.sub(r'^(?:旅途同行：|旅途同行·背景：)', '', t)
    t = re.sub(r'（[^（）]*）$', '', t)
    if '，' in t:
        t = t.split('，')[-1]
    return t.split('·')[0][:12]
def run(path):
    s = open(path, encoding='utf-8').read().replace('\r', '')
    m = NOTE.search(s)
    if m:
        s = s[:m.start()]
    s = LEG.sub('', s)
    out, sp = [], None
    for line in s.split('\n'):
        h = re.match(r'^## (.+)$', line)
        if h:
            sp = title_name(h.group(1)); continue
        v = re.search(r'【独立声口｜([^】]+)】', line)
        if v:
            name = v.group(1)
            name = re.sub(r'（传奇）', '传奇', name)
            sp = re.sub(r'[（(].*$', '', name)[:12]; continue
        b = re.match(r'^\s*-\s*([^｜：:\s，。]{1,12})｜', line)
        if b:
            sp = b.group(1); continue
        t = re.search(r'台词样例[：:](.+)$', line)
        if t and sp:
            body = t.group(1)
            parts = [p.strip() for p in body.split('／') if p.strip()]
            lines = []
            for p in parts:
                p = re.sub(r'（[^（）]*）', '', p).strip()
                p = p.strip('“”「」 ')
                if p:
                    lines.append(p)
            if lines:
                out.append('## ' + sp)
                out += ['- ' + x for x in lines]
    return '\n'.join(out) + '\n'
if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    open(dst, 'w', encoding='utf-8').write(run(src))
