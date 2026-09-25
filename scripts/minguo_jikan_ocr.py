# -*- coding: utf-8 -*-
"""《民國佛教期刊文獻集成》全集 OCR 管線（可中斷續跑；太虛相關篇目優先）。

整體：Drive 集成夾裡每一冊純影像 PDF → 本機 MinerU 逐頁文字 → 每冊一個逐頁 JSONL →
按 DILA 篇目切成單篇 .txt。工作單位是「一冊的一段 PDF 頁」（segment），狀態檔記到頁，
筆電休眠、闔蓋、班次被砍，下一班從沒做完的那一頁接著做。

    Drive 集成夾（G:\\…\\研究資料\\民國與台灣佛教史\\民國佛教期刊文獻集成\\）
        正編\\*.pdf、補編\\*.pdf              整冊原刊影印（haichaoyin_commons_fetch.py 下載）
        _篇目_全集.tsv                        DILA 整庫篇目（minguo_jikan_dila_catalog.py）
        _篇目_太虛相關_全集.tsv               太虛優先清單（同上）
        _OCR\\<叢刊><冊>.jsonl                 逐頁 OCR（一行一個 PDF 頁；欄位見 page_record()）
        _OCR\\單篇\\<叢刊><冊>\\<冊>_<起-訖>_<篇名>.txt   依篇目切出的單篇（頁標頭沿用 2026-09-24 那 18 件）
        _OCR\\_稽核\\<叢刊><冊>\\p<集成頁>.png      每冊完成後抽 3 頁的影像，配 log 裡的文字對看字序
    repo
        scripts/state/minguo_jikan_ocr.json    狀態（每冊：頁數、偏移、已完成頁段、失敗段、已切篇）
        output/minguo_jikan/                   log 與暫存

優先順序：太虛清單裡「機構」關鍵字（世界佛學苑／世苑／漢藏教理院／武昌佛學院／閩南佛學院／
柏林教理院／巴利三藏院／錫蘭留學）的篇 → 法舫／法尊 → 作者太虛／篇名含太虛 → 之後才是整冊
（太虛命中最多的冊先）。同一頁只 OCR 一次：優先篇做過的頁，整冊時直接跳過。

引擎：
    --engine auto（預設）先試 GPU（mineru_ocr.py 的 GPU 鎖，被佔就回 4），被佔就這一班改走
    `--device cpu`（不佔鎖，約 37 秒／頁，昨天實測）。GPU 段 100 頁、CPU 段 20 頁。
    🚨 電子圖書館的 `mineru_ocr.py queue` 是**整個佇列期間**握著鎖（acquire 在 main()、release 在
    finally），不是每本之間放開；fleet keeper 又會一直重拉到佇列空。所以佇列沒吃完之前 GPU 不會
    輪到我們，本管線靠 CPU 段慢慢推，不搶、不殺。
    離開碼沿用 mineru_ocr.py：3＝環境壞整場停；4＝GPU 忙不是失敗；2＝重複幻覺（段對半切再試）；
    1＝這段的問題（記失敗，連錯 3 段整場停並放回）。

頁碼：
    集成頁 ＝ PDF 頁序（0 起）− offset。offset 每冊一個（昨天核過 22 冊：多數 2、正編 202–204 為 3、
    補編 1）；沒核過的冊先假設 2、頁段前後各多留 2 頁，再從 MinerU 撿到的頁底「-N-」集成頁碼學出來
    （眾數、至少 3 頁、六成以上同意、且落在 0–8 之間才採信）。
    原刊頁 只由篇目推算（某篇集成 a–b 對應原刊 o 起 → 頁 P 的原刊頁＝o＋(P−a)），多篇打架就留空。
    🚨 推不出就是空，不准編。MinerU 撿到的所有頁碼原文另存 page_numbers 給人核對。

用法：
    python -X utf8 scripts/minguo_jikan_ocr.py status
    python -X utf8 scripts/minguo_jikan_ocr.py run --max-minutes 25            # 排程每班
    python -X utf8 scripts/minguo_jikan_ocr.py run --dry-run                   # 只印計畫
    python -X utf8 scripts/minguo_jikan_ocr.py run --engine cpu --only 正編187  # 指定冊
    python -X utf8 scripts/minguo_jikan_ocr.py import-legacy                   # 登記昨天那 18 件
    python -X utf8 scripts/minguo_jikan_ocr.py cut [--vol 正編187]             # 重切單篇
    python -X utf8 scripts/minguo_jikan_ocr.py audit --vol 正編187             # 稽核一冊
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable
MINERU_OCR = REPO / "scripts" / "mineru_ocr.py"
STATE = REPO / "scripts" / "state" / "minguo_jikan_ocr.json"
RUN_LOCK = REPO / "scripts" / "state" / "minguo_jikan_ocr.lock"
TMP = REPO / "output" / "minguo_jikan" / "tmp"
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\民國佛教期刊文獻集成")
LEGACY_DIR = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\民國與台灣佛教史\太虛研究\集成影印")
CAT_FULL = DRIVE / "_篇目_全集.tsv"
CAT_TAIXU = DRIVE / "_篇目_太虛相關_全集.tsv"
OCR_DIR = DRIVE / "_OCR"
CUT_DIR = OCR_DIR / "單篇"
AUDIT_DIR = OCR_DIR / "_稽核"

SEG_GPU = 100
SEG_CPU = 20
DEFAULT_OFFSET = 2
UNKNOWN_MARGIN = 2
SEC_PER_PAGE = {"cpu": 37.0, "cuda": 3.0}      # 初值，跑過會用實測值覆蓋
STARTUP_SEC = 60
FOOTNOTE_RULE = "—" * 15                        # 與 mineru_ocr.FOOTNOTE_RULE 同

# 昨天（2026-09-24）逐冊抽 4 處以上核過的偏移：PDF 頁序（0 起）＝集成頁＋offset
SEED_OFFSETS = {**{f"正編{v}": 2 for v in (80, 170, 171, 172, 174, 175, 180, 181, 182, 186, 187, 188,
                                          192, 193, 194, 195)},
                "正編202": 3, "正編203": 3, "正編204": 3, "補編53": 1, "補編74": 1}

PRIO_GAP = 4                                    # 優先頁段之間空不到 4 頁就併成一段
# 優先級：0 世苑本身 → 1 太虛系各院與留學團 → 2 法舫／法尊 → 3 其餘（篇名含太虛、作者太虛）
TIER_KW = (("世界佛學苑", "世苑"),
           ("漢藏教理院", "武昌佛學院", "閩南佛學院", "柏林教理院", "巴利三藏院", "錫蘭留學"),
           ("法舫", "法尊"))


# ── 純函式：頁段 ──────────────────────────────────────────────────────────────

def merge_ranges(ranges, gap: int = 0) -> list[list[int]]:
    """[(s,e)…] 閉區間 → 合併排序（相鄰也併；gap>0 時中間空不到 gap 頁的也併，
    因為 MinerU 每段起跑要十幾秒，1 頁一段太浪費，多讀幾頁整冊時反正也要）。"""
    out: list[list[int]] = []
    for s, e in sorted((int(a), int(b)) for a, b in ranges if a is not None and b >= a):
        if out and s <= out[-1][1] + 1 + gap:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def subtract_ranges(want, done) -> list[list[int]]:
    """want − done（都是閉區間清單）→ 還沒做的段。"""
    done = merge_ranges(done)
    out = []
    for s, e in merge_ranges(want):
        cur = s
        for ds, de in done:
            if de < cur:
                continue
            if ds > e:
                break
            if ds > cur:
                out.append([cur, ds - 1])
            cur = max(cur, de + 1)
            if cur > e:
                break
        if cur <= e:
            out.append([cur, e])
    return out


def chunk_ranges(ranges, size) -> list[list[int]]:
    out = []
    for s, e in ranges:
        while s <= e:
            out.append([s, min(e, s + size - 1)])
            s += size
    return out


def pages_in(ranges) -> int:
    return sum(e - s + 1 for s, e in merge_ranges(ranges))


def covered(ranges, s, e) -> bool:
    return not subtract_ranges([[s, e]], ranges)


def page_range(s: str):
    m = re.match(r"(\d+)(?:\s*~\s*(\d+))?", (s or "").strip())
    if not m:
        return None
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    return (a, b) if 0 <= b - a <= 600 else None


def learn_offset(records, lo=0, hi=8, min_n=3, min_share=0.6):
    """由 MinerU 撿到的頁底集成頁碼學 offset。records: [{pdf_index, page_numbers:[str]}]。

    頁面上同時有原刊頁碼與集成頁碼，兩套都可能被撿成 page_number；集成那套的 offset
    落在 0–8，原刊那套一般大很多，所以先用範圍篩，再看眾數同不同意。學不出來回 None。
    """
    cands = []
    for r in records:
        for pn in r.get("page_numbers") or []:
            for d in re.findall(r"\d+", pn):
                off = r["pdf_index"] - int(d)
                if lo <= off <= hi:
                    cands.append(off)
    if len(cands) < min_n:
        return None
    off, n = Counter(cands).most_common(1)[0]
    return off if n >= min_n and n / len(cands) >= min_share else None


def infer_orig_page(jicheng_page: int, rows) -> tuple:
    """篇目推算原刊頁。rows：這一冊的篇目（含 集成頁、原刊頁）。回 (原刊頁 或 None, 依據篇名 或 '')。"""
    votes = {}
    for r in rows:
        pr = page_range(r.get("集成頁", ""))
        if not pr or not (pr[0] <= jicheng_page <= pr[1]):
            continue
        om = re.match(r"(\d+)", (r.get("原刊頁") or "").strip())
        if not om:
            continue
        val = int(om.group(1)) + (jicheng_page - pr[0])
        votes.setdefault(val, r.get("篇名", ""))
    if len(votes) == 1:
        (val, title), = votes.items()
        return val, title
    return None, ""


def split_content(content: str) -> tuple[str, list[str]]:
    """mineru_ocr 把註腳接在正文後、用一條長橫線隔開；這裡拆回來。"""
    if "\n" + FOOTNOTE_RULE + "\n" in content:
        body, notes = content.split("\n" + FOOTNOTE_RULE + "\n", 1)
        return body.strip(), [n for n in notes.split("\n") if n.strip()]
    return content, []


def looks_looping(text: str) -> bool:
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        from ocr_repetition import looks_looping as _ll
        return _ll(text)
    except Exception:
        return False


def safe_name(s: str, n=60) -> str:
    return re.sub(r'[\\/:*?"<>|\r\n\t]', "_", s).strip()[:n] or "無題"


def vol_label(series: str, vol: int) -> str:
    return f"{series}{vol}"


# ── 狀態檔 ───────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"volumes": {}, "legacy": [], "sec_per_page": dict(SEC_PER_PAGE), "runs": []}


def save_state(st: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, STATE)


def vol_state(st: dict, label: str) -> dict:
    v = st["volumes"].setdefault(label, {})
    v.setdefault("done", [])
    v.setdefault("failed", {})
    v.setdefault("cut", [])
    if "offset" not in v:
        if label in SEED_OFFSETS:
            v["offset"], v["offset_source"] = SEED_OFFSETS[label], "seed-2026-09-24"
        else:
            v["offset"], v["offset_source"] = None, "unknown"
    return v


# ── Drive 上有哪些冊 ──────────────────────────────────────────────────────────

def find_volumes() -> dict[str, Path]:
    out = {}
    for series in ("正編", "補編"):
        d = DRIVE / series
        if not d.exists():
            continue
        for f in d.glob("*.pdf"):
            m = re.search(r"第(\d+)卷", f.name)
            if m and not f.name.endswith(".part"):
                out[vol_label(series, int(m.group(1)))] = f
    return out


def pdf_pages(path: Path) -> int:
    import fitz
    with fitz.open(path) as d:
        return d.page_count


# ── 篇目 ─────────────────────────────────────────────────────────────────────

def read_tsv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load_catalogs() -> tuple[list[dict], list[dict]]:
    """(整庫篇目, 太虛清單)。整庫沒抓完時整庫那份用太虛清單頂著。"""
    taixu = read_tsv(CAT_TAIXU)
    full = read_tsv(CAT_FULL) or taixu
    return full, taixu


def rows_by_volume(rows) -> dict[str, list[dict]]:
    by = defaultdict(list)
    for r in rows:
        if (r.get("冊") or "").isdigit() and r.get("叢刊") in ("正編", "補編"):
            by[vol_label(r["叢刊"], int(r["冊"]))].append(r)
    return by


def priority_tier(row: dict) -> int:
    hits = row.get("命中關鍵字", "")
    for tier, kws in enumerate(TIER_KW):
        if any(k in hits for k in kws):
            return tier
    return len(TIER_KW)


def row_id(row: dict) -> str:
    return f"{row.get('集成頁', '')}|{row.get('dila_id') or row.get('篇名', '')}"


# ── 逐頁 JSONL ───────────────────────────────────────────────────────────────

def jsonl_path(label: str) -> Path:
    return OCR_DIR / f"{label}.jsonl"


def read_jsonl(label: str) -> dict[int, dict]:
    p = jsonl_path(label)
    out = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[int(r["pdf_index"])] = r
    return out


def write_jsonl(label: str, pages: dict[int, dict]) -> None:
    p = jsonl_path(label)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for idx in sorted(pages):
            f.write(json.dumps(pages[idx], ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def page_record(label: str, chunk: dict, engine: str, ocr_at: str) -> dict:
    """mineru_ocr `run --pdf` 的一個 chunk → 本管線的一頁。集成頁／原刊頁之後由 refresh_pages 填。"""
    body, notes = split_content(chunk.get("content") or "")
    series, vol = label[:2], int(label[2:])
    return {
        "叢刊": series, "冊": vol,
        "pdf_index": int(chunk["page_number"]) - 1,
        "集成頁": None, "原刊頁": None, "原刊頁依據": "",
        "text": body,
        "footnotes": notes,
        "headers": chunk.get("headers") or [],
        "page_numbers": chunk.get("page_numbers") or [],
        "printed_page": chunk.get("printed_page"),
        "engine": f"mineru-{engine}", "ocr_at": ocr_at,
    }


def refresh_pages(pages: dict[int, dict], offset, cat_rows) -> None:
    """依現在的 offset 與篇目，重算每頁的集成頁與原刊頁（offset 學到之後要整冊重算）。"""
    for idx, r in pages.items():
        if offset is None:
            r["集成頁"], r["原刊頁"], r["原刊頁依據"] = None, None, ""
            continue
        jp = idx - offset
        r["集成頁"] = jp if jp >= 1 else None
        if r["集成頁"] is not None:
            val, why = infer_orig_page(jp, cat_rows)
            r["原刊頁"], r["原刊頁依據"] = val, (f"篇目推算：{why}" if val is not None else "")
        else:
            r["原刊頁"], r["原刊頁依據"] = None, ""


# ── 跑一段 ───────────────────────────────────────────────────────────────────

def run_segment(pdf: Path, s: int, e: int, device: str, out: Path) -> tuple[int, str]:
    argv = [PY, "-X", "utf8", str(MINERU_OCR), "run", "--pdf", str(pdf), "--out", str(out),
            "--start", str(s), "--end", str(e)]
    if device == "cpu":
        argv += ["--device", "cpu"]
    proc = subprocess.run(argv, cwd=str(REPO), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    tail = " | ".join(ln.strip() for ln in (proc.stdout or "").splitlines()[-4:] if ln.strip())
    if proc.returncode not in (0, 4):
        tail += " || " + " | ".join(ln.strip() for ln in (proc.stderr or "").splitlines()[-3:])
    return proc.returncode, tail


def plan_segments(st: dict, vols: dict[str, Path], full_by: dict, taixu_by: dict,
                  only: str | None, seg_size: int, include_whole: bool) -> list[dict]:
    """這一班要做的段，依優先序。每段：{label, s, e, why}。"""
    plan: list[dict] = []
    # 一、太虛優先篇
    prio_rows = []
    for label, rows in taixu_by.items():
        if label not in vols or (only and label != only):
            continue
        for r in rows:
            pr = page_range(r.get("集成頁", ""))
            if pr:
                prio_rows.append((priority_tier(r), label, pr, r))
    prio_rows.sort(key=lambda x: (x[0], x[1][:2], int(x[1][2:]), x[2]))
    want_by_label: dict[str, list] = defaultdict(list)
    tier_by_label: dict[str, int] = {}
    for tier, label, (a, b), r in prio_rows:
        v = vol_state(st, label)
        off = v["offset"]
        if off is None:
            s, e = a + DEFAULT_OFFSET - UNKNOWN_MARGIN, b + DEFAULT_OFFSET + UNKNOWN_MARGIN
        else:
            s, e = a + off, b + off
        n = v.get("pages") or 10 ** 6
        s, e = max(0, s), min(n - 1, e)
        if s <= e:
            want_by_label[label].append([s, e])
            tier_by_label[label] = min(tier, tier_by_label.get(label, 9))
    for label in sorted(want_by_label, key=lambda l: (tier_by_label[l], l[:2], int(l[2:]))):
        v = vol_state(st, label)
        todo = subtract_ranges(merge_ranges(want_by_label[label], gap=PRIO_GAP), v["done"])
        todo = [rg for rg in todo if not _given_up(v, rg)]
        for s, e in chunk_ranges(todo, seg_size):
            plan.append({"label": label, "s": s, "e": e, "why": f"太虛優先（第{tier_by_label[label]}級）"})
    if not include_whole:
        return plan
    # 二、整冊：太虛命中多的冊先，其餘依叢刊冊次
    hits = {label: len(rows) for label, rows in taixu_by.items()}
    order = sorted(vols, key=lambda l: (-hits.get(l, 0), l[:2], int(l[2:])))
    for label in order:
        if only and label != only:
            continue
        v = vol_state(st, label)
        n = v.get("pages")
        if not n:
            continue
        todo = subtract_ranges([[0, n - 1]], v["done"])
        todo = [rg for rg in todo if not _given_up(v, rg)]
        for s, e in chunk_ranges(todo, seg_size):
            plan.append({"label": label, "s": s, "e": e, "why": "整冊"})
    return plan


def _given_up(v: dict, rg) -> bool:
    """失敗 3 次以上的段先不再排（--retry-failed 會清掉失敗紀錄）。"""
    return v["failed"].get(f"{rg[0]}-{rg[1]}", {}).get("n", 0) >= 3


# ── 切單篇 ───────────────────────────────────────────────────────────────────

def cut_text(label: str, row: dict, pages: dict[int, dict], offset: int, engine_note: str) -> str:
    series, vol = label[:2], label[2:]
    a, b = page_range(row["集成頁"])
    src = row.get("原書資訊原文") or row.get("原刊", "")
    lines = [f"《民國佛教期刊文獻集成》{series}第{vol}冊，頁 {a}" + (f"–{b}" if b != a else "")
             + f"：{row.get('篇名', '')}（{src}）",
             f"OCR：本機 MinerU（pipeline 後端、{engine_note}、lang=ch）；未校對，直排轉橫排的字序與錯字須對照影像"
             f"（已知系統性錯字：敎→軟／敘）。",
             "每頁標【集成 冊 頁 N｜原刊 頁 M】；原刊頁碼由篇目資料的起始頁推算，推不出者標「?」。"]
    if row.get("作者"):
        lines[0] += f"　作者：{row['作者']}"
    for jp in range(a, b + 1):
        r = pages.get(jp + offset)
        if not r:
            continue
        orig = r.get("原刊頁")
        lines.append(f"\n【集成 {label} 頁 {jp}｜原刊 頁 {orig if orig is not None else '?'}】")
        lines.append(r.get("text") or "（無正文）")
        if r.get("footnotes"):
            lines.append(FOOTNOTE_RULE)
            lines.extend(r["footnotes"])
    return "\n".join(lines) + "\n"


def cut_volume(st: dict, label: str, cat_rows, pages: dict[int, dict], legacy_keys: set,
               force=False) -> int:
    v = vol_state(st, label)
    off = v["offset"]
    if off is None or not cat_rows:
        return 0
    engines = {r.get("engine", "") for r in pages.values()}
    engine_note = "CPU" if engines == {"mineru-cpu"} else ("GPU" if engines == {"mineru-cuda"} else "CPU／GPU 混跑")
    n = 0
    done_set = set(v["cut"])
    for row in cat_rows:
        pr = page_range(row.get("集成頁", ""))
        if not pr:
            continue
        a, b = pr
        rid = row_id(row)
        if (label, a, b) in legacy_keys:
            continue                       # 2026-09-24 那 18 件，不重做
        if not force and rid in done_set:
            continue
        if not covered(v["done"], a + off, b + off):
            continue
        fname = f"{label[2:]}_{a}" + (f"-{b}" if b != a else "") + f"_{safe_name(row.get('篇名', ''))}.txt"
        out = CUT_DIR / label / fname
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(cut_text(label, row, pages, off, engine_note), encoding="utf-8")
        done_set.add(rid)
        n += 1
    v["cut"] = sorted(done_set)
    return n


# ── 稽核 ─────────────────────────────────────────────────────────────────────

def audit_volume(label: str, pdf: Path, pages: dict[int, dict], offset, n_pages: int, sample=3) -> dict:
    """一冊做完的自檢：空白率、重複幻覺、迴圈頁；抽 3 頁存影像＋印文字開頭讓人對字序。"""
    import fitz
    texts = [(idx, (pages.get(idx) or {}).get("text") or "") for idx in range(n_pages)]
    blank = [idx for idx, t in texts if len(t.strip()) < 30]
    loops = [idx for idx, t in texts if looks_looping(t)]
    rep_ok, rep_msg = True, ""
    try:
        sys.path.insert(0, str(REPO / "scripts"))
        from ocr_repetition import repetition_verdict
        rep_ok, rep_msg = repetition_verdict([{"page": idx + 1, "text": t} for idx, t in texts])
    except Exception as e:
        rep_msg = f"（重複判準沒跑成：{e}）"
    chars = [len(t) for _, t in texts]
    rep = {"pages": n_pages, "blank": len(blank), "blank_rate": round(len(blank) / max(1, n_pages), 3),
           "chars_per_page": round(sum(chars) / max(1, n_pages)), "loops": loops[:20],
           "repetition_ok": rep_ok, "repetition_msg": rep_msg, "samples": []}
    body_idx = [idx for idx, t in texts if len(t) >= 200]
    picks = [body_idx[len(body_idx) * k // (sample + 1)] for k in range(1, sample + 1)] if body_idx else []
    d = AUDIT_DIR / label
    d.mkdir(parents=True, exist_ok=True)
    try:
        with fitz.open(pdf) as doc:
            for idx in picks:
                jp = idx - offset if offset is not None else None
                png = d / (f"p{jp}.png" if jp is not None else f"idx{idx}.png")
                doc[idx].get_pixmap(dpi=100).save(str(png))
                t = pages[idx]["text"]
                rep["samples"].append({"pdf_index": idx, "集成頁": jp, "png": str(png),
                                       "chars": len(t), "head": t[:80].replace("\n", "⏎")})
    except Exception as e:
        rep["samples_error"] = str(e)[:160]
    return rep


def print_audit(label: str, rep: dict) -> None:
    print(f"  ▣ 稽核 {label}：{rep['pages']} 頁，空白 {rep['blank']}（{rep['blank_rate']:.1%}），"
          f"每頁 {rep['chars_per_page']} 字，迴圈頁 {len(rep['loops'])}，"
          f"重複幻覺 {'通過' if rep['repetition_ok'] else '🚨 ' + rep['repetition_msg']}")
    if rep["loops"]:
        print(f"    🚨 迴圈頁（pdf_index）：{rep['loops']} → 已從完成頁段移除，下一班重做一次")
    for smp in rep["samples"]:
        print(f"    抽頁 集成 {smp['集成頁']}（pdf {smp['pdf_index']}）{smp['chars']} 字｜{smp['head']}")
        print(f"      影像：{smp['png']}")


# ── 指令 ─────────────────────────────────────────────────────────────────────

def refresh_volume_pages(st: dict, vols: dict[str, Path]) -> None:
    for label, pdf in vols.items():
        v = vol_state(st, label)
        if not v.get("pages"):
            try:
                v["pages"] = pdf_pages(pdf)
            except Exception as e:
                print(f"  ⚠ 讀不到頁數 {label}：{str(e)[:100]}")


def status_lines(st: dict, vols: dict[str, Path], taixu_by: dict) -> list[str]:
    total_pages = sum((vol_state(st, l).get("pages") or 0) for l in vols)
    done_pages = sum(pages_in(vol_state(st, l)["done"]) for l in vols)
    full_vols = [l for l in vols if vol_state(st, l).get("pages") and covered(vol_state(st, l)["done"], 0, vol_state(st, l)["pages"] - 1)]
    prio_rows = prio_cov = prio_pages = prio_pages_done = 0
    missing_vols = set()
    for label, rows in taixu_by.items():
        if label not in vols:
            missing_vols.add(label)
            continue
        v = vol_state(st, label)
        for r in rows:
            pr = page_range(r.get("集成頁", ""))
            if not pr:
                continue
            prio_rows += 1
            off = v["offset"]
            if off is None:
                s, e = pr[0] + DEFAULT_OFFSET - UNKNOWN_MARGIN, pr[1] + DEFAULT_OFFSET + UNKNOWN_MARGIN
            else:
                s, e = pr[0] + off, pr[1] + off
            prio_pages += e - s + 1
            if covered(v["done"], s, e):
                prio_cov += 1
                prio_pages_done += e - s + 1
    cut_n = sum(len(vol_state(st, l)["cut"]) for l in vols)
    return [
        f"冊：Drive 有 {len(vols)} 冊（正編 {sum(1 for l in vols if l.startswith('正編'))}、補編 {sum(1 for l in vols if l.startswith('補編'))}），"
        f"整冊完成 {len(full_vols)} 冊",
        f"頁：共 {total_pages:,} 頁，已 OCR {done_pages:,} 頁（{done_pages / max(1, total_pages):.1%}）",
        f"太虛優先篇：{prio_rows} 篇（涉及 {len(taixu_by)} 冊，其中 {len(missing_vols)} 冊尚未下載），"
        f"已完成 {prio_cov} 篇；優先頁 {prio_pages:,}，已做 {prio_pages_done:,}",
        f"單篇已切 {cut_n} 件；2026-09-24 舊件 {len(st.get('legacy', []))} 件；"
        f"實測秒／頁 cpu {st['sec_per_page'].get('cpu', 0):.1f}、cuda {st['sec_per_page'].get('cuda', 0):.1f}",
    ]


def cmd_status(a) -> int:
    st = load_state()
    vols = find_volumes()
    refresh_volume_pages(st, vols)
    _, taixu = load_catalogs()
    for ln in status_lines(st, vols, rows_by_volume(taixu)):
        print(ln)
    save_state(st)
    return 0


def take_run_lock() -> bool:
    RUN_LOCK.parent.mkdir(parents=True, exist_ok=True)
    if RUN_LOCK.exists():
        try:
            pid = int(RUN_LOCK.read_text(encoding="utf-8").split()[0])
            r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                                f"if (Get-Process -Id {pid} -ErrorAction SilentlyContinue) {{exit 0}} else {{exit 1}}"],
                               capture_output=True, timeout=20)
            if r.returncode == 0 and pid != os.getpid():
                print(f"⛔ 另一班還在跑（PID {pid}），這班退出")
                return False
        except Exception:
            pass
    RUN_LOCK.write_text(f"{os.getpid()} {time.strftime('%Y-%m-%d %H:%M:%S')}", encoding="utf-8")
    return True


def release_run_lock() -> None:
    try:
        if RUN_LOCK.exists() and RUN_LOCK.read_text(encoding="utf-8").split()[0] == str(os.getpid()):
            RUN_LOCK.unlink()
    except Exception:
        pass


def cmd_run(a) -> int:
    t_run = time.time()
    print(f"=== minguo_jikan_ocr run {time.strftime('%Y-%m-%d %H:%M:%S')} engine={a.engine} max={a.max_minutes}min ===")
    if not (DRIVE.exists() and Path(r"G:\我的雲端硬碟").exists()):
        print("⛔ G: 不在（Drive 卡住），整場停")
        return 3
    st = load_state()
    vols = find_volumes()
    refresh_volume_pages(st, vols)
    full, taixu = load_catalogs()
    full_by, taixu_by = rows_by_volume(full), rows_by_volume(taixu)
    if a.retry_failed:
        for v in st["volumes"].values():
            v["failed"] = {}
    for ln in status_lines(st, vols, taixu_by):
        print("  " + ln)
    legacy_keys = {(x["label"], x["a"], x["b"]) for x in st.get("legacy", [])}

    device = "cpu" if a.engine == "cpu" else "cuda"
    seg = SEG_CPU if device == "cpu" else SEG_GPU
    plan = plan_segments(st, vols, full_by, taixu_by, a.only, seg, include_whole=not a.priority_only)
    prio_n = sum(1 for p in plan if p["why"].startswith("太虛"))
    print(f"  計畫：{len(plan)} 段（優先 {prio_n} 段、整冊 {len(plan) - prio_n} 段），本班引擎先試 {device}")
    if a.dry_run:
        for p in plan[:a.show]:
            print(f"    {p['label']} pdf {p['s']}–{p['e']}（{p['e'] - p['s'] + 1} 頁）{p['why']}")
        if len(plan) > a.show:
            print(f"    …其餘 {len(plan) - a.show} 段")
        save_state(st)
        return 0
    if not plan:
        print("  沒有待做的段。MINGUO_JIKAN_DONE")
        save_state(st)
        return 0
    if not take_run_lock():
        return 0
    TMP.mkdir(parents=True, exist_ok=True)
    try:
        from keep_awake import keep_awake       # 別讓待機把這一班砍了
        keep_awake()
    except Exception:
        pass

    deadline = t_run + a.max_minutes * 60 if a.max_minutes else None
    streak: list[str] = []
    done_segs = fail_segs = 0
    touched: set[str] = set()
    rc = 0
    try:
        queue = list(plan)
        while queue:
            p = queue.pop(0)
            label, s, e = p["label"], p["s"], p["e"]
            v = vol_state(st, label)
            n_pages = e - s + 1
            est = n_pages * st["sec_per_page"].get(device, SEC_PER_PAGE[device]) + STARTUP_SEC
            if deadline and time.time() + est > deadline + 180:
                # 段太大塞不進剩餘時間就縮到塞得進的大小；連 3 頁都塞不進就收班
                fit = int((deadline + 180 - time.time() - STARTUP_SEC) / max(1.0, st["sec_per_page"].get(device, SEC_PER_PAGE[device])))
                if fit < 3:
                    print(f"  ⏱ 已達 {a.max_minutes} 分鐘上限，其餘留給下一班")
                    break
                queue.insert(0, {**p, "s": s + fit, "e": e})
                e, n_pages = s + fit - 1, fit
            # 已經做過的頁（優先篇做過、整冊再來）直接跳
            todo = subtract_ranges([[s, e]], v["done"])
            if not todo:
                continue
            if todo != [[s, e]]:
                queue[:0] = [{**p, "s": ts, "e": te} for ts, te in todo]
                continue
            pdf = vols[label]
            out = TMP / f"{label}_{s}-{e}.jsonl"
            print(f"\n▶ {label} pdf {s}–{e}（{n_pages} 頁，集成約 {s - (v['offset'] or DEFAULT_OFFSET)}–{e - (v['offset'] or DEFAULT_OFFSET)}）"
                  f" {p['why']} [{device}]", flush=True)
            t0 = time.time()
            code, tail = run_segment(pdf, s, e, device, out)
            dt = time.time() - t0
            if code == 4:
                print(f"  GPU 被佔（{tail[-160:]}）→ 這一班改走 CPU")
                device, seg = "cpu", SEG_CPU
                queue[:0] = [{**p, "s": ts, "e": te} for ts, te in chunk_ranges([[s, e]], seg)]
                queue = [q for i, q in enumerate(queue) if not (i > 0 and q["label"] == label and q["s"] == s and q["e"] == e)]
                continue
            if code == 3:
                print(f"  ⛔ 環境問題，整場停：{tail[-300:]}")
                rc = 3
                break
            if code != 0 or not out.exists():
                key = f"{s}-{e}"
                f = v["failed"].setdefault(key, {"n": 0})
                f["n"] += 1
                f["last"] = tail[-300:]
                f["at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                fail_segs += 1
                streak.append(f"{label}:{key}")
                print(f"  ✗ exit {code}（{dt:.0f}s）：{tail[-300:]}")
                if code == 2 and n_pages > 1:
                    mid = (s + e) // 2
                    print(f"  → 重複幻覺判準擋下，對半切再試：{s}–{mid}、{mid + 1}–{e}")
                    queue[:0] = [{**p, "s": s, "e": mid}, {**p, "s": mid + 1, "e": e}]
                if len(streak) >= 3:
                    print(f"\n⛔ 連續 {len(streak)} 段失敗（{', '.join(streak)}）—— 不是這幾頁的問題，整場停。")
                    rc = 3
                    break
                save_state(st)
                continue
            streak.clear()
            chunks = [json.loads(ln) for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
            out.unlink(missing_ok=True)
            got = sorted(int(c["page_number"]) - 1 for c in chunks)
            if got != list(range(s, e + 1)):
                print(f"  ✗ 頁數對不上：要 {s}–{e}，拿到 {got[:3]}…{got[-3:]}（{len(got)}）→ 記失敗")
                v["failed"].setdefault(f"{s}-{e}", {"n": 0})["n"] += 1
                fail_segs += 1
                save_state(st)
                continue
            ocr_at = time.strftime("%Y-%m-%d %H:%M:%S")
            pages = read_jsonl(label)
            for c in chunks:
                pages[int(c["page_number"]) - 1] = page_record(label, c, device, ocr_at)
            # 學 offset（只在還不知道時）
            if v["offset"] is None:
                off = learn_offset(list(pages.values()))
                if off is not None:
                    v["offset"], v["offset_source"] = off, f"learned {ocr_at}"
                    print(f"  ◎ 學到 {label} 的 offset={off}（PDF 頁序＝集成頁＋{off}）")
            refresh_pages(pages, v["offset"], full_by.get(label, []))
            write_jsonl(label, pages)
            v["done"] = merge_ranges(v["done"] + [[s, e]])
            v["failed"].pop(f"{s}-{e}", None)
            touched.add(label)
            done_segs += 1
            spp = (dt - STARTUP_SEC / 2) / n_pages if n_pages else 0
            if spp > 0:
                old = st["sec_per_page"].get(device, SEC_PER_PAGE[device])
                st["sec_per_page"][device] = round(0.7 * old + 0.3 * spp, 1)
            chars = sum(len(pg["text"]) for pg in (pages[i] for i in range(s, e + 1)))
            print(f"  ✓ {n_pages} 頁 {dt:.0f}s（{spp:.1f}s/頁）每頁 {chars // n_pages} 字；"
                  f"{label} 已 OCR {pages_in(v['done'])}/{v.get('pages')} 頁")
            if v["offset"] is not None:
                nc = cut_volume(st, label, full_by.get(label, []), pages, legacy_keys)
                if nc:
                    print(f"  ✂ 切出單篇 {nc} 件 → {CUT_DIR / label}")
            # 整冊做完 → 稽核
            if v.get("pages") and covered(v["done"], 0, v["pages"] - 1) and not v.get("audited"):
                rep = audit_volume(label, pdf, pages, v["offset"], v["pages"])
                print_audit(label, rep)
                if rep["loops"]:
                    # 迴圈頁重做一次；再迴圈就留著但標 suspect
                    redo = [i for i in rep["loops"] if not pages[i].get("suspect")]
                    for i in redo:
                        pages[i]["suspect"] = True
                    write_jsonl(label, pages)
                    if redo:
                        v["done"] = subtract_ranges(v["done"], [[i, i] for i in redo])
                        continue
                v["audited"] = ocr_at
                v["audit"] = {k: rep[k] for k in ("blank_rate", "chars_per_page", "repetition_ok", "loops")}
            save_state(st)
    finally:
        st["runs"] = (st.get("runs") or [])[-19:] + [{
            "at": time.strftime("%Y-%m-%d %H:%M:%S"), "engine": device, "segments_done": done_segs,
            "segments_failed": fail_segs, "minutes": round((time.time() - t_run) / 60, 1), "rc": rc}]
        save_state(st)
        release_run_lock()
    print(f"\n本班完成 {done_segs} 段、失敗 {fail_segs} 段，{(time.time() - t_run) / 60:.1f} 分鐘；引擎 {device}")
    for ln in status_lines(st, vols, taixu_by):
        print("  " + ln)
    return rc


def cmd_import_legacy(a) -> int:
    """把 2026-09-24 已 OCR 的 18 件 .txt 登記成完成（並把它們的頁併進逐頁 JSONL）。"""
    st = load_state()
    vols = find_volumes()
    refresh_volume_pages(st, vols)
    full, _ = load_catalogs()
    full_by = rows_by_volume(full)
    known = {(x["label"], x["a"], x["b"]) for x in st.get("legacy", [])}
    n_new = 0
    for txt in sorted(LEGACY_DIR.glob("*/*.txt")):
        m = re.match(r"(正編|補編)(\d+)_(\d+)(?:-(\d+))?_", txt.name)
        if not m:
            continue
        label = vol_label(m.group(1), int(m.group(2)))
        a_, b_ = int(m.group(3)), int(m.group(4) or m.group(3))
        if (label, a_, b_) in known:
            continue
        v = vol_state(st, label)
        off = v["offset"]
        body = txt.read_text(encoding="utf-8")
        found = re.findall(r"【集成 (正編|補編)(\d+) 頁 (\d+)｜原刊 頁 ([^】]*)】\n(.*?)(?=\n【集成 |\Z)", body, re.S)
        if off is None or not found or label not in vols:
            print(f"  略過 {txt.name}：offset={off}、頁 {len(found)}、PDF {'有' if label in vols else '無'}")
            continue
        pages = read_jsonl(label)
        idxs = []
        head = "\n".join(body.splitlines()[:3])
        engine = "gemini" if "Gemini" in head else "mineru-cpu"     # 204 那件是 Gemini 讀的
        for _, _, jp, orig, text in found:
            jp = int(jp)
            idx = jp + off
            idxs.append(idx)
            if idx in pages:
                continue
            pages[idx] = {"叢刊": label[:2], "冊": int(label[2:]), "pdf_index": idx, "集成頁": jp,
                          "原刊頁": None, "原刊頁依據": "", "text": text.strip(), "footnotes": [],
                          "headers": [], "page_numbers": [], "printed_page": None,
                          "engine": engine, "ocr_at": "2026-09-24", "legacy": str(txt)}
        refresh_pages(pages, off, full_by.get(label, []))
        write_jsonl(label, pages)
        v["done"] = merge_ranges(v["done"] + [[min(idxs), max(idxs)]])
        st.setdefault("legacy", []).append({"label": label, "a": a_, "b": b_, "path": str(txt), "pages": len(found)})
        known.add((label, a_, b_))
        n_new += 1
        print(f"  登記 {label} 頁 {a_}–{b_}（{len(found)} 頁）← {txt.name}")
    save_state(st)
    print(f"新登記 {n_new} 件，合計 {len(st.get('legacy', []))} 件")
    return 0


def cmd_cut(a) -> int:
    st = load_state()
    vols = find_volumes()
    full, _ = load_catalogs()
    full_by = rows_by_volume(full)
    legacy_keys = {(x["label"], x["a"], x["b"]) for x in st.get("legacy", [])}
    total = 0
    for label in sorted(vols):
        if a.vol and label != a.vol:
            continue
        pages = read_jsonl(label)
        if not pages:
            continue
        v = vol_state(st, label)
        refresh_pages(pages, v["offset"], full_by.get(label, []))
        write_jsonl(label, pages)
        n = cut_volume(st, label, full_by.get(label, []), pages, legacy_keys, force=a.force)
        if n:
            print(f"  {label}：切出 {n} 件")
        total += n
    save_state(st)
    print(f"合計 {total} 件 → {CUT_DIR}")
    return 0


def cmd_audit(a) -> int:
    st = load_state()
    vols = find_volumes()
    label = a.vol
    if label not in vols:
        print(f"Drive 沒有 {label}")
        return 1
    v = vol_state(st, label)
    pages = read_jsonl(label)
    n = v.get("pages") or pdf_pages(vols[label])
    rep = audit_volume(label, vols[label], pages, v["offset"], n)
    print(f"{label}：已 OCR {pages_in(v['done'])}/{n} 頁，offset={v['offset']}（{v.get('offset_source')}）")
    print_audit(label, rep)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.set_defaults(func=cmd_status)
    r = sub.add_parser("run")
    r.add_argument("--engine", choices=["auto", "cpu"], default="auto",
                   help="auto＝先試 GPU（鎖被佔就改 CPU）；cpu＝直接 CPU 不碰鎖")
    r.add_argument("--max-minutes", type=int, default=25, help="不再開新段的時限（0＝不限）")
    r.add_argument("--only", help="只做這一冊，如 正編187")
    r.add_argument("--priority-only", action="store_true", help="只做太虛優先段，不做整冊")
    r.add_argument("--retry-failed", action="store_true", help="清掉失敗紀錄再排")
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--show", type=int, default=30, help="--dry-run 列幾段")
    r.set_defaults(func=cmd_run)
    il = sub.add_parser("import-legacy"); il.set_defaults(func=cmd_import_legacy)
    c = sub.add_parser("cut")
    c.add_argument("--vol"); c.add_argument("--force", action="store_true")
    c.set_defaults(func=cmd_cut)
    au = sub.add_parser("audit"); au.add_argument("--vol", required=True); au.set_defaults(func=cmd_audit)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
