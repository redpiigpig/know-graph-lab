"""
下載 Schaff 編 38 卷教父集 EPUB 到 z-lib/
- Ante-Nicene Fathers (ANF) 10 卷
- Nicene and Post-Nicene Fathers Series 1 (NPNF1) 14 卷
- Nicene and Post-Nicene Fathers Series 2 (NPNF2) 14 卷

公版，CCEL 提供預製 EPUB。下完後由 ingest_new_books.py 自動歸位 + 分類。

執行：python scripts/_download_schaff.py
"""
import sys
from pathlib import Path
import urllib.request
import time

sys.stdout.reconfigure(encoding="utf-8")

# (CCEL slug, 作者, 標題)
VOLUMES = [
    # Ante-Nicene Fathers
    ("anf01", "Apostolic Fathers", "Apostolic Fathers with Justin Martyr and Irenaeus (ANF Vol 1)"),
    ("anf02", "Clement of Alexandria", "Fathers of the Second Century - Hermas, Tatian, Athenagoras, Theophilus, Clement (ANF Vol 2)"),
    ("anf03", "Tertullian", "Latin Christianity - Tertullian Apologetic and Anti-Marcion (ANF Vol 3)"),
    ("anf04", "Tertullian", "Tertullian IV, Minucius Felix, Commodian, Origen (ANF Vol 4)"),
    ("anf05", "Hippolytus", "Hippolytus, Cyprian, Caius, Novatian (ANF Vol 5)"),
    ("anf06", "Gregory Thaumaturgus", "Gregory Thaumaturgus, Dionysius the Great, Julius Africanus, Anatolius (ANF Vol 6)"),
    ("anf07", "Lactantius", "Lactantius, Venantius, Asterius, Methodius, Arnobius (ANF Vol 7)"),
    ("anf08", "Apostolic Constitutions", "Twelve Patriarchs, Excerpts and Epistles, Apostolic Constitutions, Homilies (ANF Vol 8)"),
    ("anf09", "Roberts and Donaldson", "Gospel of Peter, Diatessaron, Apocalypses, Visio Pauli, Apocryphal Acts (ANF Vol 9)"),
    ("anf10", "Roberts and Donaldson", "Bibliography, General Index (ANF Vol 10)"),
    # NPNF Series 1
    ("npnf101", "Augustine", "Augustine - Confessions and Letters (NPNF1 Vol 1)"),
    ("npnf102", "Augustine", "Augustine - City of God and Christian Doctrine (NPNF1 Vol 2)"),
    ("npnf103", "Augustine", "Augustine - On the Holy Trinity, Doctrinal Treatises (NPNF1 Vol 3)"),
    ("npnf104", "Augustine", "Augustine - Anti-Manichaean and Anti-Donatist Writings (NPNF1 Vol 4)"),
    ("npnf105", "Augustine", "Augustine - Anti-Pelagian Writings (NPNF1 Vol 5)"),
    ("npnf106", "Augustine", "Augustine - Sermon on the Mount, Harmony of the Gospels (NPNF1 Vol 6)"),
    ("npnf107", "Augustine", "Augustine - Homilies on the Gospel of John, First Epistle of John, Soliloquies (NPNF1 Vol 7)"),
    ("npnf108", "Augustine", "Augustine - Expositions on the Book of Psalms (NPNF1 Vol 8)"),
    ("npnf109", "Chrysostom", "Chrysostom - On the Priesthood, Ascetic Treatises, Select Homilies, Homilies on the Statues (NPNF1 Vol 9)"),
    ("npnf110", "Chrysostom", "Chrysostom - Homilies on the Gospel of Matthew (NPNF1 Vol 10)"),
    ("npnf111", "Chrysostom", "Chrysostom - Homilies on the Acts of the Apostles and Romans (NPNF1 Vol 11)"),
    ("npnf112", "Chrysostom", "Chrysostom - Homilies on First and Second Corinthians (NPNF1 Vol 12)"),
    ("npnf113", "Chrysostom", "Chrysostom - Homilies on Galatians, Ephesians, Philippians, Colossians, Thessalonians, Timothy, Titus, Philemon (NPNF1 Vol 13)"),
    ("npnf114", "Chrysostom", "Chrysostom - Homilies on the Gospel of John and Hebrews (NPNF1 Vol 14)"),
    # NPNF Series 2
    ("npnf201", "Eusebius", "Eusebius - Church History, Life of Constantine, Oration in Praise of Constantine (NPNF2 Vol 1)"),
    ("npnf202", "Socrates Scholasticus", "Socrates and Sozomenus - Ecclesiastical Histories (NPNF2 Vol 2)"),
    ("npnf203", "Theodoret", "Theodoret, Jerome, Gennadius, Rufinus - Historical Writings (NPNF2 Vol 3)"),
    ("npnf204", "Athanasius", "Athanasius - Select Works and Letters (NPNF2 Vol 4)"),
    ("npnf205", "Gregory of Nyssa", "Gregory of Nyssa - Dogmatic Treatises and Select Writings (NPNF2 Vol 5)"),
    ("npnf206", "Jerome", "Jerome - Letters and Select Works (NPNF2 Vol 6)"),
    ("npnf207", "Cyril of Jerusalem", "Cyril of Jerusalem, Gregory Nazianzen - Select Writings (NPNF2 Vol 7)"),
    ("npnf208", "Basil", "Basil - Letters and Select Works (NPNF2 Vol 8)"),
    ("npnf209", "Hilary of Poitiers", "Hilary of Poitiers, John of Damascus - Select Works (NPNF2 Vol 9)"),
    ("npnf210", "Ambrose", "Ambrose - Select Works and Letters (NPNF2 Vol 10)"),
    ("npnf211", "Sulpitius Severus", "Sulpitius Severus, Vincent of Lerins, John Cassian (NPNF2 Vol 11)"),
    ("npnf212", "Leo the Great", "Leo the Great, Gregory the Great - Select Works (NPNF2 Vol 12)"),
    ("npnf213", "Gregory the Great", "Gregory the Great Part II, Ephraim Syrus, Aphrahat (NPNF2 Vol 13)"),
    ("npnf214", "Schaff", "The Seven Ecumenical Councils (NPNF2 Vol 14)"),
]


