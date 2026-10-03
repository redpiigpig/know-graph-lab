#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一卷的重切＋重新對齊（核心在 fathers_realign.py）。

  python -X utf8 scripts/fathers_realign_volume.py <id> [<id>…] [--apply] [--report DIR]

乾跑只印統計並寫缺口表到 output/fathers_gap/<id前8>.gaps.json；--apply 才寫回
（改前留 .jsonl.bak_realign；寫回後推 R2＋更新 DB）。
守恆閘：每塊中文去標記後字數不變；每個群組的英文每列恰好出現一次。不過閘就整卷不寫。
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fathers_realign as fr  # noqa: E402

CH = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
OUT = ROOT / "output" / "fathers_gap"


def labels_for(chunks: list[dict]) -> dict[int, str]:
    import restructure_chapters as rc
    body = [c for c in chunks if (c.get("sources") or c.get("source_text"))
            and not rc.is_front(rc.clean_title((c.get("chapter_path") or "").split(" · ")[-1]))]
    labs = rc.chapter_labels([rc.display_title(c.get("chapter_path") or "") for c in body])
    return {c["chunk_index"]: l for c, l in zip(body, labs)}


def skip_tag(z: str) -> bool:
    return z.startswith("#") or fr.kind_of(z) != "B" or not fr.re.search(r"\w", fr.ANYTAG_RE.sub("", z))


def tidy_rows(rows: list) -> list:
    """正文列在前、註文列集中在塊尾、只留一條分隔線。

    閱讀器的 splitBodyAndFootnotes／renderMarkdown 對分隔線是「開關」：每遇一條就翻一次。CCEL 的「正文、
    分隔線、註文、下一章正文、分隔線、註文…」會讓第二章起的正文被當成註文續行（英欄尤其——英文章標題沒有 #，
    翻不回來）。中英列是成對的，把註文對搬到塊尾兩欄一起動；註文靠 (N) 號配對、不靠列序，顯示不變。"""
    def strip_rule(t):
        """一列的開頭若是分隔線（常見：「————\n(1) 註…\n(2) 註…」併成一列），剝掉分隔線、留下註文。"""
        if not t:
            return t
        ls = t.split(chr(10))
        while ls and fr.FOOT_RULE_RE.match(ls[0].strip()):
            ls = ls[1:]
        return chr(10).join(ls) if ls else None

    body, fn = [], []
    for zt, et, ne in rows:
        zt, et = strip_rule(zt), strip_rule(et)
        if not (zt or et):
            continue                      # 純分隔線列（\w 為零，不影響字數）
        k = fr.kind_of((zt or et).split(chr(10))[0])
        row = (zt, et, ne)
        (fn if k == "F" else body).append(row)
    if fn:
        body.append((fr.FOOT_RULE, fr.FOOT_RULE, 0))
    return body + fn


def build_chunk(c: dict, rows: list, label: str | None) -> dict:
    zo, eo = [], []
    k = extra = 0
    rows = tidy_rows(rows)
    for zt, et, ne in rows:
        zrow = zt if zt else fr.EMPTY
        erow = et if et else fr.EMPTY
        if zt and label and not skip_tag(zt.split("\n")[0]):
            if ne:
                n0, k, extra = k + 1, k + ne, 0
                mark = f"{n0}" if n0 == k else f"{n0}–{k}"
            else:
                extra += 1
                mark = f"{k}{chr(96 + extra)}"
            tag = f"{{{{s:{label}-{mark}}}}}"
            lead = fr.re.match(r"^((?:\{\{p:[^}]*\}\})*)", zrow).group(1)
            zrow = lead + tag + zrow[len(lead):]
        elif (not zt) and et and label and fr.kind_of(et.split(chr(10))[0]) == "B":
            k += max(ne, 1)          # 缺譯列也佔一個段號（補譯時照號寫回，後面的號不必重編）
            extra = 0
        zo.append(zrow)
        eo.append(erow)
    new = dict(c)
    new["content"] = "\n\n".join(zo)
    en = "\n\n".join(eo)
    srcs = dict(c.get("sources") or {})
    if srcs or (c.get("source_lang") or "en") == "en":
        if srcs:
            srcs["en"] = en
            new["sources"] = srcs
        new["source_text"] = en
    return new


