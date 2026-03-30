#!/usr/bin/env python3
"""Update index.html with today's news content - 2026-03-30"""

import re
from pathlib import Path

WORKSPACE = Path('/home/wangtong/openclaw/workspace')
HTML_FILE = WORKSPACE / 'ai-daily-news' / 'index.html'

# Global AI News (20 items) - 2026-03-30
GLOBAL_NEWS = [
    ("OpenAI 关闭 Sora 视频生成服务，转向 IPO", "OpenAI 宣布关闭 Sora 视频生成服务，将资源集中于即将到来的 IPO 和 AI 超级应用开发。", "OpenAI+shuts+down+Sora+IPO+AI+superapp", True),
    ("苹果 Siri 将开放第三方 AI 扩展", "苹果计划在 iOS 27 中推出 Siri Extensions 功能，允许用户安装第三方 AI 聊天机器人并在 Siri 内部运行。", "Apple+Siri+third-party+AI+Extensions+iOS+27", True),
    ("Anthropic 新模型 Mythos 信息泄露", "Anthropic 的未发布模型名称 Mythos 及其他内部信息在未保护的数据存储库中被发现。", "Anthropic+Mythos+model+leaked+security+breach", True),
    ("法官称五角大楼对 Anthropic 制裁非法", "在 Anthropic 诉美国国防部案件中，法官称惩罚 Anthropic 是非法的第一修正案报复行为。", "Anthropic+Pentagon+lawsuit+First+Amendment+Judge+Lin", True),
    ("NVIDIA CEO 黄仁勋宣称已实现 AGI", "NVIDIA 首席执行官黄仁勋认为我们已经实现了人工通用智能 AGI。", "Jensen+Huang+NVIDIA+AGI+achieved", True),
    ("OpenAI 洽谈收购核聚变能源公司", "Sam Altman 辞去 Helion Energy 董事会职务，OpenAI 正与这家核聚变初创公司进行高级谈判。", "OpenAI+Helion+fusion+energy+acquisition", True),
    ("谷歌 TurboQuant 算法减少 AI 内存 6 倍", "谷歌研究院发布新压缩算法 TurboQuant，可将大型语言模型存储数据缩小至少 6 倍且零精度损失。", "Google+TurboQuant+AI+memory+compression+algorithm", True),
    ("苹果与谷歌达成协议使用 Gemini 训练模型", "苹果据报道拥有对谷歌 Gemini 的完全访问权，可通过蒸馏技术训练专用于苹果设备的学生 AI 模型。", "Apple+Google+Gemini+distillation+student+models", True),
    ("欧盟电池法规阻碍 Meta AI 眼镜扩张", "欧盟要求设备在 2027 年前使用可拆卸电池的规定阻碍了 Meta Ray-Ban Display 智能眼镜推出。", "EU+battery+rules+Meta+AI+glasses+expansion", True),
    ("英特尔发布首款 AI 专用桌面 GPU", "英特尔宣布新款 Arc Pro B70 Big Battlemage 桌面 GPU，配备 32GB VRAM，售价 949 美元起。", "Intel+Arc+Pro+B70+Big+Battlemage+GPU+AI", True),
    ("音乐行业对 AI 采取不问不说政策", "各流派艺术家都在使用 AI 实验编曲但无人愿意承认，制作人猜测超一半采样嘻哈音乐用 AI 制作。", "music+industry+AI+don+t+ask+don+t+tell+policy", False),
    ("谷歌 AI 搜索被指控披露幸存者信息", "集体诉讼中 Epstein 幸存者指控谷歌不当披露幸存者个人数据。", "Google+AI+search+Epstein+survivors+privacy+lawsuit", False),
    ("Beehiiv 新闻稿管理接入 AI 机器人", "通过 MCP 连接 Beehiiv 账户到 AI 聊天机器人，客户可请求语法检查和订阅者洞察。", "Beehiiv+MCP+AI+chatbots+newsletter+management", False),
    ("自动化播客工具窃取 Zoom 会议内容", "WebinarTV 被曝抓取公开 Zoom 会议链接，未经告知将通话录音转化为平台内容。", "WebinarTV+scraping+Zoom+meetings+podcast+theft", False),
    ("参议员要求了解数据中心能耗数据", "多位参议员致信要求科技公司披露数据中心能源使用情况。", "Senators+data+centers+energy+usage+AI", False),
    ("桑德斯 AI 安全法案将暂停数据中心建设", "参议员伯尼桑德斯提出新 AI 安全法案要求暂停数据中心建设。", "Bernie+Sanders+AI+safety+bill+data+center+construction", False),
    ("AI 研究正沿地缘政治路线分裂", "WIRED 报道 AI 研究越来越难以与地缘政治分离，中美技术竞争塑造全球 AI 发展。", "AI+research+geopolitics+China+US+split", False),
    ("科技记者开始使用 AI 协助写作", "越来越多的科技记者开始使用 AI 工具帮助撰写和编辑报道。", "tech+reporters+using+AI+write+edit+stories", False),
    ("Anthropic 否认会在战争期间破坏 AI 工具", "在法庭文件中 Anthropic 否认了可能在战争期间破坏其 AI 工具的指控。", "Anthropic+denies+sabotage+AI+tools+war+Claude", False),
    ("游戏玩家讨厌 NVIDIA 的 DLSS 5", "NVIDIA 最新的 DLSS 5 技术遭到游戏玩家和开发者的双重批评。", "NVIDIA+DLSS+5+gamers+developers+criticism", False),
]

