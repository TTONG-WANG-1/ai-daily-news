#!/usr/bin/env python3
"""
Generate index.html from 2026-04-02.md - Complete rewrite
"""

import re
from pathlib import Path
from datetime import datetime

AI_NEWS_DIR = Path('/home/wangtong/openclaw/workspace/ai-daily-news')
MD_FILE = AI_NEWS_DIR / '2026-04-02.md'
HTML_FILE = AI_NEWS_DIR / 'index.html'

def parse_md_news(md_content, section_marker):
    """Parse news items from markdown section"""
    news_items = []
    section_start = md_content.find(section_marker)
    if section_start == -1:
        return news_items
    
    # Find next section
    next_section = md_content.find('\n## ', section_start + 10)
    section_content = md_content[section_start:next_section] if next_section != -1 else md_content[section_start:]
    
    # Parse each news item
    pattern = r'### \d+\. [🔥🎨]*\s*(.+?)\n\*\*来源：\*\*(.+?)\| \*\*日期：\*\*(.+?)\n\[🔗 Google 智能直达\]\((.+?)\)\n\n(.+?)(?=\n---|\Z)'
    
    for match in re.finditer(pattern, section_content, re.DOTALL):
        title = match.group(1).strip()
        source = match.group(2).strip()
        date = match.group(3).strip()
        link = match.group(4).strip()
        summary = match.group(5).strip()
        
        # Clean up summary
        summary = re.sub(r'\s+', ' ', summary).strip()
        if len(summary) > 200:
            summary = summary[:197] + '...'
        
        news_items.append({
            'title': title,
            'link': link,
            'summary': summary,
            'is_hot': '🔥' in title
        })
    
    return news_items

def make_card(item, is_hot=False, is_design=False, is_openclaw=False):
    """Generate HTML card for a news item"""
    badges = []
    classes = ['news-card']
    
    if is_hot:
        badges.append('<span class="hot-badge">🔥 热门</span>')
        classes.append('hot')
    
    if is_design:
        badges.append('<span class="design-badge">🎨 设计</span>')
        classes.append('design')
    
    if is_openclaw:
        badges.append('<span class="openclaw-badge">🦞 OpenClaw</span>')
        classes.append('openclaw')
    
    badges.append('<span class="source-badge">🔍 Google 直达</span>')
    
    return f'''            <a href="{item['link']}" target="_blank"  class="{' '.join(classes)}">
                <div class="badges">
                    {''.join(badges)}
                </div>
                <h3 class="news-title">{item['title']}</h3>
                <p class="news-summary">{item['summary']}</p>
                <span class="news-link">直达新闻详情 →</span>
            </a>'''

