---
name: research-data-hongshi
description: 「印順學派與弘誓研究資料」collection（/research-data/yinshun-hongshi，需登入）的抓取／OCR／上架流程 — 佛教弘誓學院／玄奘大學刊物典藏：弘誓雙月刊、學團日誌、玄奘佛學研究學報、歷屆學術活動、福嚴會訊。🚨 2026-08 弘誓官網已改版：www.hongshi.org.tw 現在 curl＋瀏覽器 UA 就能讀（不必再 headful Chrome），但「數位典藏」各頁改由 blog.hongshi.org.tw 的 Blogger feed 動態產生，而該 blog 尚未搬完（當時僅 13 篇）；**舊路徑全數 404**，Wayback 覆蓋也極薄。已抓下來的那批是趕上了。hcu.edu.tw（玄奘）非 Cloudflare，純 requests 即可。Use when 要補抓／重抓任一刊物、跑全文、調各子頁、新增子站。與 [[project_chengzhong_bulletins]] 的 taiwan-methodist 並列於同一 /research-data portal。
---


> ⚙️ **引擎政策**：OCR 走 Gemini Vision（4 keys 輪流）→ Sonnet(OAuth) 救援，2-strike 配額停機（[[feedback_ocr_strategy]]、[[feedback_ocr_two_strike_quota]]）。所有中文一律繁體（[[feedback_traditional_chinese_only]]）。

# 印順學派與弘誓研究資料 collection

> 🚨 **`G:` 不見了＝Drive 卡住，不是掛掉。** Drive 路徑報找不到檔案時，先
> `Test-Path 'G:\我的雲端硬碟'`；False 就結束 `GoogleDriveFS` 再跑
> `"C:\Program Files\Google\Drive File Stream\launch.bat"`，約 20 秒掛回來，
> 未上傳的檔不會掉。程序在跑不等於磁碟在（全文見 CLAUDE.md）。


`/research-data`（`middleware:'auth'` 需登入）第二個 collection，slug **`yinshun-hongshi`**（rose 🪷）。作《當代的大愛道革命》([[project_dadaodao_book]]) 背景史料。記憶 [[project_yinshun_hongshi_collection]]。

| 子頁 | 來源 | 現況 |
|---|---|---|
| 弘誓雙月刊 `/magazine` `/magazine` | hongshi（有乾淨文字層 PDF） | 116 期(80–200)；**116/116 全文 ✅**（2026-09-19 補齊 103 期）＋**單篇層 104 期 / 2,388 篇**（`magazine-articles.json`）|
| 學團日誌 `/log` `/log/[n]` | hongshi 網頁文字 | **173 則(n=27–210)** ✅ |
| 玄奘佛學研究學報 `/xuanzang` | **hcu.edu.tw（非 CF）** | 45 期 / **304 篇全文 ✅(100%)** |
| 歷屆學術活動 `/meeting` `/meeting/[n]` | hongshi（經 Wayback） | **24 項** ✅（卡 `v-if=meetCount`）|
| 福嚴會訊 `/fuyan` | 沿用 dadaodao 前綴（原檔在 Drive，全文在 R2） | 71 期 ✅（品質不一，舊期有雜訊）|
| 妙心雜誌 `/miaoxin` | **mst.org.tw（靜態 Big5 HTML，純 requests）** | 202 期 / **844 篇全文 ✅**（含傳道《法句經講記》連載 66 篇、傳道長老追思專輯 94 篇）|
| 法印學報 `/faryin` | **hcu.edu.tw 佛教學系頁**（弘誓官網改版後舊路徑全 404） | 9–13 期 45 篇（30 篇有全文）|

R2 前綴：`yinshun-hongshi/<刊>/`（原檔）、`yinshun-hongshi-fulltext/<刊>/...txt`（全文）。API：`server/api/research-data/yinshun-hongshi-file.get.ts`（簽名下載）、`yinshun-hongshi-text.get.ts`（全文，pdf key→txt key）。R2 前綴限定避免任意取用。

> 🗑️ **弘誓電子報不收**：每期 EDM = 重複學團日誌 ＋ 招生廣告 ＋ 昭慧／性廣時論，時論亦登弘誓雙月刊（已收）→ 整份冗餘。（知識保留：全 1–542 期在站上，`EDM/<n>.html` 新＋`epaper/hongshi pic{,2,3}/<n>.htm` 舊【**注意 .htm 非 .html**】，5 索引頁枚舉。）

