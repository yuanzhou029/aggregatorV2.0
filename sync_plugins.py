"""
插件脚本和配置同步脚本
此脚本用于确保subscribe/scripts目录下的脚本文件与config/plugin_config.json中的配置保持一致
"""
import json
import os
import glob


def sync_plugins():
    """
    同步脚本文件和配置文件
    """
    # 获取scripts目录下的所有Python文件
    script_dir = "subscribe/scripts"
    script_files = []

    for file_path in glob.glob(os.path.join(script_dir, "*.py")):
        filename = os.path.basename(file_path)
        if filename != "__init__.py":
            plugin_name = os.path.splitext(filename)[0]
            script_files.append(plugin_name)

    print(f"发现 {len(script_files)} 个脚本文件: {script_files}")

    # 读取现有的配置文件
    config_path = "config/plugin_config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        existing_plugins = config.get("plugins", {})
    else:
        existing_plugins = {}

    print(f"现有配置中包含 {len(existing_plugins)} 个插件")

    # 创建新的插件配置
    new_plugins = {}

    # 添加所有脚本文件对应的配置
    for script_name in script_files:
        if script_name in existing_plugins:
            # 如果已有配置，保留原有配置
            new_plugins[script_name] = existing_plugins[script_name]
            print(f"保留插件 {script_name} 的现有配置")
        else:
            # 如果没有配置，创建默认配置
            new_plugins[script_name] = {
                "module_path": f"subscribe.scripts.{script_name}",
                "function_name": "main",
                "enabled": False,
                "cron_schedule": "",
                "parameters": {},
                "timeout": 300,
                "max_retries": 3
            }
            print(f"为脚本 {script_name} 创建新配置")

    # 创建新的配置字典
    new_config = {
        "plugins": new_plugins
    }

    # 确保config目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # 写入新的配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(new_config, f, ensure_ascii=False, indent=2)

    print(f"\n同步完成!")
    print(f"最终配置包含 {len(new_plugins)} 个插件")
    print(f"插件列表: {list(new_plugins.keys())}")


if __name__ == "__main__":
    sync_plugins()
