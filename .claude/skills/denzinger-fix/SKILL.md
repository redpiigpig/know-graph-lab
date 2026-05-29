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

## 🟢 2026-05-29 全部修完 ✅

| 階段 | 結果 |
|---|---|
| Phase 0 audit | ✅ baseline 967 actionable pages |
| Phase 1 column-aware re-OCR | ✅ **967 / 967 (100%)** — Haiku 963 頁 + Gemini fallback 4 頁 |
| Phase 2 consolidate (recolumn overlay 加在 segmenter) | ✅ |
| Phase 3 segmenter — divider-aware 模式 + DH 1-76 修復 | ✅ 2379 chunks |
| Phase 3.5 sidebar TOC 中文標題 + 3-level 樹 | ✅ 20 council headers / 702 entries |
| Phase 4 /creeds 重補 | ✅ 38 份（33 council + 5 protestant 新教信條） |
| medieval-09 ~ 18 DH range 全對照詳細目錄精修 | ✅ entries.json 推算 |
| **第一部分信經 DH 1-76** | ✅ 修復 |
| **詳細目錄 pp 21-74 注入** | ✅ chunk 4 共 53 頁 / 111KB |
| **附錄五新教信條 /creeds 出口** | ✅ 新樹 `/protestant-confessions` 5 份上架 |

Reader 端 Denzinger 已是完整拉中對照版 + sidebar 樹完整 + `/creeds` 含天主教大公會議 33 份 + 新教 5 份。

### 第二輪修正記錄
- **DH 1-76 缺漏修復** (commit ad24ba7)
  - `segment_denzinger.py::overlay_recolumn()` 加 inject 邏輯：recolumn 有但 main JSONL 沒對應 page 的，會被當新 page 注入（共 31 頁）
  - `DH_MARKER` regex 從 `\d{3,5}` → `\d{1,5}` + 字母 guard（必須跟字母開頭內容）
  - 補 OCR 7 頁（pp 78/89/95-98/100）— Haiku 6 頁 + Gemini 1 頁
  - 結果：DH range 1-5597；dupes 189→73；non-monotonic 122→93
  - chunk 8 DH 1924 誤判連帶自動修正

### 第三輪修正記錄 (commit 62dff1f)
- **詳細目錄 pp 21-74 注入**：`segment_denzinger.py::is_toc_page()` 加處理 recolumn 後「--- 拉丁文 --- / --- 中譯 --- / 詳細目錄」layout：先剝 ZH_DIVIDER 再 startswith 檢查
- **`_denzinger_parse_toc.py` 升級**：
  - 不再 hard-code chunk_index=6，改 `chapter_path=='詳細目錄'` 多 chunks 合併
  - `load_toc_content()` 用 line-level filter 清掉 dividers / per-page 「詳細目錄」 reprints / recolumn `<empty>` sentinels
  - 新增 `ENTRY_DH_ONLY_RE` 支援 Part 2「DH range 獨立行 / title 下一行」layout
  - council 日期 lookahead regex 放寬接受「【1139年4月4日開幕】」格式
  - 結果：council header 15 → 20（Chalcedon / Const II/III / Lateran II/III 全進來）；entries 678 → 702；DH coverage 4044
- **`_denzinger_relabel.py::FRONT_MATTER`** 從 chunk_index key 改 page_number key + 每頁只 apply 第一個 chunk，避免 segmenter 重跑後 chunk_index drift 把詳細目錄誤標成「貳、如何應用」
- **`_denzinger_to_creeds.py::COUNCIL_DH_RANGES` 全面精修**：每個 council 範圍從「上界 council DH +1」到「下界 council DH -1」，覆蓋率明顯提升（如 medieval-15 維也納從 870-895 → 891-1150；trent / vatican-i / vatican-ii 段範圍也精化）
- **新增 `PROTESTANT_DH_RANGES`** + 5 份 protestant `.ts` metadata（路德小教理 / 奧斯堡 / 聖公宗39條 / 比利時信條 / 利馬 BEM）+ `data/creeds/textLoader.ts` 加 protestant-confessions/ loader + `data/creeds/index.ts` 4 個入 PROTESTANT_CONFESSIONS 1 個入 ECUMENICAL_DIALOGUES（Lima BEM）

---

## 🟡 已知細部殘留（可選）

主修整全部完成。剩下都是書本「真實限制」或極小邊角，不影響使用：

- **Lateran V (medieval-18) / Vatican II council header 沒當獨立 volume 抓**：Denzinger 把 Lateran V 文件編在「教宗良十世」、Vatican II 文件編在「教宗保祿六世」下，因為這些 council 文件由 Pope 簽發 — 是書本架構，不是 parser bug
- **5 份 protestant `.ts` metadata 用 stub 結構**：summary / notes 已填，但 versions 內非中文版（en / lat / de / fr / zh-Hant-Reformed 等）全標 `placeholder: true`。後續可補英拉原文
- **medieval-09 Lateran I `/creeds` 0 chunks**：書本對該 council canons 只列拉丁文沒中譯（chunks 存在但 content 中文欄為空）— Denzinger 原書限制
- **DH 5563-5574 英國公理會信條 / DH 5702 台灣基督長老教會信條 0 chunks**：書本可能因頁碼問題沒抓進 main JSONL；如要補可單獨 OCR 對應 page
- **附錄一～四（非新教）`/creeds` 出口未開**：附錄五新教信條已開（5 份）；其他附錄（無神論 / 自然宗教 / 東正教等）按需再加

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
