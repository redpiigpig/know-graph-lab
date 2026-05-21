---
name: photo-library
description: 「照片庫」多相簿管理系統 — 三個 Drive 相簿（辰瑋／訓練／弘誓）+ /photos 網站瀏覽 + 自動分類腳本（classify_photos.py）+ 統一日期 rename 腳本（rename_photos.py）。Use when 新增一批照片要分月份／截圖／下載歸位、要新增事件資料夾、要在 /photos 加新功能（icon、filter、event tile）、調整分類規則、修網站 photo viewer、把整個資料夾的檔名統一成 `YYYY-MM-DD(N)` 格式、或當使用者問「照片在哪／怎麼整理」。
---

# 照片庫 — Drive 結構 + /photos 網站

> Drive 父目錄：`G:/我的雲端硬碟/資料/儲存資料夾/`
> 網站：[pages/photos/index.vue](../../../pages/photos/index.vue)（library picker，需登入）
> 自動分類器：[scripts/classify_photos.py](../../../scripts/classify_photos.py)
> 統一 rename：[scripts/rename_photos.py](../../../scripts/rename_photos.py)
> **Index**：[scripts/build_photo_index.py](../../../scripts/build_photo_index.py) → `scripts/photo_index.json`（5 MB，gitignored）— server 讀此檔取代 fs.readdir，rename_photos.py auto 跑完自動重建

## 三個相簿

| Slug | 名稱 | Drive 路徑 | 結構 | UI |
|---|---|---|---|---|
| `chenwei` | 辰瑋相片 | `儲存資料夾/辰瑋相片/` | `{YEAR}相片/{YEAR}.MM/` + 截圖/下載/事件 | `/photos/chenwei` 走年月專用頁 |
| `training` | 訓練相片 | `儲存資料夾/訓練相片/` | 平鋪事件夾（`2024.09.01 忠烈祠 宋修傳/` ...） | `/photos/training` 走 [lib]/[...path] 通用 folder browser |
| `hongshi` | 弘誓相片 | `儲存資料夾/弘誓相片/` | 民國年份夾 → 事件夾（多層） | 同上 |

LIBRARIES 註冊在 [server/utils/photos.ts](../../../server/utils/photos.ts) 的 `LIBRARIES` map。新增相簿：加 entry + 確保資料夾 sibling 於 `photosRoot`。

---

## 狀態（2026-05-21）

| Library | Rename 狀態 | 數量 | Thumb prewarm | 備註 |
|---|---|---:|---|---|
| chenwei  | ✅ 完成 (2026-05-19) | 12,863 | ✅ 25,001 thumbs | 2026-05-17 第一輪；2026-05-19 補匯入 594 JPG + 36 MP4（Sony HX99）+ 修 440 iPhone 截圖；2026-05-21 刪 626 個 `.AAE` iPhone sidecar |
| training | ✅ 完成 (2026-05-18 早上) | 4,923 | ✅ 完成 | 50 folders（2026-05-21 刪 5 個 2016 空事件夾 + desktop.ini）|
| hongshi  | 🔄 持續上傳中 | 35,927 | 🔄 ~12% 跑中 | 使用者持續從 Drive 網頁`電腦 > 02. 歷年活動照片-69-119` 補上 |

### 🔄 進行中：hongshi thumb prewarm（重要交接）

跑在 PowerShell Start-Process 啟動的 retry-loop（**PID 18652**，session 死了 process 還活著），idempotent skip 已 cache 的、crash 後自動 relaunch 最多 50 次。

**狀態檔**：
- Loop log：[scripts/logs/prewarm_retry_loop2.log](../../../scripts/logs/) — 每 try 一行 `[try N] starting/exit=X`
- 每 try 子 log：`scripts/logs/prewarm_retry_MMDD_HHMMSS_tryN.log` — 100 檔一個進度行
- Culprit skiplist：`.cache/_prewarm_skiplist.txt` — crash 過的檔，下次跳過
- Current marker：`.cache/_prewarm_current.txt` — 正在處理中的檔（成功會刪、crash 留著）

**快速檢視進度**：
```powershell
# Loop alive?
Get-Process -Id 18652 -ErrorAction SilentlyContinue
# 最新 try 進度
Get-ChildItem scripts\logs\prewarm_retry_*.log -Exclude prewarm_retry_loop*.log | Sort LastWriteTime -Desc | Select -First 1 | % { Get-Content $_.FullName -Tail 5 }
# Cache 大小
(Get-ChildItem -Recurse -File .cache\thumbs | Measure-Object Length -Sum -Property Length) | % { "{0} files, {1:N0} MB" -f $_.Count, ($_.Sum/1MB) }
# Loop 總 try 紀錄
Get-Content scripts\logs\prewarm_retry_loop2.log -Tail 10
```

