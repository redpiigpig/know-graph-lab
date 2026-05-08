---
name: pong-sermon-polish
description: Manually polish 龐君華牧師 sermons that were auto-cleaned (rough draft quality) into publication-ready transcripts. Use when 2020-2026 sermons need higher quality cleanup beyond what `auto_clean.py` produced — full punctuation, paragraph breaks at topical shifts, Whisper error correction, traditional Chinese throughout.
---

# 龐君華 講道集 — Manual Polish Pipeline (auto-cleaned → publication-ready)

End-to-end workflow for upgrading 2020-2026 龐 sermons from auto-cleaned draft quality to publication quality. The auto_clean.py from the original pipeline produces an OK first pass but has issues:

- Run-on paragraphs without proper sentence breaks
- Whisper mistranscriptions still present (蕢/邱 name variants, place names, biblical names)
- "大家祝禮平安" type Whisper errors
- Awkward phrasing where Whisper hallucinated words
- Some text fragments that are clearly worship-leader cues bleeding into sermon

This skill turns auto-cleaned drafts into polished content matching the gold standard:

[`pong_sermons.id=20130106`](http://localhost:3001/pong-archive/sermons/20130106) (顯現節主日／立約主日) — speaker label `龐君華牧師：` on line 1, blank line, then long topical paragraphs separated by blank lines, full punctuation (，。「」—— etc.), traditional Chinese throughout.

## Scope

This skill polishes sermons that already have:
- Cleaned text in `pong_sermons.content` (and `pong_media.transcript`)
- Correct metadata (preacher, occasion, worship_leader, scripture_reader, choir, worship_team)
- Correct church_year, is_published=true

The polishing affects ONLY `content` / `transcript` text. Metadata is untouched.

## Files

| File | Role |
|---|---|
| [`scripts/pong-archive/sermon_redo.py`](../../../scripts/pong-archive/sermon_redo.py) | The CLI. Use `commit --date YYYY-MM-DD --clean-file PATH` to update. |
| `tmp_sermon/<date>_raw.txt` | Original Whisper output (reference). |
| `tmp_sermon/<date>_clean.txt` | Auto-cleaned draft (input). Polish in-place. |
| Existing `pong_sermons.content` | What's currently in DB (current draft). |

## Reference quality bar

The gold-standard structure:

```
龐君華牧師：

邱牧師，還有各位弟兄姊妹，大家平安。今天教會的時序來到了顯現日之後的第二個主日。…

第二段文字的內容，~200-800 字，主題完整。…

…

天父上帝，我們感謝祢——是因為祢的呼召，使我們的生命有了不一樣的價值。…求主幫助我們…奉主耶穌基督的聖名祈求。阿們。
```

- 16-25 paragraphs typically
- Each paragraph 200-800 chars
- Break at topical shifts (「另一方面」「所以」「今天」「但是」「於是」「我們看到」)
- Full Chinese punctuation: ，。「」『』——……（）！？
- All traditional Chinese
- Closing prayer ends in 阿們。

## How to find candidates

```sql
-- Sermons with auto-cleaned content (2020-2026), ordered by date
SELECT id, sermon_date, occasion, length(content) as char_count
FROM pong_sermons
WHERE preacher LIKE '%龐%' 
  AND sermon_date >= '2020-01-01'
  AND content IS NOT NULL
ORDER BY sermon_date;
```

The auto-cleaned ones are typically detectable by:
- Lots of `，` but few `。` (run-on paragraphs)
- "大家祝禮平安" / "感謝祖" (Whisper artifacts)
- Sentence fragments that don't connect grammatically

The hand-cleaned ones (gold standard) have:
- Balanced ，/。 ratio (~3-5x more 「，」 than 「。」 typically)
- 「」for Bible quotes
- ——or「。。」 in flow

## The loop (per-sermon)

For each session, Claude works through one or more pending sermons:

### Step 1 — Pick a sermon and load context

```bash
# List 2020-2026 sermons sorted by date (so user can pick)
python scripts/pong-archive/sermon_redo.py status \
  pong-archive/stores/城中教會講道清單/城中教會講道_2024.txt
```

User says "polish 2024-06-09" or similar, OR Claude picks the next one.

### Step 2 — Read both raw and current cleaned

```python
Read tmp_sermon/{date}_raw.txt
Read tmp_sermon/{date}_clean.txt   # if exists, OR fetch from DB
```

If `_clean.txt` doesn't exist on disk, fetch current content from DB:

```python
# scripts/pong-archive/fetch_content.py {date} > tmp_sermon/{date}_clean.txt
```

(Or use Bash with curl/python to GET from Supabase REST.)

### Step 3 — Compose the polished version

Polish the auto-cleaned draft using the raw as reference. Match the gold-standard structure:

1. **Speaker label**: First line `龐君華牧師：`, second line blank
2. **Greeting paragraph** — typically `[X牧師]，還有各位弟兄姊妹，大家平安。` (NOT 「大家祝禮平安」 etc.)
3. **Body paragraphs** — 16-25 paragraphs, each 200-800 chars, break at topical shifts
4. **Closing prayer** — ending in 阿們。
5. **Whisper fixes** — apply with confidence:
   - 邱牧師 variants: 求/丘/球/秋/熊/瓊/琼/窮/全/修/裘 → 邱
   - 蕢牧師 variants: 春/秦/祝/桂/窺/匱/餽 → 蕢
   - Bible names (薄力人 → 伯利恆, 三個佛事 → 三個博士, 灯山變象 → 登山變像, etc.)
   - 感謝祖 → 感謝主
   - 大家祝禮平安 → 大家平安
6. **Punctuation** — full-width，。「」『』——……（）；：、！？; wrap quotations and Bible quotes in 「」
7. **Traditional Chinese** — convert any remaining simplified
8. **Don't invent content** — if a passage is genuinely unclear in the raw, leave close to raw rather than fabricating
9. **Skip non-sermon parts** — pre-worship hymn practice, scripture readings, post-sermon announcements should NOT be in the cleaned content. Sermon body only.

### Step 4 — Write polished file

```python
Write tmp_sermon/{date}_clean.txt with polished content
```

### Step 5 — Commit

```bash
python scripts/pong-archive/sermon_redo.py commit \
  pong-archive/stores/城中教會講道清單/城中教會講道_YYYY.txt \
  --date {date} \
  --clean-file tmp_sermon/{date}_clean.txt
```

This updates BOTH `pong_sermons.content` AND `pong_media.transcript`.

The txt file marker won't change (already ✅ 完成).

### Step 6 — Loop

Move to next sermon. Mark progress.

## Helper: fetch current content from DB

If `tmp_sermon/{date}_clean.txt` is missing (e.g., on a fresh machine), pull it from Supabase:

```bash
python -X utf8 - <<'PY'
import os, requests
with open(".env", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

date_iso = "2024-06-09"  # ← change me
sermon_id = int(date_iso.replace("-", ""))
url = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
r = requests.get(
    f"{url}/rest/v1/pong_sermons?id=eq.{sermon_id}&select=content",
    headers={"apikey": key, "Authorization": f"Bearer {key}"},
)
content = r.json()[0]["content"]
with open(f"tmp_sermon/{date_iso}_clean.txt", "w", encoding="utf-8") as f:
    f.write(content)
print(f"wrote {len(content)} chars to tmp_sermon/{date_iso}_clean.txt")
PY
```

## Pacing

Per-sermon polish takes ~5-10 min of Claude time depending on length:
- Reading raw + current clean: 1 min
- Writing polished version: 4-8 min
- Commit: <10s

A focused session can polish 6-12 sermons per hour.

## What NOT to change

- Don't change `metadata` fields (preacher / occasion / worship_leader / scripture_reader / choir / worship_team / liturgical_season). Those are user-authoritative.
- Don't change `church_year` (already correct after retro-fix).
- Don't change `is_published` (all should be True).

## Priority targets

Polish in this order (most-needed first):

1. **2024 (12 sermons)** — most recent, user-supplied servant info, highest visibility
2. **2025 (13 sermons including 平安夜)** — most recent
3. **2023 (13 sermons)** — solid year of regular sermons
4. **2022 (5 sermons)**
5. **2021 (2 sermons via streams)** — 60週年 + 平安夜
6. **2026-01-11** — already manually polished, gold standard

## Notes specific to 平安夜 / 受難日 / 60週年

These special services have:
- Multi-role personnel in `worship_team` JSONB
- Sometimes 龐 only does 「默想」 (meditation) not full sermon (e.g., 2023-04-07)
- The "sermon" content may be shorter, more reflective, with seven 默想 segments
- Be especially careful to preserve liturgical structure
