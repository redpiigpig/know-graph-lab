---
name: islamic-tradition-layer
description: 伊斯蘭族譜的「教派傳統」視角圖層 — 古蘭明文（白）／順尼派（綠）／十二伊瑪目派（紅）／伊斯瑪儀派（紫）／栽德派（橙）／蘇菲（青）／歷史傳述（灰）。包含資料表 schema、人物清單（阿丹→穆罕默德+穆聖家族+12 伊瑪目）、UI 配色設計、未完成 API/Vue 項目。
---

# 伊斯蘭族譜 — 教派傳統視角圖層

> 姊妹 skill: [[biblical-tradition-layer]] — 兩套族譜共用相同 DB schema 模式（per-person `tradition` 列 + JSONB override 三件套），只是傳統值集合 + 視覺顏色不同。

主要檔案（規劃中，尚未實作）：
- `components/genealogy/IslamicSpineTree.vue`（待建，可大量複用 [BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue) 邏輯）
- `server/api/genealogy/islamic-graph.get.ts`（待建，鏡像 biblical-graph.get.ts）
- `pages/genealogy/islamic.vue`（待建，表格 CRUD）
- `pages/genealogy/islamic-tree.vue`（待建，族譜圖）
- `pages/genealogy/index.vue` 新增入口卡片（待建）

已完成腳本（c:\tmp）：
- `islamic_create_table.py` — 建立 `islamic_people` 表 + 索引 + updated_at trigger
- `islamic_seed_lineage.py` — 阿丹→穆罕默德 53 行
- `islamic_seed_family.py` — 穆聖叔伯姑姨、12 妻、7 子女、阿里+12 伊瑪目（含 Ismaili/Zaidi 分支）42 行

---

## 🗂 資料表 schema

`islamic_people`（mirror of `biblical_people`，差異：多 `name_ar` / `kunya`，tradition 值集合不同）：

| 欄位 | 型別 | 說明 |
|---|---|---|
| id | uuid | PK |
| name_zh | text | 中文主名，含消歧義 e.g.「阿里（艾比·塔利卜之子）」 |
| name_ar | text | 阿拉伯文原名 e.g. علي بن أبي طالب |
| name_en | text | 拉丁拼寫 e.g. "Ali ibn Abi Talib" |
| kunya | text | 阿拉伯式父子名 e.g. "Abu al-Hasan"（阿里之 kunya） |
| gender | text | 男／女 |
| nationality | text | 阿拉伯人／以色列人／古先民／猶太人（後歸信）／科普特人 |
| birth_year / death_year / child_year / age | int | 多為空，部分晚期伊瑪目可填 |
| spouse | text | `、` 分隔；存對方 name_zh |
| children | text | `、` 分隔；存對方 name_zh |
| sources | text | 古蘭章節 ／ 聖訓集 ／ 史料引用 |
| notes | text | |
| generation | int | 阿丹 = 1；穆聖 = 44；末伊瑪目馬赫迪 = 54 |
| sort_order | int | 同 gen 內排序 hint |
| **tradition** | text | NOT NULL；check constraint 7 值（見下） |
| **tradition_children** | jsonb | per-tradition override，加入 children |
| **tradition_spouse** | jsonb | per-tradition override，加入 spouse |
| **tradition_hide_children** | jsonb | per-tradition 隱藏 children（伊瑪目繼承衝突用） |
| created_at / updated_at | timestamptz | 後者用 trigger 自動更新 |

CHECK constraint:
```sql
tradition IN ('quranic','sunni','shia_twelver','shia_ismaili','shia_zaidi','sufi','historical')
```

---

## 🎨 七種傳統 — 顏色與含義

