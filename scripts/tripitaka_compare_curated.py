"""常讀經典的多譯本對照（使用者點名：金剛經、淨土經、三論）。

與 tripitaka_compare_auto.py 共用切段、閘、複核與輸出；差別在取源與「節」怎麼定：
  金剛經  梵本（GRETIL，Vaidya 校訂本）自帶 §1–32 節號 → 節由梵本決定，不讓模型分段。
          羅什本先逐節掛到梵本，其餘漢譯再掛到羅什本（漢對漢最穩）。
  阿彌陀經 梵本沒有節號 → 照自動對齊的星狀做法（羅什本為參照分段）。
  （無量壽經、中論另案，見 SKILL）

  python -X utf8 scripts/tripitaka_compare_curated.py vajracchedika
  python -X utf8 scripts/tripitaka_compare_curated.py amitabha
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tripitaka_compare_auto as A  # noqa: E402

GRETIL = Path("C:/tmp/cbeta/gretil")
GRETIL_RAW = "https://gretil.sub.uni-goettingen.de/gretil/corpustei/{}.xml"


def gretil_paras(name: str) -> list[str]:
    """TEI 正文 → 段落文字（去註、去「(Vajr, Vaidya 76)」這類版頁標記）。"""
    p = GRETIL / f"{name}.xml"
    if not p.exists():
        import urllib.request
        GRETIL.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(GRETIL_RAW.format(name), timeout=180) as r:
            p.write_bytes(r.read())
    t = p.read_text(encoding="utf-8")
    t = t[t.find("<body"):]
    t = re.sub(r"<note\b.*?</note>", " ", t, flags=re.S)
    out = []
    for m in re.finditer(r"<(p|l)\b[^>]*>(.*?)</\1>", t, re.S):
        s = html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
        s = re.sub(r"\(\s*[^()]*Vaidya\s*\d+\s*\)", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            out.append(s)
    return out


def sentences_with_sections(paras: list[str]) -> tuple[list[str], list[tuple[str, int]]]:
    """梵本段落 → 句子（在 daṇḍa「|」後的空白處斷，接回去不變）＋各節起點。
    節的終點是段尾的「|| n ||」；只認比目前大的 n（偈頌也用「|| 1 ||」編號），
    跳號時合併標成「§26–27」，不硬切。"""
    lines: list[str] = []
    marks: list[tuple[str, int]] = []
    cur, start = 0, 0
    for para in paras:
        parts = [x for x in re.split(r"(?<=\|)\s+(?=[^|])", para) if x]
        lines += parts
        m = re.search(r"\|\|\s*(\d+)\s*\|\|\s*$", para)
        if m and int(m.group(1)) > cur:
            n = int(m.group(1))
            marks.append((f"§{cur + 1}" if n == cur + 1 else f"§{cur + 1}–{n}", start))
            cur, start = n, len(lines)
    if start < len(lines):          # 最後一個節號之後的尾題、流通
        marks.append(("尾題", start))
    return lines, marks


def zh_version(work: str, label: str | None = None, node: str | None = None, seg: str | None = None,
               start: str | None = None) -> dict:
    """start：從這幾個字起取（大般若第九會前面有一篇〈第九會序〉，要從「如是我聞」起）。"""
    meta = A.cat(work)
    body = A.zh_body(work, node, seg)
    if start:
        i = body.find(start)
        if i < 0:
            raise ValueError(f"{work} 找不到起點「{start}」")
        body = body[i:]
    return {"id": work, "lang": "lzh", "label": label or meta.get("title_zh") or work,
            "who": meta.get("byline") or "", "lines": A.zh_sentences(body),
            "join": "", "work": work}


def texts_by_unit(v: dict, units: list[dict]) -> dict[int, str]:
    marks = sorted((s, k) for k, u in enumerate(units)
                   if isinstance(s := (u.get("starts") or {}).get(v["id"]), int) and 0 <= s < len(v["lines"]))
    out = {}
    for i, (s, k) in enumerate(marks):
        e = marks[i + 1][0] if i + 1 < len(marks) else len(v["lines"])
        out[k] = v["join"].join(v["lines"][s:e])
    return out


def fixed_units(ref_id: str, marks: list[tuple[str, int]], hub_id: str):
    """節由參照本（梵本）決定；hub（羅什本）先掛上，其餘漢譯掛到 hub；最後替各節取中文小標。"""
    def fn(vs: list[dict]) -> list[dict]:
        units = [{"label": lab, "starts": {ref_id: s}} for lab, s in marks]
        ref = next(v for v in vs if v["id"] == ref_id)
        hub = next(v for v in vs if v["id"] == hub_id)
        ref_txt = texts_by_unit(ref, units)
        twin_en = {v["twin"]: v for v in vs if v.get("twin")}
        order = [hub] + [v for v in vs if v is not ref and v is not hub and not v.get("twin")]
        hub_txt: dict[int, str] = {}
        for v in order:
            base = ref_txt if v is hub or v["lang"] != "lzh" else hub_txt
            disp = twin_en[v["id"]]["lines"] if v["id"] in twin_en else v["lines"]
            got = A.attach_windowed(units, base, disp, v["label"])
            for k, u in enumerate(units):
                u["starts"][v["id"]] = got[k] if k < len(got) else None
            if v is hub:
                hub_txt = texts_by_unit(hub, units)
        # 小標：拿羅什本各節開頭請模型取 4–12 字繁中標題（失敗就只留節號）
        try:
            rows = "\n".join(f"[{k}] {hub_txt.get(k, '')[:90]}" for k in range(len(units)))
            got = A.parse_json(A.llm("以下是一部經各節的開頭。請為每一節取 4–12 字的繁體中文小標，"
                                     f"描述該節內容。只輸出 JSON：{{\"labels\":[共 {len(units)} 個字串]}}\n\n{rows}",
                                     max_tokens=3000)).get("labels") or []
        except Exception:
            got = []
        for k, u in enumerate(units):
            t = A.to_trad(str(got[k]))[:14] if k < len(got) and got[k] else ""
            u["label"] = f"{u['label']} {t}".strip()
        return units
    return fn


def vajracchedika() -> dict:
    lines, marks = sentences_with_sections(gretil_paras("sa_vajracchedikA-prajJApAramitA"))
    gil, _ = sentences_with_sections(gretil_paras("sa_vajracchedikA-prajJApAramitA-gilgit"))
    vs = [
        {"id": "sa", "lang": "sa", "label": "梵本（Vaidya 校訂本）", "who": "GRETIL・節號 §1–32",
         "lines": lines, "join": " "},
        {"id": "sa-gilgit", "lang": "sa", "label": "梵本（吉爾吉特寫本）", "who": "GRETIL・Gilgit 寫本",
         "lines": gil, "join": " "},
        zh_version("T0235", "羅什本"),
        zh_version("T0236a", "菩提流支本（甲）"),
        zh_version("T0236b", "菩提流支本（乙）"),
        zh_version("T0237", "真諦本"),
        zh_version("T0238", "笈多本"),
        zh_version("T0239", "義淨本"),
        zh_version("T0220h", "玄奘本（大般若第九會）", start="如是我聞"),
    ]
    works = [v["work"] for v in vs if v.get("work")]
    return A.publish("sa-vajracchedika", "金剛般若波羅蜜經", "sa", vs, works, [],
                     units_fn=fixed_units("sa", marks, "T0235"),
                     intro_extra="節號依梵本 Vaidya 校訂本（§1–32，即學界通用的 Conze 分節）。")


def amitabha() -> dict:
    sa = []
    for p in gretil_paras("sa_smaller-sukhAvatIvyUha"):
        sa += [x for x in re.split(r"(?<=[|.])\s+", p) if x]
    bo, en = A.tmx_units("toh115", "bo"), A.tmx_units("toh115", "en")
    keep = [i for i in range(min(len(bo), len(en))) if bo[i] or en[i]]
    vs = [
        zh_version("T0366", "羅什本"),
        zh_version("T0367", "玄奘本（稱讚淨土佛攝受經）"),
        {"id": "sa", "lang": "sa", "label": "梵本（小本極樂莊嚴經）", "who": "GRETIL", "lines": sa, "join": " "},
        {"id": "bo", "lang": "bo", "label": "藏譯", "who": "德格版 Toh 115・84000",
         "lines": [bo[i] for i in keep], "join": " "},
        {"id": "en", "lang": "en", "label": "84000 英譯", "who": "譯自藏譯・與藏文逐句對齊",
         "lines": [en[i] for i in keep], "join": " ", "twin": "bo"},
    ]
    return A.publish("sa-amitabha", "阿彌陀經", "sa", vs, ["T0366", "T0367", "DKtoh0115"], [])


VERSE_PICK_PROMPT = """《中論》的一頌。梵文：
{sa}

