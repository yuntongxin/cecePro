# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

视频AI解析助手：用户上传视频/图片，系统自动分析视觉特征（颜色、运动、场景）并调用大语言模型生成AI创作提示词。支持B站、抖音等平台视频链接解析与下载。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发服务器（默认端口 5000）
python app.py

# 测试脚本
python test_api.py          # 交互式API端点测试
python test_api_config.py   # 预配置API端点测试
python test_bilibili.py     # B站链接解析测试
```

外部工具依赖：`yt-dlp`（B站等平台视频下载）

## 架构

### 后端（Flask）

`app.py` 是唯一的入口文件，包含所有路由：
- `POST /analyze_video` — 上传视频，返回分析结果和AI提示词
- `POST /analyze_image` — 上传图片，返回分析结果和AI提示词
- `POST /test_connection` — 测试API供应商连接
- `POST /parse_link` — 解析视频平台链接
- `GET /download_proxy` — 视频下载代理（B站用yt-dlp，其他平台用requests）
- `GET /image_proxy` — 图片代理（解决跨域问题）
- `GET /download_video` — 视频下载（直接下载或yt-dlp）

### utils/ 模块

- `video_analyzer.py` — VideoAnalyzer：用OpenCV分析视频帧，提取颜色（RGB/HSV）、运动程度、场景亮度。`extract_key_frames()` 提取首帧/尾帧/中间均匀帧供AI分析。
- `image_analyzer.py` — ImageAnalyzer：图片版本的视觉分析，包含颜色、场景、亮度、内容特征。
- `prompt_generator.py` — PromptGenerator：核心模块。内置20+供应商配置（OpenAI/Anthropic/Google/国内各大模型/API中继），支持三种API格式（`openai`、`anthropic`、`google`）。`generate_with_video()` 将关键帧base64编码后发给多模态模型生成提示词。`test_connection()` 支持自动探测API端点路径。
- `link_parser.py` — LinkParser：解析B站/抖音/YouTube等平台视频链接，尝试HTML解析、API调用、you-get工具等多种方式获取视频信息。

### 前端

单文件 `templates/index.html`（~118KB），包含全部HTML/CSS/JS逻辑。

### 数据流

1. 用户上传视频/图片 → `app.py` 保存到 `static/uploads/`
2. `VideoAnalyzer`/`ImageAnalyzer` 提取视觉特征
3. `PromptGenerator` 将关键帧（base64）+ 分析结果发送给用户选择的AI模型
4. AI返回提示词 → 删除临时文件 → 返回JSON结果给前端

## API配置

- 内置供应商配置在 `prompt_generator.py` 的 `api_endpoints` 字典中
- 用户自定义供应商保存在 `custom_providers.json`
- 支持三种API格式：`openai`（大多数国内模型）、`anthropic`、`google`
- 端点自动探测：输入不完整URL时会尝试常见路径后缀（`/v1/chat/completions`、`/v1/messages`等）

## 注意事项

- Flask JSON响应已配置 `JSON_AS_ASCII = False` 确保中文正确显示
- 上传限制200MB，支持格式：mp4/avi/mov/mkv/webm/jpg/jpeg/png/gif/webp
- 视频分析帧数根据时长自动计算（<10s取3帧，<60s取5帧，更长按比例增加，最多30帧）
- CORS已全局启用
- B站下载需要设置Referer为 `https://www.bilibili.com/`
