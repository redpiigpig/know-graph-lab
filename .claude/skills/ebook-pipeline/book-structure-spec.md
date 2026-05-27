# 電子書資料結構規範（Book Structure Spec）

每本書經過完整 pipeline（translate → polish → consolidate_by_ncx → repatch → sweep）後，存在 Drive `_chunks/{ebook_id}.jsonl` 並推送 R2，必須符合本規範。

兩個檢查器分別管不同類型的 bug：

| 工具 | 抓什麼 |
|---|---|
| [`scripts/validate_book_structure.py`](../../../scripts/validate_book_structure.py) | 結構 / TOC / 章節 range（R001-R022），FAIL=不可上架 |
| [`scripts/scan_translated_book.py`](../../../scripts/scan_translated_book.py) | LLM 翻譯品質（T1-T7）：標題吞內文、卷名 vs h3 漂移、索引誤掛、封面/前言命名 |

```bash
python scripts/validate_book_structure.py <ebook_id>     # 單本結構
python scripts/scan_translated_book.py    <ebook_id>     # 單本品質
python scripts/validate_book_structure.py --all          # 全庫
python scripts/scan_translated_book.py    --all          # 全庫品質
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
| `volume` | str? | 父著作中文名稱（如「巴拿巴書信」「依納爵致以弗所人書」）；front matter 為 null |
| `parent_volume` | str? | 教父／作者中文名（如「依納爵」「里昂的愛任紐」），sidebar 用來把同一作者的多卷收摺到一個展開節點下。Schaff ANF/NPNF 多作者集必設；單作者書 / front matter 為 null |
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

### 翻譯品質（scan_translated_book.py，違反 = WARN）

| Rule | 描述 |
|---|---|
| T1 | h3/h4 標題吞內文：標題尾端不是「。！？」」且含「既然/誠然/親愛的/讓我們/蓋/雖然」等 body marker → 翻譯時把內文第一句連到標題後 |
| T2 | volume 名 vs 內文首個 h3 漂移：volume＝「致丟格那妥書」但 h3＝「瑪忒特致狄奧格尼特斯書信」→ LLM 沒對齊術語 |
| T4 | chapter_path 含 markdown 控制字元 `* _ [^N]` |
| T5 | 同 volume 名在 jsonl 順序不連續（A → B → A 又出現）|
| T6 | 結尾 chunk 的 chapter_path 含「索引」但 volume 不是「索引」（前次 polish bleed 把索引掛到最後一作者下）|
| T7 | chunk 0 chapter_path != 「封面」或 chunk 1 不是「前言／序言／書名頁」|

### 內容品質（違反 = INFO，可改進但不阻擋）

| Rule | 描述 |
|---|---|
| R020 | 若有 footnotes，source_text 必須有 `[^N]` refs |
| R021 | content 至少含一個 h2/h3/h4 標題 |
| R022 | volume-less chunks < 10% 總 chunks（避免 consolidator 漏標）|

## TOC 顯示標準（reader UI）

### 三層樹（parent_volume → volume → entries）

Schaff ANF/NPNF 等多作者集走三層；單作者書（基督教要義、信仰精意等）`parent_volume` 全 null，sidebar 自動 fallback 兩層樹。

```
封面 (chunk 0, no volume)
前言 (no volume, 已併入 Title Page)
介紹說明 (no volume)
─ 羅馬的革利免 ▾                  (parent_volume 第一層；點 ▾ 折疊)
    革利免致哥林多人前書 ▸ (6)    (volume 第二層；多頁 → ▸)
      └─ 第1-10章                (entries 第三層)
      └─ ...
─ 瑪忒特 ▾
    致丟格那妥書 ▸ (2)
─ 依納爵 ▾
    依納爵致以弗所人書 ▸ (3)
    依納爵致馬內夏人書 ▸ (2)
    ...
    依納爵殉道記                  (volume 單頁 → 直接 link)
─ 里昂的愛任紐 ▾
    愛任紐《駁異端》卷一 ▸ (4)
    ...
    愛任紐《駁異端》卷三 ▸ (3)    (末頁含 Elucidation 已 fold 進去)
    愛任紐《駁異端》卷四 ▸ (5)
    愛任紐遺著殘篇 ▸ (6)
