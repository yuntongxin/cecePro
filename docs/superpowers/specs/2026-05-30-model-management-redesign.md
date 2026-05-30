# 模型管理模块重构设计

## 目标

将模型管理重构为 cc-switch 风格，支持配置文件化、分类筛选、快速切换。

## 当前问题

1. **端点自动探测 bug** — `/anthropic` 被错误添加后缀变成 `/anthropic/v1/messages`
2. **字段名不一致** — 前端用 `format`/`apiKey`，后端内置用 `api_format`
3. **内置供应商未暴露** — 前端无法使用内置的 30+ 供应商
4. **代理问题** — 后端请求走系统代理，代理未运行时失败

## 设计方案

### 1. 配置文件结构

**`providers.json`（内置供应商）**
```json
{
  "version": "1.0",
  "categories": {
    "domestic": "国内平台",
    "international": "国际平台",
    "relay": "API中继"
  },
  "providers": [
    {
      "id": "siliconflow",
      "name": "硅基流动 SiliconFlow",
      "category": "domestic",
      "endpoint": "https://api.siliconflow.cn/v1/chat/completions",
      "model": "Qwen/Qwen2.5-7B-Instruct",
      "format": "openai",
      "website": "https://www.siliconflow.cn",
      "free_credit": "注册送15元额度",
      "note": "高性能AI基础设施"
    }
  ]
}
```

**`custom_providers.json`（用户自定义）**
```json
[
  {
    "id": "my-provider",
    "name": "我的供应商",
    "endpoint": "https://api.example.com/v1/chat/completions",
    "model": "gpt-4o-mini",
    "format": "openai",
    "apiKey": "sk-xxx",
    "note": "自定义"
  }
]
```

### 2. 后端改动

**新增 API 端点：**
- `GET /providers` — 获取所有供应商（内置 + 自定义）
- `GET /providers/builtin` — 获取内置供应商
- `GET /providers/custom` — 获取自定义供应商
- `POST /providers/custom` — 添加自定义供应商
- `PUT /providers/custom/<id>` — 更新自定义供应商
- `DELETE /providers/custom/<id>` — 删除自定义供应商

**修复 test_connection：**
- 移除端点自动探测逻辑（或改为可选）
- 统一字段名为 `format` 和 `apiKey`
- 添加代理禁用参数

### 3. 前端改动

**界面布局（cc-switch 风格）：**
```
┌─────────────────────────────────────────────────┐
│  模型管理                                    [+] │
├─────────────────────────────────────────────────┤
│  [国内平台] [国际平台] [API中继] [我的]  [搜索] │
├─────────────────────────────────────────────────┤
│  □ 硅基流动 SiliconFlow                         │
│    Qwen/Qwen2.5-7B-Instruct                    │
│    注册送15元额度                    [使用][测试]│
├─────────────────────────────────────────────────┤
│  □ DeepSeek                                     │
│    deepseek-chat                                │
│    国产高性能                       [使用][测试]│
├─────────────────────────────────────────────────┤
│  □ 小米                                         │
│    mimo-v2.5-pro                                │
│    自定义                           [使用][测试]│
└─────────────────────────────────────────────────┘
```

**功能：**
- 分类标签筛选
- 搜索框按名称搜索
- 点击"使用"切换当前模型
- 点击"测试"测试连接
- 点击"+"添加自定义供应商
- 右键或更多菜单编辑/删除

### 4. 字段统一

| 字段 | 说明 | 示例 |
|------|------|------|
| `id` | 唯一标识 | `siliconflow` |
| `name` | 显示名称 | `硅基流动` |
| `category` | 分类 | `domestic`/`international`/`relay`/`custom` |
| `endpoint` | API端点 | `https://api.siliconflow.cn/v1/chat/completions` |
| `model` | 默认模型 | `Qwen/Qwen2.5-7B-Instruct` |
| `format` | API格式 | `openai`/`anthropic`/`google` |
| `apiKey` | API密钥 | `sk-xxx`（仅自定义） |
| `website` | 官网 | `https://www.siliconflow.cn` |
| `free_credit` | 免费额度 | `注册送15元额度` |
| `note` | 备注 | `高性能AI基础设施` |

### 5. 实施步骤

1. **创建 `providers.json`** — 将内置供应商从 `prompt_generator.py` 迁移出来
2. **新增后端 API** — 供应商 CRUD 接口
3. **修复 test_connection** — 统一字段名，移除自动探测或改为可选
4. **重构前端** — cc-switch 风格界面
5. **测试** — 验证所有功能

### 6. 验收标准

- [ ] 内置供应商可在前端显示和使用
- [ ] 自定义供应商可添加/编辑/删除
- [ ] 分类筛选正常工作
- [ ] 搜索功能正常工作
- [ ] 测试连接功能正常
- [ ] 端点自动探测不再破坏已有路径
- [ ] 代理问题已解决
