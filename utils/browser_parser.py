"""
Playwright 浏览器解析器
用无头浏览器打开页面，拦截网络请求，提取视频/图片链接。
用于抖音、TikTok、Instagram 等需要 JS 渲染的平台。
"""

import asyncio
import re
import time
import logging

logger = logging.getLogger(__name__)

# 各平台视频 CDN 域名特征
PLATFORM_CDN_PATTERNS = {
    'douyin': [
        r'douyinvod\.com',
        r'v\d*-web\.douyinvod\.com',
        r'v\d*-web-d\.douyinvod\.com',
        r'v\d+-web\.douyinvod\.com',
        r'bytevcloudcdn\.com',
        r'bytecdn\.cn',
        r'snssdk\.com.*?video',
    ],
    'tiktok': [
        r'tiktokcdn\.com',
        r'tikcdn\.com',
        r'bytevcloudcdn\.com',
    ],
    'instagram': [
        r'cdninstagram\.com',
        r'fbcdn\.net.*?video',
        r'instagram\.com.*?/v/',
    ],
    'twitter': [
        r'video\.twimg\.com',
        r'pbs\.twimg\.com.*?video',
    ],
    'facebook': [
        r'fbcdn\.net.*?video',
        r'facebook\.com.*?/video',
    ],
}

# 视频 Content-Type 特征
VIDEO_CONTENT_TYPES = [
    'video/mp4',
    'video/webm',
    'video/ogg',
    'video/quicktime',
    'application/x-mpegURL',
    'application/vnd.apple.mpegurl',
    'application/dash+xml',
]

# 平台特定的标题/封面提取规则
METADATA_SELECTORS = {
    'douyin': {
        'title': 'meta[property="og:title"]',
        'description': 'meta[property="og:description"]',
        'image': 'meta[property="og:image"]',
    },
    'tiktok': {
        'title': 'meta[property="og:title"]',
        'description': 'meta[property="og:description"]',
        'image': 'meta[property="og:image"]',
    },
    'instagram': {
        'title': 'meta[property="og:title"]',
        'description': 'meta[property="og:description"]',
        'image': 'meta[property="og:image"]',
    },
    'twitter': {
        'title': 'meta[property="og:title"]',
        'description': 'meta[property="og:description"]',
        'image': 'meta[property="og:image"]',
    },
}

# 平台等待选择器（页面加载完成的标志）
WAIT_SELECTORS = {
    'douyin': 'video, .video-player, [data-e2e="video-player"]',
    'tiktok': 'video, [data-e2e="video-player"]',
    'instagram': 'video, img[style*="object-fit"]',
    'twitter': 'video, [data-testid="videoPlayer"]',
}


