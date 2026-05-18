---
name: episcopal-tradition-layer
description: 使徒統緒族譜圖（/genealogy/episcopal-tree）的資料維護政策、教座清單、傳統主教列表規則。Use when 加新教座／補主教鏈／修使徒寶座傳統名單／調整 SPINE_DEFS／處理教座分裂 vs 並行對立。
---

# 使徒統緒族譜圖 — 資料維護政策

頁面：`/genealogy/episcopal-tree`（族譜視圖）+ `/genealogy/episcopal`（表格視圖）

資料表：`episcopal_sees`（教座）、`episcopal_succession`（主教鏈）、`church_teachings`（師徒/祝聖關係）

主要程式：
- API：[server/api/genealogy/episcopal-graph.get.ts](../../server/api/genealogy/episcopal-graph.get.ts)
- 元件：[components/genealogy/EpiscopalSpineTree.vue](../../components/genealogy/EpiscopalSpineTree.vue)
- 頁面：[pages/genealogy/episcopal-tree.vue](../../pages/genealogy/episcopal-tree.vue)
- 截圖：[scripts/episcopal-shot.mjs](../../scripts/episcopal-shot.mjs)

## 編輯規則：一律按傳統說法

**像羅馬教宗列表一樣**——只要該教座有「傳統公認」的主教名單就**全部列出**，不需要等到「學界可考史料」才加。使徒時代的傳說性主教（例如 凱撒利亞·巴勒斯坦 #1 撒該、羅馬 #1 彼得）一律按傳統紀年列入，notes 欄位說明史料來源即可，**不要用 `status='傳說'` 把他們區別開來**。

判斷依據：
- 有傳統教會歷史（Eusebius《Historia Ecclesiastica》、Movses Khorenatsi、Ormanian、Le Quien 等）公認的繼任名單 → 列
- 完全無記載、只是「應該存在過」的空檔 → 留空 notes 註明
- 殘缺 / 史料前段空白（如埃奇米亞津 191-239 年）notes 註明即可，不要用 `status='傳說'` 把人別開

## Archbishop / Metropolitan / Catholicos 中文翻譯慣例

| 英文 | 東正教 / 天主教 | 聖公會 / 信義宗 |
|---|---|---|
| Archbishop | **總主教** | 大主教 |
| Metropolitan | 都主教 | 都主教 |
| Patriarch | 宗主教 | — |
| Catholicos | Catholicos / 大公主教 | — |

新增資料時請按此分流。

## `tradition` 分類規則：嚴格 7 大正統

**`tradition` 欄位只能是 7 個值，不要擅自開新類別。** 即使該教座是某傳統的分裂、改革、自主、自治、合一支系，仍然歸到「最終屬於哪個傳承大宗」：

1. **羅馬公教** — 包括拉丁禮、東方禮天主教、對立教宗
2. **希臘正教** — 包括所有自主/自治東正教（保加利亞、塞爾維亞、俄羅斯、希臘、北馬其頓 OCU…）、卡帕多西亞教父等
3. **科普特正教** — 亞歷山卓非迦克墩派 + 衣索比亞 + 厄立特里亞
4. **敘利亞正教** — 安提阿非迦克墩派 + 馬蘭卡拉雅各派 + 馬爾托馬（改革派、雖受聖公宗影響但結構仍承自敘利亞正教，是其獨立支系）
5. **亞美尼亞使徒教會** — 埃奇米亞津 + 奇里乞亞 Catholicosate
6. **亞述景教** — 塞琉西亞-泰西封古代東方 + 亞述派 + 印度多馬古代線
7. **基督新教** — 聖公宗、信義宗、衛理、長老、改革宗、新興教會等

判斷原則：
- 「在哪邊脫離 / 與誰共融」決定 tradition（不是禮儀風格）
- 與羅馬共融 = 羅馬公教（不管什麼禮儀）
- 從敘利亞正教 / 古代東方教會 / 亞美尼亞使徒等正教傳統獨立 = 仍歸該正教傳統
- 16 世紀宗教改革後在歐美建立的非天主教教會 = 基督新教
- **不要開**「使徒教會」「東正教自主」「東正教自治」「東方禮天主教」「西方大分裂」「卡帕多西亞教父」「改革派敘利亞」等中間類別——全部應該歸進上述 7 大

## 7 大 spine 結構

定義在 `SPINE_DEFS`（[episcopal-graph.get.ts](../../server/api/genealogy/episcopal-graph.get.ts)）。每 spine 一個 `primaryApostleId` + 可選 `secondaryApostleId`，`patriarchateYear` 標宗主教座正式建立年份（線條粗細在此切換）。

