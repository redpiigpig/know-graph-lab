---
name: episcopal-tradition-layer
description: 使徒統緒族譜圖（/genealogy/episcopal-tree）+ 主教表格／卡片（/genealogy/episcopal）的資料維護政策、教座清單、傳統主教列表規則、肖像回填 pipeline。Use when 加新教座／補主教鏈／修使徒寶座傳統名單／調整 SPINE_DEFS／處理教座分裂 vs 並行對立 vs 改革轉變／補主教肖像。
---

# 使徒統緒族譜圖 — 資料維護政策

頁面：`/genealogy/episcopal-tree`（族譜視圖）+ `/genealogy/episcopal`（表格視圖）

資料表：`episcopal_sees`（教座）、`episcopal_succession`（主教鏈）、`church_teachings`（師徒/祝聖關係）

主要程式：
- API：[server/api/genealogy/episcopal-graph.get.ts](../../server/api/genealogy/episcopal-graph.get.ts)
- 主教詳細卡 API：[server/api/genealogy/episcopal-bishop/[id].get.ts](../../server/api/genealogy/episcopal-bishop/[id].get.ts)
- 元件：[components/genealogy/EpiscopalSpineTree.vue](../../components/genealogy/EpiscopalSpineTree.vue)
- 主教卡 modal：[components/genealogy/BishopCard.vue](../../components/genealogy/BishopCard.vue)
- 頁面：[pages/genealogy/episcopal-tree.vue](../../pages/genealogy/episcopal-tree.vue)、[pages/genealogy/episcopal.vue](../../pages/genealogy/episcopal.vue)
- 通用肖像 fallback：[public/episcopal-portraits/](../../public/episcopal-portraits/)（rome/constantinople/alexandria/antioch/armenia/assyria/protestant.svg）
- 截圖：[scripts/episcopal-shot.mjs](../../scripts/episcopal-shot.mjs)
- 名單匯出：[scripts/episcopal-audit-export.mjs](../../scripts/episcopal-audit-export.mjs) → `scripts/episcopal-sees-337.txt` + `episcopal-incomplete-bishops.txt`

## 主教卡片（BishopCard modal，2026-05-19 上線）

`/genealogy/episcopal` 表格列點 row → 開大張主教卡片 modal。資料來自 `/api/genealogy/episcopal-bishop/[id]`。

**卡片區塊（top-down）：**
1. Header：tradition spine 色 bar + see_zh / tradition
2. 肖像：`portrait_url` → 真實照片；否則 fallback 到該 tradition 的通用 SVG（7 種）
3. 身份：中文名 + #N + 英文名 + tradition/church/status badges
4. 任期 + 卸任原因 + 任命者 inline rows
5. 使徒按立鏈：consecrator + consecrated（clickable，點即跳到該主教卡）
6. 師徒關係：`church_teachings` 雙向（teachers/students），橘色 link
7. 事蹟／神學立場：`notes`
8. 史料來源：`sources`
9. 編輯肖像連結：collapsed details 內 + 即時 PATCH `portrait_url`
10. Footer：前一任 / 下一任 navigation（同 see 的 siblings；←→ 鍵盤也可）

**DB schema：** `episcopal_succession.portrait_url TEXT`（2026-05-19 新增）。沒值就 fallback。

## 編輯規則：一律按傳統說法

**像羅馬教宗列表一樣**——只要該教座有「傳統公認」的主教名單就**全部列出**，不需要等到「學界可考史料」才加。使徒時代的傳說性主教（例如 凱撒利亞·巴勒斯坦 #1 撒該、羅馬 #1 彼得）一律按傳統紀年列入，notes 欄位說明史料來源即可，**不要用 `status='傳說'` 把他們區別開來**。

判斷依據：
- 有傳統教會歷史（Eusebius《Historia Ecclesiastica》、Movses Khorenatsi、Ormanian、Le Quien 等）公認的繼任名單 → 列
- 完全無記載、只是「應該存在過」的空檔 → 留空 notes 註明
- 殘缺 / 史料前段空白（如埃奇米亞津 191-239 年）notes 註明即可

## Archbishop / Metropolitan / Catholicos 中文翻譯慣例

