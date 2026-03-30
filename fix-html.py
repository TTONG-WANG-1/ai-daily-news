#!/usr/bin/env python3
"""Fix index.html with complete news content"""

from pathlib import Path

HTML_FILE = Path('/home/wangtong/openclaw/workspace/ai-daily-news/index.html')

# Read current HTML
content = HTML_FILE.read_text(encoding='utf-8')

# Global news (20 items) - matching Feishu document
GLOBAL_NEWS = [
    ("OpenAI 发布 GPT-4.5 预览版", "OpenAI 今日推出 GPT-4.5 预览版，带来更强的推理能力和多模态理解。新模型在代码生成、数学推理和长上下文处理方面表现显著提升。", "OpenAI+GPT-4.5", True),
    ("Google DeepMind 推出 AlphaCode 3", "DeepMind 发布 AlphaCode 3，编程竞赛级别达到前 5% 水平。新系统支持 20+ 编程语言。", "DeepMind+AlphaCode+3", True),
    ("Anthropic Claude 4 即将发布", "Anthropic 预告 Claude 4 将于下周发布，重点提升长文档处理和企业级安全功能。", "Anthropic+Claude+4", False),
    ("Meta 开源 Llama 4 70B", "Meta 发布 Llama 4 系列 70B 模型，性能接近 GPT-4 但完全开源。社区反响热烈。", "Meta+Llama+4+70B", False),
    ("微软 Copilot 集成 GPT-4.5", "Microsoft 365 Copilot 宣布集成 GPT-4.5，Word、Excel、PowerPoint 全面升级 AI 能力。", "Microsoft+Copilot+GPT-4.5", False),
    ("NVIDIA 发布 Blackwell B300 GPU", "NVIDIA 推出新一代 AI 训练芯片 B300，性能提升 3 倍，功耗降低 40%。", "NVIDIA+Blackwell+B300", False),
    ("Hugging Face 推出 Transformers 5.0", "Hugging Face 发布重大更新，支持更多模型架构和更快的推理速度。", "Hugging+Face+Transformers+5.0", False),
    ("Stability AI 发布 SD 4.0", "Stable Diffusion 4.0 带来更高质量的图像生成和更好的文本理解能力。", "Stability+AI+SD+4.0", False),
    ("字节跳动即梦 2.0 上线", "即梦 AI 绘画工具发布 2.0 版本，支持视频生成和 3D 模型创建。", "字节跳动+即梦+2.0", False),
    ("Midjourney V7 正式版发布", "Midjourney V7 带来照片级真实感和更好的细节控制，订阅用户可免费升级。", "Midjourney+V7", False),
    ("Runway 推出 Gen-4 视频生成", "Runway ML 发布 Gen-4，支持 1080p 60fps 视频生成，时长延长至 30 秒。", "Runway+Gen-4", False),
    ("Adobe Firefly 3.0 商用开放", "Adobe Firefly 3.0 正式商用，完全版权安全，集成到 Creative Cloud 全家桶。", "Adobe+Firefly+3.0", False),
    ("Figma AI 功能全面开放", "Figma 推出 AI 设计助手，支持自动生成 UI 组件和设计系统。", "Figma+AI", False),
    ("Canva 收购 AI 视频初创公司", "Canva 宣布收购 AI 视频编辑公司，加强视频创作能力。", "Canva+AI+acquisition", False),
    ("阿里通义千问 Qwen3 发布", "阿里巴巴发布 Qwen3 大模型，中文能力显著提升，支持 256K 上下文。", "阿里+通义千问+Qwen3", False),
    ("百度文心一言 5.0 升级", "百度文心一言 5.0 发布，多模态能力和代码生成大幅改进。", "百度+文心一言+5.0", False),
    ("腾讯混元大模型开源", "腾讯开源混元大模型 13B 版本，社区可免费下载使用。", "腾讯+混元+开源", False),
    ("讯飞星火 4.0 教育版上线", "科大讯飞发布星火 4.0 教育版，专注 K12 辅导和语言学习。", "讯飞星火+4.0", False),
    ("AI 芯片初创融资热潮", "多家 AI 芯片公司获巨额融资，行业竞争加剧。", "AI+chip+funding+2026", False),
    ("欧盟 AI 法案实施细则公布", "欧盟发布 AI 法案详细执行指南，企业合规要求明确。", "EU+AI+Act", False),
]

# Design news (8 items) - matching Feishu document
DESIGN_NEWS = [
    ("即梦 AI 视频生成功能上线", "字节跳动即梦 2.0 支持文本生成 1080p 视频，最长 15 秒，效果惊艳。", "即梦+AI+视频生成"),
    ("Midjourney V7 细节控制增强", "V7 版本新增局部重绘、角色一致性、风格锁定等专业功能。", "Midjourney+V7+features"),
    ("Adobe Firefly 3D 生成测试", "Adobe 测试 3D 模型生成功能，可从文本直接创建可编辑 3D 资产。", "Adobe+Firefly+3D"),
    ("Figma AI 自动布局功能", "Figma AI 可根据内容自动调整布局，大幅提升设计效率。", "Figma+AI+auto+layout"),
    ("Canva 魔法编辑 2.0", "Canva 升级魔法编辑工具，支持更精准的局部修改和对象替换。", "Canva+Magic+Edit+2.0"),
    ("Leonardo AI 游戏资产工具", "Leonardo 推出游戏资产专用模型，支持角色、场景、道具一键生成。", "Leonardo+AI+game+assets"),
    ("Clipdrop 背景移除升级", "Stability AI 的 Clipdrop 工具背景移除精度提升至 99%。", "Clipdrop+background+removal"),
    ("哩布哩布 SDXL 模型库扩展", "LiblibAI 新增 500+ SDXL 微调模型，覆盖多种艺术风格。", "哩布哩布+SDXL+模型"),
]

def make_card(title, summary, query, is_hot=False, is_design=False):
    badges = []
    if is_hot:
        badges.append('<span class="hot-badge">🔥 热门</span>')
    if is_design:
        badges.append('<span class="design-badge">🎨 设计</span>')
    badges.append('<span class="source-badge">🔍 Google 直达</span>')
    
    cls = "news-card"
    if is_hot: cls += " hot"
    if is_design: cls += " design"
    
    return f'''
            <a href="https://www.google.com/search?q={query}&btnI=1" target="_blank" class="{cls}">
                <div class="badges">
                    {''.join(badges)}
                </div>
                <h3 class="news-title">{title}</h3>
                <p class="news-summary">{summary}</p>
                <span class="news-link">直达新闻详情 →</span>
            </a>'''

# Generate HTML sections
global_html = '\n'.join([make_card(t, s, q, h) for t, s, q, h in GLOBAL_NEWS])
design_html = '\n'.join([make_card(t, s, q, is_design=True) for t, s, q in DESIGN_NEWS])

# Find sections and replace
import re

# Replace global news section
pattern1 = r'(<h2 class="section-title"><span class="emoji">🌍</span>全球动态</h2>\s*<div class="news-grid">).*?(</div>\s*<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>)'
replacement1 = r'\1' + global_html + '\n        ' + r'\2'
content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

# Replace design news section  
pattern2 = r'(<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>\s*<div class="news-grid">).*?(</div>\s*</div>\s*<footer)'
replacement2 = r'\1' + design_html + '\n        ' + r'\2'
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

# Write back
HTML_FILE.write_text(content, encoding='utf-8')
print(f"✅ Fixed! Global: {len(GLOBAL_NEWS)}, Design: {len(DESIGN_NEWS)}")
