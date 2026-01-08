# GitHub部署和Docker自动构建发布完整指南

本文档详细介绍如何将Aggregator项目部署到GitHub并启用Docker自动构建发布功能。

## 1. 项目结构概览

在部署前，请确认项目包含以下关键组件：

### 1.1 核心功能模块
- **原始功能**：代理池构建、多源爬取、格式转换
- **新增功能**：精细化插件管理系统

### 1.2 插件系统组件
- `plugin_manager/` - 插件管理器
- `plugins/` - 插件目录结构
- `config/plugin_config.json` - 插件配置文件
- `plugin_control.py` - 插件控制脚本
- `main_executor.py` - 主执行器

### 1.3 Docker支持组件
- `Dockerfile` - Docker镜像构建文件
- `docker-compose.yml` - Docker Compose配置
- `.github/workflows/docker.yml` - 自动构建工作流
- `.github/workflows/publish-docker.yml` - 发布构建工作流

### 1.4 文档组件
- `README.md` - 主要文档
- `CONTAINER_DEPLOYMENT.md` - 容器化部署指南
- `DEPLOYMENT_GUIDE.md` - 部署指南
- `GITHUB_QUICK_START.md` - 快速入门指南

## 2. GitHub部署步骤

### 2.1 准备GitHub仓库
1. 登录GitHub账户
2. 点击"New repository"
3. 输入仓库名称（例如：aggregator）
4. 选择公开或私有
5. **不要**勾选"Initialize this repository with a README"
6. **不要**勾选"Add .gitignore"或"Choose a license"
7. 点击"Create repository"

### 2.2 本地Git配置
```bash
# 进入项目目录
cd d:\python项目文件\获取get_token\aggregator

# 初始化git仓库
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "feat: Add aggregator project with advanced plugin system and Docker support"
```

### 2.3 连接远程仓库
```bash
# 添加远程仓库（替换为你的仓库URL）
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 推送代码
git branch -M main
git push -u origin main
```

## 3. GitHub Actions自动构建

### 3.1 工作流配置验证
推送完成后，检查GitHub仓库：
1. 进入仓库页面
2. 点击"Actions"标签页
3. 应该能看到两个工作流：
   - "Build and Push Docker Image"
   - "Publish Docker image"

### 3.2 启用工作流
如果工作流未自动启用：
1. 在"Actions"页面
2. 点击"I understand my workflows, go ahead and enable them"
3. 点击"Enable all and run"

### 3.3 自动构建触发
- **推送构建**：推送到main分支时自动触发`docker.yml`
- **发布构建**：创建Release时自动触发`publish-docker.yml`

## 4. Docker镜像构建和发布

### 4.1 镜像仓库
构建的镜像将发布到GitHub Container Registry：
- 地址：`ghcr.io/你的用户名/你的仓库名`
- 支持的标签：latest、分支名、SHA、版本标签

### 4.2 多平台支持
- Linux AMD64
- Linux ARM64

### 4.3 镜像内容
Docker镜像包含：
- 完整的原项目功能
- 精细化插件管理系统
- 所有必需的依赖包
- 预配置的启动脚本

## 5. 使用构建的镜像

### 5.1 拉取镜像
```bash
# 登录到GitHub Container Registry（私有仓库需要）
echo $GITHUB_TOKEN | docker login ghcr.io -u 你的用户名 --password-stdin

# 拉取镜像
docker pull ghcr.io/你的用户名/你的仓库名:latest
```

### 5.2 运行容器
```bash
# 使用Docker运行
docker run -d \
  --name aggregator \
  --restart unless-stopped \
  -e GIST_PAT=你的GitHubToken \
  -e GIST_LINK=你的用户名/你的GistID \
  -e CUSTOMIZE_LINK=你的自定义链接 \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/data:/aggregator/data \
  -v $(pwd)/config:/aggregator/config \
  -v $(pwd)/plugins:/aggregator/plugins \
  ghcr.io/你的用户名/你的仓库名:latest
```

### 5.3 Docker Compose方式
```yaml
version: '3.8'

services:
  aggregator:
    image: ghcr.io/你的用户名/你的仓库名:latest
    container_name: aggregator
    environment:
      - GIST_PAT=${GIST_PAT:-}
      - GIST_LINK=${GIST_LINK:-}
      - CUSTOMIZE_LINK=${CUSTOMIZE_LINK:-}
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/aggregator/data
      - ./config:/aggregator/config
      - ./plugins:/aggregator/plugins
      - ./plugin_manager:/aggregator/plugin_manager
    restart: unless-stopped
    command: [
      "python", 
      "-u", 
      "main_executor.py"
    ]
```

## 6. 插件系统使用

### 6.1 插件管理
容器运行后，可以使用插件控制脚本：
```bash
# 进入容器
docker exec -it aggregator bash

# 查看所有插件状态
python plugin_control.py list

# 启用插件
python plugin_control.py enable plugin_name

# 禁用插件
python plugin_control.py disable plugin_name

# 运行插件
python plugin_control.py run plugin_name
```

### 6.2 配置管理
通过挂载`config/plugin_config.json`文件来管理插件配置：
```yaml
volumes:
  - ./config/plugin_config.json:/aggregator/config/plugin_config.json
```

## 7. 版本发布管理

### 7.1 创建版本发布
1. 在GitHub仓库页面点击"Releases"
2. 点击"Draft a new release"
3. 设置标签（如`v1.0.0`）
4. 设置发布标题
5. 添加发布说明
6. 点击"Publish release"

### 7.2 版本化镜像
每次发布都会生成带版本标签的Docker镜像：
- `ghcr.io/你的用户名/你的仓库名:v1.0.0`

## 8. 监控和维护

### 8.1 工作流监控
- 访问GitHub仓库的"Actions"标签页
- 查看构建日志和状态
- 监控构建成功率

### 8.2 镜像管理
- 访问"Package"页面管理Docker镜像
- 清理旧版本镜像
- 管理访问权限

### 8.3 容器监控
```bash
# 查看容器日志
docker logs -f aggregator

# 进入容器调试
docker exec -it aggregator bash
```

## 9. 安全最佳实践

### 9.1 访问控制
- 妥善保管GitHub Personal Access Token
- 使用专用的token用于Docker构建
- 定期轮换密钥

### 9.2 镜像安全
- 定期更新基础镜像
- 扫描镜像漏洞
- 使用最小化权限运行容器

### 9.3 仓库安全
- 启用两因素认证
- 限制仓库访问权限
- 定期审查协作者

## 10. 故障排除

### 10.1 工作流故障
- 检查工作流文件语法
- 验证权限设置
- 查看GitHub Actions日志

### 10.2 构建失败
- 检查Dockerfile语法
- 验证依赖包
- 查看构建日志

### 10.3 容器问题
- 检查环境变量
- 验证配置文件
- 查看容器日志

## 11. CI/CD流水线

```
代码提交 → GitHub Actions → Docker构建 → 镜像推送 → GHCR
    ↓
版本发布 → GitHub Actions → 版本化镜像 → 镜像推送 → GHCR
```

## 12. 扩展功能

### 12.1 自定义插件
- 在`plugins/`目录添加自定义插件
- 更新`config/plugin_config.json`
- 重新部署或热加载插件

### 12.2 自定义配置
- 挂载自定义配置文件
- 调整插件参数
- 管理启用/禁用状态

通过以上步骤，您已成功将项目部署到GitHub并启用了完整的Docker自动构建发布流程。项目现在具备：
- 自动化的CI/CD流程
- 完整的插件管理系统
- 多平台Docker镜像支持
- 灵活的配置管理
- 便捷的部署和维护能力