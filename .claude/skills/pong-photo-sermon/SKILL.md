---
name: pong-photo-sermon
description: Backfill / correct pong_sermons rows from chat-attached photos of a 程序單 (worship program handout) — sermon title, 服事人員名單, 詩歌, occasion, sermon_type. Use when the user uploads photos of a specific service's program (e.g., 城中教會堂慶感恩禮拜 / 平安夜燭光禮拜 / 聖誕崇拜) and says something like "你把講題、服事人員名單放到相應的時間與類別中" or "這份程序單對應 YYYY-MM-DD 那場". Sibling of `pong-photo-writing` but targets a different table.
---

> 🚨 **截圖規則 — 絕對禁止 >2000px**：傳進對話的截圖（寬或高任一邊）超過 2000px 會直接炸掉整個 session（"exceeds the dimension limit for many-image requests"）。使用者一說要傳截圖，立刻提醒先確認尺寸；推薦 Win+Shift+S 框選或縮到 ≤ 1920px。

# pong-photo-sermon — 程序單照片 → pong_sermons

End-to-end recipe for taking chat-attached photos of a printed 程序單 and applying the metadata to the matching `pong_sermons` row.

## When to use

User uploads 1-4 photos of a single service's 程序單 (worship program handout). Typical setup:

- Cover spread: church name, service title, date
- Inside opening page: list of 服事人員 (主禮 / 證道 / 司會 / 讀經 / 獻詩 / 襄禮 / 司琴 / 司獻 / 招待 …) + start of 進殿禮
- Middle page: 證道 line with the sermon title, 詩歌 lines with hymn book references, 致詞 / 贈禮 / 回顧 lines for special services

**Sibling skill, different shape**: [`pong-photo-writing`](../pong-photo-writing/SKILL.md) targets `pong_writings` for published articles. This skill targets `pong_sermons` for service metadata. Don't confuse the two — different tables, different fields, different UI page.

## Anti-patterns

- **Don't INSERT blindly.** Most service rows already exist (Whisper transcription pipeline creates them with placeholder titles like "主日崇拜"). Always look up by `sermon_date` first, then decide UPDATE vs INSERT.
- **Don't overwrite content / transcript / scripture_ref.** Those came from Whisper + manual cleanup pipelines and are authoritative. The 程序單 might list different scripture refs than what was actually preached — trust the existing `content` / `scripture_ref`, just enrich `title` / 服事人員 / songs.
- **Don't try to fill every column.** If a photo doesn't show 司獻, leave it out. The 程序單 is the source of truth; don't invent.
- **Non-Sunday services MUST be added to the calendar's `specials` list in [`pages/pong-archive/sermons/year/[year].vue`](../../../pages/pong-archive/sermons/year/[year].vue)** — the listing page generates its rows from a hardcoded church-year calendar; rows in `pong_sermons` whose date isn't a Sunday simply won't appear in the listing unless you wire them up there. See the "Non-Sunday services" section below.

## Schema (pong_sermons)

| Column | Photo source | Notes |
|---|---|---|
| `id` | n/a | INTEGER, format `YYYYMMDD` matching sermon_date |
| `title` | 證道 line (sermon title only) | NOT 「主日崇拜」 — that's the placeholder. The actual sermon title from 「證道 .... <title> .... 龐君華會督」 |
| `occasion` | Service title at top of program | e.g., 城中教會成立六十週年感恩禮拜 |
| `sermon_date` | Date on cover or first page | DATE |
| `sermon_type` | Inferred from occasion (see taxonomy below) | TEXT |
| `church_year` | Advent of YYYY-1 if sermon_date is before that year's Advent | SMALLINT |
| `liturgical_season` | See season table below | TEXT |
| `location` | Service location | 衛理公會城中教會 default |
| `preacher` | 證道 (or 主禮 if same person) | 龐君華會督 / 龐君華牧師 — match the era |
| `officiant` | 主禮 (when distinct from 證道) | TEXT |
| `worship_leader` | 司會 | TEXT |
| `scripture_reader` | 讀經 | TEXT |
| `choir` | 獻詩 / 詩班 | e.g., 城中牧區詩班 |
| `worship_team` | 襄禮、司琴、司獻、招待、藝術、點燭、領唱、指揮 等次要角色 | **JSON string** — see convention below |
| `worship_songs` | 進殿詩 / 回應詩 / 詩歌 / 結禮詩 | **JSONB array** — see convention below |
| `description` | 致詞 / 贈禮 / 回顧 names + notes | Free-form text for 嘉賓 names not captured elsewhere |
| `content` / `scripture_ref` / `youtube_url` / `media_id` | — | **Don't touch** — these come from the transcript pipeline |

