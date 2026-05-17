---
name: historical-borders-map
description: 「歷史國界地圖」工具集（/maps/historical-borders）— 6,853 個歷史政權從 -123,000 BCE 至今的政治國界演進地圖 + 國家資料庫列表。跨 53 個 historical-basemaps snapshots，Equal Earth 等積投影。資料層：historical-basemaps polygon + Wikidata SPARQL + 人工 STATE_DETAILS + Gemini batch 中文翻譯（2,420 條）+ rules-based 政權分類器（is_state，過濾部落／文化群）。Use when 補國家詳細資料、新增 SUPPLEMENT_ZH／STATE_DETAILS／sphere 對照、新增手譯／規則／snapshot、修地圖渲染、改列表過濾、調整政權分類標準（KNOWN_STATES / KNOWN_NON_STATES）、Gemini 補翻譯。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 歷史國界地圖 — 純政治國界 + 國家資料庫

> Live URL：http://localhost:3000/maps/historical-borders
> 首頁卡：[pages/maps/index.vue](../../../pages/maps/index.vue) 🗺️ 卡片
> 姊妹工具：[world-religions-map](../world-religions-map/SKILL.md)（文化圈著色版本）

純政治體呈現，**無文化圈著色** — 專門作為後續討論文化圈分類的圖層基礎。地圖／國家列表雙視圖切換。

---

## 三層資料來源

| 層 | 檔案 | 數量 | 用途 |
|---|---|---|---|
| A. 古國 polygon | `public/maps/historical-states.geojson` | **9,588 features (40 MB)** | 地圖上的古國邊界 polygon — 跨 53 snapshots |
| B. Sphere fill polygon | `public/maps/historical-sphere-fills.geojson` | **10,350 features (42 MB)** | 文化圈著色（由 world-religions-map 使用）— 跨 53 snapshots |
| C. 國家骨架（含現代涵蓋） | `public/maps/state-skeleton.json` | **2,949 條 (348 KB)** | 從 historical-states.geojson 抽出 unique names |
| D. Wikidata 主資料 | `public/maps/wikidata-states.json` | 4215 條 (~ 530 KB) | 中英文名、起始／結束年、所屬大陸、QID |
| E. 人工撰寫詳細 | `data/maps/historical-states-db.ts` (`STATE_DETAILS`) | **271 條（5 輪擴充）** | 朝代、首都、宗教、人口、面積、簡介 |
| E2. 朝代時間段標籤 | `data/maps/dynasty-labels.ts` (`DYNASTY_LABELS`) | **47 polygon × ~10 段 = ~480 段（含第三輪細分）** | 跨朝代 polygon 按年代切時期，標籤顯示「{朝代}（{國家}）」 |
| E3. polygon 年範圍修正 | `public/maps/polygon-year-overrides.json` | **11 條** | 收窄源資料過早 polygon（如 Hurrian -5000→-2500、Indus -4000→-3300）|
| E4. 細粒度 polygon（city-hull） | `public/maps/fine-polygons.geojson` | **18 polygons / 3 帝國** | 阿巴斯 6 + 伍麥亞 5 + 蒙古 7；已接入主圖，覆蓋粗 polygon |
| F. NE 50m coastline | `public/maps/ne_50m_coastline.geojson` | 1428 LineString | 海岸線（黑線） |
| G. NE 50m admin_0 | `public/maps/ne_50m_admin_0_countries.geojson` | 242 features | 陸地灰底 + **NAME_ZHT 中文國名（內建）** |
| H. Polygon 名譯本 | `public/maps/polygon-names-zh.json` | **2,420 條 (88 KB)** | Gemini batch 翻的 polygon name → 繁中 |
| I. Polygon 政權分類 | `public/maps/polygon-classifications.json` | **2,949 條** | rules-based: is_state + reason，過濾部落／文化群 |
| J. Realm/Sphere 自動推斷 | `public/maps/state-sphere-inference.json` | **360 條** | 由 modern_countries × country-sphere-timeline 推算 realm_id + sphere_id（confidence + sources）|

**Snapshot 來源**：[scripts/build_historical_layer.mjs](../../../scripts/build_historical_layer.mjs) 用 53 個 historical-basemaps snapshots：BCE 17 個（123000、10000、8000、5000、4000、3000、2000、1500、1000、700、500、400、323、300、200、100、1）+ CE 36 個（100、200、300、400、500、600、700、800、900、1000、1100、1200、1279、1300、1400、1492、1500、1530、1600、1650、1700、1715、1783、1800、1815、1880、1900、1914、1920、1930、1938、1945、1960、1994、2000、2010）。每 snapshot 的 `yearTo = 下個 snapshot 年 - 1`；最後一個（2010）`yearTo = 9999`。

**過濾策略**（多層）：
- **build 階段**：`historical-states.geojson`（給本工具）用 `NON_STATE_PATTERNS` blacklist 排除明顯非政體；`historical-sphere-fills.geojson`（給 world-religions-map）用 `STATE_NAMES` whitelist
- **runtime 階段**（前端 filter）：用 `polygon-classifications.json` 進一步過濾。**標準 v2（user-defined）**：
  - **舊大陸（歐亞非）**：至少酋邦 (chiefdom)／城邦 (city-state)／建立王權的遊牧帝國
  - **新大陸（美洲、澳洲、太平洋諸島）**：**只從「有文字民族的出現或入侵」開始算**。有文字本土文明（Maya 象形字／Aztec codex／Inca quipu）算；歐洲殖民後的所有殖民地／殖民國家算；殖民前無文字酋邦（Olmec/Toltec/Tarascan/Norte Chico/Cahokia/Mississippian/Anasazi/Iroquois Confederacy/Tu'i Tonga Empire/Hawaiian Kingdom 等）→ **排除**
  - 純 band/tribe／語族／考古文化群／古人類學名／狩獵採集者群 → 全排除

