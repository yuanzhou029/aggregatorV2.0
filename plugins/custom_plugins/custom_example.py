
"""
自定义插件示例
"""

import sys
import os
sys.path.append('/aggregator')

from subscribe.logger import logger


def my_custom_function(params: dict):
    """
    自定义插件函数示例
    
    Args:
        params: 插件参数
        
    Returns:
        插件执行结果
    """
    logger.info(f"[CustomPlugin] 执行自定义插件，参数: {params}")
    
    # 实现您的自定义逻辑
    action = params.get("action", "default")
    
    if action == "hello":
        message = "Hello from custom plugin!"
    elif action == "calculate":
        x = params.get("x", 0)
        y = params.get("y", 0)
        result = x + y
        message = f"计算结果: {x} + {y} = {result}"
    else:
        message = "自定义插件执行完成"
    
    result = {
        "status": "success",
        "message": message,
        "timestamp": __import__('time').time(),
        "params": params
    }
    
    logger.info(f"[CustomPlugin] 插件执行结果: {result}")
    return result
