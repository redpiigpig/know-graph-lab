---
name: ebook-collected-works
description: 「經典學者全集」的收錄流程 —— 以**學科**組織（哲學／社會學／宗教學／神學／佛學／心理學／人類學…），獨立 `/collected-works` portal（依學科分區）＋作家 hub（小傳／肖像／年表／著作目錄）＋單卷 reader。跟 [[ebook-translate]]（一般外文→繁中雙語）、[[scripture-fathers]]（公有領域教父原典）並列。四種收錄 pipeline：**多語對照**（原文＋既有譯本＋我的繁中，N 欄逐段）／**單一語言**（本即繁中的漢傳全集，零翻譯零對齊）／**REFERENCE**（已有完整第三方中譯就不重譯，原文逐段對照）／**自譯**（English-first 引擎逐段翻）。Use when 使用者要把某位學者的全集（依學科）做成 hub＋逐段對照上架、要新增作家或學科、要擴充 reader 多欄、要設計／修多語 JSONL schema、要對齊跨版本段落。各學科案例見下「§C 各學科案例」；schema／對齊／portal 基建見「§B 方法論核心」。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。

> 📊 **各全集翻譯線現況（2026-07-22，由 [[project_fleet_keeper]] 的 `KGL_Fleet_Keeper` 排程託管，`scripts/fleet_keeper.ps1`）**：
> - **榮格**：CW9ii／11／12 ✅＋4 部早期著作 ✅；`scripts/jung_run_queue.py` 跑全 19 卷 CW（走 **NVIDIA**，把 Gemini 讓給 ACCS OCR）。CW1-8/9i/10/13-18 待補。新收「文集典藏版（全九冊）」EPUB 進 Drive `全集/心理學/榮格/`（含 CW4/5/6/8/9i/10/15/17/18 九冊）。
> - **哲學家（柏拉圖/亞里斯多德）**：`scripts/plato_run_queue.py` 跑 26 部（**NVIDIA**）；21/26 有滿快取，近完成。
> - **潘尼卡**：7 部完成；**吠陀經驗（義文大部頭 ~1.7 萬段）走 Haiku**，sec3854 進行中。**翻完後這條改放馬克斯韋伯（社會學全集）**。
> - **內村鑑三**：第一波青空文庫 QUEUE_COMPLETE ✅（`uchimura_auto.py`）。無教會神學區另有矢內原＋七人 hub（[[project_uchimura_yanaihara]]）。
> - **東方聖書（sacred-books-east）**：奧義書✅；剩 5 卷（阿維斯陀/古蘭經/法句經/易經/耆那教）`sbe_translate.py --loop --backend haiku`。
> - **引擎分流**：Gemini→ACCS OCR；NVIDIA→榮格佇列＋哲學佇列＋大愛道；Haiku→潘尼卡吠陀＋SBE。**監管只需 1 個 session**（艦隊靠排程自我修復，多 session 會搶 checkpoint）。

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
const DISCIPLINE_ORDER = ['哲學', '宗教學', '宗教社會學', '神學', '佛學', '心理學', '社會學', '人類學']
// 未列出的學科接最後（localeCompare），空組不顯示
```

**年代→地域兩層分組（2026-07-18，user 拍板）**：`CwAuthor` 另有 `era?`／`region?` 兩欄，**只有哲學／神學用**。portal 對「有任一作家帶 `era`」的學科自動改成**兩層**：先依 `era`（年代，依組內最早生年排序）分大標，年代內再依 `region`（地域）分小標，才出卡片；沒 `era` 的學科（宗教學／宗教社會學／心理學／佛學）維持單層依 `sortYear` 排。**每個年代內都可有多個地域欄**（user：「古代中世紀近代都要分地域」）。
- 哲學 era：`古代`/`中世紀`/`近代`/`現代與當代`；region：`西方`（古代＝希臘羅馬、中世紀＝拉丁經院）/`拜占庭`/`伊斯蘭`/`猶太`/`印度`/`中國`/`日本`/`美洲`/`非洲`/`韓國`
- 神學 era：`教父時代`/`中世紀`/`宗教改革`/`近代`/`現代與當代`；region：`西方（拉丁）`（教父～近代）/**`歐陸`**（現代與當代歐洲，含英國）/`北美`/`東方（希臘）`/`東方（希臘／東正教）`/`東方（敘利亞／東方教會）`/`東方（東方正統教會）`/`拉丁美洲`/`非洲`/`東亞`/`東亞（日‧韓）`（無教會）/`南亞`/**`原住民`**（北美／毛利／台灣玉山神學院）。現當代神學共 10 地域欄；南方神學／第三世界＝拉美＋非洲＋亞洲已涵蓋，不另建重複 region。

**現況歸類（每學科 → 作家）**：

> 🆕 **2026-07-18 大規模補齊 246 位「人＋書目」骨架**（全 `planned`／`copyright`，肖像逐一驗證，翻譯之後才排）。用 13 路平行研究 agent 產 JSON → `assemble.py` 去重驗證組裝入 store。取向：**多元＋非西方中心並重**（女性與非西方代表貫徹各近現代群組）。目前 store 共約 280 位。

| 學科 | 規模 | 涵蓋（年代→地域）| pipeline |
|---|---|---|---|
| **哲學** | 123 | 古代（西方＝希臘羅馬 19／中國先秦／印度正統六派）・中世紀（西方拉丁經院／拜占庭／伊斯蘭／猶太／印度吠檀多）・近代（西方／中國明清／日本江戶／韓國性理學／波斯後古典）・現代與當代（西方／中國新儒家／印度／日本京都／非洲／拉美美洲） | 多語對照（公有領域者） |
| **宗教學** | 17 | 單層：穆勒`max-mueller`・潘尼卡`panikkar`＋泰勒→弗雷澤→奧托→伊利亞德→多尼格＋井筒俊彦／中村元 | 多語／REFERENCE／自譯 |
| **宗教社會學** | 15 | 單層（全新）：涂爾幹・韋伯・特洛爾奇・齊美爾・伯格・盧克曼・貝拉・斯塔克・道格拉斯／戴維／阿薩德… | 多語對照 |
| **神學** | 104 | 教父（拉丁／希臘／敘利亞）・中世紀（含希爾德加德等女神秘家）・宗教改革・近代・現代與當代西方（巴特／拉納／過程神學）・非西方處境（解放／女性／黑人／非洲／東亞含無教會9位／南亞／東正教）・新教其餘宗派（衛理／聖公／重浸／貴格／福音／五旬節）・東方正統教會六會 | 多語對照 |
| **佛學** | 3 | 印順`yinshun`・聖嚴`shengyen`・星雲`hsingyun` | 單一語言（本即繁中） |
| **心理學** | 18 | 單層：榮格`jung`＋佛洛伊德・阿德勒・威廉詹姆斯・佛洛姆・弗蘭克・希爾曼・荷妮／克萊恩／安娜佛洛伊德／河合隼雄／森田正馬 | 多語對照 |

已完成**轉錄**的卷（reader 可讀）仍見下 §C 各案例；上表多為 hub＋書目骨架。

**加一位新作家 = 在 `stores/collectedWorks.ts` 的 `authors[]` push 一個 `CwAuthor`**（免 DB migration、免 server route）。務必填 `disciplineGroup`（**別跟一句話副標 `discipline` 搞混**）＋ `sortYear`（生年，BCE 為負；portal 依此在學科組內排序，缺省者排末尾）；`color` 須在 [tailwind.config.ts](../../../tailwind.config.ts) safelist（amber/blue/rose/emerald/violet/sky/indigo/cyan/orange/stone/purple/teal，shade 50–300/500–700，**別用 -400**）。**一人一 hub**（前蘇格拉底不併卡）。詳見 [§B7 portal + hub](#b7-portal--作家-hub-頁)。

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

## §B6 全集專屬三欄 reader（2026-07-02 起，取代 /ebook UI）

**全集不再走 `/ebook/[id]`**（user 拍板：/ebook 空白封面＋分頁感錯位「開頭很奇怪」）。改用**聖經三欄式**專屬 reader [pages/collected-works/[slug]/[work].vue](../../../pages/collected-works/[slug]/[work].vue)（版型仿 `pages/creeds/[slug].vue` grid mode），`[work]` = ebookId。

- **每 row grid**：`3.25rem 1fr…1fr` ＝ **左引用號欄 + 繁中 + 各來源欄**（欄數依 `source_order` 動態；單語書＝引用號＋繁中兩欄）。逐段用 `lib/multilang-sources.ts` 的 `normalizeSources`＋`zipParallel`（content 與各 `sources[lang]` 按 `\n\n` 段 index zip、補白）。`## …` 開頭的段渲染為跨欄小標。
- **引用號欄**＝`chunk.anchors[i]`（**Stephanus 17a／Bekker 1094a**；無 anchors 的舊書退化用 `page_number`）。點擊複製「`{作者}《{書名}》{anchor}`」＋設 `#cite-{anchor}` hash 深連結 → 滿足「詳細引用方式」。
- **每卷頂部導讀卡**（page 1）：書名＋`data/collectedWorksIntros.ts[ebookId].intro`（簡介導讀段落）＋引用格式示例；取代原空白封面。缺項降級只顯示 `work.note`。有 cover chunk 的舊書：`chunk_type==='cover'` 只出導讀卡、不出 body。
- **Toggle**：`中 | 對照 | <各語言>`（沿用 `availableViewModes`/`langLabel`）。**分頁**：每 Stephanus/Bekker 頁一 view（`?p=N`）＋TOC 抽屜（依 `volume` 分卷）。
- **取資料鐵則**：client-side `$fetch('/api/ebooks/'+id+'?includeToc=1&page=N')` **必帶 `Authorization: Bearer <supabase access_token>`**（`getSession().access_token`）——`/api/ebooks` `requireAuth()`，SSR/純 cookie 會 401（踩過）。
- **`anchors` 資料契約**：`plato_build.build_units` 產 `anchors=[sec_id…]`（與段一一對應）→ `multilang_chunks.build/assemble` 傳遞 → `ChunkData.anchors?` → `/api/ebooks/[id].get.ts` currentPage 白名單 `anchors`（**四處都要，缺一到不了 client**）。
- **⚠️ Nuxt 巢狀路由雷**：`[slug].vue` + `[slug]/[work].vue` 會讓 `[slug]` 變父層（需 `<NuxtPage/>` 否則 child 不渲染、只出 hub）→ 已把 hub 改成 `[slug]/index.vue`、與 `[work].vue` 同層。
- **驗證（2026-07-02 截圖實證）**：新 reader page1 導讀卡＋引用格式＋Stephanus 17 三欄；page2 每 row 引用號 18a/18b + 繁中/希臘/英 逐段對齊。一次性 shot 腳本 `scripts/_cw_shot.mjs`（用完即刪、`_`-prefix 未 gitignore 別 commit；auth＝magic-link＋session cookie＋`kgl_device_id=screenshot-bot`；nav timeout 要在首個 goto 前設 150s）。
- 底層仍沿用 [lib/multilang-sources.ts](../../../lib/multilang-sources.ts)（**別各自重寫 schema 判斷**）；`/ebook/[id].vue` 保留給一般電子書。