## worship_team convention

JSON object with **Chinese keys**, escaped as Unicode in DB (PostgREST handles round-trip). When patching:

```python
import json
payload["worship_team"] = json.dumps({
    "襄禮": "邱泰耀牧師",
    "司琴": "盧思寧姊妹",
    "司獻": "楊秀惠姊妹、黃于庭姊妹",
    "招待": "招待組",
}, ensure_ascii=False)
```

Standard keys (use the printed term as the key — match the 程序單):
- 襄禮、司琴、司獻、招待、點燭、領唱、指揮、藝術、獻曲、司會 (when not in `worship_leader` column)、敬拜 (for 現代敬拜團 leadership)

If a role has multiple people, comma-separate within the value: `"司獻": "楊秀惠姊妹、黃于庭姊妹"`.

## worship_songs convention

JSONB array of formatted strings. Two shapes seen in the wild — go with the **labeled-prefix** form for 程序單-style services:

```python
payload["worship_songs"] = [
    "進殿詩：樂歌榮神（新普頌 93 首）",
    "回應詩：主頒使命（新普頌 520 首）",
    "詩　歌：復興主教會（新普頌 547 首）",
]
```

Spacing convention: 進殿詩 / 回應詩 use no padding (3 chars); 詩 歌 uses 全形 ideographic space `　` to align (2 chars + space = 3 chars wide). Don't over-engineer.

For simpler services (just one or two hymns without 程序單 categories), bare titles are also acceptable: `["新普頌 411 首", "所有美善力量"]`.

## sermon_type taxonomy

