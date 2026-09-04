---
name: original-reader-flashcards
description: 由原文讀本詞表產出「可裁切的實體印刷單字卡」— A4 橫式每頁 8 張、74.25×94 mm、正面原文背面繁中、雙面長邊翻、不印裁切線，配圖走 OpenMoji。九副：課內詞卡五副（聖經希伯來文 1000、通用希臘文上下冊各 1000、教會拉丁文上下冊各 1000）＋附錄卡三副（專名九類＋數字／親屬／曆法／職分各表）＋國小英語 1000（唯一一副**不留白**的）。Use when 要新增／重出某一副卡、要把某副的配圖率往上補、要換掉某張圖、要加新的一副（新語言）、要改版面（卡片尺寸／字級／欄序）、頁數莫名變兩倍要 debug、或使用者說「單字卡」「字卡」「配圖」。方法在本檔，逐副現況在讀本 skill 的 references/flashcard-decks.md。
---

# 原文讀本印刷單字卡

規格對齊使用者家教在用的《家教單字卡.pdf》，同一把裁刀、同一組印表機設定通吃五副。

> 詞表來源：[data/originalReaders/vocabulary/](../../../data/originalReaders/vocabulary/)（`hebrew-1000.json`／`greek-1000.json`／`greek-2000.json`／`latin-2000.json`）
> 產卡：[scripts/build_flashcards.py](../../../scripts/build_flashcards.py)
> 配圖：[scripts/match_flashcard_images.py](../../../scripts/match_flashcard_images.py)（希伯來）／[match_greek_card_images.py](../../../scripts/match_greek_card_images.py)／[match_latin_card_images.py](../../../scripts/match_latin_card_images.py)
> 詞性推定（希臘）：[scripts/flashcard_pos.py](../../../scripts/flashcard_pos.py)
> 性數狀態（希伯來）：[scripts/hebrew_card_grammar.py](../../../scripts/hebrew_card_grammar.py)
> 看圖：[scripts/flashcard_contact_sheet.py](../../../scripts/flashcard_contact_sheet.py)
> 逐副現況與歷史：[skills/build-original-language-reader/references/flashcard-decks.md](../../../skills/build-original-language-reader/references/flashcard-decks.md)
> 國小英語：詞表 [scripts/build_english_vocabulary.py](../../../scripts/build_english_vocabulary.py)、配圖 [match_english_card_images.py](../../../scripts/match_english_card_images.py)、自繪圖 [english_picture_tiles.py](../../../scripts/english_picture_tiles.py)、審圖 [english_card_sheet.py](../../../scripts/english_card_sheet.py)
> 2026-08-26：希伯來與希臘三副已 **100% 有圖、0 張缺詞性**；拉丁兩副配圖 46%／35%，是下一個目標。
> 2026-09-04：國小英語 1000 上線，**100% 有圖**（自繪 56／國旗 19／人工 324／站上 366／繁中轉移 53／Iconify 181）。
> 🚨 拉丁兩副由**別的 session** 負責；讀它的 map 沒問題（詞義轉移就是要讀），別重跑它的 matcher、別改它的卡檔。
> 🚨 **希臘補滿之後，拉丁再跑一次 matcher 會自己漲** —— 它上次配圖時希臘只有 50%，而詞義轉移讀的就是希臘的 map。

## 資料流

```
詞表 JSON ──► matcher（配圖，寫 output/source-cache/flashcards/*-card-images.json）
           └─► build_flashcards.py --deck hbo|grc1|grc2|lat1|lat2 ──► DOCX ──LibreOffice──► PDF
```

配圖表是獨立產物，重跑 matcher 不會動到卡檔；換過圖一定要重跑 build 再重出 PDF。

## 成品去處（2026-08-27 起）

