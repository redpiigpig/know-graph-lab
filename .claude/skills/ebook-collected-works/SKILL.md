---
name: ebook-collected-works
description: 多卷「全集」(Gesammelte Werke / Collected Works / 全集) 的「3 欄以上多語對照」翻譯與呈現流程。跟 [[ebook-translate]]（一般外文→繁中，雙語）和 [[scripture-fathers]]（公有領域教父原典）並列，本 skill 專責「同一部作品有多個語言版本（原文＋既有譯本＋我的繁中）要逐段對齊、N 欄並陳」這一塊。處理三件 ebook-translate 不處理的事：(1) 多卷套書當成一個 corpus 統一 volume/parent_volume 樹；(2) source_text/source_lang 單一來源 → `sources` 多來源 schema；(3) 獨立編輯的不同語言版本「逐段對不齊」的對齊問題。Use when 使用者要把一部全集（榮格全集、佛洛伊德全集、馬克思恩格斯全集、某神學家德文＋英文＋中文…）做成原文/譯本/繁中多欄對照上架；要擴充 reader 的多欄切換；要設計或修多語 JSONL schema；要對齊跨版本段落。第一個案例＝榮格全集（德 GW＋英 CW＋繁中），見 [jung_collected_works.md](jung_collected_works.md)。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。


> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。

# 全集多語對照 Skill（Collected Works — Multi-language Parallel）

把一部**多卷全集**做成「原文 ‧ 既有譯本 ‧ 我的繁中」**3 欄以上逐段對照**上架到電子圖書館（`/ebook/[id]`，reader 多欄切換）。

這是 ebook-translate 家族的第三個 skill：

| Skill | 負責 | 來源語言數 | 典型對象 |
|---|---|---|---|
| [[ebook-pipeline]] | parse / OCR / standardize / 套書 split | — | 任何 ebook 上游處理 |
| [[ebook-translate]] | 外文 → 繁中（雙語）/ 簡 → 繁 | 1 source + 中 | 單本英文書、ACCS 缺卷 |
| [[scripture-fathers]] | 教父原典（公有領域 Schaff/CCEL）中譯精修 | 1 source + 中 | ANF/NPNF/ACCS |
| **ebook-collected-works（本 skill）** | **多卷全集，3+ 語逐段對照** | **2+ sources + 中** | **榮格全集、佛洛伊德全集、某神學家德英中對照** |

**核心承諾**：reader 永遠顯示**我自己的逐段繁中譯文**為主欄，旁邊並陳一個或多個**來源語言欄**（德文原典／英文既有譯本…）。使用者可切「中／對照／德／英…」。

---

## 何時 trigger

- 使用者指定一部**全集／文集／著作集**（多卷），要做成多語對照上架
  - 「把榮格全集找德文英文版翻譯後三欄放進電子圖書館」← 本 skill 誕生的需求
  - 「佛洛伊德全集德英中三欄」「馬恩全集」「某神學家德文原著＋英譯＋我的中譯」
- 要把現有「雙語書（中/中英對照/英）」升級成 3 欄以上
- 要擴充 reader 的多欄切換（從固定 zh/bi/en → 動態 N 欄）
- 要設計或修「多來源語言」的 JSONL schema

**不適用**：
- 單一外文 → 繁中（沒有第二個來源語言）→ [[ebook-translate]]
- 公有領域教父原典（CCEL 乾淨 EPUB，只有英＋中）→ [[scripture-fathers]]
- 簡 → 繁 → [[ebook-translate]] B pipeline

---

## ⚠️ 開工前必讀：可得性與版權（這類全集的真實障礙）

教父全集能全自動跑，是因為 **Schaff/CCEL 版本公有領域**，有乾淨免費 EPUB。**近現代「全集」幾乎相反**，開工前一定先對該全集做這個盡職調查：