---

## §B7 Portal + 作家 Hub 頁

全集**不放電子圖書館（/ebook）裡**，而是獨立 `/collected-works` portal（首頁「📚 全集」cyan 卡）。portal 依學科分區（見 §A）。每位學者一張卡 → 作家 hub `/collected-works/[slug]` 最外層呈現：

1. **學術貢獻簡介**（`contribution: string[]`，繁中段落，支援 `**粗體**`）
2. **肖像**（`portraitUrl`：Wikimedia Commons `Special:FilePath/<檔名>?width=500` 公有領域縮圖，**不用 Supabase Storage**；當代人物無 PD 肖像 → `''`，hub 用 emoji 佔位）
3. **生平學術年表**（`timeline: {year, text}[]`）
4. **著作目錄**（`works[]`，**按 `category` 分組、組內依 `yearSort` 排序**；顯示年分／繁中名／原文名／來源語言標／轉錄狀態）

**單卷閱讀走全集專屬三欄 reader `/collected-works/[slug]/[work]`**（見 §B6；`work.ebookId` 帶過去；`externalUrl` 優先，如東方聖書）；hub `linkTarget()` 回 `/collected-works/${slug}/${ebookId}`（**不再是 /ebook**）。hub 只是入口＋完整書目＋路線圖。每卷導讀寫在 [data/collectedWorksIntros.ts](../../../data/collectedWorksIntros.ts)（keyed by ebookId）。

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

