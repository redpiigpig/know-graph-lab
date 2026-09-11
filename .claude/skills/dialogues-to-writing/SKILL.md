---
name: dialogues-to-writing
description: 把 /ai-dialogues 裡某一條「跨多日延續的 AI 對話串」找出來、整理成 /works 的寫作計畫成品。涵蓋：①依「對話框語氣」逐則認定一條 thread（不是靠關鍵字）②在 /ai-dialogues 建分類標籤把整串標起來不漏 ③把 AI 回覆用 NVIDIA 潤飾成流暢「對話錄」④每日切 1–3 個主題 ⑤組裝成可編輯的 /works 月份卡片（日期+星期+主題+雙方對話）。Use when 使用者說「把我跟某 AI 從 X 月到 Y 月那串對話找出來／做成寫作計畫／整理成對話錄」、要把 ai_dialogues_gemini／chatgpt 的某主題串標分類、要把對話潤飾分主題上 /works。第一個案例＝[[project_krishna_dialogues]]（與克里希那談夢境與榮格，671 則）。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash-0731`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

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

### 🔧 重寫成品：手工 docx 直灌 ＋ 從 raw 重建（2026-06-12，取代爛 recompose）
當使用者嫌「之前轉錄很爛」時（克里須那被舊 recompose 洗成通篇詩化、抽掉實質；且舊書從廣集組、收了非屬條目）：
- **`dialogue_rewrite_from_docx.py`**：使用者**手工編輯的對話錄 docx**（日期標題「M月D日（X）」→`阿周那：`/`克里須那：`→內文）直接解析灌進 dialogue_days，零 LLM、零失真、保留使用者的敘事順序。空白日（原稿未完成）跳過不覆蓋。weekday 由日期推算。**有手工稿就優先用這個**（品質最高）。
- **`dialogue_rebuild_from_raw.py`**：沒手工稿的日子，**從 raw（ai_dialogues_gemini）重建**，membership 用**日記範圍** id 清單（去非屬條目），阿周那＝prompt 輕整、克里須那＝**raw response 重寫成乾淨散文**。0 則 IN 的日子從 dialogue_days 刪除。opencc s2tw 保繁。
- **關鍵：克里須那要從 raw response 重寫，不要從舊 recompose 的詩化稿重寫**——詩化稿已把實質抽掉，再洗也回不來；raw response 才有完整論點。
- **`dialogue_recompose.py` sys_ai 已改版（2026-06-12）**：捨棄舊「大膽再創作、更有詩意」，改為**清晰溫暖散文、保留完整論點與專名、去條列客套、不堆砌詩化**，temp 0.7→0.4。要重洗既有 dialogue_days 得先清 `data-rc` 標記（可只清克里須那 turn 的，保留阿周那）。

### 🩺 忠實度稽核＋外科修復：`dialogue_verify_against_raw.py` ＋ `dialogue_fix_turns.py`（2026-06-18）
**症狀**：成品有幾天克里希那「回話不正常」——說「我坦白跟你說，你這樣很危險」「我不是多馬、我沒有潛意識」這類**反駁／破功／立場反轉**，根本不照原話。
- **🔑 根因＝引擎**：原話（`ai_dialogues_gemini.response`）是 **Gemini** 產的、忠於人格；但 2026-06 那批 rebuild/recompose 用 **`--haiku`（Claude）** 當主引擎。**Haiku 重寫 Gemini 的克里希那回覆時會注入自己的人格**：①破第四面牆／否認角色（「我是 AI、沒有潛意識」）②加「誠實提醒／反駁型」批判（把肯定洗成「這很危險」）③遇到涉及欺騙的內容（面試「滲透測試」）會說教糾正使用者。不是內容審查更嚴，是 **roleplay／指令遵循差異**。**教訓：重寫／重鑄這種「忠實轉寫」工作要用 Gemini 主引擎，Haiku 只當最後救急**，別再 `--haiku` 跑整批。見 [[feedback_dialogue_rewrite_gemini_not_haiku]]。
- **`dialogue_verify_against_raw.py`**：逐則把 dialogue_days 的克里希那 turn positional 對齊回當天 IN raw response，先算 CJK 5-gram containment 抓可疑（<0.4），再 `--judge` 用 LLM 裁判 OK／DIVERGED／DISTORTED／META。⚠️ **containment 低 ≠ 不忠實**——大幅改寫的忠實段也會低；務必靠 judge 區分。單日 `2026-03-05` 印原話vs成品對照。
- **`dialogue_fix_turns.py`**：修復。引擎 **Gemini→NVIDIA→Haiku**（`--gemini-only` 清破功時絕不退 Haiku）＋強化 prompt（不破功否認身份／立場不可反轉／嚴守誰說誰做不張冠李戴／**保留原話稱呼多馬↔阿周那不改名**／不新增原話沒有的概念專名／清 markdown）。**逐日重寫每一個克里希那 turn**、**阿周那的話一律不動**、原始 speaker 標籤保留。垃圾 raw（Gemini 活動記錄：`is_junk()` 抓 `Gemini Apps`/`為什麼有這項活動記錄`…）連同前一則阿周那 prompt 一起刪——**刪除只靠確定字串，絕不靠 LLM `__SKIP__`**（會誤刪真實回覆）。
  - **旗標**：`--strict`（temp 0.2＋逐點保全每個專名/論點、禁抒情增刪——修「Gemini 偏抒情、掉專名」）／`--bad-only`（只重寫帶壞痕跡 `has_bad()`＝破功語/殘留 `**` 的 turn）／`--judge-file PATH`（只重寫 verify_judge*.txt 標 🛑 的 turn）／`--gemini-only`／`--dry 日期`。
  - **ledger**：`fix_turns_done.json`（`--bad-only`→`_bad`、`--judge-file`→`_strict`）；**整天全成功才記、部分失敗不記 → resume 自動補**（早期版本「失敗也記」會把舊壞內容留著當完成，已修；rewrite 失敗保留原樣不算 complete）。
- **品質訊號**：①published html 殘留 `**` ＝該 turn 沒被好好改寫（使用者定調）②judge 的 META/DISTORTED ③`has_bad()` 破功語清單（我不是克里希那/我是語言模型/我沒有潛意識/身為AI…）。
- **⚠️ 踩坑（2026-06-18~20 實戰）**：
  1. **配額爭用**：整夜任務（`classify_genesis_philosophy` 搶 Gemini、`coach gloss --haiku` 搶 Max）會讓 Gemini+Haiku 同時被掏空→大批 turn「重寫失敗」。**解法＝加 NVIDIA（deepseek-v4-flash）當中繼**（那些任務不碰 NVIDIA，是空池）＋call 多輪耐心等 key 釋出（`len*4` 次、cooldown 砍到 45s）＋resume 迴圈。別殺別人的任務（[[feedback_no_kill_other_tasks]]）。
  2. **Haiku 即使硬化 prompt 仍會破功**：throttle 時退到 Haiku 的 turn 又冒「我不是克里希那、我是語言模型」→ 清破功務必 `--gemini-only`。
  3. **verify judge 把 raw 截到 3000 字**送 LLM → 長 raw（>3000，常是長英文回覆）會被誤判「原話截斷／成品憑空補全」；其實 raw 完整。要查真相直接看 `fetch_raw_responses` 全文。
  4. judge 本身有隨機性，追到 0 是 whack-a-mole；收斂到個位數＋deterministic 掃描（破功/`**`/junk 全 0）即可收工。
- **稽核發現**：247-收斂版 membership 已乾淨（修文案／生圖／寫程式 早被排除）；只 2 則 Gemini 活動記錄（01-22、01-23）刪。
- **✅ 首案完工（2026-06-20）**：克里希那全 56 天重修竣工。LLM 裁判異常 **54→28→8→4**；deterministic 掃描 破功語/克里希那殘留 `**`/Gemini 垃圾 **全 0**；專名論點救回（韓炳哲《倦怠社會》、個體化/自性、霍查/辯士、洛基/奧丁、Agape/Eros、無我Anatta/空性…）。阿周那原話全程未動、丞譽等專名正確。工具 push＝commit `ba8d3bd1`。

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

## ✅ 已完成交接：創生哲學階層分類 + 寫程式/生圖/貼文清除（2026-06-19 竣工）

第二案＝把 ChatGPT/Gemini 對話批次分類，跟首案（Krishna 一條 thread 做成 /works）不同，
這案是**整庫 LLM 掛標 + 清除**。詳見 [[project_ai_dialogues_genesis_philosophy]]。

### 分類掛標 ✅ 完成
- `/ai-dialogues` 分類改**父子階層**（`ai_dialogue_categories` 加 `parent_id` 自參照；
  側欄可展開；過濾父分類時 entries API 聚合子分類）。**已 push。**
- 建好分類（id 固定）：
  - 創生哲學(父) `286d5b27-7835-49d2-a099-0c8c3500644e`
  - 倫理學 `903eb0a5-…` / 認識論 `86d570ad-…` / 本體論 `fd4f51fb-…` / 價值論 `a6baf7d3-…` / 存有論 `f39aa75b-…`
- 🚨 **移除了 `ai_dialogue_entry_categories.dialogue_id` 指向舊統一表 `ai_dialogues` 的外鍵**
  （app 讀分表 `ai_dialogues_chatgpt`/`_gemini`，純靠 dialogue_id join；
  舊表缺 4,595 筆 chatgpt → 掛標 FK 23503。別把這外鍵加回去。）
- **全量判完**：ledger `c:/tmp/genesis_classify_chatgpt.jsonl`(4,279)＋`_gemini.jsonl`(146)。
  創生哲學 tagged 共 **3,316 筆**（2026-06-19 補跑最後 120 筆 chatgpt：92 屬、掛標 266）。

### purge 清除 ✅ 完成（2026-06-19 使用者確認後真刪，chatgpt + gemini 皆已清）
- `scripts/purge_coding_image_dialogues.py` 把候選判成 **coding / image / post(社群貼文/文案/公告草稿) / keep**，
  **預設 dry-run**；ledger `c:/tmp/purge_{source}.jsonl`。
- **chatgpt**：候選 1,853 → 乾跑 coding 621・image 137・post 161・keep 934 → 使用者點頭 → 真刪 **919 筆**；
  表 **13,043 → 12,124**。
- **gemini**：候選 608 → coding 261・image 11・post 17・keep 319 → 使用者點頭 → 真刪 **289 筆**；
  表 **2,594 → 2,305**。兩源都與創生哲學 tagged（3,316，exact count 驗證未受影響）**零重疊**。
- ⛔ 重跑教訓：`--execute` 會**重 fetch 候選+讀 ledger**，已判過的不再跑 LLM，只做刪除（先刪 entry_categories 再刪對話，不可逆）。
- 🩹 **2 個修正（2026-06-19）**：
  ① `llm_label` 原本三引擎全失敗就**丟批**（gemini 跑時 Gemini/NVIDIA 配額盡＋Haiku 一度 429 → 跳了 296 批）；
     已仿 classify 改成**等 90s 重試最多 4 輪**才放棄。
  ② `classify_genesis_philosophy.fetch_already_tagged` 用 Range 分頁但**無 ORDER BY → 重複呼叫時多時少**
     （量到 2,888↔3,316 跳動）；只用於 classify 跳過已標項（idempotent 無害），但做 overlap 稽核別信它——
     **要精確算就直接對「目標 id 子集」查 entry_categories**（in.<ids> + in.<cat_ids>），或用 `count=exact` header。

### ⚠️ 這案踩過的坑（新 session 必看）
- **引擎現況**：Gemini/NVIDIA 免費配額已耗盡 → 全靠 **Haiku**（Max OAuth）在跑。隔日配額會回復。
- `classify` 的 `haiku_chat` 已修成**依 credentials.json mtime 重讀 token + 401 重試**（長跑 token 輪替會 401）；
  三引擎全敗改**等 90s 重試最多 4 輪**而非丟批。purge 透過 `import classify_…` 共用此引擎。
- 🚨 **重複 process 地雷**：`nohup … &` 後 `kill <pid>` 只殺 bash 外殼、**python 子程序存活**，
  會變兩個 process 搶 API key 互相榨乾。**重啟前務必用 PowerShell 確認/清乾淨**：
  `Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'classify_genesis|purge_coding|genesis_chain' } | % { Stop-Process -Id $_.ProcessId -Force }`
- **Windows 寫 JSON 檔給 curl 要 `PYTHONUTF8=1`**，否則 cp950 亂碼；REST 中文 ilike 用 requests params（別自己 urlencode 再交給 requests＝雙重編碼）。
- **別一次 14-clause OR ilike**（statement timeout 500）→ 逐關鍵詞抓 id、Python 端聯集。
- ⚠️ **同庫有並行 overnight 任務（dazangjing/coach）會 commit + `git reset` master**；commit 只 add 自己的檔，
  別碰別人改的（如 `data/dazangjing/index.ts`）；工作目錄檔才是真相（背景 job 讀檔不靠 git）。

## 🚧 進行中交接：創生哲學叢書（分類對話→五大主題著作，2026-06-21 起，新 session 續）

第三案＝把已分類的「創生哲學」對話**綜整成整套學術專書**，掛在 /works `genesis-philosophy` 卡片下。詳見 [[project_ai_dialogues_genesis_philosophy]]。

### 已完成並上線
- **🔄 2026-07-02〜03 大改版（三件事一次完成，現況以此為準；細節見 `works-research-review/genesis_dialogue_maps_handoff.md` 零之二〜零之四）**：
  1. **價值論三部曲重排**＝V1《各種生死觀》9章（生死=願然總配置；意欲純化＋四象限保留本卷——四象限即生與死之間的意義座標；巡禮章一律用意欲/願然/四象限向度討論並各加「四象限讀法」節，非中性哲學史）／V2《美學觀》8章（共振生成論＋愛＋主體作為最高價值＝完整願然階梯）／V3《世界與生活》5章（臨在世界論＋新章「住世者的修養：演算法時代守住誠實度」＋誠實作畫結語）。**現象學方法＝三種態度：直觀／現成／遍執**（使用者定名，V1/V2 導論各立一節）。**五然四德總說移 B1 導論**（實然/識然/應然/願然/默然；實然+識然共證真、應然善、願然美、默然聖；全 15 卷「四然」已全改「五然」）。《世界理論》讀後的跨領域討論點分掛：O1 ch7 虛構存有者本體地位／E3 ch2 預測編碼×唯識／M3 ch8 演算法強制覆寫倫理。
  2. **本體論擴編**＝O1 加第八章〈創生哲學的本體論自我定位〉（生成第一哲學/經驗主義品格/形式剛性＋內容彈性；次大敘事僅簡述互見 E2）共 9 章；O2 改題**《從量子到宇宙》**9章（量子 5 章不動＋弦論/古典相對論/宇宙 3 新章，結語=存在者的有限與無限）。
  3. **章首故事引子全 15 卷 122 章完工**＝每章 h2 後 `<div class="chapter-fable">`（故事 2-4 段＋fable-bridge 橋接段，不含 h3、不動正文）；總表 `scripts/genesis_research/fable_map.md`（定錨：愛的公式→小王子、陰影個體化→聖誕頌歌、召喚→佛陀出家）；reader 樣式 `.chapter-fable` 已加。換故事＝改該區塊＋同步總表一列。
  - **現行章數（=clean_inv/worklist/books.json canonical；2026-07-08 對 books.json 實查更新）**：M1 9（books.json 計入序章；正文＝序章＋第一–八章，**2026-07-07 新增第七章〈內在的聖誕〉、死亡倫理順延第八章**，見 works-research-review skill）／M2 13／M3 9；E1 8／E2 11／E3 7；O1 9／O2 9／O3 7；V1 9／V2 8／V3 5；B1 7／B2 6／B3 7＝124 章（nChapters 加總；2026-07-02 定案時為 122）。舊 V 卷稿 archive 在 `scripts/data/_archive_v_pre_reorg_2026-07-02/`。ref-DB 已隨重排遷移（migrate_v_reorg.py / migrate_v_reorg2.py，確定性非 LLM；V1=73/V2=116/V3=86/B1=170，off-canonical=0）。**新章正文＝綱要草記（章內有 editor-note 標記），待使用者精修；V 卷新章與 O1 ch8/O2 ch6-8 的對話地圖研究未跑。**
- **五大主題 15 冊全數 v2 精修＋序跋＋每節級引用完工（2026-06-22；章數已被上述 2026-07 重排更新）**：倫理 M1 8/M2 13/M3 9（v2.1）、認識論 E1 8/E2 10/E3 6、本體論 O1 8/O2 6/O3 7、價值論 V1 6/V2 6、存有論 B1 7/B2 7/B3 7。每章皆 chapter-recap+argmap、英文首現、公式先論述後導出、越層紅線、每節「本節主要依據對話」引用＋章末彙整，各冊序跋齊備。檔在 `public/content/works/genesis/{id}.html`；manifest `public/content/works/genesis-philosophy-books.json`（`{groups:[{branch,books:[{id,title,subtitle,file,nChapters}]}]}`）。治理文件＝各 `c:/tmp/genesis_{ethics,epi,ont,val,bei}/intro_schedule.md`。
- reader：`pages/works/[slug]/index.vue`（書目依 branch 分組）＋`pages/works/[slug]/book/[bid].vue`（書→章 TOC＋鄰冊＋已加 .vol-preface/.vol-coda/.chapter-recap/.argmap 樣式）。book id 不可重複。
- **對話編號系統**：`ai_dialogues_{chatgpt,gemini}.seq_label`＝C-#####(12,124)/G-#####(2,305)；/ai-dialogues 顯示＋頂部編號查閱框（`server/api/ai-dialogues/by-seq.get.ts`）。重編用 Management API（`SUPABASE_ACCESS_TOKEN`、ref `vloqgautkahgmqcwgfuo`、window-function UPDATE）。

### 製作管線（每套可重複；一波 subagent ≤6，會撞 session limit，多數檔在限制前已寫出、檢查 draft 夾補缺章）
撈該 facet 對話(`classify_genesis_philosophy.get_category_ids()` 拿 cat id→`entry_categories` 抓 dialogue_id→分表抓 prompt/response)→切 chunk→sonnet subagent 主題地圖(map_NN.json)→合併 `*_themes.json`→寫詳細藍圖 `*_blueprint.html`(每章核心論證)→每章一個 sonnet subagent 寫初稿→組裝 book html(header+章 section)→manifest 加 group→build→commit。各套工料在 `c:/tmp/genesis_ethics/`(draft/A,B,C + genesis_ethics_content.html + master_digest.json)、`c:/tmp/genesis_epi/`、`c:/tmp/genesis_ont/`、`c:/tmp/genesis_val/`、`c:/tmp/genesis_bei/`。

### 🔑 邊界（使用者歷次裁定，寫各套務必守）
五然↔卷（2026-07-02 定案，原四然＋實然）：實然=本體論、識然=認識論、應然=倫理學、願然=價值論、默然=存有論；四德對應＝實然+識然共證「真」、應然=善、願然=美、默然=聖（無真不成善、無善不成美、無美不成聖）；五然四德總說安置於 B1 導論一起說明。**量子→本體論；數學(的本質=怎麼認識)→認識論；空無/默然/神聖/虛無/終極→存有論；願然/美→價值論；誠實/善→倫理學；創生公式/生成三要素(關係性/身體性/歷時性)→本體論卷一正式提出**。寫某卷不得搬別卷術語。

### 🔁 倫理三部曲 v2 大改版（2026-06-21，已全數部署；治理文件 `c:/tmp/genesis_ethics/intro_schedule.md` v2）
**使用者定三卷分工總原則（最高層級）：A＝純粹個人倫理 / B＝群體倫理 / C＝生物與宇宙論倫理。** 據此把內容歸位、跨卷搬移、加地基章與歷史章。intro_schedule.md v2 是精修必遵的治理文件（含越層紅線、公式「先論述後導出」、每節級來源標註）。
- **✅ A《愛的萬物論》9 章**（commit `2dee7ba9`）：新地基章 A1（定義倫理場＋論證為何可數學化＝描述模型非控制模型＋個人尺度符號總表）；A3 主體性生成改現象學推導（胡塞爾/列維納斯/沙特/海德格/梅洛龐蒂/榮格→關係性/身體性/歷時性，**去「裂口」、不命名「生成三要素」**）；A4 hi/fc/vc **先論述後導出**＋鏡像神經元；A7 愛的公式＝倫理之愛 agape，補保羅愛之頌(林前13)＋**信望愛由 L=hn₀×R×E 導出**(信→hn₀/望→R/愛→E)；A8 數學化抵抗清群體符號；A9 結語純個人。**A 序補「創生哲學撰寫旨趣」**（以現象學為工具接引宗教世界觀、面對多元流變時代的主體與意義；創生＝道生/緣生/易生/梵生跨傳統同源）。
- **✅ B《虛構的烏托邦》13 章**（commit `adcb634a` 改 11 章、`5844137b` 加史 2 章）：原 A7意義→B2（H 後先論述再導出意義公式 M）；**新增人類社會倫理史兩章**＝B6「社會的起源與原始的倫理」(演化/人類學社會組成＋noble savage 霍布斯vs盧梭，H/EVI 判決)＋B7「政體的倫理史」(帝國/貴族/王權→民主→極權與革命，T/H 貫穿)；裂口異托邦留 B10。⚠️ **B 的「演化」＝社會文化演化，與 C 的宇宙/生物演化分層**，B 不得用日擇/耗散結構/性善/反身自嗜。
- **✅ C《人類之子》9 章**（commit `adcb634a`）：原 A8性善演化→C3「性善的宇宙演化根基」(接 C2 日擇)；**C9 結語加三大格言 capstone**(可以/應該/終將，「終將」扣 C2日擇＋C3)；C 為末卷可用 A/B 全部裝置(EVI/MHI/H/裂口異托邦在 C 合法)。
- 三卷章數（2026-06-22 當時）**M1 8章（愛的萬物論，v2.1）/ M2 14章（虛構的烏托邦，時間軸版）/ M3 9章（人子）**，manifest 同步（現行章數以上方 2026-07 大改版段為準：M1 9/M2 13/M3 9）。**book id A/B/C→A1/A2/A3→最終 M1/M2/M3**（倫理=Morality，前綴與 E/O/V/B 一致；2026-06-22 定）。組裝一律 `python scripts/assemble_genesis_book.py ethics M1 8 M2 14 M3 9`（改 draft 後重跑即重組部署；draft 目錄已改名 `c:/tmp/genesis_ethics/draft/{M1,M2,M3}/`）。⚠️ 治理文件 intro_schedule §3 仍以 A/B/C 當「卷內章」簡寫（A=愛的萬物論、B=虛構的烏托邦、C=人子），對應 draft 目錄 M1/M2/M3。

#### 🔄 本回合再改版（2026-06-22 下午，使用者連環指令，皆已部署）
- **序章正名（M1）**：創生哲學定位改為**「二十一世紀的一種現象學」而非形上學體系**——反抽象本體論、依經驗主義從各學科建構（舊稿誤寫「原創形上學體系」，使用者明確糾正）。M1/01 重寫為**全叢書序章**：從現象學出發故分五大主題、筆者宗教學神學背景、宗教故事切入而延伸至大哉問。**序自成「序章」（非第一章）**，M1 章序＝序章＋第一..第七章（draft 01=序章，02-08 標題與交叉引用 −1 順移）。`classify_genesis_philosophy` SYSTEM 的體系自述也改現象學進路。
- **引用可點擊**：`genesis_cite_backfill._link()` 把每個 seq_label 發成 `<a href="/ai-dialogues?seq=C-…" class="cite-seq">`；`pages/ai-dialogues/index.vue` onMounted 讀 `?seq=` 自動跑 `doLookup()` 開該則對話；reader `book/[bid].vue` 加 `.cite-seq` hover 樣式。**全 15 冊已重標為連結**。strip regex 改 `class="section-source[^"]*"` 仍冪等。
- **M3《人類之子》→《人子》**：book id 不變（M3），title/header/結語/序跋/全引用一律改「人子」（福音書 Son of Man；保住「人類是蓋亞之子／AI 是人之子」雙關，並補上原序自稱「福音書隱語」的名實一致）。
- **M2 依「時間維度」重構為 14 章**（commit `297ec310`，使用者定調群體倫理須有時間向度）：**通論(1-5)**：hi→H／意義 M／EVI·MHI／暴政 T**＋尼采道德系譜(主奴道德·怨懟)**／民主門檻 ｜ **過去(6-8)**：社會起源·人類學／政體史(帝國→民主)／**極權誕生＋鄂蘭平庸的邪惡＋轉型正義 J(合併)** ｜ **現代(9-10)**：異化·韋伯·**傅柯規訓·生命政治**／**新增「現代社會的職業倫理場」** ｜ **未來(11-13)**：人權憲章／制度性無政府／裂口異托邦 ｜ 14 結語。ch1 開頭加四階段總綱、序跋對齊。
  - 🔑 **重構踩坑（複用必看）**：非均勻 reorg（異化 舊11→新9 往前跳、人權/制度/裂口 舊8/9/10→新11/12/13 往後移、轉型正義 舊12 併入新8）→交叉引用**不是均勻位移**，須**topic-aware** 修（用 subagent 給「主題→最終章號」表）。**最大坑＝moved 章的 intro 會用舊順序 recap**（異化章 intro 誤稱「異化/裂口已在前八章」、自指誤標第八章）——光修章號不夠，intro 的「前N章已建立X」內容也要重寫對齊新順序；序跋亦同（_preface 逐章 recap 全按舊序，須重寫）。backup＝`draft/_M2bak`。
