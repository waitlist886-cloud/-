# 11-23 主提示词重写第三段：四纪大框的主提示词、后置词、迷宫纪 1001 年的常驻有了自己的源稿，在 主提示词/ 下。
# make_four_era_card.py 最后一步套 apply：主提示词照 主提示词/NN_*.md 的次序原样接起来，后置词读 后置词.md，
# 1001 年的常驻读 常驻_迷宫纪1001年.md，四份四纪常驻补三句（prompt_stage2.residents）。
# 往后改四纪大框的主提示词，改 主提示词/ 下的文件。底本、four_era_prompt.SYS_EDITS、features_1110、fix_1112 里改主提示词的那些，
# 只到得了 1001 年切片和风月那一版，进不了四纪大框；流水线打出来的那一份变了，apply 会提醒一声（指纹对不上）。
# 源稿是怎么来的：tools/derive.py（流水线的主提示词过第一段 prompt_stage1.split、第二段 prompt_stage2.system）。
import copy
import hashlib
import json
import os
import re

import prompt_stage2 as S2
from prompt_stage1 import BLACK, CRED, ERA_1001, HEAD_1001, HEAD_PRE, check, wakes  # noqa: F401

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '主提示词')
REAR = '后置词.md'
RES = '常驻_迷宫纪1001年.md'
FINGER = '流水线指纹.json'


def _read(name):
    return open(os.path.join(SRC, name), encoding='utf-8', newline='').read().replace('\r\n', '\n')


def parts():
    return sorted(n for n in os.listdir(SRC) if re.match(r'^\d\d_.+\.md$', n))


def system():
    return ''.join(_read(n) for n in parts())


def rear():
    return _read(REAR).rstrip('\n')


def resident_1001():
    t = _read(RES)
    assert t.startswith(HEAD_1001 + '\n'), t[:40]
    return t


def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()[:16]


def formats(sp):
    """反引号里以 § 起头的格式串，显示正则逐字认它们"""
    return re.findall(r'`(§[^`\n]*)`', sp)


def apply(card, cases=None):
    pr = card['prompt']
    lb = pr['lorebook']
    pipe_sp, pipe_rp = pr['systemPrompt'], pr['rearPrompt']
    sp, rp, res = system(), rear(), resident_1001()
    # 格式串：流水线那一份有的，源稿里都得有（底座那一行的例子是有意换成通用写法的，例子进了 1001 常驻）
    f0, f1 = formats(pipe_sp), formats(sp) + formats(res)
    # 11-23 状态栏第三轮：命星页给 Art、Skill 两行末尾各添了一栏，源稿里那一行是“原来的整行＋｜新栏”，也算有
    lost = [f for f in f0 if f not in f1 and S2.BASE_OLD not in f and not any(g.startswith(f + '｜') for g in f1)]
    assert not lost, ('源稿里少了格式串', lost[:5])
    fp = os.path.join(SRC, FINGER)
    finger = json.load(open(fp, encoding='utf-8')) if os.path.exists(fp) else {}
    note = ''
    if finger and (finger.get('主提示词') != sha(pipe_sp) or finger.get('后置词') != sha(pipe_rp)):
        note = '提醒：流水线打出来的主提示词或后置词跟立源稿那一回不一样了（底本、SYS_EDITS、features_1110、fix_1112 有人改过），那些改动没有进四纪大框，要的话手改 主提示词/ 下的源稿，再跑 tools/derive.py --finger 记新指纹'
    pr['systemPrompt'], pr['rearPrompt'] = sp, rp
    added = S2.residents(lb)
    pre = [e for e in lb if (e.get('content') or '').startswith(HEAD_PRE + '\n')]
    assert len(pre) == 1 and not [e for e in lb if (e.get('content') or '').startswith(HEAD_1001)]
    e = copy.deepcopy(pre[0])
    e.update({'content': res, 'triggerWords': [ERA_1001, CRED], 'triggerWordsType': 'OR', 'blackListWords': list(BLACK), 'blackListWordsType': 'OR',
              'triggerRange': ['user', 'assistant'], 'impactRange': ['system'], 'scanDepth': 4, 'priority': pre[0]['priority'] + 1})
    assert not [x for x in lb if x.get('priority') == e['priority'] and x.get('folder') == e.get('folder')], '优先级撞了'
    lb.append(e)
    n, bad = check(card, cases) if cases is not None else (0, [])
    assert not bad, ('1001 常驻醒得不对', bad[:8])
    return {'主提示词': (len(pipe_sp), len(sp)), '后置词': (len(pipe_rp), len(rp)), '常驻1001': len(res), '四纪常驻添': added,
            '节': len(parts()), '核': n, '提醒': note, '流水线': (pipe_sp, pipe_rp)}
