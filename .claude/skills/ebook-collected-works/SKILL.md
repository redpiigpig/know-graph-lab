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

- **reader 主欄＝我自己的逐段繁中譯文 + 來源語言原文欄。** 既有的第三方中譯本預設**不當主欄**（版權＋品質自主），公開散布情境下只在校對時當「黃金參考」transient 使用。
  - **私人自用例外（user 拍板 2026-06-12）**：本站既是私人研究圖書館，**有第三方中譯本可入庫當「參考層」**（簡體先 opencc→繁中，[[feedback_traditional_chinese_only]]），但**僅供我校對對照／使用者參照，不取代我的逐段自譯主欄**——同 [[scripture-fathers]]「參考現成中譯校準」姿態，只是這裡可落地成資料而非純 transient。標示清楚「第三方譯本‧參考」。
- **來源語言欄**（德文原典／英文譯本）是「對照閱讀」用途。版權內的來源文字 → 比照使用者既有書庫做法在本機 pipeline 處理；**但我（Claude）不會在對話裡貼出整段受版權的原文**，文字一律走本機 script / 檔案流轉。
- **公有領域的卷優先**：能用合法公有領域來源的卷（早期著作）做最乾淨，標示清楚。
- **私人自用 → 受版權卷可用 shadow library 取來源檔（user 拍板 2026-06-12）**：本站是 **auth-gate 後的私人研究圖書館、僅供使用者個人閱讀**（非公開散布）。故受版權著作若無公有領域來源、archive.org 又只借閱不放，**可從 shadow library（Anna's Archive / Library Genesis 等）抓來源 PDF/EPUB 到本機**，比照 [[feedback_jung_nonpd_english_first]]「私人站非 PD 可用、英文先輸入」。鐵則不變：(1) 一律 **English-first**，主欄是**我自己的逐段繁中譯文**（轉化作品），(2) 來源原文**只走本機檔／script**、**絕不貼進對話**，(3) 下載走 `curl`/Bash 到 `c:/tmp` 或本機，再 `--src` 餵 pipeline。⚠️ **環境網路限制**：此 sandbox 多數 shadow 鏡像（annas-archive、libgen.is/.rs）**DNS 被擋**，僅 `libgen.li` 可達且常只索引期刊書評非專書 → 抓不到時請 user 在自己機器下載後把檔丟本機（new-book drop / `c:/tmp`）。
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

## 全集 Portal + 作家 Hub 頁（最外層，2026-06-05）

全集**不放在電子圖書館（/ebook）裡**，而是獨立的 `/collected-works` portal（首頁新增「📚 全集」cyan 卡）。

**portal 依學科分組（2026-07-01，user 拍板）**：`CwAuthor.disciplineGroup`（新欄）＝作家所屬學科，portal 依此分區顯示（順序常數 `DISCIPLINE_ORDER = ['哲學','社會學','宗教學','神學','佛學','心理學','人類學']`，未列出的學科接最後、空組不顯示，見 [pages/collected-works/index.vue](../../../pages/collected-works/index.vue)）。現況歸類：**哲學**＝古希臘六 hub（見案例 7）；**宗教學**＝穆勒；**神學**＝潘尼卡；**佛學**＝印順‧聖嚴‧星雲；**心理學**＝榮格。`disciplineGroup` 別跟既有的 `discipline`（一句話副標）搞混。新增作家務必填 `disciplineGroup`。

每位學者一張卡 → 點進**作家 hub 頁** `/collected-works/[slug]`，最外層呈現：

1. **學術貢獻簡介**（`contribution: string[]`，繁中段落，支援 `**粗體**`）
2. **肖像**（`portraitUrl`：Wikimedia Commons `Special:FilePath/<檔名>?width=500` 公有領域縮圖，**不用 Supabase Storage**）
3. **生平學術年表**（`timeline: {year, text}[]`，左側時間軸）
4. **著作目錄**（`works[]`，**按 `category` 分組、組內依 `yearSort` 排序**；每筆顯示年分／繁中名／原文名／來源語言標／轉錄狀態）

**單卷閱讀仍走既有 `/ebook/[id]` 多欄 reader**（work.ebookId 連過去）；hub 只是「最外層」入口 + 完整書目 + 路線圖。

### 資料：`stores/collectedWorks.ts`（repo-committed，沿用 /works·speech.ts 模式）

