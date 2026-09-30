"""異譯對讀・自動對齊：模型只給切點，經文一字不動。

人工三組（tripitaka_compare.py）證明了做法可行，這支把它批次化：
  1. 各本先切成「句」並編號——漢文按句末標點、巴利按 SuttaCentral 句段、藏英按 TMX 單元。
     切法保證 ''.join(句) == 原文。
  2. 模型（NVIDIA nemotron，思考關閉）只回傳「第 k 義段從各本第幾句起」。
     它說錯頂多切錯位置，不可能改字、漏字或捏造。
  3. 閘：各本起點嚴格遞增、第一個義段吃掉開頭、不得有全空義段、義段數合理。
  4. 複核：另一次呼叫看「每段各本開頭與結尾」，判斷是否講同一件事；
     錯段比例超過 25% 整組不發布。發布的組標 auto，頁面註明「自動對齊，未經人工校讀」。

候選由 tripitaka_compare_candidates.py 產生。進度寫 C:/tmp/cbeta/compare_auto_state.json，
中斷（筆電睡眠）後重跑會跳過已完成與已判失敗的組。

  python -X utf8 scripts/tripitaka_compare_auto.py --limit 5        # 先試幾組
  python -X utf8 scripts/tripitaka_compare_auto.py                  # 全部（可中斷續跑）
  python -X utf8 scripts/tripitaka_compare_auto.py --retry-failed   # 失敗的再試一次
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

SEG = Path(os.environ.get("TRIPITAKA_LOCAL", "C:/tmp/cbeta/out"))
SC_ROOT = Path("C:/tmp/cbeta/sc-data/sc_bilara_data/root/pli/ms")
CANDS = Path("C:/tmp/cbeta/compare_candidates.json")
STATE = Path("C:/tmp/cbeta/compare_auto_state.json")
OUT = ROOT / "public/content/tripitaka/compare"
CATALOG = Path("C:/tmp/cbeta/catalog.json")

MAX_PROMPT_CHARS = 60_000   # 超過就不整部送（交給分品流程，另案）
MAX_LINE = 160              # 送進提示詞的每句最多幾字（切點判斷用不到全文）


# ── 句子切分（保證接回去與原文相同）──────────────────────────────────────
_ZH_END = re.compile(r"(?<=[。！？；])(?![」』）〕”’])|(?<=[。！？；][」』）〕”’])")


def zh_sentences(text: str) -> list[str]:
    parts = [p for p in _ZH_END.split(text) if p]
    # 只有一兩個字的（如「」」）併回上一句；其餘短句（「汝等苾芻！」「舍利子！」這類呼格）
    # 併進下一句——呼格是下一段話的開頭，掛在上一句尾會被切到上一個義段去
    out: list[str] = []
    carry = ""
    for p in parts:
        if out and not carry and len(p.strip()) <= 2:
            out[-1] += p
        elif len(p.strip()) < 8:
            carry += p
        else:
            out.append(carry + p)
            carry = ""
    if carry:
        if out:
            out[-1] += carry
        else:
            out.append(carry)
    assert "".join(out) == text
    return out


# ── 讀各本 ──────────────────────────────────────────────────────────────
def _jsonl(work: str) -> list[dict]:
    return [json.loads(l) for l in (SEG / f"{work}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def zh_body(work: str, node: str | None) -> str:
    segs = _jsonl(work)
    if node:
        toc = json.loads((SEG / f"{work}.toc.json").read_text(encoding="utf-8"))["toc"]
        hit = [n for n in toc if n["head"] == node]
        if len(hit) != 1:
            raise ValueError(f"{work} 目錄「{node}」命中 {len(hit)}")
        segs = [s for s in segs if s["d"] == hit[0]["i"]]
    return "".join(s["sources"].get("lzh", "") for s in segs if s["kind"] not in ("byline", "head"))


_PALI_FILES: dict[str, Path] | None = None


def pali_lines(uid: str) -> list[str]:
    global _PALI_FILES
    if _PALI_FILES is None:
        _PALI_FILES = {f.name.split("_")[0]: f for f in SC_ROOT.rglob("*_root-pli-ms.json")}
    d = json.loads(_PALI_FILES[uid].read_text(encoding="utf-8"))
    return [v.strip() for v in d.values() if v.strip()]


_NAN: dict[str, list[str]] | None = None


def nanchuan_lines(pali_uid: str) -> list[str] | None:
    """漢譯南傳已掛在阿含的 orig.json（ref 前綴＝巴利經號）。"""
    global _NAN
    if _NAN is None:
        _NAN = {}
        for f in SEG.glob("*.orig.json"):
            for lst in json.loads(f.read_text(encoding="utf-8")).values():
                for x in lst:
                    if x["lang"] == "zh-nan":
                        key = x["ref"].split("（")[0].strip()
                        _NAN.setdefault(key, [l[1] for l in x["lines"]
                                              if not re.fullmatch(r"[一二三四五六七八九〇十]+", l[1].strip())])
    m = re.match(r"([a-z]+)(\d.*)", pali_uid)
    return _NAN.get(f"{m.group(1).upper()} {m.group(2)}") if m else None


def tmx_units(toh: str, side: str) -> list[str]:
    from tripitaka_tibetan import fetch
    raw = fetch(toh).read_text(encoding="utf-8", errors="replace")
    pat = re.compile(rf'xml:lang="{side}"[^>]*>\s*<seg>(.*?)</seg>', re.S)
    out = []
    for tu in re.findall(r"<tu[ >].*?</tu>", raw, re.S):
        m = pat.search(tu)
        out.append(re.sub(r"<[^>]+>|\s+", " ", m.group(1)).replace("\u00ad", "").strip() if m else "")
    return out


_TITLES: dict[str, dict] | None = None


def cat(work: str) -> dict:
    global _TITLES
    if _TITLES is None:
        _TITLES = {c["id"]: c for c in json.loads(CATALOG.read_text(encoding="utf-8"))}
    return _TITLES.get(work, {})


# ── 候選 → 各本（每本是一串句子）─────────────────────────────────────────
def versions_of(c: dict) -> tuple[str, str, list[dict], list[str]]:
    """→ (slug, title, versions, works)。versions: {id, lang, label, who, lines, join}"""
    vs: list[dict] = []
    if c["family"] == "pi":
        for uid in c["pi"]:
            vs.append({"id": uid, "lang": "pi", "label": f"巴利 {uid.upper()}", "who": "Mahāsaṅgīti 本・SuttaCentral",
                       "lines": pali_lines(uid), "join": " "})
            nan = nanchuan_lines(uid)
            if nan:
                vs.append({"id": f"nan-{uid}", "lang": "lzh", "label": f"漢譯南傳 {uid.upper()}",
                           "who": "元亨寺版（譯自巴利）", "lines": nan, "join": ""})
        slug = "pi-" + "-".join(c["pi"])
        title = None
    else:
        slug = f"bo-{c['toh']}"
        title = c.get("title")
        bo, en = tmx_units(c["toh"], "bo"), tmx_units(c["toh"], "en")
        keep = [i for i in range(min(len(bo), len(en))) if bo[i] or en[i]]
        vs.append({"id": "bo", "lang": "bo", "label": "藏譯", "who": f"德格版 {c['toh'].replace('toh', 'Toh ')}・84000",
                   "lines": [bo[i] for i in keep], "join": " "})
        vs.append({"id": "en", "lang": "en", "label": "84000 英譯", "who": "譯自藏譯・與藏文逐句對齊",
                   "lines": [en[i] for i in keep], "join": " ", "twin": "bo"})
    works = []
    for z in c["zh"]:
        body = zh_body(z["work"], z.get("node"))
        meta = cat(z["work"])
        name = meta.get("title_zh") or z["work"]
        label = f"{name}{' ' + z['node'] if z.get('node') else ''}"
        who = " ".join(x for x in (meta.get("byline"),) if x)
        vs.append({"id": z["work"] + (f"-{z['uid']}" if z.get("node") else ""), "lang": "lzh",
                   "label": label, "who": who, "lines": zh_sentences(body), "join": "",
                   "work": z["work"], "node": z.get("node")})
        works.append(z["work"])
        if title is None:
            title = name if not z.get("node") else None
    if title is None:
        first = next(v for v in vs if v.get("work"))
        title = first["label"]
    if c.get("dk"):
        works.append(c["dk"])
    return slug, title, vs, works


# ── 模型 ────────────────────────────────────────────────────────────────
def llm(prompt: str, max_tokens: int = 6000) -> str:
    import translate_ebook_to_zh as te  # 共用 NVIDIA 4 把 key 輪替與節流
    return te.nvidia_chat(prompt, max_tokens=max_tokens, temperature=0.1, thinking=False)


def parse_json(s: str) -> dict:
    s = re.sub(r"^```(?:json)?|```$", "", s.strip(), flags=re.M).strip()
    i, j = s.find("{"), s.rfind("}")
    return json.loads(s[i:j + 1])


ALIGN_PROMPT = """你是佛典對勘專家。以下是同一部經的 {n} 個本子（漢譯、原典或現代翻譯），每句前有編號。
請把全經切成若干「義段」（一個完整的語義單位：如序分、某一問答、某一譬喻、偈頌、流通分），
並指出每個義段在各本從第幾句開始。

