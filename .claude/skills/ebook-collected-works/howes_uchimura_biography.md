> ⚙️ **引擎政策**：LLM 工作一律 Gemini（主）→ NVIDIA → Haiku。**本卷例外**：使用者
> 2026-09-06 指定用 Haiku（免費層 Gemini 一天 20 次／key，撐不起 1,582 段）。
> 見 [[feedback_engine_nvidia_no_haiku]]、[[reference_gemini_free_tier_quotas]]。

# 豪斯《日本的現代先知》—— 內村鑑三評傳（本 portal 第一本「寫作家的書」）

內村案例的第三波。前兩波都是內村自己的著作（[uchimura_collected_works.md](uchimura_collected_works.md)：
青空文庫 11 篇日文、archive.org 兩部英文原著）；這一本是**別人寫他的傳記**。

## 為什麼選這一本

使用者要「最權威或者最通俗」的一本。盤點結果：

| 書 | 定位 | 版權 | 取得 |
|---|---|---|---|
| **John F. Howes,《Japan's Modern Prophet: Uchimura Kanzō, 1861–1930》**（UBC Press 2005, 465pp） | **英文學界定本**。作者 UBC 亞洲研究榮譽教授，五十年研究的成果；2006 年 Canada-Japan Literary Award＋Choice 年度優良學術書 | 2005，在著作權內 | libgen.li 有原生 PDF（md5 `6ce9cfab…`，9.55 MB，文字層乾淨） |
| 鈴木範久《内村鑑三》岩波新書 1984 | 日文最通俗的入門評傳 | 在著作權內（作者 1935 生） | 日文書 libgen／z-lib 覆蓋極差，沒找到 |
| 政池仁《内村鑑三伝》教文館 1960 | 日文最厚的傳記 | 政池仁卒 1985 → 2056 才 PD | 未見電子檔 |
| 藤井武、塚本虎二等門人的追憶 | 一手史料，非系統傳記 | 藤井卒 1930＝PD；塚本卒 1973＝2043 | — |

**沒有任何一本內村傳記有中譯本**（中文世界只有內村本人著作的中譯）。REFERENCE-first
（[[feedback_collected_works_reference_first]]）走完是「查無」，所以自譯。

⚠️ **本書仍在著作權內**。私人站沿用 [[feedback_jung_nonpd_english_first]] 的姿態
（榮格 Hull 英譯同樣非 PD），但這一點與前兩波（內村本人著作全球公有領域）性質不同，
別把「內村＝PD」的結論套到這一本上。

## 掛在哪裡

`ebook_id` 用內村命名空間的 `d0000000-…-0009`（前兩波用掉 0001–0008），
`collection: 'collected-works'`（[[feedback_collected_works_not_in_library]]），
store 的內村 hub 底下新開 category「**傳記與研究（他人著作）**」——這是 portal 第一次
在作家 hub 裡放非該作家本人的書，往後其他 hub 要放評傳沿用這個 category 名。

## Pipeline

`scripts/howes_build.py`（+ `scripts/tests/test_howes_build.py` 13 例綠），
translate/build/upload 沿用 `uchimura_auto.py --author howes`。

    python scripts/howes_build.py --dry
    python scripts/uchimura_auto.py --author howes --list
    python scripts/uchimura_auto.py --author howes --run-queue --backend haiku

**規模**：19 節／1,582 段／1,074,253 字（序言＋導論＋16 章＋結論）。

**只譯正文**。Notes（p428–451）、Selected Bibliography、Index 是檢索裝置不是散文，
不譯；Chronology 與 Glossary 是兩欄表格，而且內村 hub 自己已經有年表，一併略過。
節界直接取 PDF 內嵌的 TOC 頁碼（三個 Part 扉頁落在區間之間，自然被跳過）。

## 原生 PDF 的分段：靠版面幾何，不是靠空行

這本是 Acrobat Distiller 出的原生 PDF，**有真的文字層，不需要 OCR**——但也因此
`get_text()` 出來是一行一行的，段落界線不在文字裡而在版面上。四個量測到的常數：

| 訊號 | 值 | 用途 |
|---|---|---|
| 正文行 x0 | ≈37 | 續行 |
| 段落首行 x0 | ≈46 | **縮排＝新段落** |
| 正文字級 | 9.0 | — |
| 引文區塊字級 | 8.5 | 字級變化＝引文起訖，段前加 `> ` |
| 書眉字級 | 8.0（y≈36） | 丟 |
| 章名字級 | 18.0 | 丟（章名我們自己給繁中的） |
| 「This page intentionally left blank」 | 12.0 | 丟 |
| 尾註號 | superscript span（flags bit 0，字級 5.2） | **丟** |

三個坑：

1. **尾註號一定要在 span 層丟掉**。它跟正文同一行，不丟的話 `majority.14 There`
   會被翻成「多數。14 還有更多」——引擎會把裸數字當年份或數量譯出來。判準用
   PyMuPDF 的 `flags & 1`（superscript），不要用字級（字級 5.2 太貼近其他小字）。
2. **章名區塊在 PDF 裡不一定排在正文之前**。第 36 頁的章名 block 編號是 2、正文是
   0 和 1，照 block 順序讀會把章名插進頁面中段。`page_lines` 一律先按 y 再按 x 排。
3. **連續引文段落之間沒有縮排可分**（引文行 x0 全是 46），會黏成一大段——最長的一段
   近九千字。`split_long` 按句界切開，`> ` 標記每一片都要帶著；引擎偶爾會把標記吃掉，
   `make_engine` 在輸出端補回來。

## 交接

1. 進度：`python scripts/uchimura_auto.py --author howes --list`
   （log `scripts/logs/howes_translate.log`）；斷了重新分離式啟動 `--run-queue`，
   checkpoint 在 `howes_data/howes-prophet/secN.json` 會自動續傳。
2. 翻完 → store 該卷 `status→done`；reader
   `/collected-works/uchimura/d0000000-0000-4000-8000-000000000009` 截圖驗證。
3. 詞庫是事後補的，抽查發現誤譯用
   `--author howes --redo-matching <regex>` 清掉中招的段落再跑一次，不必整本重來。
4. 要再收一本傳記的話，日文那兩本（鈴木範久／政池仁）都還沒有電子檔；
   真要收得先解決取得問題，別重覆盤點。
