---
name: photos-library
description: 「照片庫」多相簿管理系統 — 三個 Drive 相簿（辰瑋／訓練／弘誓）+ /photos 網站瀏覽 + 自動分類腳本（classify_photos.py）+ 統一日期 rename 腳本（rename_photos.py）。Use when 新增一批照片要分月份／截圖／下載歸位、要新增事件資料夾、要在 /photos 加新功能（icon、filter、event tile）、調整分類規則、修網站 photo viewer、把整個資料夾的檔名統一成 `YYYY-MM-DD(N)` 格式、或當使用者問「照片在哪／怎麼整理」。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

# 照片庫 — Drive 結構 + /photos 網站

> ☁️ **雲端顯示（redpiigpig.com / Zeabur）走 Drive+R2 hybrid**，見下方「## 雲端 R2 hybrid」。本機 dev 不受影響、仍直讀 G:。

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

## 狀態（2026-05-22）

| Library | Rename 狀態 | 數量 | Thumb prewarm | 備註 |
|---|---|---:|---|---|
| chenwei  | ✅ 完成 (2026-05-19)＋ 159 stragglers 待跑 | 13,022 | ✅ 25,001 thumbs | 2026-05-17 第一輪；2026-05-19 補匯入 594 JPG + 36 MP4（Sony HX99）+ 修 440 iPhone 截圖；2026-05-21 刪 626 個 `.AAE` iPhone sidecar；2026-05-21 audit 發現 3 個事件夾共 159 檔未 rename（見「待辦 #5」，prewarm 完可跑）|
| training | ✅ 完成 (2026-05-18 早上) | 4,923 | ✅ 完成 | 50 top folders（2026-05-21 刪 5 個 2016 空事件夾 + desktop.ini）；2026-05-21 再刪 35 個 nested empty subfolder（fitcasting 32 + 一般相片 2 + 2021.08.21 ipad相片 1，log: [scripts/training_empty_dirs_cleanup_log.json](../../../scripts/training_empty_dirs_cleanup_log.json）|
| hongshi  | 🔄 持續上傳中（等使用者 ping） | 35,927 | ✅ 完成 (2026-05-22 11:25) | 使用者持續從 Drive 網頁`電腦 > 02. 歷年活動照片-69-119` 補上 |

### ✅ Hongshi thumb prewarm 完成（2026-05-22 11:25）

跑了 **18 tries / 27.2 h**（2026-05-21 08:13 → 2026-05-22 11:25），最終 try 18 從 07:57 跑到 11:25 = **3.46 h** 一口氣 break through 完成。

**最終 stats**（try 18 final）：
- Total files: **40,133**（training 4,923 + hongshi 35,210 — index snapshot 比 SKILL 記的少 717，含一些 stale entry）
- Generated: **13,998**（本 try 新生）
- Already in cache: **65,376**
- Errors: **258**（全部是 HEIC — sharp 在 Windows 沒 bundle libheif，無法 decode；前端 `renderableImage()` 本來就跳過 HEIC、fallback 📄 icon，所以不影響運作）
- Skiplist final: 317 entries（含 300 個 2026-05-21 21:50 手動 preempt 的 `93年/930703-930731` STATUS_IN_PAGE_ERROR 死區檔，這 300 檔首次點該月份要 cold thumb 生成）

**Try crash 史**：
- try 1（08:13–08:19）：Drive 醒身崩，9,400 檔
- try 2（08:19–16:23 = 8h）：crash @ 25,500，生 32,014 thumbs ⭐
- try 3–15（16:23–21:53 = 5.5h）：13 次連環短崩，全卡在 27,200-27,400 死區
- try 16（21:53–22:05 = 12 min）：break through @ 27,700
- try 17（22:05–07:38 = 9.5h）：crash @ 33,100，生 10,182 thumbs
- **try 18（07:57–11:25 = 3.5h）：穩定推進到 `=== Done` ✅**

**後續優化候選**（非必修）：
- prewarm_thumbs.mjs 的 `SUPPORTED_EXTS` 含 `.heic/.heif` → 每次 prewarm 必撞 258+ HEIC errors。可從白名單拿掉這兩個 ext，下次跑乾淨。

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
5. ~~**chenwei 159 stragglers**~~ ✅ 完成 (2026-05-22 14:36)：159 全部 rename 成功，全部走 EXIF（SKILL 原本預測「無 EXIF」全錯）。處理三個 audit 漏網事件夾，繞過 chenwei full plan 1.5+ 小時 walk，靠 [scripts/rename_chenwei_stragglers.py](../../../scripts/rename_chenwei_stragglers.py)（reuse `rename_photos.py` 的 `collect_folder_plan` / phase1+2 邏輯）只對三個目標資料夾跑 plan + execute，5 秒搞定：
   - `2019相片/法國照片/劭瑋手機相片/` — 64 檔 HTC `P_20190705_xxx.jpg` → `2019-07-05(1).jpg` 等（EXIF）
   - `2019相片/法國照片/相機相片/` — 62 檔 Canon `IMG_0661.JPG` → `2019-07-03(1).jpg` 等（EXIF；該夾共 83 檔，其中 21 個已符合格式 skip）
   - `2016相片/03.19石門區心靈之旅/新增資料夾/` — 33 檔 `獅頭山、老梅石槽、富貴角、富基漁港、廟宇_xxxx.jpg` → `2016-03-19(1).jpg` 等（EXIF 完整保留，跟父資料夾活動日期吻合）
   - **教訓**：未來新 audit 散檔的時候，**先直接看資料夾名跟內容**（PowerShell ls 一次），不要憑 SKILL 文件記憶推斷 — 上次 audit 文件記載的「美女的圖片東西區」「下載梗圖」「無 EXIF」全部錯
6. ~~（可選）後續優化：影片 tile 用 `IntersectionObserver` lazy 掛 video element~~ ✅ 完成（2026-05-21）— [components/LazyVideoTile.vue](../../../components/LazyVideoTile.vue) 取代兩個 grid page 的 inline `<video preload="metadata">`，placeholder 在 200px viewport margin 內才掛真 video，避免 50+ 影片的月份頁初載 metadata storm

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

## 雲端 R2 hybrid（redpiigpig.com 顯示，2026-06-13）

**問題**：`/photos` 照片是即時從本機 `G:/…/儲存資料夾/` 讀檔串流。redpiigpig.com 部署在 **Zeabur 雲端（Linux）**，沒有 G: 槽，連 index（gitignored）都沒有 → 公開網址一張照片都看不到（結構性，非壞掉）。

**方案**：比照電子書「Drive 原檔 + R2 derivatives」hybrid。**原檔留 Drive 不動（canonical）**，只把 **index + 網頁用縮圖（480w grid + 1600w lightbox）** 推到 R2；雲端從 R2 讀。看圖全程走 `/thumb` 端點（grid `thumbUrl(f.url,480)`、lightbox 1600），所以縮圖上 R2 即覆蓋整個看圖體驗。

**開關**：`PHOTO_BACKEND` 環境變數 — 預設 `local`（dev 直讀 G:，零回歸）；Zeabur 設 `PHOTO_BACKEND=r2`。在 `nuxt.config` runtimeConfig（私有 `photoBackend` + `public.photoBackend` 給前端判影片占位）。

**R2 key**（與端點 `thumbCacheKey` 一致）：
- index：`photos/index.json`
- thumb：`photos/thumb/{cacheKey}_{w}.webp`，`cacheKey = sha256(parts).slice(0,32)`；chenwei parts=`["chenwei",y,bucket,name]`、lib parts=`["lib",slug,subpath,name]`。helper：`r2ThumbKey()`/`r2IndexKey()`（[server/utils/photos.ts](../../../server/utils/photos.ts)）。

**改動點**：
- [server/utils/photos.ts](../../../server/utils/photos.ts)：`photoBackend()`、`r2ThumbKey`/`r2IndexKey`、`getPhotoIndex()` r2 分支（從 R2 抓 `photos/index.json`，5 分鐘 TTL 記憶體 cache）
- [server/utils/photo-thumbs.ts](../../../server/utils/photo-thumbs.ts)：`getThumbFromR2(cacheKey,width)`（r2SignedUrl+fetch，回 Buffer/null）
- 兩個 thumb 端點 + 兩個 file 端點：r2 分支 — thumb 取 R2 webp（miss→404）；file 圖片降級供 1600w R2 縮圖、影片 404
- 前端 [components/PhotoFolderBrowser.vue](../../../components/PhotoFolderBrowser.vue) + [chenwei month page](../../../pages/photos/chenwei/[year]/[month]/index.vue)：`isCloud` 時影片 tile/lightbox 顯示 🎬 占位不掛 `<video>`

**同步腳本**：[scripts/sync_photos_to_r2.mjs](../../../scripts/sync_photos_to_r2.mjs)（**只能本機跑**，原檔只在 G:）
```bash
node scripts/sync_photos_to_r2.mjs --dry-run     # 估數量+容量（不上傳、不碰 R2）
node scripts/sync_photos_to_r2.mjs               # 全三相簿（長時間、可續跑）
node scripts/sync_photos_to_r2.mjs chenwei       # 單相簿
node scripts/sync_photos_to_r2.mjs --index-only  # 只重傳 index（新增照片後快速更新清單）
```
- 可續跑：啟動 ListObjectsV2 撈 R2 既有 thumb 成 Set，已存在跳過；crash-marker+skiplist 同 prewarm（`.cache/_r2sync_*`）
- 跳過 video / HEIC（雲端不播 / Windows sharp 無 libheif）
- **規模（2026-06-13 dry-run）**：52,619 圖 → 105,238 物件 ~7.6GB（R2 免費 10GB 內、略緊）；1,094 非圖/HEIC 跳過
- ⚠️ **新增照片後要重跑**（含 `--index-only` 重傳 index）雲端才看得到，如同本機要重跑 `build_photo_index.py`。後續可併進 rename auto 流程

**部署**：Zeabur 設 `PHOTO_BACKEND=r2`（R2_* / ENCRYPTION_KEY 既有 ebook 功能已設）→ 重部署。

**已知限制（v1）**：雲端影片不能播（🎬 占位）；雲端「下載原檔」實得 1600w webp（非原畫質）；HEIC 雲端仍 📄（同本機現況）。

**測試**：[test/photos/photos.spec.ts](../../../test/photos/photos.spec.ts) 加 `r2ThumbKey`/`r2IndexKey` + 「thumbCacheKey 演算法＝sync 腳本」invariant（25 cases 綠）。

---

## 媒體瘦身：影片 HEVC 轉碼 + HEIC→JPG（2026-06-20）

> 動機：訓練相簿影片爆量（445 支 = 173.5 GB，多半是螢幕/擷取卡錄製，49Mbps + 未壓縮 PCM 音訊，浪費極大）；HEIC 照片在 sharp 無 libheif 下無法縮圖、網站顯示 📄/破圖。

### 影片轉碼 — [scripts/transcode_videos.py](../../../scripts/transcode_videos.py)

就地把訓練（全部 >20MB）+ 弘誓（>50MB）影片轉成 **HEVC（`hevc_nvenc` cq26 preset p6，RTX 4050 GPU 硬編）**。樣本實測省 ~80%（VMAF 95.95＝視覺透明）；H.264 cq23 則省 ~65% 但相容性最佳（當初選 HEVC）。

- **安全**：編到本機暫存（`c:/tmp/transcode_work`，不碰 Drive）→ 驗時長(±1s/±1%)+解析度一致+壓後 ≤85% → 才 copy 到 G: 同夾 `.tmp` 並同卷 `os.replace` atomic 覆蓋原檔（檔名/副檔名不變）。Drive 30 天垃圾桶當保險。
- **跳過**：已是 hevc 且 <12Mbps（已優化）、壓後不夠小（保留原檔）。
- **ledger** `scripts/transcode_ledger.json` 可續傳。容器保留 mp4/mov/m4v（都能裝 hevc，檔名不變不擾動 index/rename）。音訊已 aac/mp3 直接 copy、PCM 才轉 aac 192k。
- 用法：`--list` 看清單、`--limit N` 測試、無參數實跑。**用 `C:\Users\user\AppData\Local\Python\bin\python.exe`**（bash 的 `_whisper_venv` python 缺套件）。

### HEIC→JPG — [scripts/convert_heic_to_jpg.py](../../../scripts/convert_heic_to_jpg.py)

三相簿所有 HEIC/HEIF 就地轉 JPG（pillow-heif 開檔，quality 92，**保留 EXIF 含日期與方向**）。轉完縮圖/瀏覽/雲端全部正常（解 📄 根因）。jpg 比 heic 略大（總量僅 ~357MB，可忽略）。盤點：chenwei 196 + training 10 + hongshi 11 = 217 張。ledger `scripts/heic_convert_ledger.json` 可續傳。**副檔名變了，轉完必跑 `build_photo_index.py`**。

### 整夜序列 — [scripts/_media_optimize_run.ps1](../../../scripts/_media_optimize_run.ps1)

`Start-Process` detach 跑：HEIC→JPG → 重建 index → 影片轉碼 → 重建 index，log 寫 `scripts/logs/media_optimize_*.log`。各步驟用上述 AppData python。

> ⚠️ **雲端要看到成果**：影片不影響雲端（雲端本來就 🎬 占位）；但 HEIC→JPG 後那 217 張要重跑 [sync_photos_to_r2.mjs](../../../scripts/sync_photos_to_r2.mjs)（`--index-only` 至少重傳 index，理想是補傳新 jpg 的縮圖）雲端才會從 📄 變成正常顯示。
> ⚠️ **HEVC 播放**：VLC / 手機 / 現代電視原生支援；Windows 內建「相片/電影與電視」需到 Microsoft Store 裝一次免費 HEVC 擴充元件。

---

## 訓練相簿 D: 備援補檔 + 轉碼（2026-06-25 起，**✅ 全部完成含 fitcasting**）

> 背景：使用者帶來 `USB 1TB (D:)` 的 `D:\資料\`＝訓練相簿的**原始母片備份**（原相機檔名、未更名未轉碼）。Drive 上的訓練相簿（更名+轉碼工作版）**影片大量缺漏、部分照片也缺**。任務＝比對 → 補缺到 Drive → 更名 → 轉碼（影片 HEVC、HEIC→JPG）。

### 🚨 D: 槽硬體不穩
列得出頂層資料夾名（MFT 快取），但**讀資料夾內容會 I/O device error / 卡死**。重插換 USB 孔後可讀一陣子。所有 D: 讀取都要容錯（per-file retry）、且**只讀不寫**（拔了不會壞 D: 資料）。多任務勿同時壓 D:。

### 比對方法（D: 母片 vs Drive 工作版，檔名對不上因為 Drive 已更名/轉碼）
- **逐夾數量比對**用線上 `photo_index.json` 當 G: 來源（別遞迴 walk G:，Drive 冷檔 fault-in 會超時）；D: 則 live 掃。
- **照片補缺**：用「位元組大小」多重集合比對（更名不改 bytes，stat-only、對不穩硬碟最溫和）。HEIC→JPG 的會對不上 size → 另計。
- **影片補缺**：用 **ffprobe 時長**比對（轉碼保留時長±2s）；G 該夾影片=0 就全補。

### ✅ 已完成（都已落地 Drive `訓練相片/`）
1. **6 個整夾缺失** → robocopy 補上：`2016.05.04 張文軒 / 2016.05.07 童瑞琪 / 2016.06.21 江韋利 / 2016.07.01 林大為 / 2016.07.02 林政瑋 / 2023.09 中正`（825 檔 18GB，數量核對 OK）
2. **事件夾內缺漏**：1209 檔 24GB（含 2016–2020 整批缺的影片、`2021.08.21 孫凱駿` 181 張 iPad HEIC）
3. **一般相片**：224 檔 8GB（**1 個 y2mate 超長檔名下載片 Drive 拒收、略過**——非訓練照）
4. **fitcasting 轉碼補檔 582/613**：HEVC nvenc 轉碼後落地，多數是已壓縮的下載片（HEVC 打不過→改 copy_raw 原檔），只省 ~13GB；真省的是少數高位元率螢幕錄影

### ✅ 收尾連鎖（2026-06-25 11:58 完成）
`scripts/_training_final_pass.ps1` 跑完全綠：rename auto training → convert_heic_to_jpg(181) → build_index → transcode_videos(新事件影片) → build_index → R2。訓練 index totalFiles **4,923→7,730**。
- 已給 `transcode_videos.py` 加永久排除政策 `TRAIN_EXCLUDE_TOP = {2017, fitcasting, 一般相片, 新增資料夾}`（這些夾不轉碼）。
- 各步 idempotent，要重跑直接跑整支 ps1。

### ✅ fitcasting 補檔 + 去重完成（2026-06-26 凌晨，D: 重插後）
1. **補 fitcasting 剩 31 支 DONE**：`python scripts/fitcasting_transcode_fill.py`（ledger resume）跑完 `613/613 · hevc=8 · fail=0 · 省 5.2GB`；training index 7,730→**7,745**（+15 新片）。D: 讀取全程零 I/O error。判 hang 看 **ffmpeg 子程序** CPU（python 父程序 CPU 低是正常，ffmpeg 才是 nvenc worker）。
2. **fitcasting 去重 DONE（dry-run，未刪）**：[scripts/fitcasting_dedup_check.py](../../../scripts/fitcasting_dedup_check.py) 比子夾 18 支 vs root 597 支時長(±2s)。「最壞 18 支重複」實際**只 2 支疑似重複**：`new\2025-11-24(3).mp4`(3227s)↔`One_Day…Ilya…PunishmentRoom.mp4`＋`Punishment_Room_-_Ilya_One_Day….mp4`（root 內疑有兩份同片）、`新增資料夾\2025-11-24(6).mp4`(3889s)↔`Punishment_Room_-_Ilya_Epic_Punishments.mp4`。其餘 16 支是唯一長片(2025-11、86–103 分，不在 D: 母片)。**待 user 定奪刪哪份**（skill 政策：留早匯入的）。
3. **收尾未跑整支 `_training_final_pass.ps1`**：它第一步 `rename auto training` 會逐檔讀冷檔 EXIF、在 Drive 不穩時 wedge G: 句柄（同 chenwei classify/rename 卡死症）。**改只跑必要安全步驟**：`build_photo_index`（+新片）→ `sync_photos_to_r2 training`（thumbs，0 err）→ `--index-only`。rename 純命名一致性、event 夾 11:58 已更名、fitcasting 保留原描述性檔名即可，故略過。
- 腳本：[scripts/fitcasting_transcode_fill.py](../../../scripts/fitcasting_transcode_fill.py)、[scripts/fitcasting_dedup_check.py](../../../scripts/fitcasting_dedup_check.py)、[scripts/_training_final_pass.ps1](../../../scripts/_training_final_pass.ps1)（rename-first，wedge 風險，慎用）

### 🎬 雲端影片播不了（2026-06-26 診斷，待做 Drive 嵌入）
手機/平板連的是雲端 `PHOTO_BACKEND=r2`；[server/api/photos/file.get.ts](../../../server/api/photos/file.get.ts) 在 r2 模式**影片一律 404**（R2 只存縮圖、無影片原檔；Supabase Storage 禁用）。影片原檔只在 G:/本機，故只有 local 模式播得出來。次要問題：多數訓練/fitcasting 片是 **HEVC**（Android Chrome 原生 `<video>` 不支援）、且串流端**沒做 HTTP Range**（iOS Safari 需要）。
- **已定方案＝Drive 預覽嵌入**：把影片 Drive 檔案 ID 寫進 index，雲端影片 tile 改嵌 `drive.google.com/file/d/{id}/preview`，靠 user 手機既有 Google 登入驗證播放、Drive 自動轉碼(解 HEVC)、R2 不存影片。需接 Drive API 抓檔案 ID（要 Google Cloud API 憑證）。App 現為 **Supabase 登入**、無 Google OAuth/Drive API。時程：**收完照片任務後做**。

### 引擎/設定備忘
- 轉碼一律 `C:\Users\user\AppData\Local\Python\bin\python.exe`（bash venv 缺套件）
- HEVC 設定同 `transcode_videos.py`：`hevc_nvenc -preset p6 -rc vbr -cq 26 -tag:v hvc1 +faststart`，音訊 aac/mp3… copy 否則 aac192k；驗時長±/解析度/≤85% 才用，否則 copy 原檔
- 磁碟：G:（Drive 鏡像）與 C: 同實體碟、本機僅 ~3GB free；但 Drive 上傳後驅逐本機 cache，所以大量複製靠雲端配額不靠本機空間（一次一檔轉碼即可，勿堆積）

---

## 辰瑋相簿 本機 C: 大缺口補檔（2026-06-25，**✅ 已正確重跑完成（夜）**）

> 來源：`C:\Users\張辰瑋的資料\辰瑋相片\`（2014–2024相片）＝辰瑋本機完整集；比對發現 **G: 辰瑋相簿約缺一半**。

### 比對結果（用 photo_index size 多重集合比，jpg 只更名不改 bytes → size 對不上＝真缺）
- **一般 img/vid 缺 12,507 檔 / 45.3 GB**，集中 2022(2217)/2023(4627)/2024(3845)；非重複（C: 24,562 媒體檔只有 186 同 size 重複）
- **HEIC**：C 共 629（G 只轉過 196）；**CR2 RAW 21 檔 G 完全沒有**
- C: 結構：**2021–2024 已在 `{Y}.MM` 月夾**（同 G:，直接落對應月夾免 classify）；2014–2020 事件子夾(心靈之旅等)+部分散檔
- 使用者決策：**全部補上**（走 classify+rename）；**CR2 補、HEIC 補（轉 JPG）**

### 🔥 2026-06-25 過量複製事故 + 回復（重要教訓）
**經過**：訓練收尾最後一步 `build_photo_index` 執行時 **G: 閃斷** → `root.exists()=False` → 三相簿全 0 的空 index 被 atomic 覆寫好 index，且傳上 R2（雲端一度全空）。接著 `chenwei_fill_from_local.py` 讀到空基準 → 全部誤判為缺 → **把整個 C: 86.6GB / 25,212 檔全複製**到 G:（大量重複）。
**回復（已完成）**：
1. 緊急停掉 chenwei 鏈（classify 還沒 execute，沒亂搬）
2. 用「**建立時間 ≥ 2026-06-25 11:55**」精準辨識過量複製（只有那次寫 chenwei）→ 刪掉 25,212 檔/86.6GB（Drive 30 天垃圾桶當保險），chenwei 回到 13,040
3. 重建 index（chenwei 12,857 ✓ / training 7,730 / hongshi 35,819）+ R2 --index-only 修好雲端
4. 刪掉被污染的 `C:\tmp\chenwei_fill_ledger.json`（全標 done，會害 re-run 全跳過）
**防呆（已加、已 push）**：`build_photo_index.py` 三相簿全 0 拒寫覆蓋(exit 2)；`chenwei_fill_from_local.py` G chenwei 基準 size <2000 即 ABORT。

### ✅ 正確重跑方式（事故已清乾淨，可安全重跑）
**前置檢查**：`python scripts/build_photo_index.py` 後確認 chenwei totalFiles≈12,857（不是 0）；且 `C:\tmp\chenwei_fill_ledger.json` 不存在。
跑 [scripts/_chenwei_fill_pass.ps1](../../../scripts/_chenwei_fill_pass.ps1)（detached，**訓練已完成，現在可直接跑**）：
1. [scripts/chenwei_fill_from_local.py](../../../scripts/chenwei_fill_from_local.py)：缺的 img/vid 依**相同相對路徑** copy 到 G（2021-24 直落月夾、2014-20 保留事件夾）；CR2 全 copy；HEIC 轉暫存 jpg(q92)→ size 比對 G，已在跳過否則 jpg 直落。**開頭會印 `distinct=12xxx`，若印 <2000 會自動 ABORT**（基準壞）。ledger `C:\tmp\chenwei_fill_ledger.json` 可續
2. `classify_photos.py` plan+execute（散檔分月，月夾/事件夾不動；move log 可 rollback）
3. `rename_photos.py auto chenwei`（更名+重建 index，慢：逐檔讀 EXIF 冷檔）
4. `build_photo_index.py` + `sync_photos_to_r2.mjs chenwei` + `--index-only`
- log：`C:\tmp\chenwei_pass.log`，結尾 `=== CHENWEI_PASS DONE ===`
- 正常結果應該是 copied≈12,507 + cr2 21 + heic_new≈4xx + **heic_skip≈196**（被去重），**不是 24,562**
- ⚠️ Drive 雲端配額要夠 ~45GB
- 收尾後另跑 `node scripts/sync_photos_to_r2.mjs training`（補訓練新照片縮圖，11:58 那次跑在空 index 上沒生效）

### ✅ 實際重跑結果（2026-06-25 夜，DONE）
- **前置檢查綠**：index chenwei=12,857（非 0）✓ / ledger 不存在 ✓ → 安全閘 `distinct=12726` ✓（基準健康，86GB 事故結構上不可能重演）
- **fill 成果**：copied=12,411 + cr2=21 + heic_new=432 + heic_skip=197 + 補漏 126 = **共 ~47GB**（**非 86GB**，正確）；fail=126 全是 **15:57 G: 閃斷(WinError 3)** 那批，ledger resume 重跑後 `fail=0` 全補回
- **驗收**：`build_photo_index` chenwei **24,803 media**（物理檔 **26,030**；差額＝CR2/冷門影片格式不入 index 但實體都在）；R2 `--index-only` + `training` 縮圖 + `chenwei` 縮圖皆同步
- **classify / rename 此次「跳過」**：純檔名一致性(YYYY-MM-DD)，檔案已落正確月夾/事件夾、loose 散檔極少，網站靠 index+資料夾即可顯示；idempotent，待 Drive 掛載穩再補跑即可

### 🩹 本次新教訓（重要）
1. **fill 跑時絕對不要讀 `chenwei_fill_ledger.json`**：腳本每複製一檔就 `os.replace` 原子覆寫整個 ledger，外部一旦開檔讀取就和 rename 撞鎖 → `[WinError 5]` 假 FAIL（檔其實已複製，ledger 標 fail 而已，resume 會冪等重補）。監督只 tail `chenwei_fill.log` / `chenwei_pass.log`。
2. **classify / rename 會卡死 G: 句柄**：這兩步逐檔 `Image.open` 讀**冷檔 EXIF**；遇 G: 閃斷／重插 D: 擾動 Drive File Stream 後會抓到**過期句柄整個 wedge**（PID 一小時只 1 CPU-sec、log 停在「Scanning…」不動）。判斷法＝`Get-Process` 看該 step 的 PID CPU 是否累積；**深層 walk 本身沒問題**（`build_photo_index` 2~5s、實體點數 <120s 都正常），只有逐檔 EXIF 會卡。卡了就 kill 該 PID + wrapper（**只殺自己當下啟動的**）重啟。
3. **重啟即 resume**：fill 有 ledger，classify/rename 冪等 → 直接再跑同一支 `_chenwei_fill_pass.ps1`，fill 會跳過已 done、只補 fail。
4. **R2 sync 是增量**：thumb 已在 R2 就 `skip=`（不讀 G:、不上傳）；orphan 程序就算跨 session 被 harness 斷掉，OS process 多半還活著在跑（看 PID＋CPU delta 確認），但 output file 會凍結 → 改 `Start-Process … -RedirectStandardOutput C:\tmp\r2_*.log` 自管 log 才看得到進度（注意 node 對非 TTY 是**塊狀緩衝**，log 會延遲幾行）。
5. **chenwei 縮圖 R2 sync 跑了 3 輪才滿**：detached node 有時會在 session/turn 邊界被 harness 收掉（.err 空、無 crash stack ＝被 signal kill，非當機），停在 ~80%/~88%。因增量收斂，**重跑續補**即可（19,800→21,800→24,803 `Done in 4717s`）。
6. **err=36＝~18 個壞/誤命名 JPG**（2023.02 IMG_6786/6811/6812…＋2021-05-08(81)）：sharp 報 `unsupported image format`（多半 HEIC 內容存成 .JPG 或壞檔）。**檔案在 Drive 沒問題、只是無網站縮圖**，非致命，記錄即可。

---

## /photos 網站

### 路由

| URL | 頁面 | 用途 |
|---|---|---|
| `/photos` | [pages/photos/index.vue](../../../pages/photos/index.vue) | 3 個 library 卡片（library picker）|
| `/photos/chenwei` | [pages/photos/chenwei/index.vue](../../../pages/photos/chenwei/index.vue) | 辰瑋年份 grid |
| `/photos/chenwei/[year]` | [pages/photos/chenwei/[year]/index.vue](../../../pages/photos/chenwei/[year]/index.vue) | 月份 + Other 區 |
| `/photos/chenwei/[year]/[month]` | [pages/photos/chenwei/[year]/[month]/index.vue](../../../pages/photos/chenwei/[year]/[month]/index.vue) | 照片 grid + lightbox |
| `/photos/training`、`/photos/hongshi`（相簿根）| [pages/photos/[lib]/index.vue](../../../pages/photos/[lib]/index.vue) | 通用 folder browser 根層 |
| `/photos/training/<event>/...`（巢狀資料夾，任意深度）| [pages/photos/[lib]/[...path].vue](../../../pages/photos/[lib]/[...path].vue) | 同上，巢狀層 |

兩個 page 都是薄殼，只 render [components/PhotoFolderBrowser.vue](../../../components/PhotoFolderBrowser.vue)（資料夾 + 照片 + lightbox + 多選刪除全在此元件），各自 `definePageMeta({ middleware: 'auth' })`。元件靠 `useRoute().params.lib` / `.path` 同時服務根層與巢狀層。

`/photos/chenwei` 由靜態 `chenwei/` 子目錄取勝路由優先順序，所以即使 `[lib]/` 動態段也會匹配 `/photos/chenwei`，靜態仍會中標。

> ⚠️ **路由地雷（2026-06-02 修）**：原本用單一檔 `[lib]/[[...path]].vue`（optional catch-all）。**unplugin-vue-router 在動態 `[lib]/` 底下放 optional catch-all 不會產生任何路由** → `/photos/training`、`/photos/hongshi`、連巢狀 `/photos/training/2017` 全 404（curl 實測：`/photos`、`/photos/chenwei` 回 302，三相簿頁回 404）。資料層（index 有 4,923 訓練檔 / 50 夾）、API、library card 全正常，純粹 page route 沒生成。修法＝拆成 **`index.vue`（相簿根）+ `[...path].vue`（required catch-all，巢狀）** 兩檔共用元件，這是 Nuxt 可靠處理的 idiom。教訓：不要在動態段資料夾內單獨放 `[[...optional]]` catch-all。

### 測試

[test/photos/photos.spec.ts](../../../test/photos/photos.spec.ts)（vitest，22 cases）覆蓋 [server/utils/photos.ts](../../../server/utils/photos.ts) 的純邏輯：`classify` / `sourceForSegment` / `bucketDir`（含 path-traversal throw）/ `contentTypeFor` / `isLibrarySlug` / `resolveLibFolder` 守門 / `signFileUrl`+`verifyFileSig`（含竄改 reject）/ 五個 `*FromIndex` builder（用合成 index fixture 驗 chenwei year-month 與 training/hongshi folders 兩種 layout）。

- 跑：`npx vitest run test/photos/photos.spec.ts`（或 `npm run test:run` 全跑）
- **環境＝nuxt**（非 node）：photos.ts 用 auto-import `useRuntimeConfig`，node env 會丟 `[nuxt] instance unavailable`。用 `mockNuxtImport('useRuntimeConfig', …)` 注入 deterministic config，**且回傳值必須含 `app.baseURL`**，否則 nuxt env 的 router plugin 初始化會炸（覆蓋了全域 useRuntimeConfig）。
- 最後一個 describe 是 **真實 `scripts/photo_index.json` 整合測試**：檔在就驗三相簿 `totalFiles > 0` 且 `listLibraryFolderFromIndex(idx,'training','')` 非空（直接守「訓練頁有東西可顯示」這條 invariant，避免再次只壞 route 不壞 data）；檔不在（CI / 沒跑過 build_photo_index）自動 `it.skip`，不會紅。

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

- **影片 tile**：包成 [components/LazyVideoTile.vue](../../../components/LazyVideoTile.vue) — 初始渲染 🎬 placeholder div，IntersectionObserver（rootMargin 200px）偵測進 viewport 才 mount 真的 `<video preload="metadata" src="{url}#t=0.1" muted playsinline>` 抓首幀。一個月份 50+ 影片時，原本初載會發 50 個 metadata 請求 + 50 個首幀 stream，現在只發看得到的 ~10 個，scroll 時逐張上來。`.mp4` / `.mov` / `.webm` 多數瀏覽器吃；`.mkv` 看 codec
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
- ~~**training nested empty folders**（35 個尚未清）~~ ✅ 已清（2026-05-21）— `fitcasting/<workout>` × 32 + `一般相片/儀隊汗水/{健身,2012}` + `2021.08.21 孫凱駿/ipad相片` 共 35 個 nested empty subfolder 全 unlink。training rglob 後從 116 dirs 降到 81 dirs，topFolders 維持 50（被清的都是 sub-subfolder 不影響 top）。Log：[scripts/training_empty_dirs_cleanup_log.json](../../../scripts/training_empty_dirs_cleanup_log.json)

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

chenwei totalFiles：build_photo_index 報 **12,863**（深巢狀 sub-subfolder 不入 index 計數）／實際 Drive 上總媒體檔 **13,022**（多出 159 為 audit 2026-05-21 發現的三個事件夾深巢狀漏網檔，見「待辦 #5」）。`.AAE` sidecar 不入 IMAGE_EXTS 白名單，2026-05-21 unlink 626 個 不影響此 total。

歷次大整理動的檔次：
- 2026-05-16 初版大整理：5,370 個檔（5,063 散檔→月份 + 297 月份→截圖 + 10 散檔→下載 + 119 cross-year 修正）
- 2026-05-19 Sony HX99 dump：594 JPG + 36 MP4 從 `C:\Users\張辰瑋的資料\新增資料夾\` 匯入 + 774 個檔 rename（含舊照片被新照片擠開的編號對調）
- 2026-05-19 iPhone screenshot 漏網修補：440 個 PNG 從月份夾 → `{Y}截圖/`，1,906 個檔 rename（含 S 前綴 + 月份夾 gap 補正）
- 2026-05-21 lint cleanup：chenwei `.AAE` Apple Photos 編輯 sidecar 626 個全 unlink；training `desktop.ini` 1 個 + 5 個 2016 空事件夾 + 35 個 nested empty subfolder（fitcasting／儀隊汗水／ipad相片）移除 → training top-level 50，total dirs 從 116 降到 81
- 2026-05-21 chenwei straggler audit：發現 3 個事件夾共 159 漏網媒體檔未經 rename（2019 法國照片 64+62、2016 美女圖片 33）；rename 跟著 hongshi prewarm I/O 互卡，先記入「待辦 #5」等 prewarm 完成再跑
- 2026-05-21 影片 tile 改用 [LazyVideoTile](../../../components/LazyVideoTile.vue)：IntersectionObserver lazy-mount，影片密集月份頁初載 metadata storm 解決
