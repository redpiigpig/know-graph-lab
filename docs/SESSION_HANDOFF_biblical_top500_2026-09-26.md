# 交接：聖經學者三組全集＋五百篇文獻回顧＋一貫道兩位老師論文（2026-09-26）

給下一個 session 或使用者接手用。同日相關 commit：70d2b891 → eac43e32 → 05799e90 → 1e995933 → 1b30d5e2（皆已在 origin/master）。

## 一、緣起

使用者 2026-09-14 點名要「舊約十位／新約十位／次經與典外文獻十位」聖經學者全集，和「近現代前 500 篇最重要的相關論文」。
09-26 問「完工了嗎」→ 盤點發現三處各做一半（hub 只有骨架、書在 Drive 沒上站、典外組沒 hub、500 篇從未起稿）→ 當天補做。
使用者同時裁示：**「抓 N 篇最有影響力研究」以後是常規用法、其他領域也會用** → 做成通用流程並寫 skill。

## 二、做完的東西與位置

### 1. /collected-works「基督宗教研究」hub
- 四小節 54 位：新約研究 15／舊約研究 13／**次經與典外文獻 12**（新增 11 位＋帕格爾斯自教會史移入）／教會史 14。
- 資料在 `stores/collectedWorks.ts`；`ERA_ORDER` 在 `pages/collected-works/index.vue`。
- 肖像 41 位已填（私人站不限公有領域，來源 Commons／維基 infobox／任教大學官網，逐一驗過 200 且是本人）。
  13 位維基無單人照留 emoji：Dodd、Jeremias、Käsemann、Eichrodt、von Rad、Noth、Bright、Childs、Latourette、Bainton、Frend、Henry Chadwick、Schneemelcher。
- 著作 184＋52 部全是 `copyright`／`planned`，**零部可讀**——hub 是人不是全集，轉錄要另外排。

### 2. 書：獵表與原著
- z-lib 獵表 `data/zlib-wanted/biblical-studies.jsonl` 67 筆：有書 37（全在 ebooks 表且 parsed）；probe-miss 19；dry 11。
  壞命中已知：Astruc 那筆抓到 Jarick 編的論文集；Hengel 作者欄 z-lib 拼成 "Hegel"（DB 已改正）。
