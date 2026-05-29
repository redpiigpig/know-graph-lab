"""D2 — 同教父作品在目錄相鄰：parent_volume backfill.

Vol 1 之後 consolidate_by_ncx 的 PARENT_CN_FALLBACK 沒覆蓋 Vol 2-9 的教父，
所以 vol 2-9 chunks 大多 parent_volume 為空，reader 沒辦法把同教父的作品
group 在一起。

本腳本走 chunks，依 volume 名稱 substring 推斷 parent_volume：
  - "依納爵..." → "依納爵"
  - "革利免致..." → "羅馬的革利免"（Vol 1 + Vol 9）
  - "革利免《...》" "革利免勸..." → "亞歷山卓的革利免"（Vol 2）
  - … 詳見 PARENT_RULES 表
Anonymous / apocryphal 作品 (Apocalypse / Vision / Acts) parent_volume 留空。

Usage:
    python scripts/backfill_parent_volume.py <EBOOK_ID> [--dry-run]
    python scripts/backfill_parent_volume.py --all [--dry-run]   # 跑全部已精修卷
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

ALL_REFINED = [
    ("Vol 1", "c98d358d-7066-4691-a896-b7232707b0db"),
    ("Vol 2", "4e3d16fc-ef4f-420f-a3ec-56e2e92d659f"),
    ("Vol 3", "364dac2e-410f-4906-be63-8bb86b4865ee"),
    ("Vol 4", "904661d3-16fc-4f37-bb04-f7c4aa7671e9"),
    ("Vol 5", "0e08c662-540b-4186-b250-9bca0cfe1002"),
    ("Vol 6", "dffaae40-e088-41c1-ab7f-9b96f9249661"),
    ("Vol 7", "75d8aae0-7431-4be9-baee-c57d26599653"),
    ("Vol 8", "d09946ab-154b-4a97-853f-751cbb346221"),
    ("Vol 9", "72cb2f94-da86-4e16-bbbd-4cf3391031df"),
]

# Order matters: longer / more-specific patterns first. First match wins.
# Pattern matched against `volume` string with `in` (substring).
PARENT_RULES: list[tuple[str, str]] = [
    # ── Vol 1 — Apostolic Fathers / Justin / Irenaeus ──────────────────
    ("依納爵",            "依納爵"),
    ("瑪利雅致依納爵",     "依納爵"),
    ("童貞女瑪利亞致依納爵","依納爵"),
    # 2026-05-29 譯名決策：羅馬的克勉 (Latin tradition Clemens)
    # vs 亞歷山卓的革利免 (Greek tradition Klēmēs)
    ("克勉致哥林多",       "羅馬的克勉"),
    ("克勉後書",           "羅馬的克勉"),
    ("克勉前書",           "羅馬的克勉"),
    ("克勉書信集",         "羅馬的克勉"),
    # legacy 革利免致... (Roman Clement舊命名) — keep as fallback
    ("革利免致哥林多",     "羅馬的克勉"),
    ("革利免後書",         "羅馬的克勉"),
    ("革利免書信集",       "羅馬的克勉"),
    # Diognetus (Mathetes)
    ("致丟格那妥",         "瑪忒特"),
    # Polycarp
    ("坡旅甲",             "坡旅甲"),
    # Barnabas
    ("巴拿巴",             "巴拿巴"),
    # Papias
    ("帕皮亞",             "帕皮亞"),
    # Justin
    ("猶斯定",             "殉道者猶斯定"),
    ("與特里弗的對話",     "殉道者猶斯定"),
    ("致希臘人辭",         "殉道者猶斯定"),  # Justin's; might clash w/ Tatian's
    ("勸勉希臘人辭",       "殉道者猶斯定"),
    ("論神獨一治理",       "殉道者猶斯定"),
    # Irenaeus
    ("愛任紐",             "里昂的愛任紐"),

    # ── Vol 2 — Second Century ─────────────────────────────────────────
    ("黑馬",               "黑馬"),
    ("他提安",             "他提安"),
    ("提阿非羅",           "提阿非羅"),
    ("雅典那哥拉",         "雅典那哥拉"),
    ("論死者復活",         "雅典那哥拉"),
    # Clement of Alexandria — multiple works (not Roman Clement)
    ("革利免《教師》",     "亞歷山卓的革利免"),
    ("革利免《雜文集》",   "亞歷山卓的革利免"),
    ("革利免《富者得救》", "亞歷山卓的革利免"),
    ("革利免勸勉希臘人",   "亞歷山卓的革利免"),
    ("革利免殘篇",         "亞歷山卓的革利免"),

    # ── Vol 3 / 4 — Tertullian (sectional, not by author) ─────────────
    ("特土良",             "特土良"),
    ("佩爾佩圖亞",         "特土良"),  # Ethical section
    ("佩爾佩圖亞與費莉西塔斯", "特土良"),

    # ── Vol 4 — Origen / Minucius / Commodian + Tertullian Part IV ────
    ("俄利根",             "俄利根"),
    ("密努修",             "密努修‧斐力克斯"),
    ("斐力克斯",           "密努修‧斐力克斯"),
    ("科摩狄安",           "科摩狄安"),

    # ── Vol 5 — Hippolytus / Cyprian / Caius / Novatian ────────────────
    ("希波呂圖",           "希波呂圖"),
    ("居普良",             "居普良"),
    ("該猶",               "該猶"),
    ("諾瓦提安",           "諾瓦提安"),
    ("第七屆迦太基會議",   "居普良"),
    ("論異端洗禮",         "居普良"),  # 附錄
    ("論再洗禮",           "居普良"),
    ("駁諾瓦提安",         "居普良"),
    ("異端洗禮爭論",       "居普良"),

    # ── Vol 6 — many minor Eastern fathers ─────────────────────────────
    ("亞歷山卓的彼得",     "亞歷山卓的彼得"),
    ("亞歷山卓的亞歷山大", "亞歷山卓的亞歷山大"),
    ("亞歷山卓的狄奧尼修", "亞歷山卓的狄奧尼修"),
    ("亞歷山卓的提阿納",   "亞歷山卓的提阿納"),
    ("亞歷山卓的提阿諾斯托","亞歷山卓的提阿諾斯托"),
    ("亞歷山卓的阿那托里", "亞歷山卓的阿那托里"),
    ("亞納托利烏與小作家集","亞納托利烏與小作家集"),
    ("呂科波利的亞歷山大", "呂科波利的亞歷山大"),
    ("卡帕多奇亞的亞歷山大","卡帕多奇亞的亞歷山大"),
    ("格列高利‧塔烏馬圖戈斯","格列高利‧塔烏馬圖戈斯"),
    ("猶略‧阿弗里卡努斯", "猶略‧阿弗里卡努斯"),
    ("阿弗里卡努",         "猶略‧阿弗里卡努斯"),
    ("美多德",             "美多第烏"),
    ("美多第烏",           "美多第烏"),
    ("阿凱勞斯",           "阿凱勞斯"),
    ("阿基老",             "阿凱勞斯"),
    ("Archelaus",          "阿凱勞斯"),
    ("斐勒亞斯",           "斐勒亞斯"),
    ("阿諾比烏",           "阿諾比烏"),  # Arnobius of Sicca (Vol 6 end)
    ("Methodius",          "美多第烏"),  # English残留
    ("阿那托里與其他作家", "亞納托利烏與小作家集"),  # variant naming
    ("朱利亞‧阿弗里卡努", "猶略‧阿弗里卡努斯"),  # variant transliteration

    # ── Vol 7 — Lactantius and others ─────────────────────────────────
    ("拉克坦提烏",         "拉克坦提烏"),
    ("維克多里努",         "維克多里努"),
    ("維南提烏",           "維南提烏"),
    ("烏爾巴努‧阿斯特里", "亞斯特里烏"),
    ("阿斯特里",           "亞斯特里烏"),
    ("十二使徒遺訓",       "(初代禮儀典籍)"),
    ("使徒憲令",           "(初代禮儀典籍)"),
    ("早期禮儀",           "(初代禮儀典籍)"),
    ("尼西亞信經",         "(初代禮儀典籍)"),

    # ── Vol 8 — Apocrypha / Pseudo-Clementine / Apostolic Constitutions ─
    ("十二族長遺訓",       "(舊約偽典)"),
    ("狄奧多托殘篇",       "亞歷山卓的革利免"),  # Excerpta ex Theodoto preserved by Clement of Alex
    ("論貞潔書信二篇",     "羅馬的克勉"),         # attributed to Roman Clement (probably 3c)
    ("偽克勉文集",         "(偽典)"),             # Pseudo-Clementine Recognitions + Homilies
    ("偽革利免文集",       "(偽典)"),             # legacy naming fallback
    ("新約偽典",           "(新約偽典)"),
    ("教令集",             "(教令集)"),
    ("厄德薩史記與其他敘利亞古文獻", "(敘利亞古文獻)"),
    ("二三世紀殘篇",       "(殘篇集)"),

    # ── Vol 9 — Apocrypha (apocryphal works are listed by genre) ───────
    ("塔提安",             "他提安"),
    ("狄阿特撒龍",         "他提安"),  # Diatessaron
    ("亞里斯泰德",         "雅典的亞里斯泰德"),
    # Apocrypha — parent is genre group
    ("彼得福音",           "(新約偽典)"),
    ("彼得啟示錄",         "(新約偽典)"),
    ("保羅異象",           "(新約偽典)"),
    ("童貞女啟示錄",       "(新約偽典)"),
    ("塞德拉克啟示錄",     "(新約偽典)"),
    ("亞伯拉罕遺訓",       "(舊約偽典)"),
    ("散提碧",             "(新約偽典)"),
    ("波利克塞娜",         "(新約偽典)"),
    ("利百加",             "(新約偽典)"),
    ("佐西穆斯",           "(新約偽典)"),
    ("西利人殉道記",       "(殉道記)"),
]


def infer_parent(vol: str) -> str | None:
    """Infer parent_volume from a volume string. None = no inferable parent."""
    if not vol:
        return None
    for pattern, parent in PARENT_RULES:
        if pattern in vol:
            return parent
    return None


def process_book(label: str, ebook_id: str, dry_run: bool):
    src = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not src.exists():
        print(f"  {label}: jsonl not found, skipping")
        return
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    set_count = 0
    unchanged = 0
    no_match = 0
    unmatched_vols: set[str] = set()
    for r in rows:
        vol = r.get("volume")
        if not vol:
            continue
        parent = infer_parent(vol)
        if parent is None:
            no_match += 1
            unmatched_vols.add(vol)
            continue
        if r.get("parent_volume") == parent:
            unchanged += 1
            continue
        r["parent_volume"] = parent
        set_count += 1

    print(f"\n{label} ({ebook_id})")
    print(f"  parent_volume newly set: {set_count}")
    print(f"  unchanged: {unchanged}, no-match: {no_match} ({len(unmatched_vols)} unique unmatched vols)")
    if unmatched_vols and len(unmatched_vols) <= 12:
        for v in sorted(unmatched_vols):
            print(f"    no-match vol: {v}")
    if dry_run or set_count == 0:
        return

    with open(src, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  wrote {src.name} ({src.stat().st_size // 1024} KB)")

    se.push_to_r2(ebook_id, src)
    print(f"  pushed R2")
    # parent_volume isn't in the ebook_chunks preview table — no refresh needed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id", nargs="?", help="single ebook id to process")
    ap.add_argument("--all", action="store_true", help="process all refined vols")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.all:
        for label, ebid in ALL_REFINED:
            process_book(label, ebid, args.dry_run)
    elif args.ebook_id:
        label = next((l for l, e in ALL_REFINED if e == args.ebook_id), "Custom")
        process_book(label, args.ebook_id, args.dry_run)
    else:
        ap.error("specify --all or an ebook_id")


if __name__ == "__main__":
    main()
