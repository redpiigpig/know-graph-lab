---
name: papal-magisterium
description: 教宗訓導文獻對照工具（/encyclicals）— 4 世紀 Damasus I 至今的教宗通諭／使徒勸諭／使徒憲令／自動詔書／使徒書信／演說／講道，三欄逐段對照（拉丁／英文／中文）。按世紀分組瀏覽；與 `/scripture-canon` portal 第 7 卡片串接。Status: **規劃中 2026-05-27**；架構與 [[scripture-canon-portal]] 的 `/creeds` 同源，重用 paragraphParser.ts + alignDocs() + textLoader.ts；資料源走「vatican.va + papalencyclicals.net + DCO + Migne PL + Schaff NPNF」五層 fallback；與 [[fathers]] 在 4-7c 教宗自然重疊（同一文件雙邊收，依用途不同呈現）。
---

# Papal Magisterium — 教宗訓導文獻對照

> 🟢 **Status**: Phase 0 + 1B demo 已上線 2026-05-27（`/encyclicals` portal + Laudato Si' 2015 三欄對照 246 段齊全）。架構直接複用 [[scripture-canon-portal]] 的 creeds pipeline；資料層獨立 (`data/encyclicals/`) 但 `paragraphParser.ts` / `alignDocs()` 元件共用。
>
> **本 skill 與 [[scripture-canon-portal]] 的分工**：
> - scripture-canon-portal：**集體**文件（大公會議產出的信經 / canons / dogmatic decree）+ 信條 + 教會法規 + 教父著作搜尋 + 聖經對照 + 典外
> - papal-magisterium（本 skill）：**個別教宗**頒布的文件（通諭 / 勸諭 / 憲令 / 自動詔書 / 使徒書信 / 演說 / 講道）
>
> 兩者的邊界：Vatican I/II 的 dogmatic constitutions 雖由教宗頒布、但是 ecumenical council 產出 → 歸 creeds；單一教宗以個人身分頒布的 (e.g. Pius IX 1854 *Ineffabilis Deus* 聖母無染原罪定義、Pius XII 1950 *Munificentissimus Deus* 聖母升天信理) → 歸本 skill。

---

## 1. 範圍 & 文件分類

### 涵蓋類型（vatican.va 11 大文件類型 + 中世紀補丁）

| 拉丁名 | 中文 | 性質 | 規模估計 |
|---|---|---|---|
| Litterae Encyclicae | **通諭 (Encyclical)** | 教宗給全體主教 / 全體信徒的公開信，最高層級訓導 | 7c-今 ~300 篇 |
| Constitutiones Apostolicae | **使徒憲令** | 信理性 / 法律性最高層級頒布 (e.g. CIC 1983 頒布的 *Sacrae Disciplinae Leges* / *Pastor Bonus* 1988 curia 重組) | ~150 篇 |
| Exhortationes Apostolicae | **使徒勸諭** | 主教會議後綜合宣告 (e.g. *Evangelii Gaudium* 2013 / *Amoris Laetitia* 2016) | 20c-今 ~80 篇 |
| Litterae Apostolicae | **使徒書信** | 較廣泛的書信，含 motu proprio | ~500+ 篇 |
| Motu Proprio | **自動詔書** | 教宗主動頒布、無外人請示 | ~200 篇 |
| Bullae | **詔書 (Bull)** | 中世紀至 19c 主要文件形式；蠟印封 | 7c-19c 主要 |
| Brevia | **教宗短札 (Brief)** | 較簡短的官方文件 | 中世紀-近代 |
| Allocutiones / Discorsi | **演說** | 公開演講；常觸及神學議題 (e.g. Pius XII 1956 醫學倫理演說) | 19c-今 數千 |
| Homiliae | **講道** | 禮儀講道，常含教導內涵 | 19c-今 數千 |
| Epistulae | **教宗書信** | 私函公開後成訓導 | 各時期 |
| Nuntii | **訊息 (Messages)** | 世界和平日／大齋／聖誕節等訊息 | 20c-今 數千 |

### 起始點 & 分期

**起始**：第 4 世紀 — **Damasus I 366-384** + **Siricius 384-399**。Damasus I 382《Tomus Damasi》（Council of Rome 後的信經 + canon list）標誌教宗訓導文獻的最早正式體裁；Siricius 385《Directa》（致 Himerius 主教論教會紀律）是學界普遍認可的**第一封正式 Decretal**，現代教廷訓導文件的法律體裁源頭。

