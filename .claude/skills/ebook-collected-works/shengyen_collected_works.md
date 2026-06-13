# 聖嚴法師《法鼓全集 2020 紀念版》案例（collected-works 第二個「單一語言」案例）

> 繼印順之後第二套漢傳佛教全集。全集本即繁中 → 零翻譯、零對齊。
> 與印順唯一差別＝**來源解析器（HTML 而非 CBETA TEI）**，下游入庫/hub/reader 完全共用。

## 版權姿態
聖嚴法師 1930–2009，2009 圓寂 → 非公有領域。本站 auth-gate 私人研究圖書館收錄（同印順，[[feedback_jung_nonpd_english_first]]）。來源＝法鼓文化官方數位版 ddc.shengyen.org，僅私人閱讀、不公開散布。

## 來源架構：ddc.shengyen.org（**靜態 HTML、完全可枚舉**）
SPA 殼（jstree + getData.php），但真資料是靜態檔/JS 變數，三支端點全枚舉：

| 端點 | 內容 |
|---|---|
| `include/getData.php?type=all_books` | `var G_ALL_BOOKS = {"輯-冊": 書名}` — **111 冊**（含 00 總目錄，不上架 → 110 冊） |
| `include/getData.php?type=vol_dump&book=00-00` | `var G_VOLS = {"輯-冊-篇": 篇名}` — **4079 篇**（全枚舉，&book 參數被忽略，一次全給；扣總目錄 8 篇＝4071） |
| `tree_menu/toc.html` | 巢狀 `<ul><li><a html_file="輯-冊-篇.html">篇名</a>` — 書內 章/節→篇 章節樹 |
| `html/{輯-冊-篇}.html` | **每篇正文靜態檔**（`p.indent` 正文／`p.hN` 標題／`span.pb data-page` 原書頁碼／`span.lb` 空行碼） |

⚠️ requests 直接抓會被 server 丟連線 → `_fetch` 必須帶 **User-Agent + verify=False + 重試**（curl -sk 才通）。

## 資料模型
- **一書（ebook）＝ 一個 輯-冊**（110 ebook rows，`ebook_id = b0000000-0000-4000-8000-<12位序號>`）。
- **chunk ＝ 篇**（html 檔，4071 篇）；`page_number` 取該篇首個 `span.pb data-page`（**保留原書頁碼**，[[feedback_pdf_page_number]]）。
- **parent_volume ＝ 輯名**（9 輯 + 別卷）：01 教義論述／02 佛教史／03 文集／04 禪修／05 佛教入門／06 自傳遊記／07 經典釋義／08 生活佛法／09 理念願景／11 別卷（年譜）。00 總目錄不上架。
- **chapter_path ＝ 書名 · [toc 書內章節] · 篇名**。
- lb/pb 是空 `<span>` 標記 → `p.get_text()` 已乾淨；`_clean` 殺折行保全形空格（同 yinshun）。

## Pipeline（已完成 2026-06-13）
1. [x] `scripts/shengyen_build.py`：`parse_content_html`（HTML→單語 chunk，hN→markdown 標題、保留 data-page）+ `build_chapter_paths`（toc 巢狀→篇路徑）+ `build_registry`/`build_book`/`_upload`（重用 te/se，同 yinshun）。test-first `scripts/tests/test_shengyen_build.py`（9 例綠）。
2. [x] `--build-registry` → `shengyen_registry.json`（110 冊/4071 篇）。
3. [x] pilot《書序》03-05（110 篇）→ R2+DB → reader 截圖實證（頁碼 p13.../「上篇 他序」h1 渲染/篇目樹）。
4. [x] `--all --upload` 全 110 冊。
5. [x] `stores/collectedWorks.ts` 加聖嚴 `CwAuthor`（slug `shengyen`，teal/🥁；貢獻3段+年表13條+110書目按9輯分組；無 PD 肖像→emoji 降級）。

## 雷區
- requests 要帶 UA + verify=False + 重試，否則 RemoteDisconnected。
- ebooks.id 是 UUID，查全集用 `id=in.(...)` 不能 `like`。
- 截圖 reader 全頁 ~3970px > 2000px 硬限 → 讀前 PIL crop ≤1850。
- dev server 多任務並行時 :3000 可能被別任務佔/壞（[[feedback_no_kill_other_tasks]]）→ 自己另起 `PORT=3100 npm run dev` 截圖，別殺 :3000。
- 已認證 ebook reader 首次 SSR 冷編譯 >30s → screenshot 腳本要把 navigationTimeout 拉到 150s（或先暖路由）。

## 接續
星雲大師全集（`books.masterhsingyun.org`，365 冊，需先驗純 HTML vs API）。
