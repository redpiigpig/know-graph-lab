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
# 測試時用 COMPARE_STATE 指到別處：批次跑著時兩個行程寫同一個狀態檔會互相覆蓋
STATE = Path(os.environ.get("COMPARE_STATE", "C:/tmp/cbeta/compare_auto_state.json"))
OUT = ROOT / "public/content/tripitaka/compare"
CATALOG = Path("C:/tmp/cbeta/catalog.json")

MAX_PROMPT_CHARS = 110_000  # nemotron 上下文 128k tokens；漢字約 1 token/字、英梵更省
MAX_LINE = 160              # 送進提示詞的每句最多幾字（切點判斷用不到全文）
SMALL_TOTAL = 25_000       # 全部本子合計在這以內就一次整體對齊（巴利系短經驗證過）；超過走星狀


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


def zh_body(work: str, node: str | None, seg: str | None = None) -> str:
    segs = _jsonl(work)
    if node or seg:
        toc = json.loads((SEG / f"{work}.toc.json").read_text(encoding="utf-8"))["toc"]
        # 有首段 uid 就用 uid（唯一）；標題在增一阿含每品重複
        hit = [n for n in toc if n["uid"] == seg] if seg else [n for n in toc if n["head"] == node]
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
        body = zh_body(z["work"], z.get("node"), z.get("seg"))
        meta = cat(z["work"])
        name = meta.get("title_zh") or z["work"]
        label = f"{name}{' ' + z['node'] if z.get('node') else ''}"
        who = " ".join(x for x in (meta.get("byline"),) if x)
        vs.append({"id": z["work"] + (f"-{z['uid']}" if z.get("node") else ""), "lang": "lzh",
                   "label": label, "who": who, "lines": zh_sentences(body), "join": "",
                   "work": z["work"], "node": z.get("node"), "seg": z.get("seg")})
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
def llm(prompt: str, max_tokens: int = 6000, thinking: bool = False) -> str:
    import translate_ebook_to_zh as te  # 共用 NVIDIA 4 把 key 輪替與節流
    # 一時斷線（ConnectionError，筆電換網路、睡醒）別讓整批崩潰：等一下再試，三次都不行才放棄
    for attempt in range(3):
        try:
            return te.nvidia_chat(prompt, max_tokens=max_tokens, temperature=0.1, thinking=thinking)
        except RuntimeError as e:
            if "conn" not in str(e) or attempt == 2:
                raise
            time.sleep(120)
    return ""


def parse_json(s: str) -> dict:
    s = re.sub(r"^```(?:json)?|```$", "", s.strip(), flags=re.M).strip()
    i, j = s.find("{"), s.rfind("}")
    try:
        return json.loads(s[i:j + 1])
    except json.JSONDecodeError:
        # 模型偶爾多一個逗號或漏引號；修得回來就用，修不回來照樣丟 ValueError 觸發重試
        import json_repair
        out = json_repair.loads(s[i:j + 1])
        if not isinstance(out, dict):
            Path("C:/tmp/cbeta/compare_last_bad.txt").write_text(s, encoding="utf-8")
            raise ValueError(f"JSON 無法解析：{s[:120]!r}")
        return out


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

🚨 先比人名：義段標題或漢譯說的是某人（如目犍連），原典那一格開頭卻是另一人（如 Mahākāśyapa），
就是錯位——即使只差一段也要列出。原典可能是巴利、梵文或英譯，請實際讀懂再判。
以下都**不算**問題：譯語不同（如理作意／正思惟）、詳略不同、一本多一句少一句、
次第小異、某本只有經題或標題、某本缺這一段。

只輸出 JSON：{{"bad":[對錯位置的義段序號…],"note":"一句話說明（沒有就空字串）"}}