**判定完成**：最新 try log 結尾出現 `=== Done` + Loop log 寫 `All done after N tries`。預計 hongshi 35,927 張需再跑 ~15-20 小時（已過 ~4,300 張）。

**手動 kill**：`Stop-Process -Id 18652 -Force; Get-Process node | Stop-Process -Force`

### 待辦

1. **等弘誓上傳完** → 使用者會 ping「弘誓傳完了」
2. **搬資料夾**：在 Drive 網頁對 `02. 歷年活動照片-69-119` 右鍵 → 移動 → 我的雲端硬碟/資料/儲存資料夾/弘誓相片/
3. **跑 rename**：
   ```powershell
   $repo = "C:\Users\user\Desktop\know-graph-lab"
   $logDir = "$repo\scripts\logs"
   $stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
   $out = "$logDir\rename_hongshi_$stamp.log"
   $err = "$logDir\rename_hongshi_$stamp.err"
   $py = "C:\Users\user\AppData\Local\Python\bin\python.exe"
   Start-Process -FilePath $py -ArgumentList @("-u", "scripts\rename_photos.py", "auto", "hongshi") `
     -WorkingDirectory $repo -RedirectStandardOutput $out -RedirectStandardError $err -WindowStyle Hidden -PassThru
   ```
4. **跑完後驗證**：log 結尾 `=== AUTO mode done ===`、看 `photo_rename_report_hongshi.json` summary
5. （可選）後續優化：影片 tile 用 `IntersectionObserver` lazy 掛 video element，避免大量影片月份頁初載 metadata 過慢

### 提醒

- **不要**用 Drive 網頁「移動」前先確認本機 D: 那份備份是否要保留 — 移動完雲端 source 沒了，D: 那份 mirror 會跟著被刪。要保留就走 copy（PowerShell `Copy-Item`）而不是 move
- Rename 完跑 / 弘誓掃描期間請勿 push 其他大 Drive 活動，避免 I/O 互卡
- chenwei 重跑會 idempotent skip 但 plan 階段還是要 ~1.5 小時掃 HEIC，沒事不要重跑

### 新增一批 chenwei 照片（標準 workflow，2026-05-19 跑過一次）

當有零散 chenwei 照片要 import（例：相機卡 dump、舊資料夾整理）：

1. **dump 到年根**：JPG 直接搬到 `{Y}相片/`（哪個 Y 沒關係，EXIF 跨年會修正）；MP4 自己按 mtime 進對應 `{Y}.MM/`（classify 對沒 EXIF date 的 Sony 相機 MP4 會誤判為 download，要避開）
2. `python scripts/classify_photos.py plan` → review → `execute`（JPG 全分流到對的 YYYY.MM、截圖、下載）
3. （可選）byte-equal dedup：同 size 桶 SHA-256 比對，留早匯入的、刪重複
4. `python scripts/rename_photos.py plan chenwei` → review → `execute chenwei`
   - 整資料夾按 EXIF 時間重排：新照片時間落在舊照片中間時，舊的會被 renumber 對調 `(N)→(N+1)`
5. rename_photos.py auto 模式跑完自動觸發 build_photo_index；但手動 plan+execute 流程要記得自己跑 `python scripts/build_photo_index.py`

> **MP4 沒 EXIF date**：classify 對 Sony C*.MP4 / 沒 Make 的影片走低信心 → 進 `{Y}下載/`。要手動按 mtime 安置到對的月份夾。Pillow 不開影片，靠 mtime 是 rename_photos.py 的 fallback chain（EXIF → 檔名 → mtime）。
> **新批可能藏 iPhone 螢幕截圖**：classify 的月份內過濾現在已開到 {2014..2026}（[classify_photos.py:213](../../../scripts/classify_photos.py#L213)），高信心 screenshot/download 會自動分流。但 dump 到年根那階段，screenshot 跟 photo 都會走 classify → 進對應 bucket。

---

## 辰瑋相片 — Drive 資料夾結構（單一年份）

```
{YEAR}相片/
├── {YEAR}.01/ ~ {YEAR}.12/      ← 月份夾，放實際拍攝的照片（手機/相機）
├── {YEAR}截圖/                  ← 螢幕截圖（iOS / Android）
├── {YEAR}下載/                  ← 網路下載／第三方來源（無 EXIF 的 Web 圖）
└── <任意事件名>/                ← 保留：旅行、活動、特殊主題集
    例：100字頭合照、2014.11.21、畢士大服務隊、屏東行、法國照片
