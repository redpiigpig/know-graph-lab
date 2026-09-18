# 交接：本機 OCR 兩條線（通用佇列 ＋《內村鑑三全集》）

寫於 2026-09-18 08:20。接手的人先讀完再動手。這份取代
`SESSION_HANDOFF_uchimura_zenshu_2026-09-18.md`（那份只涵蓋內村那一半，仍可參考坑的部分）。

## 一句話任務

兩條線**共用同一顆 GPU、同一把鎖**，只能輪流跑：
先把《內村鑑三全集》20 卷轉完並重建《聖書之研究》書目，再回頭把通用 OCR 佇列
剩下的 107 本跑完。

---

## ✅ 第一件事已經做完（2026-09-18 11:47）

通用佇列已停，內村班已推（PID 26320），卷 01 轉錄中、量到 `+44.9s CPU / 35s` 確認在算。

停佇列那步**需要人按**——自動模式的權限層會把 `Stop-Process` 擋成
`Interfere With Workloads`。下次要停，用這段（會自己重算行程樹，子 PID 換了也對）：

```powershell
$ids=@(); Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*mineru_ocr.py queue*' } | ForEach-Object {
    $ids+=$_.ProcessId; $k=Get-CimInstance Win32_Process -Filter "ParentProcessId=$($_.ProcessId)"
    while($k){$n=@();foreach($c in $k){$ids+=$c.ProcessId;$n+=Get-CimInstance Win32_Process -Filter "ParentProcessId=$($c.ProcessId)"};$k=$n} }
Stop-Process -Id $ids -Force
```

**只停父程序不夠**：mineru 子孫會變孤兒繼續佔 GPU，所以要整棵樹。

停掉之後**不必手動清鎖**：`acquire_lock()` 看到持有者 PID 已死會自己接收。
停掉**不會掉進度**：佇列狀態存在 DB 的 `parse_error`，沒做完的書原樣留著。

推內村那班的指令（**要卸離主控台**，理由見坑 3）：

```powershell
Start-Process -FilePath 'C:\Users\user\AppData\Local\Python\bin\python.exe' `
  -ArgumentList '-u','scripts/uchimura_zenshu_ocr.py','--max-minutes','240' `
  -WorkingDirectory 'C:\Users\user\Desktop\know-graph-lab' `
  -RedirectStandardOutput 'scripts\logs\uchimura_ocr.out.log' `
  -RedirectStandardError  'scripts\logs\uchimura_ocr.err.log' `
  -WindowStyle Hidden
