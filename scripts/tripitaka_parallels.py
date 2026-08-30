"""佛教大藏經 /tripitaka —— 漢文 ↔ 梵／巴／藏 的平行經目對接。

三個來源，權威度由高到低，**入庫時分開標記，UI 分色，不可混為一談**：

  taisho-equiv   大正藏編者（1924–34）在經文腳註標出的巴利對應。
                 由 tripitaka_cbeta.py 從 <cb:div type="equiv-notes"> 抽出，
                 且靠正文內的 anchor 貼回確切段落。全藏 1,597 條、21 部。
  suttacentral   SuttaCentral relationship/parallels.json —— 5,652 組平行經目，
                 涵蓋巴利、漢譯阿含、梵文殘卷（sf）與藏譯（d / up）。經號級。
  cbeta-term     CBETA <cb:tt> 專名旁的梵巴原語形。逐詞而非逐段，另存詞條層。

對得到什麼層級，取決於文類（見 SKILL.md「對齊軸」）：
  阿含類 → 經（SC 的 sa1267 ↔ CBETA <cb:div type="jing"> n="1267"）
  其餘   → 至多對到品；SC 用 t{N} 直接指大正藏經號時只能對到整部。

  python scripts/tripitaka_parallels.py --fetch            # 抓 SC 資料
  python scripts/tripitaka_parallels.py --audit            # 對得上多少（不寫）
  python scripts/tripitaka_parallels.py --build            # 產出 parallels.jsonl
  python scripts/tripitaka_parallels.py --push             # → tripitaka_parallels
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import tripitaka_cbeta as tc  # noqa: E402

CACHE = Path(os.environ.get("SC_CACHE", "C:/tmp/cbeta"))
SEG_DIR = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
SC_RAW = "https://raw.githubusercontent.com/suttacentral/sc-data/main/"
OUT = CACHE / "parallels_rows.jsonl"

# ── SuttaCentral 集號 → 大正藏作品 ──────────────────────────
# 只列真的能對到 CBETA 單一作品者。ea-2 等散在多部的暫不映射。
SC_TO_TAISHO = {
    "da": "T0001",     # 長阿含經
    "ma": "T0026",     # 中阿含經
    "sa": "T0099",     # 雜阿含經
    "sa-2": "T0100",   # 別譯雜阿含經
    "sa-3": "T0101",   # 雜阿含經（一卷本）
    "ea": "T0125",     # 增壹阿含經
}
# split_uid 的最長前綴表：長的排前面，sa-2 要贏過 sa
_KNOWN_PREFIXES = sorted(
    list(SC_TO_TAISHO) + ["ea-2", "ea-3", "ma-2", "da-2", "t", "d", "up", "uv-kg",
                          "uv", "uvs", "sf", "sag"],
    key=len, reverse=True)
# SC 的語言分群：決定該筆對照落在哪一欄
LANG_OF_PREFIX = {
    # 巴利三藏
    **{p: "pi" for p in ("dn", "mn", "sn", "an", "kp", "dhp", "ud", "iti", "snp",
                         "vv", "pv", "thag", "thig", "tha-ap", "thi-ap", "bv",
                         "cp", "ja", "mnd", "cnd", "ps", "ne", "pe", "mil",
                         "vb", "dt", "pp", "kv", "ds", "ya", "patthana")},
    # 梵文（阿含殘卷、優陀那品、吐魯番寫本、譬喻文學、其他梵本）
    **{p: "sa" for p in ("sf", "san", "skt", "arv", "divy", "sag", "uv", "uvs",
                         "sht-sutta", "sht", "avs", "lal", "mvu", "sn-kg")},
    # 中期印度語（犍陀羅語／波特那法句經）—— 既非梵文也非巴利，
    # 混進「梵文」欄是語言學上的錯誤，另立一欄。
    **{p: "pra" for p in ("gdhp", "pdhp", "g", "pra")},
    # 藏譯（德格版、甘珠爾、俱舍論疏所引）
    **{p: "bo" for p in ("d", "up", "uv-kg", "xct")},
}

# SC 的律典 uid 是複合式：`lzh-mi-bi-vb-pc12`
#   = 語言(lzh 漢／san 梵／xct 藏／pli 巴) - 部派 - 比丘尼 - 犍度類 - 學處類 條號
# 第一段決定語言，第二段（部派）決定對應到哪一部漢譯廣律。
VINAYA_LANG = {"lzh": None, "san": "sa", "xct": "bo", "pli": "pi", "pra": "sa"}
# 部派 → 漢譯廣律（大正藏律部）
VINAYA_SCHOOL_TO_TAISHO = {
    "dg": "T1428",    # 法藏部 → 四分律
    "mi": "T1421",    # 化地部 → 五分律
    "mg": "T1425",    # 大眾部 → 摩訶僧祇律
    "sarv": "T1435",  # 說一切有部 → 十誦律
    "mu": "T1442",    # 根本說一切有部 → 根本說一切有部毘奈耶
    "tv": None,       # 上座部＝巴利律藏，無漢譯廣律
}


def fetch(name: str) -> Path:
    dst = CACHE / name.replace("/", "_")
    if dst.exists() and dst.stat().st_size > 0:
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(SC_RAW + name, timeout=180) as r:
        dst.write_bytes(r.read())
    return dst


def split_uid(raw: str) -> tuple[str, str, str, bool]:
    """'~sa1267#3.1' → (prefix, number, segment-range, partial?)

    '~' 前綴＝部分平行（SC 的標記），必須保留 —— 把部分平行當成完整對應
    是這類資料最容易犯的誇大。

    🚨 `sa-2.180` 是「別譯雜阿含第 180 經」，不是「雜阿含 2.180」。
    純用正規式切前綴會把它併進 sa，整批 380 筆對到錯的經。
    因此先用已知集號做最長前綴比對。
    """
    partial = raw.startswith("~")
    body = raw.lstrip("~")
    uid, _, seg = body.partition("#")
    for known in _KNOWN_PREFIXES:            # 長的先比：sa-2 要贏過 sa
        if not uid.startswith(known):
            continue
        rest = uid[len(known):]
        # 後面必須直接接編號（數字或小數點）；'sa' 不可吃掉 'sa-2.180' 的 '-'
        if rest == "" or rest[0].isdigit() or rest[0] == ".":
            return known, rest, seg, partial
    m = re.match(r"^([a-z][a-z-]*?)(\d.*)?$", uid)
    if not m:
        return uid, "", seg, partial
    return m.group(1).rstrip("-") or uid, (m.group(2) or ""), seg, partial


# ── 漢數字經號 ────────────────────────────────────────────
_CJK_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
              "六": 6, "七": 7, "八": 8, "九": 9}


def cjk_number(s: str) -> int | None:
    """大正藏標題的經號：「（二二二）」＝222、「（三〇）」＝30、「（十）」＝10。

    大正藏多用「逐位排列」（二二二 = 222）而非「十百進位」（二百二十二），
    但少數用進位式，兩種都要吃。
    """
    s = s.strip()
    if not s:
        return None
    if any(c in s for c in "十百千"):
        total, cur = 0, 0
        for c in s:
            if c in _CJK_DIGIT:
                cur = _CJK_DIGIT[c]
            elif c == "十":
                total += (cur or 1) * 10
                cur = 0
            elif c == "百":
                total += (cur or 1) * 100
                cur = 0
            elif c == "千":
                total += (cur or 1) * 1000
                cur = 0
            else:
                return None
        return total + cur
    if all(c in _CJK_DIGIT for c in s):
        return int("".join(str(_CJK_DIGIT[c]) for c in s))
    return None


def head_sutta_no(head: str) -> int | None:
    """「（二二二）中阿含例品例經第十一」→ 222。取開頭全形括號內的漢數字。"""
    m = re.match(r"^[（(]([一二三四五六七八九十百千〇零]+)[)）]", head.strip())
    return cjk_number(m.group(1)) if m else None


def label_of(prefix: str, number: str, names: dict[str, str]) -> str:
    """'sn', '22.12' → 'SN 22.12（Saṁyutta Nikāya）'"""
    nice = names.get(prefix, prefix)
    acro = prefix.upper() if len(prefix) <= 4 else prefix
    return f"{acro} {number}".strip() + (f"（{nice}）" if nice != prefix else "")


def load_names() -> dict[str, str]:
    d = json.loads(fetch("misc/uid_expansion.json").read_text(encoding="utf-8"))
    return {e["uid"]: e.get("name", "") for e in d if e.get("uid")}


# ── 漢文側：經號 → 段 ────────────────────────────────────────
_TOC_CACHE: dict[str, list[dict]] = {}


def toc_of(work_id: str) -> list[dict]:
    if work_id not in _TOC_CACHE:
        p = SEG_DIR / f"{work_id}.toc.json"
        _TOC_CACHE[work_id] = (
            json.loads(p.read_text(encoding="utf-8"))["toc"] if p.exists() else []
        )
    return _TOC_CACHE[work_id]


_SUTTA_INDEX: dict[str, dict[str, str]] = {}


def sutta_index(work_id: str) -> dict[str, str]:
    """一部阿含的「SC 經號 → 段」索引。

    四部阿含在 CBETA 裡的編號方式各不相同，硬套一種會整批對錯：
      T0001 長阿含  jing 的 n 是空的，經號寫在標題「（一）」裡           → 1..30
      T0026 中阿含  同上                                                → 1..222
      T0099 雜阿含  jing 的 n 直接就是經號                              → 1..1362
      T0100 別譯雜  連 jing 都沒有，是 type="other"，經號同樣在標題      → 1..364
      T0125 增壹阿含 n 是「品內序號」，SC 用「品.經」（ea32.2）          → 品號.經號
    """
    if work_id in _SUTTA_INDEX:
        return _SUTTA_INDEX[work_id]
    toc = toc_of(work_id)
    idx: dict[str, str] = {}
    for node in toc:
        t = node.get("type")
        if work_id == "T0125":
            # 增壹阿含：往上找所屬的品，組成「品.經」
            if t != "jing":
                continue
            parent = node.get("parent", -1)
            pin = toc[parent] if 0 <= parent < len(toc) else None
            if pin and pin.get("type") == "pin" and pin.get("n") and node.get("n"):
                idx.setdefault(f"{pin['n']}.{node['n']}", node["uid"])
            continue
        if t not in ("jing", "other"):
            continue
        n = node.get("n")
        if n and str(n).isdigit():
            idx.setdefault(str(int(n)), node["uid"])
            continue
        no = head_sutta_no(node.get("head") or "")
        if no is not None:
            idx.setdefault(str(no), node["uid"])
    _SUTTA_INDEX[work_id] = idx
    return idx


def jing_seg(work_id: str, number: str) -> str | None:
    """SC 的經號 → 該經在漢文本裡的起始段。對不上回 None（寧可少收，不硬湊）。"""
    if not number:
        return None
    want = number.strip().lstrip(".")
    idx = sutta_index(work_id)
    if want in idx:
        return idx[want]
    # 範圍式編號：'sa1060-1061'、'ea4.1-10'、'ma107-108' 指一段連續的經。
    # 取起點那一經 —— 對照從那裡開始讀是對的，硬拆成多筆反而虛胖。
    if "-" in want:
        start = want.split("-")[0]
        if start in idx:
            return idx[start]
    # 「32.2」在非增壹阿含的本子裡＝第 32 經（SC 偶爾帶小數層級）
    head = want.split(".")[0].split("-")[0]
    return idx.get(head)


def pin_seg(work_id: str, pin_no: str | None) -> str | None:
    """品號 → 該品的起始段。品（梵 parivarta／藏 le'u）是跨語言主對齊層。"""
    if not pin_no:
        return None
    for node in toc_of(work_id):
        if node.get("type") == "pin" and str(node.get("n") or "") == str(int(pin_no)):
            return node["uid"]
    return None


