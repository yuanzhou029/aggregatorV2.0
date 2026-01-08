# Aggregator 插件开发详细指南

## 1. 插件系统概述

Aggregator 的插件系统允许您扩展项目功能，实现自定义的数据抓取、处理和存储功能。插件系统具有以下特点：

- **模块化设计** - 每个插件都是独立的模块
- **动态加载** - 支持运行时加载和卸载插件
- **配置驱动** - 通过JSON配置文件控制插件行为
- **定时执行** - 支持cron表达式配置定时任务
- **错误处理** - 内置重试和错误处理机制

## 2. 插件结构

### 2.1 插件目录结构

```
plugins/
├── __init__.py
├── exercises/            # 练习题相关插件
│   ├── __init__.py
│   └── *.py
├── news/                 # 新闻相关插件
│   ├── __init__.py
│   └── *.py
├── custom_plugins/       # 用户自定义插件
│   ├── __init__.py
│   └── *.py
└── other_categories/     # 其他分类插件
    ├── __init__.py
    └── *.py
```

### 2.2 插件文件结构

每个插件文件应遵循以下结构：

```python
# -*- coding: utf-8 -*-
"""
插件名称: 描述插件功能
作者: 作者姓名
版本: 版本号
"""

import sys
import os
import time
import logging

# 添加项目路径到Python环境
sys.path.append('/aggregator')

from subscribe.logger import logger


def plugin_function_name(params: dict):
    """
    插件主函数
    
    Args:
        params (dict): 插件参数，包含配置信息
        
    Returns:
        插件执行结果，可以是任意Python对象
    """
    # 1. 记录插件开始执行
    logger.info(f"[插件标识] 开始执行插件，参数: {params}")
    
    try:
        # 2. 从参数中提取配置
        param_value = params.get('param_name', 'default_value')
        
        # 3. 执行插件逻辑
        result = execute_plugin_logic(param_value)
        
        # 4. 记录成功信息
        logger.info(f"[插件标识] 插件执行成功，结果: {result}")
        
        return result
        
    except Exception as e:
        # 5. 错误处理
        error_msg = f"插件执行失败: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}


def execute_plugin_logic(param_value):
    """
    插件具体实现逻辑
    """
    # 在这里实现插件的核心功能
    pass


# 如果需要，可以定义辅助函数
def helper_function():
    """
    辅助函数
    """
    pass


if __name__ == "__main__":
    # 用于测试插件的代码
    test_params = {
        "test_param": "test_value"
    }
    result = plugin_function_name(test_params)
    print(result)
```

## 3. 插件开发步骤

### 3.1 步骤一：创建插件文件

1. 选择合适的插件目录
2. 创建插件文件（使用有意义的文件名）
3. 编写插件函数

### 3.2 步骤二：实现插件功能

```python
# 示例：天气数据抓取插件
import sys
import requests
import json
from datetime import datetime

sys.path.append('/aggregator')
from subscribe.logger import logger


def weather_crawl_plugin(params: dict):
    """
    天气数据抓取插件
    
    Args:
        params (dict): 包含API密钥和城市信息的参数
        
    Returns:
        天气数据列表
    """
    logger.info("[WeatherCrawlPlugin] 开始抓取天气数据")
    
    # 从参数中获取配置
    api_key = params.get('api_key', '')
    city = params.get('city', 'Beijing')
    base_url = params.get('base_url', 'http://api.openweathermap.org/data/2.5/weather')
    
    if not api_key:
        error_result = {"status": "error", "message": "缺少API密钥"}
        logger.error("[WeatherCrawlPlugin] " + error_result['message'])
        return error_result
    
    try:
        # 构建请求URL
        url = f"{base_url}?q={city}&appid={api_key}&units=metric&lang=zh_cn"
        
        # 发起请求
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        weather_data = response.json()
        
        # 格式化结果
        formatted_data = {
            "location": weather_data.get("name"),
            "country": weather_data.get("sys", {}).get("country"),
            "temperature": weather_data.get("main", {}).get("temp"),
            "feels_like": weather_data.get("main", {}).get("feels_like"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "description": weather_data.get("weather", [{}])[0].get("description"),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[WeatherCrawlPlugin] 天气数据抓取成功: {formatted_data['location']}")
        return [formatted_data]  # 返回列表以便后续处理
        
    except requests.exceptions.RequestException as e:
        error_result = {"status": "error", "message": f"网络请求失败: {str(e)}"}
        logger.error(f"[WeatherCrawlPlugin] {error_result['message']}")
        return [error_result]
    except KeyError as e:
        error_result = {"status": "error", "message": f"数据解析失败: {str(e)}"}
        logger.error(f"[WeatherCrawlPlugin] {error_result['message']}")
        return [error_result]
    except Exception as e:
        error_result = {"status": "error", "message": f"未知错误: {str(e)}"}
        logger.error(f"[WeatherCrawlPlugin] {error_result['message']}")
        return [error_result]
```

