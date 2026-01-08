"""
自定义插件示例
"""

import sys
sys.path.append('/aggregator')

from logger import logger


def my_custom_function(params: dict):
    """
    自定义插件函数
    
    Args:
        params: 插件参数
        
    Returns:
        插件执行结果
    """
    logger.info(f"[MyCustomPlugin] 执行自定义插件，参数: {params}")
    
    # 实现您的自定义逻辑
    result = {
        "status": "success",
        "message": "自定义插件执行成功",
        "timestamp": __import__('time').time(),
        "params": params
    }
    
    logger.info(f"[MyCustomPlugin] 插件执行结果: {result}")
    return result