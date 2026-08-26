---
name: original-reader-flashcards
description: 由原文讀本詞表產出「可裁切的實體印刷單字卡」— A4 橫式每頁 8 張、74.25×94 mm、正面原文背面繁中、雙面長邊翻、不印裁切線，配圖走 OpenMoji。目前五副：聖經希伯來文 1000、通用希臘文上下冊各 1000、教會拉丁文上下冊各 1000。Use when 要新增／重出某一副卡、要把某副的配圖率往上補、要換掉某張圖、要加第六副（新語言）、要改版面（卡片尺寸／字級／欄序）、頁數莫名變兩倍要 debug、或使用者說「單字卡」「字卡」「配圖」。方法在本檔，逐副現況在讀本 skill 的 references/flashcard-decks.md。
---

# 原文讀本印刷單字卡

規格對齊使用者家教在用的《家教單字卡.pdf》，同一把裁刀、同一組印表機設定通吃五副。

> 詞表來源：[data/originalReaders/vocabulary/](../../../data/originalReaders/vocabulary/)（`hebrew-1000.json`／`greek-1000.json`／`greek-2000.json`／`latin-2000.json`）
> 產卡：[scripts/build_flashcards.py](../../../scripts/build_flashcards.py)
> 配圖：[scripts/match_flashcard_images.py](../../../scripts/match_flashcard_images.py)（希伯來）／[match_greek_card_images.py](../../../scripts/match_greek_card_images.py)／[match_latin_card_images.py](../../../scripts/match_latin_card_images.py)
> 詞性推定（希臘）：[scripts/flashcard_pos.py](../../../scripts/flashcard_pos.py)
> 看圖：[scripts/flashcard_contact_sheet.py](../../../scripts/flashcard_contact_sheet.py)
> 逐副現況與歷史：[skills/build-original-language-reader/references/flashcard-decks.md](../../../skills/build-original-language-reader/references/flashcard-decks.md)
> 🚨 希臘與拉丁兩副 2026-08-25 起由**別的 session** 負責；讀它們的 map 沒問題，別重跑它們的 matcher、別改它們的卡檔。

## 資料流

```
詞表 JSON ──► matcher（配圖，寫 output/source-cache/flashcards/*-card-images.json）
           └─► build_flashcards.py --deck hbo|grc1|grc2|lat1|lat2 ──► DOCX ──LibreOffice──► PDF
```

配圖表是獨立產物，重跑 matcher 不會動到卡檔；換過圖一定要重跑 build 再重出 PDF。

## 版面（五副共用，別自己重算）

| | |
|---|---|
| 紙 | A4 橫式 297 × 210 mm |
| 格 | 4 欄 × 2 列，每頁 8 張 |
| 卡 | 74.25 × 94 mm |
| 邊界 | 上下 5 mm，左右 0 |
| 裁切位置 | 橫向距頂 5 / 99 / 193 mm，縱向距左 74.25 / 148.5 / 222.75 mm |
| 雙面 | 長邊翻；**背面欄序鏡像 4-3-2-1** |
| 頁數 | `2 + 2 × ceil(張數 / 8)`，1000 張＝252 頁 |

🚨 **卡高 94 mm 是量出來的不是算出來的。** LibreOffice 保留的垂直空間比宣告的邊界多，兩排一接近可用高度就把第二排推到下一頁、印出一頁空白。10 mm 邊界失敗、5 mm 可行；97 mm 排高失敗、94 mm 可行。**頁數變兩倍就是踩到這個** —— 把排高調小，別跟它講道理。另外別在設了 `row.height` 之後又補一個 `w:trHeight`，兩條規則打架，症狀一模一樣。

🚨 **不印裁切線**（使用者指定）：線印歪一毫米，每張卡的邊都是斜的。裁切位置印在封面。

## 卡面

- **正面**：字頭 ＋ 課次。希臘、拉丁印完整詞典形（`ἄνθρωπος, -ου, ὁ`／動詞四主要部分），字級按長度自己縮，拉丁另有一組更寬的字級梯（最長超過四十字元，用希臘那組會縮成看不見），允許折行。
- **背面**：配圖 ＋ 繁中詞義 ＋ 詞性 ＋ 課次。詞義行按自身長度定字級（兩字到二十七字都有），不是設一次就任它溢出。
- **詞性**：希伯來、拉丁讀詞表既有欄位；希臘詞表沒有，靠 `flashcard_pos.py` 由詞典形、SBLGNT 形態標記、繁中詞義與人工清單推定。**寧可留白，不可標錯** —— 空白只是少一條資訊，錯的標籤會被當事實背起來。

## 配圖

來源 **OpenMoji 17.0.0（CC BY-SA 4.0）**，4,565 張風格一致的卡通 SVG，授權標示印在封面。44 MB 圖檔不進 git，matcher 會自己下載。

matcher 由嚴到寬四段，配不到就留白：

1. **人工 override**：以 emoji 的**本名**（不是 hexcode）指定，寫錯會當場報「查無此圖」而不是靜靜印錯。高頻核心詞與虛詞都在這裡。
2. **繁中詞義轉移**：五副共用同一套繁中詞義，別副已經配過的詞義就沿用（πῦρ 和 אֵשׁ 都是「火」）。兩副互讀、交替跑到數字不再動為止，兩輪就夠。
3. **emoji 本名精確比對**，**絕不比對標籤欄**。比標籤有 72% 命中率，但會把「房屋」配成盆栽、「道路」配成爆炸頭、「水」配成汗滴。
4. **留白**。

`AMBIGUOUS_EN` 另外擋掉義項會分岔的英文詞（watch 動詞 vs 手錶、bear 動詞 vs 熊），因為 Strong 的釋義是英文，而英文滿地都是這種詞。