| 英文 | 東正教 / 天主教 | 聖公會 / 信義宗 |
|---|---|---|
| Archbishop | **總主教** | 大主教 |
| Metropolitan | 都主教 | 都主教 |
| Patriarch | 宗主教 | — |
| Catholicos | Catholicos / 大公主教 | — |

## `tradition` 分類：嚴格 7 大正統

**`tradition` 欄只能是 7 個值**。即使是某傳統的分裂、改革、自主、合一支系，仍歸到「最終屬於哪個傳承大宗」：

1. **羅馬公教** — 拉丁禮、東方禮天主教、對立教宗
2. **希臘正教** — 所有自主/自治東正教
3. **科普特正教** — 亞歷山卓非迦克墩 + 衣索比亞 + 厄立特里亞
4. **敘利亞正教** — 安提阿非迦克墩 + 馬蘭卡拉雅各派 + 馬爾托馬
5. **亞美尼亞使徒教會** — 埃奇米亞津 + 奇里乞亞 Catholicosate
6. **亞述景教** — 塞琉西亞-泰西封古代東方 + 亞述派 + 印度多馬古代線
7. **基督新教** — 聖公宗、信義宗、衛理、長老、改革宗、新興教會

判斷原則：「在哪邊脫離 / 與誰共融」決定 tradition；不要開「使徒教會」「東正教自主」「東方禮天主教」「西方大分裂」等中間類別。

## 7 大 spine 結構

定義在 `SPINE_DEFS`（[episcopal-graph.get.ts](../../server/api/genealogy/episcopal-graph.get.ts)）。

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

**`primaryChurches`**：時序接續、無重疊的多個 church 名稱合併在同一條 spine 線上（例：羅馬 `['未分裂教會', '天主教']`）。

**`rivalChurches`**：並行存在的對立教會，自動產生 `is_split=true` 合成分支（紅鋸齒外圈曲線）。
- 例：assyria 的 `rivalChurches: ['東方教會（亞述）']`（1968 後與 古代東方教會 並存）

時序接續就用 primary，並行對立就用 rival——不要混用。

## 三種視覺差異（重要）

| see_zh vs parent | split_year | 視覺 | 語義 |
|---|---|---|---|
| 同名 | 有 | **紅鋸齒外圈 Bezier 曲線 + 預設展開 + 不進選單** | 教座分裂（爭奪同一寶座／改宗承繼） |
| 不同名 | 有 | spine 色實線 + 顯示 split_year | 自主獨立教會（autocephaly） |
| 不同名 | 無 | spine 色實線 + 顯示 founded_year | 母教座差派設立 |

**關鍵規則：**
- **教宗 / 母 spine 主教差派設立的子教座** → 不同 see_zh + 無 split_year（藍實線「設立」）
- **同一寶座的對立 / 改宗承繼** → 同 see_zh + 設 split_year（紅鋸齒 + 預設展開）
- **不同地理位置但宣告獨立** → 不同 see_zh + 設 split_year（藍實線 + 年份）

## 改革／分裂的兩種模式

**Pattern A — 完全轉變（單一傳承延續）**：天主教結束、新教接續同一個 see，無 parallel Catholic 繼續存在。
- 處理：**合併成單一 record**，church=新教派、tradition=基督新教、founded_year=原始年、split_year=null
- 新教主教 succession_number 接續舊天主教 max+1（如 烏普薩拉 Lutheran #1 → #22）
- 第一位新教主教的 notes 加「{YEAR} 宗教改革：天主教 → {新教派}」
- 例：圖爾庫 (1554)、烏普薩拉 (1531)、雷克雅維克 (Iceland)、奧斯陸、哥本哈根
- ⚠ **renumber 時要從後往前 update**（避免 unique constraint `(see, church, succession_number)` clash）

**Pattern B — 平行並存（天主教與新教雙線到今）**：兩個 record，新教變 is_split 分支。
- 處理：**保留兩個 record**。Catholic 主線（parent=rome）+ Protestant `is_split=true` 旁支（parent=Catholic 主線、split_year=改革年）
- 例：坎特伯里 (1533)、約克 (1534)、都柏林 (1536)、阿馬 (1536)、里加 (1522)
- 視覺：紅鋸齒外圈曲線、預設展開、不進選單

## 教座 → parent 接法（資料 audit 政策）

