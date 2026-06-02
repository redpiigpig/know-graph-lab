# 譜系圖測試 + 修正報告（2026-06-02）

三棵脊柱樹元件第一次有測試覆蓋；本輪也依測試結果修了真正的 bug。

- 框架：`vitest` + `@nuxt/test-utils`（`environment: 'nuxt'`）+ happy-dom
- 跑法：`npm run test:run`（或 `npx vitest run test/genealogy`）
- 結果：**28 pass / 28**（迷你 fixture + 真實資料快照回歸）
- 測試 hook：三棵樹各加一行 `defineExpose({ cv, … })`（test-only，不影響渲染）
- 真實資料快照：`test/genealogy/fixtures/snapshots/*.json`（從 live endpoint 抓；
  重抓 `node scripts/_snapshot_genealogy.mjs`，會用 .env 的 service role 臨時換 token）

---

## ✅ 已修

### E2（真 bug）— Episcopal focus-mode 把兄弟旁支誤藏
- **症狀**：分裂旁支（`is_split`，預設展開）的主教鏈，用 `chainEndY` 當 focus 範圍，
  而 `chainEndY` 含末尾一個 `BISH_VG`(90px) 空隙 → 多蓋約 90px，把掛在**更晚主教**
  （例：590 年才設立、attach 在下方的「坎特伯里」）的兄弟旁支整個判成重疊、`continue` 跳過、不渲染。
