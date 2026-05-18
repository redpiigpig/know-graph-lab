---
name: islamic-tradition-layer
description: 伊斯蘭族譜的「教派傳統」視角圖層 — 古蘭明文（白）／順尼派（綠）／十二伊瑪目派（紅）／伊斯瑪儀派（紫）／栽德派（橙）／蘇菲（青）／歷史傳述（灰）。包含資料表 schema、人物清單（阿丹→穆罕默德+穆聖家族+12 伊瑪目）、UI 配色設計、表格 CRUD + 族譜圖 + view 切換 widget（皆已上線）。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 伊斯蘭族譜 — 教派傳統視角圖層

> 📜 **資料原則：comprehensive over doctrinal** — 任何傳統有列的人物與世系都儘量收錄，不因某派宗教權威否認而排除。例如穆聖訓示「譜系家追溯阿德南以前祖先是撒謊」(الناس يكذبون النسابة) 我們**不採信**為理由刪減資料；Ibn Hisham《Sirat Rasul Allah》既已詳列 21 代伊斯瑪儀↔阿德南 chain，照列。立場：使用者看完整圖像自己判斷，不替使用者做宗教審查。

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

已完成腳本（c:\tmp）— 跑過順序大致：
- `islamic_create_table.py` — 建立 `islamic_people` 表 + 索引 + updated_at trigger
- `islamic_seed_lineage.py` — 阿丹→穆罕默德 53 行（初始 seed，gen 1-49 舊計）
- `islamic_seed_family.py` — 穆聖叔伯姑姨、12 妻、7 子女、阿里+12 伊瑪目（含 Ismaili/Zaidi 分支）42 行
- `islamic_seed_prophets.py` — 以色列先知直系 37 行（2026-05-16）：利未/猶大、穆薩+哈倫、達烏德+蘇萊曼、Davidic 王朝 12 代、麥爾彥+爾撒、宰凱里雅+葉哈雅
- `islamic_link_zechariah.py` — patch 哈倫.children += 宰凱里雅（亞倫祭司世系約 21 代略過）
- `islamic_seed_caliphs.py` — Quraysh 部族分支錨點 + 4 正統 + 14 倭馬亞 + 37 阿拔斯 + 現代哈希姆 96 行
- `islamic_insert_qaydar_adnan_bridge.py` — **舊版** 蓋達爾→阿德南 5 代史傳補白（已被 Ibn Hisham 21 代取代）
- `islamic_ibn_hisham_migration.py` — **替換** 為 Ibn Hisham 完整 21 代 伊斯瑪儀↔阿德南 bridge：新增 16 historical rows (gen 23-38) + 蓋達爾後代全鏈 generation +16
- `islamic_matthean_complete.py` — Matthean 12 代 後巴比倫 Davidic（撒拉鐵→約瑟）+ 哈蘭/魯特（易卜拉欣旁支）+ 呼德 tradition 升級 historical→quranic
- `islamic_remaining_prophets.py` — 舒阿卜/艾優卜/祖勒基福勒/優努斯/易勒亞斯/艾勒葉賽爾/米甸/西布倫 等 13 行
- `islamic_side_branches.py` — 22 旁支：阿丹兩子（蓋比勒/哈比勒）、努哈 3 子+1 妻、雅各 8 子、Lot 2 女+2 外孫（摩押/便亞米）、穆薩家（米利暗/西坡拉/革舜/以利以謝）
- `islamic_arabic_rename.py` — 68 名大規模 Arabic 衍生中譯（該隱→蓋比勒、亞伯→哈比勒、利未→拉維、雅各→葉爾孤白；同步改其他 row 的 children/spouse 引用）
- `islamic_seed_dynasties_b.py` — 法蒂瑪王朝 + 麥加謝里夫完整鏈 + 開羅阿拔斯傀儡（Task 7 後半段）
- `islamic_delete_sufi_orphans.py` — 10 蘇菲精神導師整批刪除（皆 orphan，蘇菲為精神 silsila 非血親，回退原 Task 7 ✅ 蘇菲決定）
- `islamic_fix_ali_gen.py` — 阿里 gen 微調（同人標記前置作業）
- `islamic_check_state.py` / `islamic_check_existing.py` / `islamic_find_orphans.py` / `islamic_verify_caliphs.py` / `islamic_spouse_check.py` / `islamic_stats.py` — 查表診斷工具

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
| generation | int | 阿丹 = 1；穆聖 = 65；末伊瑪目馬赫迪 = 75；現代約旦阿卜杜拉二世 = 105 |
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

## 🌳 已填入的人物世系（截至最新 388 rows）

