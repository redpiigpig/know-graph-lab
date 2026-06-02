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

### 真實資料 overlap（新增回歸）— Biblical 5 處重疊待你決定
- 把 live `/api/genealogy/*-graph` 輸出存成快照跑碰撞檢查（密集真資料才抓得到）：
  - **Islamic**：186 卡，**0 重疊** ✓
  - **Episcopal**：1,585 卡，**0 重疊** ✓
  - **Biblical**：257 卡，**5 重疊**（密集區，卡距 < NW=120）：
    1. 哥轄 ↔ 俄南（猶大之子）／她瑪（同 row y≈3314）— 利未支 vs 猶大支子嗣子樹橫向相撞
    2. 施洗約翰 ↔ 猶大／西門（主的兄弟）（y≈10556）— 施洗約翰被擠進主的兄弟群組
    3. 蘇比（亞拿之姊）↔ 亞拿（聖母之母）（y≈10272，僅差 40px）— Trinubium 同列姊妹相疊
- 這些在「亂倫群組／同列配偶／Trinubium」等手調密集區，移哪張卡是主觀取捨、動了可能波及他處 →
  **先列出待你確認**，未動 layout。回歸測試以 baseline=5 守住「不要再變更多」；islamic/episcopal 鎖死 0。

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

## 後續（未做，待你決定）
1. **Biblical 5 處 overlap**：要不要動 layout 把它們撥開（哥轄/俄南/她瑪、施洗約翰群組、蘇比/亞拿）。
   屬密集區手調，建議逐處看畫面再決定撥哪張卡。
2. （可選）E2 的「使用者手動展開長鏈時的遮蔽」可再加一支模擬 toggle 的測試（需 expose `toggleBranch`）。
