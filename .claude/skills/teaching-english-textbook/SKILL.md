---
name: teaching-english-textbook
description: 媽媽（julia5868）家教用的《Happy English 快樂學英語》B5 紙本課本 —— 50 課 × 20 字、跟 1000 張印刷單字卡同一套分課，每課含學習目標／課文／單字（帶圖）／文法／例句對話／練習（選擇 10、填空 10、重組 6、造句 8）／解答，出成上下兩冊 docx＋PDF 放 Drive 家教夾。課程內容由 LLM 逐課生成並過品質閘，版面走 python-docx。Use when 要重出課本、改課數或每課字數、改題型或題數、調版面、補生成失敗的課、或使用者說「英語課本」「家教講義」「Happy English」。網站 /english 用同一份課程資料（scripts/english_site_from_course50.py 轉出）見 [[project_english_learning]]；單字卡見 [[original-reader-flashcards]]。
---

# 國小英語課本（Happy English）

> 分課詞表：[data/originalReaders/vocabulary/english-1000.json](../../../data/originalReaders/vocabulary/english-1000.json)（50 課 × 20 字，人工校過；2026-09-16 依難易重排）
> **文法大綱**：[data/english/course50-syllabus.json](../../../data/english/course50-syllabus.json)（一課一個文法點，50 個全相異）
> 重排單字：[scripts/reorder_english_vocab.py](../../../scripts/reorder_english_vocab.py)
> 課程資料：[public/content/english/course50/](../../../public/content/english/course50/)　`L01.json` … `L50.json`
> 生成：[scripts/build_english_course50.py](../../../scripts/build_english_course50.py)
> 排版：[scripts/build_english_textbook.py](../../../scripts/build_english_textbook.py)
> 成品：Drive `玄奘/博一上/家教/國小英語課本/`（**不進版控**）

## 三份東西不要搞混

同一批一千字，有三個成品，分課方式不同：

| 成品 | 分課 | 位置 |
|---|---|---|
| **紙本課本**（本 skill） | 50 課 × 20 字 | Drive `玄奘/博一上/家教/國小英語課本/` |
| 印刷單字卡 | 50 課 × 20 字 | `output/print-masters/english-flashcards-1000.pdf` |
| 網站 `/english` | 50 課 × 20 字 | `public/content/english/lessons.json` |

2026-09-08 起三份**分課一致**，網站內容由同一份 course50 轉出：

```bash
python scripts/english_site_from_course50.py     # course50 -> 網站 lessons.json
```

改了 course50 就要重跑這支，否則網站還是舊的。網站的 emoji 也在這支裡處理——
讀單字卡人工校過的對照表（749/1000 有 OpenMoji 碼位），**不要再拿英文名去猜**，
課本與網站原本那批 order→獅子、summer→啤酒就是猜出來的。

🚨 **主題圖示不可以從 `lessons.json` 讀回來**。原本 `theme_emojis()` 是拿舊檔的
`title_en` 當鍵去查，但這支腳本自己就會覆寫 `lessons.json`——課名一改下次就對不到，
每重出一次掉更多圖示，而且只印一行「缺主題圖示的課」不當錯誤。2026-09-17 重出
50 課之後 35 課沒有圖示。二十個主題是穩定的，碼位寫死在 `THEME_EMOJI`，
查詢用 `lesson.theme` 不是課名。

網站那邊還有兩個地方跟課數綁著：`pages/english/index.vue` 的 `LESSON_COUNT`
（段考每 5 課一組，會自己長出 10 組）與 `pages/english/review/[range].vue` 的
總複習上限。測驗題庫走 `utils/englishQuiz.ts`，靠 exercises 的 `type` 挑題
（`choice` 出文法題，`fill`／`unscramble`／`translate` 出打字題）。

## 成品放哪裡

🚨 **不要放 `知識圖工作室/教學/`**（我第一次就放錯了）。使用者的家教材料在
`玄奘/博一上/家教/`，**按學生分**、由該夾的 `家教說明.md` 登記，那是上課實際帶的東西；
`知識圖工作室/教學/` 是素材庫（例如私中數學的題庫）。課本與 `國小英語單字卡/` 並排放
`國小英語課本/`。新增或改版後記得同步 `家教說明.md`。

