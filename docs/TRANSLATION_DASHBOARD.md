# 全集翻譯進度桌面面板

雙擊 `scripts/translation-dashboard.cmd` 即可開啟（2026-08-27 從根目錄移進 scripts/）。

面板每 10 秒讀取一次本機 checkpoint、日誌修改時間與 Windows 程序列表，顯示：

- 榮格：早期著作及 Hull 英譯全集 CW 1–18（含 9i／9ii）的逐段進度
- 哲學家全集：柏拉圖／亞里斯多德 26 部作品的逐節快取與上架狀態
- 潘尼卡：每部作品逐段落進度
- 東方聖卷：每卷逐段落進度
- ACCS：每書卷逐頁 OCR 進度，以及「待入庫／已入庫」狀態；新卷會從
  執行命令的 `--pages` 自動取得目標頁數
- 其他工作：自動發現文獻回顧全文翻譯、一般電子書／全集翻譯、專書校潤、
  對話錄改寫、諾斯底文獻精修、大藏經目錄整理、訪談與參考書轉錄
- API 狀態：Gemini #1–#4、NVIDIA #1–#4、Ollama 本機服務的可用性、限流、
  延遲與最後檢查時間；每 5 分鐘更新，也可手動按「檢查 API」
- 執行中、已暫停、疑似停滯、待入庫、已入庫

API 健康檢查只讀供應商的模型清單端點，不送翻譯 prompt、不生成文字，
因此不消耗模型推理 token。「可連線」代表金鑰認證成功與服務可達，
不代表生成配額仍有餘量；實際工作仍可能因供應商 quota 回傳 429。

「API 狀態」頁也列出本機 AI 分流原則：分類、標籤、OCR 草稿、粗譯、格式清理、
異常掃描與 embedding 可優先使用 Ollama；學術文獻、神學術語、經典及出版終稿
仍須雲端模型或人工複核。

## 雲端 8-lane 翻譯池

`translation_cloud_supervisor.py` 將文獻全文依 `ref_key` 的 SHA-256 穩定分成
7 個互斥 shard：

- Gemini #1–#3：shard 0–2，各 worker 固定一把 key
- NVIDIA #1–#4：shard 3–6，各 worker 固定一把 key
- Gemini #4：不參與初譯，專門逐段比對原文／中譯

Gemini #4 reviewer 對每段輸出 `ok` 或完整修正版；ledger
`scripts/state/lit_review_quality_ledger.jsonl` 記錄原文＋最終譯文 hash。
任一內容日後改變，hash 失配便自動重審。各 lane 個別冷卻，單一 key 429
不會停止其他 worker。

### Claude 臨時接手某一 lane

Claude 不應直接和既有 worker 同寫。先取得有期限的 lease：

```powershell
python -X utf8 scripts/translation_lane_claim.py acquire `
  --lane gemini-2 --owner claude --minutes 120 --note "疑難術語人工協助"
```

supervisor 會停止該 lane，並暫停 Gemini #4 reviewer；其餘六條初譯繼續。
Dashboard 顯示 `claimed-by-claude` 與到期時間。Claude 完成後：

```powershell
python -X utf8 scripts/translation_lane_claim.py release --lane gemini-2
```

原 lane 自動恢復，Gemini #4 會因內容 hash 改變而重新審查。忘記 release 時，
lease 到期也會自動恢復。

## 本機常駐 Supervisor

`scripts/translation_supervisor.py` 是確定性排程器，不使用 AI 做程序決策。只要
Windows 沒有休眠、Ollama 與 `qwen2.5:7b` 可用、且沒有同一流水線 worker，就會持續
以 round-robin 輪流處理「潘尼卡 3 段 → 東方聖卷 3 段 → …」；本機 GPU 同時
只跑一個 worker，既有的遠端 API worker 可並行（但同一作品不並寫 checkpoint）。
worker 使用 Windows 低優先序，讓前景操作優先。
每段 checkpoint 記錄
`engines[i] = "ollama"`；本機草稿不會 build 或 upload。

登入排程由 `scripts/install_translation_supervisor.ps1` 建立。狀態與日誌：

- `scripts/state/translation_supervisor.json`
- `scripts/logs/translation_supervisor.log`
- `scripts/logs/translation_supervisor_worker.log`

手動查看或停止：

```powershell
python -X utf8 scripts/translation_supervisor.py status
python -X utf8 scripts/translation_supervisor.py stop
```

停止請求會在目前小批次結束後生效；也可在 Windows 工作排程器停用
`KGL_Translation_Supervisor`，避免下次登入重新啟動。

線上 AI 回來後，可只重譯本機草稿：

```powershell
python -X utf8 scripts/panikkar_auto.py --review-queue-step `
  --backend gemini-first --max-total-paras 10

python -X utf8 scripts/sbe_translate.py --review-local-step `
  --backend gemini-first --max-total-paras 10
```

只有同一作品的 `ollama` provenance 全部清空後，另加 `--upload` 才允許發布。

它不連線、不呼叫模型，也不消耗 AI token。雙擊表格中的作品可開啟對應資料夾或 checkpoint。

命令列驗證：

```powershell
python -X utf8 scripts\translation_dashboard.py --snapshot
python -X utf8 scripts\translation_dashboard.py --api-status
```