`output/` **不進版控**。跑完一副卡，DOCX／PDF 留在本機 `output/flashcards/`，
同時複製一份到 Drive `資料\知識圖工作室\語言\原文讀本\單字卡\`；
送印用的定稿另放 `…\原文讀本\印刷母版\`。

進版控的只有配圖對照與審閱紀錄——`output/source-cache/flashcards/*.json`
（`*-card-images.json`、`*-card-icons.json`、`icon-rejects.json`、`proper-name-registers.json`）。
新增別種策展 JSON 要追蹤時，去 `.gitignore` 白名單補一條，別把整個目錄放行。
規則全文見 [docs/repo-hygiene.md](../../../docs/repo-hygiene.md)。

## 版面（各副共用，別自己重算）

| | |
|---|---|
| 紙 | A4 橫式 297 × 210 mm |
| 格 | 4 欄 × 2 列，每頁 8 張 |
| 卡 | 74.25 × 94 mm |
| 卡框 | 圓角矩形，半徑 3.75 mm、線寬 2.12 mm、比裁切線內縮 3 mm，正反面都有 |
| 框色 | 按課次十色輪替：紅 ED0A3F／橙 F07C1E／黃 E8B10A／綠 3AA655／藍 1E6FD9／紫 7B3FA0／棕 8B5A2B／粉 F080B4／深灰 4A4A4A／深綠 1F6B4A，第 11 課回到紅 |
| 邊界 | 上下 5 mm，左右 0 |
| 裁切位置 | 橫向距頂 5 / 99 / 193 mm，縱向距左 74.25 / 148.5 / 222.75 mm |
| 雙面 | 長邊翻；**背面欄序鏡像 4-3-2-1** |
| 頁數 | `2 + 2 × ceil(張數 / 8)`，1000 張＝252 頁 |

🚨 **卡高 94 mm 是量出來的不是算出來的。** LibreOffice 保留的垂直空間比宣告的邊界多，兩排一接近可用高度就把第二排推到下一頁、印出一頁空白。10 mm 邊界失敗、5 mm 可行；97 mm 排高失敗、94 mm 可行。**頁數變兩倍就是踩到這個** —— 把排高調小，別跟它講道理。另外別在設了 `row.height` 之後又補一個 `w:trHeight`，兩條規則打架，症狀一模一樣。

🚨 **不印裁切線，但每張卡有框**（使用者指定，比照桌面那副《家教單字卡.pdf》）：框的規格是量參考卡量出來的 —— 緋紅 `#ED0A3F`、線寬 2.12 mm、正反面都有。**框一定要往內縮**（本專案 3 mm）：畫在裁切線上就等於印裁切線，裁歪一毫米就缺一邊、還帶進隔壁卡的框；內縮之後裁歪只會讓白邊不等寬。參考卡自己是靠卡與卡之間留 5.2 mm 空隙做到的，本專案沒有空隙，改用內縮。

🚨 **框是圓角矩形圖形（DrawingML `roundRect`），錨在「頁面」座標上。** 表格框線沒有圓角，所以框不能用邊框做；而圖形若錨在段落或格子，y 會跟著內容高度浮動（內容是垂直置中的），八張卡的框就各自高低不一。版面是固定格線，每張卡在頁面上的座標算得出來，直接寫死最穩。`layoutInCell="0"` 一定要有，否則位置又被格子夾回去；`wp:docPr` 的 id 在整份文件必須唯一，重複的話 Word 只認第一個。格子裡仍放一張無框線的單格表，管內距與垂直置中。

🚨 **早期用表格邊框做框時踩過的坑**（現在框改成圖形，但表格結構還在，所以仍然適用），不是給卡片格加邊框 —— 表格框線畫在格子邊上，那正好是裁切線。做這個框踩到三個坑：
1. **內外兩層表格都要鎖寬**（`w:tblLayout fixed` ＋ `w:tblW` ＋ `w:gridCol`）。只鎖內層，外層欄寬會被重算，八張卡縮成 61 mm 一張並整排右移出頁面。
2. **外層格子的 `w:tcMar` 要設 0**，內縮完全交給框自己的尺寸。用邊距擠出內縮會把列撐高，`hRule=exact` 對 LibreOffice 只是下限，第二排整排下移、框壓過 193 mm 那條裁切線。
3. **框線是往外畫的**：宣告的寬高是框內緣，成品外緣還要加兩條線寬；另外留 `FRAME_SLACK_MM = 2` 讓垂直置中重新生效，否則框會偏下。

🚨 **希伯來這類複合語系要設 `w:szCs`。** python-docx 的 `run.font.size` 只寫 `w:sz`，那管的是拉丁字；RTL run 的字級，排版程式看的是 `w:szCs`。沒設就用樣式預設的 11 pt 印出來 —— **宣告 54 pt 也一樣，而且不會有任何錯誤訊息**，DOCX 裡看起來正常，要到 PDF 逐字量字級才會發現字頭跟旁邊的課次一樣小。粗體同理補 `w:bCs`。

## 卡面

- **正面**：字頭 ＋ 課次。希伯來**不按字數縮、按量到的字寬縮**：母音點、達格什、重音各自都是一個碼點，אָדָם 三個字母卻是七個碼點，按碼點數階梯短詞會被一路縮到比中文還小；字母數也不準，מִשְׁפָּחָה 五個字母比 מַלְכוּת 寬得多。改用 PIL 量 Noto Serif Hebrew 的實際字寬（與 LibreOffice 排出來的差 0.1 mm 以內），取塞得下的字級；上限 `HEADWORD_MAX_MM = 54` 是試出來的，量到 60 mm 的字（可用寬度有 69 mm）LibreOffice 仍會把最後一個字母折到第二行、把課次擠掉。其餘各副字級按長度自己縮，拉丁另有一組更寬的字級梯（最長超過四十字元，用希臘那組會縮成看不見），允許折行。
- **正面印多少詞典形**：**讀本印完整的，卡片只在推不出來時才印**（使用者 2026-08-27 定調：
  「除非是不規則的，不然我都知道冠詞和所有格是什麼」）。希臘名詞由
  `scripts/greek_citation_form.py` 判定，第一、二變格的屬格從詞尾加性別就推得出來，
  印了是白印：

  | | 卡上印 | 為什麼 |
  |---|---|---|
  | θεός（陽性 -ος） | `θεός` | 屬格必然是 -ου，推得出來 |
  | σκηνή（陰性 -η） | `σκηνή` | 屬格必然是 -ης |
  | **γένος** | `γένος, ους, τό` | 主格跟 λόγος 一模一樣，屬格卻是 -ους，**不印就分不出來** |
  | **ὁδός** | `ὁδός, οῦ, ἡ` | -ος 卻是陰性 |
  | **προφήτης** | `προφήτης, ου, ὁ` | -ης 卻是陽性 |
  | **δόξα** | `δόξα, ης, ἡ` | 不純 -α，屬格收 -ης 不是 -ας |
  | **σῶμα／πατήρ／πίστις** | 完整 | 第三變格，屬格幹整個變了 |

  兩千張裡名詞 729 張：**259 張保留完整形、470 張只印詞頭**（上冊 128/231、下冊 131/239）。
  屬格與冠詞先取詞表自己的 `printedEntry`，沒有就查 Dodson（CC0，倉庫已凍結）；
  🚨 兩邊都查不到的 80 張只印詞頭，**不自己推一個屬格出來** —— 那正是印在紙上、
  看起來完全正常、學的人無從察覺的那種錯。
  副作用是好的：詞頭短了，字級梯就把字放大，`οἰκοδομή` 現在比原本大一號。
- **背面**：配圖 ＋ 繁中詞義 ＋ 詞性 ＋ 課次。詞義行按自身長度定字級（兩字到二十七字都有），不是設一次就任它溢出。
- **希伯來的詞性連著文法一起印**：名詞一律標到性別（`名詞‧陽性`／`陰性`／`陰陽性`），字形是複數、雙數、或只當附屬形用的再往後接（`名詞‧陰陽性‧複數‧附屬形`）。同一個 Strong 號有兩三張卡時（אָב／אָבוֹת／אֲבִי、עַ֫יִן／עֵינַ֫יִם），這一行是分辨它們的唯一線索。
  🚨 **性別不能看字尾推**：אֶ֫רֶץ、עִיר、יָד、נֶ֫פֶשׁ 沒有陰性字尾卻是陰性，דֶּ֫רֶךְ、רוּחַ 兩性都用。一律讀 OSHB（morphhb）逐詞標註 —— 跟希臘卡用 SBLGNT 同一個路數，標註是事實，字尾是猜的。查無標註的（目前 3 個）就只印「名詞」。
  🚨 **附屬形只印在「同一 Strong 有多張卡」的卡上**：絕大多數單數名詞的絕對形與附屬形同形（אֶ֫רֶץ、יוֹם、מֶ֫לֶךְ），按出現次數多數決會把它們全標成附屬形，而卡上印的其實是絕對形。
- **詞性**：希伯來、拉丁讀詞表既有欄位；希臘詞表沒有，靠 `flashcard_pos.py` 推定，**強證據優先**：

  1. 手列的虛詞與不規則動詞
  2. 詞典形 —— 冠詞＝名詞、三個詞尾＝形容詞、第一人稱＝動詞
  3. **SBLGNT 的逐詞標註**。新約用過的詞，詞性是標註過的事實而不是從詞典形推的；
     前兩條剩下 723 張，這一條就補掉 603 張
  4. 繁中詞義的線索 —— `（配屬格）`＝介系詞、義項全以「的」收尾＝形容詞
  5. `EXTRA_LEXICON`：116 個七十士與教父專有的詞，逐個讀過列表。名詞占絕大多數，
     因為七十士的詞頭不帶冠詞，正是第 2 條要靠的線索

  五條合起來把兩千張全部標完。🚨 副詞字尾的樣式**要收得下重音**：`καλῶς` 帶的是揚抑符，
  寫成 `ως` 的樣式永遠配不到它。🚨 第 5 條那張表是**讀過詞義才寫的，不是從字尾猜的** ——
  希臘文的 `-ος` 既是名詞也是形容詞。**寧可留白，不可標錯** —— 空白只是少一條資訊，
  錯的標籤會被當事實背起來。

## 配圖

來源 **OpenMoji 17.0.0（CC BY-SA 4.0）**，4,565 張風格一致的卡通 SVG，授權標示印在封面。44 MB 圖檔不進 git，matcher 會自己下載。

matcher 由嚴到寬四段，配不到就留白：

1. **人工 override**：以 emoji 的**本名**（不是 hexcode）指定，寫錯會當場報「查無此圖」而不是靜靜印錯。高頻核心詞與虛詞都在這裡。
2. **繁中詞義轉移**：五副共用同一套繁中詞義，別副已經配過的詞義就沿用（πῦρ 和 אֵשׁ 都是「火」）。兩副互讀、交替跑到數字不再動為止，兩輪就夠。
3. **emoji 本名精確比對**，**絕不比對標籤欄**。比標籤有 72% 命中率，但會把「房屋」配成盆栽、「道路」配成爆炸頭、「水」配成汗滴。
4. **留白**。

`AMBIGUOUS_EN` 另外擋掉義項會分岔的英文詞（watch 動詞 vs 手錶、bear 動詞 vs 熊），因為 Strong 的釋義是英文，而英文滿地都是這種詞。

### 第二層圖庫：補「不相干的詞共用一張圖」

OpenMoji 只有兩千多個概念，五副課內詞卡卻有 3,802 張，結果 681 張圖被重複用掉——
希臘卡有一張握手用在 26 張卡上。**同詞根共用是刻意的**（בֵּן／בָּנִים 都用男孩），
**不相干的詞共用才是教錯**：學的人會把兩個字記成同一件事。

`scripts/iconify_card_images.py` 只動後者，去 Iconify 上四個開源圖庫找同名圖示：

| 圖庫 | 張數 | 授權 | 強項 |
|---|---:|---|---|
| game-icons | 4,133 | CC BY 3.0 | 古代器物最齊（鐮刀、戰車、祭壇、軛） |
| Phosphor | 9,072 | MIT | 線條乾淨 |
| MDI | 7,447 | Apache 2.0 | 概念最全 |
| Tabler | 6,184 | MIT | 與 Phosphor 互補 |

一次抓下整份圖示清單在本機比對，不逐字打 search API（三千多張卡會打上萬次）。
SVG 用 PyMuPDF 轉 PNG（`fitz.open("x.svg")` 直接讀，這台機器的 cairo 與 rlPyCairo 都裝不起來）。
四個圖庫的授權標示要印在封面。

🚨 **這一層一定要人工逐張看過才能上：328 張自動配出來的圖有 81 張是錯的（25%）。**
英文對得上不代表圖對，而 UI 圖庫的命名是給軟體用的，撞名率極高：

| 圖示 | 實際畫的 | 配到哪個詞 |
|---|---|---|
| `mdi:iron` | 熨斗 | 鐵 |
| `ph:alien` | 外星人 | 陌生人、外邦的 |
| `ph:command` | ⌘ 指令鍵 | 吩咐、命令 |
| `tabler:grave` | 墓碑 | 寫、著文 |
| `mdi:cast` | 投影 | 澆灌、鑄造 |
| `game-icons:help` | 問號 | 幫助、輔助 |
| `mdi:food` | 漢堡 | 食物、糧食 |

審圖流程：`python scripts/flashcard_contact_sheet.py --audit-icons` 會把這一層配到的圖
排成**標了中文詞義的樣張**（每頁 40 張，8 欄）——只印圖示名字看不出錯，一定要連中文詞義一起印。
逐張看過，把錯的記進 `output/source-cache/flashcards/icon-rejects.json`（`圖示|英文關鍵詞` 一行一組），
重跑時那張卡會自動去試下一個候選詞。
2026-08-27 這一輪的成果：三語不同的圖 **1,360 → 1,601**，留下 247 張都是看過的。

### 手工補圖的紀律（把某副補到 100% 時就是在做這件事）

- **先看圖再信名字。** 從名字完全看不出來的錯，這一關抓過這些：

  | 名字 | 實際畫的 | 配在哪張就錯 |
  |---|---|---|
  | `wedding` | 帶十字架的教堂 | 希伯來聖經的「新婦」 |
  | `tap` | 手指點螢幕 | 「水龍頭」 |
  | `assembly group` | 大人牽小孩 | 「會眾」 |
  | `index pointing at the viewer` | 印出來像拳頭 | 指示類的虛詞 |
  | `emergency exit door` | 人往**外**跑 | 「領進」——教成相反 |
  | `ogre` | 日本的鬼 | 「蠻族人」——不對也不妥 |
  | `passport control` | 查證件的官員 | 「皈依者」 |
  | `bellhop bell` | 餐廳送餐鈴 | 「關切」 |

  🚨 還有**名字有、圖根本沒有**的：`white square`（U+25A1）的檔案是 OpenMoji 自己的缺字佔位框
  （粉紅底、打叉），會原封不動印在卡上。拿已知佔位檔的 sha256 去比對整張配圖表就揪得出來，
  `white large square` 才是真的方框。補完一批先跑：

  ```
  python scripts/flashcard_contact_sheet.py --names "x-ray" "delete" "wedding"
  python scripts/flashcard_contact_sheet.py --deck hbo --sample 48
  ```

- **重複用同一張圖：同詞根可以，語意相對不行。** 同義詞共用一張是這副牌一貫的做法（門／出去／入口都用門），動詞與其名詞共用更是好事（רָעֵב 與 רָעָב 同一張🤤、שָׁבָה 與 שְׁבִי 同一把鎖）。但語意相對的兩張共用一張就是教錯，這一關抓過：「饑荒」跟「吃」共用🍴、「禁食」跟「吃」共用🍴、
  「管教」跟「你」共用☝️、「公義」跟「不義」共用同一支⚖️、「無身體的」跟「惡魔」共用同一隻👻。
  每輪補完**按圖分組，把共用同一張的詞義讀一遍**。一個省事的篩法：把詞義以「不／無／非／未」
  開頭的卡挑出來，看它們的圖還配給了誰 —— 多數是同義（不朽＝永遠、無瑕疵＝純潔），
  真正相對的只有幾組，但每一組都得拆開。
- **時代錯置是內容錯誤，不是風格問題。** 跟聖名同一條規矩：聖所用中性的 `place of worship` 🛐 不用會堂或教堂；但 מְנוֹרָה 就用燭台 —— 那裡燭台是那個器物本身，不是把後起符號讀回去。
- **虛詞給符號不給場景**：疑問助詞❓、כְּ ＝、לְ →、בְּ 🚩、מְעַט 🤏、עַד ♾️、בְּלִי 🪹。
- **沒有 Strong 號的詞用字形當鍵**：希伯來的 בְּ／כְּ／לְ／הֲ 走 `OVERRIDES_BY_FORM`，鍵要從詞表原字**複製**——בְּ、כְּ 的 shva 後面還有 dagesh，手打的鍵會靜默配不到、也不會報錯。
- **借來的圖對借方可能是錯的**：詞義轉移拿到的圖，遇到虛詞特別容易歪（拉丁 `itaque`「因此」借到🔚，但結論是往前的箭頭不是停止）。override 先跑就是為了讓後一副能改掉前一副的圖。
- **一張錯圖，學的人改不掉。** 拿不定主意時留白比亂配好；使用者要的是「每張都有圖」，不是「每張都有東西」。

### 已排除的圖源（別再花時間）

- **Canva**：Connect API 合作夥伴審核制，授權也不涵蓋批次匯出再製成自己的教材。
- **AI 生圖**（2026-08-25 實測）：七把 Gemini key 對 `gemini-2.5-flash-image`／`gemini-3.1-flash-image` 全 429（生圖等於付費層功能），NVIDIA 生圖端點 500/404/timeout。**若日後有付費 Gemini key，這是把風格做得比 emoji 更貼的最佳路徑，值得優先重試。**
- **Openclipart**：JSON API 已死（搜尋端點回 HTML），而且會把幾十位作者的風格混進同一副牌。

## 附錄卡（三副，接在課內詞卡後面）

讀本後面那幾張參考表——專名（人名／地名／民族與國名／君王／使徒／教宗與主教…）、
數字與度量衡、親屬稱謂、曆法與月份、教會職分——都不在五十課的詞表裡，另出三副：

```
python scripts/classify_proper_names.py --language all --write   # 先補 category
python scripts/classify_proper_names.py --reapply --write        # 上游重生附錄後只補回分類
python scripts/build_flashcards.py --deck hbo-appendix           # 或 grc-appendix / lat-appendix
```

與課內詞卡的差別只有三處，其餘（尺寸、欄序、雙面規則）完全共用：

- **框色按分節輪替，不按課次**：同一節的卡同色。卡片走 `colorKey` 這個欄位，
  詞卡不給就退回課次，所以兩種卡可以共用同一支 `framed()`。
- **下緣印分節不印課次**（`footer` 欄位）：附錄詞沒有課次可印。
- **不配圖**：人名地名與數字沒有誠實的 emoji 可對，全部留白。

**沒有繁中譯名的一律不收**，並在輸出時報出被排除的條數。

分節次序：專名走 [scripts/proper_name_categories.py](../../../scripts/proper_name_categories.py)
的 `PRINT_ORDER`（紙本附錄、網頁與卡片三處同一個次序），其餘各表走資料裡本來就有
的 `group`，照首次出現接在後面。判不出來的專名留在「待歸類」，不倒進「其他人名」
——倒進去等於宣稱它是人名。

### 兩張表刻意不收

- 拉丁上冊〈動詞主要部分與不規則變化〉841 條：那是查變化用的形態表，做成卡片會
  和課內動詞卡整批重複。
- 拉丁下冊〈近現代教廷拉丁的地名、機構名與專名〉400 條：全無中文，而且混進了
  `Psal`、`Joan`、`Latine`、`Cardinalis`、`Redemptoris` 這類縮寫、形容詞與普通名
  詞。要修的是那張表本身，不是卡片。

### 希伯來數字表是一對詞形，不是一個

`hbo-appendix` 的數字表存的是陽性／陰性一對 `pointed`，沒有單一詞形。合成一張卡
會逼讀者同時背兩個形，所以各出一張，中文那面標「（陽性）」「（陰性）」。任何新語
言的數字表都要先看它是不是這種成對結構。

## 出片

```
python scripts/hebrew_card_grammar.py --write           # 希伯來的性、數、狀態（改詞表才要重跑）
python scripts/match_flashcard_images.py --write        # 希伯來配圖表（OpenMoji）
python scripts/iconify_card_images.py --lang hbo --write   # 第二層圖庫，補共用圖的卡（grc / lat）
python scripts/flashcard_contact_sheet.py --names "x-ray" "wedding"   # 決定用哪張圖前先看圖
python scripts/flashcard_contact_sheet.py --audit-icons                # 第二層圖庫的審圖樣張（附中文詞義）
python scripts/build_flashcards.py --deck hbo           # 或 grc1 / grc2 / lat1 / lat2 / hbo-appendix / grc-appendix / lat-appendix
python scripts/build_flashcards.py --deck hbo --limit 16   # 打樣 16 張
```

轉 PDF 前**先清掉 `PYTHONHOME`／`PYTHONPATH`**，留著 `soffice` 會 exit 0 但什麼都沒寫：

```
env -u PYTHONHOME -u PYTHONPATH -u PYTHONIOENCODING \
  "C:/Program Files/LibreOffice/program/soffice.com" --headless --norestore \
  -env:UserInstallation=file:///<系統暫存>/lo-profile-cards \
  # profile 一定要寫在系統暫存（`tempfile.mkdtemp`），不要寫進 output/——
  # 舊做法在 output/ 留了 18 份 lo-profile-* 垃圾，2026-08-27 已清。
  --convert-to pdf --outdir .../output/flashcards .../output/flashcards/<deck>.docx
```

## 驗收（每次重出都跑）

- 頁數等於 `2 + 2 × ceil(張數 / 8)`。多出來就是排高踩到上面那個坑。
- **每張背面剛好 8 張圖**（配圖 100% 的牌組）：`len(page.images)` 對所有奇數頁都該是 8。出現 7 就是有卡在重建時掉了圖。
- 背面最左的卡＝正面最右的卡（鏡像對了才裁得成一副）。
- **字頭字級要是宣告的那個**：`pdfplumber` 逐字看 `size`，希伯來該是 54 pt（量寬後縮的最小 48 pt），不是 11 pt —— 這條就是為了擋 `w:szCs` 那個坑。
- 字頭沒有折行：用 PyMuPDF 取每格 `size>20` 的 span，同格內 y 差一整行（約 64 pt）就是折了；差 20 pt 上下是字母上方的重音符號，不算。
- 字頭沒有字體回退：`pdfplumber` 逐字看 fontname，不該出現 Tahoma／Calibri。**例外**：希伯來有兩張卡的繁中詞義行內嵌希伯來文（「弟兄；兄弟（אָח 的複數）」「誡命（מִצְוָה 的不規則複數）」），那一段走 UI 字型、會回退到 Tahoma，是既有現象不是壞掉。
- 配圖表每一把鍵都對得回詞表（matcher 內建 assert）。
- **卡框每頁 8 個、一個都不越裁切線**：PyMuPDF 取 `type=="s"` 且高度 > 10 mm 的線條，
  外緣要落在該排的 5–99 / 99–193 mm 內，寬高各為 68.25 × 88 mm。
- **十色到齊且對得上課次**：把每頁的框色抓出來比 `FRAME_COLORS[(lesson-1) % 10]`，
  第 11 課要回到第 1 課的紅。
- 頁面尺寸、字型內嵌、U+FFFD 與空白頁：`python scripts/render_and_check_reader_pdfs.py --only <stem>`
  一次做完轉檔與這四項（同一支腳本也管五本讀本）。

```python
import pdfplumber, collections
pdf = pdfplumber.open("output/flashcards/hebrew-flashcards-1000.pdf")
print(len(pdf.pages))                                                    # 252
print(collections.Counter(len(pdf.pages[i].images) for i in range(3, 252, 2)))   # {8: 125}
```

## 一個把好的中文擋掉的閘

詞義檢查曾把「只要 OpenCC 的 `s2t` 改動過就算簡體」當判準，而 `s2t` 會改寫本來就是繁體的字。
「台」變「臺」，於是「讀經台」被退回十一次，`ambō` 一直沒有詞義、整副卡建不起來。更糟的是
**「祢」會變成「禰」** —— 那是天主教對神的第二人稱敬語，本專案翻的禱文幾乎篇篇都有，
其中一篇讀文就叫《願祢受讚頌》。每一份用到它的譯文都被丟掉重來，無限循環。

現在的作法是整行其他部分乾淨時這些異體字個別放行，所以「皇后」「公里」會過、「以后我们」仍然退；
「号」刻意不放行，那個是真的簡體。**任何寫成往返比對的繁體中文閘都要小心這一類。**

## 國小英語 1000：唯一一副不留白的

使用者 2026-09-04：「國小單字卡不能留白」。這一句把整副卡的規則反過來——別副的最後
一關是「挑不到就空著」，這副的最後一關是**當場報錯**。差別出在用途：別副是給已經在
讀原文的人查對，留白只是少一條資訊；這副是給小學生看圖記字，**沒有圖的卡在這副裡
沒有用**。

四件別副沒有的事：

### 一、詞表要先篩過再排

站上 `/english` 那份是 20 課 × 50 字（教育部國中小基本字彙）。使用者要 50 課 × 20 字，
而且「a the to 這種沒有具體意思的就不要了」。`build_english_vocabulary.py` 抽掉 42 個
純虛詞（冠詞、對等連接詞、助動詞與情態動詞、指示詞、純數量詞、程度副詞），
**同主題補回等量的具體詞**，讓每個主題仍是 50 字、全書仍是 1000 字。

代名詞、疑問詞、介系詞與方位詞**留下**——那幾類畫得出來（you 👉、up ⬆️），
單字卡向來就是「虛詞給符號不給場景」。

一個主題橫跨兩課半（50 ÷ 20），所以卡背同時印課次與主題。

🚨 `may/ might` 那一筆是站上把情態動詞跟五月併在一起了；抽掉情態動詞之後十二個月會
缺五月，所以補回的是月份 May，不是別的字。

🚨 **大小寫正規化只能壓「首字母大寫、其餘小寫」的普通詞。** `I` 會變成 `i`、`OK` 會
變成 `oK`，兩個都會原封不動印在卡上，而且看起來只是「有點怪」，不像壞掉。

### 二、數字、星期、月份、上下午要自己畫

`english_picture_tiles.py`，56 張。這批詞任何圖庫都沒有：OpenMoji 的數字鍵帽只到 10，
Iconify 兩萬五千個圖示名字裡沒有 Monday，而近似的圖是錯的（`eleven o'clock` 是時鐘
不是十一）。

畫出來的東西**刻意不帶文字語言**，只用數量與位置表達：

| 詞 | 畫什麼 |
|---|---|
| 十一 | 十一個點，外加阿拉伯數字 11 |
| 第九 | 十個圈，第九個塗滿，上面一個箭頭 |
| 星期三 | 七格的週條，第三格塗滿 |
| 週末 | 同一條週條，最後兩格塗滿 |
| 十月 | 三乘四的年曆格，第十格塗滿 |
| 上午／下午 | 鐘面塗上半圈／下半圈 |

這樣卡背才是一張真的圖：正面英文、背面圖加中文，中間不靠另一種文字轉手。

### 三、站上既有的 559 個 hexcode 不可信

那批是拿英文名自動配的，正是本 skill 一直在防的那種錯，而且錯得很兇：

| 卡 | 站上配到 | 為什麼會這樣 |
|---|---|---|
| order 點餐 | 🦁 獅子 | 生物分類的「目」也叫 order |
| spell 拼單字 | 🧙 巫師 | 咒語也叫 spell |
| fly 飛行 | 🪰 蒼蠅 | |
| spring 春天 | 🐝 蜜蜂 | 泉水／彈簧／春天三義 |
| table 桌子 | 🏓 桌球 | table tennis |
| cross 越過 | 🤞 交叉手指 | |
| body 身體 | 💀 骷髏 | |
| age 年紀 | 🔞 未滿十八禁止 | |
| comic 漫畫 | 💩 | |
| summer 夏天 | 🍺 啤酒 | |
| soldier 軍人 | 🥷 忍者 | |
| large 大的／small 小型的 | 同一張 🤪 | **語意相對卻共用一張** |

所以人工指名（`OVERRIDES` 與 `ICONIFY_OVERRIDES`）排在站上那層**前面**，蓋掉它們。

🚨 **這一批只有把卡排成樣張逐張看過才抓得到**：

```
python scripts/english_card_sheet.py --source preset --page 1     # 每頁 80 張，六頁
python scripts/english_card_sheet.py --source iconify --page 1 --per-page 100
```

圖旁邊一定要印英文與中文——只看圖示名字看不出錯。2026-09-04 這一輪看完六頁，
改掉約九十張。

### 四、抽象詞給符號不給場景

understand、ready、basic、real 這種概念，Iconify 兩萬五千個名字裡一個都沒有。
照虛詞的老規矩處理，而且**讓相關的幾張看得出關係**：

correct ✅／wrong ❎／mistake ❌ 成組、ready 綠燈 🟢、fact 圖釘 📌、
let 開鎖 🔓 對 keep 上鎖 🔒、excellent 🥇、special ✨。
符號對抽象詞是誠實的，近似的場景圖不是。

### Iconify 那層要染色

四個線條圖庫抓下來是黑的，全黑線條擺在彩色 emoji 中間像沒畫完。
`?color=%231E6FD9` 直接在 API 上染，不必自己改 SVG。指名時用**確切的圖示 id**
（`mdi:library`），不是關鍵詞搜尋——搜尋出來的東西看起來像成功而畫的常是別的。
`icon_names()` 的索引會被前面的圖庫覆蓋，所以 `mdi:eraser` 查索引會落空，
但直接抓 API 是通的；要驗名字存不存在就打一次 API，別只查索引。

### 共用同一張圖的檢查一定要跑

```
python -c "import json,collections; d=json.load(open('output/source-cache/flashcards/english-card-images.json',encoding='utf-8'))['images']; g=collections.defaultdict(list); [g[r['file']].append((w,r['glossZh'])) for w,r in d.items()]; [print(len(v),v) for k,v in g.items() if len(v)>2]"
```

同義共用是好的（hello／hi／greeting 都用 👋，pet／dog 都用 🐶），
**語意相對共用就是教錯**：hungry 飢餓的與 full 吃飽的原本共用同一張 😋、
large 與 small 共用同一張 🤪。每輪補完按圖分組把詞義讀一遍。

### 出片

```
python scripts/build_english_vocabulary.py          # 詞表（改 DROP／REFILL 才要重跑）
python scripts/english_picture_tiles.py --probe     # 自繪圖，順便出樣張看一遍
python scripts/match_english_card_images.py --write # 配圖；還有留白會直接報錯
python scripts/build_flashcards.py --deck eng
python scripts/render_and_check_reader_pdfs.py --only english-flashcards-1000
```

## 加下一副（新語言）時

1. 詞表要先在 [data/originalReaders/vocabulary/](../../../data/originalReaders/vocabulary/) 定案（含繁中詞義與詞性），單字卡不負責補資料層。
2. 在 `build_flashcards.py` 的 deck 表加一筆（字型、字級梯、封面文案、詞表路徑）。
3. 複製一支 matcher，**先讓它讀既有各副的配圖表**做詞義轉移，再開始人工補 —— 這一段是白撿的，拉丁 802 張裡有 444 張是這樣來的。
4. 版面照抄，不要重算卡高。

相關：[[project_original_reader_flashcards]]、[[project_hebrew_original_reader]]、[[project_latin_original_reader]]、[[feedback_skill_md_keep_current]]
