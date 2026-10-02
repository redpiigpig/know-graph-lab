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
import os
import sys
import threading
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


_rr = 0
_rr_lock = threading.Lock()


def ask(prompt: str, tries: int = 4, timeout: int = 90) -> tuple[str, str]:
    """直打 NVIDIA（Gemini 額度留給掃描頁 OCR）。🚨 10-02 第三版卡在第 05 章一小時多：
    原用 te.nvidia_chat 單次 timeout=300、整體 deadline=600、連線例外只休 30 秒，
    某次請求被伺服器吊住就整條線空等。改成：單次 90 秒逾時、輪 key 最多 4 次，
    全失敗回 ("", "engine-failed")，由呼叫端沿用原文並記下來。"""
    global _rr
    import requests
    import translate_ebook_to_zh as te
    last = "?"
    for _ in range(tries):
        with _rr_lock:
            idx = _rr % len(te.NVIDIA_KEYS); _rr += 1
        try:
            r = requests.post(
                te.NVIDIA_URL,
                headers={"Authorization": f"Bearer {te.NVIDIA_KEYS[idx]}", "Content-Type": "application/json"},
                json={"model": te.NVIDIA_MODELS[0], "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.1, "max_tokens": 6000,
                      "chat_template_kwargs": {"enable_thinking": False}},
                timeout=timeout)
        except requests.exceptions.RequestException as e:
            last = f"conn {type(e).__name__}"; time.sleep(2); continue
        if r.status_code == 200:
            try:
                return te._THINK_RE.sub("", r.json()["choices"][0]["message"]["content"]).strip(), "nvidia"
            except (KeyError, IndexError, ValueError):
                last = "bad-json"; continue
        last = f"http {r.status_code}"
        time.sleep(15 if r.status_code == 429 else 3)
    return "", f"engine-failed {last}"


def split_json_wrapper(raw: str) -> str:
    raw = re.sub(r"^```\w*\n|\n```$", "", raw.strip())
    return re.sub(r"^(@@@\s*)+|(\s*@@@)+$", "", raw.strip()).strip()   # 模型常在首尾多吐 @@@


def batches(paras: list[str]):
    cur: list[str] = []
    n = 0
    for p in paras:
        if cur and n + len(p) > BATCH_CHARS:
            yield cur; cur = []; n = 0
        cur.append(p); n += len(p)
    if cur:
        yield cur


def save(cache: dict) -> None:
    tmp = CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, CACHE)


def main() -> int:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapters", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    want = set(a.chapters.split(",")) if a.chapters else None
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    chs = g.build(g.load_pages(), proof={})
    lock = threading.Lock()
    st = {"calls": 0, "ok": 0, "rej": 0, "fail": 0}

    def work(no: str, b: list[str]) -> None:
        raw, eng = ask(PROMPT.replace("{text}", SEP.join(b)))
        res: dict[str, str] = {}
        calls, rej, fail = 1, 0, 0
        new = [x.strip() for x in re.split(r"\n\s*@@@\s*\n", split_json_wrapper(raw))] if raw else []
        if len(new) == len(b):
            for p, r in zip(b, gate(b, new)):
                if r is None:
                    rej += 1
                else:
                    res[sha(p)] = r
        else:
            print(f"  {no} 段數不符或失敗 {len(new)}/{len(b)} ({eng})", flush=True)
            if len(b) > 1:   # 退一步：單段重送
                for p in b:
                    r2, e2 = ask(PROMPT.replace("{text}", p)); calls += 1
                    r = gate([p], [split_json_wrapper(r2)])[0] if r2 else None
                    if r is None:
                        rej += 1; fail += (not r2)
                    else:
                        res[sha(p)] = r
            else:
                rej += 1; fail += 1
        with lock:
            cache.update(res)
            st["calls"] += calls; st["ok"] += len(res); st["rej"] += rej; st["fail"] += fail
            save(cache)

    jobs = []
    for ch in chs:
        if want and ch["no"] not in want:
            continue
        todo = [p for p in ch["paras"] if not g.is_heading(p) and sha(p) not in cache and not p.isascii()]
        jobs += [(ch["no"], b) for b in batches(todo)]
    if a.limit:
        jobs = jobs[:a.limit]
    print(f"待校對 {len(jobs)} 批", flush=True)
    done = 0
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(work, no, b) for no, b in jobs]
        for f in as_completed(futs):
            f.result(); done += 1
            if done % 10 == 0 or done == len(jobs):
                print(f"{done}/{len(jobs)} 呼叫 {st['calls']}、採用 {st['ok']}、不採用 {st['rej']}（其中引擎失敗 {st['fail']}）", flush=True)
    save(cache)
    print(f"完成：呼叫 {st['calls']}、採用 {st['ok']}、不採用 {st['rej']}（引擎失敗 {st['fail']}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
