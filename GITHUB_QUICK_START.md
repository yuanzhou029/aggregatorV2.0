# GitHub仓库快速入门指南

本指南将帮助您快速将Aggregator项目部署到GitHub，并启用Docker自动构建功能。

## 1. 前提条件

- GitHub账户
- Git客户端
- Docker（可选，用于本地测试）

## 2. 项目上传到GitHub

### 2.1 克隆或复制项目
```bash
# 如果项目不在GitHub上
cd d:\python项目文件\获取get_token\aggregator
```

### 2.2 初始化Git仓库
```bash
git init
git add .
git commit -m "feat: initial commit with aggregator project and plugin system"
```

### 2.3 创建GitHub仓库
1. 访问 [GitHub](https://github.com)
2. 点击右上角的"+"号，选择"New repository"
3. 输入仓库名称（如 `aggregator`）
4. 选择"Public"或"Private"
5. **不要**勾选"Initialize this repository with a README"
6. **不要**添加.gitignore或license（我们已有这些文件）
7. 点击"Create repository"

### 2.4 关联并推送代码
```bash
git remote add origin https://github.com/你的用户名/aggregator.git
git branch -M main
git push -u origin main
```

## 3. 验证GitHub Actions工作流

### 3.1 检查工作流文件
推送后，转到GitHub仓库页面：
1. 点击"Actions"标签
2. 应该能看到两个工作流：
   - "Build and Push Docker Image"
   - "Publish Docker image"

### 3.2 授权工作流运行
首次推送后，GitHub可能需要您授权工作流运行：
1. 在"Actions"标签页
2. 点击"I understand my workflows, go ahead and enable them"
3. 点击"Enable all and run"

## 4. 触发Docker镜像构建

### 4.1 自动构建
当您推送代码到main分支时，`docker.yml`工作流会自动触发：
- 构建Docker镜像
- 推送到GitHub Container Registry
- 镜像地址：`ghcr.io/你的用户名/aggregator`

### 4.2 创建Release触发版本构建
1. 在GitHub仓库页面点击"Releases"
2. 点击"Draft a new release"
3. 设置Tag（如 `v1.0.0`）
4. 设置标题（如 `Version 1.0.0`）
5. 添加描述
6. 点击"Publish release"

这将触发`publish-docker.yml`工作流，构建带版本标签的镜像。

## 5. 使用构建的镜像

### 5.1 查找镜像
构建成功后，镜像将在Packages中可用：
1. 在GitHub仓库页面点击"Package"
2. 或访问 `https://github.com/你的用户名/aggregator/pkgs/container/aggregator`

### 5.2 拉取镜像
```bash
# 登录（仅私有仓库需要）
echo $GITHUB_TOKEN | docker login ghcr.io -u 你的用户名 --password-stdin

# 拉取镜像
docker pull ghcr.io/你的用户名/aggregator:latest
```

### 5.3 运行容器
```bash
docker run -d \
  --name aggregator \
  --restart unless-stopped \
  -e GIST_PAT=你的GitHubToken \
  -e GIST_LINK=你的用户名/你的GistID \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/data:/aggregator/data \
  -v $(pwd)/config:/aggregator/config \
  -v $(pwd)/plugins:/aggregator/plugins \
  ghcr.io/你的用户名/aggregator:latest
```

## 6. 配置说明

### 6.1 必需的环境变量
- `GIST_PAT`: GitHub Personal Access Token（需要gist权限）
- `GIST_LINK`: Gist ID，格式为 `username/gist_id`

### 6.2 可选的环境变量
- `CUSTOMIZE_LINK`: 自定义机场列表URL
- `TZ`: 时区，默认为UTC，建议设置为 `Asia/Shanghai`

## 7. 插件系统管理

容器运行后，可通过以下命令管理插件：

```bash
# 进入容器
docker exec -it aggregator bash

# 查看插件状态
python plugin_control.py list

# 启用插件
python plugin_control.py enable plugin_name

# 禁用插件
python plugin_control.py disable plugin_name

# 运行插件
python plugin_control.py run plugin_name
```

## 8. 持续集成/持续部署 (CI/CD)

### 8.1 自动更新
每当您推送新代码到main分支时：
- 自动构建新版本Docker镜像
- 推送到GitHub Container Registry
- 更新`latest`标签

### 8.2 版本发布
每次创建新Release时：
- 构建带版本号的Docker镜像
- 如 `ghcr.io/你的用户名/aggregator:v1.0.0`

## 9. 故障排除

### 9.1 工作流未运行
- 检查仓库设置中的Actions权限
- 确认工作流文件语法正确
- 验证推送的分支名称

### 9.2 镜像构建失败
- 查看Actions日志
- 检查Dockerfile语法
- 验证依赖项

### 9.3 容器无法启动
- 检查环境变量
- 验证配置文件格式
- 查看容器日志

## 10. 安全注意事项

- 妥善保管GitHub Personal Access Token
- 定期更新依赖包
- 监控仓库活动
- 使用双因素认证

## 11. 后续步骤

1. 根据需要自定义`config/plugin_config.json`
2. 添加自定义插件到`plugins/`目录
3. 配置所需的环境变量
4. 监控GitHub Actions构建状态
5. 定期创建Release以生成版本化镜像

现在您已经成功将项目部署到GitHub并启用了Docker自动构建功能！