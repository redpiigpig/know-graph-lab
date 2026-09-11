#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把公有領域的宗教學者原著建成全集 ebook row，交 parse_worker 解析。

緣起（2026-09-11）：使用者要優先做宗教學者，點名伊利亞德／韋伯／涂爾幹／奧托。
盤點發現**奧托全空（0 本）、涂爾幹只有 1 本**，但兩人都早已進入公有領域——
奧托 1937 卒、涂爾幹 1917 卒，原文與早期英譯都能合法直接抓，根本不必等 z-lib。

來源都選 **EPUB**：archive.org 與 Gutenberg 本來就提供，直接走現成的電子書管線，
不必為了一份 djvu.txt 另寫一支 builder。

ebook_id 照全集慣例給每位作者一個命名空間（[[ebook-collected-works]] §B5）：
奧托 `07701869-…`（otto＋生年）、涂爾幹沿用既有的 `80000000-…`。

  python scripts/pd_scholars_ingest.py            # 預演
  python scripts/pd_scholars_ingest.py --apply    # 建 row（再跑 parse_worker）
"""
from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\全集")

BOOKS = [
    {
        "id": "07701869-0000-4000-8000-000000000001",
        "title": "論「聖」",
        "subtitle": "論神聖觀念中的非理性因素及其與理性的關係（德文原著）",
        "author": "魯道夫‧奧托", "author_en": "Rudolf Otto",
        "original_title": "Das Heilige: Über das Irrationale in der Idee des Göttlichen "
                          "und sein Verhältnis zum Rationalen",
        "original_publish_year": 1917,
        "publication_year": 1926,          # 手上這一份是 Klotz, Gotha 第 14 版
        "publisher": "Leopold Klotz Verlag",
        "publisher_location": "Gotha",
        "path": STUDIO / "宗教學" / "奧托" / "Rudolf Otto，Das Heilige (14. Aufl. 1926).epub",
    },
    {
        "id": "07701869-0000-4000-8000-000000000002",
        "title": "自然主義與宗教",
        "subtitle": "英譯本（Thomson／Thomson 譯，1907）",
        "author": "魯道夫‧奧托", "author_en": "Rudolf Otto",
        "original_title": "Naturalism and Religion",
        "original_publish_year": 1904,
        "publication_year": 1907,
        "publisher": "Williams & Norgate",
        "publisher_location": "London",
        "path": STUDIO / "宗教學" / "奧托" / "Rudolf Otto，Naturalism and Religion (1907).epub",
    },
    {
        "id": "80000000-0000-4000-8000-000000000020",
        "title": "自殺論",
        "subtitle": "社會學研究（法文原著）",
        "author": "涂爾幹", "author_en": "Émile Durkheim",
        "original_title": "Le Suicide: Étude de sociologie",
        "original_publish_year": 1897,
        "publication_year": 1897,
        "publisher": "Félix Alcan",
        "publisher_location": "Paris",
        "path": STUDIO / "宗教社會學" / "涂爾幹" / "Émile Durkheim，Le Suicide (1897).epub",
    },
    {
        "id": "80000000-0000-4000-8000-000000000021",
        "title": "教育與社會學",
        "subtitle": "法文原著",
        "author": "涂爾幹", "author_en": "Émile Durkheim",
        "original_title": "Éducation et sociologie",
        "original_publish_year": 1922,
        "publication_year": 1922,
        "publisher": "Félix Alcan",
        "publisher_location": "Paris",
        "path": STUDIO / "宗教社會學" / "涂爾幹" / "Émile Durkheim，Éducation et sociologie (1922).epub",
    },
]


def env() -> dict:
    out = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip("\"'")
    return out


E = env()
URL = E["SUPABASE_URL"]
KEY = E.get("SUPABASE_SERVICE_ROLE_KEY") or E.get("SUPABASE_SERVICE_KEY")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def api(path: str, method: str = "GET", body=None, prefer: str | None = None):
    headers = dict(H)
    if prefer:
        headers["Prefer"] = prefer
    req = urllib.request.Request(
        URL + "/rest/v1/" + urllib.parse.quote(path, safe="?&=.,*()-"),
        method=method, headers=headers,
        data=json.dumps(body).encode() if body is not None else None,
    )
    raw = urllib.request.urlopen(req).read().decode("utf-8")
    return json.loads(raw) if raw.strip() else []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    print("實際建立" if a.apply else "預演（加 --apply 才會寫 DB）", "\n")
    ok = []
    for b in BOOKS:
        p: Path = b["path"]
        if not p.exists():
            print(f"  ✗ 檔案不在：{p}")
            continue
        exists = api(f"ebooks?select=id&id=eq.{b['id']}")
        state = "已存在→更新" if exists else "新建"
        print(f"  {state:8s} {b['author']}《{b['title']}》  {p.stat().st_size/1e6:.1f} MB")
        if not a.apply:
            continue
        row = {
            "id": b["id"], "title": b["title"], "subtitle": b["subtitle"],
            "author": b["author"], "author_en": b["author_en"],
            "original_title": b["original_title"],
            "original_publish_year": b["original_publish_year"],
            "publication_year": b["publication_year"],
            "publisher": b["publisher"], "publisher_location": b["publisher_location"],
            "file_type": "epub", "file_path": str(p),
            # 🚨 一定要帶 collection，否則這本會混進電子圖書館
            # （[[feedback_collected_works_not_in_library]]）
            "collection": "collected-works",
            "display_mode": "standard",
        }
        api("ebooks", "POST", [row], prefer="resolution=merge-duplicates")
        ok.append(b["id"])

    if a.apply and ok:
        print(f"\n建好 {len(ok)} 本。接著解析：")
        print("  python scripts/parse_worker.py run " + " ".join(f"--book {i}" for i in ok))


if __name__ == "__main__":
    main()