每個教座一定要 `parent_see_id` 指到某處（不能孤兒），否則不會出現在族譜圖上。

**羅馬公教：**
- Post-600 一般拉丁禮 → `parent=rome` 直屬
- Pre-600 拉丁禮 → 按地區族群接母 metropolis：Hispanic→托萊多、Gallic→里昂、Germanic→特里爾、Italian/Insular/African→rome 直屬
- 對立教宗 / Old Catholic → see_zh="羅馬"、parent=rome、設 split_year（is_split=true）
- 東儀天主教（Maronite/Melkite/Chaldean/Coptic Cath/Syriac Cath/Armenian Cath/Ukrainian GC）→ rename see_zh 成對應東方母 spine 的 see_zh、parent=該母 spine 或同地對立 see、設 split_year

**東方教會：**
- 國家層級 Orthodox 自主教會（俄羅斯/塞爾維亞/羅馬尼亞/保加利亞 等）為 君堡 旁支
- 該國境內的城市 diocese → 接國家層級母教會（如 第比利斯→姆茨赫塔、聖彼得堡→莫斯科）
- Old Believers / Old Calendar → 接母會 (莫斯科 / 雅典) + 設真正 schism 年（1666/1924 等）
- 亞美尼亞使徒教會在 君堡/耶城/基里基亞 的 sub-Patriarchates → parent=埃奇米亞津（不是 Greek Orthodox 分裂）

**基督新教：**
- 看是否承接古老 Catholic / Orthodox 教座
  - **是（Pattern A 或 B）** → 同 see_zh、parent=該古老母 see、split_year=改革年
  - **否**（新立傳教教座，無歷史前身）→ parent=rome、split_year=founded_year（藍線「設立」自拉丁基督教體系）
- 聖公宗 mission 子教座 → parent=坎特伯里|英格蘭教會

## 使徒源頭教座（apostolic-founded sees）— `founder_apostle_id` 欄

某些古老教座不是「君堡/羅馬差派出來的」而是使徒親建。`episcopal_sees.founder_apostle_id`（值 = `ap_paul`/`ap_thomas`/...）標記後 API 會：
1. 把這 see（與子孫）**從 spine BFS 排除**
2. 放進 `apostolicBranches` 陣列，附 `parent_apostle_id`
3. 前端：apostle card 顯示 ▸ + 分支數，**預設收起**，點擊才展開（琥珀色 `#a16207`）

**目前 28 個使徒源頭教座 / 7 個使徒**：
- 保羅：哥林多、科林斯、帖撒羅尼迦、克里特、多德卡尼斯、以弗所、大馬士革、普洛夫迪夫
- 巴拿巴：塞浦路斯、米蘭
- 安得烈：帕特雷、托米斯、姆茨赫塔、第比利斯、格魯吉亞
- 多馬：馬拉巴爾（含 1912 馬蘭卡拉東正教）
- 彼得：凱撒利亞·巴勒斯坦、凱撒利亞·卡帕多西亞
- 約翰：士每拿、別迦摩、推雅推喇、撒狄、非拉鐵非、老底嘉
- 雅各（西庇太之子）：布拉加、托萊多、塔拉戈納

## split_year 機制

當 `split_year` 設了之後 API 旁支 BFS 會：
1. 過濾掉 `start_year < split_year` 的主教（避免重複 spine 上的 pre-split 同人）
2. 用 split_year 取代 founded_year 作為旁支卡片顯示年份
3. 用 split_year 作 attach 點 Y（分裂線從那一年的同期 spine 主教接出來）

## 主教排序

API 對主教排序的順序：
```
1. start_year 升序（chronological 優先）
2. start_year 相同 → succession_number 升序當 tiebreaker
```

⚠ 必須 chronological 優先，否則 succession_number=0 / 負數的傳統「奠基者」會被誤排到後人前面（如 那不勒斯 聖真納羅 succession=0 但 year=303 不能排在 #1 1740-1758 前）。

**負 succession_number 慣例**：傳統奠基者用 `-N..-1`（如 米蘭 巴拿巴 #-1、埃奇米亞津 達太傳統 #-8..-1）。API 輸出時 `succession_number<=0 ? null : ...` 把編號隱藏。排序自動正確（巴拿巴 50 < 阿那多利 100）。

