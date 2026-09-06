# -*- coding: utf-8 -*-
"""國立國會圖書館デジタルコレクション → 全集卷（ja＋繁中）的取源模組。

無教會譜系裡戰前那批全是公有領域，卻不在青空文庫、也不在 libgen——只有 NDL 的
掃描本。2026-09-06 逐一探過公開範圍，共 **33 部可直接取用**（畔上賢造 16、
矢內原忠雄 9、藤井武 7、內村鑑三 1）；黒崎幸吉、塚本虎二、南原繁三位數位化了
28／35／23 部卻全是館內限定（卒後 70 年未過）。清單見
.claude/skills/ebook-collected-works/ndl_open_scans.md。

**判公開範圍只有一個可靠辦法**：抓 `https://dl.ndl.go.jp/api/iiif/{pid}/manifest.json`，
200＝インターネット公開、404＝館內限定／個人送信。目錄 metadata 不帶這個欄位。
「圖書館‧個人送信」看起來可用，但**居住在日本境外者不能用**，別把它算進來。

兩個 API 分工：
  * `lab.ndl.go.jp/dl/api/book/{pid}`  書誌＋**目次**（分章靠它），偶爾 page=0
  * `dl.ndl.go.jp/api/iiif/{pid}/...`  影像（也是公開範圍的探針）

流程：目次分章 → 逐頁取影像 → Gemini Vision OCR（直排舊字舊假名）→ 段落重建 →
交 uchimura_auto 那套 checkpoint／翻譯／上架。純函式鎖在
scripts/tests/test_ndl_build.py。

  python scripts/ndl_build.py --probe 1099766          # 看書誌與分章
  python scripts/ndl_build.py --fetch 1099766          # 下載影像到快取
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

CACHE_DIR = Path("c:/tmp/ndl_cache")
LAB_API = "https://lab.ndl.go.jp/dl/api/book/{pid}"
IIIF_MANIFEST = "https://dl.ndl.go.jp/api/iiif/{pid}/manifest.json"
IIIF_IMAGE = "https://dl.ndl.go.jp/api/iiif/{pid}/R{img:07d}/full/{size}/0/default.jpg"

# 目次一條的三種寫法：
#   第一　教派ではない/1  (0003.jp2)      章名/印刷頁 (影像)
#   舊新約の二大預言とその成就 / 1 (0006.jp2)
#   充さるべき預言 / (0006.jp2)           無印刷頁
#   標題  (0002.jp2)                      前付（無斜線）
_TOC_RE = re.compile(r"^\s*(?P<title>.*?)\s*(?:/\s*(?P<page>[0-9０-９]*)\s*)?\((?P<img>\d+)\.jp2\)\s*$")

# 前付／後付：不是正文，分章時丟掉
FRONT_MATTER = {"標題", "目次", "奥付", "奧付", "口絵", "口繪", "序", "凡例", "扉"}


def parse_toc_entry(line: str) -> dict | None:
    """NDL 目次的一行 → {title, printed_page, image}；解析不出來回 None。"""
    m = _TOC_RE.match(line or "")
    if not m:
        return None
    title = m.group("title").strip().rstrip("/").strip()
    if not title:
        return None
    return {"title": title, "printed_page": (m.group("page") or "").strip(), "image": int(m.group("img"))}


def sections_from_index(index: list[str], total_images: int, fallback_title: str = "全文") -> list[dict]:
    """目次 → [{title, start, end}]（影像編號，end 為 exclusive）。

    前付（標題／目次／奥付…）丟掉；每一節結束於下一節開始，最後一節到全書末頁。
    目次整個缺席時（NDL 對某些書沒建目次）退回「整本一節」，讓管線仍能跑。"""
    entries = [e for e in (parse_toc_entry(l) for l in index) if e]
    body = [e for e in entries if e["title"] not in FRONT_MATTER]
    if not body:
        return [{"title": fallback_title, "printed_page": "", "start": 1, "end": total_images + 1}]
    out = []
    for i, e in enumerate(body):
        end = body[i + 1]["image"] if i + 1 < len(body) else total_images + 1
        out.append({"title": e["title"], "printed_page": e["printed_page"],
                    "start": e["image"], "end": max(end, e["image"] + 1)})
    return out


def image_url(pid: str, img: int, width: int | None = None) -> str:
    return IIIF_IMAGE.format(pid=pid, img=img, size=f"{width}," if width else "full")


# ── OCR 後處理 ───────────────────────────────────────────────────────────────
# 直排舊書的振り仮名，OCR 常整段括進正文：基督教（キリストけう）は
_RUBY_RE = re.compile(r"[（(][ぁ-んァ-ヶー・]{1,12}[）)]")
# 只有數字（含漢數字與全形）的行＝頁碼
_PAGENUM_RE = re.compile(r"^[\s0-9０-９一二三四五六七八九十百]+$")
_TERMINAL = ("。", "！", "？", "」", "』", "）", "…")


def clean_ocr_text(text: str) -> str:
    """Vision OCR 的一頁文字 → 乾淨段落（以空行分段）。"""
    out = []
    for block in re.split(r"\n\s*\n", text or ""):
        lines = []
        for ln in block.split("\n"):
            s = ln.strip().strip("　").strip()
            if not s or _PAGENUM_RE.match(s):
                continue
            lines.append(_RUBY_RE.sub("", s))
        joined = "".join(lines).strip()
        if joined:
            out.append(joined)
    return "\n\n".join(out)


def paragraphs_from_pages(pages: list[str]) -> list[str]:
    """逐頁文字 → 段落。直排書換頁不換段是常態，所以上一段沒有句末標點就接下去。"""
    paras: list[str] = []
    for page in pages:
        for p in [x for x in re.split(r"\n\s*\n", (page or "").strip()) if x.strip()]:
            p = p.strip()
            if paras and not paras[-1].endswith(_TERMINAL):
                paras[-1] = paras[-1] + p
            else:
                paras.append(p)
    return paras


# ── 網路（非純函式，測試不碰） ────────────────────────────────────────────────
def is_open(pid: str) -> bool:
    """インターネット公開＝IIIF manifest 回 200。館內限定／個人送信回 404。"""
    import requests
    try:
        return requests.get(IIIF_MANIFEST.format(pid=pid), timeout=25).status_code == 200
    except Exception:
        return False


def fetch_book(pid: str) -> dict:
    """書誌＋目次＋頁數。Lab API 的 page 偶爾為 0，那時回頭數 IIIF canvas。"""
    import requests
    d = requests.get(LAB_API.format(pid=pid), timeout=40).json()
    pages = int(d.get("page") or 0)
    if not pages:
        m = requests.get(IIIF_MANIFEST.format(pid=pid), timeout=40).json()
        seq = m.get("sequences") or []
        pages = len(seq[0]["canvases"]) if seq else len(m.get("items", []))
    return {"pid": pid, "title": d.get("title", ""), "author": d.get("responsibility", ""),
            "publisher": d.get("publisher", ""), "year": d.get("published", ""),
            "pages": pages, "index": d.get("index") or []}


def fetch_images(pid: str, start: int, end: int, width: int = 1800,
                 cache_dir: Path = CACHE_DIR) -> list[Path]:
    """把 [start, end) 的影像抓下來（已存在就跳過）。回傳本機路徑。"""
    import time
    import requests
    d = cache_dir / pid
    d.mkdir(parents=True, exist_ok=True)
    out = []
    for i in range(start, end):
        p = d / f"{i:07d}.jpg"
        if not p.exists():
            r = requests.get(image_url(pid, i, width), timeout=90)
            r.raise_for_status()
            p.write_bytes(r.content)
            time.sleep(0.8)  # NDL 是公共資源，節流
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=str, help="pid：印書誌與分章")
    ap.add_argument("--fetch", type=str, help="pid：下載全部影像到快取")
    ap.add_argument("--width", type=int, default=1800)
    args = ap.parse_args()
    pid = args.probe or args.fetch
    if not pid:
        ap.error("--probe 或 --fetch 擇一")
    if not is_open(pid):
        print(f"pid={pid} 不是インターネット公開（館內限定／個人送信），不可取用")
        return
    b = fetch_book(pid)
    secs = sections_from_index(b["index"], b["pages"], fallback_title=b["title"])
    print(f"《{b['title']}》{b['author']} {b['publisher']} {b['year']}  影像 {b['pages']} 頁")
    for s in secs:
        print(f"   {s['start']:>4}–{s['end'] - 1:<4} {s['title'][:44]}")
    if args.fetch:
        got = fetch_images(pid, 1, b["pages"] + 1, width=args.width)
        print(f"下載完成 {len(got)} 張 → {CACHE_DIR / pid}")


if __name__ == "__main__":
    main()
