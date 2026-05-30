"""General NPNF volume assigner via NCX tree (depth1=work, depth2=book/chapter).

consolidate_by_ncx flattens deeply-nested works (City of God's 22 books become
470 chapter-volumes). This walks the NCX tree, maps every content src file to
its (work, book) ancestors, and assigns:
  volume        = "<zhWork> 卷N"   (multi-book works)  |  "<zhWork>"  (flat works)
  parent_volume = "<zhWork>"       (multi-book)        |  category   (front/index)
Then consolidate_letters merges chapters into pages.

Per-volume input = WORK_ZH (en depth-1 label → zh) in REGISTRY below.
A depth-2 navPoint counts as a "book" iff it has child navPoints; childless
depth-2 (prefaces) fold to work front. Books are numbered by document order.

Usage: python scripts/_fix_npnf_tree.py <ebook_id> [--dry-run]
"""
from __future__ import annotations
import argparse, json, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env"); sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se

URL = os.environ["SUPABASE_URL"]; KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}
CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:\我的雲端硬碟\資料\電子書\_chunks")

ROMAN_ARABIC = {}
def _cn(n: int) -> str:
    units = "零一二三四五六七八九"
    if n <= 10: return units[n] if n < 10 else "十"
    if n < 20: return "十" + (units[n-10] if n>10 else "")
    if n < 100:
        t, o = divmod(n, 10)
        return units[t] + "十" + (units[o] if o else "")
    return str(n)

# en depth-1 work label → zh.  "__FRONT__"/"__INDEX__" route to front/index.
REGISTRY: dict[str, dict[str, str]] = {
    # Vol 13 NPNF1-02
    "1eb50be9-34ac-4ce3-874d-1280975851fc": {
        "City of God": "上帝之城",
        "On Christian Doctrine": "論基督教教義",
        "Title Page": "__FRONT__", "Table of Contents": "__FRONT__",
        "Editor’s Preface": "__FRONT__", "Editor's Preface": "__FRONT__",
        "Subject Index": "__INDEX__", "Indexes": "__INDEX__",
    },
    # Vol 14 NPNF1-03
    "d7f66759-3fa9-4633-abde-87003cdbcc06": {
        "Doctrinal Treatises of St. Augustin": "奧古斯丁教義論集",
        "Moral Treatises of St. Augustin": "奧古斯丁道德論集",
        "Title Page": "__FRONT__", "Preface": "__FRONT__", "Contents": "__FRONT__",
        "Subject Indexes": "__INDEX__", "Indexes": "__INDEX__",
    },
    # Vol 15 NPNF1-04
    "56ef3d65-c559-41f8-8d68-ba6c13e47876": {
        "Writings in Connection with the Manichæan Controversy.": "駁摩尼派論集",
        "Writings in Connection with the Donatist Controversy.": "駁多納徒派論集",
        "Title Page": "__FRONT__", "Editor’s Preface.": "__FRONT__",
        "Editor's Preface.": "__FRONT__", "Contents": "__FRONT__",
        "Subject Indexes": "__INDEX__", "Indexes": "__INDEX__",
    },
}


def _base(src: str) -> str:
    return re.sub(r"#.*$", "", src or "").strip().lower()


def find_epub(eid: str) -> Path:
    fp = Path(requests.get(f"{URL}/rest/v1/ebooks?id=eq.{eid}&select=file_path",
                           headers=H_GET).json()[0]["file_path"]).with_suffix(".epub")
    if fp.exists(): return fp
    for f in fp.parent.iterdir():
        if f.suffix.lower() == ".epub": return f
    raise FileNotFoundError(fp)


