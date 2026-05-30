# 模型管理模块重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将模型管理重构为 cc-switch 风格，支持配置文件化、分类筛选、快速切换

**Architecture:** 将内置供应商从 prompt_generator.py 迁移到 providers.json，新增后端 API 支持 CRUD 操作，重构前端为 cc-switch 风格界面

**Tech Stack:** Python Flask, JSON 配置, HTML/CSS/JavaScript

---

## 文件结构

```
cecePro/
├── providers.json                    # 新建：内置供应商配置
├── custom_providers.json             # 已有：用户自定义供应商
├── app.py                            # 修改：新增供应商 API 端点
├── utils/
│   └── prompt_generator.py           # 修改：移除内置配置，修复 test_connection
├── templates/
│   └── index.html                    # 修改：重构模型管理界面
└── test_project.py                   # 修改：更新测试用例
```

---

### Task 1: 创建 providers.json 配置文件

**Files:**
- Create: `providers.json`

- [ ] **Step 1: 创建 providers.json 文件**

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
      "id": "openai",
      "name": "OpenAI GPT",
      "category": "international",
      "endpoint": "https://api.openai.com/v1/chat/completions",
      "model": "gpt-4o-mini",
      "format": "openai",
      "website": "https://platform.openai.com",
      "free_credit": "需付费",
      "note": "国际主流模型"
    },
    {
      "id": "anthropic",
      "name": "Anthropic Claude",
      "category": "international",
      "endpoint": "https://api.anthropic.com/v1/messages",
      "model": "claude-3-haiku-20240307",
      "format": "anthropic",
      "website": "https://www.anthropic.com",
      "free_credit": "需付费",
      "note": "英文能力强"
    },
    {
      "id": "google",
      "name": "Google Gemini",
      "category": "international",
      "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-lite:generateContent",
      "model": "gemini-1.5-flash-lite",
      "format": "google",
      "website": "https://ai.google.dev",
      "free_credit": "有免费额度",
      "note": "多模态能力强"
    },
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
    },
    {
      "id": "deepseek",
      "name": "DeepSeek",
      "category": "domestic",
      "endpoint": "https://api.deepseek.com/v1/chat/completions",
      "model": "deepseek-chat",
      "format": "openai",
      "website": "https://platform.deepseek.com",
      "free_credit": "注册送一定额度",
      "note": "国产高性能"
    },
    {
      "id": "zhipu",
      "name": "智谱AI GLM",
      "category": "domestic",
      "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
      "model": "glm-4-flash",
      "format": "openai",
      "website": "https://open.bigmodel.cn",
      "free_credit": "注册送Token",
      "note": "中文理解好"
    },
    {
      "id": "minimax",
      "name": "MiniMax",
      "category": "domestic",
      "endpoint": "https://api.minimax.chat/v1/text/chatcompletion_v2",
      "model": "abab6.5s-chat",
      "format": "openai",
      "website": "https://www.minimax.chat",
      "free_credit": "注册送Token",
      "note": "响应快"
    },
    {
      "id": "kimi",
      "name": "Kimi 月之暗面",
      "category": "domestic",
      "endpoint": "https://api.moonshot.cn/v1/chat/completions",
      "model": "moonshot-v1-8k",
      "format": "openai",
      "website": "https://platform.moonshot.cn",
      "free_credit": "注册送额度",
      "note": "长上下文"
    },
    {
      "id": "doubao",
      "name": "豆包 字节跳动",
      "category": "domestic",
      "endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
      "model": "doubao-pro-32k",
      "format": "openai",
      "website": "https://www.volcengine.com/product/doubao",
      "free_credit": "注册送额度",
      "note": "字节跳动"
    },
    {
      "id": "tongyi",
      "name": "通义千问",
      "category": "domestic",
      "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
      "model": "qwen-turbo",
      "format": "openai",
      "website": "https://dashscope.console.aliyun.com",
      "free_credit": "有免费额度",
      "note": "阿里云"
    },
    {
      "id": "baidu",
      "name": "百度文心一言",
      "category": "domestic",
      "endpoint": "https://qianfan.aiap.baidu.com/v2/chat/completions",
      "model": "ernie-4.0-8k-latest",
      "format": "openai",
      "website": "https://console.bce.baidu.com",
      "free_credit": "注册送额度",
      "note": "百度智能云"
    },
    {
      "id": "tencent",
      "name": "腾讯混元",
      "category": "domestic",
      "endpoint": "https://api.hunyuan.cloud.tencent.com/v1/chat/completions",
      "model": "hunyuan-pro",
      "format": "openai",
      "website": "https://cloud.tencent.com/product/hunyuan",
      "free_credit": "注册送额度",
      "note": "腾讯云"
    },
    {
      "id": "packycode",
      "name": "PackyCode",
      "category": "relay",
      "endpoint": "https://api.packycode.com/v1/chat/completions",
      "model": "gpt-4o-mini",
      "format": "openai",
      "website": "https://packycode.com",
      "free_credit": "首充10%折扣",
      "note": "稳定的API中继服务"
    },
    {
      "id": "aigocode",
      "name": "AIGoCode",
      "category": "relay",
      "endpoint": "https://api.aigocode.com/v1/chat/completions",
      "model": "gpt-4o-mini",
      "format": "openai",
      "website": "https://aigocode.com",
      "free_credit": "首充10% bonus",
      "note": "集成多种模型"
    },
    {
      "id": "dmxapi",
      "name": "DMXAPI",
      "category": "relay",
      "endpoint": "https://api.dmxapi.com/v1/chat/completions",
      "model": "gpt-4o-mini",
      "format": "openai",
      "website": "https://dmxapi.com",
      "free_credit": "GPT/Claude/Gemini 32% off",
      "note": "全球大模型API服务"
    }
  ]
}
```

- [ ] **Step 2: 验证 JSON 格式**

Run: `python -c "import json; json.load(open('providers.json', encoding='utf-8')); print('JSON valid')"`

Expected: `JSON valid`

- [ ] **Step 3: Commit**

```bash
git add providers.json
git commit -m "feat: create providers.json with built-in provider configurations"
```

---

### Task 2: 修改 app.py 添加供应商 API 端点

**Files:**
- Modify: `app.py`

- [ ] **Step 1: 添加 providers.json 加载函数**

在 `app.py` 的 `load_custom_providers` 函数后添加：

```python
PROVIDERS_FILE = 'providers.json'

