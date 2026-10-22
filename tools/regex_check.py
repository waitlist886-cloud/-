# 用法（在仓库根目录下）：python3 -I -X utf8 tools/regex_check.py 文件...
# 查每个文件：标题行、条目设置行一一对应，条目设置里的 `/…/` 都能编译，触发里带〔月银纪·正则〕、〔纷争纪·正则〕、〔山铜纪·正则〕、时段钥匙或日期格，文件夹号在 40 到 55 之间，量词照打包脚本查
import sys, re

# 量词检查照打包脚本 build_moon_v7.py 的 regex_problems：量词套量词、量词超过二十五个、命名组都报硬
def quant_count(k):
    s_ = re.sub(r'\\.', 'x', k); s_ = re.sub(r'\[[^\]]*\]', 'C', s_)
    s_ = s_.replace('(?:', '(').replace('(?!', '(').replace('(?=', '(').replace('(?<=', '(').replace('(?<!', '(')
    return len(re.findall(r'\{\d*,?\d*\}|[*+?]', s_))

def star_height(k):
    i, best, contains, prev_close, prev_inner = 0, 0, [0], False, 0
    while i < len(k):
        c = k[i]
        if c == '\\': i += 2; prev_close = False; continue
        if c == '[':
            j = k.find(']', i + 2 if k[i + 1:i + 2] in ('^', ']') else i + 1); i = j + 1; prev_close = False; continue
        if c == '(':
            if k[i:i + 4] in ('(?<=', '(?<!'): i += 4
            elif k[i:i + 3] in ('(?:', '(?!', '(?='): i += 3
            else: i += 1
            contains.append(0); prev_close = False; continue
        if c == ')':
            prev_inner = contains.pop(); prev_close = True; i += 1; continue
        m_ = re.match(r'\{\d*,?\d*\}', k[i:]) if c == '{' else None
        if c in '*+?' or m_:
            d_ = 1 + (prev_inner if prev_close else 0); best = max(best, d_); contains[-1] = max(contains[-1], d_)
            i += m_.end() if m_ else 1; prev_close = False; continue
        prev_close = False; i += 1
    return best

bad = 0
for f in sys.argv[1:]:
    s = open(f, encoding='utf-8').read()
    heads = re.findall(r'(?m)^## ((?:月银纪|纷争纪|山铜纪)·[^\n]+)$', s)
    sets = re.findall(r'(?m)^> 条目设置：(.+)$', s)
    print('%s：标题 %d 条，条目设置 %d 行' % (f, len(heads), len(sets)))
    if len(heads) != len(sets):
        bad += 1; print('  硬|标题和条目设置数目对不上')
    for h, ln in zip(heads, sets):
        m = re.match(r'文件夹 (\d\d)·(月银纪|纷争纪|山铜纪)｜([^，]+)，', ln)
        if not m:
            bad += 1; print('  硬|%s 文件夹格式不对' % h); continue
        if not (40 <= int(m.group(1)) <= 55) or m.group(2) != h[:3]:
            bad += 1; print('  硬|%s 文件夹 %s·%s 跟标题的纪对不上' % (h, m.group(1), m.group(2)))
        if '范围 用户与助手' not in ln or '深度 2' not in ln:
            bad += 1; print('  硬|%s 缺范围或深度' % h)
        if not re.search(r'触发（同时满足）(〔(?:月银纪|纷争纪|山铜纪)·正则〕|〔时段·[^〕]+·正则〕|`/\(\?:<br>)', ln):
            bad += 1; print('  硬|%s 触发没有纪的钥匙' % h)
        for rx in re.findall(r'`/(.+?)/`', ln):
            try:
                re.compile(rx)
            except re.error as e:
                bad += 1; print('  硬|%s 正则编译不过 %s：%s' % (h, rx[:40], e))
            if quant_count(rx) > 25:
                bad += 1; print('  硬|%s 量词 %d 个，超过二十五' % (h, quant_count(rx)))
            if star_height(rx) > 1:
                bad += 1; print('  硬|%s 量词套量词 %s' % (h, rx[:60]))
            if re.search(r'\(\?P?<[A-Za-z]', rx):
                bad += 1; print('  硬|%s 命名组' % h)
            for alt in rx.split('|'):
                core = re.sub(r'[()?:\[\]\\^$*+{}]', '', alt)
                if len(core) == 1:
                    print('  看|%s 触发里有单字 %s' % (h, alt))
print('硬问题合计', bad)
