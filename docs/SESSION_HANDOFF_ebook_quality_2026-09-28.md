# 交接 PROMPT：電子圖書館品質四條線（2026-09-28）

> 新 session 把下面「給新 session 的 PROMPT」整段貼上即可。後面是背景與各線細節，PROMPT 會叫你讀。

---

## 給新 session 的 PROMPT

```
接續電子圖書館品質工程，四條線：OCR 監測、目錄章節重排、註腳連結、原文／中譯雙欄對照。
先讀 docs/SESSION_HANDOFF_ebook_quality_2026-09-28.md 全文，再讀記憶
feedback_translation_priority_and_t_pages、feedback_save_claude_usage、feedback_transcribe_page_numbers、
feedback_commit_only_scripted_files、feedback_bash_heredoc_eats_backslash。

第一步只看不寫：
1. 跑 python -X utf8 scripts/watch_pipelines.py，回報 OCR 待轉錄數、最新 OCR 日誌、艦隊各線（含 library-religion）。
2. 看 output/toc_audit/llm_toc.log 最後幾行，補章節批次跑完沒；跑完就印 llm_toc_chapters.tsv 各結果計數。
3. 跑 python -X utf8 scripts/relink_missing_footnotes.py --scan，回報缺註腳連結最多的前 20 本。
4. 看 output/translation_queue/progress/ 各書已譯塊數，並抽 3 塊驗頁碼標記 {{p:N}} 數量與原文一致。
回報完再照文件「各線待辦」依序做。原則：能腳本不開 agent；翻譯走 Gemini→NVIDIA 不接 Haiku；
agent 最多同時 3 個、用 Sonnet；commit 只 add 自己改的檔；push 後比對 git rev-parse HEAD 與 git ls-remote origin master。
一律用繁體中文回覆。
```

---

## 共通規則與坑

- **寫入 Drive／R2／DB 會被自動模式擋下**（「Modify Shared Resources」）。乾跑可以照跑；要 `--apply` 時先把乾跑結果給使用者看、請他放行，或請他把 session 切到略過權限模式。**不要自己改權限設定**（會被判成自我修改而擋下）。
- **頁碼規則**（使用者定）：轉錄來的中譯本與原文本各自保留自己的頁碼，寫純數字；**我們自己翻譯的**中文欄頁碼顯示 `t.13`（＝原文第 13 頁），論文引用一律引原文頁。自譯的塊帶 `translation: "self"`。
- **一節一塊**：一頁一塊的書盡量合成一節一塊，原書頁碼靠 `{{p:N}}` 內嵌標記＋`page_numbers` 保留（`scripts/consolidate_page_chunks.py`）。
- **推送前的 hook 會跑整套測試約 3 分鐘**。`git push` 的逾時至少給 600 秒，不然推送被切斷、遠端還是舊版。
- **heredoc 會吃反斜線**：含 `\d`、`\n` 的 Python 用 Write／Edit 工具寫檔，不要用 `<<'EOF'`。
- **JSONL 在 Drive**：`G:\我的雲端硬碟\資料\知識圖工作室\_chunks\{id}.jsonl`。`G:` 不見先 `Test-Path 'G:\我的雲端硬碟'`（CLAUDE.md 有修法）。
- 每次改檔前腳本會留 `.jsonl.bak_*` 備份；**不要刪備份**，出錯靠它回復。

---

## 一、OCR 監測

- **看哪裡**：`scripts/watch_pipelines.py` 第三節（ebooks 總數、已解析、待轉錄、最新 `ocr_*.log` 成功／失敗／額度／斷網、三個 `KGLab-OCR-Daily-*` 排程）。
- **引擎**：MinerU 是主力（本機 GPU 6GB，一次只能跑一個，有鎖）；Gemini 為輔，免費層一天約 20 次／key，額度到頂是每天正常結尾，不是故障。
- **09-28 現況**：佇列約 108 本，另有韋伯《印度的宗教》排在 GPU 上。
- **要盯的坑**
  - 掃描書帶封面文字層會被當成已解析而漏 OCR（韋伯 536 頁只有 605 字仍「解析成功」）→ 判掃描看**每頁字數**。
  - 環境錯（CUDA、套件）會一口氣燒掉整個佇列 → 連錯 3 本整場停並放回，別放著讓它燒。
  - MinerU 只讀 `preproc_blocks`；頁碼與註腳在 `discarded_blocks`，要回頭讀 middle.json 才不會丟。
  - MinerU 會把「一二三十」這類純筆畫字判成分隔線丟掉。
  - OCR 重複幻覺：結構完美、內容胡謅，DB 的 100 字預覽看不出，要讀 Drive 全文尾段。