def generate_html():
    # Read markdown file
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Parse news from markdown
    global_news = parse_md_news(md_content, '## 🔥 全球 AI 动态')
    design_news = parse_md_news(md_content, '## 🎨 设计 AI 资讯')
    
    print(f"Parsed {len(global_news)} global news, {len(design_news)} design news")
    
    # OpenClaw news
    openclaw_news = [
        {'title': 'OpenClaw v2026.4.1: openclaw 2026.4.1', 'link': 'https://www.google.com/search?q=OpenClaw%20v2026.4.1%3A%20openclaw%202026.4.1&btnI=1', 'summary': '新增 `/tasks` 命令，为当前会话提供聊天原生后台任务板。', 'is_hot': True},
        {'title': 'OpenClaw v2026.4.1-beta.1', 'link': 'https://www.google.com/search?q=OpenClaw%20v2026.4.1-beta.1&btnI=1', 'summary': '任务板功能测试版发布，支持会话内任务管理。'},
        {'title': 'OpenClaw v2026.3.31', 'link': 'https://www.google.com/search?q=OpenClaw%20v2026.3.31&btnI=1', 'summary': '移除重复的 nodes.run shell 包装器，统一节点执行路径。'},
        {'title': 'fix(msteams): prevent duplicate text', 'link': 'https://www.google.com/search?q=OpenClaw%20fix%28msteams%29&btnI=1', 'summary': '修复 Teams 流式响应超过 4000 字符时的重复文本问题。'},
        {'title': 'Matrix: restore ordered progress', 'link': 'https://www.google.com/search?q=OpenClaw%20Matrix%20restore&btnI=1', 'summary': '恢复 Matrix 有序进度交付，支持显式流式模式。'},
    ]
    
    # Generate HTML
    dates = {'cn': '2026 年 04 月 02 日', 'weekday': '星期四'}
    
    global_html = '\n'.join([make_card(item, is_hot=item['is_hot']) for item in global_news[:20]])
    design_html = '\n'.join([make_card(item, is_design=True) for item in design_news[:8]])
    openclaw_html = '\n'.join([make_card(item, is_openclaw=True, is_hot=(i==0)) for i, item in enumerate(openclaw_news[:5])])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 前沿资讯日报 - {dates["cn"]}</title>
    
    <!-- Apple System Fonts -->
    <style>
        @font-face {{
            font-family: 'PingFang SC';
            src: local('PingFang SC Regular'), local('PingFangSC-Regular');
            font-weight: 400;
        }}
        @font-face {{
            font-family: 'PingFang SC';
            src: local('PingFang SC Medium'), local('PingFangSC-Medium');
            font-weight: 500;
        }}
        @font-face {{
            font-family: 'PingFang SC';
            src: local('PingFang SC Semibold'), local('PingFangSC-Semibold');
            font-weight: 600;
        }}
    </style>
    
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a25;
            --bg-glass: rgba(26, 26, 37, 0.6);
            
            --text-primary: #ffffff;
            --text-secondary: #a0a0b0;
            --text-tertiary: #6b6b7b;
            
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
            
            --hot-gradient: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
            --design-gradient: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
            --openclaw-gradient: linear-gradient(135deg, #f97316 0%, #fb923c 50%, #fdba74 100%);
            --product-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);
            
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(99, 102, 241, 0.3);
            
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.15);
            
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 24px;
            
            --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);
        }}

        html {{ scroll-behavior: smooth; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
        }}

        .bg-gradient {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(168, 85, 247, 0.05) 0%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        }}

        .header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(10, 10, 15, 0.8);
            backdrop-filter: saturate(180%) blur(20px);
            border-bottom: 1px solid var(--border-subtle);
            z-index: 1000;
            padding: 16px 0;
        }}

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            text-decoration: none;
        }}

        .date-badge {{
            font-size: 13px;
            font-weight: 500;
            color: var(--text-tertiary);
            padding: 6px 14px;
            background: var(--bg-card);
            border-radius: var(--radius-xl);
            border: 1px solid var(--border-subtle);
        }}

        .hero {{
            position: relative;
            text-align: center;
            padding: 160px 32px 100px;
            background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        }}

        .hero h1 {{
            font-size: clamp(48px, 10vw, 96px);
            font-weight: 600;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0b0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }}

        .hero-date {{
            font-size: 18px;
            color: var(--text-secondary);
            font-weight: 400;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 32px 80px;
            position: relative;
            z-index: 1;
        }}

        .section-title {{
            font-size: 28px;
            font-weight: 600;
            margin: 60px 0 32px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .section-title .emoji {{
            font-size: 32px;
        }}

        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 24px;
        }}

        .news-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: all var(--transition-base);
            display: flex;
            flex-direction: column;
            gap: 12px;
            position: relative;
            overflow: hidden;
        }}

        .news-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--accent-gradient);
            opacity: 0;
            transition: opacity var(--transition-base);
        }}

        .news-card:hover {{
            transform: translateY(-4px);
            border-color: var(--border-highlight);
            box-shadow: var(--shadow-glow);
        }}

        .news-card:hover::before {{
            opacity: 1;
        }}

        .news-card.hot {{
            border-color: rgba(249, 115, 22, 0.3);
        }}

        .news-card.hot::before {{
            background: var(--hot-gradient);
            opacity: 1;
        }}

        .news-card.design {{
            border-color: rgba(6, 182, 212, 0.3);
        }}

        .news-card.design::before {{
            background: var(--design-gradient);
            opacity: 1;
        }}

        .news-card.openclaw {{
            border-color: rgba(249, 115, 22, 0.3);
        }}

        .news-card.openclaw::before {{
            background: var(--openclaw-gradient);
            opacity: 1;
        }}

        .badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .hot-badge {{
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            background: var(--hot-gradient);
            border-radius: var(--radius-sm);
            color: white;
        }}

        .design-badge {{
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            background: var(--design-gradient);
            border-radius: var(--radius-sm);
            color: white;
        }}

        .openclaw-badge {{
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            background: var(--openclaw-gradient);
            border-radius: var(--radius-sm);
            color: white;
        }}

        .source-badge {{
            font-size: 12px;
            font-weight: 500;
            padding: 4px 10px;
            background: var(--bg-glass);
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            border: 1px solid var(--border-subtle);
        }}

        .news-title {{
            font-size: 18px;
            font-weight: 600;
            line-height: 1.4;
            color: var(--text-primary);
            transition: color var(--transition-fast);
        }}

        .news-card:hover .news-title {{
            color: var(--accent-primary);
        }}

        .news-summary {{
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.6;
            flex-grow: 1;
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .news-link {{
            font-size: 13px;
            font-weight: 500;
            color: var(--accent-primary);
            margin-top: auto;
        }}

        footer {{
            text-align: center;
            padding: 40px 32px;
            border-top: 1px solid var(--border-subtle);
            color: var(--text-tertiary);
            font-size: 14px;
        }}

        footer a {{
            color: var(--accent-primary);
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="bg-gradient"></div>
    
    <header class="header">
        <div class="header-content">
            <a href="#" class="logo">🦞 AI Daily News</a>
            <span class="date-badge">{dates["cn"]}</span>
        </div>
    </header>

    <section class="hero">
        <h1>AI 前沿资讯日报</h1>
        <p class="hero-date">{dates["cn"]} {dates["weekday"]}</p>
    </section>

    <div class="container">
        <h2 class="section-title"><span class="emoji">🌍</span>全球动态</h2>
        <div class="news-grid">
{global_html}
        </div>

        <h2 class="section-title"><span class="emoji">🦞</span>openclaw 龙虾资讯</h2>
        <div class="news-grid">
{openclaw_html}
        </div>

        <h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>
        <div class="news-grid">
{design_html}
        </div>
    </div>

    <footer>
        <p>📊 今日统计：全球动态 {len(global_news)} 条 | 🦞 OpenClaw {len(openclaw_news)} 条 | 设计 AI {len(design_news)} 条</p>
        <p>🔗 <a href="https://github.com/TTONG-WANG-1/ai-daily-news" target="_blank">GitHub 仓库</a></p>
        <p style="margin-top: 16px; color: var(--text-tertiary);">© 2026 AI Daily News. Generated automatically.</p>
    </footer>
</body>
</html>'''
    
    return html

def main():
    html = generate_html()
    
    # Write HTML
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML generated: {HTML_FILE}")
    
    # Git push
    import subprocess
    print("\n📤 Pushing to GitHub...")
    try:
        subprocess.run(['git', 'add', str(HTML_FILE)], cwd=AI_NEWS_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Update 2026-04-02 with latest news'], cwd=AI_NEWS_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'push'], cwd=AI_NEWS_DIR, check=True, capture_output=True, timeout=60)
        print("   ✅ Pushed")
    except Exception as e:
        print(f"   ⚠️  Git error: {e}")

if __name__ == '__main__':
    main()