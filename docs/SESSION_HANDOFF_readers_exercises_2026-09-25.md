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

## 二、待做：自撰練習題重寫

四語各一個 agent 已把**每一句**自撰題逐句覆核，報告在
`output/qa/original-readers/exercise-grammar-review-2026-09-25/{hebrew,greek,latin,japanese}.{json,md}`
（本機，`output/qa/` 不進版控——**先備份到 Drive 研究資料夾或貼進 git 白名單再動手**）。
每句有 `verdict`（ok／minor／severe）、`issues`、`fix`（多數已跑過 `compose_*_sentences.py --check`，
結果在 `fixGate`）、`fixNote`。

| 語言 | 句數 | ok | minor | severe | 結論 |
|---|---:|---:|---:|---:|---|
| 希伯來 | 369 | 290 | 71 | 8 | **逐句修**，沒有一課整組壞；第 1–12 課可視為定稿 |
| 拉丁 | 720 | 114 | 202 | 404 | 第一冊 1–18 課逐句套 fix；**其餘 82 課整組重寫** |
| 日文 | 701 | 237 | 182 | 282 | 第 1–15 課逐句修；**第 16–100 課整批重寫**，先清詞表 |
| 希臘 | 703 | （見 greek.md） | | | |

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
5. 希伯來特有：21 句「וְ＋qatal」當過去連續要換 wayyiqtol／X-qatal（修正句已過閘）；
   替換時注意 31#7、40#5、40#9 把生詞挪走要另補句；5#7 片語 `עַל־דְּבַר` 帳錯；
   第 42 課 טַף 詞義「家族」應為「孩童」。

重寫後照舊：`validate_reader_exercises.py` → 四支 builder → `render_and_check_reader_pdfs.py`
→ `audit_printed_exercises.py {heb|grc|lat|ja}` → `inspect_reader_pages.py` →
`qa_reader_rendered_pages.py` → `build_reader_spines.py` → `sync_reader_artifacts.py --write`。
🚨 同一 session 最多三個 agent（使用者這次特准四個，不是常態）。
🚨 版面又改了，`reader_page_budget.py` 的係數要重量（`fit_reader_reading_limit.py`）。
