#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全集轉錄狀態對帳：hub 上寫的 status，和 DB 裡真正有多少內容，對不對得起來。

會做這支的原因：榮格十六卷 2026-08 就翻完了，hub 上卻一直掛著 in-progress，DB 裡
只有一卷——「翻完了」「上架了」「標好了」是三件事，中間任何一環斷掉都沒有徵兆
（[[feedback_reader_silent_failures]]）。這支把三者擺在一起看。

四種對不上：
  假 done      hub 說 done，但那本 ebook 沒有 chunk（或根本沒有 ebookId）
  該標 done    hub 說 planned/in-progress，DB 其實已經滿了
  沒列進 hub   DB 有這本全集書，hub works[] 找不到對應 ebookId
  進行中       DB 有內容但本機佇列還沒跑完 —— note 要寫「做到哪」

  python scripts/collected_works_status.py              # 全部
  python scripts/collected_works_status.py --author jung
  python scripts/collected_works_status.py --progress   # 併看本機佇列進度
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
STORE = ROOT / "stores" / "collectedWorks.ts"

# 本機佇列的進度來源：slug → (目錄, 每單位的檔名樣式)。用來回答「做到哪」。
PROGRESS_DIRS = {
    "jung": (ROOT / ".claude/skills/ebook-collected-works/jung_data/cw-full", "status.json"),
    "yanaihara": (ROOT / ".claude/skills/ebook-collected-works/yanaihara_data", "sec*.json"),
    "uchimura": (ROOT / ".claude/skills/ebook-collected-works/uchimura_data", "sec*.json"),
    "plato": (pathlib.Path("c:/tmp/plato_cache"), "*.txt"),
    "plotinus": (pathlib.Path("c:/tmp/plotinus_cache"), "*.txt"),
    "epicurus": (pathlib.Path("c:/tmp/epicurus_cache"), "*.txt"),
    "epictetus": (pathlib.Path("c:/tmp/epictetus_cache"), "*.txt"),
}

_AUTHOR_RE = re.compile(r"""^\s*["']?slug["']?:\s*['"]([a-z0-9-]+)['"]""", re.M)
_FIELD_RE = re.compile(r"""["']?(title|status|ebookId|externalUrl|note)["']?:\s*['"]([^'"]*)['"]""")


# ── store 解析（純函式）──────────────────────────────────────────────────

def parse_store(text: str) -> list[dict]:
    """collectedWorks.ts → [{author, title, status, ebookId, note}]。

    這個檔一半是手寫 TS、一半是 JSON dump 進去的：key 有的帶引號有的不帶，**欄位順序
    也不一致**——手寫那半是 title→status→ebookId，dump 那半是 status→ebookId→title。
    所以一筆的邊界只能靠結尾的 `}`，不能靠 title 開頭（那樣會把下一筆的書名配到上一
    筆的 ebookId 上，星雲那一段就是這樣被讀錯的）。
    """
    out: list[dict] = []
    author = "?"

    def blank() -> dict:
        return {"author": author, "title": "", "status": "", "ebookId": "",
                "externalUrl": "", "note": "", "status_line": -1, "note_line": -1}

    cur = blank()
    for i, line in enumerate(text.splitlines()):
        m = _AUTHOR_RE.match(line)
        if m:
            author = m.group(1)
            cur = blank()
            continue
        f = _FIELD_RE.search(line)
        if f:
            key, val = f.group(1), f.group(2)
            cur[key] = val
            if key in ("status", "note"):
                cur[f"{key}_line"] = i
            continue
        if line.strip().startswith("}"):     # 一筆結束
            if cur["status"] and cur["title"]:
                out.append(cur)
            cur = blank()
    if cur:
        out.append(cur)
    return [w for w in out if w["status"]]


# ── DB ────────────────────────────────────────────────────────────────────

def db_books() -> dict[str, dict]:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"')
    url, key = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    rows, off = [], 0
    while True:
        req = urllib.request.Request(
            f"{url}/rest/v1/ebooks?collection=eq.collected-works"
            f"&select=id,title,author,chunk_count,total_chars&limit=1000&offset={off}",
            headers={"apikey": key, "Authorization": f"Bearer {key}"})
        batch = json.loads(urllib.request.urlopen(req, timeout=90).read())
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    return {r["id"]: r for r in rows}


