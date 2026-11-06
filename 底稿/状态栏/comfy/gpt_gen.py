#!/usr/bin/env python3
# 用用户电脑上已登录 ChatGPT 的官方 Codex 出图（11-03，要 Plus，免费档没有出图工具）。不改用户的 Codex 配置，模型和推理档位写在命令里。
# Codex 看不到自己出的图，常回“没拿到图”，还会多画一张；图都在 ~/.codex/generated_images/<会话号>/，这里照日志里的会话号去取。
#   from gpt_gen import gen
#   gen('out/x/right', '提示词', refs=['构图.png', '人物.png'])   写 out/x/right.png，多的叫 right_2.png，回路径列表
#   python gpt_gen.py pick 日志 out/x/right                        只取图，不出图
# 一张一两分钟，用的是订阅的额度，同时只跑一张。
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
CODEX = sorted(glob.glob(os.path.expandvars(r'%LOCALAPPDATA%\OpenAI\Codex\bin\*\codex.exe')), key=os.path.getmtime)[-1:]
ONCE = (' Make exactly one image generation call and wait until that call has fully finished, which can take several minutes; do not end your turn while it is still running. '
        'Do not start a second call, even if the finished call shows no image, because the file is saved automatically. Then stop.')   # 只写“别重试”的话，它不等画完就退出
# 11-05：不写这一句，Codex 有时觉得参考图“只是画风参考”就不交给出图工具，出来是它自己的画风
ALL = ' Pass every one of the %d attached pictures to that image generation call as reference images (num_last_images_to_include: %d); do not leave any out.'


def pick(log, stem):
    """照日志里的会话号，把这一回出的图拷到 stem.png、stem_2.png。"""
    m = re.search(r'session id: ([0-9a-f-]+)', open(log, encoding='utf-8', errors='replace').read())
    if not m:
        raise RuntimeError('日志里没有会话号：' + log)
    folder = os.path.join(os.path.expanduser('~'), '.codex', 'generated_images', m.group(1))
    files = sorted(glob.glob(os.path.join(folder, '*.png')), key=os.path.getmtime)
    out = []
    for i, f in enumerate(files):
        dst = stem + ('.png' if i == 0 else '_%d.png' % (i + 1))
        shutil.copy(f, dst)
        out.append(dst)
    return out


def gen(stem, prompt, refs=(), model='gpt-6-luna', effort='low', timeout=900):
    if os.path.exists(stem + '.png'):
        return [stem + '.png']
    if not CODEX:
        raise RuntimeError('没找到 Codex')
    if len(refs) > 5:   # 工具的 num_last_images_to_include 是 1 到 5，传六张它一张也不出；数的是最后几张，排在前头的先丢
        raise ValueError('参考图最多五张')
    lost = [r for r in refs if not os.path.exists(r)]
    if lost:
        raise FileNotFoundError('参考图不在：' + '，'.join(lost))
    os.makedirs(os.path.dirname(os.path.abspath(stem)), exist_ok=True)
    log = stem + '.log'
    # 工作目录放在仓库外面的空文件夹，只读沙盒：11-03 放在仓库里跑过一回，Codex 自己往用户的 config.toml 写了 [projects.'e:\\aldran_art'] trust_level = "trusted"
    d = tempfile.mkdtemp(prefix='aldran_codex_')
    cmd = [CODEX[0], 'exec', '--skip-git-repo-check', '--sandbox', 'read-only', '-C', d, '-m', model, '-c', 'model_reasoning_effort="%s"' % effort]
    for r in refs:
        cmd += ['-i', os.path.abspath(r)]
    cmd += ['--', '$imagegen Use the built-in image generation tool. ' + prompt + (ALL % (len(refs), len(refs)) if refs else '') + ONCE]
    with open(log, 'w', encoding='utf-8') as f:
        rc = subprocess.call(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=timeout)
    shutil.rmtree(d, ignore_errors=True)
    out = pick(log, stem)
    if not out:
        raise RuntimeError('Codex 退出码 %s，没有出图，看 %s' % (rc, log))
    return out


if __name__ == '__main__' and sys.argv[1:2] == ['pick']:
    print(pick(sys.argv[2], sys.argv[3]))
