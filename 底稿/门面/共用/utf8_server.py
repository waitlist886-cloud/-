#!/usr/bin/env python3
# 本地看书用的静态服务器（11-20）：跟 python -m http.server 一样，html、js、css、json 带上 charset=utf-8。
# 页面本身没写 <meta charset>（上平台时套壳给），内置浏览器不带字符集会按 Latin-1 解成乱码。
#   python -I 底稿/门面/共用/utf8_server.py [端口=8774]        根是 底稿/门面/
import functools
import http.server
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map, **{
        '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
        '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.md': 'text/plain; charset=utf-8'})

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8774
http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(H, directory=ROOT)).serve_forever()
