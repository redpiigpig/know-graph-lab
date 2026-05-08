---
name: pong-sermon-standardize
description: Standardize and normalize formatting across all 龐君華牧師 sermons in `pong_sermons` table — speaker label, content markdown stripping, paragraph regrouping, occasion/title/scripture_ref backfilling, preacher field consistency. Run after content cleanup is mature, to bring all 270+ sermons to a uniform publishable format the frontend `[year].vue` renderer expects.
---

# 龐君華 講道集 — Standardization Pipeline

After all sermons are transcribed and cleaned (via `pong-sermon` skill) and content polished (via `pong-sermon-polish` skill), this skill enforces a uniform format across the entire collection so the frontend renders consistently and SEO/RSS exports look professional.

## Frontend rendering contract (from `pages/pong-archive/sermons/[year].vue`)

The renderer splits `pong_sermons.content` by `\n+` and classifies each line:

| Line pattern | Render type | Example |
|---|---|---|
| `^【.+】` | section heading | `【前言】` |
| `^[（(]` | stage direction (italics) | `（會眾請坐）` |
| `^.{1,8}：` | speaker label | `龐君華牧師：` |
| anything else | paragraph | (regular prose) |

**Markdown is NOT supported.** `## 前言` will render as a paragraph starting with literal `##`. Convert to `【前言】` or remove entirely.

## Canonical format

```
龐君華牧師：

各位弟兄姊妹，大家平安。今天⋯⋯（greeting paragraph）

第二段內容，~200-800 字一段。當主題切換時開新段。

⋯（more body paragraphs）

⋯（closing prayer paragraph ending in 阿們。）
```

**Key rules:**
1. **Speaker label** on line 1: `龐君華{title}：` where title is `牧師` (pre-2019-05) or `會督` (2019-05 onwards, permanent). Determined by date; see "Preacher title era map" below. ⚠️ 沒有「牧職會長」稱謂。
2. **Blank line** after speaker label (`\n\n`).
3. **Paragraphs** separated by single blank line (`\n\n`). No leading whitespace.
4. **No markdown**: no `##`, no `*`, no `_`, no `[]()`. Convert headings to `【X】` or delete.
5. **No fragmented paragraphs**: avg paragraph length should be 200-800 chars. If avg <100 (typical of auto-cleaned), merge consecutive short paragraphs into longer ones at topical shifts.
6. **Last line** of closing prayer ends with `阿們。`.

## Preacher title era map

只有兩個稱謂：**牧師** (pre-2019-05) 和 **會督** (2019-05 onwards, 包括退休後)。

| Era | Title | DB value |
|---|---|---|
| Pre-**2019-05** | 牧師 | `龐君華牧師` |
| **2019-05** onwards (永遠, 退休後仍維持會督稱謂) | 會督 | `龐君華會督` |

⚠️ 沒有「牧職會長」稱謂。退休後 (2022-05+) 仍稱 會督，不退回牧師。

⚠️ Use the title that 龐 was using **at the time of that sermon**. When inserting a new sermon, look up his role for that date.

## Required fields (backfill if missing)

For every published 龐 sermon row, the following fields should ideally be filled:

| Field | Meaning | Source / Default |
|---|---|---|
| `id` | YYYYMMDD | (PK) |
| `sermon_date` | DATE | (set at insert) |
| `church_year` | Advent-start liturgical year | `year if month==12 else year-1` |
| `title` | sermon-specific title or generic | from raw or "{occasion} 主日證道" |
| `occasion` | liturgical occasion | from sermon body 「今天教會的時序來到 X」 |
| `scripture_ref` | lectionary reading citations | from raw 「經課一/二/福音書」 |
| `liturgical_season` | epiphany/lent/easter/pentecost/advent/christmas | derived from date |
| `preacher` | title-aware (see era map) | `龐君華牧師` default |
| `officiant` | usually same as preacher | (same) |
| `worship_leader` (司會) | person name | from servant info if available |
| `scripture_reader` (讀經) | person name | from servant info |
| `choir` (獻詩) | choir/group name | from servant info |
| `worship_team` (JSONB) | extra service roles (司琴/領唱/etc) | for special services |
| `is_published` | bool | True for 龐 sermons |
| `has_recording` | bool | True if media_id set |