_WORK_IDS: dict[str, str] | None = None


def canonical_work_id(guess: str) -> str | None:
    """把猜出來的作品 id 對回 CBETA 的正規寫法；查無則回 None。

    🚨 CBETA 的字母後綴**兩種大小寫都用**（T0128a／T0128b 小寫，
    T1670B／T2917A 大寫），不能一律轉大寫，也不能照 SC uid 的小寫直接用。
    而 Windows 檔名不分大小寫 —— 拿「檔案存在」當檢查會讓 `T1670b` 通過，
    寫進 DB 才撞外鍵。故一律對照真實目錄查正規 id。
    """
    global _WORK_IDS
    if _WORK_IDS is None:
        _WORK_IDS = {}
        for p in SEG_DIR.glob("*.toc.json"):
            wid = p.name[: -len(".toc.json")]
            _WORK_IDS[wid.lower()] = wid
    return _WORK_IDS.get(guess.lower())


def vinaya_parts(prefix: str) -> tuple[str | None, str | None]:
    """'lzh-mi-bi-vb-pc' → ('lzh', 'mi')；非律典 uid 回 (None, None)。"""
    bits = prefix.split("-")
    if len(bits) < 2 or bits[0] not in VINAYA_LANG:
        return None, None
    return bits[0], bits[1]


