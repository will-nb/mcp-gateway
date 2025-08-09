## 香港公共图书馆（HKPL） helper.py 开发说明

- 参考入口: https://www.hkpl.gov.hk/tc/services/library/library-catalogue
- 适用范围: 香港出版物（繁体中文）
- 认证/Key: 官方未公开面向公众的 ISBN 检索 JSON API
- 费用/配额: 公共服务免费
- 商用: 如需商业化/自动化访问，建议联系馆方确认许可

### 重要说明
- 官方网站提供检索页面，但未公开稳定的 REST/JSON API 规范。
- 香港政府开放数据平台可能提供相关书目数据集，但非实时检索。

### 建议的 helper 接口（占位）
```python
from typing import Any, Dict

def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> Dict[str, Any]:
    """占位：无官方 JSON API 时不抓取网页，返回未实现。"""
```

### 输出（未配置官方通道时）
```json
{
  "source": "hkpl",
  "isbn": "9789...",
  "found": false,
  "message": "HKPL 未提供公开 JSON API。请使用开放数据集或联系馆方。"
}
```

### 合规
- 避免网页抓取；如需商用/批量访问，联系馆方或使用开放数据集并遵守许可

### Key / 注册信息
- 注册入口: https://www.hkpl.gov.hk/tc/services/library/library-catalogue
- 注册/费用: 面向公众的正式 JSON API 未公开；如需系统集成，通常需与馆方联系确认开放数据或合作接口；费用与权限以馆方为准。
- 不注册的区别: 无法调用正式 API；只能使用公开检索页面（不建议爬取）。
