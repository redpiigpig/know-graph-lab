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

### 🚨 比對一定要過繁簡（2026-09-10）

我們的清單一律繁體（repo 硬規矩），**z-library 的中文藏書幾乎全是簡體**。閘門只比繁體
原字串的那段期間，等於把站上大半中文書判成不存在：

| 清單上寫的 | 站上實際有的 |
|---|---|
| 《心靈的黑夜》十字若望 | 心**灵**的黑夜　聖十字若望 |
| 《權力與無知》羅洛‧梅 | 罗洛·梅文集 **权力与无知**：寻求暴力的根源 |
| 《美的現實性》伽達默爾 | 美的**现实性** 作为游戏、象征、节日的艺术 |

`zlib_wanted.py` 的 `add_simplified()` 用 opencc 先備一份 `expect_s`／`who_s`（**只給比對
用，不進資料庫**），`rank()` 兩邊都比。同一組四十筆樣本，命中率 2.5% → 10%。

剩下的漏網多半是**書名／人名譯法不同**，繁簡救不了：涂爾幹《社會學方法的規則》站上叫
迪尔凯姆《社会学方法的准则》。要再往上拉就得接翻譯詞庫的 variants
（[[translation-glossary]]），還沒做。

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

## 每日額度：每帳號十本，四個帳號＝四十本

第 11 本開始，點下載鈕就是永遠等不到 download 事件，**站方不會明說**。所以：

* 帳本只把 `downloaded` / `not-found` / `no-usable-hit` / `probe-miss` 當「處理完」。
  `download-failed` **刻意不算**——那多半是額度用完，算成處理過的話那本書就此消失。
  🚨 這條寫在註解裡但程式沒照做，每天靜靜燒掉兩本，累計丟了 8 本，2026-09-10 才修好
  （改成連續失敗三次才放棄）。
* 連兩本下載失敗就收工，記一筆 `quota-exhausted`，換下一個帳號。

### 班表（2026-09-10 改）

使用者定調：一天三十本一年也下載不完，改四十本，**主帳號的額度也拿出來用**（被 ban 的
風險他認了）。`ZLIB_EMAIL` 沒有後綴＝主帳號，排程用 `--account 1` 指它——空字串穿不過
PowerShell → cmd → node。

* `KGL_ZLib_Daily` 一天三班 `09:30 / 14:30 / 20:30`，目標是**今天累計**四十本不是每輪
  四十本。每班先問 `zlib_today.py` 今天到幾本，湊滿就直接結束、一次搜尋都不花。
* `--max-tries` 跟著**命中率**走不是跟著下載目標走。預設六倍是「清單上的書多半存在」的
  假設，實測獵表只有一成，六倍會搜到第六本就收工、帳號另外四本額度原封不動。現在十五倍。
* 🚨 排程原本 `DisallowStartIfOnBatteries=True`——筆電沒插電整班不執行，通勤日等於停擺。
  已關掉，時限 2h → 4h。

### 🚨 一筆搜壞不可以帶走整輪

2026-09-10 實得只有 6 本，額度根本沒用完：搜「聖與俗」時 `page.goto` 回
`net::ERR_ABORTED`，`gotoPastWall` 沒接住，node 整個爆掉，**帳號 3、4 的二十本一次都
沒動用**，而排程結果碼只寫 `3221225786`（被中止），看不出是這個原因。現在：導覽失敗在
`gotoPastWall` 內部吞掉重試；整筆搜壞只跳過那一筆且**不寫帳本**（下輪再試）；連續五筆
才判定站況不對收工；頂層 `await main()` 也包了 catch。

## 🚨 清單是願望清單，不是庫存（2026-09-10）

使用者問獵表那 1,190 筆「是真的有在 z-lib 上查到嗎」。**沒有，從來沒查過。**獵表檔頭
自己就寫著「列出各全集作家尚未收錄的著作，供上 z-library 搜尋中譯本」——它是 7 月 23 日
從各作家的**著作目錄反推**出來的，不是查詢結果。