- 直接改本檔新增／編輯作家與書目，**免 DB migration、免 server route**（user 拍板 2026-06-05）。
- `WorkStatus`：`done`（已轉錄→reader）/ `in-progress`（轉錄中，可連 pilot ebook）/ `planned`（待轉錄）/ `copyright`（受版權待合法來源）。狀態 badge：綠／琥珀／灰／石。
- **新增一位全集學者** = 在 `authors[]` push 一個 `CwAuthor`（slug/name/portraitUrl/color/contribution/timeline/works）。color 必須在 [tailwind.config.ts](../../../tailwind.config.ts) safelist 內（amber/blue/rose/emerald/violet/sky/indigo/cyan/orange/stone/purple/teal，shade 50–300/500–700；**別用 -400**）。
- **某卷轉錄完成** = 把該 `work` 的 `status` 改 `done`／`in-progress` 並填 `ebookId`，hub 那筆即變成連到 reader 的可點列。
- 目前：穆勒（slug `max-mueller`，sky，16 筆書目）＋榮格（slug `jung`，rose，早期著作連 pilot ebook `22222222-…`）。

### 驗證（已實證 2026-06-05）

dev server 起 → 磁碟認證（reuse `screenshot_book.mjs` 的 magic-link＋service-role cookie 注入 + `kgl_device_id=screenshot-bot`）→ playwright 截 portal/hub。3 頁皆正確渲染（肖像載入、粗體、時間軸、書目分組排序、狀態 badge、in-progress 連 reader）。一次性截圖腳本用完即刪（`_`-prefix 在 scripts/ **未** gitignore，別 commit）。

---

## Glossary（每部全集一份專屬術語表）

教父走 `/translation-glossary`（神學家/神學名詞）。全集多半是**別的學科**，術語不同，**每部全集建一份專屬 glossary md**（放本 skill 資料夾）：

- 榮格 → [jung_glossary.md](jung_glossary.md)（原型 Archetyp、集體無意識 kollektives Unbewusstes、個體化 Individuation、阿尼瑪/阿尼姆斯、陰影、自性 Selbst…；**德文原詞為準**，英譯只是對照）
- 馬克斯‧穆勒 → [mueller_glossary.md](mueller_glossary.md)（宗教學 the science of religion、單一神教 henotheism、語言的疾病、無限者 the Infinite、雅利安/閃/圖蘭語族…；**英文原詞為準**，德文作對照）
- 規則同 ebook-translate glossary：翻譯前先鎖譯名 → 翻譯中 PROMPT 帶 glossary → 翻完跑 term sweep 收斂變體
- 跨卷一致是硬指標（同一術語不可一卷「自性」一卷「自我」）
- 若該全集人物/概念跟現有 `/translation-glossary` 重疊（神學家全集）→ 仍以 `/translation-glossary` `name_recommended` 為權威（[[feedback-glossary-strict-authority]]）

---

## 案例

### 案例 1：榮格全集

完整版權表、GW/CW 卷目對照、公有領域判定、來源、術語焦點 → **[jung_collected_works.md](jung_collected_works.md)**。

一句話現況：榮格全集（德 GW 20 卷 / 英 CW 20 卷 + 補卷）原文與英譯**多數仍在版權內到 2031**，網路免費全文多為盜版掃描；**僅 1929 前早期著作**（《Wandlungen und Symbole der Libido》1912 德文原典 + Hinkle 1916 英譯）有乾淨公有領域來源。逐段對齊在「同一文本的德＋英」才嚴格成立，CW 改寫本與早期德文原典是**不同版本**。

### 案例 2：馬克斯‧穆勒全集（宗教學家全集，2026-06-04 起）

版權表、Longmans《Collected Works》18 卷目、來源、對齊策略、接手清單 → **[mueller_collected_works.md](mueller_collected_works.md)**。

一句話現況：弗里德里希‧馬克斯‧穆勒（Friedrich Max Müller, 1823–1900，**宗教學開山祖**）卒於 1900 → **全部著作早已公有領域、全球無限制**，archive.org/Gutenberg 有乾淨全文，是 collected-works 最乾淨案例。穆勒以**英文寫作為主** → 預設英＋繁中雙語；少數有平行德文版的卷（如起手卷《宗教學導論》1873 = 德文《Einleitung》1874，**英德同構四講＋兩附論**）做真三欄。語言策略（user 拍板）：**英＋德＋繁中三欄，僅限有德文版的卷**。起手卷＝《宗教學導論》。**這是「經典宗教學家全集」系列的第一部**（後續可接其他宗教學家）。

### 案例 3：雷蒙‧潘尼卡全集（宗教間對話／比較神學，2026-06-12 起）