def lang_of(prefix: str) -> str | None:
    """決定一個 SC uid 屬於哪一語言欄。複合律典 uid 看第一段。"""
    if prefix in LANG_OF_PREFIX:
        return LANG_OF_PREFIX[prefix]
    lang, _school = vinaya_parts(prefix)
    if lang:
        return VINAYA_LANG[lang]      # lzh 回 None（那是漢文側，不是對照欄）
    return None


def resolve_chinese(prefix: str, number: str) -> tuple[str, str | None] | None:
    """SC uid → (大正藏作品 id, 段 or None)。對不到作品回 None。"""
    if prefix in SC_TO_TAISHO:
        wid = SC_TO_TAISHO[prefix]
        return wid, jing_seg(wid, number)
    if prefix == "t" and number:
        # 't213.4' ＝ 大正藏第 213 經第 4 品。只取 213 會把法句經群那四千多筆
        # 逐品對照全塌成「整部」—— 品號要用上，那正是跨語言的主對齊層。
        m = re.match(r"^(\d+)([A-Za-z]?)(?:\.(\d+))?", number)
        if m:
            wid = canonical_work_id(f"T{int(m.group(1)):04d}{m.group(2)}")
            if not wid:
                return None
            return wid, (pin_seg(wid, m.group(3)) if m.group(3) else None)
    # 漢譯廣律：lzh-{部派}-… → 該部派的漢譯廣律（只能對到整部，
    # 學處條號在 CBETA 的目錄樹裡沒有可對的鍵）
    lang, school = vinaya_parts(prefix)
    if lang == "lzh" and school:
        wid = canonical_work_id(VINAYA_SCHOOL_TO_TAISHO.get(school) or "")
        if wid:
            return wid, None
    return None


