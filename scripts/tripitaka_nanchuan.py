"""佛教大藏經 /tripitaka —— 把《漢譯南傳大藏經》掛成漢譯阿含的對照欄。

漢譯阿含旁邊擺巴利羅馬字，對多數讀者用處有限；擺**同一部巴利經的現代漢譯**
（元亨寺版），才看得出同一則教說在南北兩傳的差別。這是使用者點名要的一欄。

🚨 五尼柯耶在元亨寺版的編號方式各不相同，硬套一種會整批錯位：

    長部  N06–N08  經在 depth 0，順序即 DN 1..34
    中部  N09–N12  篇 › 品 › 經，經在 depth 2，順序即 MN 1..152
    相應部 N13–N18 相應(d1)「第一　諸天相應」› 品(d2) › 經(d3)「〔一一〕歡喜園」
                   ⚠ 〔n〕**跨品連號**（葦品〔一〕–〔一〇〕、歡喜園品〔一一〕–〔二〇〕），
                     與巴利 SN 1.1–1.10 / 1.11–1.20 一致 → 鍵為「相應.經」
    增支部 N19–N25 **不接**。理由不是沒試，是兩種判準都對不上定數（見下）：
                   ① 「經號歸零＝新的一集」→ 得 9 集
                   ② 同上但不看深度、排除「第…品」→ 得 15 集
                   定數是 11。原因是集號標記時有時無（每冊第一個集併在書名
                   節點裡，且一個集可跨冊：N25 的第一個 d0 是集十的延續，
                   經號從六十一起），而經節點的深度逐冊不同（N22 有 d4、
                   N23 有 d5），d5 那些小群組還會造成假的歸零。
                   要接得先逐冊人工核定集界，不是調參數能解決的。

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


# 小部（N26–N47）各書自成一個 N 作品，結構互異，逐本指定判別法。
# `suttas`／`vaggas` 是巴利藏的定數，對不上就該書不掛。
KHUDDAKA = {
    "ud":  {"work": "N26n0010", "form": "vagga.sutta", "vaggas": 8, "suttas": 80,
            "zh": "自說經"},
    "snp": {"work": "N27n0012", "form": "vagga.sutta", "vaggas": 5, "suttas": 72,
            "zh": "經集"},
    # `depth` 要逐本指定：如是語的經在 d1（d0 是十一個品），
    # 小誦經卻全在 d0。用同一個深度會一本全對、另一本全空。
    "iti": {"work": "N26n0011", "form": "sequential", "depth": 1,
            "suttas": 112, "zh": "如是語經"},
    "kp":  {"work": "N26n0008", "form": "sequential", "depth": 0,
            "suttas": 9, "zh": "小誦經"},
    # 法句經的 SC uid 是**偈頌號**（1–423）不是品號，要先把偈頌號換算成品。
    # 換算表不自己寫死：SuttaCentral 的檔名本身就是品的偈頌區間
    # （dhp1-20＝第一品、dhp21-32＝第二品…dhp383-423＝第二六品，恰好 26 個），
    # 直接讀那 26 個檔名，比抄一張表可靠。
    "dhp": {"work": "N26n0009", "form": "dhp-verse", "vaggas": 26, "zh": "法句經"},
}
SC_DHP_DIR = Path(os.environ.get(
    "SC_DATA", "C:/tmp/cbeta/sc-data/sc_bilara_data")) / "root/pli/ms/sutta/kn/dhp"


def dhp_verse_to_vagga() -> dict[int, int]:
    """法句偈頌號 → 品號。區間取自 SuttaCentral 的檔名，不自己寫死。"""
    ranges = []
    for p in SC_DHP_DIR.glob("dhp*-*_root-pli-ms.json"):
        m = re.match(r"^dhp(\d+)-(\d+)$", p.name.split("_")[0])
        if m:
            ranges.append((int(m.group(1)), int(m.group(2))))
    ranges.sort()
    out: dict[int, int] = {}
    for i, (lo, hi) in enumerate(ranges, start=1):
        for v in range(lo, hi + 1):
            out[v] = i
    return out


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


def belongs_to(key: str, prefix: str) -> bool:
    """key 是否屬於某個集號。

    🚨 純用 startswith 會讓 `snp1.1`（經集）被判成 `sn`（相應部）的條目 ——
    相應部若被閘擋下，清理時會把經集一起刪掉。前綴後面必須直接接編號。
    （與 tripitaka_parallels.split_uid 裡 `sa` 不可吃掉 `sa-2` 是同一類錯。）
    """
    if not key.startswith(prefix):
        return False
    rest = key[len(prefix):]
    return rest[:1].isdigit() or rest[:1] == "."


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
            for k in [k for k in idx if belongs_to(k, nik)]:
                del idx[k]

    # ── 小部：每本書自成一個 N 作品，逐本判別 ──────────────
    for pref, cfg in KHUDDAKA.items():
        wid = cfg["work"]
        toc = tpp.toc_of(wid)
        local: dict[str, tuple[str, int]] = {}
        vaggas = 0

        if cfg["form"] == "sequential":
            # ⚠ 第一單元沒有編號，併在書名節點裡（「小誦經」＝第一三歸文、
            # 「法句經」＝第一雙品），其餘才從「二」起編。故照文件順序連號，
            # 不要讀標題裡的數字。
            for node in toc:
                if node["depth"] != cfg["depth"]:
                    continue
                local[f"{pref}{len(local) + 1}"] = (wid, node["i"])
        elif cfg["form"] == "vagga.sutta":
            # 品界＝ depth 0 的節點（第一個就是書名兼第一品，
            # 自說經的「自說經」即第一品菩提品、經集的「經集」即第一品蛇品）。
            # 經號**每品重編**（一–一〇），所以鍵直接是「品.經」。
            for node in toc:
                if node["depth"] == 0:
                    vaggas += 1
                    continue
                no = ordinal_no(node["head"]) or bracket_no(node["head"])                     or tpp.cjk_number(node["head"].split()[0].strip("　"))
                if no and vaggas:
                    local.setdefault(f"{pref}{vaggas}.{no}", (wid, node["i"]))
        elif cfg["form"] == "dhp-verse":
            v2v = dhp_verse_to_vagga()
            # 品節點散在 depth 0 與 1（第一、二品在 d0，其餘在 d1），且第一品
            # 「雙品」沒有編號、併在書名節點裡 —— 所以既不能看深度、也不能讀
            # 標題數字，照文件順序連號才對（全部 26 個節點即 26 品）。
            vagga_nodes = list(toc)
            vaggas = len(vagga_nodes)
            if vaggas == cfg["vaggas"]:
                by_no = {i + 1: n for i, n in enumerate(vagga_nodes)}
                for verse, vg in v2v.items():
                    node = by_no.get(vg)
                    if node:
                        local[f"dhp{verse}"] = (wid, node["i"])

        exp_s, exp_v = cfg.get("suttas"), cfg.get("vaggas")
        n_suttas = len(local) if cfg["form"] != "dhp-verse" else vaggas
        target = exp_s if cfg["form"] != "dhp-verse" else exp_v
        ok = target is None or n_suttas == target
        if ok:
            idx.update(local)
        report[pref] = {"zh": cfg["zh"], "works": 1, "found": n_suttas,
                        "expect": target, "ok": ok, "samyuttas": None,
                        "khuddaka": True}
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
    print("增支部（1,975 筆對應）不接：兩種判準分別得 9 集與 15 集，定數是 11。")
    print("  集號標記時有時無、集可跨冊、經節點深度逐冊不同 —— 詳見檔頭。")
    print("  硬湊會在約 2,000 筆對應上產生看起來對、其實錯的結果。")


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
          f"（增支部見檔頭；律藏、譬喻經、本生經、長老偈尼偈尚未接）")


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
