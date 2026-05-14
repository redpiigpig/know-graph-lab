---
name: biblical-tradition-layer
description: 聖經族譜的「教會傳統」視角圖層 — 早期教會（橘色，東西方共識）／天主教（紅）／東方教會（黃）／拉比傳統（藍）。包含資料表 schema、人物清單、UI 切換與配色設計、未完成 layout 修正項目。
---

# 聖經族譜 — 教會傳統視角圖層

> 接手用 skill。session 之前已做過 compaction，此檔記錄所有未完成項目與設計決策。

主要檔案：[components/genealogy/BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue)、
[server/api/genealogy/biblical-graph.get.ts](../../../server/api/genealogy/biblical-graph.get.ts)、
[pages/genealogy/biblical.vue](../../../pages/genealogy/biblical.vue)（表格）、
[pages/genealogy/biblical-tree.vue](../../../pages/genealogy/biblical-tree.vue)（族譜圖）、
[scripts/biblical-shot.mjs](../../../scripts/biblical-shot.mjs)（headless screenshot 驗收）。

---

## ⚠️ 失敗實驗：global collision-avoidance post-pass（2026-05-14 移除）

**症狀**：頁面看起來壞掉 — 畫面頂端出現一條跨整個畫布的灰色橫線、左右各一條跨全高的灰色垂直線，像個外框包住整棵樹。但**不是** compile error（之前 dev overlay 顯示的 `isAnchored already declared` 是 stale cache，已收斂）。

**原因**：commit c4e8cf5 + 2d0371f 加了一個 post-pass，按 Y row 排序卡片，重疊時呼叫 `shiftCardAndLines`。函式把卡片中心對齊的 `drops` / `hbars` 端點一起平移，但同一條 hbar 的另一端可能是 spine anchored 卡（位置不動）。卡片被推到 canvas 邊緣後，hbar 的一端跟著走、另一端仍在 spine col，整條變成跨畫布的 ghost 線。Cluster-shift（往左 cascade）讓多張卡同時被推到極遠，產生兩條長 ghost vertical drops 加一條長 ghost hbar，視覺像個方框。

**修法**（commit 802a802）：直接刪掉整個 collision-avoidance 區塊（原 line 1594-1652）。代價是同 Y row 偶爾還是有 2-3 張卡 ~50px 重疊（例如 J7 row 的 洗拉/以諾 — 該隱支系），但比 ghost 框乾淨太多。

**如果未來想重做**：要區分「卡片端」與「線端」— 推卡片時，**只移動 drop（從卡片往下垂直線）**，不要碰 hbar 端點。或者乾脆每次 collision 推卡後 rebuild hbar 整段（用該 row 還活著的 anchor 點重新算），不要靠端點 cache。

**驗收 screenshot 約束**：`scripts/biblical-shot.mjs` 預設 viewport 2800×1800，會超過 2000px 上限 → 對話會卡死。**一定要用 `--width 1800 --height 1200`**（或更小）。

---

## 🟢 當前狀態快照（2026-05-14，commit `802a802`）

### 架構
- **URL 拆分**：`/genealogy/biblical`（表格 CRUD）+ `/genealogy/biblical-tree`（族譜圖），各自獨立路由
- **視角機制**：4 個 view，全域 query param `?view=protestant|early_consensus|orthodox|catholic`，預設 protestant
  - 對應到 `/api/genealogy/biblical-graph?view=...`
  - 規則：累進納入更多傳統人物 + JSONB 套用
    - protestant: biblical + rabbinic + **early_consensus**（後者為了 SPINE_B 必經的 約亞敬/亞拿 anchor；用橘色卡視覺區隔，無 JSONB 套用）
    - early_consensus: + orthodox JSONB（Epiphanian view，Jerome 393 前主流）
    - orthodox: + orthodox 全部人物 + orthodox JSONB
    - catholic: + catholic 全部人物 + catholic JSONB

