---
name: dialogues-to-writing
description: 把 /ai-dialogues 裡某一條「跨多日延續的 AI 對話串」找出來、整理成 /works 的寫作計畫成品。涵蓋：①依「對話框語氣」逐則認定一條 thread（不是靠關鍵字）②在 /ai-dialogues 建分類標籤把整串標起來不漏 ③把 AI 回覆用 NVIDIA 潤飾成流暢「對話錄」④每日切 1–3 個主題 ⑤組裝成可編輯的 /works 月份卡片（日期+星期+主題+雙方對話）。Use when 使用者說「把我跟某 AI 從 X 月到 Y 月那串對話找出來／做成寫作計畫／整理成對話錄」、要把 ai_dialogues_gemini／chatgpt 的某主題串標分類、要把對話潤飾分主題上 /works。第一個案例＝[[project_krishna_dialogues]]（與克里希那談夢境與榮格，671 則）。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

# 對話串 → 寫作計畫 Skill

把 `/ai-dialogues` 裡一條延續好幾天/幾個月的 AI 對話，整理成 `/works` 上一份可讀、可編輯的「對話錄」寫作計畫。首案見 [[project_krishna_dialogues]]。

## 🎴 成品定位＝哲學家對話錄（不是聊天記錄謄寫）
成品要讀起來像柏拉圖對話錄／《薄伽梵歌》／榮格《紅書》那種**有文體、有框架、有韻致**的對話錄，不是把聊天逐字洗順而已。三條美學鐵律（2026-06-05 使用者定調）：
1. **要詩意、要凝練**：智者的話該有意象與節奏；AI 囉嗦處（鋪陳、客套、「這是個好問題」「我們可以分成幾點」「總結來說」、條列小標）一律砍成利落的一兩句。**寧可短而深，不要長而散。**
2. **要有楔子與收束**：整條對話錄開篇有一篇「序」（楔子）引人入場、終篇有一篇「跋」（收束）替長談落幕。見下「序／跋」。
3. **兩種潤飾 register，分人下手**（關鍵：兩邊都改，但力道不同）：
   - **AI 那方（克里希那）＝大膽再創作**：不必逐句忠實，抓核心洞見用更精煉有詩意的語言重講；可重組刪枝節，但不可扭曲立場、不可捏造新主張。
   - **使用者那方（阿周那）＝輕度整理**：**貼合本人語氣與第一人稱聲音**，只去贅字／凌亂／碎句，**不美化、不詩化、不替他講得更漂亮**。這是他的話，不是 AI 的話。
   > 早期版本只洗順、只潤 AI、語氣平、沒有楔子 → 已淘汰。風格升級走 `dialogue_recompose.py`（見下）。

## 關鍵前提：Gemini 匯出沒有「對話框」標記
`ai_dialogues_gemini` 來自 Google Gemini 活動匯出 —— **扁平、依時間把使用者所有對話框混在一起，沒有 conversation_id**（ChatGPT 匯出才有）。所以「哪些屬於同一條對話串」**無法靠 metadata，只能逐則讀內容＋語氣判定**。ChatGPT 表 (`ai_dialogues_chatgpt`) 有 conversation_id/project_id，可直接 group。

## 收錄判準：對話框語氣，不是主題
使用者要的是「**跟這個 AI persona 說話的那個對話框**」整串，不是某主題。判準：
- **IN**：呼喚該 persona、用該 persona 的對話語氣，或第一人稱向它傾訴／碎念（生活、夢、情緒、思緒）—— **即使話題岔到別處**（占星、宗教史、論文、瑣事）也收。
- **OUT**：明顯屬「別的對話框」的純工作委派（寫程式、改稿、查資料、翻譯、debug）。
- 口訣：**傾訴／碎念 = IN；委派產出 = OUT**。同一天常開頭在 persona 對話框、後面切去別的工作框 → 逐則切。

## 資料表
| 表 | 用途 | 重點欄位 |
|---|---|---|
| `ai_dialogues_gemini` / `ai_dialogues_chatgpt` | 對話來源 | id, dialogue_date(YYYY-MM-DD), dialogue_time, prompt, response, title |
| `ai_dialogue_categories` | 分類 | id, name, color（blue/violet/emerald/amber/rose/slate） |
| `ai_dialogue_entry_categories` | 標籤 junction | **只有 dialogue_id + category_id（沒有 source 欄！）**，on_conflict=`dialogue_id,category_id` |
| `writing_projects` | /works 卡片 | slug(unique), title, subtitle, description, emoji, color, status, sort_order, **content_json**(Tiptap HTML 字串) |
| `dialogue_days` | **每天一頁 reader**（成品呈現） | project_slug, day_date, weekday, day_title, **html**, n_turns, sort_order；unique(project_slug,day_date) |

