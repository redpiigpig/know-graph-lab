---
name: ebook-pipeline
description: Operate the Know-Graph-Lab ebook pipeline end-to-end. Use when working on parsing books from Drive into Supabase, OCR'ing scanned PDFs (daily Gemini scheduler), back-filling DB previews from local JSONL, standardizing books (EPUB + PDF) into reader-ready markdown, or wiring the reader to chunks. The single hub for everything book-content-related.
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# Ebook Pipeline Skill

End-to-end pipeline from Drive folder → reader at `/ebook/[id]`. Single SKILL covers ingest, parse, OCR, standardize, DB back-fill, and reader-side features.

## Current state (snapshot 2026-05-21 08:15)

| | 數量 |
|---|---|
| Total ebooks | **1,552** (5/20 ingest 10 本新書) |
| Parsed | ~1,470 |
| **OCR queue（皆 >50MB 需 Haiku）** | **82** |
| Permanent OCR fail | 0 |
| EPUB standardize → markdown | 543 ✅ |
| PDF Plan A | 437 ✅ |
| PDF Plan B v0 | 152 ✅ |

### 進行中的 OCR run（會跨 session 持續）

- **腳本：** `scripts/_haiku_autorestart.sh` — 自動重啟 wrapper，最多 15 iterations 後 exit
- **log：** `scripts/logs/ocr_haiku_2026-05-19_v2.log`（continued）+ `ocr_haiku_2026-05-20.log`
- **檢查進度：** `grep -c '✓ Haiku' scripts/logs/ocr_haiku_2026-05-19_v2.log`
- **新 session 接續方法：**
  ```bash
  # 1. 確認 Anthropic OK + queue 還有書
  python -X utf8 -c "import os, json; from dotenv import load_dotenv; load_dotenv(); import anthropic, requests; from pathlib import Path; cred=json.loads(Path(os.environ['USERPROFILE']+'/.claude/.credentials.json').read_text(encoding='utf-8')); c=anthropic.Anthropic(auth_token=cred['claudeAiOauth']['accessToken'],timeout=15); print('Anthropic OK' if not c.messages.create(model='claude-haiku-4-5-20251001',max_tokens=5,messages=[{'role':'user','content':'hi'}]).usage else 'OK')"

  # 2. 啟動 wrapper（背景）
  bash scripts/_haiku_autorestart.sh 2>&1 | tee -a scripts/logs/ocr_haiku_2026-05-20.log

  # 3. Re-arm Monitor 抓書級事件
  # Monitor tool: tail -F log | grep -E "✓ Haiku|⛔|Queue empty"
  ```

### 已知狀況（5/20-5/21）

- **rate limit 累計性卡死**：Anthropic 帳號級 burst rate limit，跑 ~6 本後就連續 429，wrapper 2-strike pause + 重啟 + 又 429...iteration 燒得快。實際 ~5 本/天可完成
- **OAuth token 有效期 ~8 小時** → long-running python 緩存舊 token 後續全 401。要 kill python 讓 wrapper 重起讀新 token
- **網路抖動** → Connection error + Drive open fail 雜訊不斷
- **Anthropic content filter false positive**：知識份子論、道教史已永久 marked Haiku-OCR fail（沒進當前 queue）

### 本輪 (5/19-5/21) 完成清單

| # | 書 | 大小 | 頁數 | 用時 |
|---|---|---|---|---|
| 1 | 神話學 (Lévi-Strauss) | 51.7MB | 445 | 98m |
| 2 | 人類時代 | 52.0MB | 178 | 33.5m |
| 3 | 伊朗伊斯蘭革命及其世界影響 | 52.3MB | 229 | 50m |
| 4 | 我們世界的歷史 第 5 版 卷 3 | 59.3MB | 214 | 51.5m |
| 5 | 饒宗頤 二十世紀學術文集 卷 5 | 60.7MB | 212 | 45.5m |
| 6 | 從蒙古到大清 | 65.4MB | 434 | 39m |
| 7 | (悄悄完成沒抓到事件，~5/20 晚上) | ? | ? | ? |

### 10 大分類書數（5/20 ingest 後）

| 分類 | 書數 | 分類 | 書數 |
|---|---|---|---|
| 歷史學 | 468 | 社會政治學 | 141 |
| 世界宗教 | 372 | 宗教學 | 105 |
| 哲學 | 219 | 人類生物學 | 68 |
| 神學 ★ | 60 | 文學 | 58 |
| 自然科學 | 31 | 心理學 | 30 |

10 大分類書數（reclassification 後）：

| 分類 | 書數 | 分類 | 書數 |
|---|---|---|---|
| 歷史學 | 466 | 社會政治學 | 141 |
| 世界宗教 | 372 | 宗教學 | 105 |
| 哲學 | 218 | 人類生物學 | 68 |
| 文學 | 58 | 神學 ★ 2026-05-18 新增 | 53 |
| 自然科學 | 31 | 心理學 | 30 |

---

## 流程 — 新書 vs 舊書

### 新書（daily ingest 自動跑）

`scripts/run_ocr_daily.bat` 跑完整 5-step：

```
ingest_new_books → parse_worker → ocr_with_gemini → detect_set_volumes → split_ebook_set
```

**每日 3 次自動偵測 z-lib/ drop**（user 規則 2026-05-20）：
- **10:00 / 14:00 / 18:00 Taipei** — Windows Task Scheduler 觸發
- 對話中 Claude 啟動或被詢問「z-lib」「新書」「ingest」時，**主動跑 `python scripts/ingest_new_books.py status`** 看看有沒有未處理的 drop
- 若 status 顯示 >0 本待 ingest，立即跑 `python scripts/ingest_new_books.py run`

排程設置：
```powershell
schtasks /create /tn "KGLab-OCR-Daily-10" /tr "C:\Users\user\Desktop\know-graph-lab\scripts\run_ocr_daily.bat" /sc daily /st 10:00 /f
schtasks /create /tn "KGLab-OCR-Daily-14" /tr "C:\Users\user\Desktop\know-graph-lab\scripts\run_ocr_daily.bat" /sc daily /st 14:00 /f
schtasks /create /tn "KGLab-OCR-Daily-18" /tr "C:\Users\user\Desktop\know-graph-lab\scripts\run_ocr_daily.bat" /sc daily /st 18:00 /f
```
3 個 task 同跑 same bat，step 1 ingest 對空 z-lib 是 no-op 安全。舊的 `KGLab-OCR-Daily` (16:00) / `-08` / `-22` 已刪。

Standardize 不在 daily bat 裡 — parse/OCR 落地後 chunk_type 還是 `page` (PDF) 或 raw (EPUB)。**新書 standardize 需手動觸發**（見 Workflow B）。已知 TODO：把 standardize 鉤進 daily bat。

唯一例外是 **套書 auto-split** — `standardize_ebook.py` 在 EPUB 完成後自動呼叫 `detect_set_volumes` + `split_ebook_set`，所以 standardize-ed 套書自動拆成多個 child rows。

### 舊書（一次性 batch）

見 Workflow B 的 commands。EPUB 已全跑完；PDF Plan A 全跑完；Plan B v0 跑完 152/437；剩餘 ~285 本待 Plan B v1（無 TOC bookmark）。

---

## Pipeline scripts (all in `scripts/`)

