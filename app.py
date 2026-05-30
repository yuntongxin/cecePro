from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import uuid
import json
import cv2
import requests
import subprocess
import time
import re
import random
import urllib.parse
from werkzeug.utils import secure_filename
from utils.video_analyzer import VideoAnalyzer
from utils.image_analyzer import ImageAnalyzer
from utils.prompt_generator import PromptGenerator
from utils.link_parser import LinkParser

app = Flask(__name__)
CORS(app)

# 配置Flask的JSON响应，确保中文正确显示
app.config['JSON_AS_ASCII'] = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'jpg', 'jpeg', 'png', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

video_analyzer = VideoAnalyzer()
image_analyzer = ImageAnalyzer()
prompt_generator = PromptGenerator()
link_parser = LinkParser()

CUSTOM_PROVIDERS_FILE = 'custom_providers.json'
PROVIDERS_FILE = 'providers.json'
HIDDEN_PROVIDERS_FILE = 'hidden_providers.json'

def load_hidden_providers():
    """加载已隐藏的内置供应商ID列表"""
    try:
        if os.path.exists(HIDDEN_PROVIDERS_FILE):
            with open(HIDDEN_PROVIDERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"加载隐藏供应商列表失败: {e}")
        return []

def save_hidden_providers(hidden_ids):
    """保存已隐藏的内置供应商ID列表"""
    with open(HIDDEN_PROVIDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(hidden_ids, f, ensure_ascii=False, indent=2)

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
    """获取所有供应商（内置 + 自定义），过滤掉已隐藏的"""
    builtin = load_builtin_providers()
    custom = load_custom_providers()
    # 为自定义供应商添加 category
    for p in custom:
        if 'category' not in p:
            p['category'] = 'custom'
    # 过滤掉已隐藏的内置供应商
    hidden_ids = load_hidden_providers()
    builtin = [p for p in builtin if p.get('id') not in hidden_ids]
    return builtin + custom

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_custom_providers():
    """加载自定义供应商配置"""
    try:
        if os.path.exists(CUSTOM_PROVIDERS_FILE):
            with open(CUSTOM_PROVIDERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except:
        return []

def save_custom_providers(providers):
    """保存自定义供应商配置"""
    with open(CUSTOM_PROVIDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(providers, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze_video', methods=['POST'])
def analyze_video():
    try:
        if 'video' not in request.files:
            return jsonify({'error': '请上传视频文件'}), 400

        file = request.files['video']

        if file.filename == '':
            return jsonify({'error': '请上传视频文件'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的视频格式，请上传 MP4, AVI, MOV, MKV, WEBM 格式'}), 400

        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        analysis_mode = request.form.get('analysis_mode', 'auto')
        analysis_params = request.form.get('analysis_params', '{}')
        provider_config = request.form.get('provider_config')

        # 解析分析参数
        try:
            analysis_params = json.loads(analysis_params)
        except:
            analysis_params = {}

        # 计算帧数
        if analysis_mode == 'auto':
            # 自动模式：根据视频时长计算
            cap = cv2.VideoCapture(filepath)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            
            if duration < 10:
                max_frames = 3
            elif duration < 60:
                max_frames = 5
            else:
                max_frames = min(10, int(duration / 6) + 3)
        elif analysis_mode == 'custom':
            # 自定义帧数
            custom_frames = analysis_params.get('frames', 5)
            max_frames = max(3, min(custom_frames, 30))
        else:  # interval
            # 按时间间隔
            cap = cv2.VideoCapture(filepath)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            
            # 计算帧数，确保最少3帧
            frame_interval = analysis_params.get('interval', 2)
            calculated_frames = int(duration / frame_interval) + 1
            max_frames = max(3, min(calculated_frames, 30))

        # 处理供应商配置
        custom_config = None
        if provider_config:
            try:
                custom_config = json.loads(provider_config)
                print(f"从请求中获取供应商配置: {custom_config}")
            except:
                pass

        analysis_result = video_analyzer.analyze(filepath)
        print(f"视频分析结果: {analysis_result}")
        print(f"分析模式: {analysis_mode}")
        print(f"最大帧数: {max_frames}")
        print(f"供应商配置: {custom_config}")

        # 使用基于关键帧的提示词生成
        prompt_result = prompt_generator.generate_with_video(
            filepath,
            analysis_result,
            custom_config=custom_config,
            max_frames=max_frames
        )
        print(f"提示词生成结果: {prompt_result}")

        os.remove(filepath)

        # 如果没有配置模型，返回错误
        if prompt_result is None:
            return jsonify({'error': '提示词生成失败，请检查：1) 是否已选择供应商 2) API Key是否正确 3) 模型是否支持图片/视频分析（需要多模态模型）'}), 400

        # 格式化返回结果
        result = {
            'duration': analysis_result.get('duration', '00:00'),
            'fps': analysis_result.get('fps', 0),
            'resolution': analysis_result.get('resolution', '0x0'),
            'dominant_color': analysis_result.get('colors', {}).get('dominant', '#000000'),
            'warmth': analysis_result.get('colors', {}).get('warmth', '中性'),
            'saturation': analysis_result.get('colors', {}).get('saturation', '中等'),
            'brightness': analysis_result.get('colors', {}).get('brightness', '中等'),
            'motion_level': analysis_result.get('motion', {}).get('level', '低'),
            'scene_type': analysis_result.get('scenes', {}).get('main', '未知'),
            'prompts': [prompt_result] if prompt_result else []
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': '请上传图片文件'}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({'error': '请上传图片文件'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的图片格式，请上传 JPG, PNG, GIF, WEBP 格式'}), 400

        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        provider_config = request.form.get('provider_config')

        # 处理供应商配置
        custom_config = None
        if provider_config:
            try:
                custom_config = json.loads(provider_config)
                print(f"从请求中获取供应商配置: {custom_config}")
            except:
                pass

        analysis_result = image_analyzer.analyze(filepath)
        print(f"图片分析结果: {analysis_result}")

        # 格式化分析结果
        formatted_analysis = {
            'resolution': f"{analysis_result.get('width', 0)} x {analysis_result.get('height', 0)}",
            'dominant_color': analysis_result.get('colors', {}).get('dominant', '#000000'),
            'warmth': analysis_result.get('colors', {}).get('warmth', '中性'),
            'saturation': analysis_result.get('colors', {}).get('saturation', '中等'),
            'brightness': analysis_result.get('colors', {}).get('brightness', '中等'),
            'motion_level': '静态',
            'scene_type': analysis_result.get('scenes', {}).get('main', '未知'),
            'prompts': []
        }

        # 生成提示词
        prompt_result = prompt_generator.generate_with_image(
            filepath,
            formatted_analysis,
            custom_config=custom_config
        )
        print(f"提示词生成结果: {prompt_result}")

        os.remove(filepath)

        # 如果没有配置模型，返回错误
        if prompt_result is None:
            return jsonify({'error': '提示词生成失败，请检查：1) 是否已选择供应商 2) API Key是否正确 3) 模型是否支持图片/视频分析（需要多模态模型）'}), 400

        formatted_analysis['prompts'] = [prompt_result] if prompt_result else []

        return jsonify(formatted_analysis)

    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

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

@app.route('/providers/<provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    """删除供应商（支持内置和自定义）"""
    try:
        # 先检查是否是自定义供应商
        custom_providers = load_custom_providers()
        is_custom = any(p.get('id') == provider_id for p in custom_providers)

        if is_custom:
            # 删除自定义供应商
            custom_providers = [p for p in custom_providers if p.get('id') != provider_id]
            save_custom_providers(custom_providers)
        else:
            # 隐藏内置供应商
            hidden_ids = load_hidden_providers()
            if provider_id not in hidden_ids:
                hidden_ids.append(provider_id)
                save_hidden_providers(hidden_ids)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/providers/restore', methods=['POST'])
def restore_providers():
    """恢复所有被隐藏的内置供应商"""
    try:
        save_hidden_providers([])
        return jsonify({'success': True, 'message': '已恢复所有内置供应商'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test_connection', methods=['POST'])
def test_connection():
    try:
        data = request.get_json()
        provider_config = data.get('provider_config')

        # 处理供应商配置
        custom_config = None
        discovered_endpoint = None
        if provider_config:
            try:
                custom_config = provider_config
                print(f"从请求中获取供应商配置: {custom_config}")
            except:
                pass

        # 测试连接
        success = prompt_generator.test_connection(custom_config=custom_config)
        
        if success:
            # 检查是否发现了新的端点
            discovered_endpoint = custom_config.get('endpoint') if custom_config else None
            response = {
                'success': True,
                'message': '连接测试成功！'
            }
            if discovered_endpoint and discovered_endpoint != provider_config.get('endpoint'):
                response['discovered_endpoint'] = discovered_endpoint
                response['message'] = f'连接测试成功！发现正确的端点: {discovered_endpoint}'
            return jsonify(response)
        else:
            return jsonify({'success': False, 'error': '连接测试失败，请检查配置'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/parse_link', methods=['POST'])
def parse_link():
    try:
        data = request.get_json()
        if not data:
            response = jsonify({'error': '请提供链接信息'})
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
        
        url = data.get('url')
        platform = data.get('platform')
        
        if not url:
            response = jsonify({'error': '请输入链接'})
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
        
        # 解析链接
        result = link_parser.parse_link(url, platform)
        
        if 'error' in result:
            response = jsonify(result)
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
        
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        response = jsonify({'error': f'解析失败: {str(e)}'})
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 500

def _get_douyin_cookies():
    """获取抖音基础Cookie（ttwid等），用于yt-dlp"""
    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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


def _ytdlp_download(url, platform, filename):
    """使用yt-dlp下载视频，返回下载的文件路径"""
    import tempfile
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    cmd = [
        'yt-dlp',
        '--no-check-certificate',
        '--no-playlist',
        '--user-agent', ua,
        '-o', output_template,
    ]

    # 平台特定Referer
    referers = {
        'bilibili': 'https://www.bilibili.com/',
        'douyin': 'https://www.douyin.com/',
        'youtube': 'https://www.youtube.com/',
        'tiktok': 'https://www.tiktok.com/',
        'twitter': 'https://twitter.com/',
        'instagram': 'https://www.instagram.com/',
        'facebook': 'https://www.facebook.com/',
    }
    referer = referers.get(platform)
    if referer:
        cmd.extend(['--referer', referer])

    # 抖音需要Cookie
    if platform == 'douyin' or 'douyin.com' in url:
        cookie_file = _get_douyin_cookies()
        if cookie_file:
            cmd.extend(['--cookies', cookie_file])

    cmd.append(url)

    print(f"执行yt-dlp: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    print(f"yt-dlp 退出码: {result.returncode}")
    if result.stderr:
        print(f"yt-dlp stderr: {result.stderr[:500]}")

    if result.returncode != 0:
        return None, result.stderr

    # 找到下载的文件
    files = os.listdir(temp_dir) if os.path.exists(temp_dir) else []
    if not files:
        return None, 'yt-dlp 未生成文件'

    downloaded = os.path.join(temp_dir, files[0])
    return downloaded, None


@app.route('/download_proxy')
def download_proxy():
    import tempfile
    try:
        url = request.args.get('url')
        filename = request.args.get('filename', 'download')
        platform = request.args.get('platform', '')

        if not url:
            response = jsonify({'error': '请提供下载链接'})
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400

        url = urllib.parse.unquote(url)
        filename = urllib.parse.unquote(filename)

        print(f"开始下载: {url}")
        print(f"平台: {platform}")

        # 检查是否是CDN直链（跳过yt-dlp，直接用HTTP下载）
        is_cdn_url = any(cdn in url for cdn in [
            'douyinvod.com', 'bytevcloudcdn.com', 'bytecdn.cn',
            'tiktokcdn.com', 'tikcdn.com',
            'cdninstagram.com', 'fbcdn.net',
            'video.twimg.com', 'pbs.twimg.com',
            'googlevideo.com', 'ytimg.com',
        ])

        downloaded_file = None
        error = None

        if is_cdn_url:
            print(f"检测到CDN直链，跳过yt-dlp直接下载...")
        else:
            # Step 1: 尝试yt-dlp下载（适用于非CDN链接）
            print("使用 yt-dlp 下载...")
            downloaded_file, error = _ytdlp_download(url, platform, filename)

        if downloaded_file and os.path.exists(downloaded_file):
            try:
                file_size = os.path.getsize(downloaded_file)
                # 读取文件内容
                with open(downloaded_file, 'rb') as f:
                    content = f.read()

                # 确定文件类型和扩展名
                ext = os.path.splitext(downloaded_file)[1] or '.mp4'
                if ext in ('.m4s',):
                    ext = '.mp4'

                safe_name = re.sub(r'[^\w\s\-\.]', '', filename)
                if not safe_name or safe_name == 'download':
                    safe_name = f'video_{int(time.time())}'
                download_name = f'{safe_name}{ext}'

                content_type = 'video/mp4'
                if ext in ('.jpg', '.jpeg'):
                    content_type = 'image/jpeg'
                elif ext == '.png':
                    content_type = 'image/png'
                elif ext == '.gif':
                    content_type = 'image/gif'
                elif ext == '.webp':
                    content_type = 'image/webp'
                elif ext == '.webm':
                    content_type = 'video/webm'

                print(f"下载成功: {download_name} ({file_size} bytes)")

                return Response(
                    content,
                    content_type=content_type,
                    headers={
                        'Content-Disposition': f'attachment; filename="{download_name}"',
                        'Content-Length': str(file_size),
                        'Cache-Control': 'no-cache',
                        'Access-Control-Allow-Origin': '*',
                    }
                )
            finally:
                # 清理临时目录
                try:
                    os.remove(downloaded_file)
                    os.rmdir(os.path.dirname(downloaded_file))
                except:
                    pass

        # Step 2: yt-dlp失败或CDN直链，尝试直接下载
        print(f"尝试直接HTTP下载...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'identity',
                'Connection': 'keep-alive',
            }

            referers = {
                'bilibili': 'https://www.bilibili.com/',
                'douyin': 'https://www.douyin.com/',
                'youtube': 'https://www.youtube.com/',
                'tiktok': 'https://www.tiktok.com/',
                'twitter': 'https://twitter.com/',
                'instagram': 'https://www.instagram.com/',
                'facebook': 'https://www.facebook.com/',
            }
            if platform in referers:
                headers['Referer'] = referers[platform]

            # 对于抖音CDN，额外设置Origin
            if is_cdn_url and 'douyin' in url:
                headers['Origin'] = 'https://www.douyin.com'

            print(f"请求头: {json.dumps(headers, indent=2, ensure_ascii=False)}")
            resp = requests.get(url, headers=headers, stream=True, timeout=60)
            resp.raise_for_status()

            content_type = resp.headers.get('Content-Type', 'application/octet-stream')
            content_length = resp.headers.get('Content-Length', '0')

            safe_name = re.sub(r'[^\w\s\-\.]', '', filename)
            if not safe_name or safe_name == 'download':
                safe_name = f'download_{int(time.time())}'

            # 根据Content-Type确定扩展名
            ext = '.mp4'
            if 'image' in content_type:
                if 'png' in content_type: ext = '.png'
                elif 'gif' in content_type: ext = '.gif'
                elif 'webp' in content_type: ext = '.webp'
                else: ext = '.jpg'
            elif 'webm' in content_type:
                ext = '.webm'

            download_name = f'{safe_name}{ext}'

            def generate():
                try:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                finally:
                    resp.close()

            return Response(
                generate(),
                content_type=content_type,
                headers={
                    'Content-Disposition': f'attachment; filename="{download_name}"',
                    'Content-Length': content_length,
                    'Cache-Control': 'no-cache',
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            print(f"直接下载也失败: {e}")
            response = jsonify({
                'error': f'下载失败: {error or str(e)}',
                'hint': '可能是平台反爬限制或链接已过期，请重新解析后重试'
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 500

    except Exception as e:
        print(f"下载失败: {str(e)}")
        response = jsonify({'error': f'下载失败: {str(e)}'})
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500

@app.route('/image_proxy')
def image_proxy():
    try:
        url = request.args.get('url')
        if not url:
            return '', 400

        url = urllib.parse.unquote(url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com'
        }

        if 'hdslb.com' in url or 'bilibili.com' in url:
            headers['Referer'] = 'https://www.bilibili.com/'
        elif 'douyin.com' in url:
            headers['Referer'] = 'https://www.douyin.com/'
        elif 'youtube.com' in url:
            headers['Referer'] = 'https://www.youtube.com/'
        elif 'tiktok.com' in url:
            headers['Referer'] = 'https://www.tiktok.com/'
        elif 'instagram.com' in url:
            headers['Referer'] = 'https://www.instagram.com/'
        elif 'twitter.com' in url or 'x.com' in url:
            headers['Referer'] = 'https://twitter.com/'
        elif 'facebook.com' in url:
            headers['Referer'] = 'https://www.facebook.com/'

        response = requests.get(url, headers=headers, stream=True, timeout=15)
        content_type = response.headers.get('Content-Type', 'image/jpeg')

        return Response(
            response.iter_content(chunk_size=8192),
            content_type=content_type,
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': '*'
            }
        )
    except Exception as e:
        return '', 404

@app.route('/download_video')
def download_video():
    try:
        url = request.args.get('url')
        if not url:
            response = jsonify({'error': '请提供视频链接'})
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 400
        
        # 检查是否是直接的视频文件链接
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 处理重定向
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10, stream=True)
            real_url = response.url
            content_type = response.headers.get('Content-Type', '')
            print(f"重定向后的真实URL: {real_url}")
            print(f"内容类型: {content_type}")
            
            # 如果是直接的视频文件，直接下载
            if 'video' in content_type:
                # 获取文件名
                filename = real_url.split('/')[-1]
                # 清理文件名，去除URL参数
                if '?' in filename:
                    filename = filename.split('?')[0]
                
                # 从Content-Disposition获取文件名
                if 'content-disposition' in response.headers:
                    content_disposition = response.headers['content-disposition']
                    if 'filename=' in content_disposition:
                        cd_filename = content_disposition.split('filename=')[1].strip('"')
                        # 清理Content-Disposition中的文件名
                        if '?' in cd_filename:
                            cd_filename = cd_filename.split('?')[0]
                        filename = cd_filename
                
                # 确保文件名有扩展名
                if not any(filename.endswith(ext) for ext in ['.mp4', '.flv', '.avi', '.mkv', '.webm']):
                    # 根据内容类型添加合适的扩展名
                    if 'mp4' in content_type:
                        filename = f"{filename}.mp4"
                    elif 'webm' in content_type:
                        filename = f"{filename}.webm"
                    elif 'flv' in content_type:
                        filename = f"{filename}.flv"
                    else:
                        filename = f"video_{int(time.time())}.mp4"
                
                # 读取视频内容
                video_content = response.content
                
                # 返回视频文件
                return Response(
                    video_content,
                    content_type=content_type,
                    headers={
                        'Content-Disposition': f'attachment; filename={filename}'
                    }
                )
        except Exception as e:
            print(f"直接下载失败: {str(e)}")
        
        # 如果不是直接的视频文件，使用yt-dlp尝试下载
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 使用 yt-dlp 下载视频，添加更多参数以提高成功率
            result = subprocess.run(
                ['yt-dlp', '-o', f'{temp_dir}/%(title)s.%(ext)s', '--no-check-certificate', '--user-agent', headers['User-Agent'], url],
                capture_output=True, text=True, timeout=60
            )
            
            print(f"yt-dlp 退出码: {result.returncode}")
            print(f"yt-dlp 输出: {result.stdout}")
            print(f"yt-dlp 错误: {result.stderr}")
            
            if result.returncode == 0:
                # 找到下载的视频文件
                video_files = [f for f in os.listdir(temp_dir) if f.endswith(('.mp4', '.flv', '.avi', '.mkv'))]
                if video_files:
                    video_path = os.path.join(temp_dir, video_files[0])
                    # 读取视频文件
                    with open(video_path, 'rb') as f:
                        video_content = f.read()
                    # 清理文件名
                    clean_filename = video_files[0]
                    # 确保文件名有扩展名
                    if not any(clean_filename.endswith(ext) for ext in ['.mp4', '.flv', '.avi', '.mkv', '.webm']):
                        clean_filename = f"{clean_filename}.mp4"
                    
                    # 返回视频文件
                    return Response(
                        video_content,
                        content_type='video/mp4',
                        headers={
                            'Content-Disposition': f'attachment; filename={clean_filename}'
                        }
                    )
            
            # 如果yt-dlp失败，尝试使用link_parser解析链接
            try:
                from utils.link_parser import LinkParser
                link_parser = LinkParser()
                parse_result = link_parser.parse_link(url)
                print(f"解析结果: {parse_result}")
                
                if 'video_url' in parse_result and parse_result['video_url']:
                    video_url = parse_result['video_url']
                    # 尝试直接下载解析出的视频链接
                    response = requests.get(video_url, headers=headers, timeout=30, stream=True)
                    if response.status_code == 200:
                        # 获取文件名
                        filename = video_url.split('/')[-1]
                        if 'content-disposition' in response.headers:
                            content_disposition = response.headers['content-disposition']
                            if 'filename=' in content_disposition:
                                filename = content_disposition.split('filename=')[1].strip('"')
                        
                        # 读取视频内容
                        video_content = response.content
                        
                        # 返回视频文件
                        return Response(
                            video_content,
                            content_type=response.headers.get('Content-Type', 'video/mp4'),
                            headers={
                                'Content-Disposition': f'attachment; filename={filename}'
                            }
                        )
            except Exception as e:
                print(f"解析下载失败: {str(e)}")
            
            return jsonify({'error': '下载失败，请检查链接是否有效'}), 400
    except Exception as e:
        # 确保错误信息能够正确显示
        error_msg = str(e)
        print(f"下载错误: {error_msg}")
        # 修复编码问题，确保中文能正确显示
        response = jsonify({'error': f'下载失败: {error_msg}'})
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 500

if __name__ == '__main__':
    print("=" * 60)
    print("  视频AI解析助手")
    print("  访问地址: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)