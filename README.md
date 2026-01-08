# Aggregator - 免费代理池构建工具

[![GitHub stars](https://img.shields.io/github/stars/wzdnzd/aggregator.svg)](https://github.com/wzdnzd/aggregator/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wzdnzd/aggregator.svg)](https://github.com/wzdnzd/aggregator/network)
[![GitHub issues](https://img.shields.io/github/issues/wzdnzd/aggregator.svg)](https://github.com/wzdnzd/aggregator/issues)
[![License](https://img.shields.io/github/license/wzdnzd/aggregator.svg)](https://github.com/wzdnzd/aggregator/blob/main/LICENSE)
[![Docker Image Version](https://ghcr.io/wzdnzd/aggregator/badge)](https://ghcr.io/wzdnzd/aggregator)

## 🎯 项目简介

一个强大的免费代理池构建工具，通过爬取多个平台/网页的代理资源，自动验证、聚合并转换为各种客户端所需格式。新版本增加了精细化插件管理系统，可精确控制每个插件的启用/禁用和定时执行。

### ✨ 核心特性

- **🕷️ 多源爬取** - Telegram、GitHub、Google、Yandex、Twitter 等
- **🔍 智能验证** - 自动检测代理活性和质量
- **🔄 格式转换** - 支持 Clash、V2Ray、SingBox 等格式
- **💾 灵活存储** - GitHub Gist、PasteGG、Imperial 等多种后端
- **🔌 插件系统** - 可扩展的自定义爬取架构
- **⚡ 高效处理** - 多线程并发，批量处理
- **⚙️ 精细化管理** - 精确控制每个插件的启用/禁用和定时执行
- **🐳 容器化部署** - 支持Docker及自动构建发布

### 🌐 支持协议
VMess | Trojan | SS | SSR | Snell | Hysteria2 | VLESS | Hysteria | TUIC | AnyTLS | HTTP | SOCKS

## 🚀 快速开始

### 两种使用方式

#### 方式一：process.py（推荐）
**完整功能版本** - 支持复杂配置、多源爬取、自定义规则

```bash
# 1. 准备配置文件
cp subscribe/config/config.default.json my-config.json

# 2. 设置环境变量
export PUSH_TOKEN=your_github_token

# 3. 运行处理
python subscribe/process.py -s my-config.json
```

#### 方式二：collect.py
**简化版本** - 快速收集机场订阅

```bash
# 直接运行，自动收集并上传到 Gist
python subscribe/collect.py \
    -g username/gist-id \
    -k your-github-token \
    -t clash v2ray singbox
```

### 🎁 共享订阅
> 可前往 [Issue #91](https://github.com/wzdnzd/aggregator/issues/91) 获取现成的**共享订阅**，量大质优。**请勿浪费**

## 🔌 插件开发与管理系统

### 精细化插件管理系统
新版本支持精细化插件管理，可精确控制每个插件的启用/禁用和定时执行。

#### 系统概述
精细化插件管理系统允许您精确控制每个插件的启用/禁用和定时执行。系统采用模块化设计，支持插件热加载和动态管理。

#### 目录结构
```
aggregator/
├── plugin_manager/           # 插件管理器
│   ├── __init__.py
│   └── manager.py
├── plugins/                  # 插件目录
│   ├── __init__.py
│   ├── exercises/            # 练习题插件
│   │   ├── __init__.py
│   │   └── math_exercises.py
│   ├── news/                 # 新闻插件
│   │   └── __init__.py
│   └── custom_plugins/       # 自定义插件
│       ├── __init__.py
│       └── my_plugin.py
├── config/
│   └── plugin_config.json    # 插件配置文件
├── plugin_control.py         # 插件控制脚本
└── main_executor.py          # 主执行器
```

#### 基础操作

##### 查看所有插件状态
```bash
python plugin_control.py list
```

##### 启用插件
```bash
python plugin_control.py enable plugin_name
```

##### 禁用插件
```bash
python plugin_control.py disable plugin_name
```

##### 运行插件
```bash
python plugin_control.py run plugin_name
```

##### 查看插件状态
```bash
python plugin_control.py status plugin_name
```

#### 配置文件详解
插件配置文件位于 `config/plugin_config.json`：

```json
{
  "plugins": {
    "plugin_name": {
      "module_path": "plugins.exercises.math_exercises",  // 插件模块路径
      "function_name": "crawl_math_exercises",           // 插件函数名
      "enabled": true,                                   // 启用状态
      "cron_schedule": "0 2 * * *",                     // 定时执行配置
      "parameters": {                                   // 插件参数
        "base_url": "https://example.com",
        "grade": "3",
        "subject": "math"
      },
      "timeout": 300,                                    // 超时时间（秒）
      "max_retries": 3                                   // 最大重试次数
    }
  }
}
```

## 📦 Docker 部署

### 使用预构建镜像

```bash
# 拉取最新镜像
docker pull ghcr.io/你的用户名/aggregator:latest

# 运行容器
docker run -d \
  --name aggregator \
  --restart unless-stopped \
  -e GIST_PAT=your_github_token \
  -e GIST_LINK=your_username/your_gist_id \
  -e CUSTOMIZE_LINK=your_customize_link \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/data:/aggregator/data \
  -v $(pwd)/config:/aggregator/config \
  -v $(pwd)/plugins:/aggregator/plugins \
  ghcr.io/你的用户名/aggregator:latest
```

### 使用 Docker Compose

```yaml
version: '3.8'

services:
  aggregator:
    image: ghcr.io/你的用户名/aggregator:latest  # 使用GitHub Container Registry镜像
    container_name: aggregator
    environment:
      - GIST_PAT=${GIST_PAT:-}
      - GIST_LINK=${GIST_LINK:-}
      - CUSTOMIZE_LINK=${CUSTOMIZE_LINK:-}
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/aggregator/data
      - ./config:/aggregator/config
      - ./plugins:/aggregator/plugins
      - ./plugin_manager:/aggregator/plugin_manager
    restart: unless-stopped
    command: [
      "python", 
      "-u", 
      "main_executor.py"
    ]
```

## 🚀 GitHub自动构建发布

本项目支持使用GitHub Actions自动构建Docker镜像并发布到GitHub Container Registry (ghcr.io)。

### 部署到GitHub

1. **创建GitHub仓库**
   - 登录GitHub并创建新仓库
   - 将本地代码推送至GitHub

2. **启用Package功能**
   - 确保仓库设置允许packages

3. **自动构建触发**
   - 推送代码到main/master分支时自动构建
   - 发布release时自动构建带标签的镜像

### GitHub Actions工作流

项目包含两个工作流：

1. **自动构建** (.github/workflows/docker.yml)
   - 触发条件：推送到main/master分支或PR
   - 构建平台：linux/amd64, linux/arm64
   - 镜像标签：分支名、SHA、latest

2. **发布构建** (.github/workflows/publish-docker.yml)
   - 触发条件：创建新Release
   - 构建平台：linux/amd64
   - 镜像标签：Release标签

### 使用方法

1. **推送代码到GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

2. **创建Release以构建带标签的镜像**
   - 在GitHub仓库页面点击"Releases"
   - 点击"Draft a new release"
   - 设置标签（如v1.0.0）并发布

## 📊 工作流程

```mermaid
graph LR
    A[开始] --> B{选择方式}
    B -->|简单| C[collect.py]
    B -->|完整| D[process.py]
    
    C --> E[自动收集机场]
    E --> F[注册账号]
    F --> G[获取订阅]
    G --> H[验证代理]
    H --> I[上传到Gist]
    
    D --> J[加载配置]
    J --> K[多源爬取]
    K --> L[聚合处理]
    L --> M[质量检测]
    M --> N[格式转换]
    N --> O[推送存储]
```

## ⚡ 快速配置

### 最小配置示例

**process.py 配置**：
```json
{
    "domains": [
        {
            "name": "example-airport",
            "domain": "example.com",
            "push_to": ["free"]
        }
    ],
    "crawl": {
        "enable": true,
        "telegram": {
            "enable": true,
            "users": {
                "proxy_channel": {
                    "push_to": ["free"]
                }
            }
        }
    },
    "groups": {
        "free": {
            "targets": {"clash": "free-clash"}
        }
    },
    "storage": {
        "engine": "gist",
        "items": {
            "free-clash": {
                "username": "your-username",
                "gistid": "your-gist-id", 
                "filename": "clash.yaml"
            }
        }
    }
}
```

**环境变量**：
```bash
export PUSH_TOKEN=your_github_token
```

### 常用命令

```bash
# 快速收集（推荐新手）
python subscribe/collect.py -g username/gist-id -k token

# 完整处理（推荐进阶）
python subscribe/process.py -s config.json

# 仅检查代理活性
python subscribe/process.py -s config.json --check

# 高性能模式
python subscribe/process.py -s config.json -n 128
```


## 📚 相关文档

| 文档                         | 说明            | 适用人群            |
| ---------------------------- | --------------- | ------------------- |
| [完整文档](README_CN.md)     | 详细配置说明    | 进阶用户            |
| [English Docs](README_EN.md) | English version | International users |

## 🔧 常见问题

| 问题         | 解决方案                                   |
| ------------ | ------------------------------------------ |
| 配置文件错误 | `python -m json.tool config.json` 验证语法 |
| Token 无效   | 检查 GitHub Token 权限和有效期             |
| 网络超时     | 增加超时 `-t 15000` 或减少线程 `-n 16`     |
| 无代理输出   | 检查爬取源配置和网络连接                   |

## 🚧 TODO 路线图

### 架构重构
- [ ] **核心接口设计** - 抽象出 `ICrawler`、`IStorage`、`IConverter` 等核心接口
- [ ] **基类实现** - 创建 `BaseCrawler`、`BaseStorage`、`BaseConverter` 抽象基类
- [ ] **具体实现重构** - 将现有爬虫、存储、转换模块改为继承基类并实现接口
- [ ] **工厂模式** - 使用工厂模式动态创建爬虫和存储实例，提升扩展性
- [ ] **模块解耦** - 通过接口依赖替代直接依赖，降低模块间耦合度

### 插件化架构
- [ ] **爬虫插件化** - 将 Telegram、GitHub、Google 等爬虫重构为独立插件
- [ ] **存储插件化** - 将 Gist、PasteGG、Imperial 等存储后端重构为插件
- [ ] **插件注册机制** - 实现插件自动发现和注册系统
- [ ] **插件配置标准化** - 定义统一的插件配置规范和验证机制

### 配置系统优化
- [ ] **配置模型化** - 使用 Pydantic 定义强类型配置模型
- [ ] **配置验证增强** - 实现配置完整性检查和错误提示
- [ ] **配置模板化** - 提供常用场景的配置模板和生成工具
- [ ] **配置文档化** - 自动生成配置项说明文档

### 代码质量提升
- [ ] **类型系统完善** - 全面引入类型注解，提升 IDE 支持和代码安全性
- [ ] **异常体系重构** - 设计统一的异常层次结构和错误码系统
- [ ] **日志标准化** - 实现结构化日志和统一的日志格式
- [ ] **代码风格统一** - 集成 Black、isort、flake8 等工具链

### 性能与稳定性
- [ ] **并发模型优化** - 改进线程池管理和任务调度机制
- [ ] **资源管理** - 实现连接池和资源自动回收机制
- [ ] **容错能力增强** - 完善重试策略和降级处理逻辑
- [ ] **内存优化** - 优化大数据处理的内存使用效率

---

## ⚖️ 免责声明

+ 本项目仅用作学习爬虫技术，请勿滥用，不要通过此工具做任何违法乱纪或有损国家利益之事
+ 禁止使用该项目进行任何盈利活动，对一切非法使用所产生的后果，本人概不负责
+ 使用者应遵守当地法律法规，尊重网站服务条款，合理使用网络资源

## 🙏 致谢

### 核心依赖
- [Subconverter](https://github.com/asdlokj1qpi233/subconverter) - 订阅转换核心
- [Mihomo](https://github.com/MetaCubeX/mihomo) - 代理测试引擎

### 赞助支持
感谢以下组织的赞助支持：
- [![YXVM](https://support.nodeget.com/page/promotion?id=250)](https://yxvm.com)
- [NodeSupport](https://github.com/NodeSeekDev/NodeSupport)

### 社区贡献
感谢所有为项目贡献代码、提出建议和报告问题的开发者们！

<div align="center">

**如果这个项目对你有帮助，请给它一个 ⭐**

[报告问题](https://github.com/wzdnzd/aggregator/issues) · [功能请求](https://github.com/wzdnzd/aggregator/issues) · [贡献代码](https://github.com/wzdnzd/aggregator/pulls)

</div>