## 🚨 hongshi.org.tw = Cloudflare JS 挑戰（最關鍵）
- requests/curl/WebFetch 一律 **403 / 「請稍候／正在執行安全驗證」**。**只有 headful 真實 Chrome 過得了**：`chromium.launch({headless:false, channel:'chrome', args:['--disable-blink-features=AutomationControlled']})` + `addInitScript(navigator.webdriver=undefined)`。PDF 也在 CF 後 → 用通過挑戰的 `ctx.request.get()`（共用 cookie）下載。
- 挑戰偵測**必含中文** `正在執行安全驗證/惡意機器人/請稍候`（`hongshi.is_challenge_page`）；捕到挑戰**不可存**，退避。
- **限流真實且會累積成持續硬封**：整天連抓後會被**封數小時～一天**（連 40min／3h 冷卻都過不了）。平時：請求間隔 5–12s 隨機、index 回 0 → 重試＋退避、scraper auto-relaunch（headful 視窗會被誤關）。`log-page.php`／`meeting-B-page.php` 需 `Referer` 否則錯誤頁。
- **🆘 被硬封時改走 Wayback Machine**（archive.org 非 CF）：`http://archive.org/wayback/available?url=…` 取最近快照 → `http://web.archive.org/web/<ts>id_/<url>`（`id_` raw＝無工具列原始頁）→ 純 requests。歷屆學術活動即此法（`hongshi_meeting_wayback.py`）。**限制**：PDF 與部分頁未存檔（issue 103 PDF、6 項活動頁 Wayback 沒有）。
- **hcu.edu.tw（玄奘）不是 Cloudflare** → 純 requests（`xuanzang_journal.py`）。
- **G: streaming mount 會中途卸載** → Drive canonical 寫入一律 best-effort try/except；抓取階段先落地 `C:/tmp` staging 再搬 Drive。
- **🚨 原檔不放 R2（2026-08 改）**：弘誓雙月刊＋玄奘佛學研究 421 檔／2.8GB 已自 R2 下架，正本只在 Drive。`yinshun-hongshi-file.get.ts` 改成 **Drive 正本 → R2 後備**（[server/utils/research-files.ts](../../../server/utils/research-files.ts)），本機跑站下載照常。全文 `yinshun-hongshi-fulltext/` 純文字仍留 R2（才 45MB）。規則見 [docs/r2-policy.md](../../../docs/r2-policy.md)。

## 抓取雷區（純函式＋測試：`scripts/hongshi.py`+test 15、`scripts/xuanzang.py`+test 8）
- **弘誓雙月刊 PDF 檔名三變體**：`hongshi-magazine-187-DATE.pdf`／`magazine190-DATE.pdf`（無連字號）／`180hongshi-ROCDATE.pdf`（號在前）。`hongshi.magazine_issue()` 統一解析。1–79 期官網無 PDF；缺 85,177-180（源站連結 404）。
- **玄奘期頁有編輯誤貼的 `file:///C:\…` 本機路徑當連結**，與正常 `/files/…pdf` 並存 → harvest 必須**跳過 `file:` href**（否則被加 BASE 成假 http）。中文期數用 `xuanzang.parse_issue_no`。

## 篇目層：`scripts/hongshi_toc.py`（2026-09-10 新增）

弘誓雙月刊原本站上只有「整期 PDF」一層，所以**「某人在弘誓寫過哪些文章」查不了**
——玄奘佛學研究與法印學報都有 `articles[]`（title+author），只有這一刊沒有。

幸好這批 PDF 帶乾淨文字層，每期都有一頁排版一致的目次：

    6  　有關慈濟內湖園區爭議之商榷　／釋昭慧
    13　他們早就應該走下「神壇」
         ——點評余鐘柳律師　　／釋昭慧

`parse_toc()` 解析那一頁（找前 14 頁裡「／」最多的），零 LLM、不吃配額。四件要注意：

- **長篇名會折行**，續行以「——」起頭；`_clean` 不可 strip 破折號，否則篇名變成
  「他們早就應該走下「神壇」點評余鐘柳律師」。