```

**年份範圍**：2014-2026（13 年）。每年都建滿 01-12 月空夾（給網站 nav 用），實際照片不一定填滿。

**事件資料夾**：用戶手動命名，**自動分類腳本永遠不動**它們。

---

## 自動分類器 — [scripts/classify_photos.py](../../../scripts/classify_photos.py)

### 用法

```bash
# 1. 計畫（dry-run），輸出 scripts/photo_classification_report.json
python scripts/classify_photos.py plan

# 2. 依計畫實際搬檔，留 move log
python scripts/classify_photos.py execute
```

**安全機制**：
- `photo_move_log.jsonl` 每筆搬移都記 `{ts, from, to, bucket}`，可用來反向 rollback
- 同名衝突自動 `_dup2/_dup3` suffix
- **plan 必先跑、報告檢查過再 execute**

### 掃描範圍

| 來源 | 處理方式 |
|---|---|
| `{YEAR}相片/<file>`（散檔）| 全分類搬到對應 bucket |
| `{YEAR}相片/{YEAR}.MM/<file>`（2014-2026 月份內）| 只抽**高信心** screenshot/download，照片留在月份 |
| `{YEAR}相片/<事件夾>/<file>` | 永遠不動 |

> **`SCAN_MONTH_SUBDIR_YEARS = {2014..2026}`**（[classify_photos.py:213](../../../scripts/classify_photos.py#L213)）。月份內過濾只搬高信心結果（screenshot via UserComment / 檔名前綴 / WEBP/GIF/AVIF 明確 download），中／低信心不動 → 全年範圍開啟也安全。2026-05-19 從 {2014..2022} 擴到 {2014..2026}，連同一次性 fix 440 個 iPhone screenshot 從 2023-2024 月份夾遷出。

### 分類規則（依序）

| 條件 | 結果 | 信心 |
|---|---|---|
| 檔名 `Screenshot*` / `截圖*` / `螢幕截圖*` | screenshot | high |
| EXIF UserComment 含 `Screenshot`（iOS）| screenshot | high |
| EXIF Make ∈ {apple, samsung, huawei, htc, asus, google, xiaomi, oneplus, oppo, vivo, realme, lge, motorola} | phone | high |
| EXIF Make ∈ {canon, nikon, fujifilm, olympus, panasonic, ricoh, leica, pentax, sigma, casio, kodak, gopro} | camera | high |
| EXIF Make = sony + model 含 xperia/J9110/J8110/H9436/H8 | phone | high |
| EXIF Make = sony 其他 | camera | high |
| 有 Make 但未知品牌 | phone | high |
| **HEIC/HEIF**（Apple 專屬） | **phone** | med |
| PNG 無 Make + 比例 1.55-2.5 + 短邊 ≤ 1500 | screenshot | med |
| PNG 其他 | download | med |
| WEBP/GIF/AVIF | download | high |
| JPG/影片 無 Make 但檔名有 `20YYMMDD` | phone | low |
| JPG/影片 無 Make 無日期 | download | low |

### 目的地解析

```
screenshot                    → {EXIF年|資料夾年}相片/{年}截圖/
download                      → {EXIF年|資料夾年}相片/{年}下載/
phone/camera + 有 captured    → {EXIF年}相片/{EXIF年}.MM/
phone/camera + 無 captured    → {資料夾年}相片/{資料夾年}未分類/
```

**EXIF 年優先於資料夾年**（若 EXIF 年在 2014-2026 範圍內）。例：2017相片/P_20161003.jpg → EXIF=2016-10 → 搬到 `2016相片/2016.10/`。實測修正了 119 張被誤放的 2016 照片。

### 月份內過濾（重要）

YYYY.MM 月份夾內的檔案**只搬高信心** screenshot/download。中／低信心保持原狀，避免把照片誤判成下載搬走。

→ 一次踩過坑：HEIC 早期沒判斷時被當「下載」誤搬 750 個，後來加 HEIC=phone 規則 + high-conf filter 才解決。Rollback log 在 `photo_rollback_log.jsonl`。

---

## 統一 rename — [scripts/rename_photos.py](../../../scripts/rename_photos.py)

把每個資料夾內的檔案重新命名為 `{S|D|}YYYY-MM-DD(N).{ext}`：

- `S` 前綴 = `{YEAR}截圖/` 內
- `D` 前綴 = `{YEAR}下載/` 內
- 無前綴 = `{YEAR}.MM/` / `{YEAR}未分類/` / 事件夾

日期來源優先：EXIF DateTimeOriginal → 檔名 YYYYMMDD (允許 2000-2026) → mtime。同一天的多張依完整時間（含時分秒）由早至晚排 `(1)(2)(3)...`。HEIC EXIF 讀取靠 `pillow-heif`（已 pip install）。

```bash
python scripts/rename_photos.py plan [LIB]      # dry-run, 寫出 photo_rename_report_{lib}.json
python scripts/rename_photos.py execute [LIB]   # 依 report 兩階段 rename
python scripts/rename_photos.py auto LIB...     # 對每個 LIB 連跑 plan + execute（overnight 用）
```

`LIB ∈ {chenwei, training, hongshi}`，省略時預設 `chenwei`。Library 配置在腳本內 `LIBRARIES` map（root = `PHOTOS_PARENT / 子夾名`）。

`collect_plan()` 用**遞迴 walk** 整個 root，對任何「直接含照片檔」的資料夾排 rename plan（不論深度）。支援三種 layout：chenwei 兩層（YEAR相片/MONTH or event）、training 一層平鋪事件、hongshi 多層巢狀（民國年/事件/photos）。Prefix 由資料夾名單獨判定：`\d{4}截圖$` → S、`\d{4}下載$` → D、其他無前綴。

**兩階段 rename**：先 `src → __rename_tmp_XXXXX.ext`，再 `tmp → 目標名`。避免目標檔名跟另一個檔的當前檔名衝突。崩潰時殘留的 `__rename_tmp_*` 會在下一次 plan 偵測並阻擋 execute。

**idempotent**：已符合格式的不重命名，重跑安全。

### Overnight 排程（脫離 Claude Code session 跑）

`auto` 模式 + PowerShell `Start-Process` 直接 detach python，跑幾小時不受 harness timeout 限制：

```powershell
$repo = "C:\Users\user\Desktop\know-graph-lab"
$logDir = "$repo\scripts\logs"
$stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$out = "$logDir\rename_overnight_$stamp.log"
$err = "$logDir\rename_overnight_$stamp.err"
$py = "C:\Users\user\AppData\Local\Python\bin\python.exe"
Start-Process -FilePath $py -ArgumentList @("-u", "scripts\rename_photos.py", "auto", "chenwei", "training", "hongshi") `
  -WorkingDirectory $repo -RedirectStandardOutput $out -RedirectStandardError $err -WindowStyle Hidden -PassThru
```