**政權分類器**（[scripts/classify_polygons.mjs](../../../scripts/classify_polygons.mjs)，純 rules-based）— 5 層判定：
1. **顯式 override**：`KNOWN_NON_STATES` (~80) / `KNOWN_STATES` (~400) / `STATE_DETAILS` keys
2. **`NON_STATE_PATTERNS` regex**：Hunter-Forager / *culture / *farmers / Tribe of / Reservation / -peoples / Indigenous / Mesolithic / Neolithic Farmers / pastoralis / nomad
3. **`POLITY_PATTERNS` regex**：Empire/Kingdom/Caliphate/Khanate/Sultanate/Dynasty/Republic/Confederation/Principality/Duchy/Emirate/Shogunate/League/Protectorate/Colony/Viceroyalty/Chiefdom/...; 殖民地 prefix `Portuguese|Spanish|French|British|Dutch|Soviet|...\s+[A-Z]`
4. **NE admin_0 對應**：在 NE 的國家英文名 set 內 → 是現代國家
5. **中文翻譯後綴**（看 polygon-names-zh.json）：含「王國/帝國/汗國/王朝/...」→ true；結尾「-人/-族/文化」→ false

預設保守 = false（疑似非政權）。

過濾效果（每年顯示的 polygon 數）：
| 年 | 全部 polygons | 過濾後政權 | 排除 |
|---|---|---|---|
| 1980 | 160 | **160** | 0 |
| 1900 | 222 | 213 | 9 (非洲部族) |
| 1700 | 584 | 102 | 482 (大量原住民／部落) |
| 1500 | 133 | 92 | 41 |
| **1492** | **1303** | **89** | **1214 (含全美洲殖民前部族／chiefdom — 只剩 Aztec / Maya)** |
| 500 | 70 | 27 | 43 |
| -2000 | 32 | 11 | 21 (新大陸全空、舊大陸古文明 11 個) |
| -8000 | 11 | **0** | 11 (全 hunter-gatherers) |

**Merge 邏輯**（[data/maps/historical-states-db.ts](../../../data/maps/historical-states-db.ts) `mergeStates()`）：
- 依英文名 normalized key dedupe
- skeleton + wikidata + STATE_DETAILS 三層合併
- 最終 **6853 個獨特國家**（2949 skeleton + 4215 wikidata - 交集）
- 已填詳細 41 個

---

## 翻譯系統：100% 中文覆蓋率

**4215/4215 國家全部有中文譯名。**累積進度：
| 階段 | 累計 | 來源 |
|---|---|---|
| 1 | 60.6% (2555) | Wikidata zh / zh-hant / zh-tw / zh-hk / zh-hans / zh-cn 變體 |
| 2 | 75.0% (3162) | 第一輪規則 + 手譯 ~400 條 |
| 3 | 81.7% (3443) | State/Principality/Shogunate 等 suffix |
| 4 | 91.7% (3865) | 第二輪手譯 ~170 條 |
| 5 | 93.5% (3941) | Canton/Chiefdom/Duke 等規則 |
| 6 | 99.8% (4206) | 第三輪手譯 ~280 條 |
| 7 | **100.0%** (4215) | 最後 9 條補完 |

### 規則翻譯（~250 條）

**Prefix → 後綴**（[scripts/translate_state_names.mjs](../../../scripts/translate_state_names.mjs) `PREFIX_DICT`）：
```
Kingdom of X     → X 王國
Empire of X      → X 帝國
Duchy of X       → X 公國
Grand Duchy of X → X 大公國
Principality of X → X 親王國
Republic of X    → X 共和國
Sultanate of X   → X 蘇丹國
Emirate of X     → X 酋長國
Caliphate of X   → X 哈里發
Khanate of X     → X 汗國
Beylik of X      → X 貝伊國
County of X      → X 伯國
Margraviate of X → X 邊伯國
Marquisate of X  → X 侯爵領
Landgraviate of X → X 方伯國
Lordship of X    → X 領主國
Bishopric of X   → X 主教區
Prince-Bishopric of X → X 親王主教區
Archbishopric of X    → X 大主教區
Free Imperial City of X → X 帝國自由市
Imperial City of X    → X 帝國城市
Imperial Abbey of X   → X 帝國修道院
Crown of X       → X 王冠
Tsardom of X     → X 沙皇國
Despotate of X   → X 專制國
Banate of X      → X 班國
Voivodeship of X → X 伏伊伏丁那
Khedivate of X   → X 赫迪夫國
Eyalet of X      → X 艾雅勒
Sanjak of X      → X 桑賈克
Vilayet of X     → X 維拉耶特
Pashalik of X    → X 帕夏轄區
Barony of X      → X 男爵領
Viscounty of X   → X 子爵領
Count(s) of X    → X 伯爵
Sheikhdom of X   → X 酋長國
Provisional government of X → X 臨時政府
Free State of X  → X 自由邦
Confederation of X → X 聯盟
United States of X → X 合眾國
United Provinces of X → X 聯合省
Federation of X  → X 聯邦
Democratic Republic of X → X 民主共和國
Socialist Republic of X → X 社會主義共和國
Soviet Republic of X → X 蘇維埃共和國
Islamic Republic of X → X 伊斯蘭共和國
Crown Colony of X → X 直屬殖民地
Protectorate of X → X 保護國
Taifa of X       → X 泰法王國（西班牙伊斯蘭時期小國）
Beylik of X      → X 貝伊國
Signoria of X    → X 領主國（義大利）
Canton of X      → X 坎頓
Chiefdom of X    → X 酋邦
Duke of X        → X 公爵
Commune of X     → X 公社
（共約 80 種）
```

**Prefix 保前置**（國名形容詞，[scripts/translate_state_names.mjs](../../../scripts/translate_state_names.mjs) `PREFIX_KEEP_FRONT`）：
```
Roman X      → 羅馬 X
Russian X    → 俄屬 X
Dutch X      → 荷屬 X
Portuguese X → 葡屬 X
Spanish X    → 西屬 X
French X     → 法屬 X
British X    → 英屬 X
Italian X    → 義屬 X
German X     → 德屬 X
Ottoman X    → 奧斯曼 X
Soviet X     → 蘇聯 X
Mughal X     → 蒙兀兒 X
Byzantine X  → 拜占庭 X
Imperial X   → 帝國 X
Ancient/Old X → 古 X
Eastern X    → 東 X
Western X    → 西 X
Upper X      → 上 X
Lower X      → 下 X
Great/Greater X → 大 X
Lesser X     → 小 X
First X      → 第一 X
Second X     → 第二 X
（共約 30 種）
```