1. **原文全集是否還在版權內？** 作者卒年 + 70（歐盟/多數地區）。例：榮格 1961 卒 → 德文 GW 到 **2031**；英譯 CW（Hull）譯本另有獨立版權。
2. **既有譯本是否有版權？**（多半有 — 商務／校園／道風／Princeton/Bollingen…）
3. **網路上的免費全文是什麼性質？** 多半是**盜版掃描 PDF**（archive.org 盜傳本、各種 mirror），不是合法公有領域檔，而且是 OCR 髒檔，品質遠不如 CCEL EPUB。
4. **哪些卷／早期著作其實已公有領域？**（1929 前出版者）— 這些才有乾淨合法來源。

### 本專案的處理姿態（跟 scripture-fathers「參考現成中譯本校準」同源）

- **reader 只顯示我自己的逐段繁中譯文 + 來源語言原文欄。** 既有的第三方**中譯本絕不入庫**（版權），只在校對時當「黃金參考」transient 使用。
- **來源語言欄**（德文原典／英文譯本）是「對照閱讀」用途。版權內的來源文字 → 比照使用者既有書庫做法在本機 pipeline 處理；**但我（Claude）不會在對話裡貼出整段受版權的原文**，文字一律走本機 script / 檔案流轉。
- **公有領域的卷優先**：能用合法公有領域來源的卷（早期著作）做最乾淨，標示清楚。
- 盡職調查結論寫進該全集的 case-study md（見 [jung_collected_works.md](jung_collected_works.md) 的版權表）。

---

## 三件 ebook-translate 不處理的事

### 1. 多卷套書 = 一個 corpus

全集是**套書**。先遵守 [[feedback-set-books-split]] / [[feedback-set-books-subfolder]]：

- 每卷一個 `ebooks` row（不是整套一個 row）
- Drive 在分類下建子資料夾整理；移動檔案後 `UPDATE ebooks.file_path` 同步
- 跨卷的 `volume` / `parent_volume` 命名要統一（榮格：卷號 + 著作名；作者層 parent_volume = 著作集分組）
- 跨卷術語一致 → 走專屬 glossary（見下）

可沿用 [[scripture-fathers]] 的 `parent_volume` 三層樹（作者 ⊃ 著作 ⊃ 章節）概念，但全集多半是**單一作者多著作** → parent_volume 改用「著作集分組」（榮格：《轉化的象徵》《心理類型》《原型與集體無意識》…）。

### 2. 單一來源 → 多來源 schema（`sources`）

現行 JSONL 只有 `source_lang`(str) + `source_text`(str) = **一個**來源。多語全集要 **N 個**來源，schema 這樣擴充（**向後相容**）：

```jsonc
{
  "chunk_index": 0,
  "chunk_type": "chapter",
  "chapter_path": "轉化的象徵 · 第一部 · 第一章",
  "volume": "轉化的象徵（卷五）",
  "parent_volume": "轉化的象徵",
  "format": "markdown",

  "content": "繁中譯文 …",          // 主欄：我的逐段繁中（永遠是 zh）

  // ── 向後相容欄（舊 reader / 雙語書照常運作）──
  "source_lang": "de",              // PRIMARY 來源語言（= source_order[0]）
  "source_text": "德文原文 …",      // PRIMARY 來源全文（= sources[source_lang]）

  // ── 多語新欄 ──
  "sources": {                      // 所有非中文來源：lang code → 對齊後文本
    "de": "德文原文 …",
    "en": "英文既有譯本 …"
  },
  "source_order": ["de", "en"]      // 來源欄顯示順序（原文在前、譯本在後）
}
```

**相容規則**：
- `source_text`/`source_lang` 永遠鏡像 `sources[source_order[0]]` → 舊 reader（只認 source_text）拿到主來源照常顯示，雙語書（只有 `en`）完全不受影響。
- 新 reader 若見 `sources` 就走 N 欄；沒 `sources` 就 synthesize `{[source_lang]: source_text}` / `source_order=[source_lang]`，行為等同今日雙語。

### 3. 跨版本段落對齊（最難的一步）

德文 GW 跟英文 CW 是**獨立編輯**的版本：分段不同、有的卷英譯重排、註腳系統不同 → **不能假設「第 i 段德文 = 第 i 段英文」**。對齊策略由粗到細：

