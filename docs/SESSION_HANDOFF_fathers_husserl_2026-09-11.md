# 交接：教父三欄／胡塞爾《觀念一》／西方現象學簡史（2026-09-11）

這一輪做完的與沒做完的。**「沒做完」那幾項每一項都附了卡在哪裡**，不要從頭重查。

---

## 0. 正在跑的排程

| 排程 | 狀態 | 判準 |
|---|---|---|
| `KGL_Husserl_OCR` | ✅ **已完成並自我停用**（59/59 批） | — |
| `KGL_Fathers_Retranslate` | 🔄 進行中，**剩 1,666 段**（2026-09-12 08:05 量） | `python scripts/fathers_retranslate_untranslated.py --count` |

補譯跑完會自己 Disable。**完工判準看 `--count` 的輸出，不要看排程狀態。**

**2026-09-12 複查**：08:05 量到 1,666、08:52 量到 1,654，worker 活著（00:24 由 keeper 拉起）。
所以是有在前進，但**每小時只補得動十幾段**，照這個速度還要四天以上。瓶頸在引擎不在排程
（`scripts/logs/fathers_retranslate_run.log.err`）：

- Gemini **七把 key 全數 429**，已觸發「連兩次耗盡 → 改走 NVIDIA-only 六小時」（14:07 才回頭試）
- NVIDIA 這側 503 輪換之外，還大量被**輸出閘退件**（`reasoning-leak`／`untranslated` 各三連退）

退件是對的（壞輸出不該入庫），但也代表**這批剩下的段落特別難**——引擎一再交出推理外洩或
整段回抄。下一個人要加速，方向是換引擎或分批降難度，不是重開排程。
🚨 判準永遠是 `--count` 的數字有沒有動，不是排程狀態、也不是 pid 還在不在。

---

## 1. 胡塞爾《觀念一》——✅ 2026-09-12 切章修完，已開翻

**做完了**（原本列的五處是四處實有、一處只講到一半，另外自己又抓出兩處）：

| 原列 | 結果 |
|---|---|
| ① 目次被當成章 | ✅ `strip_toc`。目次區塊自「CONTENTS」起、收在最後一個帶頁碼的條目——多吃一行就會把正文的 `## INTRODUCTION` 也吃掉 |
| ② `sec26` 標題黏一串 | ✅ `split_glued`＋`split_head_from_body`。全書只有 7 行有行內 `##`，但其中一行黏了四件事 |
| ③ `sec24` 頁碼 `p4–111` | ✅ 先 `repair_folios` 再 `fill_folios`。⚠️ 頁數太少時 repair 會把僅有的頁碼也清掉，設了下限 |
| ④ 第三部分缺 `SECOND CHAPTER` | ✅ 而且**是兩處不是一處**：第二部分的 `FOURTH CHAPTER`(p171) 也被吞了。根因是系統性的——章首頁沒有書眉，prompt 卻叫模型丟掉最上面那一行。補的字取自本書目次 |
| ⑤ 略過 `INDEX TO PROPER NAMES` | ✅ 但**真正的大宗是 p429 起的 `ANALYTICAL INDEX`（616 段）**，它被併在最後一章裡（`## ANALYTICAL INDEX` 不以 INDEX 起頭，切章規則抓不到）。改成由目次宣告的索引起始頁去砍 |
| — | 🚨 **新抓到：印刷頁 176–177 被拍了兩次**，OCR 各轉錄一次。兩張照片像素不同所以雜湊比不出來；不去重站上就有整整兩頁重複 |
| — | 🚨 **新抓到：b0145 整批「一頁一段」**，段落界線在 OCR 那一步就沒了。加了 `looks_page_collapsed` 閘門並重跑該批，比對確認新的比舊的對（舊版把 `appearance-patterns` 讀成 `experience-patterns`） |

現況：**21 節／正文 1,547 段／註腳 119／頁碼 100%／目次對帳 20 項全 ✓**，
正文自 `INTRODUCTION`(p41) 起，13 章＝Ideen I 四部分的 2+4+4+3。
章名不交給引擎翻（四個「FIRST CHAPTER」會變成四個「第一章」），寫死在 `TITLES_ZH`。

翻譯掛在 `fleet_keeper.ps1` 的 `husserl` lane（backend auto＝Gemini→NVIDIA，**不可用 haiku**）。
複驗指令：`python scripts/husserl_build.py --dry`（末段是目次對帳）／`--gates`（逐批複驗）。

