# 视频AI解析助手

上传视频，自动分析风格并生成AI提示词

## 功能特点

- 🎬 视频分析：提取主色调、饱和度、亮度、运动程度等特征
- ✨ 智能生成：根据分析结果生成多个AI提示词
- 🤖 多模型支持：硅基流动、DeepSeek、智谱AI、MiniMax、OpenAI、Claude
- 💰 成本低：用户自配API，按需付费

## 项目结构

```
video-ai-project/
├── app.py                      # Flask主程序
├── requirements.txt            # Python依赖
├── templates/
│   └── index.html             # 前端页面
├── utils/
│   ├── __init__.py
│   ├── video_analyzer.py      # 视频分析工具
│   └── prompt_generator.py     # 提示词生成器
└── static/
    └── uploads/               # 上传文件目录
```

## 安装步骤（Windows小白教程）

### 第一步：安装Python

1. 打开浏览器，访问 https://www.python.org/downloads/
2. 下载 Python 3.8 或更高版本（约25MB）
3. 运行安装包，**必须勾选 Add Python to PATH**
4. 点击 Install Now
5. 安装完成后，按 Win+R，输入 cmd，打开命令提示符
6. 输入以下命令验证安装：

```bash
python --version
pip --version
```

### 第二步：安装依赖

1. 打开命令提示符，进入项目目录：

```bash
cd g:\AI\TraeCN\TraeWenJian\cecePro
```

2. 安装Python依赖：

```bash
pip install -r requirements.txt
```

3. 等待安装完成（约5-10分钟）

### 第三步：获取API Key

推荐使用**硅基流动**，注册送15元额度，便宜又好用：

1. 访问 https://www.siliconflow.cn
2. 注册账号
3. 进入控制台 → API Key → 创建新密钥
4. 复制API Key备用

其他可选平台：
- DeepSeek：https://platform.deepseek.com
- 智谱AI：https://open.bigmodel.cn
- MiniMax：https://www.minimax.chat

### 第四步：运行网站

1. 在命令提示符中运行：

```bash
python app.py
```

2. 等待启动，看到以下信息表示成功：

```
============================================================
  视频AI解析助手
  访问地址: http://127.0.0.1:5000
============================================================
```

3. 打开浏览器，访问 http://127.0.0.1:5000

## 使用方法

1. 选择AI服务商（下拉选择）
2. 输入API Key
3. 点击上传区域，选择视频文件
4. 点击"开始解析视频"
5. 等待分析完成，查看结果

## 常见问题

### 问题1：pip不是内部命令

**解决方法**：
1. 重启电脑
2. 按 Win+R，输入 cmd
3. 输入 `python -m pip --version`

### 问题2：安装opencv失败

**解决方法**：
如果opencv安装失败，可以单独安装：

```bash
pip install opencv-python-headless==4.8.1.78
```

### 问题3：端口5000被占用

**解决方法**：
修改 app.py 第57行，把 `port=5000` 改成 `port=5001`

### 问题4：上传视频报错

**解决方法**：
1. 确保视频格式是 MP4, AVI, MOV, MKV, WEBM
2. 确保视频大小小于200MB
3. 确保视频文件名没有中文和特殊字符

### 问题5：API调用失败

**解决方法**：
1. 检查API Key是否正确
2. 检查API Key是否有额度
3. 检查网络连接

## API模型说明

| 模型 | 说明 | 特点 |
|------|------|------|
| 硅基流动 | 国产平价API | 便宜、支持多种模型 |
| DeepSeek | 国产高性能 | 性能强、价格低 |
| 智谱AI | 国产大模型 | 中文理解好 |
| MiniMax | 国产大模型 | 响应快 |
| OpenAI | GPT-4 | 国际主流 |
| Claude | Anthropic | 英文能力强 |

## 成本说明

本项目不运行任何AI模型，所有AI调用都通过用户提供的API Key进行。

估算成本（硅基流动）：
- 分析10个视频 ≈ 0.01元
- 非常便宜！

## 技术栈

- **后端**：Python Flask
- **前端**：HTML5 + CSS3 + JavaScript
- **视频处理**：OpenCV
- **AI模型**：用户自配API

## 后续扩展

如果你想添加更多功能，可以考虑：

1. 添加更多视频分析维度（如场景识别、物体检测）
2. 添加视频下载功能（解析B站、抖音等平台）
3. 添加提示词模板库
4. 添加历史记录功能
5. 添加用户系统

## 许可证

MIT License
