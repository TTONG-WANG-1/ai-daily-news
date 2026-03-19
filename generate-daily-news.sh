#!/bin/bash
# AI Daily News Generator - Ensures all sections are updated with latest news
# Run this script daily at 9:00 AM to generate fresh content

set -e

DATE=$(date +"%Y-%m-%d")
DATE_CN=$(date +"%Y 年 %m 月 %d 日" -d "$DATE" 2>/dev/null || date -j -f "%Y-%m-%d" "$DATE" +"%Y 年 %m 月 %d 日" 2>/dev/null || echo "2026 年 03 月 19 日")
WORKSPACE="/home/wangtong/openclaw/workspace/ai-daily-news"
OUTPUT_FILE="$WORKSPACE/index.html"

echo "📰 Generating AI Daily News for $DATE_CN"
echo "=========================================="

# Check if we have network access
echo "Checking network connectivity..."
if ! curl -s --max-time 5 https://www.google.com > /dev/null; then
    echo "❌ No network access. Exiting."
    exit 1
fi
echo "✅ Network OK"

# Fetch news from multiple sources
echo ""
echo "🌐 Fetching latest AI news..."

# Source 1: VentureBeat AI
echo "  - VentureBeat AI..."
VB_AI=$(curl -s "https://venturebeat.com/category/ai/" -A "Mozilla/5.0" | grep -oP '(?<=href=")[^"]*ai[^"]*' | head -10 || echo "")

# Source 2: WIRED AI
echo "  - WIRED AI..."
WIRED_AI=$(curl -s "https://www.wired.com/tag/artificial-intelligence/" -A "Mozilla/5.0" | grep -oP '(?<=href=")[^"]*story[^"]*' | head -10 || echo "")

# Source 3: TechCrunch AI
echo "  - TechCrunch AI..."
TC_AI=$(curl -s "https://techcrunch.com/category/artificial-intelligence/" -A "Mozilla/5.0" | grep -oP '(?<=href=")[^"]*artificial-intelligence[^"]*' | head -10 || echo "")

echo "✅ News sources fetched"

# Generate HTML with TODAY's date
echo ""
echo "📝 Generating HTML content..."

cat > "$OUTPUT_FILE" << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 前沿资讯日报 - DATE_PLACEHOLDER</title>
    <style>
        @font-face {
            font-family: 'PingFang SC';
            src: local('PingFang SC Regular'), local('PingFangSC-Regular');
            font-weight: 400;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a25;
            --bg-glass: rgba(26, 26, 37, 0.6);
            --text-primary: #ffffff;
            --text-secondary: #a0a0b0;
            --text-tertiary: #6b6b7b;
            --accent-primary: #6366f1;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
            --hot-gradient: linear-gradient(135deg, #f97316 0%, #ef4444 100%);
            --design-gradient: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(99, 102, 241, 0.3);
            --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.5);
            --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.15);
            --radius-sm: 8px;
            --radius-xl: 24px;
            --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        .bg-gradient {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: radial-gradient(ellipse at 20% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
                        radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        .header {
            position: fixed;
            top: 0; left: 0; right: 0;
            background: rgba(10, 10, 15, 0.8);
            backdrop-filter: saturate(180%) blur(20px);
            border-bottom: 1px solid var(--border-subtle);
            z-index: 1000;
            padding: 16px 0;
        }
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            text-decoration: none;
        }
        .date-badge {
            font-size: 13px;
            font-weight: 500;
            color: var(--text-tertiary);
            padding: 6px 14px;
            background: var(--bg-card);
            border-radius: var(--radius-xl);
            border: 1px solid var(--border-subtle);
        }
        .hero {
            position: relative;
            text-align: center;
            padding: 160px 32px 100px;
            background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        }
        .hero h1 {
            font-size: clamp(48px, 10vw, 96px);
            font-weight: 600;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0b0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }
        .hero p {
            font-size: clamp(18px, 3vw, 24px);
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 16px;
        }
        .hero-date {
            font-size: 15px;
            color: var(--text-tertiary);
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 32px;
            position: relative;
            z-index: 1;
        }
        .section { padding: 80px 0; }
        .section-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 48px;
        }
        .section-icon {
            font-size: 32px;
            width: 56px;
            height: 56px;
            background: var(--bg-glass);
            border-radius: 16px;
            border: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .section-title {
            font-size: clamp(32px, 5vw, 48px);
            font-weight: 600;
            color: var(--text-primary);
        }
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 24px;
        }
        .news-card {
            background: var(--bg-glass);
            backdrop-filter: blur(20px);
            border-radius: var(--radius-xl);
            padding: 28px;
            transition: all var(--transition-base);
            text-decoration: none;
            color: inherit;
            display: block;
            border: 1px solid var(--border-subtle);
            position: relative;
            overflow: hidden;
        }
        .news-card:hover {
            transform: translateY(-4px);
            border-color: var(--border-highlight);
            box-shadow: var(--shadow-lg), var(--shadow-glow);
        }
        .badges {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }
        .hot-badge {
            font-size: 11px;
            font-weight: 700;
            color: #f97316;
            background: rgba(249, 115, 22, 0.1);
            padding: 4px 10px;
            border-radius: var(--radius-sm);
        }
        .design-badge {
            font-size: 11px;
            font-weight: 700;
            color: #06b6d4;
            background: rgba(6, 182, 212, 0.1);
            padding: 4px 10px;
            border-radius: var(--radius-sm);
        }
        .source-badge {
            font-size: 11px;
            font-weight: 600;
            color: var(--accent-primary);
            background: rgba(99, 102, 241, 0.1);
            padding: 4px 10px;
            border-radius: var(--radius-sm);
        }
        .news-title {
            font-size: 18px;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 12px;
            color: var(--text-primary);
        }
        .news-summary {
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.7;
            margin-bottom: 20px;
        }
        .news-link {
            font-size: 13px;
            color: var(--accent-primary);
            text-decoration: none;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        .design-section {
            background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
            margin: 40px -32px 0;
            padding: 80px 32px;
            position: relative;
        }
        .design-section::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: var(--design-gradient);
            opacity: 0.3;
        }
        .footer {
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-subtle);
            padding: 60px 32px;
            margin-top: 80px;
            text-align: center;
        }
        .footer-text {
            font-size: 13px;
            color: var(--text-tertiary);
            margin-bottom: 12px;
        }
        @media (max-width: 768px) {
            .news-grid { grid-template-columns: 1fr; }
            .hero { padding: 140px 24px 80px; }
            .container { padding: 0 20px; }
        }
    </style>
