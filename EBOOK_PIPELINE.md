# 電子書 Pipeline 設計文檔

完整參考：架構、schema 推導、運維歷史。操作摘要見 [`.claude/skills/ebook-pipeline/SKILL.md`](.claude/skills/ebook-pipeline/SKILL.md)。

---

## 1. 系統概覽

```
G:\我的雲端硬碟\資料\電子書\          ← Drive Desktop 自動同步雲端
├── 哲學\               ← 9 個主分類資料夾 + 子分類
│   ├── 黎明，西洋哲學史\
│   ├── 經典與解釋輯刊\
│   └── ...
├── 世界宗教\
├── 歷史學\
├── ... (共 9 大類)
└── _chunks\            ← parse 後的全文 (JSONL，每本一檔)
    └── {ebook_id}.jsonl

Supabase Postgres (free tier 500 MB)
├── ebooks               ← 1,309 本 metadata
└── ebook_chunks         ← 130K chunks，content 只存前 200 字預覽
```

**為什麼這樣設計**：Supabase free tier 硬性 500 MB 容量限制。1,309 本書的全文 ~375 MB + GIN 索引 ~200 MB 直接超出。把全文搬到本地 JSONL（藉由 Drive 自動雲端備份），DB 只留可索引的預覽 + metadata，是在 quota 限制下的最佳解。

---

## 2. 資料流

### 階段 1：Drive 掃描 → 重命名

```
G:/.../電子書/ 內亂七八糟的檔名
  └─→ local_drive_pipeline.py scan
       └─→ data/local_inventory.json (1309 entries)
            ↓ parse_drive_inventory.py 解析作者/書名 + 簡繁轉換 + 移除副書名
            ↓
       └─→ local_drive_pipeline.py rename
            └─→ 在地檔案改名為「作者，書名.副檔名」
```

### 階段 2：根目錄分類

```
電子書根目錄的 181 本未分類檔
  └─→ categorize_root_books.py (規則 + 人工 override)
       └─→ 移到對應主分類資料夾 + 更新 DB.category
```

### 階段 3：DB 入庫

```
data/local_inventory.json
  └─→ import_local_to_supabase.py
       └─→ ebooks table (1309 rows)
```

### 階段 4：解析 → chunks

```
ebooks where parsed_at IS NULL
  └─→ parse_worker.py run
       ├─ PDF: PyMuPDF, 每頁一 chunk, page_number 設值
       ├─ EPUB: ebooklib + bs4, 每章一 chunk, chapter_path 設值
       ├─ mobi/azw3/azw: 跳過 (純 Python 不支援)
       └─ 失敗: 寫入 parse_error
            ↓
       1. 全文寫到 G:/.../_chunks/{ebook_id}.jsonl
       2. 預覽 200 字 + metadata 寫到 ebook_chunks
            ↓
       data/parse_progress.txt 自動更新 [x]/[!]/[-]
```

### 階段 5：前端讀取 (⚠️ 待實作)

```
pages/ebook/[id].vue
  └─→ /api/ebooks/{id}?page=N
       └─→ 目前查空的 book_pages table ❌
       └─→ 應改成: 查 ebook_chunks 拿 metadata，再從本地 JSONL 拿全文
```

---

## 3. DB Schema 細節

### `ebooks`

```sql
CREATE TABLE ebooks (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  title       text UNIQUE NOT NULL,
  author      text,
  file_type   text CHECK (file_type IN ('pdf','epub','mobi','azw3','azw')),
  file_path   text,                    -- 本地完整路徑，用於 parse_worker 開檔
  category    text,                    -- 9 大主分類
  subcategory text,                    -- 子分類 (可 null)
  total_pages int,                     -- 暫未填，舊欄位
  total_chars int,                     -- 全文總字元數 (從 chunks 加總)
  publisher   text,                    -- 暫未填
  publication_year int,                -- 暫未填
  parsed_at   timestamptz,             -- NULL=未解析；NOT NULL=已成功
  chunk_count int,                     -- 解析後的 chunk 數
  parse_error text,                    -- 失敗原因 (NULL=無錯)
  created_at  timestamptz DEFAULT now()
);
```

**狀態語意**：
- `parsed_at IS NULL AND parse_error IS NULL` → 待處理
- `parsed_at NOT NULL` → 已完成
- `parse_error NOT NULL` → 失敗，可用 `--retry-errors` 重試

### `ebook_chunks`

```sql
CREATE TABLE ebook_chunks (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ebook_id     uuid REFERENCES ebooks(id) ON DELETE CASCADE,
  chunk_index  int NOT NULL,                          -- 順序 0,1,2...
  chunk_type   text CHECK (chunk_type IN ('page','chapter','section')),
  page_number  int,                                   -- PDF 用
  chapter_path text,                                  -- EPUB 用 (Part > Ch.3 > §2)
  content      text NOT NULL,                         -- ⚠️ 只有前 200 字！
  char_count   int,                                   -- 原始全文字元數
  created_at   timestamptz DEFAULT now()
);

CREATE INDEX idx_ebook_chunks_ebook_id_index ON ebook_chunks (ebook_id, chunk_index);
CREATE INDEX idx_ebook_chunks_fts ON ebook_chunks USING gin (to_tsvector('simple', content));
```

**為什麼 content 只存 200 字**：完整 130K chunk × 平均 3KB 中文 = 375 MB，加上 GIN 索引、row overhead，總共 735 MB 直接爆 free tier。預覽 200 字夠做 fuzzy filter (`WHERE content ILIKE %query%`)，全文交給本地 JSONL。

---

## 4. 本地 JSONL 結構

`G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl`，一行一 chunk：

