---
name: ebook-translate
description: 將外文 ebook 翻譯／轉成繁體中文並入庫（reader 可讀）的完整流程。涵蓋兩條子 pipeline — (A) **英文 → 繁中（雙語入庫）**：Sonnet 4.6 或 Gemini Flash 章節級翻譯，原文 source_text 同步存進 JSONL，reader 提供「中／中英對照／英」三段切換；(B) **簡體 → 繁體（直接取代）**：opencc s2tw + TRAD_FIXES，不用 LLM，覆寫 content 不保留 source_text。Use when 使用者要把英文 ebook 翻成中文上架（例 ACCS Apocrypha、未中譯的 Schaff 卷）、補 ACCS 缺的中譯卷（vol 24-25 耶利米/哀歌等），或把舊有簡體書批次轉成繁體。本 skill 與 ebook-pipeline 並列：ebook-pipeline 處理 parse/OCR/standardize，本 skill 處理「外文／簡體 → 繁中」這一段。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。使用者一說要傳截圖立刻提醒先確認尺寸。

# Ebook Translate Skill

把外文／簡體 ebook 整理成繁體中文，按 chapter-level chunks 寫入 `_chunks/{ebook_id}.jsonl`，DB previews 同步，最後 `/ebook/[id]` 可讀。

跟 [ebook-pipeline](../ebook-pipeline/SKILL.md) 並列：ebook-pipeline 處理「電子書 → 結構化 chunks」（parse/OCR/standardize），本 skill 處理「外文／簡體 chunks → 繁中 chunks」。

兩條子 pipeline，差別主要在「是否保留原文」：

| | A. 英文 → 繁中 | B. 簡體 → 繁體 |
|---|---|---|
| 何時用 | EPUB/PDF 原書是英文，要中譯後上架 | 庫內已有簡體中文書，要轉成繁體 |
| 引擎 | Sonnet 4.6 / Gemini Flash（LLM）| opencc s2tw + TRAD_FIXES（rules-based，**不用 LLM**）|
| JSONL 新欄位 | `source_lang: "en"` + `source_text`（保留原文）| 不新增；`content` 直接覆寫 |
| Reader UI | 「中／中英對照／英」三段切換 | 純繁中單欄（跟其他中文書一樣）|
| 速度 | 一本 ~244 chunks 約 4-12 小時（看引擎、quota）| 一本一兩秒（純字串替換）|

## 何時 trigger

**A. 英 → 中（LLM 翻譯）**：
- 使用者把英文 ebook 加進庫（DB row + Drive 檔），說「你來負責翻譯」「中譯」「translate」
- ACCS 英文 27/29 卷有但中譯缺（如 Apocrypha vol 15，已加入庫 2026-05-21）
- 中譯 ACCS 27 冊缺的書卷（vol 24-25 耶利米/哀歌；無官方中譯需自己翻）
- 使用者要把英文教父原典／神學典籍中譯上架

**B. 簡 → 繁（s2tw 取代）**：
- 使用者說「把簡體書都轉成繁體」「掃一遍把簡體取代掉」
- 新 ingest 的書 chunk 偵測到簡體字 → 觸發轉換
- 已上架書經抽查發現是簡體 → 補跑

不適用：中文書內容潤稿（看 ebook-pipeline 的 standardize 流程）；繁→簡（沒這需求）。

---

## A. 英 → 中 Pipeline

### 概覽

```
英文 EPUB（Drive 上）
    │
    ▼
ebooklib + BeautifulSoup → 章節級 source chunks（含 ## heading）
    │
    ▼
按 chunk 長度判斷：>20K chars 自動 split_oversized 按段落分塊
    │
    ▼
Sonnet 4.6 / Gemini Flash 翻譯（術語對齊 prompt + glossary）
    │
    ▼
s2tw 安全 pass + collapse_cjk_spacing
    │
    ▼
append-write JSONL（中斷可 --resume），每筆 chunk 同時存 `source_text`（英文原文） + `content`（繁中）
    │
    ▼
push R2 + PATCH ebooks (chunk_count, standardized_at) + refresh ebook_chunks previews
    │
    ▼
/ebook/[id] 可讀，topbar 有「中／中英對照／英」三段切換（localStorage 持久化）
```

