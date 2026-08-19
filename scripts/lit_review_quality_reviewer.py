#!/usr/bin/env python3
"""Gemini #4 full-coverage quality reviewer for literature-review translations.

Every orig/zh paragraph pair is checked. A content hash ledger makes the pass
resumable; if either side changes, the pair is reviewed again automatically.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
STATE_DIR = ROOT / "scripts" / "state"
LEDGER = STATE_DIR / "lit_review_quality_ledger.jsonl"
load_dotenv(ROOT / ".env")
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}",
           "Content-Type": "application/json"}

PROMPT = """你是學術翻譯的最終品質審查者。逐句比對原文與繁體中文譯文。

檢查：漏譯、增譯、反義、專名／數字／引文錯誤、簡體字、明顯不通順。
不要為了風格任意改寫；原譯忠實可讀就判定 ok。
只輸出 JSON：
{{"status":"ok","text":""}}
或
{{"status":"revised","text":"完整修正版繁體中文"}}

原文：
{original}

現有中譯：
{translation}"""


def get(table: str, query: str) -> list[dict]:
    response = requests.get(f"{URL}/rest/v1/{table}?{query}",
                            headers=HEADERS, timeout=90)
    response.raise_for_status()
    return response.json()


def patch_section(section_id: int, text: str) -> None:
    response = requests.patch(
        f"{URL}/rest/v1/lit_review_sections?id=eq.{section_id}",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"text": text, "char_count": len(text)}, timeout=60)
    response.raise_for_status()


def digest_pair(original: str, translation: str) -> str:
    return hashlib.sha256(
        (original + "\0" + translation).encode("utf-8")).hexdigest()


def load_ledger() -> dict[str, str]:
    done: dict[str, str] = {}
    if not LEDGER.exists():
        return done
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            done[str(row["key"])] = str(row["digest"])
        except (json.JSONDecodeError, KeyError):
            continue
    return done


def parse_review(raw: str) -> dict:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    else:
        obj = re.search(r"\{.*\}", text, re.S)
        if obj:
            text = obj.group(0)
    result = json.loads(text)
    if result.get("status") not in ("ok", "revised"):
        raise ValueError("review status must be ok/revised")
    if result["status"] == "revised" and not str(result.get("text") or "").strip():
        raise ValueError("revised review missing text")
    return result


def load_pairs(project: str) -> list[dict]:
    entries = get(
        "lit_review_entries",
        f"project_slug=eq.{project}&select=id,ref_key&order=id&limit=10000")
    ref_keys = {int(row["id"]): row["ref_key"] for row in entries}
    pairs: list[dict] = []
    ids = list(ref_keys)
    for start in range(0, len(ids), 50):
        batch = ",".join(str(value) for value in ids[start:start + 50])
        sections = get(
            "lit_review_sections",
            f"entry_id=in.({batch})&version_code=in.(orig,zh)"
            "&select=id,entry_id,version_code,order_index,text"
            "&order=entry_id,order_index&limit=20000")
        grouped: dict[tuple[int, int], dict] = {}
        for row in sections:
            key = (int(row["entry_id"]), int(row["order_index"]))
            grouped.setdefault(key, {})[row["version_code"]] = row
        for (entry_id, order_index), versions in grouped.items():
            if "orig" not in versions or "zh" not in versions:
                continue
            pairs.append({
                "key": f"{entry_id}:{order_index}",
                "ref_key": ref_keys[entry_id],
                "order_index": order_index,
                "orig": versions["orig"],
                "zh": versions["zh"],
            })
    return sorted(pairs, key=lambda row: (
        row["ref_key"], row["order_index"]))


def run(project: str, limit: int | None, dry_run: bool, pace: float) -> dict:
    # Must be set before importing the shared client: this process is the
    # dedicated Gemini #4 lane and may never rotate into #1–#3.
    os.environ["KGL_GEMINI_SLOT"] = "4"
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = "{source}"

    ledger = load_ledger()
    pairs = load_pairs(project)
    todo = [
        pair for pair in pairs
        if ledger.get(pair["key"]) != digest_pair(
            pair["orig"]["text"], pair["zh"]["text"])
    ]
    if limit is not None:
        todo = todo[:limit]
    print(f"quality-review: {len(todo)}/{len(pairs)} paragraphs to check", flush=True)
    stats = {"checked": 0, "ok": 0, "revised": 0, "failed": 0}
    if dry_run:
        return stats
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as ledger_file:
        for idx, pair in enumerate(todo):
            if pace and idx:
                time.sleep(pace)
            original = pair["orig"]["text"]
            current = pair["zh"]["text"]
            try:
                raw = te.gemini_translate(PROMPT.format(
                    original=original, translation=current))
                review = parse_review(raw)
                final = current
                if review["status"] == "revised":
                    final = te._to_traditional(str(review["text"]).strip())
                    patch_section(int(pair["zh"]["id"]), final)
                row = {
                    "key": pair["key"],
                    "digest": digest_pair(original, final),
                    "status": review["status"],
                    "ref_key": pair["ref_key"],
                    "reviewer": "gemini-slot-4",
                    "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                }
                ledger_file.write(json.dumps(row, ensure_ascii=False) + "\n")
                ledger_file.flush()
                stats["checked"] += 1
                stats[review["status"]] += 1
                print(f"  [{stats['checked']}/{len(todo)}] {pair['ref_key']} "
                      f"¶{pair['order_index']} {review['status']}", flush=True)
            except Exception as exc:  # leave absent from ledger → retry next run
                stats["failed"] += 1
                print(f"  FAIL {pair['ref_key']} ¶{pair['order_index']}: "
                      f"{type(exc).__name__}: {str(exc)[:160]}", flush=True)
                if stats["failed"] >= 4 and not stats["checked"]:
                    raise SystemExit("reviewer aborting after 4 initial failures")
    print(json.dumps(stats, ensure_ascii=False), flush=True)
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="genesis-philosophy")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--pace", type=float, default=1.0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    run(args.project, args.limit, args.dry_run, args.pace)


if __name__ == "__main__":
    main()