### UI
- **耶穌聖家詮釋 toggle**：浮動 widget anchored 到「約瑟（馬利亞之夫）」卡片右側，透過 `josephScreenPos` computed 跟 pan/zoom 同步移動（[BiblicalSpineTree.vue:1708](../../../components/genealogy/BiblicalSpineTree.vue#L1708)）
- **Card 配色**：早期教會橘 / 天主教紫 / 東方綠 / 拉比藍（避開 spine amber/rose + 女性 rose-50 衝突）
- **線條顏色**（重要！）：
  - **紅色 `#dc2626`**：**只有**「夫妻間橫向婚姻線」（亞當↔夏娃式）。
  - **灰色 `#9ca3af`**：婚姻線→T-bar drop / T-bar 本身 / T-bar→子女 drop — 全部灰色。
  - **特例**：「有妻無母」（如大衛 11 子無記載母親）— hbar 跟 marLineY 同 Y，**算婚姻線延伸**，用紅色。判定條件：`mom===null && barY===marLineY`，且 **必須 `wifeIds.length > 0`**（commit 67505f5 修補 — 否則挪亞這種無妻無母的 case 會誤判成假紅線）。
  - **聖靈感孕（約瑟↔馬利亞）**：紅色 dashed (`stroke-dasharray="6,4"`)。
  - **法律關係 / 過繼**：灰色 dashed。
  - 主幹 guide line：spine A amber `#f59e0b`、spine B rose `#f43f5e`。
- **Legend**：左下角 4 種傳統 swatch + 線條說明

### Layout
- **共妻 drop X**：`mommidX` 對每個媽媽的 drop X = 與「靠丈夫方向的相鄰卡片」的中點（主妻=與丈夫；非主妻=與前一妻子）
- **嫁出去的女兒當 leaf**：`renderedAsSpouseOnSpine` 集合 + layoutSubtree 開頭判斷；descendants 算到丈夫家樹
- **Trinubium 妻列擴展**：spine wife 同代「其他配偶」append 進婚姻列（亞拿的 3 夫並列）
- **Occlusion 強化**：bbox 內非自家 expansion 卡片/線全 hidden（lineInAnyBbox helper）
- **expansion 中渲染子代妻子**：layoutSubtree 多回傳 marriages 串到 placeOne（以底特 在 羅得 旁邊就靠這個）

### DB 重要 entries / 連線（最新）
- 葉特羅（米甸之祭司）gen 25，CUV2010 用「特」字（出 3:1）
- 何巴（摩西的內兄）gen 26
- 6 個明文 FIL：以連、達買、波提非拉、亞希瑪斯、耶羅罕、亞拿（祭便之子）
- 斯多蘭（亞拿之父）early_consensus gen 72，掛在 利未（路加 3:24, gen 71 spine B），與 瑪塔 為兄弟
- 蘇比 → 以利沙白 → 施洗約翰 整條 chain 渲染
- 約瑟（patriarch, gen 23）.spouse = 亞西納（反向連結補齊）
- 羅得家族：羅得長女/次女（biblical gen 22, children=摩押/便亞米），以底特（羅得之妻, rabbinic gen 21）
- 大衛妻 gen 補齊：拔示巴 33、亞希暖（掃羅之妻）32、哈及 33、亞希暖（耶斯列人）33
- Ruth 家族（**剛補**）：以利米勒 / 拿俄米 gen 29、瑪倫 / 基連 / 俄珥巴 / 路得 gen 30；以利米勒 加進 拿順（亞米拿達之子）.children 與 撒門 並列為兄弟
- 路得.spouse = 瑪倫、波阿斯（雙夫；先嫁瑪倫死後嫁波阿斯）

### ⚠️ 已知未解 / 待驗收
1. ~~**截圖腳本 timeout**~~ ✅ **修好（2026-05-14）**：root cause = protestant view 把 `約亞敬（聖母之父）` (tradition=early_consensus) filter 掉，導致 SPINE_B BFS 在 瑪塔→馬利亞 斷掉，整張圖 `hasSpine = false`，沒有任何 `.node-card` 渲染，所以 selector 永遠 timeout。修法：API 把 early_consensus 加進 protestant 的 allowedTraditions（無 JSONB merge，純 anchor）。dev server port 是 3002（`APP_BASE=http://localhost:3002`，Bash 用前綴語法、PowerShell 用 `$env:`）。Diag script: `scripts/biblical-spine-diag.mjs` — 抓 page 自己 fetch 的 API response 走兩條 spine 找斷點。
2. **Ruth 家族視覺驗收待 user 在瀏覽器確認** — DB 已連，但沒拍截圖驗證 layout
3. **耶穌聖家區域之前重疊問題** — 已透過「protestant 預設 filter 掉 catholic/orthodox 補充」緩解；要 user 確認沒問題
4. **toggle widget anchored 到約瑟卡片** — 邏輯已寫，但因截圖卡死所以沒視覺驗證；user 瀏覽器看時可能要實測 pan/zoom 跟隨是否流暢

---

## 已完成（前次 session）

1. ✅ **Uniform NW+HG spacing for gen-N kid row** — commit 2514ed2；spine wives + 兄弟 + 兄弟妻同一個 (NW+HG=140px) slot 等距
2. ✅ **Joseph/Mary 婚姻線改 dashed-red** — commit 16e93e8；template `:stroke-dasharray="m.holy ? '6,4' : ''"`；圖例新增第 4 條
3. ✅ **David wives + sons mother attribution** — `c:\tmp\david_wives.py`；7 妻已 INSERT/PATCH，子→母 children 字串綁定
4. ✅ **朔法 → 朔罷** rename per 1 Chr 3:5 CUV2010 — `c:\tmp\rename_shofa.py` + safe_rename token-boundary logic
5. ✅ **Solomon 的女兒** 她法、巴實抹 (1 Kgs 4:11, 4:15) + 兩女婿 — `c:\tmp\solomon_daughters.py`
6. ✅ **Schema**: `biblical_people.tradition text NOT NULL DEFAULT 'biblical'` CHECK constraint added（值：`biblical`/`early_consensus`/`catholic`/`orthodox`/`rabbinic`）+ index
7. ✅ **Phase 1 tradition tagging** — `c:\tmp\setup_traditions.py`：亞拿、約亞敬 → `early_consensus`；NT 諸人物 → `biblical`；刪除 `馬利亞（克洛帕斯之妻）` dedupe；插入 `希里（路加 3:23）`

## 已完成（本 session 後續）

14. ✅ **Trinubium spine-wife extension** — [BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue) 第 770 行附近：對每個 spine wife，把她「同代且不在 rowOf」的其他配偶加入婚姻列；同步 `placedAsRowSpouse` 集合避免 kidWife 重複渲染。修好 Task 4E-1（撒羅馬不見）+ 4E-3（革羅罷 Y 錯位）。
15. ✅ **UI Task 4A toggle / 4B card 配色 / 4C API filter / 4D Legend swatches** — 全部已就位（partial 在 commit 8f65f83；Trinubium 妻列在本次）
16. ✅ **配色避衝突** — catholic red → purple，orthodox yellow → emerald；避開 spine rose / amber + 女性卡片 rose-50（commit 73ff563）
17. ✅ **葉特羅整合** — 刪重複 entry `葉特羅`(cee98b27)；renamed `葉忒羅（米甸之祭司）` → `葉特羅（米甸之祭司）` per CUV2010 (出 3:1)；何巴.generation = 26
18. ✅ **6 個明文 FIL 插入** — `c:\tmp\insert_fils.py`：
    - 以連（拔示巴之父，gen 32，撒下 11:3）
    - 達買（基述王，gen 32，撒下 3:3）— 瑪迦之父
    - 波提非拉（安城祭司，gen 22，創 41:45）— 亞西納之父
    - 亞希瑪斯（亞希暖之父，gen 31，撒上 14:50）
    - 耶羅罕（以利加拿之父，gen 54，撒上 1:1）
    - 亞拿（祭便之子，gen 21，創 36:2）— 阿何利巴瑪之父
    - 順手補 wife gens：拔示巴 33、亞希暖（掃羅之妻）32、以利加拿（撒母耳之父）55
19. ✅ **Occlusion 強化** — `placeOne` 後的 occlusion pass 第二輪：spine cards 中心點在 `expansionBoxes` 內就 hidden（不再要求 per-card 直接 overlap）；trunkGuides 同此規則。展開 ▼ 時 spine 與 expansion 不再混雜。
20. ✅ **嫁出去的女兒當 leaf**（commit 51cd6f7）— `renderedAsSpouseOnSpine` 集合 + layoutSubtree 開頭判斷：女兒本身渲染、descendants 不算進娘家樹（subtreeIds 同步 capped）。
21. ✅ **羅得家族 + Edith** — DB 插 羅得長女、羅得次女（biblical gen 22，children=摩押/便亞米）+ 以底特（rabbinic gen 21，spouse=羅得）；摩押/便亞米 gen 22 → 23。
22. ✅ **約瑟.spouse = 亞西納** patch — 反向連結補齊。
23. ✅ **統一視圖架構**（本次大改）：
    - API 拿掉 people filter，永遠回 816+ 人；`?tradition=` → `?view=protestant|catholic|orthodox|early_consensus`（後者 = orthodox 內部）
    - 規則：tradition_X JSONB 中 cat+orth 都有值 → 視為衝突，依 view 取一；只有一邊 → 非衝突，永遠 apply；rabbinic 永遠 apply
    - UI 拿掉全域 tab，浮動 toggle widget 在族譜圖 top-center：聖經/早期教會/東方/天主教 4 選項。其他傳統人物永遠顯示，用 card 顏色辨識（橘早期共識/紫天主教/綠東方/藍拉比）。
    - layoutSubtree 擴展：expansion 中渲染子代的配偶（如 以底特 在 羅得 旁邊）；wivesReach 預留左側空間。layoutExpansion 同步串 marriages 流到 placeOne。
    - biblical-shot.mjs：`--view` 旗標取代 `--tradition`，path 直接到 /genealogy/biblical-tree。
24. ✅ **URL 拆 table / tree**：`/genealogy/biblical`（表格 CRUD）+ `/genealogy/biblical-tree`（族譜圖）各自獨立。
25. ✅ **斯多蘭（亞拿之父，early_consensus）** 插入 — Anchor 蘇比→以利沙白→施洗約翰 chain，掛在 利未（路加 3:24, gen 71 spine B）下，與 瑪塔 為兄弟。同步補 以利沙白/撒迦利亞 gen=74、施洗約翰 gen=75。
26. ✅ **大衛之子斷線修正**：`mommidX` for 非 primary wife 改為「妻子本人 X center」（而非和前一個 co-wife 的線段中點）。哈及→亞多尼雅 從妻子正下方直接掉下，不再分支自 co-wife 中間。

## 仍待

- 35 個 missing 岳父中尚有 ~20 個聖經沒寫名字（夏甲/基土拉父等）— 跳過
- 5 個明文 FIL 沒插（如 革鄙、以倫、洗便、拉麥之妻父等次要案例）— 看用戶要不要補
- Task 4E-2：蘇比（亞拿之姊）渲染需 sibling-via-shared-parent logic
- Task 1：dual-spine overlap detection
- Task 2：CUV2010 剩餘章節名字校對
- `audit_inlaws.py` parent_of map 有 name-matching false positives（拉班→利亞/拉結 連結沒接上）；script 待修

## 已完成（前次 session — commit 8f65f83）

8. ✅ **Schema: 3 個 JSONB 欄位** for per-tradition overrides — `c:\tmp\add_tradition_jsonb_cols.py`
   - `tradition_children` `{"catholic": "A、B", "orthodox": "..."}` → 加進 children
   - `tradition_spouse`   `{...}` → 加進 spouse
   - `tradition_hide_children` `{...}` → 從 children 移除
9. ✅ **Phase 2 — Catholic / Trinubium Annae** — `c:\tmp\phase2_catholic.py`
   - INSERT: 革羅罷（亞拿之第二夫）、撒羅馬（亞拿之第三夫）、馬利亞·撒羅米
   - PATCH JSONB on: 亞拿、馬利亞-革羅罷、約瑟、西庇太
10. ✅ **Phase 3 — Orthodox / Epiphanian view** — `c:\tmp\phase3_orthodox.py`
    - INSERT: 撒羅米（約瑟之前妻）、亞西亞、呂底亞、蘇比、革羅罷（約瑟之弟）
    - PATCH JSONB on: 約瑟、雅各-馬但、馬利亞-革羅罷
11. ✅ **API filter** — [server/api/genealogy/biblical-graph.get.ts](../../../server/api/genealogy/biblical-graph.get.ts) 接 `?tradition=` 並 merge JSONB columns 進統一 children/spouse 視圖
12. ✅ **biblical.vue + biblical-shot.mjs** 都支援 `?tradition=` query param
13. ✅ 驗收 screenshot：`c:/tmp/cath-mary.png`、`c:/tmp/orth-mary.png`

---

## 待辦事項

### Task 1: Dual spine overlap → 收進來等於旁支（之前未完成）

當主幹 A（馬太譜系，amber，右）與主幹 B（路加譜系，rose，左）視覺上會彼此遮到時，把其中一個收成 `旁支` 樣式。

目前狀態：用 `node scripts/biblical-shot.mjs --focus 拿單 --out c:/tmp/nathan-area.png` 看不出明顯 overlap，但 user 強調這個 spec 要實作。

**設計**：
- 偵測 spine A 第 N 代 kid row 的 leftmost X 是否 ≤ SPINE_B_CX − NW/2 − HG（會撞到 B column）
- 或：偵測某代的 expansion bbox 是否覆蓋 spine B 的卡片區
- 若是，將 spine B 在那 row 之後的 cards 改為「旁支」collapsed marker（單一灰色小卡 + 點擊展開），釋出 column 給 A
- 反之亦然

可以在 [components/genealogy/BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue) 1100 行附近的 occlusion logic 旁邊加 dual-spine overlap detection。

### Task 2: CUV2010 名字校對（之前未完成）

已查證的章節：
- 1 Chr 3:5 — **朔法→朔罷** 已 rename ✅
- 1 Kgs 4:11, 4:15 — Solomon's daughters 她法、巴實抹 ✅ inserted

未完成的 candidate report（**只是候選清單，不要 bulk apply**，per memory rule [feedback_biblical_name_rules.md](file://C:/Users/user/.claude/projects/c--Users-user-Desktop-know-graph-lab/memory/feedback_biblical_name_rules.md)）：

**Gen 36 找到 10 個 CUV2010 字形修訂候選**（最早出現章節，可以改）：

| DB 現在 | CUV2010 | 引用 |
|---|---|---|
| 阿勒完 | 亞勒文 | Gen 36:23 (朔巴 son) |
| 瑪拿哈 | 瑪拿轄 | Gen 36:23 (朔巴 son) |
| 以巴 | 以巴錄 | Gen 36:23 (朔巴 son) |
| 撒雲/示弗 | 示玻 | Gen 36:23 (朔巴 son) |
| 黑幔 | 希幔 | Gen 36:22 (羅坍 son) |
| 亞雅 | 愛亞 | Gen 36:24 (祭便 son) |
| 黑慕丹 | 欣但 | Gen 36:26 (底順 son) |
| 以實班 | 伊是班 | Gen 36:26 (底順 son) |
| 比利罕 | 辟罕 | Gen 36:27 (以察 son) |

**Gen 46 找到 2 個**：
| DB | CUV2010 | 引用 |
|---|---|---|
| 書含（但之子） | 戶伸 | Gen 46:23（earliest source vs Num 26 書含）|
| 雅述 | 雅薛 | Gen 46:24 拿弗他利之子 |

**Gen 10**: 0 discrepancies（已校對 100% match）

未校對章節：1 Chr 1（156 entry，最大）、1 Chr 2、1 Chr 7、Num 26、Gen 49、Gen 30、Luke 3。

**動作**：
1. 用 `c:\tmp\verify_gen36.py` 模式寫 verify_<chapter>.py
2. WebFetch `https://rcuv.hkbs.org.hk/RCUV2/<BOOK>/<CHAPTER>/` 取人名
3. 把 candidate diff append 到 `c:\tmp\verify_candidates.md`
4. **不要 auto-rename**；給 user review 後再用 `c:\tmp\safe_rename.py` apply

`safe_rename.py` 規則：token-boundary 匹配（split by `、`），只改 `name_zh == old` 或 `name_zh.startswith(old+'（')`，**不動 disambiguator** `（X之子）` 系列（除非父名整體 propagate）。

### Task 3: 教會傳統人物 INSERT — ✅ 本次 session 完成（commit 8f65f83）

**Tradition column 值**：
- `biblical` — 聖經（希伯來聖經 + 新約）— 預設顯示
- `early_consensus` — 早期教會東西方共識 → **橘色** card
- `catholic` — 天主教專有 → **紅色** card（西方 mode 才顯示）
- `orthodox` — 東方教會專有 → **黃色** card（東方 mode 才顯示）
- `rabbinic` — 拉比傳統 → **藍色** card（rabbinic mode 才顯示）

**已 INSERT 完整清單**：
- **Phase 1（前次）**: 亞拿、約亞敬 → `early_consensus`；撒迦利亞、以利沙白、施洗約翰、馬但、雅各-馬但、馬利亞-革羅罷、希里 → `biblical`
- **Phase 2（本次，catholic）**: 革羅罷（亞拿之第二夫）、撒羅馬（亞拿之第三夫）、馬利亞·撒羅米
- **Phase 3（本次，orthodox）**: 撒羅米（約瑟之前妻）、亞西亞（約瑟之女）、呂底亞（約瑟之女）、蘇比（亞拿之姊）、革羅罷（約瑟之弟）

**已新增 schema 欄位（JSONB）**：
- `tradition_children` — `{"catholic": "A、B", "orthodox": "..."}` 依 mode 加進 children
- `tradition_spouse`   — 同上加進 spouse
- `tradition_hide_children` — 從 children 移除（用於 Mark 6:3 兄弟在 catholic mode 從 約瑟 轉到 馬利亞-革羅罷）

**已 PATCH 的 JSONB**：
- 亞拿（聖母之母）.tradition_spouse[catholic] = 革羅罷+撒羅馬；.tradition_children[catholic] = 馬利亞-革羅罷+馬利亞-撒羅米
- 馬利亞（革羅罷之妻）.tradition_spouse[catholic] = 革羅罷-亞拿；.tradition_spouse[orthodox] = 革羅罷-約瑟；.tradition_children[catholic] = 雅各+約西
- 約瑟（馬利亞之夫）.tradition_spouse[orthodox] = 撒羅米-約瑟；.tradition_hide_children[catholic] = 雅各+約西；.tradition_hide_children[orthodox] = 雅各+約西+猶大+西門
- 雅各（馬但之子）.tradition_children[orthodox] = 革羅罷-約瑟
- 西庇太.tradition_spouse[catholic] = 馬利亞·撒羅米

**馬可 6:3 的耶穌兄弟 conflict 處理**：
- 新教：約瑟+馬利亞親生 ✅ 在 約瑟.children
- 天主教：馬利亞-革羅罷+革羅罷之子 → 用 tradition_hide_children 從 約瑟 移除；tradition_children 加到 馬利亞-革羅罷
- 東方教會：約瑟+撒羅米之子 → 從 約瑟 hide；加到 撒羅米-約瑟.children 直接（biblical 欄位）

**「革羅罷」conflict 處理**：catholic 的「亞拿之第二夫」與 orthodox 的「約瑟之弟」是兩個獨立 entry（不同 name_zh disambig），不互相 PATCH。

**API filter**（已實作）：`/api/genealogy/biblical-graph?tradition=<key>` 在 server side 把 JSONB merge 進 children/spouse 統一視圖，後續 pipeline mode-agnostic。預設 = biblical only。

**驗收**：`c:/tmp/cath-mary.png`、`c:/tmp/orth-mary.png` 都通過；biblical mode 完全不變。

### Task 4: UI 改造（核心，**部分完成**）

**檔案**：[components/genealogy/BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue)、[pages/genealogy/biblical.vue](../../../pages/genealogy/biblical.vue)、[server/api/genealogy/biblical-graph.get.ts](../../../server/api/genealogy/biblical-graph.get.ts)

**A. Tradition toggle UI** ⏳ **未完成** — 在頁面右上加：
```
[聖經] [天主教傳統] [東方教會] [拉比傳統]
```
- 預設「聖經」(biblical only)
- 任何 mode 都顯示 biblical + early_consensus；只是再加上選定的 catholic/orthodox/rabbinic
- 切換時更新 URL `?tradition=`（biblical.vue 已支援讀取，要加 binding 寫入）

**B. Card 配色** ⏳ **未完成** — 在 [BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue) `cardClass`：
```vue
const traditionColors = {
  biblical:        '',                               // 預設白底
  early_consensus: 'bg-orange-50 border-orange-300',
  catholic:        'bg-red-50 border-red-300',
  orthodox:        'bg-yellow-50 border-yellow-300',
  rabbinic:        'bg-blue-50 border-blue-300',
}
```
記得保留 spineKind 的左側 amber/rose bar（不要被 tradition 顏色蓋掉）。
**注意**：API 目前 node `data` 沒有 expose `tradition` 欄位（只有 generation/name 等），要先在 biblical-graph.get.ts 加 `tradition: p.tradition` 到 node.data。

**C. API filter** ✅ **已完成**（commit 8f65f83）
[server/api/genealogy/biblical-graph.get.ts](../../../server/api/genealogy/biblical-graph.get.ts) 接 `?tradition=catholic|orthodox|rabbinic`，預設 biblical only。在 server side merge JSONB（tradition_children/spouse/hide）進 children/spouse 統一視圖，pipeline mode-agnostic。

**D. 圖例** ⏳ **未完成** — legend 區增加 4 個 swatch 對應 4 種 tradition 顏色 + 預設說明。

**E. layout 問題**：
- ✅ **撒羅馬（亞拿之第三夫）** + **革羅罷（亞拿之第二夫）** 渲染問題 — 本次 session 修好。`placeOne` 內擴展 wifeIds：對每個 spine wife，把她「同代且不在 rowOf」的其他配偶 append 到婚姻列尾端（Trinubium extension）。同時新增 `placedAsRowSpouse` 集合，讓 kidWife 迴圈跳過已在上排渲染過的人物，避免 革羅罷 在 gen 74 重複出現。Catholic mode 現在 gen 73 列為 `撒羅馬 — 革羅罷 — 亞拿 — 約亞敬` 連續紅婚姻線。
  - **UI 妥協**：婚姻線是一條連續線，所以 革羅罷↔撒羅馬 之間視覺上像「兩人結婚」，但實際上他們都是娶亞拿。用戶接受此妥協（清楚過完全沒卡）。
- ⏳ **蘇比（亞拿之姊）不渲染** — 因為「兄妹」關係在現有 layout 沒有專門 logic（蘇比只是亞拿的姊妹，沒有父母 anchor）。需要加 sibling-via-shared-parent 處理 OR 直接把 蘇比 anchor 在某個 placeholder。
- ⏳ **Orthodox mode 中間「馬利亞」card 紅色 + 來路不明** — 在 J74 馬利亞 和 撒羅米 之間出現一張紅色（看似 catholic 傳統）「馬利亞」card，但 orthodox mode API filter 應該排除 catholic 人物。需確認該 card 究竟是 馬利亞-革羅罷（tradition=biblical 應為白底）還是其他。本次未深入。

### Task 5（小）：更新 dual-spine 圖例

目前 legend 4 條：spine A gold / spine B rose / 法律關係 gray-dashed / 聖靈感孕 red-dashed
切到 catholic / orthodox 模式時可能需要新增更多解釋。

---

## 關鍵 spec / 規則（不要違反）

1. **earliest biblical chapter wins** for names — Gen 36 > 1 Chr 1；Gen 46 > Num 26；例外只有亞伯拉罕、撒拉。
2. **不批次 propagate disambiguator**（per memory [feedback_biblical_name_rules.md](file://C:/Users/user/.claude/projects/c--Users-user-Desktop-know-graph-lab/memory/feedback_biblical_name_rules.md)）
3. **rename 一定要 token-boundary safe**（用 `c:\tmp\safe_rename.py`）— 之前用 substring replace 弄壞 7 個 `約雅斤` disambiguator，user 大怒。
4. **PowerShell 全授權**（per [feedback_powershell_full_auth.md](file://C:/Users/user/.claude/projects/c--Users-user-Desktop-know-graph-lab/memory/feedback_powershell_full_auth.md)）
5. **有改動自動 git push**（per [feedback_auto_push.md](file://C:/Users/user/.claude/projects/c--Users-user-Desktop-know-graph-lab/memory/feedback_auto_push.md)）

---

## 驗收

每次 layout / data 改完，用：
```pwsh
node scripts/biblical-shot.mjs --focus <人名> --out c:/tmp/<verify>.png
```
focus 可選：他拉 / 大衛 / 馬利亞 / 拿單 / 約瑟 / 雅各（馬但之子）/ etc。

切 tradition mode 後也要分別截圖：
```pwsh
node scripts/biblical-shot.mjs --focus 馬利亞 --out c:/tmp/cath-mary.png
# (還要在 script 裡加 --tradition catholic 等 args)
```

---

## 相關 scripts（可直接重用）

- `c:\tmp\safe_rename.py` — token-boundary rename（cor）
- `c:\tmp\david_wives.py` — David's 7 wives 插入範本
- `c:\tmp\solomon_daughters.py` — Solomon 兩女兒插入範本
- `c:\tmp\rename_shofa.py` — 朔法→朔罷 rename + 兒子順序驗證範本
- `c:\tmp\verify_gen36.py` / `c:\tmp\verify_gen46.py` / `c:\tmp\verify_gen10.py` — CUV2010 校對範本
- `c:\tmp\setup_traditions.py` — Phase 1 tradition tagging（已跑過）
- `c:\tmp\add_tradition_column.py` — schema migration（已跑過）
- `c:\tmp\add_tradition_jsonb_cols.py` — JSONB columns migration（本次，已跑過）
- `c:\tmp\phase2_catholic.py` — Phase 2 Catholic Trinubium 三人插入 + JSONB PATCH（本次，已跑過）
- `c:\tmp\phase3_orthodox.py` — Phase 3 Orthodox 五人插入 + JSONB PATCH（本次，已跑過）
- `c:\tmp\check_existing.py` / `check_gens.py` — debug 工具，列現有 row + 對應 generation
- `scripts/biblical-shot.mjs` — headless screenshot via magic-link cookie injection；新增 `--tradition catholic|orthodox|rabbinic` 旗標
- `scripts/biblical-12sons.mjs` — batch screenshot Jacob's 12 sons expansions

---

## 入門

1. 先讀此 SKILL.md 一遍
2. `git log --oneline -10` 看最近 commit
3. 跑 `node scripts/biblical-shot.mjs --out c:/tmp/start.png` 取得基線
4. 按 Task 1 → Task 2 → Task 3 → Task 4 順序做（Task 3 的 Phase 2/3 是 schema 改完後 INSERT 各 tradition 的人物；Task 4 的 UI 在 INSERT 完後做才能看到效果）
5. 每完成一個 task 就 commit + push