### 3.3 步骤三：配置插件

在 `config/plugin_config.json` 中添加插件配置：

```json
{
  "plugins": {
    "weather_crawl_plugin": {
      "module_path": "plugins.custom_plugins.weather_plugin",
      "function_name": "weather_crawl_plugin",
      "enabled": false,
      "cron_schedule": "0 */3 * * *",
      "parameters": {
        "api_key": "your_openweather_api_key",
        "city": "Beijing",
        "base_url": "http://api.openweathermap.org/data/2.5/weather"
      },
      "timeout": 60,
      "max_retries": 3
    }
  }
}
```

## 4. 插件配置参数详解

### 4.1 配置文件结构

```json
{
  "plugins": {
    "unique_plugin_identifier": {
      "module_path": "plugins.category.plugin_filename",
      "function_name": "plugin_function_name",
      "enabled": true,
      "cron_schedule": "0 2 * * *",
      "parameters": {},
      "timeout": 300,
      "max_retries": 3
    }
  }
}
```

### 4.2 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `module_path` | string | 是 | - | Python模块导入路径 |
| `function_name` | string | 是 | - | 插件执行函数名 |
| `enabled` | boolean | 是 | false | 插件启用状态 |
| `cron_schedule` | string | 否 | - | cron定时表达式 |
| `parameters` | object | 否 | {} | 传递给插件的参数 |
| `timeout` | integer | 否 | 300 | 执行超时时间（秒） |
| `max_retries` | integer | 否 | 3 | 最大重试次数 |

### 4.3 Cron表达式说明

Cron表达式由5个字段组成：`分钟 小时 日 月 星期`

| 符号 | 说明 | 示例 | 含义 |
|------|------|------|------|
| `*` | 任意值 | `* * * * *` | 每分钟 |
| `,` | 列表值 | `1,3,5 * * * *` | 1、3、5分钟 |
| `-` | 范围 | `1-5 * * * *` | 1到5分钟 |
| `/` | 步长 | `*/5 * * * *` | 每5分钟 |

**常用示例：**
- `0 2 * * *` - 每天凌晨2点
- `*/30 * * * *` - 每30分钟
- `0 0 * * 0` - 每周日午夜
- `0 */6 * * *` - 每6小时
- `30 10 * * 1-5` - 工作日上午10:30

## 5. 插件开发最佳实践

### 5.1 错误处理

```python
def robust_plugin(params: dict):
    logger.info("[RobustPlugin] 开始执行")
    
    try:
        # 主要逻辑
        result = main_logic(params)
        
        # 验证结果
        if not validate_result(result):
            raise ValueError("结果验证失败")
            
        logger.info("[RobustPlugin] 执行成功")
        return result
        
    except ValueError as e:
        logger.error(f"[RobustPlugin] 值错误: {e}")
        return {"status": "error", "message": str(e)}
    except requests.RequestException as e:
        logger.error(f"[RobustPlugin] 请求错误: {e}")
        return {"status": "error", "message": f"网络错误: {e}"}
    except Exception as e:
        logger.error(f"[RobustPlugin] 未知错误: {e}")
        return {"status": "error", "message": f"未知错误: {e}"}
```

### 5.2 日志记录

```python
def logging_plugin(params: dict):
    # 开始日志
    logger.info(f"[LoggingPlugin] 开始执行，参数: {mask_sensitive_data(params)}")
    
    start_time = time.time()
    
    try:
        result = execute_business_logic(params)
        
        # 成功日志
        execution_time = time.time() - start_time
        logger.info(f"[LoggingPlugin] 执行成功，耗时: {execution_time:.2f}秒，结果数量: {len(result) if isinstance(result, list) else 1}")
        
        return result
    except Exception as e:
        # 错误日志
        execution_time = time.time() - start_time
        logger.error(f"[LoggingPlugin] 执行失败，耗时: {execution_time:.2f}秒，错误: {str(e)}")
        raise
```

### 5.3 参数验证