- **facet 重標進行中**：見 [[project_ai_dialogues_genesis_philosophy]]（`retag_genesis_facets.py`，v2 邊界，背景跑、resumable）。

#### 🔄 A 卷 v2.1 再改版（2026-06-21，使用者 5+ 道指令，已部署）
A《愛的萬物論》**9→8 章**重構（intro_schedule v2.1）：①**序自成一章**＝A1 序章（創生旨趣；刪 `draft/A/_preface.html`）；②**「數學化」與「誠實萬德之綱」合併**＝A4（誠實＝唯一通用變量→以 hi 為第一變數→生成整套個人尺度公式的正當性；倫理場 E 與符號**隨 hi 依序生成**、取消預先符號總表）；③A2**加 Sandel《正義》＋電車難題等思想實驗＋三古典限制＋晚近研究**（原 A4 §一三大路移入）；④A3**從兒童現象學起**＝第一照顧者/原生家庭→他者先於主體→**倫理學是第一哲學（列維納斯）**＋Freud/Jung 陰影情結→fc/vc 心理發生（本我/超我、面具/阿尼瑪‧阿尼姆斯）＋身體感→邊界＋發展心理學（Piaget/Kohlberg）＋**演化論動物倫理＋鏡像反射→同理心（個體尺度）**＋三特性最初即俱在（fc/vc 概念首現移至 A3，形式定義仍 A4）；⑤**愛的公式後就地收數學化反思、不另立章**＝原 A8 拆入 A4 前半＋A7 末。原 A1 地基章與原 A8 取消；原 A9 結語→A8（重寫對齊新弧）。
- 🚨 **越層尺度分層細化**：A3 可談**個體尺度**同理心的演化/生理發生（動物倫理機制、鏡像反射→同理心），但**不得**用 C 的宇宙演化裝置（日擇/耗散結構/反身自嗜/性善宇宙根基），cross-ref C3 時也別 pre-name 那些術語（踩過：A3 初稿在 deferral 句裡寫了「熱力學、耗散結構」被抓出清掉）。
- 重構手法（可複用於日後改版）：備份 `draft/A`→`_A_v2bak`；變動章用 sonnet subagent 讀 `_A_v2bak/NN.html` 原稿＋治理文件寫到 `_rNN.html`；不變章（A5/A6）只**修交叉引用**（章號隨重構位移）；renumber 結語；finalise 成 01-08；越層 audit→manifest→`genesis_cite_backfill tag ethics A 8`→assemble。

