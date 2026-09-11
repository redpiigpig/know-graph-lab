---
name: qiangmian-transcribe
description: 千面上帝這個專案的兩條線 —— (A) 宗教史讀書會的轉錄流程：Gemini Audio 轉錄 + 潤稿 + PPT 上傳 R2 + 日期/YouTube/下載連結；(B) 七卷二十八章套書的寫作管線：目錄 docx ＋ 書摘 xlsx（1,960 條）＋ 讀書會逐字稿 ＋ 逐章文獻研究，用 Gemini 逐節寫成通俗史筆，出 Drive 七卷 Word（真頁下註）與站上 /works/million-masks 書稿分頁。Use when 要轉錄或潤稿讀書會某一集、要寫或重寫套書某一章、要改文風/篇幅/註釋規則、要重出 Word、要補研究筆記，或使用者提到「千面上帝」「宗教史讀書會」「套書」。
---


> ⚙️ **引擎政策（2026-06-04 統一）**：所有 LLM 工作一律 **Gemini（主，4 keys 輪流）→ NVIDIA（輝達 `https://integrate.api.nvidia.com/v1`，文字模型 `deepseek-ai/deepseek-v4-flash-0731`，4 把 key 輪流＋間隔節流避 429）→ Haiku（最後救急；前兩個免費池都用罄才動）**。`translate_ebook_to_zh.py --engine auto` 預設即此鏈。視覺／OCR 類仍走 Gemini Vision／Haiku Vision（NVIDIA vision 尚未驗證）。例外：/coach 互動聊天為 NVIDIA qwen3-next 主、Gemini 後備（見 [[feedback_coach_nvidia_engine]]）。見 [[feedback_engine_nvidia_no_haiku]]。

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 宗教史讀書會 — 完整自動化流程

> 🚨 **`G:` 不見了＝Drive 卡住，不是掛掉。** Drive 路徑報找不到檔案時，先
> `Test-Path 'G:\我的雲端硬碟'`；False 就結束 `GoogleDriveFS` 再跑
> `"C:\Program Files\Google\Drive File Stream\launch.bat"`，約 20 秒掛回來，
> 未上傳的檔不會掉。程序在跑不等於磁碟在（全文見 CLAUDE.md）。


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
http://localhost:3004/works/million-masks/reading-club/[id]
```

PPT 已在初始化時全部上傳到 R2（`qiangmian-ppt/ep{N:02d}.pptx`），轉錄腳本自動從 PPT 檔名取日期並填入 DB。

---

## 來源資料

| 資料 | 位置 |
|---|---|
| YouTube 播放清單 | `https://www.youtube.com/playlist?list=PLNdU3g_-OSshfnyOakO5exMMvnSNeuIjZ`（25 集）|
| PPT 投影片 | `G:/我的雲端硬碟/資料/知識圖工作室/讀書會/千面上帝宗教史讀書會/*.pptx`（29 個，按 YYYY.MM.DD 排序）|
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
    json={'project_slug': 'million-masks', 'episode': N, 'title': '...', 'content': polished},
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
-- video_transcripts 欄位（千面上帝 相關）
id            uuid
project_slug  text  -- 'million-masks'（DB slug；URL: /works/million-masks）
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
| `GET /api/works/million-masks-readings` | 列出所有集數（index 頁用）|
| `GET /api/works/transcript/[id]` | 單集全文（content + video_date + youtube_id + ppt_r2_key）|
| `GET /api/works/ppt-download/[id]` | 生成 R2 pre-signed URL（1 小時有效）並 redirect 下載 |

---

## 頁面

- 列表：`http://localhost:3004/works/million-masks`
- 單集：`http://localhost:3004/works/million-masks/reading-club/[id]`

單集頁標題下方顯示：日期 badge、YouTube 紅色按鈕、投影片下載琥珀色按鈕。

---

## 已完成集數（2026-05-07 快照，已過時）

| 集數 | 標題 | 狀態 |
|---|---|---|
| 1 | 第一章、被拋入世界的萬物之靈 | ✅ 轉錄 + 潤稿完成 |
| 2–5 | 第二～五章 | ✅ 轉錄完成（舊 Whisper，品質差，待潤稿）|
| 6–25 | 第六章以後 | ⏳ 待轉錄 |

PPT ep01–ep29 全部已上傳 R2。