版權表、Opera Omnia 12 卷目、起手卷決策、來源、對齊策略、詞庫焦點、接手清單 → **[panikkar_collected_works.md](panikkar_collected_works.md)**。

一句話現況：雷蒙‧潘尼卡（Raimon Panikkar, 1918–2010，**宗教間／宗教內對話與跨文化哲學巨擘**）卒於 2010 → **全部著作受版權至約 2080**，**跟榮格同型（非穆勒）**：網路無乾淨合法公有領域全文、第三方中譯不入庫。採 **English-first**（[[feedback_jung_nonpd_english_first]]，私人站非 PD 可用、英文先輸入）。他**用多語原創**（加泰隆／西／義／英／德），Opera Omnia（Jaca Book 義文／Orbis 英文，12 卷，Milena Carrara Pavan 主編）是**主題重編**，逐段三欄只在「同一文本恰有原文＋英譯」時嚴格成立 → 多數卷先英＋繁中雙語。語言策略（user 拍板 2026-06-12）：**English-first，英＋繁中雙語為預設；個別文本有平行原文版再升英＋原文＋繁中三欄**。起手卷＝**《印度教中未識的基督》**（原文即英文，1964/1981）。build 腳本 `scripts/panikkar_build.py`（test-first，22 例綠 `scripts/tests/test_panikkar_build.py`；reflow/align/section-chunk 比照 mueller_build）。**這是 collected-works 第三部、第一部「受版權當代神學家」案例。**

**兩種 build 模式（user 拍板 2026-06-12）**：(1) **REFERENCE 模式** `--src <en> --zh-src <zh>`：**已有完整中譯就不重譯**，把既有第三方中譯（簡→繁）當主欄、英文原典逐段對照入庫，零 LLM（潘尼卡有王志成/思竹整套中譯，起手卷《印度教中未識的基督》即走此模式）；(2) **自譯模式** `--src <en>`：無中譯的卷才走 English-first 引擎自譯。CJK 章標題（導論/第N章/第N節…）由 `_CJK_HEADING_RE` 偵測切段。

### 案例 4：印順導師全集（第一個「單一語言」案例，2026-06-13 起）

來源定案、CBETA TEI 結構、書目→volume 樹、版權姿態、全量清單 → **[yinshun_collected_works.md](yinshun_collected_works.md)**。

一句話現況：印順導師（1906–2005，**人間佛教思想巨擘**）全集**本即繁體中文** → collected-works 第一個**零翻譯、零跨語對齊**案例，pipeline 砍剩「解析→JSONL→DB/R2→hub」，reader 退化單欄（無 `sources`，向後相容）。來源＝**CBETA Y 系列 TEI P5 XML**（`cbeta-org/xml-p5`，44 XML=42 部，非商業可再散布，遠優於已改版的基金會官網）。`cb:mulu` 三層→章節樹、`lb` 邊碼→段碼錨點（已用 Y08《佛法概論》實證）。**同法適用接續的聖嚴法師（法鼓全集）、星雲大師全集。**

### 案例 5：聖嚴法師《法鼓全集 2020 紀念版》（單一語言案例 #2，2026-06-13）

來源架構、資料模型、雷區、全量清單 → **[shengyen_collected_works.md](shengyen_collected_works.md)**。

一句話現況：聖嚴法師（1930–2009，**法鼓山創辦人、學問僧**）全集亦本即繁中 → 沿用印順單語 pipeline，**唯一差別＝來源解析器 HTML 而非 TEI**，下游入庫/hub/reader 全共用。來源＝ ddc.shengyen.org（法鼓文化官方數位版，SPA 殼但靜態檔可全枚舉：`all_books`110冊／`vol_dump`4079篇／`toc.html`章節樹／`html/{輯-冊-篇}.html`正文）；`p.indent`正文／`p.hN`標題／`span.pb data-page`**保留原書頁碼**。**已完成 110 冊 / 4181 chunks 上架**（`shengyen_build.py`，9 例測試綠，slug `shengyen`，teal/🥁）。雷區：requests 要帶 UA+verify=False+指數退避重試（server 高載丟連線）、`--all` 要 per-book try/except+`--resume`、reader 截圖 ~3970px 須裁、dev server 多任務衝突另起 PORT=3100。

### 案例 6：星雲大師全集（✅ 完成，via /ArticleDetail，2026-06-14）

來源探源、全文端點、現況產出 → **[hsingyun_collected_works.md](hsingyun_collected_works.md)**。

