---
name: pong-sermon
description: 龐君華牧師講道集所有相關流程合一 SKILL — ① Re-transcribe（YouTube→Whisper→Claude 清理→DB，處理 城中教會講道_YYYY.txt 的 ⏳ 未完成）② Polish（auto-cleaned 粗稿→publication 品質）③ Standardize（speaker label / preacher / occasion / title / scripture_ref backfill / 段落重組）④ Photo metadata（程序單照片→title / worship_team / songs / occasion / sermon_type backfill + non-Sunday calendar wire-up）。Trigger 例：「重做 2013 transcripts」「⏳ 未完成」「這篇 2024 太粗糙」「跑全集統一格式」「這份程序單對應 YYYY-MM-DD」「服事人員名單放到該場」。
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session。一說要傳截圖立刻提醒先確認尺寸；推薦 Win+Shift+S 或縮到 ≤ 1920px。

# 龐君華 講道集 — 全工作流 SKILL

四階段共用 `pong_sermons` + `pong_media` 表、共用 `scripts/pong-archive/sermon_redo.py` CLI（Phase 1-3）：

| 階段 | 何時用 | 輸入 → 輸出 |
|---|---|---|
| **① Re-transcribe** | DB 還沒 content，或 queue txt 有 `# ⏳ 未完成` | YouTube URL → Whisper raw → Claude 清理 → DB |
| **② Polish** | DB 已有 auto-cleaned 粗稿（很多 `，` 少 `。`、「大家祝禮平安」「感謝祖」、句子斷裂） | 粗稿 → 手工潤稿 → DB |
| **③ Standardize** | content 文字 OK 但 speaker label / preacher / occasion / title / 段落不規範 | 既有 content + metadata → 規範化 + backfill → DB |
| **④ Photo metadata** | 使用者貼程序單照片要 backfill | 照片 → title / 服事人員 / 詩歌 / occasion / sermon_type → DB（非主日還要 wire calendar） |

四個階段可以連著做（1→2→3 處理單篇 row；4 通常獨立，使用者一次給一份程序單）。

---

# 共用 Reference（所有階段都遵守）

## Gold standard

