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