**1-3c 註記（不在本 skill 範圍）**：1 Clement (~95 CE) / Soter / Victor I / Cornelius / Stephen I 等早期羅馬主教書信仍有重要訓導意義，但歸入 [[fathers]] skill 處理（屬「使徒教父／早期教父書信」分類）；該領域與本 skill 的邊界 = 4 世紀（同一份文件如 Clement I 1 Clement 雙邊都可收，但本 skill 預設僅從 4c 起 ingest）。

**按世紀分組**（user 要求 UI 主軸）：
| 世紀 | 範圍 | 重點教宗 / 文件 |
|---|---|---|
| 4c | 366-400 | **Damasus I 366-84**（*Tomus Damasi* 382 / 致 Jerome 委託 Vulgate 翻譯諸信）、**Siricius 384-99**（*Directa* 385 — ★ 首封正式 Decretal） |
| 5c | 400-500 | Innocent I 401-17（譴 Pelagianism 諸信）、Zosimus 417-18、Celestine I 422-32（譴 Nestorius 致 Cyril 諸信）、★★ **Leo I「大良」440-61**（*Tome of Leo* 449 / 173 封書信 / 96 篇講道 — 中世紀前教宗訓導典範）、Gelasius I 492-96（*Famuli vestrae pietatis* 494 — ★ 「兩權說」doctrine） |
| 6c | 500-600 | Hormisdas 514-23（*Libellus Hormisdae* 515 — 東西教會合一公式）、★ **Gregory I「大額我略」590-604**（《Registrum Epistolarum》14 冊 ~850 信 / 《Liber Regulae Pastoralis》/《Moralia in Iob》/《Dialogues》— 中世紀教父／教宗交叉節點） |
| 7c | 600-700 | Boniface IV 608-15（萬神殿改聖殿）、Honorius I 625-38（後被第三次君士坦丁堡 681 譴責 — Vatican I 教宗無誤論辯論的歷史 case）、Martin I 649（譴 Monothelitism 殉道） |
| 8c | 700-800 | Gregory III、Zachary、Stephen II、Hadrian I（聖像爭議交涉） |
| 9c | 800-900 | Leo III（800 加冕查理曼）、Nicholas I 858-67（Photian Schism 起源）、John VIII |
| 10c | 900-1000 | 「Saeculum Obscurum 黑暗世紀」— 少量文件存世 |
| 11c | 1000-1100 | Leo IX 1049-54（東西分裂 1054）、Gregory VII 1073-85（敘任權之爭《Dictatus Papae》） |
| 12c | 1100-1200 | Alexander III 1159-81（封聖權集中）、Innocent II / III |
| 13c | 1200-1300 | ★ Innocent III 1198-1216（中世紀盛期權威）、Gregory IX（編《Decretales》／設立 Inquisition）、★ Boniface VIII 1294-1303（*Unam Sanctam* 1302） |
| 14c | 1300-1400 | Clement V 1305-14（亞維儂遷都）、John XXII 1316-34（神貧爭論）、Gregory XI 1377（回羅馬） |
| 15c | 1400-1500 | Eugene IV 1431-47（佛羅倫斯合一）、Nicholas V 1455 *Romanus Pontifex*（贊助大發現）、Sixtus IV、Alexander VI（劃地子午線 1494） |
| 16c | 1500-1600 | ★ Leo X 1520 *Exsurge Domine*（譴 Luther 41 條）、Paul III（召 Trent）、Pius V 1568-72（公佈 Tridentine 經本）、Sixtus V（CDF 設立） |
| 17c | 1600-1700 | Urban VIII（Galileo 第二次審判 1633）、Innocent X 1653 *Cum Occasione*（譴 Jansenism 5 命題）、Innocent XI、Clement XI 1713 *Unigenitus*（再譴 Jansenism） |
| 18c | 1700-1800 | ★ **Benedict XIV 1740-58** — 現代 encyclical 體裁奠基者；Clement XIII / Clement XIV（解散耶穌會 1773） |
| 19c | 1800-1900 | Pius VII（與 Napoleon Concordat 1801）、Gregory XVI 1832 *Mirari Vos*（首次譴自由主義）、★ Pius IX 1846-78（*Quanta Cura* 1864 + Syllabus / 聖母無染原罪 1854 / Vatican I 召集）、★ Leo XIII 1878-1903（*Rerum Novarum* 1891 社會訓導之父） |
| 20c | 1900-2000 | Pius X / Benedict XV / ★ Pius XI（*Casti Connubii* 1930 / *Quadragesimo Anno* 1931）/ ★ Pius XII（*Divino Afflante Spiritu* 1943 聖經研究現代化 / *Humani Generis* 1950 / *Munificentissimus Deus* 1950 聖母升天信理）/ ★ John XXIII（召梵二）/ ★ Paul VI（梵二閉幕 / *Humanae Vitae* 1968）/ John Paul I / ★★ John Paul II 1978-2005（14 encyclicals 含 *Veritatis Splendor* 1993 / *Evangelium Vitae* 1995 / *Fides et Ratio* 1998 / *Ut Unum Sint* 1995） |
| 21c | 2000-今 | ★ Benedict XVI 2005-13（*Deus Caritas Est* 2005 / *Spe Salvi* 2007 / *Caritas in Veritate* 2009）／★ Francis 2013-（*Lumen Fidei* 2013 / *Evangelii Gaudium* 2013 勸諭 / *Laudato Si'* 2015 / *Fratelli Tutti* 2020 / *Dilexit Nos* 2024） |

