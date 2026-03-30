#!/usr/bin/env python3
"""
Build index.html from fetched RSS news
"""

import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path('/home/wangtong/openclaw/workspace')
AI_NEWS_DIR = WORKSPACE / 'ai-daily-news'
FETCHED_FILE = AI_NEWS_DIR / 'fetched-news.json'
HTML_FILE = AI_NEWS_DIR / 'index.html'
TEMPLATE_FILE = AI_NEWS_DIR / 'template.html'

def get_today_date():
    now = datetime.now()
    return {
        'iso': now.strftime('%Y-%m-%d'),
        'badge': now.strftime('%Y.%m.%d'),
        'cn': now.strftime('%Y 年 %m 月 %d 日'),
        'weekday': now.strftime('%A'),
    }

def make_card(item, is_hot=False, is_design=False):
    badges = []
    if is_hot:
        badges.append('<span class="hot-badge">🔥 热门</span>')
    if is_design:
        badges.append('<span class="design-badge">🎨 设计</span>')
    badges.append('<span class="source-badge">🔍 Google 直达</span>')
    
    cls = "news-card"
    if is_hot: cls += " hot"
    if is_design: cls += " design"
    
    # Use Google Search link for direct access
    query = item['title'].replace(' ', '+')
    
    return f'''
            <a href="https://www.google.com/search?q={query}&btnI=1" target="_blank" rel="noopener noreferrer" class="{cls}">
                <div class="badges">
                    {''.join(badges)}
                </div>
                <h3 class="news-title">{item['title']}</h3>
                <p class="news-summary">{item['summary'][:150]}...</p>
                <span class="news-link">直达新闻详情 →</span>
            </a>'''

def main():
    dates = get_today_date()
    
    # Load fetched news
    with open(FETCHED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    global_news = data['global_news'][:20]
    design_news = data['design_news'][:8]
    
    # Read template
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Generate news sections
    global_html = '\n'.join([
        make_card(item, is_hot=(i < 2)) for i, item in enumerate(global_news)
    ])
    
    design_html = '\n'.join([
        make_card(item, is_design=True) for item in design_news
    ])
    
    # Replace placeholders in template
    content = template
    content = content.replace('DATE_PLACEHOLDER', dates['cn'])
    content = content.replace('2026.03.24', dates['badge'])
    content = content.replace('2026 年 03 月 24 日 星期二', f"{dates['cn']} {dates['weekday']}")
    
    # Replace news sections
    import re
    content = re.sub(
        r'(<h2 class="section-title"><span class="emoji">🌍</span>全球动态</h2>\s*<div class="news-grid">).*?(</div>\s*<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>)',
        r'\1' + global_html + '\n        ' + r'\2',
        content, flags=re.DOTALL
    )
    
    content = re.sub(
        r'(<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>\s*<div class="news-grid">).*?(</div>\s*</div>\s*<footer)',
        r'\1' + design_html + '\n        ' + r'\2',
        content, flags=re.DOTALL
    )
    
    # Write output
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ HTML built successfully!")
    print(f"   Global news: {len(global_news)} items")
    print(f"   Design news: {len(design_news)} items")
    print(f"   Date: {dates['cn']}")

if __name__ == '__main__':
    main()