- 聖經批判史 16 本原著（Spinoza 英譯、Simon、Astruc、Reimarus、Eichhorn 3 卷、Semler 4 卷、de Wette、Strauss 英譯 2 卷、Baur 英譯 2 卷）
  由 `scripts/archive_org_fetch.py` 入館 `電子圖書館\神學\聖經批判史\`，全部 parsed。bsb／goog 結尾的 identifier 改抓 djvu.txt。
- 待審分類裡的史懷哲／R. 布朗／鄧恩三本已歸神學夾；Bultmann《符類福音傳統史》重複本已刪（保留 Revised ed）。

### 3. 五百篇文獻回顧（通用流程首例）
- 頁面 `/research-data/top-papers/biblical-studies`，`/research-data` 首頁有卡。
- 資料 `data/research-data/biblical-studies/`：`top-papers.config.json` ＋ 四個 jsonl（ot 139／nt 134／apoc 128／crit 135 ＝ 536 筆）。
  每組依研究史分主題、每筆一句話說它為何重要。使用者在三種選法裡選了「分組依研究史策展」，不是引用數。
- 建置 `python -X utf8 scripts/top_papers_build.py biblical-studies`：Crossref 逐筆核對（候選快取在 `output/top-papers/`，`pick()` 挑；
  🚨 第一版把書評 DOI 當原著命中 328 筆，加「非書評、專著只認 book 類型」兩閘後剩 112，抽查全對）＋館藏比對。
- 產物 `public/content/research-data/biblical-studies/top-papers.json`（進版控）。
- 方法全文：`.claude/skills/research-data-top-papers/SKILL.md`。換領域只加 `data/research-data/<field>/`，腳本與頁面不用改。

### 4. 五百篇的「拿到」進度
| 路徑 | 結果 |
|---|---|
| Unpaywall（112 DOI） | 4 筆 OA，只 1 筆真 PDF（賴特 1978，已入館並解析） |
| 校內 IP 走 doi.org（curl） | 劍橋要付費、SAGE／OUP／JSTOR 403、de Gruyter 驗證頁 |
| 校內 IP 用真 Chrome（`scripts/doi_browser_fetch.mjs`，6 篇） | T&F／Brill／SAGE／芝加哥 4 篇「Get access／purchase」＝**校方沒訂**，不是被擋 |
| archive.org（`scripts/top_papers_archive_org.py`，497 筆） | **55 本整本入館**（`電子圖書館\神學\聖經研究五百篇\`，全 parsed）、216 本借閱制跳過 |
| z-lib 獵表 `data/zlib-wanted/biblical-top500.jsonl` | 專著 384 筆併入（source 沿用 biblical-studies 優先序 20），對帳後佇列剩 331，每日排程慢慢抓 |
| 論文與專章 102 筆 | Drive `電子圖書館\神學\聖經研究五百篇\待下載_期刊論文與專章（校內圖書館用）.csv`（52 筆有 DOI 連結） |

清單「館內已有」：38 → 88。

### 5. 一貫道：鍾雲鶯、楊弘任（楊老師＝中研院社會所楊弘任）
- 新腳本 `scripts/airiti_author_fetch.py 作者 [--download --dest 專案夾]`：華藝按作者檢索。
  🚨 JSON 的 `查詢歷史類型代碼` 要 `"ADLang"`（寫 DSF 回一頁正常的「查無資料」）；欄位代碼是數字（作者=2）；
  publisherID 要讀刊物頁 JS 變數 `全域_出版單位代碼`，不一定是數字。
- 鍾雲鶯 28 篇→27 有全文；楊弘任 9 篇→6 有全文（《台灣社會學》兩篇華藝無全文、博論不走這條）。
- 篇目 `public/content/research-data/press/airiti-authors/<作者>.json`；PDF 全在 `研究資料\一貫道\`（33 篇，檔名「作者_篇名_刊名卷期年」；早先按刊抓的 11 篇在各刊夾另留一份）；
  `研究資料\一貫道\既有資料盤點.md` 已附逐篇清單。
- 華藝當日額度用了 42／1,200。

### 6. 盤點與記憶
- `docs/holdings.md` 已重跑（ebooks 5,695）。
- 記憶：`project_biblical_scholars_collected_works`、`feedback_airiti_author_search_adlang`、`feedback_bash_heredoc_eats_backslash`（追記：`python -c '…'` 也會吃反斜線，`\b` 變 0x08，只能用 `chr(92)` 拼）。
- Skill 已同步：ebook-collected-works、ebook-zlib-harvest、research-data-airiti、research-data-yiguandao、research-data-top-papers。

## 三、還沒做／可接的

1. **hub 著作轉錄**：54 位學者 236 部全是骨架。館內已有原檔的（37＋16＋55）可以先掛 `ebookId` 讓 hub 能點進去讀——要寫一支「hub 著作 ↔ ebooks 表」的對帳補標腳本，目前沒有。
2. **五百篇論文 102 筆**：校內拿不到，等其他來源（z-lib articles 線、弘誓典藏、使用者手動）。
3. **13 位無肖像**：要就得去出版社／訃聞頁找，維基沒有。
4. **一貫道後續**：鍾老師引用書目裡的期刊論文（王見川、林榮澤…）可用同一支腳本按篇名對華藝；使用者在校時額度充裕。
5. **其他領域的 N 篇清單**：照 skill 步驟，先跟使用者定分組與筆數，自己寫 jsonl（別派 agent），跑 build，加卡。

## 四、今天踩的坑（全部已記進 skill／記憶）

- `holdings_inventory.py --find 作者姓` 的「站上書名」只比書名不比作者→回假 0；查館藏走 DB。
- Crossref 對專著回書評 DOI，題名一模一樣，看起來全對。
- 華藝 `"DSF"` 查詢回 HTTP 200 的「查無資料」頁；`publisherID=(\d+)` 會漏一半的刊。
- heredoc 與 `python -c` 都吃反斜線；`\b` 進檔案成退格字元，`ast.parse` 照樣過。
- 校內 IP 對出版社：腳本 403 不代表沒權限，真 Chrome 顯示「purchase」才是沒訂——兩個都要試過才知道是哪一種。
- 前一個 session 結束會把背景任務一起帶走（archive.org 掃描做到 299/497）；有快取的腳本重跑會接著做，所以長任務一律要有快取。
- 🚨 **檔案歸位**（使用者當天糾正）：我一度把兩位老師的論文放進新開的 `華藝期刊全文\_作者專輯\`、五百篇的 CSV 放進新開的 `研究資料\聖經研究五百篇\`。
  Drive 本來就有對應夾，已全部併回（一貫道 → `研究資料\一貫道\`；五百篇 → `電子圖書館\神學\聖經研究五百篇\`），兩個新夾已刪。
  腳本現在 `--download` 必須給 `--dest 既有專案夾`，夾不存在就停。動手前先 `ls` Drive 對應層，別新開。
