---
name: scripture-papal
description: 教宗訓導文獻對照工具（/encyclicals）— 4 世紀 Damasus I 至今的教宗通諭／使徒勸諭／使徒憲令／自動詔書／使徒書信／演說／講道，三欄逐段對照（拉丁／英文／中文）。按世紀分組瀏覽；與 `/scripture-canon` portal 第 7 卡片串接。架構與 [[scripture-canon]] 的 `/creeds` 同源，重用 paragraphParser.ts + alignDocs() + textLoader.ts；資料源走「vatican.va + papalencyclicals.net + DCO + Migne PL + Schaff NPNF」五層 fallback；與 [[fathers]] 在 4-7c 教宗自然重疊（同一文件雙邊收，依用途不同呈現）。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

# Papal Magisterium — 教宗訓導文獻對照

## 0. 現況（2026-05-29 round 6 結束）

🟢 **`/encyclicals` portal 已上線**。228 教宗中 **80 位**（35%）有 ≥1 doc。系統總計約 **700 papal-doc**：

| 區 | tier | 篇數 | LA 實文 | LA placeholder |
|---|---|---:|---:|---:|
| A | teaching | 308 | 206 | 102（14-19c 散漏 marquee） |
| B | curia | 2 | 2 | 0 |
| C | message/homily | 387 | 0 | 387（原本非拉丁） |

**按世紀**（A 區 ≥1 doc 教宗 / 該世紀總教宗數）：

4c 3/3 ✅ ／ 5c 6/11 ／ 6c 4/14 ／ 7c 2/20 ／ 8c 1/11 ／ 9c 2/21 ／ 10c 1/22 ／ 11c 3/17 ／ 12c 4/16 ／ 13c-21c 54/93。詳 `data/encyclicals/_coverage_audit.md`。

**三區命名**（user 訂正）：A 區 `tier='teaching'` 通諭／勸諭／憲令／自動詔書；B 區 `tier='curia'` 信理部／禮儀部 dicastery 發行；C 區 `tier='message'` 廣播詞／講詞／演說／講道（hsscol 來源原本非拉丁）。

### 已建立 pipeline 工具（位於 `scripts/_papal_*.py`，gitignored local）

**通用 ingest**：
- `scrape_papal_encyclical.py` — vatican.va HTML 通用抓取（la/it/en/zh_tw 四語、footnote anchor、flat heading、auto-space）
- `postprocess_papal_chinese_pdf.py` — vatican.va 中文 PDF → marker text（opencc s2tw + 中式段碼）
- `align_papal_headings.py` — EN spine + la/it/zh re-anchor
- `ingest_papal_encyclical.py` — one-stop（scrape → PDF fallback → align → 報告）
- `scrape_papalencyclicals_net.py` + `discover_papalencyclicals.py` + `_batch_ingest_papalenc_pope.py` + `_batch_papalenc_all_popes.py` — 教宗等級批次

**中譯對位**：
- `_denzinger_to_papal.py` — 光啟 Denzinger DH 範圍對位（解 19c-20c marquee 中譯）
- `_hsscol_to_papal.py` + `_hsscol_batch_ingest.py` — 香港聖神修院 archive.hsscol.org.hk 619 項中譯庫對位
- `_hsscol_discover.py` + `_hsscol_map_tier.py` — hsscol 全索引 + tier 自動分類

**LA backfill / OCR**：
- `_papal_wikisource_la_backfill.py` + `_papal_wikisource_la_round{3,6,6b,6c}.py` — Wikisource LA 批次（4-19c 共 ~80 篇）
- `_papal_pl54_column_splitter.py` + `_papal_pl54_gemini_batch.py` — PL 54 djvu 兩欄→單欄分篇
- `_papal_gemini_pdf_ocr.py` — PL PDF 頁範圍 Gemini Vision OCR（範本：PL 54 Leo I）
- `_papal_pl119_responsa_ocr.py` — PL 119 Nicholas I Responsa 完整 19 頁 OCR（107 KB publication-quality LA）

