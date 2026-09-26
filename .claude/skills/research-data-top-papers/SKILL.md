---
name: research-data-top-papers
description: 替某一個研究領域策展「最有影響力的 N 篇研究」（首例＝聖經研究五百篇：舊約／新約／次經與典外／批判史四組），做成 /research-data/top-papers/<field> 的文獻回顧頁——一筆一句話說它為何重要、Crossref 逐筆核對、標館內有無全文。使用者 2026-09-26 定調這是常規用法，其他領域（佛學、宗教學、神學、哲學…）照同一套走。Use when 使用者說「抓 N 篇最有影響力的研究／論文」「做某領域的文獻回顧清單」「哪些是某領域的經典論文」、要替新領域開一份、要補一組或改分組、要重跑核對、或問某篇為什麼在／不在清單上。與 [[research-data-theology]]／[[research-data-buddhology]] 的分工：那兩張是「書目分區」，本 skill 是「按研究史排的影響力清單」，可以互相連結但不合併。
---

# 最有影響力的 N 篇研究（/research-data/top-papers/<field>）

## 這是什麼、不是什麼

使用者要的是**完整的文獻回顧**：讀一遍就知道這個領域一百五十年來誰改變了大家怎麼問問題。
所以它是**策展清單**，不是引用數排行——引用數偏向英語近三十年、會漏掉德語老論文與奠基性專著。
使用者 2026-09-26 在三種選法（代表作交集／引用數／分組策展）裡明確選了分組策展。

三條定義：

1. **「篇」不限論文**：期刊論文、專書章節、專著都收，欄位 `type` 標 article／chapter／monograph。
   很多改變領域的東西是一本書（威爾豪森《導論》、桑德斯《保羅與巴勒斯坦猶太教》），硬排除就失真。
2. **取捨標準＝「改變了後人怎麼問問題」**，不是「寫得最好」也不是「最新」。一篇短文（Sandmel〈平行狂〉、
   Lewis〈我們說「雅麥尼亞」是什麼意思？〉）若終結了一個學界傳說，就該進。
3. **順序＝研究史順序**：每組內依主題（`theme`）分節，主題照研究史先後排，主題內照年份。
   主題名要能當小標題讀（「五經與底本學說」「三次歷史耶穌探索」），不要用抽象分類詞。

## 檔案在哪

```
data/research-data/<field>/top-papers.config.json   領域標題／說明／分組／相關連結
data/research-data/<field>/top*.jsonl               一組一檔（top500-ot.jsonl…），一行一筆
scripts/top_papers_build.py                          通用建置腳本（換領域不用改）
public/content/research-data/<field>/top-papers.json 產物（進版控，頁面直接讀）
pages/research-data/top-papers/[field].vue           通用頁面（換領域不用改）
output/top-papers/<field>-crossref.json              Crossref 快取（不進版控）
pages/research-data/index.vue                        要手動加一張卡
```

一筆的欄位：

```json
{"group":"ot","theme":"五經與底本學說","author":"Julius Wellhausen","author_zh":"威爾豪森","year":1878,
 "title":"Prolegomena zur Geschichte Israels","title_zh":"以色列史導論",
 "venue":"Berlin: Reimer（初版題 Geschichte Israels I）","type":"monograph","lang":"de",
 "note":"底本學說的定本：祭司典最晚、律法後於先知，此後一切五經研究都是對它的回應。"}
```

* `venue` 論文寫「期刊 卷: 頁碼」，專章寫「收於《書名》（編者），出版社，頁碼」，專著寫「城市: 出版社」；
  有英譯或後來單行本用「；英譯 …」接在後面。
* `note` 一句話，**說它為什麼重要**（改變了什麼），不是摘要內容。
* `author_zh` 譯名先查 [[translation-glossary]]；同姓者加括號（「布朗（R. E.）」「柯林斯」vs「亞布羅‧柯林斯」）。
* `lang` 是**原著語言**，不是我們拿到的版本語言。

## 怎麼開一個新領域

