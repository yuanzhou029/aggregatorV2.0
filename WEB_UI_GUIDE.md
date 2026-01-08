# Web UI 使用指南

本文档介绍如何使用 Aggregator 的 Web 界面来管理插件和配置。

## 🚀 快速开始

### 1. 启动 Web UI

#### 默认凭据
首次访问系统时，使用以下默认凭据登录：
- **用户名**: admin
- **密码**: admin123

> ⚠️ 安全提醒：首次登录后请立即修改默认密码

#### Docker 部署（推荐）
```bash
# 使用 Docker Compose 启动（包含 Web UI）
docker-compose up -d
```

#### 本地启动
```bash
# 安装前端依赖并启动前端
cd web
npm install
npm run dev

# 在另一个终端启动后端 API
python start_ui.py --mode dev
```

### 2. 访问界面
- 前端界面：http://localhost:3000
- 后端 API：http://localhost:5000

## 📋 界面功能说明

### 仪表板 (Dashboard)
显示系统整体状态概览：
- 总插件数
- 活跃插件数
- 总执行次数
- 最近更新时间

### 插件管理 (Plugin Management)
管理所有插件的界面：

#### 功能特性
- **查看插件列表**：显示所有可用插件及其状态
- **启用/禁用插件**：通过开关按钮控制插件启用状态
- **立即运行插件**：手动触发插件执行
- **查看插件详情**：显示插件描述、定时配置等信息

#### 操作说明
1. **启用插件**：点击插件行中的开关按钮，绿色表示启用
2. **禁用插件**：再次点击开关按钮，灰色表示禁用
3. **运行插件**：点击"运行"按钮，立即执行插件
4. **刷新列表**：点击"刷新"按钮更新插件列表

### 配置管理 (Configuration Management)

#### 插件配置
- **JSON 编辑器**：可视化编辑插件配置
- **实时预览**：显示配置的 JSON 格式预览
- **保存配置**：将更改保存到配置文件

#### 系统配置
- **全局设置**：管理系统级配置选项
- **存储配置**：配置存储后端参数

## ⚙️ 配置说明

### 插件配置结构
```json
{
  "plugins": {
    "plugin_name": {
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

### 参数说明
- `module_path`：插件模块的 Python 导入路径
- `function_name`：插件执行函数的名称
- `enabled`：插件启用状态
- `cron_schedule`：定时执行配置（cron 表达式）
- `parameters`：传递给插件的参数字典
- `timeout`：插件执行超时时间（秒）
- `max_retries`：最大重试次数

## 🛠️ 高级功能

### 1. 批量操作
- 通过配置管理界面可以批量编辑多个插件配置
- 支持复制、粘贴配置片段

### 2. 配置备份
- 系统会自动备份配置文件
- 可以导出和导入配置

### 3. 实时监控
- 通过 WebSocket 实现实时状态更新
- 显示插件执行进度和结果

## 🔐 安全考虑

### 本地部署
- Web UI 默认只绑定到 localhost
- 仅在本地网络中可访问

### 生产部署
- 建议使用反向代理（如 nginx）添加认证
- 配置 HTTPS 加密传输

## 🐛 故障排除

### 常见问题
1. **无法访问前端**：
   - 检查端口 3000 是否被占用
   - 确认前端服务已启动

2. **API 连接失败**：
   - 检查后端服务是否运行
   - 确认端口 5000 可访问

3. **配置无法保存**：
   - 检查配置文件权限
   - 验证 JSON 格式是否正确

### 调试步骤
1. 检查浏览器控制台是否有错误
2. 查看后端 API 日志
3. 确认配置文件路径正确

## 📞 支持

如遇到问题，请查看：
- 项目文档
- GitHub Issues
- 社区讨论

---
> 注意：Web UI 仍在持续开发中，新功能将定期添加。