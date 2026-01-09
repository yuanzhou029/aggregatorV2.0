# 插件生成器使用指南

## 概述

插件生成器是一个用于快速创建插件模板和配置的工具，它可以帮助开发者快速生成符合规范的插件脚本和配置。

## 使用方法

### 命令行参数

```bash
python tools/plugin_generator.py <插件名称> [选项]
```

参数说明：

- `<插件名称>`：必填，插件的名称
- `-d, --description`：可选，插件的描述
- `-e, --enable`：可选，创建后立即启用插件
- `--add-to-config`：可选，将插件配置添加到主配置文件

### 示例

#### 1. 创建基本插件

```bash
python tools/plugin_generator.py my_custom_plugin
```

#### 2. 创建带描述的插件

```bash
python tools/plugin_generator.py my_plugin -d "我的自定义插件"
```

#### 3. 创建并启用插件

```bash
python tools/plugin_generator.py my_plugin -d "我的插件" -e --add-to-config
```

## 生成的文件结构

插件生成器会创建以下文件：

1. **插件脚本文件**：`subscribe/scripts/<插件名称>.py`
2. **配置项**：添加到 `config/plugin_config.json`

## 插件模板结构

生成的插件模板包含以下内容：

```python
def main(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    插件主函数
    """
    # 插件逻辑实现
    pass
```

### 模板特点

1. **标准接口**：遵循统一的插件接口规范
2. **错误处理**：包含完整的异常处理机制
3. **日志记录**：集成日志记录功能
4. **参数处理**：支持灵活的参数配置
5. **返回格式**：统一的返回数据格式

## 配置参数

生成的插件配置包括：

- `module_path`：模块路径
- `function_name`：主函数名
- `enabled`：是否启用
- `cron_schedule`：定时执行配置
- `parameters`：默认参数配置
- `timeout`：执行超时时间
- `max_retries`：最大重试次数

## 自定义插件

创建插件后，可以根据需要修改：

1. 修改 `main` 函数实现具体的业务逻辑
2. 调整 `parameters` 参数配置
3. 修改 `cron_schedule` 定时执行规则
4. 调整 `timeout` 和 `max_retries` 参数

## 最佳实践

1. **命名规范**：插件名称使用小写字母和下划线
2. **参数设计**：设计合理的参数配置项
3. **错误处理**：妥善处理各种异常情况
4. **日志记录**：记录关键操作和错误信息
5. **资源管理**：及时释放占用的资源

## 注意事项

1. 插件名称不能包含特殊字符
2. 确保插件依赖的库已安装
3. 遵循插件接口规范
4. 测试插件功能后再正式启用

## 故障排除

如果遇到问题：

1. 检查插件名称是否已存在
2. 验证插件代码语法是否正确
3. 确认依赖库是否已安装
4. 查看日志文件获取更多信息