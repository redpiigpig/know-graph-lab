---
name: islamic-tradition-layer
description: 伊斯蘭族譜的「教派傳統」視角圖層 — 古蘭明文（白）／順尼派（綠）／十二伊瑪目派（紅）／伊斯瑪儀派（紫）／栽德派（橙）／蘇菲（青）／歷史傳述（灰）。包含資料表 schema、人物清單（阿丹→穆罕默德+穆聖家族+12 伊瑪目）、UI 配色設計、表格 CRUD + 族譜圖 + view 切換 widget（皆已上線）。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 伊斯蘭族譜 — 教派傳統視角圖層

> 姊妹 skill: [[biblical-tradition-layer]] — 兩套族譜共用相同 DB schema 模式（per-person `tradition` 列 + JSONB override 三件套），只是傳統值集合 + 視覺顏色不同。

> 🔧 **不知道怎麼處理時請看 biblical**：Islamic 族譜的 component / API / page / seed 結構全部 mirror biblical 那邊的版本。任何 layout、collapse、cross-gen 婚姻、♻ 同人標記、subtree pathFilter、widget 模式…遇到不確定的問題，**先讀 [components/genealogy/BiblicalSpineTree.vue](../../../components/genealogy/BiblicalSpineTree.vue)** 找到對應 pattern 再移植。biblical 已經處理過絕大多數 edge case（如 利亞 在 拉班 之女 + 雅各 之妻 兩處同時出現的 ♻ 同人標記）。

主要檔案（皆已就位）：
- ✅ [components/genealogy/IslamicSpineTree.vue](../../../components/genealogy/IslamicSpineTree.vue) — 單 spine 族譜圖組件，pan/zoom + 卡片色 + view widget + legend
- ✅ [server/api/genealogy/islamic-graph.get.ts](../../../server/api/genealogy/islamic-graph.get.ts) — `?view=` filter + JSONB tradition merge（鏡像 biblical-graph）
- ✅ [server/api/genealogy/islamic-people.get.ts](../../../server/api/genealogy/islamic-people.get.ts) — 列表
- ✅ [server/api/genealogy/islamic-people.post.ts](../../../server/api/genealogy/islamic-people.post.ts) — 新增
- ✅ [server/api/genealogy/islamic-people/[id].patch.ts](../../../server/api/genealogy/islamic-people/[id].patch.ts) — 更新
- ✅ [server/api/genealogy/islamic-people/[id].delete.ts](../../../server/api/genealogy/islamic-people/[id].delete.ts) — 刪除
- ✅ [pages/genealogy/islamic.vue](../../../pages/genealogy/islamic.vue) — 表格 CRUD（新增/編輯/刪除 modal）
- ✅ [pages/genealogy/islamic-tree.vue](../../../pages/genealogy/islamic-tree.vue) — 族譜圖頁 + URL `?view=` 同步
- ✅ [pages/genealogy/index.vue](../../../pages/genealogy/index.vue) — 入口卡片 ☪「伊斯蘭族譜」(emerald hover)

已完成腳本（c:\tmp）：
- `islamic_create_table.py` — 建立 `islamic_people` 表 + 索引 + updated_at trigger
- `islamic_seed_lineage.py` — 阿丹→穆罕默德 53 行
- `islamic_seed_family.py` — 穆聖叔伯姑姨、12 妻、7 子女、阿里+12 伊瑪目（含 Ismaili/Zaidi 分支）42 行
- `islamic_seed_prophets.py` — 以色列先知直系 37 行（2026-05-16）：利未/猶大、穆薩+哈倫、達烏德+蘇萊曼、Davidic 王朝 12 代、麥爾彥+爾撒、宰凱里雅+葉哈雅
- `islamic_link_zechariah.py` — patch 哈倫.children += 宰凱里雅（亞倫祭司世系約 21 代略過）

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
| generation | int | 阿丹 = 1；穆聖 = 49；末伊瑪目馬赫迪 = 59 |
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
| `quranic` | `quranic` only — 25 先知 + 古蘭點名人物（約 17 人，spine 不連貫） | 無 |
| `sunni`（預設） | `quranic` + `sunni` + `historical` | sunni override |
| `shia_twelver` | 上述 + `shia_twelver` | shia_twelver override |
| `shia_ismaili` | quranic + sunni + `shia_ismaili` | shia_ismaili override |
| `shia_zaidi` | quranic + sunni + `shia_zaidi` | shia_zaidi override |

