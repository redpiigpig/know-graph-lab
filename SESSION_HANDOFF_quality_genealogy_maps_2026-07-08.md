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
> ✅ **2026-07-11 以「驗證取代重構」結案**。系統性截圖驗收六個熱區——大衛七妻群、雅各四妻＋12子、路得利未拉特列、猶大-她瑪、以掃區、哥轄 121 人深層展開、伊斯蘭樹主幹——**全部乾淨：零婚線交錯、零卡片重疊、間距充裕**。7/8 觀察到的視覺亂象根因是資料層 bug（互指斷鏈/drop 錯位），任務 B 修完後缺陷不再重現。不做盲目重構的理由：①無可重現缺陷；②SKILL.md 多處核心規則標「不要再改！」且有 2026-05-14 全域碰撞後處理失敗實驗（ghost 框）前例；③護欄已存在（test/genealogy 6 spec：mount＋fixtures＋collisions 檢查＋realdata snapshot，220 測試綠）。日後若使用者指出具體醜點，用 scripts/_tree_shot.mjs / _tree_expand_shot.mjs 定點截圖後針對性修。

## （原任務 A 文字保留備查）
檔案：`components/genealogy/BiblicalSpineTree.vue`（~千行手刻遞迴佈局）、`IslamicSpineTree.vue`、`EpiscopalSpineTree.vue`
1. **子嗣 drop 一致化**：drop 一律從「婚姻線段中點」下垂。現況 wife.children 與 husband.children 不對齊時會從 husband 節點直落（視覺斷裂）。演算法端修 layoutSubtree 的 drop 起點計算；資料端見任務 B-1。
2. **婚線避讓**：多妻（WIFE_HG=60 固定間距）與跨脊婚線交錯壓線——加簡單的線路分層/錯開（不同 y-offset 或彎折）。
3. **間距與縮放**：檢視 NW/兄弟間距常數在大子樹的擁擠問題；縮放後字級可讀性。
4. **守護**：`test/genealogy/fixtures/snapshots/episcopal.json` 已有 snapshot fixture——為 biblical/islamic 也建 layout snapshot 測試，改演算法不退化。
5. 驗證：跑 dev server 實看三個 tree（biblical 需 DB 解鎖或 Management API 撈資料做 fixture）。

## 任務 B：族譜資料正確性
（DB 相關，鎖站期間走 Management API，或等解鎖）
1. ✅ **wife/husband children 對齊稽核（2026-07-08 完成）**：`scripts/genealogy_data_audit.py`（稽核＋--fix 分級修復，Management API）。六類檢查全歸零：懸空引用/變體引用/wife-children 對齊/spouse 互指；共修 50+ 列、新建 6 個缺 row（亦施韋/毗敦/米勒/他利亞/亞哈斯（米迦之子）/阿里斯托布魯四世）、合併以他瑪重複 row、清撒母耳母親誤植與以東王比拉誤掛子嗣。羅得亂倫群組依佈局特例刻意不動（KID_SKIP）。日後資料再髒直接重跑此腳本。
1b. ✅ **伊斯蘭＋使徒統緒稽核（2026-07-08 完成）**：`--table islamic_people` 歸零（新建 20 缺 row，388→408；神學紅線：爾撒無父/宰娜卜之子阿里同名不同人，已寫死腳本）；episcopal 六項 SQL 稽核歸零（sees 中間點·→‧正規化、圖爾庫/哈瓦那年代顛倒、漢堡赫塞編號撞鏈移鏈尾；殘留 13 筆「前任較晚」＝名人註記卡策展，非 bug）。
2. ✅ **CUV2010 人名校對（2026-07-11 完成）**：10 條改名全經本地 CUV2010 經文逐節驗證（創 36 以東家譜字形＋但之子戶伸），token-boundary 全表同步、audit 歸零。原候選表 2 處錯誤已抓出拒改（撒雲≠示玻、雅述≠雅薛），留使用者定奪——詳 genealogy-biblical SKILL.md。
3. ✅ **傳統視角圖層補密（2026-07-11 完成）**：+16 人全附文獻出處（早期教會：西面（革羅罷之子）；天主教：聖亞拿譜系 5 人含黃金傳說 Eliud→Servatius 鏈；東正教：撒羅米（約瑟之女）；拉比：比提雅/約伯/歌利亞四巨人/伊磯倫/大衛之母尼哲貝特等 9 人），989 人 audit 歸零。存疑 3 項（艾梅倫提亞 15 世紀傳統最薄弱、米利暗＝以法他與喇合嫁約書亞兩認同說刻意未做）留使用者定奪——詳 genealogy-biblical SKILL.md。

