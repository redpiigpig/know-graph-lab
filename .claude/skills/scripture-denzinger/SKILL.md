---
name: scripture-denzinger
description: Denzinger《公教會之信仰與倫理教義選集》(ebook_id 568726d3-967e-457a-ab69-7452b21d606f) 修正流程 — 全書 2430 頁拉中對照已完整轉錄上架，523 個 DH entries 100% 有中譯。本 skill 紀錄 pipeline 與 7-stage 自動化流程。Trigger 例：「修 Denzinger」「Denzinger 補 OCR」「Denzinger 重 segment」「Denzinger 第 N 頁壞了」「Denzinger /creeds 重補」「Denzinger 沒中譯」「Denzinger 目錄沒中文」。延伸 [[ebook-pipeline]] / [[scripture-canon]]。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。


# Denzinger 修正 Skill

書本：`ebook_id=568726d3-967e-457a-ab69-7452b21d606f`，2430 頁，display_mode=`bilingual-parallel`，reader `/ebook/568726d3-967e-457a-ab69-7452b21d606f`。

PDF：`G:/我的雲端硬碟/資料/電子書/世界宗教/基督教/教會法典與信條/輔仁神學著作編譯會，公教會之信仰與倫理教義選集.pdf`。

詳細上架歷史見 [DENZINGER_HANDOFF_2026-05-27.md](../ebook-pipeline/DENZINGER_HANDOFF_2026-05-27.md)；schema 見 [book-structure-bilingual-parallel.md](../ebook-pipeline/book-structure-bilingual-parallel.md)。

---

## 🟢 狀態 (2026-05-30 完工)

| 指標 | 數字 |
|---|---:|
| recolumn re-OCR 覆蓋 | 974 / 974 頁（actionable + missing 全做） |
| Main JSONL chunks | 645（entry-merged，從 1841 折合） |
| DH entries 總數 | 523 |
| 拉中對照完整 ✓ | 465（88.9%） |
| zh-only（書本對教宗信／附錄只列中譯） | 58（11.1%） |
| lat-only / 兩者皆空 | **0 / 0** |
| **→ 中譯覆蓋率** | **523/523 = 100%** |
| Sidebar TOC | 20 council headers / 702 entries |
| `/creeds` 中文檔 | 33 council + 5 protestant 新教信條 |

Reader 端：DH 寶金徽章 + entry H1 標題、正文／註釋 `## 註釋` divider 分區、section header (`I. xxx`/`A. xxx`/「宗徒信經」) markdownize 成 H2/H3、PDF 內文頁碼僅複製引用時帶入、Noto Serif TC 17px line-height 2.0 學術風 typography。

---

## 7-stage pipeline（重做順序）

```bash
# 1. 重 OCR（idempotent）
python -X utf8 -u scripts/_denzinger_recolumn_ocr.py
python -X utf8 -u scripts/_denzinger_recolumn_gemini_fallback.py <pages…>  # Haiku 被 content-filter blocked 時

# 2. Segmenter（page → DH-indexed bilingual chunks）
python -X utf8 -u scripts/segment_denzinger.py --apply

# 3. 詳細目錄解析（→ entries.json + dh_titles.json）
python -X utf8 -u scripts/_denzinger_parse_toc.py

# 4. Relabel（front matter overrides + DH chapter_path）
python -X utf8 -u scripts/_denzinger_relabel.py --no-db

# 5. Entry-merge（DH-level → TOC entry-level；DH 3-5 = 1 chunk、奧斯堡 21 條 = 1 chunk）
python -X utf8 -u scripts/_denzinger_consolidate_entries.py

# 6. 內文清理（page footer + section header H2/H3）
python -X utf8 -u scripts/_denzinger_strip_internal_pages.py
python -X utf8 -u scripts/_denzinger_markdownize_headers.py

# 7. 補空白 + /creeds 寫入
python -X utf8 -u scripts/_denzinger_rescue_blank.py
python -X utf8 -u scripts/_denzinger_to_creeds.py --write --force
```

每階段都 push R2 + patch DB（除 `--no-db` flag）。

---

## 關鍵 segmenter / parser 邏輯

### Segmenter (`segment_denzinger.py`)
- `is_toc_page()`：對 recolumn 後「`--- 拉丁文 ---` / `--- 中譯 ---` / 詳細目錄」layout 先剝 ZH_DIVIDER 再 startswith 判斷
- `DH_MARKER` 1-5 位數 + 字母 guard；DH 1-99 加 page-aware filter（< 115）+ 拉丁/希臘大寫開頭限制（排除「9 及第 10 篇」這種 inline reference 誤判）
- `_segment_divider_page()` 中譯欄 paragraph-align fallback：拉丁欄 N 個 DH ↔ 中譯欄 N 段 1:1（Denzinger 中譯欄不寫 DH 編號，靠段落順序對齊）
- `overlay_recolumn()` inject：recolumn 有但 main JSONL 沒對應 page 的，當新 page 注入
- `consolidate_across_pages()`：entry → commentary fold 用 `<<COMMENTARY>>` sentinel，後續 phase 才分離正文 / 註釋

