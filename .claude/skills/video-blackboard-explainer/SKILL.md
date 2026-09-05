---
name: video-blackboard-explainer
description: 把一份寫好的解說稿做成「無限黑板」風格的 YouTube 解說影片 —— 整塊超大黑板一次排好版，講到哪個重點該點才寫出來，鏡頭在板上平移縮放把不同事情串起來。含腳本切 cue、細流表（時間／台詞／影片配圖／音效／背景音樂）、官方預告片下載與分鏡截圖、CC 授權音樂音效與公有領域配圖、三種視覺風格、全自動出片（Playwright＋ffmpeg），以及要手調時可丟進 After Effects 的專案建置腳本。Use when 使用者要把某篇影評／解說稿做成影片、要重出某一段、要換風格、要補素材、要配音錄好後重新對時間，或提到「多馬茶房」「電影辯士」「無限黑板」「細流表」。首案＝《劇場版 吉伊卡哇──人魚島的秘密》解說。
---

# 無限黑板解說影片

一句話：**腳本 → cues.json → 黑板 → 影片**。所有東西都吃同一份 `cues.json`，
所以改腳本、改時間、改風格都不用重排版。

腳本在 `scripts/board_video/`，素材與成品在 Drive
`G:\我的雲端硬碟\創作\影片創作\<專案名>\`（成品不進 git，見 docs/repo-hygiene.md）。

## 一支影片的完整流程

1. **抽腳本**：docx → `腳本.txt`（一段一行，段落索引就是後面對應節點的鍵）。
2. **設計板面**：`spec_chiikawa.py` 這類 spec 檔，三件事——
   - `NODES`：每個節點的位置、標題、重點條目、類別（決定配色）
   - `EDGES`：哪兩個節點要用粉筆線串起來
   - `PARA_NODE`：**第幾段講到哪個節點**（最關鍵的一張表）
3. **切 cue**：`make_cues.py` 依句末標點切句、合併短句、估時長（預設 4.5 字/秒），
   產出 `cues.json` 與細流表 xlsx。
4. **收素材**：`fetch_cc_assets.py`（CC 音樂音效＋公有領域圖）、
   `extract_shots.py`（預告片分鏡截圖＋接觸表）、`make_memes.py`（名畫反應圖＋吉祥物梗圖卡）。
5. **挑配圖**：看接觸表，把編號填進 `suggest_shots.py`，重跑 `make_cues.py`。
6. **出片**：`node render.mjs --theme chalk`，逐格截圖直接 pipe 進 ffmpeg。
7. **（可選）進 AE**：`build_ae_jsx.py` → AE 執行指令碼，節點、連線、鏡頭關鍵影格全帶進去。

## 踩過的坑（會再犯的那種）

- **`cv2.imwrite` 遇中文路徑會靜默失敗**：偵測到鏡頭、印出張數，但一張都沒寫出來。
  改用 `cv2.imencode` + `Path.write_bytes`。這條對 Drive 上所有中文資料夾都適用。
- **節點沒被任何段落指到就等於不存在**：板面上設計了四個角色節點，`PARA_NODE`
  漏掉，整支片都不會出現。改完 spec 一定要驗
  `{c['node'] for c in cues} == {n['id'] for n in nodes}`。
- **鏡頭要對「量到的高度」不是「規格高度」**：spec 的 `h` 只是版面預留，
  節點實際內容通常矮很多，拿規格高度對焦會對著一大片空白。init 時量 `offsetHeight`。
- **`round(0.375) == 0`**：條目浮現數用四捨五入會讓節點第一次出現時「有框沒字」。用 `ceil` 並下限 1。
- **Openverse 匿名額度極低**：連續查會 401/429。音樂改走 ccMixter（要帶
  `Referer: https://ccmixter.org/` 否則檔案 403）與 archive.org netlabels；音效才用
  Openverse，每次查詢間隔 12 秒。
- **archive.org 會給整張專輯的單檔**：抓到 194MB 的 mp3。抓完要按大小過濾（>30MB 丟掉）。
- **yt-dlp 版本落後就是 403**：YouTube 一改動就掛，先 `pip install -U yt-dlp` 再說。

## 時間軸與配音的關係

第一版時間軸是估算的（`--cps`）。配音錄好後兩條路：整體語速微調
（`make_cues.py --cps 4.2`），或用 whisper 逐句時間戳改寫 `cues.json` 的 `t`／`dur`。
鏡頭運動、條目浮現、連線動畫全部由 `cues.json` 驅動，重跑 render 即可。

## 三種風格

`--theme chalk`（綠黑板粉筆，標楷體）／`paper`（米色手帳，卡片＋色邊）／
`neon`（深色知識圖譜，發光節點與連線）。全部在 `board.html` 的 `body.theme-*` 底下，
加新風格＝加一段 CSS。

## 授權規矩

- 官方預告片畫面＝評論用途引用，出處寫進 `授權標示.txt`。**不抓盜版片源。**
- CC BY 音樂音效必須在說明欄標作者與授權連結（`fetch_cc_assets.py` 會自動產這份文字）。
- 網路流行梗圖多半版權不明，不自動抓；改用公有領域名畫與自家吉祥物梗圖卡。

## 現況

- 首案《人魚島的秘密》：170 條 cue／估 20 分 49 秒／32 個節點／板面 15200×9400。
- 素材：預告片 13 支 421 張分鏡、魔法公主 4 支 198 張、公有領域圖 18 張、
  梗圖 15 張、CC 音樂 21 首。
- 相關：[[reels-piigpig]]（同一位使用者的短影片線，走 ffmpeg 本機合成）。
