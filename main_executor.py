"""
主执行器 - 根据配置执行插件
"""

import time
import schedule
import threading
from plugin_manager.manager import plugin_manager, run_enabled_plugins
from subscribe.logger import logger


def execute_plugins():
    """执行启用的插件"""
    logger.info("开始执行启用的插件...")
    results = run_enabled_plugins()
    logger.info(f"插件执行完成，结果: {list(results.keys())}")


def setup_schedules():
    """根据配置设置定时任务"""
    for plugin_name, config in plugin_manager.plugins.items():
        # 根据配置类型获取enabled属性和cron_schedule
        if hasattr(config, "__dict__"):  # 对象类型
            is_enabled = getattr(config, "enabled", False)
            cron_schedule = getattr(config, "cron_schedule", "")
        else:  # 字典类型
            is_enabled = config.get("enabled", config.get("enable", True))
            cron_schedule = config.get("cron_schedule", "")

        if is_enabled and cron_schedule:
            # 这里简化处理定时任务设置
            # 实际可以根据cron_schedule表达式设置更复杂的定时任务
            if "day" in cron_schedule.lower():
                schedule.every().day.at("02:00").do(execute_plugins)
            elif "hour" in cron_schedule.lower():
                schedule.every().hour.do(execute_plugins)
            else:
                # 默认每天执行一次
                schedule.every().day.at("02:00").do(execute_plugins)


def main():
    """主函数"""
    logger.info("插件管理系统启动")

    # 设置定时任务
    setup_schedules()

    # 立即执行一次
    execute_plugins()

    # 保持程序运行以执行定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    main()
