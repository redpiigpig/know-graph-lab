"""佛教大藏經 /tripitaka —— 梵文原典（GRETIL）掛到漢譯品上。

SuttaCentral 幾乎沒有梵文（root/san 只 2 檔），梵本要另從 GRETIL 取
（gretil.sub.uni-goettingen.de，TEI XML，194 部佛教梵本）。

🚨 這一支最危險的錯是「照品序對齊」。
   法華梵本 27 品、羅什漢譯 28 品（提婆達多品在梵本併入見寶塔品），
   照順序對會讓第 12 品以後**全體位移一格**，而且頁面看起來完全正常。
   所以本檔的規矩是：

     品數不合 → 拒絕逐品對齊，退回整部層級，並在稽核輸出中明列。
     要逐品對，就得在 REGISTRY 裡手寫該部的品對照表（chapter_map）。

   絕不用「長度差不多就湊」的啟發式。

GRETIL 把結構編號嵌在正文裡，每部書一個縮寫（siglum）：
   中論   `// MMK_1.1 //`      品.頌
   法華   `Saddhp_1: nidāna…`  品
   十地經 `Dbh_1`              品
故 REGISTRY 每一筆要指定該書的 siglum 與編號形態。

  python scripts/tripitaka_sanskrit.py --audit          # 梵品數 vs 漢品數（不寫）
  python scripts/tripitaka_sanskrit.py --build
  python scripts/tripitaka_sanskrit.py --build --only T1564
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import tripitaka_parallels as tpp  # noqa: E402

GRETIL_RAW = "https://gretil.sub.uni-goettingen.de/gretil/corpustei/{}.xml"
CACHE = Path(os.environ.get("GRETIL_CACHE", "C:/tmp/cbeta/gretil"))
SEG_DIR = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
TEI = "http://www.tei-c.org/ns/1.0"


# ─────────────────────────────────────────────────────────────
# 策展表。每一筆都要人工確認過梵漢確為同一部書的對譯，
# 不是靠書名相似猜的。chapter_map 只有在梵漢品數不同時才需要。
# ─────────────────────────────────────────────────────────────
REGISTRY: list[dict] = [
    # ── 中觀部 ──
    {"file": "sa_nAgArjuna-mUlamadhyamakakArikA", "work": "T1564",
     "zh": "中論", "sa": "Mūlamadhyamakakārikā", "siglum": "MMK",
     "form": "chapter.verse"},

    # ── 法華部 ──
    # 🚨 這張表不是「梵 12 起加一」那麼簡單，第一版就是那樣寫而錯了 4 個品。
    # 梵／藏本 27 品，羅什本 28 品，差異有兩處而非一處：
    #   ① 提婆達多品（漢 12）在梵本併入見寶塔品（梵 11）→ 之後位移一格
    #   ② 羅什把**囑累品移到第 22**、陀羅尼品排到第 26，梵藏本則
    #      陀羅尼在 21、囑累在最末 27 → 尾段七品的次序完全不同
    # 下表的梵本品名取自 GRETIL 的 `Saddhp_N:` 標記、漢本品名取自 CBETA 目錄，
    # 兩邊逐一核對過（藏譯 Toh 113 的章序與梵本一致，故共用此表）。
    {"file": "sa_saddharmapuNDarIkasUtra", "work": "T0262",
     "zh": "妙法蓮華經", "sa": "Saddharmapuṇḍarīkasūtra", "siglum": "Saddhp",
     "form": "chapter",
     "chapter_map": {
         **{i: i for i in range(1, 12)},        # 序…見寶塔（梵 11 含漢 12 提婆達多）
         **{i: i + 1 for i in range(12, 21)},   # 勸持…如來神力 → 漢 13–21
         21: 26,   # dhāraṇī            陀羅尼品     （羅什排第 26）
         22: 23,   # bhaiṣajyarājapūrva 藥王菩薩本事品
         23: 24,   # gadgadasvara       妙音菩薩品
         24: 25,   # samantamukha       觀世音菩薩普門品
         25: 27,   # śubhavyūharāja     妙莊嚴王本事品
         26: 28,   # samantabhadra      普賢菩薩勸發品
         27: 22,   # anuparīndanā       囑累品       （羅什移到第 22）
     },
     "note": "梵藏 27 品、羅什 28 品；提婆達多併入見寶塔，且羅什把囑累品移到第 22"},

    # ── 本緣部 ──
    {"file": "sa_lalitavistara", "work": "T0187",
     "zh": "方廣大莊嚴經", "sa": "Lalitavistara", "siglum": "Lal", "form": "chapter"},

    # ── 瑜伽部・論集部（頌號式，梵藏漢共通）──
    {"file": "sa_maitreya-madhyAntavibhAgakArikA", "work": "T1600",
     "zh": "辯中邊論", "sa": "Madhyāntavibhāgakārikā", "siglum": "Mvk",
     "form": "chapter.verse"},
    {"file": "sa_asaGga-mahAyAnasUtrAlaMkAra", "work": "T1604",
     "zh": "大乘莊嚴經論", "sa": "Mahāyānasūtrālaṃkāra", "siglum": "Msa",
     "form": "chapter.verse"},

    # ── 章節標記各自成格，逐部指定 regex（group 1 ＝ 品號）──
    {"file": "sa_zAntideva-bodhicaryAvatAra", "work": "T1662",
     "zh": "菩提行經", "sa": "Bodhicaryāvatāra",
     "siglum": r"\bPariccheda (\d+)\b", "form": "regex"},
    {"file": "sa_dazabhUmikasUtra", "work": "T0286",
     "zh": "十住經", "sa": "Daśabhūmikasūtra",
     "siglum": r"(?:^|// )(\d+) \w+ nāma \w+ bhūmiḥ", "form": "regex"},
    {"file": "sa_ratnagotravibhAga", "work": "T1611",
     "zh": "究竟一乘寶性論", "sa": "Ratnagotravibhāga",
     "siglum": r"(\d+)\. \w+ paricchedaḥ", "form": "regex"},

    # ── 般若部 ──
    {"file": "sa_aSTasAhasrikA-prajJApAramitA", "work": "T0224",
     "zh": "道行般若經", "sa": "Aṣṭasāhasrikā Prajñāpāramitā", "siglum": "ASP",
     "form": "chapter"},
    {"file": "sa_prajJApAramitAhRdayasUtra", "work": "T0251",
     "zh": "般若波羅蜜多心經", "sa": "Prajñāpāramitāhṛdayasūtra", "siglum": "",
     "form": "none", "note": "單章，不分品"},

    # ── 華嚴部 ──
    {"file": "sa_gaNDavyUhasUtra", "work": "T0293",
     "zh": "大方廣佛華嚴經（四十卷本・入法界品）", "sa": "Gaṇḍavyūhasūtra",
     "siglum": "", "form": "none",
     "note": "漢譯四十卷本為單一品（入法界品），梵本亦不另分品"},

    # ── 尚無可靠章節標記，退回整部層級 ──
    {"file": "sa_azvaghoSa-buddhacarita", "work": "T0192",
     "zh": "佛所行讚", "sa": "Buddhacarita", "siglum": "", "form": "none",
     "note": "GRETIL 此本帶校勘符號 X(C…C)，章節標記不穩定，暫不逐品對齊"},
    {"file": "sa_AryazUra-jAtakamAlA", "work": "T0160",
     "zh": "菩薩本生鬘論", "sa": "Jātakamālā", "siglum": "", "form": "none",
     "note": "漢譯僅存前十四本生且經改編，對照僅供參考"},
]


def fetch(name: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    dst = CACHE / f"{name}.xml"
    if dst.exists() and dst.stat().st_size > 1000:
        return dst
    with urllib.request.urlopen(GRETIL_RAW.format(name), timeout=180) as r:
        dst.write_bytes(r.read())
    return dst


def _text(el: ET.Element) -> str:
    return "".join(el.itertext())


def parse_gretil(path: Path, siglum: str, form: str) -> dict[int, list[str]]:
    """GRETIL TEI → {品號: [文句…]}。

    編號嵌在正文裡（`// MMK_1.1 //`、`Saddhp_1: …`），不是 XML 屬性，
    所以只能從文字抓。抓不到編號的行歸給「當前品」，順序即原書順序。
    """
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    body = root.find(f".//{{{TEI}}}body")
    if body is None:
        return {}

    if form == "regex":
        pat = re.compile(siglum)          # 此時 siglum 欄放的是完整 regex
    elif form == "chapter.verse":
        pat = re.compile(rf"\b{re.escape(siglum)}[_\s]*(\d+)[.,](\d+)")
    elif form == "chapter":
        pat = re.compile(rf"\b{re.escape(siglum)}[_\s]*(\d+)\b")
    else:
        pat = None

    out: dict[int, list[str]] = {}
    state = {"cur": 1}

    def emit(lines: list[str]):
        """一個單位（一組偈頌，或一段散文）→ 歸入一品。

        🚨 頌號標在偈的**末行**（`d e f // MMK_1.2 //`），所以不能逐行判品：
        下一品的首半偈會在看到標記前就被算進上一品。以偈頌組為單位取標記，
        整組同屬一品，才不會在每個品的交界處錯位半偈。
        """
        lines = [x for x in lines if x]
        if not lines:
            return
        if pat:
            for s in lines:
                m = pat.search(s)
                if m:
                    state["cur"] = int(m.group(1))
                    break
        out.setdefault(state["cur"], []).extend(lines)

    def walk(el: ET.Element):
        for child in el:
            tag = child.tag.split("}")[-1]
            if tag == "lg":
                emit([re.sub(r"\s+", " ", _text(l)).strip()
                      for l in child.iter() if l.tag.split("}")[-1] == "l"])
            elif tag in ("l", "p", "head"):
                # 章節標記常放在 <head> 而非 <l>/<p>（入菩提行論的 Pariccheda N
                # 即是），只掃 l/p 會讓整部書看起來只有一品
                emit([re.sub(r"\s+", " ", _text(child)).strip()])
            else:
                walk(child)

    walk(body)
    return out


def verse_ref(line: str, entry: dict) -> str:
    """從一行梵文裡抽出原書自帶的頌號（MMK_1.1）。抓不到回空字串。"""
    if entry.get("form") != "chapter.verse":
        return ""
    m = re.search(rf"{re.escape(entry['siglum'])}[_\s]*(\d+)[.,](\d+)", line)
    return f"{entry['siglum']} {m.group(1)}.{m.group(2)}" if m else ""


def zh_pin_segs(work_id: str) -> dict[int, str]:
    """漢文本的 {品號: 起始段}。

    CBETA 有時不給 div 的 type（道行般若 T0224 只有第一品標了 pin，
    其餘 29 品的 type 是空字串）。故 type 為空時，改看標題是否為品／分／會，
    避免整部書的品層被判定為「不存在」而擋掉對齊。
    """
    out: dict[int, str] = {}
    for node in tpp.toc_of(work_id):
        t = node.get("type") or ""
        head = node.get("head") or ""
        if t not in ("pin", ""):
            continue
        if t == "" and not re.search(r"[品分會]第|[品分會]$", head):
            continue
        n = node.get("n")
        if n and str(n).isdigit():
            out.setdefault(int(n), node["uid"])
            continue
        # 品號寫在標題（「觀因緣品第一」）時，取「第X」的漢數字
        m = re.search(r"第([一二三四五六七八九十百〇零]+)", head)
        if m:
            no = tpp.cjk_number(m.group(1))
            if no:
                out.setdefault(no, node["uid"])
    return out


def first_segment(work_id: str) -> str | None:
    """整部層級的落點：該經的第一段。心經、藥師這類漢本無品層的書，
    藏／梵文只能掛在全經開頭，不該因為「沒有品」就整個不掛。"""
    toc = tpp.toc_of(work_id)
    if toc:
        return toc[0]["uid"]
    p = SEG_DIR / f"{work_id}.jsonl"
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return json.loads(line)["uid"]
    return None


def audit_one(entry: dict) -> dict:
    path = fetch(entry["file"])
    sa = parse_gretil(path, entry["siglum"], entry["form"])
    zh = zh_pin_segs(entry["work"])
    cmap = entry.get("chapter_map")
    if cmap:
        status = "手寫品對照表"
        aligned = sum(1 for k, v in cmap.items() if k in sa and v in zh)
        detail = f"表列 {len(cmap)} 組，實對上 {aligned}"
    elif not zh:
        status = "漢文本無品層"
        detail = "退回整部層級"
    elif len(sa) == len(zh):
        status = "品數相符"
        detail = f"逐品對齊 {len(sa)} 品"
    else:
        status = "🚨 品數不合"
        detail = f"梵 {len(sa)} 品 vs 漢 {len(zh)} 品 —— 拒絕逐品對齊，需手寫 chapter_map"
    return {**entry, "sa_chapters": len(sa), "zh_chapters": len(zh),
            "sa_lines": sum(len(v) for v in sa.values()),
            "status": status, "detail": detail, "_sa": sa, "_zh": zh}


def cmd_audit(only: str | None):
    print(f"{'漢譯':28s} {'梵本':30s} {'梵品':>4s} {'漢品':>4s}  狀態")
    print("─" * 108)
    ok = blocked = 0
    for e in REGISTRY:
        if only and e["work"] != only:
            continue
        try:
            r = audit_one(e)
        except Exception as ex:  # noqa: BLE001
            print(f"{e['zh'][:26]:28s} {e['sa'][:28]:30s}    -    -  ⚠ {type(ex).__name__}: {ex}")
            continue
        flag = "🚨" in r["status"]
        blocked += flag
        ok += not flag
        print(f"{r['zh'][:26]:28s} {r['sa'][:28]:30s} {r['sa_chapters']:>4d} "
              f"{r['zh_chapters']:>4d}  {r['status']} — {r['detail']}")
        if e.get("note"):
            print(f"{'':60s}   註：{e['note']}")
    print("─" * 108)
    print(f"可對齊 {ok} 部；被擋下 {blocked} 部（需手寫 chapter_map，別硬對）")


def cmd_build(only: str | None):
    written = 0
    for e in REGISTRY:
        if only and e["work"] != only:
            continue
        r = audit_one(e)
        if "🚨" in r["status"]:
            print(f"  跳過 {r['zh']}：{r['detail']}")
            continue
        sa, zh = r["_sa"], r["_zh"]
        cmap = e.get("chapter_map") or {k: k for k in sa}
        if not zh:                       # 漢本無品層 → 整部掛在全經首段
            head = first_segment(e["work"])
            zh = {k: head for k in cmap} if head else {}

        by_seg: dict[str, list] = {}
        for sa_no, zh_no in cmap.items():
            lines = sa.get(int(sa_no))
            seg = zh.get(int(zh_no))
            if not lines or not seg:
                continue
            by_seg.setdefault(seg, []).append({
                "lang": "sa",
                "uid": f"{e['siglum']}_{sa_no}",
                "ref": f"{e['sa']} {sa_no}",
                "src": "site",          # 本站對齊：琥珀色，非學術定論
                "partial": False,
                # 行號只用原書真有的頌號（`// MMK_1.1 //`）；抓不到就留空。
                # 自編序號長得像引用式卻不是引用式，正是本專案要避免的錯。
                "lines": [[verse_ref(t, e), t] for t in lines],
            })
        if not by_seg:
            print(f"  跳過 {r['zh']}：無可掛的品")
            continue

        # 與巴利那一層合併寫回同一個 .orig.json（reader 只讀一個檔）
        out = SEG_DIR / f"{e['work']}.orig.json"
        existing = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
        for seg, items in by_seg.items():
            keep = [x for x in existing.get(seg, []) if x.get("lang") != "sa"]
            existing[seg] = keep + items
        out.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")
        written += 1
        print(f"  ✓ {e['zh']}（{e['work']}）：{len(by_seg)} 品掛上梵文，"
              f"{sum(len(v) for v in sa.values())} 行 → {out.name}")
    print(f"\n完成 {written} 部")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--only", type=str)
    a = ap.parse_args()
    if a.audit:
        cmd_audit(a.only)
    elif a.build:
        cmd_build(a.only)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