### 案例 7：古希臘哲學家全集（第一個「哲學」學科群，hub 骨架，2026-07-01 起）

一句話現況：portal 改依學科分組後，新增「**哲學**」學科群，第一批建六個 hub 骨架（著作目錄多為 `planned`，逐步轉錄）：**柏拉圖**（`plato`，blue，Stephanus＋Jowett 英譯／早中晚期對話錄＋書信）、**亞里斯多德**（`aristotle`，emerald，Bekker＋Ross 英譯／工具論‧自然哲學‧生物學‧形上學‧倫理政治‧修辭詩學）、**前蘇格拉底與蘇格拉底**（`presocratics`，stone，Diels-Kranz 殘篇＋第歐根尼‧拉爾修＋色諾芬；蘇格拉底無著作）、**伊比鳩魯**（`epicurus`，cyan，三書信＋主要教義＋附盧克萊修）、**愛比克泰德**（`epictetus`，violet，手冊＋談話錄＋斯多噶傳統參照）、**普羅提諾**（`plotinus`，purple，《九章集》六集＋波菲利傳）。全屬**公有領域**（古典原文＋十九世紀權威英譯 Jowett/Ross/MacKenna），可做希臘／英／繁中三欄對照——接手轉錄比照榮格 pipeline，人名先查 [[translation-glossary]] 鎖譯名（哲學家表）。肖像皆用 Wikimedia Commons 公有領域胸像（已驗證可載）。

### 案例 6：星雲大師全集（✅ 完成，via /ArticleDetail，2026-06-14）

一句話現況：星雲大師（1927–2023，**佛光山開山宗長**）全集 — 官網 reader 殼（`/bcN/bookM` 空殼、sitemap 38 URL、無 XHR）一度誤判「不出全文」，**但 user 給出 `/ArticleDetail/artcle{N}` 後破關**：每篇免登入 server-render 全文 + 麵包屑階層（大類/冊/篇），不在 sitemap、reader 殼不揭露。**已全量上架**：crawl `artcle{1..25500}`（19,888 篇有效、err=0 未被封鎖）→ 麵包屑 `book_key` 分組成 **109 冊 / 19,997 chunks**（slug `hsingyun`，orange/🪷，按 12 大類）。`scripts/hsingyun_build.py`（parse_article/classify_breadcrumb/crawl 禮貌節流+退避+resumable/`--build --resume` per-book 容錯，10 例綠）。**教訓：薄殼 JS 站找不到內容端點時，直接問 user 要一個「實際在讀的文章 URL」往往秒破關（內文常走 sitemap 外的另一條 MVC 路由）。**

---

## 📕 漢傳佛教／中文「單一語言」全集 — 抓取與入庫 PLAYBOOK

> 印順(CBETA)/聖嚴(法鼓全集)/星雲(masterhsingyun) 三套累積的通用做法。**任何「本即繁中、要逐冊上架的中文全集」都照這套**（榮格/穆勒/潘尼卡那套多語對齊**不適用**，這裡零翻譯零對齊）。下游入庫/hub/reader 三套完全共用，新案例**只需寫來源解析器**。

### 0. 單一語言鐵則
- **零翻譯、零跨語對齊**：`content` = 原文繁中本身；chunk **不寫 `sources`/`source_text`** → reader 自動退化單欄（[[multilang-sources]] 向後相容）。
- 一書（冊）＝ 一個 `ebooks` row；一篇（章/節/條目）＝ 一個 chunk；`parent_volume` = 大類/著作集分組、`volume` = 書名、`chapter_path` = 書名 · [章節…] · 篇名。
- **保留原書頁碼**（[[feedback_pdf_page_number]]）：CBETA `lb` 邊碼 / 法鼓 `span.pb data-page` / 星雲麵包屑 `pNNN` → 存進 `chunk.page_number`。
- deterministic `ebook_id` 每作家一個命名空間：印順 `a0000000-…-NN`、聖嚴 `b0000000-…`、星雲 `c0000000-…`；registry JSON committed 進 skill 資料夾。

### 1. 開工第一步：來源分級（決定可行性，**別跳過**）
| 來源型態 | 範例 | 做法 |
|---|---|---|
| **結構化標記**（TEI/XML/EPUB） | CBETA `cbeta-org/xml-p5` Y 系列 | 最佳；GitHub raw 直抓，`cb:mulu`/`cb:div` 巢狀＝章節樹。非商業可再散布 |
| **靜態每篇 HTML、可枚舉** | 法鼓 `getData.php?type=vol_dump`+`html/{id}.html` | 好；先抓「枚舉端點」(書目/篇目 JS 變數) 再逐篇抓 |
| **薄殼 JS reader、內容端點藏起來** | 星雲 `/bcN/bookM` 空殼 | ⚠️ **別爬殼**；先找真內容路由（見 §2） |

