---
name: historical-borders-map
description: 「歷史國界地圖」工具集（/maps/historical-borders）— 4215 個歷史國家從 4000 BCE 至今的政治國界演進地圖 + 國家資料庫列表。記錄三層資料源（historical-basemaps + Wikidata SPARQL + 人工 STATE_DETAILS）、翻譯系統（規則 + 880+ 手譯）、列表 UI、地圖渲染。Use when 補國家詳細資料、增加新 sphere/realm 對照、新增手譯、修地圖渲染、改列表過濾、Wikidata 重抓、加新 prefix/suffix 翻譯規則。
---

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
| E. 人工撰寫詳細 | `data/maps/historical-states-db.ts` (`STATE_DETAILS`) | 46 條（41 匹配） | 朝代、首都、宗教、人口、面積、簡介 |
| F. NE 50m coastline | `public/maps/ne_50m_coastline.geojson` | 1428 LineString | 海岸線（黑線） |
| G. NE 50m admin_0 | `public/maps/ne_50m_admin_0_countries.geojson` | 242 features | 陸地灰底 + **NAME_ZHT 中文國名（內建）** |
| H. Polygon 名譯本 | `public/maps/polygon-names-zh.json` | **2,420 條 (88 KB)** | Gemini batch 翻的 polygon name → 繁中 |

**Snapshot 來源**：[scripts/build_historical_layer.mjs](../../../scripts/build_historical_layer.mjs) 用 53 個 historical-basemaps snapshots：BCE 17 個（123000、10000、8000、5000、4000、3000、2000、1500、1000、700、500、400、323、300、200、100、1）+ CE 36 個（100、200、300、400、500、600、700、800、900、1000、1100、1200、1279、1300、1400、1492、1500、1530、1600、1650、1700、1715、1783、1800、1815、1880、1900、1914、1920、1930、1938、1945、1960、1994、2000、2010）。每 snapshot 的 `yearTo = 下個 snapshot 年 - 1`；最後一個（2010）`yearTo = 9999`。

**過濾策略**（雙軌）：
- `historical-states.geojson`（給本工具）：用 `NON_STATE_PATTERNS` blacklist 排除 hunter-gatherer/culture/tribe/nomad/farmers — 其他全收
- `historical-sphere-fills.geojson`（給 world-religions-map）：用 `STATE_NAMES` whitelist（240+ 政體名）保持原有切分

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

四層：
1. **海背景**：白
2. **陸地灰底**：modern admin_0，`fill='#D1D5DB'` 全 opacity
3. **古國 polygon**：filtered by currentYear（`year_from <= y <= year_to`），每國 **hash-based HSL 唯一色**
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
- **「顯示 N / 6,853 國」** — 大字粗體主視覺
- 「有 polygon X」「人工詳細 41」 — 次要灰色文字（避免被誤讀為總數）

過濾：搜尋（中英文）／界域（8 大界域，依 `realm_id`）／詳細（全部／已填／僅骨架）／polygon（全部／有地圖／無 polygon）

表格欄位：國名 / 年代 / 朝代統治 / 巔峰人口 / 巔峰面積 / 主要首都 / 現代涵蓋 / 界域

點國家 → 詳細彈窗（含 Wikidata QID 連結）

排序：依 `year_start` 或 `name_en`，asc/desc 切換

分頁：**50 條/頁**，~137 頁。分頁列含「⟪ 第一頁／← 上頁／第 X / Y 頁／下頁 →／最末頁 ⟫」

---

## 三個工具腳本

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

### 5. `scripts/translate_polygon_names_gemini.py`
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

---

## 待補項目（低優先）

1. **STATE_DETAILS 從 41 → 200+** — 目前只覆蓋最重要的 41 個（蘇美、阿卡德、埃及各朝、亞述、巴比倫、波斯、漢、唐、宋、元、明、清、奧斯曼、阿巴斯、馬木留克等）。可手填更多：
   - 拜占庭、薩珊、塞琉古、托勒密
   - 中世紀法蘭克／哈布斯堡／葡萄牙
   - 印度諸朝代（笈多、戒日、朱羅）
   - 東南亞王朝（吳哥、蒲甘、大城）
   - 非洲帝國（馬利、桑海、阿散蒂、辛巴威）
   - 美洲（特奧蒂瓦坎、托爾特克、奇穆）

2. **realm_id / sphere_id 自動推斷** — 從 modern_countries 對應到 sphere（透過 [country-sphere-timeline](../../../data/maps/country-sphere-timeline.ts) 查 inception_year 時的 sphere）。減輕手填負擔。

3. **地圖 + 列表雙向聯動** — 列表點國家可直接拉時間軸到該國年代並標示在地圖；地圖點 polygon 可跳到列表對應條目。

4. **匯出功能** — 列表能匯出 CSV／JSON 便於離線研究。

5. **時間軸動畫** — 地圖加「播放」按鈕，自動 -4000 → 2026 動畫演進。

6. **與 world-religions-map 整合** — 此工具是 sphere 分類討論的底層，分類確定後可同步反向更新 world-religions 的 sphere-history。

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

`a8a26e6` 中文譯名 100% 完成（4215/4215）
`4ae5aff` 翻譯 82% → 93.5%（規則 + 270 手譯）
`c7182a3` 翻譯 60% → 82%（規則 + 400 手譯）
`8719571` 接 Wikidata SPARQL，370 → 4424
`fe80628` 歷史國家資料庫 — 370 骨架 + 41 詳細 + 列表 UI
`f0115a1` 新增「歷史國界地圖」工具 /maps/historical-borders
