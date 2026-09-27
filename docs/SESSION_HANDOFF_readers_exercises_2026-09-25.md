# 交接：原文讀本第二輪版面 ✅ 與自撰練習題重寫（2026-09-25）

給下一個 session。先讀 `skills/build-original-language-reader/SKILL.md` 與
`references/layout-web-audio.md` 開頭兩節（2026-09-25 的兩輪裁示），再讀
`references/exercise-sets.md`。記憶 `feedback_reader_layout_2026_09_25`。

## 一、已完成（不用再碰）

版面第二輪已重出、稽核全綠、Drive 三邊 SHA1 一致，commit `d0add261`：
七冊 2,407 頁（希伯來單冊 384、希臘 319／465、拉丁 349／326、日文 281／283）；
讀本一段原文一段中譯（不印逐詞層）、行距 1.8、中譯標楷體；十題練習一頁、一條 8.5mm
作答線；冊名只寫一二三；Times New Roman；封面不印規格行；凡例不印發音／著作權段；
舊 PDF 直接刪；Drive 印刷母版分 讀本／單字卡／撲克牌。

Quizlet 匯入檔都在 Drive `語言\原文讀本\單字卡\Quizlet匯入\`：十二副印刷卡對應的
TSV（含希伯來）＋英文托福 B2–C2 六千字（240 課，`scripts/export_quizlet_english_b2c2.py`）。

殘留（可不理）：19 頁「最後一個短單元自己落到下一頁」的孤兒頁；拉丁第一冊附錄
第 232 頁一個 U+0001 的 Segoe UI 空字形；`qa_hebrew_full_reader` 預設路徑仍是單冊 stem。

## 一之二、翻譯定名已回寫

校對的譯名回饋 30 條已進 /translation-glossary（`scripts/seed_glossary_readers_2026_09_25.py`），
次經人名書名思高／和修分歧待使用者定奪（見 translation-glossary SKILL.md 2026-09-25 節）。

## 二、待做：自撰練習題重寫

四語各一個 agent 已把**每一句**自撰題逐句覆核，報告在
`output/qa/original-readers/exercise-grammar-review-2026-09-25/{hebrew,greek,latin,japanese}.{json,md}`
（本機，`output/qa/` 不進版控；四份都已備份到 Drive `語言\原文讀本\工作母版\練習題文法覆核-2026-09-25\`）。
每句有 `verdict`（ok／minor／severe）、`issues`、`fix`（多數已跑過 `compose_*_sentences.py --check`，
結果在 `fixGate`）、`fixNote`。

| 語言 | 句數 | ok | minor | severe | 結論 |
|---|---:|---:|---:|---:|---|
| 希伯來 | 369 | 290 | 71 | 8 | **逐句修**，沒有一課整組壞；第 1–12 課可視為定稿 |
| 拉丁 | 720 | 114 | 202 | 404 | 第一冊 1–18 課逐句套 fix；**其餘 82 課整組重寫** |
| 日文 | 701 | 237 | 182 | 282 | 第 1–15 課逐句修；**第 16–100 課整批重寫**，先清詞表 |
| 希臘 | 703 | 100 | 171 | 432 | **第二冊 1–38 課整組重寫**（ok 僅 7%）；第一冊與第二冊 39–50 課逐句修；第一課無動詞無冠詞，建議第一課就教 ἐστίν |

三本的病是同一種**生成邏輯**，不是個別句子：把本課生詞串起來（拉丁「動詞 et 動詞」、
日文「AとBとCです」、希臘詞堆），機械閘（詞形在語料、詞已教、二十詞覆蓋）全部放行。
重寫前要先改規格與閘，否則重寫一次還是同樣的東西：

1. **每句先定句型再選詞**：一句一個限定動詞（或名詞句一個述語）；二十詞覆蓋不必硬湊，
   湊不到的詞讓它出現在引用題或下一課。
2. **閘加「有述語」與「兩動詞須共主詞」**；拉丁閘要驗「詞形屬於這個標題詞」（現在只驗
   語料有這個形：fugerem≠fugō、triumphabit≠triumphus，13 句放行）；日文閘要擋
   「副詞／接續詞／助詞／量詞直接接です」與「と 並列超過兩項」。
3. **語域**：日文自撰題幾乎全不在宗教學語域（詞表就是《大家的日本語》），這是規格層的
   決定，要問擁有者要不要放寬；拉丁三句語域不當已列出。
4. **正字法**：拉丁全書 æ/œ/j 體例，語料形照印會混進 ae／i 與隨機大寫，重寫時統一。
5. 希臘特有：約 250 句沒有謂語；閘加「至少一個限定動詞」「δέ／γάρ／οὖν 不在句首」
   「ἵνα／ὅπως／ἐάν／ὅταν／μήποτε 後必有假設語氣」三條可擋六成 severe；詞表 8 處 lemma／
   配格錯（σύν、ἀνά、ἅπτω、ιν、χράω、συνόχωκα、τροπέω、ἀπαλλαξείω），διάψαλμα 剔出自撰詞池。
6. 希伯來特有：21 句「וְ＋qatal」當過去連續要換 wayyiqtol／X-qatal（修正句已過閘）；
   替換時注意 31#7、40#5、40#9 把生詞挪走要另補句；5#7 片語 `עַל־דְּבַר` 帳錯；
   第 42 課 טַף 詞義「家族」應為「孩童」。

重寫後照舊：`validate_reader_exercises.py` → 四支 builder → `render_and_check_reader_pdfs.py`
→ `audit_printed_exercises.py {heb|grc|lat|ja}` → `inspect_reader_pages.py` →
`qa_reader_rendered_pages.py` → `build_reader_spines.py` → `sync_reader_artifacts.py --write`。
🚨 同一 session 最多三個 agent（使用者這次特准四個，不是常態）。
🚨 版面又改了，`reader_page_budget.py` 的係數要重量（`fit_reader_reading_limit.py`）。

## 三、2026-09-27 收尾：練習題重寫與內容校對殘項 ✅

四語都做完、七冊與十一副單字卡重出、稽核全綠（只剩已知孤兒頁）、Drive PDF 已同步（Drive 上的 .docx 未覆蓋，照 CLAUDE.md 規矩）。
頁數：希伯來 422、希臘 367／464、拉丁 339／325、日文 285／286。

- **練習題**：希伯來 79 句、希臘 603 句、日文 464＋25 句（と 三項以上並列）逐句換掉；拉丁上冊 19–50、下冊 1–50 共 574 句**手寫重寫**。
  四支 `compose_*_sentences.py` 都加了句型閘（有述語／限定動詞、δέ・γάρ・οὖν 不在句首、ἵνα 等後須假設語氣、標題詞與詞形相符、
  拉丁正字法 æ/œ/j、日文 と 並列上限、副詞助詞不直接接です），只套自撰題，引用題不套（套了會誤殺 58/300 句真語料）。
- 🚨 **拉丁第一次重寫用「規則式產生器」→ 閘全綠但是新型詞沙拉**（`Dominus testem crēscit`、`Ignis lacrimæ est`「火與淚相關」、中譯夾拉丁字）。
  產生器版備份在 `latin-full/_prev-generator-2026-09-27/`（本機）。**自撰句禁止模板產生**；驗收一定要自己抽樣讀，不能信 agent 說「逐句讀過」。
- **內容校對**（逐條狀態在 `output/qa/original-readers/content-review-2026-09-23/status-{hebrew,greek,latin,japanese}.json`，本機）：
  希伯來 fixed 73／pending 16；希臘 fixed 167／pending 238（大宗是逐詞層，紙本不印）；拉丁 fixed 115＋already 36／逐詞層 56／pending 100；
  日文 pending 6。日文另有 179＋41 段文言譯文改白話（聖經文語譯引文、詩篇標題、信經、和歌照規矩不動）。
- 🚨 原文欄位（printedEntry／forms）不可放中文：希臘 5 條、拉丁 2 條曾印出「（簡單過去時）」「（不變格）」→ LibreOffice 退回 NotoSansJP 未內嵌。改用 aor./gen./indecl.。
- 🚨 詞表 headword 一改（αιλαμ→Αἰλάμ、edo→ēdō…）必須重跑 assemble，否則 builder 報「兩邊對的不是同一個詞」。

**待使用者定奪**：希伯來稱上帝 你／祢／您 與 אֲדֹנָי 五種譯法；次經書名思高／和修（希臘讀本已依課題用思高名）；日文語域要不要放寬出《大家的日本語》；
拉丁 operō／operor 重複；日文詞表 na 形容詞別名鍵與「いい」詞條。
**未做**：希臘／拉丁逐詞層（線上）殘錯、拉丁 -que 接回後逐詞層要重跑 `build_latin_interlinear.py`、日文 50 段逐詞層留白（別用 Haiku）、
拉丁 Trent 書目段與分節錯位三處、希臘禮儀附錄 永貞／童貞 等用字統一、部分課生詞覆蓋 16–19/20。

- 🚨 **重寫後生詞覆蓋退步 312 詞**（validate 當時只要求 50%，只有線上讀本 vitest 擋下）。已補回：希伯來、日文、希臘兩冊 0 缺；拉丁只剩語料零字形（notAttested）與 v1 第 50 課 nōlī/nōlite
  （片語要求單複數命令式同句，必撞人稱閘，要改詞條或 credit_keys 判準）。`validate_reader_exercises.py` 現在對希伯來／日文硬擋未全覆蓋，希臘／拉丁印缺詞清單不擋。
  **改練習題後一定要跑 `npx vitest run test/original-readers.spec.ts test/japanese-full-reader.spec.ts`。**
