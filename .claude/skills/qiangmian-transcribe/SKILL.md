---
name: qiangmian-transcribe
description: 千面上帝宗教史讀書會的完整自動化流程：Gemini Audio 轉錄 + 潤稿 + PPT 上傳 R2 + 日期/YouTube/下載連結。Use when the user wants to transcribe, polish, or manage episodes of 千面上帝 宗教史讀書會.
---

# 宗教史讀書會 — 完整自動化流程

## 總覽

```
YouTube 影片
    │
    ▼
yt-dlp 下載音訊（.m4a）
    │
    ▼
Gemini 2.5 Flash 轉錄（搭配 PPT 作為專有名詞參考）
    │
    ▼
Supabase video_transcripts upsert
    │
    ▼
（選）Gemini 潤稿：刪填充詞 + 加小標
    │
    ▼
http://localhost:3004/works/qiangmian/reading-club/[id]
```

PPT 已在初始化時全部上傳到 R2（`qiangmian-ppt/ep{N:02d}.pptx`），轉錄腳本自動從 PPT 檔名取日期並填入 DB。

---

## 來源資料

| 資料 | 位置 |
|---|---|
| YouTube 播放清單 | `https://www.youtube.com/playlist?list=PLNdU3g_-OSshfnyOakO5exMMvnSNeuIjZ`（25 集）|
| PPT 投影片 | `G:/我的雲端硬碟/創作/千面上帝/宗教史讀書會/*.pptx`（29 個，按 YYYY.MM.DD 排序）|
| R2 PPT | `qiangmian-ppt/ep01.pptx` … `ep29.pptx` |
| 暫存音訊 | `_tmp_audio/qiangmian/`（upsert 成功後自動刪除）|

**PPT 對應規則**：**不能機械對應 ppt_files[ep-1]**。29 PPT vs 25 影片，原因有三：
- 第五章、第十五章上 有 PPT 但沒影片（講師缺席或漏錄）
- 第十二章上 一份 PPT 講三集（ep 13/14/15 共用 PPT 14）
- 第十六章中、第十七章終 有 PPT 但沒影片

正確對應表寫死在 `scripts/overnight_qiangmian.py` 的 `EP_TO_PPT_IDX`：

| ep | PPT idx | 章節 |
|---|---|---|
| 1–4 | 1–4 | 第一～四章 |
| 5 | 6 | 第六章（跳第五章 PPT） |
| 6–12 | 7–13 | 第七～十一章下 |
| 13–15 | 14 | 第十二章上（三集共用） |
| 16 | 15 | 第十二章下 |
| 17–20 | 16–19 | 第十三、十四章 |
| 21 | 21 | 第十五章下（跳第十五章上 PPT） |
| 22 | 22 | 第十六章上 |
| 23 | 26 | 第十七章中（best guess，PPT 為「下」） |
| 24 | 28 | 第十八章上（跳第十六章中/下、第十七章上/終） |
| 25 | 29 | 第十八章中 |

---

## 步驟一：轉錄

```bash
# 查看播放清單 + PPT 對應
python scripts/transcribe_qiangmian_gemini.py --list

# 轉錄單集
python scripts/transcribe_qiangmian_gemini.py --episode 1

# 轉錄範圍
python scripts/transcribe_qiangmian_gemini.py --episode 2-5

# 全部（每集 ~3-5 分鐘，共約 2 小時）
python scripts/transcribe_qiangmian_gemini.py --all
```

腳本做的事：
1. `yt-dlp` 下載 m4a（~100 MB/集）
2. 讀取對應 PPT 文字作為 context
3. 上傳音訊到 Gemini Files API，等 state=ACTIVE
4. `gemini-2.5-flash` 轉錄（繁體中文、分段、含 PPT 專有名詞）
5. Supabase upsert（`on_conflict=project_slug,episode`）— 自動帶入 `video_date`（從 PPT 檔名）、`ppt_r2_key`（`qiangmian-ppt/ep{N:02d}.pptx`）
6. 刪除暫存音訊

**關鍵坑**：upsert 的 POST URL 必須加 `?on_conflict=project_slug,episode`，光靠 `Prefer: resolution=merge-duplicates` 會回 409。

---

## 步驟二：潤稿（每集手動觸發）

Gemini 轉錄的原始稿保留所有口語，需潤稿：

**要做的事**：
1. 刪口語填充：「就是說」、「這樣子」（語助詞）、「嘛」、口吃重複（「我、我」）、場務對話（「請問看得到投影片嗎？」）
2. 合併重複句子
3. 加 `## 小標`（二至四字，全文 8–12 個）
4. 保留所有人名、地名、書名、專有名詞
5. 格式：`---` 作分隔線，結尾加 `*備注*`（斜體）