# ── 主流程 ──────────────────────────────────────────────────
def build(audit_only: bool) -> list[dict]:
    names = load_names()
    groups = json.loads(fetch("relationship/parallels.json").read_text(encoding="utf-8"))
    rows: list[dict] = []
    stats = Counter()
    unmapped = Counter()
    dropped = Counter()

    for g in groups:
        kind = next((k for k in ("parallels", "mentions", "retells") if k in g), None)
        if kind != "parallels":          # mentions/retells 不是平行本，不入對照欄
            stats["skip_non_parallel"] += 1
            continue
        members = [split_uid(str(x)) for x in g[kind]]
        chinese = []
        foreign = []
        for prefix, number, seg, partial in members:
            hit = resolve_chinese(prefix, number)
            if hit:
                chinese.append((hit[0], hit[1], prefix, number, partial))
            else:
                lang = lang_of(prefix)
                if lang:
                    foreign.append((lang, prefix, number, seg, partial))
                else:
                    unmapped[prefix] += 1
        if not chinese or not foreign:
            stats["no_pair"] += 1
            continue
        for wid, cseg, cp, cn, cpart in chinese:
            # 收錄門檻：對得到段落就收；對不到段落時，只有當漢文那一側
            # 本來就是「整部」的指稱（SC 的 t{N}）才收。
            #
            # 否則會出現這種假資料：律典的 uid 是逐條學處（lzh-mi-bi-vb-pc12），
            # 對不到段落時全部塌成「十誦律 ↔ 巴利律藏」，同一句話重複三萬七千次。
            # 那不是對照，是噪音。捨棄的筆數在下方明列，不靜默丟。
            if not cseg and cp != "t":
                stats["dropped_collapsed_to_work"] += len(foreign)
                dropped[cp] += len(foreign)
                continue
            for lang, prefix, number, fseg, fpart in foreign:
                rows.append({
                    "work_id": wid,
                    "seg_uid": cseg,
                    "level": "seg" if cseg else "work",
                    "cn_ref": f"{cp}{cn}",
                    "lang": lang,
                    "ref": label_of(prefix, number, names),
                    "uid": prefix + number + (f"#{fseg}" if fseg else ""),
                    "src": "suttacentral",
                    "note": "部分平行" if (cpart or fpart) else None,
                })
                stats[f"lang_{lang}"] += 1
                stats["seg_level" if cseg else "work_level"] += 1

    print(f"平行組 {len(groups):,}　產出對照 {len(rows):,} 筆")
    for k, v in sorted(stats.items()):
        print(f"  {k:20s} {v:,}")
    print("  對得到段落的比例: "
          f"{stats['seg_level'] / max(1, stats['seg_level'] + stats['work_level']):.1%}")
    if dropped:
        print("  捨棄（漢文側是逐條／逐經指稱但對不到段落，塌成整部無意義）:")
        for k, v in dropped.most_common(8):
            print(f"    {k:24s} {v:,}")
    if unmapped:
        print("  未映射的集號（前 12）:", dict(unmapped.most_common(12)))

    by_work = Counter(r["work_id"] for r in rows)
    print(f"  涵蓋 {len(by_work)} 部；最多者:",
          ", ".join(f"{w}={n}" for w, n in by_work.most_common(6)))
    return [] if audit_only else rows


