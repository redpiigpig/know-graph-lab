---
name: denzinger-fix
description: Denzinger《公教會之信仰與倫理教義選集》(ebook_id 568726d3-967e-457a-ab69-7452b21d606f) 上架後的修正流程 — ① 找出問題頁（無文字／拉中同行混排／拉欄掉了／中欄掉了）② column-aware 重 OCR ③ 整合回 main JSONL ④ 重跑 segment + apply ⑤ 重補 /creeds 中譯。Trigger 例：「修 Denzinger」「Denzinger 補 OCR」「Denzinger 重 segment」「Denzinger 兩欄拉中沒切開」「Denzinger 第 N 頁壞了」「Denzinger DH range 不對」「Denzinger 目錄沒中文」「Denzinger 第一部分缺漏」。延伸 [[ebook-pipeline]] / [[scripture-canon-portal]]。
---

# Denzinger 修正 Skill

書本 metadata：
- ebook_id：`568726d3-967e-457a-ab69-7452b21d606f`
- 路徑：`G:/我的雲端硬碟/資料/電子書/世界宗教/基督教/教會法典與信條/輔仁神學著作編譯會，公教會之信仰與倫理教義選集.pdf`
- 2430 頁 PDF；reader URL：`/ebook/568726d3-967e-457a-ab69-7452b21d606f`
- display_mode = `bilingual-parallel`
- 上架歷史：[DENZINGER_HANDOFF_2026-05-27.md](../ebook-pipeline/DENZINGER_HANDOFF_2026-05-27.md)
- Spec：[book-structure-bilingual-parallel.md](../ebook-pipeline/book-structure-bilingual-parallel.md)

---

## 🟢 2026-05-29 已完成

| 階段 | 結果 |
|---|---|
| Phase 0 audit | ✅ baseline 967 actionable pages |
| Phase 1 column-aware re-OCR | ✅ **967 / 967 (100%)** — Haiku 963 頁 + Gemini fallback 4 頁 |
| Phase 2 consolidate (recolumn overlay 加在 segmenter) | ✅ |
| Phase 3 segmenter — divider-aware 模式 | ✅ 3913 chunks → re-segmented 2381 chunks (見下) |
| Phase 3.5 sidebar TOC 中文標題 + 3-level 樹 | ✅ |
| Phase 4 /creeds 重補（32 份）| ✅ |
| medieval-09/10/11 DH range 修正 | ✅ (Lateran I/II/III，已對照詳細目錄驗證) |
| **第一部分信經 DH 1-76 缺漏修復** (commit ad24ba7) | ✅ 見 ↓ |

Reader 端 Denzinger 已是完整拉中對照版。

### 2026-05-29 第二輪修正 — DH 1-76 + segmenter regex
- 補 OCR 7 頁（pp 78/89/95-98/100）— Haiku 6 頁 + Gemini 1 頁
- `segment_denzinger.py::overlay_recolumn()` 加 inject 邏輯：recolumn 有但 main JSONL 沒對應 page 的，會被當新 page 注入（共 31 頁）
- `DH_MARKER` regex 從 `\d{3,5}` → `\d{1,5}` + 字母 guard（必須跟字母開頭內容）
- 結果：DH range 從不合理的 101-8445 收斂到 1-5597；dupes 189→73、non-monotonic 122→93；sidebar 第一部分→簡單的信經 出現 DH 3/4/5/6/7 真實 entries
- chunk 8 DH 1924 誤判（原 SKILL.md 第 5 項）連帶自動修正

---

## 🟡 仍需修的（下次 session 起手）

按優先序，每項都是 self-contained 可單獨處理。

### ~~1. 第一部分信經 (DH 1-76) 整段缺漏~~ ✅ 2026-05-29 修

實際根因有兩條（在第二輪修正記錄裡）：
- `overlay_recolumn()` 只 overlay 不 inject — recolumn JSONL 已有 pp 76-100 但 main JSONL 沒對應 page，所以從未進 segmenter
- `DH_MARKER` regex 限制 3-5 位數，DH 1-76 完全抓不到

兩個都修了 → sidebar 第一部分→簡單的信經 出現 DH 3/4/5/6/7 真實 entries。

### 2. **附錄五新教信條 (DH 5500-5702) 沒 /creeds 出口**

chunks 存在 main JSONL（已 OCR）但 `_denzinger_to_creeds.py` 的 `COUNCIL_DH_RANGES` 沒這段 routing。結構上不屬於 `/ecumenical-councils/`，應該開新樹 `/protestant-creeds/` 或類似。

詳細目錄條目：
- 5500-5502 路德的小本基督徒要學
- 5503-5523 奧斯堡信條
- 5524-5562 安立甘宗信條
- 5563-5574 英國公理會信條
- 5575-5590 改革宗信仰港略
- 5591-5701 利馬文件 (BEM)
- 5702 台灣基督長老教會的信條

**修法**：在 `_denzinger_to_creeds.py` 加新表 + 新樹 root（例如 `data/creeds/protestant/...`），或者另寫一支 `_denzinger_to_protestant_creeds.py`。

### 3. **DH range 仍可能不精確**

