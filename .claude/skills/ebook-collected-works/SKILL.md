---
name: ebook-collected-works
description: 「經典學者全集」的收錄流程 —— 以**學科**組織（哲學／社會學／宗教學／神學／佛學／心理學／人類學…），獨立 `/collected-works` portal（依學科分區）＋作家 hub（小傳／肖像／年表／著作目錄）＋單卷 reader。跟 [[ebook-translate]]（一般外文→繁中雙語）、[[scripture-fathers]]（公有領域教父原典）並列。四種收錄 pipeline：**多語對照**（原文＋既有譯本＋我的繁中，N 欄逐段）／**單一語言**（本即繁中的漢傳全集，零翻譯零對齊）／**REFERENCE**（已有完整第三方中譯就不重譯，原文逐段對照）／**自譯**（English-first 引擎逐段翻）。Use when 使用者要把某位學者的全集（依學科）做成 hub＋逐段對照上架、要新增作家或學科、要擴充 reader 多欄、要設計／修多語 JSONL schema、要對齊跨版本段落。各學科案例見下「§C 各學科案例」；schema／對齊／portal 基建見「§B 方法論核心」。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。

# 經典學者全集 Skill（Collected Works — 依學科組織）

把**經典學者的全集**收進獨立的 `/collected-works` portal（**依學科分區**），每位學者一個作家 hub（小傳／肖像／年表／著作目錄），單卷進 `/ebook/[id]` reader 逐段對照閱讀。

這是 ebook-translate 家族的第三個 skill：

| Skill | 負責 | 典型對象 |
|---|---|---|
| [[ebook-pipeline]] | parse / OCR / standardize / 套書 split | 任何 ebook 上游處理 |
| [[ebook-translate]] | 外文 → 繁中（雙語）/ 簡 → 繁 | 單本英文書、ACCS 缺卷 |
| [[scripture-fathers]] | 教父原典（公有領域 Schaff/CCEL）中譯精修 | ANF/NPNF/ACCS |
| **ebook-collected-works（本 skill）** | **經典學者「全集」依學科收錄；多語／單語／參照／自譯四路** | **柏拉圖、榮格、穆勒、潘尼卡、印順‧聖嚴‧星雲…** |

**核心承諾**：portal 依學科組織；每位學者一份 hub（學術小傳＋年表＋完整書目＋轉錄狀態）；reader 主欄永遠是**我自己的逐段繁中譯文**（單語全集則主欄＝原文繁中本身），旁邊可並陳來源語言欄（原文／既有譯本），使用者可切「中／對照／原文…」。

---

## 何時 trigger

- 使用者指定**某位學者的全集／文集／著作集**要收進 `/collected-works`
  - 「把榮格全集找德文英文版三欄放進來」「馬克斯穆勒宗教學全集」「潘尼卡全集」「印順／聖嚴／星雲全集」「把古希臘哲學家的全集建起來」
- 要**新增一個學科**或把作家**重新歸類**到某學科
- 要把現有雙語書升級成 3 欄以上、要擴充 reader 多欄切換
- 要設計或修「多來源語言」JSONL schema、要對齊跨版本段落

**不適用**：
- 單一外文 → 繁中（不進全集 portal、沒有 hub 概念）→ [[ebook-translate]]
- 公有領域教父原典（走 /fathers）→ [[scripture-fathers]]
- 簡 → 繁批次轉換 → [[ebook-translate]] B pipeline

---

# §A 學科分類總覽（portal 骨架）

**portal 依學科分組（2026-07-01，user 拍板：佛學獨立一類）**。作家歸屬由 `CwAuthor.disciplineGroup`（新欄）決定，portal [pages/collected-works/index.vue](../../../pages/collected-works/index.vue) 依常數分區顯示：

```ts
const DISCIPLINE_ORDER = ['哲學', '社會學', '宗教學', '神學', '佛學', '心理學', '人類學']
// 未列出的學科接最後（localeCompare），空組不顯示
```

**現況歸類（每學科 → 作家 → 案例章節）**：