**其他**：
- `_papal_heading_translate.py` — H2 小標題 Gemini 直譯（LA + ZH）
- `_papal_la_targeted.py` — 特殊 URL 攻破單篇 placeholder

### 待辦（按優先級）

| P | 項目 | 規模 | 路徑 |
|---|---|---|---|
| P0 | 14-19c A 區散漏 LA backfill | 102 篇 | vatican.va PDF / DCO 03d/ / PL 200/214-217 OCR |
| P0 | 中文翻譯缺漏 | 171 篇 | `_chinese_audit.md` |
| P1 | Innocent III ~50 letters | PL 214-217（~210 MB） | Gemini Vision OCR |
| P1 | Leo I 剩 ~80 letters + ~70 sermons | PL 54 djvu 已下載 | `_papal_pl54_*` |
| P1 | Alexander III 封聖權 decretal | PL 200 | OCR |
| P2 | PL 13 Tomus Damasi + Siricius Directa 質量提升 | 已下載 88 MB | Gemini OCR pp.178-187 + 590-605 |
| P2 | PL 151 Urban II Clermont 質量提升 | 已下載 51 MB | OCR |
| P2 | Leo XIV（2025-） | 等台灣主教團官方中譯 | hold |

📋 完整待辦：`data/encyclicals/_todo.md`、`_chinese_audit.md`、`_coverage_audit.md`

### 跟 [[scripture-canon]] / [[fathers]] 分工

- **scripture-canon**：**集體**文件（大公會議產出的信經 / canons / dogmatic decree）+ 信條 + 教會法規 + 教父著作搜尋 + 聖經對照 + 典外
- **scripture-papal**（本 skill）：**個別教宗**頒布的文件（通諭 / 勸諭 / 憲令 / 自動詔書 / 使徒書信 / 演說 / 講道）
- 邊界：Vatican I/II dogmatic constitutions 雖由教宗頒布、但是 ecumenical council 產出 → 歸 creeds；單一教宗以個人身分頒布（e.g. *Ineffabilis Deus* 1854 / *Munificentissimus Deus* 1950）→ 歸本 skill
- 4-7c 教宗 = 教父，[[fathers]] 與本 skill 雙邊都收，但展示重點不同：[[fathers]] 以「個人神學家著作」呈現；本 skill 以「教宗訓導文獻」按世紀分組三欄對照
- 1-3c 教宗（Clement I / Soter / Victor I / Cornelius / Stephen I）暫不在本 skill 範圍，留給 [[fathers]] 處理

---

## 1. 範圍 & 文件分類

### 涵蓋類型（vatican.va 11 大文件類型 + 中世紀補丁）

| 拉丁名 | 中文 | 性質 |
|---|---|---|
| Litterae Encyclicae | **通諭 (Encyclical)** | 教宗給全體主教 / 全體信徒的公開信，最高層級訓導 |
| Constitutiones Apostolicae | **使徒憲令** | 信理性 / 法律性最高層級頒布 |
| Exhortationes Apostolicae | **使徒勸諭** | 主教會議後綜合宣告（e.g. *Evangelii Gaudium* 2013） |
| Litterae Apostolicae | **使徒書信** | 較廣泛的書信，含 motu proprio |
| Motu Proprio | **自動詔書** | 教宗主動頒布、無外人請示 |
| Bullae | **詔書 (Bull)** | 中世紀至 19c 主要文件形式；蠟印封 |
| Brevia | **教宗短札 (Brief)** | 較簡短的官方文件 |
| Allocutiones / Discorsi | **演說** | 公開演講；常觸及神學議題 |
| Homiliae | **講道** | 禮儀講道，常含教導內涵 |
| Epistulae | **教宗書信** | 私函公開後成訓導 |
| Nuntii | **訊息 (Messages)** | 世界和平日／大齋／聖誕節等訊息 |