`-u` 強制 Python unbuffered stdout，log 即時可讀。看進度：`Get-Content $out -Tail 30` 或直接打開 log 檔。完成判斷：log 結尾出現 `=== AUTO mode done ===`。

> **跟 daily OCR (16:00) 錯開**：daily OCR 那條 Task Scheduler 走 `scripts/run_ocr_daily.bat`，跟 rename 共用 G: I/O。rename 走 overnight 手動 kick off，不放 Task Scheduler。

## Photo thumbnails — sharp + disk cache（必懂）

問題：grid tile 和 lightbox 早期都直接吃原檔 signed URL，iPhone JPG 一張 3-5 MB，一個月 40 張 = 170 MB 從 G: cold cache 串給瀏覽器 → 顯示永遠像「上方一條」progressive JPG 沒解到底。

方案：sharp + libvips 在 server 端 on-the-fly 縮圖、WebP quality 80 重壓、結果寫到 `.cache/thumbs/{hash_前2}/{hash}_{w}.webp`。

- 第一次 cold 縮圖：依 Drive 冷檔狀態 1-100s（Drive 本身慢，不是 sharp）
- 之後同 URL：~25 ms（純本機 disk read），等同 Google Photos
- 寬度白名單 `{240, 480, 800, 1600}`（限制 enumeration、防 cache 爆增）
- Grid tile 用 `?w=480`、lightbox 用 `?w=1600`、`f.url` 仍指向原檔（給「下載」按鈕用）
- 簽章 reuse 原本 file endpoint 的 sig — 同 `(year,segment,name,exp,sig)`，width 不入 sig

實作：
- [server/utils/photo-thumbs.ts](../../../server/utils/photo-thumbs.ts) — `getOrGenerateThumb()` + `thumbCacheKey()` + `generateThumbToCache()`
- [server/api/photos/thumb.get.ts](../../../server/api/photos/thumb.get.ts)（chenwei） + [server/api/photos/lib/[lib]/thumb.get.ts](../../../server/api/photos/lib/[lib]/thumb.get.ts)（training/hongshi）
- Frontend `thumbUrl(url, w)` helper：把 `/file?...` 換成 `/thumb?...&w=N`（[chenwei month page](../../../pages/photos/chenwei/[year]/[month]/index.vue) 和 [lib browser](../../../pages/photos/[lib]/[[...path]].vue) 各一份）
- Prewarm 腳本 [scripts/prewarm_thumbs.mjs](../../../scripts/prewarm_thumbs.mjs)：讀 photo_index.json 走全 library，產 480w + 1600w 兩種寬度

