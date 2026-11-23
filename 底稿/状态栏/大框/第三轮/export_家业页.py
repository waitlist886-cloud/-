# 家业页这一份的导出（在仓库根上跑）：python -I -X utf8 底稿/状态栏/大框/第三轮/export_家业页.py [试用目录]
#   第三轮/家业页_rules.json   这一份的二十二条（甲、乙、丙三组连着排，插在哪见 estate_page.apply_rules 和备注）
#   第三轮/家业页.css          样式（图写 __ART__/pets.webp、__ART__/land_<纪>.webp）
# 给了试用目录的话另写两份复刻台用的：
#   <试用目录>/rules_合并.json   rules_frame.json 上打了 apply_rules 的整张表（复刻台只传这一份 extrarules）
#   <试用目录>/家业页_试.css     这一份的图换成 out/第三轮_家业页/ 下的本地地址（复刻台的 art= 只管一个目录，别的图照旧走它）
import json
import os
import sys
from urllib.request import pathname2url

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
FRAME = os.path.dirname(HERE)
ROOT = os.path.normpath(os.path.join(FRAME, '..', '..', '..'))
sys.path.insert(0, FRAME)
sys.stdout.reconfigure(encoding='utf-8')
import estate_page as EP  # noqa: E402

rs = EP.rules()
json.dump(rs, open(os.path.join(HERE, '家业页_rules.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
css = EP.css()
open(os.path.join(HERE, '家业页.css'), 'w', encoding='utf-8', newline='\n').write(css)
print('规则', len(rs), '条（甲 %d、乙 %d、丙 %d）' % (len(EP.RULES_A), len(EP.RULES_B), len(EP.RULES_C)), '样式', len(css), '字')
if len(sys.argv) > 1:
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    full = json.load(open(os.path.join(FRAME, 'rules_frame.json'), encoding='utf-8'))
    n = len(full)
    add, chg = EP.apply_rules(full)
    json.dump(full, open(os.path.join(out, 'rules_合并.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    art = os.path.join(ROOT, 'out', '第三轮_家业页', 'art')
    url = 'file:' + pathname2url(os.path.abspath(art))
    test = css
    for f in sorted(set(x.split('"')[0] for x in css.split('__ART__/')[1:])):
        if os.path.exists(os.path.join(art, f)):
            test = test.replace('__ART__/' + f, url + '/' + f)
        else:
            test = test.replace('url("__ART__/%s")' % f, EP.LAND if f.startswith('land_') else 'none')
            print('还没有图：', f)
    open(os.path.join(out, '家业页_试.css'), 'w', encoding='utf-8', newline='\n').write(test)
    print('合并：%d → %d 条（添 %d，改 %d）' % (n, len(full), add, chg))
