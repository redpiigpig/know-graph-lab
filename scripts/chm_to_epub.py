"""CHM → EPUB 的 fallback：calibre 直轉失敗時改走這裡。

calibre 的 chm_input 拿「CHM 宣告的那一個 codec」去解全部檔案，遇到下面兩種
CHM 必爆（`UnicodeDecodeError: 'gbk' codec can't decode byte 0xaf ...`）：

  * 一個 CHM 裡同時放 `big5/` 與 `gb/` 兩份同一本書（《神護理的奧秘》）
  * 整本都沒宣告 charset 的編號 htm（《馬丁路德文集》24 檔、《巴文克》28 檔）

作法是自己用 calibre 的 CHMReader 解開（把它逐檔重編碼那步短路掉），判編碼、
轉 UTF-8，再交回 calibre 出 epub。

🚨 編碼不可以用「解得開就算」判。big5hkscs 能把 GBK 位元組解成一堆罕用字而
   完全不報錯 —— 巴文克那本這樣產出過 443,887 字、1.3 MB 的漂亮 epub，
   內容全是 `誘燴 菴坋媼梒` 這種亂碼。這裡改用常用字密度：真中文 ≥0.08 落在
   最常用字表，亂碼 <0.01。
🚨 進入點不可以只挑一個檔。沒有目次的 CHM，calibre 從單一檔只跟得到有連結的
   那幾篇 —— 馬丁路德那本 24 個正文檔只出了 2 篇、11,867 字（真值 59 萬字）。
   這裡自己生一份涵蓋全部正文檔的目次當進入點。

簡體來源一律轉繁（全站中文一律繁體），用既有的
`parse_drive_inventory.to_traditional`（opencc s2tw + TRAD_FIXES），不另造一套。
🚨 只在偵測到簡體專有字時才轉 —— 對本來就是繁體的檔跑轉換會動到「祢」這類異體字。
   判準用 `accs_audit_quality.simplified_chars`（白名單，不是 OpenCC 轉換後比對）。
"""
from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from accs_audit_quality import simplified_chars
from parse_drive_inventory import to_traditional

CALIBRE = r"C:/Program Files/Calibre2"
TRAD_DIRS = ("big5", "cht", "trad", "b5")
CODECS = ("utf-8", "big5", "cp950", "big5hkscs", "gbk", "gb18030")
GOOD_ENOUGH = 0.15          # 常用字密度到這裡就不必再試別的 codec
NAV_HINT = re.compile(r"(fram|toc|contents|index|cover|readme)", re.I)

# 繁簡都收：真中文兩邊都會大量命中，亂碼兩邊都近乎零。
COMMON = set(
    "的一是不了在人有我他這中大來上個國到說們為子和你地出道也時年得就那要下以"
    "生會自著去之過家學對可她裡後小心多天而能好都然沒日於起還發成事只作當想看"
    "文無開手十用主行方又如前所本見經頭面公同三已老從動兩長知民樣意最但現實加"
    "法因此其神我們上帝基督教會信仰聖經耶穌愛世界生命"
    "这里为们说国会学对时现实经头动样发过家还开无当从两长将给应"
)


def _score(text: str) -> float:
    cjk = [c for c in text if "\u4e00" <= c <= "\u9fff"]
    return sum(1 for c in cjk if c in COMMON) / len(cjk) if cjk else 0.0


def _materialise_refs(text: str) -> str:
    """把非 ASCII 的數值字元參照（&#25991; / &#x6587;）還原成真字元。

    🚨 沒有這一步，「整檔純 ASCII、中文全存成實體」的 htm 會被當成沒有中文。
       馬丁路德文集的 14.htm（134,536 B，MSHTML 產的）就是這樣：簡體偵測看不到
       任何漢字 → 跳過簡轉繁 → calibre 事後把實體還原成簡體，1,978 處寫進 epub。
       只還原 cp > 127 的，`&lt;`／`&gt;`／`&amp;` 不動，不會弄壞標記。
    """
    def sub(m):
        cp = int(m.group(1) or m.group(2), 16 if m.group(2) else 10)
        return chr(cp) if cp > 127 else m.group(0)
    return re.sub(r"&#(?:(\d+)|[xX]([0-9a-fA-F]+));", sub, text)