def load_builtin_providers():
    """加载内置供应商配置"""
    try:
        if os.path.exists(PROVIDERS_FILE):
            with open(PROVIDERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('providers', [])
        return []
    except Exception as e:
        print(f"加载内置供应商失败: {e}")
        return []

def get_all_providers():
    """获取所有供应商（内置 + 自定义）"""
    builtin = load_builtin_providers()
    custom = load_custom_providers()
    # 为自定义供应商添加 category
    for p in custom:
        if 'category' not in p:
            p['category'] = 'custom'
    return builtin + custom
```

- [ ] **Step 2: 添加供应商 API 端点**

在 `app.py` 的 `/test_connection` 路由前添加：

```python
@app.route('/providers', methods=['GET'])
def get_providers():
    """获取所有供应商"""
    try:
        providers = get_all_providers()
        return jsonify(providers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/providers/builtin', methods=['GET'])
def get_builtin_providers_api():
    """获取内置供应商"""
    try:
        providers = load_builtin_providers()
        return jsonify(providers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/providers/custom', methods=['GET'])
def get_custom_providers_api():
    """获取自定义供应商"""
    try:
        providers = load_custom_providers()
        return jsonify(providers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/providers/custom', methods=['POST'])
def add_custom_provider():
    """添加自定义供应商"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供供应商配置'}), 400
        
        required_fields = ['name', 'endpoint', 'model', 'apiKey']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
        
        # 生成 ID
        import uuid
        data['id'] = str(uuid.uuid4())[:8]
        if 'format' not in data:
            data['format'] = 'openai'
        
        # 加载现有配置并添加
        providers = load_custom_providers()
        providers.append(data)
        save_custom_providers(providers)
        
        return jsonify({'success': True, 'provider': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/providers/custom/<provider_id>', methods=['PUT'])
def update_custom_provider(provider_id):
    """更新自定义供应商"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供供应商配置'}), 400
        
        providers = load_custom_providers()
        for i, p in enumerate(providers):
            if p.get('id') == provider_id:
                data['id'] = provider_id
                providers[i] = data
                save_custom_providers(providers)
                return jsonify({'success': True, 'provider': data})
        
        return jsonify({'error': '供应商不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/providers/custom/<provider_id>', methods=['DELETE'])
def delete_custom_provider(provider_id):
    """删除自定义供应商"""
    try:
        providers = load_custom_providers()
        providers = [p for p in providers if p.get('id') != provider_id]
        save_custom_providers(providers)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

- [ ] **Step 3: 测试新 API 端点**

启动服务器后测试：

```bash
# 测试获取所有供应商
curl http://127.0.0.1:5000/providers

# 测试获取内置供应商
curl http://127.0.0.1:5000/providers/builtin

# 测试获取自定义供应商
curl http://127.0.0.1:5000/providers/custom
```

Expected: 返回 JSON 数组

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add provider CRUD API endpoints"
```

---

### Task 3: 修复 prompt_generator.py 的 test_connection

**Files:**
- Modify: `utils/prompt_generator.py`

- [ ] **Step 1: 修复端点自动探测逻辑**

找到 `test_connection` 方法中的端点探测代码（约 1446-1454 行），修改为：

```python
        # 如果原始路径看起来不完整，尝试添加后缀
        endpoint_lower = endpoint.lower()
        # 检查是否已经是完整路径
        is_complete_path = any(suffix in endpoint_lower for suffix in ['/chat/completions', '/messages', '/generatecontent'])
        
        # 只有当路径明显不完整时才尝试添加后缀
        # 例如：只包含域名没有路径，或者路径很短
        path_parts = endpoint.replace('https://', '').replace('http://', '').split('/')
        if not is_complete_path and len(path_parts) <= 2:
            # 移除可能的结尾斜杠
            base_endpoint = endpoint.rstrip('/')
            # 尝试添加各种后缀
            for suffix in suffixes:
                if suffix:  # 跳过空后缀（已经尝试过了）
                    all_endpoints_to_try.append(f"{base_endpoint}{suffix}")
```

- [ ] **Step 2: 统一字段名读取**

找到 `test_connection` 方法开头（约 1406-1409 行），修改为：

```python
        endpoint = custom_config.get('endpoint')
        model_name = custom_config.get('model')
        # 兼容两种字段名
        api_format = custom_config.get('format') or custom_config.get('api_format', 'openai')
        api_key = custom_config.get('apiKey') or custom_config.get('api_key')
```

- [ ] **Step 3: 添加代理禁用**

找到 `requests.post` 调用（约 1517 行），修改为：

```python
                    response = requests.post(test_endpoint, headers=headers, json=payload, timeout=15, proxies={'http': None, 'https': None})
```

- [ ] **Step 4: 测试修复**

运行测试脚本：

```bash
python test_project.py
```

Expected: API 连接测试 PASS

- [ ] **Step 5: Commit**

```bash
git add utils/prompt_generator.py
git commit -m "fix: improve test_connection endpoint detection and field name compatibility"
```

---

### Task 4: 重构前端模型管理界面

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: 添加 CSS 样式**

在 `<style>` 标签内添加：

```css
/* 模型管理界面样式 */
.provider-manager {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
}

.provider-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.provider-header h3 {
    margin: 0;
    color: #fff;
}

.provider-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    flex-wrap: wrap;
}

.provider-tab {
    padding: 8px 16px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: transparent;
    color: #fff;
    cursor: pointer;
    transition: all 0.3s;
}

.provider-tab:hover {
    background: rgba(255, 255, 255, 0.1);
}

.provider-tab.active {
    background: #667eea;
    border-color: #667eea;
}

.provider-search {
    width: 100%;
    padding: 12px 15px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    margin-bottom: 15px;
}

.provider-search::placeholder {
    color: rgba(255, 255, 255, 0.5);
}

.provider-list {
    max-height: 400px;
    overflow-y: auto;
}

.provider-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.05);
    margin-bottom: 10px;
    transition: all 0.3s;
}

.provider-item:hover {
    background: rgba(255, 255, 255, 0.1);
}

.provider-item.active {
    border: 2px solid #667eea;
    background: rgba(102, 126, 234, 0.1);
}

.provider-info {
    flex: 1;
}

.provider-name {
    font-weight: bold;
    color: #fff;
    margin-bottom: 5px;
}

.provider-model {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
}

.provider-note {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
    margin-top: 3px;
}

.provider-actions {
    display: flex;
    gap: 8px;
}

.provider-btn {
    padding: 6px 12px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s;
}

.provider-btn.use {
    background: #667eea;
    color: #fff;
}

.provider-btn.use:hover {
    background: #5a6fd6;
}

.provider-btn.test {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
}

.provider-btn.test:hover {
    background: rgba(255, 255, 255, 0.2);
}

.provider-btn.edit {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
}

.provider-btn.delete {
    background: rgba(255, 0, 0, 0.2);
    color: #ff6b6b;
}

.provider-btn.delete:hover {
    background: rgba(255, 0, 0, 0.3);
}
```

- [ ] **Step 2: 添加 HTML 结构**

在合适的位置添加模型管理界面：

```html
<!-- 模型管理界面 -->
<div class="provider-manager" id="provider-manager" style="display: none;">
    <div class="provider-header">
        <h3>模型管理</h3>
        <button class="provider-btn use" onclick="showAddProviderModal()">+ 添加模型</button>
    </div>
    
    <div class="provider-tabs">
        <button class="provider-tab active" data-category="all" onclick="filterProviders('all')">全部</button>
        <button class="provider-tab" data-category="domestic" onclick="filterProviders('domestic')">国内平台</button>
        <button class="provider-tab" data-category="international" onclick="filterProviders('international')">国际平台</button>
        <button class="provider-tab" data-category="relay" onclick="filterProviders('relay')">API中继</button>
        <button class="provider-tab" data-category="custom" onclick="filterProviders('custom')">我的</button>
    </div>
    
    <input type="text" class="provider-search" placeholder="搜索模型..." oninput="searchProviders(this.value)">
    
    <div class="provider-list" id="provider-list">
        <!-- 动态生成 -->
    </div>
</div>
```

- [ ] **Step 3: 添加 JavaScript 逻辑**

在 `<script>` 标签内添加：

```javascript
// 模型管理相关变量
let allProviders = [];
let currentCategory = 'all';
let searchQuery = '';

// 加载所有供应商
async function loadAllProviders() {
    try {
        const response = await fetch('/providers');
        allProviders = await response.json();
        renderProviderList();
    } catch (error) {
        console.error('加载供应商失败:', error);
    }
}

// 渲染供应商列表
function renderProviderList() {
    const providerList = document.getElementById('provider-list');
    if (!providerList) return;
    
    let filtered = allProviders;
    
    // 分类筛选
    if (currentCategory !== 'all') {
        filtered = filtered.filter(p => p.category === currentCategory);
    }
    
    // 搜索筛选
    if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filtered = filtered.filter(p => 
            p.name.toLowerCase().includes(query) || 
            (p.note && p.note.toLowerCase().includes(query))
        );
    }
    
    if (filtered.length === 0) {
        providerList.innerHTML = '<div style="text-align: center; padding: 40px; color: #888;">暂无模型</div>';
        return;
    }
    
    providerList.innerHTML = filtered.map(provider => `
        <div class="provider-item ${currentProvider && currentProvider.id === provider.id ? 'active' : ''}">
            <div class="provider-info">
                <div class="provider-name">${provider.name}</div>
                <div class="provider-model">${provider.model}</div>
                ${provider.note ? `<div class="provider-note">${provider.note}</div>` : ''}
            </div>
            <div class="provider-actions">
                <button class="provider-btn use" onclick="useProvider('${provider.id}')">使用</button>
                <button class="provider-btn test" onclick="testProviderById('${provider.id}')">测试</button>
                ${provider.category === 'custom' ? `
                    <button class="provider-btn edit" onclick="editProvider('${provider.id}')">编辑</button>
                    <button class="provider-btn delete" onclick="deleteProvider('${provider.id}')">删除</button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

// 筛选供应商
function filterProviders(category) {
    currentCategory = category;
    document.querySelectorAll('.provider-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.category === category);
    });
    renderProviderList();
}

// 搜索供应商
function searchProviders(query) {
    searchQuery = query;
    renderProviderList();
}

// 使用供应商
function useProvider(providerId) {
    const provider = allProviders.find(p => p.id === providerId);
    if (provider) {
        currentProvider = provider;
        localStorage.setItem('currentProvider', JSON.stringify(provider));
        renderProviderList();
        showToast(`已切换到: ${provider.name}`);
    }
}

// 测试供应商
async function testProviderById(providerId) {
    const provider = allProviders.find(p => p.id === providerId);
    if (!provider) return;
    
    if (!provider.apiKey && provider.category !== 'custom') {
        showError('请先为该供应商配置 API Key');
        return;
    }
    
    const testLoading = document.getElementById('test-loading');
    if (testLoading) {
        testLoading.style.display = 'block';
        testLoading.classList.add('show');
    }
    
    try {
        const response = await fetch('/test_connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider_config: provider })
        });
        const data = await response.json();
        
        if (testLoading) {
            testLoading.classList.remove('show');
            testLoading.style.display = 'none';
        }
        
        if (data.success) {
            showToast(`连接成功: ${provider.name}`);
        } else {
            showError(`连接失败: ${data.error || '请检查配置'}`);
        }
    } catch (error) {
        if (testLoading) {
            testLoading.classList.remove('show');
            testLoading.style.display = 'none';
        }
        showError('测试失败，请检查网络连接');
    }
}

// 编辑供应商
function editProvider(providerId) {
    const provider = allProviders.find(p => p.id === providerId);
    if (provider) {
        showEditProviderModal(provider);
    }
}

// 删除供应商
async function deleteProvider(providerId) {
    if (!confirm('确定要删除这个供应商吗？')) return;
    
    try {
        const response = await fetch(`/providers/custom/${providerId}`, {
            method: 'DELETE'
        });
        const data = await response.json();
        
        if (data.success) {
            showToast('删除成功');
            loadAllProviders();
        } else {
            showError('删除失败');
        }
    } catch (error) {
        showError('删除失败');
    }
}

// 显示添加供应商模态框
function showAddProviderModal() {
    // 复用现有的模态框逻辑
    document.getElementById('modal-title').textContent = '添加模型';
    document.getElementById('provider-name').value = '';
    document.getElementById('provider-endpoint').value = '';
    document.getElementById('provider-model').value = '';
    document.getElementById('provider-format').value = 'openai';
    document.getElementById('provider-api-key').value = '';
    document.getElementById('provider-note').value = '';
    document.getElementById('provider-modal').style.display = 'block';
    document.getElementById('provider-modal').dataset.editId = '';
}

// 显示编辑供应商模态框
function showEditProviderModal(provider) {
    document.getElementById('modal-title').textContent = '编辑模型';
    document.getElementById('provider-name').value = provider.name || '';
    document.getElementById('provider-endpoint').value = provider.endpoint || '';
    document.getElementById('provider-model').value = provider.model || '';
    document.getElementById('provider-format').value = provider.format || 'openai';
    document.getElementById('provider-api-key').value = provider.apiKey || '';
    document.getElementById('provider-note').value = provider.note || '';
    document.getElementById('provider-modal').style.display = 'block';
    document.getElementById('provider-modal').dataset.editId = provider.id || '';
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadAllProviders();
});
```

- [ ] **Step 4: 测试界面**

启动服务器，打开浏览器测试：
- 分类筛选是否正常
- 搜索功能是否正常
- 使用/测试/编辑/删除按钮是否正常

- [ ] **Step 5: Commit**

```bash
git add templates/index.html
git commit -m "feat: implement cc-switch style provider management UI"
```

---

### Task 5: 更新测试脚本

**Files:**
- Modify: `test_project.py`

- [ ] **Step 1: 添加供应商 API 测试**

在 `test_error_handling` 函数后添加：

```python
def test_provider_api():
    """测试供应商 API"""
    result = TestResult("供应商 API 测试")
    
    try:
        # 测试获取所有供应商
        r = requests.get(f"{BASE_URL}/providers", proxies=NO_PROXY, timeout=10)
        if r.status_code == 200:
            providers = r.json()
            result.add_pass(f"获取所有供应商成功，共 {len(providers)} 个")
        else:
            result.add_fail(f"获取所有供应商失败，状态码: {r.status_code}")
    except Exception as e:
        result.add_fail(f"请求异常: {e}")
    
    try:
        # 测试获取内置供应商
        r = requests.get(f"{BASE_URL}/providers/builtin", proxies=NO_PROXY, timeout=10)
        if r.status_code == 200:
            providers = r.json()
            result.add_pass(f"获取内置供应商成功，共 {len(providers)} 个")
        else:
            result.add_fail(f"获取内置供应商失败，状态码: {r.status_code}")
    except Exception as e:
        result.add_fail(f"请求异常: {e}")
    
    try:
        # 测试获取自定义供应商
        r = requests.get(f"{BASE_URL}/providers/custom", proxies=NO_PROXY, timeout=10)
        if r.status_code == 200:
            providers = r.json()
            result.add_pass(f"获取自定义供应商成功，共 {len(providers)} 个")
        else:
            result.add_fail(f"获取自定义供应商失败，状态码: {r.status_code}")
    except Exception as e:
        result.add_fail(f"请求异常: {e}")
    
    return result.summary()
```

- [ ] **Step 2: 更新主测试流程**

在 `all_passed &= test_link_parse()` 后添加：

```python
    all_passed &= test_provider_api()
```

- [ ] **Step 3: 运行完整测试**

```bash
python test_project.py
```

Expected: 所有测试 PASS

- [ ] **Step 4: Commit**

```bash
git add test_project.py
git commit -m "test: add provider API tests"
```

---

### Task 6: 集成测试和验收

- [ ] **Step 1: 启动服务器**

```bash
python app.py
```

- [ ] **Step 2: 浏览器测试**

打开 http://127.0.0.1:5000，测试以下功能：
- 点击"模型管理"按钮显示管理界面
- 分类标签筛选（国内/国际/API中继/我的）
- 搜索框搜索供应商
- 点击"使用"切换当前模型
- 点击"测试"测试连接
- 点击"+"添加自定义供应商
- 编辑/删除自定义供应商

- [ ] **Step 3: 运行自动化测试**

```bash
python test_project.py
```

Expected: 所有测试 PASS

- [ ] **Step 4: 最终 Commit**

```bash
git add -A
git commit -m "feat: complete model management redesign with cc-switch style UI"
```
