# 免費全文來源清單（2026-09-11 從本機實測；2026-09-16 補俄／西／簡中）

z-library 不是唯一一條路，而且對**十九世紀與二十世紀前半的學術著作**來說它往往
不是最好的一條——那些書多半已進入公有領域，掃描本就在公開典藏裡，畫質與版次
還比 z-lib 上的隨手上傳可靠。這份清單記「哪裡有、怎麼取、有什麼坑」。

連通性是**從這台機器實測**的，不是抄來的；被擋的三個一併記下，免得下次再試一次。

## 通得到的（15）

| 站 | 強項 | 取文字的路徑 |
|---|---|---|
| **archive.org** | 什麼都有，英文為主 | `advancedsearch.php?…&output=json` 搜 → `metadata/{id}` 驗 → `download/{id}/{name}` |
| **Project Gutenberg** | 乾淨的純文字與真 EPUB，無 OCR 雜訊 | `https://gutendex.com/books?search=` 查 → `gutenberg.org/ebooks/{id}.epub3.images` |
| **NDL 國立國會圖書館** | 日文，戰前那批的唯一來源 | repo 已有 `scripts/ndl_*.py`；官方 OCR `/dl/api/book/layouttext/{pid}` |
| **青空文庫** | 日文公有領域文學與思想 | repo 已用（內村鑑三那條線） |
| **DBNL** | **荷蘭文**——蒂勒、尚特皮、克里斯滕森、范德列烏都是荷蘭人 | 首頁通，站內搜尋端點要再摸 |
| **Delpher（荷蘭國圖）** | 荷蘭文報刊與書籍掃描 | 首頁通 |
| **Persée** | **法國人文社科期刊全文**，含《社會學年鑑》 | 首頁通，搜尋頁是 JS 產生的要另找 API |
| **Runeberg** | **北歐語**（瑞典／挪威／丹麥）——瑟德布盧姆 | 目錄頁 `katalog.html` 可直讀，已確認含 Söderblom |
| **Deutsches Textarchiv** | **德文歷史文本的高品質人工校對轉錄** | 對付 Fraktur 的正解，見下 |
| **MDZ 慕尼黑數位中心** | 德文掃描（bsb-muenchen） | |
| **Zeno.org** | 德文哲學／文學全文 | 作者頁路徑要查，`/Philosophie/M/{作者}` 不一定存在 |
| **Wikisource（各語言）** | 本身的全文，以及**指向掃描本的 identifier** | 🔑 見下「Wikisource 的隱藏用途」 |
| **DOAB／OAPEN** | **當代學術專書的開放取用版**——當代宗教學唯一的合法免費路 | 值得對 32 位當代學者逐一查 |
| **ctext 中國哲學書電子化計劃** | 漢籍 | |
| **libgen.li** | 受版權 | 要 PowerShell IWR 別讓檔案落地（Defender） |

## 連不到的（3）

| 站 | 症狀 | 說明 |
|---|---|---|
| **HathiTrust** | HTTP 403 | 全文檢索與 pre-1929 full view 都拿不到 |
| **OpenEdition Books** | HTTP 500 | 法語人文社科 OA，可惜 |
| **Anna's Archive** | DNS 解析失敗 | 與 [[project_christianity_studies_littleblackbook]] 記載一致 |

另有兩個**通得到但擋機器人**的：
- **Gallica（法國國圖）**：首頁與 SRU 檢索 API 可用（`/SRU?operation=searchRetrieve&query=`），
  但 `.texteBrut` 全文端點回「Vérification de sécurité」擋下。**所以 Gallica 能用來
  確認某本書存在與取得 ark，不能用來抓全文。**
- **Les Classiques des sciences sociales（UQAC）**：連線逾時。

## 🔑 Wikisource 的隱藏用途：找 archive.org 的 identifier

