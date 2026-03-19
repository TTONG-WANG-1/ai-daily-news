#!/usr/bin/env python3
"""
AI Daily News Content Validator
Checks that all sections have fresh, up-to-date content
Run before daily push to catch errors
"""

import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path('/home/wangtong/openclaw/workspace')
AI_NEWS_DIR = WORKSPACE / 'ai-daily-news'
STATE_FILE = WORKSPACE / 'memory' / 'ai-daily-news-state.json'


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_check(name, passed, details=None):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if details:
        color = Colors.GREEN if passed else Colors.RED
        print(f"       {color}{details}{Colors.END}")


def get_today_date():
    now = datetime.now()
    return {
        'iso': now.strftime('%Y-%m-%d'),
        'badge': now.strftime('%Y.%m.%d'),
        'cn': now.strftime('%Y 年 %m 月 %d 日'),
        'year': now.strftime('%Y'),
    }


def validate_html_file():
    """Validate the main HTML file"""
    print_header("📄 HTML 文件检查")
    
    html_file = AI_NEWS_DIR / 'index.html'
    if not html_file.exists():
        print_check("HTML 文件存在", False, f"文件不存在：{html_file}")
        return False, None
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    dates = get_today_date()
    all_passed = True
    
    # Check 1: Date in title
    has_date = dates['cn'] in content or dates['iso'] in content
    print_check("网页标题包含今日日期", has_date, f"期望：{dates['cn']} 或 {dates['iso']}")
    all_passed = all_passed and has_date
    
    # Check 2: No placeholder content
    has_placeholder = '⚠️ 请使用 Python 脚本' in content or 'DATE_PLACEHOLDER' in content
    print_check("无占位符内容", not has_placeholder, "发现占位符！" if has_placeholder else "无占位符")
    all_passed = all_passed and not has_placeholder
    
    # Check 3: Count news items
    global_news_count = len(re.findall(r'<div class="section-icon">🌍</div>', content))
    design_news_count = len(re.findall(r'<div class="section-icon">🎨</div>', content))
    
    # Better counting
    news_cards = re.findall(r'class="news-card([^"]*)"', content)
    global_cards = len([c for c in news_cards if 'design' not in c])
    design_cards = len([c for c in news_cards if 'design' in c])
    
    print_check("全球动态新闻数量 (目标 20)", global_cards >= 15, f"实际：{global_cards} 条")
    all_passed = all_passed and (global_cards >= 15)
    
    print_check("设计 AI 新闻数量 (目标 8)", design_cards >= 5, f"实际：{design_cards} 条")
    all_passed = all_passed and (design_cards >= 5)
    
    # Check 4: Google Search links
    google_links = re.findall(r'href="https://www\.google\.com/search\?q=[^"]+&btnI=1"', content)
    print_check("Google 搜索链接格式正确", len(google_links) >= 15, f"实际：{len(google_links)} 个正确格式的链接")
    all_passed = all_passed and (len(google_links) >= 15)
    
    # Check 5: Hot badges
    hot_badges = len(re.findall(r'🔥 热门', content))
    print_check("热门新闻标记", 5 <= hot_badges <= 15, f"实际：{hot_badges} 个热门标记 (建议 5-15 个)")
    
    return all_passed, content


