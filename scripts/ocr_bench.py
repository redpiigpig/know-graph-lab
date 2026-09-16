# -*- coding: utf-8 -*-
"""OCR 引擎評測台 —— 用「有真文字層的 PDF」當標準答案，量出引擎的實際字元錯誤率。

為什麼要這一支：既有的 `requeue_reocr.staged_gate()` 是**相對**判準（新的要贏舊的），
它擋得住退步，但回答不了「這個引擎到底準不準」。換引擎之前得先有一把尺。

作法（三步，`make` → 引擎跑 → `score`）：

  1. `make`  從一本**有真文字層**的 PDF 抽出指定頁：
             - 文字層存成標準答案 `truth/pNNN.txt`
             - 同樣的頁 render 成影像、組成**沒有文字層**的 `exam.pdf`
             這一步是關鍵：不剝文字層，引擎直接讀字就是滿分，等於作弊。

  2. 把 `exam.pdf` 餵給要評的引擎，輸出擺一邊。

  3. `score` 逐頁比對，報 CER（字元錯誤率）、覆蓋率、長度比、重複幻覺。

比對前的正規化（這幾條決定數字公不公道）：
  - NFKC：全形半形視為同一字，OCR 吐全形不算錯。
  - 去掉所有空白與換行：斷行方式本來就不該算錯。
  - 兩邊都轉繁體：管線後面本來就會跑 s2tw，簡繁差異不是 OCR 的錯。

已知會被算進去的雜訊：書眉／頁碼。引擎多半會主動剝掉，標準答案卻留著，
所以 CER 會被高估約 1–2%（一頁 900 字裡書眉約 10 字）。要看得更準就配著
`len_ratio` 一起讀：len_ratio 明顯小於 1 且 CER 不高 → 是漏了家具不是認錯字。

用法：
    python scripts/ocr_bench.py make  --pdf <路徑> --pages 100-119 --out <目錄>
    python scripts/ocr_bench.py score --bench <目錄> --hyp <檔或目錄> --label mineru
    python scripts/ocr_bench.py score --bench <目錄> --hyp <...> --label gemini --json out.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── 正規化 ────────────────────────────────────────────────────────────────

_WS = re.compile(r"\s+")

# 引號與破折號的樣式差異不是辨識錯誤，抹平。NFKC 不管這些。
_PUNCT_MAP = str.maketrans({
    "“": '"', "”": '"', "‘": "'", "’": "'",
    "〝": '"', "〞": '"', "′": "'", "″": '"',
    "–": "-", "—": "-", "―": "-", "−": "-",
    "－": "-", "·": "·", "‧": "·", "•": "·",
})

try:
    from opencc import OpenCC

    _CC = OpenCC("s2tw")
except Exception:  # pragma: no cover - opencc 缺席時退化成不轉換
    _CC = None


def normalize(text: str) -> str:
    """把「不該算錯」的差異抹平：全半形、空白、簡繁。"""
    if not text:
        return ""
    s = unicodedata.normalize("NFKC", text)
    s = s.translate(_PUNCT_MAP)
    s = _WS.sub("", s)
    if _CC is not None:
        s = _CC.convert(s)
    return s


# ── 指標 ──────────────────────────────────────────────────────────────────


def cer(truth: str, hyp: str) -> float:
    """字元錯誤率 = 編輯距離 / 標準答案長度。答案空的時候回 0 或 1。"""
    if not truth:
        return 0.0 if not hyp else 1.0
    from rapidfuzz.distance import Levenshtein

    return Levenshtein.distance(truth, hyp) / len(truth)


def score_pages(truth_pages: dict[int, str], hyp_pages: dict[int, str]) -> dict:
    """逐頁比對後彙總。key 是頁碼（以 PDF 實體頁為準，0-based）。"""
    rows = []
    for pno in sorted(truth_pages):
        t = normalize(truth_pages[pno])
        h = normalize(hyp_pages.get(pno, ""))
        rows.append(
            {
                "page": pno,
                "truth_len": len(t),
                "hyp_len": len(h),
                "cer": round(cer(t, h), 4),
                "len_ratio": round(len(h) / len(t), 3) if t else None,
                "empty": not h,
            }
        )
    scored = [r for r in rows if r["truth_len"] >= 50]
    n = len(scored)
    total_truth = sum(r["truth_len"] for r in scored)
    total_hyp = sum(r["hyp_len"] for r in scored)
    # 用字數加權，長頁比短頁有份量
    weighted = (
        sum(r["cer"] * r["truth_len"] for r in scored) / total_truth if total_truth else 1.0
    )
    return {
        "pages_scored": n,
        "pages_empty": sum(1 for r in scored if r["empty"]),
        "cer_weighted": round(weighted, 4),
        "cer_median": round(sorted(r["cer"] for r in scored)[n // 2], 4) if n else None,
        "cer_worst": round(max((r["cer"] for r in scored), default=0), 4),
        "len_ratio_overall": round(total_hyp / total_truth, 3) if total_truth else None,
        "rows": rows,
    }


# ── make：出題 ────────────────────────────────────────────────────────────


def parse_pages(spec: str) -> list[int]:
    """'100-119' / '3,7,9' / '100-104,200' → [實體頁碼]（0-based）。"""
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    return sorted(set(out))


def cmd_make(args) -> int:
    import fitz

    src = Path(args.pdf)
    if not src.exists():
        print(f"找不到 PDF：{src}")
        return 1
    out = Path(args.out)
    (out / "truth").mkdir(parents=True, exist_ok=True)

    doc = fitz.open(src)
    pages = [p for p in parse_pages(args.pages) if 0 <= p < doc.page_count]
    if not pages:
        print("頁碼範圍是空的")
        return 1

    # 🚨 標準答案必須來自**排版產生**的文字層，不能是掃描後 OCR 出來的。
    # 拿 OCR 產物當答案，引擎認對了反而被算成錯 —— 分數看起來有模有樣，
    # 量到的卻是另一回事。判準：頁面有沒有鋪滿整頁的影像。
    scanned = 0
    for pno in pages:
        page = doc[pno]
        parea = abs(page.rect.width * page.rect.height)
        for img in page.get_images(full=True):
            try:
                bbox = page.get_image_bbox(img)
            except Exception:
                continue
            if parea and abs(bbox.width * bbox.height) / parea > 0.5:
                scanned += 1
                break
    if scanned and not args.allow_scanned:
        print(f"🚨 這 {scanned}/{len(pages)} 頁鋪著整頁影像 —— 文字層很可能是掃描後 OCR 的產物，")
        print("   拿它當標準答案量不準（引擎答對會被判錯）。請換一本原生數位排版的 PDF，")
        print("   真的要用就加 --allow-scanned。")
        doc.close()
        return 2

    exam = fitz.open()
    meta = {"source_pdf": str(src), "pages": pages, "dpi": args.dpi,
            "born_digital": scanned == 0, "truth": {}}
    thin = []
    for i, pno in enumerate(pages):
        page = doc[pno]
        text = page.get_text()
        if len(normalize(text)) < 50:
            thin.append(pno)
        (out / "truth" / f"p{pno:04d}.txt").write_text(text, encoding="utf-8")
        meta["truth"][str(pno)] = len(normalize(text))
        # render 成影像，塞進沒有文字層的新 PDF —— 這就是「考卷」
        # 走 JPEG：無壓縮的 12 頁會到 70MB，超過某些 API 的上限，
        # 兩個引擎就會拿到不同考卷，比較失去意義。
        pm = page.get_pixmap(dpi=args.dpi)
        newp = exam.new_page(width=pm.width, height=pm.height)
        newp.insert_image(
            fitz.Rect(0, 0, pm.width, pm.height),
            stream=pm.tobytes("jpeg", jpg_quality=args.jpeg_quality),
        )
        meta.setdefault("exam_index", {})[str(i)] = pno

    exam.save(out / "exam.pdf")
    exam.close()
    doc.close()

    (out / "bench.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"出題完成：{len(pages)} 頁 → {out}")
    print(f"  考卷（無文字層）: {out / 'exam.pdf'}")
    print(f"  標準答案        : {out / 'truth'}/")
    if thin:
        print(f"  ⚠ 這 {len(thin)} 頁文字層本來就薄（<50 字），評分時會自動略過：{thin[:10]}")
    return 0


# ── score：閱卷 ───────────────────────────────────────────────────────────


def load_truth(bench: Path) -> tuple[dict[int, str], dict]:
    meta = json.loads((bench / "bench.json").read_text(encoding="utf-8"))
    pages = {}
    for f in sorted((bench / "truth").glob("p*.txt")):
        pages[int(f.stem[1:])] = f.read_text(encoding="utf-8")
    return pages, meta


def load_hyp(path: Path, meta: dict) -> dict[int, str]:
    """把引擎輸出讀成 {實體頁碼: 文字}。認得三種形狀：

      - MinerU 的 `*_content_list.json`（有 page_idx，最準）
      - 我們自己的 JSONL（有 page_number）
      - 一疊 pNNN.txt
      - 單一 markdown/txt：整份當一頁比（只看整體 CER，沒有逐頁）
    """
    exam_index = {int(k): v for k, v in meta.get("exam_index", {}).items()}

    if path.is_dir():
        cl = list(path.rglob("*_content_list.json"))
        if cl:
            path = cl[0]
        else:
            txts = sorted(path.glob("p*.txt"))
            if txts:
                return {int(f.stem[1:]): f.read_text(encoding="utf-8") for f in txts}
            mds = sorted(path.rglob("*.md"))
            if mds:
                path = mds[0]

    if path.suffix == ".json" and path.name.endswith("_content_list.json"):
        blocks = json.loads(path.read_text(encoding="utf-8"))
        out: dict[int, str] = {}
        for b in blocks:
            idx = b.get("page_idx")
            if idx is None:
                continue
            pno = exam_index.get(int(idx), int(idx))
            txt = b.get("text") or ""
            if b.get("type") == "table":
                txt = b.get("table_body") or txt
            out[pno] = out.get(pno, "") + "\n" + txt
        return out

    if path.suffix == ".jsonl":
        out = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            pno = d.get("page_number")
            if pno is None:
                continue
            out[int(pno)] = d.get("content") or d.get("text") or ""
        return out

    # 單檔：整份當作一大頁
    return {-1: path.read_text(encoding="utf-8")}


def cmd_score(args) -> int:
    bench = Path(args.bench)
    truth_pages, meta = load_truth(bench)
    hyp_pages = load_hyp(Path(args.hyp), meta)

    if set(hyp_pages) == {-1}:
        # 沒有逐頁資訊 → 只能整體比
        t = normalize("".join(truth_pages[p] for p in sorted(truth_pages)))
        h = normalize(hyp_pages[-1])
        res = {
            "mode": "whole-document",
            "cer_weighted": round(cer(t, h), 4),
            "truth_len": len(t),
            "hyp_len": len(h),
            "len_ratio_overall": round(len(h) / len(t), 3) if t else None,
            "rows": [],
        }
    else:
        res = score_pages(truth_pages, hyp_pages)
        res["mode"] = "per-page"

    res["label"] = args.label
    res["source_pdf"] = meta.get("source_pdf")

    print(f"=== {args.label} — {Path(meta.get('source_pdf', '?')).name} ===")
    print(f"  模式          : {res['mode']}")
    if res["mode"] == "per-page":
        print(f"  評分頁數      : {res['pages_scored']}（空白 {res['pages_empty']} 頁）")
        print(f"  CER 中位數    : {res['cer_median']:.2%}")
        print(f"  CER 最差一頁  : {res['cer_worst']:.2%}")
    print(f"  CER（字數加權）: {res['cer_weighted']:.2%}   ← 主要指標，越低越好")
    print(f"  長度比        : {res['len_ratio_overall']}  (1.0 = 抄回來的字數跟原文一樣多)")
    acc = 1 - res["cer_weighted"]
    print(f"  → 字元正確率  : {acc:.2%}")

    if res["mode"] == "per-page" and args.verbose:
        print("\n  逐頁：")
        for r in res["rows"]:
            if r["truth_len"] < 50:
                continue
            flag = "  ⚠" if r["cer"] > 0.15 else ""
            print(
                f"    p{r['page']:<5} 原文{r['truth_len']:>5}字  CER {r['cer']:>7.2%}"
                f"  長度比 {r['len_ratio']}{flag}"
            )

    if args.json:
        Path(args.json).write_text(
            json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\n  明細寫入 {args.json}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    m = sub.add_parser("make", help="從有文字層的 PDF 出一份考卷＋標準答案")
    m.add_argument("--pdf", required=True)
    m.add_argument("--pages", required=True, help="例 100-119 或 3,7,9")
    m.add_argument("--out", required=True)
    m.add_argument("--dpi", type=int, default=200)
    m.add_argument("--jpeg-quality", type=int, default=85,
                   help="考卷影像的 JPEG 品質（預設 85，壓到 API 吃得下的大小）")
    m.add_argument("--allow-scanned", action="store_true",
                   help="明知文字層是 OCR 產物仍要出題（分數只能當參考）")
    m.set_defaults(func=cmd_make)

    s = sub.add_parser("score", help="拿引擎輸出跟標準答案比")
    s.add_argument("--bench", required=True, help="make 產生的目錄")
    s.add_argument("--hyp", required=True, help="引擎輸出（目錄／content_list.json／jsonl／md）")
    s.add_argument("--label", default="engine")
    s.add_argument("--json", help="把明細寫成 JSON")
    s.add_argument("-v", "--verbose", action="store_true", help="印逐頁明細")
    s.set_defaults(func=cmd_score)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