只有 medieval-09/10/11 對照詳細目錄驗證過。下列 council 還是「猜的」：

| Council | 現用 range | 可能問題 |
|---|---|---|
| medieval-15 維也納 | 870-895 | 870-875 是 Boniface VIII Unam Sanctam (1302)，不是 Vienne (1311-12)；應該改 891-916 |
| medieval-08 Constantinople IV | 650-664 | 詳細目錄找到一條 DH 650-664 (1 entry)，疑似真正範圍更大 |
| trent-03~25 各 session | 1500-1835 各小段 | 細部 session 邊界沒 cross-check |
| vatican-i df/pa | 3000-3045 / 3050-3075 | 看起來合理但沒查 Denzinger 第 43 版正本確認 |
| vatican-ii sc/lg/dv/gs | 4001+ | 用 Hünermann 標準編號，但個別範圍可能太寬或太窄 |

**驗證工具**：parsed 詳細目錄已存在 `scripts/_denzinger_toc/entries.json`（gitignored，可重生）— 對照 entry 的 part/volume 跟 DH range 跑檢查即可。

### 4. **TOC parser 漏了多個 council header**

`_denzinger_parse_toc.py` 解析 Part 2 council 時漏抓多個 header，因為 Part 2 entries 用「DH range 獨立一行，title 接下一行直到 dot leader」layout，跟 ENTRY_START_RE 預期不同：

漏抓的 council：加禾東 (Chalcedon) / Constantinople II / Constantinople III / Lateran I-III / Vienne / Lateran V / Vatican II — 影響 sidebar 第二部分這些 volume 顯示成不正確的 popes header（或顯示「300-303」這種裸 DH 範圍）。

**修法**：改寫 ENTRY_START_RE + COUNCIL_HINT 處理 multi-line entry layout。改完 re-run `_denzinger_parse_toc.py` + `_denzinger_relabel.py`。

### ~~5. chunk 8 DH 1924 誤判~~ ✅ 2026-05-29 連帶修

DH_MARKER 加字母 guard 後不再把 stray 數字當 DH。

### 6. **詳細目錄 page 28-67 沒進 main JSONL** ⭐ 下次起手

意外發現（修第 1 項過程中）：詳細目錄正體跨 pp 21-67，但 main JSONL chunk 6 (page 68) 只包含詳細目錄末段（4180+ Vatican II）。pp 28-67 之間有近 40 頁詳細目錄沒進 chunks。

**現況**：`scripts/_denzinger_toc/entries.json` 仍是過去 session 跑出的完整版（包含 DH 1-76 標題），所以 sidebar 暫時看起來正常。**重跑 `_denzinger_parse_toc.py` 之前**必須先解決 pp 28-67 注入問題，否則 entries.json 會退化。

**修法**：
- 先確認 pp 28-67 在 recolumn JSONL 有沒有 — 沒有就 `_denzinger_recolumn_ocr.py --pages 28..67`
- 改 `_denzinger_parse_toc.py` 不要只讀 chunk_index=6，改成合併 `chunk_type=='header' AND page in 21..68 AND content 含「詳細目錄」` 所有 chunks
- 這項解了，第 4 項（多行 council header）才有意義跑

---

## 起手步驟（新 session）

1. **第一件事**：跑 `python -X utf8 -u scripts/_denzinger_audit.py` 看當前 bucket 分布
2. 看本 SKILL.md「仍需修的」決定要動哪項
3. 改完任一項都要 commit + push（[[feedback_auto_push]]）
4. 重大狀態變更要更新本檔上方的「✅ 已完成」表

---

## 完整 Pipeline（reference）

### Phase 0：基線審計

```bash
python -X utf8 -u scripts/_denzinger_audit.py
```

寫 `scripts/_denzinger_audit.txt`，分類每頁 bucket。

### Phase 1：column-aware 重 OCR

```bash
# 全跑（idempotent，會 skip 已完成）
python -X utf8 -u scripts/_denzinger_recolumn_ocr.py

# 指定特定頁
python -X utf8 -u scripts/_denzinger_recolumn_ocr.py --pages 635 1024 1500

# 指定 bucket
python -X utf8 -u scripts/_denzinger_recolumn_ocr.py --bucket missing
```

Prompt 要 Haiku 輸出：
```
--- 拉丁文 ---
<full left column>

--- 中譯 ---
<full right column>
```

寫入 `_chunks/{id}.recolumn.jsonl`。**2-strike pause** — 連 2 頁 fail 自動退出留 checkpoint。

**Haiku content-filter blocked 頁的 fallback**：少數頁 Haiku 會回 400 `Output blocked by content filtering policy`（不是 quota，是安全層拒絕）。改用 Gemini：
```bash
python -X utf8 -u scripts/_denzinger_recolumn_gemini_fallback.py 2346 2380 2386 2401
```

### Phase 3：segmenter（divider-aware）

```bash
python -X utf8 -u scripts/segment_denzinger.py --dry-run --report
python -X utf8 -u scripts/segment_denzinger.py --apply
```

