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
CIRCLED = re.compile("[①-⑳]")

PROMPT = """下面是一本中文學術書某段正文，以及一則註釋的內容。這則註釋（第 {n} 號）的註號在 OCR 時遺失了。
先判斷：這則註釋講的人、書、事，在這段正文裡有沒有對應的內容？OCR 有時把別頁的註釋錯配過來，沒有明確對應就算無關。
有關才判斷註號原本緊接在正文哪幾個字之後。
回傳 JSON：{{"related": true 或 false, "after": "註號前緊鄰的 8 到 15 個字，必須一字不差照抄正文；無關或判斷不出來就給空字串"}}。只輸出 JSON。

【註 {n} 的內容】
{note}

【正文片段（註號應落在這段裡）】
{seg}"""


def split_body(content: str) -> tuple[str, str, str] | None:
    m = RULE.search(content)
    if not m:
        return None
    return content[:m.start()], m.group(0), content[m.end():]


def note_texts(notes: str) -> dict[int, str]:
    return {int(m.group(1)): m.group(2) for m in re.finditer(r"(?m)^\((\d+)\) (.*)$", notes)}


def segment(body: str, n: int, wide: bool = False) -> tuple[int, int] | None:
    """[^n-1] 之後到 [^n+1] 之前；兩邊都沒錨就不猜。
    wide（只給模型那步）：改用「比 n 小的最近已連註號」到「比 n 大的最近已連註號」，沒有就到塊頭／塊尾。
    連續缺號的書（加爾文缺 1,706 則）照窄規則一則都進不了模型（2026-10-02）。"""
    if wide:
        refs = {int(m.group(1)): m for m in re.finditer(r"\[\^(\d+)\]", body)}
        lo_n = max((k for k in refs if k < n), default=None)
        hi_n = min((k for k in refs if k > n), default=None)
        lo = refs[lo_n].end() if lo_n is not None else 0
        hi = refs[hi_n].start() if hi_n is not None else len(body)
        return (lo, hi) if hi > lo else None
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
    prev, nxt = seg[pos - 1], seg[pos:pos + 1]
    if prev == "-" or (prev.isascii() and prev.isalpha() and nxt.isascii() and nxt.isalpha()):
        return None                                   # 英文斷字／單字中間（Body and Society「cor-[^27]」）
    line_start = seg.rfind("\n", 0, pos) + 1
    if seg[line_start:line_start + 1] == "#" and seg[pos:pos + 1] in ("\n", ""):
        return None                                   # 標題行尾
    rest = seg[pos:]
    m = re.match(r"(\d+)(?![\d年月日])", rest)
    if m and str(n).startswith(m.group(1)):
        rest = rest[len(m.group(1)):]                  # 清 OCR 殘留的同號數字
    return seg[:pos] + tag + rest


class EngineExhausted(Exception):
    """模型連續失敗（額度／速率）：呼叫端把已補的寫回後停手，隔天再續。"""


ENGINE = {"calls": 0, "fails_in_row": 0, "max_calls": 10**9}


def relink_chunk(content: str, *, use_llm: bool, log) -> tuple[str, int, int]:
    parts = split_body(content)
    if not parts:
        return content, 0, 0
    body, rule, notes = parts
    by_rule = by_llm = 0
    texts = note_texts(notes)
    missing = sum(1 for n in texts if f"[^{n}]" not in body)
    piled = missing > 30 and len(body) < 200 * missing   # 全書註文堆在一塊（加爾文書尾 1,706 則）：不是本塊的註
    try:
        for n in sorted(texts):
            if f"[^{n}]" in body:
                continue
            rng = segment(body, n)
            if rng:
                lo, hi = rng
                seg = body[lo:hi]
                cands = rule_candidates(seg, n)
                if len(cands) == 1:
                    st, en, how = cands[0]
                    log(f"  ✓ 註{n} [{how}] …{seg[max(0, st - 12):st]}【{seg[st:en]}】{seg[en:en + 8]}…")
                    body = body[:lo] + seg[:st] + f"[^{n}]" + seg[en:] + body[hi:]
                    by_rule += 1
                    continue
            if not use_llm or piled:
                continue
            rng = segment(body, n, wide=True)
            if not rng or rng[1] - rng[0] > MAX_SEG:
                continue
            lo, hi = rng
            seg = body[lo:hi]
            if CIRCLED.search(seg):
                continue                               # 正文用 ①② 逐頁編號：分隔線下的 (N) 多半是別頁錯配來的（2026-10-02 赫爾墨斯的計謀）
            if ENGINE["calls"] >= ENGINE["max_calls"]:
                raise EngineExhausted(f"本輪呼叫上限 {ENGINE['max_calls']}")
            import chapters_via_llm_toc as cv
            ENGINE["calls"] += 1
            raw, eng = cv.ask_model(PROMPT.format(n=n, note=texts[n][:600], prev=n - 1, next=n + 1, seg=seg))
            if eng.startswith("engine-failed"):
                ENGINE["fails_in_row"] += 1
                log(f"  ✗ 註{n}（{eng}）")
                if ENGINE["fails_in_row"] >= 2:
                    raise EngineExhausted(eng)
                continue
            ENGINE["fails_in_row"] = 0
            m = re.search(r"\{.*\}", raw or "", re.S)
            try:
                ans = json.loads(m.group(0)) if m else {}
                after = ans.get("after", "") if ans.get("related") is True else ""
            except (json.JSONDecodeError, AttributeError):
                after = ""
            new = place_after(seg, after, n)
            if new is None:
                log(f"  ✗ 註{n}（{eng}）判無關／位置不唯一／緊貼他註／沒給")
                continue
            log(f"  ✓ 註{n} [模型 {eng}] …{after[-24:]}【[^{n}]】｜註文：{texts[n][:40]}")
            body = body[:lo] + new + body[hi:]
            by_llm += 1
    except EngineExhausted as e:
        e.partial = (body + rule + notes, by_rule, by_llm)
        raise
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


