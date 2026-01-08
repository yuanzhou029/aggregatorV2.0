"""
API接口实现用于前端UI与后端插件系统的交互
"""
import json
import os
import hashlib
import secrets
import psutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import threading
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, Any

# 导入插件管理器
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from plugin_manager.manager import PluginManager, plugin_manager as global_plugin_manager
from subscribe.logger import logger

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # 保持JSON键的顺序
CORS(app, supports_credentials=True, origins=['*'], allow_headers=['Content-Type', 'Authorization'])  # 允许跨域请求

# 配置文件路径
CONFIG_PATH = './config/plugin_config.json'

# 身份验证配置
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', hashlib.sha256(b'admin123').hexdigest())
SESSION_TIMEOUT = 3600  # 1小时

# 简单的会话存储
sessions = {}

# 系统启动时间
SYSTEM_START_TIME = datetime.now()

# 使用全局插件管理器实例
plugin_manager = global_plugin_manager
# logger实例已经从subscribe.logger导入，无需重新定义
# logger = logger

# 适配插件管理器的接口
# 为插件管理器创建适配器，处理不同类型的插件配置
def get_all_plugins_adaptor():
    plugins = []
    for name, config in plugin_manager.plugins.items():
        # 检查配置是数据类对象还是字典
        if hasattr(config, 'name'):
            # 这是一个PluginConfig对象
            plugin_info = {
                'name': getattr(config, 'name', name),
                'description': getattr(config, 'description', f'{name} 插件'),
                'enabled': getattr(config, 'enabled', False),
                'status': '空闲',
                'schedule': getattr(config, 'cron_schedule', ''),
                'parameters': getattr(config, 'parameters', {})
            }
        else:
            # 这是一个字典配置
            plugin_info = {
                'name': config.get('name', name),
                'description': config.get('description', f'{name} 插件'),
                'enabled': config.get('enabled', config.get('enable', True)),
                'status': '空闲',
                'schedule': config.get('schedule', config.get('cron_schedule', '')),
                'parameters': config.get('parameters', {})
            }
        plugins.append(plugin_info)
    return plugins


def get_running_tasks_count():
    """获取当前运行的任务数"""
    # 获取插件管理器中的运行中插件数量
    running_count = 0
    if hasattr(plugin_manager, 'running_plugins'):
        running_count = len(plugin_manager.running_plugins)
    else:
        # 如果插件管理器没有跟踪运行中的插件，则检查Python进程中是否有运行中的插件
        for proc in psutil.process_iter():
            try:
                if 'python' in proc.name().lower() and 'plugin' in ' '.join(proc.cmdline()).lower():
                    running_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    return running_count


def get_system_uptime():
    """获取系统运行时间"""
    uptime = datetime.now() - SYSTEM_START_TIME
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}天 {hours}小时 {minutes}分钟"
    else:
        return f"{hours}小时 {minutes}分钟 {seconds}秒"

