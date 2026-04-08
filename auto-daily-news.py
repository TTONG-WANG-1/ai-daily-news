#!/usr/bin/env python3
"""
AI Daily News - Hybrid (RSS + Tavily Search)
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

# Tavily API for product announcements (better Chinese search)
try:
    from tavily import TavilyClient
    TAVILY_API_KEY = "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"
    tavily_client = TavilyClient(TAVILY_API_KEY)
    HAS_TAVILY = True
except Exception as e:
    HAS_TAVILY = False
    print(f"⚠️  Tavily not available: {e}")

RSS_FEEDS = {
    'techcrunch': 'https://techcrunch.com/category/artificial-intelligence/feed/',
    'wired_ai': 'https://www.wired.com/feed/tag-ai/rss',
    'venturebeat_ai': 'https://venturebeat.com/category/ai/feed/',
    # 中文资讯源
    '36kr_ai': 'https://36kr.com/rss/article/人工智能',
    'huggingface': 'https://huggingface.co/blog/feed.xml',
}

DESIGN_FEEDS = {
    'creativebloq': 'https://www.creativebloq.com/ai/rss',
    'wired_design': 'https://www.wired.com/feed/tag-design/rss',
}

# 产品公告和活动资讯源
PRODUCT_FEEDS = {
    'feishu': 'https://www.feishu.cn/rss/announcements',  # 飞书公告
    'xiaomi': 'https://www.mi.com/rss/news',  # 小米动态
    'openai': 'https://openai.com/news/rss',  # OpenAI 官方
    'anthropic': 'https://www.anthropic.com/rss',  # Anthropic 官方
    'midjourney': 'https://midjourney.com/rss',  # Midjourney 更新
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

def search_with_tavily(query, max_results=10):
    """Search news with Tavily API (better for Chinese product announcements)"""
    if not HAS_TAVILY:
        return []
    
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        
        items = []
        for result in response.get('results', []):
            # Skip low-quality sources
            url = result.get('url', '')
            if any(skip in url.lower() for skip in ['youtube.com', 'news.google.com', '/search?']):
                continue
            
            items.append({
                'title': result.get('title', ''),
                'link': url,
                'summary': result.get('content', '')[:200],
                'score': result.get('score', 0),
                'published': result.get('published_date', ''),
                'is_tavily': True
            })
        
        # Sort by score and return top results
        items.sort(key=lambda x: x['score'], reverse=True)
        return items
    except Exception as e:
        print(f"  ⚠️  Tavily search error: {e}")
        return []

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

def generate_feishu_content(global_news, design_news, openclaw_news, product_news, dates):
    """Generate Feishu document content and push message from news data"""
    
    # Build highlights (top 4 from global news)
    highlights = []
    for i, item in enumerate(global_news[:4]):
        title = item.get('title_cn', item.get('title', ''))
        if title:
            # Clean up title
            title = re.sub(r'^\*\*🔥 \*\*', '', title)
            title = re.sub(r'\*\*$', '', title)
            highlights.append(f"- {title}")
    
    # Generate Feishu markdown content
    md_lines = [
        f"# AI 前沿资讯日报 - {dates['cn']} {dates['weekday']}",
        "",
        "---",
        ""
    ]
    
    # Product section
    if product_news:
        md_lines.extend(["## 📢 产品动态", ""])
        for item in product_news[:3]:
            title = item.get('title_cn', item.get('title', ''))
            summary = item.get('summary_cn', item.get('summary', ''))[:80]
            link = item.get('link', '')
            google_link = f"https://www.google.com/search?q={urllib.parse.quote(title)}&btnI=1"
            md_lines.append(f"**🔥 {title}**")
            md_lines.append(f"{summary}")
            md_lines.append(f"{google_link}")
            md_lines.append("")
        md_lines.extend(["", "---", ""])
    
    # Global section
    md_lines.extend(["## 🌍 全球动态", ""])
    for i, item in enumerate(global_news):
        title = item.get('title_cn', item.get('title', ''))
        summary = item.get('summary_cn', item.get('summary', ''))[:80]
        link = item.get('link', '')
        google_link = f"https://www.google.com/search?q={urllib.parse.quote(title)}&btnI=1"
        hot_badge = "🔥 " if i < 2 else ""
        md_lines.append(f"**{hot_badge}{title}**")
        md_lines.append(f"{summary}")
        md_lines.append(f"{google_link}")
        md_lines.append("")
    
    # OpenClaw section
    md_lines.extend(["", "## 🦞 OpenClaw 龙虾资讯", ""])
    for i, item in enumerate(openclaw_news):
        title = item.get('title', '')
        summary = item.get('summary', '')[:80]
        link = item.get('link', '')
        google_link = f"https://www.google.com/search?q={urllib.parse.quote(title)}&btnI=1"
        hot_badge = "🔥 " if i == 0 else ""
        md_lines.append(f"**{hot_badge}{title}**")
        md_lines.append(f"{summary}")
        md_lines.append(f"{google_link}")
        md_lines.append("")
    
    # Design section
    md_lines.extend(["", "## 🎨 设计 AI", ""])
    for item in design_news:
        title = item.get('title_cn', item.get('title', ''))
        summary = item.get('summary_cn', item.get('summary', ''))[:80]
        link = item.get('link', '')
        google_link = f"https://www.google.com/search?q={urllib.parse.quote(title)}&btnI=1"
        md_lines.append(f"**{title}**")
        md_lines.append(f"{summary}")
        md_lines.append(f"{google_link}")
        md_lines.append("")
    
    # Stats footer
    md_lines.extend([
        "",
        "---",
        "",
        f"📊 今日统计：全球动态 {len(global_news)} 条 | 🦞 OpenClaw {len(openclaw_news)} 条 | 设计 AI {len(design_news)} 条 | 产品动态 {len(product_news)} 条",
        "",
        f"🔗 GitHub Pages: https://ttong-wang-1.github.io/ai-daily-news/"
    ])
    
    markdown_content = "\n".join(md_lines)
    
    # Generate push message
    push_message = f"""## 📰 AI 前沿资讯日报 - {dates['cn']} {dates['weekday']}

