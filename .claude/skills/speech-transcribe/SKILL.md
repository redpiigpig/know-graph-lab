---
name: speech-transcribe
description: 受邀演講／學系專題講座／公開講座的完整 pipeline — 海報資訊 OCR → ffmpeg 切音 → Gemini Audio 平行轉錄（含 PPT context）→ Claude 對話內清稿 → PPT＋海報上 R2 → 寫入 public/content/speech/ 並更新 stores/speech.ts。Use when 使用者有新一場演講的「海報＋錄音＋PPT」要上架到 /speech。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 演講活動 — 海報＋錄音＋PPT → /speech 上架 Pipeline

把一場演講（學系專題講座、研討會主題演講、公開講座等）從**海報＋錄音＋PPT** 一路整理成 `/speech/[id]` 上可閱讀的逐字稿頁面，PPT 與海報放到 R2 供下載／顯示。

## 路徑歷史紀錄

舊版叫 `/talks`、`stores/talks.ts`、`server/api/talks/`、`pages/talks/`、`public/content/talks/`、`.claude/skills/talks-transcribe/`。**已全數改名為 `speech`**（commit 看 `d34c63d`）。R2 key 例外 — PPT 的 R2 key 仍維持 `talks-ppt/*.pptx` 不變（避免重新上傳）。

## 總覽

```
海報（jpg/png）           ─┐
PPT（pptx）               ─┼─→ Claude 解析 metadata（標題／日期／場地／主辦）
錄音（m4a/mp3）           ─┘
       │
       ├─→ ffmpeg 切成 ≤22 分鐘片段（_tmp_audio/speech/[date-slug]/partN.m4a）
       │   ⚠️ Gemini 503 重投擲時要切更小（≤11 min）
       │
       ├─→ python-pptx 抽 PPT 文字 → ppt_context.txt
       │
       ├─→ R2 上傳 PPT（talks-ppt/[date-slug].pptx）+ 海報（speech-posters/[date-slug].jpg）
       │
       ├─→ Gemini 2.5 Flash 平行轉錄（每段獨立 prompt + PPT context）
       │
       ├─→ Claude 對話中清稿（刪口語填充、合併段落、加小標、修正聽錯、移除休息）
       │
       ├─→ Fact-check：講者口誤、人名、機構、書名都要 web search 驗證一次
       │
       └─→ public/content/speech/[date-slug].txt  +  stores/speech.ts 加 entry
                +  server/api/speech/{ppt-download,poster,edit}/[id] mapping
```

## 資料命名與位置

| 資料 | 位置 |
|---|---|
| 演講錄音 | `G:/我的雲端硬碟/[單位]/[相關資料夾]/新錄音 NN.m4a` 或 `[日期]_[主題].mp3` |
| PPT | 同上資料夾 `[YYYY.MM.DD][主題].pptx` |
| 海報 | 使用者貼進對話的截圖（或別處圖檔）|
| 暫存 | `_tmp_audio/speech/[YYYY-MM-DD]/` — partN.m4a、partN_raw.txt、ppt_context.txt、ppt_images/ |
| R2 PPT | `talks-ppt/[YYYY-MM-DD]-[slug].pptx`（bucket = `knowgraphlab`）|
| R2 海報 | `speech-posters/[YYYY-MM-DD]-[slug].jpg`（同 bucket）|
| 上架逐字稿 | `public/content/speech/[YYYY-MM-DD]-[slug].txt` ⚠️ **必須 .txt 不能 .md**（見坑） |
| Store | [`stores/speech.ts`](../../../stores/speech.ts) — `useSpeechStore` |

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
- **主辦／課程／系所** — ⚠️ 常被誤判：海報上若同時有 「系所」與「中心」名稱，主辦通常是「中心」（如玄奘大學台灣佛教研究中心，不是宗教與文化學系）。**清稿前回頭跟使用者確認一次**。
- **主講人銜頭**（如「兼任講師」、「碩士研究生」）
- **海報主圖風格**（可作後續 UI 配色提示）

