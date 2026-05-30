import requests
from bs4 import BeautifulSoup
import re
import json
import random
import time
import subprocess
import urllib.parse
import os
import http.cookiejar
import asyncio

class LinkParser:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

        self.timeout = 30
        self.last_request_time = 0
        self.min_request_interval = 1.0
        self.proxy = os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY') or None

    def _get_random_headers(self, referer=None):
        headers = self.base_headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)

        if referer:
            headers['Referer'] = referer

        return headers

    def _rate_limit(self):
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)

        self.last_request_time = time.time()

    def _get_session(self):
        session = requests.Session()
        if self.proxy:
            session.proxies = {
                'http': self.proxy,
                'https': self.proxy
            }
        return session

    def parse_link(self, url, platform=None):
        if not url:
            return {'error': '链接不能为空'}

        if not platform or platform == 'auto':
            platform = self._detect_platform(url)

        result = None
        try:
            if platform == 'douyin':
                result = self._parse_douyin(url)
            elif platform == 'bilibili':
                result = self._parse_bilibili(url)
            elif platform == 'youtube':
                result = self._parse_youtube(url)
            elif platform == 'twitter':
                result = self._parse_twitter(url)
            elif platform == 'tiktok':
                result = self._parse_tiktok(url)
            elif platform == 'instagram':
                result = self._parse_instagram(url)
            elif platform == 'facebook':
                result = self._parse_facebook(url)
            elif platform == 'onlyfans':
                result = self._parse_onlyfans(url)
            elif platform == 'general':
                result = self._parse_general(url)
            else:
                return {'error': f'不支持的平台: {platform}'}
        except requests.exceptions.Timeout:
            return {'error': '请求超时，请检查网络连接'}
        except requests.exceptions.ConnectionError:
            return {'error': '网络连接失败，请检查网络设置或代理配置'}
        except requests.exceptions.RequestException as e:
            return {'error': f'网络请求失败: {str(e)}'}
        except Exception as e:
            result = {'error': f'解析失败: {str(e)}'}

        # 如果常规方法失败，且是支持浏览器解析的平台，尝试用浏览器解析
        if result and result.get('error') and platform in ('douyin', 'tiktok', 'instagram', 'twitter'):
            print(f"[LinkParser] 常规解析失败，尝试浏览器解析: {url}")
            browser_result = self._parse_with_browser(url, platform)
            if browser_result and not browser_result.get('error'):
                return browser_result

        return result

    def _parse_with_browser(self, url, platform):
        """用 Playwright 浏览器解析（同步包装异步调用）"""
        try:
            from utils.browser_parser import parse_with_browser

            # 尝试复用已有的事件循环
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行（Flask 环境），用线程池执行
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(asyncio.run, parse_with_browser(url, platform))
                        result = future.result(timeout=60)
                    return result
                else:
                    return loop.run_until_complete(parse_with_browser(url, platform))
            except RuntimeError:
                return asyncio.run(parse_with_browser(url, platform))
        except ImportError:
            print("[LinkParser] Playwright 未安装，跳过浏览器解析")
            return {'error': '浏览器解析不可用（Playwright 未安装）', 'platform': platform}
        except Exception as e:
            print(f"[LinkParser] 浏览器解析异常: {e}")
            return {'error': f'浏览器解析失败: {str(e)}', 'platform': platform}

    def _detect_platform(self, url):
        if 'douyin.com' in url or 'v.douyin.com' in url:
            return 'douyin'
        elif 'bilibili.com' in url:
            return 'bilibili'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'twitter.com' in url or 'x.com' in url:
            return 'twitter'
        elif 'tiktok.com' in url:
            return 'tiktok'
        elif 'instagram.com' in url:
            return 'instagram'
        elif 'facebook.com' in url or 'fb.watch' in url:
            return 'facebook'
        elif 'onlyfans.com' in url:
            return 'onlyfans'
        else:
            return 'general'

    def _get_douyin_cookies(self):
        """获取抖音基础Cookie"""
        try:
            import http.cookiejar
            session = requests.Session()
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
            session.get('https://www.douyin.com/discover', headers=headers, timeout=10)
            cookie_file = os.path.join(os.path.dirname(__file__), f'.douyin_cookies_{os.getpid()}.txt')
            with open(cookie_file, 'w') as f:
                f.write('# Netscape HTTP Cookie File\n')
                for cookie in session.cookies:
                    secure = 'TRUE' if cookie.secure else 'FALSE'
                    domain = cookie.domain
                    if not domain.startswith('.'):
                        domain = '.' + domain
                    f.write(f'{domain}\tTRUE\t{cookie.path}\t{secure}\t0\t{cookie.name}\t{cookie.value}\n')
            return cookie_file
        except Exception as e:
            print(f"获取抖音Cookie失败: {e}")
            return None

    def _parse_douyin(self, url):
        try:
            self._rate_limit()

            # 获取Cookie文件
            cookie_file = self._get_douyin_cookies()

            ytdlp_options = [
                'yt-dlp',
                '--dump-json',
                '--no-check-certificate',
                '--no-playlist',
                '--user-agent', random.choice(self.user_agents),
                '--referer', 'https://www.douyin.com/',
            ]

            if cookie_file:
                ytdlp_options.extend(['--cookies', cookie_file])

            if self.proxy:
                ytdlp_options.extend(['--proxy', self.proxy])

            ytdlp_options.append(url)

            result = subprocess.run(
                ytdlp_options,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout.strip():
                video_info = json.loads(result.stdout)
                video_url = video_info.get('url') or video_info.get('extractor_data', {}).get('url')
                title = video_info.get('title', '抖音视频')
                thumbnail = video_info.get('thumbnail')
                duration = video_info.get('duration')
                author = video_info.get('uploader') or video_info.get('channel')

                quality_options = []
                if 'formats' in video_info:
                    for fmt in video_info['formats']:
                        if fmt.get('vcodec') != 'none':
                            format_url = fmt.get('url') or fmt.get('extractor_data', {}).get('url')
                            if format_url:
                                quality_options.append({
                                    'quality': fmt.get('format_note', 'unknown'),
                                    'url': format_url,
                                    'label': f"{fmt.get('format_note', 'unknown')} - {fmt.get('ext', 'mp4')}"
                                })

                return {
                    'platform': 'douyin',
                    'title': title,
                    'author': author,
                    'duration': self._format_duration(duration),
                    'video_url': video_url,
                    'cover_url': thumbnail,
                    'download_url': video_url,
                    'quality_options': quality_options[:5] if quality_options else None
                }

            # 清理cookie文件
            if cookie_file and os.path.exists(cookie_file):
                try: os.remove(cookie_file)
                except: pass

            return self._parse_douyin_fallback(url)
        except FileNotFoundError:
            return self._parse_douyin_fallback(url)
        except Exception as e:
            return self._parse_douyin_fallback(url)

    def _parse_douyin_fallback(self, url):
        """抖音HTML解析降级方案"""
        try:
            self._rate_limit()

            session = self._get_session()

            # 短链接需要先获取Cookie再访问
            cookie_file = self._get_douyin_cookies()
            if cookie_file and os.path.exists(cookie_file):
                try:
                    cj = http.cookiejar.MozillaCookieJar(cookie_file)
                    cj.load(ignore_discard=True, ignore_expires=True)
                    session.cookies = cj
                except:
                    pass
                finally:
                    try: os.remove(cookie_file)
                    except: pass

            headers = self._get_random_headers(referer='https://www.douyin.com/')

            response = session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            final_url = response.url
            response.raise_for_status()

            video_url = None
            title = '抖音视频'
            cover_url = None

            # 尝试从RENDER_DATA提取
            script_match = re.search(r'<script id="RENDER_DATA" type="application/json">(.*?)</script>', response.text)
            if script_match:
                try:
                    render_data = json.loads(urllib.parse.unquote(script_match.group(1)))
                    potential_paths = [
                        ['aweme', 'video', 'playAddr'],
                        ['itemList', 0, 'video', 'playAddr'],
                        ['aweme', 'detail', 'video', 'playAddr'],
                        ['video', 'playAddr'],
                        ['item', 'video', 'playAddr'],
                        ['aweme', 'video', 'downloadAddr'],
                    ]
                    for path in potential_paths:
                        try:
                            current = render_data
                            for key in path:
                                current = current[key]
                            if current:
                                if isinstance(current, list) and len(current) > 0:
                                    if isinstance(current[0], dict):
                                        video_url = current[0].get('url') or current[0].get('Uri')
                                    else:
                                        video_url = current[0]
                                elif isinstance(current, dict):
                                    video_url = current.get('url') or current.get('Uri')
                                else:
                                    video_url = current
                                if video_url:
                                    break
                        except:
                            continue
                except Exception as e:
                    print(f"解析 RENDER_DATA 失败: {e}")

            # 尝试从页面提取视频URL
            if not video_url:
                patterns = [
                    r'"playAddr"\s*:\s*\{[^}]*"url_list"\s*:\s*\["([^"]+)"',
                    r'"play_addr"[^}]*"url_list"\s*:\s*\["([^"]+)"',
                    r'"download_addr"[^}]*"url_list"\s*:\s*\["([^"]+)"',
                    r'"video"\s*:\s*\{[^}]*"play_addr"[^}]*"url_list"\s*:\s*\["([^"]+)"',
                    r'playAddr\s*:\s*["\']([^"\']+)["\']',
                    r'https://v[0-9]*-[a-z]+\.douyinvod\.com/[^"\'>\s]+',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        video_url = matches[0]
                        break

            if video_url:
                if video_url.startswith('//'):
                    video_url = 'https:' + video_url
                video_url = urllib.parse.unquote(video_url)

            # 提取标题
            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            if title_match:
                title = title_match.group(1).replace(' - 抖音', '').replace(' - Douyin', '').strip()

            # 提取封面
            cover_match = re.search(r'og:image"?\s*content="([^"]+)"', response.text)
            if cover_match:
                cover_url = cover_match.group(1)

            if video_url:
                return {
                    'platform': 'douyin',
                    'title': title,
                    'video_url': video_url,
                    'cover_url': cover_url,
                    'download_url': video_url
                }

            # 所有方法都失败
            return {
                'error': '抖音解析失败: 抖音页面需要JavaScript渲染，无法直接提取视频链接。请尝试复制完整的视频链接（https://www.douyin.com/video/数字ID）后重试。',
                'platform': 'douyin'
            }
        except Exception as e:
            return {'error': f'抖音解析失败: {str(e)}'}

    def _parse_bilibili(self, url):
        try:
            self._rate_limit()

            # 尝试 1: 直接从 HTML 中提取视频链接
            result = self._parse_bilibili_html(url)
            if result.get('download_url'):
                return result

            # 尝试 2: 使用 you-get
            result = self._parse_bilibili_youget(url)
            if result.get('download_url'):
                return result

            # 尝试 3: 使用 yt-dlp
            ytdlp_options = [
                'yt-dlp',
                '--dump-json',
                '--no-check-certificate',
                '--no-playlist',
                '--user-agent', random.choice(self.user_agents),
            ]

            if self.proxy:
                ytdlp_options.extend(['--proxy', self.proxy])

            ytdlp_options.append(url)

            result = subprocess.run(
                ytdlp_options,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout.strip():
                video_info = json.loads(result.stdout)
                video_url = video_info.get('url')
                title = video_info.get('title', 'B站视频')
                thumbnail = video_info.get('thumbnail')
                duration = video_info.get('duration')
                author = video_info.get('uploader') or video_info.get('channel')

                quality_options = []
                if 'formats' in video_info:
                    for fmt in video_info['formats']:
                        if fmt.get('vcodec') != 'none':
                            format_url = fmt.get('url')
                            if format_url:
                                quality_options.append({
                                    'quality': fmt.get('format_note', 'unknown'),
                                    'url': format_url,
                                    'label': f"{fmt.get('format_note', 'unknown')} - {fmt.get('ext', 'mp4')}"
                                })

                return {
                    'platform': 'bilibili',
                    'title': title,
                    'author': author,
                    'duration': self._format_duration(duration),
                    'video_url': video_url,
                    'cover_url': thumbnail,
                    'download_url': video_url,
                    'quality_options': quality_options[:6] if quality_options else None
                }

            # 尝试 4: 从 API 获取
            return self._parse_bilibili_api(url)
        except FileNotFoundError:
            return self._parse_bilibili_api(url)
        except Exception as e:
            print(f"B站解析失败: {e}")
            return self._parse_bilibili_api(url)

    def _parse_bilibili_youget(self, url):
        try:
            # 使用 you-get 获取视频信息
            result = subprocess.run(
                ['you-get', '--json', url],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and result.stdout.strip():
                video_info = json.loads(result.stdout)
                title = video_info.get('title', 'B站视频')
                author = video_info.get('site', '')
                duration = video_info.get('duration')
                cover_url = video_info.get('cover')
                
                # 提取视频链接
                streams = video_info.get('streams', {})
                video_url = None
                
                # 尝试不同的清晰度
                for quality in ['flv', 'hdflv', 'mp4', 'hdmp4']:
                    if quality in streams:
                        stream = streams[quality]
                        if 'src' in stream and stream['src']:
                            video_url = stream['src'][0]
                            print(f"从 you-get 提取到视频链接: {video_url}")
                            break
                
                return {
                    'platform': 'bilibili',
                    'title': title,
                    'author': author,
                    'duration': self._format_duration(duration),
                    'video_url': video_url,
                    'cover_url': cover_url,
                    'download_url': video_url
                }
        except Exception as e:
            print(f"you-get 解析失败: {e}")
        
        return {'error': 'you-get 解析失败'}

    def _parse_bilibili_html(self, url):
        try:
            session = self._get_session()
            headers = self._get_random_headers(referer='https://www.bilibili.com/')
            
            response = session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            html = response.text
            
            # 提取标题
            title_match = re.search(r'<title>([^<]+)</title>', html)
            title = title_match.group(1).replace('_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili', '').strip() if title_match else 'B站视频'
            
            # 提取封面图
            cover_match = re.search(r'og:image"?\s*content="([^"]+)"', html)
            cover_url = cover_match.group(1) if cover_match else None
            
            # 提取作者
            author_match = re.search(r'"author"\s*:\s*"([^"]+)"', html)
            author = author_match.group(1) if author_match else None
            
            # 提取时长
            duration_match = re.search(r'"duration"\s*:\s*(\d+)', html)
            duration = self._format_duration(int(duration_match.group(1))) if duration_match else None
            
            # 提取视频链接 - 尝试从播放器配置中提取
            video_url = None
            
            # 尝试 1: 从 window.__playinfo__ 中提取
            playinfo_match = re.search(r'window\.__playinfo__\s*=\s*(\{[\s\S]+?\})\s*;', html)
            if playinfo_match:
                try:
                    playinfo = json.loads(playinfo_match.group(1))
                    if 'data' in playinfo:
                        data = playinfo['data']
                        # 尝试不同的数据结构
                        if 'durl' in data:
                            for d in data['durl']:
                                if 'url' in d:
                                    video_url = d['url']
                                    print(f"从 window.__playinfo__ 提取到视频链接: {video_url}")
                                    break
                        elif 'dash' in data:
                            dash = data['dash']
                            if 'video' in dash and len(dash['video']) > 0:
                                video_url = dash['video'][0].get('baseUrl')
                                print(f"从 dash 视频提取到视频链接: {video_url}")
                except Exception as e:
                    print(f"解析 playinfo 失败: {e}")
            
            # 尝试 2: 从 script 标签中提取
            if not video_url:
                script_patterns = [
                    r'"url"\s*:\s*"([^"]+\.m4s[^"]*)"',
                    r'"baseUrl"\s*:\s*"([^"]+)"',
                    r'"src"\s*:\s*"([^"]+\.mp4[^"]*)"',
                ]
                for pattern in script_patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        for match in matches:
                            if 'http' in match and ('mp4' in match or 'm4s' in match):
                                video_url = match
                                print(f"从 script 标签提取到视频链接: {video_url}")
                                break
                    if video_url:
                        break
            
            # 尝试 3: 从 API 直接获取
            if not video_url:
                bv_match = re.search(r'(BV\w+)', url)
                if bv_match:
                    bvid = bv_match.group(1)
                    try:
                        # 获取视频信息
                        info_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
                        info_response = session.get(info_url, headers=headers, timeout=self.timeout)
                        info_data = info_response.json()
                        
                        if info_data.get('code') == 0:
                            cid = info_data['data']['pages'][0]['cid']
                            # 获取播放地址
                            play_url = f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=80'
                            play_response = session.get(play_url, headers=headers, timeout=self.timeout)
                            play_data = play_response.json()
                            
                            if play_data.get('code') == 0:
                                if 'durl' in play_data['data']:
                                    for d in play_data['data']['durl']:
                                        if 'url' in d:
                                            video_url = d['url']
                                            print(f"从 API 提取到视频链接: {video_url}")
                                            break
                    except Exception as e:
                        print(f"API 提取失败: {e}")
            
            return {
                'platform': 'bilibili',
                'title': title,
                'author': author,
                'duration': duration,
                'video_url': video_url,
                'cover_url': cover_url,
                'download_url': video_url
            }
        except Exception as e:
            print(f"B站 HTML 解析失败: {e}")
            return {'error': f'B站解析失败: {str(e)}'}

    def _parse_bilibili_api(self, url):
        try:
            # 从 URL 提取 BV 号或 AV 号
            bv_match = re.search(r'(BV\w+)', url)
            av_match = re.search(r'(av\d+)', url)
            
            if bv_match:
                bvid = bv_match.group(1)
                print(f"提取到 BV 号: {bvid}")
            elif av_match:
                aid = av_match.group(1)[2:]
                # 转换 AV 号到 BV 号
                bvid = self._av_to_bv(aid)
                print(f"提取到 AV 号，转换为 BV 号: {bvid}")
            else:
                return {'error': '无法提取视频 ID'}

            # 使用 B 站 API
            api_url = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
            session = self._get_session()
            headers = self._get_random_headers(referer='https://www.bilibili.com/')
            
            print(f"请求 B 站 API: {api_url}")
            response = session.get(api_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            print(f"API 响应状态: {data.get('code')}")
            
            if data.get('code') != 0:
                return {'error': f'API 调用失败: {data.get("message")}'}
            
            video_data = data.get('data', {})
            title = video_data.get('title', 'B站视频')
            author = video_data.get('owner', {}).get('name')
            duration = video_data.get('duration')
            cover_url = video_data.get('pic')
            
            print(f"视频标题: {title}")
            print(f"作者: {author}")
            print(f"时长: {duration}")
            print(f"封面: {cover_url}")
            
            # 获取视频分P信息
            pages = video_data.get('pages', [])
            print(f"分P数量: {len(pages)}")
            
            if pages:
                cid = pages[0].get('cid')
                print(f"第一个分P的 CID: {cid}")
                
                # 尝试不同的 API 端点
                play_urls = [
                    f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=80&fnval=4048',
                    f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=64&fnval=4',
                    f'https://api.bilibili.com/x/player/playurl?bvid={bvid}&cid={cid}&qn=32&fnval=16'
                ]
                
                for i, play_url in enumerate(play_urls):
                    try:
                        print(f"尝试获取播放地址 ({i+1}/{len(play_urls)}): {play_url}")
                        play_response = session.get(play_url, headers=headers, timeout=self.timeout)
                        play_response.raise_for_status()
                        
                        play_data = play_response.json()
                        print(f"播放地址 API 响应状态: {play_data.get('code')}")
                        
                        if play_data.get('code') == 0:
                            durl = play_data.get('data', {}).get('durl', [])
                            print(f"获取到的 durl 数量: {len(durl)}")
                            
                            if durl:
                                video_url = durl[0].get('url')
                                print(f"获取到视频地址: {video_url}")
                                
                                return {
                                    'platform': 'bilibili',
                                    'title': title,
                                    'author': author,
                                    'duration': self._format_duration(duration),
                                    'video_url': video_url,
                                    'cover_url': cover_url,
                                    'download_url': video_url
                                }
                    except Exception as e:
                        print(f"尝试失败: {e}")
                        continue
        except Exception as e:
            print(f"B站 API 解析失败: {e}")
        
        return self._parse_bilibili_fallback(url)

    def _av_to_bv(self, aid):
        # AV 号转 BV 号的算法
        table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
        tr = {}
        for i in range(58):
            tr[table[i]] = i
        s = [11, 10, 3, 8, 4, 6]
        xor = 177451812
        add = 8728348608
        
        aid = int(aid)
        aid = (aid ^ xor) + add
        r = list('BV1  4 1 7  ')
        for i in range(6):
            r[s[i]] = table[aid // 58**i % 58]
        return ''.join(r)

    def _parse_bilibili_fallback(self, url):
        try:
            self._rate_limit()

            session = self._get_session()
            headers = self._get_random_headers(referer='https://www.bilibili.com/')

            response = session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            title_tag = soup.find('title')
            title = title_tag.text.replace('_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili', '').strip() if title_tag else 'B站视频'

            video_url = None
            cover_url = None
            duration = None
            author = None

            # 尝试从 HTML 中提取视频链接
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string:
                    # 尝试不同的模式提取视频链接
                    patterns = [
                        r'"url"\s*:\s*"([^"]+\.m4s[^"]*)"',
                        r'"video"\s*:\s*\{[^\}]*"url"\s*:\s*"([^"]+)"',
                        r'"baseUrl"\s*:\s*"([^"]+)"',
                        r'"downloadUrl"\s*:\s*"([^"]+)"',
                        r'"src"\s*:\s*"([^"]+\.mp4[^"]*)"',
                    ]
                    for pattern in patterns:
                        matches = re.findall(pattern, script.string)
                        if matches:
                            for match in matches:
                                if 'http' in match and ('mp4' in match or 'm4s' in match):
                                    video_url = match
                                    print(f"从 HTML 中提取到视频链接: {video_url}")
                                    break
                        if video_url:
                            break
                if video_url:
                    break

            # 提取封面图
            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image:
                cover_url = og_image.get('content')

            # 提取作者和时长
            script_patterns = [
                r'"title"\s*:\s*"([^"]+)"',
                r'"author"\s*:\s*"([^"]+)"',
                r'"duration"\s*:\s*(\d+)',
            ]
            for pattern in script_patterns:
                match = re.search(pattern, response.text)
                if match:
                    if 'title' in pattern:
                        title = match.group(1)
                    elif 'author' in pattern:
                        author = match.group(1)
                    elif 'duration' in pattern:
                        duration = self._format_duration(int(match.group(1)))

            if not video_url:
                # 尝试从播放器配置中提取
                player_config = re.search(r'window\.__playinfo__\s*=\s*(\{[^\}]+\})', response.text)
                if player_config:
                    try:
                        config = json.loads(player_config.group(1))
                        if 'data' in config and 'durl' in config['data']:
                            for d in config['data']['durl']:
                                if 'url' in d:
                                    video_url = d['url']
                                    print(f"从播放器配置中提取到视频链接: {video_url}")
                                    break
                    except:
                        pass

            return {
                'platform': 'bilibili',
                'title': title,
                'author': author,
                'duration': duration,
                'video_url': video_url,
                'cover_url': cover_url,
                'download_url': video_url
            }
        except Exception as e:
            print(f"B站 fallback 解析失败: {e}")
            return {'error': f'B站解析失败: {str(e)}'}

    def _parse_youtube(self, url):
        try:
            self._rate_limit()

            ytdlp_options = [
                'yt-dlp',
                '--dump-json',
                '--no-check-certificate',
                '--no-playlist',
                '--user-agent', random.choice(self.user_agents),
            ]

            if self.proxy:
                ytdlp_options.extend(['--proxy', self.proxy])

            ytdlp_options.append(url)

            result = subprocess.run(
                ytdlp_options,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                video_url = video_info.get('url')
                title = video_info.get('title', 'YouTube视频')
                thumbnail = video_info.get('thumbnail')
                duration = video_info.get('duration')
                author = video_info.get('uploader') or video_info.get('channel')
                subtitles = list(video_info.get('subtitles', {}).keys())

                quality_options = []
                if 'formats' in video_info:
                    seen_qualities = set()
                    for fmt in video_info['formats']:
                        if fmt.get('vcodec') != 'none':
                            quality = fmt.get('format_note', 'unknown')
                            if quality not in seen_qualities:
                                seen_qualities.add(quality)
                                format_url = fmt.get('url')
                                if format_url:
                                    quality_options.append({
                                        'quality': quality,
                                        'url': format_url,
                                        'label': f"{quality} - {fmt.get('ext', 'mp4')}"
                                    })

                return {
                    'platform': 'youtube',
                    'title': title,
                    'author': author,
                    'duration': self._format_duration(duration),
                    'video_url': video_url,
                    'cover_url': thumbnail,
                    'download_url': video_url,
                    'quality_options': quality_options[:6] if quality_options else None,
                    'subtitles': subtitles if subtitles else None
                }

            return self._parse_youtube_fallback(url)
        except FileNotFoundError:
            return self._parse_youtube_fallback(url)
        except Exception as e:
            return self._parse_youtube_fallback(url)

    def _parse_youtube_fallback(self, url):
        try:
            self._rate_limit()

            session = self._get_session()
            headers = self._get_random_headers()
            response = session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            title_tag = soup.find('title')
            title = title_tag.text.replace(' - YouTube', '').strip() if title_tag else 'YouTube视频'

            video_url = url
            cover_url = None

            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image:
                cover_url = og_image.get('content')

            return {
                'platform': 'youtube',
                'title': title,
                'video_url': video_url,
                'cover_url': cover_url,
                'download_url': video_url
            }
        except Exception as e:
            return {'error': f'YouTube解析失败: {str(e)}'}

    def _parse_twitter(self, url):
        try:
            self._rate_limit()

            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-check-certificate', '--no-playlist', url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                video_url = video_info.get('url')
                title = video_info.get('description') or video_info.get('title', 'Twitter视频')
                thumbnail = video_info.get('thumbnail')
                duration = video_info.get('duration')
                author = video_info.get('uploader')

                quality_options = []
                if 'formats' in video_info:
                    for fmt in video_info['formats']:
                        if fmt.get('vcodec') != 'none':
                            format_url = fmt.get('url')
                            if format_url:
                                quality_options.append({
                                    'quality': fmt.get('format_note', 'unknown'),
                                    'url': format_url,
                                    'label': f"{fmt.get('format_note', 'unknown')} - {fmt.get('ext', 'mp4')}"
                                })

                return {
                    'platform': 'twitter',
                    'title': title,
                    'author': author,
                    'duration': self._format_duration(duration),
                    'video_url': video_url,
                    'cover_url': thumbnail,
                    'download_url': video_url,
                    'quality_options': quality_options[:4] if quality_options else None
                }

            return self._parse_twitter_fallback(url)
        except FileNotFoundError:
            return self._parse_twitter_fallback(url)
        except Exception as e:
            return self._parse_twitter_fallback(url)

    def _parse_twitter_fallback(self, url):
        try:
            self._rate_limit()

            session = self._get_session()
            headers = self._get_random_headers(referer='https://twitter.com/')
            response = session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            title = title_match.group(1).replace(' on X', '') if title_match else 'Twitter内容'

            video_urls = re.findall(r'video_url\s*:\s*["\']([^"\']+)["\']', response.text)
            video_url = video_urls[0] if video_urls else None

            if video_url:
                video_url = urllib.parse.unquote(video_url)

            cover_match = re.search(r'og:image"?\s*content="([^"]+)"', response.text)
            cover_url = cover_match.group(1) if cover_match else None

            return {
                'platform': 'twitter',
                'title': title,
                'video_url': video_url,
                'cover_url': cover_url,
                'download_url': video_url
            }
        except Exception as e:
            return {'error': f'Twitter解析失败: {str(e)}'}

    def _parse_tiktok(self, url):
        try:
            self._rate_limit()

            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-check-certificate', '--no-playlist', url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                video_url = video_info.get('url')
                title = video_info.get('title', 'TikTok视频')
                thumbnail = video_info.get('thumbnail')
                duration = video_info.get('duration')
                author = video_info.get('uploader') or video_info.get('nickname')

                quality_options = []
                if 'formats' in video_info:
                    for fmt in video_info['formats']:
                        if fmt.get('vcodec') != 'none':
                            format_url = fmt.get('url')
                            if format_url:
                                quality_options.append({
                                    'quality': fmt.get('format_note', 'unknown'),
                                    'url': format_url,
                                    'label': f"{fmt.get('format_note', 'unknown')} - {fmt.get('ext', 'mp4')}"
                                })

                return {
                    'platform': 'tiktok',
                    'title': title,
                    'author': author,
                    'duration': self._format_duration(duration),
                    'video_url': video_url,
                    'cover_url': thumbnail,
                    'download_url': video_url,
                    'quality_options': quality_options[:4] if quality_options else None
                }

            return self._parse_tiktok_fallback(url)
        except FileNotFoundError:
            return self._parse_tiktok_fallback(url)
        except Exception as e:
            return self._parse_tiktok_fallback(url)

    def _parse_tiktok_fallback(self, url):
        try:
            self._rate_limit()

            session = self._get_session()
            headers = self._get_random_headers(referer='https://www.tiktok.com/')
            response = session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            title = title_match.group(1).replace(' | TikTok', '').strip() if title_match else 'TikTok视频'

            video_match = re.search(r'"playAddr"\s*:\s*"([^"]+)"', response.text)
            video_url = video_match.group(1) if video_match else None

            if video_url:
                video_url = urllib.parse.unquote(video_url)

            cover_match = re.search(r'"cover"\s*:\s*"([^"]+)"', response.text)
            cover_url = cover_match.group(1) if cover_match else None

            return {
                'platform': 'tiktok',
                'title': title,
                'video_url': video_url,
                'cover_url': cover_url,
                'download_url': video_url
            }
        except Exception as e:
            return {'error': f'TikTok解析失败: {str(e)}'}

    def _parse_instagram(self, url):
        try:
            self._rate_limit()

            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-check-certificate', url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                video_url = video_info.get('url')
                title = video_info.get('title', 'Instagram内容')
                thumbnail = video_info.get('thumbnail')

                return {
                    'platform': 'instagram',
                    'title': title,
                    'video_url': video_url,
                    'cover_url': thumbnail,
                    'download_url': video_url
                }

            return self._parse_instagram_fallback(url)
        except FileNotFoundError:
            return self._parse_instagram_fallback(url)
        except Exception as e:
            return self._parse_instagram_fallback(url)

    def _parse_instagram_fallback(self, url):
        try:
            self._rate_limit()

            session = self._get_session()
            headers = self._get_random_headers(referer='https://www.instagram.com/')
            response = session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            title = title_match.group(1).replace(' on Instagram', '').strip() if title_match else 'Instagram内容'

            media_urls = re.findall(r'display_url\s*:\s*["\']([^"\']+)["\']', response.text)
            video_urls = re.findall(r'video_url\s*:\s*["\']([^"\']+)["\']', response.text)

            media_url = video_urls[0] if video_urls else media_urls[0] if media_urls else None

            if media_url:
                media_url = urllib.parse.unquote(media_url)

            cover_match = re.search(r'og:image"?\s*content="([^"]+)"', response.text)
            cover_url = cover_match.group(1) if cover_match else None

            return {
                'platform': 'instagram',
                'title': title,
                'video_url': media_url,
                'cover_url': cover_url,
                'download_url': media_url
            }
        except Exception as e:
            return {'error': f'Instagram解析失败: {str(e)}'}

    def _parse_facebook(self, url):
        try:
            self._rate_limit()

            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-check-certificate', url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                video_url = video_info.get('url')
                title = video_info.get('title', 'Facebook视频')
                thumbnail = video_info.get('thumbnail')
                duration = video_info.get('duration')
                author = video_info.get('uploader')

                quality_options = []
                if 'formats' in video_info:
                    for fmt in video_info['formats']:
                        if fmt.get('vcodec') != 'none':
                            format_url = fmt.get('url')
                            if format_url:
                                quality_options.append({
                                    'quality': fmt.get('format_note', 'unknown'),
                                    'url': format_url,
                                    'label': f"{fmt.get('format_note', 'unknown')} - {fmt.get('ext', 'mp4')}"
                                })

                return {
                    'platform': 'facebook',
                    'title': title,
                    'author': author,
                    'duration': self._format_duration(duration),
                    'video_url': video_url,
                    'cover_url': thumbnail,
                    'download_url': video_url,
                    'quality_options': quality_options[:4] if quality_options else None
                }

            return self._parse_facebook_fallback(url)
        except FileNotFoundError:
            return self._parse_facebook_fallback(url)
        except Exception as e:
            return self._parse_facebook_fallback(url)

    def _parse_facebook_fallback(self, url):
        try:
            self._rate_limit()

            session = self._get_session()
            headers = self._get_random_headers(referer='https://www.facebook.com/')
            response = session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            title = title_match.group(1).replace(' | Facebook', '').strip() if title_match else 'Facebook视频'

            hd_video = re.search(r'hd_src\s*:\s*"([^"]+)"', response.text)
            sd_video = re.search(r'sd_src\s*:\s*"([^"]+)"', response.text)
            video_url = hd_video.group(1) if hd_video else sd_video.group(1) if sd_video else None

            if video_url:
                video_url = urllib.parse.unquote(video_url)

            cover_match = re.search(r'og:image"?\s*content="([^"]+)"', response.text)
            cover_url = cover_match.group(1) if cover_match else None

            return {
                'platform': 'facebook',
                'title': title,
                'video_url': video_url,
                'cover_url': cover_url,
                'download_url': video_url
            }
        except Exception as e:
            return {'error': f'Facebook解析失败: {str(e)}'}

    def _parse_onlyfans(self, url):
        try:
            self._rate_limit()

            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--no-check-certificate', url],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                video_url = video_info.get('url')
                title = video_info.get('title', 'OnlyFans内容')
                thumbnail = video_info.get('thumbnail')
                duration = video_info.get('duration')
                author = video_info.get('uploader')

                return {
                    'platform': 'onlyfans',
                    'title': title,
                    'author': author,
                    'duration': self._format_duration(duration),
                    'video_url': video_url,
                    'cover_url': thumbnail,
                    'download_url': video_url
                }

            return {'error': 'OnlyFans解析需要yt-dlp支持，请确保已安装'}
        except FileNotFoundError:
            return {'error': 'OnlyFans解析需要yt-dlp支持，请确保已安装'}
        except Exception as e:
            return {'error': f'OnlyFans解析失败: {str(e)}'}

    def _parse_general(self, url):
        try:
            self._rate_limit()

            session = self._get_session()
            response = session.get(url, headers=self._get_random_headers(), timeout=self.timeout)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')

            if 'video' in content_type:
                return {
                    'platform': 'general',
                    'type': 'video',
                    'title': '视频文件',
                    'video_url': url,
                    'download_url': url
                }
            elif 'image' in content_type:
                return {
                    'platform': 'general',
                    'type': 'image',
                    'title': '图片文件',
                    'image_url': url,
                    'download_url': url
                }
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.text if title_tag else '网页内容'

                return {
                    'platform': 'general',
                    'type': 'webpage',
                    'title': title,
                    'url': url,
                    'download_url': url
                }
        except Exception as e:
            return {'error': f'通用链接解析失败: {str(e)}'}

    def _format_duration(self, seconds):
        if not seconds:
            return None
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes}:{secs:02d}"
        except:
            return str(seconds)