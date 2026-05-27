"""Backfill 新教 / 天主教 dual translations on existing theologians +
theological_terms rows where we can confidently distinguish them.

Many of the 49 seed entries (from seed_glossary_anf_vol1.py) only have
name_recommended / zh_recommended set. We now want both name_protestant
and name_catholic_sgs explicit. This script walks a hand-curated table
of known Protestant↔Catholic divergences and UPDATEs the right slot.

Run:
    python scripts/backfill_dual_translations.py            # apply
    python scripts/backfill_dual_translations.py --dry-run  # preview

Idempotent. Skips rows that already have both slots filled.
"""
from __future__ import annotations
import argparse
import os

import requests
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

# ── Persons: (name_english_lowercase, protestant, catholic_sgs) ──
# Where the two traditions diverge significantly; identical translations
# fall through to populate just whichever side was previously blank.
PERSON_DUAL = {
    # Apostles / NT figures
    "paul (apostle)":           ("保羅",         "保祿"),
    "peter (apostle)":          ("彼得",         "伯多祿"),
    "john (apostle)":           ("約翰",         "若望"),
    "james (apostle)":          ("雅各",         "雅各伯"),
    "matthew (apostle)":        ("馬太",         "瑪竇"),
    "mark (evangelist)":        ("馬可",         "馬爾谷"),
    "luke (evangelist)":        ("路加",         "路加"),
    "cephas":                   ("磯法",         "刻法"),
    "mary (mother of jesus)":   ("馬利亞",       "瑪利亞"),
    "salome":                   ("撒羅米",       "撒羅默"),
    "clopas":                   ("革羅帕",       "克羅帕"),
    "trypho":                   ("特里弗",       "特黎豐"),
    "diognetus":                ("丟格那妥",     "狄奧革乃托"),
    "mathetes":                 ("瑪忒特",       "瑪忒特"),
    "hero (deacon of antioch)": ("黑羅",         "赫羅"),
    "aristion":                 ("亞里斯鐸",     "亞理斯鐸"),
    # Apostolic Fathers
    "clement of rome":          ("羅馬的革利免", "羅馬‧克萊孟一世"),
    "ignatius of antioch":      ("安提阿的依納爵","安提約基雅‧依納爵"),
    "polycarp of smyrna":       ("士每拿的坡旅甲","斯米爾納‧玻里加"),
    "papias of hierapolis":     ("希拉波利的帕皮亞","希拉波利‧帕皮亞"),
    "justin martyr":            ("殉道者游斯丁", "殉道者猶斯定"),
    "irenaeus of lyon":         ("里昂的愛任紐", "里昂‧依肋內"),
    "irenæus of lyon":          ("里昂的愛任紐", "里昂‧依肋內"),
    "tertullian":               ("特土良",       "戴爾都良"),
    "clement of alexandria":    ("亞歷山卓的革利免","亞歷山卓‧克萊孟"),
    "cassiodorus":              ("卡西奧多魯斯", "卡西奧多魯斯"),
    "barnabas":                 ("巴拿巴",       "巴爾納伯"),
    "augustine":                ("奧古斯丁",     "奧斯定"),
    "augustine of hippo":       ("奧古斯丁",     "希波‧奧斯定"),
    "athanasius":               ("亞他那修",     "亞達納修"),
    "athanasius of alexandria": ("亞他那修",     "亞歷山卓‧亞達納修"),
    "basil of caesarea":        ("巴西流",       "巴西略"),
    "gregory of nazianzus":     ("拿先素斯的貴格利","納齊安‧額我略"),
    "gregory of nyssa":         ("尼撒的貴格利", "尼撒‧額我略"),
    "john chrysostom":          ("屈梭多模",     "金口若望"),
    "jerome":                   ("耶柔米",       "聖熱羅尼莫"),
    "ambrose":                  ("安波羅修",     "安博"),
}

# ── Places: (term_english_lowercase, protestant, catholic_sgs) ──
PLACE_DUAL = {
    "corinth":            ("哥林多",      "格林多"),
    "smyrna":             ("士每拿",      "士麥拿"),
    "antioch":            ("安提阿",      "安提約基雅"),
    "philippi":           ("腓立比",      "斐理伯"),
    "ephesus":            ("以弗所",      "厄弗所"),
    "magnesia":           ("馬內夏",      "瑪格內西雅"),
    "tralles":            ("特拉勒",      "特辣肋"),
    "philadelphia":       ("非拉鐵非",    "非拉德非雅"),
    "tarsus":             ("他爾索",      "塔爾索"),
    "hierapolis":         ("希拉波利",    "希拉波里"),
    "lyon":               ("里昂",        "里昂"),
    "rome":               ("羅馬",        "羅馬"),
    "samaria":            ("撒瑪利亞",    "撒瑪黎雅"),
    "flavia neapolis":    ("弗拉維亞‧尼亞波利斯", "弗拉維亞‧納波利斯"),
}

