---
name: research-data-holdings
description: 🚨 任何研究、找文獻、下載資料、列缺件清單之前必走的第一步 —— 先查「已經有什麼」：讀 docs/holdings.md（自動產生的 Drive／R2／站上電子圖書館／repo 索引總盤點）與各主題的「既有資料盤點.md」，用 `scripts/holdings_inventory.py --find 關鍵字` 查特定書刊是否已在手上；收完資料後重跑盤點並更新主題 md。含資料夾歸類規則與「看起來有、其實沒有」的陷阱清單。Use when 要下載或整理任何研究材料、派 agent 收集資料、列「需要掃描／去圖書館」的書單、判斷某份刊物或全集有沒有、或使用者問「站上／Drive 上有沒有某某」。外部來源與管線另見 docs/data-sources.md。
---

# 研究資料：先查已有，再收集

**為什麼要有這個 skill**：每個新 session 都不知道站上和 Drive 已經收了什麼，於是重複下載、把早就有的書列成「要去圖書館掃描」、或另開一個新資料夾放同主題的東西。2026-09-24 一天內就發生：以為《太虛大師全書》沒有（其實全集夾有 20 編）、準備重抓集成（其實要確認）、把道安與太虛各開新夾。

---

## §1 動手前三步（每次都做，派 agent 也要寫進 prompt）

1. **讀總盤點** `docs/holdings.md`：看 Drive 各夾、站上電子圖書館類別、R2 前綴、repo 索引的規模與最近更新日。產生時間超過一週就先重跑：
   ```
   python -X utf8 scripts/holdings_inventory.py
   ```
2. **查關鍵字**（書名、刊名、人名都查，多查幾種寫法：繁簡、全名／簡稱）：
   ```
   python -X utf8 scripts/holdings_inventory.py --find 海潮音 太虛 道安
   ```
   它會同時搜 Drive 檔名、站上電子圖書館書名、repo 研究資料索引（篇目）。
3. **讀主題盤點 md**：總盤點第一節列出所有「既有資料盤點.md／*盤點*.md」。那裡記的是**內容層**的真相（有無頁碼、有無文字層、缺哪幾冊），總盤點只記「檔案存在」。

查完才決定要不要下載；要下載的只抓「確認沒有」的部分，並先把計畫寫進主題盤點 md。

## §2 收完之後兩步

1. 更新該主題的 `既有資料盤點.md`：新增了什麼、放哪、規模、有無頁碼／文字層、仍缺什麼。
2. 重跑 `python -X utf8 scripts/holdings_inventory.py`，並 commit `docs/holdings.md`（只加這一個檔）。新接了一個外部來源或管線，另外補 `docs/data-sources.md`。

---

## §3 東西放哪（依主題累積，不要一篇論文開一個夾）