> 預設改為 `sunni`，因為 spine 必經中段（阿丹↔努哈 中的 伊德里斯系；阿德南↔穆罕默德 22 代）皆是 sunni 傳述。`quranic` only 會讓 BFS 找不到完整路徑（17 人散落不連貫），保留作為「只看古蘭明文」嚴格過濾選項。
> `sunni`/`shia_*` 不互相納入彼此的伊瑪目人物（避免視覺擠 + 各派視角互不混雜）。

切換點：嘉法爾·薩迪克 (gen 53) 之後 — 十二派接穆薩·卡齊姆 (54)、伊斯瑪儀派接伊斯瑪儀·伊本·嘉法爾 (54)。

---

## 🌳 已填入的人物世系（aggregated 278 rows）

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
- **蓋達爾 → 阿德南 中段**（gen 23-27，5 代史傳補白）：古典史學列 ~30 代名字諸版本互異，本表選一個常見「Madinian short list」5 名變體：
  哈馬爾 (23) → 薩拉曼 (24) → 耶薩 (25) → 烏達德 (26) → 烏德 (27)
  皆 tradition='historical'（灰色，表傳統補白權威性低）。穆聖訓示「النساب يكذبون」針對的是「在阿德南之後追溯」的妄言，而非不可記載中段；既然 Ibn Hisham 等史家已列名，記入並以 `historical` 標示即為合宜。

### 阿德南 → 穆罕默德（gen 28-49，22 代）

依 Ibn Hisham《Sirat Rasul Allah》，well-attested：

阿德南 → 馬阿德 → 尼扎爾 → 穆達爾 → 易勒亞斯 → 穆德里卡 → 胡扎伊瑪 → 基納納 → **納德爾（古萊什之祖）** → 馬利克 → 菲赫爾 → 嘎利卜 → 盧艾 → 卡布 → 穆拉 → 基拉卜 → **古蘇**（統一古萊什、掌克爾白）→ 阿卜杜·瑪納夫 → **哈希姆**（哈希姆家族祖）→ **阿卜杜·穆塔利卜**（穆聖之祖父）→ 阿卜杜拉（穆聖之父，於穆聖出生前逝）+ 阿米娜（穆聖之母）→ **穆罕默德** (gen 49, ﷺ)

### 穆聖之父輩（Banu Hashim 兄弟，gen 48）

阿卜杜·穆塔利卜之子（穆聖之父 + 諸叔父）：
- **阿卜杜拉（穆聖之父）** — quranic（穆聖之父）
- **艾比·塔利卜** — 撫養孤兒穆聖；阿里之父；什葉派視為信士
- **阿巴斯（穆聖之叔父）** — 阿拔斯王朝之祖
- **哈姆扎（穆聖之叔父）** — 「眾烈士之主」，伍侯德戰役殉教
- **艾布·拉哈布** — 古蘭 111 章詛咒之對象（quranic 但反面人物）
- **烏姆·賈米爾** — 艾布·拉哈布之妻，古蘭 111:4-5「擔柴的婦人」

### 穆聖之 12 位妻（信士之母，Ummahat al-Mu'minin，gen 49）

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

### 穆聖之 7 子女（gen 50）

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
1. 阿里（艾比·塔利卜之子, gen 48）  ← quranic（古蘭 5:55 什葉派指涉）+ 順尼派第四哈里發
   └─ 配偶: 法蒂瑪（穆聖之女, gen 50）  跨代婚姻（堂叔娶姪女輩）
