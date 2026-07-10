---
name: genealogy-islamic
description: 伊斯蘭族譜的「教派傳統」視角圖層 — 古蘭明文（白）／順尼派（綠）／十二伊瑪目派（紅）／伊斯瑪儀派（紫）／栽德派（橙）／蘇菲（青）／歷史傳述（灰）。包含資料表 schema、人物清單（阿丹→穆罕默德+穆聖家族+12 伊瑪目）、UI 配色設計、表格 CRUD + 族譜圖 + view 切換 widget（皆已上線）。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 伊斯蘭族譜 — 教派傳統視角圖層

> 📜 **資料原則：comprehensive over doctrinal** — 任何傳統有列的人物與世系都儘量收錄，不因某派宗教權威否認而排除。例如穆聖訓示「譜系家追溯阿德南以前祖先是撒謊」(الناس يكذبون النسابة) 我們**不採信**為理由刪減資料；Ibn Hisham《Sirat Rasul Allah》既已詳列 21 代伊斯瑪儀↔阿德南 chain，照列。立場：使用者看完整圖像自己判斷，不替使用者做宗教審查。

> 姊妹 skill: [[genealogy-biblical]] — 兩套族譜共用相同 DB schema 模式（per-person `tradition` 列 + JSONB override 三件套），只是傳統值集合 + 視覺顏色不同。

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

已完成腳本（c:\tmp）— 跑過順序大致（🧹 c:\tmp 已依 [[feedback_tmp_cleanup]] 清空，2026-07-08 確認以下檔案均已不存在；僅留作歷史紀錄與 idempotent pattern 參考，要重用需重寫）：
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

> 配色避開 genealogy-biblical 使用的 amber（spine A）／rose（spine B 同 rose-50 衝突需注意）。
> 紅色 rose-50 已用於 biblical 女性卡 + 十二派伊瑪目；同一頁不會混用所以無衝突。

---

## 📜 視圖機制（累進納入，鏡像 biblical 的 `?view=` 邏輯）

URL：`/genealogy/islamic-tree?view=quranic|sunni|shia_twelver|shia_ismaili|shia_zaidi`

| view | 顯示 tradition |
|---|---|
| `quranic` | `quranic` only — 25 先知 + 古蘭點名（spine 不連貫，嚴格過濾） |
| `sunni`（預設） | `quranic` + `sunni` + `historical` |
| `shia_twelver` | 上述 + `shia_twelver` + JSONB override |
| `shia_ismaili` | quranic + sunni + `shia_ismaili` + JSONB override |
| `shia_zaidi` | quranic + sunni + `shia_zaidi` + JSONB override |

> 預設 sunni 因為 spine 必經中段（伊德里斯系、阿德南→穆罕默德 22 代）皆 sunni 傳述。`sunni`/`shia_*` 不互相納入彼此的伊瑪目人物。十二派 / 伊斯瑪儀派分支點：嘉法爾·薩迪克 (gen 69) 之後。

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

### 跨代婚姻處理

阿里（艾比·塔利卜之子, gen 65）娶 法蒂瑪（穆聖之女, gen 66）— 阿里在族譜兩處（堂弟線 / 女婿線）出現，已用 ♻ 同人標記跨樹顯示（仿 biblical：`makeLNode` 加 `allowDup` flag、id 加 `:dup<N>` 後綴避免 Vue key 衝突、卡片右上角藍色 ♻ marker 點擊跳對位）。`minGen` 機制暫未實作，視覺上以「兩棵獨立子樹各自顯示」為過渡解。

---

## 🚧 待辦

- ⏳ **伊瑪目之配偶與其他子女** — 目前只填了直系傳承的伊瑪目，配偶與旁支子女未補
- ⏳ **鄂圖曼蘇丹自稱哈里發**（1517-1924）— 不在血脈內，可選擇加入
- ⏳ **跨代婚姻 minGen 機制** — biblical 同類問題（猶大↔她瑪）未處理；做法 (a) graph endpoint 加 cross-subtree spouse edge 渲染，或 (b) 同人 ♻ 多卡（目前阿里已用 b 解）

