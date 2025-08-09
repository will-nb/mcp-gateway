## WorldCat Search API (OCLC) helper.py 开发说明

- 官方文档: https://developer.oclc.org/docs/worldcat-search-api
- 适用范围: 全球学术与图书馆数据，适合多版本/多语言比对
- 认证/Key: 需要 OCLC WSKey（API Key）；部分端点需要 OAuth 2.0（Bearer）
- 费用/配额: 收费，部分合作机构可免费/优惠
- 商用: 受限于 OCLC 合同条款；通常需机构授权与合规审查

### 用途
按 ISBN 检索编目记录，提取核心书目信息。

### 建议的 helper 接口
```python
from typing import Any, Dict, Optional

def fetch_by_isbn(isbn: str, *, wskey: str, access_token: Optional[str] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """查询 WorldCat 并返回规范化 JSON。"""
```

- 参数
  - `isbn`: 必填
  - `wskey`: 必填（部分场景还需 `access_token`）
  - `access_token`: 可选，OAuth 2.0 获取
  - `timeout`: 超时

### 调用方式（HTTP）
常见两类：
1) SRU 检索（无需 OAuth，带 `wskey`）：
```
GET https://worldcat.org/discovery/bib/search?&q=isbn:{ISBN}&wskey={WSKEY}&format=json&limit=1
```
2) Discovery/Records 端点（需要 OAuth Bearer）：
```
GET https://worldcat.org/discovery/bib/data/{oclcNumber}
Authorization: Bearer {ACCESS_TOKEN}
```

### 返回数据（要点）
- JSON 或 XML；包含 OCLC Number、题名、著者、出版、主题、标识符（含 ISBN）等。不同端点字段命名有差异

### 规范化输出 JSON（建议）
```json
{
  "source": "worldcat",
  "isbn": "9780134685991",
  "title": "Effective Java",
  "authors": ["Joshua Bloch"],
  "publisher": "Addison-Wesley",
  "published_date": "2018",
  "language": "en",
  "categories": ["Programming"],
  "identifiers": {"isbn_10": "0134685997", "isbn_13": "9780134685991", "oclc": "123456789"},
  "cover": null,
  "preview_url": null,
  "raw": {"...": "原始响应"}
}
```

### 错误与边界
- 鉴权失败（401/403）、无结果（200 但 `numFound=0`）、速率/配额控制
- 建议优先 SRU + `limit=1`，命中多个版本需择优（优先语言、出版年最新）

### 缓存与合规
- 按合同限制缓存/展示范围；OCLC 通常限制大规模缓存与再分发；务必核对协议

### Key / 注册信息
- 注册入口: https://developer.oclc.org/docs/worldcat-search-api
- 注册/费用: 需要 OCLC 账号和 WSKey，部分端点需 OAuth。为收费服务，通常面向机构订阅或合作院校；具体费用与权限以 OCLC 官方为准。
- 不注册的区别: 无法访问正式 Search API。仅开放样例/沙盒；生产调用需 WSKey/OAuth。