**HEIC 不支援**：sharp 預設沒 libheif（Windows 上 sharp 沒 bundle）。HEIC 從 `renderableImage()` 白名單排除，前端 fallback 到 📄 icon。要支援的話要另外裝 libheif 或換 decoder。

**Prewarm 用法**：
```bash
node scripts/prewarm_thumbs.mjs                # 全部
node scripts/prewarm_thumbs.mjs chenwei        # 只跑 chenwei
node scripts/prewarm_thumbs.mjs --widths=480   # 只跑 grid 寬
```

**Crash-tracking（2026-05-21 patch）**：
- 每張處理前寫 `.cache/_prewarm_current.txt` 為當前 path，成功後刪掉
- 下次啟動偵測到留下的 current.txt → 把那個檔加進 `.cache/_prewarm_skiplist.txt` 跳過
- 連環撞同一張破檔的循環自動斷掉
- 兩個檔不入 git，純運行時 state

**Retry-loop wrapper**（給 hongshi 級別量用，[scripts/_prewarm_retry_loop.ps1](../../../scripts/_prewarm_retry_loop.ps1)）：
node crash → PowerShell wrapper 自動 relaunch 最多 50 次。每 try 寫不同的 log 檔。Drive 中斷 / sharp native crash 全部自動恢復。啟動：
```powershell
$loopOut = "$repo\scripts\logs\prewarm_retry_loop.log"
Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","scripts\_prewarm_retry_loop.ps1") -RedirectStandardOutput $loopOut -WindowStyle Hidden -PassThru
```

預估：cold-state chenwei 12,863 張 × 2 寬度 = 25,726 thumbs 跑 ~8 小時；hongshi 35,927 張要 ~15-20 小時（會 crash 多次靠 retry-loop 自動爬起）。跑完後任何月份首次點開都瞬間。Drive 串流速度緩慢時可先排除 AV：`Add-MpPreference -ExclusionPath 'G:\','...\\DriveFS\\...\\content_cache'`（需 admin）。

**典型 crash**：exit code `-1073741818` = `STATUS_IN_PAGE_ERROR` → Drive 中斷讀；libheif `bad seek` 那串 → HEIC plugin 不支援（無法解，會 fallback 到 📄 icon，但能讓整個 node 死）。Skiplist + retry-loop 雙保險。

## Photo index — server-side（必懂）

問題：早期 `/photos` 頁載入永遠卡「載入中…」。原因是每次刷新 `summarizeLibrary` 都做三 library 遞迴 fs.readdir，G: 是 Drive 鏡像（冷檔還要 fault-in），單次 wall clock 數十秒到分鐘級。

方案：`scripts/build_photo_index.py` 預先 walk 三個 library，把每個 folder 的檔案 metadata（name/kind/ext/size/mtime）寫進 `scripts/photo_index.json`（gitignored，~5 MB）。Server 啟動讀一次 cache，mtime 變化才重 load。所有 list / count API 都改吃 index，瞬間返回。**streaming 照片本體還是直接讀 G:**，不可避免的 I/O。

什麼時候要重跑 build_photo_index：
- 大批 import 完（rename_photos.py auto 跑完 **自動觸發**，見 `cmd_auto` tail）
- 個別 drop 幾張照片到 Drive 直接想在網頁看 → 手動 `python scripts/build_photo_index.py`（25-30 秒走完三 library）
- chenwei 也跑 batch rename 不會自動跑 index（rename auto 才會）— 手動跑 build 即可

實作：
- [scripts/build_photo_index.py](../../../scripts/build_photo_index.py) — walker，原子寫入 `.json.tmp` 再 rename
- [server/utils/photos.ts](../../../server/utils/photos.ts) — `getPhotoIndex()` 讀 + mtime cache、`summarizeLibraryFromIndex` / `listYearsFromIndex` / `getYearMonthsFromIndex` / `listFilesFromIndex` / `listLibraryFolderFromIndex` 五個 builder
- API endpoints 全部 **index 優先，fs fallback**（index 不在時退回原本掃 fs 行為，不會炸）

JSON 大致結構：
```
{
  version: 1, generatedAt,
  libraries: {
    chenwei:  { totalFiles, topFolders, layout:"year-month",
                years: { "2024": { monthCounts, screenshots, downloads, events, buckets: { "01":[...], "screenshots":[...], <event>:[...] } } } },
    training: { totalFiles, topFolders, layout:"folders", folders: { "<subpath>": {folders:[], files:[]} } },
    hongshi:  同 training,
  }
}
```

> URL 簽章不存進 index — `listFilesFromIndex` / `listLibraryFolderFromIndex` 在組 response 時即時呼叫 `signFileUrl` / `signLibFileUrl`，避免 TTL stale。

## /photos 網站

### 路由