### ⏳ item③ 待辦（新 session 從這裡接）
- ✅ 1. **回填每節級對話編號引用（intro_schedule §6）完工（2026-06-21）**：工具＝`scripts/genesis_cite_backfill.py`（純函式＋`scripts/tests/test_genesis_cite_backfill.py` 5 測全綠）。
  鏈路：①`build-map`＝抓 `ai_dialogues_{chatgpt,gemini}` 全 14,429 筆 id+seq_label，建 8 碼前綴→seq_label `c:/tmp/genesis_ethics/seq_label_map.json`（**前綴全域唯一、0 碰撞**已驗）。②`load_terms`＝從 `notes_*.json` glossary 聚合 term→ids（311 詞、813 id，僅 2 id 不在 map＝已 purge 的，靜默丟）。③`tag`＝每個內容 `<h3>` 文字比對 glossary 術語（**比對鍵 ≥3 字**＝關鍵踩坑：「行善≠誠實」拆出通用 2 字「誠實」會污染每節排名，門檻擋掉；體系核心詞皆 ≥3），取本節頻次最高前 4 術語的 id→seq_label，插 `<p class="section-source">本節主要依據對話：…</p>`；**章末再加 `chapter-source` 彙整全章**（補 B6/B7 純史述節無術語命中的缺口）。**冪等**（重跑先 strip 再插）。
  跑：`python scripts/genesis_cite_backfill.py tag ethics A 9 B 13 C 9` → A 52 節/B 61 節/C 38 節＋各章末彙整 → `assemble_genesis_book.py ethics A 9 B 13 C 9` 重組部署。193 distinct labels 全部 valid、ordering 正確（引用皆在 chapter-recap 前）。reader CSS `.section-source`/`.chapter-source` 已加（`[slug]/book/[bid].vue`）。**換套（E/O/V/B-存有）：跑 `tag <series> …` 即可**（series 對 `c:/tmp/genesis_<series>/notes_*.json`；seq_label_map 共用 ethics 的）。