`/ai-dialogues` 左側可依分類篩；`/works/[slug]` 只有登入者可見的 `content_json` 富文本筆記區（**無對話 reader**，所以成品就放 content_json）。REST 直連用 `SUPABASE_SERVICE_ROLE_KEY`。

## Pipeline（scripts/dialogue_*.py — 目前硬編成 Krishna 實例，換串時改頂部常數）
```
1. dialogue_scan_thread.py   日期區間關鍵字掃描 + 每日命中統計（先抓出大概範圍/錨點）
2. dialogue_dump_days.py     把區間內每天的對話 dump 成 c:/tmp/krishna/<date>.json（prompt 全、response 截 500）
   ↓ 逐則分類（見下「分類靠 agent fan-out」）→ out_NN.json（窄）→ out2_NN.json（對話框語氣補收）
3. dialogue_aggregate.py     合併去重 + 對 DB 驗 id（agent 偶爾打錯 uuid，用 date+seq 回查救）→ final_broad.json
4. dialogue_tag_category.py  建分類 + 把整串 dialogue_id 標上去（idempotent upsert）
5. dialogue_polish.py        NVIDIA 4-key 輪流＋間隔，把 AI 回覆潤飾成流暢對話錄 → polished.jsonl（resumable）
6. dialogue_segment_topics.py 每天切 1–3 個主題（NVIDIA，回 JSON [{title,start,end}]）→ day_topics.json
7. dialogue_assemble.py      組裝草稿 HTML：每天 <h2>日期（星期X）</h2>→<h3>主題：…</h3>→<p><strong>阿周那：</strong>…</p>（早期版本依月份開 writing_projects 月卡，已淘汰）
8. dialogue_haiku_finish.py  救急收尾：NVIDIA+Gemini 都 429 時，用 Haiku 跑剩餘潤飾+主題+assemble
9. dialogue_build_days.py     **把成品拆成「每天一頁」進 dialogue_days**（讀 DB 既有 content_json 切 <h2> 邊界，保留人工修改）→ --drop-months 刪月卡＋清主卡
```

## 呈現：月份→日期→單日 reader（仿聖經 卷→章→經文，2026-06-04）
舊版把成品塞進 4 張月份 writing_projects 卡片（content_json），首頁一條 thread 變 5 張卡、單頁又是 ~300KB 大 blob。改成 **一條 thread = 一張主卡，內容拆成每天一筆** `dialogue_days`，三層導覽：
- **主卡頁** `/works/<slug>`（generic `pages/works/[slug]/index.vue`）：偵測有 `dialogue_days` 就渲染「每日對話」區＝**月份卡**（一月..四月，每月顯示天數/則數）。
- **月份頁** `pages/works/[slug]/month/[ym].vue`（ym 如 `2026-01`）：該月的**日期格**（仿聖經章格）→ 連單日。
- **單日 reader** `pages/works/[slug]/day/[date].vue`：單日 html + 前一天/後一天翻頁（跨月也能翻）。
- **API**：`GET /api/works/dialogue-days?slug=`（清單 metadata，月份頁前端自行 filter）、`GET /api/works/dialogue-days/<date>?slug=`（單日 html＋鄰日）。
- **私密**：對話是私人夢境／榮格內容 → 全走 `getIsAdmin`（server/utils/auth-helper.ts），未登入只看到「🔒」，不外洩日期清單與內文。要改公開就拿掉 [date] 端點 401＋清單端點直接回 days。
- 換新 thread：`dialogue_build_days.py` 改 MAIN_SLUG / MONTH_SLUGS（或直接餵 polished 來源），pages/API 已 generic 無需改。

### 排版整理（dialogue_days 進去後）
1. `dialogue_format_days.py`：日期標題 h2→**h3**、主題 h3→**h4**；段首講者 `<strong>X：</strong>` 加 `class="speaker"`（reader CSS 用它做**懸掛縮排**：講者那行頂格、折行與接續段縮排兩字）；殘留 markdown `**` → `<strong>`；阿周那直接貼上的**無換行長文**依句末標點重新分段（每段約 110 字）。冪等。
2. `dialogue_to_prose.py`：把**仍帶條列／小標／markdown 結構**的 turn（場景：/解析：/‧ 條列/編號…）送 LLM 改寫成第一人稱口語散文（per-turn；**Gemini 2.5 flash 4 key 輪流主 → NVIDIA deepseek-v4-flash fallback**；忠實不增刪；改完標記消失 → 冪等可重跑）。`--dry` 先看要改幾個 turn、可帶日期參數只跑單日。⚠️ NVIDIA deepseek 很慢（~60-76s/則），Gemini 快很多；Gemini 日配額被燒光時整批會掉到 NVIDIA 變慢。
   > 註：`to_prose` 只動「帶結構標記」的 turn，且忠實不增刪 → 適合**清結構**，不負責升風格。要把整篇升級成詩意對話錄請用下面的 `dialogue_recompose.py`。