**注意西元年判讀**：使用者習慣寫民國年；海報若顯示 `2025` 但實際是台灣民國 `114`，要對照當下日期判斷。例：海報寫「2025.05.19 週二」，當日是 2026-05-19 週二，那海報是檔名沿用舊年但實際是 2026。

**PPT 第一張不等於海報**：python-pptx 抽出的 image1.jpg 通常是 PPT 封面圖（書封、會場照等），不是宣傳海報。海報需要使用者另外提供。

---

## Step 2 — 切音檔

```bash
# 先看長度
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "原檔.m4a"
```

切成 ≤22 分鐘片段（避免 Gemini 2.5 Flash 處理長音檔卡進重複迴圈）：

```bash
mkdir -p _tmp_audio/speech/YYYY-MM-DD
for i in 0 1 2 3; do
  start=$((i * 1320))
  ffmpeg -y -i "原檔.m4a" -ss $start -t 1320 -c copy \
    "_tmp_audio/speech/YYYY-MM-DD/part$((i+1)).m4a"
done
# 最後一段視長度調 -t
ffmpeg -y -i "原檔.m4a" -ss 5280 -t 1200 -c copy \
  "_tmp_audio/speech/YYYY-MM-DD/part5.m4a"
```

**107 分鐘為例**：5 段（22+22+22+22+18 min）。

---

## Step 3 — 抽 PPT 文字當 context（+ 順便抽圖確認海報來源）

```bash
python -c "
import zipfile, shutil
from pathlib import Path
from pptx import Presentation

ppt = 'PPT路徑.pptx'
out = Path('_tmp_audio/speech/YYYY-MM-DD')
out.mkdir(parents=True, exist_ok=True)

# 抽文字
p = Presentation(ppt)
lines = []
for i, slide in enumerate(p.slides, 1):
    lines.append(f'=== Slide {i} ===')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                t = para.text.strip()
                if t: lines.append(t)
    lines.append('')
(out / 'ppt_context.txt').write_text('\n'.join(lines), encoding='utf-8')

# 抽圖（看裡面有沒有真的海報；通常沒有，只有書封）
img_dir = out / 'ppt_images'
img_dir.mkdir(exist_ok=True)
with zipfile.ZipFile(ppt) as z:
    for m in [n for n in z.namelist() if n.startswith('ppt/media/')]:
        with z.open(m) as src, open(img_dir / Path(m).name, 'wb') as dst:
            shutil.copyfileobj(src, dst)
print('done')
"
```

PPT 文字會餵給 Gemini 當 context，幫忙正確轉錄人名／書名／術語。

---

## Step 4 — Gemini 平行轉錄

