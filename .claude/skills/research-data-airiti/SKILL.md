---
name: research-data-airiti
description: 從華藝線上圖書館（Airiti Library）收宗教類期刊的「篇目索引 →（授權內）全文下載」流程 —— 教會刊物與神學院學報（校園／新使者／曠野／神學與教會／台灣神學論刊／華神期刊／道風／建道／神學論集…）、佛學學報（中華佛學學報／法鼓／臺大佛學研究／佛光／玄奘佛學研究／法印／華嚴…）、宗教學期刊（臺灣宗教研究／輔仁宗教研究／宗教哲學／華人宗教研究…）。這些刊自家網站多半只有內文或只有近幾年，華藝反而整份收著且帶**卷期、起訖頁、正式作者署名**——做註腳非有不可的三個欄位。Use when 要新增一份華藝期刊、補抓某刊篇目、下載某刊全文 PDF、debug 抓不到卷期或下載回傳不是 PDF、或使用者提到「華藝」「airiti」「校園雙月刊」「篇目」「卷期頁碼」。刊物本位那一層的頁面規矩見 [[research-data-christianity]] 與 [[works-corpus-layer]]。
---

> ⚙️ 所有中文一律繁體（[[feedback_traditional_chinese_only]]）。

# 華藝期刊：篇目索引與全文下載

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

## 排程

`scripts/run_airiti_batch.bat <篇數>`，Windows 排程四個時段各 50 篇＝一天 200 篇：
`KGL_Airiti_1` 09:30、`KGL_Airiti_2` 11:30、`KGL_Airiti_3` 14:30、`KGL_Airiti_4` 16:30。
log 在 `c:	mpiriti_download.log`。

🚨 **只排 09:00–18:00**。使用者的機器只有在學校時才拿得到玄奘的 IP，
不在學校的時段排了也只是每篇都失敗——而失敗的症狀是拿到 JSON 不是 PDF，
不會有紅字。要改時段先問過，別自己往晚上挪。

### 書目點名的那些篇要排在最前面

`airiti_wanted_from_bibliography.py`（另一支）把寫作計畫的書目對到**刊**；
`press_airiti.py --resolve-wanted` 再把篇名對到 **docID**，寫成
`public/content/research-data/press/airiti-wanted.json`。`--batch` 每次跑之前
會自動重算一次（純讀本機檔、不打網路），所以新抓好的篇目會讓原本
「篇目還沒抓」的條目自己補進佇列。全部 17,090 篇要跑幾個月，
論文當下要引的那些排在後面就等於沒下。

篇名比對只去標點與全半形，**不做繁簡轉換也不去虛詞**——那會把不同的兩篇
折成同一篇，而症狀是「下載到的不是我要的那篇」。破折號要涵蓋六種寫法
（—— ― ─ – － ‐），少一種就會有篇對不上。`scripts/tests/test_press_airiti.py` 在擋。

`--batch N` 與 `--download <slug> --limit N` 的差別：前者是**整批總共 N 篇**、
跨刊依 `PRIORITY` 順序取用；後者是**每一刊各 N 篇**。排程要控的是每天對華藝
發出多少下載請求，所以排程一律走 `--batch`。

`--batch` 會上鎖（`c:	mp\press_airiti_download.lock`，三小時後視為過期）。
🚨 這個鎖不是可有可無的：實測發生過兩個 session 同時在下載，那等於把對機構 IP
的請求速率乘二，而節流的整個意義就在速率。

**體量（2026-09-04 實測）**：29 個刊號共 17,426 篇目、其中 17,090 篇有電子全文，
以每篇約 2.4 MB 計約 40 GB。一天 50 篇要跑 11 個月；要在一季內下完得拉到
一天 200 篇上下。改速率就是改兩個排程任務的引數，不必動腳本。

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

**4. 寫檔到 G: 會偶發 OSError 22。**
目的地是 Google Drive 的虛擬磁碟，偶爾回 `Invalid argument`，過幾秒重寫同一個檔
就好——不是檔名的問題（實測 60 字元的純中文檔名照樣中）。`write_with_retry()`
retry 四次；沒有這層保護的話，一次打嗝會把整批 300 篇的迴圈整個帶走。

**5. 華藝的收錄起始 ≠ 創刊年。**
《校園》1957 年創刊，華藝從 2005 年的 47 卷 1 期收起。混為一談就會在論文裡
把「資料庫沒有」寫成「那些年沒出刊」。`data/press.ts` 因此把 `start`（創刊）
與 `coverage`（收錄斷限）分成兩個欄位，`test/press-airiti.spec.ts` 有一條在擋。

**6. 同一份刊會被拆成兩筆。**
刊名一改，華藝就另立 PublicationID：《中華佛學學報》舊名（至 26 期／2013）與
現名 Journal of Chinese Buddhist Studies（27 期起）是兩筆；《臺大佛學研究》與
《佛學研究中心學報》也是。要看完整年表兩筆都得抓，所以 `JOURNALS` 裡都收了。

**7. 卷期標籤格式各刊不一，不要自己排序。**
「68卷2期」「26期」「新12卷2期」「46卷2期&47卷1期」都有。`--toc` 照華藝原序
（新 → 舊）保留，前端也照原序渲染。自己 parse 數字重排一定排錯。

**8. slug 打錯不會爆。**
`data/press.ts` 的 slug 與 `press_airiti.py` 的 `JOURNALS` 鍵必須一致，
否則 `/research-data/press/<slug>` 只會渲染一個「尚未收錄篇目」的空頁——
完全正常的畫面、完全錯誤的結果。`test/press-airiti.spec.ts` 把兩邊名單對起來擋這個。

## 華藝上有／沒有的

`--discover` 的輸出在 `public/content/research-data/press/airiti-journals.json`，
記了每一筆是靠學科分類找到的還是靠刊名探測補到的（`found_by`）。
2026-09 的普查：宗教學學科底下 **68 種**，刊名探測再補 9 種（多半是慈濟系統的
校院學報，與本論文無關）。

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

## 加一份新刊要做的事

1. `--discover` 的 JSON 裡找到 `pid`（或直接開該刊資訊頁看網址的 `publicationID`）。
2. `press_airiti.py` 的 `JOURNALS` 加一行 `"<slug>": ("<pid>", "<刊名>")`。
3. `data/press.ts` 對應的 group 加一筆 `PressTitle`，`slug` 用同一個，標 `airiti: true`，
   `to` 指 `/research-data/press/<slug>`（若站內另有全文頁，`to` 留給全文頁，
   列表會自動再長出一條「華藝篇目」連結）。
4. `--toc <slug>` → `--summarize`。
5. `npx vitest run test/press-airiti.spec.ts`。