## 出書

```bash
GEN="C:/Users/user/AppData/Local/Python/bin/python.exe"          # 有 requests
PDF="C:/Users/user/AppData/Local/Microsoft/WindowsApps/python.exe" # 有 pywin32

"$GEN" -u scripts/build_english_course50.py            # 生成沒做過的課
"$GEN" -u scripts/build_english_course50.py --check    # 只驗現有產出
"$GEN" -u scripts/build_english_course50.py --fix      # 修重組題題幹、去重選擇題、洗選項
"$PDF" -u scripts/build_english_textbook.py --split --publish   # 出上下兩冊 + PDF + 送 Drive
```

🚨 **出書那支要換另一個解譯器**。`to_pdf()` 走 Word COM（`scripts/office_to_pdf.py`
`import pythoncom`），而生成用的 `AppData/Local/Python` 那支沒裝 pywin32——
docx 會正常寫出來，**轉 PDF 那一步才炸**，等於整本排完才失敗。
`WindowsApps/python.exe` 三個套件（python-docx／PIL／pywin32）都有。

🚨 **一定要寫明解譯器路徑**。背景跑的時候裸 `python` 會解析到 `_whisper_venv`，
那支沒有 `requests`，而且**不會報錯**——程序活著、CPU 0、記憶體 4.6MB，卡在 import。
從外面看跟「模型很慢」一模一樣，我在這上面白等了五分鐘才用
`Get-CimInstance Win32_Process` 看出來是 `_whisper_venv\Scripts\python.exe`。
另外加 `-u`，不然背景工作的 log 會整段被緩衝住看不到進度。

生成很慢（一課 6–15 分鐘），要並行就開幾條 `--range 20-29`，逐課寫檔可續跑。

## 定案的規格

- **B5**（JIS 18.2×25.7cm）、英文 ≥13pt、中文 ≥12pt、**不要 KK 音標**
- 課內不硬插分頁（換下一課才換頁），課文排在單字前
- 每課練習：選擇 10、填空 10、重組 6、造句 8
- **超過 300 頁分上下兩冊**
- 配圖用單字卡那份人工校過的 `english-card-images.json`，紙本 500/500 全中
  （網站走 OpenMoji 碼位，749/1000）

**一課的順序**：學習目標 → 課文（故事）→ 單字 → 文法 → 情境對話 → 練習 → 解答。
2026-09-17 砍掉原本夾在文法與練習之間的「例句」八句：使用者翻紙本的第一個反應是
「課文似乎有點多？**為何單字之前和之後都有課文**」。一課原本有四段英中對照共 27 句
（課文 9.4／文法例句 4.2／例句 8.0／對話 5.5），那八句「例句」沒有情節也沒有說話人，
版面上就是一串編號的英中對照，跟課文長得一模一樣。砍掉之後單字後面只剩「文法」
（有表格）與「情境對話」（有說話人），兩者都有明確身分，一課 27→19 句。
**課程資料仍保留 `sentences`**，網站 `/english` 有自己的版面在用。

`MCQ_PER_LESSON` 在排版腳本裡。早期那批資料檔存 30 題、出書時分層挑 10 題；
2026-09-17 重出之後一課就是 10 題，`pick_mcq` 直接全收。

## 這批材料特有的「看起來成功的失敗」

結構檢查全綠不代表東西是對的。踩過這十九個：1–5 是最早那批，6–10 是 2026-09-16
使用者翻紙本才發現的（每一個當時都通過了所有自動檢查），11–19 是加了閘之後才長出來的。

1. **覆蓋率是我自己量錯的**。詞表把複數寫成 `apple(s)`、`peach(es)`、`mango(es)`，
   比對只切 `/` 和 `、` 的話永遠對不到課文裡的 apple／peaches。L19 因此被判成
   覆蓋率 35%、白白整課重做兩次，其實課文一直是好的。改東西前先確認**壞的是尺規還是東西**。