> 📌 **2026-05-07 之後由 `scripts/overnight_qiangmian.py` 整晚自動化接手**：Phase 1＝對 DB 已完整的 Gemini 轉錄跑 Haiku 潤稿（預設 ep 3–6、8–11）；Phase 2＝缺失/截斷集先 local Whisper 轉錄再 Haiku 潤稿（預設 ep 2、7、12–25；`--polish`/`--transcribe` 可覆寫）。各集現況以 DB `video_transcripts`（project_slug=million-masks）為準，上表僅為歷史快照。

---

## 注意事項

- Gemini 2.5 Flash 有時 503（高需求）→ 等幾分鐘重試，或換 Gemini_API_Key_2/3/4
- R2 PPT 無公開 URL → 必須透過 `/api/works/ppt-download/[id]` 端點取得 signed URL
- 轉錄腳本已支援多把 `Gemini_API_Key_*` **自動輪替**（429 時自動換下一把 key；commit `590a7e3a`，見 `transcribe_qiangmian_gemini.py` 的 `GEMINI_KEYS`）

---

# 第二條線：七卷套書的寫作管線

> 2026-09-05 建立。讀書會是素材，這一節是把素材寫成書。

## 素材三源，以及它們的編號互不相通

| 素材 | 位置 | 份量 |
|---|---|---|
| 目錄（定稿） | `stores/千面上帝/千面上帝：目錄.docx` | 七卷 28 章，每章 5–7 節 |
| 書摘 | `stores/千面上帝/千面上帝：書摘.xlsx` | 28 分頁、1,960 條、177 萬字，98% 帶出處 |
| 讀書會逐字稿 | Supabase `video_transcripts`（project_slug=million-masks） | 25 集 |
| 文獻研究 | `data/qianmian/research/chNN.json` | 28 章、228 筆（進版控） |
| 書目 | Supabase `books` | 116 筆完整出版資訊，供頁下註補全 |

🚨 **最大的坑：三套「第 N 章」不是同一套編號。** 目錄是後來重排過的定稿，書摘分頁與讀書會集數沿用舊章序。全部以目錄為準，靠標題比對，**絕不能拿序號當鍵**（見 [[feedback_reader_silent_failures]]）。人工對應表寫死在 `scripts/qianmian_sources.py` 的 `SHEET_MAP`：

- 書摘「十一、經書的子民」→ 目錄第九章（被擄後猶太教經書化＝該章「上帝的究極進化」「尼希米圍牆」兩節）
- 書摘「二十一、唯獨信心的信仰」→ 目錄第二十一章「良心的改革」（同章改名）
- 書摘「六、立約與征服的血祭」「七、王國與聖殿的詩篇」→ 目錄第六、七章（同章改名）
- 🚨 **一個分頁可能對到兩章。** 舊目錄的「宇宙城邦的公民」後來被拆成新目錄的第十一、十二兩章，分頁沒跟著拆。整頁塞給第十一章的結果是：孔雀王朝、阿育王石刻、考底利耶《政事論》、董仲舒、漢武帝封禪、布匿戰爭、西塞羅、凱撒全壓在一個用不到它們的章裡，而第十二章成了全書唯一「沒素材」的一章（第一版只寫出 5,366 字）。**素材一直都在，只是分錯章。**
  解法是分頁指派完之後再按主題撿一次，見 `qianmian_sources.py` 的 `TO_CH12` 與 `FROM_CHAPTERS`；撿回 58 條之後重寫，8,177 字／38 註。
  判斷「該不該搬」的方法：先 grep 目標章與來源章各自提到那些關鍵詞幾次。第十一章只提 0–2 次，代表它根本沒用到，可以整批搬走且不會重複；若兩邊都提很多，就是真的重疊，要改動綱要而不是搬素材。

逐字稿的標題正規化要一起吃掉 `(上)(中)(下)(終)`、結尾裸露的「下」、以及同場分段的 `-1 -2 -3`。

## 四步