{table}"""


def show_lines(lines: list[str]) -> str:
    return "\n".join(f"[{i}] {l[:MAX_LINE]}" for i, l in enumerate(lines))


def align(vs: list[dict], feedback: str = "") -> list[dict]:
    active = [v for v in vs if not v.get("twin")]   # 英譯跟藏文用同一組句號，不必另切
    # 藏譯改給模型看同句號的英譯：藏文字元多又難讀，英譯逐句對齊，切點完全通用
    twin_en = {v["twin"]: v for v in vs if v.get("twin")}
    shown = [(v, twin_en[v["id"]]["lines"] if v["id"] in twin_en else v["lines"]) for v in active]
    total = sum(len(l) for v in active for l in v["lines"])
    n_lines = max(len(v["lines"]) for v in active)
    lo, hi = max(3, min(8, n_lines // 6)), max(6, min(60, n_lines // 2))
    texts = "\n\n".join(f"### 本子 {v['id']}（{v['label']}{'，以逐句對齊的英譯呈現' if v['id'] in twin_en else ''}）\n"
                        f"{show_lines(lines)}" for v, lines in shown)
    if len(texts) > MAX_PROMPT_CHARS:
        raise ValueError(f"太長（{len(texts):,} 字，{total:,} 字原文）→ 待分品")
    keys = ",".join(f'"{v["id"]}":0' for v in active)
    raw = llm(ALIGN_PROMPT.format(n=len(active), lo=lo, hi=hi, keys=keys, texts=texts) + feedback)
    return parse_json(raw)["units"]


WINDOW_PROMPT = """同一部經的兩個本子。漢譯本裡，上一段結尾是：
「{prev_tail}」
這一段（{label}）開頭是：
「{head}」

下面是另一個本子（{vlabel}）在對應位置附近的句子。哪一句是「這一段」的第一句？
只回一個數字（句號）；若這個本子沒有這一段，回 null。

