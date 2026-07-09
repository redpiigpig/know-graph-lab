---
name: ebook-translate
description: 將外文 ebook 翻譯／轉成繁體中文並入庫（reader 可讀）的完整流程。涵蓋兩條子 pipeline — (A) **英文 → 繁中（雙語入庫）**：`--engine auto`＝Gemini → NVIDIA → Haiku 三層鏈（Sonnet 4.6 仍可 `--engine sonnet` 顯式指定）章節級翻譯，原文 source_text 同步存進 JSONL，reader 提供「中／中英對照／英」三段切換；(B) **簡體 → 繁體（直接取代）**：opencc s2tw + TRAD_FIXES，不用 LLM，覆寫 content 不保留 source_text。Use when 使用者要把英文 ebook 翻成中文上架（例 ACCS Apocrypha、未中譯的 Schaff 卷）、補 ACCS 缺的中譯卷（vol 24-25 耶利米/哀歌等），或把舊有簡體書批次轉成繁體。本 skill 與 ebook-pipeline 並列：ebook-pipeline 處理 parse/OCR/standardize，本 skill 處理「外文／簡體 → 繁中」這一段。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。


> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。使用者一說要傳截圖立刻提醒先確認尺寸。

# Ebook Translate Skill

把外文／簡體 ebook 整理成繁體中文，按 chapter-level chunks 寫入 `_chunks/{ebook_id}.jsonl`，DB previews 同步，最後 `/ebook/[id]` 可讀。

跟 [ebook-pipeline](../ebook-pipeline/SKILL.md) 並列：ebook-pipeline 處理「電子書 → 結構化 chunks」（parse/OCR/standardize），本 skill 處理「外文／簡體 chunks → 繁中 chunks」。

兩條子 pipeline，差別主要在「是否保留原文」：

| | A. 英文 → 繁中 | B. 簡體 → 繁體 |
|---|---|---|
| 何時用 | EPUB/PDF 原書是英文，要中譯後上架 | 庫內已有簡體中文書，要轉成繁體 |
| 引擎 | `--engine auto`＝Gemini → NVIDIA → Haiku（LLM；`--engine sonnet` 可顯式指定 Sonnet 4.6）| opencc s2tw + TRAD_FIXES（rules-based，**不用 LLM**）|
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
LLM 翻譯（`--engine auto`＝Gemini → NVIDIA → Haiku；術語對齊 prompt + glossary）
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
python scripts/translate_ebook_to_zh.py <ebook_id> --engine auto --limit 3

