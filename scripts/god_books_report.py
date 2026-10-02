#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 merged.json + 帳本 → Drive 研究資料\神觀史與宗教起源\既有資料盤點.md"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import god_books_merge as gm
OUT = ROOT / "output" / "god_books"
LEDGER = ROOT / "scripts" / "state" / "zlib_ledger.jsonl"
DEST = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\研究資料\神觀史與宗教起源")

led = {}
for l in LEDGER.read_text(encoding="utf-8").splitlines():
    try:
        r = json.loads(l)
    except Exception:
        continue
    if str(r.get("key", "")).startswith("godbib-"):
        led[r["key"]] = r
import hashlib
rows = json.loads((OUT / "merged.json").read_text(encoding="utf-8"))
for r in rows:
    key = "godbib-" + hashlib.sha1(f"{r['author']}|{r['title']}".encode()).hexdigest()[:10]
    L = led.get(key)
    if r["status"] == "館內已有":
        r["state"] = "館內已有"
    elif L and L.get("status") == "downloaded":
        via = (L.get("pick") or {}).get("via", "z-lib")
        r["state"] = "公開典藏已下載（archive.org）" if via == "archive.org" else f"已下載（{via}）"
    elif L:
        r["state"] = f"帳本：{L['status']}"
    elif r["status"] == "公開典藏已下載":
        r["state"] = "公開典藏已下載（archive.org）"
    else:
        r["state"] = "已排入抓書單（LibGen 尚未查到，待 z-lib 排程）"
from collections import Counter
cnt = Counter(r["state"] for r in rows)
bysrc = Counter(f for r in rows for f in r["from"])
md = ["# 神觀史與宗教起源：三本書的參考書目盤點", "",
      f"> 產生日期 2026-10-02；腳本 `scripts/god_books_extract.py`／`god_books_merge.py`／`god_books_archive.py`／`god_books_report.py`", "",
      "## 一、三本書的書目來源與限制", "",
      "| 書 | 館內版本 | 書目從哪來 | 限制 |", "|---|---|---|---|",
      "| 《神的歷史》凱倫‧阿姆斯壯 | 中文：電子圖書館 神學／天主教文獻（簡體大陸版，只有正文、無註釋與書目）；英文原著 *A History of God* 也在館內 | 英文原著 PDF 的尾註（第 200–218 頁） | 英文 PDF 的尾註本身不全（只到各章部分註），無獨立書目章；以 LLM 抽書名，作者名有 OCR 錯字（如 Bouwsme） |",
      "| 《神的演化》賴特／梁永安譯 | 電子圖書館 人類生物學（掃描 PDF，OCR 完成） | 全書正文提到的書 | 🚨 中譯本掃描 PDF 只到「鳴謝」，**書末註釋與參考書目整段沒有**（「Note」頁無正文）。只能從正文抽被提到的書，不是完整書目；英文原著 Notes／Bibliography 另需取得 |",
      "| 《造神》雷薩‧阿斯蘭（God: A Human History 中譯，已確認） | 電子圖書館 宗教學／宗教史（epub） | 書末 Chicago 體參考書目 | 完整；期刊論文與書中一章已略去，只取專書；章末註釋中另提的書未逐一展開 |", "",
      "## 二、統計", "",
      f"- 三本抽出（去重後）：{len(rows)} 筆；各書出現：{dict(bysrc)}（一筆可同時出自多本）",
      *[f"- {k}：{v}" for k, v in cnt.most_common()], "",
      "## 三、逐筆清單", "", "| # | 作者 | 書名 | 年 | 出自 | 狀態 | 備註 |", "|---|---|---|---|---|---|---|"]
for i, r in enumerate(sorted(rows, key=lambda x: (gm.surname(x["author"]), x["title"])), 1):
    note = r.get("library", "") if r["state"] == "館內已有" else ""
    md.append(f"| {i} | {r['author']} | {r['title'][:90]} | {r['year'] or ''} | {'、'.join(r['from'])} | {r['state']} | {note} |")
DEST.mkdir(parents=True, exist_ok=True)
(DEST / "既有資料盤點.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(cnt, "→", DEST / "既有資料盤點.md")
