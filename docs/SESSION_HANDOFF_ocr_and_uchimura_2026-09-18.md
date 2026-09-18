# 交接：本機 OCR 兩條線（通用佇列 ＋《內村鑑三全集》）

寫於 2026-09-18 08:20。接手的人先讀完再動手。這份取代
`SESSION_HANDOFF_uchimura_zenshu_2026-09-18.md`（那份只涵蓋內村那一半，仍可參考坑的部分）。

## 一句話任務

兩條線**共用同一顆 GPU、同一把鎖**，只能輪流跑：
先把《內村鑑三全集》20 卷轉完並重建《聖書之研究》書目，再回頭把通用 OCR 佇列
剩下的 107 本跑完。

---

## 🔴 立刻要做的第一件事

停掉通用佇列那支，讓內村這條線拿到 GPU。**這一步需要人按**——自動模式的權限層
會把 `Stop-Process` 擋成 `Interfere With Workloads`：

```powershell
Stop-Process -Id 29544,7052,9176,26936,21316 -Force
```

（PID 會變，先用下面「怎麼看誰佔著 GPU」那段重新抓。）

停掉之後**不必手動清鎖**：`acquire_lock()` 看到持有者 PID 已死會自己接收，
log 會印「（接收前一個已結束的 lock：PID ...）」。

停掉**不會掉進度**：那支是逐本入庫的，佇列狀態存在 DB 的 `parse_error`，
沒做完的書原樣留著，下次再跑就是了。2026-09-18 08:16 停的時候，它手上那本
（古埃及托勒密王朝）才剛開始一分鐘。

然後推內村那班（**要卸離主控台**，理由見坑 3）：

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
| OCR | ❌ **0/20**，`chunk_count` 全 None |
| 排程 | `KGL_Uchimura_Zenshu_OCR` 每晚 01:00（Ready，下次 09-19 01:00）；20 卷全完成會自己 DISABLE |
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

### 20 卷轉完之後（最容易被忘記的一步）

```bash
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/seisho_kenkyu_index.py --source mineru
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/seisho_kenkyu_build.py
```

**驗收看數字有沒有變好，不是「跑完了」。** 2026-09-18 08:10 用
`--source archive --report` 量到的基準：

```
總筆數 1327｜相異號 349／357｜有年月且對得上 200｜號與年月打架 61
沒出現過的號 8 個：[64, 65, 66, 70, 72, 131, 137, 336]
```

目標：相異號 **> 349**、打架 **< 61**、缺號清單變短。
另外**卷 01、15、16、17、18、20 這次抽出 0 筆**——日記兩卷本來就是連載自本誌，
抽不到八成是那幾卷年譜格式不同，拿 MinerU 的文字再看一次。

（站上 `public/content/collected-works/seisho-kenkyu.json` 目前是 archive.org 粗 OCR 版：
357 號、1,302 篇、`issuesWithItems` 345、`missingIssues` 12 個。）

---

## B 線：通用 OCR 佇列（內村跑完之後回來收尾）

### 現況

| 項目 | 數字 |
|---|---|
| 佇列總數 | 127 本＝通用 **107** ＋ 內村 20 |
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

### 待查：兩本 exit 1

08:16 前後 log 裡有兩本標成失敗，**還沒查**：

- `84791d07` 戰國時代的古史記憶──虞夏之際篇
- `d9ed9c34` 歷代信條

判斷方法見坑 5——先確認不是待機打斷造成的誤判；是的話把 `parse_error`
重設回 `no extractable text` 放回佇列，不要當成書的問題。

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

11. **原刊頁碼從缺是事實不是待辦。** 內村全 20 卷、1,571 行出處紀錄裡「頁」字零次；
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