# 完整跑（中斷可 --resume）；auto = Gemini → NVIDIA → Haiku 救急
python scripts/translate_ebook_to_zh.py <ebook_id> --engine auto --resume
```

`--resume` 機制：on-disk JSONL 用 append-mode 寫，每完成一個 chunk 立刻 flush。再啟動時讀 JSONL，**match 是用 `title_en`（英文 source heading），不是 `chapter_path`**（後者是已翻譯成中文的 H2，永遠對不上 source iter 的英文 title）。所以中斷／kill 不會丟進度，重啟也不會重做。

最後一次完整跑會：
1. 按 `src_order` 排序 out_chunks（補救 failure-then-resume 造成的完成順序 ≠ source 順序）
2. 重編 chunk_index 連續
3. 寫一次 rewrite JSONL

**連續失敗保護**：3 個 chunk 連續失敗 → `time.sleep(30 min)` → 重置計數續跑（Anthropic / Gemini rate-limit wall 自動消化，不會 spin）。

**完成 ≠ 一定完整**：rate-limit / 網路 / parse-error 都會讓某些 chunk 沒寫進 JSONL；最後 chunk_count 可能小於 source_chunks 數。再跑一次 `--resume` 會補進去。

## 引擎選擇

**預設一律 `--engine auto`** = 統一三層 fallback：**Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋節流）→ Haiku 救急**。其餘 `--engine` 選項只在特殊狀況才手動指定：

| 引擎 | 何時用 | 注意 |
|---|---|---|
| **auto**（預設） | 幾乎所有情況 | Gemini 主力，撞牆自動退 NVIDIA→Haiku，不需人工切換 |
| **gemini** | == 預設鏈，想顯式標明 | 4 key rotation；free tier 250 RPD × 4 keys；撞牆自動退到 NVIDIA→Haiku |
| **nvidia** | 並行多卷時把另一卷分流到 NVIDIA 池，或 Gemini 全乾 | ⚠️ **只能 deepseek-v4-flash**：唯一保留段落對齊 + `{{p:N}}`/`[^N]` marker；qwen3-next/llama-3.3 段落會崩、marker 會壞 |
| **haiku** | 免費池乾/被 OCR 佔用、有 Claude Max 訂閱時 | Haiku 主打（`haiku_first`），失敗才退 Gemini→NVIDIA 免費鏈（2026-06-05 起；也是 auto 的第三層救急）|
| **sonnet** | idle 期、單篇要最高神學術語品質、預算寬 | OAuth；跟互動 Claude Code 共用 Max 帳號 burst rate，互動中啟立刻 429，idle 期才能用 |

**規則**：
- 大批次、小批次、不確定 → 一律 `--engine auto`（Gemini 主、三層自動退讓）
- 並行多卷時可把其中一卷切 `--engine nvidia` 分散 quota；**同一卷切勿開兩個 process**（race 同一 JSONL → dual-state bug）
- 一律先看 [Quota 協調](#quota-協調) 確認狀態

### 2-strike + 6h cooldown 全域規則

`translate_ebook_to_zh.py` 內建：每一層連續 2 次耗盡（429/throttle/exhausted）就跳下一層，並對該層上 6 小時 cooldown；cooldown 後下一個 chunk 自動探一次，成功則 streak 歸零、cooldown 解除。目的是避免「每個 chunk 浪費 ~70s 重複試十幾次才 fallback」的反覆消耗。同樣語義也套到任何轉錄 pipeline（OCR／音檔轉錄）— 詳見 [[ebook-pipeline]] 的「跨腳本 2-strike 規範」段落。

## Quota 協調

三組 quota 互動：

| 工人 | 帳號 / quota | 跟誰搶 |
|---|---|---|
| **互動 Claude Code (Opus 4.8 / Fable 5)** | Anthropic Max OAuth | Sonnet worker (硬搶) / Haiku worker (鬆) |
| **OCR Haiku wrapper** (`_haiku_autorestart.sh`) | Anthropic Max OAuth | Sonnet worker (硬搶) / 互動 Opus (鬆) |
| **OCR Gemini** (`ocr_with_gemini.py`) | Gemini API key × 4 | Gemini 翻譯 (硬搶) |

實測（2026-05-21 / 2026-05-22）：

| 狀態 | Sonnet 翻譯 | Gemini 翻譯 | Haiku 翻譯 |
|---|---|---|---|
| 互動 Opus 沒動，OCR 全停 | 順跑 ~30-60s/chunk | 順跑 ~10-30s/chunk | 順跑 ~10-30s/chunk |
| 互動 Opus 在打字 | **立刻 429**，4-6hr 都推不完 1 本 | 不受影響 | 偶爾 429，basically OK |
| OCR Gemini 在跑 | OK | **每 chunk 4 key 都試完才放棄 (~70s 浪費)**，靠 Haiku fallback 救 | OK |
| OCR Haiku wrapper 在跑 | 持續 429 | 不受影響 | 偶爾 429 |

**SOP**：開始翻譯前檢查並選對 engine：

```powershell
Get-Process bash, python -ErrorAction SilentlyContinue | Sort-Object StartTime | Format-Table Id, StartTime, CPU
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*ocr_with_gemini*" -or $_.CommandLine -like "*_haiku_*" } | Select-Object ProcessId, CommandLine | Format-List
```

殭屍偵測：`scripts/logs/ocr_haiku_YYYY-MM-DD*.log` mtime 超過 1 小時沒動 = 殭屍 worker，直接 `Stop-Process -Id <pid> -Force`。

**防多 worker race**：本 skill 的 JSONL append-mode **不防競態**。一本書 = 一個 worker。TaskStop 不一定能殺乾淨 bash 包裝下的 python，重啟前一定要 PowerShell 確認：

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*translate_ebook*" }
```

兩個 worker 並跑會造成 JSONL 重複寫入相同 chunk（觀察過：本來 7 chunks，跑兩天變 76 lines / 28 unique titles，要手動 dedupe）。dedupe 方法：

```python
# 按 title_en dedup + sort by source order，見 git log b172z82ss / 此 session
seen, kept = set(), []
for l in lines:
    if l['title_en'] in seen: continue
    seen.add(l['title_en']); kept.append(l)
kept.sort(key=lambda c: src_order.get(c['title_en'], 10**9))
```

## OAuth token refresh（Sonnet／Haiku 共用）