**Suffix**：
```
X Kingdom    → X 王國
X Empire     → X 帝國
X Khanate    → X 汗國
X dynasty    → X 王朝
X State      → X 邦
X Principality → X 親王國
X Shogunate  → X 幕府
X Voivodeship → X 伏伊伏丁那
X Banate     → X 班國
X Despotate  → X 專制國
X Civilization → X 文明
X Culture    → X 文化
X League     → X 同盟
（共約 15 種）
```

### 人工翻譯（~880 條）

`MANUAL_TRANSLATIONS` 表分批撰寫，涵蓋：
- **古近東**：哈梯、米坦尼、犍陀羅、迦勒底、烏加里特、推羅、西頓、敘拉古、呂底亞、弗里吉亞、奇里乞亞、卡帕多西亞、亞蘭、腓尼基…
- **印度諸邦**：摩揭陀、注輦、毗奢耶那伽羅、孔雀王朝、貴霜帝國、巽伽王朝、波羅帝國、邁索爾王國、康提王國、康萊帕克、加德瓦爾…（含 60+ 王公邦轉寫）
- **中亞**：花剌子模、可薩、布哈拉汗國、希瓦汗國、浩罕汗國、準噶爾汗國、突厥汗國、瓦剌、卡濟庫穆赫、卡伊塔格…
- **伊斯蘭**：法蒂瑪、薩曼、薩法維、伽色尼、塞爾柱、伊兒汗國、馬木留克、阿尤布、阿穆瓦希德…
- **中世紀歐洲**：諾曼第公國、勃艮第公國、阿基坦公國、莫斯科大公國、立陶宛大公國、波蘭立陶宛聯邦、神聖羅馬帝國、東法蘭克、西法蘭克、條頓騎士團、各 Saxe-X 公國…
- **非洲**：阿克蘇姆、剛果王國、馬利帝國、桑海帝國、祖魯王國、奧約帝國、阿散蒂、達莫特、薩卡拉瓦、瓦索盧…
- **美洲**：印加帝國、阿茲特克、馬雅文明、莫切、查文、瓦里、蒂瓦納庫、托爾特克、薩波特克…
- **中國分裂期**：商、周、秦、漢、晉、隋、唐、宋、元、明、清各朝代與三國 / 南北朝 / 五代十國 / 北元 / 西夏 / 遼 / 金…
- **東南亞**：扶南、真臘、占婆、室利佛逝、滿者伯夷、大城、東吁、貢榜、塞卡拉布拉克、都郎巴望…
- **太平洋酋邦**：東加帝國、夏威夷王國、大溪地王國…
- **20 世紀短命邦**：薩伊、撒哈拉阿拉伯民主、巴伐利亞蘇維埃、的里雅斯特自由區、薩爾保護國…
- **殖民地**：荷屬東印度、英屬印度、法屬印度支那、葡屬澳門、義屬東非…

---

## HistoricalState schema

```ts
// 骨架（自動，來自 historical-basemaps geojson）
interface StateSkeleton {
  name_en: string
  earliest_from: number        // 最早出現年（天文年）
  latest_to: number            // 最晚結束年（9999 = 至今）
  modern_countries: string[]   // ISO_A3 list（從 sphere-fills 交集統計）
  snapshots: number[]          // 出現於哪些 snapshot 年份
}

// Wikidata 補資料
interface WikidataState {
  qid: string
  name_en: string
  name_zh: string | null
  inception_year: number | null
  dissolved_year: number | null
  continents: string[]
}

// 人工撰寫詳細（高品質）
interface StateDetail {
  name_zh?: string
  dynasties?: string[]                // 統治家族／朝代
  population_peak_wan?: number        // 巔峰人口（萬人）
  area_peak_wan_km2?: number          // 巔峰面積（萬 km²）
  capitals?: string[]                 // 主要首都
  religions?: string[]                // 主要宗教
  intro?: string                      // 簡介
  successors?: string[]
  predecessors?: string[]
  realm_id?: string                   // 對應 world-religions 的 realm
  sphere_id?: string                  // 對應 sphere
}

// 合併後
interface HistoricalState extends StateSkeleton, StateDetail {
  id: string                          // slug
  has_detail: boolean                 // STATE_DETAILS 是否填了
  has_polygon: boolean                // historical-states.geojson 是否有
  qid?: string                        // Wikidata
  continents?: string[]               // Wikidata 提供
  year_start: number | null           // earliest_from > inception_year
  year_end: number | null
}
```

---

## 元件結構

| 檔案 | 用途 |
|---|---|
| [pages/maps/historical-borders.vue](../../../pages/maps/historical-borders.vue) | 頁面 + 地圖／列表 toggle |
| [components/maps/HistoricalBordersMap.vue](../../../components/maps/HistoricalBordersMap.vue) | 地圖元件（500+ 行） |
| [components/maps/HistoricalStateList.vue](../../../components/maps/HistoricalStateList.vue) | 列表元件（搜尋、過濾、排序、分頁、彈窗）|
| [components/maps/TimeAxis.vue](../../../components/maps/TimeAxis.vue) | 時間軸（與 world-religions 共用） |
| [data/maps/historical-states-db.ts](../../../data/maps/historical-states-db.ts) | schema + STATE_DETAILS + mergeStates() |

### 地圖渲染（HistoricalBordersMap.vue）

**投影**：`geoEqualEarth` (Equal Earth, 2018) — **等積投影**，真實面積保留。視覺接近 Natural Earth 但不騙面積（高緯度不誇大）。同一投影也用在 `WorldThematicMap.vue`。要改換投影改 `import { geoEqualEarth } from 'd3-geo'` 那行 + `makeProjection()` 裡的 `geoEqualEarth()` 呼叫。