---

## 2. 資料源策略（4 層 fallback）

不同時期文件分佈在不同網站，無單一全紀錄源。pipeline 對每份文件按以下優先順序嘗試：

### 拉丁原文

| Tier | 來源 | 涵蓋 | 取法 |
|---|---|---|---|
| 1 | **vatican.va** | Pius IX 1846 → 今（部分 1800 前回溯）；多語齊全 | HTML scrape；`<p>` + `<a name="N">` paragraph anchor |
| 2 | **documentacatholicaomnia.eu (DCO)** | 7c-今 — 全教宗文獻 PDF/DOC 拉丁版；URL pattern `03d/{Y}-{Y},_{Author},_{Title},_LT.{pdf\|doc}` | `pdftotext -enc UTF-8 -layout` 或 `antiword`（沿用 scripture-canon-portal 已驗證 pipeline） |
| 3 | **Migne PL (Patrologia Latina, 217 vols, 1844-55)** | 4c-12c 教宗書信全集（Damasus / Leo I / Gregory I 拉丁原文最完整源） | archive.org 掃描 PDF；OCR 較困難（Gemini Vision） |
| 4 | **Bullarium Romanum** (1733-58 編) | 中世紀-巴洛克教廷詔書集 | archive.org 掃描 |

### 英文翻譯

| Tier | 來源 | 涵蓋 | 取法 |
|---|---|---|---|
| 1 | **vatican.va** /en/ | Pius IX 1846 → 今多數有英文；部分早於 1800 倒譯 | HTML scrape |
| 2 | **papalencyclicals.net** | 7c-今 — **現存最完整教宗文件英譯匯整**；Tier 1 補缺的關鍵 | HTML scrape；已在 creeds pipeline 用過 |
| 3 | **EWTN Library** | 部分文件中文／英文 PDF | archive.org / web archive |
| 4 | 學界譯本 (Schaff NPNF / Robinson 等) | 早期教宗（Gregory I 等） | Schaff Vol 12-13 已下載 |

### 中文翻譯（user 確認 2026-05-27：vatican.va 中文 + 台灣主教團網站）

