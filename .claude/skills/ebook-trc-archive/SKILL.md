---
name: ebook-trc-archive
description: 把中文基督宗教檔案站系統性收進本專案 —— **兩邊平行收**：①檔案本身入電子圖書館（Drive 正本→轉錄→reader 可讀）②書目條目入《基督教大藏經》(時代×藏×正/外)。目前兩個來源：thereformedcatholic.org（TRC，改革宗／新教，已收 2,761 部）與 ziliaozhan.win（天主教在線，已收 71 部）。含站點 API、逐檔限速下載規矩、簡→繁轉換、書目比對與大藏經分類器的接法。Use when 要抓／續抓任一站的某個分類、要把書目歸入大藏經、要處理巢狀作品集結構、要新增第三個來源站，或使用者提到「改革宗那個下載站」「thereformedcatholic」「天主教在線」「資料站」。
---

# 中文基督宗教檔案站收錄

> **授權**：使用者已就 TRC（2026-08-24）與 ziliaozhan（2026-08-29）分別取得站方授權作**私人收藏**。新增第三個站前先確認授權。
> **🚨 一次一個檔、檔與檔之間留間隔，絕不並發、絕不整批抓。** 使用者明確要求。

## 現況（2026-08-30）

| | 電子圖書館 | 大藏經候選 |
|---|---:|---:|
| TRC 改革宗檔案站 | **2,761 部** | 56 部 |
| 天主教在線 ziliaozhan | **71 部** | 115 部 |
| 合計 | **2,832 部** | 待審 **170 部** |

待審提案：`data/dazangjing/source-catalog/PROPOSAL_2026-08-28.md`（**尚未入庫**）。
分類 ledger：同目錄 `classified-records-trc.jsonl` / `-zlz.jsonl`。

---

## 站點一：TRC（thereformedcatholic.org）

AList 檔案站，前端掛 `/download`：

```
POST https://thereformedcatholic.org/download/api/fs/list
{"path": "/", "password": "", "page": 1, "per_page": 1000, "refresh": false}
```

- 🚨 **base_path 是 `/download`**。直接打 `/api/fs/list` 會回 **WordPress 的 404 頁（HTTP 200 + HTML）**，看起來像成功。判斷：`Content-Type` 是不是 `application/json`。
- 後端是 **OneDrive 個人版 CDN**。下載不吃站方頻寬，列目錄的 metadata 呼叫會。
- `fs/get` 拿 `raw_url`，簽章有時效，**每檔臨下載前才要**，不可預取。

### 全站結構

44,994 檔／676 GB，但**體積與書目完全脫鉤**：影音 573 GB（**85%，不收**）、文字語料僅 92.8 GB／17,054 檔（收斂為 5,109 部作品）。三個 200 GB 級分類（長老宗／改革宗／路德宗）幾乎全是當代華人教會的講道錄影。

🚨 **站方分類軸不可沿用**：安立甘底下叫「CofE **1844年墜落後**認信派」；**「異端 Heresy」底下放著約翰衛斯理、查理衛斯理、芬尼**。只當來源標記，一律中性重歸（衛斯理→衛理宗、芬尼→美國復興運動、史威登堡→世界宗教）。

---

## 站點二：天主教在線（ziliaozhan.win）

1,957 筆。網址 `/download/pdf/{分類}/{yyyy-mm-dd}/{id}.html`，分頁 `/download/pdf/index_{2..79}.html`。
十分類：wenxian 文獻／shenxue 神學／zhexue 哲學／yanjiu 研究／shengjing 聖經／lishi 歷史／zhuanji 傳記／lingxiu 靈修／cidian 辭典／qita 其他。

**三段式下載**（帝國 CMS DownSys），`pass` 每次現算不可預取：
```
① 條目頁 → classid 與 id
② /e/DownSys/DownSoft/?classid=&id=&pathid=0  → 中介頁，內含 pass
③ /e/DownSys/doaction.php?...&pass=...        → 302 轉 dl.ziliaozhan.win
```

