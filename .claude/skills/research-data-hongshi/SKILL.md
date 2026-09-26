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

## 日本學者論印順（2026-09-23）— `/research-data/yinshun-hongshi/japan`

日文學界評介、研究印順的論文、書評與學位審查報告，能取得全文者逐段譯中，**左欄中譯、右欄原文**。

- **來源與普查**：Drive `研究資料\印順學派與弘誓\日本學者論印順\`，`目錄.md` 是普查結果（97 筆：專論／部分論及／僅提及／非日籍作者）。
  PDF 多取自 J-STAGE、各校機構庫、東洋哲學研究所（totetu.org）。
- **書目**：`scripts/data/yinshun_japan_catalog.json`。欄位 `translate`（要翻）、`ocr`（走 Vision OCR 不讀文字層）、
  `pageStart`／`pageStep`（印刷頁碼起點與方向；印佛研橫排論文與京產大紀要是**倒數**頁碼，step=-1）、
  `zhSame`（原件本即中文，譯文欄同原文，如《內明》21 期的審查報告中譯）、`startMarker`／`endMarker`（雜誌掃描頁混著前後篇時，本篇起訖段落的字串）。
- **腳本**：`scripts/yinshun_japan_bilingual.py`
  - `--ocr`：`ocr:true` 的篇目逐 2 頁送 Gemini Vision（`ocr_pdf_to_text.ocr_pdf`，key×模型輪替），每批寫回 Drive `_對照\<id>.ocr.json`（可續跑），全部完成才組 `_對照\<id>.ocr.txt`（每印刷頁以 `【頁 N】` 開頭）。
  - `--ocr --reocr-missing`：只把沒讀到數字頁碼的 PDF 頁重跑一次（模型常漏看頁腳「—743—」；重跑仍無就留 null）。
  - `--dry-run [--show N]`：切段＋**字數對帳**（文字層：`get_text` 全文－書眉頁碼－ルビ ＝ 切段字數，差 >2% 標 🚩；OCR：OCR 字數 vs 切段字數＋讀到頁碼的頁數）。
  - 不加旗標：切段（工作檔不存在時）＋逐段翻譯，每段寫回 `_對照\<id>.json`，斷線重跑從缺口接；`--resplit` 會清掉已譯內容。
  - `--upload`：送 R2 `yinshun-hongshi-fulltext/<id>.json`（`{id, paras:[{page, orig, zh}]}`）並重寫 `public/content/research-data/yinshun-hongshi/japan-index.json`。
  - 長跑用 scratchpad 的 worker 迴圈：每組 `--only a,b,c` 跑到全譯完，引擎連續 3 段失敗退出就睡 5 分鐘再接。多開幾條（不同篇目）可平行。
- **前端**：`pages/research-data/yinshun-hongshi/japan/index.vue`＋`server/api/research-data/yinshun-hongshi-bilingual.get.ts`（`requireAdmin`，讀 R2）。

### 切段的坑（文字層）

1. 🚨 **雙欄判準不能用「左右各有兩個 block」**：上標註號是獨立小 block，單欄頁會被判成雙欄，
   句子被註號拆散、整行消失（西野 2020 第一頁實測）。現判準：只落在左半／右半的**行**各佔全頁字數 30% 以上才算雙欄。
2. **不用 block，用 span 自組視覺行**：正文 span 按基線分行；小字 span 若是註號（`(1)`、`（12）`、`＊`）就併進緊貼的那一行成行內數字；
   純假名小字且在某行**正下方**緊貼的是ルビ，丟掉（野川 2009 整篇帶ルビ，不丟會變成「おもむ」一段）。
   🚨 找ルビ的歸屬不能用「重疊最多的行」——ルビ跟上一行的距離可能一樣近，要專找正下方那行。
3. **段首判斷看鄰行，不看整欄邊界**：首行縮排＝比下一行靠右且比上一行靠右；進入引文塊＝比上一行靠右一字半以上。
   用整欄左右緣會把兩側內縮的引文逐行切斷（伊吹 2018 一度 515 段）。
4. 「上一行提早收尾」只在句末標點／標題／字級變化時算分段——圖片旁繞排的窄行也提早收尾，但不是分段（志賀 2016）。
5. **頁首／欄首第一行沒縮排＝承接上一頁**，不可一律當段首，否則跨頁的段全斷。
6. 書眉頁碼：上下緣 12% 內、去數字後跨頁重複的短行＋純頁碼行＋「- 180 -刊名」＋首頁刊頭（以本頁頁碼收尾）。
   A5 紀要的書眉在 y≈58/595，10% 帶會漏。
7. 頁腳註文不打斷正文：暫存，等跨頁的那一段接完才放出來。

### OCR 的坑

1. 🚨 **Gemini JSON 模式會把 text 裡的換行全吃掉**（整頁一行）。prompt 要求在段尾加 `¶`，解析時 `¶` 與 `【頁 N】` 都當分隔。
2. 模型仍常照**印刷行**斷行（直排尤甚）：解析時上一行沒以句號類收尾、本行不像標題或註 → 併段。
3. 模型被叫「別抄書眉」「只轉錄本篇」照樣抄：解析時濾全篇重複的短行與純頁碼行（含漢數字「二六三」）；
   同頁混別篇（《內明》審查報告第一頁右半是前一篇結尾）靠書目 `startMarker` 截。
4. 模型偶爾把印刷頁碼填進 JSON 的 `page`：回傳頁數對得上就照順序對回 PDF 頁。
5. `gemini-flash-latest` 常 503，OCR 預設 `gemini-2.5-flash`（`YJ_OCR_MODEL` 可換）。
6. 哪些走 OCR：無文字層的（水野 1971、《內明》中譯、蓑輪 2000、菅野 2005——後兩者是東洋學術研究的**跨頁掃描**，一個 PDF 頁兩個印刷頁）、
   文字層是舊 OCR 的掃描（藤吉 1968 淨土→浮土、印佛研 2004–06、NII-ELS 那批）、以及**直排**的新刊（魏道儒 2010、何建明 2011、何燕生 2020）——直排段組用文字層排序不可靠。

### 翻譯的坑

- 🚨 **日文原文欄絕不過 OpenCC**（余輩→餘輩、岩波→巖波）。譯文欄的 NVIDIA 層會過 s2tw，所以腳本把 `《》〈〉『』` 裡的字與「岩波／余輩」先換佔位符、轉完換回。
- 頁碼只用印刷頁碼；讀不到（方東岳 2022 的 PDF 根本沒印頁碼）就留 null，不用段序頂替。
- 譯文過 `translate_ebook_to_zh.unusable_reason`（擋整段沒譯的日文、推理外洩、提示詞回音），外加剝 `<think>` 與「以下是翻譯」前言。
- 2026-09 NVIDIA 模型是 `nemotron-3-super-120b-a12b`（deepseek-v4-flash-0731 已於 08-26 停服）。

### 2026-09-24 擴充：其餘 49 篇全部轉錄＋背景續跑

- 書目新欄位：`transcribeOnly`（中文／英文原件，只轉錄、站上單欄，不譯；野川 2013、侯坤宏 2022 中文版、印佛研英文稿 6 篇）、
  `ocrEngine: "mineru"`（橫排掃描走本機 MinerU CPU，其餘 `ocr:true` 走 Gemini）。74 篇有 PDF 者 `translate` 全開。
- 哪條路：**影像＋J-STAGE 舊 OCR 層**（字體 ＭＳ明朝／Courier／MS-Gothic、每頁一張整頁圖）一律重 OCR——
  直排的（印佛研 1953–2001 與 2006–07、菅野 2005、蓑輪 2000、肖越 2009）走 Gemini；橫排的（印佛研 2002–07 大半、
  宗教と社会、天理、佛教文化学会紀要）走 MinerU。🚨 文字層說「直排 100%」的金子 2004 其實是橫排、說「橫排」的吉村 2007 其實是直排：
  掃描檔的方向要看圖，不能信 OCR 層。日本佛教學會年報 2000／2002（ILMA 字型）文字層把「『』「」―」對成韓文字、還**吃掉「瑜」字**，也改 MinerU。
- **直排文字層切段**（新，`vertical_page_items`）：印佛研直排 PDF 是「一字一個 line」。字按中心 x 分直行 → 用非通欄直行的 y 覆蓋率找段間空白（gutter）
  → 每直行歸上段／下段／通欄 → 由右而左把連續的非通欄直行併成一「區」，區內先上段後下段。
  🚨 不可整頁按 (-x1, y0) 排（上下兩段式會交錯）；🚨 不可只靠「有沒有上下對應的伴」分區（首頁通欄要旨＋左半才分段的康 2019、
  標題橫跨兩段而下段右端沒有上段對應的魏 2023 都會排錯）。註號「（ ）」小字直行連同裡面的縱中橫數字當一個記號插回正文（`とどまる（3）`）。
- 背景：`python scripts/yinshun_japan_bilingual.py --auto`（OCR→切段→翻譯→上傳 R2→重寫索引，一次一篇）；
  `--status` 印每篇進度與分母。Gemini OCR 連兩次配額錯就寫 `output/yinshun-fulltext/gemini_blocked_until.txt`（停 4 小時，與人間佛教論爭那支共用）。
  翻譯連兩篇停在失敗就整場停。排程見下節 keeper。

## 人間佛教論爭（2026-09-24）— `/research-data/yinshun-hongshi/debate`

印順《我有明珠一顆》讀後引發的現代禪論辯（李元松、溫金柯、楊惠南…），及西方與中文學界、原始佛教復原主義的相關論著。

- **來源**：Drive `研究資料\印順學派與弘誓\人間佛教論爭\`（根目錄＝論爭核心文獻、子夾 `西方與中文學界`、`復原主義比較`）；
  2026-09-24 普查 74 檔（pdf 42／html 20／htm 9／md 3）。檔名 `年_作者_題名`，年份不明者寫「年待核」。
- **腳本**：`scripts/yinshun_debate_fulltext.py`（`--status` 印分母與未完成清單、`--no-ocr`、`--only <相對路徑> --force`）。
  - PDF 文字層：借用日本學者那支的 `horizontal_page_items`／`vertical_page_items`；中文雙欄欄距窄（約 3 字）時先用 block 找欄縫、
    分 [通欄頂／左欄／右欄／通欄底] 四塊 clip 各自讀（`column_clips`）。🚨 欄縫要取最低跨越量那一段的**正中間**——貼著左欄右緣切，
    clip 會把左欄行尾的字收進右欄（林建德 2011「轉學化」）。
  - 頁碼：每頁前 `【頁 N】`＝頁上印的頁碼（上下緣 10% 短行首尾的數字，與頁序位移〔遞增或遞減〕多數一致且該頁真印著才算），
    讀不到寫 `【PDF 頁 N】`，不推算。CBETA HTML 的行號 `Y43n0041_p0221a01` 換頁處轉成 `【頁 221】`（＝《印順法師佛學著作集》頁碼）。
  - HTML：meta charset → utf-8 → big5hkscs → cp950；剝 Wayback 工具列。
  - 掃描判準：六成以上頁面 <100 字，**或**字型是 `HiddenHorzOCR／HiddenVertOCR`（掃描器附的隱形 OCR 層：林建德 2003 香光莊嚴上下兩篇，
    字在但直排讀序全亂、「印順法帥」）。英文掃描走 MinerU（CPU），中日文走 Gemini（2 頁一批，`_全文\_ocr\<md5>.json` 可續跑）。
  - 簡→繁只在「簡體專用字密度 >1.5%、無假名、漢字多於拉丁字母」時做（s2tw＋TRAD_FIXES）；西文論文裡夾的日文書名不轉。
  - 輸出：Drive `_全文\<相對路徑>.txt`、R2 `yinshun-hongshi-fulltext/人間佛教論爭/<相對路徑去副檔名>.txt`；
    原檔 ≤30MB 上 R2 `yinshun-hongshi/人間佛教論爭/…`（1917 荻原 64MB 留 Drive）；進度 Drive `_全文\_status.json`；
    索引 `public/content/research-data/yinshun-hongshi/debate-index.json`（進 git）。
- **前端**：`pages/research-data/yinshun-hongshi/debate/index.vue`；全文走 `yinshun-hongshi-text`（已擴充剝 .html/.htm/.md），
  原檔走 `yinshun-hongshi-file`（非 PDF 一律 `application/octet-stream`＋附件，第三方 HTML 不在站內同源渲染）。

## 背景 keeper：`KGL_Yinshun_Fulltext`（每 60 分）

`scripts/yinshun_fulltext_keeper.ps1`（UTF-8 BOM、python 寫完整路徑 `C:\Users\user\AppData\Local\Python\bin\python.exe`）：
兩條工作（debate／japan）沒在跑也沒完成就背景重啟，日誌 `output/yinshun-fulltext/<名>-<時間>.out.log`、keeper 自身 `keeper.log`。
兩條都印出 `ALL_DONE` → 只 commit 兩份索引並 push → **自行註銷排程**；同一「本輪結束」摘要連 36 輪不變 → 標 `<名>.stalled` 並註銷。
查進度：`python -X utf8 scripts/yinshun_debate_fulltext.py --status`、`python -X utf8 scripts/yinshun_japan_bilingual.py --status`。

<!-- rule:user-docx-no-overwrite -->
## 🚨 使用者會改的 Word 檔：只能就地改，絕不重建覆蓋

交出去的 .docx 一產出，使用者就會直接在 Word 裡改，**從那一刻起 docx 才是正本**，md、腳本、法師／老師的修訂稿都不是。

1. **寫入前先讀現檔**：抽出全文，跟自己上一次寫出的版本比對；只要有任何不是我改的差異，就代表使用者動過。
2. **只就地改指定處**：逐段改文字、插圖片。禁止「從原稿／md／修訂稿重跑一次產生器」再存回同一個檔名。
3. **有 `~$` 鎖檔就不寫**：代表 Word 正開著，寫進去會跟使用者的存檔互相覆蓋。改成把素材（圖片、段落）另存新檔，請使用者插入，或等關檔。
4. **要大改就另存新檔**，檔名加版本或日期，不覆蓋原檔。
5. **救援**：Drive 網頁 → 檔案 → 管理版本（保留 30 天）。

事故：2026-09-24 獎學金論文連續五次從 md 重建蓋掉修改；2026-09-26 弘青網路學堂文案定稿又從法師修訂稿整份重建，蓋掉使用者在定稿上的修改。