2. **課文沒用到本課的字**。覆蓋率原本只印出來看不擋，於是漏字的課照樣落地。
   現在低於 80% 會整課重做（`MIN_COVERAGE`）。
3. **例句區照抄上方文法例句**。L01 曾經八句全中，等於整區白放。排版時會去重，
   提示也加了禁止重複，但仍有 11 課各重 1–2 句（去重後都還有 5 句以上）。
4. **十題選擇題長得一模一樣**。第二批（文法選填）特別容易整批只換主詞，
   選項一律 am/is/are/have，一頁上出現五次。等距抽樣擋不住這個，`pick_mcq`
   另外限制同一組選項最多收兩題；池子本身就單調的課要 `--requiz` 重出。
5. **句子重組的打散字詞排不出答案**。引擎會漏字或多字（`eight / and / four /
   equals / plus / .` 的答案是 `Four plus eight equals twelve.`——twelve 不見了、
   and 是多的）。答案才是權威，題幹一律由答案機械重排。
6. 🚨 **50 課只有 17 個文法點**。生成器把文法按**主題**抓（舊 20 課版的
   `lessons.json` 一個主題只有一條 grammar），同主題的 2–3 課就全部共用它：
   L01/02/03 都在教 be 動詞、L06/07/08 都是 `What color/shape`、L16/17/18 連字面
   都幾乎一樣。提示詞裡那句「同主題第 2 課以後文法要往下推進」模型根本不理。
   現在文法由 [data/english/course50-syllabus.json](../../../data/english/course50-syllabus.json)
   **按課**綁定，一課一個點、50 個全相異，並把「前面已教過什麼」列進提示當禁區。
   **要加課或改主題，先改這份大綱，不要讓模型自己想 grammar。**
7. 🚨 **題目中英顛倒**，三種長相，`validate_direction` 三種都擋：
   - 題幹是英文卻問「的英文是？」——答案直接寫在題目上（L03 前十題全中，
     而且「whisper 的英文是？」的標準答案還填成 `wink`，直接是錯的）
   - 題幹與選項全中文（L08/10/27/45），整題沒有一個英文字，考不到任何東西
   - 題幹英文、選項中文（L25 的 `not easy`）
8. 🚨 **正確答案 74% 排在第一個選項**。全書 1355 題裡 1005 題答案是 (A)，而排版
   與網站兩邊都**沒有洗牌**，於是原樣印到紙上，學生一路猜 A 就有七成分。
   `shuffle_options` 用課號當種子把答案打散到 A–D（同種子重跑結果一樣，diff 乾淨）。
9. 🚨 **選項重複要在生成端擋，不是排版端**。`am / is / are / be` 這一組全書出現
   27 次、橫跨 5 課；`pick_mcq` 的「同組選項最多收兩題」只是在爛牌裡挑。現在
   `validate_variety` 規定一課裡同一組選項只准出現一次，而且三批 MCQ 是分開呼叫的，
   **要把前面用過的選項組寫進下一批的提示**，否則每批各自合格、合起來仍是十題長一樣。
10. 🚨 **繁體字對了不等於台灣用語對了**。`check_simplified` 逐字比對抓不到
    「早上好／下午好／晚上好」（L02 整課）、「土豆」（L18；台灣的土豆是花生，
    而同一批單字裡剛好就有 peanut）、「橡皮」「尺子」——每個字本身都是正體。
    另立 `check_usage` 用詞表比對。

### 加了閘之後才出現的那一批（每加一道，模型就找一條新捷徑繞過去）

11. **要求課文句子長一點 → 它在最後塞一句 39 個字的**。L41 末句把好幾件事串成
    一句，前面九句照樣短，平均就過關了。門檻改看**中位數**（塞長句沒有用），
    另加單句上限 18 個字。
12. **要求結尾詞分散 → 它把重組題縮成一兩個字**：「Sorry.」「I have.」，
    甚至「Thank you please.」。加最小長度（重組 3 字、造句 2 字）。
