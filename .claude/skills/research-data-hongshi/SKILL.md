---
name: research-data-hongshi
description: 「印順學派與弘誓研究資料」collection（/research-data/yinshun-hongshi，需登入）的抓取／OCR／上架流程 — 佛教弘誓學院刊物典藏：弘誓雙月刊（PDF＋全文）、學團日誌（網頁文字），及福嚴會訊。資料源 hongshi.org.tw 在 Cloudflare「Just a moment」JS 挑戰後，requests/curl 一律 403，必須用 headful 真實 Chrome（Playwright channel:'chrome'）才抓得到；密集抓會被限流，務必請求間隔＋退避。（弘誓電子報已評估為冗餘不收，見內文。）Use when 要補抓／重抓弘誓刊物、對弘誓雙月刊跑全文、調 /research-data/yinshun-hongshi 各子頁、新增刊物子站。與 [[project_chengzhong_bulletins]] 的 taiwan-methodist collection 並列於同一 /research-data portal。
---

> ⚙️ **引擎政策**：OCR 走 Gemini Vision（4 keys 輪流）→ Sonnet(OAuth) 救援，2-strike 配額停機（見 [[feedback_ocr_strategy]]、[[feedback_ocr_two_strike_quota]]）。翻譯類沿用 [[feedback_engine_nvidia_no_haiku]]。所有中文一律繁體（[[feedback_traditional_chinese_only]]）。

# 印順學派與弘誓研究資料 collection

`/research-data`（論文資料整理，`middleware:'auth'` 需登入）第二個 collection，slug **`yinshun-hongshi`**，作《當代的大愛道革命》([[project_dadaodao_book]]) 背景史料。記憶 [[project_yinshun_hongshi_collection]]。四個刊物子頁：

| 子頁 | 內容形態 | 來源 | 狀態 |
|---|---|---|---|
| 弘誓雙月刊 `/magazine` | PDF（**有乾淨文字層**，非純掃描）＋全文 | 官網抓 | 116 期(80–200)；全文已抽（見下節）✅ |
| 學團日誌 `/log` + `/log/[n]` | 網頁文字 | 官網抓 | 173 則(n=27–210)，免 OCR ✅ |
| 福嚴會訊 `/fuyan` | PDF＋全文 | 沿用 dadaodao R2 | 71 期，已 OCR（品質不一，舊期有雜訊）✅ |

> 🗑️ **弘誓電子報已評估後不收（2026-06-15）**：每期 EDM = 重複的「學團日誌」區塊 ＋ 招生／活動廣告 ＋ 昭慧／性廣時論文章；user 確認時論文章**亦登於弘誓雙月刊**（已全文收錄），故 EDM 整份冗餘 → 移除子頁與資料。**知識保留**：EDM 全 1–542 期確實在站上，但散落 `EDM/<n>.html`（新）與 `epaper/hongshi pic{,2,3}/<n>.htm`（舊，**注意 .htm 非 .html**）多資料夾，靠 5 個索引頁（`hongshi pic/hongshi.htm`=401-542、`301-400.htm`、`pic3/201-300.htm`、`pic2/101-200.htm`、`pic2/1-100.htm`）枚舉；若日後要重收，harvest 用 `a.href`（已解析絕對 URL）＋ `/(\d+)\.html?/`。

## 🚨 hongshi.org.tw = Cloudflare JS 挑戰（最關鍵）
- requests/curl/WebFetch 一律 **403 / 「Just a moment / 正在執行安全驗證」**。**只有 headful 真實 Chrome 過得了**：
  `chromium.launch({ headless:false, channel:'chrome', args:['--disable-blink-features=AutomationControlled'] })` + `addInitScript(navigator.webdriver=undefined)`。