| Tradition | 含義 | 卡片色 | tailwind 建議 |
|---|---|---|---|
| `quranic` | 古蘭經明文，所有教派共識（25 先知 + 古蘭點名人物） | **白底**（預設） | `bg-white border-gray-200` |
| `sunni` | 順尼派傳承（Sira / Hadith / 史傳） | **綠** | `bg-emerald-50 border-emerald-300` |
| `shia_twelver` | 十二伊瑪目派專有（含 11 位後伊瑪目 + 隱遁 Mahdi） | **紅** | `bg-rose-50 border-rose-300` |
| `shia_ismaili` | 伊斯瑪儀派（七派／法蒂瑪王朝主流，於嘉法爾·薩迪克分支） | **紫** | `bg-purple-50 border-purple-300` |
| `shia_zaidi` | 栽德派（葉門主流，於宰因·阿比丁分支） | **橙** | `bg-orange-50 border-orange-300` |
| `sufi` | 蘇菲傳承（聖徒鏈／tariqa silsila，尚未填入資料） | **青** | `bg-teal-50 border-teal-300` |
| `historical` | 史傳但古蘭未明文（阿丹↔努哈中段人物、伊斯瑪儀↔阿德南斷層猜測） | **灰** | `bg-gray-50 border-gray-300` |

> 配色避開 biblical-tradition-layer 使用的 amber（spine A）／rose（spine B 同 rose-50 衝突需注意）。
> 紅色 rose-50 已用於 biblical 女性卡 + 十二派伊瑪目；同一頁不會混用所以無衝突。

---

## 📜 視圖機制（規劃，鏡像 biblical 的 `?view=` 邏輯）

URL：`/genealogy/islamic-tree?view=quranic|sunni|shia_twelver|shia_ismaili|shia_zaidi`

規則（**累進納入**）：

| view | 顯示哪些 tradition 的人 | JSONB override 套用 |
|---|---|---|
| `quranic`（預設） | `quranic` only | 無 |
| `sunni` | `quranic` + `sunni` + `historical` | sunni override |
| `shia_twelver` | 上述 + `shia_twelver` | shia_twelver override |
| `shia_ismaili` | quranic + sunni + `shia_ismaili` | shia_ismaili override |
| `shia_zaidi` | quranic + sunni + `shia_zaidi` | shia_zaidi override |

> 預設 view 用 `quranic` 而非 `sunni`，是因為穆斯林世界對「古蘭明文」普世共識最強，可作中立起點。
> `sunni`/`shia_*` 不互相納入彼此的伊瑪目人物（避免視覺擠 + 各派視角互不混雜）。

切換點：嘉法爾·薩迪克 (gen 48) 之後 — 十二派接穆薩·卡齊姆 (49)、伊斯瑪儀派接伊斯瑪儀·伊本·嘉法爾 (49)。

---

## 🌳 已填入的人物世系（aggregated 95 rows）

### 阿丹 → 努哈（gen 1-10，10 代）
阿丹 → 施特 → 阿努施 → 蓋南 → 馬哈萊勒 → 雅利得 → **伊德里斯**（古蘭 19:56-57，與聖經以諾對應）→ 馬突舍拉 → 拉麥（努哈之父）→ **努哈**（古蘭 11:25-49 整章 71）

哈娃 (gen 1，sunni) 為阿丹之妻。

### 努哈 → 易卜拉欣（gen 11-20，10 代）
閃（努哈之子）→ 阿爾法夏德 → 沙拉赫 → **阿比爾**（即古蘭中先知呼德？）→ 法利格 → 拉烏 → 薩魯格 → 納霍爾（易卜拉欣之祖父）→ **阿札爾（易卜拉欣之父）**（古蘭 6:74，偶像匠人）→ **易卜拉欣**（古蘭 2:124-141、19:41-49，五大堅韌使者）

易卜拉欣之兩妻：
- 撒拉（易司哈格之母，gen 20）
- 哈哲爾（伊斯瑪儀之母，gen 20）

### 兩支分流：以色列家 vs. 阿拉伯家

**易司哈格線**（gen 21+，僅插入直系做兄弟對照）：
- 易司哈格 (gen 21) → 葉爾孤白（即雅各／以色列，gen 22）→ 優素福（gen 23）+ 11 兄弟

