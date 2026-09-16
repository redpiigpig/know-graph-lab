# 電子資料庫總表

本專案實際用到的每一個外部資料來源，一處記全。**「有沒有收過這個庫」這個問題
應該在這裡就能回答**，不必翻十個 SKILL.md。

三張表：**已接管線**（有腳本、有資料落地）／**已確認可用但還沒接**／**試過不能用**。
只確認連通性、還沒走通取件路徑的免費全文站，另見
[free_text_sources.md](../.claude/skills/ebook-collected-works/free_text_sources.md)，
那份記的是「哪裡有」與怎麼取；這一份記的是「我們收了什麼」。

> 規模數字的時間點是 2026-09-16。會動的（華藝、z-lib、J-Stage）另見
> `python scripts/watch_pipelines.py` 與 `--status` 各支。

## 一、已接管線

### 原典・大藏經

| 來源 | 收了什麼 | 規模 | 腳本 |
|---|---|---|---|
| **CBETA** TEI P5 | 大正藏／卍續藏／漢譯南傳全文 | 3,784 部・1.85 億字 | `tripitaka_cbeta.py` |
| **Esukhia／OpenPecha** 德格版甘珠爾 TEI | 藏文大藏經佛說部全帙 | 1,124 部・9,695 萬藏文字 | `tripitaka_derge.py` |
| **84000** Linked Open Data（CC0） | 甘珠爾的梵／英題名與英譯者 | 1,254 RDF | `tripitaka_derge_titles.py` |
| **東北大學**西藏大藏經資料庫 | 甘珠爾的漢譯對照（SAT 經號） | 447／1,124 部 | `tripitaka_derge_zh.py` |
| **SuttaCentral** | 平行經目＋巴利原典逐段 | 23,321 筆・20 部 | `tripitaka_parallels.py` |
| **GRETIL** | 梵文原典 | 12 部 | `tripitaka_sanskrit.py` |
| **DILA 佛學規範**＋佛光大辭典等 | 佛學辭典 | 13 部・13.5 萬條 | `fgs_dictionary_ingest.py` |

### 期刊・書目

| 來源 | 收了什麼 | 規模 | 腳本 |
|---|---|---|---|
| **華藝 Airiti** | 繁中宗教／神學／佛學期刊全文 | 32 刊・篇目 18,505・全文 3,841 | `press_airiti.py` |
| **臺大佛學數位圖書館** | 佛學書目（無全文） | **526,829 筆** | `ntu_dlmbs_harvest.py` |
| **Crossref** | 宗教學期刊 metadata | 822 刊・452,459 篇 | `crossref_harvest.py` |
| **DOAJ** | OA 期刊 | — | `doaj_harvest.py` |
| **J-Stage**《印度學佛教學研究》 | 日文佛學論文 | 篇目 14,747・PDF 1,393 | `jstage_ibk_harvest.py` |
| **CyberLeninka** | 俄文 OA 宗教／神學／哲學／史 | 2026-09-16 新接 | `cyberleninka_harvest.py` |

### 刊物典藏

| 來源 | 收了什麼 | 規模 | 腳本／說明 |
|---|---|---|---|
| **佛教弘誓學院**官網 | 弘誓雙月刊・學團日誌・電子報・學術活動 | 117 期＋173＋14＋24 | `hongshi_*`、`hongshi_pdf_text.py` |
| **玄奘大學** | 玄奘佛學研究學報・法印學報 | 304＋30 | 同上 |
| **妙心寺** | 妙心雜誌 | 844 篇 | 同上 |
| **福嚴佛學院** | 福嚴會訊 | 71 期 | 同上 |
| 台灣教會公報／新使者／論壇報等 | 長老教會與福音派刊物 | 見 `research-data-christianity` | |
| **thereformedcatholic.org**（TRC） | 改革宗／新教檔案 | 2,761 部 | `ebook-trc-archive` |
| **ziliaozhan.win** 天主教在線 | 天主教文獻 | 71 部 | 同上 |

### 電子書・典藏

| 來源 | 收了什麼 | 說明 |
|---|---|---|
| **z-library** | 受版權當代專書 | 獵表 6,173 筆，`zlib_fetch.mjs`＋每日排程 |
| **archive.org** | 公有領域掃描與 DjVuTXT | `archive_org_fetch.py`、`archive_djvu*.py` |
| **Project Gutenberg** | 公有領域純文字／EPUB | gutendex API |
| **NDL 國立國會圖書館** | 日文戰前（インターネット公開層） | `ndl_*.py` |
| **青空文庫** | 日文公有領域 | 內村鑑三那條線 |
| **libgen.li** | 受版權 | PowerShell IWR，別讓檔案落地 |

### 檔案