class BrowserParser:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self._started = False

    async def start(self):
        """启动 Playwright 浏览器"""
        if self._started and self.browser:
            return
        try:
            from playwright.async_api import async_playwright
            # 如果之前的实例还在，先清理
            if self.playwright:
                try:
                    await self.playwright.stop()
                except:
                    pass
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--disable-extensions',
                    '--disable-gpu',
                    '--window-size=1920,1080',
                ]
            )
            self._started = True
            logger.info("Playwright 浏览器已启动")
        except Exception as e:
            logger.error(f"启动 Playwright 失败: {e}")
            self._started = False
            raise

    async def stop(self):
        """关闭浏览器"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"关闭 Playwright 失败: {e}")
        finally:
            self.browser = None
            self.playwright = None
            self._started = False

    async def parse_url(self, url, platform=None):
        """
        用浏览器打开 URL，拦截网络请求，提取视频/图片链接。

        Args:
            url: 要解析的链接
            platform: 平台标识（douyin/tiktok/instagram/twitter 等）

        Returns:
            dict: 标准格式 {platform, title, video_url, cover_url, download_url, ...}
        """
        if not self._started or not self.browser:
            await self.start()

        if not platform:
            platform = self._detect_platform(url)

        logger.info(f"[BrowserParser] 开始解析: {url} (平台: {platform})")

        try:
            page = await self.browser.new_page(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            )
        except Exception as e:
            logger.warning(f"[BrowserParser] 创建页面失败，尝试重启浏览器: {e}")
            await self.start()
            page = await self.browser.new_page(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            )

        # 注入反检测脚本
        await page.add_init_script("""
            // 隐藏 webdriver 标志
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

            // 覆盖 plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // 覆盖 languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });

            // 覆盖 chrome 对象
            window.chrome = { runtime: {} };

            // 覆盖 permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        """)

        captured_urls = []  # 捕获的视频 URL
        page_title = ''
        page_description = ''
        page_image = ''

        try:
            # 注册网络响应监听
            async def on_response(response):
                try:
                    content_type = response.headers.get('content-type', '')
                    url_str = response.url

                    # 捕获视频类型的响应
                    if any(ct in content_type for ct in VIDEO_CONTENT_TYPES):
                        if response.status == 200 or response.status == 206:
                            captured_urls.append({
                                'url': url_str,
                                'content_type': content_type,
                                'status': response.status,
                                'size': response.headers.get('content-length', '0'),
                            })
                            logger.info(f"[BrowserParser] 捕获视频: {url_str[:100]}... (type: {content_type})")

                    # 检查 URL 是否匹配平台 CDN 特征
                    cdn_patterns = PLATFORM_CDN_PATTERNS.get(platform, [])
                    for pattern in cdn_patterns:
                        if re.search(pattern, url_str, re.IGNORECASE):
                            # 额外检查是否是视频相关请求
                            if any(ext in url_str.lower() for ext in ['.mp4', '.m3u8', '.ts', 'video', 'play']):
                                if not any(c['url'] == url_str for c in captured_urls):
                                    captured_urls.append({
                                        'url': url_str,
                                        'content_type': content_type or 'video/unknown',
                                        'status': response.status,
                                        'size': response.headers.get('content-length', '0'),
                                    })
                                    logger.info(f"[BrowserParser] CDN匹配: {url_str[:100]}...")
                                break
                except Exception as e:
                    logger.debug(f"[BrowserParser] 响应处理异常: {e}")

            page.on('response', on_response)

            # 导航到目标页面
            logger.info(f"[BrowserParser] 导航到: {url}")

            # 先访问主页预热浏览器
            try:
                await page.goto('https://www.douyin.com/', wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(2)
            except:
                pass

            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=45000)
            except Exception as e:
                logger.warning(f"[BrowserParser] 页面加载超时或失败: {e}")

            # 等待页面进一步加载
            wait_selector = WAIT_SELECTORS.get(platform)
            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=15000)
                except:
                    pass

            # 额外等待，确保视频请求被拦截
            # 对于抖音等平台，视频可能需要用户交互才能加载
            await asyncio.sleep(5)

            # 尝试点击视频元素以触发播放
            try:
                video_el = await page.query_selector('video')
                if video_el:
                    await video_el.click()
                    logger.info("[BrowserParser] 点击视频元素触发播放")
                    await asyncio.sleep(3)
            except Exception as e:
                logger.debug(f"[BrowserParser] 点击视频失败: {e}")

            # 提取页面元数据
            try:
                # 获取标题
                title_el = await page.query_selector('title')
                if title_el:
                    page_title = await title_el.inner_text()

                # 尝试从 meta 标签获取信息
                selectors = METADATA_SELECTORS.get(platform, {})
                if selectors.get('title'):
                    el = await page.query_selector(selectors['title'])
                    if el:
                        page_title = await el.get_attribute('content') or page_title

                if selectors.get('description'):
                    el = await page.query_selector(selectors['description'])
                    if el:
                        page_description = await el.get_attribute('content') or ''

                if selectors.get('image'):
                    el = await page.query_selector(selectors['image'])
                    if el:
                        page_image = await el.get_attribute('content') or ''

                # 如果没有从 meta 获取到标题，尝试从页面内容提取
                if not page_title or page_title == '抖音':
                    og_title = await page.evaluate('''() => {
                        const el = document.querySelector('meta[property="og:title"]');
                        return el ? el.content : null;
                    }''')
                    if og_title:
                        page_title = og_title

                if not page_image:
                    og_image = await page.evaluate('''() => {
                        const el = document.querySelector('meta[property="og:image"]');
                        return el ? el.content : null;
                    }''')
                    if og_image:
                        page_image = og_image

            except Exception as e:
                logger.debug(f"[BrowserParser] 元数据提取异常: {e}")

            # 从页面 HTML 中提取额外的视频 URL（作为补充）
            try:
                html_video_urls = await page.evaluate('''() => {
                    const urls = [];
                    // 检查 video 标签
                    document.querySelectorAll('video source, video').forEach(el => {
                        const src = el.src || el.getAttribute('src') || '';
                        if (src && src.startsWith('http')) urls.push(src);
                    });
                    // 检查 xgplayer 等播放器的配置
                    if (window._playInfo) urls.push(window._playInfo.url || '');
                    if (window.__playinfo__) {
                        try {
                            const d = window.__playinfo__.data;
                            if (d && d.durl) d.durl.forEach(u => { if (u.url) urls.push(u.url); });
                            if (d && d.dash && d.dash.video) d.dash.video.forEach(u => { if (u.baseUrl) urls.push(u.baseUrl); });
                        } catch(e) {}
                    }
                    // 抖音特定：检查 __INITIAL_STATE__ 或 RENDER_DATA
                    if (window.__INITIAL_STATE__) {
                        try {
                            const state = window.__INITIAL_STATE__;
                            if (state.aweme && state.aweme.video) {
                                const v = state.aweme.video;
                                if (v.playAddr) urls.push(v.playAddr);
                                if (v.downloadAddr) urls.push(v.downloadAddr);
                            }
                        } catch(e) {}
                    }
                    // 检查所有 script 标签中的视频 URL
                    document.querySelectorAll('script').forEach(el => {
                        const text = el.textContent || '';
                        const matches = text.match(/https?:\/\/[^"'\s]+douyinvod\.com[^"'\s]+/g);
                        if (matches) urls.push(...matches);
                    });
                    return urls.filter(u => u && u.startsWith('http'));
                }''')
                for u in html_video_urls:
                    if not any(c['url'] == u for c in captured_urls):
                        captured_urls.append({
                            'url': u,
                            'content_type': 'video/unknown',
                            'status': 200,
                            'size': '0',
                        })
            except Exception as e:
                logger.debug(f"[BrowserParser] HTML视频提取异常: {e}")

            logger.info(f"[BrowserParser] 共捕获 {len(captured_urls)} 个视频URL")

            # 选择最佳视频 URL
            video_url = self._select_best_url(captured_urls, platform)

            if video_url:
                # 清理 URL
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                video_url = video_url.split('?')[0] + '?' + video_url.split('?')[1] if '?' in video_url else video_url

                result = {
                    'platform': platform,
                    'title': page_title or f'{platform}视频',
                    'video_url': video_url,
                    'cover_url': page_image,
                    'download_url': video_url,
                }
                if page_description:
                    result['description'] = page_description
                logger.info(f"[BrowserParser] 解析成功: {video_url[:100]}...")
                return result
            else:
                logger.warning("[BrowserParser] 未能提取到视频URL")
                return {'error': f'浏览器解析未能提取到视频链接', 'platform': platform}

        except Exception as e:
            logger.error(f"[BrowserParser] 解析异常: {e}")
            return {'error': f'浏览器解析失败: {str(e)}', 'platform': platform}
        finally:
            try:
                await page.close()
            except:
                pass

    def _select_best_url(self, captured_urls, platform):
        """从捕获的 URL 中选择最佳视频链接"""
        if not captured_urls:
            return None

        # 排除非视频内容的关键词
        EXCLUDE_KEYWORDS = [
            '.css', '.js', '.woff', '.woff2', '.ttf', '.otf',
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            'favicon', 'tracking', 'analytics', 'pixel',
            'font', 'css?', 'stylesheet', 'api/v1/css',
            'image', 'thumbnail', 'avatar', 'logo',
        ]

        # 过滤出视频类型的 URL
        video_urls = []
        for item in captured_urls:
            ct = item.get('content_type', '')
            url = item.get('url', '')
            size = int(item.get('size', '0') or '0')

            # 排除明显不是视频的 URL
            url_lower = url.lower()
            if any(skip in url_lower for skip in EXCLUDE_KEYWORDS):
                continue

            # 优先选择大文件（通常是完整视频）
            video_urls.append({**item, '_score': size})

        if not video_urls:
            # 如果没有明确的视频类型，尝试所有 URL
            video_urls = captured_urls

        # 按文件大小降序排列
        video_urls.sort(key=lambda x: x.get('_score', 0), reverse=True)

        # 优先选择特定 CDN 域名的 URL（且必须包含视频相关路径）
        cdn_patterns = PLATFORM_CDN_PATTERNS.get(platform, [])
        for item in video_urls:
            url_lower = item['url'].lower()
            for pattern in cdn_patterns:
                if re.search(pattern, item['url'], re.IGNORECASE):
                    # 额外检查 URL 是否包含视频相关路径
                    if any(v in url_lower for v in ['video', 'play', 'mp4', 'm3u8', '.ts']):
                        return item['url']

        # 如果没有找到带视频路径的 CDN URL，返回最大的 URL
        return video_urls[0]['url'] if video_urls else None

    def _detect_platform(self, url):
        """从 URL 检测平台"""
        url_lower = url.lower()
        if 'douyin.com' in url_lower or 'v.douyin.com' in url_lower:
            return 'douyin'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return 'facebook'
        elif 'bilibili.com' in url_lower:
            return 'bilibili'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        return 'general'


# 全局单例
_browser_parser = None


def get_browser_parser():
    """获取全局 BrowserParser 单例"""
    global _browser_parser
    if _browser_parser is None:
        _browser_parser = BrowserParser()
    return _browser_parser


async def parse_with_browser(url, platform=None):
    """
    便捷函数：用浏览器解析 URL。
    每次调用都创建新的浏览器实例，避免连接问题。

    Args:
        url: 要解析的链接
        platform: 平台标识

    Returns:
        dict: 标准格式解析结果
    """
    parser = BrowserParser()
    try:
        return await parser.parse_url(url, platform)
    finally:
        await parser.stop()