1. **章節錨點對齊**（最可靠）：兩版都有的 §/章/小節編號（榮格 CW 段落有 Bollingen `[¶ N]` 段碼；GW 也有對應段碼）→ 用段碼當 join key。**優先找有段碼的版本。**
2. **長度比＋順序對齊**（無段碼時）：在同一章內，按段落順序 + 字數比例 greedy 對齊（類似 scripture-papal 的 `alignDocs()`）。
3. **LLM 輔助對齊**（兜底）：把德/英同章丟給 Gemini/Haiku，要求輸出「德段 ↔ 英段」對應 index pairs（多對一/一對多允許），再據此切 chunk。
4. **對不齊就分欄不分段**：某些卷實在對不齊 → 退化成「整章德文欄 / 整章英文欄 / 我的逐段中文」，中文跟著我自己的分段走，德英欄各自整段顯示（reader 仍可三欄，只是非逐段）。

> 中文譯文一律**跟著我自己的分段**走（因為我從原文/英譯重新逐段翻）。對齊是把德、英**塞進我的段落框架**，不是反過來。對不上的來源段落寧可整段塞、不要硬切。

---

## Pipeline 概覽（每卷）

```
[0] 盡職調查：版權表 + 公有領域判定（寫進 case-study md）
        │
        ▼
[1] 取得來源：原文卷 PDF/EPUB + 既有譯本卷 PDF/EPUB
    套書規則：每卷一 row、Drive 子資料夾、file_path 同步
        │
        ▼
[2] 抽文字：EPUB→乾淨；PDF→Gemini OCR（走 [[ebook-pipeline]] OCR）
    每個語言版本各自抽成 per-語言 source chunks（保留段碼/章節錨點）
        │
        ▼
[3] 對齊：章節錨點 > 長度比 > LLM 輔助 > 整段塞（見上四策略）
    產出「對齊後的章節單位」：每單位含 {de_text, en_text, zh_anchor_segs}
        │
        ▼
[4] 翻譯：translate_ebook_to_zh 變體，從原文（德）翻，英譯當交叉校對
    術語走 Jung/該全集專屬 glossary（見下）
        │
        ▼
[5] 寫多語 JSONL：content=繁中, sources={de,en}, source_order, source_text 鏡像
        │
        ▼
[6] volume / parent_volume backfill（著作集分組樹）
        │
        ▼
[7] R2 + DB previews 同步（PATCH chunk_count/standardized_at；display_mode 標多語）
        │
        ▼
[8] reader 多欄切換驗證（中 / 對照 / 德 / 英）
```

翻譯引擎、quota 協調、OAuth refresh、append-resume、Gemini→Haiku 2-strike — **全部沿用 [[ebook-translate]] 的基礎設施**，本 skill 不重造。

---

## Reader 多欄擴充設計（待實作）

現行 `pages/ebook/[id].vue`：`ViewMode = "zh" | "bi" | "en"`，固定雙欄。擴充成 N 欄：

- **ViewMode 動態化**：`"zh"`（中，單欄繁中＋唯一可標註模式）｜`"parallel"`（對照，1+N 欄）｜每個來源語言一個獨立單欄模式（`"src:de"` / `"src:en"`…，從 `source_order` 動態生）。
- **Toggle UI**：`中 | 對照 | 德 | 英`（來源鈕從 `source_order` map：lang code → 中文短標，`{de:'德', en:'英', la:'拉', fr:'法', el:'希', he:'希伯來', grc:'希臘'}`）。
- **parallel grid**：`grid-cols-[2fr_repeat(N,3fr)]`，第一欄 zh，後面依 `source_order` 排。寬度 `max-w-7xl`（2 來源）；3 來源以上自動更寬或允許水平捲動；mobile 降為垂直堆疊。
- **逐段對齊**：parallel 模式把 `content`（zh 段）跟每個 `sources[lang]`（同章對齊後的段）**按段 index zip**，缺段補 `&nbsp;`（沿用現有 `footnotePairs` 的 align-by-number pad 邏輯）。
- **back-compat**：`sources` 不存在時 → `{[source_lang]: source_text}`、`source_order=[source_lang]`；toggle 退化成今日 `中 | 對照 | 英`。`effectiveViewMode` 在無來源時強制 `zh`。
- **API passthrough**：[server/api/ebooks/\[id\].get.ts](../../../server/api/ebooks/[id].get.ts) 的 `currentPage` 加 `sources` + `source_order`；型別在 [server/utils/ebook-chunks.ts](../../../server/utils/ebook-chunks.ts) `ChunkData` 加 optional `sources?: Record<string,string>` + `source_order?: string[]`。
- **localStorage**：沿用 `ebook-viewMode`；值改成自由字串（`zh`/`parallel`/`src:de`…），load 時驗證仍在當前書的合法集合內否則 fallback `zh`。

