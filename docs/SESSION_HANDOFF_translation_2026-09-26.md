# 交接：譯文修正、原文中譯對照、補譯（2026-09-26）

接手前先讀：CLAUDE.md、記憶 `project_translation_audit_2026_09_25.md`、`feedback_save_claude_usage.md`、
`.claude/skills/ebook-translate/SKILL.md` 開頭政策區、`.claude/skills/ebook-collected-works/SKILL.md` 的 align_reference 一節。

## 原則（使用者定的）
- **節省 Claude 用量是最高政策**：能跑腳本就不派 agent；翻譯／補譯一律交 Gemini→NVIDIA 引擎或 fleet lane；
  非派不可時用 `model: sonnet`、一次一個、prompt 要求只看統計、回報簡短。同時最多 3 個 agent。
- 長跑工作用**獨立隱藏程序**（`Start-Process ... -WindowStyle Hidden`）或 fleet_keeper lane，session 結束不會斷。
- 不准改電源／闔蓋設定。所有中文繁體。commit 只 add 自己改的檔，push 後比對 SHA。

## 正在背景跑的（不耗 Claude）
| 項目 | 怎麼看進度 |
|---|---|
| 涂爾幹《宗教生活的基本形式（英繁對照）》補註：註文少 15 條、正文註號少 291 處，`scripts/fix_durkheim_notes.py --apply → --push → --verify` | `scripts/logs/durkheim_notes_2026-09-26.log`（UTF-16，結尾 ALL DONE）；完成後 `fix_durkheim_notes.py` 還沒 commit，要提交 |
| 研究回顧補譯 lane `litreview-retrans`（3,643 段拒答清空後補譯） | `scripts/logs/fleet_litreview-retrans.out.log` |
| 教父英文段補譯：排程 KGL_Fathers_Retranslate（已開，時限 PT10M） | 排程＋`fathers_retranslate_untranslated.py --scan` |
| 一般譯書／全集／東方聖書補譯：`output/translation_fix/retrans_{cleared,books,untrans}.ps1` 接力 | `scripts/logs/retrans_*_2026-09-25.log` 結尾 ALL DONE |
| 圖書館 MinerU OCR lane `mineru-queue`（272 本掃描書回補） | `scripts/logs/fleet_mineru-queue.out.log` |

## 待辦（依優先）
1. **原文中譯配對要加內容驗證**：`output/reverse_originals/batch_dryrun.tsv`（1,002 對乾跑結果）證明
   `align_reference.py` 的「對上率」只反映結構相似，**不能判斷是否同一本書**：中文配中文（《神護理的奧秘》多版本）與
   明顯錯配（《基督教思想史》↔ Simon Peter…）都拿到 100%。要加兩道檢查再重篩：①原文側確實是外文；
   ②抽配到的段落比對人名、數字、經文出處是否對應（不呼叫引擎）。只有通過的才 `--apply`，其餘列清單給使用者。
   另外 `--samples 0` 會除以零，要修。
2. **17 本公版原文下載**：`output/reverse_originals/shortlist_20.tsv` 已查證開放來源（古騰堡、archive.org、CCEL、vatican.va）。
3. 等所有補譯跑完，**再跑一次 `output/translation_fix/unify_names.py --apply`**（新譯段可能又冒出保祿等）；
   教父 `9edb7c37-…` 當時跳過，要補。
4. 翻譯詞庫的「脈絡待定」33 本、DB 語料的譯名、7 組以外的譯名、領域詞彙候選（修道院／日本／印度用語）都還沒做。
5. 館藏 29 對「中譯重複版本」（`output/untranslated_inventory/pairs_v2.tsv`）要不要合併，待使用者決定。
6. 全集 `sec*.json` 的修改（修正工具＋各 lane）都還沒 commit，網站已由 driver 重建；**不可 git add 整批撈**。

## 已完成（這兩天）
- 全站確定性修正（中間點、隻→只、字形、引號、章名分行、大數）、拒答清空、U+FFFD 剝字元、「未譯」判準收緊。
- 譯名依脈絡統一（教父＋ACCS 用新教寫法；亞里斯多德、佛洛伊德、俄利根）；詞庫補彼得／摩西／以賽亞。
- 《迴旋梯：掙脫幽暗的攀爬之路》全書譯完並校對（天主教用語）；前作定名《開闖世界》；刪除清單在 ebook-translate SKILL.md。
- 布迪厄〈宗教場域的生成與結構〉（研究回顧 5136）全文 169 段已翻（先確認 `lit_review_sections` 有 zh）。
- 課程三本 OCR（玄奘\博一上\上課\宗教學理論與方法(一)\ 三份「（OCR）.docx」）。
- 原文中譯對照工具 `scripts/align_reference.py`（試做《宗教經驗種種》《神聖的帷幕》已寫入）。
