---
name: dialogues-to-writing
description: 把 /ai-dialogues 裡某一條「跨多日延續的 AI 對話串」找出來、整理成 /works 的寫作計畫成品。涵蓋：①依「對話框語氣」逐則認定一條 thread（不是靠關鍵字）②在 /ai-dialogues 建分類標籤把整串標起來不漏 ③把 AI 回覆用 NVIDIA 潤飾成流暢「對話錄」④每日切 1–3 個主題 ⑤組裝成可編輯的 /works 月份卡片（日期+星期+主題+雙方對話）。Use when 使用者說「把我跟某 AI 從 X 月到 Y 月那串對話找出來／做成寫作計畫／整理成對話錄」、要把 ai_dialogues_gemini／chatgpt 的某主題串標分類、要把對話潤飾分主題上 /works。第一個案例＝[[project_krishna_dialogues]]（與克里須那談夢境與榮格，671 則）。
---

> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

# 對話串 → 寫作計畫 Skill

把 `/ai-dialogues` 裡一條延續好幾天/幾個月的 AI 對話，整理成 `/works` 上一份可讀、可編輯的「對話錄」寫作計畫。首案見 [[project_krishna_dialogues]]。

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
7. dialogue_assemble.py      組裝：依月份開 writing_projects 卡片，每天 <h2>日期（星期X）</h2>→<h3>主題：…</h3>→<p><strong>阿周那：</strong>…</p>。主卡=索引
8. dialogue_haiku_finish.py  救急收尾：NVIDIA+Gemini 都 429 時，用 Haiku 跑剩餘潤飾+主題+assemble
```

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
4. `dialogue_polish.py` 指到新 final json、改 persona 名（阿周那/克里須那 → 新的）。
5. `dialogue_segment_topics.py` → `dialogue_assemble.py` 改 slug 前綴、persona 名、月份標題 → 上 /works。
6. 配額不夠就 `dialogue_haiku_finish.py` 救急收尾。

## 與其他 skill 分工
- 對話**來源頁** `/ai-dialogues`：本 skill。對話**翻譯/簡繁**走 [[ebook-translate]] 引擎觀念。
- 多語全集對照 → [[ebook-collected-works]]；訪談逐字稿 → [[writing-thesis-interview]]（對話錄格式可參考其 Q&A 排版）。

## See also
- [[project_krishna_dialogues]] — 首案：與克里須那對話（671 則、4 張月份卡片）
- [[feedback_engine_nvidia_no_haiku]] — Gemini→NVIDIA→Haiku 統一引擎政策＋多 key 節流
