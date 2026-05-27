# 電子書資料結構規範（Book Structure Spec）

每本書經過完整 pipeline（translate → polish → extract_epub_extras → consolidate_by_ncx）後，存在 Drive `_chunks/{ebook_id}.jsonl` 並推送 R2，必須符合本規範。

驗證器：[`scripts/validate_book_structure.py`](../../../scripts/validate_book_structure.py)

```bash
python scripts/validate_book_structure.py <ebook_id>     # 單本
python scripts/validate_book_structure.py --all          # 全庫
python scripts/validate_book_structure.py <id> --json    # CI 用
```

## 每 chunk 必要欄位

| 欄位 | 型別 | 說明 |
|---|---|---|
| `chunk_index` | int | 0..N-1 連續整數 |
| `chunk_type` | `'page'\|'chapter'\|'section'` | DB check constraint |
| `chapter_path` | str | TOC 顯示名稱，≤35 字 |
| `content` | str | 繁中 markdown 正文，必含一個 h2/h3/h4 標題 |
| `source_text` | str? | 英文原文 markdown（雙語書），有 `[^N]` 腳註 ref |
| `source_lang` | `'en'`? | 雙語書 = `"en"`；純中文書省略 |
| `volume` | str? | 父著作中文名稱（如「巴拿巴書信」）；front matter 為 null |
| `format` | `"markdown"` | 固定值 |
| `page_number` | int? | 主頁碼（chunk 內第一個 page break）|
| `page_numbers` | int[]? | chunk 內所有 print-edition 頁碼，sorted ascending |
| `footnotes` | `{int: str}`? | 腳註號 → body text 對應表 |
| `is_volume_header` | bool? | 該 chunk 觸發新 volume；reader 用來決定 TOC 顯示 |
| `edited_at` | ISO timestamp? | ✏️ 編輯按鈕儲存時自動加上 |

## 驗證規則

### STRUCTURAL（違反 = FAIL，不能上架）

| Rule | 描述 |
|---|---|
| R001 | chunk_index 0..N-1 連續 |
| R002 | chunk_type ∈ {page, chapter, section}（DB constraint）|
| R003 | content 非空 |
| R004 | chapter_path 非空 |

### TOC 命名（違反 = WARN，pipeline 應該都通過）

| Rule | 描述 |
|---|---|
| R010 | chapter_path ≤ 35 字（防止標題 regex 吞 body）|
| R011 | 若 volume 設了，chapter_path 必須以 volume 為前綴 |
| R012 | 同 volume 內 chapter_path 不可重複 |
| R013 | 同 volume 內章節 range 連續無缺口（避免 1-10 / 21-30 / 11-20 亂序）|
| R014 | 同 volume 內章節 range 不重疊（避免 substring 撞名 bleed）|
| R015 | page_numbers 跨 chunk 單調遞增（front/back matter 例外）|

### 內容品質（違反 = INFO，可改進但不阻擋）

| Rule | 描述 |
|---|---|
| R020 | 若有 footnotes，source_text 必須有 `[^N]` refs |
| R021 | content 至少含一個 h2/h3/h4 標題 |
| R022 | volume-less chunks < 10% 總 chunks（避免 consolidator 漏標）|

## TOC 顯示標準（reader UI）

### 父著作 (volume) 樹

```
封面 (chunk 0, no volume)
前言 (no volume)
引言 (no volume)
革利免致哥林多人前書       (volume 多頁 → 點開展示子頁)
  └─ 第1-10章
  └─ 第11-20章
  └─ ...
  └─ 第51-59章
致丟格那妥書               (volume 多頁)
  └─ 第1-10章
  └─ 第11-12章
依納爵致羅馬人書           (volume 單頁 → 卷名本身就是 link)
依納爵致以弗所人書         (多頁)
  └─ 第1-10章
  └─ ...
愛任紐《駁異端》卷一       (5 卷各自獨立 volume)
  └─ ...
愛任紐《駁異端》卷二
  └─ ...
```

### 規則

1. **單頁 volume**（≤10 章經 consolidator 合 1 page）：直接顯示為 link，無 ▸ 展開符號
2. **多頁 volume**：顯示展開符號 `▸/▾`，點開後子項剝掉 volume 前綴（「第1-10章」而非「依納爵致以弗所人書 第1-10章」）
3. **Volume entries 一律 level=3 縮排**（不依 heading # 數）—— 避免第一頁 `###` 跟後續頁 `####` 縮排不齊
4. **Front matter chunks**（無 volume）：純 link，**禁止展開 section anchors**（避免 CCEL 書名頁的 credit 行污染 TOC）
5. **章節 anchors**（h3/h4 within chunk）：只在 volume 有設的 chunk 顯示；過濾 enum-only、與 chapter_path 同名、CCEL noise（著/編者/譯者/版權.../ANF\d+/NPNF\d+）

## Reader Vue 是 universal

`pages/ebook/[id].vue` 是**唯一 reader**，所有書共用。Vue 沒書本身的 hardcode，純從上述資料結構 + `/api/ebooks/[id]` 回傳的 `toc` + `currentPage` 渲染。

書要符合本規範，validator 通過後 reader 就會正確渲染。Vue 不需要為某本書改 code。

## 違規時的修補

| WARN 種類 | 修補手段 |
|---|---|
| R010 chapter_path 過長 | re-run `polish_translated_book.py`（更新 SUBTITLE_HARD_CAP / FRONTMATTER_HEAD_RE 邏輯後）|
| R011 volume mismatch | re-run `consolidate_by_ncx.py`（更新 chinese_label substring match 規則後） |
| R012 重複 chapter_path | 同上（chinese_label 撞名 bleed） |
| R013/R014 range 亂序 | 通常是 R012 的連帶；修了 R012 後重 consolidate |
| R015 page_numbers regression | 通常正常（front/back matter）— 可忽略 |
| R020 source_text 缺 ref | re-run `extract_epub_extras.py` |
| R022 太多 volume-less | LETTER_CN_LABELS 缺對應條目，補進去再 re-consolidate |

## 維護紀錄

| 日期 | 修改 |
|---|---|
| 2026-05-24 | 初稿；ANF Vol 1 通過全部 FAIL+WARN；Vol 2 因舊 polish 覆寫 bleed 仍有 411 WARN（需重 consolidate）|
| 2026-05-27 | **ANF Vol 1 重翻 v2 鎖定為模板**。Pipeline 3 步驟（translate→polish→consolidate；extract_epub_extras 已 inline 進 translate parser）。EPUB parser 預帶 `[^N]` refs + `{{p:N}}` 頁碼 + 末尾 `(N) body` 腳註區。PROMPT rule 7 指示 LLM 逐字保留 markers + 翻腳註本文。consolidator chinese_label 用 word-boundary 杜絕 Book I/V 互撞。polish 不覆寫 consolidator 已設 volume。loadToc：page-type chunks 不展開 section anchors，volume-less chunks 不展開（front matter），entries 一律 level=3 縮排。Reader 腳註 sup 純藍粗體無底色，雙向 anchor 互跳。複製文字自動帶芝加哥引用含原書頁碼。|
