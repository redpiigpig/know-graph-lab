---
name: research-data-hongshi
description: 「印順學派與弘誓研究資料」collection（/research-data/yinshun-hongshi，需登入）的抓取／OCR／上架流程 — 佛教弘誓學院／玄奘大學刊物典藏：弘誓雙月刊、學團日誌、玄奘佛學研究學報、歷屆學術活動、福嚴會訊。資料源 hongshi.org.tw 在 Cloudflare「Just a moment」JS 挑戰後 requests/curl 一律 403，須 headful 真實 Chrome；整天連抓會被持續硬封（改走 Wayback Machine）。hcu.edu.tw（玄奘）非 Cloudflare，純 requests 即可。Use when 要補抓／重抓任一刊物、跑全文、調各子頁、新增子站。與 [[project_chengzhong_bulletins]] 的 taiwan-methodist 並列於同一 /research-data portal。
---

> ⚙️ **引擎政策**：OCR 走 Gemini Vision（4 keys 輪流）→ Sonnet(OAuth) 救援，2-strike 配額停機（[[feedback_ocr_strategy]]、[[feedback_ocr_two_strike_quota]]）。所有中文一律繁體（[[feedback_traditional_chinese_only]]）。

# 印順學派與弘誓研究資料 collection

`/research-data`（`middleware:'auth'` 需登入）第二個 collection，slug **`yinshun-hongshi`**（rose 🪷）。作《當代的大愛道革命》([[project_dadaodao_book]]) 背景史料。記憶 [[project_yinshun_hongshi_collection]]。

| 子頁 | 來源 | 現況 |
|---|---|---|
| 弘誓雙月刊 `/magazine` `/magazine` | hongshi（有乾淨文字層 PDF） | 116 期(80–200)；**115/116 全文**（issue 103 源檔損毀待補）|
| 學團日誌 `/log` `/log/[n]` | hongshi 網頁文字 | **173 則(n=27–210)** ✅ |
| 玄奘佛學研究學報 `/xuanzang` | **hcu.edu.tw（非 CF）** | 45 期 / **304 篇全文 ✅(100%)** |
| 歷屆學術活動 `/meeting` `/meeting/[n]` | hongshi（經 Wayback） | **24 項** ✅（卡 `v-if=meetCount`）|
| 福嚴會訊 `/fuyan` | 沿用 dadaodao R2 | 71 期 ✅（品質不一，舊期有雜訊）|

R2 前綴：`yinshun-hongshi/<刊>/`（原檔）、`yinshun-hongshi-fulltext/<刊>/...txt`（全文）。API：`server/api/research-data/yinshun-hongshi-file.get.ts`（簽名下載）、`yinshun-hongshi-text.get.ts`（全文，pdf key→txt key）。R2 前綴限定避免任意取用。

> 🗑️ **弘誓電子報不收**：每期 EDM = 重複學團日誌 ＋ 招生廣告 ＋ 昭慧／性廣時論，時論亦登弘誓雙月刊（已收）→ 整份冗餘。（知識保留：全 1–542 期在站上，`EDM/<n>.html` 新＋`epaper/hongshi pic{,2,3}/<n>.htm` 舊【**注意 .htm 非 .html**】，5 索引頁枚舉。）

## 🚨 hongshi.org.tw = Cloudflare JS 挑戰（最關鍵）
- requests/curl/WebFetch 一律 **403 / 「請稍候／正在執行安全驗證」**。**只有 headful 真實 Chrome 過得了**：`chromium.launch({headless:false, channel:'chrome', args:['--disable-blink-features=AutomationControlled']})` + `addInitScript(navigator.webdriver=undefined)`。PDF 也在 CF 後 → 用通過挑戰的 `ctx.request.get()`（共用 cookie）下載。
- 挑戰偵測**必含中文** `正在執行安全驗證/惡意機器人/請稍候`（`hongshi.is_challenge_page`）；捕到挑戰**不可存**，退避。
- **限流真實且會累積成持續硬封**：整天連抓後會被**封數小時～一天**（連 40min／3h 冷卻都過不了）。平時：請求間隔 5–12s 隨機、index 回 0 → 重試＋退避、scraper auto-relaunch（headful 視窗會被誤關）。`log-page.php`／`meeting-B-page.php` 需 `Referer` 否則錯誤頁。
- **🆘 被硬封時改走 Wayback Machine**（archive.org 非 CF）：`http://archive.org/wayback/available?url=…` 取最近快照 → `http://web.archive.org/web/<ts>id_/<url>`（`id_` raw＝無工具列原始頁）→ 純 requests。歷屆學術活動即此法（`hongshi_meeting_wayback.py`）。**限制**：PDF 與部分頁未存檔（issue 103 PDF、6 項活動頁 Wayback 沒有）。
- **hcu.edu.tw（玄奘）不是 Cloudflare** → 純 requests（`xuanzang_journal.py`）。
- **G: streaming mount 會中途卸載** → Drive canonical 寫入一律 best-effort try/except，R2 才是 serving store。

