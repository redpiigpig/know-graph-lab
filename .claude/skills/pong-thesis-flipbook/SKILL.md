---
name: pong-thesis-flipbook
description: 把龐牧師（或其他作者）的學位論文 PDF 做成「翻頁電子書」上架到 /pong-archive/writings — Gemini 結構化 OCR（標題層級、引文、腳註、自動章節目錄）+ R2（PDF 原檔 + 結構化 JSONL）+ 自動寫入 pong_writings + Vue 翻頁 reader（兩頁攤開／TOC 抽屜／鍵盤導航）。Use when 使用者上傳新一本學位論文 PDF 要做成 flipbook，或要重 OCR / 重排版既有 thesis，或要新增類似格式的長篇 monograph。
---

# pong-thesis-flipbook — 學位論文翻頁電子書 pipeline

把一份掃描版（或文字版）論文 PDF 變成 reader 可開的翻頁電子書，CSS 貼合原版 — 章節標題分大小、引文塊狀、腳註頁底。

## When to use

User 帶來一份／一批論文 PDF（學位論文、長篇 monograph、會議論文集），希望在 `/pong-archive/writings/<id>` 用翻頁電子書方式呈現，而不是現有的「純文字單欄 article」格式。典型訊號：

- 「把這份論文做成翻頁電子書」
- 「我想看到章節大小／腳註樣式」
- 「pdf 太爛要 OCR 出來重排版」
- 「跟 BD/MTh 一樣的格式幫我加一本」

## Architecture (一張圖)

```
PDF (in pong-archive/stores/...)
   │
   ├──► R2: pong-writings/{slug}.pdf            (原版 PDF，server-side proxy)
   │
   ├──► Gemini 2.5 Flash structured OCR
   │      ├─ outline[]  ←  [{level, text, page}]
   │      └─ pages[]    ←  [{page, blocks:[{type, text, level?, marker?}]}]
   │
   ├──► R2: pong-writings-pages/{slug}.jsonl.gz (一頁一行，blocks 陣列)
   │
   └──► pong_writings row
          - category='thesis'
          - pdf_r2_key, pages_r2_key, outline, total_pages
          - source_url='thesis-slug:{slug}'  ← 唯一鍵
                ↓
        /pong-archive/writings/{id}
                ↓
        [id].vue branches:
          category='thesis' && pdf_r2_key → <PongThesisFlipbook>
          otherwise → 現有純文字 article
```

## Key files

| 用途 | 路徑 |
|---|---|
| Pipeline script | [scripts/pong-archive/thesis_flipbook_ingest.py](../../../scripts/pong-archive/thesis_flipbook_ingest.py) |
| SQL migration | [database/pong-writings-thesis-flipbook.sql](../../../database/pong-writings-thesis-flipbook.sql) |
| Reader component | [components/pong-archive/PongThesisFlipbook.vue](../../../components/pong-archive/PongThesisFlipbook.vue) |
| Reader 頁面分支 | [pages/pong-archive/writings/[id].vue](../../../pages/pong-archive/writings/[id].vue) |
| API – metadata | [server/api/pong-writing/[id].get.js](../../../server/api/pong-writing/[id].get.js) |
| API – PDF proxy | [server/api/pong-writing/[id]/pdf.get.ts](../../../server/api/pong-writing/[id]/pdf.get.ts) |
| API – pages JSONL | [server/api/pong-writing/[id]/pages.get.ts](../../../server/api/pong-writing/[id]/pages.get.ts) |

## Schema (already applied)

`pong_writings` 在原本 schema 上加了 4 個欄位：

```sql
pdf_r2_key   TEXT     -- R2 key, 例 'pong-writings/pong-bd-thesis-1992.pdf'
pages_r2_key TEXT     -- R2 key, 例 'pong-writings-pages/pong-bd-thesis-1992.jsonl.gz'
outline      JSONB    -- [{level:1-4, text, page}] 自動抽出的章節目錄
total_pages  INTEGER
```

新書不需要再 ALTER；既有 schema 已就位。

## Pages JSONL shape

每行一頁，每頁含 blocks 陣列：

```json
{
  "page": 12,
  "blocks": [
    {"type": "chapter_title",     "level": 1, "text": "第二章 鄉土神學"},
    {"type": "section_title",     "level": 2, "text": "第一節 政治主題"},
    {"type": "subsection_title",  "level": 3, "text": "甲、臺灣歷史的詮釋"},
    {"type": "paragraph",         "text": "..."},
    {"type": "quote",             "text": "..."},
    {"type": "list_item",         "text": "1. ..."},
    {"type": "footnote",          "marker": "1", "text": "..."},
    {"type": "page_number",       "text": "12"}
  ]
}
```