**起始**：4 世紀 Damasus I 366-384 + Siricius 384-399。Damasus 382《Tomus Damasi》最早正式體裁；Siricius 385《Directa》是學界認可第一封正式 Decretal。

---

## 2. 資料源策略（4-5 層 fallback）

### 拉丁原文

| Tier | 來源 | 涵蓋 |
|---|---|---|
| 1 | **vatican.va** | Pius IX 1846 → 今；多語齊全 |
| 2 | **documentacatholicaomnia.eu (DCO)** | 7c-今全教宗 PDF |
| 3 | **la.wikisource.org** | 4-19c marquee 散見（已驗證 ~80 篇可救） |
| 4 | **Migne PL (217 vols, 1844-55)** | 4c-12c 教宗書信全集 — archive.org 掃描 PDF；Gemini Vision OCR |
| 5 | **Bullarium Romanum** (1733-58) | 中世紀-巴洛克教廷詔書集 |

### 英文翻譯

| Tier | 來源 | 涵蓋 |
|---|---|---|
| 1 | **vatican.va** /en/ | Pius IX 1846 → 今多數 |
| 2 | **papalencyclicals.net** | 7c-今最完整英譯匯整 |
| 3 | **Fordham Internet Medieval Sourcebook** | 中世紀 marquee（Leo I / Gregory I / Nicholas I 等） |
| 4 | **Schaff NPNF Vol 12-14** + newadvent / ccel | 4-7c 教父等級 |

### 中文翻譯

| Tier | 來源 | 涵蓋 |
|---|---|---|
| 1 | **vatican.va** /zh-hant/ | Vatican II 後文件大多有；零散 ~60% |
| 2 | **archive.hsscol.org.hk** 香港聖神修院 619 項文獻 | 20-21c 完整中譯主力 |
| 3 | **catholic.org.tw** / **catholic.org.hk** | 主教團翻譯近現代訓導 |
| 4 | **光啟 Denzinger** (ebook `568726d3-...`) DH 對位 | 19-20c marquee 摘錄 |
| 5 | placeholder（**不主動用 LLM 翻譯**） | — |

**禁忌**：本 skill 不主動用 LLM 翻譯中文 placeholder 為終稿（同 creeds 規則）。

### Migne PL archive.org identifier（已驗證）

PL 13 (Damasus+Siricius / `patrologiaecur13mign`) ／ PL 54 (Leo I / `sanctileonismagn01leoi`) ／ PL 55, 56 ／ PL 63 (Hormisdas) ／ PL 77 (Gregory I) ／ PL 88, 89 (Hadrian I) ／ **PL 119 (Nicholas I)** ／ PL 144 (Leo IX) ／ PL 151 (Urban II) ／ PL 162, 200 (Alexander III) ／ PL 214-217 (Innocent III 3 卷)

**Naming 不一致**：`patrologiaecur{N}mign` / `patrologiaecursu0{NNN}mign` / `patrologiae_cursus_completus_lat_vol_{NNN}` 都試。

---

## 3. Schema & 資料佈局

### File-based（同 creeds pipeline）

```
data/encyclicals/
  types.ts                  — PapalDocument / PapalDocumentVersion interface
  index.ts                  — registry + groupByCentury() + groupByPope()
  popes-catalog.ts          — 231 位教宗（4c Sylvester I → 21c Leo XIV）
  textLoader.ts             — Vite ?raw lazy import wrapper
  paragraphParser.ts        — re-export data/creeds/paragraphParser.ts

  {NNc-pope-slug}/
    {doc-slug}.ts           — metadata
    {doc-slug}-latin.txt    — LA 原文
    {doc-slug}-english.txt  — EN 翻譯
    {doc-slug}-chinese.txt  — ZH 翻譯（placeholder = '⏳' 開頭）

pages/encyclicals/
  index.vue                 — 入口；按世紀 group + 教宗 sub-group
  [slug].vue                — Detail 三欄對照
  pope/[slug].vue           — 教宗 profile 3-tab UI（teaching / curia / message）
  century/[century].vue     — 世紀內教宗列表

server/api/encyclicals/
  list.get.ts / by-pope.get.ts
```

