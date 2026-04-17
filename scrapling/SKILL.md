# Scrapling Skill - 现代化网页爬取

## 概述

Scrapling 是一个强大的 Python 网页爬取框架，支持从单个请求到大规模爬虫的所有场景。

**核心优势**：
- 🚀 比 BeautifulSoup 快 784 倍
- 🛡️ 绕过 Cloudflare Turnstile
- 🔄 自适应元素追踪（网站改版后自动适应）
- ⚡ 并发爬取 + 暂停/恢复
- 🎯 多种爬取模式（HTTP/隐身/完整浏览器）

## 何时使用

- 需要爬取 1688/闲鱼等电商网站
- 遇到反爬虫/验证码拦截
- 需要高性能批量爬取
- 网站结构经常变化

## 三种爬取模式

### 1. HTTP 请求（最快）

适用于：静态页面、API 接口

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com', impersonate='chrome')
prices = page.css('.price::text').getall()
```

### 2. 隐身模式（绕过反爬虫）

适用于：Cloudflare 保护的网站

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://example.com',
    headless=True,
    solve_cloudflare=True
)
data = page.css('.product').getall()
```

### 3. 完整浏览器（动态加载）

适用于：JavaScript 渲染的页面

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch(
    'https://example.com',
    headless=True,
    network_idle=True
)
data = page.css('.product').getall()
```

## 常用选择器

```python
# CSS 选择器
page.css('.product')
page.css('.price::text').get()  # 单个
page.css('.price::text').getall()  # 所有

# XPath
page.xpath('//div[@class="product"]')

# BeautifulSoup 风格
page.find_all('div', class_='product')

# 文本搜索
page.find_by_text('价格', tag='span')

# 正则搜索
page.find_by_regex(r'\d+\.\d+', tag='span')
```

## 自适应元素追踪

网站改版后自动重新定位元素：

```python
# 第一次爬取，保存元素特征
products = page.css('.product', auto_save=True)

# 网站改版后，自动适应
products = page.css('.product', adaptive=True)
```

## 会话管理

保持 Cookie 和状态：

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    # 登录
    session.post('https://example.com/login', data={...})
    
    # 访问需要登录的页面
    page = session.get('https://example.com/profile')
```

## 代理轮换

```python
from scrapling.fetchers import StealthyFetcher

proxies = [
    'http://proxy1:8080',
    'http://proxy2:8080',
]

page = StealthyFetcher.fetch(
    'https://example.com',
    proxy=proxies[0]  # 手动轮换
)
```

## 实战示例

### 示例 1：爬取 1688 商品价格

```python
from scrapling.fetchers import StealthyFetcher

url = 'https://s.1688.com/selloffer/offer_search.htm?keywords=蓝牙耳机'
page = StealthyFetcher.fetch(url, headless=True)

products = page.css('.offer-item')
for product in products:
    title = product.css('.title::text').get()
    price = product.css('.price::text').get()
    print(f"{title}: {price}")
```

### 示例 2：批量下载图片

```python
from scrapling.fetchers import Fetcher
import requests

page = Fetcher.get('https://example.com/products')
images = page.css('img::attr(src)').getall()

for i, img_url in enumerate(images):
    response = requests.get(img_url)
    with open(f'image_{i}.jpg', 'wb') as f:
        f.write(response.content)
```

### 示例 3：处理分页

```python
from scrapling.fetchers import Fetcher

url = 'https://example.com/products?page=1'
all_products = []

while url:
    page = Fetcher.get(url)
    products = page.css('.product').getall()
    all_products.extend(products)
    
    # 获取下一页链接
    next_link = page.css('.next-page::attr(href)').get()
    url = next_link if next_link else None
```

## 错误处理

```python
from scrapling.fetchers import StealthyFetcher

try:
    page = StealthyFetcher.fetch('https://example.com', timeout=30)
    data = page.css('.product').getall()
except Exception as e:
    print(f"爬取失败: {e}")
    # 降级方案
    data = []
```

## 性能优化

1. **使用 HTTP 模式**（最快）- 优先选择
2. **批量请求** - 使用会话复用连接
3. **并发爬取** - 使用 Spider 框架
4. **缓存结果** - 避免重复请求

## 注意事项

1. **遵守 robots.txt** - 尊重网站规则
2. **控制频率** - 避免过快请求
3. **使用代理** - 避免 IP 封禁
4. **错误重试** - 网络不稳定时重试

## 相关资源

- 官方文档：https://scrapling.readthedocs.io
- GitHub：https://github.com/D4Vinci/Scrapling
- 示例代码：`~/.openclaw/workspace/.agents/skills/scrapling/examples/`

## 封装脚本

使用封装好的脚本：

```bash
# 爬取 1688
python ~/.openclaw/workspace/.agents/skills/scrapling/scrapling_1688.py "蓝牙耳机"

# 爬取闲鱼
python ~/.openclaw/workspace/.agents/skills/scrapling/scrapling_xianyu.py "手机支架"

# 下载图片
python ~/.openclaw/workspace/.agents/skills/scrapling/scrapling_images.py "https://example.com"
```
