---
name: ebook-translate
description: 將英文 ebook 翻譯成繁體中文並入庫（reader 可讀）的完整流程。Sonnet 4.6（OAuth）或 Gemini Flash 引擎，章節級 chunk 翻譯，教父人名／聖經書卷／神學術語對齊 glossary，append-write JSONL 支援 resume，token 自動 refresh。Use when 使用者要把英文 ebook 翻成中文上架（例 ACCS Apocrypha、未中譯的 Schaff 卷），或要補 ACCS 缺的中譯卷（vol 24-25 耶利米/哀歌等）。本 skill 與 ebook-pipeline 並列：ebook-pipeline 處理 parse/OCR/standardize，本 skill 處理「英→中」翻譯這一段。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。使用者一說要傳截圖立刻提醒先確認尺寸。

# Ebook Translate Skill

把英文 ebook 翻成繁體中文，按 chapter-level chunks 寫入 `_chunks/{ebook_id}.jsonl`，DB previews 同步，最後 `/ebook/[id]` 可讀。

跟 [ebook-pipeline](../ebook-pipeline/SKILL.md) 並列：ebook-pipeline 處理「電子書 → 結構化 chunks」（parse/OCR/standardize），本 skill 處理「英文 chunks → 中文 chunks」。

## 何時 trigger

- 使用者把英文 ebook 加進庫（DB row + Drive 檔），說「你來負責翻譯」「中譯」「translate」
- ACCS 英文 27/29 卷有但中譯缺（如 Apocrypha vol 15，已加入庫 2026-05-21）
- 中譯 ACCS 27 冊缺的書卷（vol 24-25 耶利米/哀歌；無官方中譯需自己翻）
- 使用者要把英文教父原典／神學典籍中譯上架

不適用：簡體 → 繁體（用 `opencc s2tw` + `parse_drive_inventory.py:TRAD_FIXES`，不用 LLM）；中文書內容潤稿（看 ebook-pipeline 的 standardize 流程）。

---

## Pipeline 概覽

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
append-write JSONL（中斷可 --resume）
    │
    ▼
push R2 + PATCH ebooks (chunk_count, standardized_at) + refresh ebook_chunks previews
    │
    ▼
/ebook/[id] 可讀
```

## 核心工具

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
- **ebook_chunks previews**：DELETE + INSERT 200-char preview，batch=25

`source_lang: "en"` 寫進 JSONL 每筆 chunk metadata（reader 暫時不顯示，但保留追溯）。

---

## 當前狀態（2026-05-21 晚間）

| Book | 狀態 | ebook_id | Source |
|---|---|---|---|
| **ACCS Apocrypha vol 15** | 🟡 翻譯啟動中（被 OAuth 401 中斷數次，已 fix；待重啟） | `37ff8191-8bc8-4eeb-bd84-d85fa3dd893b` | archive.org（PDF/EPUB 已下載到 IVP 兄弟資料夾） |

下次接手第一動：
1. `Get-Process python` 看有沒有殘留 worker
2. `wc -l G:/.../_chunks/37ff8191-...jsonl` 看 resume 點（之前都失敗，預期 0）
3. 確認 OCR wrapper 狀態（必要時暫停）
4. 確認 Claude Code 剛剛有互動（credentials.json mtime 在 1 小時內）
5. `python scripts/translate_ebook_to_zh.py 37ff8191-... --engine sonnet --resume` 啟動

## 待翻清單（按優先順序）

1. **ACCS Apocrypha vol 15**（英文已下載；正在翻）
2. **ACCS vol 24-25 耶利米／哀歌**（中譯 27 冊跳過這段；確認無官方中譯後從英文 ACCS vol 12 翻）
3. **ACCS 第 29 卷 / companion index**（若 archive.org 有；確認是否值得）
4. （未來）使用者指明的其他英文書

每本書翻譯前先寫一行記到本表，列：`書名｜source 位置｜source 字數估計｜術語焦點`。翻完 toggle 到 [完成清單](#完成清單)。

## 完成清單

（空）

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
