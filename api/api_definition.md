"""
API接口定义用于前端UI与后端插件系统的交互
"""

# 插件管理API
- GET /api/plugins - 获取所有插件列表及状态
- GET /api/plugins/{plugin_name} - 获取特定插件信息
- POST /api/plugins/{plugin_name}/enable - 启用插件
- POST /api/plugins/{plugin_name}/disable - 禁用插件
- POST /api/plugins/{plugin_name}/start - 启动插件
- POST /api/plugins/{plugin_name}/stop - 停止插件
- POST /api/plugins/{plugin_name}/run - 立即执行插件
- PUT /api/plugins/{plugin_name} - 更新插件配置

# 配置管理API
- GET /api/config - 获取所有配置
- GET /api/config/plugin - 获取插件配置
- PUT /api/config/plugin - 更新插件配置
- GET /api/config/system - 获取系统配置
- PUT /api/config/system - 更新系统配置

# 系统状态API
- GET /api/status - 获取系统整体状态
- GET /api/logs - 获取系统日志
- GET /api/logs/{plugin_name} - 获取特定插件日志

# 实时通信API
- WebSocket /ws/status - 实时状态更新