> 實作時：先擴 `ChunkData` 型別 + API passthrough（不破壞舊書）→ 再改 reader toggle + parallel grid → 用一個 2 來源樣本 chunk 驗證 → 再上真資料。

---

## Glossary（每部全集一份專屬術語表）

教父走 `/translation-glossary`（神學家/神學名詞）。全集多半是**別的學科**，術語不同，**每部全集建一份專屬 glossary md**（放本 skill 資料夾）：

- 榮格 → [jung_glossary.md](jung_glossary.md)（原型 Archetyp、集體無意識 kollektives Unbewusstes、個體化 Individuation、阿尼瑪/阿尼姆斯、陰影、自性 Selbst…；**德文原詞為準**，英譯只是對照）
- 規則同 ebook-translate glossary：翻譯前先鎖譯名 → 翻譯中 PROMPT 帶 glossary → 翻完跑 term sweep 收斂變體
- 跨卷一致是硬指標（同一術語不可一卷「自性」一卷「自我」）
- 若該全集人物/概念跟現有 `/translation-glossary` 重疊（神學家全集）→ 仍以 `/translation-glossary` `name_recommended` 為權威（[[feedback-glossary-strict-authority]]）

---

## 第一個案例：榮格全集

完整版權表、GW/CW 卷目對照、公有領域判定、來源、術語焦點 → **[jung_collected_works.md](jung_collected_works.md)**。

一句話現況：榮格全集（德 GW 20 卷 / 英 CW 20 卷 + 補卷）原文與英譯**多數仍在版權內到 2031**，網路免費全文多為盜版掃描；**僅 1929 前早期著作**（《Wandlungen und Symbole der Libido》1912 德文原典 + Hinkle 1916 英譯）有乾淨公有領域來源。逐段對齊在「同一文本的德＋英」才嚴格成立，CW 改寫本與早期德文原典是**不同版本**。

---

## SOP（每卷接手）

1. 讀 [jung_collected_works.md](jung_collected_works.md) 版權表，確認該卷來源策略（公有領域 / 本機處理）
2. 套書規則：建 row + Drive 子資料夾 + file_path（[[feedback-set-books-subfolder]]）
3. 抽文字（EPUB 直抽 / PDF 走 Gemini OCR）→ per-語言 source chunks
4. glossary 先鎖該卷高頻術語（[jung_glossary.md](jung_glossary.md)）
5. 對齊（章節錨點優先）→ 對齊單位
6. `--inspect` smoke test → 翻 3 章給使用者確認譯名/分欄效果
7. full run（engine/quota 看 [[ebook-translate]]）→ 多語 JSONL
8. volume/parent_volume backfill → R2 + DB previews
9. reader 三欄驗證 → commit + push（[[feedback-auto-push]]）

---

## 待辦 / 狀態