## Diagnostic queries

```sql
-- Find sermons missing speaker label (rare, mostly pre-2015)
SELECT id, sermon_date, substring(content for 50)
FROM pong_sermons
WHERE preacher LIKE '%龐%' AND content IS NOT NULL
  AND content !~ '^.{1,8}：';

-- Find markdown bleed-through
SELECT id, sermon_date FROM pong_sermons
WHERE content ~ '^##|^\*\*';

-- Find generic titles
SELECT id, sermon_date, title FROM pong_sermons
WHERE preacher LIKE '%龐%' AND title IN ('主日證道', '主日崇拜', '');

-- Find missing occasion
SELECT id, sermon_date FROM pong_sermons
WHERE preacher LIKE '%龐%' AND occasion IS NULL;

-- Find fragmented content (avg paragraph length < 100)
SELECT id, sermon_date,
  length(content) / GREATEST(1, length(content) - length(replace(content, E'\n\n', ''))) AS avg_para_len
FROM pong_sermons
WHERE preacher LIKE '%龐%' AND content IS NOT NULL
ORDER BY avg_para_len ASC
LIMIT 20;
```

## Loop (per-sermon standardization)

For each problematic row, apply fixes one at a time:

### Step 1 — Pull current content + raw

```python
# Fetch current content from DB
sermon_id = 20240609  # ← change me
url = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
r = requests.get(
    f"{url}/rest/v1/pong_sermons?id=eq.{sermon_id}&select=*",
    headers={"apikey": key, "Authorization": f"Bearer {key}"},
)
row = r.json()[0]
```

Read the raw too if it exists: `tmp_sermon/{date}_raw.txt`. Raw helps you backfill `scripture_ref` (look for 「經課一」 and the reference that follows).

### Step 2 — Standardize content

Apply the following transformations in order:

#### 2a. Strip markdown headings → 【X】 or remove
- `^## (.+)$` → `【$1】` (if heading is meaningful section like 「前言」「結語」)
- Otherwise delete the line entirely

#### 2b. Ensure speaker label format
- First line should match `^龐君華(牧師|會督|牧職會長)：`
- If missing, prepend appropriate title based on era map
- Ensure blank line after (i.e., second line is empty)

#### 2c. Regroup short paragraphs
If avg paragraph length < 100 chars (auto-cleaned text), merge consecutive paragraphs until each is ~200-500 chars or natural topical shift. Topical-shift markers: `所以` `今天` `另一方面` `但是` `於是` `我們看到` `那麼` `因此`.

Don't merge across:
- Speaker label boundary
- Stage direction `（...）` boundary
- Section heading `【...】` boundary

#### 2d. Fix common Whisper errors that survived auto-clean
- `邱牧師，還有` → `邱牧師、還有` (Chinese serial comma between names)
- `大家祝禮平安` → `大家平安`
- `感謝祖` → `感謝主`
- 「，高興。」 (sentence ending mid-thought) → check if next paragraph starts with "今天"; if yes, merge with `「⋯⋯，高興今天⋯⋯」`

### Step 3 — Backfill metadata

#### 3a. Title
If `title in ('主日證道', '主日崇拜', '')` and `occasion` is set, leave as-is OR change to `f"{occasion} 證道"`. (User preference; prefer keeping `title` short and using `occasion` for the specific liturgical day.)

For named sermons (e.g., 「心志更新同啟航」), set `title` to the actual sermon title.

#### 3b. Occasion
Search content for patterns like:
- `今天教會的(時序|節期)來到了?(.+?主日)` → extract X
- `今天.*?是(.+?主日)`
- `今天是(.+?日)` (受難日, 顯現日, etc.)

If found, set `occasion` accordingly (e.g., `顯現節後第二主日`, `主受洗日`).

For special services already with occasion (按牧禮拜, 平安夜, etc.), leave alone.

#### 3c. Scripture ref
From raw `tmp_sermon/{date}_raw.txt`, search for `經課一` `經課二` `福音書` `啟應文` and extract the references that follow (e.g., 「以賽亞書 65:17-25」).

