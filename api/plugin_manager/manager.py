"""
插件管理器实现
"""
import os
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, List

from subscribe.logger import logger


class PluginManager:
    """
    插件管理器类，负责管理插件的生命周期
    """

    def __init__(self):
        self.plugins = {}
        self.plugin_states = {}
        self.plugin_schedules = {}
        self.plugin_parameters = {}
        self.running_plugins = set()
        self.last_runs = {}
        self.next_runs = {}

        # 加载插件配置
        self.load_plugins()

    def load_plugins(self):
        """
        从配置文件加载插件配置
        """
        config_path = './config/plugin_config.json'
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    raw_plugins = config.get('plugins', {})

                    # 验证插件配置格式并转换
                    for plugin_name, plugin_config in raw_plugins.items():
                        # 确保插件配置有必需的字段
                        validated_config = {
                            'name': plugin_config.get(
                                'name', plugin_name), 'description': plugin_config.get(
                                'description', f'{plugin_name} 插件'), 'enabled': plugin_config.get(
                                'enabled', True), 'schedule': plugin_config.get(
                                'schedule', ''), 'parameters': plugin_config.get(
                                'parameters', {})}

                        self.plugins[plugin_name] = validated_config
                        self.plugin_states[plugin_name] = validated_config['enabled']
                        self.plugin_schedules[plugin_name] = validated_config['schedule']
                        self.plugin_parameters[plugin_name] = validated_config['parameters']

                        # 设置初始运行时间
                        self.last_runs[plugin_name] = None
                        self.next_runs[plugin_name] = None

                    logger.info(f"成功加载 {len(self.plugins)} 个插件配置")
            else:
                # 如果配置文件不存在，尝试从可用的脚本中加载插件
                self._load_from_scripts()

        except KeyError as e:
            logger.error(f"加载插件配置失败，缺少必要字段: {str(e)}")
            # 设置默认插件
            self._set_default_plugins()
        except Exception as e:
            logger.error(f"加载插件配置失败: {str(e)}")
            # 设置默认插件
            self._set_default_plugins()

    def _load_from_scripts(self):
        """
        从可用的脚本中加载插件
        """
        script_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__))),
            'subscribe',
            'scripts')
        if os.path.exists(script_dir):
            for filename in os.listdir(script_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    plugin_name = filename[:-3]  # 去掉.py扩展名
                    self.plugins[plugin_name] = {
                        'name': plugin_name,
                        'description': f'{plugin_name} 插件',
                        'enabled': True,
                        'schedule': '',
                        'parameters': {}
                    }
                    self.plugin_states[plugin_name] = True
                    self.plugin_schedules[plugin_name] = ''
                    self.plugin_parameters[plugin_name] = {}
                    self.last_runs[plugin_name] = None
                    self.next_runs[plugin_name] = None

    def _set_default_plugins(self):
        """
        设置默认插件
        """
        default_plugins = {
            'fofa': 'FOFA数据抓取插件',
            'gitforks': 'GitHub Forks抓取插件',
            'purefast': 'PureFast机场订阅插件',
            'tempairport': '临时机场订阅插件',
            'v2rayfree': 'V2Ray免费节点抓取插件',
            'v2rayse': 'V2RaySE节点抓取插件',
            'scaner': '网络扫描插件'
        }

        for plugin_name, description in default_plugins.items():
            self.plugins[plugin_name] = {
                'name': plugin_name,
                'description': description,
                'enabled': True,
                'schedule': '',
                'parameters': {}
            }
            self.plugin_states[plugin_name] = True
            self.plugin_schedules[plugin_name] = ''
            self.plugin_parameters[plugin_name] = {}
            self.last_runs[plugin_name] = None
            self.next_runs[plugin_name] = None

    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """
        获取所有插件信息
        """
        result = []
        for plugin_name, plugin_config in self.plugins.items():
            plugin_info = {
                'name': plugin_name,
                'description': plugin_config.get('description', ''),
                'enabled': self.plugin_states.get(plugin_name, False),
                'status': 'running' if plugin_name in self.running_plugins else 'idle',
                'schedule': self.plugin_schedules.get(plugin_name, ''),
                'parameters': self.plugin_parameters.get(plugin_name, {}),
                'lastRun': self.last_runs.get(plugin_name),
                'nextRun': self.next_runs.get(plugin_name)
            }
            result.append(plugin_info)
        return result

    def get_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """
        获取特定插件信息
        """
        if plugin_name not in self.plugins:
            return None

        return {
            'name': plugin_name,
            'description': self.plugins[plugin_name].get(
                'description',
                ''),
            'enabled': self.plugin_states.get(
                plugin_name,
                False),
            'status': 'running' if plugin_name in self.running_plugins else 'idle',
            'schedule': self.plugin_schedules.get(
                plugin_name,
                ''),
            'parameters': self.plugin_parameters.get(
                plugin_name,
                {}),
            'lastRun': self.last_runs.get(plugin_name),
            'nextRun': self.next_runs.get(plugin_name)}

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        启用插件
        """
        if plugin_name in self.plugin_states:
            self.plugin_states[plugin_name] = True
            return True
        return False

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        禁用插件
        """
        if plugin_name in self.plugin_states:
            self.plugin_states[plugin_name] = False
            return True
        return False

    def run_plugin(self, plugin_name: str) -> bool:
        """
        立即运行插件
        """
        if plugin_name not in self.plugins:
            return False

        # 检查插件是否已在运行
        if plugin_name in self.running_plugins:
            return False

        # 标记插件为正在运行
        self.running_plugins.add(plugin_name)
        self.last_runs[plugin_name] = datetime.now().isoformat()

        # 在后台线程中运行插件
        thread = threading.Thread(
            target=self._execute_plugin,
            args=(plugin_name,),
            daemon=True
        )
        thread.start()

        return True

    def _execute_plugin(self, plugin_name: str):
        """
        执行插件的实际逻辑
        """
        try:
            # 这里应该根据插件类型执行相应的逻辑
            # 暂时只记录日志
            logger.info(f"开始执行插件: {plugin_name}")

            # 模拟插件执行
            time.sleep(2)  # 模拟执行时间

            logger.info(f"插件执行完成: {plugin_name}")
        except Exception as e:
            logger.error(f"执行插件失败: {plugin_name}, 错误: {str(e)}")
        finally:
            # 从运行列表中移除
            self.running_plugins.discard(plugin_name)
            # 更新下次运行时间
            self.next_runs[plugin_name] = None

    def update_plugin_config(self, plugin_name: str,
                             config: Dict[str, Any]) -> bool:
        """
        更新插件配置
        """
        if plugin_name not in self.plugins:
            return False

        # 更新配置
        if 'enabled' in config:
            self.plugin_states[plugin_name] = config['enabled']
        if 'schedule' in config:
            self.plugin_schedules[plugin_name] = config['schedule']
        if 'parameters' in config:
            self.plugin_parameters[plugin_name] = config['parameters']
        if 'description' in config:
            self.plugins[plugin_name]['description'] = config['description']

        # 保存配置到文件
        self.save_config()

        return True

    def save_config(self):
        """
        保存插件配置到文件
        """
        config_path = './config/plugin_config.json'
        config_dir = os.path.dirname(config_path)

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 构建配置字典
        config = {
            'plugins': {}
        }

        for plugin_name, plugin_config in self.plugins.items():
            config['plugins'][plugin_name] = {
                'name': plugin_name,
                'description': plugin_config.get('description', ''),
                'enabled': self.plugin_states.get(plugin_name, False),
                'schedule': self.plugin_schedules.get(plugin_name, ''),
                'parameters': self.plugin_parameters.get(plugin_name, {})
            }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info("插件配置已保存到文件")
        except Exception as e:
            logger.error(f"保存插件配置失败: {str(e)}")


# 创建全局插件管理器实例
plugin_manager = PluginManager()