**伊斯瑪儀線**（gen 21+，穆聖直系）：
- 伊斯瑪儀 (gen 21) → 蓋達爾／納比特 (gen 22)
- **gap：蓋達爾 → 阿德南** — 古典史學列 ~30 代名字但**權威性極低**；穆聖明訓「النساب يكذبون」（譜學家在阿德南之後即妄言）。本表**省略中段，從蓋達爾直接接阿德南**，僅在 sources 註明。

### 阿德南 → 穆罕默德（gen 23-44，22 代）

依 Ibn Hisham《Sirat Rasul Allah》，well-attested：

阿德南 → 馬阿德 → 尼扎爾 → 穆達爾 → 易勒亞斯 → 穆德里卡 → 胡扎伊瑪 → 基納納 → **納德爾（古萊什之祖）** → 馬利克 → 菲赫爾 → 嘎利卜 → 盧艾 → 卡布 → 穆拉 → 基拉卜 → **古蘇**（統一古萊什、掌克爾白）→ 阿卜杜·瑪納夫 → **哈希姆**（哈希姆家族祖）→ **阿卜杜·穆塔利卜**（穆聖之祖父）→ 阿卜杜拉（穆聖之父，於穆聖出生前逝）+ 阿米娜（穆聖之母）→ **穆罕默德** (gen 44, ﷺ)

### 穆聖之父輩（Banu Hashim 兄弟，gen 43）

阿卜杜·穆塔利卜之子（穆聖之父 + 諸叔父）：
- **阿卜杜拉（穆聖之父）** — quranic（穆聖之父）
- **艾比·塔利卜** — 撫養孤兒穆聖；阿里之父；什葉派視為信士
- **阿巴斯（穆聖之叔父）** — 阿拔斯王朝之祖
- **哈姆扎（穆聖之叔父）** — 「眾烈士之主」，伍侯德戰役殉教
- **艾布·拉哈布** — 古蘭 111 章詛咒之對象（quranic 但反面人物）
- **烏姆·賈米爾** — 艾布·拉哈布之妻，古蘭 111:4-5「擔柴的婦人」

### 穆聖之 12 位妻（信士之母，Ummahat al-Mu'minin，gen 44）

按嫁穆聖順序：

1. **赫蒂徹**（首妻，所有子女除易卜拉欣之母）— sunni（古蘭未直書名）
2. 蘇黛
3. **阿伊莎**（艾布·伯克爾之女）
4. 哈芙莎（歐麥爾之女）
5. 宰娜卜·賓特·胡扎伊瑪（「貧民之母」，婚後三月即逝）
6. 烏姆·薩拉瑪（本名欣德）
7. **宰娜卜·賓特·賈赫什**（古蘭 33:37-38 明文）— **quranic**
8. 朱韋里葉
9. 烏姆·哈比巴（艾布·蘇富揚之女）
10. 莎菲婭（猶太納迪爾族）
11. 邁穆娜
12. **瑪利亞·科普特**（埃及妾，易卜拉欣之母）

### 穆聖之 7 子女（gen 45）

| 名 | 母 | tradition |
|---|---|---|
| 嘎西姆（穆聖之子）| 赫蒂徹 | sunni（夭折） |
| 宰娜卜（穆聖之女）| 赫蒂徹 | sunni |
| 魯蓋葉（穆聖之女）| 赫蒂徹 | sunni（嫁奧斯曼） |
| 烏姆·庫勒蘇姆（穆聖之女）| 赫蒂徹 | sunni（魯蓋葉逝後嫁奧斯曼） |
| **法蒂瑪（穆聖之女）** | 赫蒂徹 | **quranic**（嗣裔之源，嫁阿里） |
| 阿卜杜拉（穆聖之子）| 赫蒂徹 | sunni（夭折，又名塔伊布／塔希爾） |
| 易卜拉欣（穆聖之子）| 瑪利亞·科普特 | sunni（18 月夭折） |

