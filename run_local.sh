#!/bin/bash
# 本地运行脚本 (Linux/macOS)

echo "启动 Aggregator 本地开发环境..."
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "错误: 未找到npm，请先安装npm"
    exit 1
fi

echo "正在安装Python依赖..."
pip3 install -r requirements.txt

echo "正在安装前端依赖..."
cd web
npm install
cd ..

echo
echo "启动后端服务..."

# 在后台启动后端服务
python3 start_ui.py --mode dev &
BACKEND_PID=$!

echo
echo "请在新终端窗口中运行以下命令启动前端开发服务器:"
echo "cd web && npm run dev"
echo
echo "前端将运行在 http://localhost:14047"
echo "后端API将运行在 http://localhost:5000"
echo
echo "默认登录凭据: admin / admin123"
echo

# 提供停止服务的函数
cleanup() {
    echo
    echo "停止后端服务 (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
    echo "服务已停止"
}

# 注册信号处理器
trap cleanup EXIT INT TERM

# 等待用户输入停止
echo "按 Ctrl+C 停止服务"
wait $BACKEND_PID