四層：
1. **海背景**：白
2. **陸地灰底**：modern admin_0，`fill='#D1D5DB'` 全 opacity
3. **古國 polygon**：filtered by currentYear（`year_from <= y <= year_to`）+ **`polygon-classifications.json` 政權過濾**，每國 **hash-based HSL 唯一色**
4. **海岸線**：NE coastline 黑線 0.6/transform.k
5. **國名標籤**：centroid + 防重疊 relax，**中文優先**。`nameZhOf()` 查序：
   1. STATE_DETAILS (41，最準)
   2. SUPPLEMENT_ZH (~80 條，HistoricalBordersMap.vue 內手譯)
   3. NE admin_0 NAME_ZHT/NAME_ZH (~315 個現代國家內建)
   4. wikidata-states.json (4117 條)
   5. **polygon-names-zh.json (2420 條，Gemini 翻譯)**
   6. fallback 英文

   **總覆蓋率：95.9%（2827/2949）**。剩下 ~120 個多為澳洲原住民部落名（Wiradjuri/Yolngu 等），Gemini quota 緊時跳過。

`colorForState(name)` 用名稱字串 hash 算 HSL，**同名穩定色**（一致性）。
點 polygon → `selectedState` 彈窗顯示中文 + 英文副標 + 有效年代。

**SUPPLEMENT_ZH 涵蓋**（在 [components/maps/HistoricalBordersMap.vue](../../../components/maps/HistoricalBordersMap.vue) 內）：
- 20 世紀關鍵國名：USSR/蘇聯、East Germany/東德、West Germany/西德、Czechoslovakia/捷克斯洛伐克、Yugoslavia/南斯拉夫、Empire of Japan/大日本帝國
- 殖民地／託管地：British Raj/英屬印度、French Indo-China/法屬印度支那、Dutch East Indies/荷屬東印度、各 French/British/Italian Somaliland、Mandatory Palestine 等
- NE admin_0 對不上的常見國家：Tanzania (United Republic of)/坦尚尼亞、Korea (DPRK/RoK)/北韓南韓、Gambia, The/甘比亞、Swaziland/史瓦帝尼、Hong Kong/香港、Western Sahara/西撒哈拉
- 加勒比、太平洋小國：Antigua and Barbuda、Saint Kitts and Nevis、Tonga、Samoa、Niue、American Samoa、Wallis and Futuna 等
- 仍可能未譯的：早期文化／部落／考古群名（Olmec／Chavin／Beaker culture／Dravidians 等）— 加進 STATE_DETAILS 即可

### 列表 UI（HistoricalStateList.vue）

工具列（右側統計排版）：
- **「顯示 N / 6,853 條目」** — 大字粗體主視覺
- 「政權 X」（amber-700）／「有 polygon X」（blue-600）／「人工詳細 41」（emerald-600） — 次要灰色文字

過濾：
- 搜尋（中英文）
- 界域（8 大界域，依 `realm_id`）
- 詳細（全部／已填／僅骨架）
- polygon（全部／有地圖／無 polygon）
- **政權 filter**（預設「僅政權（含酋邦）」／僅部落／文化群／不過濾）— 用 `polygon-classifications.json`，wikidata-only 條目（無 polygon 分類）若有 inception_year 視為政權

表格欄位：國名 / 年代 / 朝代統治 / 巔峰人口 / 巔峰面積 / 主要首都 / 現代涵蓋 / 界域

點國家 → 詳細彈窗（含 Wikidata QID 連結）

排序：依 `year_start` 或 `name_en`，asc/desc 切換

分頁：**50 條/頁**，~137 頁。分頁列含「⟪ 第一頁／← 上頁／第 X / Y 頁／下頁 →／最末頁 ⟫」

---

## 工具腳本（七個）

### 1. `scripts/generate_state_skeleton.mjs`
從 `historical-states.geojson` + `historical-sphere-fills.geojson` 抽 370 國骨架，輸出 `state-skeleton.json`。
- 輸入：geojson 檔
- 輸出：name_en / earliest_from / latest_to / modern_countries[] / snapshots[]
- 用 `state_name` 在 sphere-fills 統計每國覆蓋的現代國家 ISO

### 2. `scripts/fetch_wikidata_states.mjs`
從 Wikidata SPARQL 抓 4215 個歷史國家。
- 階段 1：分類查詢（Q3024240 historical country / Q28171280 ancient civilization / Q1763761 former kingdom / Q48349 empire）
- 階段 2：每 200 個 QID 一批查 zh 變體（zh-hant > zh-tw > zh-hk > zh > zh-hans > zh-cn）
- 避免單一查詢太大 timeout
- 輸出：`wikidata-states.json`

```bash
node scripts/fetch_wikidata_states.mjs   # ~3 分鐘
```

### 3. `scripts/translate_state_names.mjs`
補完缺中文的條目，寫回 `wikidata-states.json`。
- MANUAL_TRANSLATIONS 表（人工 880+ 條）
- PREFIX_DICT 規則（80+ 種）
- PREFIX_KEEP_FRONT 規則（30+ 種）
- SUFFIX_DICT 規則（15+ 種）

```bash
node scripts/translate_state_names.mjs   # 即時，幾秒鐘
```

### 4. `scripts/fetch_hbm_snapshots.mjs`
從 GitHub `aourednik/historical-basemaps` 下載所有 53 個 `world_*.geojson` 到 `C:/tmp/hbm-sample/`。已存在的 skip。
```bash
node scripts/fetch_hbm_snapshots.mjs   # ~2 分鐘
```

### 5. `scripts/classify_polygons.mjs`
**純 rules-based 政權分類器**，輸出 `public/maps/polygon-classifications.json`（2,949 條 entries 含 `is_state` + `reason`）。

對 historical-states.geojson 中每個 unique polygon name 判定 `is_state: bool`，標準（v2）：
- 舊大陸：至少酋邦／城邦／建立王權的遊牧帝國
- 新大陸（美洲／澳洲／太平洋）：只從「有文字民族出現或入侵」開始算（Maya/Aztec/Inca + 歐洲殖民後）

5 層判定見上。每加新國家／文化群到 KNOWN_STATES / KNOWN_NON_STATES 後重跑：
```bash
node scripts/classify_polygons.mjs   # 即時，~1 秒
```

要修「某 polygon 顯不顯示」：
- 想顯示 → 加進 `KNOWN_STATES` set
- 想不顯示 → 加進 `KNOWN_NON_STATES` set
- 順序：KNOWN_NON_STATES 先檢查（優先排除），KNOWN_STATES 次檢查

KNOWN_STATES (~400) / KNOWN_NON_STATES (~120 + 新大陸殖民前無文字文明全 list) 已包含豐富覆蓋。

