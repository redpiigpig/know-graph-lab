# 交接 PROMPT：電子圖書館品質（2026-10-02）

> 新 session 把下面「給新 session 的 PROMPT」整段貼上即可。後面是現況、待辦與坑，PROMPT 會叫你讀。
> 上一份是 `docs/SESSION_HANDOFF_ebook_quality_2026-09-28.md`（已大致完成，背景參考用）。

---

## 給新 session 的 PROMPT

```
接續電子圖書館品質工程。先讀 docs/SESSION_HANDOFF_ebook_quality_2026-10-02.md 全文，
再讀 .claude/skills/ebook-pipeline/SKILL.md 開頭的〈📐 轉錄規格〉與 2026-09-30 之後各段，
以及記憶 feedback_numbered_points_not_footnotes、feedback_save_claude_usage、feedback_ebook_images_drive_only、
feedback_commit_only_scripted_files、feedback_bash_heredoc_eats_backslash。

依文件「待辦」三項依序做：①每日自動用模型補註腳（排進排程）②69 本 PDF 從版面找回上標註號
③約 900 本未重建的書分流（重 OCR／修章節／對照書）。
原則：能腳本不開 agent；模型走 Gemini→NVIDIA 不接 Haiku／Claude；agent 最多 1 個、用 Sonnet；
會改寫同一本書 JSONL 的程序不可並行；長批次用 PowerShell Start-Process 起獨立行程、寫 log；
改結構的規則上線前要抽樣逐頁用眼睛看正文順序（守恆閘只防少字、防不了搬錯位置）；
commit 只 add 自己改的檔，push 後確認進遠端。一律用繁體中文回覆。
```

---

## 現況（2026-10-02 早上）

| 項目 | 完成 | 備註 |
|---|---:|---|
| 電子圖書館一章一頁＋每頁約五千字＋段號 | 4,387／5,291 本（有全文者） | 有 `.jsonl.bak_restructure` 的即已做；含無章節模式 |
| 全集（單語） | 225／557 | 另 60 部有標準引用號（柏拉圖等）刻意不動 |
| 全集（多語）段號 | 86 部 | `number_multilingual.py`，不合併頁面 |
| 中外對照書（民主妙法等） | 民主妙法＋圖書館對照書 50 本段號、36 本分頁 | |
| 新書自動套用 | ✅ | `run_ocr_daily.bat` Step 5c → `scripts/postprocess_fresh_books.py` |

**規格**（全文在 ebook-pipeline SKILL.md〈📐 轉錄規格〉）：一章一頁、章 >6,500 字分頁每頁約五千字（節優先）；章 `##`／節 `###`；
段號 `{{s:章-節-段}}`（以原文為準）；只有分隔線（15+ 破折號）後才是註釋；EPUB 插圖只從 Drive 原檔讀（不上 R2）；
卷首引言楷體署名靠右；保留印刷頁碼；章節不可靠的書走「無章節模式」（照原順序每頁約五千字、段號全書流水號）。

**10-02 修掉的重大 bug**：`split_notes_keep_order` 把正文裡「(1)」起頭的分點全當註釋搬到章末——370 本、20,008 段，
守恆全過所以閘門擋不住；已全數從備份重建回原位（`output/restructure/misplaced_notes_ids.txt`）。
它也讓註腳盤點把分點誤算成「正文缺註號」，曾差點導向「回 EPUB 重抓註號」的錯誤工程——**EPUB 一本都不需要重抓**。

### 主要腳本
- `scripts/restructure_chapters.py`：一般模式＋無章節模式＋`paginate`；`--apply --new-only --ids 檔`；從 `.bak_restructure` 重建
- `scripts/repaginate.py`：已重建的書就地再分頁（保留補過的註腳）；中英對照頁同列一起切
- `scripts/reflow_pdf_paragraphs.py`：PDF 整頁一段的回原檔重抽段落（每本子行程、15 分鐘逾時、PDF 先複製到本機）
- `scripts/epub_figures.py`：EPUB 插圖放回正文
- `scripts/number_multilingual.py`、`scripts/rebuild_reference_bilingual.py`：對照書
- `scripts/relink_missing_footnotes.py`＋`scripts/relink_batch.py`（rule｜llm）：補註腳連結
- `scripts/postprocess_fresh_books.py`：新書後處理（每日排程）