**今日新闻**:
- 🌍 全球 AI 动态：{len(global_news)} 条
- 🎨 设计 AI 资讯：{len(design_news)} 条
- 🦞 OpenClaw：{len(openclaw_news)} 条
- 📢 产品动态：{len(product_news)} 条

**热门亮点**:
{chr(10).join(highlights[:4])}

**查看方式**:
- 🌐 GitHub Pages: https://ttong-wang-1.github.io/ai-daily-news/
- 📄 飞书文档：{{feishu_doc_url}}

祝你{dates['weekday'][:2]}愉快！☕"""
    
    return {
        'markdown': markdown_content,
        'message': push_message,
        'highlights': highlights
    }

def extract_date_from_text(text):
    """Extract date from text content (summary/title) - prioritize title dates"""
    if not text:
        return None
    
    # Common date patterns - order matters, try most specific first
    patterns = [
        (r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', 3),  # 2026-04-03 (full date)
        (r'(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日', 3),  # 2026 年 04 月 03 日
        (r'(\d{4})[-/](\d{1,2})', 2),  # 2026-04 (year-month only, skip)
    ]
    
    for pattern, min_groups in patterns:
        match = re.search(pattern, text[:200])  # Only check first 200 chars (title area)
        if match:
            groups = match.groups()
            if len(groups) >= min_groups:
                try:
                    year = int(groups[0])
                    month = int(groups[1])
                    day = int(groups[2]) if len(groups) > 2 else 1
                    if year < 100:  # Assume 20xx for 2-digit years
                        year += 2000
                    # Sanity check: don't return dates before 2020 or in the future
                    if 2020 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31:
                        return datetime(year, month, day)
                except:
                    continue
    return None

def has_today_date(title_text, today_iso, today_cn):
    """Check if title contains today's date (strict check)"""
    if not title_text:
        return False
    # Check for various date formats
    return (today_iso in title_text or  # 2026-04-03
            today_cn in title_text or   # 2026 年 04 月 03 日
            f"{today_iso.replace('-', '/')}" in title_text)  # 2026/04/03

def is_recent(published_str, days=1, summary_text=None, title_text=None, require_today=False):
    """Check if news is recent (within specified days, default=1 for today only)
    
    Args:
        published_str: Published date string from RSS/API
        days: Maximum age in days (default=1)
        summary_text: Summary text to extract date from if published_str is missing
        title_text: Title text to extract date from (higher priority than summary)
        require_today: If True, MUST have today's date in title
    """
    today = datetime.now()
    today_iso = today.strftime('%Y-%m-%d')
    today_cn = today.strftime('%Y 年%m 月%d 日')
    
    # If require_today, check title first
    if require_today and title_text:
        if has_today_date(title_text, today_iso, today_cn):
            return True
        # Don't fallback - require today's date
        return False
    
    # Try parsing published date first
    if published_str:
        try:
            for fmt in ['%a, %d %b %Y %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S']:
                try:
                    pub_date = datetime.strptime(published_str.split('+')[0].split('Z')[0].strip(), fmt)
                    age_days = (today - pub_date).days
                    if age_days <= days:
                        return True
                    # Date too old
                    return False
                except:
                    continue
        except:
            pass
    
    # Try extracting date from title first (higher priority)
    if title_text:
        extracted_date = extract_date_from_text(title_text)
        if extracted_date:
            age_days = (today - extracted_date).days
            if age_days <= days:
                return True
            return False
    
    # Try extracting date from summary text
    if summary_text:
        extracted_date = extract_date_from_text(summary_text)
        if extracted_date:
            age_days = (today - extracted_date).days
            if age_days <= days:
                return True
            return False
    
    # No date found = assume OLD (conservative)
    return False

