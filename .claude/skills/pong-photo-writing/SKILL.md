---
name: pong-photo-writing
description: Transcribe photos of printed 龐君華會督 articles (periodical / 紀念特刊 / 書章 etc.) into pong_writings rows, end-to-end. Use when the user uploads images of book/magazine pages and says something like "把這幾張的內容放到刊物文章中" or "新增一篇某某特刊的文章". Handles vertical traditional Chinese OCR, colophon (版權頁) extraction, and all DB + UI plumbing.
---

# pong-photo-writing — Photos → pong_writings

End-to-end recipe for taking 1-N chat-attached photos of an already-published 龐君華會督 article (most often a 堂慶紀念特刊 / 期刊 / 書章) and turning it into a fully-rendered entry under `/pong-archive/writings/<id>`.

## When to use

User uploads chat-attached photos of printed pages and asks to "放到刊物文章" / "轉錄成一篇文章". Typical setup:

- 3-5 photos: title page, body pages, possibly the 版權頁 (colophon) and cover
- Vertical traditional Chinese, right-to-left column order
- Article is `category='periodical'` for 紀念特刊 / 院訊 / 衛訊, or other categories for thesis / book_chapter etc.

## Anti-patterns (don't do this)

- **Don't ask the user to save the images to disk and OCR via Gemini.** Claude itself is a vision model — read the photos directly from chat context. The user pushed back on this in the inaugural session and was right. (Memory: `feedback_ocr_strategy.md` is about *book PDFs*, not chat-attached photos.)
- **Don't try `git status` to confirm your edits.** A parallel agent session is often committing & pushing during the conversation, so your files may already be in HEAD before you commit. Verify by reading file content, not git diff.
- **Don't transcribe perfectly accurately on the first pass.** Vertical Chinese from a downsampled photo (2000×1500) has unavoidable ambiguity. Mark uncertain characters with `[?]` and let the user fix in the admin or via SQL.

## Schema

`pong_writings` already has every column needed (added during the 2026-05-14 inaugural session):

| Column | Type | Purpose |
|---|---|---|
| `title` | TEXT | Article title from the spread |
| `category` | TEXT | `periodical` for 特刊/院訊; `book_chapter`, `journal`, etc. otherwise |
| `publication` | TEXT | **Full official name** from the 版權頁, e.g. `衛理公會城中教會六十週年紀念特刊` — NOT the marketing short form on the cover |
| `published_date` | DATE | First-of-month if only month known; set `date_approximate=true` |
| `editor` | TEXT | 編輯 from 版權頁 (kept as top-level for searchability; also appears inside `colophon`) |
| `page_range` | TEXT | `"14-16"` for spreads, `"12"` for single page |
| `colophon` | JSONB | `{lines: [{label, value}, ...]}` — full 版權頁 reproduction |
| `tags` | TEXT[] | Include publication name + topical tags |
| `content` | TEXT | Body, paragraph per line, `> ` prefix for quotes, plain short lines for headings |
| `is_published` | BOOLEAN | `true` |
| `sort_order` | INTEGER | `max(sort_order)+1` |

## Frontend conventions (already in place)

[`pages/pong-archive/writings/[id].vue`](../../../pages/pong-archive/writings/[id].vue) renders:

1. **Header**: cat badge → publication chip → date chip → `頁次：N-M` chip (from `page_range`)
2. **Byline**: hardcoded `龐君華 會督` under the title (all writings ARE by him; no DB field)
3. **Body**: `text-indent: 2em` on every `.wa-para`, reset to `0` for `--heading` / `--quote` / `--empty`
4. **Colophon** (`.wa-colophon` at bottom of `.wa-body`): grid of `label｜value` rows, only shown if `article.colophon.lines.length`

[`pages/pong-archive/writings/index.vue`](../../../pages/pong-archive/writings/index.vue) `PERIODICAL_ORDER` controls sub-tab order; if you add a new publication, append its **full official name** to the array.

## Process

### 1. Identify which photos contain what