| URL | 頁面 | 用途 |
|---|---|---|
| `/photos` | [pages/photos/index.vue](../../../pages/photos/index.vue) | 3 個 library 卡片（library picker）|
| `/photos/chenwei` | [pages/photos/chenwei/index.vue](../../../pages/photos/chenwei/index.vue) | 辰瑋年份 grid |
| `/photos/chenwei/[year]` | [pages/photos/chenwei/[year]/index.vue](../../../pages/photos/chenwei/[year]/index.vue) | 月份 + Other 區 |
| `/photos/chenwei/[year]/[month]` | [pages/photos/chenwei/[year]/[month]/index.vue](../../../pages/photos/chenwei/[year]/[month]/index.vue) | 照片 grid + lightbox |
| `/photos/training` 或 `/photos/hongshi`（含 nested path）| [pages/photos/[lib]/[[...path]].vue](../../../pages/photos/[lib]/[[...path]].vue) | 通用 folder browser（資料夾 + 照片 + lightbox）|

`/photos/chenwei` 由靜態 `chenwei/` 子目錄取勝路由優先順序，所以即使 `[lib]/[[...path]].vue` 也會匹配 `/photos/chenwei`，靜態仍會中標。

### 後端 API

**辰瑋專用（沿用舊路由）**
| Endpoint | 回傳 |
|---|---|
| `GET /api/photos/years` | `{years: [{year, total, monthsWithPhotos}]}` |
| `GET /api/photos/[year]/months` | `{months, screenshots, downloads, events}` |
| `GET /api/photos/[year]/[month]/files` | `{files: [{name, kind, source, ext, size, mtime, url}]}` |
| `GET /api/photos/file?y=&m=&n=&exp=&sig=` | 辰瑋照片本體串流（HMAC-SHA256，1 小時 TTL）|

**多 library 統一 API**
| Endpoint | 回傳 |
|---|---|
| `GET /api/photos/libraries` | `{libraries: [{slug, name, layout, totalFiles, topFolders}]}` |
| `GET /api/photos/lib/[lib]/list?path=` | `{folders: [{name, fileCount, subfolderCount}], files: PhotoFile[]}` |
| `GET /api/photos/lib/[lib]/file?p=&n=&exp=&sig=` | library 照片本體串流（path-based HMAC，1 小時 TTL）|

**批次刪除（直接刪 G: 檔，Drive 同步刪雲端，30 天垃圾桶可救回）**
| Endpoint | body | 行為 |
|---|---|---|
| `POST /api/photos/delete` | `{items: [{year, segment, name}]}` | 辰瑋批次刪 |
| `POST /api/photos/lib/[lib]/delete` | `{items: [{path, name}]}` | 訓練／弘誓批次刪 |

UI：grid 右上角「選取」按鈕進入多選；點 tile toggle 選取（不開 lightbox）；toolbar 顯示「刪除 N」紅按鈕一鍵刪（不問確認，Drive 垃圾桶當 safety net）。實作於 [pages/photos/chenwei/[year]/[month]/index.vue](../../../pages/photos/chenwei/[year]/[month]/index.vue) 與 [pages/photos/[lib]/[[...path]].vue](../../../pages/photos/[lib]/[[...path]].vue)。

### Mobile RWD

- **影片 tile**：`<video preload="metadata" src="{url}#t=0.1" muted playsinline>` 顯示首幀預覽 + ▶ 圓形 badge（不需 ffmpeg / server 端 preview generation）。`.mp4` / `.mov` / `.webm` 多數瀏覽器吃；`.mkv` 看 codec
- **Lightbox swipe**：手機水平滑 >50px、<600ms、水平 > 垂直 → prev/next（touchstart/touchend handler）
- **多層 breadcrumb mobile 隱藏**：所有 `<nav>` 都加 `hidden sm:flex`，靠 AppHeader 的「← 上一層」回去
- **Header / toolbar wrap**：右側 stats + selection toolbar 都加 `flex-wrap`，小機型不會被擠出邊界
- 各層 grid breakpoint：library picker 1→3 / 年份 2→3→4 / 月份 3→4→6 / 照片 2→3→4→5→6 / folder 1→2→3→4

### 圖片 URL 簽章

[server/utils/photos.ts](../../../server/utils/photos.ts) 的 `signFileUrl(year, segment, name)`：
- HMAC payload：`{year}|{segment}|{name}|{exp}`
- secret：`ENCRYPTION_KEY` 或 fallback `SUPABASE_SERVICE_ROLE_KEY`
- segment 可為 `01`-`12` / `screenshots` / `downloads` / 任意事件夾名
- `<img src>` 直接吃簽章 URL，不需前端帶 Authorization

### bucketDir 與 source

[server/utils/photos.ts](../../../server/utils/photos.ts):

