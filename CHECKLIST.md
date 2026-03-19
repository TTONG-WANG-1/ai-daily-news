# AI 日报生成检查清单

## 每日生成流程 (9:00 AM)

### 1. 内容获取 ✅
- [ ] 从 VentureBeat AI 获取最新 10 条新闻
- [ ] 从 WIRED AI 获取最新 10 条新闻
- [ ] 从 TechCrunch AI 获取最新 5 条新闻
- [ ] 从 Creative Bloq 获取设计 AI 新闻 8 条
- [ ] 确保所有新闻是**今日或昨日**发布

### 2. 内容验证 ✅
- [ ] 全球动态板块：20 条新闻
- [ ] 设计 AI 板块：8 条新闻
- [ ] 每条新闻都有标题 + 摘要 + 链接
- [ ] **无模板内容/旧闻混入**
- [ ] 所有 Google 搜索链接格式正确

### 3. 飞书文档 ✅
- [ ] 创建新文档（标题含日期）
- [ ] 格式：日期单独一行
- [ ] 每条新闻：标题 + 简报 + 链接各占一块
- [ ] 最多 20 条新闻
- [ ] 更新状态文件

### 4. GitHub Pages ✅
- [ ] 更新 index.html 日期
- [ ] 替换所有新闻内容为最新
- [ ] 设计板块同步更新
- [ ] 提交并推送

### 5. 状态更新 ✅
- [ ] 更新 `memory/ai-daily-news-state.json`
- [ ] 记录推送日期、时间、文档 ID
- [ ] 推送计数 +1

---

## 常见错误

### ❌ 错误：板块沿用旧模板
**症状**: 设计 AI 资讯板块内容是前几天的
**解决**: 必须从设计新闻源重新抓取，不可复用

### ❌ 错误：日期未更新
**症状**: 网页标题还是昨天日期
**解决**: 检查 HTML 中所有日期占位符

### ❌ 错误：链接格式错误
**症状**: Google 搜索链接无法跳转
**解决**: 确保使用 `https://www.google.com/search?q=xxx&btnI=1` 格式

---

## 自动化脚本

```bash
# 生成日报
cd /home/wangtong/openclaw/workspace/ai-daily-news
python3 generator.py

# 检查内容
cat memory/ai-daily-news-state.json

# 推送
git add .
git commit -m "Update YYYY-MM-DD"
git push
```

---

## 新闻源优先级

### 全球动态 (主板块)
1. VentureBeat AI (优先)
2. WIRED AI (优先)
3. TechCrunch AI
4. arXiv cs.AI (论文)

### 设计 AI (副板块)
1. Creative Bloq AI
2. WIRED Design
3. Adobe Max News
4. Figma Community

### 🎯 重点监控 AI 设计工具
**每日必查更新/新闻：**
- **即梦** (Jimeng) - 字节跳动 AI 绘画工具
- **Lovart** - AI 艺术生成平台
- **豆包** (Doubao) - 字节跳动 AI 助手
- **DeepSeek** - 深度求索 AI 模型
- **哩布哩布** (LiblibAI) - AI 模型分享平台
- **Midjourney** - AI 图像生成
- **Stable Diffusion** - Stability AI
- **DALL-E 3** - OpenAI
- **Adobe Firefly** - Adobe AI
- **Figma AI** - 设计工具
- **Canva AI** - 在线设计
- **Runway ML** - 视频生成
- **Leonardo AI** - 游戏/艺术生成
- **Clipdrop** - Stability AI 工具集

**监控内容：**
- 版本更新 (如 Midjourney V7、SD 3.5 等)
- 重大功能突破
- 热点争议新闻
- 价格/政策调整
- 新模型发布

---

## 质量检查

- [ ] 所有新闻标题无乱码
- [ ] 摘要简洁（50-100 字）
- [ ] 链接可点击且正确
- [ ] 热门标记合理（3-5 条）
- [ ] 无重复新闻
- [ ] 中文翻译准确

---

**最后更新**: 2026-03-19
**下次检查**: 2026-03-20 09:00