**條目頁有「圖書簡介」欄位**（作者／出版方／成書脈絡）。🚨 抓它要**先剝 HTML 標籤再比對**——`图书简介：` 與內容之間隔著標籤，直接對 raw HTML 下 regex 抓到空字串。這欄對分類器極重要（見下）。

---

## 兩邊平行收

| | 收什麼 | 去哪 |
|---|---|---|
| **電子圖書館** | 檔案本身 | Drive `{category}/{sub}/` → `trc_ingest.py` → reader |
| **基督教大藏經** | 書目條目 | `data/dazangjing/{era}.ts` 的 `DazangWork` |

Drive 落點（已建）：`神學/` 下 教父原典・信條與教理問答・聖經與神學辭典・天主教文獻・長老宗・公理宗與清教徒・安立甘宗・改革宗・路德宗・荷蘭改革宗・衛理宗・美國復興運動・詩歌與聖詩・其他改革宗資料；另 `世界宗教/羅馬公教`、`世界宗教/史威登堡傳統`、`文學/基督宗教作家`。

---

## 腳本

```
trc_catalog.py    全站普查 → c:/tmp/trc_catalog.json
trc_records.py    檔 → 作品層彙整 → 分類器 records
trc_fetch.py      逐檔限速下載（8 秒間隔，序列式，刻意無並發選項）
trc_ingest.py     內容特徵去重 → 命名 → Drive → 登錄 ebooks    ← 兩站共用
zlz_catalog.py    天主教在線書目普查（只讀目錄頁）
zlz_match.py      書目 × 大藏經 比對 → 交集／缺口
zlz_fetch.py      天主教在線逐檔下載
dazangjing_proposal.py  分類 ledger → 待審提案（Markdown + .ts 片段）
ocr_overnight.py  整夜 OCR 看守（先探活、無進度即停）
```

### 🚨 兩站共用的硬規矩

**下載帳本**（`c:/tmp/trc_downloaded.json`、`zlz_downloaded.json`）以**站內路徑**為鍵。不能只看目的夾判斷「已下載」——檔案 ingest 進 Drive 後就從 dest 消失，整批會被重抓。曾差點白抓 5 GB。

**`_dup/` 隔離**：判定為重複的檔要移進 `_dup/`。留在來源夾的話，下一輪它們各自成為所屬群組的唯一成員而被「升格」搬進 Drive——把剛剔掉的重複本又收一次。

**去重靠內容特徵**（PDF 頁數＋首尾頁文字指紋）不靠檔名。站上常有同書異名的多份掃描。🚨 用 PyMuPDF 時 **`page_count` 要在 `close()` 之前取**，否則例外被吞掉、去重完全失效。

**體積不是「是不是書」的判準**。曾用 1 MB 門檻把核心原典全擋在外——路德《九十五條論綱》只有 24 KB／7 頁、加爾文《1541 日內瓦教會章程》77 KB、萊爾《聖潔》整本 82 KB docx。**收到 20 KB 為止**。

---

## 簡轉繁

兩站幾乎整批簡體。走 [[ebook-translate]] 的簡→繁子管線（`opencc s2tw` + `TRAD_FIXES`，純規則不吃額度）。
**書目欄位也要轉，不只內文**——`title_zh` / `author` / `note` 進大藏經前都要過（[[feedback_traditional_chinese_only]]）。

---

## 餵給大藏經分類器

🚨 `dazangjing-sweep` **不能直接用**——它的 Sweep 階段上網查國家圖書館 API，不吃現成清單。接點是分類器本身：

```bash
DAZANGJING_ENGINE_ORDER=gemini,nvidia,ollama \
python scripts/dazangjing_catalog_ai.py once \
  --input <records.json> --ledger data/dazangjing/source-catalog/classified-records-<src>.jsonl
```

**引擎順序可設定**（2026-08-26 加）：`ollama,gemini,nvidia,haiku` 任意排。本機 qwen2.5:7b 每筆約 3.75 分鐘，上千筆跑不完，量大一律雲端優先。Gemini 額度乾了用 `DAZANGJING_ENGINE_ORDER=haiku`（走 Claude Code 的 OAuth，`.env` 無 `ANTHROPIC_API_KEY`）。

