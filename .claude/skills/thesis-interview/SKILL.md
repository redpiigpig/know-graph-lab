---
name: thesis-interview
description: 把碩士論文口述訪談的「音檔」整理成符合 /thesis?tab=interviews 上架格式的繁體中文逐字稿。Gemini Audio 轉錄 → Claude 在對話中整理 Q&A、分節、補前言三段 → 寫入 public/content/interviews/ → 更新 stores/thesisInterviews.ts。Use when 使用者指明某位受訪者要把音檔轉成正式紀錄並上架，或要重做某位現有訪談紀錄的清理工作。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 碩士論文口述訪談 — 音檔轉文字檔 + 整理 Pipeline

> 把 `G:\我的雲端硬碟\公事\國北教\碩士論文\口述訪談\YYYY.MM.DD [受訪者]訪談\` 下面的 m4a/mp3 整理成跟 [04.10 邱敏捷教授口述訪談紀錄.txt](../../../public/content/interviews/04.10%20%E9%82%B1%E6%95%8F%E6%8D%B7%E6%95%99%E6%8E%88%E5%8F%A3%E8%BF%B0%E8%A8%AA%E8%AB%87%E7%B4%80%E9%8C%84.txt) 一樣的逐字稿，寫入 `public/content/interviews/` 並更新 [stores/thesisInterviews.ts](../../../stores/thesisInterviews.ts)。

逐字稿要整理過 — Gemini Audio 的原始輸出已經有標點＋分段，但不會自動標出說話者、不會分節、不會補前言。整理由 Claude 在對話中完成。

## Reference quality bar

新整理出來的訪談要對齊以下三個範例之一（依受訪者類型挑）：

| 範本 | 適用 | 特色 |
|---|---|---|
| [`01.16 釋印悅法師口述訪談紀錄.txt`](../../../public/content/interviews/01.16%20釋印悅法師口述訪談紀錄.txt) | 法師 (面訪) | 前言三節 + 四個主題節 + 附件一訪談大綱 |
| [`04.10 邱敏捷教授口述訪談紀錄.txt`](../../../public/content/interviews/04.10%20邱敏捷教授口述訪談紀錄.txt) | 學者 (面訪) | 前言四節 (含「概念簡史」)、Q&A 翔實 |
| [`05.11 釋見岸法師口述訪談紀錄.txt`](../../../public/content/interviews/05.11%20釋見岸法師口述訪談紀錄.txt) | 法師 (電話訪談) | 前言四節 (含「相關文獻摘選」) |

> 渲染這些 txt 的程式是 [pages/thesis/interview/\[name\].vue](../../../pages/thesis/interview/[name].vue) 中的 `formatInterview()`，它認得 `筆者：` / `XX法師：` / `（一）` / `一、` 這幾個前綴。格式對了它就會渲染成清楚的 Q&A 卡片。

## 標準格式

```
[訪談標題]：[受訪者]訪談記
受訪者：[受訪者全名+稱謂]
訪問時間：YYYY年M月D日HH:MM-HH:MM
訪問地點：[地點]

一、前言

（一）訪問動機
[兩段：先說論文題目背景，再說為什麼訪問這個人。]

（二）受訪者簡介
[一段：生年、籍貫、學歷、職涯、與本研究主題的關係。對法師：依止師父、剃度年、得戒、現任職務。對學者：學經歷、代表著作。]

（三）訪問情形
[一段：訪問如何安排、面訪/電話、錄音與筆記、整理流程。]

(可選 四、相關文獻摘選 — 若受訪者有重要著作可直接引用)

二、[第一個主題]

筆者：[問題]

[受訪者簡稱]：[回答，依需要分段]

筆者：[後續問題]

[受訪者簡稱]：[回答]

三、[第二個主題]
...

四、[第三個主題]（可選）
...