## 跨 spine 祝聖關係：church_teachings

教座之間的「祝聖／教導」關係寫進 `church_teachings`。前端 SVG 用橘色實線（`#ea580c`）畫師徒線。

**過濾規則**：若兩個 bishop 在同一 column（同 spine / 同 branch / 同使徒立座）一律當機構性傳承，**不畫教導橘線**（避免如 Peter→Clement #4 跨任造成的視覺混亂）。

例：萊昂提烏斯（凱撒利亞·卡帕多西亞 #4）→ 聖額我略·啟蒙者（埃奇米亞津 #1），302 年祝聖。

## Layout 規格（前端 `EpiscopalSpineTree.vue`）

- **七大宗主教按順序「平均分配」橫排**（SPINE_BETWEEN_GAP=36）
- **16 使徒平均分配**橫排在 spine 之上
- **使徒→宗主教 fan 線錯開**：每個 spine 用獨立 midY (`baseMidY + i*8`)，避免重疊
- **西方教會（rome）旁支往左、6 大東方傳統旁支往右**（`branchDir`）；rome 的 see label 也 mirror 到右側、canvas 加 `ROME_LEFT_RESERVE` 留左邊給 rome 旁支
- **預設所有 branch 收起來**，但 `is_split=true` **預設展開**（對立分支隨母教宗一起呈現）
- **預設 zoom = fit-to-width**（rome 261 任主教 ≈ 30000px 高，fit-to-height 會壓到 3% 不可讀）
- **Spine 內主教傳承用 per-segment 短線**（不再用 unified 長 guide）：
  - 連續 succession_number → 實線
  - 跳號（缺資料）→ **點線** + 降 opacity 0.45
  - patriarchateYear 後 width 3 → 6 加粗
- **Branch 主教鏈同上**（per-segment + 跳號點線）
- **Branch 連接線改單一斜線**（不是 L 形，避免多支共用 midX 堆出假直線）
- **is_split 連接線：Bezier 外圈曲線**（control point 拉到分支外側 80px）

## Focus mode（避免覆蓋）

在 `renderBranches` 中追蹤 `focusYEnd`（上一個展開分支的主教鏈 Y 末端）。同 depth 的下一個兄弟分支若 `attachY < focusYEnd` → `continue` 不渲染。同時 `lastBranchYByDepth` 更新到 `chainEndY`。

效果：點開某分支主教鏈 → 那段 Y 區域只看到該分支，其他兄弟分支自動讓位/隱形。

## 多教座按立選單（exclusive reveal）

- 1 個子座 → inline 顯示
- 2+ 子座 → 全部摺進主教卡片右側「+N 被立」紫色 badge
  - 例外：`is_split=true` 永不進選單（總是並行顯示）
- 點 badge → popup menu 列出所有同教宗的子座
- 點 menu 某項 → **exclusive reveal**：只 reveal 那一個、同教宗其他兄弟子座自動回 menu 隱形
- State：`revealedFromMenu: Set<branchId>`、`openMenuBishopId: string | null`

## 導航功能：搜尋框

頂部 input 即時 filter，索引含：使徒、spine 主 see、spine 主教、旁支 see、旁支主教、使徒立座 see+主教。

- 中文名 / 英文名 / 教座名 / 任期年份 全字串 substring match
- 點結果 → 自動展開必要的 branch / apostle、`nextTick` 後 pan canvas 居中 + violet ring highlight 3s

## 截圖工具

[scripts/episcopal-shot.mjs](../../scripts/episcopal-shot.mjs) — headless：
- 預設 1800×1200 viewport（**勿超 2000px，會炸 session**）
- `--zoom 0.55` 看全圖；`--zoom 1.0` 看細節
- `--expand <branchId>` 展開某旁支；`--panX <dx>` 微調水平 pan
- 環境變數 `APP_BASE`（dev server port）

## 教座清單與名單匯出

DB 是 source of truth。截至最新（2026-05-19）：**7 大 spine + 387 旁支教座 / 5,401 主教**（含 28 使徒立座、38+ 個 is_split 分裂分支）。

