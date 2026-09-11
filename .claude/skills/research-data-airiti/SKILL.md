---
name: research-data-airiti
description: 從華藝線上圖書館（Airiti Library）收宗教類期刊的「篇目索引 →（授權內）全文下載」流程 —— 教會刊物與神學院學報（校園／新使者／曠野／神學與教會／台灣神學論刊／華神期刊／道風／建道／神學論集…）、佛學學報（中華佛學學報／法鼓／臺大佛學研究／佛光／玄奘佛學研究／法印／華嚴…）、宗教學期刊（臺灣宗教研究／輔仁宗教研究／宗教哲學／華人宗教研究…）。這些刊自家網站多半只有內文或只有近幾年，華藝反而整份收著且帶**卷期、起訖頁、正式作者署名**——做註腳非有不可的三個欄位。Use when 要新增一份華藝期刊、補抓某刊篇目、下載某刊全文 PDF、debug 抓不到卷期或下載回傳不是 PDF、或使用者提到「華藝」「airiti」「校園雙月刊」「篇目」「卷期頁碼」。刊物本位那一層的頁面規矩見 [[research-data-christianity]] 與 [[works-corpus-layer]]。
---


> ⚙️ 所有中文一律繁體（[[feedback_traditional_chinese_only]]）。

# 華藝期刊：篇目索引與全文下載

> 🚨 **`G:` 不見了＝Drive 卡住，不是掛掉。** Drive 路徑報找不到檔案時，先
> `Test-Path 'G:\我的雲端硬碟'`；False 就結束 `GoogleDriveFS` 再跑
> `"C:\Program Files\Google\Drive File Stream\launch.bat"`，約 20 秒掛回來，
> 未上傳的檔不會掉。程序在跑不等於磁碟在（全文見 CLAUDE.md）。


腳本：`scripts/press_airiti.py`（純 requests + BeautifulSoup，**不需要瀏覽器**）。
頁面：`/research-data/press`（列表）、`/research-data/press/<slug>`（單刊篇目）。
資料：`public/content/research-data/press/`（進 git）；PDF 全文進 Drive
`G:\我的雲端硬碟\資料\知識圖工作室\研究資料\華藝期刊全文\<刊名>\<卷期>\<篇名>.pdf`。

```
python -X utf8 scripts/press_airiti.py --discover        # 刊物普查
python -X utf8 scripts/press_airiti.py --toc campus      # 單刊篇目
python -X utf8 scripts/press_airiti.py --toc all         # 全部（很久，過夜跑）
python -X utf8 scripts/press_airiti.py --summarize       # 列表頁用的小索引
python -X utf8 scripts/press_airiti.py --download campus --limit 300
python -X utf8 scripts/press_airiti.py --batch 25          # 排程用：整批共 25 篇
```

## 排程：探到機構身分才下

單一排程 `KGL_Airiti_Poll` → `powershell -File scripts/run_airiti_batch.ps1 -Batch 100 -DailyCap 500`，
**每日** 08:00 起每 30 分鐘一次、持續 12 小時。log 在 `c:\tmp\airiti_download.log`。
（`run_airiti_batch.bat` 留著給手動跑用，排程不要指它——原因見下。）

🚨 **排程不可以讓 python 跟別人共用主控台。**
2026-09-07 實測：排程那幾輪跑約一分鐘就以一個 `^C` 收場，每輪只下 2–3 篇，
額度整天卡在 338。而工作排程器回報「成功完成」、log 裡也只多一個 `^C`——
看起來完全像正常結束。排除掉 Fleet Keeper（它只殺自己 `scripts/state/fleet_*.pid`
裡登記的 worker，當天一次都沒動手）與工作排程器本身之後，剩下的差別是**主控台**：
出事的是 `cmd.exe → python.exe`（有 console），而同樣每半小時跑、從不出事的
`KGL_Translation_Supervisor` 用 `pythonw.exe`（無 console）。`CTRL_C_EVENT` 會送給
同一個 console 上的**所有**行程，所以共用就可能被別人的 Ctrl+C 順手帶走。
`run_airiti_batch.ps1` 比照 `fleet_keeper.ps1`，用 `Start-Process -WindowStyle Hidden`
讓 python 拿到自己的隱藏主控台。修好後 `LastTaskResult` 從 `0xC000013A` 變成 `0`。

🚨 **那支 .ps1 必須是純 ASCII。** PowerShell 5.1 一遇到含中文的 .ps1 就解析崩，
`param()` 不被認得，錯誤訊息是 `The assignment expression is not valid`，
而且**行號對不上檔案**（誤導成別的地方壞掉）。中文說明寫在這份 SKILL 裡，
腳本裡只留英文。同一個坑 `fleet_keeper.ps1` 也踩過（[[project_fleet_keeper]]）。