### 6. `scripts/translate_polygon_names_gemini.py`
**Gemini batch 翻譯 polygon 名 → 繁體中文**，輸出 `public/maps/polygon-names-zh.json`。

流程：
1. 讀 `historical-states.geojson` 抽 unique polygon names (~2949)
2. 過濾掉已在 STATE_DETAILS / SUPPLEMENT_ZH / NE admin_0 NAME_ZHT / wikidata 的（~407）
3. 過濾掉已在 `polygon-names-zh.json` 的（incremental，跑第二次只翻新的）
4. 剩下的 batch 30~50 個一組丟給 Gemini 2.5 Flash
5. JSON 嚴格輸出格式（response_mime_type: application/json），temperature=0
6. 多 GEMINI_API_KEY 輪替過 free-tier quota (10 RPM, 250 RPD/key)
7. 每 batch 增量寫回 `polygon-names-zh.json`（crash-safe）

```bash
PYTHONIOENCODING=utf-8 python scripts/translate_polygon_names_gemini.py [--batch 50] [--rpm 10] [--limit N]
# ~6 分鐘完成 2540 個翻譯，加上 quota retry 可能 10-15 分鐘
```

Free tier `gemini-2.5-flash` 每 key 250 RPD，腳本內建 multi-key 輪替（GEMINI_API_KEY=k1,k2 或 GEMINI_API_KEY_2..._10）。

跑完後重啟 dev server，`HistoricalBordersMap.vue` 自動 fetch `polygon-names-zh.json` 並加入 `nameZhOf()` 查序最後一層。

### 7. `scripts/infer_state_realm_sphere.mjs`
**自動推斷 historical state 的 realm_id / sphere_id**，輸出 `public/maps/state-sphere-inference.json`。

對每個 state（skeleton + wikidata 合併後）：
1. 取 modern_countries[] 和 year_start（earliest_from 或 wikidata.inception_year）
2. 對每個 ISO_A3，查 `country-sphere-timeline.ts` 在 year_start 時的 sphere
3. Vote：最多票的 sphere 為勝出（confidence = top/total）
4. sphere → realm 用 `SPHERES` 表對照
5. 結果包含 `sources`（每個 ISO 投了哪個 sphere）+ `reason`

```bash
node scripts/infer_state_realm_sphere.mjs   # ~1 秒，輸出 ~360 條推斷
```

純文字 parser（regex 解 .ts 檔），無 ts-node/tsx 依賴。前端 `mergeStates(skeleton, wikidata, inference)` 第三個參數吃這份 JSON，當 `STATE_DETAILS` 沒填 realm 時自動補位並標 `has_inferred_sphere=true`，列表用紫色虛線 badge 與「推」字標示。

---

## 常見操作

### 加新國家詳細資料

在 [data/maps/historical-states-db.ts](../../../data/maps/historical-states-db.ts) 的 `STATE_DETAILS` 物件加：
```ts
'Ancient State Name (英文)': {
  name_zh: '中文名',
  dynasties: ['某王朝', '某王朝'],
  capitals: ['首都1', '首都2'],
  religions: ['宗教1'],
  population_peak_wan: 1000,         // 1000 萬人 = 一千萬
  area_peak_wan_km2: 50,             // 50 萬 km²
  intro: '簡介…',
  realm_id: 'central',                // 對應 world-religions 的 realm
  sphere_id: 'mesopotamian-levantine',
  successors: ['Successor State'],
  predecessors: ['Earlier State'],
},
```

Key 必須是 `historical-states.geojson` 中的 `properties.name` 完全一致。

### 加新手譯

編輯 [scripts/translate_state_names.mjs](../../../scripts/translate_state_names.mjs) `MANUAL_TRANSLATIONS` 表新增條目，然後跑：
```bash
node scripts/translate_state_names.mjs
```

### 加新規則模式

編輯 [scripts/translate_state_names.mjs](../../../scripts/translate_state_names.mjs)：
- `PREFIX_DICT`：地名移到前面 + 後綴（如 `'Sultanate of '` → `'蘇丹國'`）
- `PREFIX_KEEP_FRONT`：保留前綴位置（如 `'Roman '` → `'羅馬'`）
- `SUFFIX_DICT`：英文後綴對中文後綴（如 `' Kingdom'` → `'王國'`）

### 重抓 Wikidata（資料更新）

```bash
node scripts/fetch_wikidata_states.mjs
node scripts/translate_state_names.mjs
```

`fetch_wikidata_states.mjs` 會清掉舊資料，新版本可能新增／刪除條目。`translate_state_names.mjs` 補譯名再寫回。

### 重建 skeleton（polygon 變更時）

當 `historical-states.geojson` 或 `historical-sphere-fills.geojson` 變更（例如重跑 `build_historical_layer.mjs`）：
```bash
node scripts/generate_state_skeleton.mjs
```

### 完整重 build pipeline（全部資料層重生）

```bash
# 1. 抓 historical-basemaps 53 snapshots（已存在會 skip）
node scripts/fetch_hbm_snapshots.mjs

# 2. 重 build 兩個 geojson（~30 分鐘，CPU 重）
node scripts/build_historical_layer.mjs

# 3. 重抽 skeleton
node scripts/generate_state_skeleton.mjs

# 4. 重抓 wikidata（可選，~3 分鐘）
node scripts/fetch_wikidata_states.mjs
node scripts/translate_state_names.mjs

# 5. Gemini batch 翻 polygon names（~10-15 分鐘）
PYTHONIOENCODING=utf-8 python scripts/translate_polygon_names_gemini.py

# 6. 重新分類政權（~1 秒）
node scripts/classify_polygons.mjs
```

### 加新政權／排除某 polygon

編輯 [scripts/classify_polygons.mjs](../../../scripts/classify_polygons.mjs)：
- 想顯示 → 加進 `KNOWN_STATES`
- 想不顯示 → 加進 `KNOWN_NON_STATES`（會優先攔截）
- 跑 `node scripts/classify_polygons.mjs`，前端硬重整就生效

### 加新地圖標籤手譯（rules 抓不到的）

編輯 [components/maps/HistoricalBordersMap.vue](../../../components/maps/HistoricalBordersMap.vue) 的 `SUPPLEMENT_ZH` 物件，加 `'English Name': '中文名'`。HMR 即生效。

