#!/usr/bin/env python3
"""
Fetch real AI news from RSS feeds
"""

import feedparser
import json
from datetime import datetime, timedelta
from pathlib import Path

# RSS feeds that are more reliable
RSS_FEEDS = {
    'venturebeat': 'https://venturebeat.com/category/ai/feed/',
    'techcrunch': 'https://techcrunch.com/category/artificial-intelligence/feed/',
}

DESIGN_FEEDS = {
    'creativebloq': 'https://www.creativebloq.com/ai/rss',
}

def fetch_feed(url, max_items=10):
    """Fetch items from RSS feed"""
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

def is_recent(published_str, days=2):
    """Check if date is within last N days"""
    if not published_str:
        return True  # No date, assume recent
    try:
        # Try common date formats
        for fmt in ['%a, %d %b %Y %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y']:
            try:
                pub_date = datetime.strptime(published_str.split('+')[0].strip(), fmt)
                return (datetime.now() - pub_date).days <= days
            except:
                continue
        return True
    except:
        return True

def main():
    print("📰 Fetching AI News from RSS Feeds")
    print("=" * 50)
    
    all_news = []
    design_news = []
    
    # Fetch global AI news
    print("\n🌍 Global AI News:")
    for name, url in RSS_FEEDS.items():
        print(f"  Fetching {name}...")
        items, error = fetch_feed(url, max_items=15)
        if error:
            print(f"    ⚠️  Error: {error}")
        else:
            recent_items = [i for i in items if is_recent(i['published'], days=2)]
            print(f"    ✅ {len(recent_items)} recent items")
            all_news.extend(recent_items)
    
    # Fetch design AI news
    print("\n🎨 Design AI News:")
    for name, url in DESIGN_FEEDS.items():
        print(f"  Fetching {name}...")
        items, error = fetch_feed(url, max_items=10)
        if error:
            print(f"    ⚠️  Error: {error}")
        else:
            recent_items = [i for i in items if is_recent(i['published'], days=2)]
            print(f"    ✅ {len(recent_items)} recent items")
            design_news.extend(recent_items)
    
    # Deduplicate by title
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
    
    print(f"\n📊 Results:")
    print(f"   Global AI: {len(unique_news)} unique items")
    print(f"   Design AI: {len(unique_design)} unique items")
    
    # Save to file
    output = {
        'fetched_at': datetime.now().isoformat(),
        'global_news': unique_news[:20],
        'design_news': unique_design[:8]
    }
    
    output_file = Path('/home/wangtong/openclaw/workspace/ai-daily-news/fetched-news.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to: {output_file}")
    
    # Print sample
    print("\n📋 Sample headlines:")
    for i, item in enumerate(unique_news[:5], 1):
        print(f"   {i}. {item['title']}")

if __name__ == '__main__':
    main()
