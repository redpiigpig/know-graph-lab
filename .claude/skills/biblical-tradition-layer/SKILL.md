---
name: biblical-tradition-layer
description: 聖經族譜的「教會傳統」視角圖層 — 早期教會（橘色，東西方共識）／天主教（紅）／東方教會（黃）／拉比傳統（藍）。包含資料表 schema、人物清單、UI 切換與配色設計、未完成 layout 修正項目。
---

# 聖經族譜 — 教會傳統視角圖層

> 接手用 skill。session 之前已做過 compaction，此檔記錄所有未完成項目與設計決策。

主要檔案：[components/genealogy/BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue)、
[server/api/genealogy/biblical-graph.get.ts](../../../server/api/genealogy/biblical-graph.get.ts)、
[scripts/biblical-shot.mjs](../../../scripts/biblical-shot.mjs)（headless screenshot 驗收）。

---

## 已完成（前次 session）

1. ✅ **Uniform NW+HG spacing for gen-N kid row** — commit 2514ed2；spine wives + 兄弟 + 兄弟妻同一個 (NW+HG=140px) slot 等距
2. ✅ **Joseph/Mary 婚姻線改 dashed-red** — commit 16e93e8；template `:stroke-dasharray="m.holy ? '6,4' : ''"`；圖例新增第 4 條
3. ✅ **David wives + sons mother attribution** — `c:\tmp\david_wives.py`；7 妻已 INSERT/PATCH，子→母 children 字串綁定
4. ✅ **朔法 → 朔罷** rename per 1 Chr 3:5 CUV2010 — `c:\tmp\rename_shofa.py` + safe_rename token-boundary logic
5. ✅ **Solomon 的女兒** 她法、巴實抹 (1 Kgs 4:11, 4:15) + 兩女婿 — `c:\tmp\solomon_daughters.py`
6. ✅ **Schema**: `biblical_people.tradition text NOT NULL DEFAULT 'biblical'` CHECK constraint added（值：`biblical`/`early_consensus`/`catholic`/`orthodox`/`rabbinic`）+ index
7. ✅ **Phase 1 tradition tagging** — `c:\tmp\setup_traditions.py`：亞拿、約亞敬 → `early_consensus`；NT 諸人物 → `biblical`；刪除 `馬利亞（克洛帕斯之妻）` dedupe；插入 `希里（路加 3:23）`

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

### Task 3: 教會傳統人物 INSERT（核心新功能）

**Tradition column 值**：
- `biblical` — 聖經（希伯來聖經 + 新約）— 預設顯示
- `early_consensus` — 早期教會東西方共識 → **橘色** card
- `catholic` — 天主教專有 → **紅色** card（西方 mode 才顯示）
- `orthodox` — 東方教會專有 → **黃色** card（東方 mode 才顯示）
- `rabbinic` — 拉比傳統 → **藍色** card（rabbinic mode 才顯示）

**已 INSERT/Tagged**（Phase 1）：
- 亞拿（聖母之母）→ `early_consensus`，spouse=約亞敬，child=馬利亞
- 約亞敬（聖母之父）→ `early_consensus`
- 撒迦利亞、以利沙白、施洗約翰、馬但（以律之孫）、雅各（馬但之子）→ `biblical`
- 馬利亞（革羅罷之妻）→ `biblical`（dedupe 完）
- 希里（路加 3:23）→ `biblical`（新插入，Mary's traditional father per Luke）

**還要 INSERT**（Phase 2 — Catholic / Trinubium Annae）：
| name_zh | tradition | parent | spouse | children | sources |
|---|---|---|---|---|---|
| 革羅罷（亞拿之第二夫） | catholic | — | 亞拿（聖母之母） | 馬利亞（革羅罷之妻） | 黃金傳說 |
| 撒羅馬（亞拿之第三夫） | catholic | — | 亞拿（聖母之母） | 馬利亞·撒羅米 | 黃金傳說 |
| 馬利亞·撒羅米 | catholic（部分東方也認） | 亞拿+撒羅馬 | 西庇太 | 大雅各、約翰 | 馬可 15:40、16:1（撒羅米 = 西庇太之妻，新約有，但「亞拿三次婚」的關聯是 Catholic medieval） |
| 西庇太 | biblical | — | 馬利亞·撒羅米 | 大雅各、約翰 | 太 4:21；可 1:19 |