- Claude Code 的 OAuth access token 存在 `~/.claude/.credentials.json`，有效期 ~8 小時
- 互動 session 內 Claude Code 會自動 refresh，更新檔案 mtime
- 長跑 worker script 啟動時 load 舊 token，過期後每次 call 都 401
- **修法已內建**：`translate_ebook_to_zh.py:_refresh_anthropic_client_if_creds_changed`（Sonnet／Haiku 共用同一 OAuth client）每次 call 前檢查 credentials.json mtime，若更新就重建 client；401 也會強制 re-read 一次
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

## 當前狀態（2026-05-27 — ANF Vol 1 模板鎖定）

**🟢 ANF Vol 1 = 教父全集翻譯模板**（[[anf-vol1-golden-template]]）

`ebook_id: c98d358d-7066-4691-a896-b7232707b0db`
114 letter pages / 1,002,000 繁中字 / 4923 中文 [^N] refs / 4926 中文腳註本文（中譯）/ 390 頁碼 markers

新 session 接手要先驗證 Vol 1：

```bash
python scripts/validate_book_structure.py c98d358d-7066-4691-a896-b7232707b0db
# 必須 0 FAIL；2 WARN 是末尾 index 頁的小問題，可忽略
```

Vol 1 通過 = 模板鎖定，Vol 2-38 比照重跑（既有 Vol 2 翻譯有 bleed bug，需砍掉重練）。

## Pipeline 5 步驟（2026-05-27 鎖定）

```
EPUB → translate_ebook_to_zh   (含 [^N]+{{p:N}}+(N) markers)
       → polish_translated_book (chapter_path 清理 + volume 標記)
       → consolidate_by_ncx     (按 NCX 樹合成 letter pages, ≤10 章/頁,
                                 parent_volume + Elucidation fold-back +
                                 封面/前言 rename + 索引尾頁清 volume)
       → sweep_book_quality     (T1 標題 bleed + T2 h3 漂移自動修)
       → R2 + DB previews 同步
```

舊有獨立的 `extract_epub_extras.py` 已 inline 進 translate parser，不再單獨跑。

對「已 consolidate 但需要重套 normalize 規則」的書（schema 加新欄位／規則邏輯更新後），用 [`scripts/repatch_consolidated_book.py`](../../../scripts/repatch_consolidated_book.py) **in-place** 修，不必重 translate 不必重 walk NCX：

```bash
python scripts/repatch_consolidated_book.py <ebook_id> --dry-run
python scripts/repatch_consolidated_book.py <ebook_id>
```

## 翻譯品質 scanner + sweep（2026-05-27 新增）

跑完 consolidate 後**必跑** scanner + sweep，抓 LLM 留下的標題吞內文、術語不對齊等問題：

```bash
# 1. Scan: 列出 T1-T7 命中
python scripts/scan_translated_book.py <ebook_id>

# 2. Sweep: 自動修 T1 (heading bleed) + T2 (h3 vs volume drift)
python scripts/sweep_book_quality.py <ebook_id> --dry-run     # 先看會改什麼
python scripts/sweep_book_quality.py <ebook_id>               # 真的改

# 3. Re-scan 確認剩餘 WARN
python scripts/scan_translated_book.py <ebook_id>

# 4. 逐段對照 gate — 列出中英段落數對不齊、需重譯的 chunk（JSONL-only 不需 DB）
python scripts/scan_translated_book.py <ebook_id> --gate
python scripts/scan_translated_book.py --all --gate --json          # 全庫掃
python scripts/scan_translated_book.py <ebook_id> --gate --gate-threshold 0.15  # 收緊門檻
```

**逐段對照 gate（2026-06-02 新增）**：reader 的中英對照逐段左右並排，譯文段落數一旦與原文不一致整篇就錯位。`--gate` 用 `alignment_gate()`（= T11 指標 `paragraph_drift`，門檻預設 0.25）輸出「需重譯」清單。根因已在 `PROMPT_TMPL` 規則 4 補強（「段落必須逐一對應，不可合併/拆分」）；舊書（prompt 修正前翻的）需重跑該 chunk。**實測 ANF Vol 1 golden template 仍有 3 個失準 chunk（77/79/96，ZH 段落數均 < EN）— 結構驗證器抓不到，待重譯。**