# Books of the Bible commonly cited in patristic works (small set)
WORK_DUAL = {
    # Justin's works keep same Chinese title (technical translation, not denom-specific)
    # Bible book names where 思高 differs from Protestant:
    # — kept generic; users can edit per book context
}

# Sects — mostly transliteration variants, occasionally semantic shifts
SECT_DUAL = {
    "ebionites":      ("伊比昂派",     "厄比雍派"),
    "marcionites":    ("馬吉安派",     "馬西雍派"),
    "gnostics":       ("諾斯底派",     "諾斯底派"),  # same
    "valentinians":   ("瓦倫廷派",     "瓦倫提諾派"),
}

# Theological terms — many diverge significantly (Logos/聖言, etc.)
TERM_DUAL = {
    "logos":          ("道",           "聖言"),
    "trinity":        ("三位一體",     "聖三"),
    "incarnation":    ("道成肉身",     "降生成人"),
    "eucharist":      ("聖餐",         "聖體聖事"),
    "baptism":        ("洗禮",         "聖洗聖事"),
    "communion":      ("交通",         "共融"),
    "salvation":      ("救恩",         "救援"),
    "grace":          ("恩典",         "聖寵"),
    "providence":     ("護理",         "照顧"),
    "spirit":         ("聖靈",         "聖神"),
    "holy spirit":    ("聖靈",         "聖神"),
}


def fetch(url: str) -> list[dict]:
    r = requests.get(url, headers=H_GET, timeout=30)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    # ── Persons ──
    persons = fetch(f"{URL}/rest/v1/theologians?select=id,name_english,name_protestant,name_catholic_sgs,name_recommended")
    p_updates = []
    for p in persons:
        key = (p.get("name_english") or "").lower().strip()
        dual = PERSON_DUAL.get(key)
        if not dual:
            continue
        prot, cath = dual
        patch = {}
        if not p.get("name_protestant"):
            patch["name_protestant"] = prot
        if not p.get("name_catholic_sgs"):
            patch["name_catholic_sgs"] = cath
        if patch:
            p_updates.append((p["id"], p["name_english"], patch))

    # ── Terms / places / sects ──
    terms = fetch(f"{URL}/rest/v1/theological_terms?select=id,term_english,entity_type,zh_protestant,zh_catholic_sgs,zh_recommended")
    t_updates = []
    for t in terms:
        key = (t.get("term_english") or "").lower().strip()
        etype = t.get("entity_type") or "term"
        dual = None
        if etype == "place":  dual = PLACE_DUAL.get(key)
        elif etype == "sect": dual = SECT_DUAL.get(key)
        elif etype == "work": dual = WORK_DUAL.get(key)
        else:                 dual = TERM_DUAL.get(key)
        if not dual:
            continue
        prot, cath = dual
        patch = {}
        if not t.get("zh_protestant"):
            patch["zh_protestant"] = prot
        if not t.get("zh_catholic_sgs"):
            patch["zh_catholic_sgs"] = cath
        if patch:
            t_updates.append((t["id"], t["term_english"], patch))

    print(f"Person updates: {len(p_updates)}")
    for _, en, patch in p_updates[:10]:
        print(f"  {en[:40]:40s} → {patch}")
    if len(p_updates) > 10:
        print(f"  ... +{len(p_updates)-10} more")
    print(f"\nTerm/Place/Sect updates: {len(t_updates)}")
    for _, en, patch in t_updates[:10]:
        print(f"  {en[:40]:40s} → {patch}")
    if len(t_updates) > 10:
        print(f"  ... +{len(t_updates)-10} more")

    if args.dry_run:
        print("\n(dry-run; not writing)")
        return

    for pid, _, patch in p_updates:
        requests.patch(f"{URL}/rest/v1/theologians?id=eq.{pid}",
                       headers=H_JSON, json=patch, timeout=30)
    for tid, _, patch in t_updates:
        requests.patch(f"{URL}/rest/v1/theological_terms?id=eq.{tid}",
                       headers=H_JSON, json=patch, timeout=30)
    print(f"\n✓ patched {len(p_updates)} persons + {len(t_updates)} terms")


if __name__ == "__main__":
    main()