> tradition 分布：sunni 233 / historical 76 / quranic 44 / shia_ismaili 22 / shia_twelver 12 / shia_zaidi 1。
> generation 跨度 1-106。蓋達爾→阿德南中段 Ibn Hisham 21 代補白後，所有伊斯瑪儀血親 gen 全體 +16。

### 阿丹 → 努哈（gen 1-10）
阿丹 → 設特 → 阿努施 → 卡伊南 → 馬赫拉伊勒 → 雅雷德 → **伊德里斯**（古蘭 19:56-57，對應聖經以諾）→ 馬陀沙拉赫 → 拉麥克（努哈之父）→ **努哈**（古蘭 71 整章 + 11:25-49）。哈娃 (gen 1) 為阿丹之妻。

**阿丹兩子 (gen 2)**：蓋比勒（該隱）、哈比勒（亞伯）— 古蘭 5:27-31 故事（quranic）。

### 努哈 → 易卜拉欣（gen 11-20）
薩姆（閃，努哈之子）→ 阿爾法夏德 → 沙拉赫 → **阿比爾（呼德？）**（quranic；學界傾向 Hud 即希伯來 'Eber/Heber）→ 法利吉 → 拉烏 → 薩魯吉 → 納霍爾 → **阿札爾**（易卜拉欣之父，古蘭 6:74，偶像匠人）→ **易卜拉欣**（古蘭 2:124-141、19:41-49，五大堅韌使者）

**努哈其他子女**：哈姆（含）、雅菲斯（雅弗）+ 第四子（瓦姆，淹死）；妻 (sunni)。哈姆→庫什→**尼姆魯德**（與易卜拉欣對抗的暴君）。

**易卜拉欣兩妻 (gen 20)**：撒拉（易司哈格之母）、哈哲爾（伊斯瑪儀之母）。
**易卜拉欣之兄哈蘭 (gen 19)** → 子 **魯特（Lot, gen 20, quranic）** 古蘭 7:80-84 等多處明文先知。

### 兩支分流：以色列家 vs 阿拉伯家

**易司哈格線**（gen 21+）：
- 易司哈格 (21) → 葉爾孤白（即雅各／以色列, 22）+ 兄弟 **阿伊蘇**（以掃，雙胞胎）
- 葉爾孤白 12 子 (gen 23)：**優素福**（quranic 古蘭 12 整章）、本雅明、魯比勒、沙姆溫、拉維、雅胡達、賈德、阿希爾、雅薩基爾、札布倫、但、拿弗他利
- 妻：里夫卡（易司哈格之妻）；麗百加→里夫卡 rename

**伊斯瑪儀線**（gen 21+，穆聖直系）：
- 伊斯瑪儀 (21) → **蓋達爾**（穆聖直系, 22）、納比特（旁支）

### 蓋達爾 → 阿德南 中段（gen 23-43，Ibn Hisham 21 代）

依 Ibn Hisham《Sirat Rasul Allah》長表 21 代史傳補白，全部 `tradition='historical'`（灰卡，權威性低）：

```
gen 23 阿蘭姆 → 24 奧達 → 25 馬齊 → 26 薩米 → 27 扎里赫
    → 28 納希特 → 29 馬克西 → 30 阿伊哈姆 → 31 阿夫納德
    → 32 阿伊薩爾 → 33 迪沙恩 → 34 阿勒阿維 → 35 雅勒罕
    → 36 雅赫珍 → 37 耶斯里比（Yathribi，與麥地那古名同源）
    → 38 桑巴爾 → 39 哈馬爾 → 40 薩拉曼 → 41 耶薩
    → 42 烏達德 → 43 烏德 → 44 阿德南
```

> 舊版 5-代「Madinian short list」(gen 23-27 哈馬爾→…→烏德) 已被取代。整個伊斯瑪儀血親全鏈 generation +16。

### 阿德南 → 穆罕默德（gen 44-65，22 代）

阿德南 (44) → 馬阿德 → 尼扎爾 → 穆達爾 → 易勒亞斯 → 穆德里卡 → 胡扎伊瑪 → 基納納 → **納德爾（古萊什之祖, 52）** → 馬利克 → 菲赫爾 → 嘎利卜 → 盧艾 → 卡布 → 穆拉 → 基拉卜 → **古蘇**（統一古萊什、掌克爾白）→ 阿卜杜·瑪納夫 (61) → **哈希姆**（哈希姆家族祖, 62）→ **阿卜杜·穆塔利卜** (63) → 阿卜杜拉（穆聖之父, 64）+ 阿米娜（穆聖之母）→ **穆罕默德** (65, ﷺ)

### Banu Hashim 兄弟（阿卜杜·穆塔利卜之子, gen 64）