Format: `經課一：以賽亞書 65:17-25；啟應文：詩篇 130；經課二：啟示錄 21:3-5；福音書：路加福音 1:46下-55`

#### 3d. Preacher field
- Look up date in era map (above)
- Set `preacher` to canonical form
- For old rows with `preacher = '龐君華'` (no title), upgrade to `龐君華牧師`

#### 3e. Liturgical season
Derive from sermon_date:
- Dec (after Advent 1) - Jan 5 → `advent` or `christmas`
- Jan 6 - Feb (~ Ash Wed) → `epiphany`
- Lent (Ash Wed - Easter) → `lent`
- Easter - Pentecost → `easter`
- Pentecost - Christ the King → `pentecost`

### Step 4 — Update DB

```python
# Build new state
new_content = standardize_content(row["content"], date_iso)
patch = {
    "content": new_content,
    "title": new_title,
    "occasion": new_occasion,
    "scripture_ref": new_scripture,
    "preacher": new_preacher,
    "liturgical_season": new_season,
}

# Single PATCH
r = requests.patch(
    f"{url}/rest/v1/pong_sermons?id=eq.{sermon_id}",
    headers={...},
    json=patch,
)

# Also sync pong_media.transcript if media_id set
if row["media_id"]:
    requests.patch(
        f"{url}/rest/v1/pong_media?id=eq.{row['media_id']}",
        headers={...},
        json={"transcript": new_content},
    )
```

### Step 5 — Spot-check on website

Visit `http://localhost:3001/pong-archive/sermons/{id}` and verify:
- Speaker label renders distinctly (no `##` visible)
- Paragraphs flow naturally
- Title / occasion show in header
- Scripture refs (if added) visible

## Status snapshot (2026-05-08)

After full standardization pass on 284 龐 sermons:

| Issue | Before | After | Method |
|---|---|---|---|
| Missing speaker label | 28 | 0 (excl. 14 empty-content) | `standardize_sermon.py apply --preset missing_label` |
| Markdown bleed-through | 0 | 0 | (already clean) |
| Generic title (`主日證道`/`主日崇拜`) | 162 | 27 | `backfill_title.py apply` (153+32 from occasion) |
| Missing/placeholder occasion | 161+20 | 23+20 | `backfill_occasion.py apply` (138+43 derived from `今天…X主日` cue) |
| Avg paragraph < 100 chars | 41 | 0 | `regroup_fragmented.py apply` (39 sermons) |
| Missing scripture_ref | 250 | 250 | **Punted** — auto-extract from raw Whisper too lossy; lectionary table only covers 2025-11-30+ (3 candidates). Future option: RCL Year A/B/C lookup table. |
| Non-canonical preacher label `龐君華牧職會長：` | 1 (20191231) | 0 | One-off content patch → `龐君華會督：` |