| spine key | see_zh | 主使徒 | 輔使徒 | spine 色 | patriarchateYear |
|---|---|---|---|---|---|
| `rome` | 羅馬 | 彼得 | 保羅 | `#dc2626` 紅 | 451 |
| `constantinople` | 君士坦丁堡 | 安得烈 | — | `#2563eb` 藍 | 451 |
| `alexandria` | 亞歷山卓 | 彼得 | 巴拿巴 | `#d97706` 橙 | 451 |
| `antioch` | 安提阿 | 彼得 | — | `#0891b2` 青 | 451 |
| `jerusalem` | 耶路撒冷 | 義人雅各 | — | `#16a34a` 綠 | 451 |
| `armenia` | 埃奇米亞津 | 達太 | 巴多羅買 | `#9333ea` 紫 | 484 |
| `assyria` | 塞琉西亞—泰西封 | 多馬 | — | `#475569` 灰 | 410 |

## primaryChurches vs rivalChurches

**`primaryChurches`**：時序接續、無重疊的多個 church 名稱合併在同一條 spine 線上
- 例：羅馬 `['未分裂教會', '天主教']`（1054 大分裂後 天主教 接續未分裂教會）
- 例：君士坦丁堡 `['未分裂教會', '東正教']`

**`rivalChurches`**：並行存在的對立教會，自動產生 `is_split=true` 的合成分支（紅色鋸齒線）
- 例：assyria 的 `rivalChurches: ['東方教會（亞述）']`（1968 後與 古代東方教會 並存）
- attach 點：rival 第一位主教的 `start_year` 對應 spine 同期主教

**如果是時序接續就用 primary，如果是並行對立就用 rival——不要混用，會交錯排序看起來像 bug**

## 旁支（branch see）結構

凡 `episcopal_sees.parent_see_id` 指向 spine 的主 see 或另一個旁支 see → BFS 找到後成為旁支，可在 spine 圖點 ▸ 展開。

**三種視覺差異（重要）：**

| see_zh vs parent | split_year | 視覺 | 語義 | 例 |
|---|---|---|---|---|
| 同名 | 有 | 紅色鋸齒線 | 教座分裂（爭奪同一寶座 / 改宗傳承） | 對立教宗（亞威農 / 比薩），Old Catholic，坎特伯里|英格蘭教會 ← 坎特伯里|天主教，烏普薩拉|瑞典信義會 ← 烏普薩拉|天主教 |
| 不同名 | 有 | spine 色實線 + 顯示 split_year | 自主獨立教會 | 莫斯科 1448 ← 君士坦丁堡，雅典 1833 ← 君士坦丁堡 |
| 不同名 | 無 | spine 色實線 + 顯示 founded_year | 母教座差派設立 | 米蘭 ← 羅馬（巴拿巴），坎特伯里 ← 羅馬（額我略一世派奧古斯丁） |

**關鍵規則：**
- **教宗 / 母 spine 主教差派設立的子教座** → 不同 see_zh + 無 split_year（藍實線「設立」）
- **同一寶座的對立 / 改宗承繼** → 同 see_zh + 設 split_year（紅鋸齒「分裂」）
- **不同地理位置但宣告獨立** → 不同 see_zh + 設 split_year（藍實線 + 年份）

預期將來會擴張到「一個宗主教座下面延伸很多教座傳承」，spine column 之間預留了 horizontal space。

## 教座 → parent 接法（資料 audit 政策）

每個教座一定要 `parent_see_id` 指到某處（不能孤兒），否則不會出現在族譜圖上。指派原則：

**羅馬公教教座：**
- Post-600 一般拉丁禮 → `parent=rome` 直屬（教宗差派時代）
- Pre-600 拉丁禮 → 按地區族群接母 metropolis（教宗權尚不穩固，地方總主教祝聖）：Hispanic→托萊多、Gallic→里昂、Germanic→特里爾、Italian/Insular/African→rome 直屬
- 對立教宗（Avignon / Pisa）→ see_zh="羅馬"、parent=rome、設 split_year，紅鋸齒
- Old Catholic（反 Vatican I 1871/1873/1874/1897）→ 同對立教宗法
- 東儀天主教（Maronite / Melkite / Chaldean / Coptic Cath / Syriac Cath / Armenian Cath / Ukrainian GC）→ rename see_zh 成對應東方母 spine 的 see_zh、parent=該 spine、設 split_year，紅鋸齒

**東方教會教座：**
- 國家層級的 Orthodox 自主教會（俄羅斯/塞爾維亞/羅馬尼亞/保加利亞/希臘 等）已建檔為 君堡 旁支
- 該國境內的城市 diocese → 接國家層級的母教會（如 第比利斯 → 姆茨赫塔、聖彼得堡 → 莫斯科、明斯克 → 莫斯科）
- 古希臘教會 Pauline 教座（科林斯/帖撒羅尼迦/克里特/帕特雷 等）→ 君堡 直屬
- Old Believers / Old Calendar → 接對應母會（莫斯科 / 雅典）+ 設真正的 schism 年份

**基督新教教座：**
- 看是否承接古老的 Catholic / Orthodox 教座
  - **是**（同城繼承，宗教改革轉變）→ 同 see_zh、parent=該古老母 see、split_year=宗教改革年（如 烏普薩拉|瑞典信義會 ← 烏普薩拉|天主教 split=1531；圖爾庫 split=1527；里加 split=1522）
  - **否**（新立傳教教座，無歷史前身）→ parent=rome、split_year=founded_year（藍線「設立」自拉丁基督教體系；如 漢諾威 1948、棉蘭 1861、衣索比亞福音 1959）
