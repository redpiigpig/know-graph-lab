"""Seed bible_canon_books order for Orthodox / Syriac / Ethiopian (Catholic is
seeded by database/bible-canon-order.sql).

Each tradition has its own canonical sequence; deuterocanon is folded into the OT
in its traditional slot and green-marked (is_deutero = NOT in the Protestant
66-book protocanon). Books not in a tradition's canon (canon_<x>=false) are
skipped automatically, so the ordered lists below may be supersets.

Tradition-specific features encoded:
  - Orthodox (LXX/Byzantine): 1 Esdras before Ezra; Psalm 151 + Prayer of
    Manasseh by the Psalter; **Minor Prophets before Major** (LXX order);
    **Catholic epistles before Pauline** (Byzantine NT order); 4 Macc appendix.
  - Syriac (Peshitta): NT is 22 books (omits 2 Pet, 2-3 John, Jude, Revelation).
  - Ethiopian (Tewahedo): Jubilees / 1 Enoch / 4 Baruch placed among the OT.
    (Internal Ethiopian order is highly variable — best-effort standard sequence.)

Idempotent upsert. Usage: python scripts/seed_canon_order.py [--dry-run]
"""
from __future__ import annotations
import os, sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
for l in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
    if "=" in l and not l.startswith("#"):
        k, v = l.split("=", 1)
        os.environ.setdefault(k.strip().lstrip("﻿"), v.strip().strip("'\""))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
U = os.environ["SUPABASE_URL"]; K = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": K, "Authorization": f"Bearer {K}"}
HJ = {**H, "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=minimal"}

NT = {"mat", "mrk", "luk", "jhn", "act", "rom", "1co", "2co", "gal", "eph", "php",
      "col", "1th", "2th", "1ti", "2ti", "tit", "phm", "heb", "jas", "1pe", "2pe",
      "1jn", "2jn", "3jn", "jud", "rev",
      # 衣索匹亞 broader canon 新約「教會秩序書」
      "e_didache", "e_didasc", "e_sinodos1", "e_sinodos2", "e_sinodos3",
      "e_sinodos4", "e_kidan1", "e_kidan2"}

# 新約子分類（衣索匹亞「教會秩序書」）：在新約組下另立小標。
CHURCH_ORDER = ["e_didache", "e_didasc", "e_sinodos1", "e_sinodos2",
                "e_sinodos3", "e_sinodos4", "e_kidan1", "e_kidan2"]
SECTIONS: dict[str, str] = {c: "教會秩序書（含衣索匹亞六法典）" for c in CHURCH_ORDER}

# ── Per-tradition canonical order (supersets; filtered to actual members) ──────
ORTHODOX = [
    # OT — Pentateuch
    "gen", "exo", "lev", "num", "deu",
    # Historical (1 Esdras before Ezra; Tobit/Judith/Esther; 1-3 Macc)
    "jos", "jdg", "rut", "1sa", "2sa", "1ki", "2ki", "1ch", "2ch",
    "1es", "ezr", "neh", "est", "tob", "jdt", "1ma", "2ma", "3ma",
    # Poetic/Wisdom (Psalter + Ps151 + Prayer of Manasseh)
    "psa", "ps2", "man", "job", "pro", "ecc", "sng", "wis", "sir",
    # Prophets — Minor (LXX order) then Major; Daniel additions after Daniel
    "hos", "amo", "mic", "jol", "oba", "jon", "nam", "hab", "zep", "hag", "zec", "mal",
    "isa", "jer", "bar", "lam", "epj", "ezk", "dan", "sus", "bel", "aza",
    "4ma",  # appendix
    # NT — Gospels, Acts, Catholic epistles, Pauline, Revelation (Byzantine)
    "mat", "mrk", "luk", "jhn", "act",
    "jas", "1pe", "2pe", "1jn", "2jn", "3jn", "jud",
    "rom", "1co", "2co", "gal", "eph", "php", "col", "1th", "2th",
    "1ti", "2ti", "tit", "phm", "heb", "rev",
]