- PDF 也在 CF 後 → 用通過挑戰的 `ctx.request.get()`（共用 cookie）下載，不要另開 requests。
- 挑戰偵測**必含中文** `正在執行安全驗證/惡意機器人`（純函式 `hongshi.is_challenge_page`）；捕到挑戰**不可存**，退避 40s。
- **限流是真的**（user 明令「下載要有間隔」）：請求間隔 5–12s 隨機；index 回 0 筆 → 重試＋45s 退避；連發太多 log.php 會回挑戰頁。冷卻數分鐘可解。
- ⚠️ **headful 視窗被關掉會中斷**（user 誤關過一次）；腳本皆 resumable（已存跳過），中斷重跑即可。

## 抓取雷區（已寫進測試 scripts/tests/test_hongshi.py，15 例綠）
- **弘誓雙月刊 PDF 檔名三種變體**都要認：`hongshi-magazine-187-DATE.pdf`／`magazine190-DATE.pdf`（無連字號）／`180hongshi-ROCDATE.pdf`（號在前）。`hongshi.magazine_issue()` 統一解析。1–79 期官網無 PDF；缺 85,177-180（源站連結 404）。
- **🆘 hongshi 被持續硬封時 → 改走 Wayback Machine**（archive.org 非 Cloudflare）：`http://archive.org/wayback/available?url=…` 取最近快照，再以 `http://web.archive.org/web/<ts>id_/<url>`（`id_` raw 修飾）抓**無工具列原始頁**，純 requests 即可。歷屆學術活動就是整天連抓後 hongshi 封鎖、改用此法抓到的（`hongshi_meeting_wayback.py`，24/30 項，6 項未存檔）。
- **log-page.php 需 `Referer: log.php`** 否則錯誤頁；n=1–26 是空 stub（非真內容），站上學團日誌實際從 n=27 起。
- （EDM `.htm` 多資料夾枚舉法見上方 🗑️ 註，雖已不收但 `hongshi.edm_issue()` 仍保留並測試。）

## 弘誓雙月刊 OCR（掃描 PDF → 可讀全文）
- 流程仿 [[ebook-pipeline]] 的 dadaodao（`scripts/dadaodao_fulltext.py`）：每本先試 PDF 文字層（`hongshi.pdf_text_sufficient`），掃描檔則 Gemini Vision OCR（繁中、保段落）→ 存 R2 `yinshun-hongshi-fulltext/弘誓雙月刊/弘誓雙月刊-NNN.txt`。
- 驅動：`scripts/hongshi_ocr_magazine.py`（resumable：R2 已有 .txt 跳過；2-strike 配額停機；過夜批次）。
- 頁面 `pages/research-data/yinshun-hongshi/magazine/index.vue` 接「全文」鈕 → API 讀該 .txt（同 dadaodao material-text 模式）。

## 檔案索引
- 純函式＋測試：`scripts/hongshi.py` + `scripts/tests/test_hongshi.py`
- 抓取：`hongshi_harvest_magazine.mjs`／`hongshi_download_magazine.mjs`／`hongshi_fill_gaps.mjs`／`hongshi_scrape_log.mjs`／`hongshi_scrape_edm.mjs`
- 發佈：`hongshi_publish_magazine.py`／`hongshi_publish_log.py`／`hongshi_publish_edm.py`（→ R2 + Drive canonical `G:\我的雲端硬碟\公事\印順學派與弘誓研究資料\` + `public/content/research-data/yinshun-hongshi/*-index.json`）
- OCR：`hongshi_ocr_magazine.py`
- 頁面：`pages/research-data/yinshun-hongshi/*`；R2 簽名下載 `server/api/research-data/yinshun-hongshi-file.get.ts`（限 `yinshun-hongshi/` 前綴）
- R2 前綴：`yinshun-hongshi/<刊>/`（原檔）、`yinshun-hongshi-fulltext/<刊>/...txt`（全文）

## See also
[[project_yinshun_hongshi_collection]]（記憶）、[[project_chengzhong_bulletins]]（同 portal 的衛理公會 collection）、[[ebook-pipeline]]（OCR pipeline 同源）、[[feedback_drive_canonical_storage]]。