奧托《論「聖」》的德文原著在 archive.org 上搜不到——用 `creator:("Otto, Rudolf")`
翻遍前十幾筆都是別人的書或借閱館藏。**是 de.wikisource 的作者頁把它交出來的**：

    https://de.wikisource.org/w/api.php?action=parse&page=Rudolf%20Otto&prop=wikitext&format=json

原始 wikitext 裡寫著 `{{Digitalisat|IA=20200310dasheilige|LT=…14. Auflage, Klotz, Gotha 1926}}`
——`IA=` 後面就是 archive.org 的 identifier。各語言 Wikisource 的作者頁常常已經有人
把掃描本編目好了，**比自己在 archive.org 亂搜有效得多**。渲染後的 HTML 看不到這個
模板參數，要取 raw wikitext。

## 🚨 archive.org 的三個坑（每一個都會讓你以為成功了）

1. **借閱館藏搜得到、下載不到。** `metadata.access-restricted-item == "true"` 就是。
   識別碼常見 `xxxx0000auth` 樣式。每一筆候選都要查 metadata，不能只看搜尋結果。
2. **掃描件的 EPUB 常常只有頁面影像沒有文字層。** parse_worker 會回
   `no extractable text`。**一律改用 `DjVuTXT`**，從 metadata 的 `files` 找
   `format == "DjVuTXT"` 的 `name`（含空格與非 ASCII，要 URL-encode）。
3. **OCR 可能整本是廢的，而檔案大小完全正常。**

   工具：`python scripts/archive_djvu_clean.py <檔> --check de`（語言代碼 en/de/fr/sv/nl）。

   **第一道：虛詞比值**＝四個常見虛詞的命中總數 ÷（字元數/10000）。**低於 80 就有問題。**

   | 語言 | 探詞 | 中鏢實例 |
   |---|---|---|
   | 英文 | the / and / of / that | |
   | 德文 | und / der / die / ist | 奧托《康德-弗里斯學派》57 萬字裡 `und` 只 9 次、`ist` 0 次 |
   | 法文 | de / la / les / est | |
   | 瑞典文 | och / att / som / för | |

   德文中鏢幾乎都是 **Fraktur 尖角體**被當成 Antiqua 讀，系統性替換
   （bie＝die、^afein＝Dasein、beroor＝bevor）。十九世紀德文書很容易中。

   ### 🚨 第二道：長 s 檢查（只對德文，2026-09-11 補上）

   **比值合格不代表沒事。**瑟德布盧姆《Das Werden des Gottesglaubens》(1916)
   四詞比值 **139.9**，照第一道判準完全合格——但整本不能用：

   | | 該有 | 實際 |
   |---|---|---|
   | `ist` | 數百上千 | **2** |
   | `ift` + `ijt` | 0 | **934** |
   | `sich` | 數百 | 3 |
   | `fich` | 0 | 93 |

   原因是 Fraktur 的**長 s（ſ）被讀成 f 或 j**。而 `und`／`der`／`die` 三個詞
   **剛好都不含長 s**，所以它們讀得對、把比值撐起來了，第四個詞 `ist` 的崩塌被平均掉。

   所以德文一定要**另外比** `ist` vs `ift+ijt`、`sich` vs `fich`。
   `quality()` 已經內建這一條，`--check de` 會直接報 `🚨 Fraktur 長 s 誤讀`。

   **對策**：改抓同一筆的 PDF 存著待 Gemini Vision 重 OCR；或去
   **Deutsches Textarchiv** 找人工校對版（⚠️ 但 DTA 大致止於 1900 年前，
   二十世紀的書它沒有）；或**改用同一本書的其他語言版本**——瑟德布盧姆那本
   1916 德文的母本就是 1914 瑞典文《Gudstrons uppkomst》，而瑞典文那本
   OCR 乾淨（每萬字 127.7）。

4. **有 DjVuTXT 不等於有文字層。** `TotemismAndExogamyVol4` 的 DjVuTXT 只有
   9,818 bytes——是空的。**下載前先看 metadata 裡 `files[].size`**，
   一本書的文字檔低於 50 KB 就該起疑。

