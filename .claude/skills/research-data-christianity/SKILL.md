---
name: research-data-christianity
description: /research-data 底下三個基督教相關 collection 的抓取與上架流程 — 台灣基督長老教會（教會公報新聞網、新使者、總會重要文獻、賴永祥本土信徒傳記）、台灣福音派（基督教論壇報）、無教會主義（研究文獻＋《無境界者》雜誌，中日雙語）。三者合起來是博士論文第四章「長老教會的公共神學發展」與第六章「議題結盟」的史料底本，並與佛教側刊物一起進 /research-data/corpus 語料層做逐年對照。Use when 要補抓／重抓任一刊物、加新來源、調子頁、處理這些站台的解析陷阱。與 [[research-data-hongshi]]（佛教側）並列於同一 portal。
---

> ⚙️ 所有中文一律繁體（[[feedback_traditional_chinese_only]]）。抓取一律單執行緒＋延遲；義務維護的個人史料庫（laijohn）放到 0.5 秒。

# 三個基督教 collection

`/research-data`（`middleware:'auth'` 需登入）。記憶：[[project_pct_research_data]]、[[project_evangelical_collection]]、[[project_mukyokai_collection]]。

| collection | slug | 子頁 | 現況 |
|---|---|---|---|
| 台灣基督長老教會 | `pct` | 教會公報新聞網 `/tcnn` | 38,451 篇 / 4,730 萬字（2010-12–） |
| | | 新使者 `/new-messenger` | 176 期 3,848 篇 |
| | | 總會重要文獻 `/documents` | 121 件（1971–2015，含三大聲明與 1985 信仰告白） |
| | | 本土信徒傳記 `/laijohn` | 2,078 人 4,221 篇 |
| 台灣福音派 | `evangelical` | 基督教論壇報 `/ct` | 篇目 23,713（**實際可用 2019–2026**），內文陸續補 |
| 無教會主義 | `mukyokai` | （單頁） | 研究文獻 12 件（中日雙語）＋《無境界者》十期 159 篇 |

R2 前綴：`pct-fulltext/`、`evangelical-fulltext/`、`mukyokai/`＋`mukyokai-fulltext/`。
API：`pct-text`（逐篇 txt）、`pct-tcnn-text`（按年 JSONL，帶 year 回篇目、帶 id 回單篇）、`ct-text`、`mukyokai-text`、`mukyokai-file`（Drive 正本→R2 後備）。

## 各站台的解析陷阱

**tcnn.org.tw（教會公報新聞網）** `scripts/pct_tcnn.py`
WordPress 且 REST API 未關，逐篇連全文一起給，最省事。以「年」為窗口分頁避開深分頁問題。全文按年打包 JSONL 放 R2；**逐年篇目清單約 6 MB 不進 repo**，由 API 直接讀 R2 供應，否則每次重跑都整批改寫。

**gospel.pct.org.tw（新使者）** `scripts/pct_newmessenger.py --mag`
同一套舊 ASP.NET 版面用 strTID 掛多刊：1 新使者、4 女宣、6 事工說明書。三個坑：
- 內文固定在 `<td id="Zoom">`（其他選擇器都會抓到分享表單）
- **欄目那格的 class 導覽列也在用**，取第一個會拿到空的導覽格，要從題名往上找
- **期名只在文章頁的麵包屑上**，目次頁反而沒有

**www.pct.org.tw（總會重要文獻）** `scripts/pct_documents.py`
🚨 **DocID 是補零三位**（`DocID=001`）；不補零的 `1` 一律回 500，1971–2005 的早期文獻會整批漏掉——三大聲明就在那個範圍。年份取自頁面 `<title>` 的「1971重要文獻」段，比從內文猜可靠。信仰告白不走 DocID，另在 `ab_faith.aspx`（台語漢字／華語／英語三版並列），用 `--static` 收。

**ct.org.tw（基督教論壇報）** `scripts/ct_forum.py`
自寫 PHP，四個坑：
- **文章 ID 不能遞增窮舉**——無效 ID 一律回同一張預設頁（不是 404），只能從分類列表逐頁取
- **日期與作者只在列表頁上**，單篇頁沒有；列表階段就要記下來，否則語料層排不出年表
- 🚨 **翻頁的終止條件只能看「這一頁還是不是真的列表頁」**（ID 集合與第一頁相同＝已翻過頭）。用「有沒有新文章」判斷，續跑時前幾頁本來就都收過了，會一開頁就誤判到底（社論言論一類因此只抓到 36 篇，修好後 524 篇）
- 🚨 **harvest 每跑完一個分類就覆寫 HARVEST 檔**，中途 kill 掉會把先前較完整的清單覆蓋成半成品（踩過一次：完整的 23,713 篇被覆蓋成只跑到第 10 類的 10,368 篇）。要中斷就等它跑完一輪，或先備份 `C:/tmp/ct_forum.json`
- 🚨 **`--process` 一輪跑完就結束、不會自動接續**——每輪只處理當時清單裡尚未入庫的部分，看到「新增 N 篇」的結尾就是一輪結束，要再下一次
- 🚨 **專題頁判別不能只看子連結數**——每篇文章頁側欄本來就固定掛 8–9 條「相關文章」，門檻設 6 會誤殺 8,960 篇正常報導。專題頁的特徵是子連結明顯多於側欄常數且正文極短（現用 ≥14 且 <1200 字）

**laijohn.com（賴永祥長老史料庫）** `scripts/laijohn_biographies.py`
靜態 Big5、無反爬，但站方是義務維護的個人史料庫，延遲放 0.5 秒。路徑 `/archives/pc/<姓>/<姓,名>/…` 本身帶人名代碼，不必解析頁面即可歸戶。**人名代碼要用站方的羅馬字拼法**（黃彰輝是 `Ng,ChiongHui` 不是 `Ng,Chhui`），猜錯會以為沒收到；用篇名反查較保險。宋泉盛不在本土信徒區（長年在海外）。

**無教會** `scripts/mukyokai_sources.py`（單件收錄）、`scripts/nonchurch_magazine.py`（《無境界者》整本）
以「運動」而非機構為單位。日文論著保留原題（`titleOriginal`）另附中譯，`--lang ja`。支援 .docx（宣言、創刊宗旨這類原生 Word 檔，走 zipfile 讀 document.xml，不必 OCR）。
🚨 廖本恩那兩篇論文在 `G:\公事\無境界者雜誌資訊\無教會者雙月刊\`，**不在** `資料\無境界者\`（那裡只有雜誌文章 docx）。

## 拿不到的

- 《台灣教會公報》1885–2007 掃描檔須向公報社去信索取；**2008–2010 之間沒有免費線上來源**（公報社 2008–2025 PDF 合刊在 Pubu 付費）
- 《使者》（1963–1990，新使者前身）線上無全文典藏
- 女宣雜誌：依語料層的判準（會不會跑語料級運算）評估後**決定不收**
- 校園書房站上只有書目與商品頁、無全文
