---
name: ebook-zlib-harvest
description: 從 z-library 依清單長期抓書的流程 —— 把「想要哪些書」寫成結構化清單（策展主題書單＋既有獵表），每日排程自動查詢、挑版本、下載到 repo 的 z-lib/ drop 夾，交既有的 ingest_new_books.py 分類上 Drive。含 DiamWall 過牆、挑版本的兩道閘（垃圾上傳與研究專書）、帳本與每日額度的處理。Use when 要加新的主題書單、補既有獵表、調整挑版本規則、debug 抓不到書或下載沒觸發、或使用者說「去 z-lib 查／下載某某書」。上游是 [[ebook-collected-works]] 的 REFERENCE-first（動手自譯前先查有沒有中譯本），下游是 [[ebook-pipeline]] 的 new-book drop。
---

# z-library 長期抓書

## 這條線在整個流程的哪裡

```
想要的書（清單）
   ├─ data/zlib-wanted/*.jsonl          人工策展的主題書單（進 git）
   ├─ …/z-library_獵表_全集中譯.txt      全集作家未收錄著作 1,193 筆
   └─ …/基督宗教研究_中譯獵表.txt         33 筆
              │  scripts/zlib_wanted.py（合併去重）
              ▼
   output/zlib_wanted_all.jsonl（中繼，不進版控）
              │  scripts/zlib_fetch.mjs（每日一輪，額度用完就停）
              ▼
   <repo>/z-lib/                        drop 夾（gitignored）
              │  scripts/ingest_new_books.py（每日 16:00 排程）
              ▼
   Drive 電子圖書館（分類、改名、入 DB）
```

排程：**KGL_ZLib_Daily，每日 09:30**（`scripts/zlib_daily.ps1`）。先更新清單再抓一輪。

## 清單格式

一行一本 JSONL：

```json
{"key":"bib-cross-canaanite","query":"Cross Canaanite Myth and Hebrew Epic",
 "expect":"Canaanite Myth","who":"Cross","source":"biblical-studies",
 "zh":"克羅斯《迦南神話與希伯來史詩》"}
```

* `key` 帳本的鍵，**必須穩定**。獵表那邊是 `sha1(作者|書名)[:10]`——一度用 Python 內建
  `hash()`，那東西每次執行結果都不一樣（PYTHONHASHSEED 隨機），等於每天重抓同一批書。
* `query` 丟給站方搜尋的字串。
* `expect` / `who` 是**挑版本的閘**（見下）。
* `source` 統計與排序用；`zh` 只是給人看的。

### 中譯還是原文？

REFERENCE-first 的預設是找中譯本（[[feedback_collected_works_reference_first]]），所以
獵表那兩份用中文書名＋作者搜。但**近代英文學術書多半沒有中譯**，用中譯名去搜只會落空
——小黑書那 25 本（user 2026-09-02 指示）與九份主題書單一律用原文書名＋作者姓。

## 兩道閘：挑到「對的那一本」

`zlib_fetch.rank()` 先擋掉兩類，剩下的才按繁體＞簡體＞英文、EPUB＞azw3＞PDF 排序：

1. **垃圾上傳**：站上有一批「書名就是別人的搜尋字串」的檔（多半 english/txt）。命中它們
   比沒命中更糟——會把一本假書送進 drop 夾，然後被 ingest 當成真書分類上架。
2. **對不上的研究專書**：搜韋伯《中國的宗教》會抓到孫中興《久等了，韋伯先生！》。所以
   `expect`（書名核心詞）與 `who`（作者姓）都要出現，否則直接判 -100。

`--dry-run` 會把被閘擋掉的也列出來（附分數），才看得出「是閘太嚴，還是站上真的沒有」。

## 站方那面牆（DiamWall）