### PapalDocument TypeScript interface

```ts
export type PapalDocTier = 'teaching' | 'curia' | 'message'

export type PapalDocCategory =
  | 'encyclical' | 'apostolic-const' | 'apostolic-exhort' | 'apostolic-letter'
  | 'motu-proprio' | 'bull' | 'brief' | 'allocution' | 'homily' | 'message'
  | 'epistola' | 'instruction' | 'declaration' | 'decree' | 'notification'
  | 'responsum' | 'curia-document' | 'letter-informal'

export type PapalDocLanguage = 'lat' | 'en' | 'zh-Hant' | 'it' | 'fr' | 'es' | 'de' | 'pt' | 'grc'

export interface PapalDocumentVersion {
  lang: PapalDocLanguage
  label: string
  textKey: string             // 對應 {textKey}.txt（不含 .txt）
  source?: string             // URL 或紙本書名
  placeholder?: boolean
  translator?: string
}

export interface PapalDocument {
  slug: string                // 'rerum-novarum-1891'
  popeSlug: string
  tier?: PapalDocTier         // 預設 'teaching'（docTier() fallback）
  issuer?: string             // tier='curia' 時填部會名
  category: PapalDocCategory
  titleLat: string
  titleEn: string
  titleZh: string
  promulgationDate: string    // YYYY-MM-DD
  century: number
  summaryZh: string
  topics: string[]
  versions: PapalDocumentVersion[]  // 中→英→拉 排序
  displayMode: 'simple' | 'paragraph-aligned'
  related?: string[]
  vaticanUrl?: string
  notes?: string
}
```

### UI — 三欄逐段對照

`pages/encyclicals/[slug].vue` 直接 import creeds 元件：`alignDocs(latParsed, enParsed, zhParsed)` outer-join by 段號 / heading 順序，每 row 三欄並列；inline `[^N]` footnote 點擊跳 `#fn-{lang}-{N}`；經文 reference (`Rom 11:17-24`) 自動標 `.scripture-ref`。

vatican.va 文件每段有 `<a name="N">` anchor → markdown `N. {text}` 對齊；papalencyclicals.net / DCO PDF 無顯式段號者用 `## {章節}` heading 對齊。

---

## 4. /scripture-canon Portal 整合

`pages/scripture-canon/index.vue` 第 7 卡片「🕊️ 教宗訓導文獻」(`/encyclicals`)。`pages/index.vue` 工作台「📜 經典對照與註釋」卡片 ul list 也加一條。

---

## 5. URL pattern

### vatican.va

```
https://www.vatican.va/content/{pope-slug}/{lang}/encyclicals/documents/hf_{pope-slug}_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/apost_constitutions/documents/...
https://www.vatican.va/content/{pope-slug}/{lang}/apost_exhortations/documents/...
https://www.vatican.va/content/{pope-slug}/{lang}/apost_letters/documents/hf_{pope-slug}_motu-proprio_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/{messages|speeches|homilies}/...

pope-slug: leo-xiii / pius-x / benedict-xv / pius-xi / pius-xii / john-xxiii /
           paul-vi / john-paul-i / john-paul-ii / benedict-xvi / francesco / leo-xiv
lang: la / en / it / fr / es / de / pt / zh-hant / zh-hans
```

注意：Francis 拉丁 slug 是 `francesco`（義文）；早期教宗（Pius IX 1846-78）部分 vatican.va 不含；中文 URL 部分用 `zh-hant`、部分用 `zh_hant` 需兩個都試。

### papalencyclicals.net

