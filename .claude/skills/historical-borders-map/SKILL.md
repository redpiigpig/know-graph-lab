---
name: historical-borders-map
description: 「歷史國界地圖」工具集（/maps/historical-borders）— 6,853 個歷史政權從 -123,000 BCE 至今的政治國界演進地圖 + 國家資料庫列表。跨 53 個 historical-basemaps snapshots，Equal Earth 等積投影。資料層：historical-basemaps polygon + Wikidata SPARQL + 人工 STATE_DETAILS + Gemini batch 中文翻譯（2,420 條）+ rules-based 政權分類器（is_state，過濾部落／文化群）+ city-hull fine polygons（**279 polygons / 54 帝國** — 中東／中國／地中海／古波斯／古印度／神羅／美洲）+ polygon-year-overrides（43 條收窄源資料年代）。Use when 補國家詳細資料、新增 SUPPLEMENT_ZH／STATE_DETAILS／sphere 對照、新增手譯／規則／snapshot、修地圖渲染、改列表過濾、調整政權分類標準（KNOWN_STATES / KNOWN_NON_STATES）、Gemini 補翻譯、加新帝國 fine polygons。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

> ⚠️ **d3-geo 球面 winding 反向陷阱（已踩過）**：d3-geoEqualEarth／geoArea／geoCentroid 用**球面**慣例：**地理座標 CW 環 = 內部小區域，CCW = 補集（整個球面減該區）**。這與 RFC 7946 GeoJSON spec 相反。任何手寫 polygon 或 Graham 凸包（標準輸出數學 CCW）→ **必須 reverse 成 CW**，否則 `geoCentroid` 回傳對蹠點、`geoPath` 渲染出「世界輪廓 + 小洞」=全圖被填一色。`scripts/build_city_hull_polygons.mjs` 已內建 `.reverse()`，新加 polygon 一定要驗證 geoArea < 2π。

> 🏔️ **city-hull fine polygons 的本質限制**：用 Graham 凸包連城市點 → 是**幾何凸多邊形**，不沿海岸線、會切過海（如蒙兀兒 Kabul→Dhaka 直線穿孟加拉灣）。HistoricalBordersMap.vue 已加 `<clipPath id="land-clip">` 用 NE admin_0 把 state polygons 裁到現代陸地，海洋部分自動消失。長期最正解仍是改用實際邊界資料（OpenHistoricalMap、DARMC），但目前 OHM 對古近東／古印度／前哥倫布美洲覆蓋率近零（11 個我加的帝國裡 7 個 0 polygon），所以 land-clip 是當前最佳折衷。

> 🧹 **任務結束清 c:/tmp**：地圖任務常產 `historical-borders-XXX.png` 等截圖到 `/c/tmp/`，session 尾段要刪。保留 `/c/tmp/hbm-sample/`（53 snapshots，重抓 ~2 分鐘）。詳見 [[feedback-tmp-cleanup]]。

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
| E. 人工撰寫詳細 | `data/maps/historical-states-db.ts` (`STATE_DETAILS`) | **277 條（5 輪 + 中國諸侯）** | 朝代、首都、宗教、人口、面積、簡介 |
| E2. 朝代時間段標籤 | `data/maps/dynasty-labels.ts` (`DYNASTY_LABELS`) | **55 polygon × ~10 段** | 跨朝代 polygon 按年代切時期；dynastyLabelAt() 同名簡化 + 空 dynasty_zh 處理 |
| E3. polygon 年範圍修正 | `public/maps/polygon-year-overrides.json` | **43 條** | 收窄源資料錯誤年代（Sui 619、Tang 907、Yuan 1271-1368、Sinic 限商朝期、Wu 春秋吳國 -900~-473、Achaemenid -550~-330、Sasanian 224~651、Maurya -322~-185、Aztec 1428~1521、Inca 1438~1533、HRE 962~1806 等）|
| E4. 細粒度 polygon（city-hull） | `public/maps/fine-polygons.geojson` | **279 polygons / 54 帝國** | 中東 18（阿巴斯／伍麥亞／蒙古）+ 中國 135（商周秦漢三國晉南北朝隋唐五代十國北南宋遼金西夏西遼元明清）+ 地中海 36（羅馬／拜占庭／鄂圖曼）+ **古波斯 30（阿契美尼德／帕提亞早期＋極盛／薩珊）+ 古印度 35（孔雀／笈多／德里蘇丹／蒙兀兒）+ 神羅 13（962-1806）+ 美洲 13（阿茲特克／印加）**|
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

