# repo 整潔規則（2026-08-27 重訂）

## 一句話

**這個 repo 只放「網站跑得起來所需的原始碼，以及不可重生的策展資料」。**
成品放 Drive，快取留本機，兩者都不進 git。

---

## 一、三分法

每個檔案在動手前先歸一類，三類的去處互斥：

| 類別 | 判準 | 去處 | 進 git？ |
|---|---|---|---|
| **原始碼 / 策展資料** | 網站要用；或人工校訂過、刪掉就重建不回來 | repo | ✅ |
| **成品** | 給人看、給人下載、拿去印的最終檔（PDF／DOCX／PPTX／MP4／XLSX） | Drive `資料/知識圖工作室/` | ❌ |
| **快取 / 中繼 / 一次性** | 腳本重跑就會再生；或這次任務結束就沒用了 | 本機工作區 | ❌ |

判不出來時問一句：**「刪掉之後，重跑腳本能不能一模一樣長回來？」**
能 → 快取。不能、且是最終產物 → 成品。不能、且是下一步的輸入 → 策展資料。

---

## 二、成品去 Drive 哪一夾

Drive 根 `G:\我的雲端硬碟\資料\知識圖工作室\`

| 成品 | Drive 位置 |
|---|---|
| 原文讀本 PDF／DOCX、單字卡、印刷母版 | `語言/原文讀本/{讀本,單字卡,印刷母版}` |
| 短影片（reels） | `影片/YYYY-MM-DD_主題/` |
| z-library／TRC 下載、採購獵表 | `電子圖書館/_待入庫/z-lib-YYYY-MM-DD/`，歸類後移入 `電子圖書館/{學科}/` |
| 電子書原檔 | `電子圖書館/{學科}/`（Drive 是 canonical，見 `r2-policy.md`） |
| 全集卷冊 | `全集/{學科}/{作者}/` |
| 學位論文、研究計畫 | `學位論文/{博士,碩士,學士}論文/` |
| 會議論文集、排版樣稿 | `會議論文集/{屆次}/` |
| 研討會簡報 | `學術著作/會議論文/簡報/` |
| 演講錄音、投影片 | `演講/{日期 場次}/` |
| 照片 | `照片/{相簿}/` |
| 研究資料全文 | `研究資料/{專案}/` |

沒有對應夾就新增一層，**不要塞進最像的那一夾**，也不要放 repo 裡等之後再說。

---

## 三、根目錄禁令

專案根目錄**只准**放這些，其餘一律不得新增：

```
README.md  CLAUDE.md  app.vue  nuxt.config.ts  tailwind.config.ts  vitest.config.ts
package.json  package-lock.json  pnpm-lock.yaml  pnpm-workspace.yaml
pytest.ini  .gitignore  .nuxtrc  .env
```

想放在根目錄的東西，實際該去的地方：

| 你想放 | 放這裡 |
|---|---|
| 專案文檔、交接筆記、政策 | `docs/` |
| 任何 `.py` `.mjs` `.bat` `.cmd` 腳本與啟動器 | `scripts/` |
| 抓取／轉換的中繼 JSON | `output/`（不進版控） |
| 網站要讀的資料表 | `data/` |
| 網站要送出的靜態檔 | `public/` |
| 書、影片、簡報、掃描檔 | Drive（見上表） |
| 這次任務用完就丟的 | 本機暫存目錄，用完刪 |

`docs/` 底下同樣只收 `.md` 與建構用的小素材；**成品 docx／pdf 不留在 docs/**。

---

## 四、`output/` 的白名單制

`output/` 預設整個不進版控（`.gitignore` 的 `/output/**`）。
唯一例外，逐條列在 `.gitignore` 白名單裡：

- `output/source-cache/**/*.json`、`*.md` —— 各語料夾**頂層**的策展檔：
  詞表計畫（`scripture-plan.json`）、中譯 gloss（`*-gloss-zh-reviewed.json`）、
  配圖對照（`*-card-images.json`）、審閱筆記（`memory-selection-review.md`）、
  驗證報告（`validation-report*.json`）。這些人工校訂過，要能 review 與回溯。
- `output/original-readers/audio/**/manifest.json` —— 音檔清單與 checksum。

**不放行**的是同一棵樹底下抓回來的第三方語料：
`sources/`、`morphhb-src/`、`iconify/`、`openmoji-*/`、`collins-pages/`、
`latVUC*`、`UD_Latin-*`、`whitakers*`、各種 `*-lexicon.json`。腳本會重抓。

新增策展檔要進版控時，**在白名單補一條**，不要把整個目錄放行。

---

## 五、版權素材

- 第三方受版權的書稿、掃描、訪談原文：**永遠不進 git**。正本 Drive，全文入 DB。
- 已有逐條 ignore 的（Panikkar／Jung 快取、訪談書 OCR、festschrift 掃描）維持原樣。
- 新的一批版權素材，比照 `.gitignore` 既有段落補一條並註明理由。

---

## 六、每次收尾的三個檢查

1. `git status --porcelain` 沒有非預期的 `??`。
2. 根目錄 `ls` 跟第三節的白名單一致。
3. 這輪產出的成品，Drive 對應夾裡找得到。

季度另跑 `scripts/r2_reclaim.py` 體檢 R2（規則見 `r2-policy.md`）。

---

## 七、大檔的處理慣例（2026-08-27 三項已清）

`public/` 放的是網站直接送出的資產，但**體積要壓在合理範圍**：單一下載檔 ≲ 5 MB
（`docs/r2-policy.md` 的門檻），插圖用 JPEG 不用 PNG。已處理的三例可以照抄：

- **簡報 `c12-presentation.pptx` 10.77 → 4.79 MB**：內嵌圖片全是原始解析度照片
  （最大 3414×2466）。做法是解開 zip、把圖縮到寬 1920、JPEG q78 重存；那張 2.4 MB
  的封面 PNG 無透明，轉成 JPEG 並同步改 `slide1.xml.rels` 的 Target 與檔名。
  改完要驗兩件事：每個 `.rels` 的內部 Target 都存在，以及 python-pptx 讀出的
  投影片數／圖片數／文字量與原檔一致。原檔留 Drive `寫作計畫/論文寫作/`。
- **AI 生成插圖 15 → 1.8 MB**：1536×1024 的 PNG 一張 3 MB，轉 JPEG q86 只剩 0.4 MB。
  AI 圖不可完全重現，原始 PNG 一律先備份到 Drive 再轉。
- **`test/` 與 `tests/` 併成一個**：測試一律放 `test/`，副檔名一律 `.spec.ts`。

`public/maps/*.geojson`（80 MB）網站直接讀，暫時留著；若再長大就改走 API + R2。