規則：
- 義段數約 {lo}–{hi} 個，依內容而定；短經少、長經多。
- 義段照多數本子的次第排列；某本沒有這個義段就填 null。
- 若某本確實把某段放在不同位置（同源異流常見），照實填它在該本的句號，不要硬排成遞增。
- 每個本子的第一個出現的義段必須從第 0 句開始。
- 不要因為用詞不同就判為不同義段；看的是講的是不是同一件事。
- 義段名稱用繁體中文，4–14 字，描述內容（如「舍利弗請問」「幻師喻」「偈頌」）。

只輸出 JSON，不要說明：
{{"units":[{{"label":"…","starts":{{{keys}}}}}]}}

{texts}"""

REVIEW_PROMPT = """以下是同一部經幾個本子的對齊結果（同源異譯：部派不同、譯者不同、詳略不同是常態）。
每個義段列出各本在這一段的開頭與結尾。請找出**對錯位置**的義段——
也就是某本在這一段放的其實是另一段的內容（例如別本在講譬喻，它卻在講序分或偈頌）。

以下都**不算**問題：譯語不同（如理作意／正思惟）、詳略不同、一本多一句少一句、
次第小異、某本只有經題或標題、某本缺這一段。

只輸出 JSON：{{"bad":[對錯位置的義段序號…],"note":"一句話說明（沒有就空字串）"}}