## C1 哲學：古希臘哲學家（依年代）

**新學科群（2026-07-01 起，hub 骨架，pipeline ① 多語對照）**。portal 改依學科分組後開的「哲學」群，著作目錄多為 `planned`，逐步轉錄。全屬**公有領域**（古典原文＋十九世紀權威英譯 Jowett/Ross/MacKenna），可做希臘／英／繁中三欄。肖像用 Wikimedia Commons 公有領域胸像／畫像（已 curl 逐一驗證可載；普羅泰戈拉‧高爾吉亞無合適 PD 像 → emoji）。接手轉錄比照榮格 pipeline；人名先查 [[translation-glossary]] 哲學家表鎖譯名。

**🚩 結構定案（user 2026-07-01）：一人一 hub、前蘇格拉底不併卡、`sortYear` 依生年排序。** 原先的合併卡 `presocratics` 已拆為 14 個獨立作家；全群 **19 位**，portal 依 `sortYear`（生年 BCE 負值）由古到今排：

| # | slug | 生年(sortYear) | 骨架 | 肖像 |
|---|---|---|---|---|
| 1–3 米利都 | `thales` / `anaximander` / `anaximenes` | −624/−610/−586 | 水／無限者 apeiron／氣 殘篇 | ✅ |
| 4 | `pythagoras` | −570 | 數為萬物之本、靈魂輪迴（見證 DK14/58） | ✅ |
| 5 | `xenophanes` | −565 | 批判擬人神觀、趨一神（DK21） | ✅ |
| 6 | `heraclitus` | −535 | 萬物流變、邏各斯（DK22） | ✅ |
| 7 | `parmenides` | −515 | 存有為一、本體論（DK28） | ✅ |
| 8 | `anaxagoras` | −500 | 種子＋努斯 nous（DK59） | ✅ |
| 9 | `zeno-elea` | −495 | 運動悖論（DK29） | ✅ |
| 10 | `empedocles` | −494 | 四根＋愛與爭；《淨化》（DK31） | ✅ |
| 11–12 辯士 | `protagoras` / `gorgias` | −490/−483 | 人是萬物尺度／〈論非存在〉 | emoji |
| 13 | `socrates` | −470 | 無著作；見柏拉圖／色諾芬 | ✅ |
| 14 | `democritus` | −460 | 原子與虛空；歡愉倫理（DK68） | ✅ |
| 15 | `plato` | −428 | 早／中／晚期對話錄＋書信（Stephanus＋Jowett） | ✅ |
| 16 | `aristotle` | −384 | 工具論‧自然‧生物‧形上‧倫理政治‧修辭詩學（Bekker＋Ross） | ✅ |
| 17 | `epicurus` | −341 | 三書信＋主要教義＋附盧克萊修 | ✅ |
| 18 | `epictetus` | 50 | 手冊＋談話錄＋斯多噶參照 | ✅ |
| 19 | `plotinus` | 204 | 《九章集》六集＋波菲利傳（MacKenna） | ✅ |

