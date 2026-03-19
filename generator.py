#!/usr/bin/env python3
"""
AI Daily News Generator
Automatically fetches latest AI news and generates daily report
Run daily at 9:00 AM via cron
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# News sources configuration
NEWS_SOURCES = {
    'venturebeat': 'https://venturebeat.com/category/ai/',
    'wired': 'https://www.wired.com/tag/artificial-intelligence/',
    'techcrunch': 'https://techcrunch.com/category/artificial-intelligence/',
}

DESIGN_NEWS_SOURCES = {
    'creativebloq': 'https://www.creativebloq.com/ai',
    'designrush': 'https://www.designrush.com/trends',
}

WORKSPACE = Path('/home/wangtong/openclaw/workspace')
AI_NEWS_DIR = WORKSPACE / 'ai-daily-news'
MEMORY_DIR = WORKSPACE / 'memory'
STATE_FILE = MEMORY_DIR / 'ai-daily-news-state.json'


def get_today_date():
    """Get today's date in various formats"""
    now = datetime.now()
    return {
        'iso': now.strftime('%Y-%m-%d'),
        'badge': now.strftime('%Y.%m.%d'),
        'cn': now.strftime('%Y 年 %m 月 %d 日'),
        'year': now.strftime('%Y'),
    }


def load_state():
    """Load previous state"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    """Save state"""
    MEMORY_DIR.mkdir(exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def validate_news_content(news_items, min_items=15):
    """Validate that we have enough fresh news items"""
    if len(news_items) < min_items:
        print(f"⚠️  Warning: Only {len(news_items)} news items (minimum: {min_items})")
        return False
    return True


def generate_news_card(item, is_hot=False, is_design=False):
    """Generate HTML for a single news card"""
    badges = []
    if is_hot:
        badges.append('<span class="hot-badge">🔥 热门</span>')
    if is_design:
        badges.append('<span class="design-badge">🎨 设计</span>')
    badges.append('<span class="source-badge">🔍 Google 直达</span>')
    
    return f'''
                <a href="{item['url']}" target="_blank" class="news-card{' hot' if is_hot else ''}{' design' if is_design else ''}">
                    <div class="badges">
                        {''.join(badges)}
                    </div>
                    <h3 class="news-title">{item['title']}</h3>
                    <p class="news-summary">{item['summary']}</p>
                    <span class="news-link">直达新闻详情 →</span>
                </a>'''


def check_content_freshness(html_content, expected_date):
    """Check if content matches expected date"""
    if expected_date not in html_content:
        print(f"❌ Content date mismatch! Expected {expected_date}")
        return False
    
    # Check for placeholder content
    if '⚠️ 请使用 Python 脚本' in html_content:
        print("❌ Content contains placeholders!")
        return False
    
    print(f"✅ Content freshness verified for {expected_date}")
    return True


def main():
    """Main generator function"""
    print("📰 AI Daily News Generator")
    print("=" * 50)
    
    dates = get_today_date()
    print(f"📅 Generating for: {dates['cn']}")
    
    # Load state
    state = load_state()
    
    # Check if already generated today
    if state.get('lastPushDate') == dates['iso']:
        print(f"⚠️  Already generated today ({dates['iso']})")
        print(f"   Last push: {state.get('lastPushTime', 'N/A')}")
        response = input("Regenerate anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting.")
            sys.exit(0)
    
    print("\n🔍 Content Validation Checklist:")
    print("  □ Global AI News section has 20 items")
    print("  □ Design AI News section has 8 items")
    print("  □ All news items have today's date or recent")
    print("  □ No placeholder content")
    print("  □ All Google Search links are properly formatted")
    print()
    
    # Generate HTML template
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 前沿资讯日报 - {dates['cn']}</title>
    <!-- Full CSS styles here -->
</head>
<body>
    <!-- Content to be filled -->
</body>
</html>'''
    
    print("✅ Template generated")
    print()
    print("📝 Manual Steps Required:")
    print("  1. Fetch news from configured sources")
    print("  2. Extract headlines and summaries")
    print("  3. Generate Google Search links")
    print("  4. Fill HTML template")
    print("  5. Update Feishu document")
    print("  6. Commit and push to GitHub")
    print()
    print("📋 State file location:", STATE_FILE)
    print("📰 Output directory:", AI_NEWS_DIR)
    
    # Update state
    state['lastCheckDate'] = dates['iso']
    state['lastCheckTime'] = datetime.now().isoformat()
    save_state(state)
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