SUPRE = re.compile("[⁰¹²³⁴⁵⁶⁷⁸⁹]+")


def book_type(chunks: list[dict]) -> str:
    """純函式：缺連結的書分型（2026-10-02 盤點 output/relink/booktypes.py 移進來）。
    A 正文有 [^N] 但部分丟失（模型可補）／B 上標字元／C 正文是 (N)／D 正文是 [N]／
    E 註文平均 <40 字（問題清單之類，不是註腳，不必補）／F 正文完全沒註號（PDF 要回版面找上標）。"""
    notes_n = notelen = refs = sup = parmatch = brmatch = 0
    for ch in chunks:
        p = split_body(ch.get("content") or "")
        if not p:
            continue
        body, _, notes = p
        ns = note_texts(notes)
        if not ns:
            continue
        keys = {str(n) for n in ns}
        notes_n += len(ns)
        notelen += sum(len(v) for v in ns.values())
        refs += len(re.findall(r"\[\^\d+\]", body))
        sup += len(SUPRE.findall(body))
        parmatch += len(set(re.findall(r"[（(](\d{1,3})[）)]", body)) & keys)
        brmatch += len(set(re.findall(r"(?<!\^)\[(\d{1,3})\]", body)) & keys)
    if not notes_n:
        return ""
    if refs > 0.1 * notes_n:
        return "A"
    if sup >= 0.3 * notes_n:
        return "B"
    if parmatch >= 0.3 * notes_n:
        return "C"
    if brmatch >= 0.3 * notes_n:
        return "D"
    if notelen / notes_n < 40:
        return "E"
    return "F"


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
            rows.append((p.stem, tot, miss, book_type(chunks) if miss else ""))
    rows.sort(key=lambda r: -r[2])
    with out.open("w", encoding="utf-8") as f:
        f.write("id\t註文數\t缺連結\t型\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    real = [r for r in rows if r[3] != "E"]
    print(f"有註文的書 {len(rows)} 本；缺連結合計 {sum(r[2] for r in real)} 則"
          f"（另 E 型非註腳 {sum(r[2] for r in rows if r[3] == 'E')} 則不計）→ {out}")
    return 0


def relink_book(bid: str, *, use_llm: bool, apply: bool) -> tuple[int, int, bool]:
    """回傳 (規則補, 模型補, 引擎是否耗盡)。耗盡時已補的照樣寫回。"""
    p = CH / f"{bid}.jsonl"
    chunks = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
    before = gap_count(chunks)
    r = l = 0
    exhausted = False
    for k, c in enumerate(chunks):
        try:
            c["content"], a, b = relink_chunk(c.get("content") or "", use_llm=use_llm,
                                              log=lambda s, k=k: print(f"塊{k}{s}", flush=True))
        except EngineExhausted as e:
            c["content"], a, b = e.partial
            exhausted = True
            print(f"  ⏸ 引擎停（{e}）", flush=True)
        r += a
        l += b
        if exhausted:
            break
    after = gap_count(chunks)
    print(f"{bid}：註文 {before[0]}，缺連結 {before[1]} → {after[1]}（規則 {r}、模型 {l}）", flush=True)
    if apply and (r or l):
        shutil.copy2(p, p.with_suffix(".jsonl.bak_relink"))
        import standardize_ebook as se
        o = se.write_jsonl(bid, chunks)
        se.push_to_r2(bid, o)
        se.update_db(bid, chunks)
        print("  已寫回 Drive、推 R2、更新 DB", flush=True)
    return r, l, exhausted


def main() -> int:
    if "--scan" in sys.argv:
        return scan()
    ids = [a for a in sys.argv[sys.argv.index("--ids") + 1:] if re.fullmatch(r"[0-9a-f-]{36}", a)] if "--ids" in sys.argv else []
    use_llm, apply = "--llm" in sys.argv, "--apply" in sys.argv
    if "--max-calls" in sys.argv:
        ENGINE["max_calls"] = int(sys.argv[sys.argv.index("--max-calls") + 1])
    for bid in ids:
        if relink_book(bid, use_llm=use_llm, apply=apply)[2]:
            return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
