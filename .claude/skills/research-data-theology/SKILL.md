---
name: research-data-theology
description: 「當代神學研究」collection（/research-data/contemporary-theology）—— 二十世紀以來的神學研究書目與材料，十二個策展分區（神學方法論／二十世紀神學史／聖經神學／系統神學經典／實踐神學／自由神學／世俗神學／敘事神學／解放神學／性別神學／各地的神學／全球神學的嘗試）＋吉福德講座歷屆名單＋館藏盤點。含策展書目的欄位規格、吉福德那份名單怎麼抓（官網有 Cloudflare 要改走維基）、以及「已入館／缺」比對那兩個相反的壞法。Use when 要補書目、加一區、重抓吉福德名單、把缺書倒進 z-lib 獵表、或使用者提到「當代神學」「吉福德講座」「處境神學」「全球神學」「神學方法論」「聖經神學」「實踐神學」「自由神學」「世俗神學」「敘事神學」「解放神學」「性別神學」。⚠️ 與 [[research-data-christianity]] 的分工：那邊收教會史，這邊收神學本身。
---

# 當代神學研究（/research-data/contemporary-theology）

收二十世紀以來的神學研究。使用者 2026-09-11 開卡：
「把二十世紀以來重要神學研究的書目和文章都收進來，包含方法論、神學史的討論、
經典的基本系統神學與各地的神學，還有像是每年吉福德講座的人的著作清單、全球神學的嘗試。」

## 🚨 與別張卡片的邊界

| 材料 | 歸哪裡 |
|---|---|
| 系統神學、神學家著作、神學方法論 | **本卡片** |
| 教父、宗教改革、普世運動、洛桑運動（教會史與運動史） | 基督教研究（[[research-data-christianity]] 旁的 christian-studies） |
| 華語神學期刊的篇目與全文 | [[research-data-airiti]]（卷期頁碼只有華藝有） |
| 佛學的對應卡片 | [[research-data-buddhology]]（/research-data/buddhist-studies，同一套架構的佛學版） |

這條線是使用者自己定的（見 `feedback_theology_vs_christianity`）：
**教父原典／系統神學／神學家著作 → 神學；基督教史／教會史／神學家傳記 → 世界宗教/基督教。**

## 分區與各自的來源

使用者分三次把分區加到現在這個規模（2026-09-11 同一天）：先是方法論／神學史／系統神學／
各地的神學／全球神學五區，接著追加聖經神學、實踐神學、解放神學、敘事神學、自由神學，
最後補世俗神學與性別神學。**分區是使用者指定的，不要自行合併或重新分類。**

| 區 | slug | 來源 | 現況 |
|---|---|---|---|
| 神學方法論 | `method` | 策展書目 | 24 |
| 二十世紀神學史 | `history` | 策展書目 | 12 |
| 聖經神學 | `biblical` | 策展書目 | 16 |
| 系統神學經典 | `systematics` | 策展書目 | 20 |
| 實踐神學 | `practical` | 策展書目 | 12 |
| 自由神學 | `liberal` | 策展書目 | 11 |
| 世俗神學 | `secular` | 策展書目 | 11 |
| 敘事神學 | `narrative` | 策展書目 | 11 |
| 解放神學 | `liberation` | 策展書目 | 11 |
| 性別神學 | `gender` | 策展書目 | 14 |
| 各地的神學 | `contextual` | 策展書目，帶 `region` | 28 |
| 全球神學的嘗試 | `global` | 策展書目 | 16 |
| 吉福德講座 | `gifford` | 維基百科抓取 | 210 場／201 位講者（1888–2026） |
| 館藏當代神學 | `library` | 電子圖書館 | 212 本／38,534 段 |

### 🚨 三組會互相吃掉的分區

這幾條線在學界本來就重疊，本卡片的切法是**按「從誰的處境出發」而不是按「叫什麼名字」**：

* **解放神學 vs 性別神學 vs 各地的神學**——黑人神學與女性主義神學都自稱解放神學。
  本卡片把 `liberation` 限在拉丁美洲那一支及其方法論爭議，女性主義／婦女主義／
  拉美裔／酷兒進 `gender`，黑人神學與非洲亞洲各地進 `contextual`。
  ⚠️ 加新書目時要先想「它是從哪個處境出發的」，不要看書名有沒有 liberation。
* **自由神學 vs 世俗神學**——相鄰但不同。`liberal` 是士萊馬赫—立敕爾—哈納克那條
  學院神學線，`secular` 是潘霍華〈獄中書簡〉長出來的那一支（戈加騰、羅賓遜、考克斯、
  死神神學、泰勒）。田立克兩邊都沾，本卡片放在 `method` 與 `systematics`。