```python
def validated_plugin(params: dict):
    # 验证必需参数
    required_params = ['api_key', 'endpoint']
    for param in required_params:
        if param not in params or not params[param]:
            raise ValueError(f"缺少必需参数: {param}")
    
    # 验证参数类型
    timeout = params.get('timeout', 30)
    if not isinstance(timeout, int) or timeout <= 0:
        raise ValueError(f"timeout参数必须是正整数，当前值: {timeout}")
    
    # 验证URL格式
    endpoint = params.get('endpoint', '')
    if not endpoint.startswith(('http://', 'https://')):
        raise ValueError(f"endpoint必须是有效的URL，当前值: {endpoint}")
    
    # 执行主要逻辑
    return execute_main_logic(params)
```

## 6. 插件测试

### 6.1 单独测试插件

```bash
# 进入容器
docker exec -it aggregator bash

# 测试插件
python plugin_control.py run plugin_name

# 查看插件状态
python plugin_control.py status plugin_name
```

### 6.2 手动测试插件

```python
# 直接运行插件进行测试
import sys
sys.path.append('/aggregator')

from plugins.custom_plugins.your_plugin import your_function

test_params = {
    "param1": "value1",
    "param2": "value2"
}

result = your_function(test_params)
print(result)
```

## 7. 常见插件类型示例

### 7.1 数据抓取插件

```python
def web_scraper_plugin(params: dict):
    """
    网页抓取插件示例
    """
    import requests
    from bs4 import BeautifulSoup
    
    url = params.get('url', '')
    selector = params.get('selector', 'body')
    
    if not url:
        return {"status": "error", "message": "缺少URL参数"}
    
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        elements = soup.select(selector)
        
        results = []
        for elem in elements:
            results.append({
                "text": elem.get_text(strip=True),
                "html": str(elem),
                "url": url
            })
        
        return results
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

### 7.2 数据处理插件

```python
def data_processor_plugin(params: dict):
    """
    数据处理插件示例
    """
    input_data = params.get('input_data', [])
    operation = params.get('operation', 'filter')
    
    if operation == 'filter':
        # 过滤数据
        filtered_data = [item for item in input_data if item.get('active', True)]
        return filtered_data
    elif operation == 'transform':
        # 转换数据
        transformed_data = []
        for item in input_data:
            new_item = {
                'id': item.get('id'),
                'name': item.get('name', '').upper(),
                'processed_at': time.time()
            }
            transformed_data.append(new_item)
        return transformed_data
    else:
        return {"status": "error", "message": f"未知操作: {operation}"}
```

### 7.3 存储插件

```python
def data_storage_plugin(params: dict):
    """
    数据存储插件示例
    """
    import json
    import os
    
    data = params.get('data', [])
    storage_path = params.get('storage_path', '/aggregator/data/output.json')
    
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # 读取现有数据
        existing_data = []
        if os.path.exists(storage_path):
            with open(storage_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # 合并数据
        merged_data = existing_data + data
        
        # 保存数据
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success", 
            "saved_count": len(data), 
            "total_count": len(merged_data),
            "path": storage_path
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

## 8. 插件部署和管理

### 8.1 部署插件

1. 将插件文件放置到相应的插件目录
2. 在配置文件中添加插件配置
3. 验证配置语法
4. 重启服务或重新加载配置

### 8.2 管理插件

```bash
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

### 8.3 监控插件

- 检查日志输出
- 验证执行结果
- 监控资源使用情况
- 设置告警通知

## 9. 故障排除

### 9.1 常见问题

**问题1：插件无法找到**
- 检查 `module_path` 是否正确
- 确认插件文件存在
- 验证函数名拼写

**问题2：插件执行失败**
- 查看日志输出
- 检查参数配置
- 验证依赖项

**问题3：定时任务不执行**
- 检查 `cron_schedule` 语法
- 确认插件处于启用状态
- 验证时间区域设置

### 9.2 调试技巧

1. 使用测试参数运行插件
2. 检查日志级别设置
3. 验证依赖包安装
4. 使用调试模式运行

## 10. 安全注意事项

- 不要在代码中硬编码敏感信息
- 验证所有输入参数
- 限制插件资源使用
- 定期审查插件代码
- 使用沙箱环境测试

---

通过遵循本指南，您可以成功开发和部署自定义插件，扩展Aggregator项目的功能。记住始终进行充分的测试，并遵循最佳实践来确保插件的稳定性和安全性。