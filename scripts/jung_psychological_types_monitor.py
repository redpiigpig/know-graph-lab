"""Periodic quality monitor for the Jung Psychological Types overnight run."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

try:
    from opencc import OpenCC
except Exception:  # noqa: BLE001
    OpenCC = None


DATA = Path(".claude/skills/ebook-collected-works/jung_data/psychological-types-1923")
PARTS = DATA / "parts"
STATUS = DATA / "status.json"
LOG = Path("scripts/logs/jung_psychological_types_monitor.log")
_OPENCC = OpenCC("s2t") if OpenCC else None

BAD_TERMS = [
    "潜意识",
    "弗洛伊德",
    "内倾",
    "外倾",
    "专业",
    "另一个",
]


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"_error": f"cannot read {path}: {exc}"}


def simplified_delta(text: str) -> int:
    if not _OPENCC:
        return 0
    converted = _OPENCC.convert(text)
    return sum(1 for a, b in zip(text, converted) if a != b) + abs(len(text) - len(converted))


def inspect_part(path: Path) -> dict:
    obj = load_json(path) or {}
    zh = obj.get("zh", "")
    en = obj.get("en", "")
    bad = [term for term in BAD_TERMS if term in zh]
    return {
        "file": path.name,
        "heading": obj.get("heading", ""),
        "en_chars": len(en),
        "zh_chars": len(zh),
        "zh_en_ratio": round(len(zh) / max(1, len(en)), 3),
        "simplified_delta": simplified_delta(zh),
        "bad_terms": bad,
        "sample": zh[:180].replace("\n", " "),
    }


def snapshot() -> dict:
    status = load_json(STATUS) or {}
    files = sorted(PARTS.glob("*.json"))
    latest = inspect_part(files[-1]) if files else None
    recent = [inspect_part(p) for p in files[-5:]]
    issues = []
    for item in recent:
        if item["simplified_delta"]:
            issues.append(f"{item['file']}: simplified_delta={item['simplified_delta']}")
        if item["bad_terms"]:
            issues.append(f"{item['file']}: bad_terms={','.join(item['bad_terms'])}")
        if item["zh_en_ratio"] < 0.12 or item["zh_en_ratio"] > 0.55:
            issues.append(f"{item['file']}: ratio={item['zh_en_ratio']}")
    return {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "status": status,
        "parts_count": len(files),
        "latest": latest,
        "recent_issues": issues,
    }


def write_snapshot(snap: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snap, ensure_ascii=False) + "\n")
    print(json.dumps(snap, ensure_ascii=False, indent=2), flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=1800)
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    while True:
        write_snapshot(snapshot())
        if args.once:
            return
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