### 重跑 realm/sphere 自動推斷

任何時候 `country-sphere-timeline.ts` 或 skeleton 變了：
```bash
node scripts/infer_state_realm_sphere.mjs
```
覆寫 `public/maps/state-sphere-inference.json`；前端下次 mount 自動吃。

### 匯出列表資料

列表右上「⬇ 匯出」 → CSV 或 JSON，會匯出**當前 filter 結果**（檔名含計數與 filter tag）。CSV 加 BOM，Excel/Numbers 開啟中文不亂碼；list 欄位用 `|` 分隔。JSON 保留 realm_id / sphere_id / has_inferred_sphere 等所有欄位。

### 地圖 ↔ 列表雙向聯動

- 列表詳細彈窗點「🗺️ 在地圖查看」→ 自動切到地圖視圖、拉時間軸到 `year_start`、polygon 可見時開 selectedState 彈窗
- 地圖 polygon 點開後右上彈窗點「📋 在列表查看詳細」→ 自動切到列表並打開該國的詳細 modal

實作：page-level 管 `mapHighlight` / `listHighlight` ref，setTimeout(0) 賦值確保 watch 即使同名也重觸發。

### 時間軸動畫播放

TimeAxis 右上「▶ 播放」按鈕，速度可選「慢／普通／快」（2500/1200/500 ms / 格）。依 EPOCHS 逐 epoch 跳到 2026。播放中改速度即時生效。已到末端可再次按 ▶ 從 -4000 重播。

---

## 已完成（最新一輪：2026-05-17）

### ✅ A. STATE_DETAILS 第五輪擴充：177 → **271 條**（+94）

5 輪累積：46 → 78 → 135 → 177 → **271**。第 5 輪完成的 7 子類：

| 子類 | 內容 | 條目 |
|---|---|---|
| A1 印度土邦 | 錫金／克什米爾／拉賈斯坦／巴哈瓦爾布爾／特拉凡科爾／柯欽／奧德／邁索爾／博帕爾／海得拉巴／齋浦爾／烏代浦／印多爾／瓜廖爾／巴羅達／伯蒂亞拉／卡拉特／凱爾布林／曼尼普爾 | 19 |
| A2 神羅小邦 | 巴登／巴伐利亞／薩克森／黑森大公／黑森選帝侯／安哈特／漢諾威／符騰堡／梅克倫堡-S／-Strelitz／布倫瑞克／霍爾斯坦／拿騷／奧爾登堡／紹姆堡-利珀／利珀-德特摩德 | 16 |
| A3 太平洋 | 新喀里多尼亞／拉帕努伊／薩摩亞王國／諾魯託管地 | 4 |
| A4 19-20 世紀短命邦 | 新西班牙／秘魯／拉普拉塔總督轄區、巴西帝國、大哥倫比亞、滿洲國、汪精衛、巴伐利亞蘇維埃、的里雅斯特自由區、薩爾保護領、德州／加州／猶加敦共和國 | 16 |
| A5 阿拉伯 | 漢志／哈伊勒／停戰諸國（× 2）／馬斯喀特與阿曼／阿西爾／葉門宰德／葉門穆塔瓦基利亞／內志-漢志聯合王國 | 10 |
| A6 早期帝國 | 塞琉古／托勒密／巴克特里亞／希臘-巴克特里亞／貴霜諸侯／劉宋／北魏／北周／北齊／曹魏／東吳／蜀漢／吳越／南唐／高句麗 | 17 |
| A7 非洲 | 剛果王國／恩東戈／盧巴／隆達／阿散蒂／達荷美／布干達／盧安達王國／豐吉／薩伊／約魯巴地區／博爾努 | 12 |

### ✅ B. dynasty-labels 第三輪細分（+~50 段，47 polygon × ~10 段 = ~480 段）

| polygon | 細分內容 |
|---|---|
| United Kingdom | 殖民帝國分期（第二次帝國／印度直轄／瓜分非洲／戰間期帝國巔峰／蘇伊士危機／去殖民化潮／脫歐）|
| Ottoman Empire | 「停滯期」拆塞利姆 II／穆拉德 III／艾哈邁德 I／科普魯律家族；鬱金香時代與貝爾格勒和約 |
| Mughal Empire | 奧朗則布拆「北方統治／德干戰役」+ 蘇爾中斷／繼承內戰／阿富汗入侵 |
| Carolingian Empire | 查理曼倫巴底 774／薩克森 30 年戰 772-804／隆塞瓦勒 778／阿瓦爾 791-803 |
| Sultanate of Delhi | 5 王朝 → 14 段（巴勒班鎮蒙古／阿拉烏丁南征／圖格魯克遷都／帖木兒劫德里） |
| Inca Empire | 11 段（昌卡戰役／南北征／卡哈馬卡之囚／天花橫掃／比爾卡班巴亡） |
| Aztec Empire | 11 段（三方聯盟／悲傷之夜／特諾奇蒂特蘭陷落） |
| Mauryan / Gupta | 羯陵伽戰爭／海護王南征／塞犍陀笈多抗匈那 |

### ✅ C. Stage 1 City-Hull polygon：3 帝國 18 polygons 已接入主圖

- [scripts/build_city_hull_polygons.mjs](../../../scripts/build_city_hull_polygons.mjs)：CITIES 共享城市庫（~80 城）+ EMPIRES 配置
- 阿巴斯（6）+ 伍麥亞（5）+ 蒙古（7）→ [public/maps/fine-polygons.geojson](../../../public/maps/fine-polygons.geojson)（~5.5 KB）
- [HistoricalBordersMap.vue](../../../components/maps/HistoricalBordersMap.vue) runtime 抑制同名粗 polygon（StateEntry.isFine 標籤）
- 1 城 → 0.5° 方塊；2 城 → bbox；3+ → Graham scan convex hull

### ✅ D. polygon-year-overrides：源資料過早收窄

- [public/maps/polygon-year-overrides.json](../../../public/maps/polygon-year-overrides.json)（11 條）
- 修正 Hurrian -5000→-2500、Indus -4000→-3300、Elam -5000→-3200、Kerma/Minoan/Olmec/Norte Chico/Chavin/Xia/Canaan/Saba
- HistoricalBordersMap.vue runtime 載入並收窄 yearFrom/yearTo