```ts
bucketDir(year, segment):
  "01".."12"          → {year}相片/{year}.{segment}/
  "screenshots"       → {year}相片/{year}截圖/
  "downloads"         → {year}相片/{year}下載/
  其他（事件夾名）    → {year}相片/{segment}/    （path-traversal 防護）

sourceForSegment(segment) → "photo" | "screenshot" | "download" | "event"
```

`listFiles` 把 `source` 灌進每個 file 物件，前端 tile 右上角 badge 用：

| source | icon | 提示 |
|---|---|---|
| photo（kind=video）| 🎬 | 影片 |
| photo | 📱 | 手機／相機拍攝 |
| screenshot | 📸 | 螢幕截圖 |
| download | 🌐 | 網路下載 |
| event | 📁 | 事件資料夾 |

### 視覺設計

暖米色背景 `#f5f1ea` + 奶油卡片 `#fdfbf6`、襯線數字、細線分隔、單色 mono uppercase 標籤。Hover：lift -2px + 細線變長 + 滑入箭頭。空年份／月份用虛線邊框淡化。Lightbox：黑底、琥珀色 accent、← → / Esc 鍵控。

---

## 常見任務

### 新增一批照片

1. 把照片丟到 `G:/我的雲端硬碟/資料/儲存資料夾/辰瑋相片/{YEAR}相片/`（直接放年份根目錄）
2. `python scripts/classify_photos.py plan`
3. 看 stdout summary：screenshot / download / photo / undated 各幾張
4. 抽查 5-10 筆 (`python -c "import json; ..."` 看 `photo_classification_report.json`)
5. `python scripts/classify_photos.py execute`
6. Drive desktop 自動同步上雲

### 新增事件資料夾（特殊主題集）

直接在 Drive 開資料夾（任意中文／英文名）放進 `{YEAR}相片/<名稱>/`。網站會自動偵測為 📁 事件 tile 顯示在年份頁 Other 區。**不需要改 code**。

### 修改分類規則

[scripts/classify_photos.py](../../../scripts/classify_photos.py) 的 `classify()` function。常改的地方：
- 新增手機品牌：`PHONE_MAKES`
- 新增相機品牌：`CAMERA_MAKES`
- Sony 是手機還相機：`SONY_PHONE_MODEL_HINTS`
- 截圖偵測規則：尋找 `"Screenshot"` 字串或 `ext == ".png"` 區段

### 刪除 / Rollback 誤搬

`scripts/photo_move_log.jsonl` 每行：`{ts, from, to, bucket}`。寫個 5 行 Python 反向搬即可（範例：[scripts/classify_photos.py](../../../scripts/classify_photos.py) 之前已用過一次 rollback 750 個 HEIC 誤判）。

### 加新 tile 圖示／類型

1. 後端：`PhotoSource` type 加新值、`sourceForSegment` 加判斷、bucketDir 加路徑
2. 前端 [pages/photos/chenwei/[year]/[month]/index.vue](../../../pages/photos/chenwei/[year]/[month]/index.vue) 的 `tileIcon` / `sourceTitle` 加 mapping
3. 年份頁 [pages/photos/chenwei/[year]/index.vue](../../../pages/photos/chenwei/[year]/index.vue) Other 區加新卡

### 加新 library

1. [server/utils/photos.ts](../../../server/utils/photos.ts) 的 `LIBRARIES` map 加 entry（slug / name / folder / layout）
2. `LibrarySlug` union 加新 slug、`isLibrarySlug` 也補
3. [pages/photos/index.vue](../../../pages/photos/index.vue) 的 `libIcon` 加 emoji
4. [pages/photos/[lib]/[[...path]].vue](../../../pages/photos/[lib]/[[...path]].vue) 的 `LIB_META` 加 name+icon
5. Drive 上建 sibling 資料夾（位於 `儲存資料夾/` 下）；layout=year-month 走辰瑋專用頁，layout=folders 走通用 browser

---

## 已知地雷

