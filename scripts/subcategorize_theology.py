"""Re-classify 神學 books into the structured subcategory framework.

Target taxonomy (matches pages/ebook/index.vue CATEGORY_TREE):
  ── 歷史時期 ──
  教父著作 / 中世紀著作 / 改教著作 / 近現代著作
  教父研究 / 中世紀研究 / 改教研究   (近現代學者的 historical research)
  ── 主題 ──
  教科書/概論 / 主題專論 / 倫理神學 / 靈修神學 / 神學詮釋/哲學 / 本地化處境神學

Series subcategories already starting with "Schaff" or "中世紀著作 / Aquinas"
or "本地化處境神學" are preserved (their detail tail is valuable).

Usage:
  python scripts/subcategorize_theology.py status                 # show distribution
  python scripts/subcategorize_theology.py classify --dry-run     # LLM run, no DB write
  python scripts/subcategorize_theology.py classify --limit 5     # smoke test
  python scripts/subcategorize_theology.py classify               # write to DB
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_PATCH = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

# 13 canonical labels (4 periods + 3 historical-research + 6 themes)
LABELS = {
    "教父著作", "中世紀著作", "改教著作", "近現代著作",
    "教父研究", "中世紀研究", "改教研究",
    "教科書/概論", "主題專論", "倫理神學", "靈修神學",
    "神學詮釋/哲學", "本地化處境神學",
}

# Existing subcategory prefixes that we MUST preserve (series identifiers)
PRESERVE_PREFIXES = (
    "Schaff -",
    "中世紀著作 / Aquinas",
    "本地化處境神學",   # already classified by prior batch
)

# Heuristic rules for confident cases (skip LLM)
def rule_based_label(title: str, author: str, existing_sub: str | None) -> str | None:
    t = (title or "") + " " + (author or "")
    s = existing_sub or ""

    # Existing label already canonical?
    if s in LABELS:
        return s

    # Schaff series → 教父著作 / X
    if s.startswith("Schaff - "):
        return None  # preserve as-is

    if "Aquinas" in s or "阿奎那" in t or "多瑪斯" in t:
        if "Aquinas" not in s:
            return "中世紀著作"
        return None  # preserve

    # Common patterns
    if any(k in t for k in ("奧古斯丁", "Augustine")):
        return "教父著作" if "research" not in t.lower() and "研究" not in t else "教父研究"
    if any(k in t for k in ("路德", "Luther", "加爾文", "Calvin", "茨溫利", "Zwingli", "胡斯", "Hus")):
        return "改教著作"
    if any(k in t for k in ("巴特", "Barth", "莫爾特曼", "Moltmann", "拉納", "Rahner",
                            "潘霍華", "Bonhoeffer", "蒂利希", "Tillich", "潘能伯格", "Pannenberg",
                            "巴爾塔薩", "Balthasar", "Kung", "孔漢思")):
        return "近現代著作"
    if any(k in t for k in ("教科書", "導論", "概論", "introductory", "introduction to theology")):
        return "教科書/概論"
    if any(k in t for k in ("倫理神學", "性倫理", "生命倫理", "moral theology", "Christian ethics")):
        return "倫理神學"
    if any(k in t for k in ("靈修", "默觀", "spirituality", "默想", "祈禱")):
        return "靈修神學"
    if any(k in t for k in ("詮釋", "hermeneutic", "釋經", "解經")):
        return "神學詮釋/哲學"

    return None


# ── Gemini batched classifier ────────────────────────────────────────────

def _find_gemini_keys() -> list[str]:
    primary = ("GEMINI_API_KEY", "Gemini_API_Key", "gemini_api_key", "GOOGLE_API_KEY")
    raw = []
    for name in primary:
        v = os.environ.get(name)
        if v:
            raw.append(v); break
    for n in range(1, 11):
        for base in primary:
            v = os.environ.get(f"{base}_{n}")
            if v:
                raw.append(v); break
    keys, seen = [], set()
    for r in raw:
        for piece in r.split(","):
            k = piece.strip()
            if k and k not in seen:
                seen.add(k); keys.append(k)
    return keys


GEMINI_KEYS = _find_gemini_keys()
_key_idx = 0


PROMPT = """你是神學圖書分類器。每本書要分到下列 13 個子分類之一（繁體中文，逐字相同）：