```

---

## A 線：《內村鑑三全集》20 卷 →《聖書之研究》書目

### 現況（2026-09-18 08:20 實測）

| 項目 | 狀態 |
|---|---|
| PDF | ✅ 20/20，18,074 頁 / 0.88 GB，平均 45 MB |
| Drive | `G:\我的雲端硬碟\資料\知識圖工作室\全集\神學\內村鑑三\岩波全集（1932-33）\` |
| ebooks | ✅ 20 筆，`collection=collected-works`，id＝`d0000001-0000-4000-8000-0000000000NN` |
| OCR | ✅ **20/20 完成**（17,498 段／1,240 萬字），`parsed_at` 20/20、`parse_error` 全清 |
| 排程 | ✅ **已 DISABLE**（20 卷全完成，2026-09-18 收工）|
| 昨晚那班 | 結果 255＝bat 中文被 cmd 切碎，**已修**（改純 ASCII） |

### 🚨 這 20 卷不在通用佇列的名單裡（查過了，別再懷疑）

| | 時間（UTC） |
|---|---|
| 通用佇列 `fetch_ocr_targets()` 抓快照 | 2026-09-17 **11:47** |
| 20 卷建列 | 2026-09-17 **16:50 – 17:57** |

晚了快五小時，而 `acquire_lock` 在 `main()` 只呼叫一次、佇列也只抓一次，所以那支
看不到這 20 卷——**不會重複轉錄，但也不會有人順手幫你做掉**。必須跑專用腳本。

### 每一輪怎麼看

```bash
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/uchimura_zenshu_ocr.py --status
cat scripts/state/mineru_gpu.lock          # 內容＝PID + 取得時間
```

### ✅ 書目已重建（2026-09-18 收工）

```bash
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/seisho_kenkyu_index.py   # 預設 --source both
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/seisho_kenkyu_build.py
```

站上 `public/content/collected-works/seisho-kenkyu.json`：

| | 之前（archive 粗 OCR）| 現在（雙源合併）|
|---|---|---|
| 有篇目的號 | 345 | **350** |
| 缺號 | 12 | **7**：[33,61,64,65,66,70,72] |
| 篇目數 | 1302 | **1353**（archive 1213／mineru 140）|

### 🚨 「比較準的 OCR」不等於「抽得比較多」——別把 mineru 當升級版換掉 archive

20 卷轉完後實測，MinerU **單獨用比 archive.org 的粗 OCR 還差**：

```
archive.org djvu   1327 筆｜相異號 349｜缺 8
本機 MinerU         937 筆｜相異號 339｜缺 18   ← 比粗 OCR 還少
逐號取較完整者      1378 筆｜相異號 352｜缺 5   ← 比兩邊都好
```

原因：MinerU 是版面感知的，年譜那種表列會被切成多行，而 `parse_text` 逐行比對，
一斷就不匹配；archive 的 djvu 純文字反而整行連著。兩份是同一批書的**獨立** OCR，
錯的地方不一樣，合起來才補得滿。只有 mineru 抓到的號 [131,137,336]，
只有 archive 抓到的 13 個。所以 `--source both` 已設為預設。

🚨 **挑哪一邊要用下游的判準。** 第一版按「筆數」比大小，結果第 344 號 archive 抽到
`''`、mineru 抽到「回顧三十年」，1:1 平手偏向 archive，整個號就在 build 丟碎片那一步
無聲消失。改成先比「清乾淨後有兩字以上的篇名數」才輪到總筆數。

剩下 7 個缺號的原因分兩種，都不是待辦：[33,61] 兩邊都只剩一個碎片字（年譜本身斷在那）；
[64,65,66,70,72] 兩份 OCR 都沒有，是真的沒被年譜引用到。
卷 01、15–18、20 抽得少也不是 bug：卷 01 是 1900 年創刊**前**的初期著作，
全卷 55 行含「號」、80 行含「研究」，但兩者同時出現的是 **0 行**。

---

## B 線：通用 OCR 佇列（內村跑完之後回來收尾）

### 現況

| 項目 | 數字 |
|---|---|
| 佇列總數 | **111 本**（內村 20 卷已全數離開佇列；含放回的 14 本誤殺）|
| 通用那批體積 | **14.7 GB**，中位數 119 MB |
| 起始規模 | 347 本 / 24.8 GB（2026-09-17 00:23 起跑） |
| 已完成 | 約 214 本 |
| 速率 | 09-17 19:47 起 7.1 小時做 71 本＝**10.1 本/時**、29,547 頁 |
| 預估剩餘 | 15–20 小時（本數只剩三成、位元組還剩六成，後段檔案更大） |

重開指令（照 09-17 18:15 那支的形狀）：

```powershell
Start-Process -FilePath 'C:\Users\user\AppData\Local\Python\bin\python.exe' `
  -ArgumentList '-u','scripts/mineru_ocr.py','queue','--limit','400','--wait-gpu-minutes','480' `
  -WorkingDirectory 'C:\Users\user\Desktop\know-graph-lab' `
  -RedirectStandardOutput 'scripts\logs\mineru_queue.out.log' `
  -RedirectStandardError  'scripts\logs\mineru_queue.err.log' `
  -WindowStyle Hidden
```

### ✅ 查完了：那兩本不是書的問題，而且不只兩本 —— 總共 14 本被誤殺

**結論：全部是環境問題，已全數放回佇列。** 佇列從 108 回到 122 本。

病因：07:50–08:11 那次 Modern Standby 醒來後 GPU 不穩，MinerU **每隔一本就死在起跑 5 秒**
（08:17:09 起、08:17:15 死，每一本都是這個形狀）——那時模型都還沒載完，
根本沒翻開書。證明方法最快：把其中一本單獨重跑。我拿 08:41 判失敗的
《從封閉世界到無限宇宙》重跑，**exit 0、乾乾淨淨**，結案。

`84791d07` 與 `d9ed9c34` 這兩本形狀不同（訊息停在進度條中間），是 07:50 那次
待機**直接打斷**的，就是坑 5 講的那種；其餘 12 本是醒來後的後遺症。

已修（commit `117c531c`），三道閘由窄到寬：

1. 錯誤訊息改取**尾巴**。MinerU 開頭固定三行 banner，而呼叫端只留 200 字，
   所以存進 `parse_error` 的永遠是那段廢話、死因被截掉 —— 這就是先前查不出死因的原因。
2. **死在 60 秒內＝環境問題**。載模型要 10–15 秒，死在這之前它沒碰到那本書。
3. 🚨 **連續 3 本失敗就整場停，並把那 3 本放回佇列**（`--max-streak`，預設 3）。
   這道閘不靠「看不看得懂訊息」—— 關鍵字表認不出來的死法還會有下一種，
   但好書不會排隊壞。

