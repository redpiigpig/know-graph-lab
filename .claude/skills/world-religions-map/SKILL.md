---
name: world-religions-map
description: 「全球八大人文宗教界域」主題地圖工具集（/maps/world-religions）— 8 大界域 × 30 文化圈 × ~150 國家。記錄資料層（admin_0 / admin_1 50m / admin_1 10m / GADM admin_2 四層次）、配色系統、編輯模式、邊界切分邏輯。Use when 加新國家／文化圈／sphere/admin 細分；改配色；標籤位置調整；修 NE GeoJSON 對照 bug。
---

# 全球八大人文宗教界域 — 主題地圖

> 來源資料：根目錄 `全球八大人文宗教界域.docx`（手稿 50 段）。
> Live URL：http://localhost:3000/maps/world-religions
> 首頁卡：[pages/index.vue](../../../pages/index.vue) 「🗺️ 地圖繪製」

---

## 架構：四層 GeoJSON 疊加渲染

地圖由 4 個 GeoJSON 層疊加，越後面繪製越在上層（顯色覆蓋下層）：

| 層 | 檔案 | features | 內容 |
|---|---|---|---|
| 1️⃣ admin_0 | `public/maps/ne_50m_admin_0_countries.geojson` | 242 | NE 50m 國家邊界（除去 ATA + COUNTRIES_USING_ADMIN1 名單） |
| 2️⃣ admin_1 50m | `public/maps/ne_50m_admin_1_subset.geojson` | 178 | NE 50m 省／州，僅 CHN/RUS/USA/CAN |
| 3️⃣ admin_1 10m | `public/maps/ne_10m_admin_1_extra.geojson` | 161 | NE 10m 省／州，LBY/AFG/UKR/SDN/ETH/NGA/GHA + FR 5 個海外省 |
| 4️⃣ admin_2 GADM | `public/maps/cn_tibetan_prefectures.geojson` | 4 | GADM v4.1 中國 4 個藏族自治州（甘南/甘孜/阿壩/迪慶） |

渲染順序：admin_0 → admin_1(50m) → admin_1(10m) → GADM admin_2，**後者覆蓋前者**。

### COUNTRIES_USING_ADMIN1（這些國家 admin_0 不渲染，由 admin_1 取代）
```ts
new Set(['CHN','RUS','USA','CAN', 'LBY','AFG','UKR','SDN','ETH','NGA','GHA'])
```
注意 **FRA 不在此集合**：本土靠 admin_0 一張紫，僅 5 個海外省（FR-GF/MQ/GP/RE/YT）以「疊圖型 admin_1」覆蓋下方對應區域。所有「疊圖型 admin_1」（父國非 COUNTRIES_USING_ADMIN1）在 drilled 模式維持全不透明，避免下方 admin_0 顏色滲出。

---

## 資料源（單一檔）

**[data/maps/world-religions.ts](../../../data/maps/world-religions.ts)** 是唯一資料來源，~700 行，包含：

```ts
export const REALMS: Realm[]                     // 8 大界域
export const SPHERES: CulturalSphere[]            // 30 個文化圈
export const COUNTRY_REALM: Record<ISO3, RealmId> // 國家→主要界域（admin_0 上色用）
export const COUNTRY_NAME_ZH: Record<ISO3, string>// 繁體國名（不用 NE 簡體）
export const COUNTRIES_USING_ADMIN1: Set<string>  // 走 admin_1 渲染的國家
export const ADMIN1_SPHERE: Record<string, sphereId>  // iso_3166_2 → 文化圈
export const ADMIN1_NAME_ZH: Record<string, string>   // 行政區繁體名
export const COUNTRY_DEFAULT_SPHERE: Record<ISO3, sphereId>  // admin_1 沒對應時的後備
```

ADMIN1_SPHERE key 也支援 GADM admin_2 用 `'gadm:GID_2'` 前綴（如 `'gadm:CHN.5.3_1'` = 甘南）。

