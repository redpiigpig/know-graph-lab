#!/usr/bin/env python
"""精修 step 4 — 針對性補譯 zh-empty 殘段（多為邊註標題/索引行/正文片段，
當初引擎連 3 次回空 MAX_FAIL 被跳過，非真垃圾）。

只動 zh[i] 為空且 en[i] 有字的段；用 Haiku（Müller glossary prompt, retry×4）。
跑完 re-upload 受影響書。resumable：填一段存一段，重跑只補仍空的。

  python scripts/mueller_fill_residuals.py            # 全部書
  python scripts/mueller_fill_residuals.py --only natural-religion,six-systems
  python scripts/mueller_fill_residuals.py --no-upload # 只填 cache 不上傳
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import mueller_haiku_pass as mhp  # noqa: E402
import mueller_auto as ma  # noqa: E402
import mueller_build as mb  # noqa: E402
import translate_ebook_to_zh as te  # noqa: E402


def make_heading_safe_engine():
    """Like mhp.make_haiku_engine but STRIPS leading #-markers instead of deleting
    whole heading lines. The sidenote/heading residuals (e.g. 'Funeral Ceremonies
    in Greece.') were left empty because Haiku formats short titles as markdown
    headings and the default _clean nukes them → MAX_FAIL. Keep the text."""
    te.PROMPT_TMPL = mb.MUELLER_PROMPT_TMPL

    def _clean(out: str) -> str:
        out = re.sub(r"(?m)^\s*#{1,6}\s*", "", out)   # strip markers, KEEP text
        return re.sub(r"\s*\n\s*", " ", out).strip()

    def translate_para(en: str, de: str = "") -> str:
        src = en.strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)
        out = ""
        for _ in range(4):
            out = _clean(" ".join(te.haiku_translate(p) for p in pieces))
            if out:
                return out
        return out

    return translate_para

ROOT = os.path.join(os.path.dirname(__file__), "..",
                    ".claude", "skills", "ebook-collected-works", "mueller_data")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--no-upload", action="store_true")
    ap.add_argument("--heading-safe", action="store_true",
                    help="strip #-markers instead of deleting heading lines "
                         "(second pass for sidenote/title residuals)")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    tp = make_heading_safe_engine() if args.heading_safe else mhp.make_haiku_engine()
    by_slug = {w["slug"]: w for w in ma.WORKS}

    touched = set()
    filled = still = 0
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d)
        if not os.path.isdir(p):
            continue
        if only and d not in only:
            continue
        for s in sorted(glob.glob(os.path.join(p, "sec*.json"))):
            j = json.load(open(s, encoding="utf-8"))
            zh = j.get("zh") or []
            en = j.get("en") or []
            dirty = False
            for i in range(len(zh)):
                if (zh[i] or "").strip():
                    continue
                src = (en[i] if i < len(en) else "") or ""
                if not src.strip():
                    continue
                out = tp(src)
                if out and out.strip():
                    zh[i] = out
                    filled += 1
                    dirty = True
                    print(f"  ✓ [{d} {os.path.basename(s)} #{i}] {src[:46]!r} → {out[:46]!r}",
                          flush=True)
                else:
                    still += 1
                    print(f"  · [{d} {os.path.basename(s)} #{i}] still empty: {src[:50]!r}",
                          flush=True)
            if dirty:
                j["zh"] = zh
                json.dump(j, open(s, "w", encoding="utf-8"), ensure_ascii=False)
                touched.add(d)

    print(f"\nfilled={filled} still_empty={still} touched_books={sorted(touched)}", flush=True)

    if not args.no_upload and touched:
        for d in sorted(touched):
            if d == "isr":
                print("  (isr 三欄書：跑 mueller_build.py --build-only --upload 重上傳)", flush=True)
                continue
            try:
                ma.assemble_and_upload(by_slug[d])
            except Exception as e:  # noqa: BLE001
                print(f"  ✗ upload {d}: {type(e).__name__}: {e}", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