**最近補完項目（2026-05-19）**：
- 古代教父教座：希波（奧古斯丁）、尼撒、拿先斯、希拉波利斯（帕皮亞）、安卡拉、居勒拿、居魯士（提奧多禮）、摩普綏厄斯提亞（提奧多）、埃德薩（Ibas）
- Catholic 中世紀/近世：阿維尼翁、馬賽、巴塞爾、比薩、蒙特卡西諾、維洛納、帕多瓦、雷根斯堡（大阿爾伯特）、馬德堡、沃姆斯、斯特拉斯堡、烏茲堡、科爾多瓦（何西烏斯）、薩拉曼卡、錫耶納
- Orthodox：諾夫哥羅德、弗拉基米爾、托博爾斯克、喀山、佩奇（聖薩瓦）、奧赫里德古代、普雷斯拉夫、加沙、特拉布宗、赫爾松、波羅茨克
- Oriental/Assyrian：巴格達加色丁、巴士拉、泉州（元代景教）、科欽、霍姆斯
- Anglican Reformers：倫敦（Ridley）、達勒姆（Cosin）、溫徹斯特（Andrewes）、索爾茲伯里（Jewel）、烏斯特（Latimer）、林肯（Grosseteste）、伊利、羅徹斯特（Fisher）、聖大衛、新加坡、拉各斯
- 台灣天主教 7 個教區（台北總教區/高雄/台中/台南/嘉義/新竹/花蓮）+ 台灣聖公會
- 4 個拉丁禮宗主教座（耶路撒冷、安提阿、君堡、亞歷山卓）補完歷代主教鏈
- 西奈山自治大主教 22 任、Cilicia 亞美尼亞使徒/天主教雙線
- 刪除 2 個亞美尼亞正教 duplicate 0 任記錄

剩餘 2 個 audit warning 屬歷史事實（比薩對立教宗線 1409-1415 只 2 任、亞述派 1968 後分裂只 4 任 Catholici）。

SQL 補丁批檔：[database/episcopal-fill-phase1.sql](../../database/episcopal-fill-phase1.sql) 至 [phase8.sql](../../database/episcopal-fill-phase8.sql)，依序刪除→補完→新增。

跑 `node scripts/episcopal-audit-export.mjs` 重新生成兩份 txt：
- `episcopal-sees-337.txt`：每個教座 + 完整按立軌跡鏈（耶穌→使徒/spine→...→自己）+ 標記類型（★宗主教/☆使徒立座/○旁支）
- `episcopal-incomplete-bishops.txt`：主教不齊的教座清單（依「宗主教座 ≥50」「自主分裂 ≥5」「使徒立座 ≥3」「現代教座 ≥1」分類）

查清單 SQL：`SELECT see_zh, church, tradition, founded_year, split_year FROM episcopal_sees ORDER BY founded_year`。

## BishopCard 主教卡片（`/genealogy/episcopal`）

點表格 row → 開中央 modal 大彈窗，顯示該主教完整資訊：

**12 個區塊（components/genealogy/BishopCard.vue）**：
1. 肖像區（160×200px）─ `episcopal_succession.portrait_url`（新欄）／無 → 套 7 tradition fallback SVG
2. 標題 ─ 中文名 + 英文名 + 任次 #N
3. 教座 ─ see_zh + church + tradition badge（用 7 spine 色）
4. 任期 ─ start_year – end_year + 年數
5. 身份 ─ status badge（正統／對立／廢黜後復位／爭議）+ end_reason
6. 任命者 ─ appointed_by 文字
7. 按立者 ─ consecrator_bishop_id → 可點跳到該主教卡片
8. 被他按立的人 ─ 反查 consecrator_bishop_id（reverse query）
9. 教導關係 ─ `church_teachings` 中的師徒線
10. 重要事件 / 神學立場 ─ notes 全文
11. 史料來源 ─ sources（Eusebius HE / Liber Pontificalis 等）
12. 上一任／下一任 ─ 同 see 前後 ←→ 翻頁

**API**：[server/api/genealogy/episcopal-bishop/[id].get.ts](../../server/api/genealogy/episcopal-bishop/[id].get.ts) — 含 consecrator + consecrated + teachings 三個 reverse join。

