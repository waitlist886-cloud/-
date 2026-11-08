#!/usr/bin/env python3
# 用 Gemini API 出图（11-06，试 Nano Banana），接口跟 gpt_gen.gen 一样。key 只读环境变量 GEMINI_API_KEY，不写进仓库。图片模型没有免费档。
# 请求照 aistudio.google.com/docs/image-generation 的 interactions 写的。没有 key 的时候写的，头一回跑通以前算没验证。
#   from gemini_gen import gen
#   gen('out/x/sheet', '提示词', refs=['a.png', 'b.png'], ratio='3:2')    写 out/x/sheet.png，回路径列表
#   python gemini_gen.py sheet ariya [--model gemini-3-pro-image]          出这一位的设定图，写 out/立绘_试验_gemini/<模型>/<键>/
#   python gemini_gen.py pack ariya eleanor                                只写手动包（提示词和参考图），不调接口
import base64
import json
import os
import shutil
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
HERE = os.path.dirname(os.path.abspath(__file__))
URL = 'https://generativelanguage.googleapis.com/v1beta/interactions'
MODEL = 'gemini-nano-banana-2.1'
# 模板写的是透明底，Gemini 的文档里没有写透明底，这里换成纯白底，切图以前拿 cut_cpu.py（BiRefNet）抠
WHITE = 'A plain flat pure white background: no floor, no cast shadow, no gradient. '
TRANSPARENT = 'Transparent background: no floor, no cast shadow. '


def adapt(prompt):
    if TRANSPARENT not in prompt:
        raise ValueError('提示词里没有透明底那一句，模板改过了，这里跟着改')
    return prompt.replace(TRANSPARENT, WHITE)


def images_in(node):
    """响应里所有图的 base64。文档给了 output_image.data 和 steps[].content[] 两种写法，整棵树找一遍。"""
    out = []
    if isinstance(node, dict):
        if isinstance(node.get('data'), str) and (node.get('type') == 'image' or 'mime_type' in node or 'mimeType' in node):
            out.append(node['data'])
        for k, v in node.items():
            if k == 'output_image' and isinstance(v, dict) and isinstance(v.get('data'), str):
                out.append(v['data'])
            else:
                out += images_in(v)
    elif isinstance(node, list):
        for v in node:
            out += images_in(v)
    return list(dict.fromkeys(out))


def strip_data(node):
    """写日志用：把 base64 拿掉。"""
    if isinstance(node, dict):
        return {k: ('<%d 字>' % len(v) if k == 'data' and isinstance(v, str) else strip_data(v)) for k, v in node.items()}
    if isinstance(node, list):
        return [strip_data(v) for v in node]
    return node


def save(b64, path):
    raw = base64.b64decode(b64)
    if raw[:8] == b'\x89PNG\r\n\x1a\n':
        with open(path, 'wb') as f:
            f.write(raw)
        return
    import io
    from PIL import Image
    Image.open(io.BytesIO(raw)).convert('RGB').save(path)


def gen(stem, prompt, refs=(), model=MODEL, ratio='3:2', size='2K', timeout=600):
    if os.path.exists(stem + '.png'):
        return [stem + '.png']
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        raise RuntimeError('没有 GEMINI_API_KEY，这条路要用户在 Google AI Studio 开 key、设成环境变量')
    lost = [r for r in refs if not os.path.exists(r)]
    if lost:
        raise FileNotFoundError('参考图不在：' + '，'.join(lost))
    parts = [{'type': 'text', 'text': prompt}]
    for r in refs:
        with open(r, 'rb') as f:
            parts.append({'type': 'image', 'mime_type': 'image/png', 'data': base64.b64encode(f.read()).decode()})
    body = {'model': model, 'input': parts, 'response_format': {'type': 'image', 'aspect_ratio': ratio, 'image_size': size}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method='POST', headers={
        'Content-Type': 'application/json', 'x-goog-api-key': key, 'Api-Revision': '2026-05-20'})
    os.makedirs(os.path.dirname(os.path.abspath(stem)), exist_ok=True)
    log = stem + '.log'
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        text = e.read().decode('utf-8', 'replace')
        with open(log, 'w', encoding='utf-8') as f:
            f.write(text)
        raise RuntimeError('Gemini 回 %s：%s' % (e.code, text[:400]))
    with open(log, 'w', encoding='utf-8') as f:
        json.dump(strip_data(res), f, ensure_ascii=False, indent=1)
    got = images_in(res)
    if not got:
        raise RuntimeError('Gemini 没有出图，看 ' + log)
    out = []
    for i, b in enumerate(got):
        p = stem + ('.png' if i == 0 else '_%d.png' % (i + 1))
        save(b, p)
        out.append(p)
    return out


def sheet_job(k):
    import gpt_sheet as S
    p, refs = S.sheet_prompt(k)
    return adapt(p), refs


def pack(keys):
    root = os.path.join(HERE, 'out', '立绘_试验_gemini', '手动包')
    for k in keys:
        p, refs = sheet_job(k)
        d = os.path.join(root, k)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, '提示词.txt'), 'w', encoding='utf-8') as f:
            f.write(p + '\n')
        for i, r in enumerate(refs, 1):
            shutil.copy(r, os.path.join(d, '参考%d%s' % (i, os.path.splitext(r)[1])))
        print(k, '参考图', len(refs), '提示词', len(p), '字 ->', d)


if __name__ == '__main__':
    args = sys.argv[1:]
    model = MODEL
    if '--model' in args:
        i = args.index('--model')
        model = args[i + 1]
        del args[i:i + 2]
    if args[:1] == ['pack']:
        pack(args[1:])
    elif args[:1] == ['sheet']:
        for k in args[1:]:
            p, refs = sheet_job(k)
            print(gen(os.path.join(HERE, 'out', '立绘_试验_gemini', model, k, 'sheet'), p, refs=refs, model=model))
    else:
        sys.exit(__doc__ or '用法见文件头')
