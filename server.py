#!/usr/bin/env python3
"""
简单的HTTP服务器，用于运行API Key用量查询网页
解决本地文件访问API时的CORS问题，并提供API代理功能
"""

import http.server
import socketserver
import os
import sys
import urllib.request
import urllib.error

PORT = 8003
API_URL = 'https://app.factory.ai/api/organization/members/chat-usage'

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 处理API代理请求
        if self.path.startswith('/api/proxy'):
            self.handle_api_proxy()
        else:
            # 处理静态文件请求
            super().do_GET()
    
    def handle_api_proxy(self):
        """处理API代理请求，转发到目标API服务器"""
        try:
            # 获取Authorization头
            auth_header = self.headers.get('Authorization')
            if not auth_header:
                self.send_error(400, 'Authorization header is required')
                return
            
            # 创建代理请求
            req = urllib.request.Request(API_URL)
            req.add_header('Authorization', auth_header)
            req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            # 发送请求并获取响应
            with urllib.request.urlopen(req) as response:
                # 读取响应内容
                content = response.read()
                content_type = response.getheader('Content-Type', 'application/json')
                
                # 发送响应
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
        
        except urllib.error.HTTPError as e:
            # 处理HTTP错误
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f'{{"error": "{e.reason}"}}'.encode())
        
        except Exception as e:
            # 处理其他错误
            self.send_error(500, f'Proxy error: {str(e)}')
    
    def end_headers(self):
        # 添加CORS头，允许所有来源
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, User-Agent, Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.end_headers()

def main():
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"服务器已启动，运行在 http://localhost:{PORT}")
            print("请在浏览器中访问以上地址来使用API Key用量查询工具")
            print(f"HTML文件路径: {os.path.join(script_dir, 'index.html')}")
            print(f"API代理地址: http://localhost:{PORT}/api/proxy")
            print("按 Ctrl+C 停止服务器")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()