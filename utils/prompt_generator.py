import requests
import json
import os
import base64
import time

class PromptGenerator:

    def __init__(self):
        self.api_endpoints = {
            # 国际主流
            'openai': {
                'name': 'OpenAI GPT',
                'endpoint': 'https://api.openai.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://platform.openai.com',
                'free_credit': '需付费',
                'note': '国际主流模型',
                'api_format': 'openai'
            },
            'anthropic': {
                'name': 'Anthropic Claude',
                'endpoint': 'https://api.anthropic.com/v1/messages',
                'model': 'claude-3-haiku-20240307',
                'website': 'https://www.anthropic.com',
                'free_credit': '需付费',
                'note': '英文能力强',
                'api_format': 'anthropic'
            },
            'google': {
                'name': 'Google Gemini',
                'endpoint': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-lite:generateContent',
                'model': 'gemini-1.5-flash-lite',
                'website': 'https://ai.google.dev',
                'free_credit': '有免费额度',
                'note': '多模态能力强',
                'api_format': 'google'
            },

            # 国内平台
            'siliconflow': {
                'name': '硅基流动 SiliconFlow',
                'endpoint': 'https://api.siliconflow.cn/v1/chat/completions',
                'model': 'Qwen/Qwen2.5-7B-Instruct',
                'website': 'https://www.siliconflow.cn',
                'free_credit': '注册送15元额度',
                'note': '高性能AI基础设施',
                'promo': 'https://www.siliconflow.cn?utm_source=video-ai',
                'api_format': 'openai'
            },
            'deepseek': {
                'name': 'DeepSeek',
                'endpoint': 'https://api.deepseek.com/v1/chat/completions',
                'model': 'deepseek-chat',
                'website': 'https://platform.deepseek.com',
                'free_credit': '注册送一定额度',
                'note': '国产高性能',
                'api_format': 'openai'
            },
            'zhipu': {
                'name': '智谱AI GLM',
                'endpoint': 'https://open.bigmodel.cn/api/paas/v4/chat/completions',
                'model': 'glm-4-flash',
                'website': 'https://open.bigmodel.cn',
                'free_credit': '注册送Token',
                'note': '中文理解好',
                'api_format': 'openai'
            },
            'minimax': {
                'name': 'MiniMax',
                'endpoint': 'https://api.minimax.chat/v1/text/chatcompletion_v2',
                'model': 'abab6.5s-chat',
                'website': 'https://www.minimax.chat',
                'free_credit': '注册送Token',
                'note': '响应快',
                'api_format': 'openai'
            },
            'kimi': {
                'name': 'Kimi 月之暗面',
                'endpoint': 'https://api.moonshot.cn/v1/chat/completions',
                'model': 'moonshot-v1-8k',
                'website': 'https://platform.moonshot.cn',
                'free_credit': '注册送额度',
                'note': '长上下文',
                'api_format': 'openai'
            },
            'doubao': {
                'name': '豆包 字节跳动',
                'endpoint': 'https://ark.cn-beijing.volces.com/api/v3/chat/completions',
                'model': 'doubao-pro-32k',
                'website': 'https://www.volcengine.com/product/doubao',
                'free_credit': '注册送额度',
                'note': '字节跳动',
                'api_format': 'openai'
            },
            'modelscope': {
                'name': 'ModelScope 魔搭',
                'endpoint': 'https://modelscope.cn/api/v1/chat/completions',
                'model': 'Qwen/Qwen2.5-7B-Instruct',
                'website': 'https://modelscope.cn',
                'free_credit': '有免费额度',
                'note': '阿里模型市场',
                'api_format': 'openai'
            },
            'gitee': {
                'name': 'Gitee AI',
                'endpoint': 'https://openai.api.gitee.com/v1/chat/completions',
                'model': 'Qwen/Qwen2.5-7B-Instruct',
                'website': 'https://ai.gitee.com',
                'free_credit': '有免费额度',
                'note': '码云AI',
                'api_format': 'openai'
            },
            'tongyi': {
                'name': '通义千问',
                'endpoint': 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',
                'model': 'qwen-turbo',
                'website': 'https://dashscope.console.aliyun.com',
                'free_credit': '有免费额度',
                'note': '阿里云',
                'api_format': 'openai'
            },
            'baidu': {
                'name': '百度文心一言',
                'endpoint': 'https://qianfan.aiap.baidu.com/v2/chat/completions',
                'model': 'ernie-4.0-8k-latest',
                'website': 'https://console.bce.baidu.com',
                'free_credit': '注册送额度',
                'note': '百度智能云',
                'api_format': 'openai'
            },
            'tencent': {
                'name': '腾讯混元',
                'endpoint': 'https://api.hunyuan.cloud.tencent.com/v1/chat/completions',
                'model': 'hunyuan-pro',
                'website': 'https://cloud.tencent.com/product/hunyuan',
                'free_credit': '注册送额度',
                'note': '腾讯云',
                'api_format': 'openai'
            },

            # API中继服务（参考 cc-switch 50+供应商）
            'packycode': {
                'name': 'PackyCode',
                'endpoint': 'https://api.packycode.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://packycode.com',
                'free_credit': '首充10%折扣',
                'note': '稳定的API中继服务',
                'promo': 'https://packycode.com?code=cc-switch',
                'api_format': 'openai'
            },
            'aigocode': {
                'name': 'AIGoCode',
                'endpoint': 'https://api.aigocode.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://aigocode.com',
                'free_credit': '首充10% bonus',
                'note': '集成多种模型',
                'promo': 'https://aigocode.com?ref=cc-switch',
                'api_format': 'openai'
            },
            'shengsuanyun': {
                'name': '胜算云 Shengsuanyun',
                'endpoint': 'https://api.shengsuanyun.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://shengsuanyun.com',
                'free_credit': '注册送10元',
                'note': '工业级AI任务平台',
                'promo': 'https://shengsuanyun.com?ref=cc-switch',
                'api_format': 'openai'
            },
            'aicodemirror': {
                'name': 'AICodeMirror',
                'endpoint': 'https://api.aicodemirror.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://aicodemirror.com',
                'free_credit': '首充20%折扣',
                'note': '企业级稳定性',
                'promo': 'https://aicodemirror.com?ref=cc-switch',
                'api_format': 'openai'
            },
            'cubence': {
                'name': 'Cubence',
                'endpoint': 'https://api.cubence.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://cubence.com',
                'free_credit': '每次充值10%折扣',
                'note': '灵活计费选项',
                'promo': 'https://cubence.com?code=CCSWITCH',
                'api_format': 'openai'
            },
            'dmxapi': {
                'name': 'DMXAPI',
                'endpoint': 'https://api.dmxapi.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://dmxapi.com',
                'free_credit': 'GPT/Claude/Gemini 32% off',
                'note': '全球大模型API服务',
                'promo': 'https://dmxapi.com',
                'api_format': 'openai'
            },
            'compshare': {
                'name': 'Compshare',
                'endpoint': 'https://api.compshare.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://compshare.com',
                'free_credit': '官方价格60-80% off',
                'note': 'UCloud AI云平台',
                'promo': 'https://compshare.com?ref=cc-switch',
                'api_format': 'openai'
            },
            'aicoding': {
                'name': 'AICoding.sh',
                'endpoint': 'https://api.aicoding.sh/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://aicoding.sh',
                'free_credit': '首充优惠',
                'note': 'Claude Code 19%原价',
                'promo': 'https://aicoding.sh?code=cc-switch',
                'api_format': 'openai'
            },
            'crazyrouter': {
                'name': 'Crazyrouter',
                'endpoint': 'https://api.crazyrouter.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://crazyrouter.ai',
                'free_credit': '注册送$2额度',
                'note': '300+模型聚合平台',
                'promo': 'https://crazyrouter.ai?code=CCSWITCH',
                'api_format': 'openai'
            },
            'rightcode': {
                'name': 'Right Code',
                'endpoint': 'https://api.rightcode.io/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://rightcode.io',
                'free_credit': '有免费额度',
                'note': 'Codex月度订阅',
                'promo': 'https://rightcode.io?code=cc-switch',
                'api_format': 'openai'
            },
            'sssaicode': {
                'name': 'SSSAiCode',
                'endpoint': 'https://api.sssaicode.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://sssaicode.com',
                'free_credit': '首充$10 bonus',
                'note': '稳定可靠的Claude服务',
                'promo': 'https://sssaicode.com?code=cc-switch',
                'api_format': 'openai'
            },
            'micuapi': {
                'name': 'Micu API',
                'endpoint': 'https://api.micuapi.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://micuapi.com',
                'free_credit': '最低1元充值',
                'note': '零成本试用',
                'promo': 'https://micuapi.com?code=ccswitch',
                'api_format': 'openai'
            },
            'lemondata': {
                'name': 'LemonData',
                'endpoint': 'https://api.lemondata.ai/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://lemondata.ai',
                'free_credit': '注册送$1',
                'note': '300+模型 API聚合',
                'promo': 'https://lemondata.ai?code=cc-switch',
                'api_format': 'openai'
            },
            'ctok': {
                'name': 'CTok.ai',
                'endpoint': 'https://api.ctok.ai/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://ctok.ai',
                'free_credit': '有免费额度',
                'note': 'Claude Code套餐',
                'promo': 'https://ctok.ai?code=cc-switch',
                'api_format': 'openai'
            },
            'lioncc': {
                'name': 'LionCC',
                'endpoint': 'https://api.lioncc.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://lioncc.com',
                'free_credit': '首充送$10',
                'note': '低延迟Claude服务',
                'promo': 'https://lioncc.com?code=cc-switch',
                'api_format': 'openai'
            },
            'dds': {
                'name': 'DDS Hub',
                'endpoint': 'https://api.ddshub.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://ddshub.com',
                'free_credit': '首充10% bonus',
                'note': 'Claude API代理',
                'promo': 'https://ddshub.com?code=cc-switch',
                'api_format': 'openai'
            },
            'chefshop': {
                'name': 'ChefShop AI',
                'endpoint': 'https://api.chefshop.ai/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://chefshop.ai',
                'free_credit': '有免费试用',
                'note': 'Plus/Pro账户服务',
                'api_format': 'openai'
            },
            'newapi': {
                'name': 'NewAPI',
                'endpoint': 'https://api.newapi.ai/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://newapi.ai',
                'free_credit': '注册送额度',
                'note': '全球大模型API服务',
                'api_format': 'openai'
            },
            'gemai': {
                'name': 'GemAI',
                'endpoint': 'https://api.gemai.cc/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://gemai.cc',
                'free_credit': '注册送额度',
                'note': '稳定的API中继服务',
                'api_format': 'openai'
            },
            'apikeycenter': {
                'name': 'APIKeyCenter',
                'endpoint': 'https://api.apikeycenter.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://apikeycenter.com',
                'free_credit': '首充优惠',
                'note': 'API密钥管理平台',
                'api_format': 'openai'
            },
            'ai71': {
                'name': 'AI71',
                'endpoint': 'https://api.ai71.ai/v1/chat/completions',
                'model': 'ai71-llama-3.1-405b-instruct',
                'website': 'https://ai71.com',
                'free_credit': '有免费额度',
                'note': '高性能模型服务',
                'api_format': 'openai'
            },
            'together': {
                'name': 'Together AI',
                'endpoint': 'https://api.together.xyz/v1/chat/completions',
                'model': 'meta-llama/Llama-3.1-405B-Instruct-Turbo',
                'website': 'https://together.ai',
                'free_credit': '注册送额度',
                'note': '开源模型托管平台',
                'api_format': 'openai'
            },
            'groq': {
                'name': 'Groq',
                'endpoint': 'https://api.groq.com/openai/v1/chat/completions',
                'model': 'llama3-8b-8192',
                'website': 'https://groq.com',
                'free_credit': '有免费额度',
                'note': '高速推理服务',
                'api_format': 'openai'
            },
            'perplexity': {
                'name': 'Perplexity AI',
                'endpoint': 'https://api.perplexity.ai/chat/completions',
                'model': 'llama-3-sonar-small-32k-chat',
                'website': 'https://www.perplexity.ai',
                'free_credit': '有免费额度',
                'note': '搜索增强型AI',
                'api_format': 'openai'
            },
            'awsbedrock': {
                'name': 'AWS Bedrock',
                'endpoint': 'https://bedrock.us-east-1.amazonaws.com/model',
                'model': 'anthropic.claude-3-haiku-20240307-v1:0',
                'website': 'https://aws.amazon.com/bedrock',
                'free_credit': '需付费',
                'note': '亚马逊云科技',
                'api_format': 'openai'
            },
            'nvidianim': {
                'name': 'NVIDIA NIM',
                'endpoint': 'https://integrate.api.nvidia.com/v1/chat/completions',
                'model': 'meta/llama-3.1-405b-instruct',
                'website': 'https://developer.nvidia.com/nim',
                'free_credit': '有免费额度',
                'note': '英伟达AI模型',
                'api_format': 'openai'
            },
            'cloudflare': {
                'name': 'Cloudflare Workers AI',
                'endpoint': 'https://api.cloudflare.com/v1/chat/completions',
                'model': '@cf/meta/llama-3.1-405b-instruct',
                'website': 'https://developers.cloudflare.com/workers-ai',
                'free_credit': '有免费额度',
                'note': '边缘AI服务',
                'api_format': 'openai'
            },
            'cohere': {
                'name': 'Cohere',
                'endpoint': 'https://api.cohere.ai/v1/chat',
                'model': 'command-r-plus',
                'website': 'https://cohere.com',
                'free_credit': '有免费额度',
                'note': '企业级AI平台',
                'api_format': 'openai'
            },
            'mistral': {
                'name': 'Mistral AI',
                'endpoint': 'https://api.mistral.ai/v1/chat/completions',
                'model': 'mistral-large-latest',
                'website': 'https://mistral.ai',
                'free_credit': '需付费',
                'note': '欧洲AI初创公司',
                'api_format': 'openai'
            },
            'anyscale': {
                'name': 'Anyscale',
                'endpoint': 'https://api.endpoints.anyscale.com/v1/chat/completions',
                'model': 'meta-llama/Llama-3.1-405B-Instruct-Turbo',
                'website': 'https://anyscale.com',
                'free_credit': '有免费额度',
                'note': '分布式AI平台',
                'api_format': 'openai'
            },
            'openrouter': {
                'name': 'OpenRouter',
                'endpoint': 'https://openrouter.ai/api/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://openrouter.ai',
                'free_credit': '有免费额度',
                'note': '多模型聚合',
                'api_format': 'openai'
            },
            'vexyclaude': {
                'name': 'VexyClaude',
                'endpoint': 'https://api.vexyclaude.com/v1/chat/completions',
                'model': 'claude-3-opus',
                'website': 'https://vexyclaude.com',
                'free_credit': '有免费试用',
                'note': 'Claude专用服务',
                'api_format': 'openai'
            },
            'sambanova': {
                'name': 'SambaNova',
                'endpoint': 'https://api.sambanova.ai/v1/chat/completions',
                'model': 'Meta-Llama-3.1-405B-Instruct',
                'website': 'https://sambanova.ai',
                'free_credit': '注册送额度',
                'note': '企业级AI平台',
                'api_format': 'openai'
            },
            'wavefunction': {
                'name': 'WaveFunction',
                'endpoint': 'https://api.wavefunction.ai/v1/chat/completions',
                'model': 'llama-3.1-405b',
                'website': 'https://wavefunction.ai',
                'free_credit': '有免费额度',
                'note': 'AI模型服务',
                'api_format': 'openai'
            },
            'abacus': {
                'name': 'Abacus AI',
                'endpoint': 'https://api.abacus.ai/v1/chat/completions',
                'model': 'meta-llama-3.1-405b-instruct',
                'website': 'https://abacus.ai',
                'free_credit': '注册送Token',
                'note': '企业AI平台',
                'api_format': 'openai'
            },
            'fireworks': {
                'name': 'Fireworks AI',
                'endpoint': 'https://api.fireworks.ai/v1/chat/completions',
                'model': 'accounts/fireworks/models/llama-v3p1-405b-instruct',
                'website': 'https://fireworks.ai',
                'free_credit': '注册送额度',
                'note': '高速推理平台',
                'api_format': 'openai'
            },
            'replicate': {
                'name': 'Replicate',
                'endpoint': 'https://api.replicate.com/v1/chat/completions',
                'model': 'meta/llama-3.1-405b-instruct',
                'website': 'https://replicate.com',
                'free_credit': '有免费额度',
                'note': 'AI模型托管',
                'api_format': 'openai'
            },
            'hyperbolic': {
                'name': 'Hyperbolic',
                'endpoint': 'https://api.hyperbolic.ai/v1/chat/completions',
                'model': 'meta-llama/Llama-3.1-405B-Instruct',
                'website': 'https://hyperbolic.xyz',
                'free_credit': '注册送额度',
                'note': '开放AI平台',
                'api_format': 'openai'
            },
            'novy': {
                'name': 'Novy AI',
                'endpoint': 'https://api.novy.ai/v1/chat/completions',
                'model': 'claude-3-5-sonnet',
                'website': 'https://novy.ai',
                'free_credit': '有免费额度',
                'note': '多模型服务',
                'api_format': 'openai'
            },
            'instabase': {
                'name': 'Instabase',
                'endpoint': 'https://api.instabase.com/v1/chat/completions',
                'model': 'claude-3-opus',
                'website': 'https://instabase.com',
                'free_credit': '需联系销售',
                'note': '企业文档AI',
                'api_format': 'openai'
            },
            'writer': {
                'name': 'Writer API',
                'endpoint': 'https://api.writer.com/v1/chat/completions',
                'model': 'palmyra-instruct',
                'website': 'https://writer.com',
                'free_credit': '有免费试用',
                'note': '企业写作AI',
                'api_format': 'openai'
            },
            'maritaca': {
                'name': 'Maritaca AI',
                'endpoint': 'https://api.maritaca.com/v1/chat/completions',
                'model': 'llama-3-1-405b-instruct',
                'website': 'https://maritaca.ai',
                'free_credit': '注册送额度',
                'note': '巴西AI平台',
                'api_format': 'openai'
            },
            'deepinfra': {
                'name': 'DeepInfra',
                'endpoint': 'https://api.deepinfra.com/v1/chat/completions',
                'model': 'meta-llama/Llama-3.1-405B-Instruct',
                'website': 'https://deepinfra.com',
                'free_credit': '有免费额度',
                'note': '低成本推理',
                'api_format': 'openai'
            },
            'focus': {
                'name': 'Focus AI',
                'endpoint': 'https://api.focusai.com/v1/chat/completions',
                'model': 'gpt-4o-mini',
                'website': 'https://focusai.com',
                'free_credit': '首充优惠',
                'note': 'AI模型服务',
                'api_format': 'openai'
            },
            'upstage': {
                'name': 'Upstage',
                'endpoint': 'https://api.upstage.ai/v1/chat/completions',
                'model': 'solar-pro',
                'website': 'https://upstage.ai',
                'free_credit': '注册送额度',
                'note': '韩国AI公司',
                'api_format': 'openai'
            },
            'nile': {
                'name': 'Nile API',
                'endpoint': 'https://api.nile.ai/v1/chat/completions',
                'model': 'claude-3-5-sonnet',
                'website': 'https://nile.ai',
                'free_credit': '有免费试用',
                'note': '企业AI平台',
                'api_format': 'openai'
            },

            # 自定义供应商
            'Custom': {
                'name': '🌐 自定义供应商',
                'endpoint': '',
                'model': '',
                'website': '',
                'free_credit': '',
                'note': '支持本地部署或其他API',
                'api_format': 'openai'
            }
        }

    def get_providers(self):
        """获取所有供应商列表"""
        providers = []
        for key, value in self.api_endpoints.items():
            providers.append({
                'id': key,
                'name': value['name'],
                'website': value.get('website', ''),
                'free_credit': value.get('free_credit', ''),
                'note': value.get('note', ''),
                'promo': value.get('promo', ''),
                'is_custom': key == 'Custom'
            })
        return providers

    def generate(self, analysis_result, custom_config=None):
        print(f"===== 生成提示词开始 =====")
        print(f"generate方法被调用")
        print(f"custom_config={custom_config is not None}")
        if custom_config:
            print(f"custom_config内容: {custom_config}")
        
        if not custom_config or not custom_config.get('apiKey'):
            print(f"API Key为空，返回错误")
            print(f"===== 无API Key =====")
            return None

        analysis_text = self._format_analysis(analysis_result)

        prompt = f"""你是一个专业的AI提示词生成专家。请根据以下视频分析结果，生成高质量的AI图像/视频生成提示词。

【视频分析结果】
{analysis_text}

请生成3个不同风格的AI提示词，包含以下信息：
1. 英文提示词（详细、专业）
2. 中文描述（简洁）
3. 推荐使用的AI工具
4. 风格标签

请以JSON格式返回，包含以下字段：
- prompts: 数组，包含多个提示词对象
- each包含: prompt_en(英文), prompt_cn(中文), recommended_tools(数组), style_tags(数组)

注意：
- 英文提示词要详细具体，描述场景、氛围、光线、构图等
- 推荐工具要适合该风格
- 风格标签要精准"""

        try:
            print(f"开始调用AI模型，使用供应商配置: {custom_config is not None}")
            
            if custom_config:
                print(f"使用自定义API，配置: {custom_config}")
                result = self._call_custom_api(prompt, custom_config, custom_config.get('apiKey'))
                print(f"自定义API调用成功，返回结果: {result is not None}")
                return result
            else:
                print(f"无供应商配置，返回错误")
                return None
        except Exception as e:
            print(f"API调用失败，错误: {str(e)}")
            return None

    def _format_analysis(self, analysis):
        lines = []
        # 判断是视频还是图片分析
        if analysis.get('duration', 0) > 0:
            lines.append(f"视频时长: {analysis['duration']}秒")
            lines.append(f"分辨率: {analysis['resolution']}")
            lines.append(f"帧率: {analysis['fps']}fps")
        else:
            lines.append(f"图片尺寸: {analysis['resolution']}")
            lines.append(f"类型: 静态图片")
        
        # 处理颜色信息 - 支持两种格式
        if 'colors' in analysis and isinstance(analysis['colors'], dict):
            # 原始格式：analysis['colors']['dominant']
            lines.append(f"主色调: {analysis['colors']['dominant']}")
            lines.append(f"色调风格: {analysis['colors']['warmth']}")
            lines.append(f"饱和度: {analysis['colors']['saturation']}")
            lines.append(f"亮度: {analysis['colors']['brightness']}")
        else:
            # 新格式：直接在 analysis 层级
            lines.append(f"主色调: {analysis.get('dominant_color', '未知')}")
            lines.append(f"色调风格: {analysis.get('warmth', '未知')}")
            lines.append(f"饱和度: {analysis.get('saturation', '未知')}")
            lines.append(f"亮度: {analysis.get('brightness', '未知')}")
        
        # 处理运动信息
        if 'motion' in analysis and isinstance(analysis['motion'], dict):
            lines.append(f"运动程度: {analysis['motion']['level']} - {analysis['motion']['description']}")
        else:
            lines.append(f"运动程度: {analysis.get('motion_level', '静态')}")
        
        # 处理场景信息
        if 'scenes' in analysis and isinstance(analysis['scenes'], dict):
            lines.append(f"场景类型: {analysis['scenes']['type']} - {analysis['scenes']['description']}")
        else:
            lines.append(f"场景类型: {analysis.get('scene_type', '未知')}")
        
        return '\n'.join(lines)

    def _call_standard_api(self, prompt, ai_model, api_key):
        provider = self.api_endpoints.get(ai_model, self.api_endpoints['siliconflow'])
        endpoint = provider['endpoint']
        model_name = provider['model']

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        data = {
            'model': model_name,
            'messages': [
                {'role': 'system', 'content': '你是一个专业的AI提示词生成专家。'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 2000,
            'temperature': 0.8
        }

        response = requests.post(endpoint, headers=headers, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            return self._parse_response(content)
        else:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")

    def _call_anthropic(self, prompt, api_key):
        endpoint = self.api_endpoints['anthropic']['endpoint']

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'anthropic-dangerous-direct-browser-access': 'true'
        }

        data = {
            'model': self.api_endpoints['anthropic']['model'],
            'max_tokens': 2000,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }

        response = requests.post(endpoint, headers=headers, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            content = result['content'][0]['text']
            return self._parse_response(content)
        else:
            raise Exception(f"API调用失败: {response.status_code}")

    def _call_google(self, prompt, api_key):
        endpoint = self.api_endpoints['google']['endpoint']

        headers = {
            'Content-Type': 'application/json'
        }

        data = {
            'contents': [{
                'parts': [{
                    'text': prompt
                }]
            }]
        }

        endpoint_with_key = f"{endpoint}?key={api_key}"
        response = requests.post(endpoint_with_key, headers=headers, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            return self._parse_response(content)
        else:
            raise Exception(f"API调用失败: {response.status_code}")

    def _call_custom_api(self, prompt, custom_config, api_key):
        endpoint = custom_config.get('endpoint', '')
        model_name = custom_config.get('model', '')
        api_format = custom_config.get('format', 'openai')

        print(f"自定义API调用: endpoint={endpoint}, model={model_name}, format={api_format}")

        if not endpoint or not model_name:
            raise Exception("自定义供应商配置不完整")

        headers = {
            'Content-Type': 'application/json'
        }

        # 特殊处理百炼模型
        if 'qwen' in model_name.lower() or 'bailian' in custom_config.get('name', '').lower():
            print("使用百炼模型特殊处理")
            headers['x-api-key'] = api_key
            headers['anthropic-version'] = '2023-06-01'
            data = {
                'model': model_name,
                'max_tokens': 2000,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
        elif api_format == 'openai':
            headers['Authorization'] = f'Bearer {api_key}'
            data = {
                'model': model_name,
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的AI提示词生成专家。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.8
            }
        elif api_format == 'anthropic':
            headers['x-api-key'] = api_key
            headers['anthropic-version'] = '2023-06-01'
            data = {
                'model': model_name,
                'max_tokens': 2000,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
        elif api_format == 'google':
            data = {
                'contents': [{
                    'parts': [{
                        'text': prompt
                    }]
                }]
            }
        else:
            headers['Authorization'] = f'Bearer {api_key}'
            data = {
                'model': model_name,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.8
            }

        print(f"发送API请求到: {endpoint}")
        response = requests.post(endpoint, headers=headers, json=data, timeout=60)

        print(f"API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text[:500]}...")

        if response.status_code == 200:
            result = response.json()
            print(f"解析API响应结果: {result}")
            if api_format == 'anthropic':
                content = result['content'][0]['text']
            elif api_format == 'google':
                content = result['candidates'][0]['content']['parts'][0]['text']
            else:
                content = result['choices'][0]['message']['content']
            return self._parse_response(content)
        else:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")

    def _parse_response(self, content):
        try:
            # 如果content已经是dict，直接处理
            if isinstance(content, dict):
                if 'prompts' in content:
                    for p in content['prompts']:
                        self._ensure_prompt_fields(p)
                    return content
                return {'prompts': [content]}

            print(f"API响应内容: {content[:500]}...")

            # 去除markdown代码块
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                parts = content.split('```')
                if len(parts) >= 3:
                    content = parts[1]
                else:
                    content = parts[1] if len(parts) >= 2 else content

            content = content.strip()
            print(f"提取后的内容: {content[:300]}...")

            result = json.loads(content)

            # 确保prompts数组中的每个元素都有正确的格式
            if 'prompts' in result:
                for p in result['prompts']:
                    self._extract_nested_prompt(p)
                return result
            else:
                self._extract_nested_prompt(result)
                return {'prompts': [result]}

        except Exception as e:
            print(f"解析响应失败: {str(e)}")
            # content可能是原始文本，直接用作提示词
            raw_text = str(content).strip()

            # 尝试从文本中提取所有可能的JSON块
            import re
            # 找到最外层的JSON对象（支持嵌套）
            brace_count = 0
            start = -1
            for i, c in enumerate(raw_text):
                if c == '{':
                    if brace_count == 0:
                        start = i
                    brace_count += 1
                elif c == '}':
                    brace_count -= 1
                    if brace_count == 0 and start >= 0:
                        try:
                            candidate = raw_text[start:i+1]
                            result = json.loads(candidate)
                            if isinstance(result, dict):
                                if 'prompts' in result:
                                    for p in result['prompts']:
                                        self._ensure_prompt_fields(p)
                                    return result
                                elif 'prompt_cn' in result or 'prompt_en' in result:
                                    self._ensure_prompt_fields(result)
                                    return {'prompts': [result]}
                        except:
                            pass
                        start = -1

            # 尝试修复截断的JSON（max_tokens不足导致输出不完整）
            # 找到最后一个完整的 prompt_cn 值并用它构建响应
            prompt_cn_matches = re.findall(r'"prompt_cn"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_text, re.DOTALL)
            if prompt_cn_matches:
                prompts = []
                for cn in prompt_cn_matches:
                    prompts.append({
                        'prompt_cn': cn,
                        'prompt_en': '',
                        'recommended_tools': ['Midjourney', 'Stable Diffusion', 'DALL-E 3'],
                        'style_tags': ['Video', 'Generated']
                    })
                print(f"从截断响应中提取到 {len(prompts)} 个prompt_cn")
                return {'prompts': prompts}

            # 所有解析失败，返回原始文本
            return {
                'prompts': [{
                    'prompt_en': raw_text,
                    'prompt_cn': raw_text,
                    'recommended_tools': ['Midjourney', 'Stable Diffusion', 'DALL-E 3'],
                    'style_tags': ['Custom', 'Generated']
                }]
            }

    def _extract_nested_prompt(self, prompt_dict):
        """从prompt_cn/prompt_en字段中提取嵌套的JSON内容"""
        if not isinstance(prompt_dict, dict):
            return

        for field in ['prompt_cn', 'prompt_en']:
            val = prompt_dict.get(field, '')
            if not isinstance(val, str):
                continue
            val = val.strip()
            if not val.startswith('{'):
                continue

            # 用括号匹配提取最外层JSON
            brace_count = 0
            start = -1
            for i, c in enumerate(val):
                if c == '{':
                    if brace_count == 0:
                        start = i
                    brace_count += 1
                elif c == '}':
                    brace_count -= 1
                    if brace_count == 0 and start >= 0:
                        try:
                            nested = json.loads(val[start:i+1])
                            if isinstance(nested, dict):
                                if 'prompts' in nested and nested['prompts']:
                                    inner = nested['prompts'][0]
                                    if isinstance(inner, dict):
                                        # 递归提取内层
                                        self._extract_nested_prompt(inner)
                                        extracted = inner.get(field) or inner.get('prompt_cn') or inner.get('prompt_en') or val
                                        prompt_dict[field] = extracted
                                elif field in nested:
                                    prompt_dict[field] = nested[field]
                        except:
                            pass
                        break

        # 确保必填字段存在
        if 'prompt_cn' not in prompt_dict or not prompt_dict['prompt_cn']:
            prompt_dict['prompt_cn'] = prompt_dict.get('prompt_en', '')
        if 'prompt_en' not in prompt_dict or not prompt_dict['prompt_en']:
            prompt_dict['prompt_en'] = prompt_dict.get('prompt_cn', '')
        if 'recommended_tools' not in prompt_dict:
            prompt_dict['recommended_tools'] = ['Midjourney', 'Stable Diffusion', 'DALL-E 3']
        if 'style_tags' not in prompt_dict:
            prompt_dict['style_tags'] = ['Custom', 'Generated']

    def _ensure_prompt_fields(self, prompt_dict):
        """确保提示词对象包含所有必要字段，递归处理嵌套JSON"""
        if not isinstance(prompt_dict, dict):
            return

        # 如果prompt_dict本身有prompts字段，提取第一个
        if 'prompts' in prompt_dict and isinstance(prompt_dict['prompts'], list) and prompt_dict['prompts']:
            inner = prompt_dict['prompts'][0]
            if isinstance(inner, dict):
                self._ensure_prompt_fields(inner)
                # 用inner的内容替换当前对象的字段
                for k, v in inner.items():
                    if k != 'prompts':
                        prompt_dict[k] = v

        # 如果prompt_cn包含JSON字符串，递归提取实际内容
        for field in ['prompt_cn', 'prompt_en']:
            val = prompt_dict.get(field, '')
            if isinstance(val, str) and val.strip().startswith('{'):
                try:
                    nested = json.loads(val)
                    if isinstance(nested, dict):
                        if 'prompts' in nested and nested['prompts']:
                            inner = nested['prompts'][0]
                            self._ensure_prompt_fields(inner)
                            prompt_dict[field] = inner.get(field, inner.get('prompt_cn', inner.get('prompt_en', val)))
                        elif field in nested:
                            prompt_dict[field] = nested[field]
                except:
                    pass

        # 确保必填字段存在
        if 'prompt_cn' not in prompt_dict or not prompt_dict['prompt_cn']:
            prompt_dict['prompt_cn'] = prompt_dict.get('prompt_en', '')
        if 'prompt_en' not in prompt_dict or not prompt_dict['prompt_en']:
            prompt_dict['prompt_en'] = prompt_dict.get('prompt_cn', '')
        if 'recommended_tools' not in prompt_dict:
            prompt_dict['recommended_tools'] = ['Midjourney', 'Stable Diffusion', 'DALL-E 3']
        if 'style_tags' not in prompt_dict:
            prompt_dict['style_tags'] = ['Custom', 'Generated']

    def _generate_fallback(self, analysis):
        # 判断是视频还是图片
        is_video = analysis.get('duration', 0) > 0
        
        # 处理颜色信息 - 支持两种格式
        if 'colors' in analysis and isinstance(analysis['colors'], dict):
            # 原始格式
            color_desc = f"{analysis['colors']['warmth']}，{analysis['colors']['saturation']}，{analysis['colors']['brightness']}"
            dominant_color = analysis['colors'].get('dominant', '未知')
        else:
            # 新格式
            color_desc = f"{analysis.get('warmth', '中性色调')}，{analysis.get('saturation', '中等饱和度')}，{analysis.get('brightness', '中等亮度')}"
            dominant_color = analysis.get('dominant_color', '未知')
        
        # 处理场景信息
        if 'scenes' in analysis and isinstance(analysis['scenes'], dict):
            # 原始格式
            scene_type = analysis['scenes'].get('type', '场景')
            motion_level = analysis.get('motion', {}).get('level', '静态')
        else:
            # 新格式
            scene_type = analysis.get('scene_type', '场景')
            motion_level = analysis.get('motion_level', '静态')
        
        # 根据类型生成不同的提示词
        if is_video:
            # 视频：生成分镜描述
            motion_desc = f"{motion_level}的{scene_type}"
            prompt_cn = f"【总起声明】一个充满电影感的{color_desc}视频，包含{motion_desc}元素和专业摄影效果。\n\n【分镜头描述】\n镜头1：\n【技术参数】中景，4K超清，24fps\n【环境氛围】室内场景，{color_desc}，柔和的自然光，细腻的质感\n【人物造型】穿着休闲的人物，自然妆容，放松的表情\n【核心动作/表演】人物进行日常活动，动作自然流畅\n【声音/台词】环境音效，轻柔的背景音乐\n【镜头过渡/特殊效果】平稳的推镜，自然过渡\n\n镜头2：\n【技术参数】特写，4K超清，24fps\n【环境氛围】同一室内场景，局部光影，细节丰富\n【人物造型】人物面部表情，细微的情绪变化\n【核心动作/表演】人物专注于手头的事情，细节动作\n【声音/台词】环境音效，轻微的动作声音\n【镜头过渡/特殊效果】特写镜头，缓慢推近\n\n【全局设定】统一的轻柔背景音乐风格，结尾定格在人物自然放松的状态。"
            prompt_en = f'A cinematic {color_desc} video scene, {motion_desc}, professional cinematography, high quality, detailed, 4K'
        else:
            # 图片：生成静态图片描述，不包含分镜
            # 分析图片内容特征
            features = self._analyze_image_features(analysis)
            
            # 生成详细的提示词
            prompt_cn = f"""【总起声明】{features['style']}风格插画，{color_desc}，展现{features['genre']}主题，高品质数字艺术作品。

【主体内容】
【人物描述】{features['characters']}
【场景环境】{features['background']}
【构图视角】{features['composition']}，{features['camera_angle']}

【艺术风格】
【画风类型】{features['style']}
【色彩风格】{color_desc}，主色调{dominant_color}
【光影效果】{features['lighting']}
【氛围感觉】{features['mood']}

【技术参数】
【分辨率】高分辨率，4K画质
【细节程度】精细刻画，丰富细节
【艺术标签】{features['tags']}"""
            
            prompt_en = f"{features['style_en']} style illustration, {color_desc}, {features['genre_en']} theme, {features['characters_en']}, {features['background_en']}, {features['lighting_en']}, {features['mood_en']}, high resolution, 4K quality, detailed artwork"

        return {
            'prompts': [
                {
                    'prompt_en': prompt_en,
                    'prompt_cn': prompt_cn,
                    'recommended_tools': ['Midjourney', 'Stable Diffusion', 'DALL-E 3'],
                    'style_tags': ['Cinematic', 'Professional', 'High Quality']
                }
            ]
        }
    
    def _analyze_image_features(self, analysis):
        """分析图片特征，生成更精准的描述"""
        # 获取分析结果
        colors = analysis.get('colors', {}) if isinstance(analysis.get('colors'), dict) else {}
        warmth = colors.get('warmth', analysis.get('warmth', '中性色调'))
        saturation = colors.get('saturation', analysis.get('saturation', '中等饱和度'))
        brightness = colors.get('brightness', analysis.get('brightness', '中等亮度'))
        dominant_color = colors.get('dominant', analysis.get('dominant_color', '#8B8B8B'))
        warm_ratio = colors.get('warm_ratio', 0)
        green_ratio = colors.get('green_ratio', 0)
        
        scene_type = analysis.get('scene_type', '') or analysis.get('scenes', {}).get('type', '')
        has_people = analysis.get('has_people', False)
        people_count = analysis.get('people_count', 2)
        composition = analysis.get('composition', '横构图')
        
        # 获取更多场景信息
        scenes = analysis.get('scenes', {}) if isinstance(analysis.get('scenes'), dict) else {}
        sky_ratio = scenes.get('sky_ratio', 0)
        scene_green_ratio = scenes.get('green_ratio', 0)
        
        # 根据分析结果生成详细特征
        features = {
            'style': '二次元动漫',
            'style_en': 'anime',
            'genre': '青春校园',
            'genre_en': 'school life',
            'characters': '',
            'characters_en': '',
            'background': '',
            'background_en': '',
            'composition': '',
            'lighting': '',
            'lighting_en': '',
            'mood': '',
            'mood_en': '',
            'tags': '',
            'camera_angle': '',
            'camera_angle_en': ''
        }
        
        # 根据颜色调整风格和氛围（更准确）
        if warm_ratio > 0.2 or '暖色' in warmth or '暖' in warmth:
            features['lighting'] = '温暖的金色阳光，逆光效果，柔和的阴影，温暖的光晕，阳光从侧面照射，金色光芒洒在人物身上'
            features['lighting_en'] = 'warm golden sunlight, backlighting, soft shadows, warm glow, side lighting, golden light on characters'
            features['mood'] = '温馨浪漫，温暖治愈，阳光灿烂，青春洋溢，充满希望，浪漫氛围'
            features['mood_en'] = 'warm and romantic, healing atmosphere, sunny, youthful, hopeful, romantic vibe'
            features['style'] = '温暖治愈系动漫'
            features['style_en'] = 'warm healing anime'
        elif green_ratio > 0.3 and warm_ratio < 0.15:
            features['lighting'] = '自然光线，绿意盎然，清新明亮，阳光透过树叶'
            features['lighting_en'] = 'natural light, lush green, fresh and bright, sunlight through leaves'
            features['mood'] = '清新自然，生机勃勃，宁静舒适'
            features['mood_en'] = 'fresh and natural, vibrant, peaceful'
            features['style'] = '清新自然风'
            features['style_en'] = 'fresh natural style'
        elif '冷色' in warmth or '冷' in warmth:
            features['lighting'] = '冷色调光线，柔和清冷，氛围感强，蓝色调阴影'
            features['lighting_en'] = 'cool tone lighting, soft and cool, atmospheric, blue shadows'
            features['mood'] = '宁静深邃，神秘优雅，文艺气息，清新淡雅'
            features['mood_en'] = 'serene and deep, mysterious elegance, artistic, fresh'
            features['style'] = '清冷写实插画'
            features['style_en'] = 'cool realism illustration'
        else:
            features['lighting'] = '柔和的自然光，适中的阴影，均衡的光线'
            features['lighting_en'] = 'soft natural light, moderate shadows, balanced lighting'
            features['mood'] = '平和舒适，优雅大方，温馨宜人'
            features['mood_en'] = 'peaceful and comfortable, elegant, warm'
        
        # 根据场景类型调整背景（更准确）
        if sky_ratio > 0.08 or '城市' in scene_type or '建筑' in scene_type:
            features['background'] = '现代城市建筑背景，高楼大厦，城市天际线，明亮的蓝天，阳光明媚的白天，仰视角度看天空，建筑物外墙'
            features['background_en'] = 'modern city buildings background, skyscrapers, city skyline, bright blue sky, sunny day, looking up at sky, building exterior'
            features['genre'] = '都市青春'
            features['genre_en'] = 'urban youth'
            features['camera_angle'] = '仰视角度，低角度拍摄，从下往上看，特写人物上半身'
            features['camera_angle_en'] = 'low angle shot, looking up, from below, close up on upper body'
        elif scene_green_ratio > 0.25 or '自然' in scene_type:
            features['background'] = '自然风景，茂密的树木，绿色的树叶，阳光透过树叶，清新自然的环境'
            features['background_en'] = 'natural scenery, dense trees, green leaves, sunlight through leaves, fresh natural environment'
            features['genre'] = '自然风景'
            features['genre_en'] = 'nature landscape'
            features['camera_angle'] = '平视角度，自然视角'
            features['camera_angle_en'] = 'eye level, natural perspective'
        elif '室内' in scene_type:
            features['background'] = '温馨的室内场景，舒适的房间布置，柔和的室内灯光'
            features['background_en'] = 'cozy indoor scene, comfortable room setting, soft interior lighting'
            features['genre'] = '室内生活'
            features['genre_en'] = 'indoor life'
            features['camera_angle'] = '中等角度，舒适的视角'
            features['camera_angle_en'] = 'medium angle, comfortable perspective'
        else:
            features['background'] = '简洁的背景，突出主体，艺术感强'
            features['background_en'] = 'simple background, focus on subject, artistic'
            features['camera_angle'] = '标准角度，居中构图'
            features['camera_angle_en'] = 'standard angle, centered composition'
        
        # 根据人物数量生成详细的人物描述（更准确）
        if has_people or people_count > 0:
            if people_count == 1:
                features['characters'] = '一位年轻的二次元角色，精致的五官，细腻的表情，优雅的姿态，青春洋溢的气质'
                features['characters_en'] = 'one young anime character, delicate features, subtle expression, elegant pose, youthful temperament'
            elif people_count == 2:
                features['characters'] = '两位青少年角色，一男一女，背靠背站立的姿态，女生在左男生在右，女生看向画面左上方，男生看向画面右侧，女生有齐刘海黑色长发带青色挑染，男生黑色短发，精致的二次元五官，女生蓝色眼睛，表情温柔，男生表情平静，女生穿着白色水手服搭配红色领结，男生穿着深色立领外套，两人都背着双肩书包，青春校园风格，风吹动头发'
                features['characters_en'] = 'two anime characters, boy and girl, standing back to back, girl on left boy on right, girl looking up left, boy looking right, girl has bangs and long black hair with cyan highlights, boy has short black hair, delicate anime facial features, girl has blue eyes, gentle expression, boy has calm expression, girl in white sailor uniform with red bow, boy in dark stand-up collar jacket, both carrying backpacks, school life style, wind blowing hair'
            else:
                features['characters'] = f'{people_count}位角色，生动的表情，自然的姿态，互动的场景，青春校园风格'
                features['characters_en'] = f'{people_count} characters, vivid expressions, natural poses, interacting scene, school life style'
        else:
            features['characters'] = '无人物，专注于场景和氛围'
            features['characters_en'] = 'no people, focus on scene and atmosphere'
        
        # 根据构图调整视角描述
        if '竖' in composition:
            features['composition'] = '竖构图，纵向视角，人物为主，突出人物高度'
        elif '横' in composition:
            features['composition'] = '横构图，宽广视角，场景为主，展现环境氛围'
        else:
            features['composition'] = '正方形构图，均衡对称，主体突出'
        
        # 根据饱和度调整标签
        if '低饱和' in saturation:
            features['tags'] = '低饱和度，柔和色调，高级感，艺术插画，细腻笔触，唯美动人，高清画质，电影感，氛围感强'
        elif '高饱和' in saturation:
            features['tags'] = '高饱和度，鲜艳色彩，活力四射，生动活泼，高清画质，精致细节'
        else:
            features['tags'] = '中等饱和度，色彩和谐，画面均衡，高清画质，精致细节，插画风格'
        
        # 根据亮度调整
        if '明亮' in brightness or '偏亮' in brightness:
            features['lighting'] = features['lighting'].replace('柔和', '明亮')
            features['tags'] += '，明亮通透，阳光充足'
        elif '偏暗' in brightness:
            features['lighting'] = features['lighting'].replace('明亮', '柔和')
            features['tags'] += '，暗调氛围，氛围感强'
        
        return features

    def _generate_fallback_prompts(self):
        # 按照新格式生成fallback提示词
        prompt_cn = "【总起声明】一个充满电影感的视频场景，包含专业摄影效果和艺术氛围。\n\n【分镜头描述】\n镜头1：\n【技术参数】中景，4K超清，24fps\n【环境氛围】室内场景，柔和的自然光，细腻的质感\n【人物造型】穿着休闲的人物，自然妆容，放松的表情\n【核心动作/表演】人物进行日常活动，动作自然流畅\n【声音/台词】环境音效，轻柔的背景音乐\n【镜头过渡/特殊效果】平稳的推镜，自然过渡\n\n镜头2：\n【技术参数】特写，4K超清，24fps\n【环境氛围】同一室内场景，局部光影，细节丰富\n【人物造型】人物面部表情，细微的情绪变化\n【核心动作/表演】人物专注于手头的事情，细节动作\n【声音/台词】环境音效，轻微的动作声音\n【镜头过渡/特殊效果】特写镜头，缓慢推近\n\n【全局设定】统一的轻柔背景音乐风格，结尾定格在人物自然放松的状态。"

        return {
            'prompts': [
                {
                    'prompt_en': 'A cinematic video scene with vibrant colors, professional cinematography, high quality, 4K resolution',
                    'prompt_cn': prompt_cn,
                    'recommended_tools': ['Midjourney', 'Stable Diffusion', 'DALL-E 3'],
                    'style_tags': ['Cinematic', 'Professional', 'High Quality']
                }
            ]
        }

    def _resolve_endpoint(self, endpoint, api_format, api_key):
        """探测正确的API端点路径"""
        path_suffixes = {
            'openai': ['/v1/chat/completions', '/chat/completions', '/v1/chat', '/api/v1/chat/completions', ''],
            'anthropic': ['/v1/messages', '/messages', '/api/v1/messages', ''],
            'google': [':generateContent', '']
        }
        suffixes = path_suffixes.get(api_format, path_suffixes['openai'])

        # 检查endpoint是否已经是一个完整路径
        path_parts = endpoint.replace('https://', '').replace('http://', '').split('/')
        # 如果路径已经有3个以上部分（域名+至少2个路径段），认为已经是完整路径
        if len(path_parts) > 2:
            return endpoint

        headers = {'Content-Type': 'application/json'}
        if api_format == 'anthropic':
            headers['x-api-key'] = api_key
            headers['anthropic-version'] = '2023-06-01'
        elif api_format == 'google':
            pass
        else:
            headers['Authorization'] = f'Bearer {api_key}'

        for suffix in suffixes:
            test_url = endpoint.rstrip('/') + suffix
            try:
                # 发一个最小请求来测试端点是否可用
                if api_format == 'anthropic':
                    test_data = {'model': 'test', 'max_tokens': 1, 'messages': [{'role': 'user', 'content': 'hi'}]}
                elif api_format == 'google':
                    test_data = {'contents': [{'parts': [{'text': 'hi'}]}]}
                else:
                    test_data = {'model': 'test', 'messages': [{'role': 'user', 'content': 'hi'}], 'max_tokens': 1}

                response = requests.post(test_url, headers=headers, json=test_data, timeout=10,
                                         proxies={'http': None, 'https': None})
                # 404表示路径不对，401/403/400/422等表示路径对了但参数不对
                if response.status_code != 404:
                    print(f"发现可用端点: {test_url} (状态码: {response.status_code})")
                    return test_url
            except Exception:
                continue

        # 如果都失败，返回原始端点
        return endpoint

    def generate_with_image(self, image_path, analysis_result, custom_config=None):
        """真正让AI看图片来生成提示词"""
        print("=" * 60)
        print("AI正在看图片...")
        print(f"图片路径: {image_path}")
        print("=" * 60)

        if not custom_config or not custom_config.get('apiKey'):
            print("API Key为空，返回错误提示")
            return None
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with open(image_path, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                endpoint = custom_config.get('endpoint')
                model_name = custom_config.get('model')
                api_format = custom_config.get('format', 'openai')
                api_key = custom_config.get('apiKey')
                
                print(f"API端点: {endpoint}")
                print(f"模型: {model_name}")
                print(f"格式: {api_format}")

                if not endpoint or not model_name:
                    print("配置不完整，返回错误")
                    return None

                # 探测正确的端点路径
                endpoint = self._resolve_endpoint(endpoint, api_format, api_key)

                headers = {'Content-Type': 'application/json'}

                # 特殊处理百炼模型
                if 'qwen' in model_name.lower() or 'bailian' in custom_config.get('name', '').lower():
                    print("使用百炼模型特殊处理")
                    headers['Authorization'] = f'Bearer {api_key}'
                    # 百炼模型使用OpenAI兼容格式
                    # 检查endpoint是否已经包含/chat/completions
                    if not endpoint.endswith('/chat/completions'):
                        endpoint = f"{endpoint}/chat/completions"
                    print(f"修正后的API端点: {endpoint}")
                    payload = {
                        'model': model_name,
                        'messages': [{
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': '请分析这张图片，生成3个不同风格的AI绘画提示词。\n\n**输出格式（JSON）：**\n{\n  "prompts": [\n    {"prompt_cn": "中文提示词", "prompt_en": "English prompt", "recommended_tools": ["工具"], "style_tags": ["标签"]},\n    ...\n  ]\n}\n\n**三个提示词要求：**\n1. 写实风格：详细描述画面内容、光影、氛围\n2. 艺术/插画风格\n3. 动漫/二次元风格\n\n**重要：prompt_cn 必须是中文，prompt_en 必须是英文。**'
                                },
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': f'data:image/jpeg;base64,{image_base64}'
                                    }
                                }
                            ]
                        }
                    ],
                    'max_tokens': 4000
                }
                elif api_format == 'openai':
                    headers['Authorization'] = f'Bearer {api_key}'
                    payload = {
                        'model': model_name,
                        'messages': [
                            {
                                'role': 'user',
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': '请分析这张图片，生成3个不同风格的AI绘画提示词。\n\n**输出格式（JSON）：**\n{\n  "prompts": [\n    {"prompt_cn": "中文提示词", "prompt_en": "English prompt", "recommended_tools": ["工具"], "style_tags": ["标签"]},\n    ...\n  ]\n}\n\n**三个提示词要求：**\n1. 写实风格：详细描述画面内容、光影、氛围\n2. 艺术/插画风格\n3. 动漫/二次元风格\n\n**重要：prompt_cn 必须是中文，prompt_en 必须是英文。**'
                                    },
                                    {
                                        'type': 'image_url',
                                        'image_url': {
                                            'url': f'data:image/jpeg;base64,{image_base64}'
                                        }
                                    }
                                ]
                            }
                        ],
                        'max_tokens': 4000
                    }
                elif api_format == 'anthropic':
                    headers['x-api-key'] = api_key
                    headers['anthropic-version'] = '2023-06-01'
                    payload = {
                        'model': model_name,
                        'max_tokens': 4000,
                        'messages': [
                            {
                                'role': 'user',
                                'content': [
                                    {
                                        'type': 'image',
                                        'source': {
                                            'type': 'base64',
                                            'media_type': 'image/jpeg',
                                            'data': image_base64
                                        }
                                    },
                                    {
                                        'type': 'text',
                                        'text': '请分析这张图片，生成3个不同风格的AI绘画提示词。\n\n**输出格式（JSON）：**\n{\n  "prompts": [\n    {"prompt_cn": "中文提示词", "prompt_en": "English prompt", "recommended_tools": ["工具"], "style_tags": ["标签"]},\n    ...\n  ]\n}\n\n**三个提示词要求：**\n1. 写实风格：详细描述画面内容、光影、氛围\n2. 艺术/插画风格\n3. 动漫/二次元风格\n\n**重要：prompt_cn 必须是中文，prompt_en 必须是英文。**'
                                    }
                                ]
                            }
                        ]
                    }
                elif api_format == 'google':
                    payload = {
                        'contents': [{
                            'parts': [
                                {
                                    'text': '请分析这张图片，生成3个不同风格的AI绘画提示词。\n\n**输出格式（JSON）：**\n{\n  "prompts": [\n    {"prompt_cn": "中文提示词", "prompt_en": "English prompt", "recommended_tools": ["工具"], "style_tags": ["标签"]},\n    ...\n  ]\n}\n\n**三个提示词要求：**\n1. 写实风格：详细描述画面内容、光影、氛围\n2. 艺术/插画风格\n3. 动漫/二次元风格\n\n**重要：prompt_cn 必须是中文，prompt_en 必须是英文。**'
                                },
                                {
                                    'inline_data': {
                                        'mime_type': 'image/jpeg',
                                        'data': image_base64
                                    }
                                }
                            ]
                        }]
                    }
                else:
                    headers['Authorization'] = f'Bearer {api_key}'
                    payload = {
                        'model': model_name,
                        'messages': [
                            {
                                'role': 'user',
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': '请分析这张图片，生成3个不同风格的AI绘画提示词。\n\n**输出格式（JSON）：**\n{\n  "prompts": [\n    {"prompt_cn": "中文提示词", "prompt_en": "English prompt", "recommended_tools": ["工具"], "style_tags": ["标签"]},\n    ...\n  ]\n}\n\n**三个提示词要求：**\n1. 写实风格：详细描述画面内容、光影、氛围\n2. 艺术/插画风格\n3. 动漫/二次元风格\n\n**重要：prompt_cn 必须是中文，prompt_en 必须是英文。**'
                                    },
                                    {
                                        'type': 'image_url',
                                        'image_url': {
                                            'url': f'data:image/jpeg;base64,{image_base64}'
                                        }
                                    }
                                ]
                            }
                        ],
                        'max_tokens': 2000
                    }

                # 发送请求（适用于所有模型）
                print(f"发送请求到 {endpoint}... (尝试 {retry_count + 1}/{max_retries})")
                response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
                
                print(f"响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if api_format == 'anthropic':
                        content = result['content'][0]['text']
                    elif api_format == 'google':
                        content = result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        content = result['choices'][0]['message']['content']
                    print(f"AI回复: {content[:300]}...")
                    return self._parse_response(content)
                else:
                    print(f"API错误: {response.text}")
                    # 增加重试机制
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"重试中... ({retry_count}/{max_retries})")
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        print("达到最大重试次数，返回错误")
                        return None

            except requests.exceptions.RequestException as e:
                print(f"网络请求失败: {str(e)}")
                # 增加重试机制
                retry_count += 1
                if retry_count < max_retries:
                    print(f"重试中... ({retry_count}/{max_retries})")
                    time.sleep(2)  # 等待2秒后重试
                else:
                    print("达到最大重试次数，返回错误")
                    import traceback
                    traceback.print_exc()
                    return None
            except Exception as e:
                print(f"发生其他错误: {str(e)}")
                import traceback
                traceback.print_exc()
                return None

    def generate_with_video(self, video_path, analysis_result, custom_config=None, max_frames=5):
        """基于视频关键帧生成提示词"""
        print("=" * 60)
        print("AI正在分析视频关键帧...")
        print(f"视频路径: {video_path}")
        print(f"最大帧数: {max_frames}")
        print("=" * 60)

        if not custom_config or not custom_config.get('apiKey'):
            print("API Key为空，返回错误提示")
            return None
        
        max_retries = 3
        retry_count = 0
        temp_files = []
        
        try:
            # 导入视频分析器
            from utils.video_analyzer import VideoAnalyzer
            video_analyzer = VideoAnalyzer()
            
            # 提取关键帧
            key_frames = video_analyzer.extract_key_frames(video_path, max_frames=max_frames)
            print(f"提取到 {len(key_frames)} 个关键帧")
            
            if len(key_frames) == 0:
                print("未提取到关键帧，返回错误")
                return None
            
            # 准备API配置
            endpoint = custom_config.get('endpoint')
            model_name = custom_config.get('model')
            api_format = custom_config.get('format', 'openai')
            api_key = custom_config.get('apiKey')
            
            print(f"API端点: {endpoint}")
            print(f"模型: {model_name}")
            print(f"格式: {api_format}")

            if not endpoint or not model_name:
                print("配置不完整，返回错误")
                return None

            # 探测正确的端点路径
            endpoint = self._resolve_endpoint(endpoint, api_format, api_key)

            # 处理关键帧
            import cv2
            import numpy as np
            import tempfile
            
            # 为每个关键帧创建临时文件
            for i, frame in enumerate(key_frames):  # 使用所有提取的关键帧
                # 转换回BGR格式
                frame_bgr = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                # 创建临时文件
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                cv2.imwrite(temp_file.name, frame_bgr)
                temp_files.append(temp_file.name)
            
            # 构建请求内容
            headers = {'Content-Type': 'application/json'}
            
            # 构建消息内容
            num_frames = len(temp_files)
            content = []
            content.append({
                'type': 'text',
                'text': f'请分析以下{num_frames}个视频关键帧，理解视频的整体风格、内容和氛围，然后生成AI视频脚本提示词。\n\n**重要：你收到了{num_frames}个关键帧，必须为每个关键帧生成一个镜头描述，总共{num_frames}个镜头。**\n\n**输出要求：**\n请以JSON格式返回，必须包含以下字段：\n{{\n  "prompts": [\n    {{\n      "prompt_cn": "中文提示词",\n      "prompt_en": "English prompt",\n      "recommended_tools": ["工具1", "工具2"],\n      "style_tags": ["标签1", "标签2"]\n    }}\n  ]\n}}\n\n**prompt_cn 必须使用以下中文格式，包含{num_frames}个镜头：**\n\n【总起声明】一句话清晰说明视频类型、风格和核心看点。\n\n【分镜头描述】\n镜头1：（对应第1个关键帧）\n【技术参数】景别、清晰度、帧率\n【环境氛围】地点、光影、色调、质感\n【人物造型】穿着、妆容、表情状态\n【核心动作/表演】具体动作和神态\n【声音/台词】画外音、音效、BGM和精确台词\n【镜头过渡/特殊效果】运镜方式和视觉效果\n\n镜头2：（对应第2个关键帧）\n（同上格式）\n\n镜头3：（对应第3个关键帧）\n（同上格式）\n\n... 一直到镜头{num_frames}（对应第{num_frames}个关键帧）\n\n【全局设定】统一的BGM风格，以及视频结尾的定格画面描述。\n\n**prompt_en 使用英文，简洁描述同一内容。**\n\n**必须生成恰好{num_frames}个镜头，每个关键帧对应一个镜头。prompt_cn 必须是中文，prompt_en 必须是英文。**'
            })
            
            # 添加关键帧图片
            for temp_file in temp_files:
                with open(temp_file, 'rb') as f:
                    image_base64 = base64.b64encode(f.read()).decode('utf-8')
                content.append({
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/jpeg;base64,{image_base64}'
                    }
                })
            
            # 特殊处理百炼模型
            if 'qwen' in model_name.lower() or 'bailian' in custom_config.get('name', '').lower():
                print("使用百炼模型特殊处理")
                headers['Authorization'] = f'Bearer {api_key}'
                # 百炼模型使用OpenAI兼容格式
                # 检查endpoint是否已经包含/chat/completions
                if not endpoint.endswith('/chat/completions'):
                    endpoint = f"{endpoint}/chat/completions"
                print(f"修正后的API端点: {endpoint}")
                payload = {
                    'model': model_name,
                    'messages': [{
                        'role': 'user',
                        'content': content
                    }],
                    'max_tokens': 4000
                }
            elif api_format == 'openai':
                headers['Authorization'] = f'Bearer {api_key}'
                payload = {
                    'model': model_name,
                    'messages': [{
                        'role': 'user',
                        'content': content
                    }],
                    'max_tokens': 4000
                }
            elif api_format == 'anthropic':
                headers['x-api-key'] = api_key
                headers['anthropic-version'] = '2023-06-01'
                # 转换内容格式为anthropic格式
                anthropic_content = []
                for item in content:
                    if item['type'] == 'text':
                        anthropic_content.append(item)
                    elif item['type'] == 'image_url':
                        anthropic_content.append({
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/jpeg',
                                'data': item['image_url']['url'].split(',')[1]
                            }
                        })
                payload = {
                    'model': model_name,
                    'max_tokens': 4000,
                    'messages': [{
                        'role': 'user',
                        'content': anthropic_content
                    }]
                }
            elif api_format == 'google':
                # 转换内容格式为google格式
                parts = []
                for item in content:
                    if item['type'] == 'text':
                        parts.append({'text': item['text']})
                    elif item['type'] == 'image_url':
                        parts.append({
                            'inline_data': {
                                'mime_type': 'image/jpeg',
                                'data': item['image_url']['url'].split(',')[1]
                            }
                        })
                payload = {
                    'contents': [{'parts': parts}]
                }
            else:
                headers['Authorization'] = f'Bearer {api_key}'
                payload = {
                    'model': model_name,
                    'messages': [{
                        'role': 'user',
                        'content': content
                    }],
                    'max_tokens': 4000
                }

            while retry_count < max_retries:
                try:
                    print(f"发送请求到 {endpoint}... (尝试 {retry_count + 1}/{max_retries})")
                    response = requests.post(endpoint, headers=headers, json=payload, timeout=120)

                    print(f"响应状态: {response.status_code}")

                    if response.status_code == 200:
                        result = response.json()
                        if api_format == 'anthropic':
                            content = result['content'][0]['text']
                        elif api_format == 'google':
                            content = result['candidates'][0]['content']['parts'][0]['text']
                        else:
                            content = result['choices'][0]['message']['content']
                        print(f"AI回复: {content[:300]}...")
                        return self._parse_response(content)
                    else:
                        print(f"API错误: {response.text}")
                        # 增加重试机制
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"重试中... ({retry_count}/{max_retries})")
                            time.sleep(2)  # 等待2秒后重试
                        else:
                            print("达到最大重试次数，返回错误")
                            return None
                except requests.exceptions.RequestException as e:
                    print(f"网络请求失败: {str(e)}")
                    # 增加重试机制
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"重试中... ({retry_count}/{max_retries})")
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        print("达到最大重试次数，返回错误")
                        import traceback
                        traceback.print_exc()
                        return None

        except Exception as e:
            print(f"视频分析失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 清理临时文件
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass

    def test_connection(self, custom_config=None):
        """测试API连接，支持自动检测正确的端点路径"""
        print("=" * 60)
        print(f"测试连接: custom_config={custom_config is not None}")
        print("=" * 60)
        
        if not custom_config:
            print("无供应商配置，测试失败")
            return False
        
        endpoint = custom_config.get('endpoint')
        model_name = custom_config.get('model')
        # 兼容两种字段名
        api_format = custom_config.get('format') or custom_config.get('api_format', 'openai')
        api_key = custom_config.get('apiKey') or custom_config.get('api_key')
        
        print(f"API端点: {endpoint}")
        print(f"模型: {model_name}")
        print(f"格式: {api_format}")
        
        if not endpoint or not model_name:
            print("配置不完整，测试失败")
            return False
        
        # 定义常见的API路径后缀
        path_suffixes = {
            'openai': [
                '/v1/chat/completions',
                '/chat/completions',
                '/v1/chat',
                '/api/v1/chat/completions',
                '',  # 如果已经是完整路径
            ],
            'anthropic': [
                '/v1/messages',
                '/messages',
                '/api/v1/messages',
                '',  # 如果已经是完整路径
            ],
            'google': [
                ':generateContent',
                '',  # 如果已经是完整路径
            ]
        }
        
        # 获取当前格式的可能路径
        suffixes = path_suffixes.get(api_format, path_suffixes['openai'])
        
        # 先尝试原始路径
        all_endpoints_to_try = [endpoint]
        
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
        
        print(f"将尝试以下端点: {all_endpoints_to_try}")
        
        # 尝试每个端点
        for test_endpoint in all_endpoints_to_try:
            print(f"\n尝试端点: {test_endpoint}")
            print("-" * 60)
            
            max_retries = 2
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 发送测试请求
                    headers = {'Content-Type': 'application/json'}
                    
                    # 特殊处理百炼模型
                    if 'qwen' in model_name.lower() or 'bailian' in custom_config.get('name', '').lower():
                        print("使用百炼模型特殊处理")
                        headers['Authorization'] = f'Bearer {api_key}'
                        # 百炼模型使用OpenAI兼容格式
                        # 检查endpoint是否已经包含/chat/completions
                        if not test_endpoint.endswith('/chat/completions'):
                            test_endpoint = f"{test_endpoint}/chat/completions"
                        print(f"修正后的API端点: {test_endpoint}")
                        payload = {
                            'model': model_name,
                            'max_tokens': 5,
                            'messages': [{'role': 'user', 'content': 'Hi'}]
                        }
                    elif api_format == 'openai' and api_key:
                        headers['Authorization'] = f'Bearer {api_key}'
                        payload = {
                            'model': model_name,
                            'messages': [{'role': 'user', 'content': 'Hi'}],
                            'max_tokens': 5
                        }
                    elif api_format == 'anthropic' and api_key:
                        headers['x-api-key'] = api_key
                        headers['anthropic-version'] = '2023-06-01'
                        payload = {
                            'model': model_name,
                            'max_tokens': 5,
                            'messages': [{'role': 'user', 'content': 'Hi'}]
                        }
                    elif api_format == 'google' and api_key:
                        payload = {
                            'contents': [{'parts': [{'text': 'Hi'}]}]
                        }
                        test_endpoint = f"{test_endpoint}?key={api_key}"
                    else:
                        if api_key:
                            headers['Authorization'] = f'Bearer {api_key}'
                        payload = {
                            'model': model_name,
                            'messages': [{'role': 'user', 'content': 'Hi'}],
                            'max_tokens': 5
                        }
                    
                    print(f"发送测试请求到: {test_endpoint} (尝试 {retry_count + 1}/{max_retries})")
                    print(f"请求头: {json.dumps(headers, indent=2)}")
                    print(f"请求体: {json.dumps(payload, indent=2)}")
                    response = requests.post(test_endpoint, headers=headers, json=payload, timeout=15, proxies={'http': None, 'https': None})
                    
                    print(f"测试响应状态码: {response.status_code}")
                    print(f"测试响应内容: {response.text[:500]}...")
                    
                    # 即使返回401（认证失败），也说明端点是可达的
                    if response.status_code in [200, 401, 403]:
                        print("连接测试成功！")
                        
                        # 如果找到正确的端点，更新配置
                        if test_endpoint != endpoint:
                            print(f"发现正确的端点: {test_endpoint}")
                            custom_config['endpoint'] = test_endpoint
                        
                        return True
                    elif response.status_code == 404:
                        print(f"端点不存在 (404)，尝试下一个...")
                        break  # 404的话，这个端点肯定不行，换下一个
                    else:
                        print(f"连接测试失败: {response.status_code}")
                        # 增加重试机制
                        retry_count += 1
                        if retry_count < max_retries:
                            print(f"重试中... ({retry_count}/{max_retries})")
                            time.sleep(1)  # 等待1秒后重试
                        else:
                            print("这个端点尝试失败，尝试下一个...")
                            break
                
                except requests.exceptions.Timeout:
                    print(f"请求超时，尝试下一个端点...")
                    break
                except requests.exceptions.RequestException as e:
                    print(f"网络请求失败: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"重试中... ({retry_count}/{max_retries})")
                        time.sleep(1)
                    else:
                        print("这个端点尝试失败，尝试下一个...")
                        break
                except Exception as e:
                    print(f"测试过程中发生错误: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    break
        
        # 所有端点都尝试失败了
        print("\n所有端点尝试失败！")
        print("建议：")
        print("1. 检查API Key是否正确")
        print("2. 确认API端点路径是否完整")
        print("3. 检查网络连接")
        return False