**還要 INSERT**（Phase 3 — Orthodox / Epiphanian View）：
| name_zh | tradition | parent | spouse | children | sources |
|---|---|---|---|---|---|
| 撒羅米（約瑟之前妻） | orthodox | — | 約瑟（馬利亞之夫） | 雅各（主的兄弟）、約西、猶大、西門、亞西亞、呂底亞 | 雅各原始福音；木匠約瑟歷史 |
| 亞西亞（約瑟之女） | orthodox | 約瑟+撒羅米 | — | — | 木匠約瑟歷史 |
| 呂底亞（約瑟之女） | orthodox | 約瑟+撒羅米 | — | — | 木匠約瑟歷史 |
| 蘇比（亞拿之姊） | orthodox | (與亞拿同父母，傳統未具名) | — | 以利沙白（撒迦利亞之妻） | 東方傳統 |
| 革羅罷（約瑟之弟） | orthodox/early | 馬但（以律之孫） | 馬利亞（革羅罷之妻） | — | Hegesippus（Eusebius《教會史》III.11） — **與 Catholic 的「亞拿第二夫革羅罷」可能 conflict**，要 disambig |

**注意 conflict**：「革羅罷」在 Catholic = 亞拿第二夫；在 Hegesippus = 約瑟之弟。兩個傳統對「同名人物身份」不同。建議 INSERT 兩個獨立 entry，name_zh 各加 disambig。

**馬可 6:3 的耶穌兄弟**（雅各、約西、猶大、西門）：
- 新教 / 字面解經：約瑟+馬利亞親生 → 已在 DB `約瑟（馬利亞之夫）.children` 裡 ✅
- 天主教：馬利亞·克洛帕斯（亞拿次女）所生 → 在 catholic mode 應重 link 為馬利亞（革羅罷之妻）.children
- 東方教會：約瑟前妻撒羅米所生 → 在 orthodox mode 應重 link 為撒羅米（約瑟之前妻）.children

→ 因為 children 字串只能單一指向，這就需要在 **API 層** 依 mode 動態組裝 children 關係，而不是把所有 tradition 都塞進 children 字串。最簡單做法：保留 `biblical` 的 children 不變，新增一個 `tradition_children` JSON 欄位記錄各傳統的 override，或在 graph endpoint 依 mode 把 catholic/orthodox 的 children 加上去。

### Task 4: UI 改造（核心）

**檔案**：[components/genealogy/BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue)、`pages/genealogy/biblical.vue`（如果有 wrapper）、[server/api/genealogy/biblical-graph.get.ts](../../../server/api/genealogy/biblical-graph.get.ts)

**A. Tradition toggle UI**（在頁面右上或 legend 區）：
```
[聖經] [天主教傳統] [東方教會] [拉比傳統]
```
- 預設「聖經」(biblical only)
- 切「天主教」= biblical + early_consensus + catholic
- 切「東方教會」= biblical + early_consensus + orthodox
- 切「拉比傳統」= biblical + early_consensus + rabbinic
- 任何 mode 都顯示 biblical + early_consensus；只是再加上選定的 catholic/orthodox/rabbinic

**B. Card 配色**（在 [BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue) `cardClass` 或 `cardStyle`）：
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

**C. API filter**：
[server/api/genealogy/biblical-graph.get.ts](../../../server/api/genealogy/biblical-graph.get.ts) 接 `?tradition=catholic|orthodox|rabbinic|biblical`，依此 filter `biblical_people` 並調整 children 邏輯（catholic 模式時，馬可 6:3 兄弟改 link 到 馬利亞·克洛帕斯）。

**D. 圖例**：legend 區增加 4 個 swatch 對應 4 種 tradition 顏色 + 預設說明。

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
- `scripts/biblical-shot.mjs` — headless screenshot via magic-link cookie injection
- `scripts/biblical-12sons.mjs` — batch screenshot Jacob's 12 sons expansions

---

## 入門

1. 先讀此 SKILL.md 一遍
2. `git log --oneline -10` 看最近 commit
3. 跑 `node scripts/biblical-shot.mjs --out c:/tmp/start.png` 取得基線
4. 按 Task 1 → Task 2 → Task 3 → Task 4 順序做（Task 3 的 Phase 2/3 是 schema 改完後 INSERT 各 tradition 的人物；Task 4 的 UI 在 INSERT 完後做才能看到效果）
5. 每完成一個 task 就 commit + push