**做法**（Gemini 可用時）：
```python
python -c "
import sys, requests
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from google import genai

_env = {}
for line in Path('.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, _, v = line.partition('=')
        _env[k.strip()] = v.strip().strip('\"')

client = genai.Client(api_key=_env['Gemini_API_Key_1'])
raw = open('c:/tmp/ep_raw.txt', encoding='utf-8').read()
lines = raw.split('\n')
header = '\n'.join(lines[:3])
body = '\n'.join(lines[3:])

prompt = '''以下是宗教史讀書會逐字稿原文。請：
1. 刪填充詞（就是說/這樣子/嘛/口吃重複/場務對話）
2. 合併重複句子
3. 加 ## 小標（8-12 個，二至四字）
4. 保留所有專有名詞
只輸出潤稿後的正文，不加說明。

---逐字稿---
''' + body

resp = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt])
print(header + '\n\n' + resp.text.strip())
"
```

若 Gemini 503/quota，由 Claude 在對話中直接潤稿（閱讀全文後重寫）。

**upsert 潤稿結果**：
```python
import requests
resp = requests.post(
    f'{SUPABASE_URL}/rest/v1/video_transcripts?on_conflict=project_slug,episode',
    json={'project_slug': 'qiangmian', 'episode': N, 'title': '...', 'content': polished},
    headers={...Prefer: resolution=merge-duplicates...}
)
```

---

## 步驟三：加新 PPT（需要時）

若有新的 PPT 要上傳到 R2：

```python
import boto3
from pathlib import Path

r2 = boto3.client('s3', region_name='auto',
    endpoint_url=_env['R2_ENDPOINT'],
    aws_access_key_id=_env['R2_ACCESS_KEY'],
    aws_secret_access_key=_env['R2_SECRET_KEY'])

r2.upload_file(
    str(ppt_path), _env['R2_BUCKET'],
    f'qiangmian-ppt/ep{N:02d}.pptx',
    ExtraArgs={'ContentType': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'}
)
```

---

## Supabase schema

```sql
-- video_transcripts 欄位（qiangmian 相關）
id            uuid
project_slug  text  -- 'qiangmian'
episode       int
title         text
content       text  -- 格式見下方
video_date    text  -- YYYY-MM-DD（從 PPT 檔名取）
youtube_id    text  -- 11 碼 YouTube video ID
ppt_r2_key    text  -- 'qiangmian-ppt/ep01.pptx'
created_at    timestamptz
```

`content` 格式：
```
[title]
Episode: N
Date: YYYY-MM-DD

## 小標一

段落文字...

## 小標二

段落文字...

---

*本集參考書目請見課程PPT。*
```

頁面渲染規則（`[id].vue`）：
- `## 文字` → 棕色小標（`t-heading`）
- `---` → 分隔線（`t-rule`）
- `*文字*` → 灰色斜體（`t-note`）
- `Episode:/Date:` → 琥珀色左線（`t-meta`）
- 其他行 → 縮排正文（`t-para`）

---

## API 端點

| 端點 | 用途 |
|---|---|
| `GET /api/works/qiangmian-readings` | 列出所有集數（index 頁用）|
| `GET /api/works/transcript/[id]` | 單集全文（content + video_date + youtube_id + ppt_r2_key）|
| `GET /api/works/ppt-download/[id]` | 生成 R2 pre-signed URL（1 小時有效）並 redirect 下載 |

---

## 頁面

- 列表：`http://localhost:3004/works/qiangmian`
- 單集：`http://localhost:3004/works/qiangmian/reading-club/[id]`

單集頁標題下方顯示：日期 badge、YouTube 紅色按鈕、投影片下載琥珀色按鈕。

---

## 已完成集數（2026-05-07）

| 集數 | 標題 | 狀態 |
|---|---|---|
| 1 | 第一章、被拋入世界的萬物之靈 | ✅ 轉錄 + 潤稿完成 |
| 2–5 | 第二～五章 | ✅ 轉錄完成（舊 Whisper，品質差，待潤稿）|
| 6–25 | 第六章以後 | ⏳ 待轉錄 |

PPT ep01–ep29 全部已上傳 R2。DB 只有 ep01–05 有 row（其餘跑 `--all` 再建）。

---

## 注意事項

- Gemini 2.5 Flash 有時 503（高需求）→ 等幾分鐘重試，或換 Gemini_API_Key_2/3/4
- R2 PPT 無公開 URL → 必須透過 `/api/works/ppt-download/[id]` 端點取得 signed URL
- 轉錄腳本使用 `Gemini_API_Key_1`（無自動 key rotation，quota 到了手動改）
