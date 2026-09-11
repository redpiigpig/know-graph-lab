# 免費全文來源清單（2026-09-11 從本機實測）

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