## 抓取雷區（純函式＋測試：`scripts/hongshi.py`+test 15、`scripts/xuanzang.py`+test 8）
- **弘誓雙月刊 PDF 檔名三變體**：`hongshi-magazine-187-DATE.pdf`／`magazine190-DATE.pdf`（無連字號）／`180hongshi-ROCDATE.pdf`（號在前）。`hongshi.magazine_issue()` 統一解析。1–79 期官網無 PDF；缺 85,177-180（源站連結 404）。
- **玄奘期頁有編輯誤貼的 `file:///C:\…` 本機路徑當連結**，與正常 `/files/…pdf` 並存 → harvest 必須**跳過 `file:` href**（否則被加 BASE 成假 http）。中文期數用 `xuanzang.parse_issue_no`。

## 檔案索引
- 純函式＋測試：`scripts/hongshi.py`、`scripts/xuanzang.py`（+ `scripts/tests/test_{hongshi,xuanzang}.py`）
- 弘誓雙月刊：`hongshi_harvest_magazine.mjs`／`hongshi_download_magazine.mjs`／`hongshi_fill_gaps.mjs`／`hongshi_publish_magazine.py`／`hongshi_ocr_magazine.py`（文字層優先，掃描退 Vision）／`hongshi_ocr_pages.py`（逐頁 OCR，整本過大 413 時用）
- 學團日誌：`hongshi_scrape_log.mjs`／`hongshi_publish_log.py`
- 歷屆學術活動：`hongshi_meeting_wayback.py`（**現用**，走 archive.org）／`hongshi_scrape_meeting.mjs`（live headful，待 hongshi 解封可補完整清單）／`hongshi_publish_meeting.py`
- 玄奘佛學研究：`xuanzang_journal.py`（`--harvest`／`--process [--no-ocr]`／`--publish`）
- 頁面 `pages/research-data/yinshun-hongshi/*`；Drive canonical `G:\我的雲端硬碟\資料\知識圖工作室\研究資料\印順學派與弘誓\`

## ⏳ 待補（皆卡在 hongshi 持續封鎖，解封後可補；非流程問題）
- **弘誓雙月刊 issue 103**：下載的 PDF 損毀（MuPDF 無法解析），Wayback 無此 PDF → 解封後 `hongshi_download_magazine.mjs`（已刪損毀本地檔，會重抓）＋ `hongshi_ocr_magazine.py`。
- **歷屆學術活動 6 項**：Wayback 未存檔 → 解封後 `hongshi_scrape_meeting.mjs`（live 完整清單，會跳過已抓 24 項）＋ `hongshi_publish_meeting.py`。

## 姊妹站：玄奘佛學研究「公開官網」(/Hsuan_Chuang_Studies)
與本 collection 的 `/xuanzang`（研究資料、需登入、R2 全文）**不同**：`redpiigpig.com/Hsuan_Chuang_Studies`
是學報公開門戶（`pages/Hsuan_Chuang_Studies/`）。每期以**封面圖**呈現，點入 `issue/[n]` 顯示
篇名／作者／頁數／官方 PDF 下載鍵。資料同源 hcu.edu.tw：`scripts/hcjbs_journal.py` 逐期解析
（`strip_en` 裁尾端英譯、封面升 400×560 存 `public/Hsuan_Chuang_Studies/covers/`）→
`public/content/Hsuan_Chuang_Studies/issues.json`（頁面直接 `import`，SSR 友善；PDF 熱連 hcu 官方）。
重跑：`python -X utf8 scripts/hcjbs_journal.py`（封面已存則跳過）。

## See also
[[project_yinshun_hongshi_collection]]、[[project_chengzhong_bulletins]]（同 portal 衛理公會 collection）、[[ebook-pipeline]]（OCR 同源）、[[feedback_drive_canonical_storage]]。