def local_progress() -> dict[str, str]:
    """本機佇列做到哪——只給概數，回答「這本是不是還在跑」。"""
    out = {}
    for name, (d, pattern) in PROGRESS_DIRS.items():
        if not d.is_dir():
            continue
        parts = []
        for sub in sorted(p for p in d.iterdir() if p.is_dir()):
            if pattern == "status.json":
                f = sub / "status.json"
                if f.exists():
                    s = json.loads(f.read_text(encoding="utf-8"))
                    parts.append(f"{sub.name} {s.get('done')}/{s.get('total')}")
            else:
                parts.append(f"{sub.name} {len(list(sub.glob(pattern)))}")
        if parts:
            out[name] = "  ".join(parts)
    return out


# ── 標記回 store ──────────────────────────────────────────────────────────

_PROGRESS_TAG = "｜轉錄中："


def _builder_titles() -> dict[str, tuple[pathlib.Path, str]]:
    """hub 書名 → (逐節快取目錄, slug)。三支 builder 自己的 WORKS 表就是對照表。"""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    out: dict[str, tuple[pathlib.Path, str]] = {}
    for mod, cache, key in (("plotinus_build", "plotinus_cache", "title_zh"),
                            ("epicurus_build", "epicurus_cache", "title_zh"),
                            ("epictetus_build", "epictetus_cache", "title_zh")):
        try:
            m = __import__(mod)
        except Exception:  # noqa: BLE001 — 對照表拿不到就不標進度，不該擋住 status
            continue
        for slug, w in getattr(m, "WORKS", {}).items():
            title = w.get(key) or w.get("title") or ""
            if title:
                out[title] = (pathlib.Path("c:/tmp") / cache / f"{slug}_zh", slug)
    return out


def progress_note(title: str, titles: dict) -> str:
    """『做到哪』：本機逐節快取數。書名對不上或還沒開跑就回空字串。"""
    for hub_title, (d, _slug) in titles.items():
        if hub_title and (hub_title in title or title.startswith(hub_title[:6])):
            n = len(list(d.glob("*.txt"))) if d.is_dir() else 0
            if n:
                import datetime
                today = datetime.date.today().isoformat()
                return f"{_PROGRESS_TAG}本機已完成 {n} 節（{today}）"
    return ""


def demote_fake(fake_done: list, books: dict) -> int:
    """假 done 降級：status 改 planned，指向不存在的 ebookId 整行拿掉。

    留著一個查無此書的 ebookId 比沒有更糟——hub 上是可以點的連結，點進去才發現空的。
    行號會因刪行位移，所以由後往前改。
    """
    lines = STORE.read_text(encoding="utf-8").splitlines(keepends=True)
    jobs = sorted(fake_done, key=lambda t: t[0]["status_line"], reverse=True)
    changed = 0
    for w, _n in jobs:
        i = w["status_line"]
        if i < 0:
            continue
        lines[i] = re.sub(r"(['\"])done\1", r"\1planned\1", lines[i], count=1)
        eid = w["ebookId"]
        if eid and eid not in books:
            for j in range(max(0, i - 6), min(len(lines), i + 7)):
                if eid in lines[j]:
                    del lines[j]
                    break
        changed += 1
    if changed:
        STORE.write_text("".join(lines), encoding="utf-8")
    return changed


def _norm_title(s: str) -> str:
    """比對書名用：去掉括號註記（英繁對照…）與標點。"""
    s = re.sub(r"[（(\[【].*?[）)\]】]", "", s or "")
    return re.sub(r"[《》〈〉·‧・\s：:—\-]", "", s)


def author_names(text: str) -> dict[str, str]:
    """hub slug → 繁中作者名（DB 的 author 欄用的是繁中名）。"""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"""^\s*["']?slug["']?:\s*['"]([a-z0-9-]+)['"]""", line)
        if m:
            cur = m.group(1)
            continue
        m2 = re.match(r"""^\s*["']?name["']?:\s*['"]([^'"]+)['"]""", line)
        if m2 and cur and cur not in out:
            out[cur] = m2.group(1)
    return out


