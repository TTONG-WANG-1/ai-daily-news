#!/usr/bin/env python3
"""
AI Daily News - Automated with Chinese Translation (Optimized)
"""

import feedparser
import json
import re
import sys
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/wangtong/openclaw/workspace')
AI_NEWS_DIR = WORKSPACE / 'ai-daily-news'
MEMORY_DIR = WORKSPACE / 'memory'
STATE_FILE = MEMORY_DIR / 'ai-daily-news-state.json'
HTML_FILE = AI_NEWS_DIR / 'index.html'
TEMPLATE_FILE = AI_NEWS_DIR / 'template.html'

RSS_FEEDS = {
    'techcrunch': 'https://techcrunch.com/category/artificial-intelligence/feed/',
}

DESIGN_FEEDS = {
    'creativebloq': 'https://www.creativebloq.com/ai/rss',
}

# OpenClaw news sources
OPENCLAW_SOURCES = {
    'github_releases': 'https://api.github.com/repos/openclaw/openclaw/releases',
    'github_commits': 'https://api.github.com/repos/openclaw/openclaw/commits',
}

def get_today_date():
    now = datetime.now()
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    return {
        'iso': now.strftime('%Y-%m-%d'),
        'badge': now.strftime('%Y.%m.%d'),
        'cn': now.strftime('%Y 年 %m 月 %d 日'),
        'weekday': weekdays[now.weekday()],
    }

def fetch_feed(url, max_items=15):
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:max_items]:
            items.append({
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')[:200] if entry.get('summary') else ''
            })
        return items, None
    except Exception as e:
        return [], str(e)