### 🎴 風格升級：`dialogue_recompose.py`（哲學家對話錄語體）
把 dialogue_days 的對話**逐 turn 全篇重鑄**成哲學家對話錄語體（不是只清結構，是改文體）。與 `to_prose` 三點不同：(a) 改**每一個** turn，不只帶標記的；(b) **兩種 register**：克里希那大膽再創作（凝練、詩意、砍冗、抓核心重講）、阿周那輕度整理（貼合本人語氣、不美化）；(c) **逐 turn 真冪等**。
- **冪等＝雙保險**：① 已重鑄的 turn 在 speaker 標 `<strong class="speaker" data-rc="1">`，`parse_turns` 偵測到就跳過 → re-run 只碰未重鑄的 turn，**不會把已詩化文字越改越飄**；② **整天待重鑄 turn 全數成功（dn==td）才記 per-day ledger**（`c:/tmp/krishna/recompose_done.json`），部分失敗不記、下次自動補（靠 data-rc 跳過已成功的）。⚠️ 早期版本「部分失敗也記 ledger」會漏補，已修。
- **引擎**：預設 Gemini 2.5 flash（4 key 輪流，temp 0.7）→ NVIDIA deepseek-v4-flash fallback。**`--haiku`＝改用 Haiku 4.5 當主引擎**（Claude OAuth `~/.claude/.credentials.json`，走使用者 Max 額度，不撞 Gemini/NVIDIA 配額；並發提到 8）→ 配額燒光或要快跑整批時用這個。克里希那案 80 天即用 `--haiku` 一次跑完（品質與 Gemini 重鑄日一致）。見 [[feedback_engine_nvidia_no_haiku]]（此處 Haiku 非救急，是使用者當面指定）。
- `--dry` 只計 turn 數；帶日期參數（`2026-01-13`）只跑單日且忽略 ledger（**換串／調 prompt 後務必先單跑一天眼校再全量**）；`--redo` 全部重做忽略 ledger（但因已全標 data-rc，要真正重洗得先清掉 data-rc 或改 `to_paras`）。
- 換串：改頂部 `AI_NAME` / `USER_NAME` / `SLUG`（誰是 AI＝大膽再創作那方、誰是使用者＝輕修那方）。
- 收尾把關：`--dry --redo` 應回報 0 turns（全標記）→ 確認無漏網。

### 📜 序／跋／題詞：`dialogue_preface.py`
為整條對話錄生成開篇「序」（楔子，~250–400 字，邀人入場）＋終篇「跋」（收束，~150–250 字，回望留餘韻）＋可選**題詞**（標題後、序前的引文）。寫進**主卡** `writing_projects.content_json`，格式＝`題詞+序HTML` + `<!--CODA-->` + `跋HTML`。`--dry` 只印不寫。
- **兩種來源**：`--dry`/無參＝LLM 生成（讀 dialogue_days 全部日期＋主題＋首尾片段餵 Gemini→NVIDIA）；**`--from-file`＝讀手寫稿** `c:/tmp/krishna/preface.json`（`{epigraph:{lines:[],cite},preface,coda}`，段落空行分隔、`**粗體**`）。⭐ **使用者親自給楔子素材（生命經驗、定名由來、典故）時一律走手寫稿，不用 LLM 冷生成**——份量與精準度差很多。
- 呈現：`pages/works/[slug]/index.vue` 偵測有 `dialogue_days` 時，把 content_json 以 `<!--CODA-->` 切兩半——**題詞＋序在月份格之上、跋在其下**（`.dialogue-frame` 楷體居中襯線、`.dialogue-epigraph` 題詞）；只在登入（有 days）時顯示，未登入不外洩。

