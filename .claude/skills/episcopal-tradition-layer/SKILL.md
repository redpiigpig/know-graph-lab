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

## 編輯規則：一律按傳統說法

**像羅馬教宗列表一樣**——只要該教座有「傳統公認」的主教名單就**全部列出**，不需要等到「學界可考史料」才加。使徒時代的傳說性主教（例如 凱撒利亞·巴勒斯坦 #1 撒該、羅馬 #1 彼得）一律按傳統紀年列入，notes 欄位說明史料來源即可，**不要用 `status='傳說'` 把他們區別開來**。

判斷依據：
- 有傳統教會歷史（Eusebius《Historia Ecclesiastica》、Movses Khorenatsi、Ormanian、Le Quien 等）公認的繼任名單 → 列
- 完全無記載、只是「應該存在過」的空檔 → 留空 notes 註明

## 7 大 spine 結構

定義在 `SPINE_DEFS`（[episcopal-graph.get.ts](../../server/api/genealogy/episcopal-graph.get.ts)）。每 spine 一個 `primaryApostleId` + 可選 `secondaryApostleId`。

| spine key | see_zh | 主使徒 | 輔使徒 | spine 色 |
|---|---|---|---|---|
| `rome` | 羅馬 | 彼得 | 保羅 | `#dc2626` 紅 |
| `constantinople` | 君士坦丁堡 | 安得烈 | — | `#2563eb` 藍 |
| `alexandria` | 亞歷山卓 | 彼得 | 巴拿巴 | `#d97706` 橙 |
| `antioch` | 安提阿 | 彼得 | — | `#0891b2` 青 |
| `jerusalem` | 耶路撒冷 | 義人雅各 | — | `#16a34a` 綠 |
| `armenia` | 埃奇米亞津 | 達太 | 巴多羅買 | `#9333ea` 紫 |
| `assyria` | 塞琉西亞—泰西封 | 多馬 | — | `#475569` 灰 |

## primaryChurches vs rivalChurches

兩種多教會處理方式：

**`primaryChurches`**：時序接續、無重疊的多個 church 名稱合併在同一條 spine 線上
- 例：羅馬 `['未分裂教會', '天主教']`（1054 大分裂後 天主教 接續未分裂教會的羅馬線）
- 例：君士坦丁堡 `['未分裂教會', '東正教']`

**`rivalChurches`**：並行存在的對立教會，自動產生 `is_split=true` 的合成分支（紅色鋸齒線）
- 例：assyria 的 `rivalChurches: ['東方教會（亞述）']`（1968 後與 古代東方教會 並存）
- attach 點：rival 第一位主教的 `start_year` 對應 spine 同期主教
- **如果是時序接續就用 primary，如果是並行對立就用 rival——不要混用，會交錯排序看起來像 bug**

## 負 succession_number 慣例

某些教座有「使徒寶座傳統 / 正史前」主教列表，需要排在官方 #1 之前：

| 教座 | 例 | 處理 |
|---|---|---|
| 埃奇米亞津 | 達太傳統 8 位（撒杜克 → 美侯讓，68-270 AD） | succession_number `-8..-1`，格利高爾續 `#1` |

**規則：API 把負 succession_number 在輸出時轉成 `null`**（前端不顯示編號數字），但**排序仍用原值**——負數自然排在正數之前，無需修改 sort 邏輯。

如要在其他教座加類似列表：
1. DB 主教用 `succession_number = -N .. -1` 寫入
2. 不需要改 SPINE_DEFS
3. 不需要前端改 code

## 旁支（branch see）結構

凡 `episcopal_sees.parent_see_id` 指向 spine 的主 see 或另一個旁支 see → BFS 找到後成為旁支，可在 spine 圖點 ▸ 展開。

- 若旁支 see_zh **與母教座相同** → 視為 `is_split=true`（紅色鋸齒線、教座分裂）
- 若旁支 see_zh **與母教座不同** → `is_split=false`（spine 色實線、設立教座）

預期將來會擴張到「一個宗主教座下面延伸很多教座傳承」（user 原話），spine column 之間預留了 horizontal space。

## 已建立的安提阿旁支教座

- 馬龍尼特禮天主教、希臘天主教麥勒基特禮、天主教（拉丁禮）、敘利亞天主教、敘利亞正教（既有）
- **凱撒利亞·巴勒斯坦**：使徒時代基督教社群（行 10 哥尼流）；傳統 #1 撒該（由彼得按立）；該撒利亞·優西比烏（教會史家）為 313-339 在任主教；建檔 10 位主教（37-395 AD）
- **凱撒利亞·卡帕多西亞**：使徒時代有基督徒（彼前 1:1）但無使徒親建教座；萊昂提烏斯（#4）約 302 年祝聖亞美尼亞啟蒙者格利高爾，使亞美尼亞統緒透過此地接續；卡帕多西亞教父（巴西略大帝為 #9）；建檔 11 位主教（232-432 AD）

## 跨 spine 祝聖關係：church_teachings

教座之間的「祝聖／教導」關係寫進 `church_teachings`。前端 SVG 用橘色實線 + 細邊（`#ea580c`）畫師徒線。若 institutional spine/branch 鏈已連通則略過（教座傳承 takes precedence over 教導）。

已建檔：
- 萊昂提烏斯（凱撒利亞·卡帕多西亞 #4）→ 聖額我略·啟蒙者（埃奇米亞津 #1），302 年祝聖

## 截圖工具

[scripts/episcopal-shot.mjs](../../scripts/episcopal-shot.mjs)：headless 截圖
- 預設 `--zoom 0.55` 看全使徒列
- `--expand <branchId>` 展開某旁支
- `--panX <dx>` 微調水平 pan
- 因 Rome 有 261 任 pope，垂直高度 ~30000px，`--fit` 會把 zoom 縮到 4%，不實用——建議用 `--zoom 0.5` + `--panX` 看特定區域

## 已修正的歷史錯誤紀錄

- **#1 格利高爾的 appointed_by**：原寫「國王提里達底三世」（錯，國王是受洗者，不是任命者）→ 修為「凱撒利亞·萊昂提烏斯」
- **assyria spine 兩派交錯**：原 `primaryChurches: ['古代東方教會', '東方教會（亞述）']` 把 1968 後並行的兩派合進同一條線按 succession_number 排序，#1帕帕（280）→ #1馬爾·丁哈（1976）→ #2示孟（329）→ #2馬爾·吉瓦吉斯（2015）交錯亂序 → 改用 `rivalChurches` 分開