- **阿卜杜拉（穆聖之父）** — quranic
- **艾比·塔利卜** — 撫養孤兒穆聖；阿里之父；什葉派視為信士
- **阿巴斯（穆聖之叔父）** — 阿拔斯王朝之祖
- **哈姆扎** — 「眾烈士之主」，伍侯德殉教
- **艾布·拉哈布** — 古蘭 111 章詛咒對象（quranic 反面）
- **烏姆·賈米爾**（拉哈布之妻）— 古蘭 111:4-5「擔柴的婦人」

### 穆聖之 12 位妻（信士之母，gen 65）— 按嫁穆聖順序

赫蒂徹（首妻，所有子女除易卜拉欣之母）→ 蘇黛 → 阿伊莎 → 哈芙莎 → 宰娜卜·賓特·胡扎伊瑪 → 烏姆·薩拉瑪 → **宰娜卜·賓特·賈赫什**（古蘭 33:37-38 明文，quranic）→ 朱韋里葉 → 烏姆·哈比巴 → 莎菲婭 → 邁穆娜 → 瑪利亞·科普特（易卜拉欣之母）

### 穆聖之 7 子女（gen 66）

| 名 | 母 | 備註 |
|---|---|---|
| 嘎西姆 | 赫蒂徹 | 夭折 |
| 宰娜卜 | 赫蒂徹 | sunni |
| 魯蓋葉 | 赫蒂徹 | 嫁奧斯曼 |
| 烏姆·庫勒蘇姆 | 赫蒂徹 | 魯蓋葉逝後嫁奧斯曼 |
| **法蒂瑪** | 赫蒂徹 | **quranic**（嗣裔之源，嫁阿里） |
| 阿卜杜拉 | 赫蒂徹 | 夭折（又名塔伊布／塔希爾） |
| 易卜拉欣 | 瑪利亞·科普特 | 18 月夭折 |

### 阿里 + 法蒂瑪 → 12 伊瑪目鏈

```
1. 阿里（艾比·塔利卜之子, gen 65, quranic）  ← 古蘭 5:55 什葉派指涉 + 順尼第四哈里發
   └─ 配偶: 法蒂瑪（穆聖之女, gen 66）  ♻ 同人：阿里有兩卡（堂弟 + 女婿），跨代婚姻
2. 哈桑·伊本·阿里（66）          ← shia_twelver；順尼視為第五哈里發
3. 侯賽因·伊本·阿里（66）        ← shia_twelver；卡爾巴拉殉教 (680 CE)
4. 阿里·宰因·阿比丁（67）        ← shia_twelver；卡爾巴拉唯一倖存男丁
   ├─ 5. 穆罕默德·巴基爾（68）
   │   └─ 6. 嘉法爾·薩迪克（69）  ← 十二派 / 伊斯瑪儀共主，分支點
   │       ├─ 7a. 穆薩·卡齊姆（70）        ← shia_twelver（巴格達獄中殉教）
   │       │   └─ 8. 阿里·里達（71）
   │       │       └─ 9. 穆罕默德·賈瓦德（72）
   │       │           └─ 10. 阿里·哈迪（73）
   │       │               └─ 11. 哈桑·阿斯卡里（74）
   │       │                   └─ 12. 穆罕默德·馬赫迪（75）← 隱遁伊瑪目
   │       └─ 7b. 伊斯瑪儀·伊本·嘉法爾（70）← shia_ismaili 分支
   │           └─ 穆罕默德·伊本·伊斯瑪儀（71） ← 隱沒伊瑪目
   └─ 宰德·伊本·阿里（68）        ← shia_zaidi 分支（庫法起義 740 CE 殉教）
宰娜卜·賓特·阿里（66）— shia_twelver；卡爾巴拉後率女眷俘往大馬士革
```

### 古蘭 25 先知支線（已 seed 完整）

| 鏈 | 先知 | gen 範圍 | 接入點 |
|---|---|---|---|
| 穆薩鏈 | 穆薩 + 哈倫 | 23-26 | 拉維（利未）→ 卡哈特 → 阿米蘭 |
| 達烏德鏈 | 達烏德 + 蘇萊曼 | 23-34 | 雅胡達 → 法利茲 → … → 耶西 |
| Davidic 王朝 | 羅波安 → 耶哥尼雅 | 35-46 | 蘇萊曼後 12 代 |
| **Matthean 後巴比倫 12 代** | 撒拉鐵→所羅巴伯→…→馬丹→雅各→**約瑟（馬利亞之夫）** | 47-58 | 耶哥尼雅後續 |
| 麥爾彥+爾撒 | 麥爾彥（馬利亞）+ 爾撒（耶穌） | 58-59 | 阿米蘭（馬利亞之父）= 馬丹之子，與雅各兄弟 |
| 宰凱里雅+葉哈雅 | 撒迦利亞 + 施洗約翰 | 47-48 | 哈倫→[~21 代略過]→宰凱里雅 |
| 米甸／舒阿卜 | 舒阿卜 | 21-22 | 易卜拉欣 via Keturah → 米甸（quranic 略過） |
| 艾優卜鏈 | 艾優卜 + 祖勒基福勒 | 22-26 | 阿伊蘇（Esau）→拉扎→穆斯→艾優卜→祖勒基福勒 |
| 優努斯鏈 | 優努斯 | 23-25 | 札布倫（西布倫）→ 亞米太→ 優努斯 |
| Aaronic／易勒亞斯鏈 | 易勒亞斯 + 艾勒葉賽爾 | 27-30 | 哈倫→以利亞撒→非尼哈→易勒亞斯→艾勒葉賽爾 |

