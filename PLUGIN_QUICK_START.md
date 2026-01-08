# Aggregator 插件开发快速入门指南

## 1. 开发环境准备

### 1.1 确认插件系统已部署
- Docker容器正在运行
- 插件管理器已加载
- 配置文件路径正确

### 1.2 插件开发目录
```
plugins/
├── custom_plugins/     # 自定义插件目录
│   ├── __init__.py
│   └── your_plugin.py  # 您的插件文件
```

## 2. 创建第一个插件

### 2.1 创建插件文件
在 `plugins/custom_plugins/` 目录下创建 `hello_world.py`：

```python
# plugins/custom_plugins/hello_world.py
import sys
import time

# 添加项目路径
sys.path.append('/aggregator')

from subscribe.logger import logger


def hello_world_plugin(params: dict):
    """
    Hello World 插件示例
    """
    logger.info("[HelloWorldPlugin] 开始执行Hello World插件")
    
    # 获取参数
    name = params.get('name', 'World')
    greeting = params.get('greeting', 'Hello')
    
    # 执行逻辑
    message = f"{greeting}, {name}! 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    result = {
        "status": "success",
        "message": message,
        "timestamp": int(time.time())
    }
    
    logger.info(f"[HelloWorldPlugin] 执行完成: {message}")
    return result
```

### 2.2 配置插件
创建或编辑 `config/plugin_config.json`：

```json
{
  "plugins": {
    "hello_world": {
      "module_path": "plugins.custom_plugins.hello_world",
      "function_name": "hello_world_plugin",
      "enabled": false,
      "cron_schedule": "*/5 * * * *",
      "parameters": {
        "name": "Aggregator User",
        "greeting": "Welcome"
      },
      "timeout": 30,
      "max_retries": 1
    }
  }
}
```

## 3. 测试插件

### 3.1 进入容器
```bash
docker exec -it aggregator bash
```

### 3.2 测试插件
```bash
# 运行插件
python plugin_control.py run hello_world

# 查看结果
# 应该看到类似输出：
# 插件 'hello_world' 执行成功，结果: {"status": "success", "message": "Welcome, Aggregator User! 当前时间: 2023-01-01 12:00:00", "timestamp": 1234567890}
```

### 3.3 启用插件
```bash
# 启用插件
python plugin_control.py enable hello_world

# 查看状态
python plugin_control.py status hello_world
```

## 4. 常用插件模板

### 4.1 网络请求插件模板
```python
def web_request_plugin(params: dict):
    import requests
    from subscribe.logger import logger
    
    url = params.get('url', '')
    headers = params.get('headers', {})
    method = params.get('method', 'GET').upper()
    
    if not url:
        return {"status": "error", "message": "URL is required"}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=30)
        elif method == 'POST':
            data = params.get('data', {})
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        
        return {
            "status": "success",
            "url": url,
            "status_code": response.status_code,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"status": "error", "message": str(e)}
```

### 4.2 数据处理插件模板
```python
def data_processing_plugin(params: dict):
    from subscribe.logger import logger
    
    input_data = params.get('input_data', [])
    operation = params.get('operation', 'identity')  # identity, filter, transform
    
    try:
        if operation == 'filter':
            condition = params.get('condition', lambda x: True)
            result = [item for item in input_data if condition(item)]
        elif operation == 'transform':
            transformer = params.get('transformer', lambda x: x)
            result = [transformer(item) for item in input_data]
        else:
            result = input_data
            
        logger.info(f"Processed {len(input_data)} items, got {len(result)} results")
        return {"status": "success", "processed_data": result, "original_count": len(input_data), "result_count": len(result)}
    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        return {"status": "error", "message": str(e)}
```

## 5. 配置参数详解

### 5.1 基础配置项
- `module_path`: 插件模块路径（Python导入路径）
- `function_name`: 插件执行函数名
- `enabled`: 是否启用（true/false）
- `cron_schedule`: 定时执行表达式（可选）
- `timeout`: 执行超时时间（秒）
- `max_retries`: 最大重试次数

### 5.2 参数配置
- `parameters`: 传递给插件的参数字典
- 可以包含任意键值对，插件函数通过 `params.get()` 获取

## 6. 常用cron表达式

| 表达式 | 说明 |
|--------|------|
| `*/5 * * * *` | 每5分钟 |
| `0 */1 * * *` | 每小时 |
| `0 2 * * *` | 每天凌晨2点 |
| `0 0 * * 0` | 每周日凌晨 |
| `30 10 * * 1-5` | 工作日上午10:30 |

## 7. 调试技巧

### 7.1 查看日志
```bash
# 查看容器日志
docker logs aggregator

# 实时查看日志
docker logs -f aggregator
```

### 7.2 测试命令
```bash
# 列出所有插件
python plugin_control.py list

# 运行特定插件
python plugin_control.py run plugin_name

# 查看插件状态
python plugin_control.py status plugin_name

# 启用插件
python plugin_control.py enable plugin_name

# 禁用插件
python plugin_control.py disable plugin_name
```

## 8. 常见问题

### 8.1 插件找不到
- 检查 `module_path` 是否正确
- 确认文件路径和函数名拼写
- 验证 `__init__.py` 文件是否存在

### 8.2 配置无效
- 检查JSON语法是否正确
- 确认缩进和标点符号
- 验证配置文件路径

### 8.3 执行失败
- 查看日志获取错误信息
- 检查参数传递是否正确
- 验证依赖包是否安装

## 9. 最佳实践

1. **错误处理** - 始终包含try-catch块
2. **日志记录** - 使用logger记录重要信息
3. **参数验证** - 验证输入参数的有效性
4. **返回格式** - 保持返回数据的一致性
5. **资源清理** - 释放使用的资源

## 10. 下一步

- 参考 `PLUGIN_DEVELOPMENT_GUIDE.md` 获取详细开发指南
- 查看 `plugin_config_template.json` 了解配置示例
- 尝试创建更复杂的插件

---

恭喜！您已经完成了插件开发的基本入门。现在可以开始创建自己的插件了！