Block types 對應 CSS class（看 [PongThesisFlipbook.vue](../../../components/pong-archive/PongThesisFlipbook.vue) `tfb-blk--*`）：

| type | tag | 樣式重點 |
|---|---|---|
| `chapter_title` | h1 | 1.6rem bold 置中，下方一條 1px 線 |
| `section_title` | h2 | 1.25rem bold |
| `subsection_title` (level=3) | h3 | 1.08rem |
| `subsection_title` (level=4) | h4 | 1.0rem |
| `paragraph` | p | `text-indent: 2em`, `text-align: justify`, line-height 2 |
| `quote` | p | `border-left: 3px solid`, 楷體系列, 縮排 |
| `list_item` | li | 縮排 2em，不帶 list-style |
| `footnote` | div (在 `.tfb-footnotes` 內) | 0.74rem，頁底加 border-top 分隔 |
| `page_number` | (不渲染在內文) | 由 reader 自己畫 |

## Pipeline 用法

### 加新一本 thesis

1. **把 PDF 放進 `pong-archive/stores/{some-folder}/`**（Drive 同步資料夾，不進 git）

2. **在 `scripts/pong-archive/thesis_flipbook_ingest.py` 的 `THESES` dict 加一筆**：

```python
THESES = {
  # ... existing ...
  "phd": {                                # short key for CLI --only
    "slug": "pong-phd-thesis-2020",       # 唯一識別碼，用在 R2 key + source_url
    "pdf":  "pong-archive/stores/.../thesis.pdf",  # 相對 repo root
    "title":            "<暫定佔位>",       # OCR 完後可能要請使用者改
    "title_en":         "Doctor of Philosophy Thesis",
    "published_date":   "2020-06-01",     # YYYY-MM-DD
    "date_approximate": True,
    "publication":      "<學校 / 系所>",
    "tags":             ["學位論文", "PhD", "..."],
    "sort_order_hint":  "thesis-phd",     # not yet used
  },
}
```

3. **跑 pipeline**：

```bash
# 看狀態
python scripts/pong-archive/thesis_flipbook_ingest.py status

# 完整跑（PDF → R2 → Gemini OCR → JSONL → R2 → DB）
python scripts/pong-archive/thesis_flipbook_ingest.py run --only phd

# 只重新 OCR（保留已上傳的 PDF）
python scripts/pong-archive/thesis_flipbook_ingest.py run --only phd --skip-pdf-upload

# 只更新 PDF + DB row，不重 OCR（OCR 已存好時換 PDF 用）
python scripts/pong-archive/thesis_flipbook_ingest.py run --only phd --skip-ocr
```

4. **確認標題**（重要）：Gemini 對封面頁的 OCR 經常不完整／不包含正式書名。跑完看 DB row 的 title 是不是 placeholder，找使用者確認後直接 PATCH：

```python
import os, requests
URL = os.environ['SUPABASE_URL']; KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
H = {"apikey":KEY,"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}
requests.patch(
    f'{URL}/rest/v1/pong_writings',
    headers=H,
    params={'source_url':'eq.thesis-slug:pong-phd-thesis-2020'},
    json={'title': '<正式書名>', 'publication': '<正式學校>'},
)
```

### 看單本書翻頁效果

http://localhost:3006/pong-archive/writings/<id>

- 雙頁攤開（左奇右偶，1+2 / 3+4 / 5+6…）
- ← / → 鍵盤翻頁；`Home`/`End` 跳首末頁
- 左側 TOC 抽屜可開關（從 `outline` 自動建）
- Top bar 有「原版」按鈕：開 server-proxy 的 PDF stream

### 重新 OCR

OCR 出來結構不準（標題層級被當段落、引文沒抽出、腳註漏掉），可以單獨重 OCR：

```bash
python scripts/pong-archive/thesis_flipbook_ingest.py run --only bd --skip-pdf-upload
```

OCR 是非破壞的 — 重跑會覆蓋 R2 pages JSONL + DB 的 outline / total_pages，PDF 本體不動。

## OCR prompt 設計重點

prompt 在 [thesis_flipbook_ingest.py](../../../scripts/pong-archive/thesis_flipbook_ingest.py) 內的 `PROMPT` 常數。關鍵設計：

