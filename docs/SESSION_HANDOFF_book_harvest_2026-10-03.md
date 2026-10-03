# 交接：書籍大量補抓（LibGen／Anna's Archive／華藝）與入庫修復——2026-10-01～03

新 session 接手前先讀這份。起點是《基督宗教譜系學》重寫的備料（`works-christian-genealogy` skill「重寫討論」一節），
後來擴成「z-lib 排隊清單改走 LibGen 直接抓」與「當代三十位神學家全集」。

## 一、還在背景跑的（2026-10-03 09:30 時）

| 工作 | 狀態 | 紀錄檔 |
|---|---|---|
| LibGen 第四輪：整份 z-lib 排隊清單分 4 片 | 各 63–77%，剩約一千筆查詢，約 6 小時 | `c:/tmp/libgen_queue4_{0..3}.log` |
| 接力腳本（跑完自動 djvu 轉檔＋入庫） | 等上面 4 片 | `c:/tmp/overnight_libgen4.log`，看到 `OVERNIGHT DONE` 才算完 |

- 腳本 `c:/tmp/overnight_libgen4.sh`（nohup 背景，不受工具兩小時時限）。**中途停掉不會壞**：已下載的都記在
  `scripts/state/zlib_ledger.jsonl`（`pick.via = "libgen"`），重跑會跳過。重跑：
  `python -X utf8 scripts/zlib_wanted.py` 後 `python -u -X utf8 scripts/libgen_wanted.py --queue --shard k/4 --apply`（k=0..3 各開一支）。
- 跑完後檢查：`z-lib/` 收件夾清空、`_corrupt/` 剩幾本；再跑一次
  `python scripts/reclassify_review_queue.py --apply --no-gemini`（Gemini 額度用完時用 NVIDIA 分類）。

## 二、累計成果

- **LibGen 帳本 2,146 本**（10-03 09:24）。來源分布：genealogy-comparative 448、biblio 361、cw30 314、
  ht 228、biblical 163……。
- **華藝 1,492 篇**（10-02 在校，全為《新使者》）。下次到校照跑 `run_airiti_batch.ps1 -Batch 1500 -DailyCap 1500`：
  《新使者》剩 521、《神學與教會》188（那 8 篇失敗是離校斷網）、《台灣神學論刊》473。
- **Anna's Archive** 7 本抓到 6 本（Selb、Rahner／Ratzinger 兩本英譯、Goertz、Geiselmann、邢福增《基督教在中國的失敗？》）。
  **Karmiris《東正教會的教義與信經文獻》未取得**（伺服器上的檔只回空檔；使用者決定先放著）。
- **入庫**：10-02 三輪共入約 1,100 本；**重分類** 待審分類 877 本已分完（剩各輪 1 本判不出）。
- 66 本「z-lib 抓不到」的去處總表：`output/christian-genealogy/missing66_where.md`；
  期刊論文 277 篇的臺大館內可下載清單：`output/christian-genealogy/articles_ntu_checklist.md`（可下載 150）。

## 三、這兩天修掉的「看起來成功的失敗」（細節在各 skill）

1. **LibGen 殘檔**：伺服器常在 7／9／11 MB 處切斷，只驗檔頭就存成殘檔。566 本裡 54 本被隔離、17 本騙過驗證入庫上 Drive。
   修法：核對 Content-Length＋PDF 要開得起來；**Range 續傳**（伺服器回 206）；`--retry-corrupt` 重抓 `_corrupt/`。
   Drive 上那 17 本修好 13，**剩 4 本**（LibGen 一直給不出完整檔）還是殘檔，清單在 `$TEMP/ntu/drive_noeof.json` 的產生邏輯：
   掃 `_待審分類`／各類別夾今天入庫的 PDF，結尾 4KB 無 `%%EOF` 者。
2. **get.php 的 key 只能用一次**：重試沿用舊連結只拿回網頁。每次重試重取。
3. **ingest 被一本壞 PDF 整批中斷**（讀 page_count 才丟 RuntimeError）：`file_validation.py` 已接住。
4. **ingest 分類用的 gemini-2.5-flash 已下架**：改 `gemini-flash-latest`。🚨 但 Gemini 免費額度跟翻譯艦隊共用，常滿；
   滿了就退回本地分類器 → 大量進 `_待審分類`，要靠 `reclassify_review_queue.py --no-gemini`（NVIDIA）補分。
5. **重複入庫**：分到待審時只看待審夾，看不到同一本早在宗教學夾 → 已改成先查所有類別夾。10-02 刪了 13 本重複。
6. **Anna's Archive 視窗被關**：DDOS-GUARD 要人點驗證；停 node 就連視窗一起關（使用者被迫重點四次，很火）。
   現在 `annas_download.mjs` 是常駐＋佇列檔，下載另開分頁（工作分頁會被 Chrome 當下載收掉）。見 memory
   `feedback_dont_close_verified_browser`。同 IP 同時太多下載會被擋，用 `--tabs 1`。

## 四、待辦與待決

- **Anna's Archive 要不要註冊會員**（使用者決定等 LibGen 全跑完再看剩多少 LibGen 沒有的書，主要是中文書）。
- **當代三十位神學家全集**（`ebook-collected-works` skill 末節）：書目三份 JSON、獵表四層已建；
  譯名已定（郎尼根／默茨／雲格爾／梅延多夫已入詞庫；八位作家頁已改詞庫名）。
  **待做**：新建六位 hub（德呂巴克、拉青格、席勒貝克斯、默茨、雲格爾、托倫斯）；書到館後擴充各 hub works
  （現在每人 3–6 部且全標 copyright，依 `feedback_personal_research_ignore_copyright` 已過時）。
- **《基督宗教譜系學》**：書大致到齊後，照定好的順序先擬各章節次條目、再一起動筆（skill「重寫討論」）。
  輔大神圖紙本待借：Fouilloux、Poulat、Chauvet、Rahner／Ratzinger 德文兩本、Joannou、de Lubac 法文版。
- Drive 上 4 本殘檔、`_corrupt/` 剩 9 本：LibGen 給不出完整檔，留在 z-lib 排隊清單由 z-lib 排程補。

## 五、相關腳本

`scripts/libgen_wanted.py`（`--sources`／`--queue --shard k/n`／`--reverse`／`--retry-corrupt`／`--convert-djvu`）、
`scripts/annas_search.mjs`、`scripts/annas_download.mjs`、`scripts/reclassify_review_queue.py`、
`scripts/ingest_new_books.py`、`scripts/file_validation.py`、`scripts/run_airiti_batch.ps1`。
skill：`ebook-zlib-harvest`（LibGen／Anna's 兩節）、`ebook-collected-works`（當代三十位）、`works-christian-genealogy`。