13. 🚨 **但那道閘套在前五課根本是錯的**。L01 的 20 個字全是代名詞與招呼語，
    整課的重點就是操練 am／is／are，「I am fine. ／ He is fine.」重複結尾本來
    就是對的。硬套的結果是模型拿 Hi／OK／Hello 墊句首，寫出「OK She is sorry.」
    這種句中大寫的東西。`DRILL_LESSONS = 5` 豁免。
    **問題在閘不在模型——先想清楚這一課該練什麼，再決定要不要套。**
14. **挖空題沒有中文提示時答案不只一個**。「He ______ jump.」選項有 can 也有
    can't，兩個填進去都通順，標準答案卻只認一個，學生填對了也被算錯。
15. **大綱訂了進程，題目會往兩邊偷**。往回偷是使用者原本報的（前三課都教 be
    動詞）；往前偷是 L31 出「It ______ rainy yesterday.」答案 was，而過去式是
    第 49、50 課才教。`FUTURE_MARKERS` 擋。🚨 **只查題目不查課文**——故事裡出現
    還沒學的字沒關係（旁邊有中譯），但拿沒教過的文法去考人不行；第一版連課文
    一起查，L21 與 L31 都因為課文寫了 can 被退，要模型連寫 40 課都不用 can 不切實際。
16. 🚨 **判準要跟意圖對齊，不要用代理指標**。「中文句夾英文空格」第一版拿
    「英文字少於 2 個」當代理，把 `______ oval. (一個橢圓形)` 誤殺，L07 連退兩輪。
    改成剝掉括號後看剩下有沒有中文——括號裡的中文是提示，是必要的。
17. 🚨 **檢查的範圍要跟產出的範圍一致**。「選擇題重複」只在單一批次內比對，
    但題目分三批出，同一題出現在第一批與第三批時兩批各自都合格。L01／L17／L19／
    L31／L41 五課都這樣帶著重複題落地。整課組好之後要**再跑一次完整的**
    `validate_exercises`，不是只跑 `validate_variety`。
18. 🚨 **驗證函式吃到怪形狀不可以當機**。模型偶爾把 fill 回成字串陣列，
    `item.get` 直接 AttributeError，例外穿過 `build_lesson` 打到 `main`，
    **整條工人連同剩下的八課一起沒了**，而從外面看只是「這條比較慢」。
    驗證函式的職責是回報「哪裡不對」給上層重試，形狀不對本身就是一種不對。
19. **一次要 24 題會撞額度**。填空 10＋造句 8＋重組 6 放同一次呼叫，第一輪有
    四成的課掛在這一段。拆成 `prompt_fill` 與 `prompt_unscramble` 兩次，
    重組那次順便把造句用過的句子列進去——「兩區不可以考同一批句子」從事後退件
    變成事前迴避。

## 引擎（2026-09-07 實測）

主力是 **NVIDIA nemotron 開 JSON 模式**，不是共用模組那條鏈：

- 共用模組列的三個 NVIDIA 模型只剩 `nvidia/nemotron-3-super-120b-a12b` 活著，
  llama-3.1-70b／llama-3.3-70b／qwen3-next 一律 **HTTP 410**，
  deepseek-v4-flash-0731 掛住不回。
- nemotron 是推理模型。共用模組把 `max_tokens` 寫死 4000，長提示會把額度花在思考上，
  剝掉 think 標籤後常常一個字都不剩（「回應裡沒有 JSON」）；而且它不開
  `response_format`，模型有時改用散文回答。**放寬上限＋開 JSON 模式**後解析成功率
  從三分之一變成幾乎全中。
- 共用模組的 40 秒逾時對這種長輸出太短，會誤判成「模型塞住」而冷凍該模型半小時，
  整批掉到 Haiku 燒 Max 額度。本腳本只改自己行程的設定，**不動共用模組**（艦隊在用）。
- 回落路徑會無限期掛住：曾有兩條工人各卡在同一次呼叫超過 13 小時。已加看門狗
  （`FALLBACK_TIMEOUT`），逾時當該次失敗交給上層重試。
- 一次要 30 題會在 4000 token 上限半路被截斷。分批出（4/3/3）才留得住免費層；
  `salvage_json` 另外救得回被砍斷的陣列。