### 🚨 record 品質直接決定分類品質

天主教在線第一次跑，**34% 判 needs_manual_review**，理由清一色「缺乏作者、年代、出版資訊」——record 只有書名，`author` 空、`date` 填的是站方**上架日期**而非成書年代。

補上條目頁的「圖書簡介」後重跑：**入藏候選 28 → 112 部（四倍）**，待審 303 → 114。
**送進分類器前先把 record 餵飽。** TRC 靠資料夾路徑天然帶作者，這站沒有，得另抓。

---

## 正/外藏判準（使用者定調，勿再自行發明）

**zheng/wai 不是「在不在聖經正典」**——那是 `collectionKey: 'jing'` 的層級。

- **古代**：正藏＝尼西亞大公傳統所接受者（教父論著／講道／禮儀／教會法／聖徒傳／會議文獻）。
- **中世紀以降**：改讀「是否出自受認可的基督宗教傳統內部」。現代基督徒作者**不因**四世紀教會沒見過而成外藏（切斯特頓《回到正統》是正藏）。
- 🚨 **外藏是「整個異端運動或非基督宗教」的層級，不看個別查禁**。外藏＝諾斯底／馬吉安／摩尼／曼達／亞流派這類整套體系，及猶太教、伊斯蘭、外教等他宗教見證，加反基督教論戰。**基督徒作者的書被定罪、列入禁書目錄，只要作者仍在教會內就還是正藏**——蓋恩夫人《簡易祈禱法》是正藏。
- 🚨 **宗教改革後的宗派信條算近代正藏**（西敏／海德堡／比利時／多特／奧斯堡／薩伏伊／蘇格蘭人信條／高盧信綱／第二瑞士／三十九條），一律 `canon=zheng` + `keep_primary_work`。

### prompt 踩過的五個坑（都已補進 `dazangjing_catalog_ai.py`）

1. **不定義 zheng/wai，模型會自行發明**「不在聖經正典→外藏」，把巴西流《聖靈論》、奧古斯丁《論信望愛》全丟進外藏。TRC 首批 130 筆中招 53 筆（41%）。
2. 補定義時只寫「尼西亞接受」，又會**反向**把現代作品全判外藏。兩段都要寫。
3. 只寫「信條是正藏」，模型會擴張到**信條的現代註釋**，`drop_secondary_study` 從 39 塌到 4。要明說 **`canon` 與 `decision` 是兩條獨立的軸**。
4. 「註釋→次級研究」不限時代，**烏爾西努 1584 年的《海德堡要理問答註釋》也被剔除**——他正是該要理問答的執筆者。要看「作品年代與註釋者年代的落差」。
5. **文學不入藏**，即使作者虔誠。TRC 把托爾金、切斯特頓歸在「羅馬公教」下，《精靈寶鑽》《魔戒》《布朗神父》都被當原典收進來。

---

## 書目比對（`zlz_match.py`）

「藏經有的才收」把 1,957 筆收斂成 73 筆。三道關卡都是實測踩出來的：

1. **天主教↔新教定名不同**（天主之城／上帝之城、師主篇／效法基督、奧思定／奧古斯丁、宗徒大事錄／使徒行傳）。別名表**已改讀翻譯詞庫**的 `theologians.name_protestant/name_catholic_sgs` 與 `theological_terms.zh_protestant/zh_catholic_sgs`（33 → 523 組）。**以後往詞庫補譯名，比對能力自動變強，不必改程式。**
2. **完全相等只對得上 11 筆**（站上書名都帶附註如 `论三位一体-奥古斯丁`）。改包含式後 110 筆。
3. **包含式又太鬆**，兩道防呆：「同一藏經書名咬中 ≥3 筆」＝題材詞非書名（基督教史、基督教神學…）改列待審；標題像論文的（研究／探析／從…角度／比較分析）不算原典。

### 同書異名一律入翻譯詞庫