- **作者可能多位**：頓號合著、`‧` 分隔的跨宗教對談（「古倫神父‧昭慧法師」）。
  `split_authors()` 全部拆開——不拆的話用「釋昭慧」比不到那一筆。
- 分類小標（`■本期專題`、`薪火相傳`）沒有頁碼也沒有作者，不是篇目。
- 🚨 **Drive 讀取很慢**：117 期約 4.7 GB，逐期 `fitz.open` 幾乎全在等 I/O
  （CPU 只跑個位數秒）。跑全量要留時間，別以為當掉了。

    python -X utf8 scripts/hongshi_toc.py --all --out public/content/research-data/yinshun-hongshi/magazine-toc.json
    python -X utf8 scripts/hongshi_toc.py --all --author 昭慧

下游：`scripts/chaohwei_articles.py` 拿這份篇目撈昭慧法師的文章，接到
`/collected-works/chao-hwei` 的「單篇文章」區（見 [[ebook-scan-transcribe]] 案例檔）。

## 檔案索引
- 純函式＋測試：`scripts/hongshi.py`、`scripts/xuanzang.py`（+ `scripts/tests/test_{hongshi,xuanzang}.py`）
- 弘誓雙月刊：`hongshi_harvest_magazine.mjs`／`hongshi_download_magazine.mjs`／`hongshi_fill_gaps.mjs`／`hongshi_publish_magazine.py`／`hongshi_ocr_magazine.py`（文字層優先，掃描退 Vision）／`hongshi_ocr_pages.py`（逐頁 OCR，整本過大 413 時用）
- 學團日誌：`hongshi_scrape_log.mjs`／`hongshi_publish_log.py`
- 歷屆學術活動：`hongshi_meeting_wayback.py`（**現用**，走 archive.org）／`hongshi_scrape_meeting.mjs`（live headful，待 hongshi 解封可補完整清單）／`hongshi_publish_meeting.py`
- 玄奘佛學研究：`xuanzang_journal.py`（`--harvest`／`--process [--no-ocr]`／`--publish`）
- 頁面 `pages/research-data/yinshun-hongshi/*`；Drive canonical `G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\`

## ⏳ 待補（皆卡在 hongshi 持續封鎖，解封後可補；非流程問題）
- ~~**弘誓雙月刊 issue 103**：下載的 PDF 損毀~~ ✅ **2026-09-19 解決，而且當初的診斷是錯的**。
  那個檔**根本沒壞**：現在 PyMuPDF 開得起來、64 頁、結尾 `%%EOF` 完整。真正的狀況是
  **它沒有文字層**（64 頁只抽得出 2,251 字，而且全是數字）——這一期是掃描本，
  而文字層管線把「抽不到字」報成了解析失敗。🚨 **「PDF 損毀」與「PDF 沒有文字層」
  是兩回事，錯判會讓人去重抓一個根本沒問題的檔。** 處置是 OCR：
  `mineru_ocr.py run --pdf <路徑> --out <jsonl>`，64 頁 194 秒、57,087 字、零空白頁。
  逐頁 JSONL 存成側車 `弘誓雙月刊-103.ocr.jsonl` 放 PDF 旁邊（切單篇要靠它），
  整期純文字照既有格式上 R2。
- **歷屆學術活動 6 項**：Wayback 未存檔 → 解封後 `hongshi_scrape_meeting.mjs`（live 完整清單，會跳過已抓 24 項）＋ `hongshi_publish_meeting.py`。

## 姊妹站：學報公開官網 → 已移出本 skill
《玄奘佛學研究》的**公開官網**（模擬站 `redpiigpig.com/Hsuan_Chuang_Studies`＋玄奘校網後台
「臺灣佛教研究中心」底下的正式站）是使用者在玄奘的**職務工作**，不屬弘誓研究資料，
2026-09-19 起獨立成 [[hcu-hcjbs-journal]]：章則五頁的「英網-N」docx 對照、各期封面與篇目
（`scripts/hcjbs_journal.py`）、校網後台帳密與「只准新建網頁」那條硬規則都在那裡。
本 skill 只管需登入的研究資料層 `/xuanzang`（45 期 304 篇全文語料）。

## See also
[[project_yinshun_hongshi_collection]]、[[project_chengzhong_bulletins]]（同 portal 衛理公會 collection）、[[ebook-pipeline]]（OCR 同源）、[[feedback_drive_canonical_storage]]。


## 2026-08-28 新增的兩個子站與判讀陷阱

**妙心雜誌**（`scripts/mst_magazine.py`）——台南妙心寺，傳道法師人間佛教在地實踐的發聲處。站台是靜態 Big5 HTML、無反爬，但有兩個會讓人「抓到東西卻是錯的」的坑：

1. **欄目索引頁的連結文字是期別標籤而非篇名**（「214期115.7.1」），直接拿 anchor text 當標題會得到一整批叫「214期115.7.1」的文章。要回頭從檔名取篇名，期別標籤則用來補期號與**出版日期**（民國年月日，語料層年表唯一的日期來源）。
2. **相對路徑常漏掉 `magazinep/` 那一層**，導致大量 404（《法句經講記》舊期就是這樣掉的）。要備一組候選 URL（插 `magazinep/`、`.htm`/`.html` 互換）依序試。

**法印學報**（`scripts/faryin_journal.py`）——弘誓的學報，但檔案掛在 hcu.edu.tw。**第 13 期整期的連結被貼成編輯者的 `file:///C:/Users/…` 本機路徑**，原檔從未上傳；PDF 拿不到，但檔名裡的作者與題名還在，仍記成「有目無文」。第 9–12 期則相反：檔名只是 `faryin12-1.pdf` 流水號，題名要從目次列「題名 作者 起始頁」解。要引的第 1 期不在此範圍，須向學團索取。