### Parse_toc (`_denzinger_parse_toc.py`)
- 讀 `chapter_path=='詳細目錄'` 多 chunks 合併（不再 hard-code chunk_index）
- `ENTRY_DH_ONLY_RE` 支援 Part 2「DH range 獨立行 / title 下一行」layout
- council 日期 lookahead 接受「【1139年4月4日開幕】」格式

### Consolidate_entries (`_denzinger_consolidate_entries.py`)
- entries.json 為邊界 — 同 entry 範圍內所有 DH chunks 合 1 chunk
- parent-range-wins：「DH 3-5」parent 抓走 DH 3/4/5，sub-entries (a/b/c) 不獨立成 chunk
- 收 `<<COMMENTARY>>` sentinel → 正文 + 「## 註釋」分隔 + 註釋

### Rescue_blank (`_denzinger_rescue_blank.py`)
- 對 zh=0 entries 從 recolumn（優先）/ presegment.bak 抽 CJK 段補回
- cjk_ratio ≥ 0.15，cjk_count ≥ 8，drop page footer
- 末尾空 `--- 中譯 ---` divider fallback 取整 page

### Relabel (`_denzinger_relabel.py`)
- `FRONT_MATTER` 用 page_number key（不用 chunk_index，避免 segmenter 重跑後 drift）

---

## 急就版（單 chunk 手改）

Reader UI 開 `/ebook/568726d3-...?page={chunk_index+1}` → 右上 ✏️ 編輯 → 改 content / source_text / chapter_path → API 自動存 DB。**注意**：下次 segment --apply 會覆蓋手改。

---

## 工具清單

| 檔 | 作用 |
|---|---|
| `scripts/_denzinger_audit.py` | 每頁分 bucket，寫 audit.txt（gitignored） |
| `scripts/_denzinger_recolumn_ocr.py` | column-aware Haiku re-OCR |
| `scripts/_denzinger_recolumn_gemini_fallback.py` | Haiku content-filter blocked → Gemini |
| `scripts/segment_denzinger.py` | page → DH-indexed bilingual chunks |
| `scripts/_denzinger_parse_toc.py` | 詳細目錄 → entries.json + dh_titles.json |
| `scripts/_denzinger_relabel.py` | 寫 chapter_path / volume + R2 push |
| `scripts/_denzinger_consolidate_entries.py` | DH chunks → entry-merged chunks（1841→645） |
| `scripts/_denzinger_strip_internal_pages.py` | 清「- N -」「(N)」page footer 殘渣 |
| `scripts/_denzinger_markdownize_headers.py` | `I. xxx`/`A. xxx`/group label → `## H2`/`### H3` |
| `scripts/_denzinger_rescue_blank.py` | zh=0 entries 從 raw OCR 抽 CJK 補回（達 100%） |
| `scripts/_denzinger_to_creeds.py` | bilingual chunks → /creeds 中文檔 |
| `scripts/_ebook_shot.mjs` | reader 截圖驗證（`--port` `--ebook` `--page` `--vw` `--vh`） |
| `scripts/_denzinger_toc/entries.json` | 702 entries 含 part/volume/title（gitignored） |
| `_chunks/{id}.jsonl` | 上架 main（645 entry-merged） |
| `_chunks/{id}.recolumn.jsonl` | column-aware OCR 輸出（974 頁） |
| `_chunks/{id}.jsonl.{presegment,prerelabel,preentrymerge,prestrip,premarkdown}.bak` | 各階段 backup |

---

## 🟡 小邊角（不影響使用）

- **5 份 protestant `.ts` metadata 的 versions 內非中文版仍 placeholder**：summary/notes 已填，但 en / lat / de / fr / zh-Hant-Reformed 等待補原文
- **附錄一～四 `/creeds` 出口未開**：附錄五新教（5 份）已開；其他附錄按需再加
- **Lateran V / Vatican II 沒當獨立 council volume 抓**：書本架構（文件由 Pope 簽發），不是 parser bug

---

## Trigger phrases

- 「修 Denzinger」「Denzinger 修正」→ 讀本檔狀態表，需求動哪 stage
- 「Denzinger 補 OCR」「第 N 頁壞了」→ stage 1
- 「Denzinger 重 segment」「兩欄沒切開」→ stage 1+2
- 「Denzinger 目錄沒中文」「sidebar 全是 DH 編號」→ stage 3+4
- 「Denzinger 同份信條沒合在一頁」→ stage 5
- 「Denzinger 內文有殘留頁碼」「section header 沒分層」→ stage 6
- 「Denzinger 沒中譯」「DH N 空白」→ stage 7（rescue）
- 「Denzinger DH range 不對」「/creeds 重補」→ `_denzinger_to_creeds.py`
