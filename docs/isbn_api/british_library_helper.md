## British Library Catalogue API helper.py 开发说明

- 官方文档: https://www.bl.uk/catalogues-and-collections/apis
- 适用范围: 英国出版物（英语）
- 认证/Key: 视具体 API 而定；BL 提供 SRU 与部分现代 API（可能需要 Key）
- 费用/配额: 免费（公共服务），具体限额以官网为准
- 商用: 需遵守 BL 的使用条款；商业用途请先确认

### 用途
按 ISBN 检索英国图书馆书目。建议优先 SRU（稳定且公开）。

### 建议的 helper 接口
```python
from typing import Any, Dict

def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> Dict[str, Any]:
    """查询 British Library（SRU）并返回规范化 JSON。"""
```

### 调用方式（SRU 示例）
```
GET https://sru.bl.uk/SRU?operation=searchRetrieve&version=1.2&query=isbn=%22{ISBN}%22&maximumRecords=1&recordSchema=mods
```
- 说明：使用 `recordSchema=mods` 或其他支持的 schema（如 `dc`）。

### 返回数据（要点）
- XML（MODS/DC）：题名、著者、出版、ISBN、主题等。

### 规范化输出 JSON（建议）
```json
{
  "source": "british_library",
  "isbn": "9780141036144",
  "title": "...",
  "authors": ["..."],
  "publisher": "...",
  "published_date": "2008",
  "language": "en",
  "categories": null,
  "identifiers": {"isbn_13": "9780141036144"},
  "raw": {"...": "原始 XML/JSON"}
}
```

### 错误与边界
- SRU 200 但无记录；XML 解析

### 合规
- 遵守 BL API/SRU 使用条款；必要时做归因
