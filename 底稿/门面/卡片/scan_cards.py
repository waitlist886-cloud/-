#!/usr/bin/env python3
# 卡片审稿用的粗筛（11-15）：python -I -X utf8 底稿/门面/卡片/scan_cards.py <纪> [--hooks]   （仓库根上跑）
# 照介绍页收尾方向稿第四之二节第7条那几样先过一遍机器：太短的台词、“我记一下”用在别人身上、卡面上出现不该点破的名字和字眼。
# 只是提醒，报出来的要人看：有的是这个人自己的名字、这一纪当时叫得出的事。--hooks 把这一纪每条主线的钩子列出来（一行一条，好一眼扫过去）。
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
han = lambda s: len(re.findall(r'[一-鿿]', s or ''))
# 不该从卡上露出来的名字和字眼：谁其实是谁、深层、只给 AI 的那几层
WORDS = ['薇瑟兰', '维拉瑟', '真容', '女相', '面甲底下', '凯尔萨斯', '陛下', '皇帝', '欧巴德斯', '塞维娅', '塔兰迦', '赝作', '厄洛伽', '执政', '若娜瓦', '伊斯塔露', '纳贝里士', '阿斯莫代',
         '其实是', '就是那个', '真名', '化名', '乔装', '扮成', '灰叶', '艾尔维娜', '黛洛', '涅芙拉', '勇者', '辛美尔', '止戈', '恩雅', '布伦塔赫', '赫莉昂黛', '苏薇', '龙名', '真龙', '持影',
         '凝名', '传奇', '圣座', '天灾', '撼世', '凡极', '死在', '死于', '战死', '没有回来', '没回来', '下葬', '遗', '最后一个', '最后一任', '往后', '后来', '日后', '将来', '终有一天']


def main():
    ji = sys.argv[1]
    hooks = '--hooks' in sys.argv
    n = 0
    for fp in sorted(glob.glob(os.path.join(ROOT, '底稿', '门面', '卡片', ji, '*.json'))):
        era = os.path.basename(fp)[:-5]
        C = json.load(open(fp, encoding='utf-8'))
        if hooks:
            for name, l in C.get('lines', {}).items():
                print('%s　%s　%s' % (era, name, l.get('hook') or '（空）'))
            continue
        for name, p in C.get('people', {}).items():
            line = p.get('line', '')
            if line and han(line) <= 4:
                print('%s %s 台词太短：%s' % (era, name, line)); n += 1
            body = ' '.join([p.get('bg', ''), p.get('meet', ''), p.get('hook', ''), line] + [s.get('name', '') + s.get('text', '') for s in p.get('stars', [])] + p.get('head', []) + p.get('tags', []) + p.get('traits', []))
            if '我记一下' in body and '巴尔缇娜' not in name:
                print('%s %s 用了“我记一下”' % (era, name)); n += 1
            hit = [w for w in WORDS if w in body and w not in name]
            if hit:
                print('%s %s：%s' % (era, name, '、'.join(hit))); n += 1
        for name, l in C.get('lines', {}).items():
            body = (l.get('hook') or '') + (l.get('open') or '')
            hit = [w for w in WORDS if w in body]
            if hit:
                print('%s 主线 %s：%s' % (era, name, '、'.join(hit))); n += 1
    if not hooks:
        print('合计 %d 条要看' % n)


if __name__ == '__main__':
    main()