**4215/4215 國家全部有中文譯名**。所有規則／手譯在 [scripts/translate_state_names.mjs](../../../scripts/translate_state_names.mjs)：
- `PREFIX_DICT`（~80 種）：Kingdom/Empire/Duchy/Sultanate/Khanate/Caliphate/Republic/Principality… → X 王國 / X 帝國 / …
- `PREFIX_KEEP_FRONT`（~30 種）：Roman/Russian/Dutch/Portuguese/Spanish/French/British/Italian/Ottoman/Soviet/Mughal/Byzantine/Imperial/Ancient/Eastern/Western/Upper/Lower/Great/Lesser… → 保留位置 + 國名
- `SUFFIX_DICT`（~15 種）：X Kingdom / X Empire / X Khanate / X dynasty / X State / …
- `MANUAL_TRANSLATIONS`（~880 條）：古近東／印度諸邦／中亞／伊斯蘭／中世紀歐洲／非洲／美洲／中國分裂期／東南亞／太平洋酋邦／20 世紀短命邦／殖民地

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

## 已完成（最新一輪：2026-05-18）

### ✅ G. 古印度／古波斯／神羅／阿茲特克／印加 大塊區域 fine polygons（54 → fine 194 → **279**）

**目標**：源 historical-basemaps 對這些區域 polygon 不全或年代錯：
- 阿契美尼德源只 -500~-324（漏 -550~-501 居魯士滅米底＋滅巴比倫＋滅埃及；漏 -323~-330）
- 帕提亞源 'Parthia' -200~-2 + 'Parthian Empire' -1~399，後者過寬到薩珊期
- 薩珊源只 500~799，漏掉 224~499 早期 + 651 後伊斯蘭征服期過晚
- 孔雀源 -300~-2，末期 polygon 過晚（Maurya 實 -322~-185）
- 笈多源 300~599 部分過寬
- 德里蘇丹源 1200~1529（過寬到 Mughal 期 1530）
- 蒙兀兒源 1530~1782（漏 1526 建國，漏 1782~1857）
- 神羅源 1000~1782（漏 962~999 鄂圖一世時期、漏 1782~1806 解體前）
- 阿茲特克源 **只 1500~1529 一格** — 完全沒有 1428 三方聯盟成立以來的歷史擴張
- 印加源 1500~1649（1500 起算過晚，且 1533 已亡卻畫到 1649）

**做法**：city-hull 法 + polygon-year-overrides 雙管齊下。fine 從 194 → **279**（+85 polygons，54 → 11 帝國）：

