#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""教父卷缺譯列補譯（接在 fathers_realign_volume.py --apply 之後）。

  python -X utf8 scripts/fathers_fill_gaps.py --count                 # 全 38 卷還剩幾列缺譯（純數字）
  python -X utf8 scripts/fathers_fill_gaps.py --book <id>             # 只驗：印這卷缺口
  python -X utf8 scripts/fathers_fill_gaps.py --book <id> --apply [--limit N]

缺譯列＝英文欄有內容（正文／註文，不含分隔線）而同一列的中文欄是零寬佔位。逐列（或同塊連續數列
合批）翻成繁中，**只寫回那一列**，段號照 fathers_realign_volume 預留的號。

引擎只用 Gemini → NVIDIA（不用 Haiku／Claude）。Gemini 額度用盡會停用 6 小時。
譯文過閘全部要過才寫：是中文、無推理外洩／回覆語、[^N] 與 {{p:N}} 與英文相同、註文 (N) 開頭不變、
簡體字、長度比。不過閘不寫、記入 fill_fail.json，連錯 3 次的列不再試。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import fathers_realign as fr  # noqa: E402

CH = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
OUT = ROOT / "output" / "fathers_gap"
FAIL = OUT / "fill_fail.json"
MAX_FAIL = 3
BATCH_LETTERS = 3500

ADDENDUM = """
9. 這是 Schaff《尼西亞前後教父全集》英譯本的一小段，前後文不在手上也照譯；不要補充說明、不要加註、不要輸出任何原文以外的內容。
10. 聖經引文用和合本語體；教父、地名、神學名詞依上面的譯名表，表上沒有的用通行音譯（短譯優先）。
"""


# ── 目標列 ──────────────────────────────────────────────────────────────────

def rows_of(text: str | None) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text or "") if p.strip()]


def en_text(c: dict) -> str:
    return fr.chunk_en_text(c)


def find_targets(c: dict, fails: dict | None = None) -> list[dict]:
    """→ [{row, en, kind, n}]：英文有內容、中文是佔位的列。段號 n 由前一個有號的列推算。"""
    z, e = rows_of(c.get("content")), rows_of(en_text(c))
    if len(z) != len(e):
        return []
    if re.search(r"索引|Index|目次|Contents", c.get("chapter_path") or ""):
        return []
    out = []
    last_end = 0
    pend = 0
    label = None
    for zr in z:
        m0 = re.match(r"^(?:\{\{p:[^}]*\}\})*\{\{s:([^}]*)\}\}", zr)
        if m0:
            label = m0.group(1).rpartition("-")[0]
            break
    for j, (zr, er) in enumerate(zip(z, e)):
        m = re.match(r"^((?:\{\{p:[^}]*\}\})*)\{\{s:([^}]*)\}\}", zr)
        if m:
            label_s, _, tail = m.group(2).rpartition("-")
            label = label_s
            nums = re.findall(r"\d+", tail)
            last_end = int(nums[-1]) if nums else last_end
            pend = 0
            continue
        zc = zr.replace(fr.EMPTY, "").strip()
        ec = er.replace(fr.EMPTY, "").strip()
        if zc or not ec:
            continue
        kd = fr.kind_of(ec.split("\n")[0])
        if kd == "S":
            continue
        n = None
        if kd == "B":
            pend += 1
            n = last_end + pend
        key = f"{c.get('chunk_index')}:{j}"
        if fails and fails.get(key, 0) >= MAX_FAIL:
            continue
        out.append({"row": j, "en": ec, "kind": kd, "n": n, "label": label, "key": key})
    return out


# ── 過閘 ────────────────────────────────────────────────────────────────────

CJK = re.compile(r"[一-鿿]")
LAT = re.compile(r"[A-Za-z]")
REFS = re.compile(r"\[\^\d+\]")
PAGES = re.compile(r"\{\{p:\d+\}\}")


def gate_row(zh: str, en: str, kind: str) -> str:
    """過閘回 ''，否則回原因。純函式。"""
    from audit_fathers_coverage import META, SIMPLIFIED
    t = (zh or "").strip()
    if not t:
        return "empty"
    if META.search(t):
        return "meta-reply"
    if any(ch in SIMPLIFIED for ch in t):
        return "simplified"
    if sorted(REFS.findall(t)) != sorted(REFS.findall(en)):
        return "refs-mismatch"
    if sorted(PAGES.findall(t)) != sorted(PAGES.findall(en)):
        return "pages-mismatch"
    if kind == "F":
        a, b = fr.FN_RE.match(en), fr.FN_RE.match(t)
        if a and not (b and b.group(1) == a.group(1)):
            return "fn-number"
    e_lat = len(LAT.findall(REFS.sub("", en)))
    z_cjk = len(CJK.findall(t))
    if e_lat >= 60:
        r = z_cjk / e_lat
        if not (0.08 <= r <= 1.2):
            return f"len-ratio {r:.2f}"
    elif e_lat >= 15 and z_cjk == 0 and not re.search(r"[Ͱ-Ͽἀ-῿]", en):
        return "no-cjk"
    try:
        import translate_ebook_to_zh as te
        why = te.unusable_reason(t, en)
        if why:
            return why
    except Exception:  # noqa: BLE001
        pass
    return ""