### 阿里 + 法蒂瑪 → 12 伊瑪目鏈

什葉派伊瑪目傳承（哈姆扎之姪 / 穆聖之堂弟阿里為第一任）：

```
1. 阿里（艾比·塔利卜之子, gen 43）  ← quranic（古蘭 5:55 什葉派指涉）+ 順尼派第四哈里發
   └─ 配偶: 法蒂瑪（穆聖之女, gen 45）  跨代婚姻（堂叔娶姪女輩）
2. 哈桑·伊本·阿里（gen 45）          ← shia_twelver；順尼派視為第五哈里發
3. 侯賽因·伊本·阿里（gen 45）        ← shia_twelver；卡爾巴拉殉教（680 CE）
4. 阿里·宰因·阿比丁（gen 46）        ← shia_twelver；卡爾巴拉唯一倖存男丁
   ├─ 5. 穆罕默德·巴基爾（gen 47）    ← shia_twelver
   │   └─ 6. 嘉法爾·薩迪克（gen 48）  ← shia_twelver / shia_ismaili 共主
   │       ├─ 7a. 穆薩·卡齊姆（gen 49） ← shia_twelver（巴格達獄中殉教）
   │       │   └─ 8. 阿里·里達（gen 50）  ← shia_twelver
   │       │       └─ 9. 穆罕默德·賈瓦德（gen 51）
   │       │           └─ 10. 阿里·哈迪（gen 52）
   │       │               └─ 11. 哈桑·阿斯卡里（gen 53）
   │       │                   └─ 12. 穆罕默德·馬赫迪（gen 54）← 隱遁伊瑪目
   │       └─ 7b. 伊斯瑪儀·伊本·嘉法爾（gen 49） ← shia_ismaili 分支
   │           └─ 穆罕默德·伊本·伊斯瑪儀（gen 50） ← shia_ismaili 隱沒伊瑪目
   └─ 宰德·伊本·阿里（gen 47）        ← shia_zaidi 分支（庫法起義殉教 740 CE）
宰娜卜·賓特·阿里（gen 45）— shia_twelver；卡爾巴拉後率女眷俘往大馬士革，面斥葉齊德
```

---

## ⚠️ 設計決策／資料原則

### 為何另建 `islamic_people` 而非與 `biblical_people` 共用？

兩套族譜雖在阿丹→易卜拉欣段重疊（阿當/阿丹、努哈/挪亞、易卜拉欣/亞伯拉罕 等），但：

1. **代數不同** — 伊斯蘭加入了阿丹↔諾哈中段（伊德里斯線），且阿德南↔伊斯瑪儀有 gap 處理；biblical_people 用嚴格希伯來聖經代數。
2. **名稱不同** — 中文音譯來源不同（穆斯林傳統 vs. 和合本／思高本），混用會亂。
3. **同名異人** — 易卜拉欣（穆聖之子，44 gen）vs. 易卜拉欣（先知亞伯拉罕，20 gen）；法蒂瑪（穆聖之女）vs. 法蒂瑪·賓特·艾賽德（阿里之母）。需要消歧義。
4. **傳統值集合不同** — biblical 用 catholic/orthodox/early_consensus/rabbinic；islamic 用 sunni/shia_*。混在一張表上 CHECK constraint 太亂。

> 兩表共用：JSONB override 三件套設計、parent-child 用 `children` text 串、generation-int 排版邏輯、消歧義括號慣例。

### 古蘭未提及姓名的人物（如努哈之妻、易卜拉欣之父名「阿札爾」是古蘭名）

- 古蘭明文 → `quranic`
- 古蘭隱指（如哈娃、撒拉、哈哲爾，古蘭描述但未直書名）→ 此處仍標 `quranic`（穆斯林傳統視為古蘭等同來源），若不確定可降為 `sunni`
- 純《先知故事》（伊本·凱西爾）史傳 → `sunni`
- 阿丹↔努哈中段、伊斯瑪儀↔阿德南斷層 → `historical`（灰色，標記不確定）