SYRIAC = [
    "gen", "exo", "lev", "num", "deu",
    "jos", "jdg", "rut", "1sa", "2sa", "1ki", "2ki", "1ch", "2ch", "ezr", "neh", "est",
    "tob", "jdt", "1ma", "2ma",
    "job", "psa", "pro", "ecc", "sng", "wis", "sir",
    "isa", "jer", "lam", "epj", "bar", "ezk", "dan", "sus", "bel", "aza",
    "hos", "jol", "amo", "oba", "jon", "mic", "nam", "hab", "zep", "hag", "zec", "mal",
    # NT — Peshitta 22 (no 2pe/2jn/3jn/jud/rev)
    "mat", "mrk", "luk", "jhn", "act",
    "jas", "1pe", "1jn",
    "rom", "1co", "2co", "gal", "eph", "php", "col", "1th", "2th",
    "1ti", "2ti", "tit", "phm", "heb",
]

ETHIOPIAN = [
    "gen", "exo", "lev", "num", "deu", "jub",           # Jubilees retells Gen-Exod
    "jos", "jdg", "rut", "1sa", "2sa", "1ki", "2ki", "1ch", "2ch",
    "1es", "2es", "ezr", "neh", "est", "tob", "jdt", "1ma", "2ma", "3ma",
    "job", "psa", "ps2", "man", "pro", "ecc", "sng", "wis", "sir",
    "eno",                                              # 1 Enoch among the prophetic
    "isa", "jer", "bar", "4ba", "lam", "epj", "ezk", "dan", "sus", "bel", "aza",
    "hos", "amo", "mic", "jol", "oba", "jon", "nam", "hab", "zep", "hag", "zec", "mal",
    "4ma",
    "mat", "mrk", "luk", "jhn", "act",
    "rom", "1co", "2co", "gal", "eph", "php", "col", "1th", "2th",
    "1ti", "2ti", "tit", "phm", "heb",
    "jas", "1pe", "2pe", "1jn", "2jn", "3jn", "jud", "rev",
    # 新約「教會秩序書」：十二使徒遺訓 + 使徒教訓 + 衣索匹亞六法典
    "e_didache", "e_didasc", "e_sinodos1", "e_sinodos2", "e_sinodos3",
    "e_sinodos4", "e_kidan1", "e_kidan2",
]

# Catholic (思高/Vulgate order). 達尼爾增補(蘇撒納/貝耳與大龍/阿匝黎雅)與耶肋米亞書信
# 在本資料庫存為獨立書卷(sus/bel/aza/epj) → 與其他傳統一致，列為獨立綠卡置於 達/巴 之後
# （故天主教 = 77 卷，與 canon 旗標一致）。
CATHOLIC = [
    "gen", "exo", "lev", "num", "deu",
    "jos", "jdg", "rut", "1sa", "2sa", "1ki", "2ki", "1ch", "2ch", "ezr", "neh",
    "tob", "jdt", "est", "1ma", "2ma",
    "job", "psa", "pro", "ecc", "sng", "wis", "sir",
    "isa", "jer", "lam", "bar", "epj", "ezk", "dan", "sus", "bel", "aza",
    "hos", "jol", "amo", "oba", "jon", "mic", "nam", "hab", "zep", "hag", "zec", "mal",
    "mat", "mrk", "luk", "jhn", "act",
    "rom", "1co", "2co", "gal", "eph", "php", "col", "1th", "2th",
    "1ti", "2ti", "tit", "phm", "heb",
    "jas", "1pe", "2pe", "1jn", "2jn", "3jn", "jud", "rev",
]

TRADITIONS = {"catholic": CATHOLIC, "orthodox": ORTHODOX, "syriac": SYRIAC, "ethiopian": ETHIOPIAN}