[`pong_sermons.id=20130106`](http://localhost:3001/pong-archive/sermons/20130106) 黃金標準：speaker label `龐君華牧師：` on line 1、blank line、long topical paragraphs、full punctuation、全繁體。

[Phase 4 photo metadata 範例] [`pong_sermons.id=20211120`](http://localhost:3000/pong-archive/sermons/20211120) — 城中教會 60 週年感恩禮拜，完整 worship_team JSON + worship_songs labelled-prefix + calendar special wire-up。

## Preacher title era map

| Era / 場合 | Title | DB value |
|---|---|---|
| Pre-**2019-05**（一般主日） | 牧師 | `龐君華牧師` |
| **2019-05** onwards（當選會督後，退休仍維持） | 會督 | `龐君華會督` |
| **年議會講道**（2019-05 前，以教區/牧職會長職分主理） | 牧職會長 | `龐君華牧職會長` |

⚠️ **2019 年 5 月才當選會督，在那之前一律不可標會督。** 2019-05 前一般主日是 `龐君華牧師`；但**在年議會（年議會禮拜，sermon_type=年議會禮拜）的講道**，是以「牧職會長」名義 → `龐君華牧職會長`（例：2017-05-19 / 2018-05-25 / 2019-02-22 三場年議會開閉幕禮拜）。退休後仍稱 會督，不退回牧師。Speaker label / preacher field 都依 sermon date 當時的職分。

## Paragraph / 標點 / 繁體 規則

1. **Speaker label**：First line `龐君華{title}：`，second line blank。Body paragraphs 不放 speaker label，除非另有講者。
2. **Traditional Chinese**。常見轉換：显→顯、经→經、历→歷、节→節、师→師、复→復/複、实→實、让→讓、应→應、关→關、国→國、体→體、学→學、礼→禮、圣→聖、处→處、谁→誰、题→題、别→別、简→簡、类→類、选→選、爱→愛、时→時、间→間、们→們、这→這、个→個、来→來、会→會、后→後、发→發。
3. **Punctuation**：全形 `，。：；！？「」『』——……（）`。Bible / 對話引言一律 `「」` 包。
4. **Paragraphs**：16–25 段，每段 200–800 字；topical shift 斷段（另一方面 / 所以 / 今天 / 但是 / 於是 / 我們看到 / 那麼 / 因此）。
5. **Preserve voice**：不改寫、不總結。保留 filler（呢、啊、喔、那）、口頭禪、講者用字。
6. **No markdown in body**：沒 `##`、`*`、`_`、`[]()`。Section heading 用 `【X】`。
7. **Closing prayer** ends in `阿們。`。

## Whisper 錯誤對照表

聖經 / 神學名詞：薄力人→伯利恆、灯山變象→登山變像、西里王→希律王、尼賽人/尼賽特→彌賽亞、三個佛事→三個博士、依麗撒海→伊麗莎白、聖靈彷彿鴿→聖靈彷彿鴿子般、化石架→畫十字架、一道書→一缸水/聖水盆、民宿→民間、暴命→奧秘、灵形→有形、高層（「展開一個高層」）→高潮、临死/临起/离洗/离醒→領洗/受洗、重温我們所力的約→重溫我們所立的約、武器（「領受新的武器」）→祝福/洗禮、非常小可→非同小可。

人名（牧師同工）：邱牧師 variants（求/丘/球/秋/熊/瓊/琼/窮/全/修/裘）→ 邱（邱泰耀牧師）；蕢牧師 variants（春/秦/祝/桂/窺/匱/餽）→ 蕢（蕢建華會督）。

招呼語：大家祝禮平安→大家平安；感謝祖→感謝主；`邱牧師，還有`→`邱牧師、還有`（多人並列用頓號）。

其他：法利賽人/文士 keep as-is；詩篇引言用和合本修訂版；不確定就靠上下文，整段聽不懂保留 raw **不要編造**；Whisper VAD 雙偵測造成的重複段要 dedupe；英文人名 hallucinate 成中文（如 `Bister Bane`）保留近似形不硬猜。

## DB schema（相關子集）

```sql
pong_sermons (
  id INT PK,                       -- YYYYMMDD
  sermon_date DATE,
  church_year SMALLINT,            -- Advent-start year（建立時算一次不動）
  title TEXT,                      -- 講道主題（不知道默認 主日崇拜）；別跟 occasion 搞混
  content TEXT,                    -- cleaned transcript（非 raw Whisper）
  media_id INT FK,
  preacher TEXT,                   -- 依 era map
  officiant TEXT,                  -- 通常同 preacher
  occasion TEXT,                   -- 禮儀年曆日（顯現節後第二主日 等）
  sermon_type TEXT,                -- taxonomy 見 Phase 4
  scripture_ref TEXT,              -- 經課一/二/福音書 引用
  liturgical_season TEXT,          -- epiphany/lent/easter/pentecost/advent/christmas
  worship_leader TEXT,             -- 司會
  scripture_reader TEXT,           -- 讀經
  choir TEXT,                      -- 獻詩
  worship_team JSONB,              -- 額外角色（襄禮/司琴/司獻/招待/領唱…）
  worship_songs JSONB,             -- 詩歌列表（array）
  description TEXT,                -- 自由描述（嘉賓 / 致詞 / 贈禮）
  location TEXT,
  has_recording BOOLEAN,
  is_published BOOLEAN
)

pong_media (
  id SERIAL PK,
  youtube_id TEXT UNIQUE,          -- 11-char
  title TEXT,
  duration_sec INT,
  transcript TEXT,                 -- 跟 pong_sermons.content 同步
  broadcast_date DATE
)
```

`pong_sermons.content` 和 `pong_media.transcript` 保持 identical — atomic update。

## Files

| File | Role |
|---|---|
| [`scripts/pong-archive/sermon_redo.py`](../../../scripts/pong-archive/sermon_redo.py) | CLI（`status` / `prepare` / `commit`） |
| [`scripts/pong-archive/pong_sermon_pipeline.py`](../../../scripts/pong-archive/pong_sermon_pipeline.py) | 原 pipeline，提供 `download_audio` / `transcribe` / `extract_youtube_id` / `fetch_youtube_metadata` |
| [`pong-archive/stores/城中教會講道清單/城中教會講道_YYYY.txt`](../../../pong-archive/stores/城中教會講道清單/) | 每年 queue 檔 |
| [`pages/pong-archive/sermons/year/[year].vue`](../../../pages/pong-archive/sermons/year/[year].vue) | 年度 listing 頁；非主日 service 需在此加 `specials.push()` |
| `tmp_sermon/<date>_raw.txt` | Whisper raw（intermediate） |
| `tmp_sermon/<date>_clean.txt` | Claude 清理稿（intermediate） |

---

# Phase 1 — Re-transcribe（YouTube → DB）

Whisper raw 不夠好（無標點、簡體混雜、句子連在一起、Christian 名詞錯）— Claude 在 conversation 裡清，**不用 LLM API**（`.env` 沒 `ANTHROPIC_API_KEY`；Gemini cleanup 對神學名詞不穩）。

## Queue markers

每條：marker line、`YYYY-MM-DD title`、URL、空白。

```
# ⏳ 未完成
2015-01-11 主日證道
https://www.youtube.com/watch?v=AYlMJhYzk7I

# ⛔ 別人
2015-03-29 主日證道
https://www.youtube.com/watch?v=HTkBR9ST37c
```

| Marker | Action |
|---|---|
| `# ✅ 完成` | Skip |
| `# ⏳ 未完成` | Process |
| `# ⛔ 別人` | **永遠 skip** — 非龐牧師（客座、別人） |

`(別人)` 也可能出現在 title，一樣 skip。

### 年份檔格式不一致時先 normalize

- **2015**（沒 marker，只有 date+url）— 在每條前加 marker。Title 含 `(別人)` → `# ⛔ 別人`；其餘 → `# ⏳ 未完成`。保留 `Part 1`/`Part 2` 後綴。
- **2016**（inline status 在 title）— `❌ 未收錄` → `# ⏳ 未完成`（去掉）；`✅ 已收錄` → `# ✅ 完成`（去掉）；`(別人)` → `# ⛔ 別人`（去掉）。「已收錄」意指音檔早就在別系統，視為 done。

簡單 inline `python - <<'PY'` heredoc 一次性轉好。

## Loop

```bash
python scripts/pong-archive/sermon_redo.py status \
  pong-archive/stores/城中教會講道清單/城中教會講道_2013.txt
```

每次「繼續跑 queue」loop 到 `prepare` 退 code 3：

1. **prepare** — `python scripts/pong-archive/sermon_redo.py prepare <txt>` 找下個 `# ⏳ 未完成`，確保 DB row 存在，下載 audio 跑 Whisper，輸出 `tmp_sermon/<date>_raw.txt`。stdout JSON 給 `raw_file` / `clean_file` 路徑。指定日期：`--date 2013-03-17`。
2. **讀 raw** — Read tool。Sanity check：25-50 min sermon 約 5000-15000 chars，<2000 表示音檔抓壞，回報使用者。
3. **清理** — 依共用 Reference 寫 polished 繁體 transcript：speaker label → blank line → 16-25 段 prose → closing prayer (阿們。)。
4. **寫清理稿** — Write tool 寫到 `clean_file`。
5. **commit** — `python scripts/pong-archive/sermon_redo.py commit <txt> --date <YYYY-MM-DD> --clean-file <path>`。`UPDATE` `pong_media.transcript` + `pong_sermons.content`，再把 marker 改 `# ✅ 完成`。**DB 寫成功才動 txt** — crash 安全重做。
6. **Loop** — 回 1。

預設行為：使用者沒指明就跑該 txt 所有 `# ⏳`；中間不問，每 ~5 篇報進度。

## 年份特殊處理

### 2014 — `.mpg` 從 service 中間開始

整堂禮拜 rip，**起頭沒開場詩歌／呼召**。Whisper 開頭先是經課讀經 → 詩篇起應文 → 新約 → 然後才到講道。清理時 **整段讀經序幕 skip 掉**，從第一句明顯是 sermon proper（「今天⋯⋯」/「弟兄姊妹⋯⋯」）開始。清理稿不含讀經，只 sermon body + closing prayer。

### 2015 — 多 part 同一日

有些主日上兩支 `Part 1` / `Part 2`，要 **合併成一篇** clean。用 `--youtube-id`（11-char id）區分：

1. `prepare --date 2015-01-18` — 默認 Part 1。
2. `prepare --youtube-id <part2_id>` — 即使 Part 1 還 ⏳ 也選 Part 2。
3. 讀兩 raw，串接 sermon body（跳掉中間歡迎/報事項/重唸經課），產生一篇合併 clean。
4. `commit --youtube-id <part1_id> --date 2015-01-18 --clean-file <combined>` — Part 1 ✅。
5. `commit --youtube-id <part2_id> ...` — 同一 combined 也寫進 Part 2 transcript。Part 2 ✅。

特例：2015-01-25 只有 Part 2（無 Part 1）— 當單篇處理。

### 2016 — 整堂禮拜錄音，要抽 sermon

音檔 ~90+ min 整堂禮拜。Whisper 後序：詩歌→啟應文→經課→**講道**→詩歌→聖餐/奉獻→報告→祝福。Sermon 通常在 30-60 min 之間。

清 2016 時 **只抽 sermon 部分**：
- 起點：「各位弟兄姊妹平安」或福音書讀完後第一段
- 結束：closing prayer 「⋯阿們」，緊接「我們來唱回應詩歌」/「使徒信經來告白」/「以下是我們奉獻的時間」之前

窗外的全丟。`(別人)` 週次：標 `# ⛔ 別人` 之外，**一次性 PATCH** 把這些 row 的 `content` 設為 `''`（清掉舊 pipeline 的 legacy 內容）。

## 常見錯誤模式

| 症狀 | 原因 | 處理 |
|---|---|---|
| `prepare` 寫完 raw 後 exit 127 | Windows tempdir cleanup race | 美觀問題，raw 已寫好，直接 read 下一步 |
| Whisper <2000 chars | 音檔失蹤/影片私人/語言偵測錯 | 手動檢查 URL，影片沒了就標 `# ⛔ 別人` |
| `commit` 說 "no pong_sermons row" | 沒 `prepare` | 先 `prepare --date YYYY-MM-DD` |
| 非中文段 hallucinate 中文 | 短暫 code-switch 英文 | 對主題的知識 best-guess reconstruct |
| 同段重複 | Whisper VAD 雙偵測 | dedupe |

## YouTube + cookies

`download_audio` 用 Firefox cookies。YouTube 要 sign-in 時開 Firefox 一次（cookies 新鮮），再 re-run。

---

# Phase 2 — Polish（粗稿 → publication）

升級已 auto-cleaned 但粗糙的稿（2020-2026 多為此狀態）。徵狀：

- Run-on，很多 `，` 但很少 `。`
- 「大家祝禮平安」「感謝祖」 殘留
- 蕢/邱 name variants 沒修
- 句子片段不通；司會 cue 漏進來
- Whisper hallucinate 詞造成彆扭句

## Scope（嚴格）

只動 `content` / `transcript` 文字。**Metadata 完全不動**（preacher / occasion / worship_leader / scripture_reader / choir / worship_team / church_year / is_published / liturgical_season）— metadata 屬使用者權威，要動走 Phase 3。

## 怎麼找候選

```sql
SELECT id, sermon_date, occasion, length(content) AS char_count
FROM pong_sermons
WHERE preacher LIKE '%龐%'
  AND sermon_date >= '2020-01-01'
  AND content IS NOT NULL
ORDER BY sermon_date;
```

Auto-cleaned 徵狀：`，`/`。` 比例失衡（一堆逗號很少句號）+ 招呼語錯（`大家祝禮平安`）。Gold（hand-cleaned）徵狀：`「」` 包聖經、——/`。。` 自然分段、`，`/`。` 約 3-5x。

## Loop

1. 使用者說「polish 2024-06-09」或 Claude 挑下一個。
2. Read `tmp_sermon/{date}_raw.txt`；clean 不存在就 fetch from DB（見下方 Helper）。
3. 依共用 Reference 寫 polished 版本。重點：
   - First line `龐君華{title}：`（依 era map），blank line
   - Greeting `[X牧師]，還有各位弟兄姊妹，大家平安。`（不是 `大家祝禮平安`）
   - 16-25 段，每段 200-800 字，topical shift 斷段
   - Closing prayer 收 `阿們。`
   - Whisper 錯誤對照表全套
   - 不編造；raw 不清就保留近似 raw
   - Skip 非 sermon（前奏練詩、讀經、報告）
4. Write `tmp_sermon/{date}_clean.txt`。
5. `python scripts/pong-archive/sermon_redo.py commit <txt> --date {date} --clean-file <path>` — 同步 `pong_sermons.content` + `pong_media.transcript`。Txt marker 不變（早就 ✅）。

## Helper：從 DB 抓既有 content

`tmp_sermon/{date}_clean.txt` 不存在時：

```python
import os, requests
with open(".env", encoding="utf-8") as f:
    for line in f:
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

date_iso = "2024-06-09"
sermon_id = int(date_iso.replace("-", ""))
url, key = os.environ["SUPABASE_URL"].rstrip("/"), os.environ["SUPABASE_SERVICE_ROLE_KEY"]
r = requests.get(f"{url}/rest/v1/pong_sermons?id=eq.{sermon_id}&select=content",
                 headers={"apikey": key, "Authorization": f"Bearer {key}"})
content = r.json()[0]["content"]
open(f"tmp_sermon/{date_iso}_clean.txt", "w", encoding="utf-8").write(content)
```

---

# Phase 3 — Standardize（格式 + metadata 統一）

把全集拉到一致；前端 `pages/pong-archive/sermons/[year].vue` 渲染才一致。

## Frontend rendering contract

renderer 把 content 用 `\n+` split，每行分類：

| Line pattern | Render type |
|---|---|
| `^【.+】` | section heading（`【前言】`） |
| `^[（(]` | stage direction（italics，`（會眾請坐）`） |
| `^.{1,8}：` | speaker label（`龐君華牧師：`） |
| 其他 | paragraph |

**Markdown 不支援**。`## 前言` → 改 `【前言】` 或刪。

## 必填欄位（缺就 backfill）

| Field | 來源 |
|---|---|
| `title` | 講道主題（不知道默認 `主日崇拜`）；別 copy `occasion` |
| `occasion` | sermon body 「今天教會的時序來到 X」 |
| `scripture_ref` | raw 「經課一/二/福音書」 |
| `liturgical_season` | 從日期推（規則見下） |
| `preacher` | 依 era map |
| `church_year` | `year if month==12 else year-1`（已 retro-fix 過，不動） |

## Diagnostic queries

```sql
-- 缺 speaker label
SELECT id, sermon_date, substring(content for 50) FROM pong_sermons
WHERE preacher LIKE '%龐%' AND content IS NOT NULL AND content !~ '^.{1,8}：';

-- markdown 殘留
SELECT id, sermon_date FROM pong_sermons WHERE content ~ '^##|^\*\*';

-- 泛用 title
SELECT id, sermon_date, title FROM pong_sermons
WHERE preacher LIKE '%龐%' AND title IN ('主日證道', '主日崇拜', '');

-- 缺 occasion
SELECT id, sermon_date FROM pong_sermons
WHERE preacher LIKE '%龐%' AND occasion IS NULL;

-- 碎片化（avg para < 100）
SELECT id, sermon_date,
  length(content) / GREATEST(1, length(content) - length(replace(content, E'\n\n', ''))) AS avg_para_len
FROM pong_sermons
WHERE preacher LIKE '%龐%' AND content IS NOT NULL
ORDER BY avg_para_len ASC LIMIT 20;
```

## Loop（per-sermon）

1. **抓 content** — GET `pong_sermons?id=eq.{sermon_id}&select=*`。raw 存在的話也讀 `tmp_sermon/{date}_raw.txt`（backfill `scripture_ref` 用）。
2. **Standardize content**（按序）：
   - **2a 去 markdown**：`^## (.+)$` → `【$1】`（有意義 heading）；否則整行刪
   - **2b 確保 speaker label**：第一行不 match `^龐君華(牧師|會督)：` 就 prepend 該 era 的 label + blank line
   - **2c 合併短段**：avg para < 100 chars 時，連續段在 topical shift 合到 200-500 字。**不跨**：speaker label、`（...）` stage direction、`【...】` heading boundary
   - **2d 修 auto-clean 殘留**：`邱牧師，還有`→`邱牧師、還有`；`大家祝禮平安`→`大家平安`；`感謝祖`→`感謝主`
3. **Backfill metadata**：
   - **Title**：泛用 title + 已知 occasion → 留原或 `f"{occasion} 證道"`。有 named sermon → 設為實際主題
   - **Occasion**：content regex 抓 `今天教會的(時序|節期)來到了?(.+?主日)` / `今天.*?是(.+?主日)` / `今天是(.+?日)`。已有特別禮拜 occasion 不動
   - **Scripture ref**：raw 找 `經課一` `經課二` `福音書` `啟應文` 後面引用。Format：`經課一：以賽亞書 65:17-25；啟應文：詩篇 130；經課二：啟示錄 21:3-5；福音書：路加福音 1:46下-55`
   - **Preacher**：依 era map；舊 row 純 `龐君華` → 升 `龐君華牧師`
   - **Liturgical season**：Dec(Advent 1 之後)-Jan 5 → `advent`/`christmas`；Jan 6 - Feb → `epiphany`；Lent/Easter/Pentecost 日期相依
4. **Update DB**：PATCH `pong_sermons` + 同步 `pong_media.transcript`（`media_id` 存在的話）
5. **Spot-check**：`http://localhost:3001/pong-archive/sermons/{id}` 驗 speaker label / 段落 / title / occasion / scripture_refs

## DON'Ts

- **不 bulk auto-apply 沒 spot-check** — rule-based merge 可能毀流暢度
- **不改 content semantics** — 只動 FORMAT，保留確切用字
- **不刪 content** — 半截句也保留
- **不忘 `pong_media.transcript` 同步**
- **不動 `id` / `sermon_date`** — immutable PK

---

# Phase 4 — Photo metadata（程序單照片 → pong_sermons）

使用者貼 1-4 張某場禮拜程序單照片，要把上面的 title / 服事人員 / 詩歌 / occasion / sermon_type 寫進該日 `pong_sermons` row。

## Anti-patterns（先讀）

- **不要 blind INSERT**。多數 row 早被 Whisper pipeline 建好（placeholder `主日崇拜`）。先 `sermon_date` lookup，再決定 UPDATE vs INSERT。
- **不要動 `content` / `transcript` / `scripture_ref`**。這些屬 Phase 1-3 的轄區，是 Whisper + 人工清理的權威輸出。程序單列的經課可能跟實際講的不同 — 信 DB 既有的，只 enrich title / 服事人員 / songs。
- **不要硬填每欄**。照片沒 show 司獻就別填。程序單是 source of truth，不發明。
- **非主日 service MUST 在 [year].vue 的 `specials.push()` 加 block** — 列表頁從 hardcoded church-year calendar 生 row，週六/平日的 row 沒 wire 就看不見。

## 程序單 reading order

1. 封面：教會名、service title、日期
2. 內首頁：服事人員 block（主禮 / 證道 / 司會 / 讀經 / 獻詩 / 襄禮 / 司琴 / 司獻 / 招待 …） + 進殿禮起點
3. 中頁：證道 line（→ sermon title）、詩歌 lines（hymn book ref）、致詞 / 贈禮 / 回顧（特別禮拜）

關鍵欄位（沒這些不要 ship）：sermon title（不要塞 `主日崇拜`）、主禮 / 證道（→ preacher / officiant）、日期。

Nice-to-have：worship_leader / scripture_reader / choir / worship_team / worship_songs / description。

## worship_team convention

JSON object，**中文 key**（PostgREST handles round-trip）：

```python
import json
payload["worship_team"] = json.dumps({
    "襄禮": "邱泰耀牧師",
    "司琴": "盧思寧姊妹",
    "司獻": "楊秀惠姊妹、黃于庭姊妹",
    "招待": "招待組",
}, ensure_ascii=False)
```

標準 keys（key 跟程序單印的字一樣）：襄禮、司琴、司獻、招待、點燭、領唱、指揮、藝術、獻曲、司會（`worship_leader` column 沒占的話）、敬拜（現代敬拜團）。多人在 value 用頓號：`"楊秀惠姊妹、黃于庭姊妹"`。

## worship_songs convention

JSONB array of strings。**labelled-prefix** 是程序單服務的標準形：

```python
payload["worship_songs"] = [
    "進殿詩：樂歌榮神（新普頌 93 首）",
    "回應詩：主頒使命（新普頌 520 首）",
    "詩　歌：復興主教會（新普頌 547 首）",
]
```

`進殿詩` / `回應詩` 用 3 字無 pad；`詩　歌` 用全形 ideographic space `　` 對齊（2 字 + space = 3 字寬）。簡單禮拜（沒程序單分類）可以直接 `["新普頌 411 首", "所有美善力量"]`。

## sermon_type taxonomy

從既有值挑（**不發明**）：

| sermon_type | 何時 |
|---|---|
| 主日講道 | 普通主日 |
| 特殊節日 | 受難週 / 復活節 / 聖誕節 / 立約主日 / 感恩節 |
| 年議會禮拜 | 衛理公會年議會 |
| 退修會與聯合禮拜 | 退修會 / 宿營 / 聯合崇拜 |
| 堂慶與或聯合禮拜 | 堂慶 / 校慶 / 教會週年（60週年用這個） |
| 特殊禮拜 | 追思 / 安息 / 按立 / 就職 |

(`堂慶與或聯合禮拜` 有「或」typo — 保留 typo 對齊既有 row，**不要單方面改**。)

## church_year / liturgical_season

`church_year` = Advent **STARTED** 的那年。
- 2021-11-20 (Sat) 在 Advent 1 2021 (=2021-11-28) 之前 → `church_year=2020`
- 2021-11-28 (Sun, Advent 1) → `church_year=2021`
- 2022-01-15 早一月 → `church_year=2021`（Advent 2022 還沒開始）

`liturgical_season`：

| 範圍 | season |
|---|---|
| Advent 1 → Christmas Eve | `advent` |
| Dec 25 → Jan 5 | `christmas` |
| Jan 6 → Lent | `epiphany` |
| Ash Wed → Holy Saturday | `lent` |
| Easter → Pentecost - 1 週 | `easter` |
| Pentecost → next Advent - 1 | `pentecost` |

不確定看鄰近 row（去年同週）的慣例。

## Process

### 1. Lookup by sermon_date

```python
r = requests.get(f"{SB}/pong_sermons",
    headers=H,
    params={"sermon_date": f"eq.{date_iso}", "select": "*"})
existing = r.json()
```

非空 → UPDATE，**保留 `content` / `scripture_ref` / `media_id` / `youtube_url` / `church_year` / `liturgical_season`** 除非明顯錯。空 → INSERT，從照片建 row + 缺的問使用者。

### 2. 從照片抽資料

依 reading order。

### 3. PATCH

```python
import os, json, requests
from dotenv import load_dotenv
load_dotenv(r"c:\Users\user\Desktop\know-graph-lab\.env")

SB = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}",
     "Content-Type": "application/json", "Prefer": "return=representation"}

payload = {
    "title": "上帝藉著聖靈居住的所在",
    "worship_songs": [
        "進殿詩：樂歌榮神（新普頌 93 首）",
        "回應詩：主頒使命（新普頌 520 首）",
        "詩　歌：復興主教會（新普頌 547 首）",
    ],
    # row 已有的別動
}
r = requests.patch(f"{SB}/pong_sermons?id=eq.{sermon_id}", headers=H, json=payload)
```

驗 UTF-8 用 `python -c "json.load... ensure_ascii=False"` — PowerShell 終端會 mangle raw UTF-8 輸出。

### 4. 非主日 → wire calendar special

非主日 row 在 DB 但列表頁看不見。`pages/pong-archive/sermons/year/[year].vue` 的 `buildChurchYear(y)` 內加 specials block：

```js
if (y === 2020) {                            // ⚠️ 該 row 的 church_year（不是 sermon_date 的 calendar 年）
  const anniv60 = new Date(2021, 10, 20)     // month 0-indexed
  if (anniv60 <= end) {
    specials.push({
      date:        anniv60,
      dateStr:     fmtDate(anniv60) + DOW_ZH[anniv60.getDay()],
      isSpecial:   true,
      seasonKey:   'pentecost',              // liturgical_season 對應
      specialName: '城中教會六十週年感恩禮拜',
      specialColor:'#B22020',
    })
  }
}
```

renderer 用 `sermonFor(entry.date)` attach title 和 link — specials block 只要 name / color / date。

**⚠️ church_year vs calendar year 陷阱**：年頁 `/sermons/year/Y` 載入 `pong_sermons WHERE church_year=Y`。2021-11-20 的 row（Advent 1 2021 前）`church_year=2020`，所以 specials 要放 `y === 2020` block，不是 `y === 2021`。放錯：calendar 有 row 但 `sermonFor()` 回 null，title 空、無 link，看起來「沒 wire」— 2021-11-20 60週年首次 wire 就踩過這雷。

`seasonKey` 對應該日 `liturgical_season`（pentecost / lent / advent / 等）— 決定 row 出在哪一季區塊。

`specialColor` 配色：

- `#B22020` — 慶典紅（堂慶 / 60週年 / 就任）
- `#8B1818` — 殉道紅（受難日）
- `#6B4A90` — 大齋紫（聖灰日）
- `#A07828` — 聖誕金（平安夜）
- `#3A3530` — 哀悼黑（告別式 / 安息），加 `isFuneral: true`

### 5. Commit code 只在 [year].vue 真的改了

DB-only enrichment 不需 commit。加了 specials block 才提交那個檔。

## Notes

- DB `preacher` vs 程序單 mismatch（e.g. DB=邱泰耀牧師、程序單=龐君華會督）：程序單通常權威，但**先 flag 跟使用者確認**（可能 wrong-date confusion）。
- 不發明新 sermon_type — keep taxonomy stable。
- 嘉賓 / 致詞 / 贈禮 不發明新 column — append 到 `description`：e.g.「啟創會友：翁其振弟兄、費筱宗弟兄⋯；歷任牧師代表致詞：林烽銓牧師」。
- 龐君華 ~2018 前 牧師，之後 會督。程序單 era 為準（不全靠 sermon_date — 早期 sermon 後印於 later 程序單也有）。