附件一、[受訪者]訪談大綱（可選 — 把訪綱 docx 的內容附在最後）
```

### 開頭三行的「訪問時間 / 地點」格式

- 時間：`2024年5月11日10:00-12:00` 或 `2024年5月11日`（沒記時段時）
- 地點：精確到房間/堂 — 「佛教弘誓學院嵐園」、「國立台南大學人文學院院長辦公室」、「電話訪談」。

## 對話標籤縮寫

「受訪者：」這一行用完整稱呼（釋XX法師 / XX教授）；Q&A 區塊用簡稱：

| 受訪者類型 | Q&A 簡稱 | 例 |
|---|---|---|
| 出家眾 | `[法名]法師：` (不含「釋」) | 印悅法師、心皓法師、見岸法師、長慈法師 |
| 學者 | `[姓]教授：` 或 `[全名]教授：` | 邱教授／邱敏捷教授、楊教授／楊惠南教授 |
| 牧師 | `[姓]牧師：` | 盧牧師 |
| 主教 | `[姓]主教：` | 洪主教 |
| 居士 / 老師 / 女士 / 先生 | 同稱謂 | 王彩虹居士、陳悅萱老師、葉菊蘭女士、何宗勳先生 |

採訪者一律是 `筆者：`（不要寫「我」「張辰瑋」）。

## Pipeline

### Step 1 — 鎖定資料夾、挑音檔

Drive 上每場訪談一個資料夾：
```
G:\我的雲端硬碟\公事\國北教\碩士論文\口述訪談\YYYY.MM.DD [受訪者]訪談\
  ├ [受訪者]口述訪綱.docx       ← context；要餵給 Gemini
  ├ 新錄音 NN.m4a / [日期].m4a   ← audio source
  ├ IMG_NNNN.JPG                  ← 訪談合照（不用）
  └ [m4a 檔名].m4a.txt            ← Whisper 草稿（可參考，但不要直接用）
```

挑音檔優先序：
1. `[XX]訪談(合併檔).mp3` ← 若存在，優先用
2. `新錄音 NN.m4a` / `[日期] [人名]訪談.m4a`
3. 多段 m4a — 一個一個轉，最後合併

### Step 2 — Gemini Audio 轉錄

**先用 ffmpeg 看音檔長度**（`ffprobe -v error -show_entries format=duration <audio>`）。
> **超過 30 分鐘的音檔，先切成 ≤22 分鐘的片段。** Gemini 2.5 Flash 處理長音檔容易在後半段卡進「重複迴圈」（同一段問答重複幾十次直到 output token 用完），切短後分別轉錄可避免。

```bash
# 切分（以 86 min 切成 4 段為例）
mkdir -p _tmp_audio/interview/[人]_split
for i in 0 1 2 3; do
  start=$((i * 1300))
  ffmpeg -y -i "G:\...\原音檔.m4a" -ss $start -t 1320 -c copy \
    "_tmp_audio/interview/[人]_split/part$((i+1)).m4a"
done

# 各段平行轉錄（每個跑 run_in_background:true，會用不同 Gemini key 自動 fallback）
python scripts/transcribe_interview_gemini.py \
  "_tmp_audio/interview/[人]_split/part1.m4a" \
  --outline "G:\...\[人]口述訪綱.docx" \
  --interviewee "釋XX法師" \
  --out "_tmp_audio/interview/[date]_part1.txt"
# 同樣方式跑 part2/3/4
```

短音檔（≤25 min）可直接整檔轉錄：
```bash
python scripts/transcribe_interview_gemini.py \
  "G:\...\原音檔.m4a" \
  --outline "G:\...\訪綱.docx" \
  --interviewee "釋XX法師" \
  --out _tmp_audio/interview/[date]_raw.txt
