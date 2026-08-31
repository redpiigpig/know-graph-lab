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
| 合計 | **2,832 部** | 審定後 **88 部** |

待審提案：`data/dazangjing/source-catalog/PROPOSAL_2026-08-30_trc-zlz.md`（**尚未入庫**）。
分類 ledger：同目錄 `classified-records-trc.jsonl` / `-zlz.jsonl`。
人工審定表：同目錄 `adjudication-2026-08-30.json`（由 `dazangjing_build_adjudication.py` 產生）。

🚨 **檔名要帶來源**。`PROPOSAL_2026-08-30.md` 已被另一個 session 用掉（那是跨全部
ledger 的 310 部提案），本站這批一律寫 `_trc-zlz` 後綴。2026-08-30 曾整份覆蓋掉別人
那份，靠 `git checkout` 才救回。

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
dazangjing_dump_corpus.mjs      data/dazangjing/*.ts → 全藏 JSON（給 --corpus 比對）
dazangjing_proposal.py          分類 ledger → 待審提案（Markdown + .ts 片段）
dazangjing_build_adjudication.py 人工審定表 → adjudication-<date>.json
dazangjing_alias_to_glossary.py  審定表的同書異名 → theological_terms（預設 dry-run）
ocr_overnight.py                整夜 OCR 看守（先探活、無進度即停）
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
2026-08-30 審定又補 32 組（`scripts/dazangjing_alias_to_glossary.py`，含 dry-run）：
信望愛手冊／論信望愛／傳道員指南、司牧守則／牧靈指南、五篇神學講辭／神學演講錄、
法國信條／高盧信綱、多特信經／多特信條、論作基督徒／做基督徒、正統／回到正統…

🚨 **產提案時去重鍵必須含作者**。只用（書名＋時代）會把**儒斯定《護教篇》Apologia 與特土良《護教篇》Apologeticum 併成一部**——中文書名撞名在教父文獻很常見。

🚨 **別名不可用泛稱**。候選別名要先確認它不是**另一部書的正式名**：
「六日創造解」是尼撒的格列高利另一部書（不是巴西流的 Hexaemeron）、
「詩篇註」是狄奧多若的（不是奧古斯丁的 Enarrationes）。這兩個一度被寫進別名組，
真的入庫就會把兩位教父的不同著作永久黏成同一部。「三聯論」「多特法典」這類泛稱同樣剔掉。

🚨 `term_english` 有唯一索引。補別名撞 409 表示**該作品早已在詞庫、只是 `term_original` 不同**——
要 PATCH 既有列的空別名槽，不是硬塞新列。

⚠️ 詞庫與藏內定名不一致 **2 筆待使用者定奪**（[[feedback_glossary_strict_authority]] 說詞庫是權威，
但改的是藏內條目，不自行動手）：
- 詞庫 `致安提阿人論雕像講道集` ↔ 藏內 `雕像講道`
- 詞庫 `特倫多公議會教理問答` ↔ 藏內 `羅馬要理問答`

---

## 提案審定（2026-08-30 定型）

分類器只看單筆 record，看不到藏內既有 8,016 卷，所以**提案一定要過兩道關才入庫**：

```bash
node scripts/dazangjing_dump_corpus.mjs c:/tmp/dz_corpus.json
python scripts/dazangjing_proposal.py \
  --ledger .../classified-records-trc.jsonl --ledger .../classified-records-zlz.jsonl \
  --corpus c:/tmp/dz_corpus.json \
  --adjudication .../adjudication-2026-08-30.json \
  --out .../PROPOSAL_<date>_trc-zlz.md
```

- `--corpus`：**自動**撞名比對，兩級判定。書名＋作者都對上＝`same` 直接剔；只有書名對上＝
  `suspect` 留在提案另列一區。分兩級是必要的——奧古斯丁與希拉流各有一部《論三位一體》，
  湯漢與維克託利烏斯各有一部《創世論》，自動剔掉就少收真書。
- `--adjudication`：**人工**審定表，記機器判不了的。keep 條目可帶 `patch` 改欄位，
  **在自動比對之前套用**（改過的時代／藏別才是拿去比的那一份）；未判定的會列警告。

首輪成績：176 筆候選 → 剔 87 → **實收 88 部**。剔除分佈：

| 類別 | 部數 | 例 |
|---|---:|---|
| 藏內已收（多為同書異名） | 66 | 信望愛手冊／論信望愛、效法基督／師主篇、法國信條／高盧信綱 |
| 譯本合集‧選集非單一原典 | 12 | 《使徒教父著作》《安瑟倫著作選》所收各篇早已分別在藏 |
| 來源站資料夾層被當成書 | 6 | 「希波的奧古斯丁」「信綱及教理問答」 |
| 次級改編‧非原典層級 | 3 | 兒童簡明要理問答、《Rome Sweet Home》歸信見證 |

### 🚨 只靠關鍵字查「在不在藏」會漏

《高盧信綱》查了「高盧／Gallicana／法蘭西信條／拉羅歇爾」全無，判成「改革宗信條中唯一缺者」，
**其實藏內作《法國信條》**——是 `--corpus` 的自動比對抓回來的。人工查證一律要跟自動比對兩邊對照，
別只信任何一邊。

### 審定時實際抓到的錯（都不是分類器判得出來的）

- **書名欄是來源站資料夾名殘留**：「哲學大全 Summa contra Gentiles 駁異大全」。
- **作者張冠李戴**：《輕世金書》原著標成 Gerhard of Zutphen、譯者標成「利瑪竇圈」——
  實為托馬斯‧厄‧肯培原著、陽瑪諾（Manuel Dias Jr.）漢譯。
  《聖域門檻》的 Joseph Martos 被安成明清耶穌會士「馬若瑟」（Joseph de Prémare）。
- **書名 OCR 誤字**：「癖基督抹殺論」應作「**闢**」——駁幸德秋水《基督抹殺論》的民國護教書。
- **時代標錯**：清末民初材料被歸「近代」6 部（教務紀略 1905、庚子教會華人流血史 1900、
  景教碑考、卜彌格傳、聖五傷方濟各行實、聖女瑪德肋納傳）。**看的是成書年代不是題材年代。**
- **`title_orig` 只是複製 `title_zh`** 35 筆：漢語原著（天主實義、天學初函）該**清空**，
  外文原著（納匝肋人耶穌、耶穌基督）該補回真原題。
- **待定條目查得出來**：「甜蜜的家—羅馬」＝ Scott & Kimberly Hahn《Rome Sweet Home》(1993)。

### 這批真正的收穫

價值集中在**漢語天主教文獻與教廷文件**，不在教父區（教父區早就滿了）：
天主實義、天學初函、天主降生引義、七克、新法表異、李安德日記（首位華籍司鐸拉丁文日記）、
闢／評基督抹殺論、馬相伯集、超越東西方，以及十餘份此前未收的若望保祿二世通諭勸諭
（Dies Domini、Vita Consecrata、Ecclesia in Asia、Ecclesia de Eucharistia…）。
**教宗文告一律歸書信藏**，與藏內既有通諭條目同列。

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

### 🚨 Gemini 模型名會過期，503／404 要分開讀（2026-08-30）

一本書連撞三種狀態，**換模型就過**，不必動用 Haiku：

| 模型 | 結果 |
|---|---|
| `gemini-flash-latest`（`DEFAULT_MODEL`） | **503** high demand，retry 兩次仍掛 |
| `gemini-2.5-flash` | **404**，錯誤訊息明講「no longer available to new users」 |
| `gemini-3.6-flash` | ✅ 102 頁／2 批／379 秒 |

- **503 是模型忙不是額度乾**，換個模型名往往就通；429 才是額度，會自動輪 key。
- **404 的錯誤訊息會直接告訴你接班模型是哪個**，照著換即可（此次指向 `gemini-3.6-flash`）。
- `--model` 可即時覆寫，不必改 `.env`。判定 Gemini 全掛、要退 Haiku 之前，**先把候選模型名試過一輪**。

**別自己挑模型——問 `gemini_probe.py`。** 它掃 MODELS 清單找第一個真的能生成的，
把 `MODEL=xxx` 印在 stdout 第一行並寫進 `scripts/state/gemini_live_model.txt`。
免費層日配額是**每 key 每模型**各自獨立，所以「某個模型乾了」永遠不等於「Gemini 乾了」。

### 🚨 日常 OCR 排程其實沒在跑（2026-08-30 修好）

積壓不動的真正原因不在額度，是排程根本沒啟動，而且**沒有任何錯誤會被看見**：

1. `KGLab-OCR-Daily-10/14/18` 的 `DisallowStartIfOnBatteries=True`。這台是筆電，
   10/14/18 點只要在電池上就直接拒跑，`LastTaskResult=0x800710E0`（工作被拒絕）。
   **`scripts/logs/` 148 個檔案裡一個 `ocr_*.log` 都沒有**——bat 從來沒跑完過。
   已把三個排程的電池限制關掉。（`KGLab-Quality-Sweep` 仍有同樣設定，待使用者決定。）
2. `run_ocr_daily.bat` 第 3 步直接呼叫 `ocr_with_gemini.py`，**沒先跑探針**，
   吃的是正在 503 的 `DEFAULT_MODEL`。全 repo 五支 Gemini runner
   （`fleet_keeper.ps1`／`accs_ocr_gemini_runner.ps1`／`resume_lanes_on_gemini.ps1`／
   `translation_cloud_supervisor.py`／`ingest_accs_genesis.py`）都會先探，只有這支漏接。
   已補 Step 3a：探針成功就 `set GEMINI_MODEL`，全掛則跳過 OCR 並設 `GEMINI_EXIT=2`
   走既有的通知分支。

🚨 **改 bat 的控制流一定要實測兩條路徑**（`goto` 標籤打錯、`set /p` 讀不到檔會**卡住等 stdin**，
在排程裡就是掛到 `ExecutionTimeLimit` 為止）。用 scratchpad 的假 bat 分別測「探針成功」與
「全掛」兩條，確認都走到 `:after_ocr`。`set /p` 讀沒有結尾換行的檔沒問題（已實測）。

⚠️ 從 Git Bash 測 bat 要用 PowerShell 轉手：`cmd.exe /c "path"` 會被 MSYS 路徑轉換
吃掉參數而開成互動式 cmd，看起來就像「腳本卡住」。
PowerShell 端寫 ``cmd.exe /c "`"<bat>`" < NUL"``。

### 積壓的組成跟數字給人的印象不同（2026-08-30 實測）

| | 數量 |
|---|---:|
| 全館 | 5,012 |
| 未 parse 總數（`parsed_at IS NULL`） | 2,985 |
| ├ 已確認掃描本、在 OCR 佇列（`parse_error` 含 no extractable text） | **156** |
| └ 尚未過 `parse_worker`（其中 pdf 2,181） | 其餘 |

**「OCR 積壓 2,986」其實是「未處理 2,985」**，只跑 `ocr_overnight.py` 也只碰得到 156 本；
大宗要先過 `parse_worker` 分流才會落進 OCR 佇列。報進度前先把這兩個數字分清楚。

### 已有文字層 ≠ 不用 OCR

掃描本常帶 Acrobat Paper Capture 的舊 OCR 層，`parse_worker` 會把它當正文抽走並標 `parsed_at`，
書就**再也不會進 OCR 佇列**。《復活的基督》那層把「第三章」認成「第一章」、「註釋」認成
「言主釋」、「若望二十章」認成「若望二十量」。**直式排版與老舊影印本的舊文字層一律不可信**，
先 `--book <id>` 手動送 OCR，別讓 parse_worker 先碰。

`--book <id>` 吃不在 OCR 佇列的書（走 `fetch_books_by_ids`），新登錄、未 parse 的書也能直接指定。

---

## 🚨 多 session 並行時的寫檔風險

本專案常有多個 session 同時動 repo。2026-08-30 兩次實例：

1. 本檔改寫完成後、`git add` 之前，被另一個 session 的 checkout 覆蓋回舊版，
   該次 commit 因此只包含別人暫存區的無關檔案，**改寫內容完全遺失**。
2. 產提案時寫到 `PROPOSAL_2026-08-30.md`，**整份覆蓋掉另一個 session 剛 commit 的 310 部提案**。
   `git status` 顯示成 ` M`（已追蹤且被修改）而不是 `??`，才發現撞檔；靠 `git checkout --` 救回。

**寫完 skill 或任何文件後，`git add` 前先確認檔案還是你寫的那份**（`wc -l` 或 grep 特徵字），
commit 後再驗一次 `git show HEAD --stat` 有沒有你的檔。

**另外三條**：
- **輸出檔名帶來源後綴**（`_trc-zlz`），別用只有日期的通名——日期一定會撞。
- **寫檔前看 `git status`**：目標檔若是 ` M` 而非 `??`，表示別人已經建過同名檔，換名再寫。
- **只 `git add` 指定路徑，絕不 `git add -A`**。這個 repo 隨時有別的 session 的半成品
  （本輪同時在跑 hellenika 俄耳甫斯讚歌、fathers 連結、accs 正規化），
  `git diff --cached --stat` 確認staged 清單只有自己的檔再 commit。
- **共用腳本改之前先重讀**。`dazangjing_proposal.py` 在本輪被另一個 session 從 172 行擴到 386 行
  （加了全藏撞名比對），照舊版記憶去 Edit 會直接失配；失配就是提醒，不要硬改。

---

## 相關

[[ebook-pipeline]]・[[ebook-translate]]・[[scripture-canon]]（`/creeds` 本輪 5→9 份信條）・
[[translation-glossary]]（同書異名一律入庫）・[[project_dazangjing]]（四時代×十藏）
