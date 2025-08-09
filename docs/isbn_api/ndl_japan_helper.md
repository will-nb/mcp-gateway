## 日本国立国会図書館（NDL） helper.py 开发说明

- 官方文档: https://ndlsearch.ndl.go.jp/en/api
- 适用范围: 日本出版物（日语）
- 认证/Key: 依据最新文档，部分接口可能需要申请 API Key；请以官网为准
- 费用/配额: 免费
- 商用: 一般可用，需遵守 NDL 使用条款与归因/缓存限制

### 用途
按 ISBN 通过 SRU/CQL 检索编目记录，返回 XML 或 JSON（视参数与版本）。

### 建议的 helper 接口
```python
from typing import Any, Dict

def fetch_by_isbn(isbn: str, *, api_key: str | None = None, timeout: float = 10.0) -> Dict[str, Any]:
    """查询 NDL Search 并返回规范化 JSON。"""
```

### 调用方式（HTTP）
- SRU 示例：
```
GET https://ndlsearch.ndl.go.jp/api/sru?operation=searchRetrieve&recordSchema=dcndl&maximumRecords=1&query=isbn={ISBN}
```
- 如需 JSON，请参考新版 API 是否提供 `output=json` 或相应端点（以官网为准）。

### 返回数据（要点）
- 含题名、著者、出版者、出版年、ISBN、NDL ID 等；XML 命名空间较多，需要解析映射。

### 规范化输出 JSON（建议）
```json
{
  "source": "ndl",
  "isbn": "9784048913960",
  "title": "...",
  "authors": ["..."],
  "publisher": "...",
  "published_date": "2019",
  "language": "ja",
  "categories": null,
  "identifiers": {"isbn_13": "9784048913960", "ndl": "..."},
  "raw": {"...": "原始响应（XML/JSON）"}
}
```

### 错误与边界
- SRU 可能返回 200 但无记录；需判断 `numberOfRecords`
- XML 解析需处理命名空间与多值字段

### 合规
- 遵循 NDL API 使用条款与频控；必要时显示来源