```
python scripts/qianmian_sources.py                 # 三源彙整 → output/qianmian/sources/chNN.json
（研究筆記由人／Claude 寫進 data/qianmian/research/）
python scripts/qianmian_write.py --chapters 1-28   # Gemini 寫 → output/qianmian/chapters/chNN.md
─── 以下四步是收尾，每一步都可以重跑，看門人會自動跑 ───
python scripts/qianmian_repair.py                  # 補殘留註記號、註號重排成閱讀順序
python scripts/qianmian_names.py                   # 拿詞庫掃譯名（先看報告）
python scripts/qianmian_names.py --fix 蘇美        # 逐個套用（只套同一對象的拼法差異）
python scripts/qianmian_check.py                   # 七類靜默錯誤稽核
python scripts/qianmian_publish.py                 # → public/content/million-masks-book/（站上讀）
python scripts/qianmian_docx.py                    # → Drive 七卷 .docx（真頁下註）
```

## 稽核與收尾（這一段是踩出來的，不要省）

`qianmian_check.py` 查八件事：缺節／節名被改寫／殘留 `〔註:E12〕`／漏出 prompt 標籤／
註號不連續／引用與註文對不上／殘留 markdown／篇幅異常偏短。

**這條管線的所有錯誤都長得像成功。** 每一項都是「檔案存在、頁面正常、字數也對，
只是內容錯了」。所以每次寫完一定要跑，而且**抽查要抽中間的章與中間的節**，
不要只看頭尾（見 [[feedback_reader_silent_failures]]）。實際抓到過的：

| 抓到的 | 若沒抓到會怎樣 |
|---|---|
| 66 個殘留的多來源記號 `〔註:E92, E107〕` | 書上直接印出內部記號 |
| 節標題被譯名替換改掉 | 該章對不回目錄，而且頁面完全正常 |
| 掉了一整節 | 檔案看起來正常，只是少一節 |
| 沒有 E/R 前綴的壞記號 | 猜編號＝假註釋，比不標更糟 |
| 引文碎片印在正文裡 | 出處欄折行造成，Word 會印成一個段落 |
| 漏出 `〔素材三〕` 這類 prompt 標籤 | 印出去直接穿幫 |
| `*Mayim*` 這種 markdown 斜體 | Word 會原樣印出星號 |
| 一整批（導言＋兩節）沒回來卻標成 ✓ | 少半章，而檔案完全正常 |

註釋格式另外要用**精確**判準查，不能用模糊比對：一個 `《` 還沒閉合就撞到 `〉`，
就是舊規則重複包裝造成的毀損。用「書名號不成對」會漏掉「成對但包錯層」的情況。

## 🚨 出處字串的三個坑（`qianmian_cite.py`）

書摘的「出處」那一欄是人手打的，格式比想像中髒。三件事都會生出**看起來正常、
印出來卻毀掉**的註釋：

1. **儲存格裡有換行。** 書名在 Excel 裡折了行，出處字串就帶著 `
`。註文帶換行寫進
   markdown，一條註會裂成兩行——前半成了沒有 `》`、沒有頁碼的殘缺註，後半掉進正文，
   在 Word 與網站上印成一個段落。`format()` 第一件事就是攤平空白。
2. **出處自己帶了 `〈〉《》`。** 例如「周伯戡，〈北魏僧曹制度考──兼論中國僧官的起源〉，
   《臺大歷史學報》第67期」。再包一層 `《》` 會變成 `《…〉，《…》》`。所以先檢查
   `marked = any(c in title for c in "《》〈〉")`，已經有標點的原樣用。
3. **書名裡有全形冒號。**「巴比倫：美索不達米亞和文明的誕生」——別拿冒號去切欄位。

🚨 **這些坑修好之後，不要試圖「把已經散在正文裡的碎片縫回註釋」。** 試過兩次都出錯：
碎片與殘缺註的順序不一致（一條註可能含多個來源、每個都被折行），位置配對會配錯；
改用「內容驗證」又會挑到「單獨看合法、其實屬於另一條註」的碎片，把原本正確的註改壞。
**正確做法是把受影響的章整章重寫**——Citer 修好之後重寫出來的註天生就是對的，
零猜測。判斷受影響的章用「書名號不成對」這個精確判準，不要用模糊比對。

## 譯名：單位是「每一處」，不是「每一組詞」

使用者的原則：**一個一個看，不能整批替換**。踩過的四個具體陷阱：