| 學科 | 作家（slug） | pipeline 類型 | 案例 |
|---|---|---|---|
| **哲學** | 柏拉圖 `plato`、亞里斯多德 `aristotle`、前蘇格拉底與蘇格拉底 `presocratics`、伊比鳩魯 `epicurus`、愛比克泰德 `epictetus`、普羅提諾 `plotinus` | 多語對照（希／英／繁中，公有領域） | [§C 哲學](#c1-哲學古希臘哲學家全集) |
| **宗教學** | 穆勒 `max-mueller` | 多語對照（英／德／繁中） | [§C 宗教學](#c2-宗教學) |
| **神學** | 潘尼卡 `panikkar` | REFERENCE / 自譯（English-first） | [§C 神學](#c3-神學) |
| **佛學** | 印順 `yinshun`、聖嚴 `shengyen`、星雲 `hsingyun` | 單一語言（本即繁中） | [§C 佛學](#c4-佛學) |
| **心理學** | 榮格 `jung` | 多語對照（德／英／繁中，公有領域早期著作） | [§C 心理學](#c5-心理學) |
| 社會學／人類學… | （待補） | — | — |

**加一位新作家 = 在 `stores/collectedWorks.ts` 的 `authors[]` push 一個 `CwAuthor`**（免 DB migration、免 server route）。務必填 `disciplineGroup`（**別跟一句話副標 `discipline` 搞混**）；`color` 須在 [tailwind.config.ts](../../../tailwind.config.ts) safelist（amber/blue/rose/emerald/violet/sky/indigo/cyan/orange/stone/purple/teal，shade 50–300/500–700，**別用 -400**）。詳見 [§B7 portal + hub](#b7-portal--作家-hub-頁)。

---

# §B 方法論核心（跨學科共用）

## §B0 開工第一步：判版權＋選 pipeline

### 可得性與版權盡職調查（這類全集的真實障礙）

教父全集能全自動跑，是因為 Schaff/CCEL 版本公有領域。**近現代「全集」幾乎相反**，開工前一定先查：

1. **原文全集是否還在版權內？** 作者卒年 + 70。例：榮格 1961 卒 → 德文 GW 到 2031；潘尼卡 2010 卒 → 約 2080。
2. **既有譯本是否有版權？**（多半有 — 商務／校園／道風／Princeton/Bollingen…）
3. **網路免費全文是什麼性質？** 多半是**盜版掃描 PDF** 或 OCR 髒檔。
4. **哪些卷／早期著作其實已公有領域？**（1929 前出版者）— 這些才有乾淨合法來源。
5. 結論寫進該全集的 case-study md（版權表）。

### 本專案的處理姿態（跟 scripture-fathers「參考現成中譯本校準」同源）

- **reader 主欄＝我自己的逐段繁中譯文 + 來源語言原文欄。** 第三方中譯本預設**不當主欄**。
  - **私人自用例外（user 拍板 2026-06-12）**：本站是私人研究圖書館，**第三方中譯本可入庫當「參考層」**（簡體先 opencc→繁中，[[feedback_traditional_chinese_only]]），但**不取代我的逐段自譯主欄**，標示清楚「第三方譯本‧參考」。→ 即 REFERENCE pipeline。
- **來源語言欄**是「對照閱讀」用途。版權內來源文字走本機 pipeline；**我（Claude）不在對話裡貼整段受版權原文**，文字一律走本機 script / 檔案。
- **公有領域的卷優先**；標示清楚。
- **私人自用 → 受版權卷可用 shadow library 取來源檔（user 拍板 2026-06-12）**：本站 auth-gate 後僅供個人閱讀（非公開散布），受版權著作若無 PD 源、archive.org 又只借閱，**可從 shadow library（Anna's Archive / Library Genesis）抓來源到本機**（比照 [[feedback_jung_nonpd_english_first]]）。鐵則：(1) **English-first**，主欄是我的逐段繁中；(2) 來源原文**只走本機檔／script、絕不貼進對話**；(3) `curl`/Bash 抓到 `c:/tmp` 再 `--src` 餵 pipeline。⚠️ **環境網路限制**：此 sandbox 多數 shadow 鏡像（annas-archive、libgen.is/.rs）**DNS 被擋**，僅 `libgen.li` 可達且常只索引期刊書評 → 抓不到時請 user 自己下載後丟本機（new-book drop / `c:/tmp`）。

### 四種收錄 pipeline（**先判走哪條**）

| pipeline | 何時用 | 主欄 | 來源欄 | LLM | 對齊 | 案例 |
|---|---|---|---|---|---|---|
| **① 多語對照** | 原文＋既有他語譯本＋要我自譯繁中，做 N 欄 | 我的繁中 | 原文＋既有譯本 | 有（自譯） | 跨版對齊（最難） | 榮格、穆勒、古希臘 |
| **② 單一語言** | 全集本即繁體中文 | 原文繁中本身 | 無（reader 退化單欄） | 無 | 無 | 印順、聖嚴、星雲 |
| **③ REFERENCE** | 已有完整第三方中譯，不重譯 | 第三方中譯（簡→繁，標「參考」） | 原文逐段對照 | 無 | 章序配對 | 潘尼卡《宗教內對話》 |
| **④ 自譯** | 無中譯的受版權卷，English-first | 我的繁中 | 原文（英／義／西…） | 有 | 章序切段 | 潘尼卡自譯 queue |

下游（入庫 / hub / reader）四路**完全共用**；差別只在「取源＋解析＋要不要翻＋怎麼對齊」。**多語對照**細節見 §B1–§B4，**單一語言**見 §B5，**portal/hub/reader** 見 §B6–§B7。

---

## §B1 三件 ebook-translate 不處理的事（多語對照專屬）

### 1. 多卷套書 = 一個 corpus

全集是**套書**。先遵守 [[feedback-set-books-split]] / [[feedback-set-books-subfolder]]：
- 每卷一個 `ebooks` row（不是整套一個 row）
- Drive 在分類下建子資料夾整理；移動檔案後 `UPDATE ebooks.file_path` 同步
- 跨卷 `volume` / `parent_volume` 命名統一（`parent_volume` = 著作集分組）
- 跨卷術語一致 → 走專屬 glossary（見 §B8）

### 2. 單一來源 → 多來源 schema（`sources`）

現行 JSONL 只有 `source_lang`(str) + `source_text`(str) = 一個來源。多語全集要 N 個來源，schema 這樣擴充（**向後相容**）：

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
- `source_text`/`source_lang` 永遠鏡像 `sources[source_order[0]]` → 舊 reader 拿到主來源照常顯示，雙語書（只有 `en`）不受影響。
- 新 reader 見 `sources` 就走 N 欄；沒 `sources` 就 synthesize `{[source_lang]: source_text}` / `source_order=[source_lang]`（等同今日雙語）；**單一語言全集連 `source_text` 都不寫 → 自動退化單欄**。

### 3. 跨版本段落對齊（多語最難的一步）

原文與既有譯本是**獨立編輯**的版本：分段不同、有的卷重排、註腳系統不同 → **不能假設「第 i 段原文 = 第 i 段譯本」**。策略由粗到細：

1. **章節錨點對齊**（最可靠）：兩版都有的 §/章/小節編號（如 Bollingen `[¶ N]` 段碼）當 join key。優先找有段碼的版本。
2. **長度比＋順序對齊**（無段碼時）：同章內按段落順序 + 字數比例 greedy 對齊（類似 scripture-papal 的 `alignDocs()`）。
3. **LLM 輔助對齊**（兜底）：同章丟給 Gemini/Haiku 輸出「原段 ↔ 譯段」index pairs。
4. **對不齊就分欄不分段**：退化成「整章原文欄 / 整章譯本欄 / 我的逐段中文」，中文跟我自己的分段，來源欄整段顯示。

> 中文譯文一律**跟著我自己的分段**走。對齊是把原文、譯本**塞進我的段落框架**，不是反過來。對不上的來源段落寧可整段塞、不要硬切。

---

## §B2 多語對照 pipeline 概覽（每卷）

```
[0] 盡職調查：版權表 + 公有領域判定（寫進 case-study md）
        ▼
[1] 取得來源：原文卷 + 既有譯本卷（PDF/EPUB）；套書規則：每卷一 row、Drive 子資料夾、file_path 同步
        ▼
[2] 抽文字：EPUB→乾淨；PDF→Gemini/Haiku OCR（走 [[ebook-pipeline]] OCR）；per-語言 source chunks（保留段碼/章節錨點）
        ▼
[3] 對齊：章節錨點 > 長度比 > LLM 輔助 > 整段塞（§B1-3）→「對齊後章節單位」
        ▼
[4] 翻譯：translate_ebook_to_zh 變體，從原文翻、既有譯本當交叉校對；術語走專屬 glossary（§B8）
        ▼
[5] 寫多語 JSONL：content=繁中, sources={…}, source_order, source_text 鏡像
        ▼
[6] volume / parent_volume backfill（著作集分組樹）
        ▼
[7] R2 + DB previews 同步（PATCH chunk_count/standardized_at）
        ▼
[8] reader 多欄切換驗證（中 / 對照 / 各來源語言）
```

翻譯引擎、quota 協調、OAuth refresh、append-resume、Gemini→Haiku 2-strike — **全部沿用 [[ebook-translate]] 基礎設施**，本 skill 不重造。

**基建現況（都 test-first、已 push，不用重做）**：
- `sources` 契約模組 [lib/multilang-sources.ts](../../../lib/multilang-sources.ts)（client+server 共用，27 例）＋ [test/multilang-sources.spec.ts](../../../test/multilang-sources.spec.ts)：normalize / mirrorPrimarySource / availableViewModes / resolveViewMode stale 夾制 / langLabel / zipParallel 補白。**下游 reader 與 API 一律用這個 module。**
- reader N 欄 + API passthrough：`ChunkData`([server/utils/ebook-chunks.ts](../../../server/utils/ebook-chunks.ts)) 加 `sources?`/`source_order?` + [[id].get.ts](../../../server/api/ebooks/[id].get.ts) passthrough。
- Python 寫入器 [scripts/multilang_chunks.py](../../../scripts/multilang_chunks.py)（21 例，鏡像 TS 契約 + `assemble_multilang_chunks(units, translate_fn, source_order)`，engine boundary=`translate_fn`）。
- 對齊 [scripts/align_editions.py](../../../scripts/align_editions.py)（20 例：`parse_chapter_number` DE/EN/CJK+羅馬/中文數字；`align_editions` 錨點 join / order 補白 fallback）。
- 驅動 [scripts/translate_collected_work.py](../../../scripts/translate_collected_work.py)（11 例：`load_plaintext_sections`/`split_html_sections`(bs4)/`make_translate_fn(engine)`/`run`）。
- 殘留（接真語料時按需補）：段碼級 `[¶ N]` 細對齊、LLM 輔助 fallback、錨點 part-scoping（含 Part 的書章號每部重起 → key 不唯一，手工配對不依賴它）。

---

## §B5 單一語言 PLAYBOOK（漢傳佛教／中文全集）

> 印順(CBETA)/聖嚴(法鼓全集)/星雲(masterhsingyun) 三套累積的通用做法。**任何「本即繁中、要逐冊上架的中文全集」都照這套**（§B1–B4 多語對齊在此**不適用**，零翻譯零對齊）。下游入庫/hub/reader 完全共用，新案例**只需寫來源解析器**。

### 0. 單一語言鐵則
- **零翻譯、零跨語對齊**：`content` = 原文繁中本身；chunk **不寫 `sources`/`source_text`** → reader 自動退化單欄（§B1-2 向後相容）。
- 一書（冊）= 一個 `ebooks` row；一篇（章/節/條目）= 一個 chunk；`parent_volume`=大類/著作集、`volume`=書名、`chapter_path`=書名 · [章節…] · 篇名。
- **保留原書頁碼**（[[feedback_pdf_page_number]]）：CBETA `lb` 邊碼 / 法鼓 `span.pb data-page` / 星雲麵包屑 `pNNN` → 存進 `chunk.page_number`。
- deterministic `ebook_id` 每作家一個命名空間：印順 `a0000000-…-NN`、聖嚴 `b0000000-…`、星雲 `c0000000-…`；registry JSON committed 進 skill 資料夾。

### 1. 開工第一步：來源分級（決定可行性，**別跳過**）
| 來源型態 | 範例 | 做法 |
|---|---|---|
| **結構化標記**（TEI/XML/EPUB） | CBETA `cbeta-org/xml-p5` Y 系列 | 最佳；GitHub raw 直抓，`cb:mulu`/`cb:div` 巢狀＝章節樹。非商業可再散布 |
| **靜態每篇 HTML、可枚舉** | 法鼓 `getData.php?type=vol_dump`+`html/{id}.html` | 好；先抓「枚舉端點」再逐篇抓 |
| **薄殼 JS reader、內容端點藏起來** | 星雲 `/bcN/bookM` 空殼 | ⚠️ **別爬殼**；先找真內容路由（見 §2） |

判準：`curl sitemap.xml` → playwright 看載文章的 **XHR/network** → 看頁面 size（~9KB 空殼 vs 有內容）。

### 2. 找「藏起來的內容端點」（星雲教訓，最關鍵的一招）
薄殼站全文常**不在 sitemap、不被 reader 殼揭露**，走另一條 server 路由（MVC `/Controller/action{id}`）。排查順序：
1. **直接問 user 要一個「他實際在讀的文章 URL」** ← 最快，往往秒破關（星雲 `/ArticleDetail/artcle1980`）。
2. playwright 攔截所有 response，找非資產 GET（`.php`/`.json`/`.ashx`/`/ArticleDetail`）。
3. 看 `getData.php?type=…` 之類 JS 變數端點（法鼓 `all_books`/`vol_dump`）。
4. 探子網域多半不解析 → 放棄猜、回到 1。

### 3. 無乾淨目錄時：用**麵包屑反推結構**
每篇文章頁自帶 `第N類【類名】 › 冊 › 子冊 › p篇` → 靠文章自身重建整棵樹：`parent_volume`=麵包屑[0]、`book_key`=麵包屑[1]、`chapter_path`=麵包屑[1:]、多卷靠同一 `book_key` 併冊。

### 4. 禮貌大量爬取（~2 萬篇，**user 叮囑別被封**）
- **節流**：`ThreadPoolExecutor` 4 workers + 每請求 0.05s 延遲 + 指數退避（封頂 8–20s）。實測 ~7/s、err=0。
- **resumable 快取**：每篇寫 `c:/tmp/<author>_cache/{N}.json`（含 `empty:true` 標記空洞）→ 被擋重跑自動續，不重抓。
- **監控封鎖**：看 err 計數暴增＝被擋 → 停、退避久一點再續。
- **快取留著別清**（星雲快取 25500 檔保留）。
- requests 帶 **User-Agent + `verify=False`**。

### 5. 入庫批次韌性（聖嚴/星雲都踩過）
Supabase/R2 偶發 `RemoteDisconnected`/`ConnectionError` → **`--all` 迴圈一定 per-book `try/except`** + 末尾重試一輪 + **`--resume`**（查 DB `id=in.(...)` 跳過已有 chunk 的冊）。

### 6. 共用雷區
- `ebooks.id` 是 **UUID** → REST 查全集用 `id=in.(…)`，**不能 `like`**。
- `EBOOK_CHUNKS_DIR` 在 .env 可能空字串 → 用 `te.CHUNKS_DIR`（已 fallback G: 雲端）。
- **CJK 接行**：殺換行**不插空格**（`re.sub(r"[ \t]*\n[ \t\n]*","",s)`）但保留全形空格 U+3000 與英文詞間真空格。
- **截圖 reader**：全頁高 ~3800–3970px > 2000px 硬限 → 讀前 PIL crop top ≤1850。
- **dev server 多任務衝突**：:3000 可能被別任務佔/壞（[[feedback_no_kill_other_tasks]] 不可殺）→ 自己另起 `PORT=3100/3200`；已認證 reader 首次 SSR 冷編譯 >30s → `navigationTimeout` 拉 150s、或先 curl 暖路由。
- **無公有領域肖像**（當代法師照片受版權）→ `portraitUrl:''`，portal/hub 已加 emoji 佔位 `v-else`。
- 截圖腳本放 `scripts/_xy_*.mjs`（`_` 前綴）跑完即刪、**別 commit**。

### 7. 全文未到位時的 placeholder（星雲曾用）
先建 hub + **書目**（status `planned`/`copyright`，sourceNote 標明待來源），之後全文進來再把 works `status→done`+填 `ebookId`。誠實標示勝過硬刻殘缺爬蟲。

---

## §B6 Reader 多欄設計（已實作）

`pages/ebook/[id].vue` ViewMode 已動態化：`"zh"`（單欄繁中＋唯一可標註）｜`"parallel"`（對照，1+N 欄）｜每個來源語言一個獨立單欄（`"src:de"`/`"src:en"`…，從 `source_order` 動態生）。

- **Toggle UI**：`中 | 對照 | 德 | 英`（來源鈕從 `source_order` map：`{de:'德', en:'英', la:'拉', fr:'法', el:'希', grc:'希臘', he:'希伯來'}`）。
- **parallel grid**：第一欄 zh，後依 `source_order`；`content`（zh 段）跟每個 `sources[lang]` 按段 index zip（`zipParallel`），缺段補白不位移；footnote by-number 跨欄對齊。3 來源以上自動更寬 / 水平捲動；mobile 垂直堆疊。
- **back-compat**：`sources` 不存在 → `{[source_lang]: source_text}`；legacy `bi`/`en` localStorage 用 `migrateLegacyViewMode` 遷移；無來源時 `effectiveViewMode` 強制 `zh`（單語全集即此）。
- 純函式全在 [lib/multilang-sources.ts](../../../lib/multilang-sources.ts)（**別各自重寫 schema 判斷**）。
- **視覺驗證（2026-06-02）**：手造德/英/中樣本跑 dev server + `screenshot_book.mjs` 確認 toggle、3 欄逐段、body zip 補白、footnote 對齊、單來源單欄全部正確。`screenshot_book.mjs` 注入 `kgl_device_id=screenshot-bot` 繞過 device-trust gate（`trusted_devices` 已預埋 `screenshot-bot`/approved 一列，**勿刪**，fathers 校對 C 層截圖也靠它）。

---

## §B7 Portal + 作家 Hub 頁

全集**不放電子圖書館（/ebook）裡**，而是獨立 `/collected-works` portal（首頁「📚 全集」cyan 卡）。portal 依學科分區（見 §A）。每位學者一張卡 → 作家 hub `/collected-works/[slug]` 最外層呈現：

1. **學術貢獻簡介**（`contribution: string[]`，繁中段落，支援 `**粗體**`）
2. **肖像**（`portraitUrl`：Wikimedia Commons `Special:FilePath/<檔名>?width=500` 公有領域縮圖，**不用 Supabase Storage**；當代人物無 PD 肖像 → `''`，hub 用 emoji 佔位）
3. **生平學術年表**（`timeline: {year, text}[]`）
4. **著作目錄**（`works[]`，**按 `category` 分組、組內依 `yearSort` 排序**；顯示年分／繁中名／原文名／來源語言標／轉錄狀態）

**單卷閱讀走既有 `/ebook/[id]` 多欄 reader**（`work.ebookId` 連過去；`externalUrl` 優先，如東方聖書）；hub 只是入口＋完整書目＋路線圖。

### 資料：`stores/collectedWorks.ts`（repo-committed，沿用 /works·speech.ts 模式）
- 直接改本檔新增／編輯作家與書目，**免 DB migration、免 server route**（user 拍板 2026-06-05）。
- `CwAuthor` 必填欄：`slug` / `name` / `disciplineGroup`（§A 分組鍵）/ `discipline`（一句話副標）/ `fields[]` / `portraitUrl` / `color` / `emoji` / `contribution` / `timeline` / `works`。
- `WorkStatus`：`done`（已轉錄→reader）/ `in-progress`（轉錄中，可連 pilot）/ `planned`（待轉錄）/ `copyright`（受版權待來源）。badge：綠／琥珀／灰／石。hub `[slug].vue` 會 fetch 活 chunk_count → 有內容自動把 planned 升「轉錄中」可點。
- **某卷轉錄完成** = 改 `status` 為 `done`/`in-progress` 並填 `ebookId`。
- **驗證（2026-06-05 實證）**：dev server + `screenshot_book.mjs` 截 portal/hub。一次性截圖腳本用完即刪（`_`-prefix 未 gitignore，別 commit）。

---

## §B8 Glossary（每部全集一份專屬術語表）

教父走 `/translation-glossary`。全集多半是**別的學科**，術語不同，**每部全集建一份專屬 glossary md**（放本 skill 資料夾）：
- 規則同 ebook-translate glossary：翻譯前先鎖譯名 → 翻譯中 PROMPT 帶 glossary → 翻完跑 term sweep 收斂變體。
- 跨卷一致是硬指標（同一術語不可一卷「自性」一卷「自我」）。
- 若人物/概念跟現有 `/translation-glossary` 重疊 → 仍以 `name_recommended` 為權威（[[feedback-glossary-strict-authority]]）。**哲學家／科學家／帝王／地名一律先查 [[translation-glossary]] 的對應領域表鎖譯名。**
- 現有：[jung_glossary.md](jung_glossary.md)（德文原詞為準）、[mueller_glossary.md](mueller_glossary.md)（英文原詞為準）、[panikkar_glossary.md](panikkar_glossary.md)（自鑄詞 cosmotheandric…）。

---

# §C 各學科案例

> 每個案例的**完整版權表／卷目／來源／對齊策略／接手清單**在各自 case-study md；此處只給「一句話現況＋走哪條 pipeline」。

## C1 哲學：古希臘哲學家全集

**新學科群（2026-07-01 起，第一批六 hub 骨架，pipeline ① 多語對照）**。portal 改依學科分組後開的「哲學」群，著作目錄多為 `planned`，逐步轉錄。全屬**公有領域**（古典原文＋十九世紀權威英譯 Jowett/Ross/MacKenna），可做希臘／英／繁中三欄。肖像皆 Wikimedia Commons 公有領域胸像（已 curl 驗證可載）。接手轉錄比照榮格 pipeline；人名先查 [[translation-glossary]] 哲學家表鎖譯名。

| hub（slug，色） | 骨架 | 來源 |
|---|---|---|
| 柏拉圖 `plato` blue 🏛️ | 早／中／晚期對話錄＋書信 | Stephanus 原文＋Jowett 英譯 |
| 亞里斯多德 `aristotle` emerald 📐 | 工具論‧自然哲學‧生物學‧形上學‧倫理政治‧修辭詩學 | Bekker 原文＋Ross 牛津英譯 |
| 前蘇格拉底與蘇格拉底 `presocratics` stone 🌀 | Diels-Kranz 殘篇＋第歐根尼‧拉爾修＋色諾芬（蘇格拉底無著作） | DK 編號 |
| 伊比鳩魯 `epicurus` cyan 🌿 | 三書信＋主要教義＋梵蒂岡格言＋附盧克萊修 | 第歐根尼‧拉爾修卷十 |
| 愛比克泰德 `epictetus` violet ⚖️ | 手冊＋談話錄＋斯多噶傳統參照（馬可‧奧勒留／早期斯多噶殘篇） | 阿里安筆錄 |
| 普羅提諾 `plotinus` purple 🔆 | 《九章集》六集＋波菲利《普羅提諾生平》 | MacKenna 英譯 |

**下一步**：擇一 hub（建議柏拉圖《蘇格拉底的申辯》起）取 PD 希臘原文＋Jowett 英譯 → 走 §B2 多語 pipeline → 逐段三欄。專屬 glossary 建 `greek_philosophy_glossary.md`（理型 εἶδος、邏各斯、努斯、ataraxia、太一…）。

## C2 宗教學：馬克斯‧穆勒全集

案例檔 → **[mueller_collected_works.md](mueller_collected_works.md)**（版權表 / Longmans 18 卷目 / 來源 / 對齊 / 接手）＋詞庫 [mueller_glossary.md](mueller_glossary.md)。

一句話現況：Friedrich Max Müller（1823–1900，**宗教學開山祖**）卒於 1900 → **全部著作早已公有領域**，是 collected-works 最乾淨案例（pipeline ①）。以英文寫作為主 → 預設英＋繁中雙語；有平行德文版的卷（起手卷《宗教學導論》1873 = 德《Einleitung》1874，英德同構四講＋兩附論）做真三欄。**✅《宗教學導論》三欄竣**（`33333333-…`，7 chunks，~21.5 萬繁中字）；其餘 13 部走 `scripts/mueller_auto.py` 自動 queue（English-first：先無 LLM 上架英文、再逐段翻）。

## C3 神學：雷蒙‧潘尼卡全集

案例檔 → **[panikkar_collected_works.md](panikkar_collected_works.md)**（版權表 / Opera Omnia 12 卷目 / 起手卷 / 接手）＋詞庫 [panikkar_glossary.md](panikkar_glossary.md)。

一句話現況：Raimon Panikkar（1918–2010，**宗教間／宗教內對話與跨文化哲學巨擘**）卒於 2010 → **受版權至約 2080，榮格型（非穆勒）**：無乾淨 PD 全文、第三方中譯不當主欄。採 **English-first**。多語原創（加泰隆／西／義／英／德），Opera Omnia 是主題重編 → 多數卷先英＋繁中雙語。**兩種 build（user 拍板 2026-06-12）**：③ **REFERENCE**（`--src <en> --zh-src <zh>`，有完整中譯就不重譯，第三方中譯簡→繁當主欄、英文逐段對照、零 LLM）／④ **自譯**（`--src <en>`，無中譯的卷 English-first 引擎自譯）。CJK 章標題由 `_CJK_HEADING_RE` 切段。**✅ 上架 2 本**（宗教內對話 `55555556-…` REFERENCE；神的經驗 `55555561-…` 自譯 39 chunks）；自譯 queue `scripts/panikkar_auto.py --run-queue` 背景連跑（8 卷，義/英/西）。腳本 `panikkar_build.py`/`panikkar_auto.py`/`ocr_pdf_to_text.py`，pytest 29 例綠。

## C4 佛學：印順‧聖嚴‧星雲（單一語言，pipeline ②）

全集本即繁中 → 零翻譯零對齊，走 §B5 PLAYBOOK。案例檔：[yinshun_collected_works.md](yinshun_collected_works.md) / [shengyen_collected_works.md](shengyen_collected_works.md) / [hsingyun_collected_works.md](hsingyun_collected_works.md)。

- **✅ 印順導師**（`yinshun`，amber ☸️）：來源 CBETA Y 系列 TEI P5 XML（`cbeta-org/xml-p5`，44 XML=42 部，非商業可再散布）。`cb:mulu` 三層→章節樹、`lb` 邊碼→段碼。`scripts/yinshun_build.py`（8 例綠）+ `yinshun_registry.json`。**44 卷 / 5324 chunks 上架**。
- **✅ 聖嚴法師**（`shengyen`，teal 🥁）：來源 ddc.shengyen.org《法鼓全集 2020 紀念版》— SPA 殼但靜態檔全枚舉（`all_books` 110 冊／`vol_dump` 4079 篇／`toc.html`／`html/{輯-冊-篇}.html`）。`p.indent` 正文／`p.hN` 標題／`span.pb data-page` 保留頁碼。`scripts/shengyen_build.py`（9 例綠）。**110 冊 / 4181 chunks 上架**。
- **✅ 星雲大師**（`hsingyun`，orange 🪷）：官網 reader 殼一度誤判「不出全文」，**user 給 `/ArticleDetail/artcle{N}` 後破關**（每篇免登入 server-render 全文＋麵包屑階層，不在 sitemap）。crawl `artcle{1..25500}`（19,888 篇有效、err=0）→ 麵包屑分組成 **109 冊 / 19,997 chunks**。`scripts/hsingyun_build.py`（10 例綠）。**🔑 教訓：薄殼站找不到內容端點時，直接問 user 要「實際在讀的文章 URL」往往秒破關。**

## C5 心理學：榮格全集

案例檔 → **[jung_collected_works.md](jung_collected_works.md)**（版權表 / GW·CW 20 卷目 / 公有領域判定 / 來源 / 接手清單）＋詞庫 [jung_glossary.md](jung_glossary.md)。**本 skill 誕生的首案，多語對照 pipeline ① 的原型。**

一句話現況：榮格（1875–1961）GW 德文原典＋CW 英譯**多數卷版權內到 2031**，網路免費全文多盜版掃描；**僅 1929 前早期著作有乾淨 PD 來源**。**✅ Jung PD pilot 全卷完成（2026-06-24）**：1912《Wandlungen und Symbole der Libido》(de) + Hinkle 1916《Psychology of the Unconscious》(en) 完成 ch01–ch13，共 **1,205 rows / 254,474 繁中字**，`ebook_id 22222222-2222-4222-8222-222222222222`。

**起手卷決策＋方法教訓（其他多語卷通用）**：
- Pilot 選公有領域早期著作 = 唯一現在能合法取得、兩版同源可驗證跨版對齊者。受版權 CW 卷須 user 提供合法來源檔（**不抓盜版全文**）。
- 🔴 **德 1912 ↔ 英 1916 非段落同構（實證）**：Hinkle 重組結構（自序≠Jung Einleitung，heading 自動對齊會抓錯）→ **正確逐段三欄需人工逐句配對 + 親譯**，非自動 run。多數全集卷的既有他語譯本同樣非段落同構，此問題普遍。
- 穩定方法（每章）：德掃描 PDF → **Haiku 重 OCR**（Gemini 4 key 全耗盡）→ **內容指紋**配對 de↔en 章（非 heading）→ 人工逐段對齊 → 親譯（先查 [jung_glossary.md](jung_glossary.md)）→ build（三 list 段數必須相等，對齊閘會 SystemExit）。續傳細則見 [jung_collected_works.md](jung_collected_works.md)「🚀 新 session 接手清單」。

---

## SOP（每卷接手）

**多語對照卷（pipeline ①，如古希臘／榮格／穆勒）**：
1. 讀該全集 case-study md 版權表，確認來源策略（公有領域 / 本機處理）
2. 套書規則：建 row + Drive 子資料夾 + file_path（[[feedback-set-books-subfolder]]）
3. 抽文字（EPUB 直抽 / PDF 走 OCR）→ per-語言 source chunks
4. glossary 先鎖高頻術語（§B8；人名查 [[translation-glossary]]）
5. 對齊（章節錨點優先，§B1-3）→ 對齊單位
6. `--limit 2` smoke test → 翻 2–3 章給使用者確認譯名/分欄
7. full run（engine/quota 看 [[ebook-translate]]）→ 多語 JSONL
8. volume/parent_volume backfill → R2 + DB previews
9. reader 多欄驗證 → hub works `status→done`+`ebookId` → commit + push（[[feedback-auto-push]]）

**單一語言卷（pipeline ②，如印順／聖嚴／星雲）**：照 §B5 —— 來源分級 → 找內容端點 → 麵包屑反推結構 → 禮貌爬取+快取 → 解析器 → 入庫（per-book try/except+resume）→ hub。

**REFERENCE/自譯（pipeline ③④，如潘尼卡）**：見 [panikkar_collected_works.md](panikkar_collected_works.md) 接手清單。

---

## See also

- [[ebook-translate]] — 翻譯基礎設施（engine / quota / OAuth / append-resume / Gemini-Haiku fallback）＋一般雙語翻譯
- [[scripture-fathers]] — 公有領域教父原典；「參考現成中譯本校準」姿態本 skill 沿用
- [[ebook-pipeline]] — parse / OCR / standardize / 套書 split 上游
- [[translation-glossary]] — 人名／地名／哲學家／神學名詞詞庫（翻任何全集前先鎖譯名）
- [scripture-papal](../scripture-papal/SKILL.md) — 既有「拉/英/中三欄逐段對照」(alignDocs) content-file 版實作，可參考對齊邏輯
- 案例檔：[jung_collected_works.md](jung_collected_works.md)（心理學）／[mueller_collected_works.md](mueller_collected_works.md)（宗教學）／[panikkar_collected_works.md](panikkar_collected_works.md)（神學）／[yinshun_collected_works.md](yinshun_collected_works.md)‧[shengyen_collected_works.md](shengyen_collected_works.md)‧[hsingyun_collected_works.md](hsingyun_collected_works.md)（佛學）
- 詞庫：[jung_glossary.md](jung_glossary.md)／[mueller_glossary.md](mueller_glossary.md)／[panikkar_glossary.md](panikkar_glossary.md)（古希臘待建 `greek_philosophy_glossary.md`）
