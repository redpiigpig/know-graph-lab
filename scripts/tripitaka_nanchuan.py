"""佛教大藏經 /tripitaka —— 把《漢譯南傳大藏經》掛成漢譯阿含的對照欄。

漢譯阿含旁邊擺巴利羅馬字，對多數讀者用處有限；擺**同一部巴利經的現代漢譯**
（元亨寺版），才看得出同一則教說在南北兩傳的差別。這是使用者點名要的一欄。

🚨 五尼柯耶在元亨寺版的編號方式各不相同，硬套一種會整批錯位：

    長部  N06–N08  經在 depth 0，順序即 DN 1..34
    中部  N09–N12  篇 › 品 › 經，經在 depth 2，順序即 MN 1..152
    相應部 N13–N18 相應(d1)「第一　諸天相應」› 品(d2) › 經(d3)「〔一一〕歡喜園」
                   ⚠ 〔n〕**跨品連號**（葦品〔一〕–〔一〇〕、歡喜園品〔一一〕–〔二〇〕），
                     與巴利 SN 1.1–1.10 / 1.11–1.20 一致 → 鍵為「相應.經」
    增支部 N19–N25 集 › 品 › 經，集號不在標題層級裡，尚未接（見 --audit）

所以本檔的規矩是：**先驗經數，數不對就整個尼柯耶不掛**。
長部必須恰好 34 經、中部必須恰好 152 經 —— 這兩個數字是巴利藏的定數，
對不上就表示我的層級判斷錯了，寧可不掛也不要掛錯。

  python scripts/tripitaka_nanchuan.py --audit    # 驗經數（不寫）
  python scripts/tripitaka_nanchuan.py --build
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import tripitaka_parallels as tpp  # noqa: E402

SEG_DIR = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
ROWS = Path(os.environ.get("TRIPITAKA_PARALLEL_ROWS", "C:/tmp/cbeta/parallels_rows.jsonl"))
CATALOG = Path(os.environ.get("TRIPITAKA_CATALOG", "C:/tmp/cbeta/catalog.json"))

# 尼柯耶 → (N 冊區間, 經所在的 toc 深度, 巴利藏的定數)
# 定數對不上就是層級判斷錯了 —— 那是硬閘，不是警告。
NIKAYA = {
    "dn": {"vols": (6, 8), "depth": 0, "expect": 34, "zh": "長部"},
    "mn": {"vols": (9, 12), "depth": 2, "expect": 152, "zh": "中部"},
    "sn": {"vols": (13, 18), "depth": 3, "expect": "56 相應", "zh": "相應部"},
}


def n_works(lo: int, hi: int) -> list[str]:
    rows = json.loads(CATALOG.read_text(encoding="utf-8"))
    return [r["id"] for r in sorted(rows, key=lambda r: (r["vol"], r["work_no"]))
            if r["canon"] == "N" and lo <= r["vol"] <= hi]


def bracket_no(head: str) -> int | None:
    """「〔一一〕歡喜園」→ 11。相應部的經號寫在全形方括號裡。"""
    m = re.match(r"^[〔\[]([一二三四五六七八九十百千〇零]+)[〕\]]", head.strip())
    return tpp.cjk_number(m.group(1)) if m else None


def ordinal_no(head: str) -> int | None:
    """「第一　諸天相應」→ 1。"""
    m = re.match(r"^第([一二三四五六七八九十百千〇零]+)", head.strip())
    return tpp.cjk_number(m.group(1)) if m else None


def build_index() -> tuple[dict[str, tuple[str, int]], dict]:
    """SC 巴利 uid（dn1／mn10／sn1.11）→ (N 作品 id, 該經的 toc 節點索引)。"""
    idx: dict[str, tuple[str, int]] = {}
    report: dict[str, dict] = {}

    for nik, cfg in NIKAYA.items():
        works = n_works(*cfg["vols"])
        found = 0
        if nik in ("dn", "mn"):
            # 順序即經號，跨冊連號
            counter = 0
            for wid in works:
                for node in tpp.toc_of(wid):
                    if node["depth"] != cfg["depth"]:
                        continue
                    counter += 1
                    idx[f"{nik}{counter}"] = (wid, node["i"])
            found = counter
        else:
            # 相應部。三個陷阱，都會靜默錯位：
            #   ① 相應號在每冊重新編（N17 從「第八 聚落主相應」開始，
            #      跨篇又跳回「第三 念處相應」）→ 不能讀標題序數，
            #      要跨六冊照文件順序連號。
            #   ② N14 把相應與其下的品放在同一深度，父子鏈斷了
            #      → 不能用 descendants，改用「文件順序上最近的前一個相應」。
            #   ③ 判別相應要看標題結尾是「相應」，不能看深度。
            # 閘：跨六冊剛好 56 個相應（巴利藏的定數），否則整部不掛。
            sam_no = 0
            per_sam: Counter = Counter()
            for wid in works:
                for node in tpp.toc_of(wid):
                    head = node["head"].strip()
                    if node["depth"] <= 1 and head.endswith("相應"):
                        sam_no += 1
                        continue
                    if sam_no == 0:
                        continue
                    sutta = bracket_no(head)
                    if sutta is None:
                        continue
                    key = f"sn{sam_no}.{sutta}"
                    if key not in idx:
                        idx[key] = (wid, node["i"])
                        per_sam[sam_no] += 1
                        found += 1
            report_extra = {"samyuttas": sam_no}
            if sam_no != 56:
                cfg["expect"] = f"56 相應（實得 {sam_no}）"
                found = -1          # 觸發下方的定數不符

        expect = cfg["expect"]
        ok = found >= 0 and (expect is None or not isinstance(expect, int)
                             or found == expect)
        report[nik] = {"zh": cfg["zh"], "works": len(works), "found": found,
                       "expect": expect, "ok": ok,
                       "samyuttas": locals().get("sam_no")}
        if not ok:
            # 定數對不上 → 該尼柯耶整個不掛（把 idx 裡它的條目清掉）
            for k in [k for k in idx if k.startswith(nik)]:
                del idx[k]
    return idx, report


def descendants(toc: list[dict], root: int) -> set[int]:
    """一個 toc 節點與其所有子孫的索引。"""
    kids = defaultdict(list)
    for n in toc:
        if n["parent"] >= 0:
            kids[n["parent"]].append(n["i"])
    out, stack = {root}, [root]
    while stack:
        cur = stack.pop()
        for k in kids.get(cur, []):
            if k not in out:
                out.add(k)
                stack.append(k)
    return out


_SEG_CACHE: dict[str, list[dict]] = {}


def segments_of(work_id: str) -> list[dict]:
    if work_id not in _SEG_CACHE:
        p = SEG_DIR / f"{work_id}.jsonl"
        _SEG_CACHE[work_id] = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()
                               if l.strip()] if p.exists() else []
    return _SEG_CACHE[work_id]


def sutta_lines(work_id: str, node_i: int) -> list[list[str]]:
    """該經在漢譯南傳裡的全部段落 → [[段 uid, 文字], …]。"""
    toc = tpp.toc_of(work_id)
    want = descendants(toc, node_i)
    return [[s["uid"], s["sources"]["lzh"]]
            for s in segments_of(work_id) if s.get("d") in want]


def cmd_audit():
    _idx, report = build_index()
    print(f"{'尼柯耶':8s} {'冊':>3s} {'解出經數':>8s}{'':>10s} {'巴利定數':>12s}  結果")
    print("─" * 78)
    for nik, r in report.items():
        mark = "✓" if r["ok"] else "🚨 數不對，整個尼柯耶不掛"
        exp = r["expect"] if r["expect"] is not None else "—"
        got = r["found"] if r["found"] >= 0 else "—"
        extra = f"（{r['samyuttas']} 相應）" if r.get("samyuttas") else ""
        print(f"{r['zh']:8s} {r['works']:>3d} {str(got):>8s}{extra:>10s} {str(exp):>12s}  {mark}")
    print("─" * 78)
    print("增支部尚未接：集號不在標題層級裡，需另定判別法（見檔頭）。")


def cmd_build():
    idx, report = build_index()
    if not idx:
        sys.exit("索引為空 —— 先跑 --audit 看是哪一層判錯了。")
    rows = [json.loads(l) for l in ROWS.read_text(encoding="utf-8").splitlines() if l.strip()]

    by_work: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    stats = Counter()
    for r in rows:
        if r["lang"] != "pi" or not r.get("seg_uid"):
            continue
        uid = (r.get("uid") or "").split("#")[0].rstrip("-")
        hit = idx.get(uid) or idx.get(uid.split("-")[0])
        if not hit:
            stats["no_zh_nan"] += 1
            continue
        wid_n, node_i = hit
        lines = sutta_lines(wid_n, node_i)
        if not lines:
            stats["empty"] += 1
            continue
        by_work[r["work_id"]][r["seg_uid"]].append({
            "lang": "zh-nan",
            "uid": uid,
            "ref": f"{r['ref']}｜漢譯南傳 {wid_n}",
            "src": "suttacentral",
            "partial": r.get("note") == "部分平行",
            "lines": lines,
        })
        stats["attached"] += 1
        stats["lines"] += len(lines)

    for wid, segs in sorted(by_work.items()):
        out = SEG_DIR / f"{wid}.orig.json"
        existing = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
        for seg, items in segs.items():
            seen, keep = set(), [x for x in existing.get(seg, []) if x.get("lang") != "zh-nan"]
            for it in items:
                if it["uid"] in seen:
                    continue
                seen.add(it["uid"])
                keep.append(it)
            existing[seg] = keep
        out.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")
        n = sum(1 for v in segs.values() for x in v)
        print(f"  ✓ {wid}: {len(segs)} 段掛上 {n} 部漢譯南傳 → {out.name}")

    print(f"\n掛上 {stats['attached']:,} 筆／{stats['lines']:,} 段漢譯南傳，"
          f"涵蓋 {len(by_work)} 部漢文經")
    print(f"  {stats['no_zh_nan']:,} 筆巴利對應在漢譯南傳裡查不到"
          f"（增支部、小部、律藏尚未接）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if a.audit:
        cmd_audit()
    elif a.build:
        cmd_build()
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
