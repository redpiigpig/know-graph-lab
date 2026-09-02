"""Translate the full English Collected Works of C. G. Jung (Hull, Bollingen) →
繁中, one bilingual ebook per CW volume (set-books-split). Source = the complete
digital-edition EPUB the user placed in repo root. English-first: source_text=en,
content=繁中 (NVIDIA-first engine). Checkpoint per chunk, resumable, --all runs
volumes sequentially, uploads every N chunks.

Volume body is bounded via the EPUB's toc.ncx: each volume = a contiguous
part-file range; front matter (title/copyright) is filtered by paragraph pattern
and the back matter (Index / Bibliography / Footnotes) is cut at its navPoint.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, "scripts")
from multilang_chunks import build_multilang_chunk, validate_multilang_chunk, write_jsonl

_EPUB_GLOB = "The Collected Works of C. G. Jung*.epub"
# 原檔 2026-08 依 Drive-canonical 政策從 repo root 移到全集夾；repo root 先找（舊機器
# 還放著就用），找不到再讀 Drive。少了這一段，fleet keeper 的 jung lane 會每 30 分
# 秒退在 "CW EPUB not found"。
_DRIVE_JUNG = r"G:\我的雲端硬碟\資料\知識圖工作室\全集\心理學\榮格"
EPUB = next(iter(glob.glob(_EPUB_GLOB) or glob.glob(str(Path(_DRIVE_JUNG) / _EPUB_GLOB))), "")
DATA_ROOT = Path(".claude/skills/ebook-collected-works/jung_data/cw-full")

# num → (繁中卷名, part_start). Ends are the next volume's start; vol 19
# (bibliography/index) is the terminator and is NOT translated.
VOLS = {
    1: ("精神醫學研究", 2), 2: ("實驗研究（字詞聯想）", 36),
    3: ("精神疾病的心理成因", 90), 4: ("佛洛伊德與精神分析", 125),
    5: ("轉化的象徵", 190), 6: ("心理類型", 242),
    7: ("分析心理學二論", 295), 8: ("心靈的結構與動力", 363),
    "9i": ("原型與集體無意識", 421), "9ii": ("伊雍：自性現象學研究", 468),
    10: ("轉變中的文明", 514), 11: ("心理學與宗教：西方與東方", 602),
    12: ("心理學與煉金術", 638), 13: ("煉金術研究", 678),
    14: ("神祕合體", 756), 15: ("人、藝術與文學中的精神", 791),
    16: ("心理治療實務", 825), 17: ("人格的發展", 893),
    18: ("象徵的生命", 918),
}
_TERMINATOR = 1244  # part index where vol 19 (General Bibliography) begins
_ORDER = [1, 2, 3, 4, 5, 6, 7, 8, "9i", "9ii", 10, 11, 12, 13, 14, 15, 16, 17, 18]

_FRONT = re.compile(r"^(C\.\s*G\.\s*JUNG|SECOND EDITION|TRANSLATED BY|BOLLINGEN|COPYRIGHT|"
                    r"[A-Z ]{0,40}(EDITION|PRINTING)[A-Z ,0-9]*$|PRINCETON|ROUTLEDGE|"
                    r"ISBN|Library of Congress|All rights reserved|Manufactured in|"
                    r"THIS EDITION|ORIGINALLY PUBLISHED|Originally published|"
                    r"\d+ ILLUSTRATIONS|WITH \d+|Editorial (Note|Preface)$|"
                    r"Edited by |Translated by |THE FREUD ?/ ?JUNG|Published \d{4})", re.I)
_INDEXLINE = re.compile(r".{1,60}[,.]\s*\d[\d, –-]*$")  # "Term, 123, 145"
_SPACED = re.compile(r"^(?:\S ){4,}\S\s*$")  # "B O L L I N G E N S E R I E S" letter-spacing


def _is_front(t: str) -> bool:
    return bool(_FRONT.match(t) or _SPACED.match(t))


def load_env() -> None:
    for line in Path(".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _part_num(src: str) -> int | None:
    m = re.search(r"part(\d+)\.html", src)
    return int(m.group(1)) if m else None


def _spine(z: zipfile.ZipFile) -> list[str]:
    """Ordered reading sequence of hrefs — part files are NOT contiguously
    numbered, so we must follow the OPF spine, not range()."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(z.read("content.opf"), "xml")
    man = {it.get("id"): it.get("href") for it in soup.find_all("item")}
    return [man[ir.get("idref")] for ir in soup.find_all("itemref")
            if man.get(ir.get("idref"))]


