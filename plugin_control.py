#!/usr/bin/env python3
"""
插件管理脚本 - 用于控制插件的启停
"""

import sys
import os
import json
import sys
import os

# 添加项目路径到sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from plugin_manager.manager import plugin_manager

def list_plugins():
    """列出所有插件及其状态"""
    print("当前插件状态:")
    print("-" * 50)
    for name, config in plugin_manager.plugins.items():
        status = "启用" if config.enabled else "禁用"
        print(f"插件: {name:20} | 状态: {status:6} | 定时: {config.cron_schedule or '无'}")


def enable_plugin(plugin_name):
    """启用插件"""
    if plugin_manager.enable_plugin(plugin_name):
        print(f"插件 '{plugin_name}' 已启用")
    else:
        print(f"插件 '{plugin_name}' 不存在")


def disable_plugin(plugin_name):
    """禁用插件"""
    if plugin_manager.disable_plugin(plugin_name):
        print(f"插件 '{plugin_name}' 已禁用")
    else:
        print(f"插件 '{plugin_name}' 不存在")


def execute_plugin(plugin_name):
    """执行单个插件"""
    result = plugin_manager.execute_plugin(plugin_name)
    if result is not None:
        print(f"插件 '{plugin_name}' 执行成功，结果: {result}")
    else:
        print(f"插件 '{plugin_name}' 执行失败")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python plugin_control.py list                    # 列出所有插件")
        print("  python plugin_control.py enable <plugin_name>    # 启用插件")
        print("  python plugin_control.py disable <plugin_name>   # 禁用插件")
        print("  python plugin_control.py run <plugin_name>       # 运行插件")
        print("  python plugin_control.py status <plugin_name>    # 查看插件状态")
        return

    command = sys.argv[1]

    if command == "list":
        list_plugins()
    elif command == "enable" and len(sys.argv) > 2:
        enable_plugin(sys.argv[2])
    elif command == "disable" and len(sys.argv) > 2:
        disable_plugin(sys.argv[2])
    elif command == "run" and len(sys.argv) > 2:
        execute_plugin(sys.argv[2])
    elif command == "status" and len(sys.argv) > 2:
        plugin_name = sys.argv[2]
        if plugin_name in plugin_manager.plugins:
            config = plugin_manager.plugins[plugin_name]
            status = "启用" if config.enabled else "禁用"
            print(f"插件 '{plugin_name}' 状态: {status}")
        else:
            print(f"插件 '{plugin_name}' 不存在")
    else:
        print("无效的命令或参数")


if __name__ == "__main__":
    main()