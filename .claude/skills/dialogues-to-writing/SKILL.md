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
把 dialogue_days 的對話**逐 turn 全篇重鑄**成哲學家對話錄語體（不是只清結構，是改文體）。與 `to_prose` 三點不同：(a) 改**每一個** turn，不只帶標記的；(b) **兩種 register**：克里希那大膽再創作（凝練、詩意、砍冗、抓核心重講）、阿周那輕度整理（貼合本人語氣、不美化）；(c) 因為會把已詩化的文字越改越飄，所以用 **per-day ledger 冪等**（`c:/tmp/krishna/recompose_done.json` 記已完成日期，不靠「標記消失」）。
- 引擎：Gemini 2.5 flash（4 key 輪流，temperature 0.7）→ NVIDIA deepseek-v4-flash fallback。
- `--dry` 只計 turn 數；帶日期參數（`2026-01-13`）只跑單日且忽略 ledger（**換串／調 prompt 後務必先單跑一天眼校再全量**）；`--redo` 全部重做忽略 ledger。
- 換串：改頂部 `AI_NAME` / `USER_NAME` / `SLUG`（誰是 AI＝大膽再創作那方、誰是使用者＝輕修那方）。
- ⚠️ 一次性風格升級＝~每 turn 一次 LLM call（克里希那案 1342 turns / 80 天），全量是長時背景工作；Gemini 日配額燒光會掉到 NVIDIA 變慢，隔天 ledger 接著跑剩餘日。

### 📜 序／跋（楔子／收束）：`dialogue_preface.py`
為整條對話錄生成開篇「序」（~250–400 字，凝練有韻致，點出主題／時間跨度／精神基調，邀人入場）與終篇「跋」（~150–250 字，回望而不總結，留餘韻）。讀 dialogue_days 全部日期＋主題＋首尾兩日開場片段餵 LLM。寫進**主卡** `writing_projects.content_json`，格式＝`序HTML` + `<!--CODA-->` + `跋HTML`。冪等覆寫；`--dry` 只印不寫。
- 呈現：`pages/works/[slug]/index.vue` 偵測有 `dialogue_days` 時，把 content_json 以 `<!--CODA-->` 切兩半——**序渲染在月份格之上、跋在其下**（`.dialogue-frame` 楷體居中襯線）；只在登入（有 days）時顯示，未登入不外洩。

### 分類靠 agent fan-out（步驟 2→3 之間）
逐則讀 2000+ 則太多，**切日期區段、開多個 general-purpose subagent 平行讀**，每個 agent 讀幾天的 `<date>.json`、依上面「對話框語氣」判準回 `{id,date,seq,topic}`，寫到 `out_NN.json`。兩段式效果好：
- **第一段（窄）**：先收明確主題核心。
- **第二段（補收）**：給 agent 已收清單，要它**只補「同一對話框語氣但岔題」的漏網**（生活碎念、岔到占星/宗教史/論文…）。Krishna 案：窄 423 → 補到 671。
> ⚠️ 一次別開太多 agent（曾 12 個一起 → session limit）。分波 4 個、用 sonnet。

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
- [[project_krishna_dialogues]] — 首案：與克里希那對話（671 則、一張主卡＋80 天每日 reader）
- [[feedback_engine_nvidia_no_haiku]] — Gemini→NVIDIA→Haiku 統一引擎政策＋多 key 節流