**下一步**：擇一 hub（建議柏拉圖《蘇格拉底的申辯》起）取 PD 希臘原文（Perseus，Stephanus 編號，已驗證可抓）＋Jowett 英譯（Gutenberg #1656，已驗證）→ 走 §B2 多語 pipeline → 逐段三欄。專屬 glossary 建 `greek_philosophy_glossary.md`（理型 εἶδος、邏各斯 logos、努斯 nous、本原 archē、ataraxia、太一 to Hen…；對齊 repo 既有 `scripts/seed_glossary_philosophers.py`）。

## C2 宗教學：馬克斯‧穆勒 + 雷蒙‧潘尼卡

> **潘尼卡 2026-07-01 由「神學」改歸「宗教學」（user 拍板）** —— 其宗教學／比較宗教定位重於純系統神學。神學學科由內村鑑三＋矢內原忠雄開區（見 C3）。

### 穆勒（宗教學開山祖，pipeline ①）
案例檔 → **[mueller_collected_works.md](mueller_collected_works.md)**（版權表 / Longmans 18 卷目 / 來源 / 對齊 / 接手）＋詞庫 [mueller_glossary.md](mueller_glossary.md)。

一句話現況：Friedrich Max Müller（1823–1900，**宗教學開山祖**）卒於 1900 → **全部著作早已公有領域**，是 collected-works 最乾淨案例。以英文寫作為主 → 預設英＋繁中雙語；有平行德文版的卷（起手卷《宗教學導論》1873 = 德《Einleitung》1874，英德同構四講＋兩附論）做真三欄。**✅《宗教學導論》三欄竣**（`33333333-…`，7 chunks，~21.5 萬繁中字）；其餘 13 部走 `scripts/mueller_auto.py` 自動 queue（English-first：先無 LLM 上架英文、再逐段翻）。