Typically:
- **Title page** (article's opening spread): big title, byline (作者), photo of author/family, page number in corner
- **Body pages**: continuation
- **版權頁 (colophon page)**: list of 出版者 / 出版人 / 設計排版 / 地址 / 電話 / 出版日期
- **Cover**: book title, publisher logo, year

Note all page numbers (e.g. 14, 15, 16) to compute `page_range`.

### 2. Extract colophon

Read the 版權頁 photo carefully and build a colophon JSON. Standard label order (the user established this in 2026-05-14):

```json
{
  "lines": [
    {"label": "出版者",   "value": "<publication full name>"},
    {"label": "出版者",   "value": "<publishing organisation>"},
    {"label": "發行人",   "value": "<出版人 from 版權頁>"},
    {"label": "編輯",     "value": "<editor — ask user if not on 版權頁>"},
    {"label": "設計排版", "value": "..."},
    {"label": "地址",     "value": "..."},
    {"label": "電話",     "value": "..."},
    {"label": "出版日期", "value": "<YYYY年MM月>"}
  ]
}
```

**Convention**: 編輯 goes after 發行人 (the user explicitly placed it there). If the printed 版權頁 doesn't list an editor, ask the user — don't omit.

### 3. OCR the body — Claude vision, direct

Read photos column-by-column, right-to-left (vertical Chinese). Aim:

- One `\n\n`-separated paragraph per logical paragraph
- Lead `> ` for "呼召" / scripture / indented quotes
- Short standalone lines (≤ 20 chars, no terminal punctuation) become headings via `isHeading()` regex in [id].vue
- Bullet lines like `崇拜：每週主日…` / `奉獻：…` — each on its own line; the rendering preserves the colon
- Use `[?]` (max 1 per uncertain word) for characters you can't read. The user will sweep these.
- Aim for **structure first, character accuracy second**. Getting paragraph breaks and quote markers right matters more than reading 100% of characters.

### 4. Insert via PostgREST

```python
import os, requests
from dotenv import load_dotenv
load_dotenv(r"c:\Users\user\Desktop\know-graph-lab\.env")

SB = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}",
     "Content-Type": "application/json", "Prefer": "return=representation"}

next_sort = (requests.get(f"{SB}/pong_writings", headers=H,
    params={"select":"sort_order","order":"sort_order.desc","limit":1}).json()[0]["sort_order"] or 0) + 1

payload = {
  "title": "...",
  "category": "periodical",
  "publication": "<FULL official name from 版權頁>",
  "published_date": "2021-11-01",
  "date_approximate": True,
  "editor": "楊肇悅",
  "page_range": "14-16",
  "colophon": { ... see above ... },
  "content": "...with \\n\\n paragraph breaks and > for quotes...",
  "tags": ["<publication-name>", "<topical-tag>", ...],
  "is_published": True,
  "sort_order": next_sort,
}
r = requests.post(f"{SB}/pong_writings", headers=H, json=payload)
print(r.status_code, r.json()[0]["id"])
```

### 5. Add to PERIODICAL_ORDER if new publication

If the publication name isn't already in [`writings/index.vue`](../../../pages/pong-archive/writings/index.vue) `PERIODICAL_ORDER`, append it:

```js
const PERIODICAL_ORDER = ['中華衛訊', '衛神院訊', '衛報', '衛理公會城中教會六十週年紀念特刊', /* + new */]
```

The badge counter & sub-tab show up automatically; without this entry, the publication still works but gets shoved to the end of the sub-tab strip (and counts as "其他").

### 6. Commit your files only

```bash
git add server/api/pong-writing/'[id]'.get.js pages/pong-archive/writings/'[id]'.vue pages/pong-archive/writings/index.vue
git commit -m "feat(pong-archive/writings): 加《...》一篇"
git push origin master
```

**Don't `git add .` or `git add -A`** — a parallel session is usually editing `components/genealogy/BiblicalSpineTree.vue` etc. concurrently; you'd swallow their work-in-progress into your commit.

## Reference quality bar

[`pong_writings.id=43`](http://localhost:3000/pong-archive/writings/43) — 學習成為門徒的信仰群體：廿年來牧養的心路歷程 — is the gold standard for this skill. Match its layout:

- Header chips: `[刊物文章] 衛理公會城中教會六十週年紀念特刊  2021年11月  頁次：14-16`
- Byline: `龐君華 會督` (Serif, 0.18em letter-spacing, gold #6A5E4A)
- Body: `text-indent: 2em`, justify, 2.1 line-height
- Quote: indented box with left border `#C4B89A`
- Bottom: full 版權頁 in `.wa-colophon` grid

## Common metadata defaults

| Field | Default if not on photo |
|---|---|
| `published_date` | First of the month given on 版權頁; `date_approximate=true` |
| `category` | `periodical` for 院訊 / 衛訊 / 紀念特刊 / 週報 |
| `editor` | **Ask user** — usually not in the 版權頁 even when there is one |
| `is_published` | `true` |
| `cloudinary_urls` | `[]` — we don't (yet) upload scanned originals; the OCR'd text is canonical |

## Notes

- The byline `龐君華 會督` is hardcoded in `[id].vue`. If a future article needs a different attribution (e.g. co-author, interview), refactor to use a real DB column at that point — don't pre-build.
- The `colophon.lines` array preserves order, so you can put 出版者 / 發行人 / 編輯 in whatever order matches the original 版權頁 (with 編輯 after 發行人 per user preference).
- For multi-volume publications or articles spanning a few different sources, file each as its own row — don't try to merge.