# ── 引擎（Gemini → NVIDIA，不用 Haiku）──────────────────────────────────────

_ENGINE_STATE = OUT / "engine_state.json"


def _load_dead() -> float:
    try:
        return float(json.loads(_ENGINE_STATE.read_text(encoding="utf-8")).get("gemini_dead_until", 0))
    except Exception:  # noqa: BLE001
        return 0.0


def _save_dead(t: float) -> None:
    try:
        OUT.mkdir(parents=True, exist_ok=True)
        _ENGINE_STATE.write_text(json.dumps({"gemini_dead_until": t}), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


_gemini_dead_until = _load_dead()


class EnginesDown(RuntimeError):
    pass


def make_engine():
    import translate_ebook_to_zh as te
    import threading
    _lk = threading.Lock()

    def safe_throttle() -> None:
        with _lk:
            gap = te.NVIDIA_MIN_INTERVAL - (time.time() - te._nv_last_call)
            if gap > 0:
                time.sleep(gap)
            te._nv_last_call = time.time()
    te._nv_throttle = safe_throttle
    base = te.PROMPT_TMPL
    # 在 {source} 前插入補充規則
    te.PROMPT_TMPL = base.replace("只輸出翻譯後的繁體中文 markdown", ADDENDUM.strip() + "\n\n只輸出翻譯後的繁體中文 markdown", 1)

    def call(src: str) -> str:
        global _gemini_dead_until
        if time.time() >= _gemini_dead_until:
            try:
                return te.gemini_translate(src)
            except RuntimeError as e:
                if "exhausted" in str(e) or "no Gemini" in str(e) or "429" in str(e):
                    _gemini_dead_until = time.time() + 6 * 3600
                    _save_dead(_gemini_dead_until)
                    print("    Gemini 額度用盡，停用 6 小時，改 NVIDIA", flush=True)
                # 其他錯誤（輸出不能用等）直接試 NVIDIA
        try:
            return te.nvidia_translate(src)
        except RuntimeError as e:
            raise EnginesDown(str(e)[:120])
    return call


def translate_batch(call, targets: list[dict]) -> list[tuple[dict, str, str]]:
    """→ [(target, zh 或 '', 失敗原因)]。先合批，段數對不上就逐列。"""
    res = []
    if len(targets) > 1:
        src = "\n\n".join(clean_src(t["en"]) for t in targets)
        out = call(src)
        parts = [p.strip() for p in re.split(r"\n\s*\n", out) if p.strip()]
        if len(parts) == len(targets):
            ok = []
            for t, z in zip(targets, parts):
                why = gate_row(z, t["en"], t["kind"])
                ok.append((t, z if not why else "", why))
            if all(z for _, z, _ in ok):
                return ok
            # 有列不過閘：只重試那幾列
            return [(t, z, w) if z else _single(call, t) for t, z, w in ok]
        # 段數不符 → 逐列
    return [_single(call, t) for t in targets]


def _single(call, t: dict) -> tuple[dict, str, str]:
    why = "?"
    for _ in range(2):
        z = call(clean_src(t["en"])).strip()
        why = gate_row(z, t["en"], t["kind"])
        if not why:
            return t, z, ""
    return t, "", why


# ── 寫回 ────────────────────────────────────────────────────────────────────

def put_row(c: dict, row: int, zh: str, n: int | None, label: str | None) -> None:
    rows = rows_of(c.get("content"))
    zh = re.sub(r"\s*\n+\s*", "", zh).strip()     # 中文列內不留硬斷行
    lead = re.match(r"^((?:\{\{p:[^}]*\}\})*)", zh).group(1)
    if n is not None and label:
        zh = lead + f"{{{{s:{label}-{n}}}}}" + zh[len(lead):]
    rows[row] = zh
    c["content"] = "\n\n".join(rows)


def load(bid: str) -> list[dict]:
    p = CH / f"{bid}.jsonl"
    return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]


def save(bid: str, chunks: list[dict]) -> None:
    p = CH / f"{bid}.jsonl"
    tmp = p.with_suffix(".jsonl.tmp")
    tmp.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n", encoding="utf-8")
    tmp.replace(p)