{table}"""


def show_lines(lines: list[str]) -> str:
    return "\n".join(f"[{i}] {l[:MAX_LINE]}" for i, l in enumerate(lines))


def align(vs: list[dict], feedback: str = "") -> list[dict]:
    active = [v for v in vs if not v.get("twin")]   # 英譯跟藏文用同一組句號，不必另切
    total = sum(len(l) for v in active for l in v["lines"])
    n_lines = max(len(v["lines"]) for v in active)
    lo, hi = max(3, min(8, n_lines // 6)), max(6, min(60, n_lines // 2))
    texts = "\n\n".join(f"### 本子 {v['id']}（{v['label']}）\n{show_lines(v['lines'])}" for v in active)
    if len(texts) > MAX_PROMPT_CHARS:
        raise ValueError(f"太長（{len(texts):,} 字，{total:,} 字原文）→ 待分品")
    keys = ",".join(f'"{v["id"]}":0' for v in active)
    raw = llm(ALIGN_PROMPT.format(n=len(active), lo=lo, hi=hi, keys=keys, texts=texts) + feedback)
    return parse_json(raw)["units"]


def cut(vs: list[dict], units: list[dict], reordered: set | None = None) -> dict[str, dict[str, str]]:
    """閘 + 切。回 {unit_id: {version_id: 文字}}。
    段序與義段次序不同的本子記進 reordered（同源異流確有換位，如轉法輪經
    巴利「一諦三轉」對漢本「一轉四諦」）；換位過多視為亂對，拒絕。"""
    if not (2 <= len(units) <= 80):
        raise ValueError(f"義段數 {len(units)} 不合理")
    cells: dict[str, dict[str, str]] = {f"a{k:02d}": {} for k in range(len(units))}
    for v in vs:
        src_id = v.get("twin") or v["id"]
        starts = []
        for k, u in enumerate(units):
            s = (u.get("starts") or {}).get(src_id)
            if s is None:
                continue
            if not isinstance(s, int) or not (0 <= s < len(v["lines"])):
                raise ValueError(f"{v['id']} 第 {k} 段起點 {s!r} 超出範圍")
            starts.append((k, s))
        if not starts:
            raise ValueError(f"{v['id']} 一個義段都沒有")
        # 照這本自己的句序排；兩段同一個起點＝前一段在這本裡是空的，文字歸後一段。
        # （只改歸屬，不動文字）
        in_order = [k for k, _ in starts]
        starts.sort(key=lambda x: (x[1], x[0]))
        dedup: list[tuple[int, int]] = []
        for k, s in starts:
            if dedup and dedup[-1][1] == s:
                dedup[-1] = (k, s)
            else:
                dedup.append((k, s))
        starts = dedup
        ks = [k for k, _ in starts]
        inversions = sum(1 for a, b in zip(ks, ks[1:]) if b < a)
        if inversions:
            if inversions > max(1, len(ks) * 0.3):
                raise ValueError(f"{v['id']} 段序換位過多（{inversions}/{len(ks)}），疑為亂對")
            if reordered is not None:
                reordered.add(v["id"])
        del in_order
        starts[0] = (starts[0][0], 0)   # 開頭沒被歸段的句子併入第一個義段
        pieces = []
        for idx, (k, s) in enumerate(starts):
            e = starts[idx + 1][1] if idx + 1 < len(starts) else len(v["lines"])
            pieces.append((k, v["join"].join(v["lines"][s:e])))
        if re.sub(r"\s+", "", "".join(p for _, p in pieces)) != re.sub(r"\s+", "", "".join(v["lines"])):
            raise ValueError(f"{v['id']} 切完接回去與原文不符")
        for k, p in pieces:
            cells[f"a{k:02d}"][v["id"]] = p.strip()
    empty = [u for u, c in cells.items() if not c]
    if empty:
        raise ValueError(f"全空義段 {empty}")
    return cells


def review(vs: list[dict], labels: list[str], cells: dict) -> tuple[list[int], str]:
    rows = []
    for k, (u, c) in enumerate(cells.items()):
        rows.append(f"## 義段 {k}：{labels[k]}")
        for v in vs:
            if v.get("twin") or v["id"] not in c:
                continue
            t = c[v["id"]]
            rows.append(f"- {v['label']}：{t[:70]}{' … ' + t[-40:] if len(t) > 110 else ''}")
    out = parse_json(llm(REVIEW_PROMPT.format(table="\n".join(rows)), max_tokens=1500))
    return [int(b) for b in out.get("bad", []) if str(b).lstrip("-").isdigit()], out.get("note", "")


def to_trad(s: str) -> str:
    try:
        import opencc
        return opencc.OpenCC("s2twp").convert(s)
    except Exception:
        return s


# ── 主流程 ──────────────────────────────────────────────────────────────
def load_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(st: dict) -> None:
    tmp = STATE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(st, ensure_ascii=False, indent=1))
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(STATE)


def run_one(c: dict) -> dict:
    slug, title, vs, works = versions_of(c)
    # 模型偶爾給出不合格的切點或壞掉的 JSON：把錯誤回饋給它再試（「太長」不重試）
    feedback = ""
    reordered: set = set()
    for attempt in range(3):
        reordered = set()
        try:
            units = align(vs, feedback)
            cells = cut(vs, units, reordered)
            break
        except ValueError as e:
            if attempt == 2 or str(e).startswith("太長"):
                raise
            feedback = f"\n\n⚠ 上一次的輸出不合格：{e}。請重新輸出合格的 JSON。"
    labels = [to_trad(str(u.get("label") or f"第{k + 1}段"))[:20] for k, u in enumerate(units)]
    dbg = Path("C:/tmp/cbeta/compare_auto_debug") / f"{slug}.txt"
    dbg.parent.mkdir(parents=True, exist_ok=True)
    dbg.write_text("\n".join(f"## {k} {labels[k]}\n" + "\n".join(f"  {vid}: {t[:90]}" for vid, t in c.items())
                             for k, c in enumerate(cells.values())), encoding="utf-8")
    bad, note = review(vs, labels, cells)
    ratio = len(bad) / len(labels)
    if ratio > 0.25:
        raise ValueError(f"複核 {len(bad)}/{len(labels)} 段有問題：{to_trad(note)}")
    anchors = [{"work": v["work"], "node": v["node"]} for v in vs if v.get("node")]
    data = {
        "slug": slug, "title": to_trad(title), "family": c["family"], "auto": True,
        "intro": "自動對齊（模型定切點、腳本逐字切分與把關），未經人工校讀。"
                 + (f"複核標記存疑 {len(bad)} 段：{to_trad(note)}" if bad else ""),
        "units": [{"id": f"a{k:02d}", "label": labels[k], **({"doubt": True} if k in bad else {})}
                  for k in range(len(labels))],
        "versions": [{**{k: v[k] for k in ("id", "lang", "label", "who")},
                      **({"reorder": True} if v["id"] in reordered else {})} for v in vs],
        "works": sorted(set(works)), "anchors": anchors,
        "cells": cells,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"ok": True, "slug": slug, "units": len(labels), "doubt": len(bad)}


def rebuild_index() -> int:
    idx = []
    for f in sorted(OUT.glob("*.json")):
        if f.name == "index.json":
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        idx.append({"slug": d["slug"], "title": d["title"], "family": d["family"], "auto": bool(d.get("auto")),
                    "works": d["works"], "anchors": d.get("anchors", []), "versions": len(d["versions"]),
                    "labels": [v["label"] for v in d["versions"]]})
    (OUT / "index.json").write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
    return len(idx)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--family", choices=["pi", "bo", "sa"])
    ap.add_argument("--only", help="只跑這一組（slug，如 pi-sn56.12）")
    a = ap.parse_args()
    cands = json.loads(CANDS.read_text(encoding="utf-8"))
    st = load_state()
    todo = []
    for c in cands:
        if a.family and c["family"] != a.family:
            continue
        if c["family"] == "sa":
            continue  # 梵本系全是長經，走分品流程（另案）
        key = ("pi-" + "-".join(c["pi"])) if c["family"] == "pi" else f"bo-{c['toh']}"
        if a.only and key != a.only:
            continue
        prev = {} if a.only else st.get(key, {})
        if prev.get("ok") or (prev.get("err") and not a.retry_failed) or prev.get("too_long"):
            continue
        todo.append((key, c))
    if a.limit:
        todo = todo[: a.limit]
    print(f"待處理 {len(todo)} 組（狀態檔已有 {len(st)} 組）", flush=True)
    for i, (key, c) in enumerate(todo, 1):
        t0 = time.time()
        try:
            r = run_one(c)
            st[key] = r
            print(f"[{i}/{len(todo)}] ✓ {key}  {r['units']} 段  存疑 {r['doubt']}  {time.time() - t0:.0f}s", flush=True)
        except ValueError as e:
            too_long = str(e).startswith("太長")
            st[key] = {"err": str(e)[:300], **({"too_long": True} if too_long else {})}
            print(f"[{i}/{len(todo)}] ✗ {key}  {str(e)[:160]}", flush=True)
        except Exception as e:  # 引擎掛了：記下但不判死，下次照跑
            print(f"[{i}/{len(todo)}] ! {key}  {type(e).__name__}: {str(e)[:160]}", flush=True)
            if "NVIDIA" in str(e) or "404" in str(e):
                save_state(st)
                raise SystemExit("引擎不可用，整場停（別燒掉整個佇列）")
        save_state(st)
        if i % 10 == 0:
            rebuild_index()
    n = rebuild_index()
    ok = sum(1 for v in st.values() if v.get("ok"))
    print(f"完成 {ok} 組上架；索引共 {n} 組", flush=True)


if __name__ == "__main__":
    main()
