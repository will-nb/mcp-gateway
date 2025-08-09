## Open Library API helper.py 开发说明

- 官方文档: https://openlibrary.org/developers/api
- 适用范围: 全球开源书目信息，英语内容较多
- 认证/Key: 不需要
- 费用/配额: 免费，无硬性配额；请遵守礼貌访问与速率限制（对服务友好）
- 商用: 数据开放，可用于商业用途，请遵循 Open Library/Internet Archive 的使用与归因要求

### 用途
根据 ISBN 查询书目信息，兼容两类接口：
1) 详情数据: `/api/books?bibkeys=ISBN:{ISBN}&format=json&jscmd=data`
2) 直接记录: `/isbn/{ISBN}.json`（返回 edition JSON，较原始）

### 建议的 helper 接口
```python
from typing import Any, Dict, Optional

def fetch_by_isbn(isbn: str, *, prefer_data_api: bool = True, timeout: float = 10.0) -> Dict[str, Any]:
    """查询 Open Library 并返回规范化 JSON。"""
```

- 参数
  - `isbn`: 必填
  - `prefer_data_api`: 优先使用 `api/books` 的整洁数据；失败后回退到 `/isbn/{isbn}.json`
  - `timeout`: 超时

### 调用方式（HTTP）
- `GET https://openlibrary.org/api/books?bibkeys=ISBN:{ISBN}&format=json&jscmd=data`
- 备选: `GET https://openlibrary.org/isbn/{ISBN}.json`

### 返回数据（要点）
- `api/books` 形式：顶层以 `ISBN:{ISBN}` 为 key，包含 `title`、`authors[{name}]`、`publish_date`、`publishers[{name}]`、`identifiers.isbn_10/isbn_13`、`cover.{small, medium, large}`、`subjects[{name}]`
- `/isbn/{isbn}.json`：edition 原始记录，作者/出版社可能以 `/authors/OL...A`、`/publishers/...` 引用，需要二次拉取或忽略

### 规范化输出 JSON（建议）
```json
{
  "source": "open_library",
  "isbn": "9780134685991",
  "title": "Effective Java",
  "authors": ["Joshua Bloch"],
  "publisher": "Addison-Wesley",
  "published_date": "2018",
  "language": null,
  "categories": ["Programming"],
  "description": null,
  "page_count": null,
  "identifiers": {"isbn_10": "0134685997", "isbn_13": "9780134685991"},
  "cover": {
    "small": "https://covers.openlibrary.org/b/id/....-S.jpg",
    "medium": "https://covers.openlibrary.org/b/id/....-M.jpg",
    "large": "https://covers.openlibrary.org/b/id/....-L.jpg"
  },
  "preview_url": null,
  "raw": {"...": "原始响应"}
}
```

### 错误与边界
- `api/books` 返回空对象: 回退到 `/isbn/{isbn}.json`
- 作者/出版社是引用对象: 可选做二次请求或忽略（建议最小化一次查询时延）

### 速率与缓存
- 无硬性限额，但需礼貌访问；建议对结果缓存 24h

### 许可与合规
- 元数据通常为开放许可；封面由 `covers.openlibrary.org` 提供，遵守其使用条款；建议显示来源归因

### Key / 注册信息
- 注册入口: https://openlibrary.org/developers/api
- 注册/费用: 不需要注册或 Key，免费使用。请遵守礼貌访问（限速、自限并发）。
- 不注册的区别: 无注册流程；但过度访问可能被临时限速或封禁 IP。
