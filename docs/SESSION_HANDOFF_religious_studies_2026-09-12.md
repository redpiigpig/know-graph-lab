# 交接：宗教學者全集取源（2026-09-11 → 09-12）

使用者定調：**宗教學者的著作優先做**，從伊利亞德、韋伯、涂爾幹、奧托開始，
之後擴到 `/collected-works` 的「宗教學」17 位＋「宗教社會學」15 位共 32 位。
「都先找齊，之後再慢慢翻譯與修」——**這一輪只做取源與上架，不翻譯**。

## 已完成（交接時的狀態）

全集 **456 → 532 本**。一天內新上架 **74 本原著、約 2,900 萬字，零 z-lib 額度**
——全部來自 archive.org 與 Project Gutenberg。

| 學者 | 本數 | 備註 |
|---|---:|---|
| 弗雷澤 | 26 | 《金枝》四版二十一卷全收（初版二卷／二版三卷／三版十二卷／1922 節本） |
| 瓦赫 | 7 | 《理解》三卷照套書規矩拆成三筆 |
| 哈里森 | 7 | |
| 羅伯遜‧史密斯 | 7 | 《閃族宗教講座》初版與二版並存 |
| 齊美爾 | 6 | |
| 涂爾幹 | 4 | 《社會分工論》法文 1893 初版 |
| 奧托 | 4 | 從 0 本開始；《論「聖」》德文 14 版 |
| 瑟德布盧姆 | 4 | 含 1914 瑞典文原著 |
| 特洛爾奇 | 4 | |
| 泰勒 | 3 | ⚠️ 未上 hub，見「待辦 5」 |
| 范德列烏 | 2 | 德文原著＋英譯 |

基礎建設也留下來了，**新 session 直接用，不要重寫**：

* `scripts/archive_djvu_clean.py` —— djvu.txt 清理 ＋ `--check LANG` OCR 品質閘
* `scripts/pd_scholars_ingest.py` —— 讀 `data/pd-scholars/*.jsonl` 建 ebook row
* `scripts/classical_scholars_place.py` —— 清理＋放 Drive＋產 registry
* `scripts/pd_scholars_wire_hub.py` —— 接 hub（**先比對既有條目再決定接或新增**）
* `.claude/skills/ebook-collected-works/free_text_sources.md` —— 十八個免費全文站的實測結果

---

## 待辦（按使用者指定的優先序）

### 1. 昭慧法師兩本：OCR 完成但沒上架 ⭐ 使用者最近一次問的就是這個

| 書 | OCR | 站上 |
|---|---|---|
| 心靈的交會：山間對話 | ✅ 255/255（`c:/tmp/chaohwei/ocr2`） | ⚠️ **是舊的 v1** |
| 初期唯識思想——瑜伽行派形成之脈絡 | ✅ 300/300（`c:/tmp/chaohwei_vijnapti/ocr`） | 🚨 **完全沒上架** |

**心靈的交會**：站上那筆 13 段／114,647 字結構是對的（13 場對話、`〔辛格〕〔昭慧〕`
標記正確、頁碼是真的印刷頁 59/79/99），但 **v2 重跑的目的是補腳註，而站上那版
腳註標記是 0**（v2 快取有 64 個）。要重 build 取代。

**初期唯識思想**：300 頁 15.9 萬字全在快取，DB 查無此書，hub 也沒有條目。

**先修這兩個缺陷再 build：**

1. 🚨 **逗號半形／全形混用**——初期唯識 **60% 是半形**（4,715 半形 vs 3,175 全形）、
   心靈的交會 47%。實例：`唯識學用不同術語,將緣起做了` 與 `(一)識緣名色`。
   這是模型輸出的標點正規化問題，**不是原書排版**，中文要全形。
2. 印刷頁碼 280/300 與 233/255 有值（91–93%），缺的多在章首頁（照慣例不印書眉，
   可由鄰頁遞推——`howes_build.fill_folios()` 有現成作法）。
   心靈的交會前言的字母頁碼抓成 `a, b, C, d`，那個 `C` 應為 `c`。

**腳註品質實際很好**，別動它：`[^1]` 標記與註文都在，大正藏引註帶卷數頁欄
（`(大正二九・一五九上)`）。全書 299 個腳註標記。

流程見 [[ebook-scan-transcribe]] 與 `chaohwei_collected_works.md`。

### 2. drop 夾 12 本待 ingest

`python scripts/ingest_new_books.py status` 看得到。其中幾本直接補 hub 缺口：

* **不死与自由：瑜伽实践的西方阐释** —— 伊利亞德 hub 上這本到現在還掛 `copyright` 無來源
* 神圣与世俗 ／ 萨满教 古老的入迷术 —— 伊利亞德
* The meaning and end of religion（W.C. Smith）—— **他本身就是那 32 位之一**
* Likeness and Presence（Belting）、臺灣天主教史研究論集、敦煌俗字典 —— 本學期講義用書
* Totalité et infini（Levinas）—— 《神學研究宣言》
* Bhikkhuni Ordination（Analayo）—— 八敬法

