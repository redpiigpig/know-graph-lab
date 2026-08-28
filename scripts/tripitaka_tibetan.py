"""佛教大藏經 /tripitaka —— 藏譯原典（84000 翻譯記憶）掛到漢譯品上。

藏文正文的來源比梵文難找：
  84000/data-tei          是**英譯**，藏文只在術語表（1.4 MB 檔僅 6 千個藏文字元）
  Esukhia/derge-kangyur   有德格版藏文，但按函冊葉碼編排、且已封存；
                          要切出某一部得先建 Toh→葉碼表再切，正是最易靜默切錯的一類
  84000/data-translation-memory ← 用這個。**按 Toh 號命名的 TMX**（藏英逐句對齊），
                          383 部，法華 Toh 113 有 54 萬個藏文字元、4,529 個對齊單元

章節怎麼切：TMX 的 `location-id` 只是不透明里程碑，沒有結構。但英譯那一側
帶 84000 的章節標題，格式是段首的 `<章名> Chapter <N>`（注意「This concludes …
the Nth chapter」是章尾，要排除）。故以英文側偵測章界、切藏文側。

🚨 沿用 tripitaka_sanskrit 的那道閘：**章數不合就拒絕逐品對齊**。
   法華藏本 27 章、羅什漢譯 28 品，且羅什把囑累品移到第 22、陀羅尼排到第 26 ——
   差異有兩處而非一處，只做「12 起加一」會讓尾段四個品全配錯。
   藏本章序與梵本一致，故共用 tripitaka_sanskrit 那張已核對過的表。

  python scripts/tripitaka_tibetan.py --probe toh113   # 報書名與章數（建表用）
  python scripts/tripitaka_tibetan.py --audit
  python scripts/tripitaka_tibetan.py --build
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import tripitaka_parallels as tpp  # noqa: E402
import tripitaka_sanskrit as ts  # noqa: E402

TMX_LIST = "https://api.github.com/repos/84000/data-translation-memory/contents/"
TMX_RAW = "https://raw.githubusercontent.com/84000/data-translation-memory/master/{}"
CACHE = Path(os.environ.get("TIBETAN_CACHE", "C:/tmp/cbeta/tibetan"))
SEG_DIR = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))


def _lotus_map() -> dict:
    """法華的品對照表與梵文那邊共用（藏本章序與梵本一致），
    改一處就好，不要在兩個檔各抄一份會漂移的表。"""
    return next(e for e in ts.REGISTRY if e["work"] == "T0262")["chapter_map"]


# 每一筆都要用 --probe 先看過該 Toh 的自述書名與章數，確認梵漢確為同一部書，
# 不是靠 Toh 號的記憶填的。
REGISTRY: list[dict] = [
    {"toh": "toh113", "work": "T0262", "zh": "妙法蓮華經",
     "bo": "The White Lotus of the Good Dharma", "chapter_map": _lotus_map(),
     "note": "藏本 27 章，章序同梵本；與梵文共用品對照表"},
    # 以下幾部的 TMX 英文側沒有章標記（平鋪句段），漢本若有品層就會被閘擋下 ——
    # 那是對的：寧可不掛，也不要把整部藏文硬塞給某一品。
    {"toh": "toh21", "work": "T0251", "zh": "般若波羅蜜多心經",
     "bo": "The Heart of the Perfection of Wisdom", "note": "單章，漢藏皆不分品"},
    {"toh": "toh504", "work": "T0450", "zh": "藥師琉璃光如來本願功德經",
     "bo": "The Previous Aspirations of Bhaiṣajyaguru", "note": "單章"},
    {"toh": "toh106", "work": "T0676", "zh": "解深密經",
     "bo": "Unraveling the Intent", "note": "TMX 無章標記，漢本有品 → 預期被閘擋下"},
    {"toh": "toh176", "work": "T0475", "zh": "維摩詰所說經",
     "bo": "The Teaching of Vimalakīrti", "note": "TMX 無章標記，漢本有品 → 預期被閘擋下"},
]


def tmx_files() -> dict[str, str]:
    """Toh 前綴 → 檔名（toh113 → toh113-v3.tmx）。"""
    cache = CACHE / "_list.json"
    CACHE.mkdir(parents=True, exist_ok=True)
    if not cache.exists():
        with urllib.request.urlopen(TMX_LIST, timeout=120) as r:
            cache.write_bytes(r.read())
    out: dict[str, str] = {}
    for e in json.loads(cache.read_text(encoding="utf-8")):
        m = re.match(r"^(toh[\d-]+?)(?:-v\d+)?\.tmx$", e["name"])
        if m:
            out.setdefault(m.group(1), e["name"])
    return out


def fetch(toh: str) -> Path:
    files = tmx_files()
    name = files.get(toh)
    if not name:
        raise SystemExit(f"84000 翻譯記憶沒有 {toh}（共 {len(files)} 部）")
    dst = CACHE / name
    if dst.exists() and dst.stat().st_size > 1000:
        return dst
    with urllib.request.urlopen(TMX_RAW.format(name), timeout=300) as r:
        dst.write_bytes(r.read())
    return dst


_SEG_RE = {
    "bo": re.compile(r'xml:lang="bo"[^>]*>\s*<seg>(.*?)</seg>', re.S),
    "en": re.compile(r'xml:lang="en"[^>]*>\s*<seg>(.*?)</seg>', re.S),
}
_CHAPTER_RE = re.compile(r"^(?:\{\d+\}\s*)?(.{0,90}?)\bChapter\s+(\d+)\b")


def _plain(s: str) -> str:
    return re.sub(r"<[^>]+>|\s+", " ", s).strip()


def parse_tmx(path: Path) -> tuple[dict[int, list[str]], dict[int, str]]:
    """→ ({章號: [藏文句…]}, {章號: 英文章名})。

    章界靠英文側偵測；「This concludes … the Nth chapter」是章尾標記，
    若不排除會把每一章的結尾又算成下一章的開頭。
    """
    raw = path.read_text(encoding="utf-8", errors="replace")
    out: dict[int, list[str]] = {}
    titles: dict[int, str] = {}
    # 起始就算第 1 章：不少 Toh 的 TMX 英文側根本沒有章標記（解深密、維摩詰
    # 都是平鋪句段）。若從 0 起算，這些書會一句都收不到而看起來「沒有藏文」。
    cur = 1
    for tu in re.findall(r"<tu[ >].*?</tu>", raw, re.S):
        m_en = _SEG_RE["en"].search(tu)
        m_bo = _SEG_RE["bo"].search(tu)
        en = _plain(m_en.group(1)) if m_en else ""
        bo = _plain(m_bo.group(1)) if m_bo else ""
        m = _CHAPTER_RE.match(en)
        if m and "concludes" not in en[: m.end()]:
            cur = int(m.group(2))
            titles.setdefault(cur, m.group(1).strip())
        if bo:
            out.setdefault(cur, []).append(bo)
    return out, titles


def cmd_probe(toh: str):
    path = fetch(toh)
    chapters, titles = parse_tmx(path)
    raw = path.read_text(encoding="utf-8", errors="replace")
    title = ""
    m = _SEG_RE["en"].search(raw)
    if m:
        title = _plain(m.group(1))
    bo_chars = len(re.findall(r"[\u0f00-\u0fff]", raw))
    print(f"{toh}　{path.name}")
    print(f"  書名（英）: {title}")
    print(f"  藏文字元 {bo_chars:,}　章數 {len(chapters)}　"
          f"藏文句 {sum(len(v) for v in chapters.values()):,}")
    for n in sorted(titles)[:40]:
        print(f"    {n:3d} {titles[n][:56]}")


def first_segment(work_id: str) -> str | None:
    """整部層級的落點：該經的第一段。心經、藥師這類漢本無品層的書，
    藏／梵文只能掛在全經開頭，不該因為「沒有品」就整個不掛。"""
    toc = tpp.toc_of(work_id)
    if toc:
        return toc[0]["uid"]
    p = SEG_DIR / f"{work_id}.jsonl"
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return json.loads(line)["uid"]
    return None


def audit_one(entry: dict) -> dict:
    chapters, titles = parse_tmx(fetch(entry["toh"]))
    zh = ts.zh_pin_segs(entry["work"])
    cmap = entry.get("chapter_map")
    if cmap:
        aligned = sum(1 for k, v in cmap.items() if k in chapters and v in zh)
        status, detail = "手寫品對照表", f"表列 {len(cmap)} 組，實對上 {aligned}"
    elif not zh:
        status, detail = "漢文本無品層", "退回整部層級"
    elif len(chapters) == len(zh):
        status, detail = "章數相符", f"逐品對齊 {len(chapters)} 章"
    else:
        status = "🚨 章數不合"
        detail = f"藏 {len(chapters)} 章 vs 漢 {len(zh)} 品 —— 拒絕逐品對齊，需手寫 chapter_map"
    return {**entry, "bo_chapters": len(chapters), "zh_chapters": len(zh),
            "status": status, "detail": detail, "_bo": chapters, "_zh": zh,
            "_titles": titles}


def cmd_audit():
    print(f"{'漢譯':22s} {'Toh':8s} {'藏章':>4s} {'漢品':>4s}  狀態")
    print("─" * 92)
    for e in REGISTRY:
        r = audit_one(e)
        print(f"{r['zh'][:20]:22s} {r['toh']:8s} {r['bo_chapters']:>4d} "
              f"{r['zh_chapters']:>4d}  {r['status']} — {r['detail']}")
        if e.get("note"):
            print(f"{'':32s}註：{e['note']}")


def cmd_build():
    written = 0
    for e in REGISTRY:
        r = audit_one(e)
        if "🚨" in r["status"]:
            print(f"  跳過 {r['zh']}：{r['detail']}")
            continue
        bo, zh, titles = r["_bo"], r["_zh"], r["_titles"]
        cmap = e.get("chapter_map") or {k: k for k in bo}
        if not zh:                       # 漢本無品層 → 整部掛在全經首段
            head = first_segment(e["work"])
            zh = {k: head for k in cmap} if head else {}
        by_seg: dict[str, list] = {}
        for bo_no, zh_no in cmap.items():
            lines = bo.get(int(bo_no))
            seg = zh.get(int(zh_no))
            if not lines or not seg:
                continue
            by_seg.setdefault(seg, []).append({
                "lang": "bo",
                "uid": f"{e['toh']}-{bo_no}",
                "ref": f"{e['bo']} {bo_no}"
                       + (f"（{titles.get(int(bo_no))}）" if titles.get(int(bo_no)) else ""),
                "src": "site",       # 本站對齊：琥珀色，非學術定論
                "partial": False,
                # 84000 的 TMX 沒有給句級引用座標，故行號留空 ——
                # 不自編看起來像引用式的號碼（見 SKILL.md 第 15 條）
                "lines": [["", t] for t in lines],
            })
        if not by_seg:
            print(f"  跳過 {r['zh']}：無可掛的品")
            continue
        out = SEG_DIR / f"{e['work']}.orig.json"
        existing = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
        for seg, items in by_seg.items():
            keep = [x for x in existing.get(seg, []) if x.get("lang") != "bo"]
            existing[seg] = keep + items
        out.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")
        written += 1
        print(f"  ✓ {r['zh']}（{e['work']}）：{len(by_seg)} 品掛上藏文，"
              f"{sum(len(v) for v in bo.values()):,} 句 → {out.name}")
    print(f"\n完成 {written} 部")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=str, help="報某個 Toh 的書名與章數（建表用）")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if a.probe:
        cmd_probe(a.probe)
    elif a.audit:
        cmd_audit()
    elif a.build:
        cmd_build()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