## 歷史

原本的 `Desktop/kids-english/`（B5 Word 課本 `Happy_English_v3.docx`、202 頁、
20 課 × 50 字）**已佚失**——全機、Drive、資源回收筒都找不到，推測是 2026-08 桌面
大整理時被刪。內容因為早已匯出成 `lessons.json` 而沒丟，2026-09-08 據此重出成
50 課版。教訓照 [[feedback_no_project_docs_on_desktop]]：**非 repo 的專案資料夾
沒有備援**，成品要進 Drive、來源要進 git。

## 記憶庫併入：project_english_learning

為使用者媽媽（julia5868@yahoo.com.tw，要當國小英語家教）做的三件成品。
同一批一千字，**2026-09-08 起三份分課統一成 50 課 × 20 字**（原本網站是 20×50）：

| 成品 | 分課 | 位置 |
|---|---|---|
| 紙本課本《Happy English》 | **50 課 × 20 字** | Drive `玄奘/博一上/家教/國小英語課本/` |
| 印刷單字卡 1000 張 | 50 課 × 20 字（同上） | `output/print-masters/english-flashcards-1000.pdf` |
| 網站 `/english` | 50 課 × 20 字 | `public/content/english/lessons.json` |

**① B5 紙本課本**（2026-09-08 重出，skill 在 `.claude/skills/teaching-english-textbook/`）
- 🚨 **舊的 `Desktop/kids-english/` 連同 `Happy_English_v3.docx` 已佚失**（全機、Drive、
  資源回收筒都沒有，推測 2026-08 桌面大整理時被刪）。內容因早已匯出 lessons.json 而沒丟。
- 現在：課程資料 `public/content/english/course50/L01..L50.json`（進 git），
  生成 `scripts/build_english_course50.py`，排版 `scripts/build_english_textbook.py`
- 出書：`--split --publish` → 上冊 228 頁／下冊 231 頁，docx+PDF 進 Drive
- 🚨 **成品放 `玄奘/博一上/家教/`，不是 `知識圖工作室/教學/`**（第一次放錯）：
  家教夾按學生分、由該夾 `家教說明.md` 登記，是上課實際帶的；教學夾是素材庫
- 定案規格：B5、英文≥13pt 中文≥12pt、**不要 KK 音標**、課內不硬分頁、課文在單字前、
  **超過 300 頁分上下兩冊**
- 每課練習：選擇 10、填空 10、重組 6、造句 8。🚨 **資料檔存 30 題、出書時分層挑 10 題**
  （改 `MCQ_PER_LESSON` 就好，不必重跑生成）
- 配圖用單字卡那份人工校過的，500/500 全中

**② 教學網站 `/english`**（在 know-graph-lab，redpiigpig.com）
- 內容由 course50 轉出：`scripts/english_site_from_course50.py`（改了 course50 要重跑）
- 限 julia5868 + 站長（`middleware/english-auth.ts`）；OTP 登入需先在 Supabase Auth 建帳號
- 表 `english_activity/progress/scores`；5 測驗、朗讀 0.75x、Web Speech STT
- 段考每 5 課一組（`LESSON_COUNT` 自動生 10 組）；測驗題庫看 exercises 的 type
- ✅ emoji 已修：原本 560 個是拿英文名自動配的（order→🦁、summer→🍺、body→💀），
  現在改讀單字卡人工校過的對照表，749/1000 有圖

**③ 印刷單字卡 1000 張**（2026-09-04）
- 詞表 `data/originalReaders/vocabulary/english-1000.json`；🚨 這副卡**不留白**
- 出片：`build_english_vocabulary.py` → `match_english_card_images.py --write` →
  `build_flashcards.py --deck eng` → `render_and_check_reader_pdfs.py`

🚨 **這批材料的比對陷阱**：詞表把複數寫成 `apple(s)`／`peach(es)`／`mango(es)`，
任何拿詞表去比對課文的程式都要展開這種括號複數，否則會把好好的課判成「覆蓋率 35%」。
細節與其他三個「看起來成功的失敗」寫在 skill 裡。