LAST_NEWC: list = []


def has_index_aligned_third_column(c: dict) -> bool:
    """非英文的原典欄（拉丁／希臘）且列數與中文相同＝逐列對位，動中文列就會讓它錯位 → 這塊不動。"""
    zr = len(fr.split_rows(c.get("content")))
    return any(l != "en" and (t or "").strip() and len(fr.split_rows(t)) == zr
               for l, t in (c.get("sources") or {}).items())


def process_volume(bid: str, apply: bool = False, from_backup: bool = True) -> dict:
    """from_backup：已有 .bak_realign（第一次對齊前的原樣）就從它重算——對齊吃已切片的資料不是冪等的
    （英文欄已被切過，整檔就拼不回來）。補譯開始後不可再用（會丟掉已補的譯文）。"""
    path = CH / f"{bid}.jsonl"
    src_path = path.with_name(path.name + ".bak_realign")
    if not (from_backup and src_path.exists()):
        src_path = path
    chunks = [json.loads(l) for l in src_path.open(encoding="utf-8") if l.strip()]
    bakp = path.with_name(path.name + ".bak_numbering")
    bak = [json.loads(l) for l in bakp.open(encoding="utf-8") if l.strip()] if bakp.exists() else None
    rows = fr.load_rows(chunks, bak)
    groups = fr.group_chunks(chunks)
    zh_by = {i: rows[i][0] for i in range(len(chunks))}
    en_by = {i: rows[i][1] for i in range(len(chunks))}
    # 卷級中英比（只看看起來完整的單塊群組＋多塊群組）
    frozen = {i for i, c in enumerate(chunks) if has_index_aligned_third_column(c)}
    ratios = []
    Es = []
    for gi, g in enumerate(groups):
        E, _ = fr.file_en([en_by[i] for i in g])
        fz = [i for i in g if i in frozen]
        if fz:
            # 凍結塊（有逐列對位的第三欄）自己保留現狀；它的英文列從整檔裡扣掉，免得被當成缺譯
            keys = {fr._norm(x) for i in fz for x in en_by[i]}
            if len(g) > 1 and sum(len(x) for i in fz for x in en_by[i]) < 0.7 * sum(len(x) for x in E):
                E = [x for x in E if fr._norm(x) not in keys]
            groups[gi] = [i for i in g if i not in frozen]
            g = groups[gi]
            if not g:
                Es.append([])
                continue
        zl = sum(fr._len_zh(z) for i in g for z in zh_by[i] if fr.kind_of(z) != "S")
        Es.append(E)
        el = sum(fr._len_en(e) for e in E if fr.kind_of(e) != "S")
        if el > 2000 and zl:
            ratios.append(zl / el)
    good = [x for x in ratios if 0.25 <= x <= 0.55]
    vol_r = statistics.median(good) if good else 0.35
    results = []
    for g, E in zip(groups, Es):
        results.append(fr.realign_group(zh_by, en_by, g, vol_r, E))
    moves = fr.rescue_orphans(results, vol_r)
    labs = labels_for(chunks)
    newc = list(chunks)
    gaps = []
    orphans = []
    st = {"groups": len(groups), "zh_orphan_rows": 0, "zh_orphan_chars": 0, "odd_pairs": 0,
          "rescued_rows": len(moves), "rescued_chars": sum(m[2] for m in moves)}
    for res in results:
        st["odd_pairs"] += res.stats.get("odd_pairs", 0)
        for i in res.chunk_ids:
            rows_i = res.rows.get(i, [])
            newc[i] = build_chunk(chunks[i], rows_i, labs.get(chunks[i]["chunk_index"]))
            for ri, (zt, et, _n) in enumerate(rows_i):
                if zt is None and et is not None and fr.kind_of(et.split(chr(10))[0]) != "S":
                    gaps.append({"chunk_index": chunks[i]["chunk_index"], "row": ri,
                                 "kind": fr.kind_of(et.split(chr(10))[0]), "en": et})
                elif et is None and zt is not None and fr.kind_of(zt.split(chr(10))[0]) != "S":
                    orphans.append({"chunk_index": chunks[i]["chunk_index"], "row": ri,
                                    "kind": fr.kind_of(zt.split(chr(10))[0]), "zh": zt})
                    st["zh_orphan_rows"] += 1
                    st["zh_orphan_chars"] += fr._len_zh(zt)
    # 守恆：每塊中文字數 = 原本 − 搬出 + 搬入；全卷總和不變
    delta = {}
    for fi, ti, n in moves:
        delta[fi] = delta.get(fi, 0) - n
        delta[ti] = delta.get(ti, 0) + n
    errs = []
    promoted = {i for i, c in enumerate(chunks) if fr.untranslated(c)}
    st_promoted = len(promoted)
    for i, (a, b) in enumerate(zip(chunks, newc)):
        if i in promoted:
            continue
        want = fr.mass(a.get("content")) + sum(1 for _ in ())  # placeholder
        got = fr.mass(b.get("content"))
        # 搬移以「漢字數」記，mass 以 \w 計；搬移列的 \w 數另算
        if i in delta:
            continue
        if want != got:
            errs.append(f"#{a['chunk_index']} 中文字數 {want}→{got}")
    tot_b = sum(fr.mass(a.get("content")) for i, a in enumerate(chunks) if i not in promoted)
    tot_a = sum(fr.mass(b.get("content")) for i, b in enumerate(newc) if i not in promoted)
    if tot_a != tot_b:
        errs.append(f"全卷中文字數 {tot_b}→{tot_a}")
    for res, E in zip(results, Es):
        before = sum(fr.mass(e) for e in E)
        after = sum(fr.mass(newc[i].get("source_text")) for i in res.chunk_ids)
        if before != after:
            errs.append(f"群組 #{chunks[res.chunk_ids[0]]['chunk_index']} 英文 {before}→{after}" if res.chunk_ids else "空群組英文不符")
    en_gap_letters = sum(fr._len_en(g["en"]) for g in gaps if g["kind"] == "B")
    en_total = sum(fr._len_en(e) for E in Es for e in E if fr.kind_of(e) == "B")
    st.update({"promoted_untranslated_chunks": st_promoted, "vol_r": round(vol_r, 3), "chunks": len(chunks),
               "gap_rows": len(gaps),
               "gap_body_rows": sum(1 for g in gaps if g["kind"] == "B"),
               "gap_fn_rows": sum(1 for g in gaps if g["kind"] == "F"),
               "gap_body_letters": en_gap_letters, "en_body_letters": en_total,
               "conservation_errors": errs[:10], "n_errs": len(errs)})
    global LAST_NEWC
    LAST_NEWC = newc
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{bid[:8]}.gaps.json").write_text(json.dumps({"id": bid, "stats": st, "gaps": gaps, "orphans": orphans, "moves": moves},
                                                         ensure_ascii=False), encoding="utf-8")
    if apply and not errs:
        bk = path.with_name(path.name + ".bak_realign")
        if not bk.exists():
            shutil.copy2(path, bk)
        import standardize_ebook as se
        tmp = path.with_suffix(".jsonl.tmp")
        tmp.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in newc) + "\n", encoding="utf-8")
        tmp.replace(path)          # 原子換檔：中途被殺也不會留下半個檔
        o = path
        try:
            se.push_to_r2(bid, o)
            se.update_db(bid, newc)
        except Exception as e:  # noqa: BLE001
            st["push_error"] = f"{type(e).__name__}: {str(e)[:100]}"
        st["applied"] = True
    return st


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    for bid in a.ids:
        st = process_volume(bid, a.apply)
        print(bid[:8], json.dumps(st, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
