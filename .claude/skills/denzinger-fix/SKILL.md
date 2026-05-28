---
name: denzinger-fix
description: Denzinger《公教會之信仰與倫理教義選集》(ebook_id 568726d3-967e-457a-ab69-7452b21d606f) 上架後的修正流程 — ① 找出問題頁（無文字／拉中同行混排／拉欄掉了／中欄掉了）② column-aware 重 OCR ③ 整合回 main JSONL ④ 重跑 segment + apply ⑤ 重補 /creeds 中譯。Trigger 例：「修 Denzinger」「Denzinger 補 OCR」「Denzinger 重 segment」「Denzinger 兩欄拉中沒切開」「Denzinger 第 N 頁壞了」「Denzinger DH range 不對」。延伸 [[ebook-pipeline]] / [[scripture-canon-portal]]。
---

# Denzinger 修正 Skill

書本 metadata：
- ebook_id：`568726d3-967e-457a-ab69-7452b21d606f`
- 路徑：`G:/我的雲端硬碟/資料/電子書/世界宗教/基督教/教會法典與信條/輔仁神學著作編譯會，公教會之信仰與倫理教義選集.pdf`
- 2430 頁 PDF；reader URL：`/ebook/568726d3-967e-457a-ab69-7452b21d606f`
- display_mode = `bilingual-parallel`
- 上架歷史：[DENZINGER_HANDOFF_2026-05-27.md](../ebook-pipeline/DENZINGER_HANDOFF_2026-05-27.md)
- Spec：[book-structure-bilingual-parallel.md](../ebook-pipeline/book-structure-bilingual-parallel.md)

## 2026-05-29 狀態 — column-aware OCR 100% 完成 ✅

| 階段 | 狀態 |
|---|---|
| Phase 0 audit | ✅ |
| Phase 1 column-aware re-OCR | ✅ **967 / 967 (100%)** — Haiku 963 頁 + Gemini fallback 4 頁 |
| Phase 3 segment（divider-aware 模式）| ✅ 3913 chunks |
| Phase 3.5 sidebar 中文標題 | ✅ |
| Phase 4 /creeds 重補（32 份）| ✅ |
| medieval-09/10/11 DH range 修正 | ✅ (Lateran I/II/III) |

### Haiku content-filter blocked pages（學到的）

OCR'ing 過程中 4 頁 (2346 / 2380 / 2386 / 2401，全在 **附錄五 新教信條** DH 5500-5702 區) 觸發 Anthropic content-filter 硬擋（`Output blocked by content filtering policy` 400）— 不是 quota，是安全層拒絕輸出。多少 retry 都沒用。

**解法 — Gemini fallback**：寫了 [`scripts/_denzinger_recolumn_gemini_fallback.py`](../../../scripts/_denzinger_recolumn_gemini_fallback.py)（gitignored），同 prompt 同 divider 格式，用 `gemini-2.5-flash`。同樣的 4 頁 Gemini 全過。下次遇到 Haiku content-filter blocked 頁，用法：

```bash
python -X utf8 -u scripts/_denzinger_recolumn_gemini_fallback.py 2346 2380 2386 2401
# 然後 ship pipeline：
python -X utf8 -u scripts/segment_denzinger.py --apply
python -X utf8 -u scripts/_denzinger_relabel.py --no-db
python -X utf8 -u scripts/_denzinger_to_creeds.py --write --force
```

## 已知問題（修正目標）

| 類別 | 量級 | 症狀 | 修法 |
|---|---|---|---|
| **missing** | ~31 頁 | PDF 有字、OCR 沒抓到 | column-aware 重 OCR |
| **column-merged** | ~883 頁 | 兩欄拉中印成同一行 (`Latin words    Chinese words`)；segmenter 無法拆 | column-aware 重 OCR + divider prompt |
| **lat-heavy** | ~40 頁 | Latin ≥500 chars but CJK <100；中譯欄被丟 | column-aware 重 OCR |
| **cjk-heavy** | ~172 頁 | CJK ≥500 chars but Latin <100；多半正常（commentary 頁）| 通常不用動 |
| **short** | ~13 頁 | OCR <200 chars but PDF >600 | 重 OCR |
| **DH range 不對** | 6+ 條 | `_denzinger_to_creeds.py` 的 `COUNCIL_DH_RANGES` 編號猜的，medieval-09/10 跟 vatican-ii 四份要查書補 | 手翻書改 ranges |
| **DH 1-76 Part 1 信經整段缺漏** | ~11 頁 | PDF page 76-87 在 main JSONL 沒有 chunk，sidebar 第一部分只剩 1 個 placeholder | column-aware 重 OCR pp 76-87 → 重 segment |

## 修正流程（一次走完）

### Phase 0：基線審計（一定要先跑）

