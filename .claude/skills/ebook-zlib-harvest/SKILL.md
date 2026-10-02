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

## 🚨 z-library 不是唯一一條路

**十九世紀到二十世紀中葉的學術著作多半已進入公有領域**，掃描本就在公開典藏裡，
版次與畫質還比 z-lib 上的隨手上傳可靠。2026-09-11 實測了十八個站，十五個通得到，
其中十二個**完全不必帳號、curl 直接抓、可以排程**（archive.org／Gutenberg／Persée／
DBNL／Deutsches Textarchiv／MDZ／Runeberg／Zeno／Wikisource／DOAB／OAPEN／青空文庫）。

同一天的實例：奧托與涂爾幹共九本原著，**一本都沒動用 z-lib 額度**。

完整清單、各站的坑、要不要帳號、以及 archive.org 那三個會讓人誤判成功的陷阱，
見 [[ebook-collected-works]] 的 `free_text_sources.md`。

**動用 z-lib 額度之前先問一句：這本書的作者卒滿七十年了嗎？**是的話先去公開典藏找。

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

### 🚨「DiamWall 未過」不一定是 DiamWall（2026-09-19）

`gotoPastWall()` 回 false 有**兩種完全不同**的原因，而舊版上層一律丟同一句
「DiamWall 未過——這是站方擋住」：

* **wall**：真的被擋，標題一直是 challenge 頁 → 只能等站方放行、換帳號、或改天再跑。
* **net**：`page.goto` 一直丟例外（`ERR_NAME_NOT_RESOLVED`／`ERR_NETWORK_CHANGED`／
  timeout）→ 是**本機網路**，跟站方無關。筆電通勤時網路跳動就長這樣。

2026-09-18 四個帳號跑滿一整天、0 本落地，log 滿場「DiamWall 擋住」，看起來像站方封鎖；
實際上當天日誌裡夾著 `ERR_NAME_NOT_RESOLVED at https://z-library.sk/s`，而隔天實測
`z-library.sk` 解析得到（216.146.31.1）——網域好好的，是網路斷了。**認錯原因就會拿錯
對策**：以為要等站方放行，其實只要等網路回來。現在 `wallReason()` 會照實分辨。

判讀順序：看到 0 本先 `Resolve-DnsName z-library.sk` 驗網域，再看 log 裡有沒有
`↻ 導覽失敗` 那種行——有就是本機網路，沒有才是真的牆。

🚨 另外：**帳號 1 被擋不代表整站擋你。** 2026-09-19 帳號 1 連五筆被牆收手，換帳號 2
就過牆開始下載。所以別在第一個帳號失敗時就判定「今天不用跑了」。

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

### 🚨 `zlib_wanted_all.jsonl` 是「剩餘待辦」，不是全表（2026-09-16）

算進度時**不可以拿它的行數當分母**。`zlib_wanted.py` 產這個檔時就把帳本已處理的 key
扣掉了（刻意的，註解寫在 main() 裡：配額按清單位置發，已處理的還佔著位置會把後面
層級的名額吃光）。所以它每被重新生成一次就變短——這是設計，不是資料掉了。

拿它當分母的後果是**百分比雙重虛報**：分子（已處理）上升的同時分母（剩餘）下降。
`watch_pipelines.py` 一直這樣印，2026-09-16 實測印 `1,618/5,442 = 29.7%`，
真值是 `1,618/6,553 = 24.7%`。已修成：

```
全表 = 清單剩餘的 key ∪ 帳本已處理的 key（非 dry）
```

同一天也因此誤判過一次「清單從 6,173 縮到 5,442 是不是有來源靜默掉了」。
**查法**是跑 `python scripts/zlib_wanted.py --stats`——它只印不寫（不會覆寫正在被
`--probe` 讀的清單），會列出 33 個來源各自的筆數與合計，格式不對的檔會出聲跳過
（目前唯一一筆是 `mukyokai-zh-found.jsonl` 的 7 行，非獵書格式、已知）。

合計對得上「清單 − 已處理」就代表沒有來源掉，縮水純粹是扣掉已處理的。

