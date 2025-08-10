## 聚合数据 ISBN 查询（Juhe） helper.py 开发说明

- 官方文档: https://www.juhe.cn/docs/api/id/726
- 用途: 根据 ISBN（10/13 位）查询图书详情，统一输出 `NormalizedBook`
- 认证/Key: `JUHE_ISBN_API_KEY`

### Python 函数签名

```python
from typing import Dict, Any

def fetch_by_isbn(isbn: str, *, api_key: str, timeout: float = 10.0) -> Dict[str, Any]:
    """调用 Juhe ISBN API 并返回规范化 JSON。"""
```

### 请求参数
- `isbn`: 必填，支持 ISBN-10 或 ISBN-13
- `api_key`: 必填，通过环境变量 `JUHE_ISBN_API_KEY` 提供
- `timeout`: 超时秒数

### 接口与示例
- GET `http://apis.juhe.cn/isbn/query`
- Header: `Content-Type: application/x-www-form-urlencoded`
- Query: `key={API_KEY}&isbn={ISBN}`

返回示例（节选）：

```json
{
  "reason": "成功",
  "result": {
    "data": {
      "title": "霍乱时期的爱情",
      "author": "[哥伦比亚]加西亚•马尔克斯",
      "publisher": "南海出版社",
      "pubDate": "201209",
      "isbn": "9787544258975",
      "isbn10": "7544258971",
      "price": "39.50",
      "binding": "精装",
      "page": "41",
      "language": "zh",
      "img": "https://...",
      "gist": "..."
    },
    "orderid": "JH726..."
  },
  "error_code": 0
}
```

### 规范化输出字段映射
- `source`: 固定为 `"juhe_isbn"`
- `isbn`: 输入值（未经校验）
- `title`/`subtitle`: `data.title` / `data.subtitle`
- `creators`: 由 `data.author` 拆分（`；/，/,/、/|`）生成 `[{"name": str}]`
- `publisher`: `data.publisher`
- `published_date`: `data.pubDate`
- `language`: `data.language`
- `description`: `data.gist`
- `page_count`: `int(data.page)`（无法转换则为空）
- `identifiers`: `{"isbn_10": data.isbn10, "isbn_13": data.isbn}`
- `cover`: `{small, medium, large} = data.img`
- `preview_urls`: 若存在 `ebookUrl/previewUrl/detailUrl/doubanUrl`，尝试加入并做可达性过滤
- `raw`: 原始响应 JSON

### 错误处理
- `HTTP 429` → 抛出 `RateLimitError`
- `HTTP >= 400` → 抛出 `HttpError`
- `error_code != 0`（如 `272602 未找到`）→ 返回仅含 `source/isbn/raw` 的占位结构，上层会自动回退到其他来源

### 使用说明
- 在 `manager` 的国别优先级中，`CN` 已替换为 Juhe 来源
- 配置：在运行环境中设置 `JUHE_ISBN_API_KEY`
