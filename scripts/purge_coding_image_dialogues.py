#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
purge_coding_image_dialogues.py
================================
找出 AI 對話錄裡「寫程式」與「生成圖片」的對話，用 LLM 逐則確認後刪除。
（使用者 2026-06-17：GPT 裡寫程式跟生成圖片的對話都不需要。）

安全設計：
  * 候選池 = 程式/繪圖關鍵詞聯集（不是全表硬掃）。
  * LLM 把每則標成 coding / image / keep；只刪「coding 或 image」。
  * 預設 --dry-run：只判讀、寫 ledger、印報告與樣本，不刪任何東西。
  * 真刪要加 --execute；刪 dialogue 前先刪其 entry_categories（避免孤兒）。
  * ledger 在 c:/tmp，可續跑。

引擎：Gemini→NVIDIA→Haiku（重用 classify_genesis_philosophy 的基礎設施）。

用法：
    python purge_coding_image_dialogues.py --source chatgpt --dry-run
    python purge_coding_image_dialogues.py --source chatgpt --execute
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import requests

import classify_genesis_philosophy as C  # reuse sb_get/engines/_parse_json

CODE_KW = ["```", "console.log", "def ", "function ", "import ", "程式碼",
           "python", "javascript", "npm ", "報錯", "stack trace", "編譯"]
IMAGE_KW = ["畫一", "畫個", "幫我畫", "生成圖", "生成一張", "做一張圖", "DALL",
            "插圖", "示意圖", "logo", "海報"]

LEDGER_DIR = Path("c:/tmp")

SYSTEM = (
    "你是一位對話分類助理。使用者想刪掉兩類對話：(1) coding=寫程式/除錯/技術實作"
    "（請求或回應主要在寫程式碼、debug、設定環境、API 串接等）；(2) image=請 AI"
    "生成圖片/插圖/海報/logo（DALL·E 類繪圖請求）。其餘一律 keep——尤其是哲學、"
    "宗教學、學術、寫作、翻譯、一般問答，即使夾帶程式或圖片詞彙也要 keep。\n"
    "判斷依對話的『主要目的』，不要因為偶爾提到一個技術詞就誤判。"
)

PROMPT_TMPL = (
    "逐則判斷下列對話屬於 coding / image / keep。嚴格只輸出 JSON 陣列：\n"
    '  {{"i": <編號>, "label": "coding"|"image"|"keep"}}\n'
    "不要任何說明文字。\n\n對話：\n{items}"
)


def llm_label(batch: list[dict]) -> list[dict]:
    items = []
    for i, d in enumerate(batch):
        p = (d.get("prompt") or "").strip().replace("\n", " ")[:500]
        rsp = (d.get("response") or "").strip().replace("\n", " ")[:600]
        items.append(f"[{i}] 提問：{p}\n    回應：{rsp}")
    prompt = PROMPT_TMPL.format(items="\n\n".join(items))
    for name, fn in (("Gemini", C.gemini_chat), ("NVIDIA", C.nvidia_chat), ("Haiku", C.haiku_chat)):
        try:
            return C._parse_json(fn(SYSTEM, prompt))
        except Exception as e:
            print(f"  · {name} 失敗：{type(e).__name__} {str(e)[:100]}", flush=True)
    raise RuntimeError("三引擎全失敗")


def candidate_ids(table: str) -> set[str]:
    ids: set[str] = set()
    for kw in CODE_KW + IMAGE_KW:
        flt = f"prompt.ilike.*{kw}*,response.ilike.*{kw}*"
        offset, page = 0, 1000
        while True:
            r = C.sb_get(table, {"select": "id", "or": f"({flt})"}, rng=(offset, offset + page - 1))
            if r.status_code not in (200, 206):
                break
            rows = r.json()
            for row in rows:
                ids.add(row["id"])
            if len(rows) < page:
                break
            offset += page
    return ids