def parse_tree(epub: Path) -> dict[str, tuple[str, int | None]]:
    """src_basename → (depth1_en_label, book_number_or_None)."""
    with zipfile.ZipFile(epub) as z:
        ncx = z.read(next(n for n in z.namelist() if n.endswith(".ncx"))).decode("utf-8", "replace")
    root = ET.fromstring(re.sub(r'\sxmlns(:\w+)?="[^"]+"', "", ncx))
    out: dict[str, tuple[str, int | None]] = {}
    for d1 in root.find("navMap").findall("navPoint"):
        l1 = (d1.find("navLabel/text").text or "").strip() if d1.find("navLabel/text") is not None else ""
        s1 = _base(d1.find("content").get("src", ""))
        subs = d1.findall("navPoint")
        out.setdefault(s1, (l1, None))
        book_no = 0
        for d2 in subs:
            s2 = _base(d2.find("content").get("src", ""))
            kids = d2.findall("navPoint")
            if kids:                       # depth-2 with children = a book
                book_no += 1
                out[s2] = (l1, book_no)
                for d3 in kids:
                    s3 = _base(d3.find("content").get("src", ""))
                    out.setdefault(s3, (l1, book_no))
                    for d4 in d3.findall("navPoint"):
                        out.setdefault(_base(d4.find("content").get("src", "")), (l1, book_no))
            else:                          # childless depth-2 = chapter/preface
                out.setdefault(s2, (l1, None))
    return out


def main(eid: str, dry_run=False):
    work_zh = REGISTRY.get(eid)
    if not work_zh:
        raise SystemExit(f"no REGISTRY entry for {eid} — add WORK_ZH dict first")
    epub = find_epub(eid)
    tree = parse_tree(epub)
    # which works are multi-book?
    multibook: set[str] = set()
    for (l1, bk) in tree.values():
        if bk: multibook.add(l1)

    src = CHUNKS_DIR / f"{eid}.jsonl"
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]

    per_vol: dict[str, int] = {}
    unmatched = 0
    for r in rows:
        if r["chunk_index"] == 0:
            r["volume"], r["parent_volume"], r["chapter_path"] = "封面", "封面", "封面"
            r["chunk_type"] = "chapter"; continue
        b = _base(r.get("title_en") or "")
        info = tree.get(b)
        if not info:
            # prefix fallback: longest tree key that b starts with
            cand = [(k, v) for k, v in tree.items() if k and b.startswith(k.replace(".html", ""))]
            info = max(cand, key=lambda kv: len(kv[0]))[1] if cand else None
        if not info:
            unmatched += 1
            cp = r.get("chapter_path") or ""
            if "索引" in cp or "Index" in (r.get("title_en") or ""):
                r["volume"], r["parent_volume"] = "索引", "索引"
            else:
                r["volume"], r["parent_volume"] = "前言", "導論"
            v = r["volume"]; n = per_vol.get(v, 0) + 1; per_vol[v] = n
            r["chapter_path"] = f"{v} 第{n}章"
            continue
        l1, bk = info
        zh = work_zh.get(l1, l1)
        if zh == "__FRONT__":
            r["volume"], r["parent_volume"] = "前言", "導論"
        elif zh == "__INDEX__":
            r["volume"], r["parent_volume"] = "索引", "索引"
        elif l1 in multibook and bk:
            vol = f"{zh} 卷{_cn(bk)}"
            r["volume"], r["parent_volume"] = vol, zh
        else:
            r["volume"], r["parent_volume"] = zh, zh
        v = r["volume"]; n = per_vol.get(v, 0) + 1; per_vol[v] = n
        r["chapter_path"] = f"{v} 第{n}章"

    from collections import Counter
    print(f"{eid}  unmatched={unmatched}")
    for v, n in Counter(r.get("volume") for r in rows).items():
        print(f"  {n:4d}  {v}")
    if dry_run:
        print("(dry-run)"); return

    with open(src, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    se.push_to_r2(eid, src)
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}", headers=H_GET, timeout=60)
    ins = [{"ebook_id": eid, "chunk_index": r["chunk_index"], "chunk_type": r.get("chunk_type","chapter"),
            "page_number": r.get("page_number"), "chapter_path": r.get("chapter_path"),
            "content": (r.get("content") or "")[:200], "char_count": len(r.get("content") or "")} for r in rows]
    for i in range(0, len(ins), 25):
        requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON, json=ins[i:i+25], timeout=60)
    print(f"applied + synced ({len(rows)} chunks)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("ebook_id"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); main(a.ebook_id, a.dry_run)
