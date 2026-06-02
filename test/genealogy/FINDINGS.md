# 譜系圖測試 + 修正報告（2026-06-02）

三棵脊柱樹元件第一次有測試覆蓋；本輪也依測試結果修了真正的 bug。

- 框架：`vitest` + `@nuxt/test-utils`（`environment: 'nuxt'`）+ happy-dom
- 跑法：`npm run test:run`（或 `npx vitest run test/genealogy`）
- 結果：**24 pass / 24**（含修正後的回歸測試）
- 測試 hook：三棵樹各加一行 `defineExpose({ cv, … })`（test-only，不影響渲染）

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

### B1 / I1（脆弱性）— 缺一個 waypoint 整棵空白、且無提示
- **症狀**：`SPINE_*_WAYPOINTS` 任一中文名解析不到（改名／錯字／漏 disambiguator），
  `spineFromWaypoints` 回 `[]` → 整棵樹空白，且**畫面全白、無任何訊息**，極難 debug。
- **修法（本輪先做「可診斷」，不動視覺）**：`spineFromWaypoints` 在 dev 模式下 `console.warn`
  指出「是哪個名字解析不到」或「哪一段斷裂」。樹仍會空白（降級渲染列為後續），但至少抓得到原因。
- **位置**：抽出的共用模組 [utils/genealogy/spine.ts](../../utils/genealogy/spine.ts)。
- **回歸測試**：biblical／islamic 的 broken fixture 斷言「cv 為 null **且** warn 點名了斷掉的 waypoint」。

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
1. **降級渲染**：waypoint 斷裂時畫出可解析的部分並標記斷點，而非整棵空白（B1/I1 的視覺版）。
2. **真實資料 overlap 測試**：把 `/api/genealogy/*-graph` 實際輸出存成 fixture 跑 collision —
   迷你 fixture 無重疊，真實密集資料才是 overlap bug 高發區。
3. （可選）E2 的「使用者手動展開長鏈時的遮蔽」可再加一支模擬 toggle 的測試（需 expose `toggleBranch`）。