| 陷阱 | 實例 | 後果 |
|---|---|---|
| 同一個詞指兩個對象 | 「奧斯曼」既是第三任哈里發（Uthman）也是鄂圖曼土耳其 | 整批換會把哈里發改名 |
| 同名不同人 | 第 16 章的「奧古斯丁」是**坎特伯雷的**奧古斯丁，不是希波的 | 換成「希波的奧古斯丁」＝製造事實錯誤 |
| 異名其實是普通名詞 | 「征服者」在詞庫裡對到穆罕默德二世，但書裡多處指西班牙征服者 | 毀掉正文 |
| 節標題被一起改掉 | `## 冥界的主宰(奧西里斯信仰…)` 被改成歐西里斯 | 標題是對回目錄的鍵，改了稽核就對不上（已加保護） |

還有一個不在替換範圍、但要記住的分辨：詞庫的「X-民族帝國」（伍麥亞-阿拉伯帝國、鄂圖曼-土耳其帝國）是**條目命名格式**，不是行文說法。正文寫「伍麥亞王朝」是對的；該統一的只有音譯（倭馬亞→伍麥亞、阿巴斯→阿拔斯）。

`--fix 定名` 用來套「同一對象、拼法不同」那一類；`--replace 舊=新` 用來做逐詞的音譯統一（同一個字指兩個對象時只能用這個）。兩者都跳過 `##` 標題行與中間點後綴（否則馬克斯‧繆勒、馬克斯‧韋伯會被改成馬克思）。

**譯名統一**走 `qianmian_names.py`，拿 `/translation-glossary` 的 2,210 個定名當權威
（[[feedback_glossary_strict_authority]]）。🚨 **不能無差別套用**——詞庫裡有「拜占庭→
君士坦丁堡」「征服者→穆罕默德二世」「奧古斯丁→希波的奧古斯丁」這種**指涉不同**的對子，
套下去會毀掉正文。所以三道閘：異名本身也是定名就跳過、一個異名對到兩個定名就不碰、
`--fix` 只逐個定名套用。另外替換要避開 `## 節標題`（是對回目錄的鍵）與中間點後綴
（否則馬克斯‧繆勒、馬克斯‧韋伯會被改成馬克思）。

`qianmian_write.py` 一章跑三種呼叫，而且**刻意用三個不同型號**（理由見下一節的額度）：

| 步驟 | 型號（環境變數可換） | 次數 |
|---|---|---|
| 分配（書摘按標題分派到各節） | `QIANMIAN_MODEL_ALLOC`＝gemini-2.5-flash-lite | 1／章 |
| 寫作（**一章兩次**：前半＋導言、後半＋結語） | `QIANMIAN_MODEL`＝gemini-3-flash-preview | 2／章 |
| 校對（只改錯字病句） | `QIANMIAN_MODEL_POLISH`＝gemini-3.1-flash-lite | 2／章 |

**寫作為什麼不逐節呼叫**：逐節要 ~15 次／章，排不進日額度；而且同一次生成裡節與節的銜接比較自然。代價是模型會把每節壓縮（七節一次寫只給 10,900 字），所以 prompt 要把「每節都要寫足」講死，`--length` 也要開得比實際目標高（預設 3000–3500 才會落在每章 ~18,000 字）。

已有 `chNN.md` 的章直接跳過，所以整支可以無限重跑。

## 註釋為什麼掰不出來

模型只准標 `〔註:E12〕`（書摘）或 `〔註:R3〕`（研究筆記）這種**指回素材編號**的記號，prompt 裡明列該節的合法編號，禁止自己寫出處。腳本再把編號換成頁下註流水號，註文由 `qianmian_cite.Citer` 依 DB `books` 補成正式體例：

> 游斌，《希伯來聖經的文本、歷史與思想世界》（北京：宗教文化出版社，2013年），頁25。

編號對不上的一律丟棄並回報。**這是整條管線最重要的設計**：頁下註裡出現查無此書的引用，比沒有註更糟。

註釋走 `scripts/docx_footnotes.py` 的 `Footnotes`，是 Word 認得的真 footnote（排在當頁下緣、自動編號），不是章末尾註。

## 三件模型守不住、必須由程式把關的事

1. **註釋數量。** prompt 寫「一節最多 10 個」照樣冒出 30 個（第一版第一章跑出 **184 個註**，平均每 137 字一個）。`resolve_notes(..., cap=10)` 直接把超額的記號拿掉。

