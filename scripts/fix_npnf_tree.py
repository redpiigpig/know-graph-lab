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
    # Vol 16 NPNF1-05 — Augustine anti-Pelagian writings
    "df789501-5620-4833-a0a0-6e8f1a031bb1": {
        "A Treatise on the Merits and Forgiveness of Sins, and on the Baptism of Infants.": "論罪的功過與赦免及嬰兒的洗禮",
        "A Treatise on the Spirit and the Letter.": "論聖靈與字句",
        "A Treatise on Nature and Grace.": "論自然與恩典",
        "A Treatise Concerning Man’s Perfection in Righteousness.": "論人在義中的完全",
        "A Treatise Concerning Man's Perfection in Righteousness.": "論人在義中的完全",
        "A Work on the Proceedings of Pelagius.": "論伯拉糾案的審理",
        "A Treatise on the Grace of Christ, and on Original Sin.": "論基督的恩典與原罪",
        "On Marriage and Concupiscence.": "論婚姻與情慾",
        "A Treatise on the Soul and its Origin.": "論靈魂及其起源",
        "A Treatise Against Two Letters of the Pelagians.": "駁伯拉糾派的兩封書信",
        "A Treatise on Grace and Free Will.": "論恩典與自由意志",
        "A Treatise on Rebuke and Grace.": "論責備與恩典",
        "A Treatise on the Predestination of the Saints.": "論聖徒的預定",
        "Introductory Essay on Augustin and the Pelagian Controversy.": "__FRONT__",
        "About This Book": "__FRONT__", "Title Page.": "__FRONT__", "Credits.": "__FRONT__",
        "Contents": "__FRONT__", "Preface to the American Edition.": "__FRONT__",
        "Dedication of Volume I. Of the Edinburgh Edition.": "__FRONT__",
        "Dedication of Volume II. Of the Edinburgh Edition.": "__FRONT__",
        "Preface to Volume I. Of the Edinburgh Edition.": "__FRONT__",
        "Preface to Volume II. Of the Edinburgh Edition.": "__FRONT__",
        "Index of Subjects": "__INDEX__", "Indexes": "__INDEX__",
    },
    # Vol 17 NPNF1-06 — Augustine: Sermon on the Mount, Harmony of Gospels, NT Sermons
    "7bff8a13-3c35-43d4-9b4c-b7c3c9f81076": {
        "Our Lord’s Sermon on the Mount.": "主的登山寶訓",
        "Our Lord's Sermon on the Mount.": "主的登山寶訓",
        "The Harmony of the Gospels.": "四福音合參",
        "Sermons on Selected Lessons of the New Testament.": "新約經課選講",
        "About This Book": "__FRONT__", "Title Page.": "__FRONT__", "Contents": "__FRONT__",
        "Preface.": "__FRONT__", "Introductory Essay. St. Augustin as an Exegete.": "__FRONT__",
        "Indexes of Subjects": "__INDEX__", "Indexes": "__INDEX__",
    },
    # Vol 18 NPNF1-07 — Augustine: Tractates on John, Homilies on 1 John, Soliloquies
    "0069932a-7b27-4c06-9874-b74d51ad564e": {
        "Lectures or Tractates on the Gospel According to St. John.": "約翰福音講道集",
        "Ten Homilies on the First Epistle of John.": "約翰一書十講道",
        "Two Books of Soliloquies.": "獨語錄",
        "About This Book": "__FRONT__", "Title Page.": "__FRONT__", "Preface.": "__FRONT__",
        "Indexes": "__INDEX__",
    },
    # Vol 19 NPNF1-08 — Augustine: Expositions on the Book of Psalms
    "2accee20-5f9d-4099-9ce9-3dda0726a74b": {
        "Expositions on the Book of Psalms.": "詩篇講解",
        "About This Book": "__FRONT__", "Title Page.": "__FRONT__",
        "Index of Subjects": "__INDEX__", "Indexes": "__INDEX__",
    },
    # Vol 20 NPNF1-09 — Chrysostom (金口若望): On the Priesthood + ascetic treatises/homilies/letters
    "76df31fe-e732-4aa6-88c2-d650a09fb688": {
        "Treatise Concerning the Christian Priesthood.": "論司祭職",
        "An Exhortation to Theodore After His Fall.": "勸勉墮落後的狄奧多若",
        "Letter to a Young Widow.": "致年輕寡婦書",
        "Homilies on S. Ignatius and S. Babylas.": "論聖依納爵與聖巴比拉講道",
        "Homily Concerning Lowliness of Mind.": "論心靈謙卑講道",
        "Instructions to Catechumens.": "慕道者教理講授",
        "Three Homilies Concerning the Power of Demons.": "論魔鬼的權勢三講",
        "Homily on the Passage (Matt. xxvi. 19), 'Father If It Be Possible Let This Cup Pass from Me,' Etc., and Against Marcionists and Manichæans.": "論「父啊，倘若可行，求祢叫這杯離開我」並駁馬吉安派與摩尼派講道",
        "Homily on the Paralytic Let Down Through the Roof: and Concerning the Equality of the Divine Father and the Son.": "論從屋頂縋下的癱子並論聖父聖子同等講道",
        "Homily to Those Who Had Not Attended the Assembly: and on the Apostolic Saying, 'If Thine Enemy Hunger, Feed Him, Etc. (Rom. xii. 20), and Concerning Resentment of Injuries.'": "致未赴聚會者並論「仇敵若餓了就給他吃」並論寬恕傷害講道",
        "Homily Against Publishing the Errors of the Brethren, and Uttering Imprecations upon Enemies.": "駁宣揚弟兄過錯與咒詛仇敵講道",
        "Two Homilies on Eutropius.": "論歐特羅皮烏斯二講",
        "A Treatise to Prove that No One Can Harm the Man Who Does Not Injure Himself.": "論無人能傷害不自害之人",
        "Letters of St. Chrysostom to Olympias.": "致奧林匹亞書信集",
        "Correspondence of St. Chrysostom with the Bishop of Rome.": "與羅馬主教的通信",
        "The Homilies on the Statues to the People of Antioch.": "致安提阿人論雕像講道集",
        "About This Book": "__FRONT__", "Title Page.": "__FRONT__", "Preface.": "__FRONT__",
        "Prolegomena.": "__FRONT__",
        "Indexes of Subjects": "__INDEX__", "Indexes": "__INDEX__",
    },
    # Vol 21 NPNF1-10 — Chrysostom (金口若望): Homilies on the Gospel of Matthew
    "0d160c29-8d61-4dbc-8f8e-d47fee694eab": {
        "The Homilies of St. John Chrysostom.": "馬太福音講道集",
        "About This Book": "__FRONT__", "Title Page.": "__FRONT__",
        "Preface to the American Edition.": "__FRONT__",
        "Index of Subjects": "__INDEX__", "Indexes": "__INDEX__",
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
