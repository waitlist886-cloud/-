# 补充条目文件的读法（build_rili.py 和 overlay_check.py 共用）。
# 一个文件里一段一条：先一行注释写设置，下面是正文，直到下一行注释或文件尾。
#   <!-- 条目 {"folder": "超维·51民生与蒸汽科技", "priority": 8101, "depth": 2, "user": "正则", "anchors": ["正则"], "black": ["正则"], "range": ["user"]} -->
#   <!-- 补丁 {"i": 1138, "op": "append"} -->        正文接在原卡第 1138 条末尾（空一行）
#   <!-- 补丁 {"i": 1127, "op": "houlines", "lines": [十行]} -->   长夜十候每一候末尾各添一行
# user：玩家的话里认的正则（不带斜杠）；anchors：上一条回复里按行认的正则（m 标志）；range 缺省 ["user"]，有 anchors 时自动加 assistant。
import json, re
HEAD = re.compile(r'^<!--\s*(条目|补丁)\s*(\{[\s\S]*?\})\s*-->[ \t]*$', re.M)
def parse(text):
    out, ms = [], list(HEAD.finditer(text))
    for n, m in enumerate(ms):
        body = text[m.end():ms[n + 1].start() if n + 1 < len(ms) else len(text)].strip('\n')
        cfg = json.loads(m.group(2))
        out.append((m.group(1), cfg, body.strip()))
    return out
def quant_count(k):
    s = re.sub(r'\\.', 'x', k); s = re.sub(r'\[[^\]]*\]', 'C', s)
    return len(re.findall(r'\{\d*,?\d*\}|[*+?]', s))
def star_height(k):
    i, best, contains, prev_close, prev_inner = 0, 0, [0], False, 0
    while i < len(k):
        c = k[i]
        if c == '\\': i += 2; prev_close = False; continue
        if c == '[':
            j = k.find(']', i + 2 if k[i + 1:i + 2] in ('^', ']') else i + 1); i = j + 1; prev_close = False; continue
        if c == '(':
            i += 3 if k[i:i + 3] in ('(?:', '(?!', '(?=') else 1; contains.append(0); prev_close = False; continue
        if c == ')':
            prev_inner = contains.pop(); prev_close = True; i += 1; continue
        m = re.match(r'\{\d*,?\d*\}', k[i:]) if c == '{' else None
        if c in '*+?' or m:
            d = 1 + (prev_inner if prev_close else 0); best = max(best, d); contains[-1] = max(contains[-1], d)
            i += m.end() if m else 1; prev_close = False; continue
        prev_close = False; i += 1
    return best
def regex_problems(k):
    p = []
    try: re.compile(k)
    except re.error as e: p.append('编译失败 %s' % e)
    if quant_count(k) > 22: p.append('量词 %d 个（日里上限 25，包一层以后会多两三个）' % quant_count(k))
    if star_height(k) > 1: p.append('量词套量词')
    if len(k) > 900: p.append('长度 %d' % len(k))
    return p
