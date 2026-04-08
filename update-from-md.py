#!/usr/bin/env python3
"""
Update index.html from 2026-04-02.md
"""

import re
from pathlib import Path
from datetime import datetime

AI_NEWS_DIR = Path('/home/wangtong/openclaw/workspace/ai-daily-news')
MD_FILE = AI_NEWS_DIR / '2026-04-02.md'
HTML_FILE = AI_NEWS_DIR / 'index.html'
TEMPLATE_FILE = AI_NEWS_DIR / 'template.html'

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

def main():
    # Read markdown file
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Parse news from markdown
    global_news = parse_md_news(md_content, '## 🔥 全球 AI 动态')
    design_news = parse_md_news(md_content, '## 🎨 设计 AI 资讯')
    
    print(f"Parsed {len(global_news)} global news, {len(design_news)} design news")
    
    # Read template
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Generate HTML sections
    global_html = '\n'.join([make_card(item, is_hot=item['is_hot']) for item in global_news[:20]])
    design_html = '\n'.join([make_card(item, is_design=True) for item in design_news[:8]])
    
    # OpenClaw news (from GitHub)
    openclaw_news = [
        {'title': 'OpenClaw v2026.4.1: openclaw 2026.4.1', 'link': 'https://www.google.com/search?q=OpenClaw%20v2026.4.1%3A%20openclaw%202026.4.1&btnI=1', 'summary': '新增 `/tasks` 命令，为当前会话提供聊天原生后台任务板。', 'is_hot': True},
        {'title': 'OpenClaw v2026.4.1-beta.1', 'link': 'https://www.google.com/search?q=OpenClaw%20v2026.4.1-beta.1&btnI=1', 'summary': '任务板功能测试版发布，支持会话内任务管理。'},
        {'title': 'OpenClaw v2026.3.31', 'link': 'https://www.google.com/search?q=OpenClaw%20v2026.3.31&btnI=1', 'summary': '移除重复的 nodes.run shell 包装器，统一节点执行路径。'},
        {'title': 'fix(msteams): prevent duplicate text', 'link': 'https://www.google.com/search?q=OpenClaw%20fix%28msteams%29&btnI=1', 'summary': '修复 Teams 流式响应超过 4000 字符时的重复文本问题。'},
        {'title': 'Matrix: restore ordered progress', 'link': 'https://www.google.com/search?q=OpenClaw%20Matrix%20restore&btnI=1', 'summary': '恢复 Matrix 有序进度交付，支持显式流式模式。'},
    ]
    openclaw_html = '\n'.join([make_card(item, is_openclaw=True, is_hot=(i==0)) for i, item in enumerate(openclaw_news[:5])])
    
    # Product news (empty for now)
    product_html = ''
    
    # Replace in template
    content = template
    
    # Update date
    dates = {
        'badge': '2026.04.02',
        'cn': '2026 年 04 月 02 日',
        'weekday': '星期四'
    }
    content = re.sub(r'<title>AI 前沿资讯日报 - [^<]+</title>', 
                     f'<title>AI 前沿资讯日报 - {dates["cn"]}</title>', content)
    content = re.sub(r'<p class="hero-date">[^<]+</p>',
                     f'<p class="hero-date">{dates["cn"]} {dates["weekday"]}</p>', content)
    
    # Replace product section
    content = re.sub(
        r'(<h2 class="section-title"><span class="emoji">📢</span>产品动态</h2>\s*<div class="news-grid" id="product-news">).*?(</div>\s*<h2 class="section-title"><span class="emoji">🌍</span>全球动态</h2>)',
        r'\1' + product_html + '\n        ' + r'\2',
        content, flags=re.DOTALL
    )
    
    # Replace global news section
    content = re.sub(
        r'(<h2 class="section-title"><span class="emoji">🌍</span>全球动态</h2>\s*<div class="news-grid">).*?(</div>\s*<h2 class="section-title"><span class="emoji">🦞</span>openclaw 龙虾资讯</h2>)',
        r'\1' + global_html + '\n        ' + r'\2',
        content, flags=re.DOTALL
    )
    
    # Replace design news section
    content = re.sub(
        r'(<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>\s*<div class="news-grid">).*?(</div>\s*</div>\s*<footer)',
        r'\1' + design_html + '\n        ' + r'\2',
        content, flags=re.DOTALL
    )
    
    # Insert OpenClaw section
    content = re.sub(
        r'(<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>)',
        r'    <h2 class="section-title"><span class="emoji">🦞</span>openclaw 龙虾资讯</h2>\n        <div class="news-grid">\n' + openclaw_html + '\n        </div>\n\n        \1',
        content, flags=re.DOTALL
    )
    
    # Write HTML
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ HTML updated: {HTML_FILE}")
    
    # Git push
    import subprocess
    print("\n📤 Pushing to GitHub...")
    try:
        subprocess.run(['git', 'add', str(HTML_FILE)], cwd=AI_NEWS_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Update {dates["cn"]} from MD'], cwd=AI_NEWS_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'push'], cwd=AI_NEWS_DIR, check=True, capture_output=True, timeout=60)
        print("   ✅ Pushed")
    except Exception as e:
        print(f"   ⚠️  Git error: {e}")

if __name__ == '__main__':
    main()
