## Library of Congress (LoC) API helper.py 开发说明

- 官方文档: https://libraryofcongress.github.io/data-exploration/
- 适用范围: 美国出版物（英语）
- 认证/Key: 不需要
- 费用/配额: 免费；存在礼貌速率限制
- 商用: 允许使用，遵循 LoC 使用条款与归因

### 用途
使用 LoC JSON API 按 ISBN 检索图书。

### 建议的 helper 接口
```python
from typing import Any, Dict

def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> Dict[str, Any]:
    """查询 LoC 并返回规范化 JSON。"""
```

### 调用方式（HTTP）
- `GET https://www.loc.gov/books/?q=isbn:{ISBN}&fo=json&at=results&c=1`
  - `fo=json` 返回 JSON
  - `c=1` 限制返回 1 条（可选）

### 返回数据（要点）
- 顶层 `results: [ { title, creator, publisher, date, language, subject, id, ... } ]`

### 规范化输出 JSON（建议）
```json
{
  "source": "loc",
  "isbn": "9780143127796",
  "title": "...",
  "authors": ["..."],
  "publisher": "...",
  "published_date": "2014",
  "language": "en",
  "categories": ["..."],
  "identifiers": {"isbn_13": "9780143127796"},
  "preview_url": "https://www.loc.gov/item/...",
  "raw": {"...": "原始响应"}
}
```

### 错误与边界
- `results` 为空；字段可能缺省（需容错/默认值）

### 合规
- 遵守 LoC 数据使用指引；建议归因

### Key / 注册信息
- 注册入口: https://libraryofcongress.github.io/data-exploration/
- 注册/费用: LoC 的 JSON 搜索接口通常无需 Key，免费使用；请遵守访问频率建议。
- 不注册的区别: 无需注册即可使用；但需礼貌访问避免被限速。