> 🧹 **來源欄 OCR 清理（2026-07-01）**：老書 djvu OCR 的 `en`/`de` 來源欄殘留亂符（•■€™♦►）、斷詞、目錄點漏／頁眉／掃描樣板，中文因 LLM 已濾故乾淨。工具 `scripts/mueller_source_clean.py`（測試優先，`scripts/tests/test_mueller_source_clean.py` 10 綠）：`clean_source(text,lang)` 刷符號/控制字元/樣板＋保守斷詞合併（德文「„」在 de 保留）；`is_junk_para` 高精度判整段 junk（**只認「點漏後直接接頁碼」的目錄行**，避免誤殺 19 世紀散文省略號）；driver 丟 junk 時同步丟 en/de/zh/fail 保持平行，**zh 文字絕不編輯**。`--dry-run` 先驗、`--apply` 套用；改完逐卷 `mueller_auto.assemble_and_upload`（isr 走 `mueller_build --build-only --upload`）。首輪 17 部清 1437 段／丟 39 junk 段。

### 潘尼卡（宗教間對話／比較神學，pipeline ③④）
案例檔 → **[panikkar_collected_works.md](panikkar_collected_works.md)**（版權表 / Opera Omnia 12 卷目 / 起手卷 / 接手）＋詞庫 [panikkar_glossary.md](panikkar_glossary.md)。

一句話現況：Raimon Panikkar（1918–2010，**宗教間／宗教內對話與跨文化哲學巨擘**）卒於 2010 → **受版權至約 2080，榮格型（非穆勒）**：無乾淨 PD 全文、第三方中譯不當主欄。採 **English-first**。多語原創（加泰隆／西／義／英／德），Opera Omnia 是主題重編 → 多數卷先英＋繁中雙語。**兩種 build（user 拍板 2026-06-12）**：③ **REFERENCE**（`--src <en> --zh-src <zh>`，有完整中譯就不重譯，第三方中譯簡→繁當主欄、英文逐段對照、零 LLM）／④ **自譯**（`--src <en>`，無中譯的卷 English-first 引擎自譯）。CJK 章標題由 `_CJK_HEADING_RE` 切段。**✅ 上架 2 本**（宗教內對話 `55555556-…` REFERENCE；神的經驗 `55555561-…` 自譯 39 chunks）；自譯 queue `scripts/panikkar_auto.py --run-queue` 背景連跑（8 卷，義/英/西）。腳本 `panikkar_build.py`/`panikkar_auto.py`/`ocr_pdf_to_text.py`，pytest 29 例綠。

## C3 神學：無教會主義九位

**神學學科＝無教會主義（Mukyōkai）譜系群（2026-07-16 開區＋同日擴收，共九位）**，仿 C1 古希臘「一人一 hub、依 sortYear 排序」。