def delete_dialogues(table: str, source: str, ids: list[str]) -> None:
    h = dict(C.SB_HDR)
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        inlist = "(" + ",".join(chunk) + ")"
        # remove category links first (no FK cascade assumed)
        requests.delete(f"{C.SUPABASE_URL}/rest/v1/ai_dialogue_entry_categories",
                        headers=h, params={"dialogue_id": f"in.{inlist}"}, timeout=120)
        r = requests.delete(f"{C.SUPABASE_URL}/rest/v1/{table}",
                            headers=h, params={"id": f"in.{inlist}"}, timeout=120)
        if r.status_code not in (200, 204):
            print(f"  ⚠ delete HTTP {r.status_code}: {r.text[:160]}", flush=True)


def run(source: str, batch_size: int, execute: bool, limit: int | None) -> None:
    table = f"ai_dialogues_{source}"
    print(f"\n=== {source} (execute={execute}) ===", flush=True)
    cand = sorted(candidate_ids(table))
    print(f"候選池：{len(cand)} 筆", flush=True)

    ledger = LEDGER_DIR / f"purge_{source}.jsonl"
    done: dict[str, str] = {}
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            try:
                o = json.loads(line)
                done[o["id"]] = o["label"]
            except Exception:
                pass

    todo = [i for i in cand if i not in done]
    if limit:
        todo = todo[:limit]
    print(f"ledger 已判 {len(done)}・待判 {len(todo)}", flush=True)

    lf = ledger.open("a", encoding="utf-8")
    samples = {"coding": [], "image": []}
    try:
        for i in range(0, len(todo), batch_size):
            ids = todo[i:i + batch_size]
            rows = C.fetch_dialogues(table, ids)
            if not rows:
                continue
            try:
                verdicts = llm_label(rows)
            except Exception as e:
                print(f"  batch 跳過：{e}", flush=True)
                continue
            vmap = {v.get("i"): v for v in verdicts if isinstance(v, dict)}
            for idx, d in enumerate(rows):
                label = (vmap.get(idx, {}) or {}).get("label", "keep")
                if label not in ("coding", "image", "keep"):
                    label = "keep"
                lf.write(json.dumps({"id": d["id"], "label": label}, ensure_ascii=False) + "\n")
                done[d["id"]] = label
                if label in samples and len(samples[label]) < 6:
                    samples[label].append((d.get("prompt") or "")[:70].replace("\n", " "))
            lf.flush()
            print(f"  進度 {min(i + batch_size, len(todo))}/{len(todo)}", flush=True)
    finally:
        lf.close()

    to_del = [i for i, l in done.items() if l in ("coding", "image") and i in set(cand)]
    n_code = sum(1 for l in done.values() if l == "coding")
    n_img = sum(1 for l in done.values() if l == "image")
    n_keep = sum(1 for l in done.values() if l == "keep")
    print(f"\n判定結果：coding {n_code}・image {n_img}・keep {n_keep}", flush=True)
    for lab in ("coding", "image"):
        if samples[lab]:
            print(f"  {lab} 樣本：", flush=True)
            for s in samples[lab]:
                print(f"    - {s}", flush=True)
    print(f"\n預計刪除 {len(to_del)} 筆。", flush=True)

    if execute:
        delete_dialogues(table, source, to_del)
        print(f"✅ 已刪除 {len(to_del)} 筆 {source} 對話。", flush=True)
    else:
        print("（dry-run：未刪除任何東西。確認後加 --execute 真刪。）", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["chatgpt", "gemini", "all"], default="chatgpt")
    ap.add_argument("--batch", type=int, default=12)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--execute", action="store_true", help="真的刪除（否則 dry-run）")
    args = ap.parse_args()
    sources = ["chatgpt", "gemini"] if args.source == "all" else [args.source]
    for s in sources:
        run(s, args.batch, args.execute, args.limit)


if __name__ == "__main__":
    main()
