---
name: talks-transcribe
description: 受邀演講／學系專題講座／公開講座的完整 pipeline — 海報資訊 OCR → ffmpeg 切音 → Gemini Audio 平行轉錄（含 PPT context）→ Claude 對話內清稿 → PPT 上 R2 → 寫入 public/content/talks/ 並更新 stores/talks.ts。Use when 使用者有新一場演講的「海報＋錄音＋PPT」要上架到 /talks。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 演講活動 — 海報＋錄音＋PPT → /talks 上架 Pipeline

把一場演講（學系專題講座、研討會主題演講、公開講座等）從**海報＋錄音＋PPT** 一路整理成 `/talks/[id]` 上可閱讀的逐字稿頁面，並把 PPT 放到 R2 供下載。

## 總覽

```
海報（jpg/png）           ─┐
PPT（pptx）               ─┼─→ Claude 解析 metadata（標題／日期／場地／主辦）
錄音（m4a/mp3）           ─┘
       │
       ├─→ ffmpeg 切成 ≤22 分鐘片段（_tmp_audio/talks/[date-slug]/partN.m4a）
       │
       ├─→ python-pptx 抽 PPT 文字 → ppt_context.txt
       │
       ├─→ R2 上傳 PPT → talks-ppt/[date-slug].pptx
       │
       ├─→ Gemini 2.5 Flash 平行轉錄（每段獨立 prompt + PPT context）
       │
       ├─→ Claude 對話中清稿（刪口語填充、合併段落、加小標、修正聽錯、移除休息）
       │
       └─→ public/content/talks/[date-slug].md  +  stores/talks.ts 加新 entry
```

## 資料命名與位置

| 資料 | 位置 |
|---|---|
| 演講錄音 | `G:/我的雲端硬碟/[單位]/[相關資料夾]/新錄音 NN.m4a` 或 `[日期]_[主題].mp3` |
| PPT | 同上資料夾 `[YYYY.MM.DD][主題].pptx` |
| 海報 | 使用者貼進對話的截圖 |
| 暫存 | `_tmp_audio/talks/[YYYY-MM-DD]/` — partN.m4a、partN_raw.txt、ppt_context.txt |
| R2 PPT | `talks-ppt/[YYYY-MM-DD]-[slug].pptx`（bucket = `knowgraphlab`）|
| 上架逐字稿 | `public/content/talks/[YYYY-MM-DD]-[slug].md` |
| Store | [`stores/talks.ts`](../../../stores/talks.ts) |

**date-slug 命名**：`YYYY-MM-DD-[地點縮寫]`，例：
- `2026-05-19-hsuanchuang`（玄奘大學）
- `2025-10-30-dharmadrum`（法鼓山）
- `2024-12-28-tainancku`（台南大學）

---

## Step 1 — 解析海報資訊

使用者通常會貼一張海報截圖，要從中讀出：
- **標題**（含副標）
- **日期 / 時間**（YYYY-MM-DD + HH:MM–HH:MM）
- **場地**（建物 + 教室／廳）
- **主辦／課程／系所**
- **主講人銜頭**（如「兼任講師」、「碩士研究生」）
- **海報主圖風格**（可作後續 UI 配色提示）

**注意西元年判讀**：使用者習慣寫民國年；海報若顯示 `2025` 但實際是台灣民國 `114`，要對照當下日期判斷。例：海報寫「2025.05.19 週二」，當日是 2026-05-19 週二，那海報是檔名沿用舊年但實際是 2026。

---

## Step 2 — 切音檔

```bash
# 先看長度
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "原檔.m4a"
```

切成 ≤22 分鐘片段（避免 Gemini 2.5 Flash 處理長音檔卡進重複迴圈）：

```bash
mkdir -p _tmp_audio/talks/YYYY-MM-DD
# 每段 1320 秒 (22 min)，最後一段視長度調 -t
for i in 0 1 2 3; do
  start=$((i * 1320))
  ffmpeg -y -i "原檔.m4a" -ss $start -t 1320 -c copy \
    "_tmp_audio/talks/YYYY-MM-DD/part$((i+1)).m4a"
done
# 最後一段
ffmpeg -y -i "原檔.m4a" -ss 5280 -t 1200 -c copy \
  "_tmp_audio/talks/YYYY-MM-DD/part5.m4a"
```