```bash
# 每段一個 background task；scripts/transcribe_talk_gemini.py 已有 retry-with-backoff
for n in 1 2 3 4 5; do
  python scripts/transcribe_talk_gemini.py \
    _tmp_audio/speech/YYYY-MM-DD/part$n.m4a \
    --out _tmp_audio/speech/YYYY-MM-DD/part${n}_raw.txt \
    --ppt-text _tmp_audio/speech/YYYY-MM-DD/ppt_context.txt \
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
- 支援 `TALK_GEMINI_MODEL` 環境變數覆寫模型（預設 `gemini-2.5-flash`）

### Gemini 高需求時段 503 的處理（2026-05-19 實戰經驗）

**現象**：所有 4 把 key 連續 503 / `[Errno 10054] 遠端主機強制關閉連線`。整個服務都掛了，不只是個別 key 配額問題。

**處理層級**：

1. 等 5–10 分鐘整體服務恢復，重跑失敗的 part
2. 還是失敗 → **切更小**：22 分鐘 part 切成 2x 11 分鐘（part1a/part1b）
3. 換模型：`TALK_GEMINI_MODEL=gemini-2.5-pro python scripts/...`（但 Pro 同樣會受影響）
4. ⚠️ `gemini-2.0-flash` 在 free tier 是 **limit:0** — 不能用，會吐 429

**part1 一次成功率最低**（多次重試後才在 11 分鐘切片上成功）。建議：對長講座 **預設就切 11 分鐘**，不要省那一半的 round-trip。

---

## Step 5 — Claude 對話中清稿

Gemini 原始輸出已有講者標籤＋繁體＋分段，但需要：

1. **刪 Gemini 開場白**：part4/part5 常出現「好的，這是一段繁體中文的逐字稿。請注意⋯⋯」這類元說明，整段刪
2. **刪口語填充**：「就是說」「這樣子」「嘛」「啊」、口吃重複（「我、我、我」）、聽眾的「嗯／是」短回應
3. **修正連續重複**：Gemini 偶爾會把同一個字打 5–10 次（連續結巴），縮成 1 次
4. **移除休息時段**：使用者明確告知「中間有 10 分鐘休息」— 找出對應 part 中的停頓（通常 part3 中段），刪除休息中的雜聲段落、點名、隨堂提問
5. **合併破碎段落**：Gemini 會在每個停頓拆段，整理時把同一主題合併成 1–3 段
6. **加 `## 小標`**：依 PPT 章節對應（PART 1 / PART 2 / Q&A 等）插入 markdown 小標
7. **修正聽錯人名／書名**：
   - 趙文詞 / Richard Madsen、貝拉 / Robert Bellah
   - 證嚴、聖嚴、星雲、印順、昭慧、白聖、惟覺
   - 《民主妙法》、《心靈的習性》(*Habits of the Heart*)
   - 法鼓山、慈濟、佛光山、中台禪寺、福智、靈鷲山、弘誓
   - 卡理斯瑪（charisma）、人間佛教、解嚴、政教互動
   - 「1970 年代」常被聽成「19780 年代」這種數字 hiccup
8. **Q&A 段落**：在主體演講後插入 `## Q&A` 小標；保留提問者編號（A/B/C），講者用「講者：」

### 使用者偏好（2026-05 玄奘場確認）

- **書名、學術著作的英文要 *italic***（`*Title*` markdown）
- **宗教社會學專有名詞要加英文括號**：
  - 卡理斯瑪 (charisma)、日常化 (routinization)
  - 公民社會 (civil society)、民主公民 (democratic citizens)
  - 中產階級 (middle class)、道德秩序 (moral order)
  - 民主基因 (democratic genes)、制度化 (institutionalization)
  - 先知型 (prophetic)、祭司型 (priestly)
  - 三權分立 (separation of powers)、玻璃天花板 (glass ceiling)
  - 宗教市場理論 (religious market theory / religious economy)
  - 世俗主義 (laïcité / secularism)、文明衝突論 (*The Clash of Civilizations*)
  - 新教倫理與資本主義精神 (*Die protestantische Ethik und der Geist des Kapitalismus*)
  - 逃避自由 (*Escape from Freedom*)
- **書資訊一律以權威來源（出版社網站、博客來、Wikipedia、Google Scholar）為準**，不採信講者口頭說法

### Fact-check 清單（必跑）

清稿後**必須跑一輪 web search 校驗**，因為講者常會口誤：

| 項目 | 玄奘場實際校驗結果 |
|---|---|
| 作者學術單位 | 趙文詞口誤「耶魯」→ 實為 UC San Diego 社會學榮譽教授 |
| 中文版出版社 | 講者說「聯經」→ 實為國立臺灣大學出版中心（2015 年，黃雄銘譯註） |
| 原書出版社 / 年份 | UC Press 2007 |
| 法子數 / 性別 | 講者說「不太確定」→ 聖嚴 12 法子當中有 4 位比丘尼：**果鏡、果廣、果肇、果毅** |
| 數字年份 | Gemini 把「1970」聽成「19780」要修 |

校驗工具：WebSearch + WebFetch（books.com.tw 通常 403，改查臺大出版中心官網／Wikipedia／Google Scholar）。

### 輸出格式（`public/content/speech/[id].txt`）

⚠️ **副檔名一定要 .txt 不能 .md**：ofetch 預設對 `text/markdown` 嘗試 JSON 解析會炸（用 .md 結果 `error` 為真、頁面顯示「無法載入逐字稿」）。