| 帝國 | fine keyframes 數 | 涵蓋年代與事件 |
|---|---|---|
| 阿契美尼德 | 9 | -550 居魯士 / -546 滅呂底亞 / -539 滅巴比倫 / -525 岡比西斯滅埃及 / -518 取印度河 / -486 大流士末（極盛）/ -404 埃及叛離 / -343 復征埃及 / -334 亞歷山大東征前 |
| 帕提亞早期 | 3 | -247 阿薩息斯建國 / -209 安條克三世討伐 / -171 米特里達梯一世擴張 |
| 帕提亞極盛 | 9 | -129 取美索不達米亞 / -69 失亞美尼亞 / -53 卡萊大勝 / 1 奧古斯都和議 / 63 亞美尼亞共管 / 117 圖拉真攻泰西封 / 165 羅馬再侵 / 198 塞普蒂米烏斯洗劫 / 224 亡於薩珊 |
| 薩珊 | 9 | 224 Ardashir 建國 / 260 Shapur 擒瓦勒良 / 309 Shapur II / 387 與羅馬瓜分亞美尼亞 / 484 Peroz 死於匈那 / 531 Khosrow I 極盛 / 614 取耶路撒冷 / 628 希拉克略反攻 / 651 亡於阿拉伯 |
| 孔雀 | 6 | -322 旃陀羅笈多 / -305 戰勝塞琉古 / -268 阿育王即位 / -260 羯陵伽戰役（極盛）/ -232 阿育王崩 / -200 衰落 |
| 笈多 | 6 | 320 旃陀羅笈多一世 / 350 海護王 / 380 旃陀羅笈多二世（極盛）/ 415 鳩摩羅笈多 / 480 匈那入侵 / 530 末期分裂 |
| 德里蘇丹國 | 9 | 1206 奴隸王朝 / 1236 伊勒圖什密 / 1296 阿拉烏丁哈勒吉 / 1320 圖格魯克 / 1330 遷都德瓦吉里（極盛）/ 1351 退守北印 / 1398 帖木兒劫德里 / 1414 賽義德 / 1500 洛迪 |
| 蒙兀兒 | 8 | 1526 巴布爾建國 / 1540 蘇爾中斷 / 1556 阿克巴復興 / 1576 併孟加拉 / 1605 阿克巴崩 / 1659 奧朗則布 / 1687 滅戈爾康達 / 1700 暮年（含整個次大陸）|
| 神聖羅馬帝國 | 13 | 962 鄂圖一世加冕 / 1024 薩利安 / 1077 卡諾莎之辱 / 1155 巴巴羅薩 / 1250 大空位 / 1356 金璽詔書 / 1453 哈布斯堡 / 1556 查理五世退位 / 1648 西發里亞 / 1681 法併斯特拉斯堡 / 1740 瑪麗亞特蕾莎 / 1789 法革命前夕 / 1803 帝國代表決議 |
| 阿茲特克 | 6 | 1428 三方聯盟成立 / 1440 蒙特蘇馬一世擴張 / 1469 阿薩亞卡特 / 1486 阿維索托（南擴 Soconusco）/ 1502 蒙特蘇馬二世（極盛）/ 1519 科爾特斯登陸 |
| 印加 | 7 | 1438 帕查庫特克擊敗昌卡 / 1463 征服 Chimu / 1471 圖帕克‧印加 / 1493 瓦伊納‧卡帕克即位 / 1525 死於天花前極盛 / 1532 皮薩羅擒阿塔瓦爾帕 / 1533 印加亡 |

**新增 ~85 個歷史地點 lat/lon**（CITIES 表 ~220 → ~305）：
- 古波斯：Persepolis／Pasargadae／Susa／Babylon／Memphis／Pelusium／Sidon／Behistun／Halicarnassus／Ctesiphon／Hatra／Nisibis／Bishapur／Gundeshapur／Gor／Estakhr／Taxila
- 古印度：Pataliputra／Ujjain／Mathura／Sanchi／Kalinga／Bharuch／Sopara／Vidisha／Kannauj／Vallabhi／Pundravardhana／Tamralipti／Devagiri／Lakhnauti／Madurai／Surat／Hyderabad／Dhaka／Kandahar／Ahmedabad／Bijapur／Golconda／Sind／Agra／Ajmer
- 神羅：Aachen／Frankfurt／Nuremberg／Regensburg／Augsburg／Prague／Munich／Strasbourg／Hamburg／Bremen／Lubeck／Magdeburg／Worms／Speyer／Brussels／Utrecht／Basel／Bern／Zurich／Florence／Venice／Genoa／Bologna／Innsbruck／Salzburg／Dresden／Leipzig／Pavia／Verona／Trento／Antwerp
- 中美洲：Tenochtitlan／Texcoco／Tlacopan／Cholula／Tlaxcala／Cempoala／Xochimilco／Tula／Tehuantepec／Oaxaca／Soconusco／Tuxpan／Cuetlaxtla
- 安第斯：Cuzco／Quito／Cajamarca／Pachacamac／Tomebamba／ChanChan／Vilcabamba／Mendoza／Talca／Santiago／Trujillo／Arequipa／Potosi／LaPaz／Sucre／Huancayo／Tucuman／Pasto

