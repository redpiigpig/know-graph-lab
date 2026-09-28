#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""補「有註文、正文卻沒有 [^N] 連結」的註號（2026-09-28 民主妙法：454/597 → 577/597）。

適用：已經走過 consolidate_page_chunks.py 的書——每塊正文後接 15 個以上破折號的分隔線，
下面是 `(N) 註文`（reader 的註釋模式）。OCR 把正文上標註號讀壞，連結程式沒認出來。

兩步，都只在「前後兩個已連好的註號之間」找（[^N-1] 與 [^N+1] 之間），不跨塊：
  1. 規則（零成本）：候選剛好一個才補
     - 上標：「佛寺²出家」→ 註 12；「4²」＝42，前面的一般數字一起換掉
     - 黏年份：「傳人。341941年」→ 註 34
     - 殘缺：「臨濟寺1舉行」→ 註 17（只剩首或尾一位，左右都是中文／標點）
     - 排除：後面接 年月日名人位…（是數量不是註號）、前面是「圖／表」（圖號）
  2. --llm（Gemini→NVIDIA，不耗 Claude）：規則補不到的，請模型讀註文＋區間正文，
     回「註號前緊鄰的 8–15 字」；該字串在區間裡必須剛好出現一次才採用。
     過濾：新註號緊貼另一個 [^M] ＝那一帶原本就排錯，不採用；
           新註號後面殘留的數字若是 N 的開頭（「[^43]4而」），一併清掉。
     區間超過 6,000 字不送（前後註號離太遠，模型會亂猜）。

寫入前留 .jsonl.bak_relink，推 R2＋更新 DB。
  python -X utf8 scripts/relink_missing_footnotes.py --ids <id> [...]            # 乾跑，印每處
  python -X utf8 scripts/relink_missing_footnotes.py --ids <id> --llm            # 加模型那步（乾跑）
  python -X utf8 scripts/relink_missing_footnotes.py --ids <id> --llm --apply
  python -X utf8 scripts/relink_missing_footnotes.py --scan                      # 全館盤點缺連結 → output/toc_audit/footnote_gaps.tsv
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
RULE = re.compile("\n[\u2014\\-]{15,}\n")
SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
CJK_L = "[\u4e00-\u9fff\u3001\u3002\uff0c\uff1b\uff1a\u300d\u300f\uff09)\u2014]"
QTY_AFTER = "年月日名人位歲次件個元美分萬千百十"
MAX_SEG = 6000

PROMPT = """下面是一本中文學術書某段正文，以及其中一則註釋的內容。正文裡這則註釋的註號（第 {n} 號）在 OCR 時遺失了。
請判斷註號原本應該緊接在正文哪幾個字之後。回傳 JSON：{{"after": "註號前緊鄰的 8 到 15 個字，必須一字不差照抄正文"}}。
判斷不出來就回 {{"after": ""}}。只輸出 JSON。

【註 {n} 的內容】
{note}

【正文（註 {prev} 與註 {next} 之間）】
{seg}"""


def split_body(content: str) -> tuple[str, str, str] | None:
    m = RULE.search(content)
    if not m:
        return None
    return content[:m.start()], m.group(0), content[m.end():]


def note_texts(notes: str) -> dict[int, str]:
    return {int(m.group(1)): m.group(2) for m in re.finditer(r"(?m)^\((\d+)\) (.*)$", notes)}


def segment(body: str, n: int) -> tuple[int, int] | None:
    """[^n-1] 之後到 [^n+1] 之前；兩邊都沒錨就不猜。"""
    a = body.find(f"[^{n - 1}]")
    b = body.find(f"[^{n + 1}]")
    if a < 0 and b < 0:
        return None
    lo = a + len(f"[^{n - 1}]") if a >= 0 else 0
    hi = b if b > lo else len(body)
    return lo, hi


def rule_candidates(seg: str, n: int) -> list[tuple[int, int, str]]:
    """純函式：區間內可能是註 n 的位置 [(start, end, 種類)]。"""
    s = str(n)
    out = []
    for m in re.finditer("[0-9]*[⁰¹²³⁴⁵⁶⁷⁸⁹]+", seg):
        if s.endswith(m.group(0).translate(SUP)):
            out.append((m.start(), m.end(), "上標"))
    for m in re.finditer("(?<=" + CJK_L + ")(" + s + r")(?=(1[5-9]|20)\d\d年)", seg):
        out.append((m.start(1), m.end(1), "黏年份"))
    for p in ({s, s[-1], s[0]} if len(s) > 1 else {s}):
        for m in re.finditer("(?<=" + CJK_L + r")(?<!\d)(" + p + r")(?!\d)(?=[\u4e00-\u9fff\u3002\uff0c])", seg):
            if seg[m.end(1):m.end(1) + 1] in QTY_AFTER:
                continue
            if seg[max(0, m.start(1) - 1):m.start(1)] in ("圖", "表"):
                continue
            out.append((m.start(1), m.end(1), "數字" if p == s else "殘缺"))
    return sorted(set(out))