### 8 大界域定案配色（不要改）
| Realm | Hex | 樣 |
|---|---|---|
| 中央 (central) | `#16A34A` | 綠 |
| 東方 (eastern) | `#EAB308` | 黃 |
| 拉美 (latin-america) | `#DC2626` | 紅 |
| 西方 (western) | `#9333EA` | 紫 |
| 亞太 (asia-pacific) | `#2196F3` | 藍 |
| 南方 (southern) | `#A0522D` | 棕 |
| 北方 (northern) | `#7593B5` | 灰藍 |
| 北美 (north-america) | `#2A9D8F` | 翡翠綠 |

子色由 `shadeForSphere(realmHex, idx, total)` 在 HSL 空間動態算：
- L 範圍 `[max(26, l-24), min(78, l+24)]`，依基底光度伸縮（避免深色 base 下半段被 clamp 夾平）
- H 範圍 ±28°
- S 交錯 ±10/±14（奇偶 idx 強化鄰近對比）

---

## 30 個文化圈 + 各圈的 admin_1 映射

### 中央界域 (6 圈)
- 兩河-黎凡特：IRQ/SYR/LBN/PSE/ISR/JOR
- 埃及：EGY/SDN(N+E 10省)/LBY(東 Cyrenaica 7 區)
- 愛琴-小亞細亞：GRC/CYP/TUR
- 波斯：IRN/AFG(西+中 11 省)/TJK
- 高加索：ARM/GEO/AZE/RUS(北高加索 9 區)
- 阿拉伯：YEM/SAU/OMN/BHR/QAT/ARE/KWT

### 東方界域 (3 圈)
- 印度：PAK/IND/NPL/LKA/AFG(南+東 12 省)/BGD/MDV
- 漢地：CHN(關內 24 省)
- 圖博：CHN(西藏+青海 + 4 個藏族自治州)/BTN

### 拉美界域 (5 圈)
- 中美洲-墨西哥：MEX/GTM/BLZ/HND/SLV/NIC/CRI/PAN/USA(SW 延伸)
- 安地斯：PER/BOL/ECU/COL
- 加勒比：CUB/DOM/HTI/JAM/BHS/VEN/GUY/SUR/8 加勒比小國 + FR-GF/MQ/GP
- 南錐：CHL/ARG/PRY/URY
- 亞馬遜-巴西：BRA

### 西方界域 (9 圈)
- 拉丁：ITA/VAT/SMR/ESP/PRT/MLT/MCO/AND
- 巴爾幹：MKD/BGR/SRB/ROU/ALB/ex-Yugoslavia/MDA
- 高盧-法蘭西：FRA（本土）
- 不列顛-凱爾特：GBR/IRL/FLK
- 中歐：DEU/AUT/CHE/CZE/HUN/SVK/POL(東普魯士)/LIE
- 低地：BEL/NLD/LUX
- 盧布林：POL/UKR(西+基輔以西 13 州)/LTU/LVA(Latgale)
- 北歐-立窩尼亞：DNK/SWE/NOR/ISL/FIN/EST/LVA(西+中)
- 迦太基-馬格里布：TUN/DZA/MAR/LBY(中西部 15 區)

### 亞太界域 (5 圈)
- 眉公：KHM/VNM/MMR/THA/LAO
- 黑潮：PRK/KOR/JPN(含琉球)/TWN
- 班努亞：IDN/MYS/BRN/SGP/PHL/TLS
- 太平洋：VUT/FJI/WSM/TON/PLW/FSM/MHL/KIR/NRU/TUV/PNG/SLB/USA(夏威夷)
- 紐奧：AUS/NZL

### 南方界域 (6 圈)
- 衣索比亞：ETH(高地+OR/SN/GA = 8 州)/ERI
- 西非-薩赫爾：MLI/SEN/NER/CPV/BFA/GIN/GMB/GNB/MRT/TCD/SDN(達富爾+科爾多凡 6 區)/NGA(北 19 州)/GHA(北 3 州)
- 東非-斯瓦希里：SOM/KEN/TZA/MDG/SSD/UGA/RWA/BDI/DJI/COM/SYC/ETH(SO/AF/HA 3 州)/FR-RE/FR-YT
- 幾內亞灣：NGA(南 18 州)/GHA(南 7 州)/LBR/BEN/TGO/CIV/SLE
- 中非-剛果：COD/COG/CMR/CAF/GAB/GNQ/STP
- 南部非洲-班圖：ZWE/MOZ/ZAF/AGO/NAM/BWA/ZMB/MWI/LSO/SWZ