## 語料層

這批語料的最終用途是 `/research-data/corpus` 的跨刊物關鍵詞年表，見 [[project_corpus_layer]]。加新刊物時記得在 `scripts/corpus_terms.py` 的 `CORPORA` 註冊一個 `iter_*`，並確認**年份來源**——取不到年份的語料只計總數、不進年表，**一律不做內插**。

## 記憶庫併入：project_yinshun_hongshi_collection

`/research-data`（論文資料整理，需登入）2026-06-15 起的第二個 collection **「印順學派與弘誓研究資料」**（slug `yinshun-hongshi`，rose 🪷），與 [[project_chengzhong_bulletins]] 的 taiwan-methodist 並列。作《當代的大愛道革命》([[project_dadaodao_book]]) 背景史料。skill＝`research-data-hongshi`。子站：

- **弘誓雙月刊** `/magazine` — 官網 PDF（**有乾淨文字層、非純掃描**），**116 期（80–200）**。R2 `yinshun-hongshi/弘誓雙月刊/` + Drive canonical。**116/116 已抽全文**（text-layer 走 `hongshi_ocr_magazine.py`；103 期是掃描本，走 MinerU）。缺 5 期(85,177-180 源站連結 404)、1–79 期源站無 PDF。

### 單篇層（2026-09-19）— `scripts/hongshi_split_articles.py`

整期一個 txt 不夠用：要引用某一篇、要按主題找、要把某位作者的文章聚起來，都得切到單篇。
現況 **104 期 / 2,388 篇**，全文逐篇存 R2 `yinshun-hongshi-fulltext/弘誓雙月刊-單篇/`，
索引 `public/content/research-data/yinshun-hongshi/magazine-articles.json`。
昭慧法師署名 **454 篇**。

切的依據是**頁碼**，不是篇名。四個踩過的坑：

| 坑 | 症狀 |
|---|---|
| 🚨 用篇名當錨切 | 篇名是**逐頁眉標**，同一篇名在該篇每頁重複，會切出一堆碎片而段數看起來還合理 |
| 🚨 只讀 `toc_page` 一頁 | 目次常有**第二頁**（院務資訊欄）。漏掉它們，每篇結尾就吃掉夾在中間的院務頁——第 80 期最後一篇因此多吞 23 頁 |
| 🚨 短行都當欄目 | 「議程」其實是上一條篇名的續行。分辨靠排版：欄目以全形空白起首，續行是四格半形縮排 |
| 🚨 只開第一冊 | 第 200 期原檔分冊，只開 p1 會讓後半本整片落到 PDF 之外 |