**7 tradition fallback SVG**（[public/episcopal-portraits/](../../public/episcopal-portraits/)）：每個 tradition 一張通用法冠 silhouette，無 portrait 時自動套用：
- 羅馬公教 `#dc2626` 紅 → 三重冕 tiara
- 希臘正教 `#2563eb` 藍 → 拜占庭主教冠
- 科普特正教 `#d97706` 橙 → 科普特十字 + 頭巾
- 敘利亞正教 `#0891b2` 青 → 敘利亞十字 + masnafto
- 亞美尼亞 `#9333ea` 紫 → vegharakir 頭冠
- 亞述景教 `#475569` 灰 → 亞述十字 + 頭巾
- 基督新教 `#16a34a` 綠 → 簡約十架 + 開卷聖經

## Portrait 回填 pipeline（Haiku batch + Wikipedia）

`episcopal_succession.portrait_url`（TEXT）為新增欄。回填以 **Haiku agent → Wikipedia REST API** 為主軸：

```
[prep] scripts/episcopal-portrait-prep-batches.py
  → 拉所有 portrait_url IS NULL & name_en IS NOT NULL 的候選
  → 依「著名教座+現代→古早」排序切 25/batch
  → 寫到 c:/tmp/episcopal_batches/batch_NNN.jsonl

[resolve] 主 Claude spawn Haiku Agent（subagent_type=general-purpose, model=haiku）
  每個 agent 25 row：
    1. 從 name + see + era 推 Wikipedia slug
    2. WebFetch en.wikipedia.org/api/rest_v1/page/summary/{slug}
    3. 驗證主教 ＝ 該人（era/see/denomination match）
    4. 試 1-2 個 alternative slugs 若 wrong
    5. 接受 paintings/photos/frescoes/mosaics/sculptures/miniatures；拒 coats of arms / churches / scene paintings
  → 寫 batch_NNN_haiku.json: {id, slug, portrait_url, status: HIT/NO_ARTICLE/NO_IMAGE/WRONG_PERSON}

[apply] scripts/episcopal-portrait-apply-haiku.py --skip-head
  → 讀 batch_NNN_haiku.json（utf-8-sig 容 BOM）
  → PATCH portrait_url 到 episcopal_succession
```

**規模**：210 batches × 25 rows = 5,245 candidates。Quota 限制下分 21 輪 × 10 平行 agents 完成。
**最終覆蓋率**（2026-05-21）：**1,902 / 5,401 主教 = 35.2%**

**Hit rate 變化**：
- 著名教座（教宗、Canterbury 1500+、現代各 spine）→ 50-100% hit
- 中世紀（500-1300）→ 15-30% hit（多無 Wikipedia 條目／僅 coins/seals）
- 18 世紀東歐 / 16 世紀 Constantinople / 醒目 Coptic / Armenian 1290-1800 → 0-10%（極稀疏）

**注意事項**：
- Wikipedia 對單一 IP 連續 fetch 易 429 rate-limit；agent 內部 2-3s sleep；批 146/148 撞 429 → 加 sleep 後重 retry 拿到分
- Apply 預設 `--skip-head` 因為 Wikimedia 拒 HEAD（也常 429）
- 偶爾 Haiku 寫出 malformed JSON（如 `"id": "15": "15"`）— 手動修一個 entry，整 batch 即可恢復

## 譜系圖測試（三棵樹共用）

`test/genealogy/` 有 vitest 元件測試，掛載 BiblicalSpineTree / IslamicSpineTree / EpiscopalSpineTree
配迷你 fixture 斷言 `cv` layout（脊柱解析、卡片無重疊、婚姻線、Episcopal 預設展開策略）。
跑法：`npm run test:run`。三棵樹各加了 test-only 的 `defineExpose({ cv, … })`。

已修（2026-06-02，見 `test/genealogy/FINDINGS.md`）：
- **E2**：focus-mode 用 `chainEndY`（含尾端 BISH_VG 空隙）多蓋 ~90px，誤藏掛在更晚主教的兄弟旁支
  → 改用 `prevBottomY`（EpiscopalSpineTree.vue:888-896）。
- **E3**：主脊旁支主教卡補 `spineColor`。
- 共用脊柱解析抽到 `utils/genealogy/spine.ts`（Biblical/Islamic 去重），缺 waypoint 時 dev `console.warn` 點名斷點。
- 「分裂旁支預設展開／設立旁支收起」是**設計**（watcher :405-418），非 bug。