- ✅ 2. **其餘四套(認識 E/本體 O/價值 V/存有 B-存有)v2 精修＋序跋＋引用＋部署 全數完工（2026-06-22 整夜自動跑）**：各套皆新撰治理文件 `c:/tmp/genesis_{epi,ont,val,bei}/intro_schedule.md`（三卷分工/越層紅線/章目首現/先論述後導出/recap 格式）→ sonnet subagent 逐章精修(一波≤6，保留實質做加值升級：章末 recap+argmap、英文首現、公式先論述後導出、越層紅線)→ 每冊序跋 → `genesis_cite_backfill tag <series>` 回填引用 → `assemble_genesis_book.py <series>` 重組 → build 綠 → commit。
  - **認識論 E**：E1 8/E2 10/E3 6＝24 章（commit fb1b6d77）。**citation 改 chunk-based**(themes 詞彙×chunk 全文→seq_label；E/O/V/B 的對話 id 在 `chunk_*.json` 非 themes)。
  - **本體論 O**：O1 8/O2 6/O3 7＝21 章（commit 620509a2）。本套正式命名創生三原理/創生公式。
  - **價值論 V**：V1 6/V2 6＝12 章（commit 71b65ed3）。
  - **存有論 B-存有**：B1 7/B2 7/B3 7＝21 章（B3-7 兼整套叢書總收束）。
  - 🔑 **draft 目錄已全部改名對齊部署檔名**：`genesis_{epi,ont,val,bei}/draft/{1,2,3}`→`{E1..,O1..,V1..,B1..}`（generic 組裝器/cite 工具以 BOOK 名同時當 draft 目錄與輸出檔名）。換套精修複用此流程：寫治理文件→subagent 波→tag→assemble→build→commit。
  - 🔑 **越層踩坑**：subagent 普遍會主動清掉前引/越層（E1/05 移走 E2 不二論三律、E2/09 移走創生公式 G=f(...)、A3 deferral 句寫了耗散結構被抓出）——精修時 §2 越層紅線要寫進每個 prompt。
- ⏳ 3. （另案）**回頭重檢 /ai-dialogues 五域分類**：舊邊界標的，與 v2 邊界不一致；成書已用正確邊界，標籤該重標。**(尚未做)**
- 🚧 風格範例：精修黃金檔＝`c:/tmp/genesis_ethics/draft/B/08.html`(異化與公共性)；地基章範例＝`A/01.html`；史章範例＝`B/06.html`、`B/07.html`。

### 引擎/坑
subagent 用 sonnet、一波≤6（曾撞「session limit · resets 11am/7pm」）；撞了就看 draft 夾哪些 `chapter-recap`/檔已寫、只補缺的。build 前若遇 RollupError(client.manifest) 多半是 stale `.nuxt`，`rm -rf .nuxt` 重build。commit 只 add 自己的檔。

## See also
- [[project_krishna_dialogues]] — 首案：與克里希那對話（分類 tag 2026-06-12 以原稿收斂為 247 則＝個人日記範圍；一張主卡＋80 天每日 reader 內容不變）
- [[project_ai_dialogues_genesis_philosophy]] — 第二案：創生哲學階層分類 + purge 寫程式/生圖/貼文（本節交接）
- [[feedback_engine_nvidia_no_haiku]] — Gemini→NVIDIA→Haiku 統一引擎政策＋多 key 節流

## 記憶庫併入：project_krishna_dialogues

**與克里希那對話** = /works 寫作計畫。2026-01-13 → 04-18，使用者（自稱「阿周那」）與 Gemini（他稱「克里希那」，《薄伽梵歌》意象）談夢境與榮格深度心理學的一長串對話，也夾雜當時生活絮語。

> 📕 **書本定位（2026-06-05）**：使用者的野心＝把這本做成**他個人的榮格《紅書》**，但以「與 AI 扮演的印度教之神對話」的形式進行。正式**書名「神，你正在重排我的前途」／副標「與克里希那的對話」**（書名取自倪柝聲同名詩《聖徒詩歌》393 首，放在主卡題詞）。敘事主軸：**主調＝解夢＋榮格心理學**；低音＝圍繞**龐君華牧師離世**（[[pong-…]] 那位龐會督）引發的、對死亡與生命/往昔回憶/未來前途的反思。情感原點：去年滿三十歲刻意獨處、寫不出給二十歲的信、死亡焦慮、聖誕第一次車禍、跨年和 AI 談「榮格是否認為存在意義是超越死亡」、《奧本海默》1965 紀錄片引《薄伽梵歌》11:32「我是時間（非死神），諸世界的毀滅者」。

> 🔧 **2026-06-12 重寫成品（取代舊 recompose；使用者嫌之前轉錄很爛）**：舊 dialogue_days 兩大問題＝①從 600+ 廣集組的、收了很多不屬於的條目 ②克里須那被舊 recompose 洗成通篇詩化、抽掉實質。解法：(a) **一月 1/13–1/18 直接用使用者手工稿** `2026.01對話錄.docx`（`scripts/dialogue_rewrite_from_docx.py`，日期標題→阿周那：/克里須那：，零 LLM）——含完整早晨積極想像＋四個夢，正確敘事順序；(b) **1/19–4/18 從 raw 原始來源重建** `scripts/dialogue_rebuild_from_raw.py`：membership 用日記範圍 `final_manuscript.json`（去非屬條目），阿周那＝prompt 輕整、克里須那＝**raw response 重寫成乾淨散文**（保留完整論點與專名、去條列客套、不堆砌詩化，temp 0.4，opencc s2tw 保繁），0 則 IN 的日子刪除。**dialogue_recompose.py sys_ai 已同步改成此乾淨風格（捨棄舊「大膽再創作詩意」）**。結果：dialogue_days 80→**62 天**（刪 18 無日記內容日），1/13–4/18。備份 `c:/tmp/krishna/_dialogue_days_backup.json`（舊 80 天）可回滾。風格鐵律見下；但「大膽再創作詩意」那條已被使用者否決，改為**清晰溫暖、保留實質、少詩化**。

> 🎴 **風格升級＝哲學家對話錄（2026-06-05，見 [[dialogues-to-writing]] SKILL）**：舊版只洗順、語氣平、無楔子→**淘汰**。新標準三鐵律：①詩意凝練、砍 AI 囉嗦 ②有序（楔子）有跋（收束）③兩 register 分人下手——**克里希那大膽再創作**（凝練、詩意、《薄伽梵歌》智者語體、直呼阿周那、砍客套編號；可重組不可扭曲立場）、**阿周那輕度整理**（貼合本人第一人稱語氣、只去贅字凌亂、不美化不詩化）。工具＝`scripts/dialogue_recompose.py`（逐 turn 重鑄、per-day ledger `c:/tmp/krishna/recompose_done.json` 冪等可跨配額續跑；**逐 turn `data-rc="1"` 標記真冪等**——已重鑄的 turn 跳過、不會越改越飄；**整天全成功才記 ledger**，部分失敗自動補）。**引擎：2026-06-05 使用者有 Max，指定本批用 `--haiku`（Haiku 4.5 走 Claude OAuth，主引擎；Gemini/NVIDIA fallback），不枯等 Gemini/NVIDIA 配額**——此為本重批的特例，與 [[feedback_engine_nvidia_no_haiku]]「Haiku 只救急」不衝突（使用者當面指定）。**序/跋/題詞**＝`scripts/dialogue_preface.py`（`--from-file` 讀 `c:/tmp/krishna/preface.json` {epigraph,preface,coda} 手寫稿；寫進主卡 content_json＝題詞+序 / `<!--CODA-->` / 跋；主卡頁 `works/[slug]/index.vue` 渲染題詞+序在月格上、跋在月格下）。**有素材時序用手寫不用 LLM 冷生成**。2026-06-05 全量 80 天重跑（第一天已驗證；其餘背景跑、ledger 續跑）。