def link_orphans(works: list, books: dict, *, apply: bool) -> list[str]:
    """DB 有、hub 沒指到的書：書名對得上就把 ebookId 補進去（或換成內容較多的那本）。"""
    text = STORE.read_text(encoding="utf-8")
    zh2slug = {v: k for k, v in author_names(text).items()}
    claimed = {w["ebookId"] for w in works if w["ebookId"]}
    orphans = [b for eid, b in books.items()
               if eid not in claimed and (b["chunk_count"] or 0) >= 2]
    by_author: dict[str, list] = {}
    for w in works:
        by_author.setdefault(w["author"], []).append(w)

    lines = text.splitlines(keepends=True)
    plan: list[tuple[int, str, str]] = []   # (status_line, 新 ebookId, 說明)
    notes: list[str] = []
    for b in sorted(orphans, key=lambda x: -(x["chunk_count"] or 0)):
        author = b["author"] or ""
        slug = zh2slug.get(author)
        if not slug:
            # DB 的 author 常是簡稱（「弗雷澤」對 hub 的「詹姆斯‧弗雷澤」），互為包含就算同一人
            cands = [s for zh, s in zh2slug.items()
                     if len(zh) > 1 and (zh in author or author in zh)]
            slug = cands[0] if len(cands) == 1 else None
        if not slug:
            notes.append(f"無 hub：{b['author']}／{b['title'][:24]}（{b['chunk_count']} chunks）")
            continue
        nb = _norm_title(b["title"])
        for w in by_author.get(slug, []):
            nw = _norm_title(w["title"])
            if not nw or nw not in nb:
                continue
            old = (books.get(w["ebookId"], {}) or {}).get("chunk_count") or 0
            if w["ebookId"] and old >= (b["chunk_count"] or 0):
                continue                      # 已指到內容更多的版本，別動
            why = "補上" if not w["ebookId"] else f"換版本（{old}→{b['chunk_count']}）"
            plan.append((w["status_line"], b["id"], w["ebookId"],
                         f"{slug}／{w['title'][:20]}：{why}"))
            break

    for i, eid, old_id, why in sorted(plan, key=lambda t: t[0], reverse=True):
        notes.append(why)
        if not apply or i < 0:
            continue
        line = lines[i]
        quote = "'" if "'" in line.split(":", 1)[1] else '"'
        indent = line[:len(line) - len(line.lstrip())]
        lines[i] = re.sub(r"(['\"])(?:planned|in-progress)\1", r"\1done\1", line, count=1)
        if eid in "".join(lines[max(0, i - 6):i + 7]):
            continue                          # 已經有這個 id 了
        if old_id:                            # 換版本：改寫原本那行，不是再插一行
            for j in range(max(0, i - 6), min(len(lines), i + 7)):
                if old_id in lines[j]:
                    lines[j] = lines[j].replace(old_id, eid)
                    break
            continue
        lines.insert(i + 1, f"{indent}ebookId: {quote}{eid}{quote},\n")
    if apply and plan:
        STORE.write_text("".join(lines), encoding="utf-8")
    return notes