**兩位核心（各自獨立 case-study）**：內村鑑三（1861–1930，創始者）卒逾 95 年 → **全球公有領域**，青空文庫 11 篇＋archive.org 岩波全集掃描＋兩部**英文原著**（How I Became a Christian／Representative Men of Japan）；矢內原忠雄（1893–1961，殖民政策學者‧戰後東大總長）→ **日本（2012 起）與台灣 PD**（《帝国主義下の台湾》1929 出版全球乾淨，NDL pid 1191101 インターネット公開已驗證）。hub＋書目（內村 10 部／矢內原 13 部，全 planned）已上 → **[uchimura_collected_works.md](uchimura_collected_works.md)**／**[yanaihara_collected_works.md](yanaihara_collected_works.md)**。

**譜系七位（合併一檔）**：畔上賢造（1884–1938，PD，3 部）／塚本虎二（1885–1973，日版權至 2043，3 部）／黒崎幸吉（1886–1970，至 2040，3 部）／藤井武（1888–1930，**PD**，4 部）／南原繁（1889–1974，至 2044，4 部，唯一有 PD 肖像）／**金教臣**（1901–1945，**PD**，韓國《聖書朝鮮》創刊人，3 部）／咸錫憲（1901–1989，韓版權至 2059，4 部）——金教臣＋咸錫憲是本 portal **首兩個韓文（ko）案例**。受版權者比照榮格前例 `status='copyright'` hub＋書目先行。取捨（政池仁／大塚久雄／高橋三郎落選理由）、版權表（2018 日本改法不溯及）、肖像與來源盤點 → **[mukyokai_collected_works.md](mukyokai_collected_works.md)**。

全文轉錄均待起手（優先序：內村 後世への最大遺物 → 矢內原 帝国主義下の台湾 NDL OCR → 藤井武／畔上／金教臣 PD 線）。

## C4 佛學：印順‧聖嚴‧星雲（單一語言，pipeline ②）

全集本即繁中 → 零翻譯零對齊，走 §B5 PLAYBOOK。案例檔：[yinshun_collected_works.md](yinshun_collected_works.md) / [shengyen_collected_works.md](shengyen_collected_works.md) / [hsingyun_collected_works.md](hsingyun_collected_works.md)。

- **✅ 印順導師**（`yinshun`，amber ☸️）：來源 CBETA Y 系列 TEI P5 XML（`cbeta-org/xml-p5`，44 XML=42 部，非商業可再散布）。`cb:mulu` 三層→章節樹、`lb` 邊碼→段碼。`scripts/yinshun_build.py`（8 例綠）+ `yinshun_registry.json`。**44 卷 / 5324 chunks 上架**。
- **✅ 聖嚴法師**（`shengyen`，teal 🥁）：來源 ddc.shengyen.org《法鼓全集 2020 紀念版》— SPA 殼但靜態檔全枚舉（`all_books` 110 冊／`vol_dump` 4079 篇／`toc.html`／`html/{輯-冊-篇}.html`）。`p.indent` 正文／`p.hN` 標題／`span.pb data-page` 保留頁碼。`scripts/shengyen_build.py`（9 例綠）。**110 冊 / 4181 chunks 上架**。
- **✅ 星雲大師**（`hsingyun`，orange 🪷）：官網 reader 殼一度誤判「不出全文」，**user 給 `/ArticleDetail/artcle{N}` 後破關**（每篇免登入 server-render 全文＋麵包屑階層，不在 sitemap）。crawl `artcle{1..25500}`（19,888 篇有效、err=0）→ 麵包屑分組成 **109 冊 / 19,997 chunks**。`scripts/hsingyun_build.py`（10 例綠）。**🔑 教訓：薄殼站找不到內容端點時，直接問 user 要「實際在讀的文章 URL」往往秒破關。**

## C5 心理學：榮格全集

案例檔 → **[jung_collected_works.md](jung_collected_works.md)**（版權表 / GW·CW 20 卷目 / 公有領域判定 / 來源 / 接手清單）＋詞庫 [jung_glossary.md](jung_glossary.md)。**本 skill 誕生的首案，多語對照 pipeline ① 的原型。**