🚨 **位移的門檻不能只看絕對票數。** 第一版寫「少於 5 篇同意就不切」，於是第 189 期
4/5 篇（80%）一致同意位移 0 也被跳過——那期篇目本來就只有 5 篇，永遠湊不到 5 票。
現行判準：`agree≥5` 或 `agree≥3 且比例≥50%` 或 `agree≥2 且毫無異議`，另加「次高票不得超過半數」。

🚨 **旗標要跟著資料進索引。** `beyondPdf` 第一版漏了複製進 rec，於是「目次列到 PDF 以外」
在索引裡長得跟「切出來是空的」一模一樣，稽核分不出是來源缺頁還是切壞了。

**分類兩層、來源分清楚**：`column` ＝雜誌自己的欄目（薪火相傳／輝映法界／人間探照燈／
當代台灣佛教／利他主義／院務資訊…，解析自目次頁，第一手）；`topics` ＝本專案關鍵字規則
貼的標籤（印順學／戒律與僧制／性別／動物與護生／政教關係／佛教倫理學／禪修與教理／
社會運動／學術活動／教育與學團／紀念與追思／環境與生態／院務資訊），是衍生物、會有誤差。

**回報的分母**（別只講好消息）：篇名對不上頁面 182 篇已逐篇點名；12 期因位移證據不足
不切（含第 165 期兩個位移各得 4 票、第 200 期篇目層重複且殘缺）；
**357 篇是「目次列到 PDF 以外」——原檔普遍缺最後幾頁**（收支決算表／護持徵信那一疊），
另有 10 篇是海報式公告、頁面本來就抽不到字。

第 103 期走另一條路：它的目次**整份沒有頁碼**，改用「篇名出現在頁首」定位（只認該頁前
120 字、且須逐篇遞增），9/11 條目定位成功；頁碼用 MinerU 撿回的印刷頁（位移 −1，60/64 頁一致）。

### 與臺大 DLMBS 書目對帳（2026-09-19）

臺大佛學數位圖書館的作者頁是**作者本人授權提供的書目**，可以當分母回頭檢查我們收了多少。
昭慧法師 1,006 筆中有 **648 筆出自弘誓**（`弘誓=弘誓雙月刊=弘誓通訊`），對帳結果：

| | 筆數 | |
|---|---|---|
| 已有全文 | **399** | 62% |
| 期別不在館藏 | 211 | 其中 **197 筆是 1–79 期**（源站無 PDF）、14 筆在 85／177–180（連結 404） |
| 該期沒切成功 | 24 | 集中在 113／115／157–159／161／165／167 |
| 仍對不上 | 14 | 其中 4 筆是顆粒度差異（DLMBS 逐篇拆、本刊目次合併成〈一～三〉） |

🚨 **標題比對失敗多半不是「沒有這篇」，是寫法不同。** 第一版有 70 筆對不上，逐一查下去
全是可正規化的差異，修完剩 14 筆：

| 差異 | 例 |
|---|---|
| **破折號字元** | 本刊排版用製表線 `──`(U+2500)，DLMBS 用 em dash `——`；另有 `⸺`(U+2E3A)、`－`、`–`。漏一種就比不到 |
| **舊字形** | 本刊用 眞／衆／敎，DLMBS 用 真／眾／教 |
| **主副標對調** | DLMBS「《你信什麼？》作者序:一場真誠…」↔ 本刊「一場真誠…——《你信什麼？》作者序」 |
| **顆粒度** | DLMBS 把「覆函駁批印謬論（二）（三）」逐篇列，本刊目次是〈一～三〉合併一篇 |

