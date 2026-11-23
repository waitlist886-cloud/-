# 命星页（star_page.py）导出和试用的小脚本。在仓库根上跑：
#   python -I -X utf8 底稿/状态栏/大框/第三轮/命星页_build.py [接好的规则.json]
# 出两样交给主会话的：第三轮/命星页_rules.json（这一份的九条规则，照 rules_frame.json 一条的格式）、第三轮/命星页.css。
# 带了第三个参数，再出一份接好的整套规则给复刻台用：照 make_rules_frame.py 原样跑一遍，只在「伟业·目标」前头插 RULES_UP、「能力」前头插 RULES_AB
# （字眼那一道 LW 包法、robust_rules 的补丁都照常走，跟主会话往 make_rules_frame.py 里添两行出来的是一个东西）。不动 make_rules_frame.py 和 rules_frame.json。
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FRAME = os.path.dirname(HERE)
sys.path.insert(0, FRAME)
import star_page

json.dump(star_page.rules(), open(os.path.join(HERE, '命星页_rules.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(HERE, '命星页.css'), 'w', encoding='utf-8', newline='\n').write(star_page.css())
print(len(star_page.RULES), '条规则', len(star_page.css()), '字样式')

if len(sys.argv) > 1:
    src = open(os.path.join(FRAME, 'make_rules_frame.py'), encoding='utf-8').read()
    for name, var in [('伟业·目标', 'RULES_UP'), ('能力', 'RULES_AB')]:
        key = "\nrule('%s'," % name
        assert src.count(key) == 1, name
        src = src.replace(key, "\nimport star_page as _SP\nfor _n, _rx, _rep in _SP.%s:\n    rule(_n, _rx, _rep)%s" % (var, key))
    argv, sys.argv = sys.argv, [os.path.join(FRAME, 'make_rules_frame.py'), sys.argv[1]]
    g = {'__name__': '__main__', '__file__': os.path.join(FRAME, 'make_rules_frame.py')}
    exec(compile(src, g['__file__'], 'exec'), g)
    sys.argv = argv
    R = g['R']
    names = [r['name'] for r in R]
    for n, _, _ in star_page.RULES:
        assert names.count(n) == 1, n
    # 平台的边界：量词不套量词、一条里不过二十五个（粗数：* + ? {m,n}，不数 (?: (?= (?! 里的问号）
    import re
    for r in R:
        if not r['name'].startswith('星页'):
            continue
        rx = r['regex']
        body = rx[1:rx.rindex('/')]
        re.compile(body.replace('ⓖ', 'G').replace('ⓙ', 'J'))   # Python 的写法跟 JS 差不多，能编过算一道粗检
        q = len(re.findall(r'(?<!\\)(?:\*|\+|\{\d+(?:,\d*)?\})|(?<![\\(])\?(?![:=!])', body))
        nest = re.search(r'[*+}]\)[*+{]', body)
        print('%-12s 量词 %2d%s  替换串 %d 字' % (r['name'], q, '  套了量词！' if nest else '', len(r['replaceString'])))
        assert q <= 25 and not nest, r['name']
    print('接好的规则', len(R), '条 →', sys.argv[1] if False else argv[1])
