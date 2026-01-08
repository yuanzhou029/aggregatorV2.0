"""
插件管理器 - 实现精细化插件控制
"""

import json
import os
import importlib
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

import sys
import os
# 添加项目路径到sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from subscribe.logger import logger


class PluginStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginConfig:
    name: str
    module_path: str
    function_name: str
    enabled: bool
    cron_schedule: Optional[str] = None  # 定时执行配置
    parameters: Dict[str, Any] = None
    timeout: int = 300  # 执行超时时间（秒）
    max_retries: int = 3  # 最大重试次数


class PluginManager:
    def __init__(self, config_path: str = "./config/plugin_config.json"): # 修改为相对路径
        self.config_path = config_path
        self.plugins: Dict[str, PluginConfig] = {}
        self.load_plugin_config()
    
    def load_plugin_config(self):
        """从配置文件加载插件配置"""
        if not os.path.exists(self.config_path):
            logger.warning(f"插件配置文件不存在: {self.config_path}")
            # 创建默认配置文件
            self._create_default_config()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            for plugin_name, plugin_info in config_data.get("plugins", {}).items():
                plugin_config = PluginConfig(
                    name=plugin_name,
                    module_path=plugin_info["module_path"],
                    function_name=plugin_info["function_name"],
                    enabled=plugin_info.get("enabled", True),
                    cron_schedule=plugin_info.get("cron_schedule"),
                    parameters=plugin_info.get("parameters", {}),
                    timeout=plugin_info.get("timeout", 300),
                    max_retries=plugin_info.get("max_retries", 3)
                )
                        
                # 添加描述信息到插件配置对象
                if "description" in plugin_info:
                    setattr(plugin_config, 'description', plugin_info["description"])
                else:
                    setattr(plugin_config, 'description', f'{plugin_name} 插件')
                        
                self.plugins[plugin_name] = plugin_config
            
            logger.info(f"成功加载 {len(self.plugins)} 个插件配置")
        except Exception as e:
            logger.error(f"加载插件配置失败: {str(e)}")
    
    def _create_default_config(self):
        """创建默认插件配置文件"""
        default_config = {
            "plugins": {
                "fofa": {
                    "module_path": "subscribe.scripts.fofa",
                    "function_name": "main",
                    "enabled": True,
                    "cron_schedule": "",
                    "parameters": {},
                    "timeout": 300,
                    "max_retries": 3
                },
                "gitforks": {
                    "module_path": "subscribe.scripts.gitforks", 
                    "function_name": "main",
                    "enabled": True,
                    "cron_schedule": "",
                    "parameters": {},
                    "timeout": 300,
                    "max_retries": 3
                },
                "purefast": {
                    "module_path": "subscribe.scripts.purefast",
                    "function_name": "main",
                    "enabled": True,
                    "cron_schedule": "",
                    "parameters": {},
                    "timeout": 300,
                    "max_retries": 3
                },
                "tempairport": {
                    "module_path": "subscribe.scripts.tempairport",
                    "function_name": "main",
                    "enabled": True,
                    "cron_schedule": "",
                    "parameters": {},
                    "timeout": 300,
                    "max_retries": 3
                },
                "v2rayfree": {
                    "module_path": "subscribe.scripts.v2rayfree",
                    "function_name": "main",
                    "enabled": True,
                    "cron_schedule": "",
                    "parameters": {},
                    "timeout": 300,
                    "max_retries": 3
                },
                "v2rayse": {
                    "module_path": "subscribe.scripts.v2rayse",
                    "function_name": "main",
                    "enabled": True,
                    "cron_schedule": "",
                    "parameters": {},
                    "timeout": 300,
                    "max_retries": 3
                },
                "scaner": {
                    "module_path": "subscribe.scripts.scaner",
                    "function_name": "main",
                    "enabled": True,
                    "cron_schedule": "",
                    "parameters": {},
                    "timeout": 300,
                    "max_retries": 3
                }
            }
        }
        
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已创建默认插件配置文件: {self.config_path}")
        
        # 重新加载配置
        self.load_plugin_config()
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """检查插件是否启用"""
        plugin = self.plugins.get(plugin_name)
        return plugin is not None and plugin.enabled
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            self._save_plugin_config()
            logger.info(f"插件 {plugin_name} 已启用")
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            self._save_plugin_config()
            logger.info(f"插件 {plugin_name} 已禁用")
            return True
        return False
    
    def get_enabled_plugins(self) -> List[PluginConfig]:
        """获取所有启用的插件"""
        return [config for config in self.plugins.values() if config.enabled]
    
    def execute_plugin(self, plugin_name: str) -> Any:
        """执行指定插件"""
        if not self.is_plugin_enabled(plugin_name):
            logger.warning(f"插件 {plugin_name} 未启用，跳过执行")
            return None
        
        plugin_config = self.plugins[plugin_name]
        
        try:
            # 动态导入插件模块
            # 临时添加项目路径到sys.path
            sys.path.insert(0, project_root)
            module = importlib.import_module(plugin_config.module_path)
            function = getattr(module, plugin_config.function_name)
            
            logger.info(f"开始执行插件: {plugin_name}")
            
            # 执行插件函数
            result = function(plugin_config.parameters)
            
            logger.info(f"插件 {plugin_name} 执行成功")
            return result
            
        except Exception as e:
            logger.error(f"执行插件 {plugin_name} 失败: {str(e)}")
            return None
    
    def execute_all_enabled_plugins(self) -> Dict[str, Any]:
        """执行所有启用的插件"""
        results = {}
        
        for plugin_config in self.get_enabled_plugins():
            try:
                result = self.execute_plugin(plugin_config.name)
                results[plugin_config.name] = result
            except Exception as e:
                logger.error(f"执行插件 {plugin_config.name} 时发生错误: {str(e)}")
                results[plugin_config.name] = None
        
        return results
    
    def _save_plugin_config(self):
        """保存插件配置到文件"""
        config_data = {
            "plugins": {}
        }
        
        for name, config in self.plugins.items():
            config_data["plugins"][name] = {
                "module_path": config.module_path,
                "function_name": config.function_name,
                "enabled": config.enabled,
                "cron_schedule": config.cron_schedule,
                "parameters": config.parameters,
                "timeout": config.timeout,
                "max_retries": config.max_retries
            }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存插件配置失败: {str(e)}")


# 全局插件管理器实例
plugin_manager = PluginManager()


def run_enabled_plugins():
    """运行所有启用的插件"""
    return plugin_manager.execute_all_enabled_plugins()


def run_single_plugin(plugin_name: str):
    """运行单个插件"""
    return plugin_manager.execute_plugin(plugin_name)


def get_plugin_status():
    """获取所有插件状态"""
    return {
        name: "enabled" if config.enabled else "disabled"
        for name, config in plugin_manager.plugins.items()
    }