| Script | Phase | Purpose |
|---|---|---|
| `ingest_new_books.py` | 1 — ingest (**daily**) | Watches `z-lib/`. Parses filename, classifies via Gemini (+ keyword fallback), inserts ebooks row, moves file to `G:/.../電子書/{category}/`. Auto-deletes Drive dupes. See Workflow D |
| `parse_worker.py` | 2 — parse | Main parser (PyMuPDF + ebooklib). `init` / `run [--limit N] [--retry-errors]` / `status` |
| `ocr_with_gemini.py` | 3 — OCR | Gemini Vision for scanned PDFs. 4 rotating keys; pushes JSONL to R2 inline; auto-Haiku-fallback on Gemini quota / >1000 pages. `--engine {gemini,haiku}`, `--book <id>` / `--exclude <id>` repeatable. Exits code 2 on daily quota |
| `run_ocr_daily.bat` | orchestrator | Windows daily runner — 5-step: ingest → parse → OCR → detect_set_volumes → split_ebook_set. Logs to `scripts/logs/ocr_YYYY-MM-DD.log` |
| `standardize_ebook.py` | 4 — standardize | EPUB → reader-ready markdown chunks. Auto-triggers 套書 split on title match. See Workflow B |
| `standardize_pdf_lite.py` | 4 — standardize | PDF Plan A polish (s2tw + spacing collapse + publisher metadata). `page_number` preserved |
| `standardize_pdf.py` | 4 — standardize | PDF Plan B v0 TOC-driven re-chunking. Skips books with annotations / already-chunked / page-level TOC |
| `enrich_book_metadata.py` | 4b — backfill | Online lookup (Google Books → Open Library) for null publisher/year. Respects `metadata_locked` |
| `detect_set_volumes.py` | 4c — 套書 prep | Haiku detects volume boundaries in chunks → writes `volume` field or `NOT_A_SET_MARKER` |
| `split_ebook_set.py` | 4d — 套書 split | Split multi-volume ebook into one row per volume. Idempotent (SPLIT_MARKER / annotations guard). Children get `parse_error='split from set; do not re-standardize'` |
| `split_oversized_pdf_by_toc.py` | 3b — OCR rescue | Physically split a multi-volume PDF into per-volume PDFs using level-1 TOC bookmarks. For 套書 failing BOTH Gemini (>1000 pages) AND Haiku (content-filter). Children re-enter OCR queue |
| `resplit_giant_chunks.py` | 4e — chunk refinement | Break oversized chunks (>400K chars) by internal `##`/`###` headings. Annotation guard |
| `repopulate_chunk_previews.py` | 5 — DB | Back-fill `ebook_chunks` previews from local JSONL. `run` / `retry-failed` / `status` |
| `upload_chunks_to_r2.py` | 5 — R2 | One-shot bulk uploader for JSONL not yet on R2 |

## DB schema

```sql
ebooks (
  id uuid PK, title, author, file_type,
  file_path,                    -- absolute path to local Drive file
  category, subcategory,         -- 9 main categories, free-form subcategory
  total_pages, total_chars, chunk_count,
  parsed_at,                     -- NULL = not yet parsed
  parse_error,                   -- NULL on success; preserved on transient fail for retry
  book_id,                       -- nullable FK to books table (for excerpt linkage)
  cleaned_at,
  subtitle, original_title, author_en, translator,
  publisher, publication_year, original_publish_year, original_author,
  metadata_locked                -- blocks enrich_book_metadata writes
)

ebook_chunks (
  id uuid PK, ebook_id FK,
  chunk_index INT, chunk_type,   -- 'page' for PDF Plan A, 'chapter' for EPUB / PDF Plan B
  page_number, chapter_path,
  content TEXT,                  -- ⚠ first 200 chars only (preview); full text in JSONL
  char_count
)
GIN index on to_tsvector('simple', content)

annotations (
  id uuid PK, ebook_id FK, chunk_index,
  selected_text, context_before, context_after,
  note, color,                   -- yellow|green|blue|pink
  excerpt_id FK?,
  created_at
)
```

## Drive 分類結構（10 大頂層 + subcategory + 套書子資料夾）