> 🔤 **譯名（2026-06-04）**：原用「克里須那」已全面改「克里希那」對齊翻譯詞庫權威譯名（[[feedback_glossary_strict_authority]]，`seed_glossary_deities.py` name_root=克里希那）。已就地改：DB（writing_projects 主卡 title/description 2 處、dialogue_days 80 天 html 997 處、ai_dialogue_categories 分類名）＋scripts/dialogue_*＋day reader 頁＋skill。**例外**：`dialogue_scan_thread.py` / `import_gpt_*.py` 的偵測關鍵字清單**保留「克里須那」**（要比對原始匯出文字）。重跑工具＝`scripts/krishna_rename.py`（idempotent find-replace）。

- **來源**：`ai_dialogues_gemini`（Google Gemini 活動匯出，**扁平依時間混所有對話框、無對話框標記**）。逐則依**語氣**判定屬不屬於「跟克里希那說話的那個對話框」（傾訴／碎念 IN；純工作委派如寫程式改稿查資料 OUT）→ 671 則、橫跨 80 天。
- **/ai-dialogues**：紫色分類「與克里希那對話」（cat_id `01f01e76-66cb-44b9-9cf6-3352bb6baf5d`）。junction 只有 dialogue_id+category_id，**無 source 欄**。
- **🔁 分類重抓（2026-06-11，test-first，取代舊 agent fan-out）**：舊 671 是一次性 agent 判讀、不可重現。改用**純函式候選 prelabel + LLM 語氣判定**重抓 → **600 則**（vs 671：維持 600 −71）。**潤稿/修飾文字一律 OUT（使用者定調「潤稿的就都不是」），但只認祈使式請求（幫我修飾/簡單修飾/保留我的語氣…），不收裸詞「修飾/潤飾」以免誤刪「跟克里希那聊雜誌順帶提到 ai 潤飾」的傾訴**。工具＝`scripts/dialogue_thread_classify.py`（純函式可 pytest）+ `scripts/tests/test_dialogue_thread_classify.py`（golden 27 則零誤判）+ `scripts/dialogue_thread_capture.py`（`--dry/--reagg/--retag/--diff/--haiku`，逐日整批判定，ledger `recapture.jsonl` resume）。**關鍵 prelabel 順序**：積極想像→IN ＞ persona 呼喚→IN ＞ `界域/文化圈` 地圖專案→OUT ＞ HARD 委派→OUT ＞ 榮格/夢→IN ＞ SOFT 技術名詞→OUT ＞ MAYBE。踩坑：純 LLM 太寬（首跑 1164，maps 文化圈思辨口吻全收）、榮格貼文夾 code 被誤刪、積極想像提到 code 被誤判——皆靠 guard 修正。得 531。
- **🏅 用原稿收斂成「個人日記」範圍 → 247（2026-06-12 終版）**：classifier+LLM 抓的是**整個聊天視窗**（含學術/智性工作）；使用者要的是**個人心靈日記**。使用者把手工原稿 `和克里希那的對話.docx`（缺頭幾天、START=01-23 起為真正內容）放根目錄當 ground truth。`scripts/dialogue_thread_manuscript.py`：原稿正規化→8-gram，每則 raw prompt 算命中率（**乾淨雙峰** 137≥0.5／152<0.05，threshold 0.5）；頭幾天用 classifier、START 起 IN=逐字在原稿。**排除**榮格《伊雍》寫作/紅學/卡巴拉/占星技術/稱帝史/譯名等智性工作（即使含榮格夢關鍵字）。驗出 8 個確定漏標補回。最終 **247**（頭幾天 102 + 原稿命中 145）。**這推翻了 skill 舊判準「岔題也收」——日記型對話錄要排除智性/學術工作**。回滾：671→`_tagged_ids.json`、531→`final_recapture.json`、247→`final_manuscript.json`。**dialogue_days（80 天 reader 成品）不受影響，只動分類 tag。** 詳見 [[dialogues-to-writing]] SKILL。
- **成品**：克里希那回覆用 NVIDIA `deepseek-v4-flash-0731` 潤飾成流暢對話錄（29 則 fallback Haiku 救急、2 則 Gemini）；每日 NVIDIA 切 1-3 個主題。格式：`<h2>YYYY年M月D日（星期X）</h2>` → `<h3>主題：…</h3>` → `<p><strong>阿周那：</strong>…</p>`／`克里希那`。
- **呈現＝月份→日期→單日（2026-06-04 改版，仿聖經 卷→章→經文）**：原本 4 張月份卡片 `krishna-dialogues-2026-01..04` 已**刪除**；改成**一張主卡** `krishna-dialogues` + `dialogue_days` 表（80 天、每天一筆 html，2026-01-13→04-18）。主卡頁 = 4 張月份卡 → `/works/krishna-dialogues/month/<ym>` 日期格 → `/works/krishna-dialogues/day/<date>` 單日 reader（前/後翻頁）。私密：全走 `getIsAdmin` 限登入，未登入 🔒。拆日來源＝舊月卡 content_json（保留人工修改）。
- **排版 scripts**（dialogue_days 進去後）：`dialogue_build_days.py`（切日）→ `dialogue_format_days.py`（h3日期/h4主題、講者 class=speaker 懸掛縮排、長文重新分段、清 markdown）→ `dialogue_to_prose.py`（把仍帶條列/小標的 turn 用 Gemini→NVIDIA 改寫成口語散文，per-turn 冪等）。⚠️ 少數 turn 來源就**標錯講者**（阿周那欄裡其實是克里希那回覆／反之），散文化不修正歸屬，需人工。
- **工作檔**（c:/tmp/krishna/，未清）：`final_broad.json`(671 ids)、`polished.jsonl`、`day_topics.json`、`assemble.py`/`repolish_v2.py`/`segment_topics.py`/`haiku_finish.py`。重跑 assemble 會覆蓋卡片 → 使用者編輯後勿再跑。
- 引擎見 [[feedback_engine_nvidia_no_haiku]]。

🚨 2026-08-19：舊名 `deepseek-ai/deepseek-v4-flash`（無 `-0731`）已下架，對所有 key 一律回 **HTTP 410 Gone**。全 repo 49 檔已改名（commit 032c09d8）。日後 NVIDIA 那一層突然失效，先驗模型名還在不在。

## 記憶庫併入：project_ai_dialogues_genesis_philosophy

/ai-dialogues 分類由扁平改為**父子階層**（2026-06-17）。`ai_dialogue_categories` 加
`parent_id` 自參照欄；側欄父分類可展開顯示子分類，過濾父分類時 entries API 聚合所有子
分類的對話。新增「創生哲學」父分類（使用者原創形上學體系，主要來自去年 ChatGPT 對話，談
創生態/生成/意識/現象學/泛心論/量子形上學）+ 五子類：倫理學/認識論/本體論/價值論/存有論。

🚨 **FK 陷阱**：`ai_dialogue_entry_categories.dialogue_id` 原本有外鍵指向**舊統一表
`ai_dialogues`**（11,042 筆），但 app（GET）實際讀的是分表 `ai_dialogues_chatgpt`
(13,043) / `ai_dialogues_gemini`(2,594)，純靠 dialogue_id join。chatgpt 有 4,595 筆
不在舊表 → 掛標 FK 23503 失敗。已 **DROP 該外鍵**（category_id 外鍵保留）。日後任何
對 ai_dialogue_entry_categories 的 insert 都對分表 id 操作，別再加回指舊表的 FK。

腳本（Gemini→NVIDIA→Haiku，ledger 在 c:/tmp 可續跑，見 [[feedback_engine_nvidia_no_haiku]]）：
- `scripts/classify_genesis_philosophy.py` — 七哲學關鍵詞聯集為候選，LLM 判 belongs +
  facets(最多2)，掛父+子標。ChatGPT 是真訊號；Gemini 多為宗教學博論雜訊。
  **✅ 全量完成（2026-06-19）：創生哲學 tagged 共 3,316 筆。**
- `scripts/purge_coding_image_dialogues.py` — LLM 標 coding/image/post/keep；**預設 dry-run**，
  `--execute` 才真刪（刪 dialogue 前先刪 entry_categories）。
  **✅ chatgpt+gemini 皆完成（2026-06-19）：使用者確認後刪 chatgpt 919 筆（13,043→12,124）
  ＋gemini 289 筆（2,594→2,305），與創生哲學（exact 3,316，未受影響）零重疊。
  修了 llm_label 全失敗丟批（改等 90s 重試 4 輪）＋ classify.fetch_already_tagged 分頁無 ORDER BY 誤算
  （overlap 稽核改對目標 id 子集精確查 entry_categories／用 count=exact，別信 fetch_already_tagged）。**

