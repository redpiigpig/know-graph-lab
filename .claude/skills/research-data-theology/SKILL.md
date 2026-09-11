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

## 還沒做的事

1. **文章那一層還沒有。** 使用者要的是「書目和文章」，目前只有書目。華語期刊走
   [[research-data-airiti]]（神學與教會／台灣神學論刊／道風／建道／神學論集），
   英文期刊（*Modern Theology*、*IJST*、*Scottish Journal of Theology*）多半綁機構訂閱，
   開放取用的只有少數，要另外評估。
2. **書目還可以更厚。** 現行 186 筆是第一輪，各區都還能補；尤其
   東正教與天主教那兩側、以及非英語的全球南方著作。後加的七區（聖經／實踐／自由／
   世俗／敘事／解放／性別）每區只有 11–16 筆，比前五區薄。
3. **中譯資訊多半空著。** `zh` 欄只填了確知的幾筆，其餘要逐筆查證。
4. **吉福德那份缺「講稿成書與否」**。維基的 ISBN 欄多半空白，
   要補得靠另外比對；成書資訊補上之後，這一區才真的是「著作清單」。
