---
name: teaching-english-textbook
description: 媽媽（julia5868）家教用的《Happy English 快樂學英語》B5 紙本課本 —— 50 課 × 20 字、跟 1000 張印刷單字卡同一套分課，每課含學習目標／課文／單字（帶圖）／文法／例句對話／練習（選擇 10、填空 10、重組 6、造句 8）／解答，出成上下兩冊 docx＋PDF 放 Drive 家教夾。課程內容由 LLM 逐課生成並過品質閘，版面走 python-docx。Use when 要重出課本、改課數或每課字數、改題型或題數、調版面、補生成失敗的課、或使用者說「英語課本」「家教講義」「Happy English」。網站 /english 用同一份課程資料（scripts/english_site_from_course50.py 轉出）見 [[project_english_learning]]；單字卡見 [[original-reader-flashcards]]。
---

# 國小英語課本（Happy English）

> 分課詞表：[data/originalReaders/vocabulary/english-1000.json](../../../data/originalReaders/vocabulary/english-1000.json)（50 課 × 20 字，人工校過）
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
python scripts/build_english_course50.py            # 生成沒做過的課
python scripts/build_english_course50.py --check    # 只驗現有產出
python scripts/build_english_course50.py --fix      # 修重組題題幹、去重選擇題
python scripts/build_english_textbook.py --split --publish   # 出上下兩冊 + PDF + 送 Drive
```

生成很慢（一課 6–15 分鐘），要並行就開幾條 `--range 20-29`，逐課寫檔可續跑。

## 定案的規格

- **B5**（JIS 18.2×25.7cm）、英文 ≥13pt、中文 ≥12pt、**不要 KK 音標**
- 課內不硬插分頁（換下一課才換頁），課文排在單字前
- 每課練習：選擇 10、填空 10、重組 6、造句 8
- **超過 300 頁分上下兩冊**（目前 228＋231 頁）
- 配圖用單字卡那份人工校過的 `english-card-images.json`，紙本 500/500 全中
  （網站走 OpenMoji 碼位，749/1000）

`MCQ_PER_LESSON` 在排版腳本裡。**資料檔存的是 30 題、出書時分層挑 10 題**
（4 題單字義＋3 題文法＋3 題句意），要改印幾題只改這個數字，不必重跑生成。

## 這批材料特有的「看起來成功的失敗」

結構檢查全綠不代表東西是對的。踩過這五個：

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