{cands}"""


def attach_windowed(units: list[dict], ref_txt: dict[int, str], disp: list[str], vlabel: str, W: int = 12,
                    heads: dict[int, str] | None = None) -> list:
    """長品的原典逐段定位：先用長度比例預估起點，只拿附近 ±W 句問模型「哪一句是本段開頭」。
    一次丟幾百句要它報句號，nemotron 會整體錯一格，甚至無視格式把每一句都抄一遍；
    把題目縮到「二十幾句挑一句」就穩了。"""
    import bisect
    n = len(units)
    clen = [len(ref_txt.get(k, "")) for k in range(n)]
    cum = [0]
    for l in disp:
        cum.append(cum[-1] + len(l))
    r = cum[-1] / max(1, sum(clen))
    starts: list = [None] * n
    present = [k for k in range(n) if clen[k]]
    if not present:
        return starts
    starts[present[0]] = 0
    prev_i, prev_k = 0, present[0]
    for k in present[1:]:
        # 從上一個已定位的段起，把中間各段（含沒找到的）的漢譯長度都算進去
        est = bisect.bisect_left(cum, cum[prev_i] + sum(clen[prev_k:k]) * r)
        for w in (W, W * 3):                 # 窄窗找不到，放寬一次
            lo, hi = max(prev_i + 1, est - w), min(len(disp), est + w + 1)
            if lo >= hi:
                break
            cands = "\n".join(f"[{i}] {disp[i][:140]}" for i in range(lo, hi))
            # heads：參照本是梵文時給模型看的中文譯句（它讀不懂梵文，然燈佛在候選裡也回「沒有」）
            hd = heads or {}
            ans = llm(WINDOW_PROMPT.format(prev_tail=(hd.get(prev_k) or ref_txt[prev_k])[-50:], label=units[k].get("label"),
                                           head=(hd.get(k) or ref_txt[k])[:120], vlabel=vlabel, cands=cands), max_tokens=50)
            m = re.search(r"-?\d+", ans or "")
            if m and "null" not in (ans or "").lower()[:10] and lo <= int(m.group()) < hi:
                starts[k] = int(m.group())
                prev_i, prev_k = starts[k], k
                break
    return starts


def align_staged(vs: list[dict], feedback: str = "") -> list[dict]:
    """短的（全部本子合計 ≤ SMALL_TOTAL 字）一次送、整體對齊——巴利系短經實測品質好。
    長的走「星狀」：①只把一個漢譯參照本切成義段 ②其餘每一本（漢譯、原典都一樣）
    逐段用小窗定位掛上去。維摩詰經弟子品實測：一次丟多本，模型會整體錯一段，
    甚至把兩個漢譯本各自切段、根本沒對起來；拆成單本分段＋小窗定位才穩。"""
    active = [v for v in vs if not v.get("twin")]
    if sum(len(l) for v in active for l in v["lines"]) <= SMALL_TOTAL:
        return align(vs, feedback)
    zh = [v for v in active if v["lang"] == "lzh"] or active
    ref = sorted(zh, key=lambda v: sum(len(l) for l in v["lines"]))[len(zh) // 2]   # 長度居中者
    others = [v for v in active if v is not ref]
    units = align([ref], feedback)
    # 參照本各段的文字（照句號切；缺段就空著）
    marks = sorted((s, k) for k, u in enumerate(units)
                   if isinstance(s := (u.get("starts") or {}).get(ref["id"]), int) and 0 <= s < len(ref["lines"]))
    ref_txt: dict[int, str] = {}
    for idx, (s, k) in enumerate(marks):
        e = marks[idx + 1][0] if idx + 1 < len(marks) else len(ref["lines"])
        ref_txt[k] = "".join(ref["lines"][s:e])
    twin_en = {v["twin"]: v for v in vs if v.get("twin")}
    for v in others:
        # disp：給模型看的句子（藏文看英譯；梵文看逐句中譯，見 curated.gloss_lines）
        lines = twin_en[v["id"]]["lines"] if v["id"] in twin_en else (v.get("disp") or v["lines"])
        label = v["label"] + ("（以逐句對齊的英譯呈現）" if v["id"] in twin_en else "")
        got = attach_windowed(units, ref_txt, lines, label)
        for k, u in enumerate(units):
            s = got[k] if k < len(got) else None
            u.setdefault("starts", {})[v["id"]] = s if isinstance(s, int) else None
    return units


def cut(vs: list[dict], units: list[dict], reordered: set | None = None) -> dict[str, dict[str, str]]:
    """閘 + 切。回 {unit_id: {version_id: 文字}}。
    段序與義段次序不同的本子記進 reordered（同源異流確有換位，如轉法輪經
    巴利「一諦三轉」對漢本「一轉四諦」）；換位過多視為亂對，拒絕。"""
    if not (2 <= len(units) <= 80):
        raise ValueError(f"義段數 {len(units)} 不合理")
    cells: dict[str, dict[str, str]] = {f"a{k:02d}": {} for k in range(len(units))}
    for v in vs:
        src_id = v.get("twin") or v["id"]
        starts, invalid = [], 0
        for k, u in enumerate(units):
            s = (u.get("starts") or {}).get(src_id)
            if s is None:
                continue
            if not isinstance(s, int) or not (0 <= s < len(v["lines"])):
                invalid += 1      # 超出範圍的切點當作「此本無此段」；只影響歸屬，不動文字
                continue
            starts.append((k, s))
        if invalid > max(1, (len(starts) + invalid) * 0.2):
            raise ValueError(f"{v['id']} 有 {invalid} 個起點超出範圍（共 {len(v['lines'])} 句）")
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
            # 藏文不給複核看（它讀不懂，錯位一整段也放行過）；改看同句號的英譯那一欄
            if v["lang"] == "bo" or v["id"] not in c:
                continue
            t = c[v["id"]]
            rows.append(f"- {v['label']}：{t[:70]}{' … ' + t[-40:] if len(t) > 110 else ''}")
    out = parse_json(llm(REVIEW_PROMPT.format(table="\n".join(rows)), max_tokens=2500))
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
    anchors = [{"work": v["work"], "node": v["node"], "uid": v.get("seg")} for v in vs if v.get("node")]
    return publish(slug, title, c["family"], vs, works, anchors)


def publish(slug: str, title: str, family: str, vs: list[dict], works: list[str],
            anchors: list[dict], units_fn=None, intro_extra: str = "") -> dict:
    """對齊 → 切 → 複核 → 寫檔。任何一步不合格就 raise ValueError（不寫檔）。
    units_fn：節由原典自己的編號決定時（金剛經梵本 §1–32、中論頌號）由呼叫端給，不讓模型分段。"""
    # 模型偶爾給出不合格的切點或壞掉的 JSON：把錯誤回饋給它再試（「太長」不重試）
    feedback = ""
    reordered: set = set()
    for attempt in range(3):
        reordered = set()
        try:
            units = units_fn(vs) if units_fn else align_staged(vs, feedback)
            cells = cut(vs, units, reordered)
            break
        except ValueError as e:
            if attempt == 2 or str(e).startswith("太長"):
                raise
            feedback = "\n\n⚠ 上一次的輸出不合格：" + str(e) + "。請重新輸出合格的 JSON。"
    # 閘：某本只掛上極少數節＝定位失敗，不是那本真的缺（金剛經首跑羅什本 33 節只掛上 4 節，
    # 其餘全併進前一節的格子裡，閘與複核都放行）。心經羅什本本就缺序分，覆蓋 54%，不會誤殺。
    if len(units) >= 6:
        for v in vs:
            if v.get("twin"):
                continue
            got = sum(1 for c in cells.values() if c.get(v["id"]))
            if got / len(units) < 0.3:
                raise ValueError(f"{v['id']} 只掛上 {got}/{len(units)} 節，定位失敗")
    labels = [to_trad(str(u.get("label") or f"第{k + 1}段"))[:20] for k, u in enumerate(units)]
    dbg = Path("C:/tmp/cbeta/compare_auto_debug") / f"{slug}.txt"
    dbg.parent.mkdir(parents=True, exist_ok=True)
    dbg.write_text("\n".join(f"## {k} {labels[k]}\n" + "\n".join(f"  {vid}: {t[:90]}" for vid, t in c.items())
                             for k, c in enumerate(cells.values())), encoding="utf-8")
    bad, note = review(vs, labels, cells)
    ratio = len(bad) / len(labels)
    if ratio > 0.25:
        raise ValueError(f"複核 {len(bad)}/{len(labels)} 段有問題：{to_trad(note)}")
    data = {
        "slug": slug, "title": to_trad(title), "family": family, "auto": True,
        "intro": intro_extra + "自動對齊（模型定切點、腳本逐字切分與把關），未經人工校讀。"
                 + (f"複核標記存疑 {len(bad)} 段：{to_trad(note)}" if bad else ""),
        "units": [{"id": f"a{k:02d}", "label": labels[k], **({"doubt": True} if k in bad else {})}
                  for k in range(len(labels))],
        "versions": [{**{k: v[k] for k in ("id", "lang", "label", "who", "work") if k in v},
                      **({"reorder": True} if v["id"] in reordered else {})} for v in vs],
        "works": sorted(set(works)), "anchors": anchors,
        "cells": cells,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"ok": True, "slug": slug, "units": len(labels), "doubt": len(bad)}


# ── 分品模式（長經）─────────────────────────────────────────────────────
MAX_WORK_CHARS = 400_000   # 超過（大般若、大寶積那一級）先不做：品目上百，配對一次送不下
MAX_CHAPTERS = 150


def zh_chapters(work: str) -> list[tuple[str, str, str]]:
    """→ [(品名, 品首段 uid, 全文)]。品＝目錄第 0 層（序、跋除外）。"""
    toc = json.loads((SEG / f"{work}.toc.json").read_text(encoding="utf-8"))["toc"]
    by_i = {n["i"]: n for n in toc}
    top = [n for n in toc if n["depth"] == 0 and n["type"] not in ("xu", "w")]
    top_ids = {n["i"] for n in top}
    texts: dict[int, list[str]] = {n["i"]: [] for n in top}
    for sgm in _jsonl(work):
        if sgm["kind"] in ("byline", "head"):
            continue
        d = sgm["d"]
        while d in by_i and d not in top_ids:
            d = by_i[d]["parent"]
        if d in top_ids:
            texts[d].append(sgm["sources"].get("lzh", ""))
    return [(n["head"], n["uid"], "".join(texts[n["i"]])) for n in top if "".join(texts[n["i"]]).strip()]


_EN_HEAD = re.compile(r"^(?:\{\d+\}\s*)?.{0,90}?\bChapter\s+\d+\b")
_EN_TAIL = re.compile(r"(concludes|This (was|is) the).{0,240}\bchapter\b", re.I)


def bo_chapters(toh: str) -> list[tuple[str, list[str], list[str]]]:
    """TMX → [(英文首句當品名, 藏句, 英句)]。品界兩種認法：
    英文側段首「… Chapter N」（法華那類），或品尾題「This was the … — the first chapter」
    （解深密、維摩那類，TMX 沒有標題）。"""
    bo, en = tmx_units(toh, "bo"), tmx_units(toh, "en")
    n = min(len(bo), len(en))
    cuts = {0}
    for i in range(n):
        if _EN_HEAD.match(en[i]) and "concludes" not in en[i][:120]:
            cuts.add(i)
        # 品尾題：英文「This was the … chapter」，或藏文「…ལེའུ་སྟེ་དང་པོའོ།།」（第幾品）
        if (_EN_TAIL.search(en[i]) or ("ལེའུ" in bo[i] and re.search(r"འོ[།\s]*$", bo[i]))) and i + 1 < n:
            cuts.add(i + 1)
    if len(cuts) <= 1:
        cuts |= set(tei_chapter_starts(toh, en))
    cuts = sorted(cuts)
    out = []
    for a, b in zip(cuts, cuts[1:] + [n]):
        B = [x for x in bo[a:b] if x]
        E = [x for x in en[a:b] if x]
        if B and len(B) == len([x for x in bo[a:b] if x]):
            keep = [i for i in range(a, b) if bo[i] or en[i]]
            out.append(((en[a] or "")[:60], [bo[i] for i in keep], [en[i] for i in keep]))
    return out


def _letters(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


def tei_chapter_starts(toh: str, en: list[str]) -> list[int]:
    """TMX 沒有品標記時（維摩詰經 Toh 176：藏英兩側都沒有品尾題），
    改用 84000 英譯 TEI 的章節結構：取每品第一段的開頭，到 TMX 英文句裡找同一句。
    TMX 與 TEI 是同一份譯文，所以找得到；必須每品都找到且依序遞增，否則全不採用。"""
    import urllib.request
    cache = Path("C:/tmp/cbeta/tibetan")
    tree = cache / "_tei_tree.json"
    try:
        if not tree.exists():
            with urllib.request.urlopen("https://api.github.com/repos/84000/data-tei/git/trees/master?recursive=1",
                                        timeout=120) as r:
                tree.write_bytes(r.read())
        num = re.sub(r"\D", "", toh)
        paths = [t["path"] for t in json.loads(tree.read_text(encoding="utf-8"))["tree"]
                 if re.search(rf"_toh{num}[_\-]", t["path"]) and "/translations/" in t["path"]]
        if len(paths) != 1:
            return []
        f = cache / f"tei_{toh}.xml"
        if not f.exists():
            with urllib.request.urlopen("https://raw.githubusercontent.com/84000/data-tei/master/" + paths[0],
                                        timeout=300) as r:
                f.write_bytes(r.read())
        t = f.read_text(encoding="utf-8")
    except Exception:
        return []
    body = t[t.find('type="translation"'):]
    chs = re.split(r'<div type="chapter"', body)[1:]
    starts, at = [], 0
    ens = [_letters(e) for e in en]
    for c in chs:
        p = re.search(r"<p[^>]*>(.*?)</p>", c, re.S)
        if not p:
            return []
        key = _letters(re.sub(r"<[^>]+>", " ", p.group(1)))[:40]
        hit = next((i for i in range(at, len(ens)) if ens[i] and (key.startswith(ens[i][:40]) or ens[i].startswith(key))), None)
        if hit is None:
            return []
        starts.append(hit)
        at = hit + 1
    return starts if len(starts) > 1 else []


def sa_chapters(work: str) -> list[tuple[str, list[str]]]:
    """梵本（GRETIL）已按品掛在漢譯的 orig.json；依漢文段序取出、同 ref 只取一次。"""
    o = json.loads((SEG / f"{work}.orig.json").read_text(encoding="utf-8"))
    order = [sg["uid"] for sg in _jsonl(work)]
    seen, out = set(), []
    for uid in order:
        for x in o.get(uid, []):
            if x["lang"] == "sa" and x["ref"] not in seen:
                seen.add(x["ref"])
                # GRETIL 一行常是一整段散文（一品才三四十行），模型切不細、還會報超出範圍的句號。
                # 按句末標點再切；只在空白處斷，接回去（去空白比對）仍與原文相同。
                lines = []
                for l in x["lines"]:
                    lines += [p for p in re.split(r"(?<=[.|।॥])\s+", l[1].strip()) if p]
                out.append((x["ref"], lines))
    return out


PAIR_PROMPT = """以下是同一部經幾個本子的品目（每品列出編號、品名或首句、開頭文字、字數）。
請把各本中**內容相對應**的品配成一組。一組可以包含某本連續的幾品（某譯本把兩品併成一品），
某本沒有對應的品就不列。各本在各組裡的品號必須依序遞增、不可重複。
🚨 各本品數常常不同（例如漢譯 14 品、梵藏 12 品，因為梵藏把兩品併為一品）。
**絕不可照序號一對一硬配**——逐組比對開頭文字與字數，確認講的是同一段情節。
組名用繁體中文 4–14 字，以最通行的品名命名。