### 北方界域 (4 圈)
- 圖蘭-突厥：UZB/AFG(北 9 省)/TKM/CHN(新疆)/KGZ/KAZ
- 羅斯-韃靼：UKR(東+南 12 州)/BLR/RUS(歐俄 47 區)/RUS(加里寧格勒)
- 蒙古-通古斯：MNG/CHN(內蒙古+黑/吉/遼)/RUS(布里亞特/圖瓦/卡爾梅克)
- 西伯利亞：RUS(西伯利亞 13 區 + 遠東南 7 區 + 薩哈)

### 北美界域 (3 圈)
- 盎格魯美洲：USA(本土 48+DC+AK)/CAN(南 9 省)
- 法蘭西美洲：CAN(QC+NB)/USA(新法蘭西 — is_extension)
- 北極：GRL/CAN(NT/NU/YT)/USA(AK)/RUS(楚科奇)

---

## 編輯模式（拖曳標籤 + 自訂引線）

下鑽進任一界域後右上 **「✏️ 編輯標籤」** toggle 開啟：
- 拖標籤可調位置（位置存 lnglat 到 localStorage）
- 「＋線」按鈕 → 點地圖任一點新增 leader 引線錨點
- 紅圓錨點：點掉 = 刪該錨；主錨變大空心/實心 toggle 主引線顯示
- 「↺ 重置位置」清空當前界域所有 override

**localStorage key**：`maps:wr:label-overrides:v1`
```ts
type Overrides = Record<RealmId, Record<sphereId, {
  lnglat?: [n,n]              // 拖移後的顯示位置
  extraAnchors?: [n,n][]      // 用戶加的額外引線錨點（lng/lat）
  hideMainLeader?: boolean    // 隱藏主 centroid→label 線
}>>
```

優先順序：用戶 lnglat override > sphere.label_lnglat 程式硬編 > 自然 centroid。

CulturalSphere 也可在資料層硬編 `label_lnglat?: [lng, lat]` 預設位置（目前用在 `central-european: [13, 50]`，有歷史脈絡的釘位）。

---

## NE GeoJSON 對照陷阱（已踩過的雷）

1. **NE 50m admin_0 ISO_A3 == "-99"** for FRA / NOR / KOS / Northern Cyprus / Somaliland — 用 `getAdm0Code()` 後備到 `ADM0_A3`。
2. **PSE/SSD/ESH** ADM0_A3 是 PSX/SDS/SAH，但 ISO_A3 是正確的 — 我們用 ISO_A3 優先。
3. **GUF (法屬圭亞那)** 在 NE 50m admin_0 不存在獨立 feature，是 FRA multipolygon 的一部分 → 必須用 NE 10m admin_1 的 FR-GF 疊圖。其他 FR 海外省同理。
4. **NE 10m admin_1 中 Crimea (UA-43) + Sevastopol (UA-40)** 有時被標 `adm0_a3='RUS'`，10m 版正確標 UKR — 不要在 10m 子集腳本裡寫死「排除 UA-」filter（會把 25 個 UKR oblast 全篩光）。
5. **CN-Tibetan-4-Provinces** 中「四省藏區」是 sub-prefecture 概念，NE admin_1 只切到省，必須用 GADM admin_2 切自治州。

---

## 常見操作

### 加一個新國家（doc 內已列）
1. 加進 `COUNTRY_NAME_ZH` 繁體名
2. 加進 `COUNTRY_REALM` 主要界域
3. 加進對應 `SPHERES.x.members[]` 陣列
4. 視需要 `is_extension: true`（doc 用 `［...］` 表示的延伸地）

### 加跨界域國家（如 LBY 切東/西、AFG 切三向）
1. 加進 `COUNTRIES_USING_ADMIN1`
2. 在 `ne_10m_admin_1_extra.geojson` 子集腳本加入該 ADM0_A3
3. 為每個 iso_3166_2 寫 `ADMIN1_SPHERE` 對應（不寫的省份走 `COUNTRY_DEFAULT_SPHERE` 後備）
4. `ADMIN1_NAME_ZH` 補繁體
5. `COUNTRY_DEFAULT_SPHERE` 指定該國未明 admin_1 的預設 sphere

