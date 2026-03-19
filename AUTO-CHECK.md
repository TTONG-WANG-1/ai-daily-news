# AI 日报自动化检查机制

## 📋 已建立的工具和流程

### 1. 验证脚本 (`validate.py`)
**位置**: `/home/wangtong/openclaw/workspace/ai-daily-news/validate.py`

**功能**: 在每日推送前自动检查内容质量

**检查项目**:
- ✅ HTML 文件存在且包含今日日期
- ✅ 无占位符内容
- ✅ 全球动态新闻数量 ≥ 15 条
- ✅ 设计 AI 新闻数量 ≥ 5 条
- ✅ Google 搜索链接格式正确
- ✅ 热门新闻标记数量合理 (5-15 个)
- ✅ 状态文件完整
- ✅ 飞书文档链接有效

**使用方法**:
```bash
cd /home/wangtong/openclaw/workspace/ai-daily-news
python3 validate.py
```

---

### 2. 检查清单 (`CHECKLIST.md`)
**位置**: `/home/wangtong/openclaw/workspace/ai-daily-news/CHECKLIST.md`

**内容**:
- 每日生成流程（5 个步骤）
- 常见错误及解决方案
- 新闻源优先级
- 质量检查标准

---

### 3. HEARTBEAT.md 集成
**位置**: `/home/wangtong/openclaw/workspace/HEARTBEAT.md`

**每日 9:00 AM 自动检查**:
1. 全球动态板块（20 条新闻）
2. 设计 AI 板块（8 条新闻）
3. 日期验证
4. 链接验证
5. 推送验证

---

### 4. 状态管理
**状态文件**: `memory/ai-daily-news-state.json`

**记录内容**:
- 最后推送日期
- 最后推送时间
- 飞书文档 ID 和链接
- GitHub Pages 链接
- 推送次数统计

---

## 🚀 每日工作流程

### 9:00 AM - 开始准备
```bash
# 1. 运行验证脚本检查昨日内容
cd /home/wangtong/openclaw/workspace/ai-daily-news
python3 validate.py

# 2. 查看状态文件
cat ../../memory/ai-daily-news-state.json
```

### 9:00-9:30 AM - 生成内容
1. 从新闻源获取最新资讯
   - VentureBeat AI
   - WIRED AI
   - TechCrunch AI
   - Creative Bloq (设计类)

2. 更新 HTML 文件
   - 替换日期
   - 填充新闻内容
   - 确保无旧闻混入

3. 创建飞书文档

### 9:30 AM - 推送
```bash
# 1. 再次验证
python3 validate.py

# 2. 提交推送
git add .
git commit -m "Update YYYY-MM-DD"
git push

# 3. 更新状态文件
# (自动或手动更新 memory/ai-daily-news-state.json)
```

### 9:35 AM - 发送链接
- 飞书文档链接
- GitHub Pages 链接

---

## ⚠️ 常见错误检查

### 错误 1: 板块沿用旧模板
**检查方法**: 
```bash
grep -o "DATE_PLACEHOLDER" index.html  # 应无输出
grep "⚠️ 请使用" index.html  # 应无输出
```

**解决**: 必须从真实新闻源重新抓取

### 错误 2: 日期未更新
**检查方法**:
```bash
grep "2026 年 03 月" index.html | head -3
```

**解决**: 更新所有日期占位符

### 错误 3: 热门标记过多/过少
**检查方法**:
```bash
grep -o "🔥 热门" index.html | wc -l
# 应在 5-15 之间
```

---

## 📊 验证报告示例

```
🔍 AI 日报内容验证器
检查时间：2026-03-19 10:51:27
目标日期：2026 年 03 月 19 日

============================================================
📄 HTML 文件检查
============================================================

✅ PASS - 网页标题包含今日日期
✅ PASS - 无占位符内容
✅ PASS - 全球动态新闻数量 (目标 20)
✅ PASS - 设计 AI 新闻数量 (目标 8)
✅ PASS - Google 搜索链接格式正确
✅ PASS - 热门新闻标记

============================================================
📊 状态文件检查
============================================================

✅ PASS - 最后推送日期
✅ PASS - 字段 'lastPushDocId'
...

🎉 所有检查通过！可以安全推送
```

---

## 📁 相关文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| validate.py | ai-daily-news/validate.py | 内容验证 |
| CHECKLIST.md | ai-daily-news/CHECKLIST.md | 检查清单 |
| generator.py | ai-daily-news/generator.py | 内容生成 |
| generate-daily-news.sh | ai-daily-news/generate-daily-news.sh | Shell 生成脚本 |
| ai-daily-news-state.json | memory/ai-daily-news-state.json | 状态管理 |
| HEARTBEAT.md | HEARTBEAT.md | 每日任务 |

---

## 🎯 质量目标

- **零模板内容**: 所有新闻必须来自当日抓取
- **零占位符**: 不允许出现 DATE_PLACEHOLDER 等
- **日期准确**: 所有日期显示正确
- **链接有效**: 所有 Google 搜索链接可跳转
- **板块平衡**: 全球动态 20 条 + 设计 AI 8 条

---

**最后更新**: 2026-03-19 10:52
**下次检查**: 2026-03-20 09:00
