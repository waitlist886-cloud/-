# -*- coding: utf-8 -*-
"""帝国史补卷的专项扫查。用法（在仓库根目录下）：python3 -I -X utf8 tools/lint_salvis.py 萨尔维斯/补卷/帝国史_*.md
check_people_v7 管标点、禁词、冒号、「」引用；这里管这一卷自己的口径：
禁名和不进卡面的专名、中式口语和古文、旧地名、俗名在叙述里的次数、照X那一条的引用、条目设置的格式。"""
import sys, re, glob, os

HARD = {
    '禁名': ['厄洛伽', '四执政', '月相', '禁咒'],
    '真实世界': ['罗马', '元老院', '执政官', '护民官', '迦太基', '维斯塔', '十二表法', '凯撒', '恺撒'],
    '耐色瑞尔': ['耐色瑞尔', '秘法核心', '浮空城主', '奥术师', '魔网', '卡尔萨斯', '斐林'],
    '原神': ['雷穆利亚', '法图纳', '调律师', '灵露', '魔像', '乐章', '金蜂', '胎海', '水仙', '末日时钟', '谐律', '扶绥', '西比尔', '厄歌莉娅', '芙卡洛斯'],
    '旧地名': ['三川', '千塘'],
}
SOFT = ['爹', '娘', '爷爷', '奶奶', '外婆', '外公', '婆婆', '媳妇', '婆娘', '汉子', '后生', '娃', '闺女', '老汉', '大爷', '老爷', '少爷',
        '东家', '相公', '官人', '嫂子', '师兄', '师姐', '师弟', '师妹', '俺', '啥', '甭', '晌午', '咱', '吾', '汝', '尔等', '罢了', '何须',
        '矣', '焉', '哉', '此子', '岂', '何以', '灶', '龛', '长明灯', '仪轨', '会盟', '城主', '师门', '师父', '师傅', '徒弟', '剑客', '江湖',
        '武功', '内力', '真气', '侠客', '诸侯', '学塾', '驿卒', '官道', '佃户', '长衫', '袄', '庄子', '铺子', '伙计', '街坊', '米', '馒头',
        '包子', '饺子', '烧饼', '银子', '铜钱', '两银', '庙', '祠', '寺', '香火', '烧香', '磕头', '叩头', '作揖', '拱手', '衙门', '官府',
        '县', '秀才', '书生', '先生', '丫鬟', '小厮', '奴婢', '一炷香', '一盏茶', '更天', '担山', '登记', '盟主', '诏书', '遗诏', '奏报',
        '年号', '内侍', '宦官', '史馆', '簿', '族谱', '檄文', '羽书', '朕', '寡人', '陛下圣明', '万岁', '龙椅', '社稷', '天子', '宰相', '丞相',
        '尚书', '御史', '太子', '皇后娘娘', '娘娘', '公公', '太监', '宫女', '状元', '科举', '圣旨', '旨意', '钦差', '巡抚', '知府']
SOFT_KEEP = ['埃米利安', '塞普提米乌斯', '以后生', '米亚', '库米罗', '德米安', '米拉', '米娅', '卡米', '米尔', '米卡', '剑豪', '老伙计', '磨坊']
FOLK = ['浮空塔', '塔影', '月银', '炉心']  # 俗名：叙述里用正名，街上和史书里可以用
MOON_OK = ['月银纪', '月银学院', '月镜']

def page_titles(root):
    t = set()
    for f in glob.glob(os.path.join(root, '**/*.md'), recursive=True):
        if 'backup' in f or '交接存档' in f:
            continue
        for m in re.finditer(r'(?m)^## (月银纪·[^\n]+)$', open(f, encoding='utf-8').read()):
            t.add(m.group(1).strip())
    return t

root = '.'
titles = page_titles(root)
files = sys.argv[1:]
grand = 0
for f in files:
    s = open(f, encoding='utf-8').read()
    body = '\n'.join(ln for ln in s.split('\n') if not ln.startswith('>'))
    out = []
    hard = 0
    for k, ws in HARD.items():
        for w in ws:
            n = body.count(w)
            if n:
                hard += n; out.append('硬|%s %s×%d' % (k, w, n))
    b2 = body
    for k in SOFT_KEEP:
        b2 = b2.replace(k, '〇')
    for w in SOFT:
        for m in re.finditer(re.escape(w), b2):
            j = m.start()
            out.append('看|%s … %s' % (w, b2[max(0, j - 12):j + len(w) + 12].replace('\n', ' ')))
    b3 = body
    for k in MOON_OK:
        b3 = b3.replace(k, '〇')
    folk = {w: b3.count(w) for w in FOLK if b3.count(w)}
    if folk:
        out.append('俗名|' + ' '.join('%s×%d' % kv for kv in folk.items()))
    # 照X那一条：引用要指得到
    for m in re.finditer(r'(月银纪·[^｜\s，。]{1,8}｜[^\s，。、]+?)(?=那一条|那几条|那两条|那三条)', body):
        ref = m.group(1)
        if ref not in titles:
            hard += 1; out.append('硬|引用指不到 ' + ref)
    # 他指神
    for m in re.finditer(r'(神|神明|七十二位|朱亚|弥尔瓦)[^。]{0,14}他', body):
        out.append('看|神的代词 … ' + body[m.start():m.end() + 6].replace('\n', ' '))
    # 条目设置
    sets = [ln for ln in s.split('\n') if ln.startswith('> 条目设置')]
    if len(sets) != 1:
        hard += 1; out.append('硬|条目设置行数 %d' % len(sets))
    for ln in sets:
        need = ['文件夹 52·月银纪｜帝国史', '触发（同时满足）〔月银纪·正则〕', '范围 用户与助手', '深度 2', '黑名单 `/']
        for x in need:
            if x not in ln:
                hard += 1; out.append('硬|条目设置缺 ' + x)
        for m in re.finditer(r'`/(.+?)/`', ln):
            try:
                re.compile(m.group(1))
            except re.error as e:
                hard += 1; out.append('硬|正则不合法 %s' % e)
    heads = re.findall(r'(?m)^## (.+)$', s)
    if not heads or not heads[0].startswith('月银纪·帝国史｜'):
        hard += 1; out.append('硬|标题 ' + (heads[0] if heads else '无'))
    if '### 裁定锁' not in s:
        hard += 1; out.append('硬|缺裁定锁')
    if '【调用】' not in s:
        hard += 1; out.append('硬|缺【调用】')
    for lab in ['- 是什么：', '- 写法：']:
        if lab not in s:
            out.append('看|缺 ' + lab)
    han = len(re.findall(r'[一-鿿]', body))
    grand += hard
    print('==', os.path.basename(f), '| 汉字', han, '| 硬', hard)
    for o in out:
        print('   ', o)
print('硬问题合计', grand)
