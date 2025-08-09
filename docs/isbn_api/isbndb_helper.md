## ISBNdb API helper.py 开发说明

- 官方文档: https://isbndb.com/apidocs
- 适用范围: 全球（英语市场覆盖较好）
- 认证/Key: 需要 API Key（请求头）
- 费用/配额: 收费；提供免费额度（约 500 次/月，具体以官网为准）
- 商用: 支持商业使用（依订阅计划与条款）；请核对最新合约/限制

### 用途
根据 ISBN 查询权威书目信息（作者、出版社、出版日、分类、语言等）。

### 建议的 helper 接口
```python
from typing import Any, Dict

def fetch_by_isbn(isbn: str, *, api_key: str, timeout: float = 10.0) -> Dict[str, Any]:
    """查询 ISBNdb 并返回规范化 JSON。"""
```

- 参数
  - `isbn`: 必填
  - `api_key`: 必填（请求头 `X-API-KEY`）
  - `timeout`: 超时

### 调用方式（HTTP）
- `GET https://api2.isbndb.com/book/{ISBN}`
- 请求头: `X-API-KEY: <YOUR_KEY>`

### 返回数据（要点）
- 顶层常见: `{ "book": { "title", "authors", "publisher", "date_published", "language", "isbn", "isbn13", "subjects", ... } }`

### 规范化输出 JSON（建议）
```json
{
  "source": "isbndb",
  "isbn": "9780134685991",
  "title": "Effective Java",
  "authors": ["Joshua Bloch"],
  "publisher": "Addison-Wesley",
  "published_date": "2018-01-06",
  "language": "en",
  "categories": ["Computers / Programming"],
  "description": null,
  "page_count": null,
  "identifiers": {"isbn_10": "0134685997", "isbn_13": "9780134685991"},
  "cover": null,
  "preview_url": null,
  "raw": {"...": "原始响应"}
}
```

### 错误与边界
- 401/403: Key 错误或配额不足
- 404: 未找到图书
- 429: 限流，建议指数退避

### 速率与缓存
- 按订阅计划计费/限速；强烈建议缓存

### 合规
- 遵守 ISBNdb 使用条款；避免共享/泄露 API Key；遵守商业使用限制与品牌要求