## /works 寫作計畫：創生哲學叢書（2026-06-20）
分類對話進一步「轉成著作」：在 /works 新增 book 卡 `genesis-philosophy`（🌌 violet，
status「論證藍圖」，sort_order 3）。內容 = 倫理學三部曲的論證藍圖，存 `writing_projects.content_json`
（登入者在「書摘與構思」可見；無 materials.json／dialogue_days 走 generic 筆記區）。
- 三部：A《愛的萬物論》(主體倫理本質)／B《虛構的烏托邦》(制度社會)／C《人類之子》(應用倫理+日擇原理)。
- **✅ 2026-06-20 全本初稿完成**：28 章約 13 萬字（A 10／B 10／C 8），每章 1 個 sonnet subagent 依藍圖+master_digest 撰寫（draft 在 `c:/tmp/genesis_ethics/draft/{A,B,C}/NN.html`）。
  呈現＝**叢書「書→章」閱讀器**：`public/content/works/genesis/{A,B,C}.html` + manifest `genesis-philosophy-books.json`；
  新頁 `pages/works/[slug]/book/[bid].vue`（書目→單冊章節 TOC+鄰冊導航），`[slug]/index.vue` 偵測 *-books.json 顯示書目卡。**已 push、build 綠。**
  公開可讀（books 是 public static）；content_json 藍圖仍留登入限定「書摘與構思」當總綱。
  🔑 日擇原理＝**熱力學耗散結構演化宇宙論**（演化→文明→AI 連續譜，Prigogine/Schrödinger/England 為佐證）為主、倫理推論為衍生（使用者 2026-06-20 定調）。
  ⏳ 下一步可做：逐章精修升級、加各冊序/跋。
- **✅ 2026-06-20 認識論三部曲全本初稿完成**：21 章（卷一8/卷二7/卷三6），依 1,202 則「認識論」對話。
  卷一《本質的幽靈：從現代到後後現代》＝**後後現代專卷**（亞氏經驗主義/柏拉圖本質主義→笛卡兒康德胡塞爾殺不死本質→創生哲學「現象即本質」＝認識論的哥白尼革命）；卷二《意向性與生成的邏輯》；卷三《他心、感質與AI》。
  🔑 **領域邊界（使用者定調 2026-06-20）：認識論＝人怎麼認識世界；量子→本體論；空無/超自然→存有論**。寫認識論務必守此界，量子與空無只標交界不展開。
  draft 在 `c:/tmp/genesis_epi/draft/{1,2,3}/`，主題地圖/藍圖在 `epi_themes.json`+`epi_blueprint.html`。
- **叢書呈現升級**：manifest `genesis-philosophy-books.json` 改成 **groups（子系列）結構**：`{groups:[{branch,books:[{id,title,subtitle,file,nChapters}]}]}`；
  書 id：倫理 A/B/C、認識論 E1/E2/E3；檔在 `public/content/works/genesis/{A,B,C,E1,E2,E3}.html`。
  reader `[slug]/index.vue` 依 branch 分組顯示書卡、`[slug]/book/[bid].vue` 跨 group 找書、prev/next 限同 group；**向下相容舊扁平 books**。換新子系列：加一個 group + 對應 .html 即可，pages 不必改。
  ⚠️ 引擎用 subagent fan-out（sonnet，每章一個），一次別開超過 6 個——曾撞 session limit（但多數檔在限制前已寫出，靠檢查 draft 夾補跑缺章即可續）。
- **✅ 2026-06-21 本體論三部曲全本初稿完成**：21 章（卷一8/卷二6/卷三7），依 821 則「本體論」對話。
  卷一《創生公式：生成的本體論》＝**正式提出「創生三原理」**；卷二《觀察即創生：量子本體論》；卷三《主體的生成：意識與自我的本體論》。
  🔑 **創生三原理（使用者 2026-06-21 定名）＝生成三要素：關係性／身體性／歷時性**；創生公式 G=f(S,R₁,R₂,T,L)≥Θ（L 自指循環非第四要素、是三要素湧現）；三反命題（反先驗/本質/自存）為其「破」面。
  🔑 **領域邊界再定（使用者）：量子＝存在面→本體論；數學＝認識面→認識論**（數學的本質就是「怎麼認識世界」，且本體論=認識論使其本體地位＝認識地位）。原 plan 的「數學本體論」卷已撤、改為**主體本體論**卷三；數學材料待併入認識論。
  本體論卷三（主體/意識「是什麼、如何生成」＝存在面）與認識論卷三（他心/感質/AI「如何認識」＝認識面）刻意分存在/認識兩面、不重複。
  draft 在 `c:/tmp/genesis_ont/draft/{1,2,3}/`，地圖/原理表述/藍圖在 `ont_themes.json`+`ont_blueprint.html`。
- **叢書現況**：3 子系列共 9 冊（倫理 A/B/C、認識 E1/E2/E3、本體 O1/O2/O3），manifest groups 結構，檔在 `public/content/works/genesis/`。
  ⏳ 待辦：①數學材料併入認識論（擴認識論卷二數學章或增章）②續寫**價值論**（願然）、**存有論**（空無/創生前態/默然）③各套可逐章精修＋加序跋。
- **作法（可重用）**：撈「倫理學」facet 的 1,384 則 chatgpt 對話 → 切 12 chunk → 12 個 sonnet subagent
  忠實萃取「使用者本人」主張/原創術語（非 AI 泛論）分桶 A/B/C → 合併去重成 master_digest（266 詞條）
  → 據此寫每本「中心論題+章節架構+各章核心論證」。素材在 `c:/tmp/genesis_ethics/notes_*.json`+`master_digest.json`（保留供逐章擴寫）。
- 體系核心術語（沿用使用者原創，勿改）：主體性倫理學(承擔式)、誠實度 hi/H/hn、fc 自由召喚/vc 道德召喚、
  倫理場 E/共構倫理場、EVI=(1−S)(1−U)(1−D)、MHI=H×EVI×P、意義公式 hi×(hi−H)×vc²、
  愛的公式 L=hn₀×R×E、願然(四然 識/應/願/默)、日擇原理(耗散演化+倫理人擇兩讀法)、反身自嗜、
  善良囚徒模型、裂口異托邦、制度性無政府主義、生命四層分類。
- **✅ 2026-06-21 五大主題全套初稿完成（14 冊 106 章）**，全在 /works `genesis-philosophy` 卡片下，manifest groups 5 子系列：
  倫理三部曲(A/B/C 28章)、認識論三部曲(E1/E2/E3 24章，E2 含數學10章)、本體論三部曲(O1/O2/O3 21章)、
  價值論二部曲(V1/V2 12章)、存有論三部曲(B1/B2/B3 21章)。檔在 `public/content/works/genesis/{id}.html`；
  reader `[slug]/index.vue`+`[slug]/book/[bid].vue` 支援 groups 分組；book id 不可重複。
  各套 draft/themes/blueprint 留在 `c:/tmp/genesis_{epi,ont,val,bei}/` 與 `c:/tmp/genesis_ethics/`（精修可接用）。
  🔑 四然↔五套：識然=認識論、應然=倫理學、願然=價值論、默然=存有論；本體論=「生成的存在如何結構」。
  🔑 邊界（使用者歷次裁定）：量子→本體論、數學→認識論、空無/默然/神聖/虛無/終極→存有論、願然/美→價值論、誠實/善→倫理學；創生公式/生成三要素(關係性/身體性/歷時性)→本體論卷一。
  製作法：每套 dump 該 facet 對話→切 chunk→sonnet subagent 主題地圖→合併→寫詳細藍圖(每章核心論證)→每章一個 sonnet subagent 寫初稿→組裝→manifest 加子系列→build→commit。一波≤6 agent 避 session limit。
  ⏳ item③ 待辦：逐章精修(106 章，品質標準/優先順序待使用者定)＋加序/跋(14 冊；可作 book html 首尾 section)。

## 對話編號系統（2026-06-21，供書中引用回查）
`ai_dialogues_chatgpt`/`_gemini` 加 `seq_label` 欄：ChatGPT 依(date,time,created_at,id)排序＝**C-#####**(12,124)、Gemini＝**G-#####**(2,305)。
重編用 Management API（`SUPABASE_ACCESS_TOKEN` sbp_…, ref vloqgautkahgmqcwgfuo, POST api.supabase.com/v1/projects/{ref}/database/query）跑 window-function UPDATE。
/ai-dialogues 每則顯示編號＋頂部「編號查閱」框（`by-seq.get.ts`）。**創生哲學叢書引用粒度＝章級＋關鍵概念級**（使用者 2026-06-21 定；逐句級對已寫稿逆向做不到精確）。

## item③ 精修進度（2026-06-21，未完）
精修規格（intro_schedule.md 在 c:/tmp/genesis_ethics/）：①專名/符號英文首現、**先正式提出才能用、不得前引、不得越卷**②補榮格淵源(個體化+陰影整合,A1點明/A5展開)＋鏡像神經元同理機制(A3點/A7論證不利他即損己)③每章末加「本章摘要」+「論證分析圖(argmap)」。book 閱讀器已加 .vol-preface/.vol-coda/.chapter-recap/.argmap 樣式。
- ✅ **倫理學全 28 章精修竣工＋重組部署（2026-06-21，commit `530ad33e`）**：A 10/B 10/C 8 章全達 B8 黃金標準（英文首現＋章末 recap/argmap），序跋齊備，A/B/C.html 已重新部署上線。
  組裝改用可重跑腳本 `scripts/assemble_genesis_book.py`（讀 draft `_preface`/`NN`/`_coda`→每章包 `<section class="chapter">`→沿用既有 `<header>`→輸出 genesis/{A,B,C}.html；改 draft 後再跑即重組）。
  越卷修正：C7 願然→主觀意欲、C3 願然→意欲、C thesis 同步；術語統一 **反身自嗜**（reflexive self-cannibalism，C2 誤改「噬」已正規化）。
