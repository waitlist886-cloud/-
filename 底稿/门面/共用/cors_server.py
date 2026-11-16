#!/usr/bin/env python3
# 本地验薄壳和沙箱里的样子用的静态服务器：跟 python -m http.server 一样，多给一个跨域头（图床上有这个头；沙箱里的页面取别处的东西要它）。
#   python -I 底稿/门面/共用/cors_server.py [端口=8773]        根是 底稿/门面/
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class H(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8773
    ThreadingHTTPServer(('127.0.0.1', port), partial(H, directory=ROOT)).serve_forever()