- **完工判準**：待轉錄數下降、失敗類別不是環境錯；新轉錄的書要跑下一節的章節與合併流程。

## 二、目錄章節重排

**已完成**（09-27～28）：EPUB 改讀 NCX（47 本變好）、附錄子條目合併、1,043＋100 本補印刷頁碼、628 本合成一節一塊、1,246 本用 PDF 書籤補章節。

**進行中**：`scripts/chapters_via_llm_toc.py --apply`（模型讀書前幾頁的印刷目錄補章節再合併），對象是書籤不能用的 1,267 本。09-28 晚間跑到 975 本：

| 結果 | 本數 |
|---|---|
| 補好並合併 | 473 |
| 模型找不到目錄 | 408 |
| 落點不足或重複 | 83 |
| 覆蓋不到一半 | 12 |

日誌 `output/toc_audit/llm_toc.log`，逐本結果 `output/toc_audit/llm_toc_chapters.tsv`，每本改前留 `.jsonl.bak_chapters`。

**待辦**
1. **稽核那 473 本「補好」的書**。放行門檻是覆蓋過半，會漏章。實例：Madsen《Democracy's Dharma》漏了第一、二章，Notes 被吞進 Conclusions。建議判準：
   - 第一個正文章節起點落在全書 15% 之後；
   - 章數明顯少於目錄頁條目數；
   - 最後一章跨進 Notes／Bibliography／Index 頁。
   抓到的書修法見下。
2. **修法（Madsen 英文本的作法）**：讀 `.jsonl.bak_chapters`（逐頁），先驗「PDF 頁 − 印刷頁」差值全書一致，照印刷目錄列出每章起始 PDF 頁，逐頁指派 `chapter_path`，缺的 `printed_page` 用差值補，再 `consolidate_page_chunks.consolidate()` 合併，寫回＋推 R2＋更新 DB。一次性腳本寫法可參考本文件附錄。
3. **408 本「找不到目錄」**：先抽 10 本看是真的沒目錄頁（論文集、單篇），還是目錄在前 8% 以外、或 OCR 太爛。依原因決定擴大讀取範圍或改用內文標題偵測。
4. 稽核工具：`scripts/audit_toc_accuracy.py`（報告 `output/toc_audit/summary.md`）。

## 三、註腳連結

**reader 規則**：正文 `[^N]`；15 個以上破折號的分隔線切換進註釋模式；註文寫 `(N) 內容`，會出現 ↩ 回正文。

**工具**
- `scripts/relink_missing_footnotes.py`（09-28 新增，有測試）：補「有註文、正文沒連結」的註號。
  - 規則步驟零成本，處理上標「²」、黏年份「341941年」、殘缺「臨濟寺1舉行」。
  - `--llm` 讓模型定位，走 Gemini→NVIDIA，並有唯一性與緊貼他註兩道過濾。
  - `--scan` 全館盤點，輸出 `output/toc_audit/footnote_gaps.tsv`。
  - 民主妙法實績：缺連結 143 → 20。
- `scripts/link_footnotes.py`：處理「章末有 `## 註釋` 或 `[N]` 條列、但不在註釋模式」的書。🚨 09-28 第一次 `--apply` 弄壞 83 本（`{{p:[^34]}}`、`[^5],000`），已全部從備份回復，也修了程式並改成跳過已合併的書。**再 apply 前先乾跑抽 10 本逐處看。**
- `scripts/survey_footnotes.py`：全館註釋型態盤點。

**待辦**
1. `--scan` 後由缺連結最多的書開始，先乾跑、逐條看，再 `--llm`，最後給使用者放行 `--apply`。
2. 民主妙法剩 20 則：5 則前後註號相距超過 6,000 字；幾則模型給的句子不唯一；幾則旁邊的舊註號本身排錯（例：註 6 後直接接 [^10]）。**要對照原書頁面人工修**，不要放寬過濾。
3. 「舊註號排錯」可能是全館性問題：寫一個檢查，找塊內 `[^N]` 順序倒退的書，列清單給使用者。

## 四、原文／中譯雙欄對照

**使用者要求**：外文書要有中譯，中譯本要有原文，兩欄逐段對照。