def sanitize_filename(s: str) -> str:
    """Strip Windows-banned chars from a filename component (NOT the comma — the project uses 「，」 as separator)."""
    for c in '<>:"/\\|?*':
        s = s.replace(c, "")
    return s.strip()


def main():
    out_dir = Path(__file__).resolve().parent.parent / "z-lib"
    out_dir.mkdir(exist_ok=True)
    print(f"Target dir: {out_dir}")
    print(f"Volumes to download: {len(VOLUMES)}")
    print()

    ok, fail, skip = 0, 0, 0
    for i, (slug, author, title) in enumerate(VOLUMES, 1):
        url = f"https://ccel.org/ccel/s/schaff/{slug}/cache/{slug}.epub"
        # 用「，」全形逗號當 separator (parse_drive_inventory 認得)
        fname = f"{sanitize_filename(author)}，{sanitize_filename(title)}.epub"
        target = out_dir / fname

        if target.exists() and target.stat().st_size > 100_000:
            print(f"  [{i:2d}/{len(VOLUMES)}] SKIP (exists, {target.stat().st_size//1024} KB)  {fname[:80]}")
            skip += 1
            continue

        try:
            print(f"  [{i:2d}/{len(VOLUMES)}] {slug} → {fname[:80]}", flush=True)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (kglab-ingest)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            target.write_bytes(data)
            size_kb = len(data) // 1024
            print(f"    ✓ {size_kb} KB")
            ok += 1
            time.sleep(0.5)  # be gentle to CCEL
        except Exception as e:
            print(f"    ❌ {e}")
            fail += 1

    print()
    print(f"=== Done: ok={ok}, fail={fail}, skip={skip} ===")


if __name__ == "__main__":
    main()