| Tier | 來源 | 涵蓋 | 取法 |
|---|---|---|---|
| 1 | **vatican.va /zh/ 或 /zh-hant/** | Vatican II 後文件大多有；零散覆蓋 ~60% | HTML scrape + PDF/Gemini（如 vatican-ii pipeline） |
| 2 | **catholic.org.tw 主教團網站** | 台灣天主教主教團翻譯的近現代訓導 | scrape |
| 3 | **catholic.org.hk 香港教區** | 香港天主教教區翻譯 | scrape |
| 4 | **天主教研究中心 / 思高聖經學會** 月刊 / 出版物 | 學術譯本散見 | 紙本 OCR |
| 5 | Gemini Flash batch 翻譯 | 完全缺中文的標 placeholder；不自動補；user 決定特定文件再開 LLM 翻譯 task | 同 vatican-ii Gemini reextract pipeline |

**禁忌**：本 skill 不主動用 LLM 翻譯中文 placeholder 為終稿；同 scripture-canon-portal 規則 — 缺者標 placeholder 等紙本 / 官方源補。

---

## 3. Schema & 資料佈局

### File-based（同 creeds pipeline，2026-05-27 起始版本）

```
data/encyclicals/
  types.ts                  — PapalDocument / PapalDocumentVersion interface
  index.ts                  — registry + groupByCentury() + groupByPope()
  popes-catalog.ts          — { slug, name_zh, name_en, name_lat, pontificate_start, pontificate_end, century, nationality, notes_zh }
  textLoader.ts             — Vite ?raw lazy import wrapper（複用 data/creeds/textLoader.ts 模板）
  paragraphParser.ts        — 直接 re-export data/creeds/paragraphParser.ts

  04c-damasus-i/
    tomus-damasi-382.ts                   — metadata
    tomus-damasi-382-latin.txt
    tomus-damasi-382-english.txt
    tomus-damasi-382-chinese.txt          — placeholder
    ad-hieronymum-letters.ts              — 致 Jerome 委託 Vulgate 翻譯諸信
    ...
  04c-siricius/
    directa-385.ts                        — ★ 首封正式 Decretal
    ...

  05c-leo-i/
    tome-of-leo-449.ts                    — ★ 致 Flavianus 論基督論
    sermons-selected.ts                   — 96 篇講道精選
    epistolae.ts                          — 173 封書信彙整
    ...

  05c-gelasius-i/
    famuli-vestrae-494.ts                 — ★ 「兩權說」doctrine
    ...

  06c-gregory-i/
    moralia-iob-595.ts
    moralia-iob-595-latin.txt
    moralia-iob-595-english.txt
    regulae-pastoralis-591.ts
    ...

  09c-nicholas-i/
    responsa-bulgaros-866.ts              — 對保加利亞人 106 問答
    ...

  11c-gregory-vii/
    dictatus-papae-1075.ts
    ...

  13c-innocent-iii/
    venerabilem-fratrem-1202.ts
    ...

  13c-boniface-viii/
    unam-sanctam-1302.ts                  — ★ 最高教宗權威經典聲明
    ...

  16c-leo-x/
    exsurge-domine-1520.ts                — ★ 譴 Luther 41 條
    ...

  19c-leo-xiii/
    rerum-novarum-1891.ts                 — ★★★ 社會訓導開山之作
    aeterni-patris-1879.ts
    libertas-praestantissimum-1888.ts
    ...

  20c-john-paul-ii/
    veritatis-splendor-1993.ts
    evangelium-vitae-1995.ts
    fides-et-ratio-1998.ts
    ut-unum-sint-1995.ts
    ...

  21c-francis/
    laudato-si-2015.ts
    fratelli-tutti-2020.ts
    dilexit-nos-2024.ts
    ...

pages/encyclicals/
  index.vue                — 入口；按世紀 group + 教宗 sub-group
  [slug].vue               — Detail page 三欄對照（複用 alignDocs 邏輯）
  pope/[pope-slug].vue     — 單一教宗的全部文件列表

server/api/encyclicals/
  list.get.ts              — 列表 + 過濾（世紀／教宗／類型）
  by-pope.get.ts           — 按教宗

scripts/
  scrape_vatican_encyclicals.py    — vatican.va 多語言 scrape pipeline
  scrape_papalencyclicals_net.py   — Tier 2 英譯補
  scrape_dco_papal.py              — Tier 2 拉丁補（複用 scrape_dco_originals.py 模板）
  scrape_catholic_org_tw.py        — Tier 2 中文補
```

### `PapalDocument` TypeScript interface

```ts
export type PapalDocCategory =
  | 'encyclical'        // 通諭
  | 'apostolic-const'   // 使徒憲令
  | 'apostolic-exhort'  // 使徒勸諭
  | 'apostolic-letter'  // 使徒書信
  | 'motu-proprio'      // 自動詔書
  | 'bull'              // 中世紀詔書
  | 'brief'             // 短札
  | 'allocution'        // 演說
  | 'homily'            // 講道
  | 'message'           // 訊息
  | 'epistola'          // 書信

export type PapalDocLanguage = 'lat' | 'en' | 'zh-Hant' | 'it' | 'fr' | 'es' | 'de' | 'pt' | 'grc'

export interface PapalDocumentVersion {
  lang: PapalDocLanguage
  name: string             // 「拉丁原文」「英文 (vatican.va)」「中文 (主教團 1995 譯本)」
  textFile: string         // 對應 .txt 檔名
  source: string           // URL 或紙本書名
  placeholder?: boolean
  translator?: string      // 中譯者註明
}

export interface PapalDocument {
  slug: string                                  // 'rerum-novarum-1891'
  popeSlug: string                              // 'leo-xiii'
  category: PapalDocCategory
  titleLat: string                              // 'Rerum Novarum'
  titleEn: string                               // 'Of New Things' / 'On Capital and Labor'
  titleZh: string                               // 《新事》通諭
  promulgationDate: string                      // 'YYYY-MM-DD'
  century: number                               // 19
  summaryZh: string                             // 1-2 段中文摘要
  topics: string[]                              // ['社會訓導', '工人權利', '私有財產']
  versions: PapalDocumentVersion[]              // 中文 → 英文 → 拉丁 排序
  displayMode: 'simple' | 'paragraph-aligned'   // 沿用 creeds 既有兩種 mode
  related?: string[]                            // 其他相關文件 slug
  vaticanUrl?: string                           // 原 vatican.va URL（如有）
  notes?: string
}

export interface Pope {
  slug: string                  // 'leo-xiii'
  nameZh: string                // 良十三世
  nameEn: string                // Leo XIII
  nameLat: string               // Leo PP. XIII
  birthName?: string            // Vincenzo Gioacchino Pecci
  pontificateStart: string      // 'YYYY-MM-DD'
  pontificateEnd: string
  century: number               // pontificate 主要落在哪個世紀
  nationality: string           // 義大利 / 法國 / 西班牙 ...
  documentCount?: number        // 已 ingest 文件數
  notesZh?: string
}
```

### UI 互動 — 三欄逐段對照（與 creeds 完全一致）

`pages/encyclicals/[slug].vue` 直接 import creeds 既有元件：

```ts
import { parseDoc, alignDocs } from '@/data/creeds/paragraphParser'
import { loadCreedText } from '@/data/encyclicals/textLoader'  // 同樣的 Vite ?raw lazy import
```

對齊邏輯：`alignDocs(latParsed, enParsed, zhParsed)` outer-join by 段號 / heading 順序，每 row 三欄並列；inline `[^N]` footnote 點擊跳 `#fn-{lang}-{N}`；經文 reference (`Rom 11:17-24`) 自動標 .scripture-ref。

對 vatican.va 的文件：HTML 通常每段有 `<a name="N">` anchor，scraper 抓下來轉成 markdown `N. {text}`，與 paragraphParser 既有 paragraph 識別規則一致；不需改 parser。

對 papalencyclicals.net / DCO PDF 抽出的拉丁原文：通常沒有顯式段號，需用 `## {章節}` heading 對齊。中世紀短詔書（如 *Unam Sanctam* 5 段、*Dictatus Papae* 27 條）可手動補段號。

---

## 4. /scripture-canon Portal 整合

`pages/scripture-canon/index.vue` 加第 7 卡片：

```ts
{
  path: '/encyclicals',
  icon: '🕊️',
  title: '教宗訓導文獻',
  desc: '7 世紀至今教宗通諭／使徒憲令／勸諭／自動詔書／演說；按世紀分組 + 三欄對照（拉丁／英文／中文）',
  enabled: true,
}
```

`pages/index.vue` 工作台「📜 經典對照與註釋」卡片的 ul list 也加一條：
- 🕊️ 教宗訓導文獻 (`/encyclicals`)

---

## 5. Pipeline & 實作優先順序

> **實作策略（user 2026-05-27 確認，第二次調整）**：**從 21 世紀方濟各往回做**。理由：vatican.va 21c 文件中英拉三語齊全且 PDF 為主教團官方繁中譯本（品質有保證）；資料源最新最完整。**4-15c 早期教宗 + 19c 早期 19c marquee 列表暫時保留為背景脈絡，但 ingest 順序改為新→舊**。良十四世（Leo XIV, 2025-）暫不收，缺官方中譯。

### Phase 1 — Scaffold + 早期世紀「空殼卡片」+ 近代 8 篇 marquee（~1 週）

**A. 空殼卡片（4-15c）**：在 UI 預留 7 個世紀分區（4c / 5c / 6c / 7c / 8c-10c 合併 / 11-12c / 13-15c），每個分區掛 3-8 個「placeholder 教宗 + 預定文件名」卡片，點進顯示「⏳ 中譯待補 — 等 [[fathers]] Schaff 中譯成熟」狀態；**先不 ingest 任何拉丁／英文正文**，避免缺中文時看起來不齊。

預留命名列表（4-15c 共 ~30 篇骨架）：

| 世紀 | 預留教宗 + 文件 | 狀態 |
|---|---|---|
| 4c | Damasus I *Tomus Damasi* 382 / Siricius *Directa* 385 / Innocent I 致 Exuperius 405 | ⏳ |
| 5c | Innocent I 反 Pelagianism 諸信 / Celestine I 致 Cyril 諸信 / Leo I *Tome of Leo* 449 / Leo I 諸 sermons / Gelasius I *Famuli vestrae pietatis* 494 | ⏳ |
| 6c | Hormisdas *Libellus Hormisdae* 515 / Gregory I *Regulae Pastoralis* 591 / Gregory I *Moralia in Iob* / Gregory I 致 Augustine of Canterbury 諸信 | ⏳ |
| 7c | Honorius I 致 Sergius 諸信 / Martin I 拉特朗 649 譴 Monothelitism | ⏳ |
| 8-10c | Hadrian I 致 Charlemagne 諸信 / Nicholas I *Responsa ad consulta Bulgarorum* 866 | ⏳ |
| 11-12c | Gregory VII *Dictatus Papae* 1075 / Urban II 1095 號召十字軍 / Alexander III 封聖權集中 | ⏳ |
| 13-15c | Innocent III *Venerabilem* 1202 / Gregory IX *Decretales* 1234 / Boniface VIII *Unam Sanctam* 1302 / Alexander VI *Inter Caetera* 1493 | ⏳ |

**B. 近代 marquee 8 篇 ingest**（拉／英／中三語齊全；user 真實能看到三欄對照效果）：

1. Leo X 1520 *Exsurge Domine* — 譴 Luther 41 條（過渡 case：vatican.va 有英文 + 拉丁；中文 placeholder） ★
2. **Pius IX 1854 *Ineffabilis Deus*** — 聖母無染原罪信理定義
3. **Pius IX 1864 *Quanta Cura + Syllabus Errorum*** — 反現代主義
4. **Leo XIII 1891 *Rerum Novarum*** — 社會訓導開山 ★★★（第一篇 demo）
5. **Pius XII 1943 *Divino Afflante Spiritu*** — 聖經研究現代化
6. **Pius XII 1950 *Munificentissimus Deus*** — 聖母升天信理定義
7. **Paul VI 1968 *Humanae Vitae*** — 避孕爭議
8. **John Paul II 1995 *Evangelium Vitae*** — 生命福音

每篇至少 拉丁 + 英文 + 中文（vatican.va 三語檢查；無中文者標 placeholder）。

### Phase 2 — 全 Leo XIII (1878-1903) + 全 Pius XII (1939-58) + 全 John Paul II encyclicals（~3 週）

近代 encyclical 體裁鼎盛三位；社會訓導黃金期；資料源齊全 (vatican.va 全 3 語)。

### Phase 3 — 補齊 19-21c 所有 encyclical + apostolic constitution + exhortation（~6 週）

vatican.va archive 完整 scrape；按 promulgation date 排序 batch ingest；自動 deduplicate slug。
含 Francis 2013-2024 全 encyclical 與 apostolic exhortation。

### Phase 4 — Motu Proprio + 主要演說 + 訊息（~4 週）

範圍擴張到非主要訓導文件，但仍只在 vatican.va 範圍內（≥ Leo XIII 1878）。

### Phase 5 —（**等 [[fathers]] 中譯成熟後**）回頭 ingest 4-15c

中世紀文件解鎖條件：
- [[fathers]] 把 Leo I / Gregory I / Innocent III 等教父等級主教文集中譯標準化（target: Schaff NPNF Vol 12-13 中譯版完成）
- 紙本 Denzinger 中譯（光啟 2013，ebook_id `568726d3-967e-457a-ab69-7452b21d606f`）OCR 對齊到 DH 100-1500 範圍
- 或紙本《天主教大公會議文獻彙編》取得早期教宗書信中譯

到時把 Phase 1 預留的 ~30 個空殼卡片填實內容。

### Phase 6 — 中文 placeholder 系統性補

- 從 vatican.va 中文 PDF 重抽（同 vatican-ii Gemini pipeline）
- 從 catholic.org.tw / catholic.org.hk scrape 補
- 紙本《公教會之信仰與倫理教義選集》(光啟 2013 Denzinger 中譯) — 教義性 encyclical 多 DH 番號可對位（與 [[scripture-canon-portal]] Denzinger reader 共用）

---

## 6. URL pattern 已知

### vatican.va

```
https://www.vatican.va/content/{pope-slug}/{lang}/encyclicals/documents/hf_{pope-slug}_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/apost_constitutions/documents/hf_{pope-slug}_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/apost_exhortations/documents/hf_{pope-slug}_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/apost_letters/documents/hf_{pope-slug}_motu-proprio_{YYYYMMDD}_{slug}.html
https://www.vatican.va/content/{pope-slug}/{lang}/messages/...
https://www.vatican.va/content/{pope-slug}/{lang}/speeches/...
https://www.vatican.va/content/{pope-slug}/{lang}/homilies/...

pope-slug 範例：
  leo-xiii / pius-x / benedict-xv / pius-xi / pius-xii / john-xxiii / paul-vi / john-paul-i /
  john-paul-ii / benedict-xvi / francesco / leo-xiv (2025-)
lang：la / en / it / fr / es / de / pt / zh-hant / zh-hans
```

注意：
- Francis 拉丁 slug 是 `francesco`（義文），非 `franciscus`
- 早期教宗（Pius IX 1846-78）部分文件 vatican.va 不含；走 papalencyclicals.net + DCO
- 中文 URL 部分用 `zh-hant`、部分用 `zh_hant`（底線 vs hyphen），需要兩個都試

### papalencyclicals.net

```
https://www.papalencyclicals.net/{pope-slug-lower}/{slug-lower}.htm

範例：
  /leo13/l13rerum.htm     — Rerum Novarum
  /pius09/p9quanta.htm    — Quanta Cura
  /bon08/b8unam.htm       — Unam Sanctam
  /leo10/l10exdom.htm     — Exsurge Domine
```

### documentacatholicaomnia.eu (DCO)

```
https://www.documentacatholicaomnia.eu/04z/z_{ID}-{ID},_{Pope}_PP._{Roman},_{Title},_LT.pdf

範例：
  z_1198-1216,_SS_Innocentius_III,_Epistolae_Et_Decreta,_LT.pdf
  z_1740-1758,_Benedictus_XIV,_Bullarium,_LT.pdf
```

---

## 7. 跟既有 skill 的 cross-reference

- [[scripture-canon-portal]] — `/creeds` pipeline 元件 (`paragraphParser.ts` / `alignDocs()` / `textLoader.ts`) 直接複用；Denzinger 中譯 PDF (ebook_id `568726d3-967e-457a-ab69-7452b21d606f`) 含部分本 skill 範圍的中譯（DH 番號定位）
- **[[fathers]] 邊界（user 2026-05-27 確認）**：4-7c 教宗（Damasus / Leo I / Gelasius / Gregory I 等）同時是教父，**同一文件雙邊都收**；展示重點不同 —
  - 在 [[fathers]] 內：以「個人神學家著作」呈現，與其他作品並列在該教父 profile 下
  - 在本 skill 內：以「教宗訓導文獻」呈現，按世紀分組 + 三欄逐段對照（拉丁／英文／中文）
  - 1-3c 教宗（Clement I / Soter / Victor I / Cornelius / Stephen I）暫不在本 skill 範圍，留給 [[fathers]] 處理
- [[ebook-pipeline]] — 若取 Migne PL / Bullarium 紙本掃描，走 OCR pipeline
- [[ebook-translate]] — 若決定批次 Gemini 翻譯英→中作為 placeholder 替補，走此 skill
- [[translation-glossary]] — 神學名詞中譯（如 *transubstantiation* / *concupiscentia* / *anathema*）翻 encyclical 前先對

---

## 8. 已知 tradeoff & 待決定議題

| 議題 | 選 A | 選 B |
|---|---|---|
| **演說／講道是否全收** | 是 — 數千份；範圍極大 | 否 — 只收 encyclical + apostolic const + exhort + motu proprio 等正式訓導；演說／講道是 future scope |
| **中世紀文件深度** | 全收 7c-15c 所有可找到拉丁原文的 Bull | 只收 marquee 50 篇影響神學或政教關係的 |
| **中文 placeholder 策略** | 缺者標 placeholder 等紙本 / 官方源（同 creeds 規則）★推薦 | 用 Gemini Flash 批次翻譯 補 placeholder |
| **資料層** | file-based（同 creeds，~1500 .txt 檔）★推薦初版 | DB-based (`papal_documents` + `papal_document_versions` table) — 可搜尋；scale 大時遷移 |
| **是否與 creeds 合表** | 否 — 個別教宗文件 vs 大公會議產出，語義不同 | 是 — 都是「教會權威文件」可合 |

---

## 9. SOP — 新增一份教宗文件

1. 確認該文件不在 creeds 範圍（非大公會議產出）
2. 在 `data/encyclicals/{NNc-pope-slug}/{doc-slug}.ts` 建 metadata
3. 抓拉丁／英文／中文（依 4 層 fallback 順序）並落地為對應 `.txt` 檔案
4. 在 `data/encyclicals/index.ts` import + 加進 registry
5. 重啟 dev → 在 `/encyclicals` 確認出現於正確世紀 + 教宗下 → 點進確認三欄對齊正常
6. `git add` + commit + push（依「程式碼變更自動 push」記憶）

---

## 10. Status snapshot

### Scaffold + 架構
- [x] `data/encyclicals/types.ts` + `index.ts` + `popes-catalog.ts` + `textLoader.ts`
- [x] `paragraphParser.ts` 段號上限從 200 提升到 600（encyclical 常有 246-288 段）
- [x] 兩支抓檔腳本：`scripts/scrape_papal_encyclical.py`（vatican.va HTML 通用）+ `scripts/postprocess_papal_chinese_pdf.py`（中文 PDF layout → 段號標記化）
- [x] `scripts/fix_laudato_si_chinese_headings.py`：英文段標題→手譯映射，覆寫中文 PDF 抽出的雜亂 headings（每篇都需要這類專屬 fix 腳本，因 vatican.va 中文 PDF 排版各異）

### UI（三層 drill-down）
- [x] `/scripture-canon` 第 7 卡片「🕊️ 教宗訓導文獻」
- [x] `/encyclicals` — 上下排列的長型世紀卡片（21c→4c 共 18 張），每張只列教宗聖號（· 分隔，無括號注釋）
- [x] `/encyclicals/century/[century]` — 該世紀教宗列表，跨世紀者兩邊都有並掛「跨世紀」chip
- [x] `/encyclicals/pope/[slug]` — 教宗 profile + 訓導文件依類別分組
- [x] `/encyclicals/[slug]` — 三欄對照 detail，breadcrumb（🕊️/世紀/教宗/文件）

### 教宗名錄（**231 位 — 4c Sylvester I → 21c Leo XIV 全收**，2026-05-27 完成）
- [x] 中文聖號採思高聖經學會＋台灣主教團官方譯名
- [x] 跨世紀教宗在多世紀同時出現（centuriesOfPope 從 pontificate 起訖推算）
- [x] 19c-21c marquee 教宗保留 notesZh 詳述；4c-13c 重要教父教宗也補了 notesZh；其餘僅放姓名 + 任期 + 國籍

### Ingested 文件
- [x] **方濟各 2015 *Laudato Si'***（首篇 demo）— 三語 246 段齊全 + 172 footnote + 手譯 6 章節 42 個 section heading

### 待辦 ingest 順序（21c → 19c）
- [ ] **方濟各**：Fratelli Tutti 2020 / Dilexit Nos 2024 / Lumen Fidei 2013（與本篤十六合著）
- [ ] **本篤十六世**：Deus Caritas Est 2005 / Spe Salvi 2007 / Caritas in Veritate 2009
- [ ] **若望保祿二世**：14 道通諭（Redemptor Hominis 1979 / Veritatis Splendor 1993 / Evangelium Vitae 1995 / Fides et Ratio 1998 / Ut Unum Sint 1995 等）
- [ ] **保祿六世**：Humanae Vitae 1968 等 7 道通諭
- [ ] **若望二十三世**：Pacem in Terris 1963 / Mater et Magistra 1961
- [ ] **碧岳十二世**：Divino Afflante Spiritu 1943 / Munificentissimus Deus 1950（使徒憲令）/ Mystici Corporis 1943 等
- [ ] **碧岳十一世**：Quadragesimo Anno 1931 / Casti Connubii 1930 / Mit brennender Sorge 1937
- [ ] **良十三世**：Rerum Novarum 1891 ★ 起頭，88 道通諭中的 marquee 約 15 道
- [ ] **碧岳九世**：Ineffabilis Deus 1854（使徒憲令）/ Quanta Cura + Syllabus 1864
- [ ] **良十四世**（2025-）：等台灣主教團官方中譯發布後再 ingest
- [ ] **4-15c 早期教宗**：等 [[fathers-translation]] / Schaff NPNF Vol 12-13 中譯成熟 → Phase 5 回頭 ingest
