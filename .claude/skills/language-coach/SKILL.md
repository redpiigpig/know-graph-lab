---
name: language-coach
description: AI 語言教練（/coach）— 外語自學系統，多語言（英文 Emily / 日文 櫻子 上線；德法拉古希臘預留）。核心：Gemini 對話 + Web Speech 語音；每語言獨立空間（首頁/儀表板/記憶/功能各自客製）。功能含五種聊天模式（打字/口說/問答知識/情境角色/限時主題）、今日計畫（每日推薦單字測驗+5閱讀+5聽力+口說+任務）、分級文法課（CEFR/JLPT）、技能練習與 TOEFL/IELTS/GRE 考試模擬、翻譯遊戲、YouTube/文章沉浸（讀聽後 MCQ+討論+評分）、統整記憶庫、教練每日簡報與日誌、SRS 單字、雙 key 成本控管。Use when 改語言教練任何功能、加語言、調人設/難度/題材、改資安（OTP 登入/付費上限）、接 Gemini key、debug coach 端點或頁面。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：任一邊超過 2000px 會炸掉 session。

# AI 語言教練 Skill

使用者（宗教研究者）的外語自學系統。目標：英文 B2→C2→TOEFL；日文 N5 起步。題材**以宗教/神話/宗教學為主軸**，輔以人文，少量理工醫/生活/旅遊（考試模式走真實考題）。相關偏好見 [[project_language_coach]]、[[feedback_language_coach_religious_studies]]、[[feedback_traditional_chinese_only]]。

部署：**Zeabur**（GitHub master 自動部署）。DB：Supabase（Management API 跑 DDL，見 [[reference_supabase_management_api]]）。

---

## 一、頁面結構（每語言獨立空間）

選擇頁 `/coach`（只挑語言）→ 進入 `/coach/[lang]/`，之後全部專屬該語言（語言由路由決定，無語言下拉）：

- `/coach/[lang]`（index）= **語言首頁**：教練主動「今日簡報」、統計列、**📅今日計畫主入口**、聊天五磚、學習五磚、學習日曆+教練日誌、統整記憶庫
- `/coach/[lang]/today` = **今日計畫**（見下）
- `/coach/[lang]/chat` = 對話（`?mode=qa|scenario`、`?voice=1`）
- `/coach/[lang]/smalltalk` = 限時主題聊（3/5/10 分倒數 + 結束評分）
- `/coach/[lang]/grammar` = 分級文法課
- `/coach/[lang]/practice` = 技能練習 / 考試模擬 / 翻譯遊戲
- `/coach/[lang]/review` = 單字 SRS（翻卡 / 選擇題）
- `/coach/[lang]/immersion` = YouTube/文章沉浸
- `/coach/[lang]/dashboard` = 該語言儀表板 + Gemini 用量/成本

## 二、聊天五模式（chat.post.ts 依 mode 套 prompt；人格自動輪替）

- **打字 / 口說**（free，voice=1 自動朗讀）
- **問答‧知識**（qa）：像一般 AI 答題教知識，corrections 通常空
- **情境角色**（scenario）：教練演對方角色（店員/面試官/神職…）
- **限時主題聊**（smalltalk 頁）
- 人格：`lang-coaches.ts` `personas[]`，新對話依 session 數輪替（Emily 5 種）。注入統整記憶 + 人格 + 本次摘要進 system prompt。

## 三、今日計畫（today）— 每日自學核心

`lang_daily`（PK user+lang+date）一天生成一次 topics 快取。
- **進度**：已記住單字（mastery≥3）/ 待複習 / 占目標程度詞彙約 %（`daily.get` VOCAB_TARGET 概估，英文 C2≈8000）
- **今日任務** checklist + **今日 5 閱讀 + 5 聽力 + 5 口說**（點開才 `daily/item` 懶生成）
- 閱讀短文 / 聽力 TTS 朗讀 + **4 選 1 理解題**（自動對答案、記時間）
- 每項可**口說/打字討論**（/api/lang/chat 即時糾錯）+**結束給評分**（/api/lang/smalltalk/feedback）
- **沉浸（immersion）同此流程**：YouTube/文章 → 摘要/MCQ/抽單字 → 討論(語音/文字) → 評分；YT 片長計入聽力時間

## 四、其他功能

- **分級文法課**（`lang_grammar` PK user+lang+**level**）：英文 B2/C1/C2、日文 N5–N1 各一套；**Gemini 依程度自動生成**（不需手動 seed）；大綱循序 + 逐課懶生成（解說/例句/練習）+ 完成度。頁 `/coach/[lang]/grammar`。
- **主題教程**（`lang_courses`）：可選預設或自建主題（宗教文獻精讀/學術寫作/TOEFL口說/敬語/宗教神話日語…），生成循序課表，**每課標預估分鐘**，逐課懶生成 + 進度條。頁 `/coach/[lang]/courses`；端點 courses(index/create/[id]/lesson/done)。
- **單字 SRS**（`lang_vocab`，SM-2，`server/utils/srs.ts`）：到期佇列；review 預設選擇題（對=good 錯=again→複習）；不足時從整庫補未精熟字；`vocab/generate` 依**目前程度**生成主題詞組。
- **技能練習/考試**（`lang_tasks`）：`task/generate`（TOEFL/IELTS/GRE + 一般，聽說讀寫 + 翻譯）/ `task/[id]/answer`（選擇題自動批改、寫說/翻譯用 Gemini rubric 評分）。
- **記憶/簡報/日誌**：`lang_memory`（跨 session 長期了解 + highlights 強弱項，注入對話）；`briefing`（今日簡報，每日快取）；`lang_journal`（教練每日日誌，日曆點閱）。
- **難度依「目前程度」非目標**：生成都讀 `lang_progress.level`；量表 `coach.levelScale`（CEFR / JLPT / 入門初中進）；`progress.put` 設目前程度。

