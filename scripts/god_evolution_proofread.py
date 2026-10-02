#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《神的演化》朗讀檔的文字校對層：逐段送 Gemini→NVIDIA 校對，過閘才收，結果存校正檔。

只改 OCR 造成的錯（漏字、錯字、缺標點、簡體字、斷句錯位），不動梁永安的譯文用字與譯名。
校正檔 output/god-evolution/proofread.json：{sha1(原段): 校對後的段}；產生器
god_evolution_read_aloud.py 讀進來逐段套用。重跑會跳過已校對的段（可續跑）。

  python -X utf8 scripts/god_evolution_proofread.py --chapters 00,01 [--limit N]
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import god_evolution_read_aloud as g  # noqa: E402

CACHE = Path(__file__).resolve().parent.parent / "output" / "god-evolution" / "proofread.json"
NVIDIA_ONLY = True
BATCH_CHARS = 1400
SEP = "\n@@@\n"

PROMPT = """你是繁體中文書稿的 OCR 校對員。下面是《神的演化》（羅伯‧賴特著、梁永安譯）掃描 OCR 的幾個段落，
段落之間用單獨一行的 @@@ 隔開。請只修 OCR 造成的錯誤：
1. 漏掉或誤植的標點（逗號、句號、頓號、冒號、引號、書名號〈〉《》）要補正；全形標點，英文括號內維持原樣。
2. 明顯的錯字、形近字、漏字、多出的字、簡體字轉繁體。
3. 夾在句中的孤立數字（註釋號碼殘留）與頁眉殘片刪掉。
嚴禁：改寫、潤飾、換詞、調整句子、改動譯名與人名地名、增刪內容、翻譯英文。不確定就不要改。
輸出：段落數必須與輸入完全相同，同樣用 @@@ 單獨一行隔開，只輸出校對後的段落，不要任何說明、標題或前言。

{text}"""

_NOP = re.compile(r"[\s，。、；：？！「」『』《》〈〉（）()—…·・,.]")
_BAD = re.compile(r"以下是|校對後|校對結果|<think>|</think>|好的[，,]|修正後|說明[：:]|注意[：:]")


def sha(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def cjk_ratio(s: str) -> float:
    return sum(1 for c in s if "一" <= c <= "鿿") / max(len(s), 1)


def gate(orig: list[str], new: list[str]) -> list[str | None]:
    """逐段過閘：回傳每段的採用文字，None＝不採用（沿用原文）。"""
    out: list[str | None] = []
    for o, n in zip(orig, new):
        n = n.strip()
        if not n or re.search(r"\^|@@|【|\[\^", n) or _BAD.search(n) and not _BAD.search(o):
            out.append(None); continue
        if cjk_ratio(n) < cjk_ratio(o) * 0.9 - 0.02 or abs(len(n) - len(o)) > max(3, 0.05 * len(o)):
            out.append(None); continue
        # 標點以外的字至少 95% 相同；成對符號（「」『』《》〈〉（））只准增不准減
        a, b = _NOP.sub("", o), _NOP.sub("", n)
        if difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() < 0.95                 or any(n.count(ch) < o.count(ch) for ch in "「」『』《》〈〉（）()"):
            out.append(None); continue
        out.append(n)
    return out


def ask(prompt: str) -> tuple[str, str]:
    import chapters_via_llm_toc as c  # Gemini 輪 key → 全 429 冷卻 → NVIDIA
    if NVIDIA_ONLY:   # Gemini 額度要留給掃描頁 OCR，校對直接走 NVIDIA
        c._gem_dead_until = time.time() + 86400
    return c.ask_model(prompt)


def split_json_wrapper(raw: str) -> str:
    return re.sub(r"^```\w*\n|\n```$", "", raw.strip())


def batches(paras: list[str]):
    cur: list[str] = []
    n = 0
    for p in paras:
        if cur and n + len(p) > BATCH_CHARS:
            yield cur; cur = []; n = 0
        cur.append(p); n += len(p)
    if cur:
        yield cur


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    want = set(a.chapters.split(",")) if a.chapters else None
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    chs = g.build(g.load_pages(), proof={})
    calls = ok = rej = 0
    for ch in chs:
        if want and ch["no"] not in want:
            continue
        todo = [p for p in ch["paras"] if not g.is_heading(p) and sha(p) not in cache and not p.isascii()]
        for b in batches(todo):
            if a.limit and calls >= a.limit:
                break
            raw, eng = ask(PROMPT.replace("{text}", SEP.join(b).replace("\n@@@\n", SEP)))
            calls += 1
            raw = split_json_wrapper(raw)
            new = [x.strip() for x in re.split(r"\n\s*@@@\s*\n", raw)]
            if len(new) != len(b):
                rej += len(b); print(f"  {ch['no']} 段數不符 {len(new)}/{len(b)} ({eng})"); 
                if len(b) > 1:   # 退一步：單段重送
                    for p in b:
                        r2, _ = ask(PROMPT.replace("{text}", p)); calls += 1
                        r = gate([p], [split_json_wrapper(r2)])[0]
                        if r is not None:
                            cache[sha(p)] = r; ok += 1
                continue
            for p, r in zip(b, gate(b, new)):
                if r is None:
                    rej += 1
                else:
                    cache[sha(p)] = r; ok += 1
            CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        print(f"{ch['no']} 累計 呼叫 {calls}、採用 {ok}、不採用 {rej}", flush=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
