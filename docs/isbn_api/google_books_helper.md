## Google Books API helper.py 开发说明

- 官方文档: https://developers.google.com/books
- 适用范围: 全球（英语书籍覆盖最佳）
- 认证/Key: API Key 可选（无 Key 也可调用，但更易触发配额/限流）；推荐配置 Key
- 费用/配额: 免费，有每日配额和速率限制
- 商用: 可用于商业用途，需遵守 Google APIs Terms of Service 与品牌展示/归因等要求；请核对最新条款

### 用途
根据 ISBN 查询书目信息，并输出统一的规范化 JSON。

### 建议的 helper 接口
```python
from typing import Any, Dict, Optional

def fetch_by_isbn(isbn: str, *, api_key: Optional[str] = None, lang: Optional[str] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """查询 Google Books 并返回规范化 JSON。"""
```

- 参数
  - `isbn`: 必填，支持 ISBN-10 或 ISBN-13（调用前建议用 `app/utils/isbn.py` 规范化）
  - `api_key`: 可选；配置后更稳定
  - `lang`: 可选，限制返回结果语言（例如 `en`、`zh`）
  - `timeout`: 超时秒数

### 调用方式（HTTP）
- Endpoint: `GET https://www.googleapis.com/books/v1/volumes`
- 查询: `q=isbn:{ISBN}`
- 可选: `key={API_KEY}`、`langRestrict={LANG}`、`maxResults`（建议 1-5）

示例:
```
GET https://www.googleapis.com/books/v1/volumes?q=isbn:9780134685991&maxResults=1&key=YOUR_KEY
```

### 返回数据（官方 JSON 结构要点）
- 顶层: `items: [ { volumeInfo, accessInfo, ... } ]`
- `volumeInfo.title`
- `volumeInfo.authors: [str]`
- `volumeInfo.publisher`
- `volumeInfo.publishedDate`
- `volumeInfo.language`
- `volumeInfo.categories: [str]`
- `volumeInfo.description`
- `volumeInfo.pageCount`
- `volumeInfo.industryIdentifiers: [{ type: ISBN_10|ISBN_13, identifier: str }]`
- `volumeInfo.imageLinks.{smallThumbnail, thumbnail}`
- `volumeInfo.previewLink`

### 规范化输出 JSON（建议）
```json
{
  "source": "google_books",
  "isbn": "9780134685991",
  "title": "Effective Java",
  "authors": ["Joshua Bloch"],
  "publisher": "Addison-Wesley",
  "published_date": "2018-01-06",
  "language": "en",
  "categories": ["Programming"],
  "description": "...",
  "page_count": 416,
  "identifiers": {"isbn_10": "0134685997", "isbn_13": "9780134685991"},
  "cover": {
    "small_thumbnail": "https://...",
    "thumbnail": "https://..."
  },
  "preview_url": "https://books.google....",
  "raw": {"...": "原始响应用于调试"}
}
```

### 错误与边界
- 无 `items` 或列表为空: 返回 `{"source": "google_books", "isbn": <输入>, "raw": {...}}` 并标注 `found: false`
- HTTP 4xx/5xx: 记录 `status_code` 与 `error_message`
- 429 限流: 回退/重试（指数退避），并可切换到其他数据源

### 速率限制与缓存
- 有每日配额与速率；对相同 ISBN 结果做持久化缓存（例如 24h），减少调用

### 许可与合规要点
- 遵循 Google APIs TOS；必要时展示来源/归因；避免长时间缓存封面与预览 URL；遵守用户数据政策
