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
