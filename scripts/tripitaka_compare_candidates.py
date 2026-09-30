"""異譯對讀的候選盤點：哪些經有 ≥2 個漢譯本＋至少一個原典在手上。

  巴利系  SuttaCentral parallels.json：整經對整經（不收 `~` 部分平行、不收 `#` 段落級），
          ≥2 個漢譯（阿含的一經或單經譯本）＋ ≥1 部巴利經（sc-data 有逐段本）
  藏譯系  甘珠爾 zh_parallels ≥2（東北目錄，checked 不為 false）＋ 84000 有 TMX
  梵本系  手列（GRETIL 在手、漢譯多本的就那幾部），見 SA_SETS

輸出 C:/tmp/cbeta/compare_candidates.json（中繼，可重跑長回來，不進版控）。
每筆帶各本字數，交給 tripitaka_compare_auto.py 決定整部對還是分品對。

  python -X utf8 scripts/tripitaka_compare_candidates.py
"""
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tripitaka_parallels as tp  # split_uid / resolve_chinese / lang_of 沿用，不另抄一份

SEG = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
SC_ROOT = Path("C:/tmp/cbeta/sc-data/sc_bilara_data/root/pli/ms")
OUT = Path("C:/tmp/cbeta/compare_candidates.json")

# 單經譯本太大就不整部送（交給分品流程）；阿含的一經不會超過
MAX_WHOLE = 40_000

# 梵本系：GRETIL 已在 tripitaka_sanskrit 註冊、且漢譯不只一本者
SA_SETS = [
    {"key": "vimalakirti", "title": "維摩詰經", "works": ["T0474", "T0475", "T0476"], "sa": "T0475", "toh": "toh176"},
    {"key": "saddharmapundarika", "title": "法華經", "works": ["T0263", "T0262", "T0264"], "sa": "T0262", "toh": "toh113"},
    {"key": "dasabhumika", "title": "十地經", "works": ["T0285", "T0286", "T0287"], "sa": "T0286"},
    {"key": "madhyantavibhaga", "title": "辯中邊論頌", "works": ["T1599", "T1600"], "sa": "T1600"},
    {"key": "lalitavistara", "title": "普曜經／方廣大莊嚴經", "works": ["T0186", "T0187"], "sa": "T0187"},
    {"key": "astasahasrika", "title": "八千頌般若", "works": ["T0224", "T0225", "T0226", "T0227", "T0228"], "sa": "T0224"},
]


def chars(work: str, node_uid: str | None = None) -> int:
    p = SEG / f"{work}.jsonl"
    if not p.exists():
        return 0
    rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    if node_uid:
        d = next((r["d"] for r in rows if r["uid"] == node_uid), None)
        rows = [r for r in rows if r["d"] == d]
    return sum(len(r["sources"].get("lzh", "")) for r in rows)


def node_head(work: str, uid: str) -> str | None:
    for n in tp.toc_of(work):
        if n["uid"] == uid:
            return n["head"]
    return None


def pali_files() -> dict[str, Path]:
    return {f.name.split("_")[0]: f for f in SC_ROOT.rglob("*_root-pli-ms.json")}


def pali_family() -> list[dict]:
    files = pali_files()
    groups = json.loads(Path("C:/tmp/cbeta/parallels.json").read_text(encoding="utf-8"))
    seen, out, why = set(), [], Counter()
    for g in groups:
        ents = g.get("parallels")
        if not ents:
            continue
        zh, pi = [], []
        for raw in ents:
            if raw.startswith("~") or "#" in raw:
                continue
            prefix, number, _seg, _p = tp.split_uid(raw)
            if tp.lang_of(prefix) == "pi":
                uid = raw
                if uid in files:
                    pi.append(uid)
                continue
            r = tp.resolve_chinese(prefix, number)
            if not r:
                continue
            wid, seg = r
            if prefix == "t" and seg is None:
                n = chars(wid)
                if not n or n > MAX_WHOLE:
                    why["單經譯本太大或缺"] += 1
                    continue
                zh.append({"work": wid, "uid": raw, "chars": n})
            elif seg:
                head = node_head(wid, seg)
                if not head:
                    continue
                # seg＝該經首段 uid，才是唯一鍵：增一阿含每一品都有「（四）」，靠標題會撞名
                zh.append({"work": wid, "node": head, "seg": seg, "uid": raw, "chars": chars(wid, seg)})
        # 同一部經重複出現（區間 uid）只留一次
        uniq = {(z["work"], z.get("node")): z for z in zh}
        zh = list(uniq.values())
        if len(zh) < 2 or not pi:
            why["漢譯不足兩本或無巴利"] += 1
            continue
        key = tuple(sorted((z["work"], z.get("node") or "") for z in zh))
        if key in seen:
            continue
        seen.add(key)
        out.append({"family": "pi", "pi": sorted(set(pi)), "zh": zh})
    print(f"巴利系 {len(out)} 組  略過 {dict(why)}")
    return out


def tibetan_family() -> list[dict]:
    """甘珠爾的漢譯對照在 Supabase tripitaka_works.zh_parallels；TMX 清單在 84000。"""
    import tripitaka_tibetan as tt
    from dotenv import load_dotenv
    import requests
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    rows, off = [], 0
    while True:  # PostgREST 靜默截 1000 筆，要自己分頁
        r = requests.get(f"{url}/rest/v1/tripitaka_works",
                         params={"select": "id,toh,title_zh,zh_parallels", "canon": "eq.DK",
                                 "order": "id", "limit": 1000, "offset": off},
                         headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=60)
        r.raise_for_status()
        batch = r.json()
        rows += batch
        if len(batch) < 1000:
            break
        off += 1000
    tmx = tt.tmx_files()
    out, why = [], Counter()
    for w in rows:
        par = [p for p in (w.get("zh_parallels") or []) if p.get("checked") is not False]
        toh = f"toh{str(w.get('toh') or '').lower()}"
        if len(par) < 2:
            why["漢譯不足兩本"] += 1
            continue
        if toh not in tmx:
            why["84000 無 TMX"] += 1
            continue
        zh = [{"work": p["id"], "title": p.get("title"), "chars": chars(p["id"])} for p in par]
        zh = [z for z in zh if z["chars"]]
        if len(zh) < 2:
            why["漢譯本不在站上"] += 1
            continue
        out.append({"family": "bo", "dk": w["id"], "toh": toh, "title": w.get("title_zh"), "zh": zh})
    print(f"藏譯系 {len(out)} 組（甘珠爾共 {len(rows)} 部）  略過 {dict(why)}")
    return out


def sanskrit_family() -> list[dict]:
    out = []
    for s in SA_SETS:
        zh = [{"work": w, "chars": chars(w)} for w in s["works"]]
        out.append({"family": "sa", **s, "zh": [z for z in zh if z["chars"]]})
    print(f"梵本系 {len(out)} 組")
    return out


def main():
    cands = pali_family() + tibetan_family() + sanskrit_family()
    OUT.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    big = sum(1 for c in cands if max(z["chars"] for z in c["zh"]) > MAX_WHOLE)
    print(f"共 {len(cands)} 組（其中 {big} 組有本子超過 {MAX_WHOLE:,} 字，要分品）→ {OUT}")


if __name__ == "__main__":
    main()