2. 哈桑·伊本·阿里（gen 50）          ← shia_twelver；順尼派視為第五哈里發
3. 侯賽因·伊本·阿里（gen 50）        ← shia_twelver；卡爾巴拉殉教（680 CE）
4. 阿里·宰因·阿比丁（gen 51）        ← shia_twelver；卡爾巴拉唯一倖存男丁
   ├─ 5. 穆罕默德·巴基爾（gen 52）    ← shia_twelver
   │   └─ 6. 嘉法爾·薩迪克（gen 53）  ← shia_twelver / shia_ismaili 共主
   │       ├─ 7a. 穆薩·卡齊姆（gen 54） ← shia_twelver（巴格達獄中殉教）
   │       │   └─ 8. 阿里·里達（gen 55）  ← shia_twelver
   │       │       └─ 9. 穆罕默德·賈瓦德（gen 56）
   │       │           └─ 10. 阿里·哈迪（gen 57）
   │       │               └─ 11. 哈桑·阿斯卡里（gen 58）
   │       │                   └─ 12. 穆罕默德·馬赫迪（gen 59）← 隱遁伊瑪目
   │       └─ 7b. 伊斯瑪儀·伊本·嘉法爾（gen 54） ← shia_ismaili 分支
   │           └─ 穆罕默德·伊本·伊斯瑪儀（gen 55） ← shia_ismaili 隱沒伊瑪目
   └─ 宰德·伊本·阿里（gen 52）        ← shia_zaidi 分支（庫法起義殉教 740 CE）
宰娜卜·賓特·阿里（gen 50）— shia_twelver；卡爾巴拉後率女眷俘往大馬士革，面斥葉齊德
```

### 古萊什部族分支（Quraysh sub-clans）— Rashidun 三哈里發接入

```
阿卜杜·瑪納夫 (gen 45)
├─ 哈希姆 (46, spine)
└─ 阿卜杜·夏姆斯 (46) → 倭馬亞 (47)
   ├─ 艾布·阿斯·伊本·倭馬亞 (48)
   │  ├─ 阿凡 (49) → 奧斯曼·伊本·阿凡 (gen 50)  ← 第三任正統哈里發
   │  └─ 哈卡姆 (49) → 馬爾萬一世 (50)            ← Marwanid 倭馬亞支
   └─ 哈爾卜 (48) → 阿布·蘇富揚 (49)
                   ├─ 穆阿維葉一世 (50)             ← Sufyanid 倭馬亞支
                   └─ 烏姆·哈比巴 (穆聖之妻)

穆拉 (gen 42) → 泰因·伊本·穆拉 (43, Banu Taym 祖) → 薩阿德 → 卡布 → 阿穆爾 → 阿米爾 → 阿布·古哈法 (48) → 艾布·伯克爾 (49)  ← 第一任正統哈里發

卡布·伊本·盧艾 (gen 41) → 阿迪·伊本·卡布 (42, Banu Adi 祖) → 拉扎赫 → 里亞赫 → 阿卜杜拉 → 古爾特 → 努法伊勒 → 哈塔卜 (48) → 歐麥爾·伊本·哈塔卜 (49)  ← 第二任正統哈里發
```

### 倭馬亞王朝（Umayyad Caliphate, 661-750 CE，14 任哈里發）

```
Sufyanid 支系 (3 任):
  1. 穆阿維葉一世   (50, 661-680)
  2. 葉齊德一世     (51, 680-683)  — 卡爾巴拉下令
  3. 穆阿維葉二世   (52, 683-684)  — 線結束

Marwanid 支系 (11 任):
  4. 馬爾萬一世     (50, 684-685)
  5. 阿卜杜勒·馬利克 (51, 685-705)  — 建岩石圓頂
  6. 瓦利德一世     (52, 705-715)
  7. 蘇萊曼         (52, 715-717)
  8. 歐麥爾二世     (52, 717-720)  — 「第五正統哈里發」
  9. 葉齊德二世     (52, 720-724)
  10. 希沙姆        (52, 724-743)
  11. 瓦利德二世    (53, 743-744)
  12. 葉齊德三世    (53, 744)
  13. 易卜拉欣      (53, 744)
  14. 馬爾萬二世    (52, 744-750)  — 末任，阿拔斯革命中被殺
```

### 阿拔斯王朝（Abbasid Caliphate, 749-1258 CE，37 任巴格達哈里發）

```
阿巴斯（穆聖叔父, 48） → 阿卜杜拉·伊本·阿巴斯 (49) → 阿里·伊本·阿卜杜拉 (50)
  → 穆罕默德·伊本·阿里 (51, 阿拔斯革命策動)
    ├─ 易卜拉欣·伊瑪目 (52, 革命第一任 imam，被毒殺)
    ├─ 1. 阿拔斯·薩法赫    (52, 749-754)  ← 阿拔斯革命勝利者
    └─ 2. 曼蘇爾           (52, 754-775)  ← 建巴格達
       → 3. 馬赫迪 (53) → 4. 哈迪 + 5. 哈倫·拉希德 (54)
         哈倫 → 6. 阿明 + 7. 馬蒙 + 8. 穆塔西姆 (55)
           穆塔西姆 → 9. 瓦提克 + 10. 穆塔瓦基勒 (56)
             穆塔瓦基勒 → 11. 蒙塔西爾 + 13. 穆塔茲 + 15. 穆塔米德 (57)
                          → 穆瓦法克 → 16. 穆塔迪德 (58)
                                       → 17-19. 穆克塔菲/穆克塔迪爾/卡希爾 (59)