**107 分鐘為例**：5 段（22+22+22+22+18 min）。

---

## Step 3 — 抽 PPT 文字當 context

```bash
python -c "
from pptx import Presentation
from pathlib import Path
ppt = Presentation('PPT路徑.pptx')
lines = []
for i, slide in enumerate(ppt.slides, 1):
    lines.append(f'=== Slide {i} ===')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                t = para.text.strip()
                if t: lines.append(t)
    lines.append('')
Path('_tmp_audio/talks/YYYY-MM-DD/ppt_context.txt').write_text('\n'.join(lines), encoding='utf-8')
"
```

PPT 文字會餵給 Gemini 當 context，幫忙正確轉錄人名／書名／術語。

---

## Step 4 — Gemini 平行轉錄

```bash
# 每段一個 background task；scripts/transcribe_talk_gemini.py 已有 retry-with-backoff
for n in 1 2 3 4 5; do
  python scripts/transcribe_talk_gemini.py \
    _tmp_audio/talks/YYYY-MM-DD/part$n.m4a \
    --out _tmp_audio/talks/YYYY-MM-DD/part${n}_raw.txt \
    --ppt-text _tmp_audio/talks/YYYY-MM-DD/ppt_context.txt \
    --speaker "張辰瑋" \
    --title "演講標題" &
done
wait
```

**script 行為**：
- 對應 prompt 已內建：講座資訊、PPT context、繁體中文要求、講者標籤規則
- 講者標籤：`講者：` / `提問：`（多人 `提問A：`、`提問B：`）/ `主持人：`
- 每把 GEMINI key 最多 retry 3 次（指數 backoff 15s/30s），對付 `503 UNAVAILABLE`
- 自動 fallback 到下一把 key（共 4 把）

**常見 fail**：所有 key 都吐 503（Gemini 高需求時段）— 等 5–10 分鐘整體服務恢復，再跑失敗的 part。Free-tier 每 key 一天 50 次 request，演講轉錄量小不會撞配額。

---

## Step 5 — Claude 對話中清稿

Gemini 原始輸出已有講者標籤＋繁體＋分段，但需要：

1. **刪口語填充**：「就是說」「這樣子」「嘛」「啊」、口吃重複（「我、我、我」）、聽眾的「嗯／是」短回應
2. **修正連續重複**：Gemini 偶爾會把同一個字打 5–10 次（連續結巴），縮成 1 次
3. **移除休息時段**：使用者明確告知「中間有 10 分鐘休息」— 找出對應 part 中的停頓，刪除休息中的雜聲段落
4. **合併破碎段落**：Gemini 會在每個停頓拆段，整理時把同一主題合併成 1–3 段
5. **加 `## 小標`**：依 PPT 章節對應（PART 1 / PART 2 / Q&A 等）插入 markdown 小標
6. **修正聽錯人名／書名**：
   - 趙文詞 / Richard Madsen、貝拉 / Robert Bellah
   - 證嚴、聖嚴、星雲、印順、昭慧、白聖、惟覺
   - 《民主妙法》、《心靈的習性》
   - 法鼓山、慈濟、佛光山、中台禪寺、福智、靈鷲山、弘誓
   - 卡理斯瑪（charisma）、人間佛教、解嚴、政教互動
7. **Q&A 段落**：在主體演講後插入 `## Q&A` 小標；保留提問者編號（A/B/C），講者用「講者：」

### 輸出格式（`public/content/talks/[id].md`）

```markdown
## 引言

[第一段內文]

[第二段內文]

## PART 1 ‧ 引言與經典回顧

### 對話起點：《民主妙法》與作者趙文詞

[內文]

### 方法論前提

[內文]

## PART 2 ‧ ...

## Q&A

提問A：[問題]

講者：[回答]

提問B：[問題]

講者：[回答]
```

渲染由 [pages/talks/[id].vue](../../../pages/talks/[id].vue) 處理：
- `## 文字` → 玫瑰色左線 h2
- `### 文字` → 玫瑰色 h3
- `講者：/提問A：/主持人：` → 玫瑰色 chip + 換行
- `（休息／中斷）` → 灰斜體置中

