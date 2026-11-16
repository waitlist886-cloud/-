#!/usr/bin/env python3
# 全卡精炼洗稿：给 Codex 或者 Gemini（agy）搭一份活的文件夹（在仓库外头），收稿时再拿回来比。
#   python -I -X utf8 底稿/洗稿/全卡精炼/prep_job.py make <份名> <codex|agy> <文件…> [--note 话] [--splice]
#       文件写相对仓库根的路径。--splice：把主会话手写的样稿（样稿_第七歌一组.md）里已经洗好的条目先换进去，说明里写明别再动。
#   python -I -X utf8 底稿/洗稿/全卡精炼/prep_job.py check <份名> <codex|agy>      跑自查，拿 稿/ 跟 原/ 比
#   python -I -X utf8 底稿/洗稿/全卡精炼/prep_job.py take <份名> <codex|agy> [--apply]   把洗好的拷回仓库（先只报）
# 文件夹：Codex 在 C:/Users/waitl/codex_work/wash_1115/<份名>，agy 在 C:/Users/waitl/agy_work/wash_1115/<份名>。
import io
import json
import os
import re
import shutil
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
BASE = {'codex': 'C:/Users/waitl/codex_work/wash_1115', 'agy': 'C:/Users/waitl/agy_work/wash_1115'}
SAMPLE = os.path.join(HERE, '样稿_第七歌一组.md')
SRC_OF_SAMPLE = [('月银纪史诗/第七歌_焚原断刃.md', ['## 月银纪·主线｜万兽·焚原（第二稿）', '## 旅途同行：麦伦（月银纪·焚原断刃）', '## 旅途同行·背景：麦伦',
                                              '### 不折之腰 (Special | Legend)', '### 眠山血脉 (Passive | Legend)', '### 刈穗 (Art | Rare)']),
                 ('月银纪补卷/羁绊_06.md', ['## 月银纪·羁绊｜弯腰之章·带禾捆回来']),
                 ('月银纪补卷/地点_06_万兽诸地.md', ['## 月银纪·地点｜霜渡与三座平顶的山'])]


def rd(p):
    return open(p, encoding='utf-8', newline='').read().replace('\r\n', '\n')


def block(text, head):
    """从 head 那一行起取一块。## 的取到下一个 ## 以前；### 的取到下一个 ###、## 或条目设置以前。回（起，止）。"""
    i = text.index('\n' + head + '\n') + 1 if not text.startswith(head + '\n') else 0
    stops = [r'^## '] if head.startswith('## ') else [r'^### ', r'^## ', r'^> 条目设置']
    j = len(text)
    for st in stops:
        m = re.search(st, text[i + len(head):], re.M)
        if m:
            j = min(j, i + len(head) + m.start())
    return i, j


def sample_blocks():
    s = rd(SAMPLE)
    out = {}
    for _, heads in SRC_OF_SAMPLE:
        for h in heads:
            i, j = block(s, h)
            out[h] = s[i:j].rstrip('\n') + '\n\n'
    return out


def before_after():
    """样稿的改前（从源稿取同样那几条）和改后。"""
    sb = sample_blocks()
    old, new = ['# 样稿 · 改前（源稿里的原样）\n'], ['# 样稿 · 改后（主会话手写的，幅度和口气照它）\n']
    for f, heads in SRC_OF_SAMPLE:
        src = subprocess.run(['git', '-C', ROOT, 'show', '详本_11-15:' + f], capture_output=True).stdout.decode('utf-8').replace('\r\n', '\n')
        for h in heads:
            i, j = block(src, h)
            old.append(src[i:j].rstrip('\n') + '\n')
            new.append(sb[h].rstrip('\n') + '\n')
    return '\n'.join(old), '\n'.join(new)