2. **整批沒回來卻照樣落檔。** 第 2 章連續兩次「✓ 寫完」卻少了半章——第一批（導言＋前兩節）整批沒回來，程式只印警告就把殘缺的內容寫成檔案，**看起來完全正常**。現在缺段先重試三次，仍缺就整章不落檔、留給下次重跑。這是這條管線最該擋掉的失敗模式。

3. **篇幅——這件事最後是接受現實，不是解決。** 模型對中文長度有自己的偏好，喊數字的邊際效果很小：

   | 一次寫幾節 | 結果 |
   |---|---|
   | 七節（整章一次） | 10,907 字 |
   | 四節（一章兩次） | 12,879 字 |
   | 兩節（一章三次） | 12,401 字 |
   | 兩節＋「分到的書摘都要用上」 | ~12,300 字（定案） |

   最有效的槓桿是**素材覆蓋**（「這一節分到的書摘都要用上」）而不是字數。`--length` 要開得比目標高（設 3500–4000 才寫到 3,000 上下）。全書最後平均每章 12,091 字——以 5–7 節的通俗史章來說是正常的章長，別再為了追數字重跑，每重跑一輪就吃掉當天三分之一的額度。

## Gemini 免費層現況（2026-09-05 實測，七把 key）

🚨 **免費層是「每個型號各自 20 次／天／key」在管，不是每分鐘**。七把 key ＝每個型號 140 次／天，隔天才恢復。這是這條管線所有設計的前提：

- `gemini-3-flash-preview` ✅ 正文用它。三個型號同一節比對下來文筆最好——長度守得住、研究筆記融得自然
- `gemini-2.5-flash` ✅ 品質也夠（比 3.5-flash 更紮實、少空轉），但同樣 20／天
- `gemini-3.5-flash`／`3.6-flash` ⚠️ 一樣 20／天，`quotaId` 明寫 `GenerateRequestsPerDayPerProjectPerModel-FreeTier = 20`
- `gemini-3.1-pro-preview` ❌ 七把全 429（pro 不在免費層）
- `gemini-2.5-pro` ❌ 404，新帳號已下架
- `gemini-flash-latest`／`3.7`／`3.8-flash` ⚠️ 常 503
- **Google Search grounding ❌ 七把全 429** ——所以「查最新研究」這一層**不能交給 Gemini 自動做**，研究筆記是人工／Claude 寫進 `data/qianmian/research/` 的。

**因應**：①一章只呼叫兩次寫作 ②把分配與校對分流到別的型號，各吃各的額度。整套書因此是 56＋28＋56 次，三個型號都塞得下。開跑前先發一次探測請求確認型號沒被打爆。見 [[reference_gemini_free_tier_quotas]]。

## 排程

整套 28 章要跑數小時，分四條線（1-7／8-14／15-21／22-28）並行。看門人 `scripts/qianmian_keeper.py` 由排程 `KGL_Qianmian_Keeper` 每 30 分鐘檢查一次，只有在一條線都沒在跑時才重新拉起（章寫完會留檔，重跑自動跳過）。

看門人在 28 章齊了之後會自己跑收尾（補記號 → 統一譯名 → 稽核 → 上架 → 出 Word）並 `Disable-ScheduledTask` 停用自己，判準看 `output/qianmian/chapters/` 有沒有 28 個檔、不是看排程狀態（見 [[feedback_disable_finished_schedules]]）。建立排程時 `-RepetitionInterval` 要留 `Duration` 空白，否則重複會提早到期。

🚨 **額度是跟別的專案搶的。** 同一批 `Gemini_API_Key_*` 其他 session 也在用（祆教經典、翻譯艦隊…），所以「昨天還有額度」不代表今天輪得到。跑之前先探測，跑不完就交給看門人，不要硬等。

## 現況（2026-09-06 完成）

28 章、**342,155 字**、**1,157 個頁下註**，稽核全過，七卷 Word 已出、站上可讀。
最短是第 12 章 8,177 字（素材本來就少），最長第 17 章 19,667 字（九節）。
每卷的 Word 註腳「參照數＝註文數」逐卷核對過。

仍待使用者定奪的兩件：`data/qianmian/research/` 那 228 筆研究書目是 Claude 查的，
付印前要抽查；以及上表那四組指涉不同的譯名維持原樣沒動。

## 成品去處