## 任務 C：地圖邊界精度
> ✅ **2026-07-11 查證：本任務當初的候選名單（薩珊/笈多/阿拔斯/塞爾柱/印加/馬利/桑海/高棉/滿者伯夷…）其實早在 2026-05-18/20 兩輪已全覆蓋**（fine 279 + manual 219 + OHM 781 + CHGIS 94），handoff 撰寫時漏查。真正剩的邊界工作見 maps-historical-borders SKILL.md「待補 C/D」（立陶宛大公國、凹邊 alpha-shape、DARMC 整合等長期項）。

## （原任務 C 文字保留備查）
檔案：`public/maps/fine-polygons.geojson`（現 230 polygons/49 帝國）、`public/maps/polygon-year-overrides.json`
1. 擴充 fine polygons 帝國名單：優先補「地圖上最常被看、原始邊界最離譜」者——candidate：薩珊波斯、笈多、阿拔斯、法蒂瑪、塞爾柱、馬其頓繼業者諸國、印加/阿茲特克細化、東南亞（吳哥/滿者伯夷）、非洲（馬利/桑海/阿克蘇姆）。做法照 maps-historical-borders SKILL.md 的 city-hull 法，每帝國 3–8 個 polygon。
2. polygon-year-overrides 再掃一輪：源資料年代過寬的政權收窄（現 69 條）。

## 任務 D：地圖政權資料品質
> ✅ **2026-07-11 完成**：①分類器稽核零誤判（僅 3 筆全是 v2 標準刻意排除）；②可見政權中文覆蓋率 100%（補 11 條手譯，其餘缺譯全是被過濾的部落名）；③STATE_DETAILS 277→357（+80：薩法維/東羅馬/莫斯科沙皇國/察合台/德干四蘇丹/高句麗/大和/匈奴/阿克蘇姆/馬雅諸條等，realm/sphere 全合法、前身後繼對齊實存 polygon）。

## （原任務 D 文字保留備查）
1. **分類器補強**：`public/maps/polygon-classifications.json` + KNOWN_STATES/KNOWN_NON_STATES 規則——掃「被判 is_state 但實為部落/文化群」與反向漏網，批次修。
2. **中文譯名缺口**：`polygon-names-zh.json` 對 6,853 政權掃缺，Gemini batch 補（譯名遵 /translation-glossary：王朝-民族帝國格式，見記憶 feedback_dynasty_empire_naming）。
3. **STATE_DETAILS 充實**：高曝光政權（大帝國/中國朝代/聖經相關）優先補詳情彈窗內容。

## 任務 E：地圖標籤可讀性
檔案：`components/maps/HistoricalBordersMap.vue`（751 行）、`WorldThematicMap.vue`（1,171 行）
1. ✅ **HistoricalBordersMap 完成（2026-07-11，commit 27012527）**：polylabel 錨點＋縮放感知面積優先貪婪選擇＋kQuant 量化＋字級分層。驗收 1501 BCE 6/8、1900 CE 64 標籤零重疊。細節見 maps-historical-borders SKILL.md「標籤系統 v2」。
2. ✅ **WorldThematicMap 驗證無需改動（2026-07-11）**：實測截圖八大界域層標籤零重疊、清楚易讀（scripts/_wr_check.mjs）；人工策展位置健康，不套 v2。
3. 守則：polygon 標籤只放純國名/朝代名（記憶 feedback_map_label_clean_country_name）。

## 執行順序建議
E（標籤，純前端見效最快）→ C/D（資料策展，可平行）→ A（佈局演算法，配 snapshot 測試）→ B（等 DB 解鎖）。
引擎政策：Gemini→NVIDIA(deepseek-v4-flash)→Haiku。改完各 skill 的 SKILL.md 同步更新；有變更自動 commit+push。
