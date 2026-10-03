# 交接 PROMPT：Schaff 教父全集補譯＋重新對齊（2026-10-03）

> 新 session 把下面「給新 session 的 PROMPT」整段貼上即可。

---

## 給新 session 的 PROMPT

```
接續 Schaff 教父全集（ANF＋NPNF1＋NPNF2，38 本）中文欄的補譯與重新對齊。
先讀 docs/SESSION_HANDOFF_fathers_fill_2026-10-03.md 全文，再讀 .claude/skills/scripture-fathers/SKILL.md
（10-02／10-03 新增那段：fathers_realign／fathers_fill_gaps／fathers_lane），以及記憶
project_fathers_translation_gaps、project_fathers_three_column_repair、feedback_translation_output_gate、
feedback_glossary_strict_authority、feedback_bible_quote_version、feedback_translation_numerals、feedback_save_claude_usage。

背景 lane 已在跑（排程 KGL_Fathers_Fill 每 30 分鐘保姆）。依文件「待辦」：①先抽樣驗收已補的譯文與對齊
②修批次 TypeError ③確認漏掉的那一卷 ④確認 /fathers 讀到新譯文 ⑤全部補完後關排程、更新 SKILL 與記憶。
原則：模型只用 Gemini→NVIDIA；能腳本不開 agent，要開最多 1 個 Sonnet；會改寫同一本書 JSONL 的程序不可並行
（DO_NOT_TOUCH_ids.txt）；commit 只 add 自己改的檔，push 後確認進遠端。一律用繁體中文回覆。
```

---

## 為什麼做這件事

電子圖書館註腳盤點（`output/toc_audit/footnote_gaps.tsv`）的 A 型缺口 48,215 則裡，約 39,000 則落在這 38 本
CCEL 教父集中譯本。10-02 量測（`output/relink/bi_health.py`）發現根本原因不在註腳：
**中英字數比多在 0.02–0.2（完整譯本約 0.3–0.4）＝中文只譯了 5–30%**，而且同列段首節號一致率只有 20–60%
＝**中文段錯位**（例：2accee20 塊 40 英文是詩篇第 8 篇、中文是第 9 篇）。使用者 10-02 晚上定：現在做補譯。

## 現況（10-03 09:30）

| 項目 | 狀態 |
|---|---|
| 重新對齊（階段 1） | ✅ 37 卷全做完；從錯位救回 388 列 |
| 量出的真缺口 | 正文 20,740 列＋註文 12,668 列（以段為單位，不是「中文非空」） |
| 補譯（階段 2） | 6 卷補完、19 卷補到一半、12 卷未開始；已補約 4,719 列 |
| 背景 lane | `scripts/fathers_lane.py --run`（10-03 早上 PID 10696），log `output/fathers_gap/lane_run.log`、`.err` |
| 保姆排程 | `KGL_Fathers_Fill`：每 30 分鐘、ExecutionTimeLimit 2 小時、IgnoreNew；跑 `scripts/fathers_fill_keeper.ps1` |
| 狀態檔 | `output/fathers_gap/lane_state.json`（每卷 realign 統計、realigned、fill_last、fill_done）；各卷缺口 `output/fathers_gap/{id前8}.gaps.json` |

這批是 10-02 晚上一個 Sonnet agent 建的；它在撞到 Claude 用量上限時被中斷，**沒來得及回報與驗收**，
腳本由主 session 於 10-03 代為 commit。所以下面的驗收是必做，不是可選。

### 主要腳本
- `scripts/fathers_realign.py`、`scripts/fathers_realign_volume.py`：錯位中文段搬回真正對應的英文列（測試 `scripts/tests/test_fathers_realign.py`）
- `scripts/fathers_fill_gaps.py`：缺譯列逐段補譯（Gemini→NVIDIA），失敗記 `output/fathers_gap/fill_fail.json`
- `scripts/fathers_lane.py`：階段 1＋2 長跑、可續跑、額度用盡 exit 3；處理中的卷寫進 `output/restructure/DO_NOT_TOUCH_ids.txt`
- `scripts/fathers_fill_keeper.ps1`：保姆（lane 沒在跑且 `--status` 不是 DONE 就重拉）
- `scripts/audit_fathers_en_alignment.mjs`：英文欄對齊稽核
- `scripts/fix_fathers_heading_swallow.py`：加了讀 DO_NOT_TOUCH

## 待辦

1. **抽樣驗收（最優先）**：從 fill_done 的 6 卷各抽 20 段，逐段對照英文看：是不是這一段的譯文（不是鄰段）、
   `[^N]` 數量位置、譯名是否照詞庫 name_recommended、聖經引文版本、數字體例、有沒有回覆語或 <think> 外洩。
   再抽 3 卷看重新對齊搬過的列（rescued_rows）是否真的搬對。有系統性問題就先停排程（`schtasks /change /tn KGL_Fathers_Fill /disable`）再修。
2. **批次 TypeError**：`lane_run.log` 有「✗ 批次例外 TypeError: expected string or bytes-like object, got 'NoneType'」，
   整批跳過但 lane 繼續——疑似某列 source 是 None。修掉，並確認被跳過的列之後會重補（不是永久漏掉）。
3. **38 本只進了 37 卷**：對照 `bi_health.py` 的清單與 `lane_state.json` 找出缺的那卷、查為什麼沒進。
4. **/fathers 讀不讀得到**：確認 /fathers 頁面讀的是同一份 JSONL（R2）還是另有 DB 表；若另有，要一併更新（成品多處要一起改）。
5. **補完之後**：關掉 KGL_Fathers_Fill（記憶 feedback_disable_finished_schedules）、清 DO_NOT_TOUCH、
   重跑 `relink_missing_footnotes.py --scan` 看 A 型缺口降多少、更新 SKILL 與記憶 project_fathers_translation_gaps。
6. 註腳：補譯完成後，這 38 本的 `[^N]` 才有意義，再交給每日 `KGL_Footnote_Relink`（04:30）或另做「英文欄註號位置→同列中文」的搬移。

## 同時在跑、不要碰的
- `KGL_Footnote_Relink`（04:30，每日模型補註腳）：會讀 DO_NOT_TOUCH，跟 lane 不衝突。
- 538 本無文字層 PDF 的 MinerU 重轉錄：`output/restructure/night3_relay.py`（等 GPU 空就跑 `requeue_reocr --from-ledger --engine mineru`），
  log `output/restructure/night3_reocr.log`。10-03 修了 `mineru_ocr.py`（先複製成本機 ASCII 檔名再丟 MinerU——路徑含全形逗號／《》時
  它回「No supported documents found」，被當環境錯誤整場停，一夜零進度）。詳見 `docs/SESSION_HANDOFF_ebook_quality_2026-10-02.md`。