頂層 10 個分類資料夾在 `G:/我的雲端硬碟/資料/電子書/`，最新書數見 [Current state](#current-state) 表。

### 一覽

| 分類 | 收什麼 | 不收什麼（去看別處） |
|---|---|---|
| **哲學** | 哲學家本人著作 / 哲學流派研究 / 形上學 / 倫理學 / 邏輯 / 認識論 / 美學 / 科學哲學 / 宗教哲學書（看哲學家視角分析宗教） | 神話學 → 宗教學；神學家用神學語言寫的書 → 神學 |
| **神學** | 系統神學 / 教父原典英譯（Schaff、IVP ACCS）/ 信理神學 / 神學家本人著作（Barth 教會教義學、Rahner、Moltmann、Aquinas Summa）/ 教父研究 monograph / 教義論述 / 護教學 | 基督教史／教會史 / 神學家傳記 → 世界宗教/基督教 |
| **世界宗教** | 特定宗教自身的：經典原文 / 教義教理 / 神學家傳記 / 教會史 / 該宗教的歷史敘述 / 該宗教的祈禱書與禮儀 | 跨宗教比較 → 宗教學；學術系統神學 → 神學 |
| **宗教學** | 跨宗教研究（多宗教比較對話）/ 神話學（Eliade／Frazer／Durkheim 等大家）/ 宗教社會學 / 宗教心理學 / 宗教現象學 / 宗教史（不專屬一宗教） | 單一宗教的研究 → 世界宗教/{該宗教} |
| **歷史學** | 通史 / 斷代史 / 地區史 / 戰爭史 / 革命史 / 一般人物傳記（非宗教非哲學人物）/ 史學理論 / 史料原典 | 思想史／政治史 → 哲學或社會政治學；宗教史 → 看是否跨宗教 |
| **社會政治學** | 政治學 / 政治哲學 / 經濟學 / 社會學 / 法律 / 國際關係 / 性學 / 知識社會學 / 政治理論 / 政治觀念史（Voegelin 等） | 純哲學書 → 哲學；社會宗教學 → 宗教學 |
| **人類生物學** | 人類學 / 民族誌 / 考古學 / 人類起源與進化 / 生物人類學 / 體質人類學 / 文化人類學 / 語言學 / 「大歷史」流派書（Sapiens 等） | 純動植物生物學 → 自然科學；純語言哲學 → 哲學 |
| **心理學** | 心理學 / 精神分析 / 認知科學 / 心理治療 / 生死學 / Yalom 系列 / Frankl 系列 | 宗教心理學 → 宗教學 |
| **文學** | 小說 / 詩歌 / 散文 / 戲劇 / 文學評論 / 文學史 | 文化研究 → 看內容；翻譯文學原典 → 看作者所屬類 |
| **自然科學** | 物理 / 化學 / 生物學 / 地球科學 / 氣候 / 天文 / 數學 / 統計 / 演化生物學 / 科學史 | 科學哲學 → 哲學；「大歷史」流派 → 人類生物學 |

### 神學 vs 世界宗教 vs 宗教學 — 三類最常混淆的判準

**核心原則**：分類看「**這本書的書寫位置／框架**」，不是「題材碰到什麼宗教」。

| 內容性質 | 分類 | 範例 |
|---|---|---|
| 教父原典英譯／中譯（Patrologia Graeca/Latina 系列原文翻譯） | **神學** | Schaff NPNF/ANF、IVP ACCS 27 冊、《使徒教父著作》、Sarug Homilies、Babai Union |
| 系統神學論述（從信仰內部建構神學體系） | **神學** | 《基督教神學》《基督教神學導論》《信理神學》6 卷、Barth《教會教義學》、Aquinas《神學大全》/《駁異大全》、Rahner |
| 神學家本人的神學論述（不是傳記） | **神學** | Moltmann《被釘十字架的上帝》、Kung《論基督徒》、Bonhoeffer《獄中書簡》 |
| 教義專題研究（基督論／三一論／聖靈論／末世論的學術 monograph） | **神學** | Grillmeier《Christ in Christian Tradition》、Council of Chalcedon Re-Examined、Monophysite Movement、Cyril Christological Controversy |
| **基督教史／教會史／宗教改革史** | **世界宗教/基督教** | 《基督教史》《亞洲基督教史》《俄國教會史》《1550 年前的中國基督教史》、《宗教改革史》、《歷代教宗簡史》 |
| **神學家／聖人傳記** | **世界宗教/基督教** | Bonhoeffer 傳記、奧古斯丁傳、追尋之旅（奧古斯丁）、波納文圖拉傳 |
| 該宗教自身禮儀／經典／祈禱書／信經中譯 | **世界宗教/{該宗教}** | 聖經中譯本、可蘭經、佛經、Avesta、巴哈伊經典 |
| 該宗教的史 — 佛教史／伊斯蘭教史／道教史／猶太人三千年 | **世界宗教/{該宗教}** | 《佛教史》《伊斯蘭世界史》《猶太文化史》 |
| 跨宗教研究 — 兩個以上宗教並列比較／對話／法律比較 | **宗教學** | 《聖經與古蘭經》、《A state of mixture - Christians, Zoroastrians》、《Judging in Islamic, Jewish and Zoroastrian Legal Traditions》、《The Age of Faith - Medieval Christian Islamic Judaic Civilization》 |
| 宗教社會學 / 宗教心理學 / 宗教現象學 / 神話學 / 宗教比較 | **宗教學** | Eliade《神聖與世俗》、Durkheim《宗教生活的基本形式》、Frazer《金枝》、James《宗教經驗之種種》、Berger《神聖的帷幕》 |

### 邊界情況的快速判斷

| 情境 | 怎麼判 |
|---|---|
| 標題含「神學」但作者是哲學家（康德的神學／海德格爾與神學） | → **哲學**（看的是哲學家視角，不是教內神學） |
| 標題含「哲學」但內容是某宗教教義（伊斯蘭哲學／印度哲學） | 看書寫框架：學術研究 → 哲學；教內教義 → 世界宗教/{宗教} |
| 「宗教與資本主義／新教倫理」類 | → **社會政治學/政治經濟社會學**（Weber、Sombart） |
| 性別／性學／身體史（Foucault 性經驗史） | → **社會政治學/性學**（不要因「史」字就抓到歷史學） |
| 政治思想史／政治觀念史（Voegelin） | → **社會政治學/政治學**（不是歷史學） |
| 「大歷史」「人類大歷史」「Big History」（Sapiens、Yuval Harari） | → **人類生物學/人類大歷史**（user 偏好） |
| 中國思想史／儒家／道家哲學分析 | → **哲學/中國思想史** |
| 中國宗教綜論／中國民間信仰／中國五大宗教 | → **世界宗教/東亞宗教** |
| 教父研究 monograph vs 教父傳記 | monograph（教義／思想研究）→ 神學；傳記（生平故事）→ 世界宗教/基督教 |

### 套書子資料夾規則

若 ingest 進來的是套書／系列（例如 Schaff 38 卷、Aquinas《神學大全》18 冊、IVP ACCS 27 冊），**在分類資料夾內建子資料夾集中管理**，不要平鋪。範例：

```
G:/我的雲端硬碟/資料/電子書/神學/
  Schaff - Ante-Nicene Fathers (10 vols)/        anf01.epub … anf10.epub
  Schaff - Nicene and Post-Nicene Fathers Series 1 (Augustine and Chrysostom)/   npnf101…114
  Schaff - Nicene and Post-Nicene Fathers Series 2 (14 vols)/   npnf201…214
  Aquinas - Summa Theologica (神學大全 18 冊)/   ← ziliaozhan TODO 候選
  IVP Ancient Christian Commentary on Scripture (27 冊)/   ← ziliaozhan TODO 候選
```

子資料夾命名 `{編者／出版社} - {系列名} ({N} vols)`。`ebooks.subcategory` 同步存子資料夾名。

> ⚠ **移動 Drive 檔案後，必須 UPDATE `ebooks.file_path`** 指向新位置，否則 reader 找不到書。範例腳本：`scripts/_organize_schaff_to_folders.py`（移動 + DB 同步一條龍）。

### 已存在的 subcategory 命名慣例

每類目前實際使用中的 subcategory（新書 ingest 時優先沿用以保持一致）：

| 分類 | 常見 subcategory |
|---|---|
| 哲學 | 近代哲學 / 哲學原典 / 經典與解釋輯刊 / 中國思想史 / 哲學通史 / 當代哲學 / 古希臘哲學 / 東方哲學 / 政治哲學 |
| 神學 | Schaff - Ante-Nicene Fathers (10 vols) / Schaff - NPNF Series 1 / Schaff - NPNF Series 2 / 教父原典 / 系統神學 / 教父研究 / 神學家研究 / 神學專題 / 靈修神學 |
| 世界宗教 | 基督教 / 猶太教 / 東亞宗教 / 波斯宗教 / 佛教 / 伊斯蘭教 / 其他宗教 / 印度教 / 摩門教 |
| 宗教學 | 神話學 / 宗教史 / 宗教對話 / World Religions系列 / 教會史 / 宗教社會學 |
| 歷史學 | 東方界域史 / 西方界域史 / 中央界域史 / 亞太界域史 / 美州界域史 / 全球通史 / 史料原典 / 近代史 / 史學理論 |
| 社會政治學 | 政治學 / 政治經濟社會學 / 資本主義-社會主義 / 知識社會學 / 社會學 / 性學 / 名家作品 / 國際關係 |
| 人類生物學 | 人類大歷史 / 人類文化-語言學 / 人類起源與進化史 / 生物學 |
| 心理學 | 生死學 / 認知科學 |
| 文學 | 小說 / 文學評論 |
| 自然科學 | (尚無 subcategory) |

## Storage layout

- **Local JSONL** (source of truth): `G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl`
  - One JSON per line: `{chunk_index, chunk_type, page_number, page_range?, chapter_path, volume?, format?, content}`
  - G: is Drive sync mount → auto-backed up to Drive cloud
  - Configured via `EBOOK_CHUNKS_DIR` in `.env` (consumed by `nuxt.config.ts` → `runtimeConfig.ebookChunksDir`)
- **R2 mirror**: `r2://{R2_BUCKET}/ebook-chunks/{ebook_id}.jsonl.gz` (gzipped). Read at runtime by `server/utils/ebook-chunks.ts` `loadLines()` when local file unreachable (production, Zeabur)
- **DB previews**: `ebook_chunks.content` first 200 chars only — for fast SQL `ilike` full-text search

## Critical constraints

- **Supabase free tier 500 MB** — never reload full chunk text into DB. JSONL-on-disk + 200-char preview to DB.
- **Supabase IO budget on free tier** — bulk inserts (>1K/s) hit `57014` "canceling statement". `parse_worker.py`, `repopulate_chunk_previews.py`, `standardize_ebook.py`, `split_ebook_set.py` all use **adaptive batch sizes** (100 → 50 → 20 → 5 → 1).
- **No Supabase Storage bucket** — user explicitly forbade it. Local files only.
- **Service-role key in `.env`** — never hardcode.
- **PostgREST 1000-row default cap** — server endpoints that list ebooks use `.range(0, 1999)`.

---

## Workflow A — OCR scanned PDFs

[`scripts/ocr_with_gemini.py`](../../../scripts/ocr_with_gemini.py) sends each scanned PDF to Gemini Vision via the Files API and gets back structured JSON `{pages: [{page, text}]}`. After OCR: write JSONL to local `_chunks/` → push gzipped to R2 → insert 200-char preview rows → mark `ebooks.parsed_at` + clear `parse_error`.

**Rate limits**: Gemini 2.5 Flash free tier — 10 RPM, 250 RPD, 250K TPM. Default `--rpm 8`. Daily quota resets at midnight Pacific (≈ Taipei 16:00).

### Engine policy

**Default: Gemini.** 4 rotating Google API keys. 503 = transient (does NOT overwrite `parse_error`; next run retries); 429 = daily quota exhausted (script exits code 2).

**Haiku Vision: ONLY when user explicitly orders.** Always one book at a time — bulk Haiku exhausted Max subscription with zero books completed (2026-05-07).

```bash
python scripts/ocr_with_gemini.py run --engine haiku --book <id>
```

Auth via `ANTHROPIC_API_KEY` or `~/.claude/.credentials.json` OAuth token. **2-strike quota auto-pause** — after 2 consecutive 429/rate_limit/quota errors, loop breaks (user rule).

**Automatic fallback (Gemini → Haiku) wired** for:
- Gemini hits 429 mid-run → remaining books switch to Haiku for rest of run
- Gemini rejects with `>1000 pages` → that single book auto-falls-back to Haiku inline
- File > 50 MB → routes to Haiku directly

### Scheduler

Bat is a **5-step runner**: `ingest_new_books → parse_worker → ocr_with_gemini → detect_set_volumes → split_ebook_set`. Steps 4a/4b idempotent (no-op when no 套書 pending).

| Component | Path |
|---|---|
| Bat runner | [`scripts/run_ocr_daily.bat`](../../../scripts/run_ocr_daily.bat) — logs to `scripts/logs/ocr_YYYY-MM-DD.log` |
| Toast helper | [`scripts/notify.ps1`](../../../scripts/notify.ps1) — fires at start + on 429 |
| Windows Task | `KGLab-OCR-Daily` |
| Trigger | **Daily 16:00** Taipei time |
| Behavior | `WakeToRun` + `StartWhenAvailable` — wakes from sleep, catches up if missed |
| Cap | 12-hour `ExecutionTimeLimit` |

Python hardcoded to `C:\Users\user\AppData\Local\Python\bin\python.exe` (system PATH resolves to Whisper venv missing ebooklib/fitz). Bat enforces CRLF (LF-only breaks cmd.exe). Each step logs its exit code.

```powershell
schtasks /query /tn "KGLab-OCR-Daily" /v /fo list
Start-ScheduledTask -TaskName "KGLab-OCR-Daily"   # manual fire
```

### Manual operations

```bash
python scripts/ocr_with_gemini.py status                          # how many queued
python scripts/ocr_with_gemini.py run --limit 1                   # smoke test
python scripts/ocr_with_gemini.py run --rpm 8                     # full run
python scripts/ocr_with_gemini.py run --model gemini-2.5-flash-lite --rpm 12  # ~3x quota faster
python scripts/ocr_with_gemini.py run --engine haiku --book <id>  # Haiku one-at-a-time
```

### When OCR breaks

| `parse_error` | Meaning | Action |
|---|---|---|
| `no extractable text` | In OCR queue | next daily run picks up |
| `OCR ok but R2 push failed:` | OCR done, R2 write failed | next run re-tries cheaply (JSONL kept) |
| `OCR: …` | Permanent Gemini failure | investigate; possibly reset to `no extractable text` to re-try |
| `Haiku-OCR: …` | Permanent Haiku failure | investigate; often content-filter rejection |
| `file not found: …` | Drive path missing | check `G:\` is mounted; restart Drive client |
| `split from set; do not re-standardize` | Volume split child | leave alone |

### Multi-volume bundle rescue

When 套書 PDF fails BOTH Gemini (oversized) AND Haiku (content-filter), physically split into per-volume PDFs:

```bash
python scripts/split_oversized_pdf_by_toc.py <parent_ebook_id> --dry-run
python scripts/split_oversized_pdf_by_toc.py <parent_ebook_id>
```

Reads parent's level-1 TOC, writes one PDF per volume to same Drive folder, strips bundle suffixes like `（4卷本）`, inserts one new `ebooks` row per volume with `parse_error='no extractable text'`, marks parent with `SPLIT_MARKER`.

Single-volume oversized books usually go through Haiku auto-fallback fine — don't reach for this.

### Operational gotchas

- **OAuth token in `~/.claude/.credentials.json` expires every few hours.** Long-running `ocr_with_gemini.py` loads token at startup; once expired, every Haiku call returns `401`. Kill + restart.
- **Python DNS resolver caches failures.** Brief network blip → `getaddrinfo failed` persists in-process even after `ping` recovers. Kill + restart.
- **Anthropic rolling rate limit** — after ~6-7 consecutive Haiku books, next requests return Cloudflare 502 / `Connection error` for ~30 min. Effective Haiku throughput ~6 books/hour with cooldown, ~50 books/day max — still worse than Gemini's 250/day.
- **Vertical-typography Chinese books** (民族主義的不正當性, Tagore translation) — both engines struggle. Haiku scrambles column order; Gemini truncates JSON. No good fix.
- **Content-filter rejections** (哥白尼革命, 規訓與懲罰, 走向馬克思主義的人道主義) — Haiku returns `Output blocked by content filtering policy`. Use `--engine gemini --book <id>`.

---

## Workflow D — Daily z-lib drop ingest

User drops freshly-acquired ebooks into [`z-lib/`](../../../z-lib/) at project root. Filename suffix `(z-library.sk, 1lib.sk, z-lib.sk)` preserved on disk, stripped during parse. [`scripts/ingest_new_books.py`](../../../scripts/ingest_new_books.py) processes once per day as part of `run_ocr_daily.bat`. For each `.pdf` / `.epub` / `.mobi` / `.azw3`:

1. **Parse filename** → `(author, title, ext)` via `parse_drive_inventory.parse_filename()`.
2. **Classify** into 9 main categories. Two-tier:
   - **Keyword fallback first** (free): `christ|church|bonhoeffer|patristic|...` → `宗教學`; `zoroastr|avesta|islam|buddhis` → `世界宗教`.
   - **Gemini 2.5 Flash** otherwise — strict JSON. LLM mistakes ("基督教"/"神學") auto-mapped to 宗教學.
3. **Insert** `ebooks` row with `category`, `parsed_at=NULL`, `file_path` pointing to future Drive location.
4. **Move** local file → `G:/我的雲端硬碟/資料/電子書/{category}/{author}，{title}.{ext}`. G: IS Drive sync mount → move = upload + local-delete in one filesystem rename.

After ingest, new rows appear with `parsed_at=NULL`. Next `parse_worker.py run` (step 2) extracts text. If fails, `ocr_with_gemini.py` picks up (step 3).

```bash
python scripts/ingest_new_books.py status              # how many waiting
python scripts/ingest_new_books.py run --dry-run       # preview classification + paths
python scripts/ingest_new_books.py run --limit 3
python scripts/ingest_new_books.py run                 # full sweep
```

### Failure modes

| Mode | Behavior |
|---|---|
| DB insert fails | File kept in `z-lib/`; safe to re-run |
| Move fails after DB insert | File kept, row inserted but not on Drive. Manual move or delete row. Rare |
| Gemini quota / 429 | Skip that book; others continue with keyword fallback. Tomorrow's run picks up |
| Filename unparseable | Log `SKIP: could not parse title`. Add override to `parse_drive_inventory.TITLE_AUTHOR_OVERRIDES` |
| Target exists on Drive (dupe) | **Auto-delete `z-lib/` copy** (since 2026-05-14). Logs both sizes |

Keyword fallback skews Christian-studies (user backlog) — extend `fallback_category()` for other dominant areas. Junk files (`Z-Library-latest.exe`) silently ignored — only `EBOOK_EXTS` touched.

---

## Workflow B — Standardize books → reader-ready format

Turn a parsed book into reader-ready chunks at `/ebook/[id]`. Pipeline **branches on `file_type`**:

| `file_type` | Source | Script | Granularity |
|---|---|---|---|
| `epub` | `<h1-h4>`, `<b>/<em>`, `<p>`, TOC tree | [`scripts/standardize_ebook.py`](../../../scripts/standardize_ebook.py) | chapter chunks |
| `pdf` (text or OCR'd) | per-page JSONL from parse_worker / ocr_with_gemini | [`scripts/standardize_pdf_lite.py`](../../../scripts/standardize_pdf_lite.py) → [`scripts/standardize_pdf.py`](../../../scripts/standardize_pdf.py) | Plan A: per-page; Plan B: chapter |

Both branches write the **same JSONL shape** to `G:/我的雲端硬碟/資料/電子書/_chunks/{ebook_id}.jsonl`.

> **🔑 Hard rule: PDF `page_number` is sacred.** Citations in 書摘 reference real publisher page numbers. Any transform that re-numbers `page_number` is a bug. `chunk_index` can be re-numbered; `page_number` cannot.

### Quick commands

```bash
# EPUB single / batch (auto-skips PDFs)
python scripts/standardize_ebook.py <ebook_id>
python scripts/standardize_ebook.py <ebook_id> --dry-run
python scripts/standardize_ebook.py --category 哲學
python scripts/standardize_ebook.py --category 哲學 --subcategory 近代哲學

# PDF Plan A (lite — s2tw + spacing + metadata)
python scripts/standardize_pdf_lite.py <ebook_id>
python scripts/standardize_pdf_lite.py --all

# PDF Plan B v0 (TOC-driven chapter chunks; run AFTER Plan A)
python scripts/standardize_pdf.py <ebook_id>
python scripts/standardize_pdf.py --all --dry-run        # list eligible
python scripts/standardize_pdf.py --all                  # ~6.5s/book
python scripts/standardize_pdf.py <ebook_id> --force     # ignore annotations guard
```

### Output contract — 共通 JSONL shape

```json
{
  "chunk_index": 0,
  "chunk_type": "chapter",
  "page_number": null,
  "chapter_path": "第一卷　時　間",
  "volume": "文明的歷史：發現者（上冊）",
  "format": "markdown",
  "content": "## 第一卷　時　間\n\n時間是最偉大的改革者。"
}
```

| Field | EPUB | PDF Plan A | PDF Plan B v0 |
|---|---|---|---|
| `chunk_index` | 0-based contiguous | 0-based contiguous | re-numbered from 0 |
| `chunk_type` | `"chapter"` | `"page"` | `"chapter"` |
| `page_number` | null | **real PDF page (sacred)** | **first real PDF page in chapter (sacred)** |
| `page_range` | — | — | `[first, last]` |
| `chapter_path` | TOC anchor title | derived if heading detected else null | TOC ancestor hierarchy `祖 / 父 / 本` |
| `volume` | multi-volume only | — | — |
| `format` | `"markdown"` | `"text"` | `"text"` |
| `content` | markdown (h2-h4, bold, em, blockquote) | s2tw'd + spacing-collapsed | concatenated s2tw'd pages joined by `\n\n` |

Reader's [`server/utils/ebook-chunks.ts`](../../../server/utils/ebook-chunks.ts) `loadToc()` consumes this; reader page renders markdown via its own h1-h4 / bold / em / blockquote / paragraph renderer.

### EPUB pipeline (`standardize_ebook.py`)

1. **Read EPUB** via `ebooklib` — iterate spine docs in reading order.
2. **Parse TOC** (`book.toc`):
   - Strip `版权信息` / `Digital Lab` entries
   - Volume filter: keep only entries with `卷 / 冊 / 部 / 集 / 篇` (else 「目錄/插頁/出版說明」 promoted to fake volumes)
   - `href` (no anchor) → volume start at doc; `href#anchor` → volume start at anchor inside doc
   - <2 remaining volume entries → flat (single-volume) layout
3. **Per spine doc**: TOC anchors → split body into segments → each becomes a candidate chunk.
4. **HTML → markdown** via `el_to_md`:
   - `<h1>` → `##`, `<h2>` → `###`, `<h3>/<h4>` → `####`
   - `<b>/<strong>` → `**…**`, `<em>/<i>` → `*…*`
   - `<p>` → para, `<blockquote>` → `> …`, `<hr>` → `---`
   - Images / `<sup>` footnote / decorative `<svg>` stripped
5. **Drop / dedupe + s2tw + TRAD_FIXES** (see Shared rules).
6. **Pick `chapter_path`** from first markdown heading; fallback filename.
7. **Persist**: JSONL → gzip+PUT R2 → DELETE+INSERT `ebook_chunks` previews (adaptive batch) → update ebooks row.

#### Hierarchical TOC support — `parse_toc_hierarchical`

When top-level Sections have ≥2 children each, switch from flat to 2-level splitter that exposes both 章 AND 節 in sidebar.

**Role detection.** Top-level Section title shape determines role:
- **multi_volume** — tops are volume names (羅馬帝國衰亡史「全譯羅馬帝國衰亡史：1」). Split at child (chapter) AND grandchild (節) anchors. `volume=top_title`, `chapter_path=chap_or_section`. Headings: chapters `###` (sidebar pl-7), 節 `####` (pl-11).
- **single_chapter** — tops look like printed chapters (現代世界史「第1章 歐洲的興起」 — matches `_CHAPTER_TITLE_RE`). Split at top (chapter) AND child (節) anchors. `volume=None`. Headings: chapters `##` (pl-3), 節 `###` (pl-7).

Decision: `_is_chapter_title()` vs `looks_like_volume()` counts. ≥50% tops match chapter pattern AND chapter > volume count → `single_chapter`; else `multi_volume`.

Survey: 283/308 standardized EPUBs (92%) qualify for hierarchical; 25 fall back to legacy `parse_volume_toc`.

#### Anchor splitting — deep walk + per-anchor dedup

`split_body_at_anchors` walks **all body descendants** in document order (publishers wrap chapter lists inside `<div>` directly under body — naïve `body.children` loop misses everything but first anchor). Dedupes anchor matches by their `id` value (same id often emitted on both `<a>` nav target AND `<h2>` heading).

#### Heading normalization (hierarchical mode only)

Reader's `loadToc` derives sidebar nesting from each chunk's first heading depth. EPUBs use whatever `<h1>/<h2>/<h3>` the publisher chose. Standardize loop forces uniform heading level per role + prepends a heading at target level if chunk has none.

#### Post-processing pipeline (after EPUB walk, before persist)

Order matters — end of `standardize()`:

1. **`promote_implicit_volumes`** — unnamed top-level group (publisher omitted 「第一部」 but named 「第二部」+) → scan vol=None chunks for `第N部/卷` dividers in `chapter_path` and synthesize missing volume.
2. **`apply_cover_enrichment`** — replace `## 封面 (書本封面)` placeholder with structured markdown from DB title/author + 版權頁 extraction (subtitle / original_title / author_en). Insert at index 0 if no cover.
3. **`consolidate_frontmatter_into_publisher`** — CONTENTS-style chunk (目錄 / Contents) in first ~12 entries AND no volume between cover and CONTENTS → fold chunks `[1..contents-1]` into one synthesized 「出版資訊」. Named entries (序 / 致謝 / 譯者序 / 推薦序 / Acknowledgments) AFTER CONTENTS stay separate.
4. **`derive_chapter_title` smart fallback** — skips numeric/single-letter headings (academic EPUBs use `<h2>1</h2><h1>Real Title</h1>`); combines `「01 王權的誕生」` from `<h2>01</h2><p>王權的誕生</p>`.
5. **Continuation-merge size cap** — `is_continuation_title` merges tiny `「二」/「A」` into previous chunk, but only if plain text ≤ 800 chars (prevents 130KB chapter titled `「1」` being eaten).

#### Auto-split for 套書 (since 2026-05-14)

After standardize, if title matches 套書 pattern, auto-calls `detect_set_volumes` (Haiku) + `split_ebook_set` (children flattened to `##`). Each child gets `parse_error = 'split from set; do not re-standardize'`.

### PDF Plan A — `standardize_pdf_lite.py`

Polish per-page JSONL from parse_worker / ocr_with_gemini. Per chunk:

1. **s2tw + TRAD_FIXES** (Shared rules).
2. **Collapse CJK spacing** — `路 … 文 本 、 歷 史` → `路文本、歷史` via `collapse_cjk_spacing()`. Squeezes adjacent CJK without touching real spaces in mixed CJK/Latin.
3. **Strip page-number-only running header** — only when leading line is short AND starts with a number = chunk's `page_number`. Conservative: `2  Title` on a page whose actual `page_number=7` stays put.
4. **Re-derive `chapter_path`** — only when page genuinely starts with chapter heading (`第N章 / Chapter N / 引言 / 序 / 致謝 / 附錄 / Bibliography / Index`). Unclear → leave null.
5. **Preserve `page_number` exactly**.

Book-level: extract publisher metadata + PATCH ebooks row.

Plan A does NOT do: chapter-level chunking, cover synthesis, frontmatter consolidation, volume hierarchy, position-based header strip, bold/italic/heading inference.

### PDF Plan B v0 — `standardize_pdf.py` (TOC-driven)

Re-chunk Plan A's flat pages into chapter-level chunks **driven by PDF TOC bookmarks**. Same source-of-truth (existing JSONL) — no PDF text re-extraction.

> **🚧 Why TOC, not font?** 30-PDF probe showed font signal degenerate on a large fraction — many image-based PDFs where PyMuPDF extracts <1% body text yet TOC bookmarks survive. TOC more reliable + simpler. Font-driven inference deferred to v1 for no-TOC subset.

#### What v0 does

1. Load per-page JSONL (already Plan A-polished).
2. Read PDF's TOC (`fitz.Document.get_toc()`).
3. Filter to `level <= 2`, drop empties, dedupe same-start-page, sort by start page.
4. For each TOC entry, concat existing JSONL pages from `[entry.start_page, next.start_page - 1]` into one chapter chunk.
5. Pages BEFORE first TOC entry → one `前置內容` chunk (so 版權頁 / 序言 still feed `_extract_publisher_metadata`).
6. Apply `to_traditional()` + `collapse_cjk_spacing()` per chunk.
7. Build hierarchical `chapter_path` from TOC ancestors (`祖 / 父 / 本`).
8. Persist.

#### Skip conditions (book stays on Plan A output)

| Condition | Threshold |
|---|---|
| TOC entries < 3 | `MIN_TOC_ENTRIES` |
| Page-level TOC (~1 entry/page) | `total_pages / len(toc) < 1.2` |
| Existing annotations | hard refuse without `--force` |
| JSONL already chapter-chunked | re-run guard — revert via `standardize_pdf_lite` first |
| PDF file missing on Drive | `file not found:` |

#### Realistic hit rate (full `--all` batch)

152 / 437 chapter-chunked. 285 skip: ~257 had 0 TOC entries (Plan B v1 candidates), ~28 reduced to single chunk or page-level TOC.

### Plan B v1 — font-driven (deferred design)

Worth building when no-TOC subset (~285) becomes bottleneck.

1. **Per-page font analysis** — `(text, font_name, font_size, bbox, flags)` via `page.get_text("dict")`.
2. **Global font histogram** — char count per `font_size` bucket. Most common size = body.
3. **Classify spans relative to body**:
   - `≥ body + 6pt` AND short (≤30 chars) → `h2` (chapter)
   - `≥ body + 3pt` AND short → `h3` (section)
   - `≥ body + 1pt` → `h4` (subsection)
   - `flags & 16` (bold) AND short → `h3` (some publishers signal headings only by bold)
4. **Build markdown** — heading spans → `##` / `###` / `####`; body merged by same y-bbox proximity; bold/italic body → `**…**` / `*…*`.
5. **Chunking** — new chunk at every `h2`. Same per-chunk contract (`page_number` sacred, `page_range` new).

Calibration:
- **Body size is linchpin.** Filter by total char count per bucket, not frequency (footnotes are small but numerous).
- **Bold-only signaling is publisher-specific.** 商務印書館 漢譯名著 puts chapter titles in bold same-size as body. Enable bold→heading only when font-size signal weak.
- **Drop running headers/footers** — text spans at same y-bbox on most pages. Detect by frequency.
- **Page-spanning paragraphs** — don't split. Track "did previous page end mid-sentence" via `not text.endswith(('。', '!', '?', '」', '）'))`.

Skip v1 when: book reads OK after Plan A/B v0; heavy formula/table layout (PyMuPDF mangles those); image-based PDFs (run OCR first; v1 font signal will be empty).

### Shared rules (both EPUB and PDF)

#### Simplified → traditional

```python
to_traditional(text):
    1. opencc.OpenCC("s2tw").convert()
    2. Apply TRAD_FIXES table (24 entries — shared with parse_drive_inventory.py)
```

Fixes s2tw over-conversions: 历史→曆史 (should be 歷史), 託爾斯泰→托爾斯泰, 慄田→栗田. When you find a new mis-conversion, **add to `parse_drive_inventory.py:TRAD_FIXES`** (single source of truth) and re-run.

#### Drop & dedupe (publisher noise)

```python
HARD_DROP_PATTERNS = [
    r"Digital\s*Lab是上海译文出版社",
    r"我们致力于将优质的资源送到读者手中",
    r"上海译文出版社\|Digital\s*Lab",
]
DEDUPE_PATTERNS = [
    r"^版权信息", r"^版權信息",
    "圖書在版編目", "图书在版编目",   # CIP — multi-volume sets repeat per volume
]
```

Empty-doc: < 5 chars plain text:
- First cover-image-only page (`titlepage.xhtml` or filename `cover`) → emit `## 封面` placeholder once
- Later empty pages → drop silently

**Tuning heuristic:** patterns must be narrow enough not to match real content. Test on 1 book with `--dry-run` before batch.

#### Continuation-merge

EPUBs (and OCR'd PDFs) sometimes split one logical section across multiple files whose TOC titles are just `一/二/三` (續篇) or `A/B/C` (索引字母分頁). Merge into previous chunk.

```
Before:  [後記] + [二] + [索引] + [A] + [B] + … + [Z]   ← 27 chunks
After:   [後記] + [索引]                                  ← 2 chunks
```

`is_continuation_title()` regex: `[一二三四五六七八九十百千]+` / single `[A-Za-z]` / 1-3 digits / empty. Merge only if **same `volume`** as previous (don't merge across volume boundaries).

#### Chapter title derivation

`derive_chapter_title()` / `normalize_chapter_title()` — selection priority (first match wins):

1. **Markdown heading** — `## title` / `### title` (after rename normalization)
2. **CIP in first 3 lines** → `版權頁`
3. **Earliest short non-banner line** (≤30 chars, no `叢書|丛书|名著|系列|文集|文庫|出版社`) — document order, so 「目錄」 beats later「第一章」 inside TOC chunk
4. **Long chapter heading anywhere** — `^第N(章|卷|編|册|冊|部|集|篇|節|节|回|课|課)` accepted even if >30 chars (君主論's chapter titles can be 30+ chars)
5. First candidate ≤60 chars as last resort
6. Filename fallback (`text/part0001.html`) — should never reach here for well-formed books

Cosmetic renames trigger **heading rewrite** in chunk content — without this, sidebar shows `版權頁` but page renders `## 圖書在版編目（CIP）數據` as title.

#### Same-chapter cross-spine merge

Previous chunk has EXACT same `volume + chapter_path` as current → continuation (cross-spine-doc spillover). Strip duplicate heading and append. Without this each chapter's title-image spine doc becomes phantom standalone chunk.

#### Volume detection — known limits

`looks_like_volume()` requires `卷 / 冊 / 部 / 集 / 篇` in TOC entry. Works for: 文明的歷史：發現者（上冊）✅, 中國儒學史：先秦卷 ✅, 五燈會元第N部 ✅. Misses: 「上/中/下」alone (too common), Volume I/II in mixed-lang, 輯 or other markers.

If multi-volume book gets flattened, **add marker to `VOLUME_MARKERS`** and re-run.

#### Broken anchor fallback (EPUB)

Some EPUBs (e.g. 中國儒學史) put `#anchor` in TOC but body never emits matching `id`. Handler validates each `(file, anchor, title)` against doc HTML. ≥1 anchor lands → keep split-at-anchor. **No** anchors resolve → promote first title to doc-level volume start. Logged as `(N anchored volume(s) had no resolvable id — promoted to doc-level starts)`.

#### Rich publisher metadata extraction (`_extract_publisher_metadata`)

Scans every chunk for 版權頁-style key-value lines, writes to ebooks columns:

| Field | Regex source | ebooks column |
|---|---|---|
| `full_title` (subtitle split) | `書名: …` / `Title: …` | `subtitle` (post-`：` part) |
| `original_title` | `原文書名: …` / `原書名: …` / `Original Title: …` | `original_title` |
| `author_en` | `作者: 中文（English）` parens capture | `author_en` |
| `translator` | `譯者: …` (stops at `│ \| ， ; / 、`) | `translator` |
| `publisher` | `出版: …` / `出版社: …` / `Published by: …` | `publisher` |
| `publish_year` | `初版: …YYYY` / `初版首刷: YYYY` / `電子書: …YYYY` | `publication_year` |
| `original_publish_year` + `original_author` | `Copyright © YYYY by AUTHOR` | both |

Field-stop char class `_FIELD_STOP = "\n│|，,；;／/（(、"` keeps regexes from greedy-eating siblings on packed lines.

**Auto-copy to `books` on excerpt creation** — `server/api/annotations/index.post.ts` POST with `save_as_excerpt: true` reads rich columns from `ebooks` and copies into auto-created `books` row.

#### DB previews (`ebook_chunks`)

After writing JSONL + R2: DELETE existing → INSERT 200-char preview each chunk. Adaptive batch (100 → 50 → 20 → 5 → 1) to ride out 57014 timeouts on 800+ chunk books.

### Idempotency + annotation safety

| Branch | Re-run safe? | Annotation safety |
|---|---|---|
| EPUB | ✅ overwrites | ⚠ `chunk_index` shifts if drop/dedupe rules change — avoid on books with annotations |
| PDF Plan A | ✅ overwrites | ✅ `chunk_index` + `page_number` preserved exactly |
| PDF Plan B v0 on Plan-A book | ✅ overwrites | ⚠ re-chunks → `chunk_index` shifts; refuses without `--force` on annotations |
| PDF Plan B v0 on Plan-B book | ⛔ HARD STOP — revert via `standardize_pdf_lite` first | — |

Currently 3 ebooks have annotations: 文明的歷史 / A state of mixture / 道教簡史 (none 套書, none PDFs). Check first if batch-running.

### Verify a result

```bash
python -c "
import json
from pathlib import Path
p = Path('G:/我的雲端硬碟/資料/電子書/_chunks/<ebook_id>.jsonl')
chunks = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
print(f'chunks: {len(chunks)}')
print(f'first 5 page_numbers: {[c.get(\"page_number\") for c in chunks[:5]]}')
print(f'last 3 page_numbers: {[c.get(\"page_number\") for c in chunks[-3:]]}')
print(f'chapters detected: {sum(1 for c in chunks if c.get(\"chapter_path\"))}')
for i in [0, 1, len(chunks)//2, len(chunks)-1]:
    c = chunks[i]
    print(f'[{i}] vol={c.get(\"volume\")} title={c[\"chapter_path\"]}')
    print(c['content'][:200]); print()
"
```

Reader-side: open `/ebook/<id>` (restart dev server first to clear LRU cache):
- TOC sidebar groups by volume if multi-volume
- Headings render bold + sized (h2 centered with rule, h3 left-aligned)
- Chinese is traditional throughout
- No `Digital Lab` ad pages
- PDF: `?page=N` URL matches printed page in chunk content

---

## Workflow C — Back-fill `ebook_chunks` previews

Needed when full-text search must cover a book whose chunks are only on disk/R2 but not in DB previews.

```bash
python scripts/repopulate_chunk_previews.py status
python scripts/repopulate_chunk_previews.py run                       # initial back-fill
python scripts/repopulate_chunk_previews.py retry-failed              # adaptive batch 100→1
python scripts/repopulate_chunk_previews.py run --book <ebook_id> --force
```

`retry-failed` is the safe re-run mode — finds books whose `ebook_chunks` count is below their expected `ebooks.chunk_count` and only retries those.

---

## Decision tree for "this book looks broken in the reader"

```
Book opens but no content?
  → Check ebook_chunks count. If 0 → run repopulate_chunk_previews.py --book <id>
  → If still missing, check local JSONL exists. If not → re-parse

Reader sidebar shows "目錄/插頁" as fake volumes?
  → standardize_ebook.py ran before volume-marker filter. Re-run.

Reader shows "Digital Lab" or other publisher noise?
  → Add phrase to HARD_DROP_PATTERNS, re-run.

PDF chapter_path mostly null after Plan A?
  → Normal — most PDF pages are mid-chapter. Run Plan B to get chapter chunks.

"JSONL already chapter-chunked" when re-running Plan B?
  → Run standardize_pdf_lite.py <id> first to revert, then Plan B.

Search returns no fulltext hits but title/author work?
  → ebook_chunks doesn't have previews. Run repopulate_chunk_previews.py.

A scanned PDF still shows "此頁無內容" 12+ hours after OCR scheduled?
  → Check scripts/logs/ocr_YYYY-MM-DD.log. If quota hit, tomorrow's run picks up.

Many books in OCR queue showing "file not found"?
  → G: drive (Drive sync) disconnected. Re-launch Google Drive client.

New book in z-lib/ never showed up?
  → Check ocr_YYYY-MM-DD.log "--- ingest_new_books ---" section.
  → 'CLASSIFY FAILED' = Gemini quota; tomorrow retries.
  → 'could not parse title' = filename pattern unsupported; rename or extend TITLE_AUTHOR_OVERRIDES.
```

---

## Common pitfalls

- **opencc s2tw over-converts**: 历史 → 曆史 (should be 歷史), 栗→慄. Post-fix table in [`scripts/parse_drive_inventory.py:TRAD_FIXES`](../../../scripts/parse_drive_inventory.py).
- **Chinese characters in shell output on Windows**: cp950 codec errors. Always `sys.stdout.reconfigure(encoding='utf-8')` or write to UTF-8 file.
- **`server/utils/ebook-chunks.ts` LRU cache (10 min TTL)** — hot-edits to JSONL aren't visible immediately. Restart dev server after batch standardize / re-parse.
- **Filename collisions in same folder**: multiple files with same stripped title → `parse_filename()` keeps subtitle. Already handled.
- **REST API row limit 1000**: any new bulk read must use `.range()`-based pagination.
- **Errno 22 invalid Windows path** during batch — pre-existing data issue on 5 books; skip them.

## Files NOT to touch unless user requests

- `data/local_inventory.json` — frozen Drive scan snapshot
- `data/parse_progress.txt` — auto-managed by parse_worker
- `G:/我的雲端硬碟/資料/電子書/_chunks/*.jsonl` — source of truth (R2 mirrors these; if lost, must re-parse)

## Recommended order for "I'm a new agent picking this up"

1. Status checks:
   ```bash
   python scripts/ingest_new_books.py status
   python scripts/repopulate_chunk_previews.py status
   python scripts/ocr_with_gemini.py status
   ```
2. If `z-lib/` has files waiting → `python scripts/ingest_new_books.py run`.
3. Read Workflow B before touching standardize.
4. Don't re-run `standardize_ebook.py` on books with annotations.
5. For categorized batch standardize, `--dry-run` first.
6. Watch daily scheduler at 16:00 — log in `scripts/logs/ocr_YYYY-MM-DD.log`.

## Reader-side features tied to the pipeline

### Bookshelf + reading bookmarks

Schema in [`database/bookshelf-and-bookmarks.sql`](../../../database/bookshelf-and-bookmarks.sql). RLS on; service-role endpoints filter by `user_id`.

- `user_reading_status (user_id, ebook_id, status)` — `status ∈ 'reading'|'read'`. PK one row per user-book.
- `reading_bookmarks (id, user_id, ebook_id, chunk_index, created_at)` — date-stamped 「今日讀到這裡」.

Endpoints: `PUT/GET /api/ebooks/:id/reading-status`, `POST/GET /api/ebooks/:id/bookmarks`, `DELETE /api/bookmarks/:id`, `GET /api/me/bookshelf`.

Reader UX (`pages/ebook/[id].vue`): toolbar status pill 📚 → 📖 → ✅ → 📚; 「📅 今日讀到這裡」 only when `reading`; TOC sidebar shows date badges; auto-jump to latest bookmark on book open if status=`reading` AND no `?page=`.

### Excerpts auto-flow (`save_as_excerpt: true`)

「+ 書摘」 button creates annotation + auto-creates `books` row (if `book_id` null) using rich metadata from `ebooks` columns + inserts `excerpts` row + links annotation. Result: book appears in `/excerpts/library` with rich metadata, excerpts grouped by chapter on `/excerpts/library/[bookId]`.

### Tags

Schema in [`database/tags.sql`](../../../database/tags.sql). `tags` + `book_tags` + `excerpt_tags`. Endpoints: `GET/POST /api/tags`, `DELETE /api/tags/:id`, `GET/PUT /api/books/:id/tags`, `GET/PUT /api/excerpts/:id/tags`. `tagId` query param on `/api/books` and `/api/ebooks`. Reusable [`components/TagPicker.vue`](../../../components/TagPicker.vue). URL filter `?tag=<id>`.

### Markdown citation export

「📋 匯出 Markdown」 button on `/excerpts/library/[bookId]` toolbar. Self-contained markdown (bibliographic header + chapter-grouped `> blockquote` + `——《book》, chapter, page` citation). Clipboard + `<book-title>.md` download. Client-side.

---

## Pending TODOs

0. **ziliaozhan/神学 大規模待下載清單** — 見 [`ziliaozhan_theology_todo.md`](ziliaozhan_theology_todo.md)（255 本，247 新增）。包含：
   - 古代基督信仰聖經注釋叢書（IVP ACCS 中譯）27 冊 ★★★
   - 黃根春《基督教典外文獻》OT 6 + NT 4 = 10 冊 ★★
   - Aquinas《神學大全》中譯 18 冊 + 索引 ★★★
   - Aquinas《駁異大全》中譯 4 卷 ★★
   - 信理神學套書 6 卷
   - Augustine / Athanasius / Ambrose / Chrysostom / Gregory / Origen / Tertullian / Justin / Anselm 等個別教父著作
   - Bonhoeffer / Barth / Rahner / Moltmann / Küng / Pelikan / Kierkegaard 等現代神學家
   - Doctors of the Church 靈修經典：師主篇、大德蘭、十字若望、依納爵神操、沙漠教父等
   - 教父／聖師傳記
   - URL pattern: `https://dl.ziliaozhan.win/d/书籍/pdf/{neice}/{filename}`
1. **PDF Plan B v1 (font-driven)** — for ~285 no-TOC PDFs. Design above in Workflow B.
2. **37 EPUBs with single chunk >400KB and no internal headings** — `resplit_giant_chunks.py` can't help. Needs LLM page-boundary detection on raw text, or font cues from raw EPUB HTML.
3. **16 套書 with `volume=None`** — flat-TOC EPUB or PDF without volume metadata. Need font-size analysis (EPUB) or LLM-detect on TOC chunk content.
4. **Auto-trigger standardize after daily ingest** — currently manual. Wire into bat as step 6 (idempotent skip for already-standardized).
5. **17 no-hit books** for `enrich_book_metadata.py` (article fragments, Chinese-Buddhist, translated Western works absent from Google Books). Manual fill via `/excerpts/library/[bookId]` UI.

## See also

- [`EBOOK_PIPELINE.md`](../../../EBOOK_PIPELINE.md) at repo root — original design doc
- [`scripts/haiku_cleanup_guide.md`](../../../scripts/haiku_cleanup_guide.md) — Haiku text cleanup (historical)