🚨 **把 python 的輸出併回 log 時要指定 `-Encoding UTF8` 讀。**
python 寫的是 UTF-8，而 `Get-Content` 不指定編碼會用 ANSI（這裡是 Big5）讀，
再以 UTF-8 寫出去就壓壞兩次；而腳本照樣 exit 0、log 照樣有內容，只是讀不懂。

🚨🚨 **`DisallowStartIfOnBatteries` 一定要關掉——這是這個排程最要命的一條。**
工作排程器的預設是「使用電池時不啟動」。而本任務唯一有用的時機是**人在學校**，
那時筆電正在用電池，於是排程在該開火的時候一律不啟動；回到家插上電才會跑，
但那時 IP 不是校內網段、驗不過機構身分。**兩邊永遠錯開，等於這個排程從設計上
就沒辦法完成它的工作。** 2026-09-07 發現時 `NumberOfMissedRuns` 已經 4，
在此之前每一篇下載其實都是手動跑出來的。
症狀完全無聲：`State` Ready、`LastTaskResult` 0、log 裡連一行標頭都不會多
（bat 是無條件先 echo 標頭的，所以**該有標頭而沒有＝任務根本沒啟動**，
與「啟動了但驗不過機構身分」分得開——後者會留下一行紅字）。

```powershell
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
     -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
Set-ScheduledTask -TaskName 'KGL_Airiti_Poll' -Settings $s
```

`ExecutionTimeLimit` 也要跟著批次大小走：100 篇 × 每篇約 18 秒（6 秒節流＋下載）
約 30 分鐘，預設的 PT1H 勉強夠，拉到 PT2H 才有餘裕。

🚨 **觸發器一定要是 Daily（`MSFT_TaskDailyTrigger`），不能是 Once＋重複。**
2026-09-06 建的那次用的是一次性觸發（`StartBoundary 2026-09-06T08:00`、每 30 分、
持續 12 小時），當天 20:00 重複期間用盡之後就**再也不會觸發**——而工作管理員裡
`State` 是 Ready、`LastTaskResult` 是 0、工作好端端地在那裡，唯一的徵兆是
`NextRunTime` 空白。隔天完全靜悄悄，看起來像「人沒到學校所以沒下載」。
檢查方式：

```powershell
(Get-ScheduledTaskInfo -TaskName 'KGL_Airiti_Poll').NextRunTime   # 空白＝已死
(Get-ScheduledTask     -TaskName 'KGL_Airiti_Poll').Triggers[0].CimClass.CimClassName
```

重建（`New-ScheduledTaskTrigger -Daily` 不吃 `-RepetitionInterval`，要借一個
`-Once` 觸發器的 `.Repetition` 貼過去）：

```powershell
$d = New-ScheduledTaskTrigger -Daily -At 8:00am
$d.Repetition = (New-ScheduledTaskTrigger -Once -At 8:00am `
    -RepetitionInterval (New-TimeSpan -Minutes 30) `
    -RepetitionDuration (New-TimeSpan -Hours 12)).Repetition
Set-ScheduledTask -TaskName 'KGL_Airiti_Poll' -Trigger $d
```

為什麼是高頻輪詢而不是固定四個時段：**下載只有在人到學校時才可能成功**
（機構 IP 綁玄奘校內網段）。固定時段的問題是機器那時可能睡著或人不在，
而 `-StartWhenAvailable` 補跑會擠到半夜，等於整個時段的額度就沒了
（2026-09-05 實測：09:30 與 11:30 一起在 11:50 開火，16:30 那批補到 23:14）。
改成每半小時探一次：人不在學校，腳本驗完機構身分就收手（一個請求），
人一到學校就開始下。**高頻不等於高流量**。

一天的總量由 `--daily-cap` 守住，不是由排程次數守住
（帳在 `c:\tmp\press_airiti_daily.json`，跨日自動歸零）。
🚨 沒有這個上限的話，高頻排程等於把節流拆掉——一天會跑出十幾批。

要改速率就改排程的兩個引數，不必動腳本。**能動的是每日總量，不是 `DELAY_DL`**——
6 秒那個是不被停權的底線（2026-09-07 使用者定調每日 500）。

額度是**逐篇記帳**的（`download()` 每寫成功一篇就 `add_spent(1)`）。
🚨 這裡曾經是在 `batch()` 收尾才記一次，於是中途被 Ctrl+C 或被排程砍掉的那一輪，
檔案明明下到了卻一篇都不計，下一輪再開又從 0 算起——當天實際總量會悄悄超過上限，
而 log 與帳本看起來都正常（2026-09-06 15:30 那輪的 log 尾巴只有一個 `^C`）。
已於 `a6a573da` 修掉。**兩邊都記會重複計**，症狀是「明明還沒下滿就說達到上限」，
所以收尾那一次要拿掉，不是兩邊都留。

### 書目點名的那些篇要排在最前面