- **修法**：focus 範圍改用「最後一任主教卡底」`prevBottomY` 而非 `chainEndY`
  （[EpiscopalSpineTree.vue:888-896](../../components/genealogy/EpiscopalSpineTree.vue#L888-L896)）。
  長主教鏈的合理遮蔽不受影響，只移除了那段不存在的尾巴空隙。
- **回歸測試**：`both branch sees … render — no false focus-mode occlusion`。

### E3（一致性）— 旁支主教卡沒有 spineColor
- 主脊主教、使徒立座主教都有 `spineColor`（左側色條 + 標題著色），唯獨主脊旁支主教 `bbish_*` 沒有。
- **修法**：旁支主教卡補 `spineColor: sp.color`（[EpiscopalSpineTree.vue:881](../../components/genealogy/EpiscopalSpineTree.vue#L881)）。
- **回歸測試**：`branch bishop cards carry a spineColor`。

### B1 / I1（脆弱性）— 缺一個 waypoint 不再整棵空白（已做降級渲染）
- **原症狀**：`SPINE_*_WAYPOINTS` 任一中文名解析不到（改名／錯字／漏 disambiguator）→
  脊柱回 `[]` → 整棵樹空白，且**畫面全白、無任何訊息**，極難 debug。
- **修法（降級渲染）**：新 `resolveSpineWithDiagnostics`（[utils/genealogy/spine.ts](../../utils/genealogy/spine.ts)）
  在斷點**回傳能解析到的前綴**（而非 []），元件據此畫出可解析的部分，並在頂端顯示
  琥珀色 banner 標記「斷在哪兩站之間」；dev 模式同時 `console.warn` 點名。
  資料完整時 `full===true`、path 與舊版逐字相同 → happy path 不變。
- **回歸測試**：broken fixture 斷言「`hasSpine` true、`cv` 非 null、`spineDegraded` 有值、warn 點名斷點」；
  islamic 還斷言只畫到可解析的 4 站（阿丹→伊斯瑪儀）。

### 真實資料 overlap（新增回歸）— Biblical 5 處重疊 ✅ 已撥開
- 把 live `/api/genealogy/*-graph` 輸出存成快照跑碰撞檢查（密集真資料才抓得到）。
  原本：Islamic 186 卡 / Episcopal 1,585 卡 = 0；**Biblical 257 卡 = 5 重疊**。
- **根因**：5 處全是「force-expand（預設展開）的旁支 expansion 卡」落進主迴圈已排好的
  兄弟／妻位列，因為 force-expand 不像 user-expand 會推 occlusion box（[:1653](../../components/genealogy/BiblicalSpineTree.vue#L1653)）。
  作者本來就用 per-clan `FORCE_EXPAND_SHIFT_X` / `FORCE_EXPAND_MIN_GEN` 來撥開——只是這 3 個 clan 沒調夠。
- **修法**（[:1537-1539](../../components/genealogy/BiblicalSpineTree.vue#L1537-L1539)，整個 expansion 連同連接線一起平移，作者既有機制）：
  - `利未` shift 30 → **600**：摩西世系（哥轄→暗蘭→摩西/亞倫/米利暗）整支推到猶大子嗣列右側，
    自成一欄、與猶大世系留 ~570px 空槽（原本 30 只夠避深列 亞倫↔亞蘭，淺列 哥轄 仍卡在猶大列）。
  - `斯多蘭（亞拿之父）` 新增 shift **-220**：把其 expansion（含 蘇比、施洗約翰）往左推，
    一次解決 蘇比↔亞拿、施洗約翰↔西門/猶大（亞拿是 spine 妻、不在此 expansion，不動）。
- **結果**：三棵樹真實資料 **全 0 重疊**；回歸測試從 baseline≤5 收緊成**嚴格 0**。

### 去重 — `bfsPath` / `spineFromWaypoints`
- 原本在 Biblical 與 Islamic **逐字重複**。已抽到 [utils/genealogy/spine.ts](../../utils/genealogy/spine.ts) 共用，
  兩棵樹改 import（`resolveByName` 仍留各自元件，因為依賴各自的 name index）。
- 行為等價（兩棵樹的 spine 解析回歸測試全綠）。

---

## ↩️ 已撤回（前一版誤報）

### ~~E1 — 「預設全展開」~~（**不是 bug**）
- 第一版根據靜態初始值 `collapsedBranches = ref(new Set())` 判定「預設全展開、與註解矛盾」。
- **更正**：[EpiscopalSpineTree.vue:405-418](../../components/genealogy/EpiscopalSpineTree.vue#L405-L418) 有一個
  `watch(props.graph, …, { immediate: true })`，掛載即覆寫初始值，**刻意**設定預設策略：
  - 分裂旁支（`is_split`）→ 展開（並行對立支線，隨母教宗一起呈現，不需點開）
  - 設立旁支（非 `is_split`）→ 收起（只顯標頭）
  - 使徒 → 全收
- 空的靜態初始值只是 graph 載入前的暫態，被 watcher 立刻取代。屬**設計**，不修。
- 改以正確的回歸測試守住此策略：`split branches render expanded; 設立 branches collapsed`。

---

## 其他（現況正確，已有回歸防護）

- **Biblical**：雙脊 A/B 解析、共同主幹=亞當→大衛前綴、A/B 兩欄距=2·DIVERGE_X、**無卡片重疊**、
  脊柱人物妻子在左+婚姻線、婚姻線 x1<x2、無幽靈節點。
- **Islamic**：單脊 6 站解析、脊柱單欄對齊、**無重疊**、穆罕默德多妻單行（赫蒂徹首位最靠近）、無幽靈節點。
  另記契約：`view` 是 server-driven（頁面 refetch），元件內 `cv` 不因 view 重算 —— 不是 bug，但切 view 一定要 refetch。
- **Episcopal**：jesus/apostle/主脊主教渲染、`graph=null` 不 throw、各脊單欄、**無重疊**、無婚姻資料。

---

## 後續（未做，視需要）
1. （可選）E2 的「使用者手動展開長鏈時的遮蔽」可再加一支模擬 toggle 的測試（需 expose `toggleBranch`）。
2. （可選）force-expand 自動撥開：目前靠 per-clan 手調常數；之後可改成「force-expand 也按列
   占用偵測自動避讓」的通用邏輯，免得 DB 加人又要手調。