### 手工補圖的紀律（把某副補到 100% 時就是在做這件事）

- **先看圖再信名字。** `wedding` 是帶十字架的教堂（希伯來聖經的「新婦」不能用）、`tap` 是手指點擊不是水龍頭、`assembly group` 是大人牽小孩、`index pointing at the viewer` 印出來像拳頭。這四張都不是從名字看得出來的。補完一批先跑：

  ```
  python scripts/flashcard_contact_sheet.py --names "x-ray" "delete" "wedding"
  python scripts/flashcard_contact_sheet.py --deck hbo --sample 48
  ```

- **重複用同一張圖：同詞根可以，語意相對不行。** 同義詞共用一張是這副牌一貫的做法（門／出去／入口都用門），動詞與其名詞共用更是好事（רָעֵב 與 רָעָב 同一張🤤、שָׁבָה 與 שְׁבִי 同一把鎖）。但「饑荒」不能跟「吃」共用🍴、「管教」不能跟「你」共用☝️ —— 那是教成相反或教成別的字。每輪補完**按圖分組，把共用同一張的詞義讀一遍**。
- **時代錯置是內容錯誤，不是風格問題。** 跟聖名同一條規矩：聖所用中性的 `place of worship` 🛐 不用會堂或教堂；但 מְנוֹרָה 就用燭台 —— 那裡燭台是那個器物本身，不是把後起符號讀回去。
- **虛詞給符號不給場景**：疑問助詞❓、כְּ ＝、לְ →、בְּ 🚩、מְעַט 🤏、עַד ♾️、בְּלִי 🪹。
- **沒有 Strong 號的詞用字形當鍵**：希伯來的 בְּ／כְּ／לְ／הֲ 走 `OVERRIDES_BY_FORM`，鍵要從詞表原字**複製**——בְּ、כְּ 的 shva 後面還有 dagesh，手打的鍵會靜默配不到、也不會報錯。
- **借來的圖對借方可能是錯的**：詞義轉移拿到的圖，遇到虛詞特別容易歪（拉丁 `itaque`「因此」借到🔚，但結論是往前的箭頭不是停止）。override 先跑就是為了讓後一副能改掉前一副的圖。
- **一張錯圖，學的人改不掉。** 拿不定主意時留白比亂配好；使用者要的是「每張都有圖」，不是「每張都有東西」。

### 已排除的圖源（別再花時間）

- **Canva**：Connect API 合作夥伴審核制，授權也不涵蓋批次匯出再製成自己的教材。
- **AI 生圖**（2026-08-25 實測）：七把 Gemini key 對 `gemini-2.5-flash-image`／`gemini-3.1-flash-image` 全 429（生圖等於付費層功能），NVIDIA 生圖端點 500/404/timeout。**若日後有付費 Gemini key，這是把風格做得比 emoji 更貼的最佳路徑，值得優先重試。**
- **Openclipart**：JSON API 已死（搜尋端點回 HTML），而且會把幾十位作者的風格混進同一副牌。

## 出片

```
python scripts/match_flashcard_images.py --write        # 希伯來配圖表
python scripts/build_flashcards.py --deck hbo           # 或 grc1 / grc2 / lat1 / lat2
python scripts/build_flashcards.py --deck hbo --limit 16   # 打樣 16 張
```

轉 PDF 前**先清掉 `PYTHONHOME`／`PYTHONPATH`**，留著 `soffice` 會 exit 0 但什麼都沒寫：

```
env -u PYTHONHOME -u PYTHONPATH -u PYTHONIOENCODING \
  "C:/Program Files/LibreOffice/program/soffice.com" --headless --norestore \
  -env:UserInstallation=file:///.../output/lo-profile-cards \
  --convert-to pdf --outdir .../output/flashcards .../output/flashcards/<deck>.docx
```

## 驗收（每次重出都跑）

- 頁數等於 `2 + 2 × ceil(張數 / 8)`。多出來就是排高踩到上面那個坑。
- **每張背面剛好 8 張圖**（配圖 100% 的牌組）：`len(page.images)` 對所有奇數頁都該是 8。出現 7 就是有卡在重建時掉了圖。
- 背面最左的卡＝正面最右的卡（鏡像對了才裁得成一副）。
- 字頭沒有字體回退：`pdfplumber` 逐字看 fontname，不該出現 Tahoma／Calibri。**例外**：希伯來有兩張卡的繁中詞義行內嵌希伯來文（「弟兄；兄弟（אָח 的複數）」「誡命（מִצְוָה 的不規則複數）」），那一段走 UI 字型、會回退到 Tahoma，是既有現象不是壞掉。
- 配圖表每一把鍵都對得回詞表（matcher 內建 assert）。

```python
import pdfplumber, collections
pdf = pdfplumber.open("output/flashcards/hebrew-flashcards-1000.pdf")
print(len(pdf.pages))                                                    # 252
print(collections.Counter(len(pdf.pages[i].images) for i in range(3, 252, 2)))   # {8: 125}
```

## 加第六副（新語言）時

1. 詞表要先在 [data/originalReaders/vocabulary/](../../../data/originalReaders/vocabulary/) 定案（含繁中詞義與詞性），單字卡不負責補資料層。
2. 在 `build_flashcards.py` 的 deck 表加一筆（字型、字級梯、封面文案、詞表路徑）。
3. 複製一支 matcher，**先讓它讀既有各副的配圖表**做詞義轉移，再開始人工補 —— 這一段是白撿的，拉丁 802 張裡有 444 張是這樣來的。
4. 版面照抄，不要重算卡高。

相關：[[project_original_reader_flashcards]]、[[project_hebrew_original_reader]]、[[project_latin_original_reader]]、[[feedback_skill_md_keep_current]]