**polygon-year-overrides 30 → 43 條**（+13）：
- Achaemenid -550~-330、Parthia -247~-130（拆早期）、Parthian Empire -129~224（拆極盛）、Sasanian 224~651、Mauryan -322~-185、Gupta 320~550、Sultanate of Delhi 1206~1526、Mughal 1526~1857、Holy Roman 962~1806、Aztec 1428~1521、Inca 1438~1533
- Mexihcah (Triple Alliance) 隱藏（由 fine Aztec 統一處理）
- Sasanian dependencies 隱藏（與 fine Sasanian Empire 重疊）

**name_zh 來源確認**：所有 11 帝國 STATE_DETAILS 都已有 name_zh（阿契美尼德波斯／帕提亞／薩珊波斯／孔雀王朝／笈多帝國／德里蘇丹國／蒙兀兒帝國／神聖羅馬帝國／阿茲特克／印加帝國），fine polygons 用簡稱（阿契美尼德／帕提亞／薩珊／孔雀／笈多／德里蘇丹國／蒙兀兒／神聖羅馬／阿茲特克／印加），HMR 即透過 nameZhOf() 自動套上 STATE_DETAILS 名稱。

---

### ✅ 過往輪次摘要

| 主題 | 結果 | 註 |
|---|---|---|
| 中國朝代 fine polygons | 135 polygons（商→清）；polygon-year-overrides 修源資料 13 條（Sinic/Zhoa/Wu/Sui/Tang/Han/Jin/Yuan/Ming/Manchu/Song/Liao/Mongol/Qin/Tibetan/Gokturk）；CITIES +100 古都；事件級 keyframe 設計（-121 河西、668 滅高麗、1689 尼布楚等） |
| 中東／地中海 fine polygons | 阿巴斯 6 / 伍麥亞 5 / 蒙古 7 / 羅馬 10 / 拜占庭 13 / 鄂圖曼 13 = 54 polygons |
| STATE_DETAILS 五輪累積 | 271 條（46→78→135→177→271）；含印度土邦／神羅小邦／太平洋／20 世紀短命邦／阿拉伯／早期帝國／非洲 |
| dynasty-labels.ts | 47 polygon × ~10 段 = ~480 段；含 UK 殖民分期／Ottoman 停滯期／Mughal 奧朗則布拆／Carolingian／Delhi 5 王朝 14 段／Inca 11 段／Aztec 11 段 |
| 國名標籤清潔（[[feedback-map-label-clean-country-name]]）| dynasty_zh +311 條剝括號（[scripts/clean_dynasty_labels.mjs](../../../scripts/clean_dynasty_labels.mjs)）；STATE_DETAILS.name_zh +14 條剝括號；dynastyLabelAt() 重寫 |
| 翻譯系統 | wikidata 4215/4215 100% 中文；polygon-names-zh.json 2,420 條 Gemini batch |
| 政權分類器 | KNOWN_STATES ~400 / KNOWN_NON_STATES ~120；新大陸僅文字文明＋殖民後算政權 |

**設計原則：事件級 keyframe 而非機械 10 年** — 兩個 keyframe 間 polygon 不變；用實際領土變動的歷史事件年補 keyframe，比機械式採樣更準更省。

---

## 待補項目

### A. STATE_DETAILS 繼續擴充（271 → 目標 350+）