* **敘事神學 vs 方法論**——傅萊《聖經敘事的隱沒》兩邊都算。本卡片放 `method`，
  在 `narrative` 的說明裡指回去，不重複收錄（jsonl 有 (author_zh, title_zh) 去重）。

## 書目的欄位

`data/research-data/contemporary-theology/bibliography.jsonl`，一行一筆：

```json
{"area":"contextual","region":"亞洲‧台灣","author":"Choan-Seng Song 宋泉盛","author_zh":"宋泉盛",
 "year":1979,"title":"Third-Eye Theology","title_zh":"第三眼神學","lang":"en",
 "note":"以亞洲故事與民間敘事作神學材料","zh":"（有中譯本時才填）"}
```

* `area` ∈ method / history / biblical / systematics / practical / liberal / secular / narrative / liberation / gender / contextual / global
* `region` 只有 contextual 用，是**分析軸不是地理**——「黑人神學」「女性主義神學」
  「障礙神學」與「亞洲‧台灣」並列在同一欄，因為這一區真正的分類軸是「從誰的處境出發」。
* `zh` 只在**確知有中譯本**時才填；不確定就留空，頁面會顯示「缺」。寧可漏報。
* `in_library` 是跑腳本時算出來的，**不要寫進 jsonl**。

## 🚨 「已入館／缺」比對有兩個相反的壞法

`contemporary_theology_index.py` 的 `in_library()`。兩種錯都不會報錯：

1. **只拿原文題名比** → 得出「114 本只有 2 本在館」。因為館內題名九成是中文，
   `Der gekreuzigte Gott` 當然對不上《被釘十字架的上帝》。後果是把已經有的書
   全倒進獵表重抓。
2. **只拿題名比** → 潘能伯格、田立克、詹森的《系統神學》全被判成在館，
   因為館裡有湯姆華森與賀治的《系統神學》。後果是以為有而其實沒有。

現行作法：題名（原文與中譯都比）命中之後，**還要作者對得上**才算；作者欄空白的
只有在題名夠獨特（八字以上）時才採信。取寧可漏報的一側。

⚠️ 更根本的問題在館藏資料：**5,143 筆裡有 646 筆（13%）的 `author` 欄放的是書名
不是作者**（多來自 TRC 那批，中英雙題名塞進 author），另有 578 筆（11%）空白。
任何靠作者佐證的比對都會低估。要治本得先清 `ebooks.author`。

## 🚨 吉福德講座：官網抓不到，走維基

`giffordlectures.org` 有 Cloudflare，curl 一律 **403**。改抓維基百科英文版
〈Gifford Lectures〉的 wikitext：四所大學各一張 wikitable，欄位是年份／講者／講題／ISBN。

`scripts/gifford_lectures_fetch.py` 解析時踩過兩個坑，兩個都長得像正常資料：

* **欄位屬性沒剝**：`rowspan="2"|2022` 會整串當成年份。而且引號寫法不統一，
  `rowspan=2|` 不加引號的也有——只吃帶引號的正則會漏掉 11 列。
* **同格多位講者黏成一串**：`[[A]]<br>[[B]]` 去標籤之後變成
  「Manthia DiawaraTerri Geis」這種不存在的人名。要先把 `<br>` 與換行換成分隔號。

抽查一定要抽**近年**那幾列與**多講者**那幾列，只看開頭幾列會全過。

## 建置

```bash
python scripts/gifford_lectures_fetch.py              # 重抓吉福德名單
python scripts/gifford_lectures_fetch.py --list       # 只印出來看
python scripts/contemporary_theology_index.py         # 建索引
python scripts/contemporary_theology_index.py --wanted  # 另外吐缺書獵表
```

輸出 `public/content/research-data/contemporary-theology/{index.json,gifford.json}`（進版控），
缺書獵表寫到 `data/zlib-wanted/contemporary-theology.jsonl`，交
[[ebook-zlib-harvest]] 的每日排程去找。

頁面：`pages/research-data/contemporary-theology/index.vue`（各區）＋ `gifford.vue`（可搜尋的表格）。

## 期刊論文那一層（兩個來源）