```markdown
## 引言：為什麼從宗教社會學談民主

好，今天的講題我們要先跟大家介紹一本書。這本書是國立臺灣大學出版中心 2015 年出版的《民主妙法》（*Democracy's Dharma: ...*）⋯⋯

## 對話起點：《民主妙法》與作者趙文詞

⋯⋯馬克斯‧韋伯（Max Weber）的卡理斯瑪（charisma）⋯⋯

## PART 2 ‧ ...

## Q&A

提問A：[問題]

講者：[回答]

提問B：[問題]
```

渲染由 [pages/speech/[id].vue](../../../pages/speech/[id].vue) 處理：
- `## 文字` → 玫瑰色左線 h2（text-lg）
- `### 文字` → 玫瑰色 h3（text-base）
- `講者：/提問A：/主持人：` → 玫瑰色 chip + 換行
- `（休息／中斷）` → 灰斜體置中
- `*文字*` → `<em>` ／ `**文字**` → `<strong>`（v-html + inline() 處理）
- 正文 text-base / leading-8（比 /papers 還大 1.2x）
- 最外層 max-w-6xl（比 /papers max-w-3xl 寬 50%）

---

## Step 6 — 上傳 PPT + 海報到 R2

### PPT

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

### 海報（同上 boto3 模板，注意 PNG → JPG 壓縮）

```python
python -c "
import boto3
from pathlib import Path
from PIL import Image
_env = {...}  # 同上

# PNG → JPG 88% 通常 2 MB → 300 KB
img = Image.open('原檔.png')
if img.mode != 'RGB': img = img.convert('RGB')
img.save('/tmp/poster.jpg', 'JPEG', quality=88, optimize=True)

r2 = boto3.client(...)  # 同上
r2.upload_file('/tmp/poster.jpg', _env['R2_BUCKET'],
    'speech-posters/YYYY-MM-DD-slug.jpg',
    ExtraArgs={
        'ContentType': 'image/jpeg',
        'CacheControl': 'public, max-age=31536000'
    })
"
```

---

## Step 7 — 寫入 store + 3 個 API mapping

### 7a. [`stores/speech.ts`](../../../stores/speech.ts) — 加 entry

```ts
{
  id: '2026-05-19-hsuanchuang',
  title: '...',
  subtitle: '...',
  date: '2026-05-19',
  duration: '08:30–10:15',
  venue: '...',
  organizer: '...',  // ⚠️ 確認海報上是「系所」還是「中心」
  course: '...',     // 可選
  category: 'lecture',  // lecture/seminar/public/invited/panel
  hasTranscript: true,
  pptR2Key: 'talks-ppt/2026-05-19-hsuanchuang.pptx',
  posterPath: '/api/speech/poster/2026-05-19-hsuanchuang',  // 走 API redirect
  description: '...',
}
```

### 7b. [`server/api/speech/ppt-download/[id].get.ts`](../../../server/api/speech/ppt-download/[id].get.ts)

```ts
const SPEECH_PPT_KEYS: Record<string, { key: string; filename: string }> = {
  '[id]': {
    key: 'talks-ppt/[id].pptx',
    filename: '[人可讀檔名].pptx',
  },
}
```

### 7c. [`server/api/speech/poster/[id].get.ts`](../../../server/api/speech/poster/[id].get.ts)

```ts
const SPEECH_POSTER_KEYS: Record<string, string> = {
  '[id]': 'speech-posters/[id].jpg',
}
```

### 7d. [`server/api/speech/edit/[id].post.ts`](../../../server/api/speech/edit/[id].post.ts) — auth-gated 編輯

```ts
const ALLOWED_IDS = new Set([
  '[id]',  // ← 加新 entry 時要把 id 加進來
])
```

---

## Step 8 — 驗證 + commit

1. dev server 重啟確保 stores/api 更新
2. 瀏覽 `/speech` 看新項目出現
3. 點進 `/speech/[id]` 確認逐字稿渲染正常（注意：第一次測試常會載不到逐字稿，多半是 .md vs .txt 副檔名問題）
4. 點海報看是否能展開大圖（API redirect 到 R2 signed URL）
5. 點「下載投影片」測試 R2 signed URL
6. 登入後測試「編輯 → 儲存」流程
7. 依 [feedback_auto_push](../../../memory/feedback_auto_push.md) commit + push，message 例：
   `feat(speech): 新增 2026-05-19 玄奘宗教系專題講座`

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