**A. 已有中譯本的外文書（轉錄對轉錄）**
- 工具 `scripts/align_reference.py`：
  - `--dry-run --samples N` 看對齊報告與抽樣。
  - `--anchors` 啟用錨點校正，覆蓋率保證不比舊法差。
  - `--apply` 寫入；自動同一本書檢查沒過時，要人工核對後才加 `--force`。
- 09-28 修正：目錄頁不當章節錨點；導讀、中文版序、譯後記歸中譯本獨有，不按位置硬配；補「自序」「結論」「謝辭」「圖目次」；相鄰同種類小節合組。
- **民主妙法已完成**（Madsen 727d0835 ↔ 539068d3）：覆蓋 79.2%，38 塊有原文欄，兩邊頁碼各自保留。
- **對齊前一定先印兩邊的 chapter_path 清單目視**。原文側章節錯了（如 Madsen），對齊一定錯，要先照第二節修。
- 候選清單：`output/reference_pairs/report.md`、`pairs_134.tsv`、`verify_results.json`（子代理 09-28 產出）。
  - 37 組「無法判定」：多為短篇講章，人工抽 3–5 段後個別放行。
  - 47 組語言不符：其中 36 組是中文配中文或英文配英文，代表 `output/untranslated_inventory/untranslated_v2.tsv` 誤判，要回頭修清單。
  - 7 組配不到 zh_id：同作者多本書共用短題，要人工指定。
  - 另有 3 組錯書、3 組檔案損毀或缺檔。
- 09-26 重篩確定同一本的 2 對：Guthrie《基督徒的重大利益》、圖倫丁第一冊，見 `output/reverse_originals/confirmed_same.tsv`。另有 18 對在 `review_candidates.tsv` 待人工看。

**B. 沒有中譯本的外文書（自譯）**
- 艦隊 lane `library-religion`，腳本 `scripts/library_translate_queue.py`，書單 `output/translation_queue/religion_queue.tsv`。
  - 順序：論文相關（第 0 級，39 本）→ 宗教學（110）→ 世界宗教的宗教史類（72）。
- 流程：
  - 從現有 JSONL 翻，先存 `.jsonl.src_en` 快照。
  - 逐塊寫進 `output/translation_queue/progress/{id}.jsonl`。
  - 整本譯完才換檔、推 R2、更新 DB。
  - 還沒補章節的一頁一塊書先跳過。
- 09-28 修正：
  - 模型把 `{{p:6}}` 吃成 `{p:6}`，現在改回雙括號；仍缺就換引擎，都缺才補在塊首。
  - 原文沒有的 `[^N]` 改回純數字。
  - 300 字以上的塊都驗截短（目錄頁 583 字曾只回「目錄」）。
  - 組裝前對舊譯文再修一次。
- 速度卡在 Gemini 免費額度：09-28 第一本《聶斯脫里派教會》91 塊只譯 8 塊。**不要為趕進度接 Haiku。**
- 盯法：progress 檔行數；抽塊比對 `{{p:N}}` 數量；抽看有無英文殘留或推理外洩（`<think>`）。

---

## 附錄：Madsen 英文本重派章節的一次性作法（範本）

```python
import json, sys
sys.path.insert(0, "scripts")
import consolidate_page_chunks as cp, standardize_ebook as se
BID = "<原文書 id>"
cs = [json.loads(l) for l in open(rf"G:/我的雲端硬碟/資料/知識圖工作室/_chunks/{BID}.jsonl.bak_chapters", encoding="utf-8")]
OFFSET = 28                       # 先驗：所有有 printed_page 的頁，page_number - printed_page 都等於它
STARTS = [(1, ""), (7, "Contents"), (15, "Preface"), (29, "1. …"), (44, "2. …"),
          (159, "Conclusions"), (187, "Notes"), (203, "Bibliography"), (211, "Index")]   # 照印刷目錄
for c in cs:
    c["chapter_path"] = [t for s, t in STARTS if s <= c["page_number"]][-1]
    if c["page_number"] > OFFSET and not c.get("printed_page"):
        c["printed_page"] = c["page_number"] - OFFSET
merged = cp.consolidate(cs)
# 先印 merged 各塊 (page_number, printed_page, chapter_path, 字數) 目視，確定後：
# o = se.write_jsonl(BID, merged); se.push_to_r2(BID, o); se.update_db(BID, merged)
```