### 「易卜拉欣之父」古蘭名 vs. 聖經名

- 古蘭 6:74 稱阿札爾 (آزر)
- 《創世記》11:26 稱他拉 (תֶּרַח, Terah)
- 部分穆斯林學者認為阿札爾為他拉之別名或頭銜（拜偶像匠人之意）
- 本表用「阿札爾（易卜拉欣之父）」為主名，sources 註明兩源

### 阿德南↔伊斯瑪儀斷層

- Ibn Hisham 列出的中段 ~30 代（蓋達爾 → 哈馬爾 → 納比特2 → 薩拉門 → ...）權威性極低
- 穆聖本人停在阿德南並告誡勿增添
- 本表選擇**不插入虛構代數**，直接 蓋達爾 (gen 22) ⟶ 阿德南 (gen 23) 並在阿德南 sources 註明
- 若日後要展示「傳統補白」可另插一批 `tradition='historical'` 的 placeholder 人物

### 跨代婚姻處理（阿里 gen 43 娶 法蒂瑪 gen 45）

- 阿里為穆聖堂弟（艾比·塔利卜之子，gen 43）
- 法蒂瑪為穆聖之女（gen 45）
- 兩人婚姻為穆聖在世時親自主婚
- biblical-tradition-layer 已有同類處理（如猶大-她瑪：跨代亂倫案例），參考 `layoutSubtree` 的 `minGen` 機制：傳 `gen+1` 強制兒女視覺世代 ≥ 父代+1

---

## 🚧 待辦清單

### Task 1: 表格 CRUD 頁面 `pages/genealogy/islamic.vue`

複製 [pages/genealogy/biblical.vue](../../../pages/genealogy/biblical.vue) 結構，僅換 endpoint 至 `/api/genealogy/islamic-people`，欄位多加 name_ar / kunya。

### Task 2: API endpoints

新建：
- `server/api/genealogy/islamic-people.get.ts` — 列表
- `server/api/genealogy/islamic-people/[id].patch.ts` — 更新
- `server/api/genealogy/islamic-people/[id].delete.ts` — 刪除
- `server/api/genealogy/islamic-graph.get.ts` — graph view，套 `?view=` filter + JSONB merge

mirror 完全可從 biblical-* 複製 + sed。

### Task 3: Tree component `IslamicSpineTree.vue`

複用 `BiblicalSpineTree.vue` 1700+ 行邏輯。主要差異：

- **單 spine** 即可（不需 dual-spine A/B），穆聖只有一條直系；對比 biblical 有馬太/路加雙譜系
- `traditionColors` 改 5 色：`quranic`/`sunni`/`shia_twelver`/`shia_ismaili`/`shia_zaidi`/`sufi`/`historical`
- 線條規則同 biblical（紅 = 夫妻橫向；灰 = T-bar drop）
- spine 終點 = 穆罕默德（gen 44）vs. biblical 終點 = 馬利亞（gen 74）
- 後續 12 伊瑪目鏈作為穆聖→法蒂瑪 (gen 45) 的下分支展開（阿里為穆聖堂弟接入點）

### Task 4: 路由入口

更新 [pages/genealogy/index.vue](../../../pages/genealogy/index.vue) 新增第 4 張卡片：

```vue
<NuxtLink to="/genealogy/islamic" ...>
  <div class="text-3xl">☪</div>
  <div>
    <div>伊斯蘭族譜</div>
    <div>阿丹至穆罕默德 + 12 伊瑪目</div>
  </div>
</NuxtLink>
```

### Task 5: 視圖切換 widget

在 islamic-tree.vue 加浮動 toggle（鏡像 biblical-tree 的「耶穌聖家詮釋」widget）：

```
[古蘭] [順尼] [十二派] [伊斯瑪儀] [栽德]
```