```json
{"chunk_index": 0, "chunk_type": "page", "page_number": 1, "chapter_path": null, "content": "全頁文字..."}
{"chunk_index": 1, "chunk_type": "page", "page_number": 2, ...}
```

讀取範例（給前端 API 用）：
```ts
const fs = await import('fs/promises');
const lines = (await fs.readFile(`G:/我的雲端硬碟/資料/電子書/_chunks/${ebookId}.jsonl`, 'utf8')).split('\n').filter(Boolean);
const targetChunk = JSON.parse(lines[chunk_index]);
return targetChunk.content;
```

---

## 5. 解析規則 (parse_drive_inventory.py)

### 檔名格式優先序

1. **`經典與解釋NN，title`** 系列前綴 → 剝掉 `經典與解釋NN`，title 是後半
2. **`Complete/Collected Works of Author`**（英文）→ author = 後半
3. **`Title (Author) (z-lib.org)`** 或 `(Z-Library)` → 抓最後一個非系列標記的括號當 author
4. **`Title by Author`** → 切 by
5. **`作者，書名`**（全形/半形 comma）→ 切 comma
6. 都不符 → author=None, title=整個檔名

### 副書名處理

預設切 `：` 取前半當 short_title。但若同資料夾多本檔案的 short_title 相同（系列書如 `西洋哲學史：希臘`、`西洋哲學史：羅馬`），改用 full_title 保留副書名 — 否則會 collide 而無法區分。

### 簡繁轉換 (opencc s2tw)

s2tw 在某些字會誤轉，post-fix 字典 `TRAD_FIXES` 修正常見錯誤：
- `曆史 → 歷史`、`經曆 → 經歷`、`曆程 → 歷程` 等（s2tw 把 `历` 一律當 `曆`）
- `託爾斯泰 → 托爾斯泰`（人名音譯用 `托` 不用 `託`）
- `慄田 → 栗田`（日本姓氏 `栗`）

新發現誤轉時往這個字典加。

### 人工 author override

`TITLE_AUTHOR_OVERRIDES` 列舉作者沒辦法從檔名抓出來的書。例如：
- 摩門教全分類 → `約瑟‧斯密`
- 西洋哲學史系列 → `柯普斯登`
- 經典與解釋系列 → `劉小楓`
- 世界宗教史 → `任繼愈`
- 中亞文明史 → `聯合國教科文組織`

WebSearch 確認過 33 條。

---

## 6. 已知失敗模式

| 錯誤訊息 | 數量 | 解法 |
|---|---|---|
| `no extractable text` | 326 | 掃描版 PDF。需 OCR — Tesseract 或 Gemini Vision |
| `format not supported: mobi/azw3/azw` | 100 | 用 Calibre `ebook-convert` 轉 epub |
| `file not found` | 少 | 路徑被改但 DB 沒同步 — 重跑 scan + import |
| `canceling statement (57014)` | 偶發 | DB 寫入超時。`insert_chunks()` 已自動降階重試 (50→20→5→1) |
| `MuPDF cmsOpenProfileFromMem` | 警告，不致失敗 | PyMuPDF 對某些 PDF 色彩描述符警告，可忽略 |

---

## 7. 運維歷史關鍵節點 (參考)

1. 第一次 import 想直接灌 1018 本 → 跑成 2,298 筆合成資料（之前的 agent 用假資料填補）
2. 全清空，改用 Drive MCP 掃 9 大分類 + 子資料夾共 76 個 → 1,128 本真實資料
3. 發現本地 G: drive mount，省掉 Drive API 寫入認證 — 直接 rename + move 後讓 Drive Desktop 自動同步
4. 補上根目錄 181 本（+1,128 = 1,309 本）
5. parse worker 跑 1000 本後爆 IO budget；發現 GIN 索引每 INSERT 都更新很重 → DROP 後再跑剩下，最後重建
6. DB 達 735 MB 超 free tier → offload chunks 全文到本地 JSONL，DB 只留 200 字預覽 → 縮回 226 MB

---

## 8. 接手 agent 的建議起手式

1. `python scripts/parse_worker.py status` — 看當前數字
2. 讀 [`scripts/parse_worker.py`](scripts/parse_worker.py:85)（`insert_chunks` 函式 — 寫 JSONL + DB 邏輯都在這）
3. 讀 [`server/api/ebooks/[id].get.ts`](server/api/ebooks/[id].get.ts) — 改它接 `ebook_chunks` 是當前最高優先級
4. 改完用任一已 parsed 的 ebook id 測（例如 `004ab4d6-8201-4edd-be5a-30e64f4cceb0` = The Christian Tradition Vol. 4，474 chunks）

---

## 9. 環境變數 (`.env`)

```
SUPABASE_URL=https://vloqgautkahgmqcwgfuo.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sb_secret_...      # 寫入用
SUPABASE_ACCESS_TOKEN=sbp_...                # Management API (DDL/查詢用)
```

所有 Python 腳本都用 `_load_env()` 從這裡讀 — 永遠不要 hardcode。

---

## 10. 限制與待辦清單

### 必要
- [ ] **前端串 `ebook_chunks`** — 否則 1,309 本書點進去都看不到內容
- [ ] OCR 410 本掃描 PDF
- [ ] Calibre 轉 100 本 mobi/azw3
- [ ] 修 19 本沒抽到作者的（多是套裝合輯，可能維持 NULL）

### 可選
- [ ] 語意搜尋（embedding + pgvector）
- [ ] 全文搜尋介面（GIN 預覽 → JSONL 全文兩段式查詢）
- [ ] 失敗書批次重試 + 統計報表
- [ ] 上傳新書 UI（已有 `server/api/ebooks/upload.post.ts`，需驗證流程是否走新 pipeline）