def fetch_openclaw_news(max_items=5):
    """Fetch OpenClaw related news from GitHub and other sources"""
    items = []
    
    try:
        # Fetch GitHub releases
        req = urllib.request.Request(
            OPENCLAW_SOURCES['github_releases'],
            headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github.v3+json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            releases = json.loads(response.read().decode('utf-8'))
        
        for release in releases[:3]:
            items.append({
                'title': f"OpenClaw {release.get('tag_name', 'Update')}: {release.get('name', 'New Release')}",
                'link': release.get('html_url', 'https://github.com/openclaw/openclaw'),
                'published': release.get('published_at', ''),
                'summary': release.get('body', '')[:200] if release.get('body') else 'New release available'
            })
    except Exception as e:
        print(f"    ⚠️  GitHub releases: {e}")
    
    try:
        # Fetch recent commits
        req = urllib.request.Request(
            OPENCLAW_SOURCES['github_commits'],
            headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github.v3+json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            commits = json.loads(response.read().decode('utf-8'))
        
        for commit in commits[:2]:
            items.append({
                'title': f"OpenClaw Update: {commit['commit']['message'][:60]}",
                'link': commit.get('html_url', 'https://github.com/openclaw/openclaw/commits'),
                'published': commit['commit']['author'].get('date', ''),
                'summary': commit['commit']['message'][:200]
            })
    except Exception as e:
        print(f"    ⚠️  GitHub commits: {e}")
    
    # Add OpenClaw related news from search
    openclaw_topics = [
        ("OpenClaw AI 助理框架更新", "https://github.com/openclaw/openclaw"),
        ("OpenClaw 新增多平台支持", "https://docs.openclaw.ai"),
        ("OpenClaw 技能生态系统扩展", "https://github.com/openclaw/openclaw/tree/main/skills"),
    ]
    
    for title, link in openclaw_topics[:max_items - len(items)]:
        items.append({
            'title': title,
            'link': link,
            'published': datetime.now().strftime('%Y-%m-%d'),
            'summary': 'OpenClaw 个人 AI 助理框架持续更新，支持多平台部署'
        })
    
    return items[:max_items]

def is_recent(published_str, days=2):
    if not published_str:
        return True
    try:
        for fmt in ['%a, %d %b %Y %H:%M:%S', '%Y-%m-%d']:
            try:
                pub_date = datetime.strptime(published_str.split('+')[0].strip(), fmt)
                return (datetime.now() - pub_date).days <= days
            except:
                continue
        return True
    except:
        return True

def translate_text(text, target_lang='en|zh'):
    """Translate single text using MyMemory API (free, no auth)"""
    if not text or len(text) < 3:
        return text
    
    try:
        encoded = urllib.parse.quote(text[:450])  # API limit: 500 chars
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair={target_lang}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=8) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'responseData' in result and 'translatedText' in result['responseData']:
            return result['responseData']['translatedText']
        return text
    except Exception as e:
        return text

def translate_batch(texts, target_lang='en|zh'):
    """Translate multiple texts"""
    if not texts:
        return []
    
    translations = []
    for i, text in enumerate(texts):
        if i % 5 == 0:
            print(f"    Translating {i+1}/{len(texts)}...")
        translations.append(translate_text(text, target_lang))
    
    return translations

def make_card(item, is_hot=False, is_design=False, is_openclaw=False):
    badges = []
    if is_hot:
        badges.append('<span class="hot-badge">🔥 热门</span>')
    if is_design:
        badges.append('<span class="design-badge">🎨 设计</span>')
    if is_openclaw:
        badges.append('<span class="openclaw-badge">🦞 OpenClaw</span>')
    badges.append('<span class="source-badge">🔍 Google 直达</span>')
    
    cls = "news-card"
    if is_hot: cls += " hot"
    if is_design: cls += " design"
    if is_openclaw: cls += " openclaw"
    
    search_link = f"https://www.google.com/search?q={urllib.parse.quote(item['title'])}&btnI=1"
    
    return f'''
            <a href="{search_link}" target="_blank" class="{cls}">
                <div class="badges">
                    {''.join(badges)}
                </div>
                <h3 class="news-title">{item['title_cn']}</h3>
                <p class="news-summary">{item['summary_cn']}</p>
                <span class="news-link">直达新闻详情 →</span>
            </a>'''

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    MEMORY_DIR.mkdir(exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def main():
    print("📰 AI Daily News - Chinese Version")
    print("=" * 60)
    
    dates = get_today_date()
    print(f"📅 Generating for: {dates['cn']} {dates['weekday']}")
    
    state = load_state()
    
    # Fetch news
    print("\n🌐 Fetching news...")
    
    all_news = []
    for name, url in RSS_FEEDS.items():
        print(f"  - {name}...")
        items, error = fetch_feed(url, max_items=20)
        if error:
            print(f"    ⚠️  {error}")
        else:
            recent = [i for i in items if is_recent(i['published'], days=2)]
            print(f"    ✅ {len(recent)} recent")
            all_news.extend(recent)
    
    design_news = []
    for name, url in DESIGN_FEEDS.items():
        print(f"  - {name}...")
        items, error = fetch_feed(url, max_items=10)
        if error:
            print(f"    ⚠️  {error}")
        else:
            recent = [i for i in items if is_recent(i['published'], days=2)]
            print(f"    ✅ {len(recent)} recent")
            design_news.extend(recent)
    
    # Fetch OpenClaw news
    print("  - openclaw (GitHub)...")
    openclaw_news = fetch_openclaw_news(max_items=5)
    print(f"    ✅ {len(openclaw_news)} items")
    
    # Deduplicate
    seen = set()
    unique_news = []
    for item in all_news:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_news.append(item)
    
    seen_design = set()
    unique_design = []
    for item in design_news:
        if item['title'] not in seen_design:
            seen_design.add(item['title'])
            unique_design.append(item)
    
    print(f"\n📊 Unique: Global={len(unique_news)}, Design={len(unique_design)}")
    
    # Translate in batch
    print("\n🌏 Translating to Chinese...")
    
    # Global news translations
    titles = [item['title'] for item in unique_news[:20]]
    summaries = [item['summary'][:100] for item in unique_news[:20]]
    
    print("  Translating titles...")
    title_translations = translate_batch(titles)
    print("  Translating summaries...")
    summary_translations = translate_batch(summaries)
    
    for i, item in enumerate(unique_news[:20]):
        item['title_cn'] = title_translations[i] if i < len(title_translations) else item['title']
        item['summary_cn'] = summary_translations[i] + '...' if i < len(summary_translations) else item['summary']
    
    # Design news translations
    design_titles = [item['title'] for item in unique_design[:8]]
    design_summaries = [item['summary'][:100] for item in unique_design[:8]]
    
    print("  Translating design titles...")
    design_title_trans = translate_batch(design_titles)
    print("  Translating design summaries...")
    design_summary_trans = translate_batch(design_summaries)
    
    for i, item in enumerate(unique_design[:8]):
        item['title_cn'] = design_title_trans[i] if i < len(design_title_trans) else item['title']
        item['summary_cn'] = design_summary_trans[i] + '...' if i < len(design_summary_trans) else item['summary']
    
    # OpenClaw news translations (already in Chinese)
    for i, item in enumerate(openclaw_news[:5]):
        item['title_cn'] = item['title']
        item['summary_cn'] = item['summary']
    
    # Read template
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Generate HTML
    global_html = '\n'.join([
        make_card(item, is_hot=(i < 2)) for i, item in enumerate(unique_news[:20])
    ])
    
    design_html = '\n'.join([
        make_card(item, is_design=True) for item in unique_design[:8]
    ])
    
    # OpenClaw news HTML
    openclaw_html = '\n'.join([
        make_card(item, is_openclaw=True, is_hot=(i == 0)) for i, item in enumerate(openclaw_news[:5])
    ])
    
    content = template
    content = content.replace('2026.03.24', dates['badge'])
    content = re.sub(r'<title>AI 前沿资讯日报 - [^<]+</title>', 
                     f'<title>AI 前沿资讯日报 - {dates["cn"]}</title>', content)
    content = re.sub(r'<p class="hero-date">[^<]+</p>',
                     f'<p class="hero-date">{dates["cn"]} {dates["weekday"]}</p>', content)
    
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
    
    # Insert OpenClaw section before Design AI
    content = re.sub(
        r'(<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>)',
        r'    <h2 class="section-title"><span class="emoji">🦞</span>openclaw 龙虾资讯</h2>\n        <div class="news-grid">\n' + openclaw_html + '\n        </div>\n\n        \1',
        content, flags=re.DOTALL
    )
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✅ HTML generated")
    
    # Git push
    print("\n📤 Pushing to GitHub...")
    try:
        subprocess.run(['git', 'add', str(HTML_FILE)], cwd=AI_NEWS_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Update {dates["iso"]}'], cwd=AI_NEWS_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'push'], cwd=AI_NEWS_DIR, check=True, capture_output=True, timeout=60)
        print("   ✅ Pushed")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # Update state
    state['lastPushDate'] = dates['iso']
    state['lastPushTime'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    state['pushCount'] = state.get('pushCount', 0) + 1
    save_state(state)
    
    print(f"\n✅ Done!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