下面是羅什漢譯在這附近的幾頌（編號）。哪一頌是這首梵文頌的漢譯？
只回一個數字；若漢譯沒有譯這一頌，回 null。

{cands}"""


def madhyamaka() -> list[dict]:
    """中論逐頌：一頌一節（梵本頌號 MMK 品.頌），漢譯欄＝該頌＋青目釋到下一頌前。
    頌數相等的品（27 品中 17 品）按頌序一對一，不經模型；不等的品才讓模型在附近幾頌裡挑。
    漢譯的頌：四句五言兩行為一頌；青目釋文重引的頌（文字與前文某頌相同）當釋文，不算新頌。"""
    work = "T1564"
    segs = A._jsonl(work)
    toc = json.loads((A.SEG / f"{work}.toc.json").read_text(encoding="utf-8"))["toc"]
    pins = [n for n in toc if n["type"] == "pin"]
    orig = json.loads((A.SEG / f"{work}.orig.json").read_text(encoding="utf-8"))
    sa_ch = []      # 依段序取各品梵本
    for sg in segs:
        for x in orig.get(sg["uid"], []):
            if x["lang"] == "sa" and x["ref"] not in [c["ref"] for c in sa_ch]:
                sa_ch.append(x)
    if len(sa_ch) != len(pins):
        raise ValueError(f"梵本 {len(sa_ch)} 品 ≠ 漢譯 {len(pins)} 品")
    norm = lambda t: re.sub(r"[「」『』\s]", "", t)
    results = []
    for ci, (pin, sx) in enumerate(zip(pins, sa_ch), 1):
        # 漢譯：段落→行；偈頌拆成一頌一行（兩行四句）
        zh_lines, zh_sloka, seen = [], [], set()
        for sg in segs:
            if sg["d"] != pin["i"] or sg["kind"] in ("head", "byline"):
                continue
            t = sg["sources"]["lzh"]
            if sg["kind"] == "verse" and norm(t) not in seen:
                seen.add(norm(t))
                rows = t.split("\n")
                for j in range(0, len(rows), 2):
                    zh_sloka.append(len(zh_lines))
                    zh_lines.append("\n".join(rows[j:j + 2]) + ("\n" if j + 2 < len(rows) else ""))
            else:
                zh_lines.append(t)
        # 梵本：每頌以帶 MMK 頌號的那一行收尾，起點＝上一頌收尾的下一行。
        # 第一頌之前多出來的行（第 1 品的兩首歸敬頌，沒有頌號）兩行一首，另立「歸敬頌」。
        sa_lines = [txt for _lab, txt in sx["lines"]]
        ends = [i for i, (lab, _t) in enumerate(sx["lines"]) if lab.startswith("MMK")]
        if not ends:
            print(f"  ✗ 第 {ci} 品梵本沒有頌號", flush=True)
            continue
        first = max(0, ends[0] - 1)
        pre = list(range(0, first, 2))
        sa_start = pre + [first] + [e + 1 for e in ends[:-1]]
        sa_label = [f"歸敬頌{j + 1}" for j in range(len(pre))] + [sx["lines"][e][0] for e in ends]
        n = len(sa_start)
        equal = len(zh_sloka) == n

        def units_fn(vs, sa_start=sa_start, sa_label=sa_label, zh_sloka=zh_sloka, zh_lines=zh_lines,
                     sa_lines=sa_lines, equal=equal):
            units = [{"label": sa_label[k], "starts": {"sa": sa_start[k]}} for k in range(len(sa_start))]
            if equal:
                for k, u in enumerate(units):
                    u["starts"]["T1564"] = zh_sloka[k]
                return units
            # 頌數不等：逐頌在羅什本附近幾頌裡挑（依序、不回頭）
            prev = -1
            for k, u in enumerate(units):
                est = round(k * len(zh_sloka) / max(1, len(units)))
                cand = [j for j in range(max(prev + 1, est - 3), min(len(zh_sloka), est + 4))]
                pick = None
                if cand:
                    e = sa_start[k + 1] if k + 1 < len(sa_start) else len(sa_lines)
                    ans = A.llm(VERSE_PICK_PROMPT.format(
                        sa=" ".join(sa_lines[sa_start[k]:e]),
                        cands="\n".join(f"[{j}] {zh_lines[zh_sloka[j]].strip()}" for j in cand)), max_tokens=20)
                    m = re.search(r"\d+", ans or "")
                    if m and "null" not in (ans or "").lower()[:8] and int(m.group()) in cand:
                        pick = int(m.group())
                if pick is not None:
                    u["starts"]["T1564"] = zh_sloka[pick]
                    prev = pick
                else:
                    u["starts"]["T1564"] = None
            return units

        vs = [
            {"id": "sa", "lang": "sa", "label": "梵本（月稱本所存頌）", "who": "GRETIL・MMK 頌號",
             "lines": sa_lines, "join": "\n"},
            {"id": "T1564", "lang": "lzh", "label": "羅什本（頌＋青目釋）", "who": "鳩摩羅什譯・409 年",
             "lines": zh_lines, "join": "", "work": "T1564"},
        ]
        title = re.sub(r"^中論", "", pin["head"]).split("（")[0]
        slug = f"sa-mmk-c{ci:02d}"
        try:
            r = A.publish(slug, f"中論・{title}", "sa", vs, ["T1564"],
                          [{"work": "T1564", "node": pin["head"], "uid": pin["uid"]}],
                          units_fn=units_fn,
                          intro_extra=("一頌一節，頌號依梵本（MMK 品.頌）；漢譯欄為該頌加青目釋。"
                                       + ("本品漢梵頌數相等，按頌序對應。" if equal
                                          else f"本品頌數不等（漢 {len(zh_sloka)}／梵 {n}），逐頌由模型比對。")))
            results.append(r)
            print(f"  ✓ {slug} {title} 漢{len(zh_sloka)}／梵{n} {'等' if equal else '不等'}", flush=True)
        except ValueError as e:
            print(f"  ✗ {slug} {e}", flush=True)
    return results


SETS = {"vajracchedika": vajracchedika, "amitabha": amitabha, "madhyamaka": madhyamaka}

if __name__ == "__main__":
    for name in sys.argv[1:] or list(SETS):
        print(f"[{name}]", flush=True)
        try:
            r = SETS[name]()
            print(f"  ✓ {r}", flush=True)
        except ValueError as e:
            print(f"  ✗ {e}", flush=True)
    print(f"索引 {A.rebuild_index()} 組")
