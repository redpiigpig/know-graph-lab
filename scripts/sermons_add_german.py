"""Add the German 1916 original as a third column to the /gnostic "Seven Sermons
to the Dead" entry (doc_slug=seven-sermons-to-the-dead).

The gnostic library already holds gnosis.org English (182 sections) + a 繁中
translation (182 sections). Jung wrote the *Septem Sermones ad Mortuos* (1916)
in German; this script aligns that public-domain German original onto the same
182 section rows and inserts it as gnostic_versions.code='de_1916'
(category='source', is_default_orig) so the reader auto-shows 中/英/德.

Front matter sections (gnosis.org editorial intro, order_index 0–35) have no
German counterpart → no de row inserted (reader leaves that cell blank).
German source: klarerblick.de "Sieben Reden an die Toten" (Jung's text, PD).

Run --inspect first (no DB write; dumps an alignment sample).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from jung_ptypen_add_german import align_paras

DOC = "seven-sermons-to-the-dead"
VCODE = "de_1916"
EN_CODE = "gnosis_en"
BODY_START = 36  # order_index of the title; 0–35 = gnosis.org editorial front matter
DE_SRC = Path(r"C:/Users/user/AppData/Local/Temp/claude/c--Users-user-Desktop-know-graph-lab"
              r"/f9977fac-506a-4c1a-bed5-8e59876d2d0c/scratchpad/klar_text.txt")
DE_TITLE = ("Die sieben Belehrungen der Toten, geschrieben von Basilides in Alexandria, "
            "der Stadt, wo der Osten den Westen berührt.")


def load_env() -> None:
    for line in Path(".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def fetch_en_sections() -> list[dict]:
    import requests

    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    r = requests.get(
        f"{url}/rest/v1/gnostic_sections"
        f"?select=order_index,text&doc_slug=eq.{DOC}&version_code=eq.{EN_CODE}&order=order_index",
        headers=h, timeout=30)
    r.raise_for_status()
    return r.json()


def load_german_paras() -> list[str]:
    t = DE_SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("Die Toten kamen zurück von Jerusalem")
    j = t.find("Schlagwörter:", i)
    body = t[i:j if j > i else len(t)].strip()
    return [re.sub(r"\s+", " ", p).strip() for p in body.split("\n") if p.strip()]


def build_alignment() -> dict[int, str]:
    """Return {order_index: german_text} for the body sections."""
    en_rows = fetch_en_sections()
    body = [r for r in en_rows if r["order_index"] > BODY_START]  # 37..181
    en_texts = [r["text"] for r in body]
    de_paras = load_german_paras()

    de2en = align_paras(en_texts, de_paras)
    by_oi: dict[int, list[str]] = {}
    for jj, de in enumerate(de_paras):
        oi = body[de2en.get(jj, len(en_texts) - 1)]["order_index"]
        by_oi.setdefault(oi, []).append(de)
    out = {oi: "\n\n".join(v) for oi, v in by_oi.items()}
    out[BODY_START] = DE_TITLE  # German title aligned to the English title section
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", action="store_true")
    args = ap.parse_args()
    load_env()

    de_by_oi = build_alignment()
    en_rows = {r["order_index"]: r["text"] for r in fetch_en_sections()}
    print(f"aligned German into {len(de_by_oi)} body sections "
          f"(en body sections {sum(1 for oi in en_rows if oi > BODY_START)})")

    if args.inspect:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        for oi in sorted(de_by_oi)[:6] + sorted(de_by_oi)[70:73]:
            print(f"\n[{oi}] EN: {en_rows.get(oi, '')[:90]}")
            print(f"[{oi}] DE: {de_by_oi[oi][:90]}")
        return

    import requests

    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
         "Prefer": "resolution=merge-duplicates"}
    # 1) upsert the version row
    ver = {
        "code": VCODE, "name_zh": "德文原典（1916）", "name_en": "German Original (1916)",
        "language": "de", "language_zh": "德文", "category": "source", "public_domain": True,
        "copyright_notice": None, "source_url": "https://ein-klarer-blick.de/sieben-reden-an-die-toten/",
        "display_order": 5, "is_default_en": False, "is_default_zh": False, "is_default_orig": True,
    }
    requests.post(f"{url}/rest/v1/gnostic_versions", headers=h, json=ver, timeout=30).raise_for_status()
    # 2) replace this doc's de sections
    requests.delete(f"{url}/rest/v1/gnostic_sections?doc_slug=eq.{DOC}&version_code=eq.{VCODE}",
                    headers={k: v for k, v in h.items() if k != "Prefer"}, timeout=30).raise_for_status()
    rows = [{
        "doc_slug": DOC, "version_code": VCODE, "order_index": oi,
        "section_label": None, "text": txt, "char_count": len(txt),
    } for oi, txt in sorted(de_by_oi.items())]
    for i in range(0, len(rows), 50):
        requests.post(f"{url}/rest/v1/gnostic_sections", headers=h, json=rows[i:i + 50],
                      timeout=60).raise_for_status()
    print(f"inserted version {VCODE} + {len(rows)} de sections for {DOC}")


if __name__ == "__main__":
    main()