2026-09-17 把 `translation_dashboard.py` 的「z-library 收書」分頁整塊拆掉，原因同上：
它也是拿 `zlib_wanted_all.jsonl` 的行數當分母（各來源印 0.4%／2.0% 那種數字），而且
面板每次開都要重讀整本帳本。收書進度一律看 `watch_pipelines.py` 第二節，或
`zlib_wanted.py --stats`；面板只留全集翻譯。

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

**聖經研究獵表 2026-09-26 對帳**（67 筆＝舊約 11／新約 11／典外 12／批判史 10）：downloaded 26＋already-owned 11＝37 有書、
probe-miss 19、dry 11。🚨 `holdings_inventory.py --find` 的「站上電子圖書館書名」只比書名不比作者，
拿作者姓去查會回 0 筆——這 37 本其實都已在 ebooks 表且 parsed，要查請直接打 DB 的 author 欄。
兩個壞命中：`bs-hc-astruc-conjectures` 抓到的是 John Jarick 編的論文集 *Sacred Conjectures*（談 Astruc 的書，不是 Astruc 原著）；
`bs-nt-hengel-judaism` z-lib 作者欄拼成 "Martin Hegel"，DB 已改回 Hengel。批判史那組原著仍應走 archive.org。

**已下載 10 本**（舊約與福音書研究經典，2026-09-02 當時）：威爾豪森《以色列史導論》、貢克爾《創世記的
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
5. **研究史料專線**：`ingest_new_books.py` 的 `RESEARCH_ROUTES` 按檔名前綴把史料直接搬到 Drive `研究資料/…`，不進電子圖書館。
   兩蔣日記走國史館官方：
   蔣中正手稿影像官方開放下載（需會員登入），蔣經國影像標「禁止翻拍複製」不下載，只收目錄節錄（`scripts/chiang_diary_catalog.py`）。

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

## 🚨 手動補抓單本（2026-10-01《神的演化》）

- `node scripts/zlib_fetch.mjs --list <一本的清單> --limit 1 --account 3`：**手動跑要指定 `--account`**，
  不指定就一直用主帳號；排程（`zlib_daily.ps1`）才會自動輪帳號。主帳號額度用完時的長相就是
  「點了下載鈕等不到 download 事件」，看起來像檔案太大。
- 同一本 `download-failed` 累積 3 次就被 `doneKeys()` 永久放棄——額度用完造成的失敗也算。
  手動換帳號前先把帳本裡該 key 的 `download-failed` 行刪掉。
- 百 MB 級掃描本可用 `ZLIB_DL_TIMEOUT_MS=180000` 拉長等待（預設 60 秒）。

## z-lib 找不到時：LibGen 與 Anna's Archive（2026-10-01）

- **LibGen** `libgen.li`：`index.php?req=…&topics[]=l` 查 → `edition.php?id=` → `ads.php?md5=` → `get.php?md5=&key=` 直接下載，
  純 urllib 即可；常回 HTTP 500，重試幾輪就過。下載前核對：LibGen 的同作者另一本書會排在前面（邢福增那次就抓錯書）。
- **Anna's Archive**：`.li` 網域已被停放出售，現用 `annas-archive.gl`；前面有 DDOS-GUARD，curl 403、自動化 Chrome 也要
  **人工點一次驗證**。`scripts/annas_search.mjs --file q.txt --out hits.json` 用持久 profile `c:/tmp/annas_profile`，卡驗證時
  會等最多 10 分鐘並印「等待人工驗證」，且約 30 筆後會再跳一次。🚨 結果列的書名連結是 `a.js-vim-focus`；頁面另有一排
  「最近下載」也是 `/md5/` 連結——抓錯會每筆都回剛好 12 筆無關的書。
- **獵表改走 LibGen 直接抓**：`scripts/libgen_wanted.py --sources a,b --apply`（不加 `--apply` 只查不下）。對得上
  （expect 是書名子字串＋作者姓吻合）就下載進 z-lib/ 並在帳本記 `status: downloaded, pick.via: libgen`，z-lib 排程即跳過。
  同一份清單可再開一支 `--reverse` 從尾端倒著跑、會合時自停。10-01 首輪：cw30 中譯本 22/109、三套全集 11/107、
  代表作約 41/153、譜系學命中率最高（前 46 筆對上 35）。🚨 要 `python -u` 否則紀錄檔一直是空的（輸出被緩衝）。
