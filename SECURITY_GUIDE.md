# 安全配置指南

本文档介绍如何为 Aggregator 系统配置安全措施，特别是身份验证功能。

## 🛡️ 默认安全设置

系统默认使用以下凭据：
- **用户名**: admin
- **密码**: admin123

> ⚠️ 重要提醒：首次部署后请立即修改默认密码！

## 🔐 配置身份验证

### 1. 环境变量配置

在 `.env` 文件中设置以下变量：

```bash
# 身份验证配置
ADMIN_USERNAME=your_username
ADMIN_PASSWORD_HASH=your_password_sha256_hash
```

### 2. 生成密码哈希

您可以使用以下 Python 代码生成密码的 SHA256 哈希值：

```python
import hashlib

password = "your_password"
password_hash = hashlib.sha256(password.encode()).hexdigest()
print(f"Password hash: {password_hash}")
```

或者使用命令行：

```bash
echo -n "your_password" | sha256sum
```

### 3. Docker 部署安全配置

在 docker-compose.yml 中配置环境变量：

```yaml
environment:
  - ADMIN_USERNAME=your_username
  - ADMIN_PASSWORD_HASH=your_password_hash
```

## 🚪 访问控制

### 登录要求
- 所有 API 端点都需要身份验证
- 未认证用户将被重定向到登录页面
- 会话超时时间为 1 小时

### 登录凭据
- 用户名和密码区分大小写
- 登录失败会返回通用错误消息，防止用户枚举

## 🔐 安全最佳实践

### 1. 密码策略
- 使用强密码（至少8位，包含大小写字母、数字和特殊字符）
- 定期更换密码
- 不要在多个系统中重复使用相同密码

### 2. 网络安全
- 通过 HTTPS 访问管理界面
- 在生产环境中使用反向代理（如 nginx）添加额外的安全层
- 限制对管理界面的 IP 访问

### 3. 会话管理
- 系统会自动清理过期会话
- 用户登出后会立即失效会话令牌
- 会话令牌使用安全的随机生成算法

## 🚨 安全注意事项

### 1. 部署前检查清单
- [ ] 更改默认用户名和密码
- [ ] 配置 SSL/TLS 证书
- [ ] 限制对管理界面的网络访问
- [ ] 设置防火墙规则

### 2. 监控和日志
- 定期检查登录尝试日志
- 监控异常访问模式
- 记录所有配置更改

## 🛠️ 故障排除

### 忘记管理员密码
如果忘记管理员密码，可以通过以下方式重置：
1. 修改环境变量中的 `ADMIN_PASSWORD_HASH`
2. 重启服务
3. 使用新凭据登录

### 会话问题
如果遇到会话相关问题：
1. 清除浏览器缓存和 Cookie
2. 检查系统时间是否正确
3. 确认服务正常运行

---

> 提示：安全是一个持续的过程，请定期审查和更新安全配置。