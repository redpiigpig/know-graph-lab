# 《當代的大愛道革命》— Session 交接文件

> 最後更新：2026-06-14。給接手的新 session：本檔是唯一的進度真相，先讀完再動手。
> 相關記憶：[[project_dadaodao_book]]、[[feedback_drive_canonical_storage]]、[[feedback_ocr_strategy]]、[[feedback_ui_no_text_overflow]]、[[feedback_traditional_chinese_only]]。
> 引擎政策：Gemini（4 key 輪流）→ **Sonnet（claude-sonnet-4-6，OAuth）救援**（使用者明示「gemini 限速就用 sonnet」）→ 退避＋2-strike 停機。

---

## 0. 一句話

碩士論文〈印順導師人間佛教思想的傳承與實踐：以昭慧法師、性廣法師為核心〉改寫成專書 **《當代的大愛道革命》**（副標「昭慧法師與性廣法師的人間佛教思想與實踐」，強調兩位**女性宗教師全方位事蹟**，不只八敬法）。
- `/works` 書籍寫作，slug＝**`mahaprajapati-revolution`**，kind=`book`，色 rose 🪷。
- 線上：`https://redpiigpig.com/works/mahaprajapati-revolution`（**改動要等部署**才看得到 page code；DB/manifest 類改動較快）。

---

## 1. ✅ 已完成（都已 commit+push 到 master）

### 1a. 計畫與分頁
- **DB row**：`writing_projects` slug `mahaprajapati-revolution`。建/改：`node scripts/seed_dadaodao_project.mjs`（Supabase Management API upsert；描述要**精簡**，見 [[feedback_ui_no_text_overflow]]）。
- **書籍計畫支援分頁**（仿論文計畫）：[pages/works/[slug]/index.vue](../../../pages/works/) — 當 `public/content/works/<slug>-materials.json` 存在即顯示分頁 **研究資料 / 碩士文稿 / 口述訪談 / 書摘與構思**（`useBookTabs`）。million-masks / 對話書不受影響。

### 1b. 研究資料（download index）＋全文
- **manifest**：[public/content/works/mahaprajapati-revolution-materials.json](../../../public/content/works/)。每檔 `{name, key, size}`。產生流程：
  1. PowerShell 列檔 → `C:\tmp\dadaodao_files.json`（`Get-ChildItem $root -File -Recurse` rel+size）
  2. `node scripts/build_dadaodao_materials.mjs`（分類＋keys）
- **原檔上 R2 可下載**：879 件全上 R2，key `dadaodao-materials/<相對路徑>`（bucket `knowgraphlab` 私有）。上傳：`python -X utf8 scripts/upload_dadaodao_r2.py`（冪等）。下載走 [server/api/works/material.get.ts](../../../server/api/works/)（**限定前綴**簽名下載）。**Drive 仍是 canonical**。
- **全文轉錄**：[scripts/dadaodao_fulltext.py](../../../scripts/) 把每檔轉文字存 R2 `dadaodao-fulltext/<rel>.txt`。書頁每件「全文」鈕 lazy-load 走 [server/api/works/material-text.get.ts](../../../server/api/works/)（回 `{available,text,zh}`，外文有 `.zh.txt` 翻譯時提供原文/繁中切換）。

### 1c. 分類（目前定案：依論文徵引資料的「文獻類別」）
`build_dadaodao_materials.mjs` 的 `classify()`：**印順／昭慧／性廣三師維持作者分類**，其餘按文獻類別＋主題。11 類：
| 類 | 件 | 來源 |
|---|---|---|
| 📿 印順導師 | 1 | 作者/釋印順 |
| 🪷 昭慧法師 | 25 | 作者/釋昭慧＋議題/昭慧法師 |
| 🧘 性廣法師 | 15 | 作者/釋性廣＋議題/性廣法師 |
| 📚 主題研究專文 | 274 | 其他作者＋議題，**依 6 主題**分組（性別/社運/禪觀/對話/印順學思想/對比山頭） |
| 📰 期刊論文 | 13 | 人間佛教研究期刊 |
| 🎓 研討會論文 | 24 | 印順學研討會 |
| 🎓 學位論文 | 5 | 弘誓/學位論文 |
| 🗞️ 雜誌與會訊 | 100 | 《弘誓》雙月刊＋《福嚴會訊》 |
| 🗄️ 法規檔案 | 400 | 印順查禁案(8)＋善導寺(12)＋**待辨識卷宗(380)** |
| 📊 工具書與彙整 | 10 | 表格 |
| ✝️ 基督教與白色恐怖 | 12 | off-topic 檔案**再歸類（不刪）** |
- **演進**：原「依 Drive 資料夾」→「7 主題軸」→（現）「文獻類別＋3 作者例外」。徵引資料分類參考 `public/content/thesis/ch6.txt` 的〈徵引資料〉段。