```

- 訪綱當 context 餵進去，Gemini 對人名／寺院名／僧團名會準很多。
- 輸出已經是繁體＋有標點＋分段，**有 `筆者：` / `XX法師：` 前綴**（prompt 已要求），但不見得每段都對 — 整理時還要校驗。
- Free-tier 每 key 一天 20 次 request，平行多段時自動 fallback 到下一把 key。
- 一段 20-25 min 大概 2-3 min 跑完。

### Step 3 — Claude 整理（這是真正的工作）

讀 `_tmp_audio/interview/[date]_raw.txt`（或多段 `_partN.txt`），做以下整理：

1. **辨識說話者**：兩人對話為主，少數三方（如黃美瑜＋游雅婷同場）。Gemini 偶爾會搞錯說話者標籤，要對照訪綱與上下文修正。短暫的「電話中斷／與第三人對話」可整段省略。
2. **每節 2-5 個獨立問題，每個問題的回答 1-3 段**（不是「一節一個 mega-question」）：對照既有範本（[邱敏捷 04.10](../../../public/content/interviews/04.10%20邱敏捷教授口述訪談紀錄.txt)、[釋印悅 01.16](../../../public/content/interviews/01.16%20釋印悅法師口述訪談紀錄.txt)、[釋見岸 05.11](../../../public/content/interviews/05.11%20釋見岸法師口述訪談紀錄.txt)、[黃運喜 04.21](../../../public/content/interviews/04.21%20黃運喜教授口述訪談紀錄.txt)、[侯坤宏 12.22](../../../public/content/interviews/12.22%20侯坤宏教授口述訪談紀錄.txt)、[林建德 08.27](../../../public/content/interviews/08.27%20林建德教授口述訪談紀錄.txt)），每節有 2-5 個獨立的 `筆者：` 問句，每個問句後面的回答用 1-3 段多段完整敘述，**段落間不重貼說話者標籤**。問題本身可以稍微複合（例如同時問「為什麼 X」+「後來怎麼 Y」），但不要把整節壓成一個巨型問題。同時也**不要照搬 Gemini 的碎片化 Q-A**（每個「嗯」「是」都拆成獨立 turn），把短促的確認直接刪除合併。
   - 篇幅參考：一個 60-90 分鐘的訪談，整理過後通常 25-50K 字。如果你的輸出 < 15K 字而音檔超過 60 分鐘，多半是被過度精簡，應該回去拿原始稿補回更多的細節、典故、人名、確切年份。
3. **合併「嗯」「是」短回應**：Gemini 把每個確認都拆成獨立 turn，整理時直接刪掉，不要列出來。
4. **按訪綱分節**：訪綱通常有 2-4 個主題，把 Q&A 對應到 `二、`、`三、`、`四、`（`一、` 留給前言）。實際對話順序可能跟訪綱不一致，按內容歸位、不要強行重排對話順序。
5. **寫前言三節**（必須）：
   - **（一）訪問動機**：用範本起頭 — 「筆者碩士論文研究的主題是『印順導師人間佛教思想的傳承與實踐：以昭慧法師、性廣法師為核心』，...」加一段說明為什麼訪問此人（與昭慧/性廣的關係、研究價值）。
   - **（二）受訪者簡介**：一段 bio（從訪綱、著作、訪談本身整合）。法師：生年、籍貫、學歷、依止、剃度、受戒、現任職務。學者：學歷、著作、研究領域。**簡介裡寫過的基本資料（出生年、籍貫、學歷）在 Q&A 區塊不要再讓筆者重新問一遍**——直接從訪談的實質內容開始問。
   - **（三）訪問情形**：一段說明訪問如何安排、面訪/電話、錄音方式、整理流程。
6. **訪談標題**：7-10 字濃縮這場訪談的主軸，後面接「：[受訪者]訪談記」。例：
   - 「弘誓僧團的住持與財務：釋心皓法師訪談記」
   - 「論印順學派的傳承：邱敏捷教授訪談記」
   - 「在愛與公義中的信仰對話：盧俊義牧師訪談記」

### Step 4 — 佛教領域常見聽錯修正

| Gemini/Whisper 容易聽錯 | 正確 |
|---|---|
| 紅誓 / 宏誓 / 洪師 / 弘師 | 弘誓 |
| 印盾 / 印孫 | 印順 |
| 招會 / 朝會 | 昭慧 |
| 性光 / 醒光 | 性廣 |
| 印悅 / 印越 / 應悅 | 印悅 |
| 圓貌 / 圓茂 | 圓貌 |
| 嵐園 / 蘭園 / 藍園 | 嵐園（弘誓學院招待所） |
| 香光寺 / 香港寺 | 香光寺（莊嚴寺體系） |
| 普嚴 / 福源 | 福嚴（佛學院） |
| 自即 / 慈基 | 慈濟 |
| 玄裝 / 玄藏 | 玄奘 |
| 慈恩經舍 / 慈安精舍 | 慈恩精舍（玄奘大學內，性廣法師主持） |
| 高峰禪靈 / 高峰禪林 | 高峰禪林（早期用「禪靈」，現在統稱「禪林」） |
| 旃檀精舍 / 沾蓮精舍 | 栴檀精舍（高峰禪林前身） |
| 法印講堂 / 法銀講堂 | 法印講堂（見岸法師高雄道場） |
| 帕奧 / 巴奧 | 帕奧禪師 |
| Dipankara / 燈燃 / 燃燈 | Dipankara Sayalay（燃燈禪師） |
| 反賭埸 / 反賭場 | 反賭博（公投） |
| 觀音事件 / 七號公園 | 大安森林公園觀音像事件 |
| 千里苦行 | 反核四千里苦行 |
| INAM / INNB | INEB（International Network of Engaged Buddhists） |
| 三系 / 教制教史教義 | 印順導師「教制／教史／教義」三系研究 |
| 性空 / 緣起 / 唯識 / 中觀 | 保持，學派名稱不要簡化 |
| Peter Singer | Peter Singer（彼得‧辛格） |

### Step 5 — 寫檔 + 更新 store

1. **寫 txt**：
   ```
   public/content/interviews/MM.DD [受訪者]口述訪談紀錄.txt
   ```
   - `MM.DD` 用實際訪問日（與 txt 內「訪問時間」一致），不見得跟 Drive 資料夾日期一樣（兩者偶有出入，以實際為準）
   - 副檔名一律 `.txt`，UTF-8 + LF 結尾
   - 標題行（第一行）開頭**不要**有 BOM、不要有 Word docx 殘留的 `1.`（黃運喜、邱敏捷的舊檔有，是 docx 自動編號殘留）

2. **更新 [stores/thesisInterviews.ts](../../../stores/thesisInterviews.ts)**：
   - 從 `driveMissing` 陣列移除這個人
   - 加進 `published` 陣列（依日期排序）：
     ```ts
     { id: 'xxx', name: '釋XX法師', role: '...', date: 'YYYY.MM.DD',
       category: '法師', filename: 'MM.DD 釋XX法師口述訪談紀錄' },
     ```
   - `filename` **不**含 `.txt`，編碼也不要事先 URL-encode（router 會處理）
   - `category` 五選一：`法師 / 學者 / 宗教對話 / 社運界 / 其他`

3. **驗證**：dev server 跑著時，curl 一下 `http://localhost:3000/thesis/interview/<urlencoded-filename>`，或瀏覽器點進 `/thesis?tab=interviews` 看新項目出現。