---

## 待補項目（下個 session 接續）

### A. STATE_DETAILS 繼續擴充（目前 271 / 目標 350+）

第五輪後仍可擴充的 polygon（每個都有 polygon、未填 details）：

**A8. 馬德拉斯邦／南印度殘餘土邦**
- Madurai、Pudukkottai、Banganapalle、Sandur、Kalaikkurichi、Cooch Behar、Tripura、Sirohi、Jhalawar
- Ramnad、Tanjore（Tanjavur 馬拉塔分支）
- 西部沿岸：Mahe、Karikal、Yanam（法屬印度）

**A9. 神羅／義大利更小邦**
- 義大利更多：Mantua、Modena Reggio、Parma Piacenza（已有部分）、Urbino、Ferrara
- 神羅小邦：Reuss-Greiz、Reuss-Schleiz、Liechtenstein、Bremen、Hamburg、Lübeck（漢薩自由市）
- 瑞士各 Canton 早期：Uri、Schwyz、Unterwalden 三州盟誓 1291

**A10. 西非 + 中非更細**
- Wagadu（迦納帝國前身）、Takrur、Jolof、Cayor、Sine、Saloum
- Bambara／Segou、Massina Caliphate
- Sokoto Caliphate 各 emirate（Kano、Katsina、Zaria、Gobir、Bauchi）
- Lozi／Barotseland、Ovambo、Yeke、Kazembe

**A11. 美洲原住民有政權者**
- Powhatan Confederacy（17 世紀維吉尼亞）
- Iroquois Confederacy（如算政權）
- Cherokee Nation（19 世紀有憲法）
- Comanche Empire（18-19 世紀馬背帝國）
- Tarascan / Purépecha（已有 Olmec？檢查）

**A12. 東南亞補遺**
- Lan Xang（瀾滄王國）、Lan Na（蘭納）、Sukhothai
- Pegu、Mrauk-U（阿拉干王國）
- Sulu Sultanate、Maguindanao Sultanate、Aceh Sultanate
- Pagaruyung Kingdom（米南加保）

**A13. 中亞補遺**
- Khazar Khaganate（已有 Khazars？）、Cuman-Kipchak
- Volga Bulgaria、Pecheneg
- Tangut／西夏（檢查 Western Xia）

**操作流程**：每輪用 [scripts/audit_historical_borders.mjs](../../../scripts/audit_historical_borders.mjs) 列出剩餘高頻 polygon、根據 Wikipedia 寫條目；目標每條含 intro / capitals / religions / dynasties / realm_id / sphere_id。

**操作流程**：每輪用 [scripts/audit_historical_borders.mjs](../../../scripts/audit_historical_borders.mjs) 列出剩餘高頻 polygon、根據 Wikipedia 寫條目；目標每條含 intro / capitals / religions / dynasties / realm_id / sphere_id。

---

### B. dynasty-labels.ts 第三輪細分（已完成、目前 47 polygon × ~10 段 = ~480 段）

第三輪 (+~50 段) 已加：
- **United Kingdom**：殖民帝國分期（第二次帝國／印度直轄／瓜分非洲／戰間期帝國巔峰／蘇伊士危機／去殖民化潮／脫歐）
- **Ottoman Empire**：「停滯期」拆塞利姆二世／穆拉德三世／艾哈邁德一世／科普魯律家族，鬱金香時代與貝爾格勒和約
- **Mughal Empire**：奧朗則布拆「北方統治／德干戰役」（1658-80 vs 1680-1707）；蘇爾中斷期、繼承內戰、阿富汗入侵獨立段
- **Carolingian Empire**：查理曼倫巴底 774／薩克森 30 年戰爭／隆塞瓦勒 778／阿瓦爾 791-803 細節
- **Sultanate of Delhi**：5 王朝拆到 14 段（巴勒班鎮蒙古／阿拉烏丁南征／圖格魯克遷都／帖木兒劫德里）
- **Inca Empire**：卡哈馬卡之囚／天花橫掃／南北征細分 11 段
- **Aztec Empire**：三方聯盟單獨成段／悲傷之夜／特諾奇蒂特蘭陷落 11 段
- **Mauryan / Gupta**：羯陵伽戰爭單獨成段、海護王南征、塞犍陀笈多抗匈那

下一輪可考慮：
- **Roman Empire**：朱里亞-克勞狄／弗拉維／五賢君／軍人皇帝危機／戴克里先／君士坦丁／西半部崩潰
- **Tang Empire**：玄宗開元再拆早中晚／武則天周朝具體年
- **Habsburg Spain**：腓力二世具體（聖戰艦／勒班陀／英艦隊）
- **Russian Empire**：彼得大戰具體（波爾塔瓦／尼斯塔特）／葉卡捷琳娜瓜分波蘭

操作：直接編 [data/maps/dynasty-labels.ts](../../../data/maps/dynasty-labels.ts)，依 polygon name 查 Wikipedia「Territorial evolution / Timeline of X」。

---

### C. City-Hull polygon 擴展（已有 3 帝國，下一輪擴 6+）

**現況**已接入主圖（見「已完成」C 段）。下一輪可加：

1. **擴展更多帝國** — 在 [build_city_hull_polygons.mjs](../../../scripts/build_city_hull_polygons.mjs) 的 EMPIRES 加：
   - **羅馬帝國**：-200／-100／-30／0／100／150／200／300／395（西/東分裂）
   - **拜占庭帝國**：395／476／527（查士丁尼）／630／700／843／1025（巴西爾二世）／1204（十字軍）／1350／1453
   - **鄂圖曼帝國**：1326／1389／1453／1520（蘇萊曼前夕）／1566／1683（維也納）／1798／1878／1914
   - **唐帝國**：626／660／710／751（怛羅斯）／805／860／907
   - **元帝國**：1271／1279（南宋亡）／1300／1350（紅巾起義）
   - **清帝國**：1644／1662／1683（鄭氏亡）／1722（康熙終）／1759（乾隆十全武功）／1820／1860（北京條約）／1895／1911