希伯來文詞彙與片語索引 (no volume, 索引)
印刷版頁碼索引 (no volume)
```

### 規則

1. **單頁 volume**（≤10 章經 consolidator 合 1 page）：直接顯示為 link，無 ▸ 展開符號
2. **多頁 volume**：顯示展開符號 `▸/▾`，點開後子項剝掉 volume 前綴（「第1-10章」而非「依納爵致以弗所人書 第1-10章」）
3. **Volume entries 一律 level=3 縮排**（不依 heading # 數）—— 避免第一頁 `###` 跟後續頁 `####` 縮排不齊
4. **Front matter chunks**（無 volume）：純 link，**禁止展開 section anchors**（避免 CCEL 書名頁的 credit 行污染 TOC）
5. **章節 anchors**（h3/h4 within chunk）：只在 volume 有設的 chunk 顯示；過濾 enum-only、與 chapter_path 同名、CCEL noise（著/編者/譯者/版權.../ANF\d+/NPNF\d+）
6. **parent_volume 第一層**：開書時所有 parent 預設展開（避免使用者要點 7 次才看到全內容）；點 ▾ 折疊；點當前章節時所屬的 parent 自動 expand
7. **封面／前言**：consolidate_by_ncx + repatch 階段固定改寫——chunk 0 chapter_path 永遠改成「封面」；如果第 1、2 chunk 是「書名頁 + Preface」模式，merge 成單一「前言」（避免 sidebar 出現「前尼西亞教父」這種書名重複列）
8. **Elucidation / 註解**：CCEL NCX 把「Elucidation」放在 Book III 與 Book IV 之間獨立 navPoint；consolidator 偵測 `letter_label` 含 "Elucidation" 且 0 子章節 → fold 到**前**一個 letter 的最後一頁（不是獨立 volume）
9. **後段索引（Indexes parent 下的子頁）**：consolidator 與 repatch 都會清掉這些 chunk 的 stray volume／parent_volume，使其在 sidebar 顯示為 front matter 風格（無 volume 群組）

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
| T1 heading bleed | `python scripts/sweep_book_quality.py <id> --only-t1` — 規則 sweep，把標題尾端的 body marker 後段 prepend 進下一段 |
| T2 h3 letter-title drift | `python scripts/sweep_book_quality.py <id> --only-t2` — 把 chunk 內單一 h3 改成 volume 名；**多 h3 跨書 bleed 不處理**，需要 chunk 級別搬運（手動修） |
| T6 索引誤掛 / T7 封面命名 | `python scripts/repatch_consolidated_book.py <id>` — 不重翻、不重 consolidate，直接套 normalize 規則 |

## 維護紀錄

| 日期 | 修改 |
|---|---|
| 2026-05-24 | 初稿；ANF Vol 1 通過全部 FAIL+WARN；Vol 2 因舊 polish 覆寫 bleed 仍有 411 WARN（需重 consolidate）|
| 2026-05-27 | **ANF Vol 1 重翻 v2 鎖定為模板**。Pipeline 3 步驟（translate→polish→consolidate；extract_epub_extras 已 inline 進 translate parser）。EPUB parser 預帶 `[^N]` refs + `{{p:N}}` 頁碼 + 末尾 `(N) body` 腳註區。PROMPT rule 7 指示 LLM 逐字保留 markers + 翻腳註本文。consolidator chinese_label 用 word-boundary 杜絕 Book I/V 互撞。polish 不覆寫 consolidator 已設 volume。loadToc：page-type chunks 不展開 section anchors，volume-less chunks 不展開（front matter），entries 一律 level=3 縮排。Reader 腳註 sup 純藍粗體無底色，雙向 anchor 互跳。複製文字自動帶芝加哥引用含原書頁碼。|
| 2026-05-27 | **schema 加 `parent_volume`**（教父／作者中文名）→ sidebar 三層樹（parent → volume → entries），Schaff 多作者集適用；單作者書 fallback 兩層。consolidate_by_ncx 新增「Elucidation」back-fold 規則（折進前一封 letter 最後一頁）+ 封面強制改名「封面」+ 書名頁＋Preface merge 成「前言」+ 索引尾頁 stray volume 清除。新增 [`repatch_consolidated_book.py`](../../../scripts/repatch_consolidated_book.py)：對已 consolidate 的 JSONL 做 in-place 套規則，不重翻、不重 walk NCX。新增 [`scan_translated_book.py`](../../../scripts/scan_translated_book.py)：T1-T7 翻譯品質 scanner（body-marker mid-heading 偵測標題吞內文、volume vs first-h3 漂移、orphan index、封面/前言命名）。新增 [`sweep_book_quality.py`](../../../scripts/sweep_book_quality.py)：T1+T2 規則自動修——標題 bleed 切到 body marker 處、單 h3 letter-title 改成 volume 名。ANF Vol 1 結果：114→112 chunks，T1 39→0、T2 28→8（剩 8 個跨書 bleed），T6/T7 全清，validator 0 FAIL/0 WARN。|
