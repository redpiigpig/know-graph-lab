---
name: photo-library
description: 「辰瑋相片」照片管理系統 — Drive 上 YYYY相片/YYYY.MM 整理結構 + /photos 網站瀏覽 + EXIF 啟發式自動分類腳本（classify_photos.py）。Use when 新增一批照片要分月份／截圖／下載歸位、要新增事件資料夾、要在 /photos 加新功能（icon、filter、event tile）、調整分類規則、修網站 photo viewer，或當使用者問「照片在哪／怎麼整理」。
---

# 辰瑋相片 — Drive 結構 + /photos 網站

> Drive 根：`G:/我的雲端硬碟/資料/儲存資料夾/辰瑋相片/`
> 網站：[pages/photos/index.vue](../../../pages/photos/index.vue)（需登入）
> 分類器：[scripts/classify_photos.py](../../../scripts/classify_photos.py)

---

## Drive 資料夾結構（單一年份）

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
| `{YEAR}相片/{YEAR}.MM/<file>`（2014-2022 月份內）| 只抽**高信心** screenshot/download，照片留在月份 |
| `{YEAR}相片/{YEAR}.MM/<file>`（2023+）| 不掃 |
| `{YEAR}相片/<事件夾>/<file>` | 永遠不動 |

> **`SCAN_MONTH_SUBDIR_YEARS = {2014..2022}`** — 如果之後 2023+ 也要清理，改這個 set 即可。

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

## /photos 網站

### 路由

| URL | 頁面 | 用途 |
|---|---|---|
| `/photos` | [pages/photos/index.vue](../../../pages/photos/index.vue) | 年份 grid（13 個年份卡）|
| `/photos/[year]` | [pages/photos/[year]/index.vue](../../../pages/photos/[year]/index.vue) | 12 月份 tile + Other 區（📸截圖／🌐下載／📁事件）|
| `/photos/[year]/[month]` | [pages/photos/[year]/[month]/index.vue](../../../pages/photos/[year]/[month]/index.vue) | 照片 grid + lightbox（month 也接受 `screenshots`／`downloads`／事件夾名）|

### 後端 API

| Endpoint | 回傳 |
|---|---|
| `GET /api/photos/years` | `{years: [{year, total, monthsWithPhotos}]}` |
| `GET /api/photos/[year]/months` | `{months, screenshots, downloads, events}` |
| `GET /api/photos/[year]/[month]/files` | `{files: [{name, kind, source, ext, size, mtime, url}]}` |
| `GET /api/photos/file?y=&m=&n=&exp=&sig=` | 串流照片本體（HMAC-SHA256 簽章，1 小時 TTL）|

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
2. 前端 [photos/[year]/[month]/index.vue](../../../pages/photos/[year]/[month]/index.vue) 的 `tileIcon` / `sourceTitle` 加 mapping
3. 年份頁 [photos/[year]/index.vue](../../../pages/photos/[year]/index.vue) Other 區加新卡

---

## 已知地雷

- **不要對 YYYY.MM 內部跑低信心 download 分類** — HEIC、IMG_xxxx.JPG 被剝 EXIF 的 iPhone 照很容易誤判為「下載」。`classify_photos.py` 已加 `confidence != "high"` filter 守門
- **Drive sync 慢** — 移動 5000+ 檔後雲端要幾分鐘到一小時才同步完。本機 G: 已對齊，但網站若部署在別處看到的可能還是舊雲端狀態
- **檔名編碼** — 終端 (Git Bash) 顯示中文檔名常變亂碼（cp950 vs utf-8），但檔案本身沒問題
- **Pillow 不開影片** — `.MOV/.MP4` 的 EXIF 抓不到，只靠檔名 `V_YYYYMMDD_HHMMSS` 推時間。iPhone 影片檔名沒日期 → 落入 low conf
- **HEIC 必為 iPhone** — 即使 Pillow 沒讀到 Make，HEIC 副檔名本身就是判斷依據（沒人會下載 HEIC）
- **多個 plan 在跑會 race** — 同時 `python classify_photos.py plan` 跑兩次會互相覆蓋 `photo_classification_report.json`。execute 前確認 plan 跑完且沒有殘留背景 process

---

## 統計（2026-05-16 大整理後）

| 年 | YYYY.MM | 截圖 | 下載 | 事件夾 |
|---|---:|---:|---:|---:|
| 2014 | 0 | 0 | 0 | 132 |
| 2015 | 24 | 0 | 1 | 76 |
| 2016 | 123 | 0 | 4 | 972 |
| 2017 | 36 | 0 | 4 | 479 |
| 2018 | 2,372 | 0 | 0 | 15 |
| 2019 | 2,483 | 0 | 1 | 147 |
| 2020 | 25 | 0 | 0 | 92 |
| 2021 | 453 | 3 | 0 | 78 |
| 2022 | 1,655 | 294 | 0 | 0 |
| 2023 | 2,313 | 0 | 0 | 0 |
| 2024 | 1,260 | 0 | 0 | 0 |
| 2025 | 0 | 0 | 0 | 0 |
| 2026 | 0 | 0 | 0 | 0 |

該次大整理共動 5,370 個檔（5,063 散檔→月份 + 297 月份→截圖 + 10 散檔→下載 + 119 cross-year 修正）。
