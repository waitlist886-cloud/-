# -*- coding: utf-8 -*-
"""重打四纪大框的两个压缩包（卡、分批导入），薄壳拷一份成 介绍页_薄壳_<版本>.html（11-18 写的）。
into_card.py、split_card.py 跑完以后跑它。原介绍页那一张是 make_four_era_card.py 打的，卡重打了才变，要一起重打加 --old。
  python -I -X utf8 底稿/门面/共用/zip_cards.py <版本，比如 11-18> [--old] [--dlc]
--dlc（11-24）：DLC/ 下 make_dlc.py 切出来的四包另打成 奥尔德兰_四纪大框_DLC.zip。不加照旧，跟以前一样。"""
import io, json, os, shutil, sys, zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..')).replace('\\', '/') + '/'
OUT = ROOT + 'out/发布卡_四纪大框/'
VER = ([a for a in sys.argv[1:] if not a.startswith('--')] or ['11-18'])[0]
THIN = ROOT + '底稿/门面/小样_外壳/thin.html'
thin = open(THIN, encoding='utf-8').read()
card = json.load(open(OUT + '奥尔德兰_四纪大框.json', encoding='utf-8'))
assert card['introPage'] == thin, '卡里的介绍页跟 小样_外壳/thin.html 不是同一份（先跑 make_thin.py 再跑 into_card.py）'
dst = OUT + '介绍页_薄壳_%s.html' % VER
shutil.copyfile(THIN, dst)
print('薄壳', os.path.basename(dst), os.path.getsize(dst), '字节')

with zipfile.ZipFile(OUT + '奥尔德兰_四纪大框.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write(OUT + '奥尔德兰_四纪大框.json', '奥尔德兰_四纪大框.json')
names = ['导入说明.md', '清单.json'] + sorted(n for n in os.listdir(OUT + '分批导入') if n.startswith('第') and n.endswith('.json'))
with zipfile.ZipFile(OUT + '奥尔德兰_四纪大框_分批导入.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for n in names:
        z.write(OUT + '分批导入/' + n, '分批导入/' + n)
done = ['奥尔德兰_四纪大框.zip', '奥尔德兰_四纪大框_分批导入.zip']
if '--old' in sys.argv:
    with zipfile.ZipFile(OUT + '奥尔德兰_四纪大框_原介绍页.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(OUT + '奥尔德兰_四纪大框_原介绍页.json', '奥尔德兰_四纪大框_原介绍页.json')
    done.append('奥尔德兰_四纪大框_原介绍页.zip')
if '--dlc' in sys.argv:
    # 11-24 起：into_card 以后跑了 底稿/DLC/tools/make_dlc.py（原地切）的，DLC/ 下四包、清单、说明另打一个包；卡里两张已经是本体
    dn = sorted(n for n in os.listdir(OUT + 'DLC') if n.endswith('.json') or n.endswith('.md'))
    assert any(n.startswith('奥尔德兰DLC_') for n in dn), 'DLC/ 下没有包，先跑 make_dlc.py'
    with zipfile.ZipFile(OUT + '奥尔德兰_四纪大框_DLC.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in dn:
            z.write(OUT + 'DLC/' + n, 'DLC/' + n)
    done.append('奥尔德兰_四纪大框_DLC.zip')
for n in done:
    z = zipfile.ZipFile(OUT + n)
    assert z.testzip() is None
    print(n, '%.1f MB' % (os.path.getsize(OUT + n) / 1048576), [i.filename for i in z.infolist()])
# 第 1 份的介绍页是不带退路的薄壳，提交号要跟卡里的一样
import re
p1 = json.load(open(OUT + '分批导入/第1份_骨架和底卡.json', encoding='utf-8'))
a = re.findall(r'gh/[^@]+@([0-9a-f]{10})', p1['introPage'])
b = re.findall(r'gh/[^@]+@([0-9a-f]{10})', thin)
print('第 1 份薄壳的提交号跟卡里一样', a == b, len(p1['introPage']), '字')