def _boundaries(z: zipfile.ZipFile) -> dict:
    """volume key → (body_start_spine_idx, body_end_spine_idx). Body ends at the
    volume's first Index/Bibliography/Footnotes/Editor navPoint (spine position)."""
    spine = _spine(z)
    pos = {}  # part number → spine index (first occurrence)
    for i, href in enumerate(spine):
        pn = _part_num(href)
        if pn is not None and pn not in pos:
            pos[pn] = i
    ncx = z.read("toc.ncx").decode("utf-8", errors="replace")
    navs = []
    for lbl, src in re.findall(r"<navLabel>\s*<text>(.*?)</text>\s*</navLabel>\s*<content src=\"([^\"]+)\"", ncx, re.S):
        pn = _part_num(src)
        if pn is not None and pn in pos:
            navs.append((pos[pn], lbl.strip()))
    # spine index of every volume boundary (starts + terminator), ascending
    bounds = sorted(pos[p] for p in ([v[1] for v in VOLS.values()] + [_TERMINATOR]) if p in pos)
    out = {}
    for key, (_title, ps) in VOLS.items():
        si = pos.get(ps)
        if si is None:
            continue
        ei = next((b for b in bounds if b > si), len(spine))
        cut = ei
        for nav_i, lbl in navs:
            if si < nav_i < ei and re.match(r"(Index|Bibliography|Footnotes|Editor)\b", lbl, re.I):
                cut = min(cut, nav_i)
        out[key] = (si, cut)
    return out


def extract_volume(z: zipfile.ZipFile, si: int, ei: int) -> list[str]:
    from bs4 import BeautifulSoup

    spine = _spine(z)
    names = set(z.namelist())
    paras: list[str] = []
    for href in spine[si:ei]:
        name = href if href in names else "text/" + href.split("/")[-1]
        if name not in names:
            continue
        soup = BeautifulSoup(z.read(name), "html.parser")
        for p in soup.find_all(["p", "h1", "h2", "h3", "h4"]):
            t = re.sub(r"\s+", " ", p.get_text(" ")).strip()
            if not t or _is_front(t) or re.fullmatch(r"[\dIVXLCDM.\s,–-]+", t):
                continue
            if _INDEXLINE.fullmatch(t) and len(t) < 70:
                continue
            paras.append(t)
    return paras


def chunk_paras(paras: list[str], max_chars: int) -> list[str]:
    chunks, cur, n = [], [], 0
    for p in paras:
        if cur and n + len(p) + 2 > max_chars:
            chunks.append("\n\n".join(cur))
            cur, n = [], 0
        cur.append(p)
        n += len(p) + 2
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


def ebid_for(vol) -> str:
    key = str(vol).replace("i", "1").replace("9119", "9019")  # 9i→"91", 9ii→"911" not needed
    tail = {"9i": "091", "9ii": "092"}.get(str(vol), f"{int(vol):03d}" if str(vol).isdigit() else "000")
    return f"22220000-0000-4222-8222-000000000{tail}"


PRE = re.compile(r"^(以下是?|以下為|這是?|下面是?|這裡是|好的|當然|茲將)[^\n]{0,80}(翻譯|繁體中文|中文版|譯文|版本|如下|結果|Markdown|對照)[^\n]{0,120}[:：。]?\s*$")
RULE = re.compile(r"^[-*_]{3,}$")


def clean_pre(zh: str) -> str:
    ps = zh.split("\n\n")
    while ps and (PRE.match(ps[0].strip()) or RULE.match(ps[0].strip()) or not ps[0].strip()):
        ps.pop(0)
    return "\n\n".join(ps)


