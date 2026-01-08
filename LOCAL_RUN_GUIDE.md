# 本地运行指南

本文档介绍如何在本地环境中运行 Aggregator 系统。

## 📋 环境准备

### 1. 系统要求
- Python 3.8+
- Node.js 16+ 和 npm
- 确保端口 5000 和 14047 未被占用

### 2. 安装 Python 依赖
```bash
cd aggregator
pip install -r requirements.txt
```

### 3. 安装前端依赖
```bash
cd web
npm install
```

## 🔧 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# GitHub Personal Access Token (必需)
GIST_PAT=your_github_token_here

# GitHub Gist 信息 (必需) 格式: username/gist_id
GIST_LINK=your_username/your_gist_id_here

# 自定义机场列表URL地址 (可选)
CUSTOMIZE_LINK=

# 管理员用户名 (可选，默认为 admin)
ADMIN_USERNAME=admin

# 管理员密码的SHA256哈希值 (可选，默认为 admin123 的哈希)
# admin123 的 SHA256 哈希值为:
# 6ca13d52ca70c883e0f0bb101e425a89e8624de512b8c855c7b9203a1645b63b
ADMIN_PASSWORD_HASH=6ca13d52ca70c883e0f0bb101e425a89e8624de512b8c855c7b9203a1645b63b

# 时区设置 (可选，默认为 Asia/Shanghai)
TZ=Asia/Shanghai
```

## 🚀 本地运行方式

### 方式一：开发模式（推荐用于本地开发）

1. **启动后端服务**：
```bash
# 在项目根目录
python start_ui.py --mode dev
```

2. **启动前端开发服务器**：
```bash
# 在新的终端窗口中
cd web
npm run dev
```

3. **访问系统**：
- 前端：http://localhost:14047
- 后端API：http://localhost:5000

### 方式二：生产模式（构建后运行）

1. **构建前端项目**：
```bash
cd web
npm run build
```

2. **启动完整服务**：
```bash
# 在项目根目录
python start_ui.py --mode prod
```

3. **访问系统**：
- 前端：http://localhost:14047
- 后端API：http://localhost:5000

## 🔐 登录信息

- **用户名**: admin
- **密码**: admin123

> ⚠️ 安全提醒：首次登录后请立即修改默认密码

## 🛠️ 故障排除

### 常见问题

1. **端口被占用**：
   - 检查端口 5000 和 14047 是否被其他程序占用
   - 可使用 `netstat -an | grep [端口号]` 检查端口占用情况

2. **依赖安装失败**：
   - 确保网络连接正常
   - 尝试使用国内镜像源安装 Python 包：
     ```bash
     pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
     ```

3. **前端启动失败**：
   - 确保 Node.js 版本符合要求
   - 尝试清理缓存：
     ```bash
     cd web
     rm -rf node_modules package-lock.json
     npm install
     ```

### 检查服务状态

1. **检查后端服务**：
   ```bash
   curl http://localhost:5000/api/status
   ```

2. **检查前端服务**：
   - 打开浏览器访问 http://localhost:14047

## 📝 开发说明

### API 端点
- `GET /api/plugins` - 获取插件列表
- `POST /api/login` - 用户登录
- `GET /api/config/system` - 获取系统配置
- `PUT /api/config/system` - 更新系统配置

### 前端开发
- 使用 React + TypeScript + Ant Design
- API 请求通过代理转发到后端（开发模式）
- 所有配置都通过环境变量管理

## 🚀 部署到生产环境

完成本地测试后，可以使用以下命令构建 Docker 镜像：

```bash
# 构建镜像
docker build -t aggregator:latest .

# 运行容器
docker run -d \
  --name aggregator \
  -p 5000:5000 \
  -p 14047:14047 \
  -e GIST_PAT=your_token \
  -e GIST_LINK=your_username/your_gist_id \
  aggregator:latest
```

---
> 提示：本地开发时建议使用开发模式，可以享受热重载功能。