---
name: gnostic-library
description: 諾斯底主義文獻對照工具（/gnostic）— 把 The Gnostic Society Library (gnosis.org) 的文獻收進「📜 經典對照與註釋」portal 第 8 張卡片，按 gnosis.org 自己的 13 大分類瀏覽，每篇英文（站上公有領域英譯）／繁中（我逐段翻）兩欄逐段對照。架構 DB-backed，仿 [[scripture-canon-portal]] 的 /apocrypha（documents / versions / sections 三表 + N 欄 reader），翻譯走 [[ebook-translate]] 引擎，HTML 切段／去重／對齊 gate 走 scripts/gnostic_library.py（純函式，test-first）。Use when 要新增／重抓某個 gnosis.org 分類或單篇諾斯底文獻、調 /gnostic reader、補翻譯、處理與 /apocrypha（拿戈瑪第）或 /fathers（教父駁斥）重疊的去重。
---

> ⚙️ **引擎政策（2026-06-04 更新）**：所有 LLM 工作一律**優先用 NVIDIA（輝達，`https://integrate.api.nvidia.com/v1`，預設文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避免 429）**，第二層 fallback 用 Gemini，**第三層救急才用 Haiku（NVIDIA→Gemini→Haiku；前兩個免費池都用罄時才動 Haiku）**。視覺類用 NVIDIA 視覺模型（如 `nvidia/llama-3.1-nemotron-nano-vl-8b-v1`）。


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

## 🟢 狀態（2026-06-03 上線 MVP，end-to-end 已實證）

- ✅ **純函式核心（test-first，23 例綠）** — [scripts/gnostic_library.py](../../../scripts/gnostic_library.py) + [scripts/tests/test_gnostic_library.py](../../../scripts/tests/test_gnostic_library.py)：taxonomy / slug / 去重 / 分類頁解析 / 單篇 `<br>` 逐段解析 / 對齊 gate
- ✅ **DB schema** — [database/gnostic-schema.sql](../../../database/gnostic-schema.sql)（3 表 + RLS public read + seed `gnosis_en` / `zh` 兩版本），已 apply
- ✅ **reader + API + portal 卡片** — [pages/gnostic/index.vue](../../../pages/gnostic/index.vue)（13 分類 tab + 搜尋）/ [pages/gnostic/[slug].vue](../../../pages/gnostic/[slug].vue)（英中兩欄逐段 + 分類側欄）/ [server/api/gnostic/*.get.ts](../../../server/api/gnostic/)（documents / document / versions / search）/ [lib/gnostic-meta.ts](../../../lib/gnostic-meta.ts) 共用分類 meta；portal 第 8 張卡片 🜍
- ✅ **ingest 驅動腳本** — [scripts/ingest_gnostic.py](../../../scripts/ingest_gnostic.py)（`--list` / `--category` / `--url` / `--limit-paras` / `--limit-docs` / `--dry-run`）
- ✅ **pilot 實證** — Poemandres（赫密士文集，Mead 1906 PD）前 6 段英→繁中翻譯 + upsert 成功，DB 對齊正確（中譯品質佳，術語括註如 執政官（Archon））
- ⬜ **全量轉錄**：核心諾斯底各分類整批跑（建議過夜，gemini→haiku fallback 已驗證會自動接手）；reader 瀏覽器渲染尚未截圖驗證

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
- 繁中欄永遠是**我自己逐段翻**（跟 [[collected-works-multilang]] / [[fathers-translation]] 同姿態：第三方中譯絕不入庫）。

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
- [scripture-canon-portal](../scripture-canon-portal/SKILL.md) — portal 母體；本 skill 是第 8 張卡片，reader 仿其 /apocrypha
- [[ebook-translate]] — 翻譯引擎 / quota / Gemini-Haiku fallback（英→繁中那段）
- [[collected-works-multilang]] — 「HTML 抓取→切段→翻譯→逐段對照」同源姿態（`split_html_sections` 可參考）
- [[translation-glossary]] — 諾斯底／神學名詞中譯（翻譯前鎖譯名）
- [[fathers-translation]] / `/apocrypha` — 去重對象（polemics / christian_apocrypha / dead_sea 重疊處）
