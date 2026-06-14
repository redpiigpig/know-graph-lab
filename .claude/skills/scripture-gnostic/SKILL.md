---
name: scripture-gnostic
description: 諾斯底主義文獻對照工具（/gnostic）— 把 The Gnostic Society Library (gnosis.org) 的文獻收進「📜 經典對照與註釋」portal 第 8 張卡片，按 gnosis.org 自己的 13 大分類瀏覽，每篇英文（站上公有領域英譯）／繁中（我逐段翻）兩欄逐段對照。架構 DB-backed，仿 [[scripture-canon]] 的 /apocrypha（documents / versions / sections 三表 + N 欄 reader），翻譯走 [[ebook-translate]] 引擎，HTML 切段／去重／對齊 gate 走 scripts/gnostic_library.py（純函式，test-first）。Use when 要新增／重抓某個 gnosis.org 分類或單篇諾斯底文獻、調 /gnostic reader、補翻譯、處理與 /apocrypha（拿戈瑪第）或 /fathers（教父駁斥）重疊的去重。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。


> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖任一邊超過 2000px 會炸掉整個 session。

# 諾斯底主義文獻 Skill（Gnostic Library — EN/ZH 逐段對照）

把 **The Gnostic Society Library**（[gnosis.org/library.html](http://gnosis.org/library.html)）的文獻收進 `/scripture-canon` portal 的第 8 張卡片 **`/gnostic`（諾斯底主義文獻）**，按 gnosis.org 自己的 13 大分類瀏覽，每篇**英文（站上公有領域英譯）／繁中（我逐段翻）兩欄逐段對照**。

這是 portal 家族裡跟 `/apocrypha` 最像的一塊（DB-backed reader、N 欄逐段），但**獨立一區**：

| | /apocrypha | **/gnostic（本 skill）** |
|---|---|---|
| 主幹分類 | OT / NT testament × genre | gnosis.org **13 大主題分類** |
| 來源 | 黃根春《基督教典外文獻》中譯 + 英／原文 | **gnosis.org 英譯（公有領域）+ 我的逐段繁中** |
| 欄位 | 中／英／原文 3+ 欄 | **英／中 2 欄**（schema 預留 source 欄日後可加原文） |
| Nag Hammadi | 黃根春中譯版 | gnosis.org 英譯 + 我的中譯版（**並存不衝突**） |

> 為什麼 Nag Hammadi 兩邊都有不衝突：`/apocrypha` 的拿戈瑪第是黃根春紙本中譯；`/gnostic` 的是 gnosis.org Robinson/Meyer 英譯 + 我自己逐段翻的繁中。讀者用途不同（一個讀既有中譯、一個讀英中對照）。

---

## 🟢 狀態（2026-06-14 定名／清理／詞庫 · 287 篇）

> **2026-06-14 定名＋清理＋詞庫批次**（user 拍板，先做定名不動正文）— [scripts/curate_gnostic_naming.py](../../../scripts/curate_gnostic_naming.py)：
> - **刪 17 筆雜項**：整個 `dead_sea`（11 筆全是書店／時間表／資源導覽頁，非原典；真死海古卷在 `/apocrypha` 崑蘭）＋ Mead 書店頁 2＋valentinus 導覽（目錄／virtual library／bibliography）3＋NHL 索引頁 1。304→**287 篇**。
> - **近代學者著作集中到 `modern`**（11 筆，display_order 13000+ 排該類最底＝「放下面」）：Pagels／Meyer／Rudolph／Drower／Mead 導論＋數篇研究 essay。`modern` 標籤改「現代文獻與近代學術」。
> - **定名（109 筆改動）**：與 `/apocrypha`（黃根春典外文獻）重疊者**逐字對齊**並存 `apocrypha_slug`（日後直接輸入中譯，兩邊一致；23 筆已連結）；其餘自譯按詞庫權威——Thomas=多馬、Mary=馬利亞、Andrew=安得烈、Stephen=司提反、Marcion=馬吉安、Clement=革利免、Celsus=塞爾蘇斯、Heracleon=赫拉克勒翁、Basilides=巴西理德、Faustus=浮士德、Valentinus=瓦倫廷、Stromata=雜記；修簡體 论→論。
> - **詞庫補登**（[scripts/seed_gnostic_glossary_extra.py](../../../scripts/seed_gnostic_glossary_extra.py)）：deities +11（摩尼／三重至偉的赫密士／阿斯克勒庇俄斯／牧人者／烏特拉＋拿俄賽尼／馬吉安／摩尼／曼達／卡特里／卡波克拉特各派）；theologians +4（瓦倫廷／巴爾戴桑／埃皮法內斯／阿達伊）；theological_terms +5 作品名（赫密士文集／大寶庫／凱法萊亞／狄奧多托語錄／皮斯特斯·索菲亞）。
> - **新增欄** `gnostic_documents.apocrypha_slug TEXT`（記錄與 /apocrypha 的對應，供日後直接匯入黃根春中譯）。
>
> ### ⏳ 新 session 接手清單（2026-06-14 交接）
> 1. **正文逐段重譯（先標最差篇）** — user 嫌先前轉錄「翻譯不太好」。
>    - ✅ **2026-06-14 品質修復批次（user 拍板：先修最差的、不全翻；命名一律照詞庫權威）** — [scripts/fix_gnostic_quality.py](../../../scripts/fix_gnostic_quality.py)：**section 層外科手術**，不重抓整篇。診斷出主要敗筆是 2026-06-06 批次的 **幻覺**——短英文標題（章名／`PREFACE.`／署名／引用行）被 deepseek/gemini **無中生有膨脹成整段中文 essay**；另有未翻（英/拉丁殘留）、引擎 meta 註解外洩（「我無法完成…著作權」「以下為逐字翻譯：」）、逐字英文 gloss（「光（Light）」）。
>      - 偵測器（高精度多訊號，已校過避開誤判如「我無法保持貞潔」這種正當第一人稱內文）：`classify()` = halluc_heading（en<70 且 zh≥2.5×en）／untranslated（latin>50%）／meta_leak（任務性 meta 開頭）／word_gloss（≥3 個小寫英文括註）。**初掃 779 段 / 110 篇**（halluc 598、untranslated 135、meta 37、gloss 9）。
>      - 修法：對每段**從 gnosis_en 英文源重譯**（標題→只譯成短標題，幻覺自動消失；真正內文本就在相鄰 section，未受損——已抽查 against-all-heresies #72→#73 證實）。prompt 加固（ingest_gnostic.py `GNOSTIC_PROMPT_TMPL`）：禁擴寫/禁 meta/禁 gloss、非英文也照譯、人名照詞庫（Yeshua→耶穌 等）。upsert 後 `classify()` 二次把關，仍壞才跳過不蓋。
>      - 跑法：`python -X utf8 scripts/fix_gnostic_quality.py --dry [--show N]` 預覽；`--engine haiku`（免費池乾就走 Max）跑全部；`--doc <slug>` / `--limit N` 局部；idempotent 可重跑。post-check 二次把關仍壞且 en≤80 → **保留英文源 verbatim**（短結構標記如經文引註／`Sections:`／羅馬數字／引用行，語言中性，勝過幻覺）。
>      - **✅ 2026-06-14 haiku 全量完成**：779 段重譯（pass1 747 ✓ + pass2 35）＋手動補 4 編者註（抄本缺頁）＋homily 7 處經文引註統一成引註形（原 LLM 把「Matt. xxvi. 39.」幻覺成整節經文）。**最終 `--dry` 僅餘 4 段 flagged，全是正當 verbatim**（Abraxas 咒語 glossolalia `NAHTRIHECCUNDE…`／basilides 引用標頭—本文在 #4／Pagels 書目／`Text: R. 354` 標記）。pytest 25 例綠。
>      - 偵測器校準教訓：①`我無法…`/`我已準備好…` 等 meta_leak 必須綁任務性脈絡（「我無法**完成/識別**」「我已準備好**接收文本**」），否則誤殺正當第一人稱內文（「我無法保持貞潔」）。②word_gloss 只抓**英文虛詞**括註（the/is/am/and…），不可抓學術音譯註（`（gnosis）（batos）（syzygy）（ruha）` 全是正當的）。
>       - **✅ 2026-06-14 命名一致性全 corpus 掃描（第二輪）** — [scripts/fix_gnostic_names.py](../../../scripts/fix_gnostic_names.py)：curated 變體→詞庫權威（name_recommended 絕對）的 SQL replace，比重譯便宜安全。**381 段更新**：Yeshua 耶舒亞/耶書亞→耶穌（104）、Marcion 馬吉翁→馬吉安（233）、Basilides 巴西里得→巴西理德、Heracleon 赫拉克利翁/里翁→赫拉克勒翁。**人工排除的陷阱**：約書亞=Joshua≠耶穌（不動）；執政官=這些 Acts/紀年文裡的羅馬proconsul/consul，非諾斯底 Archon（執政者，不動）；克勉(羅馬革利免)≠革利免(亞歷山卓)為兩人不可混替。只動 distinctive 變體，idempotent 可重跑。
>    - 其餘篇章之 register 精緻度仍可續修；新增變體加進 `fix_gnostic_names.py` 的 `NAME_FIXES`。重譯前可先 `python scripts/export_glossary_from_db.py` 同步詞庫。挑篇可先看 `fix_gnostic_quality.py --dry` 仍 flagged 者，或人工抽查。
> 2. **/apocrypha 中譯回填** — 23 篇已存 `gnostic_documents.apocrypha_slug` 指向 /apocrypha 對應篇。等黃根春那邊中譯做完後，依此欄把 apocrypha 的 `cct_zh` sections **直接輸入覆蓋** /gnostic 的 `zh` 版本（兩邊一致，不要自譯這 23 篇）。查連結：`SELECT slug, apocrypha_slug FROM gnostic_documents WHERE apocrypha_slug IS NOT NULL;`
> 3. **空分類** — `dead_sea`／`alchemical` 現為空，reader 已自動隱藏（`.filter(count>0)`），CATEGORIES 仍保留 key（日後若補真原典可直接用）。
> - 腳本可重跑（idempotent）：`curate_gnostic_naming.py --dry`（預覽）/ `--apply`；`seed_gnostic_glossary_extra.py`。

## 🟢 狀態（2026-06-06 全量完成 · 304 篇 / 20,012 段）

- ✅ **純函式核心（test-first，25 例綠）** — [scripts/gnostic_library.py](../../../scripts/gnostic_library.py) + [scripts/tests/test_gnostic_library.py](../../../scripts/tests/test_gnostic_library.py)：taxonomy / slug / 去重 / 分類頁解析 / 單篇 `<br>` 逐段解析 / **lxml 解析不閉合 `<p>` 讚歌頁** / 對齊 gate
- ✅ **DB schema** — [database/gnostic-schema.sql](../../../database/gnostic-schema.sql)（3 表 + RLS public read + seed `gnosis_en` / `zh` 兩版本），已 apply
- ✅ **reader + API + portal 卡片** — [pages/gnostic/index.vue](../../../pages/gnostic/index.vue)（13 分類 tab + 搜尋）/ [pages/gnostic/[slug].vue](../../../pages/gnostic/[slug].vue)（英中兩欄逐段 + 分類側欄）/ [server/api/gnostic/*.get.ts](../../../server/api/gnostic/)（documents / document / versions / search）/ [lib/gnostic-meta.ts](../../../lib/gnostic-meta.ts) 共用分類 meta；portal 第 8 張卡片 🜍
- ✅ **ingest 驅動腳本** — [scripts/ingest_gnostic.py](../../../scripts/ingest_gnostic.py)（`--list` / `--category` / `--url` / `--limit-paras` / `--limit-docs` / `--dry-run`）
- ✅ **pilot 實證** — Poemandres（赫密士文集，Mead 1906 PD）前 6 段英→繁中翻譯 + upsert 成功，DB 對齊正確（中譯品質佳，術語括註如 執政官（Archon））
- ✅ **reader 截圖實證**（2026-06-03）：list（中文篇名卡片）+ reader（中左英右兩欄逐段）都正確。
- ✅ **全量轉錄完成**（2026-06-06）：**304 篇 / 20,012 段繁中**，全 13 類掃完（alchemical gnosis.org 該類為空）。對齊 0 不齊、0 prompt-echo、0 空白段。
- ✅ **不閉合 `<p>` 讚歌頁修復**（2026-06-06）：gnosis.org 摩尼教／曼達教讚歌頁是古老 HTML、`<p>` 不閉合，舊 `html.parser` 巢狀化 → 每個內容 `<p>` 被當 non-leaf 丟掉（~31 篇真文獻誤判「無段落」漏收）。改 `_doc_soup()` 用 **lxml**（HTML5 自動閉合 `<p>`），manichaean 48→**75**、mandaean 5→**14** 補齊。
- ✅ **列表/側欄段數修復**：`documents.get.ts` 原本抓全部 sections 在 JS 端 tally → 撞 PostgREST 1000-row 上限（corpus 破 500 段後多數卡片誤標「未轉錄」）。改讀 DB 聚合 view `gnostic_section_counts`。

### 🔖 轉錄完成紀錄（2026-06-06）

**最終 DB**：**304 篇 / 20,012 段繁中**，逐 order_index 對齊（en↔zh 段數全相等）—

| 分類 | 篇 | 分類 | 篇 |
|---|---|---|---|
| manichaean 摩尼教 | 75 | dead_sea 死海古卷 | 11 |
| polemics 教父駁斥 | 50 | cathar 卡特里 | 11 |
| nag_hammadi 拿戈瑪第 | 30 | valentinus 瓦倫廷 | 10 |
| hermetica 赫密士 | 30 | modern 現代 | 9 |
| christian_apocrypha 基督教偽典 | 25 | mead G.R.S. Mead | 17 |
| gnostic_scriptures 古典經典 | 22 | mandaean 曼達 | 14 |

> 仍未收：少數 Mead 的新約批判／神智學雜文（非諾斯底原典）、以及與 `/fathers`（Clement《雜記》、Augustine 駁摩尼教）／`/apocrypha` 重疊而依去重規則排除者。

> 收尾（2026-06-06）：9 段 Haiku 對 trivial 來源（`Amen!` / `NOTES` / `(2 lines missing)` / `[illegible]` …）prompt-echo，已人工策展中譯修掉；7 段被誤判 trivial 漏翻的實質 prose（Pagels 段、編者佚失註、圖說）已補翻。完整性掃描函式見下方驗收 SQL。

**完工關鍵**：免費池（Gemini/NVIDIA）整夜乾掉後，切 `--engine haiku` 直連 Claude Max OAuth 一口氣翻完剩餘 ~224 篇（見引擎政策段）。

**接手指令（單一指令即可續跑）**：
```bash
bash scripts/gnostic_resume_loop.sh        # 自癒迴圈：--all --resume，跑完/卡住自動睡 45min 重試
# 或單輪：python -X utf8 scripts/ingest_gnostic.py --all --resume --engine haiku
```
> **引擎（2026-06-05 user 拍板）**：免費池（Gemini/NVIDIA）乾掉或被佔用時，**直接 `--engine haiku` 走 Claude Max OAuth**，不要空轉戳死掉的免費 key。`--engine haiku` 已修為**直連 `haiku_translate`**（原本誤 redirect 回 gemini 鏈）；`haiku_translate` backoffs 加長（0/30/90/180/300/600/600）以撐過 Max 滾動視窗 429。resume_loop.sh 預設已切 `--engine haiku`。免費池恢復後想省 Max 額度可改回 `--engine gemini`（該鏈仍會自動 cascade 到 Haiku 當第 3 層）。
- **單一實例守衛**：迴圈用 `c:/tmp/gnostic_loop.lock`，已在跑就拒啟動（防殭屍累積搶 key）。停止用 PowerShell 殺 `resume_loop.sh`/`ingest_gnostic.py` 程序 + 刪 lock。
- **`--resume` 跳過已入庫篇**，安全重跑。

**引擎鏈（3 層，user 2026-06-04 定案）**：`--engine gemini` = **Gemini 4 key → NVIDIA deepseek-v4-flash（4 帳號 round-robin）→ Haiku 救急**。各層 2-strike + cooldown；deepseek 是 NVIDIA 唯一安全模型（其餘崩段/壞 marker）。詳見 [[ebook-translate]] `translate_ebook_to_zh.py`。⚠️ **三池都有每日上限**：一夜重度跑會三池全乾（429），靠迴圈睡 45min 等重置自癒；別同時開多個迴圈（會互相搶爆配額）。

**翻譯品質防護（都已上線）**：
- **術語鎖定**：`GNOSTIC_PROMPT_TMPL` 內嵌 35 條權威譯名表（普累若麻/移涌/巨匠造物主/執政者/索菲亞/雅達巴沃…，依張新樟《諾斯替宗教》+ 中文維基），同步入 `/translation-glossary` 神祇與宗教名詞（religion=諾斯底）。新詞補在 `scripts/seed_gnostic_glossary.py`。
- **prompt-echo 防護**：`_looks_like_prompt_echo`（deepseek 對 trivial 輸入照抄指示 → 重試 2 次退回原文）。
- **trivial 來源不送 LLM**：`is_trivial_source`（頁碼 `p.126`/引註/純數字 → 逐字保留，根絕幻覺）。修既有用 `scripts/fix_gnostic_echoes.py` / `fix_gnostic_trivial.py`。
- **中文篇名**：`TITLE_ZH` 策展表 + `translate_title` 引擎兜底；既有篇名已 backfill 中文。
- 殘留：echo 約 1 段、reader 截圖只驗過 Poemandres/Pymander/Mithra。

### 版權實證補記
- gnosis.org 的 **Nag Hammadi 現代英譯（Meyer / Barnstone / Lambdin 等）皆有版權**（拿戈瑪第 1945 才出土，無 PD 英譯）→ 入庫須視為私人研究（站台本就 auth-gate），`source_url` 標 gnosis.org。
- **Mead 系列（Corpus Hermeticum 1906 / Pistis Sophia 1896 / Fragments 等）= 公有領域**，pilot 即取 Mead Poemandres，最乾淨。**起手優先 Mead / Hermetica / 古典 PD 文本**，Nag Hammadi 版權卷之後再依私人研究姿態補。

---

## 13 大分類（= gnosis.org library 章節，`CATEGORIES` in gnostic_library.py）

| key | 中文 | gnosis.org index | 去重 |
|---|---|---|---|
| `nag_hammadi` | 拿戈瑪第經集 | `naghamm/nhl.html` | |
| `gnostic_scriptures` | 古典諾斯底經典 | `library/gs.htm` | |
| `valentinus` | 瓦倫廷與其傳統 | `library/valentinus/index.html` | |
| `hermetica` | 赫密士文集 | `library/hermet.htm` | |
| `mead` | G.R.S. Mead 文集 | `library/grs-mead/mead_index.htm` | |
| `manichaean` | 摩尼教文獻 | `library/manis.htm` | |
| `mandaean` | 曼達教文獻 | `library/mand.htm` | |
| `cathar` | 卡特里派文獻 | `library/cathtx.htm` | |
| `polemics` | 教父駁斥諾斯底文獻 | `library/polem.htm` | ✅ 去重 |
| `christian_apocrypha` | 基督教偽典 | `library/cac.htm` | ✅ 去重 |
| `alchemical` | 煉金術文獻 | `library/alch.htm` | |
| `modern` | 現代諾斯底文獻 | `library/modern.htm` | |
| `dead_sea` | 死海古卷 | `library/dss/dss.htm` | ✅ 去重 |

**去重規則（user 拍板 2026-06-03）**：`polemics` / `christian_apocrypha` / `dead_sea` 跟 `/fathers`（教父駁斥諾斯底，如 Irenaeus《駁異端》）、`/apocrypha`（NT 偽典、死海古卷）大量重疊。ingest 前用 `is_duplicate(title, existing_en_titles)` 比對既有 corpus 的 `title_en`，**已收過的就跳過不重抓不重翻**。核心諾斯底（nag_hammadi / gnostic_scriptures / valentinus / hermetica / mead / 摩尼 / 曼達 / 卡特里）一律照收。

---

## 版權姿態

- gnosis.org 主力英譯多為 **G.R.S. Mead（1900s）/ 公有領域 Robinson 早期版**等老譯本 → **公有領域**，英文欄可直接入庫（`public_domain=true`），標 `source_url` 指回 gnosis.org。
- 少數現代英譯（Meyer 等）若仍在版權 → 標 `public_domain=false`，沿用既有書庫「私人研究」姿態；翻譯走本機 pipeline，**Claude 不在對話裡整段貼受版權英文**。
- 繁中欄永遠是**我自己逐段翻**（跟 [[ebook-collected-works]] / [[scripture-fathers]] 同姿態：第三方中譯絕不入庫）。

---

## Schema（仿 apocrypha 三表，放 database/gnostic-schema.sql）

```sql
gnostic_documents (
  slug VARCHAR(48) PK,            -- 'gospel-of-thomas' / 'pistis-sophia' / 'poimandres'
  title_zh, title_zh_short, title_en, title_orig,
  category VARCHAR(30),          -- = CATEGORIES[].key
  language_orig VARCHAR(20),     -- 'coptic' / 'greek' / 'syriac' / 'mandaic' / …
  composition_low, composition_high INT,
  summary_zh TEXT,
  source_url TEXT,               -- gnosis.org 該篇 URL
  display_order INT
)
gnostic_versions (
  code VARCHAR(30) PK,           -- 'gnosis_en'（站上英譯）/ 'zh'（我的繁中）/ 預留 'coptic_orig' …
  name_zh, name_en, language, language_zh,
  category VARCHAR(20),          -- 'english' / 'chinese' / 'source'
  public_domain BOOL, source_url TEXT, display_order INT,
  is_default_en, is_default_zh, is_default_orig BOOL
)
gnostic_sections (
  id BIGSERIAL PK,
  doc_slug FK, version_code FK,
  order_index INT,               -- EN↔ZH 對齊鍵（同 order_index = 對照同一段）
  section_label VARCHAR(80),     -- 'saying 12' / '§3' / 第 N 章
  text TEXT, char_count INT,
  UNIQUE (doc_slug, version_code, order_index)
)
```

對齊承諾：同一 `doc_slug` 下，`gnosis_en` 與 `zh` 的 section **逐 order_index 一一對應**（`assert_aligned` 在寫入前硬檢查）。

---

## Pipeline（每篇）

```
[1] 抓分類頁  curl -k <gnosis index>  → parse_category_index() → [{title, url}]
        │     ⚠️ gnosis.org 憑證過期，WebFetch 會失敗 → 一律走 curl -k / requests verify=False
        ▼
[2] 去重     dedup 類別才做：is_duplicate(title, 既有 apocrypha/fathers title_en) → 跳過
        │
        ▼
[3] 抓單篇   curl -k <doc url> → parse_document() → {title, sections:[英文段…]}
        │
        ▼
[4] 翻譯     每段英→繁中（ebook-translate 引擎：gemini→haiku fallback），術語照神學詞庫
        │     assert_aligned(en_sections, zh_sections)  ← 段數必須相等
        ▼
[5] 寫 DB    upsert gnostic_documents + gnostic_sections（gnosis_en + zh 各一批，同 order_index）
        │     PostgREST batch upsert（仿 ingest_apocrypha_zh.py）
        ▼
[6] reader 驗證（英／中 兩欄逐段；列表頁分類樹）
```

翻譯引擎 / quota 協調 / Gemini→Haiku 2-strike / OAuth refresh — **全部沿用 [[ebook-translate]]**，本 skill 不重造。

### ⚠️ gnosis.org 憑證過期
站台 HTTPS 憑證已過期，`WebFetch` 會回 `certificate has expired`。一律用 `curl -sk`（或 Python `requests` `verify=False` / `urllib` unverified context）抓 HTML。

---

## 純函式核心 — scripts/gnostic_library.py（test-first）

| 函式 | 作用 |
|---|---|
| `CATEGORIES` / `CATEGORY_BY_KEY` | 13 分類 taxonomy（key / label_zh / index_path / dedup flag / display_order）|
| `make_slug(title)` | URL-safe slug（去 leading "The"、括號譯者註、標點）|
| `normalize_title(title)` | 去重鍵（同上 + 標點→空白、collapse）|
| `is_duplicate(title, existing)` | 比對既有 corpus title_en，True=已收過 |
| `parse_category_index(html, base_path)` | 分類頁 → `[{title, url}]`，濾掉 nav/外站/重複 |
| `parse_document(html)` | 單篇 → `{title, sections:[…]}`，濾 script/空段/footer chrome |
| `align_ok` / `assert_aligned(en, zh)` | 逐段對齊 gate（段數相等否則 raise）|

測試：`python -X utf8 -m pytest scripts/tests/test_gnostic_library.py -q`（20 例）。

---

## SOP — 新增一個分類

1. `curl -sk http://gnosis.org/<index_path> > c:/tmp/gnostic/<key>.html`
2. `parse_category_index` 列出該分類所有篇目；dedup 類別先 `is_duplicate` 過濾
3. 逐篇 `curl -sk <url>` → `parse_document` → 翻譯 → `assert_aligned` → upsert
4. 跑 reader 確認分類樹 + 兩欄逐段
5. commit + push（[[feedback-auto-push]]）；更新本 SKILL.md 狀態表（[[feedback-skill-md-keep-current]]）

## SOP — 補單篇 / 重翻
直接對該 `doc_slug` 重抓 + 重翻 + upsert（UNIQUE(doc_slug,version_code,order_index) 覆蓋）。

---

## 起手卷（pilot）

核心諾斯底先做幾篇驗證 end-to-end：**多馬福音（Gospel of Thomas）／真理福音（Gospel of Truth）／約翰密傳（Apocryphon of John）**（nag_hammadi）+ **Poimandres**（hermetica）。pilot 跑通後機器原封不動延伸到其餘分類。

---

## See also
- [scripture-canon](../scripture-canon/SKILL.md) — portal 母體；本 skill 是第 8 張卡片，reader 仿其 /apocrypha
- [[ebook-translate]] — 翻譯引擎 / quota / Gemini-Haiku fallback（英→繁中那段）
- [[ebook-collected-works]] — 「HTML 抓取→切段→翻譯→逐段對照」同源姿態（`split_html_sections` 可參考）
- [[translation-glossary]] — 諾斯底／神學名詞中譯（翻譯前鎖譯名）
- [[scripture-fathers]] / `/apocrypha` — 去重對象（polemics / christian_apocrypha / dead_sea 重疊處）
