@echo off
REM 本地运行脚本 (Windows)

echo 启动 Aggregator 本地开发环境...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

REM 检查npm是否安装
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到npm，请先安装npm
    pause
    exit /b 1
)

echo 正在安装Python依赖...
pip install -r requirements.txt

echo 正在安装前端依赖...
cd web
npm install
cd ..

echo.
echo 启动后端服务...
start "Aggregator Backend" cmd /k "python start_ui.py --mode dev"

echo.
echo 请在新终端窗口中运行以下命令启动前端开发服务器:
echo cd web && npm run dev
echo.
echo 前端将运行在 http://localhost:14047
echo 后端API将运行在 http://localhost:5000
echo.
echo 默认登录凭据: admin / admin123
echo.

pause