一句話現況：榮格（1875–1961）GW 德文原典＋CW 英譯**多數卷版權內到 2031**，網路免費全文多盜版掃描；**僅 1930 前早期著作有乾淨 PD 來源**。**✅ Jung PD pilot 全卷完成（2026-06-24）**：1912《Wandlungen und Symbole der Libido》(de) + Hinkle 1916《Psychology of the Unconscious》(en) 完成 ch01–ch13，共 **1,205 rows / 254,474 繁中字**，`ebook_id 22222222-2222-4222-8222-222222222222`。

**✅《分析心理學論文集》英→繁中完成（2026-07-03）**：Constance Long 編 15 篇論文集（Gutenberg #48225，公有領域，英文文集無平行德文 → 英繁中雙語）。`scripts/jung_collected_papers_translate.py`（已 commit）：解析本文 `h2 CHAPTER` 標記（非前付 `p2` TOC）→ 分章 chunk → **NVIDIA-first** 引擎（Gemini 4 key 全 429 → 略過重試風暴）→ 多語 JSONL(source_order=[en]) upsert，每段 checkpoint、每 8 段上傳、單段容錯（transient 504 跳過續跑）、可續傳。全 15 章 285 段完成，ebook `22222224-…`。**教訓**：① NVIDIA 偶爾在 zh 前洩漏前言（「以下是根據您的要求…繁體中文版本：」＋有時加 `---`），害 zh 段數 > en 段數對齊錯位 → 收尾要掃「開頭前言／水平線」清理（opener 正則 + 段數比對，見本次 14 段清理）；② detached run 要用 PowerShell `Start-Process`（Bash 背景任務會隨 session 結束被砍，本案中斷 2 次）。

**✅《七篇致亡靈的佈道》德英中三欄完成（2026-07-03，REFERENCE 復用）**：/gnostic 已有英＋繁中 182 段（doc `seven-sermons-to-the-dead`）→ 只加德文 1916 原典為第三版，**零重譯**。`scripts/sermons_add_german.py`（已 commit）：德文全文來源 klarerblick.de「Sieben Reden an die Toten」（Jung 1916，美國 PD；curl 抓 HTML→get_text 逐行→REDE I–VII 去 footer=170 段，存 committed `.claude/skills/scripture-gnostic/sermons_de_1916.json`）→ `align_paras`（借 jung_ptypen 的長度 DP）對齊到英文本文段（order_index 37–181；§36 標題另填德文題名；前付 0–35 編者導言無德文留空）→ 插 `gnostic_versions` code=de_1916(category=source, is_default_orig=true) + 140 `gnostic_sections`。reader `pickForCategory('source')` **自動顯示中/英/原文三欄，只影響此 doc**（`availableVersions` 依 doc 有無 section 過濾）。截圖實證：Die Toten kamen zurück von Jerusalem ↔ The dead came back from Jerusalem ↔ 死者從耶路撒冷回來 三欄對齊。榮格 hub 書目用 `externalUrl` 連 /gnostic、不重複建 ebook。**教訓**：WebFetch 小模型會以「版權」為由拒抓 PD 文本 → 改 curl 抓 HTML 本機解析；.env 是 CRLF，JS 載入器要 split('=')+trim（regex `$` 會被 `\r` 卡住）。

**✅《心理類型》德英中三欄完成（2026-07-01）**：既有 Baynes 1923 英＋繁中（`ebook_id 22222223-…`，257 chunks）接上 **Gutenberg #61543 德文 1921 原典** → 三欄，德文覆蓋 234/257。對齊法（`scripts/jung_ptypen_add_german.py`，無底線＝已 commit）：**敘事章（Einleitung、I–X）走長度型單調 DP 段落對齊**（`align_paras`，英文 djvu 過度切段時允許 N→1 合併）；**定義章 Ch XI 因兩語各按自家字母序排列（獨 Empfindung=英 Sensation 位置不同）改走「見出字對照」**（`align_definitions` + `DE2EN_DEF` 術語表；同 chunk 內德文定義依英文出現序 re-sort → 逐欄對齊）；Schlusswort 結論部另走段落 DP。截圖實證：敘事 p13（拉德伯圖斯三欄同段）、定義 p229（Reductive/Reduktiv/簡化 三欄同定義）。**教訓／殘留**：① 長章 V／X 中段有 ~1–2 段 drift（長度型對齊固有，可日後用 h3 小節錨點收窄）；② reader `splitParagraphs` 會 `filter(Boolean)` 去空段 → 不能用空段 padding 做 chunk 內精確 index 對齊，故定義多筆同頁靠 re-sort 對齊首段；③ 跨語「同一部作品、既有他語譯本」若**譯本忠於原文順序**（Baynes 1923 ≠ Hinkle 1916 之重組），逐段自動對齊即可成，不必人工。同法可延伸其他「德文原典 Gutenberg 有乾淨 HTML＋既有早期英譯」的卷。