def load_fails() -> dict:
    try:
        return json.loads(FAIL.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def save_fails(d: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FAIL.write_text(json.dumps(d, ensure_ascii=False, indent=0), encoding="utf-8")


def batches(targets: list[dict]) -> list[list[dict]]:
    out, cur, n = [], [], 0
    for t in targets:
        if cur and (n + len(t["en"]) > BATCH_LETTERS or t["kind"] != cur[0]["kind"]):
            out.append(cur)
            cur, n = [], 0
        cur.append(t)
        n += len(t["en"])
    if cur:
        out.append(cur)
    return out


def apply_edits(bid: str, edits: list[dict]) -> int:
    """重新讀檔、只把「仍是佔位、英文列沒變」的列寫上譯文，再原子換檔。
    （長時間翻譯期間別的程序可能改過檔，不能拿記憶體裡的舊版整份存回。）"""
    if not edits:
        return 0
    chunks = load(bid)
    by = {c.get("chunk_index"): c for c in chunks}
    n = 0
    for e in edits:
        c = by.get(e["chunk_index"])
        if not c:
            continue
        z, en = rows_of(c.get("content")), rows_of(en_text(c))
        if len(z) != len(en) or e["row"] >= len(z):
            continue
        if z[e["row"]].replace(fr.EMPTY, "").strip() or en[e["row"]].replace(fr.EMPTY, "").strip() != e["en"]:
            continue
        put_row(c, e["row"], e["zh"], e["n"], e["label"])
        n += 1
    if n:
        save(bid, chunks)
    return n


def clean_src(en: str) -> str:
    """送去翻的英文：CCEL 的硬斷行（行內單個換行）併成空白，免得模型把斷行照抄進中文。"""
    return re.sub(r"[ \t]*\n[ \t]*", " ", en).strip()


def fill_book(bid: str, apply: bool, limit: int = 0, push: bool = True) -> tuple[int, int]:
    import concurrent.futures as cf
    fails_all = load_fails()
    fails = fails_all.setdefault(bid, {})
    chunks = load(bid)
    todo = [(i, find_targets(c, fails)) for i, c in enumerate(chunks)]
    todo = [(i, ts) for i, ts in todo if ts]
    total = sum(len(ts) for _, ts in todo)
    if not apply or not total:
        return total, 0
    call = make_engine()
    done = 0
    pending: list[dict] = []
    last_save = time.time()
    bak = CH / f"{bid}.jsonl.bak_fill"
    if not bak.exists():
        shutil.copy2(CH / f"{bid}.jsonl", bak)

    def flush():
        nonlocal pending
        apply_edits(bid, pending)
        pending = []
        save_fails(fails_all)

    # 正文先、註文後；每個 job = (chunk_index, 一批目標)
    jobs = []
    for kind in ("B", "F"):
        for i, ts in todo:
            ts_k = [t for t in ts if t["kind"] == kind]
            for b in batches(ts_k):
                jobs.append((chunks[i]["chunk_index"], b))
    if limit:
        jobs = jobs[:max(1, limit)]
    workers = int(os.environ.get("KGL_FILL_WORKERS") or 4)
    down = False

    def work(job):
        ci, b = job
        src = [dict(t, en=t["en"]) for t in b]
        return ci, translate_batch(call, src)

    try:
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            inflight: set = set()
            it = iter(jobs)
            exhausted = False
            while inflight or not exhausted:
                while not exhausted and not down and len(inflight) < workers * 2:
                    try:
                        inflight.add(ex.submit(work, next(it)))
                    except StopIteration:
                        exhausted = True
                if not inflight:
                    break
                fin, inflight = cf.wait(inflight, return_when=cf.FIRST_COMPLETED)
                for f in fin:
                    try:
                        ci, out = f.result()
                    except EnginesDown as e:
                        if not down:
                            print(f"    引擎全數失敗：{e}", flush=True)
                        down = True
                        continue
                    except Exception as e:  # noqa: BLE001
                        print(f"    ✗ 批次例外 {type(e).__name__}: {str(e)[:100]}", flush=True)
                        continue
                    for t, z, why in out:
                        if z:
                            pending.append({"chunk_index": ci, "row": t["row"], "en": t["en"], "zh": z,
                                            "n": t["n"], "label": t["label"]})
                            done += 1
                        else:
                            fails[t["key"]] = fails.get(t["key"], 0) + 1
                            print(f"    ✗ #{ci} 列{t['row']} 不過閘：{why}", flush=True)
                if time.time() - last_save > 120:
                    flush()
                    last_save = time.time()
                    print(f"    …{bid[:8]} 已補 {done}/{total}", flush=True)
                if down and not inflight:
                    break
    finally:
        flush()
    if push and done:
        import standardize_ebook as se
        o = CH / f"{bid}.jsonl"
        try:
            chunks2 = load(bid)
            se.push_to_r2(bid, o)
            se.update_db(bid, chunks2)
        except Exception as e:  # noqa: BLE001
            print(f"    推 R2／DB 失敗：{type(e).__name__} {str(e)[:100]}（檔已寫，下次補推）", flush=True)
    return total, done


def all_ids() -> list[str]:
    return [l.strip() for l in (OUT / "ids37.txt").read_text(encoding="utf-8").split() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book")
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    ids = [a.book] if a.book else all_ids()
    fails = load_fails()
    if a.count:
        n = 0
        for bid in ids:
            n += sum(len(find_targets(c, fails.get(bid))) for c in load(bid))
        print(n)
        return 0
    for bid in ids:
        total, done = fill_book(bid, a.apply, a.limit)
        print(f"{bid[:8]} 缺譯 {total}" + (f"  本輪補 {done}" if a.apply else ""), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