`airiti_wanted_from_bibliography.py`（另一支）把寫作計畫的書目對到**刊**；
`press_airiti.py --resolve-wanted` 再把篇名對到 **docID**，寫成
`public/content/research-data/press/airiti-wanted.json`。`--batch` 每次跑之前
會自動重算一次（純讀本機檔、不打網路），所以新抓好的篇目會讓原本
「篇目還沒抓」的條目自己補進佇列。全部 17,090 篇要跑幾個月，
論文當下要引的那些排在後面就等於沒下。

篇名比對只去標點、全半形與**明列的**正繁異體，**不做繁簡轉換也不去虛詞**——
那會把不同的兩篇折成同一篇，而症狀是「下載到的不是我要的那篇」。破折號要涵蓋
六種寫法（—— ― ─ – － ‐），中點還有 `‧`(U+2027)／`•`(U+2022)／`・`(U+30FB) 三種
（「保羅‧尼特」書目與華藝各用一種），少一種就會有篇對不上。

異體字走 `_VARIANTS` 這張**短字表**（目前只有 臺→台、衆→眾），不是通用轉換：
2026-09-07 實測光是這兩組就讓 6 篇對上（現代臺灣佛教×2、論「解嚴」前臺灣、
戰後臺灣佛教、衆生平等、保羅•尼特）。要加字之前先問：**有沒有可能兩篇文章
只差這一個字而確實是不同的文章**（緣起／源起 就是反例，不可加）。
`scripts/tests/test_press_airiti.py` 兩個方向都在擋，還有一條盯著字表長度。

🚨 **剩下對不上的，多半該改的是書目不是比對器。**
「凡塵的美麗彩虹」少了開頭的「落在」、「敲邊鼓〉」少了結尾的「讀後感」、
「104 年」寫成阿拉伯數字而華藝是「一Ｏ四年」——把比對放寬到能吃下這些，
等於把書目裡的錯誤藏起來，而那些錯誤會原樣印進論文註腳。
`scripts/press_airiti_unresolved.py` 會把最接近的候選連卷期頁碼一起印出來，
拿它去改書目來源才是對的修法。

只收點名幾篇、不整份掃的刊要寫進 `WANTED_ONLY`（目前只有《民俗曲藝》）。
「刻意不整份收」與「忘了加進 PRIORITY」在行為上一模一樣——都掃不到也都不報錯，
寫明才分得出來。

`--batch N` 與 `--download <slug> --limit N` 的差別：前者是**整批總共 N 篇**、
跨刊依 `PRIORITY` 順序取用；後者是**每一刊各 N 篇**。排程要控的是每天對華藝
發出多少下載請求，所以排程一律走 `--batch`。

`--batch` 會上鎖（`c:\tmp\press_airiti_download.lock`，三小時後視為過期）。
🚨 這個鎖不是可有可無的：實測發生過兩個 session 同時在下載，那等於把對機構 IP
的請求速率乘二，而節流的整個意義就在速率。

**體量（2026-09-04 實測）**：29 個刊號共 17,426 篇目、其中 17,090 篇有電子全文，
以每篇約 2.4 MB 計約 40 GB。**分母是「人在學校的日子」不是日曆天**——
一天 500 篇要 34 個到校日，一天 200 篇要 85 個。改速率就是改排程的引數，不必動腳本。

精確篇數怎麼查（一刊一次請求，不必等 `--toc` 跑完）：
`POST /Article/Query`，`DSF.SearchFileds=[{FieldName:51, SearchKeyWord:<pid>}]`，
加 `DSF.SearchScope = 1` 就只算有電子全文的那些；結果數在
`<div class="resultReport">2,393 個查詢結果</div>`。

## 為什麼要收這一層

《校園》《新使者》這類刊物的內文，站內原本就有一部分（新使者走「焚而不燬」信仰資源網）。
華藝補的不是內文，是**卷期、頁碼、正式作者署名**。論文註腳要寫
「〈某篇〉，《校園》68 卷 2 期（2026 年 4 月），頁 12–17」，缺一個都寫不成。
所以 `data/press.ts` 裡同一份刊會同時有 `to`（站內全文）與 `airiti: true`（華藝篇目），
兩個連結並存，**不是二選一**。

## 站台結構（2026-09 實測）

全部 server-render，`requests` 就夠：

| 要什麼 | 怎麼拿 |
|---|---|
| 刊物清單 | POST `/Publication/Query?queryString=<urlencoded JSON>`，`PSF.SearchFileds` 用欄位碼 6（細分類主題）＝ `A00-A03*` |
| 卷期清單 | GET `/Publication/Information?publicationID=<pid>&type=期刊&tabName=2` → `<option value="<issueID>">68卷2期 (2026/04)</option>` |
| 單期篇目 | 同網址加 `&issueYear=<年>&issueID=<issueID>&page=<N>&publisherID=<pubid>`，每頁 10 筆 |
| 全文下載 | 兩段（見下） |