```bash
python -X utf8 -u scripts/_denzinger_audit.py
```

寫 `scripts/_denzinger_audit.txt`，列出每個 bucket 的頁碼。看 summary 決定要動哪幾個 bucket。

### Phase 1：column-aware 重 OCR（rate-limit 慢，一次幾百頁）

```bash
# 全部 4 個 actionable bucket 一起跑
python -X utf8 -u scripts/_denzinger_recolumn_ocr.py

# 或只跑特定 bucket
python -X utf8 -u scripts/_denzinger_recolumn_ocr.py --bucket missing
python -X utf8 -u scripts/_denzinger_recolumn_ocr.py --bucket column-merged --limit 100

# 或指定特定頁
python -X utf8 -u scripts/_denzinger_recolumn_ocr.py --pages 635 1024 1500
```

Prompt 要求 Haiku 輸出：
```
--- 拉丁文 ---
<full left column>

--- 中譯 ---
<full right column>
```

寫入 `_chunks/{id}.recolumn.jsonl`。**idempotent**，跑過的頁碼會 skip。**2-strike pause** — 連 2 頁 fail 自動退出留 checkpoint。

> ⚠ **這支 script 不是免錢**：~967 頁全跑，按 Haiku 配額 ~5 本/天的速度估，要 **跑好幾天 + 24h quota 等待**。
> 建議分批 `--limit 200` 配 background 跑。

### Phase 2：整合 recolumn 回 main JSONL

**目前 _denzinger_consolidate.py 只 merge `gaps.jsonl`、不知道 `recolumn.jsonl`**。需要先擴充 consolidate：

```python
# scripts/_denzinger_consolidate.py 加優先順序：
# recolumn > gaps > main
# recolumn 覆蓋 main（已改善的頁）+ 覆蓋 gaps（如有重疊）
```

未做，待 Phase 1 跑出可觀 recolumn 量後再寫。寫法參 `_load_gaps` pattern，多加一支 `_load_recolumn`。

### Phase 3：重跑 segment → apply

```bash
# Dry-run 先看 segmenter 對 recolumn divider 的反應
python -X utf8 -u scripts/segment_denzinger.py --dry-run --report

# 如果 column-merged chunks 變乾淨了，--apply
python -X utf8 -u scripts/segment_denzinger.py --apply
```

**segmenter 也要擴充** — 偵測 `--- 拉丁文 ---` / `--- 中譯 ---` divider，直接按 divider 切，不用 line-by-line CJK ratio 分類。改 `split_into_blocks()` 加分支：

```python
if "--- 拉丁文 ---" in content and "--- 中譯 ---" in content:
    # divider mode: easy split
    parts = content.split("--- 中譯 ---", 1)
    lat = parts[0].replace("--- 拉丁文 ---", "").strip()
    zh = parts[1].strip()
    # find DH numbers in zh (or lat) and pair
```

未做，待 Phase 2 跑完才知道輸出長相穩定。

### Phase 3.5：sidebar TOC 重貼中文標題（已上線 2026-05-28）

問題：reader 側欄 sidebar 預設從每個 chunk 的 `chapter_path` 抽 entries，
Denzinger 上架後變成「DH 100、DH 101、DH 102…」3000+ 條 flat list，無法導航。

修法（兩支 script，已 idempotent）：

```bash
# 1. 解析 chunk 6 的「詳細目錄」(103K chars, pages 21-74) → 結構化 JSON
python -X utf8 -u scripts/_denzinger_parse_toc.py
#   → scripts/_denzinger_toc/dh_titles.json   (3748 DH → 中文標題)
#   → scripts/_denzinger_toc/entries.json     (608 entries with part/volume)

# 2. 重寫每個 chunk 的 chapter_path / volume / parent_volume
python -X utf8 -u scripts/_denzinger_relabel.py --dry-run    # 預覽
python -X utf8 -u scripts/_denzinger_relabel.py --no-db      # JSONL + R2，不動 DB
python -X utf8 -u scripts/_denzinger_relabel.py              # 全部（含 DB PATCH）
```

效果：
- chunks 0-7 → 封面 / 綜合目錄 / 序言 / 壹/貳 / 詳細目錄 / 第一部分 引言
- 3164 個 entry chunks → 「DH N 中文標題」+ 教宗/會議作為 volume
- 117 個 commentary chunks → 「前一個 chapter · 註解」（避免 dedupe 隱藏）
- 131 個 header chunks → 去 `#` prefix、trim
- 全 chunks 帶 parent_volume = 第一部分／第二部分／第三部分

→ Sidebar 變成 3-level 樹（部 → 教宗/會議 → DH entry）

備份：`{id}.jsonl.prerelabel.bak`（idempotent，可 re-run）

