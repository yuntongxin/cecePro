# API端点自动检测改进说明

## 问题分析
原来的问题是：当你输入不完整的API端点（如 `https://api.xiaomimimo.com/anthropic`）时，会返回404错误，因为真正的API端点需要完整的路径。

## 解决方案

### 1. 后端改进 (`utils/prompt_generator.py`)
- 增强了 `test_connection` 方法，添加了自动检测正确API端点的功能
- 定义了常见的API路径后缀：
  - OpenAI格式：`/v1/chat/completions`, `/chat/completions`, `/v1/chat`, `/api/v1/chat/completions`
  - Anthropic格式：`/v1/messages`, `/messages`, `/api/v1/messages`
- 当检测到输入的端点不完整时，会自动尝试添加各种常见的后缀
- 找到正确的端点后，会自动更新配置对象
- 添加了更详细的调试日志

### 2. 后端API改进 (`app.py`)
- 改进了 `/test_connection` 端点
- 当发现正确的端点时，会返回 `discovered_endpoint` 字段
- 更新了成功消息，告知用户发现的正确端点

### 3. 前端改进 (`templates/index.html`)
- 更新了 `testProviderConnection` 函数
- 当后端返回发现的正确端点时，会自动更新输入框中的值
- 显示更友好的提示信息

## 使用方法

### 1. 测试连接
1. 在API配置中输入你的基础URL（如 `https://api.xiaomimimo.com` 或 `https://api.xiaomimimo.com/anthropic`）
2. 填入API Key和模型名称
3. 点击"测试连接"按钮
4. 系统会自动尝试各种可能的API路径
5. 如果找到正确的端点，会自动更新输入框并提示你

### 2. 手动输入正确端点
如果你已经知道完整的API端点，可以直接输入，例如：
- OpenAI格式：`https://api.xiaomimimo.com/v1/chat/completions`
- Anthropic格式：`https://api.xiaomimimo.com/v1/messages`

## 测试脚本
还提供了两个测试脚本：

### `test_api.py`
交互式测试脚本，会提示你输入基础URL和API Key，然后自动测试各种可能的端点路径。

### `test_api_config.py`
预配置版本的测试脚本，可以在代码中预设基础URL和API Key。

## 常见问题

### Q: 如何知道我的API应该用什么格式？
A: 查看你的API服务文档，通常会说明是OpenAI兼容格式还是Anthropic格式。

### Q: 自动检测功能会尝试多少个端点？
A: 通常会尝试4-5个最常见的路径，很快就能完成。

### Q: 自动检测失败怎么办？
A: 查看你的API服务文档，获取完整的API端点路径，然后手动输入。

## 技术细节

### 路径检测逻辑
系统会检查输入的端点是否包含常见的路径关键字：
- `/chat/completions`
- `/messages`
- `/generateContent`

如果不包含这些关键字，就会自动尝试添加各种后缀。

### 超时设置
- 单个请求超时：15秒
- 每个端点最多重试：2次
- 重试间隔：1秒

### 成功判断标准
以下状态码都被认为是端点可达（虽然不一定认证成功）：
- 200：成功
- 401：认证失败（但端点存在）
- 403：权限不足（但端点存在）

## 下一步改进建议
1. 可以添加更多常见的API路径模式
2. 可以添加用户自定义路径后缀的功能
3. 可以添加API端点历史记录功能
4. 可以添加批量测试多个API服务的功能