<details><summary>原始交辦內容（保留備查）</summary>

## 1-原. 胡塞爾《觀念一》——OCR 完成，切章有五處要修（下一步的第一件事）

OCR 成果：**472 頁 / 正文 2,373 段 / 註腳 117 條 / 有頁碼 100%**。
`python scripts/husserl_build.py --dry` 看得到目前的切章。

🚨 **翻譯之前一定要先修這五處**，否則會把目錄當正文翻、把索引也翻一遍：

1. **`sec2`–`sec18` 其實是目錄**，不是章。它們全落在印刷頁 **p35–40**，
   每個「章」有 8–33 段，那是目次在列 § 標題。真正的正文從 `sec19 INTRODUCTION`
   （p41）與 `sec20 FIRST SECTION`（p49）才開始。
   → 判準可用「連續多個 section 的頁碼都在同一小段範圍內且早於 INTRODUCTION」。
2. **`sec26` 的標題黏成一串**：`THIRD CHAPTER## THE REGION OF PURE CONSCIOUSNESS## § 47. THE`。
   `split_sections` 取 heading 時沒有在第二個 `##` 斷開。
3. **`sec24` 的頁碼範圍是 `p4–111`**——`p4` 是 OCR 把 `101` 之類讀錯。
   `fill_folios` 補不到它（它有值，只是值錯了）。可沿用
   `archive_djvu.repair_folios` 那套「與前後鄰居對不上就打掉」的作法。
4. **第三部分缺 `SECOND CHAPTER`**（sec28 FIRST → sec29 THIRD）。要查是 OCR 漏了
   標題還是那一章真的被併進前一章。
5. **`sec35 INDEX TO PROPER NAMES` 要略過**——依既定政策，只有 Index 可略
   （`[[feedback_transcribe_notes_and_bibliography]]`）。

修完才跑：`python scripts/uchimura_auto.py --author husserl --run-queue`
（husserl 已註冊進那支驅動；store 那筆《觀念一》已是 `in-progress` 並掛好 ebookId
`d0000000-0000-4000-8000-000000000021`）。

</details>

---

## 2. 教父補拉丁原典——卡在 `cc_letter_spans` 的一行判準

**不是找不到原文。** Corpus Corporum（mlat.uzh.ch）有整套 Migne PL 的機讀 TEI。

`python scripts/fathers_alignability.py` 排出來最該做的是
**奧古斯丁《懺悔錄與書信》**（`9edb7c37`，526 段只有 6%，88 部可對齊），缺的是**書信集**。

🚨 **現成的 `cc-letter` 模式吃不下它**：`cc_letter_spans()`（`fathers_add_original.py`）
要求信號所在的段 **chunk_index 連續**——

```python
if run and no is not None and no > run[-1][1] and idx == run[-1][0] + 1:
```

耶柔米那一冊一封信剛好一段所以成立（目前 100% 命中）；奧古斯丁**一封信橫跨好幾段**，
實測讀得出信號的 97 段，index 是 `3,4,5,13,14,16,17,19,21,23,25,28,43,45,50…`，
最長連續串很短，等於配不上。

**做法（順序不可換）**：
1. 先補測試鎖住耶柔米現況（`d229a6d4` 目前的命中數），再動那個判準
2. 把「連續」放寬成「單調遞增且中間沒有別的信號」
3. 跑奧古斯丁書信、**兩冊都要重驗**

---

## 3. 教父其餘尾巴（依嚴重度）

| 項 | 量 | 卡在哪 |
|---|---|---|
| 真的缺英文欄 | **586 段** | 集中在優西比烏 139／特土良 106／希拉里 97／耶柔米 54。要從來源 EPUB 撈回來 |
| 居普良《論述集》整塊拉丁 | 3 段 | 🚨 **路徑錯配**：spec 的 markers（`論文三`／`第四篇`…）確實存在但落在 **#296–349**，而帶「居普良 論述集」路徑的段是 **#103–137**。而且它的拉丁一個錨點都沒有（無頁碼、無節號）所以也切不動 |
| 希拉里卷一原典 | 0/40 | 對齊器**安全拒收**（錨點被切成兩塊、與 spec 宣告的一塊不符）。是正確拒絕，不是配錯 |
| 路徑仍認不出 | 希拉里 18 段／教會史 3 段 | 沒有可比對的標題，**故意不猜** |
| 註腳仍是英文 | 148 段 | 正文譯了、註腳沒譯 |
| 拒譯污染 | 86 段 | 「我注意到您提供的…」那類 |
| 夾簡體 | 10 段 | |
| ACCS 兩卷第三欄 | 0% | 耶利米書、次經 |