欄位碼查得到的地方：`/_Layout_js?v=…` 那支 bundle 裡有 `全域_OpPubSearchFiled`、
`全域_OpDocSearchFiled`、`全域_OpPubType`、`全域_OpLogic` 四張表，是純 JS 的
`名稱 = 數字` 對照。要加新的查詢條件就去那裡查，不要用猜的。

學科分類碼：人文學＝`A00`，其下宗教學＝`A00-A03.00.00`（查詢時寫 `A00-A03*`）。
單刊的分類碼在該刊資訊頁的 `a.資訊頁_第二層學科分類[key]`。

### 下載的兩段

```
POST /Article/TextDownloadWindowNew
     header AjaxRequestVerificationToken = 卷期頁上該篇 Common_點擊全文下載(...) 的第 4 個引數
     body   jsString=<urlencode(JSON{文章代碼,文章篇名,需扣除點數,文獻類型代碼,ActionName,OrderID})>
  → HTML 片段，裡面有新的 ajaxRequestVerificationToken_DownloadWindow 與 lan_下載編號

POST /Article/TextDownloadNew
     header AjaxRequestVerificationToken = 上一步的新 token
     body   docID=<文章代碼>&token=&key=<下載編號>
  → PDF bytes
```

`token=` 留空是對的：那一格放的是 reCAPTCHA 回應，而機構 IP 認證通過時
下載視窗會回 `lan_是否跳過reCAPTCHA檢查 = 'true'`，伺服器就不驗。

## 🚨 陷阱

**1. 下載額度綁的是機構 IP，不是帳號。**
本機被華藝認成玄奘大學（頁面右上角會寫「您好！玄奘大學 IP:…」）。跑得快＝
拿全校的訂閱在衝，而華藝對異常流量的處置是**停整個機構**。所以
`DELAY_DL = 6.0`、`DL_CAP = 300`，**不要往下調**。動手前先確認使用者知道這件事。

**2. HTTP 200 不等於拿到 PDF。**
權限沒過的時候回的是 JSON 錯誤訊息，狀態碼一樣 200。每一筆都驗 `%PDF` 開頭
（`fetch_pdf` 已經做了），驗到「取不到下載編號」就整批停——那是 IP 認證掉了，
繼續跑只會把失敗寫滿帳本。這一條屬於
[[feedback_reader_silent_failures]] 說的「看起來像成功的失敗」。

**3. 卷期頁一頁只有 10 筆，下載鈕長在該頁上。**
`fetch_pdf` 是從卷期頁的 HTML 裡撈那篇自己的 token，所以只抓第一頁的話，
一期裡第 11 篇之後全部會被判成「此篇在卷期頁上沒有全文下載鈕」——
校園 68卷2期剛好成功 10 篇、後面全掛就是這個。看起來像「這些篇沒授權」，
其實是分頁沒翻。用 `issue_html_all()` 把整期各頁串起來再找。
（舊版寫著「這篇不在第一頁，讓 fetch_pdf 自己重抓」，但那支也只抓第一頁，
重抓等於再失敗一次。）

**4. 認證掉了要在批次開頭就擋住，不是等每一份刊各失敗一篇。**
`--batch` 開頭先跑 `institution(s)`：認得就印機構名，認不得就整批跳過、不動帳本。
沒有這道閘的話，2026-09-05 那一輪的下場是每份刊各失敗一篇、log 裡 18 行一模一樣的
紅字，而真正的原因（人不在學校、對外 IP 是 HiNet 而非 210.60.61.x）一個字都沒寫出來。
🚨 `institution()` 的正規表示式要拿**當初認證通過時的存檔**驗過才算數：
認不得的時候同一個 `span.unitEntranceName` 寫的是「透過您的圖書館登入」，
直接回傳就會永遠是真值，這道閘等於沒有。測試兩個方向都驗。

**5. 鎖要記 PID，只看時間戳會被自己的殘骸擋住。**
排程那一輪被砍掉時（工作結果 `0xC000013A`）`finally` 跑不到，鎖留在原地，
後面三小時的批次全部被擋——而且擋掉時只印一行「另一輪還在跑」，看起來完全正常。
`lock_holder()` 改成記 PID，行程不在就直接清掉。

**6. 固定時段的排程對這件事是錯的工具（已改掉，別改回去）。**
`-StartWhenAvailable` 讓錯過的時段在機器醒來時補跑，於是 09:30 與 11:30 兩個
一起在 11:50 開火（鎖擋掉後到的那個＝整個時段的額度沒了），16:30 那批補到 23:14。
而下載本來就只有人到學校時才可能成功，固定時段等於在賭那幾個時刻剛好對上。
現在是每半小時探一次、認得機構身分才下、一天總量由 `--daily-cap` 守住。

