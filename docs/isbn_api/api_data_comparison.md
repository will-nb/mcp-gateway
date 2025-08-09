## 各 ISBN 来源 API — 字段对照与取舍建议

对照对象：当前 `books` 主集合（EPUB/OPF/DC 子集）字段：
- identifier: { isbn_13, isbn_10, other[] }
- title, subtitle
- creators[{name, role}], contributors[]
- publisher, published_date (ISO 8601)
- language (ISO 639-1)
- subjects[]
- description, rights
- cover{ url, thumbnail }
- preview_urls[]
- source, created_at, updated_at

评价维度：
- 核心字段齐全性（ISBN/书名/作者/语言）
- 我们未保存但 API 提供的字段（含义与是否值得保存）

---

### Google Books
- 核心字段：
  - ISBN: 通常有（industryIdentifiers）；个别记录可能缺失
  - 书名: 有（volumeInfo.title）
  - 作者: 有（volumeInfo.authors[]）
  - 语言: 有（volumeInfo.language）
- 我们未保存的常见字段：
  - pageCount（页数）→ 值得保存（展示/过滤）
  - categories（分类标签）→ 已以 subjects[] 容纳（同义）
  - previewLink/infoLink/canonicalVolumeLink（预览与详情）→ 建议新增 `preview_urls`（数组）
  - ratingsCount/averageRating（评分）→ 可选；非核心
  - imageLinks 多尺寸（smallThumbnail/thumbnail/...）→ 目前 cover 支持 url/thumbnail，已足够，如需更多可扩展

### Open Library
- 核心字段：
  - ISBN: editions 中通常有；works/部分版本可能无
  - 书名: 有
  - 作者: 可能以引用（/authors/OL...A）形式，需要二次拉取；直接命名可能缺
  - 语言: 可能缺失或为代码数组
- 我们未保存的常见字段：
  - number_of_pages（页数）→ 值得保存
  - identifiers（OLID、OCLC、LCCN、Goodreads、LibraryThing 等）→ 建议扩展 `identifier.other` 为带命名空间的键值
  - covers（封面 id）→ 已可映射至 cover.url via covers 服务
  - publish_places/series/edition_name → 可选；非核心

### ISBNdb
- 核心字段：
  - ISBN: 有（isbn/isbn13）
  - 书名: 有
  - 作者: 有
  - 语言: 多数有（language），个别可能缺
- 我们未保存的常见字段：
  - subjects/genres/classification（如 Dewey）→ 可映射到 subjects；Dewey 可入 `identifier.other.dewey`
  - binding（装帧）、edition（版次）、dimensions（尺寸）→ 可选；非核心
  - overview（简介）→ 映射 `description`

### WorldCat (OCLC)
- 核心字段：
  - ISBN: 有（记录标识符中或显示字段）
  - 书名: 有
  - 作者: 有
  - 语言: 通常有（语言代码）
- 我们未保存的常见字段：
  - oclcNumber（OCLC 编号）→ 建议保存至 `identifier.other.oclc`
  - holdings（馆藏地/可借阅信息）→ 与检索目标无直接相关，暂不存
  - subject headings（主题词表，如 LCSH）→ 可并入 subjects
  - edition/format（载体/版次）→ 可选

### 国家图书馆联合目录（中国）
- 核心字段：视接口而定（暂无公开 JSON）；一般编目有 ISBN/题名/责任者/语种
- 我们未保存的常见字段（若接入 SRU/MARC）：
  - 中图法分类号（CLC）→ 可存 `identifier.other.clc`
  - 主题词（中文主题词表）→ 可并入 subjects
  - 馆藏/索书号 → 非核心，可不存

### 香港公共图书馆（HKPL）
- 核心字段：若有开放数据或 API，通常含 ISBN/题名/作者/语种
- 潜在未保存字段：馆藏状态、分馆位置 → 非核心

### 日本国立国会图书馆（NDL）
- 核心字段：
  - ISBN: 有
  - 书名: 有
  - 作者: 有
  - 语言: 有（ja 等）
- 我们未保存的常见字段：
  - NDL bib ID → 建议 `identifier.other.ndl`
  - 分类（NDC/NDLC）→ 可选；若做学科检索可存 `identifier.other.ndc/ndlc`
  - 系列信息/卷次 → 可选

### KOLIS-NET（韩国）
- 核心字段：通常具备 ISBN/题名/著者/语种
- 我们未保存的常见字段：
  - 분류기호（分类号）→ 可选（`identifier.other.kdc`）
  - 主题词 → 并入 subjects

### British Library（SRU）
- 核心字段：
  - ISBN: 有
  - 书名: 有
  - 作者: 有
  - 语言: 常见但并非总是显式字段（可从记录推断）
- 我们未保存的常见字段：
  - BL shelfmark/标识符 → 可存 `identifier.other.bl`
  - MARC/MODS 细节（载体、系列、卷次）→ 可选

### Library of Congress（LoC）
- 核心字段：
  - ISBN: 通过 `q=isbn:` 查询，但结果条目不一定显式回传 ISBN 字段（需用查询值回填）
  - 书名: 有
  - 作者: 有（creator）
  - 语言: 有（language）
- 我们未保存的常见字段：
  - LCCN/Call Number → 可存 `identifier.other.lccn`
  - subject_headings（LCSH）→ 并入 subjects
  - resource `id`（LoC 目录项 URL）→ 可存为 `identifier.other.loc_item`；此外其目录页 URL 可加入 `preview_urls`

---

## 结论：核心字段缺失风险与处理
- 低风险（基本齐全）：ISBNdb、WorldCat、NDL、KOLIS-NET、British Library
- 中风险：Google Books（个别记录缺 ISBN 或 authors）、LoC（结果不总是回显 ISBN）
- 注意项：Open Library `editions` 足够，但作者名常为引用，需要二次拉取；否则作者可能缺失
- 无公开稳定 JSON：NLC、HKPL（需接入正式 SRU/开放数据或合作接口）

通用处理：
- 若响应未回显 ISBN，使用请求参数中的规范化 ISBN 回填 `identifier.isbn_13/10`
- Open Library 作者名：可按需懒加载作者详情以补全 `creators.name`

---

## 建议的最小 schema 扩展（保持简洁前提下的高价值字段）
- page_count（Number）：多来源提供，常用展示/过滤
- preview_urls（String[]）：Google/OL/LoC 等提供的预览/目录链接（多来源合并）
- identifiers.other（Map 或 KV 数组）：统一承接跨源主键，便于去重/溯源
  - 建议命名空间：`oclc`, `ndl`, `bl`, `lccn`, `doi`, `olid`, `dewey`, `clc`, `kdc`, `loc_item`

示例（扩展后）：
```json
{
  "identifier": {
    "isbn_13": "9780134685991",
    "isbn_10": "0134685997",
    "other": { "oclc": "123456789", "olid": "OL123M" }
  },
  "page_count": 416,
  "preview_urls": ["https://books.google.com/...", "https://openlibrary.org/books/OL123M"]
}
```

---

## 记录取舍的理由
- 我们的主目标是“通过 ISBN 或 书名+作者 找到书”，因此：
  - 保留 ISBN/题名/作者/语言/主题（subjects）作为检索核心
  - `page_count`、`preview_url` 有明显的展示/交互价值
  - 各机构的权威标识符（OCLC/NDL/LCCN/OLID 等）可用于跨源对齐和质量提升，成本低、收益高
  - 馆藏/可借阅、分馆位置、装帧、尺寸等与检索关联弱，先不纳入主表