---

## 待辦

### ① 每日自動用模型補註腳
- 最新盤點 `output/toc_audit/footnote_gaps.tsv`（10-02 04:46）：有註文 205 本、缺連結 57,305 則；其中已重建可動 145 本。
- 分型 `output/relink/booktypes.tsv`（`output/relink/booktypes.py` 產）：
  - **A 型**（有 `[^N]` 但部分丟失，模型可補）50 本、約 5,800 則——這是要每天補的對象；
  - **F 型**（正文完全沒註號）69 本、約 4,000 則→ 見待辦②；
  - **E 型**（其實不是註腳，如神學大全問題清單）19 本、約 3,900 則→不必補，應從盤點排除；
  - C／D 型（正文註號是 (N)／[N] 格式）共 7 本、33 則→量小。
- 10-02 夜跑：規則補 3 則、模型補 32 則後連續撞額度照規則停。Gemini 免費層每 key 每天約 20 次，NVIDIA 也有速率限制，
  所以一天大約只能補幾十到上百則——要做成**每日排程**：`relink_batch.py llm`（照優先級：神學／宗教學／世界宗教先），
  連續兩次額度錯就停、隔天續跑；跑前用 `booktypes.py` 重產分型（它讀 `output/relink/eligible.tsv`，eligible 的產法見
  `output/restructure/night_relay2.py`）。注意：`relink_batch.py` 會讀 `output/restructure/DO_NOT_TOUCH_ids.txt`
  （目前已清空）；若同時有重建批次在跑，要把那批 id 寫進去避開。
- 《Body and Society》（5b2128e9）重建時洗掉了上次模型補的 13 則，A 型清單裡會再補到。
- E 型排除：建議在 `relink_missing_footnotes.py --scan` 的計數加判斷（註文平均 <40 字且整頁都是短問句就不算註腳）。

### ② 69 本 F 型 PDF：從版面找回上標註號
- 書單：`output/relink/booktypes.tsv` 裡 type 以 F 開頭的（以 PDF 為主，另有少數 DOCX）。
- 想法：PyMuPDF `page.get_text("dict")` 看每個 span 的 `flags & 1`（上標）或字級明顯比前一個 span 小的純數字，
  取它前面 10–20 字當錨點，回現行 JSONL 找同一段文字插入 `[^N]`，再把章末註釋依引用頁分配（`restructure_chapters.paginate` 那套）。
- ⚠️ 10-02 拿 Watson《十誡》試，抓到 0 個上標——那本根本沒有註腳（是 bug 造成的假註腳）。先挑真正有註腳的書試，
  例：《印度的宗教》、《上帝之城》（吳飛譯）、《馬丁·路德的神學》。掃描書（MinerU OCR）沒有文字層的上標資訊，這法不適用。
- 寫回前抽 5 本逐處看註號位置對不對；字數守恆照做（只多 `[^N]`）。

### ③ 約 900 本未重建的書分流
- 清單：`output/restructure/unrestructured.tsv`（id、書名、格式、分類、最後一次被擋的原因）。910 本，原因分布：
  稽核旗標 212、章名不連續 179、未判讀 144、章內段落過少 79、少於 2 章 60、章節覆蓋不足 59、有對照欄 52、
  OCR 亂碼章名 48、章名黏正文 35、找不到檔 22、段落沒切開 14、守恆失敗 4。
  （很多原因欄後面還寫著「無章節模式也不行：段落沒切開／合併後段落沒切開」——即文字本身整頁黏成一團。）
