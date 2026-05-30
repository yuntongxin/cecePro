#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API端点测试脚本
帮助验证正确的API路径
"""

import requests
import json

def test_api_endpoint(base_url, api_key, test_cases=None):
    """测试多个可能的API端点路径"""
    
    if test_cases is None:
        test_cases = [
            # OpenAI 格式的常见路径
            '/v1/chat/completions',
            '/chat/completions',
            '/v1/chat',
            '/api/v1/chat/completions',
            
            # Anthropic 格式的常见路径
            '/v1/messages',
            '/messages',
            '/api/v1/messages',
            
            # 自定义路径
            '/anthropic/v1/messages',
            '/anthropic/messages',
        ]
    
    print("=" * 60)
    print("API端点测试工具")
    print("=" * 60)
    print(f"基础URL: {base_url}")
    print("-" * 60)
    
    results = []
    
    for path in test_cases:
        full_url = base_url.rstrip('/') + path
        print(f"\n测试: {full_url}")
        print("-" * 60)
        
        try:
            # 先尝试OpenAI格式
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            data = {
                'model': 'claude-3-haiku-20240307',
                'messages': [
                    {'role': 'user', 'content': 'Hi'}
                ],
                'max_tokens': 5
            }
            
            response = requests.post(full_url, headers=headers, json=data, timeout=10)
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ OpenAI格式成功！")
                results.append({
                    'url': full_url,
                    'format': 'openai',
                    'success': True
                })
            elif response.status_code != 404:
                # 如果不是404，可能是格式问题，试试Anthropic格式
                print(f"尝试Anthropic格式...")
                
                headers = {
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                }
                
                data = {
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 5,
                    'messages': [
                        {'role': 'user', 'content': 'Hi'}
                    ]
                }
                
                response = requests.post(full_url, headers=headers, json=data, timeout=10)
                
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Anthropic格式成功！")
                    results.append({
                        'url': full_url,
                        'format': 'anthropic',
                        'success': True
                    })
                else:
                    print(f"❌ 失败: {response.status_code}")
                    try:
                        print(f"响应: {response.json()}")
                    except:
                        print(f"响应: {response.text[:200]}")
            else:
                print(f"❌ 404 - 路径不存在")
                
        except requests.exceptions.Timeout:
            print("❌ 超时")
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求错误: {str(e)}")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    if results:
        for result in results:
            print(f"✅ {result['url']} ({result['format']}格式)")
    else:
        print("❌ 没有找到可用的API端点")
        print("\n建议检查：")
        print("1. API Key是否正确")
        print("2. 基础URL是否正确")
        print("3. 网络连接是否正常")
    
    return results

if __name__ == "__main__":
    # 用户输入
    base_url = input("请输入基础URL (例如: https://api.xiaomimimo.com): ").strip()
    api_key = input("请输入API Key: ").strip()
    
    if not base_url:
        print("请提供基础URL")
        exit(1)
    
    if not api_key:
        print("请提供API Key")
        exit(1)
    
    test_api_endpoint(base_url, api_key)