# Design AI News (8 items) - 2026-03-30
DESIGN_NEWS = [
    ("AI 玩具可能阻碍幼儿情感发展", "剑桥大学研究警告设计师在创作 AI 玩具时需要与儿童发展专家密切合作。", "AI+toys+emotional+development+children+Cambridge+study", False),
    ("建筑师是 AI 最易自动化职业之一", "Anthropic 研究发现建筑师和工程师的许多工作可用大语言模型快两倍完成。", "architects+engineers+most+automatable+AI+Anthropic+research", False),
    ("英国政府聘请谷歌开发 AI 规划工具", "谷歌将为住房部开发 AI 工具加速规划决策流程实现即时决策。", "UK+government+Google+AI+planning+tool+instant+decisions", False),
    ("石英戒指在 AI 时代证明人类身份", "设计工作室 Modem 和 Retinaa 设计概念戒指应对深度伪造诈骗。", "quartz+ring+human+identity+verification+AI+deepfake", False),
    ("AI 工作空间 Avoice 拉平竞争格局", "旧金山初创 Avoice 开发建筑师在线工作空间用 AI 自动化重复工作。", "Avoice+AI+workspace+architects+small+firms", False),
    ("软件设计师必须放弃守护者角色", "Nick Foster 撰文指出设计师应将 AI 缺陷作为机会摆脱冷酷理性方法。", "software+designers+AI+Nick+Foster+opinion", False),
    ("MIT 开发 AI 气味记忆机器", "MIT 媒体实验室原型机使用生成式 AI 将照片内容转化为独特香水。", "MIT+AI+scent+memory+machine+photographs+fragrances", False),
    ("人形机器人 Ai-Da 设计房屋展出", "Aidan Meller 和 AI 驱动创作 Ai-Da 在丹麦 Utzon 中心展出首个人形机器人设计建筑概念。", "Ai-Da+robot+home+design+Utzon+Center+Denmark", False),
]

def generate_news_card(title, summary, query, is_hot=False, is_design=False):
    """Generate HTML for a single news card"""
    badges = []
    if is_hot:
        badges.append('<span class="hot-badge">🔥 热门</span>')
    if is_design:
        badges.append('<span class="design-badge">🎨 设计</span>')
    badges.append('<span class="source-badge">🔍 Google 直达</span>')
    
    card_class = "news-card"
    if is_hot:
        card_class += " hot"
    if is_design:
        card_class += " design"
    
    return f'''
            <a href="https://www.google.com/search?q={query}&btnI=1" target="_blank" class="{card_class}">
                <div class="badges">
                    {''.join(badges)}
                </div>
                <h3 class="news-title">{title}</h3>
                <p class="news-summary">{summary}</p>
                <span class="news-link">直达新闻详情 →</span>
            </a>'''

def main():
    html_path = Path(HTML_FILE)
    content = html_path.read_text(encoding='utf-8')
    
    # Generate global news HTML
    global_news_html = '\n'.join([
        generate_news_card(title, summary, query, is_hot)
        for title, summary, query, is_hot in GLOBAL_NEWS
    ])
    
    # Generate design news HTML
    design_news_html = '\n'.join([
        generate_news_card(title, summary, query, is_design=True)
        for title, summary, query, _ in DESIGN_NEWS
    ])
    
    # Find and replace global news section
    global_pattern = r'(<h2 class="section-title"><span class="emoji">🌍</span>全球动态</h2>\s*<div class="news-grid">).*</div>\s*(<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>)'
    global_replacement = r'\1' + global_news_html + '\n        </div>\n        \2'
    
    content = re.sub(global_pattern, global_replacement, content, flags=re.DOTALL)
    
    # Find and replace design news section
    design_pattern = r'(<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>\s*<div class="news-grid">).*</div>\s*</div>\s*<footer'
    design_replacement = r'\1' + design_news_html + '\n        </div>\n    </div>\n    <footer'
    
    content = re.sub(design_pattern, design_replacement, content, flags=re.DOTALL)
    
    # Write updated content
    html_path.write_text(content, encoding='utf-8')
    print("✅ HTML updated successfully!")
    print(f"   Global news: {len(GLOBAL_NEWS)} items")
    print(f"   Design news: {len(DESIGN_NEWS)} items")

if __name__ == '__main__':
    main()
