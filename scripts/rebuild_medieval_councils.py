"""
Scrape medieval ecumenical councils (8-18) decrees to markdown txt files.

Sources:
  - papalencyclicals.net /councils/ecumNN.htm pattern (NN=08-18)
  - Exception: Lateran IV uses ecum12-2.htm

Output: data/creeds/ecumenical-councils/medieval/medieval-NN-{lang}.txt
  - NN: zero-padded council number 08-18
  - {lang}: english (only — Latin + Chinese as placeholders)

Run from project root:
  python -X utf8 scripts/rebuild_medieval_councils.py
"""
import os
import re
import time
from bs4 import BeautifulSoup, Tag
import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT_DIR = os.path.join(ROOT, "data", "creeds", "ecumenical-councils", "medieval")

# (council_num, url_filename, short_slug_for_metadata)
COUNCILS = [
    (8,  "ecum08",   "constantinople-iv"),
    (9,  "ecum09",   "lateran-i"),
    (10, "ecum10",   "lateran-ii"),
    (11, "ecum11",   "lateran-iii"),
    (12, "ecum12-2", "lateran-iv"),
    (13, "ecum13",   "lyon-i"),
    (14, "ecum14",   "lyon-ii"),
    (15, "ecum15",   "vienne"),
    (16, "ecum16",   "constance"),
    (17, "ecum17",   "basel-ferrara-florence"),
    (18, "ecum18",   "lateran-v"),
]

BASE = "https://www.papalencyclicals.net/councils"


def fetch_html(url: str) -> str | None:
    try:
        r = requests.get(
            url,
            timeout=60,
            headers={"User-Agent": "Mozilla/5.0 know-graph-lab/1.0 (creeds/medieval)"},
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except requests.RequestException as e:
        print(f"  ! fetch error: {e}")
        return None


def _normalize_for_subset(s: str) -> str:
    s = re.sub(r"[^\w\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


HEADING_START = re.compile(
    r"^(SESSION|CHAPTER|CANON|DECREE|CONSTITUTION|BULL|ON\s+THE|THE\s+SACRED|"
    r"INTRODUCTION|PROOEMIUM|PREFACE|PROFESSION|"
    r"\d+\s*[\.\)]\s+)",
    re.IGNORECASE,
)


def parse_council_page(html: str) -> str:
    """
    papalencyclicals.net medieval council pages — same general structure as Trent:
      - <h1>/<h2>/<h3> headings
      - <p>/<li> body
      - footer noise to truncate
    """
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body") or soup
    for tag in body.find_all(["script", "style"]):
        tag.decompose()

    blocks: list[tuple[str, str]] = []
    prev_para_norm = ""

    for el in body.find_all(["h1", "h2", "h3", "h4", "h5", "p", "li"]):
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        text = re.sub(r"\s+", " ", text).strip()

        low = text.lower()
        if low.startswith("return to") or low.startswith("back to"):
            continue
        if "papalencyclicals" in low and len(text) < 80:
            continue
        if low.startswith(("copyright", "all rights", "last updated", "©")):
            continue

        is_heading = (
            el.name in ("h1", "h2", "h3", "h4", "h5")
            or (text.isupper() and 4 < len(text) < 120)
            or (HEADING_START.match(text) and len(text) < 200)
        )

        if not is_heading and el.name in ("p", "li"):
            strong_tags = el.find_all(["strong", "b"])
            if strong_tags:
                inside = " ".join(s.get_text(" ", strip=True) for s in strong_tags)
                if inside and inside.replace(" ", "") == text.replace(" ", ""):
                    is_heading = True

        if not is_heading:
            norm = _normalize_for_subset(text)
            if norm and prev_para_norm and norm in prev_para_norm:
                continue
            prev_para_norm = norm
        else:
            prev_para_norm = ""

        blocks.append(("heading" if is_heading else "para", text))

    # Truncate at footer markers
    cutoff = None
    for i, (kind, text) in enumerate(blocks):
        low = text.lower()
        if "want to be automatically notified" in low or "for more information about this site" in low:
            cutoff = i
            break
    if cutoff is not None:
        blocks = blocks[:cutoff]

    lines: list[str] = []
    for kind, text in blocks:
        if kind == "heading":
            lines.append("")
            lines.append(f"## {text}")
            lines.append("")
        else:
            lines.append(text)
            lines.append("")
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).rstrip() + "\n"


CHINESE_PLACEHOLDER_TMPL = """（第 {n} 次大公會議「{name}」 ({year}) 中文版 ─ 尚未取得）

── 來源說明 ──

vatican.va 對中世紀大公會議（councils 8-18，869-1517）無中文官方版。
線上 2026-05-22 全網搜尋確認無公開全文中譯本。

唯一權威全文中譯：

  《公教會之信仰與倫理教義選集》
  原書：Denzinger-Hünermann《Enchiridion Symbolorum》(DH)
  出版：光啟文化事業（台灣）2013-02-01
  譯者：輔仁神學著作編譯會
  ISBN：9789575467418
  規格：拉中對照、2350 頁、精裝、NT$2,950
  購買：校園書房 https://shop.campus.org.tw/ProductDetails.aspx?productID=000580489

中世紀大公會議散落於 DH 600-1450 範圍。取得後手抄／OCR 後覆蓋本檔。
"""

LATIN_PLACEHOLDER_TMPL = """（第 {n} 次大公會議「{name}」 ({year}) 拉丁版 ─ 尚未取得）

候選來源：
  - documentacatholicaomnia.eu (Latin)
  - Wikisource la (Latin)
  - intratext.com Latin corpus
取得後請手動覆蓋本檔。
"""


def main() -> None:
    os.makedirs(TXT_DIR, exist_ok=True)
    summary: list[tuple[int, str, int]] = []

    for cn, url_slug, short in COUNCILS:
        url = f"{BASE}/{url_slug}.htm"
        print(f"[council {cn:02d}] {url}")
        html = fetch_html(url)
        if html is None:
            print(f"  ✗ 404 — skipping")
            summary.append((cn, "404", 0))
            continue
        md = parse_council_page(html)
        out_path = os.path.join(TXT_DIR, f"medieval-{cn:02d}-english.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"  ✓ wrote {os.path.basename(out_path)} ({len(md):,} chars)")
        summary.append((cn, "ok", len(md)))
        time.sleep(0.3)

        # Placeholders
        zh_path = os.path.join(TXT_DIR, f"medieval-{cn:02d}-chinese.txt")
        la_path = os.path.join(TXT_DIR, f"medieval-{cn:02d}-latin.txt")
        # Use short slug as name hint until generator overwrites
        if not os.path.exists(zh_path):
            with open(zh_path, "w", encoding="utf-8") as f:
                f.write(CHINESE_PLACEHOLDER_TMPL.format(n=cn, name=short, year=""))
        if not os.path.exists(la_path):
            with open(la_path, "w", encoding="utf-8") as f:
                f.write(LATIN_PLACEHOLDER_TMPL.format(n=cn, name=short, year=""))

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for cn, status, sz in summary:
        mark = "✓" if status == "ok" else "✗"
        print(f"  {mark} Council {cn:02d}: {status:6} {sz:>8,} chars")
    ok_count = sum(1 for _, s, _ in summary if s == "ok")
    print(f"\nTotal: {ok_count}/{len(COUNCILS)} councils scraped")


if __name__ == "__main__":
    main()