判準：`curl sitemap.xml`（單篇 URL 有沒有列？）→ playwright 看載文章時的 **XHR/network**（有沒有 `getData`/`.json`/`ArticleDetail` 之類）→ 看 `/bcN/bookM` 之類頁面 size（~9KB 空殼 vs 有內容）。

### 2. 找「藏起來的內容端點」（星雲教訓，最關鍵的一招）
薄殼站的全文常**不在 sitemap、不被 reader 殼揭露**，走另一條 server 路由（MVC `/Controller/action{id}`）。排查順序：
1. **直接問 user 要一個「他實際在讀的文章 URL」** ← 最快，往往秒破關（星雲 `/ArticleDetail/artcle1980`）。
2. playwright 攔截所有 response，找非資產的 GET（`.php`/`.json`/`.ashx`/`/ArticleDetail`）。
3. 看 `getData.php?type=…` 之類 JS 變數端點（法鼓 `all_books`/`vol_dump`）。
4. 探子網域/猜端點（`api.`/`app.`，多半不解析 → 放棄猜，回到 1）。

### 3. 無乾淨目錄時：用**麵包屑/breadcrumb 反推結構**
每篇文章頁自帶 `第N類【類名】 › 冊 › 子冊 › p篇` → **不需另一份目錄**，靠文章自身重建整棵樹：`parent_volume`=麵包屑[0]、`book_key`(分組鍵)=麵包屑[1]、`chapter_path`=麵包屑[1:]、多卷靠同一 `book_key` 自動併冊。

### 4. 禮貌大量爬取（~2 萬篇，**user 叮囑別被封**）
- **節流**：`ThreadPoolExecutor` 4 workers + 每請求小延遲(0.05s) + 指數退避(封頂 8–20s)。實測 ~7/s、err=0 全程未被封。
- **resumable 快取**：每篇寫 `c:/tmp/<author>_cache/{N}.json`（含 `empty:true` 標記 302 空洞）→ 被擋只要停、重跑自動續，**不重抓**。
- **監控封鎖**：看 err 計數；err 暴增＝被擋 → 停、退避久一點再續。
- **快取留著別清**：修解析重 build 時免再爬、不再打擾對方 server（星雲快取 25500 檔保留）。
- requests 要帶 **User-Agent + `verify=False`**（部分站直連會被丟連線）。

### 5. 入庫批次韌性（聖嚴/星雲都踩過）
Supabase/R2 偶發 `RemoteDisconnected`/`ConnectionError` → **`--all` 迴圈一定要 per-book `try/except`**（一冊失敗不中斷全批）+ 末尾重試一輪 + **`--resume`**（查 DB `id=in.(...)` 跳過已有 chunk 的冊）。首跑掛掉就 `--resume` 補齊。

### 6. 共用雷區
- `ebooks.id` 是 **UUID** → REST 查全集用 `id=in.(…)`，**不能 `like`**。
- `EBOOK_CHUNKS_DIR` 在 .env 可能空字串 → 用 `te.CHUNKS_DIR`（已 fallback G: 雲端）。
- **CJK 接行**：殺換行**不插空格**（`re.sub(r"[ \t]*\n[ \t\n]*","",s)`）但保留全形空格 U+3000 與英文詞間真空格（`_clean`）。
- **截圖 reader**：全頁高 ~3800–3970px > **2000px 硬限**（會炸 session）→ 讀前 PIL crop top ≤1850。
- **dev server 多任務衝突**：:3000 可能被別任務佔/壞（[[feedback_no_kill_other_tasks]] 不可殺）→ 自己另起 `PORT=3100/3200`；已認證 reader 首次 SSR 冷編譯 >30s → screenshot 腳本 `navigationTimeout` 拉 150s、或先 curl 暖路由。
- **無公有領域肖像**（當代法師照片受版權）→ `portraitUrl:''`，portal/hub 已加 emoji 佔位 `v-else` 降級。
- 截圖腳本放 `scripts/_xy_*.mjs`（`_` 前綴）跑完即刪、**別 commit**。

