# AI 日报网站

苹果官网风格的 AI 资讯日报网站，每日自动更新。

## 🌐 预览

本地预览地址：http://localhost:8080

## 📱 特性

- **苹果官网设计风格** - 极简、优雅、流畅动画
- **响应式布局** - 完美适配手机、平板、桌面
- **热门新闻标记** - 🔥 标识重磅新闻
- **🦞 OpenClaw 龙虾资讯** - 紧跟 OpenClaw 框架最新动态
- **设计垂直版块** - 🎨 专为设计师收集的 AI 资讯
- **一键分享** - 支持原生分享和复制链接

## 🚀 部署方式

### 方式 1: GitHub Pages（推荐）

1. 将 `ai-daily-news-website` 文件夹推送到 GitHub 仓库
2. 在仓库设置中启用 GitHub Pages
3. 选择 `main` 分支和 `/` 根目录
4. 获得公开链接：`https://yourusername.github.io/repo-name/`

### 方式 2: Vercel

1. 访问 https://vercel.com
2. 导入 GitHub 仓库
3. 自动部署，获得公开链接

### 方式 3: Netlify

1. 访问 https://netlify.com
2. 拖拽 `ai-daily-news-website` 文件夹到部署区域
3. 获得公开链接

### 方式 4: 本地服务器

```bash
cd ai-daily-news-website
python3 -m http.server 8080
# 访问 http://localhost:8080
```

## 📂 文件结构

```
ai-daily-news-website/
├── index.html          # 主页面（每日更新）
├── README.md           # 说明文档
└── archive/            # 往期归档（可选）
    ├── 2026-03-17.html
    └── 2026-03-18.html
```

## 🔄 每日更新流程

1. 早上 9:30 自动抓取最新 AI 新闻
2. 生成新的 `index.html`
3. 提交到 Git 仓库
4. 自动部署到托管平台

## 🎨 设计规范

### 配色
- 主背景：`#ffffff`
- 次要背景：`#fafafa`
- 主文字：`#1d1d1f`
- 次要文字：`#86868b`
- 强调色：`#0071e3`
- 热门标记：`#ff6b35`
- 设计标记：`#bf5af2`

### 字体
- 英文：SF Pro Display / -apple-system
- 中文：PingFang SC / 苹方

### 动画
- 卡片进入：`fadeInUp` 0.6s
- 悬停效果：`scale(1.02)` + 阴影
- 链接箭头：悬停时右移 4px

## 📊 内容结构

### 全球动态（20 条）
- 大公司博客更新
- 新模型发布
- 新工具/技术
- 行业热点
- 市场动态
- 学术研究

### 🦞 OpenClaw 龙虾资讯（5 条）
- GitHub 版本发布
- 代码提交更新
- 新技能发布
- 文档更新
- 社区热点讨论
- 插件/工具更新

### 设计 AI 资讯（8 条）
- 设计工具更新
- AI 绘画/视频
- 原型工具
- 色彩/排版工具
- 3D 设计工具

## 🔗 分享

- 点击页面右上角"分享"按钮
- 或复制链接直接发送
- 支持微信、钉钉、飞书等平台

## 📝 自定义

### 修改日期
编辑 `index.html` 中的：
- `<title>` 标签
- `.hero-date` 内容
- `.header .date` 内容

### 添加/删除新闻
复制/删除 `.news-card` 块，修改内容即可。

### 修改配色
编辑 `<style>` 中的 `:root` 变量。

## 📞 联系

如有问题或建议，请联系管理员。

---

© 2026 AI 日报 · 每日更新