def assemble(vol, cfg_title: str, ebid: str, data: Path, units: list[str], *, upload: bool) -> None:
    out = [{"chunk_index": 0, "chunk_type": "chapter", "page_number": None,
            "chapter_path": "封面", "format": "markdown", "content": f"## {cfg_title}"}]
    ci = 1
    for i in range(len(units)):
        part = data / "parts" / f"{i:04d}.json"
        if not part.exists():
            continue
        obj = json.loads(part.read_text(encoding="utf-8"))
        c = build_multilang_chunk(chunk_index=ci, chapter_path=f"{cfg_title} · {i + 1:04d}",
                                  volume=cfg_title, parent_volume="榮格全集（Hull 英譯）",
                                  content_zh=obj["zh"], sources={"en": obj["en"]}, source_order=["en"])
        validate_multilang_chunk(c)
        out.append(c)
        ci += 1
    base = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
    base.mkdir(parents=True, exist_ok=True)
    write_jsonl(out, base / f"{ebid}.jsonl")
    print(f"  assembled {len(out)} chunks", flush=True)
    if not upload:
        return
    import requests

    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    hj = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
          "Prefer": "resolution=merge-duplicates"}
    hg = {"apikey": key, "Authorization": f"Bearer {key}"}
    now = dt.datetime.utcnow().isoformat() + "Z"
    row = {"id": ebid, "title": f"{cfg_title}（CW {vol}·英繁中）", "author": "C. G. 榮格",
           "author_en": "C. G. Jung", "original_title": f"Collected Works vol. {vol} (Hull)",
           "file_type": "epub",
           # 全 16 卷同一個 file_path 會撞 ebooks_file_path_uniq：第一卷進得去，其餘
           # 每次上傳都 409（2026-09 之前只有 CW11 上得了站就是這個原因）。卷號後綴
           # 讓每卷唯一，仍指得回同一份 Drive 原檔。
           "file_path": f"Drive/全集/心理學/榮格/CW-complete.epub#CW{vol}",
           "category": "世界宗教", "subcategory": "深層心理學", "display_mode": "standard",
           # 少了這一欄，卷子會以 collection=NULL 落進電子圖書館
           # （[[feedback_collected_works_not_in_library]]）。
           "collection": "collected-works",
           "translator": "Codex（NVIDIA 英譯本重譯繁中）", "publication_year": 1960,
           "chunk_count": len(out), "total_pages": len(out),
           "total_chars": sum(len(c["content"]) for c in out), "parsed_at": now, "standardized_at": now}
    # raise_for_status() 只給狀態碼，PostgREST 把真正的原因（撞哪一條約束）放在 body，
    # 沒印出來就只能猜。
    def _ok(resp):
        if resp.status_code >= 300:
            raise RuntimeError(f"{resp.status_code} {resp.text[:400]}")
        return resp

    try:
        _ok(requests.post(f"{url}/rest/v1/ebooks", headers=hj, json=row, timeout=30))
        _ok(requests.delete(f"{url}/rest/v1/ebook_chunks?ebook_id=eq.{ebid}", headers=hg, timeout=60))
        prev = [{"ebook_id": ebid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
                 "page_number": c.get("page_number"), "chapter_path": c["chapter_path"],
                 "content": c["content"][:200], "char_count": len(c["content"])} for c in out]
        for i in range(0, len(prev), 20):
            _ok(requests.post(f"{url}/rest/v1/ebook_chunks", headers=hj, json=prev[i:i + 20], timeout=60))
        print(f"  upserted previews={len(prev)}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  WARN upload: {exc}", flush=True)


def run_vol(vol, cfg, bounds, args) -> None:
    import translate_ebook_to_zh as te

    engine = {"nvidia": te.nvidia_translate, "auto": te.gemini_with_nvidia_fallback,
              "haiku": te.haiku_translate}[args.engine]
    title, _start = cfg
    z = zipfile.ZipFile(EPUB)
    si, ei = bounds[vol]
    paras = extract_volume(z, si, ei)
    units = chunk_paras(paras, args.max_chars)
    if args.limit:
        units = units[:args.limit]
    ebid = ebid_for(vol)
    data = DATA_ROOT / f"cw{vol}"
    (data / "parts").mkdir(parents=True, exist_ok=True)
    print(f"[CW {vol}] {title} paras={len(paras)} units={len(units)} ebid={ebid}", flush=True)
    if args.inspect:
        return
    done = sum((data / "parts" / f"{i:04d}.json").exists() for i in range(len(units)))
    for i, en in enumerate(units):
        part = data / "parts" / f"{i:04d}.json"
        if part.exists():
            continue
        try:
            zh = clean_pre("\n\n".join(te._to_traditional(engine(s)) for s in te.split_oversized(en)))
        except Exception as exc:  # noqa: BLE001
            print(f"  SKIP {i:04d}: {type(exc).__name__} {str(exc)[:90]}", flush=True)
            time.sleep(8)
            continue
        part.write_text(json.dumps({"i": i, "en": en, "zh": zh}, ensure_ascii=False, indent=1), encoding="utf-8")
        done += 1
        (data / "status.json").write_text(json.dumps(
            {"ebook_id": ebid, "title": f"CW {vol} {title}", "done": done, "total": len(units),
             "current": f"{i:04d}", "updated_at": dt.datetime.now().isoformat(timespec="seconds")},
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  {done}/{len(units)} CW{vol} {i:04d}", flush=True)
        if done % args.upload_every == 0:
            assemble(vol, title, ebid, data, units, upload=not args.no_upload)
        time.sleep(0.4)
    assemble(vol, title, ebid, data, units, upload=not args.no_upload)
    print(f"[CW {vol}] complete", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vol", help="single volume key e.g. 11 or 9ii")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--order", help="comma vol keys for --all/order")
    ap.add_argument("--engine", default="nvidia", choices=["nvidia", "auto", "haiku"])
    ap.add_argument("--max-chars", type=int, default=4200)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--upload-every", type=int, default=8)
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--inspect", action="store_true")
    args = ap.parse_args()
    if not EPUB:
        sys.exit("CW EPUB not found in repo root")
    load_env()
    z = zipfile.ZipFile(EPUB)
    bounds = _boundaries(z)
    if args.order:
        keys = [k if not k.isdigit() else int(k) for k in args.order.split(",")]
    elif args.all:
        keys = _ORDER
    elif args.vol:
        keys = [args.vol if not args.vol.isdigit() else int(args.vol)]
    else:
        ap.error("need --vol or --all")
    for k in keys:
        run_vol(k, VOLS[k], bounds, args)


if __name__ == "__main__":
    main()