def apply_marks(should_done: list, in_flight: list, titles: dict) -> int:
    """把 status 改對、把進度寫進 note。逐行替換，不動縮排與引號風格。"""
    lines = STORE.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = 0
    for w, _n in should_done:
        i = w["status_line"]
        if i < 0:
            continue
        lines[i] = re.sub(r"(['\"])(?:planned|in-progress)\1", r"\1done\1", lines[i], count=1)
        changed += 1
    for w in in_flight:
        i, note = w["note_line"], w["note"]
        add = progress_note(w["title"], titles)
        if i < 0 or not add:
            continue
        base = note.split(_PROGRESS_TAG)[0].rstrip()
        if base + add == note:
            continue
        lines[i] = lines[i].replace(note, base + add, 1)
        changed += 1
    if changed:
        STORE.write_text("".join(lines), encoding="utf-8")
    return changed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", help="只看一位作家的 slug")
    ap.add_argument("--progress", action="store_true", help="附上本機佇列進度")
    ap.add_argument("--apply", action="store_true",
                    help="把「該標 done」改成 done，並把進度寫進 in-progress 的 note")
    ap.add_argument("--fix-fake", action="store_true",
                    help="假 done 降級 planned，並拿掉查無此書的 ebookId")
    ap.add_argument("--link", action="store_true",
                    help="孤兒書：書名對得上就把 ebookId 補進 hub（先看 --link 再加 --apply）")
    a = ap.parse_args()

    works = parse_store(STORE.read_text(encoding="utf-8"))
    if a.author:
        works = [w for w in works if w["author"] == a.author]
    books = db_books()
    claimed = {w["ebookId"] for w in works if w["ebookId"]}

    fake_done, should_done, in_flight = [], [], []
    for w in works:
        n = (books.get(w["ebookId"], {}) or {}).get("chunk_count") or 0
        # 連外部 corpus 的（東方聖書、/gnostic）本來就沒有自己的 ebook，不算假 done
        if w["status"] == "done" and n < 2 and not w["externalUrl"]:
            fake_done.append((w, n))
        elif w["status"] in ("planned", "in-progress") and n >= 2:
            should_done.append((w, n))
        elif w["status"] == "in-progress" and n < 2:
            in_flight.append(w)

    # 兩種「看起來像缺漏、其實不是」：
    #   譯本集——東方聖書那五十卷的 author 是譯者，本體在 /sacred-books-east
    #   同書異版——hub 已經指到同一著作的另一個譯本（通常是內容更多的那個）
    text = STORE.read_text(encoding="utf-8")
    zh2slug = {v: k for k, v in author_names(text).items()}
    # 只有「hub 那一筆已經指到別本」才算同書異版；hub 那筆若還沒有 ebookId，
    # 這本就是該補上去的那一本（矢內原《耶穌傳》一度被這條吃掉）。
    linked_titles: dict[str, set] = {}
    for w in works:
        if w["ebookId"]:
            linked_titles.setdefault(w["author"], set()).add(_norm_title(w["title"]))

    def other_edition(b: dict) -> bool:
        slug = zh2slug.get(b["author"] or "")
        nb = _norm_title(b["title"])
        return any(t and t in nb for t in linked_titles.get(slug, ()))

    corpus, other, orphan = [], [], []
    for eid, b in books.items():
        if eid in claimed or (b["chunk_count"] or 0) < 2 or a.author:
            continue
        (corpus if "（譯）" in (b["author"] or "")
         else other if other_edition(b) else orphan).append(b)

    def show(title, rows, fmt):
        print(f"\n■ {title}（{len(rows)}）")
        for r in rows[:40]:
            print("   " + fmt(r))
        if len(rows) > 40:
            print(f"   …另外 {len(rows) - 40} 筆")

    show("假 done：hub 說完成，DB 沒有內容", fake_done,
         lambda t: f"{t[0]['author']:14} {t[0]['title'][:26]:28} chunks={t[1]}")
    show("該標 done：DB 已經滿了，hub 還沒改", should_done,
         lambda t: f"{t[0]['author']:14} {t[0]['title'][:26]:28} chunks={t[1]}")
    show("進行中：hub 標 in-progress 且尚無內容（note 要寫做到哪）", in_flight,
         lambda w: f"{w['author']:14} {w['title'][:26]:28} {w['note'][:40]}")
    show("沒列進 hub：DB 有這本全集書，works[] 沒有它", orphan,
         lambda b: f"{(b['author'] or '?')[:14]:14} {b['title'][:30]:32} chunks={b['chunk_count']}")
    show("同書異版：hub 指到另一個譯本（不算缺漏）", other,
         lambda b: f"{(b['author'] or '?')[:14]:14} {b['title'][:30]:32} chunks={b['chunk_count']}")
    show("譯本集：本體在 /sacred-books-east（不算缺漏）", corpus,
         lambda b: f"{(b['author'] or '?')[:14]:14} {b['title'][:30]:32} chunks={b['chunk_count']}")

    if a.progress:
        print("\n■ 本機佇列進度")
        for name, line in local_progress().items():
            print(f"   {name}: {line[:160]}")

    if a.link:
        for line in link_orphans(works, books, apply=a.apply):
            print("   " + line)
    if a.fix_fake:
        n = demote_fake(fake_done, books)
        print(f"\n✔ 假 done 降級 {n} 筆（status→planned，查無此書的 ebookId 已移除）")
    if a.apply:
        n = apply_marks(should_done, in_flight, _builder_titles())
        print(f"\n✔ 已改 {n} 處（{STORE.name}）；假 done 那幾筆要人工判斷，沒有動")


if __name__ == "__main__":
    main()
