# Aggregator Docker 部署完整指南

本指南将详细说明如何部署和运行 Aggregator 项目，特别针对 Docker 镜像的使用。

## 📋 目录
1. [准备工作](#准备工作)
2. [Docker 镜像获取](#docker-镜像获取)
3. [环境变量配置](#环境变量配置)
4. [运行方式](#运行方式)
5. [插件系统管理](#插件系统管理)
6. [常见问题](#常见问题)
7. [维护与监控](#维护与监控)

## 准备工作

### 1.1 系统要求
- Docker Engine 19.03 或更高版本
- Docker Compose（可选，推荐）
- 至少 2GB 可用磁盘空间
- 稳定的网络连接

### 1.2 准备必要信息
在开始部署前，您需要准备以下信息：

#### GitHub Token
- 用于访问 GitHub Gist 服务
- 权限要求：`gist` 权限
- 获取方式：
  1. 访问 GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. 点击 "Generate new token"
  3. 选择 `gist` 权限
  4. 复制生成的 token

#### Gist 信息
- 需要一个 GitHub Gist 的 ID
- 格式：`用户名/gist_id`
- 创建方式：
  1. 访问 https://gist.github.com/
  2. 创建一个新 Gist（可以是空的）
  3. 复制 URL 中的 ID 部分

---

## Docker 镜像获取

### 2.1 从 GitHub Container Registry 拉取（推荐）

```bash
# 拉取最新镜像
docker pull ghcr.io/yuanzhou029/aggregatorv2.0:latest

# 验证镜像是否拉取成功
docker images | grep aggregator
```

### 2.2 从本地构建镜像（可选）

```bash
# 如果您想使用本地构建的镜像
docker build -t aggregator:latest .
```

---

## 环境变量配置

### 3.1 必需环境变量

| 变量名 | 说明 | 示例值 | 备注 |
|--------|------|--------|------|
| `GIST_PAT` | GitHub Personal Access Token | `ghp_xxxxxxxxxxxxxx` | 必需，需要 gist 权限 |
| `GIST_LINK` | Gist ID | `username/abc123def456` | 必需，格式：用户名/gist_id |

### 3.2 可选环境变量

| 变量名 | 说明 | 示例值 | 备注 |
|--------|------|--------|------|
| `CUSTOMIZE_LINK` | 自定义机场列表 URL | `https://example.com/list` | 可选 |
| `TZ` | 时区 | `Asia/Shanghai` | 可选，默认 UTC |

---

## 运行方式

### 4.1 单容器运行（推荐）

#### 4.1.1 基础运行命令

```bash
# 创建必要的目录
mkdir -p ./aggregator/{data,config,plugins}

# 运行容器（请将示例值替换为您的实际值）
docker run -d \
  --name aggregator \
  --restart unless-stopped \
  -e GIST_PAT=your_github_token_here \
  -e GIST_LINK=your_username/your_gist_id_here \
  -e CUSTOMIZE_LINK=your_customize_link_here \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/aggregator/data:/aggregator/data \
  -v $(pwd)/aggregator/config:/aggregator/config \
  -v $(pwd)/aggregator/plugins:/aggregator/plugins \
  ghcr.io/yuanzhou029/aggregatorv2.0:latest
```

**⚠️ 重要：请将命令中的占位符替换为您的实际值**

#### 4.1.2 命令参数说明

| 参数 | 说明 | 备注 |
|------|------|------|
| `-d` | 后台运行容器 | 必需 |
| `--name aggregator` | 指定容器名称 | 可自定义 |
| `--restart unless-stopped` | 自动重启策略 | 推荐设置 |
| `-e VAR=value` | 设置环境变量 | 必需变量必须设置 |
| `-v host:container` | 挂载数据卷 | 用于数据持久化 |

### 4.2 使用 Docker Compose（推荐）

#### 4.2.1 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  aggregator:
    image: ghcr.io/yuanzhou029/aggregatorv2.0:latest
    container_name: aggregator
    environment:
      # 必需环境变量 - 请替换为您的实际值
      - GIST_PAT=your_github_token_here
      - GIST_LINK=your_username/your_gist_id_here
      # 可选环境变量
      - CUSTOMIZE_LINK=your_customize_link_here
      - TZ=Asia/Shanghai
    volumes:
      # 数据持久化挂载
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

#### 4.2.2 运行命令

```bash
# 创建必要的目录
mkdir -p ./data ./config ./plugins ./plugin_manager

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4.3 验证部署

```bash
# 检查容器是否正在运行
docker ps

# 查看容器日志
docker logs aggregator

# 进入容器检查
docker exec -it aggregator bash
```

---

## 插件系统管理

### 5.1 插件配置文件

插件配置文件位于：`./config/plugin_config.json`

### 5.2 插件控制命令

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

# 查看插件状态
python plugin_control.py status plugin_name
```

### 5.3 插件配置示例

```json
{
  "plugins": {
    "math_exercises": {
      "module_path": "plugins.exercises.math_exercises",
      "function_name": "crawl_math_exercises",
      "enabled": true,
      "cron_schedule": "0 2 * * *",
      "parameters": {
        "base_url": "https://example.com",
        "grade": "3",
        "subject": "math"
      },
      "timeout": 300,
      "max_retries": 3
    }
  }
}
```

---

## 常见问题

### 6.1 镜像拉取失败

**问题**：`Error response from daemon: pull access denied`
**解决方案**：
- 确认镜像名称正确
- 检查网络连接
- 尝试使用完整镜像名：`ghcr.io/yuanzhou029/aggregatorv2.0:latest`

### 6.2 容器无法启动

**问题**：容器启动后立即退出
**检查步骤**：
```bash
# 查看退出原因
docker logs aggregator

# 检查环境变量是否正确设置
docker inspect aggregator | grep -i env
```

### 6.3 GitHub Token 无效

**问题**：认证失败
**解决方案**：
- 确认 Token 具有 `gist` 权限
- 检查 Token 是否过期
- 验证环境变量设置是否正确

### 6.4 端口冲突

**问题**：容器无法绑定端口
**解决方案**：
- 检查是否有其他服务占用相同端口
- 该应用通常不需要暴露端口

---

## 维护与监控

### 7.1 日常维护

```bash
# 查看容器状态
docker ps

# 查看实时日志
docker logs -f aggregator

# 重启容器
docker restart aggregator

# 停止容器
docker stop aggregator

# 启动已停止的容器
docker start aggregator
```

### 7.2 数据备份

```bash
# 备份配置和数据
docker cp aggregator:/aggregator/config ./backup/config
docker cp aggregator:/aggregator/data ./backup/data
docker cp aggregator:/aggregator/plugins ./backup/plugins
```

### 7.3 镜像更新

```bash
# 拉取最新镜像
docker pull ghcr.io/yuanzhou029/aggregatorv2.0:latest

# 停止并删除旧容器
docker stop aggregator
docker rm aggregator

# 使用新镜像重新运行
# （使用前面的运行命令）
```

### 7.4 Docker Compose 维护

```bash
# 更新镜像并重新创建容器
docker-compose pull
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs

# 重新启动服务
docker-compose restart
```

---

## 故障排除

### 8.1 检查容器健康状态

```bash
# 检查容器是否正常运行
docker ps

# 检查容器详细信息
docker inspect aggregator

# 查看容器资源使用情况
docker stats aggregator
```

### 8.2 日志分析

```bash
# 查看最近100行日志
docker logs --tail 100 aggregator

# 查看特定时间后的日志
docker logs --since "2023-01-01T00:00:00" aggregator
```

### 8.3 进入容器调试

```bash
# 进入容器进行调试
docker exec -it aggregator bash

# 在容器内检查文件
ls -la /aggregator/
cat /aggregator/config/plugin_config.json
```

---

## 安全建议

1. **保护敏感信息**：
   - 不要在代码或配置文件中硬编码 GitHub Token
   - 使用环境变量或 Docker secrets

2. **定期更新**：
   - 定期更新 Docker 镜像
   - 更新 Docker Engine

3. **访问控制**：
   - 限制对容器的访问权限
   - 定期轮换 GitHub Token

---

## 支持与反馈

如遇到问题，请检查：
1. 确认所有必需的环境变量已正确设置
2. 确认网络连接正常
3. 检查容器日志获取详细错误信息
4. 验证 GitHub Token 权限

如果问题仍然存在，请提供以下信息以便诊断：
- Docker 版本信息：`docker --version`
- 容器日志：`docker logs aggregator`
- 系统信息：`docker info`