| 症狀 | 原因 | 對策 |
|---|---|---|
| curl 拿到 513「Verifying your browser」 | JS challenge | playwright 開真 Chrome（`channel: 'chrome'`；本機沒下載 playwright 自己那份 chromium） |
| 連三次都卡在 challenge 頁 | **覆寫了 userAgent** | 不要設 `userAgent`——站方比對 UA 與指紋，自訂 UA 反而過不了 |
| 搜尋結果 0 筆 | URL 掛了 `extensions[]=EPUB&languages[]=Chinese` | 不要在 URL 過濾，全抓回來自己排序；站方對中文書的語言/格式標記很不完整 |
| 書名、作者抓成空字串 | 它們在 `<div slot="title">` 裡，不是 attribute | 年份／語言／格式才是 attribute，兩邊都讀 |
| 點了下載鈕永遠等不到 download 事件 | `a.dlButton` 在 DOM 裡先出現的是「Read Online」 | 選 `a.addDownloadedBook`（href=`/dl/…`） |

登入狀態存 `c:/tmp/zlib_state.json`，之後免登入。帳號在 `.env` 的
`ZLIB_EMAIL` / `ZLIB_PASSWORD`。

## 每日額度：實測十本

第 11 本開始，點下載鈕就是永遠等不到 download 事件，**站方不會明說**。所以：

* 帳本只把 `downloaded` / `not-found` / `no-usable-hit` 當「處理完」。
  `download-failed` **刻意不算**——那多半是額度用完，算成處理過的話那本書就此消失。
* 連兩本下載失敗就收工，記一筆 `quota-exhausted`，明天排程再來。
* `zlib_daily.ps1` 要 12 本（多要兩本讓它自己撞到牆停下來），實得 10。

照這個速度，1,444 筆大約五個月消化完。

## 現況（2026-09-02）

| 來源 | 筆數 |
|---|---|
| collected-works-hunt | 1,193 |
| christianity-studies-hunt | 33 |
| littleblackbook（英文原著） | 25 |
| biblical-studies | 22 |
| buddhist-studies | 22 |
| buddhist-textual-criticism | 22 |
| history-of-religions | 22 |
| religious-studies | 22 |
| buddhist-history | 21 |
| church-history | 21 |
| theological-method | 21 |
| buddhism-gender | 20 |
| **合計** | **1,444** |

**已下載 10 本**（舊約與福音書研究經典）：威爾豪森《以色列史導論》、貢克爾《創世記的
傳說》、馮拉德《舊約神學》、諾特《五經傳統史》、柴爾茲《作為聖經的舊約導論》、克羅斯
《迦南神話與希伯來史詩》、布魯格曼《舊約神學》、特里布爾《恐怖文本》、布特曼《符類福音
傳統史》、陶德《天國的比喻》。

## 小黑書（littleblackbook0000）

FB/IG 抓不到，改抓 WordPress：`/feed/?paged=1..3` 三頁湊齊 25 篇（sitemap.xml 也可，
但 feed 的標題就夠用）。標題格式固定：

```
小黑書Ep23 從文化人類學看新約 || 馬利納：新約世界：文化人類學的洞見
                                  └ 作者    └ 中譯書名
```

**一本 Ep = 一本聖經學術原著**。中譯書名只是導讀者的翻譯，站上搜不到，所以清單裡放的是
英文原著（`data/zlib-wanted/littleblackbook.jsonl`）。Ep4（馬爾赫比）與 Ep12（布里奇）
的原著書名我標了 `note: 英文原著書名待確認`，抓不到時先查那兩筆。

## 接手清單

1. 加新主題書單：在 `data/zlib-wanted/` 放一份 `.jsonl`，跑 `python scripts/zlib_wanted.py`
   合併即可，排程隔天就會開始抓。
2. 想看清單消化到哪：`node -e` 讀 `scripts/state/zlib_ledger.jsonl` 統計 status。
3. 抓不到某本書：先 `--dry-run` 看命中與分數，再決定是放寬 `expect` 還是改 `query`。
4. **還沒做**：libgen 那條（`小黑書_libgen下載清單.txt`，73 行）還是人工的；libgen.li
   要 PowerShell IWR 且別讓檔案落地（Defender），與這支的 playwright 路線不同
   （[[project_christianity_studies_littleblackbook]]）。