- **Drive**：`G:\我的雲端硬碟\資料\知識圖工作室\寫作計畫\書籍寫作\千面上帝\千面上帝　第N卷　卷名.docx`（成品不進 git）
- **站上**：`/works/million-masks` 的「書稿」分頁 → `/works/million-masks/book/[章號]`，內容在 `public/content/million-masks-book/`（進版控，與讀書會逐字稿同一慣例）

## 記憶庫併入：project_qianmian_book

2026-09-06 完成：28 章、342,155 字、1,157 個頁下註，七卷 Word 在 Drive、站上 /works/million-masks 書稿分頁可讀，稽核全過。

把《千面上帝》從素材寫成七卷二十八章的套書。體例是使用者定的：**通俗史筆＋頁下註**（不是章末尾註），成品出 Drive 七卷 Word ＋ 站上 `/works/million-masks` 書稿分頁。

**素材三源，編號互不相通**——這是最容易靜默出錯的地方：

- 目錄 `stores/千面上帝/千面上帝：目錄.docx` 是**後來重排過的定稿**，以它為準
- 書摘 `千面上帝：書摘.xlsx`（28 分頁、1,960 條、177 萬字）與讀書會 25 集**沿用舊章序**
- 對應要靠標題比對，人工表在 `scripts/qianmian_sources.py` 的 `SHEET_MAP`：書摘「經書的子民」→ 目錄第九章、「唯獨信心的信仰」→ 第廿一章
- 🚨 **一個書摘分頁可能對到兩章**：舊「宇宙城邦的公民」被拆成新目錄第十一、十二章，分頁沒跟著拆，第十二章因此變成「沒素材」（其實 58 條全壓在第十一章）。判斷能不能搬：grep 兩章各提那些關鍵詞幾次，來源章只提 0–2 次就是沒用到

**註釋的防偽設計**：模型只准標 `〔註:E12〕`（書摘）`〔註:R3〕`（研究筆記）這種指回素材編號的記號，prompt 明列該節合法編號、禁止自己寫出處；腳本再換成頁下註流水號，註文由 `qianmian_cite.Citer` 依 Supabase `books` 補成正式體例。對不上的編號一律丟棄。頁下註用 `scripts/docx_footnotes.py` 的真 Word footnote。

**兩件模型守不住、要程式把關的事**：註釋數量（寫「最多 10 個」照樣冒 30 個，第一版跑出 184 個註）與篇幅（寫 3000 字會給 5500）。都改成 `resolve_notes(cap=10)` 與縮短 `--length` 硬壓。

**譯名**：單位是「每一處」不是「每一組詞」（使用者定的原則）。`qianmian_names.py` 拿 /translation-glossary 掃全書。🚨 同一個詞可能指兩個對象（「奧斯曼」＝哈里發 Uthman ＋鄂圖曼土耳其）、同名可能不同人（第 16 章的奧古斯丁是坎特伯雷的不是希波的）。🚨 詞庫裡有「拜占庭→君士坦丁堡」「征服者→穆罕默德二世」這種**指涉不同**的對子，不能無差別套用；替換還要避開 `## 節標題`（對回目錄的鍵）與中間點後綴（馬克斯‧繆勒會被改壞）。

**出處字串三個坑**（`qianmian_cite.py`）：Excel 儲存格裡有換行→註文帶換行→一條註裂成兩行、後半印進正文；出處自帶〈〉《》→再包一層變成 `《…〉，《…》》`；書名裡有全形冒號。🚨 碎片**不要縫**，位置配對與內容驗證都會配錯（第二次還把正確的註改壞），受影響的章整章重寫。

**Why:** 這套書的價值在於 1,960 條帶出處的書摘；註釋若被掰出來，整套書的可信度就沒了。

**How to apply:** 動任何一章前先讀 `.claude/skills/qiangmian-transcribe/SKILL.md` 的「第二條線」。研究筆記在 `data/qianmian/research/`（進版控，Claude 寫的，付印前要抽查）。整套跑要開排程 `KGL_Qianmian_Keeper`，**28 章寫完記得停掉**。相關：[[reference_gemini_free_tier_quotas]]、[[feedback_reader_silent_failures]]、[[feedback_disable_finished_schedules]]。

**索引壓縮時移入（2026-09-11）：**
- 註數與篇幅模型守不住要程式硬壓

## 索引補記

- 第12章無素材靠研究撐
