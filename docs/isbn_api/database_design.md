## 书籍数据存储与统计设计（EPUB/OPF 对齐，简化版）

本文件记录我们关于书籍元数据的存储结构、更新日志与查询统计的设计讨论与决策，并给出 Open Library dumps 的选择与导入 MongoDB 的参考流程。

### 目标
- 尽可能贴近 EPUB/OPF（Dublin Core）字段命名，降低互通成本
- 简化 schema，易于维护；保留来源与审计能力
- 支持 ISBN 精确检索与“书名+作者”文本检索
- 可统计每本书的查询次数（按日/周/月/总）

---

## 一、集合设计
- books（主集合，版次级记录；最小可用字段集合）
- book_update_logs（对书本记录的更新日志）
- book_query_stats（查询计数器，按周期）

### 1) books
对齐 Dublin Core 核心字段，并加入必要的运行/审计字段。

示例文档：
```json
{
  "_id": "9780134685991",
  "identifier": {
    "isbn_13": "9780134685991",
    "isbn_10": "0134685997",
    "other": []
  },
  "title": "Effective Java",
  "subtitle": null,
  "creators": [ { "name": "Joshua Bloch", "role": null } ],
  "contributors": [],
  "publisher": "Addison-Wesley",
  "published_date": "2018-01-06",
  "language": "en",
  "subjects": ["Programming"],
  "description": "...",
  "rights": null,
  "cover": { "url": "https://...", "thumbnail": "https://..." },
  "preview_urls": ["https://..."],
  "source": "google_books",
  "created_at": { "$date": "2025-08-01T10:00:00Z" },
  "updated_at": { "$date": "2025-08-01T10:00:00Z" }
}
```

索引建议：
```javascript
// ISBN 检索
db.books.createIndex({ "identifier.isbn_13": 1 }, { unique: true, sparse: true })
db.books.createIndex({ "identifier.isbn_10": 1 }, { sparse: true })

// 文本检索（书名/作者/主题）
db.books.createIndex({ title: "text", "creators.name": "text", subjects: "text" }, { default_language: "none" })

// 预览链接存在性/筛选（可选）
db.books.createIndex({ preview_urls: 1 })

db.books.createIndex({ source: 1 })
```

来源常量（与各 API 文档对齐）：
- `google_books`, `open_library`, `isbndb`, `worldcat`, `nlc_china`, `hkpl`, `ndl`, `kolisnet`, `british_library`, `loc`, `manual`

Notes:
- 书籍 `_id` 优先使用 ISBN-13；若无可用 ISBN-13，可使用 `isbn10:{value}` 或随机 `_id`，同时填充 `identifier`。
- 所有日期字段使用 ISO 8601 字符串；`created_at` 与 `updated_at` 使用 UTC 时间。

### 2) book_update_logs
记录每次对一本书的字段变更，包含来源与时间。

示例文档：
```json
{
  "_id": { "$oid": "..." },
  "book_id": "9780134685991",
  "changes": [
    { "field": "title", "old": "Effective Java 2nd", "new": "Effective Java" },
    { "field": "published_date", "old": "2008", "new": "2018-01-06" }
  ],
  "source": "isbndb",                // 或 "manual"
  "source_ref": "book:9780134685991", // 可选：来源侧主键
  "updated_at": { "$date": "2025-08-02T12:00:00Z" }
}
```

索引：
```javascript
db.book_update_logs.createIndex({ book_id: 1, updated_at: -1 })
db.book_update_logs.createIndex({ source: 1, updated_at: -1 })
```

写入约定：
- 对 `books` 有任何更新时，计算字段差异，写入一条日志并更新 `books.updated_at`。

### 3) book_query_stats
按周期累加的查询次数统计。

示例文档：
```json
{
  "_id": "9780134685991|day|2025-08-02",
  "book_id": "9780134685991",
  "period": "day",               // day | week | month | total
  "period_start": { "$date": "2025-08-02T00:00:00Z" },
  "count": 123
}
```

索引与约束：
```javascript
db.book_query_stats.createIndex({ book_id: 1, period: 1, period_start: 1 }, { unique: true })
db.book_query_stats.createIndex({ period: 1, period_start: 1 })
```

更新示例：
```javascript
// 按日
db.book_query_stats.updateOne(
  { book_id: "9780134685991", period: "day", period_start: new Date("2025-08-02T00:00:00Z") },
  { $inc: { count: 1 } },
  { upsert: true }
)
// 总计
db.book_query_stats.updateOne(
  { book_id: "9780134685991", period: "total", period_start: null },
  { $inc: { count: 1 } },
  { upsert: true }
)
```

周期规则：
- day: 当天 UTC 零点
- week: ISO 周一零点
- month: 当月第一天零点
- total: `period_start = null`

---

## 二、Open Library dumps 选择与导入

### Dump 类型与差异
- `ol_dump_editions_latest.txt.gz`：仅版次（含 ISBN），ISBN 检索的核心数据源。
- `ol_dump_works_latest.txt.gz`：作品层，利于“书名+作者”的聚合与标准化。
- `ol_dump_authors_latest.txt.gz`：作者信息与别名。
- `ol_dump_latest.txt.gz`：全量混合（需按 `type.key` 筛选）。
- MARC/MARCXML：编目原始格式，解析复杂，非必要不选。

### 下载建议
- 仅 ISBN 检索：下载 `editions`。
- 同时支持“书名+作者”：下载 `editions + works`（可选 `authors` 补充别名）。

### MongoDB 导入（示例）
若使用混合包，按类型筛选：
```bash
gzcat ol_dump_latest.txt.gz | jq -c 'select(.type.key=="/type/edition")' > editions.ndjson
gzcat ol_dump_latest.txt.gz | jq -c 'select(.type.key=="/type/work")' > works.ndjson
gzcat ol_dump_latest.txt.gz | jq -c 'select(.type.key=="/type/author")' > authors.ndjson
```
导入：
```bash
mongoimport --uri "mongodb://localhost:27017/openlib" \
  --collection editions --file editions.ndjson --numInsertionWorkers 4

mongoimport --uri "mongodb://localhost:27017/openlib" \
  --collection works --file works.ndjson --numInsertionWorkers 4
```

创建索引（用于内部清洗/比对）：
```javascript
db.editions.createIndex({ isbn_13: 1 })
db.editions.createIndex({ isbn_10: 1 })
db.works.createIndex({ title: "text", subject: "text" }, { default_language: "none" })
```

---

## 三、实现要点
- 标准化 ISBN：入库/比对前用 `app/utils/isbn.normalize_isbn` 规范化 ISBN-10/13。
- 首次来源：在 `books.source` 标注初始来源（`google_books/open_library/.../manual`）。
- 审计与回溯：所有字段变更写入 `book_update_logs`，包含来源与时间。
- 查询统计：每次命中后分别对 day/week/month/total 进行 `$inc`（upsert）。
- 简化优先：暂不引入复杂的去重/聚合机制，待真实数据与用例推动演进。
