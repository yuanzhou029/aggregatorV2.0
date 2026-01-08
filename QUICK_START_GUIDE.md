# Aggregator 项目 - 完整部署指南

## 项目概述

Aggregator 是一个强大的免费代理池构建工具，通过爬取多个平台/网页的代理资源，自动验证、聚合并转换为各种客户端所需格式。项目新增了精细化插件管理系统，可精确控制每个插件的启用/禁用和定时执行。

### 核心特性
- **🕷️ 多源爬取** - Telegram、GitHub、Google、Yandex、Twitter 等
- **🔍 智能验证** - 自动检测代理活性和质量
- **🔄 格式转换** - 支持 Clash、V2Ray、SingBox 等格式
- **💾 灵活存储** - GitHub Gist、PasteGG、Imperial 等多种后端
- **🔌 插件系统** - 可扩展的自定义爬取架构
- **⚡ 高效处理** - 多线程并发，批量处理
- **⚙️ 精细化管理** - 精确控制每个插件的启用/禁用和定时执行
- **🐳 容器化部署** - 支持Docker及自动构建发布

## 部署准备

### 1. 系统要求
- Docker Engine 19.03 或更高版本
- Docker Compose (推荐)
- 至少 2GB 可用磁盘空间

### 2. GitHub 准备
- GitHub 账户
- GitHub Personal Access Token（需要 `gist` 权限）
- GitHub Gist ID（格式：用户名/gist_id）

## Docker 部署

### 1. 拉取镜像

```bash
docker pull ghcr.io/yuanzhou029/aggregatorv2.0:latest
```

### 2. 创建配置文件

创建 `docker-compose.yml` 文件：

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

### 3. 创建必要目录

```bash
mkdir -p ./data ./config ./plugins ./plugin_manager
```

### 4. 启动服务

```bash
docker-compose up -d
```

### 5. 验证部署

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 检查容器
docker exec -it aggregator bash
```

## 插件系统管理

### 1. 插件控制命令

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

### 2. 插件配置

插件配置文件位于 `./config/plugin_config.json`：

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

### 3. 自定义插件开发

#### 3.1 创建自定义插件

在 `./plugins/custom_plugins/` 目录下创建新的插件文件：

```python
# plugins/custom_plugins/my_custom_plugin.py
import sys
import os
import requests
from urllib.parse import urljoin
import time

# 添加项目路径到Python环境
sys.path.append('/aggregator')

from subscribe.logger import logger


def my_custom_function(params: dict):
    """
    自定义插件函数
    
    Args:
        params: 插件参数字典
        
    Returns:
        插件执行结果，通常是一个列表，包含要处理的数据
    """
    # 记录插件开始执行
    logger.info(f"[MyCustomPlugin] 开始执行自定义插件，参数: {params}")
    
    # 从参数中获取配置
    base_url = params.get("base_url", "https://example.com")
    timeout = params.get("timeout", 30)
    
    try:
        # 执行自定义逻辑
        response = requests.get(base_url, timeout=timeout)
        response.raise_for_status()
        
        # 处理响应数据
        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        
        # 构造返回结果
        result = {
            "status": "success",
            "message": "自定义插件执行成功",
            "timestamp": int(time.time()),
            "data": data,
            "params": params
        }
        
        logger.info(f"[MyCustomPlugin] 插件执行完成，结果: {result}")
        return result
        
    except requests.exceptions.RequestException as e:
        error_result = {
            "status": "error",
            "message": f"请求失败: {str(e)}",
            "timestamp": int(time.time()),
            "params": params
        }
        logger.error(f"[MyCustomPlugin] 插件执行失败: {error_result}")
        return error_result
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"插件执行异常: {str(e)}",
            "timestamp": int(time.time()),
            "params": params
        }
        logger.error(f"[MyCustomPlugin] 插件执行异常: {error_result}")
        return error_result
```

#### 3.2 配置自定义插件

在 `./config/plugin_config.json` 中添加新插件配置：

```json
{
  "plugins": {
    "my_custom_plugin": {
      "module_path": "plugins.custom_plugins.my_custom_plugin",
      "function_name": "my_custom_function",
      "enabled": false,
      "cron_schedule": "0 4 * * *",
      "parameters": {
        "base_url": "https://api.example.com/data",
        "timeout": 30
      },
      "timeout": 300,
      "max_retries": 3
    }
  }
}
```

#### 3.3 插件开发最佳实践

**插件函数要求：**
- 函数必须接受一个 `params: dict` 参数
- 函数必须返回一个结果（通常是字典或列表）
- 使用项目提供的 `logger` 记录日志
- 处理异常情况并返回适当的错误信息

**配置参数说明：**
- `module_path`: 插件模块的Python导入路径
- `function_name`: 插件执行函数的名称
- `enabled`: 布尔值，true为启用，false为禁用
- `cron_schedule`: 定时执行配置（cron表达式格式）
- `parameters`: 传递给插件的参数字典
- `timeout`: 插件执行超时时间（秒）
- `max_retries`: 最大重试次数

#### 3.4 快速开始插件开发

参考 `PLUGIN_QUICK_START.md` 文件，其中包含了：
- Hello World 插件示例
- 常用插件模板
- 配置参数详解
- 常用cron表达式
- 调试技巧

## 维护命令

```bash
# 查看实时日志
docker logs -f aggregator

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新镜像
docker-compose pull
docker-compose up -d

# 进入容器
docker exec -it aggregator bash
```

## 故障排除

### 1. 容器无法启动
- 检查环境变量是否正确设置
- 查看日志：`docker logs aggregator`
- 验证 GitHub Token 权限

### 2. 插件不执行
- 检查 `config/plugin_config.json` 中插件是否启用
- 验证插件文件路径和函数名
- 确认插件依赖已安装

### 3. GitHub 访问问题
- 确认 GIST_PAT 有效且有适当权限
- 验证 GIST_LINK 格式正确
- 检查网络连接是否正常

## 快速部署脚本

我们提供了一个 Windows 批处理脚本，可自动创建配置文件：

1. 运行 `quick_deploy.bat`
2. 按照提示操作
3. 编辑生成的 `docker-compose.yml` 文件
4. 启动服务

## 检查清单

部署完成后，请使用 `DEPLOYMENT_CHECKLIST.md` 确保所有配置正确。

## 详细文档

- `PLUGIN_DEVELOPMENT_GUIDE.md` - 详细的插件开发指南
- `PLUGIN_QUICK_START.md` - 插件开发快速入门指南
- `plugin_config_template.json` - 插件配置模板
- `DOCKER_DEPLOYMENT_GUIDE.md` - 详细的Docker部署指南

## 支持

如遇问题，请：
1. 检查容器日志：`docker logs aggregator`
2. 确认环境变量设置正确
3. 验证 GitHub Token 权限
4. 查看 `DOCKER_DEPLOYMENT_GUIDE.md` 获取详细说明

---

**项目已成功部署！现在您可以享受精细化插件管理系统带来的便利，精确控制每个插件的启用/禁用和定时执行。**