### 1d. 口述訪談（38 篇）
- 從 `/thesis` **移到書頁**（`/thesis` 只剩 論文內容/參考資料）。資料 `stores/thesisInterviews.ts` published + `public/content/interviews/*.txt`；reader [pages/works/[slug]/interview/[name].vue](../../../pages/works/)；docx 下載 `server/api/thesis/interview-docx`。

### 1e. 碩士文稿分頁
- 章節文字共用 `/content/thesis/*.txt`（manifest.thesis.chapters）；論文 PDF 上 R2 `dadaodao-materials/碩士文稿/張辰瑋碩士論文.pdf` 可下載。

---

## 2. 🔄 進行中／未完成

### 2a. OCR 全文轉錄（**最重要的長尾**）
- **狀態**：R2 `dadaodao-fulltext/` 已 **469 / 879**。免 API 抽完（docx 77＋文字層 PDF 370＋xlsx 2＝455）＋OCR 數件。
- **剩 ~410 件**：國家檔案局掃描 JPG（~398）＋少數掃描 PDF。OCR pass 上次 **2-strike 配額停機**（Gemini free-tier RPM＋我同時用 Sonnet 造成 contention）。
- **▶ 接續指令**：`python -X utf8 scripts/dadaodao_fulltext.py --ocr-only --pace 2`（冪等，已轉的跳過）。**過夜或我閒置時 Sonnet 可用，跑得遠**。建議設過夜重跑迴圈（resumable）。
- 轉完後 `build_dadaodao_materials.mjs` 不用改（全文是 runtime lazy-load）。

### 2b. 外文全文翻譯（`.zh.txt`）— 尚未開始
- OCR/抽出的**外文**檔案要逐段翻繁中，存 R2 `dadaodao-fulltext/<rel>.zh.txt`，reader 自動出現「原文/繁中」切換。引擎走 [[ebook-translate]]（Gemini→NVIDIA→Haiku/Sonnet）。**尚無腳本**，待寫（可仿 fulltext pipeline 加 translate stage）。

### 2c. 多語研究回顧（**另一條線，平行 session 同時在做—小心對撞**）
- **書目檔**：[scripts/data/lit_review_dadaodao.md](../../../scripts/data/) — 中/英/日 16 筆，依 **5 主題軸**（`##` 標題）分組，OA 標記。（原稱「7 主題」，實際 5 主題 + 1 待補段。）
- ✅ **已 ingest（2026-06-14, commit `e5ce8126`）**：`scripts/ingest_lit_review.py --seed --entries-only --report scripts/data/lit_review_dadaodao.md --project mahaprajapati-revolution` → `lit_review_entries` **16 筆**（14 pending / 2 zh unavailable）。**務必 `--entries-only`**：本書是 `kind='book'`，沒加會被 seed 覆寫成 `kind='paper'`。
- ✅ **解析基建已上**：`lit_review.py` 加 `BOOK_SURVEY_THEMES`（5 軸）+ `parse_review_report` 接受 `##` 標題（commit `2d7a6309`，平行 session）；`detect_language` 容忍「中文（簡體…）」→ zh（commit `e5ce8126`）。
- ✅ **書頁分頁已啟用**：`loadLitReview()` 已對所有計畫載入、`bookTabs` 有書目即顯示「研究回顧」分頁（commit `2d7a6309`）。**部署後**書頁出現 badge 16 的分頁。
- **待做**：過夜 `python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project mahaprajapati-revolution --resume --engine gemini` 抓 14 筆 OA 外文全文＋逐段翻譯（原文/中譯兩欄 reader `/works/[slug]/review/[ref]` 已存在）。⚠️ **平行 session 可能正在跑此步**——啟動前先確認，避免雙跑浪費 Gemini 配額（upsert 冪等但白翻）。

