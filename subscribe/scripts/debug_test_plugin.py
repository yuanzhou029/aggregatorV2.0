"""
调试测试插件 - 用于测试插件系统调试功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logger import logger


def main(params=None):
    """
    调试测试插件主函数
    :param params: 参数字典
    :return: 执行结果
    """
    try:
        logger.info("执行调试测试插件...")
        
        if params:
            logger.info(f"收到参数: {params}")
        
        # 模拟调试测试逻辑
        result = {
            "status": "success",
            "message": "调试测试插件执行成功",
            "data": {
                "plugin_name": "debug_test_plugin",
                "executed_at": __import__('datetime').datetime.now().isoformat(),
                "debug_info": "plugin_debug_test_completed"
            }
        }
        
        logger.info("调试测试插件执行完成")
        return result
        
    except Exception as e:
        logger.error(f"调试测试插件执行失败: {str(e)}")
        return {
            "status": "error",
            "message": f"执行失败: {str(e)}"
        }


if __name__ == "__main__":
    # 当直接运行此脚本时的测试代码
    result = main({"debug_param": "debug_value"})
    print(result)