歷史時期：
- 教父著作   (~AD 100-500 教父原典與翻譯)
- 中世紀著作 (~500-1500 經院神學、神秘主義原著)
- 改教著作   (~1500-1700 路德、加爾文等改教家原著)
- 近現代著作 (1700-至今 神學家本人著作，如巴特、莫爾特曼)

歷史研究（學者寫的歷史研究）：
- 教父研究   (學者研究教父思想／教義／傳統)
- 中世紀研究 (學者研究經院神學／中世紀)
- 改教研究   (學者研究改教時期神學)

主題：
- 教科書/概論 (神學導論、系統神學概論、教科書)
- 主題專論   (特定主題的學術 monograph，如基督論、教會論、聖經正典研究等)
- 倫理神學   (基督教倫理、生命倫理、社會倫理)
- 靈修神學   (默觀、祈禱、靈修生活)
- 神學詮釋/哲學 (神學詮釋學、宗教哲學、神哲學對話)
- 本地化處境神學 (亞洲神學、處境神學、解放神學等)

對下列每本書，回覆 JSON array：
[{{"id": "xxx", "subcategory": "教父著作"}}, ...]

注意：
- subcategory 必須剛好是上述 13 個 label 之一，不可改字。
- 翻譯／原著／註釋是「著作」；學者寫的論文／傳記／思想史是「研究」。
- 不確定就選最接近的「近現代著作」或「主題專論」。