Remaining residual issues (require manual review):
- 23 sermons where `今天-cue` matched no liturgical-day pattern (mostly 2014 expository series on 出埃及記/創世紀 where pong didn't name the day)
- 20 sermons where `occasion` is still placeholder `主日證道`/`主日崇拜` (cue matched but no useful day name)
- Known false positives from auto-occasion: 20131124 (matched `聖誕節`, should be `基督君王主日`; OCR text reads `基督威王祖日`), 20161016 (forward-reference matched `將臨期的第一個主日` from "11月27號是新的教會年曆將臨期的第一個主日")

## Priority order for processing

Process from highest-impact to lowest:

1. **Markdown bleed-through (2 entries)** — 2020-05-22, 2020-07-18, 2019-12-31. Easy fix, immediately visible improvement.
2. **Auto-cleaned 2020-2025 (~70 entries)** — fragmentation worst here. Use `/pong-sermon-polish` for content quality + this skill for metadata.
3. **Pre-2015 missing speaker label (28 entries)** — older recordings, mostly 2014. Prepend `龐君華牧師：\n\n` if missing.
4. **2002-2007 transcription quality** ✅ **DONE 2026-05-08** — replaced all 38 龐 sermons in this range with authoritative fhl.net text via `scripts/pong-archive/standardize_2002_2007_from_fhl.py`. The script:
   - Reads `tmp_fhl/index.json` (date → `sermonNNN.html` map, 144 entries from 2002.03-2007.04)
   - Fetches each fhl page (urllib + big5 decode), parses via `fhl_import.parse_page`
   - Caches HTML to `tmp_fhl/html_cache/` for re-runs
   - PATCHes `pong_sermons.content` only (preserves title/preacher/occasion/scripture_ref)
   - Syncs `pong_media.transcript` if `media_id` is set (no media existed for 2002-2007 era)
   - Throttle 3s between fetches; logs to `tmp_fhl/standardize_2002_2007_log.txt`

   For future re-runs against other date ranges from the same source: edit the date filter constants. fhl.net source is authoritative; replace whenever parsed body ≥ 500 chars.
5. **Generic titles (162 entries)** — backfill titles from occasion or raw. Lower priority since `occasion` does most of the displayed work on the year-list page.
6. **Missing scripture_ref (238 entries)** — from raw if available. Optional/nice-to-have.

## Helper script template

`scripts/pong-archive/standardize_sermon.py`:

```python
import re, os, requests
from datetime import date as _date

def derive_preacher_title(d):
    """龐 title era map: 牧師 → 會督 transition at 2019-05."""
    if d < _date(2019, 5, 1):
        return "龐君華牧師"
    return "龐君華會督"  # 2019-05+ permanent (including post-retirement)

def derive_liturgical_season(d):
    """Approximate. Frontend uses this only for color coding."""
    m = (d.month, d.day)
    if m >= (12, 1) and m < (12, 25):  return "advent"
    if m >= (12, 25) or m <= (1, 5):    return "christmas"
    if m <= (2, 28):                    return "epiphany"
    # Lent / Easter / Pentecost are date-dependent — too complex for simple rule
    # Leave as existing if set, otherwise default to "pentecost"
    return None  # keep existing

def strip_markdown(content):
    out = []
    for line in content.split("\n"):
        m = re.match(r"^##+\s+(.+)$", line)
        if m:
            out.append(f"【{m.group(1).strip()}】")
        elif re.match(r"^---+$", line):
            continue  # drop horizontal rules
        else:
            out.append(line)
    return "\n".join(out)

def ensure_speaker_label(content, date_iso):
    d = _date.fromisoformat(date_iso)
    title = derive_preacher_title(d)
    label = f"{title}："
    first_line = content.split("\n", 1)[0].strip()
    if re.match(r"^.{1,8}：", first_line):
        return content  # already has one
    return f"{label}\n\n{content}"

def regroup_short_paragraphs(content, target_min=200, target_max=600):
    paras = [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]
    if not paras:
        return content
    out = [paras[0]]  # speaker label / first paragraph
    buffer = []
    SHIFT_RE = re.compile(r"^(所以|今天|另一方面|但是|於是|我們看到|那麼|因此|然後|最後)")
    for p in paras[1:]:
        # Special lines stay separate
        if re.match(r"^[【（].", p) or re.match(r"^.{1,8}：", p):
            if buffer:
                out.append("".join(buffer))
                buffer = []
            out.append(p)
            continue
        # Try merging
        if not buffer:
            buffer.append(p)
        elif SHIFT_RE.match(p) and len("".join(buffer)) >= target_min:
            out.append("".join(buffer))
            buffer = [p]
        elif len("".join(buffer)) + len(p) > target_max:
            out.append("".join(buffer))
            buffer = [p]
        else:
            buffer.append(p)
    if buffer:
        out.append("".join(buffer))
    return "\n\n".join(out)

# ... assemble + commit pattern ...
```

## DON'Ts

- **Don't bulk auto-apply** without spot-checking. Each sermon is unique; rule-based merging may break flow.
- **Don't change content semantics**. Standardization is FORMAT only — preserve exact wording, fix only structure/punctuation/whitespace.
- **Don't drop content**. Even partial sentences should be preserved.
- **Don't forget pong_media.transcript sync**. Both must mirror.
- **Don't change `id` or `sermon_date`**. They're immutable keys.
