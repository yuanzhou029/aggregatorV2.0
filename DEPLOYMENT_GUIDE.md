# GitHub部署和Docker自动构建发布指南

本文档详细说明如何将Aggregator项目推送到GitHub并使用GitHub Actions自动构建Docker镜像发布到GitHub Container Registry。

## 1. 项目准备

### 1.1 检查项目结构
确保项目包含以下关键文件和目录：
- `Dockerfile` - Docker镜像构建文件
- `.github/workflows/` - GitHub Actions工作流目录
- `requirements.txt` - Python依赖文件
- `README.md` - 项目说明文件
- 所有源代码文件

### 1.2 验证Dockerfile
确认Dockerfile可以成功构建镜像：
```bash
docker build -t test-aggregator .
```

## 2. 创建GitHub仓库

### 2.1 在GitHub上创建新仓库
1. 登录GitHub账户
2. 点击"New repository"
3. 输入仓库名称（例如：aggregator）
4. 选择公开或私有
5. 不要初始化README、.gitignore或license（我们已有这些文件）
6. 点击"Create repository"

### 2.2 获取仓库URL
复制新创建仓库的HTTPS或SSH URL。

## 3. 推送代码到GitHub

### 3.1 初始化本地Git仓库
```bash
cd d:\python项目文件\获取get_token\aggregator

# 初始化git仓库
git init

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: Add aggregator project with plugin system and Docker support"
```

### 3.2 连接到远程仓库
```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 推送代码
git branch -M main
git push -u origin main
```

## 4. GitHub Actions自动构建配置

### 4.1 工作流文件说明
项目已包含两个GitHub Actions工作流：

#### A. 自动构建工作流
- 文件：`.github/workflows/docker.yml`
- 触发条件：
  - 推送到main/master分支
  - Pull Request
- 功能：
  - 自动构建Docker镜像
  - 支持多平台（amd64, arm64）
  - 推送到GitHub Container Registry
  - 生成多种标签（分支、SHA、latest）

#### B. 发布构建工作流
- 文件：`.github/workflows/publish-docker.yml`
- 触发条件：
  - 创建新的GitHub Release
- 功能：
  - 构建带版本标签的Docker镜像
  - 推送到GitHub Container Registry

### 4.2 验证工作流配置
推送代码后，可以在GitHub仓库的Actions标签页查看工作流运行状态。

## 5. GitHub Container Registry (GHCR) 配置

### 5.1 镜像访问权限
GitHub Actions会自动使用`GITHUB_TOKEN`向GHCR推送镜像。

### 5.2 镜像命名规则
- 格式：`ghcr.io/你的用户名/仓库名:标签`
- 示例：`ghcr.io/username/aggregator:latest`

### 5.3 访问控制
- 对于公共仓库：镜像是公开的，任何人都可以拉取
- 对于私有仓库：镜像是私有的，只有你和协作者可以访问

## 6. 创建Release以构建版本化镜像

### 6.1 创建新Release
1. 在GitHub仓库页面点击"Releases"
2. 点击"Draft a new release"
3. 设置Tag版本（如v1.0.0）
4. 设置Release标题
5. 添加Release说明
6. 点击"Publish release"

### 6.2 Release触发的构建
创建Release后，`publish-docker.yml`工作流将被触发，构建带有版本标签的Docker镜像。

## 7. 使用构建的Docker镜像

### 7.1 拉取镜像
```bash
# 登录到GitHub Container Registry（如果是私有仓库）
echo $GITHUB_TOKEN | docker login ghcr.io -u 你的用户名 --password-stdin

# 拉取最新镜像
docker pull ghcr.io/你的用户名/你的仓库名:latest

# 拉取特定版本
docker pull ghcr.io/你的用户名/你的仓库名:v1.0.0
```

### 7.2 运行容器
```bash
# 使用Docker运行
docker run -d \
  --name aggregator \
  --restart unless-stopped \
  -e GIST_PAT=你的GitHubToken \
  -e GIST_LINK=你的用户名/你的GistID \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/data:/aggregator/data \
  -v $(pwd)/config:/aggregator/config \
  -v $(pwd)/plugins:/aggregator/plugins \
  ghcr.io/你的用户名/你的仓库名:latest
```

### 7.3 使用Docker Compose
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
    restart: unless-stopped
    command: ["python", "-u", "main_executor.py"]
```

## 8. 监控和管理

### 8.1 监控构建状态
- 访问GitHub仓库的Actions标签页
- 查看工作流运行历史和状态
- 检查构建日志以排查问题

### 8.2 管理Docker镜像
- 访问GitHub Packages页面查看发布的镜像
- 管理镜像版本和访问权限

## 9. 常见问题解决

### 9.1 工作流未运行
- 确认仓库包含`.github/workflows/`目录
- 检查工作流文件语法是否正确
- 验证推送的分支名称是否匹配工作流配置

### 9.2 镜像推送失败
- 确认仓库具有正确的访问权限
- 检查`GITHUB_TOKEN`权限设置
- 验证容器注册表配置

### 9.3 构建失败
- 查看GitHub Actions日志
- 检查Dockerfile语法
- 验证依赖项是否正确

## 10. 最佳实践

### 10.1 版本管理
- 使用语义化版本号（如v1.0.0）
- 为每个重要更新创建Release
- 保持latest标签指向稳定版本

### 10.2 安全考虑
- 定期更新基础镜像
- 使用最小化依赖
- 定期审查工作流权限

### 10.3 自动化测试
- 在构建前添加测试步骤
- 验证镜像功能
- 实施安全扫描

通过以上步骤，您可以成功将项目部署到GitHub并实现Docker镜像的自动构建和发布。