未做但可加：
- DH 1-76（第一部分 信經）chunks 缺漏（pp 76-87 OCR 沒拿到），sidebar 第一部分目前只 1 個 placeholder（chunk 7 引言）
- chunk 8（DH 1924）內容其實是宗徒信經（DH 30 區段），segmenter 誤判 dh_number；要等 column-aware OCR + 重 segment 才會修正

### Phase 4：重補 /creeds

```bash
# 重跑 dry-run，看 DH ranges 配對是否更乾淨
python -X utf8 -u scripts/_denzinger_to_creeds.py

# Range 該修就改 COUNCIL_DH_RANGES table，重跑
python -X utf8 -u scripts/_denzinger_to_creeds.py --write --force
```

DH range 修正參考來源（不要憑空編）：
- 書本「綜合目錄」(page 4) 列出每個會議的 DH 起訖
- [Denzinger 維基條目](https://en.wikipedia.org/wiki/Enchiridion_Symbolorum)
- 教廷官方 vatican.va 的會議文獻索引

## 修正流程（單 chunk 急就版）

若只想修 1-2 個 DH entry 的 content（不重跑 pipeline）：
1. Reader UI 開 `/ebook/568726d3-...?page={chunk_index+1}` 找到要修的 chunk
2. 按右上 ✏️ 編輯按鈕，改 content / source_text / chapter_path
3. 直接存 DB（API：`PUT /api/ebooks/{id}/chunks/{index}`）
4. R2 JSONL 不會同步，但 reader 從 DB 讀（不是從 R2）— 即時生效

**注意**：手改的 chunks 在下次 segment --apply 會被覆蓋（segment 從 .presegment.bak 重 segment）。所以手改適合「絕對不會再 rebuild」的場景。

## 工具清單

| 檔 | 作用 |
|---|---|
| `scripts/_denzinger_audit.py` | 分類每頁 bucket，寫 audit.txt |
| `scripts/_denzinger_audit.txt` | bucket → page numbers list（gitignored）|
| `scripts/_denzinger_recolumn_ocr.py` | column-aware 重 OCR（gitignored）|
| `scripts/_denzinger_consolidate.py` | merge gaps（recolumn TBD）→ main JSONL |
| `scripts/segment_denzinger.py` | page chunks → DH-indexed bilingual chunks |
| `scripts/_denzinger_parse_toc.py` | 解析 chunk 6 詳細目錄 → dh_titles.json + entries.json |
| `scripts/_denzinger_relabel.py` | 重寫 chunks 的 chapter_path/volume/parent_volume + R2 push |
| `scripts/_denzinger_toc/` | parser 輸出（dh_titles.json + entries.json，gitignored）|
| `scripts/_denzinger_to_creeds.py` | bilingual chunks → /creeds Chinese files |
| `scripts/_ebook_shot.mjs` | reader 截圖驗證（`--port` `--ebook` `--page`）|
| `_chunks/{id}.jsonl` | 上架 main（segmented，3840 chunks）|
| `_chunks/{id}.jsonl.presegment.bak` | segment 前的 page-level 2399 chunks |
| `_chunks/{id}.jsonl.preconsolidate.bak` | consolidate 前的 main 801 chunks |
| `_chunks/{id}.gaps.jsonl` | gap-fill OCR 補的 1598 pages |
| `_chunks/{id}.bilingual.jsonl` | segment 輸出（= 現在 main JSONL）|
| `_chunks/{id}.recolumn.jsonl` | 待跑 column-aware OCR 輸出 |

## Trigger phrases

- 「修 Denzinger」「Denzinger 修正」→ Phase 0 audit → 問用戶要動哪些 bucket
- 「Denzinger 補 OCR」→ Phase 0 + Phase 1
- 「Denzinger 第 N 頁壞了」→ `--pages N` 跑 column-aware OCR
- 「Denzinger 重 segment」→ Phase 3
- 「Denzinger sidebar 全是 DH 編號」「Denzinger 目錄沒中文」「側欄目錄」→ Phase 3.5
- 「Denzinger DH range 不對」→ Phase 4 + 手改 COUNCIL_DH_RANGES
- 「Denzinger /creeds 重補」→ Phase 4
- 「Denzinger 兩欄拉中沒切開」→ Phase 1 + Phase 3

## 預估成本

| 動作 | 時間 | 備註 |
|---|---|---|
| Phase 0 audit | 1 min | local，免錢 |
| Phase 1 全跑（967 頁） | 數天 + quota 等 | Haiku 帳號 ~5 本/天上限；分批 `--limit 200` |
| Phase 2 consolidate 擴充 | 30 min code | 一次做完 |
| Phase 3 segment 擴充 + apply | 30 min code + 5 min run | divider parser 寫好就快 |
| Phase 4 /creeds 重補 | 5 min run + 手調 range | 看 range 表要查多少書 |
