"""
前端和后端服务启动脚本
"""
import os
import sys
import subprocess
import threading
import time
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
from pathlib import Path

def check_port(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def start_backend():
    """启动后端API服务"""
    try:
        from api.api_server import app
        print("启动后端API服务...")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except ImportError as e:
        print(f"导入后端服务失败: {e}")
        # 尝试直接运行API服务
        import subprocess
        subprocess.run([sys.executable, "api/api_server.py"])

def start_frontend():
    """启动前端开发服务器"""
    try:
        os.chdir('web')
        print("启动前端开发服务器...")
        subprocess.run(['npm', 'run', 'dev'], check=True)
    except Exception as e:
        print(f"启动前端失败: {e}")
        print("请确保已安装Node.js和npm，然后在web目录下运行: npm install && npm run dev")

def serve_frontend_dist():
    """使用Python内置服务器提供构建后的前端文件"""
    dist_path = Path('../frontend_dist')
    if dist_path.exists():
        os.chdir('../frontend_dist')
        print("启动前端静态文件服务器...")
        server = HTTPServer(('0.0.0.0', 14047), SimpleHTTPRequestHandler)  # 使用14047端口
        server.serve_forever()
    else:
        print("前端构建文件不存在，请先构建前端项目")

def build_frontend():
    """构建前端项目"""
    try:
        os.chdir('web')
        print("安装前端依赖...")
        subprocess.run(['npm', 'install'], check=True)
        print("构建前端项目...")
        subprocess.run(['npm', 'run', 'build'], check=True)
        print("前端构建完成")
    except Exception as e:
        print(f"构建前端失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='Aggregator UI 启动脚本')
    parser.add_argument('--mode', choices=['dev', 'prod'], default='dev', 
                       help='运行模式: dev(开发模式) 或 prod(生产模式)')
    parser.add_argument('--build', action='store_true', 
                       help='构建前端项目')
    
    args = parser.parse_args()
    
    if args.build:
        build_frontend()
        return
    
    if args.mode == 'prod':
        # 生产模式：构建前端并启动
        build_frontend()
        # 启动前端和后端服务
        backend_thread = threading.Thread(target=start_backend)
        frontend_thread = threading.Thread(target=serve_frontend_dist)
        
        backend_thread.start()
        time.sleep(2)  # 等待后端启动
        frontend_thread.start()
        
        try:
            backend_thread.join()
            frontend_thread.join()
        except KeyboardInterrupt:
            print("\n服务已停止")
    else:
        # 开发模式：启动开发服务器
        print("开发模式启动...")
        print("请确保已安装Node.js和npm")
        print("后端API服务将在 http://localhost:5000")
        print("前端开发服务器将在 http://localhost:3000")
        
        # 检查端口
        if not check_port(5000):
            print("警告: 端口5000已被占用")
        if not check_port(3000):
            print("警告: 端口3000已被占用")
        
        backend_thread = threading.Thread(target=start_backend)
        backend_thread.start()
        
        # 等待后端启动
        time.sleep(2)
        
        # 提示用户启动前端
        print("\n请在新终端中执行以下命令启动前端开发服务器:")
        print("cd web && npm install && npm run dev")
        print("\n或者直接访问 http://localhost:3000")
        print("\n默认登录凭据: admin / admin123 (请立即修改默认密码)")

if __name__ == '__main__':
    main()