@app.route('/api/plugins', methods=['GET'])
def get_plugins():
    """获取所有插件列表及状态"""
    try:
        plugins = get_all_plugins_adaptor()
        return jsonify({
            "success": True,
            "data": plugins
        })
    except Exception as e:
        logger.error(f"获取插件列表失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>', methods=['GET'])
def get_plugin(plugin_name):
    """获取特定插件信息"""
    try:
        if plugin_name in plugin_manager.plugins:
            config = plugin_manager.plugins[plugin_name]
            plugin = {
                'name': plugin_name,
                'description': getattr(config, 'description', f'{plugin_name} 插件'),
                'enabled': getattr(config, 'enabled', False),
                'status': '空闲',
                'schedule': getattr(config, 'cron_schedule', ''),
                'parameters': getattr(config, 'parameters', {})
            }
            return jsonify({
                "success": True,
                "data": plugin
            })
        else:
            return jsonify({
                "success": False,
                "error": "插件不存在"
            }), 404
    except Exception as e:
        logger.error(f"获取插件信息失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>/enable', methods=['POST'])
def enable_plugin(plugin_name):
    """启用插件"""
    try:
        success = plugin_manager.enable_plugin(plugin_name)
        if success:
            return jsonify({
                "success": True,
                "message": f"插件 {plugin_name} 已启用"
            })
        else:
            return jsonify({
                "success": False,
                "error": "启用插件失败"
            }), 400
    except Exception as e:
        logger.error(f"启用插件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>/disable', methods=['POST'])
def disable_plugin(plugin_name):
    """禁用插件"""
    try:
        success = plugin_manager.disable_plugin(plugin_name)
        if success:
            return jsonify({
                "success": True,
                "message": f"插件 {plugin_name} 已禁用"
            })
        else:
            return jsonify({
                "success": False,
                "error": "禁用插件失败"
            }), 400
    except Exception as e:
        logger.error(f"禁用插件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>/run', methods=['POST'])
def run_plugin(plugin_name):
    """立即执行插件"""
    try:
        if plugin_name in plugin_manager.plugins:
            result = plugin_manager.execute_plugin(plugin_name)
            if result is not None:
                return jsonify({
                    "success": True,
                    "message": f"插件 {plugin_name} 已执行完成"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "执行插件失败"
                }), 400
        else:
            return jsonify({
                "success": False,
                "error": "插件不存在"
            }), 404
    except Exception as e:
        logger.error(f"执行插件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>', methods=['PUT'])
def update_plugin(plugin_name):
    """更新插件配置"""
    try:
        data = request.get_json()
        if plugin_name in plugin_manager.plugins:
            # 更新插件配置
            plugin_config = plugin_manager.plugins[plugin_name]
            
            # 根据配置类型更新相应字段
            if hasattr(plugin_config, '__dict__'):  # 对象类型
                if 'enabled' in data:
                    plugin_config.enabled = data['enabled']
                if 'schedule' in data:
                    plugin_config.cron_schedule = data['schedule']
                if 'parameters' in data:
                    plugin_config.parameters = data['parameters']
                if 'description' in data:
                    plugin_config.description = data['description']
                if 'module_path' in data:
                    plugin_config.module_path = data['module_path']
                if 'function_name' in data:
                    plugin_config.function_name = data['function_name']
            else:  # 字典类型
                if 'enabled' in data:
                    plugin_config['enabled'] = data['enabled']
                if 'schedule' in data:
                    plugin_config['cron_schedule'] = data['schedule']
                if 'parameters' in data:
                    plugin_config['parameters'] = data['parameters']
                if 'description' in data:
                    plugin_config['description'] = data['description']
                if 'module_path' in data:
                    plugin_config['module_path'] = data['module_path']
                if 'function_name' in data:
                    plugin_config['function_name'] = data['function_name']
            
            # 保存配置
            plugin_manager._save_plugin_config()
            
            return jsonify({
                "success": True,
                "message": f"插件 {plugin_name} 配置已更新"
            })
        else:
            return jsonify({
                "success": False,
                "error": "插件不存在"
            }), 404
    except Exception as e:
        logger.error(f"更新插件配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/plugin', methods=['GET'])
def get_plugin_config():
    """获取插件配置"""
    try:
        # 直接读取配置文件
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return jsonify({
            "success": True,
            "data": config
        })
    except FileNotFoundError:
        logger.error("插件配置文件不存在")
        return jsonify({
            "success": False,
            "error": "插件配置文件不存在"
        }), 404
    except Exception as e:
        logger.error(f"获取插件配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/plugin', methods=['PUT'])
def update_plugin_config():
    """更新插件配置"""
    try:
        data = request.get_json()
        # 写入配置文件
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 更新插件管理器的配置
        plugin_manager.plugins = data.get('plugins', {})
        
        return jsonify({
            "success": True,
            "message": "插件配置已更新"
        })
    except Exception as e:
        logger.error(f"更新插件配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取系统整体状态"""
    try:
        plugins = get_all_plugins_adaptor()
        active_plugins = [p for p in plugins if p.get('enabled', False)]
        total_plugins = len(plugins)
        active_count = len(active_plugins)
        running_tasks = get_running_tasks_count()
        system_uptime = get_system_uptime()
        
        return jsonify({
            "success": True,
            "data": {
                "total_plugins": total_plugins,
                "active_plugins": active_count,
                "running_tasks": running_tasks,
                "system_uptime": system_uptime,
                "last_update": datetime.now().isoformat(),
                "plugins": plugins
            }
        })
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取系统日志（简化实现）"""
    try:
        # 这里简化实现，实际应从日志文件中读取
        logs = [
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "系统启动"},
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "插件管理器初始化完成"}
        ]
        return jsonify({
            "success": True,
            "data": logs
        })
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/system', methods=['GET'])
def get_system_config():
    """获取系统配置"""
    try:
        # 返回系统配置，包括环境变量
        system_config = {
            "version": "1.0.0",
            "api_port": 5000,
            "web_port": 14047,  # 默认前端端口
            "storage_type": "local",
            "env_vars": {
                "GIST_PAT": os.getenv('GIST_PAT', ''),
                "GIST_LINK": os.getenv('GIST_LINK', ''),
                "CUSTOMIZE_LINK": os.getenv('CUSTOMIZE_LINK', ''),
                "ADMIN_USERNAME": os.getenv('ADMIN_USERNAME', 'admin'),
                "TZ": os.getenv('TZ', 'Asia/Shanghai')
            }
        }
        return jsonify({
            "success": True,
            "data": system_config
        })
    except Exception as e:
        logger.error(f"获取系统配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/system', methods=['PUT'])
def update_system_config():
    """更新系统配置"""
    try:
        data = request.get_json()
        env_vars = data.get('env_vars', {})
        
        # 更新环境变量（这里仅作示例，实际在容器中需要持久化）
        if 'GIST_PAT' in env_vars:
            os.environ['GIST_PAT'] = env_vars['GIST_PAT']
        if 'GIST_LINK' in env_vars:
            os.environ['GIST_LINK'] = env_vars['GIST_LINK']
        if 'CUSTOMIZE_LINK' in env_vars:
            os.environ['CUSTOMIZE_LINK'] = env_vars['CUSTOMIZE_LINK']
        if 'ADMIN_USERNAME' in env_vars:
            os.environ['ADMIN_USERNAME'] = env_vars['ADMIN_USERNAME']
        if 'TZ' in env_vars:
            os.environ['TZ'] = env_vars['TZ']
        
        # 如果提供了新的密码，更新密码哈希
        if 'ADMIN_PASSWORD' in env_vars and env_vars['ADMIN_PASSWORD']:
            new_password_hash = hashlib.sha256(env_vars['ADMIN_PASSWORD'].encode()).hexdigest()
            os.environ['ADMIN_PASSWORD_HASH'] = new_password_hash
        
        return jsonify({
            "success": True,
            "message": "系统配置已更新"
        })
    except Exception as e:
        logger.error(f"更新系统配置失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# 身份验证装饰器
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Missing or invalid authorization header'}), 401
        
        session_token = auth_header.split(' ')[1]
        if session_token not in sessions:
            return jsonify({'success': False, 'error': 'Session expired or invalid'}), 401
        
        session_data = sessions[session_token]
        if time.time() - session_data['timestamp'] > SESSION_TIMEOUT:
            del sessions[session_token]
            return jsonify({'success': False, 'error': 'Session expired'}), 401
        
        # 更新会话时间戳
        session_data['timestamp'] = time.time()
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 尝试多种方式获取JSON数据
        data = None
        if request.is_json:
            data = request.get_json()
        else:
            # 尝试从请求数据中解析JSON
            content_type = request.content_type
            if content_type and 'application/json' in content_type:
                try:
                    import json as std_json
                    data = std_json.loads(request.get_data(as_text=True))
                except:
                    pass
            
        if data is None:
            return jsonify({
                'success': False,
                'error': 'No valid JSON data provided'
            }), 400
            
        username = data.get('username')
        password = data.get('password')
        
        # 验证用户名和密码
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
            # 创建会话令牌
            session_token = secrets.token_hex(32)
            sessions[session_token] = {
                'username': username,
                'timestamp': time.time(),
                'role': 'admin'
            }
            
            return jsonify({
                'success': True,
                'token': session_token,
                'message': 'Login successful'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid credentials'
            }), 401
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/logout', methods=['POST'])
@require_auth

def logout():
    """用户登出"""
    try:
        auth_header = request.headers.get('Authorization')
        session_token = auth_header.split(' ')[1]
        
        if session_token in sessions:
            del sessions[session_token]
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 为需要保护的端点添加身份验证
# 重新定义需要保护的路由
@app.route('/api/plugins', methods=['GET'])
@require_auth
def get_plugins_protected():
    return get_plugins()

@app.route('/api/plugins/<plugin_name>', methods=['GET'])
@require_auth
def get_plugin_protected(plugin_name):
    return get_plugin(plugin_name)

@app.route('/api/plugins/<plugin_name>/enable', methods=['POST'])
@require_auth
def enable_plugin_protected(plugin_name):
    return enable_plugin(plugin_name)

@app.route('/api/plugins/<plugin_name>/disable', methods=['POST'])
@require_auth
def disable_plugin_protected(plugin_name):
    return disable_plugin(plugin_name)

@app.route('/api/plugins/<plugin_name>/run', methods=['POST'])
@require_auth
def run_plugin_protected(plugin_name):
    return run_plugin(plugin_name)

@app.route('/api/plugins/<plugin_name>', methods=['PUT'])
@require_auth
def update_plugin_protected(plugin_name):
    return update_plugin(plugin_name)

# 添加插件管理的新API
@app.route('/api/plugins/add', methods=['POST'])
@require_auth
def add_plugin():
    """添加插件"""
    try:
        data = request.get_json()
        plugin_name = data.get('name')
        description = data.get('description', f'{plugin_name} 插件')
        module_path = data.get('module_path', f'subscribe.scripts.{plugin_name}')
        function_name = data.get('function_name', 'main')
        enabled = data.get('enabled', True)
        schedule = data.get('schedule', '')
        parameters = data.get('parameters', {})
        
        # 创建插件配置
        from dataclasses import fields
        try:
            # 检查PluginManager是否具有正确的PluginConfig类
            import inspect
            plugin_config_class = getattr(plugin_manager.__class__, 'PluginConfig', None)
            if plugin_config_class and inspect.isclass(plugin_config_class):
                plugin_config = plugin_config_class(
                    name=plugin_name,
                    module_path=module_path,
                    function_name=function_name,
                    enabled=enabled,
                    cron_schedule=schedule,
                    parameters=parameters,
                    timeout=data.get('timeout', 300),
                    max_retries=data.get('max_retries', 3)
                )
            else:
                # 创建一个简单的配置对象
                class SimplePluginConfig:
                    def __init__(self, **kwargs):
                        for k, v in kwargs.items():
                            setattr(self, k, v)
                plugin_config = SimplePluginConfig(
                    name=plugin_name,
                    module_path=module_path,
                    function_name=function_name,
                    enabled=enabled,
                    cron_schedule=schedule,
                    parameters=parameters,
                    timeout=data.get('timeout', 300),
                    max_retries=data.get('max_retries', 3)
                )
        except:
            # 如果以上都不行，使用字典形式
            plugin_config = {
                'name': plugin_name,
                'module_path': module_path,
                'function_name': function_name,
                'enabled': enabled,
                'cron_schedule': schedule,
                'parameters': parameters,
                'timeout': data.get('timeout', 300),
                'max_retries': data.get('max_retries', 3)
            }
        
        # 动态添加描述
        if isinstance(plugin_config, dict):
            plugin_config['description'] = description
        else:
            setattr(plugin_config, 'description', description)
        
        plugin_manager.plugins[plugin_name] = plugin_config
        
        # 保存配置
        plugin_manager._save_plugin_config()
        
        return jsonify({
            "success": True,
            "message": f"插件 {plugin_name} 已添加"
        })
    except Exception as e:
        logger.error(f"添加插件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/plugins/upload', methods=['POST'])
@require_auth
def upload_plugin():
    """上传插件脚本并添加插件配置"""
    try:
        from werkzeug.utils import secure_filename
        import os
        
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "error": "没有上传文件"
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                "success": False,
                "error": "没有选择文件"
            }), 400
        
        if file and file.filename.endswith('.py'):
            filename = secure_filename(file.filename)
            plugin_name = os.path.splitext(filename)[0]  # 文件名作为插件名
            
            # 设置目标目录
            script_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'subscribe', 'scripts')
            if not os.path.exists(script_dir):
                os.makedirs(script_dir)
            
            file_path = os.path.join(script_dir, filename)
            file.save(file_path)
            
            # 获取其他参数
            name = request.form.get('name', plugin_name)
            description = request.form.get('description', f'{name} 插件')
            module_path = request.form.get('module_path', f'subscribe.scripts.{name}')
            function_name = request.form.get('function_name', 'main')
            enabled = request.form.get('enabled', 'true').lower() == 'true'
            schedule = request.form.get('schedule', '')
            parameters_str = request.form.get('parameters', '{}')
            
            try:
                import json
                parameters = json.loads(parameters_str)
            except:
                parameters = {}
            
            # 创建插件配置
            try:
                import inspect
                plugin_config_class = getattr(plugin_manager.__class__, 'PluginConfig', None)
                if plugin_config_class and inspect.isclass(plugin_config_class):
                    plugin_config = plugin_config_class(
                        name=name,
                        module_path=module_path,
                        function_name=function_name,
                        enabled=enabled,
                        cron_schedule=schedule,
                        parameters=parameters,
                        timeout=int(request.form.get('timeout', 300)),
                        max_retries=int(request.form.get('max_retries', 3))
                    )
                else:
                    # 创建一个简单的配置对象
                    class SimplePluginConfig:
                        def __init__(self, **kwargs):
                            for k, v in kwargs.items():
                                setattr(self, k, v)
                    plugin_config = SimplePluginConfig(
                        name=name,
                        module_path=module_path,
                        function_name=function_name,
                        enabled=enabled,
                        cron_schedule=schedule,
                        parameters=parameters,
                        timeout=int(request.form.get('timeout', 300)),
                        max_retries=int(request.form.get('max_retries', 3))
                    )
            except:
                # 如果以上都不行，使用字典形式
                plugin_config = {
                    'name': name,
                    'module_path': module_path,
                    'function_name': function_name,
                    'enabled': enabled,
                    'cron_schedule': schedule,
                    'parameters': parameters,
                    'timeout': int(request.form.get('timeout', 300)),
                    'max_retries': int(request.form.get('max_retries', 3))
                }
            
            # 动态添加描述
            if isinstance(plugin_config, dict):
                plugin_config['description'] = description
            else:
                setattr(plugin_config, 'description', description)
            
            plugin_manager.plugins[name] = plugin_config
            
            # 保存配置
            plugin_manager._save_plugin_config()
            
            return jsonify({
                "success": True,
                "message": f"插件 {name} 已上传并添加"
            })
        else:
            return jsonify({
                "success": False,
                "error": "只支持上传Python文件(.py)"
            }), 400
    except Exception as e:
        logger.error(f"上传插件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/plugins/<plugin_name>/delete', methods=['DELETE'])
@require_auth
def delete_plugin(plugin_name):
    """删除插件"""
    try:
        if plugin_name in plugin_manager.plugins:
            del plugin_manager.plugins[plugin_name]
            
            # 从配置文件中移除
            plugin_manager._save_plugin_config()
            
            return jsonify({
                "success": True,
                "message": f"插件 {plugin_name} 已删除"
            })
        else:
            return jsonify({
                "success": False,
                "error": "插件不存在"
            }), 404
    except Exception as e:
        logger.error(f"删除插件失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/config/plugin', methods=['GET'])
@require_auth
def get_plugin_config_protected():
    return get_plugin_config()

@app.route('/api/config/plugin', methods=['PUT'])
@require_auth
def update_plugin_config_protected():
    return update_plugin_config()

@app.route('/api/config/system', methods=['GET'])
@require_auth
def get_system_config_protected():
    return get_system_config()

@app.route('/api/config/system', methods=['PUT'])
@require_auth
def update_system_config_protected():
    return update_system_config()

@app.route('/api/status', methods=['GET'])
@require_auth
def get_status_protected():
    return get_status()

@app.route('/api/logs', methods=['GET'])
@require_auth
def get_logs_protected():
    return get_logs()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)