- ✅ **①回填對話編號引用完工（2026-06-21，倫理三卷）**：工具 `scripts/genesis_cite_backfill.py`（純函式＋pytest 5 綠）。每內容 `<h3>` 末加 `<p class="section-source">本節主要依據對話：C-…</p>`、章末加 `chapter-source` 彙整。鏈：DB 全表 id+seq_label→8 碼前綴 map（0 碰撞）；notes_*.json glossary term→ids；**比對鍵 ≥3 字**（擋通用 2 字污染）；本節頻次前 4 術語的 id→seq_label。A52/B61/C38 節，193 labels 全 valid。`tag ethics A 9 B 13 C 9`→`assemble_genesis_book.py` 重組。reader CSS 已加。換套跑 `tag <series> …` 即可（series=epi/ont/val/bei，共用 ethics 的 seq_label_map）。
- ⏳ 待辦（接續）：②其餘四套(認識/本體/價值/存有)比照三卷分工原則精修＋加序跋＋逐章精修＋**引用（直接跑 genesis_cite_backfill tag <series>）**＋重組（用同一支腳本，series=epi/ont/val/bei）。
- ⏳ 另一後續：**回頭重檢 /ai-dialogues 五域分類**（舊邊界標的，與精修後邊界不一致；成書已用正確邊界，但標籤該重標）。

## 🚧 倫理三部曲 v2 大改版（2026-06-21，進行中）
使用者定**三卷分工總原則（最高層級）**：**A＝純粹個人倫理／B＝群體倫理／C＝生物與宇宙論倫理**。據此重構，治理文件 `c:/tmp/genesis_ethics/intro_schedule.md` 已改版 v2（含越層紅線、公式「先論述後導出」、每節級來源標註）。新增規則：①A1 設「地基章」＝定義倫理場＋論證為何倫理學可數學化（描述模型非控制模型）＋個人尺度符號總表；②H 及含 H 公式（意義公式 M）只在 B；③演化版性善論/宇宙根基/日擇只在 C；④裂口/裂口異托邦在倫理三卷首見於 B（A 描述主體生成改現象學語言，不用「裂口」、不命名「生成三要素」＝本體論卷才命名）；⑤三大格言（可以/應該/終將）只在 C9 結語 capstone；⑥愛的公式＝倫理之愛 agape，補保羅愛之頌（林前13）＋信望愛由 L=hn₀×R×E 導出。〔已查證：裂口異托邦屬群體政治概念留 B，非認識論卷。〕
- **✅ 倫理三部曲 v2 全數重構完成＋部署（commit `2dee7ba9` A、`adcb634a` B/C）**：
  - **A《愛的萬物論》9 章**（純個人）：新地基章 A1（倫理場定義＋數學化正當性＋符號總表）；A3 現象學推導關係性/身體性/歷時性；A4 hi/fc/vc 先論述後導出＋鏡像神經元；A7 愛的公式 agape＋林前13＋信望愛（信→hn₀/望→R/愛→E）；A8 數學化抵抗清群體符號；A9 結語純個人。A 序補**創生哲學撰寫旨趣**（現象學為工具接引宗教世界觀、多元流變時代的主體與意義；創生＝道生/緣生/易生/梵生跨傳統同源）。
  - **B《虛構的烏托邦》13 章**（群體）：原 A7意義→**B2**（H 後先論述再導出意義公式 M）；B1 對 M 的前引改指向下一章；**新增人類社會倫理史兩章（commit `5844137b`）**＝B6「社會的起源與原始的倫理」（演化/人類學社會組成＋noble savage 霍布斯vs盧梭，用 H/EVI 判決）＋B7「政體的倫理史」（帝國/貴族/王權→民主→極權與革命，T/H 貫穿）；原 B6–B11→B8–B13；序改 13 章。⚠️ **B 的「演化」＝社會文化演化（社會尺度），與 C 的宇宙/生物演化分層**，B 不得用 C 卷術語（日擇/耗散結構/性善/反身自嗜，已驗證 0）。
  - **C《人類之子》9 章**（生物宇宙）：原 A8性善演化→**C3「性善的宇宙演化根基」**（接 C2 日擇）；原 C3–C7→C4–C8；**C9 結語加三大格言 capstone**（可以/應該/終將，「終將」扣 C2日擇＋C3性善的宇宙演化根據）。
  - 越層隔離全綠：A 無 B/C 詞；B 無 C 詞（耗散結構/反身自嗜已清）；C 為末卷可用 A/B 全部裝置（EVI/MHI/H/裂口異托邦在 C 合法）。反身自嗜統一（去嗬/噬）。manifest A9/B11/C9。
- **⏳ 之後**：回填**每節級**對話編號引用（intro_schedule §6）、其餘四套（認識/本體/價值/存有）比照三卷分工原則重檢、回頭重檢 /ai-dialogues 五域分類。

## 🔄 A 卷 v2.1 再改版（2026-06-21，使用者 5+ 道指令，已部署 A8）
A《愛的萬物論》**9→8 章**（intro_schedule 升 v2.1）：①序自成一章 A1；②「數學化」併入「誠實萬德之綱」＝A4（誠實＝唯一通用變量→hi 第一變數→生成整套個人尺度公式；倫理場 E＋符號隨 hi 依序生成、取消預先符號總表）；③A2 加 Sandel《正義》/電車難題/三古典限制/晚近研究；④A3 從兒童現象學起（第一照顧者→他者先於主體→**倫理學是第一哲學**＋Freud/Jung 陰影情結→fc/vc 心理發生＝本我/超我‧面具/阿尼瑪阿尼姆斯＋身體感→邊界＋Piaget/Kohlberg＋**演化論動物倫理/鏡像反射→同理心（個體尺度）**＋三特性最初即俱在；fc/vc 概念首現移 A3、形式定義仍 A4）；⑤愛的公式後就地收數學化、不另立章（原 A8 拆入 A4 前半＋A7 末）。原 A1 地基章＋原 A8 取消；原 A9 結語→A8 重寫對齊新弧。
- 🚨 **越層尺度分層**：A3 可談個體尺度同理心的演化/生理發生，**不得**用 C 的日擇/耗散結構/反身自嗜/性善宇宙根基（cross-ref C3 也別 pre-name）。
- 手法（複用）：備份 `draft/A`→`_A_v2bak`；變動章 sonnet subagent 讀原稿＋治理文件寫 `_rNN.html`；不變章只修交叉引用；finalise 01-08→越層 audit→manifest A 9→8→`genesis_cite_backfill tag ethics A 8`→`assemble_genesis_book.py ethics A 8`→build 綠。citation 45 節/8 章末/113 labels 全 valid。
- ⏸️ item③-2 認識論（E）v2 精修暫停：治理文件已寫 `c:/tmp/genesis_epi/intro_schedule.md`（三卷分工/越層/章目/首現齊備，待續）；epi 對話 id 在 `chunk_*.json`（非 themes），citation 須改 chunk-based term→id。

## ✅ 五大主題全套 v2 精修＋引用竣工（2026-06-22 整夜自動跑）
使用者「自動化做一整晚把每一卷都精修好並加上出處」→ **15 冊全數完工並部署上線**：
- 倫理 A8（v2.1）/B13/C9（A 見上節 v2.1；B/C 沿用已精修＋引用，對 A 無章號交叉引用故未受 A 重構影響）。
- 認識論 E1 8/E2 10/E3 6（commit fb1b6d77）、本體論 O1 8/O2 6/O3 7（620509a2）、價值論 V1 6/V2 6（71b65ed3）、存有論 B1 7/B2 7/B3 7（7b730635，B3-7 兼整套總收束）。
- 每套流程：新撰 `c:/tmp/genesis_{epi,ont,val,bei}/intro_schedule.md`（三卷分工/越層紅線/章目首現/先論述後導出/recap 格式）→ sonnet subagent 逐章精修(一波≤6，保留實質做加值：章末 recap+argmap、英文首現、公式先論述後導出、越層紅線)→ 每冊序跋 → `genesis_cite_backfill tag <series>` 引用 → `assemble_genesis_book.py <series>` 重組 → build 綠 → commit。
- 🔑 **citation 改 chunk-based**：`genesis_cite_backfill.py` 加 `load_terms_chunks`（ethics 走 notes glossary.ids；E/O/V/B 的 id 在 `chunk_*.json`，以 themes 詞彙×chunk 全文搜尋取詞頻最高前 6 chunk→seq_label）。seq_label_map 五套共用。
- 🔑 **draft 目錄全改名對齊部署檔名**（1/2/3→E1.. 等）。複用流程同上。
- ✅ item③-3 /ai-dialogues 五域分類重標（進行中）：`scripts/retag_genesis_facets.py`——只重判**已屬創生哲學**對話的 facet、替換五子標保留父標，預設 dry-run/`--execute`、resumable ledger `c:/tmp/genesis_retag_{source}.jsonl`。`classify_genesis_philosophy` SYSTEM 的 facet 準則已改 v2 邊界（量子→本體論、數學→認識論、空無/默然/神聖/終極→存有論、願然/美→價值論、誠實/善→倫理學、創生公式/生成三要素→本體論；修正舊版誤把生成/創生歸存有論）。抽樣 26/30 facet 變更（多為舊存有論→本體論）。**全量 execute 背景跑中**（chatgpt 3,316＋gemini；Gemini/NVIDIA 配額耗盡退 Haiku，~81% 時）。

