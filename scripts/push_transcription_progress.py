#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""彙整「重轉錄佇列」＋「全集翻譯」進度成單一 JSON，供 /transcription-progress 監視頁。

資料源（全部本機檔案，不碰 DB — REST 被鎖也能跑）：
  - 重轉錄：c:/tmp/quality_tiers.json（quality_sweep 產出）
            + scripts/logs/reocr_ledger.json（requeue_reocr 狀態機）
  - 全集翻譯：mueller_auto.WORKS（穆勒全集）＋ sbe_translate.WORKS（東方聖書）
            ＋ panikkar_auto.WORKS（潘尼卡，若可載入）
            逐 work 掃 sec*.json 的 en[]/zh[] 算段落完成率

輸出：c:/tmp/transcription_progress.json ＋ R2 progress/transcription.json
（production 網站從 R2 讀；dev 直讀本機檔）。

排程：run_ocr_daily.bat / run_quality_sweep.bat 末尾各推一次。手動：
  python scripts/push_transcription_progress.py [--no-r2]
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from audit_book_structure import load_env  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

OUT_LOCAL = Path("c:/tmp/transcription_progress.json")
R2_KEY = "progress/transcription.json"


def _read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


# ── 重轉錄（REOCR requeue）────────────────────────────────────────────────

def reocr_block() -> dict:
    tiers = _read_json(Path("c:/tmp/quality_tiers.json")) or {}
    ledger = _read_json(SCRIPTS / "logs" / "reocr_ledger.json") or {}
    states = Counter(e.get("state") for e in ledger.values())
    recent = sorted(
        ({"title": e.get("title") or "", "state": e.get("state"),
          "updated_at": e.get("updated_at")} for e in ledger.values()),
        key=lambda x: x["updated_at"] or "", reverse=True)[:10]
    return {
        "tier_counts": tiers.get("counts") or {},
        "tiers_generated_at": tiers.get("generated_at"),
        "ledger_states": dict(states),
        "recent": recent,
    }


# ── 全集翻譯 ──────────────────────────────────────────────────────────────

def work_progress(work_dir: Path) -> dict:
    """掃一部作品的 sec*.json：段落總數/已翻數（zh 非空即算完成）。"""
    total = done = 0
    secs = sorted(work_dir.glob("sec*.json")) if work_dir.exists() else []
    for p in secs:
        s = _read_json(p) or {}
        en = s.get("en") or []
        zh = s.get("zh") or []
        total += len(en)
        done += sum(1 for j in range(len(en)) if j < len(zh) and zh[j])
    return {"sections": len(secs), "paras_total": total, "paras_zh": done}


def corpus_block(name: str, works: list[dict], data_root: Path, is_done) -> dict:
    rows = []
    for w in works:
        prog = work_progress(data_root / w["slug"])
        rows.append({
            "slug": w["slug"], "title": w["title"],
            "done": bool(is_done(w)) if prog["sections"] else False,
            **prog,
        })
    return {
        "name": name,
        "works_total": len(rows),
        "works_done": sum(1 for r in rows if r["done"]),
        "works": rows,
    }


def translation_corpora() -> list[dict]:
    out = []
    import mueller_auto as ma
    out.append(corpus_block("馬克斯‧穆勒全集", ma.WORKS, ma.DATA_ROOT, ma.is_done))
    try:
        import sbe_translate as sbe
        out.append(corpus_block("東方聖書（SBE）", sbe.WORKS, ma.DATA_ROOT, ma.is_done))
    except Exception as e:
        print(f"⚠ sbe_translate 載入失敗：{e}", file=sys.stderr)
    try:
        import panikkar_auto as pk
        data_root = getattr(pk, "DATA_ROOT", None)
        if data_root and getattr(pk, "WORKS", None):
            out.append(corpus_block("潘尼卡全集", pk.WORKS, Path(data_root), ma.is_done))
    except Exception as e:
        print(f"⚠ panikkar_auto 載入失敗：{e}", file=sys.stderr)
    return out


def push_r2(payload: str) -> None:
    import boto3
    env = load_env()
    client = boto3.client(
        "s3", endpoint_url=env["R2_ENDPOINT"],
        aws_access_key_id=env["R2_ACCESS_KEY"],
        aws_secret_access_key=env["R2_SECRET_KEY"])
    client.put_object(Bucket=env["R2_BUCKET"], Key=R2_KEY,
                      Body=payload.encode("utf-8"),
                      ContentType="application/json")


def main() -> None:
    doc = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reocr": reocr_block(),
        "translation": translation_corpora(),
    }
    payload = json.dumps(doc, ensure_ascii=False, indent=1)
    OUT_LOCAL.parent.mkdir(parents=True, exist_ok=True)
    OUT_LOCAL.write_text(payload, encoding="utf-8")
    print(f"→ {OUT_LOCAL}")
    if "--no-r2" not in sys.argv:
        try:
            push_r2(payload)
            print(f"→ r2://{R2_KEY}")
        except Exception as e:
            print(f"⚠ R2 push failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