- **不要對 YYYY.MM 內部跑低信心 download 分類** — HEIC、IMG_xxxx.JPG 被剝 EXIF 的 iPhone 照很容易誤判為「下載」。`classify_photos.py` 已加 `confidence != "high"` filter 守門
- **Drive sync 慢** — 移動 5000+ 檔後雲端要幾分鐘到一小時才同步完。本機 G: 已對齊，但網站若部署在別處看到的可能還是舊雲端狀態
- **檔名編碼** — 終端 (Git Bash) 顯示中文檔名常變亂碼（cp950 vs utf-8），但檔案本身沒問題
- **Pillow 不開影片** — `.MOV/.MP4` 的 EXIF 抓不到，只靠檔名 `V_YYYYMMDD_HHMMSS` 推時間。iPhone 影片檔名沒日期 → 落入 low conf。Sony C*.MP4 也一樣（鏡頭+型號在 XML sidecar 不在 MP4 EXIF）→ 要先按 mtime 手動分月，再 rename
- **HEIC 必為 iPhone** — 即使 Pillow 沒讀到 Make，HEIC 副檔名本身就是判斷依據（沒人會下載 HEIC）
- **多個 plan 在跑會 race** — 同時 `python classify_photos.py plan` 跑兩次會互相覆蓋 `photo_classification_report.json`。execute 前確認 plan 跑完且沒有殘留背景 process
- **iPhone 螢幕截圖混在月份夾**（2026-05-19 遇到）— iPhone PNG 截圖 750×1624 比例 2.17、Make 缺、UserComment 含 "Screenshot"。原本 `SCAN_MONTH_SUBDIR_YEARS` 卡 {2014..2022}，2023+ 月份夾完全不掃 → 440 個截圖混在月份；現已擴到 {2014..2026}。新 batch 進來會自動分流；歷史漏網用 EXIF UserComment 過濾移走
- **photo_index stale** — 大批操作（搬檔、刪檔、rename auto 以外）完要 `python scripts/build_photo_index.py` 才會在 web 看到，否則 /photos 顯示舊狀態。`.AAE` / `desktop.ini` 不在 IMAGE_EXTS/VIDEO_EXTS 白名單內，所以刪它們不影響 index totalFiles
- **`.AAE` Apple Photos edit sidecar**（2026-05-21 清除 626 個）— iPhone 在 Photos.app 編輯（裁切／濾鏡）會留 `IMG_xxxx.AAE` 純 XML edit instruction，rename_photos.py 不認識 `.AAE` 副檔名跳過 → 跟 IMG_xxxx.JPG 配對殘留在月份夾。離開 iPhone Photos.app 生態無用，可直接 unlink；新批匯入未來若再見要重複清。Cleanup log：`scripts/aae_cleanup_log.json`
- **training nested empty folders**（35 個尚未清）— `一般相片/家庭照片/合照`、`fitcasting/<workout>` 等 32 個都是空，疑似刪檔後沒清資料夾。沒影響網站顯示（getPhotoIndex 不會把空 folder 列為瀏覽 entry）但堆在 Drive 結構裡。要清的時候列 `pathlib.Path('G:/我的雲端硬碟/資料/儲存資料夾/訓練相片').rglob('*')` filter is_dir+empty 一次跑掉

---

## 統計（2026-05-16 大整理後）

## chenwei 統計（2026-05-19）

| 年 | YYYY.MM | 截圖 | 下載 | 事件夾 |
|---|---:|---:|---:|---:|
| 2014 | 0 | 0 | 0 | 132 |
| 2015 | 24 | 0 | 1 | 76 |
| 2016 | 123 | 0 | 4 | 939 |
| 2017 | 36 | 0 | 4 | 479 |
| 2018 | 2,372 | 0 | 0 | 15 |
| 2019 | 2,483 | 0 | 1 | 0 |
| 2020 | 25 | 0 | 0 | 89 |
| 2021 | 453 | 3 | 0 | 78 |
| 2022 | 1,508 | 294 | 0 | 0 |
| 2023 | 1,565 | **308** | 0 | 0 |
| 2024 | 1,719 | **132** | 0 | 0 |
| 2025 | 0 | 0 | 0 | 0 |
| 2026 | 0 | 0 | 0 | 0 |

chenwei totalFiles **12,863**（含 12,233 起始 + 630 新匯入 + 440 iPhone screenshot 從月份夾遷至截圖夾／不是新增）。`.AAE` sidecar 不入 IMAGE_EXTS 白名單，2026-05-21 unlink 626 個 不影響此 total。

歷次大整理動的檔次：
- 2026-05-16 初版大整理：5,370 個檔（5,063 散檔→月份 + 297 月份→截圖 + 10 散檔→下載 + 119 cross-year 修正）
- 2026-05-19 Sony HX99 dump：594 JPG + 36 MP4 從 `C:\Users\張辰瑋的資料\新增資料夾\` 匯入 + 774 個檔 rename（含舊照片被新照片擠開的編號對調）
- 2026-05-19 iPhone screenshot 漏網修補：440 個 PNG 從月份夾 → `{Y}截圖/`，1,906 個檔 rename（含 S 前綴 + 月份夾 gap 補正）
- 2026-05-21 lint cleanup：chenwei `.AAE` Apple Photos 編輯 sidecar 626 個全 unlink；training `desktop.ini` 1 個 + 5 個 2016 空事件夾移除 → training top-level 從 55 降到 50
