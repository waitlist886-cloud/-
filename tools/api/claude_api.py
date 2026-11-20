#!/usr/bin/env python3
# 走用户自己的 Anthropic API 额度调 Claude（11-19）。密钥从环境变量 ANTHROPIC_API_KEY 取，
# 进程里没有就去 Windows 的用户环境变量（注册表 HKCU\Environment）里读：桌面 App 起的命令不带用户环境变量。
# 密钥从不打印、不写盘。只用标准库。
#   python -I -X utf8 tools/api/claude_api.py ping            发一句最小的请求，印回话和用量
#   from claude_api import ask; ask(提示词, system=..., model=..., max_tokens=...)  回 (文字, usage)
import json
import os
import sys
import urllib.request
import urllib.error

URL = 'https://api.anthropic.com/v1/messages'


def key():
    k = os.environ.get('ANTHROPIC_API_KEY')
    if not k and sys.platform == 'win32':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as h:
                k = winreg.QueryValueEx(h, 'ANTHROPIC_API_KEY')[0]
        except OSError:
            k = None
    if not k:
        raise SystemExit('没找到 ANTHROPIC_API_KEY')
    return k


def ask(prompt, system=None, model='claude-haiku-5-5', max_tokens=1024, timeout=600):
    body = {'model': model, 'max_tokens': max_tokens, 'messages': [{'role': 'user', 'content': prompt}]}
    if system:
        body['system'] = system
    req = urllib.request.Request(URL, data=json.dumps(body).encode('utf-8'), method='POST', headers={
        'x-api-key': key(), 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        raise SystemExit('API 回错 %s：%s' % (e.code, e.read().decode('utf-8', 'replace')[:600]))
    text = ''.join(b.get('text', '') for b in d.get('content', []) if b.get('type') == 'text')
    return text, d.get('usage', {})


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1:2] == ['ping']:
        t, u = ask('用一句话回答：你是哪个模型？', max_tokens=60)
        print('回话：', t)
        print('用量：', u)
