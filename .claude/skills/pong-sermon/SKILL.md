---
name: pong-sermon
description: Re-transcribe + clean up 龐君華牧師 sermons end-to-end and write them into pong_sermons / pong_media. Use when the user asks to redo / improve a year's worth of sermon transcripts, when a specific sermon date's transcript looks rough (no punctuation, simplified Chinese, run-on text), or when 城中教會講道_YYYY.txt has 「⏳ 未完成」 entries that need processing.
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# 龐君華 講道集 — Re-transcribe & Clean-up Pipeline

End-to-end workflow that takes a year list of YouTube sermon URLs and turns each into a polished traditional-Chinese transcript stored in `pong_sermons.content` + `pong_media.transcript`.

The Whisper output alone is not good enough — it has no punctuation, mixed simplified/traditional Chinese, run-on lines, and characteristic mistranscriptions (e.g. 薄力人 instead of 伯利恆). Cleanup is done **by Claude in conversation**, not by an LLM API, because we don't have an `ANTHROPIC_API_KEY` in `.env` and Gemini-cleaned output has been inconsistent on Christian terminology.

## Reference quality bar

[`pong_sermons.id=20130106`](http://localhost:3001/pong-archive/sermons/20130106) (顯現節主日／立約主日) is the gold standard. Match it: speaker label `龐君華牧師：` on line 1, blank line, then long topical paragraphs separated by blank lines, full punctuation (，。「」—— etc.), traditional Chinese throughout.

[`pong_sermons.id=20130113`](http://localhost:3001/pong-archive/sermons/20130113) was the first one redone via this pipeline (2026-05-04) and is also a valid reference.

## Files

| File | Role |
|---|---|
| [`scripts/pong-archive/sermon_redo.py`](../../../scripts/pong-archive/sermon_redo.py) | The CLI. Subcommands `status` / `prepare` / `commit`. |
| [`scripts/pong-archive/pong_sermon_pipeline.py`](../../../scripts/pong-archive/pong_sermon_pipeline.py) | Original pipeline. `sermon_redo.py` reuses its `download_audio` / `transcribe` / `extract_youtube_id` / `fetch_youtube_metadata` helpers. |
| [`pong-archive/stores/城中教會講道清單/城中教會講道_YYYY.txt`](../../../pong-archive/stores/城中教會講道清單/) | Per-year queue. One block per sermon: marker line, then `YYYY-MM-DD title`, then YouTube URL, then blank. |
| `tmp_sermon/<date>_raw.txt` | Whisper raw output (intermediate). |
| `tmp_sermon/<date>_clean.txt` | Cleaned text Claude writes (intermediate). |

## Queue markers in the txt files

The canonical format is **header markers** — one marker line per entry, then the title line, then the URL, separated by blank lines:

```
# ⏳ 未完成
2015-01-11 主日證道
https://www.youtube.com/watch?v=AYlMJhYzk7I

# ⛔ 別人
2015-03-29 主日證道
https://www.youtube.com/watch?v=HTkBR9ST37c
```

| Marker | Meaning | Action |
|---|---|---|
| `# ✅ 完成` | Already transcribed + cleaned + in DB | Skip |
| `# ⏳ 未完成` | Pending | Process |
| `# ⛔ 別人` | Not 龐牧師 (guest preacher etc.) | **Always skip — never process** |

`(別人)` may also appear inside the title; always skip those too. The `# ⛔ 別人` marker on the line above is the canonical signal.

### Year files that arrive in a different shape — normalize first

Some year files were authored by hand and don't follow the header-marker convention out of the box. Convert them before running `prepare`:

- **2015 (no markers, just date+url pairs)** — add a header marker above every entry. `(別人)` in the title becomes `# ⛔ 別人`; everything else becomes `# ⏳ 未完成`. Keep `Part 1` / `Part 2` suffixes in the title (see "Multi-part sermons" below).
- **2016 (inline status markers in the title)** — `❌ 未收錄` → `# ⏳ 未完成` (strip from title); `✅ 已收錄` → `# ✅ 完成` (strip from title); `(別人)` → `# ⛔ 別人` (strip from title). 「已收錄」 in the source means the audio was previously archived in *another* system — for our purposes, treat it as already done and don't re-process.

A one-shot Python migration handles both shapes — read the file, detect the entry layout, prepend the right marker line, write back. Trivial enough to inline as a `python - <<'PY'` heredoc when the next "weird year file" appears.

## DB schema (relevant subset)

```sql
pong_sermons (
  id INT PK,                       -- equals YYYYMMDD of sermon_date
  sermon_date DATE,
  church_year SMALLINT,            -- Advent-start year
  title TEXT,
  content TEXT,                    -- cleaned transcript (NOT the raw Whisper output)
  media_id INT FK,
  preacher TEXT,
  location TEXT,
  has_recording BOOLEAN,
  is_published BOOLEAN
)

pong_media (
  id SERIAL PK,
  youtube_id TEXT UNIQUE,          -- 11-char video ID
  title TEXT,
  duration_sec INT,
  transcript TEXT,                 -- same cleaned text as pong_sermons.content
  broadcast_date DATE
)
```

`pong_sermons.content` and `pong_media.transcript` are kept identical — we update both atomically. `church_year` is computed once at row creation and never touched.

## The loop (what Claude does in a session)

For each session the user opens "to keep going through the queue", Claude runs this loop until `prepare` exits with status 3 (no pending entries left):

### Step 1 — Pick the next entry and run prepare

```bash
python scripts/pong-archive/sermon_redo.py prepare \
  pong-archive/stores/城中教會講道清單/城中教會講道_2013.txt
```

This finds the next `# ⏳ 未完成` entry, ensures both DB rows exist (creates them if missing), downloads the YouTube audio, runs Whisper, and writes the raw transcript to `tmp_sermon/<date>_raw.txt`.

It prints a JSON object on stdout:

```json
{"date": "2013-01-20", "title": "主日證道", "url": "...",
 "sermon_id": 20130120, "media_id": 12,
 "raw_file": "tmp_sermon/2013-01-20_raw.txt",
 "clean_file": "tmp_sermon/2013-01-20_clean.txt"}
```

To process a specific date instead of the next pending: `--date 2013-03-17`.

### Step 2 — Read the raw transcript

```python
Read tool on raw_file
```

Sanity check: the raw should be ~5000-15000 chars for a typical 25-50 min sermon. If suspiciously short (<2000 chars) or empty, the audio likely failed — don't proceed; report to user.

### Step 3 — Clean it up (this is Claude's job)

Produce a polished traditional-Chinese transcript. Match the 2013-01-06 reference exactly in structure:

```
龐君華牧師：

<paragraph 1, full traditional Chinese, full punctuation, ~200-800 chars>

<paragraph 2…>

…

<closing prayer paragraph, ending in 阿們。>
```

**Rules:**

1. **Speaker label**: First line is `龐君華牧師：`, second line blank. No speaker label inside body paragraphs unless the audio actually has another speaker.
2. **Traditional Chinese throughout**. Common conversions: 显→顯, 经→經, 历→歷, 节→節, 师→師, 复→復/複, 实→實, 实际→實際, 让→讓, 应→應, 关→關, 国→國, 体→體, 学→學, 礼→禮, 圣→聖, 处→處, 谁→誰, 题→題, 别→別, 简→簡, 类→類, 选→選, 爱→愛, 时→時, 间→間, 们→們, 这→這, 个→個, 来→來, 会→會, 后→後, 发→發.
3. **Punctuation**: full-width `，。：；！？「」『』——……（）`. Wrap quotations and Bible quotes in `「」`.
4. **Paragraphs**: 16–25 paragraphs typically; break at topical shifts (illustration → application; narrative → exposition; transitions like 「另一方面」「所以」「今天」「但是」). Mimic 2013-01-06's pacing.
5. **Preserve voice**: don't rewrite or summarize. Keep filler words (呢, 啊, 喔, 那), repeated phrases, and stylistic ticks. Preserve the speaker's actual word choices.
6. **Whisper mistranscription fixes** (apply with confidence based on context):
   - 薄力人 → 伯利恆 (Bethlehem)
   - 灯山變象 → 登山變像 (Transfiguration)
   - 西里王 → 希律王 (Herod)
   - 尼賽人 / 尼賽特 → 彌賽亞 (Messiah)
   - 三個佛事 → 三個博士 (Magi)
   - 法利賽人 / 文士 → keep as-is
   - 依麗撒海 → 伊麗莎白 (Elizabeth)
   - 聖靈彷彿鴿 → 聖靈彷彿鴿子般
   - 化石架 → 畫十字架
   - 一道書 / 一道書 → 一缸水 / 聖水盆 (in Catholic-church context)
   - 民宿 → 民間 (in 「在這民間裡所行的事」 context)
   - 暴命 → 奧秘
   - 灵形 → 有形
   - 高層 (in 「展開一個高層」) → 高潮
   - 临死 / 临起 / 离洗 / 离醒 → 領洗 / 受洗
   - 重温我們所力的約 → 重溫我們所立的約
   - 武器 (in 「領受新的武器」) → 祝福 / 洗禮
   - 非常小可 → 非同小可
   - Personal/biblical names: cross-check using sermon context.
7. **Bible references**: keep 詩篇 quotes in 和合本修訂版 phrasing if the speaker is clearly quoting (e.g. `「這是我的愛子，我今日生你」`).
8. **Don't invent content**. If a passage is genuinely unintelligible in the raw, leave it close to the raw text rather than fabricating — flag to user if a whole section is broken.
9. **English names** the speaker uses are usually attempted-by-Whisper into Chinese; preserve the closest-sounding form (e.g. `Bister Bane` from earlier transcripts) rather than aggressively guessing.
10. **No code blocks, no markdown headings** in the body. Pure prose with paragraph breaks. The frontend renders `龐君華牧師：` lines specially via regex.

### Step 4 — Write the cleaned text to the clean file

Use the Write tool to write to `clean_file` (path was returned by `prepare`).

### Step 5 — Commit to DB + mark the txt as done

```bash
python scripts/pong-archive/sermon_redo.py commit \
  pong-archive/stores/城中教會講道清單/城中教會講道_2013.txt \
  --date 2013-01-20 \
  --clean-file tmp_sermon/2013-01-20_clean.txt
```

This `UPDATE`s `pong_media.transcript` and `pong_sermons.content` (looked up by date — no IDs needed), then flips the marker in the txt file from `# ⏳ 未完成` to `# ✅ 完成`. **Only the txt is touched after the DB write succeeds**, so a crash mid-flow means the next session re-picks-up the same date safely.

### Step 6 — Loop

Go back to Step 1. Stop when `prepare` exits with code 3 ("no pending entries").

## Year-specific quirks

### 2014 — `.mpg` recordings start mid-service

The 2014 entries are titled `…主日.mpg` because they were ripped from raw service tapes that begin **after** the opening hymn / call to worship. The Whisper output therefore typically starts with the **lectionary scripture readings** (今天的經課……), then the **psalter response** (詩篇…起應文), then the **second reading** (新約…), and only *after* that does 龐牧師 begin the actual sermon.

When cleaning a 2014 sermon, **skip the readings prelude entirely** — start the cleaned text at the first sentence that's clearly the sermon proper. Often the first marker is 「今天⋯⋯」 or 「弟兄姊妹⋯⋯」 right after the gospel reading concludes. (Versus 2013, where most recordings already start with 「各位弟兄姊妹平安」.)

The cleaned file should NOT contain the scripture readings — just the sermon body and closing prayer.

### 2015 — Multi-part sermons (Part 1 + Part 2 same date)

Some Sundays in 2015 were uploaded as two separate YouTube videos: `主日證道 Part 1` and `主日證道 Part 2`. The user's instruction is to **combine these into one cleaned sermon** (they're the two halves of the same delivery, not two separate sermons).

Procedure for a Part 1+2 date (e.g. 2015-01-18). Use `--youtube-id` (the 11-char id from the YouTube URL) to disambiguate the two entries:

1. `prepare --date 2015-01-18` — defaults to Part 1 (first pending). Writes `tmp_sermon/2015-01-18_<part1_id>_raw.txt`.
2. `prepare --youtube-id <part2_id>` — picks Part 2 even though Part 1 is still ⏳. Writes `tmp_sermon/2015-01-18_<part2_id>_raw.txt`.
3. Read both raw files. Concatenate the sermon-body portions (skip the inter-part welcome / announcements / scripture re-readings) and produce **one** combined cleaned file, e.g. `tmp_sermon/2015-01-18_clean.txt`.
4. `commit --youtube-id <part1_id> --date 2015-01-18 --clean-file <combined>` — writes the combined transcript to Part 1's `pong_media.transcript` + `pong_sermons.content`. Marks Part 1 ✅ 完成.
5. `commit --youtube-id <part2_id> --date 2015-01-18 --clean-file <combined>` — same combined file goes to Part 2's `pong_media.transcript` (both videos now carry the full transcript). Marks Part 2 ✅ 完成.

Special case: 2015-01-25 has only `Part 2` listed (no Part 1) — treat as a regular single sermon.

### 2016 — Full worship recordings; extract sermon only

The 2016 audio files are full Sunday worship recordings (~90+ min), not pre-edited sermon clips. After Whisper transcribes them, you'll see the entire service: 詩歌 → 啟應文 → 經課 → 講道 → 詩歌 → 聖餐/奉獻 → 報告事項 → 祝福. The sermon proper is usually somewhere between minute 30 and minute 60.

When cleaning a 2016 file, **extract only the sermon portion**:
- **Start**: typically 「各位弟兄姊妹平安」 or the first paragraph after the gospel reading concludes.
- **End**: the closing prayer ending in 「⋯⋯阿們」, immediately before 「我們來唱回應詩歌」 / 「使徒信經來告白我們的信仰」 / 「以下是我們奉獻的時間」.

Drop everything outside that window — readings, hymns, announcements, communion words.

For the `(別人)` weeks in 2016, the user wants the existing `pong_sermons.content` cleared (some had legacy content from a prior pipeline). When converting the txt to header markers, mark these as `# ⛔ 別人` and additionally run a one-off PATCH to set `content = ''` on those `pong_sermons` rows.

## Status check

Before starting (or anytime), run:

```bash
python scripts/pong-archive/sermon_redo.py status \
  pong-archive/stores/城中教會講道清單/城中教會講道_2013.txt
```

Output:

```
queue: pong-archive\stores\城中教會講道清單\城中教會講道_2013.txt
  total   : 41
  done    : 2
  pending : 30
  skip    : 9
  next pending:
    2013-01-20  主日證道
    …
```

## Per-session pacing

A single sermon takes ~3-5 min wall time:
- Whisper download + transcribe: 2-4 min on RTX 4050 for a 25-30 min sermon (split into 20-min chunks)
- Claude cleanup: ~30s–1min (depending on length and Claude's pace)
- DB + txt update: <1s

So a session can process roughly 6-12 sermons per hour. The user typically wants to grind through one year's queue, which means several sessions.

## How to run prepare in the background

The Whisper step is slow. Run it in a foreground Bash with a long timeout (10 min is plenty for one sermon), or use `run_in_background: true` and Monitor for the file appearing:

```python
Bash(run_in_background=True, command="python scripts/pong-archive/sermon_redo.py prepare <txt_file>")
# Then wait for tmp_sermon/<expected_date>_raw.txt to appear via:
Bash(run_in_background=True, command="until [ -f /c/Users/user/Desktop/know-graph-lab/tmp_sermon/<date>_raw.txt ]; do sleep 10; done; echo done")
```

But the simpler path is just `Bash(timeout=600000)` and let it block — for a single sermon it's only a few minutes.

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `prepare` exits 127 right after writing the raw file | Windows tempdir cleanup race in `pong_sermon_pipeline.download_audio` | Cosmetic — the raw file is written before the crash; just proceed to read it. |
| Whisper produces <2000 chars for a sermon | YouTube audio missing / video private / wrong language detected | Check the YouTube URL manually. If video is gone, mark the txt entry as `# ⛔ 別人` (or a new `# ❌ 缺音檔` marker) and skip. |
| `commit` says "no pong_sermons row" | `prepare` was never run for this date | Run `prepare --date YYYY-MM-DD` first. |
| Whisper hallucinates fluent text in non-Chinese sections | Speaker code-switched briefly to English | Trust your knowledge of the sermon's topic; replace the hallucination with a best-guess reconstruction. |
| Same paragraph appears twice in the raw | Whisper VAD double-detected | Dedupe in cleanup. |

## YouTube + cookies

`download_audio` uses Firefox cookies (see `_cookie_args()` in `pong_sermon_pipeline.py`). If YouTube starts demanding sign-in, open Firefox once (so cookies are fresh), then re-run.

## When user asks "do the next batch"

Default: process all `# ⏳ 未完成` in the year file the user names (or `2013` if unspecified) until none remain. Don't ask between sermons — just keep looping, and report progress every ~5 sermons or whenever the user asks.

If the user wants to do just N sermons, do N then stop. If they want a specific date, use `prepare --date YYYY-MM-DD`.