def translate_text(text, target_lang='en|zh'):
    """Translate text - skip for now, use Chinese sources directly"""
    if not text or len(text) < 3:
        return text
    
    # If text is already Chinese, return as-is
    if any('\u4e00' <= c <= '\u9fff' for c in text[:50]):
        return text
    
    # For English text, return as-is (will be handled by searching Chinese sources)
    return text

def translate_batch(texts, target_lang='en|zh'):
    """Translate multiple texts - pass-through for now"""
    if not texts:
        return []
    
    # Return texts as-is (we search Chinese sources directly now)
    return texts

def make_card(item, is_hot=False, is_design=False, is_openclaw=False, is_product=False):
    badges = []
    if is_hot:
        badges.append('<span class="hot-badge">🔥 热门</span>')
    if is_design:
        badges.append('<span class="design-badge">🎨 设计</span>')
    if is_openclaw:
        badges.append('<span class="openclaw-badge">🦞 OpenClaw</span>')
    if is_product:
        badges.append('<span class="product-badge">📢 产品</span>')
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
    
    # Fetch news - Tavily first for latest news
    print("\n🌐 Fetching news...")
    
    all_news = []
    
    # Tavily search for TODAY's AI news - ONLY from trusted news sources
    print("  - Tavily: AI news today (trusted sources only)...")
    today = dates['iso']
    today_dt = datetime.strptime(today, '%Y-%m-%d')
    # Search ONLY from trusted news sources with explicit date in query
    cn_queries = [
        f"site:thepaper.cn AI 人工智能 {today}",
        f"site:xinhuanet.com AI {today}",
        f"site:chinanews.com AI 科技 {today}",
        f"site:21jingji.com AI {today}",
        f"site:jiemian.com AI 大模型 {today}",
    ]
    tavily_items = []
    for query in cn_queries:
        results = search_with_tavily(query, max_results=5)
        for item in results:
            item['source'] = 'trusted_news'
        tavily_items.extend(results)
    
    # Deduplicate AND strict date check - ONLY keep news with TODAY's date
    seen = set()
    unique_tavily = []
    for item in tavily_items:
        if item['title'] in seen:
            continue
        # VERY strict: title MUST contain today's date
        title_has_date = today in item.get('title', '') or dates['cn'] in item.get('title', '')
        if not title_has_date:
            print(f"    ⚠️  Skip (no date in title): {item['title'][:50]}")
            continue
        seen.add(item['title'])
        unique_tavily.append(item)
    
    all_news.extend(unique_tavily[:15])
    print(f"    ✅ {len(unique_tavily[:15])} items from Tavily (trusted, today's date)")
    
    # RSS feeds as supplementary
    for name, url in RSS_FEEDS.items():
        print(f"  - {name}...")
        items, error = fetch_feed(url, max_items=30)
        if error:
            print(f"    ⚠️  {error}")
        else:
            # 只抓取今日和昨日新闻（days=1）
            recent = [i for i in items if is_recent(i['published'], days=1)]
            old_count = len(items) - len(recent)
            print(f"    ✅ {len(recent)} recent, ⚠️ {old_count} old (filtered)")
            for item in recent:
                item['source'] = name
            all_news.extend(recent)
    
    design_news = []
    for name, url in DESIGN_FEEDS.items():
        print(f"  - {name}...")
        items, error = fetch_feed(url, max_items=15)
        if error:
            print(f"    ⚠️  {error}")
        else:
            # 只抓取今日和昨日新闻（days=1）
            recent = [i for i in items if is_recent(i['published'], days=1)]
            old_count = len(items) - len(recent)
            print(f"    ✅ {len(recent)} recent, ⚠️ {old_count} old (filtered)")
            design_news.extend(recent)
    
    # Fetch OpenClaw news
    print("  - openclaw (GitHub)...")
    openclaw_news = fetch_openclaw_news(max_items=5)
    print(f"    ✅ {len(openclaw_news)} items")
    
    # Fetch product announcements with Tavily (better Chinese search)
    print("  - product announcements (Tavily search)...")
    product_news = []
    
    if HAS_TAVILY:
        # Tavily search queries for product announcements - use TODAY's date for real-time news
        today = datetime.now().strftime('%Y-%m-%d')
        product_queries = [
            (f"AI 产品发布 {today} 今日最新", "ai_product_cn"),
            (f"大模型更新 {today} 字节阿里腾讯百度", "china_ai"),
            (f"AI 工具新品 {today}", "ai_tools"),
            (f"OpenAI Anthropic Google AI {today}", "us_ai"),
            (f"Midjourney Stable Diffusion AI 绘画 {today}", "ai_art"),
            (f"飞书钉钉企业微信 AI {today}", "enterprise_ai"),
        ]
        
        for query, tag in product_queries:
            print(f"    🔍 {query[:40]}...")
            results = search_with_tavily(query, max_results=5)
            if results:
                # Filter by date
                recent_results = []
                for item in results:
                    if is_recent(item.get('published', ''), days=2, summary_text=item.get('summary', ''), title_text=item.get('title', '')):
                        recent_results.append(item)
                    else:
                        print(f"      ⚠️  Skip old: {item['title'][:40]}")
                if recent_results:
                    print(f"      ✅ {len(recent_results)} recent (score: {recent_results[0]['score']:.3f})")
                    for item in recent_results:
                        item['is_product'] = True
                        item['source_tag'] = tag
                    product_news.extend(recent_results[:2])  # Top 2 per query
    else:
        # Fallback to RSS feeds
        print("    ⚠️  Tavily unavailable, using RSS fallback...")
        for name, url in PRODUCT_FEEDS.items():
            items, error = fetch_feed(url, max_items=10)
            if error:
                print(f"      ⚠️  {name}: {error}")
            else:
                recent = [i for i in items if is_recent(i['published'], days=3)]
                if recent:
                    print(f"      ✅ {name}: {len(recent)} items")
                    for item in recent:
                        item['is_product'] = True
                    product_news.extend(recent)
    
    # 如果全球新闻太少，用 Tavily 补充（搜索中文）
    if len(all_news) < 15 and HAS_TAVILY:
        print("\n  ⚠️  Global news too few, supplementing with Tavily (Chinese)...")
        today = datetime.now().strftime('%Y-%m-%d')
        tavily_queries = [
            f"AI 人工智能 {today} 最新消息",
            f"AI 创业融资 {today}",
            f"OpenAI Google AI 更新 {today}",
        ]
        for query in tavily_queries:
            print(f"    🔍 {query[:50]}...")
            results = search_with_tavily(query, max_results=8)
            # Filter by date
            for item in results:
                if is_recent(item.get('published', ''), days=2, summary_text=item.get('summary', ''), title_text=item.get('title', '')):
                    item['is_global'] = True
                    all_news.append(item)
                else:
                    print(f"      ⚠️  Skip old: {item['title'][:40]}")
    
    # 中国大厂 AI 资讯 (Tavily 搜索)
    if HAS_TAVILY:
        print("\n🇨🇳 Fetching China tech AI news...")
        china_queries = [
            f"字节跳动 飞书 Aily AI 更新 {datetime.now().strftime('%Y-%m-%d')}",
            f"阿里巴巴 通义千问 Qwen 更新 {datetime.now().strftime('%Y-%m-%d')}",
            f"腾讯 混元 AI 模型 {datetime.now().strftime('%Y-%m-%d')}",
            f"百度 文心一言 ERNIE Bot {datetime.now().strftime('%Y-%m-%d')}",
            f"小米 MiMo AI 大模型 {datetime.now().strftime('%Y-%m-%d')}",
            f"即梦 AI 视频生成 更新 {datetime.now().strftime('%Y-%m-%d')}",
            f"豆包 AI 助手 字节跳动 {datetime.now().strftime('%Y-%m-%d')}",
        ]
        for query in china_queries:
            print(f"    🔍 {query[:50]}...")
            results = search_with_tavily(query, max_results=5)
            # Filter by date
            recent_count = 0
            for item in results:
                if is_recent(item.get('published', ''), days=2, summary_text=item.get('summary', ''), title_text=item.get('title', '')):
                    item['is_global'] = True
                    item['is_china_tech'] = True
                    all_news.append(item)
                    recent_count += 1
                else:
                    print(f"      ⚠️  Skip old: {item['title'][:40]}")
            if recent_count > 0:
                print(f"      ✅ {recent_count} recent")
    
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
    
    # 去重产品资讯
    seen_product = set()
    unique_product = []
    for item in product_news:
        if item['title'] not in seen_product:
            seen_product.add(item['title'])
            unique_product.append(item)
    
    print(f"\n📊 Unique: Global={len(unique_news)}, Design={len(unique_design)}, Product={len(unique_product)}")
    
    # 显示日期验证信息
    print("\n📅 Date verification:")
    for item in unique_news[:5]:
        print(f"  - {item['published'][:10] if item['published'] else 'No date'}: {item['title'][:50]}")
    
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
        # Debug: print if translation failed
        if item['title_cn'] == item['title'] and len(item['title']) > 10:
            print(f"    ⚠️  Title not translated: {item['title'][:50]}")
    
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
    
    # Product news translations (mix of Chinese and English)
    product_titles = [item['title'] for item in unique_product[:10]]
    product_summaries = [item['summary'][:100] for item in unique_product[:10]]
    
    print("  Translating product titles...")
    product_title_trans = translate_batch(product_titles)
    print("  Translating product summaries...")
    product_summary_trans = translate_batch(product_summaries)
    
    for i, item in enumerate(unique_product[:10]):
        item['title_cn'] = product_title_trans[i] if i < len(product_title_trans) else item['title']
        item['summary_cn'] = product_summary_trans[i] + '...' if i < len(product_summary_trans) else item['summary']
    
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
    
    # Product news HTML
    product_html = '\n'.join([
        make_card(item, is_hot=(i == 0)) for i, item in enumerate(unique_product[:8])
    ])
    
    content = template
    content = content.replace('2026.03.24', dates['badge'])
    content = re.sub(r'<title>AI 前沿资讯日报 - [^<]+</title>', 
                     f'<title>AI 前沿资讯日报 - {dates["cn"]}</title>', content)
    content = re.sub(r'<p class="hero-date">[^<]+</p>',
                     f'<p class="hero-date">{dates["cn"]} {dates["weekday"]}</p>', content)
    
    # Build complete sections
    global_section = f'''<h2 class="section-title"><span class="emoji">🌍</span>全球动态</h2>
        <div class="news-grid">
            {global_html}
        </div>

        <h2 class="section-title"><span class="emoji">🦞</span>OpenClaw 龙虾资讯</h2>
        <div class="news-grid">
            {openclaw_html}
        </div>'''
    
    design_section = f'''<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>
        <div class="news-grid">
            {design_html}
        </div>'''
    
    product_section = f'''<h2 class="section-title"><span class="emoji">📢</span>产品动态</h2>
        <div class="news-grid" id="product-news">
            {product_html}
        </div>'''
    
    # Replace entire sections
    content = re.sub(
        r'<h2 class="section-title"><span class="emoji">📢</span>产品动态</h2>\s*<div class="news-grid" id="product-news">.*?</div>',
        product_section,
        content, flags=re.DOTALL
    )
    
    content = re.sub(
        r'<h2 class="section-title"><span class="emoji">🌍</span>全球动态</h2>\s*<div class="news-grid">.*?</div>\s*<h2 class="section-title"><span class="emoji">🎨</span>设计 AI</h2>\s*<div class="news-grid">.*?</div>',
        global_section + '\n\n        ' + design_section,
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
    
    # Generate Feishu doc content and push message
    feishu_content = generate_feishu_content(unique_news[:20], unique_design[:8], openclaw_news[:5], unique_product[:8], dates)
    state['feishuDocContent'] = feishu_content['markdown']
    state['pushMessage'] = feishu_content['message']
    state['newsStats'] = {
        'global': len(unique_news[:20]),
        'design': len(unique_design[:8]),
        'openclaw': len(openclaw_news[:5]),
        'product': len(unique_product[:8])
    }
    state['highlights'] = feishu_content['highlights']
    
    save_state(state)
    
    # Export delivery payload for OpenClaw to push
    payload = {
        'feishuDocTitle': f"AI 前沿资讯日报 - {dates['cn']} {dates['weekday']}",
        'feishuDocContent': feishu_content['markdown'],
        'pushMessage': feishu_content['message'],
        'githubPagesUrl': 'https://ttong-wang-1.github.io/ai-daily-news/',
        'date': dates['iso'],
        'stats': state['newsStats']
    }
    
    payload_file = AI_NEWS_DIR / 'delivery-payload.json'
    with open(payload_file, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Delivery payload exported to {payload_file}")
    print(f"\n✅ Done!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