- 聖公宗 mission 子教座 → parent=坎特伯里|英格蘭教會

## split_year 機制

當 `episcopal_sees.split_year` 設了之後，API 旁支 BFS 會：
1. **過濾掉 `start_year < split_year` 的主教**（避免重複 spine 上的 pre-split 同人）
2. **用 split_year 取代 founded_year** 作為旁支卡片顯示年份（更貼近語義：「這條線是從何時分出來的」）
3. **用 split_year 作 attach 點 Y**（分裂線從那一年的同期 spine 主教接出來）

適用所有並行對立分支（科普特正教 451、奇里乞亞 1293、亞美尼亞天主教 1742、保加利亞 870 等）。

## 負 succession_number 慣例

某些教座有「使徒寶座傳統 / 正史前」主教列表，需要排在官方 #1 之前：

| 教座 | 例 | 處理 |
|---|---|---|
| 埃奇米亞津 | 達太傳統 8 位（撒杜克 → 美侯讓，68-270 AD） | succession_number `-8..-1`，格利高爾續 `#1` |
| 米蘭 | 巴拿巴 50 年奠基（安波羅西禮不算進主教編號內） | succession_number `-1` |

**規則：API 把負 succession_number 在輸出時轉成 `null`**（前端不顯示編號數字），但**排序仍用原值**——負數自然排在正數之前，無需修改 sort 邏輯。

要在其他教座加類似列表：DB 主教用 `succession_number = -N .. -1` 寫入，不需要改 SPINE_DEFS 或前端 code。

## 跨 spine 祝聖關係：church_teachings

教座之間的「祝聖／教導」關係寫進 `church_teachings`。前端 SVG 用橘色實線 + 細邊（`#ea580c`）畫師徒線。若 institutional spine/branch 鏈已連通則略過（教座傳承 takes precedence over 教導關係）。

例：萊昂提烏斯（凱撒利亞·卡帕多西亞 #4）→ 聖額我略·啟蒙者（埃奇米亞津 #1），302 年祝聖

## Layout 規格（前端 `EpiscopalSpineTree.vue`）

- **七大宗主教按順序「平均分配」橫排**：每個 spine 獨立 slot（SPINE_BETWEEN_GAP=36），不按 primary apostle group
- **16 使徒平均分配**橫排在 spine 之上（APO_HG=20）
- **預設所有 branch 收起來**：使用者按 ▸ 才一個個展開（watch `props.graph` 寫滿 `collapsedBranches` Set）
- **預設 zoom = fit-to-width**：rome 261 任主教 ≈ 30000px 高，fit-to-height 會壓到 3% 不可讀
- **Spine 主線 opacity = 0.55**（之前 0.10 看不到傳承）；patriarchateYear 後加粗（width 10）強化「宗主教座成立」
- **每個 spine 至少預留 1 個 branch slot 寬度**，避免 collapsed branch headers 溢出到下一個 spine 領域

## 截圖工具

[scripts/episcopal-shot.mjs](../../scripts/episcopal-shot.mjs) — headless：
- 預設 1800×1200 viewport（**勿超 2000px，會炸 session**）
- `--zoom 0.55` 看全圖縮覽；`--zoom 1.0` 看細節
- `--expand <branchId>` 展開某旁支
- `--panX <dx>` 微調水平 pan
- 環境變數 `APP_BASE`（dev server port）

## 教座清單

DB 是 source of truth。截至最近紀錄：**7 大 spine + 330 旁支教座**（其中 23 個 Protestant orphan 已於 Stage 7 接 rome）。
- 主要傳承群：羅馬（西方大分裂對立教宗、米蘭、歐美天主教教區）、君士坦丁堡（古代/中世紀/19-21 世紀自主與自治教會、小亞細亞 7 教會、姆茨赫塔喬治亞）、亞歷山卓（科普特正教含 4 大修道院 + 努比亞古代教座、衣索比亞、厄立特里亞）、安提阿（馬龍尼特、麥勒基特、敘利亞正教、凱撒利亞·巴勒斯坦/卡帕多西亞、以弗所、塞浦路斯、大馬士革）、耶路撒冷（拉丁禮、亞美尼亞耶城）、埃奇米亞津（奇里乞亞、亞美尼亞天主教）、塞琉西亞-泰西封（古代東方 + 亞述派 rival + 馬拉巴爾系列 + 古代景教阿爾比/尼西比斯/默夫/撒馬爾罕/長安）
- 新教改革後：聖公宗（坎特伯里→各國 Province）、信義宗（北歐 + 各國）、衛理宗（巴爾的摩→各國分支）

查清單直接 `SELECT see_zh, church, tradition, founded_year, split_year FROM episcopal_sees ORDER BY founded_year`。