---

## Step 6 — 上傳 PPT 到 R2

```python
python -c "
import boto3
from pathlib import Path
_env = {}
for line in Path('.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.startswith('#'):
        k, _, v = line.partition('=')
        _env[k.strip()] = v.strip().strip('\"')
r2 = boto3.client('s3', region_name='auto',
    endpoint_url=_env['R2_ENDPOINT'],
    aws_access_key_id=_env['R2_ACCESS_KEY'],
    aws_secret_access_key=_env['R2_SECRET_KEY'])
r2.upload_file('PPT路徑.pptx', _env['R2_BUCKET'], 'talks-ppt/YYYY-MM-DD-slug.pptx',
    ExtraArgs={'ContentType': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'})
print('✓ uploaded')
"
```

---

## Step 7 — 寫入 store + API mapping

兩個地方要更新：

### 7a. [`stores/talks.ts`](../../../stores/talks.ts) — 加 entry

```ts
{
  id: '2026-05-19-hsuanchuang',
  title: '...',
  subtitle: '...',
  date: '2026-05-19',
  duration: '08:30–10:15',
  venue: '...',
  organizer: '...',
  course: '...',  // 可選
  category: 'lecture',  // lecture/seminar/public/invited/panel
  hasTranscript: true,
  pptR2Key: 'talks-ppt/2026-05-19-hsuanchuang.pptx',
  description: '...',
}
```

### 7b. [`server/api/talks/ppt-download/[id].get.ts`](../../../server/api/talks/ppt-download/[id].get.ts) — 加 mapping

```ts
const TALK_PPT_KEYS: Record<string, { key: string; filename: string }> = {
  '[id]': {
    key: 'talks-ppt/[id].pptx',
    filename: '[人可讀檔名].pptx',
  },
}
```

---

## Step 8 — 驗證 + commit

1. dev server 重啟確保 stores/api 更新
2. 瀏覽 `/talks` 看新項目出現
3. 點進 `/talks/[id]` 確認逐字稿渲染正常
4. 點「下載投影片」測試 R2 signed URL
5. 依 [feedback_auto_push](../../../memory/feedback_auto_push.md) commit + push，message 例：
   `feat(talks): 新增 2026-05-19 玄奘宗教系專題講座`

---

## 分類 (TalkCategory)

| 值 | 中文 | 場景 |
|---|---|---|
| `lecture` | 學系專題講座 | 某大學系所邀請的單場專題（玄奘宗教系、台大歷史系等） |
| `seminar` | 研討會專題 | 學術研討會的 keynote / 專題演講（非投稿論文）|
| `public` | 公開講座 | 對社會大眾的開放講座（教會、文化中心、咖啡店）|
| `invited` | 受邀演講 | 受 NGO / 宗教團體邀請的非公開內部講座 |
| `panel` | 論壇與談 | 多人與談形式，講者只是其一 |

---

## 常見坑

- **PPT 檔名年份對不上實際日期**：使用者很常沿用舊版檔名（`2025.05.19...pptx` 實際是 2026）。一律以海報上的「週幾」對照當下日期判斷。
- **休息時段未標註**：使用者會口頭說「中間有 10 分鐘休息」，要在清稿時自己抓位置（多半在演講中段）。
- **Q&A 區段融在一起**：Gemini 不會自動標 Q&A vs 演講本體，要靠語氣轉折識別（「好，我們今天的演講就講到這邊」「有沒有同學想問問題？」等）。
- **錄音前後段**：開頭可能有「請問麥克風 OK 嗎？」這類調整，可整段刪。結尾可能掛在「謝謝大家」之後一段空白。
- **講者口頭用語錯誤**：例如把「第二」說成「第二第一」、「卡理斯瑪」說成「卡里斯瑪」等。要修正常見筆誤但保留語氣。
- **錄音中講者多次重啟同個句子**：保留最後一次完整版即可。

## 不適用此 Skill 的情況

- 別人主持演講而張辰瑋只是與談（這時可能進 `panel` 但仍由本流程處理）
- 論文研討會的會議論文發表（屬於 /papers?type=conference，由 papers 流程處理）
- 教會講道（屬於 [pong-sermon](../pong-sermon/SKILL.md) 流程）