# 傳統專屬書名覆寫 (canon, book_code) → (全名, 簡稱)。
# 東正教厄斯德拉採七十士譯本命名：Ἔσδρας Αʹ=以斯拉A、Ἔσδρας Βʹ(=Ezra/Neh)=以斯拉上/下。
NAME_OVERRIDES: dict[tuple[str, str], tuple[str, str]] = {
    ("orthodox", "1es"): ("以斯拉A", "拉A"),
    ("orthodox", "ezr"): ("以斯拉上", "拉上"),
    ("orthodox", "neh"): ("以斯拉下", "拉下"),
}

# 「補編」——不是獨立成卷，而是某卷的次經增補：併入母卷（parent_code），不出獨立書卡，
# reader 內以「屬於次經範圍」標註該章。母卷在書卡上以黃色標示（has_additions）。
#   蘇撒納/貝耳與大龍/阿匝黎雅 → 但以理書；詩篇151 → 詩篇；耶肋米亞書信 → 巴錄書。
ADDITIONS: dict[str, str] = {
    "sus": "dan", "bel": "dan", "aza": "dan", "ps2": "psa", "epj": "bar",
}
# 希臘以斯帖增補無獨立書卷（併在 est 經文內）→ 這些傳統的 est 標黃。
ESTHER_GREEK = {"catholic", "orthodox", "ethiopian"}


def main():
    dry = "--dry-run" in sys.argv
    books = requests.get(
        f"{U}/rest/v1/bible_books?select=code,canon_protestant,canon_catholic,canon_orthodox,canon_syriac,canon_ethiopian,chapter_count&limit=200",
        headers=H, timeout=30).json()
    proto = {b["code"] for b in books if b["canon_protestant"]}
    member = {
        "catholic": {b["code"] for b in books if b["canon_catholic"]},
        "orthodox": {b["code"] for b in books if b["canon_orthodox"]},
        "syriac":   {b["code"] for b in books if b["canon_syriac"]},
        "ethiopian":{b["code"] for b in books if b["canon_ethiopian"]},
    }

    for canon, order in TRADITIONS.items():
        rows, seen = [], set()
        n = 0
        for code in order:
            if code not in member[canon] or code in seen:
                continue
            seen.add(code); n += 1
            ov = NAME_OVERRIDES.get((canon, code))
            parent = ADDITIONS.get(code)
            parent = parent if (parent and parent in member[canon]) else None
            rows.append({
                "canon": canon, "book_code": code,
                "testament": "nt" if code in NT else "ot",
                "sort_order": n,
                "is_deutero": code not in proto,
                "chapter_count": None,
                "name_override": ov[0] if ov else None,
                "abbr_override": ov[1] if ov else None,
                "parent_code": parent,           # 補編：所屬母卷（→不出書卡、reader 標次經）
                "has_additions": False,          # 母卷下方統一回填
                "section": SECTIONS.get(code),    # 新約子分類（教會秩序書）
            })
        # 回填母卷 has_additions（含補編 → 黃色）：被指為 parent 的卷，或希臘以斯帖
        parents_with_add = {r["parent_code"] for r in rows if r["parent_code"]}
        for r in rows:
            if r["book_code"] in parents_with_add:
                r["has_additions"] = True
            if r["book_code"] == "est" and canon in ESTHER_GREEK:
                r["has_additions"] = True
        missing = member[canon] - seen
        print(f"{canon}: {len(rows)} rows ({sum(1 for r in rows if r['is_deutero'])} deutero)"
              f"{'  MISSING=' + str(sorted(missing)) if missing else ''}")
        if dry:
            continue
        r = requests.post(
            f"{U}/rest/v1/bible_canon_books?on_conflict=canon,book_code",
            headers=HJ, json=rows, timeout=60)
        if r.status_code >= 300:
            print(f"  upsert {r.status_code}: {r.text[:300]}", file=sys.stderr)


if __name__ == "__main__":
    main()