---

## 🔑 關鍵 spec / 規則

1. **古蘭優先** — 古蘭明文人物（25 先知 + 古蘭點名者）必為 `quranic`，不可降階為 `sunni`
2. **不批次 propagate disambiguator** — 套用 [feedback_biblical_name_rules](../../../memory/feedback_biblical_name_rules.md) 同則
3. **中文音譯走伊斯蘭傳統，不沿用聖經和合本** — 該隱→蓋比勒、亞伯→哈比勒、利未→拉維、雅各→葉爾孤白、約瑟→優素福、雅弗→雅菲斯、含→哈姆、寧錄→尼姆魯德 等 68 名已批次 rename（見 `islamic_arabic_rename.py`）。新增以色列線人物時，先查 `RENAME` map 或 Arabic 拼寫，不要直接抄聖經中文名
4. **kunya（父子稱呼）** — 阿拉伯人「Abu X / Umm X / Ibn X / Bint X」是文化專有，獨立放 `kunya` 欄不要混入主名
5. **gen 計數 freeze** — 阿丹 = 1；穆罕默德 = 65；末伊瑪目馬赫迪 = 75；現代約旦阿卜杜拉二世 = 105。蓋達爾↔阿德南中段已改用 Ibn Hisham 21 代版本，伊斯瑪儀血親全鏈 gen 已 +16
6. **新批次資料 idempotent pattern** — fetch_all → set existing → INSERT skip-if-exists；parent 用 `_parent` field 同步 patch parent.children；gen shift 用 BFS（見 `islamic_ibn_hisham_migration.py` 範本）
7. **PowerShell 全授權**（per [feedback_powershell_full_auth](../../../memory/feedback_powershell_full_auth.md)）
8. **有改動自動 git push**（per [feedback_auto_push](../../../memory/feedback_auto_push.md)）

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

## 視覺驗收

- `node scripts/islamic-shot.mjs` — 預設 sunni view 截圖（仿 biblical-shot.mjs）
- `node scripts/islamic-shot.mjs --view shia_twelver --focus 哈桑·伊本·阿里 --zoom 0.8`
- `node scripts/islamic-shot.mjs --focus 烏姆·薩拉瑪 --zoom 1.1` — 看穆聖 12 妻 2 行 stack
- `node scripts/islamic-prophet-shot.mjs` — 先知鏈展開驗收
- `node scripts/islamic-branch-shots.mjs` — 朝代分支驗收
- `node scripts/check_eve_dom.mjs` — DOM 驗證（列 Adam/Eve/Muhammad/12 妻位置）

## 新增資料的標準流程

1. 查 DB 現況（原 `c:/tmp/islamic_stats.py` 已清空，需重寫小型 REST 統計腳本）
2. 撰寫批次 script 跟 `islamic_ibn_hisham_migration.py` / `islamic_side_branches.py` 等 idempotent pattern（原檔已清，pattern 見上方腳本清單描述與「關鍵 spec #6」）
3. 跑 script → 用 `islamic_check_state.py` 確認 row 數與 gens
4. 視覺驗收（islamic-shot.mjs --focus 新人物）
5. 更新本 SKILL.md（人物世系區 + scripts list）→ commit + push

## 🔍 資料一致性稽核（2026-07-08）

`python -X utf8 scripts/genealogy_data_audit.py --table islamic_people [--fix]` — 懸空引用/變體引用/wife-children 對齊/spouse 互指四類檢查＋Tier-1 機械修復。本日全歸零：新建 20 缺 row（卡爾巴拉烈士阿里·艾克巴爾/艾斯加爾/阿巴斯、艾布·伯克爾三子女、艾比·塔利卜諸子、伊本·歐麥爾、哈納菲耶、現代哈希姆費薩爾一世等），388→408 人。⚠️ 神學紅線寫死在腳本：爾撒無父只掛麥爾彥（ISLAMIC_KID_SKIP）；宰娜卜之子阿里（夭折）≠ 阿里·伊本·艾比·塔利卜（ISLAMIC_FALSE_FRIENDS）。
