#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多語全集（有 sources 的，collection=collected-works）補段號＋修列對齊（2026-10-01）。

這批（榮格 CW、穆勒、SBE…86 部）的章節路徑只是流水號（「精神醫學研究 · 0001」「第 1 節」），
真正的章名不在資料裡，所以**不合併頁面**，一塊一頁照舊；段號兩層「節序-段」，以原文段落為準：
  - 中文與各原文段數相等的塊（59 部全等、其餘多數塊）：逐列對應直接編；
  - 只有一種原文而段數不等：用 rebuild_reference_bilingual.align（長度比＋數字／西文詞重疊）
    重新對齊，兩欄不足處補零寬字元佔列，再編；併段寫 5–6、中文多出的段寫 5a；
  - 有兩種以上原文且段數不等、或塊內有小標又對不齊：這一塊不編，記下來。
段號寫在中文欄段首（頁碼標記之後）`{{s:節-段}}`，全集閱讀器搬到左欄引用號（已有 anchors 的書不動）。
守恆：各語言去掉標記與佔位字元後的字數改前改後必須相等。

  python -X utf8 scripts/number_multilingual.py [--apply] [--ids 檔]
寫回留 .jsonl.bak_numbering，推 R2＋更新 DB。
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebuild_reference_bilingual as rb  # noqa: E402
import restructure_chapters as rc  # noqa: E402

CH = rb.CHUNKS
EMPTY = rb.EMPTY_CELL
LEAD_P = re.compile(r"^((?:\{\{p:[^}]*\}\})*)")


def paras(s: str | None) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", s or "") if p.strip()]


def skip_row(z: str) -> bool:
    """不編號的列：標題、註文（[^N]: …）、分隔線、只有頁碼標記。"""
    return (z.startswith("#") or bool(re.match(r"^\[\^[^\]]{1,8}\]:", z)) or rb.FOOT_RULE_RE.match(z) is not None
            or not re.search(r"\w", rb.PAGE_MARK_RE.sub("", z).replace(EMPTY, "")))


def number_chunk(c: dict, label: str) -> tuple[dict | None, str]:
    order = c.get("source_order") or list((c.get("sources") or {}).keys())
    srcs = dict(c.get("sources") or {})
    if not srcs and c.get("source_text"):
        lang = c.get("source_lang") or "en"
        srcs, order = {lang: c["source_text"]}, [lang]
    z = paras(c.get("content"))
    s = {l: paras(srcs.get(l)) for l in order}
    if all(len(v) == len(z) for v in s.values()):
        rows = [([zz], {l: [s[l][i]] for l in order}) for i, zz in enumerate(z)]
    elif len(order) == 1 and not any(p.startswith("#") for p in z):
        l0 = order[0]
        rows = [(zg, {l0: eg}) for zg, eg in rb.align(z, s[l0])]
    else:
        return None, "段數不等且無法單獨對齊"
    k, extra = 0, 0
    zo: list[str] = []
    so: dict[str, list[str]] = {l: [] for l in order}
    for zg, sg in rows:
        zt = "\n".join(zg) if zg else EMPTY
        src_n = len(sg[order[0]])
        if zg and len(zg) == 1 and skip_row(zg[0]):
            mark = ""
        elif src_n:
            n0, k, extra = k + 1, k + src_n, 0
            mark = f"{{{{s:{label}-{n0 if n0 == k else f'{n0}–{k}'}}}}}"
        else:
            extra += 1
            mark = f"{{{{s:{label}-{k}{chr(96 + extra)}}}}}" if zg else ""
        if mark and zt != EMPTY:
            lead = LEAD_P.match(zt).group(1)
            zt = lead + mark + zt[len(lead):]
        zo.append(zt)
        for l in order:
            so[l].append("\n".join(sg[l]) if sg[l] else EMPTY)
    new = dict(c, content="\n\n".join(zo))
    if c.get("sources"):
        new["sources"] = {**c["sources"], **{l: "\n\n".join(so[l]) for l in order}}
    if c.get("source_text") is not None and order:
        new["source_text"] = "\n\n".join(so[order[0]])
    return new, "OK"


def mass(t: str | None) -> int:
    return len(re.findall(r"\w", re.sub(r"\{\{[ps]:[^}]*\}\}", "", (t or "").replace(EMPTY, ""))))


def process(chunks: list[dict]) -> tuple[list[dict] | None, str, dict]:
    if any(c.get("anchors") for c in chunks):
        return None, "已有標準引用號", {}
    if any("{{s:" in (c.get("content") or "") for c in chunks):
        return None, "已有段號", {}
    body = [c for c in chunks if (c.get("sources") or c.get("source_text"))
            and not rc.is_front(rc.clean_title((c.get("chapter_path") or "").split(" · ")[-1]))]
    if not body:
        return None, "沒有對照塊", {}
    labels = dict(zip([id(c) for c in body], rc.chapter_labels([rc.display_title(c.get("chapter_path") or "") for c in body])))
    out, skipped, realigned = [], 0, 0
    for c in chunks:
        if id(c) not in labels:
            out.append(c)
            continue
        new, why = number_chunk(c, labels[id(c)])
        if new is None:
            skipped += 1
            out.append(c)
            continue
        if len(paras(new["content"])) != len(paras(c.get("content"))):
            realigned += 1
        for key in ("content", "source_text"):
            if mass(c.get(key)) != mass(new.get(key)):
                return None, f"守恆失敗 {key}", {}
        for l, v in (c.get("sources") or {}).items():
            if mass(v) != mass((new.get("sources") or {}).get(l)):
                return None, f"守恆失敗 {l}", {}
        out.append(new)
    return out, "OK", {"chunks": len(body), "skipped": skipped, "realigned": realigned}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--ids")
    a = ap.parse_args()
    import audit_toc_accuracy as at
    import standardize_ebook as se
    meta = at.load_meta()
    ids = (Path(a.ids).read_text(encoding="utf-8").split() if a.ids
           else [k for k, v in meta.items() if v.get("collection") == "collected-works"])
    for bid in sorted(ids):
        src = CH / f"{bid}.jsonl"
        bak = src.with_name(src.name + ".bak_numbering")
        try:
            base = bak if bak.exists() else src
            if not base.exists():
                continue
            cs = [json.loads(l) for l in base.open(encoding="utf-8") if l.strip()]
            if not any(c.get("sources") or c.get("source_text") for c in cs):
                continue
            out, why, st = process(cs)
            print(("OK" if out else "SKIP"), bid, (meta.get(bid, {}).get("title") or "")[:24], why, st, flush=True)
            if out and a.apply:
                if not bak.exists():
                    shutil.copy2(src, bak)
                o = se.write_jsonl(bid, out)
                se.push_to_r2(bid, o)
                se.update_db(bid, out)
        except Exception as e:  # noqa: BLE001
            print("ERR", bid, f"{type(e).__name__}: {str(e)[:120]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
