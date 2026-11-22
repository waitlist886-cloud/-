# 神域共用条目的触发词在全卷里出现多少回（11-22）：这些条目不挡纪元，触发词撞上寻常的话就会白醒。
#   python -I -X utf8 底稿/神域/tools/trig_freq.py
# 数的是四纪各页、补卷和底卡正文里的次数（神域自己那几份不算），多于 3 回的列出来。
import glob
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))


def corpus():
    out = []
    pats = ['月银纪史诗/*.md', '诸国期/诸国期时段_*.md', '萨尔维斯/萨尔维斯时段_*.md', '月银纪补卷/*.md', '纷争纪/纷争纪时段_*.md', '纷争纪/补卷/*.md',
            '山铜纪/山铜纪时段_*.md', '山铜纪/补卷/*.md', '迷宫纪前传/迷宫纪前传时段_*.md', '迷宫纪前传/补卷/*.md', '底卡新条目/*.md']
    for p in pats:
        for f in glob.glob(os.path.join(ROOT, p)):
            if '神域' in os.path.basename(f):
                continue
            t = open(f, encoding='utf-8').read()
            # 神谱各条里新添的神域栏不算
            t = re.sub(r'(?m)^- (?:神力|神性|权柄[一二三]?｜[^：]+|神域专长|神国|国律|对上祂|陨落以后|倒下以后|剥离以后)：.*$', '', t)
            out.append(t)
    lb = json.load(open(os.path.join(ROOT, 'src', 'rili_v7.json'), encoding='utf-8'))['prompt']['lorebook']
    out.extend(e['content'] for e in lb)
    return '\n'.join(out)


def main():
    C = corpus()
    for f in ('神域_规则.md', '神域_七十二域.md'):
        t = open(os.path.join(ROOT, '通用条目', f), encoding='utf-8').read()
        title = ''
        for ln in t.split('\n'):
            m = re.match(r'^## 奥尔德兰·(.+)$', ln)
            if m:
                title = m.group(1)
            m = re.match(r'^> 条目设置：.*?触发 (.+?)，黑名单', ln)
            if not m:
                continue
            words = []
            for w in re.split(r'、(?![^`]*`(?:[^`]*`[^`]*`)*[^`]*$)', m.group(1)):
                w = w.strip()
                if w.startswith('`/') and w.endswith('/`'):
                    words += [(x, re.compile(x)) for x in w[2:-2].split('|')]
                else:
                    words.append((w, re.compile(re.escape(w))))
            bad = [(w, len(rx.findall(C))) for w, rx in words]
            bad = [(w, n) for w, n in bad if n > 3]
            if bad:
                print(title, '｜', '，'.join('%s %d' % x for x in bad))


if __name__ == '__main__':
    main()