只輸出 JSON：{{"groups":[{{"label":"…","parts":{{{keys}}}}}]}}

{lists}"""


def length_outliers(groups: list[dict], lens: dict[str, list[int]]) -> list[str]:
    """照序號硬配的典型症狀：某本對參照本的字數比，在錯配的那幾組會突然跳兩三倍。
    （維摩詰經：梵藏第 3 品＝漢譯弟子品＋菩薩品，硬配時那一組藏文長度是漢文的好幾倍）"""
    # 只比「原典對漢譯」。漢譯之間繁簡本來就差很多（支謙〈不思議品〉1,498 字、玄奘 3,742 字），
    # 拿來比會誤殺；分母用同組全部漢譯的總字數，把個別譯本的詳略抵消掉。
    zh = [k for k in lens if k.startswith("T")]
    if not zh:
        return []
    ix = lambda p, k: (p.get(k) if isinstance(p.get(k), list) else [p[k]]) if k in p and p.get(k) is not None else []
    bad = set()
    ref = "漢譯合計"
    for k in lens:
        if k in zh:
            continue
        rs = []
        for gi, g in enumerate(groups):
            p = g.get("parts") or {}
            la = sum(lens[k][i] for i in ix(p, k))
            present = [z for z in zh if ix(p, z)]
            lb = sum(lens[z][i] for z in present for i in ix(p, z)) / max(1, len(present)) * len(zh)
            if la and lb:
                rs.append((gi, la / lb))
        if len(rs) < 3:
            continue
        med = sorted(r for _, r in rs)[len(rs) // 2]
        for gi, r in rs:
            # 1.6 倍：維摩詰經實測正確配對時梵／羅什比在 4.3–5.5 間（最大偏離 1.27），
            # 照序號硬配時在 3.4–8.5 間亂跳；2.2 太寬會放過
            if r > med * 1.6 or r < med / 1.6:
                bad.add(f"「{groups[gi].get('label')}」（{k} 與 {ref} 的長度比 {r:.2f}，中位數 {med:.2f}）")
    return sorted(bad)


def pair_chapters(chaps: dict[str, list[str]], lens: dict[str, list[int]] | None = None) -> list[dict]:
    keys = ",".join(f'"{k}":[0]' for k in chaps)
    lists = "\n\n".join(f"### 本子 {k}\n" + "\n".join(f"[{i}] {t}" for i, t in enumerate(v)) for k, v in chaps.items())
    feedback = ""
    for attempt in range(3):
        try:
            groups = parse_json(llm(PAIR_PROMPT.format(keys=keys, lists=lists) + feedback, max_tokens=8000))["groups"]
            last = {k: -1 for k in chaps}
            for g in groups:
                for k, idx in (g.get("parts") or {}).items():
                    if k not in chaps:
                        raise ValueError(f"未知的本子 {k}")
                    idx = idx if isinstance(idx, list) else [idx]
                    for i in idx:
                        if not isinstance(i, int) or not (0 <= i < len(chaps[k])) or i <= last[k]:
                            raise ValueError(f"{k} 的品號 {i} 超出範圍或未遞增")
                        last[k] = i
            odd = length_outliers(groups, lens) if lens else []
            if odd:
                raise ValueError("以下幾組長度比例異常，疑似照序號硬配、實際內容不對應：" + "；".join(odd[:8]))
            return groups
        except ValueError as e:
            if attempt == 2:
                raise
            feedback = "\n\n⚠ 上一次的輸出不合格：" + str(e) + "。請重新輸出。"
    return []


def attach_by_length(groups: list[dict], key: str, olens: list[int], glens: list[float]) -> list[dict]:
    """把一本原典的各品掛到漢譯的品組上——Gale–Church 式的長度動態規劃。

    原典對漢譯的字數比在各品間大致固定（維摩詰經梵／羅什 4.3–5.5），所以比例最穩的
    那條對應路徑就是對的。允許 1-1、1-2、2-1、1-3、3-1（兩品併一品），
    以及少量 0-1／1-0（某本獨有的品）。漢譯側被併的幾組會合成一組。
    模型不擅長這件事：看不懂梵文開頭，品數不同時就照序號硬配。"""
    import math
    O, G = len(olens), len(groups)
    if not O or not G:
        return groups
    r = sum(olens) / max(1.0, sum(glens))
    beads = [(1, 1, 0.0), (1, 2, 0.35), (2, 1, 0.35), (1, 3, 0.9), (3, 1, 0.9), (0, 1, 2.0), (1, 0, 2.0)]
    INF = float("inf")
    dp = [[INF] * (G + 1) for _ in range(O + 1)]
    back: dict[tuple[int, int], tuple[int, int]] = {}
    dp[0][0] = 0.0
    for i in range(O + 1):
        for j in range(G + 1):
            if dp[i][j] == INF:
                continue
            for a, b, pen in beads:
                ni, nj = i + a, j + b
                if ni > O or nj > G:
                    continue
                lo, lg = sum(olens[i:ni]), sum(glens[j:nj])
                cost = pen if (a == 0 or b == 0) else pen + abs(math.log(max(lo, 1) / max(r * lg, 1)))
                if dp[i][j] + cost < dp[ni][nj]:
                    dp[ni][nj] = dp[i][j] + cost
                    back[(ni, nj)] = (i, j)
    path, cur = [], (O, G)
    while cur != (0, 0):
        prev = back[cur]
        path.append((prev, cur))
        cur = prev
    path.reverse()
    out: list[dict] = []
    for (i, j), (ni, nj) in path:
        if nj == j:          # 原典獨有的品：沒有漢譯可並排，略過
            continue
        merged = {"label": groups[j].get("label") if nj - j == 1 else
                  f"{groups[j].get('label')}～{groups[nj - 1].get('label')}", "parts": {}}
        for g in groups[j:nj]:
            for k, idx in (g.get("parts") or {}).items():
                merged["parts"].setdefault(k, []).extend(idx if isinstance(idx, list) else [idx])
        if ni > i:
            merged["parts"][key] = list(range(i, ni))
        out.append(merged)
    return out


def zh_group_lens(groups: list[dict], lens: dict[str, list[int]], zh: list[str]) -> list[float]:
    """每組的漢譯長度：在場各本平均後乘本數（缺本的組不吃虧）。"""
    out = []
    for g in groups:
        p = g.get("parts") or {}
        present = [(z, p[z] if isinstance(p[z], list) else [p[z]]) for z in zh if p.get(z) is not None and p.get(z) != []]
        tot = sum(lens[z][i] for z, idx in present for i in idx)
        out.append(tot / max(1, len(present)) * len(zh))
    return out


def chapter_jobs(c: dict) -> tuple[str, str, dict[str, dict]] | None:
    """長經 → (slug 前綴, 經名, {本子 id: {lang,label,who,chapters:[(名, 文或句, en?, 錨點)]}})"""
    books: dict[str, dict] = {}
    for z in c["zh"]:
        if z["chars"] > MAX_WORK_CHARS or z.get("node"):
            continue
        ch = zh_chapters(z["work"])
        if not ch or len(ch) > MAX_CHAPTERS:
            continue
        meta = cat(z["work"])
        books[z["work"]] = {"lang": "lzh", "label": meta.get("title_zh") or z["work"],
                            "who": meta.get("byline") or "", "work": z["work"],
                            "chapters": [(h, zh_sentences(t), None, {"work": z["work"], "node": h, "uid": u}) for h, u, t in ch]}
    if c["family"] == "sa" and (SEG / f"{c['sa']}.orig.json").exists():
        ch = sa_chapters(c["sa"])
        if ch:
            books["sa"] = {"lang": "sa", "label": "梵本", "who": "GRETIL 校訂本",
                           "chapters": [(r, lines, None, None) for r, lines in ch]}
    toh = c.get("toh")
    if toh:
        ch = bo_chapters(toh)
        if 1 < len(ch) <= MAX_CHAPTERS:
            books["bo"] = {"lang": "bo", "label": "藏譯", "who": f"德格版 {toh.replace('toh', 'Toh ')}・84000",
                           "chapters": [(t, B, E, None) for t, B, E in ch]}
    if len(books) < 2:
        return None
    slug = (f"sa-{c['key']}" if c["family"] == "sa" else f"bo-{toh}")
    title = c.get("title") or next(iter(books.values()))["label"]
    return slug, title, books


def run_chapters(c: dict, st: dict, retry: bool = False) -> tuple[int, int]:
    job = chapter_jobs(c)
    if not job:
        return 0, 0
    slug, title, books = job
    listing = {}
    for k, b in books.items():
        listing[k] = [f"{name[:30]} | {''.join(lines)[:50] if b['lang'] != 'bo' else (en or [''])[0][:60]} | "
                      f"{sum(len(x) for x in lines):,}字"
                      for name, lines, en, _a in b["chapters"]]
    pkey = f"{slug}#pairing"
    if st.get(pkey, {}).get("groups"):
        groups = st[pkey]["groups"]
    else:
        lens = {k: [sum(len(x) for x in ch[1]) for ch in b["chapters"]] for k, b in books.items()}
        zh = [k for k, b in books.items() if b["lang"] == "lzh"]
        orig = [k for k in books if k not in zh]
        # 1) 漢譯之間：品數相同就按序配；不同才請模型依品名配（中文品名它讀得懂）
        counts = {len(books[z]["chapters"]) for z in zh}
        if len(zh) == 1 or len(counts) == 1:
            n = len(books[zh[0]]["chapters"])
            # 品名去掉經名前綴（「維摩詰所說經方便品第二」→「方便品第二」），只影響顯示
            clean = lambda h: re.sub(r"^.{2,12}?經(?=.{1,12}品)", "", h)
            groups = [{"label": clean(books[zh[0]]["chapters"][i][0]), "parts": {z: [i] for z in zh}} for i in range(n)]
        else:
            groups = pair_chapters({z: listing[z] for z in zh})
        # 2) 原典：長度動態規劃掛上去（見 attach_by_length），逐本做
        for k in orig:
            groups = attach_by_length(groups, k, lens[k], zh_group_lens(groups, lens, zh))
        odd = length_outliers(groups, lens)
        if odd:
            raise ValueError("配品後長度比例仍異常，不發布：" + "；".join(odd[:6]))
        st[pkey] = {"groups": groups}
        save_state(st)
    ok = fail = 0
    for gi, g in enumerate(groups, 1):
        gslug = f"{slug}-c{gi:02d}"
        if st.get(gslug, {}).get("ok") or (st.get(gslug, {}).get("err") and not retry):
            continue
        vs, works, anchors = [], [], []
        for k, idx in (g.get("parts") or {}).items():
            idx = idx if isinstance(idx, list) else [idx]
            b = books[k]
            lines = [ln for i in idx for ln in b["chapters"][i][1]]
            if not lines:
                continue
            vid = k
            vs.append({"id": vid, "lang": b["lang"], "label": b["label"], "who": b["who"],
                       "lines": lines, "join": "" if b["lang"] == "lzh" else " ", **({"work": b["work"]} if b.get("work") else {})})
            if b["lang"] == "bo":
                vs.append({"id": "en", "lang": "en", "label": "84000 英譯", "who": "譯自藏譯・與藏文逐句對齊",
                           "lines": [ln for i in idx for ln in b["chapters"][i][2]], "join": " ", "twin": "bo"})
            if b.get("work"):
                works.append(b["work"])
                anchors.extend(b["chapters"][i][3] for i in idx)   # 併品時每一品都要錨，閱讀器才知道整段被涵蓋
        if len([v for v in vs if not v.get("twin")]) < 2:
            continue
        if c.get("dk"):
            works.append(c["dk"])
        try:
            r = publish(gslug, f"{title}・{to_trad(str(g.get('label') or gi))}", c["family"], vs, works, anchors)
            st[gslug] = r
            ok += 1
            print(f"    ✓ {gslug} {r['units']} 段 存疑 {r['doubt']}", flush=True)
        except ValueError as e:
            st[gslug] = {"err": str(e)[:300]}
            fail += 1
            print(f"    ✗ {gslug} {str(e)[:140]}", flush=True)
        save_state(st)
    return ok, fail


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
    ap.add_argument("--chapters", action="store_true", help="長經分品：梵本系＋短經模式判太長的藏譯系")
    a = ap.parse_args()
    cands = json.loads(CANDS.read_text(encoding="utf-8"))
    st = load_state()
    if a.chapters:
        jobs = []
        for c in cands:
            key = f"sa-{c['key']}" if c["family"] == "sa" else (f"bo-{c['toh']}" if c["family"] == "bo" else None)
            if not key or (a.only and key != a.only) or (a.family and c["family"] != a.family):
                continue
            if c["family"] == "bo" and not st.get(key, {}).get("too_long"):
                continue   # 藏譯系只接短經模式送不下的
            if st.get(f"{key}#done") and not a.only and not a.retry_failed:
                continue
            jobs.append((key, c))
        # 梵本系先做（維摩詰、法華這幾部有梵藏漢三方，最有價值）；一部要跑好幾小時
        jobs.sort(key=lambda j: j[1]["family"] != "sa")
        if a.limit:
            jobs = jobs[: a.limit]
        print(f"分品：{len(jobs)} 部", flush=True)
        for i, (key, c) in enumerate(jobs, 1):
            print(f"[{i}/{len(jobs)}] {key}", flush=True)
            try:
                ok, fail = run_chapters(c, st, a.retry_failed)
                st[f"{key}#done"] = {"ok": ok, "fail": fail}
                print(f"  → {ok} 組上架、{fail} 組未過", flush=True)
            except ValueError as e:
                st[f"{key}#done"] = {"err": str(e)[:300]}
                print(f"  ✗ {str(e)[:160]}", flush=True)
            except Exception as e:
                print(f"  ! {type(e).__name__}: {str(e)[:160]}", flush=True)
                if "NVIDIA" in str(e):
                    save_state(st)
                    raise SystemExit("引擎不可用，整場停")
            save_state(st)
            rebuild_index()
        print(f"索引共 {rebuild_index()} 組", flush=True)
        return
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