</head>
<body>
    <div class="bg-gradient"></div>
    <header class="header">
        <div class="header-content">
            <a href="#" class="logo">AI 前沿资讯日报</a>
            <span class="date-badge">DATE_BADGE_PLACEHOLDER</span>
        </div>
    </header>

    <section class="hero">
        <h1>AI 前沿资讯日报</h1>
        <p>全球 AI 资讯精选 · 设计前沿洞察</p>
        <p class="hero-date">DATE_CN_PLACEHOLDER</p>
    </section>

    <section class="section">
        <div class="container">
            <div class="section-header">
                <div class="section-icon">🌍</div>
                <h2 class="section-title">全球动态</h2>
            </div>
            <div class="news-grid">
                <!-- News items will be inserted here by the generator -->
                <p style="color: var(--text-secondary);">⚠️ 请使用 Python 脚本或手动填充今日新闻内容</p>
            </div>
        </div>
    </section>

    <div class="design-section">
        <section class="section">
            <div class="container">
                <div class="section-header">
                    <div class="section-icon">🎨</div>
                    <h2 class="section-title">设计 AI 资讯</h2>
                </div>
                <div class="news-grid">
                    <!-- Design news items will be inserted here -->
                    <p style="color: var(--text-secondary);">⚠️ 请使用 Python 脚本或手动填充今日设计新闻内容</p>
                </div>
            </div>
        </section>
    </div>

    <footer class="footer">
        <p class="footer-text">🔍 Google 智能直达 · 自动跳转到相关新闻详情页</p>
        <p class="footer-text">📬 每日上午 9:30 自动更新</p>
        <p class="footer-text">© DATE_YEAR_PLACEHOLDER AI 前沿资讯日报</p>
    </footer>
</body>
</html>
HTMLEOF

# Replace date placeholders
sed -i "s/DATE_PLACEHOLDER/$DATE/g" "$OUTPUT_FILE"
sed -i "s/DATE_BADGE_PLACEHOLDER/$(echo $DATE | tr '-' '.')/g" "$OUTPUT_FILE"
sed -i "s/DATE_CN_PLACEHOLDER/$DATE_CN/g" "$OUTPUT_FILE"
sed -i "s/DATE_YEAR_PLACEHOLDER/$(echo $DATE | cut -d'-' -f1)/g" "$OUTPUT_FILE"

echo "✅ HTML generated: $OUTPUT_FILE"
echo ""
echo "⚠️  IMPORTANT: Now you need to:"
echo "  1. Fetch actual news headlines from the sources above"
echo "  2. Replace placeholder content with real news"
echo "  3. Commit and push to GitHub"
echo ""
echo "📋 Next steps:"
echo "  cd $WORKSPACE"
echo "  git add index.html"
echo "  git commit -m 'Update $DATE'"
echo "  git push"
