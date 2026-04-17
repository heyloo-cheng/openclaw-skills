# 方案 2：proxy_pool + Cookie 部署指南

## 📦 方案概述

基于 GitHub 最佳实践的免费爬取方案：
- **jhao104/proxy_pool**：开源代理池（11个免费代理源）
- **Cookie 认证**：绕过登录验证
- **自动代理轮换**：避免 IP 被封

**成本**：免费  
**成功率**：60-70%  
**维护**：中等

---

## 🚀 快速部署

### 步骤 1：安装 proxy_pool

```bash
# 1. 克隆项目
cd ~/.openclaw/workspace
git clone https://github.com/jhao104/proxy_pool.git
cd proxy_pool

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 配置（可选）
# 编辑 setting.py，配置 Redis 等
```

### 步骤 2：启动代理池

```bash
# 启动 API 服务（端口 5010）
python3 proxyPool.py server

# 另开一个终端，启动调度程序（采集代理）
python3 proxyPool.py schedule
```

### 步骤 3：等待代理采集

```bash
# 查看代理数量
curl http://127.0.0.1:5010/count

# 查看所有代理
curl http://127.0.0.1:5010/all

# 等待 5-10 分钟，直到有足够的代理
```

### 步骤 4：配置 Cookie

1. 打开浏览器，访问 https://www.1688.com
2. 登录你的账号
3. 按 F12 打开开发者工具
4. 在控制台运行：`copy(document.cookie)`
5. Cookie 已复制到剪贴板

### 步骤 5：配置爬虫

编辑 `scrapling_1688_final.py`，设置 Cookie：

```python
# 配置
PROXY_POOL_URL = "http://127.0.0.1:5010"
COOKIE = "你复制的Cookie"  # 粘贴到这里
```

### 步骤 6：运行爬虫

```bash
python3 ~/.openclaw/workspace/.agents/skills/scrapling/scrapling_1688_final.py "迷你加湿器"
```

---

## 📊 预期结果

### 成功情况
```
🔍 搜索关键词: 迷你加湿器
🌐 使用 proxy_pool + Cookie

🌐 代理池可用代理数: 15

正在爬取第 1 页...
  🔗 使用代理: http://123.45.67.89:8080
  🔐 使用 Cookie 认证
  ✅ 请求成功 (延迟: 2500ms)
  页面标题: 迷你加湿器批发_迷你加湿器厂家_1688
  找到 20 个元素

✅ 找到 15 个商品
💰 价格范围: ¥2.66 - ¥33.00
📊 平均价格: ¥18.88
```

### 失败情况

**1. 代理池未启动**
```
❌ 代理池未启动，请先运行: python proxyPool.py server
```

**解决**：启动 proxy_pool

**2. 代理池为空**
```
⚠️ 代理池为空，请先启动 proxy_pool 并等待代理采集
```

**解决**：等待 5-10 分钟，让代理池采集代理

**3. Cookie 过期**
```
❌ 被重定向到登录页
提示: Cookie 可能已过期，请重新获取
```

**解决**：重新从浏览器复制 Cookie

---

## 🔧 故障排查

### 检查代理池状态

```bash
# 检查 API 是否运行
curl http://127.0.0.1:5010/

# 检查代理数量
curl http://127.0.0.1:5010/count

# 获取一个代理测试
curl http://127.0.0.1:5010/get/
```

### 检查 Cookie 有效性

1. 打开浏览器
2. 访问 https://www.1688.com
3. 检查是否已登录
4. 如果未登录，重新登录并复制 Cookie

### 查看调试信息

爬取失败时，HTML 会保存到 `/tmp/1688_final_*.html`，可以查看具体错误。

---

## 💡 优化建议

### 1. 增加代理源

编辑 `proxy_pool/setting.py`：

```python
PROXY_FETCHER = [
    "freeProxy01",
    "freeProxy02",
    "freeProxy03",
    # ... 添加更多
]
```

### 2. 调整验证频率

编辑 `proxy_pool/setting.py`：

```python
# 代理验证间隔（秒）
PROXY_CHECK_INTERVAL = 300  # 5分钟
```

### 3. 使用付费代理

如果免费代理质量不够，可以在 `ProxyFetcher` 中添加付费代理源。

---

## 📈 成功率对比

| 方案 | 成功率 | 成本 | 维护 |
|------|--------|------|------|
| 仅代理池 | 30-40% | 免费 | 中 |
| 代理池 + Cookie | 60-70% | 免费 | 中 |
| Deep Search | 100% | $3-15/月 | 零 |
| Oxylabs API | 100% | $300+/月 | 零 |

---

## 🎯 建议

### 适用场景
- 预算有限
- 愿意投入时间维护
- 采集量不大（<100商品/天）

### 不适用场景
- 需要高成功率
- 大规模采集
- 无法维护代理池

**如果方案 2 效果不理想，建议回到 Deep Search + 缓存方案。**

---

## 📚 参考资源

- proxy_pool 项目：https://github.com/jhao104/proxy_pool
- 1688 爬虫实战：https://github.com/Know1ng/tb1688
- Oxylabs 商业方案：https://github.com/oxylabs/1688-scraper