書目：
{rows}
"""


def gemini_batch(books: list[dict]) -> dict[str, str]:
    """Classify a batch of books. Returns id -> subcategory."""
    global _key_idx
    if not GEMINI_KEYS:
        raise RuntimeError("no Gemini API key")
    rows = []
    for b in books:
        rows.append(
            f'- id={b["id"]}  title={b["title"][:80]!r}  '
            f'author={(b.get("author") or "")[:30]!r}  '
            f'existing_sub={(b.get("subcategory") or "")[:40]!r}'
        )
    prompt = PROMPT.format(rows="\n".join(rows))
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
    }
    base = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    while _key_idx < len(GEMINI_KEYS):
        key = GEMINI_KEYS[_key_idx]
        for attempt, wait in enumerate((0, 5, 15, 30), start=1):
            if wait:
                time.sleep(wait)
            r = requests.post(f"{base}?key={key}", json=body, timeout=60)
            if r.status_code == 200:
                data = r.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text.startswith("```"):
                    text = text.strip("`").split("\n", 1)[-1].rsplit("```", 1)[0]
                parsed = json.loads(text)
                result = {}
                for item in parsed:
                    sid = item.get("id")
                    sub = (item.get("subcategory") or "").strip()
                    if sid and sub in LABELS:
                        result[sid] = sub
                return result
            if r.status_code in (429, 503):
                print(f"  Gemini {r.status_code} key#{_key_idx} attempt {attempt}", file=sys.stderr)
                if attempt >= 3:
                    if _key_idx + 1 < len(GEMINI_KEYS):
                        _key_idx += 1
                        print(f"  → rotating to key #{_key_idx}", file=sys.stderr)
                    else:
                        raise RuntimeError(f"all {len(GEMINI_KEYS)} keys exhausted")
                    break
                continue
            raise RuntimeError(f"Gemini HTTP {r.status_code}: {r.text[:300]}")
    raise RuntimeError("Gemini all keys exhausted")


# ── Main flow ────────────────────────────────────────────────────────────

def fetch_theology_books() -> list[dict]:
    r = requests.get(
        f"{URL}/rest/v1/ebooks?select=id,title,author,subcategory&category=eq.神學&limit=2000",
        headers=H_GET, timeout=30,
    )
    r.raise_for_status()
    return r.json()


def update_subcategory(book_id: str, new_sub: str) -> None:
    r = requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{book_id}",
        headers=H_PATCH,
        json={"subcategory": new_sub},
        timeout=30,
    )
    r.raise_for_status()


def cmd_status() -> None:
    books = fetch_theology_books()
    from collections import Counter
    c = Counter()
    for b in books:
        c[b.get("subcategory") or "(none)"] += 1
    print(f"Total 神學: {len(books)}")
    canonical = sum(v for k, v in c.items() if k in LABELS)
    series = sum(v for k, v in c.items() if any(k.startswith(p) for p in PRESERVE_PREFIXES))
    other = len(books) - canonical - series
    print(f"  canonical label: {canonical}")
    print(f"  series preserved: {series}")
    print(f"  needs reclassify: {other}")
    print()
    for k, v in sorted(c.items(), key=lambda x: -x[1])[:30]:
        ok = "✓" if k in LABELS or any(k.startswith(p) for p in PRESERVE_PREFIXES) else "?"
        print(f"  {ok} {v:4d}  {k}")


def cmd_classify(dry_run: bool, limit: int | None, batch_size: int) -> None:
    books = fetch_theology_books()

    # Bucket: skip (preserve), rule-based, LLM-needed
    skip = []
    decided = []  # (book, new_sub)
    todo = []
    for b in books:
        s = b.get("subcategory") or ""
        if any(s.startswith(p) for p in PRESERVE_PREFIXES):
            skip.append(b)
            continue
        rule = rule_based_label(b["title"], b.get("author") or "", s)
        if rule and rule in LABELS:
            decided.append((b, rule))
            continue
        todo.append(b)

    if limit:
        todo = todo[:limit]

    print(f"Total: {len(books)} | preserve: {len(skip)} | rule-decided: {len(decided)} | LLM: {len(todo)}")

    # Apply rule-based decisions first
    for b, sub in decided:
        if (b.get("subcategory") or "") == sub:
            continue
        if dry_run:
            print(f"  [rule] {b['title'][:50]!r} : {b.get('subcategory')!r} → {sub!r}")
        else:
            update_subcategory(b["id"], sub)
    if not dry_run and decided:
        print(f"  rule-based applied: {len(decided)}")

    # LLM in batches
    if not todo:
        return
    for i in range(0, len(todo), batch_size):
        chunk = todo[i:i + batch_size]
        print(f"\n[batch {i // batch_size + 1}/{(len(todo) + batch_size - 1) // batch_size}] {len(chunk)} books")
        try:
            result = gemini_batch(chunk)
        except Exception as e:
            print(f"  ⚠ batch failed: {e}", file=sys.stderr)
            continue
        applied = 0
        for b in chunk:
            sub = result.get(b["id"])
            if not sub:
                print(f"  ? no result for {b['title'][:40]!r}")
                continue
            if dry_run:
                print(f"  [LLM] {b['title'][:50]!r} : {b.get('subcategory')!r} → {sub!r}")
            else:
                try:
                    update_subcategory(b["id"], sub)
                    applied += 1
                except Exception as e:
                    print(f"  ⚠ patch failed for {b['id'][:8]}: {e}", file=sys.stderr)
        if not dry_run:
            print(f"  ✓ {applied}/{len(chunk)} updated")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    cl = sub.add_parser("classify")
    cl.add_argument("--dry-run", action="store_true")
    cl.add_argument("--limit", type=int)
    cl.add_argument("--batch-size", type=int, default=25)
    args = p.parse_args()

    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "classify":
        cmd_classify(dry_run=args.dry_run, limit=args.limit, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
