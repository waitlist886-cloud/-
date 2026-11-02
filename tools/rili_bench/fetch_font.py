# 复刻台用的思源宋体：从 Google Fonts 只下几个文本里用到的那几片（unicode-range 切片），写一份本地 @font-face。
# 用法：python3 -I -X utf8 fetch_font.py <输出目录> <文本文件1> [文本文件2 …]
# 产物：<输出目录>/font/*.woff2 和 <输出目录>/font_local.css，跑复刻台时 extracss= 带上它。字体文件不进仓库。
import os, re, subprocess, sys
out, files = sys.argv[1], sys.argv[2:]
os.makedirs(os.path.join(out, 'font'), exist_ok=True)
ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0 Safari/537.36'
css = subprocess.run(['curl', '-sS', '-m', '30', '-A', ua, 'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700&display=swap'],
                     check=True, capture_output=True, text=True).stdout
text = ''.join(open(f, encoding='utf-8').read() for f in files)
cps = set(ord(c) for c in text)
rows = []
for fc in re.findall(r'@font-face \{(.*?)\}', css, re.S):
    w = re.search(r'font-weight: (\d+)', fc).group(1)
    url = re.search(r'url\((.*?)\)', fc).group(1)
    ur = re.search(r'unicode-range: ([^;]+);', fc).group(1)
    rngs = []
    for part in ur.split(','):
        a, _, b = part.strip()[2:].partition('-')
        rngs.append((int(a, 16), int(b or a, 16)))
    if not any(a <= c <= b for c in cps for a, b in rngs):
        continue
    fn = os.path.join(out, 'font', '%s_%s' % (w, url.split('/')[-1]))
    if not os.path.exists(fn):
        subprocess.run(['curl', '-sS', '-m', '60', '-o', fn, url], check=True)
    rows.append("@font-face{font-family:'Noto Serif SC';font-style:normal;font-weight:%s;src:url('file://%s') format('woff2');unicode-range:%s}" % (w, os.path.abspath(fn), ur))
open(os.path.join(out, 'font_local.css'), 'w').write('\n'.join(rows))
print(len(rows), '片')