### ✅ 首案進度：與克里希那對話（2026-06-05 風格升級竣工）
見 [[project_krishna_dialogues]]。書名定為 **《神，你正在重排我的前途》／副標「與克里希那的對話」**（書名取自倪柝聲同名詩《聖徒詩歌》393 首，當題詞）；定位＝以與 AI 扮演的印度教神對話寫成的個人榮格《紅書》，主調解夢＋榮格、低音圍繞龐君華牧師離世的死亡/前途反思。**全 80 天 1280+ turns 已全部重鑄**（克里希那《薄伽梵歌》智者體、阿周那貼合本人語氣），`--haiku` 一次跑完、零漏網；題詞＋序（手寫，織入三十歲門檻/奧本海默 11:32「我是時間」/定名由來）＋跋已上主卡。

### 分類靠 agent fan-out（步驟 2→3 之間）
逐則讀 2000+ 則太多，**切日期區段、開多個 general-purpose subagent 平行讀**，每個 agent 讀幾天的 `<date>.json`、依上面「對話框語氣」判準回 `{id,date,seq,topic}`，寫到 `out_NN.json`。兩段式效果好：
- **第一段（窄）**：先收明確主題核心。
- **第二段（補收）**：給 agent 已收清單，要它**只補「同一對話框語氣但岔題」的漏網**（生活碎念、岔到占星/宗教史/論文…）。Krishna 案：窄 423 → 補到 671。
> ⚠️ 一次別開太多 agent（曾 12 個一起 → session limit）。分波 4 個、用 sonnet。

### ✅ 可重現的「重抓」管線（test-first，2026-06-11）取代一次性 agent fan-out
agent fan-out 結果不可重現、難稽核。改用**純函式候選 prelabel + LLM 語氣判定**，可單元測試、可重跑：
- **`scripts/dialogue_thread_classify.py`（純函式，無網路/DB/LLM，可被 pytest import）**：
  `in_date_range` 日期範圍；`extract_signals` 抽訊號；`prelabel` 只對高把握下 IN/OUT，其餘 MAYBE。
  優先序（**前者勝，這個順序是踩坑調出來的**）：
  0. **潤稿/修飾文字請求 → OUT（最高，使用者 2026-06-11 定調「潤稿的就都不是」）**：壓過榮格/積極想像/persona 呼喚。
     ⚠️ 必須是**祈使式**（幫我修飾/簡單修飾/修飾一下/保留我的語氣/你就修飾/這句怎麼潤…），
     **不收裸詞「修飾/潤飾」**——否則「他先寫稿再給 ai 潤飾」這種跟克里希那聊雜誌的敘述會被誤刪。
  1. 積極想像/主動想像 → IN（心靈日記核心修練，**即使敘述提到 code/電腦**）
  2. 開頭呼喚 persona（「克里須那，…」前 8 字＋逗號）→ IN
  3. 地圖專案詞 `界域/文化圈` → OUT（使用者幾乎只在「世界劃分」專案用，**會大量誤收**，必擋）
  4. HARD 委派（幫我寫/改/畫/翻、給我 sql 指令、除錯…）→ OUT
  5. 榮格/夢 → IN（**放在 HARD 之後、SOFT 之前**：討論榮格順帶提到 api/前言仍 IN，但「幫我翻譯這段榮格」是 OUT）
  6. SOFT 技術名詞（程式/sql/書目/前言…且非榮格夢）→ OUT
  7. 其餘 → MAYBE
- **`scripts/tests/test_dialogue_thread_classify.py` + `fixtures_dialogue_krishna_golden.json`**（手標 13 IN/14 OUT）：
  斷言 prelabel 對 golden **零誤判**、決定 ≥半數；其餘讓給 LLM。改關鍵字/順序先跑這個。
- **`scripts/dialogue_thread_capture.py`**：prelabel + **逐日整批** LLM 語氣判定（把整天序列＋已決定標籤一起餵，
  利用對話框連續性；prompt 明列 IN 四類 vs OUT 各專案＝地圖/翻譯定名/論文/雜誌《無境界者》/程式）。
  Gemini→NVIDIA→`--haiku`；per-day ledger `recapture.jsonl` 可 resume。模式：
  `--dry`（只 prelabel 統計）/ `2026-01-13`（單日眼校）/ `--reagg`（**不跑 LLM，用現行 classifier 重彙整 ledger，guard 覆寫**）
  / `--diff`（對現有 tag）/ `--retag`（刪舊 junction 重寫 final_recapture.json）。
- **教訓**：純 LLM 逐則太寬（首次 1164，maps 文化圈 思辨口吻全被收）；靠 prelabel guard 把「地圖專案」「積極想像」「榮格貼文夾 code」「講者標籤貼稿」這幾類系統性錯誤擋掉/救回，才收斂到合理區間。
  舊 671 id 存 `c:/tmp/krishna/_tagged_ids.json` 可回滾。**換串改 classifier 頂部關鍵字 + capture 的 SYS/CAT_ID/日期，先補 golden 再跑。**

