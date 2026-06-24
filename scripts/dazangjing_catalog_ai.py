#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Classify and monitor the Dazangjing source catalog.

Engine order is intentionally local-first:
  1. Ollama on localhost
  2. Gemini free keys from env/.env
  3. NVIDIA NIM free keys from env/.env

This script never inserts records into the canon data files. It writes a JSONL
ledger for human review and a small heartbeat file for monitoring.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "data" / "dazangjing" / "source-catalog"
DEFAULT_INPUT = CATALOG_DIR / "seed-records.json"
DEFAULT_LEDGER = CATALOG_DIR / "classified-records.jsonl"
DEFAULT_HEARTBEAT = CATALOG_DIR / "catalog-loop-heartbeat.json"
DEFAULT_LOG = CATALOG_DIR / "catalog-loop.log"

OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("DAZANGJING_OLLAMA_MODEL", "qwen2.5:7b")
GEMINI_MODEL = os.environ.get("DAZANGJING_GEMINI_MODEL", "gemini-2.5-flash")
NVIDIA_MODEL = os.environ.get("DAZANGJING_NVIDIA_MODEL", "deepseek-ai/deepseek-v4-flash")
NVIDIA_URL = os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1/chat/completions")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_dotenv(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env_keys(prefixes: tuple[str, ...]) -> list[str]:
    keys: list[str] = []
    for name, value in sorted(os.environ.items()):
        if not value:
            continue
        upper = name.upper()
        if any(upper == p or upper.startswith(p + "_") for p in prefixes):
            for part in str(value).split(","):
                part = part.strip()
                if part and part not in keys:
                    keys.append(part)
    return keys


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None, timeout: int = 45) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def parse_json_loose(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
        text = re.sub(r"```$", "", text).strip()
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1:
        text = text[first:last + 1]
    return json.loads(text)


REQUIRED_CLASSIFICATION_KEYS = {
    "decision",
    "title_orig",
    "title_zh",
    "author",
    "era",
    "place",
    "language",
    "eraKey",
    "collectionKey",
    "canon",
    "confidence",
    "reason_zh",
    "needs",
}
VALID_DECISIONS = {"keep_primary_work", "drop_secondary_study", "drop_catalog_or_edition", "needs_manual_review"}


_S2TW = None


def to_traditional(text: str) -> str:
    """Force Traditional Chinese (Taiwan). NVIDIA/deepseek and some Gemini
    replies come back Simplified despite the prompt; this is the safety net
    for the project-wide Traditional-only rule."""
    global _S2TW
    if not text:
        return text
    if _S2TW is None:
        try:
            import opencc  # type: ignore
            _S2TW = opencc.OpenCC("s2tw")
        except Exception:
            _S2TW = False
    if _S2TW is False:
        return text
    return _S2TW.convert(text)


def normalize_classification(data: dict[str, Any]) -> dict[str, Any]:
    # Some local models wrap the answer under {"record": {...}} even when asked
    # not to. Unwrap once, then require the expected schema.
    if "record" in data and isinstance(data["record"], dict) and "decision" in data["record"]:
        data = data["record"]
    missing = REQUIRED_CLASSIFICATION_KEYS - set(data)
    if missing:
        raise ValueError(f"classification missing keys: {sorted(missing)}")
    if data.get("decision") not in VALID_DECISIONS:
        raise ValueError(f"invalid decision: {data.get('decision')}")
    if data.get("eraKey") not in {"pre", "ancient", "medieval", "early-modern", "modern", "unknown"}:
        raise ValueError(f"invalid eraKey: {data.get('eraKey')}")
    if data.get("collectionKey") not in {"jing", "lu", "lun", "xuandao", "shuxin", "liyi", "shiwen", "yijiao", "shizhuan", "leishu", "unknown"}:
        raise ValueError(f"invalid collectionKey: {data.get('collectionKey')}")
    if data.get("canon") not in {"zheng", "wai", "unknown"}:
        raise ValueError(f"invalid canon: {data.get('canon')}")
    try:
        data["confidence"] = float(data.get("confidence", 0))
    except Exception:
        data["confidence"] = 0.0
    if not isinstance(data.get("needs"), list):
        data["needs"] = [str(data.get("needs"))]
    for field in ("title_zh", "reason_zh"):
        if isinstance(data.get(field), str):
            data[field] = to_traditional(data[field])
    return data


def record_key(record: dict[str, Any]) -> str:
    basis = "|".join(str(record.get(k, "")) for k in ("source", "url", "title", "author", "date"))
    return re.sub(r"\s+", " ", basis).strip().lower()


def load_done(path: Path) -> set[str]:
    done: set[str] = set()
    if not path.exists():
        return done
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Retry rows where every engine failed (transient 429/503): do not freeze
        # a transient outage as a permanent needs_manual_review.
        if item.get("engine") == "none":
            continue
        key = item.get("record_key")
        if key:
            done.add(key)
    return done


def prompt_for(record: dict[str, Any]) -> str:
    payload = {
        "record": record,
        "allowed": {
            "eraKey": ["pre", "ancient", "medieval", "early-modern", "modern", "unknown"],
            "collectionKey": ["jing", "lu", "lun", "xuandao", "shuxin", "liyi", "shiwen", "yijiao", "shizhuan", "leishu", "unknown"],
            "canon": ["zheng", "wai", "unknown"],
            "decision": ["keep_primary_work", "drop_secondary_study", "drop_catalog_or_edition", "needs_manual_review"],
        },
    }
    return (
        "You classify candidate bibliographic records for a Christian Dazangjing source catalog.\n"
        "Return JSON only. Do not invent facts. If uncertain, use unknown/needs_manual_review.\n"
        "Use Traditional Chinese for title_zh and reason_zh.\n"
        "Classify the original work's composition era, not the manuscript/printed edition date. "
        "For example, Augustine's De civitate Dei is ancient even if the holding is a 1475 print.\n"
        "Do not classify a record as zheng merely because it is famous. Use unknown or needs_manual_review "
        "when the zheng/wai boundary depends on Dazangjing editorial policy.\n"
        "If the record is only a printed edition, translation, manuscript witness, shelf/classification schedule, "
        "or mixed catalogue, preserve it as evidence only and set decision to drop_catalog_or_edition or needs_manual_review.\n"
        "collectionKey 'jing' (經藏) is ONLY for biblical scripture / canonical Bible texts and versions. "
        "Homilies, sermons, orations, and theological treatises are NOT jing: patristic homilies/orations -> 'shiwen' or 'lun'; "
        "doctrinal/theological treatises -> 'lun'; church history -> 'shizhuan'; canon law -> 'lu'; liturgy -> 'liyi'.\n"
        "Prefer primary works, canonical/near-canonical texts, patristic works, liturgy, law, "
        "hagiography, history, letters, hymns, reference works, and eastern Christian traditions. "
        "Drop modern secondary scholarship unless it is a critical source catalog/reference needed only as bibliography.\n\n"
        "JSON schema:\n"
        "{"
        "\"decision\": string,"
        "\"title_orig\": string,"
        "\"title_zh\": string,"
        "\"author\": string,"
        "\"era\": string,"
        "\"place\": string,"
        "\"language\": string,"
        "\"eraKey\": string,"
        "\"collectionKey\": string,"
        "\"canon\": string,"
        "\"confidence\": number,"
        "\"reason_zh\": string,"
        "\"needs\": string[]"
        "}\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def review_prompt(record: dict[str, Any], local_classification: dict[str, Any]) -> str:
    return (
        "You are reviewing a local Ollama bibliographic classification for a Christian Dazangjing source catalog.\n"
        "Return JSON only using the same schema. Correct mistakes. If uncertain, downgrade confidence and set needs.\n"
        "Use Traditional Chinese for title_zh and reason_zh.\n"
        "Important rules: classify the original work's composition era, not the printed edition date; "
        "patristic theological works usually belong to 論藏/lun; do not mark a work zheng merely because it is important; "
        "drop modern secondary scholarship; keep manuscript/edition records only as witnesses to a primary work. "
        "If zheng/wai is not certain from project rules, set canon=unknown and decision=needs_manual_review.\n\n"
        f"source_record={json.dumps(record, ensure_ascii=False)}\n"
        f"local_classification={json.dumps(local_classification, ensure_ascii=False)}"
    )


def call_ollama(prompt: str) -> tuple[str, str]:
    data = post_json(
        f"{OLLAMA_BASE}/api/chat",
        {
            "model": OLLAMA_MODEL,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": "You are a strict bibliographic classifier. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=60,
    )
    return data.get("message", {}).get("content", ""), OLLAMA_MODEL


def call_gemini(prompt: str, keys: list[str], cursor: int) -> tuple[str, str, int]:
    if not keys:
        raise RuntimeError("no Gemini keys")
    last = ""
    for i in range(len(keys)):
        idx = (cursor + i) % len(keys)
        key = keys[idx]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"
        try:
            data = post_json(
                url,
                {
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 2048,
                        "responseMimeType": "application/json",
                        # gemini-2.5-flash thinking otherwise eats the token budget and
                        # truncates the JSON mid-string ("Unterminated string"). Disable it.
                        "thinkingConfig": {"thinkingBudget": 0},
                    },
                },
                timeout=45,
            )
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if text:
                return text, GEMINI_MODEL, (idx + 1) % len(keys)
        except Exception as exc:
            last = str(exc)
            continue
    raise RuntimeError(f"Gemini failed: {last}")


def call_nvidia(prompt: str, keys: list[str], cursor: int) -> tuple[str, str, int]:
    if not keys:
        raise RuntimeError("no NVIDIA keys")
    last = ""
    for i in range(len(keys)):
        idx = (cursor + i) % len(keys)
        key = keys[idx]
        try:
            data = post_json(
                NVIDIA_URL,
                {
                    "model": NVIDIA_MODEL,
                    "temperature": 0.1,
                    "max_tokens": 1200,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": "You are a strict bibliographic classifier. Return valid JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                },
                headers={"Authorization": f"Bearer {key}"},
                timeout=60,
            )
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if text:
                return text, NVIDIA_MODEL, (idx + 1) % len(keys)
        except Exception as exc:
            last = str(exc)
            continue
    raise RuntimeError(f"NVIDIA failed: {last}")


def classify_record(record: dict[str, Any], gemini_keys: list[str], nvidia_keys: list[str], cursors: dict[str, int]) -> dict[str, Any]:
    if not str(record.get("title", "")).strip():
        return {
            "engine": "rule",
            "model": "blank-title-filter",
            "classification": {
                "decision": "needs_manual_review",
                "title_orig": "",
                "title_zh": "",
                "author": str(record.get("author", "")),
                "era": str(record.get("date", "")),
                "place": "",
                "language": str(record.get("language", "")),
                "eraKey": "unknown",
                "collectionKey": "unknown",
                "canon": "unknown",
                "confidence": 0.0,
                "reason_zh": "來源館藏記錄未解析出 title，需檢查 SRU/MARC 解析或原始 URL。",
                "needs": ["blank_title", "source_parse_review"],
            },
            "engine_errors": [],
        }
    prompt = prompt_for(record)
    errors: list[str] = []
    local_candidate: dict[str, Any] | None = None
    for engine in ("ollama", "gemini", "nvidia"):
        try:
            if engine == "ollama":
                text, model = call_ollama(prompt)
            elif engine == "gemini":
                text, model, cursors["gemini"] = call_gemini(prompt, gemini_keys, cursors.get("gemini", 0))
            else:
                text, model, cursors["nvidia"] = call_nvidia(prompt, nvidia_keys, cursors.get("nvidia", 0))
            parsed = normalize_classification(parse_json_loose(text))
            if engine == "ollama":
                local_candidate = parsed
                try:
                    review_text, review_model, cursors["gemini"] = call_gemini(
                        review_prompt(record, parsed),
                        gemini_keys,
                        cursors.get("gemini", 0),
                    )
                    reviewed = normalize_classification(parse_json_loose(review_text))
                    return {
                        "engine": "ollama+gemini_review",
                        "model": f"{model} + {review_model}",
                        "classification": reviewed,
                        "local_classification": parsed,
                        "engine_errors": errors,
                    }
                except Exception as review_exc:
                    errors.append(f"gemini_review: {review_exc}")
                    try:
                        review_text, review_model, cursors["nvidia"] = call_nvidia(
                            review_prompt(record, parsed),
                            nvidia_keys,
                            cursors.get("nvidia", 0),
                        )
                        reviewed = normalize_classification(parse_json_loose(review_text))
                        return {
                            "engine": "ollama+nvidia_review",
                            "model": f"{model} + {review_model}",
                            "classification": reviewed,
                            "local_classification": parsed,
                            "engine_errors": errors,
                        }
                    except Exception as review_exc2:
                        errors.append(f"nvidia_review: {review_exc2}")
                        # Never trust local Ollama unreviewed: qwen2.5:7b hallucinates
                        # (cross-record title bleed). Fall through to direct Gemini/NVIDIA.
                        raise ValueError("local classification could not be reviewed; not trusting it")
            return {
                "engine": engine,
                "model": model,
                "classification": parsed,
                **({"local_classification": local_candidate} if local_candidate else {}),
                "engine_errors": errors,
            }
        except Exception as exc:
            errors.append(f"{engine}: {exc}")
    return {
        "engine": "none",
        "model": "",
        "classification": {
            "decision": "needs_manual_review",
            "title_orig": record.get("title", ""),
            "title_zh": "",
            "author": record.get("author", ""),
            "era": record.get("date", ""),
            "place": "",
            "language": record.get("language", ""),
            "eraKey": "unknown",
            "collectionKey": "unknown",
            "canon": "unknown",
            "confidence": 0,
            "reason_zh": "所有引擎皆失敗，需人工複查。",
            "needs": ["engine_failure"],
        },
        "engine_errors": errors,
    }


def write_heartbeat(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def append_log(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"{utc_now()} {message}\n")


def load_records(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("records", []))


def run_once(args: argparse.Namespace) -> dict[str, Any]:
    load_dotenv()
    input_path = Path(args.input)
    ledger = Path(args.ledger)
    heartbeat = Path(args.heartbeat)
    log = Path(args.log)
    records = load_records(input_path)
    done = load_done(ledger)
    gemini_keys = env_keys(("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY_OLINE_ONLY"))
    nvidia_keys = env_keys(("NVIDIA_API_KEY", "NVIDIA_API_KEY_OLINE_ONLY", "NVIDIA_API_KEY_ONLINE_ONLY"))
    cursors = {"gemini": 0, "nvidia": 0}

    processed = 0
    skipped = 0
    append_log(log, f"run_once start records={len(records)} done={len(done)}")
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as out:
        for record in records:
            key = record_key(record)
            if key in done:
                skipped += 1
                continue
            result = classify_record(record, gemini_keys, nvidia_keys, cursors)
            row = {
                "record_key": key,
                "classified_at": utc_now(),
                "source_record": record,
                **result,
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            done.add(key)
            processed += 1
            write_heartbeat(
                heartbeat,
                {
                    "status": "running",
                    "updated_at": utc_now(),
                    "pid": os.getpid(),
                    "input": str(input_path),
                    "ledger": str(ledger),
                    "processed_this_run": processed,
                    "skipped_this_run": skipped,
                    "total_done": len(done),
                    "last_engine": row["engine"],
                    "last_title": record.get("title", ""),
                },
            )
            if args.max_records and processed >= args.max_records:
                break
            time.sleep(args.sleep)
    status = {
        "status": "idle",
        "updated_at": utc_now(),
        "pid": os.getpid(),
        "processed_this_run": processed,
        "skipped_this_run": skipped,
        "total_done": len(done),
        "ledger": str(ledger),
    }
    write_heartbeat(heartbeat, status)
    append_log(log, f"run_once done processed={processed} skipped={skipped} total_done={len(done)}")
    return status


def loop(args: argparse.Namespace) -> None:
    while True:
        try:
            status = run_once(args)
            append_log(Path(args.log), f"loop sleep seconds={args.interval} status={status.get('status')}")
        except Exception as exc:
            append_log(Path(args.log), f"loop error {exc}")
            write_heartbeat(
                Path(args.heartbeat),
                {"status": "error", "updated_at": utc_now(), "pid": os.getpid(), "error": str(exc)},
            )
        time.sleep(args.interval)


def health(args: argparse.Namespace) -> int:
    hb = Path(args.heartbeat)
    if not hb.exists():
        print("no heartbeat")
        return 2
    data = json.loads(hb.read_text(encoding="utf-8"))
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if data.get("status") in {"running", "idle"} else 1


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["once", "loop", "health"])
    p.add_argument("--input", default=str(DEFAULT_INPUT))
    p.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    p.add_argument("--heartbeat", default=str(DEFAULT_HEARTBEAT))
    p.add_argument("--log", default=str(DEFAULT_LOG))
    p.add_argument("--max-records", type=int, default=0)
    p.add_argument("--sleep", type=float, default=0.2)
    p.add_argument("--interval", type=int, default=3600)
    args = p.parse_args()

    if args.command == "once":
        print(json.dumps(run_once(args), ensure_ascii=False, indent=2))
    elif args.command == "loop":
        loop(args)
    else:
        sys.exit(health(args))


if __name__ == "__main__":
    main()
