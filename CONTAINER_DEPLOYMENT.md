# 容器化部署指南

本指南介绍如何将Aggregator项目容器化部署，支持多种容器注册表。

## 1. Docker镜像构建

### 1.1 本地构建
```bash
# 基础构建
docker build -t aggregator:latest .

# 使用国内镜像源加速构建（适用于中国大陆用户）
docker build --build-arg PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple" -t aggregator:latest .

# 构建多架构镜像
docker buildx build --platform linux/amd64,linux/arm64 -t aggregator:latest .
```

## 2. 容器注册表选项

### 2.1 GitHub Container Registry (GHCR.io) - 推荐
GitHub提供免费的私有和公共包存储。

#### 推送到GHCR
```bash
# 登录
echo $GITHUB_TOKEN | docker login ghcr.io -u 你的用户名

# 标记镜像
docker tag aggregator:latest ghcr.io/你的用户名/aggregator:latest

# 推送
docker push ghcr.io/你的用户名/aggregator:latest
```

### 2.2 Docker Hub
```bash
# 登录
docker login

# 标记镜像
docker tag aggregator:latest 你的用户名/aggregator:latest

# 推送
docker push 你的用户名/aggregator:latest
```

### 2.3 本地私有仓库
```bash
# 假设私有仓库地址为 myregistry.local:5000
docker tag aggregator:latest myregistry.local:5000/aggregator:latest
docker push myregistry.local:5000/aggregator:latest
```

## 3. Docker Compose部署

### 3.1 基础配置
```yaml
version: '3.8'

services:
  aggregator:
    image: aggregator:latest  # 或使用远程镜像
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

### 3.2 使用远程镜像的配置
```yaml
version: '3.8'

services:
  aggregator:
    image: ghcr.io/你的用户名/aggregator:latest  # 使用GHCR镜像
    # image: 你的用户名/aggregator:latest      # 使用Docker Hub镜像
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

## 4. 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| GIST_PAT | GitHub Personal Access Token | ghp_xxx |
| GIST_LINK | Gist ID，格式：username/gist_id | john/abc123 |
| CUSTOMIZE_LINK | 自定义机场列表URL | https://example.com/list |
| TZ | 时区 | Asia/Shanghai |

## 5. 插件系统配置

### 5.1 插件目录结构
容器内的插件目录映射：
- `/aggregator/plugins` - 插件文件
- `/aggregator/config` - 配置文件
- `/aggregator/plugin_manager` - 插件管理器

### 5.2 插件配置
通过挂载配置文件来管理插件：
```yaml
volumes:
  - ./config/plugin_config.json:/aggregator/config/plugin_config.json
```

## 6. 自动化部署

### 6.1 使用Watchtower自动更新
```yaml
version: '3.8'

services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 30 --cleanup
    restart: unless-stopped

  aggregator:
    image: ghcr.io/你的用户名/aggregator:latest
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
    depends_on:
      - watchtower
    command: [
      "python", 
      "-u", 
      "main_executor.py"
    ]
```

## 7. 监控和日志

### 7.1 查看容器日志
```bash
# 实时查看日志
docker logs -f aggregator

# 查看最近的日志
docker logs --tail 100 aggregator
```

### 7.2 进入容器调试
```bash
# 进入容器
docker exec -it aggregator bash

# 在容器内管理插件
python plugin_control.py list
python plugin_control.py status plugin_name
```

## 8. 备份和恢复

### 8.1 备份配置和数据
```bash
# 备份插件配置
docker cp aggregator:/aggregator/config ./backup/config

# 备份插件文件
docker cp aggregator:/aggregator/plugins ./backup/plugins
```

### 8.2 恢复配置和数据
```bash
# 重新创建容器时挂载备份的数据卷
docker run -d \
  --name aggregator \
  -v ./backup/config:/aggregator/config \
  -v ./backup/plugins:/aggregator/plugins \
  -v ./data:/aggregator/data \
  ghcr.io/你的用户名/aggregator:latest
```

## 9. 故障排除

### 9.1 镜像构建问题
- 确保Dockerfile语法正确
- 检查网络连接，必要时使用代理或国内镜像源
- 验证所有依赖文件存在

### 9.2 容器启动问题
- 检查环境变量是否正确设置
- 验证挂载的目录权限
- 查看容器日志定位问题

### 9.3 插件系统问题
- 确认`plugin_config.json`格式正确
- 检查插件文件路径和函数名
- 验证插件依赖是否安装

## 10. 安全最佳实践

- 使用非root用户运行容器
- 限制容器资源使用
- 定期更新基础镜像
- 使用秘密管理工具存储敏感信息
- 启用Docker安全扫描

通过以上指南，您可以选择最适合的容器注册表来部署Aggregator项目。