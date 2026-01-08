# Docker 一键安装部署指南

## 🚀 一键安装命令

使用以下命令快速部署 Aggregator 系统：

```bash
# 创建项目目录
mkdir aggregator && cd aggregator

# 创建环境变量文件
cat > .env << EOF
GIST_PAT=your_github_token_here
GIST_LINK=your_username/your_gist_id_here
CUSTOMIZE_LINK=
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$(echo -n "admin123" | sha256sum | cut -d' ' -f1)
TZ=Asia/Shanghai
EOF

# 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  aggregator-api:
    image: ghcr.io/yuanzhou029/aggregatorv2.0:latest
    container_name: aggregator
    environment:
      # 必需环境变量 - 请替换为您的实际值
      - GIST_PAT=${GIST_PAT}
      - GIST_LINK=${GIST_LINK}
      # 身份验证配置
      - ADMIN_USERNAME=${ADMIN_USERNAME}
      - ADMIN_PASSWORD_HASH=${ADMIN_PASSWORD_HASH}
      # 可选环境变量
      - CUSTOMIZE_LINK=${CUSTOMIZE_LINK}
      - TZ=${TZ}
    volumes:
      # 数据持久化挂载
      - ./data:/aggregator/data
      - ./config:/aggregator/config
      - ./plugins:/aggregator/plugins
      - ./plugin_manager:/aggregator/plugin_manager
    ports:
      - "5000:5000"  # API 端口
      - "14047:3000" # 前端UI端口
    restart: unless-stopped
    command: [
      "python", 
      "-u", 
      "start_ui.py",
      "--mode", 
      "prod"
    ]
EOF

# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

## 📋 配置说明

### 环境变量说明
- `GIST_PAT`: GitHub Personal Access Token (必需)
- `GIST_LINK`: GitHub Gist 链接 (必需) 格式: username/gist_id
- `ADMIN_USERNAME`: 管理员用户名 (默认: admin)
- `ADMIN_PASSWORD_HASH`: 管理员密码的SHA256哈希值
- `CUSTOMIZE_LINK`: 自定义机场列表URL (可选)
- `TZ`: 时区设置 (默认: Asia/Shanghai)

### 获取 GitHub Token
1. 访问 GitHub → Settings → Developer settings → Personal access tokens
2. 生成新 Token，选择 `gist` 权限
3. 复制生成的 Token

### 获取 Gist ID
1. 访问 https://gist.github.com/
2. 创建或选择一个 Gist
3. 复制 URL 中的 ID 部分

## 🚀 访问系统

安装完成后，您可以通过以下地址访问系统：

- **Web UI**: http://your-server-ip:14047
- **默认登录**: admin / admin123

> ⚠️ 安全提醒：首次登录后请立即修改默认密码

## 🔧 管理命令

```bash
# 查看服务日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新镜像
docker-compose pull && docker-compose up -d
```

## 🛠️ 故障排除

### 常见问题
1. **端口被占用**: 检查 14047 和 5000 端口是否被其他服务占用
2. **权限问题**: 确保 Docker 服务已启动并有足够权限
3. **网络问题**: 确保服务器可以访问外部网络

### 检查服务状态
```bash
# 检查容器状态
docker-compose ps

# 检查日志
docker-compose logs aggregator
```

## 📝 配置更新

系统支持通过UI面板更新配置，但需要在容器中持久化配置。您也可以直接修改 `.env` 文件来更新环境变量，然后重启服务：

```bash
docker-compose down
docker-compose up -d
```

---
> 提示：首次部署后，请务必修改默认登录凭据以确保系统安全。