稽核指令：
```
python scripts/audit_fathers_coverage.py                  # 填充率＋中譯品質
npx vite-node -c scripts/audit.vite.config.mjs scripts/audit_fathers_columns.mjs   # 對齊
EBOOK_CHUNKS_DIR="C:/nonexistent" npx vite-node -c … audit_fathers_columns.mjs     # 強制驗 R2
```
🚨 **本機與 R2 兩邊都要驗**。只讀 R2 會量到過期的；只讀本機會漏掉「線上還沒更新」。
改完 JSONL 要 `python scripts/upload_chunks_to_r2.py upload --id <id> --force`。

---

## 3b. 🚨 譯文落地閘（另一條線當天加的，我已接上補譯）

`scripts/translate_ebook_to_zh.py` 新增了 `unusable_reason(text, source)`
（見 `[[feedback_translation_output_gate]]`）。原本唯一的守門員
`_looks_like_prompt_echo` **只認中文提示詞**，驗的是「模型有沒有照我預期的方式失敗」，
所以模型改用英文外洩推理就整個穿過去——豪斯評傳因此存進 22,590 字的 deepseek
思考過程並且上線。

`fathers_retranslate_untranslated.py` 已接上這道閘（壞輸出重試／換引擎，
**絕不退回英文原文**）。

拿這道閘掃全 `/fathers` 13,173 段的結果：

| 原因 | 段數 | 說明 |
|---|---|---|
| `untranslated` | 1,414 | 補譯正在處理的那批 |
| `partial-untranslated` | 179 | **我的判準漏掉的一類**：半中半英。要逐筆看，其中有些像是誤報（整段其實是中文、只有註腳是拉丁書目） |
| `self-talk` | **136** | **既有污染**，不是補譯造成的。我自己的 meta regex 只抓到 86，這道閘多抓 50 |
| `degenerate-repetition` | 1 | |

掃描腳本：把 `unusable_reason` 套在每段 `content` 上即可（本輪用的是暫存腳本，
要常用的話值得收進 `audit_fathers_coverage.py` 當一欄）。

---

## 4. 《西方現象學簡史》——計畫寫好，正文一字未寫

`/works` slug `western-phenomenology-history`，🚨 **計畫全文只在 DB `content_json`，
grep repo 找不到**。七部 22 章＋跋。

- **12 位 hub 只有骨架**（馬里翁／亨利／克雷提安／拉考斯特／舍勒／布倫塔諾／英加登／
  施泰因／芬克／呂格爾／馬塞爾／舒茨），一卷都還沒轉錄
- **奧托《論「聖」》還沒轉錄**——`scripts/archive_djvu.py` 就是為它做的（38 例測試，
  1924 刷實測頁碼 94%、跳號 0），但後來改成胡塞爾優先，那本只做到解析層
- **范德列烏要另找來源**：archive.org 那份是借閱限制（`access-restricted-item: true`）
- 公有領域可直接動的四位：胡塞爾（進行中）／奧托／范德列烏／西田幾多郎

建議先寫的三章（決定全書立場能不能站住）：第 5 章本質直觀、第 12 章列維納斯、
第 16 章賈尼柯的控訴。

---

## 5. 這一輪學到、別再踩的

- **要問「頁面呈現對不對」就跑呈現頁面的那支函式**，不要在外面重寫一套判準。
  第一版在 Python 端近似 `alignByAnchors`，19 本全紅——判準錯不是資料錯。
- **判「譯了沒」要先切掉註腳**。教父卷的註腳大量是原樣保留的英文書目，連同正文
  一起算漢字率，正文譯好的段也會被判成未譯（2,075 → 1,675）。
- **清理不該順手把內容弄丟**。居普良那批被清空後測試立刻轉紅，測試是對的。
- **heredoc 會吃掉一層反斜線**。這一輪被咬了四次（`\n` 變真換行寫出 SyntaxError、
  `\f` 讓 ps1 的路徑變成 `scriptsathers_...py`）。寫檔一律用 Write 工具。
- **`G:` 報找不到先看 Drive 卡住沒**，不是沒掛載（CLAUDE.md 有一行修法）。
- **R2 沒有空間不足**（2.02/10 GB），而且不能拿掉——正式站在 Zeabur 讀不到 G:。