已入 `theological_terms`（`entity_type='work'`）：天主之城／上帝之城、**師主篇／效法基督／輕世金書（三名同書）**、特倫多／脫利騰公議會教理問答、使徒行傳／宗徒大事錄。人名補了大額我略、利瑪竇。

🚨 **產提案時去重鍵必須含作者**。只用（書名＋時代）會把**儒斯定《護教篇》Apologia 與特土良《護教篇》Apologeticum 併成一部**——中文書名撞名在教父文獻很常見。

---

## ebooks 入庫

`ingest_new_books.py` 不適用（只掃 z-lib 頂層、靠 Gemini 猜分類）。用 `trc_ingest.py`：站內路徑天然帶作者書名，不必問 LLM。

- `file_type` 約束 **2026-08-26 已放寬**收 `docx/doc/txt/rtf/chm`（TRC 文字語料 25% 是這些）。`parse_worker` 對非 pdf/epub 優雅跳過；內文另需 Office 解析器（**尚未寫**）。
- 🚨 **`file_path` 已建部分唯一索引** `ebooks_file_path_uniq`。先前沒有唯一鍵，`Prefer: resolution=ignore-duplicates` 形同無效，補登錄時製造了 1,391 筆重複列。

---

## OCR（詳見 [[ebook-pipeline]]）

本輪修掉三個，其中兩個會**靜默遺失資料**：

1. 🚨 **「>50 MB 一律走 Haiku」是誤診**。實測 254 MB／638 頁上傳 Gemini 後 `state=ACTIVE`、正常辨識。當初的 400 應是「中文檔名造成 `UnicodeEncodeError`」被誤判成體積問題。已改用**頁數**判斷（Gemini PDF 上限 1000 頁），體積門檻放寬到 1 GB。此前**所有中文檔名的大型掃描本都被靜默轉去 Haiku**。
2. 🚨 **截斷被當成成功**。整本一次送 Gemini，撞輸出上限後 `json_repair` 搶救幾頁就標 `parsed_at`、`parse_error` 留空——638 頁只存 47 頁卻顯示完成。已加分頁批次（`GEMINI_PAGES_PER_CALL` 預設 60）與「搶救結果 <90% 實際頁數即判失敗」。
3. **輸出無簡轉繁保險**，prompt 也沒指定字體，字跡淡時模型漂向簡體。已補 prompt 要求 + `write_jsonl` 過 `opencc s2tw`。

**超過 1000 頁要先拆**：`fitz.insert_pdf` 切子 PDF，影像位元組完全相同不劣化。已拆例：《聖經原文辭典》1187 頁 → 上冊 593＋下冊 594（原檔標 superseded）。

⚠️ **轉繁救字形，救不了認錯的字**。老舊影印本（字跡淡、筆畫斷裂）的辨識錯誤是全書性的，300 dpi 也救不回糊掉的筆畫。要提升得換路線（提高渲染 DPI 走逐頁影像，而非直接送 PDF）。

**品質閘盲區已補**：`quality_sweep` 的 `blank_rate` 抓「內容爛」，抓不到「內容漂亮卻只有前面幾十頁」。已加 `page_coverage`（chunk 最大 `page_number` ÷ 實際頁數，<0.92 標 `TRUNCATED` 落 REOCR）。

---

## 🚨 多 session 並行時的寫檔風險

本專案常有多個 session 同時動 repo。2026-08-30 實例：本檔改寫完成後、`git add` 之前，被另一個 session 的 checkout 覆蓋回舊版，該次 commit 因此只包含別人暫存區的無關檔案，**改寫內容完全遺失**。

**寫完 skill 或任何文件後，`git add` 前先確認檔案還是你寫的那份**（`wc -l` 或 grep 特徵字），commit 後再驗一次 `git show HEAD --stat` 有沒有你的檔。

---

## 相關

[[ebook-pipeline]]・[[ebook-translate]]・[[scripture-canon]]（`/creeds` 本輪 5→9 份信條）・
[[translation-glossary]]（同書異名一律入庫）・[[project_dazangjing]]（四時代×十藏）
