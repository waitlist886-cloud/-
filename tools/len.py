# usage: python3 -I len.py < lines.txt   (prints length of each non-empty line)
import sys
for l in sys.stdin.read().split('\n'):
    if l.strip():
        print(len(l), l)
