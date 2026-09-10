#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 /research-data/christian-studies（基督教研究）那張大卡片的資料。

這張卡片底下有四區，而**四區的材料來源不同**，這是它與別的 collection 最大的差別：

  教父研究     電子圖書館既有館藏（教父原典／教父著作／教父研究／Schaff 全套）
  宗教改革研究  電子圖書館既有館藏（改革宗／路德宗／安立甘宗／長老宗／清教徒…）
  普世運動     Drive 的 _corpus/ecumenical（archive.org 上 WCC 自己的數位檔案）
  洛桑運動     Drive 的 _corpus/lausanne（lausanne.org 的基礎文件與專題論文）

前兩區不必下載，館內早就很厚（教父約 270 本、宗教改革逾 2,200 本）；缺的是把它們
組織起來、看得見。後兩區則是本書第6章逼出來的新語料。

輸出 public/content/research-data/christian-studies/index.json（進版控，頁面讀它）。

用法：python scripts/christian_studies_index.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CORPUS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus")
OUT = ROOT / "public" / "content" / "research-data" / "christian-studies" / "index.json"

# 館藏區：(區名, 用來認出館藏的 subcategory 清單)
LIBRARY_AREAS = [
    ("patristics", "教父研究", "🕊️",
     "教父原典、教父著作與研究；含 Schaff《前尼西亞教父》《尼西亞及後期教父》全 38 卷",
     ["教父原典", "教父著作", "教父研究",
      "Schaff - Ante-Nicene Fathers (10 vols)",
      "Schaff - Nicene and Post-Nicene Fathers Series 1 (Augustine & Chrysostom, 14 vols)",
      "Schaff - Nicene and Post-Nicene Fathers Series 2 (14 vols)"]),
    ("reformation", "宗教改革研究", "📜",
     "改教家原著、認信文書與各宗派研究；館內最大的一批，多數來自改革宗檔案站",
     ["改革宗", "路德宗", "安立甘宗", "長老宗", "公理宗與清教徒", "荷蘭改革宗",
      "衛理宗", "改教著作", "改教研究", "其他改革宗資料", "信條與教理問答"]),
]

# 語料區：(區名, 目錄, 說明)
CORPUS_AREAS = [
    ("ecumenical", "普世運動", "🕊",
     "世界教會協會自己的數位檔案：信仰與教制文件（含利瑪文件《洗禮、聖餐與職事》）、"
     "生活與工作、世界宣教大會、羅馬天主教—WCC 聯合工作小組等系列"),
    ("lausanne", "福音派洛桑運動", "✝",
     "洛桑信約（1974）、馬尼拉宣言（1989）、開普敦承諾（2010）、首爾宣言（2024）"
     "四份基礎文件，以及洛桑專題論文（LOP）全系列"),
]


def load_env() -> dict:
    env = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8-sig").splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def library_stats(env: dict, subs: list[str]) -> list[dict]:
    """逐個 subcategory 取本數與段數。"""
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    H = {"apikey": key, "Authorization": f"Bearer {key}"}
    rows = []
    for sub in subs:
        r = requests.get(
            f'{env["SUPABASE_URL"]}/rest/v1/ebooks',
            headers=H,
            params={"select": "chunk_count", "subcategory": f"eq.{sub}", "limit": "5000"},
            timeout=60,
        )
        if r.status_code != 200:
            print(f"  ! {sub} 查詢失敗 {r.status_code}")
            continue
        data = r.json()
        rows.append({"name": sub, "books": len(data),
                     "chunks": sum(int(x.get("chunk_count") or 0) for x in data)})
    return sorted(rows, key=lambda x: -x["chunks"])


def corpus_stats(slug: str) -> dict:
    d = CORPUS / slug
    idx = d / "index.json"
    if not idx.exists():
        return {"docs": 0, "chars": 0, "items": [], "note": "尚未抓取"}
    data = json.loads(idx.read_text(encoding="utf-8"))
    items = [{"id": k, "title": (v.get("title") or k)[:110], "chars": v.get("chars", 0)}
             for k, v in data.items()]
    items.sort(key=lambda x: -x["chars"])
    return {"docs": len(data),
            "chars": sum(v.get("chars", 0) for v in data.values()),
            "items": items[:60]}


def main() -> int:
    env = load_env()
    areas = []

    for slug, name, icon, desc, subs in LIBRARY_AREAS:
        parts = library_stats(env, subs)
        areas.append({
            "slug": slug, "name": name, "icon": icon, "desc": desc,
            "source": "library",
            "books": sum(p["books"] for p in parts),
            "chunks": sum(p["chunks"] for p in parts),
            "parts": parts,
        })
        print(f'{name}：{areas[-1]["books"]} 本、{areas[-1]["chunks"]:,} 段')

    for slug, name, icon, desc in CORPUS_AREAS:
        st = corpus_stats(slug)
        areas.append({"slug": slug, "name": name, "icon": icon, "desc": desc,
                      "source": "corpus", **st})
        print(f'{name}：{st["docs"]} 份、{st["chars"]:,} 字'
              + (f'（{st.get("note")}）' if st.get("note") else ""))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"areas": areas}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
