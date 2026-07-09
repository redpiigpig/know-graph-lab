# 品質提升作戰計畫：/genealogy + /maps（2026-07-08 交接）

> 背景：全專案體檢後使用者定調「族譜與地圖品質未到水準」。痛點已確認：
> **族譜＝圖的視覺品質＋資料不完整/有錯；地圖＝邊界精度＋政權資料品質＋標籤可讀性**。
> 本檔是執行交接：開新 session 說「照 genealogy/maps 品質 handoff 跑」即可。

## 前置狀態
- Supabase 402 鎖站中（exceed_db_size_quota；DB 已瘦到 359MB < 500MB，預計 2026-07-09 內自動解鎖）。
  解鎖前 DB 讀寫可走 Management API（`api.supabase.com/v1/projects/vloqgautkahgmqcwgfuo/database/query`，見記憶 reference_supabase_management_api）。
- 26 份 SKILL.md 已審訂（commit c2af063c）；genealogy 編輯面板孤兒元件已刪（本來就沒接上）。
- 相關 skill：genealogy-biblical / genealogy-episcopal / genealogy-islamic / maps-historical-borders / maps-world-religions。

## 任務 A：族譜視覺品質（優先）
檔案：`components/genealogy/BiblicalSpineTree.vue`（~千行手刻遞迴佈局）、`IslamicSpineTree.vue`、`EpiscopalSpineTree.vue`
1. **子嗣 drop 一致化**：drop 一律從「婚姻線段中點」下垂。現況 wife.children 與 husband.children 不對齊時會從 husband 節點直落（視覺斷裂）。演算法端修 layoutSubtree 的 drop 起點計算；資料端見任務 B-1。
2. **婚線避讓**：多妻（WIFE_HG=60 固定間距）與跨脊婚線交錯壓線——加簡單的線路分層/錯開（不同 y-offset 或彎折）。
3. **間距與縮放**：檢視 NW/兄弟間距常數在大子樹的擁擠問題；縮放後字級可讀性。
4. **守護**：`test/genealogy/fixtures/snapshots/episcopal.json` 已有 snapshot fixture——為 biblical/islamic 也建 layout snapshot 測試，改演算法不退化。
5. 驗證：跑 dev server 實看三個 tree（biblical 需 DB 解鎖或 Management API 撈資料做 fixture）。

## 任務 B：族譜資料正確性
（DB 相關，鎖站期間走 Management API，或等解鎖）
1. **wife/husband children 對齊稽核**：批次掃 biblical_people——凡 wife.children ⊄ husband.children 的列出並修（規則見記憶 feedback_wife_children_alignment）。
2. **CUV2010 人名校對 Task 2 續跑**（genealogy-biblical SKILL.md 記載待續）。
3. **傳統視角圖層資料補密**：早期教會/天主教/東方教會/拉比四視角的稀疏人物補注（走 Gemini→NVIDIA→Haiku，來源標註）。

## 任務 C：地圖邊界精度
檔案：`public/maps/fine-polygons.geojson`（現 230 polygons/49 帝國）、`public/maps/polygon-year-overrides.json`
1. 擴充 fine polygons 帝國名單：優先補「地圖上最常被看、原始邊界最離譜」者——candidate：薩珊波斯、笈多、阿拔斯、法蒂瑪、塞爾柱、馬其頓繼業者諸國、印加/阿茲特克細化、東南亞（吳哥/滿者伯夷）、非洲（馬利/桑海/阿克蘇姆）。做法照 maps-historical-borders SKILL.md 的 city-hull 法，每帝國 3–8 個 polygon。
2. polygon-year-overrides 再掃一輪：源資料年代過寬的政權收窄（現 69 條）。

## 任務 D：地圖政權資料品質
1. **分類器補強**：`public/maps/polygon-classifications.json` + KNOWN_STATES/KNOWN_NON_STATES 規則——掃「被判 is_state 但實為部落/文化群」與反向漏網，批次修。
2. **中文譯名缺口**：`polygon-names-zh.json` 對 6,853 政權掃缺，Gemini batch 補（譯名遵 /translation-glossary：王朝-民族帝國格式，見記憶 feedback_dynasty_empire_naming）。
3. **STATE_DETAILS 充實**：高曝光政權（大帝國/中國朝代/聖經相關）優先補詳情彈窗內容。

## 任務 E：地圖標籤可讀性
檔案：`components/maps/HistoricalBordersMap.vue`（751 行）、`WorldThematicMap.vue`（1,171 行）
1. **碰撞偵測**：標籤加 bbox 碰撞檢查，重疊時依 polygon 面積優先級隱藏小者。
2. **縮放分級**：zoom level 決定顯示門檻（小政權標籤只在放大後出現）。
3. **標籤位置**：改用 polylabel（最大內切圓心）取代質心，避免細長 polygon 標籤跑出界。
4. 守則：polygon 標籤只放純國名/朝代名（記憶 feedback_map_label_clean_country_name）。

## 執行順序建議
E（標籤，純前端見效最快）→ C/D（資料策展，可平行）→ A（佈局演算法，配 snapshot 測試）→ B（等 DB 解鎖）。
引擎政策：Gemini→NVIDIA(deepseek-v4-flash)→Haiku。改完各 skill 的 SKILL.md 同步更新；有變更自動 commit+push。
