@echo off
REM Aggregator 项目快速部署脚本
REM 用于简化 Docker 部署流程

echo.
echo ==========================================
echo    Aggregator 项目快速部署助手
echo ==========================================
echo.

REM 检查是否安装了 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Docker，请先安装 Docker Desktop
    echo    下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ 检测到 Docker 已安装

REM 检查当前目录
if not exist "docker-compose.yml" (
    echo.
    echo 📝 未找到 docker-compose.yml 文件，正在创建...
    
    REM 创建 docker-compose.yml 文件
    echo version: '3.8' > docker-compose.yml
    echo. >> docker-compose.yml
    echo services: >> docker-compose.yml
    echo   aggregator: >> docker-compose.yml
    echo     image: ghcr.io/yuanzhou029/aggregatorv2.0:latest >> docker-compose.yml
    echo     container_name: aggregator >> docker-compose.yml
    echo     environment: >> docker-compose.yml
    echo       # 请替换为您的实际值 >> docker-compose.yml
    echo       - GIST_PAT=your_github_token_here >> docker-compose.yml
    echo       - GIST_LINK=your_username/your_gist_id_here >> docker-compose.yml
    echo       - CUSTOMIZE_LINK=your_customize_link_here >> docker-compose.yml
    echo       - TZ=Asia/Shanghai >> docker-compose.yml
    echo     volumes: >> docker-compose.yml
    echo       - ./data:/aggregator/data >> docker-compose.yml
    echo       - ./config:/aggregator/config >> docker-compose.yml
    echo       - ./plugins:/aggregator/plugins >> docker-compose.yml
    echo       - ./plugin_manager:/aggregator/plugin_manager >> docker-compose.yml
    echo     restart: unless-stopped >> docker-compose.yml
    echo     command: [ >> docker-compose.yml
    echo       "python", >> docker-compose.yml
    echo       "-u", >> docker-compose.yml
    echo       "main_executor.py" >> docker-compose.yml
    echo     ] >> docker-compose.yml
    
    echo ✅ docker-compose.yml 文件已创建
)

REM 检查并创建必要目录
if not exist "data" mkdir data
if not exist "config" mkdir config  
if not exist "plugins" mkdir plugins
if not exist "plugin_manager" mkdir plugin_manager

echo ✅ 必要目录已创建

echo.
echo 📋 部署步骤:
echo 1. 编辑 docker-compose.yml 文件，将占位符替换为您的实际值
echo 2. 运行 'docker-compose up -d' 启动服务
echo 3. 运行 'docker-compose logs -f' 查看日志
echo.

echo 🛠️  常用命令:
echo   启动服务:        docker-compose up -d
echo   查看日志:        docker-compose logs -f
echo   停止服务:        docker-compose down
echo   重启服务:        docker-compose restart
echo   查看状态:        docker-compose ps
echo.

echo 📝 docker-compose.yml 配置文件已准备就绪
echo    请按照以下说明编辑配置:
echo.
echo    GIST_PAT:       您的 GitHub Personal Access Token
echo    GIST_LINK:      您的 Gist ID (格式: 用户名/gist_id)
echo    CUSTOMIZE_LINK: 自定义链接 (可选)
echo.

echo 🚀 部署完成后，您可以:
echo   1. 进入容器: docker exec -it aggregator bash
echo   2. 管理插件: python plugin_control.py list
echo   3. 启用插件: python plugin_control.py enable plugin_name
echo.

pause