def _decode_best(raw: bytes) -> str:
    """挑常用字密度最高的 codec，不是挑「第一個不報錯的」。"""
    order = list(CODECS)
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:3000], re.I)
    if m:
        order.insert(0, m.group(1).decode("ascii", "replace").lower())
    best, best_s = None, -1.0
    for codec in order:
        try:
            text = raw.decode(codec)
        except (UnicodeDecodeError, LookupError):
            continue
        s = _score(text)
        if s > best_s:
            best, best_s = text, s
        if s >= GOOD_ENOUGH:
            break
    best = best if best is not None else raw.decode("big5", "replace")
    return _materialise_refs(best)


def _extract(src: str, out: str) -> None:
    """用 calibre 自帶的 CHMReader 解壓，但短路掉它逐檔重編碼那步。"""
    os.makedirs(out, exist_ok=True)
    script = os.path.join(out, "_extract.py")
    with open(script, "w", encoding="utf-8") as fh:
        fh.write(
            "import sys\n"
            "from calibre.utils.logging import default_log\n"
            "from calibre.ebooks.chm.reader import CHMReader\n"
            "CHMReader._reformat = lambda self, data, htmlpath: data\n"
            "CHMReader(sys.argv[-2], default_log, input_encoding=None)"
            ".extract_content(sys.argv[-1], debug_dump=False)\n")
    subprocess.run([os.path.join(CALIBRE, "calibre-debug.exe"), "-e", script, src, out],
                   check=True, capture_output=True, timeout=600)
    os.remove(script)


def _pick_tree(root: str) -> str:
    """同一本書有 big5/ 與 gb/ 兩份時取繁體（全站中文一律繁體）。"""
    for want in TRAD_DIRS:
        for d in os.listdir(root):
            if d.lower() == want and os.path.isdir(os.path.join(root, d)):
                return os.path.join(root, d)
    return root


def _natkey(path: str):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", os.path.basename(path))]


def _build_index(tree: str) -> tuple[str, int, int]:
    """逐檔轉 UTF-8＋簡轉繁，生目次，回傳 (進入點, 篇數, 轉繁檔數)。"""
    files = sorted(glob.glob(os.path.join(tree, "**", "*.htm*"), recursive=True),
                   key=_natkey)
    converted = 0
    for path in files:
        with open(path, "rb") as fh:
            text = _decode_best(fh.read())
        if simplified_chars(text):
            text = to_traditional(text)
            converted += 1
        text = re.sub(r"<meta[^>]*charset=[^>]*>", "", text, flags=re.I)
        if re.search(r"<head[^>]*>", text, re.I):
            text = re.sub(r"(<head[^>]*>)", r'\1<meta charset="utf-8">',
                          text, count=1, flags=re.I)
        else:
            text = f'<html><head><meta charset="utf-8"></head><body>{text}</body></html>'
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    # 導覽檔（frameset／目次／封面）只有在夠大時才當正文收
    content = [p for p in files
               if not NAV_HINT.search(os.path.splitext(os.path.basename(p))[0])
               or os.path.getsize(p) > 6000] or files

    links = []
    for path in content:
        rel = os.path.relpath(path, tree).replace(os.sep, "/")
        with open(path, encoding="utf-8") as fh:
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fh.read())).strip()
        links.append(f'<p><a href="{rel}">{plain[:40] or rel}</a></p>')

    index = os.path.join(tree, "_kgl_index.html")
    with open(index, "w", encoding="utf-8") as fh:
        fh.write('<html><head><meta charset="utf-8"><title>目次</title></head>'
                 f'<body>{"".join(links)}</body></html>')
    return index, len(content), converted


def convert(src_chm: str, dst_epub: str, title: str = "") -> tuple[int, int]:
    """轉一本。回傳 (正文篇數, 簡轉繁檔數)；失敗丟例外。"""
    work = tempfile.mkdtemp(prefix="chm2epub_")
    try:
        _extract(src_chm, work)
        tree = _pick_tree(work)
        index, n, conv = _build_index(tree)
        argv = [os.path.join(CALIBRE, "ebook-convert.exe"), index, dst_epub,
                "--input-encoding", "utf-8", "--breadth-first"]
        if title:
            argv += ["--title", title]
        p = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        if p.returncode != 0 or not os.path.exists(dst_epub):
            raise RuntimeError(((p.stdout or "") + (p.stderr or ""))[-400:])
        return n, conv
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    n, conv = convert(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    print(f"✓ {n} 篇　簡轉繁 {conv} 檔　{os.path.getsize(sys.argv[2]) / 1024:.0f} KB")