**7. 寫檔到 G: 會偶發 OSError 22。**
目的地是 Google Drive 的虛擬磁碟，偶爾回 `Invalid argument`，過幾秒重寫同一個檔
就好——不是檔名的問題（實測 60 字元的純中文檔名照樣中）。`write_with_retry()`
retry 四次；沒有這層保護的話，一次打嗝會把整批 300 篇的迴圈整個帶走。

**8. 華藝的收錄起始 ≠ 創刊年。**
《校園》1957 年創刊，華藝從 2005 年的 47 卷 1 期收起。混為一談就會在論文裡
把「資料庫沒有」寫成「那些年沒出刊」。`data/press.ts` 因此把 `start`（創刊）
與 `coverage`（收錄斷限）分成兩個欄位，`test/press-airiti.spec.ts` 有一條在擋。

**9. 同一份刊會被拆成兩筆。**
刊名一改，華藝就另立 PublicationID：《中華佛學學報》舊名（至 26 期／2013）與
現名 Journal of Chinese Buddhist Studies（27 期起）是兩筆；《臺大佛學研究》與
《佛學研究中心學報》也是。要看完整年表兩筆都得抓，所以 `JOURNALS` 裡都收了。

**10. 卷期標籤格式各刊不一，不要自己排序。**
「68卷2期」「26期」「新12卷2期」「46卷2期&47卷1期」都有。`--toc` 照華藝原序
（新 → 舊）保留，前端也照原序渲染。自己 parse 數字重排一定排錯。

**11. slug 打錯不會爆。**
`data/press.ts` 的 slug 與 `press_airiti.py` 的 `JOURNALS` 鍵必須一致，
否則 `/research-data/press/<slug>` 只會渲染一個「尚未收錄篇目」的空頁——
完全正常的畫面、完全錯誤的結果。`test/press-airiti.spec.ts` 把兩邊名單對起來擋這個。

## 華藝上有／沒有的

`--discover` 的輸出在 `public/content/research-data/press/airiti-journals.json`，
記了每一筆是靠學科分類找到的還是靠刊名探測補到的（`found_by`）。
2026-09 的普查：宗教學學科底下 **68 種**，刊名探測再補 9 種（多半是慈濟系統的
校院學報，與本論文無關）。

**學科分類掃不到、要按刊名另外找的**：華藝的學科分類是單一歸屬，跨領域的刊只會落在
一個類底下。《民俗曲藝》（pid `10251383`，施合鄭民俗文化基金會）被歸在**民俗類不是宗教學**，
所以 `--discover` 的 68 種裡沒有它——但它是一貫道、鸞堂、扶乩、先天道、齋教這幾條線
最主要的發表園地（收錄的 479 篇裡有 16 篇是這個題目，含鍾雲鶯談國民政府查禁一貫道那篇）。
按刊名查的作法：

```python
rows = parse_publications(pub_query(
    s, [{"FieldName": F_PUB_NAME, "SearchKeyWord": "民俗曲藝",
         "FieldQuery": True, "FieldLogic": 0}]))
```

`--discover` 的 `found_by` 欄位就是給這種情形用的。日後要找某個題目的刊，
先想「華藝會把它歸在哪一類」，不要只信宗教學那一類的名單。

**確認不在華藝**（以刊名查過，命中 0）：《使者》（1963–1990，《新使者》前身）、
《宇宙光》、《台灣教會公報》、《基督教論壇報》、《香光莊嚴》、《普門學報》、
《圓光佛學學報》、《正觀》、《福嚴會訊》、《海潮音》、《菩提樹》、《獅子吼》、
《人生》。前四份另有站內來源或另有取源計畫；後面那一批佛教老雜誌仍是
`data/press.ts` 裡 `tier: 'index'` 而尚無取源的狀態。

《使者》另有一份同名刊物是美國「基督使者協會」（AFC）發行的，**不同刊**，
書目上不要併成一筆。

### 站內已有全文的，不要再向華藝要一次

`SITE_HELD` 登記哪些刊（或哪些期）站內已經從別的來源抓齊了，整刊掃描會跳過，
**但篇目照抓、書目點名的單篇也照下**——華藝的卷期頁碼是站內那些來源沒有的。

| slug | 站內來源 | 站內有 | 華藝仍要下的 |
|---|---|---|---|
| `hcu-buddhist` 玄奘佛學研究 | 玄奘校網（[[research-data-hongshi]]） | 1–45 期全份 304 篇 | 0 篇（全重複） |
| `hongshi` 弘誓雙月刊 | 弘誓官網 | 80–200 期（缺 85、177–180），整期 PDF | 2–79 期＋缺的 5 期＋201 期，共 82 期 |

🚨 判準是**站內有沒有全文**，不是「站內有沒有這份刊」。弘誓站內有 116 期，
但華藝從第 2 期收起，前 78 期站內完全沒有——整刊跳過就會漏掉那一段。
所以 `SITE_HELD` 的值可以是 `"all"`，也可以是一組期號。

