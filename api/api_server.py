"""
API接口实现用于前端UI与后端插件系统的交互
"""

from subscribe.logger import logger
from plugin_manager.manager import (
    PluginManager,
    plugin_manager as global_plugin_manager,
)
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
import jsonschema
from typing import Dict, Any

# 限流相关
from collections import defaultdict

# 导入插件管理器
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False  # 保持JSON键的顺序
CORS(
    app, supports_credentials=True, allow_headers=["Content-Type", "Authorization"]
)  # 允许跨域请求

# 配置文件路径
CONFIG_PATH = "./config/plugin_config.json"

# 身份验证配置
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
# 使用带盐值的哈希
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))


def hash_password(password: str) -> str:
    """使用密钥哈希密码"""
    return hashlib.sha256(f"{password}{SECRET_KEY}".encode()).hexdigest()


ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", hash_password(ADMIN_PASSWORD))
SESSION_TIMEOUT = 3600  # 1小时

# 简单的会话存储
sessions = {}

# 缓存存储
cache = {}
CACHE_TIMEOUT = 30  # 缓存超时时间（秒）

# 限流配置
RATE_LIMITS = {
    "login": {"max_requests": 5, "window": 300},  # 5分钟内最多5次登录尝试
    "default": {"max_requests": 100, "window": 60},  # 1分钟内最多100次请求
}

# 限流存储
rate_limit_storage = defaultdict(list)

# 系统启动时间
SYSTEM_START_TIME = datetime.now()

# 使用全局插件管理器实例
plugin_manager = global_plugin_manager
# logger实例已经从subscribe.logger导入，无需重新定义
# logger = logger


# 身份验证装饰器
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify(
                {"success": False, "error": "Missing or invalid authorization header"}
            ), 401

        session_token = auth_header.split(" ")[1]
        if session_token not in sessions:
            return jsonify(
                {"success": False, "error": "Session expired or invalid"}
            ), 401

        session_data = sessions[session_token]
        if time.time() - session_data["timestamp"] > SESSION_TIMEOUT:
            del sessions[session_token]
            return jsonify({"success": False, "error": "Session expired"}), 401

        # 更新会话时间戳
        session_data["timestamp"] = time.time()
        return f(*args, **kwargs)

    return decorated_function


# 适配插件管理器的接口
# 为插件管理器创建适配器，处理不同类型的插件配置
def get_all_plugins_adaptor():
    plugins = []
    for name, config in plugin_manager.plugins.items():
        # 检查配置是数据类对象还是字典
        if hasattr(config, "name"):
            # 这是一个PluginConfig对象
            plugin_info = {
                "name": getattr(config, "name", name),
                "description": getattr(config, "description", f"{name} 插件"),
                "enabled": getattr(config, "enabled", False),
                "status": "running"
                if name in getattr(plugin_manager, "running_plugins", [])
                else "idle",
                "schedule": getattr(config, "cron_schedule", ""),
                "parameters": getattr(config, "parameters", {}),
            }
        else:
            # 这是一个字典配置
            plugin_info = {
                "name": config.get("name", name),
                "description": config.get("description", f"{name} 插件"),
                "enabled": config.get("enabled", config.get("enable", True)),
                "status": "running"
                if name in getattr(plugin_manager, "running_plugins", [])
                else "idle",
                "schedule": config.get("schedule", config.get("cron_schedule", "")),
                "parameters": config.get("parameters", {}),
            }
        plugins.append(plugin_info)
    return plugins


def get_running_tasks_count():
    """获取当前运行的任务数"""
    # 获取插件管理器中的运行中插件数量
    running_count = 0
    if hasattr(plugin_manager, "running_plugins"):
        running_count = len(plugin_manager.running_plugins)
    else:
        # 如果插件管理器没有跟踪运行中的插件，则检查Python进程中是否有运行中的插件
        for proc in psutil.process_iter():
            try:
                if (
                    "python" in proc.name().lower()
                    and "plugin" in " ".join(proc.cmdline()).lower()
                ):
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