| 範疇 | 位置 |
|---|---|
| 民國到戒嚴時期的佛教史料與研究（太虛、道安、民國佛教期刊、集成影印…） | `G:\…\知識圖工作室\研究資料\民國與台灣佛教史\<子題>\` |
| 解嚴後的印順學派、弘誓、人間佛教論爭、日本學者論印順 | `研究資料\印順學派與弘誓\<子題>\` |
| 某人的全集（印順、太虛、星雲、聖嚴、昭慧、各長老） | `全集\佛學\<法師名>\` |
| 單本電子書 | `電子圖書館\<類別>\`（走 ebook 管線，會進站上 ebooks 表） |
| 《民國佛教期刊文獻集成》整冊 PDF | `研究資料\民國與台灣佛教史\民國佛教期刊文獻集成\正編｜補編\`（共用，各子題只放切出來的單篇） |
| 使用者自己的論文草稿、書單、投稿文件 | `G:\我的雲端硬碟\玄奘\博一上\投稿\YYYY.MM.DD 名稱\` |

其他規則見 `docs/repo-hygiene.md`（成品不進 git、根目錄不放檔、output/ 不進版控）。

---

## §4 「看起來有，其實沒有」陷阱清單（每條都真的踩過）

| 看起來 | 實際 | 怎麼驗 |
|---|---|---|
| DLBS 索引標「有全文」（《海潮音》1,141 篇） | 只是臺大那邊有連結，我們沒抓下來 | 看 R2／Drive 有沒有實體檔 |
| repo `research-data/press/*.json` 有幾萬筆《海潮音》 | 那是**篇目**，不是全文 | 看總盤點第五節說明 |
| `全集\佛學\太虛大師\*.docx` 滿篇〔頁 N〕 | **假頁碼**（taixu_build 用流水號）；引用要回 CBETA TX XML 的 `<pb ed="TX">` | 抽一篇對 CBETA 頁碼 |
| 印順全集 `_chunks/*.jsonl` 的 page_number | 流水號，不是 Y 冊頁碼；引用用 CBETA Y XML 的 `<lb ed="Y">` | 同上 |
| 電子圖書館有《民國佛教期刊文獻集成》 | 只有第 1 冊 | `--find 民國佛教期刊` |
| 網站線上閱讀器有目錄就等於有全文 | 目錄可能指向 404 的分檔（道安著作集 44 個假連結） | 下載後比對檔數與頁碼連續性 |
| 子代理回報「本機沒有」 | 常常只查了它想到的幾個夾 | 自己跑 `--find`，見 memory「列缺件前先查站上各處」 |

---

## §5 派資料收集 agent 的 prompt 必備段落

> 動手前先讀 `docs/holdings.md` 與相關主題的 `既有資料盤點.md`，並跑 `python -X utf8 scripts/holdings_inventory.py --find <關鍵字>`。只下載確認沒有的部分；下載前檢查目標檔是否已存在（大小一致才算有），寫入先寫 `.part` 再改名。完成後更新主題盤點 md，並回報新增了什麼、放哪、仍缺什麼。不要另開新的主題資料夾，照 research-data-holdings §3 放。

## §6 定期更新

Windows 排程 `KGL_Holdings_Inventory` 每週一 03:30 重跑盤點並只 commit `docs/holdings.md`（`scripts/holdings_inventory_weekly.ps1`）。筆電休眠錯過就下次開機補跑（排程設 StartWhenAvailable）。

---

## §7 現況（2026-09-24 夜）

- 新主題夾 `研究資料\民國與台灣佛教史\`：`太虛研究\`、`民國佛教期刊文獻集成\`（海潮音 58 冊＋正編 80、補編 53、74；純影像）、`海潮音\DLBS全文\`（2007–2025，1,140 檔）、`道安法師遺集\`。
- `全集\佛學\` 新增 12 位台灣長老（盤點：`全集\佛學\台灣長老全集盤點.md`）。
- 碩博論文（太虛／民國佛教）下載進行中 → `太虛研究\碩博論文\`；NDLTD 帳密在 `.env`（`NDLTD_USER`／`NDLTD_PASS`，勿印）。
- 未竟事項清單見 `docs/SESSION_HANDOFF_taixu_papers_2026-09-24.md` 第三節。

---

## §8 《民國佛教期刊文獻集成》全集 OCR（2026-09-25 起，長期管線）

**目標**：正編 204 冊＋補編 83 冊（Commons 只有正編 204＋補編 28＋補編目錄／作者索引，
其餘 55 冊補編要去玄奘藏經閣影印）全部 OCR 成可檢索的逐頁文字；**太虛相關篇目優先**
（9/30 慧炬論文「世界佛學苑」要用）。三支腳本，一個排程，狀態記到頁，休眠／闔蓋／被砍都能接著跑：

| 步驟 | 腳本 | 產出（Drive 集成夾 `研究資料\民國與台灣佛教史\民國佛教期刊文獻集成\`） |
|---|---|---|
| 篇目 | `scripts/minguo_jikan_dila_catalog.py`（`quick`＝太虛關鍵字／作者查詢幾分鐘；`crawl`＝整庫 4,650 頁約 90 分；`build`） | `_篇目_全集.tsv`（DILA 正編 96,109＋補編 43,410 筆）、`_篇目_太虛相關_全集.tsv`（**7,516 筆、涉及 220 冊、13,626 集成頁**；欄位 叢刊、冊、集成頁、篇名、作者、原刊、原刊卷／期／頁、命中關鍵字） |
| 下載 | `scripts/haichaoyin_commons_fetch.py --series all --priority-tsv <太虛清單>`（`--vols 正80 補53`、`--max-files N`） | `正編\`、`補編\` 整冊 PDF（Commons 原檔名；`.hcy.part` 續傳、SHA1 驗）；紀錄 `正編\_下載紀錄_海潮音.json`、`補編\_下載紀錄.json` |
| OCR | `scripts/minguo_jikan_ocr.py run [--max-minutes 25] [--engine auto|cpu] [--only 正編187] [--dry-run]`；`status`／`cut`／`audit --vol`／`import-legacy` | `_OCR\<叢刊><冊>.jsonl`（一行一個 PDF 頁：pdf_index、集成頁、原刊頁＋依據、text、footnotes、headers、page_numbers、engine）；`_OCR\單篇\<叢刊><冊>\<冊>_<起-訖>_<篇名>.txt`（頁標頭 `【集成 正編187 頁 142｜原刊 頁 4】`，與 09-24 那 18 件同式）；`_OCR\_稽核\<冊>\p<集成頁>.png` |

- **排程** `KGL_Minguo_Jikan_OCR`：每 30 分鐘一班跑 `scripts/minguo_jikan_ocr.ps1`（UTF-8 BOM），
  `ExecutionTimeLimit PT2H`、`IgnoreNew`、StartWhenAvailable；一班＝補下載最多 2 冊＋OCR 25 分鐘。
  log `output/minguo_jikan/ocr_<日期>.log`，每班開頭與結尾都印分母（冊／頁／優先篇／已切件數）。
  狀態 `scripts/state/minguo_jikan_ocr.json`；跑班鎖 `scripts/state/minguo_jikan_ocr.lock`（PID 死了自動接收）。
- **優先序**：第 0 級 世界佛學苑／世苑 → 1 級 漢藏教理院／武昌／閩南／柏林／巴利三藏院／錫蘭留學 →
  2 級 法舫／法尊 → 3 級 篇名含太虛／作者太虛 → 之後整冊（太虛命中多的冊先）。同一頁只 OCR 一次。
- **引擎與 GPU 鎖的真相**：電子圖書館的 `mineru_ocr.py queue` 是**整個佇列期間握著 GPU 鎖**
  （acquire 在 `main()`、release 在 `finally`，每本之間不放），fleet keeper 又會重拉到佇列空
  （09-25 看：253 本做了 59 本，約 4 本／時，還要兩天）。所以本管線 `--engine auto` 每班先試一段 GPU，
  回 4 就整班改 `--device cpu`（不佔鎖）。**CPU 實測 8–15 秒／頁**（09-24 的 37 秒是含起跑的 3 頁小段；
  10–20 頁的段攤下來只要 8–10 秒），一班 25 分鐘約 120–150 頁；GPU 約 2–3 秒／頁。不搶鎖、不殺別人、不改電源。
- **頁碼規矩**：集成頁＝PDF 頁序（0 起）− offset；offset 每冊一個，09-24 核過的 22 冊寫死在 `SEED_OFFSETS`，
  其他冊先假設 2、段前後各多留 2 頁，再從 MinerU 撿到的頁底「-N-」學（眾數、≥3 頁、六成同意、落在 0–8）。
  原刊頁只由篇目推算（多篇打架就留空），MinerU 撿到的頁碼原文全存 `page_numbers` 給人核；**推不出就是空，不准編**。
  `mineru_ocr.py` 09-25 起 `to_chunks` 多帶 `headers`／`page_numbers` 兩鍵（下游其他路徑不受影響）。
- **失敗處理**：離開碼 3（環境）整場停；連錯 3 段整場停；離開碼 2（重複幻覺）段對半切再試；同一段錯 3 次先不排
  （`--retry-failed` 清掉）；每冊做完自動稽核（空白率、重複幻覺、迴圈頁重做一次、抽 3 頁存 png＋log 印文字開頭）。
- **09-24 那 18 件**已用 `import-legacy` 登記成完成並併進 JSONL（切單篇時跳過同範圍不重做）。
- 🚨 兩個下載程序（手動整批＋排程班）會 append 同一個 `.hcy.part`；腳本已把 2 分鐘內有更新的 `.hcy.part`
  當「別人在下」延後，班 ps1 也先查有沒有另一個 fetcher 在跑。
- 🚨 DILA `spValue` 關鍵字查詢**要一併送三個 checkbox**（`myLessAreaTitle/JournalName/Author=on`），不送回的是空表單；
  0 筆時頁面寫「回傳結果 : 0筆」不是 `<span>N筆</span>`。
- 已知 OCR 系統性錯字：敎→軟／敘；圈點多半掉；「（講）」一類夾註標記會殘缺。**摘句一律回影像核**（`_稽核\` 或自己用 fitz 畫）。
