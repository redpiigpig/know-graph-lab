---
name: teaching-playing-cards
description: 由人物名單產出「可裁切的實體印刷撲克牌」— A4 橫式每頁 8 張、71.25×94 mm、正面點數花色＋類別插圖＋中文名＋原文名＋生卒年，背面全牌統一，可照一般撲克牌玩法使用。版面與卡框沿用單字卡那一套（build_flashcards），同一把裁刀通吃。目前兩副：佛教人物、基督宗教人物。Use when 要新增一副撲克牌（換一個宗教／學科的人物名單）、要抽換某張牌的人物或圖、要改點數分類軸、要改花色配色、或使用者說「撲克牌」「做一副牌」。方法在本檔；名單在 data/playingCards/。
---

# 教學用印刷撲克牌

跟 [[original-reader-flashcards]] 共用整套版面，只換卡面，所以**不要重算任何尺寸**。

> 名單：[data/playingCards/](../../../data/playingCards/)（`buddhist.json`／`christian.json`）
> 產牌：[scripts/build_playing_cards.py](../../../scripts/build_playing_cards.py)
> 驗收：[scripts/render_and_check_reader_pdfs.py](../../../scripts/render_and_check_reader_pdfs.py) `--only <stem>`
> 成品：Drive `資料\知識圖工作室\教學\撲克牌\`（`output/` 不進版控）

## 與單字卡的三個差別

1. **背面是統一的牌背。** 撲克牌之所以能玩，靠的就是每張背面長得一樣；資訊全部
   印在正面。單字卡是正面問、背面答，兩者的正反面意義相反。**如果哪天要做「背面
   印生平」的教具版，那就不是撲克牌了**，要另開一個 deck 設定，別改這一支。
2. **框色按花色不按課次**，四色牌：♠ 黑 1B1B1B、♥ 紅 C8102E、♦ 藍 1E6FD9、
   ♣ 綠 1F6B4A，鬼牌紫 7B3FA0、說明卡灰 4A4A4A。四色牌是既有的撲克牌慣例，
   也讓「同一點數的四張」在桌面上一眼分得開。
3. **點數才是分類軸**，花色只作四色分組。這一條印在封面與說明卡上——不寫清楚，
   四個花色會被讀成價值排序。

## 54 張要補成 56 張

一頁 8 張，七張紙 56 格，54 張填不滿。**空著會裁出兩張正面全白的牌**，所以補兩
張說明卡：一張點數分類對照，一張花色與授權說明。`note_cards()` 自動生成，不必
手寫。

## 卡面

- **正面**：左上角與右下角的點數＋花色（`Segoe UI Symbol`——**這是內建字型裡唯一
  同時有 ♠♥♦♣ 與數字的**）、類別插圖、中文名、原文名（`Noto Serif`，梵語轉寫的
  ā ṇ ṃ ś ṭ 只有它有）、生卒年、點數類別。
- 🚨 **鬼牌與說明卡的角標是中文**（大鬼／小鬼／※），Segoe UI Symbol 沒有中日韓字，
  不換字型就靜靜回退成 NotoSansJP-Thin，PDF 驗收才會抓到「未內嵌字型」。
  `index_font()` 就是為了這個。
- 中文名從三個字（藥師佛）到十三個字（若望二十三世與若望保祿二世）都有，
  字級按長度縮（`ZH_STEPS`）。上限 20 pt 是看排版量出來的，再大就頂到插圖。

## 插圖：畫的是「類別」不是「人物肖像」

同一點數的四張共用一張圖，這是**刻意的**——那張圖標的是 K 佛陀、Q 菩薩這個類別。

- 真人肖像一律不用：在世人物（達賴喇嘛、巴契勒）的照片有版權，古代人物的畫像
  又是後世想像，兩者都不該印成「這個人長這樣」。
- 圖以 OpenMoji 的**本名**指定，查無就當場報錯（`icon_path()`）。名字打錯若靜靜
  略過，卡上就是隔壁那張圖——這一類錯印在紙上看起來完全正常。
- 🚨 **名字不等於圖，動手前先看圖**：
  `python scripts/flashcard_contact_sheet.py --names "wheel of dharma" "lotus"`
  OpenMoji 的 ☸ 法輪畫在一個紫色方框裡，跟其餘留白的圖擺在一起像貼錯；改指名
  `noto-v1:wheel-of-dharma`（`prefix:slug` 格式會走 `emoji_variant_images.png_for`）。
- OpenMoji 的 `pagoda`（1F6D4）**有名字沒圖檔**——618 px 那包少了它。這種情況
  `icon_path()` 會報「有名字沒圖檔」，換一張就好。

## 名單的體例

`data/playingCards/*.json`：`ranks`（13 個點數的 `label` 與 `icon`）、`cards`
（52 張，`rank`／`suit`／`zh`／`orig`／`dates`）、`jokers`（2 張，另帶 `label`
與 `icon`）、`sources`（印在封面的三行）。載入時會檢查 13×4 有沒有缺格。

- **生卒年用繁中格式**：`前563–前483`、`約80–150`、`1935–`、`在位 約前307–前267`。
  信仰人物不繫年，寫「願力所成・無生卒年」「經中人物・無生卒年」。
- **原文名**：印度人物用梵語羅馬轉寫，巴利傳統的人物用巴利語轉寫；漢傳、日本、
  藏傳用該語言的通行轉寫。
- 🚨 **使用者給的名單要逐條查過再排版。** 首兩副就抓到六處人名與生卒年對不上：
  讖摩（Khemā）被寫成 Channa（車匿，男性車夫）、蓮華色（Uppalavaṇṇā）被寫成
  Padmavati、勝鬘（Śrīmālādevī）被寫成 Sakyamati、韋提希（Vaidehī）被寫成
  Vajirā、真諦（Paramārtha 499–569）被寫成 Dharmarakṣa 並掛上曇無讖的生卒年、
  印順導師（1906–2005）被掛上 Sulak Sivaraksa 的名字。**譯名沿用使用者的寫法，
  只改事實錯誤**——這兩件事要分開。
- 🚨 **同名不同人要在卡上分開**：亞歷山卓的西里爾（376–444）與斯拉夫使徒西里爾
  （827–869）同在一副牌裡，前者加地名。

## 出片

```
python scripts/build_playing_cards.py --deck buddhist     # 或 christian
python scripts/render_and_check_reader_pdfs.py --only buddhist-playing-cards
```

## 驗收（每次重出都跑）

- 頁數 `2 + 2 × 7 = 16`。
- 每張正面 8 格都有框，外緣落在該排的 7–105 / 105–203 mm 內、寬高 65.25×92 mm。
- 背面八張長得一模一樣（不一樣就不是撲克牌了）。
- 字型全部內嵌，沒有 NotoSansJP-Thin（那是角標字型回退）。
- 頁面 297×210 mm、無 U+FFFD、無空白頁——`render_and_check_reader_pdfs.py` 一次做完。

## 加第三副時

1. 照 `data/playingCards/` 的體例寫名單，13 個點數各四張，兩張鬼牌。
2. 挑十五張類別插圖，**先跑 contact sheet 看過**再寫進 `ranks`。
3. 在 `build_playing_cards.py` 的 `DECKS` 加一筆（名單路徑、輸出檔名、牌背色）。
4. 在 `render_and_check_reader_pdfs.py` 的 stem 清單加一行。
5. 版面照抄，不要重算卡高——那個數字是量出來的，見 [[original-reader-flashcards]]。

相關：[[original-reader-flashcards]]、[[feedback_repo_hygiene]]、[[feedback_skill_md_keep_current]]