這批命中今早重排的優先序，是重排有效的證據。

### 3. 兩份獵表還沒裝進排程

| 檔 | 條數 | 內容 |
|---|---:|---|
| `c:/tmp/pd_sources/socrel_wanted.jsonl` | 137 | 當代宗教社會學 13 位 |
| `c:/tmp/pd_sources/classical2_wanted.jsonl` | 6 | 古典期找不到的 |

裝法：複製到 `data/zlib-wanted/`，在 `scripts/zlib_wanted.py` 的 `PRIORITY` 加一層
（宗教學者相關目前都在層 12），跑一次 `python scripts/zlib_wanted.py`。

🚨 **socrel 那份有兩個勘誤要保留**：
* 多尼格 *The Hindus* **沒有中譯本**——《印度：一部歷史》是 John Keay 的書，別搞混
* 斯塔克 *The Triumph of Christianity* 中譯是《社会学家笔下的基督教史》，**書名與原題完全不同**，自行直譯必定落空

### 4. 四位新學者只做了一半

使用者批准補的是宗教現象學的斷層——范德列烏的前輩與老師：

| 學者 | 狀態 |
|---|---|
| **C.P. 蒂勒**（1830–1902） | 🔎 來源已找到未下載。archive.org：`elementsofthesci01tieluoft`（Elements of the Science of Religion 1897）、`outlinesofthehi00tieluoft`（Outlines 1888）、`geschichtederrel02tieluoft`（德文 1896）、`einleitungindie00gehrgoog`（Einleitung in die Religionswissenschaft 1899） |
| **尚特皮‧德拉索塞**（1848–1920） | 🔎 同上。`lehrbuchderreli00sausgoog`（Lehrbuch der Religionsgeschichte 1905）、`manualofscienceo00chan`（英譯 1891）、`MN40163ucmf_1`（1887 初版 microform）、`vierschetsenuitd00chan`（**荷蘭文** 1883） |
| **W.B. 克里斯滕森**（1867–1953） | ✗ archive.org 查無。要走 **DBNL**（荷蘭文學數位圖書館，首頁通得到、免帳號） |
| **姉崎正治**（1873–1949） | ⏳ 未動。走 NDL，repo 已有 `scripts/ndl_author_survey.py`。🚨 NDL 對舊字體／新字體敏感，查不到不會報錯就回 0 筆，兩種字形都要查 |

這四位在 store 裡**還沒有 hub**，要先建。

### 5. 三本英文原著該上 hub 了——我先前排除的理由已證實不成立

| ebook_id | 書 | 段 |
|---|---|---:|
| `e7541832-0000-4000-8000-000000000001` | 泰勒《原始文化（卷一）》 | 349 |
| `e7541832-0000-4000-8000-000000000002` | 泰勒《原始文化（卷二）》 | 339 |
| `f4a21854-0000-4000-8000-000000000018` | 弗雷澤《金枝（一卷節本）》 | 743 |

我原本把它們列進 `pd_scholars_wire_hub.py` 的 `SKIP`，理由是「站上已有帶內容的中譯，
接上去會變成兩個《原始文化》」。**那個理由錯了**——見下方「我做錯的事」。
既有的那兩筆本來就是完整的中英對照，這三本是**獨立的版本**（初版／第四版／1922 節本），
不衝突，應該正常上架。把它們從 `SKIP` 拿掉重跑即可。

### 6. 佇列裡 1,421 筆結構上幾乎注定落空的條目

診斷完成、**未修**。那些條目 `lang: "zh"`（要找中譯本）但 `query` 是英文書名，
而 `zlib_fetch.rank()` 的語言閘 `if (wantLang === 'zh' && !lang.includes('chinese')) return -100`
會把搜回來的英文書全部擋掉。佔佇列 **23%**，每輪都在燒搜尋次數。

實測 17 次只成功 2 次（11.8%），而那 2 次裡：
* 1 次是真的（《宗教經驗種種》，因為那個中譯版在 z-lib 上的書名**同時掛著英文原題**）
* 1 次是垃圾（`who='Tu'` 杜維明配空 `expect`，抓回《十天突破雅思寫作》——那本已不在庫裡）

產生器是 `scripts/zlib_wanted_from_bibliography.py` 第 374 行附近。
**修法要先問使用者**：是拿掉這些條目，還是保留但降權。

### 7. 三本 Fraktur 待重 OCR

| 書 | 檔 |
|---|---|
| 奧托《康德-弗里斯學派的宗教哲學》1909 | `全集/宗教學/奧托/…[Fraktur 待重OCR].pdf` |
| 瑟德布盧姆《神信仰的生成》1916 | `c:/tmp/pd_sources/classical2/soderblom_werden-des-gottesglaubens_de_1916_FRAKTUR.pdf` |
| 瑟德布盧姆《地上諸宗教》1906 | 同夾 `…die-religionen-der-erde_de_1906_FRAKTUR.pdf` |

走 Gemini Vision。**但瑟德布盧姆那本有更快的路**：1916 德文本的母本就是
1914 瑞典文《Gudstrons uppkomst》，而**瑞典文掃描本 OCR 乾淨**（每萬字 127.7）、已上架。