def validate_state_file():
    """Validate state file"""
    print_header("📊 状态文件检查")
    
    if not STATE_FILE.exists():
        print_check("状态文件存在", False, f"文件不存在：{STATE_FILE}")
        return False
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    dates = get_today_date()
    all_passed = True
    
    # Check last push date
    last_date = state.get('lastPushDate')
    if last_date:
        is_recent = last_date >= (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        print_check("最后推送日期", is_recent, f"最后推送：{last_date}")
        all_passed = all_passed and is_recent
    else:
        print_check("最后推送日期", False, "未设置")
        all_passed = False
    
    # Check required fields
    required_fields = ['lastPushDocId', 'pushCount', 'recipient', 'links']
    for field in required_fields:
        has_field = field in state
        print_check(f"字段 '{field}'", has_field)
        all_passed = all_passed and has_field
    
    return all_passed


def validate_feishu_doc():
    """Check Feishu document link (basic validation)"""
    print_header("📝 飞书文档检查")
    
    if not STATE_FILE.exists():
        print_check("状态文件存在", False)
        return False
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    links = state.get('links', {})
    feishu_doc = links.get('feishuDoc')
    
    if not feishu_doc:
        print_check("飞书文档链接", False, "未设置")
        return False
    
    # Basic URL validation
    is_valid = feishu_doc.startswith('https://feishu.cn/docx/')
    print_check("飞书文档链接格式", is_valid, feishu_doc if is_valid else "格式错误")
    
    return is_valid


def check_monitored_tools(html_content):
    """Check if monitored AI tools are mentioned"""
    print_header("🎯 重点工具监控检查")
    
    if not html_content:
        print("❌ 无法检查，HTML 内容为空")
        return
    
    # Tools to monitor (Chinese and English names)
    monitored_tools = {
        '即梦': ['即梦', 'Jimeng'],
        'Lovart': ['Lovart', 'lovart'],
        '豆包': ['豆包', 'Doubao'],
        'DeepSeek': ['DeepSeek', 'deepseek', '深度求索'],
        '哩布哩布': ['哩布哩布', 'LiblibAI', 'liblib'],
        'Midjourney': ['Midjourney', 'midjourney', 'MJ'],
        'Stable Diffusion': ['Stable Diffusion', 'SD', 'stability ai'],
        'Adobe Firefly': ['Firefly', 'Adobe Firefly'],
        'Figma AI': ['Figma', 'figma ai'],
        'Runway': ['Runway', 'runway ml', 'Gen-3'],
    }
    
    found_tools = []
    missing_tools = []
    
    for tool_name, keywords in monitored_tools.items():
        found = any(keyword.lower() in html_content.lower() for keyword in keywords)
        if found:
            found_tools.append(tool_name)
        else:
            missing_tools.append(tool_name)
    
    if found_tools:
        print(f"{Colors.GREEN}✅ 发现监控工具{Colors.END}: {', '.join(found_tools)}")
    else:
        print(f"{Colors.YELLOW}⚠️  今日未发现重点监控工具新闻{Colors.END}")
        print(f"   建议检查：Midjourney, Stable Diffusion, 即梦，豆包等")
    
    return found_tools


def generate_report(html_content):
    """Generate a summary report"""
    print_header("📋 内容摘要")
    
    if not html_content:
        print("❌ 无法生成摘要，HTML 文件检查失败")
        return
    
    # Extract news titles
    titles = re.findall(r'<h3 class="news-title">([^<]+)</h3>', html_content)
    
    if titles:
        print(f"📰 共 {len(titles)} 条新闻")
        print(f"\n前 5 条新闻标题:")
        for i, title in enumerate(titles[:5], 1):
            print(f"  {i}. {title[:60]}...")
    else:
        print("⚠️  未找到新闻标题")


def main():
    """Main validation function"""
    print(f"\n{Colors.BOLD}🔍 AI 日报内容验证器{Colors.END}")
    print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    dates = get_today_date()
    print(f"目标日期：{dates['cn']}")
    
    results = []
    
    # Run validations
    html_passed, html_content = validate_html_file()
    results.append(("HTML 文件", html_passed))
    
    state_passed = validate_state_file()
    results.append(("状态文件", state_passed))
    
    feishu_passed = validate_feishu_doc()
    results.append(("飞书文档", feishu_passed))
    
    # Generate report
    generate_report(html_content)
    
    # Check monitored tools
    check_monitored_tools(html_content)
    
    # Summary
    print_header("📊 验证总结")
    
    all_passed = all(passed for _, passed in results)
    
    for name, passed in results:
        status = f"{Colors.GREEN}✅{Colors.END}" if passed else f"{Colors.RED}❌{Colors.END}"
        print(f"{status} {name}")
    
    print()
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 所有检查通过！可以安全推送{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  发现错误！请修复后再推送{Colors.END}\n")
        print(f"{Colors.YELLOW}建议操作:{Colors.END}")
        print("  1. 检查失败的项目")
        print("  2. 参考 ai-daily-news/CHECKLIST.md")
        print("  3. 修复后重新运行验证")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
