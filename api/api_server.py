"""
API接口实现用于前端UI与后端插件系统的交互
"""
import json
import os
import hashlib
import secrets
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import threading
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, Any

# 导入插件管理器
from plugin_manager.manager import PluginManager
from subscribe.logger import setup_logger

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置文件路径
CONFIG_PATH = './config/plugin_config.json'

# 身份验证配置
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', hashlib.sha256(b'admin123').hexdigest())
SESSION_TIMEOUT = 3600  # 1小时

# 简单的会话存储
sessions = {}

# 初始化插件管理器
plugin_manager = PluginManager()
logger = setup_logger()

@app.route('/api/plugins', methods=['GET'])
def get_plugins():
    """获取所有插件列表及状态"""
    try:
        plugins = plugin_manager.get_all_plugins()
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
        plugin = plugin_manager.get_plugin_info(plugin_name)
        if plugin:
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
        success = plugin_manager.run_plugin(plugin_name)
        if success:
            return jsonify({
                "success": True,
                "message": f"插件 {plugin_name} 已启动执行"
            })
        else:
            return jsonify({
                "success": False,
                "error": "执行插件失败"
            }), 400
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
        success = plugin_manager.update_plugin_config(plugin_name, data)
        if success:
            return jsonify({
                "success": True,
                "message": f"插件 {plugin_name} 配置已更新"
            })
        else:
            return jsonify({
                "success": False,
                "error": "更新插件配置失败"
            }), 400
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
        plugins = plugin_manager.get_all_plugins()
        active_plugins = [p for p in plugins if p.get('enabled', False)]
        total_plugins = len(plugins)
        active_count = len(active_plugins)
        
        return jsonify({
            "success": True,
            "data": {
                "total_plugins": total_plugins,
                "active_plugins": active_count,
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
        data = request.get_json()
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
app.add_url_rule('/api/plugins', 'get_plugins', require_auth(get_plugins), methods=['GET'])
app.add_url_rule('/api/plugins/<plugin_name>', 'get_plugin', require_auth(get_plugin), methods=['GET'])
app.add_url_rule('/api/plugins/<plugin_name>/enable', 'enable_plugin', require_auth(enable_plugin), methods=['POST'])
app.add_url_rule('/api/plugins/<plugin_name>/disable', 'disable_plugin', require_auth(disable_plugin), methods=['POST'])
app.add_url_rule('/api/plugins/<plugin_name>/run', 'run_plugin', require_auth(run_plugin), methods=['POST'])
app.add_url_rule('/api/plugins/<plugin_name>', 'update_plugin', require_auth(update_plugin), methods=['PUT'])
app.add_url_rule('/api/config/plugin', 'get_plugin_config', require_auth(get_plugin_config), methods=['GET'])
app.add_url_rule('/api/config/plugin', 'update_plugin_config', require_auth(update_plugin_config), methods=['PUT'])
app.add_url_rule('/api/config/system', 'get_system_config', require_auth(get_system_config), methods=['GET'])
app.add_url_rule('/api/config/system', 'update_system_config', require_auth(update_system_config), methods=['PUT'])
app.add_url_rule('/api/status', 'get_status', require_auth(get_status), methods=['GET'])
app.add_url_rule('/api/logs', 'get_logs', require_auth(get_logs), methods=['GET'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)