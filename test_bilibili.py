#!/usr/bin/env python3
# 测试 B 站解析逻辑

import sys
sys.path.append('g:\\AI\\TraeCN\\TraeWenJian\\cecePro')

from utils.link_parser import LinkParser

# 测试 B 站链接
url = "https://www.bilibili.com/video/BV1Jg411A7Qt"

print(f"测试 B 站链接: {url}")
print("=" * 60)

parser = LinkParser()

# 测试 HTML 解析
print("\n1. 测试 HTML 解析:")
try:
    result = parser._parse_bilibili_html(url)
    print(f"   标题: {result.get('title')}")
    print(f"   作者: {result.get('author')}")
    print(f"   时长: {result.get('duration')}")
    print(f"   封面: {result.get('cover_url')}")
    print(f"   视频链接: {result.get('video_url')}")
except Exception as e:
    print(f"   错误: {e}")

# 测试 you-get 解析
print("\n2. 测试 you-get 解析:")
try:
    result = parser._parse_bilibili_youget(url)
    print(f"   标题: {result.get('title')}")
    print(f"   作者: {result.get('author')}")
    print(f"   时长: {result.get('duration')}")
    print(f"   封面: {result.get('cover_url')}")
    print(f"   视频链接: {result.get('video_url')}")
except Exception as e:
    print(f"   错误: {e}")

# 测试 API 解析
print("\n3. 测试 API 解析:")
try:
    result = parser._parse_bilibili_api(url)
    print(f"   标题: {result.get('title')}")
    print(f"   作者: {result.get('author')}")
    print(f"   时长: {result.get('duration')}")
    print(f"   封面: {result.get('cover_url')}")
    print(f"   视频链接: {result.get('video_url')}")
except Exception as e:
    print(f"   错误: {e}")

# 测试完整解析
print("\n4. 测试完整解析:")
try:
    result = parser.parse_link(url, 'bilibili')
    print(f"   平台: {result.get('platform')}")
    print(f"   标题: {result.get('title')}")
    print(f"   作者: {result.get('author')}")
    print(f"   时长: {result.get('duration')}")
    print(f"   封面: {result.get('cover_url')}")
    print(f"   视频链接: {result.get('video_url')}")
    print(f"   下载链接: {result.get('download_url')}")
    if 'quality_options' in result:
        print(f"   画质选项: {len(result['quality_options'])}")
except Exception as e:
    print(f"   错误: {e}")

print("\n" + "=" * 60)
print("测试完成!")