> 中段世代多處 simplified（穆薩→ Davidic、Aaronic 線跳 ~20 代）；notes 註明，視覺上保連貫。

### 旁支家庭（22 rows，2026-05-17 補）

- **魯特家**：2 女（露絲？）+ 2 外孫摩押、便亞米（古蘭未提，sunni）
- **穆薩家**：姊 米利暗（quranic 譯名 Maryam bint Imran）、妻 沙福拉（西坡拉）、2 子 賈舒姆、阿利亞撒（穆薩之子）
- **雅各 8 子**：上述以外的兄弟（魯比勒、沙姆溫、拉維、雅胡達、賈德、阿希爾、雅薩基爾、本雅明）
- **達烏德家**：拔示巴 (巴特舒巴) + 暗嫩、押沙龍、亞多尼雅

> 跳過：Saul/Goliath/Samuel — 中間世代不明會 orphan。

### Quraysh 部族分支（Rashidun 三哈里發接入）

```
阿卜杜·瑪納夫 (gen 61)
├─ 哈希姆 (62, spine)
└─ 阿卜杜·夏姆斯 (62) → 倭馬亞 (63)
   ├─ 艾布·阿斯·伊本·倭馬亞 (64)
   │  ├─ 阿凡 (65) → 奧斯曼·伊本·阿凡 (66)        ← 第三任正統哈里發
   │  └─ 哈卡姆 (65) → 馬爾萬一世 (66)              ← Marwanid 倭馬亞祖
   └─ 哈爾卜 (64) → 阿布·蘇富揚 (65)
                   ├─ 穆阿維葉一世 (66)              ← Sufyanid 倭馬亞祖
                   └─ 烏姆·哈比巴 (穆聖之妻)

穆拉 (58) → … Banu Taym 鏈 → 艾布·伯克爾 (65)  ← 第一任正統哈里發
卡布·伊本·盧艾 (57) → … Banu Adi 鏈 → 歐麥爾·伊本·哈塔卜 (65)  ← 第二任正統哈里發
```

### 朝代鏈（resumé 形式，DB 詳列）

| 朝代 | 期間 | 任數 | gen 範圍 | 接入點 |
|---|---|---|---|---|
| 倭馬亞王朝 | 661-750 | 14 (3 Sufyanid + 11 Marwanid) | 66-69 | 倭馬亞 (63) 下 |
| 阿拔斯王朝（巴格達） | 749-1258 | 37 | 66-87 | 阿巴斯 (64) 下 |
| 開羅阿拔斯傀儡 | 1258-1517 | 18 | 88-91 | 馬木留克時期延續 |
| **法蒂瑪王朝** | 909-1171 | 14 + 4 satr 隱遁 | 72-85 | 穆罕默德·伊本·伊斯瑪儀 (71) 下 |
| 麥加謝里夫（Banu Qatadah） | 9 世紀-1924 | ~35 代 | 67-101 | 哈桑·伊本·阿里 (66) 下 |
| 現代哈希姆王朝 | 1916-至今 | 約旦 4 代 + 伊拉克 3 代 | 101-106 | 沙里夫·胡笙 (101) 下 |

**現代哈希姆**：沙里夫·胡笙 (101) → {阿里·漢志、阿卜杜拉一世·約旦 → 塔拉勒 → 胡笙·約旦 → **阿卜杜拉二世·約旦 (105)** → 胡笙王儲 (106)；費薩爾一世·伊拉克 → 加齊 → 費薩爾二世·伊拉克（1958 革命終）；宰德·伊本·胡笙}

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
5. **gen 計數** — 阿丹 = 1；穆罕默德 = 65；末伊瑪目馬赫迪 = 75；現代約旦阿卜杜拉二世 = 105。**不要重編**（freeze；蓋達爾↔阿德南中段已改用 Ibn Hisham 21 代版本，伊斯瑪儀血親全鏈 gen 已 +16）
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