## 🔄 創生哲學叢書 — 序章正名／引用可點擊／M3 改名／M2 時間軸（2026-06-22 下午）
- **序章正名（最重要）**：創生哲學**是現象學、不是形上學**——反抽象本體論、依經驗主義從各學科建構（舊稿「原創形上學體系」是錯的，使用者糾正）。M1/01 重寫為全叢書**序章**（現象學出發→五大主題；筆者宗教學神學背景；宗教切入延伸至大哉問）；**序自成序章非第一章**，M1＝序章＋第一..七章。
- **引用可點擊**：`genesis_cite_backfill` 發 `<a href="/ai-dialogues?seq=…" class="cite-seq">`；`ai-dialogues` 頁 onMounted 讀 `?seq=` 自動 `doLookup`；reader 加 `.cite-seq` 樣式。全 15 冊已連結化。
- **M3《人類之子》→《人子》**（id 不變；福音書 Son of Man＋「蓋亞之子／人之子」雙關）。**book id 沿革：A/B/C→A1/A2/A3→M1/M2/M3**（倫理=Morality，與 E/O/V/B 一致）。
- **M2 重構 14 章＝時間維度**（使用者定調群體倫理須有時間向度；commit `297ec310`）：通論(hi/H/M/EVI·MHI/暴政T＋尼采/民主門檻)→過去(社會起源/政體史/極權＋鄂蘭平庸的邪惡＋轉型正義)→現代(異化·傅柯/**新增職業倫理場**)→未來(人權/無政府/異托邦)→結語。
  - 🔑 重構複用警示：非均勻 reorg 的交叉引用須 topic-aware 修；**moved 章的 intro／序跋會按舊順序 recap，必須連內容一起重寫對齊**（不只改章號）。backup `draft/_M2bak`。
- 治理文件 intro_schedule §3 的 A/B/C＝卷內章簡寫（A=M1 愛的萬物論/B=M2 虛構的烏托邦/C=M3 人子）。組裝 `assemble_genesis_book.py ethics M1 8 M2 14 M3 9`。

## ✅ facet 重標全量完成（2026-06-22）
`retag_genesis_facets.py --source all --execute` 跑完：chatgpt ledger 3,258／gemini 56；facet 有變更 ~508；94 則 LLM 現判非創生哲學（**只去五子標、保留父標**，符合設計）。引擎全程 Gemini/NVIDIA 配額耗盡退 Haiku。ledger `c:/tmp/genesis_retag_{chatgpt,gemini}.jsonl`。

## ✅ 引用連結修復＋hover 預覽（2026-06-22）
- **修 401**：`/ai-dialogues` 的 `doLookup()` 漏帶 auth header（requireAuth 只認 `Authorization: Bearer`，非 cookie）→ 點書中引用查閱 401。已補 `authHeader()`（commit 同批）。
- **hover 預覽**：book reader `.cite-seq` 滑過浮窗預覽該則對話（編號/日期/問答摘要），Teleport+快取，未登入提示「登入後可預覽」（by-seq 需登入，書頁公開）。
- 引用全是 **ChatGPT（C-）0 則 Gemini**：素材 dump 自 chatgpt facet 對話，Gemini 多雜訊、術語密度低不被選中。seq_label 按 (date,time,created_at,id) 排序＝固定，**facet 重標不動 seq_label，引用編號永不變**。

## 🔄 倫理三部曲依三層時間軸重構（2026-06-22，commit 已 push）
使用者定調：倫理三卷各是一條**時間軸**，三層嵌套。沿用既有「A 個人／B 群體／C 宇宙」分工，再加時間維度。
- **M1《愛的萬物論》8 章＝個人生命時間軸**：序章/為何/**主體的誕生(童年現象學)**/誠實數學化/召喚/陰影/**愛的公式擴(戀愛→婚姻→家庭→群體)**/🆕**死亡倫理**(向死存在·超義務·愛超越死亡，吸收原結語「愛的萬物論」收束)/跋。🚨越層保守：死亡章超義務只談**個人尺度 vc 極限/捨身**，不引 H/意義公式 M（已驗 M1 群體量＝0，唯一「意義公式」是 defer-to-B 的 cross-ref）；超越向度點到、形上學留存有論。
- **M2《虛構的烏托邦》14→13 章＝人類歷史時間軸**：🆕**第六章宗教倫理**(作為異托邦的宗教與文明發源；傅柯異托邦/軸心時代雅斯培/涂爾幹/伊利亞德；H/EVI 中性分析雙面性；接 B5 Dunbar、與 B12 裂口異托邦＝起源↔未來異托邦呼應)。**合併**：舊1+2→新1(H與意義生成)、舊12+13→新12(制度性無政府與裂口異托邦)。🚨**非均勻 reorg 交叉引用＝最大坑**：用專屬 sonnet agent topic-aware 重對全 13 檔（舊→新 mapping 表），結語(13)全書回顧整段重寫；驗證 0「第十四章」、0 B-code、裂口異托邦一律指第十二章。
- **M3《人子》9 章＝地球宇宙深時時間軸**：第一章導論重構為深時主敘事(McPhee deep time/Sagan 宇宙曆/三層時間軸路線圖)；🆕**第九章熱寂或永續共生圈**(熱寂vs共生圈、**三大格言 capstone 移此**、人子意象收束)。中間 2-8 章內容沿用。
- **製作法（複用）**：更新 `intro_schedule.md` §2/§3/§7→背書 `_M{1,2,3}bak`→變動章 sonnet agent 寫 `_rNN.html`(一波≤6，曾撞 1 個 connection-closed 重跑即可)→純移章直接 cp+sed 修 h2 章號→**專屬 agent 修交叉引用**→`genesis_cite_backfill tag ethics M1 8 M2 13 M3 9`→`assemble_genesis_book.py ethics M1 8 M2 13 M3 9`→build→push。manifest M2 nChapters→13。
- ⏳ 殘留小瑕：M3 第四章標題仍「生命倫理」（治理文件提議「生命的起源與生命倫理」但未擴 abiogenesis 內容，故未改標題，誠實保留）。

## 🔧 倫理三部曲後續微調（2026-06-22，已 push）
- **M3「複製與傳送」§四移除**：複製/意識傳送的「主體能否還原為資訊」＝主體意識的**本體論**問題（非倫理）。本體論卷 **O3 第四章「自我同一性」已有更完整版**（意向性連續＋具身性不可缺；Parfit/Locke/特修斯之船/Merleau-Ponty）。M3 ch4 生命倫理改留一條指向 O3 的交叉引用，四場域→三場域，recap/argmap 同步去傳送指涉。⚠️ 日後若再有「某倫理章其實是 X 論問題」＝先查該 X 卷是否已涵蓋，多半是去重而非搬寫。
- **章名一致化（使用者要全書順）**：原則＝短題、去冒號長副標/列舉題、保留 序/序章/導論/結語 結構標籤；副標內容留章內。改了 7 章：M1 ch1 去「一門」、ch2「主體的誕生」、ch6「愛的公式」、ch7「死亡倫理」（去副標）；M2 ch6「宗教倫理與起源異托邦」、ch8「極權政治與轉型正義」；M3 ch9「熱寂與永續共生圈」。保留 M1 ch3、M2 ch1 兩個較長「A與B」式（同形可接受）。改 h2 後只需 `assemble_genesis_book.py` 重組（不必 re-tag，引用不變）。

## 🔧 M1 章序重排＋清 A/B/C 卷標籤（2026-06-23，已 push）
- **M1 章序（質性→形式化，使用者定）**：召喚的結構、倫理陰影與補償移到誠實/數學化之前。新權威序：序章/①為何/②主體的誕生/③召喚的結構/④倫理陰影與補償/⑤誠實作為萬德之綱與數學化/⑥愛的公式/⑦死亡倫理。**前引鐵律**：③④只能用②的「心理層 fc/vc」，不得預設 hi 形式定義/fc-vc 形式變數/倫理場 E 形式化（這些⑤才建立）→ ③④須前向預告「留待第五章」；⑤＝承③④質性探討的形式化樞紐。🚨**子代理重排交叉引用易 off-by-one**（曾把②誤算第三章）——renumber 後務必逐章 topic-aware 驗證 第N章（07/08 已修）。
- **無 A/B/C 卷標籤**：倫理三卷對外一律 M1/M2/M3 或「第一/二/三卷《書名》」，跨卷引用附現行章號。全叢書 20 處已清（M2/M3/O2/V2+M1）；兩處 stale「A 卷第八章」（性善論/反身自嗜，現在 M3 ch3）正名「本卷第三章」；自指 B/C 卷→本卷。日後新增跨卷引用一律別用 A/B/C 卷。
- governance `intro_schedule.md` §3 已更新章序/前引/無-ABC 政策。
- ✅ **重排後通讀驗證（2026-06-23）**：逐章查方向性過渡詞（前一章/下一章/前N章），④⑤⑥⑦銜接全對——③召喚回顧②誕生·預告④陰影；④陰影回顧②③·預告⑤誠實給形式定義；⑤誠實回顧前三章質性·預告⑥愛；⑥愛預告⑦死亡。「前六章→前面各章」「下一章（結語）→（死亡倫理）」斷裂處已修。質性→形式化→應用弧線連貫無殘留。

並列 [[project_krishna_dialogues]]（同 /ai-dialogues，紫色「與克里希那對話」分類）。