## 找不到一本書的時候該怎麼辦（決策順序）

z-lib 找不到、華藝也沒有，**不是走到底了，是還沒開始分流**。
這份清單之所以存在，就是因為「z-library 不是唯一一條路」。

### 🚨 第一步不是搜尋，是先確定它屬於哪一類

同一本書在不同的庫裡，命中率差一個數量級。先問三件事，答案決定去哪裡找：

| 問 | 為什麼決定去哪 |
|---|---|
| **出版年？** | 1929 年前／作者歿逾 70 年 → 公有領域，掃描本就在公開典藏裡，**畫質與版次還比 z-lib 的隨手上傳可靠** |
| **什麼語言？** | 每種語言的主力庫不一樣，而且多半**不是英文那幾個** |
| **書還是文章？** | 專書走典藏與 OA 書庫，期刊論文走 DOI／OA 期刊平台，兩條路幾乎不重疊 |

### 分流表

**公有領域（多數十九世紀與二十世紀前半的學術著作都是）**

1. **先查該語言 Wikisource 的作者頁拿 archive.org identifier**——實測比在
   archive.org 亂搜有效得多（見上面「Wikisource 的隱藏用途」）。
2. archive.org（記得避開借閱館藏、用 `DjVuTXT` 不要 EPUB、驗虛詞比值）
3. 語言特化的那幾個，OCR 品質常常比 archive.org 好：
   德文 1900 前 → **Deutsches Textarchiv**（人工校對）；德文掃描 → MDZ／Zeno.org；
   北歐 → **Runeberg**；荷蘭文 → **DBNL**；日文戰前 → **NDL「インターネット公開」層**；
   法文期刊 → **Persée**；英文純文字 → **Gutenberg**
4. 同一本找不到乾淨的 OCR 時，**改找它的其他語言版本**——瑟德布盧姆 1916 德文
   OCR 是廢的，但它的母本 1914 瑞典文在 Runeberg 上乾淨得多。

**當代學術（受版權）**

1. **DOAB／OAPEN**——當代學術專書的開放取用版，是當代宗教學唯一的合法免費路
2. 出版社自己的 OA 頁（近年不少大學社會放單章）
3. z-library ／ libgen
4. 期刊論文另走：Crossref 查 DOI → DOAJ → 期刊自己的網站 →
   俄文 **CyberLeninka**（唯一路徑完全走通的新站）／日文 **J-Stage**／
   法文 Persée／繁中 **華藝**（綁機構 IP）

**中文**

- 古典漢籍 → ctext／中華典藏／國學大師
- 繁中當代期刊 → 華藝（32 刊已收）
- 佛學 → CBETA（原典）／臺大佛學數位圖書館（**書目層 52 萬筆，但沒有全文**）
- 簡中當代學術 → **幾乎全鎖**（CNKI 付費、NCPSSD 要登入、讀秀綁機構），
  能取的只有古籍。要當代中文研究就回頭走華藝

**都沒有**

**不要把它從獵表刪掉。** 記 `no-usable-hit` 留在清單裡，
`zlib_fetch.mjs --probe` 會定期重探——z-library 的庫存一直在變，
今天沒有的下個月可能就有。真的非要不可才走館際合作或買實體書。

## 建一位學者的全集，要把每個資料庫都搜一遍嗎？

**不要。這樣做既慢又永遠不知道自己漏了什麼。**

關鍵在順序反過來：**先確定分母，再逐筆去找**。

### 1. 先立著作目錄，那才是權威

分母來自**書目**，不是搜尋結果。搜尋只能告訴你「找得到什麼」，
永遠不會告訴你「還缺什麼」。可用的權威來源：

- 專論的附錄（昭慧法師全集的分母就是一本碩論的附錄三，46 本）
- 紀念文集／Festschrift 的著作目錄
- 學者本人的履歷或基金會官網
- 國家圖書館的權威檔（作者典藏記錄）

