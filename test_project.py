#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目功能测试脚本
使用前请填写下方的 API 配置
"""

import requests
import json
import os
import sys
import time
from pathlib import Path

# 禁用代理
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# ============================================================
#  配置区域 - 请在此处填写你的 API 信息
# ============================================================

API_CONFIG = {
    # API 供应商端点 - 使用完整路径避免自动探测
    "endpoint": "https://token-plan-cn.xiaomimimo.com/anthropic/v1/messages",
    # API Key
    "apiKey": "tp-cmzypdfagzt86hkt592t9uqhr675ubk48palaptibvg6uawi",  # <-- 替换为你的 API Key
    # 模型名称
    "model": "mimo-v2.5-pro",
    # API 格式: openai / anthropic / google
    "format": "anthropic",
    # 供应商名称（可选）
    "name": "小米"
}

# 服务器地址
BASE_URL = "http://127.0.0.1:5000"

# 禁用代理
NO_PROXY = {"http": None, "https": None}

# ============================================================
#  测试用例
# ============================================================

class TestResult:
    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.details = []

    def add_pass(self, msg):
        self.passed += 1
        self.details.append(("[PASS]", msg))

    def add_fail(self, msg):
        self.failed += 1
        self.details.append(("[FAIL]", msg))

    def add_skip(self, msg):
        self.skipped += 1
        self.details.append(("[SKIP]", msg))

    def summary(self):
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*60}")
        print(f"  {self.name}")
        print(f"{'='*60}")
        for status, msg in self.details:
            print(f"  {status} {msg}")
        print(f"{'='*60}")
        print(f"  Total: {total} | Pass: {self.passed} | Fail: {self.failed} | Skip: {self.skipped}")
        print(f"{'='*60}\n")
        return self.failed == 0


def test_homepage():
    """测试首页加载"""
    result = TestResult("首页加载测试")
    try:
        r = requests.get(f"{BASE_URL}/", timeout=10, proxies=NO_PROXY)
        if r.status_code == 200 and "视频AI解析助手" in r.text:
            result.add_pass("首页正常加载，状态码 200")
        else:
            result.add_fail(f"首页异常，状态码: {r.status_code}")
    except Exception as e:
        result.add_fail(f"首页请求失败: {e}")
    return result.summary()


def test_api_connection():
    """测试 API 连接"""
    result = TestResult("API 连接测试")

    if "sk-xxxxxxxx" in API_CONFIG["apiKey"]:
        result.add_skip("未配置 API Key，跳过测试")
        return result.summary()

    try:
        r = requests.post(f"{BASE_URL}/test_connection", json={
            "provider_config": API_CONFIG
        }, timeout=30, proxies=NO_PROXY)
        data = r.json()

        if data.get("success"):
            result.add_pass(f"API 连接成功: {API_CONFIG['name']}")
            if "discovered_endpoint" in data:
                result.add_pass(f"发现正确端点: {data['discovered_endpoint']}")
        else:
            result.add_fail(f"API 连接失败: {data.get('error', '未知错误')}")
    except Exception as e:
        result.add_fail(f"请求异常: {e}")

    return result.summary()


def test_video_analyze():
    """测试视频分析（需要提供测试视频）"""
    result = TestResult("视频分析测试")

    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        result.add_skip(f"未找到测试视频 {test_video}，跳过")
        return result.summary()

    if "sk-xxxxxxxx" in API_CONFIG["apiKey"]:
        result.add_skip("未配置 API Key，跳过提示词生成测试")
        # 只测试视频分析，不测试AI生成
        try:
            with open(test_video, 'rb') as f:
                r = requests.post(f"{BASE_URL}/analyze_video", files={
                    'video': (test_video, f, 'video/mp4')
                }, data={
                    'analysis_mode': 'auto'
                }, timeout=120, proxies=NO_PROXY)
            data = r.json()

            if r.status_code == 200:
                result.add_pass(f"视频分析成功")
                result.add_pass(f"  时长: {data.get('duration')}s")
                result.add_pass(f"  分辨率: {data.get('resolution')}")
                result.add_pass(f"  主色调: {data.get('dominant_color')}")
                result.add_pass(f"  运动程度: {data.get('motion_level')}")
            else:
                result.add_fail(f"视频分析失败: {data.get('error')}")
        except Exception as e:
            result.add_fail(f"请求异常: {e}")
        return result.summary()

    try:
        with open(test_video, 'rb') as f:
            r = requests.post(f"{BASE_URL}/analyze_video", files={
                'video': (test_video, f, 'video/mp4')
            }, data={
                'analysis_mode': 'auto',
                'provider_config': json.dumps(API_CONFIG)
            }, timeout=120, proxies=NO_PROXY)
        data = r.json()

        if r.status_code == 200:
            result.add_pass(f"视频分析成功")
            result.add_pass(f"  时长: {data.get('duration')}s")
            result.add_pass(f"  分辨率: {data.get('resolution')}")
            result.add_pass(f"  主色调: {data.get('dominant_color')}")
            result.add_pass(f"  运动程度: {data.get('motion_level')}")

            prompts = data.get('prompts', [])
            if prompts:
                result.add_pass(f"  生成提示词: {len(prompts)} 条")
                print(f"\n  提示词预览:\n  {prompts[0][:200]}...")
            else:
                result.add_fail("未生成提示词")
        else:
            result.add_fail(f"视频分析失败: {data.get('error')}")
    except Exception as e:
        result.add_fail(f"请求异常: {e}")

    return result.summary()


def test_image_analyze():
    """测试图片分析（需要提供测试图片）"""
    result = TestResult("图片分析测试")

    test_image = "test_image.jpg"
    if not os.path.exists(test_image):
        result.add_skip(f"未找到测试图片 {test_image}，跳过")
        return result.summary()

    if "sk-xxxxxxxx" in API_CONFIG["apiKey"]:
        result.add_skip("未配置 API Key，跳过提示词生成测试")
        return result.summary()

    try:
        with open(test_image, 'rb') as f:
            r = requests.post(f"{BASE_URL}/analyze_image", files={
                'image': (test_image, f, 'image/jpeg')
            }, data={
                'provider_config': json.dumps(API_CONFIG)
            }, timeout=120, proxies=NO_PROXY)
        data = r.json()

        if r.status_code == 200:
            result.add_pass(f"图片分析成功")
            result.add_pass(f"  分辨率: {data.get('resolution')}")
            result.add_pass(f"  主色调: {data.get('dominant_color')}")

            prompts = data.get('prompts', [])
            if prompts:
                result.add_pass(f"  生成提示词: {len(prompts)} 条")
            else:
                result.add_fail("未生成提示词")
        else:
            result.add_fail(f"图片分析失败: {data.get('error')}")
    except Exception as e:
        result.add_fail(f"请求异常: {e}")

    return result.summary()


def test_link_parse():
    """测试链接解析"""
    result = TestResult("链接解析测试")

    test_cases = [
        ("https://www.bilibili.com/video/BV1Jg411A7Qt", "bilibili"),
    ]

    for url, platform in test_cases:
        try:
            r = requests.post(f"{BASE_URL}/parse_link", json={
                "url": url,
                "platform": platform
            }, timeout=30, proxies=NO_PROXY)
            data = r.json()

            if r.status_code == 200 and "error" not in data:
                result.add_pass(f"{platform} 解析成功")
                if data.get("title"):
                    result.add_pass(f"  标题: {data['title'][:50]}")
            else:
                result.add_fail(f"{platform} 解析失败: {data.get('error', '未知')}")
        except Exception as e:
            result.add_fail(f"{platform} 请求异常: {e}")

    return result.summary()


def test_error_handling():
    """测试错误处理"""
    result = TestResult("错误处理测试")

    tests = [
        ("POST", "/analyze_video", {}, "无文件上传"),
        ("POST", "/analyze_image", {}, "无文件上传"),
        ("POST", "/parse_link", {}, "无链接"),
        ("POST", "/test_connection", {}, "无配置"),
    ]

    for method, path, data, desc in tests:
        try:
            r = requests.post(f"{BASE_URL}{path}", json=data, timeout=10, proxies=NO_PROXY)
            if r.status_code in [400, 500]:
                result.add_pass(f"{path} ({desc}) 返回 {r.status_code}")
            else:
                result.add_fail(f"{path} ({desc}) 应返回 400/500，实际 {r.status_code}")
        except Exception as e:
            result.add_fail(f"{path} 请求异常: {e}")

    return result.summary()


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


# ============================================================
#  主程序
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  视频AI解析助手 - 项目功能测试")
    print("=" * 60)
    print(f"  服务器: {BASE_URL}")
    print(f"  API: {API_CONFIG['name']}")
    print(f"  API Key: {'已配置' if 'sk-xxxxxxxx' not in API_CONFIG['apiKey'] else '未配置'}")
    print("=" * 60)

    # 检查服务器是否运行
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5, proxies=NO_PROXY)
        print("\n[OK] 服务器运行正常\n")
    except:
        print("\n[ERROR] 服务器未运行，请先启动: python app.py")
        sys.exit(1)

    # 运行测试
    all_passed = True
    all_passed &= test_homepage()
    all_passed &= test_error_handling()
    all_passed &= test_api_connection()
    all_passed &= test_link_parse()
    all_passed &= test_provider_api()
    all_passed &= test_video_analyze()
    all_passed &= test_image_analyze()

    # 最终结果
    print("=" * 60)
    if all_passed:
        print("  所有测试通过！")
    else:
        print("  存在失败的测试，请检查上方输出")
    print("=" * 60)
