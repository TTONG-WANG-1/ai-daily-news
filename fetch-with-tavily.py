#!/usr/bin/env python3
"""
AI Daily News - Fetch with Tavily Search API
"""

from tavily import TavilyClient
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/home/wangtong/openclaw/workspace')
AI_NEWS_DIR = WORKSPACE / 'ai-daily-news'
MEMORY_DIR = WORKSPACE / 'memory'

TAVILY_API_KEY = "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"
client = TavilyClient(TAVILY_API_KEY)

def get_today_date():
    now = datetime.now()
    return {
        'iso': now.strftime('%Y-%m-%d'),
        'yesterday': (now.replace(day=now.day-1) if now.day > 1 else now.replace(month=now.month-1, day=28)).strftime('%Y-%m-%d'),
    }

def search_news(query, max_results=20):
    """Search news with Tavily"""
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        
        items = []
        for result in response.get('results', []):
            items.append({
                'title': result.get('title', ''),
                'link': result.get('url', ''),
                'summary': result.get('content', '')[:200],
                'score': result.get('score', 0),
                'published': result.get('published_date', '')
            })
        
        # 按分数排序
        items.sort(key=lambda x: x['score'], reverse=True)
        return items
    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
        return []

def main():
    print("🔍 AI Daily News - Tavily Search")
    print("=" * 60)
    
    dates = get_today_date()
    print(f"📅 Searching for: {dates['iso']} and {dates['yesterday']}")
    
    # 搜索全球 AI 新闻
    print("\n🌍 Searching global AI news...")
    global_queries = [
        f"AI news {dates['iso']} artificial intelligence",
        f"AI startup funding {dates['iso']}",
        f"OpenAI Anthropic Google AI news {dates['iso']}",
        f"AI model release {dates['iso']}",
    ]
    
    all_global = []
    for query in global_queries:
        print(f"  - {query[:50]}...")
        results = search_news(query, max_results=10)
        all_global.extend(results)
    
    # 去重
    seen = set()
    unique_global = []
    for item in all_global:
        if item['link'] not in seen:
            seen.add(item['link'])
            unique_global.append(item)
    
    print(f"  ✅ Found {len(unique_global)} unique global news")
    
    # 搜索产品动态
    print("\n📢 Searching product announcements...")
    product_queries = [
        "飞书 Aily 预约 2026",
        "Xiaomi MiMo Agent framework 2026",
        "OpenAI new feature 2026",
        "Anthropic Claude update 2026",
    ]
    
    all_product = []
    for query in product_queries:
        print(f"  - {query[:50]}...")
        results = search_news(query, max_results=5)
        all_product.extend(results)
    
    # 去重
    seen_product = set()
    unique_product = []
    for item in all_product:
        if item['link'] not in seen_product:
            seen_product.add(item['link'])
            unique_product.append(item)
    
    print(f"  ✅ Found {len(unique_product)} unique product news")
    
    # 保存结果
    fetched_data = {
        'fetched_at': datetime.now().isoformat(),
        'global_news': unique_global[:20],
        'product_news': unique_product[:10],
    }
    
    output_file = AI_NEWS_DIR / 'fetched-news-tavily.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fetched_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to {output_file}")
    
    # 显示示例
    print("\n📊 Sample results:")
    print("\n--- Global News (Top 5) ---")
    for i, item in enumerate(unique_global[:5], 1):
        print(f"{i}. {item['title'][:60]}")
        print(f"   Score: {item['score']:.4f} | Date: {item['published'] or 'N/A'}")
    
    print("\n--- Product News (Top 5) ---")
    for i, item in enumerate(unique_product[:5], 1):
        print(f"{i}. {item['title'][:60]}")
        print(f"   Score: {item['score']:.4f} | Date: {item['published'] or 'N/A'}")
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