### 2. 目錄逐筆進獵表，一筆一個 key

每一筆帶 `who`／`lang`／`expect`。同一本書的原文與中譯**分成兩筆**
（`-orig`／`-zh`），因為它們會在完全不同的庫裡。

### 3. 每一筆按上面的分流表選庫，不是每個庫都打一遍

一本 1902 年的德文書不必去 z-lib 問，一本 2019 年的英文專書不必去 DTA 問。

### 4. 帳本記每一筆的下場，查不到也要記

`scripts/state/zlib_ledger.jsonl` 就是這個。有了分母與帳本，
「這位學者的全集收了幾成」才是一個可以回答的問題——
否則永遠只能說「我找到了這些」，說不出還缺哪些。

> 🚨 **獵表是願望清單不是庫存清單。** 它從書目生成，沒跟館藏比對過，
> 所以別的路徑收進來的書還是會被排進去再抓一次。
> 定期跑 `scripts/zlib_retire_owned.py --audit` 把已經有的註銷掉。

### 現況：知道哪裡有，還不能一鍵查

| | |
|---|---|
| 已接進管線 | archive.org、Gutenberg、NDL、青空文庫 |
| 路徑走通、還沒寫腳本 | **CyberLeninka**（俄文，POST API → 全文 → PDF 全程可腳本化） |
| 只確認連得到 | Persée、DBNL、DTA、MDZ、Runeberg、Zeno.org、DOAB／OAPEN、Mercaba、中華典藏… |

**沒有一支「一次查遍所有來源」的工具**，目前是逐庫手動。
要補的話，第一個該寫的是 CyberLeninka（唯一路徑完全走通的）。

## 俄文・西班牙文・簡體中文（2026-09-16 補測）

原本這份清單少了三種語言。一樣是從這台機器逐站打過，不是抄的。

### 俄文

| 站 | 狀態 | 說明 |
|---|---|---|
| **CyberLeninka** | ✅ **全程可腳本化** | 俄文的主力，見下面的取件配方 |
| Предание.ру | ✅ 通 | 東正教文獻，176 KB／33,888 西里爾字；有 epub／fb2，但下載連結是 JS 產的，作者頁上抓不到 |
| Богослов.Ru | ✅ 通 | 神學期刊與論文 |
| ImWerden | ✅ 首頁通 | 俄文文學與哲學 PDF 典藏；`/cat/` 與 `/cat/authors.php` 都 404，目錄路徑要再找 |
| Runivers | ✅ 通 | 俄國史料掃描，95 KB／13,364 字 |
| Lib.ru | ✅ 通 | 老牌純文字庫。⚠️ **首頁是 windows-1251 不是 UTF-8**——用 utf-8 解會一個西里爾字都看不到，誤判成空頁 |
| publ.lib.ru | ✅ 通但慢 | 8.2 秒才回，掃描書目錄 |
| Азбука веры | ❌ HTTP 403 | 東正教教父全文庫，可惜——這是俄文教父學最完整的一個 |
| RusNEB 國家電子圖書館 | ❌ HTTP 403 | |
| eLIBRARY.RU | ❌ DNS 不通 | 本來就多半要帳號 |

#### 🔑 CyberLeninka 取件配方（免帳號，實測 2026-09-16）

搜尋是 **POST JSON**，不是 GET——直接 GET `/api/search` 回 405，會讓人以為端點不存在。

```python
POST https://cyberleninka.ru/api/search
     {"mode": "articles", "q": "религиозная философия", "size": 3, "from": 0}
  → {"found": 1000, "articles": [{"name": "…<b>…</b>…", "link": "/article/n/…"}]}

GET  https://cyberleninka.ru{link}          → 文章頁，含全文（實測 46,753 西里爾字）
GET  https://cyberleninka.ru{link}/pdf      → application/pdf
```

`name` 欄裡有 `<b>` 標記命中詞，入庫前要剝掉。