T1-T7 規則見 [book-structure-spec.md](../ebook-pipeline/book-structure-spec.md#翻譯品質-scan_translated_bookpy違反--warn)。

**sweep 不處理的剩餘 T2 case**：當 chunk 有兩個以上 h3（EPUB packaging 把下一封 letter 的 intro 灌進 chunk 末尾），sweep 自動 skip。需要 chunk 級別搬運，目前手動修（在 reader ✏️ 編輯按鈕）。實測 ANF Vol 1 剩 8 筆。

走 [scripts/translate_corpus_queue.py](../../../scripts/translate_corpus_queue.py) — queue runner 順序跑全 38 本，每本完成自動接後 2 步。state 存 `scripts/logs/corpus_queue_state.json`。

順序：ANF 1 → ANF 2 → … → ANF 10 → NPNF1 1 → … → NPNF2 14。

```powershell
python scripts/translate_corpus_queue.py --status     # 查進度
python scripts/translate_corpus_queue.py --only ANF:N # 單跑某本
```

詳細結構規範見 [book-structure-spec.md](../ebook-pipeline/book-structure-spec.md)。

簡→繁 batch 已掃完全庫（1688 本 / 29 本簡體轉好 / 3 本 JSONL 壞讀不開未處理）。

## 待翻清單（按優先順序）

1. **Schaff 38 冊**（自動跑中，見上）
2. **ACCS 第 29 卷 / companion index**（若 archive.org 有；確認是否值得）
3. （未來）使用者指明的其他英文書

完成歷史見 [完成清單](#完成清單)。

每本書翻譯前先寫一行記到本表，列：`書名｜source 位置｜source 字數估計｜術語焦點`。翻完 toggle 到 [完成清單](#完成清單)。

### 新書 ingest 簡略 SOP（無源檔走 archive.org 時）

對「中譯叢書缺卷、但 archive.org 完整套有英文版」的情形（ACCS vol 12 即此案例）：

1. WebSearch `"Ancient Christian Commentary" <book> EPUB archive.org` 找 internet archive item
2. `archive.org/details/...` 拉取 EPUB+PDF 直連 URL
3. `urllib.request.urlopen` 下載到 `G:\...\電子書\<category>\<subcategory>\IVP - ACCS <Book> (English, vol N)\` 新建子資料夾
4. INSERT ebooks row（參照已完成 vol 15 row 的 shape）：
   - title: `[English] <Original Title> (Ancient Christian Commentary on Scripture vol N)`
   - file_path: 完整 Drive 路徑（**含 `資料\`**）
   - category=世界宗教 / subcategory=`基督教／古代基督徒聖經註釋叢書 ACCS` / publisher=InterVarsity Press
5. `--inspect` 確認 EPUB 解析結構乾淨（chapter count、頭幾個 chunk 內容）
6. glossary.md 補書內 proper noun（人名‧地名‧主題）
7. smoke test → full run（見 [引擎選擇](#引擎選擇) / [Quota 協調](#quota-協調)）

## 完成清單

| Date | Book | Stats | Engine | 備註 |
|---|---|---|---|---|
| **2026-05-27** | **ANF Vol 1 精修 v3**（同上 ebook_id）| 112 letter pages（v2 的 114 - chunk 1 併入前言 - Elucidation 折進卷三）/ 1,002,003 繁中字 | repatch + sweep（不重翻）| 加 parent_volume 三層樹／封面「源自...」→「封面」／chunk 1+2 merge→「前言」／Elucidation fold 進卷三末頁／索引尾頁 stray volume 清除／T1 標題 bleed 39→0／T2 h3 letter-title 28→8（剩跨書 bleed）。validator 0 FAIL/0 WARN。**🟢 升級後的教父全集模板**|
| **2026-05-27** | **ANF Vol 1 重翻 v2**（同上 ebook_id）| 114 letter pages / 1,002,000 繁中字 / 4923 中文 [^N] / 4926 中譯腳註本文 / 390 頁碼 markers / 跑時間 ~3.5 hr | haiku 新 pipeline | EPUB parser 預帶 markers，PROMPT rule 7 指示 LLM 保留並翻腳註本文。validator 0 FAIL / 2 WARN（末尾 index 頁誤掛 Irenaeus 卷，可忽略，已於 v3 精修修掉）|
| **2026-05-23** | ANF Vol 1（v1，已棄）| 918 chunks / 778K 繁中字 / 跑 2h49m | haiku | 第一版有 consolidator bleed bug（Phila 第1-10章 內混 ch 7-11+士每拿 ch 1-5），且中文側完全無腳註 ref。已重翻 v2 |
| **2026-05-22** | ANF Vol 1（同上）| 中斷暫停 28/938 chunks（已併入上列完成） | gemini | 校 glossary／PROMPT/JSONL → 觸發新建 [translation-glossary](../translation-glossary/SKILL.md) 工具校所有譯名 |
| **2026-05-22** | **ACCS OT XII vol 12**（古代基督徒聖經註釋叢書 卷十二：耶利米書‧耶利米哀歌）<br>`ebook_id: 3f678406-3969-49c1-a971-d76a6fd62f0e` | 112 chunks / 434,720 繁中字 / 1.19M 英文字 / 跑時間 1h24m / 涵蓋 General Intro + Jeremiah 1-52 + Lamentations 1-5 + Subject/Scripture/Author Index + Notes | haiku（Gemini 4 key 全 429，直接走 Haiku；Vatican II Haiku worker 並跑無衝突） | English source 從 archive.org `ancient-christian-commentary-on-scripture_ot` item 下載 EPUB+PDF；補因中譯 27 冊跳過的 gap；少數 chapter_path 標題抓取偏長（chunk 6/40/100）— 內文品質乾淨可讀 |
| **2026-05-22** | **ACCS Apocrypha vol 15**（古代基督徒聖經註釋叢書 卷十五：次經）<br>`ebook_id: 37ff8191-8bc8-4eeb-bd84-d85fa3dd893b` | 243 chunks / 497,817 繁中字 / 1.43M 英文字 / 含多俾亞傳・智慧篇・德訓篇・巴錄・耶利米書信・三童歌・蘇撒納・比勒與大龍 + 教父人物簡介 + 各種索引 | gemini → 切 haiku | smoke test (gemini) 過 → 跑 gemini 撞 quota → 切 haiku direct 完成；中途撞 Anthropic 帳號 rate-limit 用 auto-pause 接住；最後按 src_order 排序入庫 |

## 下次接手第一動

1. 確認沒有殘留 worker，並注意 **Python launcher 假象**：

   ```powershell
   Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*translate_*" -or $_.CommandLine -like "*corpus*" } | Select-Object ProcessId, ParentProcessId, CommandLine | Format-List
   ```

   ⚠️ **正常會看到 2 個 python.exe per worker**（whisper_venv launcher + uv interpreter，parent-child）— 不是 race condition。判斷依據是 ParentProcessId：每個 `_whisper_venv\Scripts\python.exe` 都該有一個 child `uv\python\...\python.exe`。**真的 race condition 是同一個 ebook_id 出現在兩條獨立的 parent chain。**

2. 在跑 Schaff queue → `python scripts/translate_corpus_queue.py --status` 看進度，**不要再啟 worker**，會撞 JSONL race。要插隊單跑某本 → 先 TaskStop 整個 queue，再 `--only SERIES:VOL`。

2. 看待翻清單挑下一本，先 `--inspect` 看 source 結構：

   ```bash
   python scripts/translate_ebook_to_zh.py <ebook_id> --inspect
   ```

3. **🆕 譯名前置確認**（必做，2026-05-22 起新 SOP）：開 `http://localhost:3010/translation-glossary` 把 source 主要會出現的人名／神學術語都查一遍：
   - 確認 ★建議譯名跟使用者偏好一致
   - 不確定的問使用者「Justin Martyr 你要新教游斯丁、思高猶斯定、還是東正教尤斯丁？」
   - 確認後把該書要用的譯名同步寫進 `translate_ebook_to_zh.py:PROMPT_TMPL` 強化（補一行 `Justin Martyr → 殉道者猶斯定`）
   - 詳見 [translation-glossary](../translation-glossary/SKILL.md) skill
4. 確認 OCR Gemini worker 狀態（不衝突可放著）；OCR Haiku wrapper 狀態（若想用 sonnet/haiku 翻譯就先停）
5. `--engine` 選擇看 [引擎選擇](#引擎選擇) 規則
6. smoke test `--limit 3` 後**請使用者看 1-2 chunks 確認譯名**再 `--resume` 全跑

### 為什麼要先校譯名

實測：2026-05-22 跑 ANF Vol 1 直接開翻，Gemini 把 Justin Martyr 譯成「遊斯丁」，使用者糾正後要：
1. 殺 worker 避免繼續寫錯名
2. 修 [glossary.md](glossary.md) + `PROMPT_TMPL`
3. 改已寫的 JSONL chunks 內人名
4. push R2 + refresh DB previews
5. 重啟 worker

走 `/translation-glossary` 校過再開翻，這整套修正都不會發生。一本書 ~900 chunks，越早糾正越省事。

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

# 只重補 previews（不 s2tw 再跑）— 救撞到 Supabase 8s timeout 的大書
python scripts/simp_to_trad_batch.py --previews-only <ebook_id>
```

**Supabase previews timeout 救法**：DELETE + INSERT 在 >500 chunks 的書（例 2026-05-21 二思集 535 chunks）會撞 Supabase 8s `statement_timeout` (`code: 57014`)。`--previews-only` 子指令用 batch=10（vs main 用 25）+ 每批 3 次 retry，可以救回來。

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
- **JSONL 跨進程寫**（同一本書多開 worker）— 不要這樣做。append-mode 不防競態。一本書 = 一個 worker。TaskStop **不保證** kill python，重啟前一定要 PowerShell 確認（見 [Quota 協調](#quota-協調)）
- **chunk_index 跳號**（resume 模式）— 最後 final rewrite 會重編，中途看到不連續正常
- **R2 push 失敗** — 看 `se.push_to_r2` 錯誤；通常網路抖一下，script 不會 retry，下次跑時要手動 trigger，或加上 retry decorator
- **Reader 看不到新內容** — `server/utils/ebook-chunks.ts` 有 10min LRU cache，dev server 要 restart 才看得到（生產不用）
- **Reader 的 total_pages 卡在 stale DB 數**（翻譯途中讀者點 next 過不去）— API 已修為 `max(dbChunkCount, tocLen)`，TOC 走即時 JSONL，所以翻譯中 reload 就能即時跟上
- **目錄章節順序錯**（例：TOBIT 2:1-3:6 排在 1:3-22 前）— 完成順序 ≠ 源順序的副作用。final rewrite 已加 src_order sort 自動處理。歷史壞掉的 JSONL 可手動 dedupe + sort（見 [Quota 協調](#quota-協調) 末段的 snippet）
- **DB title 全英文搜不到中文**：新 ingest 預設用 `[English] Original Title` tag。翻完應 PATCH title 成 `中文書名（Original Title）` 格式（例 2026-05-22 ACCS Apocrypha vol 15）—— search 走 ilike 對 title，無中文則中文 query 命不中
- **跨翻譯 worker 名稱不一致**（例：多比傳 vs 多俾亞傳）— Haiku 偶爾忽略 PROMPT_TMPL 的 glossary 跳譯一次。改進方向：翻完後跑一個 glossary sweep 全文取代（沿用 `parse_drive_inventory.TRAD_FIXES` 模式但範圍更廣）。**目前狀態：未實作，使用者讀時可能會看到不一致**

## Tests

Pure-function pytest suite at [`scripts/tests/`](../../../scripts/tests/README.md)（`npm run test:py`）涵蓋本 pipeline 的可測邏輯：`split_oversized`（切塊不丟內容、段落數守恆）、`scan_translated_book.paragraph_drift`（逐段對照 T11 指標，已抽成 module-level 可重用 gate）、`sweep_book_quality` 的 T1/T2/T3 自動修、簡→繁 `to_traditional` + TRAD_FIXES（历→歷 不為曆）。改 regex／threshold 後先跑這套抓回歸。新發現的譯文品質 bug 先寫一條 `xfail(strict=True)` 當修復目標，修好自動轉綠。

## See also

- [ebook-pipeline](../ebook-pipeline/SKILL.md) — parse / OCR / standardize / 套書 split 等 ebook 上游處理
- [scripture-fathers](../scripture-fathers/SKILL.md) — 教父原典（公有領域 Schaff/CCEL）中譯精修，從本 skill 分出
- [ebook-collected-works](../ebook-collected-works/SKILL.md) — 多卷全集「3 欄以上多語對照」（原文＋既有譯本＋繁中）；source_text/source_lang 單一來源 → `sources` 多來源 schema 的擴充版，共用本 skill 的翻譯基礎設施（engine/quota/resume）
- [scripture-canon](../scripture-canon/SKILL.md) — 教父原典／信條／典外文獻網站，會引用本 skill 翻譯出來的書
- [`scripts/translate_ebook_to_zh.py`](../../../scripts/translate_ebook_to_zh.py) — 核心翻譯腳本
- [glossary.md](glossary.md) — 教父／聖經書卷／神學術語對照
