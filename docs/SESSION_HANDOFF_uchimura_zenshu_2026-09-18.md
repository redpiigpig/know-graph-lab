# 交接：《內村鑑三全集》20 卷本機 OCR ＋《聖書之研究》書目重建

寫於 2026-09-18 07:30。接手的人先把這份讀完再動手。

## 一句話任務

把已經下載好的《內村鑑三全集》（岩波 1932–33）20 卷用**本機 MinerU** 轉錄完，
然後用轉錄結果重跑《聖書之研究》的逐號書目，把站上的分號目次接上正文。

## 現況（2026-09-18 07:30 實測）

| 項目 | 狀態 |
|---|---|
| PDF 下載 | ✅ 20/20，18,074 頁 / 0.88 GB，逐卷用 PyMuPDF 開過 |
| Drive 位置 | `G:\我的雲端硬碟\資料\知識圖工作室\全集\神學\內村鑑三\岩波全集（1932-33）\` |
| ebooks 登記 | ✅ 20 筆，`collection=collected-works`，id＝`d0000001-0000-4000-8000-0000000000NN`（NN＝卷次） |
| OCR | ❌ **0 卷**。`chunk_count` 全 None |
| 夜班排程 | `KGL_Uchimura_Zenshu_OCR` 每晚 01:00，上限 5 小時，錯過補跑，20 卷全完成會自己 DISABLE |
| 書目（archive.org 粗 OCR 版） | ✅ 1,302 篇、涵蓋 345／357 號 → `public/content/collected-works/seisho-kenkyu.json` |
| 站上頁面 | ✅ `/collected-works/uchimura/seisho-kenkyu`（逐年→逐號；卷轉錄好了篇名才變連結） |

### 為什麼 0 卷

昨晚 01:00 那班離開碼 255、一行 log 都沒寫——bat 裡的中文被 cmd.exe 從中間切碎。
**已修**（改純 ASCII），手動跑過確認 log 正常。

但接著撞到真正的阻塞：**GPU 被另一個 MinerU 佔著**。
PID 29544 ＝ 2026-09-17 18:15 啟動的 `mineru_ocr.py queue --limit 400 --wait-gpu-minutes 480`，
它一啟動就把 `scripts/state/mineru_gpu.lock` 鎖住**整場**（`acquire_lock` 在 main 只呼叫一次），
所以我們的夜班只能讓路。那是別的 session 起的程序，**不要自己殺**。

## 每一輪要做什麼

```bash
# 1. 看全集轉到哪
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/uchimura_zenshu_ocr.py --status

# 2. 看 GPU 現在誰在用（鎖檔內容＝PID＋取得時間）
cat scripts/state/mineru_gpu.lock
```

判斷鎖的持有者是「真的在算」還是「卡死」——**不要只看 PID 活著**：

```powershell
# 父程序 CPU 低、記憶體小是正常的，真正在算的是它的子程序
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.WorkingSetSize -gt 500MB } |
  Select-Object ProcessId, @{n='MB';e={[math]::Round($_.WorkingSetSize/1MB)}}, CommandLine
# 量 10 秒 CPU 增量；有在動就是真的在跑
```

GPU 一空出來就手動推一班（不必等 01:00）：

```bash
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/uchimura_zenshu_ocr.py --max-minutes 240
```

## 20 卷轉完之後（這才是重點，別忘了）

```bash
# 1. 用 MinerU 的輸出重跑書目抽取（現在那版是 archive.org 的粗 OCR）
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/seisho_kenkyu_index.py --source mineru

# 2. 重建站上 JSON
C:/Users/user/AppData/Local/Python/bin/python.exe scripts/seisho_kenkyu_build.py
```

驗收要看**數字有沒有變好**，不是「跑完了」：

- 相異號數 **要多於 349／357**（目前缺 12 號：18、33、61、64、65、66、70、72、131、137、336、344）
- 「號數與年月打架」要少於 61 筆
- 卷 1、15、16、17、18、20 這次抽出 0 筆——日記兩卷本來就是連載自本誌，抽不到八成是
  那幾卷年譜格式不同，用 MinerU 的文字再看一次

## 🚨 這條線特有的坑（都是踩過的）

1. **bat 只能放 ASCII**。中文註解或 echo 會讓 cmd 把指令切碎，症狀是離開碼 255 且**一行 log 都不寫**。
2. **Python 腳本開頭要把 stdout 轉 utf-8**。主控台是 cp950，印一個「✓」就 UnicodeEncodeError
   整支掛掉——register 那支就這樣死在第 13 卷。三支都補過了，新寫的也要補。
3. **python 一律寫死 `C:\Users\user\AppData\Local\Python\bin\python.exe`**。裸 `python` 會中
   `_whisper_venv`，沒有 requests/fitz，卡在 import 不報錯。
4. **MinerU 離開碼**：0 成功／1 這本的問題／2 幻覺擋下／**3 環境壞了要整場停**（一次斷網曾把 30 本
   全標成 failed）／**4 GPU 忙，不是失敗**。`uchimura_zenshu_ocr.py` 已照這個分流，別改壞。
5. **GPU 只有 6 GB，同時只准一個 MinerU**。lock 在 `scripts/state/mineru_gpu.lock`。
6. **筆電會通勤休眠**：昨晚 23:14→今早 07:15 完全沒進度，而且半夜斷網（daily log 一片
   `getaddrinfo failed`）。所有東西都要能續跑，別照「機器一直開著」設計。
7. **原刊頁碼從缺，這是事實不是待辦**。全 20 卷、1,571 行出處紀錄裡「頁」字零次；年譜只記
   篇名／號數／年月。頁面已經把「原刊頁碼｜從缺」寫在統計列，**不要**為了好看去補流水號。
8. **不要殺別人的程序**；**commit 只加自己動過的檔**（工作區有別的 session 未提交的東西）。
9. 目前測試有一個紅燈 `test/original-readers.spec.ts`（希伯來讀本名詞分組順序），
   是別的 session 的在製品，不是這條線的，別順手「修」它。

## 完成的定義

- `uchimura_zenshu_ocr.py --status` 顯示「待轉錄 0 卷」，排程自己 DISABLE 掉
- 書目重跑後相異號數 > 349，缺號清單變短
- `/collected-works/uchimura/seisho-kenkyu` 上的篇名已經連得到正文