## 華藝之外：臺大佛學數位圖書館（開放取用，2026-09-06 實測）

華藝完全沒有的那批佛教老雜誌，臺大佛圖有，而且**不需要機構認證**。

🚨 **它的檢索是 Solr，直接打就好，不要去爬 JSP。** 網頁 `search/default.jsp`
的結果是 JS 填的：純 HTTP 抓回來的 HTML 裡永遠是 `<span id="Doct">0</span>`
（`display:none` 的樣板），看起來就像「查無資料」。真正的資料在：

```
GET https://dlbs.liberal.ntu.edu.tw/solr/mit/select
    ?q=SOURCETOPIC:"海潮音" AND BFULLTEXT:1&wt=json&rows=50&start=0
```

欄位：`TOPIC` 篇名／`AUTHOR`／`SOURCETOPIC` 刊名（值長這樣「菩提樹=Bodhedrum」）／
`ARCHIVE` 卷期／`PAGE` 起訖頁／`PRESSTIME` 出版日／`BFULLTEXT` 0|1／`FULLTEXTPATH`。

實測筆數（篇目 / 其中有全文）：
海潮音 26,220/1,141、人生 8,581/1,074、菩提樹 3,215/2,529、香光莊嚴 2,845/2,806、
弘誓 1,949/1,909、獅子吼 1,557/**4**、普門學報 1,287/564、福嚴會訊 708/692、
正觀 395/391、諦觀 388/**0**、圓光佛學學報 281/273、中華佛學學報 438/435。

🚨 三個坑：
1. `FULLTEXTPATH` **有時絕對（`http://buddhism.lib.ntu.edu.tw/FULLTEXT/…`）
   有時相對（`/FULLTEXT/…`）**，兩種都要處理。
2. **舊雜誌的 PDF 是掃描版、沒有文字層**（1953 年《菩提樹》那篇：3 頁 1.9 MB，
   `get_text()` 回空字串）。近年的學報才是原生數位（2008《中華佛學學報》32 頁 8 萬字）。
   所以「有全文」不等於「可全文檢索」，要 OCR 的那一批得另外算成本。
3. 有些 `FULLTEXTPATH` 指到的不是 PDF（法鼓佛學學報那筆回 35 KB 的 HTML）。
   一律驗 `%PDF` 開頭。

## 華藝之外：香光尼眾佛學院圖書館（開放取用，2026-09-06 實測）

🚨 **這一站的失敗模式跟臺大佛圖剛好相反：假的「非零」。**
查詢是前端 JS 組 raw SQL 塞進 `sql_form`，伺服器直接執行。只送
`title=`／`book=` 這些看得見的欄位，伺服器**完全忽略**，回的是**全庫 8,427 筆**。
實測 `title=佛` → 8,427 筆，首筆是一篇白居易墓誌銘的英文論文，跟「佛」無關。
所以**「回 8,427 筆」要當成查詢沒成立的警訊寫進 gate，不是當成成功**。
真的沒有時回的是 `alert("查無資料")`，跟有結果的頁面分得開。

```
GET https://www.gaya.org.tw/library/paper_index/index.asp
    ?sql_form=%20WHERE%20出處題名%20like%20'%獅子吼%'
    &page_rec_form=100&ScrollAction_form=<頁碼>&submit_form=開始檢索
```
欄位名：`題名`／`作者`／`關鍵詞`／`出處題名`／`提要一`…`提要五`。

`paper_index` 共 8,427 筆、1969–2001。實測：獅子吼 1,090、海潮音 1,059、
菩提樹 993、正觀 67、普門學報 32、圓光佛學學報 14；**人生與福嚴會訊是真的 0**。
🚨 只有 題名／作者／出版年月，**沒有卷期與起訖頁**——做註腳補不了，
那三個欄位仍然只有華藝與臺大佛圖有。詳目頁 `submit_form=詳細` 回 HTTP 500，壞的。

另外兩處：
- `ejournal`（佛教期刊論文檢索系統）**有卷數／期數／總期數欄位**，正是缺的那些，
  但查詢引擎壞了——任何參數組合都回同一份 14,846 bytes 的表單頁。日後值得回頭再測。
- **《香光莊嚴》全文在 `gayamagazine.org`**（不在 gaya.org.tw），1985–2026 全刊期、
  約 3,800 篇、`/article/detail/{id}` 是完整正文。列表 `?per_page=N` 的 N 是**頁碼不是筆數**，
  每頁 9 條連結裡有 3 條是固定側欄、實際 6 篇。

`www.gaya.org.tw/library/database/index.htm` 那張總目頁上的 19 條連結**全部 404**
（多插了一層 `database/`），正確路徑是 `/library/<db>/index.asp`。

## 華藝之外：國圖臺灣期刊論文索引（已建管線）

`scripts/press_ncl.py --harvest` → `public/content/research-data/press/ncl/<slug>.json`。
26 刊 / **22,345 篇目 / 缺卷期 0、缺頁次 0** / 2,081 篇有可匿名下載的 PDF。

華藝完全沒有、只有國圖收的六份佛教老雜誌（收它的全部理由）：
海潮音 4,995（**1921–2026**，最早那批就是太虛本人的〈覺明因起論〉等）、
人生 4,673（1966–2009）、獅子吼 1,417（1962–1994）、菩提樹 1,250（1952–1996）、
香光莊嚴 1,282（1992–2009）、普門學報 1,163（2001–2010）。

國圖有 PDF 且**匿名可下載、不綁 IP**的：中華佛學學報 442/442、中華佛學研究 201/201、
正觀 379/399、法鼓佛學學報 139/146、輔仁宗教研究 282/336、新世紀宗教研究 312/435、
臺大佛學研究 103/134、玉山神學院學報 116/266、臺灣神學論刊 79/398。
這幾份華藝雖然也有，但走國圖不必賭機構 IP。

🚨 四個坑（都在 `press_ncl.py` 裡有 gate）：
1. **整組表單參數都要帶**，只丟 `q[0].f`/`q[0].i` 一律回 0 筆——像「查無此刊」，
   其實是查詢沒成立。
2. **`JT` 是子字串比對**：查「人生」會撈進《財富人生》《孔學與人生》（6,370 vs 實收 4,673）、
   查「臺灣宗教研究」會混入《臺灣宗教研究通訊》（309 vs 240）。
   一定要用 `書刊名` 欄位精確過濾，不能信「檢索結果筆數」。
3. **`pageSize` 給足就一次拿完**（8000）。站方會掛「已超過系統最大設定值 (300)」的警告，
   但實測**有顯示而沒有生效**（442 筆全數回傳）。仍然要比對自報總數與實際解析筆數。
4. **PDF 標記要在原始 HTML 上判**（找 `pdfdownload` 連結）。那顆鈕的文字包在圖片裡，
   純文字化之後就消失——第一版在純文字上找「PDF全文」，442 筆全判成沒有 PDF，
   而「0 篇有 PDF」看起來完全像個合理的結果。
5. 卷期欄有三種寫法，第三種**只有民國年**（`79:12 民87.12`）。只抓西元四位數的話，
   《海潮音》早年那批會全部被判成沒有年份——而 1920–40 年代正是太虛那一段。

**國圖不收**（各試 3–4 種刊名寫法，全部真 0）：曠野、新使者、使者、台灣教會公報、
基督教論壇報、道雜誌。宇宙光只有 32 筆等同沒收。基督教側幾乎補不到東西。

### 臺大佛圖篇目：400 刊 33 萬筆（篇目在 R2，git 只留統計）

`scripts/press_dlbs.py --all` 抓（facet ≥150 筆的刊全掃），
`scripts/press_dlbs_publish.py --publish` 把逐筆篇目推到
R2 `research-private/dlbs/<slug>.jsonl.gz`，git 只留
`public/content/research-data/press/dlbs-index.json`（86 KB，各刊統計＋R2 key）。

**400 刊 / 331,389 篇目 / 117,177 有全文。** 整批放 git 是 129 MB，而其中
一大半（日文韓文的佛教學期刊、敦煌學、宗派紀要）跟博論沒有直接關係，
是掃全庫順手收的——放 git 等於每個 clone 都付那個代價，而這一層只是要「查得到」。
分工照 TCNN 那一套（全文在 R2、index 在 git）。

🚨 遷移的順序是 **上傳 → 驗 key 真的在 → 才刪本地檔**。反過來寫的話，
   R2 掛掉那一刻資料就沒了，而腳本會照常印「完成」。

🚨 **查 `ST` 不要查 `SOURCETOPIC`**（見 press_dlbs.py 檔頭）。第一次全掃用了
   SOURCETOPIC，**72 種刊實得 0 筆**而看起來只是「這些刊剛好沒東西」，
   少收 46,724 筆。另外 facet 回來的刊名帶不斷行空白（`印度學佛教學研究 `），
   過濾時兩邊都要 strip，否則那 14,715 筆會被自己的核對行擋掉。

### 南瀛佛教（已建管線，2026-09-06）

`scripts/press_dlbs.py --harvest --only 南瀛` → 篇目 12,028 筆（卷期 100% 齊）
`scripts/press_dlbs.py --nanying-fulltext` → **161 期 / 658 萬字**全文進 R2
`research-private/nanying/`，索引 `public/content/research-data/press/nanying-index.json`。

日治台灣佛教的官方機關刊物 1923–1943，計畫書第二章第五節點名的南瀛佛教會就是它；
首任會長丸井圭治郎的卷頭辭在裡面。**這批不是掃描檔、是真的文字，不必 OCR。**

🚨 五個坑，每一個都會安靜地出錯：
1. **`SOURCETOPIC:"南瀛佛教"` 是 phrase 比對，會連《南瀛佛教會會報》一起撈進來**
   （12,028 vs facet 的 10,151，差的 1,877 正好是會報）。不逐筆核對刊名，
   兩份刊互相灌水、合併時還會重複計一次。
2. **`FULLTEXTPATH` 指的是一個 HTML frameset 檢視器**（477 bytes），不是 PDF。
   直接抓會拿到一段 `<FRAMESET>`，看起來像「這篇壞掉了」。真正的內文在同目錄的
   `ny{卷}-{期}.htm`（`museum/TAIWAN/ny/`）。
3. **全文是期別層不是單篇層**：1,877 筆會報篇目的 path 全指向同一組期別檔。
   篇目照收（有卷期頁碼可引用），全文按期收，再用頁碼對應期內位置。
4. **Big5**。用 UTF-8 讀會整片亂碼而 HTTP 一樣 200（同 laijohn 那個坑）。
5. **續跑時字數不可以留成 None**。第一版「R2 已有就跳過」那條沒補字數，
   已抓過的那幾期就從統計裡消失，總字數從 658 萬安靜地少報成 634 萬——
   而索引看起來一切正常。改成先沿用舊索引、沒有才回 R2 取。

## 查證一筆引註存不存在

華藝查不到**不等於**不存在——各刊的收錄起始差很多（《神學與教會》從 2011 才收，
《台灣神學論刊》倒是 1979 起全份）。要判「這筆引註是不是幻覺」得兩邊都查：

**國圖臺灣期刊論文索引**（`https://tpl.ncl.edu.tw/NclService/JournalContent`，GET）。
🚨 只丟 `q[0].f` 與 `q[0].i` 會一律回 0 筆——看起來像「查無此篇」，其實是查詢
沒成立。**整組表單參數都要帶**：

```python
p = {"q[0].f": "AU", "q[0].i": "鄭仰恩",        # 欄位：* / TI / PTI / AU / KW / JT / CC / AB
     "q[1].o": "0", "q[1].f": "*", "q[1].i": "",
     "lang": "", "mt": "", "pys": "", "pms": "", "pye": "", "pme": "",
     "pageSize": "100"}
```
先 GET 一次 `/NclService/JournalQuery` 建 session，帶 Referer。筆數在
「檢索結果筆數(34)。」，每筆是「題　名：／作　者：／書刊名：／卷　期：／頁　次：」。

**國圖的覆蓋缺口**（2026-09 實測，用 `JT` 查刊名的筆數）：
臺灣神學論刊 398、神學與教會 638、玉山神學院學報 266、校園 1,212；
但 **《新使者》與《臺灣教會公報》都是 0**——它不收這兩份。
所以「國圖查不到《新使者》的文章」是正常的，那要走華藝。
反過來說，題名裡有「彰輝」的在國圖是 0 筆，正是因為寫黃彰輝的文章多半登在
這兩份它不收的刊物上，**不能拿來當「查無此人相關研究」的證據**。

兩邊互補：華藝有《新使者》全份而《神學與教會》只到 2011；國圖有《神學與教會》
回溯到 1985 而完全沒有《新使者》。要判一筆引註，兩邊都查過才算數。

**9. `list_issues()` 回的是兩元組不是清單。**
`issues, publisher_id = list_issues(s, pid)`。當成清單直接 `issues[0]['label']` 會
噴 `TypeError: list indices must be integers`——publisherID 是下載時的必要參數，
順手一起回傳的。

**10. 書目佇列與 PRIORITY 是兩件事。**
`PRIORITY` 是「整份刊都要收」的名單；書目點名的佇列（`airiti-wanted.json`）
可能包含**不在 PRIORITY 裡**的刊——例如《民俗曲藝》479 篇裡只要 16 篇，
就不該列入全刊掃描。`batch()` 清佇列時若只迭代 `PRIORITY`，那些刊會被整個跳過，
佇列上永遠掛著卻永遠不下載、也不報錯。正確作法是先照 PRIORITY 的序、
再把不在名單上的補在後面。

## 加一份新刊要做的事

1. `--discover` 的 JSON 裡找到 `pid`（或直接開該刊資訊頁看網址的 `publicationID`）。
2. `press_airiti.py` 的 `JOURNALS` 加一行 `"<slug>": ("<pid>", "<刊名>")`。
3. `data/press.ts` 對應的 group 加一筆 `PressTitle`，`slug` 用同一個，標 `airiti: true`，
   `to` 指 `/research-data/press/<slug>`（若站內另有全文頁，`to` 留給全文頁，
   列表會自動再長出一條「華藝篇目」連結）。
4. `--toc <slug>` → `--summarize`。
5. `npx vitest run test/press-airiti.spec.ts`。