def validate_plugin_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """验证插件配置是否符合规范"""
    schema = {
        "type": "object",
        "properties": {
            "module_path": {"type": "string", "minLength": 1},
            "function_name": {"type": "string", "minLength": 1},
            "enabled": {"type": "boolean"},
            "cron_schedule": {"type": "string"},
            "parameters": {"type": "object"},
            "timeout": {"type": "number", "minimum": 1},
            "max_retries": {"type": "number", "minimum": 0},
        },
        "required": ["module_path", "function_name", "enabled"],
    }

    try:
        jsonschema.validate(config, schema)
        return True, "配置验证通过"
    except jsonschema.ValidationError as e:
        return False, f"配置验证失败: {e.message}"


def validate_system_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """验证系统配置是否符合规范"""
    schema = {
        "type": "object",
        "properties": {
            "env_vars": {
                "type": "object",
                "properties": {
                    "GIST_PAT": {"type": "string"},
                    "GIST_LINK": {"type": "string"},
                    "CUSTOMIZE_LINK": {"type": "string"},
                    "ADMIN_USERNAME": {"type": "string"},
                    "TZ": {"type": "string"},
                    "ADMIN_PASSWORD": {"type": "string"},
                    "API_PORT": {"type": "number", "minimum": 1, "maximum": 65535},
                    "WEB_PORT": {"type": "number", "minimum": 1, "maximum": 65535},
                },
            },
            "storage_type": {"type": "string", "enum": ["local", "gist"]},
            "version": {"type": "string"},
            "api_port": {"type": "number", "minimum": 1, "maximum": 65535},
            "web_port": {"type": "number", "minimum": 1, "maximum": 65535},
        },
    }

    try:
        jsonschema.validate(config, schema)
        return True, "配置验证通过"
    except jsonschema.ValidationError as e:
        return False, f"配置验证失败: {e.message}"


def get_cache_key(endpoint: str, params: Dict = None) -> str:
    """生成缓存键"""
    key_str = f"{endpoint}:{str(params or {})}"
    return hashlib.sha256(key_str.encode()).hexdigest()


def get_cached_data(key: str) -> tuple[bool, any]:
    """获取缓存数据"""
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < CACHE_TIMEOUT:
            return True, data
        else:
            # 缓存过期，删除它
            del cache[key]
    return False, None


def set_cached_data(key: str, data: any):
    """设置缓存数据"""
    cache[key] = (data, time.time())


def is_rate_limited(identifier: str, limit_type: str = "default") -> tuple[bool, int]:
    """检查是否超出请求限制"""
    now = time.time()
    window = RATE_LIMITS[limit_type]["window"]
    max_requests = RATE_LIMITS[limit_type]["max_requests"]

    # 清理过期的请求记录
    rate_limit_storage[identifier] = [
        req_time
        for req_time in rate_limit_storage[identifier]
        if now - req_time < window
    ]

    # 检查是否超过限制
    if len(rate_limit_storage[identifier]) >= max_requests:
        # 计算剩余时间
        oldest_req = min(rate_limit_storage[identifier])
        reset_time = int(oldest_req + window)
        return True, reset_time

    # 添加当前请求记录
    rate_limit_storage[identifier].append(now)
    return False, 0