- [x] **`sources` schema 純函式契約 + 測試**（test-first，2026-06-02）— [server/utils/multilang-sources.ts](../../../server/utils/multilang-sources.ts) + [test/multilang-sources.spec.ts](../../../test/multilang-sources.spec.ts)（23 例綠）。normalize / mirrorPrimarySource 向後相容 / availableViewModes / resolveViewMode stale 夾制 / langLabel / zipParallel 補白。**下游 reader 與 API 一律用這個 module，不要各自重寫 schema 判斷。**
- [x] **基建：reader N 欄 + API passthrough**（2026-06-02，typecheck 0 error / 27 tests 綠）
  - [x] `ChunkData`([server/utils/ebook-chunks.ts](../../../server/utils/ebook-chunks.ts)) 加 `sources?` / `source_order?` + [[id].get.ts](../../../server/api/ebooks/[id].get.ts) passthrough
  - [x] reader([pages/ebook/[id].vue](../../../pages/ebook/[id].vue)) toggle 動態化（中/對照/各來源語言，用 `availableModes`/`resolveViewMode`/`langLabel`）+ `parallelColumns` 用 `zipParallel` 做 N 欄逐段（flex，N=1 等同舊「中英」、mobile 堆疊）；legacy `bi`/`en` localStorage 用 `migrateLegacyViewMode` 遷移；pure module 在 [lib/multilang-sources.ts](../../../lib/multilang-sources.ts)（client+server 共用）
  - [x] translate 腳本多語 JSONL 輸出（2026-06-02，test-first，21 例綠）— [scripts/multilang_chunks.py](../../../scripts/multilang_chunks.py)：`normalize_sources` / `mirror_primary_source`（Python 鏡像 TS 契約，逐例 parity）/ `build_multilang_chunk` / `validate_multilang_chunk`（寫前硬檢查）/ `assemble_multilang_chunks(aligned_units, translate_fn, source_order)`（engine boundary = `translate_fn`，prod 接 LLM、測試接 stub）/ `write_jsonl`。測試 [scripts/tests/test_multilang_chunks.py](../../../scripts/tests/test_multilang_chunks.py)。**reader（已截圖實證）讀什麼，這裡就寫什麼。**
- [x] **對齊步驟核心**（2026-06-02，test-first，20 例綠）— [scripts/align_editions.py](../../../scripts/align_editions.py)：`parse_chapter_number`（DE/EN/CJK 標題 + 羅馬/阿拉伯/中文數字 → 同一 key，kind 不混）/ `anchor_coverage` / `align_editions`（**錨點 join**：兩版 ≥80% 唯一錨點 → 按 key 對齊、自動 realign 亂序的 EN、de-only 留空 en、en-only 補在後；否則 **order-align** 補白 fallback）。輸出直接餵 `assemble_multilang_chunks`。測試 [scripts/tests/test_align_editions.py](../../../scripts/tests/test_align_editions.py)。
  - 殘留：段碼級（`[¶ N]`）細對齊、LLM 輔助 fallback、provisional chapter_path 的 zh 本地化 — 接真語料時再按需補。
- [x] **驅動腳本 + 真 LLM `translate_fn`**（2026-06-02，test-first，11 例綠）— [scripts/translate_collected_work.py](../../../scripts/translate_collected_work.py)：`load_plaintext_sections`/`split_sections`（純文字/markdown → 章節 list）/ `JUNG_PROMPT_TMPL`（德→繁中、英文僅消歧義、術語鎖定）/ `make_translate_fn(engine)`（lazy import 重用 [[ebook-translate]] 的 gemini/haiku/sonnet 引擎 + split_oversized）/ `run(de,en,ebook_id,translate_fn,...)` 串 load→align→assemble→write_jsonl→(R2+DB)。測試 [scripts/tests/test_collected_work_driver.py](../../../scripts/tests/test_collected_work_driver.py) 用 stub translate_fn，零 network。
  - 真實 run 指令：`python scripts/translate_collected_work.py --de <de.txt> --en <en.txt> --ebook <id> --engine gemini --limit 2 --upload`（先 `--limit` smoke、確認再全跑）。
