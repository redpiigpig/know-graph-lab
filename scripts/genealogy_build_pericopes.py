"""以 ACCS 的段落總論（accs_commentary.section_kind='overview'）為界線，建新約段落骨架。

    python scripts/genealogy_build_pericopes.py

為什麼用 ACCS 的分段而不自己切：那是《古代基督信仰聖經註釋叢書》出版時
的段落劃分，有出處、可覆核，而且每段自帶中文標題。自己切 700 段沒有任何
人能驗證界線對不對。

輸出 data/christian-genealogy/nt-pericopes.json：
  { book: [ {v_from:[ch,v], v_to:[ch,v], title, verses, gap:bool} ] }
未被任何 overview 蓋到的節，另立 gap 段（標題留空待補），確保逐節 100% 有段。
"""
import json
from collections import defaultdict
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
IDX = ROOT / "data/christian-genealogy/nt-verse-index.json"
OUT = ROOT / "data/christian-genealogy/nt-pericopes.json"

NT = "mat mrk luk jhn act rom 1co 2co gal eph php col 1th 2th 1ti 2ti tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev".split()


def env():
    return dict(
        l.strip().split("=", 1)
        for l in (ROOT / ".env").read_text(encoding="utf-8").splitlines()
        if "=" in l and not l.startswith("#")
    )


def fetch_overviews(e):
    url, key = e["SUPABASE_URL"].strip(), e["SUPABASE_SERVICE_ROLE_KEY"].strip()
    h = {"apikey": key, "Authorization": "Bearer " + key}
    rows, off = [], 0
    while True:
        r = requests.get(
            f"{url}/rest/v1/accs_commentary?select=book_code,chapter,verse_start,verse_end,heading"
            f"&section_kind=eq.overview&order=id&limit=1000&offset={off}", headers=h)
        b = r.json()
        # 🚨 查詢壞掉時 PostgREST 回 dict，直接 break 會讓分母變 0 看起來像「沒有資料」
        if not isinstance(b, list):
            raise SystemExit(f"accs_commentary 查詢失敗：{b}")
        if not b:
            break
        rows += b
        off += len(b)
        if len(b) < 1000:
            break
    return rows


def main():
    idx = json.loads(IDX.read_text(encoding="utf-8"))["books"]
    ovs = fetch_overviews(env())
    print(f"ACCS overview 列：{len(ovs)}")

    by_book = defaultdict(list)
    for x in ovs:
        if x["book_code"] not in NT:
            continue
        c, v1 = x["chapter"], x["verse_start"]
        v2 = x["verse_end"] or v1
        by_book[x["book_code"]].append((c, v1, v2, (x["heading"] or "").strip()))

    out, tally = {}, []
    for code in NT:
        verses = []  # 該卷所有節，依序
        for ch in sorted(idx[code]["chapters"], key=int):
            for v in idx[code]["chapters"][ch]:
                verses.append((int(ch), v))
        # 🚨 ACCS 的總論是巢狀重疊的（章級總論套著小段總論），直接相加會重複
        #    計節（第一版算出 112% 覆蓋）。改為：每一節指派給「包住它的最短範圍」，
        #    再把連續同屬一段的節併起來，得到互不重疊的分割。
        ranges = sorted(set(by_book[code]))
        assign = {}
        for cv in verses:
            best = None
            for c, v1, v2, head in ranges:
                if c == cv[0] and v1 <= cv[1] <= v2:
                    span = v2 - v1
                    if best is None or span < best[0]:
                        best = (span, (c, v1, v2, head))
            if best:
                assign[cv] = best[1]
        segs = []
        cur = None
        for cv in verses:
            key = assign.get(cv)
            if cur and cur["key"] == key and cur["to"][0] == cv[0] and cur["to"][1] == cv[1] - 1:
                cur["to"] = list(cv)
                cur["verses"] += 1
                continue
            if cur:
                segs.append(cur)
            cur = {"key": key, "from": list(cv), "to": list(cv), "verses": 1,
                   "title": (key[3] or None) if key else None,
                   "source": "accs" if key else "gap"}
        if cur:
            segs.append(cur)
        for sgm in segs:
            sgm.pop("key", None)
        segs.sort(key=lambda s: (s["from"][0], s["from"][1]))
        out[code] = segs
        acc = sum(s["verses"] for s in segs if s["source"] == "accs")
        gap = sum(s["verses"] for s in segs if s["source"] == "gap")
        tally.append((code, idx[code]["name_zh"], len(segs), acc, gap, len(verses)))

    total_v = sum(t[5] for t in tally)
    total_a = sum(t[3] for t in tally)
    total_g = sum(t[4] for t in tally)
    total_s = sum(t[2] for t in tally)

    OUT.write_text(json.dumps({
        "meta": {
            "title": "新約段落骨架（ACCS 分段）",
            "boundary_source": "accs_commentary section_kind='overview'（《古代基督信仰聖經註釋叢書》的段落總論）",
            "verse_index": "data/christian-genealogy/nt-verse-index.json",
            "generated_by": "scripts/genealogy_build_pericopes.py",
            "counts": {"segments": total_s, "verses": total_v,
                       "from_accs": total_a, "gap_filled": total_g},
            "note": "gap 段是 ACCS 未分段之處，標題留空待補；它們存在是為了保證逐節 100% 落在某一段內",
        },
        "books": out,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{'卷':<5}{'段':>5}{'ACCS 蓋到':>10}{'補 gap':>8}{'全卷節':>8}{'覆蓋':>7}")
    for code, name, segs, acc, gap, tot in tally:
        print(f"{code:<5}{segs:>5}{acc:>10}{gap:>8}{tot:>8}{acc/tot*100:>6.0f}%")
    print(f"\n合計：{total_s} 段，{total_v} 節")
    print(f"  ACCS 分段直接蓋到 {total_a} 節（{total_a/total_v*100:.1f}%）")
    print(f"  補 gap 段         {total_g} 節（{total_g/total_v*100:.1f}%）")
    print(f"  逐節落段率        {(total_a+total_g)/total_v*100:.1f}%")
    print("寫出 →", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