```
https://www.papalencyclicals.net/{pope-slug-lower}/{slug-lower}.htm
範例：/leo13/l13rerum.htm / /pius09/p9quanta.htm / /bon08/b8unam.htm
```

### documentacatholicaomnia.eu (DCO)

```
https://www.documentacatholicaomnia.eu/04z/z_{ID}-{ID},_{Pope}_PP._{Roman},_{Title},_LT.pdf
範例：z_1198-1216,_SS_Innocentius_III,_Epistolae_Et_Decreta,_LT.pdf
```

### Wikisource LA（已驗證的 pattern）

```
https://la.wikisource.org/wiki/{Title}                  — 單篇直接
https://la.wikisource.org/wiki/Epistolae_({Pope})       — 集合作品
https://la.wikisource.org/wiki/Epistolae_({Pope})/N     — 分章
```

對 4-12c 早期教宗，wikisource 常以 `Epistolae (X)` / `Decreta (X)` / `Privilegia (X)` 形式整集；Round 6 一次 batch 救入 ~80 篇 LA。

### Fordham Medieval Sourcebook

```
https://sourcebooks.fordham.edu/{basis|source}/{slug}.asp
範例：/basis/866nicholas-bulgar.asp（Nicholas I Responsa 191 KB）
     /source/urban2-5vers.asp（Urban II Clermont 5 chronicler 版本）
```

### archive.hsscol.org.hk

香港聖神修院神哲學院文獻庫，619 項教廷文獻完整中譯。`_hsscol_to_papal.py` + `_hsscol_batch_ingest.py` 對位下載 + pdftotext / big5hkscs HTML 轉檔。

---

## 6. SOP — 新增一份教宗文件

1. 確認該文件不在 creeds 範圍（非大公會議產出）
2. 在 `data/encyclicals/{NNc-pope-slug}/{doc-slug}.ts` 建 metadata
3. 抓拉丁／英文／中文（依 fallback 順序）並落地為對應 `.txt`
4. 在 `data/encyclicals/index.ts` import + 加進 `ALL_DOCUMENTS`；如為新教宗，patch `textLoader.ts` POPE_LOADERS + POPE_FOLDER
5. `npx vue-tsc -p .nuxt/tsconfig.json --noEmit` 驗證
6. 重啟 dev → `/encyclicals` 確認三欄對齊正常
7. `git add` + commit + push（依「程式碼變更自動 push」記憶）

---

## 7. 已知 tradeoff

| 議題 | 現行決策 |
|---|---|
| 演說／講道是否全收 | 是 — hsscol C 區 387 篇已收（無 LA） |
| 中世紀文件深度 | 全收可找到拉丁原文者；Wikisource 缺者標 placeholder |
| 中文 placeholder 策略 | 缺者標 `⏳` placeholder 等紙本／官方源；**不**用 LLM 翻譯為終稿 |
| 資料層 | file-based（同 creeds，~700 .txt + .ts）。scale 大時可遷 DB |
| 是否與 creeds 合表 | 否 — 個別教宗 vs 大公會議，語義不同 |

---

## 8. 跟既有 skill cross-reference

- [[scripture-canon]] — `/creeds` pipeline 元件（`paragraphParser.ts` / `alignDocs()` / `textLoader.ts`）直接複用；Denzinger 中譯 ebook 含部分中譯 DH 對位
- [[scripture-fathers]] — 4-7c 教宗 = 教父，雙邊都收（見 §0 分工）
- [[ebook-pipeline]] — Migne PL / Bullarium 紙本掃描走 OCR pipeline
- [[ebook-translate]] — 若決定批次 Gemini 翻譯英→中
- [[translation-glossary]] — 神學名詞中譯（*transubstantiation* / *concupiscentia* / *anathema*）翻 encyclical 前先對
- [[scripture-denzinger]] — DH 100-1500 範圍對位（Trent 之前部分）