def place_after(seg: str, after: str, n: int) -> str | None:
    """純函式：把 [^n] 插在 after 之後；after 須在 seg 剛好出現一次。套用兩道過濾，不合回 None。"""
    after = (after or "").strip()
    if len(after) < 4 or seg.count(after) != 1:
        return None
    pos = seg.index(after) + len(after)
    tag = f"[^{n}]"
    if seg[pos:pos + 2] == "[^" or seg[max(0, pos - 1):pos] == "]":
        return None                                   # 緊貼其他註號：那一帶原本就排錯
    rest = seg[pos:]
    m = re.match(r"(\d+)(?![\d年月日])", rest)
    if m and str(n).startswith(m.group(1)):
        rest = rest[len(m.group(1)):]                  # 清 OCR 殘留的同號數字
    return seg[:pos] + tag + rest


def relink_chunk(content: str, *, use_llm: bool, log) -> tuple[str, int, int]:
    parts = split_body(content)
    if not parts:
        return content, 0, 0
    body, rule, notes = parts
    by_rule = by_llm = 0
    texts = note_texts(notes)
    for n in sorted(texts):
        if f"[^{n}]" in body:
            continue
        rng = segment(body, n)
        if not rng:
            continue
        lo, hi = rng
        seg = body[lo:hi]
        cands = rule_candidates(seg, n)
        if len(cands) == 1:
            st, en, how = cands[0]
            log(f"  ✓ 註{n} [{how}] …{seg[max(0, st - 12):st]}【{seg[st:en]}】{seg[en:en + 8]}…")
            body = body[:lo] + seg[:st] + f"[^{n}]" + seg[en:] + body[hi:]
            by_rule += 1
            continue
        if not use_llm or len(seg) > MAX_SEG:
            continue
        import chapters_via_llm_toc as cv
        raw, eng = cv.ask_model(PROMPT.format(n=n, note=texts[n][:600], prev=n - 1, next=n + 1, seg=seg))
        m = re.search(r"\{.*\}", raw or "", re.S)
        try:
            after = json.loads(m.group(0)).get("after", "") if m else ""
        except json.JSONDecodeError:
            after = ""
        new = place_after(seg, after, n)
        if new is None:
            log(f"  ✗ 註{n}（{eng}）位置不唯一／緊貼他註／沒給")
            continue
        log(f"  ✓ 註{n} [模型 {eng}] …{after[-12:]}【[^{n}]】")
        body = body[:lo] + new + body[hi:]
        by_llm += 1
    return body + rule + notes, by_rule, by_llm


def gap_count(chunks: list[dict]) -> tuple[int, int]:
    """(註文總數, 有註文卻沒連結數)"""
    tot = miss = 0
    for c in chunks:
        parts = split_body(c.get("content") or "")
        if not parts:
            continue
        refs = set(re.findall(r"\[\^(\d+)\]", parts[0]))
        ns = {str(k) for k in note_texts(parts[2])}
        tot += len(ns)
        miss += len(ns - refs)
    return tot, miss


def scan() -> int:
    out = ROOT / "output/toc_audit/footnote_gaps.tsv"
    rows = []
    for p in sorted(CH.glob("*.jsonl")):
        try:
            with p.open(encoding="utf-8") as f:
                chunks = [json.loads(l) for l in f if l.strip()]
        except Exception:  # noqa: BLE001
            continue
        tot, miss = gap_count(chunks)
        if tot:
            rows.append((p.stem, tot, miss))
    rows.sort(key=lambda r: -r[2])
    with out.open("w", encoding="utf-8") as f:
        f.write("id\t註文數\t缺連結\n")
        for r in rows:
            f.write(f"{r[0]}\t{r[1]}\t{r[2]}\n")
    print(f"有註文的書 {len(rows)} 本；缺連結合計 {sum(r[2] for r in rows)} 則 → {out}")
    return 0


def main() -> int:
    if "--scan" in sys.argv:
        return scan()
    ids = [a for a in sys.argv[sys.argv.index("--ids") + 1:] if not a.startswith("--")] if "--ids" in sys.argv else []
    use_llm, apply = "--llm" in sys.argv, "--apply" in sys.argv
    for bid in ids:
        p = CH / f"{bid}.jsonl"
        chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        before = gap_count(chunks)
        r = l = 0
        for k, c in enumerate(chunks):
            c["content"], a, b = relink_chunk(c.get("content") or "", use_llm=use_llm,
                                              log=lambda s, k=k: print(f"塊{k}{s}", flush=True))
            r += a
            l += b
        after = gap_count(chunks)
        print(f"{bid}：註文 {before[0]}，缺連結 {before[1]} → {after[1]}（規則 {r}、模型 {l}）")
        if apply and (r or l):
            shutil.copy2(p, p.with_suffix(".jsonl.bak_relink"))
            import standardize_ebook as se
            o = se.write_jsonl(bid, chunks)
            se.push_to_r2(bid, o)
            se.update_db(bid, chunks)
            print("  已寫回 Drive、推 R2、更新 DB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