隨機抽四十筆（36 位作家）跑探勘，修好繁簡比對之後命中 **10%**。照這個比例，那 1,190 筆
實際大概拿得到一百二十本上下。各來源體質差很多，別把獵表的數字當成書的數字：

| 來源 | 實測命中率 | 為什麼 |
|---|---|---|
| `relstudy-course-hcu` | 91.7%（11/12） | 課程指定用書，真的存在的教科書 |
| `bib-*` 各研究書目 | 23.6%（35/148） | 從論文參考文獻抄的，近人西文專書多半沒中譯 |
| `collected-works-hunt` | 10%（4/40 抽樣） | 從著作目錄反推，連「有沒有出過中譯」都沒查 |

### 探勘（`--probe`）

只搜不下載——**不花下載額度，只花時間**。帳本裡有任何紀錄的一律跳過，所以每輪都在啃還
沒探過的那一段。命中記 `dry`（留在佇列等正式跑去抓），落空記 `probe-miss`（退出佇列）。
接在 `zlib_daily.ps1` 每輪四十本抓完之後，用備用帳號跑 120 筆，一天三班約 360 筆，兩週
左右把整份五千多筆過一遍。

🚨 `probe-miss` 是**規則判的，不是人看過的**。2026-09-10 當天就示範過規則會錯（繁簡那
一條，四十筆判掉三十九筆而其中至少三本站上有貨）。所以每筆都附 `rule` 版本
（目前 `v2-t2s`），比對再放寬時可以只撤那一批重探——別直接清整本帳本。

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

## 記憶庫併入：feedback_zlib_3x_daily_check

z-lib/ drop folder 的處理：

**⚠️ 自動排程 2026-05-27 已 Disabled（使用者要求關閉）**
- `KGLab-OCR-Daily-10` / `-14` / `-18` 三個 task 都 `Disable-ScheduledTask` 停用
- 定義仍在 Task Scheduler（State=Disabled），未刪除 — 將來想恢復可 `Enable-ScheduledTask`
- 不會再自動觸發 `scripts/run_ocr_daily.bat`

**Why:** 使用者 2026-05-27 「不需要了」。Gemini quota 經常用罄、Haiku 帳號級 burst limit 每天 ~5 本上限，daily 自動 OCR 多半 no-op 或浪費 retry。使用者偏好整本書手動 ingest+OCR 嚴格控制（搭配 [[feedback_ocr_strategy]] Haiku one-at-a-time）。

**仍適用：Claude 在對話中主動檢查 z-lib/ drop folder**
- 對話開始時，或被詢問「z-lib」「新書」「ingest」「下載」相關話題時
- 主動跑 `python scripts/ingest_new_books.py status`
- 若 status 顯示 >0 本待 ingest → 視情況問使用者要不要 ingest，或直接跑 `ingest_new_books.py run`（只入庫不 OCR，安全）

**How to apply:**
1. 任何 session 開頭涉及 ebook 工作流，先 `ingest_new_books.py status`
2. 看到 user mention 下載書 / z-lib / 新書 / 加書，立即偵測
3. **不要重新啟用** daily 排程，除非使用者明確要求

## 記憶庫併入：feedback_zlib_auto_dedup

當 `ingest_new_books.py` 偵測到 z-lib drop 的目標檔在 G:\我的雲端硬碟\資料\電子書\... 已存在時，**自動刪掉 z-lib/ 那份**（log 兩邊 size 後 unlink），不要保留要 user 手動清。

**Why:** 不刪會讓每 6 小時的 daily scheduler run 反覆掃同一批 dupes，浪費 Gemini classify quota 也讓 log 雜訊變多。User explicitly 2026-05-14 要求改成 auto-delete。

**How to apply:**
- code 已改在 `scripts/ingest_new_books.py:381` 附近（commit `609aca4`），新 session 不需要再改
- 若未來改 ingest 邏輯時不要把 auto-delete 拿掉
- 詳細記在 [[project_new_book_drop]]（ebook-pipeline SKILL Workflow D「Failure modes」「Target file already exists」段）

關聯：[[project_new_book_drop]]