- 🚨 **LibGen 會半途切斷連線、留下「檔頭正確的殘檔」**（10-02：566 本裡 54 本只下到 9／11／13 MB，入庫時被隔離；
  另 17 本被 PyMuPDF 修復後打得開、**已入庫上 Drive** 才查出來）。`libgen_wanted.check_complete()` 現在核對
  Content-Length、PDF 要開得起來；`--retry-corrupt` 照帳本的 edition 重抓 `_corrupt/` 裡的殘檔。
  稽核已入庫的：看 PDF 結尾 4KB 有沒有 `%%EOF`，大小剛好是整數 MB 的幾乎都是殘檔。

## 從專書書目批次產生抓書單（2026-10-02《神的歷史》《神的演化》《造神》）

三本書的引用書目 → 抓書單 → 公開典藏／LibGen → drop 夾。腳本 `scripts/god_books_{extract,merge,archive,report}.py`，
中繼在 `output/god_books/`，抓書單 `data/zlib-wanted/god-books-bibliography.jsonl`（source=`god-books-bibliography`，
key=`godbib-`＋sha1(作者|書名)[:10]`），盤點 md 在 Drive `研究資料\神觀史與宗教起源\既有資料盤點.md`。

流程：`extract`（造神＝書末 Chicago 體書目規則解析；神的歷史＝英文原著 PDF 尾註交 LLM；神的演化＝正文）→
`merge`（去重、對 ebooks 表、產獵表）→ 出版年 ≤1930 先 `archive`（archive.org，免額度）→
`libgen_wanted.py --sources god-books-bibliography --apply`（可加一支 `--reverse` 對跑）→ `merge` 再跑一次（吸收 archive 結果）→ `report`。

踩到的坑：
- 🚨 **「館內有這本書」不等於「館內有它的註釋與書目」。** 《神的演化》館內中譯本（DuXiu 掃描）只到「鳴謝」，書末「Note」頁
  無正文，`c:/tmp/evo` 的 OCR 也到不了——書目只能退而求其次從正文抽被提到的書，**不是完整書目**，要補得取得英文原著的 Notes／Bibliography。
  《神的歷史》館內中文版是大陸簡體排版、尾頁是出版社郵購廣告，同樣沒有註釋；書目改從館內英文原著 PDF 尾註抽。
- 🚨 LLM 抽「書」會自己編中文書名（`zh` 欄）與把無作者的經典當書（Philo、Bhagavad Gita），`zh` 只當提示、不拿去比對或搜尋；
  merge 時濾掉作者＝書名、書名 <8 字、聖經譯本、古典原典。
- 館藏比對只比書名會把 Köhler／Preuss 兩本同名《Old Testament Theology》、Sampson《Writing Systems》對到別人的書：
  **書名主體相符還要作者姓也在館內作者欄或書名裡**；只有館內書的 `original_title` 命中且主體 ≥12 字才免作者（中譯本作者欄是中文）。
- Chicago 體書目解析：作者段的句點要跳過「名字縮寫（單一大寫字母）」；`Md.`／`D.C.` 這種出版地縮寫含句點，
  切書名不能用「第一個含冒號的句子」，改取第一個句末、並以最後一段的年份判斷是書。正則字串裡的 `\b` 在非 raw 字串會變成退格字元（靜默失敗，全數判成「解析失敗」）。
- archive.org 驗 OCR 取樣用 `Range: bytes=200000-500000`（小檔會回 416，要退回不帶 Range）；整本 DjVuTXT 抓下來驗會卡好幾分鐘。
  大檔下載在 libgen 多支並跑時只有 ~100KB/s，一本百 MB 的 PDF 要十幾分鐘，整份獵表要排幾小時。
- 抓書單照 `lang: orig` 只出原文一格；沒有為每本再出「中譯」一格（中譯書名不知道、純作者閘會抓到垃圾，見 zlib_wanted_from_bibliography.py 的警告）。