Pick from existing values (don't invent):

| sermon_type | When |
|---|---|
| 主日講道 | Ordinary Sunday worship, no special occasion |
| 特殊節日 | 受難週 / 復活節 / 聖誕節 / 立約主日 / 感恩節 / 等 |
| 年議會禮拜 | 衛理公會年議會 sessions |
| 退修會與聯合禮拜 | 退修會、宿營、 聯合崇拜 |
| 堂慶與或聯合禮拜 | 堂慶 / 校慶 / 教會週年 — `60週年感恩禮拜` 用這個 |
| 特殊禮拜 | 追思禮拜、安息禮拜、按立禮、就職禮 等 |

(`堂慶與或聯合禮拜` has a 「或」 typo in the canonical value — preserve the typo to match existing rows. Don't try to fix unilaterally.)

## church_year / liturgical_season

`church_year` = the year that Advent **STARTED**. So:

- Advent 2021 starts on 2021-11-28 (1st Sunday of Advent that year)
- A sermon on 2021-11-20 is still in `church_year=2020` (in 將臨期前最後 ordinary 主日 of the 2020-2021 church year)
- A sermon on 2021-11-28 is in `church_year=2021`

`liturgical_season` for the dates that matter:

| Range | season |
|---|---|
| 1st Sunday of Advent → Christmas Eve | `advent` |
| Dec 25 → Jan 5 | `christmas` |
| Jan 6 → Lent | `epiphany` |
| Ash Wed → Holy Saturday | `lent` |
| Easter → Pentecost - 1 week | `easter` |
| Pentecost → next Advent - 1 | `pentecost` |

When in doubt, look at an adjacent row (the same week prior year) for the convention.

## Process

### 1. Look up the existing row by sermon_date

```python
r = requests.get(f"{SB}/pong_sermons",
    headers=H,
    params={"sermon_date": f"eq.{date_iso}", "select": "*"})
existing = r.json()
```

If `existing` is non-empty: this is an UPDATE. Note current values — preserve `content`, `scripture_ref`, `media_id`, `youtube_url`, `church_year`, `liturgical_season` unless they're clearly wrong.

If empty: this is an INSERT. Build full row from photo (and ask user for what's missing).

### 2. Extract from photos

Reading order: cover (date + service name) → first inside page (服事人員 block) → middle page (證道 line + 詩歌 lines + special-occasion blocks like 致詞 / 贈禮).

**Critical fields to find** (don't ship without these):
- Sermon title (證道 line) — NOT 「主日崇拜」 (that's a placeholder, not a title)
- 主禮 / 證道 person — to set `preacher` (and `officiant` if different)
- Date — to confirm `sermon_date` matches

**Nice-to-have**:
- 服事人員 details (worship_leader, scripture_reader, choir, song_leader)
- Additional roles → worship_team JSON
- Hymn list → worship_songs
- 嘉賓 / 致詞 / 贈禮 names → description (for special services)

### 3. PATCH (UPDATE) the existing row

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
    # 上 row 已有的別動 — 只 patch 你從照片新讀到的
    "worship_songs": [
        "進殿詩：樂歌榮神（新普頌 93 首）",
        "回應詩：主頒使命（新普頌 520 首）",
        "詩　歌：復興主教會（新普頌 547 首）",
    ],
}
r = requests.patch(f"{SB}/pong_sermons?id=eq.{sermon_id}",
                   headers=H, json=payload)
print(r.status_code, r.json()[0]["title"])
```

Verify via curl with `python -c "json.load... ensure_ascii=False"` — PowerShell terminal mangles UTF-8 in raw output; curl + Python printing handles it.

### 4. If the service is NOT on a Sunday — wire up the calendar special

The year listing page [`/pong-archive/sermons/year/[year].vue`](../../../pages/pong-archive/sermons/year/[year].vue) builds its row list from a hardcoded **church-year calendar** (Advent 1 → next Advent), plus a small set of `specials.push(...)` blocks for non-Sunday events. If your service is on a Saturday / weekday, the DB row alone is invisible — add a special block:

```js
// in buildChurchYear(y), after the existing specials:
if (y === 2020) {                            // <-- match the CHURCH YEAR (= Advent-start
                                             //     year of the row's church_year column),
                                             //     NOT the calendar year of the date below
  const anniv60 = new Date(2021, 10, 20)     // <-- the service date (month is 0-indexed)
  if (anniv60 <= end) {
    specials.push({
      date:        anniv60,
      dateStr:     fmtDate(anniv60) + DOW_ZH[anniv60.getDay()],
      isSpecial:   true,
      seasonKey:   'pentecost',              // <-- the liturgical season for grouping
      specialName: '城中教會六十週年感恩禮拜',
      specialColor:'#B22020',                // <-- red for 慶典 / 受難; see palette below
    })
  }
}
```

The renderer looks up `sermonFor(entry.date)` to attach the DB title and link — the special block only needs name + color + date.

**⚠ Critical: church_year vs calendar year mismatch.** The year page at `/sermons/year/Y` loads `pong_sermons WHERE church_year=Y`. A row whose `sermon_date` is November 2021 has `church_year=2020` if it falls before Advent 1 2021 (Nov 28). If you put the `specials.push` block under the wrong `y`, the entry shows up on the calendar but `sermonFor()` returns null → the title is blank, the row isn't clickable, and it looks like nothing is wired up. **Always check the DB row's `church_year` column and match `y === <that value>`**, regardless of the date's calendar year. This is exactly the bug that hit the inaugural 2021-11-20 wire-up.

**Color palette for specialColor** (match existing usages):
- `#B22020` — 慶典紅 (堂慶 / 60週年 / 就任禮拜)
- `#8B1818` — 殉道紅 (受難日)
- `#6B4A90` — 大齋紫 (聖灰日)
- `#A07828` — 聖誕金 (平安夜)
- `#3A3530` — 哀悼黑 (告別式 / 安息禮拜) + set `isFuneral: true` for extra styling

**`seasonKey` should match the liturgical_season** the date falls in (pentecost for late Nov ordinary time, lent for Holy Week dates, etc.) — this determines which season group the row appears under.

**Computing church_year** — the year that **Advent started**, NOT the calendar year:
- Advent 1 of year Y is the Sunday closest to Nov 30 of year Y (rule: Sunday in the range Nov 27 – Dec 3)
- Anything before that Advent Sunday is still in the PREVIOUS church year
- e.g. 2021-11-20 (Sat) is before Advent 1 2021 (= 2021-11-28), so `church_year = 2020`
- e.g. 2021-11-28 (Sun, Advent 1) is `church_year = 2021`
- e.g. 2022-01-15 (early January) is still `church_year = 2021` (since Advent 2022 hasn't started)

### 5. Commit code changes only when [year].vue actually changed

DB-only enrichment (UPDATE of an existing row) needs no commit. If you added a `specials` block in [year].vue, commit & push that single file:

```bash
git add pages/pong-archive/sermons/year/'[year]'.vue
git commit -m "feat(pong-archive/sermons): 加 YYYY-MM-DD 《<service-name>》 special"
git push origin master
```

## Reference quality bar

[`pong_sermons.id=20211120`](http://localhost:3000/pong-archive/sermons/20211120) — 上帝藉著聖靈居住的所在（城中教會 60 週年感恩禮拜）— is the gold standard for this skill. After processing it has:

- `title`: 上帝藉著聖靈居住的所在 (the actual sermon title — fixed from placeholder "主日崇拜")
- `occasion`: 城中教會成立六十週年感恩禮拜
- `sermon_type`: 堂慶與或聯合禮拜
- Full worship team across 7 fields:
  - `preacher` / `officiant`: 龐君華會督
  - `worship_leader`: 周慶同弟兄 (司會)
  - `scripture_reader`: 黃玲媛姊妹 (讀經)
  - `choir`: 城中牧區詩班 (獻詩)
  - `worship_team` JSON: {襄禮:邱泰耀牧師, 司琴:盧思寧姊妹, 司獻:楊秀惠姊妹、黃于庭姊妹, 招待:招待組}
- `worship_songs` array of 3 labelled hymns
- **`content` left untouched** (Whisper-cleaned 龐君華 transcript stays as-is)
- **Calendar special wired up**: [year].vue has a `y === 2020 → anniv60` block pushing the Nov-20 (Sat) entry as a `specials` row in 聖靈降臨期, color `#B22020`. Note `y===2020` not `y===2021` — the row's `church_year=2020` (date is before Advent 2021). Without this block, the DB row is orphaned; with the wrong `y`, the row appears but has no title and isn't clickable.

## Notes

- If the existing row's `preacher` doesn't match what's on the program (e.g. DB says 邱泰耀牧師 but program shows 龐君華會督), the program is usually authoritative — but flag the discrepancy and ask before changing, since it might mean wrong-date confusion.
- Don't update `sermon_type` to a value that doesn't already exist in the DB — keep taxonomy stable.
- For 致詞 / 嘉賓 / 贈禮 names that don't fit the standard worship roles, append a free-form `description` rather than inventing a new column. E.g.: `"啟創會友：翁其振弟兄、費筱宗弟兄、費趙鳳宜姊妹、鄭段宛琪姊妹；歷任牧師代表致詞：林烽銓牧師"`.
- 龐君華 was 牧師 until ~2018, 會督 thereafter. Match `preacher` to the era shown on the program (not just sermon_date — sometimes a 牧師-era sermon is reprinted in a later program).