def cmd_build():
    rows = build(audit_only=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"✓ {len(rows):,} 筆 → {OUT}")


def cmd_push():
    import tripitaka_db as td
    rows = [json.loads(l) for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()]
    # 大正藏原註那一層也一併推（每部經的 .equiv.json，已含 seg）
    for p in sorted(SEG_DIR.glob("*.equiv.json")):
        wid = p.name.split(".")[0]
        for e in json.loads(p.read_text(encoding="utf-8")):
            rows.append({"work_id": wid, "seg_uid": e.get("uid"), "lang": "pi",
                         "ref": e["ref"], "src": "taisho-equiv", "note": None})
    # 同一漢文段可能從兩個平行組收到同一筆對應（例：一經同時是甲乙兩部漢譯的
    # 平行本）。同批次出現重複的唯一鍵，PostgREST 的 upsert 會回 21000
    # 「cannot affect row a second time」—— 推之前先去重。
    seen: set[tuple] = set()
    payload = []
    for r in rows:
        rec = {**{k: r.get(k) for k in ("work_id", "seg_uid", "lang", "ref", "src", "note")},
               "seg_uid": r.get("seg_uid") or ""}       # 整部層級用空字串，見 schema 註
        key = (rec["work_id"], rec["seg_uid"], rec["lang"], rec["ref"], rec["src"])
        if key in seen:
            continue
        seen.add(key)
        payload.append(rec)
    print(f"去重後 {len(payload):,} 筆（原 {len(rows):,}）", flush=True)
    for i in range(0, len(payload), 500):
        td.postgrest("tripitaka_parallels?on_conflict=work_id,seg_uid,lang,ref,src",
                     payload[i:i + 500])
        print(f"  … {min(i + 500, len(payload))}/{len(payload)}", flush=True)
    print(f"✓ tripitaka_parallels {len(payload):,} 筆")

    # 回填每部經有哪些對照語言，供列表頁的標籤。
    # 不用 PostgREST 的 upsert：那是 INSERT…ON CONFLICT，只給三個欄位會撞
    # tripitaka_works 的 NOT NULL（回 409）。直接下 UPDATE…FROM 才對。
    n = td.pg_exec("""
        update tripitaka_works w
           set parallel_langs = s.langs,
               parallel_count = s.n
          from (select work_id,
                       array_agg(distinct lang order by lang) as langs,
                       count(*) as n
                  from tripitaka_parallels group by work_id) s
         where w.id = s.work_id
     returning w.id
    """)
    print(f"✓ 回填 {len(n)} 部的 parallel_langs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    if a.fetch:
        for n in ("relationship/parallels.json", "misc/uid_expansion.json"):
            print("✓", fetch(n))
    if a.audit:
        build(audit_only=True)
    if a.build:
        cmd_build()
    if a.push:
        cmd_push()
    if not any(vars(a).values()):
        ap.print_help()


if __name__ == "__main__":
    main()