所以對帳要**拆成主副標、任一半對上就算**，並且把「對不上」再分成四種成因來報，
不能只丟一個覆蓋率。
- **學團日誌** `/log` `/log/[n]` — `log-page.php?n=N`（需 `Referer: log.php`），**173 則(n=27–210)**全文。n=1–26 是空 stub。
- **玄奘佛學研究學報** `/xuanzang` — **hcu.edu.tw（非 Cloudflare，純 requests！）**，45 期 / 304 篇，**297 篇有全文**（born-digital 文字層）。7 篇缺：5 篇期45 源站 `file:///C:/…` 壞連結、2 篇掃描檔待 OCR。`xuanzang_journal.py`（harvest/process/publish；`--no-ocr` 延後掃描檔避配額卡）。
- **歷屆學術活動** `/meeting` `/meeting/[n]` — 印順導師思想之理論與實踐國際學術會議歷屆＋性別倫理/動物倫理研討會公告全文，**24 項已上架**。原始碼在 hongshi `meeting-B-page.php?n=N`，但整天連抓後被 Cloudflare **持續硬封**（連 40min+ 冷卻都過不了）→ **改走 Wayback Machine** `hongshi_meeting_wayback.py`（archive.org，`<ts>id_` raw，純 requests）抓到 24/30（6 項未存檔）。`hongshi_scrape_meeting.mjs`（live headful）留著待 hongshi 解封後可補。
- **福嚴會訊** `/fuyan` — 71 期，沿用既有 dadaodao R2（`dadaodao-materials/福嚴會訊/`+fulltext，品質不一），UI 接入未重傳。
- 🗑️ **弘誓電子報已評估後不收**：每期=重複學團日誌+招生廣告+昭慧/性廣時論，user 確認時論亦登雙月刊（已收）→ 冗餘移除。（全 1–542 期確在站上：`EDM/<n>.html` 新 + `epaper/hongshi pic{,2,3}/<n>.htm` 舊**注意 .htm**，5 索引頁枚舉。）

**🚨 hongshi.org.tw = Cloudflare「Just a moment」JS 挑戰**：requests/curl 一律 403。必須 **headful 真實 Chrome**（`chromium.launch({headless:false, channel:'chrome', args:['--disable-blink-features=AutomationControlled']})` + `navigator.webdriver=undefined`）；PDF 也在 CF 後，用通過挑戰的 `ctx.request.get()` 下載。挑戰偵測含中文 `正在執行安全驗證/惡意機器人`。**密集抓必被限流**（user 明令間隔；整天連抓後會被持續 block，需數小時冷卻）：5–12s 隨機間隔、捕到挑戰退避 40s 不存、index 0-entry 重試＋冷卻、scraper auto-relaunch（headful 視窗被關過數次）。**hcu.edu.tw 不是 Cloudflare**，純 requests 即可。**G: streaming mount 會中途卸載** → Drive canonical 寫入一律 best-effort try/except，R2 才是 serving store。

純函式＋測試：`scripts/hongshi.py`(+test 15 例)、`scripts/xuanzang.py`(+test 8 例)。R2 前綴：`yinshun-hongshi/<刊>/`(原檔)、`yinshun-hongshi-fulltext/<刊>/...txt`(全文)。API：`server/api/research-data/yinshun-hongshi-file.get.ts`(簽名下載)、`yinshun-hongshi-text.get.ts`(全文,pdf key→txt)。

🚨 2026-08-27：**弘誓官網改版，舊路徑全數 404**。新站 www.hongshi.org.tw 已可用 curl＋瀏覽器 UA 直接讀（不必再 headful Chrome），但「數位典藏」各頁是靠 blog.hongshi.org.tw 的 Blogger feed 動態產生，而該 blog 當時只有 13 篇——歷史刊物尚未搬完。Wayback 覆蓋極薄（電子報 7 筆、法印學報 4 個 PDF）。所以：**先前抓下來的弘誓雙月刊／玄奘／福嚴／學團日誌是趕上了，現在原路徑已經拿不到**。

同日新增兩個子站：
- **妙心雜誌** 202 期 844 篇全文（`scripts/mst_magazine.py`）。台南妙心寺 mst.org.tw 是靜態 Big5 HTML、純 requests 可抓。兩個站方毛病：欄目索引頁的連結**文字是期別標籤而非篇名**（要回頭取檔名）、相對路徑常漏掉 `magazinep/` 那一層（要試候選 URL）。含傳道《法句經講記》連載 66 篇、傳道長老追思專輯 94 篇。
- **法印學報** 9–13 期 45 篇（30 篇有全文），`scripts/faryin_journal.py`，改從 hcu.edu.tw 佛教學系網站取。**第13期整期的連結被貼成編輯者的 `file:///C:/Users/…` 本機路徑**，原檔從未上傳，只存得下目次。要引的第 1 期（闞正宗〈傳法弘道〉、昭慧〈傳道法師對南傳佛教…〉）不在此範圍，須向學團索取。

## 索引補記

- 弘誓雙月刊116期(全文)/學團日誌173則/玄奘佛學研究45期304篇/福嚴會訊71期/學術活動(待冷卻重抓)
