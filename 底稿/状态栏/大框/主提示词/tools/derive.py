# 11-23 立源稿：拿流水线打出来的主提示词、后置词（make_four_era_card.py 每回打卡都存一份在输出目录：主提示词_流水线.txt、后置词_流水线.txt），
# 过第一段（prompt_stage1.split：1001 年的硬锚、手边的东西、名录切出去）、第二段（prompt_stage2.system / rear：骨架和后置词理一遍），
# 照大节切开写成 主提示词/NN_*.md、后置词.md、常驻_迷宫纪1001年.md。
#   python -I -X utf8 底稿/状态栏/大框/主提示词/tools/derive.py <主提示词_流水线.txt> <后置词_流水线.txt>            只比：照两段推出来的跟眼下的源稿一不一样
#   … --write    写源稿（头一回立，或者想整个重来；手改过的源稿会被盖掉）
#   … --finger   只记指纹（源稿手改过、流水线那一头也变了，看过以后记新指纹）
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
BIG = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, BIG)
import prompt_stage1 as S1   # noqa: E402
import prompt_stage2 as S2   # noqa: E402
import prompt_src as PS      # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
pipe_sp = open(args[0], encoding='utf-8', newline='').read().replace('\r\n', '\n')
pipe_rp = open(args[1], encoding='utf-8', newline='').read().replace('\r\n', '\n')


def save_finger():
    json.dump({'主提示词': PS.sha(pipe_sp), '后置词': PS.sha(pipe_rp), '字数': [len(pipe_sp), len(pipe_rp)]},
              open(os.path.join(PS.SRC, PS.FINGER), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('指纹记了', PS.sha(pipe_sp), PS.sha(pipe_rp))


if '--finger' in sys.argv:
    save_finger()
    sys.exit()

sp1, res1, acct = S1.split(pipe_sp)
sp2, places = S2.system(sp1)
rp2 = S2.rear(pipe_rp)
# 1001 常驻：第一段切出来的那一份，在「名录与固定名词」那一节前头添「底座和面板」一节
mark = '# 名录与固定名词（迷宫纪1001年'
assert res1.count(mark) == 1
res2 = res1.replace(mark, S2.res_1001_format(places) + '\n\n' + mark)

# 主提示词照大节切：每个行首「# 」起一节，原样切，接起来一字不差
cuts = [m.start() for m in re.finditer(r'(?m)^# ', sp2)]
assert cuts and cuts[0] == 0, cuts[:2]
secs = [sp2[a:b] for a, b in zip(cuts, cuts[1:] + [len(sp2)])]
names = []
for i, s in enumerate(secs):
    title = s.split('\n', 1)[0][2:]
    title = re.split(r'[（(]', title)[0].strip().replace('·', '_').replace(' ', '')
    names.append('%02d_%s.md' % (i + 1, title))
assert ''.join(secs) == sp2

if '--write' in sys.argv:
    os.makedirs(PS.SRC, exist_ok=True)
    for n in PS.parts():
        os.remove(os.path.join(PS.SRC, n))
    for n, s in zip(names, secs):
        open(os.path.join(PS.SRC, n), 'w', encoding='utf-8', newline='\n').write(s)
    open(os.path.join(PS.SRC, PS.REAR), 'w', encoding='utf-8', newline='\n').write(rp2 + '\n')
    open(os.path.join(PS.SRC, PS.RES), 'w', encoding='utf-8', newline='\n').write(res2)
    save_finger()
    print('写了', names, PS.REAR, PS.RES)

same = (PS.system() == sp2, PS.rear() == rp2.rstrip('\n'), PS.resident_1001() == res2)
print('源稿接起来跟两段推出来的一字不差：主提示词', same[0], '后置词', same[1], '1001 常驻', same[2])
print('主提示词 %d → 第一段 %d → 第二段 %d 字；后置词 %d → %d 字；1001 常驻 %d 字' % (len(pipe_sp), len(sp1), len(sp2), len(pipe_rp), len(rp2), len(res2)))
for n, s in zip(names, secs):
    print('  ', n, len(s))
f0, f1 = PS.formats(pipe_sp), PS.formats(sp2)
gone = [f for f in f0 if f not in f1]
new = [f for f in f1 if f not in f0]
print('格式串 %d → %d 条；没了的 %d 条，新出现的 %d 条' % (len(f0), len(f1), len(gone), len(new)))
for f in gone:
    print('   -', f[:110], '｜在 1001 常驻里' if f in PS.formats(res2) else '')
for f in new:
    print('   +', f[:110])