### 7. 全文未到位時的 placeholder（星雲曾用）
若全文一時抓不到：先建 hub + **書目**（status `planned`/`copyright`，sourceNote 標明待來源），之後全文進來再把 works `status→done`+填 `ebookId`、換掉 placeholder。誠實標示勝過硬刻殘缺爬蟲。

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
- [x] **✅ Jung PD pilot 全卷完成（2026-06-24）**：1912《Wandlungen und Symbole der Libido》+ Hinkle 1916《Psychology of the Unconscious》已完成 ch01–ch13，共 1,205 rows / 254,474 繁中字，ebook_id=`22222222-2222-4222-8222-222222222222`，見 [jung_collected_works.md](jung_collected_works.md)。若延伸到受版權 CW/GW 卷，需使用者提供合法來源檔，不抓盜版全文。
- [ ] **錨點 part-scoping**（次要）：含 Part 的書章號每部重起 → `anchor_coverage` key 不唯一。手工配對流程不依賴它，低優先。

## 起手卷決策（2026-06-02，Claude 拍板）

**Pilot = 公有領域早期著作**：1912《Wandlungen und Symbole der Libido》(de, archive.org) + Hinkle 1916《Psychology of the Unconscious》(en, 公有領域)。理由：(1) 唯一**現在就能合法取得並處理**、不需使用者給檔、不碰受版權全文的 Jung 來源；(2) 兩版是**同一部作品**，能真正驗證跨版對齊；(3) 受版權的 CW 卷無論如何都要使用者提供 HTML 來源檔（不抓盜版全文）。pilot 建好的機器原封不動延伸到那些卷。詳見 [jung_collected_works.md](jung_collected_works.md)。
- [x] **視覺驗證**（2026-06-02）：手造德/英/中樣本 chunk 跑 dev server + `screenshot_book.mjs` 確認 `中/對照/德/英` toggle、3 欄逐段對齊、**body zip 補白**（英缺第 2 段 → 空白格不位移）、**footnote by-number 跨欄對齊**（英缺 (2) → 該格空白）、單來源「德」單欄模式 全部正確。
  - 📌 `screenshot_book.mjs` 已修：注入 `kgl_device_id` 呈現預先核准的 `screenshot-bot` 裝置，繞過新的 device-trust gate（`middleware/device.global.ts`）。需在 `trusted_devices` 預埋一列 `device_id='screenshot-bot', status='approved'`（已埋）。否則所有 reader 截圖（含 [[scripture-fathers]] 校對 C 層）會被導去 `/device-pending`。
- [x] **榮格全集盡職調查表**（[jung_collected_works.md](jung_collected_works.md)）＋版權表＋來源紀錄
- [x] **jung_glossary.md**（心靈工坊/TSAP/《榮格心理學辭典》查證鎖定；辭典為版權書只作參考不轉錄）
- [x] PD pilot 全卷三欄/多欄上架完成（ch01–ch13；德/英來源可得處對照，繁中全段完成）

---

## See also

- [[ebook-translate]] — 翻譯基礎設施（engine / quota / OAuth / append-resume / Gemini-Haiku fallback）＋ 一般雙語翻譯
- [[scripture-fathers]] — 公有領域教父原典；「參考現成中譯本校準」姿態本 skill 沿用
- [[ebook-pipeline]] — parse / OCR / standardize / 套書 split 上游
- [[translation-glossary]] — 神學家/神學名詞詞庫（神學家全集才用；其餘全集各自 glossary）
- [scripture-papal](../scripture-papal/SKILL.md) — 既有「拉/英/中三欄逐段對照」(alignDocs) 的 content-file 版實作，可參考對齊邏輯（但本 skill 走 ebook reader，不走 content files）
- [jung_collected_works.md](jung_collected_works.md) — 榮格全集案例：版權表 + 卷目 + 來源
- [jung_glossary.md](jung_glossary.md) — 榮格術語德/英/中對照
- [mueller_collected_works.md](mueller_collected_works.md) — 馬克斯‧穆勒全集案例（宗教學家全集 #1）：版權表 + 18 卷目 + 來源 + 接手清單
- [mueller_glossary.md](mueller_glossary.md) — 穆勒比較宗教學術語英/德/中對照
- [panikkar_collected_works.md](panikkar_collected_works.md) — 雷蒙‧潘尼卡全集案例（受版權當代神學家 #1，English-first）：版權表 + Opera Omnia 12 卷目 + 起手卷《印度教中未識的基督》+ 接手清單
- [panikkar_glossary.md](panikkar_glossary.md) — 潘尼卡比較神學／宗教哲學術語英/原文/中對照（cosmotheandric、宗教內對話、Christophany…）