## 常見坑（2026-05 玄奘場血淚實錄）

### 內容處理

- **PPT 檔名年份對不上實際日期**：使用者很常沿用舊版檔名（`2025.05.19...pptx` 實際是 2026）。一律以海報上的「週幾」對照當下日期判斷。
- **休息時段未標註**：使用者會口頭說「中間有 10 分鐘休息」，要在清稿時自己抓位置（多半在演講中段）。休息中會夾雜：點名、隨堂提問、PPT 索取等，全部刪掉。
- **Q&A 區段融在一起**：Gemini 不會自動標 Q&A vs 演講本體，要靠語氣轉折識別（「好，我們今天的演講就講到這邊」「有沒有同學想問問題？」等）。
- **錄音前後段**：開頭可能有「請問麥克風 OK 嗎？」這類調整，可整段刪。結尾可能掛在「謝謝大家」之後一段空白。
- **講者口頭用語錯誤**：例如把「第二」說成「第二第一」、「卡理斯瑪」說成「卡里斯瑪」等。要修正常見筆誤但保留語氣。
- **錄音中講者多次重啟同個句子**：保留最後一次完整版即可。
- **講者口誤事實**：機構（耶魯 vs UC San Diego）、出版社（聯經 vs 臺大出版中心）、人數（12 法子有幾位女性）— 一定要 fact-check。

### 技術坑

- **副檔名必須 .txt 不能 .md**：Nuxt `useFetch` / `$fetch` 預設對 `text/markdown` content-type 嘗試 JSON 解析會丟 SyntaxError，導致 `error` 為真、頁面顯示「無法載入逐字稿」。
- **`useFetch` 不要用 `responseType: 'text'`**：在新版 ofetch 不可靠，改用 `useAsyncData + $fetch + parseResponse: txt => txt` 強制純文字。
- **`pages/speech/[id].vue` 跟 `index.vue` 的 helper function 不共享**：`formatDate` 在 index.vue 定義過，但 [id].vue 也用到時要重新定義一份（不然 `_ctx.formatDate is not a function`）。
- **PPT 第一張圖不是海報**：python-pptx 抽出來的 image1.jpg 通常是書封／會場照，**不是宣傳海報**。海報要使用者另外提供（剪貼簿 / 存到根目錄 / 路徑 etc.）。
- **PNG 海報要轉 JPG**：原檔 PNG 常常 2 MB+；轉 JPG 88% quality 可以縮到 300 KB 上下不失真。
- **Gemini 503 不是個別 key 問題**：高需求時段所有 key 一起掛 + 連線重置（10054）。對策：等 5-10 min + 切更小 chunk（11 min）。
- **`gemini-2.0-flash` free tier 沒配額**：撞 429 limit:0，不能用。
- **ScheduleWakeup 不要連 schedule 多個**：等東西時排了 wakeup，東西在 wakeup 觸發前提早完成，會收到一堆過期的 wakeup 觸發，要識別出來不重做。

### UI 偏好

- 逐字稿 max-width `max-w-6xl`（1152px，比 papers 寬 50%）
- 正文 `text-base / leading-8`（比 papers 大 1.2x）
- 海報：列表卡片左側小張 + 詳情頁標題列左側小張（點擊用新分頁開原圖）；**逐字稿內文上方不要再放一張大的**
- 編輯模式：整篇 textarea 開啟（min-h-70vh、font-mono），不要 inline per-paragraph

---

## 不適用此 Skill 的情況

- 別人主持演講而張辰瑋只是與談（這時可能進 `panel` 但仍由本流程處理）
- 論文研討會的會議論文發表（屬於 /papers?type=conference，由 papers 流程處理）
- 教會講道（屬於 [pong-sermon](../pong-sermon/SKILL.md) 流程）
