# -*- coding: utf-8 -*-
"""NDL 官方 OCR（layouttext）→ ocr-ndl/ checkpoint。

**這是本管線的首選取源，視覺模型 OCR 退為輔助。**

2026-09-08 實測（畔上賢造《無教會主義》影像 4，拿原圖逐字對）：

| 位置 | Gemini Vision | NDL 官方 |
|---|---|---|
| 教派**別**を無視 | 漏「別」 | ✅ |
| 加**へ**て | 加えて | ✅ |
| 無教**會的**精神 | 無教**的の**精神 | ✅ |
| 保**續** | 保持 | ✅ |
| 以上**に精神** | 以上は精 | ✅ |
| 呼ば**ね**ばならぬ | 呼べばならぬ | ✅ |

NDL 唯一的短處是字集裡沒有的舊字體會印成 `〓`（本書 397 處），
而那正是視覺模型讀得出來的 —— 兩邊互補，用 `fill_placeholders()` 接起來。

    python scripts/ndl_official_text.py 1099766 --refs gemini,gemini2

見 .claude/skills/ebook-collected-works/ndl_open_scans.md。
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from io import BytesIO
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import ndl_build as nb  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

LAYOUT_API = "https://lab.ndl.go.jp/dl/api/book/layouttext/{pid}"


def fetch_layout_zip(pid: str, cache_dir: Path) -> Path:
    """下載 layouttext ZIP（已存在就沿用，這是公共資源不要重抓）。"""
    import requests
    dst = cache_dir / pid / "layouttext.zip"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        r = requests.get(LAYOUT_API.format(pid=pid), timeout=120,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        dst.write_bytes(r.content)
    return dst


def pages_from_zip(zip_path: Path) -> dict:
    """ZIP → {影像號: [段落]}。"""
    out, title_at = {}, {}
    with zipfile.ZipFile(zip_path) as z:
        for name in sorted(z.namelist()):
            if not name.endswith(".xml"):
                continue
            try:
                img = int(name.rsplit("_", 1)[1].split(".")[0])
            except (IndexError, ValueError):
                continue
            lines = nb.parse_layout_xml(z.read(name))
            # 過渡頁：切掉正文之後接著排的書籍廣告／奧付
            keep = nb.body_lines_before_layout_break(lines)
            kept = {id(l) for l in keep}
            lines = [l for l in lines
                     if l.get("type") not in nb.BODY_LINE_TYPES or id(l) in kept]
            paras, titles = nb.lines_to_layout_paras(lines, mark_titles=True)
            title_at[img] = titles
            out[img] = [nb.restore_old_forms(p) for p in paras]
    return out, title_at


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pid")
    ap.add_argument("--refs", default="gemini,gemini2",
                    help="用來補 〓 的參照 OCR（逗號分隔，依序套用）")
    args = ap.parse_args()

    cache = nb.CACHE_DIR
    zp = fetch_layout_zip(args.pid, cache)
    pages, title_at = pages_from_zip(zp)
    print("NDL 官方 OCR：%d 頁" % len(pages))

    out_dir = cache / args.pid / "ocr-ndl"
    out_dir.mkdir(parents=True, exist_ok=True)
    before = after = 0
    inferred = []
    for img, paras in sorted(pages.items()):
        text = "\n\n".join(paras)
        before += text.count(nb.PLACEHOLDER)
        for ref in [r.strip() for r in args.refs.split(",") if r.strip()]:
            f = cache / args.pid / ("ocr-" + ref) / ("%07d.txt" % img)
            if f.exists():
                text = nb.fill_placeholders(text, f.read_text(encoding="utf-8"))
        # 參照對齊補完之後，剩下的用上下文規則推論。
        # 🚨 順序不可顛倒：參照對齊是逐字驗證過的，規則推論是統計性的，
        #    先跑規則的話會把本來能驗證的位置也變成推論。
        text, guessed = nb.resolve_ndl_placeholders(text, report=True)
        inferred.extend((img, g) for g in guessed)
        after += text.count(nb.PLACEHOLDER)
        (out_dir / ("%07d.txt" % img)).write_text(text, encoding="utf-8")

    chars = sum(len((out_dir / ("%07d.txt" % i)).read_text(encoding="utf-8"))
                for i in pages)
    print("〓 %d → %d（補回 %d；其中通用規則推論 %d 處）"
          % (before, after, before - after, len(inferred)))
    if inferred:
        # 🚨 通用規則（〓→敎）是統計推論不是逐字查證。印**相異上下文**而不是
        #    每一次 —— 310 次沒人看得完，20 種看得完。賀川那本就是這樣才發現
        #    整章的「鹽」被改成了「敎」。
        import collections as _c
        ctx = _c.Counter(g for _, g in inferred)
        print("   通用規則動過的相異上下文 %d 種（請掃一眼有沒有不像「敎」的）："
              % len(ctx))
        for g, n in ctx.most_common(30):
            print("     %-12s x%d" % (g.replace("\n", " "), n))
    import json as _json
    (out_dir / "_titles.json").write_text(
        _json.dumps({str(k): v for k, v in title_at.items()}, ensure_ascii=False),
        encoding="utf-8")
    # 🚨 重生會沖掉逐字精修的人工更正，這裡自動重套（見 ndl_corrections.py）
    import ndl_corrections
    n_fix = ndl_corrections.apply(args.pid, cache)
    if n_fix:
        print("重套人工更正 %d 條" % n_fix)
    print("共 %d 字 → %s" % (chars, out_dir))
    if after:
        print("🚨 仍有 %d 處 〓 要看圖裁定：" % after)
        for img in sorted(pages):
            t = (out_dir / ("%07d.txt" % img)).read_text(encoding="utf-8")
            for k, ch in enumerate(t):
                if ch == nb.PLACEHOLDER:
                    print("   影像 %-3d %s" % (img, t[max(0, k - 12):k + 13].replace("\n", " ")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