放回佇列＝把 `parse_error` 寫回 `'no extractable text'`（`fetch_ocr_targets()` 靠這字串撈）。

---

## 🚨 共同的坑（都是這兩天踩過的）

1. **GPU 只有 6 GB，同時只准一個 MinerU。** 鎖在 `scripts/state/mineru_gpu.lock`，
   `acquire_lock()` 在 `main()` 只呼叫一次，所以一支長班會**整場**佔著。撞到回 exit 4
   （忙碌，不是失敗）。

2. **不要只看 PID 活著就判斷卡死或沒卡死。** 父程序 CPU 長期 +0.0s 是**正常的**，
   真正在算的是子程序。而且**換書的空檔會讓子程序也靜止十幾秒**——
   2026-09-18 07:43 量 10 秒得到「沒在動」，量 30 秒得到「+86.6s，在算」。
   一律量 ≥30 秒：

```powershell
$snap=@{}; $ps = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*mineru*' }
foreach ($p in $ps) { $snap[$p.ProcessId] = (Get-Process -Id $p.ProcessId).CPU }
Start-Sleep -Seconds 30
foreach ($id in $snap.Keys) { $pr = Get-Process -Id $id -EA SilentlyContinue
  if ($pr) { "pid=$id +{0:N1}s" -f ($pr.CPU - $snap[$id]) } }
```

   **GPU 利用率也一樣**：單次 `nvidia-smi` 讀到 0% 很常見（用量是陣發的），
   連續取樣才作數——實測同一分鐘內在 0–87% 之間跳。

3. **長班一定要卸離主控台啟動。** 這台是 S0 Modern Standby，一進待機，掛在主控台的
   行程會收到 `STATUS_CONTROL_C_EXIT` 當場死掉——09-17 17:29 那次就這樣弄死了
   pid 2432。改用 `Start-Process -WindowStyle Hidden` 之後，09-17 20:02→09-18 00:31
   那次 4.5 小時待機**行程活下來了**。
   `keep_awake()` 有生效（`powercfg /requests` 看得到 SYSTEM 與 AWAYMODE），
   但那組旗標只擋閒置逾時，**擋不住闔蓋**。使用者的選擇是「人在才跑、走了就讓它睡」。

4. **PowerShell 裸 `python` 會中 `_whisper_venv`**，沒有 requests/fitz，卡在 import 不報錯。
   一律寫死 `C:\Users\user\AppData\Local\Python\bin\python.exe`。

5. **離開碼分流：0 成功／1 這本的問題／2 幻覺擋下／3 環境壞了要整場停／4 GPU 忙。**
   🚨 **2026-09-18 更新：這個判準已經補強，但要知道它為什麼補。**
   關鍵字表（`ENV_SIGNS`）只認得網路錯，而環境壞掉的死法列不完（GPU／驅動／待機／磁碟…），
   所以 09-16 斷網燒掉 30 本、09-18 待機醒來又燒掉 14 本。現在多了兩條：
   **死在 60 秒內一律判環境**，以及 **連錯 3 本就整場停並把那 3 本放回佇列**。
   查錯時記得：`parse_error` 存的是訊息**尾巴**了（以前存的是開頭的 banner，永遠看不到死因）。
   證明「是環境不是書」最快的方法是**把同一本單獨重跑一次**，exit 0 就結案。
   🚨 **待機打斷會被誤判成「這本的問題」。** 09-17 19:47:10 一次短暫 Modern Standby
   打斷了《波斯拜火教與古代中國》（死在 `Layout Predict 50%`），被標成 exit 1 踢出佇列。
   已把它重設回 `no extractable text`。判準：錯誤訊息停在進度條中間、時間點對得上
   睡眠事件（`Get-WinEvent -FilterHashtable @{LogName='System'; Id=@(506,507)}`），
   就是被打斷，不是書的問題。

6. **稽核一定要印分母，而且先驗迴圈有沒有跑到。**
   🚨 我的狀態腳本曾把 20 卷內村報成「MinerU 失敗」——因為它的分類順序把
   「訊息含 MinerU」擺在「含 no extractable text」前面，而那 20 卷的訊息是
   `no extractable text (1932 岩波掃描本，走本機 MinerU)`。**判失敗要看訊息是不是以
   `MinerU:` 開頭**，不要用 `in`。

7. **PostgREST 沒帶足夠 limit 會靜默截斷**（`limit=2000` 也會被伺服器上限壓回去）。
   要全撈就分頁 `limit=1000&offset=N` 迴圈。

8. **UTC。** `parsed_at`／`created_at` 都存 UTC，本地 +8。用本地日期去 filter 會撈到 0 筆
   而看起來「什麼都沒做」——這一天內犯過兩次。