### 西班牙文

| 站 | 狀態 | 說明 |
|---|---|---|
| **Mercaba** | ✅ 通 | 天主教神學文獻庫，300 KB 純 HTML，直接讀得到文字。西語神學目前最實用的一個 |
| Corpus Thomisticum | ✅ 通 | 多瑪斯全集（拉丁原典，西語介面） |
| Cervantes Virtual | ⚠️ **查得到、抓不到** | 搜尋頁通（239 KB，回 `/obra/…` 連結），但**作品頁 HTTP 403**。與 Gallica 同類：能確認書在不在，不能取全文 |
| Redalyc | ⚠️ JS 殼 | 首頁 129 KB 正常，但搜尋回 5,680 B 的空殼；`/oai` 404 |
| SciELO.org | ⚠️ 擋 | 首頁通，`search.scielo.org` 403，`scielo.br/oai` 逾時 |
| Dialnet | ❌ 連不上 | 21 秒逾時。西語學術索引最大的一個，可惜 |
| Biblioteca Digital Hispánica | ❌ HTTP 403 | 西班牙國圖掃描 |
| SciELO España | ❌ 連不上 | |
| Memoria Chilena | ❌ JS 殼 | 首頁只回 434 B |

> 西語這邊的結論跟英德不同：**大平台（Dialnet／SciELO／Redalyc）反而都取不到，
> 能用的是 Mercaba 這種老派純 HTML 站。** 要系統性收西語當代學術，
> 得走 DOAB／OAPEN（已在上面的清單裡）而不是這幾個。

### 簡體中文

| 站 | 狀態 | 說明 |
|---|---|---|
| **國家哲學社會科學文獻中心**（ncpssd.org／.cn） | ⚠️ 站通、取件未通 | 官方免費 OA，期刊頁回 175 KB／3,784 漢字，但 `/ncpssd/search/index` 與 `/api/search/searchList` 都不通；全文多半仍要登入。兩個域名內容相同，回應要 17–24 秒 |
| 中華典藏 | ✅ 通 | 古籍全文，分類頁 46 KB／8,585 漢字 |
| 國學大師 | ✅ 通 | 古籍與工具書 |
| 漢典 zdic.net | ✅ 通 | 字書工具，不是全文來源 |
| 印順文教基金會 | ✅ 通 | 印順導師著作全集（本專案已另有管線） |
| CBETA 線上 | ✅ 通 | 已在管線 |
| 書格 shuge.org | ❌ HTTP 403 | 古籍高清掃描，公有領域，被擋掉很可惜 |
| 中國國家數字圖書館 nlc.cn | ❌ 連不上 | |
| 讀秀／超星 | ⚠️ 綁機構 | 首頁通但要機構帳號 |
| 中國知網 CNKI | ❌ 付費 | 首頁只回 381 B 的殼 |

> 簡中這邊**古籍豐富、當代學術幾乎全鎖**——古籍有中華典藏／國學大師／ctext，
> 當代期刊則 CNKI 付費、NCPSSD 要登入、讀秀綁機構。
> 本專案要的當代中文研究，還是走華藝（繁中）與臺大佛學數位圖書館的書目層。

### 🚨 探測站台時自己會犯的三個錯

1. **首頁 200 不等於抓得到全文。** Cervantes Virtual 搜尋頁好好的，作品頁 403；
   SciELO 首頁好好的，搜尋子網域 403。**一定要走通一次「搜尋→取件」**才算數。
2. **回 200 但只有幾百 bytes ＝ JS 殼。** CNKI 381 B、Memoria Chilena 434 B、
   Redalyc 搜尋 5,680 B，都是這種。判準：長度 ＋ 該語言的字元數。
3. **編碼猜錯會讓活站看起來像空站。** Lib.ru 首頁是 windows-1251，
   用 utf-8 解出來西里爾字數 0，差點被記成「通但沒內容」。

## 要不要帳號？（2026-09-11 實測＋已知）