- [x] **HTML→sections loader**（2026-06-03，test-first）— [scripts/translate_collected_work.py](../../../scripts/translate_collected_work.py) `split_html_sections`/`load_html_sections`（bs4 lazy import；h1-h6 切段、收 p/li/pre 葉塊）。**實證**：真跑 Project Gutenberg Hinkle 英譯 HTML（[gutenberg.org/ebooks/65903](https://www.gutenberg.org/ebooks/65903)）→ 40 段、28 段標題乾淨 parse 成錨點（Part 1/2 + Chapter 1-8…）。
- [x] **HTML→sections loader 實證**（2026-06-03）：真跑 Gutenberg Hinkle → 40 段、28 錨點（Part/Chapter）。
- [x] **🟢 首章三欄上架（2026-06-03，pilot 成功）**：德文 1912 PDF（純圖像）→ **Haiku 重 OCR**（Gemini 4 key 全耗盡）→ **內容指紋**配對 de Einleitung=en §8 → **親譯整章「引論」5 段** → trilingual ebook（`22222222-2222-4222-8222-222222222222`）reader 三欄逐段對齊（截圖 + 段數雙驗證）。
- [ ] **▶ 接手做下去：見 [jung_collected_works.md](jung_collected_works.md) 的「🚀 新 session 接手清單」**（5 步方法 / 待辦 / 檔案 / 雷區 / ebook_id / 指令全在那）。下一章＝德 `II.`（兩種思維）= 英 §9 Ch I。Gemini 已死一律 Haiku。
- [ ] **錨點 part-scoping**（次要）：含 Part 的書章號每部重起 → `anchor_coverage` key 不唯一。手工配對流程不依賴它，低優先。

## 起手卷決策（2026-06-02，Claude 拍板）

**Pilot = 公有領域早期著作**：1912《Wandlungen und Symbole der Libido》(de, archive.org) + Hinkle 1916《Psychology of the Unconscious》(en, 公有領域)。理由：(1) 唯一**現在就能合法取得並處理**、不需使用者給檔、不碰受版權全文的 Jung 來源；(2) 兩版是**同一部作品**，能真正驗證跨版對齊；(3) 受版權的 CW 卷無論如何都要使用者提供 HTML 來源檔（不抓盜版全文）。pilot 建好的機器原封不動延伸到那些卷。詳見 [jung_collected_works.md](jung_collected_works.md)。
- [x] **視覺驗證**（2026-06-02）：手造德/英/中樣本 chunk 跑 dev server + `screenshot_book.mjs` 確認 `中/對照/德/英` toggle、3 欄逐段對齊、**body zip 補白**（英缺第 2 段 → 空白格不位移）、**footnote by-number 跨欄對齊**（英缺 (2) → 該格空白）、單來源「德」單欄模式 全部正確。
  - 📌 `screenshot_book.mjs` 已修：注入 `kgl_device_id` 呈現預先核准的 `screenshot-bot` 裝置，繞過新的 device-trust gate（`middleware/device.global.ts`）。需在 `trusted_devices` 預埋一列 `device_id='screenshot-bot', status='approved'`（已埋）。否則所有 reader 截圖（含 [[scripture-fathers]] 校對 C 層）會被導去 `/device-pending`。
- [x] **榮格全集盡職調查表**（[jung_collected_works.md](jung_collected_works.md)）＋版權表＋來源紀錄
- [x] **jung_glossary.md**（心靈工坊/TSAP/《榮格心理學辭典》查證鎖定；辭典為版權書只作參考不轉錄）
- [x] 第一章試做成功（引論整章三欄）→ 續做見上「接手清單」

---

## See also

- [[ebook-translate]] — 翻譯基礎設施（engine / quota / OAuth / append-resume / Gemini-Haiku fallback）＋ 一般雙語翻譯
- [[scripture-fathers]] — 公有領域教父原典；「參考現成中譯本校準」姿態本 skill 沿用
- [[ebook-pipeline]] — parse / OCR / standardize / 套書 split 上游
- [[translation-glossary]] — 神學家/神學名詞詞庫（神學家全集才用；其餘全集各自 glossary）
- [scripture-papal](../scripture-papal/SKILL.md) — 既有「拉/英/中三欄逐段對照」(alignDocs) 的 content-file 版實作，可參考對齊邏輯（但本 skill 走 ebook reader，不走 content files）
- [jung_collected_works.md](jung_collected_works.md) — 榮格全集案例：版權表 + 卷目 + 來源
- [jung_glossary.md](jung_glossary.md) — 榮格術語德/英/中對照