**華語**走既有的華藝篇目（[[research-data-airiti]]，早就抓好了，不必重抓）。
`contemporary_theology_articles.py` 拿十二區各一組關鍵詞去掃十二份神學期刊的篇名，
11,111 篇裡篩出 1,073 筆候選，97% 華藝有全文。⚠️ 這是**粗篩不是分類**：一篇可落多區
（刻意的），也必然有假命中（篇名有「敘事」不等於敘事神學），頁面標明未經人工複核。
命中分布本身有意思——實踐神學 231、神學史 159 最多，自由神學 5、世俗神學 6、
解放神學 7 最少，華語神學期刊幾乎不談自由與世俗神學。

**外文**走 DOAJ（`scripts/doaj_harvest.py`）。313 種宗教／神學期刊、104,491 篇。
語言重心不在英語世界：英 266、印尼 55、西 53、法 51、德 47、義 41、阿 38、葡 32、波 28；
國別以印尼 76、波蘭 28、土耳其 22、巴西 17、南非 13 居前。

### 🚨 DOAJ API 兩個坑

1. **不吃萬用字元**：`bibjson.subject.code:BR*` 一律 400（disallowed Lucene features）。
   要用加引號的完整分類詞。
2. **一個查詢最多 1000 筆**，第 11 頁（pageSize=100）直接 400。照分頁抓到出錯就停，
   會寫出一個**剛好 1000 筆**的檔案——數字整齊、不報錯、看起來完全正常，
   而 Acta Theologica 其實有 1355 篇。解法是用 `bibjson.year:[lo TO hi]` 遞迴二分
   把查詢切小，寫檔後再與整刊總數對帳。

## 校內訂閱庫：先探測再動手

玄奘訂的庫清單在 `data/research-data/hcu-eresources.json`，分級計畫在
`hcu-harvest-plan.json`（tier A 不需校網／tier B 需校內 IP／tier C 不相關）。

🚨 **清單上有 ≠ 還在訂 ≠ 這台機器驗得過**，而這件事在校外怎麼查都是 unknown。
`scripts/campus_probe.py` 一連上校網就把 `access` 欄從 unknown 換成實測結果；
排程 `KGL_Campus_Probe`（每 30 分一次、每日 13 小時），離校時是一次 HTTP 請求的
安靜 no-op，在校內每天只做一次完整探測。

🚨 **只探測不下載。** 訂閱庫的大量下載會被當成異常流量，處置是停**整個機構**的權限。
tier B 一律只做「抓篇目索引」與「人工速率的選擇性全文下載」，不做整庫鏡像。

排程的四條硬規矩（全都踩過）：.ps1 必須純 ASCII（PowerShell 5.1 遇中文註解會解析崩
且行號對不上）、`-AllowStartIfOnBatteries`（人在學校時筆電正在用電池，預設的
「使用電池時不啟動」會讓這個排程從設計上就沒辦法完成工作）、觸發器要 Daily 不能
Once＋重複（重複期用盡後再也不觸發，而 State 仍是 Ready）、python 要有自己的隱藏
主控台（共用 console 會被別人的 Ctrl+C 帶走，而排程器回報成功）。

⚠️ **專書的免費來源是另一份清單**：`.claude/skills/ebook-collected-works/free_text_sources.md`
（實測 18 站，其中 12 站不必帳號、curl 直接抓、可排程）。那份管專書，本節管期刊電子庫，
動手前兩份都看一眼，別重複造。

### 清單上沒有的三個缺口

* **ATLA Religion Database** —— 宗教研究的標準索引庫（1,700 餘種期刊回溯到十九世紀），
  玄奘**沒訂**。這是本研究最大的一個缺口，要走圖書館資料庫推薦或 NDDS 館際調件。
* **Index Theologicus（IxTheo，圖賓根）** —— 德語神學索引最完整，而且**本身免費開放**，
  優先度高於多數 tier B。
* **JSTOR** —— 清單裡沒看到，要確認有無其他聯盟管道。

## 還沒做的事

1. **書目還可以更厚。** 現行 186 筆是第一輪；後加的七區（聖經／實踐／自由／世俗／
   敘事／解放／性別）每區只有 11–16 筆，比前五區薄。東正教與天主教那兩側、
   以及非英語的全球南方著作都還能補。
2. **中譯資訊多半空著。** `zh` 欄只填了確知的幾筆，其餘要逐筆查證。
3. **吉福德那份缺「講稿成書與否」**。維基的 ISBN 欄多半空白；補上之後這一區
   才真的是「著作清單」。
4. **華藝那 1,073 筆候選要人工複核**，現在只是候選。
5. **tier B 的抓取程式一個都還沒寫**——要等 `KGL_Campus_Probe` 帶回實測結果，
   才知道該先寫哪一個。IxTheo 不必等（免費開放）。
