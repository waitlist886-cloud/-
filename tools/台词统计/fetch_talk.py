#!/usr/bin/env python3
"""补抓 BinOutput/Talk/Quest/<子任务>.json：给定主任务号，从 01 往后试，连续缺 8 个就停。
用法：python3 -I fetch_talk.py OUT_DIR 主任务号...
"""
import os, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
OUT = sys.argv[1]; mains = [int(x) for x in sys.argv[2:]]
os.makedirs(OUT, exist_ok=True)
BASE = 'https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/BinOutput/Talk/Quest/'
def get(n):
    p = os.path.join(OUT, f'{n}.json')
    if os.path.exists(p):
        return True
    try:
        with urllib.request.urlopen(BASE + f'{n}.json', timeout=60) as r:
            data = r.read()
        if data[:1] != b'{':
            return False
        open(p, 'wb').write(data)
        return True
    except urllib.error.HTTPError:
        return False
    except Exception:
        return False
def one(m):
    miss, got, n = 0, 0, 1
    while miss < 8 and n < 99:
        if get(m * 100 + n):
            got += 1; miss = 0
        else:
            miss += 1
        n += 1
    return m, got
with ThreadPoolExecutor(8) as ex:
    for m, got in ex.map(one, mains):
        print(m, got, flush=True)