分成三類。**第一類是本專案該優先用的**——不必註冊、curl 直接抓、可以寫進排程。

### A. 完全不必帳號（腳本可直接抓，適合排程）

| 站 | 說明 |
|---|---|
| **archive.org** | **下載公有領域項目不必登入**；只有「借閱館藏」（`access-restricted-item: true`）才要帳號，而那種借了也只能線上閱讀、下載不到，對管線沒用 |
| **Project Gutenberg** | 全站無門檻 |
| **Persée** | 法國國家級開放平台，全文免費 |
| **DBNL** | 荷蘭文學數位圖書館，全開放 |
| **Deutsches Textarchiv** | 全開放，且提供 TCF／XML 下載 |
| **MDZ 慕尼黑數位中心** | 全開放，有 IIIF |
| **Runeberg** | 全開放 |
| **Zeno.org** | 全開放 |
| **Wikisource（各語言）** | 全開放，有 MediaWiki API |
| **DOAB／OAPEN** | 開放取用專書，全開放 |
| **ctext 中國哲學書電子化計劃** | 讀與基本檢索免帳號；**進階功能與 API 配額要免費帳號** |
| **青空文庫** | 全開放 |

### B. 要帳號，但值得辦（一次性成本）

| 站 | 要什麼 | 換到什麼 |
|---|---|---|
| **NDL 國立國會圖書館** | 「個人向けデジタル化資料送信サービス」要**日本國內圖書館的利用者登錄**（本人須赴日或有日本住址） | 大量戰前日文書。⚠️ 但標示「インターネット公開」那一批**不必帳號**，repo 現有的內村／畔上／賀川都是走這條，已經夠用 |
| **HathiTrust** | 完整 PDF 下載要**會員館 SSO**（大學帳號）。玄奘大學若是會員館就能用 | pre-1929 全文瀏覽與整本下載。⚠️ 本機目前**連 HTTP 403 都過不去**，要先解決連線 |
| **JSTOR** | 免費帳號可讀開放取用與每月限額；完整需機構訂閱 | 期刊論文 |
| **Google Books** | 部分公有領域全覽要登入 | 與 archive.org 高度重疊，優先度低 |

### C. 綁機構 IP，不是帳號

| 站 | 說明 |
|---|---|
| **華藝 Airiti** | 下載綁**機構 IP**，不是帳號密碼。離開校園網就失效，而且**權限掉了會回 HTTP 200 的 JSON 而不是 PDF**——這一點害過我們（見 [[research-data-airiti]]） |

### 建議

**先把 A 類全部接進管線**——它們不必帳號、可排程、涵蓋十九世紀到二十世紀中葉的宗教學幾乎所有經典。
B 類裡真正值得追的是 **HathiTrust**（若玄奘是會員館），因為它補的正是 archive.org
缺的那一塊：pre-1929 的完整下載。NDL 送信服務**不必急**——本專案要的戰前日文書多半
已經在「インターネット公開」那一層。

## 清理 djvu.txt

`scripts/archive_djvu_clean.py`——接回行尾軟連字號 `¬`、收多重空格、刪頁碼與書眉。
**只做機械性清理不改字**：OCR 認錯的留著，看得見的錯遠好過被掩蓋的錯。

## 選版本

同一本書常有十幾個掃描本（蒂勒《宗教學要義》一次就搜到 20 個）。挑法：
1. 先排除借閱館藏
2. 比較虛詞命中率，挑最高的
3. **版次要寫進 manifest**——弗雷澤《金枝》有二卷本(1890)、三卷本(1900)、
   十二卷本(1906–15)、節本(1922)，版本弄錯比沒找到更糟

## See also

- [[ebook-zlib-harvest]] — 受版權那一條路（獵表＋每日排程）
- [[ebook-pipeline]] — 下載回來之後的 parse／standardize
- `scripts/pd_scholars_ingest.py` — 公有領域原著建 row 的 registry