## 五、資安（鎖回站長專屬）

- **登入 = Email OTP 6 碼**（login.vue：signInWithOtp→verifyOtp，shouldCreateUser:false）。⚠️ **Supabase Email Template「Magic Link」必須含 `{{ .Token }}`** 否則收不到碼。
- **裝置核准閘門已於 2026-06-03 移除**（單人私站、登入已靠 email OTP + allowedEmail 白名單，多一層只會把站長自己鎖在外）。`trusted_devices` 表保留但不再使用；middleware/頁面/API 皆已刪。
- **付費 key 僅站長**（coach-ai `isOwner` 比對 allowedEmail）；coach-auth 站長專屬；`/signup` 關閉。
- **付費每月上限 NT$500**（env `GEMINI_PAID_MONTHLY_CAP_TWD`）：超過自動退免費；儀表板顯示+警示。

## 六、模型與 key（成本）

- **主引擎＝NVIDIA NIM（2026-06-03 起）**：`server/utils/nvidia.ts` `callNvidiaFull`（OpenAI 相容、key 輪替、剝 `<think>`）。`coach-ai.ts` `coachGemini` 先試 NVIDIA → 失敗才落 Gemini。env `nvidiaApiKeys`=`NVIDIA_API_Key_1..3`、`nvidiaModel` 預設 **`qwen/qwen3-next-80b-a3b-instruct`**（繁中佳、支援 JSON、穩定）。無限量、零成本，用量記 tier=`nvidia`。
  - ⚠️ **不要改回 `deepseek-ai/deepseek-v4-flash`**：該模型在 NVIDIA 免費層長期 429（互動式教練不可靠）；deepseek 只適合 translate 腳本那種可退避重試的批次。其餘 NVIDIA 模型（qwen3-next、llama-3.1）正常 200。
  - **fileData（YouTube 等多模態 part）NVIDIA 不支援** → `coachGemini` 偵測到自動跳過走 Gemini。
- **Fallback＝Gemini**：`server/utils/gemini.ts`（callGemini/callGeminiFull + key 輪替 + usageMetadata）；`coach-ai.ts` `coachGemini`（tier 選 key + owner/budget 守門 + 用量寫 `lang_api_usage`）。
- 預設模型 **`gemini-flash-latest`**（固定 ID 2.5-flash 免費日限 20 太低；alias 配額桶分開）。env `GEMINI_MODEL`/`GEMINI_GRADE_MODEL` 可覆寫。
- 雙 key env：`GEMINI_COACH_FREE_KEY`（空則 fallback `Gemini_API_Key_*` 池）/ `GEMINI_COACH_PAID_KEY`。Gemini 免費用完→前端 `useCoachAi.aiFetch` 跳確認→切付費重試（NVIDIA 為主後此路徑幾乎不觸發）。
- 前端 AI 呼叫一律走 `useCoachAi().aiFetch`（自動帶 usePaid + free_exhausted 處理）。

## 七、DB 表（Supabase，全 RLS 依 user_id）

`lang_profile`/`lang_progress`/`lang_sessions`(persona/mode/topic/duration/feedback)/`lang_messages`/`lang_vocab`(SM-2)/`lang_homework`/`lang_activity`/`lang_level_history`/`lang_api_usage`(+bump_lang_usage RPC)/`lang_memory`(memory/highlights/briefing/briefing_date)/`lang_journal`/`lang_word_lists`/`lang_tasks`/`lang_content`/`lang_grammar`/`lang_daily`/`trusted_devices`。migration SQL 在 `database/language-coach-*.sql` 等，用 Supabase Management API 套用。

## 八、端點（`server/api/lang/*` + `server/api/devices/*`）

chat / profile(get,put) / progress(get,put) / activity / dashboard / usage / assess / briefing / memory(get,regenerate) / journal(get, generate) / sessions / messages / coaches / vocab(index,generate,review get/post,[id] patch/delete) / homework / task(generate, [id]/answer) / smalltalk(start, feedback) / content(ingest, index) / grammar(index, lesson, done) / daily(get, item, done) / devices(check, index, [id] patch)。

## 九、加語言 / 擴充

- 加語言：`server/utils/lang-coaches.ts` 加一筆（language/levelScale/defaultLevel/personas/scenarios/smalltalkTopics/systemPrompt…），設 `enabled:true`。前後端自動支援。古語言設 `voiceless:true`。
- 古語言人設定向（勿改回）：日文關東標準語、希臘文 1 世紀聖經 Koine、拉丁文教會拉丁。

## 十、使用者要手動做（部署前）

1. **Supabase Auth → Email Templates → Magic Link 加 `{{ .Token }}`**（最關鍵，否則驗證碼收不到）
2. Supabase Auth 關「Allow new signups」；建議設自訂 SMTP（預設寄信額度低）
3. Zeabur Variables 加 `GEMINI_COACH_PAID_KEY`（改上限再加 `GEMINI_PAID_MONTHLY_CAP_TWD`）

## 待辦（次要）

Live2D、雲端 TTS、開放德/法、AWL/GRE 詞庫實際 seed、速率限制、MFA、用量異常 email 通知、%C2 換真實 C2 wordlist。