1. 跟使用者確認**分組**與**每組筆數**（聖經研究是四組各約 125）。分組是使用者定的，別自行合併。
2. 建 `data/research-data/<field>/top-papers.config.json`（照聖經研究那份改）。
3. 每組寫一個 `top*.jsonl`。**自己按研究史寫**，不要派 agent（[[feedback_save_claude_usage]]）；
   一組 125 筆大約是一次 Write。先想主題骨架（每組 8–15 個主題），再往主題裡填 6–20 筆。
4. `python -X utf8 scripts/top_papers_build.py <field>`——會印每檔筆數、Crossref 命中、館內命中；
   **每一個數字都要看**，「0」先疑迴圈沒跑到（[[feedback_silent_zero_is_a_bug]]）。
5. `pages/research-data/index.vue` 加一張卡（顏色要在 tailwind safelist：amber/blue/rose/emerald/violet/sky/indigo/cyan/orange/stone/purple/teal）。
6. commit：data／public/content／index.vue 三處，快取不進。

## Crossref 核對的意義與極限

`query.bibliographic` 帶「題名＋作者」查，題名相似度 ≥ 0.82 且年份差 ≤ 2 才算命中，命中補 DOI／刊名／卷頁。
**核不到不代表資料錯**：專著、1990 年代以前的德語論文、十九世紀以前的作品多半沒有 DOI。
聖經研究首例 536 筆的命中率見 build 輸出；頁面上「已核對」只是「有 DOI 可點」的意思。
🚨 Crossref 對常見題名（"Genesis"、"Paul"）會回同名他書，所以相似度門檻不能放低；
若要人工補核，優先補 `type: article` 而核不到的那些。

## 館內比對

沿用 `contemporary_theology_index.in_library`（題名關鍵詞命中之後還要作者對得上），兩種相反的壞法那邊有寫。
🚨 `holdings_inventory.py --find 作者姓` 的「站上書名」欄只比書名不比作者，拿它查作者會回假 0——查館藏走 DB。

## 首例現況（聖經研究，2026-09-26）

| 組 | 檔 | 筆數 | 主題數 |
|---|---|---|---|
| 舊約研究 | top500-ot.jsonl | 139 | 15 |
| 新約研究 | top500-nt.jsonl | 134 | 11 |
| 次經與典外文獻 | top500-apoc.jsonl | 128 | 9 |
| 聖經批判史 | top500-crit.jsonl | 135 | 8 |

合計 536（名為五百、實收五百餘，寧多勿缺）。與同日上架的 /collected-works「基督宗教研究」54 位學者 hub
（新約 15／舊約 13／次經與典外 12／教會史 14）互為表裡：hub 是人，這裡是文獻。

## 接手清單

* 使用者若說「某篇該進／不該進」：直接改 jsonl 那一行，重跑 build，不用重寫整組。
* 要加第五組：config 加一個 group、新開一個 jsonl 即可。
* 要換領域：從步驟 1 起，不要動腳本與頁面；若真的要改頁面，改的是通用版，所有領域一起變。

## 清單之後怎麼「拿到」（2026-09-26 實測）

使用者想在校內把五百篇一次下載——**走不通**，三條證據：Unpaywall 112 個 DOI 只有 4 筆 OA（其中兩筆是目次／前言）；
校內 IP 開 doi.org：劍橋顯示「Get access／purchase」（校方沒訂）、SAGE 與 OUP 對腳本直接 403、de Gruyter 回 202 驗證頁、JSTOR 也是 403。
華藝那條額度（1,200／日）對這批西文文獻無用。所以分兩路：

1. **專著**（type=monograph，本例 434 筆、扣館內與已在獵表者剩 384）→ `data/zlib-wanted/biblical-top500.jsonl`（key `bt-`、source 沿用 `biblical-studies` 吃它的優先序 20），
   `python scripts/zlib_wanted.py` 併入後由每日 z-lib 排程慢慢抓（[[ebook-zlib-harvest]]）。
2. **期刊論文與專章**（本例 102 筆、52 有 DOI）→ Drive `研究資料/<領域>/待下載_期刊論文與專章（校內圖書館用）.csv`，
   帶 DOI 連結與出處，給使用者在校用瀏覽器走圖書館下載；OA 的那幾筆腳本直接抓進同一夾。
🚨 不要對出版社網站寫自動下載：機構 IP 被擋是整校一起擋，和華藝那條的道理一樣。
