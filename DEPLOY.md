# 🚀 GitHub Pages 部署指南

## 步骤 1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `ai-daily-news`（或你喜欢的名字）
   - **Description**: AI 资讯日报网站 - 每日更新
   - **Visibility**: Public（公开）或 Private（私有）都可以
   - **不要** 勾选 "Add a README file"
3. 点击 **Create repository**

## 步骤 2: 获取仓库 URL

创建后，你会看到类似这样的 URL：
```
https://github.com/你的用户名/ai-daily-news.git
```

## 步骤 3: 配置远程仓库

在终端执行以下命令（替换为你的仓库 URL）：

```bash
cd /home/wangtong/openclaw/workspace
git remote add origin https://github.com/你的用户名/ai-daily-news.git
git branch -M main
git push -u origin main
```

## 步骤 4: 启用 GitHub Pages

1. 进入你的 GitHub 仓库页面
2. 点击 **Settings**（设置）
3. 左侧菜单点击 **Pages**
4. 在 **Build and deployment** 下：
   - Source: 选择 `Deploy from a branch`
   - Branch: 选择 `main`，文件夹选择 `/ (root)`
5. 点击 **Save**

## 步骤 5: 获取分享链接

等待 1-2 分钟部署完成后，你的网站地址是：

```
https://你的用户名.github.io/ai-daily-news/
```

---

## 📱 分享给同事

直接发送上面的链接即可！例如：
```
https://wangtong.github.io/ai-daily-news/
```

---

## 🔄 每日自动更新

配置 cron 任务自动推送更新：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天 9:35 推送，在日报生成后 5 分钟）
35 9 * * * cd /home/wangtong/openclaw/workspace && git add -A && git commit -m "每日更新 $(date +\%Y-\%m-\%d)" && git push origin main
```

---

## ⚠️ 常见问题

### 页面显示 404
- 等待 1-2 分钟，GitHub Pages 需要时间构建
- 检查 Pages 设置是否正确

### 样式不加载
- 确保 HTML 中的路径是相对的
- 检查浏览器控制台是否有错误

### 更新后看不到变化
- 清除浏览器缓存
- 使用 Ctrl+F5 强制刷新

---

## 🎯 快速命令

```bash
# 查看当前 remote
git remote -v

# 修改 remote URL
git remote set-url origin https://github.com/你的用户名/ai-daily-news.git

# 手动推送更新
cd /home/wangtong/openclaw/workspace
git add -A
git commit -m "更新 AI 日报"
git push origin main
```

---

需要帮助？告诉我你的 GitHub 用户名，我可以生成完整的命令！
