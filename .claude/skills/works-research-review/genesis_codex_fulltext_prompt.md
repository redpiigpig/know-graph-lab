# Codex 交辦 prompt — 創生哲學參考資料庫「OA 全文逐段中譯」

> 把下面 `---` 之間整段貼給 Codex 即可。書目層（663 筆）已全部完成上架；這支只做加值：把**開放取用（OA）**文獻抓全文、逐段翻成繁中，供 reader 原文／中譯兩欄對照。

---

你在 repo `c:\Users\user\Desktop\know-graph-lab`（Windows）。請執行「創生哲學叢書參考資料庫」的 OA 全文抓取＋逐段繁中翻譯，這是一個可中斷、可續跑的長時間批次工作。

## 要跑的指令

```bash
python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project genesis-philosophy --resume --engine haiku --pace 1
```

- 共 **538 筆**待處理（橫跨 15 卷 O/V/B/M/E）。
- log 寫到 `c:/tmp/lit_review_genesis_fulltext.log`（請 `tee` 或 `>>` 同時落檔，方便追進度）。建議背景跑：
  ```bash
  python -X utf8 scripts/ingest_lit_review.py --fetch-fulltext --project genesis-philosophy --resume --engine haiku --pace 1 >> c:/tmp/lit_review_genesis_fulltext.log 2>&1
  ```

## 引擎選擇（重要）

`--engine` 四選一：`gemini`（內含 gemini→nvidia 自動 fallback）／`nvidia`／`sonnet`／`haiku`。

- **優先用 `--engine haiku`**：它走付費 Max OAuth 的**獨立額度池**，跟免費 Gemini/NVIDIA key 不同池。先前用 gemini/nvidia/sonnet 過夜跑時，三者全部撞 429（帳號層級限流），只有 haiku 的 Max 池能繞過。
- 若 haiku 也不順，改 `--engine sonnet --resume`，或等限流退去後回到 `--engine gemini --resume`。
- 切換引擎不會弄亂進度（見下「續跑」），可以隨時換。

## 續跑 / 自動中止行為（這是設計好的，不是 bug）

- **resume 安全**：已翻好的段落記在 `done_zh_indices`，加 `--resume` 會**從缺口接續、不重做**。同一指令重跑即可。
- **連續 4 次失敗會自動中止**（`CONSEC_FAIL_ABORT=4`，通常是 quota/網路），會印「aborting: … re-run with --resume later」並結束。**這是正常的**——等一下（讓限流退去）再跑**完全相同的指令**就會從斷點接續。可能要重跑好幾輪才能磨完全部。

## 哪些會被「跳過」（正常，不是錯誤，不用修）

只有 OA 來源抓得到全文：SEP / IEP / arXiv（`/pdf/`）/ PMC / 其他 OA PDF。以下會自動跳過、維持「書目層」：

- 付費牆：Nature / Science / Wiley / Annual Reviews 等 → 常見 `403`/抓不到正文。
- 擋 bot：MDPI（`403 Forbidden`）。
- 版權書、出版社書目頁。
- `language=zh` 的中文文獻（本來就只做書目層、不抓全文）。

所以 log 裡看到一堆 `✗ FAIL: 403 …` 或 `skip` 是**預期內**的，繼續跑即可，不要去「修」這些連結。

## 怎麼算完成 / 怎麼回報

- 工作目標：把所有**可抓的 OA 文獻**都翻完（剩下的本來就只能停在書目層）。
- 進度可看 log 裡 `→ <ref_key>` 與 `· para N/總數` 行；每篇翻完會落 DB（即時 persist，中途中止已翻段不丟）。
- 跑到指令自然結束（不再有新的 `→` 條目、或印出已全部處理）即完成。請回報：總共處理幾筆、實際翻成全文幾筆、仍維持書目層幾筆、有沒有反覆中止的引擎。

## 注意

- **只管這支自己啟動的 python**。機器上可能有別人的背景程序（例如 `_whisper_venv` 的其他 python 任務），**絕對不要 kill 不是你這次啟動的程序**。
- 這支腳本是冪等的：on_conflict 在 `(project_slug, book_id, ref_key)`＋段落層 resume，重跑不會產生重複資料。
- 不需要動任何 `.md` 報告檔或重新 ingest 書目——書目早就入庫完成，這支只填全文／中譯欄。

---