---

## 3. ⏳ 待使用者決定 / 待辦

1. **380 件「國家檔案局其他卷宗」**（代碼命名掃描，論文未徵引、檔名無法判斷內容）：使用者選**「等 OCR 辨識內容再決定」**。→ OCR 跑完後讀全文，是基督教界白色恐怖類的併入「基督教與白色恐怖」、是印順/善導寺相關的留法規檔案。
2. **「基督教與白色恐怖」類**（12 件，再歸類不刪）：使用者要**衛理堂/周聯華相關遷到衛理公會研究資料** `/research-data/taiwan-methodist`（見 [[project_chengzhong_bulletins]]）。manifest 已把該子群標「（可遷衛理公會資料）」。→ 跨專案搬移待做（Drive 檔＋該專案資料結構）。
3. **研究回顧分頁**要不要對 book 開（見 2c）。

---

## 4. 關鍵事實 / 架構

- **R2**：bucket `knowgraphlab`（私有）。前綴：`dadaodao-materials/<rel>`（原檔）、`dadaodao-fulltext/<rel>.txt`（全文）、`.zh.txt`（翻譯）。`.env` 有 `R2_*`、`Gemini_API_Key_1..4`、`SUPABASE_*`、`SUPABASE_ACCESS_TOKEN`（Management API）。**無 ANTHROPIC_API_KEY** → Sonnet 走 `~/.claude/.credentials.json` OAuth（fulltext 腳本已內建 refresh）。
- **Drive canonical**：原檔在 `G:\我的雲端硬碟\資料\知識圖工作室\研究資料\大愛道革命\論文資料`（5.44GB / 879 件：381 PDF＋410 JPG＋82 docx＋…）。口述訪談原始夾 `…\碩士論文\口述訪談`。論文全文/PDF 在 `…\碩士論文\`。
- **頁面結構不需改**即可吃新 manifest（categories→groups→files{name,key,size}）。
- **部署**：commit 後網站自動部署；page code 改動要等部署，DB（描述/狀態）即時。
- **build 驗證**：`npm run build`（exit 0）；pre-push 跑 vitest 154 例。

---

## 5. 檔案／腳本索引

| 用途 | 路徑 |
|---|---|
| 建 manifest（分類） | `scripts/build_dadaodao_materials.mjs` |
| 建/改計畫 row | `scripts/seed_dadaodao_project.mjs` |
| 上傳原檔→R2 | `scripts/upload_dadaodao_r2.py` |
| 全文轉錄（抽+OCR） | `scripts/dadaodao_fulltext.py` |
| 多語研究回顧書目 | `scripts/data/lit_review_dadaodao.md`（平行 session） |
| 下載路由 | `server/api/works/material.get.ts` |
| 全文路由 | `server/api/works/material-text.get.ts` |
| 書頁 | `pages/works/[slug]/index.vue` |
| 訪談 reader | `pages/works/[slug]/interview/[name].vue` |
| manifest 產物 | `public/content/works/mahaprajapati-revolution-materials.json` |
| 論文徵引資料（分類依據） | `public/content/thesis/ch6.txt`〈徵引資料〉 |

---

## 6. 下一步建議優先序

1. **設過夜 OCR 迴圈**跑完剩 ~410 掃描（`--ocr-only --pace 2`，2-strike 停就重啟）。
2. OCR 完 → 讀 380 卷宗全文 → 重歸類（基督教白色恐怖 vs 印順/善導寺）。
3. 外文檔案 `.zh.txt` 翻譯 stage（仿 fulltext pipeline）。
4. 研究回顧：確認平行 session 狀態 → ingest `lit_review_dadaodao.md` → book 開「研究回顧」分頁 → 過夜抓 OA 全文＋翻譯。
5. 衛理堂/周聯華 跨專案遷 `/research-data/taiwan-methodist`。