### 加 admin_2 級細分（如四省藏區）
1. 下載 GADM `gadm41_<ISO>_2.json`（~5MB/國）
2. node script 篩出需要的 GID_2，輸出 `public/maps/<name>.geojson`，properties 留 `GID_0/GID_2/NAME_1/NAME_2`
3. 在 [components/maps/WorldThematicMap.vue](../../../components/maps/WorldThematicMap.vue) `onMounted` 加 fetch + entries 迴圈，key 用 `'gadm:' + GID_2`
4. `ADMIN1_SPHERE['gadm:GID']` 對應 sphere
5. `ADMIN1_NAME_ZH['gadm:GID']` 繁體名

### 加新 sphere（如「迦太基-馬格里布」）
1. `SPHERES` 陣列追加：`{ id, name_zh, name_en, realm_id, members[] }`
2. `COUNTRY_REALM` 改對應國家的主要界域
3. `ADMIN1_SPHERE` 把該國 admin_1 指向新 sphere id
4. 新 sphere 在 realm 內的位置（陣列 index）影響子色 idx — 重要！

### 改某 admin_1 區劃歸屬
直接改 `ADMIN1_SPHERE['CN-XX']` 即可，不必改 SPHERES.members（那是「資訊列表」用，不影響地圖渲染）。

---

## 主要元件結構

[components/maps/WorldThematicMap.vue](../../../components/maps/WorldThematicMap.vue) ~600 行：
- `featureEntries` ref：四層所有 features 統一陣列
- `paths` ref：每 feature 算好的 d 字串 + fill + opacity + tooltip 資訊
- `realmLabels`/`sphereLabels` ref：標籤位置 + 是否需 leader line
- `transform` ref：d3-zoom 的 k/x/y 狀態
- `selectedRealm`/`selectedFeature`/`editMode`/`addAnchorFor`/`overrides` 編輯狀態
- `rebuildAll()`：重算所有 paths + labels（在 features 載入、selectedRealm 切換、resize 時觸發）
- `relaxLabelCollisions()`：40 次迭代斥力推開重疊標籤；用戶鎖定的不動

[components/maps/RealmInfoList.vue](../../../components/maps/RealmInfoList.vue)：純 SPHERES 資料的階層列表，依 realm 分卡片，沒有 admin_1 對照（資料層的 sphere.members 只記 doc 列名單）。

[pages/maps/world-religions.vue](../../../pages/maps/world-religions.vue)：地圖／列表雙 view 切換。

---

## 已知限制與待辦

- ETH 內部 admin_1 切分依「Menelik 帝國 vs Cushitic Muslim 邊緣」做了概略劃分，邊界州（Oromia 內部、Harari）有判斷餘地。
- SDN 西部 Darfur+Kordofan → 西非-薩赫爾是延伸解讀（doc 沒明確指）。
- USA Mesoamerican 西南州延伸（is_extension）目前不在地圖上染色，僅資料記錄。
- 若日後 doc 出新版 / 用戶提新分類，動 ADMIN1_SPHERE 即可，不必動 SPHERES.members。

---

## Recent commit（按近期順序）

`1adb11f` 衣索比亞圈擴展至帝國時代整入區
`fd8b95f` shadeForSphere 改用基底光度動態範圍
`566079f` 引線錨點統一視覺
`ae7d43e` 子色拉開差距 + 高盧標籤回法國 + 切主引線
`ebd0cf4` 標籤編輯模式（拖曳 + 多引線 + localStorage）
`e5e9d95` UKR 25 個 oblast 重新出現
`81cc73b` 迦太基-馬格里布回西方界域
`c778261` 法國回 admin_0 + 新增馬格里布圈 + RU 重判 + 標籤手動鎖定
`4e46a1b` 蒙古-滿洲改名蒙古-通古斯 + 俄羅斯遠東移西伯利亞
`57be959` 四省藏區 GADM 染圖博色
`158e054` 法屬圭亞那獨立染色 + 點海洋退出 + 標籤防重疊
`c5a83fc` admin_1 次國家上色 + 繁體國名 + 台灣修為亞太黑潮
`b448b07` 全球八大人文宗教界域主題地圖（首版）