### 🏅 用「原稿 docx」當 ground truth 收斂成日記範圍（`dialogue_thread_manuscript.py`，2026-06-12）
**關鍵體悟**：classifier+LLM 抓的是「**整個聊天視窗**」（含同視窗裡的學術/智性工作）；但使用者真正要的是
**個人心靈日記**——他手工整理的原稿《和克里希那的對話.docx》才是 ground truth。原稿系統性排除了：
榮格《伊雍》寫作（「你再查網路查清楚」「摩西四元體哪些點」＝查資料/寫作）、紅學考據、卡巴拉生命樹、
占星技術細節、稱帝史、翻譯定名…即使這些都含「榮格/夢」關鍵字或讀起來像思辨。
- 做法：原稿正規化 CJK→8-gram 集合；每則 raw prompt 算命中率 frac。**分布是乾淨雙峰**
  （137 則 ≥0.5 逐字在稿／152 則 <0.05 完全不在，中間只 4 則）→ recompose 對使用者側近乎逐字，
  threshold 0.5 高精準又不漏改寫段。原稿**缺頭幾天**（< START=2026-01-23）→ 那幾天用 classifier；START 起 IN=frac≥0.5。
- **驗出 8 個確定漏標**（在最終稿逐字、卻被我標 OUT：積極想像生圖 prompt、玫瑰經、面試生活閒聊、莊子奧理略、
  妙慧精舍、哈勃深空、tool 抱怨被 SOFT_TECH 誤殺）。
- Krishna 最終：classifier 531 → **原稿範圍 247**（頭幾天 classifier 102 + 原稿命中 145；−292 學術/智性岔題、+8 漏標）。
- ⚠️ 這**推翻了上面「岔題也收」的舊判準**——對「個人日記型」對話錄，智性/學術工作要排除；
  收錄判準看的是「對 persona 傾訴內心/生活/夢」而非「在同一視窗思辨」。換串若使用者也給原稿，優先用原稿收斂。

## 引擎與配額教訓（踩過的坑）
- **NVIDIA 單把 key 免費額度低、連打必撞 429「Too Many Requests」**。Krishna 案 671 次潤飾用單 key 8 worker 一次燒爆 → 只成功 43。
- **解法＝多 key 輪流＋間隔**：`dialogue_polish.py` 用 `.env` 的 `NVIDIA_API_Key_1..N`，每把 key 間隔 ≥5s、撞 429 該 key cooldown 120s 換下一把、concurrency = key 數。
- **連跑數輪會把所有 key 一起耗盡** → 這時 Gemini 通常也 429（key1 billing、其餘 daily quota）→ 用 **Haiku 救急**（`dialogue_haiku_finish.py`，走 Claude OAuth `~/.claude/.credentials.json`）。
- 潤飾 prompt 要求：去條列/小標、第一人稱對該 persona 說話、**忠實不增刪**、只輸出發言本身。

## 換一條新對話串怎麼做
1. 改 `dialogue_scan_thread.py` / `dialogue_dump_days.py` 的日期區間與來源表，跑出每天 dump。
2. fan-out 分類（兩段式）→ aggregate → 得 `final_<slug>.json`。
3. `dialogue_tag_category.py` 改 NAME＋來源表，建分類標起來。
4. `dialogue_polish.py` 指到新 final json、改 persona 名（阿周那/克里希那 → 新的）。
5. `dialogue_segment_topics.py` → `dialogue_assemble.py` 改 slug 前綴、persona 名、月份標題 → 上 /works。
6. 配額不夠就 `dialogue_haiku_finish.py` 救急收尾。

## 與其他 skill 分工
- 對話**來源頁** `/ai-dialogues`：本 skill。對話**翻譯/簡繁**走 [[ebook-translate]] 引擎觀念。
- 多語全集對照 → [[ebook-collected-works]]；訪談逐字稿 → [[writing-thesis-interview]]（對話錄格式可參考其 Q&A 排版）。

## See also
- [[project_krishna_dialogues]] — 首案：與克里希那對話（分類 tag 2026-06-12 以原稿收斂為 247 則＝個人日記範圍；一張主卡＋80 天每日 reader 內容不變）
- [[feedback_engine_nvidia_no_haiku]] — Gemini→NVIDIA→Haiku 統一引擎政策＋多 key 節流