### Step 6 — Commit + push

依 [feedback_auto_push](../../projects/c--Users-user-Desktop-know-graph-lab/memory/feedback_auto_push.md) 自動 commit + push，message 用 `feat(thesis): 新增 [人名] 訪談紀錄` 之類的格式。

## 訪談已上架但 Drive 沒 docx 的情況

[stores/thesisInterviews.ts](../../../stores/thesisInterviews.ts) 的 `publishedButDriveMissing` computed 列出這類人 — 網站有 txt 但 Drive 沒整理過的 docx。例如 `釋見岸法師` 現有的 txt 是手動整理的，不見得有對應的 Drive docx。

要重做這類訪談時：
- **先讀現有 txt 當參照**：確認既有版本的標題、章節、Q&A 切分。如果既有版本品質夠，**不要重做**，只考慮微調。
- 真要重做才跑 Step 2-5；不要無端覆蓋使用者手動整理過的版本。

## 訪綱對應「資料夾日期 vs 真實訪問日」對照（已知對不上的）

| Drive 資料夾日期 | 真實訪問日 (內文/docx) | 已上架 filename |
|---|---|---|
| 2024.01.09 何宗勳 | 2024.01.16 | `01.16 何宗勳先生口述訪談紀錄` |
| 2024.02.03 艾琳達 | 2024.02.02 | `02.02 艾琳達教授口述訪談紀錄` |
| 2024.03.25 張莉筠 | 2024.03.26 | `03.26 張莉筠居士口述訪談紀錄` |

碰到日期對不上的，以 docx／訪綱內所寫的訪問日為準。

## 不適用此 Skill 的情況

- 別人主持的訪談（不是張辰瑋作的） — 不上架。
- 訪綱還沒寫的訪談 — 那只是訪前準備。
- `電話訪問` 資料夾下的人（江燦騰、藍吉富）— 那是訪綱草稿，沒有錄音。
- 已上架且品質可接受的訪談 — 不要重做。

## 待處理清單在哪

[`stores/thesisInterviews.ts`](../../../stores/thesisInterviews.ts) 的 `driveMissing` 陣列。狀態分三類（透過 `driveMissingByStatus` getter）：

| 類別 | 條件 | 處理方式 |
|---|---|---|
| `draft` | 有 `m4a.txt` 逐字稿草稿 | 跳過 Step 2，直接拿草稿開始 Step 3 整理（仍要校驗品質、補前言三節） |
| `audioOnly` | 只有 m4a 沒草稿 | 從 Step 2 開始 |
| `outlineOnly` | 連錄音都沒有 | 不在這個 skill 範圍內，請聯絡受訪者重訪或補錄 |