Segmenter 會：
1. `overlay_recolumn()` — 把 recolumn.jsonl 的 page content 覆蓋到對應 page
2. `_segment_divider_page()` — 偵測 `--- 拉丁文 ---` / `--- 中譯 ---` 切兩塊各自抓 DH
3. 沒 divider 的頁 fallback 原 line-by-line CJK ratio

### Phase 3.5：sidebar TOC 中文標題

```bash
python -X utf8 -u scripts/_denzinger_parse_toc.py
#   → scripts/_denzinger_toc/dh_titles.json + entries.json

python -X utf8 -u scripts/_denzinger_relabel.py --no-db   # JSONL + R2
python -X utf8 -u scripts/_denzinger_relabel.py           # 含 DB PATCH
```

效果：
- chunks 0-7：封面 / 綜合目錄 / 序言 / 壹 / 貳 / 詳細目錄 / 第一部分引言
- entry chunks：「DH N 中文標題」+ volume = 教宗/會議 + parent_volume = 第一/二/三部分
- commentary chunks：「前一 chapter · 註解」（避免 dedupe 隱藏）

### Phase 4：重補 /creeds

```bash
python -X utf8 -u scripts/_denzinger_to_creeds.py             # dry-run
python -X utf8 -u scripts/_denzinger_to_creeds.py --write --force
```

`COUNCIL_DH_RANGES` 在 script 內。改 range 來源：
- 詳細目錄解析結果（`scripts/_denzinger_toc/entries.json`）
- [Denzinger 維基條目](https://en.wikipedia.org/wiki/Enchiridion_Symbolorum)
- vatican.va 會議文獻索引

---

## 單 chunk 急就版（不重跑 pipeline）

要修 1-2 個 DH entry：
1. Reader UI 開 `/ebook/568726d3-...?page={chunk_index+1}` 找到要修的 chunk
2. 按右上 ✏️ 編輯按鈕，改 content / source_text / chapter_path
3. 直接存 DB（API：`PUT /api/ebooks/{id}/chunks/{index}`）

**注意**：手改的 chunks 在下次 segment --apply 會被覆蓋。

---

## 工具清單

| 檔 | 作用 |
|---|---|
| `scripts/_denzinger_audit.py` | 分類每頁 bucket，寫 audit.txt |
| `scripts/_denzinger_audit.txt` | bucket → page numbers list（gitignored） |
| `scripts/_denzinger_recolumn_ocr.py` | column-aware 重 OCR（Haiku，gitignored） |
| `scripts/_denzinger_recolumn_gemini_fallback.py` | Haiku content-filter blocked 頁的 Gemini fallback（gitignored） |
| `scripts/_denzinger_consolidate.py` | merge gaps → main JSONL（recolumn 由 segmenter overlay 處理） |
| `scripts/segment_denzinger.py` | page chunks → DH-indexed bilingual chunks（含 recolumn overlay + divider 模式） |
| `scripts/_denzinger_parse_toc.py` | 解析 chunk 6 詳細目錄 → dh_titles.json + entries.json |
| `scripts/_denzinger_relabel.py` | 重寫 chunks 的 chapter_path / volume / parent_volume + R2 push |
| `scripts/_denzinger_toc/` | parser 輸出（gitignored） |
| `scripts/_denzinger_to_creeds.py` | bilingual chunks → /creeds Chinese files |
| `scripts/_denzinger_overnight.sh` | 通宵 auto-resume + auto-ship loop（gitignored） |
| `scripts/_ebook_shot.mjs` | reader 截圖驗證（`--port` `--ebook` `--page`） |
| `_chunks/{id}.jsonl` | 上架 main（segmented + relabeled，3913 chunks） |
| `_chunks/{id}.jsonl.presegment.bak` | segment 前的 page-level（2399 chunks） |
| `_chunks/{id}.jsonl.preconsolidate.bak` | consolidate 前的 main 801 chunks |
| `_chunks/{id}.jsonl.prerelabel.bak` | relabel 前的備份 |
| `_chunks/{id}.gaps.jsonl` | gap-fill OCR 補的 pages |
| `_chunks/{id}.bilingual.jsonl` | segment 輸出 |
| `_chunks/{id}.recolumn.jsonl` | column-aware OCR 輸出（967/967） |

---

## Trigger phrases

- 「修 Denzinger」「Denzinger 修正」→ 先讀本檔「🟡 仍需修的」清單問用戶要動哪項
- 「Denzinger 補 OCR」「Denzinger 第 N 頁壞了」→ Phase 1 `--pages N` 或 Gemini fallback
- 「Denzinger 兩欄拉中沒切開」→ Phase 1 + Phase 3
- 「Denzinger 重 segment」→ Phase 3
- 「Denzinger sidebar 全是 DH 編號」「目錄沒中文」「側欄目錄」→ Phase 3.5
- 「Denzinger DH range 不對」→ Phase 4 + 手改 COUNCIL_DH_RANGES（先查詳細目錄）
- 「Denzinger /creeds 重補」→ Phase 4
- 「Denzinger 第一部分缺漏」「DH 1-76 沒了」→ 仍需修第 1 項
- 「Denzinger 新教信條」「附錄五」→ 仍需修第 2 項