def make(name, engine, files, note, splice):
    d = os.path.join(BASE[engine], name)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(os.path.join(d, '稿'))
    os.makedirs(os.path.join(d, '原'))
    sb = sample_blocks()
    done = []
    meta = {'files': {}, 'engine': engine}
    for f in files:
        text = rd(os.path.join(ROOT, f))
        base = os.path.basename(f)
        open(os.path.join(d, '原', base), 'w', encoding='utf-8', newline='\n').write(text)
        if splice:
            for sf, heads in SRC_OF_SAMPLE:
                if sf == f:
                    for h in heads:
                        i, j = block(text, h)
                        text = text[:i] + sb[h] + text[j:]
                        done.append(h)
        open(os.path.join(d, '稿', base), 'w', encoding='utf-8', newline='\n').write(text)
        meta['files'][base] = f
    for x in ('洗稿说明.md', '自查.py'):
        shutil.copyfile(os.path.join(HERE, x), os.path.join(d, x))
    old, new = before_after()
    open(os.path.join(d, '样稿_改前.md'), 'w', encoding='utf-8', newline='\n').write(old)
    open(os.path.join(d, '样稿_改后.md'), 'w', encoding='utf-8', newline='\n').write(new)
    a = ['# 这个文件夹的活', '',
         '照 `洗稿说明.md` 把 `稿/` 里的文件洗一遍。先把 `洗稿说明.md` 读完，再对着读 `样稿_改前.md` 和 `样稿_改后.md`，幅度和口气照样稿。', '',
         '要洗的文件：' + '、'.join('`稿/%s`' % os.path.basename(f) for f in files), '']
    if done:
        a += ['下面几条主会话已经洗好、换进 `稿/` 里了（就是样稿里的那几条），**不要再动**：', ''] + ['- `%s`' % h for h in done] + ['']
        a += ['别的条目照同样的幅度洗。同一个文件里别的条目要是把上面几条已经讲过的事又讲了一遍，收成一句、只提名字。', '']
    if note:
        a += ['这一份另外要注意的：' + note, '']
    if engine == 'codex':
        a += ['做完在这个文件夹里跑 `python -I -X utf8 自查.py`，报“错”的都改掉，再交。', '']
    else:
        a += ['这里跑不了命令，不用跑自查，写完自己照 `洗稿说明.md` 第三、四节逐条对一遍：受保护的行一个字没动，没有禁用的标点，引号里的话没改字，数字都出自原稿。', '']
    a += ['交三样：`稿/` 里改好的文件（文件名不变），`改动说明.md`，`删除单.md`。只动这三样，不要改 `原/`，不要联网。', '',
          '一条一条地洗，整份洗完再交，别洗到一半就停。文件长，照 `## ` 标题一节一节来。']
    open(os.path.join(d, 'AGENTS.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(a) + '\n')
    json.dump(meta, open(os.path.join(d, 'job.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('搭好了', d, '｜文件', len(files), '｜先换进去的样稿条目', len(done))


def check(name, engine):
    d = os.path.join(BASE[engine], name)
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, '自查.py'), os.path.join(d, '稿'), os.path.join(d, '原')], capture_output=True)
    print(r.stdout.decode('utf-8', 'replace'))


def take(name, engine, apply):
    d = os.path.join(BASE[engine], name)
    meta = json.load(open(os.path.join(d, 'job.json'), encoding='utf-8'))
    for base, f in meta['files'].items():
        new = rd(os.path.join(d, '稿', base))
        p = os.path.join(ROOT, f)
        raw = open(p, encoding='utf-8', newline='').read()
        crlf = '\r\n' in raw
        cur = raw.replace('\r\n', '\n')
        org = rd(os.path.join(d, '原', base))
        if cur != org:
            print('！仓库里的 %s 在派活以后又改过，先别拷，手工并' % f)
            continue
        print('%s：%d 字 → %d 字%s' % (f, len(cur), len(new), '，拷回去了' if apply else ''))
        if apply:
            open(p, 'w', encoding='utf-8', newline='').write(new.replace('\n', '\r\n') if crlf else new)


if __name__ == '__main__':
    cmd, name, engine = sys.argv[1], sys.argv[2], sys.argv[3]
    rest = sys.argv[4:]
    if cmd == 'make':
        note = ''
        if '--note' in rest:
            k = rest.index('--note')
            note = rest[k + 1]
            rest = rest[:k] + rest[k + 2:]
        splice = '--splice' in rest
        make(name, engine, [x for x in rest if not x.startswith('--')], note, splice)
    elif cmd == 'check':
        check(name, engine)
    elif cmd == 'take':
        take(name, engine, '--apply' in rest)