| 來源 | 收了什麼 | 腳本 |
|---|---|---|
| **檔案管理局**國家檔案 | 一貫道相關卷宗 | `archives_gov.py`、`archives_images.py` |
| **國史館** | 同上 | `archives_guoshiguan.py` |

## 二、已確認可用、還沒接管線

連得到、也知道怎麼取，只是還沒寫腳本。優先度由上而下。

| 來源 | 語言 | 為什麼值得接 |
|---|---|---|
| **DOAB／OAPEN** | 多語 | 當代學術專書的開放取用版，**當代宗教學唯一的合法免費路** |
| **Deutsches Textarchiv** | 德 | 1900 年前德文的人工校對轉錄，OCR 品質勝過 archive.org |
| **Persée** | 法 | 法國人文社科期刊全文，含《社會學年鑑》 |
| **DBNL** | 荷 | 蒂勒、尚特皮、克里斯滕森、范德列烏都是荷蘭人 |
| **Runeberg** | 北歐 | 瑟德布盧姆；且常是德譯本的乾淨母本 |
| **MDZ 慕尼黑數位中心** | 德 | 德文掃描，有 IIIF |
| **Zeno.org** | 德 | 德文哲學／文學全文 |
| **Mercaba** | 西 | 西語天主教神學文獻，純 HTML |
| **中華典藏／國學大師** | 簡中 | 古籍全文 |
| **ctext** | 中 | 漢籍（讀與基本檢索免帳號） |
| **Wikisource**（各語言） | 多語 | 本身的全文，以及**指向 archive.org 掃描本的 identifier** |

## 三、試過不能用

別再試一次。

| 來源 | 症狀 | 備註 |
|---|---|---|
| **IxTheo** | 17-bit SHA-256 PoW 驗證 | 刻意的反爬控制，不繞。改用 Crossref |
| **HathiTrust** | HTTP 403 | 完整下載本來就要會員館 SSO |
| **Anna's Archive** | DNS 解析失敗 | |
| **OpenEdition Books** | HTTP 500 | 法語人文社科 OA，可惜 |
| **Dialnet** | 連線逾時（21 秒） | 西語最大學術索引，可惜 |
| **Азбука веры** | HTTP 403 | 俄文教父學最完整的一個，可惜 |
| **RusNEB** 俄國家電子圖書館 | HTTP 403 | |
| **書格 shuge.org** | HTTP 403 | 古籍高清掃描，公有領域卻擋 |
| **中國國家數字圖書館** nlc.cn | 連不上 | |
| **SciELO** 搜尋子網域 | HTTP 403；OAI 逾時 | 首頁通但取不到件 |
| **Redalyc** | 搜尋是 JS 殼；`/oai` 404 | |
| **Biblioteca Digital Hispánica** | HTTP 403 | |
| **Cervantes Virtual** | 搜尋通、**作品頁 403** | 與 Gallica 同類：查得到、抓不到 |
| **Gallica** | SRU 檢索可用、`.texteBrut` 被擋 | 能確認 ark，不能取全文 |
| **CNKI／讀秀／超星** | 付費或綁機構 | |
| **NCPSSD** 國家哲社文獻中心 | 站通、搜尋端點不通、全文要登入 | |
| **eLIBRARY.RU** | DNS 不通 | 本來也多半要帳號 |

## 四、取件時反覆踩到的坑

跨來源共通的那幾個，每一個都會讓失敗看起來像成功：

1. **首頁 200 不等於抓得到全文。** 一定要走通一次「搜尋→取件」才算數。
2. **回 200 但只有幾百 bytes ＝ JS 殼。** 判準是長度＋該語言的字元數。
3. **編碼猜錯會讓活站看起來像空站。** Lib.ru 是 windows-1251，用 utf-8 解西里爾字數為 0。
4. **API 回的「總數」可能是假的。** CyberLeninka 的 `found` 永遠是 1000；
   PostgREST 不帶 limit 靜默截在 1000。拿它當分母就會謊報收齊了。
5. **有些 API 永遠不會說「沒有了」。** CyberLeninka 翻到 3000 還在吐，
   但相關度早就崩了——停止條件要用相關度不是用「抓完」。
6. **抽出來的字要驗是不是真的。** 虛詞密度低於每萬字 80 就有問題
   （見 `archive_djvu_clean.py --check`）。
7. **獵表是願望清單不是庫存清單。** 定期跑 `zlib_retire_owned.py` 跟館藏對帳。

## See also

- [free_text_sources.md](../.claude/skills/ebook-collected-works/free_text_sources.md)
  —— 各站的**取件路徑**與坑，以及「一本書找不到時的分流順序」
- `scripts/watch_pipelines.py` —— 三條每日管線的即時對帳
- [r2-policy.md](r2-policy.md) —— 收回來的東西放哪（Drive 正本／R2 小衍生物）