- **要求繁體中文**：Gemini OCR 對簡體版掃描檔有時會 OCR 成簡體，我們直接在 prompt 裡要它「若 OCR 看到簡體，請靜默轉繁體」
- **block types 嚴格定義**：列出 8 種 type（chapter_title / section_title / subsection_title / paragraph / quote / list_item / footnote / page_number），避免 model 自己創 type
- **level 強制 1-4**：對應 reader 4 級標題大小
- **footnote 必須帶 marker**：方便未來做點擊跳 footnote
- **同時回傳 outline**：自動章節目錄（PDF 沒有 outline 時的 fallback）

Response 用 `response_mime_type='application/json' + response_schema=PAGES_SCHEMA`（structured output），保證 JSON valid。

## 已知陷阱

- **OCR 對封面頁常常空白**：封面通常只有大字書名 + 學校 logo，Gemini 容易直接 skip 不抽，或者抽得很短。**請務必 OCR 完後人工確認 DB 的 title 是否正確**。
- **掃描歪斜會降低層級識別準確度**：subsection_title L3 vs L4 對 Gemini 是視覺判斷，掃描歪斜時可能 level 全部變 3。reader 對 L3/L4 樣式差異小，不致命，但若使用者明顯不滿意，可在 prompt 加更具體的層級規則。
- **R2 沒有 public CDN**：PDF 必須走 server proxy `/api/pong-writing/{id}/pdf`，不能用 R2 直連 URL 嵌 iframe（沒 public domain）。`pages.get.ts` 也是 server-side 解 gzip 後回 JSON。
- **bucket 容量 9 GB 上限**：依 [`upload_chunks_to_r2.py`](../../../scripts/upload_chunks_to_r2.py) 的 SAFETY_CEILING_GB。論文 PDF 通常 20-50MB，加 OCR JSONL 30-100KB，每本約 50MB。10 本以內安全。
- **`source_url='thesis-slug:<slug>'` 是唯一鍵**：upsert 靠這個欄位識別「已存在」。換 slug 等於開新 row，舊 row 不會被清掉 — 換 slug 前手動 DELETE 舊 row。
- **OCR 時間**：Gemini 2.5 Flash 大約 4 秒/頁。BD 48 頁約 3 分鐘；MTh 91 頁約 6-7 分鐘；中型論文 200 頁 ~15 分鐘。Gemini Files API 上限 1000 頁，所以即使更厚也撐得住。
- **PDF >50MB 走不了 Gemini Files API**：BD/MTh 都在 50MB 以下沒事。若要處理 >50MB 的論文，得改走 Haiku image-batch 路徑（參考 [`ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) `_haiku_ocr_book`）— 目前 thesis pipeline 還沒接這條 fallback，必要時補。

## Reader 行為 (`PongThesisFlipbook.vue`)

- **2-page spread**：左頁=奇數頁、右頁=偶數頁，與印刷裝訂一致（書打開來左奇右偶，pages 1+2 / 3+4…）
- **TOC 抽屜**：左側 280px wide，分 L1/L2/L3/L4 縮排與字體大小，點擊跳對應頁
- **鍵盤**：← / → / PageUp / PageDown / Home / End
- **頁面邊緣 hot zone**：滑鼠靠近頁邊會有微弱 hover 高光，點擊翻頁
- **全螢幕**：頂部按鈕，`position: fixed; inset: 0`，按 ESC 不自動退出（按鈕變「退出」）
- **原版 PDF**：頂部「原版」按鈕，新分頁開 `/api/pong-writing/{id}/pdf`（server stream，無 download 預設）

## Anti-patterns (don't do this)

- **不要把 OCR'd thesis 內文貼進 chat**：論文是作者的著作 — pipeline 設計上 OCR'd text 只進 R2 / DB / browser，不該 dump 到 console output 或 chat。即使是要 debug，也最多印「page X 有 Y 個 block」級別的 metadata。
- **不要重複跑 PDF upload**：`upload_pdf()` 已 idempotent（同 size 直接 skip），但白白把 18MB / 41MB 推上 R2 兩三次依然在浪費頻寬。要重 OCR 時記得加 `--skip-pdf-upload`。
- **不要把 thesis 內容塞回 `content` 欄位**：[id].vue 的純文字 article 分支會把 content 直接顯示，可能造成 thesis 變成「上面 flipbook、下面又一份純文字」雙重顯示。thesis row 的 content 欄位保持 NULL。
- **不要在 reader 直接用 PDF.js 渲染**：使用者明確選擇 OCR + HTML 重排路徑（2026-05-22）。PDF.js 路徑會放棄所有 CSS 重排能力。原版 PDF 透過頂部「原版」按鈕另開分頁就好。
- **不要在 SKILL 加新 thesis 時忘了 commit migration SQL**：schema 已套用，但 sql 檔本身要在 repo 內，未來 setup 新環境才能重現。