2. **凹邊處理** — 當控制不連續（如阿巴斯 900 失埃及但保敘利亞），改用 alpha-shape 或一帝國同年拆多 polygon
3. **Gemini Vision 自動化** — 50+ 帝國時，從 Wikipedia「Territorial evolution of X」抓城市清單

**polygon_name 必須對齊 historical-states.geojson** — 跑前用以下檢查：
```bash
node -e "const fs=require('fs');const gj=JSON.parse(fs.readFileSync('public/maps/historical-states.geojson'));const ns=new Set(gj.features.map(f=>f.properties.name));console.log(ns.has('Tang Empire'))"
```

其他長期路徑：

**方案 2：CHGIS 整合（中國年解析度）**
- 哈佛 + 復旦的中國歷史 GIS，-2 BCE → 1911 CE 縣級資料
- 開放下載 Shapefile，整合進 historical-states.geojson 可補齊中國朝代年密度
- URL：https://sites.fas.harvard.edu/~chgis/

**方案 3：DARMC 整合（羅馬+中世紀歐洲）**
- 哈佛 DARMC（Digital Atlas of Roman and Medieval Civilizations）
- Shapefile 需註冊

---

### D. 其他低優先

1. **CHGIS 整合**（C 方案 2 同上）— 補中國朝代年密度
2. **與 world-religions-map 整合** — 此工具是 sphere 分類討論的底層，分類確定後可同步反向更新 world-religions 的 sphere-history
3. **OpenHistoricalMap 抓取阿巴斯等帝國 polygon**（被 Cloudflare 擋，需 browser-mode 解）
4. **polygon-year-overrides 擴充** — 已加 11 條；剩可加項目：Vinča / Cucuteni / Yangshao（中歐銅器文化非政體）、Mycenaean -1700 起、Phoenicia -1500 起、Etruria -900 起。要加新 override：直接編 [public/maps/polygon-year-overrides.json](../../../public/maps/polygon-year-overrides.json) 的 `overrides`，HMR 即生效。

---

## 已知限制

- **某些 polygon 與 Wikidata 的對應不完美** — Wikidata 用「Tang dynasty」，historical-basemaps 用「Tang Empire」，依英文名 normalized key dedupe 可能有少數 mismatch。匹配未上時各為一筆。
- **modern_countries 來自 sphere-fills 交集** — 部落／hunter-gatherer 標籤已排除（whitelisted），所以一些早期文化（如 Norte Chico、Dapenkeng）的 modern_countries 可能空。
- **column 9 之後的細小 Indian princely state** — 多為轉寫，準確度不高但已盡量按音譯。
- **Wikidata 資料品質依賴社群編輯** — 某些 inception_year 可能誤差（特別是傳說早期）。可能要交叉比對 historical-states.geojson 的 polygon 出現年份。
- **檔案大小** — wikidata-states.json (530KB) + state-skeleton.json (49KB) 都不大，但若加 STATE_DETAILS 到全部 4215 國家可能膨脹。建議只填重要的 200-500 個。

---

## 與 world-religions-map 的差別

| 工具 | URL | 主視覺 | 用途 |
|---|---|---|---|
| world-religions-map | /maps/world-religions | sphere 著色（8 realm × 30 sphere 配色） | 文化／宗教界域呈現 |
| **historical-borders-map** | **/maps/historical-borders** | 每國唯一色（hash HSL）+ 國家列表 | 純政治體呈現、資料庫查閱 |

兩者共用：
- TimeAxis 元件（時間軸）
- historical-states.geojson（古國 polygon）
- ne_50m_coastline.geojson（海岸線）
- ne_50m_admin_0_countries.geojson（現代國家輪廓）

historical-borders-map 額外用：
- wikidata-states.json（從 Wikidata 抽）
- state-skeleton.json（從 polygon 抽）
- STATE_DETAILS（人工撰寫）

---

## Recent commits

`f079cf3` city-hull 多帝國通用版 + 接入主圖：阿巴斯 6 / 伍麥亞 5 / 蒙古 7 = 18 polygons → fine-polygons.geojson；HistoricalBordersMap.vue 載入並抑制對應粗 polygon
`db7f443` STATE_DETAILS 177 → 271（+94 第五輪：印度土邦／神羅小邦／太平洋／20 世紀短命邦／阿拉伯／早期帝國／非洲）+ dynasty-labels 第三輪 + Stage 1 city-hull POC + polygon-year-overrides.json
`3ded3db` STATE_DETAILS 78 → 177（+99 條第二+三輪：太平洋／加勒比／拉美／歐洲／義大利城邦／中世紀伊斯蘭／中國北朝／朝鮮三國）
`9615360` STATE_DETAILS 46 → 78（+32 條：殖民／印度／東南亞／西非／衣索比亞／日韓／法德義西）
`37ff74b` dynasty-labels.ts 第二輪 — 葡西英荷殖民／西非／印度／東南亞／美洲（+22 polygon × ~130 段）
`0d6101a` dynasty-labels.ts 大擴充 — 戰爭/擴張/分裂期細到 5-30 年（30 polygon × ~300 段）
`3a4bc93` label dedupe + 朝代標籤（同名 polygon 去重，跨朝代顯示「{朝代}（{國家}）」）
`0bc5faa` realm/sphere 自動推斷 + 雙向聯動 + 匯出 CSV/JSON + 時間軸動畫播放
`a0080cb` 政權標準 v2 — 新大陸從文字／殖民開始算
`5c10c98` 政權標準分類器（rules-based）— 排除部落／文化群／hunter-gatherer
`56722b1` polygon 名 95.9% 中文化 (Gemini batch) + 改 Equal Earth 等積投影
`abf4d79` 補齊 53 個 historical-basemaps snapshots，修 1980 等近代年份
`967e837` 地圖標籤中文化 + 列表工具列強化
`a8a26e6` 中文譯名 100% 完成（4215/4215，wikidata 名）
`4ae5aff` 翻譯 82% → 93.5%（規則 + 270 手譯）
`c7182a3` 翻譯 60% → 82%（規則 + 400 手譯）
`8719571` 接 Wikidata SPARQL，370 → 4424
`fe80628` 歷史國家資料庫 — 370 骨架 + 41 詳細 + 列表 UI
`f0115a1` 新增「歷史國界地圖」工具 /maps/historical-borders