- 分流建議：
  - **文字整頁黏成一團、且是掃描書**（沒有文字層可重抽）→ 排回 OCR 佇列重做（MinerU；GPU 一次只准跑一個，有 lock）；
  - **有文字層的 PDF** → `reflow_pdf_paragraphs.py` 再試；
  - **OCR 亂碼章名** → 重 OCR；
  - **有對照欄（52 本）** → `number_multilingual.py --ids` ＋ `repaginate.py --ids`；
  - **未判讀（144）** → 多半是新書或檔案剛補，直接跑 `restructure_chapters.py --apply --new-only --ids`。
- 做完的書每日排程不會重做（看 `.bak_restructure`），但新書會自動走同一套。

---

## 10-02 下午進度（接手先看這段）

- **① 完成**：排程 `KGL_Footnote_Relink` 每日 04:30 跑 `scripts/relink_footnotes_daily.py`（log `output/relink/daily.log`）。
  舊版兩個靜默失效已修（N±1 區間→連續缺號整本 0 則；額度用完偵測不到→整批空跑）；加了四道防硬放閘；昨晚上線的 32 則人工看過、拆掉 5 則錯的。
  每天上限 400 次呼叫，實測約 15% 會放（其餘被閘擋），一天約補 60 則。**明早看 daily.log 抽 10 則落點**。
- **② 改道**：F 型缺口 89% 在 EPUB，新工具 `scripts/relink_from_epub.py` 從原檔錨點補（零模型），已補加爾文 882／猶太文化史 150／論神性 121／暗網 14，
  並排在每日排程的模型前面。F 型 PDF 多為無文字層掃描，不做。
  未解：《奧德賽,伊利亞特,薩迦,艾達》e71cb862——JSONL 是**簡體**，只配到 54／3,366 且不守恆，要先轉繁再處理。
- **③ 部分**：「未判讀」144 本 → 129 本重建上線（抽 3 本看過，多為無章節模式）、15 本被擋（多為 NO_TOC）；
  「有對照欄」52 本 → `number_multilingual.py --apply` 50 本寫回、2 本略過（民主妙法已有段號、Gregory of Nyssa 守恆失敗）。
  `output/restructure/unrestructured.tsv` 尚未重產，裡面這 179 本的狀態是舊的。剩：稽核旗標 212、章名不連續 179、章內段落過少 79…（重 OCR／reflow 分流）。

## 坑（這幾天實際踩過）
- 🚨 **(N) 起頭不是註腳**：只有分隔線後才是註釋（見上）。改結構的規則一定抽樣用眼睛看。
- 🚨 **守恆量尺會誤報**：HTML 表格標籤字母、`<[^>]+>` 跨塊誤刪、段號在 `(1)` 前導致行首 (N) 沒被剔除——三次都是量尺壞不是真丟字；
  `repaginate.py` 只准多 ≤50 字。
- 🚨 `pages[-2] += pages.pop()` 會蓋掉前一頁（-2 在 pop 前就算好位置）。
- 🚨 **PyMuPDF 零碎讀 Drive 上的 PDF 會卡死**（CPU 不動、無網路連線）：先 `shutil.copyfile` 到本機再讀，每本子行程加逾時。
- 🚨 **Drive 會自己重掛**（10-01 03:09）：G: 消失幾分鐘，整條接力讀不到檔空轉；接力腳本每步前先確認 G: 在。
- 🚨 Bash 的 `run_in_background` 有時間上限（約 30 分鐘會被砍）：長批次用 PowerShell `Start-Process`；盯進度的等待器每次 ≤15 分鐘。
- 🚨 Bash heredoc 吃反斜線：含 `\d`、`\n` 的 Python 用 Write／Edit 工具寫，不要用 `<<'EOF'`。
- 推 R2 偶爾斷線：檔已換上但沒推上去，重跑會判「不用改」而不補推——要記下 ERR 的 id 手動補推（`se.push_to_r2`＋`se.update_db`）。
- R2 用量 3.75／10 GB；書內插圖使用者定只存 Drive，**任何圖片衍生物別往 R2 推**。
- 多 session 共用 working tree：commit 只 add 自己改的檔；push 常被別的 session 搶先 reject，確認自己的 commit 已在 origin/master 即可。
