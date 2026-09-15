#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Gemini 潤飾 /works 論文草稿的正文，只動文句、不動事實。

只處理章節正文段落；標題、表格、引文塊、清單、書目、註釋、附錄一律不送。
每塊都過驗收閘，任何一項不過就保留原文（寧可不順，不可失真）。

閘：① 〔註N〕 序列完全相同 ② 不得出現簡體字 ③ 不得出現 LLM 後設回話
    ④ 不得殘留 <think> ⑤ 長度比 0.80–1.35 ⑥ 數字集合不得減少 ⑦ 段落數相同

🚨 genai.Client 必須留強參考重複使用；每次呼叫現建的臨時 client 會被回收，
   回報 "Cannot send a request, as the client has been closed."

跑法：
  python scripts/polish_paper_gemini.py <ref> [--dry] [--chunk 2200]
"""
from __future__ import annotations

import argparse
import itertools
import os
import re
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests

from ocr_with_gemini import _find_gemini_keys  # type: ignore
import translate_ebook_to_zh as engines  # type: ignore

from google import genai

MODEL = os.environ.get("POLISH_GEMINI_MODEL", "gemini-flash-latest")

PROMPT = """你是學術中文的編輯。請潤飾以下論文段落，使行文更通順自然。

嚴格規則：
1. 只改文句，不改意思。禁止增加、刪除或更動任何事實、人名、地名、機構、年份、數字、頁碼、書名、引號內的引文。
2. 〔註1〕〔註2〕這類註標必須原樣保留，位置與順序完全不變，不可增刪。
3. 一律繁體中文（台灣用語）。不得出現簡體字。
4. 段落數與段落順序必須完全一致，段落之間以一個空行分隔。
5. 保留原有的 **粗體**、*斜體*、引號、括號等標記。
6. 直接輸出潤飾後的段落，不要任何說明、前言、標題或編號。

待潤飾的段落：
---
{body}
---"""

SIMPLIFIED = set("为个国这来后会学发实现对说时开门题产业经过样点东车马长书电话语义题运动")
META = ("我注意到", "作為一個", "抱歉", "以下是", "潤飾後", "好的", "As an AI", "I cannot")


def gates(src: str, out: str) -> str:
    """回傳失敗原因；通過回空字串。"""
    if not out or not out.strip():
        return "空回應"
    if "<think" in out or "</think" in out:
        return "推理外洩"
    for m in META:
        if out.lstrip().startswith(m):
            return "後設回話：%s" % m
    a = re.findall(r"〔註(\d+)〕", src)
    b = re.findall(r"〔註(\d+)〕", out)
    if a != b:
        return "註標不符 %s → %s" % (a, b)
    bad = SIMPLIFIED & set(out)
    if bad:
        return "簡體字 %s" % "".join(sorted(bad))
    ratio = len(out) / max(len(src), 1)
    if not 0.80 <= ratio <= 1.35:
        return "長度比 %.2f" % ratio
    lost = set(re.findall(r"\d+", src)) - set(re.findall(r"\d+", out))
    if lost:
        return "數字遺失 %s" % sorted(lost)
    if out.count("\n\n") != src.count("\n\n"):
        return "段落數不符"
    return ""


def nvidia(prompt: str) -> tuple[str, str]:
    """引擎鏈第二層。回傳 (文本, 失敗原因)。"""
    keys = list(engines.NVIDIA_KEYS)
    if not keys:
        return "", "無 NVIDIA key"
    last = "?"
    for i, key in enumerate(keys):
        try:
            r = requests.post(
                engines.NVIDIA_URL,
                headers={"Authorization": "Bearer %s" % key,
                         "Content-Type": "application/json"},
                json={"model": engines.NVIDIA_MODELS[0],
                      "messages": [{"role": "user", "content": prompt}],
                      "max_tokens": 8000, "temperature": 0.3},
                timeout=300)
        except requests.exceptions.RequestException as exc:
            last = type(exc).__name__
            continue
        if r.status_code == 200:
            txt = r.json()["choices"][0]["message"]["content"]
            return engines._THINK_RE.sub("", txt).strip(), ""
        last = "HTTP %d" % r.status_code
        time.sleep(2)
    return "", "NVIDIA：%s" % last


def polishable(line: str) -> bool:
    t = line.strip()
    if not t:
        return False
    return not t.startswith(("#", "|", ">", "-", "*")) and not re.match(r"^\d+\.\s", t)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("--chunk", type=int, default=2200)
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    path = Path("public/content/works/%s-revision-draft.md" % args.ref)
    lines = path.read_text(encoding="utf-8").split("\n")

    lo = next(i for i, l in enumerate(lines) if l.startswith("## 一、"))
    hi = next(i for i, l in enumerate(lines) if l.startswith("## 徵引書目"))
    idxs = [i for i in range(lo, hi) if polishable(lines[i])]
    print("可潤飾段落：%d 段 / %d 字" % (len(idxs), sum(len(lines[i]) for i in idxs)))

    chunks: list[list[int]] = []
    cur: list[int] = []
    size = 0
    for i in idxs:
        if cur and size + len(lines[i]) > args.chunk:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(i)
        size += len(lines[i])
    if cur:
        chunks.append(cur)
    print("切成 %d 塊（模型 %s）" % (len(chunks), MODEL))
    if args.dry:
        return 0

    keys = _find_gemini_keys()
    if not keys:
        print("ERR: 無 GEMINI_API_KEY", file=sys.stderr)
        return 1
    clients = [genai.Client(api_key=k) for k in keys]
    rot = itertools.cycle(clients)
    print("金鑰數：%d" % len(keys))

    ok = skipped = 0
    for n, grp in enumerate(chunks, 1):
        src = "\n\n".join(lines[i] for i in grp)
        out = None
        engine = "Gemini"
        why = "未嘗試"
        for _ in range(len(clients)):
            client = next(rot)
            try:
                resp = client.models.generate_content(
                    model=MODEL, contents=PROMPT.format(body=src))
                cand = (resp.text or "").strip()
            except Exception as exc:
                why = "API：%s" % str(exc)[:90]
                time.sleep(2)
                continue
            why = gates(src, cand)
            if not why:
                out = cand
                break
        if out is not None:
            for i, para in zip(grp, out.split("\n\n")):
                lines[i] = para.strip()
            ok += 1
            print("  塊 %2d/%d  已潤飾 %d 段（%s）" % (n, len(chunks), len(grp), engine))
            continue

        # Gemini 用罄或過載 → 引擎鏈第二層。
        # 🚨 nemotron 整塊送會重複輸出（註標暴增），必須逐段送才過閘。
        done = 0
        for i in grp:
            one = lines[i]
            cand, err = nvidia(PROMPT.format(body=one))
            bad = err or gates(one, cand)
            if bad:
                continue
            lines[i] = cand.strip()
            done += 1
        if done:
            ok += 1
            print("  塊 %2d/%d  逐段潤飾 %d/%d 段（NVIDIA；Gemini：%s）"
                  % (n, len(chunks), done, len(grp), why))
        else:
            skipped += 1
            print("  塊 %2d/%d  保留原文（%s）" % (n, len(chunks), why))

    path.write_text("\n".join(lines), encoding="utf-8")
    print("完成：潤飾 %d 塊、保留原文 %d 塊" % (ok, skipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
