# Aggregator 项目部署检查清单

## 部署前准备检查

### 1. 系统要求
- [ ] Docker Engine 19.03 或更高版本
- [ ] Docker Compose (推荐)
- [ ] 至少 2GB 可用磁盘空间
- [ ] 稳定的网络连接

### 2. GitHub 账户准备
- [ ] 拥有 GitHub 账户
- [ ] 已生成 GitHub Personal Access Token
  - [ ] Token 具有 `gist` 权限
  - [ ] Token 未过期
- [ ] 已创建 Gist 并获取 Gist ID
  - [ ] 格式正确：`用户名/gist_id`

### 3. 本地环境检查
- [ ] 已将项目推送到 GitHub 仓库
- [ ] GitHub Actions 工作流文件存在
  - [ ] `.github/workflows/docker.yml`
  - [ ] `.github/workflows/publish-docker.yml`
- [ ] Docker 镜像已成功构建

## Docker 部署检查

### 1. 镜像获取
- [ ] 已拉取镜像：`ghcr.io/yuanzhou029/aggregatorv2.0:latest`
- [ ] 镜像拉取成功，无错误信息

### 2. 配置文件准备
- [ ] 已创建 `docker-compose.yml` 文件
- [ ] 已创建以下目录：
  - [ ] `./data`
  - [ ] `./config`
  - [ ] `./plugins`
  - [ ] `./plugin_manager`

### 3. 环境变量配置
- [ ] `GIST_PAT` 已设置为有效的 GitHub Token
- [ ] `GIST_LINK` 已设置为正确的 Gist ID 格式
- [ ] `CUSTOMIZE_LINK` (可选) 已根据需要设置
- [ ] `TZ` 已设置为期望的时区

### 4. 服务启动
- [ ] 运行 `docker-compose up -d` 命令
- [ ] 服务启动无错误
- [ ] 容器正在运行 (`docker-compose ps`)

## 功能验证检查

### 1. 容器状态验证
- [ ] 容器状态为 "Up" 或 "Running"
- [ ] 无重启循环
- [ ] 日志中无严重错误

### 2. 插件系统验证
- [ ] 可以进入容器：`docker exec -it aggregator bash`
- [ ] 插件控制脚本可正常运行
  - [ ] `python plugin_control.py list` 显示插件列表
  - [ ] 插件配置文件存在：`config/plugin_config.json`

### 3. 功能测试
- [ ] 插件可以启用/禁用
- [ ] 插件可以手动运行
- [ ] 配置文件挂载正常
- [ ] 数据持久化正常

## 常见问题排查

### 1. 容器无法启动
- [ ] 检查环境变量是否正确设置
- [ ] 查看容器日志：`docker logs aggregator`
- [ ] 验证 GitHub Token 权限

### 2. 插件不执行
- [ ] 检查 `config/plugin_config.json` 中插件是否启用
- [ ] 验证插件文件路径和函数名
- [ ] 确认插件依赖已安装

### 3. GitHub 访问问题
- [ ] 确认 GIST_PAT 有效且有适当权限
- [ ] 验证 GIST_LINK 格式正确
- [ ] 检查网络连接是否正常

## 维护任务检查

### 1. 日志监控
- [ ] 可以查看实时日志：`docker-compose logs -f`
- [ ] 日志轮转配置正常

### 2. 数据备份
- [ ] 配置文件已持久化到本地
- [ ] 数据文件已持久化到本地
- [ ] 插件配置已保存

### 3. 更新流程
- [ ] 可以更新镜像：`docker-compose pull`
- [ ] 可以重新部署：`docker-compose up -d`
- [ ] 版本控制正常

## 部署完成确认

### 1. 服务状态
- [ ] 服务正常运行
- [ ] 插件系统正常工作
- [ ] 自动任务按计划执行

### 2. 功能验证
- [ ] 代理抓取功能正常
- [ ] 配置管理正常
- [ ] 存储后端正常

### 3. 安全检查
- [ ] 敏感信息未硬编码
- [ ] 访问权限适当
- [ ] 定期更新计划已制定

---

**部署完成时间：** ___________

**部署人员：** ___________

**备注：** 
_________________________________
_________________________________
_________________________________