def rate_limit(limit_type: str = "default"):
    """限流装饰器"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 使用IP地址作为标识符
            ip_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
            is_limited, reset_time = is_rate_limited(ip_addr, limit_type)

            if is_limited:
                reset_in = reset_time - int(time.time())
                return jsonify(
                    {
                        "success": False,
                        "error": f"请求过于频繁，请在 {reset_in} 秒后重试",
                        "reset_time": reset_time,
                    }
                ), 429

            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route("/api/plugins", methods=["GET"])
@require_auth
def get_plugins():
    """获取所有插件列表及状态"""
    try:
        # 检查缓存
        cache_key = get_cache_key("/api/plugins", {})
        is_cached, cached_data = get_cached_data(cache_key)
        if is_cached:
            return jsonify(cached_data)

        plugins = get_all_plugins_adaptor()
        response_data = {"success": True, "data": plugins}

        # 设置缓存
        set_cached_data(cache_key, response_data)

        return jsonify(response_data)
    except Exception as e:
        logger.error(f"获取插件列表失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/<plugin_name>", methods=["GET"])
def get_plugin(plugin_name):
    """获取特定插件信息"""
    try:
        if plugin_name in plugin_manager.plugins:
            config = plugin_manager.plugins[plugin_name]
            # 根据配置类型获取属性值
            if hasattr(config, "__dict__"):  # 对象类型
                description = getattr(config, "description", f"{plugin_name} 插件")
                enabled = getattr(config, "enabled", False)
                schedule = getattr(config, "cron_schedule", "")
                parameters = getattr(config, "parameters", {})
            else:  # 字典类型
                description = config.get("description", f"{plugin_name} 插件")
                enabled = config.get("enabled", config.get("enable", True))
                schedule = config.get("schedule", config.get("cron_schedule", ""))
                parameters = config.get("parameters", {})

            plugin = {
                "name": plugin_name,
                "description": description,
                "enabled": enabled,
                "status": "空闲",
                "schedule": schedule,
                "parameters": parameters,
            }
            return jsonify({"success": True, "data": plugin})
        else:
            return jsonify({"success": False, "error": "插件不存在"}), 404
    except Exception as e:
        logger.error(f"获取插件信息失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/<plugin_name>/enable", methods=["POST"])
def enable_plugin(plugin_name):
    """启用插件"""
    try:
        success = plugin_manager.enable_plugin(plugin_name)
        if success:
            # 清除相关缓存
            cache_key = get_cache_key("/api/plugins", {})
            if cache_key in cache:
                del cache[cache_key]

            cache_status_key = get_cache_key("/api/status", {})
            if cache_status_key in cache:
                del cache[cache_status_key]

            return jsonify({"success": True, "message": f"插件 {plugin_name} 已启用"})
        else:
            return jsonify({"success": False, "error": "启用插件失败"}), 400
    except Exception as e:
        logger.error(f"启用插件失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/<plugin_name>/disable", methods=["POST"])
def disable_plugin(plugin_name):
    """禁用插件"""
    try:
        success = plugin_manager.disable_plugin(plugin_name)
        if success:
            # 清除相关缓存
            cache_key = get_cache_key("/api/plugins", {})
            if cache_key in cache:
                del cache[cache_key]

            cache_status_key = get_cache_key("/api/status", {})
            if cache_status_key in cache:
                del cache[cache_status_key]

            return jsonify({"success": True, "message": f"插件 {plugin_name} 已禁用"})
        else:
            return jsonify({"success": False, "error": "禁用插件失败"}), 400
    except Exception as e:
        logger.error(f"禁用插件失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/<plugin_name>/run", methods=["POST"])
def run_plugin(plugin_name):
    """立即执行插件"""
    try:
        if plugin_name in plugin_manager.plugins:
            result = plugin_manager.execute_plugin(plugin_name)
            if result is not None:
                return jsonify(
                    {"success": True, "message": f"插件 {plugin_name} 已执行完成"}
                )
            else:
                return jsonify({"success": False, "error": "执行插件失败"}), 400
        else:
            return jsonify({"success": False, "error": "插件不存在"}), 404
    except Exception as e:
        logger.error(f"执行插件失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/<plugin_name>", methods=["PUT"])
def update_plugin(plugin_name):
    """更新插件配置"""
    try:
        data = request.get_json()
        if plugin_name in plugin_manager.plugins:
            # 更新插件配置
            plugin_config = plugin_manager.plugins[plugin_name]

            # 根据配置类型更新相应字段
            if hasattr(plugin_config, "__dict__"):  # 对象类型
                if "enabled" in data:
                    plugin_config.enabled = data["enabled"]
                if "schedule" in data:
                    plugin_config.cron_schedule = data["schedule"]
                if "parameters" in data:
                    plugin_config.parameters = data["parameters"]
                if "description" in data:
                    plugin_config.description = data["description"]
                if "module_path" in data:
                    plugin_config.module_path = data["module_path"]
                if "function_name" in data:
                    plugin_config.function_name = data["function_name"]
            else:  # 字典类型
                if "enabled" in data:
                    plugin_config["enabled"] = data["enabled"]
                if "schedule" in data:
                    plugin_config["cron_schedule"] = data["schedule"]
                if "parameters" in data:
                    plugin_config["parameters"] = data["parameters"]
                if "description" in data:
                    plugin_config["description"] = data["description"]
                if "module_path" in data:
                    plugin_config["module_path"] = data["module_path"]
                if "function_name" in data:
                    plugin_config["function_name"] = data["function_name"]

            # 保存配置
            plugin_manager._save_plugin_config()

            # 清除相关缓存
            cache_key = get_cache_key("/api/plugins", {})
            if cache_key in cache:
                del cache[cache_key]

            cache_status_key = get_cache_key("/api/status", {})
            if cache_status_key in cache:
                del cache[cache_status_key]

            return jsonify(
                {"success": True, "message": f"插件 {plugin_name} 配置已更新"}
            )
        else:
            return jsonify({"success": False, "error": "插件不存在"}), 404
    except Exception as e:
        logger.error(f"更新插件配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config/plugin", methods=["GET"])
def get_plugin_config():
    """获取插件配置"""
    try:
        # 直接读取配置文件
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return jsonify({"success": True, "data": config})
    except FileNotFoundError:
        logger.error("插件配置文件不存在")
        return jsonify({"success": False, "error": "插件配置文件不存在"}), 404
    except Exception as e:
        logger.error(f"获取插件配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config/plugin", methods=["PUT"])
def update_plugin_config():
    """更新插件配置"""
    try:
        data = request.get_json()
        # 写入配置文件
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 更新插件管理器的配置，保留原有的对象类型
        new_plugins = {}
        for name, config in data.get("plugins", {}).items():
            # 将字典配置转换为对象（如果尚未转换）
            if isinstance(config, dict):
                plugin_config = PluginConfig(
                    name=name,
                    module_path=config.get("module_path", ""),
                    function_name=config.get("function_name", "main"),
                    enabled=config.get("enabled", config.get("enable", True)),
                    cron_schedule=config.get(
                        "cron_schedule", config.get("schedule", "")
                    ),
                    parameters=config.get("parameters", {}),
                    timeout=config.get("timeout", 300),
                    max_retries=config.get("max_retries", 3),
                    description=config.get("description", f"{name} 插件"),
                )
                new_plugins[name] = plugin_config
            else:
                new_plugins[name] = config
        plugin_manager.plugins = new_plugins

        return jsonify({"success": True, "message": "插件配置已更新"})
    except Exception as e:
        logger.error(f"更新插件配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/status", methods=["GET"])
def get_status():
    """获取系统整体状态"""
    try:
        # 检查缓存
        cache_key = get_cache_key("/api/status", {})
        is_cached, cached_data = get_cached_data(cache_key)
        if is_cached:
            return jsonify(cached_data)

        plugins = get_all_plugins_adaptor()
        active_plugins = [p for p in plugins if p.get("enabled", False)]
        total_plugins = len(plugins)
        active_count = len(active_plugins)
        running_tasks = get_running_tasks_count()
        system_uptime = get_system_uptime()

        response_data = {
            "success": True,
            "data": {
                "total_plugins": total_plugins,
                "active_plugins": active_count,
                "running_tasks": running_tasks,
                "system_uptime": system_uptime,
                "last_update": datetime.now().isoformat(),
                "plugins": plugins,
            },
        }

        # 设置缓存
        set_cached_data(cache_key, response_data)

        return jsonify(response_data)
    except Exception as e:
        logger.error(f"获取系统状态失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/logs", methods=["GET"])
def get_logs():
    """获取系统日志（简化实现）"""
    try:
        # 这里简化实现，实际应从日志文件中读取
        logs = [
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "系统启动",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": "插件管理器初始化完成",
            },
        ]
        return jsonify({"success": True, "data": logs})
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config/system", methods=["GET"])
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
                "GIST_PAT": os.getenv("GIST_PAT", ""),
                "GIST_LINK": os.getenv("GIST_LINK", ""),
                "CUSTOMIZE_LINK": os.getenv("CUSTOMIZE_LINK", ""),
                "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME", "admin"),
                "TZ": os.getenv("TZ", "Asia/Shanghai"),
            },
        }
        return jsonify({"success": True, "data": system_config})
    except Exception as e:
        logger.error(f"获取系统配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config/system", methods=["PUT"])
def update_system_config():
    """更新系统配置"""
    try:
        data = request.get_json()
        env_vars = data.get("env_vars", {})

        # 更新环境变量（这里仅作示例，实际在容器中需要持久化）
        if "GIST_PAT" in env_vars:
            os.environ["GIST_PAT"] = env_vars["GIST_PAT"]
        if "GIST_LINK" in env_vars:
            os.environ["GIST_LINK"] = env_vars["GIST_LINK"]
        if "CUSTOMIZE_LINK" in env_vars:
            os.environ["CUSTOMIZE_LINK"] = env_vars["CUSTOMIZE_LINK"]
        if "ADMIN_USERNAME" in env_vars:
            os.environ["ADMIN_USERNAME"] = env_vars["ADMIN_USERNAME"]
        if "TZ" in env_vars:
            os.environ["TZ"] = env_vars["TZ"]

        # 如果提供了新的密码，更新密码哈希
        if "ADMIN_PASSWORD" in env_vars and env_vars["ADMIN_PASSWORD"]:
            new_password_hash = hashlib.sha256(
                env_vars["ADMIN_PASSWORD"].encode()
            ).hexdigest()
            os.environ["ADMIN_PASSWORD_HASH"] = new_password_hash

        return jsonify({"success": True, "message": "系统配置已更新"})
    except Exception as e:
        logger.error(f"更新系统配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
@rate_limit("login")
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
            if content_type and "application/json" in content_type:
                try:
                    import json as std_json

                    data = std_json.loads(request.get_data(as_text=True))
                except Exception as e:
                    logger.warning(f"Failed to parse JSON from request data: {str(e)}")

        if data is None:
            return jsonify(
                {"success": False, "error": "No valid JSON data provided"}
            ), 400

        username = data.get("username")
        password = data.get("password")

        # 验证用户名和密码
        password_hash = hash_password(password)
        if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
            # 创建会话令牌
            session_token = secrets.token_hex(32)
            sessions[session_token] = {
                "username": username,
                "timestamp": time.time(),
                "role": "admin",
            }

            return jsonify(
                {"success": True, "token": session_token, "message": "Login successful"}
            )
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/logout", methods=["POST"])
@require_auth
def logout():
    """用户登出"""
    try:
        auth_header = request.headers.get("Authorization")
        session_token = auth_header.split(" ")[1]

        if session_token in sessions:
            del sessions[session_token]

        return jsonify({"success": True, "message": "Logout successful"})
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/<plugin_name>/validate", methods=["POST"])
@require_auth
def validate_plugin_config_api(plugin_name):
    """验证插件配置"""
    try:
        data = request.get_json()
        is_valid, message = validate_plugin_config(data)
        return jsonify({"success": is_valid, "message": message})
    except Exception as e:
        logger.error(f"验证插件配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/<plugin_name>/status", methods=["GET"])
@require_auth
def get_plugin_status(plugin_name):
    """获取单个插件状态"""
    try:
        if plugin_name in plugin_manager.plugins:
            config = plugin_manager.plugins[plugin_name]
            # 根据配置类型获取属性值
            if hasattr(config, "__dict__"):  # 对象类型
                description = getattr(config, "description", f"{plugin_name} 插件")
                enabled = getattr(config, "enabled", False)
                schedule = getattr(config, "cron_schedule", "")
                parameters = getattr(config, "parameters", {})
                module_path = getattr(config, "module_path", "")
                function_name = getattr(config, "function_name", "main")
            else:  # 字典类型
                description = config.get("description", f"{plugin_name} 插件")
                enabled = config.get("enabled", config.get("enable", True))
                schedule = config.get("schedule", config.get("cron_schedule", ""))
                parameters = config.get("parameters", {})
                module_path = config.get("module_path", "")
                function_name = config.get("function_name", "main")

            plugin = {
                "name": plugin_name,
                "description": description,
                "enabled": enabled,
                "status": "running"
                if plugin_name in getattr(plugin_manager, "running_plugins", [])
                else "idle",
                "schedule": schedule,
                "parameters": parameters,
                "module_path": module_path,
                "function_name": function_name,
            }
            return jsonify({"success": True, "data": plugin})
        else:
            return jsonify({"success": False, "error": "插件不存在"}), 404
    except Exception as e:
        logger.error(f"获取插件状态失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


# 添加插件管理的新API
@app.route("/api/plugins/add", methods=["POST"])
@require_auth
def add_plugin():
    """添加插件"""
    try:
        data = request.get_json()
        plugin_name = data.get("name")
        description = data.get("description", f"{plugin_name} 插件")
        module_path = data.get("module_path", f"subscribe.scripts.{plugin_name}")
        function_name = data.get("function_name", "main")
        enabled = data.get("enabled", True)
        schedule = data.get("schedule", "")
        parameters = data.get("parameters", {})

        # 创建插件配置
        from dataclasses import fields

        try:
            # 检查PluginManager是否具有正确的PluginConfig类
            import inspect

            plugin_config_class = getattr(
                plugin_manager.__class__, "PluginConfig", None
            )
            if plugin_config_class and inspect.isclass(plugin_config_class):
                plugin_config = plugin_config_class(
                    name=plugin_name,
                    module_path=module_path,
                    function_name=function_name,
                    enabled=enabled,
                    cron_schedule=schedule,
                    parameters=parameters,
                    timeout=data.get("timeout", 300),
                    max_retries=data.get("max_retries", 3),
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
                    timeout=data.get("timeout", 300),
                    max_retries=data.get("max_retries", 3),
                )
        except Exception as e:
            logger.warning(
                f"Failed to create PluginConfig object, falling back to dict: {str(e)}"
            )
            # 如果以上都不行，使用字典形式
            plugin_config = {
                "name": plugin_name,
                "module_path": module_path,
                "function_name": function_name,
                "enabled": enabled,
                "cron_schedule": schedule,
                "parameters": parameters,
                "timeout": data.get("timeout", 300),
                "max_retries": data.get("max_retries", 3),
            }

        # 动态添加描述
        if isinstance(plugin_config, dict):
            plugin_config["description"] = description
        else:
            setattr(plugin_config, "description", description)

        plugin_manager.plugins[plugin_name] = plugin_config

        # 保存配置
        plugin_manager._save_plugin_config()

        # 清除相关缓存
        cache_key = get_cache_key("/api/plugins", {})
        if cache_key in cache:
            del cache[cache_key]

        cache_status_key = get_cache_key("/api/status", {})
        if cache_status_key in cache:
            del cache[cache_status_key]

        return jsonify({"success": True, "message": f"插件 {plugin_name} 已添加"})
    except Exception as e:
        logger.error(f"添加插件失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/upload", methods=["POST"])
@require_auth
def upload_plugin():
    """上传插件脚本并添加插件配置"""
    try:
        from werkzeug.utils import secure_filename
        import os

        # 检查是否有文件上传
        if "file" not in request.files:
            return jsonify({"success": False, "error": "没有上传文件"}), 400

        file = request.files["file"]

        # 检查文件名
        if file.filename == "":
            return jsonify({"success": False, "error": "没有选择文件"}), 400

        if file and file.filename.endswith(".py"):
            filename = secure_filename(file.filename)
            plugin_name = os.path.splitext(filename)[0]  # 文件名作为插件名

            # 设置目标目录
            script_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "subscribe", "scripts"
            )
            if not os.path.exists(script_dir):
                os.makedirs(script_dir)

            file_path = os.path.join(script_dir, filename)
            file.save(file_path)

            # 获取其他参数
            name = request.form.get("name", plugin_name)
            description = request.form.get("description", f"{name} 插件")
            module_path = request.form.get("module_path", f"subscribe.scripts.{name}")
            function_name = request.form.get("function_name", "main")
            enabled = request.form.get("enabled", "true").lower() == "true"
            schedule = request.form.get("schedule", "")
            parameters_str = request.form.get("parameters", "{}")

            try:
                import json

                parameters = json.loads(parameters_str)
            except json.JSONDecodeError as e:
                logger.warning(
                    f"Failed to parse parameters JSON: {str(e)}, using empty dict"
                )
                parameters = {}

            # 创建插件配置
            try:
                import inspect

                plugin_config_class = getattr(
                    plugin_manager.__class__, "PluginConfig", None
                )
                if plugin_config_class and inspect.isclass(plugin_config_class):
                    plugin_config = plugin_config_class(
                        name=name,
                        module_path=module_path,
                        function_name=function_name,
                        enabled=enabled,
                        cron_schedule=schedule,
                        parameters=parameters,
                        timeout=int(request.form.get("timeout", 300)),
                        max_retries=int(request.form.get("max_retries", 3)),
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
                        timeout=int(request.form.get("timeout", 300)),
                        max_retries=int(request.form.get("max_retries", 3)),
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to create SimplePluginConfig, falling back to dict: {str(e)}"
                )
                # 如果以上都不行，使用字典形式
                plugin_config = {
                    "name": name,
                    "module_path": module_path,
                    "function_name": function_name,
                    "enabled": enabled,
                    "cron_schedule": schedule,
                    "parameters": parameters,
                    "timeout": int(request.form.get("timeout", 300)),
                    "max_retries": int(request.form.get("max_retries", 3)),
                }

            # 动态添加描述
            if isinstance(plugin_config, dict):
                plugin_config["description"] = description
            else:
                setattr(plugin_config, "description", description)

            plugin_manager.plugins[name] = plugin_config

            # 保存配置
            plugin_manager._save_plugin_config()

            # 清除相关缓存
            cache_key = get_cache_key("/api/plugins", {})
            if cache_key in cache:
                del cache[cache_key]

            cache_status_key = get_cache_key("/api/status", {})
            if cache_status_key in cache:
                del cache[cache_status_key]

            return jsonify({"success": True, "message": f"插件 {name} 已上传并添加"})
        else:
            return jsonify(
                {"success": False, "error": "只支持上传Python文件(.py)"}
            ), 400
    except Exception as e:
        logger.error(f"上传插件失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/plugins/<plugin_name>/delete", methods=["DELETE"])
@require_auth
def delete_plugin(plugin_name):
    """删除插件"""
    try:
        if plugin_name in plugin_manager.plugins:
            # 删除插件对应的脚本文件
            script_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "subscribe", "scripts"
            )
            script_path = os.path.join(script_dir, f"{plugin_name}.py")

            if os.path.exists(script_path):
                os.remove(script_path)
                logger.info(f"已删除插件脚本文件: {script_path}")

            del plugin_manager.plugins[plugin_name]

            # 从配置文件中移除
            plugin_manager._save_plugin_config()

            # 清除相关缓存
            cache_key = get_cache_key("/api/plugins", {})
            if cache_key in cache:
                del cache[cache_key]

            cache_status_key = get_cache_key("/api/status", {})
            if cache_status_key in cache:
                del cache[cache_status_key]

            return jsonify({"success": True, "message": f"插件 {plugin_name} 已删除"})
        else:
            return jsonify({"success": False, "error": "插件不存在"}), 404
    except Exception as e:
        logger.error(f"删除插件失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/config/system/validate", methods=["POST"])
@require_auth
def validate_system_config_api():
    """验证系统配置"""
    try:
        data = request.get_json()
        is_valid, message = validate_system_config(data)
        return jsonify({"success": is_valid, "message": message})
    except Exception as e:
        logger.error(f"验证系统配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
