import requests
import json

# 测试更新自定义供应商
url = "http://localhost:5000/api/custom-providers/1f433466"

headers = {
    'Content-Type': 'application/json'
}

# 测试数据 - 修改名称和模型
data = {
    "name": "百炼1-测试",
    "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    "model": "qwen3.5-plus-test",
    "format": "openai"
}

print("发送更新请求...")
response = requests.put(url, headers=headers, json=data)

print(f"状态码: {response.status_code}")
print(f"响应内容: {response.text}")

if response.status_code == 200:
    print("\n更新成功！")
    # 检查文件内容
    with open('custom_providers.json', 'r', encoding='utf-8') as f:
        providers = json.load(f)
    print("\n更新后的文件内容:")
    print(json.dumps(providers, ensure_ascii=False, indent=2))
else:
    print("\n更新失败！")
