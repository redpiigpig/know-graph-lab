# know-graph-lab

Nuxt 3 網站 + Python／Node 資料管線。網站原始碼在 `pages/ server/ components/ stores/`，
管線腳本在 `scripts/`，各工作流的作法寫在 `.claude/skills/` 與 `skills/`。

## 檔案該放哪裡 — 動手前先看 `docs/repo-hygiene.md`

三條硬規則：

1. **成品不進 git。** PDF／DOCX／PPTX／MP4／單字卡／掃描檔一律放 Drive
   `G:\我的雲端硬碟\資料\知識圖工作室\` 的對應夾（對照表在 repo-hygiene.md 第二節）。
2. **根目錄不准新增檔案。** 只留工具鏈設定與 `README.md`／`CLAUDE.md`。
   文檔進 `docs/`，腳本進 `scripts/`，中繼進 `output/`（不進版控）。
3. **`output/` 預設不進版控。** 只有 `.gitignore` 白名單裡的策展 JSON／審閱筆記例外；
   要新增就補白名單那一條，不要整個目錄放行。

判不出來時問：「刪掉後重跑腳本能不能一模一樣長回來？」
能 → 快取（本機）。不能且是最終產物 → 成品（Drive）。不能且是下一步輸入 → 進 git。

## 其他既有規則

- 所有中文書寫一律繁體。
- 大檔存放策略（Drive canonical／R2 只放小衍生物）見 `docs/r2-policy.md`。
- 完成一項工作流後，同步更新對應的 `SKILL.md`。

## 姊妹專案：nonchurch-nuxt（無境界者雜誌＋龐會督典藏）

`C:\Users\user\Desktop\nonchurch-nuxt` 是另一個獨立 repo，兩邊互相引用：

- **本 repo 的論文用那邊的史料**。`/works` 的〈龐君華會督的衛斯理神學實踐與「新修道主義」願景〉
  （`public/content/works/pong-pastoral-spirituality-revision-draft.md`）一手材料全部出自
  **龐君華會督數位典藏**，資料在 nonchurch 的 Supabase，憑證在**那邊的 `.env`**
  （`VITE_SUPABASE_URL` ＋ `SUPABASE_SECRET_KEY`；本 repo 的 .env 連不到那個專案）。
- **表**：`pong_writings`(43 著作，有 `page_range`／`publication`／`supervisor`／`provider`)、
  `pong_sermons`(705 講道)、`pong_media`(236 講座影音，含 `transcript`)、`pong_reports`(21 相關報導)、
  `pong_remembrance`、`pong_daily_office`。`pong_manuscripts` 與 `pong_photos` **是空表**。
- **《無境界者》各期 PDF**在 `issues.pdf_link`（Cloudinary `Vol.N.pdf`）。引用篇目頁碼時
  下載該 PDF 讀目次與印刷頁碼，**不要用 Drive `雜誌\09-第九期\9-0目次.docx`**——那份目次是空的
  （頁碼在排版時才生成）。
- 🚨 **典藏尚未公開**（等著作權授權處理完），站上 `/pong-archive` 有登入牆；論文書目一律寫
  「龐君華會督數位典藏（尚未公開），文稿／影音編號 N」，**不可掛 URL**。
- 🚨 **年議會事工報告只有掃描、沒有文字層**：Drive `資料\無境界者\龐君華檔案\事工報告\`
  2008–2022 共 110 張照片（頁面有屆次書眉與真頁碼，如「第四十五屆年議會第一次會議，頁 172」），
  但 **DB 任何一表都查不到**（`年議會第`／`事工報告` 全庫零命中）。要引用得先自己 OCR。


## 🚨 `G:` 不見了＝Drive 卡住，不是掛掉

Drive 路徑報「找不到檔案」時，**第一件事是 `Test-Path 'G:\我的雲端硬碟'`**。
若是 False：一次短暫離線會讓 DriveFS 的 OAuth token 刷新逾時，它就主動卸載磁碟
（日誌 `Volume removed: G:\`），網路恢復後**不會自己重掛**，程序還活著、視窗停在
「正在載入帳戶…」。所以「Drive 程序在跑」不等於「磁碟在」。修法就一行：

```powershell
Get-Process GoogleDriveFS | Stop-Process -Force
Start-Process "C:\Program Files\Google\Drive File Stream\launch.bat" -WindowStyle Hidden
```

約 20 秒後就掛回來；未上傳的檔在本機快取，重啟後接著傳，不會掉。
別改用 Google Drive 連接器頂替——它只能逐檔讀寫小檔，撐不起管線的幾十 MB 進出。

## 🚨 一個 session 同時最多開 3 個 agent

不論任務多大，並行 agent 上限 3 個，要多就排隊接力。2026-09-23 一次開 20 個，
兩分鐘燒光五小時的額度，二十個一個都沒做完。