### 核心工具

[`scripts/translate_ebook_to_zh.py`](../../../scripts/translate_ebook_to_zh.py)

```bash
# 看 source 結構（不打 API）
python scripts/translate_ebook_to_zh.py <ebook_id> --inspect

# 跑 3 個 chunk 試水溫
python scripts/translate_ebook_to_zh.py <ebook_id> --engine sonnet --limit 3

# 完整跑（中斷可 --resume）
python scripts/translate_ebook_to_zh.py <ebook_id> --engine sonnet --resume

# 也可改用 Gemini Flash（quota 與 OCR 不衝突）
python scripts/translate_ebook_to_zh.py <ebook_id> --engine gemini --resume
```

`--resume` 機制：on-disk JSONL 用 append-mode 寫，每完成一個 chunk 立刻 flush。再啟動時讀 JSONL，看 `chapter_path` 對 source 的 title_en — 已完成的 skip。所以中斷／kill 不會丟進度。

最後一次完整跑會把 chunk_index 重編連續寫一次（rewrite JSONL）。

## 引擎選擇

| 引擎 | 何時用 | 注意 |
|---|---|---|
| **Sonnet 4.6** | 預設，神學術語準確度最高 | OAuth token 每 ~8 小時 refresh；script 已加自動 re-read `~/.claude/.credentials.json` mtime advance 就重建 client；如果跑時 OCR Haiku wrapper 也在跑，會 burst 429 — 看 [quota 協調](#quota-協調) |
| **Gemini Flash** | OCR 在跑且不想暫停；或 Sonnet OAuth re-auth 麻煩時 | 4 個 key rotation；翻譯品質略遜 Sonnet；術語對齊靠 prompt 自己撐；free tier 250 RPD 跑 1 本 ~244 chunks 一天內可完成 |

**規則**：使用者沒指明 → 先試 Sonnet。若 OCR queue 還很多本要打（>10 本）且使用者不想暫停 OCR → 改 Gemini。

## Quota 協調（與 ebook-pipeline 的 OCR）

ebook-pipeline 的 OCR Haiku wrapper（`_haiku_autorestart.sh` / `_haiku_ivp_priority.sh`）跟本 skill 的 Sonnet 翻譯 **共用同一個 Anthropic Max 帳號的 burst rate limit**。實測：

| OCR 狀態 | Sonnet 翻譯預期 |
|---|---|
| OCR 完全停 | 順跑，每 chunk ~30-60s API time |
| 1 個 wrapper 在跑（~1 call/min） | 偶爾 429，backoff [0,60,180,300,600]s 可吃下，但 244 chunks 預估 4-6hr |
| 2 個 wrapper 並跑 | 持續 429，根本無法推進 — 必須先停一個 |

**SOP**：開始 Sonnet 翻譯前先檢查並收斂到 ≤ 1 個 OCR wrapper。檢查命令：

```powershell
Get-Process bash, python -ErrorAction SilentlyContinue | Sort-Object StartTime | Format-Table Id, StartTime, CPU
```

看 `scripts/logs/ocr_haiku_YYYY-MM-DD*.log` mtime — 若 mtime 超過 1 小時沒動 = 殭屍 worker，直接 `Stop-Process -Id <pid> -Force`（zombie burning RAM but not making progress 是已知 pattern）。

## OAuth token refresh（Sonnet 專屬）

- Claude Code 的 OAuth access token 存在 `~/.claude/.credentials.json`，有效期 ~8 小時
- 互動 session 內 Claude Code 會自動 refresh，更新檔案 mtime
- 長跑 worker script 啟動時 load 舊 token，過期後每次 call 都 401
- **修法已內建**：`translate_ebook_to_zh.py:_refresh_sonnet_client_if_creds_changed` 每次 call 前檢查 credentials.json mtime，若更新就重建 client；401 也會強制 re-read 一次
- 仍然 401 = 互動 session 沒有 refresh（離開電腦太久 Claude Code 也沒動）→ 開個 Claude Code 互動視窗執行任意指令（讓它 refresh token）後再跑 worker

## Source 處理細節

EPUB 來源最乾淨（PDF OCR'd 噪聲多）：

```python
ebooklib.epub.read_epub(...) → iter ITEM_DOCUMENT
  → BeautifulSoup soup
  → 抓 h1-h4, p, blockquote, li 轉成 markdown
  → 每個 ITEM_DOCUMENT = 一個 source chunk
```

對 ACCS Apocrypha：244 source chunks，1.43M chars total。

**大 chunk 分塊** — 一個 source chunk 超過 20,000 chars（Sonnet 16K output cap + 安全 margin）會按 `\n\n` paragraph break 切成多 pieces，每 piece 個別翻，最後合併。例：「General Introduction」68K chars 切 ~4 pieces。

## Translation prompt

`PROMPT_TMPL` in [translate_ebook_to_zh.py](../../../scripts/translate_ebook_to_zh.py) 包含：

1. 嚴守繁體中文
2. 教父／教會傳統術語對齊（看 [glossary.md](glossary.md)）
3. 保留 Markdown 結構（## / ### / **bold** / *italic* / > / -）
4. 聖經引用格式：英文 `(1 Mac 4:18)` → 繁中`（瑪加伯上 4:18）`
5. 章節標題簡潔（「Chapter 1」→「第一章」）

新書翻譯前 update [glossary.md](glossary.md)，把該書會大量出現的特有人名／地名／作品名都先列入。然後手動把 glossary 的新增條目同步進 PROMPT_TMPL（或寫個讀 glossary 自動拼 prompt 的版本）。

## DB / Storage 對齊

翻譯完寫入：
- **JSONL**：`G:/.../_chunks/{ebook_id}.jsonl` — append-mode 漸進寫，最後 rewrite 重編 chunk_index
- **R2 mirror**：`r2://{R2_BUCKET}/ebook-chunks/{ebook_id}.jsonl.gz`（gzipped）
- **ebooks row PATCH**：`chunk_count`, `total_chars`, `parsed_at`, `standardized_at`（兩個 timestamp 都寫，daily bat `--only-fresh` 不會再碰）
- **ebook_chunks previews**：DELETE + INSERT 200-char preview，batch=25（preview 只取 `content`，**不存** `source_text`）

每筆 chunk JSON 結構（雙語 schema, 2026-05-21+）：

```jsonc
{
  "chunk_index": 0,
  "chunk_type": "chapter",
  "page_number": null,
  "chapter_path": "Introduction",
  "format": "markdown",
  "source_lang": "en",          // 來源語言；簡 → 繁 pipeline 不寫此欄
  "source_text": "Origen ...",  // 英文原文，雙語 reader 用；簡 → 繁 pipeline 不寫此欄
  "content": "奧利金 ..."       // 翻譯後／轉換後的繁中
}
```

### Reader bilingual toggle

`pages/ebook/[id].vue` topbar 在 `chunk.source_text` 存在時顯示「中／中英對照／英」三段切換：

- **中**（zh）：單欄繁中，現有預設行為。標註（annotations）只在這個模式下能 selection → highlight
- **中英對照**（bi）：grid-cols-2，左中右英，lg 寬度 max-w-7xl；mobile 自動降為單欄垂直堆疊
- **英**（en）：單欄英文，no annotation interaction

切換值存 `localStorage["ebook-viewMode"]`，跨頁／reload 保留。chunk 沒 source_text 時 `effectiveViewMode` 強制 fallback 到 zh（避免讀到舊書／簡轉繁書時看到空白英文欄）。

API（`/api/ebooks/[id]`）`currentPage.source_text` + `currentPage.source_lang` 已從 JSONL passthrough。Type 在 [server/utils/ebook-chunks.ts](../../../server/utils/ebook-chunks.ts) 加了 optional `source_text` / `source_lang`。

---

## 當前狀態（2026-05-21 晚間）

| Book | 狀態 | ebook_id | Source |
|---|---|---|---|
| **ACCS Apocrypha vol 15** | 🟢 雙語 schema smoke test 通過（Gemini, 3 chunks 已 R2 + DB）；待全量啟動 | `37ff8191-8bc8-4eeb-bd84-d85fa3dd893b` | archive.org（PDF/EPUB 已下載到 IVP 兄弟資料夾） |

下次接手第一動：
1. `Get-Process python` 看有沒有殘留 worker
2. `(Get-Content G:/.../_chunks/37ff8191-....jsonl | Measure-Object -Line).Lines` 看 resume 點（smoke test 已寫 3）
3. 確認 OCR wrapper / 互動 Claude Code（Opus/Sonnet）狀態 — Sonnet 翻譯跟使用者跟我互動會搶 Anthropic quota（**實測 2026-05-21：互動中啟 Sonnet worker 立刻 429**）；建議 idle 期跑 Sonnet，否則用 `--engine gemini`
4. 確認 Claude Code 剛剛有互動（credentials.json mtime 在 1 小時內，僅 Sonnet 需要）
5. `python scripts/translate_ebook_to_zh.py 37ff8191-... --engine <gemini|sonnet> --resume` 啟動

## 待翻清單（按優先順序）

1. **ACCS Apocrypha vol 15**（英文已下載；正在翻）
2. **ACCS vol 24-25 耶利米／哀歌**（中譯 27 冊跳過這段；確認無官方中譯後從英文 ACCS vol 12 翻）
3. **ACCS 第 29 卷 / companion index**（若 archive.org 有；確認是否值得）
4. （未來）使用者指明的其他英文書

每本書翻譯前先寫一行記到本表，列：`書名｜source 位置｜source 字數估計｜術語焦點`。翻完 toggle 到 [完成清單](#完成清單)。

## 完成清單

（空）

---

## B. 簡 → 繁 Pipeline

把舊有「JSONL `content` 是簡體中文」的 ebook **直接覆寫**成繁體。

### 規則

- **不用 LLM**：opencc s2tw + `parse_drive_inventory.TRAD_FIXES` 已足夠精確
- **直接取代**：不存 `source_text`、不存 `source_lang`，跟原本中文書 schema 一致
- **冪等**：對純繁中文本跑也沒副作用（opencc s2tw 對純繁字串幾乎是 identity）

### 偵測規則

對每本 ebook 抽 chunk[0]+chunk[1]+chunk[2] 的 `content`（合計 ~600 chars），檢查是否含**簡體獨佔指示字**（trad system 不會出現的字）：

```
历这们时国个来书学经长现产业实从问开关动头爱东车电话语门间见马体识号买卖书师
```

任一個指示字命中 → 標記為簡體 → 進 conversion queue。沒命中 → skip。

### 處理流程

```
ebooks WHERE chunk_count > 0
    │
    ▼
load JSONL（local 優先；fallback R2）
    │
    ▼
sample 簡體偵測（chunk[0..2] 的 content；任一指示字命中即判定）
    │
    ▼
若是簡體 → 對每 chunk 的 content 跑 standardize_ebook.to_traditional(content)
    │           （保留 chunk_index / chapter_path / format / page_number 不動；不寫 source_lang/source_text）
    ▼
rewrite JSONL（原地覆寫，無 backup — Drive 有版本歷史）
    │
    ▼
push R2 + refresh ebook_chunks previews（chunk_count 不變，不 PATCH ebooks.standardized_at）
```

### 核心工具

[`scripts/simp_to_trad_batch.py`](../../../scripts/simp_to_trad_batch.py)

```bash
# Dry run：只報告哪些書會被轉
python scripts/simp_to_trad_batch.py --scan

# 對單本書轉
python scripts/simp_to_trad_batch.py --id <ebook_id>

# 全庫掃 + 自動轉
python scripts/simp_to_trad_batch.py --run-all
```

### 常見坑

- **TRAD_FIXES 不夠**：opencc s2tw 的常見 over-conversion bug（历 → 曆 而非 歷）由 [`parse_drive_inventory.TRAD_FIXES`](../../../scripts/parse_drive_inventory.py) 處理。新發現的錯誤要加到那邊（**不要**在本 batch script 自己另寫一份）
- **書名／作者欄是簡體**：本 batch script 只動 JSONL `content`。`ebooks.title` / `ebooks.author` 的簡體要另跑（或在 ingest 時就 to_traditional）
- **判定誤殺**：英文書的 `content` 可能不含中文字 → 偵測不到指示字 → skip（正確行為）；若 mix 雙語（中英對照書）chunk[0] 是純英可能 miss → 偵測延伸到 chunk[0..2]
- **轉換後 reader cache 沒更新**：`server/utils/ebook-chunks.ts` 有 10min LRU cache，dev server 要 restart 才看得到

---

## Glossary 維護

[glossary.md](glossary.md) 是核心資產 — 教父人名／聖經書卷／神學術語的標準中文對應。

維護規則：
- 新書翻譯前先掃 source 抓未在 glossary 的高頻 proper noun，加入後再開翻
- 翻譯時若 LLM 回傳的中文跟 glossary 不一致 → glossary 是真理，手動修 chunk
- glossary 條目穩定後，把高頻項放進 PROMPT_TMPL（避免每次都靠 glossary 隱晦傳達）
- glossary 同時也是未來 reader 的「術語對照表」UI 的資料源（feature 待開）

## 常見坑

- **Token 過期殺整個 run** — script 已自動 re-read credentials.json；若 Claude Code 互動 session 已關超過 8 小時，沒有刷 token，必須先開個互動視窗觸發
- **OCR wrapper 殭屍**（log mtime 超過 1 小時沒動 + python process 高 CPU 但無進度）— 直接 `Stop-Process -Id <pid> -Force`，IVP / main wrapper 是兩個獨立 python，殺一個不影響另一個
- **Source EPUB 缺**（只有 PDF）— 改寫 `find_epub_for_book` 接 PDF：用 PyMuPDF 抽 page text → 簡單 chapter heuristic 切 source chunks。但 PDF OCR 雜訊多，翻譯品質會掉
- **JSONL 跨進程寫**（同一本書多開 worker）— 不要這樣做。append-mode 不防競態。一本書 = 一個 worker
- **chunk_index 跳號**（resume 模式）— 最後 final rewrite 會重編，中途看到不連續正常
- **R2 push 失敗** — 看 `se.push_to_r2` 錯誤；通常網路抖一下，script 不會 retry，下次跑時要手動 trigger，或加上 retry decorator
- **Reader 看不到新內容** — `server/utils/ebook-chunks.ts` 有 10min LRU cache，dev server 要 restart 才看得到（生產不用）

## See also

- [ebook-pipeline](../ebook-pipeline/SKILL.md) — parse / OCR / standardize / 套書 split 等 ebook 上游處理
- [scripture-canon-portal](../scripture-canon-portal/SKILL.md) — 教父原典／信條／典外文獻網站，會引用本 skill 翻譯出來的書
- [`scripts/translate_ebook_to_zh.py`](../../../scripts/translate_ebook_to_zh.py) — 核心翻譯腳本
- [glossary.md](glossary.md) — 教父／聖經書卷／神學術語對照