9. **Bash heredoc 會吃掉一層反斜線。** 用 heredoc 寫 Python 會把 `\d` 變成 `d`、
   `\b` 變成**真的退格字元 `\x08`**（regex 從此永不命中且不報錯）。
   要寫含 regex 的腳本，用 Write 工具寫檔，不要用 heredoc。

10. **bat 只能放 ASCII**（中文註解或 echo 會讓 cmd 切碎指令，症狀是離開碼 255 且
    一行 log 都不寫）；**Python 腳本開頭要 `sys.stdout.reconfigure(encoding="utf-8")`**
    （主控台是 cp950，印一個「✓」就整支掛掉）。

11. 🚨 **簡繁轉換不可以套在日文上，而且要以整本為單位判。**
    入庫路徑（`ocr_with_gemini.write_jsonl` → `_trad`）會做簡→繁。內村是日文，
    第 11 卷就這樣入庫了，實測 0.78% 的字被改動、改的全是要害：

        云ふ → 雲ふ 604 處（「云ふ」＝說）      余輩 → 餘輩 61 處（「余」＝我）
        岩波書店 → 巖波書店      面→麵   里→裡   干→幹   却→卻   淀→澱（毀掉「淀橋」）

    **這種錯字數、段數、頁碼、簡體殘留率全部正常**，結構性稽核一律看不出來。
    已修（`11f77fd7`＋`8d501b30`）：用假名偵測，且 `book_is_japanese()` **整本算一次**
    ——逐段判會漏掉日文書裡本來就沒假名的扉頁、英文目次、年表（20 卷有 6 卷中招）。
    第 11 卷原檔已被覆寫救不回，重轉過了。要驗一卷乾不乾淨就數這個：
    `云ふ` 應該遠多於 `雲ふ`、`余輩` 應該遠多於 `餘輩`、`巖波` 應該是 0。

12. 🚨 **成品才是事實，帳本不是。** `uchimura_zenshu_ocr.py` 本來先看 ledger 有沒有記
    「做過了」就跳過，於是成品被刪掉要重轉時它照樣跳過、印「轉錄了 0 卷」收工——
    看起來像沒事做，其實是該做的沒做。判準一律用 `transcribed()`（Drive 上的 JSONL
    段數）。同理 `--status` 與 `uchimura_zenshu_done.py` 本來查 `ebooks.chunk_count`，
    但這條線從不寫 DB，所以 20 卷全轉完也永遠印「待轉錄 20 卷」、排程永遠不會自己關。

13. **看到「有別的 MinerU 在跑」先確認它走的是 GPU 還是 CPU。**
    `scripts/ocr_cct_apocrypha.py`（基督教典外文獻 10 冊）直接呼叫 `mineru.exe`
    且**沒有** `acquire_lock()`——但那是對的：它設了 `MINERU_DEVICE_MODE="cpu"`，
    不佔顯存所以本來就不必排鎖（小活不必跟夜班搶那張卡）。
    光看「呼叫 mineru.exe 卻沒取鎖」會誤判成繞過鎖；判準看 `MINERU_DEVICE_MODE`，
    或直接連續取樣 `nvidia-smi`——CPU 那種一路 0 MiB。

14. **原刊頁碼從缺是事實不是待辦。** 內村全 20 卷、1,571 行出處紀錄裡「頁」字零次；
    年譜只記篇名／號數／年月。頁面已把「原刊頁碼｜從缺」寫在統計列，
    **不要**為了好看去補流水號——假頁碼比沒有更糟。

---

## 不要做的事

- **不要殺不是自己啟動的程序。** 上面那條 `Stop-Process` 是使用者當面授權的例外。
- **commit 只加自己動過的檔**（`git add <具體檔名>`）。工作區有別的 session 未提交的
  東西，`git add -A` 或 `git diff --name-only` 全撈會把它們一起吞掉。
- **`test/original-readers.spec.ts` 與 `test/greek-full-reader.spec.ts` 的紅燈是別人的在製品**，
  別順手修。push 被 pre-push 擋下時用 `--no-verify`（使用者已授權），
  但**推完一定要比對 SHA**——hook 擋下也照樣 exit 0：

```bash
git fetch -q origin; git rev-parse master; git rev-parse origin/master
```

## 完成的定義

- `uchimura_zenshu_ocr.py --status` 顯示「待轉錄 0 卷」，排程自己 DISABLE
- 書目重跑後相異號 > 349、打架 < 61、缺號清單變短
- `/collected-works/uchimura/seisho-kenkyu` 的篇名連得到正文
- 通用佇列 `no extractable text` 歸零（或剩下的都有明確原因）