**起手卷決策＋方法教訓（其他多語卷通用）**：
- Pilot 選公有領域早期著作 = 唯一現在能合法取得、兩版同源可驗證跨版對齊者。受版權 CW 卷須 user 提供合法來源檔（**不抓盜版全文**）。
- 🔴 **德 1912 ↔ 英 1916 非段落同構（實證）**：Hinkle 重組結構（自序≠Jung Einleitung，heading 自動對齊會抓錯）→ **正確逐段三欄需人工逐句配對 + 親譯**，非自動 run。多數全集卷的既有他語譯本同樣非段落同構，此問題普遍。
- 穩定方法（每章）：德掃描 PDF → **Haiku 重 OCR**（Gemini 4 key 全耗盡）→ **內容指紋**配對 de↔en 章（非 heading）→ 人工逐段對齊 → 親譯（先查 [jung_glossary.md](jung_glossary.md)）→ build（三 list 段數必須相等，對齊閘會 SystemExit）。續傳細則見 [jung_collected_works.md](jung_collected_works.md)「🚀 新 session 接手清單」。

---

## §B9 文體版面（genre → reader 版面，2026-07-19）

**轉錄/翻譯時先判斷文體**（user 拍板：不同文體要不同版面，非通用一種）。`CwWork.genre`（`CwGenre`）決定 collected-works reader `[work].vue` 的呈現：
- `dialogue` 對話錄：段首 `〔講者〕內文` → 講者標籤 + 對話輪。**🚨 現有 Plato 是逐 Stephanus 節翻（一節多講者、zh 一整塊）無法 retrofit 講者分行 → 未來 dialogue 收錄要改「逐 speech 為單位」ingest**（Perseus Plato TEI 有 `<said who>` 可取講者）。
- `verse` 詩歌讚歌：保留詩行（單行換行）與詩節（空行）、懸掛縮排、逐行對齊（以法蓮/衛斯理聖詩/內薩瓦爾科約特爾/蘇菲詩）。
- `aphorism` 格言命題：逐條編號卡（斯多噶手冊/伊比鳩魯主要教義/維根斯坦小數編號）。
- `quaestio` 經院問答：段首 `〔異議/反之/正解/答覆〕` → 四段角色分區配色（阿奎那神學大全）。
- `treatise`(預設)/`essay`/`lecture`/`diary-letters`/`narrative`：通用逐段版面。
判定 helper `scripts/genre_classify.py`（結構啟發式；**hint（fetch manifest 已標／Haiku 覆核）優先**，純文字易被目錄騙故門檻保守）。reader 改動 regression-safe（未標＝現行版面，已截圖驗證）。內容慣例：對話錄/問答段落一律以 `〔角色〕` 起始，詩歌保留換行——**ingest 時就要埋好這些標記**。

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
- 案例檔：[jung_collected_works.md](jung_collected_works.md)（心理學）／[mueller_collected_works.md](mueller_collected_works.md)（宗教學）／[panikkar_collected_works.md](panikkar_collected_works.md)（宗教學）／[yinshun_collected_works.md](yinshun_collected_works.md)‧[shengyen_collected_works.md](shengyen_collected_works.md)‧[hsingyun_collected_works.md](hsingyun_collected_works.md)（佛學）
- 詞庫：[jung_glossary.md](jung_glossary.md)／[mueller_glossary.md](mueller_glossary.md)／[panikkar_glossary.md](panikkar_glossary.md)（古希臘待建 `greek_philosophy_glossary.md`）
