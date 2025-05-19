<div align="center">
  <p><img src="/code/image/logo.png" width="480" alt="logo"></p>
</div>

<div align="center">

# Anime Progress - 本地番剧进度管理器

_✨ 本地番剧进度管理 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/SuperGuGuGu/nonebot_plugin_qbittorrent_manager.svg" alt="license">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>


## 📖 项目简介

一个轻量级的本地番剧进度管理解决方案，实现以下功能：

进度跟踪：分类观看和未观看番剧

智能管理：自动扫描添加jellyfin媒体库，添加番剧资源

个性化评分：为每部番剧添加评分

跨平台访问：通过 Web 界面随时随地管理收藏

## 🚀 快速部署

### 环境要求

Python 3.9+

pip 包管理工具

### 安装步骤

```
# 克隆此项目
git clone https://github.com/SuperGuGuGu/anime-progress
cd anime-progress

# 2. 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
cd code
python.exe main.py
```

### 访问使用

成功启动后，通过浏览器访问：

http://[服务器IP]:[端口]

### 首次运行指南

程序将自动生成配置文件 ```config.toml```

## 配置项

首次运行后将会生成 ‘config.toml’,请修改该文件来配置项目

|        配置项         | 必填 |   类型    |     默认值     |
|:------------------:|:--:|:-------:|:-----------:|
| media_library_path | 是  |  list   |     []      |
|        host        | 否  |   str   | "127.0.0.1" |
|        port        | 否  | str/int |    8080     |

```toml
# 示例：
media_library_path = ["./媒体库"]
host = "0.0.0.0"
port = 8080
```

