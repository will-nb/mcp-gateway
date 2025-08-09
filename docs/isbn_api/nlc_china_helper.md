## 国家图书馆联合目录（中国） helper.py 开发说明

- 参考入口: http://opac.nlc.cn/F/?func=file&file_name=find-b （传统馆藏检索入口）
- 适用范围: 中国大陆出版物
- 认证/Key: 通常无需；但可能受 IP 白名单/访问频率限制
- 费用/配额: 免费（面向机构/图书馆服务为主）
- 商用: 未提供面向公众的正式商业 API；生产用途需与馆方沟通并签署协议

### 重要说明
- 官方未提供稳定公开的 JSON API；常见实现为 Aleph/OPAC 页面或 SRU/Z39.50 协议。
- 建议优先采用 SRU（如有开放）或通过合作渠道获取正式接口。直接抓取 OPAC HTML 不建议在生产中使用。

### 建议的 helper 接口（占位）
```python
from typing import Any, Dict

def fetch_by_isbn(isbn: str, *, timeout: float = 10.0) -> Dict[str, Any]:
    """占位：若无官方 SRU/REST，不进行自动抓取，直接返回未实现状态。"""
```

### 输出（当未配置官方通道时）
```json
{
  "source": "nlc_china",
  "isbn": "9787...",
  "found": false,
  "message": "未配置官方 API 通道（SRU/JSON）。请联系馆方或通过合作接口接入。"
}
```

### 合规
- 不建议抓取 HTML；请走正式开放接口或签约渠道；遵守馆方条款与频控