剩餘高頻 polygon（未填 details）：
- 南印度殘餘土邦：Madurai／Pudukkottai／Banganapalle／Cooch Behar／Tripura／Sirohi／Jhalawar／Ramnad／Tanjore；法屬 Mahe／Karikal／Yanam
- 神羅／義大利小邦：Mantua／Modena Reggio／Urbino／Ferrara；Reuss-Greiz／Reuss-Schleiz／Liechtenstein；瑞士 Uri／Schwyz／Unterwalden（1291 盟誓）
- 西非／中非：Wagadu／Takrur／Jolof／Cayor／Sine／Saloum／Bambara／Segou／Massina；Sokoto 各 emirate（Kano／Katsina／Zaria／Gobir／Bauchi）；Lozi／Ovambo／Kazembe
- 美洲原住民有政權者：Powhatan／Cherokee Nation／Comanche Empire／Tarascan
- 東南亞補遺：Lan Xang／Lan Na／Sukhothai／Pegu／Mrauk-U／Sulu／Maguindanao／Aceh／Pagaruyung
- 中亞補遺：Khazar Khaganate／Cuman-Kipchak／Volga Bulgaria／Pecheneg

操作：[scripts/audit_historical_borders.mjs](../../../scripts/audit_historical_borders.mjs) 列剩餘高頻 polygon → Wikipedia 寫條目（intro / capitals / religions / dynasties / realm_id / sphere_id）。

### B. dynasty-labels.ts 下一輪候選

- Roman Empire：朱里亞-克勞狄／弗拉維／五賢君／軍人皇帝危機／戴克里先／君士坦丁／西半部崩潰
- Tang Empire：玄宗開元再拆早中晚／武則天周朝具體年
- Habsburg Spain：腓力二世具體（聖戰艦／勒班陀／英艦隊）
- Russian Empire：彼得大戰具體（波爾塔瓦／尼斯塔特）／葉卡捷琳娜瓜分波蘭

### C. City-Hull fine polygons 下一輪

- 中世紀俄國／立陶宛大公國（莫斯科崛起 1300-1547；立陶宛-波蘭聯邦 1569）
- 東南亞大邦（高棉／大城／東吁／滿者伯夷）
- 西非帝國（馬利／桑海／加奈姆-博爾努）
- 凹邊處理：控制不連續時用 alpha-shape 或同年拆多 polygon
- Gemini Vision 自動化：從 Wikipedia「Territorial evolution of X」自動抓城市清單

polygon_name 對齊檢查：
```bash
node -e "const fs=require('fs');const gj=JSON.parse(fs.readFileSync('public/maps/historical-states.geojson'));const ns=new Set(gj.features.map(f=>f.properties.name));console.log(ns.has('Tang Empire'))"
```

### D. 長期路徑

- CHGIS 整合：哈佛+復旦中國歷史 GIS，-2 BCE→1911 CE 縣級資料 https://sites.fas.harvard.edu/~chgis/
- DARMC 整合：哈佛 Digital Atlas of Roman and Medieval Civilizations；Shapefile 需註冊
- 與 world-religions-map 整合：分類確定後反向更新 world-religions 的 sphere-history
- polygon-year-overrides 擴充：Vinča／Cucuteni／Yangshao（中歐銅器文化）、Mycenaean -1700 起、Phoenicia -1500 起、Etruria -900 起

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

最新：古印度／古波斯／神羅／阿茲特克／印加 fine polygons（fine 194 → 279 / 43 → 54 帝國；polygon-year-overrides 30 → 43）

舊輪次見 `git log -- public/maps/fine-polygons.geojson scripts/build_city_hull_polygons.mjs data/maps/historical-states-db.ts`：
- 中國朝代徹底校正（商→清 135 polygons，事件級 keyframe；polygon-year-overrides 修源 13 條）
- 地中海三大帝國（羅馬／拜占庭／鄂圖曼 36 polygons）
- STATE_DETAILS 五輪累積 46→271；dynasty-labels.ts 三輪累積 ~480 段
- 國名標籤保持乾淨（dynasty_zh 剝括號 311 條）
- realm/sphere 自動推斷 + 雙向聯動 + 匯出 + 時間軸動畫
- 翻譯 100% 覆蓋 + Equal Earth 等積投影 + 53 snapshots 補齊近代
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