### 8. 這 74 本全都還沒翻譯

主欄現在是原文。翻譯走 [[ebook-translate]] 的 `--engine auto`
（Gemini → NVIDIA → Haiku）。使用者說「之後再慢慢翻譯與修」，**不急**。

### 9. 名單擴充只批准了四位

我提過宗教學名單有四個結構性的洞，使用者只點頭補了現象學那一支的三位＋姉崎：

* **宗教人類學整支缺席**：紀爾茲、維克多‧特納、坦比亞、薩巴‧馬哈茂德
* **「宗教」範疇批判／後殖民**：增澤托莫科、理查‧金、布魯斯‧林肯、薩伊德
* **認知宗教學完全空白**：博耶、阿特蘭、懷特豪斯
* **非西方學統薄、女性僅 4/32**：楊慶堃、李亦園、法茲盧爾‧拉赫曼、瑞塔‧格羅斯…

要不要做由使用者決定。

---

## 🚨 我做錯的事，新 session 別重蹈

### 查「有沒有原文欄」要看 JSONL，不是看 DB

我要替泰勒《原始文化（英繁對照）》補英文原文欄。查 DB 的 `ebook_chunks`，
`source_text` 全是空的，於是判定「有中譯沒原文」，寫了章級比例分配把英文塞進去，
680 段全填、覆蓋率 99.6%，**數字很漂亮**。

**但 DB 從來不存 `source_text`。**它只存 `content` 的 200 字 preview，
全文正本一律在 `_chunks/{id}.jsonl`。那本書的 JSONL 裡本來就有 682 段
**逐段對齊好的**英文，我蓋掉了 675 段。

比對之後看得很清楚，原本的比我的好：

```
#343 中文 ：註腳 782：Hardy《佛教手冊》第 291、443 頁…
     原英文：Cross in 'Journ. Amer. Oriental Soc.' vol. iv. p. 309. …   ← 腳註對腳註
     我寫的：Having thus surveyed at large the theory of spirits…      ← 不相干的正文
```

**已全量還原**（從 `sources.en` 救回 680 段）。救得回來是因為多語 schema 把各語言
另存在 `sources[lang]`，而我的腳本沒動那一欄。

防線已寫進 `scripts/merge_original_column.py`：動手前先數有沒有原文欄，有就擋下退出。

**順帶的真實收穫**：泰勒與弗雷澤這兩本的 Drive `_chunks` 副本本來就不見了、只剩 R2。
Drive 才是 canonical，現在補回去了。**其他書可能也有同樣情形，值得全庫掃一次。**

### 比例分配對齊會漂移，別拿它當段級對照

中文側的「段」是標準化時**按長度切的塊、不是段落**，兩邊沒有段落對應關係可還原。
章開頭對得上，章中段必漂一到三段。要做逐段對照只能靠真正的錨點（段碼、頁碼），
沒有錨點就照 [[ebook-collected-works]] §B1-3 第四級「分欄不分段」。

### archive.org 三個會讓人誤判成功的陷阱

1. **借閱館藏搜得到下載不到**——每筆候選都要查 `archive.org/metadata/{id}` 的
   `access-restricted-item`
2. **掃描件的 EPUB 常常只有頁面影像沒有文字層**——一律改用 `DjVuTXT`
   （Gutenberg 的 EPUB 是真的，可放心用）
3. **OCR 可能整本是廢的而檔案大小完全正常**——`archive_djvu_clean.py --check LANG`

### 🚨 虛詞比值會漏掉 Fraktur 的「半中鏢」

瑟德布盧姆《Das Werden des Gottesglaubens》(1916) 四詞比值 **139.9 完全合格**，
但 `ist` 全書只出現 **2** 次、`ift`+`ijt` 有 **934** 次——Fraktur 的長 s（ſ）被讀成
f／j，而 `und`／`der`／`die` **剛好都不含長 s**，三個讀對就把第四個的崩塌平均掉了。
`quality()` 已內建這道檢查，德文一定要跑。

### 投遞點的 schema 不一致會靜默毀掉整份清單

`data/zlib-wanted/` 是多條線共用的投遞點，一天內被丟進兩份書目格式的檔，
`load_curated` 兩次 `KeyError`。而 `zlib_daily.ps1` 是 `ErrorActionPreference=Continue`，
**清單沒刷新它照樣往下跑，當天用舊清單抓，數字全是對的**。已改成跳過並印警告。

---

## 順便：z-lib 每天四十本已經修好了

2026-09-11 實測：四個帳號全部跑到（`fetch exit=0` ×4）、探勘跑了 120 筆、當天下載 12 本。
修的是四件事——`gotoPastWall` 未捕捉例外會帶走整輪、`download-failed` 被誤當已處理
（累計燒掉 8 本）、排程 `DisallowStartIfOnBatteries=True` 沒插電整班不跑、
`--max-tries` 跟著下載目標走而不是跟著命中率走。

班表 `09:30 / 14:30 / 20:30`，目標是**今天累計**四十本，湊滿就直接結束。
