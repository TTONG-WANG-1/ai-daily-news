#!/usr/bin/env python3
"""
AI Daily News - 包含中国大厂 AI 资讯监控
每日自动执行，收集全球 + 中国 AI 动态
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
MD_FILE = AI_NEWS_DIR / '2026-04-02.md'  # Will be dynamic

# Tavily API
try:
    from tavily import TavilyClient
    TAVILY_API_KEY = "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"
    tavily_client = TavilyClient(TAVILY_API_KEY)
    HAS_TAVILY = True
except Exception as e:
    HAS_TAVILY = False
    print(f"⚠️  Tavily not available: {e}")

# RSS 资讯源
RSS_FEEDS = {
    'techcrunch': 'https://techcrunch.com/category/artificial-intelligence/feed/',
    'wired_ai': 'https://www.wired.com/feed/tag-ai/rss',
    'venturebeat_ai': 'https://venturebeat.com/category/ai/feed/',
    '36kr_ai': 'https://36kr.com/rss/article/人工智能',
    'huggingface': 'https://huggingface.co/blog/feed.xml',
}

DESIGN_FEEDS = {
    'creativebloq': 'https://www.creativebloq.com/ai/rss',
    'wired_design': 'https://www.wired.com/feed/tag-design/rss',
}

# 🇨🇳 中国大厂 AI 监控关键词
CHINA_TECH_QUERIES = [
    "字节跳动 飞书 Aily AI 智能助手",
    "阿里巴巴 通义千问 Qwen 大模型",
    "腾讯 混元 AI 模型 微信",
    "百度 文心一言 ERNIE Bot",
    "小米 MiMo AI 大模型 Agent",
    "即梦 AI 视频生成 字节跳动",
    "豆包 AI 助手 字节跳动",
    "阿里云 AI 通义",
    "钉钉 AI 助理",
    "华为 盘古大模型",
]

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
    """Search with Tavily API"""
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
            url = result.get('url', '')
            # Skip low-quality sources
            if any(skip in url.lower() for skip in ['youtube.com', 'news.google.com', '/search?']):
                continue
            
            items.append({
                'title': result.get('title', ''),
                'link': url,
                'summary': result.get('content', '')[:200],
                'score': result.get('score', 0),
                'published': result.get('published_date', ''),
            })
        
        items.sort(key=lambda x: x['score'], reverse=True)
        return items
    except Exception as e:
        print(f"  ⚠️  Tavily error: {e}")
        return []

def fetch_china_tech_news():
    """Fetch China tech AI news via Tavily"""
    print("\n🇨🇳 中国大厂 AI 资讯...")
    all_items = []
    
    for query in CHINA_TECH_QUERIES:
        print(f"    🔍 {query[:30]}...")
        results = search_with_tavily(query, max_results=5)
        if results:
            print(f"      ✅ {len(results)} results")
            for item in results[:2]:  # Top 2 per query
                item['is_china'] = True
                all_items.append(item)
    
    # Deduplicate
    seen = set()
    unique = []
    for item in all_items:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique.append(item)
    
    print(f"  📊 Unique: {len(unique)} items")
    return unique[:10]  # Max 10 China tech news

def translate_text(text, target_lang='en|zh'):
    """Translate using MyMemory API"""
    if not text or len(text) < 3:
        return text
    
    try:
        encoded = urllib.parse.quote(text[:450])
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair={target_lang}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=8) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'responseData' in result and 'translatedText' in result['responseData']:
            return result['responseData']['translatedText']
        return text
    except Exception:
        return text

def format_google_search_link(title):
    """Generate Google Search link with btnI"""
    return f"https://www.google.com/search?q={urllib.parse.quote(title)}&btnI=1"

def generate_md_content(global_news, china_news, design_news, openclaw_news, dates):
    """Generate markdown content"""
    
    md = f"# AI 前沿资讯日报 | {dates['cn'].replace('年', '-').replace('月', '-').replace('日', '')}\n\n"
    md += f"> 📅 日期：{dates['cn']}（{dates['weekday']}）\n"
    md += f"> 🌍 覆盖范围：全球 AI 动态 + 中国大厂 + 设计 AI 专项\n"
    md += f"> 🔗 所有链接均为 Google 智能直达，点击即可跳转原文\n\n"
    md += "---\n\n"
    
    # Global AI News
    md += f"## 🔥 全球 AI 动态（{len(global_news)} 条）\n\n"
    for i, item in enumerate(global_news[:20], 1):
        is_hot = "🔥 " if i <= 5 else ""
        md += f"### {i}. {is_hot}{item.get('title_cn', item['title'])}\n"
        md += f"**来源：** {item.get('source', 'AI News')} | **日期：** {item.get('date', 'N/A')}\n"
        md += f"[🔗 Google 智能直达]({format_google_search_link(item['title'])})\n\n"
        md += f"{item.get('summary_cn', item.get('summary', 'N/A')[:150])}...\n\n"
        md += "---\n\n"
    
    # China Tech News
    if china_news:
        md += f"## 🇨🇳 中国大厂 AI（{len(china_news)} 条）\n\n"
        for i, item in enumerate(china_news[:10], 1):
            md += f"### {i}. {item.get('title_cn', item['title'])}\n"
            md += f"**来源：** 中国科技媒体 | **日期：** {item.get('date', 'N/A')}\n"
            md += f"[🔗 Google 智能直达]({format_google_search_link(item['title'])})\n\n"
            md += f"{item.get('summary_cn', item.get('summary', 'N/A')[:150])}...\n\n"
            md += "---\n\n"
    
    # Design AI News
    md += f"## 🎨 设计 AI 资讯（{len(design_news)} 条）\n\n"
    for i, item in enumerate(design_news[:8], 1):
        md += f"### {i}. 🎨 {item.get('title_cn', item['title'])}\n"
        md += f"**来源：** 设计媒体 | **日期：** {item.get('date', 'N/A')}\n"
        md += f"[🔗 Google 智能直达]({format_google_search_link(item['title'])})\n\n"
        md += f"{item.get('summary_cn', item.get('summary', 'N/A')[:150])}...\n\n"
        md += "---\n\n"
    
    # OpenClaw News
    md += f"## 🦞 OpenClaw 龙虾资讯（{len(openclaw_news)} 条）\n\n"
    for i, item in enumerate(openclaw_news[:5], 1):
        md += f"### {i}. 🦞 {item['title']}\n"
        md += f"[🔗 Google 智能直达]({format_google_search_link(item['title'])})\n\n"
        md += f"{item['summary'][:150]}...\n\n"
        md += "---\n\n"
    
    # Summary
    md += f"## 📊 今日数据摘要\n\n"
    md += f"| 类别 | 数量 |\n"
    md += f"|------|------|\n"
    md += f"| 全球 AI 动态 | {len(global_news)} 条 |\n"
    if china_news:
        md += f"| 中国大厂 AI | {len(china_news)} 条 |\n"
    md += f"| 设计 AI 资讯 | {len(design_news)} 条 |\n"
    md += f"| OpenClaw | {len(openclaw_news)} 条 |\n"
    md += f"| **总计** | **{len(global_news) + len(china_news) + len(design_news) + len(openclaw_news)}** 条 |\n\n"
    
    return md

def main():
    dates = get_today_date()
    print(f"📰 AI Daily News - 中国大厂监控版")
    print("=" * 60)
    print(f"📅 生成日期：{dates['cn']} {dates['weekday']}")
    
    # Fetch China tech news
    china_news = fetch_china_tech_news()
    
    # Translate
    print("\n🌏 翻译中...")
    for i, item in enumerate(china_news[:10]):
        if any('\u4e00' <= c <= '\u9fff' for c in item['title']):
            item['title_cn'] = item['title']
            item['summary_cn'] = item['summary']
        else:
            item['title_cn'] = translate_text(item['title'])
            item['summary_cn'] = translate_text(item['summary'][:100])
    
    # Placeholder for other news (would be fetched from RSS)
    global_news = []
    design_news = []
    openclaw_news = [
        {'title': 'OpenClaw v2026.4.1', 'summary': '新增/tasks 命令'},
        {'title': 'OpenClaw v2026.4.1-beta.1', 'summary': '任务板测试版'},
    ]
    
    # Generate markdown
    md_content = generate_md_content(global_news[:20], china_news[:10], design_news[:8], openclaw_news, dates)
    
    # Write MD file
    md_filename = f"2026-04-02.md"
    md_path = AI_NEWS_DIR / md_filename
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✅ Markdown 已生成：{md_filename}")
    print(f"   全球动态：{len(global_news)} 条")
    print(f"   中国大厂：{len(china_news)} 条")
    print(f"   设计 AI: {len(design_news)} 条")
    print(f"   OpenClaw: {len(openclaw_news)} 条")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
