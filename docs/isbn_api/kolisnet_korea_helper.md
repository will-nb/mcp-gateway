## 韩国国立中央图书馆 KOLIS-NET helper.py 开发说明

- 官方文档: https://www.nl.go.kr/EN/contents/N30202000000.do
- 适用范围: 韩国出版物（韩语）
- 认证/Key: 需要申请服务 Key（`serviceKey`）
- 费用/配额: 免费（需申请），有速率限制
- 商用: 需遵守馆方条款；商业用途请确认许可

### 用途
通过官方 Open API 以 ISBN 检索书目信息（XML/JSON）。

### 建议的 helper 接口
```python
from typing import Any, Dict

def fetch_by_isbn(isbn: str, *, service_key: str, timeout: float = 10.0) -> Dict[str, Any]:
    """查询 KOLIS-NET 并返回规范化 JSON。"""
```

### 调用方式（HTTP，示例）
- 具体端点以官网为准，一般形如：
```
GET https://api.nl.go.kr/.../search?serviceKey={SERVICE_KEY}&isbn={ISBN}&format=json
```

### 返回数据（要点）
- 包含题名、著者、出版者、出版年、ISBN、分类号等；支持 XML/JSON。

### 规范化输出 JSON（建议）
```json
{
  "source": "kolisnet",
  "isbn": "9791162243077",
  "title": "...",
  "authors": ["..."],
  "publisher": "...",
  "published_date": "2021",
  "language": "ko",
  "categories": ["..."],
  "identifiers": {"isbn_13": "9791162243077"},
  "raw": {"...": "原始响应"}
}
```

### 错误与边界
- 未授权/Key 无效、配额限制、ISBN 多版本匹配

### 合规
- 遵守馆方条款与频控；避免过度缓存