預設「古蘭」，URL `?view=quranic` 同步。

### Task 6: 圖例

左下 Legend：
- 7 色 swatch（含 `sufi` 預留）
- 紅實線 = 婚姻
- 灰虛線 = T-bar / 下傳
- spine guide color（穆聖直系用 emerald 綠？）

### Task 7（資料補完）

- 伊瑪目之配偶與其他子女（目前只填了直系傳承的伊瑪目）
- 主要哈里發：艾布·伯克爾、歐麥爾、奧斯曼、阿里（已填）
- 早期蘇菲聖徒鏈（Junayd, Bayazid, ...）→ tradition='sufi'
- 烏麥葉／阿拔斯／法蒂瑪王朝主要君主（與本族譜的血緣分支）

---

## 🔑 關鍵 spec / 規則

1. **古蘭優先** — 古蘭明文人物（25 先知 + 古蘭點名者）必為 `quranic`，不可降階為 `sunni`
2. **不批次 propagate disambiguator** — 套用 [feedback_biblical_name_rules](../../../memory/feedback_biblical_name_rules.md) 同則
3. **中文音譯遵循中國穆斯林傳統** — 阿丹／努哈／易卜拉欣／伊斯瑪儀／穆罕默德／阿里／法蒂瑪／侯賽因 等通行譯名；遇到罕見人物可參考《伊斯蘭百科全書》中文版或《穆罕默德傳》（Martin Lings 馬丁·林斯 中譯本）
4. **kunya（父子稱呼）** — 阿拉伯人「Abu X / Umm X / Ibn X / Bint X」是文化專有，獨立放 `kunya` 欄不要混入主名
5. **gen 計數** — 阿丹 = 1；穆罕默德 = 44；末伊瑪目 = 54。**不要重編**（已 freeze）
6. **PowerShell 全授權**（per [feedback_powershell_full_auth](../../../memory/feedback_powershell_full_auth.md)）
7. **有改動自動 git push**（per [feedback_auto_push](../../../memory/feedback_auto_push.md)）

---

## 📁 相關 scripts（可直接重用 / 改寫）

- `c:\tmp\islamic_create_table.py` — schema migration（已跑過）
- `c:\tmp\islamic_seed_lineage.py` — 阿丹→穆罕默德 53 行（已跑過）
- `c:\tmp\islamic_seed_family.py` — 穆聖叔伯 + 12 妻 + 7 子女 + 12 伊瑪目 42 行（已跑過）
- `c:\tmp\inspect_biblical_schema.py` — 範本，列任意 supabase 表 column

未來新批次（如蘇菲聖徒鏈、伊瑪目其他子女）依此模式：fetch_all → set existing → INSERT skip-if-exists。

---

## 📚 主要史料引用

- **古蘭經** — 默認以「中文譯解古蘭經」（馬堅譯本）為中文人名來源
- **Ibn Hisham 《Sirat Rasul Allah》** — 阿德南→穆聖譜系權威
- **Ibn Kathir 《先知故事》（قصص الأنبياء）** — 阿丹→努哈→易卜拉欣段
- **Tarikh al-Tabari** — 古典通史對照
- **什葉派《光輝之書》（نهج البلاغة Nahj al-Balagha）** — 阿里言行集；伊瑪目資料
- **《卡爾巴拉述》** — 侯賽因殉教 + 宰娜卜事蹟
- **Martin Lings 《Muhammad: His Life Based on the Earliest Sources》** — 英文／中文現代彙整

---

## 入門

1. 先讀此 SKILL.md
2. 跑 `python c:/tmp/inspect_biblical_schema.py` 改寫成 `islamic_people` 查表，看當前 95 行資料
3. 依 Task 1-7 順序做（先 API + 表格頁，再 tree 組件，最後 widget + legend）
4. 每完成一個 task 就 commit + push
5. 視覺驗收可仿 `scripts/biblical-shot.mjs` 寫 `scripts/islamic-shot.mjs`