… 一路到 37. 穆斯塔西姆 (gen 71, 1242-1258，巴格達被蒙古旭烈兀攻陷處死)
```
（共 37 任 + 4-5 個未即位但血脈中介；中間沿襲 al-Muqtadi → al-Mustazhir → an-Nasir → al-Musta'sim 主線）

### 現代哈希姆王朝（Modern Hashemite Dynasty）

由末任麥加謝里夫沙里夫·胡笙（descent from Hasan ibn Ali via Banu Qatadah, ~35 gens 略過）開創：

```
沙里夫·胡笙 (gen 85, 末任麥加謝里夫 1908-1924 + 漢志國王 1916-1924)
├─ 阿里·伊本·胡笙 (86, 末任漢志國王 1924-25)
│  └─ 阿卜杜·伊拉 (87, 伊拉克攝政 1939-53)
├─ 阿卜杜拉一世·約旦 (86, 約旦王國首任 1921-51) ← 1951 在阿克薩遇刺
│  └─ 塔拉勒 (87, 1951-52)
│     └─ 胡笙·約旦 (88, 1952-99) — 47 年在位
│        └─ 阿卜杜拉二世·約旦 (89, 1999-至今) ← 當代在位國王
│           └─ 胡笙王儲 (90, 2009-至今)
├─ 費薩爾一世·伊拉克 (86, 敘利亞→伊拉克王 1921-33)
│  └─ 加齊 (87, 1933-39)
│     └─ 費薩爾二世·伊拉克 (88, 1939-58) ← 1958 七月革命處死，伊拉克王國終
└─ 宰德·伊本·胡笙 (86, 1958 後伊拉克王位繼承權人，流亡)
```

> 註：沙里夫·胡笙 ← 哈桑·伊本·阿里 中間 ~35 代 Banu Qatadah 麥加謝里夫世系暫未插入（Task 9 待辦）。

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

- Ibn Hisham 等史家列出的中段 ~30 代名字，諸版本互異，權威性低
- 穆聖訓示「النساب يكذبون」是針對「阿德南之後追溯祖先」的妄言，**非禁止記載中段**
- 本表選 5 名「Madinian short list」變體：哈馬爾→薩拉曼→耶薩→烏達德→烏德 (gen 23-27)
- 全部 tag `tradition='historical'`（灰卡），表示「傳統補白／權威性低」，視覺上既保 spine 連貫，也清楚標明 epistemic 等級

### 跨代婚姻處理（阿里 gen 43 娶 法蒂瑪 gen 45）

- 阿里為穆聖堂弟（艾比·塔利卜之子，gen 43）
- 法蒂瑪為穆聖之女（gen 45）
- 兩人婚姻為穆聖在世時親自主婚
- biblical-tradition-layer 已有同類處理（如猶大-她瑪：跨代亂倫案例），參考 `layoutSubtree` 的 `minGen` 機制：傳 `gen+1` 強制兒女視覺世代 ≥ 父代+1

---

## ✅ 完成項目

### Task 1: 表格頁 `pages/genealogy/islamic.vue` — ✅ 完整 CRUD 完成

已就位：
- 列表頁（7 種傳統徽章 + 列底色 + 搜尋 / 傳統 filter）
- 中／阿／英三欄姓名顯示，kunya 跟在中文名後以小字呈現
- 「+ 新增人物」按鈕（emerald 綠）
- 編輯／刪除按鈕（hover 顯示，與 biblical.vue 一致的 UX）
- Modal 表單：中／阿／英 / kunya / 性別 / 傳統下拉（7 選項）/ 國別 / generation / sort_order / birth_year / death_year / child_year / age / spouse / children / sources / notes
- 表頭族譜圖 tab 連到 `/genealogy/islamic-tree`

### Task 2: API endpoints — ✅ 全部完成

- ✅ `server/api/genealogy/islamic-people.get.ts` — 列表
- ✅ `server/api/genealogy/islamic-people.post.ts` — 新增（含 tradition CHECK 驗證）
- ✅ `server/api/genealogy/islamic-people/[id].patch.ts` — 更新（含 JSONB 三件套欄位）
- ✅ `server/api/genealogy/islamic-people/[id].delete.ts` — 刪除
- ✅ `server/api/genealogy/islamic-graph.get.ts` — graph view，套 `?view=` filter + JSONB merge

view 規則（鏡像 biblical-graph）：
- `quranic`（預設）→ 只 quranic
- `sunni` → quranic + sunni + historical
- `shia_twelver` → 上 + shia_twelver + JSONB merge
- `shia_ismaili` → quranic + sunni + shia_ismaili + JSONB merge
- `shia_zaidi` → quranic + sunni + shia_zaidi + JSONB merge

### Task 3: Tree component `IslamicSpineTree.vue` — ✅ v2 重做完成（2026-05-16）

v2 重點修正（per biblical 規則）：
- **婚姻線 per-wife**：每位妻子畫獨立紅線到右側鄰居（首妻→root；二妻→首妻 等）
- **親子 drop 起點 = 婚姻中點**（`rootCX - SLOT_K/2`，Y=marriage-line Y）— 而非從父卡正下方掉下
- **T-bar 跨所有子嗣 X**，每個子卡上方有個別灰色垂直線
- **多妻分組**：哈蒂徹的 6 子女從 哈蒂徹↔穆罕默德 中點下，瑪利亞·科普特的 1 子（易卜拉欣）從 瑪利亞↔對位 中點下
- **`layoutSubtree` 遞迴**：非 spine 子樹（伊瑪目鏈、哈里發朝代、麥加謝里夫鏈）以 biblical 的左右佈局演算法處理
- **Siblings of spine** 仍放在 spine 卡右側（hbar 從 spine_parent 下伸出）
- **Orphan 區**：暫放在 spine 左側 -1200 開始的 6 列 grid（蘇菲 + 未連通的 historical placeholder）

v1（已被取代）的問題：
- 只畫一條 marriage line（最右側妻 ↔ root），其他妻沒線
- 子嗣 drop 從 spine 卡正下方掉下，看不出是父+妻所生
- 沒有 T-bar，多子嗣直接平行下垂
- 伊瑪目鏈用 BFS row-by-row 排，亂

仍未實作（biblical 有但 Islamic 暫無）：
- ✅ ~~subtree ▼ 收摺~~（2026-05-16 已實作；非 spine 卡片有後代 → 顯示 ▼N 鈕；點擊展開）
- ♻ same-person marker（跨子樹同人跳轉，如法蒂瑪 既是穆聖女兒又是阿里之妻）
- 跨代婚姻 minGen 機制（阿里 gen 48 娶 法蒂瑪 gen 50，目前以較低的 gen 為準）— BUG 6 暫不修

### Task 4: 路由入口 — ✅ 完成

[pages/genealogy/index.vue](../../../pages/genealogy/index.vue) 已加第 4 張卡片 ☪「伊斯蘭族譜」(emerald hover)。

### Task 5: 視圖切換 widget — ✅ 完成

於 `islamic-tree.vue` 加浮動 toggle（在 IslamicSpineTree 內，緊鄰穆罕默德卡）：
`[古蘭] [順尼] [十二派] [伊斯瑪儀] [栽德]`
預設「古蘭」（quranic）；URL `?view=` 同步；非預設值才寫入 query。

### Task 6: 圖例 — ✅ 完成

左下 Legend：emerald 主幹色 + 7 色 swatch + 紅線婚姻 + 灰線親子 + 操作提示。

---

## 🚧 後續待辦（next）

### Task 10：♻ 同人標記 + 阿里跨樹顯示（2026-05-16 完成）

阿里（艾比·塔利卜之子）在族譜上是 **同一人多卡**：
- gen 49 row（穆聖表弟線）：作為 艾比·塔利卜 之子，與 穆罕默德 同代
- gen 50 row（穆聖女婿線）：作為 法蒂瑪 之夫，與她並列，下接 12 伊瑪目

**實作**（仿 biblical 同人標記）：
- `makeLNode` 加 `allowDup=true` 參數。`layoutSubtree` 的 root 放置呼叫使用此參數允許重複，placeWivesHere / spine wives / orphan loop 不允許重複。
- LNode `id` 對 dup 加 `:dup<N>` 後綴避免 Vue key 衝突。
- 卡片右上角 ♻ 藍色 marker。click 跳到同人 peer 位置（有 fallback：往上找最近渲染的祖先，展開其 ▼）。
- 「先知鏈」按鈕含 `艾比·塔利卜` → 一鍵 expand 後阿里在兩處同時顯示，並都有 ♻。

**DB 修正**：阿里 DB gen 48 → 49（穆聖表弟同 gen 49，非穆聖叔伯 gen 48 輩）。跨代婚姻 仍 gen 49 ↔ 法蒂瑪 gen 50（一代差）。子嗣 哈桑/侯賽因 維持 gen 50。

### Task 9：以色列先知直系（2026-05-16 完成）

古蘭 25 位先知中，以色列線（葉爾孤白後裔）已 seed 完整 37 rows：

**穆薩鏈（gen 23-26）**：利未 → 卡哈特 → 阿米蘭（穆薩之父）→ 穆薩 + 哈倫（古蘭 3:33「阿米蘭的後裔」）

**達烏德鏈（gen 23-34）**：猶大 → 法勒斯 → 希斯崙 → 蘭 → 阿米拿達 → 拿順 → 撒門 → 波阿斯 → 俄備得 → 耶西 → 達烏德 → 蘇萊曼

**Davidic 王朝（gen 35-46）**：羅波安 → 亞比雅 → 亞撒 → 約沙法 → 約蘭 → 烏西雅 → 約坦 → 亞哈斯 → 希西家 → 瑪拿西 → 亞們 → 約西亞 → 耶哥尼雅 → 阿米蘭（馬利亞之父）

**麥爾彥+爾撒（gen 47-48）**：阿米蘭（馬利亞之父）+ 哈拿（妻）→ 麥爾彥 → 爾撒（無父奇蹟受孕）

**宰凱里雅+葉哈雅（gen 47-48，亞倫祭司線）**：哈倫 → [~21 代略過] → 宰凱里雅 + 伊麗莎白 → 葉哈雅。`哈倫.children` 直接列 宰凱里雅 製造視覺接點，notes 註明世代略過。

**UI**：右上角控制區加「先知鏈」鈕（amber 色），點擊 expandClans 預載 32 位先知 chain IDs → 一鍵展開三條平行 chain。

### Task 7（資料補完，可後續批次）

- ✅ 主要哈里發：艾布·伯克爾、歐麥爾、奧斯曼、阿里（2026-05-16 完成）
- ✅ 倭馬亞王朝 14 任哈里發 + Sufyanid/Marwanid 兩支接入（2026-05-16 完成）
- ✅ 阿拔斯王朝 37 任巴格達哈里發（2026-05-16 完成）
- ✅ 現代哈希姆王朝（沙里夫·胡笙、約旦王國四代、伊拉克王國三代）（2026-05-16 完成）
- ✅ **法蒂瑪王朝** 14 任哈里發 + 4 satr 隱遁伊瑪目（穆罕默德·伊本·伊斯瑪儀往下，gen 56-69）（2026-05-16 完成）
- ✅ **歷代麥加謝里夫**完整鏈（Hasan ibn Ali → Banu Qatadah → 沙里夫·胡笙，~35 gens 已連通）（2026-05-16 完成）
- ✅ 開羅阿拔斯傀儡哈里發 18 任（1258-1517 CE，馬木留克時期）（2026-05-16 完成）
- ✅ 早期蘇菲聖徒 10 位（順序：Uways/Hasan al-Basri/Rabia/Ibrahim Adham/Ma'ruf/Sari/Bayazid/Junayd/Hallaj/Ahmad Ghazali）（2026-05-16 完成；皆 orphan，蘇菲為精神 silsila 非血親）
- ⏳ 伊瑪目之配偶與其他子女（目前只填了直系傳承的伊瑪目）
- ⏳ 鄂圖曼蘇丹自稱哈里發（1517-1924）— 不在血脈內，可選擇加入

### Task 8（tree 進階）— ✅ 2026-05-16 視覺驗收 8 大 BUG 已修

`scripts/islamic-shot.mjs` ✅ 已建立（仿 biblical-shot.mjs）。視覺驗收截圖存於 `c:/tmp/islamic-*.png`。

**已驗證**：
- 132 / 86 cards rendered（sunni / shia_twelver view，subtree 收摺後）
- 婚姻線 ✅ Row 1 妻 horizontal、Row 2 妻 vertical 紅 stub 連到 spine marY
- 親子 drop ✅ 從婚姻中點下降；Row 1 妻 → marY 中點下；Row 2 妻 → 妻卡底下垂直
- spine 列 ✅ 阿丹 (gen 1) → 穆罕默德 (gen 49) 完整連貫，每張綠卡左側 3px emerald 條帶
- 視角 widget ✅ 固定 viewport 左上角，pan/zoom 不影響

**🟢 BUG 1：spine 中段 row 出現超長紅色橫線** — 已解
偵錯後發現 DB 沒有 phantom spouse 資料。實際原因是 cardClass 回傳 `relative` 蓋掉 inline `absolute`（BUG 5 同源），導致 v-for 第 N 張卡片掉到 normal flow 第 N 行，視覺上婚姻線連結到錯位的卡片。修 cardClass 去掉 `relative` 後消失。

**🟢 BUG 2：沙里夫·胡笙 35 代直系造成 canvas 7000+px 高** — 已解
實作 subtree ▼/▲ 收摺機制：每張非 spine 且有子孫的卡片掛一個 ▼N 鈕，預設收摺，點開展開該支。沙里夫·胡笙鏈現在預設躲在 哈桑·穆斯安納 的 ▼ 後面。countDescendants 計算每人後代數，深度上限 25 防自環。

**🟢 BUG 3：阿拔斯王朝 37 哈里發子樹寬度爆炸** — 已解
同 BUG 2，阿巴斯（穆聖叔父）卡掛 ▼37 鈕。預設收摺，點開才往下渲染 37 代哈里發。

**🟢 BUG 4：fitSpine 預設縮放只到 18%** — 已解
新增 `resetToTop()` (mount 時跑、根據 viewport / desiredRows 算 zoom 0.35-0.75) + `fitSpine()` (14 row 為基準)。不再 fit 整個 canvas 高（含 collapsed subtree + orphan）。

**🟢 BUG 5：哈娃 (Eve) 卡未驗證可見** — 已解
根因：`cardClass()` 回傳含 `relative`，與 inline `class="node-card absolute"` 衝突。Tailwind 中 `.relative` (alphabetical) 出現在 `.absolute` 之後，cascade 取最後一個 → `position: relative` 勝出 → 所有卡片掉到 normal flow，第 49 張卡 (哈娃) 出現在 y≈2181（screen 外）。修法：cardClass 移除 `relative`，子元素的 absolute 定位由 .node-card 自身的 absolute + left/top inline 提供 containing block。

**🟡 BUG 6：跨代婚姻 阿里(48) × 法蒂瑪(50) 未實作 minGen** — 暫不修
複雜度高 / 視覺影響小。目前阿里在 gen 48 row (作為 艾比·塔利卜 sibling 子樹)，法蒂瑪在 gen 50 row (穆聖之女)，兩人沒有跨樹婚姻線。語意上是兩棵獨立子樹各自顯示 — 不致誤導但無連結。後續若要做需要：(a) 在 graph endpoint 加 cross-subtree spouse edge 渲染，或 (b) 讓 阿里 也在 gen 50 出現第二張卡 + 跳同人 ♻ marker（biblical 已有此功能可參考）。

**🟢 BUG 7：視角 widget 在非穆罕默德視窗會跑到畫面外** — 已解
從 `anchored to Muhammad card` 改為 `absolute top-3 left-3` 永遠在 viewport 左上角。橫式排列 5 個 view 選項，z-40 不被卡片蓋住。

**🟢 BUG 8：穆罕默德的 12 妻全擺左側畫面寬度爆炸** — 已解
妻數 > 6 自動 stack 2 行：Row 1（spine row）放 row1Count = ceil(N/2)，Row 2 在 NH+12 px 下方。Row 2 妻的婚姻線用紅色垂直 stub 連到 Row 1 的 marY。同時加 wife 排序：spineId 的 `spouse` 欄位字串順序為準（赫蒂徹是首妻 → 靠近穆聖），新增 `spouseField` 透過 graph endpoint 帶到 node data。

**Orphan 區重設計**
原本 orphan area 從 (-1200, PAD=60) 開始，後來與 Eve 衝突（都在 y=60 那一列）。現改放在 spine 最後一代 + 2 row 下方、SPINE_X 兩側 ±450 內，6 cols × N rows 排列。`descendsFromSpine()` 走 parent + spouse chain 判定是否屬於 spine，是 → 屬於 collapsed subtree 暫時隱藏；否 → 才是真 orphan（蘇菲鏈、view-filter 後失聯人物）。

驗收 screenshot：
- `node scripts/islamic-shot.mjs` — 預設 sunni view，看到 spine gen 1-11 + 哈娃
- `node scripts/islamic-shot.mjs --view shia_twelver --focus 哈桑·伊本·阿里 --zoom 0.8` — 切換到十二派視角，rendered 86 cards
- `node scripts/islamic-shot.mjs --focus 烏姆·薩拉瑪 --zoom 1.1` — 看 12 妻 2 行 stack（赫蒂徹靠近穆聖、瑪利亞·科普特連 易卜拉欣）

DOM 驗證腳本：`node scripts/check_eve_dom.mjs` — 列 Adam/Eve/Muhammad/12 妻位置。

---

## 🔑 關鍵 spec / 規則

1. **古蘭優先** — 古蘭明文人物（25 先知 + 古蘭點名者）必為 `quranic`，不可降階為 `sunni`
2. **不批次 propagate disambiguator** — 套用 [feedback_biblical_name_rules](../../../memory/feedback_biblical_name_rules.md) 同則
3. **中文音譯遵循中國穆斯林傳統** — 阿丹／努哈／易卜拉欣／伊斯瑪儀／穆罕默德／阿里／法蒂瑪／侯賽因 等通行譯名；遇到罕見人物可參考《伊斯蘭百科全書》中文版或《穆罕默德傳》（Martin Lings 馬丁·林斯 中譯本）
4. **kunya（父子稱呼）** — 阿拉伯人「Abu X / Umm X / Ibn X / Bint X」是文化專有，獨立放 `kunya` 欄不要混入主名
5. **gen 計數** — 阿丹 = 1；穆罕默德 = 49；末伊瑪目馬赫迪 = 59。**不要重編**（已 freeze；2026-05-16 因加入蓋達爾→阿德南 5 代史傳補白，全表 gen ≥ 23 已 +5）
6. **PowerShell 全授權**（per [feedback_powershell_full_auth](../../../memory/feedback_powershell_full_auth.md)）
7. **有改動自動 git push**（per [feedback_auto_push](../../../memory/feedback_auto_push.md)）

---

## 📁 相關 scripts（可直接重用 / 改寫）

- `c:\tmp\islamic_create_table.py` — schema migration（已跑過）
- `c:\tmp\islamic_seed_lineage.py` — 阿丹→穆罕默德 53 行（已跑過）
- `c:\tmp\islamic_seed_family.py` — 穆聖叔伯 + 12 妻 + 7 子女 + 12 伊瑪目 42 行（已跑過）
- `c:\tmp\islamic_insert_qaydar_adnan_bridge.py` — 蓋達爾→阿德南 5 代史傳補白 + gen >= 23 全表 +5（已跑過）
- `c:\tmp\islamic_seed_caliphs.py` — Quraysh 部族分支錨點 + 4 正統 + 14 倭馬亞 + 37 阿拔斯 + 現代哈希姆 共 96 行（已跑過）
- `c:\tmp\islamic_check_state.py` / `c:\tmp\islamic_verify_caliphs.py` — DB 狀態檢查工具
- `c:\tmp\inspect_biblical_schema.py` — 範本，列任意 supabase 表 column

未來新批次（如蘇菲聖徒鏈、法蒂瑪王朝、麥加謝里夫完整鏈）依此模式：fetch_all → set existing → INSERT skip-if-exists；parent 用 `_parent` field 同步 patch parent.children。

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
